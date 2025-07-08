// frontend/types/api.ts
// Core API Response Types
export interface APIResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: {
    code?: string;
    message: string;
    details?: string;
  };
  timestamp?: string;
  requestId?: string;
  fallback?: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

// Template and Style Profile Types
export interface TemplateParameter {
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'number' | 'select' | 'checkbox' | 'date' | 'email' | 'url';
  placeholder?: string;
  default?: string | number | boolean;
  options?: string[];
  required?: boolean;
  validation?: Record<string, unknown>;
}

export interface BackendTemplate {
  id: string;
  slug: string;
  name: string;
  description?: string;
  category?: string;
  parameters?: Record<string, TemplateParameter>;
  metadata?: Record<string, unknown>;
  version?: string;
  filename: string;
}

export interface BackendStyleProfile {
  id: string;
  name: string;
  description?: string;
  category?: string;
  platform?: string;
  tone?: string;
  voice?: string;
  structure?: string;
  system_prompt?: string;
  settings?: Record<string, unknown>;
  filename: string;
}

// Legacy Types (keep for backward compatibility)
export interface Template {
  id: string;
  name: string;
  slug: string;
  description?: string;
  parameters?: Record<string, unknown>;
}

export interface StyleProfile {
  id: string;
  name: string;
  platform: string;
  tone: string;
  voice: string;
  description?: string;
  category?: string;
}

// Content Generation Types
export interface GenerationRequest {
  template: string;
  style_profile: string;
  dynamic_parameters?: Record<string, unknown>;
  priority?: number;
  timeout_seconds?: number;
}

export interface GenerationResponse {
  requestId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress?: number;
  current_step?: string;
  content?: string;
  metadata?: Record<string, unknown>;
  errors?: string[];
  warnings?: string[];
  metrics?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
  completed_at?: string;
}

// Legacy Generation Types (keep for backward compatibility)
export interface GenerationStatus {
  id: string;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  error?: string;
  progress?: number;
  content?: string;
}

export interface GenerationPayload {
  template_id: string;
  style_profile_id: string;
  inputs: Record<string, string>;
  dynamic_parameters?: Record<string, unknown>;
}

// Content Types
export interface ContentItem {
  id: string;
  title: string;
  body: string;
  createdAt: string;
  updatedAt: string;
  metadata?: Record<string, unknown>;
}

export interface GeneratedContent {
  content: string;
  title?: string;
  contentHtml?: string;
  metadata?: Record<string, unknown>;
}

// User and Analytics Types
export interface UserProfile {
  id: string;
  name: string;
  email: string;
  preferences?: Record<string, unknown>;
}

export interface AnalyticsData {
  views: number;
  generatedCount: number;
  retentionRate: number;
  averageGenerationTime?: number;
  popularTemplates?: string[];
}

// Utility Types
export interface PaginationData {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}