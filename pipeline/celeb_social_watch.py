#!/usr/bin/env python3
"""
Celebrity social watcher for The Videshi.

Kiran's scoped policy (2026-11-08): for a WHITELIST of celebrities
(pipeline/celeb-whitelist.json) we may do the NDTV model — take the
celebrity's OWN public Instagram posts and republish the updates as
our own branded carousels — under these guardrails:

  * whitelist only; the source is the celeb's own verified post
    (handle + verified flag re-checked on every fetch) — never fan
    accounts, paparazzi, or other outlets;
  * brand-collab / ad posts are skipped (marked seen, reason logged);
  * "📸 @<handle>" credit rides on the queue captions AND on the
    deck's closing slide, with the original post URL;
  * provenance for every staged photo set is appended to the image
    ledger (pipeline/.state/image-provenance.jsonl);
  * everything lands in the delayed-publish queue
    (social_queue.add_entry) — NOTHING is published here; Kiran
    vetoes the actual photos at a flush sitting, as with every
    other staged entry.

Articles on the site are untouched by this — they keep using
official embeds. Videos/reels are never downloaded; they are
recorded as reel candidates in the state file for Kiran to see.

Detection: instagram-cli posts per enabled handle (read-only).
Media: the post's public embed page
(https://www.instagram.com/p/<shortcode>/embed/captioned/) fetched
with curl — urllib/requests fail through this box's proxy. If the
embed page yields no scontent photo URLs the post is skipped and
the run report says so; there is no fallback source.

State: pipeline/.state/celeb-watch-state.json
  {handle: {"seen_post_ids": [...], "reel_candidates": [...],
            "author_name": ..., "followers": ...}}
The first run for a handle SEEDS all currently-visible posts as
seen without staging anything (no backlog dump into the queue).

Usage:
  python3 -u celeb_social_watch.py              detect new + stage
  python3 -u celeb_social_watch.py --dry-run    detect + report only
  python3 -u celeb_social_watch.py --stage-post <post_id>
      stage one specific post even if already seen (sample/testing)
  python3 -u celeb_social_watch.py --make-reel <post_id>
      build a YouTube Short for one celeb post through the
      production reel chain (fact-check gate -> Reels v7 render ->
      frame QA, exactly as reel_produce.py drives them) and, only
      if every gate passes, upload it UNLISTED via
      reel_publish.py (sample protocol: Kiran reviews and flips
      it public himself). The reel's ground truth is the post's
      own caption; its photos are the post's own frames; the
      closing scene is the navy credit card. A gate hold stops
      the chain — nothing uploads.
"""
import argparse
import hashlib
import html as html_mod
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import social_card as sc          # noqa: E402  Cards v1 style/helpers
import social_queue               # noqa: E402

IG_CLI = "/opt/hatch/bin/instagram-cli"
IG_ACCOUNT_ID = "17841426005310230"        # @the.videshi
WHITELIST_FILE = HERE / "celeb-whitelist.json"
STATE_FILE = HERE / ".state" / "celeb-watch-state.json"
OUT_ROOT = HERE / ".state" / "celeb-cards"
LEDGER_PATH = HERE / ".state" / "image-provenance.jsonl"
SOURCE_TAG = "celeb-social-watch"

# Mobile UA is load-bearing: Instagram serves a logged-out checkpoint
# shell (no media) to desktop UAs from this box, but the real embed —
# caption + scontent media URLs — to an iPhone UA (verified 2026-11-08:
# desktop UA -> 512 KB shell with zero media; iPhone UA -> 291 KB with
# the carousel's media URLs).
BROWSER_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
              "AppleWebKit/605.1.15 (KHTML, like Gecko) "
              "Version/17.0 Mobile/15E148 Safari/604.1")

MIN_LONG_SIDE = 800        # hard floor: frames below this are dropped
TARGET_LONG_SIDE = 1080    # preferred minimum where the post offers it
THREADS_TEXT_LIMIT = 500
FB_TEXT_LIMIT = 1000

# Brand-collab / ad markers (Kiran's rule: personal and festive
# updates are the genre; ads are not). Matched against the
# lowercased caption; a hit skips the post but marks it seen.
AD_MARKERS = ["#ad", "#sponsored", "#collab", "paid partnership",
              "in collaboration with", "use code", "% off", "shop now"]

VIDEO_MEDIA_TYPES = {"video", "reel", "clip"}

# Topical hashtag hooks (caption keyword -> tag). Capped so the
# total hashtag count never exceeds 4 including the name tag and
# #TheVideshi.
TOPIC_TAGS = [("diwali", "#Diwali"), ("birthday", "#HappyBirthday"),
              ("trailer", "#TrailerOut"), ("wedding", "#Wedding"),
              ("song", "#NewMusic"), ("festival", "#Festival"),
              ("movie", "#Cinema"), ("film", "#Cinema")]


# ── whitelist ─────────────────────────────────────────────────────
def load_whitelist(path=WHITELIST_FILE):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    entries = data.get("celebrities", [])
    out = []
    for e in entries:
        if not e.get("name"):
            continue
        out.append({"name": e["name"],
                    "handle": (e.get("handle") or "").strip().lstrip("@"),
                    "enabled": bool(e.get("enabled")),
                    "note": e.get("note") or ""})
    return out


def enabled_entries(entries):
    return [e for e in entries if e["enabled"] and e["handle"]]


# ── ad / collab filter ────────────────────────────────────────────
def ad_marker_in(caption):
    """Return the matched ad marker, or None for a clean caption."""
    low = (caption or "").lower()
    for marker in AD_MARKERS:
        if marker in low:
            return marker
    return None


