#!/usr/bin/env python3
"""
reel_renderer_pro3.py — SAMPLE-ONLY "pro techniques v3" renderer
(2026-10-24): the jerk fix for the multi-image v2 sample, approved
by Kiran ("continuous camera path + crossfade at switches").

v2 rendered every sub-segment as an independent clip — a separate
pre-cropped still per crop window, each with its own zoompan whose
frame counter restarted — joined by plain concat. Measured on the
v2 render: all 4 sub-segment switches teleport in one frame (worst:
grid at frame 595->596, content jumps (-46, +356) canvas px AND the
scale snaps x0.9528 as the zoom restarts 1.0496 -> 1.0000).

v3 changes ONLY the background assembly (everything else — per-scene
verified images, crop plans, the <=1.5x upscale guard with auto-
widen, kinetic text, SFX, two-pass loudnorm — is v2-identical):

  * CONTINUOUS CAMERA PATH — each scene's background is rendered
    frame by frame from the scene's 2x master as ONE continuous
    pass. A frame's view window replicates v2's zoompan geometry
    exactly (same window, same anchor (0.50, 0.30), same z(on)
    curve), but across a glide window centred on each sub-segment
    switch the view window is interpolated (smoothstep ease) from
    the outgoing sub-segment's view to the incoming one's, so the
    zoom phase carries through the switch — z never restarts.
    Glide length scales with the measured reframing displacement
    (min 8 frames) so a big punch-in glides longer than a nudge.

  * CROSSFADE — across each glide the gliding frame is blended
    toward the incoming sub-segment's own view with a sin^2 bump
    (peak 0.5 at the switch point, zero at both glide ends, where
    the blend is a no-op because the path has arrived). NOTE: v3's
    first renders used a 5-frame bump; measurement showed its own
    beta steps were the largest discontinuity left (hero switch
    pairs 12.6/16.7/12.1 against a 3.6 glide baseline), so the
    bump was stretched across the glide — per-frame beta change
    drops ~25x and the spike with it.

Production reel_renderer.py is untouched. This module NEVER writes
to prebuilt_reels and NEVER uploads.
"""
import json, math, subprocess, time
from pathlib import Path

from PIL import Image

import reel_renderer as R
import reel_renderer_pro as P
import reel_renderer_pro2 as P2

W, H, FPS, TOTAL = R.W, R.H, R.FPS, R.TOTAL
BEATS = R.BEATS
MAX_UPSCALE = P2.MAX_UPSCALE

ANCHOR_X, ANCHOR_Y = 0.50, 0.30   # v2 zoompan anchor fractions
GLIDE_MIN = 8                     # frames, centred on the switch
GLIDE_MAX = 64
GLIDE_PX_PER_FRAME = 11.0         # peak canvas-px/frame budget
GLIDE_FACE_CAP = 20               # glide cap when the destination
                                  # framing puts a face in the text
                                  # zone (pre-existing v2 trait of
                                  # the diaspora wide crop): a long
                                  # glide would sweep the face
                                  # through the text block
XFADE_PEAK = 0.5                  # crossfade bump peak at switch


def _smoothstep(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3.0 - 2.0 * u)


def _view_window(win, zdir, on, frames):
    """Master-coords view window replicating v2's zoompan on the
    still cut from `win`: z(on) = 1 + ZR*on/frames ('in') or
    (1+ZR) - ZR*on/frames ('out'); the visible region is the
    1/z-sized window anchored at (0.50, 0.30). `on` may run a few
    frames past either end during a glide (z extrapolates by
    <0.3% — that is the zoom phase carrying through)."""
    zr = P.ZOOM_RANGE
    z = 1.0 + zr * on / frames if zdir == "in" \
        else (1.0 + zr) - zr * on / frames
    x, y, w, h = win
    fx = (1.0 - 1.0 / z) * ANCHOR_X
    fy = (1.0 - 1.0 / z) * ANCHOR_Y
    return (x + w * fx, y + h * fy, w / z, h / z)


