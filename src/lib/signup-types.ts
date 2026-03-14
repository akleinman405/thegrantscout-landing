export interface SignupFormData {
  // Step 1: Organization
  orgName: string
  ein: string
  orgType: string
  contactName: string
  contactEmail: string

  // Step 2: Mission
  mission: string
  focusAreas: string[]
  programs: string
  populations: string[]

  // Step 3: Capacity
  state: string
  city: string
  geographicScope: string
  annualBudget: string
  grantSizeSeeking: string
  grantTypes: string[]
  grantCapacity: string

  // Step 4: Preferences
  nteeCode: string
  knownFunders: string
  timeframe: string
  additionalNotes: string

  // Step 5: Plan
  planType: 'monthly' | 'annual'
}

export const INITIAL_FORM_DATA: SignupFormData = {
  orgName: '',
  ein: '',
  orgType: '',
  contactName: '',
  contactEmail: '',
  mission: '',
  focusAreas: [],
  programs: '',
  populations: [],
  state: '',
  city: '',
  geographicScope: '',
  annualBudget: '',
  grantSizeSeeking: '',
  grantTypes: [],
  grantCapacity: '',
  nteeCode: '',
  knownFunders: '',
  timeframe: '',
  additionalNotes: '',
  planType: 'monthly',
}

export const ORG_TYPES = [
  '501(c)(3) Public Charity',
  '501(c)(3) Private Foundation',
  '501(c)(4)',
  '501(c)(6)',
  'Fiscal Sponsorship',
  'Other',
]

export const FOCUS_AREAS = [
  'Arts & Culture',
  'Education (K-12)',
  'Education (Higher Ed)',
  'Environment',
  'Health & Medicine',
  'Human Services',
  'Housing & Shelter',
  'Youth Development',
  'Senior Services',
  'Disabilities',
  'Religion',
  'Animal Welfare',
  'International',
  'Community Development',
  'Science & Technology',
  'Other',
]

export const POPULATIONS = [
  'Children & Youth (0-17)',
  'Young Adults (18-25)',
  'Adults',
  'Seniors (65+)',
  'Veterans',
  'Immigrants/Refugees',
  'People with Disabilities',
  'LGBTQ+',
  'Low-Income Communities',
  'Communities of Color',
  'Rural Communities',
  'Unhoused Individuals',
  'General Public',
  'Other',
]

export const US_STATES = [
  { value: 'AL', label: 'Alabama' }, { value: 'AK', label: 'Alaska' },
  { value: 'AZ', label: 'Arizona' }, { value: 'AR', label: 'Arkansas' },
  { value: 'CA', label: 'California' }, { value: 'CO', label: 'Colorado' },
  { value: 'CT', label: 'Connecticut' }, { value: 'DE', label: 'Delaware' },
  { value: 'DC', label: 'District of Columbia' }, { value: 'FL', label: 'Florida' },
  { value: 'GA', label: 'Georgia' }, { value: 'HI', label: 'Hawaii' },
  { value: 'ID', label: 'Idaho' }, { value: 'IL', label: 'Illinois' },
  { value: 'IN', label: 'Indiana' }, { value: 'IA', label: 'Iowa' },
  { value: 'KS', label: 'Kansas' }, { value: 'KY', label: 'Kentucky' },
  { value: 'LA', label: 'Louisiana' }, { value: 'ME', label: 'Maine' },
  { value: 'MD', label: 'Maryland' }, { value: 'MA', label: 'Massachusetts' },
  { value: 'MI', label: 'Michigan' }, { value: 'MN', label: 'Minnesota' },
  { value: 'MS', label: 'Mississippi' }, { value: 'MO', label: 'Missouri' },
  { value: 'MT', label: 'Montana' }, { value: 'NE', label: 'Nebraska' },
  { value: 'NV', label: 'Nevada' }, { value: 'NH', label: 'New Hampshire' },
  { value: 'NJ', label: 'New Jersey' }, { value: 'NM', label: 'New Mexico' },
  { value: 'NY', label: 'New York' }, { value: 'NC', label: 'North Carolina' },
  { value: 'ND', label: 'North Dakota' }, { value: 'OH', label: 'Ohio' },
  { value: 'OK', label: 'Oklahoma' }, { value: 'OR', label: 'Oregon' },
  { value: 'PA', label: 'Pennsylvania' }, { value: 'PR', label: 'Puerto Rico' },
  { value: 'RI', label: 'Rhode Island' }, { value: 'SC', label: 'South Carolina' },
  { value: 'SD', label: 'South Dakota' }, { value: 'TN', label: 'Tennessee' },
  { value: 'TX', label: 'Texas' }, { value: 'UT', label: 'Utah' },
  { value: 'VT', label: 'Vermont' }, { value: 'VA', label: 'Virginia' },
  { value: 'WA', label: 'Washington' }, { value: 'WV', label: 'West Virginia' },
  { value: 'WI', label: 'Wisconsin' }, { value: 'WY', label: 'Wyoming' },
]