# ── instagram-cli detection ───────────────────────────────────────
def fetch_posts(handle, limit=5):
    """instagram-cli posts for one handle -> parsed JSON dict.
    Read-only; raises RuntimeError on CLI/parse failure."""
    cmd = [IG_CLI, "posts", "--account-id", IG_ACCOUNT_ID,
           "--username", handle, "--limit", str(limit)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError(f"instagram-cli exit {r.returncode}: "
                           f"{(r.stderr or r.stdout)[:200]}")
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"instagram-cli non-JSON output: "
                           f"{r.stdout[:200]}")


def own_posts(data, handle):
    """Rows in a posts response that belong to `handle` itself.
    The CLI response can include other accounts' rows; only rows
    whose username matches the whitelist handle count, and only
    when the author rows carry verified=True."""
    rows = [p for p in (data.get("posts") or [])
            if (p.get("username") or "").lower() == handle.lower()]
    return rows


def is_feed_post(post):
    """True for real feed posts/reels. The posts response also
    carries story + highlight items (URLs under /stories/) — those
    are not posts and are never staged or treated as candidates."""
    return shortcode_from_url(post.get("url")) is not None


def author_verified(rows):
    """(ok, info) — ok only when we have own rows and every own
    row's author is verified. info carries name/followers."""
    if not rows:
        return False, {}
    first = rows[0]
    info = {"author_name": first.get("author_name"),
            "followers": first.get("follower_count")}
    ok = all(p.get("verified") is True for p in rows)
    return ok, info


# ── embed-page media extraction ───────────────────────────────────
_SCONTENT_RE = re.compile(r"https?://[^\"'\\<>\s]+?\.jpg[^\"'\\<>\s]*")
_SIZE_RE = re.compile(r"[?&]stp=dst-jpg_e35_s(\d+)x(\d+)")
_SIZE_PATH_RE = re.compile(r"/s(\d+)x(\d+)/")
_STEM_RE = re.compile(r"/([A-Za-z0-9._-]+?)_n\.jpg")


def _url_size(url):
    # Rendition sizes live in the stp parameter in several shapes:
    # dst-jpg_e35_s640x640, dst-jpg_e35_p1080x1080 (portrait box),
    # and crop-prefixed c0.512.3072.3072a_dst-jpg_e35_s1080x1080.
    # Scan the whole stp value for [sp]<w>x<h> tokens and take the
    # largest; fall back to a /s<w>x<h>/ path segment.
    m = re.search(r"[?&]stp=([^&]+)", url)
    if m:
        sizes = re.findall(r"[sp](\d{3,4})x(\d{3,4})", m.group(1))
        if sizes:
            return max(((int(w), int(h)) for w, h in sizes),
                       key=lambda s: s[0] * s[1])
    m = _SIZE_PATH_RE.search(url)
    if m:
        return int(m.group(1)), int(m.group(2))
    return (0, 0)


def extract_scontent_photos(page_html):
    """Group every scontent .jpg URL in an embed page by media
    filename stem (the part before '_n.jpg') and pick the largest
    s<w>x<h> variant per photo. Returns an ordered list of
    {"stem", "url", "width", "height"} — order = first appearance
    of the stem in the page (the carousel order)."""
    text = html_mod.unescape(page_html or "")
    # The embed page embeds its media JSON with JSON escapes — the
    # full-size variants only become matchable URLs after unescaping
    # them too (verified 2026-11-08: without this, the picker saw
    # only the small srcset renditions and every frame failed the
    # resolution floor).
    text = (text.replace("\\u0026", "&").replace("\\u002F", "/")
            .replace("\\/", "/"))
    best = {}
    order = []
    for m in _SCONTENT_RE.finditer(text):
        url = m.group(0)
        if "scontent" not in url:
            continue
        # Post media lives under t51.82787-15; the author's profile
        # picture (t51.82787-19) is also an scontent .jpg in the page
        # and must never become a "frame".
        if "t51.82787-15" not in url:
            continue
        sm = _STEM_RE.search(url)
        if not sm:
            continue
        stem = sm.group(1)
        w, h = _url_size(url)
        if stem not in best:
            best[stem] = {"stem": stem, "url": url,
                          "width": w, "height": h}
            order.append(stem)
        else:
            cur = best[stem]
            if (w * h, max(w, h)) > (cur["width"] * cur["height"],
                                     max(cur["width"], cur["height"])):
                best[stem] = {"stem": stem, "url": url,
                              "width": w, "height": h}
    return [best[s] for s in order]


def curl_text(url, timeout=60):
    r = subprocess.run(
        ["curl", "-sSL", "-A", BROWSER_UA, "--max-time", str(timeout),
         url], capture_output=True, text=True, timeout=timeout + 30)
    if r.returncode != 0:
        raise RuntimeError(f"curl failed for {url}: {r.stderr[:200]}")
    return r.stdout


def curl_download(url, dest, timeout=120):
    r = subprocess.run(
        ["curl", "-sSL", "-A", BROWSER_UA, "--max-time", str(timeout),
         "-o", str(dest), url],
        capture_output=True, text=True, timeout=timeout + 30)
    if r.returncode != 0 or not Path(dest).exists() \
            or Path(dest).stat().st_size < 5000:
        raise RuntimeError(f"download failed for {url}: "
                           f"{r.stderr[:160]}")


def shortcode_from_url(url):
    m = re.search(r"instagram\.com/(?:p|reel)/([^/?#]+)", url or "")
    return m.group(1) if m else None


