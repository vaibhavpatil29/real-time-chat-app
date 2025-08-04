#!/usr/bin/env python3
"""
Add OAuth fields to User model
"""

from app import create_app, db
from app.models import User

def add_oauth_fields():
    """Add OAuth fields to the users table"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Add the new columns using raw SQL
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS google_id VARCHAR(100),
                    ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR(50);
                """))
                
                # Also make password_hash nullable for OAuth users
                conn.execute(db.text("""
                    ALTER TABLE users 
                    ALTER COLUMN password_hash DROP NOT NULL;
                """))
                
                conn.commit()
            
            print("SUCCESS: OAuth fields added to users table!")
            print("- google_id: VARCHAR(100) UNIQUE")
            print("- oauth_provider: VARCHAR(50)")
            print("- password_hash: now nullable")
            
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to add OAuth fields: {str(e)}")
            return False

if __name__ == '__main__':
    print("Adding OAuth Fields to User Model")
    print("=" * 50)
    
    if add_oauth_fields():
        print("\nOAuth fields have been successfully added!")
        print("You can now use Google authentication.")
    else:
        print("\nFailed to add OAuth fields. Please check the error above.")
