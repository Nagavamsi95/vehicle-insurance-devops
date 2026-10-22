# app/main.py
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from app.model import estimate_premium

BASE_DIR = Path(__file__).resolve().parent.parent
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/quote", methods=["GET", "POST"])
def quote_page():
    if request.method == "GET":
        return render_template("quote.html")
    try:
        premium = estimate_premium(
            vehicle_age=int(request.form["vehicle_age"]),
            driver_age=int(request.form["driver_age"]),
            vehicle_value=float(request.form["vehicle_value"]),
        )
    except (KeyError, ValueError):
        return render_template("quote.html", error="Please fill in all fields with valid numbers."), 400
    return render_template("result.html", premium=round(premium, 2))


@app.route("/api/quote", methods=["POST"])
def api_quote():
    data = request.get_json(silent=True) or {}
    try:
        premium = estimate_premium(
            vehicle_age=int(data["vehicle_age"]),
            driver_age=int(data["driver_age"]),
            vehicle_value=float(data["vehicle_value"]),
        )
    except (KeyError, ValueError, TypeError):
        return jsonify(error="vehicle_age, driver_age and vehicle_value are required"), 400
    return jsonify(premium=round(premium, 2)), 200


@app.route("/health")
def health():
    return jsonify(status="ok"), 200