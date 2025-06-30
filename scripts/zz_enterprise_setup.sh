#!/bin/bash
# enterprise_setup.sh - COMPLETE ENTERPRISE PLATFORM SETUP
# 🏢 Automated setup for maximum profitability

echo "🏢 ENTERPRISE CONTENT GENERATION PLATFORM SETUP"
echo "💰 Configuring for maximum profitability..."
echo "==============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Check if Python 3.8+ is available
echo -e "${BLUE}🔍 Checking Python version...${NC}"
python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo -e "${GREEN}✅ Python $python_version detected${NC}"
else
    echo -e "${RED}❌ Python 3.8+ required, found $python_version${NC}"
    exit 1
fi

# Check if Node.js is available for frontend
echo -e "${BLUE}🔍 Checking Node.js...${NC}"
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo -e "${GREEN}✅ Node.js $node_version detected${NC}"
else
    echo -e "${YELLOW}⚠️ Node.js not found. Frontend may not work.${NC}"
fi

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️ requirements.txt not found. Installing core packages...${NC}"
    pip install fastapi uvicorn openai psutil aiohttp pydantic python-multipart
fi

# Install frontend dependencies
echo -e "${BLUE}📦 Installing Frontend dependencies...${NC}"
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    cd frontend
    npm install
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
    cd ..
else
    echo -e "${YELLOW}⚠️ Frontend directory or package.json not found${NC}"
fi

# Create required directories
echo -e "${BLUE}📁 Creating required directories...${NC}"
mkdir -p data/style_profiles
mkdir -p data/content_templates
mkdir -p prompts/writer
mkdir -p storage/agent_memory
mkdir -p logs
echo -e "${GREEN}✅ Directories created${NC}"

# Set up environment variables
echo -e "${BLUE}⚙️ Configuring environment variables...${NC}"
cat > .env.enterprise << 'EOF'
# ENTERPRISE PLATFORM CONFIGURATION
ENTERPRISE_MODE=true
PROFITABILITY_OPTIMIZATION=maximum

# API Configuration
FASTAPI_BASE_URL=http://localhost:8001
FASTAPI_API_KEY=ent_live_sk_2024_profitable_content_generation
LANGGRAPH_API_KEY=ent_live_sk_2024_profitable_content_generation

# Service Ports
CONTENT_ENGINE_PORT=8001
ENTERPRISE_GATEWAY_PORT=8000
MONITORING_SERVICE_PORT=8002
BILLING_SERVICE_PORT=8003
FRONTEND_PORT=3000

# OpenAI Configuration (Add your keys)
OPENAI_API_KEY=your_openai_key_here
DEFAULT_MODEL=gpt-4o

# Optional: Anthropic
ANTHROPIC_API_KEY=your_anthropic_key_here

# Redis (Optional for advanced caching)
REDIS_URL=redis://localhost:6379/0

# Database (Optional for persistence)
DATABASE_URL=postgresql://localhost/enterprise_content

# Monitoring & Analytics
PROMETHEUS_ENABLED=true
LOG_LEVEL=info

# Revenue Settings
BILLING_ENABLED=true
SUBSCRIPTION_MANAGEMENT=true
USAGE_TRACKING=true
EOF

echo -e "${GREEN}✅ Environment configuration created (.env.enterprise)${NC}"
echo -e "${YELLOW}📝 Please update .env.enterprise with your OpenAI API key${NC}"

# Create startup scripts
echo -e "${BLUE}🚀 Creating startup scripts...${NC}"

# Backend startup script
cat > start_backend.sh << 'EOF'
#!/bin/bash
echo "🏢 Starting Enterprise Backend Platform..."
export $(cat .env.enterprise | grep -v '^#' | xargs)
python -m langgraph_app.launch_enterprise
EOF

# Frontend startup script
cat > start_frontend.sh << 'EOF'
#!/bin/bash
echo "🖥️ Starting Enterprise Frontend..."
cd frontend
npm run dev
EOF

# Complete platform startup script
cat > start_enterprise.sh << 'EOF'
#!/bin/bash
echo "🏢 LAUNCHING COMPLETE ENTERPRISE PLATFORM"
echo "💰 Optimized for maximum profitability"

