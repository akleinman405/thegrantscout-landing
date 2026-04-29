import { createClient, type SupabaseClient } from '@supabase/supabase-js'
import { createBrowserClient as createSSRBrowserClient } from '@supabase/ssr'

// Browser client with cookie-based auth (used for signup/login in client components).
// Memoized so we don't trip the "Multiple GoTrueClient instances" warning when
// hooks call it multiple times within a single page lifecycle.
let browserAuthClient: SupabaseClient | null = null
export function createBrowserAuthClient(): SupabaseClient {
  if (!browserAuthClient) {
    browserAuthClient = createSSRBrowserClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    )
  }
  return browserAuthClient
}

// Server client (used in API routes and server components)
export function createServerClient() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
