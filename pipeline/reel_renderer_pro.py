#!/usr/bin/env python3
"""
reel_renderer_pro.py — SAMPLE-ONLY "pro techniques" renderer for
Kiran's judgment (2026-10-24). NOT production: the locked v6
production renderer (reel_renderer.py) is untouched and its defaults
are unchanged. This module imports the production building blocks
(font metrics, scene painters, fit planner, face detection, bright
grade, legibility gradient) and changes ONLY the assembly, adding
the four upgrades from the professional-reel research:

  1. PATTERN-INTERRUPT CROPS — instead of one cover crop + a single
     slow zoom for 35 s, each scene plays across wide -> medium ->
     tight crops of the SAME full-res article photo (sub-segments
     inside long scenes, so the picture changes every ~3 s). Crops
     are windows of one 2x "master" composition; per-scene text
     zones are re-planned per crop with the production rules
     (real face -> below the chin mapped through the worst-case
     zoom; no face -> the standard lower band), and a crop that
     cannot fit its scene's text falls back toward wider crops.

  2. KINETIC TEXT — each scene's production-painted overlay is
     split into element bands (alpha row runs: eyebrow pill, each
     text line, each stat row) and the bands arrive staggered
     (fade-in + an ease-out rise) instead of one static block.
     All fit checks still happen in the production painters BEFORE
     compositing; the full overlay is also written to disk exactly
     as production writes it (overlay-<beat>.png) so frame QA's
     expected-text geometry stays valid.

  3. LOUDNESS — the mixed audio (music + SFX) is mastered with
     two-pass ffmpeg loudnorm to -14 LUFS integrated / -1 dBTP,
     and the FINAL file is re-measured; measured values land in
     the manifest (audio.loudnorm).

  4. SFX + LICENCE LOG — 4 subtle synthesized transition hits
     (airy whoosh / soft pop, generated with ffmpeg lavfi — no
     external assets) at scene boundaries, mixed well under the
     bed; the music track's licence (from music/music-index.json)
     is recorded in the manifest.

This module NEVER writes to prebuilt_reels and NEVER uploads.
"""
import json, math, subprocess, sys, time
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_renderer as R

W, H, FPS, TOTAL = R.W, R.H, R.FPS, R.TOTAL
BEATS = R.BEATS

# ── Upgrade 1: crop choreography ─────────────────────────────────────
# Crop library: name -> (center_x, center_y, width) as fractions of
# the 2x master frame. Windows always keep the 9:16 aspect.
CROPS = {
    "wide":       (0.50, 0.50, 1.00),
    "medA":       (0.50, 0.45, 0.70),
    "medB":       (0.47, 0.58, 0.70),
    "tightFlame": (0.50, 0.72, 0.50),
    "tightPlume": (0.44, 0.70, 0.50),
}
# Per beat: [(crop_name, share_of_scene, zoom_dir)] — sub-segments
# inside the >=6 s beats so the picture changes every ~3 s.
SCENE_CROPS = {
    "hook":     [("wide", 1.0, "in")],
    "news":     [("medA", 0.55, "in"), ("medB", 0.45, "out")],
    "hero":     [("tightFlame", 0.55, "out"), ("medA", 0.45, "in")],
    "grid":     [("medB", 0.55, "in"), ("tightFlame", 0.45, "in")],
    "diaspora": [("tightPlume", 0.55, "in"), ("wide", 0.45, "out")],
    "payoff":   [("wide", 1.0, "in")],
}
ZOOM_RANGE = 0.05               # within-scene Ken Burns (pro pass)
LADDER = ["tightFlame", "tightPlume", "medA", "medB", "wide"]

# ── Upgrade 4: SFX placement (scene boundaries, seconds) ─────────────
SFX_HITS = [(10.0, "whoosh"), (16.0, "pop"),
            (23.0, "whoosh"), (30.0, "pop")]
SFX_GAIN = {"whoosh": 0.25, "pop": 0.22}

# ── Upgrade 3: loudnorm targets ──────────────────────────────────────
LN_I, LN_TP, LN_LRA = -14.0, -1.0, 11.0


def _run(cmd, what):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{what} failed: {r.stderr[-1500:]}")
    return r


