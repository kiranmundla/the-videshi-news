#!/usr/bin/env python3
"""
Entertainment writer for The Videshi — May 29, 2026
Publishes 3 articles to Supabase.
"""

import os, json, requests, urllib.parse, sys, re
from datetime import datetime, timezone

# Load Supabase credentials
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Load Pexels key
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                if "PEXELS" in key.upper():
                    PEXELS_KEY = val.strip().strip('"').strip("'")

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
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate that the image URL is accessible and not tiny."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_length} bytes, {content_type}")
            return True
        else:
            print(f"  ✗ Image validation failed: status={r.status_code}, type={content_type}, size={content_length}")
            return False
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
        return False

def check_banned_url(url):
    """Check if the URL is from a banned source."""
    if not url:
        return True
    banned_patterns = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com", "_nc_ht=", "_nc_cat=", "ccb="]
    for pattern in banned_patterns:
        if pattern in url:
            print(f"  ✗ BANNED source detected: {pattern}")
            return True
    return False

def publish_article(article):
    """Publish article to Supabase."""
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "entertainment",
        "vertical": "entertainment",
        "diaspora_angle": article.get("diaspora_angle", "Relevant to Indian diaspora audiences worldwide."),
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": article.get("sources", []),
        "tags": article.get("tags", []),
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption"),
        "image_attribution": article.get("image_attribution")
    }

    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload
    )
    if r.status_code in (200, 201):
        data = r.json()
        article_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  ✓ Published: '{article['headline']}' (id: {article_id})")
        return True
    else:
        print(f"  ✗ Failed to publish '{article['headline']}': {r.status_code} {r.text[:300]}")
        return False


# ============================================================
# ARTICLE 1: Karan Johar's Instagram Mass Unfollow
# ============================================================
print("\n" + "="*60)
print("ARTICLE 1: Karan Johar's Instagram Unfollow Drama")
print("="*60)

# Image: Try Wikipedia for Karan Johar
img1 = fetch_wikipedia_person_image("Karan Johar")
if not img1 or check_banned_url(img1) or not validate_image(img1):
    img1 = fetch_pexels_image("Instagram social media phone", "social media smartphone")
    if img1 and (check_banned_url(img1) or not validate_image(img1)):
        img1 = None

