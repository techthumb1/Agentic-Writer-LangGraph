// frontend/hooks/useTemplates.ts
import { useQuery } from "@tanstack/react-query";

interface TemplateParameter {
  name: string;
  label: string;
  type: "text" | "textarea" | "number" | "select" | "checkbox";
  placeholder?: string;
  default?: string | number | boolean;
  options?: string[];
  required?: boolean;
}

interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  sections?: string[];
  metadata?: Record<string, unknown>;
  filename: string;
  parameters?: TemplateParameter[]; // Add parameters property
}

interface TemplatesResponse {
  templates: Template[];
  total: number;
  error?: string;
}


// Mock parameters for templates that don't have them
const generateMockParameters = (templateId: string): TemplateParameter[] => {
  // Common parameters for most templates
  const baseParameters: TemplateParameter[] = [
    {
      name: "topic",
      label: "Topic",
      type: "text",
      placeholder: "Enter the main topic...",
      required: true,
      default: ""
    },
    {
      name: "audience",
      label: "Target Audience",
      type: "select",
      options: ["General Public", "Technical Professionals", "Business Leaders", "Students", "Researchers"],
      default: "General Public",
      required: true
    },
    {
      name: "tone",
      label: "Tone",
      type: "select",
      options: ["Professional", "Casual", "Educational", "Persuasive", "Informative"],
      default: "Professional",
      required: false
    }
  ];

  // Template-specific parameters
  if (templateId.includes("technical") || templateId.includes("tutorial")) {
    baseParameters.push({
      name: "difficulty_level",
      label: "Difficulty Level",
      type: "select",
      options: ["Beginner", "Intermediate", "Advanced"],
      default: "Intermediate"
    });
  }

  if (templateId.includes("startup") || templateId.includes("business")) {
    baseParameters.push({
      name: "industry",
      label: "Industry",
      type: "text",
      placeholder: "e.g., Technology, Healthcare, Finance...",
      default: ""
    });
  }

  if (templateId.includes("research") || templateId.includes("academic")) {
    baseParameters.push({
      name: "research_depth",
      label: "Research Depth",
      type: "select",
      options: ["Surface Level", "Moderate", "Deep Dive", "Comprehensive"],
      default: "Moderate"
    });
  }

  return baseParameters;
};

async function fetcher(url: string): Promise<Template[]> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch templates: ${res.status} ${res.statusText}`);
  }
  
  const result = await res.json();
  
  // Debug logging
  console.log('Templates API response:', result);
  
  // Check if response has templates array (from our transformed API route)
  if (result.templates && Array.isArray(result.templates)) {
    // Add mock parameters to templates that don't have them
    const templatesWithParameters = result.templates.map((template: Template) => ({
      ...template,
      parameters: template.parameters || generateMockParameters(template.id)
    }));
    
    console.log(`✅ Loaded ${templatesWithParameters.length} templates with parameters`);
    return templatesWithParameters;
  }
  
  // Handle error cases
  console.error('Templates API error:', result.error || 'Unexpected response format');
  throw new Error(result.error || 'Failed to load templates');
}

export function useTemplates() {
  const { data, error, isLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: () => fetcher("/api/templates"),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 3,
    retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  return {
    templates: data || [],
    isLoading,
    isError: !!error,
    error: error as Error | null,
  };
}

export type { Template, TemplatesResponse, TemplateParameter };