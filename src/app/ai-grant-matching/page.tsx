import { Metadata } from 'next'
import Link from 'next/link'
import Navigation from '@/components/shared/Navigation'
import Footer from '@/components/shared/Footer'
import BreadcrumbSchema from '@/components/shared/BreadcrumbSchema'

export const metadata: Metadata = {
  title: 'AI Grant Matching | How Technology Transforms Grant Research',
  description: 'Learn how AI-powered grant matching works. Our technology analyzes 8.3M+ grants to identify foundations funding work like yours, saving hours of manual research.',
  keywords: 'AI grant matching, AI-powered grant research, grant matching technology, automated grant search, machine learning grants, AI for nonprofits',
  alternates: {
    canonical: 'https://thegrantscout.com/ai-grant-matching',
  },
  openGraph: {
    title: 'AI Grant Matching | How Technology Transforms Grant Research',
    description: 'Learn how AI-powered grant matching analyzes millions of grants to find foundations funding work like yours.',
    url: 'https://thegrantscout.com/ai-grant-matching',
  },
}

export default function AIGrantMatchingPage() {
  const breadcrumbItems = [
    { name: 'Home', url: 'https://thegrantscout.com' },
    { name: 'AI Grant Matching', url: 'https://thegrantscout.com/ai-grant-matching' },
  ]

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'What is AI grant matching?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'AI grant matching uses artificial intelligence and machine learning to analyze large datasets of foundation grants and identify patterns in giving behavior. Instead of manually searching through databases, AI can analyze millions of grants to find foundations whose giving history aligns with your nonprofit\'s mission, programs, and geography.',
        },
      },
      {
        '@type': 'Question',
        name: 'How does AI analyze foundation giving patterns?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'AI analyzes IRS Form 990-PF filings which document every grant a foundation makes. The algorithm examines recipient characteristics (sector, geography, size), grant amounts, and purpose descriptions to identify patterns. It then matches your nonprofit\'s profile against these patterns to find the most relevant foundations.',
        },
      },
      {
        '@type': 'Question',
        name: 'Is AI grant matching better than manual research?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'AI grant matching complements manual research by dramatically reducing the time needed to identify potential funders. While a human researcher might review dozens of foundations manually, AI can analyze patterns across millions of grants instantly. The best approach combines AI-powered discovery with human judgment for relationship building and proposal development.',
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
                <li className="text-accent">AI Grant Matching</li>
              </ol>
            </nav>

            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
              AI Grant Matching: <span className="text-accent">How Technology Transforms Grant Research</span>
            </h1>
            <p className="text-lg md:text-xl text-gray-200 mb-8 max-w-3xl mx-auto">
              Artificial intelligence is revolutionizing how nonprofits find foundation funding. Learn how AI analyzes millions of grants to connect you with the right funders.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/sample-report.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary inline-flex items-center gap-2 text-lg px-8 py-4"
              >
                See AI Matching in Action
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

      {/* What is AI Grant Matching */}
      <section className="py-16 md:py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <h2 className="heading-2 text-center mb-8">What is AI Grant Matching?</h2>
          <div className="prose prose-lg max-w-none text-gray-600">
            <p className="text-lg leading-relaxed mb-6">
              AI grant matching uses artificial intelligence and machine learning to analyze large datasets of foundation grants and identify patterns in giving behavior. Instead of manually searching through databases, AI can analyze millions of grants to find foundations whose giving history aligns with your nonprofit&apos;s mission, programs, and geography.
            </p>
            <p className="text-lg leading-relaxed mb-6">
              The technology works by examining the characteristics of past grants—recipient type, sector, geography, grant size, and purpose—to build a comprehensive picture of what each foundation funds. When you provide information about your organization, the AI compares your profile against these patterns to identify the most promising matches.
            </p>
          </div>
        </div>
      </section>

      {/* How AI Analyzes Foundation Giving Patterns */}
      <section className="py-16 md:py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="heading-2">How AI Analyzes Foundation Giving Patterns</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our AI examines multiple dimensions of foundation giving to find the best matches.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <div className="bg-white rounded-xl p-6 shadow-md">
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-primary mb-2">IRS 990-PF Data</h3>
              <p className="text-gray-600">Every foundation must report grants to the IRS. We analyze 8.3M+ grants from these official filings.</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md">
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-primary mb-2">Geographic Patterns</h3>
              <p className="text-gray-600">AI identifies foundations that focus on specific states, regions, or communities.</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md">
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-primary mb-2">Sector Analysis</h3>
              <p className="text-gray-600">Understanding which causes and sectors each foundation prefers to fund.</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md">
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-primary mb-2">Grant Size Ranges</h3>
              <p className="text-gray-600">Matching your funding needs with foundations that give at appropriate levels.</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md">
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-primary mb-2">Giving Trends</h3>
              <p className="text-gray-600">Analyzing multi-year patterns to identify growing or consistent funders.</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md">
              <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-primary mb-2">Purpose Matching</h3>
              <p className="text-gray-600">Analyzing grant descriptions to match your programs with similar funded work.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits of AI-Powered Grant Research */}
      <section className="py-16 md:py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="heading-2">Benefits of AI-Powered Grant Research</h2>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <div className="flex gap-4">
            <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-primary mb-2">Save Hours of Research Time</h3>
              <p className="text-gray-600">What takes weeks of manual research can be done in minutes with AI. Focus your time on building relationships and writing proposals.</p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-primary mb-2">Discover Hidden Opportunities</h3>
              <p className="text-gray-600">AI can surface foundations you&apos;ve never heard of but that have a strong pattern of funding work like yours.</p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-primary mb-2">Data-Driven Decisions</h3>
              <p className="text-gray-600">Make informed choices about which foundations to approach based on actual giving history, not just stated priorities.</p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-primary mb-2">Better Hit Rates</h3>
              <p className="text-gray-600">By focusing on foundations with proven giving patterns that match your profile, you improve your success rate.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Our AI Matching Methodology */}
      <section className="py-16 md:py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <span className="inline-block px-3 py-1 bg-accent/10 text-accent-dark rounded-full text-xs font-semibold mb-3">OUR METHODOLOGY</span>
            <h2 className="heading-2">Our AI Matching Methodology</h2>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl p-8 shadow-lg">
              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 bg-accent rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <span className="text-primary font-bold text-sm">1</span>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-primary mb-1">Profile Your Organization</h3>
                    <p className="text-gray-600">We gather information about your mission, programs, geography, budget, and the populations you serve.</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 bg-accent rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <span className="text-primary font-bold text-sm">2</span>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-primary mb-1">Analyze Foundation Patterns</h3>
                    <p className="text-gray-600">Our AI examines 8.3M+ grants across 143K+ foundations to understand each funder&apos;s giving behavior.</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 bg-accent rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <span className="text-primary font-bold text-sm">3</span>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-primary mb-1">Score & Rank Matches</h3>
                    <p className="text-gray-600">Foundations are scored based on how closely their giving patterns align with your organization&apos;s profile.</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 bg-accent rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <span className="text-primary font-bold text-sm">4</span>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-primary mb-1">Deliver Actionable Intelligence</h3>
                    <p className="text-gray-600">You receive a curated report with foundation profiles, giving history, and positioning strategies.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 md:py-20 bg-gradient-to-br from-primary via-primary to-primary-dark">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Start Using AI to Find Grants
            </h2>
            <p className="text-lg text-gray-200 mb-8">
              Join TheGrantScout and receive your first AI-powered grant matching report within 48 hours.
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
