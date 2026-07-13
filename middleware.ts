// Edge Middleware — API key check for /api/* (jp-municipal-heritage API v1).
//
// Key format (issued by /api/signup):
//   key = base64url( email + "." + HMAC-SHA256-hex(email, JMH_API_SECRET) )
// Stateless: no DB. The key itself carries the (normalized) email, so usage
// is attributable per key via the console.log line below in Vercel's logs.
//
// Scope: /api/* only. The map site (/site/*) and bulk files (/data/*) stay
// open. /api/signup is exempt (it is the key-issuing endpoint itself).

export const config = {
  matcher: "/api/:path*",
};

const DOCS_URL =
  "https://github.com/kazuki-netizen/jp-municipal-heritage/blob/main/API.md";

const CORS_HEADERS: Record<string, string> = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "x-api-key, content-type",
};

function json(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      ...CORS_HEADERS,
    },
  });
}

function unauthorized(message: string): Response {
  return json(401, {
    error: message,
    signup: "/api/signup",
    docs: DOCS_URL,
  });
}

function b64urlDecode(s: string): string | null {
  try {
    const b64 = s.replace(/-/g, "+").replace(/_/g, "/");
    const pad = b64.length % 4 === 2 ? "==" : b64.length % 4 === 3 ? "=" : "";
    if (b64.length % 4 === 1) return null;
    return atob(b64 + pad);
  } catch {
    return null;
  }
}

async function hmacHex(message: string, secret: string): Promise<string> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(message));
  return Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) {
    diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return diff === 0;
}

export default async function middleware(
  req: Request,
): Promise<Response | undefined> {
  const url = new URL(req.url);

  // The signup endpoint itself must stay keyless.
  if (url.pathname === "/api/signup") return undefined;

  // CORS preflight for browser clients sending x-api-key.
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS_HEADERS });
  }

  const secret = process.env.JMH_API_SECRET;
  if (!secret) {
    // Fail closed, but distinguishably from a bad key.
    return json(500, { error: "API auth is not configured on the server." });
  }

  const rawKey =
    req.headers.get("x-api-key") || url.searchParams.get("key") || "";
  if (!rawKey) {
    return unauthorized(
      "Missing API key. Send it as an 'x-api-key' header (or '?key=' query parameter). Get a free key instantly: POST /api/signup with JSON body {\"email\": \"you@example.com\"}.",
    );
  }

  const decoded = b64urlDecode(rawKey.trim());
  const sep = decoded ? decoded.lastIndexOf(".") : -1;
  if (!decoded || sep <= 0 || sep === decoded.length - 1) {
    return unauthorized("Malformed API key.");
  }

  const email = decoded.slice(0, sep);
  const givenSig = decoded.slice(sep + 1);
  const expectedSig = await hmacHex(email, secret);
  if (!timingSafeEqual(givenSig, expectedSig)) {
    return unauthorized("Invalid API key.");
  }

  // Attribution: visible in Vercel runtime logs.
  console.log(`jmh-api key-ok email=${email} path=${url.pathname}`);
  return undefined; // continue to the static file / function
}
