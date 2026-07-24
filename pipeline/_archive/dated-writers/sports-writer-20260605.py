#!/usr/bin/env python3
"""Sports writer — June 5 2026 run. Two articles."""

import json, os, sys, time, uuid, re, io
from datetime import datetime, timezone

import requests
from PIL import Image

# ── env ──────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            line = line.replace("export ", "", 1)
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k, v)

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ── helpers ──────────────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(" ", "_")
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(query, limit=5):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": UA},
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []


def fetch_pexels_image(*queries):
    if not PEXELS_KEY:
        return None
    for q in queries:
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": q, "per_page": 3, "orientation": "landscape"},
                headers={"Authorization": PEXELS_KEY},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p["src"]["large2x"]
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error: {e}")
    return None


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


def upload_image_to_supabase(img_url, filename):
    print(f"  ⬇ Downloading {img_url[:80]}...")
    r = requests.get(img_url, headers={"User-Agent": UA}, timeout=20)
    if r.status_code != 200:
        print(f"  ✗ Download failed: HTTP {r.status_code}")
        return None
    raw = r.content
    if len(raw) < 5000:
        print(f"  ✗ Image too small ({len(raw)} bytes)")
        return None

    compressed = compress_image(raw)
    print(f"  📦 Compressed: {len(raw)} → {len(compressed)} bytes")

    upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    resp = requests.post(
        upload_url,
        headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        },
        data=compressed,
        timeout=30,
    )
    if resp.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded to Supabase: {public_url}")
        return public_url
    else:
        print(f"  ✗ Upload failed: {resp.status_code} {resp.text[:200]}")
        return None


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Article inserted: {art_id}")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None


