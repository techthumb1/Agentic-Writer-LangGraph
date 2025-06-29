/* File: frontend/lib/toast-utils.ts */
import { toast } from 'sonner'

export const showToast = {
  success: (message: string, description?: string) => {
    return toast.success(message, {
      description,
      duration: 4000,
      closeButton: true,
    })
  },
  
  error: (message: string, description?: string) => {
    return toast.error(message, {
      description,
      duration: 4000,
      closeButton: true,
    })
  },
  
  info: (message: string, description?: string) => {
    return toast.info(message, {
      description,
      duration: 4000,
      closeButton: true,
    })
  },
  
  warning: (message: string, description?: string) => {
    return toast.warning(message, {
      description,
      duration: 3000,
      closeButton: true,
    })
  },

  custom: (message: string, options?: Record<string, unknown>) => {
    return toast(message, {
      closeButton: true,
      duration: 2000,
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