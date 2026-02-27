from db.models import Question
from db.quiz_db import db


class QuestionRepository:
    @staticmethod
    def get_by_quiz(quiz_id, limit=20, offset=0):
        return (
            db.session.query(Question)
            .filter(Question.quiz_id == quiz_id)
            .order_by(Question.id)
            .limit(limit)
            .offset(offset)
            .all()
        )
