import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import SessionLocal
from app.models import Post, PostStatus

logger = logging.getLogger(__name__)


class PostScheduler:
    """Handles post scheduling and publishing"""
    
    def __init__(self):
        self.is_running = False
        self.task = None
    
    async def start(self):
        """Start the scheduler"""
        if not self.is_running:
            self.is_running = True
            self.task = asyncio.create_task(self._run_scheduler())
            logger.info("Post scheduler started")
    
    async def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Post scheduler stopped")
    
    async def _run_scheduler(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                await self._check_scheduled_posts()
                # Check every 10 seconds
                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def _check_scheduled_posts(self):
        """Check for posts that need to be published"""
        db = SessionLocal()
        try:
            # Get posts that are scheduled and due for publishing
            now = datetime.now()
            # Round down to the current minute for precise scheduling
            current_minute = now.replace(second=0, microsecond=0)
            
            scheduled_posts = db.query(Post).filter(
                and_(
                    Post.status == PostStatus.SCHEDULED,
                    Post.scheduled_at <= current_minute
                )
            ).all()
            
            for post in scheduled_posts:
                try:
                    await self._publish_post(post, db)
                except Exception as e:
                    logger.error(f"Error publishing post {post.id}: {e}")
                    continue
                    
        finally:
            db.close()
    
    async def _publish_post(self, post: Post, db: Session):
        """Publish a scheduled post"""
        try:
            # Update post status
            post.status = PostStatus.PUBLISHED
            post.published_at = datetime.now()
            
            # Simulate LinkedIn API call
            await self._simulate_linkedin_post(post)
            
            db.commit()
            logger.info(f"Successfully published post {post.id}: {post.title}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to publish post {post.id}: {e}")
            raise
    
    async def _simulate_linkedin_post(self, post: Post):
        """Simulate LinkedIn API post request"""
        # This simulates the LinkedIn API call
        # In a real implementation, this would call the actual LinkedIn API
        logger.info(f"Simulating LinkedIn API call for post: {post.title}")
        
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        # Simulate random success/failure (95% success rate)
        import random
        if random.random() < 0.95:
            logger.info(f"LinkedIn API call successful for post {post.id}")
        else:
            raise Exception("LinkedIn API call failed (simulated)")
    
    async def schedule_post(self, post_id: int, scheduled_at: datetime):
        """Schedule a post for future publishing"""
        db = SessionLocal()
        try:
            post = db.query(Post).filter(Post.id == post_id).first()
            if not post:
                raise ValueError(f"Post {post_id} not found")
            
            if post.status != PostStatus.DRAFT:
                raise ValueError(f"Only draft posts can be scheduled")
            
            if scheduled_at <= datetime.now():
                raise ValueError("Cannot schedule posts in the past")
            
            post.status = PostStatus.SCHEDULED
            post.scheduled_at = scheduled_at
            
            db.commit()
            logger.info(f"Post {post_id} scheduled for {scheduled_at}")
            
        finally:
            db.close()
    
    async def cancel_scheduled_post(self, post_id: int):
        """Cancel a scheduled post"""
        db = SessionLocal()
        try:
            post = db.query(Post).filter(Post.id == post_id).first()
            if not post:
                raise ValueError(f"Post {post_id} not found")
            
            if post.status != PostStatus.SCHEDULED:
                raise ValueError(f"Post {post_id} is not scheduled")
            
            post.status = PostStatus.DRAFT
            post.scheduled_at = None
            
            db.commit()
            logger.info(f"Scheduled post {post_id} cancelled")
            
        finally:
            db.close()
    
    def get_scheduled_posts_count(self) -> int:
        """Get count of scheduled posts"""
        db = SessionLocal()
        try:
            count = db.query(Post).filter(Post.status == PostStatus.SCHEDULED).count()
            return count
        finally:
            db.close()


# Global scheduler instance
post_scheduler = PostScheduler()


async def start_scheduler():
    """Start the post scheduler"""
    await post_scheduler.start()


async def stop_scheduler():
    """Stop the post scheduler"""
    await post_scheduler.stop()
