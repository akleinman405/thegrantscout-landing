'use client'

import { SignupFormData, ORG_TYPES, StepValidationErrors } from '@/lib/signup-types'
import FormField, { TextInput, Select } from './FormField'

interface Props {
  data: SignupFormData
  errors: StepValidationErrors
  onChange: (field: keyof SignupFormData, value: string) => void
}

export default function StepOrganization({ data, errors, onChange }: Props) {
  const handleEinChange = (value: string) => {
    // Allow digits and dashes only, max 10 chars (9 digits + 1 dash)
    const cleaned = value.replace(/[^\d-]/g, '').slice(0, 10)
    onChange('ein', cleaned)
  }

  return (
    <div>
      <h2 className="heading-3 mb-1">Organization Information</h2>
      <p className="text-gray-medium text-sm mb-6">Tell us about your nonprofit.</p>

      <FormField label="Organization Name" required error={errors.orgName}>
        <TextInput
          value={data.orgName}
          onChange={(v) => onChange('orgName', v)}
          placeholder="e.g., Horizons National"
          error={errors.orgName}
        />
      </FormField>

      <FormField label="EIN (Employer Identification Number)" required error={errors.ein} hint="9-digit IRS number, e.g. 12-3456789 or 123456789">
        <TextInput
          value={data.ein}
          onChange={handleEinChange}
          placeholder="XX-XXXXXXX"
          error={errors.ein}
        />
      </FormField>

      <FormField label="Organization Type" required error={errors.orgType}>
        <Select
          value={data.orgType}
          onChange={(v) => onChange('orgType', v)}
          options={ORG_TYPES}
          placeholder="Select type..."
          error={errors.orgType}
        />
      </FormField>

      <FormField label="Contact Name" required error={errors.contactName}>
        <TextInput
          value={data.contactName}
          onChange={(v) => onChange('contactName', v)}
          placeholder="Your full name"
          error={errors.contactName}
        />
      </FormField>

      <FormField label="Contact Email" required error={errors.contactEmail} hint="Reports will be delivered to this address">
        <TextInput
          value={data.contactEmail}
          onChange={(v) => onChange('contactEmail', v)}
          placeholder="you@organization.org"
          type="email"
          error={errors.contactEmail}
        />
      </FormField>
    </div>
  )
}
