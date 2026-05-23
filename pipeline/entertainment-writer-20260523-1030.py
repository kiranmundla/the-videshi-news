#!/usr/bin/env python3
"""Entertainment writer — May 23 2026, 10:30 PDT batch:
1. Ramayana preponed to October 30, 2026 — Namit Malhotra's pre-Diwali strategy
2. Raja Shivaji becomes highest-grossing Marathi film, surpassing Sairat
3. Score decay for old entertainment articles
"""

import json, os, re, uuid, requests
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

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Ramayana preponed to October 30, 2026
# ══════════════════════════════════════════════════════════════

a1_id = str(uuid.uuid4())

articles.append({
    "id": a1_id,
    "headline": "Ramayana Might Hit Theaters a Week Before Diwali. The Strategy Behind October 30 Tells You Everything About How Bollywood Now Thinks About Money.",
    "subheadline": "Namit Malhotra is reportedly considering preponing the Ranbir Kapoor-Yash epic to October 30, 2026 — not to rush it, but to let word of mouth peak during Diwali week. The distribution deal alone is reportedly worth ₹450 crore.",
    "slug": "ramayana-october-30-diwali-prepone-namit-malhotra-ranbir-kapoor-strategy-20260523",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "standard",
    "status": "published",
    "published_at": now,
    "score_total": 85,
    "tags": ["Ramayana", "Ranbir Kapoor", "Yash", "Sai Pallavi", "Sunny Deol", "Nitesh Tiwari", "Namit Malhotra", "Diwali 2026", "box office strategy", "Prime Focus", "distribution deal"],
    "diaspora_angle": "For the Indian diaspora, Ramayana is not just a film — it's the event that will define the 2026 Diwali season globally. NRI families have already been circling the release window, and the October 30 prepone is designed with them in mind: arriving a week early means diaspora audiences in the US, UK, Gulf, and Australia can watch the film during the pre-Diwali weekend, then drive word-of-mouth through WhatsApp groups and family calls that reach back to India. The ₹450 crore distribution deal reflects the industry's confidence that overseas collections will be historic — the teaser alone broke viewership records across NRI-heavy markets. For a generation of diaspora Indians who grew up hearing the Ramayana from grandparents and watching Ramanand Sagar's TV serial on loop, this is the most anticipated cultural event since RRR's Oscar night.",
    "sources": [
        {"url": "https://www.bollywoodhungama.com", "name": "Bollywood Hungama"},
        {"url": "https://www.sacnilk.com", "name": "Sacnilk"},
        {"url": "https://www.zoomtventertainment.com", "name": "Zoom TV"},
        {"url": "https://gulte.com", "name": "Gulte"},
        {"url": "https://www.mensxp.com", "name": "MensXP"}
    ],
    "image_search_query": "Ramayana epic Indian film production temple grand set 2026",
    "word_count": 780,
    "body": """The biggest film in Indian cinema history might just have moved its release date — and the reason why tells you more about the state of Bollywood in 2026 than any box office number could.

According to Bollywood Hungama, producer Namit Malhotra is in active discussions to prepone Ramayana: Part One from its Diwali 2026 slot to October 30 — exactly one week before the festival begins. The move, if confirmed, would represent one of the most calculated release strategies in Indian film history.

## The Logic of Arriving Early

The thinking is counterintuitive but brilliant. A Diwali release means opening against the festival itself — when families are traveling, visiting relatives, bursting crackers, and doing everything except sitting in a cinema on Day 1. By opening a week early, Ramayana would have seven days to build word of mouth before the Diwali holiday period amplifies everything.

"Namit Malhotra wants the film to establish itself before the Diwali period," a source told Bollywood Hungama. "He wants the word of mouth to spread all across, so that the business peaks in the second week. He is here to redefine business by not just bringing a pre-Diwali release, but also a film that scores a bigger second week than the first due to the festive period."

This is Baahubali-era thinking applied to a Baahubali-scale film. The goal isn't a massive opening day — it's a massive second week. If Ramayana opens well on October 30 and word of mouth carries through WhatsApp groups and social media, the Diwali weekend (November 5-9) becomes the film's real launch pad. Families who couldn't make it opening week will have the festival holidays free. Repeat viewings spike. The multiplier effect kicks in.

## The ₹450 Crore Distribution Deal

The distribution economics underscore the stakes. Malhotra is reportedly negotiating offers worth ₹450 crore for the theatrical distribution rights alone. To put that number in perspective, it's roughly what most Bollywood films make in their entire theatrical run. For Ramayana, it's the minimum guarantee — the floor, not the ceiling.

The film's production budget has been estimated at ₹600-700 crore across both parts, making it the most expensive Indian film ever produced. Part Two is already slated for Diwali 2027, meaning the franchise is designed as a two-year event cycle that dominates consecutive festival seasons.

## What the Film Actually Is

Directed by Nitesh Tiwari (Dangal, Chhichhore), Ramayana: Part One stars Ranbir Kapoor as Lord Ram, Sai Pallavi as Goddess Sita, Yash as Ravana, and Sunny Deol as Hanuman. The film reportedly features a collaboration between A.R. Rahman and Hans Zimmer on the score — a pairing that alone would make this the most globally ambitious Indian soundtrack ever attempted.

The first teaser, released earlier this year, broke viewership records and signaled that this isn't a devotional retelling — it's a cinematic epic designed to compete globally. Prime Focus Studios' visual effects work has drawn comparisons to Hollywood tentpoles, and the film's CinemaCon presentation reportedly left international distributors scrambling for rights.

## Why October 30 Changes Everything

The prepone creates a fascinating competitive dynamic. No other major release is currently positioned for October 30, which means Ramayana would have a clean corridor into Diwali. Compare this to a Diwali-day release, where it might have shared screens with holdover titles or late-arriving competitors.

There's also an IMAX factor. Ramayana has been confirmed for the IMAX format, and opening a week early would give it exclusive access to premium screens before any Diwali-week competition arrives. Given that IMAX tickets command 2-3x the average ticket price, a week of uncontested premium-format screening could add ₹50-100 crore to the total.

## The Bigger Question

What makes this story significant isn't just the strategy — it's what it reveals about Bollywood's evolution. Five years ago, studios treated release dates as immovable religious holidays. You picked Diwali, Christmas, or Independence Day, and you held the slot. The idea of deliberately arriving early to game the word-of-mouth cycle would have been heresy.

Now it's orthodoxy. Dhurandhar 2 proved that a well-timed release with room to breathe can generate historic numbers. Ramayana's team is applying the same philosophy at an even larger scale.

The formal announcement of the October 30 date is expected once the distribution deal is finalized. Until then, the film industry — and every NRI family group chat already making Diwali plans — is holding its breath.

For a film about a prince in exile who eventually comes home, the timing feels almost poetic. Ramayana isn't waiting for Diwali. It's making Diwali wait for it."""
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Raja Shivaji — first Marathi film to cross ₹100 Cr
# ══════════════════════════════════════════════════════════════

a2_id = str(uuid.uuid4())

articles.append({
    "id": a2_id,
    "headline": "A Marathi Film Just Crossed ₹100 Crore for the First Time in History. It Took Riteish Deshmukh Playing a King to Break a Record That Stood for a Decade.",
    "subheadline": "Raja Shivaji has surpassed Sairat as the highest-grossing Marathi film ever — ₹110 crore worldwide in 22 days. But the real story is how a regional-language historical epic did what no Marathi film has done before: cross the ₹100 crore mark in India.",
    "slug": "raja-shivaji-highest-grossing-marathi-film-riteish-deshmukh-sairat-record-20260523",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "standard",
    "status": "published",
    "published_at": now,
    "score_total": 78,
    "tags": ["Raja Shivaji", "Riteish Deshmukh", "Marathi cinema", "Sairat", "box office record", "Chhatrapati Shivaji Maharaj", "regional cinema", "Jio Studios", "Nagraj Manjule", "100 crore club"],
    "diaspora_angle": "For the Marathi diaspora — concentrated in the US (particularly New Jersey, the Bay Area, and Texas), the UK, and the Gulf — Raja Shivaji crossing ₹100 crore is a moment of cultural validation. Marathi communities abroad have watched Bollywood and South Indian industries achieve this milestone repeatedly while their own cinema remained boxed into modest budgets and limited releases. The film's Hindi-dubbed version, which contributed roughly ₹29 crore of the total, suggests that the story of Chhatrapati Shivaji Maharaj resonates far beyond Maharashtra. For NRI Marathi families who have maintained language and cultural identity across generations, seeing their cinema achieve a mainstream commercial benchmark — with a story about the foundational figure of Maratha identity — carries weight that transcends box office arithmetic.",
    "sources": [
        {"url": "https://www.sacnilk.com", "name": "Sacnilk"},
        {"url": "https://www.pinkvilla.com", "name": "Pinkvilla"},
        {"url": "https://www.koimoi.com", "name": "Koimoi"},
        {"url": "https://www.zoomtventertainment.com", "name": "Zoom TV"},
        {"url": "https://glamsham.com", "name": "Glamsham"}
    ],
    "image_search_query": "Maratha warrior historical fort Maharashtra India cinematic 2026",
    "word_count": 720,
    "body": """For a decade, the ceiling of Marathi cinema was a film about two teenagers who fell in love across caste lines and paid for it with their lives. Nagraj Manjule's Sairat, released in 2016, grossed ₹110 crore worldwide and became the benchmark that every Marathi filmmaker measured themselves against — and fell short of.

That record is now gone. Riteish Deshmukh's Raja Shivaji, a historical epic about Chhatrapati Shivaji Maharaj, has crossed ₹110 crore worldwide in 22 days. It is officially the highest-grossing Marathi film of all time, and the first to breach the ₹100 crore mark at the Indian box office.

## The Numbers

Raja Shivaji's trajectory tells the story of a film that opened like an event and held like a classic. Released on Maharashtra Day (May 1), the film earned roughly ₹13.85 crore worldwide on its first day and ₹41.65 crore in its opening weekend — numbers that would be respectable for a mid-range Bollywood release, and record-shattering for Marathi cinema.

After three weeks, the film has grossed approximately ₹101.85 crore at the Indian box office (net), with the Marathi version contributing around ₹76 crore and the Hindi-dubbed version adding ₹29 crore. The overseas contribution stands at ₹4.20 crore, bringing the worldwide total past the ₹110 crore milestone that defined the old ceiling.

Pinkvilla estimates the film will wind up its theatrical run at ₹110-115 crore gross at the Indian box office alone. On a reported production budget of ₹75 crore, the film has already achieved a 30% profit margin — a rare feat for a regional-language film of this scale.

## Why This Matters Beyond Maharashtra

The Hindi-dubbed version's performance — ₹29 crore out of a ₹110 crore total — is the most significant data point in this story. It means roughly a quarter of Raja Shivaji's audience chose to watch a Marathi historical epic in Hindi, suggesting that the appeal of the Shivaji Maharaj narrative extends well beyond the Marathi-speaking audience.

This mirrors a broader trend in Indian cinema where regional-language films with culturally specific stories have found pan-India audiences through dubbed versions. The Kerala Story, Kantara, and KGF all demonstrated that a powerful narrative rooted in regional identity can transcend linguistic boundaries when the filmmaking is ambitious enough.

For Riteish Deshmukh, who directed and starred in the film, this is a personal landmark. Known primarily as a Bollywood comedy actor through franchises like Housefull and Total Dhamaal, Deshmukh has spent years building a parallel identity as a Marathi-language filmmaker. His previous directorial effort, Ved, earned ₹73 crore — impressive for Marathi cinema, but well short of the Sairat benchmark. Raja Shivaji didn't just clear that bar; it demolished it.

## The Sairat Comparison

What makes the record change fascinating is how different the two films are. Sairat was a ₹4 crore production — a raw, visceral love story shot with non-professional actors that became a cultural phenomenon through word of mouth and repeat viewings. Its ₹110 crore gross represented a 2,750% return on investment.

Raja Shivaji is the opposite model — a ₹75 crore production backed by Jio Studios and Mumbai Film Company, featuring an established star, extensive VFX work, and a national marketing campaign. It's the big-budget approach to regional cinema that the industry has been debating for years: can you spend Bollywood money on a regional film and get Bollywood returns?

The answer, apparently, is yes — if the subject is Chhatrapati Shivaji Maharaj and the timing is Maharashtra Day.

## What Comes Next

The ₹100 crore barrier for Marathi cinema has now been psychologically broken, and the implications will play out over the next several years. Producers who previously capped Marathi film budgets at ₹10-20 crore will now consider ₹50-75 crore investments for the right subject. Studios like Jio, which co-produced Raja Shivaji, will look at Marathi cinema as a viable commercial market rather than a prestige play.

The highest-grossing Marathi films now read: Raja Shivaji (₹110+ crore), Sairat (₹110 crore), Baipan Bhari Deva (₹90.50 crore), Ved (₹73 crore), and Natsamrat (₹46 crore). The gap between first and fifth is now more than double — a concentration at the top that suggests the market can support blockbusters but hasn't yet built the depth of mid-range commercial hits.

For Marathi cinema, the century has been scored. The question now is whether it was a one-off innings or the start of a new era."""
})

# ── Insert articles ──
for a in articles:
    result = sb_post("p2_articles", a)
    print(f"✅ Published: {a['id'][:8]} — {a['headline'][:80]}")

# ── Score decay ──
cutoff = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
decay_r = requests.get(
    f"{SB_URL}/rest/v1/p2_articles?status=eq.published&category=eq.Entertainment&published_at=lt.{cutoff}&score_total=gt.30&select=id,score_total&limit=200",
    headers=HEADERS, timeout=30
)
decayed = 0
for art in decay_r.json():
    new_score = max(30, int(art["score_total"] * 0.95))
    if new_score < art["score_total"]:
        sb_patch("p2_articles", f"id=eq.{art['id']}", {"score_total": new_score})
        decayed += 1
print(f"📉 Score decay: {decayed} articles decayed (of {len(decay_r.json())} eligible)")

print("\n✅ Entertainment writer 10:30 batch complete.")
