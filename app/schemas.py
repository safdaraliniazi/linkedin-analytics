from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class PostStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"


class ReactionType(str, Enum):
    LIKE = "like"
    PRAISE = "praise"
    EMPATHY = "empathy"
    INTEREST = "interest"
    APPRECIATION = "appreciation"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Post Schemas
class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    scheduled_at: Optional[datetime] = None


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[PostStatus] = None
    scheduled_at: Optional[datetime] = None


class Post(PostBase):
    id: int
    author_id: int
    status: PostStatus
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PostWithAuthor(Post):
    author: User


# Reaction Schemas
class PostReactionBase(BaseModel):
    reaction_type: ReactionType
    count: int


class PostReactionCreate(PostReactionBase):
    post_id: int


class PostReactionUpdate(BaseModel):
    count: int


class PostReaction(PostReactionBase):
    id: int
    post_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Analytics Schemas
class PostAnalyticsBase(BaseModel):
    total_reactions: int = 0
    total_engagement: int = 0
    total_impressions: int = 0
    total_shares: int = 0
    total_comments: int = 0
    likes_count: int = 0
    praise_count: int = 0
    empathy_count: int = 0
    interest_count: int = 0
    appreciation_count: int = 0


class PostAnalyticsCreate(PostAnalyticsBase):
    post_id: int


class PostAnalyticsUpdate(BaseModel):
    total_reactions: Optional[int] = None
    total_engagement: Optional[int] = None
    total_impressions: Optional[int] = None
    total_shares: Optional[int] = None
    total_comments: Optional[int] = None
    likes_count: Optional[int] = None
    praise_count: Optional[int] = None
    empathy_count: Optional[int] = None
    interest_count: Optional[int] = None
    appreciation_count: Optional[int] = None


class PostAnalytics(PostAnalyticsBase):
    id: int
    post_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Combined schemas for detailed responses
class PostWithAnalytics(Post):
    analytics: Optional[PostAnalytics] = None
    reactions: List[PostReaction] = []


class PostWithFullDetails(PostWithAnalytics):
    author: User


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Filter and Query Schemas
class PostFilter(BaseModel):
    author_id: Optional[int] = None
    status: Optional[PostStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 10
    offset: int = 0


class AnalyticsFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    top_n: int = 5


# Response schemas
class TopEngagingPost(BaseModel):
    post_id: int
    title: str
    total_engagement: int
    total_reactions: int
    author_username: str


class AnalyticsGraphData(BaseModel):
    date: str
    engagement: int
    reactions: int
    impressions: int
