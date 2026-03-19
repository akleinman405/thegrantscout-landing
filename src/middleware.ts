import { NextRequest, NextResponse } from 'next/server'
import { rateLimit } from '@/lib/rate-limit'

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

function getClientIp(request: NextRequest): string {
  return (
    request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ||
    request.headers.get('x-real-ip') ||
    'unknown'
  )
}

function auditLog(request: NextRequest, status: number, extra?: Record<string, unknown>) {
  const entry = {
    ts: new Date().toISOString(),
    method: request.method,
    path: request.nextUrl.pathname,
    ip: getClientIp(request),
    ua: request.headers.get('user-agent')?.slice(0, 120) || '',
    status,
    ...extra,
  }
  console.log(JSON.stringify(entry))
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const ip = getClientIp(request)

  // --- Rate limiting for /api/crm/* ---
  if (pathname.startsWith('/api/crm')) {
    // Stricter limit for auth endpoint: 5 attempts per 15 min
    if (pathname.startsWith('/api/crm/auth')) {
      const authCheck = rateLimit(`auth:${ip}`, 5, 15 * 60 * 1000)
      if (!authCheck.allowed) {
        auditLog(request, 429, { reason: 'auth_rate_limit' })
        return NextResponse.json(
          { error: 'Too many login attempts. Try again later.' },
          {
            status: 429,
            headers: { 'Retry-After': String(authCheck.retryAfter) },
          }
        )
      }
    }

    // General CRM rate limit: 100 req/min per IP
    const generalCheck = rateLimit(`crm:${ip}`, 100, 60 * 1000)
    if (!generalCheck.allowed) {
      auditLog(request, 429, { reason: 'general_rate_limit' })
      return NextResponse.json(
        { error: 'Rate limit exceeded. Try again later.' },
        {
          status: 429,
          headers: { 'Retry-After': String(generalCheck.retryAfter) },
        }
      )
    }
  }

  // --- Auth check for protected routes ---
  if (!pathname.startsWith('/crm') && !pathname.startsWith('/api/crm')) {
    return NextResponse.next()
  }
  if (pathname === '/crm/login') return NextResponse.next()
  if (pathname.startsWith('/api/crm/auth')) {
    return NextResponse.next()
  }

  const cookie = request.cookies.get(COOKIE_NAME)
  const secret = process.env.CRM_SECRET

  if (!cookie || !secret || !(await verifyCookie(cookie.value, secret))) {
    if (pathname.startsWith('/api/')) {
      auditLog(request, 401)
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    const loginUrl = new URL('/crm/login', request.url)
    return NextResponse.redirect(loginUrl)
  }

  auditLog(request, 200)
  return NextResponse.next()
}

export const config = {
  matcher: ['/crm/:path*', '/api/crm/:path*'],
}
