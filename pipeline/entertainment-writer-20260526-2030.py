#!/usr/bin/env python3
"""Entertainment writer — May 26 2026, 20:30 PDT batch:
1. Kangana Ranaut defends Aishwarya Rai at Cannes 2026 amid age-shaming trolls — L'Oreal replaced her with Alia Bhatt after 24 years, Aishwarya still showed up, Kangana posted Instagram Story calling out body-shamers.
2. Sonam Kapoor & Anand Ahuja's London property purchases spark neighbourhood revolt — 5 flats near ₹270 crore Notting Hill mansion, British residents allege "servant quarters", NRI wealth class dynamics.
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
# ARTICLE 1: Kangana Ranaut defends Aishwarya Rai at Cannes 2026
# ─────────────────────────────────────────────────────────────────────
slug1 = "kangana-ranaut-defends-aishwarya-rai-cannes-2026-loreal-alia-bhatt-age-shaming-20260526"
if not check_duplicate(slug1):
    art1_id = str(uuid.uuid4())
    articles.append(
        {
            "id": art1_id,
            "headline": "L'Oréal Replaced Aishwarya Rai With Alia Bhatt After 24 Years. Aishwarya Showed Up Anyway. Then Kangana Ranaut — Kangana Ranaut — Defended Her Against the Trolls.",
            "subheadline": "L'Oréal Paris quietly dropped Aishwarya from their Cannes 2026 campaign and put Alia Bhatt front and center. Aishwarya flew to the south of France anyway, walked the red carpet in a custom Amit Aggarwal gown called 'Luminara' that took 1,500 hours to make, brought Aaradhya, posed with Eva Longoria, and blew kisses to the cameras like she has been doing since 2002. When trolls body-shamed her and compared her to younger stars, Kangana Ranaut of all people posted an Instagram Story telling them to get used to seeing older women on red carpets.",
            "slug": slug1,
            "category": "Entertainment",
            "vertical": "entertainment",
            "urgency": "standard",
            "status": "published",
            "published_at": now_iso,
            "score_total": 85,
            "tags": [
                "Aishwarya Rai Bachchan",
                "Kangana Ranaut",
                "Cannes 2026",
                "L'Oréal Paris",
                "Alia Bhatt",
                "Amit Aggarwal",
                "79th Cannes Film Festival",
                "age-shaming",
                "body-shaming",
                "NRI",
                "Bollywood",
            ],
            "diaspora_angle": "Aishwarya Rai is not merely a Bollywood actress for the Indian diaspora — she is the first face that represented India on a global red carpet when most NRIs were still explaining to colleagues what Bollywood was. She won Miss World in 1994, when the diaspora was smaller, less confident, and desperate for any sign that the West saw India as something other than poverty and call centers. When she started walking at Cannes in 2002, she was not just representing L'Oréal — she was representing every NRI who had ever been made to feel invisible at a formal event. Twenty-four years later, when L'Oréal replaces her with someone younger and she walks the carpet anyway, the reaction in NRI WhatsApp groups is not about fashion. It is about the specific pain of watching someone who looked like you in spaces where no one looked like you, and seeing her discarded. Kangana defending her is its own plot twist — in a diaspora that tracks Bollywood feuds like fantasy football, these two were never allies. The fact that Kangana's defense was specifically about ageism — 'get used to seeing older women on red carpets' — resonates with NRI women who navigate the same scrutiny in their own communities, where aunties at Diwali parties still comment on weight and age with the subtlety of a cricket commentator.",
            "sources": [
                {
                    "url": "https://www.bollywoodshaadis.com/articles/kangana-ranaut-slams-trolls-targeting-aishwarya-rai-cannes-look-79587",
                    "name": "BollywoodShaadis",
                },
                {
                    "url": "https://www.thedailyjagran.com/entertainment/news/she-is-not-here-to-please-you-kangana-ranaut-defends-aishwarya-rai-amid-cannes-2026-criticism-10313521",
                    "name": "The Daily Jagran",
                },
                {
                    "url": "https://www.bollywoodhungama.com/news/aishwarya-rai-bachchan-cannes-2026-regal-sapphire/",
                    "name": "Bollywood Hungama",
                },
                {
                    "url": "https://www.pinkvilla.com/entertainment/cannes-2026-aishwarya-rai-bachchan-reigns-over-the-red-carpet-fans-call-her-undisputed-queen.html",
                    "name": "Pinkvilla",
                },
                {
                    "url": "https://www.hollywoodreporterindia.com/entertainment/aishwarya-rai-cannes-2026-kangana-ranaut-support/",
                    "name": "Hollywood Reporter India",
                },
            ],
            "person_name": "Aishwarya Rai",
            "image_search_query": "Aishwarya Rai Bachchan actress",
            "word_count": 780,
            "body": """Before the gown, before the trolls, before Kangana Ranaut became the most unlikely ally in Bollywood, there was the quiet fact that L'Oréal Paris — the brand that had put Aishwarya Rai Bachchan on the Cannes red carpet every year since 2002 — had moved on.

