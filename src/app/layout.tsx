import type { Metadata } from 'next'
import { Inter, Raleway } from 'next/font/google'
import './globals.css'
import GoogleAnalytics from '@/components/GoogleAnalytics'
import StructuredData from '@/components/StructuredData'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const raleway = Raleway({
  subsets: ['latin'],
  variable: '--font-raleway',
  display: 'swap',
  weight: ['500', '600', '700'],
})

export const metadata: Metadata = {
  title: 'TheGrantScout - AI-Powered Grant Matching for Nonprofits',
  description: 'Find foundations already funding work like yours. TheGrantScout uses AI to match nonprofits with grant opportunities from 85,000+ foundations and 1.6M+ grants.',
  keywords: 'grant matching, nonprofit grants, foundation funding, AI grant search, find foundation grants, nonprofit funding, private foundation grants',
  authors: [{ name: 'TheGrantScout' }],
  icons: {
    icon: '/favicon.svg',
    shortcut: '/favicon.svg',
    apple: '/favicon.svg',
  },
  metadataBase: new URL('https://thegrantscout.com'),
  openGraph: {
    title: 'TheGrantScout - AI-Powered Grant Matching for Nonprofits',
    description: 'Find foundations already funding work like yours. Monthly reports with curated opportunities, funder intel, and positioning strategy.',
    url: 'https://thegrantscout.com',
    siteName: 'TheGrantScout',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'TheGrantScout - AI-Powered Grant Matching for Nonprofits',
    description: 'Find foundations already funding work like yours. AI-powered grant matching for nonprofits.',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  alternates: {
    canonical: 'https://thegrantscout.com',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${raleway.variable}`}>
      <head>
        <GoogleAnalytics />
        <StructuredData />
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  )
}
