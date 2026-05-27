#!/usr/bin/env python3
"""Entertainment writer — May 27 2026, 06:00 UTC (May 26 23:00 PDT) batch:
1. Nepal's Elephants in the Fog — first Nepali film to win at Cannes, Un Certain
   Regard Jury Prize, Kinnar community story, while India's Cannes coverage was
   consumed by red carpet scam narratives.
2. Dhurandhar gets its Star Gold TV premiere on May 30 — the cultural ritual of the
   Bollywood TV premiere in the streaming era, what it means for NRIs, and why this
   ₹3,000 crore franchise's small-screen debut still matters.
+ Score decay
"""

import json, os, uuid, requests, urllib.parse, math
from datetime import datetime, timezone
from pathlib import Path

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
    r = requests.patch(
        f"{SB_URL}/rest/v1/{table}?{filters}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json=data,
        timeout=30,
    )
    return r.status_code


def check_duplicate(slug):
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
        headers=HEADERS,
        timeout=15,
    )
    return len(r.json()) > 0 if r.status_code == 200 else False


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get(
                "thumbnail", {}
            ).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


PEXELS_KEY = None
pexels_env = Path.home() / "workspace/.env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if k.strip() == "PEXELS_API_KEY":
                PEXELS_KEY = v.strip()


def fetch_pexels_image(query, fallback=None):
    if not PEXELS_KEY:
        return None
    for q in [query, fallback]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    return photos[0]["src"]["large2x"]
        except Exception:
            pass
    return None


def upload_image_to_supabase(img_url, filename):
    try:
        img_data = requests.get(
            img_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0"}
        ).content
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        r = requests.post(
            upload_url,
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true",
            },
            data=img_data,
            timeout=30,
        )
        if r.status_code in (200, 201):
            return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return img_url


# --- Score decay ---
print("Running score decay...")
try:
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?status=eq.published&score_total=gt.10&select=id,score_total,published_at",
        headers=HEADERS,
        timeout=30,
    )
    if r.status_code == 200:
        now_ts = datetime.now(timezone.utc)
        decayed = 0
        for art in r.json():
            try:
                pub = datetime.fromisoformat(art["published_at"].replace("Z", "+00:00"))
                age_h = (now_ts - pub).total_seconds() / 3600
                if age_h > 6:
                    factor = max(0.3, math.exp(-0.02 * (age_h - 6)))
                    new_score = max(10, int(art["score_total"] * factor))
                    if new_score < art["score_total"]:
                        sb_patch("p2_articles", f"id=eq.{art['id']}", {"score_total": new_score})
                        decayed += 1
            except Exception:
                pass
        print(f"  Decayed {decayed} articles")
except Exception as e:
    print(f"  Score decay error: {e}")

now = datetime.now(timezone.utc)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S")

