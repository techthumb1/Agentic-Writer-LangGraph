export type TemplateMetadata = {
  id: string;
  title: string;
  description: string;
  category: string;
  styleProfileDefault: string;
  createdAt: Date;
  updatedAt: Date;
};

export type APIResponse<T> = {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: string;
  };
};

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
  category: string; // ✅ Add this line
  isDefault: boolean;
  createdAt: Date;
  updatedAt: Date;
};
