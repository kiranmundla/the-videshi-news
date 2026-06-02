#!/usr/bin/env python3
"""
The Videshi — Sports Writer (2026-06-02)
Generates 3 sports articles with Wikipedia-first image sourcing.
"""

import json, os, sys, time, uuid, re, urllib.parse
import requests
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                k, v = line.split('=', 1)
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY   = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}

# ── image helpers ────────────────────────────────────────────────────
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
    """Fetch an image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Check URL returns a valid image."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Some servers don't return content-length on HEAD
        if r.status_code == 200 and 'image' in ct:
            return True
    except:
        pass
    return False

def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(image_url, timeout=15,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed or too small: {len(r.content)} bytes")
            return None
        
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            content_type = 'image/jpeg'
        
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': content_type,
                'x-upsert': 'true',
            },
            data=r.content,
            timeout=20,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({resp.status_code}): {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

def source_image(person_name=None, pexels_query=None, pexels_fallback=None, article_id=None):
    """Source image following hierarchy: Wikipedia → Pexels → None."""
    attribution = None
    url = None
    
    if person_name:
        url = fetch_wikipedia_person_image(person_name)
        if url:
            attribution = "Wikimedia Commons"
    
    if not url and pexels_query:
        url = fetch_pexels_image(pexels_query, pexels_fallback)
        if url:
            attribution = "Pexels"
    
    if url and article_id:
        # Upload to Supabase for permanence
        ext = 'jpg'
        filename = f"{article_id}.{ext}"
        final_url = upload_to_supabase_storage(url, filename)
        if final_url:
            return final_url, attribution
        # If upload fails, check if original is permanent
        if 'upload.wikimedia.org' in url or 'images.pexels.com' in url:
            return url, attribution
    
    if url:
        return url, attribution
    
    return None, None

# ── Supabase insert ──────────────────────────────────────────────────
def insert_article(article):
    """Insert an article into p2_articles."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=20)
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            return data[0].get('id')
        return True
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:800]}")
    return None

def patch_article(article_id, patch):
    """Patch an existing article."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    r = requests.patch(url, headers=HEADERS, json=patch, timeout=15)
    return r.status_code in (200, 204)

# ── Articles ─────────────────────────────────────────────────────────

ARTICLES = []

# ━━━ ARTICLE 1: Bhuvneshwar Kumar IPL 2026 Revival ━━━
ARTICLES.append({
    "headline": "He Was Written Off at Thirty-Four. At Thirty-Six, He Took More Wickets Than Any Indian Pacer in a Single IPL Season.",
    "subheadline": "Bhuvneshwar Kumar's reinvention at RCB — wobbly seam, relentless discipline, and 28 wickets — has forced India's selectors into a debate they thought was settled four years ago.",
    "slug": "bhuvneshwar-kumar-ipl-2026-revival-28-wickets-rcb-india-comeback-debate-nri",
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "is_editorial": False,
    "is_featured": False,
    "tags": [],
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps(["CricketAddictor", "InsideSport India", "RevSportz", "CricTracker", "Yardbarker"]),
    "image_person": "Bhuvneshwar Kumar",
    "pexels_query": "cricket fast bowler",
    "pexels_fallback": "cricket bowling action",
    "body": """Three years ago, Bhuvneshwar Kumar looked finished. His pace had dropped below 130 kph. His economy rates in IPL 2023 and 2024 — 9.35 and 9.28 respectively — were the worst of his career. SunRisers Hyderabad, the franchise he had served for a decade, let him go. When Royal Challengers Bengaluru picked him up at the 2025 mega auction, eyebrows went up across the cricketing world.

At thirty-six, in a format that devours aging pacers, Bhuvneshwar Kumar has answered every sceptic with the most prolific season of his career.

## The Numbers That Silenced the Doubters

In IPL 2026, Bhuvneshwar finished with 28 wickets from 16 matches at an average of 17.89 and an economy of 7.95. That is the most wickets ever taken by an Indian fast bowler in a single edition of the IPL. He joins Lasith Malinga, Kagiso Rabada, and Jasprit Bumrah as only the fourth pacer to record four individual 20-wicket IPL seasons, and alongside Dwayne Bravo, he is one of just two pacers to register multiple 25-wicket hauls.