def download_frames(post):
    """Fetch the post's embed page and download its photos.
    Returns (frames, note): frames is a list of PIL Images (RGB)
    that clear the size floor; note explains an empty result.
    There is deliberately NO fallback source."""
    shortcode = shortcode_from_url(post.get("url"))
    if not shortcode:
        return [], f"no shortcode in post url {post.get('url')!r}"
    page = curl_text(
        f"https://www.instagram.com/p/{shortcode}/embed/captioned/")
    photos = extract_scontent_photos(page)
    if not photos:
        return [], (f"embed page for {shortcode} returned "
                    f"{len(page)} bytes with 0 scontent photo URLs "
                    f"(Instagram served no media — likely a "
                    f"logged-out/challenge page from this box)")
    tmp = OUT_ROOT / ".download-tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    frames, dropped = [], []
    for i, ph in enumerate(photos):
        dest = tmp / f"{shortcode}-{i}.jpg"
        try:
            curl_download(ph["url"], dest)
            img = Image.open(dest)
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img).convert("RGB")
            img.load()
        except Exception as e:
            dropped.append(f"{ph['stem']}: {e}")
            continue
        long_side = max(img.size)
        if long_side < MIN_LONG_SIDE:
            dropped.append(f"{ph['stem']}: {img.size[0]}x{img.size[1]} "
                           f"below {MIN_LONG_SIDE}px floor")
            continue
        frames.append(img)
    note = "; ".join(dropped)
    return frames, note


# ── text composition (no invented facts — caption-derived only) ──
_EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF☀-➿️‍]+")
_HASHTAG_RE = re.compile(r"#\w+")


def clean_text(text):
    t = _EMOJI_RE.sub("", text or "")
    t = t.replace(" ", " ")
    return re.sub(r"\s+", " ", t).strip()


def caption_first_line(caption):
    for line in (caption or "").splitlines():
        line = clean_text(_HASHTAG_RE.sub("", line))
        if len(line) >= 8:
            return line
    return ""


def caption_excerpt(caption, limit=200):
    para = ""
    for chunk in re.split(r"\n\s*\n", caption or ""):
        para = clean_text(_HASHTAG_RE.sub("", chunk))
        if para:
            break
    if len(para) > limit:
        para = para[:limit].rsplit(" ", 1)[0] + "…"
    return para


def derive_headline(name, caption):
    """A short factual headline from the caption's own first line —
    the celebrity's words, never an invented claim. Falls back to a
    plain factual label when the caption carries no usable line."""
    line = caption_first_line(caption)
    if line:
        if len(line) > 110:
            line = line[:110].rsplit(" ", 1)[0] + "…"
        return line
    return f"{name} shares a new post"


def hashtags_for(name, caption):
    tags = ["#" + re.sub(r"[^A-Za-z0-9]", "", name), "#TheVideshi"]
    low = (caption or "").lower()
    for key, tag in TOPIC_TAGS:
        if key in low and tag not in tags:
            tags.append(tag)
        if len(tags) >= 4:
            break
    return tags[:4]


def compose_caption(name, handle, caption, post_url, channel):
    """Queue caption: factual line + mandatory handle credit +
    hashtags (max 4). Facebook additionally carries the original
    post URL in the text."""
    excerpt = caption_excerpt(caption)
    factual = f"{name}: {excerpt}" if excerpt \
        else f"New update from {name} (@{handle})"
    credit = f"📸 @{handle} on Instagram"
    parts = [factual, credit]
    if channel == "facebook":
        parts.append(f"Original post: {post_url}")
    parts.append(" ".join(hashtags_for(name, caption)))
    text = "\n\n".join(parts)
    limit = THREADS_TEXT_LIMIT if channel == "threads" else FB_TEXT_LIMIT
    if len(text) > limit:
        room = limit - (len(text) - len(factual))
        factual = factual[:max(40, room - 1)].rsplit(" ", 1)[0] + "…"
        parts[0] = factual
        text = "\n\n".join(parts)
    return text


# ── rendering (Cards v1 via social_card helpers) ──────────────────
def kicker_for_name(name):
    return clean_text(name).upper()


def render_hook(img, headline, kicker):
    track, _scale, _note = sc.choose_track(*img.size)
    if track == "full-bleed":
        card, _info = sc.render_full_bleed(img, headline, kicker)
        return card, "full-bleed"
    card, _info = sc.render_backdrop(img, headline, kicker)
    return card, "backdrop"


def render_middle_photo(img, pos, total):
    """A plain photo slide: cover-crop to the 4:5 canvas, small
    brand chip, discreet position marker."""
    fx, fy, _m = sc.focal_anchor(img)
    card, _scale = sc.cover_crop(img, fx, fy)
    sc.brand_chip(card, 48, 44)
    sc._position_marker(ImageDraw.Draw(card), pos, total)
    return card


def render_credit_closer(name, handle, caption, post_url, pos, total):
    """Navy closer: handle credit, caption excerpt, original URL."""
    card = Image.new("RGB", (sc.W, sc.H), sc.NAVY)
    sc.brand_mark_v(card)
    d = ImageDraw.Draw(card)
    y = 300
    sc.draw_tracked(d, (sc.M, y), "PHOTO CREDIT",
                    sc.inter(sc.KICKER_SIZE, "700"),
                    sc.KICKER_TRACKING, sc.GOLD)
    y += sc.KICKER_TO_RULE
    d.rectangle((sc.M, y, sc.M + sc.RULE_W, y + sc.RULE_H), fill=sc.GOLD)
    y += sc.RULE_TO_HEADLINE + 10
    font, lines, size, _tr = sc.fit_headline(
        d, f"@{handle}", sc.CW, max_lines=2, start=64, floor=44)
    for ln in lines:
        d.text((sc.M, y), ln, font=font, fill=sc.WHITE)
        y += int(size * sc.LINE_RATIO)
    excerpt = caption_excerpt(caption, limit=280)
    if excerpt:
        y += 26
        ef = sc.inter(30, "400")
        for ln in sc.wrap(d, excerpt, ef, sc.CW):
            d.text((sc.M, y), ln, font=ef, fill=(214, 219, 228))
            y += 42
    y += 34
    uf = sc.inter(27, "600")
    for ln in sc.wrap(d, post_url, uf, sc.CW):
        d.text((sc.M, y), ln, font=uf, fill=sc.GOLD)
        y += 38
    sc._position_marker(ImageDraw.Draw(card), pos, total)
    return card


