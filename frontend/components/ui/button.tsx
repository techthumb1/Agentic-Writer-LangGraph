import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground shadow-xs hover:bg-primary/90 border border-primary",
        destructive:
          "bg-destructive text-white shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60 border border-destructive",
        outline:
          "border border-input bg-background shadow-xs hover:bg-accent hover:text-accent-foreground dark:bg-background dark:border-input dark:hover:bg-input/50 dark:text-foreground",
        secondary:
          "bg-secondary text-secondary-foreground shadow-xs hover:bg-secondary/80 border border-secondary",
        ghost:
          "hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50 text-foreground",
        link: 
          "text-primary underline-offset-4 hover:underline bg-transparent",
        // ✅ NEW: Add explicit white/light button variant for better visibility
        light:
          "bg-white text-gray-900 border border-gray-300 shadow-xs hover:bg-gray-50 hover:text-gray-900 dark:bg-gray-100 dark:text-gray-900 dark:border-gray-300 dark:hover:bg-gray-200",
        // ✅ NEW: Add purple gradient variant
        gradient:
          "bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-xs hover:from-purple-700 hover:to-pink-700 border border-purple-600",
      },
      size: {
        default: "h-9 px-4 py-2 has-[>svg]:px-3",
        sm: "h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5",
        lg: "h-10 rounded-md px-6 has-[>svg]:px-4",
        icon: "size-9",
        xs: "h-7 rounded-md gap-1 px-2 text-xs has-[>svg]:px-1.5",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : "button"

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }