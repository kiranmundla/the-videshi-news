#!/usr/bin/env python3
"""Entertainment writer — May 25 2026, 21:30 UTC batch (14:30 PDT):
1. Cannes 2026 Red Carpet Scams — Indians paying €5,750+ for fake carpet access, people stranded, self-funded glamour narratives (Hollywood Reporter India)
2. Aaradhya Bachchan's Cannes Red Carpet Debut — 14-year-old walks with Aishwarya Rai, mother-daughter generational moment
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
# ARTICLE 1: Cannes 2026 Red Carpet Scams — India's Fake Glamour Economy
# ══════════════════════════════════════════════════════════════
slug1 = "cannes-2026-red-carpet-scams-india-paid-access-fake-glamour-influencers-stranded-20260525"
if not check_duplicate(slug1):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Indians Are Paying ₹7 Lakh to Walk a Red Carpet Nobody Invited Them To. Some Get Stranded in Cannes. Some Don't Even Get the Walk. The Fake 'India at Cannes' Economy Is Now an Industry.",
        "subheadline": "Hollywood Reporter India's investigation reveals a thriving black market where Indians pay €5,750 to €7,250 for red carpet access, fly to the French Riviera on promises from organisers who then vanish, and create entirely self-funded narratives of 'representing India.' The founder of Fetch India says she has received calls from people stranded in Cannes after being promised carpet appearances that never materialised.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 74,
        "tags": ["Cannes 2026", "red carpet scams", "India at Cannes", "influencers", "paid access", "Pankhuri Harikrishnan", "Fetch India", "film festival", "fake glamour", "diaspora", "NRI", "status culture"],
        "diaspora_angle": "For NRIs, the Cannes red carpet scam economy exposes something they recognise intimately from their own social circles: the desperate performance of status for audiences back home. The same psychology that drives the ₹7 lakh Cannes ticket purchase drives the curated NRI Instagram life — the right car, the right school district, the right vacation photos. The difference is scale. When someone in New Jersey posts a photo from a family trip to Paris, the stakes are low. When someone flies to Cannes, pays a scalper, gets a 30-second walk on a carpet during a non-premiere hour, and posts it as 'India at Cannes' to an audience that cannot distinguish between an official invitation and a purchased ticket, the stakes include national reputation. Pankhuri Harikrishnan's point — 'we are giving India a terrible name at an international platform' — lands differently for NRIs who have spent years building professional credibility abroad and now watch it diluted by people who can buy media coverage and amplification. The Cannes scam is the influencer economy's logical endpoint: if attention is currency, and currency can buy attention, then the loop closes and authenticity becomes irrelevant.",
        "sources": [
            {"url": "https://www.hollywoodreporterindia.com/features/interviews/india-at-cannes-2026-the-rise-of-red-carpet-scams-ticket-scalping-and-self-funded-narratives", "name": "Hollywood Reporter India"},
            {"url": "https://www.zoomtventertainment.com/bollywood/cannes-2026-namrata-lodaya", "name": "Zoom TV"},
            {"url": "https://whosthat360.com/cannes-film-festival-business", "name": "WhosThat360"}
        ],
        "image_search_query": "film festival red carpet empty corridor velvet rope glamour",
        "image_entities": ["Cannes Film Festival"],
        "image_must_show": "Red carpet corridor or velvet ropes at film festival, empty or atmospheric",
        "word_count": 780,
        "body": """Every May, a specific kind of Indian social media post begins to circulate. A woman in a couture gown. A man in a tuxedo. The Cannes Film Festival logo visible somewhere in the frame. The caption says something about "representing India" or "Indian talent at Cannes." The comments are full of fire emojis and national flags.

What the comments do not contain is a single question about why this person was there.

A **Hollywood Reporter India** investigation published on May 23 has pulled back the curtain on what has become a thriving industry: the **Cannes red carpet access market**, where Indians are paying between **€5,750 (approximately ₹5.5 lakh) for balcony seating** and **€7,250 (around ₹7 lakh) for premium orchestra access** to walk a carpet that nobody invited them to walk.

## The Scam Economy

**Pankhuri Harikrishnan**, founder and director of **Fetch India**, has attended Cannes since 2018. This year, she says, the situation spiralled.

"I've been called by various individuals who had been promised carpet appearances, but after they have landed in Cannes... the organisers vanished," she told the publication.

The sequence she describes is now a recognisable pattern: Indians book flights and hotels to the French Riviera on the promise of a red carpet walk. They arrive. The person who sold them the package disappears. They are stranded in one of the most expensive cities in Europe during its most expensive week, without the access they paid for and without a backup plan.

