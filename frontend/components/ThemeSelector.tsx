/* File: frontend/components/ThemeSelector.tsx */
"use client"

import { useTheme } from 'next-themes'
import { useState, useEffect } from 'react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { toast } from 'sonner'
import { Sun, Moon, Monitor, Palette } from 'lucide-react'

type CustomTheme = 'default' | 'agentwrite-pro'

export function ThemeSelector() {
  const { theme, setTheme, systemTheme } = useTheme()
  const [customTheme, setCustomTheme] = useState<CustomTheme>('default')
  const [mounted, setMounted] = useState(false)

  // Ensure component is mounted to avoid hydration issues
  useEffect(() => {
    setMounted(true)
    // Load custom theme from localStorage
    const saved = localStorage.getItem('custom-theme') as CustomTheme
    if (saved && (saved === 'default' || saved === 'agentwrite-pro')) {
      setCustomTheme(saved)
      applyCustomTheme(saved)
    }
  }, [])

  const applyCustomTheme = (newCustomTheme: CustomTheme) => {
    // Remove existing custom theme classes
    document.body.classList.remove('agentwrite-pro')
    document.documentElement.classList.remove('agentwrite-pro')
    
    // Apply new custom theme
    if (newCustomTheme === 'agentwrite-pro') {
      document.body.classList.add('agentwrite-pro')
      document.documentElement.classList.add('agentwrite-pro')
    }
  }

  const handleBaseThemeChange = (newTheme: string) => {
    setTheme(newTheme)
    toast.success(`Switched to ${newTheme} theme`)
  }

  const handleCustomThemeChange = (newCustomTheme: string) => {
    const customThemeValue = newCustomTheme as CustomTheme
    setCustomTheme(customThemeValue)
    localStorage.setItem('custom-theme', customThemeValue)
    applyCustomTheme(customThemeValue)
    
    const themeName = customThemeValue === 'agentwrite-pro' ? 'AgentWrite Pro' : 'Default'
    toast.success(`Switched to ${themeName} theme`)
  }

  const quickSwitchToDefault = () => {
    setTheme('light')
    handleCustomThemeChange('default')
    toast.success('Switched to Default Light theme')
  }

  const quickSwitchToAgentWritePro = () => {
    setTheme('dark')
    handleCustomThemeChange('agentwrite-pro')
    toast.success('Switched to AgentWrite Pro theme')
  }

  if (!mounted) {
    return <div>Loading...</div>
  }

  const currentTheme = theme === 'system' ? systemTheme : theme

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Palette className="h-5 w-5" />
          Appearance Settings
        </CardTitle>
        <CardDescription>
          Customize the look and feel of AgentWrite Pro
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Base Theme Selection */}
        <div className="space-y-3">
          <label className="text-sm font-medium">Base Theme</label>
          <Select value={theme || 'system'} onValueChange={handleBaseThemeChange}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select base theme" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="light">
                <div className="flex items-center gap-2">
                  <Sun className="h-4 w-4" />
                  Light
                </div>
              </SelectItem>
              <SelectItem value="dark">
                <div className="flex items-center gap-2">
                  <Moon className="h-4 w-4" />
                  Dark
                </div>
              </SelectItem>
              <SelectItem value="system">
                <div className="flex items-center gap-2">
                  <Monitor className="h-4 w-4" />
                  System
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Custom Theme Selection */}
        <div className="space-y-3">
          <label className="text-sm font-medium">Custom Theme</label>
          <Select value={customTheme} onValueChange={handleCustomThemeChange}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select custom theme" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="default">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-gray-300"></div>
                  Default
                </div>
              </SelectItem>
              <SelectItem value="agentwrite-pro">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-gradient-to-r from-purple-500 to-blue-600"></div>
                  AgentWrite Pro
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Quick Switch Buttons */}
        <div className="space-y-3">
          <label className="text-sm font-medium">Quick Switch</label>
          <div className="flex gap-3">
            <Button 
              variant="outline" 
              onClick={quickSwitchToDefault}
              className="flex-1"
            >
              <Sun className="h-4 w-4 mr-2" />
              Default Light
            </Button>
            <Button 
              variant="outline" 
              onClick={quickSwitchToAgentWritePro}
              className="flex-1"
            >
              <Palette className="h-4 w-4 mr-2" />
              AgentWrite Pro
            </Button>
          </div>
        </div>

        {/* Current Theme Display */}
        <div className="pt-4 border-t">
          <div className="text-xs text-muted-foreground space-y-1">
            <div>Current base theme: <span className="font-medium">{currentTheme}</span></div>
            <div>Current custom theme: <span className="font-medium">{customTheme}</span></div>
          </div>
        </div>

        {/* Theme Preview */}
        <div className="space-y-3">
          <label className="text-sm font-medium">Preview</label>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-4 rounded-lg border bg-card text-card-foreground">
              <div className="text-sm font-medium mb-2">Sample Card</div>
              <div className="text-xs text-muted-foreground">
                This is how content looks with your current theme.
              </div>
            </div>
            <div className="p-4 rounded-lg border bg-secondary text-secondary-foreground">
              <div className="text-sm font-medium mb-2">Secondary</div>
              <div className="text-xs text-muted-foreground">
                Secondary background example.
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}