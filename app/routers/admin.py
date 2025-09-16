from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Post
from app.schemas import User as UserSchema, Post as PostSchema, PostStatus
from app.auth import get_admin_user

router = APIRouter()


@router.get("/users", response_model=List[UserSchema])
async def get_all_users(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (Admin only)"""
    users = db.query(User).all()
    return users


@router.get("/posts", response_model=List[PostSchema])
async def get_all_posts(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all posts (Admin only)"""
    posts = db.query(Post).all()
    return posts


@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get admin statistics"""
    total_users = db.query(User).count()
    total_posts = db.query(Post).count()
    published_posts = db.query(Post).filter(Post.status == PostStatus.PUBLISHED).count()
    scheduled_posts = db.query(Post).filter(Post.status == PostStatus.SCHEDULED).count()
    draft_posts = db.query(Post).filter(Post.status == PostStatus.DRAFT).count()
    
    return {
        "total_users": total_users,
        "total_posts": total_posts,
        "published_posts": published_posts,
        "scheduled_posts": scheduled_posts,
        "draft_posts": draft_posts
    }
