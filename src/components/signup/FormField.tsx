'use client'

import { ReactNode } from 'react'

interface FormFieldProps {
  label: string
  error?: string
  required?: boolean
  hint?: string
  children: ReactNode
}

export default function FormField({ label, error, required, hint, children }: FormFieldProps) {
  return (
    <div className="mb-5">
      <label className="block text-sm font-semibold text-primary mb-1.5">
        {label}
        {required && <span className="text-error ml-1">*</span>}
      </label>
      {hint && <p className="text-xs text-gray-medium mb-1.5">{hint}</p>}
      {children}
      {error && <p className="text-error text-sm mt-1">{error}</p>}
    </div>
  )
}

interface TextInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  type?: string
  error?: string
}

export function TextInput({ value, onChange, placeholder, type = 'text', error }: TextInputProps) {
  return (
    <input
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className={`form-input-mobile ${error ? 'border-error' : ''}`}
    />
  )
}

interface TextAreaProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  rows?: number
  error?: string
  maxLength?: number
}

export function TextArea({ value, onChange, placeholder, rows = 4, error, maxLength }: TextAreaProps) {
  return (
    <div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={rows}
        maxLength={maxLength}
        className={`form-textarea-mobile ${error ? 'border-error' : ''}`}
      />
      {maxLength && (
        <p className="text-xs text-gray-medium mt-1 text-right">{value.length}/{maxLength}</p>
      )}
    </div>
  )
}

interface SelectProps {
  value: string
  onChange: (value: string) => void
  options: string[] | { value: string; label: string }[]
  placeholder?: string
  error?: string
}

export function Select({ value, onChange, options, placeholder, error }: SelectProps) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={`form-input-mobile ${error ? 'border-error' : ''} ${!value ? 'text-gray-400' : ''}`}
    >
      <option value="">{placeholder || 'Select...'}</option>
      {options.map((opt) => {
        const optValue = typeof opt === 'string' ? opt : opt.value
        const optLabel = typeof opt === 'string' ? opt : opt.label
        return (
          <option key={optValue} value={optValue}>
            {optLabel}
          </option>
        )
      })}
    </select>
  )
}

interface MultiSelectProps {
  selected: string[]
  onChange: (selected: string[]) => void
  options: string[]
  error?: string
}

export function MultiSelect({ selected, onChange, options, error }: MultiSelectProps) {
  const hasOtherOption = options.includes('Other')
  // "Other" is active if any selected value isn't in the predefined options
  const otherCustomValue = selected.find((s) => !options.includes(s)) || ''
  const isOtherActive = selected.includes('Other') || !!otherCustomValue

  const toggle = (option: string) => {
    if (option === 'Other') {
      if (isOtherActive) {
        // Remove "Other" and any custom value
        onChange(selected.filter((s) => s !== 'Other' && options.includes(s)))
      } else {
        onChange([...selected, 'Other'])
      }
    } else if (selected.includes(option)) {
      onChange(selected.filter((s) => s !== option))
    } else {
      onChange([...selected, option])
    }
  }

  const handleOtherText = (text: string) => {
    // Remove old custom value and "Other" marker, add new custom text
    const base = selected.filter((s) => s !== 'Other' && options.includes(s))
    if (text.trim()) {
      onChange([...base, text.trim()])
    } else {
      onChange([...base, 'Other'])
    }
  }

  return (
    <div>
      <div className={`flex flex-wrap gap-2 ${error ? 'ring-2 ring-error/20 rounded-lg p-2' : ''}`}>
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => toggle(option)}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-all border-2 ${
              option === 'Other'
                ? isOtherActive
                  ? 'bg-primary text-white border-primary'
                  : 'bg-white text-charcoal border-gray-200 hover:border-primary/40'
                : selected.includes(option)
                  ? 'bg-primary text-white border-primary'
                  : 'bg-white text-charcoal border-gray-200 hover:border-primary/40'
            }`}
          >
            {option}
          </button>
        ))}
      </div>
      {hasOtherOption && isOtherActive && (
        <input
          type="text"
          value={otherCustomValue}
          onChange={(e) => handleOtherText(e.target.value)}
          placeholder="Please specify..."
          className="form-input-mobile mt-2"
          autoFocus
        />
      )}
    </div>
  )
}
