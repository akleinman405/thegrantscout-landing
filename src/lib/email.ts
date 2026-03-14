import { Resend } from 'resend'

function getResend() {
  return new Resend(process.env.RESEND_API_KEY)
}

export async function sendWelcomeEmail(
  contactName: string,
  contactEmail: string,
  orgName: string
) {
  const firstName = contactName.split(' ')[0]

  await getResend().emails.send({
    from: 'TheGrantScout <hello@thegrantscout.com>',
    to: contactEmail,
    subject: 'Welcome to TheGrantScout — Your First Report is On Its Way',
    html: `
      <div style="font-family: system-ui, sans-serif; max-width: 600px; margin: 0 auto; color: #2C3E50;">
        <div style="background-color: #1e3a5f; padding: 24px; text-align: center;">
          <h1 style="color: #d4a853; margin: 0; font-size: 24px;">TheGrantScout</h1>
        </div>
        <div style="padding: 32px 24px;">
          <h2 style="color: #1e3a5f; margin-top: 0;">Welcome, ${firstName}!</h2>
          <p>Thank you for signing up <strong>${orgName}</strong> with TheGrantScout.</p>
          <p>Here's what happens next:</p>
          <ol style="line-height: 1.8;">
            <li>We'll review your organization profile and begin matching you with relevant foundations.</li>
            <li><strong>Your first report will arrive within 3-5 business days</strong> at this email address.</li>
            <li>After that, you'll receive a fresh report every month with new opportunities.</li>
          </ol>
          <p>Each report includes curated foundation matches with giving history, contact information, and positioning strategy tailored to your mission.</p>
          <p>If you have any questions, reply to this email or reach out to <a href="mailto:hello@thegrantscout.com" style="color: #1e3a5f;">hello@thegrantscout.com</a>.</p>
          <p style="margin-top: 32px;">Best,<br>Alec Kleinman<br>Founder, TheGrantScout</p>
        </div>
        <div style="background-color: #f8f9fa; padding: 16px 24px; text-align: center; font-size: 12px; color: #6C757D;">
          <p>&copy; ${new Date().getFullYear()} TheGrantScout. All rights reserved.</p>
        </div>
      </div>
    `,
  })
}

export async function sendInternalNotification(
  orgName: string,
  ein: string,
  contactName: string,
  contactEmail: string,
  state: string,
  budget: string
) {
  const adminEmail = process.env.ADMIN_EMAIL || 'alec@thegrantscout.com'

  await getResend().emails.send({
    from: 'TheGrantScout <hello@thegrantscout.com>',
    to: adminEmail,
    subject: `New TGS Subscriber: ${orgName}`,
    html: `
      <div style="font-family: system-ui, sans-serif; max-width: 600px; color: #2C3E50;">
        <h2 style="color: #1e3a5f;">New Subscriber Signup</h2>
        <table style="border-collapse: collapse; width: 100%;">
          <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Organization</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${orgName}</td></tr>
          <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">EIN</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${ein}</td></tr>
          <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Contact</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${contactName} (${contactEmail})</td></tr>
          <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">State</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${state}</td></tr>
          <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Budget</td><td style="padding: 8px; border-bottom: 1px solid #eee;">${budget}</td></tr>
        </table>
        <p style="margin-top: 16px; color: #6C757D;">Action needed: Begin report generation within 3-5 business days.</p>
      </div>
    `,
  })
}
