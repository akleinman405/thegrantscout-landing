import { NextRequest, NextResponse } from 'next/server'

// Configuration
const CONTACT_EMAIL = 'info@thegrantscout.com'

// Type for form data
interface ContactFormData {
  name: string
  organization: string
  email: string
  fundingGoals: string
}

export async function POST(request: NextRequest) {
  try {
    const data: ContactFormData = await request.json()

    // Validate required fields
    if (!data.name || !data.organization || !data.email || !data.fundingGoals) {
      return NextResponse.json(
        { error: 'All fields are required' },
        { status: 400 }
      )
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(data.email)) {
      return NextResponse.json(
        { error: 'Invalid email format' },
        { status: 400 }
      )
    }

    // Log submission (for now - will be replaced with actual email/sheets integration)
    console.log('New contact form submission:', {
      timestamp: new Date().toISOString(),
      ...data
    })

    // TODO: Integrate with email service (Resend, SendGrid, etc.)
    // Example with Resend:
    // const resend = new Resend(process.env.RESEND_API_KEY)
    // await resend.emails.send({
    //   from: 'TheGrantScout <noreply@thegrantscout.com>',
    //   to: CONTACT_EMAIL,
    //   subject: `New Lead: ${data.organization}`,
    //   html: `
    //     <h2>New Grant Report Request</h2>
    //     <p><strong>Name:</strong> ${data.name}</p>
    //     <p><strong>Organization:</strong> ${data.organization}</p>
    //     <p><strong>Email:</strong> ${data.email}</p>
    //     <p><strong>Funding Goals:</strong></p>
    //     <p>${data.fundingGoals}</p>
    //     <hr>
    //     <p><em>Submitted at: ${new Date().toISOString()}</em></p>
    //   `
    // })

    // TODO: Integrate with Google Sheets API
    // Example with Google Sheets:
    // const auth = new google.auth.GoogleAuth({
    //   credentials: JSON.parse(process.env.GOOGLE_CREDENTIALS || '{}'),
    //   scopes: ['https://www.googleapis.com/auth/spreadsheets']
    // })
    // const sheets = google.sheets({ version: 'v4', auth })
    // await sheets.spreadsheets.values.append({
    //   spreadsheetId: process.env.GOOGLE_SHEET_ID,
    //   range: 'Leads!A:E',
    //   valueInputOption: 'USER_ENTERED',
    //   requestBody: {
    //     values: [[
    //       new Date().toISOString(),
    //       data.name,
    //       data.organization,
    //       data.email,
    //       data.fundingGoals
    //     ]]
    //   }
    // })

    // For now, we'll store in a simple file as backup
    // In production, use proper database or external services

    return NextResponse.json(
      {
        success: true,
        message: 'Thank you! We will be in touch within 48 hours.'
      },
      { status: 200 }
    )

  } catch (error) {
    console.error('Contact form error:', error)
    return NextResponse.json(
      { error: 'Failed to process submission. Please try again.' },
      { status: 500 }
    )
  }
}

// Handle other methods
export async function GET() {
  return NextResponse.json(
    { error: 'Method not allowed' },
    { status: 405 }
  )
}