The posters for Cannes 2026 did not feature Aishwarya. The campaign materials centered **Alia Bhatt** as the face of L'Oréal at the festival. After 24 years — a partnership that had become as synonymous with Cannes as the Palme d'Or itself — the brand had, without announcement or explanation, replaced its longest-serving Indian ambassador.

Rumours swirled for weeks that Aishwarya would not attend this year.

She attended.

## The Luminara gown

On May 22, 2026, Aishwarya Rai Bachchan walked the red carpet at the **79th Cannes Film Festival** in a custom couture gown by Indian designer **Amit Aggarwal**.

The gown was called **Luminara** — named for its concept of light in motion. It took over **1,500 hours** of handcrafted Crystal Vein embroidery to complete: thousands of crystal decorations arranged in vein-like patterns across a sculptural mermaid silhouette in deep royal sapphire blue. Aggarwal described it as "less like a garment and more like an energy field around her."

Aishwarya styled the gown with minimal jewellery, open hair, and the specific posture of a woman who has walked this carpet twenty-four times and is not about to let the twenty-fourth feel like a farewell.

She blew kisses to the cameras. She made heart signs. She greeted the crowd with a namaste. She spent time with her longtime friend **Eva Longoria**. She brought her daughter **Aaradhya Bachchan**, who wore a red silk outfit with a matching drape.

Over the following days, Aishwarya wore a powder pink **Sophie Couture** gown, a white feathered pantsuit by **Cheney Chan** with bejewelled lapels, and a custom **Fjolla Nil** couture piece for interviews. Each appearance generated the kind of attention that suggested the brand switch had not diminished her draw — if anything, it had amplified it.

## The trolls

Predictably, the internet was not kind.

Within hours of her red carpet photos going live, social media was flooded with comments about her body, her weight, and her age. One widely shared tweet compared her unfavourably to actresses who maintain "yoga bodies" and asked why she could not look like Shilpa Shetty. Others were cruder. The general tone was one that Indian women — in India and in the diaspora — know intimately: the expectation that a woman who was once declared the most beautiful in the world owes the public a perpetual performance of that beauty, on the public's terms, at the public's preferred weight.

Aishwarya, characteristically, said nothing.

## Kangana enters

What happened next genuinely surprised people.

On **May 24**, **Kangana Ranaut** — Member of Parliament, former actress, and perhaps the last person anyone expected to publicly defend Aishwarya Rai — posted a photo of Aishwarya's Cannes look on her Instagram Story with a message that was blunt even by her standards:

*"Fashion and style is a self expression, it is one's own interpretation of life and their attitude, no woman owes anything to anyone, Ash looks great!! Those of you who want to see her any other way, why don't you show what you got?? She is not here to please you, she is glorious, if you are not used to seeing older women on red carpets, get used to them now. Thanks."*

The message was notable for several reasons. Kangana and Aishwarya have never been close. They have operated in entirely different orbits of Bollywood for over a decade, with Kangana's public persona built partly on a willingness to criticise the industry establishment that Aishwarya is part of. The two have no history of public support, no joint appearances, no collaborative projects.

And yet here was Kangana, unequivocally defending not just Aishwarya but the principle that older women have a right to occupy glamorous spaces without apology.

## What it actually means

The Cannes ageism conversation is not new globally. Hollywood has been having it since at least Meryl Streep's 2015 comments about being offered witch roles after turning 40. But in India and the Indian diaspora, the conversation carries a different weight because the beauty standards are enforced not just by an industry but by a culture — by aunties, by WhatsApp groups, by matrimonial listings that still specify "fair, slim" as qualifications for marriage.

