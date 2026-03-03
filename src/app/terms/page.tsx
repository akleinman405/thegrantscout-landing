'use client'

import Link from 'next/link'
import { useEffect } from 'react'

export default function TermsOfService() {
  useEffect(() => {
    document.title = 'Terms of Service - TheGrantScout'
  }, [])
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed w-full bg-white/95 backdrop-blur-sm shadow-sm z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link
                href="/"
                className="text-2xl font-bold text-primary hover:text-primary-light transition-colors"
              >
                TheGrantScout
              </Link>
            </div>
            <Link
              href="/"
              className="text-charcoal hover:text-primary transition-colors font-medium"
            >
              Back to Home
            </Link>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="pt-24 pb-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl font-bold text-primary mb-8">Terms of Service</h1>
          <p className="text-gray-600 mb-8">Last updated: December 9, 2025</p>

          <div className="prose prose-lg max-w-none">
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-primary mb-4">1. Acceptance of Terms</h2>
              <p className="text-gray-700 mb-4">
                By accessing or using TheGrantScout&apos;s website and services (&quot;Services&quot;), you agree to be bound by these Terms of Service (&quot;Terms&quot;). If you do not agree to these Terms, please do not use our Services.
              </p>
              <p className="text-gray-700">
                These Terms apply to all visitors, users, and others who access or use the Services.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-primary mb-4">2. Description of Services</h2>
              <p className="text-gray-700 mb-4">
                TheGrantScout provides AI-powered grant matching services for nonprofit organizations. Our Services include:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li>Analysis of IRS Form 990 data to identify potential foundation matches</li>
                <li>Monthly reports with curated grant opportunities</li>
                <li>Foundation profiles and giving history information</li>
                <li>Positioning insights and recommendations</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-primary mb-4">3. User Accounts and Registration</h2>
              <p className="text-gray-700 mb-4">
                To use certain features of our Services, you may be required to provide information about your organization. You agree to:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li>Provide accurate, current, and complete information</li>
                <li>Maintain and promptly update your information</li>
                <li>Keep your account credentials confidential</li>
                <li>Notify us immediately of any unauthorized use of your account</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-primary mb-4">4. Subscription and Payment</h2>

              <h3 className="text-xl font-semibold text-primary mb-3">Fees</h3>
              <p className="text-gray-700 mb-4">
                Our Services are provided on a subscription basis. Current pricing is displayed on our website. We reserve the right to change our pricing with reasonable notice to existing subscribers.
              </p>

              <h3 className="text-xl font-semibold text-primary mb-3">Billing</h3>
              <p className="text-gray-700 mb-4">
                Subscription fees are billed monthly in advance. Payment is due at the time of subscription and on each monthly renewal date.
              </p>

              <h3 className="text-xl font-semibold text-primary mb-3">Cancellation</h3>
              <p className="text-gray-700 mb-4">
                You may cancel your subscription at any time. Upon cancellation, you will continue to have access to the Services through the end of your current billing period. No refunds will be provided for partial months.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-primary mb-4">5. Use Restrictions</h2>
              <p className="text-gray-700 mb-4">
                You agree not to:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li>Use the Services for any unlawful purpose</li>
                <li>Share, resell, or redistribute our reports or data to third parties</li>
                <li>Attempt to reverse engineer, decompile, or extract our algorithms</li>
                <li>Use automated systems (bots, scrapers) to access our Services</li>
                <li>Interfere with or disrupt the integrity or performance of the Services</li>
                <li>Misrepresent your organization or its eligibility for grants</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-primary mb-4">6. Intellectual Property</h2>
              <p className="text-gray-700 mb-4">
                The Services, including all content, features, and functionality, are owned by TheGrantScout and are protected by copyright, trademark, and other intellectual property laws.
              </p>
              <p className="text-gray-700">
                Your subscription grants you a limited, non-exclusive, non-transferable license to access and use the Services for your organization&apos;s internal purposes only.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-primary mb-4">7. Data and Privacy</h2>
              <p className="text-gray-700 mb-4">
                Our collection and use of your information is governed by our <Link href="/privacy" className="text-primary hover:text-accent">Privacy Policy</Link>, which is incorporated into these Terms by reference.
              </p>
              <p className="text-gray-700">
                You retain ownership of the information you provide about your organization. By using our Services, you grant us a license to use this information to provide and improve our Services.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-primary mb-4">8. Disclaimer of Warranties</h2>
              <p className="text-gray-700 mb-4">
                THE SERVICES ARE PROVIDED &quot;AS IS&quot; AND &quot;AS AVAILABLE&quot; WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED.
              </p>
              <p className="text-gray-700 mb-4">
                We do not warrant that:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li>The Services will be uninterrupted, timely, secure, or error-free</li>
                <li>The information provided will result in grant funding</li>
                <li>All foundation data will be completely accurate or up-to-date</li>
                <li>The Services will meet your specific requirements</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-primary mb-4">9. Limitation of Liability</h2>
              <p className="text-gray-700 mb-4">
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, THEGRANTSCOUT SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO LOSS OF PROFITS, DATA, OR OTHER INTANGIBLE LOSSES.
              </p>
              <p className="text-gray-700">
                Our total liability for any claims arising from these Terms or your use of the Services shall not exceed the amount you paid to us in the twelve (12) months preceding the claim.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-primary mb-4">10. Indemnification</h2>
              <p className="text-gray-700 mb-4">
                You agree to indemnify and hold harmless TheGrantScout and its officers, directors, employees, and agents from any claims, damages, losses, or expenses arising from:
              </p>
              <ul className="list-disc pl-6 text-gray-700 space-y-2">
                <li>Your use of the Services</li>
                <li>Your violation of these Terms</li>
                <li>Your violation of any third-party rights</li>
                <li>Any misrepresentation made by you</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-primary mb-4">11. Termination</h2>
              <p className="text-gray-700 mb-4">
                We may terminate or suspend your access to the Services immediately, without prior notice or liability, for any reason, including if you breach these Terms.
              </p>
              <p className="text-gray-700">
                Upon termination, your right to use the Services will immediately cease. Provisions that by their nature should survive termination shall survive, including ownership provisions, warranty disclaimers, and limitations of liability.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-primary mb-4">12. Changes to Terms</h2>
              <p className="text-gray-700 mb-4">
                We reserve the right to modify these Terms at any time. We will provide notice of significant changes by posting the new Terms on our website and updating the &quot;Last updated&quot; date.
              </p>
              <p className="text-gray-700">
                Your continued use of the Services after changes are posted constitutes your acceptance of the modified Terms.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-primary mb-4">13. Governing Law</h2>
              <p className="text-gray-700 mb-4">
                These Terms shall be governed by and construed in accordance with the laws of the State of California, without regard to its conflict of law provisions.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-primary mb-4">14. Dispute Resolution</h2>
              <p className="text-gray-700 mb-4">
                Any disputes arising from these Terms or your use of the Services shall first be attempted to be resolved through good-faith negotiation. If negotiation fails, disputes shall be resolved through binding arbitration in accordance with the rules of the American Arbitration Association.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-primary mb-4">15. Severability</h2>
              <p className="text-gray-700 mb-4">
                If any provision of these Terms is found to be unenforceable or invalid, that provision shall be limited or eliminated to the minimum extent necessary, and the remaining provisions shall remain in full force and effect.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-primary mb-4">16. Contact Information</h2>
              <p className="text-gray-700 mb-4">
                If you have any questions about these Terms, please contact us at:
              </p>
              <p className="text-gray-700">
                <strong>TheGrantScout</strong><br />
                Email: <a href="mailto:hello@thegrantscout.com" className="text-primary hover:text-accent">hello@thegrantscout.com</a>
              </p>
            </section>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-primary-dark text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-gray-400 text-sm">&copy; 2025 TheGrantScout. All rights reserved.</p>
            <div className="flex gap-6">
              <Link href="/privacy" className="text-gray-300 hover:text-accent transition-colors text-sm">Privacy Policy</Link>
              <Link href="/terms" className="text-gray-300 hover:text-accent transition-colors text-sm">Terms of Service</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
