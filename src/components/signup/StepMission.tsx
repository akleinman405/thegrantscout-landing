'use client'

import { SignupFormData, FOCUS_AREAS, POPULATIONS, StepValidationErrors } from '@/lib/signup-types'
import FormField, { TextArea, MultiSelect } from './FormField'

interface Props {
  data: SignupFormData
  errors: StepValidationErrors
  onChange: (field: keyof SignupFormData, value: string | string[]) => void
}

export default function StepMission({ data, errors, onChange }: Props) {
  return (
    <div>
      <h2 className="heading-3 mb-1">Mission & Focus</h2>
      <p className="text-gray-medium text-sm mb-6">Help us understand your work so we can find the right funders.</p>

      <FormField label="Mission Statement" required error={errors.mission} hint="Describe your organization's mission (min 50 characters)">
        <TextArea
          value={data.mission}
          onChange={(v) => onChange('mission', v)}
          placeholder="What is your organization's mission? What impact do you strive to make?"
          error={errors.mission}
        />
      </FormField>

      <FormField label="Focus Areas" required error={errors.focusAreas} hint="Select all that apply">
        <MultiSelect
          selected={data.focusAreas}
          onChange={(v) => onChange('focusAreas', v)}
          options={FOCUS_AREAS}
          error={errors.focusAreas}
        />
      </FormField>

      <FormField label="Programs & Services" required error={errors.programs} hint="Describe your key programs (min 50 characters)">
        <TextArea
          value={data.programs}
          onChange={(v) => onChange('programs', v)}
          placeholder="Describe your main programs, services, or initiatives. What specific activities do you carry out?"
          error={errors.programs}
        />
      </FormField>

      <FormField label="Populations Served" required error={errors.populations} hint="Select all that apply">
        <MultiSelect
          selected={data.populations}
          onChange={(v) => onChange('populations', v)}
          options={POPULATIONS}
          error={errors.populations}
        />
      </FormField>
    </div>
  )
}
