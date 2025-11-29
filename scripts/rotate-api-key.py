#!/usr/bin/env python3
import secrets
import os
from pathlib import Path

def generate_new_api_key():
    return secrets.token_urlsafe(32)

def update_env_file(file_path, key_name, new_key):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        updated = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key_name}="):
                lines[i] = f"{key_name}={new_key}\n"
                updated = True
                break
        
        if not updated:
            lines.append(f"{key_name}={new_key}\n")
        
        with open(file_path, 'w') as f:
            f.writelines(lines)
    else:
        with open(file_path, 'w') as f:
            f.write(f"{key_name}={new_key}\n")

if __name__ == "__main__":
    new_key = generate_new_api_key()
    print(f"Generated new API key: {new_key}")
    
    # Update backend .env
    update_env_file(".env", "LANGGRAPH_API_KEY", new_key)
    
    # Update frontend .env.local
    update_env_file("frontend/.env.local", "FASTAPI_API_KEY", new_key)
    
    print("Updated both backend and frontend environment files")
    print("Please restart both servers")