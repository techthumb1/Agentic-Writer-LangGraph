from fastapi import APIRouter, Header
from langgraph_app.database import prisma
import uuid

router = APIRouter()
@router.post("/content/save")
async def save_content(
    data: dict,
    x_user_id: str = Header(..., alias="X-User-Id")
):
    """Save content"""
    content = await prisma.content.create(
        data={
            "id": str(uuid.uuid4()),
            "userId": x_user_id,
            "title": data.get("title", "Untitled"),
            "content": data.get("content", ""),
            "contentHtml": data.get("contentHtml"),
            "status": data.get("status", "draft"),
            "type": data.get("type", "article"),
            "metadata": data.get("metadata", {})
        }
    )
    
    return {
        "success": True,
        "contentId": content.id
    }