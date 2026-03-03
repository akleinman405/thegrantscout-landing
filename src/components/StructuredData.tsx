export default function StructuredData() {
  const websiteSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'TheGrantScout',
    alternateName: ['The Grant Scout', 'GrantScout', 'Grant Scout'],
    url: 'https://thegrantscout.com',
    description: 'AI-powered grant matching service for nonprofits. Find foundations already funding work like yours.',
  }

  const organizationSchema = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'TheGrantScout',
    alternateName: ['The Grant Scout', 'GrantScout', 'Grant Scout'],
    url: 'https://thegrantscout.com',
    logo: 'https://thegrantscout.com/favicon.svg',
    description: 'AI-powered grant matching service for nonprofits. Find foundations already funding work like yours.',
    foundingDate: '2024',
    slogan: 'Your mission deserves funding. We help you find it.',
    sameAs: [
      'https://www.linkedin.com/company/thegrantscout',
    ],
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
    brand: {
      '@type': 'Brand',
      name: 'TheGrantScout',
      logo: 'https://thegrantscout.com/favicon.svg',
    },
    serviceOutput: {
      '@type': 'Report',
      name: 'Monthly Grant Matching Report',
      description: 'Curated foundation opportunities with funder profiles, giving history, contact information, and positioning strategies.',
    },
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
        description: '$83/mo billed annually at $999',
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
        name: 'What information do I need to provide?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'During our call, we\'ll ask about your organization\'s mission, programs, geographic focus, annual budget, and the populations you serve. The more detail you provide, the better we can match you with relevant foundations.',
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
      {
        '@type': 'Question',
        name: 'Do you guarantee I\'ll get grants?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'We can\'t guarantee you\'ll receive funding, but we significantly improve your chances by matching you with foundations that have a proven track record of funding organizations like yours.',
        },
      },
      {
        '@type': 'Question',
        name: 'How current is your foundation data?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'We update our database regularly as new 990 forms are filed with the IRS. Most foundation data is updated quarterly, ensuring you have access to the most recent giving patterns and contact information.',
        },
      },
      {
        '@type': 'Question',
        name: 'How do I get started?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Book a call with us to discuss your organization\'s needs. We\'ll walk you through how TheGrantScout works and answer any questions. If it\'s a good fit, we\'ll get you set up as a Founding Member.',
        },
      },
      {
        '@type': 'Question',
        name: 'What is grant matching?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Grant matching is the process of identifying foundations whose giving history and priorities align with your nonprofit\'s mission, programs, and geography. TheGrantScout uses AI to analyze 8.3M+ grants to find foundations most likely to fund your work.',
        },
      },
      {
        '@type': 'Question',
        name: 'How much does grant research typically cost?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Grant research services range from $50-500+ per month. TheGrantScout offers founding member pricing at $83-99/month for comprehensive monthly reports with curated opportunities, funder profiles, and positioning strategies.',
        },
      },
      {
        '@type': 'Question',
        name: 'What are IRS 990-PF forms?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'IRS Form 990-PF is an annual tax return filed by private foundations. It contains detailed information about every grant made, including recipient names, amounts, and purposes. TheGrantScout analyzes these public filings to identify funding patterns.',
        },
      },
      {
        '@type': 'Question',
        name: 'How is TheGrantScout different from grant writing services?',
        acceptedAnswer: {
          '@type': 'Answer',
          text: 'Grant writing services help you write proposals; TheGrantScout helps you find the right foundations to approach in the first place. We focus on the research and matching phase, providing intelligence about which funders are most likely to fund work like yours.',
        },
      },
    ],
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(websiteSchema) }}
      />
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
