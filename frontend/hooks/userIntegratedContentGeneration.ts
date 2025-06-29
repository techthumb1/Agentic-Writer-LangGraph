// File: frontend/hooks/useIntegratedContentGeneration.ts
import { useState, useCallback, useEffect, useRef } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

// Enhanced type definitions for the integrated system
interface ContentRequirements {
  category?: string;
  difficulty?: 'simple' | 'intermediate' | 'advanced';
  complexity?: 'simple' | 'moderate' | 'complex';
  wordCount?: number;
  sections?: string[];
  tone?: string;
  audience?: string;
}

interface StyleRequirements {
  voice?: 'formal' | 'casual' | 'technical' | 'conversational';
  format?: 'article' | 'blog' | 'report' | 'tutorial' | 'guide';
  citations?: boolean;
  examples?: boolean;
}

interface StructureRequirements {
  hasIntroduction?: boolean;
  hasConclusion?: boolean;
  numberOfSections?: number;
  includeTableOfContents?: boolean;
  headingLevels?: number[];
}

interface LanguageRequirements {
  language?: string;
  locale?: string;
  terminology?: 'technical' | 'general' | 'industry-specific';
  readingLevel?: 'elementary' | 'intermediate' | 'advanced' | 'expert';
}

interface FormattingRequirements {
  format?: 'markdown' | 'html' | 'plain' | 'json';
  includeMetadata?: boolean;
  includeSEO?: boolean;
  codeBlocks?: boolean;
}

interface UserParameters {
  include_code?: boolean;
  include_images?: boolean;
  research_depth?: 'shallow' | 'moderate' | 'deep';
  auto_publish?: boolean;
  publication_config?: PublicationConfig;
  maxTokens?: number;
  temperature?: number;
  model?: string;
}

interface PublicationConfig {
  platform?: string;
  schedule?: string;
  tags?: string[];
  visibility?: 'public' | 'private' | 'unlisted';
}

interface WorkflowType {
  type: 'simple' | 'comprehensive' | 'research_heavy' | 'technical' | 'visual' | 'publication_ready';
  name: string;
  description: string;
  estimated_time: string;
  best_for: string[];
}

interface EnhancedGenerationRequest {
  prompt: {
    content_requirements: ContentRequirements;
    style_requirements: StyleRequirements;
    structure_requirements: StructureRequirements;
    language_requirements: LanguageRequirements;
    formatting_requirements: FormattingRequirements;
    user_parameters: UserParameters;
  };
  preferences: {
    maxTokens: number;
    temperature: number;
    model: string;
  };
  workflow: {
    workflow_type: string;
    auto_detect: boolean;
    async_processing: boolean;
    priority: number;
  };
  user_id?: string;
  session_id?: string;
}

interface ContentSection {
  title: string;
  content: string;
  wordCount: number;
}

interface AgentStep {
  agent: string;
  action: string;
  result: string;
  timestamp: string;
}

interface GenerationMetadata {
  generation_id: string;
  model_used: string;
  workflow_type: string;
  tokens_consumed: number;
  generation_time: number;
  total_processing_time: number;
  agent_steps: AgentStep[];
  cache_hits: number;
  word_count: number;
  sections: ContentSection[];
  images?: ImageData[];
  code_blocks?: CodeBlock[];
  published_urls?: string[];
  infrastructure_stats: {
    cache_hits: number;
    model_calls: number;
    workflow_type: string;
  };
}

interface ImageData {
  url: string;
  alt: string;
  caption?: string;
  width?: number;
  height?: number;
}

interface CodeBlock {
  language: string;
  code: string;
  description?: string;
  lineNumbers?: boolean;
}

interface GenerationResult {
  generation_id: string;
  content: string;
  metadata: GenerationMetadata;
  status: 'success' | 'error' | 'partial';
  errors?: string[];
}

interface AgentUpdate {
  agent: string;
  action: string;
  timestamp: string;
  result?: string;
}

interface GenerationProgress {
  generation_id: string;
  status: 'queued' | 'processing' | 'completed' | 'error';
  progress: number;
  current_step: string;
  agent_updates: AgentUpdate[];
  estimated_completion?: string;
  result?: GenerationResult;
  error?: string;
}

interface CacheSystem {
  hit_rate: number;
  total_entries: number;
  memory_usage: string;
}

interface JobQueue {
  pending_jobs: number;
  active_jobs: number;
  completed_jobs: number;
}

interface ModelRegistry {
  available_models: string[];
  model_usage: Record<string, number>;
}

