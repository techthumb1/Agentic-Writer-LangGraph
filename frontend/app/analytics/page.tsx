// File: frontend/app/analytics/page.tsx
/* eslint-disable @typescript-eslint/no-explicit-any */

'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
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

// Dynamic imports for recharts to avoid SSR issues
const LineChart = dynamic(() => import('recharts').then(mod => mod.LineChart as any), { ssr: false }) as any;
const Line = dynamic(() => import('recharts').then(mod => mod.Line as any), { ssr: false }) as any;
const BarChart = dynamic(() => import('recharts').then(mod => mod.BarChart as any), { ssr: false }) as any;
const Bar = dynamic(() => import('recharts').then(mod => mod.Bar as any), { ssr: false }) as any;
const XAxis = dynamic(() => import('recharts').then(mod => mod.XAxis as any), { ssr: false }) as any;
const YAxis = dynamic(() => import('recharts').then(mod => mod.YAxis as any), { ssr: false }) as any;
const CartesianGrid = dynamic(() => import('recharts').then(mod => mod.CartesianGrid as any), { ssr: false }) as any;
const Tooltip = dynamic(() => import('recharts').then(mod => mod.Tooltip as any), { ssr: false }) as any;
const Legend = dynamic(() => import('recharts').then(mod => mod.Legend as any), { ssr: false }) as any;

interface AnalyticsData {
  totalGenerations: number;
  totalWords: number;
  avgGenerationTime: number;
  mostUsedTemplate: string;
  mostUsedStyle: string;
  successRate: number;
}

interface TemplateData {
  id: string;
  name: string;
  usageCount: number;
  avgTime: number;
  successRate: number;
  totalWords: number;
}

interface PerformanceData {
  dailyStats: {
    date: string;
    count: number;
    avgTime: number;
    successRate: number;
  }[];
}

interface UsageData {
  hourlyDistribution: { hour: number; count: number }[];
  dailyTotals: { date: string; count: number }[];
}

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [templateData, setTemplateData] = useState<TemplateData[]>([]);
  const [performanceData, setPerformanceData] = useState<PerformanceData | null>(null);
  const [usageData, setUsageData] = useState<UsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');

  useEffect(() => {
    async function fetchAllAnalytics() {
      try {
        setLoading(true);
        
        const [insights, templates, performance, usage] = await Promise.all([
          fetch(`/api/analytics/insights?range=${timeRange}`).then(r => r.ok ? r.json() : null),
          fetch(`/api/analytics/templates?range=${timeRange}`).then(r => r.ok ? r.json() : null),
          fetch(`/api/analytics/performance?range=${timeRange}`).then(r => r.ok ? r.json() : null),
          fetch(`/api/analytics/usage?range=${timeRange}`).then(r => r.ok ? r.json() : null)
        ]);
        
        setAnalytics(insights);
        setTemplateData(templates?.templates || []);
        setPerformanceData(performance);
        setUsageData(usage);
      } catch (error) {
        console.error('Analytics fetch error:', error);
        setAnalytics(null);
      } finally {
        setLoading(false);
      }
    }

    fetchAllAnalytics();
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
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Analytics Dashboard</h1>
          <p className="text-gray-300">Track your content generation performance and insights</p>
        </div>

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
                    {templateData.slice(0, 3).map((template) => (
                      <div key={template.id} className="flex items-center justify-between">
                        <span className="text-white">{template.name}</span>
                        <span className="text-purple-400 font-semibold">{template.usageCount}</span>
                      </div>
                    ))}
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
                <CardTitle className="text-white">Template Usage</CardTitle>
                <CardDescription className="text-gray-300">
                  Performance by template type
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {templateData.length > 0 ? (
                    templateData.slice(0, 10).map((template) => (
                      <div key={template.id} className="flex items-center justify-between py-3 border-b border-white/10">
                        <div className="flex-1">
                          <h4 className="text-white font-medium">{template.name}</h4>
                          <p className="text-sm text-gray-400">{template.usageCount} generations • {template.totalWords.toLocaleString()} words</p>
                        </div>
                        <div className="flex gap-6 text-right">
                          <div>
                            <p className="text-purple-400 font-semibold">{template.avgTime}s</p>
                            <p className="text-xs text-gray-400">Avg Time</p>
                          </div>
                          <div>
                            <p className="text-green-400 font-semibold">{template.successRate}%</p>
                            <p className="text-xs text-gray-400">Success</p>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-400">No template data available</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="performance">
            <Card className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Performance Trends</CardTitle>
                <CardDescription className="text-gray-300">
                  Generation time and success rate over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                {performanceData?.dailyStats && performanceData.dailyStats.length > 0 ? (
                  <div style={{ width: '100%', height: 300 }}>
                    <div style={{ width: '100%', height: 300 }}>
                      <LineChart width={800} height={300} data={performanceData.dailyStats}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                        <XAxis dataKey="date" stroke="#9ca3af" />
                        <YAxis stroke="#9ca3af" />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                          labelStyle={{ color: '#f3f4f6' }}
                        />
                        <Legend />
                        <Line type="monotone" dataKey="avgTime" stroke="#a855f7" name="Avg Time (s)" strokeWidth={2} />
                        <Line type="monotone" dataKey="successRate" stroke="#22c55e" name="Success Rate %" strokeWidth={2} />
                      </LineChart>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-400">No performance data available</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="usage">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-white/10 backdrop-blur-sm border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Hourly Distribution</CardTitle>
                  <CardDescription className="text-gray-300">Peak usage hours</CardDescription>
                </CardHeader>
                <CardContent>
                  {usageData?.hourlyDistribution && usageData.hourlyDistribution.length > 0 ? (
                    <div style={{ width: '100%', height: 300 }}>
                      <div style={{ width: '100%', height: 300 }}>
                        <BarChart width={400} height={300} data={usageData.hourlyDistribution}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                          <XAxis dataKey="hour" stroke="#9ca3af" />
                          <YAxis stroke="#9ca3af" />
                          <Tooltip 
                            contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                            labelStyle={{ color: '#f3f4f6' }}
                          />
                          <Bar dataKey="count" fill="#a855f7" />
                        </BarChart>
                      </div>
                    </div>
                  ) : (
                    <p className="text-gray-400">No hourly data available</p>
                  )}
                </CardContent>
              </Card>
              
              <Card className="bg-white/10 backdrop-blur-sm border-white/20">
                <CardHeader>
                  <CardTitle className="text-white">Daily Activity</CardTitle>
                  <CardDescription className="text-gray-300">Generations per day</CardDescription>
                </CardHeader>
                <CardContent>
                  {usageData?.dailyTotals && usageData.dailyTotals.length > 0 ? (
                    <div style={{ width: '100%', height: 300 }}>
                      <div style={{ width: '100%', height: 300 }}>
                        <BarChart width={400} height={300} data={usageData.dailyTotals}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
                          <XAxis dataKey="date" stroke="#9ca3af" />
                          <YAxis stroke="#9ca3af" />
                          <Tooltip 
                            contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                            labelStyle={{ color: '#f3f4f6' }}
                          />
                          <Bar dataKey="count" fill="#ec4899" />
                        </BarChart>
                      </div>
                    </div>
                  ) : (
                    <p className="text-gray-400">No daily data available</p>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}