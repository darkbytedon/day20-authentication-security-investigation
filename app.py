import os
from datetime import timedelta

from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[]
)

# Simulated user database
users = {
    "alice": {
        "username": "alice",
        "password": generate_password_hash("alice123")
    },
    "bob": {
        "username": "bob",
        "password": generate_password_hash("bob123")
    }
}


@app.post("/api/login")
@limiter.limit("5 per minute")
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "Username and password required"}), 400

    user = users.get(username)

    # Prevent username enumeration
    if user is None or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Create authenticated session
    session["username"] = user["username"]
    session.permanent = True

    return jsonify({"message": "Login successful"}), 200

@app.get("/api/profile")
def profile():
    username = session.get("username")

    if username is None:
        return jsonify({"error": "Authentication required"}), 401

    return jsonify({"username": username}), 200
@app.post("/api/logout")
def logout():
    session.clear()

    return jsonify({"message": "Logged out successfully"}), 200


if __name__ == "__main__":
    app.run(debug=False, port=5002)
