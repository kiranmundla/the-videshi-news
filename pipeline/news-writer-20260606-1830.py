#!/usr/bin/env python3
"""
News writer - 2026-06-06 18:30 UTC run
Writes 3 articles: Republican revolt, NY Senate India resolution, Georgia Indian American wins
"""

import os, json, requests, urllib.parse, subprocess, sys, re
from datetime import datetime, timezone

# Load env
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, val = line.split('=', 1)
            os.environ[key.strip()] = val.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# Load Pexels key
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                if 'PEXELS' in key.upper():
                    PEXELS_KEY = val.strip().strip('"').strip("'")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
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


def fetch_wikimedia_commons(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for page_id, page in pages.items():
                info = page.get("imageinfo", [{}])[0]
                url = info.get("thumburl") or info.get("url")
                mime = info.get("mime", "")
                width = info.get("width", 0)
                if url and "image" in mime and width >= 200:
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": width,
                        "height": info.get("height", 0)
                    })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} results for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for an image using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0]["src"]["large2x"]
            print(f"  ✓ Pexels image for '{query}': {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def validate_image(url):
    """Check image URL returns 200 and content > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD didn't return content-length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except:
        pass
    return False


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Inserted: {result[0].get('headline', 'unknown')}")
            return True
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
    return False


# ============================================================
# ARTICLE 1: Republican revolt against Trump
# ============================================================
print("\n=== ARTICLE 1: Republican revolt against Trump ===")

# Image: US Capitol / Congress
img1 = None
img1_caption = ""
img1_attribution = ""

# Try Wikimedia Commons for US Capitol
commons = fetch_wikimedia_commons("United States Capitol building Congress", limit=5)
for c in commons:
    title_lower = c["title"].lower()
    if "capitol" in title_lower and c["width"] >= 600:
        if validate_image(c["url"]):
            img1 = c["url"]
            img1_caption = "The United States Capitol building in Washington, DC"
            img1_attribution = "Wikimedia Commons"
            print(f"  ✓ Using Commons Capitol image")
            break

if not img1:
    # Pexels fallback
    img1 = fetch_pexels_image("US Capitol building Washington DC")
    if img1 and validate_image(img1):
        img1_caption = "The United States Capitol building in Washington, DC"
        img1_attribution = "Pexels"
    else:
        img1 = None

article1 = {
    "headline": "Trump's Own Party Just Voted to End His War and Fund Ukraine. The Cracks Are Widening.",
    "subheadline": "In a single week, House Republicans defied the president on Iran, Ukraine, his ballroom, and a $1.8 billion settlement fund. For Indian Americans watching immigration and trade policy, the intra-party revolt may reshape what gets done before November.",
    "slug": "republican-revolt-trump-iran-ukraine-midterms-diaspora-june-2026",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img1,
    "image_caption": img1_caption,
    "image_attribution": img1_attribution,
    "sources": json.dumps(["Reuters", "CNN", "USA Today", "Washington Examiner"]),
    "body": """Donald Trump remains the undisputed leader of the Republican Party. But this week, his grip on Capitol Hill loosened in ways that would have been unthinkable six months ago — and the consequences ripple directly into the lives of Indian Americans navigating immigration backlogs, trade uncertainty, and rising fuel costs.

In the span of four days, House Republicans crossed party lines to pass the Ukraine Support Act with $1.3 billion in aid and new Russia sanctions (226–195, with 18 Republicans defying leadership). A day earlier, the House voted for the first time to invoke war powers against Trump's Iran campaign, with four GOP members joining every Democrat. In the Senate, more than a dozen Republicans took symbolic votes against the president's $1.8 billion "anti-weaponisation" settlement fund, his planned White House ballroom, and the nomination of MAGA loyalist Bill Pulte to lead the intelligence community.

## Not the Usual Suspects

What makes this week different is who is breaking ranks. Senators Dan Sullivan of Alaska and Jon Husted of Ohio — both facing competitive re-election races in November — voted to kill the settlement fund. Ashley Moody of Florida voted to bar taxpayer-funded settlements for January 6 rioters. Jerry Moran of Kansas voted to block the ballroom. These are not the "YOLO senators" (John Cornyn, Bill Cassidy, Thom Tillis) whose re-election bids Trump personally torpedoed. These are lawmakers doing the electoral maths five months out.

In the House, Rep. Tom Barrett — one of the GOP's most endangered incumbents — voted to limit Trump's Iran war powers. Former committee chairs Michael McCaul, Mike Turner, Glenn Thompson, and Andrew Garbarino all defied the president on Ukraine policy.

"I fill up my gas tank too. I have four kids," Barrett told CNN. "I see it as well."

## Why It Matters for Indian Americans

The Republican fracture is not abstract for the diaspora. Three policy fronts are directly at stake.

**Immigration enforcement.** The $70 billion ICE and CBP funding bill — the vehicle for most of this week's drama — is expected to pass next week. But the fight over the settlement fund exposed deep disagreement about how immigration enforcement dollars should be spent. For H-1B holders, green card applicants, and OPT participants already facing a hostile regulatory environment, the internal chaos means less bandwidth for the streamlining reforms the tech industry has lobbied for.

**The Iran war and oil prices.** The war powers votes, though largely symbolic, signal that Congress is losing patience with an open-ended conflict. For Indian Americans, the Iran war is not just geopolitics — it is the reason gas prices have climbed past $5 in parts of California and why India's crude oil import bill has ballooned. India imports roughly 85 per cent of its oil, and Hormuz disruptions have already forced New Delhi to pivot sourcing to Venezuela and West Africa.

**The India-US trade deal.** With the first tranche of the bilateral trade agreement expected by mid-July, any legislative paralysis in Washington could slow the ratification process. Trade Minister Piyush Goyal said both sides are "fast moving towards closing all the open ends," but a Congress consumed by internal warfare is a Congress that does not prioritise trade deals.

## The Midterm Calculus

Trump has shown no sign of retreat. He called retiring Senator Thom Tillis "a loser" after Tillis threatened to oppose his next attorney general pick. He dismissed the war powers vote as "meaningless." His next flashpoint — the expected nomination of personal attorney Todd Blanche as permanent attorney general — is likely to trigger the sharpest confirmation fight of his second term.

But the numbers tell a story Trump may not want to hear. His approval ratings are sliding, and Senate Republicans are privately admitting that their majority is at risk for the first time since November 2024. "There's this realisation — if no one's looking out for me, I have to look out for myself," a senior GOP aide told CNN.

For Indian Americans watching from Silicon Valley, the Dallas suburbs, or the New Jersey corridor, the question is whether this Republican revolt produces legislative outcomes — or just noise. History suggests the latter. But with gas prices, immigration raids, and a war without a congressional mandate all colliding in an election year, this week felt different.

The cracks are real. Whether they widen into a fracture depends on what happens between now and November."""
}

# ============================================================
# ARTICLE 2: New York State Senate India Independence Day resolution
# ============================================================
print("\n=== ARTICLE 2: NY Senate India Independence Day resolution ===")

# Image: Try New York State Capitol or Albany legislature
img2 = None
img2_caption = ""
img2_attribution = ""

commons2 = fetch_wikimedia_commons("New York State Capitol Albany", limit=5)
for c in commons2:
    title_lower = c["title"].lower()
    if ("capitol" in title_lower or "albany" in title_lower) and c["width"] >= 400:
        if validate_image(c["url"]):
            img2 = c["url"]
            img2_caption = "The New York State Capitol building in Albany"
            img2_attribution = "Wikimedia Commons"
            print(f"  ✓ Using Commons NY Capitol image")
            break

if not img2:
    img2 = fetch_pexels_image("New York state capitol building Albany")
    if img2 and validate_image(img2):
        img2_caption = "The New York State Capitol building in Albany"
        img2_attribution = "Pexels"
    else:
        img2 = None

article2 = {
    "headline": "New York's State Senate Just Voted to Make August 15 India Independence Day",
    "subheadline": "Resolution J1935 memorialises the Governor to proclaim India Independence Day in New York State — a recognition of the diaspora's political muscle in a state that is home to one of the largest Indian American communities in the Western Hemisphere.",
    "slug": "new-york-state-senate-india-independence-day-resolution-j1935-august-2026",
    "category": "nri-world",
    "vertical": "nri-world",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img2,
    "image_caption": img2_caption,
    "image_attribution": img2_attribution,
    "sources": json.dumps(["The Indian Eye", "New York State Senate", "Consulate General of India, New York"]),
    "body": """The New York State Senate has adopted Resolution J1935, memorialising the Governor to proclaim August 15, 2026, as India Independence Day in the State of New York. The resolution, sponsored by Senator Jeremy Cooney, passed with bipartisan support and was accompanied by a series of floor speeches that went well beyond ceremonial pleasantries.

Several senators spoke at length about India's civilisational heritage, its democratic traditions, and the contributions of the Indian American community to the state's economy, academia, and civic life. The remarks reflected something deeper than protocol — they reflected the growing political weight of a community that now numbers in the hundreds of thousands across the New York metropolitan area.

## What the Senators Said

Senator Jeremy Cooney, the resolution's sponsor, framed the occasion as both a celebration and an obligation. "Across the globe, Indians are making lasting impacts in their communities, and this is an opportunity to join together and celebrate and reflect on our shared history, culture, and heritage," he said.

Senator Joseph P. Addabbo Jr. invoked Mahatma Gandhi directly. "Gandhi once said that the future depends on what we do in the present. That message of Gandhi is inspiration even for Indian Americans today and for future generations too," he said.

But it was Senator John C. Liu who struck the most pointed note. "India has been around for thousands of years. It has been a civilisation. It has been a country. It has been a model of democracy for actually a lot longer than our country. But we celebrate the contributions of Indian Americans to our communities right here in New York and in the United States," he said.

## A Pattern of Recognition

The resolution follows a similar measure adopted last year for August 15, 2025, as well as a November 2025 resolution commemorating the 75th anniversary of the Indian Constitution — both sponsored by Senator Cooney. What was once a one-off ceremonial gesture appears to be hardening into an annual legislative tradition.

The Consulate General of India in New York expressed its gratitude to the Senate for the recognition, thanking the legislators for their "warm recognition of India's rich heritage and the invaluable contributions of the Indian-American community to New York."

## The Diaspora's Growing Political Weight

The resolution matters beyond its symbolic value because of what it represents about the Indian American community's political trajectory in New York.

The New York City metropolitan area is home to one of the largest Indian American populations in the Western Hemisphere. According to recent census data, Indian Americans in the region have higher overall incomes and educational attainment than most other demographic groups. They are concentrated heavily in Queens, but have expanded into Long Island, New Jersey, and the Hudson Valley.

That demographic footprint has translated into increasing political representation. New York is home to the first Indian American elected to the State Senate (Kevin Thomas), the first Indian Americans elected to the State Assembly (Jenifer Rajkumar and Zohran Mamdani), and, more recently, Mamdani's election as New York City Mayor — the first person of South Asian descent to hold the office.

The resolution also arrives at a moment when Indian Americans are navigating a complex political landscape. Hate crime incidents targeting Hindu temples in the Bay Area and elsewhere have put the community on edge. Immigration policy remains in flux. And the India-US bilateral relationship — from trade negotiations to defence cooperation — is more consequential than at any point in recent history.

## What Happens Next

The resolution memorialises the Governor to issue the proclamation — it does not compel it. But given the political dynamics and the precedent set last year, the proclamation is widely expected. Governor Hochul's office has not yet commented on the timeline.

For the estimated 300,000-plus Indian Americans in the New York metro area, the resolution is a milestone in a longer arc. Twenty years ago, such a legislative acknowledgement would have been difficult to imagine. Today, it is becoming routine — which may be the most significant thing about it.

August 15 will mark India's 79th year of independence. In Albany, it will also mark another year in which a legislative body formally acknowledged that the Indian diaspora is not a footnote in American political life, but a chapter."""
}

