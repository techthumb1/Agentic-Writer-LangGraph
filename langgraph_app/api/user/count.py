# langgraph_app/api/user/count.py
from fastapi import APIRouter
from langgraph_app.db_client import prisma

router = APIRouter()

@router.get("/users/count")
async def get_user_count():
    """Get total user count for middleware/admin"""
    count = await prisma.user.count()
    
    return {
        "success": True,
        "count": count
    }