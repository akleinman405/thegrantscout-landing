'use client'

import { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'

function SuccessContent() {
  const searchParams = useSearchParams()
  const sessionId = searchParams.get('session_id')
  const [orgName, setOrgName] = useState('')
  const [email, setEmail] = useState('')

  useEffect(() => {
    // Clear saved form data
    try {
      localStorage.removeItem('tgs_signup_form')
    } catch {
      // Ignore
    }

    // Fetch session details
    if (sessionId) {
      fetch(`/api/checkout?session_id=${sessionId}`)
        .then((res) => res.json())
        .then((data) => {
          if (data.orgName) setOrgName(data.orgName)
          if (data.email) setEmail(data.email)
        })
        .catch(() => {
          // Non-critical, page works without session details
        })
    }
  }, [sessionId])

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="text-2xl font-bold text-primary hover:text-primary-light transition-colors">
              TheGrantScout
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <div className="bg-white rounded-2xl shadow-lg p-8 sm:p-12">
          <div className="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>

          <h1 className="heading-2 mb-4">Welcome to TheGrantScout!</h1>

          {orgName && (
            <p className="text-lg text-charcoal mb-2">
              <strong>{orgName}</strong> is all set.
            </p>
          )}

          <p className="text-gray-medium mb-8">
            Your first grant matching report will arrive
            {email ? ` at ${email}` : ''} within <strong>3-5 business days</strong>.
          </p>

          <div className="bg-gray-50 rounded-xl p-6 mb-8 text-left">
            <h3 className="font-semibold text-primary mb-3">What happens next:</h3>
            <ol className="space-y-3 text-sm text-charcoal">
              <li className="flex gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center text-xs font-bold">1</span>
                <span>We review your organization profile and begin matching you with relevant foundations.</span>
              </li>
              <li className="flex gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center text-xs font-bold">2</span>
                <span>Your first report arrives via email within 3-5 business days.</span>
              </li>
              <li className="flex gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center text-xs font-bold">3</span>
                <span>Every month, you receive a fresh report with new foundation matches.</span>
              </li>
            </ol>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/" className="btn-primary inline-block text-center">
              Back to Home
            </Link>
            <a href="mailto:hello@thegrantscout.com" className="btn-secondary inline-block text-center">
              Contact Us
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function SuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-pulse text-gray-400">Loading...</div>
      </div>
    }>
      <SuccessContent />
    </Suspense>
  )
}
