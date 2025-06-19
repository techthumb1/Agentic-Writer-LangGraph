import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

// --- Types ---
export interface ContentItem {
  id: string;
  title: string;
  contentHtml: string;
  saved_path?: string;
  createdAt?: string;
  updatedAt?: string;
  metadata?: Record<string, unknown>;
}

export interface Template {
  id: string;
  name: string;
  description?: string;
  parameters: {
    name: string;
    label: string;
    type: 'text' | 'textarea' | 'number' | 'select' | 'checkbox';
    default?: string | number | boolean;
    placeholder?: string;
    options?: string[];
    required?: boolean;
  }[];
}

export interface StyleProfile {
  id: string;
  name: string;
  description?: string;
  settings?: Record<string, unknown>;
}

export interface UserProfile {
  id: string;
  email: string;
  name?: string;
  role?: string;
}

export interface GenerationStatus {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  error?: string;
}

export interface AnalyticsData {
  views: number;
  clicks: number;
  topTemplates: Record<string, number>;
}

// --- fetchApi wrapper ---
async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(errorData.message || `HTTP error! status: ${response.status}`) as Error & {
        status?: number;
        data?: unknown;
      };
      error.status = response.status;
      error.data = errorData;
      throw error;
    }

    const contentType = response.headers.get('content-type');
    if (contentType?.includes('application/json')) {
      return await response.json();
    } else {
      return await response.text() as unknown as T;
    }
  } catch (error: unknown) {
    if (typeof error === 'object' && error !== null && !('status' in error)) {
      (error as Error).message = 'Network error. Please check your connection.';
    }
    throw error;
  }
}

// --- Query Keys ---
export const queryKeys = {
  all: ['api'] as const,
  content: () => [...queryKeys.all, 'content'] as const,
  contentList: (filters?: Record<string, string>) => [...queryKeys.content(), 'list', filters] as const,
  contentDetail: (id: string) => [...queryKeys.content(), 'detail', id] as const,
  templates: () => [...queryKeys.all, 'templates'] as const,
  templatesList: () => [...queryKeys.templates(), 'list'] as const,
  templateDetail: (id: string) => [...queryKeys.templates(), 'detail', id] as const,
  styleProfiles: () => [...queryKeys.all, 'styleProfiles'] as const,
  user: () => [...queryKeys.all, 'user'] as const,
  userProfile: () => [...queryKeys.user(), 'profile'] as const,
  analytics: () => [...queryKeys.all, 'analytics'] as const,
  generation: () => [...queryKeys.all, 'generation'] as const,
  generationStatus: (id: string) => [...queryKeys.generation(), 'status', id] as const,
};
// --- Content API Hooks ---

export function useContentList(filters?: Record<string, string>) {
  return useQuery<ContentItem[]>({
    queryKey: queryKeys.contentList(filters),
    queryFn: () =>
      fetchApi<ContentItem[]>('/content', {
        method: 'GET',
        ...(filters && {
          body: JSON.stringify({ params: new URLSearchParams(filters).toString() }),
        }),
      }),
    staleTime: 5 * 60 * 1000,
  });
}

export function useContentDetail(id: string) {
  return useQuery<ContentItem>({
    queryKey: queryKeys.contentDetail(id),
    queryFn: () => fetchApi<ContentItem>(`/content/${id}`),
    enabled: !!id,
  });
}

export function useCreateContent() {
  const queryClient = useQueryClient();

  return useMutation<ContentItem, Error, Partial<ContentItem>>({
    mutationKey: ['createContent'],
    mutationFn: (data) =>
      fetchApi<ContentItem>('/content', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.content() });
    },
  });
}

export function useUpdateContent() {
  const queryClient = useQueryClient();

  return useMutation<ContentItem, Error, { id: string; data: Partial<ContentItem> }>({
    mutationKey: ['updateContent'],
    mutationFn: ({ id, data }) =>
      fetchApi<ContentItem>(`/content/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    onSuccess: (data, variables) => {
      queryClient.setQueryData(queryKeys.contentDetail(variables.id), data);
      queryClient.invalidateQueries({ queryKey: queryKeys.contentList() });
    },
  });
}

export function useDeleteContent() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationKey: ['deleteContent'],
    mutationFn: (id) =>
      fetchApi<void>(`/content/${id}`, {
        method: 'DELETE',
      }),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: queryKeys.contentDetail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.contentList() });
    },
  });
}
// --- Templates API Hooks ---

export function useTemplatesList() {
  return useQuery<Template[]>({
    queryKey: queryKeys.templatesList(),
    queryFn: () => fetchApi<Template[]>('/templates'),
    staleTime: 15 * 60 * 1000,
  });
}

export function useTemplateDetail(id: string) {
  return useQuery<Template>({
    queryKey: queryKeys.templateDetail(id),
    queryFn: () => fetchApi<Template>(`/templates/${id}`),
    enabled: !!id,
  });
}

// --- Content Generation ---

// Define GenerationPayload type according to your API requirements
export interface GenerationPayload {
  templateId: string;
  parameters: Record<string, string | number | boolean>;
  styleProfileId?: string;
  [key: string]: unknown;
}

export function useGenerateContent() {
  const queryClient = useQueryClient();

  return useMutation<ContentItem, Error, GenerationPayload>({
    mutationKey: ['generateContent'],
    mutationFn: (data) =>
      fetchApi<ContentItem>('/generate', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.content() });
    },
  });
}

export function useGenerationStatus(id: string) {
  return useQuery<GenerationStatus>({
    queryKey: queryKeys.generationStatus(id),
    queryFn: () => fetchApi<GenerationStatus>(`/generate/status/${id}`),
    enabled: !!id,
    refetchInterval: (query) => {
      const data = query.state.data as GenerationStatus | undefined;
      return data?.status === 'completed' || data?.status === 'failed' ? false : 2000;
    },
  });
}

// --- Style Profiles ---

export function useStyleProfiles() {
  return useQuery<StyleProfile[]>({
    queryKey: queryKeys.styleProfiles(),
    queryFn: () => fetchApi<StyleProfile[]>('/style-profiles'),
    staleTime: 30 * 60 * 1000,
  });
}

// --- User & Analytics ---

export function useUserProfile() {
  return useQuery<UserProfile>({
    queryKey: queryKeys.userProfile(),
    queryFn: () => fetchApi<UserProfile>('/user/profile'),
    staleTime: 10 * 60 * 1000,
  });
}

export function useAnalytics(timeRange: string = '7d') {
  return useQuery<AnalyticsData>({
    queryKey: [...queryKeys.analytics(), timeRange],
    queryFn: () => fetchApi<AnalyticsData>(`/analytics?range=${timeRange}`),
    staleTime: 5 * 60 * 1000,
  });
}