export const GEOGRAPHIC_SCOPES = [
  'Local (city/county)',
  'Regional (multi-county)',
  'Statewide',
  'Multi-state/Regional',
  'National',
  'International',
]

export const BUDGET_RANGES = [
  'Under $250K',
  '$250K-$500K',
  '$500K-$1M',
  '$1M-$5M',
  '$5M-$10M',
  '$10M-$25M',
  '$25M+',
]

export const GRANT_SIZE_RANGES = [
  'Under $10K',
  '$10K-$25K',
  '$25K-$50K',
  '$50K-$100K',
  '$100K-$250K',
  '$250K-$500K',
  '$500K+',
]

export const GRANT_TYPES = [
  'General Operating Support',
  'Program/Project Grants',
  'Capital Campaigns',
  'Capacity Building',
  'Research',
  'Scholarships/Fellowships',
  'Emergency/Disaster',
  'Seed Funding',
]

export const GRANT_CAPACITIES = [
  'New to grants',
  'Some experience (1-5 grants)',
  'Experienced (5-20 grants)',
  'Highly experienced (20+ grants)',
]

export const TIMEFRAMES = [
  'ASAP (within 1 month)',
  'Short-term (1-3 months)',
  'Medium-term (3-6 months)',
  'Long-term (6-12 months)',
  'Ongoing/No rush',
]

export type StepValidationErrors = Record<string, string>

export function validateStep(step: number, data: SignupFormData): StepValidationErrors {
  const errors: StepValidationErrors = {}

  switch (step) {
    case 1: {
      if (!data.orgName || data.orgName.trim().length < 2) errors.orgName = 'Organization name is required'
      const cleanEin = data.ein.replace(/-/g, '')
      if (!cleanEin || !/^\d{9}$/.test(cleanEin)) errors.ein = 'Enter a valid 9-digit EIN'
      if (!data.orgType) errors.orgType = 'Select your organization type'
      if (!data.contactName || data.contactName.trim().length < 2) errors.contactName = 'Contact name is required'
      if (!data.contactEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.contactEmail)) errors.contactEmail = 'Enter a valid email address'
      break
    }
    case 2: {
      if (!data.mission || data.mission.trim().length < 50) errors.mission = 'Mission statement must be at least 50 characters'
      if (!data.focusAreas.length) errors.focusAreas = 'Select at least one focus area'
      if (!data.programs || data.programs.trim().length < 50) errors.programs = 'Programs description must be at least 50 characters'
      if (!data.populations.length) errors.populations = 'Select at least one population'
      break
    }
    case 3: {
      if (!data.state) errors.state = 'Select your state'
      if (!data.city || data.city.trim().length < 2) errors.city = 'City is required'
      if (!data.geographicScope) errors.geographicScope = 'Select your geographic scope'
      if (!data.annualBudget) errors.annualBudget = 'Select your annual budget range'
      if (!data.grantSizeSeeking) errors.grantSizeSeeking = 'Select grant size range'
      if (!data.grantTypes.length) errors.grantTypes = 'Select at least one grant type'
      if (!data.grantCapacity) errors.grantCapacity = 'Select your grant experience level'
      break
    }
    case 4:
      // All optional
      if (data.additionalNotes && data.additionalNotes.length > 1000) errors.additionalNotes = 'Notes must be under 1000 characters'
      break
    case 5:
      if (!data.planType) errors.planType = 'Select a plan'
      break
  }

  return errors
}
