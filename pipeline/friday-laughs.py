#!/usr/bin/env python3
"""
friday-laughs.py — Friday Laughs comic generator for The Videshi.

Character bible: ../comics/character-bible.md
Frontend: src/components/homepage/FridayLaughs.tsx (reads `comics` table)

Modes:
  --write-script
      Pick the next topic (rotates through the 10 bible categories, tracked in
      the state file), ask GPT-4o-mini for a 4-panel script, save everything
      to pipeline/.state/friday-laughs-pending.json, and print the image
      generation prompt for the media pipeline.

  --publish --image <path> [--title ...]
      Composite header / panel numbers / speech bubbles / yellow punchline
      banner onto the generated 4-panel artwork with PIL, upload to Supabase
      storage (article-images/comics/), and insert a row into the `comics`
      table.

The cron worker (a Muse agent) runs --write-script, generates the image with
the media tool using the printed prompt, then runs --publish --image <path>.

Usage:
  python3 -u friday-laughs.py --write-script
  python3 -u friday-laughs.py --publish --image /tmp/comic.png
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import textwrap

sys.stdout.reconfigure(line_buffering=True)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(REPO_ROOT, "pipeline", ".state")
ROTATION_FILE = os.path.join(STATE_DIR, "friday-laughs.json")
PENDING_FILE = os.path.join(STATE_DIR, "friday-laughs-pending.json")

# ── Topic categories (from character-bible.md) ──────────────────────────────
CATEGORIES = [
    {"id": "immigration", "label": "Immigration & visa struggles",
     "brief": "green card wait, H-1B lottery, USCIS delays, visa stamping trips"},
    {"id": "groceries", "label": "Grocery / cost of living shock",
     "brief": "US vs India prices, desi grocery store hauls, $8 tomatoes"},
    {"id": "family-calls", "label": "Family calls from India",
     "brief": "WhatsApp calls, time zones, mom's advice, good-morning forwards"},
    {"id": "tech-life", "label": "Tech life in Silicon Valley",
     "brief": "standups, layoffs, side projects, performance reviews"},
    {"id": "code-switching", "label": "Cultural code-switching",
     "brief": "office vs home behavior, American holidays vs Indian ones"},
    {"id": "food", "label": "Food & cooking abroad",
     "brief": "finding ingredients, explaining Indian food to Americans, pressure cooker nostalgia"},
    {"id": "housing", "label": "Housing & rent in the Bay Area",
     "brief": "rent prices, roommates, landlords, the eternal buying-vs-renting debate"},
    {"id": "commute", "label": "Driving & commuting",
     "brief": "Bay Bridge traffic, Caltrain, parking tickets, DMV visits"},
    {"id": "parenting", "label": "Parenting as immigrants",
     "brief": "US school system, playdates, explaining festivals to kids' friends"},
    {"id": "return-india", "label": "Return-to-India debates",
     "brief": "'should we go back?', reverse culture shock math, parents' hopes"},
]

# ── Character descriptions (condensed from the bible, for prompts) ──────────
CHARACTERS = {
    "raj": ("Raj Mehta, late-20s Indian-American tech worker: messy black hair, "
            "rectangular glasses, navy blue hoodie, slim build, wide-eyed earnest "
            "expressions. Always holding a coffee mug with a funny slogan."),
    "priya": ("Priya Mehta, late-20s, Raj's wife: long dark wavy hair, green top "
              "in casual Indian-modern style, sharp expressive face, deadpan "
              "confident delivery."),
    "amma": ("Amma, Raj's mom in her mid-50s in India: warm face, traditional "
             "salwar/sari. Always shown on a phone screen as a WhatsApp video "
             "call."),
    "vik": ("Vikram ('Vik'), mid-30s coworker: slightly stocky, beard, polo shirt, "
            "confident know-it-all posture."),
    "dadi": ("Dadi, Raj's grandmother in her 70s: white hair in a bun, reading "
             "glasses, simple cotton sari, serene wise expression."),
}

# ── GPT script prompt ───────────────────────────────────────────────────────
SCRIPT_SYSTEM = """You write 4-panel comic strip scripts for "Friday Laughs" by The Videshi Comics — warm, affectionate satire about Indian-diaspora life in the Bay Area. Think slice-of-life humor, never mean-spirited, never punching down. Diaspora in-jokes that make immigrants feel seen.

