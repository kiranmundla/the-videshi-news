#!/usr/bin/env python3
"""Entertainment writer — Jr NTR birthday/empire + RHTDM nostalgia articles."""

import os, json, sys, uuid, requests
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ["SUPABASE_ANON_KEY"])
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ─── ARTICLE 1: Jr NTR Birthday / Empire ───

article1 = {
    "topic_id": "5e20ca0c-7e30-4b29-bcf8-2ec670d293d8",
    "headline": "Jr NTR Turns 42 Tomorrow With a ₹500 Crore Empire, a Private Jet, and Four Films That Could Change Everything",
    "subheadline": "From the man who made 'Naatu Naatu' a global earworm to a Bollywood debut opposite Hrithik Roshan — the Telugu superstar's wealth tells the story of a regional industry that's gone fully global.",
    "body": """The numbers alone are staggering. A net worth estimated at ₹500 crore. Per-film fees between ₹45 crore and ₹80 crore. An ₹80 crore private jet. A ₹25 crore duplex in Hyderabad's Jubilee Hills. A Lamborghini Urus, a Porsche 718 Cayman, a Richard Mille watch worth ₹4 crore, and a Patek Philippe Nautilus at ₹2.5 crore. This is not a Bollywood Khan's balance sheet. This is Jr NTR — a Telugu superstar who, until three years ago, most North Indians couldn't name.

**How RRR Rewired the Math**

When SS Rajamouli's *RRR* exploded in 2022, grossing over ₹1,200 crore worldwide and winning an Oscar for "Naatu Naatu," it didn't just make Jr NTR famous outside Andhra Pradesh and Telangana. It fundamentally restructured what a South Indian star could command. Before *RRR*, his fee hovered around ₹15-20 crore per film. After it, the number quadrupled. The three years he spent locked into Rajamouli's production schedule — turning down an estimated ₹100-200 crore in other projects — turned out to be the most profitable sacrifice in Indian cinema history.

The wealth goes beyond acting. Jr NTR co-owns the Telugu Titans kabaddi franchise, runs Nandamuri Taraka Ramarao Arts (his production house), and pulls ₹8-12 crore annually from brand endorsements with Zepto, Malabar Gold, and Appy Fizz. His real estate portfolio includes properties in Hyderabad, Bengaluru, and Mumbai — strategic footholds in every major film industry hub.

**The Four-Film Gauntlet**

What makes 2026-27 extraordinary for NTR isn't the past — it's the slate. *War 2* opposite Hrithik Roshan marks his Bollywood debut (reportedly for a ₹50 crore fee). *Dragon* with Prashanth Neel — the director who reinvented Yash with *KGF* — is now confirmed as a two-part epic releasing in 2027, with Anil Kapoor as the villain and a rumoured ₹1.5 crore daily shooting budget. *Devara: Part 2* continues a franchise whose first installment opened strong. And *God of War* with Trivikram Srinivas is a mythological drama with a budget that reportedly dwarfs anything NTR has done before.

A first-look glimpse for *Dragon* drops tonight — May 19, the eve of his 42nd birthday.

**The Jubilee Hills Life**

NTR's renovated Jubilee Hills mansion has become something of a mini-landmark. The duplex — eco-conscious with solar panels and a rainwater harvesting system — features a private theater, tropical gardens, and interiors that blend modern minimalism with traditional Telugu aesthetics. His farmhouse on the outskirts of Hyderabad, "Brindavanam," is where the extended Nandamuri clan gathers for family events. It's a dynasty, after all: his grandfather, N.T. Rama Rao, was both a legendary actor and the founder of the Telugu Desam Party, serving as Chief Minister of Andhra Pradesh.

**What This Means for the Diaspora**

For the Telugu diaspora in particular — one of the largest and most economically powerful Indian communities abroad — Jr NTR's rise represents something more than celebrity wealth. After decades of Bollywood monopolizing the Indian entertainment conversation in the West, *RRR* cracked the code. Screening parties in New Jersey, Dallas, and the Bay Area became communal events. "Naatu Naatu" at the Oscars was a moment of collective vindication.

Now, with *War 2* set to bridge the Hindi-Telugu divide and *Dragon* potentially rivalling *KGF*'s cult following, NTR is positioned as the first South Indian star to hold simultaneous commercial power across both industries. For NRIs who grew up watching him on pirated VCDs or streaming Aadi on early YouTube, the ₹500 crore figure isn't just about money. It's proof that Telugu cinema has arrived — not as Bollywood's regional cousin, but as its equal.

**What to Watch**

May 19 (tonight): *Dragon* first glimpse release. May 20: NTR's 42nd birthday, expected to bring more project announcements. *War 2* release date still locked for later in 2026. The next 18 months will determine whether NTR can sustain multi-industry dominance — or whether the Telugu-Bollywood crossover was a one-film phenomenon.""",
    "diaspora_angle": "Jr NTR's post-RRR trajectory represents a paradigm shift for the Telugu diaspora — the community whose screening parties, Oscar night celebrations, and grassroots promotion helped make Naatu Naatu a global moment. His ₹500 crore empire signals that South Indian cinema's economic power now matches its cultural influence abroad.",
    "vertical": "celebrity",
    "tags": ["Jr NTR", "Telugu cinema", "RRR", "Bollywood", "wealth", "Dragon", "War 2"],
    "urgency": "trending",
    "sources": [
        {"url": "https://www.indulgexpress.com/entertainment/celebs/2025/May/20/jr-ntr-turns-42-a-look-at-the-telugu-superstars-impressive-net-worth-and-upcoming-projects", "name": "Indulge Express — Jr NTR Birthday Profile"},
        {"url": "https://www.filmfare.com/news/bollywood/jr-ntrs-dragon-set-for-box-office-clash-with-hollywood-films-in-june-2027", "name": "Filmfare — Dragon Release and Box Office Analysis"},
        {"url": "https://bharathorizon.com/jr-ntr-net-worth-2025/", "name": "Bharat Horizon — Net Worth Breakdown"},
        {"url": "https://www.pinkvilla.com/entertainment/south/inside-jr-ntrs-rs-25-crore-duplex-house-in-jubilee-hills", "name": "Pinkvilla — Jubilee Hills Mansion"}
    ],
    "slug": "jr-ntr-42-birthday-500-crore-empire-dragon-war2-20260519",
    "word_count": 740,
    "status": "published",
    "is_featured": False,
    "category": "entertainment",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None
}