# ============================================================
# ARTICLE 3: Indian American political wins in Georgia
# ============================================================
print("\n=== ARTICLE 3: Georgia Indian American political wins ===")

# Image: Try Wikipedia for Georgia State Capitol or Nabilah Islam Parkes
img3 = None
img3_caption = ""
img3_attribution = ""

# Try Georgia State Capitol from Commons
commons3 = fetch_wikimedia_commons("Georgia State Capitol Atlanta", limit=5)
for c in commons3:
    title_lower = c["title"].lower()
    if ("georgia" in title_lower or "capitol" in title_lower or "atlanta" in title_lower) and c["width"] >= 400:
        if validate_image(c["url"]):
            img3 = c["url"]
            img3_caption = "The Georgia State Capitol in Atlanta"
            img3_attribution = "Wikimedia Commons"
            print(f"  ✓ Using Commons Georgia Capitol image")
            break

if not img3:
    # Try Nabilah Islam Parkes from Wikipedia
    img3 = fetch_wikipedia_person_image("Nabilah Islam")
    if img3 and validate_image(img3):
        img3_caption = "Nabilah Islam Parkes, advancing to a runoff for Georgia Lieutenant Governor"
        img3_attribution = "Wikimedia Commons"
    else:
        img3 = fetch_pexels_image("Georgia state capitol Atlanta government")
        if img3 and validate_image(img3):
            img3_caption = "Georgia's political landscape is being reshaped by South Asian American candidates"
            img3_attribution = "Pexels"
        else:
            img3 = None

