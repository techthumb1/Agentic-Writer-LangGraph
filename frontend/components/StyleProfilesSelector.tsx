'use client'

import React from 'react'
import { useStyleProfiles } from '@/hooks/useStyleProfiles'
import type { StyleProfile } from '@/types'

interface StyleProfileSelectorProps {
  value?: string
  onChange: (slug: string) => void
}

export default function StyleProfileSelector({
  value,
  onChange,
}: StyleProfileSelectorProps) {
  const { profiles, isLoading, isError } = useStyleProfiles()

  if (isLoading) return <p>Loading styles…</p>
  if (isError)   return <p className="text-red-500">Failed to load styles</p>

  return (
    <select
      value={value || ''}
      onChange={e => onChange(e.target.value)}
      className="border rounded p-2 w-full"
    >
      <option value="">Select a style profile</option>
      {profiles.map((profile: StyleProfile) => (
        <option key={profile.id} value={profile.id}>
          {profile.name}
        </option>
      ))}
    </select>
  )
}
