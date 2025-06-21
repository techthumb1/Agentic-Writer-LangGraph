// frontend/hooks/useEnhancedGeneration.ts
"use client";

import { useState, useCallback, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';

interface GenerationParams {
  template: string;  // Changed from templateId to match backend
  style_profile: string;  // Changed to match backend
  dynamic_parameters?: Record<string, unknown>;  // Changed to match backend
}

interface GenerationResult {
  content: string;
  metadata: {
    template?: string;
    style_profile?: string;
    generated_at?: string;
    word_count?: number;
    model?: string;
    [key: string]: unknown;
  };
}

interface GenerationResponse {
  request_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  content?: string;
  metadata?: GenerationResult['metadata'];
  progress?: number;
  errors?: string[];
  warnings?: string[];
}

interface GenerationState {
  isGenerating: boolean;
  progress: number;
  currentStep: string;
  error: string | null;
  result: GenerationResult | null;
  requestId: string | null;
}

export function useEnhancedGeneration() {
  const [state, setState] = useState<GenerationState>({
    isGenerating: false,
    progress: 0,
    currentStep: '',
    error: null,
    result: null,
    requestId: null,
  });

  const [isPolling, setIsPolling] = useState(false);

  // Start generation
  const startGeneration = async (params: GenerationParams): Promise<GenerationResponse> => {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Generation failed: ${response.statusText}`);
    }

    const json = await response.json();
    return json.data; // Return the data field from the response
  };

  // Check generation status
  const checkStatus = async (requestId: string): Promise<GenerationResponse> => {
    const response = await fetch(`/api/generate?request_id=${requestId}`);
    
    if (!response.ok) {
      throw new Error('Failed to check generation status');
    }

    const json = await response.json();
    return json.data;
  };

  // Polling function
  const pollStatus = useCallback(async (requestId: string) => {
    try {
      const status = await checkStatus(requestId);
      
      setState(prev => ({
        ...prev,
        progress: (status.progress || 0) * 100,
        currentStep: getStepFromProgress(status.progress || 0),
      }));

      if (status.status === 'completed' && status.content) {
        setState(prev => ({
          ...prev,
          isGenerating: false,
          progress: 100,
          currentStep: 'Complete',
          result: {
            content: status.content!,
            metadata: status.metadata || {},
          },
        }));
        setIsPolling(false);
      } else if (status.status === 'failed') {
        setState(prev => ({
          ...prev,
          isGenerating: false,
          error: status.errors?.join(', ') || 'Generation failed',
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

  // Convert progress to step name
  const getStepFromProgress = (progress: number): string => {
    if (progress < 0.2) return 'Researching...';
    if (progress < 0.5) return 'Planning...';
    if (progress < 0.8) return 'Writing...';
    if (progress < 0.95) return 'Editing...';
    if (progress < 1.0) return 'Formatting...';
    return 'Complete';
  };

  // Polling effect
  useEffect(() => {
    if (isPolling && state.requestId) {
      const interval = setInterval(() => {
        pollStatus(state.requestId!);
      }, 2000); // Poll every 2 seconds

      return () => clearInterval(interval);
    }
  }, [isPolling, state.requestId, pollStatus]);

  const mutation = useMutation({
    mutationFn: startGeneration,
    onMutate: () => {
      setState(prev => ({
        ...prev,
        isGenerating: true,
        progress: 0,
        currentStep: 'Starting...',
        error: null,
        result: null,
        requestId: null,
      }));
    },
    onSuccess: (data) => {
      setState(prev => ({
        ...prev,
        requestId: data.request_id,
        currentStep: 'Initializing...',
      }));
      setIsPolling(true);
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
      error: null,
      result: null,
      requestId: null,
    });
  }, []);

  return {
    ...state,
    startGeneration: startGenerationWrapper,
    cancelGeneration,
    resetGeneration,
    isLoading: mutation.isPending,
  };
}