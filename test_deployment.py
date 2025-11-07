#!/usr/bin/env python3
# test_deployment.py - Validate production deployment

import os
import sys
import requests
import psycopg2
import redis
from typing import Dict, List, Tuple

class DeploymentTester:
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip('/')
        self.results: List[Tuple[str, bool, str]] = []
    
    def test_health_endpoint(self) -> bool:
        """Test basic health check"""
        try:
            resp = requests.get(f"{self.api_url}/health", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("status") == "healthy"
            return False
        except Exception as e:
            self.results.append(("Health Check", False, str(e)))
            return False
    
    def test_database_connection(self) -> bool:
        """Test database connectivity"""
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            conn.close()
            return True
        except Exception as e:
            self.results.append(("Database", False, str(e)))
            return False
    
    def test_redis_connection(self) -> bool:
        """Test Redis connectivity"""
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            self.results.append(("Redis", True, "Not configured (optional)"))
            return True
        
        try:
            r = redis.from_url(redis_url)
            r.ping()
            return True
        except Exception as e:
            self.results.append(("Redis", False, str(e)))
            return False
    
    def test_template_endpoints(self) -> bool:
        """Test template listing"""
        try:
            resp = requests.get(f"{self.api_url}/api/templates", timeout=10)
            if resp.status_code == 200:
                templates = resp.json()
                return len(templates) > 0
            return False
        except Exception as e:
            self.results.append(("Templates API", False, str(e)))
            return False
    
    def test_style_profiles(self) -> bool:
        """Test style profile listing"""
        try:
            resp = requests.get(f"{self.api_url}/api/style-profiles", timeout=10)
            if resp.status_code == 200:
                profiles = resp.json()
                return len(profiles) > 0
            return False
        except Exception as e:
            self.results.append(("Style Profiles API", False, str(e)))
            return False
    
    def test_cors(self) -> bool:
        """Test CORS headers"""
        try:
            resp = requests.options(
                f"{self.api_url}/health",
                headers={"Origin": "https://example.com"}
            )
            return "access-control-allow-origin" in resp.headers
        except Exception as e:
            self.results.append(("CORS", False, str(e)))
            return False
    
    def run_all_tests(self) -> Dict[str, any]:
        """Run all deployment tests"""
        print("🧪 Running Deployment Tests")
        print("=" * 50)
        
        tests = [
            ("Health Endpoint", self.test_health_endpoint),
            ("Database Connection", self.test_database_connection),
            ("Redis Connection", self.test_redis_connection),
            ("Templates API", self.test_template_endpoints),
            ("Style Profiles API", self.test_style_profiles),
            ("CORS Configuration", self.test_cors),
        ]
        
        passed = 0
        failed = 0
        
        for name, test_func in tests:
            try:
                result = test_func()
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} - {name}")
                
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL - {name}: {e}")
                failed += 1
        
        print("\n" + "=" * 50)
        print(f"Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("✅ All tests passed! Deployment is healthy.")
            return {"status": "success", "passed": passed, "failed": failed}
        else:
            print("❌ Some tests failed. Check logs above.")
            return {"status": "failed", "passed": passed, "failed": failed}

if __name__ == "__main__":
    api_url = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:8000")
    
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    
    print(f"Testing deployment at: {api_url}\n")
    
    tester = DeploymentTester(api_url)
    results = tester.run_all_tests()
    
    sys.exit(0 if results["status"] == "success" else 1)