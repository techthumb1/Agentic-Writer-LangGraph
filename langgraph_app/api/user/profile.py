from fastapi import APIRouter, HTTPException
from langgraph_app.integrated_server import prisma

router = APIRouter()

@router.put("/user/profile")
async def update_profile(data: dict):
    """Update user profile"""
    user_id = data.get("userId")
    
    updated = await prisma.user.update(
        where={"id": user_id},
        data={
            "name": data.get("name"),
            "email": data.get("email")
        }
    )
    
    return {
        "success": True,
        "user": {
            "name": updated.name,
            "email": updated.email
        }
    }