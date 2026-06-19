#!/usr/bin/env python3
"""
media-library-source.py — fill the media_library with HIGH-QUALITY,
attribution-clean images AND videos for queued subjects.

Sources (in priority order):
  1. Wikimedia Commons  (PRIMARY) — images AND CC videos; captures author,
     license, source page. Highest trust.
  2. PIB photo index    — Indian officials/events; captions ready-made.
  3. Pexels (GENERIC tier ONLY) — subject_type forced to 'concept'; reserved for
     abstract reel b-roll (skylines, rupee notes). NEVER an article photo.

Quality gates (hard — Kiran's top requirement; see media_library_store.py):
  images  : longest side >= 1600px
  videos  : short side  >= 720px AND 4s <= duration <= 90s

Each kept asset is downloaded, uploaded to Supabase storage (so links never
rot), captioned + attributed, scored, and written to BOTH the JSON mirror and
(if present) the Supabase media_library table.

Idempotent + low-volume: caps total assets per run, skips already-covered
subjects, never touches last_used/times_used.

Run:
    python3 media-library-source.py                 # work the queue
    python3 media-library-source.py --subjects "Narendra Modi:person,Mumbai:place"
    python3 media-library-source.py --max 15 --videos
Flags:
    --max N        cap assets sourced this run (default 30)
    --per-subject N  max assets per subject (default 2)
    --videos       also attempt video sourcing (default images only; videos are
                   slower/heavier, enable on a separate cadence)
    --allow-pexels include the generic Pexels concept tier
    --subjects S   comma list of "subject:subject_type" overriding the queue
    --dry          source + gate but don't upload/persist (debug)
"""

import os, re, sys, json, time, argparse, tempfile, subprocess
import requests
import media_library_store as store

store.load_env("~/workspace/.env.pexels")
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

PIPELINE_DIR = store.PIPELINE_DIR
PIB_INDEX = os.path.join(PIPELINE_DIR, "pib-photo-index.json")
UA = store.UA


# ════════════════════════════════════════════════════════════════════════════
# WIKIMEDIA COMMONS
# ════════════════════════════════════════════════════════════════════════════
def commons_search(query, want_video=False, limit=8):
    """Search Commons; return raw candidates with full imageinfo+extmetadata."""
    gsrsearch = f"{query} filetype:video" if want_video else f"{query} filetype:bitmap"
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": gsrsearch, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata|mediatype|duration",
        "iiurlwidth": "2000",
        "format": "json",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            return []
        pages = r.json().get("query", {}).get("pages", {})
        out = []
        for _, p in pages.items():
            ii = (p.get("imageinfo") or [{}])[0]
            ii["_title"] = p.get("title", "")
            out.append(ii)
        return out
    except Exception as e:
        print(f"  ⚠ Commons search error: {e}")
        return []


def _commons_attr(ii):
    em = ii.get("extmetadata", {})
    def g(k):
        return store.strip_html(em.get(k, {}).get("value", "")) if em.get(k) else ""
    artist = g("Artist") or g("Credit") or "Wikimedia Commons"
    lic = g("LicenseShortName") or g("License") or "see source"
    desc = g("ImageDescription") or g("ObjectName")
    return artist, lic, desc


def _is_free_license(lic):
    if not lic:
        return False
    l = lic.lower()
    bad = ["non-free", "fair use", "all rights reserved", "copyright", "no known copyright"]
    if any(b in l for b in bad):
        return False
    ok = ["cc", "public domain", "pdm", "cc0", "godl", "government open data", "attribution"]
    return any(o in l for o in ok)


def source_commons_image(subject, candidates_needed, max_per):
    """Return list of asset dicts (gated, attributed) for images."""
    got = []
    cands = commons_search(subject, want_video=False, limit=10)
    for ii in cands:
        if len(got) >= max_per:
            break
        mime = ii.get("mime", "")
        if not mime.startswith("image/") or mime == "image/svg+xml":
            continue
        w, h = ii.get("width"), ii.get("height")
        if not store.image_passes(w, h):
            continue
        artist, lic, desc = _commons_attr(ii)
        if not _is_free_license(lic):
            continue
        # full-res original URL (best quality); fall back to a large thumb
        src = ii.get("url") or ii.get("thumburl")
        if not src:
            continue
        title = ii.get("_title", "").replace("File:", "").rsplit(".", 1)[0]
        caption = desc or title or subject
        got.append({
            "media_type": "image",
            "subject": subject,
            "_src": src,
            "_thumb_src": ii.get("thumburl"),
            "width": w, "height": h, "duration": None,
            "source": "wikimedia_commons",
            "caption": caption[:280],
            "attribution": f"Wikimedia Commons / {artist}, {lic}".strip(),
            "license": lic,
            "source_url": f"https://commons.wikimedia.org/wiki/{ii.get('_title','').replace(' ','_')}",
        })
    return got


