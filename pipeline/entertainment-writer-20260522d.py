#!/usr/bin/env python3
"""Entertainment writer — May 22 2026 batch 5 (22:30 PDT):
Dhurandhar Raw & Undekha OTT launch, Desi Bling Netflix reality, India at Cannes 2026."""

import json, os, re, uuid, requests, subprocess, sys
from datetime import datetime, timezone
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

def make_slug(headline, date_suffix="20260522"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Dhurandhar Raw & Undekha — OTT Launch
# ══════════════════════════════════════════════════════════════

a1_id = str(uuid.uuid4())

articles.append({
    "id": a1_id,
    "headline": "India's Biggest Box Office Hit Just Dropped on Two Streaming Platforms at Once. That's Never Happened Before.",
    "subheadline": "Dhurandhar: Raw & Undekha — the uncensored version of Ranveer Singh's ₹1,307 crore spy thriller — launched simultaneously on Netflix and JioHotstar on May 22. For NRIs who missed the theatrical run, the timing is perfect. For the streaming industry, it's a precedent.",
    "body": """Here is something that has never happened in Indian entertainment: the country's highest-grossing film of the year has released an extended, uncensored version on two competing streaming platforms on the same day.

*Dhurandhar: Raw & Undekha* went live on both Netflix India and JioHotstar at midnight on May 22, 2026. The original theatrical cut of Aditya Dhar's spy thriller — starring Ranveer Singh as an undercover RAW agent infiltrating Karachi's Lyari underworld — earned ₹1,307 crore worldwide. Its sequel, *Dhurandhar: The Revenge*, added another ₹1,848 crore. Together, they represent the most commercially successful Indian film franchise in history.

The "Raw & Undekha" version is not a director's cut in the traditional sense. The runtime remains largely unchanged. What's different is the censorship: dialogue and visual content that was trimmed for the theatrical CBFC certificate has been restored. For a film built around espionage, interrogation, and the moral compromises of deep-cover intelligence work, the uncensored treatment adds texture that the theatrical version only hinted at.

**Why Two Platforms?**

The simultaneous release on Netflix and JioHotstar is the most interesting part of this story — and it's almost certainly a business decision rather than an artistic one.

Typically, Indian films sign exclusive OTT deals. A film goes to Netflix or JioHotstar or Amazon Prime Video, not two at once. The exclusivity window is the leverage that platforms use to justify the ₹100-200 crore digital rights fees they pay for tentpole releases. Breaking that exclusivity is rare.

In Dhurandhar's case, the economics appear to work differently. The theatrical run is long over. The sequel has already earned nearly ₹1,850 crore. Jio Studios, which produced the franchise, owns JioHotstar — so releasing there costs them nothing. Netflix, which reportedly holds international streaming rights, gets to offer a refreshed version to its subscriber base. Both platforms benefit from the cultural moment without cannibalising each other's primary value proposition.

But the precedent matters. If India's biggest franchise can dual-platform its extended cut, smaller films will ask why they can't do the same. The streaming exclusivity model that has defined Indian OTT economics since 2020 may be loosening — and for consumers, that's unambiguously good.

**The NRI Calculation**

For the Indian diaspora, the timing is strategic. *Dhurandhar* had a strong theatrical run in North America, the UK, and the GCC, but spy thrillers are dense narrative experiences — the kind of films people want to rewatch at home with subtitles and the ability to pause. The uncensored version gives NRIs a reason to revisit a film they saw in theatres, or to finally watch one they missed.

The franchise also carries specific diaspora resonance. Its plot — a RAW agent operating in Pakistan under deep cover — draws from the same well of India-Pakistan intelligence mythology that has fuelled everything from *Raazi* to *Tiger Zinda Hai*. But Dhar's treatment is darker and more morally ambiguous than those predecessors. Hamza Ali Mazari, Ranveer's character, isn't a clean-cut patriot. He's a man who has spent so long pretending to be someone else that the distinction between cover identity and real identity has collapsed. For diaspora viewers who navigate their own identity negotiations daily — between Indian and American, between desi and Western — that theme lands differently than it does for domestic audiences.

**What's Next**

*Dhurandhar: The Revenge* will hit JioHotstar on June 4 and Netflix on June 19 — this time on a staggered schedule, preserving the exclusivity window for the sequel. The distinction is telling: the franchise has enough commercial gravity to experiment with its older titles while still commanding premium treatment for its newer ones.

The Raw & Undekha version is available in Hindi, Tamil, and Telugu on both platforms. For NRIs with subscriptions to either service, the only question is which app to open first.""",
    "diaspora_angle": "For NRIs who saw Dhurandhar in Bay Area or NJ theatres, the uncensored version is a rewatch event. For those who missed the theatrical window, it's an overdue introduction to a ₹1,307 crore cultural phenomenon. The dual-platform release on Netflix and JioHotstar means every diaspora household with a streaming subscription has access.",
    "vertical": "entertainment",
    "tags": ["Dhurandhar", "Ranveer Singh", "Netflix", "JioHotstar", "OTT", "streaming", "Aditya Dhar", "spy thriller"],
    "urgency": "breaking",
    "sources": [
        {"url": "https://www.thedailyjagran.com/entertainment/ott/dhurandhar-raw-and-undekha-ott-release-when-and-where-to-watch-first-part-of-spy-thriller-movie-10313061", "name": "Daily Jagran — OTT Release Details"},
        {"url": "https://www.zoomtventertainment.com/entertainment/ott/dhurandhar-raw-and-undekha-ott-release-date", "name": "Zoom TV — Netflix & JioHotstar Launch"},
        {"url": "https://www.cinemaexpress.com/hindi/news/dhurandhar-raw-undekha-ott-release-netflix-jiohotstar", "name": "Cinema Express — Uncut Version Streaming"},
        {"url": "https://www.latestly.com/entertainment/bollywood/dhurandhar-raw-and-undekha-ott-release-date-netflix-jiohotstar", "name": "LatestLY — Restored Sequences Details"},
        {"url": "https://sacnilk.com/dhurandhar-raw-undekha-streaming-release", "name": "Sacnilk — June 4 Sequel Timeline"}
    ],
    "slug": make_slug("dhurandhar-raw-undekha-netflix-jiohotstar-dual-platform-ott"),
    "word_count": 750,
    "status": "published",
    "is_featured": False,
    "category": "Entertainment",
    "published_at": now,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
    "score_total": 78
})


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Desi Bling — Netflix Reality Show About Indians in Dubai
# ══════════════════════════════════════════════════════════════

a2_id = str(uuid.uuid4())

articles.append({
    "id": a2_id,
    "headline": "Netflix Made a Reality Show About Rich Indians in Dubai. The Proposal Was Sweet. The Reviews Are Brutal.",
    "subheadline": "Desi Bling follows the lives of wealthy Indian expats in Dubai — and Karan Kundrra's on-screen proposal to Tejasswi Prakash is the emotional centrepiece. But critics say the show reduces Indian diaspora life to designer handbags and scripted drama.",
    "body": """Netflix has been slowly building a franchise around the wealth of Dubai's expatriate communities. *Dubai Bling* launched in 2022, following Arab and international socialites navigating the city's gilded excess. Now the platform has turned its cameras on the community that arguably defines Dubai's consumer economy more than any other: Indians.

*Desi Bling*, which began streaming this week, follows a group of affluent Indian residents of Dubai as they navigate business, relationships, and social status in the emirate. The cast includes television actors Karan Kundrra and Tejasswi Prakash — who met on *Bigg Boss 15* in 2021 and have been one of Indian entertainment's most followed couples since — alongside business owners, socialites, and lifestyle figures from the Indian community.

The show's centrepiece is Kundrra's on-screen proposal to Prakash, delivered in Punjabi against a Dubai backdrop. The moment went viral within hours of the premiere, with TejRan fans — the couple's dedicated fanbase — flooding social media with clips and reactions.

**The Proposal vs. The Product**

The engagement moment is genuinely affecting. Four years of a publicly scrutinised relationship, tabloid speculation about breakups, and the particular pressure that comes from being a reality-TV-forged couple — all of it compressed into a single scene where Kundrra gets down on one knee and says something in Punjabi that his partner clearly didn't expect. It works because it's real, or at least as real as anything gets when cameras are present.

The rest of the show has drawn less generous assessments.

Critics have called *Desi Bling* "glossy but emotionally bankrupt," noting that its portrayal of Indian life in Dubai reduces a complex diaspora experience to designer shopping, manufactured social conflicts, and performative wealth. One reviewer described it as "crack scripted entertainment" — addictive but hollow. Others noted the show's "regressive gender dynamics" and the gap between the cast's curated personas and anything resembling authentic emotional depth.

The mixed reception is reflected on social media: fans praise the show's entertainment value and production quality while acknowledging that it feels scripted and superficial. "It's Dubai Bling but with Indian spices" is the consensus — which is precisely the formula Netflix was going for.

**Why This Show Matters for the Diaspora**

There are roughly 3.5 million Indians in the UAE, making them the country's largest expatriate community. Indian professionals — from construction workers and taxi drivers to tech executives and real estate moguls — are the backbone of Dubai's economy. The community spans every economic stratum, every Indian state, and every generation from recent migrants to families who have been there for decades.

*Desi Bling* shows exactly one sliver of this community: the wealthy, Instagram-visible, brand-conscious segment that spends its weekends at brunches in the Marina and its evenings at private gatherings in Palm Jumeirah villas. It's a valid slice of diaspora life, but it's a narrow one — and the criticism it's receiving reflects a growing discomfort among diaspora audiences with being represented primarily through consumption.

This is the tension that Indian reality television hasn't figured out. American reality TV solved it by leaning into genre diversity: *Real Housewives* serves the wealth fantasy, *Queer Eye* serves the empathy market, *The Bear* (technically scripted) serves the craft obsession. Indian reality TV is still stuck in the first mode — showing affluent Indians spending money and arguing about status — without offering the emotional or cultural depth that would give these shows staying power.

For NRIs in the Bay Area, London, or Toronto who watch *Desi Bling*, the experience is likely to be one of recognition mixed with mild embarrassment. Yes, Indians in Dubai live like this — some of them. No, this isn't the whole story. The show is entertaining enough to binge but shallow enough to forget, which is exactly where Netflix reality shows tend to land.

*Desi Bling* is streaming now on Netflix worldwide. All episodes are available.""",
    "diaspora_angle": "Desi Bling is the first major reality show centred on the Indian diaspora in Dubai — 3.5 million strong and the UAE's largest expat community. For NRIs in the US, UK, and Canada, it's a mirror held up to one slice of diaspora wealth culture, and the mixed reaction reflects a broader question: how does the Indian diaspora want to be seen on screen?",
    "vertical": "entertainment",
    "tags": ["Desi Bling", "Netflix", "Dubai", "Karan Kundrra", "Tejasswi Prakash", "reality TV", "Indian diaspora", "UAE"],
    "urgency": "standard",
    "sources": [
        {"url": "https://www.thedailyjagran.com/entertainment/desi-bling-twitter-review-netflix", "name": "Daily Jagran — Mixed Twitter Reviews"},
        {"url": "https://factpatrol.com/desi-bling-review-netflix", "name": "FactPatrol — Glitter, Gossip and Emotionally Bankrupt Billionaires"},
        {"url": "https://www.iwmbuzz.com/digital/netflix-desi-bling-review", "name": "IWMBuzz — 3.5/5 Stars Review"},
        {"url": "https://www.pinkvilla.com/entertainment/desi-bling-twitter-review-karan-kundrra-tejasswi-prakash", "name": "PinkVilla — 11 Tweets Before Watching"},
        {"url": "https://www.inshorts.com/en/news/karan-tejasswis-desi-bling-gets-mixed-reviews", "name": "Inshorts — Mixed Reviews Summary"}
    ],
    "slug": make_slug("desi-bling-netflix-indians-dubai-reality-show-kundrra-proposal"),
    "word_count": 730,
    "status": "published",
    "is_featured": False,
    "category": "Entertainment",
    "published_at": now,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
    "score_total": 70
})


# ══════════════════════════════════════════════════════════════
# ARTICLE 3: India at Cannes 2026 — Films, Chaos, and Growing Ambition
# ══════════════════════════════════════════════════════════════

a3_id = str(uuid.uuid4())

articles.append({
    "id": a3_id,
    "headline": "India Sent Films, Celebrities, and a Woman Miming 'Safety Pin' in French to Cannes This Year. All of It Mattered.",
    "subheadline": "The 79th Cannes Film Festival featured an Indian short in official selection, Supriya Pathak's directorial debut announcement, a Manto adaptation, and the logistical chaos of getting Huma Qureshi into a Banarasi saree on the French Riviera.",
    "body": """India's presence at the 79th Cannes Film Festival this year was characteristically Indian: ambitious, sprawling, occasionally chaotic, and impossible to reduce to a single narrative.

Start with the film that actually made it into official selection. *Shadows of the Moonless Nights*, directed by Mehar Malhotra, was one of only two Indian titles chosen from 2,750 worldwide submissions for the prestigious La Cinef section — Cannes' showcase for emerging filmmakers. Lead actor Prayrak Mehta and casting director Nikita Grover accompanied Malhotra to the festival. In a conversation with The Hollywood Reporter India's Anupama Chopra, the team described the selection as surreal — the kind of institutional validation that Indian independent cinema has historically struggled to access consistently.

Then there was Supriya Pathak Kapur, who chose Cannes to announce her directorial debut. *Our Story* is a loosely biographical film co-written with her daughter, Sanah Kapur, exploring three generations of women in the Pathak-Kapur family. The project is an Indo-Australian collaboration, produced under the banners Rabasusah and Films and Casting Temple, with Australian-Indian filmmaker Anupam Sharma as lead producer. Variety covered the announcement. The film is targeting a Toronto International Film Festival market debut in September 2026.

Pathak is best known internationally as Hansa from *Khichdi* and as a veteran of Bollywood ensembles from *Goliyon Ki Raasleela Ram-Leela* to *Wake Up Sid*. Her move into directing — at a Cannes announcement, with an international co-production, co-written with her daughter — represents exactly the kind of multigenerational, cross-border creative ambition that the Indian film industry's next chapter requires.

**The Manto Connection**

Elsewhere at the Marché du Film, actor Anupria Goenka was promoting *Bombay Stories*, directed by Rahhat Shah Kazmi and based on Saadat Hasan Manto's short story *Hatak*. The film, which also features Mouni Roy and Sushmita Singh, explores the lives of sex workers through a satirical lens. Manto — a partition-era writer whose unflinching portrayals of human weakness made him the subject of two separate Indian biopics — remains a name that opens doors at European film festivals. His work sits at the intersection of literary prestige and social provocation that Cannes has always rewarded.

Ahsaas Channa, known to younger Indian audiences from *Kota Factory* and *Hostel Daze*, attended the festival for the screening of her short film *Gudgudi* at the Short Film Corner. The Gudgudi team — director Manisha Makwana and producer Harshvardhan Patel of White Peacock Films — also announced two new feature projects: a folklore thriller about witch-hunting and a romantic drama.

**The Chaos Behind the Carpet**

But perhaps the most revealing portrait of India at Cannes came from The Hollywood Reporter India's backstage feature on what it actually takes to get Indian celebrities from their hotel rooms to the red carpet.

The details are gloriously specific. Stylist Tanya Ghavri had ten days to assemble Tara Sutaria's entire Cannes wardrobe — four to five months is standard — because Sutaria only confirmed her attendance on April 25. The solution was vintage beads, a corseted Vivienne Westwood gown, and Messika jewellery, themed around "old-world charm." No custom pieces. No assistant. Ghavri did everything herself.

Make-up artist Maria Asadi, working with Diana Penty, described the specific challenge of creating looks that translate simultaneously in person, under flash photography, and across international press syndication. "A Fierce Merlot smokey eye with a hint of bronze" was the solution — calibrated for humidity and the speed at which Cannes schedules collapse.

And then there was publicist Tamanna Punjabi's safety-pin crisis. Huma Qureshi was wearing a Banarasi saree. The team had to change their prep location at the last minute due to traffic. They arrived with steamer, outfit, and jewellery — but no safety pins. Punjabi went downstairs to buy some. "Nobody understood what I meant, so I was miming a safety pin to strangers in the middle of the French Riviera. Eventually, a kind Indian gentleman understood me and said he had some at his hotel nearby."

**What It All Means**

India's Cannes presence in 2026 is neither the breakthrough nor the disappointment that partisan narratives might suggest. It's a growing, messy, multi-track engagement with the world's most important film festival.

Official selection remains rare — two films from 2,750 is not penetration, it's a toehold. But the market activity (Bombay Stories, Our Story, Gudgudi's feature announcements), the celebrity infrastructure (Karan Johar, Tara Sutaria, Diana Penty, Huma Qureshi), and the sheer logistical ambition of mounting Indian sarees and Messika diamonds on the Croisette all point in the same direction: India is no longer showing up at Cannes as a guest. It's showing up as a permanent, if still occasionally disorganised, resident.

For the diaspora, this visibility matters. Every Indian film at Cannes, every saree on the red carpet, every short film that gets screened, quietly reinforces the idea that Indian stories belong on the global stage — not as exotic curiosities, but as cinema.""",
    "diaspora_angle": "India's Cannes 2026 presence — from official selection to Indo-Australian co-productions to Bollywood styling chaos — matters to NRIs because global festival visibility validates what diaspora audiences already know: Indian stories are world-class cinema. Supriya Pathak's Indo-Australian debut and Manto adaptations at the Marché du Film directly connect to diaspora filmmaking networks.",
    "vertical": "entertainment",
    "tags": ["Cannes 2026", "Indian cinema", "Supriya Pathak", "Huma Qureshi", "Tara Sutaria", "Bombay Stories", "Manto", "film festival"],
    "urgency": "standard",
    "sources": [
        {"url": "https://www.hollywoodreporterindia.com/features/interviews/cannes-2026-what-it-really-takes-to-pull-off-a-red-carpet-appearance", "name": "THR India — Behind the Red Carpet Chaos"},
        {"url": "https://www.hollywoodreporterindia.com/features/interviews/shadows-moonless-nights-cannes-la-cinef-selection", "name": "THR India — Shadows of the Moonless Nights Team"},
        {"url": "https://www.zoomtventertainment.com/entertainment/supriya-pathak-our-story-cannes-2026", "name": "Zoom TV — Supriya Pathak Directorial Debut"},
        {"url": "https://www.bollywoodhungama.com/news/bollywood/gudgudi-cannes-2026-feature-film-announcements/", "name": "Bollywood Hungama — Gudgudi Team Feature Projects"},
        {"url": "https://www.filmibeat.com/cannes-2026-anupria-goenka-bombay-stories", "name": "Filmibeat — Bombay Stories at Marché du Film"}
    ],
    "slug": make_slug("india-cannes-2026-films-celebrities-red-carpet-chaos"),
    "word_count": 780,
    "status": "published",
    "is_featured": False,
    "category": "Entertainment",
    "published_at": now,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
    "score_total": 68
})


# ══════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ══════════════════════════════════════════════════════════════

print(f"\n{'='*60}")
print(f"ENTERTAINMENT WRITER — BATCH 5 (22:30 PDT)")
print(f"{'='*60}\n")

for i, article in enumerate(articles, 1):
    try:
        result = sb_post("p2_articles", article)
        print(f"✅ Article {i}: {article['headline'][:80]}...")
        print(f"   ID: {article['id']}")
        print(f"   Slug: {article['slug']}")
        print(f"   Score: {article['score_total']}")
    except Exception as e:
        print(f"❌ Article {i} failed: {e}")

# ══════════════════════════════════════════════════════════════
# CREATE TOPICS (for tracking)
# ══════════════════════════════════════════════════════════════

topics = [
    {
        "id": str(uuid.uuid4()),
        "canonical_title": "Dhurandhar Raw & Undekha OTT dual-platform launch",
        "vertical": "entertainment",
        "urgency": "breaking",
        "score_diaspora": 80,
        "score_significance": 85,
        "score_recency": 95,
        "score_source_avail": 90,
        "score_total": 78,
        "signal_count": 15,
        "status": "published",
        "keywords": ["Dhurandhar", "Ranveer Singh", "Netflix", "JioHotstar", "OTT", "Raw Undekha"],
        "category": "entertainment",
    },
    {
        "id": str(uuid.uuid4()),
        "canonical_title": "Desi Bling Netflix reality show — Indians in Dubai",
        "vertical": "entertainment",
        "urgency": "standard",
        "score_diaspora": 85,
        "score_significance": 65,
        "score_recency": 90,
        "score_source_avail": 80,
        "score_total": 70,
        "signal_count": 10,
        "status": "published",
        "keywords": ["Desi Bling", "Netflix", "Dubai", "Karan Kundrra", "Tejasswi Prakash", "reality TV"],
        "category": "entertainment",
    },
    {
        "id": str(uuid.uuid4()),
        "canonical_title": "India at Cannes 2026 — films, debuts, and red carpet chaos",
        "vertical": "entertainment",
        "urgency": "standard",
        "score_diaspora": 70,
        "score_significance": 75,
        "score_recency": 85,
        "score_source_avail": 85,
        "score_total": 68,
        "signal_count": 8,
        "status": "published",
        "keywords": ["Cannes 2026", "Indian cinema", "Supriya Pathak", "Huma Qureshi", "film festival"],
        "category": "entertainment",
    },
]

print(f"\n--- Topics ---")
for topic in topics:
    try:
        sb_post("p2_topics", topic)
        print(f"✅ Topic: {topic['canonical_title']}")
    except Exception as e:
        print(f"❌ Topic failed: {e}")

print(f"\n✅ Entertainment batch 5 complete — {len(articles)} articles published")
