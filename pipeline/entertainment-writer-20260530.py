#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-30 evening batch"""

import json, os, sys, time, uuid, re, urllib.parse
import requests
from datetime import datetime, timezone

# ── Supabase config ──────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Pexels config ────────────────────────────────────────────────────
PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
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
    """Fetch an image from Pexels API using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key found")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                src = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if src:
                    print(f"  ✓ Pexels image found for '{q}': {src[:80]}...")
                    return src
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Validate that image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't support HEAD, try GET with range
        if r.status_code in (200, 405, 403):
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            ct2 = r2.headers.get("Content-Type", "")
            # Read first chunk to estimate size
            chunk = next(r2.iter_content(8192), b"")
            r2.close()
            if r2.status_code == 200 and "image" in ct2 and len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def sb_insert(table, row):
    """Insert a row into Supabase and return it."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=row,
    )
    if r.status_code in (200, 201):
        data = r.json()
        return data[0] if isinstance(data, list) else data
    else:
        print(f"  ✗ Insert {table} failed: {r.status_code} {r.text[:300]}")
        return None


def create_topic(title, category):
    """Create a topic in p2_topics and return its ID."""
    topic_id = str(uuid.uuid4())
    row = {
        "id": topic_id,
        "canonical_title": title[:200],
        "vertical": category,
        "urgency": "daily",
        "score_diaspora": 70,
        "score_significance": 65,
        "score_recency": 80,
        "score_source_avail": 60,
        "score_total": 70,
        "signal_count": 1,
        "status": "published",
        "keywords": title.split()[:5],
        "category": category,
    }
    result = sb_insert("p2_topics", row)
    if result:
        return topic_id
    return None


def sb_patch(table, match, patch):
    """Update rows in Supabase matching filter."""
    params = "&".join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=patch,
    )
    if r.status_code in (200, 204):
        print(f"  ✓ Patched {table}")
    else:
        print(f"  ✗ Patch {table} failed: {r.status_code} {r.text[:300]}")


