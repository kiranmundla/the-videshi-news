#!/usr/bin/env python3
"""Entertainment writer — May 23 2026, 20:30 PDT batch:
1. Desi Bling on Netflix — NRI reality show about wealthy Indians in Dubai divides the internet
2. India's biggest OTT week of 2026 — Dhurandhar uncut, Desi Bling, System, Warrant all drop together
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

def check_duplicate(slug):
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
        headers=HEADERS, timeout=15
    )
    return len(r.json()) > 0 if r.status_code == 200 else False

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Desi Bling on Netflix — NRI reality show
# ══════════════════════════════════════════════════════════════

a1_slug = "desi-bling-netflix-dubai-indians-reality-show-nri-diaspora-20260523"
if not check_duplicate(a1_slug):
    a1_id = str(uuid.uuid4())
    articles.append({
        "id": a1_id,
        "headline": "Netflix Made a Reality Show About Rich Indians in Dubai. It's Called 'Desi Bling.' The Internet Can't Decide Whether to Cringe or Binge.",
        "subheadline": "Shilpa Shetty, Karan Kundrra, Tejasswi Prakash, and a cast of Dubai's wealthiest Indian expats spend eight episodes spending money. NRIs are watching it through their fingers — one hand covering their eyes, the other reaching for the remote.",
        "slug": a1_slug,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now,
        "score_total": 79,
        "tags": ["Desi Bling", "Netflix", "reality TV", "Dubai", "NRI", "Karan Kundrra", "Tejasswi Prakash", "Shilpa Shetty", "Indian diaspora", "streaming"],
        "diaspora_angle": "Desi Bling is, perhaps for the first time, a major international streaming show whose entire premise is the Indian diaspora experience — specifically the ultra-wealthy end of it. For NRIs in the US, UK, and Canada watching from their apartments and suburban homes, the show provokes a complicated reaction: these are technically 'our people' on a global platform, but the version of Indian expat life being showcased bears zero resemblance to the H-1B grind, the parking-lot garba night, or the weekend temple visit. The show forces a conversation the diaspora has been having quietly for years — who gets to represent us on screen, and does representation count when it's this cartoonishly lavish?",
        "sources": [
            {"url": "https://www.livemint.com", "name": "Mint"},
            {"url": "https://www.pinkvilla.com", "name": "Pinkvilla"},
            {"url": "https://www.gadgets360.com", "name": "Gadgets 360"},
            {"url": "https://dubai.news", "name": "Dubai News"},
            {"url": "https://thetab.com", "name": "The Tab"}
        ],
        "image_search_query": "Desi Bling Netflix reality show Dubai Indians 2026",
        "word_count": 870,
        "body": """Three days into its release, Netflix's Desi Bling has become the most talked-about Indian show on the internet — and almost none of the conversation is about its quality. It's about what it represents. Who it represents. And whether that representation is a gift or a curse for the Indian diaspora.

The show, which dropped on May 20, follows wealthy Indian expats living in Dubai as they navigate friendships, rivalries, business, romance, and the kind of lifestyle decisions that involve choosing between a Rolls-Royce and a Bentley for the Tuesday school run. It's a spiritual successor to Dubai Bling, Netflix's earlier reality hit about the emirate's wealthy social scene, but this time the lens is trained squarely on the Indian community.

## The Cast, The Money, The Drama

The headline names are familiar to anyone who's spent time in the Indian entertainment ecosystem. Karan Kundrra and Tejasswi Prakash — the Bigg Boss 15 couple who've been dating for four years — are the show's emotional centrepiece. In the most-discussed moment of the season, Kundrra proposes to Prakash in a grand Dubai setting that has fans of the couple (they call themselves "TejRan") in tears and everyone else in disbelief at the production value of a proposal.

Shilpa Shetty appears in a role that straddles mentor and participant. Rizwan Sajan — the billionaire founder of Danube Group, one of Dubai's largest real estate developers — brings actual, operational wealth to a genre that usually trades in aspirational affluence. Satish Sanpal, founder of ANAX Holding, represents the newer wave of Indian entrepreneurs reshaping Dubai's luxury real estate landscape.

