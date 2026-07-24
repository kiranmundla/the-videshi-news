#!/usr/bin/env python3
"""Entertainment writer — May 25 2026, 09:30 UTC batch:
1. Deool Band 2 — Marathi devotional comedy becomes 2nd biggest Marathi opener ever
2. Weekend box office: Regional cinema (Drishyam 3, Karuppu, Deool Band 2) crushes Bollywood
+ Score decay for older entertainment articles
"""

import json, os, uuid, requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Supabase config ──
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_patch(table, filters, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filters}", headers={**HEADERS, "Prefer": "return=minimal"}, json=data, timeout=30)
    return r.status_code

def sb_get(table, filters, select="*"):
    r = requests.get(f"{SB_URL}/rest/v1/{table}?{filters}&select={select}", headers=HEADERS, timeout=15)
    return r.json() if r.status_code == 200 else []

def check_duplicate(slug):
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
        headers=HEADERS, timeout=15
    )
    return len(r.json()) > 0 if r.status_code == 200 else False

now = datetime.now(timezone.utc)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S")
articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Deool Band 2 — Marathi Devotional Comedy Breakout
# ══════════════════════════════════════════════════════════════
slug1 = "deool-band-2-marathi-devotional-comedy-15-crore-weekend-pravin-tarde-20260525"
if not check_duplicate(slug1):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "A Marathi Film About a Village Deity and a Locked Temple Just Made ₹15.75 Crore in Four Days. Nobody in Bollywood Is Talking About It. Everyone in Maharashtra Is.",
        "subheadline": "Deool Band 2, starring Pravin Tarde, has become the second biggest Marathi opener in history — outperforming Chand Mera Dil's entire weekend despite releasing on a fraction of the screens. For the Marathi diaspora, it's proof that their cinema doesn't need Bollywood's validation to command the box office.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 76,
        "tags": ["Deool Band 2", "Pravin Tarde", "Marathi cinema", "box office", "devotional comedy", "Maharashtra", "regional cinema", "Raja Shivaji", "Riteish Deshmukh"],
        "diaspora_angle": "For the Marathi diaspora in the US — concentrated in the Bay Area, New Jersey, Chicago, and Dallas — Deool Band 2 represents something specific: a film that succeeds on cultural specificity rather than despite it. The devotional comedy genre doesn't translate easily across languages, which makes its domestic dominance all the more remarkable. NRI Maharashtrians who grew up watching the original Deool (2011) and its exploration of rural faith, politics, and commerce will find the sequel's continued examination of these themes deeply resonant — especially from thousands of miles away, where temple politics takes on a different but equally loaded significance.",
        "sources": [
            {"url": "https://sacnilk.com/movies/Deool_Band_2_2026", "name": "Sacnilk"},
            {"url": "https://www.pinkvilla.com/entertainment/box-office/deool-band-2-box-office-collections-pravin-tardes-devotional-comedy-drama-performs-well-collects-rs-6-crore-plus-in-two-days-1467816", "name": "Pinkvilla"},
            {"url": "https://www.zoomtventertainment.com/entertainment/deool-band-2-achieves-6th-largest-opening-for-marathi-films-on-day-1-marking-its-best-career-launch", "name": "Zoom TV"},
            {"url": "https://www.koimoi.com/box-office/deool-band-2-box-office-collection-day-2/", "name": "Koimoi"}
        ],
        "image_search_query": "Deool Band 2 Marathi film 2026 Pravin Tarde devotional comedy",
        "image_entities": ["Pravin Tarde", "Deool Band 2", "Marathi cinema"],
        "image_must_show": "Deool Band 2 film poster or Pravin Tarde in the film",
        "word_count": 780,
        "body": """While Bollywood trade analysts spent the weekend debating whether Chand Mera Dil could cross ₹15 crore, a Marathi film about a village deity and a locked temple had already done it.

*Deool Band 2*, directed by and starring Pravin Tarde, collected an estimated **₹15.75 crore net** in its four-day opening weekend — making it the **second biggest Marathi opener in history**, behind only Riteish Deshmukh's *Raja Shivaji* (₹12.4 crore on Day 1 alone, though that was a mega-budget spectacle). The devotional comedy-drama grossed ₹18.60 crore at the India box office, with remarkable occupancy rates across Maharashtra that rivalled — and in some centres exceeded — the Hindi releases competing alongside it.

## The Numbers That Should Embarrass Bollywood

Here's the comparison that the industry doesn't want to make:

| Film | Weekend Gross | Total Domestic | Screens |
|------|-------------|----------------|---------|
| **Drishyam 3** (Malayalam) | ₹45.00 Cr | ₹63.35 Cr | 2,500+ |
| **Karuppu** (Tamil, Week 2) | ₹40.55 Cr | ₹172.40 Cr | 3,000+ |
| **Deool Band 2** (Marathi) | ₹15.70 Cr | ₹18.60 Cr | ~1,500 |
| **Chand Mera Dil** (Hindi) | ₹13.25 Cr | ₹13.25 Cr | 2,200+ |
| **Pati Patni Aur Woh Do** (Hindi, Week 3) | ₹8.80 Cr | ₹43.25 Cr | 1,800+ |

A Marathi film playing on roughly 1,500 screens outgrossed a Dharma Productions Hindi romance on 2,200+ screens. That's not an anomaly anymore — it's a pattern.

## What Deool Band 2 Actually Is

The sequel to the 2011 cult hit *Deool* (which itself was a National Award-winning Marathi satire about how a village's claim of a divine sighting transforms into a commercial circus), *Deool Band 2* picks up the themes of faith, commerce, and rural politics with a different premise: this time, the temple is locked. The village deity's absence becomes the catalyst for a story that blends devotional sentiment with sharp social comedy.

Pravin Tarde, who has become one of Marathi cinema's most bankable names, both directs and leads the film. The formula is deceptively simple: take a premise rooted in the lived reality of small-town Maharashtra, cast actors the audience trusts, and deliver a film that families watch together. No Marvel VFX. No ₹500 crore budgets. No pan-India ambitions.

The result? In 48 hours, it had already become the 4th highest-grossing Marathi film of 2026. By Sunday evening, it was closing in on the lifetime collections of several Hindi films that released this year.

## The Marathi Box Office Renaissance

What's happening in Marathi cinema right now is quietly historic. *Raja Shivaji* crossed ₹100 crore — a first for any Marathi film. *Deool Band 2* is the latest in a string of Marathi films that are finding massive theatrical audiences without the crutch of Hindi dubbing or pan-India marketing.

The reason is structural: Maharashtra is India's wealthiest state, with the highest per-capita multiplex density. When a Marathi film connects with its audience, the infrastructure to convert that connection into box office numbers already exists. What was missing for decades was the confidence — both from producers and audiences — to back Marathi-language films with the kind of theatrical commitment usually reserved for Hindi releases.

That confidence has now arrived.

## Why NRIs Should Care

For the Marathi diaspora in America — and there are significant communities in New Jersey, the Bay Area, Chicago, and the DFW area — *Deool Band 2*'s success carries a specific emotional weight. These are families that grew up watching Marathi theatre and cinema, often feeling like their cultural products existed in a different league from Bollywood's glitz.

The original *Deool* was exactly the kind of film that circulated on hard drives and USB sticks at Marathi mandals across the US — a film too culturally specific for wide theatrical release outside Maharashtra, but too good to ignore. Its sequel opening to ₹15+ crore domestically validates what the diaspora has always known: Marathi storytelling, when given the commercial infrastructure, can compete with anyone.

## The Bigger Picture

The May 22-24 weekend wasn't an accident. It was a statement. The top three grossers at the Indian box office were a Malayalam thriller, a Tamil fantasy actioner, and a Marathi devotional comedy. The Hindi releases — from major production houses, with recognisable stars and significant marketing budgets — finished behind all three.

This isn't about Bollywood dying. It's about Indian cinema finally becoming what it always should have been: a multilingual industry where the best stories win, regardless of the language they're told in. For NRIs who have spent years explaining to American friends that "Indian film" means more than Bollywood, the box office receipts are finally doing the explaining for them.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Weekend Box Office — Regional Cinema Dominates
# ══════════════════════════════════════════════════════════════
slug2 = "india-box-office-weekend-may-2026-regional-cinema-drishyam-3-karuppu-deool-band-bollywood"
if not check_duplicate(slug2):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The Three Films That Won India's Box Office This Weekend Were in Malayalam, Tamil, and Marathi. The Two That Lost Were in Hindi. This Is the New Normal.",
        "subheadline": "Drishyam 3, Karuppu, and Deool Band 2 collected a combined ₹101 crore over the weekend. Chand Mera Dil and Pati Patni Aur Woh Do managed ₹22 crore between them. For the diaspora that still treats 'Indian film' and 'Bollywood' as synonyms, the correction is long overdue.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 80,
        "tags": ["box office", "weekend", "regional cinema", "Bollywood", "Drishyam 3", "Karuppu", "Deool Band 2", "Chand Mera Dil", "Mohanlal", "Suriya", "Marathi cinema", "Malayalam cinema", "Tamil cinema"],
        "diaspora_angle": "For NRIs, this weekend's box office is a cultural wake-up call. The diaspora's movie-watching habits are still overwhelmingly Bollywood-centric — NRI WhatsApp groups debate SRK vs Salman while India's actual box office is being driven by Mohanlal, Suriya, and Pravin Tarde. The disconnect between what NRIs watch and what India watches has never been wider, and this weekend's numbers make the case in hard rupees. It also raises a practical question for NRI families planning summer India trips: the films everyone in India is talking about might not be the ones playing at your local AMC's Bollywood showtimes.",
        "sources": [
            {"url": "https://sacnilk.com/tag/drishyam_3_malayalam_2026", "name": "Sacnilk"},
            {"url": "https://www.pinkvilla.com/entertainment/box-office/chand-mera-dil-opening-weekend-box-office", "name": "Pinkvilla"},
            {"url": "https://sacnilk.com/movies/Deool_Band_2_2026", "name": "Sacnilk"},
            {"url": "https://www.zoomtventertainment.com/entertainment/top-5-box-office-weekend-grossers-may-22-24", "name": "Zoom TV"}
        ],
        "image_search_query": "Indian cinema box office regional languages Malayalam Tamil Marathi 2026",
        "image_entities": ["Mohanlal", "Suriya", "Drishyam 3", "Karuppu", "Indian box office"],
        "image_must_show": "Indian movie theatre or box office scene representing regional cinema",
        "word_count": 800,
        "body": """India's box office has a new power structure, and it doesn't speak Hindi.

