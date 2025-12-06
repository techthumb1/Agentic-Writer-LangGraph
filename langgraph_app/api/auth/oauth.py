# langgraph_app/api/auth/oauth.py
from fastapi import APIRouter, HTTPException
from langgraph_app.db_client import prisma
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/auth/user-by-email")
async def get_user_by_email(data: dict):
    """Find user by email for Google OAuth flow"""
    email = data.get("email")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    
    user = await prisma.user.find_unique(where={"email": email.lower().strip()})
    
    if not user:
        return {"user": None}
    
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "image": user.image,
            "emailVerified": user.emailVerified.isoformat() if user.emailVerified else None,
            "createdAt": user.createdAt.isoformat(),
            "updatedAt": user.updatedAt.isoformat()
        }
    }

@router.post("/auth/sync-user")
async def sync_oauth_user(data: dict):
    """Create or update user from OAuth provider (Google)"""
    email = data.get("email")
    name = data.get("name")
    image = data.get("image")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    
    # Check if user exists
    existing = await prisma.user.find_unique(where={"email": email.lower().strip()})
    
    if existing:
        # Update existing user
        user = await prisma.user.update(
            where={"id": existing.id},
            data={
                "name": name or existing.name,
                "image": image or existing.image,
                "emailVerified": datetime.utcnow()
            }
        )
    else:
        # Create new user
        user = await prisma.user.create(
            data={
                "id": str(uuid.uuid4()),
                "email": email.lower().strip(),
                "name": name or email.split("@")[0],
                "image": image,
                "emailVerified": datetime.utcnow()
            }
        )
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "image": user.image,
            "emailVerified": user.emailVerified.isoformat() if user.emailVerified else None
        }
    }