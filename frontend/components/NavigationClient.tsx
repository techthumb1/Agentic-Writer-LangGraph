'use client'

import React, { useState, useEffect } from 'react';
import { useTheme } from 'next-themes';
import { usePathname } from "next/navigation";
import Link from 'next/link';
import { 
  Menu, 
  X, 
  Sun, 
  Moon, 
  ChevronDown,
  Zap,
  Users,
  FileText,
  LogIn,
  UserPlus,
  LucideIcon,
  LayoutDashboard,
  Settings,
  FolderOpen
} from 'lucide-react';

interface NavigationItem {
  name: string;
  href?: string;
  dropdown?: boolean;
  items?: Array<{
    name: string;
    href: string;
    icon?: LucideIcon;
  }>;
}

interface MainNavigationItem {
  href: string;
  label: string;
  icon?: LucideIcon;
}

const NavigationClient = () => {
  const { theme, setTheme } = useTheme();
  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProductsOpen, setIsProductsOpen] = useState(false);
  const [isSolutionsOpen, setIsSolutionsOpen] = useState(false);
  const [isClient, setIsClient] = useState(false);

  // Your existing navigation items with icons
  const mainNavigationItems: MainNavigationItem[] = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/generate", label: "Generate Content", icon: FileText },
    { href: "/content", label: "My Content", icon: FolderOpen },
    { href: "/templates", label: "Templates", icon: Zap },
    { href: "/settings", label: "Settings", icon: Settings },
  ];

  // Public navigation items for dropdowns
  const publicNavigationItems: NavigationItem[] = [
    {
      name: 'Products',
      dropdown: true,
      items: [
        { name: 'Content Generator', href: '/generate', icon: FileText },
        { name: 'Template Library', href: '/templates', icon: Zap },
        { name: 'Style Profiles', href: '/profiles', icon: Users },
      ]
    },
    {
      name: 'Solutions',
      dropdown: true,
      items: [
        { name: 'Marketing Teams', href: '/solutions#marketing' },
        { name: 'Content Creators', href: '/solutions#creators' },
        { name: 'Enterprises', href: '/solutions#enterprise' },
        { name: 'Agencies', href: '/solutions#agencies' },
      ]
    },
    { name: 'Pricing', href: '/pricing' },
    { name: 'Customers', href: '/customers' },
    { name: 'Docs', href: '/docs' },
  ];

  // Ensure component is mounted before rendering theme-dependent content
  useEffect(() => {
    setMounted(true);
    setIsClient(true);
  }, []);

  // Check if user is on app pages (dashboard, generate, etc.)
  const isAppPage = mainNavigationItems.some(item => pathname === item.href);

  if (!mounted || !isClient) {
    return null; // Avoid hydration mismatch
  }

  return (
    <nav className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50 transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          {/* @ts-expect-error - React 19 + Next.js 15 Link compatibility issue */}
          <Link href="/" className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Zap className="h-6 w-6 text-white" />
              </div>
            </div>
            <div className="hidden md:block">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                WriterzRoom
              </h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Multi-Agent Content Creation
              </p>
            </div>
          </Link>

          {/* Navigation - Show different nav based on page type */}
          <div className="hidden md:flex items-center space-x-4">
            {isAppPage ? (
            /* Fixed app navigation with Link components */
            <div className="flex space-x-2">
              {mainNavigationItems.map(({ href, label, icon: Icon }) => {
                const isActive = pathname === href;

                return (
                  /* @ts-expect-error - React 19 + Next.js 15 Link compatibility issue */
                  <Link
                    key={href}
                    href={href}
                    className={`
                      flex items-center px-4 py-2 text-sm font-medium rounded-md transition-all duration-200
                      ${isActive 
                        ? "bg-primary text-primary-foreground shadow-lg" 
                        : "text-muted-foreground hover:text-foreground hover:bg-accent"
                      }
                    `}
                  >
                    {Icon && <Icon className="w-4 h-4 mr-2" />}
                    {label}
                  </Link>
                );
              })}
            </div>
            ) : (
              /* Public navigation with dropdowns */
              <div className="flex items-center space-x-8">
                {publicNavigationItems.map((item) => (
                  <div key={item.name} className="relative">
                    {item.dropdown ? (
                      <div className="relative">
                        <button
                          onClick={() => {
                            if (item.name === 'Products') {
                              setIsProductsOpen(!isProductsOpen);
                              setIsSolutionsOpen(false);
                            } else if (item.name === 'Solutions') {
                              setIsSolutionsOpen(!isSolutionsOpen);
                              setIsProductsOpen(false);
                            }
                          }}
                          className="flex items-center text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-200"
                        >
                          {item.name}
                          <ChevronDown className="ml-1 h-4 w-4" />
                        </button>
                        
                        {((item.name === 'Products' && isProductsOpen) || 
                          (item.name === 'Solutions' && isSolutionsOpen)) && (
                          <div className="absolute top-full left-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-2 z-50">
                            {item.items?.map((dropdownItem) => (
                              /* @ts-expect-error - React 19 + Next.js 15 Link compatibility issue */
                              <Link
                                key={dropdownItem.name}
                                href={dropdownItem.href}
                                className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
                                onClick={() => {
                                  setIsProductsOpen(false);
                                  setIsSolutionsOpen(false);
                                }}
                              >
                                {dropdownItem.icon && (
                                  <dropdownItem.icon className="mr-3 h-4 w-4" />
                                )}
                                {dropdownItem.name}
                              </Link>
                            ))}
                          </div>
                        )}
                      </div>
                    ) : (
                      /* @ts-expect-error - React 19 + Next.js 15 Link compatibility issue */
                      <Link
                        href={item.href || '#'}
                        className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-200"
                      >
                        {item.name}
                      </Link>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Right side buttons */}
          <div className="flex items-center space-x-4">
            {/* Dark mode toggle */}
            <button
              onClick={() => setTheme(theme === 'light' ? 'agentwrite-pro' : 'light')}
              className="p-2 rounded-lg bg-accent text-accent-foreground hover:bg-accent/80 transition-all duration-200"
              aria-label="Toggle theme"
            >
              {theme === 'light' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
            </button>

            {/* Auth buttons - only show on public pages */}
            {!isAppPage && (
              <div className="hidden md:flex items-center space-x-3">
                {/* @ts-expect-error - React 19 + Next.js 15 Link compatibility issue */}
                <Link 
                  href="/auth/signin"
                  className="flex items-center px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-200"
                >
                  <LogIn className="mr-2 h-4 w-4" />
                  Sign In
                </Link>
                {/* @ts-expect-error - React 19 + Next.js 15 Link compatibility issue */}
                <Link 
                  href="/generate"
                  className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors duration-200"
                >
                  <UserPlus className="mr-2 h-4 w-4" />
                  Get Started
                </Link>
              </div>
            )}

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-200"
            >
              {isMobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {isAppPage ? (
                /* Mobile app navigation */
                <>
                  {mainNavigationItems.map(({ href, label, icon: Icon }) => {
                    const isActive = pathname === href;
                    
                    return (
                      /* @ts-expect-error - React 19 + Next.js 15 Link compatibility issue */
                      <Link
                        key={href}
                        href={href}
                        className={`
                          flex items-center w-full px-3 py-2 text-base font-medium rounded-lg transition-colors duration-200
                          ${isActive 
                            ? "bg-primary text-primary-foreground" 
                            : "text-muted-foreground hover:text-foreground hover:bg-accent"
                          }
                        `}
                        onClick={() => setIsMobileMenuOpen(false)}
                      >
                        {Icon && <Icon className="mr-3 h-5 w-5" />}
                        {label}
                      </Link>
                    );
                  })}
                </>
              ) : (
                /* Mobile public navigation */
                <>
                  {publicNavigationItems.map((item) => (
                    <div key={item.name}>
                      {item.dropdown ? (
                        <div>
                          <button
                            onClick={() => {
                              if (item.name === 'Products') {
                                setIsProductsOpen(!isProductsOpen);
                              } else if (item.name === 'Solutions') {
                                setIsSolutionsOpen(!isSolutionsOpen);
                              }
                            }}
                            className="flex items-center justify-between w-full px-3 py-2 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors duration-200"
                          >
                            {item.name}
                            <ChevronDown className={`h-4 w-4 transform transition-transform duration-200 ${
                              (item.name === 'Products' && isProductsOpen) || 
                              (item.name === 'Solutions' && isSolutionsOpen) ? 'rotate-180' : ''
                            }`} />
                          </button>
                          
                          {((item.name === 'Products' && isProductsOpen) || 
                            (item.name === 'Solutions' && isSolutionsOpen)) && (
                            <div className="pl-6 mt-1 space-y-1">
                              {item.items?.map((dropdownItem) => (
                                /* @ts-expect-error - React 19 + Next.js 15 Link compatibility issue */
                                <Link
                                  key={dropdownItem.name}
                                  href={dropdownItem.href}
                                  className="flex items-center px-3 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors duration-200"
                                  onClick={() => setIsMobileMenuOpen(false)}
                                >
                                  {dropdownItem.icon && (
                                    <dropdownItem.icon className="mr-3 h-4 w-4" />
                                  )}
                                  {dropdownItem.name}
                                </Link>
                              ))}
                            </div>
                          )}
                        </div>
                      ) : (
                        /* @ts-expect-error - React 19 + Next.js 15 Link compatibility issue */
                        <Link
                          href={item.href || '#'}
                          className="block px-3 py-2 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors duration-200"
                          onClick={() => setIsMobileMenuOpen(false)}
                        >
                          {item.name}
                        </Link>
                      )}
                    </div>
                  ))}
                  
                  {/* Mobile auth buttons for public pages */}
                  <div className="pt-4 mt-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
                    {/* @ts-expect-error - React 19 + Next.js 15 Link compatibility issue */}
                    <Link 
                      href="/auth/signin"
                      className="flex items-center w-full px-3 py-2 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors duration-200"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      <LogIn className="mr-3 h-5 w-5" />
                      Sign In
                    </Link>
                    {/* @ts-expect-error - React 19 + Next.js 15 Link compatibility issue */}
                    <Link 
                      href="/generate"
                      className="flex items-center w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-base font-medium rounded-lg transition-colors duration-200"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      <UserPlus className="mr-3 h-5 w-5" />
                      Get Started
                    </Link>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Click outside to close dropdowns */}
      {(isProductsOpen || isSolutionsOpen) && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => {
            setIsProductsOpen(false);
            setIsSolutionsOpen(false);
          }}
        />
      )}
    </nav>
  );
};

export default NavigationClient;