#!/usr/bin/env python3
"""
Entertainment article: Guru Randhawa gym shooting by Bishnoi gang
"""

import os, json, requests, uuid
from datetime import datetime, timezone

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                k = k.replace('export ', '').strip()
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/.env.supabase'))

SB_URL = os.environ.get('SUPABASE_URL', '')
SB_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')

def sb_headers():
    return {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def insert_article(article):
    url = f"{SB_URL}/rest/v1/p2_articles"
    r = requests.post(url, json=article, headers=sb_headers(), timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) else data.get('id')
        print(f"  ✓ Inserted article: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:500]}")
        return None

slug = "guru-randhawa-gym-shooting-bishnoi-gang-boompala-20260612"

headline = "Seven Bullets Hit Guru Randhawa's Delhi Gym. Five Days Earlier, He Made K-Pop History."

subheadline = "The Bishnoi gang's latest message targets Bollywood's favourite Punjabi hitmaker — and the industry's growing fear of proximity to Salman Khan."

body = """Five days ago, Guru Randhawa was celebrating the biggest crossover of his career — a global remix of LE SSERAFIM's viral hit "BOOMPALA," his first K-pop collaboration, already racking up millions of streams across continents. On Wednesday night, two men on a motorcycle pulled up to his Delhi gym franchise and fired seven rounds into the glass facade.

The message, posted to social media shortly after by Bishnoi gang operative Anil Pandit, was chillingly direct: "We targeted Guru Randhawa's gym in Delhi as he was getting very close to Salman Khan."

No one was hurt. The 24HS Fitness outlet in Paschim Vihar's Pushkar Enclave was closed at 4 AM when the shots rang out. A caretaker discovered shattered glass and bullet pockmarks at 5:15 AM and called the police. But in an industry that's spent the better part of a decade watching the Bishnoi gang turn its grudge against one actor into a sprawling campaign of intimidation, the absence of casualties is cold comfort.

## The Salman Khan Orbit

The Bishnoi-Salman Khan feud is the entertainment industry's longest-running background threat. It traces back to a 1998 blackbuck poaching case in Rajasthan, where the actor was convicted of killing two animals considered sacred by the Bishnoi community. A Jodhpur court sentenced him to five years in 2018; he was granted bail and continues to challenge the conviction.

What began as a legal dispute has metastasised into something far more dangerous. The gang, now operating through a network of handlers based in the US, Canada, and Europe, has systematically expanded its list of targets to include anyone perceived as close to Salman. Guru Randhawa — who has been photographed with the actor at Bollywood events and whose music career increasingly intersects with the Hindi film industry — apparently crossed that invisible line.

The gym itself tells a more nuanced story than the gang's statement suggests. According to Delhi Police, the 24HS Fitness franchise in Paschim Vihar is actually owned by two businessmen from Rajouri Garden. Randhawa serves as its brand ambassador, not its proprietor. The outlet opened just this February. Police have registered a case under the Bharatiya Nyaya Sanhita and the Arms Act and are examining CCTV footage from surrounding streets — the shooting, strategically, occurred just outside the gym's own camera range.

Investigators are pursuing multiple angles, including standard extortion, gang rivalry, and the celebrity connection. The pattern is familiar: a high-profile name attached to a business creates a soft target for gangs looking to make headlines with minimal risk.

## A Pattern That's Gone Global

What makes the Randhawa shooting especially unnerving for diaspora audiences is how neatly it fits into a pattern that has already crossed international borders. Kapil Sharma's Kap's Cafe in Surrey, British Columbia, has been targeted in four separate shooting incidents since July 2025 — the most recent in May 2026, when the gang warned the comedian to "fall in line." That same month, shots were fired at the Haryana home of Diljit Dosanjh's manager, with the gang claiming responsibility on social media.

For NRIs who grew up on these artists' music, who attend their concerts in Toronto and Houston and London, who tag their reels with #GuruRandhawa, the message lands differently than it does in a Delhi police report. The threats that once seemed confined to Mumbai's underworld now follow Indian entertainers — and their businesses — across oceans.

## BOOMPALA and the Whiplash of Two Headlines

The timing borders on cinematic. On June 6, Guru Randhawa released the "BOOMPALA" remix with K-pop group LE SSERAFIM — a landmark collaboration marking the first time the group worked with an Indian artist. The original track had already amassed over 18 million Spotify streams and 10 million YouTube views in its first four days; the Randhawa version, weaving Punjabi lyrics alongside Korean, English, and Spanish, positioned him as a genuinely global hitmaker. Warner Music India facilitated the partnership; Randhawa had already built international bridges with Pitbull, Jay Sean, The Chainsmokers, and Rick Ross.

"LE SSERAFIM is incredible, and 'BOOMPALA' has an infectious energy that reminds me of the massive, celebratory vibe we love in India," Randhawa said days before the attack.

Now, the same week that proved Guru Randhawa can sell records across continents, he's learned that the Bishnoi gang can reach him across Delhi — and that, in Bollywood's grimly expanding map of collateral damage, being friends with the wrong person still carries a price.

Delhi Police confirmed the investigation is ongoing. The gym remains temporarily closed. Randhawa has not issued a public statement.

*Sources: Bollywood Hungama, The Daily Jagran, Dainik Bhaskar, LatestLY*"""

article = {
    "id": str(uuid.uuid4()),
    "headline": headline,
    "subheadline": subheadline,
    "body": body,
    "slug": slug,
    "category": "entertainment",
    "vertical": "entertainment",
    "is_editorial": False,
    "status": "review",
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
        {"name": "The Daily Jagran", "url": "https://www.thedailyjagran.com"},
        {"name": "Dainik Bhaskar English", "url": "https://www.bhaskarenglish.in"},
        {"name": "LatestLY", "url": "https://www.latestly.com"}
    ]),
    "published_at": datetime.now(timezone.utc).isoformat(),
    "created_at": datetime.now(timezone.utc).isoformat()
}

print(f"\n═══ Guru Randhawa Gym Shooting Article ═══")
print(f"  Headline: {headline[:80]}...")
print(f"  Slug: {slug}")
print(f"  Word count: {len(body.split())}")

art_id = insert_article(article)
if art_id:
    print(f"\n  ✅ Article published! ID: {art_id}")
    print(f"  Next: run source-image.py --article-id {art_id}")
else:
    print(f"\n  ❌ Failed to insert article")
