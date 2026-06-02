#!/usr/bin/env python3
"""Entertainment writer — 2026-06-02 batch"""

import json, os, sys, uuid, time, re
import requests, urllib.parse
from datetime import datetime, timezone

# ── Supabase config ──────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Pexels config ─────────────────────────────────────────────────────────────
PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")


# ── Image helpers ─────────────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    for q in [query, fallback_query]:
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
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Check image URL is valid, returns 200, and is > 5KB."""
    if not url:
        return False
    # Block banned sources
    banned = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com"]
    if any(b in url for b in banned):
        print(f"  ✗ Banned image source: {url[:60]}")
        return False
    banned_params = ["_nc_ht=", "_nc_cat=", "ccb="]
    if any(p in url for p in banned_params):
        print(f"  ✗ Banned signed URL params: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {ct}, {cl} bytes")
            return True
        # Some servers don't return Content-Length on HEAD
        if r.status_code == 200 and "image" in ct:
            print(f"  ✓ Image validated (no Content-Length): {ct}")
            return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def sb_insert(table, payload):
    """Insert row into Supabase, return the inserted row."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=payload,
    )
    if r.status_code in (200, 201):
        data = r.json()
        return data[0] if isinstance(data, list) else data
    print(f"  ✗ Insert error ({table}): {r.status_code} — {r.text[:300]}")
    return None


def sb_patch(table, filters, payload):
    """Patch a row in Supabase."""
    params = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=payload,
    )
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch error ({table}): {r.status_code} — {r.text[:300]}")
    return False


# ── Articles ──────────────────────────────────────────────────────────────────

