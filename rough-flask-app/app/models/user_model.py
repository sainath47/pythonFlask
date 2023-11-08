# app/models/user_model.py

from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Make 'age' and 'occupation' optional with default values of None
    age = db.Column(db.Integer, default=None)
    occupation = db.Column(db.String(120), default=None)

    def __init__(self, username, email, age=None, occupation=None):
        self.username = username
        self.email = email
        self.age = age
        self.occupation = occupation
