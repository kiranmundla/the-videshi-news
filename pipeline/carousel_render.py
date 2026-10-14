#!/usr/bin/env python3
"""
carousel_render.py — Phase 1 Instagram carousel renderer (sample scope).

Builds a 4-card 1080x1350 (4:5) carousel for one article, modeled on
the Firstpost format Kiran approved 2026-10-13:
  1. Cover — full-bleed graded photo, smooth full-frame gradient,
     gold eyebrow pill, big serif display headline (measured, no
     boxes, no scrim blob — the locked reel type discipline).
  2. Quote — solid navy; oversized gold quote mark; the quote in
     large serif type; the speaker's verified photo (face-aware
     circular crop of the article's full-res hero) with name + role.
  3. Key facts — solid navy; three short verified facts.
  4. End card — The Videshi masthead + THIS story's headline and
     standfirst (an end card about a different story is exactly the
     failure Kiran spotted on the Firstpost post — so the end card is
     fact-checked like everything else).

Gates, same as reels:
  - Fact-check: the quote must be a VERBATIM substring of the article
    body (normalized) with the speaker grounded; every other card
    string goes through reel_factcheck (deterministic + GPT-4o-mini).
    The cover eyebrow must equal the article's own category.
  - Card QA (computed, post-render): text-layer bboxes inside the
    margins, text/background contrast sampled from the card pixels,
    cover text clear of the detected face, photo resolution floor.

LOCAL ONLY — renders PNGs to a local outdir; never posts anywhere.

Usage:
  python3 -u carousel_render.py --spec spec.json --article article.json \
      --hero hero.jpg --outdir <dir> [--no-llm]
Exit codes: 0 ready · 1 held · 4 input error.
"""
import argparse, json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_factcheck
from reel_renderer import (NAVY, GOLD, RED, WHITE, OFFWHITE, TEXT_SHADOW,
                           STROKE_FILL, GRAD_COLOR, GRAD_EXP,
                           MIN_PHOTO_W, MIN_PHOTO_H, TextFitError,
                           PhotoTooSmallError, enhance_raw,
                           detect_face_box, text_width, _wrap)

CW, CH = 1080, 1350               # 4:5 IG portrait
MARGIN = 72
CONTENT_W = CW - 2 * MARGIN       # 936
QA_MARGIN_X = (48, CW - 48)       # hard text bounds for QA
QA_MARGIN_Y = (52, CH - 52)
BG_SOLID = NAVY                   # solid cards: brand navy, not black
SERIF_BOLD = "NotoSerifDisplay-Bold.ttf"
SERIF_SEMI = "NotoSerifDisplay-SemiBold.ttf"

from reel_renderer import FONT_DIR
_font_cache = {}


