#!/usr/bin/env python3
"""
reel_renderer_pro2.py — SAMPLE-ONLY "pro techniques v2" renderer
(2026-10-24): the multi-image iteration of reel_renderer_pro.py.

Kiran's feedback on v1: "not just single image — more and relevant
and newsworthy images; images and their resolution may be the
issue." v1 choreographed crops of ONE 1200x901 hero; for a 9:16
cover that source forces >2x upscaling (wide window = 507 source
px stretched to 1080). v2 keeps v1's four upgrades (pattern-
interrupt crops, kinetic text, loudnorm mastering, SFX + licence
log) and changes the imagery model:

  * PER-SCENE PHOTOS — every scene can carry its OWN verified,
    rights-clean, high-resolution photo with its own 2x master,
    crop choreography and text plan. Scenes without a verified
    image of their own fall back to the article hero's crops
    (v1 behaviour), and the fallback is recorded per scene.

  * RESOLUTION ACCOUNTING — every crop window is mapped back to
    ORIGINAL source pixels. A crop whose effective upscale (window
    resized to the 1080-wide canvas, worst-case Ken Burns zoom
    included) would exceed MAX_UPSCALE is widened toward the full
    frame until it complies; if even the full frame cannot comply
    (small fallback hero), the violation is logged in the manifest
    instead of hidden. Per-image source URL, licence, artist and
    native resolution are recorded in the manifest.

Production reel_renderer.py is untouched; v1's pro module is
imported for its shared machinery (painters come from production
via reel_renderer_pro's imports). This module NEVER writes to
prebuilt_reels and NEVER uploads.
"""
import json, math, time
from pathlib import Path

from PIL import Image

import reel_renderer as R
import reel_renderer_pro as P

W, H, FPS, TOTAL = R.W, R.H, R.FPS, R.TOTAL
BEATS = R.BEATS
MAX_UPSCALE = 1.5                # render rule for this iteration
ZOOM_MAX = 1.0 + P.ZOOM_RANGE    # worst-case in-segment zoom (1.05)


def compose_master_mapped(enh, face_enh):
    """P.compose_master_2x geometry, plus the source mapping:
    returns (master, face_in_master, f, (x0, y0)) where a master
    point m maps to ORIGINAL source pixels as (m + (x0, y0)) / f
    (f folds in the grade's 2x supersample)."""
    W2, H2 = 2 * W, 2 * H
    scale = max(W2 / enh.width, H2 / enh.height)
    sw, sh = round(enh.width * scale), round(enh.height * scale)
    img = enh.resize((sw, sh), Image.LANCZOS)
    fx, fy, fw, fh = [v * scale for v in face_enh]
    x0 = int(min(max(fx + fw / 2 - W2 / 2, 0), max(sw - W2, 0)))
    y0 = int(min(max(fy - 300, 0), max(sh - H2, 0)))
    master = img.crop((x0, y0, x0 + W2, y0 + H2))
    return master, (fx - x0, fy - y0, fw, fh), R.ENH["upscale"] * scale, (x0, y0)


class SceneImage:
    """One scene's photo: source, grade, master, face, mapping."""

    def __init__(self, path, meta, log):
        self.path = Path(path)
        self.meta = meta or {}
        self.src = Image.open(self.path).convert("RGB")
        self.native = (self.src.width, self.src.height)
        face_src, method = R.detect_face_box(self.src)
        self.method = method
        self.has_face = method.startswith(("yunet", "haar"))
        self.face_src = face_src
        enh = R.enhance_raw(self.src)
        face_enh = tuple(v * R.ENH["upscale"] for v in face_src)
        self.master, self.face_master, self.f, self.offset = \
            compose_master_mapped(enh, face_enh)
        log(f"    image {self.path.name}: native "
            f"{self.native[0]}x{self.native[1]} face={method} "
            f"master_scale f={self.f:.3f}")

    def upscale_for(self, window):
        """(base, worst) upscale factors for a master window:
        base = canvas width / source-region width; worst folds in
        the in-segment Ken Burns zoom (<=1.05)."""
        src_w = window[2] / self.f
        base = W / src_w
        return base, base * ZOOM_MAX

    def compliant_window(self, name):
        """The requested crop, widened toward full frame until its
        worst-case upscale <= MAX_UPSCALE (or the widest crop).
        Returns (applied_name, window, base, worst, widened?)."""
        order = sorted(P.CROPS, key=lambda c: P.CROPS[c][2])
        start = order.index(name)
        for cand in order[start:]:
            window = P.crop_window(self.master, cand)
            base, worst = self.upscale_for(window)
            if worst <= MAX_UPSCALE or cand == order[-1]:
                return cand, window, base, worst, cand != name
        raise AssertionError("unreachable")


