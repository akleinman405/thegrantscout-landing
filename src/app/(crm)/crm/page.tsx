'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

interface Meeting {
  contact: string
  orgAbbrev: string
  date: string
  notesFile: string
  orgSlug: string | null
}

interface NewClient {
  id: number
  name: string
  ein: string | null
  contact_name: string | null
  contact_email: string | null
  subscription_type: string | null
  subscription_status: string | null
  start_date: string | null
  created_at: string
}

interface DashboardData {
  reportFile: string | null
  meetings: Meeting[]
  newClients: NewClient[]
}

export default function CRMDashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/crm/dashboard')
      .then((r) => r.json())
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSkeleton />
  if (!data) return <p className="text-error">Failed to load dashboard</p>

  return (
    <div>
      <h1 className="text-2xl font-heading font-bold text-primary mb-6">Dashboard</h1>

      {/* New Clients */}
      <div className="bg-white rounded-xl shadow-card overflow-hidden mb-6">
        <div className="px-5 py-3 border-b border-gray-200 bg-gray-50 flex items-center gap-2">
          <svg viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4 text-primary">
            <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v1h8v-1zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-1a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 17v1h-3zM4.75 14.094A5.973 5.973 0 004 17v1H1v-1a3 3 0 013.75-2.906z"/>
          </svg>
          <h2 className="text-sm font-semibold text-primary-dark">New Clients</h2>
        </div>
        {!data.newClients || data.newClients.length === 0 ? (
          <p className="p-6 text-gray-medium text-sm">
            No clients yet. New signups from Stripe will appear here.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-medium border-b border-gray-100">
                  <th className="px-5 py-2 font-medium">Organization</th>
                  <th className="px-5 py-2 font-medium">Contact</th>
                  <th className="px-5 py-2 font-medium">Plan</th>
                  <th className="px-5 py-2 font-medium">Status</th>
                  <th className="px-5 py-2 font-medium">Start Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data.newClients.map((c) => {
                  const isNew = isWithinDays(c.created_at, 7)
                  return (
                    <tr key={c.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-5 py-3">
                        <Link
                          href={`/crm/orgs/${c.id}`}
                          className="text-primary font-medium hover:underline"
                        >
                          {c.name}
                        </Link>
                        {isNew && (
                          <span className="ml-2 inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700 bg-emerald-50 rounded-full px-2 py-0.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            NEW
                          </span>
                        )}
                      </td>
                      <td className="px-5 py-3">
                        <div className="text-charcoal">{c.contact_name || '\u2014'}</div>
                        {c.contact_email && (
                          <div className="text-xs text-gray-medium">{c.contact_email}</div>
                        )}
                      </td>
                      <td className="px-5 py-3 capitalize text-charcoal">
                        {c.subscription_type || '\u2014'}
                      </td>
                      <td className="px-5 py-3">
                        <StatusBadge status={c.subscription_status} />
                      </td>
                      <td className="px-5 py-3 text-gray-medium whitespace-nowrap">
                        {c.start_date ? formatDate(c.start_date) : '\u2014'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* LinkedIn Report */}
      <div className="bg-white rounded-xl shadow-card overflow-hidden mb-6">
        <div className="px-5 py-3 border-b border-gray-200 bg-gray-50">
          <h2 className="text-sm font-semibold text-primary-dark">
            Weekly LinkedIn Report
          </h2>
          {data.reportFile && (
            <p className="text-xs text-gray-medium mt-0.5">{data.reportFile}</p>
          )}
        </div>
        {data.reportFile ? (
          <iframe
            src="/api/crm/dashboard/report"
            className="w-full border-0"
            style={{ height: '70vh' }}
            title="Weekly LinkedIn Report"
            sandbox="allow-same-origin"
          />
        ) : (
          <p className="p-6 text-gray-medium text-sm">
            No LinkedIn report found. Generate one with <code>/kpi</code>.
          </p>
        )}
      </div>

      {/* Recent Meetings */}
      <div className="bg-white rounded-xl shadow-card overflow-hidden">
        <div className="px-5 py-3 border-b border-gray-200 bg-gray-50">
          <h2 className="text-sm font-semibold text-primary-dark">Recent Meetings</h2>
        </div>
        {data.meetings.length === 0 ? (
          <p className="p-4 text-gray-medium text-sm">No meetings recorded yet</p>
        ) : (
          <div className="divide-y divide-gray-100">
            {data.meetings.map((m) => (
              <div key={m.notesFile} className="px-5 py-3 flex items-center gap-4">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-charcoal">{m.contact}</p>
                  <p className="text-xs text-gray-medium">
                    {m.orgSlug ? (
                      <Link
                        href={`/crm/orgs/${m.orgSlug}`}
                        className="text-primary hover:underline"
                      >
                        {m.orgAbbrev}
                      </Link>
                    ) : (
                      m.orgAbbrev
                    )}
                  </p>
                </div>
                <time className="text-xs text-gray-medium whitespace-nowrap">
                  {formatDate(m.date)}
                </time>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function isWithinDays(dateStr: string, days: number): boolean {
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  return diff < days * 24 * 60 * 60 * 1000
}

function StatusBadge({ status }: { status: string | null }) {
  const map: Record<string, { bg: string; text: string; label: string }> = {
    active: { bg: 'bg-emerald-50', text: 'text-emerald-700', label: 'Active' },
    past_due: { bg: 'bg-amber-50', text: 'text-amber-700', label: 'Past Due' },
    canceled: { bg: 'bg-red-50', text: 'text-red-700', label: 'Canceled' },
    pending_payment: { bg: 'bg-gray-100', text: 'text-gray-600', label: 'Pending' },
  }
  const s = map[status || ''] || { bg: 'bg-gray-100', text: 'text-gray-600', label: status || '\u2014' }
  return (
    <span className={`inline-block text-xs font-medium rounded-full px-2 py-0.5 ${s.bg} ${s.text}`}>
      {s.label}
    </span>
  )
}

function LoadingSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-40 mb-6" />
      <div className="h-32 bg-white rounded-xl shadow-card mb-6" />
      <div className="h-96 bg-white rounded-xl shadow-card mb-6" />
      <div className="h-48 bg-white rounded-xl shadow-card" />
    </div>
  )
}
