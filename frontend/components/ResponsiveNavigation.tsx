'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Menu, X } from 'lucide-react';
import { useSession } from 'next-auth/react';

export function ResponsiveNavigation() {
  const [isOpen, setIsOpen] = useState(false);
  const { data: session } = useSession();

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const closeMenu = () => {
    setIsOpen(false);
  };

  // Define navigation items based on authentication status
  const publicNavItems = [
    { href: "/", label: "Home" },
    { href: "/solutions", label: "Solutions" },
    { href: "/pricing", label: "Pricing" },
    { href: "/customers", label: "Customers" },
  ];

  const authenticatedNavItems = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/generate", label: "Generate" },
    { href: "/content", label: "My Content" },
    { href: "/templates", label: "Templates" },
    { href: "/settings", label: "Settings" },
  ];

  const allNavItems = [...publicNavItems, ...(session?.user ? authenticatedNavItems : [])];

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={toggleMenu}
        className="inline-flex items-center justify-center p-2 rounded-md text-gray-300 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-purple-500 transition-colors duration-200"
        aria-expanded="false"
        aria-label="Main menu"
      >
        <span className="sr-only">Open main menu</span>
        {isOpen ? (
          <X className="block h-6 w-6" aria-hidden="true" />
        ) : (
          <Menu className="block h-6 w-6" aria-hidden="true" />
        )}
      </button>

      {/* Mobile Menu Overlay */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40 bg-black bg-opacity-50 transition-opacity duration-300"
            onClick={closeMenu}
          />
          
          {/* Menu Panel */}
          <div className="fixed inset-y-0 right-0 max-w-xs w-full bg-gray-800 shadow-xl z-50 transform transition-transform duration-300 ease-in-out">
            <div className="flex items-center justify-between px-4 py-4 border-b border-gray-700">
              <h2 className="text-lg font-semibold text-white">Menu</h2>
              <button
                onClick={closeMenu}
                className="p-2 rounded-md text-gray-300 hover:text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-colors duration-200"
                aria-label="Close menu"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <nav className="px-4 py-6">
              <div className="space-y-1">
                {allNavItems.map(({ href, label }) => (
                  <Link
                    key={href}
                    href={href}
                    onClick={closeMenu}
                    className="block px-3 py-3 text-base font-medium text-gray-300 hover:text-white hover:bg-gray-700 rounded-lg transition-colors duration-200 border-l-4 border-transparent hover:border-purple-400"
                  >
                    {label}
                  </Link>
                ))}
              </div>
              
              {/* Additional actions in mobile menu */}
              {!session?.user && (
                <div className="mt-6 pt-6 border-t border-gray-700">
                  <Link
                    href="/auth/signin"
                    onClick={closeMenu}
                    className="block w-full text-center bg-purple-600 hover:bg-purple-700 text-white px-4 py-3 rounded-lg text-base font-medium transition-colors duration-200"
                  >
                    Sign In
                  </Link>
                </div>
              )}
            </nav>
          </div>
        </>
      )}
    </>
  );
}