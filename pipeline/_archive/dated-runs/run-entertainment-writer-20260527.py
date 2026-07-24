#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-27 run"""

import json, os, sys, uuid, re, time
from datetime import datetime, timezone
import requests, urllib.parse, subprocess

# --- Config ---
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# --- Wikipedia image fetcher ---
def fetch_wikipedia_person_image(person_name):
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
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    pexels_key = os.environ.get("PEXELS_API_KEY", "")
    if not pexels_key:
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        cmd = ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3", "-H", f"Authorization: {pexels_key}"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    if not url:
        return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except:
        pass
    return False

def sb_insert(table, row):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=row, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        return data[0] if isinstance(data, list) else data
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:500]}")
        return None

# ============================================================
# ARTICLES
# ============================================================

articles = [
    {
        "headline": "Madhuri Dixit Lived in Denver for Fifteen Years, Raised Two Sons, and Came Back to Bollywood. On June 4, She Hides a Dead Body on Netflix.",
        "subheadline": "Maa Behen pairs Madhuri with Triptii Dimri in a dark comedy about a mother-daughter trio covering up a murder in their colony. It is the most un-Madhuri thing Madhuri has ever done.",
        "slug": "madhuri-dixit-maa-behen-netflix-june-4-dark-comedy-triptii-dimri-nri-comeback-20260527",
        "category": "entertainment",
        "vertical": "entertainment",
        "tags": ["madhuri-dixit", "triptii-dimri", "maa-behen", "netflix", "dark-comedy", "nri", "streaming", "dharna-durga"],
        "urgency": "daily",
        "score_total": 78,
        "sources_json": json.dumps([
            {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/news/bollywood/maa-behen-trailer-out-madhuri-dixit-triptii-dimri/"},
            {"name": "Netflix India", "url": ""},
            {"name": "Hollywood Reporter India", "url": "https://hollywoodreporterindia.com/maa-behen-netflix/"},
            {"name": "Filmfare", "url": "https://www.filmfare.com/news/bollywood/maa-behen-trailer-madhuri-dixit-triptii-dimri"}
        ]),
        "persons": ["Madhuri Dixit", "Triptii Dimri"],
        "pexels_query": "Indian family comedy drama",
        "pexels_fallback": "Bollywood actress comedy",
        "body": """For a generation of NRIs, Madhuri Dixit is not just an actress. She is a timestamp. She is the woman in your parents' wedding video playlist, the reason your mother owns a VHS copy of *Hum Aapke Hain Koun*, the face that launched a thousand Bollywood nights at community centers from Edison to Fremont.

And then she left.

In 2002, Madhuri married Dr. Shriram Nene, a cardiovascular surgeon based in Denver, Colorado, and effectively vanished from Hindi cinema for a decade. She raised two sons — Arin and Ryan — in suburban America, far from the paparazzi and the Filmfare stage. She was, by all accounts, an NRI mom. Soccer games, school runs, the works.

When she returned to Mumbai in 2011, the industry had moved on. The heroines were younger, the scripts were different, the audience had splintered across platforms. Her comeback films — *Dedh Ishqiya*, *Gulaab Gang*, *Bucket List* — were respectable but not the blockbusters of her prime.

## Then Netflix Called

*Maa Behen*, premiering June 4 on Netflix, is not a comeback vehicle. It is something riskier: a role that asks one of India's most beloved screen presences to play against type entirely.

Directed by Suresh Triveni — the man behind *Tumhari Sulu* and *Jalsa* — the film is a dark comedy about three women in Adarsh Colony: Rekha (Madhuri), Jaya (Triptii Dimri), and Sushma (content creator Dharna Durga). When the body of Mr. Gupta (played by Ravi Kishan) turns up in Rekha's home, the three women must cover up the crime while navigating nosy neighbours, family dysfunction, and their own fractured relationships.

The trailer, which dropped on May 22, shows Madhuri doing things audiences have never seen from her: panicking, scheming, lying through her teeth. It is the furthest cry from *Dil To Pagal Hai* imaginable.

## Why NRIs Should Care

Madhuri's American chapter is not incidental to this story. It *is* the story — at least the meta one. She is the rare Bollywood star who lived the NRI life authentically: the cultural dislocation, the identity recalibration, the quiet reinvention that happens when you are no longer the biggest star in the room but someone's mom at a Colorado school function.

That lived experience may be what makes *Maa Behen* resonate. The film's themes — family secrets, generational silence, women protecting each other in impossible situations — are universal, but they hit differently when the woman hiding the body once danced to *Dhak Dhak Karne Laga*.

Triptii Dimri, meanwhile, has become the most bankable young actress in Hindi cinema since her breakout in *Animal* and *Bhool Bhulaiyaa 3*. Pairing her with Madhuri is a generational handshake: the actress your parents loved meeting the actress your younger sibling cannot stop watching.

## What Is Next

*Maa Behen* is part of Netflix's aggressive June slate, which also includes the JioHotstar premiere of *Dhurandhar 2* (June 4) and *House of the Dragon* Season 3. The film is produced by Abundantia Entertainment — the production house behind *Shakuntala Devi*, *Sherni*, and *Jalsa* — all of which were women-led stories that found their audience on streaming.

For Madhuri, this is not about proving she can still open a film. It is about proving she does not need to. The NRI chapter is over. The Netflix chapter has just begun."""
    },
    {
        "headline": "Abhijeet Bhattacharya Called the Chunnari Chunnari Remake a 'Bhajan.' The Internet Agreed. Now There Is a Lawsuit.",
        "subheadline": "Varun Dhawan's 'Hai Jawani Toh Ishq Hona Hai' remixed the 1999 anthem without consulting the original singer. The copyright dispute, the nostalgia backlash, and why NRIs took it personally.",
        "slug": "chunnari-chunnari-remake-controversy-abhijeet-varun-dhawan-nostalgia-copyright-nri-20260527",
        "category": "entertainment",
        "vertical": "entertainment",
        "tags": ["chunnari-chunnari", "abhijeet-bhattacharya", "varun-dhawan", "remake", "copyright", "nostalgia", "david-dhawan", "nri"],
        "urgency": "daily",
        "score_total": 74,
        "sources_json": json.dumps([
            {"name": "Filmfare", "url": "https://www.filmfare.com/news/bollywood/abhijeet-bhattacharya-criticises-varun-dhawan-chunnari-chunnari-remake"},
            {"name": "MensXP", "url": "https://www.mensxp.com/entertainment/bollywood/varun-dhawan-teases-ramesh-taurani-copyright-case"},
            {"name": "GIBN", "url": "https://globalindiabroadcastnews.com/abhijeet-bhattacharya-criticizes-chunnari-chunnari-remake"},
            {"name": "Indulge Express", "url": "https://www.indulgexpress.com/entertainment/abhijeet-bhattacharya-labels-chunnari-chunnari-bhajan"}
        ]),
        "persons": ["Varun Dhawan", "Abhijeet Bhattacharya"],
        "pexels_query": "Indian wedding dance celebration",
        "pexels_fallback": "Bollywood dance party celebration",
        "body": """There is a specific category of Bollywood songs that do not belong to any one film anymore. They belong to the diaspora. They play at every garba night in New Jersey, every Diwali party in Toronto, every sangeet in London. *Chunnari Chunnari* — from David Dhawan's 1999 film *Biwi No. 1* — is one of them.

So when Varun Dhawan, David Dhawan's son, released a remixed version of the song for his upcoming film *Hai Jawani Toh Ishq Hona Hai* (releasing June 5), the reaction was not just criticism. It was grief.

## The Singer Speaks

Abhijeet Bhattacharya, who sang the original *Chunnari Chunnari* alongside Anu Malik's composition, did not hold back. In interviews this week, he called the remake a "bhajan" — a devotional hymn — implying the remake had drained the song of every ounce of its original energy.

"Varun Dhawan iss gaane se Salman Khan nahi ban sakta," Abhijeet said bluntly. *Varun Dhawan cannot become Salman Khan through this song.* He went on to say that the producers never consulted him about the recreation, that the original's legacy would be "degraded," and that Bollywood's obsession with remaking 90s hits was creative bankruptcy dressed as nostalgia.

He is not entirely wrong.

## The Copyright Mess

Beyond the artistic debate, *Hai Jawani Toh Ishq Hona Hai* has walked into a legal minefield. Vashu Bhagnani, the original producer of *Biwi No. 1*, has filed a court case over the use of both *Chunnari Chunnari* and *Ishq Sona Hai* in the new film. Bhagnani argues that the tracks belong to the original production and cannot be reused without proper clearance.

Tips Industries, which holds the music rights, maintains that they have the legal authority to license the songs. The dispute is ongoing, and the irony is rich: a David Dhawan film is being sued for using songs from another David Dhawan film.

Varun Dhawan himself appeared to treat the controversy lightly, teasing producer Ramesh Taurani about the legal mess at a recent event. The internet was less amused.

## Why NRIs Took It Personally

Here is the thing about 90s Bollywood songs for the diaspora: they are not just music. They are cultural infrastructure. *Chunnari Chunnari* is the song your cousin choreographed a sangeet dance to in 2003. It is the song that played at every Indian grocery store in the early 2000s. It is the sound of being Indian abroad before streaming existed, when culture travelled on pirated CDs and satellite TV.

Remaking it is not like remaking any song. It is touching something sacred — and the backlash reflects that. Comments on social media ranged from "ruined another iconic song" to "90s kids crying" to longer posts about how Bollywood has systematically strip-mined its own legacy for content.

## The Bigger Pattern

This is not an isolated incident. Bollywood has spent the last five years remaking, remixing, or "recreating" classic tracks at an industrial pace. *Tip Tip Barsa Pani*, *Saki Saki*, *O O Jaane Jaana*, *Maahi Ve* — the list is long and the originals are almost always better.

The economics are simple: a familiar hook gets clicks. But the cost is harder to measure. Every bad remake makes the next one less interesting and the original less special. At some point, the nostalgia well runs dry.

*Hai Jawani Toh Ishq Hona Hai* releases June 5. It is reportedly David Dhawan's final directorial film. Whether the *Chunnari Chunnari* remake is remembered as a tribute or a travesty will depend entirely on who you ask — and when they grew up."""
    },
    {
        "headline": "Hollywood and Bollywood Just Made It Official. The LA-India Film Council Wants Indian Filmmakers to Shoot in Los Angeles.",
        "subheadline": "The new council will ease permits, fast-track visas, and offer tax incentives to Indian productions. For NRI filmmakers who have always lived between two industries, this is the door they have been waiting for.",
        "slug": "la-india-film-council-bollywood-hollywood-collaboration-permits-visas-nri-filmmakers-20260527",
        "category": "entertainment",
        "vertical": "entertainment",
        "tags": ["bollywood-hollywood", "la-india-film-council", "anil-ambani", "bobby-bedi", "indian-filmmakers", "nri", "co-production", "los-angeles"],
        "urgency": "daily",
        "score_total": 72,
        "sources_json": json.dumps([
            {"name": "Goldsea Asian American Daily", "url": "https://goldsea.com/bollywood-takes-bigger-role-in-hollywood"},
            {"name": "Bollywood Hungama", "url": ""},
            {"name": "California Film Commission", "url": ""}
        ]),
        "persons": ["Anil Ambani", "Bobby Bedi"],
        "pexels_query": "Hollywood sign Los Angeles film industry",
        "pexels_fallback": "movie production studio camera",
        "body": """For decades, the relationship between Hollywood and Bollywood has been polite but transactional. Indian productions would occasionally shoot a song sequence in Switzerland or a chase scene in Spain, and Hollywood would occasionally cast an Indian actor in a supporting role and call it representation. The actual infrastructure for sustained collaboration — permits, visas, co-production treaties, shared studio space — barely existed.

That changed this week.

## The Council

The Los Angeles-India Film Council, announced on May 26, is a formal joint initiative designed to make it significantly easier for Indian filmmakers to shoot in Los Angeles and for Hollywood studios to co-produce with Indian partners. The council is led by Anil Ambani and veteran producer Bobby Bedi on the Indian side, with participation from the LA Mayor's office and the California Film Commission.

The key provisions are concrete, not aspirational:

- **Simplified permits** for Indian productions shooting in LA County
- **Fast-tracked visa processing** for Indian cast and crew working on approved projects
- **Tax incentives** aligned with California's existing film production credits, extended to qualifying Indian co-productions
- **Anti-piracy cooperation** between Indian and American enforcement agencies
- **Shared studio access** at facilities in Burbank and Culver City

This is not the first time someone has tried to bring Bollywood to LA. But it is the first time there is a formal institutional structure behind it, with government backing on both sides.

## The Numbers Behind the Move

India's film industry produces over 1,800 films annually — more than any country on earth. The Indian box office crossed $2.7 billion in 2025, and the overseas market (primarily the US, UK, Canada, Australia, and the Gulf) accounts for a growing share of revenue. *Dhurandhar 2* alone has crossed Rs 1,150 crore domestically and earned over $60 million overseas.

Los Angeles, meanwhile, has been losing production to Georgia, New York, and the UK — all of which offer more aggressive tax incentives. The LA-India Film Council is partly a play to stem that bleeding by tapping into the single largest film-producing nation on earth.

For Indian producers, the math works too. Shooting in LA — when you can actually get permits and visas without a six-month bureaucratic marathon — gives access to Hollywood-grade post-production facilities, a massive NRI audience in Southern California, and the credibility that comes with an American production address.

## What It Means for NRI Filmmakers

The most interesting beneficiaries of this council are not the Ambanis or the big studio heads. They are the thousands of Indian-origin filmmakers already living in Los Angeles who have spent their careers toggling between two industries that did not talk to each other.

These are the directors who went to film school at USC or UCLA and then could not get a permit to shoot their Bollywood project in the city they live in. The producers who had to fly entire Indian crews to Thailand or Europe because the US visa process for entertainment workers was prohibitively slow. The NRI cinematographers and editors who work on Hollywood sets by day and moonlight on Indian projects by night, never quite belonging to either industry.

The LA-India Film Council does not solve all of those problems, but it creates a pathway. If it works as designed, an Indian filmmaker living in Glendale should be able to produce a Hindi-language film in LA with the same ease as a Hollywood production — which, if you have ever tried to do this before, would be revolutionary.

## The Precedent

Indian productions have shot in LA before — *My Name Is Khan* (2010) and *Dhoom 3* (2013) being the most notable examples. But those were exceptions that required extraordinary resources and personal connections. The council aims to make that the rule, not the exception.

Bobby Bedi, who has produced cross-cultural films like *Fire* and *Bandit Queen*, called the initiative "long overdue" and emphasized that the real opportunity is in co-productions — films made jointly by Indian and American teams, for global audiences, with shared IP and distribution.

For the 4.4 million Indian-Americans in the United States — many of whom consume both Bollywood and Hollywood — this convergence has been a long time coming. The question is whether a formal council can do what informal relationships have not: make the two largest film industries in the world actually work together, not just next to each other."""
    },
]


# ============================================================
# PUBLISH
# ============================================================

def publish_article(art):
    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline'][:80]}...")

    # 1. Image sourcing — Wikipedia first for persons
    img_url = None
    img_attr = None

    for person in art.get("persons", []):
        img_url = fetch_wikipedia_person_image(person)
        if img_url:
            img_attr = "Wikimedia Commons"
            break

    # Fall back to Pexels
    if not img_url:
        img_url = fetch_pexels_image(art["pexels_query"], art.get("pexels_fallback"))
        if img_url:
            img_attr = "Pexels"

    # Validate
    if img_url and not validate_image_url(img_url):
        print(f"  ⚠ Image validation failed: {img_url[:60]}...")
        # Try next person or Pexels
        img_url = None
        img_attr = None
        # Attempt pexels fallback if Wikipedia failed validation
        img_url = fetch_pexels_image(art["pexels_query"], art.get("pexels_fallback"))
        if img_url:
            if validate_image_url(img_url):
                img_attr = "Pexels"
            else:
                img_url = None

    if img_url:
        print(f"  ✓ Final image: {img_url[:80]}...")
    else:
        print(f"  ⚠ No valid image — publishing without image")

    # 2. Insert article
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "body": art["body"].strip(),
        "category": "entertainment",
        "vertical": "entertainment",
        "status": "published",
        "published_at": now,
        "sources": art["sources_json"],
        "tags": art["tags"],
        "urgency": art["urgency"],
        "score_total": art["score_total"],
        "image_url": img_url,
        "image_attribution": img_attr,
    }
    result = sb_insert("p2_articles", row)
    if result:
        art_id = result.get("id")
        print(f"  ✓ Published: {art_id} — {art['slug']}")
        return art_id
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")
        return None


if __name__ == "__main__":
    published = []
    for art in articles:
        art_id = publish_article(art)
        if art_id:
            published.append((art_id, art["slug"]))
        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Done. Published {len(published)}/{len(articles)} articles.")
    for pid, slug in published:
        print(f"  ✓ {pid} — {slug}")
