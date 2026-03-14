'use client'

import { SignupFormData, TIMEFRAMES, StepValidationErrors } from '@/lib/signup-types'
import FormField, { TextInput, TextArea, Select } from './FormField'

interface Props {
  data: SignupFormData
  errors: StepValidationErrors
  onChange: (field: keyof SignupFormData, value: string) => void
}

export default function StepPreferences({ data, errors, onChange }: Props) {
  return (
    <div>
      <h2 className="heading-3 mb-1">Preferences</h2>
      <p className="text-gray-medium text-sm mb-6">Optional details to improve your matches. Skip any you&apos;re unsure about.</p>

      <FormField label="NTEE Code" hint="If you know your IRS NTEE classification code (e.g., B20, P80)">
        <TextInput
          value={data.nteeCode}
          onChange={(v) => onChange('nteeCode', v.toUpperCase())}
          placeholder="e.g., B20"
        />
      </FormField>

      <FormField label="Known Funders" hint="Foundations you already have relationships with (we'll exclude them from your report)">
        <TextArea
          value={data.knownFunders}
          onChange={(v) => onChange('knownFunders', v)}
          placeholder="List foundation names separated by commas, e.g., Ford Foundation, Gates Foundation"
          rows={3}
        />
      </FormField>

      <FormField label="Timeframe" hint="When are you looking to apply for grants?">
        <Select
          value={data.timeframe}
          onChange={(v) => onChange('timeframe', v)}
          options={TIMEFRAMES}
          placeholder="Select timeframe..."
        />
      </FormField>

      <FormField label="Additional Notes" error={errors.additionalNotes} hint="Anything else we should know?">
        <TextArea
          value={data.additionalNotes}
          onChange={(v) => onChange('additionalNotes', v)}
          placeholder="Any specific requirements, priorities, or context that would help us find better matches..."
          rows={3}
          maxLength={1000}
        />
      </FormField>
    </div>
  )
}
