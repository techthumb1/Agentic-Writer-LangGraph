// File: frontend/components/ui/separator.tsx
// Create this file if you don't have shadcn/ui separator component

import * as React from "react"
import { cn } from "@/lib/utils"

const Separator = React.forwardRef<
  React.ElementRef<"div">,
  React.ComponentPropsWithoutRef<"div"> & {
    orientation?: "horizontal" | "vertical"
    decorative?: boolean
  }
>(
  (
    { className, orientation = "horizontal", decorative = true, ...props },
    ref
  ) => (
    <div
      ref={ref}
      role={decorative ? "none" : "separator"}
      aria-orientation={orientation}
      className={cn(
        "shrink-0 bg-border",
        orientation === "horizontal" ? "h-px w-full" : "h-full w-px",
        className
      )}
      {...props}
    />
  )
)
Separator.displayName = "Separator"

export { Separator }
