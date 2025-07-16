// frontend/types/template.ts
export interface TemplateParameter {
  name: string;
  label: string;
  type: "text" | "textarea" | "number" | "select" | "checkbox" | "string";
  placeholder?: string;
  default?: string | number | boolean;
  options?: string[];
  min?: number;
  max?: number;
  required?: boolean;
  description?: string;
}

export interface Template {
  id: string;
  slug: string;
  name: string;
  description: string;
  category: string;
  sections: unknown[];
  defaults: Record<string, unknown>;
  system_prompt?: string;
  structure: Record<string, unknown>;
  research: Record<string, unknown>;
  parameters: Record<string, TemplateParameter>;
  metadata: {
    version: string;
    created_by: string;
    last_updated: string;
    parameter_flexibility: string;
  };
  version: string;
  filename: string;
}