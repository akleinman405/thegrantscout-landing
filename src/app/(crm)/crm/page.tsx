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

interface DashboardData {
  reportFile: string | null
  meetings: Meeting[]
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

function LoadingSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-40 mb-6" />
      <div className="h-96 bg-white rounded-xl shadow-card mb-6" />
      <div className="h-48 bg-white rounded-xl shadow-card" />
    </div>
  )
}
