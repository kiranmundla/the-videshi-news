#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-28 batch."""

import json, os, sys, time, uuid, re
import requests
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

PEXELS_KEY = None
try:
    with open(os.path.expanduser("~/.env.pexels")) as f:
        for line in f:
            if "PEXELS_API_KEY" in line:
                PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
except Exception:
    pass

# ── Image helpers ────────────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = requests.utils.quote(person_name.replace(' ', '_'))
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
    """Fetch a relevant image from Pexels. Returns URL or None."""
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
                timeout=10
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


def validate_image(url):
    """Verify an image URL returns 200 with image content and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD properly
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct:
            # Read a chunk to verify
            chunk = r.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation failed for {url[:60]}: {e}")
    return False


def sb_insert(table, payload):
    """Insert a row into Supabase and return the response."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if r.status_code in (200, 201):
        data = r.json()
        return data[0] if isinstance(data, list) and data else data
    else:
        print(f"  ✗ Insert to {table} failed ({r.status_code}): {r.text[:300]}")
        return None


# ── Articles ─────────────────────────────────────────────────────────────────

articles = []

# ─── Article 1: Karuppu ──────────────────────────────────────────────────────
articles.append({
    "headline": "Karuppu Was Supposed to Be Vijay's Last Film. Suriya Took It to ₹253 Crore.",
    "subheadline": "The Tamil fantasy blockbuster was written for the Chief Minister. Then RJ Balaji gave it to Suriya, who delivered the highest-grossing Tamil film of 2026 and his career-best.",
    "slug": "karuppu-suriya-vijay-last-film-253-crore-rj-balaji-tamil-blockbuster-nri-20260528",
    "category": "entertainment",
    "body": """When RJ Balaji sat across from Vijay in a room in Chennai and narrated the story of a guardian deity who disguises himself as a lawyer to fight judicial corruption, both men knew it was a farewell. Vijay was preparing to leave cinema for politics. This was supposed to be his last film.

"This was supposed to be his last film, so we had two or three meetings which went on for some time, discussing things like him entering politics and taking a call as to which film to make as his last film," Balaji told The Hollywood Reporter India.

Vijay backed out. Balaji respected the decision. And then the producers asked the obvious question: can you narrate it to Suriya?

## The Film That Nearly Didn't Happen

Karuppu was initially scheduled for May 14, 2026. Then the shows got cancelled. The audience waited exactly one day. On May 15, Suriya and Trisha Krishnan's fantasy courtroom drama opened across India — and something extraordinary happened.

The film crossed ₹100 crore in Tamil Nadu alone within eight days. It became the first Tamil film in nine months to hit the ₹100 crore mark in India, ending a drought that had lasted since Rajinikanth's Coolie. By Day 12, the worldwide gross had climbed past ₹253 crore, with approximately ₹160 crore in India net and significant overseas contributions.

For Suriya, this was personal. After years of mid-range commercial results, Karuppu became his first ₹100 crore film in India and his highest-grossing film ever — by a massive margin.

## Ancient Mythology Meets Modern Courtroom

The premise is deceptively simple. A father's gold is stolen. He prays to the guardian deity Karuppasamy. The deity takes human form — as a lawyer named Saravanan — and walks into a corrupt courtroom to deliver divine justice. What follows blends Tamil folk religion, superhero-scale action, and genuine social commentary about a judicial system that fails the poor.

RJ Balaji, who both directed and co-starred, has made a career of wrapping populist political commentary inside commercial Tamil cinema. But Karuppu operates on a different scale. GK Vishnu's cinematography gives the deity sequences an almost mythological grandeur, and Sai Abhyankkar's score pushes the emotional crescendos past standard masala territory.

## The Suriya-Trisha Reunion

The last time Suriya and Trisha Krishnan shared a screen was in 2005's Aaru — twenty-one years ago. Their reunion in Karuppu has been one of the film's most discussed elements, with audiences and critics both noting the effortless chemistry that time apparently did not diminish.

The supporting cast includes Indrans (the National Award-winning Malayalam actor making his Tamil debut), Swasika, Sshivada, and Yogi Babu, with RJ Balaji himself playing a key role.

## A Sequel Is Coming

At a recent meet-and-greet, Suriya dropped a telling line: "Belief is life." The film's epilogue already hints at a sequel titled Karuppu vs Vellai — Black vs White. Given the box office numbers, it's not a question of if but when.

Balaji thanked Vijay — now Tamil Nadu's Chief Minister — in the opening credits. Vijay personally congratulated the team after the film's release. "The entire thing happened because he asked me the right questions after my narration, questions that made my film and my script better," Balaji said.

## What It Means for the Diaspora

Karuppu is streaming in Tamil, Telugu (as Veerabhadrudu), Hindi, Malayalam, and Kannada — making it accessible to virtually every Indian language audience abroad. The film's overseas gross of approximately ₹57 crore in its first week alone signals that the Tamil diaspora showed up in force, particularly in Malaysia, Singapore, the US, and the Gulf states.

For NRIs who grew up watching Suriya in Ghajini, Kaakha Kaakha, and Singham, this is the comeback they have been waiting for — and perhaps the most satisfying second act in contemporary Tamil cinema.""",
    "sources": [
        {"url": "https://www.hollywoodreporterindia.com", "name": "The Hollywood Reporter India"},
        {"url": "https://www.cinemaexpress.com", "name": "Cinema Express"},
        {"url": "https://www.pinkvilla.com", "name": "Pinkvilla"},
        {"url": "https://www.koimoi.com", "name": "Koimoi"},
    ],
    "vertical": "entertainment",
    "tags": ["Suriya", "Karuppu", "Vijay", "RJ Balaji", "Tamil cinema", "Trisha Krishnan", "box office"],
    "image_person": "Suriya (actor)",
    "image_attribution": "Wikimedia Commons",
})

