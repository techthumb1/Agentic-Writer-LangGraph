// frontend/app/dashboard/page.tsx
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
  totalContent: number
  drafts: number
  published: number
  views: number
  recentContent: RecentContentItem[]
  recentActivity: ActivityItem[]
}

interface RecentContentItem {
  id: string
  title: string
  status: 'published' | 'draft'
  updatedAt: string
  type: string
}

interface ActivityItem {
  id: string
  type: 'published' | 'created' | 'updated' | 'generated'
  description: string
  timestamp: string
}

interface ContentResponse {
  content?: RecentContentItem[]
  totalViews?: number
}

interface ActivityResponse {
  activities?: ActivityItem[]
}

// Custom hook for dashboard data
function useDashboardData() {
  const [data, setData] = useState<DashboardStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDashboardData = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      // Fetch dashboard stats from your backend
      const statsResponse = await fetch('/api/dashboard/stats', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!statsResponse.ok) {
        if (statsResponse.status === 404) {
          // If dashboard stats endpoint doesn't exist yet, fall back to individual endpoints
          const [contentResponse, activityResponse] = await Promise.all([
            fetch('/api/content').catch(() => null),
            fetch('/api/dashboard/activity').catch(() => null)
          ])

          // Parse responses if available
          const contentData: ContentResponse | null = contentResponse?.ok ? await contentResponse.json() : null
          const activityData: ActivityResponse | null = activityResponse?.ok ? await activityResponse.json() : null

          // Build stats from available data
          const stats: DashboardStats = {
            totalContent: contentData?.content?.length || 0,
            drafts: contentData?.content?.filter((item: RecentContentItem) => item.status === 'draft').length || 0,
            published: contentData?.content?.filter((item: RecentContentItem) => item.status === 'published').length || 0,
            views: contentData?.totalViews || 0,
            recentContent: contentData?.content?.slice(0, 4) || [],
            recentActivity: activityData?.activities?.slice(0, 4) || []
          }

          setData(stats)
          return
        }
        throw new Error(`Failed to fetch dashboard data: ${statsResponse.status}`)
      }

      const statsData = await statsResponse.json()
      setData(statsData)

    } catch (err) {
      console.error('Dashboard data fetch error:', err)
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data')
      
      // Set fallback data to prevent complete UI failure
      setData({
        totalContent: 0,
        drafts: 0,
        published: 0,
        views: 0,
        recentContent: [],
        recentActivity: []
      })
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchDashboardData()
  }, [fetchDashboardData])

  return { data, isLoading, error, refresh: fetchDashboardData }
}

