'use client'

import React from 'react'
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
import { Loader2, AlertCircle, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

interface StyleProfileSelectorProps {
  value?: string
  onChange: (slug: string) => void
  label?: string
  placeholder?: string
  required?: boolean
  showDescription?: boolean
  className?: string
  disabled?: boolean
}

export default function StyleProfileSelector({
  value,
  onChange,
  label = "Style Profile",
  placeholder = "Select a style profile",
  required = false,
  showDescription = true,
  className = "",
  disabled = false
}: StyleProfileSelectorProps) {
  const { styleProfiles, isLoading, isError, error } = useStyleProfiles()

  // Find the selected profile for description display
  const selectedProfile = styleProfiles?.find(profile => profile.id === value)

  // Handle retry
  const handleRetry = () => {
    window.location.reload() // Simple reload since refetch isn't available
  }

  // Loading state
  if (isLoading) {
    return (
      <div className={`space-y-2 ${className}`}>
        {label && (
          <Label className="text-sm font-medium">
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
          <Label className="text-sm font-medium">
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </Label>
        )}
        <div className="space-y-2">
          <div className="flex items-center gap-2 p-3 border border-red-200 rounded-lg bg-red-50 text-red-700">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">Failed to load style profiles</span>
          </div>
          {error && (
            <p className="text-xs text-red-600">{error.message}</p>
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
          <Label className="text-sm font-medium">
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
    <div className={`space-y-2 ${className}`}>
      {label && (
        <Label className="text-sm font-medium">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
          <Badge variant="secondary" className="ml-2 text-xs">
            {styleProfiles.length} available
          </Badge>
        </Label>
      )}
      
      <Select 
        value={value || undefined} 
        onValueChange={onChange}
        disabled={disabled}
      >
        <SelectTrigger className="w-full">
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          {styleProfiles.map((profile, index) => (
            <SelectItem 
              key={`profile-selector-${profile.id}-${index}`}
              value={profile.id || `profile-${profile.name}`}
              className="flex flex-col items-start"
            >
              <div className="flex flex-col">
                <span className="font-medium">{profile.name}</span>
                {profile.description && (
                  <span className="text-xs text-muted-foreground line-clamp-2">
                    {profile.description}
                  </span>
                )}
                <div className="flex gap-1 mt-1">
                  <Badge variant="secondary" className="text-xs">
                    {profile.category}
                  </Badge>
                </div>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Selected Profile Description */}
      {showDescription && selectedProfile && (
        <Card className="mt-2">
          <CardContent className="p-3">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <h4 className="text-sm font-medium">{selectedProfile.name}</h4>
                <div className="flex gap-1">
                  <Badge variant="secondary" className="text-xs">
                    {selectedProfile.category}
                  </Badge>
                </div>
              </div>
              
              {selectedProfile.description && (
                <p className="text-xs text-muted-foreground">
                  {selectedProfile.description}
                </p>
              )}

              {selectedProfile.system_prompt && (
                <div className="mt-2 p-2 bg-muted/50 rounded text-xs">
                  <span className="font-medium">Style Guide: </span>
                  <span className="text-muted-foreground">
                    {selectedProfile.system_prompt.slice(0, 150)}
                    {selectedProfile.system_prompt.length > 150 && '...'}
                  </span>
                </div>
              )}

              {selectedProfile.settings && Object.keys(selectedProfile.settings).length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {Object.entries(selectedProfile.settings).slice(0, 3).map(([key, value], settingIndex) => (
                    <Badge key={`setting-${selectedProfile.id}-${key}-${settingIndex}`} variant="outline" className="text-xs">
                      {key}: {String(value)}
                    </Badge>
                  ))}
                  {Object.keys(selectedProfile.settings).length > 3 && (
                    <Badge variant="outline" className="text-xs">
                      +{Object.keys(selectedProfile.settings).length - 3} more
                    </Badge>
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Debug Info (only in development) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="text-xs text-muted-foreground">
          Debug: {styleProfiles.length} profiles loaded
          {value && ` | Selected: ${value}`}
        </div>
      )}
    </div>
  )
}