from db.result_db import db
from db.models import Attempt, Answer
from sqlalchemy.orm import joinedload

class ResultRepository:

    @staticmethod
    def create_attempt(username: str, quiz_id: str, score: int, total: int, elapsed_seconds: int, answers_data: list) -> Attempt:
        attempt = Attempt(
            username=username,
            quiz_id=quiz_id,
            score=score,
            total=total,
            elapsed_seconds=elapsed_seconds
        )
        
        for ans_data in answers_data:
            answer = Answer(
                question_id=ans_data["question_id"],
                selected_option_id=ans_data.get("selected_option_id"),
                correct_option_id=ans_data.get("correct_option_id"),
                is_correct=ans_data["is_correct"]
            )
            attempt.answers.append(answer)

        db.session.add(attempt)
        db.session.commit()
        return attempt

    @staticmethod
    def get_attempts_by_username(username: str):
        # order by newest first
        return Attempt.query.filter_by(username=username).order_by(Attempt.created_at.desc()).all()

    @staticmethod
    def get_attempt_by_id(attempt_id: str):
        return Attempt.query.options(joinedload(Attempt.answers)).filter_by(id=attempt_id).first()
