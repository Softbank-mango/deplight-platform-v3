"""
Simple Blog API - Delightful Deploy Demo
A FastAPI application for testing AI-powered deployment
"""
import os
import time
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# App configuration
app = FastAPI(
    title="Simple Blog API",
    description="A demo blog API for Delightful Deploy",
    version="1.0.0"
)

# In-memory storage (production would use DynamoDB)
posts_db = []
post_id_counter = 0

# Models
class Post(BaseModel):
    title: str
    content: str
    author: str = "Anonymous"
    tags: List[str] = []

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author: str
    tags: List[str]
    created_at: str
    updated_at: str

# Initialize with sample data
def init_sample_data():
    global post_id_counter
    sample_posts = [
        {
            "title": "Welcome to Delightful Deploy!",
            "content": "This is our AI-powered deployment system that makes deploying applications to AWS ECS incredibly easy.",
            "author": "Delightful Team",
            "tags": ["deployment", "devops", "aws"]
        },
        {
            "title": "How Blue/Green Deployment Works",
            "content": "Blue/Green deployment is a strategy that reduces downtime and risk by running two identical production environments.",
            "author": "DevOps Engineer",
            "tags": ["blue-green", "deployment", "strategy"]
        },
        {
            "title": "Getting Started with FastAPI",
            "content": "FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.",
            "author": "Python Developer",
            "tags": ["fastapi", "python", "api"]
        }
    ]

    for post_data in sample_posts:
        post_id_counter += 1
        now = datetime.utcnow().isoformat()
        posts_db.append({
            "id": post_id_counter,
            "title": post_data["title"],
            "content": post_data["content"],
            "author": post_data["author"],
            "tags": post_data["tags"],
            "created_at": now,
            "updated_at": now
        })

# Initialize sample data on startup
@app.on_event("startup")
async def startup_event():
    init_sample_data()
    print(f"✅ Blog API started with {len(posts_db)} sample posts")

# Routes
@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Simple Blog API!",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "endpoints": {
            "health": "/health",
            "status": "/api/status",
            "posts": "/api/posts",
            "metrics": "/api/metrics"
        },
        "features": [
            "AI-powered deployment analysis",
            "Blue/Green deployment with CodeDeploy",
            "CloudWatch monitoring and X-Ray tracing",
            "Auto-scaling based on CPU/Memory",
            "Automated health checks"
        ]
    }

@app.get("/health")
def health():
    """Health check endpoint for ALB"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "simple-blog-api",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    )

@app.get("/api/status")
def api_status():
    """API status with detailed information"""
    return {
        "status": "operational",
        "service": "simple-blog-api",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": {
            "type": "in-memory",
            "posts_count": len(posts_db)
        },
        "deployment": {
            "strategy": "blue-green",
            "platform": "ECS Fargate",
            "region": "ap-northeast-2"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/posts", response_model=List[PostResponse])
def get_posts(limit: int = 10, tag: Optional[str] = None):
    """Get all blog posts with optional filtering"""
    filtered_posts = posts_db

    if tag:
        filtered_posts = [p for p in posts_db if tag in p["tags"]]

    return filtered_posts[:limit]

@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int):
    """Get a specific blog post by ID"""
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.post("/api/posts", response_model=PostResponse, status_code=201)
def create_post(post: Post):
    """Create a new blog post"""
    global post_id_counter
    post_id_counter += 1

    now = datetime.utcnow().isoformat()
    new_post = {
        "id": post_id_counter,
        "title": post.title,
        "content": post.content,
        "author": post.author,
        "tags": post.tags,
        "created_at": now,
        "updated_at": now
    }

    posts_db.append(new_post)
    return new_post

@app.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post: Post):
    """Update an existing blog post"""
    existing_post = next((p for p in posts_db if p["id"] == post_id), None)
    if not existing_post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_post.update({
        "title": post.title,
        "content": post.content,
        "author": post.author,
        "tags": post.tags,
        "updated_at": datetime.utcnow().isoformat()
    })

    return existing_post

@app.delete("/api/posts/{post_id}")
def delete_post(post_id: int):
    """Delete a blog post"""
    global posts_db
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    posts_db = [p for p in posts_db if p["id"] != post_id]
    return {"message": "Post deleted successfully"}

@app.get("/api/metrics")
def get_metrics():
    """Get application metrics"""
    tag_counts = {}
    for post in posts_db:
        for tag in post["tags"]:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return {
        "total_posts": len(posts_db),
        "tags": tag_counts,
        "most_popular_tag": max(tag_counts.items(), key=lambda x: x[1])[0] if tag_counts else None,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/search")
def search_posts(q: str):
    """Search posts by title or content"""
    query = q.lower()
    results = [
        p for p in posts_db
        if query in p["title"].lower() or query in p["content"].lower()
    ]
    return {
        "query": q,
        "results_count": len(results),
        "results": results
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
