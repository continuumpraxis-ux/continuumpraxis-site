#!/usr/bin/env python3
"""Build reels.built.json from the media present in reels/media.

Combines caption/url/show from reels.json with dimensions from reels.meta.json
(when available) and the actual downloaded media files. A reel is treated as a
video when its .mp4 exists, otherwise as an image when its .jpg exists.

Run:  python3 reel-desk/build_manifest.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESK = os.path.join(ROOT, "reel-desk")
MEDIA = os.path.join(ROOT, "reels", "media")

src = json.load(open(os.path.join(DESK, "reels.json")))
meta_path = os.path.join(DESK, "reels.meta.json")
meta = {}
if os.path.exists(meta_path):
    for r in json.load(open(meta_path)):
        meta[r["shortcode"]] = r

out = []
n_vid = n_img = n_none = 0
for r in src["reels"]:
    sc = r["shortcode"]
    m = meta.get(sc, {})
    rec = {
        "shortcode": sc,
        "url": r.get("url", f"https://www.instagram.com/reel/{sc}/"),
        "caption": r.get("caption", ""),
        "show": r.get("show", True),
        "w": m.get("w"),
        "h": m.get("h"),
    }
    mp4 = os.path.join(MEDIA, sc + ".mp4")
    jpg = os.path.join(MEDIA, sc + ".jpg")
    if os.path.exists(mp4) and os.path.getsize(mp4) > 1000:
        rec["video"] = f"/reels/media/{sc}.mp4"
        if os.path.exists(jpg):
            rec["poster"] = f"/reels/media/{sc}.jpg"
        n_vid += 1
    elif os.path.exists(jpg) and os.path.getsize(jpg) > 1000:
        rec["image"] = f"/reels/media/{sc}.jpg"
        n_img += 1
    else:
        n_none += 1
    out.append(rec)

json.dump(
    {"updated": src.get("updated"), "count": len(out), "reels": out},
    open(os.path.join(DESK, "reels.built.json"), "w"),
    indent=1,
)
print(f"manifest: videos={n_vid} images={n_img} none={n_none} total={len(out)}")
