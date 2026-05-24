#!/usr/bin/env python3
"""Entertainment writer — May 24 2026, 00:30 PDT batch:
1. Varanasi: Rajamouli + Mahesh Babu — India's most expensive film wrapping by August, April 2027 release
2. TIFFNZ: New Zealand launches its first Indian film festival — Richa Chadha & Ali Fazal to inaugurate
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
# ARTICLE 1: Varanasi — Rajamouli's ₹1300 Crore Time-Travel Epic
# ══════════════════════════════════════════════════════════════

a1_slug = "varanasi-rajamouli-mahesh-babu-india-most-expensive-film-antarctica-2027-nri-20260524"
if not check_duplicate(a1_slug):
    a1_id = str(uuid.uuid4())
    articles.append({
        "id": a1_id,
        "headline": "India's Most Expensive Film Ever Is About a Time-Travelling Shiva Devotee. Rajamouli Is Wrapping It by August.",
        "subheadline": "Varanasi stars Mahesh Babu, Priyanka Chopra, and Prithviraj Sukumaran. The ₹1,300 crore epic was partly shot in Antarctica. Filming is in its final stretch in Hyderabad with an April 2027 release locked in. If you thought RRR was ambitious, Rajamouli says you haven't seen anything yet.",
        "slug": a1_slug,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now,
        "score_total": 82,
        "tags": ["Varanasi", "SS Rajamouli", "Mahesh Babu", "Priyanka Chopra", "Prithviraj Sukumaran", "Indian cinema", "time travel", "Antarctica", "April 2027", "Telugu cinema", "RRR"],
        "diaspora_angle": "For NRIs, Varanasi represents everything RRR promised about Indian cinema going truly global — but at a scale that makes even RRR look like a rehearsal. Priyanka Chopra, the Indian diaspora's most recognisable global face, is the co-lead. The film was partially shot in Antarctica — a first for Indian cinema, and the kind of production credential that commands attention at the multiplex in New Jersey as easily as Hyderabad. At ₹1,300 crore, it's the most expensive Indian film ever made, and its April 2027 release positions it as a direct competitor to Hollywood tentpoles during the global summer season. After RRR won the Oscar for Naatu Naatu and turned into a cult phenomenon among Western audiences, Rajamouli's next film isn't just an Indian event — it's a global one.",
        "sources": [
            {"url": "https://www.pinkvilla.com", "name": "Pinkvilla"},
            {"url": "https://english.tupaki.com", "name": "Tupaki English"},
            {"url": "https://en.wikipedia.org/wiki/Varanasi_(film)", "name": "Wikipedia"},
            {"url": "https://sacnilk.com", "name": "Sacnilk"},
            {"url": "https://watch.plex.tv", "name": "Plex"}
        ],
        "image_search_query": "Varanasi film Mahesh Babu SS Rajamouli epic 2027",
        "word_count": 850,
        "body": """Somewhere in Hyderabad right now, on a massive set in Katedan, Mahesh Babu is filming a song sequence for a movie about a Shiva devotee who travels through time to retrieve an ancient cosmic artefact. The movie has already been shot across multiple continents, including Antarctica. Its budget exceeds ₹1,300 crore. Its director is the man who made RRR. And it's scheduled to wrap principal photography by August.

This is Varanasi. And it might be the most ambitious Indian film ever made.

## What We Know

Directed by S.S. Rajamouli and starring Mahesh Babu in the lead, Varanasi is an epic action-adventure set across multiple timelines and continents. The plot follows Rudra — a rugged adventurer and devotee of Shiva — who is sent on a mission to recover a lost cosmic artefact of immense power. As he pieces together ancient secrets scattered across centuries, he discovers that the force that set him on this path is a calculating mastermind with ambitions of global domination.

Mahesh Babu plays Rudra as the primary character, but reportedly also appears as Lord Rama in one of the film's historical episodes — a dual-role structure that echoes the kind of mythological layering Rajamouli perfected in the Baahubali films.

Priyanka Chopra Jonas plays Mandakini, the co-lead. Details about her character are sparse, but this marks Chopra's return to Indian cinema in a major production role after years of primarily Western projects. For diaspora audiences who've watched her navigate Hollywood with varying degrees of success, seeing her in a Rajamouli film — where the Indian star system operates at full power — is a homecoming of sorts.

Prithviraj Sukumaran plays Kumbha, the film's villain. The first-look material shows him in a futuristic wheelchair, suggesting a character that spans the same time-jumping narrative. He's described in early reports as a "vicious supervillain" — language that Rajamouli's team doesn't use lightly.

## The Scale

The numbers surrounding Varanasi are staggering even by Bollywood standards. At a reported budget of over ₹1,300 crore, it surpasses every Indian production to date. For context, Baahubali 2 cost approximately ₹250 crore. RRR came in around ₹550 crore. Varanasi represents a more-than-doubling of Rajamouli's own ceiling.

