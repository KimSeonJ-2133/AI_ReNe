from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

view_router = APIRouter()

# Static directory path calculation
# Current file: src/api/endpoints/view_router.py
# Target: src/api/static
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

@view_router.get("/")
async def read_root():
    return FileResponse(os.path.join(STATIC_DIR, "interview_test.html"))

@view_router.get("/profile")
async def read_profile():
    return FileResponse(os.path.join(STATIC_DIR, "profile.html"))
