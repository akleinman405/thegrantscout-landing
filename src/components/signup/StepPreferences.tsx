'use client'

import { SignupFormData, ReportRecipient, REPORT_COUNT_OPTIONS, StepValidationErrors } from '@/lib/signup-types'
import FormField, { TextInput, TextArea } from './FormField'

interface Props {
  data: SignupFormData
  errors: StepValidationErrors
  onChange: (field: keyof SignupFormData, value: string | number | ReportRecipient[]) => void
}

export default function StepPreferences({ data, errors, onChange }: Props) {
  const handleCountChange = (count: number) => {
    onChange('reportCount', count)
    // Resize recipients array to match
    const current = data.reportRecipients
    if (count > current.length) {
      const added = Array.from({ length: count - current.length }, () => ({ name: '', email: '', focus: '' }))
      onChange('reportRecipients', [...current, ...added])
    } else {
      onChange('reportRecipients', current.slice(0, count))
    }
  }

  const updateRecipient = (index: number, field: 'name' | 'email' | 'focus', value: string) => {
    const updated = data.reportRecipients.map((r, i) =>
      i === index ? { ...r, [field]: value } : r
    )
    onChange('reportRecipients', updated)
  }

  return (
    <div>
      <h2 className="heading-3 mb-1">Preferences</h2>
      <p className="text-gray-medium text-sm mb-6">Help us tailor your playbook. Skip anything you&apos;re unsure about.</p>

      <FormField
        label="Funders You Have Relationships With or Are Currently Pursuing"
        hint="We'll exclude these from your playbook so we only surface new opportunities"
      >
        <TextArea
          value={data.knownFunders}
          onChange={(v) => onChange('knownFunders', v)}
          placeholder="List foundation names separated by commas, e.g., Ford Foundation, Gates Foundation"
          rows={3}
        />
      </FormField>

      <FormField
        label="How Many Playbooks Do You Need?"
        hint="If different team members have different focuses, each can get a tailored playbook"
      >
        <div className="flex gap-2">
          {REPORT_COUNT_OPTIONS.map((n) => (
            <button
              key={n}
              type="button"
              onClick={() => handleCountChange(n)}
              className={`w-12 h-12 rounded-lg text-sm font-semibold transition-all border-2 ${
                data.reportCount === n
                  ? 'bg-primary text-white border-primary'
                  : 'bg-white text-charcoal border-gray-200 hover:border-primary/40'
              }`}
            >
              {n}
            </button>
          ))}
        </div>
      </FormField>

      {data.reportCount > 1 && (
        <div className="space-y-4 mb-5">
          <p className="text-sm font-semibold text-primary">Playbook Recipients</p>
          {data.reportRecipients.map((recipient, i) => (
            <div key={i} className="bg-gray-50 rounded-xl p-4">
              <p className="text-xs font-semibold text-primary/60 uppercase tracking-wide mb-3">Playbook {i + 1}</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4">
                <FormField label="Recipient Name">
                  <TextInput
                    value={recipient.name}
                    onChange={(v) => updateRecipient(i, 'name', v)}
                    placeholder="e.g., Jane Smith"
                  />
                </FormField>
                <FormField label="Email">
                  <TextInput
                    value={recipient.email}
                    onChange={(v) => updateRecipient(i, 'email', v)}
                    placeholder="e.g., jane@organization.org"
                    type="email"
                  />
                </FormField>
              </div>
              <FormField label="Their Focus">
                <TextArea
                  value={recipient.focus}
                  onChange={(v) => updateRecipient(i, 'focus', v)}
                  placeholder="e.g., Relationship building with new corporate foundations, open grant opportunities for capital campaigns..."
                  rows={2}
                />
              </FormField>
            </div>
          ))}
        </div>
      )}

      {data.reportCount === 1 && (
        <FormField label="Playbook Focus" hint="What kind of opportunities are you most interested in?">
          <TextArea
            value={data.reportRecipients[0]?.focus || ''}
            onChange={(v) => updateRecipient(0, 'focus', v)}
            placeholder="e.g., Relationship building with new funders, open grant opportunities, both..."
            rows={2}
          />
        </FormField>
      )}

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
