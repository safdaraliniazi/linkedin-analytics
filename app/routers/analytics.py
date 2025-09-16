from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from app.database import get_db
from app.models import User, Post, PostAnalytics, PostReaction
from app.schemas import (
    PostAnalytics as PostAnalyticsSchema,
    PostReactionCreate,
    PostReactionUpdate,
    TopEngagingPost,
    AnalyticsGraphData,
    ReactionType,
    UserRole
)
from app.auth import get_current_active_user, get_admin_user

router = APIRouter()


def can_access_analytics(user: User, post: Post) -> bool:
    """Check if user can access analytics for a specific post"""
    if user.role == UserRole.ADMIN:
        return True
    return post.author_id == user.id


@router.post("/reactions/{post_id}")
async def add_reaction(
    post_id: int,
    reaction: PostReactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add or update reaction for a post"""
    # Verify post exists and user has access
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not can_access_analytics(current_user, post):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to add reactions to this post"
        )
    
    # Check if reaction already exists
    existing_reaction = db.query(PostReaction).filter(
        and_(
            PostReaction.post_id == post_id,
            PostReaction.reaction_type == reaction.reaction_type
        )
    ).first()
    
    if existing_reaction:
        # Update existing reaction
        existing_reaction.count += reaction.count
        db.commit()
        db.refresh(existing_reaction)
    else:
        # Create new reaction
        new_reaction = PostReaction(
            post_id=post_id,
            reaction_type=reaction.reaction_type,
            count=reaction.count
        )
        db.add(new_reaction)
        db.commit()
        db.refresh(new_reaction)
        existing_reaction = new_reaction
    
    # Update analytics
    await update_post_analytics(post_id, db)
    
    return existing_reaction


@router.put("/reactions/{post_id}/{reaction_type}")
async def update_reaction(
    post_id: int,
    reaction_type: ReactionType,
    reaction_update: PostReactionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update reaction count for a post"""
    # Verify post exists and user has access
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not can_access_analytics(current_user, post):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to update reactions for this post"
        )
    
    # Find existing reaction
    reaction = db.query(PostReaction).filter(
        and_(
            PostReaction.post_id == post_id,
            PostReaction.reaction_type == reaction_type
        )
    ).first()
    
    if not reaction:
        raise HTTPException(status_code=404, detail="Reaction not found")
    
    # Update reaction count
    reaction.count = reaction_update.count
    db.commit()
    db.refresh(reaction)
    
    # Update analytics
    await update_post_analytics(post_id, db)
    
    return reaction


async def update_post_analytics(post_id: int, db: Session):
    """Update analytics for a post based on reactions"""
    # Get all reactions for the post
    reactions = db.query(PostReaction).filter(PostReaction.post_id == post_id).all()
    
    # Calculate totals
    total_reactions = sum(reaction.count for reaction in reactions)
    
    # Get reaction counts by type
    reaction_counts = {
        ReactionType.LIKE: 0,
        ReactionType.PRAISE: 0,
        ReactionType.EMPATHY: 0,
        ReactionType.INTEREST: 0,
        ReactionType.APPRECIATION: 0,
    }
    
    for reaction in reactions:
        reaction_counts[ReactionType(reaction.reaction_type)] = reaction.count
    
    # Get or create analytics record
    analytics = db.query(PostAnalytics).filter(PostAnalytics.post_id == post_id).first()
    
    if not analytics:
        analytics = PostAnalytics(post_id=post_id)
        db.add(analytics)
    
    # Update analytics
    analytics.total_reactions = total_reactions
    analytics.total_engagement = total_reactions  # Simplified: engagement = reactions
    analytics.likes_count = reaction_counts[ReactionType.LIKE]
    analytics.praise_count = reaction_counts[ReactionType.PRAISE]
    analytics.empathy_count = reaction_counts[ReactionType.EMPATHY]
    analytics.interest_count = reaction_counts[ReactionType.INTEREST]
    analytics.appreciation_count = reaction_counts[ReactionType.APPRECIATION]
    
    # Add some mock data for other metrics (in real app, these would come from LinkedIn API)
    analytics.total_impressions = total_reactions * 10  # Mock: 10x impressions vs reactions
    analytics.total_shares = total_reactions // 5  # Mock: 1 share per 5 reactions
    analytics.total_comments = total_reactions // 3  # Mock: 1 comment per 3 reactions
    
    db.commit()
    db.refresh(analytics)


