#!/usr/bin/env python3
"""
Test script to verify the unified structure works correctly
"""

import requests
import json
import sys
from datetime import datetime

def test_server_endpoints():
    """Test all server endpoints with the new unified structure"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Unified Structure Implementation")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed")
            print(f"   Templates loaded: {health_data.get('metrics', {}).get('templates_loaded', 'unknown')}")
            print(f"   Profiles loaded: {health_data.get('metrics', {}).get('profiles_loaded', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Debug file structures
    print("\n2. Testing file structure parsing...")
    try:
        response = requests.get(f"{base_url}/debug/file-structures", timeout=10)
        if response.status_code == 200:
            debug_data = response.json()
            if debug_data.get('success'):
                data = debug_data.get('data', {})
                results = data.get('parsing_results', {})
                
                print(f"✅ File structure debug successful")
                print(f"   Templates loaded: {results.get('templates_loaded', 0)}")
                print(f"   Templates failed: {results.get('templates_failed', 0)}")
                print(f"   Profiles loaded: {results.get('profiles_loaded', 0)}")
                print(f"   Profiles failed: {results.get('profiles_failed', 0)}")
                
                # Show details of parsed files
                if data.get('templates'):
                    print(f"\n   📄 Template parsing details:")
                    for template in data['templates'][:3]:  # Show first 3
                        status = "✅" if template['status'] == 'parsed_successfully' else "❌"
                        print(f"   {status} {template['filename']}: {template.get('name', 'unnamed')}")
                
                if data.get('style_profiles'):
                    print(f"\n   🎨 Style profile parsing details:")
                    for profile in data['style_profiles'][:3]:  # Show first 3
                        status = "✅" if profile['status'] == 'parsed_successfully' else "❌"
                        print(f"   {status} {profile['filename']}: {profile.get('name', 'unnamed')}")
            else:
                print(f"❌ File structure debug failed: {debug_data}")
        else:
            print(f"❌ File structure debug error: {response.status_code}")
    except Exception as e:
        print(f"❌ File structure debug error: {e}")
    
    # Test 3: Templates endpoint
    print("\n3. Testing templates endpoint...")
    try:
        response = requests.get(f"{base_url}/api/templates", timeout=10)
        if response.status_code == 200:
            templates_data = response.json()
            if templates_data.get('success'):
                templates = templates_data.get('data', {}).get('items', [])
                print(f"✅ Templates endpoint successful")
                print(f"   Found {len(templates)} templates")
                
                # Check for blog_post template
                blog_template = next((t for t in templates if t['id'] == 'blog_post'), None)
                if blog_template:
                    print(f"   ✅ blog_post template found: {blog_template['name']}")
                    params = blog_template.get('parameters', {})
                    print(f"   📋 Parameters: {list(params.keys())}")
                else:
                    print(f"   ❌ blog_post template not found")
                    print(f"   Available: {[t['id'] for t in templates]}")
            else:
                print(f"❌ Templates endpoint failed: {templates_data}")
        else:
            print(f"❌ Templates endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Templates endpoint error: {e}")
    
    # Test 4: Style profiles endpoint
    print("\n4. Testing style-profiles endpoint...")
    try:
        response = requests.get(f"{base_url}/api/style-profiles", timeout=10)
        if response.status_code == 200:
            profiles_data = response.json()
            if profiles_data.get('success'):
                profiles = profiles_data.get('data', {}).get('items', [])
                print(f"✅ Style profiles endpoint successful")
                print(f"   Found {len(profiles)} profiles")
                
                # Check for beginner_friendly profile
                beginner_profile = next((p for p in profiles if p['id'] == 'beginner_friendly'), None)
                if beginner_profile:
                    print(f"   ✅ beginner_friendly profile found: {beginner_profile['name']}")
                    print(f"   🎨 Tone: {beginner_profile.get('tone', 'not specified')}")
                    print(f"   🎯 Audience: {beginner_profile.get('audience', 'not specified')}")
                else:
                    print(f"   ❌ beginner_friendly profile not found")
                    print(f"   Available: {[p['id'] for p in profiles]}")
            else:
                print(f"❌ Style profiles endpoint failed: {profiles_data}")
        else:
            print(f"❌ Style profiles endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Style profiles endpoint error: {e}")
    
    # Test 5: Generation endpoint
    print("\n5. Testing generation endpoint...")
    try:
        generate_payload = {
            "template": "blog_post",
            "style_profile": "beginner_friendly",
            "dynamic_parameters": {
                "topic": "Testing Unified Structure",
                "audience": "developers",
                "tone": "conversational"
            }
        }
        
        response = requests.post(
            f"{base_url}/api/generate",
            json=generate_payload,
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ Generation request successful!")
                request_id = result.get('data', {}).get('request_id')
                print(f"   📋 Request ID: {request_id}")
                
                # Check the status
                if request_id:
                    print("   🔄 Checking generation status...")
                    status_response = requests.get(f"{base_url}/api/generate/{request_id}", timeout=10)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data.get('success'):
                            status_info = status_data.get('data', {})
                            print(f"   📊 Status: {status_info.get('status', 'unknown')}")
                            print(f"   📈 Progress: {status_info.get('progress', 0) * 100:.1f}%")
                        else:
                            print(f"   ❌ Status check failed: {status_data}")
                    else:
                        print(f"   ❌ Status check error: {status_response.status_code}")
            else:
                print(f"   ❌ Generation failed: {result}")
        else:
            print(f"   ❌ Generation error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw error: {response.text}")
                
    except Exception as e:
        print(f"❌ Generation test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary")
    print("If all tests show ✅, your unified structure is working!")
    print("If you see ❌, check the server logs and file structures")
    
    return True

def verify_file_structures():
    """Verify the file structures are correctly formatted"""
    print("\n🔍 Verifying Local File Structures")
    print("=" * 50)
    
    import yaml
    import os
    from pathlib import Path
    
    # Check template files
    template_dirs = ["data/content_templates", "frontend/content-templates"]
    print("\n📄 Checking template files...")
    
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            print(f"\n📁 {template_dir}/")
            for filename in os.listdir(template_dir):
                if filename.endswith('.yaml'):
                    file_path = os.path.join(template_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            data = yaml.safe_load(f)
                        
                        # Check unified structure
                        has_id = 'id' in data
                        has_name = 'name' in data
                        has_params = 'parameters' in data
                        params_is_list = isinstance(data.get('parameters'), list)
                        
                        status = "✅" if has_id and has_name else "⚠️"
                        param_status = "✅" if has_params and params_is_list else "⚠️"
                        
                        print(f"   {status} {filename}: id={has_id}, name={has_name}")
                        print(f"   {param_status}   parameters: exists={has_params}, is_list={params_is_list}")
                        
                    except Exception as e:
                        print(f"   ❌ {filename}: Error - {e}")
    
    # Check style profile files
    style_dirs = ["data/style_profiles", "style_profiles", "frontend/style-profiles"]
    print("\n🎨 Checking style profile files...")
    
    for style_dir in style_dirs:
        if os.path.exists(style_dir):
            print(f"\n📁 {style_dir}/")
            for filename in os.listdir(style_dir):
                if filename.endswith('.yaml'):
                    file_path = os.path.join(style_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            data = yaml.safe_load(f)
                        
                        # Check unified structure
                        has_id = 'id' in data
                        has_name = 'name' in data
                        has_system_prompt = 'system_prompt' in data
                        has_settings = 'settings' in data
                        
                        status = "✅" if has_id and has_name else "⚠️"
                        
                        print(f"   {status} {filename}: id={has_id}, name={has_name}")
                        print(f"       system_prompt={has_system_prompt}, settings={has_settings}")
                        
                    except Exception as e:
                        print(f"   ❌ {filename}: Error - {e}")

if __name__ == "__main__":
    verify_file_structures()
    test_server_endpoints()
    
    print("\n💡 Next steps if tests fail:")
    print("1. Run the migration script: python migration_script.py")
    print("2. Update server.py with the new loader functions")
    print("3. Restart your FastAPI server")
    print("4. Run this test script again")