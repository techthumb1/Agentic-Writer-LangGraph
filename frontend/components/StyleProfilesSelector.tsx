'use client'

import React, { useState } from 'react'
import { useStyleProfiles } from '@/hooks/useStyleProfiles'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Loader2, AlertCircle, RefreshCw, ChevronRight, GraduationCap, Settings, BarChart3, BookOpen, Megaphone } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

interface StyleProfileSelectorProps {
  value?: string
  onChange: (slug: string) => void
  label?: string
  required?: boolean
  showDescription?: boolean
  className?: string
  disabled?: boolean
}

// Category mapping based on your category_overview.yaml
const CATEGORY_INFO = {
  academic_research: {
    name: "Academic & Research",
    description: "Scholarly writing for academic institutions, research papers, and peer-reviewed publications",
    icon: GraduationCap
  },
  technical_documentation: {
    name: "Technical Documentation", 
    description: "Precise technical writing for developers, engineers, and technical professionals",
    icon: Settings
  },
  business_strategy: {
    name: "Business Strategy",
    description: "Strategic business communication for executives, stakeholders, and decision-makers", 
    icon: BarChart3
  },
  educational_content: {
    name: "Educational Content",
    description: "Instructional content for learning, training, and knowledge transfer",
    icon: BookOpen
  },
  marketing_communications: {
    name: "Marketing Communications",
    description: "Persuasive marketing content for brand building and customer engagement",
    icon: Megaphone
  }
}

type CategoryKey = keyof typeof CATEGORY_INFO

