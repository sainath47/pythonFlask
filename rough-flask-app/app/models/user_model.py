# app/models/user_model.py

from app import db

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullname = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    mobile = db.Column(db.String(45), nullable=True)  # Adjust as needed
    password = db.Column(db.String(255), nullable=False)
    organisation = db.Column(db.String(255), nullable=True)  # Adjust as needed

    def __init__(self, fullname, email, password, mobile=None, organisation=None):
        self.fullname = fullname
        self.email = email
        self.mobile = mobile
        self.password = password
        self.organisation = organisation
