// File: frontend/lib/settings-context.tsx
'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'

// Types
export interface UserSettings {
  name: string
  email: string
  bio: string
  company: string
  role: string
  notifications: {
    email: boolean
    push: boolean
    marketing: boolean
  }
  language: string
  timezone: string
  joinDate: string
}

export interface GenerationSettings {
  maxTokens: number
  temperature: number
  autoSave: boolean
  backupFrequency: string
  contentQuality: 'fast' | 'balanced' | 'premium'
  enableMultiModel: boolean
}

export interface UserStats {
  contentGenerated: number
  totalTimeSaved: number
  averageRating: number
  daysActive: number
}

export interface ContentItem {
  title: string
  type: string
  createdAt: string
  words: number
  rating: number
  metadata?: {  // Add optional metadata
    wordCount?: number
    words?: number
    rating?: number
  }
}

interface SettingsContextType {
  userSettings: UserSettings
  generationSettings: GenerationSettings
  userStats: UserStats
  recentContent: ContentItem[]
  updateUserSettings: (updates: Partial<UserSettings>) => void
  updateGenerationSettings: (updates: Partial<GenerationSettings>) => void
  refreshStats: () => Promise<void>
  isLoading: boolean
  resetToDefaults: () => void
  getCurrentSettings: () => { userSettings: UserSettings; generationSettings: GenerationSettings }
}

// Default values
const defaultUserSettings: UserSettings = {
  name: '',
  email: '',
  bio: '',
  company: '',
  role: '',
  notifications: {
    email: true,
    push: false,
    marketing: false
  },
  language: 'en',
  timezone: 'UTC',
  joinDate: new Date().toISOString().split('T')[0]
}

const defaultGenerationSettings: GenerationSettings = {
  maxTokens: 2000,
  temperature: 0.7,
  autoSave: true,
  backupFrequency: 'weekly',
  contentQuality: 'balanced',
  enableMultiModel: false
}

const defaultUserStats: UserStats = {
  contentGenerated: 0,
  totalTimeSaved: 0,
  averageRating: 0,
  daysActive: 0
}

// Storage keys
const USER_SETTINGS_KEY = 'writerzroom_user_settings'
const GENERATION_SETTINGS_KEY = 'writerzroom_generation_settings'

// Context
const SettingsContext = createContext<SettingsContextType | undefined>(undefined)

// Provider component
export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [userSettings, setUserSettings] = useState<UserSettings>(defaultUserSettings)
  const [generationSettings, setGenerationSettings] = useState<GenerationSettings>(defaultGenerationSettings)
  const [userStats, setUserStats] = useState<UserStats>(defaultUserStats)
  const [recentContent, setRecentContent] = useState<ContentItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Track if mounted to skip initial save
  const hasMounted = React.useRef(false)

  // Load settings from localStorage on mount
  useEffect(() => {
    const loadSettings = async () => {
      try {
        if (typeof window !== 'undefined') {
          // Load user settings
          const storedUser = localStorage.getItem(USER_SETTINGS_KEY)
          if (storedUser) {
            const parsed = JSON.parse(storedUser)
            setUserSettings(prev => ({ ...prev, ...parsed }))
          }

          // Load generation settings
          const storedGen = localStorage.getItem(GENERATION_SETTINGS_KEY)
          if (storedGen) {
            const parsed = JSON.parse(storedGen)
            setGenerationSettings(prev => ({ ...prev, ...parsed }))
          }

          console.log('✅ Settings loaded from localStorage')
        }
      } catch (error) {
        console.error('❌ Failed to load settings from storage:', error)
      } finally {
        setIsLoading(false)
      }
    }

    loadSettings()
  }, [])

  // Save to localStorage whenever settings change (after initial load)
  useEffect(() => {
    if (!hasMounted.current) {
      hasMounted.current = true
      return
    }

    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem(USER_SETTINGS_KEY, JSON.stringify(userSettings))
        localStorage.setItem(GENERATION_SETTINGS_KEY, JSON.stringify(generationSettings))
        console.log('✅ Settings saved to localStorage')
      } catch (error) {
        console.error('❌ Failed to save settings to storage:', error)
        throw error
      }
    }
  }, [userSettings, generationSettings])

  // Load stats from generated content
  useEffect(() => {
    if (!isLoading) {
      refreshStats()
    }
  }, [isLoading])

  // Refresh stats from content API
  const refreshStats = async () => {
    try {
      const response = await fetch('/api/content/list')
      if (response.ok) {
        const data = await response.json()
        const content: ContentItem[] = data.content || []
        
        // Calculate stats from content
        const stats: UserStats = {
          contentGenerated: content.length,
          totalTimeSaved: Math.round(content.reduce((acc, item) => {
            const words = item.words || item.metadata?.wordCount || 0;
            return acc + (words / 200);
          }, 0)),
          averageRating: content.length > 0 
            ? Math.round((content.reduce((acc, item) => acc + (item.rating || 0), 0) / content.length) * 10) / 10
            : 0,
          daysActive: new Set(content.map(item => 
            new Date(item.createdAt).toDateString())).size
        }
        
        setUserStats(stats)
        setRecentContent(content.slice(0, 5)) // Top 5 recent
      }
    } catch (error) {
      console.error('Failed to refresh stats:', error)
    }
  }

  // Update user settings
  const updateUserSettings = (updates: Partial<UserSettings>) => {
    setUserSettings(prev => {
      const updated = { ...prev, ...updates }
      
      // Handle nested notifications object
      if (updates.notifications) {
        updated.notifications = { ...prev.notifications, ...updates.notifications }
      }
      
      return updated
    })
  }

  // Update generation settings
  const updateGenerationSettings = (updates: Partial<GenerationSettings>) => {
    setGenerationSettings(prev => ({ ...prev, ...updates }))
  }

  // Reset to defaults
  const resetToDefaults = () => {
    setUserSettings(defaultUserSettings)
    setGenerationSettings(defaultGenerationSettings)
  }

  // Get current settings (for API calls)
  const getCurrentSettings = () => {
    return { userSettings, generationSettings }
  }

  return (
    <SettingsContext.Provider value={{
      userSettings,
      generationSettings,
      userStats,
      recentContent,
      updateUserSettings,
      updateGenerationSettings,
      refreshStats,
      isLoading,
      resetToDefaults,
      getCurrentSettings
    }}>
      {children}
    </SettingsContext.Provider>
  )
}

// Hook to use settings
export function useSettings() {
  const context = useContext(SettingsContext)
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider')
  }
  return context
}