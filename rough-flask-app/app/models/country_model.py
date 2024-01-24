# app/models/countries_model.py
from app import db

class Country(db.Model):
    __tablename__ = 'countries'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(20), nullable=False)
    emoji = db.Column(db.String(10), nullable=False)
    unicode = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(255), nullable=False)

    def __init__(self, name, country, emoji, unicode, image):
        self.name = name
        self.country = country
        self.emoji = emoji
        self.unicode = unicode
        self.image = image

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'emoji': self.emoji,
            'unicode': self.unicode,
            'image': self.image
        }
