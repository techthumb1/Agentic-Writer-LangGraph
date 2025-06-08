// frontend/app/theme-provider.tsx
"use client";

import { ThemeProvider as NextThemeProvider, ThemeProviderProps } from "next-themes";
import { ReactNode } from "react";

// Extend ThemeProviderProps to include `children`
interface Props extends ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children, ...rest }: Props) {
  return (
    <NextThemeProvider {...rest}>
      {children}
    </NextThemeProvider>
  );
}
