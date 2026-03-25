'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

interface BriefData {
  source: 'brief'
  slug: string
  name: string
  hasBrief: boolean
}

interface SupabaseOrg {
  id: number
  ein: string | null
  name: string
  type: string
  stage: string | null
  city: string | null
  state: string | null
  website: string | null
  phone: string | null
  mission_text: string | null
  contact_name: string | null
  contact_email: string | null
  subscription_type: string | null
  subscription_status: string | null
  start_date: string | null
  next_payment_date: string | null
  stripe_customer_id: string | null
  created_at: string
}

interface Subscriber {
  org_name: string
  ein: string
  contact_name: string
  contact_email: string
  mission: string | null
  focus_areas: string[] | null
  programs: string | null
  populations: string[] | null
  geographic_scope: string | null
  locations: Array<{ type: string; state: string; detail: string }> | null
  annual_budget: string | null
  grant_size_seeking: string | null
  grant_types: string[] | null
  grant_capacity: string | null
  known_funders: string | null
  additional_notes: string | null
  plan_type: string
  subscription_status: string
  created_at: string
}

interface SupabaseData {
  source: 'supabase'
  org: SupabaseOrg
  subscriber: Subscriber | null
}

type OrgResponse = BriefData | SupabaseData | { error: string }

export default function OrgProfilePage() {
  const { slug } = useParams<{ slug: string }>()
  const [data, setData] = useState<OrgResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [briefHtml, setBriefHtml] = useState<string | null>(null)

  useEffect(() => {
    fetch(`/api/crm/orgs/${slug}`)
      .then((r) => r.json())
      .then((d: OrgResponse) => {
        setData(d)
        if ('source' in d && d.source === 'brief' && d.hasBrief) {
          fetch(`/api/crm/orgs/${slug}/brief`)
            .then((r) => (r.ok ? r.text() : null))
            .then(setBriefHtml)
            .catch(console.error)
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [slug])

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-64 mb-4" />
        <div className="h-96 bg-white rounded-xl shadow-card" />
      </div>
    )
  }

  if (!data || 'error' in data) {
    return <p className="text-error">Organization not found</p>
  }

  // Supabase client profile
  if (data.source === 'supabase') {
    return <ClientProfile org={data.org} subscriber={data.subscriber} />
  }

  // Filesystem brief
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-heading font-bold text-primary">{data.name}</h1>
      </div>
      <div className="bg-white rounded-xl shadow-card p-1 overflow-hidden">
        {briefHtml ? (
          <iframe
            srcDoc={briefHtml}
            className="w-full border-0 rounded-lg"
            style={{ height: '85vh' }}
            title="Viability Brief"
            sandbox="allow-same-origin"
          />
        ) : (
          <p className="p-6 text-gray-medium text-sm">Loading brief...</p>
        )}
      </div>
    </div>
  )
}

const US_STATES: Record<string, string> = {
  AL:'Alabama',AK:'Alaska',AZ:'Arizona',AR:'Arkansas',CA:'California',CO:'Colorado',
  CT:'Connecticut',DE:'Delaware',DC:'District of Columbia',FL:'Florida',GA:'Georgia',
  HI:'Hawaii',ID:'Idaho',IL:'Illinois',IN:'Indiana',IA:'Iowa',KS:'Kansas',KY:'Kentucky',
  LA:'Louisiana',ME:'Maine',MD:'Maryland',MA:'Massachusetts',MI:'Michigan',MN:'Minnesota',
  MS:'Mississippi',MO:'Missouri',MT:'Montana',NE:'Nebraska',NV:'Nevada',NH:'New Hampshire',
  NJ:'New Jersey',NM:'New Mexico',NY:'New York',NC:'North Carolina',ND:'North Dakota',
  OH:'Ohio',OK:'Oklahoma',OR:'Oregon',PA:'Pennsylvania',PR:'Puerto Rico',RI:'Rhode Island',
  SC:'South Carolina',SD:'South Dakota',TN:'Tennessee',TX:'Texas',UT:'Utah',VT:'Vermont',
  VA:'Virginia',WA:'Washington',WV:'West Virginia',WI:'Wisconsin',WY:'Wyoming',
}

function ClientProfile({ org, subscriber }: { org: SupabaseOrg; subscriber: Subscriber | null }) {
  const sub = subscriber

  function formatLocations(locs: Array<{ type: string; state: string; detail: string }> | null | undefined): string {
    if (!locs || locs.length === 0) return 'Not specified'
    return locs.map((l) => {
      const stateName = US_STATES[l.state] || l.state
      return l.type === 'state' ? stateName : `${l.detail}, ${stateName}`
    }).join('; ')
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-heading font-bold text-primary">{org.name}</h1>
          <div className="flex items-center gap-3 mt-1 text-sm text-gray-medium">
            {org.ein && <span>EIN: {org.ein}</span>}
            {org.city && org.state && <span>{org.city}, {org.state}</span>}
          </div>
        </div>
        <SubscriptionBadge status={org.subscription_status} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Contact & Subscription */}
        <div className="bg-white rounded-xl shadow-card overflow-hidden">
          <div className="px-5 py-3 border-b border-gray-200 bg-gray-50">
            <h2 className="text-sm font-semibold text-primary-dark">Contact & Subscription</h2>
          </div>
          <div className="p-5 space-y-3 text-sm">
            <InfoRow label="Contact" value={org.contact_name} />
            <InfoRow label="Email" value={org.contact_email} isEmail />
            {org.phone && <InfoRow label="Phone" value={org.phone} />}
            {org.website && <InfoRow label="Website" value={org.website} isLink />}
            <div className="border-t border-gray-100 pt-3 mt-3" />
            <InfoRow label="Plan" value={org.subscription_type ? `${org.subscription_type.charAt(0).toUpperCase()}${org.subscription_type.slice(1)}` : null} />
            <InfoRow label="Start Date" value={org.start_date ? formatDate(org.start_date) : null} />
            <InfoRow label="Next Payment" value={org.next_payment_date ? formatDate(org.next_payment_date) : null} />
            <InfoRow label="Signed Up" value={formatDate(org.created_at.split('T')[0])} />
          </div>
        </div>

        {/* Mission & Programs */}
        <div className="bg-white rounded-xl shadow-card overflow-hidden">
          <div className="px-5 py-3 border-b border-gray-200 bg-gray-50">
            <h2 className="text-sm font-semibold text-primary-dark">Mission & Programs</h2>
          </div>
          <div className="p-5 space-y-3 text-sm">
            {sub?.mission ? (
              <div>
                <span className="text-gray-medium text-xs uppercase tracking-wide">Mission</span>
                <p className="text-charcoal mt-1">{sub.mission}</p>
              </div>
            ) : org.mission_text ? (
              <div>
                <span className="text-gray-medium text-xs uppercase tracking-wide">Mission</span>
                <p className="text-charcoal mt-1">{org.mission_text}</p>
              </div>
            ) : null}
            {sub?.programs && (
              <div>
                <span className="text-gray-medium text-xs uppercase tracking-wide">Programs</span>
                <p className="text-charcoal mt-1">{sub.programs}</p>
              </div>
            )}
            {sub?.focus_areas && sub.focus_areas.length > 0 && (
              <div>
                <span className="text-gray-medium text-xs uppercase tracking-wide">Focus Areas</span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {sub.focus_areas.map((a) => (
                    <span key={a} className="bg-blue-50 text-primary text-xs rounded-full px-2.5 py-0.5">{a}</span>
                  ))}
                </div>
              </div>
            )}
            {sub?.populations && sub.populations.length > 0 && (
              <div>
                <span className="text-gray-medium text-xs uppercase tracking-wide">Populations Served</span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {sub.populations.map((p) => (
                    <span key={p} className="bg-purple-50 text-purple-700 text-xs rounded-full px-2.5 py-0.5">{p}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Geography & Capacity */}
        <div className="bg-white rounded-xl shadow-card overflow-hidden">
          <div className="px-5 py-3 border-b border-gray-200 bg-gray-50">
            <h2 className="text-sm font-semibold text-primary-dark">Geography & Capacity</h2>
          </div>
          <div className="p-5 space-y-3 text-sm">
            {sub && (
              <>
                <InfoRow label="Geographic Scope" value={sub.geographic_scope} />
                <InfoRow label="Locations" value={formatLocations(sub.locations)} />
                <InfoRow label="Annual Budget" value={sub.annual_budget} />
                <InfoRow label="Grant Size Seeking" value={sub.grant_size_seeking} />
                <InfoRow label="Grant Capacity" value={sub.grant_capacity} />
                {sub.grant_types && sub.grant_types.length > 0 && (
                  <div>
                    <span className="text-gray-medium text-xs uppercase tracking-wide">Grant Types</span>
                    <div className="flex flex-wrap gap-1.5 mt-1">
                      {sub.grant_types.map((t) => (
                        <span key={t} className="bg-amber-50 text-amber-700 text-xs rounded-full px-2.5 py-0.5">{t}</span>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
            {!sub && (
              <p className="text-gray-medium">No questionnaire data available yet.</p>
            )}
          </div>
        </div>

        {/* Additional Info */}
        <div className="bg-white rounded-xl shadow-card overflow-hidden">
          <div className="px-5 py-3 border-b border-gray-200 bg-gray-50">
            <h2 className="text-sm font-semibold text-primary-dark">Additional Info</h2>
          </div>
          <div className="p-5 space-y-3 text-sm">
            {sub?.known_funders && (
              <div>
                <span className="text-gray-medium text-xs uppercase tracking-wide">Known Funders</span>
                <p className="text-charcoal mt-1">{sub.known_funders}</p>
              </div>
            )}
            {sub?.additional_notes && (
              <div>
                <span className="text-gray-medium text-xs uppercase tracking-wide">Notes</span>
                <p className="text-charcoal mt-1">{sub.additional_notes}</p>
              </div>
            )}
            {!sub?.known_funders && !sub?.additional_notes && (
              <p className="text-gray-medium">No additional information.</p>
            )}
          </div>
        </div>
      </div>

      {/* Back link */}
      <div className="mt-6">
        <Link href="/crm" className="text-sm text-primary hover:underline">
          &larr; Back to Dashboard
        </Link>
      </div>
    </div>
  )
}

function InfoRow({ label, value, isEmail, isLink }: { label: string; value: string | null | undefined; isEmail?: boolean; isLink?: boolean }) {
  if (!value) return (
    <div className="flex justify-between">
      <span className="text-gray-medium">{label}</span>
      <span className="text-gray-300">{'\u2014'}</span>
    </div>
  )
  return (
    <div className="flex justify-between">
      <span className="text-gray-medium">{label}</span>
      {isEmail ? (
        <a href={`mailto:${value}`} className="text-primary hover:underline">{value}</a>
      ) : isLink ? (
        <a href={value.startsWith('http') ? value : `https://${value}`} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline truncate max-w-[200px]">{value}</a>
      ) : (
        <span className="text-charcoal">{value}</span>
      )}
    </div>
  )
}

function SubscriptionBadge({ status }: { status: string | null }) {
  const map: Record<string, { bg: string; text: string; label: string }> = {
    active: { bg: 'bg-emerald-50 border-emerald-200', text: 'text-emerald-700', label: 'Active Subscriber' },
    past_due: { bg: 'bg-amber-50 border-amber-200', text: 'text-amber-700', label: 'Past Due' },
    canceled: { bg: 'bg-red-50 border-red-200', text: 'text-red-700', label: 'Canceled' },
    pending_payment: { bg: 'bg-gray-100 border-gray-200', text: 'text-gray-600', label: 'Pending Payment' },
  }
  const s = map[status || ''] || { bg: 'bg-gray-100 border-gray-200', text: 'text-gray-600', label: status || 'Unknown' }
  return (
    <span className={`inline-flex items-center text-xs font-semibold rounded-full px-3 py-1 border ${s.bg} ${s.text}`}>
      {s.label}
    </span>
  )
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