def compose_master_2x(enh, face_enh):
    """Production compose_cover geometry at 2x canvas: the master
    every scene crop is cut from. Returns (master, face_in_master)."""
    W2, H2 = 2 * W, 2 * H
    scale = max(W2 / enh.width, H2 / enh.height)
    sw, sh = round(enh.width * scale), round(enh.height * scale)
    img = enh.resize((sw, sh), Image.LANCZOS)
    fx, fy, fw, fh = [v * scale for v in face_enh]
    x0 = int(min(max(fx + fw / 2 - W2 / 2, 0), max(sw - W2, 0)))
    y0 = int(min(max(fy - 300, 0), max(sh - H2, 0)))
    return img.crop((x0, y0, x0 + W2, y0 + H2)), (fx - x0, fy - y0, fw, fh)


def crop_window(master, name):
    cx, cy, wf = CROPS[name]
    mw = int(master.width * wf)
    mh = int(mw * H / W)
    x0 = int(min(max(cx * master.width - mw / 2, 0), master.width - mw))
    y0 = int(min(max(cy * master.height - mh / 2, 0), master.height - mh))
    return (x0, y0, mw, mh)


def plan_scene_pro(key, script, category, window, face_master, has_face):
    """Production zone rules, evaluated against ONE scene crop.
    Returns (scale, painter, block_top, zone_top) or None."""
    if has_face:
        sy = H / window[3]
        chin_scene = (face_master[1] + face_master[3] - window[1]) * sy
        # Worst case over the scene's zoom range (z up to 1.05):
        # below the 0.30 anchor line the chin only moves DOWN as z
        # grows; above it, it moves up (zone only gets easier).
        chin_out = R.bg_to_out_y(chin_scene, 1.0 + ZOOM_RANGE)
        zone_top = max(R.TOP_SAFE, math.ceil(chin_out) + R.FACE_MARGIN)
    else:
        zone_top = R.NO_FACE_ZONE_TOP
    zone_h = R.BOT_SAFE - zone_top
    fit = R.fit_scene(key, script, category, zone_h, R.COVER_MIN_SCALE)
    if fit is None:
        return None
    s, content_h, painter = fit
    shift = min(90, max(0, (zone_h - content_h) // 2))
    return s, painter, zone_top + shift, zone_top, content_h


def split_strips(ov, key, outdir):
    """Upgrade 2: split a painted overlay into element bands by
    alpha row runs. Returns strip dicts with staggered timing."""
    alpha = np.array(ov.split()[3])
    rows = np.where((alpha > 10).any(axis=1))[0]
    bands = []
    if len(rows):
        start = prev = int(rows[0])
        for r in rows[1:]:
            r = int(r)
            if r - prev > 18:
                bands.append((start, prev))
                start = r
            prev = r
        bands.append((start, prev))
    # Merge hairline bands (e.g. the 3px gold stat divider) into the
    # previous band instead of dropping them — a dropped band's
    # pixels would never reach the screen.
    merged = []
    for b in bands:
        if merged and b[1] - b[0] < 6:
            merged[-1] = (merged[-1][0], b[1])
        else:
            merged.append(b)
    bands = merged
    n = len(bands)
    step = min(0.16, 1.25 / max(1, n - 1)) if n > 1 else 0.0
    tallest = max(range(n), key=lambda i: bands[i][1] - bands[i][0]) \
        if n else -1
    strips = []
    for i, (y0, y1) in enumerate(bands):
        strip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        strip.paste(ov.crop((0, y0, W, y1 + 1)), (0, y0))
        p = outdir / f"strip-{key}-{i}.png"
        strip.save(p)
        strips.append({
            "file": p.name, "rows": [y0, y1],
            "delay": round(0.15 + i * step, 2),
            "rise": 44 if i == tallest else 28,
        })
    return strips


def synthesize_sfx(outdir):
    """Upgrade 4: synthesize the two transition hits with lavfi."""
    whoosh = outdir / "sfx-whoosh.wav"
    _run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
          "anoisesrc=color=pink:duration=0.5:sample_rate=48000",
          "-af", "highpass=f=300,lowpass=f=900,"
                 "afade=t=in:st=0:d=0.22,afade=t=out:st=0.28:d=0.22",
          str(whoosh)], "whoosh synth")
    pop = outdir / "sfx-pop.wav"
    _run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
          "aevalsrc='0.8*sin(2*PI*(150-500*t)*t)*exp(-28*t)'"
          ":duration=0.16:sample_rate=48000",
          "-af", "volume=0.9", str(pop)], "pop synth")
    return {"whoosh": whoosh, "pop": pop}


