#!/usr/bin/env python3
"""
The Videshi - Sports Writer (2026-05-29 evening run)
Publishes 3 fresh sports articles with NRI/diaspora angle.
"""

import json, os, sys, time, uuid, re, subprocess
import requests, urllib.parse
from datetime import datetime, timezone

# ── env ──
for env_file in [os.path.expanduser("~/.env.supabase"), os.path.expanduser("~/workspace/.env.pexels")]:
    if os.path.exists(env_file):
        for line in open(env_file):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ── helpers ──

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Verify image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent": "TheVideshi/1.0"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't give Content-Length
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True, headers={"User-Agent": "TheVideshi/1.0"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except:
        pass
    # Final attempt: just try GET
    try:
        r = requests.get(url, timeout=10, stream=True, headers={"User-Agent": "TheVideshi/1.0"})
        if r.status_code == 200:
            ct = r.headers.get("Content-Type", "")
            if "image" in ct:
                chunk = r.raw.read(6000)
                if len(chunk) > 5000:
                    return True
    except:
        pass
    return False


def sb_insert(table, data):
    """Insert a row into Supabase."""
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    print(f"  ✗ Insert error ({r.status_code}): {r.text[:200]}")
    return None


def sb_patch(table, filters, data):
    """Update rows in Supabase."""
    params = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{params}", headers=HEADERS, json=data)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch error ({r.status_code}): {r.text[:200]}")
    return False


def generate_article_with_ai(topic, context, existing_headlines):
    """Use OpenAI to generate article content."""
    if not OPENAI_KEY:
        print("  ⚠ No OpenAI API key, writing manually")
        return None
    
    prompt = f"""You are a senior sports journalist at The Videshi, an Indian diaspora news platform for NRIs in the US, UK, and Canada.

Write a sports article about: {topic}

Context/facts to use:
{context}

RULES:
- 600-800 words
- Economist-style writing: clean prose, strong opening, analytical depth
- Must include a DIASPORA/NRI angle (how this affects fans abroad, time zones, streaming, cultural significance)
- Structure: Lead paragraph → Context & Background → Current Developments → Diaspora Impact → What's Next
- Use markdown format (not HTML)
- Include **bold** for key names on first mention
- Subheadline is mandatory and should be at least 15 characters
- Headline should be short, punchy, declarative (under 200 chars)
- At least 2-3 real source references
- Category must be "sports" (lowercase)
- Do NOT duplicate these existing headlines: {json.dumps(existing_headlines[:15])}

Return ONLY a JSON object with these fields:
- headline (string, under 200 chars)
- subheadline (string, at least 15 chars)  
- body (string, markdown, 600-800 words)
- slug (string, lowercase-hyphenated, human-readable, append -20260529)
- sources (array of objects with "name" and "url" fields, at least 2)
- image_search_person (string or null - primary person name for Wikipedia image)
- image_search_pexels (string or null - Pexels search query if no person)
"""

    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 3000,
                "response_format": {"type": "json_object"}
            },
            timeout=120
        )
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        else:
            print(f"  ✗ OpenAI error ({r.status_code}): {r.text[:200]}")
    except Exception as e:
        print(f"  ✗ OpenAI exception: {e}")
    return None


# ── Article definitions ──

