#!/usr/bin/env python3
"""
reel_produce.py — production driver for The Videshi reels.

Runs the full gate chain for ONE article + reel script:

    fact-check gate  ->  render (Reels v7)  ->  frame QA

and writes a verdict.json whose status is "ready" only if every
gate passed on measured evidence:

  - reel_factcheck.py: every on-screen claim grounded in the
    article (deterministic numbers/names/eyebrow + GPT-4o-mini
    verification). UNCHANGED by the v7 adoption.
  - reel_renderer_v7.py: the Cards v1 design system ("Firstpost
    revised style") on the v6 pipeline — per-scene images (hero,
    article inlines, verified supplementary entity pictures),
    full-bleed only when the 9:16 cover-crop needs no upscale,
    otherwise the constant-size backdrop box on the BLACK stage
    (production default; navy remains a --stage parameter),
    0.4s crossfade scene joins, Playfair/Inter type. Adopted
    2026-10-24 on Kiran's approval of the rev.2 sample.
  - reel_entity_sourcing.py: when the article's own images
    (hero + inlines) total fewer than 5 usable scene images,
    supplementary entity pictures are sourced through the gated
    ladder (Commons originals -> official sources -> web search
    as discovery) with provenance recorded in the run's
    supplementary/provenance.json. Sourcing never blocks the
    reel: zero yield falls back to the hero chain.
  - reel_frame_qa.py: computed pixel QA on the rendered MP4
    (safe zones, face overlap, contrast, photo resolution,
    technicals). UNCHANGED.

ROLLBACK: production renders through render_reel_v7 by default.
Setting USE_V7_RENDERER = False below (one line) restores the
locked v6 renderer (reel_renderer.py, kept intact in the tree);
the verdict and gate flow are identical either way.

A failure at any stage = status "held", the stage and failing
checks named, and the chain stops. This driver never uploads and
never writes to prebuilt_reels — reel_publish.py is the single
publisher and consumes a "ready" verdict.

Usage:
  set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; set +a
  python3 -u reel_produce.py --slug <article-slug> --script script.json \
      --outdir <dir> [--music bed.mp3] [--stage black|navy] \
      [--no-sourcing] [--extras provenance.json] [--no-llm]

Exit codes: 0 ready · 1 held · 4 input/config error.
"""
import argparse, json, subprocess, sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_entity_sourcing
import reel_factcheck
import reel_frame_qa
import reel_publish
import reel_renderer

# NOTE: reel_renderer_v7 and social_card are imported LAZILY (in
# render() / fetch_inline_images). social_card imports
# original_url from THIS module at its top level, and
# reel_renderer_v7 imports social_card — a top-level import of
# either here would be circular and would silently leave
# social_card with its no-upgrade fallback binding.

# ── ROLLBACK SWITCH ─────────────────────────────────────────────
# True  = Reels v7 renderer (production, adopted 2026-10-24).
# False = the locked v6 renderer (reel_renderer.py) — one-line
# rollback; nothing else in this file changes.
USE_V7_RENDERER = True

# Fallback bed only — callers (the videshi-pulse-reels job) always
# pass --music with a rotated upbeat collection track. The previous
# default, anthemic-triumph-eternal-hope.mp3 (~66 BPM, sparse),
# was judged dull by Kiran on 2026-10-14 and is excluded from the
# rotation pool.
DEFAULT_MUSIC = (Path(__file__).resolve().parent / "music"
                 / "pixabay-breaking-full.mp3")

