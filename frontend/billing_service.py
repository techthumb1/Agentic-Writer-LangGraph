# langgraph_app/billing_service.py - ENTERPRISE BILLING & REVENUE ENGINE
"""
💰 ENTERPRISE BILLING & REVENUE SERVICE
🏢 Subscription Management & Usage Tracking
📊 Revenue Optimization & Analytics
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

logger = logging.getLogger(__name__)

class SubscriptionTier(Enum):
    """Subscription tier definitions"""
    FREE = "free"
    STARTER = "starter"  # $29/month
    PROFESSIONAL = "professional"  # $99/month
    ENTERPRISE = "enterprise"  # $299/month
    ENTERPRISE_PLUS = "enterprise_plus"  # $599/month

class UsageType(Enum):
    """Types of billable usage"""
    BASIC_GENERATION = "basic_generation"
    PREMIUM_GENERATION = "premium_generation"
    INNOVATION_GENERATION = "innovation_generation"
    BULK_GENERATION = "bulk_generation"
    API_CALL = "api_call"
    PREMIUM_TEMPLATE = "premium_template"
    CUSTOM_STYLE = "custom_style"

@dataclass
class PricingTier:
    """Pricing configuration for each tier"""
    name: str
    monthly_price: float
    generation_limit: int  # -1 for unlimited
    premium_generations: int
    innovation_features: bool
    api_access: bool
    priority_support: bool
    custom_templates: bool
    white_label: bool
    
    # Per-usage pricing (when over limits)
    overage_price_per_generation: float
    premium_generation_price: float
    innovation_generation_price: float

# Enterprise pricing configuration
PRICING_TIERS = {
    SubscriptionTier.FREE: PricingTier(
        name="Free",
        monthly_price=0.0,
        generation_limit=10,
        premium_generations=0,
        innovation_features=False,
        api_access=False,
        priority_support=False,
        custom_templates=False,
        white_label=False,
        overage_price_per_generation=0.75,
        premium_generation_price=1.50,
        innovation_generation_price=2.50
    ),
    SubscriptionTier.STARTER: PricingTier(
        name="Starter",
        monthly_price=29.0,
        generation_limit=500,
        premium_generations=50,
        innovation_features=False,
        api_access=True,
        priority_support=False,
        custom_templates=False,
        white_label=False,
        overage_price_per_generation=0.50,
        premium_generation_price=1.00,
        innovation_generation_price=2.00
    ),
    SubscriptionTier.PROFESSIONAL: PricingTier(
        name="Professional",
        monthly_price=99.0,
        generation_limit=2000,
        premium_generations=500,
        innovation_features=True,
        api_access=True,
        priority_support=True,
        custom_templates=True,
        white_label=False,
        overage_price_per_generation=0.35,
        premium_generation_price=0.75,
        innovation_generation_price=1.50
    ),
    SubscriptionTier.ENTERPRISE: PricingTier(
        name="Enterprise",
        monthly_price=299.0,
        generation_limit=10000,
        premium_generations=2500,
        innovation_features=True,
        api_access=True,
        priority_support=True,
        custom_templates=True,
        white_label=True,
        overage_price_per_generation=0.25,
        premium_generation_price=0.50,
        innovation_generation_price=1.00
    ),
    SubscriptionTier.ENTERPRISE_PLUS: PricingTier(
        name="Enterprise Plus",
        monthly_price=599.0,
        generation_limit=-1,  # Unlimited
        premium_generations=-1,  # Unlimited
        innovation_features=True,
        api_access=True,
        priority_support=True,
        custom_templates=True,
        white_label=True,
        overage_price_per_generation=0.0,
        premium_generation_price=0.0,
        innovation_generation_price=0.0
    )
}

@dataclass
class UsageRecord:
    """Individual usage record for billing"""
    id: str
    user_id: str
    usage_type: UsageType
    quantity: int
    unit_price: float
    total_cost: float
    metadata: Dict[str, Any]
    timestamp: datetime
    billing_period: str  # YYYY-MM format

@dataclass
class BillingAccount:
    """Enterprise billing account"""
    user_id: str
    subscription_tier: SubscriptionTier
    current_period_start: datetime
    current_period_end: datetime
    usage_records: List[UsageRecord]
    monthly_subscription_cost: float
    current_period_usage_cost: float
    total_cost_current_period: float
    payment_method_id: Optional[str] = None
    billing_email: Optional[str] = None
    company_name: Optional[str] = None

class EnterpriseBillingService:
    """Enterprise billing and revenue management"""
    
    def __init__(self):
        self.billing_accounts: Dict[str, BillingAccount] = {}
        self.usage_records: List[UsageRecord] = []
        
    def create_billing_account(self, user_id: str, subscription_tier: SubscriptionTier = SubscriptionTier.FREE) -> BillingAccount:
        """Create new billing account"""
        now = datetime.now()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        pricing = PRICING_TIERS[subscription_tier]
        
        account = BillingAccount(
            user_id=user_id,
            subscription_tier=subscription_tier,
            current_period_start=period_start,
            current_period_end=period_end,
            usage_records=[],
            monthly_subscription_cost=pricing.monthly_price,
            current_period_usage_cost=0.0,
            total_cost_current_period=pricing.monthly_price
        )
        
        self.billing_accounts[user_id] = account
        logger.info(f"💰 Created billing account for {user_id} ({subscription_tier.value})")
        return account
    
    def record_usage(self, user_id: str, usage_type: UsageType, quantity: int = 1, 
                    metadata: Dict[str, Any] = None) -> UsageRecord:
        """Record billable usage"""
        if user_id not in self.billing_accounts:
            self.create_billing_account(user_id)
        
        account = self.billing_accounts[user_id]
        pricing = PRICING_TIERS[account.subscription_tier]
        
        # Calculate cost based on usage type and tier
        unit_price = self._calculate_unit_price(usage_type, pricing, account)
        total_cost = unit_price * quantity
        
        # Create usage record
        usage_record = UsageRecord(
            id=str(uuid.uuid4()),
            user_id=user_id,
            usage_type=usage_type,
            quantity=quantity,
            unit_price=unit_price,
            total_cost=total_cost,
            metadata=metadata or {},
            timestamp=datetime.now(),
            billing_period=datetime.now().strftime("%Y-%m")
        )
        
        # Add to account and global records
        account.usage_records.append(usage_record)
        self.usage_records.append(usage_record)
        
        # Update account totals
        account.current_period_usage_cost += total_cost
        account.total_cost_current_period = account.monthly_subscription_cost + account.current_period_usage_cost
        
        logger.info(f"💳 Recorded usage: {user_id} - {usage_type.value} x{quantity} = ${total_cost:.2f}")
        return usage_record
    
    def _calculate_unit_price(self, usage_type: UsageType, pricing: PricingTier, account: BillingAccount) -> float:
        """Calculate unit price based on usage type and tier"""
        current_period_usage = self._get_current_period_usage(account)
        
        if usage_type == UsageType.BASIC_GENERATION:
            # Check if within included limit
            basic_generations = current_period_usage.get(UsageType.BASIC_GENERATION, 0)
            if pricing.generation_limit == -1 or basic_generations < pricing.generation_limit:
                return 0.0  # Within included limit
            else:
                return pricing.overage_price_per_generation
        
        elif usage_type == UsageType.PREMIUM_GENERATION:
            premium_generations = current_period_usage.get(UsageType.PREMIUM_GENERATION, 0)
            if pricing.premium_generations == -1 or premium_generations < pricing.premium_generations:
                return 0.0  # Within included limit
            else:
                return pricing.premium_generation_price
        
        elif usage_type == UsageType.INNOVATION_GENERATION:
            if not pricing.innovation_features:
                return pricing.innovation_generation_price * 1.5  # Premium for non-innovation tiers
            return pricing.innovation_generation_price
        
        elif usage_type == UsageType.API_CALL:
            if not pricing.api_access:
                return 0.10  # Charge for API access on free tier
            return 0.0
        
        elif usage_type == UsageType.PREMIUM_TEMPLATE:
            if not pricing.custom_templates:
                return 5.00  # One-time fee for premium templates
            return 0.0
        
        else:
            return 0.0
    
    def _get_current_period_usage(self, account: BillingAccount) -> Dict[UsageType, int]:
        """Get usage counts for current billing period"""
        current_period = datetime.now().strftime("%Y-%m")
        usage_counts = {}
        
        for record in account.usage_records:
            if record.billing_period == current_period:
                usage_type = record.usage_type
                usage_counts[usage_type] = usage_counts.get(usage_type, 0) + record.quantity
        
        return usage_counts
    
    def get_account_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive account summary"""
        if user_id not in self.billing_accounts:
            raise HTTPException(status_code=404, detail="Billing account not found")
        
        account = self.billing_accounts[user_id]
        pricing = PRICING_TIERS[account.subscription_tier]
        current_usage = self._get_current_period_usage(account)
        
        # Calculate usage limits and remaining
        basic_remaining = (
            pricing.generation_limit - current_usage.get(UsageType.BASIC_GENERATION, 0)
            if pricing.generation_limit != -1 else -1
        )
        premium_remaining = (
            pricing.premium_generations - current_usage.get(UsageType.PREMIUM_GENERATION, 0)
            if pricing.premium_generations != -1 else -1
        )
        
        return {
            "user_id": user_id,
            "subscription": {
                "tier": account.subscription_tier.value,
                "name": pricing.name,
                "monthly_cost": pricing.monthly_price,
                "features": {
                    "generation_limit": pricing.generation_limit,
                    "premium_generations": pricing.premium_generations,
                    "innovation_features": pricing.innovation_features,
                    "api_access": pricing.api_access,
                    "priority_support": pricing.priority_support,
                    "custom_templates": pricing.custom_templates,
                    "white_label": pricing.white_label
                }
            },
            "current_period": {
                "start": account.current_period_start.isoformat(),
                "end": account.current_period_end.isoformat(),
                "subscription_cost": account.monthly_subscription_cost,
                "usage_cost": account.current_period_usage_cost,
                "total_cost": account.total_cost_current_period
            },
            "usage": {
                "basic_generations": {
                    "used": current_usage.get(UsageType.BASIC_GENERATION, 0),
                    "limit": pricing.generation_limit,
                    "remaining": basic_remaining
                },
                "premium_generations": {
                    "used": current_usage.get(UsageType.PREMIUM_GENERATION, 0),
                    "limit": pricing.premium_generations,
                    "remaining": premium_remaining
                },
                "innovation_generations": current_usage.get(UsageType.INNOVATION_GENERATION, 0),
                "api_calls": current_usage.get(UsageType.API_CALL, 0)
            },
            "upgrade_recommendations": self._get_upgrade_recommendations(account, current_usage)
        }
    
    def _get_upgrade_recommendations(self, account: BillingAccount, current_usage: Dict[UsageType, int]) -> List[Dict[str, Any]]:
        """Generate upgrade recommendations based on usage patterns"""
        recommendations = []
        current_tier = account.subscription_tier
        current_pricing = PRICING_TIERS[current_tier]
        
        # Check if approaching limits
        basic_usage = current_usage.get(UsageType.BASIC_GENERATION, 0)
        premium_usage = current_usage.get(UsageType.PREMIUM_GENERATION, 0)
        
        if current_tier == SubscriptionTier.FREE:
            if basic_usage >= 8:  # 80% of free limit
                recommendations.append({
                    "type": "usage_limit",
                    "message": "You're approaching your free generation limit. Upgrade to Starter for 500 generations/month.",
                    "suggested_tier": "starter",
                    "savings": "Save $0.25 per generation with a monthly plan"
                })
        
        elif current_tier == SubscriptionTier.STARTER:
            if basic_usage >= 400:  # 80% of starter limit
                recommendations.append({
                    "type": "usage_limit", 
                    "message": "Upgrade to Professional for 4x more generations plus innovation features.",
                    "suggested_tier": "professional",
                    "savings": f"Break-even at {int(70/0.15)} extra generations"
                })
            
            if premium_usage > 0:
                recommendations.append({
                    "type": "feature_usage",
                    "message": "You're using premium features. Professional tier includes 500 premium generations.",
                    "suggested_tier": "professional",
                    "savings": "Included premium generations save $0.75 each"
                })
        
        elif current_tier == SubscriptionTier.PROFESSIONAL:
            if basic_usage >= 1600:  # 80% of pro limit
                recommendations.append({
                    "type": "usage_limit",
                    "message": "Upgrade to Enterprise for 5x more generations plus white-label options.",
                    "suggested_tier": "enterprise", 
                    "savings": "Lower per-generation overage costs"
                })
        
        elif current_tier == SubscriptionTier.ENTERPRISE:
            if basic_usage >= 8000:  # 80% of enterprise limit
                recommendations.append({
                    "type": "usage_limit",
                    "message": "Upgrade to Enterprise Plus for unlimited generations.",
                    "suggested_tier": "enterprise_plus",
                    "savings": "No overage charges, unlimited premium features"
                })
        
        return recommendations
    
    def calculate_potential_savings(self, user_id: str, target_tier: SubscriptionTier) -> Dict[str, Any]:
        """Calculate potential cost savings from tier upgrade"""
        if user_id not in self.billing_accounts:
            raise HTTPException(status_code=404, detail="Billing account not found")
        
        account = self.billing_accounts[user_id]
        current_usage = self._get_current_period_usage(account)
        current_pricing = PRICING_TIERS[account.subscription_tier]
        target_pricing = PRICING_TIERS[target_tier]
        
        # Calculate current total cost
        current_total = account.total_cost_current_period
        
        # Calculate cost with target tier
        target_subscription_cost = target_pricing.monthly_price
        target_usage_cost = 0.0
        
        # Recalculate usage costs with target tier pricing
        for usage_type, quantity in current_usage.items():
            if usage_type == UsageType.BASIC_GENERATION:
                if target_pricing.generation_limit == -1 or quantity <= target_pricing.generation_limit:
                    continue  # Within limit
                else:
                    overage = quantity - target_pricing.generation_limit
                    target_usage_cost += overage * target_pricing.overage_price_per_generation
            
            elif usage_type == UsageType.PREMIUM_GENERATION:
                if target_pricing.premium_generations == -1 or quantity <= target_pricing.premium_generations:
                    continue  # Within limit
                else:
                    overage = quantity - target_pricing.premium_generations
                    target_usage_cost += overage * target_pricing.premium_generation_price
        
        target_total = target_subscription_cost + target_usage_cost
        monthly_savings = current_total - target_total
        annual_savings = monthly_savings * 12
        
        return {
            "current_tier": account.subscription_tier.value,
            "target_tier": target_tier.value,
            "current_monthly_cost": current_total,
            "target_monthly_cost": target_total,
            "monthly_savings": monthly_savings,
            "annual_savings": annual_savings,
            "break_even_point": abs(monthly_savings) if monthly_savings < 0 else 0,
            "recommendation": "upgrade" if monthly_savings > 0 else "stay" if monthly_savings == 0 else "analyze"
        }

