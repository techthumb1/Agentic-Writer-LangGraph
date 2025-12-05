from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from langgraph_app.database import prisma
import json
from datetime import datetime
import io

router = APIRouter()

@router.post("/user/export")
async def export_user_data(x_user_id: str = Header(..., alias="X-User-Id")):
    """Export complete user data for GDPR compliance"""
    
    user = await prisma.user.find_unique(
        where={"id": x_user_id},
        include={
            "generated_content": {
                "select": {
                    "id": True,
                    "title": True,
                    "content": True,
                    "wordCount": True,
                    "status": True,
                    "createdAt": True,
                    "templateId": True,
                    "styleProfileId": True
                },
                "order_by": {"createdAt": "desc"}
            },
            "content_templates": {
                "select": {
                    "id": True,
                    "title": True,
                    "description": True,
                    "category": True,
                    "createdAt": True
                }
            },
            "style_profiles": {
                "select": {
                    "id": True,
                    "name": True,
                    "description": True,
                    "category": True,
                    "createdAt": True
                }
            },
            "usage_stats": {
                "select": {
                    "date": True,
                    "contentGenerated": True,
                    "tokensConsumed": True,
                    "generationTime": True,
                    "modelsUsed": True
                },
                "order_by": {"date": "desc"},
                "take": 90
            },
            "subscriptions": {
                "select": {
                    "plan": True,
                    "status": True,
                    "startDate": True,
                    "endDate": True,
                    "monthlyTokenLimit": True,
                    "monthlyContentLimit": True
                }
            }
        }
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate aggregations
    total_content = sum(s.contentGenerated for s in user.usage_stats)
    total_tokens = sum(s.tokensConsumed for s in user.usage_stats)
    total_time = sum(s.generationTime for s in user.usage_stats)
    avg_words = (
        sum(c.wordCount for c in user.generated_content) / len(user.generated_content)
        if user.generated_content else 0
    )
    
    user_data = {
        "profile": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "image": user.image,
            "bio": getattr(user, "bio", None),
            "avatar": getattr(user, "avatar", None),
            "language": getattr(user, "language", None),
            "timezone": getattr(user, "timezone", None),
            "emailVerified": user.emailVerified.isoformat() if user.emailVerified else None,
            "createdAt": user.createdAt.isoformat(),
            "updatedAt": user.updatedAt.isoformat()
        },
        "preferences": {
            "notifications": {
                "email": getattr(user, "emailNotifications", True),
                "push": getattr(user, "pushNotifications", False),
                "marketing": getattr(user, "marketingCommunications", False)
            },
            "generation": {
                "defaultMaxTokens": getattr(user, "defaultMaxTokens", 2000),
                "defaultTemperature": getattr(user, "defaultTemperature", 0.7),
                "defaultModel": getattr(user, "defaultModel", "gpt-4"),
                "defaultContentQuality": getattr(user, "defaultContentQuality", "high")
            },
            "system": {
                "autoSave": getattr(user, "autoSave", True),
                "backupFrequency": getattr(user, "backupFrequency", "daily")
            }
        },
        "content": {
            "generated": [
                {
                    "id": c.id,
                    "title": c.title or "Untitled",
                    "wordCount": c.wordCount,
                    "status": c.status,
                    "templateId": c.templateId,
                    "styleProfileId": c.styleProfileId,
                    "createdAt": c.createdAt.isoformat(),
                    "contentPreview": c.content[:500] + "..."
                }
                for c in user.generated_content
            ],
            "templates": [
                {k: v for k, v in t.__dict__.items() if not k.startswith("_")}
                for t in user.content_templates
            ],
            "styleProfiles": [
                {k: v for k, v in s.__dict__.items() if not k.startswith("_")}
                for s in user.style_profiles
            ],
            "statistics": {
                "totalGenerated": len(user.generated_content),
                "totalTemplates": len(user.content_templates),
                "totalStyleProfiles": len(user.style_profiles)
            }
        },
        "usage": {
            "summary": {
                "totalContentGenerated": total_content,
                "totalTokensConsumed": total_tokens,
                "totalGenerationTimeMs": total_time,
                "averageWordsPerContent": round(avg_words)
            },
            "dailyStats": [
                {
                    "date": s.date.isoformat().split("T")[0],
                    "contentGenerated": s.contentGenerated,
                    "tokensConsumed": s.tokensConsumed,
                    "generationTime": s.generationTime,
                    "modelsUsed": s.modelsUsed
                }
                for s in user.usage_stats
            ]
        },
        "subscription": (
            {
                "plan": user.subscriptions.plan,
                "status": user.subscriptions.status,
                "startDate": user.subscriptions.startDate.isoformat(),
                "endDate": user.subscriptions.endDate.isoformat() if user.subscriptions.endDate else None,
                "limits": {
                    "monthlyTokens": user.subscriptions.monthlyTokenLimit,
                    "monthlyContent": user.subscriptions.monthlyContentLimit
                }
            }
            if user.subscriptions else None
        ),
        "export": {
            "requestedAt": datetime.utcnow().isoformat(),
            "format": "JSON",
            "version": "1.0",
            "gdprCompliant": True
        }
    }
    
    json_data = json.dumps(user_data, indent=2)
    return StreamingResponse(
        io.BytesIO(json_data.encode()),
        media_type="application/json"
    )

@router.get("/user/export/info")
async def get_export_info(x_user_id: str = Header(..., alias="X-User-Id")):
    """Get export metadata"""
    
    counts = await prisma.user.find_unique(
        where={"id": x_user_id},
        select={
            "_count": {
                "select": {
                    "generated_content": True,
                    "content_templates": True,
                    "style_profiles": True,
                    "usage_stats": True
                }
            }
        }
    )
    
    if not counts:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "message": "Export endpoint available",
        "supportedFormats": ["JSON"],
        "dataTypes": [
            "Profile information",
            "User preferences",
            "Generated content",
            "Usage statistics",
            "Account settings",
            "Subscription details"
        ],
        "statistics": {
            "generatedContent": counts._count.generated_content,
            "templates": counts._count.content_templates,
            "styleProfiles": counts._count.style_profiles,
            "usageRecords": counts._count.usage_stats
        },
        "note": "Use POST method to download complete data export",
        "gdprCompliant": True
    }