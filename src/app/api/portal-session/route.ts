import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'

function getStripe() {
  return new Stripe(process.env.STRIPE_SECRET_KEY!, {
    apiVersion: '2026-02-25.clover',
  })
}

export async function GET(request: NextRequest) {
  const sessionId = request.nextUrl.searchParams.get('session_id')
  const customerId = request.nextUrl.searchParams.get('customer_id')

  try {
    const stripe = getStripe()
    let customer: string | null = null

    if (customerId) {
      customer = customerId
    } else if (sessionId) {
      const session = await stripe.checkout.sessions.retrieve(sessionId)
      customer = (session.customer as string | null) ?? null
    } else {
      return NextResponse.json({ error: 'Provide session_id or customer_id' }, { status: 400 })
    }

    if (!customer) {
      return NextResponse.json({ error: 'Customer not found' }, { status: 404 })
    }

    const portal = await stripe.billingPortal.sessions.create({
      customer,
      return_url: `${request.nextUrl.origin}/`,
    })

    return NextResponse.json({ url: portal.url })
  } catch (error) {
    console.error('Portal session error:', error)
    return NextResponse.json({ error: 'Could not create portal session' }, { status: 500 })
  }
}
