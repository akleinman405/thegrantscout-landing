import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Terms of Service',
  description: 'TheGrantScout Terms of Service - Read our terms and conditions for using our AI-powered grant matching service for nonprofits.',
  alternates: {
    canonical: 'https://thegrantscout.com/terms',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-snippet': 50,  // Limit snippet length for secondary pages
    },
  },
}

export default function TermsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}
