---
name: sns-auto-posting
description: >
  Use when automating posting of generated videos/images to social platforms
  (Instagram Reels, TikTok, YouTube Shorts) from a headless server via their
  official APIs — especially when a container/upload is accepted but the post
  silently fails, when you must serve a video to a platform's server-side
  fetcher, when stripping AI-provenance/metadata before posting, or when
  diagnosing opaque platform errors. Keywords: Instagram Graph API,
  graph.instagram.com, Reels, media_publish, container ERROR, 2207076,
  "media download failed", video_url, cloudflared tunnel, named tunnel, C2PA,
  CBOR provenance, is_ai_generated, TikTok Content Posting API, video.publish,
  exiftool, content_publishing_limit. NOT for one-off manual uploads or for
  generating the media itself (use video-media-studio for that).
---

# sns-auto-posting

Automating posting of generated media to Instagram / TikTok / YouTube via their
official APIs. **Core insight: platforms fetch and transcode your media
server-side and report failures OPAQUELY.** The API calls are easy; the hard,
non-obvious parts are (1) making the media reachable to the platform's fetcher,
(2) diagnosing silent failures, (3) not leaking provenance/metadata. This skill
is the hard-won gotchas, not the happy-path docs.

## Instagram (graph.instagram.com — "Instagram API with Instagram Login")

Flow (async, 3 steps): **container** `POST /{ig_user_id}/media`
(`media_type=REELS`, `video_url=<public HTTPS>`, `caption`) → **poll**
`GET /{creation_id}?fields=status_code` until `FINISHED` → **publish**
`POST /{ig_user_id}/media_publish` (`creation_id`).

- **video_url ONLY.** Meta fetches the URL server-side. There is **no** local
  byte upload for Instagram Login. `rupload.facebook.com` / `upload_type=resumable`
  is **Facebook Login only** — a trap; don't reach for it here.
- **★ THE killer bug: the public URL you hand Meta MUST include the file path**
  (e.g. `https://media.example.com/clip.mp4`, not the bare host). A tunnel/proxy
  forwards the incoming request path to your origin as-is, so the bare host `/`
  hits your origin's `/` → 404 → Meta reports the OPAQUE
  `container status_code=ERROR`. Cost hours chasing DNS/tunnel red herrings.
- **Diagnose an ERROR container** by calling `media_publish` on it: Meta returns
  the real reason, e.g. `error_subcode 2207076 error_user_msg "メディアを
  ダウンロードできませんでした"` (media download failed) = the fetcher could not
  GET your URL. `status_code`/`status` alone only say `ERROR`.
- **Dev/unpublished app:** only accounts with an app role can post, and the IG
  account must **accept the Instagram tester invite** inside the app
  (Instagram → Settings → Apps and websites → Tester invites). "テスター 0 of 50"
  is the Facebook-login tester slot — irrelevant; use the **Instagram tester** tab.
- **AI disclosure** (`is_ai_generated`) is a request parameter, not in the file.
- `code 190`=token expired; `code 200 "API access blocked"`=permission/app state
  (often transient or dev-mode/role); `content_publishing_limit` = daily quota.

## Delivering the video to the platform's fetcher

**Never upload persona/private generated media to third-party storage**
(S3/imgur/catbox/etc.) — opsec leak. Serve it from your own box via a
**cloudflared tunnel**:

- **Named tunnel on your own domain (production).** Stable DNS record →
  resolves reliably for both the platform and locally. Quick tunnels
  (`*.trycloudflare.com`) use ephemeral random subdomains that fail DNS
  resolution (negative-cached by some resolvers) and hit rate limits → the
  platform's fetch fails → `media download failed`. Quick tunnel = test only.
- **Set up headlessly via the Cloudflare API** (no `cloudflared login`):
  `POST /accounts/{id}/cfd_tunnel` (send your own base64 `tunnel_secret`,
  `config_src:"local"`) → write credentials `{AccountTag,TunnelID,TunnelSecret}`
  → DNS `CNAME media.<domain> → <tunnel-id>.cfargotunnel.com` (proxied).
- **Run it (arg order matters):**
  `cloudflared tunnel --no-autoupdate run --credentials-file <f> --url http://127.0.0.1:PORT <UUID>`.
  `--no-autoupdate` goes **before** `run` (it's a tunnel-command option; after
  `run` → `flag provided but not defined` and cloudflared dies instantly).
  With `--credentials-file` + UUID you need **no cert.pem** (`login`).
