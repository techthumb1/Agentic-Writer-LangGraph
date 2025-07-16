// File: frontend/components/mcp/MCPToolTester.tsx
import React, { useState } from 'react';
import { Play, Loader2, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { useMCP } from '../../hooks/useMCP';
import type { MCPTool } from '../../hooks/useMCP';

interface MCPToolTesterProps {
  tool: MCPTool;
}

// Simple UI Components
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

const Input: React.FC<{
  id?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  className?: string;
}> = ({ id, value, onChange, placeholder, className = '' }) => (
  <input
    id={id}
    type="text"
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${className}`}
  />
);

const Textarea: React.FC<{
  id?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  placeholder?: string;
  className?: string;
}> = ({ id, value, onChange, placeholder, className = '' }) => (
  <textarea
    id={id}
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    rows={4}
    className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${className}`}
  />
);

const Label: React.FC<{
  htmlFor?: string;
  children: React.ReactNode;
  className?: string;
}> = ({ htmlFor, children, className = '' }) => (
  <label
    htmlFor={htmlFor}
    className={`block text-sm font-medium text-gray-700 ${className}`}
  >
    {children}
  </label>
);

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

const MCPToolTester: React.FC<MCPToolTesterProps> = ({ tool }) => {
  const { callTool } = useMCP();
  const [arguments_, setArguments] = useState<string>('{}');
  const [namespace, setNamespace] = useState<string>('default');
  const [result, setResult] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTest = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const parsedArgs = JSON.parse(arguments_);
      
      const response = await callTool({
        tool_name: tool.name,
        arguments: parsedArgs,
        namespace: namespace || undefined,
      });

      setResult(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Test failed';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = () => {
    if (loading) return <Loader2 className="w-4 h-4 animate-spin" />;
    
    if (result && typeof result === 'object' && result !== null) {
      const resultObj = result as { success?: boolean; error?: string };
      if (resultObj.success) return <CheckCircle className="w-4 h-4 text-green-500" />;
      if (resultObj.error) return <XCircle className="w-4 h-4 text-red-500" />;
    }
    
    if (error) return <XCircle className="w-4 h-4 text-red-500" />;
    return <Play className="w-4 h-4" />;
  };

  const formatResult = (data: unknown): string => {
    if (typeof data === 'string') return data;
    if (typeof data === 'object' && data !== null) {
      try {
        return JSON.stringify(data, null, 2);
      } catch {
        return String(data);
      }
    }
    return String(data);
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {getStatusIcon()}
          {tool.name}
          <Badge variant="outline">{tool.server}</Badge>
        </CardTitle>
        <p className="text-sm text-gray-600">{tool.description}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="arguments">Arguments (JSON)</Label>
          <Textarea
            id="arguments"
            value={arguments_}
            onChange={(e) => setArguments(e.target.value)}
            placeholder='{"key": "value"}'
            className="mt-1"
          />
        </div>

        {tool.name.includes('memory') && (
          <div>
            <Label htmlFor="namespace">Namespace</Label>
            <Input
              id="namespace"
              value={namespace}
              onChange={(e) => setNamespace(e.target.value)}
              placeholder="default"
              className="mt-1"
            />
          </div>
        )}

        <Button 
          onClick={handleTest} 
          disabled={loading}
          className="w-full"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Testing...
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-2" />
              Test Tool
            </>
          )}
        </Button>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

                <pre className="text-xs bg-gray-100 p-2 rounded overflow-x-auto">
          {formatResult((result as { result?: unknown }).result) as React.ReactNode}
        </pre>
      </CardContent>
    </Card>
  );
};

export default MCPToolTester;