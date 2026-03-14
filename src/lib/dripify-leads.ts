import { readFileSync } from 'fs'

const CSV_PATH = '/Users/aleckleinman/Documents/TheGrantScout/4. Sales/2. Linkedin/Campaign/LeadsFromDripify.csv'

export interface DripifyLead {
  firstName: string
  lastName: string
  email: string | null
  phone: string | null
  title: string | null
  company: string | null
  linkedinUrl: string | null
  website: string | null
  lastAction: string | null
}

let cachedLeads: DripifyLead[] | null = null

function parseCSV(): DripifyLead[] {
  if (cachedLeads) return cachedLeads

  let content: string
  try {
    content = readFileSync(CSV_PATH, 'utf-8')
  } catch {
    cachedLeads = []
    return cachedLeads
  }

  const lines = content.split('\n').filter((l) => l.trim())
  if (lines.length < 2) {
    cachedLeads = []
    return cachedLeads
  }

  // Simple CSV parse (no quoted commas expected in this data)
  const rows = lines.slice(1)
  cachedLeads = rows.map((line) => {
    const cols = line.split(',')
    return {
      firstName: cols[0]?.trim() || '',
      lastName: cols[1]?.trim() || '',
      email: cols[2]?.trim() || cols[3]?.trim() || cols[4]?.trim() || null,
      phone: cols[5]?.trim() || null,
      title: cols[6]?.trim() || null,
      company: cols[7]?.trim() || null,
      linkedinUrl: cols[13]?.trim() || cols[9]?.trim() || null, // prefer public URL
      website: cols[12]?.trim() || null,
      lastAction: cols[10]?.trim() || null,
    }
  })

  return cachedLeads
}

export function getAllLeads(): DripifyLead[] {
  return parseCSV()
}

export function findLead(firstName: string): DripifyLead | null {
  const leads = parseCSV()
  const normalized = firstName.toLowerCase().trim()
  return leads.find((l) => l.firstName.toLowerCase() === normalized) || null
}
