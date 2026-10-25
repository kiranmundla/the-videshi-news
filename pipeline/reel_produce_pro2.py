#!/usr/bin/env python3
"""
reel_produce_pro2.py — SAMPLE driver for the multi-image "pro
techniques v2" reel (2026-10-24, for Kiran's judgment). Mirrors
reel_produce_pro.py's gate chain — fact-check -> render -> frame
QA — but renders with reel_renderer_pro2.py (per-scene verified
high-res images, per-crop upscale accounting).

LOCAL ONLY: never writes to prebuilt_reels, never uploads, never
publishes. There is deliberately NO publish path in this file.

Usage:
  set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; set +a
  python3 -u reel_produce_pro2.py --script script.json \
      --article-file article.json --images images.json \
      --music bed.mp3 --outdir <dir>

images.json: {beat_key: {"url" or "path", "source_url",
"page_url", "license", "artist"}} — scenes missing from the file
fall back to the article hero inside the renderer.

Exit codes: 0 ready · 1 held · 4 input/config error.
"""
import argparse, json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_factcheck
import reel_frame_qa
import reel_renderer
import reel_renderer_pro2

DEFAULT_MUSIC = (Path(__file__).resolve().parent / "music"
                 / "breaking-news-background.mp3")


def download(url, dest):
    r = subprocess.run(["curl", "-sSL", "-A", "TheVideshi/1.0",
                        "-o", str(dest), url],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not Path(dest).exists() \
            or Path(dest).stat().st_size < 10000:
        raise RuntimeError(f"download failed: {url} "
                           f"({r.stderr[:200]})")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--script", required=True)
    ap.add_argument("--slug", default=None)
    ap.add_argument("--article-file", default=None)
    ap.add_argument("--hero-file", default=None)
    ap.add_argument("--images", default=None,
                    help="JSON map of beat -> image spec")
    ap.add_argument("--music", default=str(DEFAULT_MUSIC))
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--name", default=None)
    ap.add_argument("--no-llm", action="store_true")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    verdict = {"driver": "reel_produce_pro2.py (SAMPLE v2)",
               "status": "held", "stage": None}

    def finish(code):
        (outdir / "verdict.json").write_text(json.dumps(verdict,
                                                        indent=2))
        print(json.dumps(verdict, indent=2))
        return code

    if not Path(args.script).exists():
        print(f"🚫 script not found: {args.script}", file=sys.stderr)
        verdict["stage"] = "input"
        return finish(4)
    script = json.loads(Path(args.script).read_text())
    try:
        if args.article_file:
            article = json.loads(Path(args.article_file).read_text())
            if isinstance(article, list):
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
    print(f"🎬 {slug} — PRO SAMPLE v2 (multi-image) gate chain")

    # ── Gate 1: fact-check (production gate, unchanged) ─────────────
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

    # ── Hero photo (fallback for scenes without their own) ─────────
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
            download(photo_url, hero)
        except Exception as e:
            print(f"🚫 {e}", file=sys.stderr)
            verdict["stage"] = "photo"
            return finish(1)

    # ── Scene images (originals; renderer falls back per scene) ────
    scene_images = {}
    if args.images:
        specs = json.loads(Path(args.images).read_text())
        imgdir = outdir / "scene-images"
        imgdir.mkdir(exist_ok=True)
        for key, spec in specs.items():
            spec = dict(spec)
            if spec.get("url") and not spec.get("path"):
                ext = Path(spec["url"].split("?")[0]).suffix or ".jpg"
                dest = imgdir / f"{key}{ext}"
                try:
                    download(spec["url"], dest)
                    spec["path"] = str(dest)
                except Exception as e:
                    print(f"⚠ scene {key} image download failed "
                          f"({e}); renderer will use hero fallback")
                    continue
            scene_images[key] = spec
        verdict["scene_images"] = {
            k: {"license": v.get("license"),
                "source_url": v.get("source_url")}
            for k, v in scene_images.items()}

    # ── Gate 2: pro v2 render ────────────────────────────────────────
    print("── gate 2/3: render (v6 recipe + pro upgrades v2)")
    try:
        manifest = reel_renderer_pro2.render_reel_pro2(
            script, hero, scene_images, args.music, outdir, name,
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
    verdict["pro_upgrades"] = manifest.get("pro_upgrades")

    # ── Gate 3: frame QA (production gate, unchanged) ───────────────
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
