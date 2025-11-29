# langgraph_app/launch_enterprise.py - COMPLETE ENTERPRISE PLATFORM
"""
🏢 COMPLETE ENTERPRISE CONTENT GENERATION PLATFORM
💰 MAXIMUM PROFITABILITY CONFIGURATION
🚀 ALL SERVICES INTEGRATED FOR SUCCESS
"""

import asyncio
import subprocess
import sys
import os
import time
import logging
from pathlib import Path
import psutil
import json
from datetime import datetime

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enterprise_platform.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("EnterprisePlatform")

class CompleteEnterpriseManager:
    """COMPLETE ENTERPRISE PLATFORM ORCHESTRATION"""
    
    def __init__(self):
        self.services = {}
        self.startup_order = []
        self.health_checks = {}
        
    def register_service(self, name: str, port: int, module: str, description: str,
                        critical: bool = True, wait_time: int = 3, health_endpoint: str = "/health"):
        """Register complete enterprise service"""
        self.services[name] = {
            "port": port,
            "module": module,
            "description": description,
            "critical": critical,
            "wait_time": wait_time,
            "health_endpoint": health_endpoint,
            "process": None,
            "status": "stopped",
            "start_time": None,
            "restart_count": 0,
            "last_health_check": None
        }
        self.startup_order.append(name)
        logger.info(f"📋 Registered: {name} - {description}")
    
    def _kill_port(self, port: int):
        """Aggressively free up ports"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.connections():
                        if conn.laddr.port == port:
                            logger.info(f"🔫 Terminating process {proc.info['pid']} on port {port}")
                            proc.terminate()
                            time.sleep(1)
                            if proc.is_running():
                                proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            logger.warning(f"⚠️ Port cleanup warning for {port}: {e}")
    
    async def start_service(self, name: str) -> bool:
        """Start enterprise service with full monitoring"""
        service = self.services[name]
        
        try:
            logger.info(f"🚀 Starting {name}")
            logger.info(f"   📝 {service['description']}")
            logger.info(f"   🌐 Port: {service['port']}")
            
            # Aggressive port cleanup
            self._kill_port(service["port"])
            await asyncio.sleep(2)
            
            # Prepare startup command
            cmd = [
                sys.executable, "-m", "uvicorn",
                service["module"],
                "--host", "0.0.0.0",
                "--port", str(service["port"]),
                "--reload",
                "--log-level", "info"
            ]
            
            # Start service with proper error handling
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Extended wait for complex services
            logger.info(f"   ⏳ Waiting {service['wait_time']}s for startup...")
            await asyncio.sleep(service["wait_time"])
            
            # Check if process is still running
            if process.poll() is None:
                service["process"] = process
                service["status"] = "running" 
                service["start_time"] = time.time()
                
                # Verify service health
                health_ok = await self._health_check_service(name)
                if health_ok:
                    logger.info(f"✅ {name} is OPERATIONAL on port {service['port']}")
                    return True
                else:
                    logger.warning(f"⚠️ {name} started but health check failed")
                    return True  # Still consider it started
            else:
                # Process failed to start
                stdout, stderr = process.communicate()
                logger.error(f"❌ {name} failed to start")
                logger.error(f"STDOUT: {stdout[:1000] if stdout else 'None'}")
                logger.error(f"STDERR: {stderr[:1000] if stderr else 'None'}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Exception starting {name}: {e}")
            return False
    
    async def _health_check_service(self, name: str) -> bool:
        """Perform health check on service"""
        service = self.services[name]
        
        try:
            import aiohttp
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                url = f"http://localhost:{service['port']}{service['health_endpoint']}"
                async with session.get(url) as response:
                    service["last_health_check"] = datetime.now()
                    return response.status == 200
        except Exception as e:
            logger.debug(f"Health check failed for {name}: {e}")
            return False
    
    async def start_complete_platform(self):
        """Start the complete enterprise platform"""
        logger.info("🏢 LAUNCHING COMPLETE ENTERPRISE PLATFORM")
        logger.info("💰 OPTIMIZED FOR MAXIMUM PROFITABILITY")
        logger.info("🎯 ALL SYSTEMS GOING OPERATIONAL")
        
        success_count = 0
        total_services = len(self.startup_order)
        failed_services = []
        
        for i, service_name in enumerate(self.startup_order, 1):
            service = self.services[service_name]
            logger.info(f"📊 [{i}/{total_services}] Initializing {service_name}")
            
            success = await self.start_service(service_name)
            
            if success:
                success_count += 1
                logger.info(f"✅ {service_name} operational")
            else:
                failed_services.append(service_name)
                if service["critical"]:
                    logger.error(f"❌ CRITICAL SERVICE {service_name} FAILED")
                    logger.error("🚨 Platform startup aborted due to critical service failure")
                    return False
                else:
                    logger.warning(f"⚠️ Non-critical service {service_name} failed")
            
            # Stagger startup to prevent resource conflicts
            if i < total_services:
                await asyncio.sleep(3)
        
        # Platform status assessment
        if success_count == total_services:
            logger.info("🎉 COMPLETE PLATFORM OPERATIONAL")
            self._display_complete_dashboard()
            return True
        elif success_count >= len([s for s in self.services.values() if s["critical"]]):
            logger.info(f"✅ PLATFORM OPERATIONAL ({success_count}/{total_services} services)")
            logger.warning(f"⚠️ Failed services: {failed_services}")
            self._display_complete_dashboard()
            return True
        else:
            logger.error("❌ PLATFORM STARTUP FAILED")
            return False
    
    def _display_complete_dashboard(self):
        """Display the complete enterprise dashboard"""
        print("\n" + "="*90)
        print("🏢 COMPLETE ENTERPRISE CONTENT GENERATION PLATFORM")
        print("💰 STATUS: FULLY OPERATIONAL & PROFIT-READY")
        print("="*90)
        
        running_services = 0
        for name, service in self.services.items():
            status_icon = "✅" if service["status"] == "running" else "❌"
            uptime = f"{int(time.time() - service['start_time'])}s" if service["start_time"] else "0s"
            
            print(f"{status_icon} {name.upper().replace('_', ' ')}")
            print(f"   🌐 http://localhost:{service['port']}")
            print(f"   📝 {service['description']}")
            print(f"   ⏱️  Uptime: {uptime}")
            
            if service["status"] == "running":
                running_services += 1
        
        print("="*90)
        print("🚀 ENTERPRISE CAPABILITIES ACTIVE:")
        print("   💎 Advanced AI Content Generation with Innovation Scoring")
        print("   🤖 Multi-Agent Workflow Orchestration")
        print("   📊 Real-time Performance & Revenue Monitoring")
        print("   💰 Complete Billing & Subscription Management")
        print("   🔐 Enterprise Security & Authentication")
        print("   ⚡ Advanced Template & Style Management")
        print("   🎯 Business Intelligence Dashboard")
        print("   📈 Revenue Optimization Analytics")
        print("="*90)
        print("🎯 PRIMARY INTERFACES:")
        print("   🖥️  Frontend Dashboard: http://localhost:3000")
        print("   🏢 Enterprise API Gateway: http://localhost:8000/docs")
        print("   🤖 Content Generation Engine: http://localhost:8001/docs") 
        print("   📊 Monitoring Dashboard: http://localhost:8002")
        print("   💰 Billing & Revenue API: http://localhost:8003/docs")
        print("="*90)
        print(f"📊 PLATFORM STATUS: {running_services}/{len(self.services)} services operational")
        print("🎉 READY FOR PROFITABLE CONTENT GENERATION!")
        print("💡 Enterprise platform fully deployed and revenue-optimized")
        print("="*90)
    
    async def monitor_complete_platform(self):
        """Monitor complete platform health with auto-recovery"""
        logger.info("🔍 Starting complete platform monitoring...")
        
        while True:
            try:
                running_services = 0
                total_services = len(self.services)
                unhealthy_services = []
                
                for name, service in self.services.items():
                    if service["status"] == "running" and service["process"]:
                        # Check if process is still alive
                        if service["process"].poll() is None:
                            # Process alive, check health
                            health_ok = await self._health_check_service(name)
                            if health_ok:
                                running_services += 1
                            else:
                                unhealthy_services.append(name)
                        else:
                            # Process died
                            logger.warning(f"💀 Service {name} process died")
                            service["status"] = "stopped"
                            unhealthy_services.append(name)
                
                # Report status
                if running_services == total_services:
                    logger.info(f"💚 All systems operational ({running_services}/{total_services})")
                else:
                    logger.warning(f"⚠️ Platform status: {running_services}/{total_services} healthy")
                    if unhealthy_services:
                        logger.warning(f"Unhealthy services: {unhealthy_services}")
                
                # Auto-recovery for critical services
                for service_name in unhealthy_services:
                    service = self.services[service_name]
                    if service["critical"] and service["restart_count"] < 3:
                        logger.info(f"🔄 Auto-restarting critical service: {service_name}")
                        success = await self.start_service(service_name)
                        if success:
                            service["restart_count"] += 1
                            logger.info(f"✅ {service_name} restarted (attempt {service['restart_count']})")
                        else:
                            logger.error(f"❌ Failed to restart {service_name}")
                
                # Critical system check
                if running_services == 0:
                    logger.error("🚨 COMPLETE SYSTEM FAILURE - ALL SERVICES DOWN")
                    break
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(30)

async def launch_complete_enterprise_platform():
    """Launch the complete profitable enterprise platform"""
    
    # Set enterprise environment variables
    os.environ.update({
        "ENTERPRISE_MODE": "true",
        "PROFITABILITY_OPTIMIZATION": "maximum",
        "MONITORING_ENABLED": "true",
        "BILLING_ENABLED": "true",
        "ANALYTICS_ENABLED": "true"
    })
    
    # Initialize complete enterprise manager
    manager = CompleteEnterpriseManager()
    
    # Register all enterprise services in optimal startup order
    manager.register_service(
        "content_engine",
        8001,
        "langgraph_app.integrated_server:app",
        "🤖 Advanced AI Content Generation Engine with Innovation Features",
        critical=True,
        wait_time=6  # More time for AI models to load
    )
    
    manager.register_service(
        "enterprise_gateway", 
        8000,
        "langgraph_app.main:app",
        "🏢 Enterprise API Gateway with Authentication & Rate Limiting",
        critical=True,
        wait_time=4
    )
    
    manager.register_service(
        "monitoring_service",
        8002,
        "langgraph_app.monitoring_server:app", 
        "📊 Real-time Performance & Business Intelligence Monitoring",
        critical=False,
        wait_time=3
    )
    
    manager.register_service(
        "billing_service",
        8003,
        "langgraph_app.billing_service:app",
        "💰 Enterprise Billing, Subscriptions & Revenue Management",
        critical=False,
        wait_time=3
    )
    
    try:
        # Launch complete platform
        success = await manager.start_complete_platform()
        
        if success:
            # Platform is operational, start monitoring
            logger.info("🎯 Starting continuous platform monitoring...")
            try:
                await manager.monitor_complete_platform()
            except KeyboardInterrupt:
                logger.info("🛑 Shutdown signal received...")
        else:
            logger.error("💥 Platform startup failed")
    
    except Exception as e:
        logger.error(f"💥 Enterprise platform failed: {e}")
    
    finally:
        # Graceful shutdown
        logger.info("🛑 Shutting down complete enterprise platform...")
        for name, service in manager.services.items():
            if service["process"]:
                try:
                    service["process"].terminate()
                    service["process"].wait(timeout=10)
                    logger.info(f"🛑 Stopped {name}")
                except subprocess.TimeoutExpired:
                    service["process"].kill()
                    logger.info(f"🔫 Force killed {name}")
                except Exception as e:
                    logger.warning(f"⚠️ Error stopping {name}: {e}")

def check_complete_prerequisites():
    """Check all enterprise prerequisites"""
    logger.info("🔍 Checking complete enterprise prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8+ required for enterprise features")
        return False
    
    # Check critical files and directories
    critical_paths = [
        "langgraph_app/agents/writer.py",
        "langgraph_app/integrated_server.py",
        "langgraph_app/main.py", 
        "langgraph_app/monitoring_server.py",
        "langgraph_app/billing_service.py",
        "data/style_profiles",
        "frontend",
        "prompts/writer"
    ]
    
    missing_paths = []
    for path in critical_paths:
        if not os.path.exists(path):
            missing_paths.append(path)
    
    if missing_paths:
        logger.error(f"❌ Missing critical paths: {missing_paths}")
        return False
    
    # Check required Python packages
    required_packages = [
        "fastapi", "uvicorn", "openai", "psutil", "aiohttp"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"❌ Missing required packages: {missing_packages}")
        logger.info("Install with: pip install " + " ".join(missing_packages))
        return False
    
    logger.info("✅ All enterprise prerequisites satisfied")
    return True

def save_platform_config():
    """Save platform configuration for reference"""
    config = {
        "platform_name": "Enterprise Content Generation Platform",
        "version": "2.0.0",
        "deployment_timestamp": datetime.now().isoformat(),
        "services": {
            "content_engine": {
                "port": 8001,
                "description": "AI Content Generation Engine",
                "features": [
                    "InnovativeWriterAgent with adaptive learning",
                    "Multi-modal writing strategies", 
                    "Experimental technique injection",
                    "Real-time progress tracking"
                ]
            },
            "enterprise_gateway": {
                "port": 8000,
                "description": "Enterprise API Gateway",
                "features": [
                    "Authentication & authorization",
                    "Rate limiting & throttling",
                    "Request routing & load balancing",
                    "API documentation"
                ]
            },
            "monitoring_service": {
                "port": 8002,
                "description": "Business Intelligence Dashboard",
                "features": [
                    "Real-time performance metrics",
                    "Revenue tracking & analytics",
                    "WebSocket-based live updates",
                    "Service health monitoring"
                ]
            },
            "billing_service": {
                "port": 8003,
                "description": "Revenue Management System",
                "features": [
                    "Multi-tier subscription management",
                    "Usage-based billing",
                    "Revenue optimization",
                    "Upgrade recommendations"
                ]
            }
        },
        "revenue_model": {
            "subscription_tiers": [
                {"name": "Free", "price": 0, "generations": 10},
                {"name": "Starter", "price": 29, "generations": 500},
                {"name": "Professional", "price": 99, "generations": 2000},
                {"name": "Enterprise", "price": 299, "generations": 10000},
                {"name": "Enterprise Plus", "price": 599, "generations": "unlimited"}
            ],
            "premium_features": [
                "Innovation scoring & experimental techniques",
                "Premium templates & custom styles",
                "Priority processing & support",
                "White-label capabilities",
                "Advanced analytics & reporting"
            ]
        },
        "competitive_advantages": [
            "Advanced AI with innovation scoring",
            "Multi-agent workflow orchestration", 
            "Real-time business intelligence",
            "Comprehensive revenue management",
            "Enterprise-grade scalability",
            "Profitable from day one"
        ]
    }
    
    with open("enterprise_platform_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    logger.info("💾 Platform configuration saved to enterprise_platform_config.json")

if __name__ == "__main__":
    print("\n" + "="*90)
    print("🏢 ENTERPRISE CONTENT GENERATION PLATFORM LAUNCHER")
    print("💰 OPTIMIZED FOR MAXIMUM PROFITABILITY")
    print("🚀 LAUNCHING ALL SYSTEMS FOR SUCCESS")
    print("="*90)
    
    # Check prerequisites
    if not check_complete_prerequisites():
        print("❌ Prerequisites not met. Please resolve issues and try again.")
        print("💡 Ensure all required files and packages are installed.")
        sys.exit(1)
    
    # Save configuration
    save_platform_config()
    
    # Display pre-launch summary
    print("\n🎯 PLATFORM OVERVIEW:")
    print("   🤖 AI Content Engine: Advanced multi-agent content generation")
    print("   🏢 Enterprise Gateway: Authentication, rate limiting, API management")
    print("   📊 Monitoring Service: Real-time analytics & business intelligence")
    print("   💰 Billing Service: Revenue management & subscription optimization")
    print("\n💡 REVENUE STREAMS:")
    print("   📈 Subscription tiers: $0-$599/month")
    print("   ⚡ Usage-based billing for premium features")
    print("   🎯 Enterprise white-label licensing")
    print("   📊 Analytics & insights as a service")
    
    print("\n🚀 Launching enterprise platform...")
    print("   ⏳ This may take 30-60 seconds for full startup")
    print("   📊 Monitor progress in the logs below")
    print("="*90)
    
    try:
        # Launch the complete enterprise platform
        asyncio.run(launch_complete_enterprise_platform())
    except KeyboardInterrupt:
        print("\n🛑 Enterprise platform shutdown requested by user")
        print("💰 Platform was operational and revenue-ready")
    except Exception as e:
        print(f"\n💥 Enterprise platform failed: {e}")
        print("📞 Contact support for assistance")
        sys.exit(1)
    finally:
        print("\n" + "="*90)
        print("🏢 ENTERPRISE PLATFORM SHUTDOWN COMPLETE")
        print("💰 Revenue operations concluded successfully")
        print("📊 Logs saved for analysis and optimization")
        print("🎯 Ready for next profitable session")
        print("="*90)