Where did the money go? Partly to locations. Varanasi is the first Indian film to have been shot in Antarctica — a production decision that signals the kind of visual ambition that only a handful of directors globally would attempt. The film has also been shot in multiple locations across Uttar Pradesh, including Varanasi and Prayagraj, and features extensive sequences filmed on purpose-built sets in Hyderabad.

Recent reports indicate that the team recently completed an underwater sequence and is now filming the crucial song that's been occupying the Katedan set. Telugu Chitraalu reports that this particular track isn't a standalone musical number — it plays a key role in the story's progression, which is consistent with how Rajamouli uses songs as narrative devices rather than intermissions.

The target is to wrap all filming by the end of August 2026, which would give the post-production team approximately seven months before the April 7, 2027 release date. Given the film's visual effects requirements — multiple time periods, Antarctica footage, mythological sequences — that's a tight but credible timeline for a team of Rajamouli's calibre.

## Why NRIs Should Care

Start with the obvious: this is the next film from the director of RRR. For the Indian diaspora, RRR was a watershed moment. It wasn't just a hit in India — it became a genuine cultural phenomenon in the West. The Oscar for Naatu Naatu. The standing ovations at American screenings. The articles in the New York Times and the Guardian trying to explain why two Indian men fighting the British Empire with CGI animals was the most exhilarating cinema of 2022.

Varanasi is Rajamouli's attempt to build on that momentum with a film designed from the ground up for global audiences. The time-travel adventure genre is universally legible. The mythological Indian elements give it cultural distinctiveness that Hollywood can't replicate. And the cast — Mahesh Babu's star power across South and Southeast Asia, Priyanka Chopra's global name recognition, Prithviraj's acting pedigree — covers virtually every market.

The April 2027 release date positions Varanasi to open during the global spring-summer corridor, competing directly with Hollywood tentpoles. That's deliberate. Rajamouli doesn't want a "good for an Indian film" reception. He wants to compete on the world stage, on the world's terms.

For NRIs who've spent years explaining Indian cinema to friends and colleagues — who've tried to convey why Baahubali is epic storytelling, why RRR isn't "just a Bollywood movie" — Varanasi is the film that makes the case by itself. It's designed to need no cultural translation. It's designed to fill IMAX screens globally. And if anyone can deliver on that promise, it's the man who turned two freedom fighters into the most entertaining buddy-action film of the decade.

## The Competition

Varanasi doesn't exist in a vacuum. Tollywood's 2027 slate is potentially the most competitive in Indian cinema history. Prabhas and Sandeep Reddy Vanga's Spirit is scheduled for March 5. Jr NTR and Prashanth Neel's Dragon is set for June 11. Allu Arjun and Atlee's Raaka is targeting late 2027. And the Ramayana, now potentially preponed to October 30, 2026, will still be fresh in audiences' minds.

This is Indian cinema operating at a scale that was unimaginable a decade ago. Multiple ₹500-crore-plus productions competing for the same year. For the diaspora, it means there won't be one Indian event film to look forward to — there'll be several. And that's arguably the biggest shift of all: Indian cinema is no longer seasonal. It's year-round, and it's global.

Varanasi releases on April 7, 2027. Start saving your IMAX ticket money now."""
    })
else:
    print(f"⏭ Skipping duplicate: {a1_slug}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: TIFFNZ — New Zealand's First Indian Film Festival
# ══════════════════════════════════════════════════════════════

a2_slug = "new-zealand-first-indian-film-festival-tiffnz-richa-chadha-ali-fazal-diaspora-20260524"
if not check_duplicate(a2_slug):
    a2_id = str(uuid.uuid4())
    articles.append({
        "id": a2_id,
        "headline": "New Zealand Is Getting Its First Indian Film Festival. It Tells You Something About Where the Diaspora Is Heading.",
        "subheadline": "Richa Chadha and Ali Fazal will launch The Indian Film Festival of New Zealand on June 2 with a screening of their Sundance-acclaimed 'Girls Will Be Girls.' The four-day event runs in October across Auckland, Wellington, and Christchurch — and it's part of a much bigger story about Indian cinema's expanding global footprint.",
        "slug": a2_slug,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now,
        "score_total": 74,
        "tags": ["TIFFNZ", "New Zealand", "Indian film festival", "Richa Chadha", "Ali Fazal", "Girls Will Be Girls", "Indian diaspora", "Indian cinema", "Sundance", "Auckland"],
        "diaspora_angle": "The launch of New Zealand's first dedicated Indian film festival is a marker of the diaspora's growing cultural footprint in countries beyond the traditional 'big three' of the US, UK, and Canada. New Zealand's Indian-origin population has grown significantly — from roughly 155,000 in 2013 to over 240,000 in 2023, making Indians one of the fastest-growing ethnic communities in the country. TIFFNZ isn't just a film festival. It's an acknowledgment that the Indian community in New Zealand has reached a cultural mass where a dedicated four-day cinema event across three cities is commercially and culturally viable. For NRIs globally, it's another data point in a trend that's been building for years: Indian cinema is no longer an export that needs a diaspora audience to show up — it's becoming part of the cultural fabric of its host countries.",
        "sources": [
            {"url": "https://www.filmfare.com", "name": "Filmfare"},
            {"url": "https://www.bollywoodhungama.com", "name": "Bollywood Hungama"},
            {"url": "https://www.devdiscourse.com", "name": "Devdiscourse"},
            {"url": "https://www.filmibeat.com", "name": "Filmibeat"},
            {"url": "https://inshorts.com", "name": "Inshorts"}
        ],
        "image_search_query": "New Zealand Indian film festival launch Auckland 2026",
        "word_count": 780,
        "body": """On June 2, actors Richa Chadha and Ali Fazal will be in New Zealand — not for a vacation, not for a brand deal, but to launch the country's first-ever dedicated Indian film festival. The Indian Film Festival of New Zealand, or TIFFNZ, will debut in October 2026 as a four-day celebration of Indian cinema across Auckland, Wellington, and Christchurch.

