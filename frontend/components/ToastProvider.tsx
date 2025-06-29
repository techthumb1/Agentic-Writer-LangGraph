/* File: frontend/components/ToastProvider.tsx */
"use client"

import { Toaster } from 'sonner'
import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'

export function ToastProvider() {
  const { theme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  return (
    <Toaster
      position="bottom-right"
      expand={true}
      richColors={true}
      closeButton={true}
      duration={4000}
      toastOptions={{
        style: {
          background: 'hsl(var(--background))',
          color: 'hsl(var(--foreground))',
          border: '1px solid hsl(var(--border))',
        },
        className: 'toast-item',
        descriptionClassName: 'toast-description',
        actionButtonStyle: {
          background: 'hsl(var(--primary))',
          color: 'hsl(var(--primary-foreground))',
        },
        cancelButtonStyle: {
          background: 'hsl(var(--secondary))',
          color: 'hsl(var(--secondary-foreground))',
        },
      }}
      theme={theme as 'light' | 'dark' | 'system'}
    />
    )
}  