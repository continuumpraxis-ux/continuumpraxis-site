#!/usr/bin/env python3
"""One-command refresh for the /reels wall.

Reads reel-desk/reels.json, fetches + processes media for every reel that is
not hidden (show:false), then regenerates reels/index.html. Idempotent: it
skips reels whose video is already present unless you pass --force.

Pipeline per reel:
  1. Download the source video with yt-dlp (uses Instagram's web API, which is
     not rate-limited the way the embed endpoint is).
  2. Transcode to a small, web-optimized MP4 (H.264, longest side <=960px,
     faststart, audio stripped).
  3. Crop any baked-in black bars (ffmpeg cropdetect).
  4. Generate a poster JPEG from a frame (also used as the blurred fill).
  Reels with no video (photo/carousel posts) fall back to their thumbnail
  image. Reels Instagram marks "audience restricted" can't be fetched by
  anyone off-platform; they're reported and left out (make them public on
  Instagram to include them).

Usage:
  python3 reel-desk/refresh_reels.py                # fetch missing + rebuild
  python3 reel-desk/refresh_reels.py --force        # re-fetch every reel
  python3 reel-desk/refresh_reels.py --only SC1 SC2 # only these shortcodes
  python3 reel-desk/refresh_reels.py --build-only   # just rebuild the HTML

Requires: yt-dlp and ffmpeg on PATH.
"""
import argparse
import collections
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESK = os.path.join(ROOT, "reel-desk")
MEDIA = os.path.join(ROOT, "reels", "media")
CACHE = os.path.join(DESK, ".cache")  # gitignored source downloads
REELS_JSON = os.path.join(DESK, "reels.json")
MAX_LONG_EDGE = 960


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def ytdlp_cmd():
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    local = os.path.expanduser("~/.local/bin/yt-dlp")
    if os.path.exists(local):
        return [local]
    return [sys.executable, "-m", "yt_dlp"]


YTDLP = ytdlp_cmd()


def download_video(sc, tries=4):
    """Return path to a downloaded source video, or ('restricted'|None)."""
    dst = os.path.join(CACHE, f"{sc}.mp4")
    if os.path.exists(dst) and os.path.getsize(dst) > 1000:
        return dst
    last_err = ""
    for attempt in range(tries):
        r = sh(
            YTDLP
            + [
                "-f",
                "mp4/best",
                "--no-warnings",
                "-o",
                os.path.join(CACHE, f"{sc}.%(ext)s"),
                f"https://www.instagram.com/reel/{sc}/",
            ]
        )
        if os.path.exists(dst) and os.path.getsize(dst) > 1000:
            return dst
        last_err = (r.stderr or "") + (r.stdout or "")
        if "isn't available to everyone" in last_err or "Restricted" in last_err:
            return "restricted"
        import time

        time.sleep(4 + 4 * attempt)
    return None


def transcode(src, out):
    vf = (
        f"scale='if(gt(iw,ih),min({MAX_LONG_EDGE},iw),-2)':"
        f"'if(gt(iw,ih),-2,min({MAX_LONG_EDGE},ih))'"
    )
    return sh(
        [
            "ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", vf,
            "-c:v", "libx264", "-crf", "30", "-preset", "veryfast",
            "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", out,
        ]
    )


def autocrop(path):
    """Remove stable baked-in black borders, if any."""
    dims = sh(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", path]
    ).stdout.strip()
    if "," not in dims:
        return
    w, h = (int(x) for x in dims.split(","))
    det = sh(["ffmpeg", "-hide_banner", "-i", path, "-vf",
              "cropdetect=24:2:0", "-t", "6", "-f", "null", "-"])
    crops = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", det.stderr)
    if not crops:
        return
    cw, ch, cx, cy = (int(v) for v in collections.Counter(crops).most_common(1)[0][0])
    if (w - cw) <= 8 and (h - ch) <= 8:
        return  # no meaningful border
    tmp = path + ".crop.mp4"
    r = sh(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-vf",
            f"crop={cw}:{ch}:{cx}:{cy}", "-c:v", "libx264", "-crf", "30",
            "-preset", "veryfast", "-pix_fmt", "yuv420p", "-an",
            "-movflags", "+faststart", tmp])
    if os.path.exists(tmp) and os.path.getsize(tmp) > 1000:
        os.replace(tmp, path)


def poster_from_video(path, out):
    sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1", "-i", path,
        "-frames:v", "1", "-vf", "scale='min(640,iw)':-2", "-q:v", "5", out])
    if not os.path.exists(out):  # very short clip; grab first frame
        sh(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-frames:v", "1",
            "-vf", "scale='min(640,iw)':-2", "-q:v", "5", out])


def download_thumbnail(thumb_url, out):
    if not thumb_url:
        return False
    tmp = os.path.join(CACHE, "_thumb.jpg")
    sh(["curl", "-sL", "--max-time", "40", "-o", tmp, thumb_url])
    if os.path.exists(tmp) and os.path.getsize(tmp) > 2000:
        r = sh(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-vf",
                "scale='min(640,iw)':-2", "-q:v", "5", out])
        if not os.path.exists(out):
            shutil.copy(tmp, out)
        return True
    return False


def process_reel(r, force):
    sc = r["shortcode"]
    mp4 = os.path.join(MEDIA, f"{sc}.mp4")
    jpg = os.path.join(MEDIA, f"{sc}.jpg")
    if os.path.exists(mp4) and os.path.getsize(mp4) > 1000 and not force:
        return "video (cached)"
    src = download_video(sc)
    if src == "restricted":
        return "RESTRICTED (skipped — make public on Instagram to include)"
    if src:
        if transcode(src, mp4).returncode == 0 and os.path.exists(mp4):
            autocrop(mp4)
            poster_from_video(mp4, jpg)
            return f"video ({os.path.getsize(mp4)/1e6:.2f}MB)"
        return "TRANSCODE FAILED"
    # No video: treat as a photo/carousel post -> use its thumbnail image.
    if download_thumbnail(r.get("thumbnail"), jpg):
        return "image (photo post)"
    return "NO MEDIA (download failed)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="re-fetch every reel")
    ap.add_argument("--only", nargs="*", help="only these shortcodes")
    ap.add_argument("--build-only", action="store_true",
                    help="skip fetching; just rebuild the page")
    args = ap.parse_args()

    os.makedirs(MEDIA, exist_ok=True)
    os.makedirs(CACHE, exist_ok=True)
    data = json.load(open(REELS_JSON))

    if not args.build_only:
        for r in data["reels"]:
            if r.get("show") is False:
                continue
            if args.only and r["shortcode"] not in args.only:
                continue
            status = process_reel(r, args.force)
            print(f"  {r['shortcode']:14} {status}", flush=True)

    # Rebuild manifest + page using the sibling scripts.
    for script in ("build_manifest.py", "build_page.py"):
        r = sh([sys.executable, os.path.join(DESK, script)])
        sys.stdout.write(r.stdout)
        if r.returncode != 0:
            sys.stderr.write(r.stderr)
            sys.exit(r.returncode)


if __name__ == "__main__":
    main()
