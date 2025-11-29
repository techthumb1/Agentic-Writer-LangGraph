// File: frontend/app/status/page.tsx
// Enhanced System Status page for AI Content Studio (Professional - No Emojis)

import { Metadata } from 'next';
import Link from 'next/link';
import { 
  CheckCircle, 
  Clock, 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Mail, 
  Smartphone, 
  Webhook, 
  Calendar, 
  ExternalLink 
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'System Status | AI Content Studio',
  description: 'Real-time status of AI Content Studio services, APIs, and infrastructure.',
};

export default function SystemStatusPage() {
  const currentStatus = {
    overall: 'operational', // operational, degraded, outage
    lastUpdate: '2025-01-15T10:30:00Z',
    uptime: '99.97%'
  };

  const services = [
    {
      name: 'Content Generation API',
      status: 'operational',
      uptime: '99.98%',
      responseTime: '245ms',
      description: 'Core API for generating AI content',
      lastIncident: null
    },
    {
      name: 'LangGraph Workflows',
      status: 'degraded',
      uptime: '99.85%',
      responseTime: '1.2s',
      description: 'Multi-agent workflow orchestration',
      lastIncident: '2025-01-15T08:15:00Z'
    },
    {
      name: 'Authentication Service',
      status: 'operational',
      uptime: '99.99%',
      responseTime: '89ms',
      description: 'User authentication and authorization',
      lastIncident: null
    },
    {
      name: 'Template Engine',
      status: 'operational',
      uptime: '99.95%',
      responseTime: '156ms',
      description: 'Content template processing',
      lastIncident: null
    },
    {
      name: 'Style Profile Service',
      status: 'operational',
      uptime: '99.92%',
      responseTime: '203ms',
      description: 'Content styling and voice management',
      lastIncident: null
    },
    {
      name: 'Dashboard & UI',
      status: 'operational',
      uptime: '99.96%',
      responseTime: '124ms',
      description: 'Web dashboard and user interface',
      lastIncident: null
    },
    {
      name: 'Webhook Delivery',
      status: 'operational',
      uptime: '99.89%',
      responseTime: '678ms',
      description: 'Event notifications and callbacks',
      lastIncident: null
    },
    {
      name: 'File Storage',
      status: 'operational',
      uptime: '99.94%',
      responseTime: '312ms',
      description: 'Content and asset storage',
      lastIncident: null
    }
  ];

  const recentIncidents = [
    {
      id: 1,
      title: 'LangGraph Performance Degradation',
      status: 'investigating',
      severity: 'minor',
      startTime: '2025-01-15T08:15:00Z',
      description: 'We are investigating reports of slower than normal response times for LangGraph workflow executions.',
      updates: [
        {
          time: '2025-01-15T10:30:00Z',
          message: 'We have identified the root cause and are implementing a fix. Expected resolution within 2 hours.'
        },
        {
          time: '2025-01-15T09:45:00Z',
          message: 'Engineering team is investigating the performance issues. We will provide updates every 30 minutes.'
        },
        {
          time: '2025-01-15T08:15:00Z',
          message: 'We are aware of performance issues affecting LangGraph workflows and are investigating.'
        }
      ]
    },
    {
      id: 2,
      title: 'Scheduled Maintenance - Database Optimization',
      status: 'completed',
      severity: 'maintenance',
      startTime: '2025-01-14T02:00:00Z',
      endTime: '2025-01-14T04:30:00Z',
      description: 'Scheduled database optimization to improve overall system performance.',
      updates: [
        {
          time: '2025-01-14T04:30:00Z',
          message: 'Maintenance completed successfully. All services are operating normally.'
        },
        {
          time: '2025-01-14T02:00:00Z',
          message: 'Maintenance window started. Some services may experience brief interruptions.'
        }
      ]
    }
  ];

  const metrics = [
    {
      name: 'API Requests',
      value: '2.4M',
      change: '+12.5%',
      period: 'Last 24h',
      trend: 'up'
    },
    {
      name: 'Average Response Time',
      value: '187ms',
      change: '-8.2%',
      period: 'Last 24h',
      trend: 'down'
    },
    {
      name: 'Success Rate',
      value: '99.94%',
      change: '+0.02%',
      period: 'Last 24h',
      trend: 'up'
    },
    {
      name: 'Content Generated',
      value: '145K',
      change: '+18.7%',
      period: 'Last 24h',
      trend: 'up'
    }
  ];

  const upcomingMaintenance = [
    {
      title: 'AI Model Updates',
      scheduledTime: '2025-01-20T06:00:00Z',
      duration: '2 hours',
      impact: 'Content generation may be temporarily unavailable',
      type: 'update'
    },
    {
      title: 'Infrastructure Scaling',
      scheduledTime: '2025-01-25T03:00:00Z',
      duration: '4 hours',
      impact: 'Brief service interruptions possible',
      type: 'maintenance'
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational':
        return 'text-green-400 bg-green-500/20';
      case 'degraded':
        return 'text-yellow-400 bg-yellow-500/20';
      case 'outage':
        return 'text-red-400 bg-red-500/20';
      default:
        return 'text-gray-400 bg-gray-500/20';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-red-400 bg-red-500/20';
      case 'major':
        return 'text-orange-400 bg-orange-500/20';
      case 'minor':
        return 'text-yellow-400 bg-yellow-500/20';
      case 'maintenance':
        return 'text-blue-400 bg-blue-500/20';
      default:
        return 'text-gray-400 bg-gray-500/20';
    }
  };

  return (
    <div className="container mx-auto px-6 py-12">
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-6">
            System Status
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Real-time status and performance metrics for all AI Content Studio services.
          </p>
          
          {/* Overall Status */}
          <div className="max-w-2xl mx-auto">
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6">
              <div className="flex items-center justify-center gap-4 mb-4">
                <div className={`w-4 h-4 rounded-full ${
                  currentStatus.overall === 'operational' ? 'bg-green-400' :
                  currentStatus.overall === 'degraded' ? 'bg-yellow-400' :
                  'bg-red-400'
                }`}></div>
                <h2 className="text-2xl font-bold text-white">
                  {currentStatus.overall === 'operational' ? 'All Systems Operational' :
                   currentStatus.overall === 'degraded' ? 'Degraded Performance' :
                   'Service Outage'}
                </h2>
              </div>
              <div className="flex justify-center gap-8 text-sm text-gray-300">
                <span className="flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  Last updated: {new Date(currentStatus.lastUpdate).toLocaleString()}
                </span>
                <span className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  Overall uptime: {currentStatus.uptime}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">Performance Metrics</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {metrics.map((metric, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 text-center">
                <h3 className="text-lg font-semibold text-white mb-2">{metric.name}</h3>
                <div className="text-3xl font-bold text-purple-400 mb-2">{metric.value}</div>
                <div className="flex items-center justify-center gap-2 text-sm">
                  <span className={`flex items-center gap-1 ${metric.trend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
                    {metric.trend === 'up' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                    {metric.change}
                  </span>
                  <span className="text-gray-400">{metric.period}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Service Status */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">Service Status</h2>
          <div className="space-y-4">
            {services.map((service, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-2">
                      <div className={`w-3 h-3 rounded-full ${
                        service.status === 'operational' ? 'bg-green-400' :
                        service.status === 'degraded' ? 'bg-yellow-400' :
                        'bg-red-400'
                      }`}></div>
                      <h3 className="text-xl font-semibold text-white">{service.name}</h3>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(service.status)}`}>
                        {service.status.charAt(0).toUpperCase() + service.status.slice(1)}
                      </span>
                    </div>
                    <p className="text-gray-300 mb-4">{service.description}</p>
                  </div>
                  
                  <div className="flex flex-col lg:flex-row gap-4 lg:gap-8 text-sm">
                    <div className="text-center">
                      <div className="text-white font-medium">Uptime</div>
                      <div className="text-green-400">{service.uptime}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-white font-medium">Response Time</div>
                      <div className="text-blue-400">{service.responseTime}</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Recent Incidents */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">Recent Incidents</h2>
          <div className="space-y-6">
            {recentIncidents.map((incident) => (
              <div key={incident.id} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-2">
                      <h3 className="text-xl font-semibold text-white">{incident.title}</h3>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(incident.severity)}`}>
                        {incident.severity.charAt(0).toUpperCase() + incident.severity.slice(1)}
                      </span>
                    </div>
                    <p className="text-gray-300 mb-4">{incident.description}</p>
                    <div className="text-sm text-gray-400">
                      Started: {new Date(incident.startTime).toLocaleString()}
                      {incident.endTime && (
                        <span> • Resolved: {new Date(incident.endTime).toLocaleString()}</span>
                      )}
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    incident.status === 'resolved' ? 'text-green-400 bg-green-500/20' :
                    incident.status === 'investigating' ? 'text-yellow-400 bg-yellow-500/20' :
                    'text-blue-400 bg-blue-500/20'
                  }`}>
                    {incident.status.charAt(0).toUpperCase() + incident.status.slice(1)}
                  </span>
                </div>
                
                {/* Incident Updates */}
                <div className="mt-6">
                  <h4 className="text-lg font-semibold text-white mb-4">Updates</h4>
                  <div className="space-y-4">
                    {incident.updates.map((update, updateIndex) => (
                      <div key={updateIndex} className="border-l-2 border-purple-500 pl-4">
                        <div className="text-sm text-gray-400 mb-1">
                          {new Date(update.time).toLocaleString()}
                        </div>
                        <p className="text-gray-300">{update.message}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Upcoming Maintenance */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">Scheduled Maintenance</h2>
          {upcomingMaintenance.length > 0 ? (
            <div className="space-y-4">
              {upcomingMaintenance.map((maintenance, index) => (
                <div key={index} className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-white mb-2">{maintenance.title}</h3>
                      <p className="text-gray-300 mb-4">{maintenance.impact}</p>
                      <div className="text-sm text-gray-400">
                        <span className="flex items-center gap-2">
                          <Calendar className="w-4 h-4" />
                          Scheduled: {new Date(maintenance.scheduledTime).toLocaleString()}
                        </span>
                        <span className="flex items-center gap-2 ml-4 mt-1">
                          <Clock className="w-4 h-4" />
                          Duration: {maintenance.duration}
                        </span>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      maintenance.type === 'maintenance' ? 'text-blue-400 bg-blue-500/20' :
                      'text-purple-400 bg-purple-500/20'
                    }`}>
                      {maintenance.type.charAt(0).toUpperCase() + maintenance.type.slice(1)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8 text-center">
              <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No Scheduled Maintenance</h3>
              <p className="text-gray-300">All services are running normally with no planned maintenance windows.</p>
            </div>
          )}
        </section>

        {/* Subscribe to Updates */}
        <section className="mb-16">
          <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm border border-white/20 rounded-xl p-8 text-center">
            <h2 className="text-2xl font-bold text-white mb-4">Stay Informed</h2>
            <p className="text-gray-300 mb-6">
              Get notified about service updates, maintenance windows, and incident resolutions.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-6 py-3 rounded-lg transition-all duration-300 inline-flex items-center justify-center gap-2">
                <Mail className="w-4 h-4" />
                Subscribe to Email Updates
              </button>
              <button className="border border-white/30 text-white hover:bg-white/10 font-semibold px-6 py-3 rounded-lg transition-all duration-300 inline-flex items-center justify-center gap-2">
                <Smartphone className="w-4 h-4" />
                SMS Notifications
              </button>
              <Link href="/docs/webhooks" className="border border-purple-500/50 text-purple-400 hover:bg-purple-500/10 font-semibold px-6 py-3 rounded-lg transition-all duration-300 inline-flex items-center justify-center gap-2">
                <Webhook className="w-4 h-4" />
                Webhook Integration
              </Link>
            </div>
          </div>
        </section>

        {/* Historical Data */}
        <section>
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">Historical Uptime</h2>
            <div className="grid md:grid-cols-3 gap-6 text-center">
              <div>
                <div className="text-3xl font-bold text-green-400 mb-2">99.97%</div>
                <p className="text-gray-300">Last 30 days</p>
              </div>
              <div>
                <div className="text-3xl font-bold text-green-400 mb-2">99.95%</div>
                <p className="text-gray-300">Last 90 days</p>
              </div>
              <div>
                <div className="text-3xl font-bold text-green-400 mb-2">99.94%</div>
                <p className="text-gray-300">Last 12 months</p>
              </div>
            </div>
            <div className="mt-6 text-center">
              <Link href="/status/history" className="text-purple-400 hover:text-purple-300 font-medium inline-flex items-center gap-2">
                View Detailed History
                <ExternalLink className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}