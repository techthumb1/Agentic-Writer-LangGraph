'use client'

import React, { useState } from 'react';
import { 
  Settings, 
  User, 
  Shield, 
  Bell, 
  Palette, 
  Database, 
  Globe, 
  Key, 
  CreditCard, 
  Users, 
  FileText, 
  Brain, 
  Zap, 
  Mail, 
  Smartphone, 
  Monitor, 
  Moon, 
  Sun, 
  Volume2, 
  Eye, 
  Lock, 
  Trash2, 
  Download, 
  Upload, 
  RefreshCw, 
  ChevronRight,
  Save,
  Edit,
  BarChart3,
  Cpu
} from 'lucide-react';

const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState('profile');

  const settingsCategories = [
    {
      id: 'profile',
      label: 'Profile & Account',
      icon: User,
      description: 'Manage your personal information and account preferences'
    },
    {
      id: 'security',
      label: 'Security & Privacy',
      icon: Shield,
      description: 'Control your security settings and data privacy'
    },
    {
      id: 'notifications',
      label: 'Notifications',
      icon: Bell,
      description: 'Configure how and when you receive notifications'
    },
    {
      id: 'appearance',
      label: 'Appearance',
      icon: Palette,
      description: 'Customize the look and feel of your workspace'
    },
    {
      id: 'ai-settings',
      label: 'AI Configuration',
      icon: Brain,
      description: 'Configure AI models and generation preferences'
    },
    {
      id: 'data',
      label: 'Data & Storage',
      icon: Database,
      description: 'Manage your data, exports, and storage settings'
    },
    {
      id: 'billing',
      label: 'Billing & Usage',
      icon: CreditCard,
      description: 'View usage statistics and manage billing information'
    },
    {
      id: 'team',
      label: 'Team & Collaboration',
      icon: Users,
      description: 'Manage team members and collaboration settings'
    }
  ];

  const SettingsHeader = () => (
    <div className="border-b border-gray-200 pb-6 mb-6">
      <div className="flex items-center gap-3 mb-2">
        <Settings size={32} className="text-blue-600" />
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
      </div>
      <p className="text-gray-600">Manage your account settings and preferences</p>
    </div>
  );

  const SettingsSidebar = () => (
    <div className="w-80 bg-gray-50 border-r border-gray-200 p-6">
      <nav className="space-y-2">
        {settingsCategories.map((category) => (
          <button
            key={category.id}
            onClick={() => setActiveTab(category.id)}
            className={`w-full flex items-center gap-3 p-3 rounded-lg text-left transition-colors ${
              activeTab === category.id
                ? 'bg-blue-100 text-blue-700 border border-blue-200'
                : 'hover:bg-gray-100 text-gray-700'
            }`}
          >
            <category.icon size={20} />
            <div className="flex-1 min-w-0">
              <div className="font-medium">{category.label}</div>
              <div className="text-sm text-gray-500 truncate">{category.description}</div>
            </div>
            <ChevronRight size={16} className={activeTab === category.id ? 'text-blue-600' : 'text-gray-400'} />
          </button>
        ))}
      </nav>
    </div>
  );

  const ProfileSettings = () => (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <User size={24} className="text-blue-600" />
        <h2 className="text-2xl font-semibold">Profile & Account</h2>
      </div>

      <div className="grid gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Edit size={20} className="text-gray-600" />
            <h3 className="text-lg font-medium">Personal Information</h3>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your full name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
              <input
                type="email"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your email"
              />
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Globe size={20} className="text-gray-600" />
            <h3 className="text-lg font-medium">Regional Settings</h3>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>English (US)</option>
                <option>English (UK)</option>
                <option>Spanish</option>
                <option>French</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>UTC-05:00 (Eastern Time)</option>
                <option>UTC-06:00 (Central Time)</option>
                <option>UTC-07:00 (Mountain Time)</option>
                <option>UTC-08:00 (Pacific Time)</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const SecuritySettings = () => (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Shield size={24} className="text-blue-600" />
        <h2 className="text-2xl font-semibold">Security & Privacy</h2>
      </div>

      <div className="grid gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Key size={20} className="text-gray-600" />
            <h3 className="text-lg font-medium">Authentication</h3>
          </div>
          <div className="space-y-4">
            <button className="flex items-center gap-3 w-full p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
              <Lock size={20} className="text-gray-600" />
              <div className="text-left">
                <div className="font-medium">Change Password</div>
                <div className="text-sm text-gray-500">Update your account password</div>
              </div>
            </button>
            <button className="flex items-center gap-3 w-full p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
              <Smartphone size={20} className="text-gray-600" />
              <div className="text-left">
                <div className="font-medium">Two-Factor Authentication</div>
                <div className="text-sm text-gray-500">Add an extra layer of security</div>
              </div>
            </button>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Eye size={20} className="text-gray-600" />
            <h3 className="text-lg font-medium">Privacy Controls</h3>
          </div>
          <div className="space-y-3">
            <label className="flex items-center gap-3">
              <input type="checkbox" className="rounded" defaultChecked />
              <span>Allow analytics data collection</span>
            </label>
            <label className="flex items-center gap-3">
              <input type="checkbox" className="rounded" />
              <span>Share usage data for improvements</span>
            </label>
            <label className="flex items-center gap-3">
              <input type="checkbox" className="rounded" defaultChecked />
              <span>Enable security monitoring</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const NotificationSettings = () => (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Bell size={24} className="text-blue-600" />
        <h2 className="text-2xl font-semibold">Notifications</h2>
      </div>

      <div className="grid gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Mail size={20} className="text-gray-600" />
            <h3 className="text-lg font-medium">Email Notifications</h3>
          </div>
          <div className="space-y-3">
            <label className="flex items-center justify-between">
              <span>Content generation completed</span>
              <input type="checkbox" className="rounded" defaultChecked />
            </label>
            <label className="flex items-center justify-between">
              <span>Weekly analytics summary</span>
              <input type="checkbox" className="rounded" defaultChecked />
            </label>
            <label className="flex items-center justify-between">
              <span>Team collaboration updates</span>
              <input type="checkbox" className="rounded" />
            </label>
            <label className="flex items-center justify-between">
              <span>Security alerts</span>
              <input type="checkbox" className="rounded" defaultChecked />
            </label>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Smartphone size={20} className="text-gray-600" />
            <h3 className="text-lg font-medium">Push Notifications</h3>
          </div>
          <div className="space-y-3">
            <label className="flex items-center justify-between">
              <span>Real-time generation updates</span>
              <input type="checkbox" className="rounded" />
            </label>
            <label className="flex items-center justify-between">
              <span>System maintenance alerts</span>
              <input type="checkbox" className="rounded" defaultChecked />
            </label>
            <label className="flex items-center justify-between">
              <span>Usage limit warnings</span>
              <input type="checkbox" className="rounded" defaultChecked />
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const AppearanceSettings = () => (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Palette size={24} className="text-blue-600" />
        <h2 className="text-2xl font-semibold">Appearance</h2>
      </div>

      <div className="grid gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Monitor size={20} className="text-gray-600" />
            <h3 className="text-lg font-medium">Display Settings</h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Theme</label>
              <div className="flex gap-3">
                <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg bg-white">
                  <Sun size={16} />
                  Light
                </button>
                <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg">
                  <Moon size={16} />
                  Dark
                </button>
                <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg">
                  <Monitor size={16} />
                  System
                </button>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Density</label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>Comfortable</option>
                <option>Compact</option>
                <option>Spacious</option>
              </select>
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Volume2 size={20} className="text-gray-600" />
            <h3 className="text-lg font-medium">Sound Settings</h3>
          </div>
          <div className="space-y-3">
            <label className="flex items-center justify-between">
              <span>Enable sound effects</span>
              <input type="checkbox" className="rounded" defaultChecked />
            </label>
            <label className="flex items-center justify-between">
              <span>Notification sounds</span>
              <input type="checkbox" className="rounded" />
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const AISettings = () => (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Brain size={24} className="text-blue-600" />
        <h2 className="text-2xl font-semibold">AI Configuration</h2>
      </div>

      <div className="grid gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Cpu size={20} className="text-gray-600" />
            <h3 className="text-lg font-medium">Model Preferences</h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Default AI Model</label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>GPT-4 Turbo</option>
                <option>Claude 3 Sonnet</option>
                <option>GPT-3.5 Turbo</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Creativity Level</label>
              <input type="range" className="w-full" min="0" max="100" defaultValue="70" />
              <div className="flex justify-between text-sm text-gray-500 mt-1">
                <span>Conservative</span>
                <span>Creative</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Zap size={20} className="text-gray-600" />
            <h3 className="text-lg font-medium">Generation Settings</h3>
          </div>
          <div className="space-y-3">
            <label className="flex items-center justify-between">
              <span>Enable auto-save drafts</span>
              <input type="checkbox" className="rounded" defaultChecked />
            </label>
            <label className="flex items-center justify-between">
              <span>Show generation progress</span>
              <input type="checkbox" className="rounded" defaultChecked />
            </label>
            <label className="flex items-center justify-between">
              <span>Enable content suggestions</span>
              <input type="checkbox" className="rounded" />
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const DataSettings = () => (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Database size={24} className="text-blue-600" />
        <h2 className="text-2xl font-semibold">Data & Storage</h2>
      </div>

      <div className="grid gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 size={20} className="text-gray-600" />
            <h3 className="text-lg font-medium">Usage Statistics</h3>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">2.4GB</div>
              <div className="text-sm text-gray-600">Storage Used</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">847</div>
              <div className="text-sm text-gray-600">Documents Created</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">12.3K</div>
              <div className="text-sm text-gray-600">AI Requests</div>
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText size={20} className="text-gray-600" />
            <h3 className="text-lg font-medium">Data Management</h3>
          </div>
          <div className="space-y-3">
            <button className="flex items-center gap-3 w-full p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
              <Download size={20} className="text-gray-600" />
              <div className="text-left">
                <div className="font-medium">Export All Data</div>
                <div className="text-sm text-gray-500">Download your content and settings</div>
              </div>
            </button>
            <button className="flex items-center gap-3 w-full p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
              <Upload size={20} className="text-gray-600" />
              <div className="text-left">
                <div className="font-medium">Import Data</div>
                <div className="text-sm text-gray-500">Import content from other platforms</div>
              </div>
            </button>
            <button className="flex items-center gap-3 w-full p-3 border border-red-200 rounded-lg hover:bg-red-50 text-red-600">
              <Trash2 size={20} />
              <div className="text-left">
                <div className="font-medium">Delete All Data</div>
                <div className="text-sm text-red-500">Permanently remove all your data</div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'profile': return <ProfileSettings />;
      case 'security': return <SecuritySettings />;
      case 'notifications': return <NotificationSettings />;
      case 'appearance': return <AppearanceSettings />;
      case 'ai-settings': return <AISettings />;
      case 'data': return <DataSettings />;
      default: return <ProfileSettings />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white">
          <div className="p-6">
            <SettingsHeader />
          </div>
          
          <div className="flex">
            <SettingsSidebar />
            
            <div className="flex-1 p-6">
              {renderActiveTab()}
              
              <div className="mt-8 pt-6 border-t border-gray-200">
                <div className="flex items-center gap-3">
                  <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    <Save size={16} />
                    Save Changes
                  </button>
                  <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                    <RefreshCw size={16} />
                    Reset to Defaults
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;