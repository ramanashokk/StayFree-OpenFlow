/**
 * OpenFlow Cloudflare Worker
 * - Verifies Firebase ID token (Google OAuth) using the 'jose' library
 * - Enforces a 2,000 words/day free quota per user (via Workers KV)
 * - Proxies transcription/cleanup requests to Groq, keeping the API key server-side
 *
 * Bindings required (set in wrangler.toml or dashboard):
 *   - USAGE_KV        : Workers KV namespace for daily usage tracking
 *   - GROQ_API_KEY     : secret, your Groq API key
 *   - FIREBASE_PROJECT_ID : secret/var, your Firebase project ID (for token verification)
 *
 * Dependencies (add to package.json): "jose": "^5.x"
 */

import { createRemoteJWKSet, jwtVerify } from "jose";

const DAILY_WORD_LIMIT = 2000;
const FIREBASE_JWKS_URL =
  "https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com";
const jwks = createRemoteJWKSet(new URL(FIREBASE_JWKS_URL));
const GROQ_API_URL = "https://api.groq.com/openai/v1";

export default {
  async fetch(request, env, ctx) {
    // CORS preflight
    if (request.method === "OPTIONS") {
      return corsResponse(new Response(null, { status: 204 }));
    }

    if (request.method !== "POST") {
      return corsResponse(jsonError("Method not allowed", 405));
    }

    const url = new URL(request.url);

    try {
      // 1. Verify Firebase ID token
      const authHeader = request.headers.get("Authorization") || "";
      const idToken = authHeader.replace(/^Bearer\s+/i, "");
      if (!idToken) {
        return corsResponse(jsonError("Missing auth token", 401));
      }

      const userId = await verifyFirebaseToken(idToken, env.FIREBASE_PROJECT_ID);
      if (!userId) {
        return corsResponse(jsonError("Invalid or expired auth token", 401));
      }

      // 2. Check today's usage
      const today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
      const usageKey = `usage:${userId}:${today}`;
      const currentUsageRaw = await env.USAGE_KV.get(usageKey);
      const currentUsage = currentUsageRaw ? parseInt(currentUsageRaw, 10) : 0;

      if (currentUsage >= DAILY_WORD_LIMIT) {
        return corsResponse(
          jsonError(
            `Daily limit reached (${DAILY_WORD_LIMIT} words/day). Resets at midnight UTC.`,
            429
          )
        );
      }

      // 3. Route: /transcribe (audio -> text) or /cleanup (text -> polished text)
      if (url.pathname === "/transcribe") {
        return corsResponse(await handleTranscribe(request, env, userId, usageKey, currentUsage));
      } else if (url.pathname === "/cleanup") {
        return corsResponse(await handleCleanup(request, env, userId, usageKey, currentUsage));
      } else {
        return corsResponse(jsonError("Not found", 404));
      }
    } catch (err) {
      console.error(err);
      return corsResponse(jsonError("Internal error", 500));
    }
  },
};

// ---- Handlers ----

async function handleTranscribe(request, env, userId, usageKey, currentUsage) {
  const formData = await request.formData();
  const audioFile = formData.get("audio");
  const language = formData.get("language") || "en";

  if (!audioFile) {
    return jsonError("Missing audio file", 400);
  }

  const groqForm = new FormData();
  groqForm.append("file", audioFile, "audio.webm");
  groqForm.append("model", "whisper-large-v3");
  groqForm.append("language", language);

  const groqResp = await fetch(`${GROQ_API_URL}/audio/transcriptions`, {
    method: "POST",
    headers: { Authorization: `Bearer ${env.GROQ_API_KEY}` },
    body: groqForm,
  });

  if (!groqResp.ok) {
    const errText = await groqResp.text();
    return jsonError(`Transcription failed: ${errText}`, 502);
  }

  const result = await groqResp.json();
  const wordCount = (result.text || "").trim().split(/\s+/).filter(Boolean).length;

  await incrementUsage(env, usageKey, currentUsage, wordCount);

  return new Response(JSON.stringify({ text: result.text, wordsUsedToday: currentUsage + wordCount, dailyLimit: DAILY_WORD_LIMIT }), {
    headers: { "Content-Type": "application/json" },
  });
}

async function handleCleanup(request, env, userId, usageKey, currentUsage) {
  const body = await request.json();
  const { text, mode = "clean" } = body; // mode: clean | bullets | email | hindi

  if (!text) {
    return jsonError("Missing text", 400);
  }

  const systemPrompts = {
    clean: "You clean up dictated speech into polished, well-punctuated text. Preserve meaning and tone. Return only the cleaned text.",
    bullets: "You convert dictated speech into a concise bulleted list. Return only the bullets.",
    email: "You convert dictated speech into a polished, professional email body. Return only the email text.",
    hindi: "You clean up dictated Hindi speech into polished, well-punctuated Hindi (Devanagari) text. Return only the cleaned text.",
  };

  const systemPrompt = systemPrompts[mode] || systemPrompts.clean;
  const wordCount = text.trim().split(/\s+/).filter(Boolean).length;

  const groqResp = await fetch(`${GROQ_API_URL}/chat/completions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.GROQ_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "llama-3.3-70b-versatile",
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: text },
      ],
      temperature: 0.3,
    }),
  });

  if (!groqResp.ok) {
    const errText = await groqResp.text();
    return jsonError(`Cleanup failed: ${errText}`, 502);
  }

  const result = await groqResp.json();
  const cleanedText = result.choices?.[0]?.message?.content || "";

  await incrementUsage(env, usageKey, currentUsage, wordCount);

  return new Response(
    JSON.stringify({ text: cleanedText, wordsUsedToday: currentUsage + wordCount, dailyLimit: DAILY_WORD_LIMIT }),
    { headers: { "Content-Type": "application/json" } }
  );
}

// ---- Helpers ----

async function incrementUsage(env, usageKey, currentUsage, addedWords) {
  const newUsage = currentUsage + addedWords;
  // Expire the key after 2 days so KV doesn't grow unbounded
  await env.USAGE_KV.put(usageKey, String(newUsage), { expirationTtl: 172800 });
}

function jsonError(message, status) {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function corsResponse(response) {
  const newHeaders = new Headers(response.headers);
  newHeaders.set("Access-Control-Allow-Origin", "*");
  newHeaders.set("Access-Control-Allow-Methods", "POST, OPTIONS");
  newHeaders.set("Access-Control-Allow-Headers", "Content-Type, Authorization");
  return new Response(response.body, { status: response.status, headers: newHeaders });
}

/**
 * Verifies a Firebase ID token against Google's JWKS endpoint and validates
 * standard claims (issuer, audience, expiry). Returns the Firebase user ID
 * (sub claim) if valid, otherwise null.
 */
async function verifyFirebaseToken(idToken, projectId) {
  try {
    const { payload } = await jwtVerify(idToken, jwks, {
      issuer: `https://securetoken.google.com/${projectId}`,
      audience: projectId,
    });

    if (!payload.sub || typeof payload.sub !== "string") return null;
    if (payload.auth_time && payload.auth_time > Math.floor(Date.now() / 1000)) return null;

    return payload.sub; // Firebase UID
  } catch (err) {
    console.error("Token verification failed:", err.message);
    return null;
  }
}
