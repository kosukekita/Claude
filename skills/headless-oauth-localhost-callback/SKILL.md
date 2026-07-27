---
name: headless-oauth-localhost-callback
description: Use when completing a browser OAuth 2.0 / device-consent flow whose redirect_uri is localhost or 127.0.0.1, but the machine running the callback listener is headless or accessed remotely (no usable GUI browser there) — so the browser's redirect cannot reach the listener and the token never returns. Symptoms: callback times out, ERR_EMPTY_RESPONSE or "connection refused" on localhost after authorizing, token file never written on a remote/headless server.
---

# Completing localhost-callback OAuth on a headless / remote server

## Overview
A browser OAuth flow redirects to `http://localhost:PORT/callback?code=...&state=...`. The
callback listener runs on your headless/remote server, but the human's browser is on a
DIFFERENT machine, so its `localhost` is the human's PC, not your server → the redirect
never reaches your listener.

**Core principle: YOU run the listener and deliver the callback yourself. The human's only
irreducible steps are (1) authorize in their own logged-in browser and (2) hand you the
redirect URL.** Do NOT make the human set up SSH tunnels, launch/verify servers, or run
diagnostics — you can do all of that. (See CLAUDE.md "解けることを人間に投げない".)

## Method (curl-delivery — default, no SSH, no code change)
1. **You**: start the OAuth flow's callback command on the server in the background (it prints
   the auth URL and blocks on `127.0.0.1:PORT` waiting for the redirect).
2. **You**: read the printed authorization URL and give it to the human.
3. **Human (irreducible)**: open that URL in their own browser (already logged into the
   service) and click Authorize. It's their account/consent — only they can.
4. **Human (irreducible)**: after authorizing, the browser navigates to
   `http://localhost:PORT/callback?code=...&state=...` and shows an error page
   (ERR_EMPTY_RESPONSE / can't connect) — **that is expected and fine**. They copy the
   **address-bar URL** (it contains `code` and `state`) and paste it to you.
5. **You**: deliver that callback to your waiting listener, on the server, with the loopback
   IP **explicit**:
   ```bash
   curl 'http://127.0.0.1:PORT/callback?code=<code>&state=<state>'
   ```
   The listener receives the exact request a browser redirect would → validates `state` →
   exchanges `code` → saves the token. (Quote the URL so `&` isn't treated as a shell job.)
6. **You**: verify — the auth process exited 0 and the token file now exists (never print the
   token). Do a lightweight authed call if the tool has one.

SSH local port-forward (`ssh -L PORT:localhost:PORT user@server`) is a valid alternative but
makes the human set up plumbing — prefer curl-delivery. Only fall back to SSH if the flow
can't accept an out-of-band callback delivery.

## Traps (all hit in real runs)
- **IPv6 `localhost` trap**: `localhost` often resolves to `::1` first. If a leftover
  `ssh -L` (or anything) holds `[::1]:PORT` with a broken forward, the browser/curl hits it →
  ERR_EMPTY_RESPONSE / timeout, even though your IPv4 listener is fine. **Always curl
  `127.0.0.1` explicitly, never `localhost`.** Diagnose owners with
  `lsof -iTCP:PORT -sTCP:LISTEN -Pn` (shows which PID owns IPv4 `127.0.0.1` vs IPv6 `[::1]`).
- **Probe with real HTTP, not a raw socket**: to check the listener is alive without
  consuming the one-shot callback, `curl` a NON-callback path (`curl http://127.0.0.1:PORT/`
  → expect 404). A bare `socket.connect()` leaves a half-open connection in a single-threaded
  server's accept queue and can wedge it so real requests hang.
- **Never GET `/callback` just to "test"** — it consumes the single callback and kills the
  waiting flow. Test with `/` or any non-callback path.
- **The `code` is single-use and short-lived**: deliver it promptly. If it expired (exchange
  returns `invalid_grant` / already-used), just re-run the auth command to mint a fresh
  URL+state and repeat.
- **Client auth method mismatch**: if the token exchange returns HTTP 401 `invalid_client`
  ("supports client_secret_basic but client_secret_post was requested"), the token request
  must send credentials via HTTP Basic (`Authorization: Basic base64(id:secret)`), not in the
  POST body. Fix the client, not the provider.

## When NOT to use
The machine running the listener has a usable browser (localhost callback resolves to the
same host) — just run the normal flow. Also not for pure device-code flows that already poll
(no localhost callback).
