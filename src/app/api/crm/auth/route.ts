import { NextRequest, NextResponse } from 'next/server'
import { checkPassword, createSessionCookie } from '@/lib/crm-auth'

export async function POST(request: NextRequest) {
  try {
    // Content-Type check
    const contentType = request.headers.get('content-type')
    if (!contentType || !contentType.includes('application/json')) {
      return NextResponse.json(
        { error: 'Content-Type must be application/json' },
        { status: 415 }
      )
    }

    const body = await request.json()
    const { password } = body

    if (!password || !checkPassword(password)) {
      return NextResponse.json({ error: 'Invalid password' }, { status: 401 })
    }

    const cookie = createSessionCookie()
    const response = NextResponse.json({ ok: true })
    response.cookies.set(cookie.name, cookie.value, {
      maxAge: cookie.maxAge,
      httpOnly: cookie.httpOnly,
      secure: cookie.secure,
      sameSite: cookie.sameSite,
      path: cookie.path,
    })
    return response
  } catch (err) {
    console.error('Auth error:', err)
    return NextResponse.json({ error: 'Server error' }, { status: 500 })
  }
}
