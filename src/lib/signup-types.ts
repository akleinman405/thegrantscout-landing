export interface LocationEntry {
  type: 'city' | 'state' | 'county'
  state: string
  detail: string // city name, county name, or empty for state-wide
}

export interface ReportRecipient {
  name: string
  email: string
  focus: string // e.g., "relationship building", "open opportunities"
}

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
  locations: LocationEntry[]
  geographicScope: string
  annualBudget: string
  grantSizeSeeking: string[]
  grantTypes: string[]
  grantCapacity: string

  // Step 4: Preferences
  knownFunders: string
  reportCount: number
  reportRecipients: ReportRecipient[]
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
  locations: [],
  geographicScope: '',
  annualBudget: '',
  grantSizeSeeking: [],
  grantTypes: [],
  grantCapacity: '',
  knownFunders: '',
  reportCount: 1,
  reportRecipients: [{ name: '', email: '', focus: '' }],
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

export const REPORT_COUNT_OPTIONS = [1, 2, 3, 4, 5]

export const LOCATION_TYPES = [
  { value: 'city', label: 'City' },
  { value: 'county', label: 'County' },
  { value: 'state', label: 'Entire State' },
]

export const PREVIEW_FORM_DATA: SignupFormData = {
  orgName: 'Habitat for Humanity International',
  ein: '912167871',
  orgType: '501(c)(3) Public Charity',
  contactName: 'Jane Smith',
  contactEmail: 'jane.smith@habitat.org',
  mission: 'Seeking to put God\'s love into action, Habitat for Humanity brings people together to build homes, communities and hope. Through volunteer labor and donations of money and materials, Habitat builds and rehabilitates simple, decent houses with the help of the homeowner (partner) families.',
  focusAreas: ['Housing & Shelter', 'Community Development', 'Human Services'],
  programs: 'Habitat for Humanity builds affordable housing through volunteer construction programs, neighborhood revitalization efforts, and the ReStore home improvement retail operation. We also provide homeowner education, financial literacy training, and disaster response rebuilding services in communities across all 50 states and 70+ countries.',
  populations: ['Low-Income Communities', 'Adults', 'Children & Youth (0-17)'],
  locations: [
    { type: 'city', state: 'GA', detail: 'Atlanta' },
    { type: 'state', state: 'GA', detail: '' },
    { type: 'county', state: 'NC', detail: 'Mecklenburg County' },
  ],
  geographicScope: 'National',
  annualBudget: '$25M+',
  grantSizeSeeking: ['$100K-$250K', '$250K-$500K'],
  grantTypes: ['General Operating Support', 'Program/Project Grants', 'Capital Campaigns'],
  grantCapacity: 'Highly experienced (20+ grants)',
  knownFunders: 'The Home Depot Foundation, Wells Fargo Foundation, Whirlpool Foundation',
  reportCount: 2,
  reportRecipients: [
    { name: 'Jane Smith', email: 'jane.smith@habitat.org', focus: 'Relationship building with new corporate foundations' },
    { name: 'Tom Rivera', email: 'tom.rivera@habitat.org', focus: 'Open grant opportunities for capital campaigns' },
  ],
  additionalNotes: 'Interested in expanding corporate foundation partnerships for our neighborhood revitalization initiative.',
  planType: 'annual',
}

// Coerce a partial/untrusted form payload (from localStorage or a Supabase draft row)
// into a fully-populated SignupFormData. Drafts can legitimately contain nulls or
// missing keys — e.g. form_data JSONB that was written before a field existed, or
// nullable string columns that echo back as null. Spreading those over
// INITIAL_FORM_DATA overrides the defaults with null, which crashes steps that
// call `.length`, `.map`, or `.includes` on array fields.
export function normalizeFormData(partial: Partial<SignupFormData> | null | undefined): SignupFormData {
  const p = (partial ?? {}) as Partial<SignupFormData>
  const asArray = <T,>(v: unknown, fallback: T[]): T[] => (Array.isArray(v) ? (v as T[]) : fallback)
  const asString = (v: unknown): string => (typeof v === 'string' ? v : '')

  const count =
    typeof p.reportCount === 'number' && p.reportCount >= 1 ? Math.floor(p.reportCount) : 1
  const recipients = asArray<ReportRecipient>(p.reportRecipients, []).map((r) => ({
    name: asString(r?.name),
    email: asString(r?.email),
    focus: asString(r?.focus),
  }))
  const sizedRecipients =
    recipients.length >= 1
      ? recipients
      : [{ name: '', email: '', focus: '' }]

  return {
    ...INITIAL_FORM_DATA,
    ...p,
    orgName: asString(p.orgName),
    ein: asString(p.ein),
    orgType: asString(p.orgType),
    contactName: asString(p.contactName),
    contactEmail: asString(p.contactEmail),
    mission: asString(p.mission),
    focusAreas: asArray<string>(p.focusAreas, []),
    programs: asString(p.programs),
    populations: asArray<string>(p.populations, []),
    locations: asArray<LocationEntry>(p.locations, []),
    geographicScope: asString(p.geographicScope),
    annualBudget: asString(p.annualBudget),
    grantSizeSeeking: asArray<string>(p.grantSizeSeeking, []),
    grantTypes: asArray<string>(p.grantTypes, []),
    grantCapacity: asString(p.grantCapacity),
    knownFunders: asString(p.knownFunders),
    reportCount: count,
    reportRecipients: sizedRecipients,
    additionalNotes: asString(p.additionalNotes),
    planType: p.planType === 'annual' ? 'annual' : 'monthly',
  }
}

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
      if (!data.locations.length) errors.locations = 'Add at least one location'
      if (!data.geographicScope) errors.geographicScope = 'Select your geographic scope'
      if (!data.annualBudget) errors.annualBudget = 'Select your annual budget range'
      if (!data.grantSizeSeeking.length) errors.grantSizeSeeking = 'Select at least one grant size range'
      if (!data.grantTypes.length) errors.grantTypes = 'Select at least one grant type'
      if (!data.grantCapacity) errors.grantCapacity = 'Select your grant experience level'
      break
    }
    case 4:
      if (data.additionalNotes && data.additionalNotes.length > 1000) errors.additionalNotes = 'Notes must be under 1000 characters'
      break
    case 5:
      if (!data.planType) errors.planType = 'Select a plan'
      break
  }

  return errors
}