def render_deck(celeb, post, frames):
    """Render the full slide set for one post into
    .state/celeb-cards/<handle>-<post_id>/. Returns
    (card_files, card_texts, card_track)."""
    handle, name = celeb["handle"], celeb["name"]
    post_id = str(post.get("post_id"))
    out_dir = OUT_ROOT / f"{handle}-{post_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    headline = derive_headline(name, post.get("post_caption"))
    kicker = kicker_for_name(name)
    total = len(frames) + 1
    card_files, card_texts = [], []

    hook, track = render_hook(frames[0], headline, kicker)
    p = out_dir / "card-1.png"
    hook.save(p)
    card_files.append(str(p))
    card_texts.append(headline)

    for i, img in enumerate(frames[1:], start=2):
        card = render_middle_photo(img, i, total)
        p = out_dir / f"card-{i}.png"
        card.save(p)
        card_files.append(str(p))
        card_texts.append(
            f"Photo {i - 1} from @{handle}'s Instagram post")

    closer = render_credit_closer(name, handle,
                                  post.get("post_caption"),
                                  post.get("url"), total, total)
    p = out_dir / f"card-{total}.png"
    closer.save(p)
    card_files.append(str(p))
    card_texts.append(f"📸 @{handle} on Instagram — {post.get('url')}")
    return card_files, card_texts, track


# ── provenance ────────────────────────────────────────────────────
def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def append_provenance(celeb, post, card_files):
    """One JSONL record per staged photo set, in the image
    ledger's style (append with flock, same file the ledger uses)."""
    record = {
        "source": "celeb_own_post",
        "celeb": celeb["name"],
        "handle": celeb["handle"],
        "post_id": str(post.get("post_id")),
        "post_url": post.get("url"),
        "slug": f"celeb-{celeb['handle']}-{post.get('post_id')}",
        "files": [{"path": p, "sha256": file_sha256(p)}
                  for p in card_files],
        "staged_at": datetime.now(timezone.utc).isoformat(),
        "staged_by": SOURCE_TAG,
    }
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False)
    import fcntl
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(line + "\n")
        fcntl.flock(f, fcntl.LOCK_UN)
    return record


# ── staging ───────────────────────────────────────────────────────
def queue_entries(celeb, post, card_files, card_texts, card_track):
    handle, name = celeb["handle"], celeb["name"]
    post_id = str(post.get("post_id"))
    slug = f"celeb-{handle}-{post_id}"
    headline = derive_headline(name, post.get("post_caption"))
    caption = post.get("post_caption")
    post_url = post.get("url")
    base = {"kind": "article_post", "slug": slug, "headline": headline,
            "image_url": None, "card_file": card_files[0],
            "card_files": card_files, "card_texts": card_texts,
            "card_track": card_track, "media_file": None,
            "cover_file": None, "alt_text": headline,
            "source": SOURCE_TAG}
    entries = []
    fb = dict(base, channel="facebook",
              text=compose_caption(name, handle, caption, post_url,
                                   "facebook"),
              link=post_url)
    entries.append(fb)
    th = dict(base, channel="threads",
              text=compose_caption(name, handle, caption, post_url,
                                   "threads"),
              link=post_url, with_link=True)
    entries.append(th)
    # Instagram: the flush's proven IG article shape is a single
    # card (publish_ig_article posts card_file only — IG stays
    # single-card per social_queue's field contract), so the IG
    # entry mirrors the deck entry with the hook card as card_file.
    ig = dict(base, channel="instagram",
              text=compose_caption(name, handle, caption, post_url,
                                   "instagram"),
              link=None)
    entries.append(ig)
    return entries


def stage_post(celeb, post, dry_run, report):
    """Full path for one photo post: ad filter -> download ->
    render -> stage FB+Threads+IG -> provenance. Returns one of
    'staged' / 'ad-skip' / 'no-frames' / 'dry-run'."""
    handle = celeb["handle"]
    post_id = str(post.get("post_id"))
    marker = ad_marker_in(post.get("post_caption"))
    if marker:
        report["skipped_ads"].append(
            f"{handle}/{post_id}: ad marker {marker!r}")
        return "ad-skip"
    frames, note = download_frames(post)
    if note:
        report.setdefault("notes", []).append(f"{handle}/{post_id}: {note}")
    if not frames:
        report["no_frames"].append(f"{handle}/{post_id}")
        return "no-frames"
    if dry_run:
        report["would_stage"].append(f"{handle}/{post_id} "
                                     f"({len(frames)} photos)")
        return "dry-run"
    card_files, card_texts, track = render_deck(celeb, post, frames)
    staged_ids = []
    for entry in queue_entries(celeb, post, card_files, card_texts,
                               track):
        if social_queue.add_entry(entry):
            staged_ids.append(f"{entry['channel']}:{entry['id']}")
    append_provenance(celeb, post, card_files)
    report["staged"].append(
        f"{handle}/{post_id}: {len(card_files)} slides "
        f"({track}) -> {', '.join(staged_ids) or 'already queued'}")
    return "staged"


