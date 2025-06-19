'use client'

import { useEffect, useCallback } from 'react'

// Extend Window interface to include gtag
declare global {
  interface Window {
    gtag?: (
      command: 'config' | 'event' | 'exception' | 'page_view' | 'purchase' | 'refund' | 'select_content' | 'set' | 'timing_complete',
      targetId: string,
      config?: Record<string, unknown>
    ) => void;
  }
}

interface PerformanceMetric {
  name: string
  value: number
  timestamp: number
}

export function usePerformanceMonitoring() {
  const reportMetric = useCallback((metric: PerformanceMetric) => {
    // Send to analytics service
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'performance_metric', {
        custom_parameter_1: metric.name,
        custom_parameter_2: metric.value,
      })
    }
    
  }, [])

  const measureFunction = useCallback(
    <T extends unknown[], R>(
      fn: (...args: T) => R,
      name: string
    ): ((...args: T) => R) => {
      return (...args: T): R => {
        const start = performance.now()
        const result = fn(...args)
        const end = performance.now()
        
        reportMetric({
          name,
          value: end - start,
          timestamp: Date.now(),
        })
        
        return result
      }
    },
    [reportMetric]
  )

  useEffect(() => {
    // Monitor Core Web Vitals
    if (typeof window !== 'undefined') {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.entryType === 'navigation') {
            const navEntry = entry as PerformanceNavigationTiming
            
            reportMetric({
              name: 'page_load_time',
              value: navEntry.loadEventEnd - navEntry.fetchStart,
              timestamp: Date.now(),
            })
          }
        }
      })
      
      observer.observe({ entryTypes: ['navigation'] })
      
      return () => observer.disconnect()
    }
  }, [reportMetric])

  return {
    reportMetric,
    measureFunction,
  }
}