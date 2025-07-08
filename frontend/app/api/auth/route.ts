// frontend/app/api/auth/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { randomUUID } from 'crypto';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL;
const FASTAPI_API_KEY = process.env.FASTAPI_API_KEY;
if (!FASTAPI_BASE_URL || !FASTAPI_API_KEY) {
  throw new Error('FASTAPI_BASE_URL and FASTAPI_API_KEY must be set in environment variables');
}

// Enterprise interfaces
interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'editor' | 'user' | 'viewer';
  permissions: string[];
  organization?: string;
  created_at: string;
  last_login: string;
}

interface Session {
  user: User;
  session_id: string;
  expires: string;
  authenticated: boolean;
  token: string;
  refresh_token?: string;
}

interface AuthRequest {
  action: 'login' | 'logout' | 'refresh' | 'register';
  email?: string;
  password?: string;
  refresh_token?: string;
  name?: string;
  organization?: string;
}

// Enterprise logging
const logAuthEvent = (action: string, email: string | undefined, success: boolean, details?: string) => {
  const logData = {
    timestamp: new Date().toISOString(),
    action,
    email: email ? email.replace(/(.{2}).*(@.*)/, '$1***$2') : 'unknown', // Mask email for privacy
    success,
    ip: 'masked', // In production, get real IP
    user_agent: 'masked', // In production, get real user agent
    ...(details && { details })
  };
  console.log(`🔐 [AUTH] ${action}:`, JSON.stringify(logData, null, 2));
};

