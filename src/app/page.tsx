'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function Home() {
  const [openFaq, setOpenFaq] = useState<number | null>(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const toggleFaq = (index: number) => {
    setOpenFaq(openFaq === index ? null : index)
  }

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Skip to main content for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[200] focus:bg-white focus:px-4 focus:py-2 focus:rounded focus:shadow-lg focus:text-primary"
      >
        Skip to main content
      </a>

      {/* Navigation */}
      <nav className="fixed w-full bg-white/95 backdrop-blur-sm shadow-sm z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={scrollToTop}
                className="text-2xl font-bold text-primary hover:text-primary-light transition-colors cursor-pointer"
              >
                TheGrantScout
              </button>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <a href="#how-it-works" className="text-charcoal hover:text-primary transition-colors font-medium">How It Works</a>
              <a href="#features" className="text-charcoal hover:text-primary transition-colors font-medium">Features</a>
              <a href="#pricing" className="text-charcoal hover:text-primary transition-colors font-medium">Pricing</a>
              <a href="#faq" className="text-charcoal hover:text-primary transition-colors font-medium">FAQ</a>
              <a href="https://calendly.com/alec_kleinman/meeting-with-alec" target="_blank" rel="noopener noreferrer" className="btn-primary min-h-[44px]">Book a Call</a>
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
                <a href="#how-it-works" onClick={() => setMobileMenuOpen(false)} className="text-charcoal hover:text-primary transition-colors font-medium py-4 block">How It Works</a>
                <a href="#features" onClick={() => setMobileMenuOpen(false)} className="text-charcoal hover:text-primary transition-colors font-medium py-4 block">Features</a>
                <a href="#pricing" onClick={() => setMobileMenuOpen(false)} className="text-charcoal hover:text-primary transition-colors font-medium py-4 block">Pricing</a>
                <a href="#faq" onClick={() => setMobileMenuOpen(false)} className="text-charcoal hover:text-primary transition-colors font-medium py-4 block">FAQ</a>
                <a href="https://calendly.com/alec_kleinman/meeting-with-alec" target="_blank" rel="noopener noreferrer" onClick={() => setMobileMenuOpen(false)} className="btn-primary text-center">Book a Call</a>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section id="main-content" className="pt-32 pb-20 md:pt-40 md:pb-28 bg-gradient-to-br from-primary via-primary to-primary-light">
        <div className="section-container">
          <div className="max-w-5xl mx-auto text-center">
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
              <span className="block sm:inline">Your mission deserves</span>
              <span className="block sm:inline"> funding.</span>
              <br className="hidden sm:block" />
              <span className="text-accent block sm:inline mt-2 sm:mt-0">We&apos;ll help you find it.</span>
            </h1>
            <p className="text-lg md:text-xl lg:text-2xl text-gray-200 mb-10 max-w-3xl mx-auto leading-relaxed px-2">
              Every month, get a curated report of foundations funding work like yours—with funder intel, positioning strategy, and everything you need to apply confidently.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <a
                href="https://calendly.com/alec_kleinman/meeting-with-alec"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary inline-block text-lg px-10 py-4 shadow-xl hover:shadow-2xl transform hover:-translate-y-1"
              >
                Book a Call
              </a>
              <a
                href="/sample-report.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-white hover:text-accent font-medium transition-colors border border-white/30 rounded-lg px-6 py-3"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                See a Sample Report
              </a>
            </div>
            <p className="text-gray-300 mt-6 text-sm">Founding Member pricing: $99/month</p>

            {/* Trust Indicators */}
            <div className="flex flex-wrap justify-center gap-4 md:gap-8 mt-8 text-gray-200 text-sm">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <span>IRS-Verified Data</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                <span>1.6M+ Grants Analyzed</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                <span>85,000+ Foundations</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Data Authority Section - Compact */}
      <section className="py-10 md:py-12 bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-6">
            <span className="inline-block px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-semibold mb-2">OUR DATA ADVANTAGE</span>
            <p className="text-lg text-gray-600 max-w-xl mx-auto">
              Every match is grounded in official IRS filings.
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-4 md:gap-8 max-w-4xl mx-auto">
            <div className="flex items-center gap-3 px-4 py-3 bg-gray-50 rounded-lg">
              <div className="w-10 h-10 bg-accent/10 rounded-full flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <div className="text-lg font-bold text-primary">IRS 990-PF</div>
                <div className="text-sm text-gray-500">Verified Data</div>
              </div>
            </div>

            <div className="flex items-center gap-3 px-4 py-3 bg-gray-50 rounded-lg">
              <div className="w-10 h-10 bg-accent/10 rounded-full flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <div className="text-lg font-bold text-primary">1.6M+</div>
                <div className="text-sm text-gray-500">Grants Analyzed</div>
              </div>
            </div>

            <div className="flex items-center gap-3 px-4 py-3 bg-gray-50 rounded-lg">
              <div className="w-10 h-10 bg-accent/10 rounded-full flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <div className="text-lg font-bold text-primary">8 Years</div>
                <div className="text-sm text-gray-500">Of Giving Data</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works - Compact */}
      <section id="how-it-works" className="py-12 md:py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8 md:mb-12">
          <span className="inline-block px-3 py-1 bg-accent/10 text-accent-dark rounded-full text-xs font-semibold mb-3">SIMPLE PROCESS</span>
          <h2 className="heading-2">How It Works</h2>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 relative">
          {/* Connecting line for desktop */}
          <div className="hidden lg:block absolute top-6 left-[12.5%] right-[12.5%] h-0.5 bg-gradient-to-r from-accent/20 via-accent to-accent/20"></div>

          <div className="text-center group p-3 md:p-4">
            <div className="w-12 h-12 md:w-14 md:h-14 bg-accent rounded-full flex items-center justify-center text-xl md:text-2xl font-bold text-primary mx-auto mb-3 shadow-lg group-hover:scale-110 transition-transform duration-300 relative z-10">
              1
            </div>
            <h3 className="text-base md:text-lg font-semibold text-primary mb-2">Tell Us About You</h3>
            <p className="text-sm text-gray-600">
              Share your mission, the communities you serve, and your funding goals.
            </p>
          </div>

          <div className="text-center group p-3 md:p-4">
            <div className="w-12 h-12 md:w-14 md:h-14 bg-accent rounded-full flex items-center justify-center text-xl md:text-2xl font-bold text-primary mx-auto mb-3 shadow-lg group-hover:scale-110 transition-transform duration-300 relative z-10">
              2
            </div>
            <h3 className="text-base md:text-lg font-semibold text-primary mb-2">AI Analyzes Data</h3>
            <p className="text-sm text-gray-600">
              We analyze 1.6M+ grants from IRS filings.
            </p>
          </div>

          <div className="text-center group p-3 md:p-4">
            <div className="w-12 h-12 md:w-14 md:h-14 bg-accent rounded-full flex items-center justify-center text-xl md:text-2xl font-bold text-primary mx-auto mb-3 shadow-lg group-hover:scale-110 transition-transform duration-300 relative z-10">
              3
            </div>
            <h3 className="text-base md:text-lg font-semibold text-primary mb-2">Get Your Report</h3>
            <p className="text-sm text-gray-600">
              Receive your monthly report via email—packed with opportunities, funder intel, and positioning advice.
            </p>
          </div>

          <div className="text-center group p-3 md:p-4">
            <div className="w-12 h-12 md:w-14 md:h-14 bg-accent rounded-full flex items-center justify-center text-xl md:text-2xl font-bold text-primary mx-auto mb-3 shadow-lg group-hover:scale-110 transition-transform duration-300 relative z-10">
              4
            </div>
            <h3 className="text-base md:text-lg font-semibold text-primary mb-2">Apply Confidently</h3>
            <p className="text-sm text-gray-600">
              Reach out to proven funders in your space.
            </p>
          </div>
        </div>
      </section>

      {/* Features - Compact 2-card layout */}
      <section id="features" className="py-12 md:py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8 md:mb-12">
            <span className="inline-block px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-semibold mb-3">WHY THEGRANTSCOUT</span>
            <h2 className="heading-2">Save Time, Find Better Opportunities</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all duration-300 border-2 border-transparent hover:border-accent">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-primary mb-2">Smart AI Matching</h3>
                  <p className="text-gray-600 text-sm">Match with foundations that have a proven track record of funding organizations like yours. 8 years of verified IRS data.</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-all duration-300 border-2 border-transparent hover:border-accent">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-primary mb-2">Save 20+ Hours Monthly</h3>
                  <p className="text-gray-600 text-sm">Stop spending hours researching grants. Get a curated list of relevant opportunities delivered in minutes, not weeks.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing - Single Founding Member Offer */}
      <section id="pricing" className="py-12 md:py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-10">
          <span className="inline-block px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-semibold mb-3">FOUNDING MEMBER PRICING</span>
          <h2 className="heading-2">Join as a Founding Member</h2>
          <p className="text-lg text-gray-600 max-w-xl mx-auto">
            Early adopter pricing — limited availability
          </p>
        </div>

        <div className="max-w-md mx-auto">
          <div className="bg-white rounded-2xl p-8 shadow-xl border-2 border-accent relative">
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <span className="bg-accent text-primary px-4 py-1 rounded-full text-sm font-semibold">
                FOUNDING MEMBER
              </span>
            </div>
            <div className="text-center mb-6 pt-2">
              <div className="text-5xl font-bold text-primary mb-2">$99</div>
              <div className="text-gray-600">per month</div>
            </div>
            <div className="mb-6">
              <div className="flex items-start mb-4">
                <svg className="w-5 h-5 text-accent mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>Monthly PDF report delivered to your inbox</span>
              </div>
              <div className="flex items-start mb-4">
                <svg className="w-5 h-5 text-accent mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>Email support</span>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <h4 className="font-semibold text-primary mb-3 text-sm">What&apos;s Inside Each Report</h4>
              <div className="grid grid-cols-1 gap-2 text-sm">
                <div className="flex items-start gap-2">
                  <svg className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  <div><strong>Curated Opportunities</strong> — Foundations actively funding work like yours</div>
                </div>
                <div className="flex items-start gap-2">
                  <svg className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  <div><strong>Funder Profiles</strong> — Giving history, grant ranges, geographic focus</div>
                </div>
                <div className="flex items-start gap-2">
                  <svg className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  <div><strong>Positioning Strategy</strong> — How to approach each funder based on their patterns</div>
                </div>
                <div className="flex items-start gap-2">
                  <svg className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  <div><strong>Contact Information</strong> — Direct contacts and application details</div>
                </div>
                <div className="flex items-start gap-2">
                  <svg className="w-4 h-4 text-accent mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  <div><strong>Approach Recommendations</strong> — What to emphasize in your outreach</div>
                </div>
              </div>
            </div>
            <a
              href="https://calendly.com/alec_kleinman/meeting-with-alec"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary w-full text-center min-h-[48px] text-lg block"
            >
              Book a Call
            </a>
            <p className="text-center text-sm text-gray-500 mt-4">Cancel anytime. No long-term commitment.</p>
          </div>

          {/* Sample Report Link */}
          <div className="text-center mt-8">
            <p className="text-gray-600 mb-3">Want to see what you&apos;ll get?</p>
            <a
              href="/sample-report.pdf"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-primary hover:text-accent font-semibold transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              See a Sample Report
            </a>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="section-container bg-gray-50">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 bg-accent/10 text-accent-dark rounded-full text-sm font-semibold mb-4">GOT QUESTIONS?</span>
          <h2 className="heading-2">Frequently Asked Questions</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Everything you need to know about TheGrantScout
          </p>
        </div>

        <div className="max-w-3xl mx-auto space-y-2">
          {faqData.map((faq, index) => (
            <div
              key={index}
              className={`bg-white rounded-xl shadow-md overflow-hidden transition-all duration-300 ${openFaq === index ? 'ring-2 ring-accent shadow-lg' : 'hover:shadow-lg'}`}
            >
              <button
                type="button"
                className="w-full px-6 py-5 text-left flex justify-between items-center gap-4 cursor-pointer min-h-[56px]"
                onClick={() => toggleFaq(index)}
                aria-expanded={openFaq === index}
              >
                <span className="font-semibold text-primary text-lg">{faq.question}</span>
                <span className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${openFaq === index ? 'bg-accent text-primary rotate-180' : 'bg-gray-100 text-gray-500'}`}>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </span>
              </button>
              <div
                className={`transition-all duration-300 ease-in-out overflow-hidden ${openFaq === index ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'}`}
              >
                <div className="px-6 pb-5 text-gray-600 leading-relaxed">
                  {faq.answer}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section id="cta" className="py-16 md:py-20 bg-gradient-to-br from-primary via-primary to-primary-dark relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-96 h-96 bg-accent rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2"></div>
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-accent rounded-full blur-3xl translate-x-1/2 translate-y-1/2"></div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Ready to Find Your Next Grant?
            </h2>
            <p className="text-lg text-gray-200 mb-8 leading-relaxed">
              Join as a Founding Member. Every month, you&apos;ll get a report with everything you need to confidently pursue your next grant.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <a
                href="https://calendly.com/alec_kleinman/meeting-with-alec"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary text-lg px-10 py-4 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300"
              >
                Book a Call
              </a>
              <a
                href="/sample-report.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-white hover:text-accent font-medium transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                See a Sample Report
              </a>
            </div>
            <p className="text-gray-300 mt-6 text-sm">Founding Member pricing: $99/month</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-primary-dark text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-12">
            <div>
              <button
                onClick={scrollToTop}
                className="text-2xl font-bold mb-4 text-accent hover:text-accent-light transition-colors cursor-pointer"
              >
                TheGrantScout
              </button>
              <p className="text-gray-300 leading-relaxed">
                AI-powered grant matching built on IRS-verified data. Helping nonprofits find foundations already funding work like theirs.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-white">Product</h4>
              <ul className="space-y-3">
                <li><a href="#how-it-works" className="text-gray-300 hover:text-accent transition-colors">How It Works</a></li>
                <li><a href="#features" className="text-gray-300 hover:text-accent transition-colors">Features</a></li>
                <li><a href="#pricing" className="text-gray-300 hover:text-accent transition-colors">Pricing</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-white">Support</h4>
              <ul className="space-y-3">
                <li><a href="#faq" className="text-gray-300 hover:text-accent transition-colors">FAQ</a></li>
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
            <p className="text-gray-400 text-sm">&copy; 2025 TheGrantScout. All rights reserved.</p>
            <p className="text-gray-400 text-sm">Built for nonprofits, by people who understand the grant landscape.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

const faqData = [
  {
    question: "How does TheGrantScout find relevant foundations?",
    answer: "We use advanced AI to analyze IRS Form 990 filings from thousands of foundations. Our algorithm identifies patterns in their giving history and matches them with your organization's mission, programs, and the communities you serve."
  },
  {
    question: "What information do I need to provide?",
    answer: "During our call, we'll ask about your organization's mission, programs, geographic focus, annual budget, and the populations you serve. The more detail you provide, the better we can match you with relevant foundations."
  },
  {
    question: "How long does it take to get results?",
    answer: "Your first report is delivered within 48 hours of your onboarding call. After that, you'll receive a new report via email each month with fresh opportunities tailored to your organization."
  },
  {
    question: "What's included in a grant report?",
    answer: "Each month, you'll receive a PDF report via email containing curated opportunities. For each one, you get: the funder's giving history, typical grant ranges, geographic preferences, direct contact info, and a positioning strategy explaining how to approach them based on their funding patterns."
  },
  {
    question: "Can I cancel my subscription anytime?",
    answer: "Absolutely. All monthly subscriptions can be cancelled at any time. You'll continue to have access through the end of your billing period."
  },
  {
    question: "Do you guarantee I'll get grants?",
    answer: "We can't guarantee you'll receive funding, but we significantly improve your chances by matching you with foundations that have a proven track record of funding organizations like yours."
  },
  {
    question: "How current is your foundation data?",
    answer: "We update our database regularly as new 990 forms are filed with the IRS. Most foundation data is updated quarterly, ensuring you have access to the most recent giving patterns and contact information."
  },
  {
    question: "How do I get started?",
    answer: "Book a call with us to discuss your organization's needs. We'll walk you through how TheGrantScout works and answer any questions. If it's a good fit, we'll get you set up as a Founding Member."
  }
]
