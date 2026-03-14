/**
 * One-time script to backfill existing Stripe subscriptions into core.subscribers.
 *
 * Usage:
 *   npx tsx scripts/backfill_stripe_subscribers.ts
 *
 * Prerequisites:
 *   - STRIPE_SECRET_KEY in .env.local
 *   - DATABASE_URL in .env.local
 *   - core.subscribers table exists (run 001_create_subscribers.sql first)
 */

import Stripe from 'stripe'
import { Pool } from 'pg'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2026-02-25.clover',
})

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
})

async function backfill() {
  console.log('Fetching active subscriptions from Stripe...')

  let hasMore = true
  let startingAfter: string | undefined
  let count = 0

  while (hasMore) {
    const params: Stripe.SubscriptionListParams = {
      status: 'active',
      limit: 100,
      expand: ['data.customer'],
    }
    if (startingAfter) params.starting_after = startingAfter

    const subscriptions = await stripe.subscriptions.list(params)

    for (const sub of subscriptions.data) {
      const customer = sub.customer as Stripe.Customer
      const metadata = sub.metadata || {}

      const orgName = metadata.org_name || customer.name || 'Unknown'
      const ein = metadata.ein || ''
      const contactName = metadata.contact_name || customer.name || ''
      const contactEmail = customer.email || ''
      const state = metadata.state || ''

      // Determine plan type from price interval
      const priceInterval = sub.items.data[0]?.price?.recurring?.interval
      const planType = priceInterval === 'year' ? 'annual' : 'monthly'

      await pool.query(
        `INSERT INTO core.subscribers (
          stripe_customer_id, stripe_subscription_id, subscription_status,
          org_name, ein, contact_name, contact_email, state, plan_type, signup_source
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'backfill')
        ON CONFLICT (stripe_subscription_id) DO UPDATE SET
          subscription_status = EXCLUDED.subscription_status,
          updated_at = NOW()`,
        [
          customer.id, sub.id, 'active',
          orgName, ein, contactName, contactEmail, state, planType,
        ]
      )

      count++
      console.log(`  Synced: ${orgName} (${sub.id})`)
    }

    hasMore = subscriptions.has_more
    if (subscriptions.data.length > 0) {
      startingAfter = subscriptions.data[subscriptions.data.length - 1].id
    }
  }

  console.log(`\nDone. Backfilled ${count} subscriptions.`)
  await pool.end()
}

backfill().catch((err) => {
  console.error('Backfill failed:', err)
  process.exit(1)
})
