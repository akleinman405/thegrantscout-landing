import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Privacy Policy',
  description: 'TheGrantScout Privacy Policy - Learn how we collect, use, and protect your personal information when you use our grant matching service.',
  alternates: {
    canonical: 'https://thegrantscout.com/privacy',
  },
}

export default function PrivacyLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}
