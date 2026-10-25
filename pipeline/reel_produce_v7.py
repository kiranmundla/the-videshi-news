#!/usr/bin/env python3
"""
reel_produce_v7.py — SAMPLE driver for Reels v7 (2026-10-24).

Runs ONE story through the v7 sample renderer under the SAME
gates as production: reel_factcheck.py judges the script's claims
against the article, reel_frame_qa.py judges the rendered frames.
verdict.json lands in the outdir (status ready / held) with the
v7 driver named.

LOCAL ONLY — this driver has no publish path at all. The story it
is built for (tonight's Infosys/DOJ reel) already has a live
unlisted v6 upload; reel_publish.py correctly refuses duplicates.
If Kiran prefers v7, he deletes the v6 in Studio and the
supersede+redo path publishes v7.

Usage:
  python3 -u reel_produce_v7.py --script runs/<slug>/script.json \
      --article-file runs/<slug>/article.json \
      --music music/tech-corporate-technology.mp3 \
      --outdir runs/<slug>/output-v7 \
      [--stage navy|black] \
      [--extras runs/<slug>/supplementary/provenance.json]
"""
import argparse, json, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_factcheck
import reel_frame_qa
import reel_renderer as R
import reel_renderer_v7 as R7
import social_card as SC
from reel_produce import download_hero, original_url, download


