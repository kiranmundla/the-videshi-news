#!/usr/bin/env python3
"""
wc_social_images.py — Source World Cup images from Instagram & Threads.

Modes:
  --refresh --posts-file FILE   Scrape CDN URLs from posts, download best, upload to Supabase
  --query "France vs Sweden"    Lookup from index
  --teams "France,Sweden"       Lookup by team
  --solidify                    Re-upload any CDN-only images to Supabase
  --stats                       Index summary
  --verify                      Check all Supabase URLs still work, flag broken

Image lifecycle: CDN URL → download → quality gate → compress → Supabase upload → permanent URL
"""
import os, sys, re, json, subprocess, hashlib, html as html_mod, time, struct
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
INDEX_PATH = SCRIPT_DIR / "wc-social-images-index.json"
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

GOOGLEBOT_UA = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

TRUSTED_ACCOUNTS = {
    "fifaworldcup", "fifa", "foxsports", "brfootball", "espn", "espnfc",
    "cbssportsgolazo", "usmnt", "england", "sabordefutbol",
    "tsn_official", "yahoosports", "daznfootball", "concacaf",
    "goal", "bleacherreport", "mls", "stuholden",
}

STORAGE_BUCKET = "article-images"
STORAGE_PREFIX = "wc-social"

# ── Quality gates ──

MIN_WIDTH = 600
MIN_HEIGHT = 400
MIN_BYTES = 15000
MAX_IMAGES_PER_POST = 4  # First 4 carousel slides max


def _get_image_dims(path):
    """Read JPEG/PNG dimensions."""
    for cmd in [["gm", "identify", "-format", "%w %h", path], ["identify", "-format", "%w %h", path]]:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                parts = r.stdout.strip().split()
                return int(parts[0]), int(parts[1])
        except (FileNotFoundError, ValueError, IndexError):
            continue
    # Fallback: JPEG header parse
    try:
        with open(path, "rb") as f:
            data = f.read(50000)
        i = 0
        while i < len(data) - 10:
            if data[i] == 0xFF and data[i + 1] in (0xC0, 0xC2):
                h = struct.unpack(">H", data[i + 5:i + 7])[0]
                w = struct.unpack(">H", data[i + 7:i + 9])[0]
                return w, h
            i += 1
    except:
        pass
    return 0, 0


def _compress_image(src, dst, max_dim=1600, quality=82):
    """Compress/resize image for storage efficiency."""
    # Try gm (GraphicsMagick) first, then ImageMagick convert
    for cmd in [["gm", "convert"], ["convert"]]:
        try:
            subprocess.run(
                cmd + [src, "-resize", f"{max_dim}x{max_dim}>",
                       "-quality", str(quality), "-strip", dst],
                capture_output=True, timeout=10
            )
            if os.path.exists(dst) and os.path.getsize(dst) > 1000:
                return True
        except FileNotFoundError:
            continue
    # Fallback: ffmpeg
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", src, "-vf", f"scale='min({max_dim},iw)':'min({max_dim},ih)':force_original_aspect_ratio=decrease",
             "-q:v", "3", dst],
            capture_output=True, timeout=10
        )
        return os.path.exists(dst) and os.path.getsize(dst) > 1000
    except:
        return False


def _passes_quality_gate(path):
    """Check if downloaded image meets quality bar."""
    size = os.path.getsize(path) if os.path.exists(path) else 0
    if size < MIN_BYTES:
        return False, "too_small"
    w, h = _get_image_dims(path)
    if w < MIN_WIDTH or h < MIN_HEIGHT:
        return False, f"low_res_{w}x{h}"
    # Check it's actually an image (not an HTML error page)
    with open(path, "rb") as f:
        header = f.read(4)
    if header[:2] == b'\xff\xd8':  # JPEG
        return True, "ok"
    if header[:4] == b'\x89PNG':  # PNG
        return True, "ok"
    return False, "not_image"


# ── Supabase upload ──

