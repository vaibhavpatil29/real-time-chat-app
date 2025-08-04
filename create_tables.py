#!/usr/bin/env python3
"""
Create database tables directly
"""

import os
from flask import Flask
from config import config

def create_tables():
    """Create all database tables"""
    
    # Create app using the app factory
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        from app import db
        try:
            # Import models to ensure they're registered
            from app.models import User, Message
            
            print("Creating database tables...")
            
            # Drop all tables and recreate (be careful with this in production!)
            db.drop_all()
            db.create_all()
            
            print("SUCCESS: All tables created successfully!")
            print("\nTables created:")
            print("  - users (with enhanced authentication fields)")
            print("  - messages (for chat functionality)")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Table creation failed: {str(e)}")
            return False

if __name__ == '__main__':
    print("ChatApp Table Creation")
    print("=" * 30)
    
    if create_tables():
        print("\nDatabase ready! Start your application with: python run.py")
    else:
        print("\nTable creation failed. Please check the errors above.")