The rest of the cast fills out the standard reality template: beauty queens, socialites, fitness influencers, and the occasional spouse who seems to have wandered onto set by accident.

## The NRI Reaction: It's Complicated

Social media has been predictably split. On Twitter and Instagram, the reaction ranges from "this is the whole vibe" to "second-hand embarrassment" — sometimes in the same thread.

For NRIs in the US and UK, the show triggers a specific discomfort that goes beyond reality TV cringe. The Indian diaspora experience is extraordinarily varied — from the Gujarati motel owner in rural Texas to the Bengali data scientist in Seattle to the Punjabi truck driver in Ontario. What unites these experiences is a shared awareness that how Indians are perceived abroad matters. Every cultural export — every film, every show, every high-profile news story — contributes to that perception.

Desi Bling chooses to represent the ultra-wealthy. The beach clubs, the designer wardrobes, the golf courses that cost more to join than most NRIs earn in a year. It's aspirational television in a very specific register: Dubai-Indian wealthy, which is its own culture, distinct from Silicon Valley-Indian wealthy or Canary Wharf-Indian wealthy or Brampton-Indian wealthy.

The question NRI viewers are grappling with isn't whether the show is entertaining (it is, in the way all reality television is). It's whether this is the version of Indian diaspora life they want Netflix's global audience to see.

## What the Show Gets Right

Strip away the wealth and the drama, and Desi Bling actually captures something real about the Indian expat experience in the Gulf: the way community forms around shared culture in a foreign country. The casual code-switching between Hindi and English. The way business relationships and social relationships blur into one another. The unspoken hierarchy of old money versus new money, of established families versus recent arrivals.

Dubai's Indian community — estimated at over 3.5 million, the largest expat group in the UAE — has its own social ecosystem that's distinct from both India and the Western diaspora. The show, to its credit, doesn't try to explain this to Western viewers. It just drops you into it.

The Karan-Tejasswi proposal, for all its spectacle, also reflects something genuine about how Indian public figures navigate relationships. Their entire courtship has been public property since Bigg Boss. The proposal being filmed for Netflix isn't cynical — it's the logical endpoint of a relationship that has always existed partially on camera.

## Where It Falls Short

The show suffers from the same disease that afflicts most reality television about wealth: it mistakes consumption for character. We see what these people buy. We rarely learn what they think, fear, or actually care about beyond their social standing.

For a show about Indians in Dubai, there's remarkably little exploration of what it actually means to be Indian in the Gulf. The kafala system. The labour economy. The fact that for every Indian billionaire in Dubai, there are thousands of Indian workers building the buildings those billionaires live in. Desi Bling exists in a hermetically sealed bubble where the only problems are interpersonal — who said what at which party, whose invitation list was shorter than expected.

This isn't a criticism unique to this show. It's a criticism of the entire luxury reality genre. But when the cast is specifically Indian, and the show is named "Desi Bling," the omission feels more pointed.

## The Bottom Line for Diaspora Viewers

Watch it or don't — Desi Bling is already a cultural event. It's the first major international streaming show whose entire cast is Indian diaspora, and that alone makes it significant. Whether it's good representation or bad representation is a conversation worth having, but the fact that this conversation is happening at all — on a platform with 283 million subscribers worldwide — is itself a kind of progress.

