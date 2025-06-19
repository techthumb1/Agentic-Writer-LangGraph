// frontend/components/ui/toaster.tsx (Custom implementation)
"use client"

import { useToast } from "@/hooks/use-toast"
import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastTitle,
  ToastViewport,
  ToastIcon,
} from "@/components/ui/toast"
import { AnimatePresence, motion } from "framer-motion"

export function Toaster() {
  const { toasts, dismiss } = useToast()

  return (
    <ToastViewport>
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => {
          const { id, title, description, action, variant, ...props } = toast
          
          return (
            <motion.div
              key={id}
              layout
              initial={{ opacity: 0, y: 50, scale: 0.3 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.5, transition: { duration: 0.2 } }}
              whileHover={{ scale: 1.02 }}
              className="relative"
            >
              <Toast variant={variant} {...props}>
                <div className="flex items-start space-x-3 flex-1">
                  <div className="flex-shrink-0 mt-0.5">
                    <ToastIcon variant={variant} />
                  </div>
                  <div className="flex-1 grid gap-1">
                    {title && <ToastTitle>{title}</ToastTitle>}
                    {description && (
                      <ToastDescription>{description}</ToastDescription>
                    )}
                  </div>
                </div>
                {action}
                <ToastClose onClose={() => dismiss(id)} />
              </Toast>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </ToastViewport>
  )
}