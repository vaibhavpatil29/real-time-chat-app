from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from time import time
import jwt
from flask import current_app

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)  # Optional for OAuth users
    
    # Authentication fields
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(100), unique=True)
    password_reset_token = db.Column(db.String(100), unique=True)
    password_reset_expires = db.Column(db.DateTime)
    
    # Profile fields
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    avatar_url = db.Column(db.String(200))
    bio = db.Column(db.Text)
    
    # OAuth fields
    google_id = db.Column(db.String(100), unique=True)
    oauth_provider = db.Column(db.String(50))  # 'google', 'github', etc.
    
    # Activity tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Security fields
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32))
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def generate_email_verification_token(self):
        """Generate email verification token"""
        self.email_verification_token = secrets.token_urlsafe(32)
        return self.email_verification_token
    
    def verify_email_token(self, token):
        """Verify email verification token"""
        if self.email_verification_token == token:
            self.email_verified = True
            self.email_verification_token = None
            return True
        return False
    
    def generate_password_reset_token(self, expires_in=3600):
        """Generate password reset token (expires in 1 hour by default)"""
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_expires = datetime.utcnow() + datetime.timedelta(seconds=expires_in)
        return self.password_reset_token
    
    def verify_password_reset_token(self, token):
        """Verify password reset token"""
        if (self.password_reset_token == token and 
            self.password_reset_expires and 
            datetime.utcnow() < self.password_reset_expires):
            return True
        return False
    
    def reset_password(self, new_password):
        """Reset password and clear reset token"""
        self.set_password(new_password)
        self.password_reset_token = None
        self.password_reset_expires = None
        self.failed_login_attempts = 0
        self.account_locked_until = None
    
    def is_account_locked(self):
        """Check if account is locked due to failed login attempts"""
        if self.account_locked_until:
            if datetime.utcnow() < self.account_locked_until:
                return True
            else:
                # Lock period expired, reset
                self.account_locked_until = None
                self.failed_login_attempts = 0
        return False
    
    def increment_failed_login(self):
        """Increment failed login attempts and lock account if needed"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:  # Lock after 5 failed attempts
            self.account_locked_until = datetime.utcnow() + datetime.timedelta(minutes=30)
    
    def successful_login(self):
        """Reset failed login attempts on successful login"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.last_login = datetime.utcnow()
        self.last_seen = datetime.utcnow()
    
    def update_last_seen(self):
        """Update last seen timestamp"""
        self.last_seen = datetime.utcnow()
    
    def get_full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.get_full_name(),
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'is_active': self.is_active
        }

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




