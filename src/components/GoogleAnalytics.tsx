'use client'

import Script from 'next/script'

const GA_MEASUREMENT_ID = 'G-QDCG0DXNXF'

export default function GoogleAnalytics() {
  return (
    <>
      <Script
        src={`https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`}
        strategy="afterInteractive"
      />
      <Script id="google-analytics" strategy="afterInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${GA_MEASUREMENT_ID}');
        `}
      </Script>
    </>
  )
}

// Helper function to track events - import this in components that need tracking
export function trackEvent(action: string, category: string, label?: string, value?: number) {
  if (typeof window !== 'undefined' && (window as any).gtag) {
    (window as any).gtag('event', action, {
      event_category: category,
      event_label: label,
      value: value,
    })
  }
}

// Pre-defined tracking functions for common CTA events
export const trackCTA = {
  bookCall: (location: string) => {
    trackEvent('click', 'CTA', `book_call_${location}`)
  },
  sampleReport: (location: string) => {
    trackEvent('click', 'CTA', `sample_report_${location}`)
  },
  navigation: (section: string) => {
    trackEvent('click', 'Navigation', section)
  },
}
