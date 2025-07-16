// File: frontend/components/mcp/MCPDashboard.tsx
import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, 
  XCircle, 
  Activity, 
  Database, 
  Search, 
  FileText,
  Brain,
  GitBranch,
  BarChart3,
  RefreshCw,
  AlertCircle
} from 'lucide-react';

// Types for MCP integration
interface MCPServer {
  enabled: boolean;
  connected: boolean;
  tools_count: number;
}

interface MCPTool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
  server: string;
}

interface MCPStatus {
  servers: Record<string, MCPServer>;
  total_tools: number;
  total_resources: number;
}

interface MCPCapabilities {
  research: boolean;
  github: boolean;
  memory: boolean;
  filesystem: boolean;
  database: boolean;
}

interface MCPDashboardProps {
  onToolCall?: (toolName: string, args: Record<string, unknown>) => void;
  onRefresh?: () => void;
}

// Custom UI Components (simplified versions)
const Card: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`bg-white rounded-lg border shadow-sm ${className}`}>
    {children}
  </div>
);

const CardHeader: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`px-6 py-4 border-b ${className}`}>
    {children}
  </div>
);

const CardTitle: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <h3 className={`text-lg font-semibold ${className}`}>
    {children}
  </h3>
);

const CardContent: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`px-6 py-4 ${className}`}>
    {children}
  </div>
);