def make_stills(outdir, manifest):
    """One frame per scene + a labelled contact sheet."""
    outdir = Path(outdir)
    stills = outdir / "stills"
    stills.mkdir(exist_ok=True)
    video = manifest["video"]
    frames = {}
    for key, sc in manifest["scenes"].items():
        t = sc["start"] + sc["duration"] / 2.0
        fp = stills / f"frame-{key}.png"
        r = subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}",
             "-i", str(video), "-frames:v", "1", str(fp)],
            capture_output=True, text=True)
        if r.returncode == 0:
            frames[key] = fp
    if not frames:
        return None
    # Contact sheet: 2 cols x 3 rows, each cell = frame at 540x960
    # + a 92px label bar (scene #, beat, image source, track,
    # render scale).
    keys = [k for k, _s, _d in R.BEATS if k in frames]
    cw, chh, lab = 540, 960, 92
    sheet = Image.new("RGB", (cw * 2, (chh + lab) * 3), (16, 16, 20))
    d = ImageDraw.Draw(sheet)
    f_lab = R.get_font(700, 30)
    f_sub = R.get_font(600, 26)
    for i, key in enumerate(keys):
        fr = Image.open(frames[key]).resize((cw, chh), Image.LANCZOS)
        x = (i % 2) * cw
        y = (i // 2) * (chh + lab)
        sheet.paste(fr, (x, y))
        v7 = manifest["scenes"][key]["v7"]
        pl = v7["placement"]
        disp = (f"{pl['w']}x{pl['h']}" if pl["w"] else "—")
        d.text((x + 18, y + chh + 10),
               f"{i + 1}. {key.upper()} — {v7['image_source']}",
               font=f_lab, fill=(255, 255, 255))
        d.text((x + 18, y + chh + 48),
               f"track: {v7['track']} · display {disp} · "
               f"scale {v7['render_scale']:.2f}x",
               font=f_sub, fill=(190, 198, 214))
    sheet_path = outdir / "contact-sheet.png"
    sheet.save(sheet_path, "PNG")
    return sheet_path


def load_extras(extras_path):
    """provenance.json -> the renderer's extras dict, with local
    paths resolved against the provenance file's directory. Only
    entries carrying a beat assignment are used."""
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


def produce(script_path, article, music_path, outdir, stage="navy",
            extras=None, log=print):
    """article: dict with the v6 produce fields. Returns the
    verdict dict."""
    extras = extras or {}
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    script = json.loads(Path(script_path).read_text())
    slug = article.get("slug")
    name = slug or "reel"

    verdict = {"driver": "reel_produce_v7.py (SAMPLE v7 rev.2 — "
                         "Cards v1 skin; NOT production)",
               "slug": slug, "article_id": article.get("id"),
               "script": str(script_path), "music": str(music_path),
               "outdir": str(outdir), "status": "held",
               "stage": stage,
               "extras": {b: e["label"] for b, e in extras.items()},
               "factcheck": None, "qa": None, "video": None,
               "problems": []}

    # ── Gate 1: independent fact-check (unchanged production gate)
    log("🔎 gate 1/2: independent fact-check (blind judge)…")
    fc = reel_factcheck.run_gate(script, article)
    (outdir / "factcheck-report.json").write_text(json.dumps(fc,
                                                             indent=1))
    verdict["factcheck"] = {"verdict": fc["verdict"],
                            "held_claims": fc["held_claims"],
                            "llm_cost_usd": fc["llm"]["cost_usd"],
                            "report": str(outdir
                                          / "factcheck-report.json")}
    if fc["verdict"] != "pass":
        verdict["stage"] = "factcheck"
        verdict["problems"].append(
            f"fact-check FAILED: {fc['held_claims']}")
        (outdir / "verdict.json").write_text(json.dumps(verdict,
                                                        indent=1))
        log(f"🚫 HELD at fact-check: {fc['held_claims']}")
        return verdict, 1
    log("   ✓ all claims grounded")

    # ── Images: hero + inline pool, originals at render time ────
    log("🖼  downloading hero (original resolution)…")
    ext = Path(article["image_url"].split("?")[0]).suffix or ".jpg"
    hero_path = outdir / f"hero{ext}"
    download_hero(article["image_url"], hero_path)
    verdict["photo_url_upgraded"] = original_url(article["image_url"])
    inline_paths = []
    inline_urls = [u for u in SC.extract_inline_images(
        article.get("body")) if not SC._same_image(
            u, article["image_url"])]
    for i, url in enumerate(inline_urls):
        try:
            p = download(original_url(url),
                         outdir / f"inline-{i + 1}.jpg")
            with Image.open(p) as im:
                inline_paths.append((p, im.size))
            log(f"   inline {i + 1}: {inline_paths[-1][1]}")
        except Exception as e:
            log(f"   inline {i + 1} skipped ({e})")
    log(f"   hero + {len(inline_paths)} inline image(s)")

    category = str(article.get("category") or "News") \
        .replace("-", " ").title()

    # ── Render (v7) ─────────────────────────────────────────────
    log(f"🎞  rendering Reels v7 rev.2 (stage={stage}, "
        f"{len(extras)} supplementary assignment(s))…")
    try:
        video, manifest = R7.render_reel_v7(
            script, hero_path, inline_paths, music_path, outdir,
            name=name, category=category,
            photo_url=article["image_url"], article_slug=slug,
            article_id=article.get("id"), stage=stage,
            extras=extras, log=log)
    except R.PhotoTooSmallError as e:
        verdict["problems"].append(str(e))
        (outdir / "verdict.json").write_text(json.dumps(verdict,
                                                        indent=1))
        log(f"🚫 HELD — {e}")
        return verdict, 1
    except R.TextFitError as e:
        verdict["problems"].append(f"text fit: {e}")
        (outdir / "verdict.json").write_text(json.dumps(verdict,
                                                        indent=1))
        log(f"🚫 HELD — text fit: {e}")
        return verdict, 1
    verdict["video"] = str(video)
    verdict["manifest"] = str(outdir / "render-manifest.json")

    # ── Gate 2: frame QA (unchanged production gate) ────────────
    log("🧪 gate 2/2: frame QA on the rendered MP4…")
    qa = reel_frame_qa.run_qa(video, outdir / "render-manifest.json",
                              outdir / "qa")
    (outdir / "qa" / "qa-report.json").write_text(json.dumps(qa,
                                                             indent=1))
    verdict["qa"] = {"passed": qa["qa_passed"],
                     "score": qa["qa_score"],
                     "failing_checks": qa["failing_checks"],
                     "report": str(outdir / "qa" / "qa-report.json")}
    if not qa["qa_passed"]:
        verdict["problems"].append(
            "frame QA FAILED: " + ", ".join(qa["failing_checks"]))
        (outdir / "verdict.json").write_text(json.dumps(verdict,
                                                        indent=1))
        log(f"🚫 HELD at frame QA ({qa['qa_score']}/10)")
        make_stills(outdir, manifest)
        return verdict, 1
    log(f"   ✓ QA score {qa['qa_score']}/10")

    sheet = make_stills(outdir, manifest)
    if sheet:
        verdict["contact_sheet"] = str(sheet)
    verdict["status"] = "ready"
    (outdir / "verdict.json").write_text(json.dumps(verdict,
                                                    indent=1))
    log(f"✅ v7 SAMPLE READY (local only — NOT uploaded): {video}")
    return verdict, 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--slug")
    src.add_argument("--article-file",
                     help="local article.json (offline; no Supabase)")
    ap.add_argument("--script", required=True)
    ap.add_argument("--music", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--stage", choices=("navy", "black"),
                    default="navy")
    ap.add_argument("--extras",
                    help="supplementary provenance.json (sourcing "
                         "ladder output; per-beat assignments)")
    args = ap.parse_args()

    if args.article_file:
        article = json.loads(Path(args.article_file).read_text())
    else:
        from reel_produce import fetch_article
        article = fetch_article(args.slug)
    extras = load_extras(args.extras) if args.extras else {}
    verdict, code = produce(args.script, article,
                            Path(args.music), Path(args.outdir),
                            stage=args.stage, extras=extras)
    return code


if __name__ == "__main__":
    sys.exit(main())
