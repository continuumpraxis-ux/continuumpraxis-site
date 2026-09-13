#!/usr/bin/env python3
"""Generate reels/index.html from reels.built.json.

Each reel is rendered as a self-hosted <video> (or <img> for photo posts) so
playback works in-page for every visitor, independent of Instagram's embed.
Clicking a tile opens the original post on Instagram.

Run:  python3 reel-desk/build_page.py
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "reel-desk", "reels.built.json")
OUT = os.path.join(ROOT, "reels", "index.html")

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Reels — Continuum Praxis</title>
  <meta name="description" content="Studio reels from Continuum Praxis. Videos play right on the page; tap any clip to open it on Instagram." />
  <link rel="canonical" href="https://continuumpraxisapp.com/reels" />
  <link rel="icon" href="/icons/favicon.jpg" type="image/jpeg" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Outfit:wght@400;500;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/css/styles.css" />
  <link rel="stylesheet" href="/css/reels.css" />
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="site">
    <div class="wrap nav">
      <a class="brand" href="/"><img src="/img/logo-cp-nav.png" alt="Continuum Praxis" /> Continuum Praxis</a>
      <button class="menu-btn" id="menu" aria-label="Menu" aria-expanded="false">\u2630</button>
      <nav class="nav-links" id="nav-links">
        <a href="/">Home</a>
        <a href="/method">Method</a>
        <a href="/services">Services</a>
        <a href="/work">Work</a>
        <a class="active" href="/reels">Reels</a>
        <a href="/about">About</a>
        <a class="btn btn-primary" href="/contact">Start a conversation</a>
      </nav>
    </div>
  </header>

  <main id="main">
    <section class="hero">
      <div class="wrap">
        <p class="eyebrow">Reels</p>
        <h1>Reels from the studio.</h1>
      </div>
    </section>

    <section>
      <div class="wrap">
        <div class="reel-grid" id="reel-grid">
"""

FOOT = """        </div>
      </div>
    </section>
  </main>

  <footer class="site">
    <div class="wrap foot">
      <div>
        <a class="brand" href="/"><img src="/img/logo-cp-nav.png" alt="Continuum Praxis" /> Continuum Praxis</a>
        <p>Alex Koenig \u00b7 Marketing studio</p>
        <p style="margin-top:8px">continuumpraxisapp.com</p>
      </div>
      <div>
        <strong style="color:var(--ink)">Pages</strong>
        <ul>
          <li><a href="/method">Method</a></li>
          <li><a href="/services">Services</a></li>
          <li><a href="/work">Work</a></li>
          <li><a href="/reels">Reels</a></li>
          <li><a href="/about">About</a></li>
        </ul>
      </div>
      <div>
        <strong style="color:var(--ink)">Contact</strong>
        <ul>
          <li><a href="mailto:continuumpraxismarketing@outlook.com">continuumpraxismarketing@outlook.com</a></li>
          <li><a href="mailto:continuumpraxis@gmail.com">continuumpraxis@gmail.com</a></li>
          <li><a href="/contact">Working session</a></li>
        </ul>
      </div>
    </div>
  </footer>
  <script src="/js/main.js"></script>
  <script src="/js/reels.js"></script>
</body>
</html>
"""

