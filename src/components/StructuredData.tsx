export default function StructuredData() {
  const organizationSchema = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'TheGrantScout',
    url: 'https://thegrantscout.com',
    logo: 'https://thegrantscout.com/favicon.svg',
    description: 'AI-powered grant matching service for nonprofits. Find foundations already funding work like yours.',
    contactPoint: {
      '@type': 'ContactPoint',
      email: 'hello@thegrantscout.com',
      contactType: 'customer service',
    },
  }

  const serviceSchema = {
    '@context': 'https://schema.org',
    '@type': 'Service',
    name: 'TheGrantScout Grant Matching',
    provider: {
      '@type': 'Organization',
      name: 'TheGrantScout',
    },
    description: 'Monthly grant matching reports for nonprofits featuring curated foundation opportunities, funder profiles, and positioning strategies.',
    serviceType: 'Grant Research and Matching',
    areaServed: 'United States',
    offers: [
      {
        '@type': 'Offer',
        name: 'Monthly Plan',
        price: '99',
        priceCurrency: 'USD',
        priceSpecification: {
          '@type': 'UnitPriceSpecification',
          price: '99',
          priceCurrency: 'USD',
          billingDuration: 'P1M',
          unitText: 'month',
        },
        availability: 'https://schema.org/InStock',
      },
      {
        '@type': 'Offer',
        name: 'Annual Plan',
        price: '999',
        priceCurrency: 'USD',
        priceSpecification: {
          '@type': 'UnitPriceSpecification',
          price: '83',
          priceCurrency: 'USD',
          referenceQuantity: {
            '@type': 'QuantitativeValue',
            value: '1',
            unitCode: 'MON',
          },
          billingDuration: 'P1Y',
          unitText: 'month (billed annually)',
        },
        availability: 'https://schema.org/InStock',
        description: '$83/mo billed annually at $999 - 2 months free!',
      },
    ],
  }

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'How does TheGrantScout find relevant foundations?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'We use advanced AI to analyze IRS Form 990 filings from thousands of foundations. Our algorithm identifies patterns in their giving history and matches them with your organization\'s mission, programs, and the communities you serve.',
        },
      },
      {
        '@type': 'Question',
        name: 'How long does it take to get results?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Your first report is delivered within 48 hours of your onboarding call. After that, you\'ll receive a new report via email each month with fresh opportunities tailored to your organization.',
        },
      },
      {
        '@type': 'Question',
        name: 'What\'s included in a grant report?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Each month, you\'ll receive a PDF report via email containing curated opportunities. For each one, you get: the funder\'s giving history, typical grant ranges, geographic preferences, direct contact info, and a positioning strategy explaining how to approach them based on their funding patterns.',
        },
      },
      {
        '@type': 'Question',
        name: 'Can I cancel my subscription anytime?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Absolutely. All monthly subscriptions can be cancelled at any time. You\'ll continue to have access through the end of your billing period.',
        },
      },
    ],
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(serviceSchema) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />
    </>
  )
}