# FastAPI app for billing service
app = FastAPI(
    title="Enterprise Billing & Revenue Service",
    description="Advanced billing, subscription management, and revenue optimization",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global billing service
billing_service = EnterpriseBillingService()

# Pydantic models for API
class CreateAccountRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    subscription_tier: str = Field(default="free")
    billing_email: Optional[str] = None
    company_name: Optional[str] = None

class RecordUsageRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    usage_type: str = Field(..., min_length=1)
    quantity: int = Field(default=1, ge=1)
    metadata: Optional[Dict[str, Any]] = None

class UpgradeRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    target_tier: str = Field(..., min_length=1)

# API Endpoints
@app.post("/api/accounts")
async def create_account(request: CreateAccountRequest):
    """Create new billing account"""
    try:
        tier = SubscriptionTier(request.subscription_tier)
        account = billing_service.create_billing_account(request.user_id, tier)
        
        if request.billing_email:
            account.billing_email = request.billing_email
        if request.company_name:
            account.company_name = request.company_name
        
        return {
            "success": True,
            "account": asdict(account),
            "message": f"Billing account created for {request.user_id}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid subscription tier: {request.subscription_tier}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/usage")
async def record_usage(request: RecordUsageRequest):
    """Record billable usage"""
    try:
        usage_type = UsageType(request.usage_type)
        usage_record = billing_service.record_usage(
            request.user_id, 
            usage_type, 
            request.quantity, 
            request.metadata
        )
        
        return {
            "success": True,
            "usage_record": asdict(usage_record),
            "total_cost": usage_record.total_cost
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid usage type: {request.usage_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/accounts/{user_id}")
async def get_account_summary(user_id: str):
    """Get comprehensive account summary"""
    try:
        summary = billing_service.get_account_summary(user_id)
        return {
            "success": True,
            "account_summary": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pricing")
async def get_pricing_tiers():
    """Get all pricing tier information"""
    pricing_info = {}
    for tier, pricing in PRICING_TIERS.items():
        pricing_info[tier.value] = {
            "name": pricing.name,
            "monthly_price": pricing.monthly_price,
            "generation_limit": pricing.generation_limit,
            "premium_generations": pricing.premium_generations,
            "features": {
                "innovation_features": pricing.innovation_features,
                "api_access": pricing.api_access,
                "priority_support": pricing.priority_support,
                "custom_templates": pricing.custom_templates,
                "white_label": pricing.white_label
            },
            "overage_pricing": {
                "basic_generation": pricing.overage_price_per_generation,
                "premium_generation": pricing.premium_generation_price,
                "innovation_generation": pricing.innovation_generation_price
            }
        }
    
    return {
        "success": True,
        "pricing_tiers": pricing_info
    }

@app.post("/api/calculate-savings")
async def calculate_savings(request: UpgradeRequest):
    """Calculate potential savings from tier upgrade"""
    try:
        target_tier = SubscriptionTier(request.target_tier)
        savings = billing_service.calculate_potential_savings(request.user_id, target_tier)
        
        return {
            "success": True,
            "savings_analysis": savings
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid target tier: {request.target_tier}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/revenue")
async def get_revenue_analytics():
    """Get revenue analytics"""
    total_revenue = 0.0
    total_accounts = len(billing_service.billing_accounts)
    tier_breakdown = {}
    
    for account in billing_service.billing_accounts.values():
        total_revenue += account.total_cost_current_period
        tier = account.subscription_tier.value
        tier_breakdown[tier] = tier_breakdown.get(tier, 0) + 1
    
    mrr = sum(account.monthly_subscription_cost for account in billing_service.billing_accounts.values())
    arr = mrr * 12
    
    return {
        "success": True,
        "revenue_analytics": {
            "total_monthly_revenue": total_revenue,
            "monthly_recurring_revenue": mrr,
            "annual_recurring_revenue": arr,
            "total_accounts": total_accounts,
            "tier_breakdown": tier_breakdown,
            "average_revenue_per_user": total_revenue / max(total_accounts, 1),
            "timestamp": datetime.now().isoformat()
        }
    }

@app.get("/api/analytics/usage")
async def get_usage_analytics():
    """Get usage analytics"""
    usage_stats = {}
    total_usage = 0
    
    for record in billing_service.usage_records:
        usage_type = record.usage_type.value
        usage_stats[usage_type] = usage_stats.get(usage_type, 0) + record.quantity
        total_usage += record.quantity
    
    return {
        "success": True,
        "usage_analytics": {
            "total_usage_events": total_usage,
            "usage_by_type": usage_stats,
            "total_usage_records": len(billing_service.usage_records),
            "timestamp": datetime.now().isoformat()
        }
    }

@app.get("/health")
async def health_check():
    """Health check for billing service"""
    return {
        "status": "healthy",
        "service": "enterprise_billing",
        "total_accounts": len(billing_service.billing_accounts),
        "total_usage_records": len(billing_service.usage_records),
        "timestamp": datetime.now().isoformat()
    }

# Initialize some demo accounts for testing
@app.on_event("startup")
async def startup_event():
    """Initialize demo data"""
    logger.info("💰 Initializing Enterprise Billing Service")
    
    # Create demo accounts
    demo_users = [
        ("demo_free", SubscriptionTier.FREE),
        ("demo_starter", SubscriptionTier.STARTER), 
        ("demo_pro", SubscriptionTier.PROFESSIONAL),
        ("demo_enterprise", SubscriptionTier.ENTERPRISE)
    ]
    
    for user_id, tier in demo_users:
        billing_service.create_billing_account(user_id, tier)
        
        # Add some demo usage
        billing_service.record_usage(user_id, UsageType.BASIC_GENERATION, 5)
        if tier != SubscriptionTier.FREE:
            billing_service.record_usage(user_id, UsageType.PREMIUM_GENERATION, 2)
        if tier in [SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE]:
            billing_service.record_usage(user_id, UsageType.INNOVATION_GENERATION, 1)
    
    logger.info("✅ Demo billing accounts created")

if __name__ == "__main__":
    uvicorn.run(
        "billing_service:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )