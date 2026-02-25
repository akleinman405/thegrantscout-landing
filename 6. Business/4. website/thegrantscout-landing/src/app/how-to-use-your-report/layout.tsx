import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Grant Report Guide: What\'s Inside & How to Use It',
  description: 'See exactly what\'s in a TheGrantScout grant report: funder profiles, grant histories, positioning strategies, and action plans. Interactive guide with real examples.',
  alternates: {
    canonical: 'https://thegrantscout.com/how-to-use-your-report',
  },
  openGraph: {
    title: 'Grant Report Guide: What\'s Inside & How to Use It | TheGrantScout',
    description: 'See exactly what\'s in a TheGrantScout grant report: funder profiles, grant histories, positioning strategies, and action plans. Interactive guide with real examples.',
    url: 'https://thegrantscout.com/how-to-use-your-report',
    type: 'website',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
    },
  },
}

export default function ReportGuideLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}
