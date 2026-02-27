from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
from services.result_service import ResultService

result_bp = Blueprint("result", __name__, url_prefix="/api/results/v1.0")

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("jwt")
        if not token:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1]

        if not token:
            return jsonify({"error": "Missing authentication token"}), 401
        
        try:
            # We assume user-service issued tokens using same JWT_SECRET
            payload = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        request.current_username = payload.get("sub")
        if not request.current_username:
             return jsonify({"error": "Token subject missing"}), 401

        return f(*args, **kwargs)
    return decorated


@result_bp.route("/attempts", methods=["POST"])
@jwt_required
def submit_attempt():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    quiz_id = data.get("quiz_id")
    answers = data.get("answers") # Expected format: [{"question_id": "...", "selected_option_id": "..."}]
    elapsed_seconds = data.get("elapsed", 0)

    if not quiz_id:
        return jsonify({"error": "quiz_id is required"}), 400
    
    if not isinstance(answers, list):
         return jsonify({"error": "answers must be a list of objects"}), 400

    username = request.current_username
    result, status = ResultService.submit_attempt(username, quiz_id, elapsed_seconds, answers)
    
    return jsonify(result), status

@result_bp.route("/attempts", methods=["GET"])
@jwt_required
def get_attempts():
    username = request.current_username
    result, status = ResultService.get_attempts(username)
    return jsonify(result), status

@result_bp.route("/attempts/<attempt_id>", methods=["GET"])
@jwt_required
def get_attempt_details(attempt_id):
    username = request.current_username
    result, status = ResultService.get_attempt_details(username, attempt_id)
    return jsonify(result), status
