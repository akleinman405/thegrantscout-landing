'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { SignupFormData, INITIAL_FORM_DATA, PREVIEW_FORM_DATA, LocationEntry, ReportRecipient, validateStep, StepValidationErrors } from '@/lib/signup-types'
import { createBrowserAuthClient } from '@/lib/supabase'
import type { User } from '@supabase/supabase-js'

const STORAGE_KEY = 'tgs_signup_form'
const DRAFT_TOKEN_KEY = 'tgs_draft_token'

export function useSignupForm(initialStep?: number, preview?: boolean) {
  const [step, setStep] = useState(initialStep || 1)
  const [formData, setFormData] = useState<SignupFormData>(preview ? PREVIEW_FORM_DATA : INITIAL_FORM_DATA)
  const [errors, setErrors] = useState<StepValidationErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [loaded, setLoaded] = useState(false)
  const [draftToken, setDraftToken] = useState<string | null>(null)
  const [authUser, setAuthUser] = useState<User | null>(null)
  const [authLoading, setAuthLoading] = useState(false)
  const [authError, setAuthError] = useState<string | null>(null)

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

  // Restore from localStorage + Supabase on mount (skip in preview mode)
  useEffect(() => {
    if (preview) {
      try { localStorage.removeItem(STORAGE_KEY) } catch { /* ignore */ }
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
      setFormData({ ...INITIAL_FORM_DATA, ...localData.formData })
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
            setFormData({ ...INITIAL_FORM_DATA, ...data.formData })
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

  // Auth: create account
  const createAccount = useCallback(async (email: string, password: string) => {
    setAuthLoading(true)
    setAuthError(null)
    try {
      const supabase = createBrowserAuthClient()
      const { data, error } = await supabase.auth.signUp({ email, password })
      if (error) {
        setAuthError(error.message)
        return false
      }
      // signUp returns a user even if email confirmation is pending.
      // data.user exists but data.session may be null (if confirm required).
      const user = data.user
      if (user) {
        setAuthUser(user)
        // Link draft to user via server route (uses service role, no auth needed)
        if (draftTokenRef.current) {
          await fetch('/api/signup/auth', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              action: 'link-draft',
              draftToken: draftTokenRef.current,
              userId: user.id,
            }),
          })
        }
        // Save current form state
        saveDraft()
      }
      return true
    } catch {
      setAuthError('Something went wrong. Please try again.')
      return false
    } finally {
      setAuthLoading(false)
    }
  }, [saveDraft])

  // Auth: login
  const login = useCallback(async (email: string, password: string) => {
    setAuthLoading(true)
    setAuthError(null)
    try {
      const supabase = createBrowserAuthClient()
      const { data, error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) {
        setAuthError(error.message)
        return false
      }
      if (data.user) {
        setAuthUser(data.user)
        // Fetch their saved draft
        const res = await fetch(`/api/signup/save-draft?user_id=${data.user.id}`)
        const draft = await res.json()
        if (draft.found) {
          setFormData({ ...INITIAL_FORM_DATA, ...draft.formData })
          setStep(draft.step)
          setDraftToken(draft.draftToken)
          try { localStorage.setItem(DRAFT_TOKEN_KEY, draft.draftToken) } catch { /* ignore */ }
        }
      }
      return true
    } catch {
      setAuthError('Something went wrong. Please try again.')
      return false
    } finally {
      setAuthLoading(false)
    }
  }, [])

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
    createAccount,
    login,
    saveDraft,
  }
}