articles = [
    {
        "headline": "Salman Khan Fires a Legal Notice at the Makers of Kala Hiran. The Producer Says He Won't Back Down.",
        "subheadline": "A blackbuck, a courtroom, and a personality rights battle that exposes Bollywood's next big legal frontier — all before the teaser even drops.",
        "slug": "salman-khan-kala-hiran-legal-notice-personality-rights-blackbuck-nri-20260602",
        "category": "entertainment",
        "sources": ["Filmfare", "Livemint", "MensXP", "BollywoodBubble"],
        "image_person": "Salman Khan",
        "image_pexels_query": None,
        "body": """Salman Khan's legal team has sent a formal cease-and-desist notice to the makers of *Kala Hiran: The Battle for Legacy*, a film reportedly inspired by the actor's 1998 blackbuck poaching case. The notice, issued through the law firm DSK Legal and dated April 24, demands an immediate halt to the film's development, production, and promotion.

## The Legal Argument

The crux of Salman's case rests on three pillars. First, that the blackbuck poaching case remains sub judice before the Rajasthan High Court, and any dramatisation of the events could amount to interference with judicial proceedings and impinge on his right to a fair trial. Second, that the film constitutes a "gross violation of personality rights" — the actor has not authorised the use of his name, persona, or events associated with him. Third, that the project is "defamatory in nature" and could damage his professional reputation and public image.

The notice specifically names casting director Akshay Pandey, alleging that he was approaching actors and circulating project materials — including a synopsis and character sketches — that drew a direct line to the blackbuck case. Salman's lawyers have demanded an unconditional written apology and warned that failure to comply within 24 hours would trigger both civil and criminal proceedings.

## The Producer Pushes Back

Producer Amit Jani, whose banner Jani Firefox Films previously made *Udaipur Files*, is not going quietly. He took to social media to share the legal notice publicly and accused Salman Khan of "threatening people related to the movie." His response: "The purpose of the notice is to intimidate people so that they succumb to his glamour. It's my nature to not be intimidated."

Jani maintains the film is not a biopic but a courtroom drama and crime thriller that uses the blackbuck case as a narrative springboard. Director Bharat S. Shrinate had reportedly shot portions in Sambhal and Moradabad in Uttar Pradesh, and the team had planned to release a first look poster and teaser on June 20.

## The Bigger Picture for the Diaspora

The dispute sits at the intersection of two legal concepts that Indian courts are still actively defining. Personality rights — the right of public figures to control commercial use of their name and image — have been the subject of several recent orders, including the Delhi High Court's sweeping ruling in Varun Dhawan's favour on AI deepfakes just weeks ago. But the boundaries between personality rights and artistic freedom remain blurry, especially when a film claims to be inspired by real events rather than depicting a specific person.

For NRIs who have followed Salman Khan's legal saga across decades — from the hit-and-run case to the blackbuck appeals — this latest front opens a new chapter. It is no longer just about the star and the courtroom. It is about who owns the story.

The film's poster features an unnamed actor resembling Salman, posing with a gun and wearing a firoza bracelet — a deliberate visual echo of the actor's real-life signature accessory. Whether a courtroom will see that as artistic expression or personality rights violation will likely define a legal precedent that extends far beyond one Bollywood star and one blackbuck.

*The teaser was planned for June 20. Whether it ever arrives now depends on what happens in a courtroom first.*""",
    },
    {
        "headline": "Zee Just Grabbed the FIFA World Cup. Ten Days Before Kickoff. For a Third of FIFA's Asking Price.",
        "subheadline": "After months of silence and a collapsed JioStar bid, Zee Entertainment swoops in with an eight-year deal, four new channels, and a $60 million bet that Indian football is finally ready to pay off.",
        "slug": "zee-fifa-world-cup-2026-india-broadcast-unite8-sports-deal-nri-20260602",
        "category": "entertainment",
        "sources": ["Reuters", "Inc42", "SacNilk", "BestMediaInfo"],
        "image_person": None,
        "image_pexels_query": "FIFA World Cup football stadium",
        "image_pexels_fallback": "soccer football match crowd",
        "body": """The 2026 FIFA World Cup starts on June 11 across the United States, Canada, and Mexico. Until yesterday, India — one of the world's fastest-growing football markets — did not have a confirmed broadcaster. That changed on Monday when Zee Entertainment announced it had secured the rights to broadcast the tournament and 38 other FIFA events through 2034.

## The Deal

FIFA had initially sought approximately $100 million for the India package covering the 2026 and 2030 World Cups. JioStar, the Reliance-Disney joint venture that had broadcast the 2022 tournament through its predecessor Viacom18, reportedly offered $20 million and was rejected. Sony, which held the rights for the 2014 and 2018 editions, held discussions but ultimately did not bid. FIFA eventually slashed its asking price to roughly $60 million, and Zee stepped in.

The deal covers 39 FIFA events, including both men's World Cups (2026 and 2030), the 2027 Women's World Cup, multiple youth tournaments, Futsal World Cups, the Intercontinental Cup, and docu-series content. It is the most comprehensive football rights package ever acquired by an Indian broadcaster.

## Unite8 Sports: Zee's New Sports Play

To house this acquisition, Zee is launching a brand-new sports network called Unite8 Sports. Four channels are going live: Unite8 Sports 1 (Hindi), Unite8 Sports 1 HD, Unite8 Sports 2 (English), and Unite8 Sports 2 HD. Airtel Digital TV has already lined up the channels in the 300–303 band, with activation set for June 4 — exactly one week before the opening match.

For digital viewers, ZEE5 will stream matches live. Zee's CEO Punit Goenka called the deal a reflection of "clear belief in football's long-term potential" and positioned it as a growth driver for youth engagement.

## What This Means for NRIs

For the Indian diaspora in the US, UK, and Canada, the Zee deal carries specific implications. NRIs in North America are in the unique position of having the World Cup literally in their backyard — games will be played in cities from New York to Los Angeles, from Toronto to Mexico City. While they can watch locally on Fox and Telemundo (in the US) or TSN (in Canada), the Zee deal ensures that Hindi and English commentary from an Indian perspective will be available via ZEE5 streaming.

This matters because the Indian football audience has evolved. The Indian Super League built a domestic fanbase, and the 2022 World Cup final between Argentina and France drew massive Indian viewership. Football is no longer a niche sport in India — it is the second-most-watched sport after cricket, particularly among viewers under 30.

## The Bigger Strategic Bet

Zee's move is as much about corporate positioning as it is about football. The company had exited sports broadcasting roughly eight years ago when it sold its sports assets to Sony. This deal marks a decisive re-entry, and it comes at a moment when Zee's stock price jumped approximately 7% on the announcement alone.

The implicit bet: that football, unlike cricket, is not yet locked up by JioStar's near-monopoly on premium Indian sports content. By securing FIFA rights for eight years, Zee is carving out a territory that no other Indian broadcaster controls. The Unite8 Sports brand is designed to carry more than just football — the channels are also planned for kabaddi, badminton, wrestling, boxing, and combat sports.

Whether this gamble pays off depends on advertising revenue, ZEE5 subscription growth, and whether Indian football fandom translates into sustained viewership beyond World Cup spikes. But for now, Zee has ensured that when India's 1.4 billion people want to watch the world's biggest sporting event, they know exactly where to find it.

*The opening match is June 11. Zee's channels go live June 4. The clock is ticking.*""",
    },
    {
        "headline": "Akshay Kumar Is Bringing Back the Welcome Franchise With the Biggest Ensemble Bollywood Has Assembled in Years.",
        "subheadline": "Welcome to the Jungle arrives June 26 with a cast list that reads like a '90s and 2000s reunion party — and Bollywood is betting big on nostalgia as its counter-programming weapon.",
        "slug": "welcome-to-the-jungle-akshay-kumar-june-26-ensemble-comedy-nri-20260602",
        "category": "entertainment",
        "sources": ["Bollywood Hungama", "Filmfare", "The Daily Jagran"],
        "image_person": "Akshay Kumar",
        "image_pexels_query": None,
        "body": """At a time when Hindi cinema is saturated with intense actioners, spy thrillers, and heavy-duty emotional dramas, *Welcome to the Jungle* is positioning itself as the stress-buster Bollywood badly needs. The film is scheduled for a theatrical release on June 26, and with Akshay Kumar leading an ensemble cast that borders on absurd in its size and ambition, it has already generated enormous buzz.

## The Cast

The cast list alone tells the story of what the makers are attempting. Akshay Kumar, Suniel Shetty, Paresh Rawal, Johnny Lever, Rajpal Yadav — the comedy veterans who anchored the original *Welcome* (2007) and its sequel *Welcome Back* (2015). Then add Arshad Warsi, Raveena Tandon, Lara Dutta, Jacqueline Fernandez, Disha Patani, Tusshar Kapoor, and Shreyas Talpade. The film has managed what most Bollywood productions struggle to do in today's date-sheet-driven industry: get more than a dozen established names in front of the same camera.

Mounting a multi-starrer at this scale is not easy. Dates are difficult to match, actor combinations are tricky, costs escalate rapidly, and every performer expects screen time that justifies their presence. Yet the *Welcome* franchise has always operated on an unspoken promise — controlled chaos, where everyone gets their moment and nobody needs to carry the film alone.

## Why It Matters for the Diaspora

The original *Welcome* occupies a particular space in the Indian diaspora's collective memory. It is, alongside *Hera Pheri*, *Bhagam Bhag*, and *Housefull*, one of those films that NRI families have watched repeatedly on long flights, during Diwali gatherings, and at Saturday night house parties. Its dialogue has become shorthand in group chats. Nana Patekar's "Aapka ghoda kitna paani mein?" entered the diaspora lexicon the same way "Babu Bhaiya" did from *Hera Pheri*.

*Welcome to the Jungle* is betting that this nostalgia carries real box-office power. The timing is deliberate — a June 26 release sits in the summer window when overseas markets traditionally spike, and NRI audiences are the most reliable ticket-buyers for big Hindi comedies.

## Akshay Kumar's Comic Reset

The film also represents something personal for Akshay Kumar. Before the action universes and pan-India spectacles became the industry's default mode, Akshay had built one of Bollywood's strongest comic legacies. His ability to play chaos with a straight face, to react deadpan in the middle of absurdity, was what made him irreplaceable in films like *Garam Masala* and *Bhool Bhulaiyaa*. Recent years have seen him swing between patriotic dramas and action vehicles with diminishing returns. *Welcome to the Jungle* is a deliberate return to the zone audiences have loved him in for decades.

## The Counter-Programming Angle

June 2026 is one of the most stacked months in Indian cinema. Ram Charan's *Peddi* opens June 4. Yash's *Toxic* arrives the same day. Bobby Deol and Anurag Kashyap's *Bandar* releases June 5. Diljit Dosanjh's *Main Vaapas Aaunga* follows on June 12. Samantha Ruth Prabhu's *Maa Inti Bangaram* hits on June 19. And Shahid Kapoor's *Cocktail 2* targets the same week.

In a month dominated by intense, dark, and action-heavy films, *Welcome to the Jungle* is the only major release that promises pure, uncut laughter. That positioning could be its biggest advantage — the counter-programming play that gives audiences a breather between all the gunfights and courtroom dramas.

Whether the franchise magic still works in 2026, nearly two decades after the original, is the multi-hundred-crore question. But if the first day's advance bookings follow the pattern of previous *Welcome* films, Bollywood's biggest stress-buster might also become its most commercially significant comedy of the year.

*Welcome to the Jungle arrives in theatres on June 26. For NRIs in North America, expect IMAX and premium format screenings in major metros.*""",
    },
]


