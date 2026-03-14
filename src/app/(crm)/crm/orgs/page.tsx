'use client'

import { useEffect, useState, useRef, useCallback } from 'react'
import Link from 'next/link'
import { supabase } from '@/lib/supabase'

// ============================================================
// Types
// ============================================================

interface Org {
  id: number
  ein: string | null
  name: string
  type: 'client' | 'lead' | 'nonprofit' | 'funder'
  stage: string | null
  city: string | null
  state: string | null
  website: string | null
  phone: string | null
  ntee_code: string | null
  assets: number | null
  annual_giving: number | null
  mission_text: string | null
  // Stripe / subscription
  stripe_customer_id: string | null
  stripe_subscription_id: string | null
  subscription_type: 'monthly' | 'quarterly' | 'annual' | null
  subscription_status: 'active' | 'past_due' | 'canceled' | 'pending_payment' | null
  start_date: string | null
  next_payment_date: string | null
  // Contact / follow-up
  contact_name: string | null
  contact_email: string | null
  last_contact_date: string | null
  next_followup_date: string | null
  next_followup_note: string | null
  // Financial / reports
  revenue: number | null
  reports_sent_count: number | null
}

type TabName = 'clients' | 'leads' | 'nonprofits' | 'funders'

// ============================================================
// Formatting helpers
// ============================================================

function formatCurrency(n: number | null): string {
  if (n == null) return '—'
  if (n >= 1_000_000_000) return `$${(n / 1_000_000_000).toFixed(1)}B`
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `$${(n / 1_000).toFixed(0)}K`
  return `$${n.toLocaleString()}`
}

function formatDate(d: string | null): string {
  if (!d) return '—'
  const date = new Date(d + 'T12:00:00')
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

// ============================================================
// Badge component
// ============================================================

function Badge({ label, variant }: { label: string; variant: string }) {
  return <span className={`badge ${variant}`}>{label}</span>
}

function HealthBadge({ status }: { status: string }) {
  const statusMap: Record<string, { dot: string; label: string }> = {
    active: { dot: 'green', label: 'Active' },
    past_due: { dot: 'yellow', label: 'Past Due' },
    canceled: { dot: 'red', label: 'Canceled' },
    pending_payment: { dot: 'yellow', label: 'Pending' },
    current: { dot: 'green', label: 'Current' },
    paused: { dot: 'yellow', label: 'Paused' },
  }
  const info = statusMap[status] || { dot: 'green', label: status.charAt(0).toUpperCase() + status.slice(1) }
  return (
    <span className={`badge ${status}`}>
      <span className={`health-dot ${info.dot}`} />
      {info.label}
    </span>
  )
}

// ============================================================
// Stage Dropdown (for Leads)
// ============================================================

const STAGE_OPTIONS = [
  { css: 'interested', label: 'Interested', color: '#5a9e7c' },
  { css: 'meeting-scheduled', label: 'Meeting Scheduled', color: '#4a7fb5' },
  { css: 'reviewing', label: 'Reviewing', color: '#b8943e' },
  { css: 'not-interested', label: 'Not Interested', color: '#b86b53' },
]

function StageDropdown({ stage, onChange }: { stage: string; onChange: (s: string) => void }) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('click', handleClick)
    return () => document.removeEventListener('click', handleClick)
  }, [])

  return (
    <div className="stage-cell" ref={ref}>
      <span
        className={`badge ${stage} clickable`}
        onClick={(e) => { e.stopPropagation(); setOpen(!open) }}
      >
        {STAGE_OPTIONS.find(o => o.css === stage)?.label || stage}
      </span>
      {open && (
        <div className="stage-dropdown show">
          {STAGE_OPTIONS.map(o => (
            <div
              key={o.css}
              className="stage-option"
              onClick={(e) => { e.stopPropagation(); onChange(o.css); setOpen(false) }}
            >
              <span className="option-dot" style={{ background: o.color }} />
              {o.label}
            </div>
          ))}
          <div className="stage-divider" />
          <div
            className="stage-option convert"
            onClick={(e) => { e.stopPropagation(); onChange('converted'); setOpen(false) }}
          >
            &#10003; Convert to Client
          </div>
        </div>
      )}
    </div>
  )
}

