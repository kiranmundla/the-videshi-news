#!/usr/bin/env python3
"""
reel_produce.py — Phase 1 local production driver for The Videshi reels.

Runs the full Phase 1 gate chain for ONE article + reel script:

    fact-check gate  ->  local render (v6 recipe)  ->  frame QA

and writes a verdict.json whose status is "ready" only if every gate
passed on measured evidence:

  - reel_factcheck.py: every on-screen claim grounded in the article
    (deterministic numbers/names/eyebrow + GPT-4o-mini verification).
  - reel_renderer.py: PIL+ffmpeg render on the locked v6 recipe; text
    measured with real font metrics; full-res photo floor enforced.
  - reel_frame_qa.py: computed pixel QA on the rendered MP4 (safe
    zones, face overlap, contrast, photo resolution, technicals).

A failure at any stage = status "held", the stage and failing checks
named, and the chain stops (no render credits/time wasted past a
failed gate). LOCAL ONLY: this driver never writes to prebuilt_reels,
never uploads, never publishes. "ready" is a local sample status —
Phase 2's single publisher is what will consume ready reels later.

Usage:
  set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; set +a
  python3 -u reel_produce.py --slug <article-slug> --script script.json \
      --outdir <dir> [--music bed.mp3] [--no-llm]

Exit codes: 0 ready · 1 held · 4 input/config error.
"""
import argparse, json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_factcheck
import reel_frame_qa
import reel_renderer

# Fallback bed only — callers (the videshi-pulse-reels job) always pass
# --music with a rotated upbeat collection track. The previous default,
# anthemic-triumph-eternal-hope.mp3 (~66 BPM, sparse), was judged dull
# by Kiran on 2026-10-14 and is excluded from the rotation pool.
DEFAULT_MUSIC = (Path(__file__).resolve().parent / "music"
                 / "pixabay-breaking-full.mp3")


def download(url, dest):
    r = subprocess.run(["curl", "-sSL", "-A", "TheVideshi/1.0",
                        "-o", str(dest), url],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0 or not Path(dest).exists() \
            or Path(dest).stat().st_size < 10000:
        raise RuntimeError(f"hero download failed: {url} "
                           f"({r.stderr[:200]}")


_RASTER_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def original_url(url):
    """Best render-time upgrade of a stored hero URL to its original.

    Article heroes are stored at the article rung (Wikimedia thumbs at
    1920 wide, NASA ~large) — right for readers, but a landscape hero's
    9:16 reel crop is set by its HEIGHT (a 1920-wide Capitol frame is
    only 963px tall), so reels layout-held on heroes that were fine for
    the article. Reel downloads are pipeline-side (readers pay no
    bytes), so fetch the original at render time (Kiran's pick,
    2026-10-24):
    - upload.wikimedia.org thumb URLs -> the original file URL
    - commons Special:FilePath?width=N -> width dropped (original)
    - NASA ~large.jpg -> ~orig.jpg
    - Pexels size params (w/h/dpr) -> dropped (original)
    Anything else is returned unchanged.
    """
    import urllib.parse
    try:
        p = urllib.parse.urlparse(url)
    except Exception:
        return url
    host = (p.netloc or "").lower()
    if host in ("upload.wikimedia.org", "thumb.wikimedia.org") \
            and "/thumb/" in p.path:
        parts = p.path.split("/")
        # /wikipedia/commons/thumb/<a>/<ab>/<file>/<rendition>
        # (the Commons API serves thumbs from thumb.wikimedia.org and
        # appends utm query params; originals live on upload.wikimedia.org)
        if len(parts) >= 8 and parts[3] == "thumb":
            original_path = "/".join(parts[:3] + parts[4:-1])
            if Path(original_path).suffix.lower() in _RASTER_SUFFIXES:
                return urllib.parse.urlunparse(p._replace(
                    netloc="upload.wikimedia.org", path=original_path,
                    query=""))
        return url
    if "Special:FilePath" in p.path and p.query:
        qs = urllib.parse.parse_qsl(p.query)
        if any(k == "width" for k, _v in qs):
            qs = [(k, v) for k, v in qs if k != "width"]
            return urllib.parse.urlunparse(
                p._replace(query=urllib.parse.urlencode(qs)))
        return url
    if "~large." in url and ("nasa.gov" in host or "nasa" in url):
        return url.replace("~large.", "~orig.")
    if host == "images.pexels.com" and p.query:
        qs = urllib.parse.parse_qsl(p.query)
        kept = [(k, v) for k, v in qs if k not in ("w", "h", "dpr")]
        if len(kept) != len(qs):
            return urllib.parse.urlunparse(
                p._replace(query=urllib.parse.urlencode(kept)))
    return url


def download_hero(url, dest):
    """Download the hero, preferring the render-time original (see
    original_url); falls back to the stored URL if the upgrade fails."""
    upgraded = original_url(url)
    if upgraded != url:
        try:
            download(upgraded, dest)
            print(f"   hero: original fetched for render ({upgraded[:90]})")
            return
        except Exception:
            print("   hero: original fetch failed, using stored URL")
    download(url, dest)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--script", required=True)
    ap.add_argument("--slug", default=None)
    ap.add_argument("--article-file", default=None)
    ap.add_argument("--hero-file", default=None,
                    help="use a local hero instead of the article image")
    ap.add_argument("--music", default=str(DEFAULT_MUSIC))
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--name", default=None,
                    help="output stem (default: article slug)")
    ap.add_argument("--no-llm", action="store_true")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    verdict = {"driver": "reel_produce.py", "status": "held",
               "stage": None}

    def finish(code):
        (outdir / "verdict.json").write_text(json.dumps(verdict,
                                                        indent=2))
        print(json.dumps(verdict, indent=2))
        return code

    # ── Load script + article ───────────────────────────────────────────
    if not Path(args.script).exists():
        print(f"🚫 script not found: {args.script}", file=sys.stderr)
        verdict["stage"] = "input"
        return finish(4)
    script = json.loads(Path(args.script).read_text())
    try:
        if args.article_file:
            article = json.loads(Path(args.article_file).read_text())
            if isinstance(article, list):   # raw Supabase REST dump
                article = article[0]
        elif args.slug:
            article = reel_factcheck.fetch_article_by_slug(args.slug)
        else:
            print("🚫 need --slug or --article-file", file=sys.stderr)
            verdict["stage"] = "input"
            return finish(4)
    except Exception as e:
        print(f"🚫 article load failed: {e}", file=sys.stderr)
        verdict["stage"] = "input"
        return finish(4)
    slug = article.get("slug") or args.slug or "reel"
    name = args.name or slug
    verdict.update({"article_slug": slug, "name": name,
                    "script": str(args.script)})
    print(f"🎬 {slug} — Phase 1 gate chain")

    # ── Gate 1: fact-check ──────────────────────────────────────────────
    print("── gate 1/3: fact-check")
    fc = reel_factcheck.run_gate(script, article,
                                 use_llm=not args.no_llm)
    (outdir / "factcheck-report.json").write_text(json.dumps(fc,
                                                            indent=2))
    verdict["factcheck"] = {
        "verdict": fc["verdict"], "held_claims": fc["held_claims"],
        "llm_cost_usd": fc["llm"]["cost_usd"]}
    if fc["verdict"] != "pass":
        verdict["stage"] = "factcheck"
        print(f"🚫 HELD at fact-check: {fc['held_claims']}",
              file=sys.stderr)
        return finish(1)
    print("   ✅ all claims grounded")

    # ── Hero photo (full-res, from the article) ─────────────────────────
    if args.hero_file:
        hero = Path(args.hero_file)
        photo_url = article.get("image_url")
    else:
        photo_url = article.get("image_url")
        if not photo_url:
            print("🚫 article has no image_url", file=sys.stderr)
            verdict["stage"] = "photo"
            return finish(1)
        ext = Path(photo_url.split("?")[0]).suffix or ".jpg"
        hero = outdir / f"hero{ext}"
        try:
            download_hero(photo_url, hero)
        except Exception as e:
            print(f"🚫 {e}", file=sys.stderr)
            verdict["stage"] = "photo"
            return finish(1)

    # ── Gate 2: render ──────────────────────────────────────────────────
    print("── gate 2/3: render (v6 recipe)")
    try:
        manifest = reel_renderer.render_reel(
            script, hero, args.music, outdir, name,
            category=(article.get("category") or "News").replace(
                "-", " ").title(),
            photo_url=photo_url, article_slug=slug,
            article_id=article.get("id"))
    except reel_renderer.PhotoTooSmallError as e:
        verdict["stage"] = "render_photo_floor"
        verdict["detail"] = str(e)
        print(f"🚫 HELD: {e}", file=sys.stderr)
        return finish(1)
    except (reel_renderer.TextFitError, RuntimeError,
            FileNotFoundError) as e:
        verdict["stage"] = "render"
        verdict["detail"] = str(e)[:500]
        print(f"🚫 HELD at render: {e}", file=sys.stderr)
        return finish(1)
    verdict["manifest"] = str(outdir / "render-manifest.json")
    verdict["video"] = manifest["video"]

    # ── Gate 3: frame QA ────────────────────────────────────────────────
    print("── gate 3/3: frame QA")
    try:
        qa = reel_frame_qa.run_qa(manifest["video"],
                                  outdir / "render-manifest.json",
                                  outdir / "qa")
    except Exception as e:
        verdict["stage"] = "frame_qa_error"
        verdict["detail"] = str(e)[:500]
        print(f"🚫 QA could not run: {e}", file=sys.stderr)
        return finish(1)
    (outdir / "qa-report.json").write_text(json.dumps(qa, indent=2))
    verdict["qa"] = {"score": qa["qa_score"], "passed": qa["qa_passed"],
                     "failing_checks": qa["failing_checks"]}
    if not qa["qa_passed"]:
        verdict["stage"] = "frame_qa"
        print(f"🚫 HELD at frame QA (score {qa['qa_score']}): "
              f"{qa['failing_checks']}", file=sys.stderr)
        return finish(1)

    verdict["status"] = "ready"
    verdict["stage"] = "complete"
    print(f"✅ READY — fact-check ✓ · render ✓ · frame QA "
          f"{qa['qa_score']}/10 · {manifest['video']}")
    return finish(0)


if __name__ == "__main__":
    sys.exit(main())