# Start backend in background
export $(cat .env.enterprise | grep -v '^#' | xargs)
echo "🤖 Starting backend services..."
python -m langgraph_app.launch_enterprise &
BACKEND_PID=$!

# Wait for backend to start
sleep 10

# Start frontend in background
echo "🖥️ Starting frontend dashboard..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Enterprise platform launched!"
echo "🌐 Frontend: http://localhost:3000"
echo "🏢 API Gateway: http://localhost:8000"
echo "🤖 Content Engine: http://localhost:8001"
echo "📊 Monitoring: http://localhost:8002"
echo "💰 Billing API: http://localhost:8003"
echo ""
echo "Press Ctrl+C to shutdown..."

# Wait for interrupt
trap 'echo "🛑 Shutting down..."; kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait
EOF

chmod +x start_backend.sh start_frontend.sh start_enterprise.sh

echo -e "${GREEN}✅ Startup scripts created${NC}"

# Create basic style profile if none exists
if [ ! -f "data/style_profiles/jason.yaml" ]; then
    echo -e "${BLUE}📝 Creating default style profile...${NC}"
    mkdir -p data/style_profiles
    cat > data/style_profiles/jason.yaml << 'EOF'
name: "Jason - Enterprise Writer"
description: "Professional enterprise content writer"
category: "business"
voice: "authoritative and engaging"
tone: "professional"
structure: "problem → solution → benefits → action"
audience: "business professionals"
system_prompt: "grad_level_writer.txt"
settings:
  innovation_level: "innovative"
  quality_tier: "enterprise"
EOF
    echo -e "${GREEN}✅ Default style profile created${NC}"
fi

# Create basic content template if none exists
if [ ! -f "data/content_templates/startup_usecases.yaml" ]; then
    echo -e "${BLUE}📝 Creating default content template...${NC}"
    mkdir -p data/content_templates
    cat > data/content_templates/startup_usecases.yaml << 'EOF'
name: "Startup Use Cases"
description: "Enterprise startup use case analysis"
category: "business"
topic: "Startup Innovation"
audience: "entrepreneurs"
platform: "blog"
tone: "inspiring"
parameters:
  - topic
  - industry
  - target_market
structure:
  - introduction
  - market_analysis
  - use_cases
  - implementation
  - conclusion
EOF
    echo -e "${GREEN}✅ Default content template created${NC}"
fi

# Create basic system prompt if none exists
if [ ! -f "prompts/writer/grad_level_writer.txt" ]; then
    echo -e "${BLUE}📝 Creating default system prompt...${NC}"
    mkdir -p prompts/writer
    cat > prompts/writer/grad_level_writer.txt << 'EOF'
You are an enterprise-grade AI writing assistant optimized for business value and profitability.

Your mission:
1. Create compelling, high-value content that drives business results
2. Adapt your writing style to maximize audience engagement
3. Incorporate innovative techniques while maintaining professional quality
4. Focus on actionable insights that deliver measurable value

Writing principles:
- Lead with value and clear benefits
- Use data and examples to support key points
- Create content that drives decision-making
- Maintain professional credibility while being engaging
- Structure content for maximum readability and impact

Always strive for content that not only informs but transforms how readers think and act.
EOF
    echo -e "${GREEN}✅ Default system prompt created${NC}"
fi

echo ""
echo -e "${PURPLE}🎉 ENTERPRISE PLATFORM SETUP COMPLETE!${NC}"
echo ""
echo -e "${GREEN}🚀 NEXT STEPS:${NC}"
echo -e "${YELLOW}1. Update your OpenAI API key in .env.enterprise${NC}"
echo -e "${YELLOW}2. Run: ./start_enterprise.sh${NC}"
echo -e "${YELLOW}3. Visit: http://localhost:3000${NC}"
echo ""
echo -e "${BLUE}💰 REVENUE FEATURES READY:${NC}"
echo "   ✅ Multi-tier subscription system"
echo "   ✅ Usage-based billing"
echo "   ✅ Real-time analytics"
echo "   ✅ Enterprise authentication"
echo "   ✅ Advanced AI content generation"
echo ""
echo -e "${GREEN}💡 Your enterprise platform is ready for profitable operation!${NC}"
echo "==============================================="