# ── YouTube Short (production reel chain, caption as ground truth) ──
# The celeb reel is NOT a fork: the spec is built in the exact
# reel_produce.py shape, the gates are reel_factcheck.run_gate and
# reel_frame_qa.run_qa called the way reel_produce.main calls them,
# the render goes through reel_produce.render (Reels v7), and the
# upload goes through reel_publish.publish(..., unlisted=True).
# Differences from an article reel, all forced by the source:
#   * ground truth = the post's own caption (+ a source line
#     naming the author/handle/URL — the post's own metadata);
#   * images = the post's own downloaded frames only (no
#     supplementary sourcing ladder — outside pictures have no
#     place in a celeb-update reel);
#   * the article "category" carries the celeb's name, because in
#     the v7 hook scene the category slot IS the kicker pill —
#     the carousel puts the celeb's name in that slot too;
#   * the payoff (the v7 navy closer) carries the photo credit +
#     the original post URL, mirroring the deck's closer card.
REEL_RUNS_DIR = HERE / "reel-runs"
MUSIC_DIR = HERE / "music"
REEL_STAGE = "navy"            # celeb reels use the navy stage
BANNED_MUSIC = {"anthemic-triumph-eternal-hope.mp3"}
# Full-length beds only (the -15s/-30s/-20s cuts are for other
# formats); news beds are wrong for a celeb update by genre.
_MUSIC_VARIANT_RE = re.compile(r"-(15|20|30)s\.mp3$")
_MUSIC_EXCLUDE_PREFIXES = ("breaking-", "pixabay-breaking",
                           "tech-corporate", "dramatic-")
# Festive/topic anchors for the stat grid: keyword -> on-screen
# big text. Only anchors literally present in the caption are
# used; labels are the caption's own sentences.
REEL_ANCHORS = [("homam", "HOMAM"), ("diwali", "DIWALI"),
                ("japan", "JAPAN"), ("birthday", "BIRTHDAY"),
                ("wedding", "WEDDING"), ("holi", "HOLI"),
                ("christmas", "CHRISTMAS"), ("new year", "NEW YEAR"),
                ("pongal", "PONGAL"), ("onam", "ONAM"),
                ("eid", "EID"), ("anniversary", "ANNIVERSARY")]


def caption_sentences(caption):
    """The caption as a list of cleaned sentences (emoji and
    hashtags stripped, the celeb's own words otherwise intact).
    Lines are split FIRST: Instagram captions carry no sentence
    punctuation between their lines, and collapsing the whole
    caption to one blob sentence starves every downstream
    derivation (sub, bullets, labels) into invented fallbacks —
    the first sample's fact-check hold was exactly that."""
    out = []
    for line in (caption or "").splitlines():
        text = clean_text(_HASHTAG_RE.sub("", line))
        for part in re.split(r"(?<=[.!?])\s+", text):
            part = part.strip()
            if len(part) >= 8:
                out.append(part)
    return out


def _anchor_label(sentences, key):
    """A short label for one stat-grid anchor: the word window
    around the anchor's first occurrence in the caption (the
    celeb's own words, never a paraphrase)."""
    for s in sentences:
        words = s.split()
        for i, w in enumerate(words):
            if key in w.lower().strip("(),.!?"):
                lo = max(0, i - 4)
                window = " ".join(words[lo:i + 5])
                window = window.strip(" ,;()")
                return _trim(window, 90)
    return ""


def _trim(text, limit):
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",;:—-") + "…"


def reel_slug(celeb, post):
    return f"celeb-{celeb['handle']}-{post.get('post_id')}"


def build_reel_article(celeb, post):
    """The reel_factcheck 'article' for a celeb post: headline +
    subheadline derived from the caption, body = the caption
    verbatim plus the source line (the post's own metadata:
    author name, handle, URL). Nothing else is asserted."""
    name, handle = celeb["name"], celeb["handle"]
    caption = post.get("post_caption")
    body = (caption or "").strip()
    source_line = (f"Source: {name} (@{handle}) on Instagram — "
                   f"{post.get('url')}")
    if body:
        body = body + "\n\n" + source_line
    else:
        body = source_line
    return {
        "id": None,
        "slug": reel_slug(celeb, post),
        "headline": derive_headline(name, caption),
        "subheadline": caption_excerpt(caption, limit=160),
        # v7 renders the category as the hook scene's kicker pill;
        # for a celeb reel the kicker is the celeb's name (the
        # same choice the carousel deck makes).
        "category": name.lower().replace(" ", "-"),
        "body": body,
        "image_url": post.get("url"),
        "tags": [],
        "sources": [{"name": f"@{handle} on Instagram",
                     "url": post.get("url")}],
    }


def _reel_anchors(caption):
    low = (caption or "").lower()
    found = []
    for key, big in REEL_ANCHORS:
        if key in low and big not in [b for _k, b in found]:
            found.append((key, big))
    return found


