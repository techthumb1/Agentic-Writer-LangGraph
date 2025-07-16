// File: frontend/hooks/useMCP.ts
import { useState, useEffect, useCallback } from 'react';

// Strict Types for MCP integration
interface MCPServer {
  enabled: boolean;
  connected: boolean;
  tools_count: number;
}

interface MCPStatus {
  servers: Record<string, MCPServer>;
  total_tools: number;
  total_resources: number;
}

interface MCPTool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
  server: string;
}

interface MCPCapabilities {
  research: boolean;
  github: boolean;
  memory: boolean;
  filesystem: boolean;
  database: boolean;
}

interface MCPToolsResponse {
  tools: MCPTool[];
  capabilities: MCPCapabilities;
}

interface MCPToolCall {
  tool_name: string;
  arguments: Record<string, unknown>;
  namespace?: string;
}

interface MCPToolResponse {
  success: boolean;
  result?: unknown;
  error?: string;
  tool_name: string;
  server: string;
  execution_time: number;
}

interface MCPMemoryOperation {
  key: string;
  value?: string;
  namespace?: string;
}

interface MCPFileOperation {
  path: string;
  content?: string;
}

interface MCPSearchRequest {
  query: string;
  search_type?: 'web' | 'github';
  count?: number;
}

interface MCPAPIResponse {
  success: boolean;
  result?: unknown;
  error?: string;
  detail?: string;
  message?: string;
}

interface MCPAnalytics {
  publications: unknown[];
  research_history: unknown[];
  server_status: MCPStatus;
}

interface UseMCPReturn {
  // Status
  mcpStatus: MCPStatus | null;
  mcpTools: MCPTool[];
  mcpCapabilities: MCPCapabilities | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  refreshMCP: () => Promise<void>;
  callTool: (toolCall: MCPToolCall) => Promise<MCPToolResponse>;
  storeMemory: (operation: MCPMemoryOperation) => Promise<MCPAPIResponse>;
  recallMemory: (operation: Omit<MCPMemoryOperation, 'value'>) => Promise<MCPAPIResponse>;
  readFile: (path: string) => Promise<MCPAPIResponse>;
  writeFile: (operation: MCPFileOperation) => Promise<MCPAPIResponse>;
  search: (request: MCPSearchRequest) => Promise<MCPAPIResponse>;
  getAnalytics: () => Promise<MCPAnalytics>;
}

export const useMCP = (): UseMCPReturn => {
  const [mcpStatus, setMcpStatus] = useState<MCPStatus | null>(null);
  const [mcpTools, setMcpTools] = useState<MCPTool[]>([]);
  const [mcpCapabilities, setMcpCapabilities] = useState<MCPCapabilities | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleError = (error: unknown, context: string) => {
    console.error(`MCP Error in ${context}:`, error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    setError(`${context}: ${errorMessage}`);
  };

  const refreshMCP = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch status
      const statusResponse = await fetch('/api/mcp/status');
      if (!statusResponse.ok) {
        throw new Error('Failed to fetch MCP status');
      }
      const statusData: MCPStatus = await statusResponse.json();
      setMcpStatus(statusData);

      // Fetch tools
      const toolsResponse = await fetch('/api/mcp/tools');
      if (!toolsResponse.ok) {
        throw new Error('Failed to fetch MCP tools');
      }
      const toolsData: MCPToolsResponse = await toolsResponse.json();
      setMcpTools(toolsData.tools || []);
      setMcpCapabilities(toolsData.capabilities || null);

    } catch (err) {
      handleError(err, 'Refresh MCP');
    } finally {
      setLoading(false);
    }
  }, []);

  const callTool = useCallback(async (toolCall: MCPToolCall): Promise<MCPToolResponse> => {
    try {
      const response = await fetch('/api/mcp/tools/call', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(toolCall),
      });

      const data: MCPToolResponse = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Tool call failed');
      }

      return data;
    } catch (err) {
      handleError(err, 'Tool Call');
      throw err;
    }
  }, []);

  const storeMemory = useCallback(async (operation: MCPMemoryOperation): Promise<MCPAPIResponse> => {
    try {
      const response = await fetch('/api/mcp/memory/store', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(operation),
      });

      const data: MCPAPIResponse = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Memory store failed');
      }

      return data;
    } catch (err) {
      handleError(err, 'Memory Store');
      throw err;
    }
  }, []);

  const recallMemory = useCallback(async (operation: Omit<MCPMemoryOperation, 'value'>): Promise<MCPAPIResponse> => {
    try {
      const response = await fetch('/api/mcp/memory/recall', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(operation),
      });

      const data: MCPAPIResponse = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Memory recall failed');
      }

      return data;
    } catch (err) {
      handleError(err, 'Memory Recall');
      throw err;
    }
  }, []);

  const readFile = useCallback(async (path: string): Promise<MCPAPIResponse> => {
    try {
      const response = await fetch('/api/mcp/files/read', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ path }),
      });

      const data: MCPAPIResponse = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || data.error || 'File read failed');
      }

      return data;
    } catch (err) {
      handleError(err, 'File Read');
      throw err;
    }
  }, []);

  const writeFile = useCallback(async (operation: MCPFileOperation): Promise<MCPAPIResponse> => {
    try {
      const response = await fetch('/api/mcp/files/write', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(operation),
      });

      const data: MCPAPIResponse = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || data.error || 'File write failed');
      }

      return data;
    } catch (err) {
      handleError(err, 'File Write');
      throw err;
    }
  }, []);

  const search = useCallback(async (request: MCPSearchRequest): Promise<MCPAPIResponse> => {
    try {
      const response = await fetch('/api/mcp/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      const data: MCPAPIResponse = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Search failed');
      }

      return data;
    } catch (err) {
      handleError(err, 'Search');
      throw err;
    }
  }, []);

  const getAnalytics = useCallback(async (): Promise<MCPAnalytics> => {
    try {
      const response = await fetch('/api/mcp/analytics');
      const data: MCPAnalytics = await response.json();
      
      if (!response.ok) {
        throw new Error('Analytics fetch failed');
      }

      return data;
    } catch (err) {
      handleError(err, 'Analytics');
      throw err;
    }
  }, []);

  // Initialize on mount
  useEffect(() => {
    refreshMCP();
  }, [refreshMCP]);

  return {
    mcpStatus,
    mcpTools,
    mcpCapabilities,
    loading,
    error,
    refreshMCP,
    callTool,
    storeMemory,
    recallMemory,
    readFile,
    writeFile,
    search,
    getAnalytics,
  };
};

