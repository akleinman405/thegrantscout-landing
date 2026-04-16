'use client'

import { useState, Suspense } from 'react'
import Link from 'next/link'
import { createBrowserAuthClient } from '@/lib/supabase'

function ResumeForm() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sent, setSent] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return

    setLoading(true)
    setError(null)

    try {
      const supabase = createBrowserAuthClient()
      const origin = typeof window !== 'undefined' ? window.location.origin : ''
      const { error: authError } = await supabase.auth.signInWithOtp({
        email,
        options: {
          shouldCreateUser: false,
          emailRedirectTo: `${origin}/auth/callback?next=/signup`,
        },
      })
      if (authError) {
        setError(authError.message)
        setLoading(false)
        return
      }
      setSent(true)
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="text-2xl font-bold text-primary hover:text-primary-light transition-colors">
              TheGrantScout
            </Link>
            <Link href="/signup?fresh=true" className="text-sm text-gray-medium hover:text-primary transition-colors">
              Start New Application
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-md mx-auto px-4 py-16">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h1 className="heading-3 mb-2 text-center">Resume Your Application</h1>

          {sent ? (
            <div className="mt-4 bg-success/5 border border-success/20 rounded-xl p-4 text-sm text-charcoal">
              <p className="font-semibold mb-1">Check your inbox</p>
              <p>We sent a one-click resume link to <span className="font-medium">{email}</span>. Click it from any device to pick up where you left off. (Check spam if it doesn&apos;t show up in a minute.)</p>
            </div>
          ) : (
            <>
              <p className="text-gray-medium text-sm text-center mb-8">
                Enter the email you used when saving your progress — we&apos;ll send you a one-click resume link.
              </p>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-charcoal mb-1">Email</label>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@organization.org"
                    required
                    className="form-input-mobile w-full"
                  />
                </div>

                {error && (
                  <p className="text-sm text-error">{error}</p>
                )}

                <button
                  type="submit"
                  disabled={loading || !email}
                  className="btn-primary w-full py-3 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Sending...' : 'Email me a resume link'}
                </button>
              </form>

              <p className="text-center text-xs text-gray-medium mt-6">
                Don&apos;t have a saved application?{' '}
                <Link href="/signup?fresh=true" className="text-primary hover:underline">Start a new application</Link>
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default function ResumePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-pulse text-gray-400">Loading...</div>
      </div>
    }>
      <ResumeForm />
    </Suspense>
  )
}
