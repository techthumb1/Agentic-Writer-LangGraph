/* File: frontend/app/theme-provider.tsx */
"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import { type ThemeProviderProps } from "next-themes"

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  React.useEffect(() => {
    // Load and apply custom theme on mount
    const customTheme = localStorage.getItem('custom-theme')
    
    if (customTheme === 'agentwrite-pro') {
      document.body.classList.add('agentwrite-pro')
      document.documentElement.classList.add('agentwrite-pro')
    } else {
      document.body.classList.remove('agentwrite-pro')
      document.documentElement.classList.remove('agentwrite-pro')
    }
  }, [])

  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange={false}
      {...props}
    >
      {children}
    </NextThemesProvider>
  )
}