def build_audio(music_path, sfx, outdir, log):
    """Music bed (production trim/fade) + SFX hits -> mix.wav."""
    mix = outdir / "audio-mix.wav"
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(music_path),
           "-i", str(sfx["whoosh"]), "-i", str(sfx["pop"])]
    filters = [
        f"[0:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS,"
        f"afade=t=out:st={TOTAL - 1.6}:d=1.6[mus]",
        "[1:a]asplit=2[w1][w2]", "[2:a]asplit=2[p1][p2]",
    ]
    labels = ["[mus]"]
    used = {"whoosh": 0, "pop": 0}
    for i, (t, kind) in enumerate(SFX_HITS):
        pool = ["w1", "w2"] if kind == "whoosh" else ["p1", "p2"]
        src = pool[used[kind]]
        used[kind] += 1
        ms = int(t * 1000)
        filters.append(f"[{src}]adelay={ms}|{ms},"
                       f"volume={SFX_GAIN[kind]}[s{i}]")
        labels.append(f"[s{i}]")
    filters.append("".join(labels) +
                   f"amix=inputs={len(labels)}:duration=first:"
                   "normalize=0[mix]")
    cmd += ["-filter_complex", ";".join(filters), "-map", "[mix]",
            "-t", str(TOTAL), "-ar", "48000", str(mix)]
    _run(cmd, "audio mix")
    log(f"  🔊 audio mix: bed + {len(SFX_HITS)} SFX hits at "
        f"{[t for t, _ in SFX_HITS]}s")
    return mix


