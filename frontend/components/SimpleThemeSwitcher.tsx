/* File: frontend/components/SimpleThemeSwitcher.tsx */
"use client"

import { useTheme } from 'next-themes'
import { useState, useEffect } from 'react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { showToast } from '@/lib/toast-utils'

export function SimpleThemeSwitcher() {
  const { theme, setTheme } = useTheme()
  const [customTheme, setCustomTheme] = useState<string>('default')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    // Load custom theme from localStorage
    const saved = localStorage.getItem('custom-theme') || 'default'
    setCustomTheme(saved)
    applyCustomTheme(saved)
  }, [])

  const applyCustomTheme = (newCustomTheme: string) => {
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
    showToast.success(`Theme Updated`, `Switched to ${newTheme} theme`)
  }

  const handleCustomThemeChange = (newCustomTheme: string) => {
    setCustomTheme(newCustomTheme)
    localStorage.setItem('custom-theme', newCustomTheme)
    applyCustomTheme(newCustomTheme)
    
    const themeName = newCustomTheme === 'agentwrite-pro' ? 'AgentWrite Pro' : 'Default'
    showToast.success(`Theme Updated`, `Switched to ${themeName} theme`)
  }

  const resetThemes = () => {
    setTheme('light')
    setCustomTheme('default')
    localStorage.setItem('custom-theme', 'default')
    applyCustomTheme('default')
    showToast.info('Themes Reset', 'All themes have been reset to default')
  }

  const testToast = () => {
    showToast.success('Test Toast', 'This is a test toast with a close button')
    
    // Test different toast types
    setTimeout(() => showToast.error('Error Toast', 'This is an error message'), 1000)
    setTimeout(() => showToast.warning('Warning Toast', 'This is a warning message'), 2000)
    setTimeout(() => showToast.info('Info Toast', 'This is an info message'), 3000)
  }

  if (!mounted) {
    return <div>Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <label className="text-sm font-medium mb-2 block">Base Theme</label>
        <Select value={theme || 'system'} onValueChange={handleBaseThemeChange}>
          <SelectTrigger>
            <SelectValue placeholder="Select base theme" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="light">Light</SelectItem>
            <SelectItem value="dark">Dark</SelectItem>
            <SelectItem value="system">System</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <div>
        <label className="text-sm font-medium mb-2 block">Custom Theme</label>
        <Select value={customTheme} onValueChange={handleCustomThemeChange}>
          <SelectTrigger>
            <SelectValue placeholder="Select custom theme" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="default">Default</SelectItem>
            <SelectItem value="agentwrite-pro">AgentWrite Pro</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="flex gap-2">
        <button
          onClick={resetThemes}
          className="px-3 py-1 text-xs bg-secondary text-secondary-foreground rounded hover:bg-secondary/80"
        >
          Reset Themes
        </button>
        <button
          onClick={testToast}
          className="px-3 py-1 text-xs bg-primary text-primary-foreground rounded hover:bg-primary/80"
        >
          Test Toasts
        </button>
      </div>
      
      <div className="text-xs text-muted-foreground">
        Current: {theme} + {customTheme}
      </div>
    </div>
  )
}