export default function DashboardPage() {
  const { data: session } = useSession()
  const { data: dashboardData, isLoading, error } = useDashboardData()

  // Redirect to auth if not authenticated
  useEffect(() => {
    if (!session?.user) {
      redirect('/auth/signin')
    }
  }, [session])

  if (!session?.user) {
    return null // Will redirect
  }

  if (isLoading) {
    return (
      <div className="container mx-auto p-6 flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-purple-400 mx-auto mb-4" />
          <p className="text-gray-300">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <Card className="bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800 max-w-md">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3 text-red-700 dark:text-red-300">
                <AlertCircle className="h-5 w-5" />
                <div>
                  <h3 className="font-medium">Failed to load dashboard</h3>
                  <p className="text-sm mt-1">{error}</p>
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
    )
  }

  const stats = dashboardData!

  return (
    <div className="container mx-auto p-6 space-y-8 text-white">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
            Dashboard
          </h1>
          <p className="text-gray-300 mt-2">
            Welcome back, {typeof session.user.name === 'string' && session.user.name
              ? session.user.name
              : (typeof session.user.email === 'string' && session.user.email
                ? session.user.email
                : 'User')}
          </p>
        </div>
        <div className="flex gap-3">
          <Button asChild className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
            <Link href="/generate" className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              New Content
            </Link>
          </Button>
          <Button variant="outline" asChild className="border-purple-400 text-purple-300 hover:bg-purple-900/20">
            <Link href="/settings" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Settings
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-white/10 backdrop-blur-sm border-white/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Total Content</CardTitle>
            <FileText className="h-4 w-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats.totalContent}</div>
            <p className="text-xs text-gray-300">
              All generated content
            </p>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border-white/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Drafts</CardTitle>
            <Clock className="h-4 w-4 text-yellow-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats.drafts}</div>
            <p className="text-xs text-gray-300">
              Work in progress
            </p>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border-white/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Published</CardTitle>
            <BookOpen className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats.published}</div>
            <p className="text-xs text-gray-300">
              Live content
            </p>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border-white/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Total Views</CardTitle>
            <TrendingUp className="h-4 w-4 text-pink-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{stats.views.toLocaleString()}</div>
            <p className="text-xs text-gray-300">
              Content engagement
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Content */}
        <Card className="lg:col-span-2 bg-white/10 backdrop-blur-sm border-white/20">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-white">Recent Content</CardTitle>
                <CardDescription className="text-gray-300">
                  Your latest articles and drafts
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" asChild className="border-purple-400 text-purple-300 hover:bg-purple-900/20">
                <Link href="/content" className="flex items-center gap-2">
                  View All
                  <ChevronRight className="h-4 w-4" />
                </Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.recentContent.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-gray-500 mx-auto mb-3" />
                  <p className="text-gray-400 mb-2">No content yet</p>
                  <p className="text-sm text-gray-500 mb-4">Start generating amazing content with AI</p>
                  <Button asChild size="sm" className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
                    <Link href="/generate">
                      <Plus className="h-4 w-4 mr-2" />
                      Create Content
                    </Link>
                  </Button>
                </div>
              ) : (
                stats.recentContent.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between p-3 border border-white/20 rounded-lg hover:bg-white/5 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex-shrink-0">
                        <FileText className="h-5 w-5 text-purple-400" />
                      </div>
                      <div>
                        <h4 className="font-medium text-white">{item.title}</h4>
                        <div className="flex items-center gap-2 text-sm text-gray-300">
                          <span className="capitalize">{item.type}</span>
                          <span>•</span>
                          <span>{new Date(item.updatedAt).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          item.status === 'published'
                            ? 'bg-green-600/20 text-green-300 border border-green-600/30'
                            : 'bg-yellow-600/20 text-yellow-300 border border-yellow-600/30'
                        }`}
                      >
                        {item.status}
                      </span>
                      <Button variant="ghost" size="sm" asChild className="text-gray-300 hover:text-white hover:bg-white/10">
                        <Link href={`/content/${item.id}`}>
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
        <Card className="bg-white/10 backdrop-blur-sm border-white/20">
          <CardHeader>
            <CardTitle className="text-white">Quick Actions</CardTitle>
            <CardDescription className="text-gray-300">
              Common tasks and shortcuts
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button asChild className="w-full justify-start bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white">
              <Link href="/generate" className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                Create New Content
              </Link>
            </Button>
            
            <Button asChild className="w-full justify-start border-purple-400 text-purple-300 hover:bg-purple-900/20" variant="outline">
              <Link href="/templates" className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Browse Templates
              </Link>
            </Button>
            
            <Button asChild className="w-full justify-start border-purple-400 text-purple-300 hover:bg-purple-900/20" variant="outline">
              <Link href="/content" className="flex items-center gap-2">
                <BookOpen className="h-4 w-4" />
                Manage Content
              </Link>
            </Button>
            
            <Button asChild className="w-full justify-start border-purple-400 text-purple-300 hover:bg-purple-900/20" variant="outline">
              <Link href="/analytics" className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                View Analytics
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card className="bg-white/10 backdrop-blur-sm border-white/20">
        <CardHeader>
          <CardTitle className="text-white">Recent Activity</CardTitle>
          <CardDescription className="text-gray-300">
            Latest updates and system activities
          </CardDescription>
        </CardHeader>
        <CardContent>
          {stats.recentActivity.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="h-12 w-12 text-gray-500 mx-auto mb-3" />
              <p className="text-gray-400">No recent activity</p>
              <p className="text-sm text-gray-500">Activity will appear here as you use the platform</p>
            </div>
          ) : (
            <div className="space-y-3">
              {stats.recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-center gap-3 text-sm">
                  <div className={`w-2 h-2 rounded-full ${
                    activity.type === 'published' ? 'bg-green-500' :
                    activity.type === 'created' ? 'bg-blue-500' :
                    activity.type === 'updated' ? 'bg-yellow-500' :
                    'bg-purple-500'
                  }`}></div>
                  <span className="text-gray-400">{new Date(activity.timestamp).toLocaleString()}</span>
                  <span className="text-gray-200">{activity.description}</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}