The launch event will feature a special screening of Girls Will Be Girls, the first feature film produced by Chadha and Fazal's production company. The film, directed by Shuchi Talati, has already earned recognition at the Sundance Film Festival and the Independent Spirit Awards — the kind of international credentials that give a new festival instant programming credibility.

## Why New Zealand, Why Now

India's relationship with New Zealand tends to be overshadowed by the larger diaspora stories in the US, UK, Canada, and the Gulf states. But the numbers tell a different story. New Zealand's Indian-origin population has been growing rapidly — by some estimates doubling over the past decade, with Indians now one of the largest and fastest-growing ethnic communities in the country. Cities like Auckland have vibrant Indian neighbourhoods, Indian grocery stores, Indian restaurants, and Indian community organizations.

What they haven't had, until now, is a dedicated Indian film festival. There have been Indian films at broader multicultural festivals. There have been one-off Bollywood screenings at community centres. But a curated, multi-day, multi-city festival dedicated to Indian cinema across all its languages and genres — that's new. And it's significant.

TIFFNZ is the brainchild of Petrina D'Rozario, who saw a gap between the size and cultural appetite of New Zealand's Indian community and the programming available to them. The festival plans to screen nearly 30 films over four days, covering a range of Indian cinema that goes well beyond the Bollywood blockbusters that typically get international distribution.

## The Richa-Ali Factor

The choice of Richa Chadha and Ali Fazal as the faces of the launch is smart on multiple levels. Both are known for choosing projects that sit at the intersection of commercial appeal and artistic credibility — Chadha through films like Gangs of Wasseypur and Masaan, Fazal through Mirzapur and his Hollywood role in Death on the Nile.

Their transition into production with Girls Will Be Girls signals a broader shift in how Indian actors engage with the global film ecosystem. They're not just promoting a film — they're building institutional bridges between India's creative community and international platforms. A film festival launch in New Zealand is exactly the kind of soft-power infrastructure that creates long-term pathways for Indian cinema in new markets.

"Film festivals play an important role in creating space for diverse stories," Chadha and Fazal said in a joint statement. It's a standard-issue quote, but in context, it carries weight. Diverse stories in the Indian film context means more than just representation — it means Tamil films, Malayalam films, Marathi films, Bengali films, Konkani films getting screens they'd never have access to through commercial distribution alone.

## The Bigger Picture

TIFFNZ joins an expanding network of Indian film festivals globally. IFFLA in Los Angeles has been running since 2002. LIFF in London is a cultural institution. Toronto's TIFF regularly programmes Indian films. The Melbourne Indian Film Festival, the Singapore South Asian International Film Festival, the New York Indian Film Festival — the map is filling in.

What's notable about TIFFNZ is where it sits on that map. New Zealand isn't an obvious choice for an Indian film festival. It doesn't have the sheer population numbers of Indian communities in the US or UK. It doesn't have the proximity to India that Southeast Asian countries have. But it has something that matters perhaps more for the long-term health of Indian cinema abroad: a growing, integrated, second-generation diaspora that wants cultural programming that reflects their identity without reducing it to stereotypes.

The festival's three-city model — Auckland, Wellington, and Christchurch — is particularly smart. It prevents the event from being a one-city affair that only reaches the densest Indian community. Spreading across the country's three main centres signals that Indian cinema isn't a niche offering for one neighbourhood — it's programming for the whole country.

## For NRIs Everywhere

Whether you're in New Zealand or not, the launch of TIFFNZ matters because of what it represents. Every new Indian film festival in a new country is a data point in the same trend: Indian cinema's global footprint is expanding not through Hollywood co-productions or crossover casting, but through the organic growth of diaspora communities who want their stories, their cinema, and their cultural identity reflected on screens in their adopted homes.

Richa Chadha and Ali Fazal launching the festival on June 2 with a Sundance-acclaimed film is the kind of image that would have been unimaginable a generation ago. An Indian couple, successful in both commercial and independent cinema, inaugurating an Indian film festival in the South Pacific. The world is getting smaller, and Indian cinema is getting everywhere.

TIFFNZ runs in October 2026 across Auckland, Wellington, and Christchurch. Mark your calendars — or at least, mark the trend."""
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
