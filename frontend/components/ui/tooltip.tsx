// frontend/components/ui/tooltip.tsx
"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface TooltipContextType {
  open: boolean
  setOpen: (open: boolean) => void
  delayDuration: number
}

const TooltipContext = React.createContext<TooltipContextType>({
  open: false,
  setOpen: () => {},
  delayDuration: 300,
})

// Tooltip Provider
interface TooltipProviderProps {
  children: React.ReactNode
  delayDuration?: number
  skipDelayDuration?: number
}

export function TooltipProvider({
  children,
  delayDuration = 300,
}: TooltipProviderProps) {
  const [open, setOpen] = React.useState(false)

  return (
    <TooltipContext.Provider value={{ open, setOpen, delayDuration }}>
      {children}
    </TooltipContext.Provider>
  )
}

// Main Tooltip Component
interface TooltipProps {
  children: React.ReactNode
  delayDuration?: number
}

export function Tooltip({ children, delayDuration }: TooltipProps) {
  const [open, setOpen] = React.useState(false)
  const timeoutRef = React.useRef<NodeJS.Timeout | undefined>(undefined)

  const handleMouseEnter = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    timeoutRef.current = setTimeout(() => {
      setOpen(true)
    }, delayDuration || 300)
  }

  const handleMouseLeave = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
    setOpen(false)
  }

  React.useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return (
    <TooltipContext.Provider value={{ open, setOpen, delayDuration: delayDuration || 300 }}>
      <div
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onFocus={handleMouseEnter}
        onBlur={handleMouseLeave}
        className="relative inline-block"
      >
        {children}
      </div>
    </TooltipContext.Provider>
  )
}

// Tooltip Trigger
interface TooltipTriggerProps extends React.HTMLAttributes<HTMLElement> {
  children: React.ReactNode
  asChild?: boolean
}

export const TooltipTrigger = React.forwardRef<
  HTMLElement,
  TooltipTriggerProps
>(({ children, asChild = false, className, ...props }, ref) => {
  if (asChild && React.isValidElement(children)) {
    // Type assertion for React element with props
    const childElement = children as React.ReactElement<React.HTMLAttributes<HTMLElement> & { ref?: React.Ref<HTMLElement> }>
    return React.cloneElement(childElement, {
      ...props,
      className: cn(childElement.props.className, className),
    } as React.HTMLAttributes<HTMLElement>)
  }

  return (
    <span
      ref={ref as React.Ref<HTMLSpanElement>}
      className={cn("cursor-pointer", className)}
      {...props}
    >
      {children}
    </span>
  )
})
TooltipTrigger.displayName = "TooltipTrigger"

// Tooltip Content
interface TooltipContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  side?: "top" | "right" | "bottom" | "left"
  align?: "start" | "center" | "end"
  sideOffset?: number
  alignOffset?: number
  className?: string
}

export const TooltipContent = React.forwardRef<
  HTMLDivElement,
  TooltipContentProps
>(({
  children,
  side = "top",
  align = "center",
  sideOffset = 8,
  alignOffset = 0,
  className,
  ...props
}, ref) => {
  const { open } = React.useContext(TooltipContext)
  const [position, setPosition] = React.useState({ x: 0, y: 0 })
  const contentRef = React.useRef<HTMLDivElement>(null)
  const triggerRef = React.useRef<HTMLElement | null>(null)

  // Position calculation
  React.useEffect(() => {
    if (!open || !triggerRef.current) return

    const trigger = triggerRef.current
    const content = contentRef.current
    if (!content) return

    const triggerRect = trigger.getBoundingClientRect()
    const contentRect = content.getBoundingClientRect()
    const viewport = {
      width: window.innerWidth,
      height: window.innerHeight,
    }

    let x = 0
    let y = 0

    // Calculate position based on side
    switch (side) {
      case "top":
        x = triggerRect.left + triggerRect.width / 2 - contentRect.width / 2
        y = triggerRect.top - contentRect.height - sideOffset
        break
      case "bottom":
        x = triggerRect.left + triggerRect.width / 2 - contentRect.width / 2
        y = triggerRect.bottom + sideOffset
        break
      case "left":
        x = triggerRect.left - contentRect.width - sideOffset
        y = triggerRect.top + triggerRect.height / 2 - contentRect.height / 2
        break
      case "right":
        x = triggerRect.right + sideOffset
        y = triggerRect.top + triggerRect.height / 2 - contentRect.height / 2
        break
    }

    // Adjust for alignment
    if (side === "top" || side === "bottom") {
      if (align === "start") x = triggerRect.left + alignOffset
      if (align === "end") x = triggerRect.right - contentRect.width + alignOffset
    } else {
      if (align === "start") y = triggerRect.top + alignOffset
      if (align === "end") y = triggerRect.bottom - contentRect.height + alignOffset
    }

    // Keep tooltip within viewport
    x = Math.max(8, Math.min(x, viewport.width - contentRect.width - 8))
    y = Math.max(8, Math.min(y, viewport.height - contentRect.height - 8))

    setPosition({ x, y })
  }, [open, side, align, sideOffset, alignOffset])

  // Find trigger element
  React.useEffect(() => {
    const findTrigger = (element: Element): HTMLElement | null => {
      if (element.previousElementSibling) {
        return element.previousElementSibling as HTMLElement
      }
      return element.parentElement?.querySelector('[data-tooltip-trigger]') as HTMLElement || null
    }

    if (contentRef.current) {
      triggerRef.current = findTrigger(contentRef.current)
    }
  }, [])

  if (!open) return null

  return (
    <>
      {/* Backdrop for mobile */}
      <div className="fixed inset-0 z-[60] sm:hidden" />
      
      {/* Tooltip content */}
      <div
        ref={ref || contentRef}
        className={cn(
          "fixed z-[70] px-3 py-1.5 text-sm text-white bg-gray-900 rounded-md shadow-lg pointer-events-none",
          "animate-in fade-in-0 zoom-in-95 duration-200",
          "dark:bg-gray-800 dark:text-gray-200",
          // Arrow styles based on side
          side === "top" && "after:absolute after:top-full after:left-1/2 after:transform after:-translate-x-1/2 after:border-4 after:border-transparent after:border-t-gray-900 dark:after:border-t-gray-800",
          side === "bottom" && "before:absolute before:bottom-full before:left-1/2 before:transform before:-translate-x-1/2 before:border-4 before:border-transparent before:border-b-gray-900 dark:before:border-b-gray-800",
          side === "left" && "after:absolute after:left-full after:top-1/2 after:transform after:-translate-y-1/2 after:border-4 after:border-transparent after:border-l-gray-900 dark:after:border-l-gray-800",
          side === "right" && "before:absolute before:right-full before:top-1/2 before:transform before:-translate-y-1/2 before:border-4 before:border-transparent before:border-r-gray-900 dark:before:border-r-gray-800",
          className
        )}
        style={{
          left: `${position.x}px`,
          top: `${position.y}px`,
        }}
        {...props}
      >
        {children}
      </div>
    </>
  )
})
TooltipContent.displayName = "TooltipContent"

// Utility hook for using tooltip context
export function useTooltip() {
  const context = React.useContext(TooltipContext)
  if (!context) {
    throw new Error("useTooltip must be used within a TooltipProvider")
  }
  return context
}