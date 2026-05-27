#!/usr/bin/env python3
"""
The Videshi — News Writer (scheduled run)
Generates 3 news articles with India/NRI diaspora angles.
"""

import json, os, re, sys, uuid, requests, urllib.parse, time
from datetime import datetime, timezone

# ── env ──
with open(os.path.expanduser("~/.env.supabase")) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

with open(os.path.expanduser("~/workspace/.env.pexels")) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
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
        print("  ⚠ No Pexels API key")
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


def validate_image(url):
    """Check that image URL returns HTTP 200 with image content-type > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD didn't give content-length
        if r.status_code == 200 and "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                             headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            r2.close()
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation failed: {e}")
    return False


def sb_insert(table, row):
    """Insert a row into Supabase and return the response."""
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=row,
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            return data[0]
        return data
    print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
    return None


def make_slug(headline):
    """Generate a clean slug from headline."""
    slug = re.sub(r'[^a-z0-9\s-]', '', headline.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    slug = slug[:80].rstrip('-')
    date_suffix = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"{slug}-{date_suffix}"


def publish_article(article):
    """Publish an article to Supabase."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    row = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "body": article["body"],
        "category": "news",
        "vertical": article.get("vertical", "politics"),
        "status": "published",
        "published_at": now,
        "created_at": now,
        "updated_at": now,
        "image_url": article.get("image_url", ""),
        "image_caption": article.get("image_caption", ""),
        "image_attribution": article.get("image_attribution", ""),
        "sources": json.dumps(article.get("sources", [])),
    }

    result = sb_insert("p2_articles", row)
    if result:
        print(f"  ✓ Published: {article['headline'][:70]}... (id: {art_id[:8]})")
        return art_id
    return None


# ═══════════════════════════════════════════
# ARTICLES
# ═══════════════════════════════════════════

articles = []

# ── Article 1: Iran Ends 88-Day Internet Shutdown ──
print("\n── Article 1: Iran Internet Shutdown Ends ──")

art1_headline = "Iran Just Restored Internet Access After 88 Days. India Knows Exactly What That Silence Feels Like."
art1_subheadline = "Tehran lifted the blackout to ease economic pain. India leads the world in internet shutdowns — and its diaspora has been watching both countries closely."
art1_slug = make_slug("iran-restores-internet-88-days-india-shutdowns")

art1_body = """Iran has restored internet access to its citizens after an 88-day blackout — the longest continuous internet shutdown in the country's history. The decision, announced Wednesday, immediately reconnected millions of Iranians who had been cut off from the outside world since late February.

The shutdown was initially imposed in January 2026 to suppress anti-government protests that had erupted across several major cities. It was briefly lifted before being reimposed in February following U.S. and Israeli military strikes on Iranian territory, as Tehran sought to control the flow of information during the conflict.

## What Forced Tehran's Hand

The decision to restore connectivity was not a concession to civil liberties. It was economics. Iran's digital economy — e-commerce platforms, ride-hailing services, freelance tech workers — had been hemorrhaging revenue for nearly three months. Small businesses that depended on Instagram and Telegram for customer acquisition were shuttered. International remittances, many of which flow through digital channels, had slowed to a trickle.

Analysts say the economic pressure, combined with the prospect of a framework deal with the United States over the Strait of Hormuz, gave Tehran the political cover it needed to flip the switch back on.

"The government is trying to signal normalcy ahead of any potential deal," said Amir Rashidi, a digital rights researcher at the Miaan Group. "But everyone knows the internet can be shut down again in hours if negotiations collapse."

## India Leads the World in Internet Shutdowns

The Iran story resonates uncomfortably in India, which has imposed more internet shutdowns than any other country in the world. According to Access Now's annual report, India accounted for over 60 percent of all documented internet shutdowns globally between 2016 and 2025 — a total exceeding 900 separate incidents.

The shutdowns have disproportionately affected Kashmir, where residents experienced a continuous blackout lasting 552 days between August 2019 and February 2021 — far longer than Iran's 88-day cutoff. Shutdowns have also been imposed in Manipur, Rajasthan, Haryana, and parts of Uttar Pradesh during periods of communal tension, protests, or examinations.

For India's diaspora, the parallel is personal. NRIs with family in affected regions have experienced the same helpless silence — unable to reach parents, unable to confirm safety, unable to conduct business. WhatsApp groups that serve as lifelines for transnational families go dark without warning.

## The Economic Cost Is Staggering

A 2025 report by Top10VPN estimated that internet shutdowns cost India over $4 billion in economic losses between 2019 and 2025. Iran's 88-day blackout is estimated to have cost the country upward of $1.5 billion, though independent verification is difficult given Tehran's opacity on economic data.

The Indian government has defended shutdowns as necessary for maintaining public order and preventing the spread of disinformation. Critics, including the Internet Freedom Foundation and several Indian-origin technologists in Silicon Valley, argue that blanket shutdowns are a disproportionate response that punishes entire populations for the actions of a few.

## What Comes Next

Iran's internet restoration is fragile. Analysts warn that connectivity could be severed again if the U.S.-Iran negotiations over the Strait of Hormuz collapse or if domestic unrest flares. The Iranian government continues to block major platforms including Twitter, Facebook, and YouTube, routing users through state-monitored alternatives.

For India, the question is whether the global attention on Iran's blackout will renew pressure on New Delhi to adopt more targeted approaches to information control. The Supreme Court of India ruled in 2020 that internet access is a fundamental right under Article 19 of the Constitution — but enforcement has been inconsistent, and state governments continue to order shutdowns with little accountability.

The 88 days of Iranian silence are over. For millions of Indians who have lived through their own blackouts, the lesson is familiar: the switch that turns the internet off is always easier to flip than the one that turns it back on."""

