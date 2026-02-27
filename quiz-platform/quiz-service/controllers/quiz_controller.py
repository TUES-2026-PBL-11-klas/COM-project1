from flask import Blueprint, request, jsonify
from services.quiz_service import QuizService

quiz_bp = Blueprint("quiz", __name__, url_prefix="/api/quiz/v1.0")


def _pagination_params():
    try:
        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return None, None, (jsonify({"error": "'limit' and 'offset' must be integers"}), 400)
    if limit < 1 or limit > 200:
        return None, None, (jsonify({"error": "'limit' must be between 1 and 200"}), 400)
    if offset < 0:
        return None, None, (jsonify({"error": "'offset' must be >= 0"}), 400)
    return limit, offset, None


@quiz_bp.route("/subjects", methods=["GET"])
def get_subjects():
    limit, offset, err = _pagination_params()
    if err:
        return err
    result, status = QuizService.get_subjects(limit, offset)
    return jsonify(result), status


@quiz_bp.route("/quizzes", methods=["GET"])
def get_quizzes():
    limit, offset, err = _pagination_params()
    if err:
        return err
    subject_id = request.args.get("subject")  # optional
    result, status = QuizService.get_quizzes(limit, offset, subject_id=subject_id)
    return jsonify(result), status


@quiz_bp.route("/quizzes/<quiz_id>/questions", methods=["GET"])
def get_questions(quiz_id):
    limit, offset, err = _pagination_params()
    if err:
        return err
    result, status = QuizService.get_questions(quiz_id, limit, offset)
    return jsonify(result), status


@quiz_bp.route("/internal/quizzes/<quiz_id>/answer-key", methods=["GET"])
def get_answer_key(quiz_id):
    result, status = QuizService.get_answer_key(quiz_id)
    return jsonify(result), status
