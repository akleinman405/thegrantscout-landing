import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Sample Report',
  description: 'See a real TheGrantScout grant matching report. Monthly foundation recommendations with funder intel, positioning strategy, and action plans.',
}

export default function SampleReportPage() {
  return (
    <div className="fixed inset-0 w-screen h-screen">
      <object
        data="/sample-report.pdf"
        type="application/pdf"
        className="w-full h-full"
      >
        <div className="flex items-center justify-center h-full bg-gray-50">
          <div className="text-center p-8">
            <p className="text-lg text-gray-700 mb-4">
              Unable to display PDF in browser.
            </p>
            <a
              href="/sample-report.pdf"
              download
              className="inline-block px-6 py-3 bg-[#1e3a5f] text-white rounded-lg hover:bg-[#152b47] transition-colors"
            >
              Download Sample Report (PDF)
            </a>
          </div>
        </div>
      </object>
    </div>
  )
}
