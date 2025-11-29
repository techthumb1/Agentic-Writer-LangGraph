"use client"

import { Toaster, toast } from 'sonner'
import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'

export function ToastProvider() {
  const { theme } = useTheme()
  const pathname = usePathname()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  // Clear toasts when navigating between pages (as backup to duration)
  useEffect(() => {
    if (mounted) {
      // Small delay to prevent clearing toasts immediately on mount
      const timer = setTimeout(() => {
        toast.dismiss()
      }, 100)
      
      return () => clearTimeout(timer)
    }
  }, [pathname, mounted])

  if (!mounted) {
    return null
  }

  return (
    <Toaster
      position="bottom-right"
      expand={true}
      richColors={true}
      closeButton={true}
      duration={2500} // Default fallback duration
      visibleToasts={4} // Limit visible toasts
      gap={8}
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