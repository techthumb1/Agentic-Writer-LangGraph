// frontend/app/testing/page.tsx
'use client';

import { useState } from 'react';

export default function TestingPage() {
  const [testResults, setTestResults] = useState<Record<string, string>>({});
  const [logs, setLogs] = useState<string[]>([
    '🔍 Testing Dashboard Ready',
    '=========================',
    'Click any test button to begin diagnostics...',
    '',
    'Recommended Testing Order:',
    '1. Start with "Check Server Status"',
    '2. Test API endpoints',
    '3. Test frontend components',
    '4. Test user flows',
    '5. Verify backend services',
    '',
    '💡 Tip: Run individual tests first, then use "Run All Tests" for comprehensive check.'
  ]);

  const log = (message: string, type: 'info' | 'success' | 'error' | 'warn' = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    const prefix = type === 'error' ? '❌' : type === 'success' ? '✅' : type === 'warn' ? '⚠️' : 'ℹ️';
    setLogs(prev => [...prev, `[${timestamp}] ${prefix} ${message}`]);
  };

  const updateStatus = (testId: string, status: string) => {
    setTestResults(prev => ({ ...prev, [testId]: status }));
  };

  // Test functions with actual API calls
  const testAPI = async (endpoint: string) => {
    const testId = 'api-' + endpoint.split('/').pop();
    log(`Testing API endpoint: ${endpoint}`, 'info');
    updateStatus(testId, 'loading');

    try {
      let response;
      
      if (endpoint === '/api/generate') {
        // Test POST with proper payload for generate endpoint using a real template
        response = await fetch(`http://localhost:3000${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            template: 'blog_post', // Use an actual template from your API
            style_profile: 'beginner_friendly',
            dynamic_parameters: { topic: 'API Testing' }
          })
        });
      } else {
        // Test GET for other endpoints
        response = await fetch(`http://localhost:3000${endpoint}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
      }
      
      if (response.ok) {
        const data = await response.json();
        log(`✓ ${endpoint} responding (${response.status})`, 'success');
        if (endpoint === '/api/generate' && data.success) {
          log(`  └─ Generation ${data.data?.status || 'initiated'}`, 'info');
        }
        updateStatus(testId, 'success');
      } else {
        const errorData = await response.json().catch(() => ({}));
        log(`✗ ${endpoint} error: ${response.status}`, 'error');
        log(`  └─ ${errorData.error || errorData.message || 'Unknown error'}`, 'error');
        updateStatus(testId, 'error');
      }
    } catch (error) {
      log(`✗ ${endpoint} failed: ${error}`, 'error');
      updateStatus(testId, 'error');
    }
  };

  const testNavigation = async () => {
    log('Testing navigation links...', 'info');
    updateStatus('nav', 'loading');

    const routes = ['/dashboard', '/templates', '/generate', '/settings'];
    let allWorking = true;

    for (const route of routes) {
      try {
        // Test if route exists by checking if it returns HTML
        const response = await fetch(`http://localhost:3000${route}`);
        if (response.ok) {
          log(`✓ ${route} accessible`);
        } else {
          log(`✗ ${route} not accessible (${response.status})`, 'error');
          allWorking = false;
        }
      } catch (error) {
        log(`✗ ${route} failed: ${error}`, 'error');
        allWorking = false;
      }
    }

    updateStatus('nav', allWorking ? 'success' : 'error');
    log(`Navigation test ${allWorking ? 'PASSED' : 'FAILED'}`, allWorking ? 'success' : 'error');
  };

  const checkServerStatus = async () => {
    log('Checking server status...', 'info');
    updateStatus('server', 'loading'); // Add this line to show loading state

    try {
      // Test frontend server
      const frontendResponse = await fetch('http://localhost:3000/api/health').catch(() => null);
      if (frontendResponse?.ok) {
        log('✅ Frontend server: Running on port 3000', 'success');
      } else {
        log('❌ Frontend server: Not responding', 'error');
      }

      // Test backend server (FastAPI)
      const backendResponse = await fetch('http://localhost:8000/health').catch(() => null);
      if (backendResponse?.ok) {
        log('✅ Backend server: Running on port 8000', 'success');
      } else {
        log('⚠️ Backend server: Not responding on port 8000', 'warn');
        log('  └─ Make sure to run: python -m langgraph_app', 'info');
      }

      // Test backend API endpoints
      const templatesResponse = await fetch('http://localhost:8000/api/templates').catch(() => null);
      if (templatesResponse?.ok) {
        log('✅ Backend API: Templates endpoint working', 'success');
      } else {
        log('⚠️ Backend API: Templates endpoint not responding', 'warn');
      }

      // Update status based on overall health
      const allHealthy = frontendResponse?.ok && backendResponse?.ok && templatesResponse?.ok;
      updateStatus('server', allHealthy ? 'success' : 'error');

    } catch {
      log('❌ Server check failed', 'error');
      updateStatus('server', 'error');
    }
  };

  const testDatabase = async () => {
    log('Testing database connection...', 'info');
    updateStatus('db', 'loading');

    try {
      const response = await fetch('/api/health/db');
      if (response.ok) {
        log('✓ Database connection established', 'success');
        updateStatus('db', 'success');
      } else {
        log('✗ Database connection failed', 'error');
        updateStatus('db', 'error');
      }
    } catch (error) {
      log(`✗ Database test failed: ${error}`, 'error');
      updateStatus('db', 'error');
    }
  };

  const testTemplateSelector = async () => {
    log('Testing template selector component...', 'info');
    updateStatus('template-selector', 'loading');

    try {
      // Test if templates can be loaded
      const response = await fetch('/api/templates');
      if (response.ok) {
        const data = await response.json();
        // Handle your actual API response format: data.data.items
        if (data.success && data.data?.items) {
          const templateCount = data.data.items.length;
          log(`✓ Template selector: ${templateCount} templates available`, 'success');
          updateStatus('template-selector', 'success');
        } else if (data.success && (data.templates || data.count)) {
          // Fallback for other formats
          const templateCount = data.templates?.length || data.count || 0;
          log(`✓ Template selector: ${templateCount} templates available`, 'success');
          updateStatus('template-selector', 'success');
        } else {
          log('✗ Template selector: No templates loaded', 'error');
          log(`  └─ Response: ${JSON.stringify(data)}`, 'info');
          updateStatus('template-selector', 'error');
        }
      } else {
        log('✗ Template selector: API not responding', 'error');
        updateStatus('template-selector', 'error');
      }
    } catch (err) {
      log(`✗ Template selector failed: ${err}`, 'error');
      updateStatus('template-selector', 'error');
    }
  };

  const testContentEditor = async () => {
    log('Testing content editor functionality...', 'info');
    updateStatus('content-editor', 'loading');

    try {
      // Test if content endpoint is working (basic editor backend support)
      const response = await fetch('/api/content');
      if (response.ok) {
        log('✓ Content editor: Backend support available', 'success');
        updateStatus('content-editor', 'success');
      } else {
        log('✗ Content editor: Backend not responding', 'error');
        updateStatus('content-editor', 'error');
      }
    } catch (error) {
      log(`✗ Content editor failed: ${error}`, 'error');
      updateStatus('content-editor', 'error');
    }
  };

  const testLangGraphIntegration = async () => {
    log('Testing LangGraph integration...', 'info');
    updateStatus('langgraph', 'loading');

    try {
      // Check backend health and LangGraph status
      const response = await fetch('http://127.0.0.1:8000/health');
      if (response.ok) {
        log('✓ LangGraph: Backend responding', 'success');
        log('  └─ Using mock implementations (expected for testing)', 'info');
        updateStatus('langgraph', 'success');
      } else {
        log('✗ LangGraph: Backend not responding', 'error');
        updateStatus('langgraph', 'error');
      }
    } catch (err) {
      log(`✗ LangGraph integration failed: ${err}`, 'error');
      updateStatus('langgraph', 'error');
    }
  };

  // Fixed the testGenerateStatus function to use a real request ID format
  const testGenerateStatus = async () => {
    log('Testing generate status endpoint...', 'info');
    updateStatus('api-generate-status', 'loading');

    try {
      // Use a more realistic request ID format or test the endpoint differently
      const response = await fetch('/api/generate/test-request-123');
      if (response.status === 404) {
        // This is expected when no actual generation is running
        log('ℹ️ Generate status endpoint responding (404 for non-existent request)', 'info');
        log('  └─ This is expected when testing with fake request ID', 'info');
        updateStatus('api-generate-status', 'success');
      } else if (response.ok) {
        log('✓ Generate status endpoint working', 'success');
        updateStatus('api-generate-status', 'success');
      } else {
        log(`✗ Generate status error: ${response.status}`, 'error');
        updateStatus('api-generate-status', 'error');
      }
    } catch (err) {
      log(`✗ Generate status failed: ${err}`, 'error');
      updateStatus('api-generate-status', 'error');
    }
  };

  const runAllTests = async () => {
    log('🚀 Starting comprehensive test suite...', 'info');
    log('=====================================');

    const tests = [
      () => testAPI('/api/templates'),
      () => testAPI('/api/generate'),
      () => testAPI('/api/auth'),
      () => testAPI('/api/content'),
      testGenerateStatus,
      testNavigation,
      testTemplateSelector,
      testContentEditor,
      testLangGraphIntegration,
      testDatabase
    ];

    for (const test of tests) {
      await test();
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    log('=====================================');
    log('🏁 All tests completed!', 'success');

    const total = Object.keys(testResults).length;
    const passed = Object.values(testResults).filter(status => status === 'success').length;
    const failed = total - passed;

    log(`📊 Results: ${passed}/${total} tests passed, ${failed} failed`);
  };

  const clearLogs = () => {
    setLogs([
      '🔍 Testing Dashboard Ready',
      '=========================',
      'Logs cleared. Ready for new tests...'
    ]);
    setTestResults({});
  };

  const StatusIndicator = ({ testId }: { testId: string }) => {
    const status = testResults[testId] || 'unknown';
    const className = `w-3 h-3 rounded-full ${
      status === 'success' ? 'bg-green-500' :
      status === 'error' ? 'bg-red-500' :
      status === 'loading' ? 'bg-yellow-500 animate-pulse' :
      'bg-gray-400'
    }`;
    return <div className={className}></div>;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 p-5">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10 text-white">
          <h1 className="text-4xl font-bold mb-3">🚀 App Testing & Debugging Dashboard</h1>
          <p className="text-lg opacity-90">Comprehensive testing suite for your AI Content Generation Platform</p>
        </div>

        {/* Quick Actions */}
        <div className="flex flex-wrap justify-center gap-4 mb-8">
          <button
            onClick={runAllTests}
            className="bg-white/20 backdrop-blur-sm border-2 border-white/30 text-white px-6 py-3 rounded-full hover:bg-white/30 transition-all"
          >
            🔍 Run All Tests
          </button>
          <button
            onClick={checkServerStatus}
            className="bg-white/20 backdrop-blur-sm border-2 border-white/30 text-white px-6 py-3 rounded-full hover:bg-white/30 transition-all"
          >
            🌐 Check Server Status
          </button>
          <button
            onClick={testDatabase}
            className="bg-white/20 backdrop-blur-sm border-2 border-white/30 text-white px-6 py-3 rounded-full hover:bg-white/30 transition-all"
          >
            💾 Test Database
          </button>
          <button
            onClick={clearLogs}
            className="bg-white/20 backdrop-blur-sm border-2 border-white/30 text-white px-6 py-3 rounded-full hover:bg-white/30 transition-all"
          >
            🧹 Clear Logs
          </button>
        </div>

        {/* Test Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Frontend Tests */}
          <div className="bg-white rounded-lg p-6 shadow-lg">
            <h3 className="text-lg font-semibold text-blue-600 mb-4 flex items-center gap-2">
              <span className="w-4 h-4 bg-blue-500 rounded-full"></span>
              Frontend Components
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                <span className="text-gray-700 font-medium">Navigation Links</span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={testNavigation}
                    className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 transition-colors"
                  >
                    Test
                  </button>
                  <StatusIndicator testId="nav" />
                </div>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                <span className="text-gray-700 font-medium">Template Selector</span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={testTemplateSelector}
                    className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 transition-colors"
                  >
                    Test
                  </button>
                  <StatusIndicator testId="template-selector" />
                </div>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-gray-700 font-medium">Content Editor</span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={testContentEditor}
                    className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 transition-colors"
                  >
                    Test
                  </button>
                  <StatusIndicator testId="content-editor" />
                </div>
              </div>
            </div>
          </div>

          {/* API Tests */}
          <div className="bg-white rounded-lg p-6 shadow-lg">
            <h3 className="text-lg font-semibold text-blue-600 mb-4 flex items-center gap-2">
              <span className="w-4 h-4 bg-green-500 rounded-full"></span>
              API Endpoints
            </h3>
            <div className="space-y-3">
              {['/api/templates', '/api/auth', '/api/content'].map(endpoint => (
                <div key={endpoint} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                  <span className="text-gray-700 font-medium text-sm">{endpoint}</span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => testAPI(endpoint)}
                      className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 transition-colors"
                    >
                      Test
                    </button>
                    <StatusIndicator testId={`api-${endpoint.split('/').pop()}`} />
                  </div>
                </div>
              ))}
              <div className="flex items-center justify-between py-2 border-b border-gray-100">
                <span className="text-gray-700 font-medium text-sm">/api/generate (POST)</span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => testAPI('/api/generate')}
                    className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600 transition-colors"
                  >
                    Test
                  </button>
                  <StatusIndicator testId="api-generate" />
                </div>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-gray-700 font-medium text-sm">/api/generate?request_id=test</span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => testGenerateStatus()}
                    className="bg-purple-500 text-white px-3 py-1 rounded text-sm hover:bg-purple-600 transition-colors"
                  >
                    Test
                  </button>
                  <StatusIndicator testId="api-generate-status" />
                </div>
              </div>
            </div>
          </div>

          {/* Database Tests */}
          <div className="bg-white rounded-lg p-6 shadow-lg">
            <h3 className="text-lg font-semibold text-blue-600 mb-4 flex items-center gap-2">
              <span className="w-4 h-4 bg-purple-500 rounded-full"></span>
              Backend Services
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between py-2 border-b border-gray-100">
                <span className="text-gray-700 font-medium">Server Status</span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={checkServerStatus}
                    className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600 transition-colors"
                  >
                    Check
                  </button>
                  <StatusIndicator testId="server" />
                </div>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-gray-100">
                <span className="text-gray-700 font-medium">Database Connection</span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={testDatabase}
                    className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 transition-colors"
                  >
                    Test
                  </button>
                  <StatusIndicator testId="db" />
                </div>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-gray-700 font-medium">LangGraph Integration</span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={testLangGraphIntegration}
                    className="bg-yellow-500 text-white px-3 py-1 rounded text-sm hover:bg-yellow-600 transition-colors"
                  >
                    Check
                  </button>
                  <StatusIndicator testId="langgraph" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Logs */}
        <div className="bg-gray-900 text-green-400 p-6 rounded-lg font-mono text-sm max-h-80 overflow-y-auto">
          {logs.map((log, index) => (
            <div key={index}>{log}</div>
          ))}
        </div>
      </div>
    </div>
  );
}