import { NextRequest, NextResponse } from 'next/server'
import { createServerAuthClient, createServerClient } from '@/lib/supabase'

// Magic-link callback. Supabase emails a URL that lands here with ?code=...&next=/path.
// We exchange the code for a session (persisted as a cookie), link any
// still-unclaimed draft to the user by email (so cross-device resume works),
// then redirect.
export async function GET(request: NextRequest) {
  const url = request.nextUrl
  const code = url.searchParams.get('code')
  const next = url.searchParams.get('next') || '/signup'

  if (!code) {
    return NextResponse.redirect(new URL('/signup?auth_error=1', url.origin))
  }

  try {
    const supabase = await createServerAuthClient()
    const { error } = await supabase.auth.exchangeCodeForSession(code)
    if (error) {
      return NextResponse.redirect(new URL('/signup?auth_error=1', url.origin))
    }

    // Attach any pre-login draft (identified only by contact_email) to the
    // newly-authenticated user so /signup can find it by user_id on the next
    // device.
    const { data: userData } = await supabase.auth.getUser()
    const email = userData.user?.email
    const userId = userData.user?.id
    if (email && userId) {
      const admin = createServerClient()
      const { data: drafts } = await admin
        .from('signup_drafts')
        .select('draft_token')
        .ilike('contact_email', email)
        .is('user_id', null)
        .eq('status', 'in_progress')
        .order('updated_at', { ascending: false })
        .limit(1)
      if (drafts && drafts.length > 0) {
        await admin
          .from('signup_drafts')
          .update({ user_id: userId })
          .eq('draft_token', drafts[0].draft_token)
      }
    }

    // Only allow same-origin relative paths for `next` to prevent open-redirect.
    const safeNext = next.startsWith('/') ? next : '/signup'
    return NextResponse.redirect(new URL(safeNext, url.origin))
  } catch {
    return NextResponse.redirect(new URL('/signup?auth_error=1', url.origin))
  }
}
