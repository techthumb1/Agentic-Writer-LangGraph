#!/bin/bash

# Create Footer Routes Script for AI Content Studio
# Run this from the frontend directory: bash create_routes.sh

echo "🚀 Creating footer routes for AI Content Studio..."

# Set the base directory
BASE_DIR="app"

# Create directories and route files
create_route() {
    local route_path="$1"
    local page_title="$2"
    local page_description="$3"
    
    # Create directory
    mkdir -p "${BASE_DIR}/${route_path}"
    
    # Create page.tsx file
    cat > "${BASE_DIR}/${route_path}/page.tsx" << EOF
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: '${page_title} | AI Content Studio',
  description: '${page_description}',
};

export default function ${page_title//[^a-zA-Z]/}Page() {
  return (
    <div className="container mx-auto px-6 py-12">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">
            ${page_title}
          </h1>
          <p className="text-xl text-gray-300">
            ${page_description}
          </p>
        </div>
        
        <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
          <div className="text-center text-gray-300">
            <h2 className="text-2xl font-semibold mb-4">Coming Soon</h2>
            <p className="mb-6">
              We're working hard to bring you this feature. Check back soon for updates!
            </p>
            <div className="flex justify-center">
              <a 
                href="/"
                className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-6 py-3 rounded-lg transition-all duration-300"
              >
                Back to Home
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
EOF
    
    echo "✅ Created ${route_path}/page.tsx"
}

# Product routes
echo "📦 Creating Product routes..."
create_route "api-access" "API Access" "Access our powerful APIs to integrate AI content generation into your applications."
create_route "integrations" "Integrations" "Connect AI Content Studio with your favorite tools and platforms."

# Support routes  
echo "🆘 Creating Support routes..."
create_route "help" "Help Center" "Find answers to common questions and get support for AI Content Studio."
create_route "docs" "Documentation" "Comprehensive documentation and guides for using AI Content Studio."
create_route "contact" "Contact Support" "Get in touch with our support team for assistance."
create_route "community" "Community" "Join our community of content creators and AI enthusiasts."
create_route "status" "System Status" "Check the current status of AI Content Studio services."

# Company routes
echo "🏢 Creating Company routes..."
create_route "about" "About Us" "Learn about our mission to democratize AI-powered content creation."
create_route "careers" "Careers" "Join our team and help shape the future of AI content generation."
create_route "press" "Press Kit" "Media resources and press information for AI Content Studio."
create_route "privacy" "Privacy Policy" "How we collect, use, and protect your personal information."
create_route "terms" "Terms of Service" "Terms and conditions for using AI Content Studio."

echo ""
echo "🎉 All routes created successfully!"
echo ""
echo "📁 Created the following pages:"
echo "   📦 Product: /api-access, /integrations"
echo "   🆘 Support: /help, /docs, /contact, /community, /status" 
echo "   🏢 Company: /about, /careers, /press, /privacy, /terms"
echo ""
echo "💡 Next steps:"
echo "   1. Update the footer links in layout.tsx to use these new routes"
echo "   2. Customize the content for each page as needed"
echo "   3. Add proper metadata and SEO optimization"
echo ""
echo "✨ Happy coding!"