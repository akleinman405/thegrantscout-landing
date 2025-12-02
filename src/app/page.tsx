'use client'

import { useState } from 'react'

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
              <a href="#cta" className="btn-primary">Get Started</a>
            </div>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
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
              <div className="flex flex-col space-y-4">
                <a href="#how-it-works" onClick={() => setMobileMenuOpen(false)} className="text-charcoal hover:text-primary transition-colors font-medium py-2">How It Works</a>
                <a href="#features" onClick={() => setMobileMenuOpen(false)} className="text-charcoal hover:text-primary transition-colors font-medium py-2">Features</a>
                <a href="#pricing" onClick={() => setMobileMenuOpen(false)} className="text-charcoal hover:text-primary transition-colors font-medium py-2">Pricing</a>
                <a href="#faq" onClick={() => setMobileMenuOpen(false)} className="text-charcoal hover:text-primary transition-colors font-medium py-2">FAQ</a>
                <a href="#cta" onClick={() => setMobileMenuOpen(false)} className="btn-primary text-center">Get Started</a>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 md:pt-40 md:pb-28 bg-gradient-to-br from-primary via-primary to-primary-light">
        <div className="section-container">
          <div className="max-w-5xl mx-auto text-center">
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
              <span className="whitespace-nowrap">Your mission deserves funding.</span>
              <br className="hidden sm:block" />
              <span className="sm:hidden"> </span>
              <span className="text-accent">We&apos;ll help you find it.</span>
            </h1>
            <p className="text-lg md:text-xl lg:text-2xl text-gray-200 mb-10 max-w-3xl mx-auto leading-relaxed">
              TheGrantScout uses AI to match your nonprofit with foundations already supporting work like yours.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <a href="#cta" className="btn-primary inline-block text-lg px-10 py-4 shadow-xl hover:shadow-2xl transform hover:-translate-y-1">
                Get Your First Report Free
              </a>
            </div>
            <p className="text-gray-300 mt-6 text-sm">No credit card required</p>

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

      {/* Data Authority Section */}
      <section className="py-16 md:py-20 bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <span className="inline-block px-4 py-1 bg-primary/10 text-primary rounded-full text-sm font-semibold mb-4">OUR DATA ADVANTAGE</span>
            <h2 className="text-3xl md:text-4xl font-bold text-primary mb-4">Built on the Most Authoritative Foundation Data</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Every match is grounded in official IRS filings—not web scraping or incomplete databases.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center p-6 rounded-xl hover:bg-gray-50 transition-all duration-300">
              <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div className="text-3xl font-bold text-primary mb-2">IRS 990-PF</div>
              <div className="text-gray-600">Verified Data Source</div>
              <p className="text-sm text-gray-500 mt-2">Official foundation tax filings—the same data used by major research institutions.</p>
            </div>

            <div className="text-center p-6 rounded-xl hover:bg-gray-50 transition-all duration-300">
              <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="text-3xl font-bold text-primary mb-2">1.6M+</div>
              <div className="text-gray-600">Grants Analyzed</div>
              <p className="text-sm text-gray-500 mt-2">Comprehensive giving history to identify foundations funding work like yours.</p>
            </div>

            <div className="text-center p-6 rounded-xl hover:bg-gray-50 transition-all duration-300">
              <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="text-3xl font-bold text-primary mb-2">8 Years</div>
              <div className="text-gray-600">Of Giving Patterns</div>
              <p className="text-sm text-gray-500 mt-2">Analyze trends from 2016-2024 to find consistent funders in your space.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="section-container">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 bg-accent/10 text-accent-dark rounded-full text-sm font-semibold mb-4">SIMPLE PROCESS</span>
          <h2 className="heading-2">How It Works</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Get matched with relevant grant opportunities in four simple steps
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 relative">
          {/* Connecting line for desktop */}
          <div className="hidden lg:block absolute top-8 left-[12.5%] right-[12.5%] h-0.5 bg-gradient-to-r from-accent/20 via-accent to-accent/20"></div>

          <div className="text-center group">
            <div className="w-16 h-16 bg-accent rounded-full flex items-center justify-center text-3xl font-bold text-primary mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300 relative z-10">
              1
            </div>
            <h3 className="text-xl font-semibold text-primary mb-3">Tell Us About You</h3>
            <p className="text-gray-600">
              Share your nonprofit&apos;s mission, programs, and the communities you serve.
            </p>
          </div>

          <div className="text-center group">
            <div className="w-16 h-16 bg-accent rounded-full flex items-center justify-center text-3xl font-bold text-primary mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300 relative z-10">
              2
            </div>
            <h3 className="text-xl font-semibold text-primary mb-3">AI Analyzes IRS Data</h3>
            <p className="text-gray-600">
              Our AI analyzes 1.6M+ grants from IRS Form 990-PF filings to identify foundations funding similar missions.
            </p>
          </div>

          <div className="text-center group">
            <div className="w-16 h-16 bg-accent rounded-full flex items-center justify-center text-3xl font-bold text-primary mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300 relative z-10">
              3
            </div>
            <h3 className="text-xl font-semibold text-primary mb-3">Get Matched Results</h3>
            <p className="text-gray-600">
              Receive a curated list of foundations with contact info and giving history.
            </p>
          </div>

          <div className="text-center group">
            <div className="w-16 h-16 bg-accent rounded-full flex items-center justify-center text-3xl font-bold text-primary mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300 relative z-10">
              4
            </div>
            <h3 className="text-xl font-semibold text-primary mb-3">Apply with Confidence</h3>
            <p className="text-gray-600">
              Reach out knowing these foundations have funded organizations like yours.
            </p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="section-container bg-gray-50">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 bg-primary/10 text-primary rounded-full text-sm font-semibold mb-4">POWERFUL FEATURES</span>
          <h2 className="heading-2">Why Choose TheGrantScout</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Intelligent features that save you time and improve your grant success rate
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <div className="card group hover:border-accent border-2 border-transparent">
            <div className="w-14 h-14 bg-accent/10 rounded-xl flex items-center justify-center mb-5 group-hover:bg-accent group-hover:scale-110 transition-all duration-300">
              <svg className="w-7 h-7 text-accent group-hover:text-primary transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 className="heading-3">Smart Matching</h3>
            <p className="text-gray-600">
              We analyze 8 years of IRS-verified giving data to match you with foundations that have a proven track record of funding organizations like yours.
            </p>
            <div className="mt-4 text-sm text-accent font-semibold">Curated matches from verified data</div>
          </div>

          <div className="card group hover:border-accent border-2 border-transparent">
            <div className="w-14 h-14 bg-accent/10 rounded-xl flex items-center justify-center mb-5 group-hover:bg-accent group-hover:scale-110 transition-all duration-300">
              <svg className="w-7 h-7 text-accent group-hover:text-primary transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="heading-3">Data-Driven Insights</h3>
            <p className="text-gray-600">
              Get detailed information on grant amounts, application deadlines, geographic preferences, and historical giving trends.
            </p>
            <div className="mt-4 text-sm text-accent font-semibold">1.6M+ grants analyzed</div>
          </div>

          <div className="card group hover:border-accent border-2 border-transparent">
            <div className="w-14 h-14 bg-accent/10 rounded-xl flex items-center justify-center mb-5 group-hover:bg-accent group-hover:scale-110 transition-all duration-300">
              <svg className="w-7 h-7 text-accent group-hover:text-primary transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="heading-3">Save Time</h3>
            <p className="text-gray-600">
              Stop spending hours researching grants. Get a curated list of relevant opportunities delivered to you in minutes, not weeks.
            </p>
            <div className="mt-4 text-sm text-accent font-semibold">20 hours saved per month</div>
          </div>

          <div className="card group hover:border-accent border-2 border-transparent">
            <div className="w-14 h-14 bg-accent/10 rounded-xl flex items-center justify-center mb-5 group-hover:bg-accent group-hover:scale-110 transition-all duration-300">
              <svg className="w-7 h-7 text-accent group-hover:text-primary transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
            <h3 className="heading-3">Always Updated</h3>
            <p className="text-gray-600">
              We continuously monitor foundation activity and update our database with the latest 990 filings to ensure you have current information.
            </p>
            <div className="mt-4 text-sm text-accent font-semibold">Updated quarterly</div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="section-container">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 bg-primary/10 text-primary rounded-full text-sm font-semibold mb-4">PRICING</span>
          <h2 className="heading-2">Simple, Transparent Pricing</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Choose the plan that works for your organization
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {/* Starter Plan */}
          <div className="card border-2 border-gray-200 hover:border-accent transition-colors duration-300">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-primary mb-2">Starter</h3>
              <div className="text-4xl font-bold text-primary mb-2">$49</div>
              <div className="text-gray-600">per report</div>
            </div>
            <ul className="space-y-3 mb-8">
              <li className="flex items-start">
                <span className="text-accent mr-2">✓</span>
                <span>One comprehensive grant report</span>
              </li>
              <li className="flex items-start">
                <span className="text-accent mr-2">✓</span>
                <span>Up to 25 matched foundations</span>
              </li>
              <li className="flex items-start">
                <span className="text-accent mr-2">✓</span>
                <span>Contact information included</span>
              </li>
              <li className="flex items-start">
                <span className="text-accent mr-2">✓</span>
                <span>Basic giving history</span>
              </li>
            </ul>
            <a href="#cta" className="btn-secondary w-full text-center block">
              Get Started
            </a>
          </div>

          {/* Professional Plan */}
          <div className="card border-2 border-accent shadow-2xl transform md:scale-105 hover:border-accent-dark transition-colors duration-300">
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <span className="bg-accent text-primary px-4 py-1 rounded-full text-sm font-semibold">
                MOST POPULAR
              </span>
            </div>
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-primary mb-2">Professional</h3>
              <div className="text-4xl font-bold text-primary mb-2">$149</div>
              <div className="text-gray-600">per month</div>
            </div>
            <ul className="space-y-3 mb-8">
              <li className="flex items-start">
                <span className="text-accent mr-2">✓</span>
                <span>2 detailed reports per month</span>
              </li>
              <li className="flex items-start">
                <span className="text-accent mr-2">✓</span>
                <span>Up to 50 matched foundations per report</span>
              </li>
              <li className="flex items-start">
                <span className="text-accent mr-2">✓</span>
                <span>Advanced analytics and insights</span>
              </li>
              <li className="flex items-start">
                <span className="text-accent mr-2">✓</span>
                <span>Priority email support</span>
              </li>
              <li className="flex items-start">
                <span className="text-accent mr-2">✓</span>
                <span>Quarterly updates on your matches</span>
              </li>
            </ul>
            <a href="#cta" className="btn-primary w-full text-center block">
              Get Started
            </a>
          </div>

          {/* Enterprise Plan */}
          <div className="card border-2 border-gray-200 hover:border-accent transition-colors duration-300">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-primary mb-2">Enterprise</h3>
              <div className="text-4xl font-bold text-primary mb-2">Custom</div>
              <div className="text-gray-600">contact us</div>
            </div>
            <ul className="space-y-3 mb-8">
              <li className="flex items-start">
                <span className="text-accent mr-2">✓</span>
                <span>Unlimited reports</span>
              </li>
              <li className="flex items-start">
                <span className="text-accent mr-2">✓</span>
                <span>Unlimited foundation matches</span>
              </li>
              <li className="flex items-start">
                <span className="text-accent mr-2">✓</span>
                <span>Custom integrations</span>
              </li>
              <li className="flex items-start">
                <span className="text-accent mr-2">✓</span>
                <span>Dedicated account manager</span>
              </li>
              <li className="flex items-start">
                <span className="text-accent mr-2">✓</span>
                <span>API access</span>
              </li>
            </ul>
            <a href="#cta" className="btn-secondary w-full text-center block">
              Contact Sales
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

        <div className="max-w-3xl mx-auto space-y-4">
          {faqData.map((faq, index) => (
            <div
              key={index}
              className={`bg-white rounded-xl shadow-md overflow-hidden transition-all duration-300 ${openFaq === index ? 'ring-2 ring-accent shadow-lg' : 'hover:shadow-lg'}`}
            >
              <button
                type="button"
                className="w-full px-6 py-5 text-left flex justify-between items-center gap-4 cursor-pointer"
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
      <section id="cta" className="py-20 md:py-28 bg-gradient-to-br from-primary via-primary to-primary-dark relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-96 h-96 bg-accent rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2"></div>
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-accent rounded-full blur-3xl translate-x-1/2 translate-y-1/2"></div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-6">
              Ready to Find Your Next Grant?
            </h2>
            <p className="text-xl text-gray-200 mb-10 leading-relaxed">
              Get your first report free and discover foundations that are already funding work like yours.
            </p>
            <div className="max-w-md mx-auto">
              <form className="space-y-4">
                <input
                  type="text"
                  placeholder="Your Name"
                  className="w-full px-5 py-4 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent bg-white/95 text-charcoal placeholder-gray-400 shadow-lg"
                />
                <input
                  type="email"
                  placeholder="Organization Email"
                  className="w-full px-5 py-4 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent bg-white/95 text-charcoal placeholder-gray-400 shadow-lg"
                />
                <input
                  type="text"
                  placeholder="Organization Name"
                  className="w-full px-5 py-4 rounded-xl focus:outline-none focus:ring-2 focus:ring-accent bg-white/95 text-charcoal placeholder-gray-400 shadow-lg"
                />
                <button type="submit" className="btn-primary w-full text-lg py-4 shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300">
                  Get My Free Report
                </button>
              </form>
              <p className="text-gray-300 mt-6 text-sm flex items-center justify-center gap-2">
                <svg className="w-5 h-5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                No credit card required. Results delivered within 48 hours.
              </p>
            </div>
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
                <li><a href="#" className="text-gray-300 hover:text-accent transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="text-gray-300 hover:text-accent transition-colors">Terms of Service</a></li>
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
    answer: "We'll ask about your organization's mission, programs, geographic focus, annual budget, and the populations you serve. The more detail you provide, the better we can match you with relevant foundations."
  },
  {
    question: "How long does it take to get results?",
    answer: "Most reports are delivered within 48 hours. For professional and enterprise plans with more complex matching requirements, it may take up to 3-5 business days."
  },
  {
    question: "Is my first report really free?",
    answer: "Yes! We offer one free report so you can experience the quality of our matching service. No credit card required, and there's no obligation to purchase additional reports."
  },
  {
    question: "What's included in a grant report?",
    answer: "Each report includes a list of matched foundations with contact information, giving history, typical grant ranges, application deadlines, geographic preferences, and insights on why they're a good match for your organization."
  },
  {
    question: "Can I cancel my subscription anytime?",
    answer: "Absolutely. All monthly subscriptions can be cancelled at any time. You'll continue to have access through the end of your billing period."
  },
  {
    question: "Do you guarantee I'll get grants?",
    answer: "We can't guarantee you'll receive funding, but we significantly improve your chances by matching you with foundations that have a proven track record of funding organizations like yours. Our users report a higher success rate compared to traditional grant research methods."
  },
  {
    question: "How current is your foundation data?",
    answer: "We update our database regularly as new 990 forms are filed with the IRS. Most foundation data is updated quarterly, ensuring you have access to the most recent giving patterns and contact information."
  }
]
