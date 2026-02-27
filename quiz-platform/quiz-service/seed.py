import uuid
from app import create_app
from db.quiz_db import db
from db.models import Subject, Quiz, Question, Option

app = create_app()

with app.app_context():
    # 1. Subject
    math = Subject(name="Mathematics", subject_type="math")
    physics = Subject(name="Physics", subject_type="physics")
    db.session.add_all([math, physics])
    db.session.commit()

    # 2. Quiz
    quiz1 = Quiz(title="Basic Math", subject_id=math.id)
    db.session.add(quiz1)
    db.session.commit()

    # 3. Question
    q1 = Question(quiz_id=quiz1.id, condition="What is 2+2?")
    db.session.add(q1)
    db.session.commit()

    # 4. Options
    o1 = Option(question_id=q1.id, option_text="3", is_correct=False)
    o2 = Option(question_id=q1.id, option_text="4", is_correct=True)
    o3 = Option(question_id=q1.id, option_text="5", is_correct=False)
    db.session.add_all([o1, o2, o3])
    db.session.commit()

    print("Seeding complete!")
