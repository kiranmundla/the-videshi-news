#!/usr/bin/env python3
"""Entertainment writer — May 26 2026, 22:30 PDT batch:
1. Cannes 2026 Red Carpet Scam Economy — Indians paying ₹5-7 lakh for carpet access,
   scam organizers vanishing after taking money, "India at Cannes" as manufactured narrative.
   Hollywood Reporter India exposé. Diaspora representation vs. purchased prestige.
2. Netflix's Desi Bling — ultra-wealthy Indian expats in Dubai, Karan Kundrra proposes
   to Tejasswi Prakash on-camera, the guilty pleasure NRI cringe debate, premiered May 20.
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
# ARTICLE 1: Cannes 2026 Red Carpet Scam Economy
# ─────────────────────────────────────────────────────────────────────
slug1 = "cannes-2026-red-carpet-scams-indians-paying-lakhs-fake-access-manufactured-glamour-20260527"
if not check_duplicate(slug1):
    art1_id = str(uuid.uuid4())
    articles.append(
        {
            "id": art1_id,
            "headline": "Indians Are Paying ₹7 Lakh to Walk the Cannes Red Carpet. Some of Them Are Getting Scammed Before They Even Land. The 'India at Cannes' Narrative Has Become a Marketplace.",
            "subheadline": "The Hollywood Reporter India investigated the booming black market for Cannes red carpet access — packages starting at €5,750, ticket scalpers from India running rampant, organisers vanishing after taking money, and people flying to the French Riviera only to find themselves stranded. The real story is not about who walked the carpet. It is about who paid to walk it and why the Indian diaspora should care about what 'representing India' has come to mean.",
            "slug": slug1,
            "category": "Entertainment",
            "vertical": "entertainment",
            "urgency": "standard",
            "status": "published",
            "published_at": now_iso,
            "score_total": 82,
            "tags": [
                "Cannes 2026",
                "79th Cannes Film Festival",
                "red carpet",
                "India at Cannes",
                "scam",
                "influencer culture",
                "NRI",
                "Bollywood",
                "Pankhuri Harikrishnan",
                "Brut India",
                "representation",
            ],
            "diaspora_angle": "For the Indian diaspora, Cannes has always been a proxy for a larger question: does the world take us seriously? When Aishwarya Rai first walked the red carpet in 2002, it mattered because NRIs saw one of their own on a stage that had been inaccessible. When Nandita Das screened a film there, it mattered because it was about the work. But 'India at Cannes' in 2026 has become something else entirely — a marketplace where anyone with ₹5-7 lakh and a willingness to fly to Nice can claim they 'represented India at an international platform.' The scam economy that has grown around this is not a Bollywood problem or an influencer problem. It is a diaspora problem. NRIs who share these photos in family WhatsApp groups, who point to the 'India at Cannes' hashtag as evidence that the motherland is finally being seen — they are consuming a narrative that is, in many cases, literally purchased. The distinction between someone invited by the festival for their work and someone who paid a scalper ₹7 lakh for a 90-second carpet walk at 11 AM when no cameras are rolling is a distinction that matters, and it is being deliberately blurred. For a diaspora that has spent decades earning credibility in foreign countries, the spectacle of Indians buying their way onto a red carpet and then being stranded in the south of France by scam artists is not just embarrassing. It is a microcosm of the tension between the India the diaspora wants to project and the India that shows up when money is the only qualification.",
            "sources": [
                {
                    "url": "https://www.hollywoodreporterindia.com/features/interviews/india-at-cannes-2026-the-rise-of-red-carpet-scams-ticket-scalping-and-self-funded-narratives",
                    "name": "The Hollywood Reporter India",
                },
                {
                    "url": "https://www.hollywoodreporterindia.com/features/interviews/cannes-2026-what-it-really-takes-to-pull-off-a-red-carpet-appearance",
                    "name": "The Hollywood Reporter India",
                },
                {
                    "url": "https://afaqs.com/news/media/how-brut-made-cannes-work-for-brands-and-influencers",
                    "name": "afaqs!",
                },
                {
                    "url": "https://www.whosthat360.com/cannes-film-festival-business-influencers",
                    "name": "WhosThat360",
                },
            ],
            "image_search_query": "Cannes film festival red carpet crowd",
            "word_count": 780,
            "body": """The 79th Cannes Film Festival ended last week. The films that screened, the awards that were given, the deals that were struck in the Marché du Film — these are footnotes in the Indian media coverage. What dominated instead was the same thing that has dominated every year since the pandemic: photographs. Hundreds of them. Indians on the red carpet, in gowns that cost more than apartments in tier-two cities, with captions that said some version of "representing India on the global stage."

