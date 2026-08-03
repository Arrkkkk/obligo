// In-memory only — never localStorage/sessionStorage (CLAUDE.md: access
// tokens live in JS memory only). Lost on page refresh by design; the
// callback page re-derives it via POST /auth/refresh, which works because
// the actual credential (the refresh token) lives in an HttpOnly cookie,
// not here.
let accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}
