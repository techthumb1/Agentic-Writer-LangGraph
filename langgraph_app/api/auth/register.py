# langgraph_app/api/auth/register.py

from fastapi import APIRouter, HTTPException
from passlib.hash import bcrypt
from prisma import Prisma
import uuid

router = APIRouter()
prisma = Prisma()

@router.post("/api/auth/register")
async def register_user(data: dict):
    """Register new user with hashed password"""
    
    email = data.get("email")
    name = data.get("name")
    password = data.get("password")
    
    # Check if user exists
    existing = await prisma.user.find_unique(where={"email": email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    # Hash password
    hashed_password = bcrypt.hash(password)
    
    # Create user
    user = await prisma.user.create(
        data={
            "id": str(uuid.uuid4()),
            "email": email,
            "name": name,
            "password": hashed_password,
            "emailVerified": None
        }
    )
    
    # TODO: Send verification email
    return {"success": True, "message": "Registration successful. Check email to verify."}