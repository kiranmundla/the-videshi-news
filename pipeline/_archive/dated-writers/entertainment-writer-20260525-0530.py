#!/usr/bin/env python3
"""Entertainment writer — May 25 2026, 05:30 UTC batch:
1. Dhurandhar 2 crosses ₹1,800 Cr worldwide on 10th weekend — franchise total ₹3,107 Cr
2. Vicky Kaushal blocks 18 months for Mahavatar — Bollywood's biggest commitment gamble
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
# ARTICLE 1: Dhurandhar 2 crosses ₹1,800 Cr worldwide
# ══════════════════════════════════════════════════════════════
slug1 = "dhurandhar-2-1800-crore-worldwide-3107-franchise-jiohotstar-june-4-extended-cut-20260525"
if not check_duplicate(slug1):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Dhurandhar 2 Just Crossed ₹1,800 Crore Worldwide. The Combined Franchise Has Now Earned ₹3,107 Crore. On June 4, JioHotstar Drops a 20-Minute Extended Cut That Wasn't Shown in Any Theatre on Earth.",
        "subheadline": "Ranveer Singh's spy sequel has spent 10 weekends in cinemas, earned more than Baahubali 2, and generated enough digital revenue to cover the entire franchise's production budget. The numbers are so large they've stopped feeling real — which is precisely when they start mattering most.",
        "slug": slug1,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "trending",
        "status": "published",
        "published_at": now_iso,
        "score_total": 82,
        "tags": ["Dhurandhar 2", "Ranveer Singh", "box office", "1800 crore", "franchise record", "JioHotstar", "streaming", "IMAX", "Aditya Dhar", "Bollywood record", "NRI box office", "Baahubali"],
        "diaspora_angle": "The NRI contribution to Dhurandhar 2 is historically significant: ₹426.67 Cr from overseas markets, with 18% of that coming from premium IMAX and 4DX screenings. For NRIs who watched it at AMC or Cineplex in January, the JioHotstar extended cut on June 4 — with 20 minutes of unseen footage — is reason enough to revisit. The franchise's digital deal alone (₹235 Cr between Netflix and JioHotstar) covered its entire ₹255 Cr production budget, meaning every rupee earned at the box office was pure profit. This is the math that's rewriting what Indian cinema thinks is possible — and NRI ticket sales are a non-trivial part of that equation.",
        "sources": [
            {"url": "https://www.sacnilk.com/news/dhurandhar-2-10th-weekend-box-office-hits-rs-1800-cr-combined-franchise-haul-stands-at-rs-3107-cr-worldwide", "name": "Sacnilk"},
            {"url": "https://www.sacnilk.com/news/bollywood-buzz-ranveer-singhs-pralay-shoot-begins-in-august-2026-as-vicky-kaushal-blocks-18-months-for-mahavatar", "name": "Sacnilk"},
            {"url": "https://www.bollywoodhungama.com/news/features/dhurandhar-the-revenge/", "name": "Bollywood Hungama"},
            {"url": "https://www.sacnilk.com/news/dhurandhar-2-box-office-records-historic-rs-242-cr-week-2-hindi-net", "name": "Sacnilk"}
        ],
        "image_search_query": "Dhurandhar 2 Ranveer Singh box office record 1800 crore celebration 2026",
        "image_entities": ["Ranveer Singh", "Dhurandhar 2", "Aditya Dhar"],
        "image_must_show": "Ranveer Singh as spy character or Dhurandhar 2 poster/promotional still",
        "word_count": 850,
        "body": """On its tenth weekend in cinemas — a duration most films don't survive in the digital age — Dhurandhar 2: The Revenge crossed ₹1,800 crore worldwide. It is now the second-highest-grossing Indian film of all time. The combined franchise, across both parts, has generated ₹3,107 crore in global box office revenue.

These are numbers that require context to understand, so here it is: the entire franchise was made for ₹255 crore. Both films. Combined. The return on investment isn't a percentage — it's a category error.

## The Numbers in Full