Some of them were told they could walk the carpet at **11 AM** — a time when no premiere is happening and the carpet is just a physical object sitting in the sun without cameras, crowds, or significance.

"Someone called me and asked, 'Can you get me a ticket?'" Harikrishnan recalls. "It was very last minute, but then they said, 'Would you be able to get us clothes too?'" The package being sold, in other words, includes not just the ticket but the costume — a complete rental of glamour for the duration of a photograph.

## The Three Legitimate Paths

According to Harikrishnan, there are only three real ways to walk the Cannes red carpet. The first is through **official festival accreditation or invitation** — which requires being part of the film industry in a meaningful capacity. The second is by being **associated with a film premiering** at the festival. The third is through **brands affiliated with Cannes** who are permitted to bring guests.

Everything else — the packages, the brokers, the WhatsApp forwards promising "VIP Cannes access" — is a grey market at best and a scam at worst.

A **2025 Screen Daily** article documented the pricing structure: a red carpet-only experience costs **$2,995 per person**. A Tier 1 premiere package for the biggest films goes for **$10,795** and includes hair and makeup, a limousine, and photographs — with a **Getty photographer** available for an additional fee.

The market is real. The question is whether the people buying access understand what they are actually purchasing.

## The Self-Funded Narrative

Harikrishnan identifies the core problem as a feedback loop that social media has made frictionless.

"Not only are you getting access because you can buy it, you're also getting media because you can buy that too," she says. "Together, therefore, you're creating a narrative that's completely self-funded."

This is the mechanism: pay for the ticket, pay for the outfit, pay for the photographer, post on your own social media, pay for promotion and bots to amplify the post, and within 24 hours you have a story that reads as "Indian personality shines at Cannes" — a story that no journalist wrote, no editor vetted, and no one at the festival endorsed.

"Earlier, even if you walked the carpet, how would anyone know unless someone covered you?" Harikrishnan points out. "You got covered in newspapers or magazines if you were of a certain repute." Media gatekeeping once filtered out those who did not belong. Social media removed the filter entirely.

## What This Means for the Audience at Home

The people most affected by the Cannes scam economy are not the people in Cannes. It is the **audience in India and the diaspora** that consumes the content without context.

When a viewer in Mumbai or Chicago sees a photo of someone in a gown on the Cannes red carpet, they have no way to distinguish between Aishwarya Rai Bachchan — who has been L'Oréal's brand ambassador at Cannes for over two decades — and someone who paid ₹7 lakh for a 30-second walk during a non-premiere window. The visual language is identical. The social proof is identical. The only difference is legitimacy, and legitimacy is invisible in a photograph.

This is why the phenomenon resonates differently for NRIs. The diaspora has spent decades building professional and cultural credibility abroad — credibility that is earned through work, not purchased through a broker. When "India at Cannes" becomes a commodity available to anyone with a credit card, it does not elevate Indian representation. It devalues it.

As Harikrishnan wrote on Instagram: "We're looking ridiculous with these fancy dresses that are going up on the carpet. And each festival has its own limit, right? So whatever these tickets are, whoever's buying them and selling them, they are dipping into the scope of others who could actually be there."

## The AI Layer

Adding another dimension to the artificiality, **Namrata Vishal Lodaya**, a Mumbai-based performance artist, noted that **AI-generated images of her Cannes appearance** circulated online, overshadowing genuine moments from the festival. Her conceptual art piece, titled **"The Inner Red Carpet,"** was intended to provoke thought about validation and ego — themes that the scam economy around her illustrated more effectively than any art installation could.

## The Demand Problem

Harikrishnan acknowledges that the ecosystem is unlikely to disappear. "The reason this is happening is because there's a demand, right? Someone's tapped into it and they're making lots of money off it."

The demand is not for cinema. Almost none of the people paying for access want tickets to the films screening at what is, fundamentally, a film festival. They want the photograph. They want the caption. They want the 48 hours of social media engagement that follows.