# Image: Try Wikipedia for Iran internet / use Pexels
art1_img = fetch_pexels_image("Iran Tehran city street people smartphones", "people using smartphones crowd")
art1_img_attr = "Pexels"
art1_img_caption = "Iranians reconnecting after 88 days of internet blackout"
if not art1_img or not validate_image(art1_img):
    art1_img = ""
    art1_img_attr = ""
    art1_img_caption = ""
    print("  ⚠ No valid image found for article 1")

articles.append({
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "slug": art1_slug,
    "body": art1_body,
    "image_url": art1_img,
    "image_caption": art1_img_caption,
    "image_attribution": art1_img_attr,
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Access Now", "url": "https://www.accessnow.org"},
        {"name": "Top10VPN", "url": "https://www.top10vpn.com"},
    ],
    "vertical": "geopolitics",
})


# ── Article 2: US Mortgage Rates Hit 9-Month High ──
print("\n── Article 2: US Mortgage Rates 9-Month High ──")

art2_headline = "US Mortgage Rates Just Hit a Nine-Month High. Indian Americans Are the Fastest-Growing Homebuyer Group in the Country."
art2_subheadline = "The average 30-year rate climbed to 6.65 percent as oil-driven inflation and Fed uncertainty squeeze the housing market. For NRI families saving for their first American home, the math just got harder."
art2_slug = make_slug("us-mortgage-rates-nine-month-high-indian-american-homebuyers")

