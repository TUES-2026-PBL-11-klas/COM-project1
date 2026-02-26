from flask import Blueprint, request, jsonify, current_app
import re
from functools import wraps
import jwt
from services.auth_service import AuthService
from repository.user_repository import UserRepository

auth_bp = Blueprint('auth', __name__, url_prefix='/api/users/v1.0')

def is_valid_email(email: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired — please log in again"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token — please log in again"}), 401

        username = payload.get("sub")
        user = UserRepository.get_by_username(username)
        if not user:
            return jsonify({"error": "User no longer exists"}), 401

        request.current_user = user
        return f(*args, **kwargs)
    return decorated


@auth_bp.route("/register", methods=["POST"])
def register():
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

    result, status = AuthService.register_user(username, email, password)
    return jsonify(result), status


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    result, status = AuthService.login_user(username, password)
    return jsonify(result), status

@auth_bp.route("/logout", methods=["POST"])
@jwt_required
def logout():
    username = request.current_user.username
    return jsonify({"message": f"User '{username}' logged out successfully — discard your token"}), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required
def me():
    user = request.current_user
    return jsonify(user.to_dict()), 200
