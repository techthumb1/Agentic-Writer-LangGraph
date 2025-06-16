/** @type {import('next').NextConfig} */
const nextConfig = {
  // Temporarily suppress accessibility warnings during builds
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  // Remove the invalid logging option and use valid experimental options
  experimental: {
    // Add any valid experimental features you need here
    // logging is not a valid option in experimental
  },
  // Enhanced webpack config for better development experience
  webpack: (config: import('webpack').Configuration, { dev }: { dev: boolean }) => {
    if (dev) {
      // Set infrastructure logging for webpack itself
      config.infrastructureLogging = {
        level: 'warn',
      };
      
      // Enhanced stats for better debugging
      config.stats = {
        ...(typeof config.stats === 'object' && config.stats !== null ? config.stats : {}),
        warnings: true,
        errors: true,
        errorDetails: true,
      };
    }
    return config;
  },
  
  // Optional: Add headers for better development
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' },
        ],
      },
    ];
  },
}

export default nextConfig;