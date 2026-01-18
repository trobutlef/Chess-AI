"""
Multiplayer WebSocket module for real-time chess games.
Uses Flask-SocketIO for WebSocket communication.
"""
import os
import logging
from datetime import datetime
from flask import session
from flask_socketio import SocketIO, emit, join_room, leave_room

logger = logging.getLogger(__name__)

# Room storage (in production, use Redis)
rooms = {}  # room_id -> room_data
user_rooms = {}  # user_id -> room_id


def init_socketio(app, db, Game, User):
    """Initialize SocketIO with the Flask app."""
    
    # Allow all origins in development
    cors_origins = "*" if os.getenv("FLASK_ENV") != "production" else os.getenv("CORS_ORIGINS", "").split(",")
    
    socketio = SocketIO(
        app,
        cors_allowed_origins=cors_origins,
        async_mode='eventlet',
        logger=True,
        engineio_logger=True
    )
    
    @socketio.on('connect')
    def handle_connect():
        user_id = session.get('user_id')
        if not user_id:
            logger.warning("Unauthenticated socket connection attempt")
            return False  # Reject connection
        
        logger.info(f"User {user_id} connected")
        emit('connected', {'user_id': user_id})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        user_id = session.get('user_id')
        if user_id and user_id in user_rooms:
            room_id = user_rooms[user_id]
            leave_game_room(user_id, room_id)
        logger.info(f"User {user_id} disconnected")
    
    @socketio.on('create_room')
    def handle_create_room(data):
        """Create a new game room."""
        user_id = session.get('user_id')
        if not user_id:
            emit('error', {'message': 'Not authenticated'})
            return
        
        # Get user info
        user = User.query.get(user_id)
        if not user:
            emit('error', {'message': 'User not found'})
            return
        
        # Generate room ID
        room_id = f"room_{user_id}_{datetime.utcnow().timestamp()}"
        
        # Store room
        rooms[room_id] = {
            'id': room_id,
            'host_id': user_id,
            'host_name': user.name,
            'guest_id': None,
            'guest_name': None,
            'time_control': data.get('time_control', 300),
            'status': 'waiting',  # waiting, playing, finished
            'game_id': None,
            'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            'white_player': user_id,  # Host is white by default
            'created_at': datetime.utcnow().isoformat()
        }
        
        user_rooms[user_id] = room_id
        join_room(room_id)
        
        emit('room_created', rooms[room_id])
        emit('room_list_updated', get_available_rooms(), broadcast=True)
    
    @socketio.on('join_room')
    def handle_join_room(data):
        """Join an existing game room."""
        user_id = session.get('user_id')
        room_id = data.get('room_id')
        
        if not user_id:
            emit('error', {'message': 'Not authenticated'})
            return
        
        if room_id not in rooms:
            emit('error', {'message': 'Room not found'})
            return
        
        room = rooms[room_id]
        
        if room['status'] != 'waiting':
            emit('error', {'message': 'Room is not available'})
            return
        
        if room['guest_id']:
            emit('error', {'message': 'Room is full'})
            return
        
        user = User.query.get(user_id)
        room['guest_id'] = user_id
        room['guest_name'] = user.name
        room['status'] = 'playing'
        
        user_rooms[user_id] = room_id
        join_room(room_id)
        
        # Create game in database
        game = Game(
            user_id=room['host_id'],
            opponent_type='human',
            opponent_id=user_id,
            time_control=room['time_control'],
            user_color='white',
            white_time=room['time_control'] * 1000,
            black_time=room['time_control'] * 1000,
        )
        db.session.add(game)
        db.session.commit()
        
        room['game_id'] = game.id
        
        emit('room_joined', room, room=room_id)
        emit('game_started', room, room=room_id)
        emit('room_list_updated', get_available_rooms(), broadcast=True)
    
    @socketio.on('make_move')
    def handle_make_move(data):
        """Handle a move in a multiplayer game."""
        user_id = session.get('user_id')
        room_id = data.get('room_id')
        move = data.get('move')  # UCI format
        fen = data.get('fen')
        san = data.get('san')
        white_time = data.get('white_time')
        black_time = data.get('black_time')
        
        if room_id not in rooms:
            emit('error', {'message': 'Room not found'})
            return
        
        room = rooms[room_id]
        
        # Verify it's this player's turn
        is_white = room['white_player'] == user_id
        is_white_turn = 'w' in fen.split()[1] if fen else True
        
        # Update room state
        room['fen'] = fen
        
        # Broadcast move to opponent
        emit('move_made', {
            'move': move,
            'fen': fen,
            'san': san,
            'from_user': user_id,
            'white_time': white_time,
            'black_time': black_time,
        }, room=room_id, include_self=False)
        
        # Save to database
        if room['game_id']:
            game = Game.query.get(room['game_id'])
            if game and san:
                moves = game.pgn.split() if game.pgn else []
                move_number = len([m for m in moves if not m.endswith('.')]) // 2 + 1
                if len(moves) % 3 == 0:  # New move number
                    game.pgn = f"{game.pgn} {move_number}. {san}".strip()
                else:
                    game.pgn = f"{game.pgn} {san}".strip()
                game.white_time = white_time
                game.black_time = black_time
                db.session.commit()
    
    @socketio.on('game_over')
    def handle_game_over(data):
        """Handle game over."""
        room_id = data.get('room_id')
        result = data.get('result')
        reason = data.get('reason')
        
        if room_id not in rooms:
            return
        
        room = rooms[room_id]
        room['status'] = 'finished'
        
        # Update database
        if room['game_id']:
            game = Game.query.get(room['game_id'])
            if game:
                game.result = result
                db.session.commit()
        
        emit('game_ended', {
            'result': result,
            'reason': reason,
        }, room=room_id)
        
        # Clean up room after a delay
        # In production, schedule this properly
    
    @socketio.on('get_rooms')
    def handle_get_rooms():
        """Get list of available rooms."""
        emit('room_list', get_available_rooms())
    
    @socketio.on('leave_room')
    def handle_leave_room(data):
        """Leave the current room."""
        user_id = session.get('user_id')
        room_id = data.get('room_id') or user_rooms.get(user_id)
        
        if room_id:
            leave_game_room(user_id, room_id)
            emit('room_left', {'room_id': room_id})
            emit('room_list_updated', get_available_rooms(), broadcast=True)
    
    def leave_game_room(user_id, room_id):
        """Helper to leave a room and clean up."""
        if room_id in rooms:
            room = rooms[room_id]
            
            if room['host_id'] == user_id:
                # Host left, notify guest and remove room
                emit('opponent_left', {'message': 'Host left the game'}, room=room_id)
                del rooms[room_id]
            elif room['guest_id'] == user_id:
                # Guest left
                room['guest_id'] = None
                room['guest_name'] = None
                room['status'] = 'waiting'
                emit('opponent_left', {'message': 'Opponent left the game'}, room=room_id)
            
            leave_room(room_id)
        
        if user_id in user_rooms:
            del user_rooms[user_id]
    
    def get_available_rooms():
        """Get list of rooms waiting for players."""
        return [
            {
                'id': r['id'],
                'host_name': r['host_name'],
                'time_control': r['time_control'],
                'created_at': r['created_at'],
            }
            for r in rooms.values()
            if r['status'] == 'waiting'
        ]
    
    return socketio
