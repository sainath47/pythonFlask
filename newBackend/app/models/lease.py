from app import db
from datetime import datetime

class Lease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lease_number = db.Column(db.String(20), unique=True, index=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __init__(self, lease_number, start_date, end_date):
        self.lease_number = lease_number
        self.start_date = start_date
        self.end_date = end_date

    def __repr__(self):
        return f"<Lease {self.lease_number}>"
