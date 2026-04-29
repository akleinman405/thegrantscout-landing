import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase'
import { z } from 'zod'

const saveDraftSchema = z.object({
  draftToken: z.union([z.string().uuid(), z.null()]).optional(),
  step: z.number().int().min(1).max(5),
  formData: z.record(z.string(), z.unknown()),
})

export async function POST(request: NextRequest) {
  try {
    const contentType = request.headers.get('content-type')
    if (!contentType || !contentType.includes('application/json')) {
      return NextResponse.json({ error: 'Content-Type must be application/json' }, { status: 415 })
    }

    const raw = await request.json()
    const parsed = saveDraftSchema.safeParse(raw)
    if (!parsed.success) {
      return NextResponse.json(
        { error: 'Invalid request data', details: parsed.error.flatten().fieldErrors },
        { status: 400 }
      )
    }

    const { draftToken, step, formData } = parsed.data
    const sb = createServerClient()

    // Extract denormalized fields for admin visibility
    const orgName = typeof formData.orgName === 'string' ? formData.orgName : null
    const contactName = typeof formData.contactName === 'string' ? formData.contactName : null
    const contactEmail = typeof formData.contactEmail === 'string' ? formData.contactEmail : null
    const ein = typeof formData.ein === 'string' ? formData.ein.replace(/\D/g, '').slice(0, 9) : null

    if (draftToken) {
      // Upsert existing draft
      const { data, error } = await sb
        .from('signup_drafts')
        .upsert(
          {
            draft_token: draftToken,
            current_step: step,
            form_data: formData,
            org_name: orgName,
            contact_name: contactName,
            contact_email: contactEmail,
            ein: ein,
            expires_at: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(),
          },
          { onConflict: 'draft_token' }
        )
        .select('draft_token')
        .single()

      if (error) {
        console.error('Draft upsert error:', error)
        return NextResponse.json({ error: 'Failed to save draft' }, { status: 500 })
      }

      return NextResponse.json({ draftToken: data.draft_token })
    } else {
      // Create new draft
      const { data, error } = await sb
        .from('signup_drafts')
        .insert({
          current_step: step,
          form_data: formData,
          org_name: orgName,
          contact_name: contactName,
          contact_email: contactEmail,
          ein: ein,
        })
        .select('draft_token')
        .single()

      if (error) {
        console.error('Draft insert error:', error)
        return NextResponse.json({ error: 'Failed to save draft' }, { status: 500 })
      }

      return NextResponse.json({ draftToken: data.draft_token })
    }
  } catch (error) {
    console.error('Save draft error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

export async function GET(request: NextRequest) {
  try {
    const token = request.nextUrl.searchParams.get('token')
    const userId = request.nextUrl.searchParams.get('user_id')

    if (!token && !userId) {
      return NextResponse.json({ error: 'Provide token or user_id' }, { status: 400 })
    }

    const sb = createServerClient()

    let query = sb
      .from('signup_drafts')
      .select('draft_token, current_step, form_data, status, updated_at')
      .eq('status', 'in_progress')

    if (userId) {
      query = query.eq('user_id', userId)
    } else if (token) {
      query = query.eq('draft_token', token)
    }

    const { data, error } = await query.order('updated_at', { ascending: false }).limit(1).single()

    if (error || !data) {
      return NextResponse.json({ found: false })
    }

    return NextResponse.json({
      found: true,
      draftToken: data.draft_token,
      step: data.current_step,
      formData: data.form_data,
      updatedAt: data.updated_at,
    })
  } catch (error) {
    console.error('Get draft error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
