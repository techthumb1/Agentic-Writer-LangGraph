// File: frontend/lib/content-generation-engine.ts
import { z } from 'zod';

// Enterprise API Schema matching your backend

// Enterprise response schemas
const QualityScoreSchema = z.object({
  overall: z.number(),
  completeness: z.number(),
  coherence: z.number(),
  style_adherence: z.number(),
  technical_accuracy: z.number(),
});

const InnovationReportSchema = z.object({
  techniques_used: z.array(z.string()),
  innovation_level: z.string(),
  creative_risk_score: z.number(),
});

const GenerationMetadataSchema = z.object({
  generation_id: z.string(),
  template_id: z.string(),
  style_profile: z.string(),
  completed_agents: z.array(z.string()),
  failed_agents: z.array(z.string()),
  generation_time: z.string(),
  word_count: z.number(),
  seo_metadata: z.record(z.unknown()).optional(),
  innovation_report: InnovationReportSchema.optional(),
});

const EnterpriseGenerationResponseSchema = z.object({
  success: z.boolean(),
  content: z.string().optional(),
  metadata: GenerationMetadataSchema.optional(),
  quality_score: QualityScoreSchema.optional(),
  generation_id: z.string().optional(),
  error: z.string().optional(),
  errors: z.array(z.string()).optional(),
});

// Template and Style Profile schemas (simplified - backend loads these)
const TemplateInfoSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  category: z.string(),
  sections: z.array(z.string()),
  metadata: z.record(z.unknown()),
  filename: z.string(),
});

const StyleProfileInfoSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  category: z.string(),
  tone: z.string(),
  voice: z.string(),
  structure: z.string(),
  system_prompt: z.string(),
  settings: z.record(z.unknown()),
  filename: z.string(),
});

// Define the EnterpriseGenerationRequestSchema to match the structure used in convertToEnterpriseRequest
export type EnterpriseGenerationRequest = {
  prompt: {
    content_requirements: {
      title: string;
      sections: string[];
      category: string;
      difficulty: string;
      target_audience: string;
    };
    style_requirements: {
      tone: string;
      voice: string;
      formality: string;
      perspective: string;
      technical_level: string;
    };
    structure_requirements: {
      introduction_style: string;
      paragraph_length: string;
      use_headings: boolean;
      use_bullet_points: boolean;
      include_examples: boolean;
      include_analogies: boolean;
    };
    language_requirements: {
      vocabulary_level: string;
      sentence_complexity: string;
      use_jargon: boolean;
      preferred_phrases: string[];
      avoid_phrases: string[];
    };
    formatting_requirements: {
      markdown_enabled: boolean;
      emoji_usage: string;
      code_block_style?: string;
      quote_style?: string;
    };
    user_parameters: Record<string, unknown>;
  };
  preferences: {
    maxTokens: number;
    temperature: number;
    model: string;
  };
  workflow: string;
};
export type EnterpriseGenerationResponse = z.infer<typeof EnterpriseGenerationResponseSchema>;
export type QualityScore = z.infer<typeof QualityScoreSchema>;
export type InnovationReport = z.infer<typeof InnovationReportSchema>;
export type TemplateInfo = z.infer<typeof TemplateInfoSchema>;
export type StyleProfileInfo = z.infer<typeof StyleProfileInfoSchema>;

interface SimpleGenerationRequest {
  template: string;
  style_profile: string;
  dynamic_parameters?: Record<string, unknown>;
  priority?: number;
  timeout_seconds?: number;
  generation_mode?: 'standard' | 'premium' | 'enterprise';
}

interface EnterpriseGenerationResult {
  id: string;
  content: string;
  metadata: {
    generation_id: string;
    template_used: string;
    style_profile_used: string;
    generated_at: Date;
    word_count: number;
    completed_agents: string[];
    failed_agents: string[];
    processing_time_ms?: number;
    seo_metadata?: Record<string, unknown>;
    innovation_report?: InnovationReport;
  };
  quality_score: QualityScore | null;
  status: 'success' | 'error' | 'queued';
  errors?: string[];
}

export class EnterpriseContentGenerationEngine {
  private baseUrl: string;
  private apiKey: string;
  private templates: Map<string, TemplateInfo> = new Map();
  private styleProfiles: Map<string, StyleProfileInfo> = new Map();
  private isInitialized = false;