@router.get("/post/{post_id}", response_model=PostAnalyticsSchema)
async def get_post_analytics(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a specific post"""
    # Verify post exists and user has access
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not can_access_analytics(current_user, post):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to view analytics for this post"
        )
    
    # Get analytics
    analytics = db.query(PostAnalytics).filter(PostAnalytics.post_id == post_id).first()
    
    if not analytics:
        # Create default analytics if none exist
        analytics = PostAnalytics(post_id=post_id)
        db.add(analytics)
        db.commit()
        db.refresh(analytics)
    
    return analytics


@router.get("/top-engaging", response_model=List[TopEngagingPost])
async def get_top_engaging_posts(
    top_n: int = Query(5, ge=1, le=50, description="Number of top posts to return"),
    start_date: Optional[datetime] = Query(None, description="Filter posts from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter posts until this date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get top N most engaging posts"""
    query = db.query(
        Post.id,
        Post.title,
        PostAnalytics.total_engagement,
        PostAnalytics.total_reactions,
        User.username.label('author_username')
    ).join(
        PostAnalytics, Post.id == PostAnalytics.post_id
    ).join(
        User, Post.author_id == User.id
    )
    
    # Role-based filtering
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Post.author_id == current_user.id)
    
    # Date filtering
    if start_date:
        query = query.filter(Post.created_at >= start_date)
    if end_date:
        query = query.filter(Post.created_at <= end_date)
    
    # Order by engagement and get top N
    results = query.order_by(desc(PostAnalytics.total_engagement)).limit(top_n).all()
    
    return [
        TopEngagingPost(
            post_id=result.id,
            title=result.title,
            total_engagement=result.total_engagement,
            total_reactions=result.total_reactions,
            author_username=result.author_username
        )
        for result in results
    ]


@router.get("/graph-data/{post_id}", response_model=List[AnalyticsGraphData])
async def get_analytics_graph_data(
    post_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get analytics graph data for a specific post over time"""
    # Verify post exists and user has access
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not can_access_analytics(current_user, post):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to view analytics for this post"
        )
    
    # For this demo, we'll generate mock time-series data
    # In a real implementation, you'd query actual time-series data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    graph_data = []
    current_date = start_date
    
    while current_date <= end_date:
        # Mock data - in real app, this would come from time-series analytics
        engagement = 10 + (current_date.day % 20)  # Mock variation
        reactions = 5 + (current_date.day % 15)    # Mock variation
        impressions = engagement * 10               # Mock: 10x impressions vs engagement
        
        graph_data.append(AnalyticsGraphData(
            date=current_date.strftime("%Y-%m-%d"),
            engagement=engagement,
            reactions=reactions,
            impressions=impressions
        ))
        
        current_date += timedelta(days=1)
    
    return graph_data


@router.get("/overview")
async def get_analytics_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get analytics overview for current user's posts"""
    # Build base query
    query = db.query(PostAnalytics).join(Post, PostAnalytics.post_id == Post.id)
    
    # Role-based filtering
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Post.author_id == current_user.id)
    
    # Get aggregated data
    analytics_data = query.with_entities(
        func.sum(PostAnalytics.total_reactions).label('total_reactions'),
        func.sum(PostAnalytics.total_engagement).label('total_engagement'),
        func.sum(PostAnalytics.total_impressions).label('total_impressions'),
        func.sum(PostAnalytics.total_shares).label('total_shares'),
        func.sum(PostAnalytics.total_comments).label('total_comments'),
        func.count(PostAnalytics.id).label('total_posts')
    ).first()
    
    return {
        "total_posts": analytics_data.total_posts or 0,
        "total_reactions": analytics_data.total_reactions or 0,
        "total_engagement": analytics_data.total_engagement or 0,
        "total_impressions": analytics_data.total_impressions or 0,
        "total_shares": analytics_data.total_shares or 0,
        "total_comments": analytics_data.total_comments or 0,
        "average_engagement_per_post": (
            analytics_data.total_engagement / analytics_data.total_posts
            if analytics_data.total_posts > 0 else 0
        )
    }
