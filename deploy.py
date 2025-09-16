#!/usr/bin/env python3
"""
Deployment script for LinkedIn Analytics Backend
This script handles database migrations and initial setup for production deployment.
"""

import os
import sys
import subprocess
from sqlalchemy import create_engine, text
from app.config import settings
from app.database import Base, engine
from app.models import User, Post, PostReaction, PostAnalytics
from app.auth import get_password_hash
from app.schemas import UserRole

def run_migrations():
    """Run database migrations using Alembic"""
    try:
        print("Running database migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Migrations completed successfully")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_tables():
    """Create database tables if migrations fail"""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def create_default_admin():
    """Create a default admin user if none exists"""
    try:
        from app.database import SessionLocal
        
        db = SessionLocal()
        
        # Check if admin user exists
        admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
        
        if not admin_user:
            print("Creating default admin user...")
            admin_user = User(
                email="admin@linkedin-analytics.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("✅ Default admin user created:")
            print("   Email: admin@linkedin-analytics.com")
            print("   Password: admin123")
            print("   ⚠️  Please change the password after first login!")
        else:
            print("✅ Admin user already exists")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        return False

def verify_database_connection():
    """Verify database connection"""
    try:
        print("Testing database connection...")
        
        # Test basic connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Starting LinkedIn Analytics Backend deployment...")
    print(f"Database URL: {settings.database_url}")
    print(f"API Title: {settings.api_title}")
    
    # Step 1: Verify database connection
    if not verify_database_connection():
        print("❌ Deployment failed: Cannot connect to database")
        sys.exit(1)
    
    # Step 2: Run migrations
    if not run_migrations():
        print("⚠️  Migrations failed, trying to create tables directly...")
        if not create_tables():
            print("❌ Deployment failed: Cannot create database tables")
            sys.exit(1)
    
    # Step 3: Create default admin user
    if not create_default_admin():
        print("⚠️  Warning: Could not create default admin user")
    
    print("\n🎉 Deployment completed successfully!")
    print("Your LinkedIn Analytics Backend is ready to use.")
    print("\n📝 Next steps:")
    print("1. Test the API endpoints")
    print("2. Change the default admin password")
    print("3. Create additional users as needed")
    print("4. Set up monitoring and logging")

if __name__ == "__main__":
    main()
