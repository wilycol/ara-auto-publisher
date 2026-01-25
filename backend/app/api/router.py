from fastapi import APIRouter
from app.api import topics, jobs, posts, projects, auth, campaigns, guide, internal_usage, tracking, internal_impact, internal_versioning, internal_automation, internal_control, forums, forum_threads

api_router = APIRouter()

api_router.include_router(forums.router, prefix="/forums", tags=["Forums"])
api_router.include_router(forum_threads.router, prefix="/forums", tags=["ForumThreads"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(topics.router, prefix="/topics", tags=["Topics"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Auto Publisher Jobs"])
api_router.include_router(posts.router, prefix="/posts", tags=["Posts"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(guide.router, prefix="/guide", tags=["Guide AI"])
api_router.include_router(internal_usage.router, prefix="/internal", tags=["Internal Ops"])
api_router.include_router(tracking.router, prefix="/internal/tracking", tags=["Tracking"])
api_router.include_router(internal_impact.router, prefix="/internal/impact", tags=["Impact Metrics"])
api_router.include_router(internal_versioning.router, prefix="/internal/content", tags=["Content Versioning"])
api_router.include_router(internal_automation.router, prefix="/internal/automation", tags=["Campaign Automation"])
api_router.include_router(internal_control.router, prefix="/internal/control", tags=["Human Control & Observability"])