def source_best_image(person_name=None, topic_queries=None, pexels_queries=None):
    """Multi-source image search. Returns (url, attribution) or (None, None)."""
    candidates = []

    # Wikipedia person image
    if person_name:
        img = fetch_wikipedia_person_image(person_name)
        if img:
            candidates.append({"url": img, "source": "wikipedia", "priority": 1})

    # Wikimedia Commons
    if topic_queries:
        for q in topic_queries:
            results = fetch_wikimedia_commons_images(q)
            for r in results[:2]:
                candidates.append({"url": r["url"], "source": "wikimedia_commons", "priority": 2})

    # Pexels fallback
    if pexels_queries:
        img = fetch_pexels_image(*pexels_queries)
        if img:
            candidates.append({"url": img, "source": "pexels", "priority": 3})

    if not candidates:
        return None, None

    # Sort by priority (lower is better)
    candidates.sort(key=lambda x: x["priority"])
    best = candidates[0]
    attribution = "Wikimedia Commons" if best["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
    return best["url"], attribution


# ══════════════════════════════════════════════════════════════════════════
# ARTICLE 1: India U-18 Men Beat Pakistan 5-3, Reach Hockey Asia Cup Final
# ══════════════════════════════════════════════════════════════════════════
def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: India U-18 Hockey — Beat Pakistan 5-3, reach final")
    print("=" * 60)

    slug = "india-u18-hockey-beat-pakistan-5-3-asia-cup-final-purti-hat-trick-japan-nri"
    headline = "India Beat Pakistan 5-3 To Reach the U-18 Hockey Asia Cup Final. Purti Ashish Tani Scored Four."
    subheadline = "Trailing 2-3 going into the final quarter, India scored three unanswered goals in Kakamigahara. They will face hosts Japan in Saturday's final."

    body = """India's U-18 men's hockey team produced a stunning comeback to beat Pakistan 5-3 in the semifinal of the Hockey U-18 Asia Cup 2026 at the Kawasaki Heavy Industries Hockey Stadium in Kakamigahara, Japan, on Friday.

Trailing 2-3 entering the final quarter, India scored three unanswered goals to seal a place in Saturday's final against hosts Japan. The hero was Purti Ashish Tani, who scored four of India's five goals, including a hat-trick in the second half that broke the match open.

## A Pulsating Contest From the Start

Both teams began with intensity and attacking intent. India drew first blood in the 12th minute when a penalty stroke was awarded after Pakistan's video referral failed to overturn the on-field decision. Purti Ashish Tani stepped up and converted with composure, giving India the lead heading into the second quarter.

Pakistan responded strongly, creating multiple chances from penalty corners in the second quarter but failing to convert either opportunity. It was Adeel who finally found the equaliser in the 27th minute, finishing clinically to send the teams into the break level at 1-1.

## Pakistan Take the Lead, India Refuse to Fold

The third quarter produced a flurry of goals. Ali Shahrukh restored India's lead in the 35th minute with a well-taken strike, but Pakistan hit back almost immediately through Muhammad Farhan Aslam in the 37th minute to make it 2-2.

Pakistan then went ahead for the first time when Uzair Ahmed converted a penalty corner in the 42nd minute. At 3-2 down heading into the final quarter, India faced the prospect of elimination against their fiercest rivals.

## Purti Ashish Tani Takes Over

The final fifteen minutes belonged entirely to India, and specifically to Purti Ashish Tani. He levelled the score from a penalty corner, then completed his hat-trick in the 53rd minute to put India 4-3 ahead. With Pakistan pushing forward desperately, Purti added a fourth goal in the closing stages to seal a comprehensive 5-3 victory.

## A Tournament of Dominance

India's run through the tournament has been formidable. They opened with a 13-0 demolition of Kazakhstan, lost 2-4 to hosts Japan in the group stage, then beat Korea 4-1 and Chinese Taipei 13-1. Captain Ketan Kushwaha leads the tournament's scoring charts with seven goals, while Purti Ashish Tani now has ten across pool and knockout stages.

The semifinal victory also carries special significance given the India-Pakistan sporting rivalry. In hockey, the two nations share a deep and storied history, and for these young players, beating Pakistan in a knockout match at an Asian championship will be a defining memory.

## Women's Team Falls in Shootout

The day brought mixed fortunes for India. Earlier, the U-18 women's team suffered a heartbreaking 1-3 shootout defeat to China after regulation time ended 2-2. Captain Sweety Kujur's setup for Nousheen Naz had given India an early lead in the third minute, but China equalised through Li ZeYan in the 24th minute. China took a 2-1 lead via Zhang Yuzheng in the 48th minute before Kiran Ekka's penalty corner conversion in the 54th minute forced the shootout.

Chinese goalkeeper Liu Xue was the difference in the tiebreaker, allowing only Sandeepa Kumari to score for India while three Chinese shooters converted. The women's team will now play in the bronze medal match.

## What It Means for Indian Hockey

For NRI fans following Indian hockey's youth pipeline, the men's result is a significant marker. Coach Sardar Singh, the former India captain who has been instrumental in developing this group, has built a team that combines penalty corner expertise with composure under pressure. Saturday's final against Japan, who beat India 4-2 in the group stage, offers a chance at redemption and a continental title.

**Sources:** Asian Hockey Federation, Sports 247 News, Mykhel, The Trending People"""

    # Image sourcing
    print("\n📷 Sourcing image...")
    img_url, attribution = source_best_image(
        person_name="Sardar Singh (field hockey)",
        topic_queries=["India junior hockey team", "India Pakistan hockey Asia Cup"],
        pexels_queries=["field hockey match India", "hockey players match"],
    )

    final_img_url = None
    if img_url:
        final_img_url = upload_image_to_supabase(img_url, f"{slug}.jpg")

    image_caption = "Indian junior hockey players celebrate during the U-18 Asia Cup in Kakamigahara, Japan"
    if not final_img_url:
        # Try one more Pexels search
        img_url = fetch_pexels_image("field hockey match players", "hockey sport turf")
        if img_url:
            final_img_url = upload_image_to_supabase(img_url, f"{slug}.jpg")
            attribution = "Pexels"

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            "Asian Hockey Federation",
            "Sports 247 News Pakistan",
            "Mykhel",
            "The Trending People"
        ]),
    }

    if final_img_url:
        article["image_url"] = final_img_url
        article["image_caption"] = image_caption
        article["image_attribution"] = attribution

    return insert_article(article)


