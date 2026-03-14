'use client'

import { SignupFormData, US_STATES } from '@/lib/signup-types'

interface Props {
  data: SignupFormData
  onChange: (field: keyof SignupFormData, value: string) => void
}

function ReviewSection({ title, items }: { title: string; items: { label: string; value: string }[] }) {
  return (
    <div className="mb-6">
      <h3 className="text-sm font-semibold text-primary uppercase tracking-wide mb-2">{title}</h3>
      <div className="bg-gray-50 rounded-lg p-4 space-y-2">
        {items.map((item) => (
          <div key={item.label} className="flex flex-col sm:flex-row sm:gap-2">
            <span className="text-sm text-gray-medium font-medium min-w-[140px]">{item.label}:</span>
            <span className="text-sm text-charcoal">{item.value || <span className="italic text-gray-400">Not provided</span>}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function StepReview({ data, onChange }: Props) {
  const stateName = US_STATES.find((s) => s.value === data.state)?.label || data.state

  return (
    <div>
      <h2 className="heading-3 mb-1">Review & Select Plan</h2>
      <p className="text-gray-medium text-sm mb-6">Review your information, then choose a plan to continue.</p>

      <ReviewSection
        title="Organization"
        items={[
          { label: 'Name', value: data.orgName },
          { label: 'EIN', value: data.ein },
          { label: 'Type', value: data.orgType },
          { label: 'Contact', value: `${data.contactName} (${data.contactEmail})` },
        ]}
      />

      <ReviewSection
        title="Mission & Focus"
        items={[
          { label: 'Mission', value: data.mission.length > 120 ? data.mission.slice(0, 120) + '...' : data.mission },
          { label: 'Focus Areas', value: data.focusAreas.join(', ') },
          { label: 'Programs', value: data.programs.length > 120 ? data.programs.slice(0, 120) + '...' : data.programs },
          { label: 'Populations', value: data.populations.join(', ') },
        ]}
      />

      <ReviewSection
        title="Capacity & Geography"
        items={[
          { label: 'Location', value: `${data.city}, ${stateName}` },
          { label: 'Scope', value: data.geographicScope },
          { label: 'Budget', value: data.annualBudget },
          { label: 'Grant Size', value: data.grantSizeSeeking },
          { label: 'Grant Types', value: data.grantTypes.join(', ') },
          { label: 'Experience', value: data.grantCapacity },
        ]}
      />

      {(data.nteeCode || data.knownFunders || data.timeframe || data.additionalNotes) && (
        <ReviewSection
          title="Preferences"
          items={[
            ...(data.nteeCode ? [{ label: 'NTEE Code', value: data.nteeCode }] : []),
            ...(data.knownFunders ? [{ label: 'Known Funders', value: data.knownFunders }] : []),
            ...(data.timeframe ? [{ label: 'Timeframe', value: data.timeframe }] : []),
            ...(data.additionalNotes ? [{ label: 'Notes', value: data.additionalNotes.length > 120 ? data.additionalNotes.slice(0, 120) + '...' : data.additionalNotes }] : []),
          ]}
        />
      )}

      {/* Plan Selection */}
      <div className="mt-8 mb-4">
        <h3 className="text-sm font-semibold text-primary uppercase tracking-wide mb-3">Choose Your Plan</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <button
            type="button"
            onClick={() => onChange('planType', 'annual')}
            className={`relative p-5 rounded-xl border-2 text-left transition-all ${
              data.planType === 'annual'
                ? 'border-accent bg-accent/5 shadow-md'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="absolute -top-3 left-4">
              <span className="bg-accent text-primary px-2 py-0.5 rounded-full text-xs font-semibold">BEST VALUE</span>
            </div>
            <div className="text-2xl font-bold text-primary">$83<span className="text-base font-semibold">/mo</span></div>
            <div className="text-sm text-gray-medium">Billed annually at $999</div>
            <div className="text-xs text-success font-medium mt-1">Save $189/year</div>
          </button>

          <button
            type="button"
            onClick={() => onChange('planType', 'monthly')}
            className={`p-5 rounded-xl border-2 text-left transition-all ${
              data.planType === 'monthly'
                ? 'border-accent bg-accent/5 shadow-md'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="text-2xl font-bold text-primary">$99<span className="text-base font-semibold">/mo</span></div>
            <div className="text-sm text-gray-medium">Billed monthly</div>
            <div className="text-xs text-gray-medium mt-1">Cancel anytime</div>
          </button>
        </div>
      </div>
    </div>
  )
}
