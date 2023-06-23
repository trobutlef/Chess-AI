#!usr/bin/env python3
from flask import Flask, Response, request, render_template
import engine

app = Flask(__name__)

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/takeback")
def takeback():
  return "<h1>hello</h1>"

#make an endpoint for the takeback
@app.route("/takeback/<int:move>")
def takeback_move(move):
  engine.takeback(move)
  return render_template("index.html")

@app.route("/newgame")
def newgame():
  s.board()


if __name__ == "__main__":
  # add option to play with itself
  app.run(debug=True, port=4000)
