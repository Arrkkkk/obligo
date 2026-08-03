"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { setAccessToken } from "@/lib/session";

const CORE_URL = process.env.NEXT_PUBLIC_CORE_URL ?? "http://localhost:8080";

// core redirects here after Google sign-in with no token in the URL —
// the refresh token was already set as an HttpOnly cookie server-side.
// This page's only job is to exchange that cookie for the first access
// token via POST /auth/refresh, entirely over XHR, before ever navigating
// anywhere a token could end up in browser history.
export default function AuthCallbackPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${CORE_URL}/api/v1/auth/refresh`, {
      method: "POST",
      credentials: "include",
    })
      .then(async (res) => {
        if (!res.ok) {
          throw new Error(`refresh failed with status ${res.status}`);
        }
        const body = (await res.json()) as { access_token: string };
        setAccessToken(body.access_token);
        router.replace("/dashboard");
      })
      .catch((e) => setError(String(e)));
  }, [router]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-2">
      {error ? (
        <p className="text-destructive">Sign-in failed: {error}</p>
      ) : (
        <p className="text-muted-foreground">Signing you in…</p>
      )}
    </main>
  );
}
