'use client'

import { useState } from 'react'
import type { User } from '@supabase/supabase-js'

interface Props {
  email: string
  authUser: User | null
  authLoading: boolean
  authError: string | null
  onCreateAccount: (email: string, password: string) => Promise<boolean>
}

export default function SaveProgressBanner({ email, authUser, authLoading, authError, onCreateAccount }: Props) {
  const [password, setPassword] = useState('')
  const [dismissed, setDismissed] = useState(false)
  const [success, setSuccess] = useState(false)

  if (dismissed) return null

  // Already has an account
  if (authUser) {
    return (
      <div className="mt-6 mb-2 bg-success/5 border border-success/20 rounded-xl p-4 flex items-center gap-3">
        <svg className="w-5 h-5 text-success flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
        <p className="text-sm text-charcoal">
          Progress saved to your account (<span className="font-medium">{authUser.email}</span>). You can resume from any device.
        </p>
      </div>
    )
  }

  // Just created account
  if (success) {
    return (
      <div className="mt-6 mb-2 bg-success/5 border border-success/20 rounded-xl p-4 flex items-center gap-3">
        <svg className="w-5 h-5 text-success flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
        <p className="text-sm text-charcoal">
          Account created! Your progress is saved. You can close this page and come back anytime.
        </p>
      </div>
    )
  }

  const handleSubmit = async () => {
    if (!password || password.length < 6) return
    const ok = await onCreateAccount(email, password)
    if (ok) {
      setSuccess(true)
      setPassword('')
    }
  }

  return (
    <div className="mt-6 mb-2 bg-primary/5 border border-primary/15 rounded-xl p-4 relative">
      <button
        type="button"
        onClick={() => setDismissed(true)}
        className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 p-1"
        aria-label="Dismiss"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <p className="text-sm font-semibold text-primary mb-1">Save & continue later?</p>
      <p className="text-xs text-gray-medium mb-3">Create a free account to save your progress and resume from any device.</p>

      <div className="flex flex-col sm:flex-row gap-2">
        <input
          type="email"
          value={email}
          disabled
          className="form-input-mobile flex-1 bg-gray-100 text-gray-500 cursor-not-allowed text-sm"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Create a password"
          minLength={6}
          className="form-input-mobile flex-1 text-sm"
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
        />
        <button
          type="button"
          onClick={handleSubmit}
          disabled={authLoading || !password || password.length < 6}
          className="btn-primary px-4 py-2 text-sm whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {authLoading ? 'Saving...' : 'Save Progress'}
        </button>
      </div>

      {authError && (
        <p className="text-xs text-error mt-2">{authError}</p>
      )}
      {password && password.length < 6 && (
        <p className="text-xs text-gray-medium mt-1">Password must be at least 6 characters</p>
      )}
    </div>
  )
}
