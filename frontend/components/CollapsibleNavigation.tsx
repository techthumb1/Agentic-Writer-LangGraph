'use client';

import { useState } from 'react';
import Link from 'next/link';
import { 
  Menu, 
  X, 
  Home, 
  FileText, 
  Settings, 
  User, 
  CreditCard, 
  Users,
  Lightbulb,
  Zap,
  LayoutDashboard,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { useSession } from 'next-auth/react';

interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface NavGroup {
  title: string;
  items: NavItem[];
}

export function CollapsibleNavigation() {
  const [isOpen, setIsOpen] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<string[]>(['main']);
  const { data: session } = useSession();

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const closeMenu = () => {
    setIsOpen(false);
  };

  const toggleGroup = (groupTitle: string) => {
    setExpandedGroups(prev => 
      prev.includes(groupTitle) 
        ? prev.filter(g => g !== groupTitle)
        : [...prev, groupTitle]
    );
  };

  // Define navigation groups
  const publicNavGroups: NavGroup[] = [
    {
      title: "Main",
      items: [
        { href: "/", label: "Home", icon: Home },
        { href: "/solutions", label: "Solutions", icon: Lightbulb },
        { href: "/pricing", label: "Pricing", icon: CreditCard },
        { href: "/customers", label: "Customers", icon: Users },
      ]
    }
  ];

  const authenticatedNavGroups: NavGroup[] = [
    {
      title: "Main",
      items: [
        { href: "/", label: "Home", icon: Home },
        { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
      ]
    },
    {
      title: "Content",
      items: [
        { href: "/generate", label: "Generate", icon: Zap },
        { href: "/content", label: "Content", icon: FileText },
        { href: "/templates", label: "Templates", icon: Lightbulb },
      ]
    },
    {
      title: "Product",
      items: [
        { href: "/solutions", label: "Solutions", icon: Lightbulb },
        { href: "/pricing", label: "Pricing", icon: CreditCard },
        { href: "/customers", label: "Customers", icon: Users },
      ]
    },
    {
      title: "Account",
      items: [
        { href: "/settings", label: "Settings", icon: Settings },
        { href: "/profile", label: "Profile", icon: User },
      ]
    }
  ];

  const navGroups = session?.user ? authenticatedNavGroups : publicNavGroups;

  return (
    <>
      {/* Menu Button */}
      <button
        onClick={toggleMenu}
        className="inline-flex items-center justify-center p-2 rounded-md text-gray-300 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-purple-500 transition-colors duration-200"
        aria-expanded="false"
        aria-label="Navigation menu"
      >
        <span className="sr-only">Open navigation menu</span>
        {isOpen ? (
          <X className="block h-6 w-6" aria-hidden="true" />
        ) : (
          <Menu className="block h-6 w-6" aria-hidden="true" />
        )}
      </button>

      {/* Navigation Overlay */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40 bg-black bg-opacity-50 transition-opacity duration-300"
            onClick={closeMenu}
          />
          
          {/* Menu Panel */}
          <div className="fixed inset-y-0 right-0 max-w-sm w-full bg-gray-800 shadow-xl z-50 transform transition-transform duration-300 ease-in-out overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-gray-800/90 backdrop-blur-sm sticky top-0">
              <div className="flex items-center">
                <Menu className="h-5 w-5 text-purple-400 mr-2" />
                <h2 className="text-lg font-semibold text-white">Navigation</h2>
              </div>
              <button
                onClick={closeMenu}
                className="p-2 rounded-md text-gray-300 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-colors duration-200"
                aria-label="Close menu"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            {/* Navigation Groups */}
            <nav className="px-4 py-6">
              <div className="space-y-6">
                {navGroups.map((group) => (
                  <div key={group.title}>
                    {/* Group Header */}
                    <button
                      onClick={() => toggleGroup(group.title)}
                      className="w-full flex items-center justify-between px-2 py-2 text-sm font-medium text-gray-400 hover:text-white transition-colors duration-200"
                    >
                      <span className="uppercase tracking-wider">{group.title}</span>
                      {expandedGroups.includes(group.title) ? (
                        <ChevronDown className="h-4 w-4" />
                      ) : (
                        <ChevronRight className="h-4 w-4" />
                      )}
                    </button>
                    
                    {/* Group Items */}
                    {expandedGroups.includes(group.title) && (
                      <div className="space-y-1 mt-2">
                        {group.items.map((item) => {
                          const IconComponent = item.icon;
                          return (
                            <Link
                              key={item.href}
                              href={item.href}
                              onClick={closeMenu}
                              className="flex items-center px-3 py-3 text-base font-medium text-gray-300 hover:text-white hover:bg-gray-700 rounded-lg transition-all duration-200 border-l-4 border-transparent hover:border-purple-400 group"
                            >
                              <IconComponent className="h-5 w-5 mr-3 text-gray-400 group-hover:text-purple-400 transition-colors duration-200" />
                              {item.label}
                            </Link>
                          );
                        })}
                      </div>
                    )}
                  </div>
                ))}
              </div>
              
              {/* Additional Actions */}
              {!session?.user && (
                <div className="mt-8 pt-6 border-t border-gray-700">
                  <Link
                    href="/auth/signin"
                    onClick={closeMenu}
                    className="flex items-center justify-center w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-4 py-3 rounded-lg text-base font-medium transition-all duration-200 transform hover:scale-105"
                  >
                    <User className="h-5 w-5 mr-2" />
                    Sign In
                  </Link>
                </div>
              )}
              
              {/* Quick Stats for Authenticated Users */}
              {session?.user && (
                <div className="mt-8 pt-6 border-t border-gray-700">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-purple-600/20 rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-purple-400">12</div>
                      <div className="text-xs text-gray-400">Generated</div>
                    </div>
                    <div className="bg-pink-600/20 rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-pink-400">5</div>
                      <div className="text-xs text-gray-400">Templates</div>
                    </div>
                  </div>
                </div>
              )}
            </nav>
          </div>
        </>
      )}
    </>
  );
}