// ============================================================
// Search Autocomplete
// ============================================================

function SearchAutocomplete({ orgs }: { orgs: Org[] }) {
  const [query, setQuery] = useState('')
  const [showResults, setShowResults] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setShowResults(false)
    }
    document.addEventListener('click', handleClick)
    return () => document.removeEventListener('click', handleClick)
  }, [])

  const filtered = query.length > 0
    ? orgs.filter(o => o.name.toLowerCase().includes(query.toLowerCase())).slice(0, 8)
    : []

  return (
    <div className="crm-search-bar" ref={ref}>
      <input
        type="text"
        className="crm-search-input"
        placeholder="Search organizations..."
        value={query}
        onChange={(e) => { setQuery(e.target.value); setShowResults(true) }}
        onFocus={() => { if (query) setShowResults(true) }}
      />
      {showResults && query && (
        <div className="crm-search-results show">
          {filtered.length === 0 ? (
            <div className="search-no-results">No results for &ldquo;{query}&rdquo;</div>
          ) : (
            filtered.map(o => (
              <Link
                key={o.id}
                href={o.type === 'funder' ? `/crm/funders/${o.id}` : `/crm/orgs/${o.id}`}
                className="search-result-item"
                onClick={() => setShowResults(false)}
                style={{ textDecoration: 'none' }}
              >
                <div style={{ flex: 1 }}>
                  <div className="sr-name">{o.name}</div>
                  <div className="sr-meta">{o.state}{o.ntee_code ? ` · ${o.ntee_code}` : ''}</div>
                </div>
                <span className={`sr-type ${o.type}`}>{o.type}</span>
              </Link>
            ))
          )}
        </div>
      )}
    </div>
  )
}

// ============================================================
// Sort helpers
// ============================================================

type SortDir = 'asc' | 'desc' | null
type SortKey = { col: string; dir: SortDir }

function useSortableTable<T>(data: T[], defaultSort?: SortKey) {
  const [sort, setSort] = useState<SortKey>(defaultSort || { col: '', dir: null })

  const toggleSort = useCallback((col: string) => {
    setSort(prev => {
      if (prev.col !== col) return { col, dir: 'asc' }
      if (prev.dir === 'asc') return { col, dir: 'desc' }
      return { col: '', dir: null }
    })
  }, [])

  const sorted = [...data].sort((a, b) => {
    if (!sort.col || !sort.dir) return 0
    const va = (a as Record<string, unknown>)[sort.col]
    const vb = (b as Record<string, unknown>)[sort.col]
    if (va == null && vb == null) return 0
    if (va == null) return 1
    if (vb == null) return -1
    const cmp = typeof va === 'number' && typeof vb === 'number'
      ? va - vb
      : String(va).localeCompare(String(vb))
    return sort.dir === 'asc' ? cmp : -cmp
  })

  return { sorted, sort, toggleSort }
}

function SortArrow({ col, sort }: { col: string; sort: SortKey }) {
  const cls = sort.col === col ? (sort.dir === 'asc' ? 'sort-asc' : 'sort-desc') : ''
  return <span className={`sort-arrow ${cls}`}>&#9650;&#9660;</span>
}

// ============================================================
// Table Components per Tab
// ============================================================