ARTICLES = [
    {
        "topic": "IPL 2026 Final: RCB vs GT in Ahmedabad on Sunday - Complete NRI Viewing Guide",
        "context": """
- IPL 2026 Final: Royal Challengers Bengaluru (RCB) vs Gujarat Titans (GT) on Sunday May 31 at Narendra Modi Stadium, Ahmedabad
- RCB are defending champions, beat GT by 92 runs in Qualifier 1; GT bounced back to beat RR by 7 wickets in Qualifier 2
- Shubman Gill scored 104 off 53 balls in Q2; Sai Sudharsan made 58; 167-run opening partnership
- RCB's Rajat Patidar scored 93* in Q1; Virat Kohli captains; Josh Hazlewood, Jacob Duffy in bowling
- GT: Gill, Sudharsan, Buttler, Rashid Khan, Kagiso Rabada, Mohammed Siraj
- Narendra Modi Stadium capacity: 132,000 - largest cricket stadium in the world
- Match starts at 7:30 PM IST = 10:00 AM ET / 7:00 AM PT / 3:00 PM BST / 10:00 PM GST
- Streaming in US: Willow TV/JioCinema; UK: Sky Sports/JioCinema; Canada: Willow TV
- GT won IPL 2022 in their debut season at this same venue; RCB won their first-ever title in 2025
- Kohli's RCB vs Gill's GT — a generational clash of Indian batting
- Bay Area, NYC, Toronto, London watch parties expected at Indian restaurants and community centers
- RCB have won the title once (2025); GT once (2022) — both relatively new champions
""",
        "primary_person": "Virat Kohli",
        "backup_person": "Shubman Gill",
        "pexels_query": "cricket stadium India night"
    },
    {
        "topic": "Rashid Khan Had the Worst T20 Night of His Career. Gujarat Titans Still Won Comfortably.",
        "context": """
- In IPL 2026 Qualifier 2 (GT vs RR, May 29), Rashid Khan bowled 2 overs for 0/45 — worst economy (22.5) in his entire 524-innings T20 career
- Donovan Ferreira smashed Rashid for 4 sixes in the final over (27 runs in the over)
- This is the joint-most expensive over by a spinner in IPL playoffs history (equalling Ravi Bishnoi's 27 in 2022)
- Rashid's previous worst economy was 18.00 vs LSG in IPL 2025 (0/36 in 2 overs)
- Despite Rashid's nightmare, GT won by 7 wickets chasing 215, with Gill's 104 and Sudharsan's 58
- Earlier in IPL 2026 season, Rashid was effective: 3/27 vs CSK, key spells in league stage
- Anil Kumble had warned before IPL 2026: "The novelty of Rashid Khan has worn off a little"
- Rashid had back surgery in 2023, struggled in IPL 2025 (9 wickets in 15 matches, 9.35 economy)
- Afghan-origin cricketer, one of the most popular players in the IPL
- GT still reach the final — showing their batting depth makes them less Rashid-dependent
- In IPL 2022 final (also vs RCB), Rashid was key with both bat and ball
- Vaibhav Sooryavanshi (96 off 47) and Riyan Parag also hit him for sixes
""",
        "primary_person": "Rashid Khan (cricketer)",
        "backup_person": "Rashid Khan",
        "pexels_query": "cricket spinner bowling"
    },
    {
        "topic": "India Women's Cricket: 2nd T20I Against England in Bristol Tomorrow as World Cup Prep Intensifies",
        "context": """
- India Women beat England by 38 runs in the 1st T20I at Chelmsford on May 28
- India scored 188/7 in 20 overs; England were bowled out for 150/8
- Smriti Mandhana captaining in place of Harmanpreet Kaur (who is resting/managing workload)
- 2nd T20I is Saturday May 30 at County Ground, Bristol (starts 6:30 AM PDT / 2:30 PM BST / 7:00 PM IST)
- This is a 3-match T20I series (3rd T20I on June 2)
- Women's T20 World Cup 2026 starts in England in ~2 weeks (June 12-29)
- India vs Pakistan at T20 World Cup on June 14 in Birmingham
- India are building squad depth and momentum ahead of the World Cup
- Series is a dress rehearsal: playing in England conditions right before a World Cup hosted in England
- Key players: Smriti Mandhana, Jemimah Rodrigues, Deepti Sharma, Renuka Singh
- This is India's first bilateral T20I series win chance in England in the T20 era
- For NRIs in UK, this is a rare chance to watch India Women live at affordable ticket prices
- For US/Canada NRIs, morning viewing times work well (6:30 AM PT / 9:30 AM ET)
""",
        "primary_person": "Smriti Mandhana",
        "backup_person": None,
        "pexels_query": "women cricket India match"
    }
]

# ── Main ──

