from repository.subject_repository import SubjectRepository
from repository.quiz_repository import QuizRepository
from repository.question_repository import QuestionRepository


class QuizService:
    @staticmethod
    def get_subjects(limit, offset):
        subjects = SubjectRepository.get_all(limit=limit, offset=offset)
        return [s.to_dict() for s in subjects], 200

    @staticmethod
    def get_quizzes(limit, offset, subject_id=None, search=None):
        if subject_id is not None:
            # Validate the subject exists
            if SubjectRepository.get_by_id(subject_id) is None:
                return {"error": f"Subject '{subject_id}' not found"}, 404
        quizzes = QuizRepository.get_all(limit=limit, offset=offset, subject_id=subject_id, search=search)
        return [q.to_dict() for q in quizzes], 200

    @staticmethod
    def get_quiz(quiz_id):
        quiz = QuizRepository.get_by_id(quiz_id)
        if quiz is None:
            return {"error": f"Quiz '{quiz_id}' not found"}, 404
        return quiz.to_dict(), 200

    @staticmethod
    def get_questions(quiz_id, limit, offset):
        if QuizRepository.get_by_id(quiz_id) is None:
            return {"error": f"Quiz '{quiz_id}' not found"}, 404
        questions = QuestionRepository.get_by_quiz(quiz_id, limit=limit, offset=offset)
        # Public endpoint — answers hidden
        return [q.to_dict(include_answers=False) for q in questions], 200

    @staticmethod
    def get_answer_key(quiz_id):
        if QuizRepository.get_by_id(quiz_id) is None:
            return {"error": f"Quiz '{quiz_id}' not found"}, 404
        questions = QuestionRepository.get_by_quiz(quiz_id, limit=10_000, offset=0)
        # Internal endpoint — answers included
        return [q.to_dict(include_answers=True) for q in questions], 200
