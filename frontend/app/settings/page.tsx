// File: frontend/app/settings/page.tsx
'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useSettings } from '@/lib/settings-context'
import { showToast } from '@/lib/toast-utils'
import { useTheme } from 'next-themes'
import { 
  User, 
  Bell, 
  Palette, 
  Database, 
  Shield, 
  Download, 
  Upload,
  Save,
  AlertCircle,
  Sparkles,
  Sun,
  Moon,
  Monitor,
  Zap,
  Scale,
  Gem,
  FileText,
  BookOpen,
  Clipboard,
  Calendar,
  CalendarDays,
  CalendarX,
  X,
  ArrowRight
} from 'lucide-react'
import { useState } from 'react'


export default function SettingsPage() {
  const { theme, setTheme } = useTheme() // Use next-themes instead of custom theme management
  const [isLoading, setIsLoading] = useState(false)
  const [deleteConfirmation, setDeleteConfirmation] = useState('')
  
const {
  userSettings,
  generationSettings,
  updateUserSettings,
  updateGenerationSettings
} = useSettings()
  
// Use next-themes instead of custom theme handling
const handleThemeChange = (newTheme: string) => {
  setTheme(newTheme)

  // Toast without duration since it's not supported
  showToast.success(
    'Theme Updated',
    `Switched to ${newTheme === 'writerzroom' ? 'WriterzRoom' : newTheme} theme`
  )
}

const saveUserSettings = async () => {
  try {
    setIsLoading(true)
    
    // Save to localStorage
    localStorage.setItem('writerzroom_user_settings', JSON.stringify(userSettings))
    
    // Dispatch event for other components
    window.dispatchEvent(new CustomEvent('settings-updated', { 
      detail: { userSettings } 
    }))
    
    showToast.success('Success', 'User settings saved successfully')
  } catch (err) {
    console.error('Failed to save user settings:', err)
    showToast.error('Error', 'Failed to save user settings')
  } finally {
    setIsLoading(false)
  }
}

  const saveGenerationSettings = async () => {
    try {
      setIsLoading(true)
      
      // Save to localStorage
      localStorage.setItem('writerzroom_generation_settings', JSON.stringify(generationSettings))
      
      // Dispatch event for Generate page
      window.dispatchEvent(new CustomEvent('settings-updated', { 
        detail: { generationSettings } 
      }))
      
      showToast.success('Success', 'Generation settings saved successfully')
      
    } catch (err) {
      console.error('Failed to save generation settings:', err)
      showToast.error('Error', 'Failed to save generation settings')
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
      a.download = 'writerzroom-settings.json'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      showToast.success('Success', 'User settings saved successfully')
    } catch (err) {
      console.error('Failed to export settings:', err)
      showToast.error('Error', 'Failed to load settings')
    }
  }

  const importSettings = async (event: React.ChangeEvent<HTMLInputElement>) => {
    try {
      const file = event.target.files?.[0]
      if (!file) return

      const text = await file.text()
      const imported = JSON.parse(text)
      
      if (imported.userSettings) updateUserSettings(imported.userSettings)
      if (imported.generationSettings) updateGenerationSettings(imported.generationSettings)
      
      showToast.success('Success', 'User settings saved successfully')
    } catch (err) {
      console.error('Failed to import settings:', err)
      showToast.error('Error', 'Failed to load settings')
    }
  }

    const exportUserData = async () => {
    try {
      setIsLoading(true)

      // Fetch generated content from API
      const contentResponse = await fetch('/api/content/list')
      let generatedContent: unknown[] = []

      if (contentResponse.ok) {
        const contentData = await contentResponse.json()
        generatedContent = contentData.content || []
      } else {
        console.warn('⚠️ Could not fetch generated content for export')
      }

      const userData = {
        profile: userSettings,
        settings: generationSettings,
        content: generatedContent,
        exportDate: new Date().toISOString(),
        version: '2.0.0'
      }

      const blob = new Blob([JSON.stringify(userData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `writerzroom-data-export-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      showToast.success('Success', `Exported ${generatedContent.length} content items`)
    } catch (err) {
      console.error('Failed to export user data:', err)
      showToast.error('Error', 'Failed to export user data')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl sm:text-5xl font-bold mb-4 text-foreground">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
                Settings
              </span>
            </h1>
            <p className="text-xl text-muted-foreground">
              Manage your WriterzRoom preferences and account settings
            </p>
          </div>

          <Tabs defaultValue="profile" className="space-y-8">
            <TabsList className="grid w-full grid-cols-5 bg-muted">
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
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5 text-primary" />
                    Profile Settings
                  </CardTitle>
                  <CardDescription>
                    Update your personal information and preferences
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Full Name</Label>
                      <Input
                        id="name"
                        value={userSettings.name}
                        onChange={(e) => updateUserSettings({ name: e.target.value })}
                        placeholder="Enter your full name"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">Email Address</Label>
                      <Input
                        id="email"
                        type="email"
                        value={userSettings.email}
                        onChange={(e) => updateUserSettings({ email: e.target.value })}
                        placeholder="Enter your email"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="bio">Bio</Label>
                    <Textarea
                      id="bio"
                      value={userSettings.bio}
                      onChange={(e) => updateUserSettings({ bio: e.target.value })}
                      placeholder="Tell us about yourself"
                      rows={3}
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="language">Language</Label>
                      <Select
                        value={userSettings.language}
                        onValueChange={(value) => updateUserSettings({ language: value })}
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
                        onValueChange={(value) => updateUserSettings({ timezone: value })}
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

                  <Button 
                    onClick={saveUserSettings} 
                    disabled={isLoading} 
                    className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Save Profile
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="notifications">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bell className="h-5 w-5 text-primary" />
                    Notification Preferences
                  </CardTitle>
                  <CardDescription>
                    Configure how you want to receive notifications
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-0.5">
                      <Label>Email Notifications</Label>
                      <p className="text-sm text-muted-foreground">
                        Receive notifications via email about content generation and account updates
                      </p>
                    </div>
                    <Switch
                      checked={userSettings.notifications.email}
                      onCheckedChange={(checked) => 
                        updateUserSettings({
                          notifications: { ...userSettings.notifications, email: checked }
                        })
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-0.5">
                      <Label>Push Notifications</Label>
                      <p className="text-sm text-muted-foreground">
                        Receive push notifications in your browser when content generation is complete
                      </p>
                    </div>
                    <Switch
                      checked={userSettings.notifications.push}
                      onCheckedChange={(checked) => 
                        updateUserSettings({
                          notifications: { ...userSettings.notifications, push: checked }
                        })
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-0.5">
                      <Label>Marketing Communications</Label>
                      <p className="text-sm text-muted-foreground">
                        Receive updates about new features, tips, and WriterzRoom promotions
                      </p>
                    </div>
                    <Switch
                      checked={userSettings.notifications.marketing}
                      onCheckedChange={(checked) => 
                        updateUserSettings({
                          notifications: { ...userSettings.notifications, marketing: checked }
                        })
                      }
                    />
                  </div>

                  <Button 
                    onClick={saveUserSettings} 
                    disabled={isLoading} 
                    className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Save Notifications
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="appearance">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Palette className="h-5 w-5 text-primary" />
                    Appearance Settings
                  </CardTitle>
                  <CardDescription>
                    Customize the look and feel of WriterzRoom
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="theme">Theme Preference</Label>
                    <Select
                      value={theme || 'writerzroom'}
                      onValueChange={handleThemeChange}
                      key={theme} // This forces re-render when theme changes
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select a theme" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="writerzroom">
                          <div className="flex items-center gap-2">
                            <Sparkles className="h-4 w-4" />
                            WriterzRoom
                          </div>
                        </SelectItem>
                        <SelectItem value="light">
                          <div className="flex items-center gap-2">
                            <Sun className="h-4 w-4" />
                            Light Theme
                          </div>
                        </SelectItem>
                        <SelectItem value="dark">
                          <div className="flex items-center gap-2">
                            <Moon className="h-4 w-4" />
                            Dark Theme
                          </div>
                        </SelectItem>
                        <SelectItem value="system">
                          <div className="flex items-center gap-2">
                            <Monitor className="h-4 w-4" />
                            System Default
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-muted-foreground">
                      Current: {theme === 'writerzroom' ? 'WriterzRoom' : theme} theme
                    </p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="generation">
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Database className="h-5 w-5 text-primary" />
                      Content Generation Settings
                    </CardTitle>
                    <CardDescription>
                      Configure default settings for WriterzRoom content generation
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-2">
                      <Label htmlFor="contentQuality">Content Generation Quality</Label>
                      <Select
                        value={generationSettings.contentQuality}
                        onValueChange={(value: 'fast' | 'balanced' | 'premium') => 
                          updateGenerationSettings({ contentQuality: value })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="fast">
                            <div className="flex items-center gap-2">
                              <Zap className="h-4 w-4" />
                              Fast - Quick generation, good for drafts
                            </div>
                          </SelectItem>
                          <SelectItem value="balanced">
                            <div className="flex items-center gap-2">
                              <Scale className="h-4 w-4" />
                              Balanced - Optimal speed and quality
                            </div>
                          </SelectItem>
                          <SelectItem value="premium">
                            <div className="flex items-center gap-2">
                              <Gem className="h-4 w-4" />
                              Premium - Highest quality, slower generation
                            </div>
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="maxTokens">Max Output Length</Label>
                        <Select
                          value={generationSettings.maxTokens.toString()}
                          onValueChange={(value) => 
                            updateGenerationSettings({ maxTokens: parseInt(value) })
                          }
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="1000">
                              <div className="flex items-center gap-2">
                                <FileText className="h-4 w-4" />
                                Short (1K tokens)
                              </div>
                            </SelectItem>
                            <SelectItem value="2000">
                              <div className="flex items-center gap-2">
                                <BookOpen className="h-4 w-4" />
                                Medium (2K tokens)
                              </div>
                            </SelectItem>
                            <SelectItem value="4000">
                              <div className="flex items-center gap-2">
                                <Clipboard className="h-4 w-4" />
                                Long (4K tokens)
                              </div>
                            </SelectItem>
                            <SelectItem value="8000">
                              <div className="flex items-center gap-2">
                                <Database className="h-4 w-4" />
                                Very Long (8K tokens)
                              </div>
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="backupFrequency">Auto-backup Frequency</Label>
                        <Select
                          value={generationSettings.backupFrequency}
                          onValueChange={(value) => 
                            updateGenerationSettings({ backupFrequency: value })
                          }
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="never">
                              <div className="flex items-center gap-2">
                                <X className="h-4 w-4" />
                                Never
                              </div>
                            </SelectItem>
                            <SelectItem value="daily">
                              <div className="flex items-center gap-2">
                                <Calendar className="h-4 w-4" />
                                Daily
                              </div>
                            </SelectItem>
                            <SelectItem value="weekly">
                              <div className="flex items-center gap-2">
                                <CalendarDays className="h-4 w-4" />
                                Weekly
                              </div>
                            </SelectItem>
                            <SelectItem value="monthly">
                              <div className="flex items-center gap-2">
                                <CalendarX className="h-4 w-4" />
                                Monthly
                              </div>
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="temperature">
                        Creativity Level: {generationSettings.temperature}
                      </Label>
                      <input
                        id="temperature"
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={generationSettings.temperature}
                        onChange={(e) => 
                          updateGenerationSettings({ temperature: parseFloat(e.target.value) })
                        }
                        className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer"
                      />
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>More Focused</span>
                        <span>More Creative</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="space-y-0.5">
                        <Label>Auto-save Generated Content</Label>
                        <p className="text-sm text-muted-foreground">
                          Automatically save content as it&apos;s generated to prevent data loss
                        </p>
                      </div>
                      <Switch
                        checked={generationSettings.autoSave}
                        onCheckedChange={(checked) => 
                          updateGenerationSettings({ autoSave: checked })
                        }
                      />
                    </div>

                    <Button 
                      onClick={saveGenerationSettings} 
                      disabled={isLoading} 
                      className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white"
                    >
                      <Save className="h-4 w-4 mr-2" />
                      Save Generation Settings
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

          {/* Backup & Export Tab Content */}
          <TabsContent value="backup">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-primary" />
                  Backup & Export
                </CardTitle>
                <CardDescription>
                  Export or import your WriterzRoom settings for backup purposes
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-4">
                  <Button 
                    onClick={exportSettings} 
                    variant="outline" 
                    className="flex items-center gap-2"
                  >
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
                    <Button 
                      variant="outline" 
                      className="flex items-center gap-2"
                    >
                      <Upload className="h-4 w-4" />
                      Import Settings
                    </Button>
                  </div>
                </div>
                
                <div className="flex items-start gap-2 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                  <AlertCircle className="h-4 w-4 text-yellow-600 mt-0.5" />
                  <p className="text-sm text-yellow-800 dark:text-yellow-200">
                    Importing settings will overwrite your current configuration. Export your current settings first if you want to keep them.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

        {/* Account Tab Content */}
        <TabsContent value="account">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-primary" />
                  Account Information
                </CardTitle>
                <CardDescription>
                  View and manage your WriterzRoom account details
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Account ID</Label>
                    <Input value="user_agp_12345" disabled />
                  </div>
                  <div className="space-y-2">
                    <Label>Member Since</Label>
                    <Input value="January 15, 2025" disabled />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Account Type</Label>
                  <Input value="WriterzRoom Premium" disabled />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Download className="h-5 w-5 text-primary" />
                  Data Export
                </CardTitle>
                <CardDescription>
                  Download all your WriterzRoom data for backup or migration
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  Export all your content, settings, templates, and account data. This includes generated content, 
                  custom templates, style profiles, and user preferences.
                </p>
                <Button 
                  onClick={exportUserData}
                  variant="outline" 
                  className="flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  Download My Data
                </Button>
              </CardContent>
            </Card>

            <Card className="border-destructive/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-destructive">
                  <AlertCircle className="h-5 w-5" />
                  Danger Zone
                </CardTitle>
                <CardDescription>
                  Permanently delete your WriterzRoom account and all associated data
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                  <h4 className="font-semibold text-destructive mb-2">
                    Account Deletion
                  </h4>
                  <p className="text-sm text-muted-foreground mb-4">
                    This action cannot be undone. This will permanently delete your WriterzRoom account, 
                    all your generated content, templates, and remove all associated data from our servers.
                  </p>
                  <ul className="text-sm text-muted-foreground space-y-1 mb-4">
                    <li className="flex items-center gap-2">
                      <ArrowRight className="h-3 w-3" />
                      All generated content will be permanently deleted
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="h-3 w-3" />
                      All custom templates and style profiles will be removed
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="h-3 w-3" />
                      Account settings and preferences will be lost
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="h-3 w-3" />
                      Subscription and billing history will be deleted
                    </li>
                    <li className="flex items-center gap-2">
                      <ArrowRight className="h-3 w-3" />
                      This action cannot be reversed
                    </li>
                  </ul>
                </div>

                <div className="space-y-3">
                  <div className="space-y-2">
                    <Label htmlFor="delete-confirmation">
                      Type <strong>DELETE</strong> to confirm account deletion
                    </Label>
                    <Input
                      id="delete-confirmation"
                      value={deleteConfirmation}
                      onChange={(e) => setDeleteConfirmation(e.target.value)}
                      placeholder="Type DELETE here"
                      className="border-destructive/50 focus:border-destructive"
                    />
                  </div>
                  
                  <Button 
                    variant="destructive" 
                    className="w-full"
                    disabled={deleteConfirmation !== 'DELETE'}
                    onClick={() => {
                      showToast.error(
                        'Account Deletion',
                        'This feature is not implemented in demo mode'
                      )
                    }}
                  >
                    <AlertCircle className="h-4 w-4 mr-2" />
                    Delete My Account Permanently
                  </Button>
                </div>

                <div className="flex items-start gap-2 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                  <AlertCircle className="h-4 w-4 text-yellow-600 mt-0.5" />
                  <div className="text-sm text-yellow-800 dark:text-yellow-200">
                    <p className="font-medium mb-1">Before you delete your account:</p>
                    <ul className="space-y-1">
                      <li className="flex items-center gap-2">
                        <ArrowRight className="h-3 w-3" />
                        Make sure you&apos;ve exported any data you want to keep
                      </li>
                      <li className="flex items-center gap-2">
                        <ArrowRight className="h-3 w-3" />
                        Cancel any active subscriptions in your billing settings
                      </li>
                      <li className="flex items-center gap-2">
                        <ArrowRight className="h-3 w-3" />
                        Consider downgrading to a free account instead
                      </li>
                      <li className="flex items-center gap-2">
                        <ArrowRight className="h-3 w-3" />
                        Contact support if you need help with anything
                      </li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        </Tabs>
      </div>
      </div>
    </div>
  )
}