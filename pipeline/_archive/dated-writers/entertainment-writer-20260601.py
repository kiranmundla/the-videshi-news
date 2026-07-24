#!/usr/bin/env python3
"""Entertainment writer for The Videshi - June 1, 2026 evening run"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import requests
from datetime import datetime, timezone

# Load env
env_path = os.path.expanduser("~/workspace/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k] = v

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


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


def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels as fallback. Returns URL or None."""
    api_key = os.environ.get("PEXELS_API_KEY", "")
    if not api_key:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                [
                    "curl",
                    "-sS",
                    f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3",
                    "-H",
                    f"Authorization: {api_key}",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image for '{q}': {url[:60]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image_url(url):
    """Validate image URL returns HTTP 200 with image content."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True, headers={
            "User-Agent": "TheVideshi/1.0 (thevideshi.com)"
        })
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_length} bytes, {content_type}")
            return True
        # Try GET if HEAD fails
        r2 = requests.get(url, timeout=10, stream=True, headers={
            "User-Agent": "TheVideshi/1.0 (thevideshi.com)"
        })
        ct2 = r2.headers.get("Content-Type", "")
        cl2 = int(r2.headers.get("Content-Length", 0))
        if r2.status_code == 200 and "image" in ct2 and cl2 > 5000:
            print(f"  ✓ Image validated (GET): {cl2} bytes, {ct2}")
            return True
        print(f"  ✗ Image validation failed: status={r2.status_code}, type={ct2}, size={cl2}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def sb_insert(table, payload):
    """Insert row into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS, json=payload)
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            return data[0]
        return data
    print(f"  ✗ Insert error: {r.status_code} {r.text[:200]}")
    return None


def sb_patch(table, filters, payload):
    """Patch row in Supabase."""
    filter_str = "&".join(f"{k}={v}" for k, v in filters.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filter_str}"
    r = requests.patch(url, headers=HEADERS, json=payload)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch error: {r.status_code} {r.text[:200]}")
    return False


# ── ARTICLES ──

articles = []

# ═══════════════════════════════════════════════════════════════
# ARTICLE 1: Ranveer Singh Don 3 FWICE Controversy
# ═══════════════════════════════════════════════════════════════

articles.append({
    "headline": "Ranveer Singh Has Been Shadow-Banned by Bollywood's Biggest Union. The Don 3 Fallout Is Getting Ugly.",
    "subheadline": "FWICE issued a non-cooperation directive after the actor walked out of Farhan Akhtar's franchise reboot. Ram Gopal Varma says ban the union, not the actor. Salman Khan is mediating. The diaspora is watching a power struggle play out in real time.",
    "slug": "ranveer-singh-don-3-fwice-shadow-ban-bollywood-union-nri-20260601",
    "category": "entertainment",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        "Bollywood Hungama",
        "Devdiscourse",
        "Zoom TV Entertainment",
        "Pinkvilla",
        "Indulge Express"
    ]),
    "body": """The Federation of Western India Cine Employees (FWICE) — the union that claims to represent over five lakh workers across the Indian film industry — has issued a non-cooperation directive against Ranveer Singh. The directive effectively shadow-bans the actor, advising the entire industry to refrain from collaborating with him until he resolves his dispute with Excel Entertainment over the shelved *Don 3*.

It is one of the most significant industry interventions in recent Bollywood memory. And it is dividing the film fraternity right down the middle.

## How It Started

The trouble traces back to late 2025, when reports first surfaced that Ranveer Singh had exited *Don 3* — the long-awaited reboot of the franchise that Farhan Akhtar and Ritesh Sidhwani's Excel Entertainment had been developing for years. The original *Don* (2006) and *Don 2* (2011), both starring Shah Rukh Khan, were box office successes. A third instalment with Ranveer was meant to relaunch the franchise for a new generation.

But creative differences derailed the project. Ranveer reportedly wanted the Don character portrayed with more sinister, darker overtones. Farhan Akhtar insisted on keeping things consistent with the franchise's established tone. After nearly two years of back-and-forth, the actor walked out — just three weeks before the scheduled shoot.

Excel Entertainment claims the departure caused losses of approximately ₹45 crore (roughly $5.4 million), covering pre-production work, location scouting, costume design, and other development expenses. The production house lodged a formal complaint with the Indian Film & Television Directors' Association, which referred the matter to FWICE.

## FWICE Steps In

FWICE sent three separate notices to Ranveer Singh's team, asking the actor to appear before the federation and present his side. His legal team responded by questioning FWICE's jurisdiction over what they described as a private commercial agreement between two parties.

That response was perceived as a snub. FWICE's chief adviser Ashoke Pandit clarified that the directive was technically a "non-cooperation measure" rather than an outright ban, but the distinction felt academic. The practical effect is the same: the union has advised its vast membership — technicians, spot boys, makeup artists, assistant directors, the daily-wage workers who form the backbone of every film set — to avoid working with Ranveer Singh.

For NRI audiences who follow the Indian film industry from abroad, the move raises uncomfortable questions about how disputes between millionaire actors and production houses end up affecting the livelihoods of the industry's most vulnerable workers.

## Settlement Talks and Salman Khan's Mediation

Behind the scenes, efforts to defuse the crisis have been underway. Ranveer's team reportedly offered a settlement worth ₹35 crore, structured as a ₹10 crore upfront payment plus a ₹25 crore discount on a future project. Farhan and Ritesh rejected the offer and maintained their demand of ₹45 crore in full compensation.

Enter Salman Khan. The actor, who shares a cordial relationship with both Ranveer and Farhan, stepped in as an informal mediator. His advice, according to multiple reports: sort it out between yourselves without dragging in unions or courts. Both sides are believed to be following his counsel, though Farhan and Ritesh have insisted that any future settlement discussions must happen with them personally present — no proxies, no intermediaries.

## Ram Gopal Varma Goes to War

The controversy took a new turn when filmmaker Ram Gopal Varma weighed in with a blistering critique of FWICE. In a long post on X (formerly Twitter), Varma wrote: "BAN 'FWICE' and not @RanveerOfficial."

Varma called the federation a "kangaroo court" and described the non-cooperation directive as "a massive PR disaster" for the union itself. His argument was blunt: the dispute is a private contractual matter between a production house and an actor, the kind of thing that happens "in millions of cases all the time and all over India in all businesses." FWICE, he argued, is "neither a court of legal justice nor a government-authorised regulatory body."

He went further, questioning the federation's claim to represent five lakh workers. "The brutal truth is that most of those lakhs don't even know the internal facts of the two parties' dispute," he wrote, calling the ban "pure performative muscle flexing by an extremely outdated union system desperately trying to hold on to their grip."

## The Precedent Question

FWICE's position, however, has its own logic. If a major star can exit a project three weeks before shooting begins, cause crores in losses, and then refuse to even engage with the industry's dispute resolution mechanisms, what deterrent exists for future producers? That question has genuine weight, particularly for the smaller producers who cannot absorb tens of crores in sunk costs.

The federation's argument is less about Ranveer Singh the individual and more about maintaining a system where commitments carry consequences. Without some enforcement mechanism, producers face asymmetric risk every time they invest heavily in a star-driven project.

## What It Means for the Diaspora

For NRI audiences in the US, UK, Canada, and the Gulf, the Don 3 saga is more than industry gossip. Ranveer Singh is one of the most visible Indian stars in global markets. His *Dhurandhar* franchise has been a massive international hit — the sequel is currently dominating Netflix charts in multiple countries. His presence (or absence) in upcoming projects directly affects what Indian cinema looks like on screens outside India.

The FWICE directive, if it holds, could delay or derail multiple projects that diaspora audiences are looking forward to. Ranveer's *Pralay*, reportedly set to begin shooting in August 2026, could face logistical complications if the non-cooperation measure isn't resolved. The actor's legal team has the option of challenging the directive in court, but that would mean a prolonged public battle that benefits no one.

The resolution, when it comes, will likely happen in a quiet room rather than on social media. But the episode has already exposed the fault lines in Bollywood's power structure — the tensions between star power and institutional authority, between contractual obligations and creative freedom, between a union system built for a different era and an industry that has outgrown it.

For now, Ranveer Singh remains one of the biggest box office draws in Indian cinema. And one of its most controversial figures.""",
})

