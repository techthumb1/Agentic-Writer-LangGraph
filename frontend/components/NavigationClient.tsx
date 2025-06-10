// frontend/components/NavigationClient.tsx
"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";

const navigationItems = [
  { href: "/generate", label: "Generate Content" },
  { href: "/content", label: "My Content" },
  { href: "/templates", label: "Templates" },
  { href: "/settings", label: "Settings" },
];

export function NavigationClient() {
  const pathname = usePathname();

  return (
    <div className="space-x-4">
      {navigationItems.map(({ href, label }) => {
        const isActive = pathname === href;
        
        return (
          <Link key={href} href={href} passHref>
            <Button
              variant={isActive ? "default" : "ghost"}
              className={`
                transition-all duration-200 ease-in-out
                ${isActive 
                  ? "bg-purple-600 text-white hover:bg-purple-700 shadow-lg transform scale-105" 
                  : "text-white hover:bg-gray-700 hover:text-purple-300"
                }
              `}
            >
              {label}
            </Button>
          </Link>
        );
      })}
    </div>
  );
}