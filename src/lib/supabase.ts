import { createClient } from '@supabase/supabase-js'
import {
  createBrowserClient as createSSRBrowserClient,
  createServerClient as createSSRServerClient,
} from '@supabase/ssr'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

// Browser client (used in 'use client' components — no auth)
export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Browser client with cookie-based auth (used for signup/login in client components)
export function createBrowserAuthClient() {
  return createSSRBrowserClient(supabaseUrl, supabaseAnonKey)
}

// Server client (used in API routes and server components)
export function createServerClient() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}

// Server auth client — reads/writes Supabase auth cookies for the magic-link
// callback route so exchangeCodeForSession can persist the session.
export async function createServerAuthClient() {
  const { cookies } = await import('next/headers')
  const cookieStore = cookies()
  return createSSRServerClient(supabaseUrl, supabaseAnonKey, {
    cookies: {
      getAll() {
        return cookieStore.getAll()
      },
      setAll(cookiesToSet) {
        try {
          cookiesToSet.forEach(({ name, value, options }) => {
            cookieStore.set(name, value, options)
          })
        } catch {
          // `set` throws in Server Components; Route Handlers allow it, which
          // is where we use this client.
        }
      },
    },
  })
}