What those captions did not say: most of them paid to be there.

## The price of the carpet

According to a report by *The Hollywood Reporter India*, the going rate for a red carpet appearance at Cannes 2026 starts at approximately **€5,750 (₹5.5 lakh)** for balcony seating at a screening, which includes carpet access. For premium positions — orchestra seating, corbeille access, the kind of placement where Getty photographers might actually point a camera at you — the number climbs to **€7,250 (around ₹7 lakh)**.

These are not official festival packages. These are tickets sold through a network of intermediaries, event managers, and outright scalpers who have identified a market that is, almost exclusively, Indian.

**Pankhuri Harikrishnan**, founder of Fetch India and a Cannes attendee since 2018, told *The Hollywood Reporter India* that the situation in 2026 "spiralled out of control." She was contacted by multiple people who had flown to Cannes on the promise of walking the red carpet — flights booked, hotels paid for, outfits arranged — only to discover that their organisers had vanished.

"I've been called by various individuals who had been promised carpet appearances, but after they have landed in Cannes… the organisers vanished," Harikrishnan said.

Some of them did not even understand the basic mechanics of the festival. The red carpet is active only during evening premieres and screenings. Outside those hours, it is just a strip of fabric in front of a building. Multiple Indians were told they could walk the carpet at 11 AM — a time when it is functionally a corridor.

## The package

What is being sold is not merely access. It is a narrative.

According to Harikrishnan, the packages often include hair and makeup at the hotel, a limousine from the hotel to the Palais des Festivals, and a set of photographs — sometimes with the option of a Getty photographer for an additional fee. A 2025 *Screen Daily* investigation documented Tier 1 Premiere packages costing **$10,795 per person**, including all of the above plus guaranteed positioning at a major screening.

The buyer walks the carpet, gets photographed, posts the photos on Instagram with the right hashtags — #IndiaAtCannes, #CannesFilmFestival, #RepresentingIndia — and returns home with content that is, to the average viewer, indistinguishable from a legitimate invitation.

"Not only are you getting access because you can buy it, you're also getting media because you can buy that too," Harikrishnan said. "Together, you're creating a narrative that's completely self-funded."

## The industry that enables it

The scams are the extreme end. But the broader infrastructure is not illegal — it is simply commercial.

**Brut India**, the digital media company, has become a significant Cannes content machine, bringing influencers and creators to the festival as part of brand partnerships. In 2026, Samsung's Galaxy S26 Ultra was the principal partner, with all Brut Cannes content shot on the device. The operation is transparent — Brut is not hiding that its Cannes presence is commercially funded. But it has normalised the idea that Cannes attendance is something that can be purchased as part of a marketing budget, which in turn has normalised the idea for individuals.

The result is a festival where the red carpet has become, in Harikrishnan's words, "a joke."

"Earlier, even if you walked the carpet, how would anyone know unless someone covered you? You got covered in newspapers or magazines if you were of a certain repute," she said. "But today, with bots, social media and multiple platforms where you can pay to promote yourself, the landscape has changed. Anybody who has the ability to buy and amplify can go."

## What the diaspora sees

Here is the part that matters for NRIs: the people buying these packages are, overwhelmingly, not interested in cinema. Harikrishnan noted that almost none of the buyers she encountered wanted tickets to actual film screenings. They wanted the carpet walk. The photograph. The content.

This means the "India at Cannes" narrative — which NRI WhatsApp groups share with pride, which Indian media covers as evidence of the country's growing cultural influence — is, in many cases, a purchased product. The carpet walk that your uncle forwarded to the family group was not the result of artistic recognition. It was the result of a €5,750 transaction.

This is not to say that legitimate Indian presence at Cannes does not exist. It does. **Payal Kapadia** won the Grand Prix in 2024 for *All We Imagine as Light*. **Anupria Goenka** brought *Bombay Stories* to the Marché du Film this year, wearing a Sejal Kamdar design that used ajrakh embroidery and vintage rupee coins in jewellery inspired by Manto's *Hatak*. Manish Malhotra showcased Assamese textiles. These are people who were there for the work.

But they are increasingly outnumbered by people who were there for the photo. And the line between the two is being deliberately obscured by an industry that profits from the confusion.

## The scam within the scam

The deepest irony is structural. The people flying to Cannes and paying ₹7 lakh for a carpet walk are being scammed twice. Once by the organisers who take their money and disappear. And once by a culture — both in India and in the diaspora — that has convinced them the photograph is worth ₹7 lakh in the first place.

"We're looking ridiculous with these fancy dresses that are going up on the carpet," Harikrishnan wrote on Instagram. "We are just giving India a terrible, terrible name at an international platform."

