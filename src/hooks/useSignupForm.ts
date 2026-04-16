'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { SignupFormData, INITIAL_FORM_DATA, PREVIEW_FORM_DATA, LocationEntry, ReportRecipient, validateStep, StepValidationErrors, normalizeFormData } from '@/lib/signup-types'
import { createBrowserAuthClient } from '@/lib/supabase'
import type { User } from '@supabase/supabase-js'

const STORAGE_KEY = 'tgs_signup_form'
const DRAFT_TOKEN_KEY = 'tgs_draft_token'

export function useSignupForm(initialStep?: number, preview?: boolean, fresh?: boolean) {
  const [step, setStep] = useState(initialStep || 1)
  const [formData, setFormData] = useState<SignupFormData>(preview ? PREVIEW_FORM_DATA : INITIAL_FORM_DATA)
  const [errors, setErrors] = useState<StepValidationErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [loaded, setLoaded] = useState(false)
  const [draftToken, setDraftToken] = useState<string | null>(null)
  const [authUser, setAuthUser] = useState<User | null>(null)
  const [authLoading, setAuthLoading] = useState(false)
  const [authError, setAuthError] = useState<string | null>(null)
  const [magicLinkSent, setMagicLinkSent] = useState(false)

  // Ref to avoid stale closures in saveDraft
  const formDataRef = useRef(formData)
  const stepRef = useRef(step)
  const draftTokenRef = useRef(draftToken)
  useEffect(() => { formDataRef.current = formData }, [formData])
  useEffect(() => { stepRef.current = step }, [step])
  useEffect(() => { draftTokenRef.current = draftToken }, [draftToken])

  // Check for existing auth session on mount
  useEffect(() => {
    if (preview) return
    const supabase = createBrowserAuthClient()
    supabase.auth.getUser().then(({ data }) => {
      if (data.user) setAuthUser(data.user)
    })
  }, [preview])

  // Restore from localStorage + Supabase on mount (skip in preview mode or when ?fresh=true)
  useEffect(() => {
    if (preview) {
      try { localStorage.removeItem(STORAGE_KEY) } catch { /* ignore */ }
      setLoaded(true)
      return
    }

    if (fresh) {
      // User clicked "Start New Application" — wipe local draft and skip Supabase restore
      try {
        localStorage.removeItem(STORAGE_KEY)
        localStorage.removeItem(DRAFT_TOKEN_KEY)
      } catch { /* ignore */ }
      setDraftToken(null)
      setLoaded(true)
      return
    }

    // Restore localStorage first (fast path)
    let localData: { formData?: Partial<SignupFormData>; step?: number; savedAt?: string } | null = null
    let localToken: string | null = null
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) localData = JSON.parse(saved)
      localToken = localStorage.getItem(DRAFT_TOKEN_KEY)
    } catch { /* ignore */ }

    if (localData) {
      setFormData(normalizeFormData(localData.formData))
      if (!initialStep && localData.step) setStep(localData.step)
    }
    if (localToken) {
      setDraftToken(localToken)
    }

    // Then try Supabase (prefer if newer)
    const fetchDraft = async () => {
      try {
        const params = new URLSearchParams()
        if (localToken) params.set('token', localToken)

        // Also check by auth user
        const supabase = createBrowserAuthClient()
        const { data: userData } = await supabase.auth.getUser()
        if (userData.user) {
          params.set('user_id', userData.user.id)
        }

        if (!params.toString()) {
          setLoaded(true)
          return
        }

        const res = await fetch(`/api/signup/save-draft?${params}`)
        const data = await res.json()

        if (data.found) {
          // Supabase draft found — use it if newer than localStorage
          const supabaseTime = new Date(data.updatedAt).getTime()
          const localTime = localData?.savedAt ? new Date(localData.savedAt).getTime() : 0

          if (supabaseTime >= localTime) {
            setFormData(normalizeFormData(data.formData))
            if (!initialStep) setStep(data.step)
          }
          setDraftToken(data.draftToken)
          try { localStorage.setItem(DRAFT_TOKEN_KEY, data.draftToken) } catch { /* ignore */ }
        }
      } catch {
        // Non-fatal — localStorage is the fallback
      }
      setLoaded(true)
    }

    fetchDraft()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Save to localStorage on change (skip in preview mode)
  useEffect(() => {
    if (!loaded || preview) return
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        formData,
        step,
        savedAt: new Date().toISOString(),
      }))
    } catch { /* ignore */ }
  }, [formData, step, loaded, preview])

  // Auto-save to Supabase (non-blocking)
  const saveDraft = useCallback(async (nextStep?: number) => {
    if (preview) return
    const currentFormData = formDataRef.current
    const currentStep = nextStep ?? stepRef.current
    const currentToken = draftTokenRef.current

    try {
      const res = await fetch('/api/signup/save-draft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          draftToken: currentToken,
          step: currentStep,
          formData: currentFormData,
        }),
      })
      const data = await res.json()
      if (data.draftToken && data.draftToken !== currentToken) {
        setDraftToken(data.draftToken)
        try { localStorage.setItem(DRAFT_TOKEN_KEY, data.draftToken) } catch { /* ignore */ }
      }
    } catch {
      // Non-fatal — localStorage is the fallback
    }
  }, [preview])

  const updateField = useCallback((field: keyof SignupFormData, value: string | string[] | number | LocationEntry[] | ReportRecipient[]) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    setErrors((prev) => {
      const next = { ...prev }
      delete next[field]
      return next
    })
  }, [])

  const goNext = useCallback(() => {
    if (!preview) {
      const stepErrors = validateStep(step, formData)
      if (Object.keys(stepErrors).length > 0) {
        setErrors(stepErrors)
        return false
      }
    }
    setErrors({})
    const nextStep = Math.min(step + 1, 5)
    setStep(nextStep)

    // Auto-save to Supabase after successful step transition
    saveDraft(nextStep)

    return true
  }, [step, formData, preview, saveDraft])

  const goBack = useCallback(() => {
    setErrors({})
    setStep((s) => Math.max(s - 1, 1))
  }, [])

  const clearSavedData = useCallback(() => {
    try {
      localStorage.removeItem(STORAGE_KEY)
      localStorage.removeItem(DRAFT_TOKEN_KEY)
    } catch { /* ignore */ }
    setDraftToken(null)
  }, [])

  // Auth: email the user a one-click resume link. Supabase's signInWithOtp sends
  // a magic link when the email+emailRedirectTo path is configured (Auth → URL
  // Configuration). shouldCreateUser=true covers both brand-new savers and
  // returning users — either way they get a link.
  const sendMagicLink = useCallback(async (email: string) => {
    setAuthLoading(true)
    setAuthError(null)
    setMagicLinkSent(false)

    // Make sure the server has the latest draft before we email the link,
    // so when the user clicks the link on another device the restore finds
    // something at least as fresh as what's in localStorage.
    await saveDraft()

    try {
      const supabase = createBrowserAuthClient()
      const origin = typeof window !== 'undefined' ? window.location.origin : ''
      const { error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          shouldCreateUser: true,
          emailRedirectTo: `${origin}/auth/callback?next=/signup`,
        },
      })
      if (error) {
        setAuthError(error.message)
        return false
      }
      setMagicLinkSent(true)
      return true
    } catch {
      setAuthError('Something went wrong. Please try again.')
      return false
    } finally {
      setAuthLoading(false)
    }
  }, [saveDraft])

  return {
    step,
    setStep,
    formData,
    errors,
    isSubmitting,
    setIsSubmitting,
    updateField,
    goNext,
    goBack,
    clearSavedData,
    loaded,
    draftToken,
    authUser,
    authLoading,
    authError,
    magicLinkSent,
    sendMagicLink,
    saveDraft,
  }
}
