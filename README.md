# AI Content Generator

A multi-agent content generation platform that leverages LangGraph and modern web technologies to create high-quality AI-focused content with customizable style profiles and templates.

## Features

- **Multi-Agent Architecture**: Specialized agents for planning, research, writing, editing, SEO optimization, and publishing
- **Dynamic Style Profiles**: 17 pre-configured writing styles from beginner-friendly to PhD-level academic
- **Content Templates**: Flexible YAML-based templates for various AI topics
- **Real-time Generation**: Live preview and status tracking during content creation
- **Modern Frontend**: Next.js 14+ with TypeScript, Tailwind CSS, and shadcn/ui components
- **Database Integration**: Prisma ORM with PostgreSQL for content management
- **Deployment Ready**: Configured for Render.com deployment

## Architecture

### Backend (Python)

- **LangGraph**: Multi-agent workflow orchestration
- **Specialized Agents**:
  - `planner.py`: Content strategy and structure planning
  - `researcher.py`: Information gathering and fact verification
  - `writer.py`: Content generation with style-specific prompts
  - `editor.py`: Content refinement and quality assurance
  - `seo_agent.py`: SEO optimization and metadata generation
  - `publisher.py`: Content publishing and distribution

### Frontend (Next.js)

- **React Components**: Modular UI with TypeScript
- **Custom Hooks**: Content generation, style profiles, and template management
- **Real-time Updates**: WebSocket-based generation status tracking
- **Responsive Design**: Mobile-first approach with Tailwind CSS

## Prerequisites

- Python 3.12+
- Node.js 18+
- pnpm or npm
- PostgreSQL database
- OpenAI API key (or compatible LLM API)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-content-generator
```

### 2. Backend Setup

```bash
# Create and activate virtual environment
python -m venv writer
source writer/bin/activate  # On Windows: writer\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
pnpm install
# or
npm install
```

### 4. Database Setup

```bash
# Generate Prisma client
cd frontend
npx prisma generate

# Run migrations
npx prisma migrate dev

# Seed database (optional)
npx prisma db seed
```

### 5. Environment Configuration

Create `.env` files in both root and frontend directories:

**Root `.env`:**

```env
OPENAI_API_KEY=your_openai_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ai-content-generator
```

**Frontend `.env.local`:**

```env
DATABASE_URL="postgresql://username:password@localhost:5432/ai_content"
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_nextauth_secret
```

## Usage

### Development Mode

1. **Start the Backend Server:**

```bash
python -m langgraph_app
```

2. **Start the Frontend Development Server:**

```bash
cd frontend
pnpm dev
```

3. **Access the Application:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000

### Content Generation Workflow

1. **Select Template**: Choose from available content templates (e.g., "Federated Learning 101")
2. **Choose Style Profile**: Pick from 17+ writing styles:
   - `beginner_friendly`: Accessible explanations for newcomers
   - `technical_dive`: Deep technical analysis
   - `phd_academic`: Research-level academic writing
   - `ai_in_healthcare`: Healthcare-focused AI content
   - `startup_trends_brief`: Business and startup perspectives

3. **Generate Content**: The multi-agent system will:
   - Plan the content structure
   - Research relevant information
   - Generate initial content
   - Edit and refine the output
   - Optimize for SEO
   - Prepare for publishing

## Project Structure

```plaintext
├── langgraph_app/          # Python backend with LangGraph agents
│   ├── agents/            # Specialized AI agents
│   ├── graph.py           # LangGraph workflow definition
│   └── model_registry.py  # LLM model management
├── frontend/              # Next.js frontend application
│   ├── app/              # Next.js 14+ app router
│   ├── components/       # React components
│   ├── hooks/           # Custom React hooks
│   └── lib/             # Utility libraries
├── data/                # Content templates and style profiles
│   ├── content_templates/ # YAML content templates
│   └── style_profiles/   # Writing style configurations
├── storage/             # Generated content storage
├── prompts/             # LLM prompt templates
└── prisma/              # Database schema and migrations
```

## Design System

- Tailwind config → `tailwind.config.ts`
- Shadcn components live in `frontend/components/ui`

┌────────────┐            JSON / HTML            ┌─────────────┐
│  Next.js   │  ─ REST →  /api/generate  ───────▶│ LangGraph   │
│  frontend  │◀─ SSE ─┐        ▲                │  Agents     │
└────────────┘        │        │                └─────────────┘
      │               │        │ markdown / md          │
      │               └── /api/content/{id} ────────────┘
      ▼      
─ storage/{week}/{slug}.json / .md

## Style Profiles

The system includes 17 pre-configured writing styles:

- **Academic**: `phd_academic`, `phd_lit_review`
- **Educational**: `beginner_friendly`, `educational_expert`, `technical_tutor`
- **Business**: `founder_storytelling`, `startup_trends_brief`, `market_flash`
- **Technical**: `technical_dive`, `experimental_lab_log`
- **Specialized**: `ai_in_healthcare`, `ai_news_brief`, `policy_watch`
- **Media**: `popular_sci`, `debate_position`

## Configuration

### Adding New Templates

Create YAML files in `data/content_templates/`:

```yaml
name: "Your Template Name"
description: "Template description"
parameters:
  topic: "Main topic"
  audience: "Target audience"
