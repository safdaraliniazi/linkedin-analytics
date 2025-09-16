# LinkedIn Analytics Backend - Setup Guide

This guide will help you set up and run the LinkedIn Analytics Backend project.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package installer)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository (if applicable)
cd linkedin-analytics-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

#### Option A: Local PostgreSQL
```bash
# Install PostgreSQL (if not already installed)
# Create database
createdb linkedin_analytics

# Update database URL in app/config.py or create .env file
# Default: postgresql://user:password@localhost:5432/linkedin_analytics
```

#### Option B: Docker PostgreSQL
```bash
# Run PostgreSQL in Docker
docker run --name linkedin-postgres \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=linkedin_analytics \
  -p 5432:5432 \
  -d postgres:13
```

### 3. Environment Configuration

Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/linkedin_analytics
SECRET_KEY=your-very-long-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Database Migration

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### 5. Create Sample Data

```bash
# Run the sample data script
python create_sample_data.py
```

### 6. Start the Application

```bash
# Option 1: Using the run script
python run.py

# Option 2: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Testing with Postman

1. Import the `postman_collection.json` file into Postman
2. Set the `base_url` variable to `http://localhost:8000`
3. Start with the Authentication requests:
   - Register users
   - Login to get access tokens
4. Test the Posts and Analytics endpoints

## Sample Login Credentials

After running `create_sample_data.py`, you can use these credentials:

### Admin User
- Email: `admin@linkedin-analytics.com`
- Password: `admin123`

### Regular Users
- Email: `john.doe@example.com`, Password: `password123`
- Email: `jane.smith@example.com`, Password: `password123`
- Email: `bob.wilson@example.com`, Password: `password123`

## Key Features Implemented

### ✅ Authentication & Authorization
- JWT-based authentication
- Role-based access control (Admin/User)
- Password hashing with bcrypt

### ✅ Post Management
- CRUD operations for posts
- Post status: draft, scheduled, published
- Filtering by author, status, date range
- Pagination support

### ✅ Analytics System
- Track 5 reaction types: like, praise, empathy, interest, appreciation
- Calculate engagement metrics: reactions, impressions, shares, comments
- Analytics APIs for graphs and top engaging posts

### ✅ Post Scheduling
- Schedule posts with minute-level precision
- Background scheduler processes scheduled posts
- Simulates LinkedIn API calls
- Handles edge cases (past scheduling)

### ✅ Database Optimization
- Proper indexing for faster queries
- Optimized SQL queries with joins and aggregates
- Efficient pagination

### ✅ API Features
- Input validation with Pydantic
- Proper error handling with HTTP status codes
- Comprehensive API documentation
- CORS support

## Project Structure

```
linkedin-analytics-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection
│   ├── models.py              # SQLAlchemy models
│   ├── schemas.py             # Pydantic schemas
│   ├── auth.py                # Authentication utilities
│   ├── scheduler.py           # Post scheduling system
│   └── routers/
│       ├── auth.py            # Authentication endpoints
│       ├── posts.py           # Post management
│       ├── analytics.py       # Analytics endpoints
│       └── admin.py           # Admin endpoints
├── alembic/                   # Database migrations
├── requirements.txt           # Python dependencies
├── postman_collection.json    # API testing collection
├── create_sample_data.py      # Sample data script
├── run.py                     # Application runner
└── README.md                  # Project documentation
```

## API Endpoints Overview

### Authentication (`/auth`)
- `POST /register` - Register new user
- `POST /login` - Login and get token
- `GET /me` - Get current user info

### Posts (`/posts`)
- `POST /` - Create post
- `GET /` - List posts (with filtering)
- `GET /{id}` - Get specific post
- `PUT /{id}` - Update post
- `DELETE /{id}` - Delete post
- `POST /{id}/publish` - Publish post

### Analytics (`/analytics`)
- `POST /reactions/{post_id}` - Add reactions
- `PUT /reactions/{post_id}/{type}` - Update reaction
- `GET /post/{post_id}` - Get post analytics
- `GET /top-engaging` - Get top engaging posts
- `GET /graph-data/{post_id}` - Get analytics graph data
- `GET /overview` - Get analytics overview

### Admin (`/admin`)
- `GET /users` - Get all users (Admin only)
- `GET /posts` - Get all posts (Admin only)
- `GET /stats` - Get admin statistics

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify database credentials in config
   - Ensure database exists

2. **Import Errors**
   - Activate virtual environment
   - Install all requirements: `pip install -r requirements.txt`

3. **Authentication Errors**
   - Check JWT secret key is set
   - Verify token is included in Authorization header
   - Ensure user has proper role permissions

4. **Scheduling Issues**
   - Check system time is correct
   - Verify scheduler is running (check logs)
   - Ensure posts have valid scheduled_at times

### Logs and Debugging

The application includes comprehensive logging. Check the console output for:
- Database connection status
- Scheduler activity
- API request/response logs
- Error messages

## Production Deployment

For production deployment:

1. **Security**
   - Change default secret keys
   - Use environment variables for sensitive data
   - Enable HTTPS
   - Configure proper CORS origins

2. **Database**
   - Use connection pooling
   - Set up database backups
   - Monitor performance

3. **Application**
   - Use production ASGI server (gunicorn)
   - Set up logging and monitoring
   - Configure health checks

4. **Infrastructure**
   - Use container orchestration (Docker/Kubernetes)
   - Set up load balancing
   - Configure auto-scaling

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify all prerequisites are met
3. Test with the provided sample data
4. Review the API documentation at `/docs`

The project is designed to be production-ready with proper error handling, validation, and security measures in place.
