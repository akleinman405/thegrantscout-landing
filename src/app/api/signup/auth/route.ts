import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase'
import { z } from 'zod'

const linkDraftSchema = z.object({
  action: z.literal('link-draft'),
  draftToken: z.string().uuid(),
  userId: z.string().uuid(),
})

export async function POST(request: NextRequest) {
  try {
    const contentType = request.headers.get('content-type')
    if (!contentType || !contentType.includes('application/json')) {
      return NextResponse.json({ error: 'Content-Type must be application/json' }, { status: 415 })
    }

    const raw = await request.json()

    // Link a draft to an authenticated user
    const parsed = linkDraftSchema.safeParse(raw)
    if (!parsed.success) {
      return NextResponse.json(
        { error: 'Invalid request data', details: parsed.error.flatten().fieldErrors },
        { status: 400 }
      )
    }

    const { draftToken, userId } = parsed.data
    const sb = createServerClient()

    const { error } = await sb
      .from('signup_drafts')
      .update({ user_id: userId })
      .eq('draft_token', draftToken)

    if (error) {
      console.error('Link draft error:', error)
      return NextResponse.json({ error: 'Failed to link draft' }, { status: 500 })
    }

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Auth route error:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