def _upload_to_supabase(local_path, dest_key):
    """Upload to Supabase storage. Returns public URL or None."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{dest_key}"
    r = subprocess.run(
        ["curl", "-sS", "-X", "POST", upload_url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: image/jpeg",
         "-H", "x-upsert: true",
         "--data-binary", f"@{local_path}",
         "-w", "\n%{http_code}"],
        capture_output=True, text=True, timeout=30
    )
    lines = r.stdout.strip().split("\n")
    status = lines[-1] if lines else "0"
    if status in ("200", "201"):
        return f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{dest_key}"
    # Parse error
    try:
        body = json.loads(lines[0]) if len(lines) > 1 else {}
        if "already exists" in str(body.get("error", body.get("message", ""))).lower():
            return f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{dest_key}"
    except:
        pass
    print(f"    Upload failed ({status}): {r.stdout[:200]}", file=sys.stderr)
    return None


def _verify_url(url):
    """HEAD check a Supabase URL. Returns True if 200."""
    r = subprocess.run(
        ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "-I", url],
        capture_output=True, text=True, timeout=10
    )
    return r.stdout.strip() == "200"


# ── CDN scraping ──

def _scrape_post_images(post_url, platform):
    """Scrape CDN image URLs from an Instagram or Threads post page."""
    try:
        r = subprocess.run(
            ["curl", "-sS", "-L", "-A", GOOGLEBOT_UA, post_url],
            capture_output=True, text=True, timeout=15
        )
        if r.returncode != 0 or len(r.stdout) < 1000:
            return []

        page = r.stdout

        og_desc = re.search(r'<meta property="og:description" content="([^"]*)"', page)
        caption = html_mod.unescape(og_desc.group(1)) if og_desc else ""
        og_title = re.search(r'<meta property="og:title" content="([^"]*)"', page)
        title_text = html_mod.unescape(og_title.group(1)) if og_title else ""

        cdn_raw = re.findall(
            r'(https?://(?:scontent[-\w.]*\.cdninstagram\.com|instagram\.\w+\.fbcdn\.net)/v/[^"\\]+\.(?:jpg|jpeg|png)[^"\\]*)',
            page
        )
        cdn_clean = list(dict.fromkeys(html_mod.unescape(u) for u in cdn_raw))
        # Skip tiny thumbnails
        good = [u for u in cdn_clean
                if "s150x150" not in u and "s320x320" not in u
                and "s64x64" not in u and "s100x100" not in u]

        seen_fnames = set()
        images = []
        for url in good[:MAX_IMAGES_PER_POST * 2]:  # extra margin for dedup
            fname = url.split("?")[0].split("/")[-1]
            if fname not in seen_fnames:
                seen_fnames.add(fname)
                images.append({
                    "cdn_url": url,
                    "post_url": post_url,
                    "platform": platform,
                    "caption": (caption or title_text)[:400],
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                })
            if len(images) >= MAX_IMAGES_PER_POST:
                break

        return images
    except Exception as e:
        print(f"  Scrape error {post_url}: {e}", file=sys.stderr)
        return []


# ── Index management ──

def load_index():
    if INDEX_PATH.exists():
        with open(INDEX_PATH) as f:
            return json.load(f)
    return {"version": 2, "last_refresh": None, "posts": {}, "images": []}


def save_index(index):
    index["version"] = 2
    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2)


def refresh_index(post_list, upload=True):
    """
    Scrape posts, download images, quality-gate, upload to Supabase.
    post_list: [{url, platform, account, likes}, ...]
    """
    index = load_index()
    new_count = 0
    uploaded_count = 0
    skipped_count = 0

    for post in post_list:
        url = post["url"]
        if url in index["posts"]:
            skipped_count += 1
            continue

        platform = post.get("platform", "instagram")
        account = post.get("account", "unknown")
        likes = post.get("likes", 0)

        print(f"  Scraping {platform} @{account}: {url}")
        imgs = _scrape_post_images(url, platform)

        index["posts"][url] = {
            "account": account, "platform": platform, "likes": likes,
            "image_count": len(imgs),
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

        for img in imgs:
            img["account"] = account
            img["likes"] = likes
            img["trusted"] = account.lower() in TRUSTED_ACCOUNTS

            if upload and SUPABASE_URL:
                # Download, quality-gate, compress, upload
                result = _download_and_upload(img)
                if result:
                    img["permanent_url"] = result["permanent_url"]
                    img["width"] = result["width"]
                    img["height"] = result["height"]
                    img["size_bytes"] = result["size_bytes"]
                    uploaded_count += 1
                else:
                    img["permanent_url"] = None

            index["images"].append(img)
            new_count += 1

        time.sleep(0.5)

    index["last_refresh"] = datetime.now(timezone.utc).isoformat()
    save_index(index)
    print(f"  Done: +{new_count} images ({uploaded_count} uploaded to Supabase, {skipped_count} posts skipped)")
    return index


def _download_and_upload(img):
    """Download CDN image → quality gate → compress → upload to Supabase."""
    cdn_url = img["cdn_url"]
    # Stable filename from CDN URL
    fname_hash = hashlib.md5(cdn_url.encode()).hexdigest()[:12]
    account = img.get("account", "unknown")
    platform = img.get("platform", "ig")
    plat_code = "ig" if platform == "instagram" else "th"

    tmp_raw = f"/tmp/wc_{fname_hash}_raw.jpg"
    tmp_comp = f"/tmp/wc_{fname_hash}.jpg"

    try:
        # Download
        r = subprocess.run(
            ["curl", "-sS", "-L", "-o", tmp_raw, "-w", "%{http_code}",
             "-A", BROWSER_UA, cdn_url],
            capture_output=True, text=True, timeout=15
        )
        if r.stdout.strip() != "200":
            return None

        # Quality gate
        ok, reason = _passes_quality_gate(tmp_raw)
        if not ok:
            _cleanup(tmp_raw, tmp_comp)
            return None

        w, h = _get_image_dims(tmp_raw)

        # Compress
        if not _compress_image(tmp_raw, tmp_comp):
            # Use raw if compress fails
            tmp_comp = tmp_raw

        size = os.path.getsize(tmp_comp)

        # Upload to Supabase
        dest_key = f"{STORAGE_PREFIX}/{plat_code}-{account}-{fname_hash}.jpg"
        perm_url = _upload_to_supabase(tmp_comp, dest_key)

        _cleanup(tmp_raw, tmp_comp)

        if perm_url:
            return {"permanent_url": perm_url, "width": w, "height": h, "size_bytes": size}
        return None

    except Exception as e:
        print(f"    Download/upload error: {e}", file=sys.stderr)
        _cleanup(tmp_raw, tmp_comp)
        return None


def _cleanup(*paths):
    for p in paths:
        try:
            os.unlink(p)
        except:
            pass


# ── Solidify: re-upload any CDN-only images ──

def solidify_index():
    """Find images without permanent_url and upload them."""
    index = load_index()
    count = 0
    for img in index["images"]:
        if img.get("permanent_url"):
            continue
        result = _download_and_upload(img)
        if result:
            img["permanent_url"] = result["permanent_url"]
            img["width"] = result["width"]
            img["height"] = result["height"]
            img["size_bytes"] = result["size_bytes"]
            count += 1
            print(f"  ✅ Uploaded @{img.get('account','?')}: {result['permanent_url'][:80]}")
        else:
            print(f"  ❌ Failed @{img.get('account','?')}: {img['cdn_url'][:60]}")
        time.sleep(0.3)
    save_index(index)
    print(f"  Solidified {count} images")


# ── Verify: check all permanent URLs still work ──

def verify_index():
    """Check all permanent URLs and flag broken ones."""
    index = load_index()
    broken = []
    ok_count = 0
    for img in index["images"]:
        purl = img.get("permanent_url")
        if not purl:
            continue
        if _verify_url(purl):
            ok_count += 1
        else:
            broken.append(img)
            print(f"  ❌ Broken: {purl[:80]} (@{img.get('account','?')})")
    print(f"  Verified: {ok_count} OK, {len(broken)} broken")
    return broken


# ── Lookup ──

def lookup_images(query, limit=5, require_permanent=True):
    """Find best matching images from the index."""
    index = load_index()
    if not index["images"]:
        return []

    query_words = set(re.findall(r'\w+', query.lower()))
    query_words -= {"the", "vs", "and", "in", "of", "a", "for", "world", "cup", "2026", "fifa", "match", "game"}

    scored = []
    for img in index["images"]:
        if require_permanent and not img.get("permanent_url"):
            continue

        cap_words = set(re.findall(r'\w+', img.get("caption", "").lower()))
        overlap = query_words & cap_words

        score = len(overlap) * 100
        if img.get("trusted"):
            score += 50
        score += min(img.get("likes", 0) / 1000, 50)

        # Bonus for having permanent URL
        if img.get("permanent_url"):
            score += 25

        # Bonus for high-res
        w = img.get("width", 0)
        if w >= 1000:
            score += 20
        elif w >= 600:
            score += 10

        if score > 0:
            scored.append((score, img))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Dedupe by post URL (one image per post max for variety)
    seen_posts = set()
    seen_fnames = set()
    results = []
    for score, img in scored:
        post = img.get("post_url", "")
        fname = img["cdn_url"].split("?")[0].split("/")[-1]
        if fname in seen_fnames:
            continue
        # Allow max 1 per post for variety in results
        if post in seen_posts and len(results) > 0:
            continue
        seen_posts.add(post)
        seen_fnames.add(fname)
        results.append(img)
        if len(results) >= limit:
            break

    return results


def get_image_for_article(query, prefer_landscape=True):
    """
    Get the single best image for a World Cup article.
    Returns dict with permanent_url, attribution, post_url, width, height
    or None.
    """
    images = lookup_images(query, limit=5, require_permanent=True)
    if not images:
        return None

    # If prefer_landscape, try to find one wider than tall
    if prefer_landscape:
        for img in images:
            w = img.get("width", 0)
            h = img.get("height", 0)
            if w > h:
                return _format_result(img)

    # Fall back to best match regardless
    return _format_result(images[0])


def _format_result(img):
    account = img.get("account", "unknown")
    platform = img.get("platform", "social")
    plat_label = "Instagram" if platform == "instagram" else "Threads" if platform == "threads" else platform.title()
    return {
        "image_url": img.get("permanent_url", img.get("cdn_url")),
        "attribution": f"@{account} / {plat_label}",
        "image_credit": f"@{account} / {plat_label}",
        "post_url": img.get("post_url", ""),
        "platform": platform,
        "account": account,
        "width": img.get("width", 0),
        "height": img.get("height", 0),
        "caption": img.get("caption", ""),
    }


# ── CLI ──

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--posts-file")
    parser.add_argument("--no-upload", action="store_true", help="Skip Supabase upload during refresh")
    parser.add_argument("--solidify", action="store_true", help="Upload any CDN-only images to Supabase")
    parser.add_argument("--verify", action="store_true", help="Check all permanent URLs still work")
    parser.add_argument("--query")
    parser.add_argument("--teams", help="Comma-separated")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--json-out", action="store_true", help="Output lookup as JSON")
    args = parser.parse_args()

    if args.stats:
        idx = load_index()
        total = len(idx.get("images", []))
        perm = sum(1 for i in idx.get("images", []) if i.get("permanent_url"))
        print(f"Last refresh: {idx.get('last_refresh', 'never')}")
        print(f"Posts indexed: {len(idx.get('posts', {}))}")
        print(f"Images: {total} total, {perm} with permanent Supabase URLs, {total-perm} CDN-only")
        accts = {}
        for img in idx.get("images", []):
            a = img.get("account", "?")
            accts[a] = accts.get(a, 0) + 1
        for a, c in sorted(accts.items(), key=lambda x: -x[1])[:15]:
            print(f"  @{a}: {c}")

    elif args.solidify:
        solidify_index()

    elif args.verify:
        verify_index()

    elif args.refresh:
        if args.posts_file and os.path.exists(args.posts_file):
            with open(args.posts_file) as f:
                posts = json.load(f)
        else:
            print("Provide --posts-file"); sys.exit(1)
        refresh_index(posts, upload=not args.no_upload)

    elif args.query or args.teams:
        q = args.query or ""
        if args.teams:
            q += " " + " ".join(args.teams.split(","))
        q = q.strip()
        images = lookup_images(q, limit=args.limit)
        if args.json_out:
            print(json.dumps([_format_result(i) for i in images], indent=2))
        else:
            for i, img in enumerate(images):
                perm = "✅" if img.get("permanent_url") else "⚠️ CDN"
                print(f"[{i+1}] {perm} @{img.get('account','?')} ({img.get('platform','?')})")
                url = img.get("permanent_url") or img.get("cdn_url", "")
                print(f"    URL: {url[:100]}")
                print(f"    Post: {img.get('post_url','')}")
                print(f"    {img.get('caption','')[:80]}")
                w, h = img.get("width", 0), img.get("height", 0)
                if w:
                    print(f"    Dims: {w}x{h}")
    else:
        parser.print_help()
