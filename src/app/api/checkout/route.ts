import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'
import { createServerClient } from '@/lib/supabase'
import { z } from 'zod'

function getStripe() {
  return new Stripe(process.env.STRIPE_SECRET_KEY!, {
    apiVersion: '2026-02-25.clover',
  })
}

const checkoutSchema = z.object({
  orgName: z.string().min(1).max(500),
  ein: z.string().max(20).optional().default(''),
  orgType: z.string().max(100).optional(),
  contactName: z.string().min(1).max(200),
  contactEmail: z.string().email().max(320),
  mission: z.string().min(1).max(5000),
  focusAreas: z.array(z.string().max(200)).max(20).optional().default([]),
  programs: z.string().max(5000).optional(),
  populations: z.array(z.string().max(200)).max(20).optional().default([]),
  locations: z.array(z.object({
    type: z.enum(['city', 'state', 'county']),
    state: z.string().max(10),
    detail: z.string().max(200),
  })).max(20).optional().default([]),
  geographicScope: z.string().max(200).optional(),
  annualBudget: z.string().max(100).optional(),
  grantSizeSeeking: z.array(z.string().max(100)).max(10).optional().default([]),
  grantTypes: z.array(z.string().max(200)).max(20).optional().default([]),
  grantCapacity: z.string().max(200).optional(),
  knownFunders: z.string().max(5000).nullable().optional().default(null),
  reportCount: z.number().int().min(1).max(50).optional().default(1),
  reportRecipients: z.array(z.object({
    name: z.string().max(200),
    email: z.string().email().max(320),
    focus: z.string().max(500),
  })).max(20).optional().default([]),
  additionalNotes: z.string().max(5000).nullable().optional().default(null),
  planType: z.enum(['monthly', 'annual']).optional().default('monthly'),
  draftToken: z.string().uuid().nullable().optional().default(null),
})

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

    const raw = await request.json()
    const parsed = checkoutSchema.safeParse(raw)
    if (!parsed.success) {
      return NextResponse.json(
        { error: 'Invalid request data', details: parsed.error.flatten().fieldErrors },
        { status: 400 }
      )
    }
    const data = parsed.data

    const cleanEin = data.ein?.replace(/-/g, '') || ''
    const priceId =
      data.planType === 'annual'
        ? process.env.STRIPE_PRICE_ID_ANNUAL
        : process.env.STRIPE_PRICE_ID_MONTHLY

    if (!priceId) {
      return NextResponse.json({ error: 'Pricing not configured' }, { status: 500 })
    }

    // Store subscriber with pending status in Supabase
    const sb = createServerClient()
    const { data: inserted, error: insertError } = await sb
      .from('subscribers')
      .insert({
        org_name: data.orgName,
        ein: cleanEin,
        org_type: data.orgType,
        contact_name: data.contactName,
        contact_email: data.contactEmail,
        mission: data.mission,
        focus_areas: data.focusAreas || [],
        programs: data.programs,
        populations: data.populations || [],
        locations: data.locations || [],
        geographic_scope: data.geographicScope,
        annual_budget: data.annualBudget,
        grant_size_seeking: data.grantSizeSeeking || [],
        grant_types: data.grantTypes || [],
        grant_capacity: data.grantCapacity,
        known_funders: data.knownFunders || null,
        report_count: data.reportCount || 1,
        report_recipients: data.reportRecipients || [],
        additional_notes: data.additionalNotes || null,
        plan_type: data.planType || 'monthly',
        subscription_status: 'pending_payment',
      })
      .select('id')
      .single()

    if (insertError || !inserted) {
      console.error('Supabase insert error:', insertError)
      return NextResponse.json(
        { error: 'Failed to create subscriber record. Please try again.' },
        { status: 500 }
      )
    }

    const subscriberId = inserted.id

    // Mark draft as converted if a draft token was provided
    if (data.draftToken) {
      await sb
        .from('signup_drafts')
        .update({ status: 'converted', subscriber_id: subscriberId })
        .eq('draft_token', data.draftToken)
        .then(({ error }) => {
          if (error) console.error('Draft conversion error (non-fatal):', error)
        })
    }

    const stripe = getStripe()
    const qty = data.reportCount || 1

    // Create Stripe Checkout Session
    const isAnnual = data.planType === 'annual'
    const unitPrice = isAnnual ? 83 : 99
    const totalDisplay = qty > 1
      ? `${qty} playbooks \u00d7 $${unitPrice}/mo = $${unitPrice * qty}/mo`
      : `1 playbook \u2014 $${unitPrice}/mo`

    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      payment_method_types: ['card'],
      customer_email: data.contactEmail,
      allow_promotion_codes: true,
      line_items: [{
        price: priceId,
        quantity: qty,
      }],
      success_url: `${request.nextUrl.origin}/signup/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${request.nextUrl.origin}/signup?step=5`,
      custom_text: {
        submit: {
          message: `${totalDisplay}. Each playbook includes 5 curated foundation opportunities matched to your mission.`,
        },
      },
      metadata: {
        subscriber_id: String(subscriberId),
        org_name: (data.orgName || '').slice(0, 500),
        ein: cleanEin,
        contact_name: (data.contactName || '').slice(0, 500),
        locations: JSON.stringify(data.locations || []).slice(0, 500),
        playbook_count: String(qty),
      },
      subscription_data: {
        metadata: {
          subscriber_id: String(subscriberId),
          org_name: (data.orgName || '').slice(0, 500),
          ein: cleanEin,
          playbook_count: String(qty),
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
