import json
from pathlib import Path

from flask import Flask, jsonify, render_template


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "static" / "data"

app = Flask(__name__)


def read_json(filename):
    with (DATA_DIR / filename).open(encoding="utf-8") as handle:
        return json.load(handle)
    

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/team-rosters")
def team_rosters():
    return render_template("team-rosters.html")


@app.route("/methodology")
def methodology():
    return render_template("methodology.html")


@app.route("/api/data")
def app_data():
    return jsonify(read_json("nba_app_data.json"))


if __name__ == "__main__":
    app.run(debug=True)
