# OpenFlow Frontend Integration

## 1. Add Firebase Auth (Google sign-in)

```bash
npm install firebase
```

```js
// firebase.js
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged } from "firebase/auth";

const firebaseConfig = {
  apiKey: "YOUR_FIREBASE_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
const provider = new GoogleAuthProvider();

export async function signIn() {
  const result = await signInWithPopup(auth, provider);
  return result.user;
}

export function watchAuthState(callback) {
  return onAuthStateChanged(auth, callback);
}
```

## 2. Get a fresh ID token before each request

```js
async function getAuthToken() {
  const user = auth.currentUser;
  if (!user) throw new Error("Not signed in");
  return await user.getIdToken(); // auto-refreshes if expired
}
```

## 3. Call the Worker instead of Groq directly

```js
const WORKER_URL = "https://openflow-worker.YOUR_SUBDOMAIN.workers.dev";

async function transcribeAudio(audioBlob, language = "en") {
  const token = await getAuthToken();
  const form = new FormData();
  form.append("audio", audioBlob, "recording.webm");
  form.append("language", language);

  const resp = await fetch(`${WORKER_URL}/transcribe`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });

  if (resp.status === 429) {
    const { error } = await resp.json();
    // Show "daily limit reached" UI here
    throw new Error(error);
  }
  if (!resp.ok) throw new Error("Transcription failed");

  return resp.json(); // { text, wordsUsedToday, dailyLimit }
}

async function cleanupText(text, mode = "clean") {
  const token = await getAuthToken();
  const resp = await fetch(`${WORKER_URL}/cleanup`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text, mode }),
  });

  if (resp.status === 429) {
    const { error } = await resp.json();
    throw new Error(error);
  }
  if (!resp.ok) throw new Error("Cleanup failed");

  return resp.json(); // { text, wordsUsedToday, dailyLimit }
}
```

## 4. Show usage in the UI

Every successful response includes `wordsUsedToday` and `dailyLimit` —
use these to show a small "1,240 / 2,000 words today" indicator, similar
to how Wispr Flow surfaces free-tier usage. This also nudges users toward
a paid tier later without you having to build that yet.

## Deployment checklist

1. `cd openflow-worker && npm install`
2. `wrangler kv:namespace create USAGE_KV` → paste the id into `wrangler.toml`
3. `wrangler secret put GROQ_API_KEY` → paste your Groq key when prompted
4. Set `FIREBASE_PROJECT_ID` in `wrangler.toml` vars
5. `wrangler deploy`
6. Update `WORKER_URL` in the PWA to your deployed Worker URL
7. Remove the "paste your API key" flow from the PWA entirely — auth replaces it