Aishwarya Rai Bachchan is 52 years old. She has been in the public eye since she was 21. She has been compared to every generation of actress that followed her. She was the gold standard, and now she is being told — by anonymous accounts on X, by YouTube thumbnails, by the implicit messaging of a brand that quietly replaced her — that the gold standard has an expiry date.

Kangana's post, for all its Instagram-Story brevity, said the quiet part out loud: the scrutiny Aishwarya faces is not about fashion. It is about a culture that does not know what to do with women who refuse to age on schedule.

## The L'Oréal footnote

L'Oréal has not publicly commented on the ambassador transition. Neither has Alia Bhatt addressed it directly. But the optics were unmistakable: Alia arrived at Cannes with full brand infrastructure — custom couture, official events, the works. Aishwarya arrived on her own terms, in a gown made by an Indian designer she chose herself, with her daughter by her side.

Both walked the same carpet. The internet watched both. And for the second time in 24 years, Aishwarya Rai Bachchan at Cannes was the story everyone talked about — not because of the brand on her dress, but because of who she is and the fact that she showed up.""",
        }
    )

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: Sonam Kapoor & Anand Ahuja London property controversy
# ─────────────────────────────────────────────────────────────────────
slug2 = "sonam-kapoor-anand-ahuja-london-notting-hill-five-flats-neighbours-revolt-servant-quarters-20260526"
if not check_duplicate(slug2):
    art2_id = str(uuid.uuid4())
    articles.append(
        {
            "id": art2_id,
            "headline": "Sonam Kapoor and Anand Ahuja Bought Five Flats Next to Their £21 Million Notting Hill Mansion. The British Neighbours Are Calling Them 'Servant Quarters.' This Is the NRI Property Story Nobody Wanted to Have Out Loud.",
            "subheadline": "The couple already own a mansion in one of London's most exclusive streets that took three years and a planning dispute to renovate. Now a company linked to them has purchased five apartments in the adjacent Hill Crest development. Residents have told British media the flats will be used to house staff. Some have used the word 'deport.' The story touches every raw nerve the Indian diaspora has about wealth, acceptance, and the limits of belonging in Britain.",
            "slug": slug2,
            "category": "Entertainment",
            "vertical": "entertainment",
            "urgency": "standard",
            "status": "published",
            "published_at": now_iso,
            "score_total": 80,
            "tags": [
                "Sonam Kapoor",
                "Anand Ahuja",
                "London",
                "Notting Hill",
                "NRI property",
                "UK",
                "real estate",
                "diaspora",
                "Bollywood",
                "Hill Crest",
            ],
            "diaspora_angle": "This story is not really about Sonam Kapoor. It is about the specific anxiety that every affluent NRI in London, New York, or the Bay Area has lived with quietly: the feeling that no matter how much money you make, no matter how many properties you buy, there is a line you are expected not to cross, and you will not be told where that line is until you cross it. When British neighbours describe the flats as 'servant quarters,' they are reaching for a colonial vocabulary that NRIs recognise instantly. When someone on social media says 'deport them,' the subtext is not about planning permission. It is about who gets to be wealthy in certain postcodes. The Kapoor-Ahuja situation is a compressed version of a story playing out across NRI enclaves — in Mayfair, in the Hamptons, in Atherton — where Indian money is welcome at the bank but not always at the neighbourhood meeting. For the diaspora, this story will land as confirmation of something they have always suspected: integration has a ceiling, and real estate is where you find it.",
            "sources": [
                {
                    "url": "https://www.bollywoodhungama.com/news/sonam-kapoor-anand-ahuja-london-property-purchase-neighbourhood-controversy/",
                    "name": "Bollywood Hungama",
                },
                {
                    "url": "https://www.mensxp.com/entertainment/bollywood/sonam-kapoor-anand-ahuja-notting-hill-five-flats-dispute-locals.html",
                    "name": "MensXP",
                },
                {
                    "url": "https://www.womansera.com/sonam-kapoor-anand-ahuja-london-mansion-controversy/",
                    "name": "Woman's Era",
                },
                {
                    "url": "https://www.saindiamagazine.com/bollywood/sonam-kapoor-anand-ahuja-london-property-controversy/",
                    "name": "SA India Magazine",
                },
            ],
            "person_name": "Sonam Kapoor",
            "image_search_query": "Sonam Kapoor actress Bollywood",
            "word_count": 750,
            "body": """The property at the centre of this story is a mansion on one of Notting Hill's most exclusive streets. **Sonam Kapoor** and her husband, businessman **Anand Ahuja**, acquired it in 2023 for a reported **₹270 crore** (approximately £21 million). The renovation took three years and a planning dispute with the local council before approvals came through. The plans included underground facilities and the kind of specification that signals not a home but an estate.