The show is streaming on Netflix now. All eight episodes are available. Your mileage, as they say in both New Jersey and Dubai, will vary."""
    })
else:
    print(f"⏭ Skipping duplicate: {a1_slug}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: India's Biggest OTT Week of 2026
# ══════════════════════════════════════════════════════════════

a2_slug = "india-biggest-ott-week-2026-dhurandhar-uncut-desi-bling-system-streaming-wars-20260523"
if not check_duplicate(a2_slug):
    a2_id = str(uuid.uuid4())
    articles.append({
        "id": a2_id,
        "headline": "This Was the Biggest OTT Week in Indian Streaming History. Here's Everything That Dropped — and Why It Matters.",
        "subheadline": "Dhurandhar's uncensored cut on Netflix and JioHotstar. Desi Bling. System with Sonakshi Sinha and Jyotika. Warrant on Zee5. Jack Ryan's final mission. Five major releases in five days. The streaming wars just got very real.",
        "slug": a2_slug,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now,
        "score_total": 77,
        "tags": ["OTT", "streaming", "Netflix", "JioHotstar", "Amazon Prime Video", "Zee5", "Dhurandhar", "Desi Bling", "System", "Warrant", "Jack Ryan", "Ranveer Singh", "Sonakshi Sinha", "Indian streaming"],
        "diaspora_angle": "For NRIs who've fully transitioned to streaming as their primary way of consuming Indian content, this week was overwhelming in the best way. Every major platform dropped something significant simultaneously — a rare event that usually only happens during Diwali or Christmas release windows. The Dhurandhar dual-platform release is especially significant for diaspora viewers: it means both Netflix and JioHotstar subscribers get the same content at the same time, regardless of which platform they're paying for. The days of one platform hoarding India's biggest films for months are ending. Competition is finally benefiting the viewer.",
        "sources": [
            {"url": "https://www.gadgets360.com", "name": "Gadgets 360"},
            {"url": "https://www.filmibeat.com", "name": "Filmibeat"},
            {"url": "https://www.analyticsinsight.net", "name": "Analytics Insight"},
            {"url": "https://www.cinemaexpress.com", "name": "Cinema Express"},
            {"url": "https://ottranks.com", "name": "OTT Ranks"}
        ],
        "image_search_query": "Indian OTT streaming platforms Netflix JioHotstar 2026 competition",
        "word_count": 880,
        "body": """If you're an Indian content consumer — anywhere in the world — and you blinked this week, you missed something. Between May 18 and May 24, every major streaming platform serving the Indian market released a headline title. Not filler. Not a dubbed acquisition. Genuine, marquee, "clear your Friday evening" content.

This doesn't happen by accident. And it tells you something important about where Indian streaming is heading.

## The Lineup

Let's start with the biggest: **Dhurandhar: Raw and Undekha** hit both Netflix and JioHotstar simultaneously on May 22. This is the uncut, uncensored version of the Ranveer Singh spy thriller that earned over ₹1,800 crore at the worldwide box office — making it the highest-grossing Indian film of all time. The theatrical version was already streaming on Netflix from January. But this new cut adds 12 minutes of footage, including an extended fight sequence and a character backstory that was trimmed for the theatrical CBFC certification.

The dual-platform release is unprecedented. Netflix and JioHotstar are direct competitors. Having the same version of India's biggest film drop on both platforms at midnight on the same day is like Pepsi and Coca-Cola simultaneously releasing the same limited-edition flavour. It happened because of a licensing arrangement where JioHotstar secured post-theatrical streaming rights while Netflix held the original deal. The Raw and Undekha cut exists in a contractual grey zone that allowed both platforms to claim it.

For viewers, this is great. For the platforms, it's a preview of a future where exclusive windows shrink and content becomes more platform-agnostic.

**Desi Bling** dropped on Netflix on May 20 — the reality show about wealthy Indian expats in Dubai that has become this week's most-discussed Indian content globally. Featuring Karan Kundrra, Tejasswi Prakash, and Shilpa Shetty, it's the first major international reality show built entirely around the Indian diaspora.

**System** arrived on Amazon Prime Video on May 22 — a courtroom thriller starring Sonakshi Sinha and Jyotika. The pairing alone is notable: Sinha has been rebuilding her career through streaming after a mixed theatrical run, while Jyotika is one of Tamil cinema's most respected actors making a rare Hindi-language appearance. Early reviews suggest it's a slow-burn legal drama in the mold of Jailer meets courtroom procedural.