def build_reel_script(celeb, post):
    """The reel_produce-shaped script for a celeb post. Every
    on-screen string is built ONLY from the post's caption (plus
    the fixed credit template on the closer)."""
    name, handle = celeb["name"], celeb["handle"]
    caption = post.get("post_caption")
    sentences = caption_sentences(caption)
    first = caption_first_line(caption) \
        or f"{name} shares a new post"
    summary = _trim(" ".join(sentences), 260) if sentences else first
    anchors = _reel_anchors(caption)

    # Hero stat scene: the caption's signature term if it has one
    # (a parenthesised ritual/festival term), else its first
    # anchor, else the update itself.
    paren = re.search(r"([A-Za-z]+)\s*\(([^)]+)\)", caption or "")
    if paren:
        big = f"{paren.group(1).upper()} ({paren.group(2).upper()})"
    elif anchors:
        big = anchors[0][1]
    else:
        big = "NEW POST"
    # Sub: the caption's second sentence. NEVER an invented
    # fallback — a builder-written sentence ("X's latest update
    # on Instagram") is precisely what the fact-check gate held
    # on the first sample (ungrounded possessive entity). When
    # the caption is a single sentence, reuse its own words.
    sub = sentences[1] if len(sentences) > 1 else first
    hook_stat = {"eyebrow": "THE BIG PICTURE", "big": big,
                 "sub": _trim(sub, 130)}

    # Stat grid: up to two caption anchors (skipping any whose
    # key already rides in the hero stat's big text), labelled
    # with the caption's own word window around the anchor. At
    # least one entry is required by the grid measurer; the
    # fallback big is a template label, its text the caption's
    # own first line.
    stats = []
    for _key, abig in anchors:
        if abig == big or _key in big.lower():
            continue
        label = _anchor_label(sentences, _key)
        if not label:
            continue
        stats.append({"big": abig, "label": label})
        if len(stats) >= 2:
            break
    if not stats:
        stats = [{"big": "THE UPDATE",
                  "label": _trim(first, 90)}]

    bullets = [_trim(s, 140) for s in sentences[1:3]]
    if not bullets:
        bullets = [_trim(first, 140)]

    shortcode = shortcode_from_url(post.get("url")) or ""
    payoff = (f"Photos from @{handle}'s Instagram post: "
              f"https://www.instagram.com/p/{shortcode}/")
    entities = [name] + [abig.title() if abig.isupper() else abig
                         for _k, abig in anchors[:2]]
    return {
        "hook_line": _trim(first, 90),
        "hook_stat": hook_stat,
        "stats": stats,
        "diaspora_bullets": bullets,
        "key_entities": entities,
        "news_summary": summary,
        "payoff": payoff,
        "versus": "",
        "story_mood": "celebratory",
    }


def build_scene_plan(celeb, post, n_frames):
    """The intended scene composition (mirrors the v7 planner's
    assignment order): hook takes photo 0; the middle beats
    consume any further floor-passing photos in order, then fall
    back to text-on-stage; the payoff is always the navy credit
    closer. Photo indices in the plan are unique by construction.
    Returns [{beat, source, texts}] with source 'photo:<i>',
    'stage', or 'credit'."""
    script = build_reel_script(celeb, post)
    plan = [{"beat": "hook", "source": "photo:0",
             "texts": [celeb["name"], script["hook_line"]]}]
    photo_i = 1
    middle = [
        ("news", [script["news_summary"]]),
        ("hero", [script["hook_stat"]["big"],
                  script["hook_stat"]["sub"]]),
        ("grid", [f"{s['big']} — {s['label']}"
                  for s in script["stats"]]),
        ("diaspora", list(script["diaspora_bullets"])),
    ]
    for beat, texts in middle:
        if photo_i < n_frames:
            plan.append({"beat": beat, "source": f"photo:{photo_i}",
                         "texts": texts})
            photo_i += 1
        else:
            plan.append({"beat": beat, "source": "stage",
                         "texts": texts})
    plan.append({"beat": "payoff", "source": "credit",
                 "texts": [script["payoff"]]})
    return plan


def pick_music(caption, music_dir=MUSIC_DIR):
    """Pick a festive/entertainment bed from the production music
    pool. Topical first (a Diwali caption gets the Diwali bed),
    then celebration/inspiring beds. Never the banned track,
    never a news/tech bed. Returns a Path or None."""
    if not music_dir.exists():
        return None
    pool = []
    for p in sorted(music_dir.glob("*.mp3")):
        n = p.name.lower()
        if n in BANNED_MUSIC or _MUSIC_VARIANT_RE.search(n):
            continue
        if n.startswith(_MUSIC_EXCLUDE_PREFIXES):
            continue
        pool.append(p)
    low = (caption or "").lower()

    def first_with(*words):
        for p in pool:
            if all(w in p.name.lower() for w in words):
                return p
        return None

    if "diwali" in low:
        pick = first_with("diwali")
        if pick:
            return pick
    for words in [("indian-classical",), ("celebration",),
                  ("inspiring-uplifting",), ("indian",),
                  ("upbeat",)]:
        pick = first_with(*words)
        if pick:
            return pick
    return pool[0] if pool else None


def build_celeb_tiktok_caption(celeb, post):
    """TikTok caption in Kiran's copyable-text format: the update
    line, the 📸 credit with the post URL as plain text, then
    hashtags (max 4, the watcher's own hashtag set)."""
    name, handle = celeb["name"], celeb["handle"]
    headline = derive_headline(name, post.get("post_caption"))
    return "\n\n".join([
        headline,
        f"📸 @{handle} on Instagram — full post: {post.get('url')}",
        " ".join(hashtags_for(name, post.get("post_caption"))),
    ])


def _find_post(post_id):
    """Locate one post across the enabled handles (same verified
    detection path as run()). Returns (celeb, post) or
    (None, reason)."""
    for celeb in enabled_entries(load_whitelist()):
        handle = celeb["handle"]
        try:
            data = fetch_posts(handle, limit=5)
        except Exception:
            continue
        rows = own_posts(data, handle)
        ok, _info = author_verified(rows)
        if not rows or not ok:
            continue
        for post in rows:
            if is_feed_post(post) \
                    and str(post.get("post_id")) == str(post_id):
                return celeb, post
    return None, (f"post {post_id} not found in the latest 5 "
                  f"posts of any enabled handle")


