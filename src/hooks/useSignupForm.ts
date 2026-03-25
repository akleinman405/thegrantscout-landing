'use client'

import { useState, useEffect, useCallback } from 'react'
import { SignupFormData, INITIAL_FORM_DATA, PREVIEW_FORM_DATA, LocationEntry, ReportRecipient, validateStep, StepValidationErrors } from '@/lib/signup-types'

const STORAGE_KEY = 'tgs_signup_form'

export function useSignupForm(initialStep?: number, preview?: boolean) {
  const [step, setStep] = useState(initialStep || 1)
  const [formData, setFormData] = useState<SignupFormData>(preview ? PREVIEW_FORM_DATA : INITIAL_FORM_DATA)
  const [errors, setErrors] = useState<StepValidationErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [loaded, setLoaded] = useState(false)

  // Restore from localStorage on mount (skip in preview mode)
  useEffect(() => {
    if (preview) {
      // Clear any saved data so preview doesn't leak into normal visits
      try { localStorage.removeItem(STORAGE_KEY) } catch { /* ignore */ }
    } else {
      try {
        const saved = localStorage.getItem(STORAGE_KEY)
        if (saved) {
          const parsed = JSON.parse(saved)
          setFormData({ ...INITIAL_FORM_DATA, ...parsed.formData })
          if (parsed.step) setStep(parsed.step)
        }
      } catch {
        // Ignore parse errors
      }
    }
    setLoaded(true)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Save to localStorage on change (skip in preview mode)
  useEffect(() => {
    if (!loaded || preview) return
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ formData, step }))
    } catch {
      // Ignore storage errors
    }
  }, [formData, step, loaded, preview])

  const updateField = useCallback((field: keyof SignupFormData, value: string | string[] | number | LocationEntry[] | ReportRecipient[]) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    // Clear field error on change
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
    setStep((s) => Math.min(s + 1, 5))
    return true
  }, [step, formData, preview])

  const goBack = useCallback(() => {
    setErrors({})
    setStep((s) => Math.max(s - 1, 1))
  }, [])

  const clearSavedData = useCallback(() => {
    try {
      localStorage.removeItem(STORAGE_KEY)
    } catch {
      // Ignore
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
  }
}
