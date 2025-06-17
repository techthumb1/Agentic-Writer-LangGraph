// frontend/app/dashboard/page.tsx
import { auth } from '@/auth'
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
  ChevronRight
} from 'lucide-react'
import Link from 'next/link'

interface DashboardStats {
  totalContent: number
  drafts: number
  published: number
  views: number
}

// Mock data - replace with real data fetching
const mockStats: DashboardStats = {
  totalContent: 24,
  drafts: 8,
  published: 16,
  views: 1247
}

const recentContent = [
  {
    id: '1',
    title: 'Introduction to Contrastive Learning',
    status: 'published',
    updatedAt: '2 hours ago',
    type: 'article'
  },
  {
    id: '2',
    title: 'Federated Learning 101',
    status: 'draft',
    updatedAt: '1 day ago',
    type: 'guide'
  },
  {
    id: '3',
    title: 'Future of LLMs',
    status: 'published',
    updatedAt: '3 days ago',
    type: 'analysis'
  },
  {
    id: '4',
    title: 'Startup Use Cases',
    status: 'draft',
    updatedAt: '5 days ago',
    type: 'report'
  }
]

export default async function DashboardPage() {
  const session = await auth()
  
  if (!session?.user) {
    redirect('/auth/signin')
  }

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
            <div className="text-2xl font-bold text-white">{mockStats.totalContent}</div>
            <p className="text-xs text-gray-300">
              +2 from last month
            </p>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border-white/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Drafts</CardTitle>
            <Clock className="h-4 w-4 text-yellow-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{mockStats.drafts}</div>
            <p className="text-xs text-gray-300">
              +1 from last week
            </p>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border-white/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Published</CardTitle>
            <BookOpen className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{mockStats.published}</div>
            <p className="text-xs text-gray-300">
              +3 from last month
            </p>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-sm border-white/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-white">Total Views</CardTitle>
            <TrendingUp className="h-4 w-4 text-pink-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{mockStats.views.toLocaleString()}</div>
            <p className="text-xs text-gray-300">
              +12% from last month
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
              {recentContent.map((item) => (
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
                        <span>{item.updatedAt}</span>
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
                    <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white hover:bg-white/10">
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
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
          <div className="space-y-3">
            <div className="flex items-center gap-3 text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-gray-400">2 hours ago</span>
              <span className="text-gray-200">Published &quot;Introduction to Contrastive Learning&quot;</span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-gray-400">1 day ago</span>
              <span className="text-gray-200">Created draft &quot;Federated Learning 101&quot;</span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span className="text-gray-400">3 days ago</span>
              <span className="text-gray-200">Updated settings and preferences</span>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span className="text-gray-400">5 days ago</span>
              <span className="text-gray-200">Generated content using AI writer</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}