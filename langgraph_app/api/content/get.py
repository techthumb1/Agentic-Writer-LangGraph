from fastapi import APIRouter, Header
from langgraph_app.db_client import prisma

router = APIRouter()

@router.get("/content")
async def get_content(x_user_id: str = Header(..., alias="X-User-Id")):
    """Get all user content"""
    content = await prisma.content.find_many(
        where={"userId": x_user_id},
        order_by={"createdAt": "desc"}
    )
    
    return {
        "content": [
            {
                "id": c.id,
                "title": c.title,
                "status": c.status,
                "type": c.type,
                "createdAt": c.createdAt.isoformat(),
                "updatedAt": c.updatedAt.isoformat()
            }
            for c in content
        ],
        "stats": {
            "total": len(content),
            "published": sum(1 for c in content if c.status == "published"),
            "drafts": sum(1 for c in content if c.status == "draft")
        }
    }