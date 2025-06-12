'use client';

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch'
import { 
  UserCog, 
  CreditCard, 
  Bell, 
  Shield, 
  Palette, 
  Globe, 
  Zap,
  Settings,
  Moon,
  Sun,
  Monitor,
  Lock,
  Smartphone,
  Mail,
  Download,
  Trash2
} from 'lucide-react';

export default function SettingsPage() {
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    marketing: false,
    security: true
  });
  const [privacy, setPrivacy] = useState({
    analytics: true,
    profileVisible: false,
    dataSharing: false
  });

  const handleNotificationChange = (type: string, value: boolean) => {
    setNotifications(prev => ({ ...prev, [type]: value }));
  };

  const handlePrivacyChange = (type: string, value: boolean) => {
    setPrivacy(prev => ({ ...prev, [type]: value }));
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 p-6 text-gray-900 dark:text-white">
      {/* Header Section */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-3 mb-4">
          <div className="p-3 rounded-full bg-gradient-to-br from-blue-500 to-purple-600">
            <Settings className="h-8 w-8 text-white" />
          </div>
        </div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-green-600 bg-clip-text text-transparent">
          Account Settings
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Customize your experience, manage your account, and control your privacy preferences.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Profile Section */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <UserCog className="h-5 w-5 text-blue-600" />
              Profile Information
            </CardTitle>
            <CardDescription>Manage your personal information and account details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Email Address</label>
                <p className="text-sm bg-gray-50 dark:bg-gray-800 p-2 rounded border">creator@example.com</p>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Username</label>
                <p className="text-sm bg-gray-50 dark:bg-gray-800 p-2 rounded border">ai_writer_pro</p>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Account Type</label>
                <Badge variant="outline" className="text-xs">Individual</Badge>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Member Since</label>
                <p className="text-sm text-gray-600 dark:text-gray-400">January 2024</p>
              </div>
            </div>
            <div className="flex gap-2 pt-2">
              <Button variant="outline" size="sm">
                <Mail className="h-4 w-4 mr-2" />
                Update Email
              </Button>
              <Button variant="outline" size="sm">
                <UserCog className="h-4 w-4 mr-2" />
                Edit Profile
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Subscription Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="h-5 w-5 text-purple-600" />
              Subscription & Usage
            </CardTitle>
            <CardDescription>Your current plan and usage statistics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <Badge variant="secondary" className="text-sm px-3 py-1">Free Plan</Badge>
              <span className="text-xs text-gray-500">Renews monthly</span>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Content Generations</span>
                <span className="font-medium">2 / 5</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full" style={{width: '40%'}}></div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>API Calls</span>
                <span className="font-medium">148 / 1,000</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div className="bg-gradient-to-r from-green-500 to-blue-600 h-2 rounded-full" style={{width: '14.8%'}}></div>
              </div>
            </div>

            <Button className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white">
              <Zap className="h-4 w-4 mr-2" />
              Upgrade to Pro
            </Button>
          </CardContent>
        </Card>

        {/* Appearance Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Palette className="h-5 w-5 text-green-600" />
              Appearance
            </CardTitle>
            <CardDescription>Customize your visual experience</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <label className="text-sm font-medium">Theme Preference</label>
              <div className="grid grid-cols-3 gap-2">
                <Button variant="outline" size="sm" className="flex flex-col gap-1 h-auto py-3">
                  <Sun className="h-4 w-4" />
                  <span className="text-xs">Light</span>
                </Button>
                <Button variant="outline" size="sm" className="flex flex-col gap-1 h-auto py-3 bg-gray-100 dark:bg-gray-800">
                  <Moon className="h-4 w-4" />
                  <span className="text-xs">Dark</span>
                </Button>
                <Button variant="outline" size="sm" className="flex flex-col gap-1 h-auto py-3">
                  <Monitor className="h-4 w-4" />
                  <span className="text-xs">Auto</span>
                </Button>
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <label className="text-sm font-medium">Compact Mode</label>
                <p className="text-xs text-gray-500">Reduce spacing and padding</p>
              </div>
              <Switch />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <label className="text-sm font-medium">High Contrast</label>
                <p className="text-xs text-gray-500">Improve accessibility</p>
              </div>
              <Switch />
            </div>
          </CardContent>
        </Card>

        {/* Notifications Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-orange-600" />
              Notifications
            </CardTitle>
            <CardDescription>Control when and how you are notified</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <label className="text-sm font-medium">Email Notifications</label>
                <p className="text-xs text-gray-500">Account updates and alerts</p>
              </div>
              <Switch 
                checked={notifications.email}
                onCheckedChange={(value) => handleNotificationChange('email', value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <label className="text-sm font-medium">Push Notifications</label>
                <p className="text-xs text-gray-500">Browser notifications</p>
              </div>
              <Switch 
                checked={notifications.push}
                onCheckedChange={(value) => handleNotificationChange('push', value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <label className="text-sm font-medium">Marketing Emails</label>
                <p className="text-xs text-gray-500">Product updates and tips</p>
              </div>
              <Switch 
                checked={notifications.marketing}
                onCheckedChange={(value) => handleNotificationChange('marketing', value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <label className="text-sm font-medium">Security Alerts</label>
                <p className="text-xs text-gray-500">Login and security notifications</p>
              </div>
              <Switch 
                checked={notifications.security}
                onCheckedChange={(value) => handleNotificationChange('security', value)}
              />
            </div>
          </CardContent>
        </Card>

        {/* Privacy & Security Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-red-600" />
              Privacy & Security
            </CardTitle>
            <CardDescription>Manage your privacy and security settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <label className="text-sm font-medium">Usage Analytics</label>
                <p className="text-xs text-gray-500">Help improve our services</p>
              </div>
              <Switch 
                checked={privacy.analytics}
                onCheckedChange={(value) => handlePrivacyChange('analytics', value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <label className="text-sm font-medium">Public Profile</label>
                <p className="text-xs text-gray-500">Make profile visible to others</p>
              </div>
              <Switch 
                checked={privacy.profileVisible}
                onCheckedChange={(value) => handlePrivacyChange('profileVisible', value)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <label className="text-sm font-medium">Data Sharing</label>
                <p className="text-xs text-gray-500">Share anonymized data</p>
              </div>
              <Switch 
                checked={privacy.dataSharing}
                onCheckedChange={(value) => handlePrivacyChange('dataSharing', value)}
              />
            </div>

            <div className="flex gap-2 pt-2 border-t">
              <Button variant="outline" size="sm">
                <Lock className="h-4 w-4 mr-2" />
                Change Password
              </Button>
              <Button variant="outline" size="sm">
                <Smartphone className="h-4 w-4 mr-2" />
                2FA Setup
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Language & Region */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5 text-blue-600" />
              Language & Region
            </CardTitle>
            <CardDescription>Localization preferences</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Language</label>
              <select className="w-full p-2 border rounded text-sm bg-white dark:bg-gray-800 dark:border-gray-600">
                <option>English (US)</option>
                <option>English (UK)</option>
                <option>Spanish</option>
                <option>French</option>
                <option>German</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Timezone</label>
              <select className="w-full p-2 border rounded text-sm bg-white dark:bg-gray-800 dark:border-gray-600">
                <option>Pacific Standard Time (PST)</option>
                <option>Eastern Standard Time (EST)</option>
                <option>Central European Time (CET)</option>
                <option>UTC</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Date Format</label>
              <select className="w-full p-2 border rounded text-sm bg-white dark:bg-gray-800 dark:border-gray-600">
                <option>MM/DD/YYYY</option>
                <option>DD/MM/YYYY</option>
                <option>YYYY-MM-DD</option>
              </select>
            </div>
          </CardContent>
        </Card>

        {/* Data Management Section */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Download className="h-5 w-5 text-indigo-600" />
              Data Management
            </CardTitle>
            <CardDescription>Export your data or delete your account</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <h4 className="font-medium text-sm">Export Data</h4>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Download a copy of all your data including content, settings, and usage history.
                </p>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Request Export
                </Button>
              </div>
              
              <div className="space-y-3">
                <h4 className="font-medium text-sm text-red-600 dark:text-red-400">Danger Zone</h4>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  Permanently delete your account and all associated data. This action cannot be undone.
                </p>
                <Button variant="outline" size="sm" className="text-red-600 border-red-200 hover:bg-red-50 dark:border-red-800 dark:hover:bg-red-950">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Account
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Footer */}
      <div className="text-center pt-8 border-t text-sm text-gray-500">
        <p>Need help? Contact our support team or visit our documentation.</p>
        <div className="flex justify-center gap-4 mt-2">
          <Button variant="link" size="sm" className="text-xs">Support Center</Button>
          <Button variant="link" size="sm" className="text-xs">API Documentation</Button>
          <Button variant="link" size="sm" className="text-xs">Privacy Policy</Button>
        </div>
      </div>
    </div>
  );
}