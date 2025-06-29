// frontend/hooks/useEnhancedGeneration.ts
"use client";

import { useState, useCallback, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';

interface GenerationParams {
  template: string;
  style_profile: string; 
  dynamic_parameters?: Record<string, unknown>;
  priority?: number;
  timeout_seconds?: number;
  generation_mode?: 'standard' | 'premium' | 'enterprise';
}

interface GenerationPreferences {
  maxTokens?: number;
  temperature?: number; 
  model?: string;
}

interface EnterpriseGenerationRequest {
  prompt: {
    content_requirements: {
      title: string;
      sections: string[];
      category: string;
      difficulty?: string;
      target_audience?: string;
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
      preferred_phrases?: string[];
      avoid_phrases?: string[];
    };
    formatting_requirements: {
      markdown_enabled: boolean;
      emoji_usage: string;
      code_block_style?: string;
      quote_style?: string;
    };
    user_parameters: Record<string, unknown>;
  };
  preferences: GenerationPreferences;
  workflow: string;
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
  metadata?: GenerationResult['metadata'];
  quality_score?: GenerationResult['quality_score'];
  generation_id?: string;
  error?: string;
  errors?: string[];
}

interface GenerationStatusResponse {
  generation_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  current_agent?: string;
  estimated_completion?: string;
  content?: string;
  error?: string;
  metadata?: Record<string, unknown>;
}

interface GenerationState {
  isGenerating: boolean;
  progress: number;
  currentStep: string;
  currentAgent: string;
  error: string | null;
  result: GenerationResult | null;
  generationId: string | null;
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
    generationId: null,
    qualityScore: null,
  });

  const [isPolling, setIsPolling] = useState(false);

  // Convert frontend params to enterprise backend format
  const convertToEnterpriseRequest = (params: GenerationParams): EnterpriseGenerationRequest => {
    const dynamicParams = params.dynamic_parameters || {};
    
    return {
      prompt: {
        content_requirements: {
          title: (dynamicParams.topic as string) || 'Untitled Content',
          sections: (dynamicParams.sections as string[]) || [],
          category: (dynamicParams.category as string) || 'general',
          difficulty: (dynamicParams.difficulty as string) || 'intermediate',
          target_audience: (dynamicParams.audience as string) || 'general',
        },
        style_requirements: {
          tone: (dynamicParams.tone as string) || 'professional',
          voice: (dynamicParams.voice as string) || 'authoritative',
          formality: (dynamicParams.formality as string) || 'formal',
          perspective: (dynamicParams.perspective as string) || 'third-person',
          technical_level: (dynamicParams.technical_level as string) || 'intermediate',
        },
        structure_requirements: {
          introduction_style: (dynamicParams.introduction_style as string) || 'hook',
          paragraph_length: (dynamicParams.paragraph_length as string) || 'medium',
          use_headings: (dynamicParams.use_headings as boolean) ?? true,
          use_bullet_points: (dynamicParams.use_bullet_points as boolean) ?? true,
          include_examples: (dynamicParams.include_examples as boolean) ?? true,
          include_analogies: (dynamicParams.include_analogies as boolean) ?? false,
        },
        language_requirements: {
          vocabulary_level: (dynamicParams.vocabulary_level as string) || 'intermediate',
          sentence_complexity: (dynamicParams.sentence_complexity as string) || 'mixed',
          use_jargon: (dynamicParams.use_jargon as boolean) ?? false,
          preferred_phrases: (dynamicParams.preferred_phrases as string[]) || [],
          avoid_phrases: (dynamicParams.avoid_phrases as string[]) || [],
        },
        formatting_requirements: {
          markdown_enabled: (dynamicParams.markdown_enabled as boolean) ?? true,
          emoji_usage: (dynamicParams.emoji_usage as string) || 'none',
          code_block_style: (dynamicParams.code_block_style as string),
          quote_style: (dynamicParams.quote_style as string),
        },
        user_parameters: {
          template: params.template,
          style_profile: params.style_profile,
          ...dynamicParams,
        },
      },
      preferences: {
        maxTokens: (dynamicParams.max_tokens as number) || 2000,
        temperature: (dynamicParams.temperature as number) || 0.7,
        model: (dynamicParams.model as string) || 'gpt-4-turbo',
      },
      workflow: 'content_generation',
    };
  };

  // Start generation with enterprise backend
  const startGeneration = async (params: GenerationParams): Promise<GenerationResponse> => {
    const enterpriseRequest = convertToEnterpriseRequest(params);
    
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_LANGGRAPH_API_KEY || 'dev-key'}`,
      },
      body: JSON.stringify(enterpriseRequest),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || `Generation failed: ${response.statusText}`);
    }

    return await response.json();
  };

  // Check generation status using enterprise endpoint
  const checkStatus = async (generationId: string): Promise<GenerationStatusResponse> => {
    const response = await fetch(`/api/generation/${generationId}`, {
      headers: {
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_LANGGRAPH_API_KEY || 'dev-key'}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to check generation status');
    }

    return await response.json();
  };

  // Enhanced polling with agent tracking
  const pollStatus = useCallback(async (generationId: string) => {
    try {
      const status = await checkStatus(generationId);
      
      setState(prev => ({
        ...prev,
        progress: status.progress,
        currentAgent: status.current_agent || '',
        currentStep: getStepFromAgent(status.current_agent || ''),
      }));

      if (status.status === 'completed' && status.content) {
        setState(prev => ({
          ...prev,
          isGenerating: false,
          progress: 100,
          currentStep: 'Complete',
          currentAgent: 'completed',
          result: {
            content: status.content!,
            metadata: status.metadata as GenerationResult['metadata'] || {} as GenerationResult['metadata'],
            quality_score: {} as GenerationResult['quality_score'], // Would come from metadata
          },
        }));
        setIsPolling(false);
      } else if (status.status === 'failed') {
        setState(prev => ({
          ...prev,
          isGenerating: false,
          error: status.error || 'Generation failed',
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
    }
  }, []);

  // Convert agent name to user-friendly step
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

  // Polling effect with enterprise intervals
  useEffect(() => {
    if (isPolling && state.generationId) {
      const interval = setInterval(() => {
        pollStatus(state.generationId!);
      }, 1500); // Poll every 1.5 seconds for better UX

      return () => clearInterval(interval);
    }
  }, [isPolling, state.generationId, pollStatus]);

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
        generationId: null,
        qualityScore: null,
      }));
    },
    onSuccess: (data) => {
      if (data.success) {
        if (data.content) {
          // Immediate completion
          setState(prev => ({
            ...prev,
            isGenerating: false,
            progress: 100,
            currentStep: 'Complete',
            currentAgent: 'completed',
            result: {
              content: data.content!,
              metadata: data.metadata || {} as GenerationResult['metadata'],
              quality_score: data.quality_score || {} as GenerationResult['quality_score'],
            },
            qualityScore: data.quality_score || null,
            generationId: data.generation_id || null,
          }));
        } else if (data.generation_id) {
          // Async processing - start polling
          setState(prev => ({
            ...prev,
            generationId: data.generation_id!,
            currentStep: 'Queued for processing...',
            currentAgent: 'queued',
          }));
          setIsPolling(true);
        }
      } else {
        setState(prev => ({
          ...prev,
          isGenerating: false,
          error: data.error || 'Generation failed',
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
      generationId: null,
      qualityScore: null,
    });
  }, []);

  return {
    ...state,
    startGeneration: startGenerationWrapper,
    cancelGeneration,
    resetGeneration,
    isLoading: mutation.isPending,
    // Additional enterprise features
    hasQualityScore: !!state.qualityScore,
    completedAgents: state.result?.metadata?.completed_agents || [],
    failedAgents: state.result?.metadata?.failed_agents || [],
    innovationReport: state.result?.metadata?.innovation_report,
  };
}