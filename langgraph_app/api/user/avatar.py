# langgraph_app/api/user/avatar.py
from fastapi import APIRouter, File, UploadFile, Header, HTTPException
from langgraph_app.db_client import prisma
from pathlib import Path
import shutil
from datetime import datetime

router = APIRouter()

@router.post("/api/user/avatar")
async def upload_avatar(
    avatar: UploadFile = File(...),
    userId: str = Header(..., alias="userId")
):
    """Upload and save user avatar"""
    from pathlib import Path
    import shutil
    from datetime import datetime
    
    # Validate file type
    if not avatar.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validate size (5MB max)
    avatar.file.seek(0, 2)
    size = avatar.file.tell()
    avatar.file.seek(0)
    if size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    
    # Save file
    upload_dir = Path("static/avatars")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    ext = avatar.filename.split('.')[-1]
    filename = f"{userId}_{int(datetime.now().timestamp())}.{ext}"
    file_path = upload_dir / filename
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(avatar.file, buffer)
    
    # Update user
    avatar_url = f"/avatars/{filename}"
    await prisma.user.update(
        where={"id": userId},
        data={"image": avatar_url}
    )
    
    return {"success": True, "avatarUrl": avatar_url}