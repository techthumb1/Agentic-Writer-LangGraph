// app/settings/page.tsx

'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useToast } from '@/hooks/use-toast'
import { 
  Settings, 
  User, 
  Bell, 
  Palette, 
  Database, 
  Shield, 
  Download, 
  Upload,
  Save,
  AlertCircle
} from 'lucide-react'

interface UserSettings {
  name: string
  email: string
  bio: string
  notifications: {
    email: boolean
    push: boolean
    marketing: boolean
  }
  theme: 'light' | 'dark' | 'system'
  language: string
  timezone: string
}

interface GenerationSettings {
  maxTokens: number
  temperature: number
  autoSave: boolean
  backupFrequency: string
  contentQuality: 'fast' | 'balanced' | 'premium'
  enableMultiModel: boolean
}

export default function SettingsPage() {
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [userSettings, setUserSettings] = useState<UserSettings>({
    name: '',
    email: '',
    bio: '',
    notifications: {
      email: true,
      push: false,
      marketing: false
    },
    theme: 'system',
    language: 'en',
    timezone: 'UTC'
  })

  const [generationSettings, setGenerationSettings] = useState<GenerationSettings>({
    maxTokens: 2000,
    temperature: 0.7,
    autoSave: true,
    backupFrequency: 'daily',
    contentQuality: 'balanced',
    enableMultiModel: true
  })

  // Load settings on component mount
  useEffect(() => {
    const loadSettings = async () => {
      try {
        setIsLoading(true)
        // Replace with actual API call
        const response = await fetch('/api/settings')
        if (response.ok) {
          const data = await response.json()
          setUserSettings(data.userSettings || userSettings)
          setGenerationSettings(data.generationSettings || generationSettings)
        }
      } catch (err) {
        console.error('Failed to load settings:', err)
        toast({
          title: 'Error',
          description: 'Failed to load settings',
          variant: 'destructive'
        })
      } finally {
        setIsLoading(false)
      }
    }

    loadSettings()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const saveUserSettings = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('/api/settings/user', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userSettings)
      })
      
      if (response.ok) {
        toast({
          title: 'Success',
          description: 'User settings saved successfully'
        })
      } else {
        throw new Error('Failed to save settings')
      }
    } catch (err) {
      console.error('Failed to save user settings:', err)
      toast({
        title: 'Error',
        description: 'Failed to save user settings',
        variant: 'destructive'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const saveGenerationSettings = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('/api/settings/generation', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(generationSettings)
      })
      
      if (response.ok) {
        toast({
          title: 'Success',
          description: 'Generation settings saved successfully'
        })
      } else {
        throw new Error('Failed to save settings')
      }
    } catch (err) {
      console.error('Failed to save generation settings:', err)
      toast({
        title: 'Error',
        description: 'Failed to save generation settings',
        variant: 'destructive'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const exportSettings = async () => {
    try {
      const settings = { userSettings, generationSettings }
      const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'settings-backup.json'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      toast({
        title: 'Success',
        description: 'Settings exported successfully'
      })
    } catch (err) {
      console.error('Failed to export settings:', err)
      toast({
        title: 'Error',
        description: 'Failed to export settings',
        variant: 'destructive'
      })
    }
  }

  const importSettings = async (event: React.ChangeEvent<HTMLInputElement>) => {
    try {
      const file = event.target.files?.[0]
      if (!file) return

      const text = await file.text()
      const imported = JSON.parse(text)
      
      if (imported.userSettings) setUserSettings(imported.userSettings)
      if (imported.generationSettings) setGenerationSettings(imported.generationSettings)
      
      toast({
        title: 'Success',
        description: 'Settings imported successfully'
      })
    } catch (err) {
      console.error('Failed to import settings:', err)
      toast({
        title: 'Error',
        description: 'Failed to import settings. Please check the file format.',
        variant: 'destructive'
      })
    }
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="flex items-center gap-3 mb-8">
        <Settings className="h-8 w-8" />
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent">Settings</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage your account and application preferences
          </p>
        </div>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="profile" className="flex items-center gap-2">
            <User className="h-4 w-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="appearance" className="flex items-center gap-2">
            <Palette className="h-4 w-4" />
            Appearance
          </TabsTrigger>
          <TabsTrigger value="generation" className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            Generation
          </TabsTrigger>
          <TabsTrigger value="account" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Account
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent">
                <User className="h-5 w-5 text-blue-600" />
                Profile Settings
              </CardTitle>
              <CardDescription>
                Update your personal information and preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input
                    id="name"
                    value={userSettings.name}
                    onChange={(e) => setUserSettings(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Enter your full name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={userSettings.email}
                    onChange={(e) => setUserSettings(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="Enter your email"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="bio">Bio</Label>
                <Textarea
                  id="bio"
                  value={userSettings.bio}
                  onChange={(e) => setUserSettings(prev => ({ ...prev, bio: e.target.value }))}
                  placeholder="Tell us about yourself"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="language">Language</Label>
                  <Select
                    value={userSettings.language}
                    onValueChange={(value) => setUserSettings(prev => ({ ...prev, language: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="es">Spanish</SelectItem>
                      <SelectItem value="fr">French</SelectItem>
                      <SelectItem value="de">German</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="timezone">Timezone</Label>
                  <Select
                    value={userSettings.timezone}
                    onValueChange={(value) => setUserSettings(prev => ({ ...prev, timezone: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="UTC">UTC</SelectItem>
                      <SelectItem value="America/New_York">Eastern Time</SelectItem>
                      <SelectItem value="America/Chicago">Central Time</SelectItem>
                      <SelectItem value="America/Denver">Mountain Time</SelectItem>
                      <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Button onClick={saveUserSettings} disabled={isLoading} className="flex items-center gap-2">
                <Save className="h-4 w-4" />
                Save Profile
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent">
                <Bell className="h-5 w-5 text-blue-600" />
                Notification Preferences
              </CardTitle>
              <CardDescription>
                Configure how you want to receive notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Email Notifications</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Receive notifications via email
                  </p>
                </div>
                <Switch
                  checked={userSettings.notifications.email}
                  onCheckedChange={(checked) => 
                    setUserSettings(prev => ({
                      ...prev,
                      notifications: { ...prev.notifications, email: checked }
                    }))
                  }
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Push Notifications</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Receive push notifications in your browser
                  </p>
                </div>
                <Switch
                  checked={userSettings.notifications.push}
                  onCheckedChange={(checked) => 
                    setUserSettings(prev => ({
                      ...prev,
                      notifications: { ...prev.notifications, push: checked }
                    }))
                  }
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Marketing Communications</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Receive updates about new features and promotions
                  </p>
                </div>
                <Switch
                  checked={userSettings.notifications.marketing}
                  onCheckedChange={(checked) => 
                    setUserSettings(prev => ({
                      ...prev,
                      notifications: { ...prev.notifications, marketing: checked }
                    }))
                  }
                />
              </div>

              <Button onClick={saveUserSettings} disabled={isLoading} className="flex items-center gap-2">
                <Save className="h-4 w-4" />
                Save Notifications
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="appearance">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent">
                <Palette className="h-5 w-5 text-blue-600" />
                Appearance Settings
              </CardTitle>
              <CardDescription>
                Customize the look and feel of the application
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="theme">Theme</Label>
                <Select
                  value={userSettings.theme}
                  onValueChange={(value: 'light' | 'dark' | 'system') => 
                    setUserSettings(prev => ({ ...prev, theme: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="light">Light</SelectItem>
                    <SelectItem value="dark">Dark</SelectItem>
                    <SelectItem value="system">System</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button onClick={saveUserSettings} disabled={isLoading} className="flex items-center gap-2">
                <Save className="h-4 w-4" />
                Save Appearance
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="generation">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent">
                <Database className="h-5 w-5 text-blue-600" />
                Content Generation Settings
              </CardTitle>
              <CardDescription>
                Configure default settings for content generation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="contentQuality">Content Generation Quality</Label>
                <Select
                  value={generationSettings.contentQuality}
                  onValueChange={(value: 'fast' | 'balanced' | 'premium') => 
                    setGenerationSettings(prev => ({ ...prev, contentQuality: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="fast">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">Fast</span>
                        <span className="text-xs text-muted-foreground">Quick generation, good for drafts</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="balanced">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">Balanced</span>
                        <span className="text-xs text-muted-foreground">Optimal speed and quality balance</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="premium">
                      <div className="flex flex-col items-start">
                        <span className="font-medium">Premium</span>
                        <span className="text-xs text-muted-foreground">Highest quality, slower generation</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  Our AI automatically selects the best models based on your content type and quality preference
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="maxTokens">Max Output Length</Label>
                  <Select
                    value={generationSettings.maxTokens.toString()}
                    onValueChange={(value) => 
                      setGenerationSettings(prev => ({ 
                        ...prev, 
                        maxTokens: parseInt(value) 
                      }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1000">Short (1K tokens)</SelectItem>
                      <SelectItem value="2000">Medium (2K tokens)</SelectItem>
                      <SelectItem value="4000">Long (4K tokens)</SelectItem>
                      <SelectItem value="8000">Very Long (8K tokens)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="backupFrequency">Backup Frequency</Label>
                  <Select
                    value={generationSettings.backupFrequency}
                    onValueChange={(value) => 
                      setGenerationSettings(prev => ({ ...prev, backupFrequency: value }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="never">Never</SelectItem>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="monthly">Monthly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="temperature">Temperature: {generationSettings.temperature}</Label>
                <input
                  id="temperature"
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={generationSettings.temperature}
                  onChange={(e) => 
                    setGenerationSettings(prev => ({ 
                      ...prev, 
                      temperature: parseFloat(e.target.value) 
                    }))
                  }
                  className="w-full"
                />
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Higher values make output more random, lower values more focused
                </p>
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Auto-save Generated Content</Label>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Automatically save content as it&#39;s generated
                  </p>
                </div>
                <Switch
                  checked={generationSettings.autoSave}
                  onCheckedChange={(checked) => 
                    setGenerationSettings(prev => ({ ...prev, autoSave: checked }))
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="backupFrequency">Backup Frequency</Label>
                <Select
                  value={generationSettings.backupFrequency}
                  onValueChange={(value) => 
                    setGenerationSettings(prev => ({ ...prev, backupFrequency: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="never">Never</SelectItem>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                    <SelectItem value="monthly">Monthly</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button onClick={saveGenerationSettings} disabled={isLoading} className="flex items-center gap-2">
                <Save className="h-4 w-4" />
                Save Generation Settings
              </Button>
            </CardContent>
          </Card>

          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent">
                <Shield className="h-5 w-5 text-blue-600" />
                Backup & Restore
              </CardTitle>
              <CardDescription>
                Export or import your settings for backup purposes
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-4">
                <Button onClick={exportSettings} variant="outline" className="flex items-center gap-2">
                  <Download className="h-4 w-4" />
                  Export Settings
                </Button>
                
                <div className="relative">
                  <input
                    type="file"
                    accept=".json"
                    onChange={importSettings}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  <Button variant="outline" className="flex items-center gap-2">
                    <Upload className="h-4 w-4" />
                    Import Settings
                  </Button>
                </div>
              </div>
              
              <div className="flex items-start gap-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-400 mt-0.5" />
                <p className="text-sm text-yellow-800 dark:text-yellow-300">
                  Importing settings will overwrite your current configuration. Make sure to export your current settings first if you want to keep them.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="account">
          <div className="space-y-6">
            {/* Account Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent">
                  <Shield className="h-5 w-5 text-blue-600" />
                  Account Information
                </CardTitle>
                <CardDescription>
                  View and manage your account details
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Account ID</Label>
                    <Input value="user_12345" disabled className="bg-muted" />
                  </div>
                  <div className="space-y-2">
                    <Label>Member Since</Label>
                    <Input value="January 2025" disabled className="bg-muted" />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label>Account Type</Label>
                  <Input value="Premium" disabled className="bg-muted" />
                </div>
              </CardContent>
            </Card>

            {/* Data Export */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent">
                  <Download className="h-5 w-5 text-blue-600" />
                  Data Export
                </CardTitle>
                <CardDescription>
                  Download all your data before deletion
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  Export all your content, settings, and account data. This includes generated content, templates, and preferences.
                </p>
                <Button variant="outline" className="flex items-center gap-2">
                  <Download className="h-4 w-4" />
                  Download My Data
                </Button>
              </CardContent>
            </Card>

            {/* Danger Zone - Account Deletion */}
            <Card className="border-red-200 dark:border-red-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-red-600 dark:text-red-400">
                  <AlertCircle className="h-5 w-5" />
                  Danger Zone
                </CardTitle>
                <CardDescription className="text-red-600 dark:text-red-400">
                  Permanently delete your account and all associated data
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <h4 className="font-semibold text-red-800 dark:text-red-300 mb-2">
                    Account Deletion
                  </h4>
                  <p className="text-sm text-red-700 dark:text-red-400 mb-4">
                    This action cannot be undone. This will permanently delete your account, all your content, 
                    generated articles, templates, and remove all associated data from our servers.
                  </p>
                  <ul className="text-sm text-red-700 dark:text-red-400 space-y-1 mb-4">
                    <li>• All generated content will be permanently deleted</li>
                    <li>• All templates and style profiles will be removed</li>
                    <li>• Account settings and preferences will be lost</li>
                    <li>• This action cannot be reversed</li>
                  </ul>
                </div>

                <div className="space-y-3">
                  <div className="space-y-2">
                    <Label htmlFor="delete-confirmation" className="text-red-600 dark:text-red-400">
                      Type <strong>DELETE</strong> to confirm account deletion
                    </Label>
                    <Input
                      id="delete-confirmation"
                      placeholder="Type DELETE here"
                      className="border-red-300 focus:border-red-500 focus:ring-red-500"
                    />
                  </div>
                  
                  <Button 
                    variant="destructive" 
                    className="w-full bg-red-600 hover:bg-red-700"
                    disabled={true} // Enable based on confirmation input
                  >
                    <AlertCircle className="h-4 w-4 mr-2" />
                    Delete My Account Permanently
                  </Button>
                </div>

                <div className="flex items-start gap-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-400 mt-0.5" />
                  <div className="text-sm text-yellow-800 dark:text-yellow-300">
                    <p className="font-medium mb-1">Before you delete your account:</p>
                    <ul className="space-y-1">
                      <li>• Make sure you&apos;ve exported any data you want to keep</li>
                      <li>• Cancel any active subscriptions</li>
                      <li>• Consider downgrading to a free account instead</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}