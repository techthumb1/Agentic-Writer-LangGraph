# langgraph_app/api/content/crud.py
from fastapi import APIRouter, Header, HTTPException
from langgraph_app.db_client import prisma

router = APIRouter()

@router.get("/content/{content_id}")
async def get_single_content(
    content_id: str,
    x_user_id: str = Header(..., alias="X-User-Id")
):
    """Get single content item by ID"""
    content = await prisma.content.find_unique(
        where={"id": content_id}
    )
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Verify ownership
    if content.userId != x_user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "id": content.id,
        "title": content.title,
        "content": content.content,
        "contentHtml": content.contentHtml,
        "status": content.status,
        "type": content.type,
        "createdAt": content.createdAt.isoformat(),
        "updatedAt": content.updatedAt.isoformat(),
        "metadata": content.metadata or {}
    }

@router.put("/content/{content_id}")
async def update_content(
    content_id: str,
    data: dict,
    x_user_id: str = Header(..., alias="X-User-Id")
):
    """Update existing content"""
    # Verify content exists and user owns it
    existing = await prisma.content.find_unique(where={"id": content_id})
    
    if not existing:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if existing.userId != x_user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update content
    updated = await prisma.content.update(
        where={"id": content_id},
        data={
            "title": data.get("title", existing.title),
            "content": data.get("content", existing.content),
            "contentHtml": data.get("contentHtml", existing.contentHtml),
            "status": data.get("status", existing.status),
            "metadata": data.get("metadata", existing.metadata)
        }
    )
    
    return {
        "success": True,
        "content": {
            "id": updated.id,
            "title": updated.title,
            "status": updated.status,
            "updatedAt": updated.updatedAt.isoformat()
        }
    }

@router.delete("/content/{content_id}")
async def delete_content(
    content_id: str,
    x_user_id: str = Header(..., alias="X-User-Id")
):
    """Delete content"""
    # Verify content exists and user owns it
    existing = await prisma.content.find_unique(where={"id": content_id})
    
    if not existing:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if existing.userId != x_user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete content
    await prisma.content.delete(where={"id": content_id})
    
    return {
        "success": True,
        "message": "Content deleted successfully"
    }