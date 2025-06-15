//import type { NextConfig } from "next";
//
//const nextConfig: NextConfig = {
//  /* config options here */
//};
//
//export default nextConfig;
//

/** @type {import('next').NextConfig} */
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Temporarily suppress accessibility warnings
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  // Add this to see which components are causing warnings
  experimental: {
    logging: {
      level: 'verbose',
    },
  },
  // Add webpack config to show more detailed warnings
  webpack: (config: import('webpack').Configuration, { dev }: { dev: boolean }) => {
    if (dev) {
      config.infrastructureLogging = {
        level: 'warn',
      };
    }
    return config;
  },
}

module.exports = nextConfig


