from fastapi import APIRouter, HTTPException
from prisma import Prisma
from datetime import datetime

router = APIRouter()
prisma = Prisma()

@router.post("/api/auth/verify")
async def verify_email(data: dict):
    """Verify email token and activate account"""
    from datetime import datetime
    
    token = data.get("token")
    
    # Find user with valid token
    user = await prisma.user.find_first(
        where={
            "verificationToken": token,
            "tokenExpires": {"gt": datetime.now()}
        }
    )
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Update user
    await prisma.user.update(
        where={"id": user.id},
        data={
            "emailVerified": datetime.now(),
            "verificationToken": None,
            "tokenExpires": None
        }
    )
    
    return {"success": True, "verified": True}