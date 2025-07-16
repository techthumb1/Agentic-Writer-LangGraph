// components/WriterzRoomLogo.tsx
'use client'

import React from 'react';
import { useRouter } from 'next/navigation';

interface WriterzRoomLogoProps {
  variant?: 'full' | 'icon' | 'text';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  className?: string;
  href?: string;
  showTooltip?: boolean;
}

export default function WriterzRoomLogo({ 
  variant = 'full', 
  size = 'md', 
  className = '',
  href = '/',
  showTooltip = false
}: WriterzRoomLogoProps) {
  const router = useRouter();

  const sizes = {
    xs: { icon: 'w-4 h-4', text: 'text-sm' },
    sm: { icon: 'w-6 h-6', text: 'text-base' },
    md: { icon: 'w-8 h-8', text: 'text-xl' },
    lg: { icon: 'w-10 h-10', text: 'text-2xl' },
    xl: { icon: 'w-12 h-12', text: 'text-3xl' },
    '2xl': { icon: 'w-16 h-16', text: 'text-4xl' }
  };

  const currentSize = sizes[size];

  const IconComponent = () => (
    <div 
      className={`
        bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-600 
        rounded-xl flex items-center justify-center 
        shadow-lg hover:shadow-xl transition-all duration-300
        hover:scale-105 group-hover:rotate-3
        ${currentSize.icon}
      `}
      title={showTooltip ? "WriterzRoom - AI-Powered Writing Assistant" : undefined}
    >
      <svg 
        viewBox="0 0 24 24" 
        className="w-1/2 h-1/2 text-white fill-current"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Stylized "WR" letterform */}
        <path d="M3 4h4l2 8 2-8h4l2 8 2-8h4v1l-2.5 11H16l-2-7-2 7h-3.5L6 5H3V4z" />
        <circle cx="19" cy="16" r="2" className="fill-yellow-300" />
      </svg>
    </div>
  );

  const TextComponent = () => (
    <span 
      className={`
        font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 
        bg-clip-text text-transparent dark:from-white dark:via-blue-200 dark:to-purple-200
        ${currentSize.text}
      `}
    >
      WriterzRoom
    </span>
  );

  const LogoContent = () => {
    if (variant === 'icon') {
      return <IconComponent />;
    }
    
    if (variant === 'text') {
      return <TextComponent />;
    }
    
    // variant === 'full'
    return (
      <div className="flex items-center space-x-3">
        <IconComponent />
        <TextComponent />
      </div>
    );
  };

  const logoElement = (
    <div className={`group transition-all duration-300 ${className}`}>
      <LogoContent />
    </div>
  );

  if (href) {
    return (
      <button
        onClick={() => router.push(href)}
        aria-label="WriterzRoom Home"
        className="inline-flex items-center hover:opacity-80 transition-opacity bg-transparent border-none p-0 cursor-pointer"
      >
        {logoElement}
      </button>
    );
  }

  return logoElement;
}

// Animated version for loading states
export function WriterzRoomLogoAnimated({ 
  size = 'lg',
  message = "WriterzRoom is working..."
}: {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  message?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center space-y-4">
      <div className="relative">
        <WriterzRoomLogo variant="icon" size={size} href={undefined} />
        <div className="absolute inset-0 border-4 border-blue-200 border-t-blue-600 rounded-xl animate-spin"></div>
      </div>
      <p className="text-gray-600 dark:text-gray-400 text-sm animate-pulse">
        {message}
      </p>
    </div>
  );
}

// Compact version for navigation
export function WriterzRoomNavLogo() {
  return (
    <WriterzRoomLogo 
      variant="full" 
      size="sm" 
      className="hover:scale-105 transition-transform"
      showTooltip
    />
  );
}

// Large hero version
export function WriterzRoomHeroLogo() {
  return (
    <div className="text-center">
      <WriterzRoomLogo 
        variant="icon" 
        size="2xl" 
        className="mx-auto mb-6"
        href={undefined}
      />
      <h1 className="text-5xl md:text-6xl font-bold">
        <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
          WriterzRoom
        </span>
      </h1>
      <p className="mt-4 text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
        Where creativity meets AI. Transform your ideas into compelling content 
        with professional writing assistance.
      </p>
    </div>
  );
}

// Footer version
export function WriterzRoomFooterLogo() {
  return (
    <div className="flex flex-col items-center space-y-3">
      <WriterzRoomLogo variant="full" size="md" href={undefined} />
      <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
        Professional AI-powered content creation platform
      </p>
    </div>
  );
}