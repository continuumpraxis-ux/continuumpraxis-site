# Continuum Praxis — Cloud Agent notes

## Standing rule: no revert loops on /reels

If a website update would put play behavior back to a previously failed pattern
(Option 1 outbound-only, Instagram embed click-to-load that CSP blocks, or
tile-click → Instagram), **do not ship that revert**.

Instead:

1. Name why the environment/OS/deploy path is pushing toward the old pattern
   (e.g. empty `dist/`, CSP blocking inline scripts, Workers Build failing).
2. Invent a **new** implementation that solves in-page play without circling.
3. Prefer self-hosted `/reels/media/*.mp4` + `js/reels.js` play/pause.
4. Instagram may only be an optional link under each card.

## Grok usage-gap handoff (John Amber / Jeremy Fields offline)

When Grok bots cannot run (usage exhausted until reset):

1. Read Drive folder `06_Website_System` (`parentId` `1emh1FD5HRyQxU1R5kycKhOoIpvpTFcxV`).
2. Prefer newest `*_Site_State_LIVE_*` and `*_SHIP_*` docs + skill docs
   (`John_Amber_Site_Desk_Reels_Skill`, `Jeremy_Fields_Reel_Desk_Skill`).
3. Continue unfinished SHIP items in Cursor; file a new LIVE/SHIP receipt in Drive
   after deploy.
4. Do not wait for Grok — Cursor owns continuity until usage resets.

Canonical continuity playbook: Drive doc titled
`Cursor_Grok_Usage_Gap_Continuity_Playbook` in `06_Website_System`.

## Deploy

- `wrangler.toml` assets `directory = "."` with root `.assetsignore` (excludes `.git`).
- Do not point assets at empty `dist/` — that leaves live on a stale Worker.
- Regenerate reels page: `python3 reel-desk/build_page.py`
