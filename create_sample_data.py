#!/usr/bin/env python3
"""
Script to create sample data for the LinkedIn Analytics Backend
Run this script after setting up the database to populate it with sample data
"""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import User, Post, PostAnalytics, PostReaction
from app.auth import get_password_hash
from app.schemas import UserRole, PostStatus, ReactionType

def create_sample_data():
    """Create sample data for testing"""
    db = SessionLocal()
    
    try:
        # Create sample users
        print("Creating sample users...")
        
        # Admin user
        admin_user = User(
            email="admin@linkedin-analytics.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        
        # Regular users
        users_data = [
            {
                "email": "john.doe@example.com",
                "username": "johndoe",
                "password": "password123",
                "role": UserRole.USER
            },
            {
                "email": "jane.smith@example.com", 
                "username": "janesmith",
                "password": "password123",
                "role": UserRole.USER
            },
            {
                "email": "bob.wilson@example.com",
                "username": "bobwilson", 
                "password": "password123",
                "role": UserRole.USER
            }
        ]
        
        users = [admin_user]
        for user_data in users_data:
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                is_active=True
            )
            db.add(user)
            users.append(user)
        
        db.commit()
        print(f"Created {len(users)} users")
        
        # Create sample posts
        print("Creating sample posts...")
        
        posts_data = [
            {
                "title": "The Future of Remote Work",
                "content": "Remote work has transformed the way we think about productivity and work-life balance. Here are some insights from my experience leading distributed teams.",
                "author": users[1],  # john.doe
                "status": PostStatus.PUBLISHED,
                "published_at": datetime.now() - timedelta(days=5)
            },
            {
                "title": "AI and Machine Learning Trends 2024",
                "content": "Artificial Intelligence continues to evolve rapidly. Let's explore the key trends that will shape the industry in 2024.",
                "author": users[2],  # jane.smith
                "status": PostStatus.PUBLISHED,
                "published_at": datetime.now() - timedelta(days=3)
            },
            {
                "title": "Building Strong Professional Networks",
                "content": "Networking isn't just about collecting business cards. It's about building meaningful relationships that can support your career growth.",
                "author": users[1],  # john.doe
                "status": PostStatus.PUBLISHED,
                "published_at": datetime.now() - timedelta(days=2)
            },
            {
                "title": "Sustainable Business Practices",
                "content": "Sustainability is no longer optional for businesses. Here's how companies can integrate eco-friendly practices into their operations.",
                "author": users[3],  # bob.wilson
                "status": PostStatus.PUBLISHED,
                "published_at": datetime.now() - timedelta(days=1)
            },
            {
                "title": "Leadership in the Digital Age",
                "content": "Digital transformation requires new approaches to leadership. Learn how to adapt your leadership style for the modern workplace.",
                "author": users[2],  # jane.smith
                "status": PostStatus.SCHEDULED,
                "scheduled_at": datetime.now() + timedelta(hours=2)
            },
            {
                "title": "Cybersecurity Best Practices",
                "content": "With increasing cyber threats, it's crucial to implement robust security measures. Here are some essential practices every business should follow.",
                "author": users[3],  # bob.wilson
                "status": PostStatus.DRAFT
            },
            {
                "title": "The Power of Data-Driven Decision Making",
                "content": "Data is the new oil. Learn how to leverage analytics and insights to make better business decisions and drive growth.",
                "author": users[1],  # john.doe
                "status": PostStatus.DRAFT
            }
        ]
        
        posts = []
        for post_data in posts_data:
            post = Post(
                title=post_data["title"],
                content=post_data["content"],
                author_id=post_data["author"].id,
                status=post_data["status"],
                published_at=post_data.get("published_at"),
                scheduled_at=post_data.get("scheduled_at")
            )
            db.add(post)
            posts.append(post)
        
        db.commit()
        print(f"Created {len(posts)} posts")
        
        # Create analytics for published posts
        print("Creating sample analytics...")
        
        published_posts = [post for post in posts if post.status == PostStatus.PUBLISHED]
        
        for post in published_posts:
            # Create analytics record
            analytics = PostAnalytics(post_id=post.id)
            db.add(analytics)
            
            # Create reactions with random counts
            import random
            reactions_data = [
                (ReactionType.LIKE, random.randint(5, 50)),
                (ReactionType.PRAISE, random.randint(2, 20)),
                (ReactionType.EMPATHY, random.randint(1, 15)),
                (ReactionType.INTEREST, random.randint(3, 25)),
                (ReactionType.APPRECIATION, random.randint(1, 10))
            ]
            
            for reaction_type, count in reactions_data:
                reaction = PostReaction(
                    post_id=post.id,
                    reaction_type=reaction_type,
                    count=count
                )
                db.add(reaction)
        
        db.commit()
        
        # Update analytics with calculated values
        print("Updating analytics calculations...")
        for post in published_posts:
            analytics = db.query(PostAnalytics).filter(PostAnalytics.post_id == post.id).first()
            reactions = db.query(PostReaction).filter(PostReaction.post_id == post.id).all()
            
            if analytics and reactions:
                analytics.total_reactions = sum(r.count for r in reactions)
                analytics.total_engagement = analytics.total_reactions
                analytics.total_impressions = analytics.total_reactions * 10
                analytics.total_shares = analytics.total_reactions // 5
                analytics.total_comments = analytics.total_reactions // 3
                
                # Update individual reaction counts
                for reaction in reactions:
                    if reaction.reaction_type == ReactionType.LIKE:
                        analytics.likes_count = reaction.count
                    elif reaction.reaction_type == ReactionType.PRAISE:
                        analytics.praise_count = reaction.count
                    elif reaction.reaction_type == ReactionType.EMPATHY:
                        analytics.empathy_count = reaction.count
                    elif reaction.reaction_type == ReactionType.INTEREST:
                        analytics.interest_count = reaction.count
                    elif reaction.reaction_type == ReactionType.APPRECIATION:
                        analytics.appreciation_count = reaction.count
        
        db.commit()
        print("Sample data creation completed successfully!")
        
        # Print summary
        print("\n=== SAMPLE DATA SUMMARY ===")
        print(f"Users created: {len(users)}")
        print(f"Posts created: {len(posts)}")
        print(f"Published posts: {len(published_posts)}")
        print(f"Draft posts: {len([p for p in posts if p.status == PostStatus.DRAFT])}")
        print(f"Scheduled posts: {len([p for p in posts if p.status == PostStatus.SCHEDULED])}")
        
        print("\n=== LOGIN CREDENTIALS ===")
        print("Admin User:")
        print("  Email: admin@linkedin-analytics.com")
        print("  Password: admin123")
        print("\nRegular Users:")
        for user_data in users_data:
            print(f"  Email: {user_data['email']}")
            print(f"  Password: {user_data['password']}")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating sample data for LinkedIn Analytics Backend...")
    create_sample_data()
    print("Done! You can now test the API with the sample data.")
