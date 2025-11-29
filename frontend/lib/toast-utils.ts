/* File: frontend/lib/toast-utils.ts */
import { toast } from 'sonner'

export const showToast = {
  success: (message: string, description?: string) => {
    return toast.success(message, {
      description,
      duration: 5000, // Changed from 5000 to 2.5 seconds
      closeButton: true,
    })
  },
  
  error: (message: string, description?: string) => {
    return toast.error(message, {
      description,
      duration: 5000, // Changed from 5000 to 3 seconds (slightly longer for errors)
      closeButton: true,
    })
  },
  
  info: (message: string, description?: string) => {
    return toast.info(message, {
      description,
      duration: 5000, // Changed from 5000 to 2.5 seconds
      closeButton: true,
    })
  },
  
  warning: (message: string, description?: string) => {
    return toast.warning(message, {
      description,
      duration: 5000, // Changed from 5000 to 2.5 seconds
      closeButton: true,
    })
  },

  custom: (message: string, options?: Record<string, unknown>) => {
    return toast(message, {
      closeButton: true,
      duration: 2000, // This one was already at 2 seconds
      ...options,
    })
  },

  // Programmatically dismiss a toast
  dismiss: (toastId?: string | number) => {
    if (toastId) {
      toast.dismiss(toastId)
    } else {
      toast.dismiss() // Dismiss all toasts
    }
  },

  // Dismiss all toasts
  dismissAll: () => {
    toast.dismiss()
  }
}