def sfont(fname, size):
    key = (fname, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(str(FONT_DIR / fname), size)
    return _font_cache[key]


def ifont(weight, size):
    return sfont(f"Inter-{weight}.ttf", size)


def fit_serif(text, fname, size, max_w, max_lines, min_size=34):
    """Measured wrap+shrink for serif text (same discipline as the
    reel renderer: real font metrics, TextFitError when it can't fit)."""
    size = int(size)
    while size >= min_size:
        f = sfont(fname, size)
        lines = _wrap(f, text, max_w)
        if len(lines) <= max_lines and all(
                text_width(f, ln) <= max_w for ln in lines):
            return f, lines, size
        size -= 2
    raise TextFitError(f"serif cannot fit {text!r}")


def fit_inter(text, weight, size, max_w, max_lines, min_size=26):
    size = int(size)
    while size >= min_size:
        f = ifont(weight, size)
        lines = _wrap(f, text, max_w)
        if len(lines) <= max_lines and all(
                text_width(f, ln) <= max_w for ln in lines):
            return f, lines, size
        size -= 2
    raise TextFitError(f"inter cannot fit {text!r}")


def draw_lines(draw, x, y, lines, font, fill, lh, align="left",
               shadow=False, stroke=0, cx=None):
    for ln in lines:
        if align == "center":
            tx = cx - text_width(font, ln) / 2
        elif align == "right":
            tx = x - text_width(font, ln)
        else:
            tx = x
        if shadow:
            draw.text((tx + 2, y + 3), ln, font=font, fill=TEXT_SHADOW,
                      stroke_width=stroke, stroke_fill=TEXT_SHADOW)
        draw.text((tx, y), ln, font=font, fill=fill,
                  stroke_width=stroke, stroke_fill=STROKE_FILL)
        y += lh
    return y


def tracked(draw, x, y, text, font, fill, tracking, align="left"):
    total = text_width(font, text, tracking)
    tx = x if align == "left" else (x - total / 2 if align == "center"
                                    else x - total)
    for ch in text:
        draw.text((tx, y), ch, font=font, fill=fill)
        tx += font.getlength(ch) + tracking
    return total


def pill(draw, x, y, text):
    """Gold eyebrow pill, navy tracked caps — the brand badge from the
    locked reel design, left-anchored for the editorial cover."""
    f = ifont(700, 30)
    tw = text_width(f, text.upper(), 6)
    pw, ph = tw + 52, 58
    draw.rounded_rectangle([x, y, x + pw, y + ph], ph // 2,
                           fill=GOLD + (255,))
    tracked(draw, x + 26, y + (ph - 30) // 2 - 2, text.upper(), f,
            NAVY + (255,), 6)
    return pw, ph


def gradient_card(img, amax=178, t0=0.22):
    """Smooth full-frame downward gradient (locked recipe form)."""
    alpha = Image.new("L", (1, CH))
    for yy in range(CH):
        t = yy / CH
        a = 0 if t <= t0 else int(amax * ((t - t0) / (1 - t0)) ** GRAD_EXP)
        alpha.putpixel((0, yy), a)
    alpha = alpha.resize((CW, CH))
    grad = Image.new("RGB", (CW, CH), GRAD_COLOR)
    return Image.composite(grad, img, alpha)


def cover_crop(enh, face_enh):
    """Face-aware cover-fill crop of the enhanced photo to 1080x1350.
    Returns (card_img, face_box_in_card)."""
    s = max(CW / enh.width, CH / enh.height)
    sw, sh = round(enh.width * s), round(enh.height * s)
    img = enh.resize((sw, sh), Image.LANCZOS)
    fx, fy, fw, fh = [v * s for v in face_enh]
    fcx, fcy = fx + fw / 2, fy + fh / 2
    x0 = int(min(max(fcx - CW / 2, 0), max(sw - CW, 0)))
    y0 = int(min(max(fcy - CH * 0.38, 0), max(sh - CH, 0)))
    card = img.crop((x0, y0, x0 + CW, y0 + CH))
    return card, (fx - x0, fy - y0, fw, fh)


def circle_photo(enh, face_enh, diameter=300):
    """Face-aware circular crop (gold-ringed by the caller)."""
    fx, fy, fw, fh = face_enh
    side = max(fw, fh) * 2.3
    cx, cy = fx + fw / 2, fy + fh / 2
    x0 = int(min(max(cx - side / 2, 0), max(enh.width - side, 0)))
    y0 = int(min(max(cy - side / 2, 0), max(enh.height - side, 0)))
    crop = enh.crop((x0, y0, int(x0 + side), int(y0 + side)))
    crop = crop.resize((diameter * 2, diameter * 2), Image.LANCZOS)
    mask = Image.new("L", (diameter * 2, diameter * 2), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, diameter * 2, diameter * 2],
                                 fill=255)
    out = Image.new("RGBA", (diameter * 2, diameter * 2), (0, 0, 0, 0))
    out.paste(crop, (0, 0), mask)
    return out.resize((diameter, diameter), Image.LANCZOS)