articles = []

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 1: Nepal's Elephants in the Fog wins at Cannes 2026
# ─────────────────────────────────────────────────────────────────────
slug1 = "nepal-elephants-in-the-fog-cannes-2026-un-certain-regard-jury-prize-kinnar-india-diaspora-20260527"
if not check_duplicate(slug1):
    art1_id = str(uuid.uuid4())
    articles.append(
        {
            "id": art1_id,
            "headline": "A Nepali Film About a Transgender Community Just Won at Cannes. It Is the First Film From Nepal to Ever Win There. India Sent Influencers.",
            "subheadline": "Abinash Bikram Shah's 'Elephants in the Fog' won the Un Certain Regard Jury Prize at the 79th Cannes Film Festival — the first Nepali film to win any award at the world's most prestigious film festival. The film follows a Kinnar community in Nepal's Terai plains, where a matriarch faces an impossible choice between love and duty when a woman goes missing. Meanwhile, India's Cannes 2026 narrative was consumed by debates over who paid ₹7 lakh to walk a red carpet. For a diaspora that has spent decades celebrating Indian cinema's global reach, the question is uncomfortable: why was South Asia's most significant Cannes moment this year not Indian?",
            "slug": slug1,
            "category": "Entertainment",
            "vertical": "entertainment",
            "urgency": "standard",
            "status": "published",
            "published_at": now_iso,
            "score_total": 80,
            "tags": [
                "Cannes 2026",
                "79th Cannes Film Festival",
                "Elephants in the Fog",
                "Nepal",
                "Abinash Bikram Shah",
                "Un Certain Regard",
                "Kinnar",
                "transgender",
                "South Asian cinema",
                "India",
                "NRI",
                "diaspora",
            ],
            "diaspora_angle": "For the Indian diaspora, Cannes has always been a proxy measure for whether the world takes South Asian storytelling seriously. When Satyajit Ray received his honorary Palme d'Or in 1992, it was a point of pride for every NRI who had ever been asked to explain Indian cinema. When Payal Kapadia won the Grand Prix in 2024 for 'All We Imagine as Light,' it was shared in diaspora group chats as proof that India could compete with anyone. But in 2026, the most significant South Asian win at Cannes came from Nepal — a country whose entire film industry is smaller than the production budget of a single Bollywood tentpole. The fact that 'Elephants in the Fog,' a film about a marginalised Kinnar community, won the Un Certain Regard Jury Prize while India's Cannes presence was dominated by influencer red carpet photos and ₹7 lakh access scams is a contrast that the diaspora cannot easily explain away. It raises a question that NRIs in the US, UK, and Canada are increasingly asking: does India's massive film industry, which produces more movies than any country on Earth, still have something to say at the world's most important film festival — or has it outsourced that ambition to red carpet content creation?",
            "sources": [
                {
                    "url": "https://indulgexpress.com/entertainment/movies/cannes-2026-elephants-in-the-fog-nepal-history-win",
                    "name": "Indulge Express",
                },
                {
                    "url": "https://www.devdiscourse.com/article/entertainment/nepals-elephants-fog-cannes-un-certain-regard",
                    "name": "Devdiscourse",
                },
                {
                    "url": "https://homegrown.co.in/article/elephants-in-the-fog-nepali-film-cannes-un-certain-regard",
                    "name": "Homegrown",
                },
                {
                    "url": "https://en.wikipedia.org/wiki/Elephants_in_the_Fog",
                    "name": "Wikipedia",
                },
            ],
            "person_name": "Abinash Bikram Shah",
            "image_search_query": "Cannes film festival Un Certain Regard award ceremony",
            "word_count": 770,
            "body": """On May 23, 2026, the 79th Cannes Film Festival announced its awards. The Palme d'Or went to a Brazilian film. The Grand Prix went to a Russian director. And the Un Certain Regard Jury Prize — the award given to the most distinctive and innovative film in one of Cannes's most respected sections — went to **Elephants in the Fog**, directed by **Abinash Bikram Shah**.

It is the first film from Nepal to win any award at Cannes. Ever.

## The film

Elephants in the Fog is set in Nepal's Terai plains, in the flat, humid lowlands that border India. It follows a **Kinnar community** — a group of transgender and intersex people who have lived in South Asia for centuries, often on the margins of the societies around them. The community's matriarch faces a moral crisis when a woman goes missing, and the search forces a reckoning between love, duty, and the fragile stability the community has built.

Shah, the director, is a debut filmmaker. His film premiered at Cannes on May 20 in the Un Certain Regard section — a category that has historically been a launchpad for filmmakers who go on to define global cinema. Previous Un Certain Regard winners and nominees include **Hirokazu Kore-eda**, **Warwick Thornton**, and **Nadine Labaki**.

"This film is about making the invisible visible," Shah said after the award. "The Kinnar community in Nepal has always existed, but cinema has rarely looked at them as complete human beings with desires, conflicts, and dignity."

The jury that selected the film was presided over by **Park Chan-wook**, the South Korean director of *Oldboy* and *Decision to Leave*. Jury members included **Demi Moore** and **Ruben Östlund**.

## What India was doing at Cannes

India's Cannes 2026 presence was substantial in volume. Aishwarya Rai Bachchan attended the closing ceremony with her daughter Aaradhya — a moment that generated the most social media engagement of any South Asian at the festival. Alia Bhatt walked the red carpet. Aditi Rao Hydari was photographed extensively. Huma Qureshi attended.

But India's most-discussed Cannes story was not about any film. It was about the **red carpet access economy** — the investigation by *The Hollywood Reporter India* that documented how Indian influencers and socialites were paying €5,750 to €7,250 (₹5.5 to ₹7 lakh) for red carpet walk packages, and how some of them were being scammed by organisers who vanished after taking payment.

No Indian film won an award at Cannes this year.

India did have a presence at the Marché du Film — the festival's business wing, where deals are made and films are sold. **Anupria Goenka** brought *Bombay Stories* to the market. But the Marché is a trade event, not a competition. The awards — the part that defines a country's artistic standing — belonged to others.

## The numbers

This is not a new pattern. India's relationship with Cannes prizes has always been intermittent:

- **2024**: Payal Kapadia won the Grand Prix for *All We Imagine as Light* — the first Indian film to win a major Cannes award in decades.
- **2023–2025**: No other Indian film won a competition prize.
- **1946–2024**: India has won exactly two competition prizes at Cannes over 78 years — Kapadia's Grand Prix and Shaji N. Karun's Caméra d'Or in 1988.

Nepal, by contrast, had never had a film in official Cannes competition at all until this year. Shah's debut went from zero to a Jury Prize in a single edition.

## The industry gap

The comparison is not entirely fair. India produces approximately **1,500 films per year** across all languages. Nepal produces fewer than 100. India's film industry generates over **$2.5 billion** in annual revenue. Nepal's entire entertainment sector is a rounding error by comparison.

But that is precisely what makes the contrast significant. India has the money, the talent pool, the production infrastructure, and the historical legacy to dominate every major film festival in the world. It does not. The films that India sends to festivals — when it sends them at all — are often independent productions made outside the mainstream studio system, with budgets that would not cover the marketing spend on a single Dharma Productions release.

The mainstream Indian industry, the one that produces ₹3,000 crore franchises and ₹1,300 crore epics, is not interested in Cannes. It is interested in box office records, OTT deals, and — this year — red carpet photo opportunities.

## What this means for the diaspora

For NRIs who follow both Bollywood and global cinema, the Nepal win produces a specific kind of discomfort. It is the same discomfort that arises when a Pakistani film gets nominated for an Oscar, or when a Bangladeshi novel wins a Booker. It is the feeling of watching a neighbour achieve something that India should, by every structural advantage, have achieved first.

The Kinnar community that Shah's film centres on exists across South Asia — including India, where the **hijra** community has been documented in art, literature, and religious texts for millennia. An Indian filmmaker could have made this film. Many Indian filmmakers have the skill and the vision to make films that would win at Cannes. The question is whether the industry that surrounds them values that ambition — or whether it values the red carpet photo.

In 2026, the answer was the photo. Nepal chose the film.""",
        }
    )

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: Dhurandhar Star Gold TV Premiere — May 30
# ─────────────────────────────────────────────────────────────────────
slug2 = "dhurandhar-star-gold-tv-premiere-may-30-ranveer-singh-3000-crore-streaming-era-20260527"
if not check_duplicate(slug2):
    art2_id = str(uuid.uuid4())
    articles.append(
        {
            "id": art2_id,
            "headline": "Dhurandhar Gets Its Star Gold TV Premiere on May 30. Everyone Has Already Seen It on Netflix. It Will Still Be the Biggest TV Event of the Week. Here Is Why.",
            "subheadline": "The first Dhurandhar film — the spy thriller that launched a ₹3,000 crore franchise, turned Ranveer Singh into India's definitive action star, and spent six weeks as the most-watched Indian film on Netflix globally — will have its world television premiere on Star Gold, Star Gold 2, and Colors Cineplex on Friday, May 30 at 7 PM. In an era where most NRIs watched it on a laptop three months ago, the TV premiere is still a cultural event in India. Because in India, a film does not truly become a classic until an entire family watches it on a Friday night with ad breaks.",
            "slug": slug2,
            "category": "Entertainment",
            "vertical": "entertainment",
            "urgency": "standard",
            "status": "published",
            "published_at": now_iso,
            "score_total": 76,
            "tags": [
                "Dhurandhar",
                "Ranveer Singh",
                "Star Gold",
                "TV premiere",
                "Aditya Dhar",
                "Akshaye Khanna",
                "Sanjay Dutt",
                "R. Madhavan",
                "Indian cinema",
                "NRI",
                "streaming",
                "JioHotstar",
                "Netflix",
            ],
            "diaspora_angle": "The Dhurandhar TV premiere will be the most-watched television event in India on May 30. And it will be almost entirely irrelevant to most NRIs — because they already watched it on Netflix or JioHotstar months ago. This is the specific texture of the NRI entertainment experience that no one talks about: the desynchronisation of cultural moments. When Dhurandhar first released theatrically in October 2025, NRIs watched it in cinemas across North America, the UK, and the Gulf in the same week. When it hit Netflix globally, they binged it on their own schedules. But the TV premiere — the moment when 200 million households across India tune in simultaneously, when WhatsApp family groups light up with 'Dhurandhar aa raha hai Star Gold pe,' when your father watches it for the fourth time and still texts you during the climax — that is the cultural event. NRIs miss this specific ritual. Streaming gave the diaspora access to the content. It did not give them access to the communal experience of watching something at the same time as the entire country. The Star Gold premiere is not about access. It is about belonging to a moment. And for NRIs who grew up with 'Sholay' premieres on Doordarshan and 'DDLJ' Saturday night screenings on Star Movies, the loss of that shared viewing experience is one of the small, unnamed costs of emigration.",
            "sources": [
                {
                    "url": "https://www.bollywoodhungama.com/news/dhurandhar-world-television-premiere-may-30-star-gold",
                    "name": "Bollywood Hungama",
                },
                {
                    "url": "https://blazetrends.com/dhurandhar-television-premiere-star-gold-may-30",
                    "name": "Blaze Trends",
                },
                {
                    "url": "https://www.thedailyjagran.com/entertainment/dhurandhar-star-gold-premiere-ranveer-singh",
                    "name": "The Daily Jagran",
                },
            ],
            "person_name": "Ranveer Singh",
            "image_search_query": "Ranveer Singh Dhurandhar spy film",
            "word_count": 740,
            "body": """On Friday, May 30, at 7 PM IST, **Star Gold** will broadcast the world television premiere of **Dhurandhar** — the Aditya Dhar-directed spy thriller that has, over the past eight months, become the most commercially successful Indian franchise in history. Star Gold 2 and Colors Cineplex will simulcast.

This is not news in the traditional sense. Dhurandhar has been available on Netflix globally since January. It has been on JioHotstar in India since March. Its sequel, **Dhurandhar 2: The Revenge**, has already earned ₹1,800 crore worldwide. The combined franchise stands at over **₹3,100 crore** — the first Indian film series to cross ₹3,000 crore.

Everyone who wanted to see Dhurandhar has seen it. Many have seen it multiple times. And yet the Star Gold premiere will still be, by every measurable metric, the most-watched television event in India this week.

## The ritual

To understand why, you have to understand what a TV premiere means in India — which is something fundamentally different from what it means anywhere else.

In India, approximately **200 million households** have a television. Of those, roughly 100 million have access to OTT platforms. The remaining 100 million — and this is a number larger than the total number of households in Germany, France, and the UK combined — experience films primarily through television.

For these households, a Star Gold premiere is not a rerun. It is the first time they will see the film.

But even for the households that have Netflix or JioHotstar, the TV premiere serves a different function. It is the moment when a film stops being content and becomes a cultural reference point. It is when your mother watches it. It is when your neighbour's driver watches it. It is when the tea stall outside your office has it playing in the background.

**Sholay** became Sholay not because of its 1975 theatrical run, but because of its Doordarshan premiere. **Dilwale Dulhania Le Jayenge** became DDLJ not because of its 1995 release, but because of its Star Movies airings every Saturday. **Baahubali** entered the national vocabulary not through its ₹600 crore box office, but through its repeated Star Maa and Star Gold broadcasts.

The TV premiere is the second birth of an Indian film.

## The franchise context

Dhurandhar's TV premiere arrives at a specific moment for the franchise. Ranveer Singh, who plays deep-cover R&AW agent **Jaskirat Singh Rangi**, is currently the subject of a **FWICE non-cooperation directive** — effectively a temporary industry ban — over his exit from Farhan Akhtar's Don 3. Excel Entertainment claims ₹45 crore in pre-production losses. Ranveer's team has responded with silence.

The timing creates an unusual juxtaposition: the biggest star in India, promoting the biggest franchise in India, banned by the industry body of India, all in the same week. Star Gold's premiere timing was almost certainly locked months ago, before the FWICE dispute. But the coincidence means that 200 million households will watch Ranveer Singh being India's hero on Friday night, while the industry he works in debates whether he should be allowed to work.

For what it is worth, the FWICE directive is widely expected to be resolved through negotiation. These things usually are. But the optics of the country's most-watched actor on the country's most-watched channel during the country's most-talked-about industry dispute are, at minimum, cinematic.

## The JioStar strategy

The simulcast across Star Gold, Star Gold 2, and Colors Cineplex is not accidental. It reflects JioStar's strategy of using the Dhurandhar franchise as a tent-pole event across its entire television network. The timing — a Friday evening slot — is designed to maximise family viewership. The multi-channel approach ensures that the premiere reaches both Hindi-speaking and multilingual audiences.

This is also a play for advertising revenue. A Dhurandhar premiere is expected to command some of the highest ad rates of the year outside of cricket and elections. Consumer brands will have bought slots months in advance. The premiere is not just a broadcast event — it is a marketplace.

## What NRIs will feel

For NRIs, the Star Gold premiere will surface as a WhatsApp notification from a relative. "Dhurandhar on Star Gold tonight!" — sent with the energy of a cricket match announcement. And the NRI will reply, "Already seen it three times," and move on.

But something will be lost in that exchange. The NRI has the content. They do not have the event. They watched Dhurandhar on a 13-inch laptop screen in a studio apartment in Jersey City at 11 PM on a Tuesday. Their father watched it on a 55-inch TV in the living room in Pune at 7 PM on a Friday, with the family, with chai, with the neighbours dropping in because they heard the volume through the wall.

The content is the same. The experience is not.

This is the small, unnamed cost of the streaming era for the diaspora: you get everything first, but you watch it alone. The Star Gold premiere is not about access. It is about an entire country pressing play at the same time. And that is something that no OTT platform has figured out how to replicate.""",
        }
    )

# --- Publish articles ---
for art in articles:
    print(f"\n→ Publishing: {art['headline'][:80]}...")
    payload = {
        k: v
        for k, v in art.items()
        if k not in ["person_name", "image_search_query"]
    }
    res = sb_post("p2_articles", payload)
    art_id = res[0]["id"]
    # Image sourcing — Wikipedia first for person articles
    img_url = None
    attribution = "The Videshi"
    if "person_name" in art:
        img_url = fetch_wikipedia_person_image(art["person_name"])
        if img_url:
            attribution = "Wikimedia Commons"
    if not img_url:
        img_url = fetch_pexels_image(
            art.get("image_search_query", "Indian cinema"),
            art.get("image_search_query"),
        )
    if img_url:
        filename = f"{art['slug']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        sb_patch(
            "p2_articles",
            f"id=eq.{art_id}",
            {"image_url": final_url, "image_attribution": attribution},
        )
        print(f"  ✓ Image set ({attribution})")
    else:
        print(f"  ⚠ No image found, leaving blank")

print("\n✅ Entertainment writer batch done")
