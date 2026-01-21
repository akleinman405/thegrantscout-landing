import { Metadata } from 'next'
import Link from 'next/link'
import Navigation from '@/components/shared/Navigation'
import Footer from '@/components/shared/Footer'
import BreadcrumbSchema from '@/components/shared/BreadcrumbSchema'

export const metadata: Metadata = {
  title: 'New York Foundation Grants | Find NY Nonprofit Funding',
  description: 'Discover foundation grants for New York nonprofits. Our database includes 18,000+ New York-based foundations and tracks their giving patterns to help you find funding.',
  keywords: 'New York foundation grants, New York nonprofit funding, NY foundation grants, foundations in New York, New York grant opportunities, NYC foundations, Manhattan foundations',
  alternates: {
    canonical: 'https://thegrantscout.com/grants/new-york',
  },
  openGraph: {
    title: 'New York Foundation Grants | Find NY Nonprofit Funding',
    description: 'Discover foundation grants for New York nonprofits from 18,000+ NY-based foundations.',
    url: 'https://thegrantscout.com/grants/new-york',
  },
}

export default function NewYorkGrantsPage() {
  const breadcrumbItems = [
    { name: 'Home', url: 'https://thegrantscout.com' },
    { name: 'Grants', url: 'https://thegrantscout.com/grants' },
    { name: 'New York', url: 'https://thegrantscout.com/grants/new-york' },
  ]

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'How many foundations are based in New York?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'New York has over 18,000 private foundations, making it the second-largest state for philanthropy in the United States. Major foundations include the Ford Foundation, the Rockefeller Foundation, and the Carnegie Corporation, along with thousands of family foundations.',
        },
      },
      {
        '@type': 'Question',
        name: 'What types of causes do New York foundations fund?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'New York foundations fund a wide range of causes including education, arts and culture, social justice, healthcare, and international development. Many focus specifically on New York City and surrounding areas, while others have national or global reach.',
        },
      },
      {
        '@type': 'Question',
        name: 'How can I find New York foundations that fund my type of work?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'TheGrantScout analyzes IRS 990-PF filings to identify New York foundations with giving patterns that match your nonprofit\'s mission, geography, and programs. Our AI-powered matching helps you discover foundations you might not find through manual research.',
        },
      },
    ],
  }

  const topFoundations = [
    { name: 'Ford Foundation', focus: 'Social Justice, Democracy, Economic Opportunity', location: 'New York City' },
    { name: 'Rockefeller Foundation', focus: 'Health, Food, Power, Economic Opportunity', location: 'New York City' },
    { name: 'Carnegie Corporation of New York', focus: 'Education, Democracy, International Peace', location: 'New York City' },
    { name: 'Robin Hood Foundation', focus: 'Poverty Alleviation, NYC Focus', location: 'New York City' },
    { name: 'New York Community Trust', focus: 'Community Development, NYC Region', location: 'New York City' },
    { name: 'Bloomberg Philanthropies', focus: 'Arts, Education, Environment, Health', location: 'New York City' },
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
                <li className="text-accent">New York</li>
              </ol>
            </nav>

            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
              New York Foundation Grants for <span className="text-accent">Nonprofits</span>
            </h1>
            <p className="text-lg md:text-xl text-gray-200 mb-8 max-w-3xl mx-auto">
              New York is home to some of the largest and most influential foundations in the world. Discover 18,000+ New York-based funders and find the ones most likely to support your work.
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

      {/* New York Foundation Stats */}
      <section className="py-12 md:py-16 bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            <div className="text-center p-4">
              <div className="text-3xl md:text-4xl font-bold text-primary mb-2">18K+</div>
              <div className="text-gray-600 text-sm">NY Foundations</div>
            </div>
            <div className="text-center p-4">
              <div className="text-3xl md:text-4xl font-bold text-primary mb-2">#2</div>
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

      {/* Top New York Foundations */}
      <section className="py-16 md:py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="heading-2">Notable New York Foundations</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            New York City is the philanthropic capital of the United States, home to many of the world&apos;s largest foundations.
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
          These are just a few examples. TheGrantScout analyzes 18,000+ New York foundations to find the best matches for your organization.
        </p>
      </section>

      {/* New York Giving Trends */}
      <section className="py-16 md:py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="heading-2">New York Foundation Giving Trends</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-white rounded-xl p-6 shadow-md">
              <h3 className="text-lg font-semibold text-primary mb-4">Top Funded Sectors</h3>
              <ul className="space-y-3">
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-accent rounded-full"></div>
                  <span className="text-gray-600">Arts, Culture & Humanities</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-accent rounded-full"></div>
                  <span className="text-gray-600">Education & Higher Education</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-accent rounded-full"></div>
                  <span className="text-gray-600">Social Justice & Civil Rights</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-accent rounded-full"></div>
                  <span className="text-gray-600">Health & Medical Research</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-accent rounded-full"></div>
                  <span className="text-gray-600">International Development</span>
                </li>
              </ul>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md">
              <h3 className="text-lg font-semibold text-primary mb-4">Regional Focus Areas</h3>
              <ul className="space-y-3">
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span className="text-gray-600">New York City (All 5 Boroughs)</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span className="text-gray-600">Long Island</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span className="text-gray-600">Hudson Valley</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span className="text-gray-600">Upstate New York</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span className="text-gray-600">National & International Programs</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* How TheGrantScout Helps */}
      <section className="py-16 md:py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="heading-2">Find New York Foundations That Match Your Work</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            TheGrantScout analyzes the giving patterns of New York foundations to find the best matches for your organization.
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
            <p className="text-gray-600">We analyze every grant made by New York foundations in IRS filings.</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-primary mb-2">Local Focus</h3>
            <p className="text-gray-600">Identify foundations that specifically fund in your New York region.</p>
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
              Find New York Foundations for Your Nonprofit
            </h2>
            <p className="text-lg text-gray-200 mb-8">
              Join TheGrantScout and get matched with New York foundations that fund work like yours.
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
              <Link href="/grants/texas" className="text-primary hover:text-accent transition-colors font-medium">Texas Grants</Link>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}