# ── Card builders: each returns (card_img, text_overlay_img) ────────────────
def build_cover(spec, enh, face_enh):
    card, face_card = cover_crop(enh, face_enh)
    card = gradient_card(card.convert("RGB"))
    ov = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    pill(d, MARGIN, 64, spec["eyebrow"])
    # Headline: serif display, bottom-anchored, must clear the chin.
    f, lines, sz = fit_serif(spec["cover_headline"], SERIF_BOLD, 86,
                             CONTENT_W, 4, min_size=40)
    lh = int(sz * 1.16)
    block_h = lh * len(lines)
    bottom = CH - 78
    top = bottom - block_h
    chin = face_card[1] + face_card[3]
    if top < chin + 44:
        # Tighten: shrink until the block clears the chin or bottoms out.
        while sz > 40 and top < chin + 44:
            sz -= 4
            f, lines, _ = fit_serif(spec["cover_headline"], SERIF_BOLD,
                                    sz, CONTENT_W, 4, min_size=40)
            lh = int(sz * 1.16)
            block_h = lh * len(lines)
            top = bottom - block_h
    # Gold rule above the headline.
    d.rectangle([MARGIN, top - 34, MARGIN + 84, top - 28],
                fill=GOLD + (255,))
    draw_lines(d, MARGIN, top, lines, f, WHITE + (255,), lh,
               shadow=True, stroke=max(3, round(sz * 0.09)))
    card.paste(Image.alpha_composite(card.convert("RGBA"), ov)
               .convert("RGB"), (0, 0))
    return card, ov, {"face_box_card": [round(v, 1) for v in face_card],
                      "headline_size": sz, "headline_lines": len(lines)}