def _lerp_win(a, b, e):
    """Interpolate two view windows: centre linearly, size
    GEOMETRICALLY (log space). For a zoom-dominant reframe the
    relative scale change per frame is then constant instead of
    peaking where the window is smallest — a smoother punch."""
    acx, acy = a[0] + a[2] / 2, a[1] + a[3] / 2
    bcx, bcy = b[0] + b[2] / 2, b[1] + b[3] / 2
    cx, cy = acx + (bcx - acx) * e, acy + (bcy - acy) * e
    w = math.exp(math.log(a[2]) + (math.log(b[2]) - math.log(a[2])) * e)
    h = math.exp(math.log(a[3]) + (math.log(b[3]) - math.log(a[3])) * e)
    return (cx - w / 2, cy - h / 2, w, h)


def _reframe_displacement(va, vb):
    """Max displacement (canvas px) of fixed master points between
    two view windows — sizes the glide so peak velocity is capped."""
    pts = [(va[0], va[1]), (va[0] + va[2], va[1]),
           (va[0], va[1] + va[3]), (va[0] + va[2], va[1] + va[3]),
           (va[0] + va[2] / 2, va[1] + va[3] / 2)]
    worst = 0.0
    for mx, my in pts:
        ax, ay = (mx - va[0]) / va[2] * W, (my - va[1]) / va[3] * H
        bx, by = (mx - vb[0]) / vb[2] * W, (my - vb[1]) / vb[3] * H
        worst = max(worst, math.hypot(bx - ax, by - ay))
    return worst


_GRAD_CACHE = {}


def _apply_gradient_cached(bg):
    """R.apply_gradient, with the (frame-size-only) alpha + colour
    plates cached across frames. Verified identical output."""
    if "alpha" not in _GRAD_CACHE:
        alpha = Image.new("L", (1, H))
        for yy in range(H):
            t = yy / H
            a = 0 if t <= R.GRAD_T0 else int(
                R.GRAD_AMAX * ((t - R.GRAD_T0) / (1 - R.GRAD_T0))
                ** R.GRAD_EXP)
            alpha.putpixel((0, yy), a)
        _GRAD_CACHE["alpha"] = alpha.resize((W, H))
        _GRAD_CACHE["grad"] = Image.new("RGB", (W, H), R.GRAD_COLOR)
    return Image.composite(_GRAD_CACHE["grad"], bg,
                           _GRAD_CACHE["alpha"])


def _face_box_canvas(face_master, view):
    fx, fy, fw, fh = face_master
    vx, vy, vw, vh = view
    return ((fx - vx) / vw * W, (fy - vy) / vh * H,
            fw / vw * W, fh / vh * H)


def _box_hits_rect(box, rect, pad):
    x, y, w, h = box
    return not (x + w < rect[0] - pad or x > rect[2] + pad
                or y + h < rect[1] - pad or y > rect[3] + pad)