# ═══════════════════════════════════════════════════════════════
# ARTICLE 2: Netflix Tamil Original Series Slate
# ═══════════════════════════════════════════════════════════════

articles.append({
    "headline": "Netflix Just Unveiled a Tamil Original Slate. R. Madhavan Is Leading a Crime Saga. The Diaspora Should Pay Attention.",
    "subheadline": "Legacy, a family crime drama starring Madhavan and Nimisha Sajayan, headlines a new lineup of Tamil-language originals. Netflix is betting that hyperlocal South Indian stories can travel globally.",
    "slug": "netflix-tamil-original-series-slate-madhavan-legacy-nri-diaspora-20260601",
    "category": "entertainment",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        "Sacnilk",
        "Netflix India",
        "What's on Netflix",
        "Zoom TV Entertainment"
    ]),
    "body": """Netflix has formally announced a new slate of Tamil-language original series, marking what may be the streaming giant's most aggressive push into South Indian content to date. The lineup features a star-powered crime saga, a modern romantic comedy, and a psychological thriller — all commissioned as Netflix originals rather than post-theatrical acquisitions.

For the Tamil diaspora spread across the US, UK, Canada, Singapore, Malaysia, Australia, and the Gulf, the announcement carries particular significance. This is not Netflix licensing a theatrical hit after its cinema run. This is Netflix investing in Tamil-language storytelling from the ground up, betting that hyperlocal narratives from Chennai and Tamil Nadu can travel as effectively globally as Korean dramas or Spanish thrillers.

## Legacy: Madhavan Returns to Tamil

The most anticipated project is *Legacy*, a high-stakes family crime drama that represents one of the most impressive ensemble casts assembled for a Tamil streaming series. R. Madhavan — whose career has spanned three decades from *Alaipayuthey* and *Minnale* to the Hindi-language hits *3 Idiots*, *Tanu Weds Manu*, and *Rehnaa Hai Terre Dil Mein* — takes the lead.

Joining him are Nimisha Sajayan, the National Award-winning Malayalam actress making her Tamil streaming debut; Gautham Karthik, continuing his evolution beyond the legacy of his father Karthik; and Gulshan Devaiah in his Tamil debut. The series is produced by Stone Bench Pvt Ltd and directed by Charukesh Sekar.

The premise centers on an aging patriarch of a powerful crime family who must choose a successor to protect his empire from an inevitable siege. Netflix's official description promises a narrative exploring "power, morality, and familial betrayal" — themes that have driven some of the greatest crime sagas in global television, from *The Sopranos* to *Succession*.

For NRI Tamil audiences who grew up watching Madhavan transition from romantic hero to versatile actor, *Legacy* represents something new: a prestige Tamil-language series with global production values on the world's biggest streaming platform. The question is whether it will be the Tamil equivalent of *Sacred Games* — the show that proved Hindi-language original content could compete on an international stage.

## A Strategic Shift in Content

Netflix's Tamil push is not happening in isolation. The platform has simultaneously unveiled an expansive Telugu original slate featuring projects with Nani, Venkatesh, and Vijay Deverakonda. Taken together, these announcements represent a clear strategic pivot: Netflix is no longer treating South Indian content as a secondary market to be served with post-theatrical licensing deals. It is building original content pipelines for each major language.

The timing is deliberate. The South Indian film industry has been outperforming Bollywood at the box office with increasing regularity. Malayalam cinema has produced a string of globally successful films. Telugu cinema's reach in North America has grown exponentially — Ram Charan's *Peddi* is already at $700,000 in US advance bookings before its release. Tamil cinema, with global stars like Dhanush, Vijay, and Suriya, has one of the most passionate and geographically dispersed fan bases in the world.

For Netflix, the calculation is straightforward: South Indian audiences are among the most engaged streaming consumers globally, and they have been underserved by original content. JioHotstar and Amazon Prime Video have been competing aggressively for this audience; Netflix needed to respond with more than theatrical acquisitions.

## What Else Is in the Lineup

Beyond *Legacy*, the Tamil slate includes several other projects whose details are still emerging. A modern romantic comedy series is in development, reflecting Netflix's awareness that not all South Indian content needs to be high-stakes crime drama. A psychological thriller rounds out the confirmed genres, suggesting Netflix is building a diverse portfolio rather than betting everything on one tone.

The involvement of Stone Bench Pvt Ltd — the production company behind the recently streamed Tamil romantic drama *29* (directed by Rathna Kumar, which hit Netflix on June 5) — signals that Netflix is building ongoing relationships with Tamil production houses rather than treating each project as a one-off.

## The Diaspora Opportunity

For Tamil diaspora families in the US and Canada, streaming has become the primary way they consume Indian entertainment. The days of waiting months for a VHS or DVD to arrive from Chennai are long gone. But the content available on streaming platforms has not always reflected the depth and quality of Tamil storytelling.

What Netflix is offering is not just more Tamil content — it is Tamil content made with the production budgets, writing ambitions, and distribution reach that were previously reserved for Hindi-language shows. *Legacy*, with its crime-saga premise and star cast, is clearly positioned to compete not just with other Indian shows but with international prestige television.

The Tamil diaspora has been one of the most loyal communities on streaming platforms. They subscribe to multiple services to access content, often switching between Netflix, Amazon Prime, JioHotstar, and Zee5 depending on which platform has the latest theatrical release. Netflix's gamble is that by offering high-quality originals, it can become the default platform for Tamil-language entertainment abroad — not just a place to catch up on movies that already played in theatres.

## The Competition Responds

Netflix's move is expected to accelerate investment from rivals. JioHotstar, which already streams a significant portion of Tamil theatrical content, has been developing its own Tamil originals. Amazon Prime Video has had success with Tamil-language content and is likely to intensify its commissioning. The winners, ultimately, are the audiences — particularly the diaspora audiences who have been asking for prestige South Indian content on global platforms for years.

The release dates for most of the newly announced Tamil originals have not been disclosed. But with *Legacy* carrying the weight of Madhavan's star power and a crime-saga premise designed for global appeal, the series is likely to be Netflix's highest-profile Tamil launch to date.

For a diaspora that has watched Tamil cinema evolve from local industry to global cultural force, the message from Netflix is clear: Tamil stories are no longer regional content. They are global entertainment.""",
})