def build_quote(spec, enh, face_enh):
    card = Image.new("RGB", (CW, CH), BG_SOLID)
    ov = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    q = spec["quote"]
    # Oversized gold quote mark.
    fmark = sfont(SERIF_BOLD, 300)
    d.text((MARGIN - 8, 30), "“", font=fmark, fill=GOLD + (255,))
    # Quote text.
    f, lines, sz = fit_serif(q["text"], SERIF_SEMI, 64, CONTENT_W, 7,
                             min_size=38)
    lh = int(sz * 1.34)
    y = draw_lines(d, MARGIN, 330, lines, f, WHITE + (255,), lh)
    # Speaker block: photo lower-right, name/role to its left.
    photo = circle_photo(enh, face_enh, 300)
    px, py = CW - MARGIN - 300, CH - 120 - 300
    ring = Image.new("RGBA", (312, 312), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([0, 0, 312, 312], outline=GOLD + (255,),
                                 width=6)
    card.paste(ring, (px - 6, py - 6), ring)
    card.paste(photo, (px, py), photo)
    # Name + role, right-aligned toward the photo.
    tx_right = px - 44
    f_name, name_lines, _ = fit_inter(q["speaker"], 800, 42, 560, 2)
    role_w = 560
    f_role, role_lines, _ = fit_inter(q["role"], 400, 30, role_w, 3)
    name_h = int(42 * 1.2) * len(name_lines)
    role_h = int(30 * 1.3) * len(role_lines)
    block_h = 26 + name_h + 10 + role_h
    by = py + 150 - block_h // 2
    d.rectangle([tx_right - 84, by, tx_right, by + 5],
                fill=GOLD + (255,))
    by += 26
    by = draw_lines(d, tx_right, by, name_lines, f_name, WHITE + (255,),
                    int(42 * 1.2), align="right")
    by += 10
    draw_lines(d, tx_right, by, role_lines, f_role,
               OFFWHITE + (255,), int(30 * 1.3), align="right")
    card.paste(Image.alpha_composite(card.convert("RGBA"), ov)
               .convert("RGB"), (0, 0))
    return card, ov, {"quote_size": sz, "quote_lines": len(lines),
                      "text_bottom": y}


def build_facts(spec):
    card = Image.new("RGB", (CW, CH), BG_SOLID)
    ov = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    f_eb = ifont(700, 30)
    tracked(d, MARGIN, 104, "KEY FACTS", f_eb, GOLD + (255,), 6)
    d.rectangle([MARGIN, 168, MARGIN + 84, 173], fill=GOLD + (255,))
    y = 262
    for i, fact in enumerate(spec["facts"]):
        f_num = sfont(SERIF_BOLD, 74)
        d.text((MARGIN, y - 8), f"{i + 1:02d}", font=f_num,
               fill=GOLD + (255,))
        f, lines, sz = fit_inter(fact, 600, 45, CONTENT_W - 170, 4,
                                 min_size=30)
        lh = int(sz * 1.32)
        fy = draw_lines(d, MARGIN + 170, y, lines, f, WHITE + (255,),
                        lh)
        y = fy + 100
        if i < len(spec["facts"]) - 1:
            d.line([MARGIN, y - 50, CW - MARGIN, y - 50],
                   fill=(212, 168, 67, 90), width=2)
    card.paste(Image.alpha_composite(card.convert("RGBA"), ov)
               .convert("RGB"), (0, 0))
    return card, ov, {"facts_bottom": y}


def build_end(spec):
    card = Image.new("RGB", (CW, CH), BG_SOLID)
    ov = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    cx = CW // 2
    # Masthead.
    f_mast = ifont(900, 56)
    w_mast = tracked(d, cx, 300, "THE VIDESHI", f_mast, GOLD + (255,), 10,
                     align="center")
    d.rectangle([cx - 190, 392, cx + 190, 397], fill=GOLD + (255,))
    # This story's headline.
    f, lines, sz = fit_serif(spec["end"]["headline"], SERIF_SEMI, 60,
                             880, 4, min_size=36)
    lh = int(sz * 1.24)
    y = draw_lines(d, 0, 470, lines, f, WHITE + (255,), lh,
                   align="center", cx=cx)
    # Standfirst line.
    f2, lines2, _ = fit_inter(spec["end"]["line"], 400, 33, 820, 3)
    y = draw_lines(d, 0, y + 36, lines2, f2, OFFWHITE + (255,),
                   int(33 * 1.35), align="center", cx=cx)
    # Footer.
    f_url = ifont(700, 32)
    tracked(d, cx, CH - 150, "thevideshi.com", f_url, GOLD + (255,), 2,
            align="center")
    f_h = ifont(400, 27)
    tracked(d, cx, CH - 104, "@the.videshi", f_h, OFFWHITE + (255,), 1,
            align="center")
    card.paste(Image.alpha_composite(card.convert("RGBA"), ov)
               .convert("RGB"), (0, 0))
    return card, ov, {"headline_size": sz}


# ── Fact-check for carousel text ────────────────────────────────────────────
def carousel_factcheck(spec, article, use_llm=True):
    """Verbatim quote check + the standard claim gate over all other
    card text. Returns (report_dict, ok)."""
    body_norm = reel_factcheck.norm_text(article.get("body") or "")
    quote = spec["quote"]["text"]
    verbatim = reel_factcheck.norm_text(quote) in body_norm
    art_norm = reel_factcheck.norm_text(
        " ".join([article.get("headline") or "",
                  article.get("subheadline") or "",
                  article.get("body") or ""]))
    speaker_ok = reel_factcheck.entity_grounded(
        spec["quote"]["speaker"], art_norm, article.get("body") or "")
    # A role line is a composite ("Chair, University of X") that never
    # appears verbatim — ground it per entity + per number instead.
    role = spec["quote"]["role"]
    role_ok = all(
        reel_factcheck.entity_grounded(e, art_norm,
                                       article.get("body") or "")
        for e in reel_factcheck.extract_entities(role)) and \
        reel_factcheck.extract_numbers(role) <= \
        reel_factcheck.article_number_set(
            " ".join([article.get("headline") or "",
                      article.get("subheadline") or "",
                      article.get("body") or ""]))
    cat_ok = spec["eyebrow"].strip().upper() == \
        (article.get("category") or "").replace("-", " ").upper()
    pseudo = {
        "hook_line": spec["cover_headline"],
        "news_summary": spec["end"]["line"],
        "hook_stat": {"big": "", "sub": "", "eyebrow": ""},
        "stats": [{"big": "", "label": f} for f in spec["facts"]],
        "diaspora_bullets": [spec["quote"]["speaker"],
                             spec["quote"]["role"]],
        "payoff": spec["end"]["headline"],
        "key_entities": [],
    }
    gate = reel_factcheck.run_gate(pseudo, article, use_llm=use_llm)
    ok = bool(verbatim and speaker_ok and role_ok and cat_ok
              and gate["verdict"] == "pass")
    report = {"verbatim_quote": verbatim, "speaker_grounded": speaker_ok,
              "role_grounded": role_ok, "eyebrow_is_category": cat_ok,
              "claim_gate": gate, "verdict": "pass" if ok else "fail"}
    return report, ok


# ── Card QA (computed from the rendered pixels) ─────────────────────────────
def run_card_qa(cards, overlays, manifest):
    import numpy as np
    from reel_frame_qa import luminance
    results = []
    hard_fail = []
    contrast_marks = 0
    for i, (card_path, ov) in enumerate(zip(cards, overlays), start=1):
        img = Image.open(card_path).convert("RGB")
        dims_ok = img.size == (CW, CH)
        alpha = ov.split()[3]
        bbox = alpha.getbbox() or (0, 0, 0, 0)
        margins_ok = (bbox[0] >= QA_MARGIN_X[0] and bbox[2] <= QA_MARGIN_X[1]
                      and bbox[1] >= QA_MARGIN_Y[0]
                      and bbox[3] <= QA_MARGIN_Y[1])
        # Contrast: bright-fill glyph cores (white/gold overlay pixels
        # at full alpha — shadows and dark strokes excluded, they
        # would drag the sample) vs a ring around the text bbox,
        # sampled from the actual card image.
        arr = np.array(img).astype(np.float32)
        mask = np.array(alpha) > 60
        ov_arr = np.array(ov.convert("RGBA")).astype(np.float32)
        core = (ov_arr[..., 3] >= 250) & (luminance(ov_arr) > 90)
        lum = luminance(arr)
        x0, y0, x1, y1 = bbox
        ring = np.zeros_like(mask)
        ring[max(y0 - 26, 0):min(y1 + 26, CH),
             max(x0 - 26, 0):min(x1 + 26, CW)] = True
        import cv2
        dil = cv2.dilate(mask.astype("uint8"),
                         np.ones((13, 13), np.uint8)) > 0
        ring &= ~dil
        if core.sum() >= 100 and ring.sum() >= 200:
            delta = float(np.median(lum[core]) - np.median(lum[ring]))
        else:
            delta = 0.0
        contrast_ok = delta >= 30
        contrast_full = delta >= 50
        contrast_marks += 1 if contrast_full else 0
        face_overlap = None
        if i == 1 and manifest.get("cover", {}).get("face_box_card"):
            fx, fy, fw, fh = manifest["cover"]["face_box_card"]
            region = np.zeros_like(mask)
            region[int(fy):int(fy + fh), int(fx):int(fx + fw)] = True
            face_overlap = int((mask & region).sum())
            if face_overlap > 30:
                hard_fail.append("cover_face_overlap")
        if not dims_ok:
            hard_fail.append(f"card{i}_dims")
        if not margins_ok:
            hard_fail.append(f"card{i}_margins")
        if not contrast_ok:
            hard_fail.append(f"card{i}_contrast")
        results.append({"card": i, "dims_ok": bool(dims_ok),
                        "text_bbox": list(bbox),
                        "margins_ok": bool(margins_ok),
                        "contrast_delta": round(delta, 1),
                        "contrast_full": bool(contrast_full),
                        "face_overlap_px": face_overlap})
    n = len(cards)
    photo_ok = manifest["photo"]["width"] >= MIN_PHOTO_W \
        and manifest["photo"]["height"] >= MIN_PHOTO_H
    score = round(3.0 * (1 if not any('margins' in h for h in hard_fail)
                         else 0)
                  + 3.0 * (contrast_marks / n)
                  + 2.0 * (1 if "cover_face_overlap" not in hard_fail
                           else 0)
                  + 1.0 * (1 if photo_ok else 0)
                  + 1.0 * (1 if all(r["dims_ok"] for r in results)
                           else 0), 2)
    passed = not hard_fail and photo_ok and score >= 7.0
    return {"qa_passed": bool(passed), "qa_score": score,
            "pass_threshold": 7.0, "failing_checks": hard_fail,
            "cards": results, "photo_ok": bool(photo_ok)}


# ── Driver ──────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--spec", required=True)
    ap.add_argument("--article", required=True)
    ap.add_argument("--hero", required=True)
    ap.add_argument("--photo-url", default=None)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--stem", default="carousel")
    ap.add_argument("--no-llm", action="store_true")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    spec = json.loads(Path(args.spec).read_text())
    article = json.loads(Path(args.article).read_text())
    if isinstance(article, list):
        article = article[0]
    slug = article.get("slug") or "carousel"
    verdict = {"kind": "carousel", "article_slug": slug,
               "status": "held", "stage": None}

    def finish(code):
        (outdir / "carousel-verdict.json").write_text(
            json.dumps(verdict, indent=2))
        print(json.dumps(verdict, indent=2))
        return code

    print(f"🗂  carousel for {slug}")
    print("── gate 1/2: fact-check (incl. verbatim quote)")
    fc, fc_ok = carousel_factcheck(spec, article,
                                   use_llm=not args.no_llm)
    (outdir / "carousel-factcheck.json").write_text(json.dumps(fc,
                                                              indent=2))
    verdict["factcheck"] = {
        "verdict": fc["verdict"], "verbatim_quote": fc["verbatim_quote"],
        "speaker_grounded": fc["speaker_grounded"],
        "role_grounded": fc["role_grounded"],
        "eyebrow_is_category": fc["eyebrow_is_category"],
        "llm_cost_usd": fc["claim_gate"]["llm"]["cost_usd"]}
    if not fc_ok:
        verdict["stage"] = "factcheck"
        print("🚫 HELD at fact-check", file=sys.stderr)
        return finish(1)
    print("   ✅ quote verbatim; all card text grounded")

    print("── render + gate 2/2: card QA")
    src = Image.open(args.hero).convert("RGB")
    if src.width < MIN_PHOTO_W or src.height < MIN_PHOTO_H:
        verdict["stage"] = "photo_floor"
        verdict["detail"] = f"{src.width}x{src.height}"
        print(f"🚫 HELD: photo below floor", file=sys.stderr)
        return finish(1)
    face_src, method = detect_face_box(src)
    enh = enhance_raw(src)
    face_enh = tuple(v * 2 for v in face_src)
    manifest = {"photo": {"url": args.photo_url, "width": src.width,
                          "height": src.height},
                "face": {"method": method,
                         "box_source": [int(v) for v in face_src]}}
    try:
        cover, ov1, m1 = build_cover(spec, enh, face_enh)
        quote_c, ov2, m2 = build_quote(spec, enh, face_enh)
        facts_c, ov3, m3 = build_facts(spec)
        end_c, ov4, m4 = build_end(spec)
    except TextFitError as e:
        verdict["stage"] = "render_fit"
        verdict["detail"] = str(e)
        print(f"🚫 HELD at render: {e}", file=sys.stderr)
        return finish(1)
    manifest["cover"] = m1
    manifest["quote"] = m2
    manifest["facts"] = m3
    manifest["end"] = m4
    cards, overlays = [], []
    for i, (card, ov) in enumerate(
            [(cover, ov1), (quote_c, ov2), (facts_c, ov3), (end_c, ov4)],
            start=1):
        p = outdir / f"{args.stem}-{i}.png"
        card.save(p)
        ov.save(outdir / f"{args.stem}-{i}-overlay.png")
        cards.append(p)
        overlays.append(ov)
    (outdir / "carousel-manifest.json").write_text(
        json.dumps(manifest, indent=2))
    qa = run_card_qa(cards, overlays, manifest)
    (outdir / "carousel-qa.json").write_text(json.dumps(qa, indent=2))
    verdict["qa"] = {"score": qa["qa_score"], "passed": qa["qa_passed"],
                     "failing_checks": qa["failing_checks"]}
    verdict["cards"] = [str(c) for c in cards]
    if not qa["qa_passed"]:
        verdict["stage"] = "card_qa"
        print(f"🚫 HELD at card QA: {qa['failing_checks']}",
              file=sys.stderr)
        return finish(1)
    verdict["status"] = "ready"
    verdict["stage"] = "complete"
    print(f"✅ carousel READY — QA {qa['qa_score']}/10 · "
          f"{', '.join(str(c) for c in cards)}")
    return finish(0)


if __name__ == "__main__":
    sys.exit(main())
