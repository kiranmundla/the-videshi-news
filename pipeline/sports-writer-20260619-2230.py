#!/usr/bin/env python3
"""
Sports Writer — June 19, 2026 (22:30 UTC slot)
Article: Neeraj Chopra's 2026 comeback at the Doha Diamond League ends in a
fourth-place finish (85.69m season's best), but the throw clears the
Commonwealth Games qualifying standard — so the lay-off ends with the season
back on track.

ANGLE: Recent sports coverage included two PREVIEW pieces on Chopra's Doha
return (the "274 days without a throw" preview and a comeback-context piece).
Neither covered the ACTUAL RESULT, which only landed late June 19 / early
June 20. This is the news: he finished 4th with 85.69m on a windy night,
behind Sri Lanka's Rumesh Pathirage (88.96), Anderson Peters (86.38) and the
USA's Curtis Thompson (85.99). The story isn't a defeat — it's a marker:
rust after a back injury, but the CWG standard ticked off and the body
holding up ahead of Glasgow and the Asian Games.

Hero: Wikipedia portrait of Neeraj Chopra (upload.wikimedia.org), then Commons.
"""

import os, sys, json, io
from datetime import datetime, timezone

import requests
from PIL import Image

# ── ENV ──
env_supa = os.path.expanduser("~/.env.supabase")
for line in open(env_supa):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
UA = "TheVideshi/1.0 (thevideshi.com)"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(" ", "_")
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=8):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    }
    out = []
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers={"User-Agent": UA}, timeout=15,
        )
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            for p in pages.values():
                ii = (p.get("imageinfo") or [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and mime.startswith("image/") and ii.get("width", 0) >= 800:
                    out.append({"url": url, "title": p.get("title", ""),
                                "w": ii.get("width"), "h": ii.get("height")})
    except Exception as e:
        print(f"  \u26a0 Commons error for '{search_query}': {e}")
    return out


def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_url, filename):
    try:
        import subprocess
        tmp = f"/tmp/{filename}"
        subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, img_url], capture_output=True)
        if not (os.path.exists(tmp) and os.path.getsize(tmp) > 5000):
            print(f"  \u2717 Download failed for {img_url[:80]}")
            return None
        content = open(tmp, "rb").read()
        compressed = compress_image(content)
        print(f"  \U0001f4e6 Compressed to {len(compressed)/1024:.0f} KB")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true",
            },
            data=compressed, timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded: {public_url}")
            return public_url
        else:
            print(f"  \u2717 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  \u2717 Upload error: {e}")
        return None


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  \u2713 Inserted article: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


print("\n" + "="*60)
print("ARTICLE: Neeraj Chopra 4th in Doha comeback, but CWG mark ticked off")
print("="*60)

art_slug = "neeraj-chopra-fourth-doha-diamond-league-2026-comeback-85-69m-season-best-commonwealth-games-qualifying-standard-back-injury-nri"
art_headline = "Neeraj Chopra Finished Fourth on His Comeback. The Number That Matters Is 85.69."
art_subheadline = "After 275 days out with a back injury, India's two-time Olympic medallist returned in Doha well short of his best \u2014 but his season's-best throw cleared the Commonwealth Games qualifying mark, and that was the point all along."

