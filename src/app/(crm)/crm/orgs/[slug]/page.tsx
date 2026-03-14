'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'

interface OrgData {
  slug: string
  name: string
  hasBrief: boolean
}

export default function OrgProfilePage() {
  const { slug } = useParams<{ slug: string }>()
  const [data, setData] = useState<OrgData | null>(null)
  const [loading, setLoading] = useState(true)
  const [briefHtml, setBriefHtml] = useState<string | null>(null)

  useEffect(() => {
    fetch(`/api/crm/orgs/${slug}`)
      .then((r) => r.json())
      .then((d) => {
        setData(d)
        // Auto-load brief
        if (d.hasBrief) {
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

  if (!data || data.slug === undefined) {
    return <p className="text-error">Organization not found</p>
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-heading font-bold text-primary">{data.name}</h1>
      </div>

      {/* Viability Brief */}
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