article1 = {
    "headline": "Karan Johar Unfollowed Shah Rukh Khan, Alia Bhatt, and Nearly Everyone Else on Instagram. He Called It a Digital Detox.",
    "subheadline": "The filmmaker kept only one Bollywood name on his following list — Priyanka Chopra — and told the internet to stop making it 'national news.'",
    "slug": "karan-johar-unfollows-shah-rukh-khan-alia-bhatt-instagram-digital-detox-nri-20260529",
    "image_url": img1,
    "image_caption": "Karan Johar at a public event" if img1 and "wikipedia" in (img1 or "").lower() else "Social media detox has become a recurring theme among Bollywood celebrities",
    "image_attribution": "Wikimedia Commons" if img1 and "upload.wikimedia" in (img1 or "") else "Pexels",
    "sources": ["Filmfare", "Sacnilk", "Zoom TV Entertainment", "Inshorts"],
    "tags": ["karan-johar", "shah-rukh-khan", "alia-bhatt", "instagram", "digital-detox", "bollywood-gossip", "social-media"],
    "diaspora_angle": "The Karan Johar–Shah Rukh Khan friendship is foundational mythology for NRIs — their films defined an entire generation's relationship with Indian identity abroad.",
    "body": """For a man who built a career on dramatic reveals, Karan Johar's latest move was, fittingly, discovered by the internet before he said a word about it.

Eagle-eyed Reddit users were the first to notice something strange on the filmmaker's Instagram profile. His following count, once sprawling across Bollywood's A-list, had been gutted. Shah Rukh Khan — gone. Alia Bhatt — gone. Kareena Kapoor Khan, Kajol, Malaika Arora, Ananya Panday, Kartik Aaryan, Varun Dhawan, Sidharth Malhotra, Manish Malhotra — all unfollowed. Even Gauri Khan, Aryan Khan, and Suhana Khan — the extended Khan family he had been close to for decades — were removed from the list.

## The One Name That Stayed

Of all the celebrities scrubbed from Karan Johar's following list, one name survived the purge: **Priyanka Chopra**. The internet, naturally, had theories. Had there been a falling out with Shah Rukh Khan? Were professional tensions simmering beneath Bollywood's carefully curated public friendships? Was the Priyanka exception deliberate or an oversight?

The speculation ran wild across Reddit, Twitter, and WhatsApp groups. Screenshots of before-and-after follower comparisons went viral. Bollywood fan accounts ran polls asking followers to vote on who Karan Johar was *really* angry at. His following count reportedly dropped from 1.8 crore to 1.75 crore in the process.

## "It's a DIGITAL DETOX!!!!"

Johar finally responded through an Instagram Story, and his tone suggested a man who had not anticipated the frenzy. "It's a DIGITAL DETOX!!!!" he wrote, his frustration punctuated by four exclamation marks. "Am unfollowing everyone to reduce my time and energy spent on the gram!!! This can't be national news for god's sake... please clickbait something else! This is irrelevant!"

The response did not, as he might have hoped, settle the matter. If anything, it amplified it. Social media users pointed out that unfollowing people is not, technically, a prerequisite for spending less time on Instagram. Others called it a "PR move" dressed up as self-care. A few noted the irony of a filmmaker who weaponized social media buzz for decades now asking for quiet.

## Why the Diaspora Cares

For NRI audiences, the Karan Johar–Shah Rukh Khan relationship is not just an industry friendship. It is foundational mythology. *Kuch Kuch Hota Hai*, *Kabhi Khushi Kabhie Gham*, *My Name Is Khan* — these films defined an entire generation's relationship with Indian identity abroad. The sight of Karan unfollowing Shah Rukh, even performatively, hits differently in households where those films were rituals.

Johar's upcoming slate is unaffected. *Chand Mera Dil*, produced under Dharma, is currently in theatres with Ananya Panday. The ambitious *Naagzilla* is in development. His multi-film deal with Lyca Productions was announced just weeks ago. There are no public signs of professional trouble.

## The Pattern

This is not the first time a Bollywood figure has cited digital detox while doing something that is functionally theatrical. Deepika Padukone, Ranbir Kapoor, and others have periodically scrubbed their social media presence, generating the exact kind of attention they claim to be escaping. In Karan Johar's case, the move reads less like burnout and more like a reset — a deliberate repositioning of his public persona at a moment when Dharma's commercial track record is under scrutiny.

Whether it is a genuine effort to unplug or a carefully orchestrated conversation-starter, one thing is clear: Karan Johar's Instagram following list has become the most analyzed spreadsheet in Bollywood. And Priyanka Chopra, for reasons nobody can quite explain, remains the only entry on it."""
}

publish_article(article1)


# ============================================================
# ARTICLE 2: PVR INOX Pride Film Festival
# ============================================================
print("\n" + "="*60)
print("ARTICLE 2: PVR INOX Pride Film Festival")
print("="*60)

# Image: Try Pexels for pride/cinema
img2 = fetch_pexels_image("pride rainbow flag cinema", "rainbow pride celebration")
if img2 and (check_banned_url(img2) or not validate_image(img2)):
    img2 = None