That was the first act. The second act is smaller in scale but far more revealing about who gets to buy what in London.

## Five flats in Hill Crest

A company linked to the couple recently purchased **five apartments** and associated garages in **Hill Crest**, a 23-flat residential development adjacent to their Notting Hill mansion. The total acquisition is reported at approximately **₹51 crore**.

Hill Crest is not a luxury block in the way the mansion is luxury. It is a residential development with working families, long-term tenants, and the kind of close-knit community that British neighbourhoods — particularly in affluent West London — define themselves by. The residents there did not sign up to live next to a Bollywood star's domestic infrastructure.

And that is exactly what they believe is happening.

## 'Servant quarters'

Multiple residents have told British media that they believe the five flats will be converted into **staff accommodation** — housing for the domestic employees who will service the couple's renovated mansion. The word used, repeatedly, was "servant quarters."

The vocabulary is not accidental. In a post-colonial context, describing Indian-owned property as servant quarters carries a weight that the residents may or may not have intended but that the Indian diaspora will understand immediately. It is the language of the Raj inverted: instead of British households in India staffed by Indian servants, it is an Indian household in Britain being accused of importing a servitude model into a London postcode.

Some residents have gone further. On social media, responses to the story included the word **"deport"** — a word that, in 2026 Britain, carries enough anti-immigrant charge to make the story about more than just planning permission.

## The renovation backstory

The Kapoor-Ahuja London story has been building for years. When they first submitted renovation plans for the mansion, neighbours objected. The dispute lasted three years. Permission was eventually granted, but the relationship between the couple and the street was already strained.

The five-flat purchase appears to have been the tipping point. Residents told reporters they feel "pressured to remain silent" due to the couple's wealth and influence. Others described a sense that the character of their neighbourhood was being reshaped by a single family's expansion — not through one large purchase, which London's property market has mechanisms to absorb, but through a creeping accumulation of adjacent units that functionally extends the mansion's footprint into a community building.

Neither Sonam Kapoor nor Anand Ahuja has publicly addressed the controversy. Through intermediaries, the couple has reportedly said the flats were purchased as **investment properties**, not as staff housing.

## What the diaspora hears

For NRIs in Britain — and there are roughly **1.8 million** people of Indian origin in the UK — this story is not gossip. It is a case study in the limits of financial integration.

The Indian diaspora in Britain is, by most economic metrics, successful. Indian-origin Britons are overrepresented in medicine, law, technology, and finance. They own homes in the right postcodes. They send their children to the right schools. They have produced a former Prime Minister.

And yet the Sonam Kapoor story suggests that success has a ceiling — or at least a perimeter. You can buy a £21 million mansion. You can renovate it. You can live in Notting Hill. But when you start buying adjacent properties, when your presence becomes structurally visible rather than politely contained, the neighbourhood pushes back. And the language of that pushback — servant quarters, deport — reveals something about the terms on which integration was offered.

This is not unique to Britain. NRIs in Atherton, California have faced similar neighbourhood resistance to home expansions. In the Hamptons, Indian-owned properties have been subjects of zoning disputes that carry racial undertones their participants deny. The pattern is consistent: Indian money is welcome when it is discreet. When it is conspicuous — when it buys five flats instead of one, when it employs staff who need housing, when it transforms a postcode rather than merely inhabiting one — it encounters friction that no amount of purchase price can smooth.

## The bigger picture

Sonam Kapoor is not the first Indian celebrity to face property pushback abroad. She will not be the last. The story's resonance comes not from its celebrity component but from its universality. Every NRI who has ever been made to feel like a guest in a country they have paid taxes in for decades will see themselves in this story.

The five flats may indeed be investment properties. The mansion may be a perfectly legitimate purchase. But the conversation around them — the servant quarters language, the deportation rhetoric, the quiet pressure to stay silent — is a conversation about belonging. And for the Indian diaspora in Britain, it is a conversation that has been happening in private for a very long time.

It is now, thanks to a Bollywood actress and five apartments in Notting Hill, happening in public.""",
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
        img_url = fetch_pexels_image(art.get("image_search_query", ""))
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
