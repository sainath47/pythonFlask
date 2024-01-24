# app/models/otp_model.py
from app import db

class OTP(db.Model):
    __tablename__ = 'otps'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    otp = db.Column(db.String(10))
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

    def __init__(self, user_id, otp):
        self.user_id = user_id
        self.otp = otp
