#!/usr/bin/env python3
"""
Deployment fix script for Render
This script handles common deployment issues
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main deployment fix function"""
    print("🚀 LinkedIn Analytics Backend - Deployment Fix")
    
    # Check if we're in Render environment
    is_render = os.environ.get("RENDER", False)
    database_url = os.environ.get("DATABASE_URL", "")
    
    print(f"🌍 Environment: {'Render' if is_render else 'Local'}")
    print(f"🗄️  Database URL configured: {'Yes' if database_url else 'No'}")
    
    # Try to import and test the application
    try:
        print("📦 Testing application imports...")
        sys.path.append('/opt/render/project/src' if is_render else '.')
        
        from app.config import settings
        from app.database import engine, Base
        from app.models import User, Post, PostReaction, PostAnalytics
        
        print("✅ All imports successful")
        
        # Test database connection
        print("🗄️  Testing database connection...")
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        print("✅ Database connection successful")
        
        # Create tables if they don't exist
        print("📋 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
        
        # Create default admin user
        print("👤 Setting up default admin user...")
        from app.database import SessionLocal
        from app.auth import get_password_hash
        from app.schemas import UserRole
        
        db = SessionLocal()
        try:
            admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
            if not admin_user:
                admin_user = User(
                    email="admin@linkedin-analytics.com",
                    username="admin",
                    hashed_password=get_password_hash("admin123"),
                    role=UserRole.ADMIN,
                    is_active=True
                )
                db.add(admin_user)
                db.commit()
                print("✅ Default admin user created")
            else:
                print("✅ Admin user already exists")
        finally:
            db.close()
        
        print("\n🎉 Deployment fix completed successfully!")
        print("Your LinkedIn Analytics Backend is ready to use.")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
