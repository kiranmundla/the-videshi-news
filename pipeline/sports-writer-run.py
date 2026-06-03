#!/usr/bin/env python3
"""Sports writer for The Videshi — June 3 2026 evening run."""

import json, os, re, subprocess, sys, time, uuid, requests, urllib.parse
from datetime import datetime, timezone

# ── Load env files first ─────────────────────────────────────────────────────
for env_file in [os.path.expanduser("~/.env.supabase"), os.path.expanduser("~/workspace/.env.supabase")]:
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k, v.strip().strip('"').strip("'"))

# ── Supabase config ──────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
PEXELS_KEY = None
try:
    with open(os.path.expanduser("~/workspace/.env.pexels")) as f:
        for line in f:
            if line.startswith("PEXELS_API_KEY="):
                PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
except Exception:
    pass

UA = "TheVideshi/1.0 (thevideshi.com)"

# ── Image sourcing helpers ───────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
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


def fetch_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons. Returns list of image URLs."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
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
                for ii in page.get("imageinfo", []):
                    mime = ii.get("mime", "")
                    if mime.startswith("image/") and "svg" not in mime:
                        url = ii.get("thumburl") or ii.get("url")
                        if url:
                            results.append(url)
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{query}': {e}")
    return []


def fetch_pexels(query, per_page=5):
    """Search Pexels for images. Returns list of image URLs."""
    if not PEXELS_KEY:
        return []
    try:
        r = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page={per_page}"],
            capture_output=True, text=True, timeout=15,
        )
        data = json.loads(r.stdout)
        return [p["src"]["large2x"] for p in data.get("photos", [])]
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return []


def validate_image(url):
    """Check that URL returns a valid image >5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD; try GET
        if "image" in ct and cl == 0:
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception:
        pass
    return False


def best_image(person_names=None, wiki_queries=None, pexels_queries=None):
    """Multi-source compare: Wikipedia person → Wikimedia Commons → Pexels."""
    # 1. Wikipedia person images
    if person_names:
        for name in person_names:
            url = fetch_wikipedia_person_image(name)
            if url and validate_image(url):
                return url, "Wikimedia Commons"

    # 2. Wikimedia Commons search
    if wiki_queries:
        for q in wiki_queries:
            urls = fetch_wikimedia_commons(q)
            for url in urls:
                if validate_image(url):
                    print(f"  ✓ Commons image: {url[:80]}...")
                    return url, "Wikimedia Commons"

    # 3. Pexels fallback
    if pexels_queries:
        for q in pexels_queries:
            urls = fetch_pexels(q)
            for url in urls:
                if validate_image(url):
                    print(f"  ✓ Pexels image: {url[:80]}...")
                    return url, "Pexels"

    return None, None


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Published: {data[0].get('headline', '')[:60]}...")
            return True
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
    return False


# ── Article 1: Satwik-Chirag retire injured from Indonesia Open ───────────

def write_article_1():
    print("\n=== Article 1: Satwik-Chirag Indonesia Open withdrawal ===")

    headline = "They Won the Singapore Open Six Days Ago. On Wednesday in Jakarta, Satwik Pointed to His Shoulder and Walked Off."
    subheadline = "Satwiksairaj Rankireddy's recurring right shoulder injury forced India's top doubles pair to retire from the Indonesia Open first round. The BAI says recovery is now the priority."
    slug = "satwik-chirag-retire-injured-indonesia-open-2026-shoulder-singapore-open-nri"

    body = """A week ago, Satwiksairaj Rankireddy and Chirag Shetty stood on a podium in Singapore holding the trophy that ended a two-year drought on the BWF World Tour. They had beaten Indonesia's Fajar Alfian and Muhammad Shohibul Fikri from a game down. They were the first Indian men's doubles pair to ever win the Singapore Open. The form was emphatic. The momentum was real.

Six days later, it evaporated in Jakarta.

## Seven Minutes

Satwik and Chirag walked onto Court 1 at the Istora Senayan on Wednesday as the fourth seeds at the Indonesia Open 2026, one of the marquee Super 1000 events on the BWF calendar. Their opponents were Malaysia's Aaron Tai and Kang Khai Xing, a pair ranked well outside the top 20.

