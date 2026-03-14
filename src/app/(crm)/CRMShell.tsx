'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function CRMShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <div className="crm-app">
      {/* Sidebar — matches mockup exactly */}
      <nav className="crm-sidebar">
        <div className="crm-sidebar-brand">
          <h1>TheGrantScout</h1>
          <p>CRM</p>
        </div>
        <div className="crm-sidebar-nav">
          <Link href="/crm" className={pathname === '/crm' ? 'active' : ''}>
            <svg viewBox="0 0 20 20" fill="currentColor"><path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zm10 0a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"/></svg>
            Dashboard
          </Link>
          <Link href="/crm/tasks" className={pathname.startsWith('/crm/tasks') ? 'active' : ''}>
            <svg viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd"/></svg>
            Tasks
          </Link>
          <Link href="/crm/orgs" className={pathname.startsWith('/crm/orgs') ? 'active' : ''}>
            <svg viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 01-1 1h-2a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clipRule="evenodd"/></svg>
            Organizations
          </Link>
          <Link href="/crm/reports" className={pathname.startsWith('/crm/reports') ? 'active' : ''}>
            <svg viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd"/></svg>
            Reports
          </Link>
          <Link href="/crm/meetings" className={pathname.startsWith('/crm/meetings') ? 'active' : ''}>
            <svg viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd"/></svg>
            Meeting Notes
          </Link>
        </div>
        <div className="crm-sidebar-footer">Alec Kleinman</div>
      </nav>

      {/* Main content */}
      <div className="crm-main">
        {children}
      </div>
    </div>
  )
}
