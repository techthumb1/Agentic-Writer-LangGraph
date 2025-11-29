// lib/api.ts
// Enterprise-grade API client with authentication and error handling

// Note: Commented out unused import to fix ESLint error
// import { API_ENDPOINTS } from './constants';

/**
 * Type definitions for better type safety
 */
export interface APIResponse<T> {
  success: boolean;
  data: T;
  error?: {
    message: string;
    code?: string;
  };
  requestId?: string;
}

export interface StyleProfile {
  id: string;
  name: string;
  description?: string;
  // Add other properties as needed
}

/**
 * Enterprise API Configuration
 */
const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  apiKey: process.env.NEXT_PUBLIC_LANGGRAPH_API_KEY || process.env.LANGGRAPH_API_KEY || 'prod_api_key_2025_secure_content_gen_v1',
  timeout: 30000, // 30 seconds
  retries: 3,
} as const;

/**
 * Enterprise API Error Class
 */
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public requestId?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * Type-safe error handling utility
 */
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  return 'Unknown error occurred';
}

/**
 * Enterprise HTTP Client
 */
class EnterpriseAPIClient {
  private readonly baseURL: string;
  private readonly apiKey: string;
  private readonly timeout: number;
  private readonly retries: number;

  constructor() {
    this.baseURL = API_CONFIG.baseURL;
    this.apiKey = API_CONFIG.apiKey;
    this.timeout = API_CONFIG.timeout;
    this.retries = API_CONFIG.retries;
    
    // Validate configuration
    if (!this.apiKey) {
      throw new Error('ENTERPRISE ERROR: API key is required');
    }
  }