His best spell — 4/23 against Mumbai Indians — was a masterclass in seam movement and death-over execution. In the IPL 2026 final against Gujarat Titans, he returned figures of 2/29 in four overs, dismissing Sai Sudharsan in the powerplay and Jason Holder in the death overs. RCB restricted GT to 155/8 and won by five wickets to complete a historic back-to-back title defence.

## Sachin Decoded the Secret

Sachin Tendulkar, analysing Bhuvneshwar's transformation on social media, identified the key change: the wobbly seam.

"This season, if you look at Bhuvi's seam, it is a wobbly seam," Tendulkar said. "When a wobbly seam comes, a batsman often doesn't know whether the ball is going to fall out or in. And that is what Bhuvi has been doing."

Tendulkar explained that in previous seasons, Bhuvneshwar relied on conventional outswingers and inswingers with a clearly visible seam position. In 2026, he made a deliberate technical shift — bowling as straight as possible with a scrambled seam, making the ball deviate unpredictably off the surface. It is a variation more commonly associated with English county cricket, and Bhuvneshwar has weaponised it for T20s.

## The India Debate

BCCI Vice-President Rajeev Shukla, speaking hours after the final, hailed Bhuvneshwar's "amazing revival" and called his season "nothing short of extraordinary." Former India off-spinner Ravichandran Ashwin went further, suggesting Bhuvneshwar — not Virat Kohli — deserved the Player of the Match award in the final.

The calls for an India comeback are growing louder. Bhuvneshwar has not played international cricket since 2022. But his IPL 2026 numbers are hard to ignore: he is now the most-capped fast bowler in IPL history with 205 matches and 762.4 overs bowled, more than Bumrah.

Yet Bhuvneshwar himself refuses to chase it.

"I'm not thinking about any India comeback," he said after the final. "It's been so many years now since I stopped setting long-term goals because whenever I set them, they didn't really work for me. I am just happy that I have played 200 matches and have taken so many wickets at the powerplay and at the death."

## The Diaspora Angle

For NRI cricket fans who grew up watching Bhuvneshwar's swing bowling in the 2013 Champions Trophy and 2017 Champions Trophy, his revival is more than a statistical anomaly. It is a story of reinvention — of a cricketer who lost his pace, lost his place, and found an entirely new way to be dangerous.

At thirty-six, in a league that discards fast bowlers like used match balls, Bhuvneshwar Kumar has 28 wickets, two IPL titles with RCB, and a debate he never asked for raging around his name.

The selectors will pick squads for the England tour later this summer. Whether Bhuvneshwar's name is on the list may depend less on his own ambitions and more on whether India can afford to ignore the best Indian pacer of the 2026 IPL.

*Sources: CricketAddictor, InsideSport India, RevSportz, CricTracker, Yardbarker*"""
})

# ━━━ ARTICLE 2: ISL Crisis — 150 Players Out of Contract ━━━
ARTICLES.append({
    "headline": "One Hundred and Fifty Players. No Contracts. The ISL's Off-Season Has Become an Existential Crisis.",
    "subheadline": "As 150 Indian Super League players enter free agency without new deals, a commercial rights dispute between clubs and the AIFF has left Indian football's top division in limbo — and families across the northeast are feeling it first.",
    "slug": "isl-crisis-150-players-out-of-contract-commercial-rights-dispute-aiff-2026-nri",
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "is_editorial": False,
    "is_featured": False,
    "tags": [],
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps(["Mykhel/PTI", "Wikipedia - 2025-26 ISL", "Bhaskar English", "RevSportz"]),
    "image_person": None,
    "pexels_query": "Indian football stadium fans",
    "pexels_fallback": "football empty stadium",
    "body": """The 2025-26 Indian Super League season ended on May 21 with East Bengal FC lifting their first national title in twenty-two years. By June 2, the celebration had given way to a crisis that threatens the very structure of Indian professional football.

One hundred and fifty ISL players are now out of contract. The league has no confirmed commercial partner for next season. And a bitter dispute between the clubs and the All India Football Federation over revenue-sharing has left the country's top football division without a clear path forward.

## The Contract Vacuum

When the ISL season ended, clubs were expected to move quickly on renewals and new signings. Instead, many have stalled. The reason is simple: nobody knows what the league will look like next season, or how much money will be available.