def main():
    print("=" * 60)
    print("The Videshi Sports Writer — 2026-05-29 Evening Run")
    print("=" * 60)

    # Get existing headlines for dedup
    existing = []
    try:
        r = requests.get(
            f"{SB_URL}/rest/v1/p2_articles?select=headline,slug&status=eq.published&published_at=gte.2026-05-27T00:00:00Z&category=eq.sports&order=published_at.desc&limit=30",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"}
        )
        if r.status_code == 200:
            existing = [a["headline"] for a in r.json()]
            print(f"Found {len(existing)} existing sports articles in last 3 days")
    except Exception as e:
        print(f"Warning: Could not fetch existing articles: {e}")

    published_count = 0

    for i, article_def in enumerate(ARTICLES):
        print(f"\n{'─' * 50}")
        print(f"Article {i+1}/{len(ARTICLES)}: {article_def['topic'][:80]}...")
        print(f"{'─' * 50}")

        # 1. Generate article content with AI
        result = generate_article_with_ai(article_def["topic"], article_def["context"], existing)
        if not result:
            print(f"  ✗ Failed to generate article content, skipping")
            continue

        headline = result.get("headline", "")
        subheadline = result.get("subheadline", "")
        body = result.get("body", "")
        slug = result.get("slug", "")
        sources = result.get("sources", [])

        # Validate
        if len(headline) < 20 or len(headline) > 200:
            print(f"  ⚠ Headline length issue ({len(headline)} chars): {headline[:60]}")
        if len(subheadline) < 15:
            print(f"  ⚠ Subheadline too short: {subheadline}")
            subheadline = result.get("subheadline", headline)
        if len(body) < 400:
            print(f"  ✗ Body too short ({len(body)} chars), skipping")
            continue
        if not slug or len(slug) < 10:
            slug = re.sub(r'[^a-z0-9]+', '-', headline.lower().strip())[:80].strip('-') + "-20260529"

        # Ensure slug ends with date
        if not slug.endswith("-20260529"):
            slug = slug.rstrip("-") + "-20260529"

        print(f"  Headline: {headline}")
        print(f"  Slug: {slug}")
        print(f"  Body length: {len(body)} chars, ~{len(body.split())} words")

        # 2. Image sourcing — Wikipedia first for person articles
        image_url = None
        image_attribution = None

        person = article_def.get("primary_person")
        if person:
            print(f"  Fetching Wikipedia image for: {person}")
            image_url = fetch_wikipedia_person_image(person)
            if image_url:
                image_attribution = "Wikimedia Commons"

        if not image_url and article_def.get("backup_person"):
            print(f"  Trying backup person: {article_def['backup_person']}")
            image_url = fetch_wikipedia_person_image(article_def["backup_person"])
            if image_url:
                image_attribution = "Wikimedia Commons"

        if not image_url and article_def.get("pexels_query"):
            print(f"  Falling back to Pexels: {article_def['pexels_query']}")
            image_url = fetch_pexels_image(article_def["pexels_query"])
            if image_url:
                image_attribution = "Pexels"

        # Validate image
        if image_url:
            if validate_image(image_url):
                print(f"  ✓ Image validated: {image_url[:80]}...")
            else:
                print(f"  ✗ Image validation failed, trying without image")
                image_url = None

        # Check for banned image sources
        if image_url:
            banned_patterns = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
            for bp in banned_patterns:
                if bp in image_url:
                    print(f"  ✗ BANNED image source detected ({bp}), removing")
                    image_url = None
                    break

        # 3. Publish to Supabase
        now_iso = datetime.now(timezone.utc).isoformat()
        article_id = str(uuid.uuid4())

        article_data = {
            "id": article_id,
            "headline": headline,
            "subheadline": subheadline,
            "body": body,
            "slug": slug,
            "category": "sports",
            "vertical": "sports",
            "status": "published",
            "published_at": now_iso,
            "sources": json.dumps(sources) if isinstance(sources, list) else sources,
            "image_attribution": image_attribution or "The Videshi"
        }

        if image_url:
            article_data["image_url"] = image_url

        result_row = sb_insert("p2_articles", article_data)
        if result_row:
            print(f"  ✓ PUBLISHED: {headline}")
            print(f"    ID: {article_id}")
            print(f"    Image: {'yes' if image_url else 'no'}")
            published_count += 1
            existing.append(headline)
        else:
            print(f"  ✗ FAILED to publish: {headline}")

        # Brief pause between articles
        time.sleep(2)

    print(f"\n{'=' * 60}")
    print(f"Sports Writer Complete: {published_count}/{len(ARTICLES)} articles published")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
