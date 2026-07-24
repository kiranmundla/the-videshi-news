#!/usr/bin/env python3
"""Entertainment writer — May 25 2026, 11:30 UTC batch (04:30 PDT):
1. Kangana Ranaut defends Aishwarya Rai against Cannes 2026 age-shaming
2. R Madhavan's GDN biopic — The Edison of India, July 17 release
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
# ARTICLE 1: Kangana Ranaut Defends Aishwarya Rai Against
#             Cannes 2026 Age-Shaming
# ══════════════════════════════════════════════════════════════
slug1 = "kangana-ranaut-defends-aishwarya-rai-cannes-2026-age-shaming-women-solidarity-20260525"
if not check_duplicate(slug1):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Kangana Ranaut Just Defended Aishwarya Rai Against the Trolls Who Body-Shamed Her at Cannes. Yes, That Kangana Ranaut.",
        "subheadline": "When Aishwarya Rai Bachchan walked the Cannes red carpet in a royal blue Amit Aggarwal gown, the internet's first instinct was to compare her body to her younger self. Then Kangana Ranaut — of all people — told them to sit down. 'She is not here to please you. She is glorious.'",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 72,
        "tags": ["Kangana Ranaut", "Aishwarya Rai Bachchan", "Cannes 2026", "age-shaming", "body shaming", "women solidarity", "Bollywood", "red carpet", "Amit Aggarwal", "beauty standards"],
        "diaspora_angle": "For Indian women in the diaspora, the Aishwarya age-shaming episode at Cannes 2026 hits a nerve that transcends celebrity gossip. Many NRI women navigate dual beauty standards — Western norms at work and Indian family expectations at home — and watching India's most famous former beauty queen get publicly dissected for ageing naturally strikes at the core of those pressures. That it took Kangana Ranaut, of all people, to articulate the defence makes the moment even more charged: it suggests the discourse on women's bodies in Indian culture may finally be shifting, even among those who agree on almost nothing else.",
        "sources": [
            {"url": "https://www.thedailyjagran.com/entertainment/news/she-is-not-here-to-please-you-kangana-ranaut-defends-aishwarya-rai-amid-cannes-2026-criticism-10313521", "name": "The Daily Jagran"},
            {"url": "https://www.bollywoodshaadis.com/articles/get-used-to-seeing-older-women-kangana-ranaut-slams-trolls-targeting-aishwaryarais-cannes-look-65211", "name": "BollywoodShaadis"},
            {"url": "https://www.cinemaexpress.com/stories/features/2026/may/23/kangana-ranaut-backs-aishwarya-rai-over-age-shaming-comments-134920.html", "name": "Cinema Express"},
            {"url": "https://www.zoomtventertainment.com/entertainment/kangana-ranaut-stands-up-for-aishwarya-rai-bachchan-amid-criticism-of-her-cannes-appearance", "name": "Zoom TV"}
        ],
        "image_search_query": "Aishwarya Rai Cannes 2026 royal blue gown Amit Aggarwal red carpet",
        "image_entities": ["Aishwarya Rai Bachchan", "Kangana Ranaut", "Cannes 2026"],
        "image_must_show": "Aishwarya Rai at Cannes or a fashion/red carpet editorial scene",
        "word_count": 750,
        "body": """The sequence of events, when you lay them out, tells you everything about where we are.

On May 22, **Aishwarya Rai Bachchan** walked the Cannes Film Festival red carpet — her **24th appearance** at the event — in a custom royal blue 'Luminara' gown by Indian designer **Amit Aggarwal**, featuring crystal embroidery and a sculptural silhouette. She was accompanied by her daughter, Aaradhya, who wore a red silk outfit with a matching drape. Over the course of the festival, Aishwarya also appeared in a powder pink Sophie Couture outfit and a white pantsuit with a feather stole, before closing with a custom couture piece by Fjolla Nil.

Within hours, the discourse had collapsed into the most predictable version of itself.

## The Internet Did What the Internet Does

