// ───────────────────────────────────────────────
// types/content.ts - Enhanced Enterprise Content Types
// ───────────────────────────────────────────────

// ═══════════════════════════════════════════════
// Core Template & Profile Types
// ═══════════════════════════════════════════════

export interface TemplateParameter {
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'number' | 'select' | 'checkbox' | 'multiselect' | 'range' | 'date';
  placeholder?: string;
  default?: string | number | boolean | string[];
  options?: string[];
  required?: boolean;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    message?: string;
  };
  conditional?: {
    dependsOn: string;
    value: string | number | boolean;
  };
}

export interface ContentTemplate {
  id: string;
  title: string;
  description?: string;
  category: string;
  difficulty?: string;
  estimatedLength?: string;
  targetAudience?: string;
  icon?: string;
  tags: string[];
  parameters: TemplateParameter[];
  templateData: {
    parameters: TemplateParameter[];
    metadata?: Record<string, unknown>;
    [key: string]: unknown;
  };
  isBuiltIn: boolean;
  isPublic: boolean;
  createdBy?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface StyleProfile {
  id: string;
  name: string;
  description: string;
  category: string;
  icon?: string;
  tags: string[];
  profileData: {
    tone?: string;
    style?: string;
    voice?: string;
    audience?: string;
    format?: string;
    complexity?: string;
    metadata?: Record<string, unknown>;
    [key: string]: unknown;
  };
  isBuiltIn: boolean;
  isPublic: boolean;
  createdBy?: string;
  createdAt: Date;
  updatedAt: Date;
}

// ═══════════════════════════════════════════════
// Content Generation Types
// ═══════════════════════════════════════════════

export interface Section {
  id: string;
  title: string;
  content: string;
  word_count: number;
  order: number;
  sectionType?: 'introduction' | 'body' | 'conclusion' | 'abstract' | 'methodology' | 'results' | 'discussion';
  icon?: string;
  metadata?: {
    confidence_score?: number;
    sources?: string[];
    keywords?: string[];
    readability_score?: number;
    [key: string]: unknown;
  };
}

export interface GenerationMetadata {
  generation_id: string;
  template_used: string;
  style_profile_used: string;
  generated_at: Date;
  word_count: number;
  completed_agents: string[];
  failed_agents: string[];
  processing_time_ms?: number;
  model_used: string;
  tokens_consumed?: number;
  sections?: Section[];
  seo_metadata?: {
    title?: string;
    description?: string;
    keywords?: string[];
    readability_score?: number;
    content_score?: number;
  };
  innovation_report?: {
    originality_score?: number;
    research_depth?: number;
    technical_accuracy?: number;
    practical_applicability?: number;
    sources_count?: number;
  };
  quality_metrics?: {
    coherence_score?: number;
    clarity_score?: number;
    engagement_score?: number;
    technical_accuracy?: number;
    grammar_score?: number;
  };
}

export interface GenerationResult {
  id: string;
  generation_id: string;
  status: 'success' | 'error' | 'partial' | 'pending' | 'processing';
  content?: {
    title: string;
    body: string;
    sections?: Section[];
    summary?: string;
    abstract?: string;
    conclusion?: string;
  };
  metadata: GenerationMetadata;
  errors?: string[];
  warnings?: string[];
}

// ═══════════════════════════════════════════════
// Request & Response Types
// ═══════════════════════════════════════════════

export interface GenerationRequest {
  template: string;
  styleProfile: string;
  parameters?: Record<string, string | number | boolean | string[]>;
  userPreferences?: {
    model?: string;
    maxTokens?: number;
    temperature?: number;
    quality?: 'fast' | 'balanced' | 'high' | 'premium';
    includeReferences?: boolean;
    includeSEO?: boolean;
    customInstructions?: string;
  };
  userId?: string;
  priority?: 'low' | 'normal' | 'high' | 'urgent';
  deadline?: Date;
}

// Legacy support - SimpleGenerationRequest is now an alias for GenerationRequest
export type SimpleGenerationRequest = GenerationRequest;

export interface GenerateContentPayload extends GenerationRequest {
  templateId: string; // Legacy field name
  styleProfileId: string; // Legacy field name
}

// ═══════════════════════════════════════════════
// Enhanced Content Types
// ═══════════════════════════════════════════════

export interface GeneratedContent {
  id: string;
  title?: string;
  content: string;
  wordCount: number;
  sectionCount: number;
  status: 'success' | 'error' | 'partial';
  errors: string[];
  
  // Generation context
  parameters: Record<string, unknown>;
  preferences: Record<string, unknown>;
  
  // Performance metrics
  modelUsed: string;
  tokensConsumed?: number;
  generationTime?: number;
  
  // Agent workflow
  agentSteps?: Array<{
    agent: string;
    action: string;
    result: string;
    timestamp: string;
    wordCount?: number;
  }>;
  
  // Relationships
  templateId: string;
  styleProfileId: string;
  userId: string;
  
  // Content organization
  sections: Section[];
  feedback: ContentFeedback[];
  
  // Versioning
  version: number;
  parentId?: string;
  
  // Publishing
  isPublished: boolean;
  publishedAt?: Date;
  