Characters (use 2-3 per strip):
- Raj: earnest late-20s tech worker, navy hoodie, rectangular glasses, messy black hair. Things happen TO him. Wide-eyed reactions.
- Priya: his sharp, practical wife. Deadpan voice of reason. Her line usually sets up or lands the joke.
- Amma: his mom in India, appears via WhatsApp video call. Compares US prices to India, asks when he's visiting.
- Vik: mid-30s coworker, bearded know-it-all, got his green card "the hard way."
- Dadi: 70s grandmother, occasional appearance, drops surprise wisdom.

Structure: Panel 1 = setup (ordinary moment), Panel 2 = buildup (complication), Panel 3 = twist (expectation subverted), Panel 4 = punchline (the laugh + the truth).

Rules:
- Dialogue must be SHORT: 1-2 lines per character per panel, comic-strip length.
- The yellow punchline banner is a one-liner caption summarizing the joke (max 90 chars).
- Raj's coffee mug has a different funny slogan every strip (max 22 chars).
- Title: 2-5 words, evocative.
- Caption: one warm sentence for the website (max 120 chars).
- Humor is warm and specific: real details (USCIS case trackers, ₹-to-$ math, Caltrain delays) beat generic jokes.

Return ONLY valid JSON, no markdown fences:
{
  "title": "...",
  "caption": "...",
  "mug_slogan": "...",
  "punchline_banner": "...",
  "characters": ["raj", "priya"],
  "panels": [
    {"panel": 1, "scene": "one-sentence visual description of the scene",
     "dialogue": {"raj": "...", "priya": "..."}},
    ... 4 panels total
  ]
}"""


def load_env():
    for name in (".env.supabase", ".env.openai"):
        p = os.path.expanduser(f"~/workspace/{name}")
        if os.path.exists(p):
            for line in open(p):
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def curl_json(url, data=None, headers=None, timeout=60):
    cmd = ["curl", "-sS", "--max-time", str(timeout), url]
    for h in (headers or []):
        cmd.extend(["-H", h])
    if data is not None:
        cmd.extend(["-d", json.dumps(data)])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
    return json.loads(r.stdout)


def gpt_script(category):
    """Ask GPT-4o-mini for a 4-panel script on the given category."""
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        sys.exit("ERROR: OPENAI_API_KEY not set")
    user_msg = (
        f"Write a Friday Laughs strip on this topic: {category['label']} "
        f"({category['brief']}). Use characters that fit the topic naturally. "
        f"Make it feel like this specific week in diaspora life."
    )
    resp = curl_json(
        "https://api.openai.com/v1/chat/completions",
        data={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SCRIPT_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            "temperature": 0.9,
            "max_tokens": 1200,
        },
        headers=[f"Authorization: Bearer {key}", "Content-Type: application/json"],
        timeout=90,
    )
    text = resp["choices"][0]["message"]["content"].strip()
    # Strip accidental markdown fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    script = json.loads(text)
    assert len(script["panels"]) == 4, "GPT returned != 4 panels"
    # Normalize character keys to lowercase (GPT sometimes returns 'ammA')
    script["characters"] = [c.lower() for c in script.get("characters", [])]
    for p in script["panels"]:
        p["dialogue"] = {k.lower(): v for k, v in p.get("dialogue", {}).items()}
    return script


def next_category():
    os.makedirs(STATE_DIR, exist_ok=True)
    try:
        with open(ROTATION_FILE) as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {"last_index": -1, "history": []}
    idx = (state["last_index"] + 1) % len(CATEGORIES)
    state["last_index"] = idx
    state["history"].append({
        "category": CATEGORIES[idx]["id"],
        "date": datetime.date.today().isoformat(),
    })
    state["history"] = state["history"][-52:]
    with open(ROTATION_FILE, "w") as f:
        json.dump(state, f, indent=2)
    return CATEGORIES[idx]


def build_image_prompt(script, category):
    """Detailed prompt for the media pipeline. NO text in the artwork —
    all text (dialogue, banners, headers) is composited with PIL later,
    because AI text rendering is unreliable."""
    chars = [CHARACTERS[c] for c in script["characters"] if c in CHARACTERS]
    char_block = "\n".join(f"- {c}" for c in chars)
    scenes = "\n".join(
        f"Panel {p['panel']}: {p['scene']}" for p in script["panels"]
    )
    return f"""Four-panel comic strip in a 2x2 grid layout (panel 1 top-left, panel 2 top-right, panel 3 bottom-left, panel 4 bottom-right), clean modern cartoon style, warm colors, expressive faces.