def source_commons_video(subject, max_per):
    got = []
    cands = commons_search(subject, want_video=True, limit=10)
    for ii in cands:
        if len(got) >= max_per:
            break
        mime = ii.get("mime", "")
        if not mime.startswith("video/"):
            continue
        w, h = ii.get("width"), ii.get("height")
        dur = ii.get("duration")
        if not store.video_passes(w, h, dur):
            continue
        artist, lic, desc = _commons_attr(ii)
        if not _is_free_license(lic):
            continue
        src = ii.get("url")
        if not src:
            continue
        title = ii.get("_title", "").replace("File:", "").rsplit(".", 1)[0]
        got.append({
            "media_type": "video",
            "subject": subject,
            "_src": src,
            "_thumb_src": None,
            "width": w, "height": h, "duration": round(float(dur), 2),
            "source": "wikimedia_commons",
            "caption": (desc or title or subject)[:280],
            "attribution": f"Wikimedia Commons / {artist}, {lic}".strip(),
            "license": lic,
            "source_url": f"https://commons.wikimedia.org/wiki/{ii.get('_title','').replace(' ','_')}",
        })
    return got


# ════════════════════════════════════════════════════════════════════════════
# PIB (Indian officials/events) — captions ready-made
# ════════════════════════════════════════════════════════════════════════════
def source_pib(subject, max_per):
    """Match PIB photos by caption keyword. PIB gallery pages list photos under a
    GODL-India license. We can only store entries whose direct image URL we can
    resolve; the index stores gallery pages + captions, so we match by caption."""
    if not os.path.exists(PIB_INDEX):
        return []
    try:
        idx = json.load(open(PIB_INDEX))
    except Exception:
        return []
    photos = idx.get("photos", [])
    s = subject.lower()
    got = []
    for ph in photos:
        if len(got) >= max_per:
            break
        cap = (ph.get("caption") or "")
        if s not in cap.lower():
            continue
        # PIB index holds gallery_url, not a direct CDN image; we keep it as a
        # captioned, attributed reference. (Direct-image resolution from PIB
        # galleries is brittle; Commons is the primary high-res path.)
        # Only store if we have a resolvable direct image — skip otherwise so we
        # never store a non-image URL as media. Most PIB entries are gallery
        # pages, so this typically yields 0 unless a direct image is present.
        img = ph.get("image_url") or ph.get("img")
        if not img:
            continue
        got.append({
            "media_type": "image",
            "subject": subject,
            "_src": img,
            "_thumb_src": None,
            "width": ph.get("width"), "height": ph.get("height"), "duration": None,
            "source": "pib",
            "caption": cap[:280],
            "attribution": "Press Information Bureau (PIB), Government of India / GODL-India",
            "license": "GODL-India",
            "source_url": ph.get("gallery_url", ""),
        })
    return got


