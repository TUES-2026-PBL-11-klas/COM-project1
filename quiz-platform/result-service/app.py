import os
from flask import Flask
from db.result_db import db
from controllers.result_controller import result_bp

def create_app():
    app = Flask(__name__)

    app.config["JWT_SECRET"] = os.environ.get("JWT_SECRET", "change-this-to-a-secure-random-secret-key")
    
    # Database config
    db_url = os.environ.get("DATABASE_URL", "sqlite:///results.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        from db import models
        db.create_all()

    app.register_blueprint(result_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)