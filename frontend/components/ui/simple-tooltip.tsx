// frontend/components/ui/simple-tooltip.tsx
"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface SimpleTooltipProps {
  children: React.ReactNode
  content: React.ReactNode
  side?: "top" | "right" | "bottom" | "left"
  className?: string
  delayDuration?: number
  disabled?: boolean
}

export function SimpleTooltip({
  children,
  content,
  side = "top",
  className,
  delayDuration = 300,
  disabled = false,
}: SimpleTooltipProps) {
  const [isVisible, setIsVisible] = React.useState(false)
  const [position, setPosition] = React.useState({ x: 0, y: 0 })
  const timeoutRef = React.useRef<NodeJS.Timeout | null>(null)
  const triggerRef = React.useRef<HTMLDivElement>(null)
  const tooltipRef = React.useRef<HTMLDivElement>(null)

  const showTooltip = React.useCallback(() => {
    if (disabled) return

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true)

      // Calculate position
      if (triggerRef.current && tooltipRef.current) {
        const triggerRect = triggerRef.current.getBoundingClientRect()
        const tooltipRect = tooltipRef.current.getBoundingClientRect()

        let x = 0
        let y = 0

        switch (side) {
          case "top":
            x = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2
            y = triggerRect.top - tooltipRect.height - 8
            break
          case "bottom":
            x = triggerRect.left + triggerRect.width / 2 - tooltipRect.width / 2
            y = triggerRect.bottom + 8
            break
          case "left":
            x = triggerRect.left - tooltipRect.width - 8
            y = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2
            break
          case "right":
            x = triggerRect.right + 8
            y = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2
            break
        }

        // Keep within viewport
        const padding = 8
        x = Math.max(padding, Math.min(x, window.innerWidth - tooltipRect.width - padding))
        y = Math.max(padding, Math.min(y, window.innerHeight - tooltipRect.height - padding))

        setPosition({ x, y })
      }
    }, delayDuration)
  }, [side, delayDuration, disabled])

  const hideTooltip = React.useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    setIsVisible(false)
  }, [])

  React.useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return (
    <>
      <div
        ref={triggerRef}
        onMouseEnter={showTooltip}
        onMouseLeave={hideTooltip}
        onFocus={showTooltip}
        onBlur={hideTooltip}
        className="inline-block"
      >
        {children}
      </div>

      {isVisible && !disabled && (
        <div
          ref={tooltipRef}
          className={cn(
            "fixed z-[100] px-2 py-1 text-xs text-white bg-gray-900 rounded shadow-lg pointer-events-none",
            "animate-in fade-in-0 zoom-in-95 duration-150",
            "dark:bg-gray-700",
            className
          )}
          style={{
            left: `${position.x}px`,
            top: `${position.y}px`,
          }}
        >
          {content}

          {/* Arrow */}
          <div
            className={cn(
              "absolute w-2 h-2 bg-gray-900 dark:bg-gray-700 rotate-45",
              side === "top" && "bottom-[-4px] left-1/2 transform -translate-x-1/2",
              side === "bottom" && "top-[-4px] left-1/2 transform -translate-x-1/2",
              side === "left" && "right-[-4px] top-1/2 transform -translate-y-1/2",
              side === "right" && "left-[-4px] top-1/2 transform -translate-y-1/2"
            )}
          />
        </div>
      )}
    </>
  )
}