# Production stage variant (Kiran's pick on the rev.2 sample).
DEFAULT_STAGE = "black"


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
    """Best render-time upgrade of a stored hero URL to its
    original.

    Article heroes are stored at the article rung (Wikimedia
    thumbs at 1920 wide, NASA ~large) — right for readers, but a
    landscape hero's 9:16 reel crop is set by its HEIGHT (a
    1920-wide Capitol frame is only 963px tall), so reels
    layout-held on heroes that were fine for the article. Reel
    downloads are pipeline-side (readers pay no bytes), so fetch
    the original at render time (Kiran's pick, 2026-10-24):
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
        # (the Commons API serves thumbs from thumb.wikimedia.org
        # and appends utm query params; originals live on
        # upload.wikimedia.org)
        if len(parts) >= 8 and parts[3] == "thumb":
            original_path = "/".join(parts[:3] + parts[4:-1])
            if Path(original_path).suffix.lower() in _RASTER_SUFFIXES:
                return urllib.parse.urlunparse(p._replace(
                    netloc="upload.wikimedia.org",
                    path=original_path, query=""))
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
    original_url); falls back to the stored URL if the upgrade
    fails."""
    upgraded = original_url(url)
    if upgraded != url:
        try:
            download(upgraded, dest)
            print(f"   hero: original fetched for render "
                  f"({upgraded[:90]})")
            return
        except Exception:
            print("   hero: original fetch failed, using stored URL")
    download(url, dest)


def fetch_inline_images(article, outdir, log=print):
    """Download the article's inline body images (originals at
    render time, hero excluded) -> [(path, (w, h)), ...] in body
    order. Unusable downloads are skipped, never fatal: the v7
    planner falls back down its chain."""
    import social_card as SC    # lazy: see the import note above
    hero_url = article.get("image_url")
    urls = [u for u in SC.extract_inline_images(article.get("body"))
            if not SC._same_image(u, hero_url)]
    paths = []
    for i, url in enumerate(urls):
        dest = outdir / f"inline-{i + 1}.jpg"
        try:
            download(original_url(url), dest)
            with Image.open(dest) as im:
                paths.append((dest, im.size))
            log(f"   inline {i + 1}: {paths[-1][1]}")
        except Exception as e:
            log(f"   inline {i + 1} skipped ({e})")
    return paths


def load_extras(extras_path):
    """provenance.json -> the v7 renderer's extras dict, with
    local paths resolved against the provenance file's directory.
    Only entries carrying a beat assignment are used."""
    extras_path = Path(extras_path)
    data = json.loads(extras_path.read_text())
    out = {}
    for e in data.get("extras", []):
        if not e.get("beat"):
            continue
        out[e["beat"]] = {
            "label": e["label"],
            "path": str(extras_path.parent / e["path"]),
            "size": e["size"], "role": e.get("role"),
            "anchor": e.get("anchor"),
            "provenance": {k: e.get(k) for k in
                           ("subject", "route", "source_page",
                            "file_url", "license", "artist")}}
    return out