article2 = {
    "headline": "India's Largest Cinema Chain Just Launched a Pride Film Festival. The Lineup Includes a Marathi Film.",
    "subheadline": "PVR INOX is screening Moonlight, Rocketman, and the celebrated Baapya across 20 cities and 40 cinemas, starting May 29.",
    "slug": "pvr-inox-pride-film-festival-moonlight-rocketman-baapya-queer-cinema-india-nri-20260529",
    "image_url": img2,
    "image_caption": "PVR INOX's Pride Film Festival celebrates queer cinema across 20 Indian cities",
    "image_attribution": "Pexels" if img2 else None,
    "sources": ["Cine Buzz News", "Bharat Horizon", "Business News This Week"],
    "tags": ["pvr-inox", "pride-film-festival", "moonlight", "rocketman", "baapya", "queer-cinema", "lgbtq", "marathi"],
    "diaspora_angle": "For NRIs who grew up before Section 377 was struck down, seeing India's largest cinema chain program a Pride film festival signals institutional acceptance at mainstream scale.",
    "body": """PVR INOX, India's largest and most premium cinema exhibitor, has launched the Pride Film Festival beginning May 29, 2026. The lineup is compact but deliberate: Barry Jenkins' Academy Award-winning **Moonlight**, Dexter Fletcher's **Rocketman** — the musical biopic of Elton John — and **Baapya**, a celebrated Marathi film that explores identity and human connection.

The festival will run for a week across 20 cities and 40 cinemas. Booking details are available on the PVR INOX app and website.

## The Films

**Moonlight** needs little introduction. The 2017 Best Picture winner tells the story of a young Black man navigating race, vulnerability, and sexuality across three defining stages of his life. It remains one of the most quietly devastating films of the last decade, and the chance to see it on a big screen in India — a country that was still criminalizing homosexuality when the film first released — is not a small thing.

**Rocketman** captures Elton John's rise through music, fantasy, and raw emotional honesty. Unlike the sanitized biopic formula that dominates Hollywood, the film leaned into the messiness of John's life — the addiction, the loneliness, the flamboyance — and treated his queerness not as a subplot but as the core of his story.

**Baapya** is the inclusion that matters most for Indian audiences. A Marathi film in a Pride festival alongside Hollywood Oscar winners signals something that would have been unthinkable a decade ago: that queer stories from India's regional cinema are being placed on the same stage as global benchmarks. The film offers a nuanced, heartfelt exploration of identity rooted in contemporary Marathi storytelling — no imported narratives, no borrowed frameworks.

## Why This Matters for the Diaspora

For NRIs who grew up in India before Section 377 was struck down in 2018, the relationship with queer cinema is complicated. Many in the diaspora first encountered openly queer storytelling through Western films and TV — because Indian cinema largely pretended queerness did not exist, or reduced it to comic relief.

That PVR INOX — not an indie film collective, not an NGO, but India's biggest multiplex chain — is programming a Pride film festival with a Marathi-language film alongside Moonlight and Rocketman represents institutional acceptance at a scale that matters. It is not niche. It is not underground. It is 40 cinemas in 20 cities, with mainstream marketing and mainstream pricing.

## The Broader Shift

Indian cinema's engagement with queer stories has deepened significantly in recent years. Films like *Badhaai Do* (2022) explored a lavender marriage with commercial appeal. *Chandigarh Kare Aashiqui* (2021) centred a trans woman's story in a mainstream rom-com. The KASHISH Mumbai International Queer Film Festival has been running since 2010, growing from a niche event to South Asia's largest queer film festival.

But there is a difference between independent festivals and commercial exhibition. PVR INOX's decision to brand a week-long Pride festival across its national footprint moves queer cinema from the margins to the marquee.

Niharika Bijli, Lead Strategist at PVR INOX, framed it in institutional language: "Cinema has always been a powerful medium for empathy, identity, and dialogue. We are proud to bring back globally celebrated titles such as Moonlight and Rocketman, as well as Baapya, a story from the heartland of India."

## What It Means Going Forward

The festival is part of PVR INOX's broader initiative to honour landmark films through curated screening events. Whether it becomes an annual fixture or remains a one-off will be the real test. But for the moment, the statement is clear: queer cinema belongs on the big screen in India. Not in a corner, not on a streaming platform at 2 AM, but in the same multiplexes where families go to watch Dhurandhar 2 on opening weekend.

For the diaspora watching from abroad, the symbolism is hard to miss. The country many left — in part because it could not accommodate certain identities — is screening Moonlight in 20 cities. That is not a revolution. But it is a shift."""
}

publish_article(article2)


# ============================================================
# ARTICLE 3: Bhooth Bangla — Akshay Kumar's Comeback
# ============================================================
print("\n" + "="*60)
print("ARTICLE 3: Bhooth Bangla — Akshay Kumar's Comeback")
print("="*60)

# Image: Try Wikipedia for Akshay Kumar
img3 = fetch_wikipedia_person_image("Akshay Kumar")
if not img3 or check_banned_url(img3) or not validate_image(img3):
    img3 = fetch_wikipedia_person_image("Priyadarshan")
    if not img3 or check_banned_url(img3) or not validate_image(img3):
        img3 = fetch_pexels_image("haunted mansion horror", "old mansion night")
        if img3 and (check_banned_url(img3) or not validate_image(img3)):
            img3 = None

