// File: frontend/lib/settings-context.tsx
'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'

// Types
export interface UserSettings {
  name: string
  email: string
  bio: string
  notifications: {
    email: boolean
    push: boolean
    marketing: boolean
  }
  language: string
  timezone: string
}

export interface GenerationSettings {
  maxTokens: number
  temperature: number
  autoSave: boolean
  backupFrequency: string
  contentQuality: 'fast' | 'balanced' | 'premium'
  enableMultiModel: boolean
}

interface SettingsContextType {
  userSettings: UserSettings
  generationSettings: GenerationSettings
  updateUserSettings: (updates: Partial<UserSettings>) => void
  updateGenerationSettings: (updates: Partial<GenerationSettings>) => void
  isLoading: boolean
  resetToDefaults: () => void
  getCurrentSettings: () => { userSettings: UserSettings; generationSettings: GenerationSettings }
}

// Default values
const defaultUserSettings: UserSettings = {
  name: '',
  email: '',
  bio: '',
  notifications: {
    email: true,
    push: false,
    marketing: false
  },
  language: 'en',
  timezone: 'UTC'
}

const defaultGenerationSettings: GenerationSettings = {
  maxTokens: 2000,
  temperature: 0.7,
  autoSave: true,
  backupFrequency: 'weekly',
  contentQuality: 'balanced',
  enableMultiModel: false
}

// Storage key
const SETTINGS_STORAGE_KEY = 'writerzroom-settings'

// Context
const SettingsContext = createContext<SettingsContextType | undefined>(undefined)

// Provider component
export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [userSettings, setUserSettings] = useState<UserSettings>(defaultUserSettings)
  const [generationSettings, setGenerationSettings] = useState<GenerationSettings>(defaultGenerationSettings)
  const [isLoading, setIsLoading] = useState(true)

  // Load settings from localStorage on mount
  useEffect(() => {
    const loadSettings = async () => {
      try {
        if (typeof window !== 'undefined') {
          const stored = localStorage.getItem(SETTINGS_STORAGE_KEY)
          if (stored) {
            const parsed = JSON.parse(stored)
            
            // Merge with defaults to handle missing fields
            if (parsed.userSettings) {
              setUserSettings(prev => ({ ...prev, ...parsed.userSettings }))
            }
            if (parsed.generationSettings) {
              setGenerationSettings(prev => ({ ...prev, ...parsed.generationSettings }))
            }
            
            console.log('✅ Settings loaded from localStorage')
          }
        }
      } catch (error) {
        console.error('❌ Failed to load settings from storage:', error)
      } finally {
        setIsLoading(false)
      }
    }

    loadSettings()
  }, [])

  // Save to localStorage whenever settings change
  const saveToStorage = (userSettings: UserSettings, generationSettings: GenerationSettings) => {
    try {
      if (typeof window !== 'undefined') {
        const toSave = {
          userSettings,
          generationSettings,
          lastUpdated: new Date().toISOString()
        }
        localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(toSave))
        console.log('✅ Settings saved to localStorage')
      }
    } catch (error) {
      console.error('❌ Failed to save settings to storage:', error)
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
      
      // Save to localStorage
      saveToStorage(updated, generationSettings)
      
      return updated
    })
  }

  // Update generation settings
  const updateGenerationSettings = (updates: Partial<GenerationSettings>) => {
    setGenerationSettings(prev => {
      const updated = { ...prev, ...updates }
      
      // Save to localStorage
      saveToStorage(userSettings, updated)
      
      return updated
    })
  }

  // Reset to defaults
  const resetToDefaults = () => {
    setUserSettings(defaultUserSettings)
    setGenerationSettings(defaultGenerationSettings)
    saveToStorage(defaultUserSettings, defaultGenerationSettings)
  }

  // Get current settings (for API calls)
  const getCurrentSettings = () => {
    return { userSettings, generationSettings }
  }

  return (
    <SettingsContext.Provider value={{
      userSettings,
      generationSettings,
      updateUserSettings,
      updateGenerationSettings,
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