IG_SVG = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.2c3.2 0 3.6 0 4.9.1 '
    "1.2.1 1.8.3 2.2.4.6.2 1 .4 1.4.9.5.4.7.8.9 1.4.1.4.3 1 .4 2.2.1 1.3.1 1.7.1 "
    "4.9s0 3.6-.1 4.9c-.1 1.2-.3 1.8-.4 2.2-.2.6-.4 1-.9 1.4-.4.5-.8.7-1.4.9-.4.1-1 "
    ".3-2.2.4-1.3.1-1.7.1-4.9.1s-3.6 0-4.9-.1c-1.2-.1-1.8-.3-2.2-.4-.6-.2-1-.4-1.4-.9-.5-.4-.7-.8-.9-1.4-.1-.4-.3-1-.4-2.2C2.2 "
    "15.6 2.2 15.2 2.2 12s0-3.6.1-4.9c.1-1.2.3-1.8.4-2.2.2-.6.4-1 .9-1.4.4-.5.8-.7 "
    "1.4-.9.4-.1 1-.3 2.2-.4C8.4 2.2 8.8 2.2 12 2.2m0 3.5A6.3 6.3 0 1 0 18.3 12 "
    "6.3 6.3 0 0 0 12 5.7m0 10.4A4.1 4.1 0 1 1 16.1 12 4.1 4.1 0 0 1 12 16.1m6.5-10.7a1.5 "
    '1.5 0 1 0 1.5 1.5 1.5 1.5 0 0 0-1.5-1.5"/></svg>'
)


def esc(s):
    return html.escape(s or "", quote=True)


def card(i, r):
    sc = r["shortcode"]
    url = r.get("url") or f"https://www.instagram.com/reel/{sc}/"
    cap = r.get("caption") or ""
    w = r.get("w") or 9
    h = r.get("h") or 16
    aspect = f"{w} / {h}"
    label = f"Open on Instagram: {cap[:80]}".strip()
    badge = f'<span class="reel-badge">{IG_SVG}Open on Instagram</span>'
    # A horizontal (landscape) reel would look wrong autoplaying in the tall
    # grid, so show a portrait cover thumbnail instead; clicking opens the reel
    # on Instagram, where it plays in its native horizontal orientation.
    portrait_rel = f"/reels/media/{sc}.portrait.jpg"
    is_horizontal = (
        r.get("video")
        and r.get("w")
        and r.get("h")
        and r["w"] > r["h"]
        and os.path.exists(os.path.join(ROOT, portrait_rel.lstrip("/")))
    )
    if is_horizontal:
        aspect = "9 / 16"
        media_inner = (
            f'<img class="reel-fill" src="{esc(portrait_rel)}" alt="" '
            f'loading="lazy" decoding="async" />'
            f'<span class="reel-play" aria-hidden="true">\u25b6</span>{badge}'
        )
    elif r.get("video"):
        poster = f' poster="{esc(r["poster"])}"' if r.get("poster") else ""
        media_inner = (
            f'<video src="{esc(r["video"])}"{poster} muted loop playsinline '
            f'preload="metadata" disablepictureinpicture></video>'
            f'<span class="reel-play" aria-hidden="true">\u25b6</span>{badge}'
        )
    elif r.get("image"):
        media_inner = (
            f'<img class="reel-fill" src="{esc(r["image"])}" alt="" '
            f'loading="lazy" decoding="async" />{badge}'
        )
    else:
        return ""  # no media available; skip
    return (
        f'      <article class="reel-card" data-reel="{i}" data-shortcode="{esc(sc)}">\n'
        f'        <div class="reel-media" data-href="{esc(url)}" role="link" '
        f'tabindex="0" aria-label="{esc(label)}" style="aspect-ratio: {aspect}">\n'
        f"          {media_inner}\n"
        f"        </div>\n"
        f'        <p class="reel-caption">{esc(cap)}</p>\n'
        f'        <p class="reel-link"><a href="{esc(url)}" target="_blank" '
        f'rel="noopener noreferrer">Open on Instagram</a></p>\n'
        f"      </article>\n"
    )


def main():
    data = json.load(open(MANIFEST))
    reels = data["reels"]
    cards = []
    n = 0
    skipped = []
    for r in reels:
        if r.get("show") is False:
            continue
        if not (r.get("video") or r.get("image")):
            skipped.append(r["shortcode"])
            continue
        n += 1
        cards.append(card(n, r))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(HEAD)
        f.write("".join(cards))
        f.write(FOOT)
    print(f"Wrote {OUT} with {n} cards.")
    if skipped:
        print(f"Skipped {len(skipped)} (no media): {skipped}")


if __name__ == "__main__":
    main()
