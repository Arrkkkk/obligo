import { buttonVariants } from "@/components/ui/button";

const CORE_URL = process.env.NEXT_PUBLIC_CORE_URL ?? "http://localhost:8080";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-2xl font-semibold">obligo</h1>
      <p className="text-muted-foreground">Phase 2 — identity, tenancy & authorization.</p>
      {/* Plain <a>, not a Next.js <Link>: this must be a real browser
          navigation to core, not a client-side route change — core owns
          the whole Google OAuth2+PKCE exchange (§10.1/§10.2). */}
      <a href={`${CORE_URL}/oauth2/authorization/google`} className={buttonVariants({})}>
        Sign in with Google
      </a>
    </main>
  );
}
