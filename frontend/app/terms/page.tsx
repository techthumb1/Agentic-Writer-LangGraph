// File: frontend/app/terms/page.tsx
// Enhanced Terms of Service page for AI Content Studio

import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Terms of Service | AI Content Studio',
  description: 'Terms of Service and usage agreements for AI Content Studio platform and services.',
};

export default function TermsPage() {
  const lastUpdated = 'January 15, 2025';
  const effectiveDate = 'January 15, 2025';

  return (
    <div className="container mx-auto px-6 py-12">
      <div className="max-w-4xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-6">
            Terms of Service
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Please read these terms carefully before using AI Content Studio. 
            By accessing our services, you agree to be bound by these terms.
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-sm">
            <span className="bg-white/10 px-4 py-2 rounded-full text-gray-300">
              Last updated: {lastUpdated}
            </span>
            <span className="bg-white/10 px-4 py-2 rounded-full text-gray-300">
              Effective: {effectiveDate}
            </span>
          </div>
        </div>

        {/* Quick Summary */}
        <section className="mb-16">
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-3xl font-bold text-white mb-6">Terms Summary</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-xl font-semibold text-white mb-3">What You Can Do</h3>
                <ul className="space-y-2 text-gray-300">
                  <li>• Use our AI services for content generation</li>
                  <li>• Integrate our APIs into your applications</li>
                  <li>• Create commercial content using our platform</li>
                  <li>• Share and distribute generated content</li>
                  <li>• Modify and customize generated outputs</li>
                </ul>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white mb-3">What You Cannot Do</h3>
                <ul className="space-y-2 text-gray-300">
                  <li>• Use our services for illegal activities</li>
                  <li>• Generate harmful or malicious content</li>
                  <li>• Reverse engineer our AI models</li>
                  <li>• Resell our services without permission</li>
                  <li>• Violate intellectual property rights</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Terms Content */}
        <section className="space-y-12">
          {/* 1. Acceptance of Terms */}
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">1. Acceptance of Terms</h2>
            <div className="space-y-4 text-gray-300">
              <p>
                By accessing or using AI Content Studio (&quot;the Service&quot;), you agree to be bound by these Terms of Service (&quot;Terms&quot;). 
                If you disagree with any part of these terms, you may not access the Service.
              </p>
              <p>
                These Terms apply to all visitors, users, and others who access or use the Service, including but not limited to:
              </p>
              <ul className="list-disc list-inside ml-4 space-y-2">
                <li>Individual users accessing our web platform</li>
                <li>Developers integrating our APIs</li>
                <li>Enterprise customers using our services</li>
                <li>Third-party applications utilizing our platform</li>
              </ul>
            </div>
          </div>

          {/* 2. Description of Service */}
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">2. Description of Service</h2>
            <div className="space-y-4 text-gray-300">
              <p>
                AI Content Studio is a platform that provides artificial intelligence-powered content generation services, including:
              </p>
              <ul className="list-disc list-inside ml-4 space-y-2">
                <li>Text content generation using advanced language models</li>
                <li>Multi-agent workflow orchestration via LangGraph</li>
                <li>Content styling and voice customization</li>
                <li>Template-based content creation</li>
                <li>API access for integration into third-party applications</li>
                <li>Enterprise features including team management and compliance tools</li>
              </ul>
              <p>
                We reserve the right to modify, suspend, or discontinue any aspect of the Service at any time, 
                with or without notice, though we will make reasonable efforts to provide advance notice of significant changes.
              </p>
            </div>
          </div>

          {/* 3. User Accounts and Registration */}
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">3. User Accounts and Registration</h2>
            <div className="space-y-4 text-gray-300">
              <p>
                To access certain features of the Service, you must register for an account. When you create an account, you agree to:
              </p>
              <ul className="list-disc list-inside ml-4 space-y-2">
                <li>Provide accurate, current, and complete information</li>
                <li>Maintain the security of your account credentials</li>
                <li>Accept responsibility for all activities under your account</li>
                <li>Notify us immediately of any unauthorized use</li>
                <li>Comply with all applicable laws and regulations</li>
              </ul>
              <p>
                We reserve the right to suspend or terminate accounts that violate these Terms or are used for fraudulent, 
                illegal, or harmful activities.
              </p>
            </div>
          </div>

          {/* 4. Acceptable Use Policy */}
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">4. Acceptable Use Policy</h2>
            <div className="space-y-4 text-gray-300">
              <h3 className="text-lg font-semibold text-white">Prohibited Uses</h3>
              <p>You may not use our Service to:</p>
              <ul className="list-disc list-inside ml-4 space-y-2">
                <li>Generate content that is illegal, harmful, or violates others&#39; rights</li>
                <li>Create misleading, fraudulent, or defamatory content</li>
                <li>Produce content that promotes violence, harassment, or discrimination</li>
                <li>Generate spam, malware, or other malicious content</li>
                <li>Infringe on intellectual property rights</li>
                <li>Attempt to reverse engineer or extract our AI models</li>
                <li>Exceed rate limits or abuse system resources</li>
                <li>Share account credentials or resell access without authorization</li>
              </ul>
              
              <h3 className="text-lg font-semibold text-white mt-6">Content Guidelines</h3>
              <p>All content generated through our Service must comply with:</p>
              <ul className="list-disc list-inside ml-4 space-y-2">
                <li>Applicable laws and regulations</li>
                <li>Platform-specific content policies</li>
                <li>Industry standards and best practices</li>
                <li>Third-party terms of service when applicable</li>
              </ul>
            </div>
          </div>

          {/* 5. Intellectual Property Rights */}
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">5. Intellectual Property Rights</h2>
            <div className="space-y-4 text-gray-300">
              <h3 className="text-lg font-semibold text-white">Your Content</h3>
              <p>
                You retain ownership of any content you input into our Service (&quot;Input Content&quot;) and any content 
                generated by our Service based on your inputs (&quot;Generated Content&quot;), subject to these Terms.
              </p>
              
              <h3 className="text-lg font-semibold text-white mt-6">Our Technology</h3>
              <p>
                AI Content Studio retains all rights to our technology, including:
              </p>
              <ul className="list-disc list-inside ml-4 space-y-2">
                <li>AI models and algorithms</li>
                <li>Software and platform architecture</li>
                <li>APIs and integration tools</li>
                <li>Documentation and training materials</li>
                <li>Trademarks, logos, and brand assets</li>
              </ul>
              
              <h3 className="text-lg font-semibold text-white mt-6">License to Use Generated Content</h3>
              <p>
                Subject to these Terms and your payment obligations, we grant you a worldwide, non-exclusive, 
                royalty-free license to use, modify, and distribute Generated Content for any lawful purpose.
              </p>
            </div>
          </div>

          {/* 6. Privacy and Data Protection */}
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">6. Privacy and Data Protection</h2>
            <div className="space-y-4 text-gray-300">
              <p>
                Your privacy is important to us. Our collection and use of personal information is governed by our 
                <Link href="/privacy" className="text-purple-400 hover:text-purple-300 underline">Privacy Policy</Link>, 
                which is incorporated into these Terms by reference.
              </p>
              
              <h3 className="text-lg font-semibold text-white">Data Processing</h3>
              <ul className="list-disc list-inside ml-4 space-y-2">
                <li>We process your content solely to provide our services</li>
                <li>We do not use your proprietary content to train our models without consent</li>
                <li>We implement appropriate security measures to protect your data</li>
                <li>We comply with applicable data protection laws (GDPR, CCPA, etc.)</li>
              </ul>
              
              <h3 className="text-lg font-semibold text-white mt-6">Data Retention</h3>
              <p>
                We retain your data only as long as necessary to provide our services or as required by law. 
                You may request deletion of your data at any time, subject to legal and operational requirements.
              </p>
            </div>
          </div>

          {/* 7. Payment Terms */}
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">7. Payment Terms</h2>
            <div className="space-y-4 text-gray-300">
              <h3 className="text-lg font-semibold text-white">Billing</h3>
              <ul className="list-disc list-inside ml-4 space-y-2">
                <li>Subscription fees are billed in advance on a monthly or annual basis</li>
                <li>Usage-based charges are billed monthly in arrears</li>
                <li>All fees are non-refundable unless otherwise specified</li>
                <li>Prices may change with 30 days&apos; notice</li>
              </ul>
              
              <h3 className="text-lg font-semibold text-white mt-6">Payment Methods</h3>
              <p>
                We accept major credit cards, ACH transfers, and other payment methods as specified in your account. 
                You authorize us to charge your selected payment method for all applicable fees.
              </p>
              
              <h3 className="text-lg font-semibold text-white mt-6">Late Payments</h3>
              <p>
                If payment is not received when due, we may suspend your access to the Service until payment is made. 
                Late payments may incur additional charges as permitted by law.
              </p>
            </div>
          </div>

          {/* 8. Service Availability */}
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">8. Service Availability</h2>
            <div className="space-y-4 text-gray-300">
              <p>
                We strive to maintain high availability of our Service, but we do not guarantee uninterrupted access. 
                Service may be temporarily unavailable due to:
              </p>
              <ul className="list-disc list-inside ml-4 space-y-2">
                <li>Scheduled maintenance and updates</li>
                <li>Emergency repairs or security updates</li>
                <li>Third-party service dependencies</li>
                <li>Force majeure events</li>
              </ul>
              <p>
                We will provide advance notice of scheduled maintenance when possible and work to minimize 
                service disruptions.
              </p>
            </div>
          </div>

          {/* 9. Limitation of Liability */}
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">9. Limitation of Liability</h2>
            <div className="space-y-4 text-gray-300">
              <p>
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, AI CONTENT STUDIO SHALL NOT BE LIABLE FOR ANY 
                INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO:
              </p>
              <ul className="list-disc list-inside ml-4 space-y-2">
                <li>Loss of profits, data, or business opportunities</li>
                <li>Service interruptions or delays</li>
                <li>Content accuracy or quality issues</li>
                <li>Third-party claims or actions</li>
              </ul>
              <p>
                Our total liability for any claim shall not exceed the amount paid by you for the Service 
                in the 12 months preceding the claim.
              </p>
            </div>
          </div>

          {/* 10. Termination */}
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">10. Termination</h2>
            <div className="space-y-4 text-gray-300">
              <h3 className="text-lg font-semibold text-white">Termination by You</h3>
              <p>
                You may terminate your account at any time through your account settings or by contacting us. 
                Termination will be effective at the end of your current billing period.
              </p>
              
              <h3 className="text-lg font-semibold text-white mt-6">Termination by Us</h3>
              <p>
                We may terminate or suspend your account immediately if you:
              </p>
              <ul className="list-disc list-inside ml-4 space-y-2">
                <li>Violate these Terms or our policies</li>
                <li>Fail to pay applicable fees</li>
                <li>Engage in fraudulent or illegal activities</li>
                <li>Pose a security risk to our systems or other users</li>
              </ul>
              
              <h3 className="text-lg font-semibold text-white mt-6">Effect of Termination</h3>
              <p>
                Upon termination, your access to the Service will cease, and we may delete your account data 
                in accordance with our data retention policies.
              </p>
            </div>
          </div>

          {/* 11. Changes to Terms */}
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">11. Changes to Terms</h2>
            <div className="space-y-4 text-gray-300">
              <p>
                We may update these Terms from time to time. When we make changes, we will:
              </p>
              <ul className="list-disc list-inside ml-4 space-y-2">
                <li>Update the &quot;Last Updated&quot; date at the top of this page</li>
                <li>Notify you of material changes via email or platform notifications</li>
                <li>Provide at least 30 days&#39; notice for significant changes</li>
                <li>Allow you to review changes before they take effect</li>
              </ul>
              <p>
                Your continued use of the Service after changes take effect constitutes acceptance of the new Terms.
              </p>
            </div>
          </div>

          {/* 12. Governing Law */}
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">12. Governing Law and Disputes</h2>
            <div className="space-y-4 text-gray-300">
              <p>
                These Terms are governed by the laws of the State of California, United States, without regard 
                to conflict of law principles.
              </p>
              <p>
                Any disputes arising from these Terms or your use of the Service will be resolved through 
                binding arbitration in accordance with the rules of the American Arbitration Association, 
                except that you may bring claims in small claims court if they qualify.
              </p>
            </div>
          </div>

          {/* 13. Contact Information */}
          <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">13. Contact Information</h2>
            <div className="space-y-4 text-gray-300">
              <p>
                If you have questions about these Terms, please contact us:
              </p>
              <div className="bg-black/20 rounded-lg p-4 mt-4">
                <p><strong>AI Content Studio, Inc.</strong></p>
                <p>123 AI Innovation Drive</p>
                <p>San Francisco, CA 94105</p>
                <p>Email: <a href="mailto:legal@aicontentstudio.com" className="text-purple-400 hover:text-purple-300">legal@aicontentstudio.com</a></p>
                <p>Phone: +1 (555) 123-4567</p>
              </div>
            </div>
          </div>
        </section>

        {/* Acknowledgment */}
        <section className="mt-16">
          <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm border border-white/20 rounded-xl p-8 text-center">
            <h2 className="text-2xl font-bold text-white mb-4">Agreement Acknowledgment</h2>
            <p className="text-gray-300 mb-6">
              By using AI Content Studio, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/privacy" className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-6 py-3 rounded-lg transition-all duration-300">
                📄 View Privacy Policy
              </Link>
              <Link href="/contact" className="border border-white/30 text-white hover:bg-white/10 font-semibold px-6 py-3 rounded-lg transition-all duration-300">
                💬 Contact Legal Team
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}