The May 22-24 weekend delivered the clearest evidence yet of a tectonic shift in Indian cinema: the three highest-grossing films at the domestic box office were in **Malayalam, Tamil, and Marathi**. The two Hindi films — one from Dharma Productions, one an established franchise sequel — finished in fourth and fifth place.

This isn't a one-weekend anomaly. It's the second consecutive weekend where regional cinema has comfortably outperformed Bollywood. And for the Indian diaspora, which still overwhelmingly equates "Indian film" with "Hindi film," the numbers demand a reckoning.

## The Weekend Scoreboard

| Rank | Film | Language | Weekend Gross | Total Collection | Status |
|------|------|----------|--------------|-----------------|--------|
| 1 | **Drishyam 3** | Malayalam | ₹45.00 Cr | ₹63.35 Cr | Opening weekend |
| 2 | **Karuppu** | Tamil | ₹40.55 Cr | ₹172.40 Cr | 2nd weekend |
| 3 | **Deool Band 2** | Marathi | ₹15.70 Cr | ₹18.60 Cr | Opening weekend |
| 4 | **Chand Mera Dil** | Hindi | ₹13.25 Cr | ₹13.25 Cr | Opening weekend |
| 5 | **Pati Patni Aur Woh Do** | Hindi | ₹8.80 Cr | ₹43.25 Cr | 3rd weekend |

