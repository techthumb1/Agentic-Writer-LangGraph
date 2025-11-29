// lib/app-config.ts - Updated for WriterzRoom
export const APP_CONFIG = {
  name: 'WriterzRoom',
  description: 'AI-powered content generation and publishing platform where intelligent agents become your personal writing team',
  url: process.env.NEXT_PUBLIC_APP_URL || 'https://writerzroom.com',
  domain: 'writerzroom.com',
  
  // Branding
  tagline: 'Where AI agents become your personal writing team',
  shortDescription: 'Professional content creation with AI assistance',
  
  // SEO
  keywords: [
    'AI writing',
    'content generation', 
    'writing assistant',
    'publishing platform',
    'automated content',
    'AI agents',
    'content creation',
    'writing automation'
  ],
  
  // Social Media
  social: {
    twitter: '@writerzroom',
    github: 'writerzroom',
    linkedin: 'writerz-room',
  },
  
  // Contact
  contact: {
    email: 'hello@writerzroom.com',
    support: 'support@writerzroom.com',
  },
  
  // Features
  features: {
    contentGeneration: true,
    multiplatformPublishing: true,
    scheduledPublishing: true,
    contentTemplates: true,
    styleProfiles: true,
    qualityAnalysis: true,
    exportFormats: ['markdown', 'html', 'pdf'],
    publishingPlatforms: ['substack', 'medium', 'linkedin', 'twitter', 'wordpress'],
  },
  
  // API Configuration
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api',
    backendUrl: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
    timeout: 30000,
  },
  
  // UI Configuration
  ui: {
    theme: {
      primary: '#3B82F6', // Blue
      secondary: '#8B5CF6', // Purple
      accent: '#10B981', // Green
      gradients: {
        primary: 'from-blue-600 via-purple-600 to-indigo-600',
        secondary: 'from-purple-400 to-pink-600',
        background: 'from-gray-900 via-purple-900 to-gray-900',
      }
    },
    animation: {
      duration: 200,
      easing: 'ease-in-out',
    }
  },
  
  // Content Configuration
  content: {
    maxWordCount: 10000,
    defaultTemplate: 'blog-post',
    defaultStyleProfile: 'professional',
    qualityThreshold: 70,
  },
  
  // Publishing Configuration
  publishing: {
    platforms: {
      substack: {
        name: 'Substack',
        icon: '📰',
        color: 'bg-orange-500',
        capabilities: ['draft', 'publish', 'schedule', 'newsletter']
      },
      medium: {
        name: 'Medium',
        icon: '✍️',
        color: 'bg-green-500',
        capabilities: ['draft', 'publish', 'tags', 'publications']
      },
      linkedin: {
        name: 'LinkedIn',
        icon: '💼',
        color: 'bg-blue-600',
        capabilities: ['post', 'article', 'schedule']
      },
      twitter: {
        name: 'Twitter/X',
        icon: '🐦',
        color: 'bg-black',
        capabilities: ['thread', 'single', 'schedule']
      },
      wordpress: {
        name: 'WordPress',
        icon: '📝',
        color: 'bg-blue-500',
        capabilities: ['draft', 'publish', 'schedule', 'categories']
      }
    }
  }
} as const;

// Type definitions for better TypeScript support
export type AppConfig = typeof APP_CONFIG;
export type PublishingPlatform = keyof typeof APP_CONFIG.publishing.platforms;
export type ExportFormat = typeof APP_CONFIG.features.exportFormats[number];

// Helper functions
export const getAppName = () => APP_CONFIG.name;
export const getAppDescription = () => APP_CONFIG.description;
export const getAppUrl = () => APP_CONFIG.url;

export const getPlatformConfig = (platform: PublishingPlatform) => {
  return APP_CONFIG.publishing.platforms[platform];
};

export const isFeatureEnabled = (feature: keyof typeof APP_CONFIG.features) => {
  return APP_CONFIG.features[feature] === true;
};

// Environment-specific configurations
export const isDevelopment = process.env.NODE_ENV === 'development';
export const isProduction = process.env.NODE_ENV === 'production';

// Default export for convenience
export default APP_CONFIG;