def loudnorm_master(video_mp4, mix_wav, out_mp4, log):
    """Upgrade 3: two-pass loudnorm; returns measured-final dict."""
    # Pass 1 — measure the mix.
    r = subprocess.run(
        ["ffmpeg", "-i", str(mix_wav), "-af",
         f"loudnorm=I={LN_I}:TP={LN_TP}:LRA={LN_LRA}:print_format=json",
         "-f", "null", "-"], capture_output=True, text=True)
    meas = json.loads(r.stderr[r.stderr.index("[Parsed_loudnorm"):
                                r.stderr.rindex("}") + 1].split("\n", 1)[1])
    args = (f"loudnorm=I={LN_I}:TP={LN_TP}:LRA={LN_LRA}"
            f":measured_I={meas['input_i']}:measured_TP={meas['input_tp']}"
            f":measured_LRA={meas['input_lra']}"
            f":measured_thresh={meas['input_thresh']}"
            f":offset={meas['target_offset']}:linear=true")
    _run(["ffmpeg", "-y", "-v", "error", "-i", str(video_mp4),
          "-i", str(mix_wav), "-af", args, "-map", "0:v", "-map", "1:a",
          "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
          "-t", str(TOTAL), "-movflags", "+faststart", str(out_mp4)],
         "loudnorm pass 2")
    # Verify — measure the FINAL file's audio.
    r = subprocess.run(
        ["ffmpeg", "-i", str(out_mp4), "-vn", "-af",
         "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    fin = json.loads(r.stderr[r.stderr.index("[Parsed_loudnorm"):
                              r.stderr.rindex("}") + 1].split("\n", 1)[1])
    out = {"target_I": LN_I, "target_TP": LN_TP, "target_LRA": LN_LRA,
           "mix_measured_I": float(meas["input_i"]),
           "mix_measured_TP": float(meas["input_tp"]),
           "final_measured_I": float(fin["input_i"]),
           "final_measured_TP": float(fin["input_tp"]),
           "final_measured_LRA": float(fin["input_lra"])}
    log(f"  🔊 loudnorm: mix {out['mix_measured_I']} LUFS / "
        f"{out['mix_measured_TP']} dBTP -> final "
        f"{out['final_measured_I']} LUFS / {out['final_measured_TP']} dBTP")
    return out


def music_licence(music_path):
    idx_path = Path(__file__).resolve().parent / "music" \
        / "music-index.json"
    try:
        idx = json.loads(idx_path.read_text())
        for t in idx.get("tracks", []):
            if t.get("filename") == Path(music_path).name:
                return {"file": t["filename"],
                        "license": t.get("license"),
                        "source": t.get("source"),
                        "author": t.get("author"),
                        "source_url": t.get("source_url")}
    except Exception:
        pass
    return {"file": Path(music_path).name, "license": None,
            "source": None, "author": None, "source_url": None}


def render_scene_segment(key, dur, subs, strips, outdir, log):
    """One scene: pattern-interrupt bg sub-segments + kinetic strips."""
    seg = outdir / f"seg-{key}.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for png, _, _ in subs:
        cmd += ["-loop", "1", "-framerate", str(FPS), "-i", str(png)]
    for st in strips:
        cmd += ["-loop", "1", "-framerate", str(FPS), "-i",
                str(outdir / st["file"])]
    filters = []
    for j, (_, secs, zdir) in enumerate(subs):
        frames = int(round(secs * FPS))
        z = (f"1+{ZOOM_RANGE}*on/{frames}" if zdir == "in"
             else f"{1 + ZOOM_RANGE}-{ZOOM_RANGE}*on/{frames}")
        filters.append(
            f"[{j}:v]scale=2160:3840:flags=lanczos,"
            f"zoompan=z='{z}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*0.30'"
            f":d={frames}:s={W}x{H}:fps={FPS},"
            f"trim=end_frame={frames},setpts=PTS-STARTPTS[bg{j}]")
    if len(subs) > 1:
        filters.append("".join(f"[bg{j}]" for j in range(len(subs))) +
                       f"concat=n={len(subs)}:v=1:a=0[bgv]")
        last = "bgv"
    else:
        last = "bg0"
    for i, st in enumerate(strips):
        idx = len(subs) + i
        t0, rise = st["delay"], st["rise"]
        filters.append(
            f"[{idx}:v]format=rgba,"
            f"fade=t=in:st={t0}:d=0.28:alpha=1,"
            f"fade=t=out:st={dur - 0.3:.2f}:d=0.3:alpha=1[st{i}]")
        yexpr = (f"{rise}*pow(1-clip((t-{t0})/0.30\\,0\\,1)\\,2)")
        filters.append(f"[{last}][st{i}]overlay=0:'{yexpr}'[v{i}]")
        last = f"v{i}"
    filters.append(f"[{last}]format=yuv420p,"
                   f"trim=end_frame={int(round(dur * FPS))}[vout]")
    cmd += ["-filter_complex", ";".join(filters), "-map", "[vout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "17",
            "-t", str(dur), str(seg)]
    _run(cmd, f"scene segment {key}")
    return seg


def render_reel_pro(script, hero_path, music_path, outdir, name,
                    category="Technology", photo_url=None,
                    article_slug=None, article_id=None, log=print):
    """Render one PRO sample reel. Returns the manifest dict.
    Raises R.PhotoTooSmallError / R.TextFitError / RuntimeError."""
    t0 = time.time()
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    hero_path = Path(hero_path)

    # 0. Full-res floor (production rule, unchanged).
    src = Image.open(hero_path).convert("RGB")
    if src.width < R.MIN_PHOTO_W or src.height < R.MIN_PHOTO_H:
        raise R.PhotoTooSmallError(
            f"photo {src.width}x{src.height} below full-res floor "
            f"{R.MIN_PHOTO_W}x{R.MIN_PHOTO_H}")
    log(f"  🖼  photo: {src.width}x{src.height} (floor ✓)")

    # 1. Face detection + bright grade (production, unchanged).
    face_src, method = R.detect_face_box(src)
    has_face = method.startswith(("yunet", "haar"))
    log(f"  🔍 face detection: method={method} has_face={has_face}")
    enh = R.enhance_raw(src)
    face_enh = tuple(v * R.ENH["upscale"] for v in face_src)

    # 2. Master composition (2x) + per-scene crop planning.
    master, face_master = compose_master_2x(enh, face_enh)
    master.save(outdir / "master-2x.jpg", quality=92)
    scene_plan = {}
    for key, start, dur in BEATS:
        primary = SCENE_CROPS[key][0][0]
        order = [primary] + [c for c in LADDER if c != primary]
        chosen = None
        for cand in order:
            window = crop_window(master, cand)
            plan = plan_scene_pro(key, script, category, window,
                                  face_master, has_face)
            if plan is not None:
                chosen = (cand, window, plan)
                break
        if chosen is None:
            raise R.TextFitError(
                f"scene '{key}' cannot fit under any crop")
        cand, window, (s, painter, block_top, zone_top, content_h) = chosen
        scene_plan[key] = {
            "start": start, "duration": dur, "crop": cand,
            "window": window, "scale": s, "painter": painter,
            "block_top": block_top, "zone_top": zone_top,
            "content_h": content_h,
        }
        log(f"  ✓ scene {key}: primary crop {primary}"
            + ("" if cand == primary else f" -> fell back to {cand}")
            + f" scale={s} block_top={block_top}")

    # 3. Per-scene backgrounds + production overlays + kinetic strips.
    overlay_paths, scene_bgs = {}, {}
    for key, _, dur in BEATS:
        sp = scene_plan[key]
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sp["painter"](ov, sp["block_top"])
        p = outdir / f"overlay-{key}.png"
        ov.save(p)
        overlay_paths[key] = p
        sp["text_bbox"] = R._overlay_text_bbox(ov)
        sp["texts"] = R.SCENE_TEXTS[key](script, category)
        sp["strips"] = split_strips(ov, key, outdir)
        subs = []
        frames_left = int(round(dur * FPS))
        plan_subs = SCENE_CROPS[key]
        for j, (cname, share, zdir) in enumerate(plan_subs):
            frames = frames_left if j == len(plan_subs) - 1 \
                else int(round(dur * FPS * share))
            frames_left -= frames
            window = crop_window(master, cname)
            bg = master.crop(window).resize((W, H), Image.LANCZOS)
            bg = R.apply_gradient(bg)
            bp = outdir / f"bg-{key}-{j}.jpg"
            bg.save(bp, quality=92)
            subs.append((bp, frames / FPS, zdir, cname, window))
            if key == "hook" and j == 0:
                bg.save(outdir / "background.jpg", quality=92)
        scene_bgs[key] = subs
        log(f"  🎞  scene {key}: {len(subs)} crop sub-segment(s), "
            f"{len(sp['strips'])} kinetic strip(s)")

    # 4. Render scene segments, concat, add audio, master loudness.
    segs = []
    for key, _, dur in BEATS:
        subs = [(bp, secs, zdir)
                for bp, secs, zdir, _, _ in scene_bgs[key]]
        segs.append(render_scene_segment(key, dur, subs,
                                         scene_plan[key]["strips"],
                                         outdir, log))
    video_only = outdir / f"{name}-video.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for s in segs:
        cmd += ["-i", str(s)]
    cmd += ["-filter_complex",
            "".join(f"[{i}:v]" for i in range(len(segs))) +
            f"concat=n={len(segs)}:v=1:a=0,format=yuv420p[vout]",
            "-map", "[vout]", "-c:v", "libx264", "-preset", "medium",
            "-crf", "17", "-t", str(TOTAL), str(video_only)]
    _run(cmd, "segment concat")

    sfx = synthesize_sfx(outdir)
    mix = build_audio(music_path, sfx, outdir, log)
    out_path = outdir / f"{name}.mp4"
    ln = loudnorm_master(video_only, mix, out_path, log)

    licence = music_licence(music_path)
    manifest = {
        "renderer": "reel_renderer_pro.py (SAMPLE — pro upgrades on "
                    "v6 recipe)",
        "name": name,
        "article_slug": article_slug,
        "article_id": article_id,
        "category": category,
        "video": str(out_path),
        "duration_s": TOTAL,
        "canvas": [W, H],
        "photo": {"url": photo_url, "local_path": str(hero_path),
                  "width": src.width, "height": src.height,
                  "floor": [R.MIN_PHOTO_W, R.MIN_PHOTO_H]},
        "face": {"method": method, "has_face": has_face,
                 "box_source": [int(v) for v in face_src],
                 "box_bg": [round(v / 2, 1) for v in face_master],
                 "chin_bg": (round((face_master[1] + face_master[3]) / 2, 1)
                             if has_face else None),
                 "margin_px": R.FACE_MARGIN},
        "composition": {"branch": "pro-crops (master 2x cover)",
                        "cover_min_scale": R.COVER_MIN_SCALE},
        "grade": dict(R.ENH),
        "gradient": {"color": R.GRAD_COLOR, "t0": R.GRAD_T0,
                     "exponent": R.GRAD_EXP, "amax": R.GRAD_AMAX},
        "safe_zone": {"x": [R.PANEL_X0, R.PANEL_X1], "top": R.TOP_SAFE,
                      "bottom": R.BOT_SAFE, "text_max_w": R.TEXT_MAX_W},
        "scenes": {},
        "music": {"file": Path(music_path).name,
                  "path": str(music_path), "licence": licence},
        "pro_upgrades": {
            "pattern_interrupt_crops": {
                k: [{"crop": c, "window_master": list(w),
                     "zoom": z}
                    for _, _, z, c, w in scene_bgs[k]] for k, _, _
                in BEATS},
            "kinetic_text": {
                k: scene_plan[k]["strips"] for k, _, _ in BEATS},
            "sfx": {"hits": [{"t": t, "kind": k2}
                             for t, k2 in SFX_HITS],
                    "gain": SFX_GAIN, "synthesized": True},
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
        }
    (outdir / "render-manifest.json").write_text(
        json.dumps(manifest, indent=2))
    log(f"✅ {out_path} ({manifest['mp4_bytes'] / 1e6:.1f} MB, "
        f"{manifest['render_seconds']}s)")
    return manifest
