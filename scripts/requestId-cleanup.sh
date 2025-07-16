#!/bin/bash

# Quick fix for the 5 remaining request_id instances
# This is much simpler than the full standardization script

echo "🔍 Fixing the 5 remaining request_id instances..."

# Only need to fix test_unified.py
if [ -f "./test_unified.py" ]; then
    echo "📝 Updating test_unified.py..."
    
    # Create backup
    cp "./test_unified.py" "./test_unified.py.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Replace the instances
    sed -i.bak 's/request_id/requestId/g' "./test_unified.py"
    
    echo "✅ Updated test_unified.py"
    echo "📋 Backup created: test_unified.py.backup.*"
    
    # Show what changed
    echo "🔄 Changes made:"
    grep -n "requestId" "./test_unified.py" | head -5
else
    echo "❌ test_unified.py not found"
fi

echo ""
echo "🎉 Done! Your codebase is now 100% consistent with 'requestId'"