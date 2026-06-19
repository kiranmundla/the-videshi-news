#!/usr/bin/env python3
"""
social_scrapers.py — best-effort public-post scrapers for Threads and Instagram,
used as LOWER-CONFIDENCE fallbacks for the reel "ON THE FEED" social card after
the reliable X (Twitter) API path.

Design contract (see shotstack-reel.py social-card block + the build task):
  * FAIL-SAFE ABOVE ALL. Every public function returns None on ANY failure
    (network, proxy stall, 429, login wall, parse error, private/missing field).
    Nothing here raises. Short hard timeouts. A blocked/empty scraper must never
    slow down or break a reel build.
  * ATTRIBUTION-CLEAN. We only ever return a post we actually fetched: a real
    author, real handle, and a real photo URL. No fabrication.
  * Same return shape as fetch-tweets.best_photo_tweet() PLUS identity fields,
    so the reel matcher can treat all platforms uniformly:
        {
          "platform": "threads" | "instagram",
          "text": str,
          "photos": [url, ...],
          "photo_count": int,
          "likes": int,
          "created_at": iso8601 str,
          "url": permalink str,
          "name": author display name str,
          "avatar": author avatar url str,
        }

SOURCE-ACCESS REALITY (measured 2026-06-18 from this VM):
  * Instagram: the public web endpoint
      GET https://www.instagram.com/api/v1/users/web_profile_info/?username=<h>
      with header  x-ig-app-id: 936619743392459
    returns real JSON with the last ~12 posts (display_url, caption, likes,
    taken_at_timestamp) for PUBLIC accounts. Works reliably here. CDN images
    download fine via curl. Private accounts return is_private=True (we skip).
  * Threads: the equivalent web_profile_info on threads.com returns the IG
    identity but ZERO timeline posts. The Barcelona GraphQL post-listing
    endpoint (POST /api/graphql) STALLS through the egress proxy (curl status
    000) — the same proxy-hang signature documented in AGENTS.md for X's OAuth2
    token endpoint. So Threads post scraping is effectively unavailable from
    this environment. The fetcher below tries it with a short hard timeout and
    fails safe (returns None). It is written to start working automatically if
    the endpoint ever becomes reachable, without changing callers.
"""

import os
import re
import json
import time
import subprocess

# Hard caps so a hung endpoint can never stall a reel build.
_HTTP_TIMEOUT = 12          # per-request seconds (curl --max-time)
_HARD_TIMEOUT = 16          # outer subprocess wall-clock kill
_DESKTOP_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
               "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
_IG_APP_ID = "936619743392459"  # public web app id used by instagram.com itself


def _curl_get(url, headers=None, timeout=_HTTP_TIMEOUT):
    """Proxy-safe GET via curl. Returns response bytes or None. Never raises.
    curl honors the authenticated egress proxy env vars automatically (Python
    urllib does NOT — see AGENTS.md)."""
    try:
        cmd = ["curl", "-sL", "-A", _DESKTOP_UA, "--max-time", str(timeout)]
        for k, v in (headers or {}).items():
            cmd += ["-H", f"{k}: {v}"]
        cmd.append(url)
        out = subprocess.run(cmd, capture_output=True,
                             timeout=_HARD_TIMEOUT).stdout
        return out if out else None
    except Exception:
        return None


def _relevance(text, topic_keywords):
    if not topic_keywords:
        return 0
    tl = (text or "").lower()
    return sum(1 for kw in topic_keywords if kw and kw.lower() in tl)


def _pick_best(posts, topic_keywords):
    """From a list of normalized post dicts (each WITH >=1 photo), pick the best:
    topical relevance first, then likes, then recency. Mirrors the X path's
    best_photo_tweet ranking. Returns one dict or None."""
    if not posts:
        return None
    scored = []
    for p in posts:
        rel = _relevance(p.get("text", ""), topic_keywords)
        scored.append((rel, p.get("likes", 0) or 0, p.get("created_at", ""), p))
    # If keywords were given and at least one post is on-topic, require relevance>0
    # (don't ship an off-topic post when we were asked for a specific subject).
    if topic_keywords and any(s[0] > 0 for s in scored):
        scored = [s for s in scored if s[0] > 0]
    scored.sort(key=lambda s: (-s[0], -s[1], s[2]), reverse=False)
    # note: created_at ascending would prefer older; we want newer as final
    # tiebreak, so re-sort with recency descending as the last key:
    scored.sort(key=lambda s: (s[0], s[1], s[2]), reverse=True)
    return scored[0][3] if scored else None


