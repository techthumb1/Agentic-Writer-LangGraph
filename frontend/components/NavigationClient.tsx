// frontend/components/NavigationClient.tsx (Debug Version)
"use client";

import { usePathname, useRouter } from "next/navigation";
import { useState, useEffect } from "react";

const navigationItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/generate", label: "Generate Content" },
  { href: "/content", label: "My Content" },
  { href: "/templates", label: "Templates" },
  { href: "/settings", label: "Settings" },
];

export function NavigationClient() {
  const pathname = usePathname();
  const router = useRouter();
  const [clickedButton, setClickedButton] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleClick = (href: string) => {
    console.log('Button clicked:', href); // Debug log
    setClickedButton(href);
    
    // Navigate after showing feedback
    setTimeout(() => {
      router.push(href);
      setClickedButton(null);
    }, 150);
  };

  if (!isClient) {
    return null;
  }

  return (
    <div className="flex space-x-2">
      {navigationItems.map(({ href, label }) => {
        const isActive = pathname === href;
        const isClicked = clickedButton === href;
        
        return (
          <button
            key={href}
            onClick={() => handleClick(href)}
            className={`
              px-4 py-2 text-sm font-medium rounded-md transition-all duration-150 ease-in-out transform
              ${isActive 
                ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg scale-105" 
                : isClicked
                  ? "bg-purple-700 text-white scale-95 shadow-inner"
                  : "text-white hover:bg-gray-700 hover:text-purple-300 hover:scale-105"
              }
              ${isClicked ? 'ring-2 ring-purple-400 ring-opacity-50' : ''}
            `}
          >
            {isClicked && (
              <span className="inline-block w-2 h-2 bg-white rounded-full animate-pulse mr-2" />
            )}
            {label}
          </button>
        );
      })}
    </div>
  );
}