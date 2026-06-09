#!/usr/bin/env python3
"""
News writer for The Videshi — 2026-06-09 batch
3 articles: Modi France-Slovakia, TCS AI Agents, US-Iran Deal India angle
"""

import json, os, sys, time, re, uuid
import requests
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

UA = 'TheVideshi/1.0 (thevideshi.com)'

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    encoded = person_name.replace(' ', '_')
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
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

def fetch_wikimedia_commons(search_query, limit=5):
    """Search Wikimedia Commons for images."""
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
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                if url and ii.get("mime", "").startswith("image/"):
                    width = ii.get("thumbwidth") or ii.get("width", 0)
                    results.append({"url": url, "width": width, "title": page.get("title", "")})
            # Sort by width descending
            results.sort(key=lambda x: x["width"], reverse=True)
            return results
    except Exception as e:
        print(f"  ⚠ Commons search error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for a relevant image."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 5, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found: {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image(url):
    """Verify image URL returns 200 with image content type and > 5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Try GET if HEAD doesn't give content-length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: >{len(chunk)} bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
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
            print(f"  ✓ Inserted: {result[0].get('id', 'unknown')} — {article['headline']}")
            return True
        print(f"  ✓ Inserted: {article['headline']}")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return False


# ============================================================
# ARTICLE 1: Modi France-Slovakia Visit
# ============================================================
def write_modi_france_slovakia():
    print("\n=== ARTICLE 1: Modi France-Slovakia Visit ===")

    # Image sourcing
    print("Sourcing images...")
    img_url = fetch_wikipedia_person_image("Narendra Modi")
    img_caption = "Indian Prime Minister Narendra Modi"
    img_attribution = "Wikimedia Commons"

    if not img_url or not validate_image(img_url):
        # Try Commons
        commons = fetch_wikimedia_commons("Narendra Modi Emmanuel Macron")
        for c in commons:
            if validate_image(c["url"]):
                img_url = c["url"]
                img_caption = "Indian Prime Minister Narendra Modi during a diplomatic meeting"
                break

    if not img_url:
        print("  ✗ No valid image found")
        return False

    body = """Modi will land in Nice on June 13 for the first leg of a six-day European tour that covers France and Slovakia — and carries weight well beyond the photo opportunities.

## France: Strategic Partnership, Startup Diplomacy

The visit to France comes during the India-France Year of Innovation, and the centrepiece is an event called **Bharat Innovates** — a gathering of Indian and French startups and venture capital funds in Nice. Macron and Modi will jointly inaugurate it on June 14, turning what could have been a routine bilateral into a showcase for cross-border tech collaboration.

The two leaders are expected to review the full arc of a relationship that was elevated to a Special Global Strategic Partnership earlier this year. That upgrade was not merely ceremonial: it covers defence procurement, civil nuclear cooperation, space partnerships, and a growing alignment on Indo-Pacific maritime security. With the Iran war disrupting energy supply chains and forcing India to diversify both its oil sources and its strategic alliances, the France relationship has gained practical urgency.

After Nice, Modi will attend the 52nd G7 Summit in Evian, where India holds an outreach seat. The summit agenda is expected to be dominated by the Iran war, global energy security, and the AI governance frameworks that the G7 has been debating since last year. India's voice at the table matters more now than in any recent summit cycle, given its position as the world's third-largest oil importer navigating a supply crisis.

## Slovakia: A Historic First

The Slovakia leg is the headline-maker for diplomatic historians. No Indian Prime Minister has visited Slovakia since the country's independence in 1993. Modi will hold talks with Slovak Prime Minister Robert Fico and meet President Peter Pellegrini — both of whom have visited India in the past year, setting the groundwork for this trip.

The bilateral agenda focuses on trade, investment, and manufacturing partnerships, particularly in automobiles and railways — sectors where Slovakia has deep industrial capacity and India has enormous demand. For the roughly 5,000 Indians living in Slovakia, many of them IT professionals and students, the visit is a recognition moment. Slovakia has been a quiet but steady destination for Indian talent in Central Europe, and a prime ministerial visit tends to unlock visa and mobility conversations that were previously stuck at the bureaucratic level.

## The Diaspora Angle

For NRIs in Europe, the visit is a signal that India's diplomatic bandwidth extends beyond the usual Washington-London-Abu Dhabi circuit. France already hosts one of Western Europe's largest Indian communities, with over 100,000 people of Indian origin. The startup event in Nice could open doors for diaspora entrepreneurs looking to build bridges between Indian and European markets.

The timing is also pointed. With India's economy absorbing the Iran war's oil shock — inflation just crossed the RBI's 4% target, the rupee has weakened to 95 against the dollar, and the fiscal deficit is under pressure — Modi's European outreach is partly about diversifying economic relationships and securing investment flows that can cushion the blow.

## What to Watch

The G7 outreach session will be the most closely watched moment. If Trump and Iran are indeed "in the final throes" of a ceasefire deal, as the U.S. president claimed this week, India will want to ensure its energy interests are baked into any arrangement that reopens the Strait of Hormuz. Modi's conversations with Macron and other G7 leaders could shape whether India gets a seat at that table — or is left to deal with the consequences."""

    article = {
        "headline": "Modi Heads to France and Slovakia This Week. It Is India's First PM Visit to Bratislava Ever.",
        "subheadline": "The six-day European tour covers the G7 summit in Evian, a startup showcase in Nice, and the first Indian prime ministerial visit to Slovakia since the country's independence in 1993.",
        "body": body.strip(),
        "slug": "modi-france-slovakia-visit-g7-bharat-innovates-first-ever-bratislava-20260609",
        "category": "news",
        "vertical": "news",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "sources": json.dumps([
            {"name": "Ministry of External Affairs / narendramodi.in", "url": "https://www.narendramodi.in"},
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "Wikipedia - List of international PM trips", "url": "https://en.wikipedia.org/wiki/List_of_international_prime_ministerial_trips_made_by_Narendra_Modi"}
        ]),
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ============================================================
# ARTICLE 2: TCS AI Agents = Human Employees
# ============================================================
def write_tcs_ai_agents():
    print("\n=== ARTICLE 2: TCS AI Agents ===")

    # Image sourcing — N Chandrasekaran
    print("Sourcing images...")
    img_url = fetch_wikipedia_person_image("N. Chandrasekaran")
    img_caption = "Tata Sons Chairman N. Chandrasekaran at a corporate event"
    img_attribution = "Wikimedia Commons"

    if not img_url or not validate_image(img_url):
        img_url = fetch_wikipedia_person_image("Natarajan Chandrasekaran")
        if not img_url or not validate_image(img_url):
            # Try Commons
            commons = fetch_wikimedia_commons("Natarajan Chandrasekaran TCS Tata")
            for c in commons:
                if validate_image(c["url"]):
                    img_url = c["url"]
                    break

    if not img_url or not validate_image(img_url):
        # Fallback to TCS building or generic
        commons = fetch_wikimedia_commons("Tata Consultancy Services headquarters")
        for c in commons:
            if validate_image(c["url"]):
                img_url = c["url"]
                img_caption = "Tata Consultancy Services headquarters in Mumbai"
                break

    if not img_url:
        # Last resort: Pexels for AI/tech office
        img_url = fetch_pexels_image("artificial intelligence technology office")
        img_caption = "Artificial intelligence is reshaping India's IT services industry"
        img_attribution = "Pexels"
        if img_url and not validate_image(img_url):
            img_url = None

    if not img_url:
        print("  ✗ No valid image found")
        return False

    body = """Half a million humans. Half a million AI agents. Working side by side.

That is the future Tata Sons Chairman N. Chandrasekaran sketched out at TCS's 31st Annual General Meeting on Tuesday — and it is not a decade-away aspiration. He gave it three years.

## The Numbers Behind the Prediction

TCS ended fiscal year 2026 with 584,519 employees, already down 23,460 from the previous year after the company's largest-ever layoff drive last July, when it cut more than 12,000 positions. Chandrasekaran's prediction means TCS would deploy roughly one AI agent for every human employee still on its payroll — an army of automated software workers handling tasks that were, until recently, the bread and butter of India's IT services model.

"If the company has half a million employees, the day is not far when the company will have half a million AI agents," Chandrasekaran told shareholders in Mumbai. "The company's employees and AI agents will work together, and that will be the future."

He framed the shift not as a threat but as the industry's biggest opportunity. TCS's AI revenue has been growing at a compound quarterly rate of more than 22%, hitting an annualised $2.5 billion in the last quarter of FY26. Nearly three-quarters of enterprises globally expect their technology spending to rise over the next two years, he said, driven largely by AI adoption.

## What This Means for Indian IT Workers

The implications ripple far beyond TCS's Mumbai headquarters. India's $315-billion IT sector is one of the country's largest private employers, and the diaspora is deeply entwined with it — hundreds of thousands of Indian professionals in the US, UK, and Canada built their careers and immigration pathways through IT services firms like TCS, Infosys, and Wipro.

Chandrasekaran was blunt: hiring will slow. "Will it definitely lead to a decrease in hiring? Absolutely," he said. "The company will not be hiring the kind of numbers that it used to hire, because certain portions of the work, in the current scheme of things, will go to agents."

He ruled out further layoffs for now, and said new roles and opportunities would emerge as AI reshapes what work looks like. But the reassurance rings hollow for the lakhs of engineering graduates who enter the job market each year expecting an IT services career as the default path to a middle-class life.

TCS shares have fallen more than 32% in 2026, compared with a 25% decline in the broader Nifty IT index. The market has been pricing in this transition for months.

## The Diaspora Impact

For NRIs on H-1B visas or green card tracks tied to IT services employers, the shift carries a specific anxiety. If TCS and its peers are hiring fewer bodies, the pipeline of sponsored visa petitions will narrow. For those already in the US, the question is whether their current roles will be among those absorbed by AI agents or whether they can pivot to the new roles Chandrasekaran hinted at — ones that bridge AI, physical infrastructure, and enterprise systems.

"Today, AI primarily exists in the world of software and computers, but soon it will make inroads into the physical world: stores, factories, warehouses, energy networks, vehicles and supply chains," Chandrasekaran said. "This will require experts who understand how to link IT, AI and physical equipment and infrastructure."

That is the upskilling bet. Whether TCS — and India's IT industry — can execute on it before the old model erodes completely is the question that will define the next three years.

## The Bigger Picture

Chandrasekaran described AI as "the most consequential work" in TCS's history and pushed back on the existential panic that has hung over India's IT sector since ChatGPT landed. "Far from being a mortal threat, AI is the most significant opportunity yet for enterprise IT," he said.

The market will judge that claim by the numbers. For now, the company that once symbolised India's services export miracle is betting its future on a workforce where humans and machines split the work 50-50. The transition has already begun. The only question is how many people it leaves behind."""

    article = {
        "headline": "TCS Will Have Half a Million AI Agents Within Three Years. Hiring Will Shrink.",
        "subheadline": "Tata Sons Chairman N. Chandrasekaran told shareholders that AI workers will match TCS's human headcount — and that the days of mass IT hiring are over.",
        "body": body.strip(),
        "slug": "tcs-half-million-ai-agents-chandrasekaran-agm-hiring-slowdown-20260609",
        "category": "news",
        "vertical": "news",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
            {"name": "Mint", "url": "https://www.livemint.com"}
        ]),
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ============================================================
# ARTICLE 3: US-Iran Deal Nearing — India Angle
# ============================================================
def write_iran_deal_india():
    print("\n=== ARTICLE 3: US-Iran Deal Nearing — India Angle ===")

    # Image sourcing
    print("Sourcing images...")
    # Try Commons for Strait of Hormuz / Iran deal
    img_url = None
    img_caption = ""
    img_attribution = "Wikimedia Commons"

    commons = fetch_wikimedia_commons("Strait of Hormuz shipping oil tanker")
    for c in commons:
        if validate_image(c["url"]):
            img_url = c["url"]
            img_caption = "Oil tankers near the Strait of Hormuz, a critical chokepoint for global energy supplies"
            break

    if not img_url:
        img_url = fetch_wikipedia_person_image("Strait of Hormuz")
        if img_url and validate_image(img_url):
            img_caption = "The Strait of Hormuz, through which a fifth of the world's oil transits"
        else:
            img_url = None

    if not img_url:
        img_url = fetch_pexels_image("oil tanker shipping sea")
        img_caption = "Oil tankers in transit — India imports 90% of its crude oil"
        img_attribution = "Pexels"
        if img_url and not validate_image(img_url):
            img_url = None

    if not img_url:
        print("  ✗ No valid image found")
        return False

    body = """The Strait of Hormuz could reopen within days. For India, that changes everything.

After months of fire, sanctions, and the worst energy supply disruption since the Ukraine war, the United States and Iran appear to be converging on a ceasefire extension that would unlock the waterway through which a fifth of the world's oil and gas flowed before the conflict began.

## What the Deal Looks Like

A senior Arab official involved in the negotiations told NBC News that negotiators from both sides have reached an agreement, with final approval pending from President Trump and Iran's top leadership. The reported framework would reopen the Strait of Hormuz immediately and extend the ceasefire by 60 days to allow negotiations on Iran's nuclear program to continue.

Trump, speaking to reporters early Tuesday, said the sides were "in the final throes" of what he called a "very, very good deal." Vice President JD Vance confirmed that negotiators are working through final language points. Treasury Secretary Scott Bessent outlined three U.S. conditions: "Open the Strait, highly enriched uranium, no nuclear program."

Iran, however, has been pushing to maintain some control over strait traffic indefinitely — a sticking point that could still derail the talks. The U.S. carried out fresh strikes on military targets in southern Iran overnight, even as both sides said the ceasefire remains in effect.

## Why India Is Watching Every Word

No major economy has been hit harder by the Hormuz blockade than India. The numbers tell the story:

India imports roughly 90% of its crude oil, and before the war, more than 40% of those imports came through the strait. LPG imports — 90% of which transited Hormuz — have cratered, triggering what officials call the worst cooking gas supply crisis in decades. State-owned fuel retailers have raised petrol and diesel prices four times in May alone. Inflation has crossed the RBI's 4% target for the first time in 16 months.

The economic damage is compounding. India's fertiliser ministry has asked to double its subsidy budget barely three months into the fiscal year. The rupee has sunk to a record low of 95 against the dollar. The Congress party's latest report claims India has slipped from the world's fourth-largest economy to sixth. Oil Minister Hardeep Singh Puri acknowledged that the situation could become "worrying" if the crisis expands, though he insists India has oil reserves for 76-80 days.

A deal that reopens Hormuz would begin to reverse this cascade. Crude prices, which have surged 40% to near $100 a barrel since the war, would face immediate downward pressure. LPG shipments from the Gulf — India's primary cooking gas source — would resume. Freight insurance costs, which have ballooned as tankers avoid the war zone, would drop.

## The Diaspora Stake

For NRIs, especially those in the US, the deal has a double edge. On one hand, cheaper oil would ease inflation both in India and in the US, where gasoline prices have hit their highest levels in years. The Broadcom-triggered tech selloff last week wiped $2.5 trillion from US markets, hitting NRI portfolios heavy in tech stocks. A geopolitical de-escalation could stabilise markets.

On the other hand, any deal that includes expanded Abraham Accords — Trump has said he wants more Middle Eastern countries to normalise relations with Israel as part of the agreement — could reshape the Gulf's political dynamics in ways that affect the 9 million Indians living and working in the region.

## What Could Go Wrong

The gap between "largely negotiated" and "signed" has been wide before. Trump has claimed an Iran deal was imminent at least half a dozen times since the war began. Iran has suspended nuclear negotiations, demanding a complete ceasefire in Lebanon as a precondition. Israel struck the Lebanese port city of Tyre on Tuesday, killing eight people — the deadliest raid on the city since fighting erupted in March.

India's foreign ministry, which expressed "utmost concern" over renewed hostilities on Monday, is watching from a position of limited leverage. New Delhi has repeatedly called for diplomacy but has little influence over the principals at the table.

For now, the only certainty is that every day the strait remains closed costs India roughly ₹3,500 crore in additional import bills. A deal — even an imperfect, 60-day one — would buy time. And time, in this economy, is worth more than it has been in years."""

    article = {
        "headline": "The US and Iran Say a Deal Is Days Away. India Needs It More Than Anyone at the Table.",
        "subheadline": "A ceasefire framework that reopens the Strait of Hormuz would begin to reverse the worst energy supply crisis India has faced in years — but the gap between 'largely negotiated' and 'signed' has been wide before.",
        "body": body.strip(),
        "slug": "us-iran-deal-hormuz-india-oil-relief-ceasefire-60-days-20260609",
        "category": "news",
        "vertical": "news",
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "sources": json.dumps([
            {"name": "NBC News", "url": "https://www.nbcnews.com"},
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "CNN", "url": "https://www.cnn.com"},
            {"name": "USA Today", "url": "https://www.usatoday.com"}
        ]),
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    results = []
    results.append(("Modi France-Slovakia", write_modi_france_slovakia()))
    results.append(("TCS AI Agents", write_tcs_ai_agents()))
    results.append(("US-Iran Deal India", write_iran_deal_india()))

    print("\n=== RESULTS ===")
    for name, ok in results:
        print(f"  {'✓' if ok else '✗'} {name}")

    failures = sum(1 for _, ok in results if not ok)
    if failures:
        print(f"\n⚠ {failures} article(s) failed")
        sys.exit(1)
    else:
        print(f"\n✓ All {len(results)} articles inserted successfully")