sections:
  - title: "Introduction"
    content_type: "overview"
  - title: "Main Content"
    content_type: "detailed_analysis"
```

### Creating Custom Style Profiles

Add YAML files to `data/style_profiles/`:

```yaml
name: "Your Style Name"
description: "Style description"
tone: "professional"
complexity: "intermediate"
format: "structured"
special_instructions: "Any specific requirements"
```

## Deployment

### Render.com Deployment

The project includes `deployment/render.yaml` for easy deployment:

1. Connect your repository to Render
2. Use the provided `render.yaml` configuration
3. Set environment variables in Render dashboard
4. Deploy both frontend and backend services

### Manual Deployment

```bash
# Build frontend
cd frontend
pnpm build

# Start production servers
pnpm start  # Frontend
python -m langgraph_app  # Backend
```

## Testing

```bash
# Run Python tests
pytest tests/

# Run frontend tests (if configured)
cd frontend
pnpm test
```

## Monitoring and Analytics

- **LangSmith Integration**: Trace and debug agent interactions
- **Content Analytics**: Track generation success rates and quality metrics
- **Performance Monitoring**: Monitor API response times and resource usage

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## API Documentation

### Content Generation Endpoint

```typescript
POST /api/generate
{
  "template": "federated_learning_101",
  "style_profile": "technical_dive",
  "parameters": {
    "topic": "Federated Learning",
    "audience": "ML Engineers"
  }
}
```

### Template Management

- `GET /api/templates` - List all templates
- `POST /api/templates` - Create new template
- `PUT /api/templates/:id` - Update template

### Style Profile Management

- `GET /api/styles` - List all style profiles
- `POST /api/styles` - Create new style profile

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify DATABASE_URL in environment variables
   - Ensure PostgreSQL is running
   - Run `npx prisma migrate dev`

2. **LangGraph Agent Errors**
   - Check OpenAI API key configuration
   - Verify LangChain environment variables
   - Review agent logs in `langgraph_app/__pycache__/`

3. **Frontend Build Errors**
   - Clear node_modules and reinstall: `rm -rf node_modules && pnpm install`
   - Check TypeScript configuration
   - Verify all dependencies are installed

## License

This project is licensed under the MIT License © 2025 Jason Robinson - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- LangGraph for multi-agent orchestration
- OpenAI for language model capabilities
- Next.js team for the excellent framework
- shadcn/ui for beautiful UI components

---

For more information, please refer to the individual component documentation or open an issue on GitHub.