# ════════════════════════════════════════════════════════════════════════════
# PEXELS — GENERIC tier only (concept), reel b-roll, never article photos
# ════════════════════════════════════════════════════════════════════════════
def source_pexels_concept(subject, max_per, want_video=False):
    if not PEXELS_KEY:
        return []
    got = []
    try:
        if want_video:
            url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(subject)}&per_page=10&orientation=portrait"
        else:
            url = f"https://api.pexels.com/v1/search?query={requests.utils.quote(subject)}&per_page=10&orientation=portrait"
        r = subprocess.run(["curl", "-s", "-H", f"Authorization: {PEXELS_KEY}", url],
                           capture_output=True, text=True, timeout=30)
        data = json.loads(r.stdout or "{}")
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
        return []

    if want_video:
        for v in data.get("videos", []):
            if len(got) >= max_per:
                break
            dur = v.get("duration", 0)
            files = sorted(v.get("video_files", []),
                           key=lambda f: (f.get("width") or 0) * (f.get("height") or 0),
                           reverse=True)
            best = files[0] if files else None
            if not best:
                continue
            w, h = best.get("width"), best.get("height")
            if not store.video_passes(w, h, dur):
                continue
            got.append({
                "media_type": "video", "subject": subject,
                "_src": best.get("link"), "_thumb_src": v.get("image"),
                "width": w, "height": h, "duration": float(dur),
                "source": "pexels",
                "caption": f"{subject} (stock footage)",
                "attribution": f"Pexels / {v.get('user',{}).get('name','Pexels')}",
                "license": "Pexels License",
                "source_url": v.get("url", ""),
                "_force_concept": True,
            })
    else:
        for ph in data.get("photos", []):
            if len(got) >= max_per:
                break
            w, h = ph.get("width"), ph.get("height")
            if not store.image_passes(w, h):
                continue
            src = ph.get("src", {}).get("original")
            if not src:
                continue
            got.append({
                "media_type": "image", "subject": subject,
                "_src": src, "_thumb_src": ph.get("src", {}).get("large"),
                "width": w, "height": h, "duration": None,
                "source": "pexels",
                "caption": (ph.get("alt") or f"{subject} (stock photo)")[:280],
                "attribution": f"Pexels / {ph.get('photographer','Pexels')}",
                "license": "Pexels License",
                "source_url": ph.get("url", ""),
                "_force_concept": True,
            })
    return got


# ════════════════════════════════════════════════════════════════════════════
# PERSIST one candidate: download → (probe) → upload → write asset
# ════════════════════════════════════════════════════════════════════════════
def persist(cand, subject_type, tags, dry=False):
    mtype = cand["media_type"]
    src = cand["_src"]
    # concept override for generic stock
    st = "concept" if cand.get("_force_concept") else subject_type

    ext = "mp4" if mtype == "video" else "jpg"
    if mtype == "video" and src.lower().endswith(".webm"):
        ext = "webm"
    aid = store.make_id(st, cand["subject"], cand["source_url"] or src, mtype)
    remote = f"{store.STORAGE_PREFIX}/{st}/{store.slugify(cand['subject'])}-{aid[-6:]}.{ext}"

    if dry:
        print(f"    [dry] would keep {mtype} {cand['subject']} "
              f"{cand['width']}x{cand['height']} via {cand['source']}")
        return None

    with tempfile.TemporaryDirectory() as td:
        local = os.path.join(td, f"asset.{ext}")
        if not store.curl_download(src, local, timeout=150):
            return None

        thumb_url = None
        if mtype == "video":
            # verify real dimensions/duration from the file (don't trust API alone)
            w, h, dur = store.probe_video(local)
            if not store.video_passes(w, h, dur):
                print(f"    ✗ video failed gate after probe: {w}x{h} {dur}s")
                return None
            cand["width"], cand["height"], cand["duration"] = w, h, round(dur, 2)
            # poster frame
            poster = os.path.join(td, "poster.jpg")
            if store.make_video_poster(local, poster):
                thumb_url = store.upload_file(poster, remote.rsplit(".", 1)[0] + "-poster.jpg", "image/jpeg")
            content_type = "video/mp4" if ext == "mp4" else "video/webm"
        else:
            # verify real pixels from the file
            try:
                from PIL import Image
                with Image.open(local) as im:
                    w, h = im.size
                if not store.image_passes(w, h):
                    print(f"    ✗ image failed gate after open: {w}x{h}")
                    return None
                cand["width"], cand["height"] = w, h
            except Exception as e:
                print(f"    ✗ could not open image: {e}")
                return None
            content_type = "image/jpeg" if ext == "jpg" else f"image/{ext}"

        public_url = store.upload_file(local, remote, content_type)
        if not public_url:
            return None
        # thumb for images = the large/thumb source if present (re-host optional; keep simple)
        if mtype == "image" and not thumb_url:
            thumb_url = public_url

    qs = store.quality_score(mtype, cand["width"], cand["height"], cand["source"], cand.get("duration"))
    asset = {
        "id": aid,
        "media_type": mtype,
        "url": public_url,
        "thumb_url": thumb_url,
        "subject": cand["subject"],
        "subject_type": st,
        "caption": cand["caption"],
        "attribution": cand["attribution"],
        "license": cand["license"],
        "source_url": cand["source_url"],
        "tags": tags,
        "width": cand["width"],
        "height": cand["height"],
        "duration": cand.get("duration"),
        "quality_score": qs,
        "added_date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "last_used": None,
        "times_used": 0,
    }
    store.upsert_mirror(asset)
    store.upsert_table(asset)  # best-effort
    print(f"    ✓ kept {mtype} {st}/{cand['subject']} {cand['width']}x{cand['height']} "
          f"q={qs} via {cand['source']}")
    return asset


