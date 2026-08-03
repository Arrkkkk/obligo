"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/session";

const CORE_URL = process.env.NEXT_PUBLIC_CORE_URL ?? "http://localhost:8080";

type Me = {
  userId: string;
  orgId: string;
  role: string;
  orgName: string;
};

// The end-to-end proof surface: this page's only data comes from an
// Authorization-header request that core scopes via TenantContext/RLS
// (see apps/core's MeController) — if isolation were ever wrong, this is
// where it would visibly show up as the wrong org.
export default function DashboardPage() {
  const [me, setMe] = useState<Me | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setError("No access token in memory. Sign in first.");
      return;
    }

    fetch(`${CORE_URL}/api/v1/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(async (res) => {
        if (!res.ok) {
          throw new Error(`request failed with status ${res.status}`);
        }
        setMe((await res.json()) as Me);
      })
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-2">
      {error && <p className="text-destructive">{error}</p>}
      {!error && !me && <p className="text-muted-foreground">Loading…</p>}
      {me && (
        <div className="flex flex-col items-center gap-1">
          <h1 className="text-2xl font-semibold">{me.orgName}</h1>
          <p className="text-muted-foreground">role: {me.role}</p>
          <p className="text-muted-foreground text-xs">user {me.userId}</p>
          <p className="text-muted-foreground text-xs">org {me.orgId}</p>
        </div>
      )}
    </main>
  );
}