**Warrant** premiered on Zee5 — a gritty crime series that continues the platform's quiet streak of producing some of Indian streaming's most underrated shows. The genre that Zee5 has carved out — mid-budget, dark, Hindi-heartland crime — has become its identity in a market dominated by Netflix's prestige dramas and JioHotstar's cricket.

And for the international overlay: **Jack Ryan: Ghost War** dropped on Prime Video globally, marking John Krasinski's final mission in the franchise. While it's not Indian content, its release on the same platform as System creates a compelling A/B test of what Indian Prime Video subscribers choose on a given evening.

## Why This Week Happened

Streaming platforms plan their release calendars months in advance. When five major titles land in the same week, it's usually because of one of two things: either they're all trying to capture the same seasonal window, or they're deliberately counter-programming each other.

This week appears to be both. Late May is historically dead for Indian theatrical releases — the gap between the Eid and summer windows. That makes it prime territory for OTT platforms to grab attention. Netflix launched two titles (Dhurandhar uncut and Desi Bling) in the same week, which suggests they're confident enough in both to not worry about cannibalization.

The broader trend is clear: Indian streaming is no longer a dumping ground for films that didn't work in theatres. It's becoming a first-choice distribution channel for content designed specifically for the platform. System isn't a theatrical film that went to streaming. Desi Bling isn't a format that could exist in cinemas. Warrant is episodic storytelling that only works in a binge model.

## What This Means for NRI Viewers

For the diaspora, this is the week that streaming finally felt like it had caught up to the theatrical experience in terms of event-level releases. If you're an NRI in the US, UK, or Canada, you had access to every single one of these titles from day one, in your living room, without waiting for a local theatrical release or a delayed OTT window.

That's the promise of streaming finally delivering. Five years ago, an NRI wanting to watch the biggest Indian content of the week would have needed a cinema showing it (unlikely outside of major metros), a pirated stream (unreliable), or patience (weeks to months of waiting). Now, every platform is competing to serve you content on release day.

The question is whether this pace is sustainable. Producing this volume of high-quality content requires enormous investment. Netflix India alone reportedly spent over $400 million on Indian content in 2025. JioHotstar's content budget is believed to be even larger. At some point, subscriber numbers need to justify the spend.

For now, though, the viewer wins. If you haven't caught up on this week's releases yet, clear your weekend. There's enough here to fill it twice over.

Here's the full list for your watchlist:

- **Dhurandhar: Raw and Undekha** — Netflix & JioHotstar (May 22)
- **Desi Bling** — Netflix (May 20)
- **System** — Amazon Prime Video (May 22)
- **Warrant** — Zee5 (May 22)
- **Jack Ryan: Ghost War** — Amazon Prime Video (May 19)

Stream responsibly."""
    })
else:
    print(f"⏭ Skipping duplicate: {a2_slug}")


# ══════════════════════════════════════════════════════════════
# PUBLISH ARTICLES
# ══════════════════════════════════════════════════════════════

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✓ Published: {art['slug']} → {art['id']}")
    except Exception as e:
        print(f"✗ Failed: {art['slug']} → {e}")

if not articles:
    print("No new articles to publish (all duplicates)")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY — reduce scores for entertainment articles >48h old
# ══════════════════════════════════════════════════════════════

cutoff = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat().replace("+00:00", "Z")
decay_url = f"{SB_URL}/rest/v1/p2_articles?category=eq.Entertainment&status=eq.published&published_at=lt.{cutoff}&score_total=gt.10&select=id,score_total,slug&order=published_at.desc&limit=50"
r = requests.get(decay_url, headers=HEADERS, timeout=30)
decay_candidates = r.json() if r.status_code == 200 else []

decayed = 0
for art in decay_candidates:
    old_score = art["score_total"]
    new_score = max(10, int(old_score * 0.92))
    if new_score < old_score:
        sc = sb_patch("p2_articles", f"id=eq.{art['id']}", {"score_total": new_score})
        if sc in (200, 204):
            decayed += 1

print(f"\nScore decay: {decayed} articles decayed out of {len(decay_candidates)} eligible")

print("\nDone!")
