# Authentication routes for user registration and login
from flask import request, jsonify
from flask_jwt_extended import create_access_token
from backend.models.table_models import db, User

# Register a new user
def register_user(data):
    # Check if user already exists
    if User.query.filter_by(email = data['email']).first():
        return {"msg" : "User already exists"}, 400

    # Create new user instance
    user = User(
        email=data['email'],
        full_name=data['full_name'],
        address=data['address'],
        pincode=data['pincode']
    )

    # Hash and store password
    user.hash_password(data['password'])

    # Add user to database
    db.session.add(user)
    db.session.commit()

    return {"msg" : "User registered successfully"}, 201

# Login user and return JWT token
def login_user(data):
    user = User.query.filter_by(email = data['email']).first()

    # Validate credentials
    if not user or not user.check_password(data['password']):
        return {"msg" : "Invalid credentials"}, 401

    # Generate JWT access token
    access_token = create_access_token(identity=str(user.id))  # Use user ID as string

    return {'access_token': access_token, 'role': user.role, 'user_id': user.id}, 200