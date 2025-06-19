// frontend/components/ResponsiveNavigation.tsx
"use client";

import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { Menu, X } from "lucide-react";

const navigationItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/generate", label: "Generate Content" },
  { href: "/content", label: "My Content" },
  { href: "/templates", label: "Templates" },
  { href: "/settings", label: "Settings" },
];

export function ResponsiveNavigation() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();

  // Close mobile menu when route changes
  useEffect(() => {
    setIsOpen(false);
  }, [pathname]);

  // Close mobile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (isOpen && !(event.target as Element).closest('.mobile-menu-container')) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  return (
    <div className="lg:hidden mobile-menu-container">
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center justify-center p-2 rounded-md text-gray-300 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-purple-500 transition-colors duration-200"
        aria-expanded="false"
      >
        <span className="sr-only">Open main menu</span>
        {isOpen ? (
          <X className="block h-6 w-6" aria-hidden="true" />
        ) : (
          <Menu className="block h-6 w-6" aria-hidden="true" />
        )}
      </button>

      {/* Mobile menu panel */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Menu panel */}
          <div className="absolute top-full right-0 mt-2 w-56 bg-gray-800 rounded-md shadow-lg border border-gray-700 z-50 lg:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navigationItems.map(({ href, label }) => {
                const isActive = pathname === href;
                
                return (
                  <Link
                    key={href}
                    href={href}
                    className={`
                      block px-3 py-2 rounded-md text-sm font-medium transition-all duration-200
                      ${isActive 
                        ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg" 
                        : "text-gray-300 hover:text-white hover:bg-gray-700"
                      }
                    `}
                    onClick={() => setIsOpen(false)}
                  >
                    {label}
                  </Link>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}