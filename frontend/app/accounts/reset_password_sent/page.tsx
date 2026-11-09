import Link from 'next/link';
export default function Page() { return <main className="container section"><h1>Password reset sent</h1><p>If an active account exists for this email address, you will receive a password reset link.</p><Link href="/accounts/login/">Back to login</Link></main>; }
