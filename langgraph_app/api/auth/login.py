from fastapi import APIRouter, HTTPException
from passlib.hash import bcrypt
from langgraph_app.db_client import prisma

router = APIRouter()


@router.post("/auth/login")
async def login(data: dict):
    """Authenticate user with email/password"""
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    user = await prisma.user.find_unique(where={"email": email.lower().strip()})
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check password hash
    stored_hash = user.passwordHash or user.hashedPassword or user.password
    if not stored_hash or not bcrypt.verify(password, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "image": user.image
    }