function ClientsTable({ orgs }: { orgs: Org[] }) {
  const { sorted, sort, toggleSort } = useSortableTable(orgs, { col: 'name', dir: 'asc' })

  return (
    <table className="org-table">
      <thead>
        <tr>
          <th onClick={() => toggleSort('name')}>Organization <SortArrow col="name" sort={sort} /></th>
          <th>Contact</th>
          <th>Subscription</th>
          <th>Status</th>
          <th onClick={() => toggleSort('start_date')}>Start Date <SortArrow col="start_date" sort={sort} /></th>
          <th onClick={() => toggleSort('next_payment_date')}>Next Payment <SortArrow col="next_payment_date" sort={sort} /></th>
          <th>Next Report Due</th>
          <th style={{ textAlign: 'center' }} onClick={() => toggleSort('reports_sent_count')}>Reports Sent <SortArrow col="reports_sent_count" sort={sort} /></th>
        </tr>
      </thead>
      <tbody>
        {sorted.map(o => (
          <tr key={o.id} onClick={() => window.location.href = `/crm/orgs/${o.id}`}>
            <td><Link href={`/crm/orgs/${o.id}`}>{o.name}</Link></td>
            <td>{o.contact_name || '—'}</td>
            <td>{o.subscription_type ? <Badge label={o.subscription_type.charAt(0).toUpperCase() + o.subscription_type.slice(1)} variant={o.subscription_type} /> : '—'}</td>
            <td><HealthBadge status={o.subscription_status || 'active'} /></td>
            <td>{formatDate(o.start_date)}</td>
            <td>{formatDate(o.next_payment_date)}</td>
            <td>—</td>
            <td className="number" style={{ textAlign: 'center' }}>{o.reports_sent_count ?? 0}</td>
          </tr>
        ))}
        {sorted.length === 0 && (
          <tr><td colSpan={8} style={{ textAlign: 'center', padding: '24px', color: '#6c757d' }}>No clients yet</td></tr>
        )}
      </tbody>
    </table>
  )
}

function LeadsTable({ orgs }: { orgs: Org[] }) {
  const [stages, setStages] = useState<Record<number, string>>({})
  const { sorted, sort, toggleSort } = useSortableTable(orgs, { col: 'name', dir: 'asc' })

  function getStage(o: Org): string {
    return stages[o.id] || o.stage || 'interested'
  }

  async function updateStage(orgId: number, newStage: string) {
    setStages(prev => ({ ...prev, [orgId]: newStage }))
    await supabase.from('organizations').update({ stage: newStage }).eq('id', orgId)
  }

  return (
    <table className="org-table">
      <thead>
        <tr>
          <th onClick={() => toggleSort('name')}>Organization <SortArrow col="name" sort={sort} /></th>
          <th>Contact</th>
          <th>Stage</th>
          <th>Last Contact</th>
          <th>Next Follow-Up</th>
          <th>Notes / Next Steps</th>
          <th style={{ textAlign: 'center' }}>Follow-Up Task</th>
        </tr>
      </thead>
      <tbody>
        {sorted.map(o => (
          <tr key={o.id} onClick={() => window.location.href = `/crm/orgs/${o.id}`}>
            <td><Link href={`/crm/orgs/${o.id}`}>{o.name}</Link></td>
            <td>{o.contact_name || '—'}</td>
            <td onClick={(e) => e.stopPropagation()}>
              <StageDropdown stage={getStage(o)} onChange={(s) => updateStage(o.id, s)} />
            </td>
            <td>{formatDate(o.last_contact_date)}</td>
            <td>{formatDate(o.next_followup_date)}</td>
            <td>{o.next_followup_note || '—'}</td>
            <td className="add-task-cell" onClick={(e) => e.stopPropagation()}>
              <button className="btn-add-task">+ Task</button>
            </td>
          </tr>
        ))}
        {sorted.length === 0 && (
          <tr><td colSpan={7} style={{ textAlign: 'center', padding: '24px', color: '#6c757d' }}>No leads yet</td></tr>
        )}
      </tbody>
    </table>
  )
}

