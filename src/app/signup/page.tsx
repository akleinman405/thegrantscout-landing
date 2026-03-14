'use client'

import { useSearchParams } from 'next/navigation'
import { Suspense } from 'react'
import Link from 'next/link'
import { useSignupForm } from '@/hooks/useSignupForm'
import ProgressBar from '@/components/signup/ProgressBar'
import StepOrganization from '@/components/signup/StepOrganization'
import StepMission from '@/components/signup/StepMission'
import StepCapacity from '@/components/signup/StepCapacity'
import StepPreferences from '@/components/signup/StepPreferences'
import StepReview from '@/components/signup/StepReview'

function SignupForm() {
  const searchParams = useSearchParams()
  const initialStep = searchParams.get('step') ? parseInt(searchParams.get('step')!) : undefined

  const {
    step,
    formData,
    errors,
    isSubmitting,
    setIsSubmitting,
    updateField,
    goNext,
    goBack,
    loaded,
  } = useSignupForm(initialStep)

  const handleSubmit = async () => {
    setIsSubmitting(true)
    try {
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })
      const data = await res.json()
      if (data.url) {
        window.location.href = data.url
      } else {
        alert(data.error || 'Something went wrong. Please try again.')
        setIsSubmitting(false)
      }
    } catch {
      alert('Network error. Please try again.')
      setIsSubmitting(false)
    }
  }

  if (!loaded) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-pulse text-gray-400">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="text-2xl font-bold text-primary hover:text-primary-light transition-colors">
              TheGrantScout
            </Link>
            <Link href="/" className="text-sm text-gray-medium hover:text-primary transition-colors">
              Back to Home
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-2xl mx-auto px-4 py-8 sm:py-12">
        <div className="text-center mb-8">
          <h1 className="heading-2 mb-2">Get Started with TheGrantScout</h1>
          <p className="text-gray-medium">Tell us about your nonprofit and we&apos;ll match you with the right funders.</p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8">
          <ProgressBar currentStep={step} />

          {step === 1 && <StepOrganization data={formData} errors={errors} onChange={updateField} />}
          {step === 2 && <StepMission data={formData} errors={errors} onChange={updateField} />}
          {step === 3 && <StepCapacity data={formData} errors={errors} onChange={updateField} />}
          {step === 4 && <StepPreferences data={formData} errors={errors} onChange={updateField} />}
          {step === 5 && <StepReview data={formData} onChange={updateField} />}

          {/* Navigation */}
          <div className="flex justify-between mt-8 pt-6 border-t border-gray-100">
            {step > 1 ? (
              <button
                type="button"
                onClick={goBack}
                className="btn-secondary px-6 py-2.5"
              >
                Back
              </button>
            ) : (
              <div />
            )}

            {step < 5 ? (
              <button
                type="button"
                onClick={goNext}
                className="btn-primary px-8 py-2.5"
              >
                Next
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="btn-primary px-8 py-2.5 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Redirecting to checkout...' : `Subscribe — ${formData.planType === 'annual' ? '$999/year' : '$99/month'}`}
              </button>
            )}
          </div>
        </div>

        <p className="text-center text-xs text-gray-medium mt-6">
          Secure checkout powered by Stripe. By subscribing you agree to our{' '}
          <Link href="/terms" className="underline hover:text-primary">Terms of Service</Link>{' '}
          and{' '}
          <Link href="/privacy" className="underline hover:text-primary">Privacy Policy</Link>.
        </p>
      </div>
    </div>
  )
}

export default function SignupPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-pulse text-gray-400">Loading...</div>
      </div>
    }>
      <SignupForm />
    </Suspense>
  )
}