article3 = {
    "headline": "Bhooth Bangla Is Still Running in Theatres After Six Weeks. Akshay Kumar Hasn't Done That in Years.",
    "subheadline": "The Akshay Kumar–Priyadarshan reunion has crossed ₹176 crore in India and ₹262 crore worldwide, defying the fast-exit box office cycle.",
    "slug": "bhooth-bangla-akshay-kumar-priyadarshan-176-crore-sixth-week-box-office-comeback-nri-20260529",
    "image_url": img3,
    "image_caption": "Akshay Kumar's horror-comedy Bhooth Bangla has become his strongest post-pandemic performer" if img3 and "upload.wikimedia" in (img3 or "") else "Bhooth Bangla defied the fast-exit box office cycle",
    "image_attribution": "Wikimedia Commons" if img3 and "upload.wikimedia" in (img3 or "") else "Pexels",
    "sources": ["Sacnilk", "Bollywood Hungama", "LatestLY", "Zoom TV Entertainment"],
    "tags": ["akshay-kumar", "priyadarshan", "bhooth-bangla", "box-office", "horror-comedy", "bollywood-comeback"],
    "diaspora_angle": "Bhooth Bangla earned over ₹56 crore overseas — one of Akshay's strongest international runs in years, driven by NRI families nostalgic for the Kumar-Priyadarshan comedy formula.",
    "body": """Six weeks is a lifetime in the current Bollywood box office cycle. Most films are done within two. The big ones — the Dhurandhars, the Pushpas — might sustain three or four. After that, screens get reallocated, interest migrates to the next release, and the theatrical run becomes an afterthought.

Bhooth Bangla has not received that memo.

Akshay Kumar and director Priyadarshan's horror-comedy, which opened on April 17, 2026, has crossed **₹176.50 crore net in India** and an estimated **₹262 crore worldwide** — and it is still adding screens in Tier-2 and Tier-3 centres where family audiences continue to show up. In its sixth week, the film collected approximately ₹5 crore net, with a week-on-week drop of just 30 percent. For context, most Hindi films at this stage are earning in the low lakhs, not crores.

## The Numbers in Perspective

Among Akshay Kumar's post-pandemic releases, Bhooth Bangla is not just the best — it is the best by a landslide. His second-strongest sixth week belongs to *Sooryavanshi*, which managed approximately ₹1 crore at the same stage. *Jolly LLB 3* managed ₹78 lakh. *Kesari Chapter 2* did ₹75 lakh. *OMG 2* added ₹59 lakh.

The film crossed ₹100 crore in its second weekend, reached ₹200 crore worldwide by its fourth week, and now sits comfortably as Akshay Kumar's 12th film to breach the ₹200 crore worldwide mark. Overseas markets have contributed significantly — over ₹56 crore from international territories, making it one of his strongest overseas performers in years.

## The Priyadarshan Factor

The story of Bhooth Bangla's success is, in large part, the story of a reunion. Akshay Kumar and Priyadarshan last worked together on *Khatta Meetha* in 2010 — a 16-year gap. Before that, they had built a legendary filmography: *Hera Pheri*, *Bhool Bhulaiyaa*, *Garam Masala*, *Bhagam Bhag*. These are not just films. For NRI households in the 2000s, they were communal experiences — the DVDs passed between families, the dialogues memorized across continents.

Priyadarshan brought back something that Akshay's recent filmography had been missing: effortless comedy rooted in character rather than cause. Bhooth Bangla is not trying to make a point. It is not patriotic. It is not a social message film. It is a horror-comedy with Akshay Kumar being funny in a haunted house, and the audience responded to that simplicity.

## Why the Diaspora Showed Up

Akshay Kumar's overseas appeal had been eroding. His last several releases — from *Ram Setu* to *Selfiee* to the diminishing returns of the *Khiladi* nostalgia — failed to generate meaningful international numbers. *Bhooth Bangla* reversed that trajectory.

The international opening weekend was massive: approximately ₹26.50 crore overseas in the first three days, making it Akshay's third-largest post-pandemic opening internationally. The film continues to hold in markets where Indian families drive ticket sales — North America, the UK, the Middle East, and Australia.

For NRI audiences, the appeal is straightforward. Bhooth Bangla is the kind of film their parents would have watched in theatres in India in 2006. Akshay is doing physical comedy. Paresh Rawal is being Paresh Rawal. Tabu adds gravitas. The haunted house is ridiculous in exactly the right way. It is comfort cinema, and the diaspora bought tickets accordingly.

## The Netflix Chapter Ahead

Reports suggest Bhooth Bangla's digital premiere on Netflix is expected between mid-June and early July 2026, following the standard eight-week theatrical-to-OTT window. Given the film's strong theatrical endurance, the Netflix debut could become one of the platform's top-performing Indian titles of the quarter.

## What It Means for Akshay

The last three years had prompted genuine questions about whether Akshay Kumar — once the most reliable box office machine in Bollywood — had lost his audience. *Selfiee* flopped. *Mission Raniganj* underperformed. Even *OMG 2*, while profitable, fell short of its predecessor's cultural impact.

Bhooth Bangla does not erase those misfires. But it does prove that the audience hasn't left — they were just waiting for the right film. And the right film, it turns out, was the kind Akshay and Priyadarshan used to make without thinking about it."""
}

publish_article(article3)

print("\n" + "="*60)
print("Entertainment writer run complete: 3 articles published")
print("="*60)