def render_reel_pro2(script, hero_path, scene_images, music_path,
                     outdir, name, category="Technology",
                     photo_url=None, article_slug=None,
                     article_id=None, log=print):
    """Render one PRO v2 sample reel.

    scene_images: {beat_key: {"path":..., "source_url":...,
    "page_url":..., "license":..., "artist":...}} — scenes absent
    from the dict (or whose image fails to load) use the hero.
    Returns the manifest dict. Raises like v1."""
    t0 = time.time()
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    hero_path = Path(hero_path)

    # 0. Hero (fallback for every scene) — production floor rule.
    hero_src = Image.open(hero_path).convert("RGB")
    if hero_src.width < R.MIN_PHOTO_W or hero_src.height < R.MIN_PHOTO_H:
        raise R.PhotoTooSmallError(
            f"hero {hero_src.width}x{hero_src.height} below full-res "
            f"floor {R.MIN_PHOTO_W}x{R.MIN_PHOTO_H}")
    log(f"  🖼  hero (fallback): {hero_src.width}x{hero_src.height}")

    # 1. Build per-scene images (own photo or hero fallback).
    hero_img = SceneImage(hero_path, {"role": "article hero"}, log)
    images = {}
    for key, _, _ in BEATS:
        spec = (scene_images or {}).get(key)
        if spec and Path(spec["path"]).exists():
            try:
                images[key] = (SceneImage(spec["path"], spec, log),
                               "own")
                continue
            except Exception as e:
                log(f"  ⚠ scene {key}: own image failed ({e}); "
                    f"falling back to hero")
        images[key] = (hero_img, "hero-fallback")
    hero_img.master.save(outdir / "master-hero-2x.jpg", quality=92)

    # 2. Per-scene planning against the scene's OWN master.
    scene_plan, scene_bgs = {}, {}
    for key, start, dur in BEATS:
        img, role = images[key]
        primary = P.SCENE_CROPS[key][0][0]
        order = [primary] + [c for c in P.LADDER if c != primary]
        chosen = None
        for cand in order:
            window = P.crop_window(img.master, cand)
            plan = P.plan_scene_pro(key, script, category, window,
                                    img.face_master, img.has_face)
            if plan is not None:
                chosen = (cand, window, plan)
                break
        if chosen is None:
            raise R.TextFitError(
                f"scene '{key}' cannot fit under any crop")
        cand, window, (s, painter, block_top, zone_top, content_h) = \
            chosen
        scene_plan[key] = {
            "start": start, "duration": dur, "crop": cand,
            "window": window, "scale": s, "painter": painter,
            "block_top": block_top, "zone_top": zone_top,
            "content_h": content_h, "image_role": role,
        }
        log(f"  ✓ scene {key} [{role}]: primary crop {cand} "
            f"scale={s} block_top={block_top}")

        # Backgrounds: choreographed sub-crops of the scene's own
        # master, each widened until the upscale rule complies.
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        painter(ov, block_top)
        ov.save(outdir / f"overlay-{key}.png")
        scene_plan[key]["text_bbox"] = R._overlay_text_bbox(ov)
        scene_plan[key]["texts"] = R.SCENE_TEXTS[key](script, category)
        scene_plan[key]["strips"] = P.split_strips(ov, key, outdir)

        subs, frames_left = [], int(round(dur * FPS))
        for j, (cname, share, zdir) in enumerate(P.SCENE_CROPS[key]):
            frames = frames_left if j == len(P.SCENE_CROPS[key]) - 1 \
                else int(round(dur * FPS * share))
            frames_left -= frames
            applied, win, base, worst, widened = \
                img.compliant_window(cname)
            bg = img.master.crop(win).resize((W, H), Image.LANCZOS)
            bg = R.apply_gradient(bg)
            bp = outdir / f"bg-{key}-{j}.jpg"
            bg.save(bp, quality=92)
            if key == "hook" and j == 0:
                bg.save(outdir / "background.jpg", quality=92)
            subs.append({
                "file": bp, "secs": frames / FPS, "zoom": zdir,
                "crop_requested": cname, "crop_applied": applied,
                "widened": widened, "window_master": list(win),
                "src_region_px": [round(win[2] / img.f),
                                  round(win[3] / img.f)],
                "upscale_base": round(base, 3),
                "upscale_max": round(worst, 3),
                "upscale_ok": worst <= MAX_UPSCALE,
            })
            log(f"    🎞 {key}[{j}] {cname}"
                + (f" -> widened to {applied}" if widened else "")
                + f" src {round(win[2] / img.f)}px wide, "
                  f"upscale x{worst:.2f}")
        scene_bgs[key] = subs

    # 3. Segments, concat, audio, loudnorm (v1 machinery, unchanged).
    segs = []
    for key, _, dur in BEATS:
        subs = [(s["file"], s["secs"], s["zoom"]) for s in scene_bgs[key]]
        segs.append(P.render_scene_segment(
            key, dur, subs, scene_plan[key]["strips"], outdir, log))
    video_only = outdir / f"{name}-video.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for s in segs:
        cmd += ["-i", str(s)]
    cmd += ["-filter_complex",
            "".join(f"[{i}:v]" for i in range(len(segs))) +
            f"concat=n={len(segs)}:v=1:a=0,format=yuv420p[vout]",
            "-map", "[vout]", "-c:v", "libx264", "-preset", "medium",
            "-crf", "17", "-t", str(TOTAL), str(video_only)]
    P._run(cmd, "segment concat")

    sfx = P.synthesize_sfx(outdir)
    mix = P.build_audio(music_path, sfx, outdir, log)
    out_path = outdir / f"{name}.mp4"
    ln = P.loudnorm_master(video_only, mix, out_path, log)
    licence = P.music_licence(music_path)

    # 4. Manifest — v1 contract preserved (QA reads photo/face/
    #    scenes/background/overlays), extended with the image set.
    def image_record(img, role):
        return {
            "role": role, "local_path": str(img.path),
            "source_url": img.meta.get("source_url"),
            "page_url": img.meta.get("page_url"),
            "license": img.meta.get("license"),
            "artist": img.meta.get("artist"),
            "native_resolution": list(img.native),
            "face_method": img.method, "has_face": img.has_face,
        }

    manifest = {
        "renderer": "reel_renderer_pro2.py (SAMPLE v2 — per-scene "
                    "images on the v6 recipe + pro upgrades)",
        "name": name,
        "article_slug": article_slug,
        "article_id": article_id,
        "category": category,
        "video": str(out_path),
        "duration_s": TOTAL,
        "canvas": [W, H],
        "photo": {"url": photo_url, "local_path": str(hero_path),
                  "width": hero_src.width, "height": hero_src.height,
                  "floor": [R.MIN_PHOTO_W, R.MIN_PHOTO_H]},
        "face": {"method": hero_img.method,
                 "has_face": hero_img.has_face,
                 "box_source": [int(v) for v in hero_img.face_src],
                 "box_bg": [round(v / 2, 1)
                            for v in hero_img.face_master],
                 "chin_bg": (round((hero_img.face_master[1]
                                    + hero_img.face_master[3]) / 2, 1)
                             if hero_img.has_face else None),
                 "margin_px": R.FACE_MARGIN},
        "composition": {"branch": "pro2-multi-image (per-scene 2x "
                                   "masters)", "cover_min_scale":
                        R.COVER_MIN_SCALE},
        "grade": dict(R.ENH),
        "gradient": {"color": R.GRAD_COLOR, "t0": R.GRAD_T0,
                     "exponent": R.GRAD_EXP, "amax": R.GRAD_AMAX},
        "safe_zone": {"x": [R.PANEL_X0, R.PANEL_X1],
                      "top": R.TOP_SAFE, "bottom": R.BOT_SAFE,
                      "text_max_w": R.TEXT_MAX_W},
        "scenes": {},
        "images": {k: image_record(images[k][0], images[k][1])
                   for k, _, _ in BEATS},
        "music": {"file": Path(music_path).name,
                  "path": str(music_path), "licence": licence},
        "pro_upgrades": {
            "multi_image": {
                "max_upscale_rule": MAX_UPSCALE,
                "scenes_with_own_image": [k for k, _, _ in BEATS
                                          if images[k][1] == "own"],
                "scenes_on_hero_fallback": [k for k, _, _ in BEATS
                                            if images[k][1]
                                            == "hero-fallback"],
            },
            "pattern_interrupt_crops": {
                k: [{"crop": s["crop_applied"],
                     "crop_requested": s["crop_requested"],
                     "widened_for_resolution": s["widened"],
                     "window_master": s["window_master"],
                     "src_region_px": s["src_region_px"],
                     "upscale_max": s["upscale_max"],
                     "zoom": s["zoom"]} for s in scene_bgs[k]]
                for k, _, _ in BEATS},
            "kinetic_text": {k: scene_plan[k]["strips"]
                             for k, _, _ in BEATS},
            "sfx": {"hits": [{"t": t, "kind": k2}
                             for t, k2 in P.SFX_HITS],
                    "gain": P.SFX_GAIN, "synthesized": True},
            "loudnorm": ln,
        },
        "render_seconds": round(time.time() - t0, 1),
        "mp4_bytes": out_path.stat().st_size,
    }
    for key, _, _ in BEATS:
        sp = scene_plan[key]
        manifest["scenes"][key] = {
            "start": sp["start"], "duration": sp["duration"],
            "zoom_at_end": round(R.zoom_at(
                sp["start"] + sp["duration"], TOTAL), 4),
            "chin_out": None, "zone_top": sp["zone_top"],
            "zone_h": R.BOT_SAFE - sp["zone_top"], "scale": sp["scale"],
            "content_h": sp["content_h"], "block_top": sp["block_top"],
            "block_bottom": sp["block_top"] + sp["content_h"],
            "text_bbox": sp["text_bbox"], "texts": sp["texts"],
            "pro_crop": sp["crop"],
            "pro_window_master": list(sp["window"]),
            "image_role": sp["image_role"],
        }
    (outdir / "render-manifest.json").write_text(
        json.dumps(manifest, indent=2))
    log(f"✅ {out_path} ({manifest['mp4_bytes'] / 1e6:.1f} MB, "
        f"{manifest['render_seconds']}s)")
    return manifest