CHARACTERS (keep consistent across all 4 panels):
{char_block}

SCENES (illustrate each, NO text, NO words, NO letters anywhere in the image — leave the top 15% of each panel as clear sky/background space for dialogue bubbles to be added later):
{scenes}

SETTING DETAILS: Bay Area apartment interior and/or office; SF skyline or Transamerica Pyramid visible through a window in at least one panel; small Indian touches (potted plant, framed family photo, steel dabba containers).

STYLE: clean cartoon/manga-influenced linework, warm palette, soft shading. Wide landscape composition. Absolutely no text, no speech bubbles, no captions, no watermarks in the artwork."""


def cmd_write_script(args):
    load_env()
    category = next_category()
    print(f"Topic this week: {category['label']} ({category['id']})")
    script = gpt_script(category)
    # Attach a mug slogan per panel is overkill; bible says one per strip.
    # GPT returns one mug_slogan for the strip.
    pending = {
        "category": category["id"],
        "category_label": category["label"],
        "script": script,
        "image_prompt": build_image_prompt(script, category),
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    with open(PENDING_FILE, "w") as f:
        json.dump(pending, f, indent=2)
    print(f"Script saved to {PENDING_FILE}")
    print(f"Title: {script['title']}")
    print(f"Punchline: {script['punchline_banner']}")
    print()
    print("=" * 70)
    print("IMAGE GENERATION PROMPT (use with the media pipeline, no text in art):")
    print("=" * 70)
    print(pending["image_prompt"])


# ── PIL compositing ─────────────────────────────────────────────────────────
def _font(size, bold=True):
    from PIL import ImageFont
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for p in (f"/usr/share/fonts/truetype/dejavu/{name}",
              f"/usr/share/fonts/{name}"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = f"{cur} {w}".strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill,
                           outline=outline, width=width)


def composite(script, src_path, out_path):
    """Overlay header, panel numbers, speech bubbles, and the yellow
    punchline banner onto the 4-panel artwork."""
    from PIL import Image, ImageDraw

    img = Image.open(src_path).convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    # ── Header bar ──
    header_h = int(H * 0.07)
    draw.rectangle([0, 0, W, header_h], fill=(11, 29, 58))  # Videshi navy
    fh = _font(int(header_h * 0.42))
    draw.text((int(W * 0.03), header_h // 2), "FRIDAY LAUGHS",
              font=fh, fill=(212, 168, 67), anchor="lm")  # gold
    fl = _font(int(header_h * 0.30), bold=False)
    draw.text((int(W * 0.97), header_h // 2), "the Videshi comics",
              font=fl, fill=(255, 255, 255), anchor="rm")

    # ── Panel geometry (2x2 grid below header, above banner) ──
    banner_h = int(H * 0.11)
    grid_top = header_h
    grid_h = H - header_h - banner_h
    pw, ph = W // 2, grid_h // 2

    # Panel divider lines
    line_c = (230, 230, 230)
    draw.line([W // 2, grid_top, W // 2, grid_top + grid_h], fill=line_c, width=3)
    draw.line([0, grid_top + grid_h // 2, W, grid_top + grid_h // 2],
              fill=line_c, width=3)

    # ── Speech bubbles + panel numbers ──
    name_font = _font(max(14, int(W * 0.011)))
    dlg_font = _font(max(16, int(W * 0.0135)))
    num_font = _font(max(18, int(W * 0.016)))

    for p in script["panels"]:
        i = p["panel"] - 1
        col, row = i % 2, i // 2
        px, py = col * pw, grid_top + row * ph

        # Panel number badge (top-left of panel)
        bx, by, br = px + 12, py + 12, int(W * 0.016)
        draw.ellipse([bx, by, bx + br * 2, by + br * 2], fill=(11, 29, 58))
        draw.text((bx + br, by + br), str(p["panel"]), font=num_font,
                  fill=(255, 255, 255), anchor="mm")

        # Build bubble text: "NAME: line" per speaker
        lines = []
        for who, line in p["dialogue"].items():
            who_label = {"raj": "RAJ", "priya": "PRIYA", "amma": "AMMA",
                         "vik": "VIK", "dadi": "DADI"}.get(who, who.upper())
            lines.append((who_label, line))
        if not lines:
            continue

        # Measure bubble
        max_tw = pw - 60
        rendered = []
        total_h = 16
        for who_label, line in lines:
            wl = [(who_label, name_font)]
            for chunk in _wrap(draw, line, dlg_font, max_tw - 24):
                wl.append((chunk, dlg_font))
            rendered.append(wl)
            total_h += sum(
                int(draw.textbbox((0, 0), t, font=f)[3] + 6) for t, f in wl
            ) + 10
        bubble_w = max(
            max(draw.textlength(t, font=f) for t, f in wl) for wl in rendered
        ) + 32
        bubble_w = min(bubble_w, max_tw)
        bubble_h = total_h

        # Bubble position: top-center of panel, below the number badge area
        bx0 = px + (pw - bubble_w) // 2
        by0 = py + 14
        # Keep clear of the badge on panel left
        if bx0 < px + 60:
            bx0 = px + 60
        _rounded(draw, [bx0, by0, bx0 + bubble_w, by0 + bubble_h],
                 radius=14, fill=(255, 255, 255),
                 outline=(30, 30, 30), width=2)
        # Bubble tail
        cx = bx0 + bubble_w // 2
        draw.polygon([(cx - 10, by0 + bubble_h - 2), (cx + 10, by0 + bubble_h - 2),
                      (cx, by0 + bubble_h + 14)], fill=(255, 255, 255),
                     outline=(30, 30, 30))

        y = by0 + 12
        for wl in rendered:
            for t, f in wl:
                colr = (163, 45, 47) if f == name_font else (20, 20, 20)
                draw.text((bx0 + 16, y), t, font=f, fill=colr)
                y += int(draw.textbbox((0, 0), t, font=f)[3] + 6)
            y += 8

    # ── Yellow punchline banner ──
    by0 = H - banner_h
    draw.rectangle([0, by0, W, H], fill=(255, 193, 7))
    draw.rectangle([0, by0, W, by0 + 4], fill=(11, 29, 58))
    bf = _font(int(banner_h * 0.34))
    banner_text = script["punchline_banner"]
    lines = _wrap(draw, banner_text, bf, W - 80)
    # shrink font if two lines needed and too tall
    while len(lines) > 2:
        bf = _font(bf.size - 2)
        lines = _wrap(draw, banner_text, bf, W - 80)
    line_h = int(bf.size * 1.25)
    ty = by0 + (banner_h - line_h * len(lines)) // 2 + 4
    for ln in lines:
        tw = draw.textlength(ln, font=bf)
        draw.text(((W - tw) / 2, ty), ln, font=bf, fill=(20, 20, 20))
        ty += line_h

    img.save(out_path, "JPEG", quality=92)
    print(f"Composited comic saved to {out_path} ({W}x{H})")
    return out_path


def slugify(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    return re.sub(r"\s+", "-", s.strip())[:80]


def sb_upload(local_path, storage_path):
    sb_url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    host = sb_url.replace("https://", "")
    # Need BOTH apikey and Authorization headers (AGENTS.md)
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "60", "-X", "POST",
         f"{sb_url}/storage/v1/object/article-images/{storage_path}",
         "-H", f"apikey: {key}",
         "-H", f"Authorization: Bearer {key}",
         "-H", "Content-Type: image/jpeg",
         "--data-binary", f"@{local_path}"],
        capture_output=True, text=True, timeout=70,
    )
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        sys.exit(f"ERROR: storage upload failed: {r.stdout[:300]} {r.stderr[:200]}")
    if isinstance(data, dict) and data.get("error"):
        sys.exit(f"ERROR: storage upload: {data}")
    return f"{sb_url}/storage/v1/object/public/article-images/{storage_path}"


def sb_insert(row):
    sb_url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "30", "-X", "POST",
         f"{sb_url}/rest/v1/comics",
         "-H", f"apikey: {key}",
         "-H", f"Authorization: Bearer {key}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=representation",
         "-d", json.dumps(row)],
        capture_output=True, text=True, timeout=40,
    )
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        sys.exit(f"ERROR: comics insert failed: {r.stdout[:300]}")
    if isinstance(data, dict) and data.get("code"):
        sys.exit(f"ERROR: comics insert: {data.get('message')}")
    return data


def cmd_publish(args):
    load_env()
    if not os.path.exists(PENDING_FILE):
        sys.exit(f"ERROR: no pending script at {PENDING_FILE} — run --write-script first")
    with open(PENDING_FILE) as f:
        pending = json.load(f)
    script = pending["script"]
    category = pending["category"]

    if not os.path.exists(args.image):
        sys.exit(f"ERROR: image not found: {args.image}")

    # Composite text onto the artwork
    out_path = os.path.join("/tmp", f"friday-laughs-{slugify(script['title'])}.jpg")
    composite(script, args.image, out_path)

    if args.test:
        print(f"TEST MODE: composited image saved to {out_path}, "
              "skipping upload/insert.")
        return

    # Upload
    storage_path = f"comics/{slugify(script['title'])}.jpg"
    image_url = sb_upload(out_path, storage_path)
    print(f"Uploaded: {image_url}")

    # Insert row
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    row = {
        "title": script["title"],
        "slug": slugify(script["title"]),
        "topic": category,
        "script": script,
        "image_url": image_url,
        "caption": script["caption"],
        "characters": script["characters"],
        "published_at": now,
    }
    inserted = sb_insert(row)
    print(f"Inserted comic: {inserted[0]['id']} — {inserted[0]['title']}")

    # Archive pending
    os.rename(PENDING_FILE, PENDING_FILE + ".done")
    print("Done. Pending file archived.")


def main():
    ap = argparse.ArgumentParser(description="Friday Laughs comic generator")
    ap.add_argument("--write-script", action="store_true",
                    help="Pick topic + write 4-panel script via GPT")
    ap.add_argument("--publish", action="store_true",
                    help="Composite, upload, and insert the comic")
    ap.add_argument("--image", default=None,
                    help="Path to the generated 4-panel artwork")
    ap.add_argument("--test", action="store_true",
                    help="With --publish: composite only, skip upload/insert "
                         "(saves to /tmp for review)")
    args = ap.parse_args()

    if args.write_script:
        cmd_write_script(args)
    elif args.publish:
        if not args.image:
            sys.exit("ERROR: --publish needs --image <path>")
        cmd_publish(args)
    else:
        ap.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
