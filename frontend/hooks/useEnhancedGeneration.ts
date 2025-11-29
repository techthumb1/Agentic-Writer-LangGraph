// frontend/hooks/useEnhancedGeneration.ts
"use client";

import { useState, useCallback, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';

interface GenerationParams {
  template: string
  style_profile: string
  dynamic_parameters?: Record<string, unknown>
  priority?: number
  timeout_seconds?: number
  generation_mode?: 'standard' | 'premium' | 'enterprise'
  platform?: string
  topic?: string
  audience?: string
  tags?: string[]
  use_mock?: boolean
  generation_settings?: {
    quality_mode?: 'fast' | 'balanced' | 'premium'
    max_tokens?: number
    temperature?: number
    auto_save?: boolean
    backupFrequency?: string
  }
}

interface GenerationResult {
  content: string;
  metadata: {
    generation_id: string;
    template_id: string;
    style_profile: string;
    completed_agents: string[];
    failed_agents: string[];
    generation_time: string;
    word_count: number;
    seo_metadata?: Record<string, unknown>;
    innovation_report?: {
      techniques_used: string[];
      innovation_level: string;
      creative_risk_score: number;
    };
    [key: string]: unknown;
  };
  quality_score: {
    overall: number;
    completeness: number;
    coherence: number;
    style_adherence: number;
    technical_accuracy: number;
  };
}

interface GenerationResponse {
  success: boolean;
  content?: string;
  generation_id?: string;
  request_id?: string;
  metadata?: Record<string, unknown>;
  data?: {
    request_id?: string;
    status?: string;
    content?: string;
    metadata?: GenerationResult['metadata'];
  };
  quality_score?: GenerationResult['quality_score'];
  error?: string;
  errors?: string[];
}

interface GenerationStatusResponse {
  success: boolean;
  data: {
    request_id: string;
    status: 'queued' | 'pending' | 'running' | 'completed' | 'failed';
    progress?: number;
    current_agent?: string;
    estimated_completion?: string;
    content?: string;
    error?: string;
    metadata?: Record<string, unknown>;
  };
}

interface GenerationState {
  isGenerating: boolean;
  progress: number;
  currentStep: string;
  currentAgent: string;
  error: string | null;
  result: GenerationResult | null;
  request_id: string | null;
  qualityScore: GenerationResult['quality_score'] | null;
}

export function useEnhancedGeneration() {
  const [state, setState] = useState<GenerationState>({
    isGenerating: false,
    progress: 0,
    currentStep: '',
    currentAgent: '',
    error: null,
    result: null,
    request_id: null,
    qualityScore: null,
  });

  const [isPolling, setIsPolling] = useState(false);

  const startGeneration = async (params: GenerationParams): Promise<GenerationResponse> => {
    const sessionRes = await fetch('/api/auth/session')
    const session = await sessionRes.json()

    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'X-User-ID': session?.user?.id || ''
      },
      body: JSON.stringify({
        // ✅ Fixed field names
        template: params.template,
        style_profile: params.style_profile,

        // ✅ Moved to top level with required quality_mode
        generation_settings: params.generation_settings || {
          max_tokens: 8000,
          temperature: 0.7,
          quality_mode: 'balanced'
        },

        // Top-level request fields
        topic: params.topic,
        audience: params.audience,
        platform: params.platform,
        tags: params.tags,
        priority: params.priority ?? 1,
        timeout_seconds: params.timeout_seconds ?? 1000,
        generation_mode: params.generation_mode || 'standard',

        // Separate dynamic parameters
        dynamic_parameters: {
          ...params.dynamic_parameters,
          user_id: session?.user?.id
        },
      }),
    })

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Generation failed: ${response.statusText}`);
    }

    return await response.json();
  };
  
  const checkStatus = async (request_id: string): Promise<GenerationStatusResponse> => {
    const response = await fetch(`/api/generate/status/${request_id}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_LANGGRAPH_API_KEY || 'dev-key'}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to check generation status');
    }

    return await response.json();
  };

  const pollStatus = useCallback(async (request_id: string) => {
    try {
      const statusResponse = await checkStatus(request_id);
      
      const { status, progress = 0, current_agent, content, error, metadata } = statusResponse.data;
      
      setState(prev => ({
        ...prev,
        progress,
        currentAgent: current_agent || '',
        currentStep: getStepFromAgent(current_agent || ''),
      }));

      if (status === 'completed' && content) {
        setState(prev => ({
          ...prev,
          isGenerating: false,
          progress: 100,
          currentStep: 'Complete',
          currentAgent: 'completed',
          result: {
            content: content as string,
            metadata: metadata as GenerationResult['metadata'] || {} as GenerationResult['metadata'],
            quality_score: {} as GenerationResult['quality_score'],
          },
        }));
        setIsPolling(false);
      } else if (status === 'failed') {
        setState(prev => ({
          ...prev,
          isGenerating: false,
          error: error || 'Generation failed',
        }));
        setIsPolling(false);
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        isGenerating: false,
        error: error instanceof Error ? error.message : 'Failed to check status',
      }));
      setIsPolling(false);
      console.log('Poll error:', error);
    }
  }, []);

  const getStepFromAgent = (agent: string): string => {
    const agentSteps: Record<string, string> = {
      'initialize': 'Initializing...',
      'load_templates': 'Loading templates...',
      'check_cache': 'Checking cache...',
      'plan': 'Planning content...',
      'research': 'Researching topic...',
      'write': 'Writing content...',
      'edit': 'Editing and refining...',
      'seo_optimize': 'Optimizing for SEO...',
      'finalize': 'Finalizing content...',
      'cache_result': 'Saving results...',
      'completed': 'Complete!',
    };
    
    return agentSteps[agent] || `Processing: ${agent}...`;
  };

  useEffect(() => {
    if (isPolling && state.request_id) {
      const interval = setInterval(() => {
        pollStatus(state.request_id!);
      }, 1500);

      return () => clearInterval(interval);
    }
  }, [isPolling, state.request_id, pollStatus]);

  const mutation = useMutation({
    mutationFn: startGeneration,
    onMutate: () => {
      setState(prev => ({
        ...prev,
        isGenerating: true,
        progress: 0,
        currentStep: 'Starting...',
        currentAgent: 'initialize',
        error: null,
        result: null,
        request_id: null,
        qualityScore: null,
      }));
    },

    onSuccess: (data) => {
      console.log('🔍 [HOOK] Generation API Response:', data);
      
      // ✅ FIX: Extract request_id FIRST before anything else
      const requestId = data.request_id || data.generation_id || data.data?.request_id;
      
      if (!requestId) {
        console.error('❌ [HOOK] No request_id in response:', data);
        setState(prev => ({
          ...prev,
          isGenerating: false,
          error: 'No request ID received from server',
        }));
        return;
      }
      
      console.log('✅ [HOOK] Extracted request_id:', requestId);
      
      if (data.success) {
        const content = data.content || data.data?.content;
        
        if (content) {
          // Content found - mark as completed
          setState(prev => ({
            ...prev,
            isGenerating: false,
            progress: 100,
            currentStep: 'Complete',
            currentAgent: 'completed',
            result: {
              content: content,
              metadata: (data.metadata || data.data?.metadata || {}) as GenerationResult['metadata'],
              quality_score: data.quality_score || {} as GenerationResult['quality_score'],
            },
            qualityScore: data.quality_score || null,
            request_id: requestId,
          }));
          
          console.log('✅ [HOOK] Content generation completed successfully:', content.length, 'characters');
          
        } else {
          // Async processing - start polling with requestId
          setState(prev => ({
            ...prev,
            request_id: requestId,
            currentStep: 'Queued for processing...',
            currentAgent: 'queued',
          }));
          setIsPolling(true);
          
          console.log('🔄 [HOOK] Starting polling for request:', requestId);
        }
      } else {
        console.error('❌ [HOOK] API returned success: false:', data);
        setState(prev => ({
          ...prev,
          isGenerating: false,
          error: data.error || 'Generation failed',
          request_id: requestId,
        }));
      }
    },

    onError: (error) => {
      setState(prev => ({
        ...prev,
        isGenerating: false,
        error: error instanceof Error ? error.message : 'Generation failed',
      }));
      setIsPolling(false);
    },
  });

  const startGenerationWrapper = useCallback((params: GenerationParams) => {
    mutation.mutate(params);
  }, [mutation]);

  const cancelGeneration = useCallback(() => {
    setIsPolling(false);
    setState(prev => ({
      ...prev,
      isGenerating: false,
      progress: 0,
      error: null,
    }));
  }, []);

  const resetGeneration = useCallback(() => {
    setIsPolling(false);
    setState({
      isGenerating: false,
      progress: 0,
      currentStep: '',
      currentAgent: '',
      error: null,
      result: null,
      request_id: null,
      qualityScore: null,
    });
  }, []);

  return {
    ...state,
    startGeneration: startGenerationWrapper,
    cancelGeneration,
    resetGeneration,
    isLoading: mutation.isPending,
    hasQualityScore: !!state.qualityScore,
    completedAgents: state.result?.metadata?.completed_agents || [],
    failedAgents: state.result?.metadata?.failed_agents || [],
    innovationReport: state.result?.metadata?.innovation_report,
  };
}