# ─────────────────────────────── Instagram ────────────────────────────────

def instagram_best_photo_post(handle, hours=168, topic_keywords=None):
    """Best-effort: fetch a PUBLIC Instagram profile's recent posts and return
    the most topically-relevant recent post WITH a photo. Returns a normalized
    post dict or None. Never raises."""
    try:
        handle = (handle or "").lstrip("@").strip()
        if not handle:
            return None
        body = _curl_get(
            f"https://www.instagram.com/api/v1/users/web_profile_info/?username={handle}",
            headers={"x-ig-app-id": _IG_APP_ID,
                     "Referer": f"https://www.instagram.com/{handle}/"})
        if not body:
            return None
        try:
            data = json.loads(body)
        except Exception:
            return None
        user = (data.get("data") or {}).get("user") or {}
        if not user or user.get("is_private"):
            return None
        name = user.get("full_name") or handle
        avatar = user.get("profile_pic_url_hd") or user.get("profile_pic_url") or ""
        edges = ((user.get("edge_owner_to_timeline_media") or {}).get("edges")) or []
        cutoff = time.time() - hours * 3600
        posts = []
        for e in edges:
            n = e.get("node") or {}
            ts = n.get("taken_at_timestamp") or 0
            if ts and ts < cutoff:
                continue  # too old
            # Collect ALL still photos from this post. Carousels (GraphSidecar)
            # carry children in edge_sidecar_to_children; single posts use
            # display_url. INSTAGRAM = PHOTOS ONLY — skip every video child and
            # skip a top-level single video post entirely (stills only for now).
            photos = []
            has_video = bool(n.get("is_video"))
            children = ((n.get("edge_sidecar_to_children") or {}).get("edges")) or []
            if children:
                for ce in children:
                    cn = ce.get("node") or {}
                    if cn.get("is_video"):
                        has_video = True
                        continue  # never render native video
                    durl = cn.get("display_url") or ""
                    if durl:
                        photos.append(durl)
            elif not n.get("is_video"):
                durl = n.get("display_url") or ""
                if durl:
                    photos.append(durl)
            if not photos:
                continue  # video-only post or no usable still — skip
            # Caption
            cap = ""
            ce = ((n.get("edge_media_to_caption") or {}).get("edges")) or []
            if ce:
                cap = (ce[0].get("node") or {}).get("text", "") or ""
            shortcode = n.get("shortcode") or ""
            posts.append({
                "platform": "instagram",
                "text": cap,
                "photos": photos,
                "photo_count": len(photos),
                "has_video": has_video,
                "likes": (n.get("edge_liked_by") or {}).get("count", 0) or 0,
                "created_at": (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))
                              if ts else ""),
                "url": f"https://www.instagram.com/p/{shortcode}/" if shortcode else
                       f"https://www.instagram.com/{handle}/",
                "name": name,
                "avatar": avatar,
            })
        best = _pick_best(posts, topic_keywords)
        return best
    except Exception:
        return None


# ──────────────────────────────── Threads ─────────────────────────────────

def _threads_user_id(handle):
    """Resolve a Threads/IG numeric user id from the threads.com profile JSON.
    Returns str id or None. Never raises."""
    try:
        body = _curl_get(
            f"https://www.threads.com/api/v1/users/web_profile_info/?username={handle}",
            headers={"x-ig-app-id": _IG_APP_ID,
                     "Referer": f"https://www.threads.com/@{handle}"})
        if not body:
            return None
        data = json.loads(body)
        user = (data.get("data") or {}).get("user") or {}
        return str(user.get("id")) if user.get("id") else None
    except Exception:
        return None