def _scene_frame_windows(subs_meta, face_master=None, text_bbox=None):
    """Per-frame view windows for one scene + switch records.
    subs_meta: [{window_master, frames, zoom}] in play order."""
    starts, acc = [], 0
    for s in subs_meta:
        starts.append(acc)
        acc += s["frames"]
    total = acc
    switches = []
    for j in range(len(subs_meta) - 1):
        s = starts[j + 1]
        va = _view_window(subs_meta[j]["window_master"],
                          subs_meta[j]["zoom"],
                          subs_meta[j]["frames"],
                          subs_meta[j]["frames"])
        vb = _view_window(subs_meta[j + 1]["window_master"],
                          subs_meta[j + 1]["zoom"], 0,
                          subs_meta[j + 1]["frames"])
        disp = _reframe_displacement(va, vb)
        # smoothstep peak velocity = 1.5 * disp / glide <= budget
        glide = int(math.ceil(1.5 * disp / GLIDE_PX_PER_FRAME))
        glide = max(GLIDE_MIN, min(GLIDE_MAX, glide))
        face_capped = False
        if face_master is not None and text_bbox is not None:
            # Destination framing face-unsafe (the face lands in
            # the text zone at the incoming sub-segment's views)?
            # Then keep the glide short: the switch stays smooth
            # but the face does not sweep the text block.
            for on in (0, subs_meta[j + 1]["frames"] - 1):
                vend = _view_window(subs_meta[j + 1]["window_master"],
                                    subs_meta[j + 1]["zoom"], on,
                                    subs_meta[j + 1]["frames"])
                if _box_hits_rect(
                        _face_box_canvas(face_master, vend),
                        text_bbox, R.FACE_MARGIN):
                    glide = min(glide, GLIDE_FACE_CAP)
                    face_capped = True
                    break
        switches.append({"frame": s, "glide": glide,
                         "displacement_px": round(disp, 1),
                         "face_capped": face_capped})
    wins = []
    for f in range(total):
        j = max(i for i, st in enumerate(starts) if st <= f)
        base = _view_window(subs_meta[j]["window_master"],
                            subs_meta[j]["zoom"], f - starts[j],
                            subs_meta[j]["frames"])
        for k, sw in enumerate(switches):
            g0 = sw["frame"] - sw["glide"] // 2
            g1 = g0 + sw["glide"]
            if g0 <= f < g1:
                e = _smoothstep((f - g0) / sw["glide"])
                va = _view_window(subs_meta[k]["window_master"],
                                  subs_meta[k]["zoom"],
                                  f - starts[k],
                                  subs_meta[k]["frames"])
                vb = _view_window(subs_meta[k + 1]["window_master"],
                                  subs_meta[k + 1]["zoom"],
                                  f - starts[k + 1],
                                  subs_meta[k + 1]["frames"])
                base = _lerp_win(va, vb, e)
        wins.append(base)
    return wins, switches, starts


def render_scene_segment_v3(key, dur, img, subs_meta, strips,
                            outdir, log, text_bbox=None):
    """One scene: continuous-path background + kinetic strips
    (strip compositing identical to v2/v1)."""
    master = img.master
    wins, switches, starts = _scene_frame_windows(
        subs_meta,
        face_master=img.face_master if img.has_face else None,
        text_bbox=text_bbox)
    total_frames = int(round(dur * FPS))
    assert len(wins) == total_frames, (key, len(wins), total_frames)

    bg_seg = outdir / f"seg-{key}-bg.mp4"
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo",
         "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium",
         "-crf", "17", "-pix_fmt", "yuv420p", str(bg_seg)],
        stdin=subprocess.PIPE)
    for f, win in enumerate(wins):
        frame = master.resize(
            (W, H), Image.LANCZOS,
            box=(win[0], win[1], win[0] + win[2], win[1] + win[3]))
        # Crossfade: a sin^2 bump spanning the whole glide (peak
        # XFADE_PEAK at the switch), blending the gliding frame
        # toward the incoming sub-segment's own view. Per-frame
        # beta steps stay ~0.01, so the blend adds no step of its
        # own; at the glide's end the two images coincide and the
        # bump lands at zero regardless.
        for k, sw in enumerate(switches):
            g0 = sw["frame"] - sw["glide"] // 2
            if g0 <= f < g0 + sw["glide"]:
                u = (f - g0) / sw["glide"]
                beta = XFADE_PEAK * math.sin(math.pi * u) ** 2
                if beta > 0.001:
                    vb = _view_window(
                        subs_meta[k + 1]["window_master"],
                        subs_meta[k + 1]["zoom"], f - starts[k + 1],
                        subs_meta[k + 1]["frames"])
                    inc = master.resize(
                        (W, H), Image.LANCZOS,
                        box=(vb[0], vb[1], vb[0] + vb[2],
                             vb[1] + vb[3]))
                    frame = Image.blend(frame, inc, beta)
        proc.stdin.write(_apply_gradient_cached(frame).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"scene bg render failed: {key}")
    for sw in switches:
        log(f"    🛤 {key} switch @frame {sw['frame']}: glide "
            f"{sw['glide']}f over {sw['displacement_px']}px "
            f"reframe + glide-coupled crossfade "
            f"(peak {XFADE_PEAK})"
            + (" [face-capped]" if sw.get("face_capped") else ""))

    seg = outdir / f"seg-{key}.mp4"
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(bg_seg)]
    for st in strips:
        cmd += ["-loop", "1", "-framerate", str(FPS), "-i",
                str(outdir / st["file"])]
    filters = []
    for i, st in enumerate(strips):
        idx = i + 1
        t0, rise = st["delay"], st["rise"]
        filters.append(
            f"[{idx}:v]format=rgba,"
            f"fade=t=in:st={t0}:d=0.28:alpha=1,"
            f"fade=t=out:st={dur - 0.3:.2f}:d=0.3:alpha=1[st{i}]")
        yexpr = (f"{rise}*pow(1-clip((t-{t0})/0.30\\,0\\,1)\\,2)")
        filters.append(f"[{'0:v' if i == 0 else f'v{i - 1}'}]"
                       f"[st{i}]overlay=0:'{yexpr}'[v{i}]")
    last = f"v{len(strips) - 1}" if strips else "0:v"
    filters.append(f"[{last}]format=yuv420p,"
                   f"trim=end_frame={total_frames}[vout]")
    cmd += ["-filter_complex", ";".join(filters), "-map", "[vout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "17",
            "-t", str(dur), str(seg)]
    P._run(cmd, f"scene segment {key}")
    return seg, switches