# ── PROCESS ARTICLES ──

for i, article in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"ARTICLE {i+1}: {article['headline'][:60]}...")
    print(f"{'='*60}")

    # Image sourcing
    img_url = None
    img_attribution = None

    if i == 0:  # Ranveer Singh
        img_url = fetch_wikipedia_person_image("Ranveer Singh")
        img_attribution = "Wikimedia Commons"
        if not img_url:
            img_url = fetch_pexels_image("Bollywood film industry", "Indian cinema studio")
            img_attribution = "The Videshi"

    elif i == 1:  # Netflix Tamil / Madhavan
        img_url = fetch_wikipedia_person_image("R. Madhavan")
        img_attribution = "Wikimedia Commons"
        if not img_url:
            img_url = fetch_wikipedia_person_image("Madhavan (actor)")
            img_attribution = "Wikimedia Commons"
        if not img_url:
            img_url = fetch_pexels_image("streaming service television", "digital entertainment")
            img_attribution = "The Videshi"

    # Validate image
    if img_url and not validate_image_url(img_url):
        print(f"  ⚠ Image failed validation, trying fallback...")
        img_url = fetch_pexels_image("Indian cinema", "Bollywood")
        img_attribution = "The Videshi"
        if img_url and not validate_image_url(img_url):
            img_url = None

    if img_url:
        article["image_url"] = img_url
        article["image_attribution"] = img_attribution
        print(f"  ✓ Final image: {img_url[:80]}...")
    else:
        print(f"  ✗ No valid image found")

    # Insert article
    result = sb_insert("p2_articles", article)
    if result:
        art_id = result.get("id")
        print(f"  ✓ Published: {article['slug']} (id: {art_id})")
    else:
        print(f"  ✗ Failed to publish: {article['slug']}")

    time.sleep(1)

print("\n✅ Entertainment writer complete!")
