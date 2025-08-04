#!/usr/bin/env python3
"""
Script to manually verify a user's email for testing purposes
"""

import sys
from app import create_app, db
from app.models import User

def verify_user_email(username_or_email):
    """Manually verify a user's email"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Find user by username or email
            user = User.query.filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            ).first()
            
            if not user:
                print(f"ERROR: User '{username_or_email}' not found.")
                return False
            
            if user.email_verified:
                print(f"INFO: User '{user.username}' is already verified.")
                return True
            
            # Manually verify the user
            user.email_verified = True
            user.email_verification_token = None
            user.email_verification_token_expires = None
            
            db.session.commit()
            
            print(f"SUCCESS: User '{user.username}' ({user.email}) has been verified!")
            print("You can now log in to the application.")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to verify user: {str(e)}")
            return False

def list_users():
    """List all users in the database"""
    
    app = create_app()
    
    with app.app_context():
        try:
            users = User.query.all()
            
            if not users:
                print("No users found in the database.")
                return
            
            print("Users in database:")
            print("-" * 60)
            for user in users:
                status = "✓ Verified" if user.email_verified else "✗ Not Verified"
                print(f"Username: {user.username}")
                print(f"Email: {user.email}")
                print(f"Status: {status}")
                print(f"Created: {user.created_at}")
                print("-" * 60)
                
        except Exception as e:
            print(f"ERROR: Failed to list users: {str(e)}")

if __name__ == '__main__':
    print("ChatApp User Email Verification Tool")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python verify_user.py <username_or_email>  - Verify a specific user")
        print("  python verify_user.py --list               - List all users")
        print("")
        print("Examples:")
        print("  python verify_user.py Paras0201")
        print("  python verify_user.py paraschavan796@gmail.com")
        print("  python verify_user.py --list")
        sys.exit(1)
    
    if sys.argv[1] == '--list':
        list_users()
    else:
        username_or_email = sys.argv[1]
        if verify_user_email(username_or_email):
            print("\nYou can now log in at: http://127.0.0.1:5000/login")
        else:
            print("\nVerification failed. Please check the error above.")
            sys.exit(1)
