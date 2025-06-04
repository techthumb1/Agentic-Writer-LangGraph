# Agentic Writer

![Agentic Writer Logo](https://raw.githubusercontent.com/agentic-writer-langgraph/agentic-writer-langgraph/main/public/logo.png)

**AI-powered content pipeline** for Substack, Medium, and tech blogs.  
Built with **Next JS 15**, **LangGraph**, and **Python agents** (Planner → Writer → Publisher → Editor).

---

## Features

| Capability | Description |
|------------|-------------|
| **One-click Drafts** | Pick a *Style Profile* (PhD Academic, Market Flash, etc.), enter a topic, and generate a fully-formatted draft. |
| **Executable Code Blocks** | Code-Verifier agent runs every code cell and inlines output / screenshots. |
| **Cross-posting** | Publish to Substack & Medium with canonical URL. |
| **Template Marketplace** | YAML templates (Case Study, Lab Log) purchasable à la carte. |
| **Analytics Feedback** | Open-rate and read-time metrics feed back to the Planner agent to improve future drafts. |

---


*See* `frontend/README.md` *for UI dev workflow.*

---

## Quick Start (dev)

```bash
git clone https://github.com/yourname/agentic-writer
cd agentic-writer

# Backend venv
python -m venv writer && source writer/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm i
npm run dev
```

## Roadmap

- Stripe metered billing & credit counter- 
- Team workspaces- 
- Template marketplace launch- 
- Self-host & on-prem offering

</details>

---

## 4  Optional `/frontend/README.md` snippet

```md
# Frontend — Agentic Writer

Next JS 15 + Tailwind + Shadcn.
```

## Key Commands

| Command | Purpose |
|---------|---------|
| `npm run dev` | local dev |
| `npm run lint`| ESLint |
| `npm run build && npm start` | production preview |

## Design System

* Tailwind config → `tailwind.config.ts`
* Shadcn components live in `frontend/components/ui`

## Local API proxy

During dev the frontend talks to the Python agents via **Next.js API routes** under `/app/api/*`.

Production split:  
* Vercel (frontend) ↔ Render (FastAPI) with `/api/*` rewrites.

## License

MIT © 2025 Jason Robinson