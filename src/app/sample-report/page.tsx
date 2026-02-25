import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Sample Report',
  description: 'See a real TheGrantScout grant matching report. Monthly foundation recommendations with funder intel, positioning strategy, and action plans.',
}

export default function SampleReportPage() {
  return (
    <iframe
      src="/sample-report.pdf#view=FitH"
      title="TheGrantScout Sample Report"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        border: 'none',
      }}
    />
  )
}
