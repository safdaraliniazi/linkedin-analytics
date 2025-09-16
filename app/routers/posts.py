from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.database import get_db
from app.models import User, Post, PostAnalytics, PostReaction
from app.schemas import (
    PostCreate, PostUpdate, Post as PostSchema, PostWithAnalytics, 
    PostWithAuthor, PostFilter, PostStatus, UserRole
)
from app.auth import get_current_active_user, get_admin_user

router = APIRouter()


def can_access_post(user: User, post: Post) -> bool:
    """Check if user can access a specific post"""
    if user.role == UserRole.ADMIN:
        return True
    return post.author_id == user.id


@router.post("/", response_model=PostSchema)
async def create_post(
    post: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new post"""
    # Validate scheduling
    if post.scheduled_at:
        if post.scheduled_at < datetime.now():
            raise HTTPException(
                status_code=400,
                detail="Cannot schedule posts in the past"
            )
    
    db_post = Post(
        title=post.title,
        content=post.content,
        author_id=current_user.id,
        scheduled_at=post.scheduled_at,
        status=PostStatus.SCHEDULED if post.scheduled_at else PostStatus.DRAFT
    )
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # Create analytics record
    analytics = PostAnalytics(post_id=db_post.id)
    db.add(analytics)
    db.commit()
    
    return db_post


@router.get("/", response_model=List[PostWithAuthor])
async def get_posts(
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    status: Optional[PostStatus] = Query(None, description="Filter by post status"),
    start_date: Optional[datetime] = Query(None, description="Filter posts from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter posts until this date"),
    limit: int = Query(10, ge=1, le=100, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get posts with filtering options"""
    query = db.query(Post)
    
    # Role-based filtering
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Post.author_id == current_user.id)
    elif author_id is not None:
        query = query.filter(Post.author_id == author_id)
    
    # Status filtering
    if status:
        query = query.filter(Post.status == status)
    
    # Date filtering
    if start_date:
        query = query.filter(Post.created_at >= start_date)
    if end_date:
        query = query.filter(Post.created_at <= end_date)
    
    # Apply pagination
    posts = query.offset(offset).limit(limit).all()
    
    return posts


@router.get("/{post_id}", response_model=PostWithAnalytics)
async def get_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific post by ID"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    # Check access permissions
    if not can_access_post(current_user, post):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to access this post"
        )
    
    return post


@router.put("/{post_id}", response_model=PostSchema)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    # Check access permissions
    if not can_access_post(current_user, post):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to update this post"
        )
    
    # Update fields
    update_data = post_update.dict(exclude_unset=True)
    
    # Validate scheduling
    if "scheduled_at" in update_data and update_data["scheduled_at"]:
        if update_data["scheduled_at"] < datetime.now():
            raise HTTPException(
                status_code=400,
                detail="Cannot schedule posts in the past"
            )
        update_data["status"] = PostStatus.SCHEDULED
    
    for field, value in update_data.items():
        setattr(post, field, value)
    
    db.commit()
    db.refresh(post)
    
    return post


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    # Check access permissions
    if not can_access_post(current_user, post):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to delete this post"
        )
    
    # Delete related analytics and reactions first
    db.query(PostAnalytics).filter(PostAnalytics.post_id == post_id).delete()
    db.query(PostReaction).filter(PostReaction.post_id == post_id).delete()
    
    # Delete the post
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted successfully"}


@router.post("/{post_id}/publish")
async def publish_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Manually publish a scheduled or draft post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    
    # Check access permissions
    if not can_access_post(current_user, post):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to publish this post"
        )
    
    if post.status == PostStatus.PUBLISHED:
        raise HTTPException(
            status_code=400,
            detail="Post is already published"
        )
    
    # Update post status and published time
    post.status = PostStatus.PUBLISHED
    post.published_at = datetime.now()
    
    db.commit()
    db.refresh(post)
    
    # Simulate LinkedIn API call
    await simulate_linkedin_post(post)
    
    return {"message": "Post published successfully", "post": post}


async def simulate_linkedin_post(post: Post):
    """Simulate LinkedIn API post request (placeholder function)"""
    # This is a placeholder function that simulates posting to LinkedIn
    # In a real implementation, this would call the actual LinkedIn API
    print(f"Simulating LinkedIn API call for post: {post.title}")
    # Add any logging or external service calls here
    pass
