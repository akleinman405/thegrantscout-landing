import Link from 'next/link'

export default function Footer() {
  return (
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
            <h4 className="font-semibold mb-4 text-white">Resources</h4>
            <ul className="space-y-3">
              <li><Link href="/grant-finder" className="text-gray-300 hover:text-accent transition-colors">Grant Finder</Link></li>
              <li><Link href="/foundation-grants" className="text-gray-300 hover:text-accent transition-colors">Foundation Grants</Link></li>
              <li><Link href="/ai-grant-matching" className="text-gray-300 hover:text-accent transition-colors">AI Grant Matching</Link></li>
              <li><Link href="/#faq" className="text-gray-300 hover:text-accent transition-colors">FAQ</Link></li>
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
  )
}
