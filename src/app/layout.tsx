import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'TheGrantScout - AI-Powered Grant Matching for Nonprofits',
  description: 'TheGrantScout uses AI to match your nonprofit with foundations already supporting work like yours. Find funding faster with intelligent grant matching.',
  keywords: 'grants, nonprofit funding, foundation grants, grant matching, AI grant search',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className={inter.className}>{children}</body>
    </html>
  )
}
