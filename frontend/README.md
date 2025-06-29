# AgentWrite Pro - Frontend

[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0+-38B2AC.svg)](https://tailwindcss.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)

> Modern, responsive frontend for the AgentWrite Pro platform built with Next.js 14+, TypeScript, and cutting-edge web technologies.

![Frontend Preview](../docs/images/frontend-preview.png)
*Modern, responsive interface design*

## Features

- **Next.js 14+**: Latest App Router with server components and streaming
- **TypeScript**: Full type safety across the application
- **Tailwind CSS**: Utility-first styling with custom design system
- **shadcn/ui**: Beautiful, accessible component library
- **Real-time Updates**: WebSocket integration for live generation status
- **Responsive Design**: Mobile-first approach with adaptive layouts
- **Dark/Light Theme**: Seamless theme switching with persistence
- **Authentication**: Secure user management with NextAuth.js
- **Analytics Integration**: Built-in tracking and user behavior analysis

![Component Showcase](../docs/images/component-showcase.png)
*Key UI components and interactions*

## Architecture

### Technology Stack

```mermaid
graph TB
    A[Next.js 14+] --> B[React 18+]
    A --> C[TypeScript]
    A --> D[App Router]
    B --> E[Custom Hooks]
    B --> F[Context Providers]
    C --> G[Type Definitions]
    D --> H[Server Components]
    D --> I[Client Components]
```

### Key Libraries & Dependencies

| Library | Purpose | Version |
|---------|---------|---------|
| **Next.js** | React framework | 14+ |
| **TypeScript** | Type safety | 5.0+ |
| **Tailwind CSS** | Styling | 3.0+ |
| **shadcn/ui** | Component library | Latest |
| **React Query** | Data fetching | 4.0+ |
| **Prisma** | Database ORM | 5.0+ |
| **NextAuth.js** | Authentication | 4.0+ |
| **Framer Motion** | Animations | 10.0+ |
| **Lucide React** | Icons | Latest |

## Quick Start

### Prerequisites

- Node.js 18.0+
- pnpm (recommended) or npm
- PostgreSQL database

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
pnpm install
# or
npm install

# Copy environment variables
cp .env.example .env.local

# Generate Prisma client
npx prisma generate

# Run database migrations
npx prisma migrate dev

# Start development server
pnpm dev
```

**Access the application at:** <http://localhost:3000>

![Development Setup](../docs/images/dev-setup.png)
*Development environment setup*

## Project Structure

```bash
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/               # Authentication pages
│   ├── api/                  # API routes
│   ├── dashboard/            # Main dashboard
│   ├── generate/             # Content generation
│   ├── settings/             # User settings
│   ├── templates/            # Template management
│   ├── globals.css           # Global styles
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Homepage
├── components/            # React components
│   ├── auth/                 # Authentication components
│   ├── ui/                   # shadcn/ui components
│   ├── content-editor.tsx    # Rich text editor
│   ├── GenerationPreview.tsx # Content preview
│   ├── Navigation.tsx        # Main navigation
│   └── StyleProfilesSelector.tsx # Style selection
├── hooks/                 # Custom React hooks
│   ├── useContentGeneration.ts
│   ├── useStyleProfiles.ts
│   ├── useTemplates.ts
│   └── useGenerationStatus.ts
├── lib/                   # Utility libraries
│   ├── api.ts                # API client
│   ├── prisma.ts             # Database client
│   ├── utils.ts              # Helper functions
│   └── validation.ts         # Form validation
├── types/                 # TypeScript definitions
│   ├── api.ts                # API types
│   ├── content.ts            # Content types
│   └── models.ts             # Database models
├── styles/                # Global styles
│   └── globals.css
└── public/                # Static assets
    ├── icons/
    └── images/
```

## Key Components

### Content Generation Flow

```typescript
// useContentGeneration.ts
export function useContentGeneration() {
  const [status, setStatus] = useState<GenerationStatus>('idle');
  const [progress, setProgress] = useState(0);
  
  const generateContent = async (params: GenerationParams) => {
    setStatus('generating');
    
    const response = await api.post('/api/generate', params);
    const { id } = response.data;
    
    // Connect to WebSocket for real-time updates
    const ws = new WebSocket(`ws://localhost:8000/ws/generate/${id}`);
    
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      setProgress(update.progress);
      setStatus(update.status);
    };
    
    return response.data;
  };
  
  return { generateContent, status, progress };
}
```

![Generation Flow](../docs/images/generation-flow.png)
*Content generation user interface*

### Style Profile Selector

```typescript
// StyleProfilesSelector.tsx
interface StyleProfile {
  id: string;
  name: string;
  description: string;
  category: string;
  complexity: 'beginner' | 'intermediate' | 'advanced';
}

