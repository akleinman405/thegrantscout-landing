import { NextResponse } from 'next/server'
import { readdirSync } from 'fs'
import { getMeetings } from '@/lib/meetings'
import { createServerClient } from '@/lib/supabase'

export const dynamic = 'force-dynamic'

const KPI_DIR = '/Users/aleckleinman/Documents/TheGrantScout/5. Operations/3. KPI\'s/KPI'

export async function GET() {
  try {
    // Find most recent weekly LinkedIn report HTML
    let reportFile: string | null = null
    try {
      const files = readdirSync(KPI_DIR)
        .filter((f) => f.startsWith('OUTPUT_') && f.includes('weekly_linkedin_report') && f.endsWith('.html'))
        .sort()
        .reverse()
      reportFile = files[0] || null
    } catch { /* dir not found */ }

    // Get meetings from Video Call Notes
    const meetings = getMeetings().slice(0, 5)

    // Get new clients from Supabase (Stripe signups)
    let newClients: Array<{
      id: number
      name: string
      ein: string | null
      contact_name: string | null
      contact_email: string | null
      subscription_type: string | null
      subscription_status: string | null
      start_date: string | null
      created_at: string
    }> = []
    try {
      const sb = createServerClient()
      const { data } = await sb
        .from('organizations')
        .select('id, name, ein, contact_name, contact_email, subscription_type, subscription_status, start_date, created_at')
        .eq('type', 'client')
        .order('created_at', { ascending: false })
        .limit(10)
      newClients = data || []
    } catch { /* Supabase unavailable */ }

    return NextResponse.json({
      reportFile,
      meetings,
      newClients,
    })
  } catch (err) {
    console.error('Dashboard API error:', err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