# ─── ARTICLE 2: RHTDM Vanity Van / Nostalgia ───

article2 = {
    "topic_id": "ea3509bf-1896-47de-9425-9118195ffd52",
    "headline": "Dia Mirza Changed Costumes in a South African Mall. Daisy Shah Huddled Near Lights to Stay Warm. The Making of RHTDM Was Chaos — and NRIs Made It Immortal.",
    "subheadline": "A background dancer's revelations from the set of Rehnaa Hai Terre Dil Mein remind us that Bollywood's most beloved NRI comfort film was made without vanity vans, proper toilets, or any expectation of success.",
    "body": """Daisy Shah remembers the cold. Not the scripted romance, not the songs, not R Madhavan's debut Bollywood charm — the cold. The year was 2001, and a 19-year-old Daisy was working as a background dancer on a song sequence for *Rehnaa Hai Terre Dil Mein* in South Africa, shivering between takes.

"When we would be asked to go for the shot, we would be freezing," Daisy recalled in a recent interview with Bollywood Bubble. "But the good part was that the makers did not ignore us. The next day, they got body suits to wear under our costumes so we don't feel cold."

The body suits were the luxury. Everything else was improvisation.

**No Vans, No Privacy, No Frills**

"I remember, Dia once had to change her costume during a song so she had to go to a mall to change her outfit," Daisy said. "We didn't have vanity vans. Even the main actors didn't have them, let alone the dancers. They would look for nearby malls and change there. Or we would be sitting in a restaurant and they would be doing their makeup there, and we would be doing it there too."

This was not some ultra-low-budget indie. This was a Pooja Entertainment production directed by Gautham Vasudev Menon, a Hindi remake of his Tamil hit *Minnale*. It starred R Madhavan, Dia Mirza (in her debut), and Saif Ali Khan. And yet the leading lady was changing in shopping centres.

Dia Mirza herself has corroborated the picture. In an interview with BBC Hindi, she described the conditions on location shoots of that era: "When we would go to locations to shoot songs, a basic thing like a toilet wouldn't be available. We would have to go behind trees, behind rocks, and three people would shield you with large sheets. We wouldn't have space to change clothes. Basically, we lacked access to privacy, access to basic hygiene."

**The Flop That Refused to Die**

*Rehnaa Hai Terre Dil Mein* released on October 19, 2001, and was declared a box office failure. Reviews were mixed. Dia Mirza later described the experience as "cruel" for a newcomer. But something strange happened in the years that followed: the film simply would not go away.

It circulated on pirated DVDs across Indian households in America, the UK, and the Gulf. "Zara Zara Behekta Hai" became the unofficial slow-dance anthem at desi college parties from Rutgers to UC Davis. University cultural shows choreographed routines to "Kaise Mujhe Tum Mil Gayi." Indian grocery stores stocked the DVD next to Parle-G and Maggi.

By the time YouTube made the songs globally accessible, RHTDM had already achieved what no marketing budget could buy: it became the film every NRI millennial had seen, argued about, and secretly loved. Maddy's earnest over-the-top pursuit of Reena — problematic in hindsight, irresistible in nostalgia — defined a generation's idea of desi romance.

**The Conversation Has Changed**

Dia Mirza has been candid about re-evaluating the film through a modern lens. She's spoken about being "uncomfortable" with Maddy's stalking of Reena and questioned why her character chose the man who deceived her over the one who was kind. It's a nuanced position — loving the film's legacy while acknowledging its blind spots — and it resonates with diaspora audiences who grew up adoring the film and now see it differently.

A sequel, *RHTDM 2*, has been discussed for years. In 2024, Dia joked that the cast "isn't old enough yet" for a reunion story. More recently, reports suggest a script has been found that all three leads could agree on, though nothing is confirmed.

The 2024 theatrical re-release packed cinemas across India and in NRI markets, with fans singing along to every song — a quarter-century later.

**Why It Matters**

Daisy Shah's memories aren't just behind-the-scenes trivia. They're a window into how radically Bollywood's production infrastructure has changed. Today's stars arrive with air-conditioned vanity vans, personal stylists, and contractual riders. In 2001, Dia Mirza was changing in a mall in Durban.

That the film made under those conditions became the most rewatched comfort film in the diaspora's collective memory is the kind of outcome no one on that freezing South African set could have predicted. Least of all a 19-year-old background dancer who would, years later, star opposite Salman Khan.""",
    "diaspora_angle": "RHTDM is arguably the single most shared Bollywood film in NRI millennial culture — circulated on pirated DVDs in the early 2000s, soundtracked at university garba nights, and re-released to packed diaspora theaters in 2024. Its behind-the-scenes reality reveals how far Indian cinema's production values have come.",
    "vertical": "nostalgia",
    "tags": ["RHTDM", "Dia Mirza", "Daisy Shah", "R Madhavan", "Bollywood", "nostalgia", "NRI culture"],
    "urgency": "evergreen",
    "sources": [
        {"url": "https://dailyheadlinez.com/2026/05/19/dia-mirza-didnt-have-a-vanity-van-during-rehnaa-hai-terre-dil-mein-with-r-madhavan-recalls-daisy-shah-who-was-a-background-dancer-that-time/", "name": "Daily Headlinez — Daisy Shah's Vanity Van Revelation"},
        {"url": "https://www.filmfare.com/news/bollywood/dia-mirza-speaks-out-about-being-uncomfortable-with-r-madhavan-stalking-her-in-rhtdm", "name": "Filmfare — Dia Mirza on Stalking in RHTDM"},
        {"url": "https://www.ottplay.com/news/as-rhtdm-re-releases-in-theatres-dia-mirza-recalls-initial-reception", "name": "OTTplay — RHTDM Re-Release and Initial Reception"},
        {"url": "https://www.bollywoodhungama.com/news/features/dia-mirza-opens-up-on-potential-rehnaa-hai-terre-dil-mein-sequel/", "name": "Bollywood Hungama — RHTDM Sequel Discussions"}
    ],
    "slug": "rhtdm-dia-mirza-daisy-shah-vanity-van-nri-cult-film-20260519",
    "word_count": 780,
    "status": "published",
    "is_featured": False,
    "category": "entertainment",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None
}