# ── Articles ─────────────────────────────────────────────────────────
articles = [
    {
        "headline": "Vashu Bhagnani Just Filed a ₹400 Crore Lawsuit Over Two Songs. David Dhawan's Final Film Could Be Collateral Damage.",
        "subheadline": "The fight over 'Chunnari Chunnari' and 'Ishq Sona Hai' from Biwi No. 1 has escalated into one of Bollywood's biggest copyright battles — and it could delay the June 5 release of Hai Jawani Toh Ishq Hona Hai.",
        "slug": "vashu-bhagnani-400-crore-lawsuit-chunnari-chunnari-david-dhawan-hai-jawani-nri-20260530",
        "category": "entertainment",
        "person": "Vashu Bhagnani",
        "pexels_query": "Bollywood film courtroom legal",
        "pexels_fallback": "Indian court gavel law",
        "sources": json.dumps([
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
            {"name": "ANI", "url": "https://aninews.in"},
            {"name": "Zoom TV", "url": "https://www.zoomtventertainment.com"}
        ]),
        "body": """Bollywood's biggest copyright war just got a price tag.

Vashu Bhagnani's production company, Puja Entertainment, has filed a **₹400 crore lawsuit** in the Bombay High Court against Tips Industries Limited, its founders Ramesh and Kumar Taurani, and filmmaker David Dhawan. The suit alleges unauthorized use of two iconic songs — *Chunnari Chunnari* and *Ishq Sona Hai* — from Bhagnani's 1999 hit *Biwi No. 1* in the upcoming Varun Dhawan-starrer *Hai Jawani Toh Ishq Hona Hai*, which is set to release on June 5.

## What's Actually Being Fought Over

The dispute centers on the difference between audio rights and visual rights — a distinction that didn't matter much when Bollywood deals were handshake affairs in the 1990s, but now carries hundreds of crores in commercial value.

According to Bhagnani's legal counsel, V.K. Dubey Associates, the original agreement with Tips covered only audio rights. In 2018, Tips reportedly emailed Bhagnani requesting visual rights — the kind you'd need to, say, shoot a new movie sequence around an old song. Bhagnani responded, but the two sides never reached an agreement. Puja Entertainment has since sent a formal notice cancelling the audio rights previously granted to Tips, which the lawsuit argues means the songs cannot legally appear in the new film.

"If they are the lawful owners of the music rights, they must show their documents," Bhagnani's lawyer told ANI. "This is why we have filed a claim against Tips. Justice will prevail."

The suit seeks an immediate injunction to halt the release, distribution, streaming, and all commercial exploitation of *Hai Jawani Toh Ishq Hona Hai* — including any promotional material featuring the disputed songs.

## Why This Matters Beyond the Courtroom

This isn't just about two songs or one film. It's about how Bollywood's relationship with its own musical catalogue is being rewritten in real time.

For decades, song rights in Indian cinema existed in a grey zone. Producers sold audio rights to labels, which then controlled distribution on cassettes, CDs, and eventually streaming platforms. But those deals were drafted in an era when nobody could imagine a song being used to sell a *different* film two decades later. Now, with remixes and nostalgia-driven marketing becoming Bollywood's go-to playbook, the question of who actually owns what — and for what purpose — has become a multi-crore legal minefield.

The timing makes this even more significant. *Hai Jawani Toh Ishq Hona Hai* is David Dhawan's self-declared final film. The veteran comedy director, who gave Hindi cinema *Coolie No. 1*, *Hero No. 1*, and the original *Biwi No. 1*, is closing his career with a film starring his son Varun alongside Mrunal Thakur and Pooja Hegde. A court-ordered delay or injunction would cast a shadow over what was meant to be a celebratory farewell.

## The Diaspora Angle

For NRIs who grew up on *Chunnari Chunnari* — hearing it at every garba, every sangeet, every Indo-Canadian wedding reception — this lawsuit is a reminder of how the music that formed the soundtrack of diaspora childhoods is now a contested commodity. The songs may live rent-free in your head, but in a Bombay High Court filing, someone is putting a very precise number on their value.

Tips Industries has previously maintained that it holds lawful ownership of the songs. The court has accepted the filing and is expected to hear the case shortly. Whether it moves fast enough to impact the June 5 release remains the ₹400 crore question.

*The film is slated for a global theatrical release. A hearing date has not been publicly confirmed.*"""
    },
    {
        "headline": "Kirti Kulhari Questioned Paying ₹10,000 to Her Maid. The Internet Had Thoughts.",
        "subheadline": "A viral clip of the actress questioning her domestic worker's monthly salary triggered a nationwide debate on fair wages, class privilege, and what household labor is actually worth in urban India.",
        "slug": "kirti-kulhari-domestic-worker-salary-debate-mini-mathur-class-divide-nri-20260530",
        "category": "entertainment",
        "person": "Kirti Kulhari",
        "pexels_query": "Indian domestic worker household cleaning",
        "pexels_fallback": "cleaning home domestic help",
        "sources": json.dumps([
            {"name": "India Forums", "url": "https://www.indiaforums.com"},
            {"name": "Hauterrfly", "url": "https://hauterrfly.com"},
            {"name": "Jobaaj News", "url": "https://news.jobaaj.com"}
        ]),
        "body": """Kirti Kulhari didn't set out to start a national conversation about domestic labor. But that's exactly what happened.

In a recent interview with Bollywood Bubble, the *Pink* and *Four More Shots Please!* actress talked about moving to a new apartment on Yaari Road in Mumbai and being surprised by the salary quoted by a cook and maid. "For two hours of work — which includes sweeping, mopping, doing the dishes — I wanted that whatever could be done within those two hours, like dusting, laundry, all of it, would be taken care of," she explained. "She was charging me ₹10,000."

Kulhari went further: "I was like, you're coming in for two hours and only doing as much work as you feel like… and then you're charging me ₹10,000 for what? At that point, we were thinking, are they looking at us and assuming we must have money, so they might as well ask for more?"

The clip went viral. And then the rebuttals arrived.

## Mini Mathur Fires Back

Television host and actress Mini Mathur didn't mince words. In an Instagram Story response that was widely shared, Mathur argued that the domestic worker's two hours are what *enable* the employer's own productive hours — and that ₹10,000 is "below minimum wage anywhere in the world."

The math, Mathur and other commenters pointed out, isn't hard: a domestic worker earning ₹10,000 from one household while working two-hour shifts can serve maybe five homes. That's ₹50,000 a month for 10 hours of physically demanding daily labor — in a city where even a small room in a shared chawl can cost ₹15,000-20,000.

"Even if she works in 5 houses, she will be able to earn ₹50,000 per month by working 10 hours," one Instagram user wrote. "In a city like Mumbai, one needs at least ₹50,000 to live a respectable life. I don't think this is a wrong demand."

## The Bigger Picture

India has an estimated **50 million domestic workers**, the vast majority of whom are women from marginalized communities. They have no nationally binding minimum wage, no standardized working hours, and limited access to social security. The Domestic Workers (Regulation of Work and Social Security) Bill has been discussed since 2008 but remains unlegislated.

In this context, the question isn't really whether ₹10,000 for two hours of daily work is a lot. It's about who gets to define "a lot."

Kulhari's comment revealed a blind spot that isn't uniquely hers — it's embedded in the way urban, upper-middle-class India has historically valued household labor. The work is essential enough that most dual-income households can't function without it, yet it's consistently undervalued in compensation and social status.

## Why the Diaspora Is Watching

For NRIs, this debate hits differently. Many grew up in homes where domestic help was a given — the *bai* or *didi* who was part of the household fabric. Moving abroad, they discovered that the same services — cleaning, cooking, childcare — cost $25-$50 per hour in North America, often more.

The dissonance is real: paying ₹10,000 per month for daily household work that would cost $3,000-$4,000 monthly in the US or Canada feels, from a diaspora vantage point, not expensive but extraordinarily cheap.

This isn't about shaming Kulhari specifically. It's about a broader reckoning with the class assumptions baked into everyday life in India — assumptions that become visible precisely when someone says the quiet part out loud.

The debate, predictably, has already moved on to the next viral moment. But the 50 million workers at the center of it are still waiting for a law that recognizes their labor as work worthy of legal protection.

*Kulhari has not publicly responded to the backlash at the time of writing.*"""
    },
    {
        "headline": "Pooja Bhatt Called Bobby Deol 'A Magical Human Being.' Then She Said Why She'll Never Tell You What Went Wrong.",
        "subheadline": "In a rare and graceful interview, Pooja Bhatt revisited her 1990s romance with Bobby Deol — praising his Animal comeback while drawing a firm line on privacy that Bollywood could learn from.",
        "slug": "pooja-bhatt-bobby-deol-relationship-90s-breakup-dignity-animal-bollywood-nri-20260530",
        "category": "entertainment",
        "person": "Pooja Bhatt",
        "person_alt": "Bobby Deol",
        "pexels_query": None,
        "pexels_fallback": None,
        "sources": json.dumps([
            {"name": "MensXP", "url": "https://www.mensxp.com"},
            {"name": "BollywoodShaadis", "url": "https://www.bollywoodshaadis.com"},
            {"name": "Zoom TV", "url": "https://www.zoomtventertainment.com"}
        ]),
        "body": """In an industry that treats ex-relationships like content, Pooja Bhatt just delivered a masterclass in grace.

In a candid conversation with journalist Vickey Lalwani, the actress-producer opened up about her relationship with Bobby Deol — a romance that unfolded in the 1990s, when both were young, famous, and very much in the public eye. What she said was warm, generous, and unflinchingly private all at once.

"Of course," she said, when asked if she was deeply in love with him. "What's not to fall in love with? It was a magical time of my life, and he was a magical human being to be with."

Then came the line that set the tone for the entire exchange: "But I don't think it is in good taste to sit down today and talk about why my relationship with him ended."

## What She Said — and What She Didn't

Bhatt acknowledged the relationship openly, calling their time together "magical" and Bobby "a magical human being." But she refused to narrate the ending. "It worked till it didn't work. That's it."

She offered no blame, no veiled accusations, no coded references. Instead, she centered something Bollywood gossip culture rarely allows for: the dignity of the other person's present life.

"He is a married man today, father of grown-up children, and is enjoying a wonderful new surge in his career," she said. "I loved him in *Animal*. For me, he made the film. I'm so happy for him."

That last line carried weight. Bobby Deol's performance as Abrar in Sandeep Reddy Vanga's *Animal* (2023) was widely considered his career-defining comeback — a menacing, electrifying turn that reminded audiences why he was always more than just a Deol. To hear his ex-partner praise that work publicly, without agenda or ambiguity, was quietly remarkable.

## The Aashiqui Clarification

The interview also untangled an old rumor. When Bhatt mentioned that a boyfriend early in her career was unsupportive of her film ambitions — the reason she turned down the lead role in her father Mahesh Bhatt's *Aashiqui* — speculation naturally pointed to Deol. She corrected it directly: that partner was someone else entirely. She met Bobby later.

This matters because it separates the professional frustration from the romantic memory. The relationship with Bobby, in Bhatt's telling, was untainted by career resentment. It was simply a chapter that ended when two people grew in different directions.

## Why This Resonates

Bollywood ex-couples rarely get to exist in public with this much peace. The standard script is either dramatic denial, pointed silence, or weaponized memoir. Bhatt chose a fourth option: warmth without exposition. Acknowledgment without detail.

"Dignity and grace for the present, for not only your own life but for the people who have been in your life, and the people who they have in their life, is a very important thing to maintain," she said.

It's a sentence that could function as a personal philosophy — and one that stands out sharply against the current Bollywood landscape, where PR-managed narratives and social media subtweets have replaced actual communication.

## The Diaspora Connection

For Indians abroad, the Deol-Bhatt era represents a very specific Bollywood. It was the decade of *Gupt*, *Soldier*, *Barsaat*, and the Deol brothers' rise — the same era many NRI families were taping Zee TV on VHS and sending cassettes to relatives. Pooja Bhatt, as Mahesh Bhatt's daughter and a star in her own right, was inescapable in that ecosystem.

To hear her speak about that time with tenderness rather than regret feels like the kind of emotional maturity that the nostalgia machine rarely allows for. The 1990s weren't perfect. The relationships weren't fairy tales. But they were real — and Bhatt's refusal to perform the narrative for an audience is, in its own quiet way, the most interesting Bollywood interview of the week.

*Bobby Deol has not publicly commented on the interview.*"""
    },
]


