import { Metadata } from 'next'
import Link from 'next/link'
import Navigation from '@/components/shared/Navigation'
import Footer from '@/components/shared/Footer'
import BreadcrumbSchema from '@/components/shared/BreadcrumbSchema'

export const metadata: Metadata = {
  title: 'Texas Foundation Grants | Find TX Nonprofit Funding',
  description: 'Discover foundation grants for Texas nonprofits. Our database includes 12,000+ Texas-based foundations and tracks their giving patterns to help you find funding.',
  keywords: 'Texas foundation grants, Texas nonprofit funding, TX foundation grants, foundations in Texas, Texas grant opportunities, Houston foundations, Dallas foundations, Austin foundations',
  alternates: {
    canonical: 'https://thegrantscout.com/grants/texas',
  },
  openGraph: {
    title: 'Texas Foundation Grants | Find TX Nonprofit Funding',
    description: 'Discover foundation grants for Texas nonprofits from 12,000+ TX-based foundations.',
    url: 'https://thegrantscout.com/grants/texas',
  },
}

export default function TexasGrantsPage() {
  const breadcrumbItems = [
    { name: 'Home', url: 'https://thegrantscout.com' },
    { name: 'Grants', url: 'https://thegrantscout.com/grants' },
    { name: 'Texas', url: 'https://thegrantscout.com/grants/texas' },
  ]

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'How many foundations are based in Texas?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Texas has over 12,000 private foundations, making it one of the top states for philanthropy in the United States. Major foundations include the Meadows Foundation, the Houston Endowment, and the Moody Foundation, along with thousands of family foundations.',
        },
      },
      {
        '@type': 'Question',
        name: 'What types of causes do Texas foundations fund?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Texas foundations fund a wide range of causes including education, healthcare, arts and culture, social services, and community development. Many focus specifically on Texas communities, with strong regional giving in Houston, Dallas-Fort Worth, Austin, and San Antonio.',
        },
      },
      {
        '@type': 'Question',
        name: 'How can I find Texas foundations that fund my type of work?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'TheGrantScout analyzes IRS 990-PF filings to identify Texas foundations with giving patterns that match your nonprofit\'s mission, geography, and programs. Our AI-powered matching helps you discover foundations you might not find through manual research.',
        },
      },
    ],
  }

  const topFoundations = [
    { name: 'Meadows Foundation', focus: 'Education, Arts, Health, Human Services', location: 'Dallas' },
    { name: 'Houston Endowment', focus: 'Education, Environment, Health, Houston Area', location: 'Houston' },
    { name: 'Moody Foundation', focus: 'Education, Health, Social Services', location: 'Galveston' },
    { name: 'Communities Foundation of Texas', focus: 'Community Development, North Texas', location: 'Dallas' },
    { name: 'Kronkosky Charitable Foundation', focus: 'Health, Education, San Antonio Area', location: 'San Antonio' },
    { name: 'Sid W. Richardson Foundation', focus: 'Education, Health, Human Services', location: 'Fort Worth' },
  ]

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
                <li><span className="hover:text-accent transition-colors">Grants</span></li>
                <li><span className="mx-2">/</span></li>
                <li className="text-accent">Texas</li>
              </ol>
            </nav>

            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
              Texas Foundation Grants for <span className="text-accent">Nonprofits</span>
            </h1>
            <p className="text-lg md:text-xl text-gray-200 mb-8 max-w-3xl mx-auto">
              Texas has a strong philanthropic tradition with over 12,000 private foundations. Discover Texas-based funders and find the ones most likely to support your work.
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

      {/* Texas Foundation Stats */}
      <section className="py-12 md:py-16 bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            <div className="text-center p-4">
              <div className="text-3xl md:text-4xl font-bold text-primary mb-2">12K+</div>
              <div className="text-gray-600 text-sm">TX Foundations</div>
            </div>
            <div className="text-center p-4">
              <div className="text-3xl md:text-4xl font-bold text-primary mb-2">Top 5</div>
              <div className="text-gray-600 text-sm">State by Foundation Count</div>
            </div>
            <div className="text-center p-4">
              <div className="text-3xl md:text-4xl font-bold text-primary mb-2">$Billions</div>
              <div className="text-gray-600 text-sm">Annual Giving</div>
            </div>
            <div className="text-center p-4">
              <div className="text-3xl md:text-4xl font-bold text-primary mb-2">8 Years</div>
              <div className="text-gray-600 text-sm">Of Giving Data</div>
            </div>
          </div>
        </div>
      </section>

      {/* Top Texas Foundations */}
      <section className="py-16 md:py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="heading-2">Notable Texas Foundations</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Texas is home to major foundations with deep roots in local communities.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {topFoundations.map((foundation, index) => (
            <div key={index} className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
              <h3 className="text-lg font-semibold text-primary mb-2">{foundation.name}</h3>
              <p className="text-sm text-gray-500 mb-2">{foundation.location}</p>
              <p className="text-gray-600 text-sm">{foundation.focus}</p>
            </div>
          ))}
        </div>

        <p className="text-center text-gray-500 mt-8 text-sm">
          These are just a few examples. TheGrantScout analyzes 12,000+ Texas foundations to find the best matches for your organization.
        </p>
      </section>

      {/* Texas Giving Trends */}
      <section className="py-16 md:py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="heading-2">Texas Foundation Giving Trends</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-white rounded-xl p-6 shadow-md">
              <h3 className="text-lg font-semibold text-primary mb-4">Top Funded Sectors</h3>
              <ul className="space-y-3">
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-accent rounded-full"></div>
                  <span className="text-gray-600">Education & Higher Education</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-accent rounded-full"></div>
                  <span className="text-gray-600">Healthcare & Medical Research</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-accent rounded-full"></div>
                  <span className="text-gray-600">Human Services & Social Welfare</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-accent rounded-full"></div>
                  <span className="text-gray-600">Arts, Culture & Humanities</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-accent rounded-full"></div>
                  <span className="text-gray-600">Religion & Faith-Based</span>
                </li>
              </ul>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md">
              <h3 className="text-lg font-semibold text-primary mb-4">Regional Focus Areas</h3>
              <ul className="space-y-3">
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span className="text-gray-600">Greater Houston Area</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span className="text-gray-600">Dallas-Fort Worth Metroplex</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span className="text-gray-600">Austin & Central Texas</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span className="text-gray-600">San Antonio & South Texas</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span className="text-gray-600">Statewide Programs</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* How TheGrantScout Helps */}
      <section className="py-16 md:py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="heading-2">Find Texas Foundations That Match Your Work</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            TheGrantScout analyzes the giving patterns of Texas foundations to find the best matches for your organization.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <div className="text-center">
            <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-primary mb-2">Deep Analysis</h3>
            <p className="text-gray-600">We analyze every grant made by Texas foundations in IRS filings.</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-primary mb-2">Local Focus</h3>
            <p className="text-gray-600">Identify foundations that specifically fund in your Texas region.</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-primary mb-2">Curated Matches</h3>
            <p className="text-gray-600">Receive a monthly report with foundations matched to your mission.</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 md:py-20 bg-gradient-to-br from-primary via-primary to-primary-dark">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Find Texas Foundations for Your Nonprofit
            </h2>
            <p className="text-lg text-gray-200 mb-8">
              Join TheGrantScout and get matched with Texas foundations that fund work like yours.
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

      {/* Other State Links */}
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-gray-600 mb-4">Explore grants in other states:</p>
            <div className="flex flex-wrap justify-center gap-4">
              <Link href="/grants/california" className="text-primary hover:text-accent transition-colors font-medium">California Grants</Link>
              <span className="text-gray-300">|</span>
              <Link href="/grants/new-york" className="text-primary hover:text-accent transition-colors font-medium">New York Grants</Link>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}