export function StyleProfilesSelector({ onSelect }: Props) {
  const { data: profiles, isLoading } = useStyleProfiles();
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {profiles?.map((profile) => (
        <Card 
          key={profile.id}
          className="cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => onSelect(profile)}
        >
          <CardHeader>
            <CardTitle>{profile.name}</CardTitle>
            <Badge variant="secondary">{profile.category}</Badge>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {profile.description}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
```

![Style Selector](../docs/images/style-selector.png)
*Style profile selection interface*

### Real-time Generation Preview

```typescript
// GenerationPreview.tsx
export function GenerationPreview({ generationId }: Props) {
  const { data: content, status } = useGenerationStatus(generationId);
  
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Generation Preview</h3>
        <Badge variant={status === 'completed' ? 'success' : 'default'}>
          {status}
        </Badge>
      </div>
      
      {status === 'generating' && (
        <div className="space-y-2">
          <Progress value={content?.progress || 0} />
          <p className="text-sm text-muted-foreground">
            Current step: {content?.currentAgent}
          </p>
        </div>
      )}
      
      {content?.preview && (
        <div className="prose prose-slate dark:prose-invert max-w-none">
          <ReactMarkdown>{content.preview}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}
```

## API Integration

### Content Generation API

```typescript
// lib/api.ts
class ApiClient {
  async generateContent(params: GenerationParams): Promise<GenerationResponse> {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });
    
    if (!response.ok) {
      throw new Error('Generation failed');
    }
    
    return response.json();
  }
  
  async getTemplates(): Promise<Template[]> {
    const response = await fetch('/api/templates');
    return response.json();
  }
  
  async getStyleProfiles(): Promise<StyleProfile[]> {
    const response = await fetch('/api/styles');
    return response.json();
  }
}
```

### Type Definitions

```typescript
// types/content.ts
export interface GenerationParams {
  template: string;
  styleProfile: string;
  parameters: Record<string, any>;
}

export interface GenerationResponse {
  id: string;
  status: GenerationStatus;
  progress: number;
  estimatedTime?: number;
}

export type GenerationStatus = 
  | 'idle'
  | 'queued'
  | 'planning'
  | 'researching'
  | 'writing'
  | 'editing'
  | 'optimizing'
  | 'completed'
  | 'failed';
```

![API Integration](../docs/images/api-integration.png)
*API integration architecture*

## Styling & Design System

### Tailwind Configuration

```typescript
// tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        secondary: {
          50: '#f8fafc',
          500: '#64748b',
          900: '#0f172a',
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      }
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
```

### Component Design Patterns

```typescript
// components/ui/button.tsx
const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "underline-offset-4 hover:underline text-primary",
      },
      size: {
        default: "h-10 py-2 px-4",
        sm: "h-9 px-3 rounded-md",
        lg: "h-11 px-8 rounded-md",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);
```

![Design System](../docs/images/design-system.png)
*Design system components and patterns*

## Development Workflow

### Available Scripts

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "format": "prettier --write .",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:e2e": "playwright test",
    "db:generate": "prisma generate",
    "db:migrate": "prisma migrate dev",
    "db:studio": "prisma studio",
    "db:seed": "tsx prisma/seed.ts"
  }
}
```

### Code Quality Tools

```bash
# Type checking
pnpm type-check

# Linting
pnpm lint

# Code formatting
pnpm format

# Run tests
pnpm test

# E2E testing
pnpm test:e2e
```

## Performance Optimization

### Next.js Optimizations

- **Server Components**: Reduce client-side JavaScript
- **Image Optimization**: Automatic image optimization with next/image
- **Code Splitting**: Automatic route-based code splitting
- **Bundle Analysis**: Use @next/bundle-analyzer for optimization

### Loading States & Suspense

```typescript
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-64" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-48" />
        ))}
      </div>
    </div>
  );
}
```

![Performance Metrics](../docs/images/performance-metrics.png)
*Application performance analytics*

## Testing

### Unit Testing with Jest

```typescript
// __tests__/components/StyleProfilesSelector.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { StyleProfilesSelector } from '@/components/StyleProfilesSelector';

describe('StyleProfilesSelector', () => {
  it('renders style profiles correctly', () => {
    const mockProfiles = [
      { id: '1', name: 'Technical', category: 'Technical' },
      { id: '2', name: 'Academic', category: 'Academic' },
    ];
    
    render(
      <StyleProfilesSelector 
        profiles={mockProfiles}
        onSelect={jest.fn()}
      />
    );
    
    expect(screen.getByText('Technical')).toBeInTheDocument();
    expect(screen.getByText('Academic')).toBeInTheDocument();
  });
});
```

### E2E Testing with Playwright

```typescript
// e2e/content-generation.spec.ts
import { test, expect } from '@playwright/test';

test('content generation flow', async ({ page }) => {
  await page.goto('/dashboard');
  
  // Select template
  await page.click('[data-testid="template-selector"]');
  await page.click('[data-testid="template-federated-learning"]');
  
  // Select style profile
  await page.click('[data-testid="style-technical-dive"]');
  
  // Start generation
  await page.click('[data-testid="generate-button"]');
  
  // Wait for completion
  await expect(page.locator('[data-testid="generation-status"]'))
    .toContainText('completed');
});
```

## Deployment

### Environment Variables

```bash
# .env.local
DATABASE_URL="postgresql://user:pass@localhost:5432/agentwrite_pro"
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key"
NEXT_PUBLIC_API_URL="http://localhost:8000"
```

### Build & Deploy

```bash
# Build for production
pnpm build

# Start production server
pnpm start

# Deploy to Vercel
vercel --prod
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "start"]
```

![Deployment Pipeline](../docs/images/deployment-pipeline.png)
*Continuous deployment workflow*

## Troubleshooting

### Common Issues

#### Database Connection

```bash
# Check Prisma connection
npx prisma db push

# Reset database
npx prisma migrate reset

# View database
npx prisma studio
```

#### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Clear node modules
rm -rf node_modules
pnpm install

# Type check
pnpm type-check
```

#### WebSocket Connection Issues

```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify WebSocket endpoint
wscat -c ws://localhost:8000/ws/generate/test
```

## Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Run the test suite
6. Submit a pull request

### Code Standards

- Use TypeScript for all new code
- Follow ESLint configuration
- Write tests for components and hooks
- Use semantic commit messages
- Update documentation as needed

## Support

- **Documentation**: [Internal Wiki](https://wiki.company.com/agentwrite-pro)
- **Issues**: [GitHub Issues](https://github.com/company/agentwrite-pro/issues)
- **Slack**: #agentwrite-pro-support
