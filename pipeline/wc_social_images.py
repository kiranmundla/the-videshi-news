#!/usr/bin/env python3
"""
wc_social_images.py — Source World Cup images from Instagram & Threads.

Two modes:
1. REFRESH (--refresh): Accepts a JSON file of post URLs from social_media_search,
   scrapes CDN image URLs, builds a local index. Run via cron every few hours.
2. LOOKUP (--query / --teams): Find best matching images from the index
   for a given match or article. Used by writer scripts.

Usage:
    python3 wc_social_images.py --refresh --posts-file /tmp/wc_posts.json
    python3 wc_social_images.py --query "France vs Sweden"
    python3 wc_social_images.py --teams "France,Sweden" --download
    python3 wc_social_images.py --stats
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
        images = []

        og_desc = re.search(r'<meta property="og:description" content="([^"]*)"', page)
        caption = html_mod.unescape(og_desc.group(1)) if og_desc else ""
        og_title = re.search(r'<meta property="og:title" content="([^"]*)"', page)
        title_text = html_mod.unescape(og_title.group(1)) if og_title else ""

        cdn_raw = re.findall(
            r'(https?://(?:scontent[-\w.]*\.cdninstagram\.com|instagram\.\w+\.fbcdn\.net)/v/[^"\\]+\.(?:jpg|jpeg|png)[^"\\]*)',
            page
        )
        cdn_clean = list(dict.fromkeys(html_mod.unescape(u) for u in cdn_raw))
        good = [u for u in cdn_clean if "s150x150" not in u and "s320x320" not in u and "s64x64" not in u]

        seen_fnames = set()
        for url in good[:8]:
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

        return images
    except Exception as e:
        print(f"  Scrape error {post_url}: {e}", file=sys.stderr)
        return []


def _get_image_dims(path):
    try:
        with open(path, "rb") as f:
            data = f.read(50000)
        i = 0
        while i < len(data) - 10:
            if data[i] == 0xFF and data[i + 1] in (0xC0, 0xC2):
                h = struct.unpack(">H", data[i + 5 : i + 7])[0]
                w = struct.unpack(">H", data[i + 7 : i + 9])[0]
                return w, h
            i += 1
    except:
        pass
    return 0, 0


def load_index():
    if INDEX_PATH.exists():
        with open(INDEX_PATH) as f:
            return json.load(f)
    return {"last_refresh": None, "posts": {}, "images": []}


def save_index(index):
    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2)


def refresh_index(post_list):
    """post_list: list of {url, platform, account, likes}"""
    index = load_index()
    new_count = 0

    for post in post_list:
        url = post["url"]
        if url in index["posts"]:
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
            index["images"].append(img)
            new_count += 1

        time.sleep(0.5)

    index["last_refresh"] = datetime.now(timezone.utc).isoformat()
    save_index(index)
    print(f"  Index: +{new_count} new images, {len(index['images'])} total")
    return index


def lookup_images(query, limit=5):
    index = load_index()
    if not index["images"]:
        return []

    query_words = set(re.findall(r'\w+', query.lower()))
    query_words -= {"the", "vs", "and", "in", "of", "a", "for", "world", "cup", "2026", "fifa"}

    scored = []
    for img in index["images"]:
        cap_words = set(re.findall(r'\w+', img.get("caption", "").lower()))
        overlap = query_words & cap_words
        score = len(overlap) * 100
        if img.get("trusted"):
            score += 50
        score += min(img.get("likes", 0) / 1000, 50)
        if score > 0:
            scored.append((score, img))

    scored.sort(key=lambda x: x[0], reverse=True)

    seen = set()
    results = []
    for score, img in scored:
        fname = img["cdn_url"].split("?")[0].split("/")[-1]
        if fname not in seen:
            seen.add(fname)
            results.append(img)
    return results[:limit]


def download_best(query):
    images = lookup_images(query, limit=3)
    for img in images:
        hx = hashlib.md5(img["cdn_url"].encode()).hexdigest()[:8]
        tmp = f"/tmp/wc_social_{hx}.jpg"
        r = subprocess.run(
            ["curl", "-sS", "-L", "-o", tmp, "-w", "%{http_code}",
             "-A", BROWSER_UA, img["cdn_url"]],
            capture_output=True, text=True, timeout=15
        )
        if r.stdout.strip() != "200":
            continue
        w, h = _get_image_dims(tmp)
        size = os.path.getsize(tmp)
        if w < 400 or size < 5000:
            try: os.unlink(tmp)
            except: pass
            continue
        return {
            "local_path": tmp, "cdn_url": img["cdn_url"],
            "post_url": img.get("post_url", ""), "platform": img.get("platform"),
            "account": img.get("account", "unknown"),
            "attribution": f"@{img.get('account','unknown')} / {img.get('platform','social').title()}",
            "caption": img.get("caption", ""),
            "width": w, "height": h, "size_bytes": size,
        }
    return None


def upload_hero(article_slug, local_path):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    dest = f"heroes/{article_slug}-social.jpg"
    upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{dest}"
    r = subprocess.run(
        ["curl", "-sS", "-X", "POST", upload_url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: image/jpeg",
         "-H", "x-upsert: true",
         "--data-binary", f"@{local_path}"],
        capture_output=True, text=True, timeout=30
    )
    resp = json.loads(r.stdout) if r.stdout else {}
    if "error" in resp:
        return None
    return f"{SUPABASE_URL}/storage/v1/object/public/article-images/{dest}"


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--posts-file", help="JSON array of {url, platform, account, likes}")
    parser.add_argument("--query")
    parser.add_argument("--teams", help="Comma-separated")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()

    if args.stats:
        idx = load_index()
        print(f"Last refresh: {idx.get('last_refresh', 'never')}")
        print(f"Posts indexed: {len(idx.get('posts', {}))}")
        print(f"Images indexed: {len(idx.get('images', []))}")
        accts = {}
        for img in idx.get("images", []):
            a = img.get("account", "?")
            accts[a] = accts.get(a, 0) + 1
        for a, c in sorted(accts.items(), key=lambda x: -x[1]):
            print(f"  @{a}: {c} images")
    elif args.refresh:
        if args.posts_file and os.path.exists(args.posts_file):
            with open(args.posts_file) as f:
                posts = json.load(f)
        else:
            print("Provide --posts-file with JSON array"); sys.exit(1)
        refresh_index(posts)
    elif args.query or args.teams:
        q = args.query or ""
        if args.teams:
            q += " " + " ".join(args.teams.split(","))
        q = q.strip()
        if args.download:
            result = download_best(q)
            if result:
                print(f"✅ {result['local_path']} ({result['width']}x{result['height']})")
                print(f"   @{result['account']} / {result['platform']}")
                print(f"   {result['post_url']}")
            else:
                print("No downloadable images found")
        else:
            images = lookup_images(q, limit=args.limit)
            for i, img in enumerate(images):
                print(f"[{i+1}] @{img.get('account','?')} ({img.get('platform','?')})")
                print(f"    {img.get('post_url','')}")
                print(f"    {img.get('caption','')[:80]}")
    else:
        parser.print_help()
