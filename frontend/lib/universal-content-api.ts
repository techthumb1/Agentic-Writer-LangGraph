// frontend/lib/universal-content-api.ts
// Frontend integration for Universal Dynamic Content Generation
// FIXED: All TypeScript 'any' types replaced with proper types

import { toast } from '@/hooks/use-toast';

export interface UniversalContentRequest {
  user_request: string;
  template_id?: string;
  style_profile?: string;
  user_context?: {
    expertise_level?: 'beginner' | 'intermediate' | 'advanced' | 'expert';
    domain?: string;
    industry?: string;
    content_purpose?: string;
  };
}

export interface UniversalContentResponse {
  success: boolean;
  approach: 'static_template' | 'dynamic_generation' | 'explicit_selection';
  template: {
    id: string;
    name: string;
    content: Record<string, unknown>; // FIXED: was 'any'
    instructions: string;
    system_prompt: string;
    source: 'static_yaml' | 'dynamic_generated' | 'fallback';
  };
  generation_config: {
    parameters: Record<string, unknown>; // FIXED: was 'any'
    style_profile: string;
    model: string;
  };
  metadata: {
    user_request: string;
    estimated_length?: string;
    reading_time?: string;
    confidence: number;
    template_source: string;
    category: string;
  };
  error?: string;
}

export interface GenerationStatus {
  request_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress?: number;
  current_step?: string;
  result?: {
    content: string;
    metadata: Record<string, unknown>; // FIXED: was 'any'
  };
  error?: string;
}

// FIXED: Proper interface for API response
interface APIResponse<T = unknown> {
  success?: boolean;
  error?: string;
  data?: T;
}

