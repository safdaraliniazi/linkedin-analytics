#!/bin/bash

# Build script for Render deployment
# This script ensures proper installation of dependencies

echo "🚀 Starting LinkedIn Analytics Backend build..."

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install wheel and setuptools first
echo "🔧 Installing build tools..."
pip install wheel setuptools

# Install dependencies with no cache to avoid conflicts
echo "📚 Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Run database migrations
echo "🗄️  Running database migrations..."
python -c "
import os
import sys
sys.path.append('/opt/render/project/src')

try:
    from app.database import engine, Base
    from app.models import User, Post, PostReaction, PostAnalytics
    from app.auth import get_password_hash
    from app.schemas import UserRole
    
    print('Creating database tables...')
    Base.metadata.create_all(bind=engine)
    print('✅ Database tables created successfully')
    
    # Create default admin user
    from app.database import SessionLocal
    db = SessionLocal()
    
    admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if not admin_user:
        print('Creating default admin user...')
        admin_user = User(
            email='admin@linkedin-analytics.com',
            username='admin',
            hashed_password=get_password_hash('admin123'),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print('✅ Default admin user created')
    else:
        print('✅ Admin user already exists')
    
    db.close()
    print('🎉 Build completed successfully!')
    
except Exception as e:
    print(f'❌ Build failed: {e}')
    sys.exit(1)
"

echo "✅ Build script completed!"
