from db.models import Subject
from db.quiz_db import db


class SubjectRepository:
    @staticmethod
    def get_all(limit=20, offset=0):
        return (
            db.session.query(Subject)
            .order_by(Subject.id)
            .limit(limit)
            .offset(offset)
            .all()
        )

    @staticmethod
    def get_by_id(subject_id):
        return db.session.get(Subject, subject_id)