She is not wrong. But the demand exists because the reward exists. In an attention economy where a Cannes photo generates social proof that translates directly into brand deals, followers, and status — especially in India, where proximity to global glamour still carries outsized social capital — ₹7 lakh is not a scam. It is an investment. And until the audience stops rewarding the investment, the marketplace will keep growing.""",
        }
    )

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: Netflix's Desi Bling — NRI Dubai wealth on display
# ─────────────────────────────────────────────────────────────────────
slug2 = "netflix-desi-bling-dubai-indian-expats-karan-kundrra-tejasswi-prakash-engagement-nri-wealth-20260527"
if not check_duplicate(slug2):
    art2_id = str(uuid.uuid4())
    articles.append(
        {
            "id": art2_id,
            "headline": "Netflix Made a Show About Ultra-Rich Indians in Dubai. Karan Kundrra Proposed to Tejasswi Prakash on Camera. The Internet Cannot Decide if Desi Bling Is a Mirror or a Joke.",
            "subheadline": "Desi Bling premiered on Netflix on May 20 and immediately became the most-discussed Indian reality show since Fabulous Lives. It follows billionaire Indian families in Dubai — the Sajans, the Sanpals — alongside TV celebrities Karan Kundrra and Tejasswi Prakash, whose on-camera engagement went viral within hours. Critics called it cringe. The audience called it addictive. The NRI internet called it the most accurate portrayal of diaspora wealth dynamics they have ever seen on a streaming platform.",
            "slug": slug2,
            "category": "Entertainment",
            "vertical": "entertainment",
            "urgency": "standard",
            "status": "published",
            "published_at": now_iso,
            "score_total": 78,
            "tags": [
                "Desi Bling",
                "Netflix",
                "Karan Kundrra",
                "Tejasswi Prakash",
                "TejRan",
                "Dubai",
                "NRI",
                "reality TV",
                "Indian expats",
                "Rizwan Sajan",
                "Danube Group",
                "streaming",
            ],
            "diaspora_angle": "Desi Bling is the first mainstream show that puts NRI wealth — specifically Gulf NRI wealth — on screen without either romanticising it or condemning it. For the Indian diaspora, Dubai occupies a unique position: it is where middle-class Indians go to become rich, where rich Indians go to become richer, and where the entire Indian class system is compressed into a 45-minute drive between Deira and Palm Jumeirah. Every NRI has a Dubai uncle. Every NRI has attended a Dubai wedding that cost more than their first apartment. Every NRI has scrolled through a Dubai Indian's Instagram and felt that specific cocktail of admiration, envy, and discomfort that the show captures with precision. The engagement between Karan Kundrra and Tejasswi Prakash — a televised proposal in a Dubai penthouse — is being consumed simultaneously as romance, as content strategy, and as a case study in how Indian celebrity functions in the diaspora economy. For NRIs who have watched their own community events in London, Toronto, and the Bay Area become increasingly performative — where the guest list is curated for Instagram and the charity fundraiser exists primarily for the photos — Desi Bling is not cringe. It is a documentary.",
            "sources": [
                {
                    "url": "https://www.livemint.com/entertainment/whole-vibe-to-second-hand-embarrassment-internet-reviews-netflix-desi-bling",
                    "name": "Mint",
                },
                {
                    "url": "https://www.bollywoodhungama.com/news/karan-kundrra-proposes-to-tejasswi-prakash-on-netflix-desi-bling",
                    "name": "Bollywood Hungama",
                },
                {
                    "url": "https://www.pinkvilla.com/entertainment/karan-kundrra-admits-to-parenting-fiancee-tejasswi-prakash-on-desi-bling",
                    "name": "Pinkvilla",
                },
                {
                    "url": "https://www.koimoi.com/desi-bling-review-watch-it-if-youre-interested-to-see-tejasswi-prakash",
                    "name": "Koimoi",
                },
                {
                    "url": "https://dubai.news/desi-bling-netflix-full-series-cast-episodes-dubai-premise",
                    "name": "Dubai News",
                },
            ],
            "person_name": "Tejasswi Prakash",
            "image_search_query": "Tejasswi Prakash actress",
            "word_count": 760,
            "body": """On May 20, Netflix released **Desi Bling** — seven episodes, roughly 40 minutes each, filmed in Dubai, featuring a cast that includes billionaire business families, their extended social circles, and one of Indian television's most-followed couples. Within 48 hours, it had generated more social media conversation than any Indian reality show since *Fabulous Lives of Bollywood Wives*.

The premise is simple: ultra-wealthy Indian expats in Dubai, living lives that most people only encounter through Instagram reels, are now doing it on camera for a global streaming platform. The execution is exactly as messy, aspirational, and uncomfortable as that sounds.

