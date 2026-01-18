"""
Tests for the game history API endpoints.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(__file__, os.pardir, os.pardir)))

import pytest
from app import app as flask_app, db, User, Game


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    
    with flask_app.app_context():
        db.create_all()
        # Create test user
        user = User(email="test@example.com", name="Test User")
        db.session.add(user)
        db.session.commit()
        test_user_id = user.id
    
    with flask_app.test_client() as c:
        with c.session_transaction() as sess:
            sess["user_id"] = test_user_id
        yield c
    
    with flask_app.app_context():
        db.drop_all()


@pytest.fixture
def unauthenticated_client():
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    
    with flask_app.app_context():
        db.create_all()
    
    with flask_app.test_client() as c:
        yield c
    
    with flask_app.app_context():
        db.drop_all()


class TestLogout:
    def test_logout_clears_session(self, client):
        """Logout should clear the session."""
        res = client.post("/api/logout")
        assert res.status_code == 200
        assert res.get_json()["message"] == "Logged out successfully"
    
    def test_me_after_logout(self, client):
        """After logout, /api/me should return null user."""
        client.post("/api/logout")
        res = client.get("/api/me")
        assert res.status_code == 200
        assert res.get_json()["user"] is None


class TestGameCRUD:
    def test_create_game(self, client):
        """Should create a new game."""
        res = client.post("/api/games", json={
            "engine": "neural",
            "depth": 4,
            "user_color": "black",
            "time_control": 300
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["engine"] == "neural"
        assert data["depth"] == 4
        assert data["user_color"] == "black"
        assert data["time_control"] == 300
        assert "id" in data
    
    def test_list_games_empty(self, client):
        """Should return empty list when no games."""
        res = client.get("/api/games")
        assert res.status_code == 200
        assert res.get_json()["games"] == []
    
    def test_list_games_with_games(self, client):
        """Should list created games."""
        # Create a game
        client.post("/api/games", json={"engine": "minimax"})
        
        res = client.get("/api/games")
        assert res.status_code == 200
        games = res.get_json()["games"]
        assert len(games) == 1
        assert games[0]["engine"] == "minimax"
    
    def test_get_single_game(self, client):
        """Should get a specific game."""
        create_res = client.post("/api/games", json={"engine": "neural"})
        game_id = create_res.get_json()["id"]
        
        res = client.get(f"/api/games/{game_id}")
        assert res.status_code == 200
        assert res.get_json()["engine"] == "neural"
    
    def test_get_nonexistent_game(self, client):
        """Should return 404 for nonexistent game."""
        res = client.get("/api/games/99999")
        assert res.status_code == 404
    
    def test_add_move_to_game(self, client):
        """Should add moves to game PGN."""
        create_res = client.post("/api/games", json={})
        game_id = create_res.get_json()["id"]
        
        # Add first move
        res = client.post(f"/api/games/{game_id}/move", json={"move": "e4"})
        assert res.status_code == 200
        assert "1. e4" in res.get_json()["pgn"]
        
        # Add second move
        res = client.post(f"/api/games/{game_id}/move", json={"move": "e5"})
        assert "e5" in res.get_json()["pgn"]
    
    def test_update_time_and_result(self, client):
        """Should update game times and result."""
        create_res = client.post("/api/games", json={"time_control": 300})
        game_id = create_res.get_json()["id"]
        
        res = client.post(f"/api/games/{game_id}/move", json={
            "move": "e4",
            "white_time": 290000,
            "result": "1-0"
        })
        assert res.status_code == 200
        
        game_res = client.get(f"/api/games/{game_id}")
        game = game_res.get_json()
        assert game["white_time"] == 290000
        assert game["result"] == "1-0"
    
    def test_delete_game(self, client):
        """Should delete a game."""
        create_res = client.post("/api/games", json={})
        game_id = create_res.get_json()["id"]
        
        res = client.delete(f"/api/games/{game_id}")
        assert res.status_code == 200
        
        # Verify deleted
        get_res = client.get(f"/api/games/{game_id}")
        assert get_res.status_code == 404


class TestAuthentication:
    def test_list_games_unauthenticated(self, unauthenticated_client):
        """Should return 401 when not authenticated."""
        res = unauthenticated_client.get("/api/games")
        assert res.status_code == 401
    
    def test_create_game_unauthenticated(self, unauthenticated_client):
        """Should return 401 when not authenticated."""
        res = unauthenticated_client.post("/api/games", json={})
        assert res.status_code == 401