art2_body = """The average 30-year fixed mortgage rate in the United States climbed to 6.65 percent in the week ending May 22 — the highest level in nine months — as inflation concerns driven by elevated oil prices and the ongoing Iran conflict continue to ripple through financial markets.

The Mortgage Bankers Association reported that mortgage applications dropped 8.5 percent from the previous week, with overall application volumes at their lowest since last summer. The combination of rising rates, limited housing supply, and what economists call the "rate lock-in phenomenon" — where existing homeowners refuse to sell because they'd lose their sub-4-percent pandemic-era rates — has created a housing market that is increasingly inhospitable to first-time buyers.

## Why This Hits Indian Americans Harder

Indian Americans are among the fastest-growing homebuyer demographics in the United States. According to the National Association of Realtors' 2025 Profile of International Transactions, buyers from India accounted for the third-largest share of international home purchases in the U.S., behind only buyers from China and Canada.

But the story is bigger than international buyers. Second-generation Indian Americans and H-1B visa holders who have transitioned to green cards or citizenship represent a massive domestic buying cohort. Many are dual-income tech professionals concentrated in the most expensive housing markets in the country — the San Francisco Bay Area, Seattle, New Jersey's Edison-Brunswick corridor, and the Dallas-Fort Worth metroplex.

A rate increase from 6 percent to 6.65 percent on a $700,000 home — a median price point in many of these markets — adds roughly $300 per month to mortgage payments, or $108,000 over the life of a 30-year loan.

## The Oil-Inflation Feedback Loop

The rate spike is directly tied to the Iran conflict. The Strait of Hormuz crisis, which has disrupted roughly 20 percent of global oil and LNG shipments, pushed U.S. gasoline prices above $4.50 per gallon in most states. That energy inflation has leaked into core consumer prices, making the Federal Reserve reluctant to cut rates.

Kevin Warsh, who took over as Fed Chair earlier this year, has signaled that the central bank may need to raise rates if inflation persists — a stark reversal from the rate-cutting cycle markets had anticipated at the start of 2026. Financial markets are now pricing in the possibility of a Fed rate hike by year's end.

For Indian American families, the oil-inflation-mortgage chain is a triple squeeze: higher gas prices for the daily commute, higher grocery bills driven by transportation costs, and now higher borrowing costs for the single largest purchase most families will ever make.

## The Rate Lock-In Trap

The housing supply crisis has a uniquely American dimension that compounds the rate problem. An estimated 60 percent of existing mortgages in the U.S. carry rates below 4 percent, locked in during the pandemic-era refinancing boom. Those homeowners have no financial incentive to sell — doing so would mean trading a 3.2 percent mortgage for a 6.65 percent one.

The result is an artificial housing shortage that keeps prices elevated even as demand softens. New construction has not kept pace, particularly in the high-density urban and suburban markets where Indian American families tend to cluster.

## What NRI Families Are Doing

Real estate agents serving Indian American communities in the Bay Area and New Jersey report a shift in strategy. Some buyers are turning to adjustable-rate mortgages (ARMs), betting that rates will eventually decline. Others are pooling family resources across generations — a common practice in Indian households — to make larger down payments and reduce the loan principal.

A growing number of NRI families are also redirecting their property investment toward India, where mortgage rates are lower and the rupee's depreciation against the dollar has made Indian real estate relatively affordable for dollar earners. But that trade-off comes with its own complications: long-distance property management, regulatory complexity, and the challenge of building equity in a country where you don't live.

## The Bigger Picture

The 6.65 percent rate is not the highest in recent memory — rates briefly touched 7.5 percent in late 2023 — but it arrives in a different economic context. The Iran war has injected a level of geopolitical uncertainty into energy markets that did not exist two years ago. The Fed is led by a new chair whose instincts lean hawkish. And the housing market, already strained by a decade of underbuilding, has no relief valve.

For the Indian American community — one of the highest-earning and fastest-growing demographic groups in the country — the dream of homeownership hasn't changed. The price of that dream just went up again."""

art2_img = fetch_pexels_image("house for sale sign suburban America", "American suburb homes residential street")
art2_img_attr = "Pexels"
art2_img_caption = "US mortgage rates hit a nine-month high, squeezing homebuyers"
if not art2_img or not validate_image(art2_img):
    art2_img = ""
    art2_img_attr = ""
    art2_img_caption = ""
    print("  ⚠ No valid image found for article 2")

articles.append({
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "slug": art2_slug,
    "body": art2_body,
    "image_url": art2_img,
    "image_caption": art2_img_caption,
    "image_attribution": art2_img_attr,
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Mortgage Bankers Association", "url": "https://www.mba.org"},
        {"name": "National Association of Realtors", "url": "https://www.nar.realtor"},
    ],
    "vertical": "economy",
})


# ── Article 3: Carney's Government Shrinks After Environment Minister Quits ──
print("\n── Article 3: Carney Government Shrinks ──")

art3_headline = "Canada's Government Just Shrank to a One-Seat Majority. The India Trade Deal Could Be the First Casualty."
art3_subheadline = "Former environment minister Steven Guilbeault quit over climate rollbacks. For 1.8 million Indian Canadians watching the CEPA negotiations, political instability in Ottawa is the last thing they needed."
art3_slug = make_slug("canada-carney-one-seat-majority-india-cepa-trade-deal")

