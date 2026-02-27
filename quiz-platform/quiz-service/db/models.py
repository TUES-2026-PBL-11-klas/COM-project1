import uuid
from db.quiz_db import db


def _gen_uuid():
    return str(uuid.uuid4())


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Text, primary_key=True, default=_gen_uuid)
    name = db.Column(db.Text, nullable=False, unique=True)
    # ENUM-like constraint kept as Text; enforce at app level or via DB check
    subject_type = db.Column(db.Text, nullable=False)  # 'math' | 'physics' | 'it'

    quizzes = db.relationship("Quiz", back_populates="subject", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "subject_type": self.subject_type,
        }


class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Text, primary_key=True, default=_gen_uuid)
    title = db.Column(db.Text, nullable=False)
    subject_id = db.Column(db.Text, db.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)

    subject = db.relationship("Subject", back_populates="quizzes")
    questions = db.relationship("Question", back_populates="quiz", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "subject_id": self.subject_id,
        }


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Text, primary_key=True, default=_gen_uuid)
    quiz_id = db.Column(db.Text, db.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    condition = db.Column(db.Text, nullable=False)

    quiz = db.relationship("Quiz", back_populates="questions")
    options = db.relationship("Option", back_populates="question", cascade="all, delete-orphan")

    def to_dict(self, include_answers=False):
        d = {
            "id": self.id,
            "quiz_id": self.quiz_id,
            "condition": self.condition,
            "options": [o.to_dict(include_answer=include_answers) for o in self.options],
        }
        return d


class Option(db.Model):
    __tablename__ = "options"

    id = db.Column(db.Text, primary_key=True, default=_gen_uuid)
    question_id = db.Column(db.Text, db.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)

    question = db.relationship("Question", back_populates="options")

    def to_dict(self, include_answer=False):
        d = {
            "id": self.id,
            "question_id": self.question_id,
            "option_text": self.option_text,
        }
        if include_answer:
            d["is_correct"] = self.is_correct
        return d