  // Timestamps
  createdAt: Date;
  updatedAt: Date;
}

export interface ContentFeedback {
  id: string;
  rating: number; // 1-5 scale
  comment?: string;
  tags: string[]; // 'helpful', 'accurate', 'well-written', etc.
  feedbackType: 'quality' | 'accuracy' | 'style' | 'usefulness';
  generatedContentId: string;
  userId: string;
  createdAt: Date;
  updatedAt: Date;
}

// ═══════════════════════════════════════════════
// Analytics & Usage Types
// ═══════════════════════════════════════════════

export interface UsageStats {
  id: string;
  userId: string;
  date: Date;
  contentGenerated: number;
  tokensConsumed: number;
  generationTime: number;
  modelsUsed: string[];
  templatesUsed: string[];
  styleProfilesUsed: string[];
  averageWordCount?: number;
  successRate?: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface TemplateUsage {
  id: string;
  templateId: string;
  templateTitle: string;
  usageCount: number;
  successRate?: number;
  averageRating?: number;
  date: Date;
  totalWordCount: number;
  totalTokens: number;
  averageGenTime: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface StyleProfileUsage {
  id: string;
  profileId: string;
  profileName: string;
  usageCount: number;
  successRate?: number;
  averageRating?: number;
  date: Date;
  totalWordCount: number;
  totalTokens: number;
  averageGenTime: number;
  createdAt: Date;
  updatedAt: Date;
}

// ═══════════════════════════════════════════════
// Queue & Processing Types
// ═══════════════════════════════════════════════

export interface GenerationQueue {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  priority: number;
  retryCount: number;
  maxRetries: number;
  requestData: GenerationRequest;
  resultData?: GenerationResult;
  errorMessage?: string;
  scheduledAt?: Date;
  startedAt?: Date;
  completedAt?: Date;
  userId: string;
  createdAt: Date;
  updatedAt: Date;
}

// ═══════════════════════════════════════════════
// Export & Integration Types
// ═══════════════════════════════════════════════

export interface ContentExport {
  id: string;
  exportType: 'full' | 'content_only' | 'templates' | 'profiles' | 'analytics';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  fileUrl?: string;
  fileName?: string;
  fileSize?: number;
  itemCount?: number;
  exportFormat: 'json' | 'csv' | 'markdown' | 'pdf' | 'docx';
  userId: string;
  requestedAt: Date;
  completedAt?: Date;
  expiresAt?: Date;
}

// ═══════════════════════════════════════════════
// API Response Types
// ═══════════════════════════════════════════════

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  metadata?: {
    timestamp: string;
    requestId: string;
    version: string;
    [key: string]: unknown;
  };
}

export interface GenerationStatusResponse {
  success: boolean;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number; // 0-100
  content?: GenerationResult;
  metadata?: GenerationMetadata;
  requestId: string;
  message?: string;
  estimatedTimeRemaining?: number;
}

export interface ContentListResponse {
  content: GeneratedContent[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
  filters?: {
    status?: string;
    templateId?: string;
    styleProfileId?: string;
    dateRange?: {
      start: Date;
      end: Date;
    };
  };
}

// ═══════════════════════════════════════════════
// Utility Types
// ═══════════════════════════════════════════════

export type ContentStatus = 'draft' | 'generating' | 'completed' | 'failed' | 'archived';
export type GenerationPriority = 'low' | 'normal' | 'high' | 'urgent';
export type ContentQuality = 'fast' | 'balanced' | 'high' | 'premium';
export type SectionType = 'introduction' | 'body' | 'conclusion' | 'abstract' | 'methodology' | 'results' | 'discussion';
export type FeedbackType = 'quality' | 'accuracy' | 'style' | 'usefulness';
export type ExportFormat = 'json' | 'csv' | 'markdown' | 'pdf' | 'docx';

// ═══════════════════════════════════════════════
// Form & Validation Types
// ═══════════════════════════════════════════════

export interface FormValidation {
  isValid: boolean;
  errors: Record<string, string>;
  warnings: Record<string, string>;
}

export interface GenerationForm {
  template: string;
  styleProfile: string;
  parameters: Record<string, unknown>;
  preferences: {
    model: string;
    quality: ContentQuality;
    maxTokens: number;
    temperature: number;
    includeReferences: boolean;
    includeSEO: boolean;
    customInstructions?: string;
  };
  validation: FormValidation;
}

// ═══════════════════════════════════════════════
// Event & Notification Types
// ═══════════════════════════════════════════════

export interface ContentEvent {
  id: string;
  type: 'generation_started' | 'generation_completed' | 'generation_failed' | 'content_published' | 'feedback_received';
  contentId: string;
  userId: string;
  data: Record<string, unknown>;
  timestamp: Date;
}

export interface NotificationPreferences {
  emailNotifications: boolean;
  pushNotifications: boolean;
  generationComplete: boolean;
  generationFailed: boolean;
  weeklyReports: boolean;
  newFeatures: boolean;
}

// ═══════════════════════════════════════════════
// Search & Filter Types
// ═══════════════════════════════════════════════

export interface SearchFilters {
  query?: string;
  status?: ContentStatus[];
  templateIds?: string[];
  styleProfileIds?: string[];
  dateRange?: {
    start: Date;
    end: Date;
  };
  wordCountRange?: {
    min: number;
    max: number;
  };
  tags?: string[];
  categories?: string[];
  userId?: string;
}

export interface SortOptions {
  field: 'createdAt' | 'updatedAt' | 'title' | 'wordCount' | 'rating';
  direction: 'asc' | 'desc';
}