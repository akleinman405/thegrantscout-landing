'use client'

import {
  SignupFormData,
  US_STATES,
  GEOGRAPHIC_SCOPES,
  BUDGET_RANGES,
  GRANT_SIZE_RANGES,
  GRANT_TYPES,
  GRANT_CAPACITIES,
  StepValidationErrors,
} from '@/lib/signup-types'
import FormField, { TextInput, Select, MultiSelect } from './FormField'

interface Props {
  data: SignupFormData
  errors: StepValidationErrors
  onChange: (field: keyof SignupFormData, value: string | string[]) => void
}

export default function StepCapacity({ data, errors, onChange }: Props) {
  return (
    <div>
      <h2 className="heading-3 mb-1">Capacity & Geography</h2>
      <p className="text-gray-medium text-sm mb-6">Where you work and what you&apos;re looking for.</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4">
        <FormField label="State" required error={errors.state}>
          <Select
            value={data.state}
            onChange={(v) => onChange('state', v)}
            options={US_STATES}
            placeholder="Select state..."
            error={errors.state}
          />
        </FormField>

        <FormField label="City" required error={errors.city}>
          <TextInput
            value={data.city}
            onChange={(v) => onChange('city', v)}
            placeholder="e.g., San Diego"
            error={errors.city}
          />
        </FormField>
      </div>

      <FormField label="Geographic Scope" required error={errors.geographicScope}>
        <Select
          value={data.geographicScope}
          onChange={(v) => onChange('geographicScope', v)}
          options={GEOGRAPHIC_SCOPES}
          placeholder="How broad is your service area?"
          error={errors.geographicScope}
        />
      </FormField>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4">
        <FormField label="Annual Budget" required error={errors.annualBudget}>
          <Select
            value={data.annualBudget}
            onChange={(v) => onChange('annualBudget', v)}
            options={BUDGET_RANGES}
            placeholder="Select range..."
            error={errors.annualBudget}
          />
        </FormField>

        <FormField label="Grant Size Seeking" required error={errors.grantSizeSeeking}>
          <Select
            value={data.grantSizeSeeking}
            onChange={(v) => onChange('grantSizeSeeking', v)}
            options={GRANT_SIZE_RANGES}
            placeholder="Select range..."
            error={errors.grantSizeSeeking}
          />
        </FormField>
      </div>

      <FormField label="Grant Types Preferred" required error={errors.grantTypes} hint="Select all that apply">
        <MultiSelect
          selected={data.grantTypes}
          onChange={(v) => onChange('grantTypes', v)}
          options={GRANT_TYPES}
          error={errors.grantTypes}
        />
      </FormField>

      <FormField label="Grant Experience" required error={errors.grantCapacity}>
        <Select
          value={data.grantCapacity}
          onChange={(v) => onChange('grantCapacity', v)}
          options={GRANT_CAPACITIES}
          placeholder="Select experience level..."
          error={errors.grantCapacity}
        />
      </FormField>
    </div>
  )
}