# ─── Article 2: Bhooth Bangla ────────────────────────────────────────────────
articles.append({
    "headline": "Bhooth Bangla Just Crossed ₹260 Crore. Akshay Kumar's Longest Box Office Run in a Decade.",
    "subheadline": "Priyadarshan's horror-comedy is the third-biggest Bollywood grosser of 2026 and Akshay Kumar's most durable hit since Housefull 4. It's still in theatres on Day 40.",
    "slug": "bhooth-bangla-260-crore-akshay-kumar-priyadarshan-horror-comedy-third-biggest-2026-nri-20260528",
    "category": "entertainment",
    "body": """Forty days into its theatrical run, Bhooth Bangla is still filling seats. That sentence, applied to an Akshay Kumar film in 2026, would have been dismissed as fantasy three months ago.

The horror-comedy directed by Priyadarshan has crossed ₹260 crore worldwide — approximately ₹175 crore net in India and over ₹48 crore from overseas territories. It is now the third-highest-grossing Bollywood film of 2026, behind only the Dhurandhar franchise's colossal numbers. And for Akshay Kumar, it represents something far more significant than a box office milestone.

## The Priyadarshan Factor

Priyadarshan and Akshay Kumar built an empire together in the 2000s. Hera Pheri, Bhool Bhulaiyaa, Bhagam Bhag, Garam Masala — these films defined a generation of Bollywood comedy. Then came a decade-long gap, during which Akshay shifted to nationalistic dramas, social message films, and action thrillers with diminishing returns.

Bhooth Bangla is a deliberate return to what worked. Priyadarshan has constructed a haunted-house comedy that plays on every horror trope while relying on Kumar's physical comedy instincts — the same instincts that made Bhool Bhulaiyaa a cultural landmark in 2007.

The results speak for themselves. Bhooth Bangla has already surpassed OMG 2 to become Akshay Kumar's third-biggest post-pandemic film. Its legs are remarkable: the film earned ₹100 crore in India by Day 13 and has continued adding steady numbers through its fifth and sixth weeks, a rarity in an era where most Bollywood films evaporate after the opening weekend.

## Horror-Comedy: Bollywood's Safest Bet

The genre is on an unprecedented streak. Stree 2 shattered records in 2024. Bhool Bhulaiyaa 3 crossed ₹400 crore worldwide in the same year. Now Bhooth Bangla adds another data point to what is becoming Bollywood's most reliable formula.

The pattern is clear: Indian audiences are choosing laughter and scares over earnest social dramas. The horror-comedy allows for star-driven set pieces, memorable supporting characters, catchy music, and franchise potential — all wrapped in a premise that travels across demographics.

Bhooth Bangla benefits particularly from occupancy in Tier 2 and Tier 3 cities, where family audiences have driven its weekday numbers consistently. Cities like Pune, Bengaluru, and Ahmedabad have shown stronger holds than the traditional Mumbai-Delhi corridor.

## The BookMyShow Record

Bollywood's box office in 2026 has been dominated by a single metric: BookMyShow ticket sales. Dhurandhar 2 crossed 18 million tickets on the platform, an all-time record. Bhooth Bangla, while not in that stratosphere, has comfortably entered the top-performing films of the year on the platform, validating the horror-comedy genre's mainstream appeal.

What is notable about Bhooth Bangla's performance is not the peak but the plateau. The film's daily collections have remained above ₹1 crore even in its sixth week — a feat that most 2026 Bollywood releases, including some that opened much bigger, could not sustain.

## Why the Diaspora Cares

For NRIs, the Priyadarshan-Akshay reunion carries deep nostalgia value. Hera Pheri and Bhool Bhulaiyaa are comfort films for an entire generation that grew up in Indian households abroad — films that played at family gatherings, on road trips, and during every Diwali weekend.

Bhooth Bangla's overseas gross of ₹48 crore confirms that the diaspora responded to that nostalgia. The film's clean comedy and family-friendly tone — no graphic violence, no heavy social messaging — made it an easy choice for multiplex audiences in North America, the UK, and Australia.

The question now is whether this represents a genuine course correction for Akshay Kumar's career. His recent track record has been uneven: Selfiee, Bade Miyan Chote Miyan, Khel Khel Mein, and Sarfira all underperformed. Bhooth Bangla suggests the answer was always obvious — stay in the lane where the audience already loves you.""",
    "sources": [
        {"url": "https://sacnilk.com", "name": "Sacnilk"},
        {"url": "https://www.bollywoodhungama.com", "name": "Bollywood Hungama"},
        {"url": "https://www.koimoi.com", "name": "Koimoi"},
    ],
    "vertical": "entertainment",
    "tags": ["Akshay Kumar", "Bhooth Bangla", "Priyadarshan", "horror-comedy", "box office", "Bollywood 2026"],
    "image_person": "Akshay Kumar",
    "image_attribution": "Wikimedia Commons",
})

