#!/usr/bin/env python3
"""
Production database initialization script
Run this in Render Shell to create all database tables
"""

import os
from app import create_app, db
from app.models import User

def init_production_database():
    """Initialize the production database with all tables"""
    print("🚀 Initializing production database...")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            print("📋 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Verify tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Created tables: {', '.join(tables)}")
            
            print("🎉 Database initialization complete!")
            print("🌐 Your app should now work at: https://chatapp-3g10.onrender.com")
            
        except Exception as e:
            print(f"❌ Error initializing database: {str(e)}")
            print("🔍 Check your DATABASE_URL environment variable")
            return False
    
    return True

if __name__ == "__main__":
    success = init_production_database()
    if success:
        print("\n✅ SUCCESS: Database is ready!")
    else:
        print("\n❌ FAILED: Database initialization failed")