function NonprofitsTable({ orgs }: { orgs: Org[] }) {
  const { sorted, sort, toggleSort } = useSortableTable(orgs, { col: 'name', dir: 'asc' })

  return (
    <table className="org-table">
      <thead>
        <tr>
          <th onClick={() => toggleSort('name')}>Organization <SortArrow col="name" sort={sort} /></th>
          <th onClick={() => toggleSort('state')}>State <SortArrow col="state" sort={sort} /></th>
          <th>Sector</th>
          <th onClick={() => toggleSort('ntee_code')}>NTEE <SortArrow col="ntee_code" sort={sort} /></th>
          <th onClick={() => toggleSort('revenue')}>Revenue <SortArrow col="revenue" sort={sort} /></th>
          <th>Relationship</th>
        </tr>
      </thead>
      <tbody>
        {sorted.map(o => (
          <tr key={o.id} onClick={() => window.location.href = `/crm/orgs/${o.id}`}>
            <td><Link href={`/crm/orgs/${o.id}`}>{o.name}</Link></td>
            <td>{o.state || '—'}</td>
            <td>—</td>
            <td>{o.ntee_code || '—'}</td>
            <td className="number">{formatCurrency(o.revenue)}</td>
            <td><Badge label="Sibling" variant="sibling" /></td>
          </tr>
        ))}
        {sorted.length === 0 && (
          <tr><td colSpan={6} style={{ textAlign: 'center', padding: '24px', color: '#6c757d' }}>No nonprofits yet</td></tr>
        )}
      </tbody>
    </table>
  )
}

function FundersTable({ orgs }: { orgs: Org[] }) {
  const { sorted, sort, toggleSort } = useSortableTable(orgs, { col: 'assets', dir: 'desc' })

  return (
    <table className="org-table">
      <thead>
        <tr>
          <th onClick={() => toggleSort('name')}>Foundation <SortArrow col="name" sort={sort} /></th>
          <th onClick={() => toggleSort('state')}>State <SortArrow col="state" sort={sort} /></th>
          <th onClick={() => toggleSort('assets')}>Assets <SortArrow col="assets" sort={sort} /></th>
          <th onClick={() => toggleSort('annual_giving')}>5yr Giving <SortArrow col="annual_giving" sort={sort} /></th>
          <th>Median Grant</th>
          <th>Recipients</th>
          <th>Last Active</th>
        </tr>
      </thead>
      <tbody>
        {sorted.map(o => (
          <tr key={o.id} onClick={() => window.location.href = `/crm/funders/${o.id}`}>
            <td><Link href={`/crm/funders/${o.id}`}>{o.name}</Link></td>
            <td>{o.state || '—'}</td>
            <td className="number">{formatCurrency(o.assets)}</td>
            <td className="number">{formatCurrency(o.annual_giving)}</td>
            <td className="number">—</td>
            <td className="number">—</td>
            <td className="number">—</td>
          </tr>
        ))}
        {sorted.length === 0 && (
          <tr><td colSpan={7} style={{ textAlign: 'center', padding: '24px', color: '#6c757d' }}>No funders yet</td></tr>
        )}
      </tbody>
    </table>
  )
}

// ============================================================
// CSV Import (Dripify)
// ============================================================

