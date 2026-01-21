'use client'

import { useState } from 'react'
import Link from 'next/link'
import { trackCTA } from '@/components/GoogleAnalytics'

export default function Navigation() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
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
            <a href="https://calendly.com/alec_kleinman/meeting-with-alec" target="_blank" rel="noopener noreferrer" className="btn-primary min-h-[44px]" onClick={() => trackCTA.bookCall('nav')}>Book a Call</a>
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
              <a href="https://calendly.com/alec_kleinman/meeting-with-alec" target="_blank" rel="noopener noreferrer" onClick={() => { setMobileMenuOpen(false); trackCTA.bookCall('mobile_nav'); }} className="btn-primary text-center">Book a Call</a>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
