#!/usr/bin/env python3
"""
Simple database initialization script for the chat application
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init, migrate, upgrade
from config import config

def init_database():
    """Initialize database and create tables"""
    
    # Get configuration
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db = SQLAlchemy(app)
    migrate_obj = Migrate(app, db)
    
    with app.app_context():
        try:
            # Import models to ensure they're registered
            from app.models import User, Message
            
            print("Creating database tables...")
            
            # Check if migrations directory exists
            migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
            if not os.path.exists(migrations_dir):
                print("Initializing migrations directory...")
                init()
            
            # Create migration
            print("Generating migration script...")
            migrate(message="Initial migration with enhanced authentication")
            
            # Apply migration
            print("Applying migration to database...")
            upgrade()
            
            print("SUCCESS: Database initialization completed!")
            print("\nNew authentication features available:")
            print("  - Enhanced User model with security fields")
            print("  - Email verification system")
            print("  - Password reset functionality")
            print("  - Account locking for failed login attempts")
            print("  - User profile fields")
            print("  - Activity tracking")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Database initialization failed: {str(e)}")
            print("\nTroubleshooting steps:")
            print("1. Ensure PostgreSQL is running")
            print("2. Check database connection settings in config.py")
            print("3. Verify database user has CREATE permissions")
            print("4. Check if database 'chatdb' exists")
            return False

if __name__ == '__main__':
    print("ChatApp Database Initialization")
    print("=" * 40)
    
    if init_database():
        print("\nDatabase ready! Start your application with: python run.py")
    else:
        print("\nDatabase initialization failed. Please check the errors above.")
        sys.exit(1)