A senior ISL club official, quoted by PTI, laid out the scale of the problem. "The players are the biggest sufferers," the official said. Free agency, normally a lever of player power, has become a trap. Without clarity on budgets, clubs are offering lower fees. Transfer fees that would normally flow between clubs are drying up. For many players, the phone has simply stopped ringing.

The official flagged a particularly painful dimension. Many ISL players come from India's northeast — from Manipur, Mizoram, and surrounding states. For these players, an ISL contract is not just a career; it is the primary income for entire households. The uncertainty is hitting these families hardest.

## The Commercial Rights Standoff

At the root of the crisis is an unresolved battle over the ISL's commercial future.

The previous commercial partner, Football Sports Development Limited, ended its Master Rights Agreement with the AIFF in December 2025. The 2025-26 season was delayed for months and only began in February 2026 after Supreme Court intervention and direct involvement by Sports Minister Mansukh Mandaviya. The truncated season featured just 91 matches in a single-leg format, a fraction of the league's usual scale.

A new bidding process attracted Genius Sports as the top bidder in March, offering Rs 2,129 crore per year on a 15-plus-5 year deal. But ISL clubs have balked at the terms. They want Genius confined to a data and technology partnership, not a full commercial partnership. Instead, the clubs are proposing a radical restructuring: they want to keep 90 per cent of the league's economic interest, with the AIFF holding the remaining share.

A meeting between club representatives and AIFF leadership in Kolkata last month ended without agreement. A Special General Body Meeting decided that the Executive Committee would study fresh offers, but any final decision on a commercial partner must be taken by the full AIFF General Body. That meeting has not been scheduled.

## What It Means for Indian Football

The ISL was supposed to be the vehicle that professionalised Indian football. Launched in 2014, it attracted global stars, built stadiums, and created a generation of Indian players who could earn a living from the sport. At its peak, it featured clubs backed by some of India's wealthiest business houses — the Ambanis, the Jindals, the Tatas.

Now the league finds itself in a situation where its own players cannot get contracts, its clubs cannot plan budgets, and its governing body cannot agree on who should sell the product.

For the 150 players currently in limbo, the stakes are immediate. Pre-season training typically begins in August. If the commercial dispute is not resolved by then, there may be no season to train for.

## The NRI Perspective

For Indian diaspora football fans — particularly those who follow the ISL through FanCode from the US, UK, and the Middle East — the crisis is a reminder of how fragile Indian football's infrastructure remains. While the BCCI's IPL generated Rs 5,761 crore in revenue last financial year, the ISL's entire media rights deal for 2025-26 was worth Rs 8.62 crore. The gap is not just financial; it is institutional.

The FIFA World Cup begins in North America on June 11. Indian football will not be represented on the pitch. The question now is whether it will even have a functioning top division by the time the tournament ends.

*Sources: Mykhel/PTI, Wikipedia (2025-26 ISL season), Bhaskar English, RevSportz*"""
})

# ━━━ ARTICLE 3: India Football — Unity Cup Disaster + Tajikistan ━━━
ARTICLES.append({
    "headline": "Zero Goals. Two Defeats. India's Blue Tigers Left London Without Scoring. Now They Head to Tajikistan.",
    "subheadline": "India's Unity Cup campaign ended in embarrassment — no goals in two matches — and Khalid Jamil's squad now faces two friendlies in Tajikistan with star forward Ryan Williams ruled out.",
    "slug": "india-blue-tigers-unity-cup-goalless-tajikistan-friendlies-june-2026-nri",
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "is_editorial": False,
    "is_featured": False,
    "tags": [],
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps(["AIFF Official", "KhelNow", "Yardbarker", "IANS"]),
    "image_person": None,
    "pexels_query": "India football national team",
    "pexels_fallback": "football soccer match action",
    "body": """The Indian men's national football team left London at the weekend having played two matches, lost both, and scored zero goals. It was, by any measure, a dismal showing — and it came barely two weeks before the FIFA World Cup begins in their diaspora backyard across North America.

India's Unity Cup 2026 campaign started with hope. The four-team tournament at The Valley — home of Charlton Athletic — was the Blue Tigers' first match on British soil since 2002. They arrived with a 22-player squad assembled by head coach Khalid Jamil, though Mohun Bagan Super Giant's last-minute decision to recall their players hours before departure forced the AIFF into a frantic scramble to fly in replacements.

## Jamaica: 0-2