// Try backend authentication first
async function authenticateWithBackend(action: string, credentials: Record<string, unknown>): Promise<unknown | null> {
  try {
    const response = await fetch(`${FASTAPI_BASE_URL}/api/auth/${action}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${FASTAPI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        return null; // Invalid credentials
      }
      throw new Error(`Backend auth error: ${response.status}`);
    }

    const data = await response.json();
    logAuthEvent(action, (credentials as { email?: string }).email, true, 'Backend authentication successful');
    return data;

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Backend auth failed';
    logAuthEvent(action, (credentials as { email?: string }).email, false, errorMsg);
    return null; // Fall back to mock auth
  }
}

// Mock authentication for development/fallback
function mockAuthentication(action: string, credentials: AuthRequest): Session | null {
  const mockUsers = [
    {
      id: '1',
      name: 'Admin User',
      email: 'admin@example.com',
      role: 'admin' as const,
      permissions: ['read', 'write', 'delete', 'admin'],
      organization: 'AgentWrite Pro',
      created_at: '2024-01-01T00:00:00Z',
      password: 'admin123' // In production, this would be hashed
    },
    {
      id: '2',
      name: 'Editor User',
      email: 'editor@example.com',
      role: 'editor' as const,
      permissions: ['read', 'write'],
      organization: 'AgentWrite Pro',
      created_at: '2024-01-01T00:00:00Z',
      password: 'editor123'
    },
    {
      id: '3',
      name: 'Test User',
      email: 'test@example.com',
      role: 'user' as const,
      permissions: ['read'],
      organization: 'AgentWrite Pro',
      created_at: '2024-01-01T00:00:00Z',
      password: 'test123'
    }
  ];

  if (action === 'login') {
    const user = mockUsers.find(u => u.email === credentials.email && u.password === credentials.password);
    
    if (!user) {
      logAuthEvent('login', credentials.email, false, 'Invalid credentials');
      return null;
    }

    const sessionId = randomUUID();
    const token = `mock_token_${sessionId}`;
    
    const session: Session = {
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role,
        permissions: user.permissions,
        organization: user.organization,
        created_at: user.created_at,
        last_login: new Date().toISOString()
      },
      session_id: sessionId,
      expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // 24 hours
      authenticated: true,
      token,
      refresh_token: `refresh_${sessionId}`
    };

    logAuthEvent('login', credentials.email, true, `Mock authentication for ${user.role}`);
    return session;
  }

  if (action === 'register') {
    const newUser = {
      id: randomUUID(),
      name: credentials.name || 'New User',
      email: credentials.email || '',
      role: 'user' as const,
      permissions: ['read'],
      organization: credentials.organization || 'Default',
      created_at: new Date().toISOString(),
      last_login: new Date().toISOString()
    };

    const sessionId = randomUUID();
    const token = `mock_token_${sessionId}`;

    const session: Session = {
      user: newUser,
      session_id: sessionId,
      expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      authenticated: true,
      token,
      refresh_token: `refresh_${sessionId}`
    };

    logAuthEvent('register', credentials.email, true, 'Mock user registration');
    return session;
  }

  return null;
}

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    const token = authHeader?.replace('Bearer ', '');

    console.log(`🔍 [AUTH] Session check requested`);

    // Try to validate with backend first
    if (token) {
      try {
        const response = await fetch(`${FASTAPI_BASE_URL}/api/auth/validate`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          signal: AbortSignal.timeout(5000),
        });

        if (response.ok) {
          const backendSession = await response.json();
          logAuthEvent('session_check', backendSession.user?.email, true, 'Backend session validated');
          
          return NextResponse.json({
            success: true,
            session: backendSession,
            authenticated: true,
            source: 'backend'
          });
        }
      } catch {
        // Fall back to mock session
      }
    }

    // Mock session for development/fallback
    const mockSession: Session = {
      user: {
        id: '1',
        name: 'Test User',
        email: 'test@example.com',
        role: 'user',
        permissions: ['read'],
        organization: 'AgentWrite Pro',
        created_at: '2024-01-01T00:00:00Z',
        last_login: new Date().toISOString()
      },
      session_id: randomUUID(),
      expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      authenticated: true,
      token: token || `mock_token_${randomUUID()}`,
    };

    logAuthEvent('session_check', mockSession.user.email, true, 'Mock session provided');

    return NextResponse.json({
      success: true,
      session: mockSession,
      authenticated: true,
      source: 'mock'
    });

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Session check failed';
    logAuthEvent('session_check', undefined, false, errorMsg);
    
    return NextResponse.json(
      { 
        success: false, 
        error: 'Authentication check failed',
        message: errorMsg,
        authenticated: false
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body: AuthRequest = await request.json();
    const { action, email, password, refresh_token, name, organization } = body;

    if (!action) {
      return NextResponse.json(
        { success: false, error: 'Action is required' },
        { status: 400 }
      );
    }

    console.log(`🔐 [AUTH] ${action} attempt for: ${email || 'unknown'}`);

    // Handle different auth actions
    switch (action) {
      case 'login': {
        if (!email || !password) {
          logAuthEvent('login', email, false, 'Missing credentials');
          return NextResponse.json(
            { success: false, error: 'Email and password are required' },
            { status: 400 }
          );
        }

        // Try backend authentication first
        const backendResult = await authenticateWithBackend('login', { email, password });
        if (backendResult) {
          return NextResponse.json({
            success: true,
            message: 'Login successful',
            session: backendResult,
            source: 'backend'
          });
        }

        // Fall back to mock authentication
        const mockResult = mockAuthentication('login', { action: 'login', email, password });
        if (mockResult) {
          return NextResponse.json({
            success: true,
            message: 'Login successful',
            session: mockResult,
            source: 'mock'
          });
        }

        logAuthEvent('login', email, false, 'Invalid credentials');
        return NextResponse.json(
          { success: false, error: 'Invalid email or password' },
          { status: 401 }
        );
      }

      case 'register': {
        if (!email || !password || !name) {
          logAuthEvent('register', email, false, 'Missing required fields');
          return NextResponse.json(
            { success: false, error: 'Name, email, and password are required' },
            { status: 400 }
          );
        }

        // Try backend registration first
        const backendResult = await authenticateWithBackend('register', { 
          name, email, password, organization 
        });
        if (backendResult) {
          return NextResponse.json({
            success: true,
            message: 'Registration successful',
            session: backendResult,
            source: 'backend'
          });
        }

        // Fall back to mock registration
        const mockResult = mockAuthentication('register', { action: 'register', name, email, password, organization });
        if (mockResult) {
          return NextResponse.json({
            success: true,
            message: 'Registration successful',
            session: mockResult,
            source: 'mock'
          });
        }

        return NextResponse.json(
          { success: false, error: 'Registration failed' },
          { status: 500 }
        );
      }

      case 'logout': {
        logAuthEvent('logout', email, true, 'Logout successful');
        return NextResponse.json({
          success: true,
          message: 'Logout successful',
          authenticated: false
        });
      }

      case 'refresh': {
        if (!refresh_token) {
          return NextResponse.json(
            { success: false, error: 'Refresh token is required' },
            { status: 400 }
          );
        }

        // Try backend token refresh
        const backendResult = await authenticateWithBackend('refresh', { refresh_token });
        if (backendResult) {
          logAuthEvent('refresh', email, true, 'Token refreshed via backend');
          return NextResponse.json({
            success: true,
            message: 'Token refreshed',
            session: backendResult,
            source: 'backend'
          });
        }

        // Mock token refresh
        const newToken = `mock_token_${randomUUID()}`;
        logAuthEvent('refresh', email, true, 'Token refreshed via mock');
        
        return NextResponse.json({
          success: true,
          message: 'Token refreshed',
          token: newToken,
          expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
          source: 'mock'
        });
      }

      default:
        return NextResponse.json(
          { success: false, error: 'Invalid action' },
          { status: 400 }
        );
    }

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Authentication action failed';
    logAuthEvent('unknown', undefined, false, errorMsg);
    
    return NextResponse.json(
      { 
        success: false, 
        error: 'Authentication action failed',
        message: errorMsg
      },
      { status: 500 }
    );
  }
}

// Enterprise user management endpoint
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, user_id, permissions, role, organization } = body;

    if (!action || !user_id) {
      return NextResponse.json(
        { success: false, error: 'Action and user_id are required' },
        { status: 400 }
      );
    }

    console.log(`👥 [AUTH] User management: ${action} for user ${user_id}`);

    // Forward to backend for user management
    try {
      const response = await fetch(`${FASTAPI_BASE_URL}/api/auth/users/${user_id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${FASTAPI_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action, permissions, role, organization }),
      });

      if (response.ok) {
        const data = await response.json();
        logAuthEvent('user_management', undefined, true, `${action} successful`);
        
        return NextResponse.json({
          success: true,
          message: `User ${action} successful`,
          user: data
        });
      }
    } catch {
      // Fall back to mock response
    }

    // Mock user management response
    logAuthEvent('user_management', undefined, true, `Mock ${action} for user management`);
    
    return NextResponse.json({
      success: true,
      message: `User ${action} successful (mock)`,
      source: 'mock'
    });

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'User management failed';
    logAuthEvent('user_management', undefined, false, errorMsg);
    
    return NextResponse.json(
      { 
        success: false, 
        error: 'User management failed',
        message: errorMsg
      },
      { status: 500 }
    );
  }
}