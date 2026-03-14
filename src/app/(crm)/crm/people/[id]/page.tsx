'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

interface PersonData {
  person: {
    name: string
    title: string | null
    company: string | null
    email: string | null
    phone: string | null
    linkedinUrl: string | null
    website: string | null
  }
  meeting: {
    date: string
    orgAbbrev: string
    orgSlug: string | null
  }
  notes: string | null
}

export default function PersonProfilePage() {
  const { id } = useParams<{ id: string }>()
  const [data, setData] = useState<PersonData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`/api/crm/people/${id}`)
      .then((r) => r.json())
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-48 mb-4" />
        <div className="h-32 bg-white rounded-xl shadow-card" />
      </div>
    )
  }

  if (!data || !data.person) {
    return <p className="text-error">Person not found</p>
  }

  const { person, meeting, notes } = data

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-heading font-bold text-primary">{person.name}</h1>
        <p className="text-sm text-gray-medium">
          {person.title && `${person.title} | `}
          {meeting.orgSlug ? (
            <Link href={`/crm/orgs/${meeting.orgSlug}`} className="text-primary hover:underline">
              {person.company || meeting.orgAbbrev}
            </Link>
          ) : (
            person.company || meeting.orgAbbrev
          )}
        </p>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Left column: contact info + meeting notes */}
        <div className="col-span-2 space-y-6">
          {/* Contact Info */}
          <div className="bg-white rounded-xl shadow-card p-5">
            <h3 className="text-sm font-semibold text-primary-dark mb-3">Contact Info</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-medium">Email:</span>{' '}
                <span className="text-charcoal">
                  {person.email ? (
                    <a href={`mailto:${person.email}`} className="text-primary hover:underline">
                      {person.email}
                    </a>
                  ) : (
                    'Not available'
                  )}
                </span>
              </div>
              <div>
                <span className="text-gray-medium">Phone:</span>{' '}
                <span className="text-charcoal">{person.phone || 'Not available'}</span>
              </div>
              <div>
                <span className="text-gray-medium">LinkedIn:</span>{' '}
                <span className="text-charcoal">
                  {person.linkedinUrl ? (
                    <a
                      href={person.linkedinUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline"
                    >
                      Profile
                    </a>
                  ) : (
                    'Not available'
                  )}
                </span>
              </div>
              <div>
                <span className="text-gray-medium">Meeting:</span>{' '}
                <span className="text-charcoal">
                  {new Date(meeting.date + 'T00:00:00').toLocaleDateString('en-US', {
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </span>
              </div>
            </div>
          </div>

          {/* Meeting Notes */}
          <div className="bg-white rounded-xl shadow-card p-5">
            <h3 className="text-sm font-semibold text-primary-dark mb-3">Meeting Notes</h3>
            {notes ? (
              <div className="text-sm text-charcoal leading-relaxed whitespace-pre-wrap">
                {notes}
              </div>
            ) : (
              <p className="text-gray-medium text-sm">No notes available</p>
            )}
          </div>
        </div>

        {/* Right column */}
        <div className="space-y-6">
          {person.website && (
            <div className="bg-white rounded-xl shadow-card p-5">
              <h3 className="text-sm font-semibold text-primary-dark mb-3">Company</h3>
              <a
                href={person.website.startsWith('http') ? person.website : `https://${person.website}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary hover:underline"
              >
                {person.website}
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