# ─── Article 3: Netflix Telugu Slate ──────────────────────────────────────────
articles.append({
    "headline": "Netflix Just Spent Over ₹500 Crore on Telugu Cinema. This Is the 2026 Slate.",
    "subheadline": "Thirteen films. Ram Charan, Pawan Kalyan, Nani, Fahadh Faasil, Vijay Deverakonda, Dulquer Salmaan. The streaming giant's Telugu bet is now bigger than most Bollywood budgets.",
    "slug": "netflix-telugu-slate-2026-500-crore-peddi-pawan-kalyan-nani-tollywood-nri-streaming-20260528",
    "category": "entertainment",
    "body": """Netflix South has unveiled its 2026 Telugu film slate, and the numbers are staggering. The streaming giant has secured post-theatrical digital rights for thirteen Telugu films, with reported acquisition costs that collectively exceed ₹500 crore — a figure that, even two years ago, would have seemed implausible for a single regional language.

The headline deal: ₹105–130 crore for Ram Charan's Peddi alone. Then ₹80–100 crore for Pawan Kalyan's Ustaad Bhagat Singh. Then ₹65 crore for Nani's The Paradise. The economics of Telugu cinema have shifted permanently, and Netflix is leading the bet.

## The Big Three

**Peddi** opens June 4 with A.R. Rahman's soundtrack, a ₹250–300 crore production budget, and advance booking numbers in North America that are already challenging RRR's premiere records. Ram Charan plays a rugged 1980s villager who uses cricket to defend his community's honour. The first single, Chikiri Chikiri, crossed 200 million views. Netflix's digital rights deal helps the film recover a massive portion of its budget before a single ticket is sold.

**Ustaad Bhagat Singh** marks Pawan Kalyan's return to the screen after his political commitments. Director Harish Shankar has confirmed this is an original script — not a remake — tailored specifically for the Power Star. Pawan Kalyan plays a police officer, with Sreeleela and Raashii Khanna in the cast. The budget sits at ₹150–170 crore, and Netflix's reported ₹80–100 crore digital deal underscores the platform's belief in the film's global appeal.

**The Paradise** reunites Nani with Dasara director Srikanth Odela in what Nani himself has called "India's Mad Max." Set in 1980s Secunderabad, it follows a marginalized community's fight for survival, with Mohan Babu as the antagonist and Raghav Juyal making his Telugu debut. Anirudh Ravichander composed the score. Netflix paid ₹65 crore for the streaming rights — the highest for any Nani film.

## The Prestige Projects

Two films on the slate carry particular weight for cinephiles.

**Don't Trouble the Trouble** pairs Fahadh Faasil — arguably the best actor working in Indian cinema — with director Shashank Yeleti, and is presented by SS Rajamouli under Arka Mediaworks. A fantasy-tinged drama about a character who "counts his fortune amidst sirens and screams," it will stream in five languages after its theatrical run. Rajamouli's name as presenter alone elevates this beyond a standard acquisition.

**VD14** is Vijay Deverakonda's most ambitious project: a period epic set during British colonial rule in the Rayalaseema region (1854–1878). The cast is extraordinary — Amitabh Bachchan in a pivotal role, Rashmika Mandanna, and South African actor Arnold Vosloo (The Mummy) as a British officer. Ajay-Atul composed the score. The budget exceeds ₹100 crore.

## The Discovery Plays

Netflix's Telugu slate is not all star-driven spectacle. 418 is a supernatural thriller about a haunted hotel room. Biker is India's first authentic motocross racing film, with Sharwanand undergoing real track training. Raakaasa headlines Sangeeth Shobhan in a revenge thriller. Funky reunites Vishwak Sen with Jathi Ratnalu director Anudeep KV for a satire on the film industry itself.

These mid-budget films — with budgets between ₹30–60 crore — represent Netflix's conviction that Telugu cinema's audience has an appetite beyond the ₹100-crore tentpoles.

## What It Means for NRIs

Here is the shift that matters for the diaspora: these thirteen films will be available globally on Netflix in Telugu, Tamil, Hindi, Malayalam, and Kannada within weeks of their theatrical release. For NRIs who cannot get to an Indian cinema, or who live in cities without Telugu-language screens, Netflix has essentially become the primary window.

The platform's investment also reflects a demographic truth. Telugu-speaking audiences abroad — particularly in the US, UK, Canada, and Australia — are among the highest-spending diaspora moviegoers per capita. They drove Baahubali's international gross. They made RRR a global phenomenon. They powered Pushpa 2's overseas numbers.

Netflix is not making a bet on Telugu cinema. It is following the money that the diaspora already laid down.

## The Bigger Picture

Two years ago, Netflix India was perceived as a Hindi-first platform struggling with subscriber churn. The Telugu slate announcement is the clearest signal yet that the strategy has fundamentally changed. Regional cinema — particularly from the South — is now the growth engine.

JioHotstar's ₹4,000 crore investment in South Indian content, announced earlier this week, confirms the trend. Amazon Prime Video has been acquiring Tamil and Malayalam rights aggressively. But Netflix's Telugu slate, with its combination of star power, auteur-driven projects, and mid-budget genre films, represents the most coherent and ambitious regional cinema strategy from any global streaming platform operating in India.

The era of Telugu cinema as a "regional" afterthought is over. The numbers have made that argument for years. Netflix just put ₹500 crore behind the obvious conclusion.""",
    "sources": [
        {"url": "https://sacnilk.com", "name": "Sacnilk"},
        {"url": "https://www.filmibeat.com", "name": "FilmiBeat"},
        {"url": "https://www.whats-on-netflix.com", "name": "What's on Netflix"},
        {"url": "https://bizzbuzz.news", "name": "Bizz Buzz"},
    ],
    "vertical": "entertainment",
    "tags": ["Netflix", "Telugu cinema", "Tollywood", "OTT", "streaming", "Peddi", "Pawan Kalyan", "Nani"],
    "image_person": "Nani (actor)",
    "image_attribution": "Wikimedia Commons",
})


