// ───────────────────────────────────────────────
// types/content.ts
// ───────────────────────────────────────────────

export interface TemplateParameter {
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'number' | 'select' | 'checkbox';
  placeholder?: string;
  default?: string | number | boolean;
  options?: string[];
  required?: boolean;
}

export interface ContentTemplate {
  id: string;
  name: string;
  description?: string;
  parameters: TemplateParameter[];
}

export interface StyleProfile {
  id: string;
  name: string;
  description?: string;
}

export interface GeneratedContent {
  id?: string;
  title: string;
  contentHtml: string;
  metadata?: Record<string, unknown>;
}

export interface GenerateContentPayload {
  templateId: string;
  styleProfileId: string;
  parameters: Record<string, string | number | boolean>;
}