def make_reel(post_id, log=print):
    """Build + gate + (on a full pass) upload UNLISTED a YouTube
    Short for one celeb post. Mirrors reel_produce.main's chain
    and verdict shape. Returns a result dict; a gate hold is a
    result, not an exception."""
    import reel_factcheck          # lazy: production import graph
    import reel_frame_qa
    import reel_produce
    import reel_publish
    reel_publish.load_env()
    reel_publish.load_env_file(
        Path.home() / "workspace" / ".env.openai")

    celeb, post = _find_post(post_id)
    if celeb is None:
        return {"status": "error", "detail": post}
    handle, name = celeb["handle"], celeb["name"]
    marker = ad_marker_in(post.get("post_caption"))
    if marker:
        return {"status": "ad-skip",
                "detail": f"ad marker {marker!r} — celeb reels "
                          f"follow the same genre rule as decks"}
    if (post.get("media_type") or "").lower() in VIDEO_MEDIA_TYPES:
        return {"status": "error",
                "detail": "post is a video/reel — the celeb Short "
                          "path is for photo updates"}

    frames, note = download_frames(post)
    if not frames:
        return {"status": "no-frames", "detail": note}
    slug = reel_slug(celeb, post)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    run_dir = REEL_RUNS_DIR / f"{today}-{slug}"
    outdir = run_dir / "output"
    outdir.mkdir(parents=True, exist_ok=True)

    frame_paths = []
    for i, img in enumerate(frames):
        p = outdir / f"frame-{i}.jpg"
        img.save(p, quality=95)
        frame_paths.append((p, img.size))
    hero_path, inline_paths = frame_paths[0][0], frame_paths[1:]

    article = build_reel_article(celeb, post)
    script = build_reel_script(celeb, post)
    (run_dir / "article.json").write_text(
        json.dumps(article, indent=2, ensure_ascii=False))
    script_path = run_dir / "script.json"
    script_path.write_text(
        json.dumps(script, indent=2, ensure_ascii=False))
    music = pick_music(post.get("post_caption"))
    if music is None:
        return {"status": "error",
                "detail": "no eligible music bed in the pool"}

    verdict = {"driver": "celeb_social_watch.py --make-reel",
               "status": "held", "stage": None,
               "render": {"renderer": "reel_renderer_v7.py",
                          "stage_color": REEL_STAGE},
               "article_slug": slug, "name": slug,
               "script": str(script_path),
               "celeb": {"name": name, "handle": handle,
                         "post_id": str(post_id),
                         "post_url": post.get("url")},
               "scene_plan": build_scene_plan(celeb, post,
                                              len(frames)),
               "music": str(music)}

    def finish():
        (outdir / "verdict.json").write_text(
            json.dumps(verdict, indent=2, ensure_ascii=False))
        return verdict

    # ── Gate 1: fact-check (ground truth = the caption) ──
    log("── gate 1/3: fact-check")
    fc = reel_factcheck.run_gate(script, article, use_llm=True)
    (outdir / "factcheck-report.json").write_text(
        json.dumps(fc, indent=2, ensure_ascii=False))
    verdict["factcheck"] = {
        "verdict": fc["verdict"], "held_claims": fc["held_claims"],
        "llm_cost_usd": fc["llm"]["cost_usd"]}
    if fc["verdict"] != "pass":
        verdict["stage"] = "factcheck"
        log(f"HELD at fact-check: {fc['held_claims']}")
        return finish()
    log("   all claims grounded in the caption")

    # ── Gate 2: render (Reels v7 via reel_produce.render) ──
    log("── gate 2/3: render (reel_renderer_v7, stage=navy)")
    import reel_renderer
    try:
        manifest = reel_produce.render(
            script, article, hero_path, inline_paths, {}, music,
            outdir, slug, REEL_STAGE, log=log)
    except reel_renderer.PhotoTooSmallError as e:
        verdict["stage"] = "render_photo_floor"
        verdict["detail"] = str(e)
        return finish()
    except (reel_renderer.TextFitError, RuntimeError,
            FileNotFoundError) as e:
        verdict["stage"] = "render"
        verdict["detail"] = str(e)[:500]
        return finish()
    verdict["manifest"] = str(outdir / "render-manifest.json")
    verdict["video"] = manifest["video"]
    verdict["scene_sources"] = {
        k: s["v7"]["image_source"]
        for k, s in manifest["scenes"].items()}

    # ── Gate 3: frame QA ──
    log("── gate 3/3: frame QA")
    try:
        qa = reel_frame_qa.run_qa(manifest["video"],
                                  outdir / "render-manifest.json",
                                  outdir / "qa")
    except Exception as e:
        verdict["stage"] = "frame_qa_error"
        verdict["detail"] = str(e)[:500]
        return finish()
    (outdir / "qa-report.json").write_text(
        json.dumps(qa, indent=2, ensure_ascii=False))
    verdict["qa"] = {"score": qa["qa_score"],
                     "passed": qa["qa_passed"],
                     "failing_checks": qa["failing_checks"]}
    if not qa["qa_passed"]:
        verdict["stage"] = "frame_qa"
        log(f"HELD at frame QA (score {qa['qa_score']}): "
            f"{qa['failing_checks']}")
        return finish()

    verdict["status"] = "ready"
    verdict["stage"] = "complete"
    finish()

    # TikTok pack beside the verdict (file artifact only).
    pack = outdir / "tiktok-caption.txt"
    pack.write_text(build_celeb_tiktok_caption(celeb, post) + "\n",
                    encoding="utf-8")
    verdict["tiktok_pack"] = str(pack)

    # ── Upload: UNLISTED only (sample protocol) ──
    log("── upload (UNLISTED via reel_publish.py)")
    try:
        result = reel_publish.publish(str(outdir / "verdict.json"),
                                      unlisted=True)
        verdict["publish"] = {"video_id": result["video_id"],
                              "url": result["shorts_url"],
                              "privacy": result["privacy"],
                              "live_title": result["live_title"]}
    except reel_publish.PublishRefused as e:
        verdict["publish"] = {"error": f"REFUSED: {e}"}
    except reel_publish.PublishFailed as e:
        verdict["publish"] = {"error": f"FAILED: {e}"}
        # reel_publish appends the publish log BEFORE the DB
        # write-back, so an upload that succeeded but failed
        # write-back is still recoverable from the log.
        try:
            for entry in reversed(reel_publish.load_publish_log()):
                if entry.get("article_slug") == slug:
                    verdict["publish"]["video_id"] = \
                        entry.get("video_id")
                    verdict["publish"]["url"] = (
                        "https://youtube.com/shorts/"
                        f"{entry.get('video_id')}")
                    break
        except Exception:
            pass
    (outdir / "verdict.json").write_text(
        json.dumps(verdict, indent=2, ensure_ascii=False))
    return verdict


