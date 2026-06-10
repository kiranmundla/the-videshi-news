#!/usr/bin/env python3
"""Celebrity Buzz Refresh — fetch Wikipedia thumbnails + Google News RSS headlines for 23 celebrities."""

import json, time, re, ssl, sys
import html as html_mod
from datetime import datetime, timezone
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import xml.etree.ElementTree as ET

SSL_CTX = ssl.create_default_context()
UA = "TheVideshi/1.0 (https://thevideshi.com; news aggregator)"

CELEBRITIES = [
    {"name": "Katrina Kaif", "handle": "katrinakaif", "wiki": None},
    {"name": "Diljit Dosanjh", "handle": "diljitdosanjh", "wiki": None},
    {"name": "Alia Bhatt", "handle": "aliaabhatt", "wiki": None},
    {"name": "Priyanka Chopra", "handle": "priyankachopra", "wiki": "Priyanka_Chopra"},
    {"name": "Shah Rukh Khan", "handle": "iamsrk", "wiki": None},
    {"name": "Kareena Kapoor Khan", "handle": "kareenakapoorkhan", "wiki": "Kareena_Kapoor"},
    {"name": "Shraddha Kapoor", "handle": "shraddhakapoor", "wiki": None},
    {"name": "Deepika Padukone", "handle": "deepikapadukone", "wiki": None},
    {"name": "Ranveer Singh", "handle": "ranveersingh", "wiki": None},
    {"name": "Aishwarya Rai Bachchan", "handle": "aishwaryaraibachchan_arb", "wiki": "Aishwarya_Rai"},
    {"name": "Rashmika Mandanna", "handle": "rashmika_mandanna", "wiki": None},
    {"name": "Samantha Ruth Prabhu", "handle": "samantharuthprabhuoffl", "wiki": "Samantha_Ruth_Prabhu"},
    {"name": "Allu Arjun", "handle": "alluarjunonline", "wiki": None},
    {"name": "Ram Charan", "handle": "alwaysramcharan", "wiki": None},
    {"name": "Jr NTR", "handle": "jrntr", "wiki": "Jr._NTR"},
    {"name": "Janhvi Kapoor", "handle": "janhvikapoor", "wiki": None},
    {"name": "Ananya Panday", "handle": "ananyapanday", "wiki": None},
    {"name": "Kiara Advani", "handle": "kiaraaliaadvani", "wiki": None},
    {"name": "Hrithik Roshan", "handle": "hrithikroshan", "wiki": None},
    {"name": "Varun Dhawan", "handle": "varundhawan", "wiki": None},
    {"name": "Shreya Ghoshal", "handle": "shreyaghoshal", "wiki": None},
    {"name": "AR Rahman", "handle": "arrahman", "wiki": "A._R._Rahman"},
    {"name": "Vijay Thalapathy", "handle": "actorvijay", "wiki": "Vijay_(actor)"},
]

def fetch(url, timeout=12):
    req = Request(url, headers={"User-Agent": UA})
    try:
        resp = urlopen(req, timeout=timeout, context=SSL_CTX)
        return resp.status, resp.read()
    except HTTPError as e:
        return e.code, None
    except Exception:
        return 0, None

def wiki_thumb(name, override=None):
    titles = [override] if override else [
        name.replace(" ", "_"),
        f"{name.replace(' ', '_')}_(actor)",
        f"{name.replace(' ', '_')}_(actress)",
        f"{name.replace(' ', '_')}_(singer)",
    ]
    for t in titles:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(t)}"
        code, body = fetch(url)
        if code == 200 and body:
            try:
                d = json.loads(body)
                src = d.get("thumbnail", {}).get("source", "")
                if src:
                    return src
            except Exception:
                pass
        time.sleep(0.15)
    return ""

def news_headlines(name):
    q = quote(f'"{name}"')
    url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
    code, body = fetch(url, timeout=15)
    if code != 200 or not body:
        return []
    try:
        root = ET.fromstring(body)
        out = []
        for item in root.findall(".//item")[:6]:
            te = item.find("title")
            if te is not None and te.text:
                t = html_mod.unescape(te.text.strip())
                t = re.sub(r'\s+-\s+[A-Z][\w\s&.\'\-,]+$', '', t)
                if t and len(t) > 12:
                    out.append(t)
        return out
    except ET.ParseError:
        return []

def caption_from(name, headlines):
    if not headlines:
        return f"Stay updated with the latest from {name}."
    c = re.sub(r'\.\.\.+$', '', headlines[0]).strip()
    if not c.endswith(('.', '!', '?')):
        c += '.'
    if len(headlines) > 1 and len(c) < 80:
        h2 = re.sub(r'\.\.\.+$', '', headlines[1]).strip()
        if not h2.endswith(('.', '!', '?')):
            h2 += '.'
        c = f"{c} {h2}"
    return c

def main():
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    print(f"Celebrity Buzz Refresh — {now.isoformat()}")

    posts = []
    missing_news = []
    missing_thumb = []

    for i, cel in enumerate(CELEBRITIES):
        name, handle = cel["name"], cel["handle"]
        print(f"[{i+1:2d}/23] {name}", end=" … ", flush=True)

        thumb = wiki_thumb(name, cel.get("wiki"))
        hl = news_headlines(name)
        cap = caption_from(name, hl)

        if not thumb:
            missing_thumb.append(name)
        if not hl:
            missing_news.append(name)

        print(f"thumb={'✓' if thumb else '✗'}  news={len(hl)}  cap={cap[:70]}")

        posts.append({
            "celebrity": name,
            "name": name,
            "handle": handle,
            "platform": "instagram",
            "thumbnail": thumb,
            "caption": cap,
            "url": f"https://www.instagram.com/{handle}/",
            "media_type": "image",
            "timestamp": today,
        })
        time.sleep(0.35)

    output = {"last_updated": now.isoformat(), "posts": posts}
    path = "/home/hatch/workspace/the-videshi-news/public/data/celebrity-buzz.json"
    with open(path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {len(posts)} entries.")
    if missing_thumb:
        print(f"MISSING THUMBS: {missing_thumb}")
    if missing_news:
        print(f"MISSING NEWS (need browser_search): {missing_news}")

    # Also dump missing lists to temp for easy reading
    with open("/tmp/celeb_missing.json", "w") as f:
        json.dump({"missing_news": missing_news, "missing_thumb": missing_thumb}, f)

if __name__ == "__main__":
    main()
