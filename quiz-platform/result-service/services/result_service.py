import requests
import os
from repository.result_repository import ResultRepository

class ResultService:

    @staticmethod
    def submit_attempt(username: str, quiz_id: str, submitted_answers: list):
        quiz_service_url = os.environ.get("QUIZ_SERVICE_URL", "http://quiz-service:5001")
        # 1. Fetch correct answers from quiz-service internally
        try:
            url = f"{quiz_service_url}/api/quiz/v1.0/internal/quizzes/{quiz_id}/answer-key"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 404:
                return {"error": f"Quiz not found: {quiz_id}"}, 404
            elif response.status_code != 200:
                print(f"Error calling quiz-service: {response.status_code} - {response.text}")
                return {"error": "Failed to retrieve quiz details from quiz-service"}, 500
                
            quiz_data = response.json()
            correct_answers_map = {}
            for question in quiz_data:
                correct_opt = next((opt["id"] for opt in question.get("options", []) if opt.get("is_correct")), None)
                if correct_opt:
                    correct_answers_map[question["id"]] = correct_opt
                
        except requests.exceptions.RequestException as e:
            print(f"Connection error to quiz-service: {e}")
            return {"error": "Failed to connect to quiz-service"}, 500

        # 2. Evaluate answers
        total_questions = len(correct_answers_map)
        score = 0
        processed_answers = []

        # Convert submitted answers into a lookup dict
        # submitted format: [{"question_id": "...", "selected_option_id": "..."}, ...]
        submitted_lookup = {item["question_id"]: item.get("selected_option_id") for item in submitted_answers}

        for q_id, correct_opt_id in correct_answers_map.items():
            selected_opt_id = submitted_lookup.get(q_id)
            is_correct = (selected_opt_id == correct_opt_id) if selected_opt_id else False
            
            if is_correct:
                score += 1
                
            processed_answers.append({
                "question_id": q_id,
                "selected_option_id": selected_opt_id,
                "is_correct": is_correct
            })

        # 3. Store result
        try:
            attempt = ResultRepository.create_attempt(
                username=username,
                quiz_id=quiz_id,
                score=score,
                total=total_questions,
                answers_data=processed_answers
            )
            return attempt.to_dict(), 201
        except Exception as e:
            print(f"Database error saving attempt: {e}")
            return {"error": "Failed to save attempt to database"}, 500

    @staticmethod
    def get_attempts(username: str):
        attempts = ResultRepository.get_attempts_by_username(username)
        # return basic attempt data, omit detailed answers mapping for list view
        return [
            {
                "id": a.id,
                "quiz_id": a.quiz_id,
                "score": a.score,
                "total": a.total,
                "created_at": a.created_at.isoformat() if a.created_at else None
            } 
            for a in attempts
        ], 200

    @staticmethod
    def get_attempt_details(username: str, attempt_id: str):
        attempt = ResultRepository.get_attempt_by_id(attempt_id)
        if not attempt:
            return {"error": "Attempt not found"}, 404
            
        # Ensure users can only see their own attempts
        if attempt.username != username:
            return {"error": "You do not have permission to view this attempt"}, 403
            
        return attempt.to_dict(), 200