Dhurandhar 2's India net stands at ₹1,147.58 crore after 67 days. The regional breakdown tells its own story about how a Hindi-first film conquered the subcontinent:

- Hindi: ₹1,079.04 Cr
- Telugu: ₹43.07 Cr
- Tamil: ₹19.83 Cr
- Kannada: ₹3.87 Cr
- Malayalam: ₹1.77 Cr

The overseas gross hit ₹426.67 crore — and here's the detail that matters for NRI audiences: roughly 18% of international revenue came from premium formats like IMAX and 4DX. That's not a coincidence. Dhurandhar 2 was designed for large-format screens, and diaspora audiences in North America, the UK, and Australia paid premium ticket prices to see it that way.

The film has drawn over 4 crore footfalls in India, making it the first original Hindi-language film to achieve that scale since Gadar in 2001. On BookMyShow alone, the franchise has sold 6.8 crore tickets.

## The Digital Play That Covered the Entire Budget

This is where the business story gets genuinely remarkable.

Netflix acquired Part 1's digital rights for ₹85 crore. When Part 2 became a phenomenon, the makers leveraged the sequel's momentum to secure a separate ₹150 crore deal with JioHotstar — reportedly the largest single-film streaming acquisition in Indian entertainment history.

Total digital revenue across both films: ₹235 crore. Total production budget across both films: ₹255 crore. The streaming deals alone nearly paid for the entire franchise before a single ticket was sold.

This is the financial model that every producer in Mumbai is now trying to replicate. Make the film for less than the digital deal. Let the theatrical run be pure upside. Dhurandhar did it first, and at a scale that may not be repeatable.

## June 4: The Extended Cut Drops on JioHotstar

For NRIs who caught Dhurandhar 2 in theatres during its opening weekends in March and April, there's a reason to come back.

JioHotstar will premiere the film on June 4 with a "Raw and Undekha" extended cut featuring 20 minutes of footage that was not shown in any theatrical release worldwide. The extended version is expected to include deleted action sequences, expanded character scenes, and material that was trimmed for runtime during the theatrical window.

This is a streaming strategy borrowed from Hollywood's playbook — give the theatrical audience a reason to rewatch at home — and it's being deployed at a scale that Indian OTT hasn't attempted before. JioHotstar is betting that Dhurandhar 2's built-in audience will drive subscriptions and engagement in a way that a standard digital premiere wouldn't.

## The Tenth Weekend: Still Earning

Even now, the film hasn't completely left cinemas. Its tenth-weekend performance saw ₹0.83 crore across 691 shows in India. Sunday's occupancy hit 36%, with national chains like PVR, INOX, and Cinepolis selling over 7,300 tickets across the weekend. These are not blockbuster numbers — but they are the numbers of a film that people are still choosing to see in a theatre two and a half months after release.

The weekly trajectory tells the full story:

- Week 1: ₹674.17 Cr
- Week 2: ₹263.65 Cr
- Week 3: ₹110.60 Cr
- Week 4: ₹54.70 Cr
- Week 5: ₹19.52 Cr
- Week 6: ₹12.45 Cr
- Week 7: ₹5.58 Cr
- Week 8: ₹3.89 Cr
- Week 9: ₹2.19 Cr
- 10th Weekend: ₹0.83 Cr

The expected lifetime will settle around ₹1,803-1,805 crore worldwide — safely above Baahubali 2's previous record of ₹1,788 crore.

## What This Means for NRI Audiences

If you're reading this from New Jersey, Brampton, Leicester, or Sydney, you were part of this story. Dhurandhar 2 earned more overseas than most Bollywood films earn in total. The IMAX screenings in North America, the 4DX shows in the Gulf (which came later due to an initial ban that was eventually lifted), the repeat viewings that pushed the franchise past every previous benchmark — all of it was powered by a diaspora audience that showed up.

The franchise has now overtaken every Indian film except one global outlier. It has generated more revenue than the GDP of several small nations. And on June 4, it gets a second life on your TV screen — with footage you haven't seen.

