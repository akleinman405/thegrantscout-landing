'use client'

const STEP_LABELS = ['Organization', 'Mission', 'Capacity', 'Preferences', 'Review']

interface ProgressBarProps {
  currentStep: number
}

export default function ProgressBar({ currentStep }: ProgressBarProps) {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-2">
        {STEP_LABELS.map((label, index) => {
          const stepNum = index + 1
          const isActive = stepNum === currentStep
          const isComplete = stepNum < currentStep
          return (
            <div key={label} className="flex flex-col items-center flex-1">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                  isComplete
                    ? 'bg-success text-white'
                    : isActive
                    ? 'bg-primary text-white'
                    : 'bg-gray-200 text-gray-500'
                }`}
              >
                {isComplete ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  stepNum
                )}
              </div>
              <span
                className={`text-xs mt-1 hidden sm:block ${
                  isActive ? 'text-primary font-semibold' : 'text-gray-500'
                }`}
              >
                {label}
              </span>
            </div>
          )
        })}
      </div>
      <div className="flex gap-1">
        {STEP_LABELS.map((_, index) => (
          <div
            key={index}
            className={`h-1 flex-1 rounded-full transition-all ${
              index + 1 <= currentStep ? 'bg-primary' : 'bg-gray-200'
            }`}
          />
        ))}
      </div>
    </div>
  )
}
