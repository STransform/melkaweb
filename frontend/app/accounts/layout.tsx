import type { ReactNode } from 'react';

// Account pages use browser-only session/CSRF requests and must not be
// prerendered during a production build.
export const dynamic = 'force-dynamic';

export default function AccountsLayout({ children }: { children: ReactNode }) {
  return children;
}