# ════════════════════════════════════════════════════════════════════════════
# DRIVER
# ════════════════════════════════════════════════════════════════════════════
def load_queue():
    if os.path.exists(store.QUEUE_PATH):
        try:
            return json.load(open(store.QUEUE_PATH))
        except Exception:
            pass
    return {"queue": []}


def save_queue(q):
    tmp = store.QUEUE_PATH + ".tmp"
    json.dump(q, open(tmp, "w"), indent=1, ensure_ascii=False)
    os.replace(tmp, store.QUEUE_PATH)


def source_subject(subject, subject_type, tags, per_subject, do_video, allow_pexels, dry):
    print(f"\n● {subject} ({subject_type})  tags={tags}")
    kept = []
    have = store.coverage_count(subject, "image")
    need_img = max(0, per_subject - have)

    # 1) Commons images (primary)
    if need_img:
        for c in source_commons_image(subject, need_img, need_img):
            a = persist(c, subject_type, tags, dry)
            if a:
                kept.append(a)
            time.sleep(0.4)

    # 2) PIB (Indian officials/events) — fills if Commons came up short
    if len(kept) < need_img:
        for c in source_pib(subject, need_img - len(kept)):
            a = persist(c, subject_type, tags, dry)
            if a:
                kept.append(a)
            time.sleep(0.3)

    # 3) Pexels concept tier (generic, opt-in)
    if allow_pexels and len(kept) < need_img:
        for c in source_pexels_concept(subject, need_img - len(kept), want_video=False):
            a = persist(c, subject_type, tags, dry)
            if a:
                kept.append(a)
            time.sleep(0.3)

    # videos (separate budget; Commons primary, Pexels concept opt-in)
    if do_video:
        have_v = store.coverage_count(subject, "video")
        need_v = max(0, 1 - have_v)  # 1 good video per subject is plenty
        if need_v:
            vids = source_commons_video(subject, need_v)
            if not vids and allow_pexels:
                vids = source_pexels_concept(subject, need_v, want_video=True)
            for c in vids:
                a = persist(c, subject_type, tags, dry)
                if a:
                    kept.append(a)
                time.sleep(0.5)
    return kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=30)
    ap.add_argument("--per-subject", type=int, default=2)
    ap.add_argument("--videos", action="store_true")
    ap.add_argument("--allow-pexels", action="store_true")
    ap.add_argument("--subjects", type=str, default="")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    # Build work list
    work = []  # (subject, subject_type, tags)
    if args.subjects:
        for tok in args.subjects.split(","):
            tok = tok.strip()
            if not tok:
                continue
            if ":" in tok:
                subj, st = tok.rsplit(":", 1)
            else:
                subj, st = tok, "thing"
            work.append((subj.strip(), st.strip(), [subj.strip().lower()]))
    else:
        q = load_queue()
        items = sorted(q.get("queue", []), key=lambda x: -(x.get("priority", 0)))
        for it in items:
            work.append((it["subject"], it.get("subject_type", "thing"), it.get("tags", [it["subject"].lower()])))

    if not work:
        print("Nothing to source (empty queue / no --subjects).")
        return

    total = 0
    sourced_subjects = set()
    for subject, st, tags in work:
        if total >= args.max:
            break
        kept = source_subject(subject, st, tags, args.per_subject,
                              args.videos, args.allow_pexels, args.dry)
        total += len(kept)
        if kept:
            sourced_subjects.add(subject)

    # Prune sourced subjects from the queue (only those now covered)
    if not args.subjects and not args.dry:
        q = load_queue()
        remaining = []
        for it in q.get("queue", []):
            if store.coverage_count(it["subject"], "image") >= 1:
                continue
            remaining.append(it)
        q["queue"] = remaining
        save_queue(q)

    print(f"\n── Done. Kept {total} assets across {len(sourced_subjects)} subjects. "
          f"Mirror now holds {len(store.mirror_assets())} assets.")


if __name__ == "__main__":
    main()