def render(script, article, hero, inline_paths, extras, music,
           outdir, name, stage, log=print):
    """The render dispatch — the ONLY place production chooses a
    renderer (see USE_V7_RENDERER). Returns the manifest dict
    (with a 'video' path) in both branches."""
    category = (article.get("category") or "News") \
        .replace("-", " ").title()
    if USE_V7_RENDERER:
        import reel_renderer_v7     # lazy: see the import note
        video, manifest = reel_renderer_v7.render_reel_v7(
            script, hero, inline_paths, music, outdir, name=name,
            category=category, photo_url=article.get("image_url"),
            article_slug=article.get("slug"),
            article_id=article.get("id"), stage=stage,
            extras=extras, log=log)
        manifest = dict(manifest)
        manifest["video"] = str(video)
        return manifest
    return reel_renderer.render_reel(
        script, hero, music, outdir, name, category=category,
        photo_url=article.get("image_url"),
        article_slug=article.get("slug"),
        article_id=article.get("id"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--script", required=True)
    ap.add_argument("--slug", default=None)
    ap.add_argument("--article-file", default=None)
    ap.add_argument("--hero-file", default=None,
                    help="use a local hero instead of the article "
                         "image")
    ap.add_argument("--music", default=str(DEFAULT_MUSIC))
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--name", default=None,
                    help="output stem (default: article slug)")
    ap.add_argument("--stage", choices=("navy", "black"),
                    default=DEFAULT_STAGE,
                    help="v7 stage variant (production default: "
                         "black)")
    ap.add_argument("--extras", default=None,
                    help="supplementary provenance.json to use "
                         "instead of running the sourcing ladder")
    ap.add_argument("--no-sourcing", action="store_true",
                    help="skip supplementary entity sourcing")
    ap.add_argument("--no-llm", action="store_true")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    renderer_name = ("reel_renderer_v7.py" if USE_V7_RENDERER
                     else "reel_renderer.py")
    verdict = {"driver": "reel_produce.py", "status": "held",
               "stage": None,
               "render": {"renderer": renderer_name,
                          "stage_color": args.stage
                          if USE_V7_RENDERER else None}}

    def finish(code):
        (outdir / "verdict.json").write_text(json.dumps(verdict,
                                                        indent=2))
        print(json.dumps(verdict, indent=2))
        return code

    # ── Load script + article ───────────────────────────────────
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
            print("🚫 need --slug or --article-file",
                  file=sys.stderr)
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
    print(f"🎬 {slug} — gate chain (renderer: {renderer_name})")

    # ── Gate 1: fact-check ──────────────────────────────────────
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

    # ── Images: hero + the article's own inlines ────────────────
    if args.hero_file:
        hero = Path(args.hero_file)
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
    inline_paths = fetch_inline_images(article, outdir)

    # ── Supplementary entity sourcing (v7 production step) ────
    extras = {}
    own_count = 1 + len(inline_paths)
    if args.extras:
        extras = load_extras(args.extras)
        verdict["sourcing"] = {
            "mode": "provided", "provenance": str(args.extras),
            "extras": {b: e["label"] for b, e in extras.items()}}
    elif args.no_sourcing or not USE_V7_RENDERER:
        verdict["sourcing"] = {"mode": "skipped", "extras": {}}
    elif own_count < reel_entity_sourcing.TARGET_DISTINCT:
        print("── supplementary entity sourcing")
        supp_dir = outdir / "supplementary"
        supp_dir.mkdir(parents=True, exist_ok=True)
        try:
            prov = reel_entity_sourcing.source_extras(
                article, script, supp_dir, own_count)
        except Exception as e:      # sourcing never blocks a reel
            print(f"   ⚠ sourcing failed ({e}) — hero chain only")
            prov = {"extras": []}
        (supp_dir / "provenance.json").write_text(
            json.dumps(prov, indent=2))
        extras = load_extras(supp_dir / "provenance.json")
        verdict["sourcing"] = {
            "mode": "ladder",
            "provenance": str(supp_dir / "provenance.json"),
            "own_images": own_count,
            "extras": {b: e["label"] for b, e in extras.items()}}
    else:
        verdict["sourcing"] = {
            "mode": "not-needed", "own_images": own_count,
            "extras": {}}

    # ── Gate 2: render ──────────────────────────────────────────
    print(f"── gate 2/3: render ({renderer_name}"
          + (f", stage={args.stage}" if USE_V7_RENDERER else "")
          + ")")
    try:
        manifest = render(script, article, hero, inline_paths,
                          extras, args.music, outdir, name,
                          args.stage)
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

    # ── Gate 3: frame QA ────────────────────────────────────────
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
    verdict["qa"] = {"score": qa["qa_score"],
                     "passed": qa["qa_passed"],
                     "failing_checks": qa["failing_checks"]}
    if not qa["qa_passed"]:
        verdict["stage"] = "frame_qa"
        print(f"🚫 HELD at frame QA (score {qa['qa_score']}): "
              f"{qa['failing_checks']}", file=sys.stderr)
        return finish(1)

    verdict["status"] = "ready"
    verdict["stage"] = "complete"
    # TikTok pack beside the verdict (file artifact only — the
    # caption + MP4 path Kiran gets at delivery; never fatal).
    try:
        pack = reel_publish.write_tiktok_pack(
            outdir, manifest["video"], article, script)
        verdict["tiktok_pack"] = str(pack)
    except Exception as e:
        print(f"   ⚠ TikTok pack not written ({e})")
    print(f"✅ READY — fact-check ✓ · render ✓ · frame QA "
          f"{qa['qa_score']}/10 · {manifest['video']}")
    return finish(0)


if __name__ == "__main__":
    sys.exit(main())
