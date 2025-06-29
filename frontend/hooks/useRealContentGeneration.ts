// File: frontend/hooks/useRealContentGeneration.ts
import { useState, useCallback, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

interface GenerationRequest {
  templateId: string;
  styleProfileId: string;
  parameters: Record<string, unknown>;
  userPreferences?: {
    maxTokens?: number;
    temperature?: number;
    model?: string;
  };
}

interface GenerationResult {
  id: string;
  content: string;
  metadata: {
    templateUsed: string;
    styleProfileUsed: string;
    generatedAt: string;
    wordCount: number;
    sections: Array<{
      title: string;
      content: string;
      wordCount: number;
    }>;
    modelUsed: string;
    tokensConsumed: number;
    generationTime: number;
    agentSteps: Array<{
      agent: string;
      action: string;
      result: string;
      timestamp: string;
    }>;
  };
  status: 'success' | 'error' | 'partial';
  errors?: string[];
}

interface Template {
  id: string;
  title: string;
  description?: string;
  category: string;
}

interface StyleProfile {
  id: string;
  name: string;
  description: string;
  category: string;
}

interface TemplateInput {
  title: string;
  description?: string;
  category: string;
}

interface StyleProfileInput {
  name: string;
  description: string;
  category: string;
}

interface GenerationStatus {
  isGenerating: boolean;
  progress: number;
  currentStep: string;
  estimatedTimeRemaining?: number;
}

export const useRealContentGeneration = () => {
  const [generationStatus, setGenerationStatus] = useState<GenerationStatus>({
    isGenerating: false,
    progress: 0,
    currentStep: 'idle',
  });
  const [currentResult, setCurrentResult] = useState<GenerationResult | null>(null);
  const queryClient = useQueryClient();

  // Fetch available templates
  const {
    data: templates,
    isLoading: templatesLoading,
    error: templatesError,
  } = useQuery<Template[]>({
    queryKey: ['templates'],
    queryFn: async () => {
      const response = await fetch('/api/generate-content?action=templates');
      if (!response.ok) {
        throw new Error('Failed to fetch templates');
      }
      const data = await response.json();
      return data.templates;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Fetch available style profiles
  const {
    data: styleProfiles,
    isLoading: profilesLoading,
    error: profilesError,
  } = useQuery<StyleProfile[]>({
    queryKey: ['style-profiles'],
    queryFn: async () => {
      const response = await fetch('/api/generate-content?action=style-profiles');
      if (!response.ok) {
        throw new Error('Failed to fetch style profiles');
      }
      const data = await response.json();
      return data.styleProfiles;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Fetch template parameters
  const fetchTemplateParameters = useCallback(async (templateId: string) => {
    const response = await fetch(`/api/generate-content?action=template-parameters&templateId=${templateId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch template parameters');
    }
    const data = await response.json();
    return data.parameters;
  }, []);

  // Generation mutation
  const generateContentMutation = useMutation({
    mutationFn: async (request: GenerationRequest): Promise<GenerationResult> => {
      setGenerationStatus({
        isGenerating: true,
        progress: 0,
        currentStep: 'initializing',
      });

      const response = await fetch('/api/generate-content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Content generation failed');
      }

      // Simulate progress updates (in a real implementation, you'd use WebSockets or Server-Sent Events)
      const progressSteps = [
        { progress: 20, step: 'researching' },
        { progress: 40, step: 'writing' },
        { progress: 60, step: 'editing' },
        { progress: 80, step: 'optimizing' },
        { progress: 100, step: 'finalizing' },
      ];

      for (const { progress, step } of progressSteps) {
        setGenerationStatus(prev => ({
          ...prev,
          progress,
          currentStep: step,
        }));
        await new Promise(resolve => setTimeout(resolve, 500)); // Simulate processing time
      }

      const result = await response.json();
      
      setGenerationStatus({
        isGenerating: false,
        progress: 100,
        currentStep: 'completed',
      });

      return result;
    },
    onSuccess: (result) => {
      setCurrentResult(result);
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['generation-history'] });
      queryClient.invalidateQueries({ queryKey: ['usage-stats'] });
    },
    onError: (error) => {
      setGenerationStatus({
        isGenerating: false,
        progress: 0,
        currentStep: 'error',
      });
      console.error('Content generation failed:', error);
    },
  });

  // Fetch generation history
  const {
    data: generationHistory,
  } = useQuery({
    queryKey: ['generation-history'],
    queryFn: async () => {
      const response = await fetch('/api/generate-content?action=generation-history');
      if (!response.ok) {
        throw new Error('Failed to fetch generation history');
      }
      const data = await response.json();
      return data.history;
    },
    staleTime: 1 * 60 * 1000, // 1 minute
  });

  // Real-time progress tracking (if implementing WebSocket)
  useEffect(() => {
    if (!generationStatus.isGenerating) return;

    // This would be replaced with actual WebSocket connection
    // const ws = new WebSocket('ws://localhost:8000/ws/generation-progress');
    // ws.onmessage = (event) => {
    //   const data = JSON.parse(event.data);
    //   setGenerationStatus(prev => ({
    //     ...prev,
    //     progress: data.progress,
    //     currentStep: data.currentStep,
    //     estimatedTimeRemaining: data.estimatedTimeRemaining,
    //   }));
    // };
    // return () => ws.close();
  }, [generationStatus.isGenerating]);

  // Generate content function
  const generateContent = useCallback(
    async (request: GenerationRequest) => {
      try {
        const result = await generateContentMutation.mutateAsync(request);
        return result;
      } catch (error) {
        throw error;
      }
    },
    [generateContentMutation]
  );

  // Validate parameters function
  const validateParameters = useCallback(
    (templateId: string) => {
      const template = templates?.find(t => t.id === templateId);
      if (!template) {
        return { valid: false, errors: ['Template not found'] };
      }

      // This would include actual parameter validation logic
      // based on the template's parameter schema
      return { valid: true, errors: [] };
    },
    [templates]
  );

  // Save generated content
  const saveContent = useCallback(async (content: GenerationResult, title?: string) => {
    const response = await fetch('/api/content/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...content,
        title: title || `Generated Content - ${new Date().toLocaleDateString()}`,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to save content');
    }

    return response.json();
  }, []);

  // Export content
  const exportContent = useCallback(async (content: GenerationResult, format: 'markdown' | 'html' | 'pdf' = 'markdown') => {
    const response = await fetch('/api/content/export', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content: content.content,
        format,
        metadata: content.metadata,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to export content');
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `content-${content.id}.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, []);

  // Get usage statistics
  const getUsageStats = useCallback(async (timeframe: 'day' | 'week' | 'month' = 'month') => {
    const response = await fetch(`/api/analytics/usage?timeframe=${timeframe}`);
    if (!response.ok) {
      throw new Error('Failed to fetch usage statistics');
    }
    return response.json();
  }, []);

  // Reset generation state
  const resetGeneration = useCallback(() => {
    setGenerationStatus({
      isGenerating: false,
      progress: 0,
      currentStep: 'idle',
    });
    setCurrentResult(null);
    generateContentMutation.reset();
  }, [generateContentMutation]);

  return {
    // Data
    templates,
    styleProfiles,
    generationHistory,
    currentResult,

    // Status
    generationStatus,
    isLoading: templatesLoading || profilesLoading,
    error: templatesError || profilesError || generateContentMutation.error,

    // Functions
    generateContent,
    fetchTemplateParameters,
    validateParameters,
    saveContent,
    exportContent,
    getUsageStats,
    resetGeneration,

    // Mutation state
    isGenerating: generateContentMutation.isPending || generationStatus.isGenerating,
    generationError: generateContentMutation.error,
  };
};

// Custom hook for template management
export const useTemplateManagement = () => {
  const queryClient = useQueryClient();

  const createTemplate = useMutation({
    mutationFn: async (templateData: TemplateInput) => {
      const response = await fetch('/api/templates/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(templateData),
      });

      if (!response.ok) {
        throw new Error('Failed to create template');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });

  const updateTemplate = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: TemplateInput }) => {
      const response = await fetch(`/api/templates/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Failed to update template');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });

  const deleteTemplate = useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(`/api/templates/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete template');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });

  return {
    createTemplate: createTemplate.mutateAsync,
    updateTemplate: updateTemplate.mutateAsync,
    deleteTemplate: deleteTemplate.mutateAsync,
    isCreating: createTemplate.isPending,
    isUpdating: updateTemplate.isPending,
    isDeleting: deleteTemplate.isPending,
  };
};

// Custom hook for style profile management
export const useStyleProfileManagement = () => {
  const queryClient = useQueryClient();

  const createStyleProfile = useMutation({
    mutationFn: async (profileData: StyleProfileInput) => {
      const response = await fetch('/api/style-profiles/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData),
      });

      if (!response.ok) {
        throw new Error('Failed to create style profile');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['style-profiles'] });
    },
  });

  const updateStyleProfile = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: StyleProfileInput }) => {
      const response = await fetch(`/api/style-profiles/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Failed to update style profile');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['style-profiles'] });
    },
  });

  const deleteStyleProfile = useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(`/api/style-profiles/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete style profile');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['style-profiles'] });
    },
  });

  return {
    createStyleProfile: createStyleProfile.mutateAsync,
    updateStyleProfile: updateStyleProfile.mutateAsync,
    deleteStyleProfile: deleteStyleProfile.mutateAsync,
    isCreating: createStyleProfile.isPending,
    isUpdating: updateStyleProfile.isPending,
    isDeleting: deleteStyleProfile.isPending,
  };
};