const Badge: React.FC<{ 
  children: React.ReactNode; 
  variant?: 'default' | 'destructive' | 'outline' | 'secondary';
  className?: string;
}> = ({ children, variant = 'default', className = '' }) => {
  const variantClasses = {
    default: 'bg-blue-100 text-blue-800',
    destructive: 'bg-red-100 text-red-800',
    outline: 'bg-transparent border text-gray-700',
    secondary: 'bg-gray-100 text-gray-700'
  };
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variantClasses[variant]} ${className}`}>
      {children}
    </span>
  );
};

const Button: React.FC<{
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'default' | 'outline' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  disabled?: boolean;
}> = ({ 
  children, 
  onClick, 
  variant = 'default', 
  size = 'md', 
  className = '',
  disabled = false
}) => {
  const variantClasses = {
    default: 'bg-blue-600 hover:bg-blue-700 text-white',
    outline: 'border border-gray-300 hover:bg-gray-50 text-gray-700',
    destructive: 'bg-red-600 hover:bg-red-700 text-white'
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };
  
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        inline-flex items-center justify-center rounded-md font-medium transition-colors
        ${variantClasses[variant]} ${sizeClasses[size]} ${className}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      {children}
    </button>
  );
};

const Alert: React.FC<{ 
  children: React.ReactNode; 
  variant?: 'default' | 'destructive';
  className?: string;
}> = ({ children, variant = 'default', className = '' }) => {
  const variantClasses = {
    default: 'border-blue-200 bg-blue-50 text-blue-800',
    destructive: 'border-red-200 bg-red-50 text-red-800'
  };
  
  return (
    <div className={`border rounded-md p-4 ${variantClasses[variant]} ${className}`}>
      {children}
    </div>
  );
};

const AlertDescription: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`text-sm ${className}`}>
    {children}
  </div>
);

const MCPDashboard: React.FC<MCPDashboardProps> = ({ onToolCall, onRefresh }) => {
  const [mcpStatus, setMcpStatus] = useState<MCPStatus | null>(null);
  const [mcpTools, setMcpTools] = useState<MCPTool[]>([]);
  const [mcpCapabilities, setMcpCapabilities] = useState<MCPCapabilities | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMCPStatus();
    fetchMCPTools();
  }, []);

  const fetchMCPStatus = async () => {
    try {
      const response = await fetch('/api/mcp/status');
      const data = await response.json();
      
      if (response.ok) {
        setMcpStatus(data);
      } else {
        setError(data.error || 'Failed to fetch MCP status');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Network error fetching MCP status';
      setError(errorMessage);
    }
  };

  const fetchMCPTools = async () => {
    try {
      const response = await fetch('/api/mcp/tools');
      const data = await response.json();
      
      if (response.ok) {
        setMcpTools(data.tools || []);
        setMcpCapabilities(data.capabilities || {});
      } else {
        setError(data.error || 'Failed to fetch MCP tools');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Network error fetching MCP tools';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    setError(null);
    await fetchMCPStatus();
    await fetchMCPTools();
    onRefresh?.();
  };

  const getServerIcon = (serverName: string) => {
    switch (serverName) {
      case 'filesystem': return <FileText className="w-4 h-4" />;
      case 'web_search': return <Search className="w-4 h-4" />;
      case 'github': return <GitBranch className="w-4 h-4" />;
      case 'memory': return <Brain className="w-4 h-4" />;
      case 'postgres': return <Database className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const getCapabilityIcon = (capability: string) => {
    switch (capability) {
      case 'research': return <Search className="w-4 h-4" />;
      case 'github': return <GitBranch className="w-4 h-4" />;
      case 'memory': return <Brain className="w-4 h-4" />;
      case 'filesystem': return <FileText className="w-4 h-4" />;
      case 'database': return <Database className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="w-6 h-6 animate-spin mr-2" />
        <span>Loading MCP status...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className="mb-6">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          {error}
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleRefresh}
            className="ml-2"
          >
            <RefreshCw className="w-4 h-4 mr-1" />
            Retry
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">MCP Integration Dashboard</h2>
          <p className="text-gray-600">Model Context Protocol servers and capabilities</p>
        </div>
        <Button onClick={handleRefresh} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Server Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {mcpStatus && Object.entries(mcpStatus.servers).map(([serverName, server]) => (
          <Card key={serverName} className="relative">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-sm">
                {getServerIcon(serverName)}
                {serverName.replace('_', ' ').toUpperCase()}
                {server.connected ? (
                  <CheckCircle className="w-4 h-4 text-green-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-red-500" />
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500">Status</span>
                  <Badge variant={server.connected ? "default" : "destructive"}>
                    {server.connected ? 'Connected' : 'Disconnected'}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500">Tools</span>
                  <Badge variant="outline">{server.tools_count}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500">Enabled</span>
                  <Badge variant={server.enabled ? "default" : "secondary"}>
                    {server.enabled ? 'Yes' : 'No'}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Capabilities Overview */}
      {mcpCapabilities && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Enhanced Capabilities
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {Object.entries(mcpCapabilities).map(([capability, enabled]) => (
                <div key={capability} className="flex items-center gap-2">
                  {getCapabilityIcon(capability)}
                  <span className="text-sm capitalize">{capability}</span>
                  {enabled ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <XCircle className="w-4 h-4 text-gray-400" />
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Available Tools */}
      <Card>
        <CardHeader>
          <CardTitle>Available MCP Tools</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {mcpTools.map((tool) => (
              <div key={tool.name} className="border rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getServerIcon(tool.server)}
                    <span className="font-medium">{tool.name}</span>
                    <Badge variant="outline" className="text-xs">
                      {tool.server}
                    </Badge>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => onToolCall?.(tool.name, {})}
                  >
                    Test
                  </Button>
                </div>
                <p className="text-sm text-gray-600 mt-1">{tool.description}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <Card>
        <CardHeader>
          <CardTitle>MCP Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {mcpStatus?.total_tools || 0}
              </div>
              <div className="text-sm text-gray-500">Total Tools</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {mcpStatus ? Object.values(mcpStatus.servers).filter(s => s.connected).length : 0}
              </div>
              <div className="text-sm text-gray-500">Connected Servers</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {mcpStatus?.total_resources || 0}
              </div>
              <div className="text-sm text-gray-500">Resources</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {mcpCapabilities ? Object.values(mcpCapabilities).filter(Boolean).length : 0}
              </div>
              <div className="text-sm text-gray-500">Capabilities</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MCPDashboard;