# ── state ─────────────────────────────────────────────────────────
def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=1, ensure_ascii=False)
    os.replace(tmp, STATE_FILE)


# ── main run ──────────────────────────────────────────────────────
def run(dry_run=False, stage_post_id=None):
    whitelist = load_whitelist()
    celebs = enabled_entries(whitelist)
    state = load_state()
    report = {"handles": {}, "staged": [], "would_stage": [],
              "skipped_ads": [], "no_frames": [], "reel_candidates": [],
              "errors": [], "notes": []}
    target_found = False

    for celeb in celebs:
        handle = celeb["handle"]
        hrep = {"new": 0, "seeded": False}
        report["handles"][handle] = hrep
        try:
            data = fetch_posts(handle, limit=5)
        except Exception as e:
            report["errors"].append(f"{handle}: fetch failed: {e}")
            continue
        rows = own_posts(data, handle)
        ok, info = author_verified(rows)
        if not rows:
            report["errors"].append(
                f"{handle}: no own posts in response — skipped")
            continue
        if not ok:
            report["errors"].append(
                f"{handle}: author rows NOT verified — skipped "
                f"(guardrail: unverified handle)")
            continue
        hrep.update(info)
        hstate = state.setdefault(
            handle, {"seen_post_ids": [], "reel_candidates": []})
        hstate["author_name"] = info.get("author_name")
        hstate["followers"] = info.get("followers")
        seen = set(hstate.get("seen_post_ids") or [])
        first_run = not hstate.get("seeded_once")

        for post in rows:
            if not is_feed_post(post):
                continue
            post_id = str(post.get("post_id"))
            is_target = stage_post_id and post_id == str(stage_post_id)
            if is_target:
                target_found = True
            if post_id in seen and not is_target:
                continue
            if (post.get("media_type") or "").lower() \
                    in VIDEO_MEDIA_TYPES:
                cand = {"handle": handle, "post_id": post_id,
                        "url": post.get("url"),
                        "caption": caption_excerpt(
                            post.get("post_caption"), 160),
                        "date": (post.get("post_created_at") or {})
                        .get("user_local")}
                if post_id not in {c.get("post_id") for c in
                                   hstate["reel_candidates"]}:
                    hstate["reel_candidates"].append(cand)
                report["reel_candidates"].append(
                    f"{handle}/{post_id}: {post.get('url')}")
                seen.add(post_id)
                continue
            if first_run and not is_target:
                # Seed silently — never dump a backlog into the queue.
                seen.add(post_id)
                hrep["seeded"] = True
                continue
            if post_id not in seen:
                hrep["new"] += 1
            outcome = stage_post(celeb, post, dry_run, report)
            if outcome != "no-frames":
                # A no-frames skip (e.g. the embed page served no
                # media) stays unseen so a later run can retry it.
                seen.add(post_id)
        hstate["seen_post_ids"] = sorted(seen)
        hstate["seeded_once"] = True

    if stage_post_id and not target_found:
        report["errors"].append(
            f"--stage-post {stage_post_id}: post not found in the "
            f"latest 5 posts of any enabled handle")
    if not dry_run:
        save_state(state)
    return report


def print_report(report):
    print("=" * 64)
    print("CELEB SOCIAL WATCH — RUN REPORT")
    print("=" * 64)
    for handle, h in report["handles"].items():
        print(f"{handle}: new={h['new']} seeded={h['seeded']} "
              f"followers={h.get('followers')}")
    for label, key in [("STAGED", "staged"),
                       ("WOULD STAGE (dry-run)", "would_stage"),
                       ("SKIPPED (ad/collab)", "skipped_ads"),
                       ("SKIPPED (no usable frames)", "no_frames"),
                       ("REEL CANDIDATES (not downloaded)",
                        "reel_candidates"),
                       ("NOTES", "notes"), ("ERRORS", "errors")]:
        if report[key]:
            print(f"\n{label}:")
            for line in report[key]:
                print(f"  - {line}")
    print("\nDone.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="detect + report, stage nothing")
    ap.add_argument("--stage-post", metavar="POST_ID",
                    help="stage one specific post even if seen")
    ap.add_argument("--make-reel", metavar="POST_ID",
                    help="build a YouTube Short for one celeb post "
                         "through the production reel gates and, on "
                         "a full pass, upload it UNLISTED")
    args = ap.parse_args(argv)
    if args.make_reel:
        result = make_reel(args.make_reel)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("status") in ("ready",) else 1
    report = run(dry_run=args.dry_run, stage_post_id=args.stage_post)
    print_report(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