export default function StyleProfileSelector({
  value,
  onChange,
  label = "Style Profile",
  required = false,
  showDescription = true,
  className = "",
  disabled = false
}: StyleProfileSelectorProps) {
  const { styleProfiles, isLoading, isError, error } = useStyleProfiles()
  const [selectedCategory, setSelectedCategory] = useState<string>("")

  // Group profiles by category
  const profilesByCategory = React.useMemo(() => {
    if (!styleProfiles) return {}
    
    return styleProfiles.reduce((acc, profile) => {
      const category = profile.category || 'other'
      if (!acc[category]) {
        acc[category] = []
      }
      acc[category].push(profile)
      return acc
    }, {} as Record<string, typeof styleProfiles>)
  }, [styleProfiles])

  // Find the selected profile for description display
  const selectedProfile = styleProfiles?.find(profile => profile.id === value)
  const selectedProfileCategory = selectedProfile?.category

  // Get available categories
  const availableCategories = Object.keys(profilesByCategory).filter(cat => 
    profilesByCategory[cat] && profilesByCategory[cat].length > 0
  )

  // Get profiles for selected category
  const categoryProfiles = selectedCategory ? profilesByCategory[selectedCategory] || [] : []

  // Handle category selection
  const handleCategoryChange = (categoryKey: string) => {
    setSelectedCategory(categoryKey)
    // Clear profile selection when category changes
    onChange("")
  }

  // Handle profile selection
  const handleProfileChange = (profileId: string) => {
    onChange(profileId)
  }

  // Handle retry
  const handleRetry = () => {
    window.location.reload()
  }

  // Loading state
  if (isLoading) {
    return (
      <div className={`space-y-2 ${className}`}>
        {label && (
          <Label className="text-sm font-medium text-foreground">
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </Label>
        )}
        <div className="flex items-center gap-2 p-3 border rounded-lg bg-muted/50">
          <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Loading style profiles...</span>
        </div>
      </div>
    )
  }

  // Error state
  if (isError) {
    return (
      <div className={`space-y-2 ${className}`}>
        {label && (
          <Label className="text-sm font-medium text-foreground">
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </Label>
        )}
        <div className="space-y-2">
          <div className="flex items-center gap-2 p-3 border border-red-200 rounded-lg bg-red-50 text-red-700 dark:bg-red-950 dark:border-red-800 dark:text-red-300">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">Failed to load style profiles</span>
          </div>
          {error && (
            <p className="text-xs text-red-600 dark:text-red-400">{error.message}</p>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={handleRetry}
            className="w-full"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    )
  }

  // No profiles available
  if (!styleProfiles || styleProfiles.length === 0) {
    return (
      <div className={`space-y-2 ${className}`}>
        {label && (
          <Label className="text-sm font-medium text-foreground">
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </Label>
        )}
        <div className="flex items-center gap-2 p-3 border rounded-lg bg-muted/50">
          <AlertCircle className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">No style profiles available</span>
        </div>
      </div>
    )
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {label && (
        <div className="flex items-center justify-between">
          <Label className="text-sm font-medium text-foreground">
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </Label>
          <Badge variant="secondary" className="text-xs">
            {styleProfiles.length} profiles • {availableCategories.length} categories
          </Badge>
        </div>
      )}
      
      {/* Category Selection */}
      <div className="space-y-3">
        <div>
          <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            Step 1: Select Category
          </Label>
          <Select 
            value={selectedCategory} 
            onValueChange={handleCategoryChange}
            disabled={disabled}
          >
            <SelectTrigger className="mt-1">
              <SelectValue placeholder="Choose a content category" />
            </SelectTrigger>
            <SelectContent>
              {availableCategories.map((categoryKey) => {
                const categoryInfo = CATEGORY_INFO[categoryKey as CategoryKey] || {
                  name: categoryKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
                  description: "Style profiles for this category",
                  icon: Settings
                }
                
                const IconComponent = categoryInfo.icon
                
                return (
                  <SelectItem key={categoryKey} value={categoryKey}>
                    <div className="flex items-center gap-3">
                      <IconComponent className="h-4 w-4 text-muted-foreground" />
                      <div className="flex flex-col">
                        <span className="font-medium">{categoryInfo.name}</span>
                        <span className="text-xs text-muted-foreground">
                          {profilesByCategory[categoryKey]?.length || 0} profiles
                        </span>
                      </div>
                    </div>
                  </SelectItem>
                )
              })}
            </SelectContent>
          </Select>
        </div>

        {/* Profile Selection */}
        {selectedCategory && (
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                Step 2: Select Style Profile
              </Label>
              <ChevronRight className="h-3 w-3 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">
                {CATEGORY_INFO[selectedCategory as CategoryKey]?.name || selectedCategory}
              </span>
            </div>
            <Select 
              value={value || ""} 
              onValueChange={handleProfileChange}
              disabled={disabled}
            >
              <SelectTrigger>
                <SelectValue placeholder="Choose a specific style profile" />
              </SelectTrigger>
              <SelectContent>
                {categoryProfiles.map((profile, index) => (
                  <SelectItem key={`${profile.id}-${index}`} value={profile.id}>
                    <div className="flex flex-col">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{profile.name}</span>
                        {profile.metadata?.complexity_level !== undefined && (
                          <Badge variant="outline" className="text-xs">
                            {String(profile.metadata.complexity_level)}
                          </Badge>
                        )}
                      </div>
                      {profile.description && (
                        <span className="text-xs text-muted-foreground line-clamp-1">
                          {profile.description}
                        </span>
                      )}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}
      </div>

      {/* Selected Profile Details */}
      {showDescription && selectedProfile && (
        <Card className="border-primary/20 bg-primary/5 dark:bg-primary/10">
          <CardContent className="p-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {selectedProfileCategory && CATEGORY_INFO[selectedProfileCategory as CategoryKey] ? (
                    React.createElement(CATEGORY_INFO[selectedProfileCategory as CategoryKey].icon, {
                      className: "h-4 w-4 text-muted-foreground"
                    })
                  ) : (
                    <Settings className="h-4 w-4 text-muted-foreground" />
                  )}
                  <div>
                    <h4 className="text-sm font-semibold text-foreground">{selectedProfile.name}</h4>
                    <p className="text-xs text-muted-foreground">
                      {selectedProfileCategory && CATEGORY_INFO[selectedProfileCategory as CategoryKey]
                        ? CATEGORY_INFO[selectedProfileCategory as CategoryKey].name
                        : selectedProfile.category
                      }
                    </p>
                  </div>
                </div>
                <Badge variant="secondary" className="text-xs">
                  Selected
                </Badge>
              </div>
              
              {selectedProfile.description && (
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {selectedProfile.description}
                </p>
              )}

              {/* Style Parameters */}
              <div className="grid grid-cols-2 gap-3 pt-2 border-t border-border/50">
                {selectedProfile.metadata?.complexity_level !== undefined && (
                  <div>
                    <span className="text-xs font-medium text-muted-foreground">Complexity</span>
                    <p className="text-xs text-foreground">
                      {String(selectedProfile.metadata.complexity_level)}
                    </p>
                  </div>
                )}
                {selectedProfile.metadata?.target_audience !== undefined && (
                  <div>
                    <span className="text-xs font-medium text-muted-foreground">Audience</span>
                    <p className="text-xs text-foreground">
                      {String(selectedProfile.metadata.target_audience)}
                    </p>
                  </div>
                )}
                {selectedProfile.tone && (
                  <div>
                    <span className="text-xs font-medium text-muted-foreground">Tone</span>
                    <p className="text-xs text-foreground">{selectedProfile.tone}</p>
                  </div>
                )}
                {selectedProfile.voice && (
                  <div>
                    <span className="text-xs font-medium text-muted-foreground">Voice</span>
                    <p className="text-xs text-foreground">{selectedProfile.voice}</p>
                  </div>
                )}
              </div>

              {selectedProfile.system_prompt && (
                <div className="pt-2 border-t border-border/50">
                  <span className="text-xs font-medium text-muted-foreground">Style Guide Preview</span>
                  <div className="mt-1 p-2 bg-muted/50 rounded text-xs text-muted-foreground">
                    {selectedProfile.system_prompt.slice(0, 120)}
                    {selectedProfile.system_prompt.length > 120 && '...'}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}