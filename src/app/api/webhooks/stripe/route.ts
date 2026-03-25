import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'
import { createServerClient } from '@/lib/supabase'
import { sendWelcomeEmail, sendInternalNotification } from '@/lib/email'

function getStripe() {
  return new Stripe(process.env.STRIPE_SECRET_KEY!, {
    apiVersion: '2026-02-25.clover',
  })
}

function mapStripeInterval(interval: string | undefined): 'monthly' | 'quarterly' | 'annual' {
  if (interval === 'year') return 'annual'
  if (interval === 'month') return 'monthly'
  return 'monthly'
}

function mapSubscriptionStatus(status: string): 'active' | 'past_due' | 'canceled' | 'pending_payment' {
  if (status === 'active') return 'active'
  if (status === 'past_due') return 'past_due'
  if (status === 'canceled') return 'canceled'
  return 'pending_payment'
}

export async function POST(request: NextRequest) {
  const body = await request.text()
  const signature = request.headers.get('stripe-signature')

  if (!signature) {
    return NextResponse.json({ error: 'Missing signature' }, { status: 400 })
  }

  const stripe = getStripe()
  let event: Stripe.Event

  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    )
  } catch (err) {
    console.error('Webhook signature verification failed:', err)
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 })
  }

  const sb = createServerClient()

  try {
    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session
        const subscriberId = session.metadata?.subscriber_id

        if (subscriberId) {
          // 1. Update subscriber in Supabase
          await sb
            .from('subscribers')
            .update({
              stripe_customer_id: session.customer as string,
              stripe_subscription_id: session.subscription as string,
              subscription_status: 'active',
            })
            .eq('id', Number(subscriberId))

          // Fetch subscriber details for emails
          const { data: sub } = await sb
            .from('subscribers')
            .select('org_name, ein, contact_name, contact_email, locations, annual_budget')
            .eq('id', Number(subscriberId))
            .single()

          if (sub) {
            // Format locations for email
            const US_STATES: Record<string, string> = { AL:'Alabama',AK:'Alaska',AZ:'Arizona',AR:'Arkansas',CA:'California',CO:'Colorado',CT:'Connecticut',DE:'Delaware',DC:'District of Columbia',FL:'Florida',GA:'Georgia',HI:'Hawaii',ID:'Idaho',IL:'Illinois',IN:'Indiana',IA:'Iowa',KS:'Kansas',KY:'Kentucky',LA:'Louisiana',ME:'Maine',MD:'Maryland',MA:'Massachusetts',MI:'Michigan',MN:'Minnesota',MS:'Mississippi',MO:'Missouri',MT:'Montana',NE:'Nebraska',NV:'Nevada',NH:'New Hampshire',NJ:'New Jersey',NM:'New Mexico',NY:'New York',NC:'North Carolina',ND:'North Dakota',OH:'Ohio',OK:'Oklahoma',OR:'Oregon',PA:'Pennsylvania',PR:'Puerto Rico',RI:'Rhode Island',SC:'South Carolina',SD:'South Dakota',TN:'Tennessee',TX:'Texas',UT:'Utah',VT:'Vermont',VA:'Virginia',WA:'Washington',WV:'West Virginia',WI:'Wisconsin',WY:'Wyoming' }
            const locs = (sub.locations || []) as Array<{ type: string; state: string; detail: string }>
            const locationsFormatted = locs.length > 0
              ? locs.map((l: { type: string; state: string; detail: string }) => {
                  const stateName = US_STATES[l.state] || l.state
                  return l.type === 'state' ? stateName : `${l.detail}, ${stateName}`
                }).join('; ')
              : 'Not specified'

            // Send emails (non-blocking)
            await Promise.allSettled([
              sendWelcomeEmail(sub.contact_name, sub.contact_email, sub.org_name),
              sendInternalNotification(sub.org_name, sub.ein, sub.contact_name, sub.contact_email, locationsFormatted, sub.annual_budget),
            ])
          }

          // 2. Upsert into Supabase CRM organizations table
          try {
            const stripeSubscription = await stripe.subscriptions.retrieve(session.subscription as string)
            const interval = stripeSubscription.items.data[0]?.price?.recurring?.interval

            // Compute next payment from billing_cycle_anchor + interval
            const anchor = stripeSubscription.billing_cycle_anchor
            let nextPaymentDate: string | null = null
            if (anchor) {
              const anchorDate = new Date(anchor * 1000)
              if (interval === 'year') {
                anchorDate.setFullYear(anchorDate.getFullYear() + 1)
              } else {
                anchorDate.setMonth(anchorDate.getMonth() + 1)
              }
              nextPaymentDate = anchorDate.toISOString().split('T')[0]
            }

            const ein = session.metadata?.ein || sub?.ein || null
            await sb.from('organizations').upsert(
              {
                ein: ein || undefined,
                name: session.metadata?.org_name || sub?.org_name || 'Unknown',
                type: 'client' as const,
                stage: 'active',
                locations: sub?.locations || session.metadata?.locations || null,
                stripe_customer_id: session.customer as string,
                stripe_subscription_id: session.subscription as string,
                subscription_type: mapStripeInterval(interval),
                subscription_status: 'active' as const,
                start_date: new Date().toISOString().split('T')[0],
                next_payment_date: nextPaymentDate,
                contact_name: session.metadata?.contact_name || sub?.contact_name || null,
                contact_email: session.customer_email || sub?.contact_email || null,
              },
              { onConflict: 'ein', ignoreDuplicates: false }
            )
          } catch (sbError) {
            console.error('Supabase org upsert error (non-fatal):', sbError)
          }
        }
        break
      }

      case 'customer.subscription.updated': {
        const subscription = event.data.object as Stripe.Subscription
        const status = mapSubscriptionStatus(subscription.status)

        // 1. Update subscribers table
        await sb
          .from('subscribers')
          .update({ subscription_status: status })
          .eq('stripe_subscription_id', subscription.id)

        // 2. Update organizations table
        try {
          await sb.from('organizations')
            .update({ subscription_status: status })
            .eq('stripe_subscription_id', subscription.id)
        } catch (sbError) {
          console.error('Supabase org update error (non-fatal):', sbError)
        }
        break
      }

      case 'customer.subscription.deleted': {
        const subscription = event.data.object as Stripe.Subscription

        // 1. Update subscribers table
        await sb
          .from('subscribers')
          .update({
            subscription_status: 'canceled',
            canceled_at: new Date().toISOString(),
          })
          .eq('stripe_subscription_id', subscription.id)

        // 2. Update organizations table
        try {
          await sb.from('organizations')
            .update({
              subscription_status: 'canceled' as const,
              type: 'lead' as const,
              stage: 'churned',
            })
            .eq('stripe_subscription_id', subscription.id)
        } catch (sbError) {
          console.error('Supabase org update error (non-fatal):', sbError)
        }
        break
      }

      case 'invoice.payment_failed': {
        const invoiceObj = event.data.object
        const subId = 'subscription' in invoiceObj ? (invoiceObj.subscription as string | null) : null
        if (subId) {
          // 1. Update subscribers table
          await sb
            .from('subscribers')
            .update({ subscription_status: 'past_due' })
            .eq('stripe_subscription_id', subId)

          // 2. Update organizations table
          try {
            await sb.from('organizations')
              .update({ subscription_status: 'past_due' as const })
              .eq('stripe_subscription_id', subId)
          } catch (sbError) {
            console.error('Supabase org update error (non-fatal):', sbError)
          }
        }
        break
      }
    }
  } catch (error) {
    console.error('Webhook handler error:', error)
    // Return 200 anyway to prevent Stripe retries for processing errors
  }

  return NextResponse.json({ received: true })
}
