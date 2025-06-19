export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: string;
  };
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
export interface ContentItem {
  id: string;
  title: string;
  body: string;
  createdAt: string;
  updatedAt: string;
  // Add more fields as needed
}

export interface Template {
  id: string;
  name: string;
  slug: string;
  description?: string;
  // etc.
}

export interface StyleProfile {
  id: string;
  name: string;
  platform: string;
  tone: string;
  voice: string;
  // etc.
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  // etc.
}

export interface AnalyticsData {
  views: number;
  generatedCount: number;
  retentionRate: number;
  // etc.
}

export interface GenerationStatus {
  id: string;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  error?: string;
}

export interface GenerationPayload {
  template_id: string;
  style_profile_id: string;
  inputs: Record<string, string>;
}
