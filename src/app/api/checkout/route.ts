import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'
import { query } from '@/lib/db'

function getStripe() {
  return new Stripe(process.env.STRIPE_SECRET_KEY!, {
    apiVersion: '2026-02-25.clover',
  })
}

export async function POST(request: NextRequest) {
  try {
    const data = await request.json()

    const cleanEin = data.ein?.replace(/-/g, '') || ''
    const priceId =
      data.planType === 'annual'
        ? process.env.STRIPE_PRICE_ID_ANNUAL
        : process.env.STRIPE_PRICE_ID_MONTHLY

    if (!priceId) {
      return NextResponse.json({ error: 'Pricing not configured' }, { status: 500 })
    }

    // Store subscriber with pending status
    const insertResult = await query(
      `INSERT INTO core.subscribers (
        org_name, ein, org_type, contact_name, contact_email,
        mission, focus_areas, programs, populations,
        state, city, geographic_scope, annual_budget, grant_size_seeking,
        grant_types, grant_capacity,
        ntee_code, known_funders, timeframe, additional_notes,
        plan_type, subscription_status
      ) VALUES (
        $1, $2, $3, $4, $5,
        $6, $7, $8, $9,
        $10, $11, $12, $13, $14,
        $15, $16,
        $17, $18, $19, $20,
        $21, 'pending_payment'
      ) RETURNING id`,
      [
        data.orgName, cleanEin, data.orgType, data.contactName, data.contactEmail,
        data.mission, data.focusAreas || [], data.programs, data.populations || [],
        data.state, data.city, data.geographicScope, data.annualBudget, data.grantSizeSeeking,
        data.grantTypes || [], data.grantCapacity,
        data.nteeCode || null, data.knownFunders || null, data.timeframe || null, data.additionalNotes || null,
        data.planType || 'monthly',
      ]
    )

    const subscriberId = insertResult.rows[0].id

    // Create Stripe Checkout Session
    const stripe = getStripe()
    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      payment_method_types: ['card'],
      customer_email: data.contactEmail,
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${request.nextUrl.origin}/signup/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${request.nextUrl.origin}/signup?step=5`,
      metadata: {
        subscriber_id: String(subscriberId),
        org_name: (data.orgName || '').slice(0, 500),
        ein: cleanEin,
        contact_name: (data.contactName || '').slice(0, 500),
        state: data.state || '',
        city: (data.city || '').slice(0, 500),
      },
      subscription_data: {
        metadata: {
          subscriber_id: String(subscriberId),
          org_name: (data.orgName || '').slice(0, 500),
          ein: cleanEin,
        },
      },
    })

    return NextResponse.json({ url: session.url })
  } catch (error) {
    console.error('Checkout error:', error)
    return NextResponse.json(
      { error: 'Failed to create checkout session. Please try again.' },
      { status: 500 }
    )
  }
}

// GET handler for success page to retrieve session info
export async function GET(request: NextRequest) {
  const sessionId = request.nextUrl.searchParams.get('session_id')
  if (!sessionId) {
    return NextResponse.json({ error: 'Missing session_id' }, { status: 400 })
  }

  try {
    const stripe = getStripe()
    const session = await stripe.checkout.sessions.retrieve(sessionId)
    return NextResponse.json({
      orgName: session.metadata?.org_name || '',
      email: session.customer_email || '',
    })
  } catch {
    return NextResponse.json({ error: 'Session not found' }, { status: 404 })
  }
}
