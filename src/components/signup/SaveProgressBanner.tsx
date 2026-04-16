'use client'

import { useState } from 'react'
import type { User } from '@supabase/supabase-js'

interface Props {
  email: string
  authUser: User | null
  authLoading: boolean
  authError: string | null
  onSendMagicLink: (email: string) => Promise<boolean>
}

export default function SaveProgressBanner({ email, authUser, authLoading, authError, onSendMagicLink }: Props) {
  const [dismissed, setDismissed] = useState(false)
  const [sent, setSent] = useState(false)

  if (dismissed) return null

  // Already has an active session (clicked a magic link earlier this visit, or is signed in)
  if (authUser) {
    return (
      <div className="mt-6 mb-2 bg-success/5 border border-success/20 rounded-xl p-4 flex items-center gap-3">
        <svg className="w-5 h-5 text-success flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
        <p className="text-sm text-charcoal">
          Signed in as <span className="font-medium">{authUser.email}</span>. Your progress is saved and you can resume from any device.
        </p>
      </div>
    )
  }

  // Just sent a magic link
  if (sent) {
    return (
      <div className="mt-6 mb-2 bg-success/5 border border-success/20 rounded-xl p-4 flex items-start gap-3">
        <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
        <div className="text-sm text-charcoal">
          <p className="font-semibold mb-1">Check your inbox</p>
          <p>We sent a one-click resume link to <span className="font-medium">{email}</span>. Click it from any device to pick up where you left off. (Check spam if it doesn&apos;t show up in a minute.)</p>
        </div>
      </div>
    )
  }

  const handleSubmit = async () => {
    if (!email) return
    const ok = await onSendMagicLink(email)
    if (ok) setSent(true)
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
      <p className="text-xs text-gray-medium mb-3">We&apos;ll email you a one-click link to resume from any device — no password needed.</p>

      <div className="flex flex-col sm:flex-row gap-2">
        <input
          type="email"
          value={email}
          disabled
          className="form-input-mobile flex-1 bg-gray-100 text-gray-500 cursor-not-allowed text-sm"
        />
        <button
          type="button"
          onClick={handleSubmit}
          disabled={authLoading || !email}
          className="btn-primary px-4 py-2 text-sm whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {authLoading ? 'Sending...' : 'Email me a link'}
        </button>
      </div>

      {authError && (
        <p className="text-xs text-error mt-2">{authError}</p>
      )}
    </div>
  )
}