article3 = {
    "headline": "Five South Asian Candidates Just Won or Advanced in Georgia. One Could Make History.",
    "subheadline": "Nabilah Islam Parkes is poised to become the first South Asian and Asian American lieutenant governor nominee in Georgia history. She is not alone — Jyot Singh is set to become the state's first Sikh elected official.",
    "slug": "indian-american-georgia-primary-wins-nabilah-parkes-jyot-singh-june-2026",
    "category": "nri-world",
    "vertical": "nri-world",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img3,
    "image_caption": img3_caption,
    "image_attribution": img3_attribution,
    "sources": json.dumps(["Indian American Impact", "The Indian Eye", "Georgia Secretary of State"]),
    "body": """Five South Asian American candidates endorsed by Indian American Impact either won their primaries outright or advanced to runoff elections in Georgia this week, marking what the organisation called a breakthrough moment for a community that has long been underrepresented in Southern state politics.

The headline result: Nabilah Islam Parkes advanced to a runoff in the race for lieutenant governor and is now poised to become the first South Asian and Asian American lieutenant governor nominee from either party in Georgia history.

But Parkes was not the only candidate to make the night historic. Jyot Singh secured an outright victory in State House District 97 and is on track to become the first Sikh elected official in Georgia's history.

## The Full Slate

Indian American Impact, the national political organisation that has endorsed and supported more than 200 South Asian American candidates since its founding in 2016, celebrated five results across the state:

**Advancing to runoffs:**
- **Nabilah Islam Parkes** — Lieutenant Governor. If she wins the runoff, she would be the first South Asian American to serve as a constitutional officer in Georgia.
- **Rahul Garabadu** — State Senate, District 7. Garabadu advanced in a competitive primary for a seat in the state's upper chamber.

**Outright victories:**
- **Jyot Singh** — State House, District 97. Singh's win makes him the presumptive first Sikh elected official in Georgia.
- **Saira Draper** — State Senate, District 44. Draper won a contested primary for a state senate seat.
- **Akbar Ali** — State House, District 106. Ali secured the Democratic nomination and will continue serving as the youngest state legislator in Georgia.

"Last night's results in Georgia speak to the growing political power and representation of our communities," said Chintan Patel, Executive Director of Indian American Impact.

## Why Georgia

Georgia is home to more than 600,000 Asian American residents, a population that has grown rapidly over the past two decades — driven in large part by the tech and healthcare sectors in the Atlanta metropolitan area. Indian Americans are the single largest Asian American subgroup in the state, concentrated in Gwinnett, Forsyth, and Fulton counties.

The community's political awakening has been building for years. In 2020, Georgia's Asian American vote was widely credited as a decisive factor in flipping the state for Joe Biden and electing two Democratic senators. Since then, Indian American candidates have begun competing not just for state legislature seats but for statewide office — a trajectory that mirrors patterns seen earlier in New Jersey, Illinois, and California.

What makes the Georgia results striking is the breadth of representation. The five winning or advancing candidates include a Bangladeshi American woman (Parkes), a Sikh man (Singh), and candidates of Indian, Pakistani, and mixed South Asian heritage — a diversity that reflects the actual composition of the diaspora rather than a monolithic "Indian American" label.

## The Road Ahead

For Parkes, the runoff will be the more difficult test. Lieutenant governor races in Georgia have historically attracted modest attention, but her candidacy — coming at a time when anti-Asian hate crimes and immigration enforcement are national flashpoints — is likely to draw significant outside attention and fundraising.

Singh's path is comparatively clearer. Having won his primary outright, he will face a general election in a district that favours Democrats. If he prevails in November, his swearing-in would add Georgia to the short list of states that have elected Sikh officials — a list that includes Connecticut, New Jersey, and Virginia.

## A National Pattern

The Georgia results are part of a broader wave. Indian American Impact has now marshalled upwards of $20 million in support of South Asian American candidates across the country. The organisation's strategy — identifying competitive races early, endorsing before primaries, and investing in grassroots organising — has produced a pipeline of candidates that extends well beyond the traditional coastal strongholds.

In 2026 alone, Indian American candidates are running for Congress, state legislatures, and local offices in more than a dozen states. The question is no longer whether the community will be represented in American politics, but how quickly that representation will scale.

For the five candidates in Georgia, the primary was the first test. The general election in November will be the real one. But the fact that five South Asian Americans are in position to win seats in a Southern state that was, until recently, considered out of reach for the community — that is the story that matters.

"We are thrilled to see so many South Asian leaders stepping into the halls of power," Patel said. "This is what building political power looks like." """
}

# ============================================================
# INSERT ALL ARTICLES
# ============================================================
print("\n=== Inserting articles ===")

for i, article in enumerate([article1, article2, article3], 1):
    if article["image_url"] is None:
        print(f"  ⚠ Article {i} has no image, skipping image fields")
        article.pop("image_url", None)
        article.pop("image_caption", None)
        article.pop("image_attribution", None)
    
    print(f"\n--- Article {i}: {article['headline'][:60]}... ---")
    print(f"  Category: {article['category']}, Vertical: {article['vertical']}")
    print(f"  Slug: {article['slug']}")
    if article.get("image_url"):
        print(f"  Image: {article['image_url'][:80]}...")
    
    success = insert_article(article)
    if not success:
        print(f"  ✗ FAILED to insert article {i}")

print("\n=== Done ===")
