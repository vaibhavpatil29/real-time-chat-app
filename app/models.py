from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text)


    def __repr__(self):
        return f"<User {self.username}>"
    from datetime import datetime
from app import db

# app/models.py

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    room = db.Column(db.String(100))

    # NEW FIELDS for private messaging
    recipient = db.Column(db.String(100), nullable=True)  # recipient username
    is_private = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Message from {self.username} to {self.recipient or self.room}>"




