#!/bin/bash

echo "🚀 Starting your existing FastAPI server"
echo "========================================"

# Activate environment
echo "📦 Activating virtual environment..."
source writer/bin/activate

echo ""
echo "🔍 Checking required dependencies..."
pip list | grep -E "(fastapi|uvicorn|pydantic|structlog|prometheus)"

echo ""
echo "📥 Installing any missing dependencies..."
pip install fastapi uvicorn pydantic structlog prometheus-client pyyaml

echo ""
echo "🔍 Checking for enhanced_graph module..."
python -c "
try:
    from enhanced_graph import *
    print('✅ enhanced_graph module found')
except ImportError as e:
    print(f'⚠️  enhanced_graph module not found: {e}')
    print('This might cause server startup issues')
except Exception as e:
    print(f'❌ Error importing enhanced_graph: {e}')
"

echo ""
echo "🔍 Checking if server.py can be imported..."
python -c "
import sys
sys.path.append('langgraph_app')
try:
    import server
    print('✅ server.py can be imported')
except ImportError as e:
    print(f'❌ Cannot import server.py: {e}')
except Exception as e:
    print(f'⚠️  Error importing server.py: {e}')
"

echo ""
echo "🌐 Attempting to start server..."
echo "================================"
echo "If this fails, check the error message above for missing modules"
echo ""

# Try to start the server
python langgraph_app/server.py