// File: frontend/utils/mcpUtils.ts
export const mcpUtils = {
  /**
   * Check if MCP is available and properly configured
   */
  isMCPAvailable: (mcpStatus: MCPStatus | null): boolean => {
    if (!mcpStatus || !mcpStatus.servers) return false;
    
    return Object.values(mcpStatus.servers).some(
      (server: MCPServer) => server.enabled && server.connected
    );
  },

  /**
   * Get available MCP capabilities
   */
  getAvailableCapabilities: (mcpCapabilities: MCPCapabilities | null): string[] => {
    if (!mcpCapabilities) return [];
    
    return Object.entries(mcpCapabilities)
      .filter(([, enabled]) => enabled)
      .map(([capability]) => capability);
  },

  /**
   * Check if a specific tool is available
   */
  isToolAvailable: (mcpTools: MCPTool[], toolName: string): boolean => {
    return mcpTools.some(tool => tool.name === toolName);
  },

  /**
   * Get tools by server
   */
  getToolsByServer: (mcpTools: MCPTool[], serverName: string): MCPTool[] => {
    return mcpTools.filter(tool => tool.server === serverName);
  },

  /**
   * Format MCP error for display
   */
  formatMCPError: (error: unknown): string => {
    if (typeof error === 'string') return error;
    if (error instanceof Error) return error.message;
    if (typeof error === 'object' && error !== null) {
      if ('message' in error && typeof error.message === 'string') return error.message;
      if ('detail' in error && typeof error.detail === 'string') return error.detail;
    }
    return 'Unknown MCP error';
  },

  /**
   * Generate MCP-enhanced generation request
   */
  createMCPEnhancedRequest: (
    baseRequest: Record<string, unknown>,
    mcpCapabilities: MCPCapabilities | null
  ): Record<string, unknown> => {
    const enhancedRequest: Record<string, unknown> = {
      ...baseRequest,
      mcp_enhanced: true,
      mcp_capabilities: mcpCapabilities,
      generation_mode: 'mcp_enhanced',
    };

    if (!mcpCapabilities) return enhancedRequest;

    // Add research enhancement if available
    if (mcpCapabilities.research) {
      enhancedRequest.research_enhanced = true;
    }

    // Add GitHub integration if available
    if (mcpCapabilities.github) {
      enhancedRequest.github_integration = true;
    }

    // Add memory context if available
    if (mcpCapabilities.memory) {
      enhancedRequest.memory_context = true;
    }

    return enhancedRequest;
  },

  /**
   * Extract content from MCP-enhanced response
   */
  extractMCPContent: (response: Record<string, unknown>): string => {
    // Priority order for content extraction
    const contentFields = [
      'content',
      'formatted_content',
      'edited_content',
      'draft_content',
      'result'
    ];

    for (const field of contentFields) {
      const value = response[field];
      if (value && typeof value === 'string') {
        return value;
      }
    }

    return '';
  },

  /**
   * Get MCP enhancement status from response
   */
  getMCPEnhancementStatus: (response: Record<string, unknown>): {
    enhanced: boolean;
    capabilities_used: string[];
    tools_used: string[];
    errors: string[];
  } => {
    const metadata = (response.metadata as Record<string, unknown>) || {};
    
    return {
      enhanced: Boolean(metadata.mcp_enhanced),
      capabilities_used: Array.isArray(metadata.mcp_capabilities) ? metadata.mcp_capabilities : [],
      tools_used: Array.isArray(metadata.mcp_tools_used) ? metadata.mcp_tools_used : [],
      errors: Array.isArray(metadata.errors) ? metadata.errors : []
    };
  },
};

// Export types for use in other components
export type {
  MCPServer,
  MCPStatus,
  MCPTool,
  MCPCapabilities,
  MCPToolCall,
  MCPToolResponse,
  MCPMemoryOperation,
  MCPFileOperation,
  MCPSearchRequest,
  MCPAPIResponse,
  MCPAnalytics,
  UseMCPReturn
};