import { isAuthenticated } from '@/lib/crm-auth'
import CRMShell from './CRMShell'
import '@/styles/crm.css'

export const metadata = {
  title: 'CRM | TheGrantScout',
  robots: { index: false, follow: false },
}

export default async function CRMLayout({ children }: { children: React.ReactNode }) {
  const authed = await isAuthenticated()

  if (!authed) {
    return <>{children}</>
  }

  return <CRMShell>{children}</CRMShell>
}
