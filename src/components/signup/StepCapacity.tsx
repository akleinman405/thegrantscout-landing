'use client'

import { useState } from 'react'
import {
  SignupFormData,
  LocationEntry,
  US_STATES,
  GEOGRAPHIC_SCOPES,
  BUDGET_RANGES,
  GRANT_SIZE_RANGES,
  GRANT_TYPES,
  GRANT_CAPACITIES,
  LOCATION_TYPES,
  StepValidationErrors,
} from '@/lib/signup-types'
import FormField, { Select, MultiSelect } from './FormField'

interface Props {
  data: SignupFormData
  errors: StepValidationErrors
  onChange: (field: keyof SignupFormData, value: string | string[] | LocationEntry[]) => void
}

function LocationBuilder({ locations, onChange, error }: {
  locations: LocationEntry[]
  onChange: (locations: LocationEntry[]) => void
  error?: string
}) {
  const [locType, setLocType] = useState<'city' | 'county' | 'state'>('city')
  const [locState, setLocState] = useState('')
  const [locDetail, setLocDetail] = useState('')

  const addLocation = () => {
    if (!locState) return
    if (locType !== 'state' && !locDetail.trim()) return

    const entry: LocationEntry = {
      type: locType,
      state: locState,
      detail: locType === 'state' ? '' : locDetail.trim(),
    }

    // Prevent duplicates
    const isDup = locations.some(
      (l) => l.type === entry.type && l.state === entry.state && l.detail === entry.detail
    )
    if (!isDup) {
      onChange([...locations, entry])
    }

    setLocDetail('')
  }

  const removeLocation = (index: number) => {
    onChange(locations.filter((_, i) => i !== index))
  }

  const formatLocation = (loc: LocationEntry) => {
    const stateLabel = US_STATES.find((s) => s.value === loc.state)?.label || loc.state
    if (loc.type === 'state') return stateLabel
    return `${loc.detail}, ${stateLabel}`
  }

  const formatLocationType = (loc: LocationEntry) => {
    return loc.type === 'state' ? 'State' : loc.type === 'county' ? 'County' : 'City'
  }

  return (
    <div>
      {/* Location tags */}
      {locations.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {locations.map((loc, i) => (
            <span
              key={i}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium"
            >
              <span className="text-xs text-primary/60">{formatLocationType(loc)}</span>
              {formatLocation(loc)}
              <button
                type="button"
                onClick={() => removeLocation(i)}
                className="ml-0.5 text-primary/40 hover:text-error transition-colors"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Add location form */}
      <div className={`flex flex-col sm:flex-row gap-2 ${error ? 'ring-2 ring-error/20 rounded-lg p-2' : ''}`}>
        <select
          value={locType}
          onChange={(e) => setLocType(e.target.value as 'city' | 'county' | 'state')}
          className="form-input-mobile sm:w-32"
        >
          {LOCATION_TYPES.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>

        <select
          value={locState}
          onChange={(e) => setLocState(e.target.value)}
          className={`form-input-mobile sm:flex-1 ${!locState ? 'text-gray-400' : ''}`}
        >
          <option value="">State...</option>
          {US_STATES.map((s) => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>

        {locType !== 'state' && (
          <input
            type="text"
            value={locDetail}
            onChange={(e) => setLocDetail(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addLocation() } }}
            placeholder={locType === 'city' ? 'City name...' : 'County name...'}
            className="form-input-mobile sm:flex-1"
          />
        )}

        <button
          type="button"
          onClick={addLocation}
          disabled={!locState || (locType !== 'state' && !locDetail.trim())}
          className="btn-secondary px-4 py-2 text-sm disabled:opacity-40 disabled:cursor-not-allowed whitespace-nowrap"
        >
          + Add
        </button>
      </div>
    </div>
  )
}

export default function StepCapacity({ data, errors, onChange }: Props) {
  return (
    <div>
      <h2 className="heading-3 mb-1">Capacity & Geography</h2>
      <p className="text-gray-medium text-sm mb-6">Where you work and what you&apos;re looking for.</p>

      <FormField
        label="Service Locations"
        required
        error={errors.locations}
        hint="Add the cities, counties, or states where you operate or seek funding"
      >
        <LocationBuilder
          locations={data.locations}
          onChange={(locs) => onChange('locations', locs)}
          error={errors.locations}
        />
      </FormField>

      <FormField label="Geographic Scope" required error={errors.geographicScope}>
        <Select
          value={data.geographicScope}
          onChange={(v) => onChange('geographicScope', v)}
          options={GEOGRAPHIC_SCOPES}
          placeholder="How broad is your service area?"
          error={errors.geographicScope}
        />
      </FormField>

      <FormField label="Annual Budget" required error={errors.annualBudget}>
        <Select
          value={data.annualBudget}
          onChange={(v) => onChange('annualBudget', v)}
          options={BUDGET_RANGES}
          placeholder="Select range..."
          error={errors.annualBudget}
        />
      </FormField>

      <FormField label="Grant Size Seeking" required error={errors.grantSizeSeeking} hint="Select all that apply">
        <MultiSelect
          selected={data.grantSizeSeeking}
          onChange={(v) => onChange('grantSizeSeeking', v)}
          options={GRANT_SIZE_RANGES}
          error={errors.grantSizeSeeking}
        />
      </FormField>

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