The combined weekend gross of the top three regional films: **₹101.25 crore**. The combined gross of the two Hindi films: **₹22.05 crore**. Regional cinema didn't just beat Bollywood — it outearned it nearly five to one.

## Drishyam 3: The Franchise That Prints Money

Mohanlal's return as Georgekutty has been nothing short of extraordinary from a commercial standpoint. *Drishyam 3* opened to ₹43.50 crore worldwide on Day 1 — the second biggest Malayalam opening ever — and crossed ₹140 crore worldwide in its first four days.

But the story beneath the headline numbers is more complicated. The film has received **mixed word-of-mouth**, with some audiences and critics finding the third instalment a step down from its iconic predecessors. The pattern — massive opening driven by franchise loyalty, followed by potential erosion from divided reception — mirrors what happened with Mohanlal's *L2: Empuraan* last year, which opened to ₹175 crore worldwide but ultimately stopped at ₹265 crore, short of the ₹300 crore milestone that Malayalam cinema has been chasing.

For NRIs, Drishyam 3's Gulf numbers are particularly striking: **₹35.70 crore from the Middle East in three days alone**, with 345,000 tickets sold across the GCC region. The Malayali diaspora in the Gulf remains the most reliable international audience for any language in Indian cinema.

## Karuppu: Suriya's Resurrection Continues

