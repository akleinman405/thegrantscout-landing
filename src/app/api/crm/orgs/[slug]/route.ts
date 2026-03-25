import { NextRequest, NextResponse } from 'next/server'
import { existsSync } from 'fs'
import { createServerClient } from '@/lib/supabase'

export const dynamic = 'force-dynamic'

const BRIEF_DIR = '/Users/aleckleinman/Documents/TheGrantScout/4. Sales/1. Leads/1. Viability/1. Nonprofits'

function slugToName(slug: string): string {
  return slug
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params

  try {
    // If slug is numeric, look up in Supabase (client from Stripe)
    if (/^\d+$/.test(slug)) {
      const sb = createServerClient()

      // Fetch organization
      const { data: org, error: orgError } = await sb
        .from('organizations')
        .select('*')
        .eq('id', Number(slug))
        .single()

      if (orgError || !org) {
        return NextResponse.json({ error: 'Org not found' }, { status: 404 })
      }

      // Fetch subscriber details (questionnaire data) by EIN
      let subscriber = null
      if (org.ein) {
        const { data: sub } = await sb
          .from('subscribers')
          .select('*')
          .eq('ein', org.ein)
          .order('created_at', { ascending: false })
          .limit(1)
          .single()
        subscriber = sub
      }

      return NextResponse.json({
        source: 'supabase',
        org,
        subscriber,
      })
    }

    // Otherwise, look for a filesystem brief (existing behavior)
    const briefPath = `${BRIEF_DIR}/BRIEF_${slug}.html`
    const hasBrief = existsSync(briefPath)

    if (!hasBrief) {
      return NextResponse.json({ error: 'Org not found' }, { status: 404 })
    }

    return NextResponse.json({
      source: 'brief',
      slug,
      name: slugToName(slug),
      hasBrief: true,
    })
  } catch (err) {
    console.error('Org detail API error:', err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
