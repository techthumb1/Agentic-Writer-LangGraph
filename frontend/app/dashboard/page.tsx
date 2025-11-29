// frontend/app/dashboard/page.tsx
// Enterprise-grade dashboard with strict fail-fast behavior
// No fallbacks, no degraded modes - if backend fails, show error
'use client';

import { redirect } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  FileText, 
  Plus, 
  BarChart3, 
  Clock, 
  TrendingUp,
  BookOpen,
  Settings,
  ChevronRight,
  Loader2,
  AlertCircle
} from 'lucide-react'
import Link from 'next/link'
import { useEffect, useState, useCallback } from 'react'
import { useSession } from 'next-auth/react'

interface DashboardStats {
  total_content: number
  drafts: number
  published: number
  views: number
  recent_content: RecentContentItem[]
  recent_activity: ActivityItem[]
}

interface RecentContentItem {
  id: string
  title: string
  status: 'published' | 'draft'
  updated_at: string
  type: string
}

interface ActivityItem {
  id: string
  type: 'published' | 'created' | 'updated' | 'generated'
  description: string
  timestamp: string
}

function useDashboardData() {
  const [data, setData] = useState<DashboardStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDashboardData = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      const statsResponse = await fetch('/api/dashboard/stats', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!statsResponse.ok) {
        throw new Error(`Dashboard API returned ${statsResponse.status}`)
      }

      const statsData = await statsResponse.json()
      
      if (!statsData || typeof statsData !== 'object') {
        throw new Error('Invalid dashboard data structure')
      }

      setData(statsData)

    } catch (err) {
      console.error('Dashboard data fetch failed:', err)
      setError(err instanceof Error ? err.message : 'Dashboard unavailable')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchDashboardData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return { data, isLoading, error, refresh: fetchDashboardData }
}