  constructor(baseUrl = '', apiKey = '') {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey || process.env.NEXT_PUBLIC_LANGGRAPH_API_KEY || 'dev-key';
    this.initialize();
  }

  private async initialize() {
    try {
      await this.loadTemplatesFromBackend();
      await this.loadStyleProfilesFromBackend();
      this.isInitialized = true;
      console.log('Enterprise Content Generation Engine initialized');
    } catch (error) {
      console.error('Failed to initialize Enterprise Engine:', error);
    }
  }

  private async loadTemplatesFromBackend() {
    try {
      const response = await fetch(`${this.baseUrl}/api/templates`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to load templates: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.success && data.data?.items) {
        for (const template of data.data.items) {
          const validated = TemplateInfoSchema.parse(template);
          this.templates.set(validated.id, validated);
        }
        console.log(`Loaded ${this.templates.size} templates from backend`);
      }
    } catch (error) {
      console.error('Failed to load templates from backend:', error);
    }
  }

  private async loadStyleProfilesFromBackend() {
    try {
      const response = await fetch(`${this.baseUrl}/api/style-profiles`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to load style profiles: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.success && data.data?.items) {
        for (const profile of data.data.items) {
          const validated = StyleProfileInfoSchema.parse(profile);
          this.styleProfiles.set(validated.id, validated);
        }
        console.log(`Loaded ${this.styleProfiles.size} style profiles from backend`);
      }
    } catch (error) {
      console.error('Failed to load style profiles from backend:', error);
    }
  }

  private convertToEnterpriseRequest(request: SimpleGenerationRequest): EnterpriseGenerationRequest {
    const params = request.dynamic_parameters || {};
    
    return {
      prompt: {
        content_requirements: {
          title: (params.topic as string) || 'Untitled Content',
          sections: (params.sections as string[]) || [],
          category: (params.category as string) || 'general',
          difficulty: (params.difficulty as string) || 'intermediate',
          target_audience: (params.audience as string) || 'general',
        },
        style_requirements: {
          tone: (params.tone as string) || 'professional',
          voice: (params.voice as string) || 'authoritative',
          formality: (params.formality as string) || 'formal',
          perspective: (params.perspective as string) || 'third-person',
          technical_level: (params.technical_level as string) || 'intermediate',
        },
        structure_requirements: {
          introduction_style: (params.introduction_style as string) || 'hook',
          paragraph_length: (params.paragraph_length as string) || 'medium',
          use_headings: (params.use_headings as boolean) ?? true,
          use_bullet_points: (params.use_bullet_points as boolean) ?? true,
          include_examples: (params.include_examples as boolean) ?? true,
          include_analogies: (params.include_analogies as boolean) ?? false,
        },
        language_requirements: {
          vocabulary_level: (params.vocabulary_level as string) || 'intermediate',
          sentence_complexity: (params.sentence_complexity as string) || 'mixed',
          use_jargon: (params.use_jargon as boolean) ?? false,
          preferred_phrases: (params.preferred_phrases as string[]) || [],
          avoid_phrases: (params.avoid_phrases as string[]) || [],
        },
        formatting_requirements: {
          markdown_enabled: (params.markdown_enabled as boolean) ?? true,
          emoji_usage: (params.emoji_usage as string) || 'none',
          code_block_style: (params.code_block_style as string),
          quote_style: (params.quote_style as string),
        },
        user_parameters: {
          template: request.template,
          style_profile: request.style_profile,
          priority: request.priority || 1,
          timeout_seconds: request.timeout_seconds || 300,
          generation_mode: request.generation_mode || 'standard',
          ...params,
        },
      },
      preferences: {
        maxTokens: (params.max_tokens as number) || 2000,
        temperature: (params.temperature as number) || 0.7,
        model: (params.model as string) || 'gpt-4-turbo',
      },
      workflow: 'content_generation',
    };
  }

  async generateContent(request: SimpleGenerationRequest): Promise<EnterpriseGenerationResult> {
    if (!this.isInitialized) {
      throw new Error('Enterprise Content Generation Engine is not initialized yet.');
    }

    const generationId = `gen_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`;

    try {
      // Validate template and style profile exist
      if (!this.templates.has(request.template)) {
        throw new Error(`Template '${request.template}' not found`);
      }

      if (!this.styleProfiles.has(request.style_profile)) {
        throw new Error(`Style profile '${request.style_profile}' not found`);
      }

      // Convert to enterprise request format
      const enterpriseRequest = this.convertToEnterpriseRequest(request);

      // Call enterprise backend
      const response = await fetch(`${this.baseUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`,
        },
        body: JSON.stringify(enterpriseRequest),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || errorData.error || `Generation failed: ${response.statusText}`);
      }