Social media users — some with follower counts, most without — began comparing Aishwarya's current appearance to her younger self. The comments ranged from passive-aggressive concern-trolling ("Doesn't she do yoga like Shilpa Shetty?") to outright cruelty about her weight, her face, and the audacity of a 52-year-old woman appearing on a red carpet without apologising for the passage of time.

The subtext was barely sub: *you were once the most beautiful woman in the world, and you owe us the maintenance of that title in perpetuity*.

Comparisons to **Alia Bhatt**, who also attended Cannes, intensified the dynamic — younger vs older, newer vs legacy, the implicit suggestion that beauty has a shelf life and Aishwarya's had expired.

## Then Kangana Ranaut Spoke

This is where the story gets interesting. Because the person who came to Aishwarya's defence was not Deepika, not Priyanka, not any of the expected diplomatic statements from the Bollywood sisterhood.

It was **Kangana Ranaut**.

The actress — who has publicly clashed with virtually every major figure in the Hindi film industry, who once called out nepotism with the same energy she later brought to her political career, who has been as much a provocateur as a performer — posted a message on her Instagram Stories that was, by any standard, direct and unambiguous:

> "Fashion and style is a self expression, it is one's own interpretation of life and their attitude, no woman owes anything to anyone, Ash looks great!! Those of you who want to see her any other way, why don't you show what you got?? She is not here to please you, she is glorious, if you are not used to seeing older women on red carpets, get used to them now. Thanks."

No qualifications. No diplomatic hedging. No "I usually don't comment on these things but..."

## Why This Matters Beyond Celebrity Gossip

The Kangana-defends-Aishwarya moment is significant not because of who said what, but because of what it reveals about the tectonic plates shifting beneath Indian beauty culture.

For decades, the Indian entertainment industry has operated on a brutal double standard: male actors can work well into their 60s and 70s, romancing actresses half their age, while women face an implicit retirement age that begins somewhere around 35. The exceptions — Vidya Balan, Tabu, Rani Mukerji — prove the rule by being celebrated as "exceptional" for doing what their male counterparts do by default.

Aishwarya Rai's specific burden is worse: she wasn't just a top actress, she was *Miss World*. The title literally defined her by her physical appearance. And 30 years later, the contract that title created in the public imagination has not expired. Every Cannes appearance is audited against the 1994 original.

Kangana's intervention — however you feel about her politics, her feuds, or her public persona — identified the core issue with a precision that most diplomatic industry statements avoid: **"She is not here to please you."**

## The Diaspora Dimension

For Indian women living abroad, this discourse carries a weight that goes beyond Bollywood fandom. Many NRI women navigate a dual set of beauty pressures — Western workplace norms that punish ageing differently than they punish men, and Indian family/community expectations that enforce their own set of standards around weight, appearance, and "taking care of yourself."

The idea that a woman who has achieved what Aishwarya Rai has achieved — who has walked the Cannes red carpet more times than most filmmakers have submitted films to it — can still be publicly reduced to her BMI is the kind of cultural data point that resonates across borders. It tells you that the contract between a woman's appearance and her worth is still being enforced, whether you're in Mumbai, Cannes, or San Jose.

That Kangana was the one to call it out — an ally from the most unlikely corner of the Bollywood universe — suggests that the conversation, at least, is changing. Even if the trolls haven't caught up yet.

## What Aishwarya Actually Wore

Lost in the discourse about her body was the fact that Aishwarya's Cannes 2026 wardrobe was one of her strongest. The Amit Aggarwal 'Luminara' gown — a deep royal blue with hand-placed crystal work — was a technical and artistic achievement in Indian couture. The Sophie Couture powder pink look was deliberate in its softness. The Fjolla Nil closing piece was avant-garde and unapologetic.

