// File: frontend/app/contact/page.tsx
// Enhanced Contact page for AI Content Studio (Professional - No Emojis)

import { Metadata } from 'next';
import Link from 'next/link';
import { 
  Briefcase, 
  Wrench, 
  Handshake, 
  Lock, 
  Mail, 
  Phone, 
  Clock, 
  Zap, 
  AlertTriangle, 
  MessageSquare, 
  Linkedin, 
  Github, 
  Twitter 
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'Contact Us | AI Content Studio',
  description: 'Get in touch with our team for support, sales inquiries, or partnership opportunities.',
};

export default function ContactPage() {
  const contactMethods = [
    {
      title: 'Sales & Enterprise',
      description: 'Interested in enterprise features or custom solutions?',
      icon: Briefcase,
      email: 'sales@aicontentstudio.com',
      phone: '+1 (555) 123-4567',
      hours: 'Mon-Fri, 9 AM - 6 PM PST',
      responseTime: 'Within 2 hours'
    },
    {
      title: 'Technical Support',
      description: 'Need help with APIs, integrations, or technical issues?',
      icon: Wrench,
      email: 'support@aicontentstudio.com',
      phone: '+1 (555) 234-5678',
      hours: '24/7 Support Available',
      responseTime: 'Within 1 hour'
    },
    {
      title: 'Partnerships',
      description: 'Explore integration partnerships and collaboration opportunities',
      icon: Handshake,
      email: 'partnerships@aicontentstudio.com',
      phone: '+1 (555) 345-6789',
      hours: 'Mon-Fri, 9 AM - 5 PM PST',
      responseTime: 'Within 24 hours'
    },
    {
      title: 'Privacy & Security',
      description: 'Questions about data privacy, security, or compliance?',
      icon: Lock,
      email: 'privacy@aicontentstudio.com',
      phone: '+1 (555) 456-7890',
      hours: 'Mon-Fri, 9 AM - 5 PM PST',
      responseTime: 'Within 4 hours'
    }
  ];

  const offices = [
    {
      city: 'San Francisco',
      address: '123 AI Innovation Drive\nSan Francisco, CA 94105',
      phone: '+1 (555) 123-4567',
      type: 'Headquarters'
    },
    {
      city: 'New York',
      address: '456 Tech Avenue\nNew York, NY 10001',
      phone: '+1 (555) 234-5678',
      type: 'East Coast Office'
    },
    {
      city: 'Austin',
      address: '789 Innovation Blvd\nAustin, TX 78701',
      phone: '+1 (555) 345-6789',
      type: 'Development Center'
    },
    {
      city: 'London',
      address: '321 AI Street\nLondon, UK EC1A 1BB',
      phone: '+44 20 1234 5678',
      type: 'European Operations'
    }
  ];

  const faqs = [
    {
      question: 'What is the typical response time for support requests?',
      answer: 'Our support team responds to most inquiries within 1 hour during business hours. Enterprise customers receive priority support with even faster response times.'
    },
    {
      question: 'Do you offer custom AI model development?',
      answer: 'Yes, we provide custom AI model development and fine-tuning services for enterprise customers. Contact our sales team to discuss your specific requirements.'
    },
    {
      question: 'Can I schedule a demo of the platform?',
      answer: 'Absolutely! We offer personalized demos for potential customers. Use the contact form or call our sales team to schedule a demonstration.'
    },
    {
      question: 'What compliance certifications do you have?',
      answer: 'We maintain SOC 2 Type II, GDPR compliance, and are working towards ISO 27001 certification. Contact our privacy team for detailed compliance information.'
    },
    {
      question: 'Do you offer on-premises deployment?',
      answer: 'Yes, we offer on-premises and private cloud deployment options for enterprise customers with specific security or compliance requirements.'
    }
  ];

  return (
    <div className="container mx-auto px-6 py-12">
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-6">
            Get in Touch
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Whether you need technical support, want to explore enterprise features, or have questions about our AI platform, 
            we&apos;re here to help. Reach out through any of the channels below.
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-400">
            <span className="bg-white/10 px-4 py-2 rounded-full">24/7 Support</span>
            <span className="bg-white/10 px-4 py-2 rounded-full">Enterprise Ready</span>
            <span className="bg-white/10 px-4 py-2 rounded-full">Global Presence</span>
          </div>
        </div>

        {/* Contact Methods */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">How Can We Help?</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {contactMethods.map((method, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8 hover:bg-white/15 transition-all duration-300">
                <div className="flex items-center gap-4 mb-4">
                  <method.icon className="w-8 h-8 text-purple-400" />
                  <h3 className="text-2xl font-semibold text-white">{method.title}</h3>
                </div>
                <p className="text-gray-300 mb-6">{method.description}</p>
                
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Mail className="w-4 h-4 text-purple-400" />
                    <a href={`mailto:${method.email}`} className="text-white hover:text-purple-400 transition-colors">
                      {method.email}
                    </a>
                  </div>
                  <div className="flex items-center gap-3">
                    <Phone className="w-4 h-4 text-purple-400" />
                    <a href={`tel:${method.phone}`} className="text-white hover:text-purple-400 transition-colors">
                      {method.phone}
                    </a>
                  </div>
                  <div className="flex items-center gap-3">
                    <Clock className="w-4 h-4 text-purple-400" />
                    <span className="text-gray-300">{method.hours}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Zap className="w-4 h-4 text-green-400" />
                    <span className="text-green-400 text-sm font-medium">{method.responseTime}</span>
                  </div>
                </div>
                
                <button className="w-full mt-6 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-3 rounded-lg transition-all duration-300">
                  Contact {method.title}
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* Contact Form */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Send Us a Message</h2>
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <form className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="firstName" className="block text-white font-medium mb-2">
                    First Name *
                  </label>
                  <input
                    type="text"
                    id="firstName"
                    name="firstName"
                    required
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="John"
                  />
                </div>
                <div>
                  <label htmlFor="lastName" className="block text-white font-medium mb-2">
                    Last Name *
                  </label>
                  <input
                    type="text"
                    id="lastName"
                    name="lastName"
                    required
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Doe"
                  />
                </div>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="email" className="block text-white font-medium mb-2">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    required
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="john@company.com"
                  />
                </div>
                <div>
                  <label htmlFor="company" className="block text-white font-medium mb-2">
                    Company
                  </label>
                  <input
                    type="text"
                    id="company"
                    name="company"
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Your Company"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="subject" className="block text-white font-medium mb-2">
                  Subject *
                </label>
                <select
                  id="subject"
                  name="subject"
                  required
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="">Select a subject</option>
                  <option value="sales">Sales Inquiry</option>
                  <option value="support">Technical Support</option>
                  <option value="partnership">Partnership Opportunity</option>
                  <option value="privacy">Privacy & Security</option>
                  <option value="demo">Request Demo</option>
                  <option value="other">Other</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="message" className="block text-white font-medium mb-2">
                  Message *
                </label>
                <textarea
                  id="message"
                  name="message"
                  rows={6}
                  required
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-vertical"
                  placeholder="Tell us how we can help you..."
                ></textarea>
              </div>
              
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="newsletter"
                  name="newsletter"
                  className="w-4 h-4 text-purple-500 border-white/20 rounded focus:ring-purple-500"
                />
                <label htmlFor="newsletter" className="text-gray-300">
                  I&apos;d like to receive updates about new features and AI content generation insights
                </label>
              </div>
              
              <button
                type="submit"
                className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-4 rounded-lg transition-all duration-300"
              >
                Send Message
              </button>
            </form>
          </div>
        </section>

        {/* Office Locations */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Our Global Presence</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {offices.map((office, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 text-center hover:bg-white/15 transition-all duration-300">
                <h3 className="text-xl font-semibold text-white mb-2">{office.city}</h3>
                <span className="text-sm text-purple-400 font-medium mb-4 block">{office.type}</span>
                <div className="text-gray-300 text-sm mb-4 whitespace-pre-line">
                  {office.address}
                </div>
                <a href={`tel:${office.phone}`} className="text-white hover:text-purple-400 transition-colors flex items-center justify-center gap-2">
                  <Phone className="w-4 h-4" />
                  {office.phone}
                </a>
              </div>
            ))}
          </div>
        </section>

        {/* FAQ Section */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">Frequently Asked Questions</h2>
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 hover:bg-white/15 transition-all duration-300">
                <h3 className="text-lg font-semibold text-white mb-3">{faq.question}</h3>
                <p className="text-gray-300">{faq.answer}</p>
              </div>
            ))}
          </div>
          <div className="text-center mt-8">
            <Link href="/help" className="text-purple-400 hover:text-purple-300 font-medium">
              View All FAQs →
            </Link>
          </div>
        </section>

        {/* Emergency Support */}
        <section className="mb-16">
          <div className="bg-gradient-to-r from-red-500/20 to-orange-500/20 backdrop-blur-sm border border-red-500/30 rounded-xl p-8">
            <div className="flex items-center gap-4 mb-4">
              <AlertTriangle className="w-8 h-8 text-red-400" />
              <h2 className="text-2xl font-bold text-white">Emergency Support</h2>
            </div>
            <p className="text-gray-300 mb-6">
              For critical system outages or security incidents affecting production systems, 
              contact our emergency hotline for immediate assistance.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <a 
                href="tel:+15551234567" 
                className="bg-red-500 hover:bg-red-600 text-white font-semibold px-6 py-3 rounded-lg transition-all duration-300 text-center flex items-center justify-center gap-2"
              >
                <Phone className="w-4 h-4" />
                Emergency Hotline: +1 (555) 123-4567
              </a>
              <a 
                href="mailto:emergency@aicontentstudio.com" 
                className="border border-red-500/50 text-red-400 hover:bg-red-500/10 font-semibold px-6 py-3 rounded-lg transition-all duration-300 text-center flex items-center justify-center gap-2"
              >
                <Mail className="w-4 h-4" />
                emergency@aicontentstudio.com
              </a>
            </div>
          </div>
        </section>

        {/* Social Media & Community */}
        <section className="mb-16">
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8 text-center">
            <h2 className="text-2xl font-bold text-white mb-4">Join Our Community</h2>
            <p className="text-gray-300 mb-6">
              Connect with other developers, share ideas, and get quick answers from our community.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <a href="https://discord.gg/aicontentstudio" className="bg-[#5865F2] hover:bg-[#4752C4] text-white px-6 py-3 rounded-lg font-medium transition-all duration-300 flex items-center gap-2">
                <MessageSquare className="w-4 h-4" />
                Discord Community
              </a>
              <a href="https://github.com/aicontentstudio" className="bg-gray-800 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-300 flex items-center gap-2">
                <Github className="w-4 h-4" />
                GitHub
              </a>
              <a href="https://twitter.com/aicontentstudio" className="bg-[#1DA1F2] hover:bg-[#1A91DA] text-white px-6 py-3 rounded-lg font-medium transition-all duration-300 flex items-center gap-2">
                <Twitter className="w-4 h-4" />
                Twitter
              </a>
              <a href="https://linkedin.com/company/aicontentstudio" className="bg-[#0077B5] hover:bg-[#006BA6] text-white px-6 py-3 rounded-lg font-medium transition-all duration-300 flex items-center gap-2">
                <Linkedin className="w-4 h-4" />
                LinkedIn
              </a>
            </div>
          </div>
        </section>

        {/* Response Time Promise */}
        <section>
          <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm border border-white/20 rounded-xl p-8 text-center">
            <h2 className="text-2xl font-bold text-white mb-4">Our Response Time Promise</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <Zap className="w-12 h-12 text-purple-400 mx-auto mb-2" />
                <h3 className="text-lg font-semibold text-white mb-2">Critical Issues</h3>
                <p className="text-purple-400 font-bold">&lt; 15 minutes</p>
                <p className="text-gray-300 text-sm">System outages, security incidents</p>
              </div>
              <div>
                <Wrench className="w-12 h-12 text-purple-400 mx-auto mb-2" />
                <h3 className="text-lg font-semibold text-white mb-2">Urgent Support</h3>
                <p className="text-purple-400 font-bold">&lt; 1 hour</p>
                <p className="text-gray-300 text-sm">API issues, integration problems</p>
              </div>
              <div>
                <MessageSquare className="w-12 h-12 text-purple-400 mx-auto mb-2" />
                <h3 className="text-lg font-semibold text-white mb-2">General Inquiries</h3>
                <p className="text-purple-400 font-bold">&lt; 4 hours</p>
                <p className="text-gray-300 text-sm">Questions, feature requests</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}