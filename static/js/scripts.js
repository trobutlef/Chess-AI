var board,
  game = new Chess()
  sstatusEl = $('#status'),
  fenEl = $('#fen'),
  pgnEl = $('#pgn');


var onDragStart = function(source, piece, position, orientation) {
  if ( (game.game_over() == true) || (game.turn() === 'w' && piece.search(/^b/) !== -1) || (game.turn() === 'b' && piece.search(/^w/) !== -1)  ) {
    return false;
  }
};

var onDrop = function(source, target) {
  var move = game.move({
    from: source,
    to: target,
    promotion: 'q'
  });

  //verifying illegal move
  if (move == null) return 'snapback';

  //updateStatus();
  //getResponseMove();
};