def render_reel_pro3(script, hero_path, scene_images, music_path,
                     outdir, name, category="Technology",
                     photo_url=None, article_slug=None,
                     article_id=None, log=print):
    """Render one PRO v3 sample reel. Identical planning to v2;
    only the background assembly differs (continuous camera path +
    crossfade). Returns the manifest dict."""
    t0 = time.time()
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    hero_path = Path(hero_path)

    hero_src = Image.open(hero_path).convert("RGB")
    if hero_src.width < R.MIN_PHOTO_W or hero_src.height < R.MIN_PHOTO_H:
        raise R.PhotoTooSmallError(
            f"hero {hero_src.width}x{hero_src.height} below full-res "
            f"floor {R.MIN_PHOTO_W}x{R.MIN_PHOTO_H}")
    log(f"  🖼  hero (fallback): {hero_src.width}x{hero_src.height}")

    hero_img = P2.SceneImage(hero_path, {"role": "article hero"}, log)
    images = {}
    for key, _, _ in BEATS:
        spec = (scene_images or {}).get(key)
        if spec and Path(spec["path"]).exists():
            try:
                images[key] = (P2.SceneImage(spec["path"], spec, log),
                               "own")
                continue
            except Exception as e:
                log(f"  ⚠ scene {key}: own image failed ({e}); "
                    f"falling back to hero")
        images[key] = (hero_img, "hero-fallback")
    hero_img.master.save(outdir / "master-hero-2x.jpg", quality=92)

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
                "file": bp, "secs": frames / FPS, "frames": frames,
                "zoom": zdir,
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

    segs, scene_switches = [], {}
    for key, _, dur in BEATS:
        seg, switches = render_scene_segment_v3(
            key, dur, images[key][0], scene_bgs[key],
            scene_plan[key]["strips"], outdir, log,
            text_bbox=scene_plan[key]["text_bbox"])
        segs.append(seg)
        scene_switches[key] = switches
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
        "renderer": "reel_renderer_pro3.py (SAMPLE v3 — per-scene "
                    "images + continuous camera path & crossfade "
                    "on the v6 recipe + pro upgrades)",
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
        "composition": {"branch": "pro3-multi-image-continuous "
                                   "(per-scene 2x masters)",
                        "cover_min_scale": R.COVER_MIN_SCALE},
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
            "continuous_camera": {
                "glide_min_frames": GLIDE_MIN,
                "glide_max_frames": GLIDE_MAX,
                "glide_peak_px_per_frame": GLIDE_PX_PER_FRAME,
                "crossfade": "glide-coupled sin^2 bump",
                "crossfade_peak_beta": XFADE_PEAK,
                "zoom_anchor": [ANCHOR_X, ANCHOR_Y],
                "switches": scene_switches,
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
