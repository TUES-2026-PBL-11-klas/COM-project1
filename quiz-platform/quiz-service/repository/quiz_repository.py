from db.models import Quiz
from db.quiz_db import db


class QuizRepository:
    @staticmethod
    def get_all(limit=20, offset=0, subject_id=None):
        q = db.session.query(Quiz)
        if subject_id is not None:
            q = q.filter(Quiz.subject_id == subject_id)
        return q.order_by(Quiz.id).limit(limit).offset(offset).all()

    @staticmethod
    def get_by_id(quiz_id):
        return db.session.get(Quiz, quiz_id)
