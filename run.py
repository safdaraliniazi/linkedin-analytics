#!/usr/bin/env python3
"""
Startup script for LinkedIn Analytics Backend
"""

import os
import uvicorn
from app.config import settings

if __name__ == "__main__":
    # Get port from environment variable (for Render) or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Determine if we're in production (Render) or development
    is_production = os.environ.get("RENDER", False) or "render" in os.environ.get("DATABASE_URL", "")
    
    print(f"🚀 Starting LinkedIn Analytics Backend...")
    print(f"📍 Port: {port}")
    print(f"🌍 Environment: {'Production' if is_production else 'Development'}")
    print(f"🗄️  Database: {'Connected' if settings.database_url else 'Not configured'}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=not is_production,  # Only reload in development
        log_level="info"
    )