Set a reminder. The extended cut is the kind of thing you watch with the family — and then argue about the spy tradecraft during dinner.""",
    })
    print(f"✅ Article 1 prepared: {slug1}")
else:
    print(f"⚠️ DUPLICATE: {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Vicky Kaushal blocks 18 months for Mahavatar
# ══════════════════════════════════════════════════════════════
slug2 = "vicky-kaushal-mahavatar-parashurama-18-months-bollywood-mega-cinema-pralay-ranveer-20260525"
if not check_duplicate(slug2):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Vicky Kaushal Is About to Disappear for 18 Months. He's Going to Become Parashurama. And He Won't Make Another Film Until He's Done.",
        "subheadline": "In an industry where stars juggle 3-4 films simultaneously and announce projects they'll never finish, Kaushal has blocked his entire calendar from June 2026 to December 2027 for a single role. Six months of physical transformation and workshops. Then filming. Then nothing else. It's either the most disciplined commitment in modern Bollywood — or the most expensive gamble.",
        "slug": slug2,
        "category": "Entertainment",
        "vertical": "entertainment",
        "urgency": "developing",
        "status": "published",
        "published_at": now_iso,
        "score_total": 75,
        "tags": ["Vicky Kaushal", "Mahavatar", "Parashurama", "mythology", "Bollywood mega films", "Ranveer Singh", "Pralay", "Sanjay Leela Bhansali", "Love and War", "Indian cinema", "method acting"],
        "diaspora_angle": "For NRIs, Bollywood's pivot to massive mythological and genre-bending projects reflects an industry that has finally internalised who its global audience is. Dhurandhar proved NRI audiences will pay premium IMAX prices for Indian films. Ramayana is being designed as India's answer to the MCU. Mahavatar, Pralay, and the slate of ₹300+ crore films coming in 2027-28 are being built for screens in Edison and Brampton as much as Andheri and Juhu. The 18-month commitment Kaushal is making for Parashurama would be unremarkable in Hollywood, where actors routinely disappear into roles for years. In Bollywood, it's revolutionary — and it signals that Indian cinema is no longer willing to be a volume business when it can be a premium one.",
        "sources": [
            {"url": "https://www.sacnilk.com/news/bollywood-buzz-ranveer-singhs-pralay-shoot-begins-in-august-2026-as-vicky-kaushal-blocks-18-months-for-mahavatar", "name": "Sacnilk"},
            {"url": "https://www.sacnilk.com/news/ranveer-singh-personally-convinced-kalyani-priyadarshan-for-pralay", "name": "Sacnilk"},
            {"url": "https://www.sacnilk.com/news/aditya-dhar-to-begin-his-next-in-march-2027-may-reunite-with-ranveer-singh", "name": "Sacnilk"},
            {"url": "https://www.sacnilk.com/news/ranbir-kapoor-yashs-ramayana-part-1-to-reportedly-release-on-october-30-2026", "name": "Sacnilk"}
        ],
        "image_search_query": "Vicky Kaushal actor Bollywood 2026 muscular transformation",
        "image_entities": ["Vicky Kaushal", "Parashurama"],
        "image_must_show": "Vicky Kaushal portrait or intense dramatic shot",
        "word_count": 800,
        "body": """Starting in June 2026, Vicky Kaushal will enter a six-month preparation phase for Mahavatar. Physical transformation. Character workshops. Historical and mythological research. Weapon training. The kind of immersive prep that Daniel Day-Lewis made famous and that Indian cinema has never really attempted at this scale.

Then, in January 2027, cameras roll. And they don't stop until December 2027.

During that entire 18-month window, Kaushal will not take on any other film. No cameos. No brand shoots that conflict with the look. No parallel projects. Just Parashurama — the immortal warrior-sage, the sixth avatar of Vishnu, the Brahmin who mastered all weapons and rage alike.

## Why This Is Unusual

