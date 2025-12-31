import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Terms of Service',
  description: 'TheGrantScout Terms of Service - Read our terms and conditions for using our AI-powered grant matching service for nonprofits.',
  alternates: {
    canonical: 'https://thegrantscout.com/terms',
  },
}

export default function TermsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}
