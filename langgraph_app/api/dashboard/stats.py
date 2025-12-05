from fastapi import APIRouter, Header
from prisma import Prisma

router = APIRouter()
prisma = Prisma()

@router.get("/dashboard/stats")
async def get_dashboard_stats(x_user_id: str = Header(..., alias="X-User-Id")):
    """Get user dashboard statistics"""
    content = await prisma.content.find_many(
        where={"userId": x_user_id},
        order_by={"updatedAt": "desc"}
    )
    
    total_views = sum(c.views or 0 for c in content)
    
    return {
        "total_content": len(content),
        "drafts": sum(1 for c in content if c.status == "draft"),
        "published": sum(1 for c in content if c.status == "published"),
        "views": total_views,
        "recent_content": [
            {
                "id": c.id,
                "title": c.title,
                "status": c.status,
                "updated_at": c.updatedAt.isoformat(),
                "type": c.type
            }
            for c in content[:5]
        ],
        "recent_activity": [
            {
                "id": c.id,
                "type": "published" if c.status == "published" else "updated",
                "description": f"{'Published' if c.status == 'published' else 'Updated'} \"{c.title}\"",
                "timestamp": c.updatedAt.isoformat()
            }
            for c in content[:5]
        ]
    }