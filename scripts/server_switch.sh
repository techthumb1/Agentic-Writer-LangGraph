#!/bin/bash

echo "🔄 Switching from integrated_server.py to server.py..."

# Check if we're in the right directory
if [ ! -f "langgraph_app/server.py" ]; then
    echo "❌ Error: langgraph_app/server.py not found. Run this from the project root."
    exit 1
fi

if [ ! -f "langgraph_app/integrated_server.py" ]; then
    echo "❌ Error: langgraph_app/integrated_server.py not found."
    exit 1
fi

# Backup current integrated_server.py
echo "📦 Backing up current integrated_server.py..."
cp langgraph_app/integrated_server.py langgraph_app/integrated_server.py.backup

# Copy server.py to replace integrated_server.py
echo "📋 Copying server.py to integrated_server.py..."
cp langgraph_app/server.py langgraph_app/integrated_server.py

# Fix the import paths for relative imports
echo "🔧 Fixing import paths..."
sed -i.bak 's/from enhanced_graph import/from .enhanced_graph import/g' langgraph_app/integrated_server.py
sed -i.bak 's/from langgraph_app\.enhanced_model_registry import/from .enhanced_model_registry import/g' langgraph_app/integrated_server.py

# Remove the backup file created by sed
rm langgraph_app/integrated_server.py.bak

# Verify the directories exist
echo "📁 Checking required directories..."
if [ -d "data/content_templates" ]; then
    template_count=$(ls data/content_templates/*.yaml 2>/dev/null | wc -l)
    echo "✅ Templates directory found: $template_count templates"
else
    echo "⚠️  Warning: data/content_templates not found"
fi

if [ -d "data/style_profiles" ]; then
    profile_count=$(ls data/style_profiles/*.yaml 2>/dev/null | wc -l)
    echo "✅ Style profiles directory found: $profile_count profiles"
else
    echo "⚠️  Warning: data/style_profiles not found"
fi

echo ""
echo "✅ Switch complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Stop your current backend server (Ctrl+C)"
echo "2. Restart with: cd langgraph_app && python -m uvicorn integrated_server:app --reload --port 8000"
echo "3. Test with: curl http://localhost:8000/health"
echo ""
echo "📊 Your files:"
echo "- Templates: $template_count files in data/content_templates/"
echo "- Profiles: $profile_count files in data/style_profiles/"
echo "- Backup: langgraph_app/integrated_server.py.backup"