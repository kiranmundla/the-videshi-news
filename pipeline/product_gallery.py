"""Product-gallery rung (Kiran, 2026-11-15).

For a story about a specific PRODUCT, the pictures readers want
are the maker's own: studio shots, lifestyle shots, the full
range of styles. Those live on the company's official
announcement/product pages — the same pages our writers already
cite as primary sources — and Kiran's 2026-10-11 rule puts
company press/product imagery in-bounds for media use.

Before this rung, nothing harvested them: the Gemini eyewear
article (2026-11-13) shipped with a hotlinked Android Police
hero, a one-word caption and zero inlines, while Google's own
announcement — already in the article's sources — carried a
dozen official product images. The frontend already renders a
scroll strip whenever `gallery_images` is populated
(ArticlePage → PhotoScrollStrip, hero first); the missing piece
was sourcing.

What this module does, when the picture pass hands it an
article:
  1. Find an OFFICIAL source in the article's own sources (host
     in image_sourcer's official-domain map — blog.google,
     apple.com, microsoft.com, samsung.com, …).
  2. Trigger only for visual stories or technology articles
     with no gallery yet.
  3. Extract the page's images (og:image + <img> src/srcset,
     largest variant, logos/icons skipped, size-variant dupes
     collapsed).
  4. Download and verify each (real image, ≥800px wide); need
     at least 3 verified to proceed — fewer is not a gallery.
  5. Re-host on our Supabase storage (never hotlink a company
     CDN into the strip), hero = the strongest landscape product
     shot, gallery = the rest (≤5).
  6. Hero replacement is conservative: only when the current
     hero is missing or a third-party hotlink (not our storage,
     not Wikimedia). A verified hero is never downgraded.
  7. Captions come from the page's own alt text (the maker's
     description of its own product), cleaned, plus the credit
     line "Official <Company> product image." Never the lede.

Fail-closed throughout: any doubt → return None, article
untouched.
"""
import html as html_mod
import json
import os
import re
import subprocess
import urllib.parse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MIN_W = 800
MAX_GALLERY = 5
MIN_GALLERY_TOTAL = 3  # hero + at least 2 more
_TRIGGER_CATEGORIES = {"technology"}

_SKIP_NAME = re.compile(
    r"logo|icon|sprite|avatar|favicon|badge|pixel|spacer|"
    r"1x1|blank|placeholder", re.I)
_SIZE_SUFFIX = re.compile(
    r"([._-](width|w|h|fill|size)[._-]?\d+|\.2e16d0ba|"
    r"-\d+x\d+|\.format-[a-z0-9]+)+$", re.I)


def _official_domain_names():
    """domain → display name, from image_sourcer's official map."""
    try:
        import image_sourcer
        return dict(getattr(image_sourcer,
                            "_OFFICIAL_DOMAIN_NAMES", {}) or {})
    except Exception:
        return {}


def official_source(article):
    """(url, company_display_name) of the first source hosted on
    an official company domain, else None."""
    names = _official_domain_names()
    if not names:
        return None
    for src in article.get("sources") or []:
        url = (src or {}).get("url") or ""
        host = urllib.parse.urlparse(url).netloc.lower()
        host = host[4:] if host.startswith("www.") else host
        for dom, disp in names.items():
            if host == dom or host.endswith("." + dom):
                return url, disp
    return None


def qualifies(article):
    """Trigger: no gallery yet, visual story or technology, and
    an official source to harvest."""
    if article.get("gallery_images"):
        return False
    if not (article.get("is_visual_story")
            or article.get("category") in _TRIGGER_CATEGORIES):
        return False
    return official_source(article) is not None


def _stem(url):
    """Collapse size/format variants of one image to a stem so
    srcset dupes dedupe (blog.google serves width-500…2200 of
    the same file)."""
    path = urllib.parse.urlparse(url).path
    base = path.rsplit("/", 1)[-1]
    base = re.sub(r"\.(jpg|jpeg|png|webp|gif)$", "", base, flags=re.I)
    prev = None
    while prev != base:
        prev = base
        base = _SIZE_SUFFIX.sub("", base)
    return base.lower()


def _largest_srcset(srcset):
    best, best_w = None, -1
    for part in (srcset or "").split(","):
        part = part.strip()
        if not part:
            continue
        bits = part.split()
        w = 0
        if len(bits) > 1 and bits[1].endswith("w"):
            try:
                w = int(bits[1][:-1])
            except ValueError:
                w = 0
        if w >= best_w:
            best, best_w = bits[0], w
    return best


def extract_candidates(page_html, page_url):
    """Ordered [{url, alt}] from og:image + <img> tags, largest
    srcset variant each, logos/icons skipped, variants deduped
    by stem."""
    out, seen = [], set()

    def add(url, alt=""):
        if not url or url.startswith("data:"):
            return
        url = urllib.parse.urljoin(page_url, url.strip())
        name = urllib.parse.urlparse(url).path.rsplit("/", 1)[-1]
        if _SKIP_NAME.search(name):
            return
        stem = _stem(url)
        if stem in seen:
            return
        seen.add(stem)
        out.append({"url": url, "alt": html_mod.unescape(alt or "")
                    .strip()})

    m = re.search(r'property="og:image"\s+content="([^"]+)"',
                  page_html or "")
    if m:
        add(m.group(1))
    for tag in re.findall(r"<img\b[^>]*>", page_html or ""):
        src = re.search(r'\bsrc="([^"]+)"', tag)
        srcset = re.search(r'\bsrcset="([^"]+)"', tag)
        alt = re.search(r'\balt="([^"]*)"', tag)
        url = None
        if srcset:
            url = _largest_srcset(srcset.group(1))
        if not url and src:
            url = src.group(1)
        if url:
            add(url, alt.group(1) if alt else "")
    return out