The Cannes red carpet has become, for a specific segment of Indian society, what a Harvard sweatshirt purchased from a street vendor is for tourists in Cambridge: a signifier of proximity to excellence, available for purchase, convincing only to those who have never been close enough to know the difference.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Aaradhya Bachchan's Cannes Red Carpet Debut
# ══════════════════════════════════════════════════════════════
slug2 = "aaradhya-bachchan-cannes-2026-red-carpet-debut-aishwarya-rai-mother-daughter-dynasty-20260525"
if not check_duplicate(slug2):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Aaradhya Bachchan Just Made Her Cannes Red Carpet Debut. She Is 14. She Walked in a Ruby-Red Gown Beside Her Mother. The Bachchan Dynasty Just Extended Its Cannes Timeline by a Generation.",
        "subheadline": "Aishwarya Rai Bachchan, who has walked the Cannes red carpet since 2002, appeared at the Lights on Women's Worth gala in a crystal-embellished blush-pink Sophie Couture gown. Her daughter Aaradhya, in a satin red gown with a glittering cape, walked beside her. The mother-daughter duo generated over 3,000 flash frames and became the most photographed appearance of the evening.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 71,
        "tags": ["Aaradhya Bachchan", "Aishwarya Rai", "Cannes 2026", "red carpet debut", "Bachchan family", "mother daughter", "fashion", "Sophie Couture", "dynasty", "diaspora", "NRI"],
        "diaspora_angle": "For the Indian diaspora, the image of Aaradhya walking the Cannes red carpet beside Aishwarya carries a weight that transcends celebrity gossip. Aishwarya Rai Bachchan's Cannes journey began in 2002, when she was the first Indian woman to be a L'Oréal ambassador at the festival. For 24 years, she has been the face that proved Indian women belonged on the world's most photographed carpet. Now her daughter stands beside her — not as a child being carried or held backstage, but as a 14-year-old in her own gown, with her own pose, drawing her own cameras. For NRI families who have watched Aishwarya's Cannes appearances become an annual cultural event — discussed in WhatsApp family groups, debated on Twitter, dissected on YouTube — the appearance of Aaradhya is a generational marker. It says: this did not end with one woman. This is a lineage now. The Bachchan name carried weight in Indian cinema for 50 years before it arrived at Cannes. The question of whether Aaradhya will choose to extend that timeline is hers alone, but the image of her walking the carpet at 14 has already become the answer the diaspora wanted.",
        "sources": [
            {"url": "https://www.filmfare.com/news/bollywood/aaradhya-makes-glamorous-debut-at-the-cannes-film-festival", "name": "Filmfare"},
            {"url": "https://www.indiaforums.com/article/aishwarya-rai-cannes-comeback-aaradhya-debut", "name": "India Forums"},
            {"url": "https://www.bollywoodbubble.com/bollywood-news/cannes-2026-aishwarya-rai-aaradhya-sophie-couture/", "name": "Bollywood Bubble"},
            {"url": "https://www.bollywoodhungama.com/news/bollywood/aishwarya-rai-cannes-2026-aaradhya/", "name": "Bollywood Hungama"},
            {"url": "https://www.panasiabiz.com/aishwarya-rai-aaradhya-cannes-2026/", "name": "Pan Asia Biz"}
        ],
        "image_search_query": "elegant mother daughter red carpet gala event evening gown formal",
        "image_entities": ["Aishwarya Rai Bachchan", "Aaradhya Bachchan", "Cannes"],
        "image_must_show": "Mother and daughter or elegant red carpet moment",
        "word_count": 720,
        "body": """On Friday evening at the **Cannes Film Festival 2026**, at the **Lights on Women's Worth** gala dinner, **Aishwarya Rai Bachchan** walked the red carpet in a crystal-embellished **blush-pink Sophie Couture gown** with floral detailing and a dramatic sheer cape. She has done this before. She has, in fact, done this every year since 2002, when she became the first Indian woman to serve as a **L'Oréal** ambassador at the festival. In 24 years, the Cannes red carpet has become as much a part of Aishwarya's annual calendar as Diwali.

What made Friday different was the person standing beside her.

**Aaradhya Bachchan**, 14 years old, walked the red carpet in a **satin ruby-red gown** with a glittering cape detail. Her hair was down in soft curls, styled in a side part. She wore red lips. She posed. She did not look like she was there for the first time.

According to **Pan Asia Biz**, the mother-daughter duo generated over **3,000 flash frames** and became the most photographed appearance of the evening.

## The 24-Year Runway

Aishwarya Rai Bachchan's Cannes timeline is not just a personal achievement — it is a chronological record of how India's relationship with international glamour has evolved.

In **2002**, her first year at the festival, she was a former **Miss World** with a handful of Bollywood films. India's presence at Cannes was minimal and largely confined to arthouse cinema. The idea of an Indian actor being a cosmetics brand ambassador at the world's most prestigious film festival was novel enough to be newsworthy in itself.

By **2016**, she had been attending for 14 years and brought Aaradhya — then a toddler — to the festival for the first time. The images of Aaradhya in Aishwarya's arms on the Croisette were among the most shared celebrity photographs of that year in India.

In **2023**, she appeared at Cannes amid tabloid speculation about her marriage to **Abhishek Bachchan**, walking the carpet in a dramatic black and gold hooded gown that was immediately read as a statement of independence. She brought Aaradhya, who was photographed backstage but did not walk the carpet.

In **2026**, Aaradhya is no longer backstage. She is not in her mother's arms. She is beside her, in her own gown, with her own photographers.

## Earlier That Week

Before the gala dinner appearance, Aishwarya had already made her mark at Cannes 2026. Her first red carpet look was a **futuristic abyss-blue Amit Aggarwal gown** — by an Indian designer — that drew comparisons to armour. The choice of Aggarwal, known for his recycled polymer textile work, was noted by fashion critics as a deliberate departure from the European luxury houses that dominate Cannes fashion.

On her second day, she wore a **white pantsuit with a feather wrap** for daytime events, where she was filmed signing autographs while fans chanted her name. The videos went viral in India, reinforcing the specific mythology that has built around Aishwarya at Cannes: that she is not just attending, she is being received.

**Kangana Ranaut**, not typically an ally, publicly defended Aishwarya against online trolls who criticised her appearance. "She is not here to please critics," Kangana said — a rare moment of solidarity in an industry where public support between A-list actors is carefully rationed.

## What Aaradhya's Debut Means

Aaradhya Bachchan's red carpet walk was not announced in advance. There was no press release, no brand partnership disclosed, no promotional framework. She simply appeared beside her mother, in a coordinated but distinct outfit, and walked.

The lack of commercial context is what makes the moment significant. Every other high-profile appearance at Cannes comes wrapped in a brand deal, a film promotion, or a PR strategy. Aaradhya's appearance came wrapped in nothing except the fact that her mother wanted her there and she chose to walk.

Whether this is the beginning of a public career or a one-time family moment is a question only Aaradhya can answer, and she is 14 — an age when most questions of that magnitude should remain unanswered. But the image now exists. It will be referenced every year for the next decade, every time Aishwarya returns to Cannes, every time Aaradhya does anything publicly. It is the kind of photograph that creates its own gravity.

## The Dynasty Question

The **Bachchan** name has been present in Indian cinema for over 50 years. **Amitabh Bachchan** redefined what a Hindi film hero could be in the 1970s. **Abhishek Bachchan** carried the name into the 2000s with a career that was always measured against his father's. **Aishwarya Rai**, through marriage and through her own work, extended the Bachchan brand into international spaces that neither Amitabh nor Abhishek had occupied.

Now Aaradhya — who carries the Bachchan name, the Rai genes, and 24 years of Cannes institutional memory — stands on the same carpet her mother first walked when the world did not yet know India could belong there.

For NRI families who have watched this story unfold across two decades — who saw the first Cannes appearance as a novelty, the middle years as a tradition, and now the daughter's debut as a succession — the moment is less about celebrity and more about inheritance. It is about the specific Indian understanding that what one generation builds, the next generation is expected to either extend or explain why they chose not to.

Aaradhya Bachchan, at 14, in a ruby-red gown, beside her mother in pink, has not yet had to explain anything. The carpet was there. She walked it. The cameras found her without being asked.""",
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
# IMAGE SOURCING — Pexels editorial images
# ══════════════════════════════════════════════════════════════
print("\n── Image Sourcing ──")

PEXELS_KEY = None
pexels_env = Path.home() / "workspace/.env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if k.strip() == "PEXELS_API_KEY":
                PEXELS_KEY = v.strip()

def search_pexels(query, per_page=5):
    if not PEXELS_KEY:
        return []
    r = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "per_page": per_page, "orientation": "landscape"},
        timeout=10
    )
    if r.status_code == 200:
        return r.json().get("photos", [])
    print(f"  Pexels HTTP {r.status_code}")
    return []

image_queries = {
    slug1: "film festival red carpet velvet rope empty glamorous evening",
    slug2: "elegant mother daughter formal event gala evening gown red carpet",
}

for slug, query in image_queries.items():
    photos = search_pexels(query)
    if photos:
        photo = photos[0]
        img_url = photo["src"]["large2x"]
        print(f"  Pexels: {photo['id']} for {slug[:50]}")
        status = sb_patch(
            "p2_articles",
            f"slug=eq.{slug}",
            {"image_url": img_url}
        )
        print(f"  PATCH image_url → HTTP {status}")
    else:
        print(f"  ⚠️ No Pexels result for: {query}")


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