art_body = """DOHA \u2014 For nine months, the most reliable arm in Indian athletics had not let go of a javelin in competition. So when Neeraj Chopra walked into the Qatar Sports Club on Friday night, the question was never really about where he would finish. It was about whether the back would hold, whether the rhythm would come, and whether the body that carried India to an Olympic gold and a silver could be trusted again. The answer, by the end of a windy evening, was a qualified yes \u2014 wrapped inside a fourth-place finish that, on paper, looks like a disappointment.

Chopra ended the night with a best throw of 85.69 metres, behind Sri Lanka's Rumesh Tharanga Pathirage (88.96m), Grenada's former world champion Anderson Peters (86.38m), and the United States' Curtis Thompson (85.99m). It was the first time in a long while that the Indian had walked off a Diamond League runway without a podium place. And yet, for those who understand what this evening was actually for, 85.69 was the number that mattered most.

## Why 85.69 Is a Win

That throw cleared the Athletics Federation of India's qualifying standard of 82.61m for the Commonwealth Games, which begin on July 23. In other words, the very outing that left fans deflated also booked Chopra's ticket to Glasgow and confirmed, in the most concrete terms available, that the back injury that wiped out the first half of his season is behind him. A man returning from 275 days away does not need to win in June. He needs to throw far enough to know the machinery still works \u2014 and to do it without breaking down. Chopra did both.

"This is still a good outing," is the prevailing read among those around the camp, because it allows him to assess his recovery ahead of the season's two mega events \u2014 the Commonwealth Games and the Asian Games. For an athlete who has built a career on peaking at the right championship rather than chasing every June meet, a low-stakes return that ticks the qualifying box is close to the ideal first step.

## The Throws Tell the Story

The series itself read like a man shaking off rust. Chopra opened with a foul, then settled to a modest 82.77m in the second round. His third attempt \u2014 85.69m \u2014 was his best of the night and his season's best. He could not improve on it, managing 83.45m in the fourth round before fouling his fifth and final throw. Usually his opening attempt is his strongest; on Friday, an overstep on the runway cost him that early marker and he never quite found the release that has taken him beyond 90 metres.

The conditions did not help. Doha's shifting winds have shaped some of the longest throws in javelin history \u2014 including Chopra's own maiden 90.23m here last year \u2014 but they cut both ways. Pathirage, the world leader who launched a stunning 92.62m in Rome two weeks ago, could manage only 88.96m and looked nowhere near his best either. Fellow Indian Sachin Yadav failed to qualify for the final.

## A Different Kind of Season

What makes 2026 unusual is that, for once, there is no Olympic or World Championship title on the line. The marquee events are the Commonwealth Games in Glasgow and the Asian Games in Japan \u2014 competitions Chopra has won before, and where he carries the weight of defending champion rather than chasing a maiden crown. He has warned that the fields will be unforgiving regardless. "The Commonwealth will be no less than the Olympics or the World Championships," he has said, pointing to a generation of throwers now routinely past 90 metres.

Much of his recovery was spent at the Swiss Olympic Training Centre in Magglingen, a mountain base he credits for the quiet it offered. "I really like that place; it's in the mountains, and very quiet, so you can focus on your things and techniques," he said. That focus will be tested quickly: the Diamond League calendar does not pause, and Chopra will want sharper outings before Glasgow.

## What's Next

The comeback is no longer a question mark. Chopra is back on the circuit, healthy enough to compete and far enough along to have already qualified for his first big target of the year. The distances will come; they always have. For a diaspora that has adopted him as the rare Indian track-and-field icon \u2014 the man who turned javelin into prime-time viewing in households from New Jersey to Surrey \u2014 a fourth place in June is not the headline. The headline is that the most decorated athlete India has produced is whole again, spear in hand, with the season's biggest nights still ahead of him."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Neeraj Chopra, India's two-time Olympic javelin medallist"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Subject athlete (Wikipedia portrait)
for person, cap in [
    ("Neeraj Chopra", "Neeraj Chopra, who returned from a back injury to finish fourth at the 2026 Doha Diamond League"),
]:
    wiki_img = fetch_wikipedia_person_image(person)
    if wiki_img:
        got = upload_to_supabase(wiki_img, f"{art_slug}.jpg")
        if got:
            img_final = got
            img_caption = cap
            break

# 2) Fallback: on-topic Commons imagery
if not img_final:
    for q in ["Neeraj Chopra", "Neeraj Chopra javelin", "javelin throw Diamond League"]:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            low = c["title"].lower()
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                           "letters", "diagram", "chart", "flag", "icon"]):
                continue
            if not any(g in low for g in ["neeraj", "chopra", "javelin"]):
                continue
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
                img_caption = "Neeraj Chopra, India's two-time Olympic javelin medallist"
                break
        if img_final:
            break

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "athletics",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "IANS \u2014 Neeraj Chopra finishes fourth in Doha Diamond League on return to action for crucial season", "url": "https://ianslive.in/neeraj-chopra-finishes-fourth-in-doha-diamond-league-on-return-to-action-for-crucial-season--20260620004840"},
        {"name": "IANS \u2014 CWG will be no less than Olympics or World C'ships, will be really tough: Neeraj Chopra", "url": "https://ianslive.in/"},
        {"name": "PTI \u2014 Neeraj Chopra to return to action at Doha Diamond League", "url": "https://www.ptinews.com/"},
        {"name": "Olympics.com \u2014 Doha Diamond League 2026 javelin throw results", "url": "https://olympics.com/"},
    ]),
    "diaspora_angle": "Neeraj Chopra is the rare Indian track-and-field superstar the diaspora has made appointment viewing, and his healthy return from a long injury lay-off \u2014 with a Commonwealth Games berth already secured \u2014 keeps alive the medal hopes NRIs rally behind at every global championship.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

print("\n" + "="*60)
print("DONE")
print("="*60)
mark = "\u2713" if art_id else "\u2717"
print(f"Article: {mark} {art_slug}")
print(f"Word count: ~{len(art_body.split())} words")
print(f"Image: {img_final or '(none)'}")
print("Set to status='review'")
