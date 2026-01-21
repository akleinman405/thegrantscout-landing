import { Metadata } from 'next'
import Link from 'next/link'
import Navigation from '@/components/shared/Navigation'
import Footer from '@/components/shared/Footer'
import BreadcrumbSchema from '@/components/shared/BreadcrumbSchema'

export const metadata: Metadata = {
  title: 'Foundation Grants for Nonprofits | Complete Guide',
  description: 'Learn how to find and secure foundation grants for your nonprofit. Understand private foundations, their giving patterns, and how to identify the best funding opportunities.',
  keywords: 'foundation grants for nonprofits, private foundation grants, foundation funding, nonprofit foundation grants, foundation grant opportunities, how to get foundation grants',
  alternates: {
    canonical: 'https://thegrantscout.com/foundation-grants',
  },
  openGraph: {
    title: 'Foundation Grants for Nonprofits | Complete Guide',
    description: 'Learn how to find and secure foundation grants. Understand private foundations and how to identify funding opportunities.',
    url: 'https://thegrantscout.com/foundation-grants',
  },
}

export default function FoundationGrantsPage() {
  const breadcrumbItems = [
    { name: 'Home', url: 'https://thegrantscout.com' },
    { name: 'Foundation Grants', url: 'https://thegrantscout.com/foundation-grants' },
  ]

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'What are foundation grants?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Foundation grants are funds awarded by private foundations, family foundations, or corporate foundations to nonprofit organizations. Unlike government grants, foundation grants are funded by private wealth and typically have fewer bureaucratic requirements. Foundations are required to distribute at least 5% of their assets annually.',
        },
      },
      {
        '@type': 'Question',
        name: 'What types of private foundations exist?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'There are several types: 1) Private non-operating foundations - traditional grantmaking foundations funded by a single source, 2) Family foundations - funded and controlled by a family, 3) Corporate foundations - established by companies, 4) Operating foundations - primarily run their own charitable programs rather than making grants.',
        },
      },
      {
        '@type': 'Question',
        name: 'How do I find foundation grant opportunities?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Research IRS Form 990-PF filings to see foundation giving history, use grant databases or matching services like TheGrantScout, network with other nonprofits to learn about funders, and attend funder briefings and nonprofit conferences. Focus on foundations that have funded similar organizations.',
        },
      },
    ],
  }

  return (
    <div className="min-h-screen bg-white">
      <BreadcrumbSchema items={breadcrumbItems} />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <Navigation />

      {/* Hero Section */}
      <section className="pt-32 pb-16 md:pt-40 md:pb-20 bg-gradient-to-br from-primary via-primary to-primary-light">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            {/* Breadcrumb */}
            <nav className="mb-6" aria-label="Breadcrumb">
              <ol className="flex items-center justify-center gap-2 text-sm text-gray-300">
                <li><Link href="/" className="hover:text-accent transition-colors">Home</Link></li>
                <li><span className="mx-2">/</span></li>
                <li className="text-accent">Foundation Grants</li>
              </ol>
            </nav>

            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
              Foundation Grants for Nonprofits: <span className="text-accent">Your Complete Guide</span>
            </h1>
            <p className="text-lg md:text-xl text-gray-200 mb-8 max-w-3xl mx-auto">
              Private foundations distribute billions in grants each year. Learn how to identify the right foundations for your organization and position yourself for success.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/sample-report.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary inline-flex items-center gap-2 text-lg px-8 py-4"
              >
                See a Sample Report
              </a>
              <a
                href="https://calendly.com/alec_kleinman/meeting-with-alec"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 text-white hover:text-accent font-medium transition-colors border border-white/30 rounded-lg px-6 py-3"
              >
                Book a Call
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* What Are Foundation Grants */}
      <section className="py-16 md:py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <h2 className="heading-2 text-center mb-8">What Are Foundation Grants?</h2>
          <div className="prose prose-lg max-w-none text-gray-600">
            <p className="text-lg leading-relaxed mb-6">
              Foundation grants are funds awarded by private foundations to nonprofit organizations for charitable purposes. Unlike government grants, foundation grants come from private wealth—endowments established by individuals, families, or corporations.
            </p>
            <p className="text-lg leading-relaxed mb-6">
              Private foundations are required by law to distribute at least 5% of their assets annually for charitable purposes. This creates a steady stream of funding opportunities for nonprofits. In the United States, there are over 143,000 private foundations collectively holding hundreds of billions in assets.
            </p>
            <div className="bg-accent/10 rounded-xl p-6 my-8">
              <h3 className="text-xl font-semibold text-primary mb-3">Key Foundation Grant Statistics</h3>
              <ul className="space-y-2 text-gray-700">
                <li className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-accent mt-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>143,000+ private foundations in the US</span>
                </li>
                <li className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-accent mt-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>8.3M+ grants recorded in IRS 990-PF filings</span>
                </li>
                <li className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-accent mt-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>5% minimum payout requirement annually</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Types of Private Foundations */}
      <section className="py-16 md:py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="heading-2">Types of Private Foundations</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Understanding foundation types helps you target the right funders.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <div className="bg-white rounded-xl p-6 shadow-md">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-primary mb-3">Private Non-Operating Foundations</h3>
              <p className="text-gray-600">The most common type. These foundations primarily make grants to other organizations rather than running their own programs. Funded by an individual, family, or corporation.</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-primary mb-3">Family Foundations</h3>
              <p className="text-gray-600">Funded and governed by members of a family. Often reflect the philanthropic interests and values of the founding family. May be more accessible to smaller nonprofits.</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-primary mb-3">Corporate Foundations</h3>
              <p className="text-gray-600">Established by corporations as separate legal entities. Often fund causes aligned with company values or employee interests. May offer both grants and employee matching programs.</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-primary mb-3">Operating Foundations</h3>
              <p className="text-gray-600">Primarily conduct their own charitable activities rather than making grants. May still offer some grants, but focus is on direct program operation.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How to Find Foundation Grant Opportunities */}
      <section className="py-16 md:py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="heading-2">How to Find Foundation Grant Opportunities</h2>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className="space-y-6">
            <div className="flex gap-4 p-6 bg-white rounded-xl shadow-md">
              <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-primary font-bold">1</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-primary mb-2">Research IRS 990-PF Filings</h3>
                <p className="text-gray-600">Every private foundation must file Form 990-PF with the IRS, listing every grant they made. This public data reveals exactly who foundations fund, how much they give, and what causes they support.</p>
              </div>
            </div>

            <div className="flex gap-4 p-6 bg-white rounded-xl shadow-md">
              <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-primary font-bold">2</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-primary mb-2">Use Grant Matching Services</h3>
                <p className="text-gray-600">Services like TheGrantScout analyze millions of grants to match your nonprofit with foundations that have funded similar work. This saves countless hours of manual research.</p>
              </div>
            </div>

            <div className="flex gap-4 p-6 bg-white rounded-xl shadow-md">
              <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-primary font-bold">3</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-primary mb-2">Look for Geographic Alignment</h3>
                <p className="text-gray-600">Many foundations focus on specific regions or communities. Prioritize foundations that have a track record of giving in your area.</p>
              </div>
            </div>

            <div className="flex gap-4 p-6 bg-white rounded-xl shadow-md">
              <div className="w-10 h-10 bg-accent rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-primary font-bold">4</span>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-primary mb-2">Network with Peer Organizations</h3>
                <p className="text-gray-600">Connect with other nonprofits in your sector to learn about funders. Many foundation opportunities come through referrals and relationships.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* TheGrantScout's Foundation Database */}
      <section className="py-16 md:py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <span className="inline-block px-3 py-1 bg-accent/10 text-accent-dark rounded-full text-xs font-semibold mb-3">OUR DATABASE</span>
            <h2 className="heading-2">TheGrantScout&apos;s Foundation Database</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              We&apos;ve analyzed every foundation grant in IRS 990-PF filings to help you find the right funders.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto mb-12">
            <div className="text-center p-6 bg-white rounded-xl shadow-md">
              <div className="text-3xl font-bold text-primary mb-2">143K+</div>
              <div className="text-gray-600">Foundations</div>
            </div>
            <div className="text-center p-6 bg-white rounded-xl shadow-md">
              <div className="text-3xl font-bold text-primary mb-2">8.3M+</div>
              <div className="text-gray-600">Grants Analyzed</div>
            </div>
            <div className="text-center p-6 bg-white rounded-xl shadow-md">
              <div className="text-3xl font-bold text-primary mb-2">2016-24</div>
              <div className="text-gray-600">Data Coverage</div>
            </div>
            <div className="text-center p-6 bg-white rounded-xl shadow-md">
              <div className="text-3xl font-bold text-primary mb-2">Monthly</div>
              <div className="text-gray-600">Report Delivery</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 md:py-20 bg-gradient-to-br from-primary via-primary to-primary-dark">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Get Matched with Foundations
            </h2>
            <p className="text-lg text-gray-200 mb-8">
              Stop searching manually. Get a curated list of foundations that fund work like yours.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="https://calendly.com/alec_kleinman/meeting-with-alec"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary text-lg px-10 py-4"
              >
                Book a Call
              </a>
              <a
                href="/sample-report.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 text-white hover:text-accent font-medium transition-colors"
              >
                See a Sample Report
              </a>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}