      const rawResult = await response.json();
      const validatedResult = EnterpriseGenerationResponseSchema.parse(rawResult);

      if (!validatedResult.success) {
        return {
          id: generationId,
          content: '',
          metadata: {
            generation_id: validatedResult.generation_id || generationId,
            template_used: request.template,
            style_profile_used: request.style_profile,
            generated_at: new Date(),
            word_count: 0,
            completed_agents: [],
            failed_agents: [],
          },
          quality_score: null,
          status: 'error',
          errors: validatedResult.errors || [validatedResult.error || 'Unknown error'],
        };
      }

      // Process successful result
      const content = validatedResult.content || '';
      const metadata = validatedResult.metadata;
      const wordCount = content.split(/\s+/).length;

      return {
        id: metadata?.generation_id || generationId,
        content,
        metadata: {
          generation_id: metadata?.generation_id || generationId,
          template_used: request.template,
          style_profile_used: request.style_profile,
          generated_at: new Date(),
          word_count: metadata?.word_count || wordCount,
          completed_agents: metadata?.completed_agents || [],
          failed_agents: metadata?.failed_agents || [],
          seo_metadata: metadata?.seo_metadata,
          innovation_report: metadata?.innovation_report,
        },
        quality_score: validatedResult.quality_score || null,
        status: validatedResult.content ? 'success' : 'queued',
        errors: [],
      };

    } catch (error) {
      console.error('Enterprise content generation failed:', error);
      
      return {
        id: generationId,
        content: '',
        metadata: {
          generation_id: generationId,
          template_used: request.template,
          style_profile_used: request.style_profile,
          generated_at: new Date(),
          word_count: 0,
          completed_agents: [],
          failed_agents: [],
        },
        quality_score: null,
        status: 'error',
        errors: [error instanceof Error ? error.message : 'Unknown error occurred'],
      };
    }
  }

  async getGenerationStatus(generationId: string): Promise<{
    status: 'queued' | 'running' | 'completed' | 'failed';
    progress: number;
    current_agent?: string;
    content?: string;
    error?: string;
    metadata?: Record<string, unknown>;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/generation/${generationId}`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to get generation status: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to get generation status:', error);
      throw error;
    }
  }

  // Enhanced utility methods using backend data
  getAvailableTemplates(): TemplateInfo[] {
    return Array.from(this.templates.values());
  }

  getAvailableStyleProfiles(): StyleProfileInfo[] {
    return Array.from(this.styleProfiles.values());
  }

  getTemplateById(id: string): TemplateInfo | undefined {
    return this.templates.get(id);
  }

  getStyleProfileById(id: string): StyleProfileInfo | undefined {
    return this.styleProfiles.get(id);
  }

  async refreshTemplatesAndProfiles(): Promise<void> {
    this.templates.clear();
    this.styleProfiles.clear();
    await this.loadTemplatesFromBackend();
    await this.loadStyleProfilesFromBackend();
  }

  // Health check for backend connectivity
  async checkBackendHealth(): Promise<{
    status: 'healthy' | 'error';
    version?: string;
    available_models?: string[];
    active_generations?: number;
    cache_hit_rate?: number;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/health`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Backend health check failed:', error);
      return { status: 'error' };
    }
  }

  // Analytics methods
  getEngineStats(): {
    templates_loaded: number;
    style_profiles_loaded: number;
    is_initialized: boolean;
  } {
    return {
      templates_loaded: this.templates.size,
      style_profiles_loaded: this.styleProfiles.size,
      is_initialized: this.isInitialized,
    };
  }
}

// Singleton instance
export const enterpriseContentEngine = new EnterpriseContentGenerationEngine();

// Legacy compatibility wrapper
export class ContentGenerationEngine extends EnterpriseContentGenerationEngine {
  constructor() {
    super();
    console.warn('ContentGenerationEngine is deprecated. Use EnterpriseContentGenerationEngine instead.');
  }
}

// Export legacy singleton for backward compatibility
export const contentGenerationEngine = enterpriseContentEngine;