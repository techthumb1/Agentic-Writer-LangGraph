// types/index.d.ts

/**
 * Basic response structure used by API endpoints.
 */
export type APIResponse<T> = {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: string;
  };
};

/**
 * Pagination wrapper for API responses returning lists.
 */
export type PaginatedResponse<T> = {
  items: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
};

/**
 * Metadata structure used by content generation templates.
 */
export type TemplateMetadata = {
  id: string;
  title: string;
  description: string;
  category: string;
  styleProfileDefault: string;
  createdAt: Date;
  updatedAt: Date;
};

/**
 * Style profile definition used to guide tone and structure.
 */
export type StyleProfile = {
  id: string;
  name: string;
  description: string;
  settings: {
    tone: string;
    formality: string;
    complexity: string;
    length: string;
  };
  category: string;
  isDefault: boolean;
  createdAt: Date;
  updatedAt: Date;
};

export type ContentTemplate = {
  id: string;
  title: string;
  description: string;
};

export type GenerateContentPayload = {
  templateId: string;
  styleId: string;
  researchText?: string;
};

export type GeneratedContent = {
  id: string;
  text: string;
  createdAt: Date;
};