# ── Publish loop ──────────────────────────────────────────────────────────────
published = 0
for art in articles:
    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline'][:70]}...")

    # Image sourcing
    img_url = None
    img_attribution = None

    # 1. Wikipedia for person articles
    if art.get("image_person"):
        img_url = fetch_wikipedia_person_image(art["image_person"])
        if img_url:
            img_attribution = "Wikimedia Commons"

    # 2. Pexels fallback
    if not img_url and art.get("image_pexels_query"):
        img_url = fetch_pexels_image(
            art["image_pexels_query"],
            art.get("image_pexels_fallback"),
        )
        if img_url:
            img_attribution = "The Videshi"

    # 3. Validate
    if img_url and not validate_image_url(img_url):
        print(f"  ⚠ Image failed validation, publishing without image")
        img_url = None
        img_attribution = None

    # Build payload
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "body": art["body"],
        "category": art["category"],
        "status": "published",
        "published_at": now,
        "sources": json.dumps(art["sources"]),
        "is_editorial": False,
    }

    if img_url:
        payload["image_url"] = img_url
    if img_attribution:
        payload["image_attribution"] = img_attribution

    row = sb_insert("p2_articles", payload)
    if row:
        art_id = row.get("id", "unknown")
        print(f"  ✓ Published: {art['slug']} (id={art_id})")
        published += 1
    else:
        print(f"  ✗ FAILED to publish: {art['slug']}")

    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