_ALT_BOILERPLATE = re.compile(
    r"\s+Along the (top|bottom|side)[^.]*\.\s*$", re.I)


def caption_for(alt, company):
    """Caption from the maker's own alt text, cleaned of layout
    boilerplate, with the credit line appended. No alt → the
    honest generic."""
    text = _ALT_BOILERPLATE.sub("", (alt or "").strip())
    text = re.sub(r"\s+", " ", text)
    if text:
        if not text.endswith((".", "!", "?")):
            text += "."
        return f"{text} Official {company} product image."
    return f"Official {company} product image."


def _curl(url, out_path=None, max_time=45):
    cmd = ["curl", "-sSL", "--max-time", str(max_time),
           "-A", "TheVideshi/1.0 (news; product gallery)"]
    if out_path:
        cmd += ["-o", out_path]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True,
                       timeout=max_time + 15)
    if r.returncode != 0:
        return None
    if out_path:
        return out_path
    return r.stdout


def _probe(path):
    try:
        from PIL import Image
        im = Image.open(path)
        im.verify()
        im = Image.open(path)
        return im.size, im.format
    except Exception:
        return (0, 0), None


def _upload(local_path, dest_name, supabase_url, service_key):
    host = supabase_url.replace("https://", "").rstrip("/")
    url = (f"https://{host}/storage/v1/object/article-images/"
           f"product-gallery/{dest_name}")
    r = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
         "-X", "POST", url,
         "-H", f"apikey: {service_key}",
         "-H", f"Authorization: Bearer {service_key}",
         "-H", "Content-Type: image/jpeg",
         "--data-binary", f"@{local_path}"],
        capture_output=True, text=True, timeout=90)
    if r.stdout.strip() != "200":
        return None
    return (f"{supabase_url}/storage/v1/object/public/"
            f"article-images/product-gallery/{dest_name}")


def _hero_is_replaceable(article):
    """Replace the hero only when it is missing or a third-party
    hotlink. Our storage and Wikimedia heroes are verified
    placements — never downgraded."""
    url = article.get("image_url") or ""
    if not url:
        return True
    host = urllib.parse.urlparse(url).netloc.lower()
    if "supabase.co" in host or "wikimedia.org" in host:
        return False
    return True


def apply_product_gallery(article, patch_fn, log=print,
                          workdir=None, allow_hero_replace=True):
    """Harvest the official gallery for one article. Returns a
    report dict, or None when the article does not qualify or
    the harvest fails closed."""
    if not qualifies(article):
        return None
    page_url, company = official_source(article)
    slug = article.get("slug") or "article"
    supabase_url = os.environ.get("SUPABASE_URL", "")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not supabase_url or not service_key:
        log("product-gallery: supabase env missing — skip")
        return None
    page_html = _curl(page_url)
    if not page_html:
        return None
    cands = extract_candidates(page_html, page_url)
    if len(cands) < MIN_GALLERY_TOTAL:
        return None
    workdir = workdir or os.path.join(
        SCRIPT_DIR, ".state", "product-gallery", slug)
    os.makedirs(workdir, exist_ok=True)
    verified = []
    for cand in cands[:10]:
        raw = os.path.join(workdir, f"c{len(verified)}.bin")
        if not _curl(cand["url"], out_path=raw):
            continue
        (w, h), _fmt = _probe(raw)
        if not w or w < MIN_W:
            continue
        jpg = os.path.join(workdir, f"c{len(verified)}.jpg")
        try:
            from PIL import Image
            Image.open(raw).convert("RGB").save(jpg, quality=88)
        except Exception:
            continue
        verified.append({**cand, "path": jpg, "w": w, "h": h})
        if len(verified) >= MAX_GALLERY + 1:
            break
    if len(verified) < MIN_GALLERY_TOTAL:
        log(f"product-gallery: {slug}: only {len(verified)} "
            "verified official images — no gallery")
        return None
    # Hero: strongest landscape (widest, ratio ≥ 1.3); else the
    # first verified image. Banner-named files are skipped while
    # an alternative exists — announcement banners are usually
    # labeled composites/collages, weaker heroes than a clean
    # product shot (the blog's og:image banner vs its studio
    # shots, 2026-11-15).
    hero = None
    for v in verified:
        if "banner" in _stem(v["url"]):
            continue
        if v["w"] >= 1200 and v["w"] / max(v["h"], 1) >= 1.3:
            hero = v
            break
    hero = hero or verified[0]
    uploaded = {}
    for i, v in enumerate(verified):
        name = f"{slug}/{i}-{_stem(v['url'])[:40]}.jpg"
        url = _upload(v["path"], name, supabase_url, service_key)
        if url:
            uploaded[id(v)] = url
    if id(hero) not in uploaded or len(uploaded) < MIN_GALLERY_TOTAL:
        return None
    gallery = [{"url": uploaded[id(v)],
                "caption": caption_for(v["alt"], company)}
               for v in verified
               if id(v) in uploaded and v is not hero]
    payload = {"gallery_images": gallery[:MAX_GALLERY],
               "is_visual_story": True}
    if allow_hero_replace and _hero_is_replaceable(article):
        payload["image_url"] = uploaded[id(hero)]
        payload["image_caption"] = caption_for(hero["alt"],
                                               company)
        payload["image_attribution"] = (
            f"{company} (official product images)")
    if patch_fn(article["id"], payload):
        return {"slug": slug, "company": company,
                "hero_replaced": "image_url" in payload,
                "gallery_count": len(payload["gallery_images"]),
                "source_page": page_url}
    return None
