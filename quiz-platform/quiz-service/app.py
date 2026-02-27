import os
from flask import Flask
from db.quiz_db import db
from controllers.quiz_controller import quiz_bp


def create_app():
    app = Flask(__name__)

    # Database config — default to SQLite for local dev
    db_url = os.environ.get("QUIZ_DB_URL", "sqlite:///quiz.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        from db import models
        db.create_all()

    app.register_blueprint(quiz_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)