class UniversalContentAPI {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || '/api';
  }

  /**
   * Main method: Generate content for ANY user request
   */
  async generateUniversalContent(request: UniversalContentRequest): Promise<UniversalContentResponse> {
    try {
      console.log('🚀 Generating universal content:', request.user_request.substring(0, 50) + '...');

      const response = await fetch(`${this.baseUrl}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          approach: 'universal',
          ...request,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: UniversalContentResponse = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Generation failed');
      }

      console.log('✅ Universal content generated:', {
        approach: data.approach,
        template: data.template.name,
        style: data.generation_config.style_profile,
        model: data.generation_config.model,
      });

      return data;

    } catch (error) {
      console.error('❌ Universal content generation failed:', error);
      throw error;
    }
  }

  /**
   * Poll for generation status (for long-running generations)
   */
  async pollGenerationStatus(requestId: string): Promise<GenerationStatus> {
    try {
      const response = await fetch(`${this.baseUrl}/generate/status/${requestId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json() as GenerationStatus;

    } catch (error) {
      console.error('❌ Status polling failed:', error);
      throw error;
    }
  }

  /**
   * Get available templates (for explicit selection)
   */
  async getAvailableTemplates(): Promise<Array<{
    id: string;
    name: string;
    description: string;
    category: string;
    source: string;
  }>> {
    try {
      const response = await fetch(`${this.baseUrl}/templates`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json() as APIResponse<{
        templates: Array<{
          id: string;
          name: string;
          description: string;
          category: string;
          source: string;
        }>;
      }>;
      
      return data.data?.templates || [];

    } catch (error) {
      console.error('❌ Failed to fetch templates:', error);
      return [];
    }
  }

  /**
   * Get available style profiles
   */
  async getAvailableStyles(): Promise<Array<{
    id: string;
    name: string;
    description: string;
    category: string;
  }>> {
    try {
      const response = await fetch(`${this.baseUrl}/style-profiles`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json() as APIResponse<{
        styles: Array<{
          id: string;
          name: string;
          description: string;
          category: string;
        }>;
      }>;
      
      return data.data?.styles || [];

    } catch (error) {
      console.error('❌ Failed to fetch styles:', error);
      return [];
    }
  }
}

// React Hook for Universal Content Generation
export function useUniversalContentGeneration() {
  const api = new UniversalContentAPI();

  const generateContent = async (request: UniversalContentRequest): Promise<UniversalContentResponse> => {
    try {
      const result = await api.generateUniversalContent(request);
      
      toast({
        title: "Content Generated Successfully!",
        description: `Generated ${result.template.name} using ${result.approach.replace('_', ' ')}`,
      });

      return result;
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      toast({
        variant: "destructive",
        title: "Generation Failed",
        description: errorMessage,
      });

      throw error;
    }
  };

  const pollStatus = async (requestId: string): Promise<GenerationStatus> => {
    return await api.pollGenerationStatus(requestId);
  };

  const getTemplates = async () => {
    return await api.getAvailableTemplates();
  };

  const getStyles = async () => {
    return await api.getAvailableStyles();
  };

  return {
    generateContent,
    pollStatus,
    getTemplates,
    getStyles,
  };
}

// Enhanced Content Generation Hook with Real-time Updates
export function useEnhancedContentGeneration() {
  const { generateContent, pollStatus } = useUniversalContentGeneration();

  const generateWithStatusUpdates = async (
    request: UniversalContentRequest,
    onStatusUpdate?: (status: GenerationStatus) => void
  ): Promise<string> => {
    
    // Start generation
    const response = await generateContent(request);
    
    // If it's a simple response, return immediately
    if (response.metadata.confidence > 0.8) {
      // High confidence, likely immediate response
      // FIXED: Proper handling of template.content object
      return extractContentString(response.template.content);
    }

    // For complex generations, poll for status
    const requestId = `gen_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    return new Promise((resolve, reject) => {
      const pollInterval = setInterval(async () => {
        try {
          const status = await pollStatus(requestId);
          
          if (onStatusUpdate) {
            onStatusUpdate(status);
          }

          if (status.status === 'completed' && status.result) {
            clearInterval(pollInterval);
            resolve(status.result.content);
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            reject(new Error(status.error || 'Generation failed'));
          }
          
        } catch (error) {
          clearInterval(pollInterval);
          reject(error);
        }
      }, 2000); // Poll every 2 seconds

      // Timeout after 5 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        reject(new Error('Generation timeout'));
      }, 300000);
    });
  };

  return {
    generateWithStatusUpdates,
    generateContent,
  };
}

// FIXED: Helper function to extract content string from object
function extractContentString(content: Record<string, unknown>): string {
  // If template.content is an object, try to extract a string property or stringify it
  if (typeof content === 'string') {
    return content;
  } else if (
    typeof content === 'object' &&
    content !== null &&
    'content' in content &&
    typeof content.content === 'string'
  ) {
    return content.content;
  } else if (
    typeof content === 'object' &&
    content !== null &&
    'text' in content &&
    typeof content.text === 'string'
  ) {
    return content.text;
  } else if (
    typeof content === 'object' &&
    content !== null &&
    'body' in content &&
    typeof content.body === 'string'
  ) {
    return content.body;
  } else {
    // FIXED: Proper JSON stringification
    return JSON.stringify(content, null, 2);
  }
}

// Utility functions for the universal system
export const UniversalContentUtils = {
  /**
   * Analyze user input to suggest optimal parameters
   */
  analyzeUserRequest(userRequest: string): Partial<UniversalContentRequest> {
    const request = userRequest.toLowerCase();
    
    const suggestions: Partial<UniversalContentRequest> = {
      user_context: {}
    };

    // Detect expertise level
    if (request.includes('beginner') || request.includes('introduction') || request.includes('basics')) {
      suggestions.user_context!.expertise_level = 'beginner';
    } else if (request.includes('advanced') || request.includes('expert') || request.includes('deep dive')) {
      suggestions.user_context!.expertise_level = 'advanced';
    } else {
      suggestions.user_context!.expertise_level = 'intermediate';
    }

    // Detect domain
    const domains: Record<string, string[]> = {
      'ai': ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural', 'llm'],
      'programming': ['code', 'programming', 'development', 'software', 'api'],
      'gardening': ['garden', 'plant', 'grow', 'seed', 'soil', 'flower'],
      'cooking': ['cook', 'recipe', 'food', 'ingredient', 'kitchen', 'meal'],
      'business': ['business', 'startup', 'entrepreneur', 'marketing', 'sales'],
      'health': ['health', 'fitness', 'exercise', 'nutrition', 'wellness'],
      'politics': ['politics', 'policy', 'government', 'election', 'voting'],
      'finance': ['finance', 'money', 'investment', 'budget', 'financial']
    };

    for (const [domain, keywords] of Object.entries(domains)) {
      if (keywords.some(keyword => request.includes(keyword))) {
        suggestions.user_context!.domain = domain;
        break;
      }
    }

    // Detect content purpose
    if (request.includes('tutorial') || request.includes('how to') || request.includes('guide')) {
      suggestions.user_context!.content_purpose = 'tutorial';
    } else if (request.includes('analysis') || request.includes('compare') || request.includes('review')) {
      suggestions.user_context!.content_purpose = 'analysis';
    } else if (request.includes('explain') || request.includes('understand') || request.includes('what is')) {
      suggestions.user_context!.content_purpose = 'explanation';
    }

    return suggestions;
  },

  /**
   * Estimate reading time from word count
   */
  estimateReadingTime(wordCount: number): string {
    const wordsPerMinute = 200;
    const minutes = Math.ceil(wordCount / wordsPerMinute);
    
    if (minutes < 1) return '< 1 min read';
    if (minutes === 1) return '1 min read';
    if (minutes < 60) return `${minutes} min read`;
    
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m read`;
  },

  /**
   * Format content approach for display
   */
  formatApproach(approach: string): string {
    return approach
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  },

  /**
   * Validate content request before sending
   */
  validateContentRequest(request: UniversalContentRequest): { 
    isValid: boolean; 
    errors: string[]; 
  } {
    const errors: string[] = [];

    if (!request.user_request || request.user_request.trim().length === 0) {
      errors.push('User request is required');
    }

    if (request.user_request && request.user_request.length < 10) {
      errors.push('User request should be at least 10 characters long');
    }

    if (request.user_request && request.user_request.length > 2000) {
      errors.push('User request should be less than 2000 characters');
    }

    // Validate user_context if provided
    if (request.user_context) {
      const validExpertiseLevels = ['beginner', 'intermediate', 'advanced', 'expert'];
      if (request.user_context.expertise_level && 
          !validExpertiseLevels.includes(request.user_context.expertise_level)) {
        errors.push('Invalid expertise level');
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  },

  /**
   * Format response metadata for display
   */
  formatResponseMetadata(metadata: UniversalContentResponse['metadata']): {
    displayText: string;
    details: Record<string, string>;
  } {
    const details: Record<string, string> = {
      'Approach': this.formatApproach(metadata.template_source),
      'Category': metadata.category,
      'Confidence': `${Math.round(metadata.confidence * 100)}%`
    };

    if (metadata.estimated_length) {
      details['Length'] = metadata.estimated_length;
    }

    if (metadata.reading_time) {
      details['Reading Time'] = metadata.reading_time;
    }

    const displayText = `${details['Category']} • ${details['Confidence']} confidence ${details['Reading Time'] ? '• ' + details['Reading Time'] : ''}`;

    return { displayText, details };
  }
};

// Type guards for better type safety
export const TypeGuards = {
  isUniversalContentResponse(obj: unknown): obj is UniversalContentResponse {
    return (
      typeof obj === 'object' &&
      obj !== null &&
      'success' in obj &&
      'approach' in obj &&
      'template' in obj &&
      'generation_config' in obj &&
      'metadata' in obj
    );
  },

  isGenerationStatus(obj: unknown): obj is GenerationStatus {
    return (
      typeof obj === 'object' &&
      obj !== null &&
      'request_id' in obj &&
      'status' in obj
    );
  },

  isValidContentRequest(obj: unknown): obj is UniversalContentRequest {
    return (
      typeof obj === 'object' &&
      obj !== null &&
      'user_request' in obj &&
      typeof (obj as UniversalContentRequest).user_request === 'string'
    );
  }
};

// Error handling utilities
export class UniversalContentError extends Error {
  constructor(
    message: string,
    public code: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'UniversalContentError';
  }
}

export const ErrorHandler = {
  handleAPIError(error: unknown): UniversalContentError {
    if (error instanceof UniversalContentError) {
      return error;
    }

    if (error instanceof Error) {
      return new UniversalContentError(
        error.message,
        'API_ERROR',
        { originalError: error.name }
      );
    }

    return new UniversalContentError(
      'An unknown error occurred',
      'UNKNOWN_ERROR',
      { originalError: error }
    );
  },

  formatErrorForUser(error: UniversalContentError): string {
    switch (error.code) {
      case 'NETWORK_ERROR':
        return 'Network connection failed. Please check your internet connection.';
      case 'VALIDATION_ERROR':
        return 'Please check your input and try again.';
      case 'RATE_LIMIT_ERROR':
        return 'Too many requests. Please wait a moment and try again.';
      case 'GENERATION_TIMEOUT':
        return 'Content generation took too long. Please try a simpler request.';
      default:
        return error.message || 'Something went wrong. Please try again.';
    }
  }
};

export default UniversalContentAPI;