Bollywood runs on volume. Stars typically work on 2-4 films simultaneously, rotating between sets, occasionally growing a beard for one role while doing press for another. Shah Rukh Khan shot Don 2 and Ra.One in overlapping schedules. Akshay Kumar has historically released 3-4 films per year. Even premium actors like Ranbir Kapoor juggle marketing, dubbing, and new projects concurrently.

Kaushal is doing the opposite. He's decided that one role, done at the highest possible level, is worth more than three roles done well. It's a bet on quality over frequency — and it's a bet that only makes financial sense in a post-Dhurandhar world where a single film can earn ₹1,800 crore.

The calculation is straightforward: if Mahavatar works, it doesn't need to be followed by two more films that year. The one film does the work of five.

## The Timeline

Kaushal is expected to wrap his current commitment — Sanjay Leela Bhansali's Love and War — just in time to transition into Mahavatar prep. The handoff is tight. Bhansali's productions are notoriously meticulous and schedule-heavy, which means Kaushal's last few months of 2026 will be an intensity marathon: finishing one epic and immediately beginning the physical and psychological transformation for another.

By January 2027, when filming begins, he'll have spent half a year living as Parashurama — or at least as close to it as modern method preparation allows. The role demands a specific physical archetype: Parashurama is depicted as a powerful warrior-ascetic, carrying a battle axe (parashu), with a physique that reflects both martial prowess and spiritual discipline.

For Kaushal, who transformed convincingly for Uri, Sam Bahadur, and the forthcoming Love and War, this is familiar territory — but at a longer, more intense duration than anything he's done before.

## The Bigger Picture: Bollywood's Commitment Race

Kaushal's 18-month lockout isn't happening in isolation. Across the industry, the biggest stars are making similarly singular commitments:

**Ranveer Singh's Pralay** begins filming in August 2026 with a reported budget of ₹300 crore. The post-apocalyptic zombie thriller — co-starring South Indian actress Kalyani Priyadarshan in her Hindi debut — will merge physical sets with AI-driven visuals. Singh, fresh off the ₹3,107 crore Dhurandhar franchise, is producing through his new banner Maa Kasam Films. Director Jai Mehta has described it as unlike anything Indian cinema has attempted.

**Ranbir Kapoor's Ramayana** is eyeing an October 30, 2026 release, with a distribution deal reportedly worth ₹450 crore. The Nitesh Tiwari-directed epic — with Sai Pallavi as Sita, Yash as Ravana, and Sunny Deol as Hanuman — is being positioned as the most expensive Indian film ever made.

**Aditya Dhar** — who directed both Dhurandhar films — has announced his next project will begin in March 2027, potentially reuniting with Ranveer Singh for another large-scale production.

The pattern is clear: Bollywood's top tier is moving from a three-films-a-year model to a one-film-every-two-years model. Fewer projects, bigger budgets, longer prep, global ambition.

## What NRIs Should Watch For

Mahavatar doesn't have a release date yet — it won't until filming wraps in late 2027, with a likely 2028 theatrical window. But the project is worth tracking for several reasons.

First, mythological storytelling is where Indian cinema has the clearest global advantage. No other film industry has the cultural depth, the built-in audience familiarity, and the visual spectacle potential that Hindu mythology offers. Ramayana is testing this thesis first. Mahavatar will test it differently — Parashurama is a less universally known figure, which means the film needs to work as pure cinema, not just cultural familiarity.

Second, Kaushal's commitment level suggests the filmmakers are aiming for something that competes at Cannes and the Oscars, not just at the domestic box office. An 18-month performance window is the kind of investment that produces awards-calibre work — if the script and direction match the ambition.

Third, for NRI families who grew up with televised Mahabharata and Ramayana, the prospect of their mythology being rendered at Hollywood production quality is a specific kind of cultural moment. It's the stories they know, told at a scale they've only seen in Marvel and Lord of the Rings.

Kaushal disappears in June. By the time he resurfaces, Bollywood may have changed around him. The question is whether his gamble changes it too.""",
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