- Serve the file with **HTTP Range support** (platforms do ranged fetches) and
  bind the origin to `127.0.0.1`; the public face is the tunnel only.
- After the tunnel registers, the edge route needs a few seconds to propagate.
  Confirm serving before handing off the URL:
  `curl --resolve host:443:<edgeIP> -r 0-1 <full-url-with-filename>` → expect 206.

## Metadata / provenance hygiene (before every post)

- **AI video models embed C2PA provenance that leaks the model name.** Seedance
  2.0 writes `CBOR:ActionsParametersModel_Name = dreamina-seedance-2-0`,
  `CBOR:ActionsSoftwareAgentName = BytePlus_ModelArk`, plus real timestamps.
- **`ffprobe` misses it** (it only sees container/stream tags, not EXIF/XMP/atom/
  C2PA-CBOR-JUMBF). Verify with **`exiftool -G1 -a -s`**.
- **`ffmpeg -map_metadata -1 -map_chapters -1 -c copy` remux drops C2PA + the
  SOURCE's Encoder LOSSLESSLY** (no re-encode; the C2PA manifest is a top-level
  box that remux discards). **BUT the remux itself writes a NEW `Encoder=Lavf...`
  tag — add `-fflags +bitexact -flags:v +bitexact -flags:a +bitexact` to suppress
  it** (verified 2026-07-22: a plain clean-remux failed the metadata checker on
  `Encoder = Lavf60.16.100`; the bitexact remux passed). If you must re-encode,
  libx264 single-pass leaves `CompressorName`/`Encoder` → do encode → bitexact
  `-c copy` remux (2 stages).
- A metadata **checker must treat `CBOR`/`C2PA`/`JUMBF` exiftool groups as leaks**,
  not just `XMP`/`IPTC`/`ICC`/EXIF — otherwise a video with an embedded model
  name passes when the `Encoder` tag happens to be absent.
- Aspect: assert `width*16 == height*9` via ffprobe (don't trust nominal res).

## Other platforms (brief)

- **TikTok** (Content Posting API): Direct Post via **FILE_UPLOAD pushes bytes**
  (`/v2/post/publish/video/init/` → PUT bytes → poll status) — **no public URL
  needed**, so no tunnel. Unaudited client → `privacy_level=SELF_ONLY` **and the
  account must be Private** (else init 403 `unaudited_client_can_only_post_to_private_accounts`).
  `is_aigc` = AI disclosure. Login Kit v2 OAuth for the token.
- **YouTube** (`videos.insert`): an **unaudited** API project gets its uploads
  **private-locked irrecoverably**. There is no API to query audit status — gate
  on a human-set `audited` flag; until then write to an outbox and upload by hand.

## Diagnosing opaque post failures — order matters

1. Container/upload accepted but post never lands → get the platform's **real**
   error (IG: `media_publish` on the errored container → `error_user_msg`/subcode).
2. IG `2207076 media download failed` → the fetcher can't GET your URL. `curl`
   the **exact URL you handed the platform** (with filename). 404 → URL missing
   the file path. 530 → tunnel origin down. DNS NXDOMAIN → quick-tunnel subdomain
   / broken resolver → switch to a named tunnel.
3. **Don't chase DNS/tunnel/codec before confirming the URL path is correct.**

## Common mistakes

| Mistake | Fix |
|---|---|
| Hand the platform the bare tunnel host (no filename) | Append `/{filename}`; bare host → 404 → opaque ERROR |
| Read only `status_code` on an ERROR container | `media_publish` on it to get `error_user_msg`/subcode |
| Host persona media on S3/imgur | Cloudflared named tunnel from your own box (opsec) |
| Quick tunnel in production | Named tunnel on your domain (stable DNS, no rate limit) |
| `--no-autoupdate` after `run` | It goes before `run`; else cloudflared dies |
| Trust `ffprobe` / `-map_metadata -1` alone for cleanliness | `exiftool -G1`; strip C2PA/CBOR via `-c copy` remux |
| Post immediately after tunnel "Registered" | Wait for edge route; verify serving with `curl` first |