The semi-final against Jamaica on May 28 exposed India's limitations. Ranked 71st in the world — sixty-five places above India's 136th — Jamaica controlled the game comfortably. Two goals were enough. India rarely threatened.

## Zimbabwe: 0-1

Three days later, facing 130th-ranked Zimbabwe in the third-place playoff, Khalid Jamil made four changes. Vikram Partap Singh, Rahim Ali, Macarton Nickson, and Ricky Shabong all started. Shabong, who had made his international debut as a substitute against Jamaica, produced the best Indian moment of the tournament in the 29th minute — a perfectly weighted ball over the Zimbabwe defence for Vikram Partap Singh, who seemed certain to score until Zimbabwe captain John Takwara executed a stunning sliding challenge.

Four minutes later, Farukh Choudhary crashed into Washington Gift Navaya inside the box. The referee pointed to the spot. Prince Dube converted. India spent the rest of the match chasing an equaliser that never came.

The final record: two matches, two defeats, zero goals scored, three conceded.

## Tajikistan Is Next

There is no time to regroup at home. The Blue Tigers fly directly from London to Tajikistan for two international friendlies during the June FIFA window. The matches are scheduled for June 5 and June 9 at the Hisor Central Stadium, with both games kicking off at 20:30 IST.

The squad will be largely the same, but India have suffered a significant blow: star forward Ryan Williams has been ruled out with an injury. Williams has quickly established himself as a key figure in Khalid Jamil's attacking setup, and his absence will be keenly felt against a Tajikistan side playing at home.

## What the World Cup Window Means

The timing is pointed. The 2026 FIFA World Cup kicks off on June 11 in Mexico, the United States, and Canada — the three countries with the largest Indian diaspora populations outside the subcontinent. NRI fans will be surrounded by World Cup fever while their national team plays friendlies in Central Asia against teams ranked within twenty places of them.

India's 136th FIFA ranking means they are not remotely close to World Cup qualification. But friendlies like these are supposed to be the building blocks — opportunities to develop combinations, blood young players, and build a competitive identity.

The Unity Cup showed how far India still has to go. A squad weakened by Mohun Bagan's withdrawal, a formation that could not create chances, and a forward line that could not find the net — these are structural problems, not one-off results.

## The Bigger Picture

Indian football is at a crossroads that extends well beyond results on the pitch. The ISL, the country's top football league, is embroiled in a commercial rights dispute that has left 150 players without contracts. The domestic calendar remains fragmented. The pathway from youth football to the senior national team is underdeveloped compared to cricketing infrastructure.

For NRI fans planning to attend World Cup matches in New York, Dallas, Houston, and Los Angeles, the tournament will be a celebration of global football. For Indian football specifically, it will be a reminder of the distance still to travel.

Khalid Jamil has two matches in Tajikistan to start closing that gap. The question is whether a goalless squad can find its voice in Hisor.

*Sources: AIFF Official, KhelNow, Yardbarker, IANS*"""
})

# ── Main execution ───────────────────────────────────────────────────
def main():
    print(f"\n{'='*60}")
    print(f"  The Videshi Sports Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}\n")
    
    success_count = 0
    
    for i, article in enumerate(ARTICLES):
        print(f"\n── Article {i+1}/{len(ARTICLES)}: {article['headline'][:70]}...")
        
        # Extract image sourcing params
        person_name = article.pop("image_person", None)
        pexels_query = article.pop("pexels_query", None)
        pexels_fallback = article.pop("pexels_fallback", None)
        
        # Generate article ID
        article_id = str(uuid.uuid4())
        article["id"] = article_id
        
        # Source image
        print(f"  Sourcing image...")
        img_url, attribution = source_image(
            person_name=person_name,
            pexels_query=pexels_query,
            pexels_fallback=pexels_fallback,
            article_id=article_id,
        )
        
        if img_url:
            article["image_url"] = img_url
            article["image_attribution"] = attribution or "The Videshi"
            print(f"  ✓ Image set")
        else:
            print(f"  ⚠ No image found — publishing without image")
        
        # Insert
        print(f"  Inserting article...")
        result = insert_article(article)
        if result:
            print(f"  ✓ Published: {article['slug']}")
            success_count += 1
        else:
            print(f"  ✗ FAILED to publish")
        
        time.sleep(1)  # Be kind to Supabase
    
    print(f"\n{'='*60}")
    print(f"  Done. {success_count}/{len(ARTICLES)} articles published.")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