def threads_best_photo_post(handle, hours=168, topic_keywords=None):
    """Best-effort: fetch a PUBLIC Threads profile's recent posts and return the
    most topically-relevant recent post WITH a photo. Returns a normalized post
    dict or None. Never raises.

    NOTE: The Threads post-listing GraphQL endpoint currently STALLS through the
    egress proxy from this environment (curl status 000), so this returns None in
    practice today. It is written to work if/when the endpoint is reachable.
    Uses the canonical threads.com domain (never threads.net — see AGENTS.md)."""
    try:
        handle = (handle or "").lstrip("@").strip()
        if not handle:
            return None

        # Need an LSD token + the numeric user id to call the GraphQL list query.
        prof_html = _curl_get(f"https://www.threads.com/@{handle}")
        if not prof_html:
            return None
        prof_html = prof_html.decode("utf-8", "ignore")
        m = re.search(r'"LSD",\[\],\{"token":"([^"]+)"', prof_html)
        lsd = m.group(1) if m else None
        user_id = _threads_user_id(handle)
        if not lsd or not user_id:
            return None

        # Barcelona profile threads-tab GraphQL. doc_id rotates; this is the best
        # known public one. Short hard timeout — if the proxy stalls we bail.
        variables = json.dumps({
            "userID": user_id,
            "__relay_internal__pv__BarcelonaIsLoggedInrelayprovider": False,
            "__relay_internal__pv__BarcelonaIsThreadContextHeaderEnabledrelayprovider": False,
        })
        try:
            cmd = ["curl", "-sL", "-A", _DESKTOP_UA, "--max-time", "6",
                   "-H", f"X-FB-LSD: {lsd}",
                   "-H", f"X-IG-App-ID: {_IG_APP_ID}",
                   "-H", "Sec-Fetch-Site: same-origin",
                   "-H", "Origin: https://www.threads.com",
                   "-H", f"Referer: https://www.threads.com/@{handle}",
                   "-H", "Content-Type: application/x-www-form-urlencoded",
                   "--data-urlencode", f"lsd={lsd}",
                   "--data-urlencode", f"variables={variables}",
                   "--data", "doc_id=7448594591874178",
                   "https://www.threads.com/api/graphql"]
            raw = subprocess.run(cmd, capture_output=True, timeout=7).stdout
        except Exception:
            return None
        if not raw:
            return None
        try:
            data = json.loads(raw)
        except Exception:
            return None

        # Walk the (deeply nested, frequently-changing) response defensively.
        posts = []
        cutoff = time.time() - hours * 3600

        def walk(node):
            """Collect Threads post nodes with photo(s) from an arbitrary tree.
            Captures ALL still images on a post (carousels included) and skips
            video. Threads embeds media in 'image_versions2' (single) and/or
            'carousel_media' (multi)."""
            if isinstance(node, dict):
                photos = []
                # Single image
                iv = node.get("image_versions2")
                if iv and isinstance(iv, dict) and not node.get("video_versions"):
                    cands = iv.get("candidates") or []
                    if cands and cands[0].get("url"):
                        photos.append(cands[0]["url"])
                # Carousel: multiple children, skip any with video_versions
                for cm in (node.get("carousel_media") or []):
                    if not isinstance(cm, dict) or cm.get("video_versions"):
                        continue  # never render native video
                    civ = cm.get("image_versions2") or {}
                    ccands = civ.get("candidates") or []
                    if ccands and ccands[0].get("url"):
                        photos.append(ccands[0]["url"])
                if photos:
                    cap = ""
                    capobj = node.get("caption")
                    if isinstance(capobj, dict):
                        cap = capobj.get("text", "") or ""
                    ts = node.get("taken_at") or 0
                    code = node.get("code") or ""
                    if not ts or ts >= cutoff:
                        posts.append({
                            "platform": "threads",
                            "text": cap,
                            "photos": photos,
                            "photo_count": len(photos),
                            "has_video": bool(node.get("video_versions") or
                                              any((cm or {}).get("video_versions")
                                                  for cm in (node.get("carousel_media") or []))),
                            "likes": node.get("like_count", 0) or 0,
                            "created_at": (time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                          time.gmtime(ts)) if ts else ""),
                            "url": f"https://www.threads.com/@{handle}/post/{code}"
                                   if code else f"https://www.threads.com/@{handle}",
                            "name": handle,
                            "avatar": "",
                        })
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(data)
        return _pick_best(posts, topic_keywords)
    except Exception:
        return None


# ─────────────────────────────── CLI / smoke test ─────────────────────────

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("platform", choices=["instagram", "threads"])
    ap.add_argument("handle")
    ap.add_argument("--hours", type=int, default=168)
    ap.add_argument("--topic", type=str, default="")
    args = ap.parse_args()
    kws = [w.strip() for w in args.topic.split(",") if w.strip()] or None
    fn = instagram_best_photo_post if args.platform == "instagram" else threads_best_photo_post
    t0 = time.time()
    res = fn(args.handle, hours=args.hours, topic_keywords=kws)
    dt = time.time() - t0
    if res:
        print(f"✓ {args.platform} @{args.handle} ({dt:.1f}s): "
              f"likes={res['likes']} ts={res['created_at']}")
        print(f"  text: {res['text'][:80]}")
        print(f"  photo: {res['photos'][0][:90]}")
        print(f"  url: {res['url']}")
    else:
        print(f"✗ {args.platform} @{args.handle} ({dt:.1f}s): no usable post (fail-safe None)")
