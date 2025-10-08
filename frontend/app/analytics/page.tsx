// File: frontend/app/analytics/page.tsx

'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart3, 
  FileText, 
  Zap, 
  Clock, 
  Target,
  Activity,
  Calendar,
  Loader2
} from 'lucide-react';

interface AnalyticsData {
  totalGenerations: number;
  totalWords: number;
  avgGenerationTime: number;
  mostUsedTemplate: string;
  mostUsedStyle: string;
  successRate: number;
}

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');

  useEffect(() => {
    async function fetchAnalytics() {
      try {
        setLoading(true);
        const response = await fetch(`/api/analytics/insights?range=${timeRange}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch analytics');
        }
        
        const data = await response.json();
        setAnalytics(data);
        } catch (error) {
          console.error('Analytics fetch error:', error);
          setAnalytics(null); // Let UI show "No data available"
        } finally {
        setLoading(false);
      }
    }

    fetchAnalytics();
  }, [timeRange]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-400 text-lg mb-2">No analytics data available</p>
          <p className="text-gray-500 text-sm">Generate content to see insights</p>
        </div>
      </div>
    );
  }

  const stats = [
    {
      title: 'Total Generations',
      value: analytics?.totalGenerations || 0,
      icon: FileText,
      change: '+12.5%',
      trend: 'up'
    },
    {
      title: 'Words Generated',
      value: (analytics?.totalWords || 0).toLocaleString(),
      icon: BarChart3,
      change: '+18.2%',
      trend: 'up'
    },
    {
      title: 'Avg Time',
      value: `${analytics?.avgGenerationTime || 0}s`,
      icon: Clock,
      change: '-8.3%',
      trend: 'down'
    },
    {
      title: 'Success Rate',
      value: `${analytics?.successRate || 0}%`,
      icon: Target,
      change: '+2.1%',
      trend: 'up'
    }
  ];

  return (
    <div className="container mx-auto px-6 py-12">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Analytics Dashboard</h1>
          <p className="text-gray-300">Track your content generation performance and insights</p>
        </div>

        {/* Time Range Selector */}
        <div className="flex gap-2 mb-6">
          {(['7d', '30d', '90d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                timeRange === range
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                  : 'bg-white/10 text-gray-300 hover:bg-white/20'
              }`}
            >
              {range === '7d' ? 'Last 7 Days' : range === '30d' ? 'Last 30 Days' : 'Last 90 Days'}
            </button>
          ))}
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <Card key={index} className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-gray-300">
                  {stat.title}
                </CardTitle>
                <stat.icon className="h-4 w-4 text-purple-400" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
                <p className={`text-xs ${stat.trend === 'up' ? 'text-green-400' : 'text-blue-400'}`}>
                  {stat.change} from last period
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Main Content */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="bg-white/10 backdrop-blur-sm border-white/20">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="templates" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Templates
            </TabsTrigger>
            <TabsTrigger value="performance" className="flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Performance
            </TabsTrigger>
            <TabsTrigger value="usage" className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Usage
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-white/10 backdrop-blur-sm border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Most Used Templates</CardTitle>
                  <CardDescription className="text-gray-300">
                    Your top templates by generation count
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-white">Blog Article</span>
                      <span className="text-purple-400 font-semibold">42</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-white">Technical Documentation</span>
                      <span className="text-purple-400 font-semibold">31</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-white">Social Media Campaign</span>
                      <span className="text-purple-400 font-semibold">28</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white/10 backdrop-blur-sm border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Content Quality</CardTitle>
                  <CardDescription className="text-gray-300">
                    Average quality metrics
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-white">Readability</span>
                        <span className="text-purple-400">8.5/10</span>
                      </div>
                      <div className="w-full bg-white/10 rounded-full h-2">
                        <div className="bg-purple-500 h-2 rounded-full" style={{ width: '85%' }} />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-white">Engagement</span>
                        <span className="text-purple-400">7.8/10</span>
                      </div>
                      <div className="w-full bg-white/10 rounded-full h-2">
                        <div className="bg-purple-500 h-2 rounded-full" style={{ width: '78%' }} />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-white">SEO Score</span>
                        <span className="text-purple-400">9.2/10</span>
                      </div>
                      <div className="w-full bg-white/10 rounded-full h-2">
                        <div className="bg-purple-500 h-2 rounded-full" style={{ width: '92%' }} />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="templates">
            <Card className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Template Usage Details</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">Template analytics coming soon...</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="performance">
            <Card className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Performance Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">Performance analytics coming soon...</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="usage">
            <Card className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Usage Patterns</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">Usage analytics coming soon...</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}