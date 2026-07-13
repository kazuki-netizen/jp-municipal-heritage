// POST /api/signup — instant, keyless API-key issuance (v1).
//
// Body: {"email": "you@example.com"} → returns a stateless signed key:
//   key = base64url( email + "." + HMAC-SHA256-hex(email, JMH_API_SECRET) )
// No verification email is sent (v1 trade-off, documented in API.md).
// The same email always yields the same key, so "I lost my key" is solved
// by signing up again.

import { createHmac } from "node:crypto";

const DOCS_URL =
  "https://github.com/kazuki-netizen/jp-municipal-heritage/blob/main/API.md";

// Pragmatic format check only (no deliverability check in v1).
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export default function handler(req: any, res: any) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "content-type");
  res.setHeader("Cache-Control", "no-store");

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }
  if (req.method !== "POST") {
    return res.status(405).json({
      error:
        'Use POST with a JSON body: {"email": "you@example.com"}. Example: curl -X POST -H "content-type: application/json" -d \'{"email":"you@example.com"}\' https://jp-municipal-heritage.vercel.app/api/signup',
      docs: DOCS_URL,
    });
  }

  const secret = process.env.JMH_API_SECRET;
  if (!secret) {
    return res
      .status(500)
      .json({ error: "API auth is not configured on the server." });
  }

  let body: any = req.body;
  if (typeof body === "string") {
    try {
      body = JSON.parse(body);
    } catch {
      body = null;
    }
  }
  const email = String(body?.email ?? "")
    .trim()
    .toLowerCase();

  if (!email || email.length > 254 || !EMAIL_RE.test(email)) {
    return res.status(400).json({
      error:
        'Invalid or missing email. Send a JSON body: {"email": "you@example.com"}.',
      docs: DOCS_URL,
    });
  }

  const sig = createHmac("sha256", secret).update(email).digest("hex");
  const key = Buffer.from(`${email}.${sig}`, "utf8").toString("base64url");

  return res.status(200).json({
    email,
    key,
    usage: {
      header: "x-api-key: <key>",
      query: "?key=<key>",
      example: `curl -s -H "x-api-key: ${key}" https://jp-municipal-heritage.vercel.app/api/v1/index.json`,
    },
    note:
      "Keep this key. No verification email is sent; signing up again with the same email returns the same key. The key encodes your email address (base64url) — do not share it publicly.",
    docs: DOCS_URL,
  });
}
