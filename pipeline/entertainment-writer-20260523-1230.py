#!/usr/bin/env python3
"""Entertainment writer — May 23 2026, 12:30 PDT batch:
1. Drishyam 3 crosses ₹117 Cr worldwide in 3 days — overseas carries the franchise
2. Ranveer Singh's ₹300 Cr zombie film Pralay + Vicky Kaushal blocks 18 months for Mahavatar
3. Score decay for old entertainment articles
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

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Drishyam 3 crosses ₹117 Cr worldwide in 3 days
# ══════════════════════════════════════════════════════════════

a1_id = str(uuid.uuid4())

articles.append({
    "id": a1_id,
    "headline": "Drishyam 3 Just Crossed ₹117 Crore Worldwide in Three Days. Sixty Percent of That Money Came From Outside India.",
    "subheadline": "Mohanlal's franchise closer has collected ₹70 crore overseas and ₹47 crore domestically in its opening weekend — making it the most diaspora-dependent Indian blockbuster of 2026.",
    "slug": "drishyam-3-117-crore-worldwide-3-days-overseas-dominance-mohanlal-20260523",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "standard",
    "status": "published",
    "published_at": now,
    "score_total": 82,
    "tags": ["Drishyam 3", "Mohanlal", "Jeethu Joseph", "Malayalam cinema", "box office", "overseas", "NRI", "weekend collection", "franchise"],
    "diaspora_angle": "Drishyam 3's overseas haul — ₹70 crore in three days, roughly 60% of its worldwide total — is the clearest evidence yet that Malayalam cinema's biggest franchises now depend on the diaspora more than on Kerala itself. The Gulf, North America, the UK, and Australia drove these numbers, and the NRI Malayali community essentially bankrolled the film's opening weekend. For diaspora audiences who grew up with the first two Drishyam films — the original a cult classic, the sequel an OTT sensation during Covid — this is the theatrical event they've been waiting for. Kerala contributed ₹29 crore domestically, but the Gulf alone may have matched or exceeded that figure. When 60% of your opening weekend comes from outside India, the diaspora isn't just your audience — it's your business model.",
    "sources": [
        {"url": "https://www.sacnilk.com", "name": "Sacnilk"},
        {"url": "https://www.pinkvilla.com", "name": "Pinkvilla"},
        {"url": "https://www.zoomtventertainment.com", "name": "Zoom TV"},
        {"url": "https://www.bollywoodlife.com", "name": "Bollywood Life"},
        {"url": "https://www.nripage.com", "name": "NRI Page"}
    ],
    "image_search_query": "Drishyam 3 Mohanlal poster theatrical release 2026",
    "word_count": 750,
    "body": """Here's a number that should rewrite how the Indian film industry thinks about Malayalam cinema: ₹70 crore.

That's what Drishyam 3 has collected from overseas markets alone in its first three days. Against a domestic India gross of ₹47.17 crore, overseas revenue accounts for roughly 60% of the film's ₹117 crore worldwide total. In the history of Malayalam cinema, no film has ever been this dependent on — or this rewarded by — the diaspora.

## The Weekend Numbers

