# langgraph_app/monitoring_server.py - ENTERPRISE MONITORING & ANALYTICS
"""
🔍 ENTERPRISE MONITORING & ANALYTICS SERVICE
💰 Revenue Tracking & Performance Optimization
📊 Real-time Business Intelligence Dashboard
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

logger = logging.getLogger(__name__)

@dataclass
class RevenueMetrics:
    """Enterprise revenue tracking"""
    total_generations: int = 0
    premium_generations: int = 0
    enterprise_generations: int = 0
    total_revenue: float = 0.0
    avg_generation_value: float = 0.0
    conversion_rate: float = 0.0
    monthly_recurring_revenue: float = 0.0

@dataclass
class PerformanceMetrics:
    """System performance tracking"""
    avg_generation_time: float = 0.0
    success_rate: float = 100.0
    uptime_percentage: float = 100.0
    active_users: int = 0
    queue_length: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0

@dataclass
class QualityMetrics:
    """Content quality analytics"""
    avg_quality_score: float = 85.0
    avg_innovation_score: float = 0.5
    customer_satisfaction: float = 4.5
    content_categories: Dict[str, int] = None
    premium_features_usage: Dict[str, int] = None

class EnterpriseMonitoringService:
    """Real-time enterprise monitoring and analytics"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.metrics_history: List[Dict] = []
        
        # Initialize metrics
        self.revenue_metrics = RevenueMetrics()
        self.performance_metrics = PerformanceMetrics()
        self.quality_metrics = QualityMetrics(
            content_categories={},
            premium_features_usage={}
        )
        
        # Start background monitoring
        asyncio.create_task(self._collect_metrics())
    
    async def connect(self, websocket: WebSocket):
        """Connect new monitoring client"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"📊 New monitoring client connected ({len(self.active_connections)} total)")
        
        # Send initial metrics
        await self._send_to_client(websocket, {
            "type": "initial_metrics",
            "revenue": asdict(self.revenue_metrics),
            "performance": asdict(self.performance_metrics),
            "quality": asdict(self.quality_metrics),
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect monitoring client"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"📊 Monitoring client disconnected ({len(self.active_connections)} remaining)")
    
    async def _send_to_client(self, websocket: WebSocket, data: Dict):
        """Send data to specific client"""
        try:
            await websocket.send_json(data)
        except Exception as e:
            logger.error(f"Failed to send to client: {e}")
            self.disconnect(websocket)
    
    async def broadcast_metrics(self, metrics: Dict):
        """Broadcast metrics to all connected clients"""
        if not self.active_connections:
            return
        
        message = {
            "type": "metrics_update",
            "data": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def record_generation(self, generation_data: Dict):
        """Record a new content generation for analytics"""
        try:
            # Update revenue metrics
            generation_tier = generation_data.get("tier", "standard")
            generation_value = self._calculate_generation_value(generation_data)
            
            self.revenue_metrics.total_generations += 1
            self.revenue_metrics.total_revenue += generation_value
            
            if generation_tier == "premium":
                self.revenue_metrics.premium_generations += 1
            elif generation_tier == "enterprise":
                self.revenue_metrics.enterprise_generations += 1
            
            # Update performance metrics
            generation_time = generation_data.get("generation_time", 0)
            if generation_time > 0:
                # Moving average of generation time
                current_avg = self.performance_metrics.avg_generation_time
                total = self.revenue_metrics.total_generations
                self.performance_metrics.avg_generation_time = (
                    (current_avg * (total - 1) + generation_time) / total
                )
            
            # Update quality metrics
            quality_score = generation_data.get("quality_score", {}).get("overall", 85)
            innovation_score = generation_data.get("innovation_score", 0.5)
            
            current_quality = self.quality_metrics.avg_quality_score
            current_innovation = self.quality_metrics.avg_innovation_score
            total = self.revenue_metrics.total_generations
            
            self.quality_metrics.avg_quality_score = (
                (current_quality * (total - 1) + quality_score) / total
            )
            self.quality_metrics.avg_innovation_score = (
                (current_innovation * (total - 1) + innovation_score) / total
            )
            
            # Track content categories
            category = generation_data.get("category", "general")
            self.quality_metrics.content_categories[category] = (
                self.quality_metrics.content_categories.get(category, 0) + 1
            )
            
            # Track premium features usage
            premium_features = generation_data.get("premium_features_used", [])
            for feature in premium_features:
                self.quality_metrics.premium_features_usage[feature] = (
                    self.quality_metrics.premium_features_usage.get(feature, 0) + 1
                )
            
            # Broadcast updated metrics
            await self.broadcast_metrics({
                "revenue": asdict(self.revenue_metrics),
                "performance": asdict(self.performance_metrics),
                "quality": asdict(self.quality_metrics)
            })
            
            logger.info(f"📈 Recorded generation: ${generation_value:.2f} value, {quality_score:.1f} quality")
            
        except Exception as e:
            logger.error(f"Failed to record generation: {e}")
    
    def _calculate_generation_value(self, generation_data: Dict) -> float:
        """Calculate the revenue value of a generation"""
        base_value = 0.50  # Base generation value
        
        # Tier multipliers
        tier_multipliers = {
            "free": 0.0,
            "standard": 1.0,
            "premium": 2.5,
            "enterprise": 5.0
        }
        
        tier = generation_data.get("tier", "standard")
        tier_multiplier = tier_multipliers.get(tier, 1.0)
        
        # Complexity bonus
        complexity_score = generation_data.get("complexity_score", 0.5)
        complexity_bonus = complexity_score * 0.25
        
        # Innovation bonus
        innovation_score = generation_data.get("innovation_score", 0.0)
        innovation_bonus = innovation_score * 0.30
        
        # Word count factor
        word_count = generation_data.get("word_count", 500)
        word_factor = min(word_count / 1000, 2.0) * 0.20
        
        total_value = base_value * tier_multiplier + complexity_bonus + innovation_bonus + word_factor
        return round(total_value, 2)
    
    async def _collect_metrics(self):
        """Background task to collect system metrics"""
        while True:
            try:
                # Simulate collecting system metrics
                # In production, integrate with actual monitoring tools
                import psutil
                
                self.performance_metrics.memory_usage_mb = psutil.virtual_memory().used / 1024 / 1024
                self.performance_metrics.cpu_usage_percent = psutil.cpu_percent()
                
                # Calculate success rate (placeholder)
                total_gens = self.revenue_metrics.total_generations
                if total_gens > 0:
                    # Simulate 98% success rate
                    self.performance_metrics.success_rate = 98.0
                
                # Update MRR estimate
                if self.revenue_metrics.total_revenue > 0:
                    daily_revenue = self.revenue_metrics.total_revenue  # Today's revenue
                    self.revenue_metrics.monthly_recurring_revenue = daily_revenue * 30
                
                # Store metrics history
                current_metrics = {
                    "timestamp": datetime.now().isoformat(),
                    "revenue": asdict(self.revenue_metrics),
                    "performance": asdict(self.performance_metrics),
                    "quality": asdict(self.quality_metrics)
                }
                
                self.metrics_history.append(current_metrics)
                
                # Keep only last 24 hours of metrics
                cutoff = datetime.now() - timedelta(hours=24)
                self.metrics_history = [
                    m for m in self.metrics_history 
                    if datetime.fromisoformat(m["timestamp"]) > cutoff
                ]
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)

# FastAPI app for monitoring service
app = FastAPI(
    title="Enterprise Monitoring & Analytics",
    description="Real-time business intelligence for content generation platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global monitoring service
monitoring_service = EnterpriseMonitoringService()

@app.get("/")
async def monitoring_dashboard():
    """Enterprise monitoring dashboard"""
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Enterprise Monitoring Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric-value { font-size: 2em; font-weight: bold; color: #2563eb; }
        .metric-label { color: #6b7280; font-size: 0.9em; }
        .revenue { color: #059669; }
        .performance { color: #dc2626; }
        .quality { color: #7c3aed; }
        h1 { color: #1f2937; text-align: center; }
        .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
        .online { background: #10b981; }
        .offline { background: #ef4444; }
    </style>
</head>
<body>
    <h1>🏢 Enterprise Content Generation Platform</h1>
    <p style="text-align: center;">
        <span class="status-indicator online"></span>
        Real-time Monitoring & Analytics Dashboard
    </p>
    
    <div class="dashboard">
        <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value revenue" id="total-revenue">$0.00</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-label">Monthly Recurring Revenue</div>
            <div class="metric-value revenue" id="mrr">$0.00</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-label">Total Generations</div>
            <div class="metric-value" id="total-generations">0</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-label">Success Rate</div>
            <div class="metric-value performance" id="success-rate">100%</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-label">Avg Quality Score</div>
            <div class="metric-value quality" id="quality-score">85.0</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-label">Avg Generation Time</div>
            <div class="metric-value performance" id="gen-time">0.0s</div>
        </div>
    </div>
    
    <script>
        const ws = new WebSocket('ws://localhost:8002/ws');
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            if (data.type === 'initial_metrics' || data.type === 'metrics_update') {
                const metrics = data.type === 'initial_metrics' ? data : data.data;
                
                document.getElementById('total-revenue').textContent = 
                    '$' + (metrics.revenue?.total_revenue || 0).toFixed(2);
                document.getElementById('mrr').textContent = 
                    '$' + (metrics.revenue?.monthly_recurring_revenue || 0).toFixed(2);
                document.getElementById('total-generations').textContent = 
                    metrics.revenue?.total_generations || 0;
                document.getElementById('success-rate').textContent = 
                    (metrics.performance?.success_rate || 100).toFixed(1) + '%';
                document.getElementById('quality-score').textContent = 
                    (metrics.quality?.avg_quality_score || 85).toFixed(1);
                document.getElementById('gen-time').textContent = 
                    (metrics.performance?.avg_generation_time || 0).toFixed(1) + 's';
            }
        };
        
        ws.onopen = function() {
            console.log('Connected to monitoring service');
        };
        
        ws.onclose = function() {
            console.log('Disconnected from monitoring service');
            setTimeout(() => location.reload(), 5000);
        };
    </script>
</body>
</html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics"""
    await monitoring_service.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        monitoring_service.disconnect(websocket)

@app.post("/api/record-generation")
async def record_generation(generation_data: Dict[str, Any]):
    """Record a generation for analytics"""
    await monitoring_service.record_generation(generation_data)
    final_state = None  # inserted for safety
    if final_state:
        if final_state:
            return {**final_state, "success": True, "message": "Generation recorded"}
        else:
            return {"error": "final_state undefined", "status": "failed"}
    else:
        return {"error": "final_state undefined", "status": "failed"}

@app.get("/api/metrics")
async def get_metrics():
    """Get current metrics"""
    return {
        "revenue": asdict(monitoring_service.revenue_metrics),
        "performance": asdict(monitoring_service.performance_metrics),
        "quality": asdict(monitoring_service.quality_metrics),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/metrics/history")
async def get_metrics_history():
    """Get historical metrics"""
    return {
        "history": monitoring_service.metrics_history[-100:],  # Last 100 data points
        "total_points": len(monitoring_service.metrics_history)
    }

@app.get("/health")
async def health_check():
    """Health check for monitoring service"""
    return {
        "status": "healthy",
        "service": "enterprise_monitoring",
        "active_connections": len(monitoring_service.active_connections),
        "metrics_collected": len(monitoring_service.metrics_history),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "monitoring_server:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )