# AgentWrite Pro

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)

> A sophisticated multi-agent content generation platform that leverages LangGraph and modern web technologies to create high-quality AI-focused content with customizable style profiles and templates.

![App Dashboard Preview](./docs/images/dashboard-preview.png)
*Main dashboard showing template selection and style profiles*

## Features

- **Multi-Agent Architecture**: Specialized AI agents for planning, research, writing, editing, SEO, and publishing
- **Dynamic Style Profiles**: 17+ pre-configured writing styles from beginner-friendly to PhD-level academic
- **Content Templates**: Flexible YAML-based templates for various AI topics and use cases
- **Real-time Generation**: Live preview and status tracking during content creation
- **Modern Frontend**: Next.js 14+ with TypeScript, Tailwind CSS, and shadcn/ui components
- **Database Integration**: Prisma ORM with PostgreSQL for robust content management
- **Deployment Ready**: Pre-configured for Render.com and Vercel deployment

![Generation Process](./docs/images/generation-process.gif)
*Real-time content generation in action*

## Architecture

### Backend (Python + LangGraph)

Our multi-agent system orchestrates content creation through specialized agents:

```mermaid
graph LR
    A[Planner] --> B[Researcher]
    B --> C[Writer]
    C --> D[Editor]
    D --> E[SEO Agent]
    E --> F[Publisher]
```bash

**Specialized Agents:**

- **Planner**: Content strategy and structure planning
- **Researcher**: Information gathering and fact verification
- **Writer**: Content generation with style-specific prompts
- **Editor**: Content refinement and quality assurance
- **SEO Agent**: SEO optimization and metadata generation
- **Publisher**: Content publishing and distribution

### Frontend (Next.js + TypeScript)

- **React Components**: Modular UI with TypeScript for type safety
- **Custom Hooks**: Content generation, style profiles, and template management
- **Real-time Updates**: WebSocket-based generation status tracking
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Component Library**: shadcn/ui for consistent, accessible UI components

![Architecture Diagram](./docs/images/architecture-diagram.png)
*System architecture overview*

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- pnpm or npm
- PostgreSQL database
- OpenAI API key (or compatible LLM API)

### 1. Clone & Setup

```bash
git clone <repository-url>
cd agentwrite-pro

# Backend setup
python -m venv writer
source writer/bin/activate  # Windows: writer\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend
pnpm install
```bash

### 2. Environment Configuration

**Root `.env`:**

```env
OPENAI_API_KEY=your_openai_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=agentwrite-pro
```bash

**Frontend `.env.local`:**

```env
DATABASE_URL="postgresql://username:password@localhost:5432/agentwrite_pro"
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_nextauth_secret
```

### 3. Database Setup

```bash
cd frontend
npx prisma generate
npx prisma migrate dev
npx prisma db seed  # Optional
```

### 4. Run the Application

```bash
# Terminal 1: Backend
python -m langgraph_app

# Terminal 2: Frontend
cd frontend
pnpm dev
```

**Access:** Frontend at <http://localhost:3000>, API at <http://localhost:8000>

![Setup Success](./docs/images/setup-success.png)
*Successful setup confirmation*

## Usage Guide

### Content Generation Workflow

![Content Generation Flow](./docs/images/content-flow.png)
*Step-by-step content generation process*

1. **Select Template**: Choose from available content templates
   - "Federated Learning 101"
   - "Future of LLMs"
   - "Startup AI Use Cases"
   - Custom templates

2. **Choose Style Profile**: Pick from 17+ writing styles:
   - `beginner_friendly`: Accessible explanations for newcomers
   - `technical_dive`: Deep technical analysis
   - `phd_academic`: Research-level academic writing
   - `ai_in_healthcare`: Healthcare-focused AI content
   - `startup_trends_brief`: Business and startup perspectives
   - And many more...

3. **Generate Content**: The multi-agent system will:
   - Plan the content structure
   - Research relevant information
   - Generate initial content
   - Edit and refine the output
   - Optimize for SEO
   - Prepare for publishing

![Style Profiles](./docs/images/style-profiles.png)
*Available writing style profiles*

## Project Structure

```bash
agentwrite-pro/
├── langgraph_app/          # Python backend with LangGraph agents
│   ├── agents/               # Specialized AI agents
│   ├── graph.py             # LangGraph workflow definition
│   └── model_registry.py    # LLM model management
├── frontend/              # Next.js frontend application
│   ├── app/                 # Next.js 14+ app router
│   ├── components/          # React components
│   ├── hooks/              # Custom React hooks
│   └── lib/                # Utility libraries
├── data/                 # Content templates and style profiles
│   ├── content_templates/   # YAML content templates
│   └── style_profiles/      # Writing style configurations
├── storage/              # Generated content storage
├── prompts/              # LLM prompt templates
└── prisma/              # Database schema and migrations
```

## Style Profiles

Our system includes 17+ pre-configured writing styles organized by category:

### Academic Styles

- **phd_academic**: Research-level academic writing
- **phd_lit_review**: Literature review format
- **educational_expert**: Expert-level educational content

### Business Styles

- **founder_storytelling**: Narrative-driven business content
- **startup_trends_brief**: Startup and market analysis
- **market_flash**: Quick market insights

### Technical Styles

- **technical_dive**: Deep technical analysis
- **experimental_lab_log**: Research documentation style
- **technical_tutor**: Step-by-step technical guidance

### Specialized Styles

- **ai_in_healthcare**: Healthcare-focused AI content
- **ai_news_brief**: News and updates format
- **policy_watch**: Policy analysis and implications

![Style Examples](./docs/images/style-examples.png)
*Examples of different writing styles*

## Configuration

### Adding New Templates

Create YAML files in `data/content_templates/`:

```yaml
name: "Your Template Name"
description: "Comprehensive template description"
category: "AI/ML"
difficulty: "intermediate"
estimated_length: "2000-3000 words"
parameters:
  topic: 
    type: "string"
    description: "Main topic focus"
    required: true
  audience: 
    type: "string"
    description: "Target audience"
    default: "general"
  depth:
    type: "string"
    options: ["overview", "intermediate", "advanced"]
    default: "intermediate"
sections:
  - title: "Introduction"
    content_type: "overview"
    word_count: 300
  - title: "Core Concepts"
    content_type: "detailed_analysis"
    word_count: 800
  - title: "Practical Applications"
    content_type: "examples"
    word_count: 600
  - title: "Conclusion"
    content_type: "summary"
    word_count: 200
```

### Creating Custom Style Profiles

Add YAML files to `data/style_profiles/`:

```yaml
name: "Your Style Name"
description: "Detailed style description"
category: "technical"
tone: "professional"
complexity: "intermediate"
format: "structured"
audience: "ML engineers"
special_instructions: |
  - Use technical terminology appropriately
  - Include code examples when relevant
  - Maintain professional but approachable tone
writing_guidelines:
  - paragraph_length: "medium"
  - use_bullet_points: true
  - include_examples: true
  - technical_depth: "high"
```

![Template Configuration](./docs/images/template-config.png)
*Template configuration interface*

## Deployment

### Render.com (Recommended)

1. **Connect Repository**: Link your GitHub repository to Render
2. **Use Configuration**: The project includes `deployment/render.yaml`
3. **Set Environment Variables**: Configure in Render dashboard
4. **Deploy**: Both frontend and backend services automatically

### Vercel (Frontend) + Railway (Backend)

```bash
# Deploy frontend to Vercel
cd frontend
vercel --prod

# Deploy backend to Railway
# Use Railway CLI or connect GitHub repository
```

### Manual Deployment

```bash
# Build frontend
cd frontend
pnpm build
pnpm start

# Start backend
python -m langgraph_app
```

![Deployment Status](./docs/images/deployment-status.png)
*Successful deployment dashboard*

## Monitoring & Analytics

### LangSmith Integration

- **Trace Workflows**: Monitor agent interactions and decision points
- **Debug Issues**: Identify bottlenecks in the generation process
- **Performance Metrics**: Track response times and success rates

### Content Analytics

- **Generation Success Rate**: Monitor completion rates by template/style
- **Quality Metrics**: Track user feedback and content ratings
- **Usage Patterns**: Analyze most popular templates and styles

![Analytics Dashboard](./docs/images/analytics-dashboard.png)
*Content generation analytics*

## API Documentation

### Content Generation Endpoint

```typescript
POST /api/generate
Content-Type: application/json

{
  "template": "federated_learning_101",
  "style_profile": "technical_dive",
  "parameters": {
    "topic": "Federated Learning in Healthcare",
    "audience": "ML Engineers",
    "depth": "advanced",
    "include_code": true
  }
}

// Response
{
  "id": "gen_123456",
  "status": "generating",
  "progress": 0,
  "estimated_time": 120
}
```

### WebSocket Status Updates

```typescript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/generate/gen_123456');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // { status: "planning", progress: 20, current_agent: "planner" }
};
```

### Template Management

```typescript
// Get all templates
GET /api/templates

// Create new template
POST /api/templates
{
  "name": "New Template",
  "description": "Template description",
  "category": "AI/ML",
  // ... template configuration
}

// Update template
PUT /api/templates/:id
```

![API Documentation](./docs/images/api-docs.png)
*Interactive API documentation*

## Testing

```bash
# Run Python tests
pytest tests/ -v

# Run frontend tests
cd frontend
pnpm test

# Run E2E tests
pnpm test:e2e

# Generate coverage report
pytest --cov=langgraph_app tests/
```

## Development Tools

### Recommended VS Code Extensions

- Python
- TypeScript and JavaScript
- Tailwind CSS IntelliSense
- Prisma
- ESLint
- Prettier

### Development Commands

```bash
# Format code
black langgraph_app/
cd frontend && pnpm format

# Lint code
flake8 langgraph_app/
cd frontend && pnpm lint

# Type checking
mypy langgraph_app/
cd frontend && pnpm type-check
```

## Troubleshooting

### Common Issues

#### Database Connection

```bash
# Check connection
npx prisma db push

# Reset database
npx prisma migrate reset

# View database
npx prisma studio
```

#### LangGraph Agent Errors

```bash
# Check logs
tail -f logs/langgraph.log

# Test individual agents
python -m pytest tests/test_agents.py -v

# Verify API keys
python -c "import os; print('OPENAI_API_KEY' in os.environ)"
```

#### Frontend Build Issues

```bash
# Clear cache and reinstall
rm -rf node_modules .next
pnpm install
pnpm build
```

![Troubleshooting Guide](./docs/images/troubleshooting.png)
*Common issues and solutions*

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Test** your changes: `pytest tests/ && cd frontend && pnpm test`
5. **Push** to branch: `git push origin feature/amazing-feature`
6. **Open** a Pull Request

### Code Standards

- Follow PEP 8 for Python code
- Use TypeScript for all frontend code
- Include tests for new features
- Update documentation as needed

## Roadmap

### Q1 2025

- [ ] Multi-language support
- [ ] Advanced SEO optimization
- [ ] Content scheduling
- [ ] Team collaboration features

### Q2 2025

- [ ] Custom AI model integration
- [ ] Advanced analytics dashboard
- [ ] API rate limiting
- [ ] Content versioning

### Q3 2025

- [ ] Mobile app
- [ ] WordPress plugin
- [ ] Bulk content generation
- [ ] A/B testing for styles

![Roadmap](./docs/images/roadmap.png)
*Feature development roadmap*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **LangGraph** for multi-agent orchestration capabilities
- **OpenAI** for advanced language model integration
- **Next.js Team** for the excellent React framework
- **shadcn/ui** for beautiful, accessible UI components
- **Prisma** for type-safe database operations
- **Tailwind CSS** for utility-first styling

## Support

- **Documentation**: [docs.example.com](https://docs.example.com)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: <support@example.com>

---

**Made with ❤️ by [Jason Robinson](https://github.com/jasonrobinson)**

[⭐ Star this repo](https://github.com/your-repo) • [🐛 Report Bug](https://github.com/your-repo/issues) • [💡 Request Feature](https://github.com/your-repo/issues)