In its second weekend, Suriya's fantasy action drama *Karuppu* added ₹40.55 crore to its total, pushing it past **₹172.40 crore domestically** and past ₹250 crore worldwide. The film became the first Suriya starrer to cross ₹100 crore gross in Tamil Nadu alone — a milestone that places him alongside Vijay and Rajinikanth in a club that, until this film, seemed permanently closed to him.

Directed by RJ Balaji, *Karuppu* has benefited from the kind of sustained audience enthusiasm that Bollywood hasn't seen since Dhurandhar 2. Its second weekend performance of ₹40+ crore is the kind of hold that suggests the film will run well into June.

## Deool Band 2: The Quiet Earthquake

The most remarkable performance of the weekend might be *Deool Band 2*. Playing on roughly 1,500 screens — a fraction of what the Hindi films commanded — Pravin Tarde's Marathi devotional comedy collected ₹15.70 crore over the weekend, becoming the second biggest Marathi opener in history.

A Marathi devotional comedy outperforming a Dharma Productions Hindi romance is the kind of sentence that would have been unthinkable five years ago. It is now a data point.

## What Went Wrong for Bollywood

*Chand Mera Dil*, starring Lakshya and Ananya Panday, opened to a disappointing ₹2.75 crore on Day 1 — well below expectations for a Dharma Productions release with a strong promotional campaign. The film improved over the weekend but finished at ₹13.25 crore, a number that signals a theatrical run that will struggle to recover its investment.

The problem isn't unique to this film. Hindi cinema's mid-range releases — films budgeted between ₹25-75 crore, starring emerging stars, banking on genre appeal — are consistently underperforming in theatres. The audience has bifurcated: they'll show up for mega-event films (Dhurandhar 2, Ramayana) and they'll show up for language-specific cultural products they feel personally connected to. The middle ground that sustained Bollywood for decades is eroding.

## The Diaspora Disconnect

Here's the uncomfortable truth for NRIs: the films that dominate your AMC Bollywood showtimes, your community screening WhatsApp groups, and your Netflix queues are increasingly disconnected from what India actually watches.

When an NRI family visits India this summer, the films everyone is talking about won't be the Hindi releases they tracked from abroad. They'll be Suriya's *Karuppu*, Mohanlal's *Drishyam 3*, and a Marathi film about a locked village temple that most non-Maharashtrians have never heard of.

The solution isn't complicated: start watching. South Indian and regional cinema has never been more accessible internationally, with theatrical releases in major US and UK cities, same-day OTT drops, and dubbed versions that — while imperfect — at least lower the barrier.

## What's Next

The coming weeks bring more tests. *Toxic* (Yash, June 4), *Peddi* (Ram Charan, June 4), and *Hai Jawani Toh Ishq Hona Hai* (David Dhawan, June 5) will flood theatres simultaneously. The first two are Telugu/Kannada mega-productions with pan-India ambitions; the third is classic Bollywood comedy.

If the current pattern holds, the regional films will lead. The question is no longer whether this shift is real. It's whether Bollywood can figure out how to respond before the audience moves on entirely.""",
    })
    print(f"✅ Article 2 prepared: {slug2}")
else:
    print(f"⚠️ DUPLICATE: {slug2}")


# ══════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ══════════════════════════════════════════════════════════════
print(f"\n📝 Inserting {len(articles)} articles...")
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ Inserted: {art['slug'][:60]} → {result[0]['id'][:8] if result else '?'}")
    except Exception as e:
        print(f"❌ Insert failed for {art['slug'][:40]}: {e}")


# ══════════════════════════════════════════════════════════════
# SCORE DECAY — entertainment articles
# ══════════════════════════════════════════════════════════════
print("\n── Score Decay ──")

# 7+ days old → score 35
cutoff_7d = (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
status_7d = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_7d}&score_total=gt.35",
    {"score_total": 35}
)
print(f"7d+ decay → HTTP {status_7d}")

# 3-7 days old → score 50
cutoff_3d = (now - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
status_3d = sb_patch(
    "p2_articles",
    f"category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff_3d}&published_at=gte.{cutoff_7d}&score_total=gt.50",
    {"score_total": 50}
)
print(f"3-7d decay → HTTP {status_3d}")

print("\n✅ Entertainment writer batch complete.")
