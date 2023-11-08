# app/controllers/user_controller.py

from flask import request, jsonify
from app.models.user_model import User
from app import db

def create_user_route():
    data = request.get_json()
    username = data['username']
    email = data['email']
    
    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'})

def list_users_route():
    users = User.query.all()
    user_list = [{'username': user.username, 'email': user.email} for user in users]
    return jsonify({'users': user_list})