# ── Publish loop ─────────────────────────────────────────────────────
def main():
    published = 0
    for art in articles:
        print(f"\n{'='*60}")
        print(f"Publishing: {art['headline'][:70]}...")

        # Image sourcing
        img_url = None
        img_attribution = None

        # Try Wikipedia for person articles
        person = art.get("person")
        if person:
            img_url = fetch_wikipedia_person_image(person)
            if img_url:
                img_attribution = "Wikimedia Commons"

        # Try alternate person name
        if not img_url and art.get("person_alt"):
            img_url = fetch_wikipedia_person_image(art["person_alt"])
            if img_url:
                img_attribution = "Wikimedia Commons"

        # Fall back to Pexels
        if not img_url and art.get("pexels_query"):
            img_url = fetch_pexels_image(art["pexels_query"], art.get("pexels_fallback"))
            if img_url:
                img_attribution = "The Videshi"

        # Validate image
        if img_url and not validate_image_url(img_url):
            print(f"  ⚠ Image validation failed, skipping image")
            img_url = None
            img_attribution = None

        if img_url:
            print(f"  ✓ Using image: {img_url[:80]}...")
        else:
            print(f"  ⚠ No valid image found — publishing without image")

        # Create topic first
        topic_id = create_topic(art["headline"], art["category"])
        if not topic_id:
            print(f"  ✗ Failed to create topic, skipping article")
            continue

        # Build article row
        article_id = str(uuid.uuid4())
        word_count = len(art["body"].split())
        row = {
            "id": article_id,
            "topic_id": topic_id,
            "headline": art["headline"],
            "subheadline": art["subheadline"],
            "slug": art["slug"],
            "category": art["category"],
            "body": art["body"],
            "sources": art["sources"],
            "image_url": img_url,
            "image_attribution": img_attribution,
            "vertical": art["category"],
            "word_count": word_count,
            "status": "published",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        result = sb_insert("p2_articles", row)
        if result:
            print(f"  ✓ Published: {art['slug']}")
            published += 1
        else:
            print(f"  ✗ Failed to publish: {art['slug']}")

        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Done: {published}/{len(articles)} articles published")


if __name__ == "__main__":
    main()
