import { Metadata } from 'next'
import Link from 'next/link'
import Navigation from '@/components/shared/Navigation'
import Footer from '@/components/shared/Footer'
import BreadcrumbSchema from '@/components/shared/BreadcrumbSchema'

export const metadata: Metadata = {
  title: 'Nonprofit Grant Finder | Find Grants for Your Organization',
  description: 'Discover foundations already funding work like yours. Our AI-powered grant finder analyzes 8.3M+ grants from 143,000+ foundations to match your nonprofit with relevant funding opportunities.',
  keywords: 'nonprofit grant finder, find grants for nonprofits, grant search, foundation grants, grant opportunities, grant database, nonprofit funding',
  alternates: {
    canonical: 'https://thegrantscout.com/grant-finder',
  },
  openGraph: {
    title: 'Nonprofit Grant Finder | Find Grants for Your Organization',
    description: 'Discover foundations already funding work like yours. AI-powered grant matching from 143,000+ foundations.',
    url: 'https://thegrantscout.com/grant-finder',
  },
}

export default function GrantFinderPage() {
  const breadcrumbItems = [
    { name: 'Home', url: 'https://thegrantscout.com' },
    { name: 'Grant Finder', url: 'https://thegrantscout.com/grant-finder' },
  ]

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'What is a nonprofit grant finder?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'A nonprofit grant finder is a tool or service that helps organizations identify and discover grant opportunities from foundations, government agencies, and other funders. TheGrantScout uses AI to analyze IRS 990-PF filings to match nonprofits with foundations that have historically funded similar work.',
        },
      },
      {
        '@type': 'Question',
        name: 'How do I find grants for my nonprofit?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'To find grants for your nonprofit: 1) Define your mission and programs clearly, 2) Identify your geographic focus and target populations, 3) Use a grant finder service like TheGrantScout that analyzes foundation giving patterns, 4) Review the match results to identify foundations whose giving history aligns with your work.',
        },
      },
      {
        '@type': 'Question',
        name: 'Is TheGrantScout grant finder free?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'TheGrantScout offers founding member pricing starting at $83/month (annual) or $99/month (monthly). This includes monthly curated reports with foundation matches, funder profiles, and positioning strategies. You can see a sample report before subscribing.',
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
                <li className="text-accent">Grant Finder</li>
              </ol>
            </nav>

            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
              Nonprofit Grant Finder: <span className="text-accent">Discover Foundations Funding Your Work</span>
            </h1>
            <p className="text-lg md:text-xl text-gray-200 mb-8 max-w-3xl mx-auto">
              Stop searching through thousands of foundations manually. Our AI-powered grant finder analyzes 8.3M+ grants to match your nonprofit with funders who are already supporting work like yours.
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

      {/* How Our Grant Finder Works */}
      <section className="py-16 md:py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <span className="inline-block px-3 py-1 bg-accent/10 text-accent-dark rounded-full text-xs font-semibold mb-3">HOW IT WORKS</span>
          <h2 className="heading-2">How Our Grant Finder Works</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            We do the research for you, so you can focus on your mission.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-accent">1</span>
            </div>
            <h3 className="text-xl font-semibold text-primary mb-3">Share Your Mission</h3>
            <p className="text-gray-600">Tell us about your organization, programs, geographic focus, and the populations you serve.</p>
          </div>
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-accent">2</span>
            </div>
            <h3 className="text-xl font-semibold text-primary mb-3">AI Analyzes 8.3M+ Grants</h3>
            <p className="text-gray-600">Our algorithm scans IRS 990-PF filings to find foundations with a track record of funding similar work.</p>
          </div>
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-accent">3</span>
            </div>
            <h3 className="text-xl font-semibold text-primary mb-3">Get Matched Results</h3>
            <p className="text-gray-600">Receive a monthly report with curated foundation matches, giving history, and positioning strategies.</p>
          </div>
        </div>
      </section>

      {/* What Makes Our Grant Matching Different */}
      <section className="py-16 md:py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <span className="inline-block px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-semibold mb-3">OUR DIFFERENCE</span>
            <h2 className="heading-2">What Makes Our Grant Matching Different</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-white rounded-xl p-6 shadow-md">
              <h3 className="text-lg font-semibold text-primary mb-3">Grant Databases</h3>
              <p className="text-gray-600 mb-4">Traditional databases give you access to data. You still have to search, filter, and research each foundation yourself.</p>
              <p className="text-sm text-gray-500">Examples: Candid, Foundation Directory Online</p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-md border-2 border-accent">
              <div className="flex items-center gap-2 mb-3">
                <h3 className="text-lg font-semibold text-primary">TheGrantScout</h3>
                <span className="text-xs bg-accent/20 text-accent-dark px-2 py-0.5 rounded-full">Our Approach</span>
              </div>
              <p className="text-gray-600 mb-4">We do the research FOR you. You get a curated list of foundations matched to your specific mission, plus intelligence on how to approach each one.</p>
              <p className="text-sm text-accent-dark font-medium">Research done. Strategy included.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Foundation Database Stats */}
      <section className="py-16 md:py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <span className="inline-block px-3 py-1 bg-accent/10 text-accent-dark rounded-full text-xs font-semibold mb-3">OUR DATABASE</span>
          <h2 className="heading-2">Foundation Database Stats</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Built on official IRS data, updated as new filings are released.
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
          <div className="text-center p-6 bg-gray-50 rounded-xl">
            <div className="text-3xl md:text-4xl font-bold text-primary mb-2">143K+</div>
            <div className="text-gray-600">Foundations</div>
          </div>
          <div className="text-center p-6 bg-gray-50 rounded-xl">
            <div className="text-3xl md:text-4xl font-bold text-primary mb-2">8.3M+</div>
            <div className="text-gray-600">Historical Grants</div>
          </div>
          <div className="text-center p-6 bg-gray-50 rounded-xl">
            <div className="text-3xl md:text-4xl font-bold text-primary mb-2">8</div>
            <div className="text-gray-600">Years of Data</div>
          </div>
          <div className="text-center p-6 bg-gray-50 rounded-xl">
            <div className="text-3xl md:text-4xl font-bold text-primary mb-2">IRS</div>
            <div className="text-gray-600">Verified Source</div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16 md:py-20 bg-gray-50">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="heading-2">Grant Finder FAQ</h2>
          </div>

          <div className="space-y-6">
            <div className="bg-white rounded-xl p-6 shadow-md">
              <h3 className="text-lg font-semibold text-primary mb-2">What is a nonprofit grant finder?</h3>
              <p className="text-gray-600">A nonprofit grant finder is a tool or service that helps organizations identify and discover grant opportunities from foundations, government agencies, and other funders. TheGrantScout uses AI to analyze IRS 990-PF filings to match nonprofits with foundations that have historically funded similar work.</p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-md">
              <h3 className="text-lg font-semibold text-primary mb-2">How do I find grants for my nonprofit?</h3>
              <p className="text-gray-600">To find grants for your nonprofit: 1) Define your mission and programs clearly, 2) Identify your geographic focus and target populations, 3) Use a grant finder service like TheGrantScout that analyzes foundation giving patterns, 4) Review the match results to identify foundations whose giving history aligns with your work.</p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-md">
              <h3 className="text-lg font-semibold text-primary mb-2">Is TheGrantScout grant finder free?</h3>
              <p className="text-gray-600">TheGrantScout offers founding member pricing starting at $83/month (annual) or $99/month (monthly). This includes monthly curated reports with foundation matches, funder profiles, and positioning strategies. You can see a sample report before subscribing.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 md:py-20 bg-gradient-to-br from-primary via-primary to-primary-dark">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Get Started with Grant Finding
            </h2>
            <p className="text-lg text-gray-200 mb-8">
              Join as a Founding Member and receive your first curated report within 48 hours.
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
