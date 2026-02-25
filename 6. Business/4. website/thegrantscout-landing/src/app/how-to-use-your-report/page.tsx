'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { trackCTA, trackEvent } from '@/components/GoogleAnalytics'

// --- Data: Report sections grouped into 3 categories ---

interface ReportSection {
  id: string
  title: string
  description: string
  group: 'start' | 'foundations' | 'action'
  whatsInIt: string[]
  whatItMeans: string
  exampleCallout: string
}

const reportSections: ReportSection[] = [
  {
    id: 'quick-win',
    title: 'Quick Win: If You Only Have 5 Hours',
    description: 'Your single highest-impact action',
    group: 'start',
    whatsInIt: [
      'The one foundation you should contact first',
      'Exactly what to send them and why',
      'Why this foundation is the strongest match',
      'Time estimate for the submission',
    ],
    whatItMeans:
      'Not every nonprofit has 16 hours a month for grant research. This section cuts straight to your best opportunity so even the busiest development director can take action. If you do nothing else, do this.',
    exampleCallout:
      'Email grants@stfsf.org with a 2-page LOI introducing your organization. Why them: They gave $75,000 to a similar program in 2023. Their mission explicitly includes your focus area, and they operate in the same region. Time required: 4 hours.',
  },
  {
    id: 'this-months-focus',
    title: "This Month's Focus",
    description: 'Priorities, time guide, and contacts',
    group: 'start',
    whatsInIt: [
      'Priority-ranked list of all foundations in the report',
      'Time allocation guide (5 hours, 8 hours, 12 hours, 16+ hours)',
      'Foundation type and deadline for each',
      'Contact quick-reference table with names, emails, and phone numbers',
    ],
    whatItMeans:
      'This is your roadmap for the month. It tells you exactly where to spend your time based on how many hours you have available, so you always work on the highest-value opportunities first.',
    exampleCallout:
      'Priority 1: St. Francis Sailing Foundation | LOI-Ready | Same Bay Area waters; $75K to similar program; April deadline | 4 hours\nPriority 2: Louie Family Foundation | LOI-Ready | 7 veteran grants in 2023; military preference; 15 miles away | 3 hours',
  },
  {
    id: 'foundation-types',
    title: 'Foundation Types Explained',
    description: 'LOI-Ready, Open Application, Cultivation',
    group: 'foundations',
    whatsInIt: [
      'Three foundation categories and what each means',
      'What action to take for each type',
      'Why "Cultivation" foundations are included (and when to skip them)',
    ],
    whatItMeans:
      'Not all foundations work the same way. Some accept cold applications, others require a relationship first. Knowing the type tells you how to approach each one and set realistic expectations for the timeline.',
    exampleCallout:
      'LOI-Ready: Foundation accepts unsolicited Letters of Inquiry. If interested, they\'ll invite a full proposal. Your action: Write and submit LOI this month.\n\nCultivation: Foundation is bank-managed or rarely funds without an existing relationship. Your action: Research staff, identify connections, begin relationship-building.',
  },
  {
    id: 'foundations-at-a-glance',
    title: 'Foundations at a Glance',
    description: 'Compare all foundations side by side',
    group: 'foundations',
    whatsInIt: [
      'One-row summary for each foundation',
      'Typical grant range, foundation type, and time required',
      'Ranked by fit and priority',
    ],
    whatItMeans:
      'This table gives you a bird\'s-eye view of all your opportunities before diving into the details. Use it to quickly compare grant sizes, timelines, and effort required.',
    exampleCallout:
      '#1 St. Francis Sailing Foundation | $11,000-$75,000 | LOI-Ready | 4 hrs\n#2 Louie Family Foundation | $5,000-$10,000 | LOI-Ready | 3 hrs\n#3 Stout Foundation | $5,000-$20,000 | Open Application | 4 hrs',
  },
  {
    id: 'foundation-profiles',
    title: 'Foundation Profiles',
    description: 'Deep-dive profiles for each funder',
    group: 'foundations',
    whatsInIt: [
      '"Why This Foundation" narrative with specific evidence',
      'Fit Evidence table: what we looked for vs. what we found',
      'Funder Snapshot: annual giving, typical grant, geographic focus, giving style, assets',
      'How to Apply: submission method, requirements, deadlines',
      'Contacts table with names, roles, emails, and phone numbers',
      'Potential Connections: shared grantees, network paths, geographic ties',
      'Positioning Strategy: exactly how to frame your ask',
      'Step-by-step Action Plan with time estimates',
    ],
    whatItMeans:
      'This is the heart of the report. Each profile gives you everything you need to approach a foundation with confidence: why they\'re a match, how to apply, who to contact, and exactly what to say. No more guessing whether a funder is the right fit.',
    exampleCallout:
      'Funder Snapshot: Annual Giving $151,000 across 3 grants | Typical Grant $65,000 median ($11K-$75K) | Geographic Focus 100% California | Total Assets $7.7M\n\nPositioning: Lead with adaptive sailing for veterans. Reference a comparable program they already fund at $75,000. Emphasize that you operate in the same region, serving a distinct population.',
  },
  {
    id: 'monthly-action-plan',
    title: 'Monthly Action Plan',
    description: 'Week-by-week tasks and follow-ups',
    group: 'action',
    whatsInIt: [
      'Week-by-week breakdown of tasks across all foundations',
      'Total monthly time estimate',
      '"What You\'ll Be Waiting On" tracker with expected response times',
      'Follow-up dates so nothing falls through the cracks',
    ],
    whatItMeans:
      'Grant seeking requires sustained effort over months. This plan turns your report into a calendar so you know exactly what to do each week and when to follow up. No action items get lost.',
    exampleCallout:
      'Week 1: Review grants page, identify connections, draft LOI (3 hrs) + Begin second LOI draft (1 hr)\nWeek 2: Finalize and submit both LOIs (3 hrs)\nWeek 3: Make introductory calls to two foundations (1.5 hrs)\nWeek 4: Begin application for June deadline (2.5 hrs)',
  },
  {
    id: 'quick-reference',
    title: 'Quick Reference & Timeline',
    description: 'Contacts, deadlines, and the process',
    group: 'action',
    whatsInIt: [
      'Master contact table: every person, email, and phone number in one place',
      'Application summary: type, deadline, and process for each foundation',
      'Time and probability summary for prioritizing',
      'Typical grant timeline (3-9 months from submission to decision)',
      'Data sources and methodology notes',
    ],
    whatItMeans:
      'When you\'re ready to pick up the phone or send an email, you don\'t want to dig through 20 pages. This section puts every contact and deadline in one place. The timeline section sets realistic expectations so you know that grant seeking is a marathon, not a sprint.',
    exampleCallout:
      'Typical Grant Process (3-9 months):\nMonth 1: Research + Submit LOI/Application\nMonths 2-3: Wait for response (6-8 weeks typical)\nMonths 3-4: If invited, write full proposal\nMonths 6-9: Decision received',
  },
]

