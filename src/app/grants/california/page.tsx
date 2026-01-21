import { Metadata } from 'next'
import Link from 'next/link'
import Navigation from '@/components/shared/Navigation'
import Footer from '@/components/shared/Footer'
import BreadcrumbSchema from '@/components/shared/BreadcrumbSchema'

export const metadata: Metadata = {
  title: 'California Foundation Grants | Find CA Nonprofit Funding',
  description: 'Discover foundation grants for California nonprofits. Our database includes 20,000+ California-based foundations and tracks their giving patterns to help you find funding.',
  keywords: 'California foundation grants, California nonprofit funding, CA foundation grants, foundations in California, California grant opportunities, Los Angeles foundations, San Francisco foundations',
  alternates: {
    canonical: 'https://thegrantscout.com/grants/california',
  },
  openGraph: {
    title: 'California Foundation Grants | Find CA Nonprofit Funding',
    description: 'Discover foundation grants for California nonprofits from 20,000+ CA-based foundations.',
    url: 'https://thegrantscout.com/grants/california',
  },
}

export default function CaliforniaGrantsPage() {
  const breadcrumbItems = [
    { name: 'Home', url: 'https://thegrantscout.com' },
    { name: 'Grants', url: 'https://thegrantscout.com/grants' },
    { name: 'California', url: 'https://thegrantscout.com/grants/california' },
  ]

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'How many foundations are based in California?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'California has over 20,000 private foundations, making it the state with the most foundations in the United States. These range from major foundations like the William and Flora Hewlett Foundation and the David and Lucile Packard Foundation to thousands of smaller family foundations.',
        },
      },
      {
        '@type': 'Question',
        name: 'What types of causes do California foundations fund?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'California foundations fund a wide range of causes including education, healthcare, environmental conservation, arts and culture, social services, and community development. Many focus specifically on California communities, particularly in the Bay Area and Los Angeles metro regions.',
        },
      },
      {
        '@type': 'Question',
        name: 'How can I find California foundations that fund my type of work?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'TheGrantScout analyzes IRS 990-PF filings to identify California foundations with giving patterns that match your nonprofit\'s mission, geography, and programs. Our AI-powered matching helps you discover foundations you might not find through manual research.',
        },
      },
    ],
  }

  const topFoundations = [
    { name: 'William and Flora Hewlett Foundation', focus: 'Education, Environment, Global Development', location: 'Menlo Park' },
    { name: 'David and Lucile Packard Foundation', focus: 'Conservation, Science, Children', location: 'Los Altos' },
    { name: 'Gordon and Betty Moore Foundation', focus: 'Science, Environment, Bay Area', location: 'Palo Alto' },
    { name: 'California Community Foundation', focus: 'Community Development, LA Region', location: 'Los Angeles' },
    { name: 'Silicon Valley Community Foundation', focus: 'Regional Grantmaking, Tech Philanthropy', location: 'Mountain View' },
    { name: 'Weingart Foundation', focus: 'Human Services, Southern California', location: 'Los Angeles' },
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
                <li className="text-accent">California</li>
              </ol>
            </nav>

            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
              California Foundation Grants for <span className="text-accent">Nonprofits</span>
            </h1>
            <p className="text-lg md:text-xl text-gray-200 mb-8 max-w-3xl mx-auto">
              California has the most private foundations of any state. Discover 20,000+ California-based funders and find the ones most likely to support your work.
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

      {/* California Foundation Stats */}
      <section className="py-12 md:py-16 bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            <div className="text-center p-4">
              <div className="text-3xl md:text-4xl font-bold text-primary mb-2">20K+</div>
              <div className="text-gray-600 text-sm">CA Foundations</div>
            </div>
            <div className="text-center p-4">
              <div className="text-3xl md:text-4xl font-bold text-primary mb-2">#1</div>
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

      {/* Top California Foundations */}
      <section className="py-16 md:py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="heading-2">Notable California Foundations</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            California is home to some of the largest and most active foundations in the country.
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
          These are just a few examples. TheGrantScout analyzes 20,000+ California foundations to find the best matches for your organization.
        </p>
      </section>

      {/* California Giving Trends */}
      <section className="py-16 md:py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="heading-2">California Foundation Giving Trends</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-white rounded-xl p-6 shadow-md">
              <h3 className="text-lg font-semibold text-primary mb-4">Top Funded Sectors</h3>
              <ul className="space-y-3">
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-accent rounded-full"></div>
                  <span className="text-gray-600">Education & Youth Development</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-accent rounded-full"></div>
                  <span className="text-gray-600">Environment & Conservation</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-accent rounded-full"></div>
                  <span className="text-gray-600">Health & Human Services</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-accent rounded-full"></div>
                  <span className="text-gray-600">Arts & Culture</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-accent rounded-full"></div>
                  <span className="text-gray-600">Community Development</span>
                </li>
              </ul>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md">
              <h3 className="text-lg font-semibold text-primary mb-4">Regional Focus Areas</h3>
              <ul className="space-y-3">
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span className="text-gray-600">Bay Area / Silicon Valley</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span className="text-gray-600">Greater Los Angeles</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span className="text-gray-600">San Diego Region</span>
                </li>
                <li className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  <span className="text-gray-600">Central Valley</span>
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
          <h2 className="heading-2">Find California Foundations That Match Your Work</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            TheGrantScout analyzes the giving patterns of California foundations to find the best matches for your organization.
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
            <p className="text-gray-600">We analyze every grant made by California foundations in IRS filings.</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-primary mb-2">Local Focus</h3>
            <p className="text-gray-600">Identify foundations that specifically fund in your California region.</p>
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
              Find California Foundations for Your Nonprofit
            </h2>
            <p className="text-lg text-gray-200 mb-8">
              Join TheGrantScout and get matched with California foundations that fund work like yours.
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
              <Link href="/grants/texas" className="text-primary hover:text-accent transition-colors font-medium">Texas Grants</Link>
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