export default function DashboardPage() {
  const { data: session, status } = useSession()
  const { data: dashboardData, error } = useDashboardData()

  if (status === 'loading') {
    return (
      <div className="min-h-screen theme-background">
        <div className="container mx-auto p-6 flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
            <p className="text-muted-foreground">Loading dashboard...</p>
          </div>
        </div>
      </div>
    )
  }

  if (!session?.user) {
    redirect('/auth/signin')
    return null
  }

  if (error || !dashboardData) {
    return (
      <div className="min-h-screen theme-background">
        <div className="container mx-auto p-6">
          <div className="flex items-center justify-center min-h-[400px]">
            <Card className="theme-card max-w-md">
              <CardContent className="pt-6">
                <div className="flex items-center gap-3 text-destructive">
                  <AlertCircle className="h-5 w-5" />
                  <div>
                    <h3 className="font-medium">Dashboard Unavailable</h3>
                    <p className="text-sm mt-1">{error || 'Failed to load dashboard data'}</p>
                  </div>
                </div>
                <Button 
                  variant="outline" 
                  className="mt-4 w-full" 
                  onClick={() => window.location.reload()}
                >
                  Retry
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    )
  }

  const stats = dashboardData
  
  return (
    <div className="min-h-screen theme-background">
      <div className="container mx-auto p-6 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold mb-4 text-foreground">
              <span className="text-transparent bg-clip-text bg-linear-to-r from-purple-400 to-pink-600">
                Dashboard
              </span>
            </h1>
            <p className="text-muted-foreground text-xl">
              Welcome back, {typeof session.user.name === 'string' && session.user.name
                ? session.user.name
                : (typeof session.user.email === 'string' && session.user.email
                  ? session.user.email
                  : 'User')}
            </p>
          </div>
          <div className="flex gap-3">
            <Button asChild className="action-btn primary">
              <Link href="/generate" className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                New Content
              </Link>
            </Button>
            <Button variant="outline" asChild className="action-btn outline">
              <Link href="/settings" className="flex items-center gap-2">
                <Settings className="h-4 w-4" />
                Settings
              </Link>
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="stats-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-foreground">Total Content</CardTitle>
              <FileText className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{stats.total_content}</div>
              <p className="text-xs text-muted-foreground">
                All generated content
              </p>
            </CardContent>
          </Card>

          <Card className="stats-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-foreground">Drafts</CardTitle>
              <Clock className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{stats.drafts}</div>
              <p className="text-xs text-muted-foreground">
                Work in progress
              </p>
            </CardContent>
          </Card>

          <Card className="stats-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-foreground">Published</CardTitle>
              <BookOpen className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{stats.published}</div>
              <p className="text-xs text-muted-foreground">
                Live content
              </p>
            </CardContent>
          </Card>

          <Card className="stats-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-foreground">Total Views</CardTitle>
              <TrendingUp className="h-4 w-4 text-pink-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{stats.views.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                Content engagement
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Content */}
          <Card className="lg:col-span-2 theme-card">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-foreground">Recent Content</CardTitle>
                  <CardDescription className="text-muted-foreground">
                    Your latest articles and drafts
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm" asChild className="action-btn outline">
                  <Link href="/content" className="flex items-center gap-2">
                    View All
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stats.recent_content.length === 0 ? (
                  <div className="empty-state">
                    <FileText className="empty-state-icon" />
                    <h3 className="empty-state-title">No content yet</h3>
                    <p className="empty-state-description">Start generating amazing content with AI</p>
                    <Button asChild size="sm" className="action-btn primary mt-4">
                      <Link href="/generate">
                        <Plus className="h-4 w-4 mr-2" />
                        Create Content
                      </Link>
                    </Button>
                  </div>
                ) : (
                  stats.recent_content.map((item: RecentContentItem) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between p-3 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="shrink-0">
                          <FileText className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <h4 className="font-medium text-foreground">{item.title}</h4>
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <span className="capitalize">{item.type}</span>
                            <span>•</span>
                            <span>{new Date(item.updated_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`status-badge ${item.status}`}>
                          {item.status}
                        </span>
                        <Button variant="ghost" size="sm" asChild className="text-muted-foreground hover:text-foreground hover:bg-muted">
                          <Link href={`/content/${encodeURIComponent(item.id)}`}>
                            <ChevronRight className="h-4 w-4" />
                          </Link>

                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="theme-card">
            <CardHeader>
              <CardTitle className="text-foreground">Quick Actions</CardTitle>
              <CardDescription className="text-muted-foreground">
                Common tasks and shortcuts
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button asChild className="w-full justify-start action-btn primary">
                <Link href="/generate" className="flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  Create New Content
                </Link>
              </Button>
              
              <Button asChild className="w-full justify-start action-btn outline" variant="outline">
                <Link href="/templates" className="flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  Browse Templates
                </Link>
              </Button>
              
              <Button asChild className="w-full justify-start action-btn outline" variant="outline">
                <Link href="/content" className="flex items-center gap-2">
                  <BookOpen className="h-4 w-4" />
                  Manage Content
                </Link>
              </Button>
              
              <Button asChild className="w-full justify-start action-btn outline" variant="outline">
                <Link href="/analytics" className="flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  View Analytics
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card className="theme-card">
          <CardHeader>
            <CardTitle className="text-foreground">Recent Activity</CardTitle>
            <CardDescription className="text-muted-foreground">
              Latest updates and system activities
            </CardDescription>
          </CardHeader>
          <CardContent>
            {stats.recent_activity.length === 0 ? (
              <div className="empty-state">
                <Clock className="empty-state-icon" />
                <h3 className="empty-state-title">No recent activity</h3>
                <p className="empty-state-description">Activity will appear here as you use the platform</p>
              </div>
            ) : (
              <div className="space-y-3">
                {stats.recent_activity.map((activity: ActivityItem) => (
                  <div key={activity.id} className="flex items-center gap-3 text-sm">
                    <div className={`w-2 h-2 rounded-full ${
                      activity.type === 'published' ? 'bg-green-500' :
                      activity.type === 'created' ? 'bg-blue-500' :
                      activity.type === 'updated' ? 'bg-yellow-500' :
                      'bg-purple-500'
                    }`}></div>
                    <span className="text-muted-foreground">{new Date(activity.timestamp).toLocaleString()}</span>
                    <span className="text-foreground">{activity.description}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}