interface SemanticSearch {
  indexed_documents: number;
  search_performance: number;
}

interface InfrastructureStats {
  cache_system: CacheSystem;
  job_queue: JobQueue;
  model_registry: ModelRegistry;
  semantic_search: SemanticSearch;
  active_generations: number;
  total_connections: number;
}

interface Template {
  id: string;
  title: string;
  description?: string;
  category: string;
  parameters?: Record<string, unknown>;
}

interface StyleProfile {
  id: string;
  name: string;
  description: string;
  category: string;
  settings?: Record<string, unknown>;
}

interface SemanticSearchResult {
  id: string;
  content: string;
  score: number;
  metadata: Record<string, unknown>;
}

interface SimilarContentResult {
  id: string;
  content: string;
  similarity_score: number;
  metadata: Record<string, unknown>;
}


interface BatchStatus {
  batch_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  completed_count: number;
  total_count: number;
  results: GenerationResult[];
  errors?: string[];
}

interface WebSocketMessage {
  type: 'status_update' | 'agent_update' | 'completion' | 'error' | 'pong';
  generation_id?: string;
  status?: string;
  progress?: number;
  current_step?: string;
  agent?: string;
  action?: string;
  timestamp?: string;
  result?: GenerationResult | string;
  error?: string;
}

interface SystemStats {
  queue_size: number;
  cache_hit_rate: number;
  active_generations: number;
  memory_usage?: string;
  cpu_usage?: number;
}

interface TemplateData {
  title: string;
  description?: string;
  category: string;
  parameters?: Record<string, unknown>;
  content_structure?: Record<string, unknown>;
}

interface StyleProfileData {
  name: string;
  description: string;
  category: string;
  settings: Record<string, unknown>;
  voice_characteristics?: Record<string, unknown>;
}

interface GenerationStats {
  total_generations: number;
  successful_generations: number;
  failed_generations: number;
  average_generation_time: number;
  token_usage: number;
  model_distribution: Record<string, number>;
}

interface ModelUsageStats {
  model_name: string;
  usage_count: number;
  total_tokens: number;
  average_response_time: number;
  success_rate: number;
}

