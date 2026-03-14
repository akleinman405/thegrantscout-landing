import { NextResponse } from 'next/server'
import { readdirSync } from 'fs'
import { getMeetings } from '@/lib/meetings'

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

    return NextResponse.json({
      reportFile,
      meetings,
    })
  } catch (err) {
    console.error('Dashboard API error:', err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