function CSVImportZone() {
  const [show, setShow] = useState(false)
  const [dragover, setDragover] = useState(false)
  const [preview, setPreview] = useState<{ headers: string[]; rows: string[][] } | null>(null)

  function parseCSV(text: string) {
    const lines = text.trim().split('\n')
    if (lines.length < 2) return
    const headers = lines[0].split(',').map(h => h.trim())
    const rows = lines.slice(1).map(line => line.split(',').map(c => c.trim()))
    setPreview({ headers, rows: rows.slice(0, 20) })
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    setDragover(false)
    const file = e.dataTransfer.files[0]
    if (file && file.name.endsWith('.csv')) {
      file.text().then(parseCSV)
    }
  }

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) file.text().then(parseCSV)
  }

  return (
    <>
      <button className="btn-import" onClick={() => setShow(!show)}>&#8593; Import CSV</button>
      {show && (
        <div className="import-zone show">
          {!preview ? (
            <div
              className={`import-dropzone ${dragover ? 'dragover' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setDragover(true) }}
              onDragLeave={() => setDragover(false)}
              onDrop={handleDrop}
            >
              <div className="import-dropzone-icon">&#128196;</div>
              <div className="import-dropzone-text">Drop a Dripify CSV here</div>
              <div className="import-dropzone-hint">
                or <label className="import-file-label">
                  browse
                  <input type="file" accept=".csv" onChange={handleFile} style={{ display: 'none' }} />
                </label>
              </div>
            </div>
          ) : (
            <div className="import-preview">
              <div className="import-preview-header">
                <span className="import-preview-count">{preview.rows.length} leads found</span>
                <button className="import-preview-clear" onClick={() => setPreview(null)}>&#10005; Clear</button>
              </div>
              <div className="import-preview-table-wrap">
                <table className="import-preview-table">
                  <thead>
                    <tr>
                      {preview.headers.slice(0, 6).map((h, i) => <th key={i}>{h}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {preview.rows.map((row, i) => (
                      <tr key={i}>
                        {row.slice(0, 6).map((c, j) => <td key={j}>{c}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="import-actions">
                <button className="import-btn primary" onClick={() => { /* TODO: POST to API */ setPreview(null); setShow(false) }}>Import as Leads</button>
                <button className="import-btn cancel" onClick={() => setPreview(null)}>Cancel</button>
              </div>
            </div>
          )}
        </div>
      )}
    </>
  )
}

// ============================================================
// Main Page
// ============================================================

export default function OrgsPage() {
  const [activeTab, setActiveTab] = useState<TabName>('clients')
  const [orgs, setOrgs] = useState<Org[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      const { data, error } = await supabase
        .from('organizations')
        .select('*')
        .order('name')

      if (!error && data) setOrgs(data as Org[])
      setLoading(false)
    }
    load()
  }, [])

  const clients = orgs.filter(o => o.type === 'client')
  const leads = orgs.filter(o => o.type === 'lead')
  const nonprofits = orgs.filter(o => o.type === 'nonprofit')
  const funders = orgs.filter(o => o.type === 'funder')

  const tabs: { name: TabName; label: string }[] = [
    { name: 'clients', label: 'Clients' },
    { name: 'leads', label: 'Leads' },
    { name: 'nonprofits', label: 'Nonprofits' },
    { name: 'funders', label: 'Funders' },
  ]

  return (
    <>
      <div className="crm-page-header">
        <h2>Organizations</h2>
        <CSVImportZone />
      </div>

      <SearchAutocomplete orgs={orgs} />

      {/* Tab Bar */}
      <div className="entity-tabs">
        {tabs.map(t => (
          <div
            key={t.name}
            className={`entity-tab ${activeTab === t.name ? 'active' : ''}`}
            onClick={() => setActiveTab(t.name)}
          >
            {t.label}
          </div>
        ))}
      </div>

      {/* Table Container */}
      <div className="table-container">
        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#6c757d' }}>Loading...</div>
        ) : (
          <>
            <div className={`tab-panel ${activeTab === 'clients' ? 'active' : ''}`}>
              <ClientsTable orgs={clients} />
            </div>
            <div className={`tab-panel ${activeTab === 'leads' ? 'active' : ''}`}>
              <LeadsTable orgs={leads} />
            </div>
            <div className={`tab-panel ${activeTab === 'nonprofits' ? 'active' : ''}`}>
              <NonprofitsTable orgs={nonprofits} />
            </div>
            <div className={`tab-panel ${activeTab === 'funders' ? 'active' : ''}`}>
              <FundersTable orgs={funders} />
            </div>
          </>
        )}
      </div>
    </>
  )
}
