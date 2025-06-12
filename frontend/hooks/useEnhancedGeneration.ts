// frontend/hooks/useEnhancedGeneration.ts
"use client";

import { useState, useCallback } from 'react';
import { useMutation } from '@tanstack/react-query';

interface GenerationParams {
  templateId: string;
  styleProfile: string;
  customParameters?: Record<string, unknown>;
}

interface GenerationResult {
  content: string;
  metadata: {
    templateName: string;
    styleProfile: string;
    generatedAt: string;
    tokensUsed?: number;
    model?: string;
  };
}

interface GenerationState {
  isGenerating: boolean;
  progress: number;
  currentStep: string;
  error: string | null;
  result: GenerationResult | null;
}

export function useEnhancedGeneration() {
  const [state, setState] = useState<GenerationState>({
    isGenerating: false,
    progress: 0,
    currentStep: '',
    error: null,
    result: null,
  });

  // Simulate the generation API call
  const generateContent = async (params: GenerationParams): Promise<GenerationResult> => {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(`Generation failed: ${response.statusText}`);
    }

    return response.json();
  };

  const mutation = useMutation({
    mutationFn: generateContent,
    onMutate: () => {
      setState(prev => ({
        ...prev,
        isGenerating: true,
        progress: 0,
        error: null,
        result: null,
      }));
    },
    onSuccess: (data) => {
      setState(prev => ({
        ...prev,
        isGenerating: false,
        progress: 100,
        result: data,
      }));
    },
    onError: (error) => {
      setState(prev => ({
        ...prev,
        isGenerating: false,
        error: error instanceof Error ? error.message : 'Generation failed',
      }));
    },
  });

  const startGeneration = useCallback((params: GenerationParams) => {
    mutation.mutate(params);
  }, [mutation]);

  const cancelGeneration = useCallback(() => {
    // In a real implementation, you'd cancel the API request
    setState(prev => ({
      ...prev,
      isGenerating: false,
      progress: 0,
      error: null,
    }));
  }, []);

  const resetGeneration = useCallback(() => {
    setState({
      isGenerating: false,
      progress: 0,
      currentStep: '',
      error: null,
      result: null,
    });
  }, []);

  return {
    ...state,
    startGeneration,
    cancelGeneration,
    resetGeneration,
    isLoading: mutation.isPending,
  };
}