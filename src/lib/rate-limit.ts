/**
 * In-memory sliding-window rate limiter.
 * Suitable for single-process deployments (Netlify Functions, Next.js dev).
 */

interface WindowEntry {
  timestamps: number[]
  windowMs: number
}

const store = new Map<string, WindowEntry>()

// Prune expired entries every 5 minutes
const CLEANUP_INTERVAL = 5 * 60 * 1000
let lastCleanup = Date.now()

function cleanup(now: number) {
  if (now - lastCleanup < CLEANUP_INTERVAL) return
  lastCleanup = now
  store.forEach((entry, key) => {
    entry.timestamps = entry.timestamps.filter((t) => now - t < entry.windowMs)
    if (entry.timestamps.length === 0) store.delete(key)
  })
}

export function rateLimit(
  key: string,
  max: number,
  windowMs: number
): { allowed: boolean; retryAfter?: number } {
  const now = Date.now()
  cleanup(now)

  let entry = store.get(key)
  if (!entry) {
    entry = { timestamps: [], windowMs }
    store.set(key, entry)
  }

  // Remove timestamps outside the window
  entry.timestamps = entry.timestamps.filter((t) => now - t < windowMs)

  if (entry.timestamps.length >= max) {
    const oldest = entry.timestamps[0]
    const retryAfter = Math.ceil((oldest + windowMs - now) / 1000)
    return { allowed: false, retryAfter }
  }

  entry.timestamps.push(now)
  return { allowed: true }
}
