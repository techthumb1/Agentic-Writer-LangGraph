// hooks/useUnifiedTheme.ts
"use client"

import { useTheme } from 'next-themes'
import { useState, useEffect, useCallback } from 'react'

// Define the CustomTheme type
type CustomTheme = 'default' | 'agentwrite-pro';
// Optionally, define BaseTheme if not already defined elsewhere
type BaseTheme = 'light' | 'dark' | 'system';

export function useUnifiedTheme() {
  const { theme, setTheme, systemTheme } = useTheme()
  const [customTheme, setCustomTheme] = useState<CustomTheme>('agentwrite-pro') // Your current default
  
  // Function to apply all theme classes
  const applyThemeClasses = useCallback((baseTheme: string, customTheme: CustomTheme) => {
    // Clear all existing theme classes
    document.documentElement.classList.remove('dark', 'light')
    document.body.classList.remove('dark', 'light', 'agentwrite-pro')
    document.documentElement.removeAttribute('data-theme')
    
    // Apply base theme (light/dark)
    const resolvedTheme = baseTheme === 'system' 
      ? (systemTheme || 'light') 
      : baseTheme
    
    document.documentElement.classList.add(resolvedTheme)
    document.body.classList.add(resolvedTheme)
    
    // Apply custom theme
    if (customTheme === 'agentwrite-pro') {
      document.documentElement.setAttribute('data-theme', 'agentwrite-pro')
      document.body.classList.add('agentwrite-pro')
    }
    
    console.log('Applied theme:', { baseTheme, customTheme, resolvedTheme })
  }, [systemTheme])
  
  // Apply themes whenever they change
  useEffect(() => {
    if (theme) {
      applyThemeClasses(theme, customTheme)
    }
  }, [theme, systemTheme, customTheme, applyThemeClasses])
  
  const setBaseTheme = (newTheme: BaseTheme) => {
    setTheme(newTheme)
  }
  
  const setCustomThemeOnly = (newCustomTheme: CustomTheme) => {
    setCustomTheme(newCustomTheme)
    localStorage.setItem('custom-theme', newCustomTheme)
  }
  
  const setBothThemes = (baseTheme: BaseTheme, customTheme: CustomTheme) => {
    setCustomTheme(customTheme)
    setTheme(baseTheme)
    localStorage.setItem('custom-theme', customTheme)
  }
  
  // Load custom theme from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('custom-theme') as CustomTheme
    if (saved && (saved === 'default' || saved === 'agentwrite-pro')) {
      setCustomTheme(saved)
    }
  }, [])
  
  return {
    baseTheme: theme as BaseTheme,
    customTheme,
    setBaseTheme,
    setCustomTheme: setCustomThemeOnly,
    setBothThemes,
    resolvedTheme: theme === 'system' ? systemTheme : theme
  }
}