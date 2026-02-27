import os
from flask import Flask
from db.database import db
from controllers.auth_controller import auth_bp

def create_app():
    app = Flask(__name__)
    
    app.config["JWT_SECRET"] = os.environ.get("JWT_SECRET", "change-this-to-a-secure-random-secret-key")
    app.config["JWT_EXPIRY_HOURS"] = int(os.environ.get("JWT_EXPIRY_HOURS", 12))
    
    # Database config
    db_url = os.environ.get("USER_DB_URL", "sqlite:///users.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)