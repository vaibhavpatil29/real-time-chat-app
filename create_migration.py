#!/usr/bin/env python3
"""
Database migration script for enhanced authentication features
Run this script to update your database schema with the new authentication fields
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init, migrate, upgrade
from config import config

def create_migration():
    """Create and apply database migration for enhanced authentication"""
    
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
            
            print("🔄 Creating database migration for enhanced authentication...")
            
            # Check if migrations directory exists
            migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
            if not os.path.exists(migrations_dir):
                print("📁 Initializing migrations directory...")
                init()
            
            # Create migration
            print("📝 Generating migration script...")
            migrate(message="Enhanced authentication features")
            
            # Apply migration
            print("⚡ Applying migration to database...")
            upgrade()
            
            print("✅ Database migration completed successfully!")
            print("\n📋 New authentication features added:")
            print("   • Enhanced User model with security fields")
            print("   • Email verification system")
            print("   • Password reset functionality")
            print("   • Account locking for failed login attempts")
            print("   • User profile fields (first_name, last_name, bio)")
            print("   • Activity tracking (last_login, last_seen)")
            print("   • Two-factor authentication preparation")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            print("\n🔧 Troubleshooting steps:")
            print("1. Ensure PostgreSQL is running")
            print("2. Check database connection settings in config.py")
            print("3. Verify database user has CREATE permissions")
            print("4. Check if database 'chatdb' exists")
            return False
    
    return True

def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    try:
        # Connection parameters
        conn_params = {
            'host': 'localhost',
            'user': 'postgres',
            'password': '@vaibhav29v',
            'port': 5432
        }
        
        # Connect to PostgreSQL server
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'chatdb'")
        exists = cursor.fetchone()
        
        if not exists:
            print("📊 Creating database 'chatdb'...")
            cursor.execute('CREATE DATABASE chatdb')
            print("✅ Database 'chatdb' created successfully!")
        else:
            print("📊 Database 'chatdb' already exists.")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database creation failed: {str(e)}")
        print("\n🔧 Please create the database manually:")
        print("1. Connect to PostgreSQL as superuser")
        print("2. Run: CREATE DATABASE chatdb;")
        print("3. Run this script again")
        return False

if __name__ == '__main__':
    print("🚀 ChatApp Database Migration Script")
    print("=" * 40)
    
    # Create database if needed
    if not create_database_if_not_exists():
        sys.exit(1)
    
    # Run migration
    if create_migration():
        print("\n🎉 Migration completed! Your ChatApp is ready with enhanced authentication.")
        print("\n🔐 New authentication features available:")
        print("   • Secure password validation")
        print("   • Email verification")
        print("   • Password reset via email")
        print("   • Account lockout protection")
        print("   • User profile management")
        print("   • Session management")
        print("\n▶️  Start your application with: python run.py")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        sys.exit(1)