Drishyam 3 opened on May 21 (Mohanlal's birthday) with ₹43.50 crore worldwide on Day 1 — the second-biggest opening day ever for a Malayalam film, behind only L2: Empuraan's ₹67.50 crore. Day 2 added ₹30 crore more despite the usual post-opening drop, and Day 3 — Saturday — saw a 24% jump to ₹13.70 crore India net, bringing the domestic tally to ₹40.60 crore net and ₹47.17 crore gross.

The day-wise India net breakdown tells a clear story of weekend momentum:

- **Day 1** (Thursday): ₹15.85 crore
- **Day 2** (Friday): ₹11.05 crore (30% drop — expected for a weekday)
- **Day 3** (Saturday): ₹13.70 crore (24% jump — the weekend kicks in)

Kerala dominated the domestic performance with ₹29.15 crore gross across three days, followed by Karnataka (₹6.80 crore), Andhra Pradesh/Telangana (₹4.25 crore), and Tamil Nadu (₹3.75 crore). Kochi theatres ran at 88% occupancy on Saturday. Kozhikode hit 85%. Kollam and Alappuzha both crossed 80%.

But the real story is the ₹70 crore from overseas.

## The Diaspora Carried This Film

The Gulf region has always been the backbone of Malayalam cinema's international business — the Malayali diaspora in Dubai, Abu Dhabi, Qatar, Bahrain, Kuwait, and Oman treats major releases as community events. But Drishyam 3's overseas performance goes beyond the Gulf. North America, the UK, and Australia all delivered exceptional numbers, driven by second-generation NRI Malayalis who grew up watching the first Drishyam on their parents' laptops and the second one streaming during Covid lockdowns.

The overseas advance bookings alone had crossed $2.3 million (₹22 crore) before release, and walk-in sales over the weekend pushed the total well past ₹70 crore. To put this in perspective: the entire lifetime overseas collection of many successful Malayalam films falls in the ₹15-25 crore range. Drishyam 3 did that in a single day.

This 60/40 overseas-to-domestic split is unprecedented for Malayalam cinema. Even L2: Empuraan, which had a bigger opening, was more domestically weighted. What Drishyam 3 demonstrates is that franchise recognition transcends geography — NRI audiences don't need to be sold on Georgekutty. They already know the character. They already know the stakes. They just need a theatre nearby.

## Mixed Reviews, Massive Collections

The elephant in the room is word of mouth. Drishyam 3 has received mixed reactions from critics and audiences — some calling it a worthy conclusion to the trilogy, others feeling it doesn't match the tight plotting of the original. Despite this, the film is collecting as if it were unanimously praised.

This is the franchise effect: audiences show up for the brand regardless of reviews, especially in the opening weekend. The question is whether Drishyam 3 can sustain its run into Week 2 if the mixed word of mouth dampens repeat viewings. The original Drishyam earned its legendary status through legs — growing collections week after week. Drishyam 3 is front-loaded by comparison, which is both a sign of the times and a potential ceiling.

## Racing Toward ₹150 Crore

At its current pace, Drishyam 3 should cross ₹150 crore worldwide by Sunday night, making it the fastest Malayalam film to reach that milestone after L2: Empuraan. The ₹200 crore lifetime target looks achievable but not guaranteed — it depends entirely on whether the film holds through the weekdays.

What's already guaranteed is that Drishyam 3 has changed the math of Malayalam cinema's economics. When 60% of your opening weekend comes from outside India, the diaspora isn't a bonus market — it's the primary market. Future Malayalam blockbusters will be greenlit, budgeted, and marketed with this reality in mind.

## What This Means for NRI Audiences

For Malayali NRIs who drove to their nearest IMAX or multiplex this weekend, Drishyam 3 was more than a movie — it was a community event. The franchise that defined Malayalam thriller cinema for a decade concluded with a theatrical run that their ticket purchases made possible. Kerala contributed ₹29 crore. The diaspora contributed ₹70 crore. The numbers speak for themselves.

Georgekutty's story may be over. But the business model he built — one that depends on NRIs as much as Kochi multiplexes — is just getting started."""
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Ranveer's Pralay + Vicky's Mahavatar
# ══════════════════════════════════════════════════════════════

a2_id = str(uuid.uuid4())

articles.append({
    "id": a2_id,
    "headline": "Ranveer Singh Is Making a ₹300 Crore Zombie Film. Vicky Kaushal Has Blocked 18 Months to Play a God. Bollywood Has Never Bet This Big.",
    "subheadline": "Pralay and Mahavatar represent a new era of Indian filmmaking — where stars commit years of their lives and producers invest the GDP of a small town on a single story. Here's what NRIs need to know about the two most ambitious Hindi films in development.",
    "slug": "ranveer-singh-pralay-vicky-kaushal-mahavatar-bollywood-ambitious-slate-20260523",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "standard",
    "status": "published",
    "published_at": now,
    "score_total": 79,
    "tags": ["Ranveer Singh", "Pralay", "Vicky Kaushal", "Mahavatar", "Parashurama", "Bollywood", "zombie film", "Jai Mehta", "Kalyani Priyadarshan", "box office", "Indian cinema 2027"],
    "diaspora_angle": "For NRIs who watched Bollywood evolve from ₹10 crore romantic comedies to ₹300 crore post-apocalyptic thrillers in a single generation, Pralay and Mahavatar represent something new: Indian cinema that's being conceived at the same budget and ambition level as mid-range Hollywood tentpoles. Ranveer's Pralay — a zombie survival film — is the kind of genre work that NRI audiences have traditionally sought from Hollywood. If it works, it could be the first Indian genre film to genuinely compete for the diaspora audience that currently defaults to Marvel and Blumhouse. Vicky Kaushal's Mahavatar, meanwhile, taps into the same mythological-epic energy as Ramayana but through a less-explored avatar — Parashurama. Both films will release theatrically worldwide, and both are explicitly designed with international audiences in mind.",
    "sources": [
        {"url": "https://www.sacnilk.com", "name": "Sacnilk"},
        {"url": "https://www.pinkvilla.com", "name": "Pinkvilla"},
        {"url": "https://www.bollywoodhungama.com", "name": "Bollywood Hungama"},
        {"url": "https://www.koimoi.com", "name": "Koimoi"}
    ],
    "image_search_query": "Ranveer Singh dramatic actor portrait 2026",
    "word_count": 740,
    "body": """Something has shifted in Bollywood. Not in the films being released this weekend — but in the films being planned for 2027 and beyond. Two announcements in the past week tell you everything about where India's biggest film industry is headed.

Ranveer Singh's post-apocalyptic zombie thriller Pralay begins principal photography in August 2026 with a reported budget of ₹300 crore. Vicky Kaushal has blocked 18 months of his calendar — eighteen months, no other projects — to play Parashurama in the mythological epic Mahavatar. Both commitments would have been unthinkable in Bollywood five years ago. Now they're table stakes.

## Pralay: Bollywood's First Real Zombie Film

Let's start with the stranger of the two. Pralay, directed by Jai Mehta and produced by Applause Entertainment along with Ranveer's own production house Maa Kasam Films, is being described as a survival action drama set in a post-apocalyptic world. The genre tag: zombie thriller.

Indian cinema has never produced a serious zombie film. There have been horror comedies, there have been B-movie experiments, but there has never been a ₹300 crore production with an A-list star that takes the genre at face value. Ranveer is betting that Indian audiences — and crucially, Indian diaspora audiences — are ready for it.

The casting adds an interesting dimension. Kalyani Priyadarshan, who was last seen in the blockbuster Tamil film Lokah, will star opposite Ranveer. This is her Bollywood debut, and the pairing signals Pralay's pan-Indian ambitions — a Hindi-language film with a South Indian co-lead, designed for audiences across every region and every diaspora market.

Ranveer personally convinced Kalyani to take the role, according to Sacnilk. The film will explore themes of survival and family bonds in a world ravaged by disaster — suggesting it's less World War Z and more The Road with Indian sensibilities. Filming begins August 2026, with a projected 2027 release.

## Mahavatar: Vicky Kaushal Disappears for a Year and a Half

If Pralay is Bollywood's genre experiment, Mahavatar is its devotional commitment. Vicky Kaushal will play Parashurama — the sixth avatar of Vishnu, a Brahmin warrior who wielded an axe and is one of the most complex figures in Hindu mythology.

The 18-month exclusive commitment is unprecedented for a Hindi film actor. No other projects, no brand shoots, no parallel films. Kaushal has essentially agreed to live as Parashurama for a year and a half — a level of immersion that echoes Christian Bale's approach to The Machinist or Daniel Day-Lewis in anything he's ever done.

The production details are sparse, but the ambition is clear. After Ramayana (which is tracking for an October 2026 release) and Adipurush (which… happened), Mahavatar is the next entry in Bollywood's mythological-epic phase. The difference is the commitment level: instead of a six-month shoot squeezed between brand deals, Kaushal is treating this like a complete transformation.

## The ₹300 Crore Question

Both films represent a new financial reality in Bollywood. Five years ago, a ₹300 crore budget was reserved for multi-part franchise spectacles. Now it's the starting point for any film that wants to compete globally.

The economics only work if these films collect ₹500+ crore worldwide — which means overseas markets aren't optional, they're essential. Dhurandhar and its sequel proved that Indian action films can collect ₹1,000+ crore with the right star and marketing. Pralay and Mahavatar are being conceived in that post-Dhurandhar reality, where anything less than ₹300 crore worldwide is considered a disappointment.

For producers, the calculus has changed. A ₹50 crore romantic comedy that earns ₹100 crore is a hit — but it doesn't move the culture. A ₹300 crore epic that earns ₹600 crore becomes an event, drives streaming deals, sells merchandise, and builds franchise potential. The risk is higher, but the upside is exponentially larger.

## What NRIs Should Watch For

Pralay could be the first Indian film that competes directly with Hollywood genre movies in NRI markets. If a diaspora family in Texas has to choose between Pralay and the next Blumhouse horror on a Friday night, and they choose Pralay — that's a paradigm shift.

Mahavatar, meanwhile, speaks to the growing appetite for mythological storytelling that treats Hindu epics with the same cinematic ambition that Hollywood applies to Greek and Norse mythology. For NRI parents who have struggled to find culturally rooted entertainment that their American or British-raised kids will actually watch, a Vicky Kaushal-as-Parashurama epic might be exactly the bridge they've been looking for.

Neither film will arrive before 2027. But the fact that they're being planned now — at this scale, with this commitment — tells you that Bollywood isn't just competing with South Indian cinema anymore. It's competing with Marvel. And for the first time, the budgets are starting to match."""
})

# ── Insert articles ──
for a in articles:
    result = sb_post("p2_articles", a)
    print(f"✅ Published: {a['id'][:8]} — {a['headline'][:80]}")

# ── Score decay for entertainment articles older than 48h ──
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

print(f"\n✅ Entertainment writer 12:30 batch complete.")
print(f"  Article 1: {articles[0]['id']}")
print(f"  Article 2: {articles[1]['id']}")