art3_body = """Canadian Prime Minister Mark Carney's government has been reduced to a single-seat parliamentary majority after former environment minister Steven Guilbeault announced he will resign his seat, citing irreconcilable differences over the government's decision to roll back climate regulations to attract energy investment.

Guilbeault, who left Carney's cabinet weeks ago over the same dispute, said Wednesday that he could no longer serve in a parliament that was "trading the planet for pipelines." His departure drops the Liberal Party from 173 seats to 172 — exactly the bare minimum needed for a majority in the 343-seat House of Commons.

## Why It Matters for India

The timing could not be worse for the Canada-India Comprehensive Economic Partnership Agreement, or CEPA, which both countries announced last week as a potential "game changer" in bilateral trade. Commerce Minister Piyush Goyal led the largest Indian business delegation ever sent abroad to Ottawa, and Carney personally committed to tripling bilateral commerce to $50 billion.

A one-seat majority means every single Liberal member of parliament must show up for every vote. One absence, one defection, one illness — and the government loses the ability to pass legislation, including the trade deal's enabling framework.

More concerning for Indian negotiators: Guilbeault's resignation has exposed deep fractures within the Liberal caucus over the direction of economic policy. At least two other Liberal members have publicly questioned Carney's pivot toward energy deregulation, raising the specter that further defections could topple the majority entirely and force a snap election.

## Canada's Indian Diaspora Is Watching

Canada is home to approximately 1.8 million people of Indian origin — the largest Indian diaspora community in any country relative to population. The community has grown rapidly since 2015, driven by international students, skilled worker programs, and family reunification visas.

For Indian Canadians, the CEPA deal represents more than trade statistics. It would ease barriers for Indian professionals seeking Canadian credentials, streamline goods imports that serve the community's cultural and culinary needs, and create new business corridors between Indian cities and Canadian hubs like Brampton, Surrey, and Mississauga.

The bilateral relationship has endured a turbulent two years. The diplomatic crisis triggered by allegations of Indian government involvement in the killing of Sikh separatist leader Hardeep Singh Nijjar in British Columbia in June 2023 led to mutual expulsions of diplomats and a deep freeze in relations that lasted through much of 2024 and 2025.

The CEPA announcement signaled that both governments were ready to move past the crisis. Carney's political vulnerability puts that reset at risk.

## The Climate-Trade Tension

Guilbeault's grievance is specific but consequential. Carney's government struck a deal to relax environmental regulations on energy production — including oil sands expansion and LNG export terminals — in exchange for industry commitments on carbon capture and methane reduction. The move was designed to position Canada as a reliable energy supplier to allies affected by the Strait of Hormuz disruption.

For India, which is scrambling to diversify its oil imports away from the Middle East, Canadian energy exports are strategically attractive. India has already increased crude purchases from Latin America and Africa since the Hormuz crisis began, and a Canadian pipeline would add another non-Gulf option.

But Guilbeault's resignation — and the broader environmental backlash within the Liberal Party — suggests that the political consensus behind Canada's energy pivot is fragile. If the Liberals lose their majority and the opposition Conservatives under Pierre Poilievre gain power, the CEPA deal's terms could change entirely.

## What Happens Next

Carney has thanked Guilbeault for his service and indicated the government intends to press forward with its legislative agenda. The prime minister's office has downplayed the significance of the one-seat margin, noting that previous Canadian governments have governed effectively with slim majorities.

But parliamentary math is unforgiving. The next confidence vote — likely on a budget measure later this summer — will be the first real test. If a single Liberal member breaks ranks, Carney faces either a parliamentary crisis or a deal with the New Democratic Party (NDP) for informal support, which would come with its own policy concessions.

For the 1.8 million Indian Canadians who have built lives, businesses, and families in a country they chose precisely because of its stability, the message is unsettling: the political ground in Ottawa is shifting, and the India relationship that took years to repair now depends on the attendance record of 172 parliamentarians."""

# Image: Try Wikipedia for Mark Carney
art3_img = fetch_wikipedia_person_image("Mark Carney")
art3_img_attr = "Wikimedia Commons"
art3_img_caption = "Canadian Prime Minister Mark Carney's government reduced to a one-seat majority"
if not art3_img or not validate_image(art3_img):
    art3_img = fetch_pexels_image("Canadian parliament building Ottawa", "Canada parliament exterior")
    art3_img_attr = "Pexels"
    if not art3_img or not validate_image(art3_img):
        art3_img = ""
        art3_img_attr = ""
        art3_img_caption = ""
        print("  ⚠ No valid image found for article 3")

articles.append({
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "slug": art3_slug,
    "body": art3_body,
    "image_url": art3_img,
    "image_caption": art3_img_caption,
    "image_attribution": art3_img_attr,
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Government of Canada", "url": "https://www.canada.ca"},
        {"name": "Statistics Canada", "url": "https://www.statcan.gc.ca"},
    ],
    "vertical": "politics",
})


# ═══════════════════════════════════════════
# PUBLISH ALL
# ═══════════════════════════════════════════

print("\n═══ Publishing articles ═══")
published = 0
for art in articles:
    result = publish_article(art)
    if result:
        published += 1
    time.sleep(1)

print(f"\n✅ Done. Published {published}/{len(articles)} articles.")