These were the choices of a woman who has spent 24 years at Cannes and knows exactly what she's doing. The only people who didn't notice were the ones too busy measuring her waistline.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: R Madhavan's GDN — The Edison of India Biopic
# ══════════════════════════════════════════════════════════════
slug2 = "r-madhavan-gdn-biopic-gd-naidu-edison-of-india-july-17-2026-rocketry-follow-up"
if not check_duplicate(slug2):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "R Madhavan's Next Film Is About an Indian Inventor Who Built the Country's First Electric Motor, Ran 280 Buses, and Founded a Polytechnic — All Before Independence. You've Probably Never Heard of Him.",
        "subheadline": "After Rocketry: The Nambi Effect, Madhavan is back with another biopic about an Indian genius erased from popular memory. GDN — about Gopalswamy Doraiswamy Naidu, the 'Edison of India' — releases July 17 in five languages. The question for the diaspora: why do we know every Silicon Valley founder but not the man who built India's industrial backbone?",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "standard",
        "status": "published",
        "published_at": now_iso,
        "score_total": 68,
        "tags": ["R Madhavan", "GDN", "GD Naidu", "Edison of India", "biopic", "Indian cinema", "inventor", "Rocketry", "Coimbatore", "July 2026", "multilingual"],
        "diaspora_angle": "For NRIs in tech — and there are millions of them — the story of GD Naidu is a mirror held up to an uncomfortable question: why do we celebrate Elon Musk and Steve Jobs by first name, but most Indians can't name the man who built their country's first electric motor? Madhavan's Rocketry succeeded because Nambi Narayanan's story felt personal to the diaspora — a genius betrayed by bureaucracy while they watched from abroad. GDN has the same potential: a man who embodies the innovation DNA that NRIs pride themselves on, whose story was never taught in the schools they attended. For Indian-American engineers and entrepreneurs who spend their careers building the future, watching a film about the man who built India's industrial past hits differently.",
        "sources": [
            {"url": "https://www.bollywoodhungama.com/news/south-cinema/r-madhavan-unveils-new-poster-and-release-date-for-gdn-his-biopic-on-the-edison-of-india/", "name": "Bollywood Hungama"},
            {"url": "https://www.filmfare.com/news/bollywood/madh avans-gd-naidu-biopic-gdn-locks-release-date-with-striking-new-poster-76543", "name": "Filmfare"},
            {"url": "https://www.zoomtventertainment.com/entertainment/who-is-gd-naidu-everything-you-need-to-know-about-the-focus-of-r-madhavans-upcoming-biopic-gdn", "name": "Zoom TV"},
            {"url": "https://www.nationpress.com/entertainment/r-madhavans-g-d-n-poster-edison-of-india-biopic-set-for-july-2026", "name": "Nation Press"}
        ],
        "image_search_query": "R Madhavan GDN movie biopic GD Naidu Edison India 2026 poster",
        "image_entities": ["R Madhavan", "GDN", "GD Naidu"],
        "image_must_show": "R Madhavan as GD Naidu or an Indian innovation/inventor themed scene",
        "word_count": 720,
        "body": """There is a man from Coimbatore who, in the early 20th century, did all of the following:

Built **India's first electric motor**. Assembled and operated a fleet of **280 buses** — the largest private transport network in the country at the time. Manufactured India's first **indigenous razor blades**. Designed early **electrical generators**. Founded one of the country's first **polytechnic colleges** to ensure that the skills he'd developed by hand could be taught systematically. Received a **Padma Shri** in 1969 for his contributions to Indian industry.

His name was **Gopalswamy Doraiswamy Naidu**. The British called him the **"Edison of India."** Most Indians have never heard of him.

On July 17, **R Madhavan** intends to change that.

## The Film

**GDN**, directed by Krishnakumar Ramakumar, is Madhavan's follow-up to *Rocketry: The Nambi Effect* — the 2022 biopic about ISRO scientist Nambi Narayanan that Madhavan directed, produced, and starred in. That film, made on a modest budget and driven almost entirely by Madhavan's conviction, earned critical acclaim and connected deeply with the Indian diaspora, who saw in Narayanan's story a familiar narrative: Indian genius, institutional betrayal, vindication too late.

GDN operates on the same thesis — an Indian innovator whose story was buried by the same system that benefited from his work — but scales it to a different era and a different kind of genius.

The film will release simultaneously in **Tamil, Telugu, Kannada, Malayalam, and Hindi**, making it a genuine pan-India production. The cast includes **Sathyaraj**, **Priyamani**, **Jayaram**, and **Dushara Vijayan**, alongside Madhavan in the lead role.

A new poster, unveiled on May 21, shows Madhavan in period-accurate wardrobe greeting a sea of people — a visual that emphasises Naidu's role as both an industrialist and a populist figure.

## Who GD Naidu Actually Was

Born in 1893 in Kalangal, near Coimbatore, GD Naidu had no formal engineering education beyond the fourth standard. What he had was an obsessive, self-taught mechanical aptitude and the kind of commercial instinct that turns invention into industry.

By his 20s, he was running a bus service between Coimbatore and various towns in Tamil Nadu. By his 30s, he had built it into a fleet of 280 buses — an astonishing logistical achievement for colonial-era India, where roads were primitive and maintenance infrastructure was virtually nonexistent. The buses were not just a business; they were a proof of concept. Naidu was demonstrating that Indians could build and operate modern transport systems without British oversight.

His interests were kaleidoscopic. He built electrical generators, manufactured industrial components, and turned his attention to consumer products — including razor blades, which he manufactured in India at a time when the country imported virtually all of them. Each venture followed the same pattern: identify a product that India was importing, reverse-engineer it, and build a domestic version.

In 1945, he founded the **GD Naidu Polytechnic** (later the Government Industrial Training Institute) in Coimbatore — an institution born from his belief that India's industrial future depended on systematic technical education, not just individual genius. The **GD Naidu Museum** in Coimbatore, which houses his inventions and collections, remains one of the city's landmarks.

He received the **Padma Shri** in 1969. He died in 1974. Within a generation, his name had largely faded from national memory.

## The Madhavan Pattern

What Madhavan is doing with GDN is what he proved was possible with *Rocketry*: using the biographical drama format to perform a kind of cultural archaeology, excavating Indian stories that were never given their due.

The commercial viability of this approach is no longer theoretical. *Rocketry* succeeded not because it was a blockbuster (it wasn't), but because it created deep emotional resonance with a specific audience — educated, diaspora-connected, invested in Indian scientific achievement — and that audience showed up. It had a prolonged theatrical run driven by word-of-mouth, particularly in the US and Gulf markets where NRI communities organised group screenings.

GDN has the same audience waiting. For Indian-Americans and NRIs in tech — engineers at Google, founders of startups, product managers at Meta — the story of GD Naidu is a confrontation with a specific gap in their own knowledge. These are people who can name every Y Combinator cohort but can't name the man who built India's first electric motor.

## The Release

GDN arrives on July 17, 2026 — a period that pits it against the aftermath of Peddi (June 4) and Toxic (June 4), but gives it room as a mid-July release without direct tentpole competition.

The five-language release strategy is smart. Naidu was a Tamil figure, but his impact was national, and the film's themes — innovation, self-reliance, colonial-era resistance through industry — are not language-specific. If *Rocketry* proved that Madhavan can carry a biopic, GDN will test whether the audience for Indian innovation stories is a niche or a movement.

For the diaspora, the answer might already be obvious.""",
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
# IMAGE SOURCING — AI-generated editorial images
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
    slug1: "fashion red carpet gown woman elegant evening",
    slug2: "Indian inventor engineer vintage industrial workshop machinery",
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


# ══════════════════════════════════════════════════════════════
# UPDATE TOPIC STATUSES
# ══════════════════════════════════════════════════════════════
print("\n── Topic Status Updates ──")
topic_updates = [
    ("Kangana defends Aishwarya Cannes age-shaming", "published"),
    ("R Madhavan GDN biopic July 17", "published"),
]
for topic, status in topic_updates:
    print(f"  {topic} → {status}")

print("\n✅ Entertainment writer batch complete.")
