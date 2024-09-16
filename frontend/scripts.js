// frontend/scripts.js
$(document).ready(function () {
  var board = null;
  var game = null;
  var fen = null;
  var playerColor = "white";
  var $status = $("#status");
  var apiUrl = "http://localhost:5000/api"; // Adjust the port if necessary

  function initGame() {
    $.ajax({
      url: apiUrl + "/new_game",
      type: "GET",
      success: function (response) {
        fen = response.fen;
        game = new Chess(fen);
        board.position(fen);
        updateStatus();
      },
    });
  }

  function onDragStart(source, piece, position, orientation) {
    if (game.game_over()) return false;
    if (piece.search(/^b/) !== -1) return false; // Only allow moving white pieces
  }

  function onDrop(source, target) {
    var move = game.move({
      from: source,
      to: target,
      promotion: "q", // Promote to queen if needed
    });

    if (move === null) return "snapback";

    updateStatus();

    // Send move to server
    $.ajax({
      url: apiUrl + "/make_move",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        fen: game.fen(),
        move: move.from + move.to + (move.promotion ? move.promotion : ""),
      }),
      success: function (response) {
        game.load(response.fen);
        board.position(game.fen());
        updateStatus();
        if (response.game_over) {
          alert("Game Over. Result: " + (response.result || "Draw"));
        }
      },
      error: function (xhr, status, error) {
        alert("Error: " + xhr.responseJSON.error);
        game.undo();
        board.position(game.fen());
      },
    });
  }

  function updateStatus() {
    var status = "";

    if (game.in_checkmate()) {
      status =
        "Game over, " +
        (game.turn() === "w" ? "Black" : "White") +
        " wins by checkmate.";
    } else if (game.in_draw()) {
      status = "Game over, draw.";
    } else {
      status = (game.turn() === "w" ? "White" : "Black") + " to move";
      if (game.in_check()) {
        status +=
          ", " + (game.turn() === "w" ? "White" : "Black") + " is in check";
      }
    }

    $status.text(status);
  }

  var config = {
    draggable: true,
    position: "start",
    onDragStart: onDragStart,
    onDrop: onDrop,
    orientation: playerColor,
  };
  board = Chessboard("myBoard", config);

  // Start a new game when the page loads
  initGame();

  // Event handlers for buttons
  $("#startGameBtn").on("click", function () {
    window.location.href = "game.html";
  });
});
