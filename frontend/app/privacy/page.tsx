// File: frontend/app/privacy/page.tsx
// Enhanced Privacy Policy page for AI Content Studio (Professional - No Emojis)

import { Metadata } from 'next';
import Link from 'next/link';
import { 
  Lock, 
  Database, 
  Key, 
  Search, 
  Building, 
  AlertTriangle, 
  Shield, 
  Mail, 
  CheckCircle,
  XCircle 
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'Privacy Policy | AI Content Studio',
  description: 'Our commitment to protecting your privacy and data in AI content generation.',
};

export default function PrivacyPage() {
  const dataTypes = [
    {
      category: 'Account Information',
      description: 'Information you provide when creating an account',
      examples: ['Email address', 'Name', 'Company information', 'Billing details'],
      retention: '7 years after account closure',
      purpose: 'Account management and billing'
    },
    {
      category: 'Content Data',
      description: 'Content inputs and generated outputs',
      examples: ['Prompts and inputs', 'Generated content', 'Template preferences', 'Style profiles'],
      retention: '30 days (configurable up to 7 years for Enterprise)',
      purpose: 'Content generation and improvement'
    },
    {
      category: 'Usage Analytics',
      description: 'How you interact with our platform',
      examples: ['API usage patterns', 'Feature utilization', 'Performance metrics', 'Error logs'],
      retention: '2 years',
      purpose: 'Service improvement and optimization'
    },
    {
      category: 'Technical Data',
      description: 'Technical information about your usage',
      examples: ['IP addresses', 'Browser information', 'Device identifiers', 'Session data'],
      retention: '1 year',
      purpose: 'Security and fraud prevention'
    }
  ];

  const securityMeasures = [
    {
      title: 'Encryption in Transit',
      description: 'All data transmission uses TLS 1.3 encryption',
      icon: Lock
    },
    {
      title: 'Encryption at Rest',
      description: 'AES-256 encryption for all stored data',
      icon: Database
    },
    {
      title: 'Access Controls',
      description: 'Role-based access with multi-factor authentication',
      icon: Key
    },
    {
      title: 'Regular Audits',
      description: 'SOC 2 Type II compliance and regular security assessments',
      icon: Search
    },
    {
      title: 'Data Isolation',
      description: 'Customer data is logically and physically isolated',
      icon: Building
    },
    {
      title: 'Incident Response',
      description: '24/7 security monitoring and incident response team',
      icon: AlertTriangle
    }
  ];

  const userRights = [
    {
      right: 'Access',
      description: 'Request a copy of your personal data',
      howTo: 'Contact support or use the data export feature in your account settings'
    },
    {
      right: 'Rectification',
      description: 'Request correction of inaccurate personal data',
      howTo: 'Update information in your account settings or contact support'
    },
    {
      right: 'Erasure',
      description: 'Request deletion of your personal data',
      howTo: 'Use account deletion feature or contact support for specific data deletion'
    },
    {
      right: 'Portability',
      description: 'Receive your data in a machine-readable format',
      howTo: 'Use the data export feature in your account settings'
    },
    {
      right: 'Restriction',
      description: 'Request limitation of processing of your data',
      howTo: 'Contact support to discuss processing restrictions'
    },
    {
      right: 'Objection',
      description: 'Object to processing based on legitimate interests',
      howTo: 'Contact support to exercise your right to object'
    }
  ];

  return (
    <div className="container mx-auto px-6 py-12">
      <div className="max-w-4xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-6">
            Privacy Policy
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Your privacy is fundamental to our mission. Learn how we protect and handle your data 
            in our AI content generation platform.
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-sm">
            <span className="bg-white/10 px-4 py-2 rounded-full text-gray-300">
              Last updated: January 15, 2025
            </span>
            <span className="bg-green-500/20 text-green-400 px-4 py-2 rounded-full flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              GDPR Compliant
            </span>
            <span className="bg-blue-500/20 text-blue-400 px-4 py-2 rounded-full flex items-center gap-2">
              <Shield className="w-4 h-4" />
              SOC 2 Type II
            </span>
          </div>
        </div>

        {/* Quick Summary */}
        <section className="mb-16">
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-3xl font-bold text-white mb-6">Privacy at a Glance</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-xl font-semibold text-white mb-3">What We Collect</h3>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                    Account and billing information
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                    Content inputs and generated outputs
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                    Usage analytics and performance data
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                    Technical data for security purposes
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white mb-3">How We Protect It</h3>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                    End-to-end encryption (TLS 1.3 + AES-256)
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                    Zero-knowledge architecture for content
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                    Regular security audits and compliance
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                    Strict access controls and monitoring
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Data We Collect */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">Data We Collect</h2>
          <div className="space-y-6">
            {dataTypes.map((dataType, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-white mb-3">{dataType.category}</h3>
                <p className="text-gray-300 mb-4">{dataType.description}</p>
                
                <div className="grid md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <h4 className="font-semibold text-white mb-2">Examples</h4>
                    <ul className="space-y-1 text-gray-300">
                      {dataType.examples.map((example, exIndex) => (
                        <li key={exIndex} className="flex items-start gap-2">
                          <CheckCircle className="w-3 h-3 text-green-400 mt-0.5 flex-shrink-0" />
                          {example}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold text-white mb-2">Retention</h4>
                    <p className="text-gray-300">{dataType.retention}</p>
                  </div>
                  <div>
                    <h4 className="font-semibold text-white mb-2">Purpose</h4>
                    <p className="text-gray-300">{dataType.purpose}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* How We Use Data */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">How We Use Your Data</h2>
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold text-white mb-4">Primary Uses</h3>
                <ul className="space-y-3 text-gray-300">
                  <li className="flex items-start">
                    <CheckCircle className="w-4 h-4 text-green-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span>Provide AI content generation services</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-4 h-4 text-green-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span>Process billing and manage accounts</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-4 h-4 text-green-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span>Improve our AI models and services</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-4 h-4 text-green-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span>Provide customer support</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="w-4 h-4 text-green-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span>Ensure security and prevent fraud</span>
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white mb-4">We Never</h3>
                <ul className="space-y-3 text-gray-300">
                  <li className="flex items-start">
                    <XCircle className="w-4 h-4 text-red-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span>Sell your personal data to third parties</span>
                  </li>
                  <li className="flex items-start">
                    <XCircle className="w-4 h-4 text-red-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span>Use your content for advertising</span>
                  </li>
                  <li className="flex items-start">
                    <XCircle className="w-4 h-4 text-red-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span>Share data without your consent</span>
                  </li>
                  <li className="flex items-start">
                    <XCircle className="w-4 h-4 text-red-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span>Train models on your proprietary content</span>
                  </li>
                  <li className="flex items-start">
                    <XCircle className="w-4 h-4 text-red-400 mr-3 mt-0.5 flex-shrink-0" />
                    <span>Store content longer than necessary</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Security Measures */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">Security Measures</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {securityMeasures.map((measure, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 text-center hover:bg-white/15 transition-all duration-300">
                <measure.icon className="w-12 h-12 text-purple-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-3">{measure.title}</h3>
                <p className="text-gray-300">{measure.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* AI-Specific Privacy */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">AI-Specific Privacy Considerations</h2>
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold text-white mb-3">Content Processing</h3>
                <p className="text-gray-300 mb-4">
                  Your content inputs are processed by our AI models to generate outputs. We use a zero-knowledge 
                  architecture where possible, meaning our systems can process your content without retaining 
                  human-readable copies.
                </p>
              </div>
              
              <div>
                <h3 className="text-xl font-semibold text-white mb-3">Model Training</h3>
                <p className="text-gray-300 mb-4">
                  We may use aggregated, anonymized usage patterns to improve our models, but we never use 
                  your specific content or proprietary information for training without explicit consent.
                </p>
              </div>
              
              <div>
                <h3 className="text-xl font-semibold text-white mb-3">Third-Party AI Services</h3>
                <p className="text-gray-300 mb-4">
                  When using third-party AI services, we ensure they meet our privacy standards and have 
                  appropriate data processing agreements in place. Enterprise customers can opt for 
                  on-premises or private cloud deployments.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Your Rights */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">Your Rights</h2>
          <div className="space-y-4">
            {userRights.map((right, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6">
                <div className="flex flex-col md:flex-row md:items-start gap-4">
                  <div className="md:w-1/3">
                    <h3 className="text-xl font-semibold text-white mb-2">Right to {right.right}</h3>
                    <p className="text-gray-300">{right.description}</p>
                  </div>
                  <div className="md:w-2/3">
                    <h4 className="font-semibold text-white mb-2">How to Exercise This Right</h4>
                    <p className="text-gray-300">{right.howTo}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Contact Information */}
        <section className="mb-16">
          <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-3xl font-bold text-white mb-6">Questions About Privacy?</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-xl font-semibold text-white mb-3">Data Protection Officer</h3>
                <div className="flex items-center gap-2 text-gray-300 mb-2">
                  <Mail className="w-4 h-4" />
                  <span>privacy@aicontentstudio.com</span>
                </div>
                <p className="text-gray-300">Response time: Within 72 hours</p>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white mb-3">General Privacy Inquiries</h3>
                <div className="flex items-center gap-2 text-gray-300 mb-2">
                  <Mail className="w-4 h-4" />
                  <span>support@aicontentstudio.com</span>
                </div>
                <p className="text-gray-300">Response time: Within 24 hours</p>
              </div>
            </div>
            <div className="mt-6 flex flex-col sm:flex-row gap-4">
              <Link href="/contact" className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-6 py-3 rounded-lg transition-all duration-300 text-center">
                Contact Privacy Team
              </Link>
              <Link href="/docs/privacy" className="border border-white/30 text-white hover:bg-white/10 font-semibold px-6 py-3 rounded-lg transition-all duration-300 text-center">
                Privacy Documentation
              </Link>
            </div>
          </div>
        </section>

        {/* Version History */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8">Policy Updates</h2>
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6">
            <div className="space-y-4">
              <div className="flex justify-between items-center border-b border-white/20 pb-4">
                <div>
                  <h3 className="text-white font-semibold">Version 3.0</h3>
                  <p className="text-gray-300 text-sm">Enhanced AI-specific privacy provisions</p>
                </div>
                <span className="text-gray-400 text-sm">January 15, 2025</span>
              </div>
              <div className="flex justify-between items-center border-b border-white/20 pb-4">
                <div>
                  <h3 className="text-white font-semibold">Version 2.1</h3>
                  <p className="text-gray-300 text-sm">Updated data retention policies</p>
                </div>
                <span className="text-gray-400 text-sm">September 20, 2024</span>
              </div>
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-white font-semibold">Version 2.0</h3>
                  <p className="text-gray-300 text-sm">GDPR compliance and user rights expansion</p>
                </div>
                <span className="text-gray-400 text-sm">May 25, 2024</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}