It was supposed to be a routine opener. Instead, it lasted seven minutes.

Trailing 6-11 in the first game, Satwik gestured toward his right shoulder — the same shoulder that has been a recurring concern since early in the season. He spoke briefly with Chirag, then with the umpire. The pair gave a walkover. The match was over before it had really begun.

## A Pattern That Worries

This is not the first time Satwik's shoulder has disrupted their campaign. The same injury led to their withdrawal from the Badminton Asia Championship earlier this year, depriving them of a chance to build ranking points during a critical stretch of the Olympic qualification cycle.

The Badminton Association of India confirmed the withdrawal with a statement on Wednesday: "Satwiksairaj Rankireddy and Chirag Shetty have withdrawn from the POLYTRON Indonesia Open 2026 due to the former's injury. The pair will now focus on recovery and rehabilitation as they prepare for the important tournaments ahead."

The language was measured, but the subtext is hard to miss. Satwik's shoulder is not a new problem, and the fact that it flared up just days after a physically demanding Singapore Open final raises questions about load management during back-to-back Super 1000 events.

## What This Means for the Rest of 2026

Satwik and Chirag are currently ranked world No. 4 in men's doubles. Their Singapore Open title was a breakthrough moment — proof that the pair, who won the 2022 French Open and have been consistently ranked in the top five, still had the hunger and the game to beat the best.

But the schedule ahead is unforgiving. The next few months include the Japan Open, the Korea Open, and the run-in to the Asian Games and the World Championships. Rankings points from Super 1000 events are among the most valuable on the circuit. Every withdrawal costs them — not just in points, but in momentum, match sharpness, and the confidence that comes from winning tight matches under pressure.

For Indian badminton fans watching from the diaspora, this is a familiar anxiety. India's best doubles pair has the talent to compete for every title, but the margins in men's doubles are razor-thin. Fitness is not a luxury; it is the baseline. When one half of the partnership is managing a chronic shoulder issue, every tournament entry becomes a calculation.

## Indonesia Open: Where India Stands

The withdrawal compounds what has already been a difficult Indonesia Open for India. On Day 1, Lakshya Sen — the country's top-ranked men's singles player — was eliminated by Indonesia's Alwi Farhan in straight games. Kidambi Srikanth also fell in the first round. The mixed doubles pair of Dhruv Kapila and Tanisha Crasto were outclassed by China's sixth seeds. Treesa Jolly and Gayatri Gopichand lost in women's doubles.

The lone bright spots have been PV Sindhu, who defeated Busanan Ongbamrungphan to reach the Round of 16, and the men's doubles pair of Hariharan Amsakarunan and MR Arjun, who upset a Malaysian pair featuring 2016 Olympic silver medallist Tan Wee Kiong.

Sindhu now faces a probable showdown with world No. 1 An Se-young — a player she has lost to nine times without a single win. That is a mountain. But at least Sindhu is on the court.

Satwik and Chirag are headed home to recover. For a pair that just proved they belong at the top, the timing could not be worse.

*Sources: BAI official statement, IANS, BWF tournament records*"""

    # Image sourcing
    img_url, img_attr = best_image(
        person_names=["Satwiksairaj Rankireddy", "Chirag Shetty"],
        wiki_queries=["Satwiksairaj Rankireddy badminton", "Chirag Shetty badminton India"],
        pexels_queries=["badminton doubles match"],
    )

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
        "sources": "BAI, IANS, BWF",
        "image_url": img_url or "",
        "image_attribution": img_attr or "",
    }

    return insert_article(article)


# ── Article 2: India Women SAFF Championship semifinal ──────────────────────

def write_article_2():
    print("\n=== Article 2: India Women SAFF Championship semifinal win ===")

    headline = "Nongrum Scored in the 58th Minute. India Beat Bhutan 1-0. The Blue Tigresses Are in the SAFF Final."
    subheadline = "After scoring 14 goals in the group stage, India needed just one against a resolute Bhutan in the semifinal. Bangladesh await in Thursday's final at Margao."
    slug = "india-women-saff-championship-2026-semifinal-nongrum-bhutan-final-bangladesh-nri"

    body = """The numbers from the group stage told one story: 14 goals scored, zero conceded, three matches won with barely a contested moment. India's women had rolled through the 2026 SAFF Women's Championship like a side playing a different sport from the rest of the field.

