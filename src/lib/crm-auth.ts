import { cookies } from 'next/headers'
import { createHmac } from 'crypto'

const COOKIE_NAME = 'tgs_crm_session'
const MAX_AGE = 30 * 24 * 60 * 60 // 30 days

function getSecret(): string {
  const secret = process.env.CRM_SECRET
  if (!secret) throw new Error('CRM_SECRET not set')
  return secret
}

function sign(value: string): string {
  const sig = createHmac('sha256', getSecret()).update(value).digest('hex')
  return `${value}.${sig}`
}

function verify(signed: string): string | null {
  const idx = signed.lastIndexOf('.')
  if (idx === -1) return null
  const value = signed.slice(0, idx)
  const sig = signed.slice(idx + 1)
  const expected = createHmac('sha256', getSecret()).update(value).digest('hex')
  if (sig.length !== expected.length) return null
  // Constant-time comparison
  let mismatch = 0
  for (let i = 0; i < sig.length; i++) {
    mismatch |= sig.charCodeAt(i) ^ expected.charCodeAt(i)
  }
  return mismatch === 0 ? value : null
}

export function checkPassword(password: string): boolean {
  return password === process.env.CRM_PASSWORD
}

export function createSessionCookie(): { name: string; value: string; maxAge: number; httpOnly: boolean; secure: boolean; sameSite: 'lax'; path: string } {
  const payload = `crm_auth:${Date.now()}`
  return {
    name: COOKIE_NAME,
    value: sign(payload),
    maxAge: MAX_AGE,
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax' as const,
    path: '/',
  }
}

export async function isAuthenticated(): Promise<boolean> {
  const cookieStore = await cookies()
  const cookie = cookieStore.get(COOKIE_NAME)
  if (!cookie) return false
  const value = verify(cookie.value)
  return value !== null && value.startsWith('crm_auth:')
}
