#!/usr/bin/env python3
"""
Admin script to manage users in the chat application
"""

import sys
from app import create_app, db
from app.models import User

def verify_all_users():
    """Verify all users in the database"""
    
    app = create_app()
    
    with app.app_context():
        try:
            users = User.query.filter_by(email_verified=False).all()
            
            if not users:
                print("All users are already verified.")
                return True
            
            print(f"Found {len(users)} unverified users. Verifying...")
            
            for user in users:
                user.email_verified = True
                user.email_verification_token = None
                user.email_verification_token_expires = None
                print(f"✓ Verified: {user.username} ({user.email})")
            
            db.session.commit()
            
            print(f"\nSUCCESS: Verified {len(users)} users!")
            print("All users can now log in without email verification.")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to verify users: {str(e)}")
            return False

def list_all_users():
    """List all users with their status"""
    
    app = create_app()
    
    with app.app_context():
        try:
            users = User.query.all()
            
            if not users:
                print("No users found in the database.")
                return
            
            print("All Users in Database:")
            print("=" * 80)
            
            for i, user in enumerate(users, 1):
                status = "Verified" if user.email_verified else "Not Verified"
                active = "Active" if user.is_active else "Inactive"
                
                print(f"{i}. Username: {user.username}")
                print(f"   Email: {user.email}")
                print(f"   Name: {user.first_name or 'N/A'} {user.last_name or 'N/A'}")
                print(f"   Status: {status}")
                print(f"   Account: {active}")
                print(f"   Created: {user.created_at}")
                print(f"   Last Login: {user.last_login or 'Never'}")
                print("-" * 80)
                
        except Exception as e:
            print(f"ERROR: Failed to list users: {str(e)}")

def delete_user(username_or_email):
    """Delete a user from the database"""
    
    app = create_app()
    
    with app.app_context():
        try:
            user = User.query.filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            ).first()
            
            if not user:
                print(f"ERROR: User '{username_or_email}' not found.")
                return False
            
            username = user.username
            email = user.email
            
            db.session.delete(user)
            db.session.commit()
            
            print(f"SUCCESS: User '{username}' ({email}) has been deleted!")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to delete user: {str(e)}")
            return False

def create_test_user():
    """Create a test user that's already verified"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Check if test user already exists
            existing_user = User.query.filter_by(username='testuser').first()
            if existing_user:
                print("Test user already exists!")
                return True
            
            # Create test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                first_name='Test',
                last_name='User'
            )
            test_user.set_password('password123')
            test_user.email_verified = True  # Pre-verified
            
            db.session.add(test_user)
            db.session.commit()
            
            print("SUCCESS: Test user created!")
            print("Username: testuser")
            print("Password: password123")
            print("Email: test@example.com")
            print("Status: Pre-verified")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to create test user: {str(e)}")
            return False

if __name__ == '__main__':
    print("ChatApp User Administration Tool")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python admin_users.py --list                    - List all users")
        print("  python admin_users.py --verify-all              - Verify all users")
        print("  python admin_users.py --delete <username>       - Delete a user")
        print("  python admin_users.py --create-test             - Create test user")
        print("")
        print("Examples:")
        print("  python admin_users.py --list")
        print("  python admin_users.py --verify-all")
        print("  python admin_users.py --delete testuser")
        print("  python admin_users.py --create-test")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == '--list':
        list_all_users()
    elif command == '--verify-all':
        if verify_all_users():
            print("\nAll users can now log in at: http://127.0.0.1:5000/login")
    elif command == '--delete':
        if len(sys.argv) < 3:
            print("ERROR: Please specify username or email to delete")
            sys.exit(1)
        delete_user(sys.argv[2])
    elif command == '--create-test':
        if create_test_user():
            print("\nYou can now log in with the test user at: http://127.0.0.1:5000/login")
    else:
        print(f"ERROR: Unknown command '{command}'")
        sys.exit(1)
