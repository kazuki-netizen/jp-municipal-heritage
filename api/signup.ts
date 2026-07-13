// POST /api/signup — API-key issuance.
//
// Body: {"email": "you@example.com"} → a stateless signed key:
//   key = base64url( email + "." + HMAC-SHA256-hex(email, JMH_API_SECRET) )
// The same email always yields the same key, so "I lost my key" is solved
// by signing up again.
//
// Delivery modes:
//   - RESEND_API_KEY + MAIL_FROM set: the key is EMAILED to the address and
//     never returned in the response — receiving it proves inbox ownership.
//   - otherwise: the key is returned directly in the response (v1 fallback,
//     documented in API.md).

import { createHmac } from "node:crypto";

const DOCS_URL =
  "https://github.com/kazuki-netizen/jp-municipal-heritage/blob/main/API.md";

// Pragmatic format check only (no deliverability check in v1).
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

async function sendKeyEmail(email: string, key: string): Promise<void> {
  const from = process.env.MAIL_FROM!;
  const example =
    `curl -s -H "x-api-key: ${key}" https://jp-municipal-heritage.vercel.app/api/v1/index.json`;
  const text = [
    "Your API key for jp-municipal-heritage / APIキーをお送りします",
    "",
    key,
    "",
    "Usage / 使い方:",
    `  ${example}`,
    "",
    "Send the key as an 'x-api-key' header (recommended) or '?key=' query parameter.",
    "Signing up again with this address always returns this same key.",
    "The key encodes your email address — do not share it publicly.",
    "キーは x-api-key ヘッダ（推奨）または ?key= クエリで送ります。",
    "同じアドレスで再登録すると常に同じキーが届きます。紛失時は再登録してください。",
    "",
    `Docs: ${DOCS_URL}`,
    "",
    "If you did not request this key, you can ignore this email — no account",
    "was created and nothing else is stored.",
  ].join("\n");

  const resp = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      authorization: `Bearer ${process.env.RESEND_API_KEY}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      from,
      to: [email],
      subject: "Your jp-municipal-heritage API key / APIキーのご案内",
      text,
    }),
  });
  if (!resp.ok) {
    throw new Error(`mail provider returned ${resp.status}: ${await resp.text()}`);
  }
}

export default async function handler(req: any, res: any) {
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

  // Verified delivery: email the key instead of returning it, so only the
  // inbox owner receives a working key.
  if (process.env.RESEND_API_KEY && process.env.MAIL_FROM) {
    try {
      await sendKeyEmail(email, key);
    } catch (e: any) {
      return res.status(502).json({
        error:
          "Could not send the key email right now. Please try again in a few minutes.",
        docs: DOCS_URL,
      });
    }
    return res.status(200).json({
      sent: true,
      email,
      note:
        "Your API key has been emailed to this address. Signing up again with the same email re-sends the same key. / APIキーをメールで送信しました。届かない場合は迷惑メールフォルダを確認のうえ、再度お試しください。",
      docs: DOCS_URL,
    });
  }

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