# ─── INSERT ARTICLES ───

for i, article in enumerate([article1, article2], 1):
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        aid = data[0]["id"] if isinstance(data, list) else data["id"]
        print(f"✅ Article {i} inserted: {aid}")
        print(f"   Headline: {article['headline'][:80]}...")
        print(f"   Slug: {article['slug']}")
    else:
        print(f"❌ Article {i} failed: {resp.status_code} {resp.text}")

# ─── UPDATE TOPIC STATUSES ───

# Mark written topics as published
for topic_id in ["5e20ca0c-7e30-4b29-bcf8-2ec670d293d8", "ea3509bf-1896-47de-9425-9118195ffd52"]:
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{topic_id}",
        headers=HEADERS,
        json={"status": "published"}
    )
    print(f"  Topic {topic_id[:8]}... -> published ({resp.status_code})")

# Mark non-Indian topics as rejected
# Metronade YouTuber (no India/diaspora connection)
# William Daniels open marriage (no India/diaspora connection)
for topic_id in ["321bc12d-8624-4758-bc17-23be514b7197", "557ff116-c744-42a3-b995-d18899c40164"]:
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{topic_id}",
        headers=HEADERS,
        json={"status": "rejected"}
    )
    print(f"  Topic {topic_id[:8]}... -> rejected ({resp.status_code})")

# Farhana Bodi at Cannes — decent but Cannes already well-covered today. Skip for now.
# Leave as pending for potential future pickup.

print("\n✅ Entertainment writer complete.")
