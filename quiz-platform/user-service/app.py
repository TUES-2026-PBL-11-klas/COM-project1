from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime
import re
import jwt

app = Flask(__name__)
app.config["JWT_SECRET"] = "change-this-to-a-secure-random-secret-key"  # Change in production!
app.config["JWT_EXPIRY_HOURS"] = 12

# In-memory user store (replace with a real database in production)
users = {}


def is_valid_email(email: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=app.config["JWT_EXPIRY_HOURS"]),
    }
    return jwt.encode(payload, app.config["JWT_SECRET"], algorithm="HS256")


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, app.config["JWT_SECRET"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired — please log in again"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token — please log in again"}), 401

        username = payload.get("sub")
        if username not in users:
            return jsonify({"error": "User no longer exists"}), 401

        request.current_user = users[username]
        return f(*args, **kwargs)
    return decorated


@app.route("/api/v1.0/register", methods=["POST"])
def register():
    """
    Expected JSON body:
        {
            "username": "user67",
            "email": "funni@example.com",
            "password": "securepassword6767"
        }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username:
        return jsonify({"error": "Username is required"}), 400
    if not email or not is_valid_email(email):
        return jsonify({"error": "A valid email address is required"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    if username in users:
        return jsonify({"error": "Username already taken"}), 409
    if any(u["email"] == email for u in users.values()):
        return jsonify({"error": "Email already registered"}), 409

    users[username] = {
        "username": username,
        "email": email,
        "password_hash": generate_password_hash(password),
    }
    return jsonify({"message": f"User '{username}' registered successfully"}), 201


@app.route("/api/v1.0/login", methods=["POST"])
def login():
    """
    Expected JSON body:
        {
            "username": "user67",
            "password": "securepassword6767"
        }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = users.get(username)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    token = create_token(username)
    return jsonify({"message": f"Welcome back, {username}!", "token": token}), 200


@app.route("/api/v1.0/logout", methods=["POST"])
@jwt_required
def logout():
    username = request.current_user["username"]
    return jsonify({"message": f"User '{username}' logged out successfully — discard your token"}), 200


@app.route("/api/v1.0/me", methods=["GET"])
@jwt_required
def me():
    user = request.current_user
    return jsonify({"username": user["username"], "email": user["email"]}), 200


if __name__ == "__main__":
    app.run(debug=True)