#!/bin/bash

echo "🔍 Debugging API Routes"
echo "======================="

# 1. Check your current API structure
echo "📁 Current API structure:"
find app/api -type f -name "*.ts" | sort

echo ""
echo "📄 Templates route content:"
echo "------------------------"
if [ -f "app/api/templates/route.ts" ]; then
    head -20 app/api/templates/route.ts
else
    echo "❌ app/api/templates/route.ts not found"
fi

echo ""
echo "📄 Generate route content:"
echo "------------------------"
if [ -f "app/api/generate/route.ts" ]; then
    head -20 app/api/generate/route.ts
else
    echo "❌ app/api/generate/route.ts not found"
fi

echo ""
echo "📁 Data directories:"
echo "-------------------"
echo "Content templates:"
ls -la ../data/content_templates/ 2>/dev/null || echo "❌ ../data/content_templates/ not found"
ls -la data/content_templates/ 2>/dev/null || echo "❌ data/content_templates/ not found"
ls -la content-templates/ 2>/dev/null || echo "❌ content-templates/ not found"

echo ""
echo "Style profiles:"
ls -la ../data/style_profiles/ 2>/dev/null || echo "❌ ../data/style_profiles/ not found"
ls -la data/style_profiles/ 2>/dev/null || echo "❌ data/style_profiles/ not found"
ls -la style-profiles/ 2>/dev/null || echo "❌ style-profiles/ not found"

echo ""
echo "🧪 Quick API tests:"
echo "==================="
echo "Testing templates endpoint..."
curl -s http://localhost:3000/api/templates | head -200

echo ""
echo "Testing generate endpoint..."
curl -s http://localhost:3000/api/generate | head -200

echo ""
echo "💡 Next steps:"
echo "1. Check your terminal/console for server error messages"
echo "2. Look at the file contents above to see if there are obvious issues"
echo "3. Check if the data directories exist where your code expects them"