'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

interface Person {
  id: string
  name: string
  title: string | null
  company: string | null
  email: string | null
  meeting_date: string
  org_slug: string | null
}

export default function PeoplePage() {
  const [people, setPeople] = useState<Person[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(true)
      fetch(`/api/crm/people?q=${encodeURIComponent(search)}`)
        .then((r) => r.json())
        .then((d) => setPeople(d.people || []))
        .catch(console.error)
        .finally(() => setLoading(false))
    }, 300)
    return () => clearTimeout(timer)
  }, [search])

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-heading font-bold text-primary">People</h1>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name or company..."
          className="px-4 py-2 border border-gray-200 rounded-lg text-sm w-72 focus:outline-none focus:ring-2 focus:ring-primary/30"
        />
      </div>

      <div className="bg-white rounded-xl shadow-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="text-left text-xs font-medium text-gray-medium px-4 py-3">Name</th>
              <th className="text-left text-xs font-medium text-gray-medium px-4 py-3">Title</th>
              <th className="text-left text-xs font-medium text-gray-medium px-4 py-3">Company</th>
              <th className="text-left text-xs font-medium text-gray-medium px-4 py-3">Email</th>
              <th className="text-left text-xs font-medium text-gray-medium px-4 py-3">Meeting Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <tr key={i}>
                  <td colSpan={5} className="px-4 py-3">
                    <div className="h-4 bg-gray-100 rounded animate-pulse" />
                  </td>
                </tr>
              ))
            ) : people.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-medium text-sm">
                  No people found
                </td>
              </tr>
            ) : (
              people.map((p) => (
                <tr key={p.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <Link
                      href={`/crm/people/${p.id}`}
                      className="text-sm font-medium text-charcoal hover:text-primary"
                    >
                      {p.name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-medium">{p.title || '--'}</td>
                  <td className="px-4 py-3">
                    {p.org_slug ? (
                      <Link
                        href={`/crm/orgs/${p.org_slug}`}
                        className="text-sm text-charcoal hover:text-primary"
                      >
                        {p.company || '--'}
                      </Link>
                    ) : (
                      <span className="text-sm text-gray-medium">{p.company || '--'}</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-medium">{p.email || '--'}</td>
                  <td className="px-4 py-3 text-sm text-gray-medium">
                    {new Date(p.meeting_date + 'T00:00:00').toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                    })}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