# ── Main execution ───────────────────────────────────────────────────────────
def main():
    published = 0
    
    for i, art in enumerate(articles, 1):
        print(f"\n{'='*60}")
        print(f"Article {i}: {art['headline'][:60]}...")
        print(f"{'='*60}")
        
        # 1. Source image
        person = art.get("image_person")
        img_url = None
        img_attr = art.get("image_attribution", "")
        
        if person:
            img_url = fetch_wikipedia_person_image(person)
            if not img_url:
                # Try alternate forms
                alt = person.split("(")[0].strip()
                if alt != person:
                    img_url = fetch_wikipedia_person_image(alt)
        
        if img_url:
            if validate_image(img_url):
                print(f"  ✓ Image validated: {img_url[:60]}...")
            else:
                print(f"  ✗ Image validation failed, trying Pexels fallback")
                img_url = fetch_pexels_image(person.split("(")[0].strip() if person else art["slug"][:20])
                img_attr = "Pexels"
                if img_url and not validate_image(img_url):
                    img_url = None
                    img_attr = ""
        
        if not img_url:
            print(f"  ⚠ No valid image found, publishing without image")
        
        # 2. Build payload
        article_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()
        
        payload = {
            "id": article_id,
            "headline": art["headline"],
            "subheadline": art["subheadline"],
            "slug": art["slug"],
            "category": art["category"],
            "vertical": art.get("vertical", art["category"]),
            "body": art["body"].strip(),
            "sources": art["sources"],
            "tags": art.get("tags", []),
            "status": "published",
            "published_at": now_iso,
            "created_at": now_iso,
            "image_url": img_url or None,
            "image_caption": f"Photo: {img_attr}" if img_url else None,
            "image_attribution": img_attr if img_url else None,
        }
        
        # 3. Insert into Supabase
        result = sb_insert("p2_articles", payload)
        if result:
            aid = result.get("id", article_id)
            print(f"  ✓ Published: {art['slug']}")
            print(f"    ID: {aid}")
            print(f"    Category: {art['category']}")
            print(f"    Image: {'Yes' if img_url else 'No'}")
            published += 1
        else:
            print(f"  ✗ Failed to publish: {art['slug']}")
        
        time.sleep(1)  # Brief pause between inserts
    
    print(f"\n{'='*60}")
    print(f"DONE: {published}/{len(articles)} articles published")
    print(f"{'='*60}")
    return 0 if published == len(articles) else 1


if __name__ == "__main__":
    sys.exit(main())
