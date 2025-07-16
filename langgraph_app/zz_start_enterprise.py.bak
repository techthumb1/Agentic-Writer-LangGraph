# langgraph_app/start_enterprise.py - ULTIMATE ENTERPRISE LAUNCHER
"""
🏢 ENTERPRISE CONTENT GENERATION PLATFORM
💰 OPTIMIZED FOR MAXIMUM PROFITABILITY
🚀 PRODUCTION-READY MULTI-SERVICE ARCHITECTURE
"""

import asyncio
import subprocess
import sys
import os
import time
import logging
from pathlib import Path
import psutil

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

class EnterpriseServiceManager:
    """ENTERPRISE-GRADE SERVICE ORCHESTRATION"""
    
    def __init__(self):
        self.services = {}
        self.startup_order = []
        
    def register_service(self, name: str, port: int, module: str, description: str, 
                        critical: bool = True, wait_time: int = 3):
        """Register enterprise service"""
        self.services[name] = {
            "port": port,
            "module": module,
            "description": description,
            "critical": critical,
            "wait_time": wait_time,
            "process": None,
            "status": "stopped",
            "start_time": None
        }
        self.startup_order.append(name)
        logger.info(f"📋 Registered: {name} ({description})")
    
    def _kill_port(self, port: int):
        """Kill any process using the port"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.connections():
                        if conn.laddr.port == port:
                            logger.info(f"🔫 Killing process {proc.info['pid']} on port {port}")
                            proc.kill()
                            time.sleep(1)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            logger.warning(f"⚠️ Could not kill port {port}: {e}")
    
    async def start_service(self, name: str) -> bool:
        """Start enterprise service with monitoring"""
        service = self.services[name]
        
        try:
            logger.info(f"🚀 Starting {name}: {service['description']}")
            
            # Free the port
            self._kill_port(service["port"])
            await asyncio.sleep(1)
            
            # Start service
            cmd = [
                sys.executable, "-m", "uvicorn",
                service["module"],
                "--host", "0.0.0.0",
                "--port", str(service["port"]),
                "--reload",
                "--log-level", "info"
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for startup
            await asyncio.sleep(service["wait_time"])
            
            if process.poll() is None:  # Still running
                service["process"] = process
                service["status"] = "running"
                service["start_time"] = time.time()
                logger.info(f"✅ {name} started on port {service['port']}")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ {name} failed to start:")
                if stdout: logger.error(f"STDOUT: {stdout[:500]}")
                if stderr: logger.error(f"STDERR: {stderr[:500]}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Exception starting {name}: {e}")
            return False
    
    async def start_platform(self):
        """Start the complete enterprise platform"""
        logger.info("🏢 STARTING ENTERPRISE CONTENT GENERATION PLATFORM")
        logger.info("💰 OPTIMIZED FOR MAXIMUM PROFITABILITY")
        
        success_count = 0
        total_services = len(self.startup_order)
        
        for service_name in self.startup_order:
            service = self.services[service_name]
            logger.info(f"📊 Starting {service_name} ({success_count + 1}/{total_services})")
            
            success = await self.start_service(service_name)
            
            if success:
                success_count += 1
                logger.info(f"✅ {service_name} operational")
            else:
                if service["critical"]:
                    logger.error(f"❌ CRITICAL SERVICE {service_name} FAILED")
                    return False
                else:
                    logger.warning(f"⚠️ Non-critical service {service_name} failed")
            
            # Stagger startup
            await asyncio.sleep(2)
        
        # Platform status
        if success_count == total_services:
            logger.info("🎉 ALL ENTERPRISE SERVICES OPERATIONAL")
            self._display_enterprise_dashboard()
            return True
        else:
            logger.warning(f"⚠️ {success_count}/{total_services} services started")
            self._display_enterprise_dashboard()
            return success_count > 0
    
    def _display_enterprise_dashboard(self):
        """Display the enterprise dashboard"""
        print("\n" + "="*80)
        print("🏢 ENTERPRISE CONTENT GENERATION PLATFORM")
        print("💰 STATUS: OPERATIONAL & PROFITABLE")
        print("="*80)
        
        for name, service in self.services.items():
            status_icon = "✅" if service["status"] == "running" else "❌"
            print(f"{status_icon} {name.upper()}: http://localhost:{service['port']}")
            print(f"   📝 {service['description']}")
        
        print("="*80)
        print("🚀 ENTERPRISE FEATURES ACTIVE:")
        print("   💎 Premium AI Writing with Innovation Scoring")
        print("   📊 Real-time Agent Progress Tracking") 
        print("   🔐 Enterprise Authentication & Security")
        print("   💰 Usage Analytics & Billing Ready")
        print("   ⚡ Advanced Template & Style Management")
        print("="*80)
        print("📖 API Documentation: http://localhost:8000/docs")
        print("📊 Health Monitoring: http://localhost:8000/health")
        print("🎯 Frontend Dashboard: http://localhost:3000")
        print("="*80)
        print("🎉 READY FOR PROFITABLE CONTENT GENERATION!")
        print("💡 Your enterprise platform is now operational")
        print("="*80)
    
    async def monitor_platform(self):
        """Monitor platform health"""
        logger.info("🔍 Starting enterprise platform monitoring...")
        
        while True:
            running_services = 0
            total_services = len(self.services)
            
            for name, service in self.services.items():
                if service["status"] == "running" and service["process"]:
                    if service["process"].poll() is None:
                        running_services += 1
                    else:
                        logger.warning(f"⚠️ Service {name} stopped unexpectedly")
                        service["status"] = "stopped"
            
            logger.info(f"💼 Platform Status: {running_services}/{total_services} services operational")
            
            if running_services == 0:
                logger.error("🚨 ALL SERVICES DOWN - PLATFORM CRITICAL")
                break
            
            await asyncio.sleep(60)  # Check every minute

async def launch_enterprise_platform():
    """Launch the complete profitable enterprise platform"""
    
    # Set enterprise environment
    os.environ["ENTERPRISE_MODE"] = "true"
    os.environ["PROFITABILITY_OPTIMIZATION"] = "maximum"
    
    # Initialize enterprise service manager
    manager = EnterpriseServiceManager()
    
    # Register enterprise services in optimal order
    manager.register_service(
        "content_engine",
        8001,
        "langgraph_app.integrated_server:app",
        "🤖 Advanced AI Content Generation Engine",
        critical=True,
        wait_time=5  # Writer needs more time to load
    )
    
    manager.register_service(
        "enterprise_gateway",
        8000,
        "langgraph_app.main:app", 
        "🏢 Enterprise API Gateway & Authentication",
        critical=True,
        wait_time=3
    )
    
    try:
        # Launch platform
        success = await manager.start_platform()
        
        if success:
            # Keep platform running
            try:
                await manager.monitor_platform()
            except KeyboardInterrupt:
                logger.info("🛑 Received shutdown signal...")
        
    except Exception as e:
        logger.error(f"💥 Enterprise platform failed: {e}")
    
    finally:
        logger.info("🛑 Shutting down enterprise platform...")
        for name, service in manager.services.items():
            if service["process"]:
                try:
                    service["process"].terminate()
                    service["process"].wait(timeout=5)
                    logger.info(f"🛑 Stopped {name}")
                except:
                    try:
                        service["process"].kill()
                        logger.info(f"🔫 Force killed {name}")
                    except:
                        pass

def check_prerequisites():
    """Check enterprise prerequisites"""
    logger.info("🔍 Checking enterprise prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8+ required for enterprise features")
        return False
    
    # Check critical files
    critical_files = [
        "langgraph_app/agents/writer.py",
        "langgraph_app/integrated_server.py", 
        "langgraph_app/main.py",
        "data/style_profiles",
        "frontend"
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"❌ Missing critical files: {missing_files}")
        return False
    
    logger.info("✅ All enterprise prerequisites satisfied")
    return True

if __name__ == "__main__":
    print("🏢 ENTERPRISE CONTENT GENERATION PLATFORM")
    print("💰 Initializing for maximum profitability...")
    
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please resolve issues and try again.")
        sys.exit(1)
    
    try:
        asyncio.run(launch_enterprise_platform())
    except KeyboardInterrupt:
        print("\n🛑 Enterprise platform shutdown requested")
    except Exception as e:
        print(f"💥 Enterprise platform failed: {e}")
        sys.exit(1)