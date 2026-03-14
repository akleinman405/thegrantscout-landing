import { NextRequest, NextResponse } from 'next/server'

const COOKIE_NAME = 'tgs_crm_session'

async function verifyCookie(value: string, secret: string): Promise<boolean> {
  const idx = value.lastIndexOf('.')
  if (idx === -1) return false
  const payload = value.slice(0, idx)
  const sig = value.slice(idx + 1)

  const encoder = new TextEncoder()
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  )
  const sigBytes = await crypto.subtle.sign('HMAC', key, encoder.encode(payload))
  const expected = Array.from(new Uint8Array(sigBytes))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')

  if (sig.length !== expected.length) return false
  let mismatch = 0
  for (let i = 0; i < sig.length; i++) {
    mismatch |= sig.charCodeAt(i) ^ expected.charCodeAt(i)
  }
  return mismatch === 0 && payload.startsWith('crm_auth:')
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Only protect /crm routes (not login or auth API)
  if (!pathname.startsWith('/crm') && !pathname.startsWith('/api/crm')) return NextResponse.next()
  if (pathname === '/crm/login') return NextResponse.next()
  if (pathname.startsWith('/api/crm/auth')) return NextResponse.next()

  const cookie = request.cookies.get(COOKIE_NAME)
  const secret = process.env.CRM_SECRET

  if (!cookie || !secret || !(await verifyCookie(cookie.value, secret))) {
    // For API routes, return 401 instead of redirect
    if (pathname.startsWith('/api/')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    const loginUrl = new URL('/crm/login', request.url)
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/crm/:path*', '/api/crm/:path*'],
}
