from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Index, func
from enum import Enum
class PostStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")  # "admin" or "user"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    posts = relationship("Post", back_populates="author")
    
    # Indexes
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_role', 'role'),
    )


class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False, default="draft")  # "draft", "scheduled", "published"
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship("User", back_populates="posts")
    analytics = relationship("PostAnalytics", back_populates="post", uselist=False)
    reactions = relationship("PostReaction", back_populates="post")
    
    # Indexes for faster retrieval
    __table_args__ = (
        Index('idx_posts_author_id', 'author_id'),
        Index('idx_posts_status', 'status'),
        Index('idx_posts_scheduled_at', 'scheduled_at'),
        Index('idx_posts_published_at', 'published_at'),
        Index('idx_posts_created_at', 'created_at'),
        Index('idx_posts_author_status', 'author_id', 'status'),
    )


class PostReaction(Base):
    __tablename__ = "post_reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    reaction_type = Column(String, nullable=False)  # "like", "praise", "empathy", "interest", "appreciation"
    count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    post = relationship("Post", back_populates="reactions")
    
    # Indexes
    __table_args__ = (
        Index('idx_reactions_post_id', 'post_id'),
        Index('idx_reactions_type', 'reaction_type'),
        Index('idx_reactions_post_type', 'post_id', 'reaction_type'),
    )


class PostAnalytics(Base):
    __tablename__ = "post_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, unique=True)
    
    # Engagement metrics
    total_reactions = Column(Integer, default=0)
    total_engagement = Column(Integer, default=0)
    total_impressions = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    
    # Reaction breakdowns
    likes_count = Column(Integer, default=0)
    praise_count = Column(Integer, default=0)
    empathy_count = Column(Integer, default=0)
    interest_count = Column(Integer, default=0)
    appreciation_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    post = relationship("Post", back_populates="analytics")
    
    # Indexes
    __table_args__ = (
        Index('idx_analytics_post_id', 'post_id'),
        Index('idx_analytics_total_engagement', 'total_engagement'),
        Index('idx_analytics_total_reactions', 'total_reactions'),
    )
