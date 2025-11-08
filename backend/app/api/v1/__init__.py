"""
API v1 routes
"""
from fastapi import APIRouter
from app.api.v1 import auth, files, templates, jobs, parse, ai, jobs_enhanced, transform

api_router = APIRouter()

# Include route modules
api_router.include_router(auth.router)
api_router.include_router(files.router)
api_router.include_router(templates.router)
api_router.include_router(jobs.router)
api_router.include_router(jobs_enhanced.router)  # Enhanced job endpoints
api_router.include_router(parse.router)
api_router.include_router(ai.router)
api_router.include_router(transform.router)

@api_router.get("/")
async def api_root():
    """API root endpoint"""
    return {
        "message": "PBM Auto Conversion System API v1",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth",
            "files": "/files",
            "templates": "/templates",
            "jobs": "/jobs (CRUD + Enhanced processing)",
            "parse": "/parse",
            "ai": "/ai",
            "transform": "/transform"
        }
    }