const groupLabels: Record<string, string> = {
  start: 'Where to Start',
  foundations: 'Understanding Your Foundations',
  action: 'Taking Action',
}

const groupOrder = ['start', 'foundations', 'action'] as const

// --- Component ---

export default function ReportGuidePage() {
  const [openSections, setOpenSections] = useState<Set<string>>(new Set())
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  // URL hash deep-linking on mount
  useEffect(() => {
    document.title = "Grant Report Guide: What's Inside & How to Use It | TheGrantScout"

    const hash = window.location.hash.replace('#', '')
    if (hash) {
      const section = reportSections.find((s) => s.id === hash)
      if (section) {
        setOpenSections(new Set([hash]))
        setTimeout(() => {
          const el = document.getElementById(hash)
          if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'start' })
          }
        }, 100)
      }
    }
  }, [])

  const toggleSection = (id: string) => {
    setOpenSections((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
        trackEvent('section_open', 'report_guide', id)
      }
      return next
    })
  }

  const allOpen = reportSections.every((s) => openSections.has(s.id))

  const toggleAll = () => {
    if (allOpen) {
      setOpenSections(new Set())
    } else {
      setOpenSections(new Set(reportSections.map((s) => s.id)))
    }
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Skip to main content */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[200] focus:bg-white focus:px-4 focus:py-2 focus:rounded focus:shadow-lg focus:text-primary"
      >
        Skip to main content
      </a>

      {/* Navigation — Full site nav (same as homepage) */}
      <nav className="fixed w-full bg-white/95 backdrop-blur-sm shadow-sm z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link
                href="/"
                className="text-2xl font-bold text-primary hover:text-primary-light transition-colors"
              >
                TheGrantScout
              </Link>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <Link href="/#how-it-works" className="text-charcoal hover:text-primary transition-colors font-medium">How It Works</Link>
              <Link href="/#features" className="text-charcoal hover:text-primary transition-colors font-medium">Features</Link>
              <Link href="/#pricing" className="text-charcoal hover:text-primary transition-colors font-medium">Pricing</Link>
              <Link href="/#faq" className="text-charcoal hover:text-primary transition-colors font-medium">FAQ</Link>
              <a
                href="https://calendly.com/alec_kleinman/meeting-with-alec"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary min-h-[44px]"
                onClick={() => trackCTA.bookCall('nav')}
              >
                Book a Call
              </a>
            </div>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden w-12 h-12 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-colors"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle menu"
            >
              <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {mobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-gray-100 animate-fade-in">
              <div className="flex flex-col space-y-2">
                <Link href="/#how-it-works" onClick={() => setMobileMenuOpen(false)} className="text-charcoal hover:text-primary transition-colors font-medium py-4 block">How It Works</Link>
                <Link href="/#features" onClick={() => setMobileMenuOpen(false)} className="text-charcoal hover:text-primary transition-colors font-medium py-4 block">Features</Link>
                <Link href="/#pricing" onClick={() => setMobileMenuOpen(false)} className="text-charcoal hover:text-primary transition-colors font-medium py-4 block">Pricing</Link>
                <Link href="/#faq" onClick={() => setMobileMenuOpen(false)} className="text-charcoal hover:text-primary transition-colors font-medium py-4 block">FAQ</Link>
                <a
                  href="https://calendly.com/alec_kleinman/meeting-with-alec"
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => { setMobileMenuOpen(false); trackCTA.bookCall('mobile_nav') }}
                  className="btn-primary text-center"
                >
                  Book a Call
                </a>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section — compact navy gradient */}
      <section id="main-content" className="pt-28 pb-14 md:pt-36 md:pb-20 bg-gradient-to-br from-primary via-primary to-primary-light">
        <div className="section-container">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white leading-tight mb-5">
              How to Use Your <span className="text-accent">Grant Report</span>
            </h1>
            <p className="text-lg md:text-xl text-gray-200 mb-3 max-w-2xl mx-auto leading-relaxed">
              Each report is packed with funder profiles, grant histories, positioning strategies, and action plans. Here&apos;s how to get the most out of every section.
            </p>
            <p className="text-sm text-gray-300 mb-8">
              New to TheGrantScout? This guide works with our{' '}
              <a
                href="/sample-report.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="underline hover:text-accent transition-colors"
                onClick={() => trackCTA.sampleReport('report_guide_hero')}
              >
                sample report
              </a>.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <a
                href="/sample-report.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary inline-flex items-center gap-2 text-lg px-8 py-4 shadow-xl hover:shadow-2xl transform hover:-translate-y-1"
                onClick={() => trackCTA.sampleReport('report_guide_hero')}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download Sample Report
              </a>
              <a
                href="https://calendly.com/alec_kleinman/meeting-with-alec"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-white hover:text-accent font-medium transition-colors border border-white/30 rounded-lg px-6 py-3"
                onClick={() => trackCTA.bookCall('report_guide_hero')}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Book a Call
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content — Accordion walkthrough */}
      <section className="py-12 md:py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Section header + Expand/Collapse toggle */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mb-10">
            <div className="text-center sm:text-left">
              <span className="inline-block px-4 py-1.5 bg-accent/10 text-accent-dark rounded-full text-xs font-semibold mb-3">
                REPORT WALKTHROUGH
              </span>
            </div>
            <button
              onClick={toggleAll}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full border border-gray-300 text-sm font-medium text-charcoal hover:bg-gray-50 hover:border-primary transition-colors min-h-[44px]"
            >
              <svg className={`w-4 h-4 transition-transform duration-300 ${allOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
              {allOpen ? 'Collapse All' : 'Expand All'}
            </button>
          </div>

          {/* Accordion groups */}
          {groupOrder.map((groupKey, groupIndex) => {
            const groupSections = reportSections.filter((s) => s.group === groupKey)
            return (
              <div key={groupKey} className="mb-10">
                {/* Group heading */}
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 bg-accent rounded-full flex items-center justify-center text-sm font-bold text-primary flex-shrink-0">
                    {groupIndex + 1}
                  </div>
                  <h2 className="text-xl md:text-2xl font-bold text-primary">
                    {groupLabels[groupKey]}
                  </h2>
                </div>

                <div className="space-y-3">
                  {groupSections.map((section) => {
                    const isOpen = openSections.has(section.id)
                    return (
                      <div
                        key={section.id}
                        id={section.id}
                        className={`bg-white rounded-xl shadow-md overflow-hidden transition-all duration-300 ${isOpen ? 'ring-2 ring-accent shadow-lg' : 'hover:shadow-lg'}`}
                      >
                        {/* Accordion button */}
                        <button
                          type="button"
                          id={`heading-${section.id}`}
                          className="w-full px-5 py-5 text-left flex items-center gap-4 cursor-pointer min-h-[56px]"
                          onClick={() => toggleSection(section.id)}
                          aria-expanded={isOpen}
                          aria-controls={`panel-${section.id}`}
                        >
                          <div className="w-8 h-8 bg-accent/10 rounded-lg flex items-center justify-center flex-shrink-0">
                            <svg className="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          </div>
                          <div className="flex-1 min-w-0">
                            <span className="font-semibold text-primary text-lg block">{section.title}</span>
                            <span className="text-sm text-gray-500">{section.description}</span>
                          </div>
                          <span className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${isOpen ? 'bg-accent text-primary rotate-180' : 'bg-gray-100 text-gray-500'}`}>
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                          </span>
                        </button>

                        {/* Expanded panel */}
                        <div
                          id={`panel-${section.id}`}
                          role="region"
                          aria-labelledby={`heading-${section.id}`}
                          className={`transition-all duration-300 ease-in-out overflow-hidden ${isOpen ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0'}`}
                        >
                          <div className="px-5 pb-6 space-y-5">
                            {/* What's in This Section */}
                            <div>
                              <h4 className="text-sm font-semibold text-primary uppercase tracking-wide mb-2">
                                What&apos;s in This Section
                              </h4>
                              <ul className="space-y-1.5">
                                {section.whatsInIt.map((item, i) => (
                                  <li key={i} className="flex items-start gap-2 text-gray-600">
                                    <svg className="w-4 h-4 text-accent mt-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                    <span>{item}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>

                            {/* What It Means for You */}
                            <div>
                              <h4 className="text-sm font-semibold text-primary uppercase tracking-wide mb-2">
                                What It Means for You
                              </h4>
                              <p className="text-gray-600 leading-relaxed">
                                {section.whatItMeans}
                              </p>
                            </div>

                            {/* Example from the Report */}
                            <div>
                              <h4 className="text-sm font-semibold text-primary uppercase tracking-wide mb-2">
                                Example from the Report
                              </h4>
                              <div className="border-l-4 border-accent bg-gray-50 rounded-lg p-4">
                                <p className="text-gray-700 text-sm leading-relaxed whitespace-pre-line">
                                  {section.exampleCallout}
                                </p>
                              </div>
                            </div>

                            {/* Inline micro-CTA */}
                            <p className="text-sm text-gray-500">
                              See the full version in our{' '}
                              <a
                                href="/sample-report.pdf"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-primary underline hover:text-accent transition-colors"
                                onClick={() => trackCTA.sampleReport(`report_guide_${section.id}`)}
                              >
                                sample report</a>.
                            </p>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>

                {/* Mid-page CTA after "Understanding Your Foundations" group */}
                {groupKey === 'foundations' && (
                  <div className="mt-10 mb-2 bg-primary/5 border border-primary/10 rounded-xl p-8 text-center">
                    <p className="text-lg font-semibold text-primary mb-2">
                      This is what your report looks like.
                    </p>
                    <p className="text-gray-600 mb-5">
                      Download the full sample to see funder profiles, grant histories, and positioning strategies.
                    </p>
                    <a
                      href="/sample-report.pdf"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-primary inline-flex items-center gap-2 px-8 py-3"
                      onClick={() => trackCTA.sampleReport('report_guide_mid')}
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      Download Sample Report
                    </a>
                  </div>
                )}

                {/* Testimonial after "Taking Action" group */}
                {groupKey === 'action' && (
                  <div className="mt-10 mb-2 bg-gray-50 rounded-xl p-8 text-center">
                    <svg className="w-10 h-10 text-accent/30 mx-auto mb-3" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
                    </svg>
                    <blockquote className="text-lg md:text-xl text-primary font-medium italic mb-3 max-w-2xl mx-auto">
                      &ldquo;The way you broke down the work ensures no action is overlooked.&rdquo;
                    </blockquote>
                    <p className="text-gray-500 text-sm">
                      Mariam, Development Director
                    </p>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </section>

      {/* Bottom CTA Section */}
      <section className="py-16 md:py-20 bg-gradient-to-br from-primary via-primary to-primary-dark relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-96 h-96 bg-accent rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2"></div>
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-accent rounded-full blur-3xl translate-x-1/2 translate-y-1/2"></div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Ready to Get Your First Report?
            </h2>
            <p className="text-lg text-gray-200 mb-8 leading-relaxed">
              Book a 30-minute call to tell us about your organization. Your first report arrives within 48 hours.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <a
                href="https://calendly.com/alec_kleinman/meeting-with-alec"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary text-lg px-10 py-4 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300"
                onClick={() => trackCTA.bookCall('report_guide_bottom')}
              >
                Book a Call
              </a>
              <a
                href="/sample-report.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-white hover:text-accent font-medium transition-colors"
                onClick={() => trackCTA.sampleReport('report_guide_bottom')}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                Download Sample Report
              </a>
            </div>
            <p className="text-gray-300 mt-6 text-sm">Founding Member pricing: from $83/month</p>
          </div>
        </div>
      </section>

      {/* Footer — Full (same as homepage) */}
      <footer className="bg-primary-dark text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-12">
            <div>
              <Link
                href="/"
                className="text-2xl font-bold mb-4 text-accent hover:text-accent-light transition-colors block"
              >
                TheGrantScout
              </Link>
              <p className="text-gray-300 leading-relaxed">
                AI-powered grant matching built on IRS-verified data. Helping nonprofits find foundations already funding work like theirs.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-white">Product</h4>
              <ul className="space-y-3">
                <li><Link href="/#how-it-works" className="text-gray-300 hover:text-accent transition-colors">How It Works</Link></li>
                <li><Link href="/#features" className="text-gray-300 hover:text-accent transition-colors">Features</Link></li>
                <li><Link href="/#pricing" className="text-gray-300 hover:text-accent transition-colors">Pricing</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-white">Support</h4>
              <ul className="space-y-3">
                <li><Link href="/#faq" className="text-gray-300 hover:text-accent transition-colors">FAQ</Link></li>
                <li><Link href="/how-to-use-your-report" className="text-gray-300 hover:text-accent transition-colors">Report Guide</Link></li>
                <li><a href="mailto:hello@thegrantscout.com" className="text-gray-300 hover:text-accent transition-colors">Contact Us</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-white">Legal</h4>
              <ul className="space-y-3">
                <li><Link href="/privacy" className="text-gray-300 hover:text-accent transition-colors">Privacy Policy</Link></li>
                <li><Link href="/terms" className="text-gray-300 hover:text-accent transition-colors">Terms of Service</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-primary-light/20 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-gray-400 text-sm">&copy; {new Date().getFullYear()} TheGrantScout. All rights reserved.</p>
            <p className="text-gray-400 text-sm">Built for nonprofits, by people who understand the grant landscape.</p>
          </div>
        </div>
      </footer>

      {/* FAQPage Structured Data (for rich snippets) */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            mainEntity: reportSections.map((section) => ({
              '@type': 'Question',
              name: `What is the "${section.title}" section of a grant report?`,
              acceptedAnswer: {
                '@type': 'Answer',
                text: `${section.whatItMeans} This section includes: ${section.whatsInIt.join('; ')}.`,
              },
            })),
          }),
        }}
      />
    </div>
  )
}
