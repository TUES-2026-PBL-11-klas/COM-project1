import datetime
import jwt
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from repository.user_repository import UserRepository

class AuthService:
    @staticmethod
    def register_user(username, email, password):
        if len(password) < 8:
            return {"error": "Password must be at least 8 characters"}, 400
            
        if UserRepository.get_by_username(username):
            return {"error": "Username already taken"}, 409
            
        if UserRepository.get_by_email(email):
            return {"error": "Email already registered"}, 409
            
        hashed_pw = generate_password_hash(password)
        UserRepository.create_user(username, email, hashed_pw)
        return {"message": f"User '{username}' registered successfully"}, 201

    @staticmethod
    def login_user(username, password):
        user = UserRepository.get_by_username(username)
        if not user or not check_password_hash(user.password_hash, password):
            return {"error": "Invalid username or password"}, 401

        payload = {
            "sub": user.username,
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=current_app.config["JWT_EXPIRY_HOURS"]),
        }
        token = jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")
        
        return {"message": f"Welcome back, {username}!", "token": token}, 200
