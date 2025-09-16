# LinkedIn Analytics Backend

A FastAPI + PostgreSQL backend system that powers a simplified LinkedIn analytics platform.

## Features

- **Authentication & Authorization**: JWT-based authentication with role-based access control (Admin/User)
- **Post Management**: CRUD operations for posts with filtering capabilities
- **Analytics**: Track reactions (like, praise, empathy, interest, appreciation) and engagement metrics
- **Post Scheduling**: Schedule posts with minute-level precision
- **Optimized Database**: Proper indexing and optimized queries
- **Real-time Processing**: Background scheduler for handling scheduled posts

## Project Structure

```
app/
├── __init__.py
├── main.py                 # FastAPI application
├── config.py              # Configuration settings
├── database.py            # Database connection and session
├── models.py              # SQLAlchemy models
├── schemas.py             # Pydantic schemas
├── auth.py                # Authentication utilities
├── scheduler.py           # Post scheduling system
└── routers/
    ├── __init__.py
    ├── auth.py            # Authentication endpoints
    ├── posts.py           # Post management endpoints
    ├── analytics.py       # Analytics endpoints
    └── admin.py           # Admin-only endpoints
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL database and update the connection string in `app/config.py`

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user information

### Posts
- `POST /posts/` - Create a new post
- `GET /posts/` - Get posts with filtering options
- `GET /posts/{post_id}` - Get a specific post
- `PUT /posts/{post_id}` - Update a post
- `DELETE /posts/{post_id}` - Delete a post
- `POST /posts/{post_id}/publish` - Manually publish a post

### Analytics
- `POST /analytics/reactions/{post_id}` - Add reactions to a post
- `PUT /analytics/reactions/{post_id}/{reaction_type}` - Update reaction count
- `GET /analytics/post/{post_id}` - Get analytics for a specific post
- `GET /analytics/top-engaging` - Get top engaging posts
- `GET /analytics/graph-data/{post_id}` - Get analytics graph data
- `GET /analytics/overview` - Get analytics overview

### Admin
- `GET /admin/users` - Get all users (Admin only)
- `GET /admin/posts` - Get all posts (Admin only)
- `GET /admin/stats` - Get admin statistics

## Database Schema

### Users
- User authentication and role management
- Roles: `admin`, `user`

### Posts
- Post content and metadata
- Status: `draft`, `scheduled`, `published`
- Scheduling support with minute-level precision

### Post Reactions
- Track different reaction types: like, praise, empathy, interest, appreciation
- Count-based tracking system

### Post Analytics
- Aggregated engagement metrics
- Total reactions, engagement, impressions, shares, comments
- Reaction breakdown by type

## Scheduling System

The application includes a background scheduler that:
- Checks for scheduled posts every 10 seconds
- Publishes posts at the scheduled time (within the specified minute)
- Handles edge cases like scheduling in the past
- Simulates LinkedIn API calls (placeholder function)
- Optimized to handle multiple users scheduling posts simultaneously

## Security Features

- JWT token-based authentication
- Role-based access control
- Password hashing with bcrypt
- Input validation with Pydantic
- Proper error handling with HTTP status codes

## Performance Optimizations

- Database indexes for faster queries
- Optimized SQL queries with joins and aggregates
- Efficient pagination
- Background processing for scheduling

## Testing

Run tests with:
```bash
pytest
```

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

Copy `env.example` to `.env` and configure:
- Database connection string
- JWT secret key
- API settings

## Deployment

The application is production-ready and can be deployed using:
- Docker containers
- Cloud platforms (AWS, GCP, Azure)
- Traditional servers with uvicorn/gunicorn

For production deployment, make sure to:
- Use environment variables for sensitive configuration
- Set up proper database connection pooling
- Configure HTTPS
- Set up monitoring and logging
- Use a production-grade ASGI server like gunicorn