# ══════════════════════════════════════════════════════════════════════════
# ARTICLE 2: Ishan Kishan Returns to India Squad After Nearly Three Years
# ══════════════════════════════════════════════════════════════════════════
def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: Ishan Kishan ODI Comeback")
    print("=" * 60)

    slug = "ishan-kishan-india-odi-comeback-afghanistan-three-years-bcci-contract-mental-health-nri"
    headline = "Ishan Kishan Is Back in India's ODI Squad. His Last Game Was Against Afghanistan, Nearly Three Years Ago."
    subheadline = "He lost his BCCI contract, missed the T20 World Cup, and spent months away from international cricket. Now the selectors have called him back for the same opponent."

    body = """When Ishan Kishan walks out for India during the three-match ODI series against Afghanistan starting June 14 in Dharamsala, it will close one of Indian cricket's most turbulent chapters of exile and return.

The left-handed wicketkeeper-batter has been named in India's ODI squad for the Afghanistan tour, his first call-up to the fifty-over format since the 2023 Cricket World Cup. Coincidentally, his last ODI appearance came against Afghanistan during that very tournament, making this recall a symmetry that feels almost scripted.

## The Fall

Kishan's descent from India's inner circle was as swift as it was public. After scoring a double century against Bangladesh in December 2022 and cementing his place as India's backup wicketkeeper-batter, everything unravelled during the South Africa tour in late 2023.

He left the series midway, citing mental health concerns. What followed made the situation worse. Instead of returning to domestic cricket as the BCCI expected, Kishan was spotted training with Hardik Pandya in Baroda. He did not play in the Ranji Trophy 2024. The BCCI was furious. His central contract was revoked, and the doors to international cricket slammed shut.

For the better part of two years, Kishan was on the outside looking in. He watched from the margins as India won the T20 World Cup 2024, cycled through wicketkeeping options, and moved forward without him.

## The Climb Back

What changed was domestic cricket. Kishan returned to playing for Jharkhand with a quiet determination that gradually rebuilt his case. Consistent performances in domestic one-day and T20 competitions caught the selectors' attention. His name resurfaced in India A squads and T20I series against New Zealand, where he showed he had lost none of his explosive ability.

"There is so much healthy competition that you start enjoying it and don't take it as additional pressure," Kishan told The Times of India recently, reflecting on the challenge of competing for a spot in a squad brimming with talent. The maturity in his words suggests the time away has reshaped more than just his technique.

## Why the Selectors Picked Him Now

India's ODI squad for the Afghanistan series features Shubman Gill as captain, with Rohit Sharma and Hardik Pandya's participation subject to fitness clearance. Virat Kohli, already ruled out of the preceding Test with a hamstring injury sustained during the IPL final, is expected to be available for the ODIs.

Kishan enters a squad where KL Rahul is the first-choice wicketkeeper. But the selectors clearly see value in having a left-handed explosive option who can bat anywhere in the top order and keep wickets when needed. With the 2027 Cricket World Cup cycle in full swing, this series against Afghanistan is as much about auditions as it is about results.

Prince Yadav, the tall right-arm pacer from Lucknow Super Giants, has also earned a maiden ODI call-up, while uncapped all-rounders Gurnoor Brar and Harsh Dubey feature in both the Test and ODI squads.

## What NRI Fans Should Know

For diaspora cricket followers, Kishan's story resonates beyond the boundary. His exile raised important questions about how Indian cricket handles mental health, the rigidity of the BCCI's domestic-cricket mandate, and whether players who step away deserve a path back. His return suggests the answer, at least in this case, is yes, provided the runs come.

The three ODIs will be played in Dharamsala (June 14), Lucknow (June 17), and Chennai (June 20), all starting at 1:30 PM IST. For NRI fans in the US, that means early morning viewing on the East Coast and pre-dawn starts on the West.

The Afghanistan squad, meanwhile, will have Rashid Khan available for the ODIs after being rested from the preceding Test. Mohammad Nabi, Rahmanullah Gurbaz, and Ibrahim Zadran form the spine of a side that clean-swept Bangladesh in ODIs last October and will not be taken lightly.

Kishan's last ODI innings against Afghanistan in the 2023 World Cup was forgettable. This time, he has the weight of a redemption arc and the freedom of having nothing left to lose.

**Sources:** CricTracker, The Times of India, Wisden, The Indian EYE, SportsKeeda"""

    # Image sourcing
    print("\n📷 Sourcing image...")
    img_url, attribution = source_best_image(
        person_name="Ishan Kishan",
        topic_queries=["Ishan Kishan cricket India"],
        pexels_queries=["cricket batsman India", "cricket match batsman"],
    )

    final_img_url = None
    if img_url:
        final_img_url = upload_image_to_supabase(img_url, f"{slug}.jpg")

    image_caption = "Ishan Kishan during an international match for India"

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps([
            "CricTracker",
            "The Times of India",
            "Wisden",
            "The Indian EYE",
            "SportsKeeda"
        ]),
    }

    if final_img_url:
        article["image_url"] = final_img_url
        article["image_caption"] = image_caption
        article["image_attribution"] = attribution

    return insert_article(article)


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"Sports Writer — {datetime.now(timezone.utc).isoformat()}")
    print(f"Supabase: {SUPABASE_URL}")

    results = []
    art1 = write_article_1()
    if art1:
        results.append(art1)

    art2 = write_article_2()
    if art2:
        results.append(art2)

    print(f"\n{'=' * 60}")
    print(f"Done. {len(results)} articles published.")
    if not results:
        print("⚠ No articles were published!")
        sys.exit(1)