## The cast

The show's anchor families are the **Sajans** and the **Sanpals** — two of Dubai's most prominent Indian business dynasties. **Rizwan Sajan**, founder of the **Danube Group**, is among the wealthiest Indian businessmen in the UAE. His son **Adel Sajan** and daughter-in-law **Sana Sajan** appear alongside him. **Satish Sanpal** and his wife **Tabinda Sanpal** represent another layer of the Dubai Indian elite.

Then there are the wildcards: **Pamela Serena**, **Dyuti Parruck**, **Alizey Mirza**, and others who orbit the social scene — exactly the kind of figures who make reality television combustible.

And then there is the main event: **Karan Kundrra** and **Tejasswi Prakash**.

## The proposal

Karan Kundrra and Tejasswi Prakash — known to their fanbase as **TejRan** — have been one of Indian television's most-tracked couples since they met on *Bigg Boss 15* in 2021. For four years, the internet has been waiting for an engagement announcement with the intensity usually reserved for cricket match results.

It happened on Desi Bling. In the final episode, Karan proposed to Tejasswi in what the show presented as a surprise — candles, a ring, tears, the whole production. The clip went viral immediately. #TejRan trended on X for two days. Instagram reels of the moment have been viewed tens of millions of times.

The authenticity debate started approximately 14 minutes later. **Rajiv Adatia**, a friend of the couple and former *Bigg Boss* contestant, confirmed the engagement was real. Rakhi Sawant weighed in. Multiple former reality TV participants offered commentary. The internet split into its usual factions: people who were genuinely moved, people who called it scripted, and people who pointed out that Karan had told cameras during the show that he was "literally parenting" Tejasswi — a comment his own parents questioned on screen.

## The "parenting" comment

The most-discussed moment on the show is not the proposal. It is Karan Kundrra saying, on camera, that he is **"parenting"** Tejasswi Prakash and that he "needs her to grow up."

The comment produced the kind of internet firestorm that Indian relationship discourse specialises in. On one side: people who saw it as a red flag, evidence of a controlling dynamic being normalised in front of millions of viewers. On the other: people who saw it as an honest admission of an imperfect relationship, the kind of thing that couples say privately but rarely on camera.

Karan's parents, who appeared on the show, reportedly questioned whether the relationship's dynamics were balanced. This added a layer that Indian audiences found particularly resonant — the in-law scrutiny of a son's relationship, played out not in a living room in Delhi but in a penthouse in Dubai, on a platform owned by Netflix.

## What the critics say

Reviews have been mixed in the specific way that Indian reality TV reviews are always mixed. **Koimoi** gave it a lukewarm assessment, noting that Tejasswi says "shut up" approximately 8,000 times per episode and that many scenes felt scripted. **Mint** reported that the internet was split between viewers calling it a "whole vibe" and others experiencing "second-hand embarrassment." **MensXP** declared it the "perfect guilty pleasure after Bollywood Wives."

The show's director, **Charbel Youssef**, brings the same reality-TV grammar that powered *Dubai Bling* — the Netflix show about Dubai's international social scene that Desi Bling is explicitly modelled on. The difference is specificity. Dubai Bling featured a diverse cast. Desi Bling is exclusively about the Indian community — its internal hierarchies, its obsession with status markers, its particular brand of wealth display.

## What it actually captures

Here is what Desi Bling gets right, whether it intended to or not: it captures the specific texture of Indian wealth in the Gulf.

Dubai is not London or New York for the Indian diaspora. It is closer — geographically, culturally, and in terms of accessibility. The Gulf has been an Indian economic corridor for decades. The families on this show did not arrive in Dubai with H-1B visas and engineering degrees. They arrived with business plans, construction contracts, and trading networks that predate the UAE's modern economy.

The result is a diaspora community that is both supremely integrated — these families are part of Dubai's economic fabric — and completely insular. The parties on Desi Bling feature only Indian guests. The drama is Indian drama. The social hierarchies map directly onto Indian social hierarchies, just with larger numbers.

For NRIs in the West, this is simultaneously alien and recognisable. The scale is Dubai. The dynamics are every Indian community event you have ever attended — the uncle who mentions his net worth within 90 seconds of meeting you, the aunt who is keeping score of who wore what, the couple whose relationship everyone has an opinion about.

The question is whether Netflix intended Desi Bling as a mirror or a spectacle. The answer, based on seven episodes, is both. And the Indian internet — which is nothing if not self-aware about its own excesses — is treating it accordingly: binge-watching it, criticising it, and recognising itself in it, all at the same time.""",
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
        img_url = fetch_pexels_image(art.get("image_search_query", "Cannes film festival"), art.get("image_search_query"))
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
