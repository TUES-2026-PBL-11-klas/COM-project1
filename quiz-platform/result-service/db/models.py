import uuid
from datetime import datetime
from db.result_db import db

def _gen_uuid():
    return str(uuid.uuid4())

class Attempt(db.Model):
    __tablename__ = "attempts"

    id = db.Column(db.Text, primary_key=True, default=_gen_uuid)
    username = db.Column(db.Text, nullable=False)
    quiz_id = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)
    total = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    answers = db.relationship("Answer", back_populates="attempt", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "quiz_id": self.quiz_id,
            "score": self.score,
            "total": self.total,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "answers": [a.to_dict() for a in self.answers]
        }

class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Text, primary_key=True, default=_gen_uuid)
    attempt_id = db.Column(db.Text, db.ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = db.Column(db.Text, nullable=False)
    selected_option_id = db.Column(db.Text, nullable=True) # can be null if skipped
    is_correct = db.Column(db.Boolean, default=False, nullable=False)

    attempt = db.relationship("Attempt", back_populates="answers")

    def to_dict(self):
        return {
            "id": self.id,
            "question_id": self.question_id,
            "selected_option_id": self.selected_option_id,
            "is_correct": self.is_correct
        }
