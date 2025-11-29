// Optional: components/ThemeBackground.tsx
// This is an alternative approach if you want more React control over themes

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';

interface ThemeBackgroundProps {
  children: React.ReactNode;
  className?: string;
}

export function ThemeBackground({ children, className = '' }: ThemeBackgroundProps) {
  const { theme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Prevent hydration mismatch
  if (!mounted) {
    return (
      <div className={`min-h-screen theme-background ${className}`}>
        {children}
      </div>
    );
  }

  const getBackgroundStyle = () => {
    const currentTheme = theme === 'system' ? resolvedTheme : theme;
    
    switch (currentTheme) {
      case 'light':
        return {
          background: '#ffffff',
          backgroundAttachment: 'initial' as const,
        };
      case 'dark':
        return {
          background: '#030712',
          backgroundAttachment: 'initial' as const,
        };
      case 'writerzroom':
      default:
        return {
          background: 'linear-gradient(135deg, #1a1a2e 0%, #533a7d 50%, #0f3460 100%)',
          backgroundAttachment: 'fixed' as const,
        };
    }
  };

  return (
    <div 
      className={`min-h-screen transition-all duration-300 ${className}`}
      style={getBackgroundStyle()}
    >
      {children}
    </div>
  );
}

// Usage example (if you want to use this instead of CSS classes):
// Replace <main className="min-h-screen theme-background"> with:
// <ThemeBackground><main className="min-h-screen">{children}</main></ThemeBackground>