'use client'

import { useState, Suspense } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { createBrowserAuthClient } from '@/lib/supabase'

function ResumeForm() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) return

    setLoading(true)
    setError(null)

    try {
      const supabase = createBrowserAuthClient()
      const { data, error: authError } = await supabase.auth.signInWithPassword({ email, password })

      if (authError) {
        setError(authError.message)
        setLoading(false)
        return
      }

      if (data.user) {
        // Fetch their saved draft
        const res = await fetch(`/api/signup/save-draft?user_id=${data.user.id}`)
        const draft = await res.json()

        if (draft.found) {
          // Store draft data in localStorage for the signup page to pick up
          try {
            localStorage.setItem('tgs_signup_form', JSON.stringify({
              formData: draft.formData,
              step: draft.step,
              savedAt: draft.updatedAt,
            }))
            localStorage.setItem('tgs_draft_token', draft.draftToken)
          } catch { /* ignore */ }

          router.push(`/signup?step=${draft.step}`)
        } else {
          setError('No saved application found for this account. You can start a new one.')
          setLoading(false)
        }
      }
    } catch {
      setError('Something went wrong. Please try again.')
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
            <Link href="/signup" className="text-sm text-gray-medium hover:text-primary transition-colors">
              Start New Application
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-md mx-auto px-4 py-16">
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h1 className="heading-3 mb-2 text-center">Resume Your Application</h1>
          <p className="text-gray-medium text-sm text-center mb-8">
            Enter the email and password you used when saving your progress.
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

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-charcoal mb-1">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Your password"
                required
                minLength={6}
                className="form-input-mobile w-full"
              />
            </div>

            {error && (
              <p className="text-sm text-error">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading || !email || !password}
              className="btn-primary w-full py-3 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Logging in...' : 'Resume Application'}
            </button>
          </form>

          <p className="text-center text-xs text-gray-medium mt-6">
            Don&apos;t have an account?{' '}
            <Link href="/signup" className="text-primary hover:underline">Start a new application</Link>
          </p>
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