  /**
   * Get enterprise headers with authentication
   */
  private getHeaders(additionalHeaders: Record<string, string> = {}): HeadersInit {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.apiKey}`,
      'X-Client': 'WriterzRoom-Enterprise',
      'X-Client-Version': '2.0.0',
      ...additionalHeaders,
    };
  }

  /**
   * Build full URL
   */
  private buildURL(endpoint: string): string {
    // Handle both relative and absolute endpoints
    if (endpoint.startsWith('http')) {
      return endpoint;
    }
    
    // Remove leading slash if present to avoid double slashes
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
    return `${this.baseURL}/${cleanEndpoint}`;
  }

  /**
   * Enterprise fetch with retry logic and error handling
   */
  private async fetchWithRetry(
    url: string,
    options: RequestInit = {},
    attempt: number = 1
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        headers: this.getHeaders(options.headers as Record<string, string>),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      
      // Retry on network errors (not on HTTP errors)
      if (attempt < this.retries && (error instanceof TypeError || (error as Error)?.name === 'AbortError')) {
        console.warn(`API call failed (attempt ${attempt}/${this.retries}), retrying...`, getErrorMessage(error));
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000)); // Exponential backoff
        return this.fetchWithRetry(url, options, attempt + 1);
      }
      
      throw error;
    }
  }

  /**
   * Process API response with enterprise error handling
   */
  private async processResponse<T>(response: Response): Promise<APIResponse<T>> {
    try {
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        
        throw new APIError(
          errorData.error?.message || `HTTP ${response.status} ${response.statusText}`,
          response.status,
          errorData.error?.code,
          errorData.requestId
        );
      }

      const data = await response.json();
      
      // Validate response structure
      if (typeof data !== 'object' || data === null) {
        throw new APIError('Invalid response format', 500);
      }

      return data as APIResponse<T>;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      
      throw new APIError(
        `Response processing failed: ${getErrorMessage(error)}`,
        500
      );
    }
  }

  /**
   * Generic GET request
   */
  async get<T>(endpoint: string, params?: URLSearchParams): Promise<APIResponse<T>> {
    const url = this.buildURL(endpoint);
    const fullURL = params ? `${url}?${params.toString()}` : url;
    
    const response = await this.fetchWithRetry(fullURL, {
      method: 'GET',
    });

    return this.processResponse<T>(response);
  }

  /**
   * Generic POST request
   */
  async post<T>(endpoint: string, data?: Record<string, unknown>): Promise<APIResponse<T>> {
    const url = this.buildURL(endpoint);
    
    const response = await this.fetchWithRetry(url, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });

    return this.processResponse<T>(response);
  }

  /**
   * Generic PUT request
   */
  async put<T>(endpoint: string, data?: Record<string, unknown>): Promise<APIResponse<T>> {
    const url = this.buildURL(endpoint);
    
    const response = await this.fetchWithRetry(url, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });

    return this.processResponse<T>(response);
  }

  /**
   * Generic DELETE request
   */
  async delete<T>(endpoint: string): Promise<APIResponse<T>> {
    const url = this.buildURL(endpoint);
    
    const response = await this.fetchWithRetry(url, {
      method: 'DELETE',
    });

    return this.processResponse<T>(response);
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<{ healthy: boolean; services: Record<string, boolean> }> {
    try {
      const response = await this.get<{ services?: Record<string, boolean> }>('/health');
      return {
        healthy: response.success,
        services: response.data?.services || {}
      };
    } catch {
      return {
        healthy: false,
        services: {}
      };
    }
  }
}

// Global API client instance
const apiClient = new EnterpriseAPIClient();

/**
 * Enterprise API Methods
 */

/**
 * Fetch style profiles with enterprise authentication
 */
export async function fetchStyleProfiles(params?: URLSearchParams): Promise<APIResponse<{
  items: StyleProfile[];
  pagination: Record<string, unknown>;
}>> {
  try {
    return await apiClient.get('/api/style-profiles', params);
  } catch (error) {
    if (error instanceof APIError) {
      console.error(`❌ Style profiles fetch failed: ${error.status} "${error.message}"`, error);
      throw error;
    }
    throw new APIError('Failed to fetch style profiles', 500);
  }
}

/**
 * Fetch templates with enterprise authentication
 */
export async function fetchTemplates(): Promise<APIResponse<{
  items: Record<string, unknown>[];
  count: number;
}>> {
  try {
    return await apiClient.get('/api/templates');
  } catch (error) {
    if (error instanceof APIError) {
      console.error(`❌ Templates fetch failed: ${error.status} "${error.message}"`, error);
      throw error;
    }
    throw new APIError('Failed to fetch templates', 500);
  }
}

/**
 * Generate content with enterprise authentication
 */
export async function generateContent(data: {
  template: string;
  style_profile: string;
  dynamic_parameters: Record<string, unknown>;
  priority?: number;
  timeout_seconds?: number;
}): Promise<APIResponse<{
  requestId: string;
  status: string;
  metadata: Record<string, unknown>;
}>> {
  try {
    return await apiClient.post('/api/generate', data);
  } catch (error) {
    if (error instanceof APIError) {
      console.error(`❌ Content generation failed: ${error.status} "${error.message}"`, error);
      throw error;
    }
    throw new APIError('Failed to generate content', 500);
  }
}

/**
 * Get generation status with enterprise authentication
 */
export async function getGenerationStatus(requestId: string): Promise<APIResponse<{
  requestId: string;
  status: string;
  progress: number;
  content: string;
  errors: string[];
  warnings: string[];
}>> {
  try {
    return await apiClient.get(`/api/generate/${requestId}`);
  } catch (error) {
    if (error instanceof APIError) {
      console.error(`❌ Status fetch failed: ${error.status} "${error.message}"`, error);
      throw error;
    }
    throw new APIError('Failed to fetch generation status', 500);
  }
}

/**
 * Cancel generation with enterprise authentication
 */
export async function cancelGeneration(requestId: string): Promise<APIResponse<{
  message: string;
}>> {
  try {
    return await apiClient.delete(`/api/generate/${requestId}`);
  } catch (error) {
    if (error instanceof APIError) {
      console.error(`❌ Cancellation failed: ${error.status} "${error.message}"`, error);
      throw error;
    }
    throw new APIError('Failed to cancel generation', 500);
  }
}

/**
 * Get dashboard stats with enterprise authentication
 */
export async function getDashboardStats(): Promise<APIResponse<{
  total: number;
  totalContent: number;
  drafts: number;
  published: number;
  views: number;
  recentContent: Record<string, unknown>[];
  recentActivity: Record<string, unknown>[];
}>> {
  try {
    return await apiClient.get('/api/dashboard/stats');
  } catch (error) {
    if (error instanceof APIError) {
      console.error(`❌ Dashboard stats fetch failed: ${error.status} "${error.message}"`, error);
      throw error;
    }
    throw new APIError('Failed to fetch dashboard stats', 500);
  }
}

/**
 * Get usage statistics (legacy compatibility)
 */
export async function getUsage(): Promise<{ used: number; limit: number; remaining: number }> {
  try {
    const response = await apiClient.get<{ published?: number }>('/api/dashboard/stats');
    return {
      used: response.data?.published || 0,
      limit: 25, // Default limit
      remaining: Math.max(0, 25 - (response.data?.published || 0))
    };
  } catch {
    console.warn('Usage stats unavailable, using defaults');
    return { used: 0, limit: 25, remaining: 25 };
  }
}

/**
 * Enterprise system status check
 */
export async function getSystemStatus(): Promise<APIResponse<{
  enterprise_mode: boolean;
  system_status: Record<string, unknown>;
  environment: Record<string, unknown>;
  validation: { all_systems_operational: boolean };
}>> {
  try {
    return await apiClient.get('/debug/enterprise-status');
  } catch (error) {
    if (error instanceof APIError) {
      console.error(`❌ System status check failed: ${error.status} "${error.message}"`, error);
      throw error;
    }
    throw new APIError('Failed to fetch system status', 500);
  }
}

// Export the client for advanced usage
export { apiClient, EnterpriseAPIClient };

// Default export for backwards compatibility
export default apiClient;