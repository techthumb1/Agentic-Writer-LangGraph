#!/bin/bash

echo "🔍 Checking your existing server.py"
echo "==================================="

echo "📄 First 30 lines of langgraph_app/server.py:"
head -30 langgraph_app/server.py

echo ""
echo "🔍 Looking for FastAPI app initialization:"
grep -n "app.*=.*FastAPI\|FastAPI()" langgraph_app/server.py

echo ""
echo "🔍 Looking for uvicorn run command:"
grep -n "uvicorn\|app.run\|if __name__" langgraph_app/server.py

echo ""
echo "🔍 Looking for port configuration:"
grep -n "port.*=\|:8000\|PORT" langgraph_app/server.py

echo ""
echo "📊 File size and structure:"
wc -l langgraph_app/server.py
echo ""
echo "Functions and classes found:"
grep -n "^def \|^class \|^async def " langgraph_app/server.py | head -10

echo ""
echo "💡 How to start your existing server:"
echo "1. Try: python langgraph_app/server.py"
echo "2. Try: uvicorn langgraph_app.server:app --host 0.0.0.0 --port 8000 --reload"
echo "3. Check if there's a specific run command in the file"