The semifinal told a different story entirely.

## Bhutan Made India Work

At the Jawaharlal Nehru Stadium in Margao, Goa, on Wednesday evening, Bhutan did what no other team in the tournament had managed. They made India uncomfortable.

Head coach Crispin Chettri made two changes from the side that beat Bangladesh 3-0 in the final group match, bringing in Karishma Shirvoikar and Priyangka Devi Naorem for Pyari Xaxa and Sangita Basfore. India were expected to cruise. They did not.

Bhutan sat deep from the opening whistle, packing bodies behind the ball and denying India the space that had made the group stage so straightforward. India had most of the possession — that was never in doubt — but converting territory into chances, and chances into goals, proved far harder than it had been against the Maldives and Sri Lanka.

The first real opportunity came inside three minutes when Bhutan goalkeeper Sangita Monger fumbled a long ball, but Karishma's heavy first touch let defender Namgyel Dema clear. It set the tone: India would dominate, but finishing would be a problem.

## Nongrum Breaks the Deadlock

For nearly an hour, Bhutan held. The Indian attack probed, circulated, and pressed, but the final ball kept going astray. Soumya Guguloth lacked power on a first-time effort. Crosses found no one. Passes into the box were intercepted.

Then, in the 58th minute, Sanfida Nongrum found the breakthrough. The midfielder — not a regular starter in the group matches — finished from close range after India finally managed to carve open the Bhutan defense with a sequence of quick, incisive passes.

It was the only goal India would need, but it was the only goal they could manage. Final score: India 1, Bhutan 0.

## A Final Against Bangladesh

India will now face Bangladesh in the final on Thursday, June 5, at 18:30 IST in Margao. Bangladesh reached the final by edging out Nepal 2-1 in the other semifinal, with Ritu Porna Chakma equalizing in first-half stoppage time and an own goal from Nepal's Preeti Rai settling the contest in the 93rd minute.

Bangladesh are the defending champions, and they have improved significantly over the past two cycles. India beat them 3-0 in the group stage, but tournament finals are a different proposition entirely. Bangladesh will carry the confidence of a comeback win over Nepal, and they know that a tight, organized defensive effort — the kind Bhutan just demonstrated — can take India out of their comfort zone.

## What the Diaspora Should Know

For Indian women's football, the SAFF Championship is the most important regional title. India have won it four times, but they failed to reach the final in the last two editions — an unacceptable slide for a team that considers itself the dominant force in South Asian football.

This year's squad, under Chettri, has looked rejuvenated. Aveka Singh has been the tournament's top scorer with four goals. Priyangka Devi Naorem and Pyari Xaxa have added firepower from midfield. The defense, anchored by Grace Dangmei's versatility and organization, has been the tightest in the competition.

But the semifinal exposed a vulnerability. When opponents sit deep and deny space, India's ball circulation can become sterile. Against Bangladesh in a final, that patience will be tested again.

The match will be played in Margao — the heart of Indian football in many ways, a state where the sport runs deeper than almost anywhere else in the country. For NRI fans following from abroad, the stakes are straightforward: India need this title to reassert themselves as the team to beat in South Asia before a critical 2027 that includes the Asian Cup qualifiers.

One match. One title. One chance to prove the group-stage dominance was real.

*Sources: AIFF, LiveNewsGoa, SAFF Championship official records*"""

    # Image sourcing — try India women's football, then generic
    img_url, img_attr = best_image(
        person_names=["India women's national football team"],
        wiki_queries=["India women football team 2026", "Blue Tigresses India football", "SAFF Women's Championship"],
        pexels_queries=["women football match India"],
    )

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
        "sources": "AIFF, LiveNewsGoa, SAFF",
        "image_url": img_url or "",
        "image_attribution": img_attr or "",
    }

    return insert_article(article)


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ok1 = write_article_1()
    ok2 = write_article_2()

    total = sum([ok1, ok2])
    print(f"\n{'='*60}")
    print(f"Sports writer complete: {total}/2 articles published")
    if total == 0:
        sys.exit(1)