export const useIntegratedContentGeneration = () => {
  const [generationProgress, setGenerationProgress] = useState<GenerationProgress | null>(null);
  const [currentResult, setCurrentResult] = useState<GenerationResult | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const queryClient = useQueryClient();

  // Fetch available workflows
  const {
    data: availableWorkflows,
    isLoading: workflowsLoading,
    error: workflowsError,
  } = useQuery<WorkflowType[]>({
    queryKey: ['workflows', 'available'],
    queryFn: async () => {
      const response = await fetch('/api/workflows/available', {
        headers: {
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch workflows');
      }
      const data = await response.json();
      return data.workflows;
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
  });

  // Fetch infrastructure stats
  const {
    data: infrastructureStats,
  } = useQuery<InfrastructureStats>({
    queryKey: ['infrastructure', 'stats'],
    queryFn: async () => {
      const response = await fetch('/api/infrastructure/stats', {
        headers: {
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch infrastructure stats');
      }
      return response.json();
    },
    refetchInterval: 30000, // Refresh every 30 seconds
    staleTime: 15000, // Consider stale after 15 seconds
  });

  // Enhanced generation mutation
  const generateContentMutation = useMutation({
    mutationFn: async (request: EnhancedGenerationRequest): Promise<GenerationResult> => {
      const response = await fetch('/api/generate/enhanced', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Enhanced content generation failed');
      }

      const result = await response.json();
      
      // If async processing, set up WebSocket connection
      if (request.workflow.async_processing && result.generation_id) {
        setupWebSocketConnection(result.generation_id);
        return result; // This will be the queued response
      }

      return result;
    },
    onSuccess: (result) => {
      if (result.status === 'success' || result.status === 'partial') {
        setCurrentResult(result);
      }
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
      queryClient.invalidateQueries({ queryKey: ['infrastructure', 'stats'] });
    },
    onError: (error) => {
      console.error('Enhanced content generation failed:', error);
    },
  });

  // WebSocket connection for real-time updates
  const setupWebSocketConnection = useCallback((generationId: string) => {
    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/generation/${generationId}`;
    
    wsRef.current = new WebSocket(wsUrl);
    
    wsRef.current.onopen = () => {
      setIsConnected(true);
      console.log(`WebSocket connected for generation: ${generationId}`);
    };
    
    wsRef.current.onmessage = (event) => {
      try {
        const update: WebSocketMessage = JSON.parse(event.data);
        
        switch (update.type) {
          case 'status_update':
            setGenerationProgress(prev => ({
              ...prev,
              generation_id: update.generation_id || '',
              status: (update.status as 'queued' | 'processing' | 'completed' | 'error') || 'processing',
              progress: update.progress || 0,
              current_step: update.current_step || '',
              agent_updates: prev?.agent_updates || [],
            }));
            break;
            
          case 'agent_update':
            setGenerationProgress(prev => prev ? {
              ...prev,
              agent_updates: [...prev.agent_updates, {
                agent: update.agent || '',
                action: update.action || '',
                timestamp: update.timestamp || new Date().toISOString(),
                result: typeof update.result === 'string' ? update.result : undefined,
              }],
            } : null);
            break;
            
          case 'completion':
            setGenerationProgress(prev => prev ? {
              ...prev,
              status: 'completed',
              progress: 100,
              result: typeof update.result === 'object' ? update.result as GenerationResult : undefined,
            } : null);
            if (typeof update.result === 'object') {
              setCurrentResult(update.result as GenerationResult);
            }
            break;
            
          case 'error':
            setGenerationProgress(prev => prev ? {
              ...prev,
              status: 'error',
              error: update.error,
            } : null);
            break;
            
          case 'pong':
            // Keep-alive response
            break;
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
    
    wsRef.current.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket connection closed');
    };
    
    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };
    
    // Send periodic ping to keep connection alive
    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);
    
    // Cleanup interval when connection closes
    const currentWs = wsRef.current;
    const originalOnClose = currentWs.onclose;
    currentWs.onclose = (event) => {
      clearInterval(pingInterval);
      if (originalOnClose) {
        originalOnClose.call(currentWs, event);
      }
    };
    
  }, []);

  // Cancel generation
  const cancelGeneration = useCallback((generationId: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'cancel',
        generation_id: generationId,
      }));
    }
  }, []);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Fetch templates and style profiles (using your existing system)
  const {
    data: templates,
    isLoading: templatesLoading,
  } = useQuery<Template[]>({
    queryKey: ['templates', 'list'],
    queryFn: async () => {
      const response = await fetch('/api/templates/list', {
        headers: {
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch templates');
      }
      const data = await response.json();
      return data.templates;
    },
    staleTime: 5 * 60 * 1000,
  });

  const {
    data: styleProfiles,
    isLoading: profilesLoading,
  } = useQuery<StyleProfile[]>({
    queryKey: ['style-profiles', 'list'],
    queryFn: async () => {
      const response = await fetch('/api/style-profiles/list', {
        headers: {
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch style profiles');
      }
      const data = await response.json();
      return data.profiles;
    },
    staleTime: 5 * 60 * 1000,
  });

  // Enhanced semantic search
  const searchSemantic = useCallback(async (query: string, contentType?: string): Promise<SemanticSearchResult[]> => {
    const response = await fetch('/api/search/semantic', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
      },
      body: JSON.stringify({
        query,
        content_type: contentType,
        limit: 10,
      }),
    });

    if (!response.ok) {
      throw new Error('Semantic search failed');
    }

    const data = await response.json();
    return data.results;
  }, []);

  // Find similar content
  const findSimilarContent = useCallback(async (content: string, threshold = 0.7): Promise<SimilarContentResult[]> => {
    const response = await fetch('/api/search/similar', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
      },
      body: JSON.stringify({
        content,
        threshold,
        limit: 5,
      }),
    });

    if (!response.ok) {
      throw new Error('Similar content search failed');
    }

    const data = await response.json();
    return data.similar_content;
  }, []);

  // Generate content with enhanced options
  const generateContent = useCallback(async (request: EnhancedGenerationRequest) => {
    try {
      // Reset previous state
      setGenerationProgress(null);
      setCurrentResult(null);
      
      const result = await generateContentMutation.mutateAsync(request);
      return result;
    } catch (error) {
      throw error;
    }
  }, [generateContentMutation]);

  // Batch generation
  const generateBatch = useCallback(async (requests: EnhancedGenerationRequest[]): Promise<BatchStatus> => {
    const response = await fetch('/api/batch/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
      },
      body: JSON.stringify(requests),
    });

    if (!response.ok) {
      throw new Error('Batch generation failed');
    }

    return response.json();
  }, []);

  // Get batch status
  const getBatchStatus = useCallback(async (batchId: string): Promise<BatchStatus> => {
    const response = await fetch(`/api/batch/${batchId}/status`, {
      headers: {
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to get batch status');
    }

    return response.json();
  }, []);

  // Publish content
  const publishContent = useCallback(async (contentId: string, publicationConfig: PublicationConfig) => {
    const response = await fetch('/api/publish/content', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
      },
      body: JSON.stringify({
        content_id: contentId,
        publication_config: publicationConfig,
      }),
    });

    if (!response.ok) {
      throw new Error('Content publication failed');
    }

    return response.json();
  }, []);

  // Get analytics
  const getAnalytics = useCallback(async (timeframe = '7d'): Promise<GenerationStats> => {
    const response = await fetch(`/api/analytics/generation-stats?timeframe=${timeframe}`, {
      headers: {
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch analytics');
    }

    return response.json();
  }, []);

  // Get model usage stats
  const getModelUsage = useCallback(async (timeframe = '7d'): Promise<ModelUsageStats[]> => {
    const response = await fetch(`/api/analytics/model-usage?timeframe=${timeframe}`, {
      headers: {
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch model usage');
    }

    return response.json();
  }, []);

  // Clear cache (admin function)
  const clearCache = useCallback(async (cacheType = 'all') => {
    const response = await fetch('/api/cache/clear', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
      },
      body: JSON.stringify({ cache_type: cacheType }),
    });

    if (!response.ok) {
      throw new Error('Failed to clear cache');
    }

    // Invalidate queries after cache clear
    queryClient.invalidateQueries({ queryKey: ['infrastructure', 'stats'] });
    
    return response.json();
  }, [queryClient]);

  // Reset generation state
  const resetGeneration = useCallback(() => {
    setGenerationProgress(null);
    setCurrentResult(null);
    generateContentMutation.reset();
    
    // Close WebSocket if open
    if (wsRef.current) {
      wsRef.current.close();
    }
  }, [generateContentMutation]);

  // Get optimal workflow suggestion
  const suggestWorkflow = useCallback((contentRequirements: ContentRequirements, userParameters: UserParameters): string => {
    if (!availableWorkflows) return 'comprehensive';

    // Simple logic to suggest workflow based on requirements
    if (userParameters.include_code || contentRequirements.category?.includes('technical')) {
      return 'technical';
    }
    
    if (userParameters.include_images || contentRequirements.category?.includes('visual')) {
      return 'visual';
    }
    
    if (contentRequirements.difficulty === 'advanced' || userParameters.research_depth === 'deep') {
      return 'research_heavy';
    }
    
    if (userParameters.auto_publish || userParameters.publication_config) {
      return 'publication_ready';
    }
    
    if (contentRequirements.complexity === 'simple') {
      return 'simple';
    }
    
    return 'comprehensive';
  }, [availableWorkflows]);

  // Validate template parameters
  const validateTemplate = useCallback(async (templateData: TemplateData) => {
    const response = await fetch('/api/templates/validate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
      },
      body: JSON.stringify(templateData),
    });

    if (!response.ok) {
      throw new Error('Template validation failed');
    }

    return response.json();
  }, []);

  // Get generation status
  const getGenerationStatus = useCallback(async (generationId: string): Promise<GenerationProgress> => {
    const response = await fetch(`/api/generation/status/${generationId}`, {
      headers: {
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to get generation status');
    }

    return response.json();
  }, []);

  return {
    // Data
    availableWorkflows,
    templates,
    styleProfiles,
    infrastructureStats,
    currentResult,
    generationProgress,

    // Connection status
    isConnected,
    isWebSocketActive: wsRef.current?.readyState === WebSocket.OPEN,

    // Loading states
    isLoading: workflowsLoading || templatesLoading || profilesLoading,
    isGenerating: generateContentMutation.isPending || generationProgress?.status === 'processing',
    
    // Error states
    error: workflowsError || generateContentMutation.error,
    generationError: generationProgress?.error,

    // Generation functions
    generateContent,
    generateBatch,
    cancelGeneration,
    resetGeneration,
    
    // Status and monitoring
    getGenerationStatus,
    getBatchStatus,
    
    // Search functions
    searchSemantic,
    findSimilarContent,
    
    // Publishing
    publishContent,
    
    // Analytics
    getAnalytics,
    getModelUsage,
    
    // Workflow optimization
    suggestWorkflow,
    
    // Template management
    validateTemplate,
    
    // Admin functions
    clearCache,
    
    // Real-time progress
    currentStep: generationProgress?.current_step || 'idle',
    progress: generationProgress?.progress || 0,
    agentUpdates: generationProgress?.agent_updates || [],
    
    // Infrastructure insights
    cacheHitRate: infrastructureStats?.cache_system?.hit_rate || 0,
    activeJobs: infrastructureStats?.job_queue?.active_jobs || 0,
    pendingJobs: infrastructureStats?.job_queue?.pending_jobs || 0,
    activeConnections: infrastructureStats?.active_generations || 0,
  };
};

// Specialized hook for real-time system monitoring
export const useSystemMonitoring = () => {
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/system`;
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      setIsConnected(true);
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'system_stats') {
          setSystemStats(data);
        }
      } catch (error) {
        console.error('Error parsing system stats:', error);
      }
    };
    
    ws.onclose = () => {
      setIsConnected(false);
    };
    
    ws.onerror = (error) => {
      console.error('System WebSocket error:', error);
      setIsConnected(false);
    };
    
    return () => {
      ws.close();
    };
  }, []);

  return {
    systemStats,
    isConnected,
    queueSize: systemStats?.queue_size || 0,
    cacheHitRate: systemStats?.cache_hit_rate || 0,
    activeGenerations: systemStats?.active_generations || 0,
  };
};

// Hook for template and style profile management
export const useContentAssetManagement = () => {
  const queryClient = useQueryClient();

  // Create template
  const createTemplate = useCallback(async (templateData: TemplateData) => {
    const response = await fetch('/api/templates/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
      },
      body: JSON.stringify(templateData),
    });

    if (!response.ok) {
      throw new Error('Failed to create template');
    }

    const result = await response.json();
    
    // Invalidate templates list
    queryClient.invalidateQueries({ queryKey: ['templates', 'list'] });
    
    return result;
  }, [queryClient]);

  // Update template
  const updateTemplate = useCallback(async (templateId: string, templateData: TemplateData) => {
    const response = await fetch(`/api/templates/${templateId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
      },
      body: JSON.stringify(templateData),
    });

    if (!response.ok) {
      throw new Error('Failed to update template');
    }

    const result = await response.json();
    
    // Invalidate related queries
    queryClient.invalidateQueries({ queryKey: ['templates'] });
    
    return result;
  }, [queryClient]);

  // Create style profile
  const createStyleProfile = useCallback(async (profileData: StyleProfileData) => {
    const response = await fetch('/api/style-profiles/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
      },
      body: JSON.stringify(profileData),
    });

    if (!response.ok) {
      throw new Error('Failed to create style profile');
    }

    const result = await response.json();
    
    // Invalidate style profiles list
    queryClient.invalidateQueries({ queryKey: ['style-profiles', 'list'] });
    
    return result;
  }, [queryClient]);

  // Update style profile
  const updateStyleProfile = useCallback(async (profileId: string, profileData: StyleProfileData) => {
    const response = await fetch(`/api/style-profiles/${profileId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
      },
      body: JSON.stringify(profileData),
    });

    if (!response.ok) {
      throw new Error('Failed to update style profile');
    }

    const result = await response.json();
    
    // Invalidate related queries
    queryClient.invalidateQueries({ queryKey: ['style-profiles'] });
    
    return result;
  }, [queryClient]);

  return {
    createTemplate,
    updateTemplate,
    createStyleProfile,
    updateStyleProfile,
  };
};

// Hook for analytics and reporting
export const useAnalyticsDashboard = () => {
  const [timeframe, setTimeframe] = useState('7d');

  const {
    data: generationStats,
    isLoading: statsLoading,
  } = useQuery<GenerationStats>({
    queryKey: ['analytics', 'generation-stats', timeframe],
    queryFn: async () => {
      const response = await fetch(`/api/analytics/generation-stats?timeframe=${timeframe}`, {
        headers: {
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch generation stats');
      }
      return response.json();
    },
    refetchInterval: 60000, // Refresh every minute
  });

  const {
    data: modelUsageStats,
    isLoading: modelStatsLoading,
  } = useQuery<ModelUsageStats[]>({
    queryKey: ['analytics', 'model-usage', timeframe],
    queryFn: async () => {
      const response = await fetch(`/api/analytics/model-usage?timeframe=${timeframe}`, {
        headers: {
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch model usage stats');
      }
      return response.json();
    },
    refetchInterval: 60000,
  });

  return {
    generationStats,
    modelUsageStats,
    isLoading: statsLoading || modelStatsLoading,
    timeframe,
    setTimeframe,
  };
};