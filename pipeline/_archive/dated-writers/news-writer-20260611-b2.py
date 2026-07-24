#!/usr/bin/env python3
"""Videshi News Writer - June 11, 2026 batch 2
Topics:
1. TCS partners with Anthropic (50K employees get Claude)
2. India fertiliser subsidy doubles as Iran war costs mount
3. Telangana student Anshul Kuncha shot dead in Philadelphia pizza delivery trap
"""

import requests
import json
import os
from datetime import datetime, timezone

# ── Load env ──────────────────────────────────────────────────────
def load_env(path):
    env = {}
    try:
        with open(os.path.expanduser(path)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return env

supabase_env = load_env('~/.env.supabase')
pexels_env = load_env('~/workspace/.env.pexels')

SUPABASE_URL = supabase_env.get('SUPABASE_URL', '')
SUPABASE_KEY = supabase_env.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = pexels_env.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

UA = 'TheVideshi/1.0 (thevideshi.com)'

# ── Image sourcing ────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(' ', '_')
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
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


def fetch_wikimedia_commons(query, limit=5):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime",
        "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                w = ii.get("width", 0)
                if w < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": w, "height": ii.get("height", 0)
                })
            if results:
                print(f"  ✓ Commons: {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{query}': {e}")
    return []


def fetch_pexels(query, per_page=5):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return []
    try:
        r = requests.get("https://api.pexels.com/v1/search",
                         params={"query": query, "per_page": per_page, "orientation": "landscape"},
                         headers={"Authorization": PEXELS_KEY}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            results = []
            for photo in data.get("photos", []):
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large", "")
                if url:
                    results.append({"url": url, "width": photo.get("width", 0),
                                    "height": photo.get("height", 0), "alt": photo.get("alt", "")})
            if results:
                print(f"  ✓ Pexels: {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return []


def validate_image(url):
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and ct.startswith('image/') and cl > 5000:
            print(f"  ✓ Valid: {cl} bytes, {ct}")
            return True
        if r.status_code == 200 and ct.startswith('image/') and cl == 0:
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Valid (GET): >{len(chunk)} bytes")
                return True
        print(f"  ✗ Failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Validation error: {e}")
    return False


def best_image(commons_results, pexels_results, wiki_person_url=None):
    if wiki_person_url and validate_image(wiki_person_url):
        return wiki_person_url, "Wikimedia Commons"
    for img in commons_results:
        url = img.get("url", "")
        if url and validate_image(url):
            return url, "Wikimedia Commons"
    for img in pexels_results:
        url = img.get("url", "")
        if url and validate_image(url):
            return url, "Pexels"
    return None, None


# ── Insert article ────────────────────────────────────────────────
def insert_article(article):
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": article["category"],
        "vertical": article.get("vertical", article["category"]),
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption", ""),
        "image_attribution": article.get("image_attribution", ""),
        "sources": json.dumps(article.get("sources", [])),
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "created_at": now
    }
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles",
                      headers=HEADERS_SB, json=payload, timeout=15)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            art_id = result[0].get('id', 'unknown')
            print(f"  ✓ Inserted: {article['slug']} (id: {art_id})")
            return True
        print(f"  ✓ Inserted: {article['slug']}")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return False


# ══════════════════════════════════════════════════════════════════
# ARTICLE 1: TCS + Anthropic
# ══════════════════════════════════════════════════════════════════
def article_tcs_anthropic():
    print("\n═══ Article 1: TCS + Anthropic ═══")
    wiki_img = fetch_wikipedia_person_image("Tata Consultancy Services")
    commons = fetch_wikimedia_commons("Tata Consultancy Services building")
    pexels = fetch_pexels("enterprise AI technology office")
    image_url, attribution = best_image(commons, pexels, wiki_img)

    body = """Tata Consultancy Services, India's largest IT services exporter, has partnered with Anthropic to bring the company's Claude AI models to 50,000 employees — a move that underscores how dramatically India's $315-billion IT sector is reshaping itself around artificial intelligence.

The alliance, announced on Thursday, will see TCS equip tens of thousands of its associates with Claude while jointly developing AI solutions for highly regulated industries including banking, healthcare and insurance. It comes just days after TCS chairman N. Chandrasekaran told shareholders at the company's annual general meeting that AI agents would eventually match the company's human headcount — and that mass hiring as the industry has known it is over.

For a company that built its empire on deploying hundreds of thousands of engineers to client sites around the world, the partnership marks a philosophical shift as much as a technological one.

## The Deal

Under the agreement, TCS and Anthropic will co-develop enterprise-grade AI solutions tailored for sectors where safety, compliance and accuracy are non-negotiable. The 50,000 associates receiving access to Claude will not simply be using it as a chatbot — they will be trained to integrate it into existing client workflows, effectively turning each worker into an AI-augmented operator.

TCS said the partnership would allow it to bring responsible AI solutions to market faster, at a time when enterprises are demanding both speed and reliability from their technology providers.

The move mirrors a similar deal struck by rival Infosys with Anthropic in February. That partnership prompted a significant selloff across the Indian IT sector, with companies losing more than $62.8 billion in combined market capitalisation as investors feared that AI tools would fundamentally disrupt the labour-intensive outsourcing model.

## The Workforce Reckoning

The timing is pointed. TCS cut more than 12,000 jobs last July, and its net headcount fell by more than 23,000 over the fiscal year ending March 2026. Chandrasekaran's remarks at the AGM this week — that TCS expects to eventually have an equal number of employees and AI agents — were widely interpreted as a signal that the age of incremental hiring is over.

For the millions of Indian IT workers who have built careers and middle-class lives in cities like Bengaluru, Hyderabad and Pune — and for the tens of thousands who have moved to the United States, the United Kingdom and Canada on work visas — the question is existential. If the value proposition of Indian IT was always volume at a competitive price, what happens when AI agents can deliver output at a fraction of the cost?

Industry analysts say the shift is not about replacing workers overnight but about changing what employers expect from each one. The floor has moved. A mid-level developer who was billable at a certain rate will now be expected to produce multiples of their previous output. That is the real disruption — not mass layoffs, but a permanent ratcheting of expectations.

## What It Means for the Diaspora

For NRIs working in the US tech sector, the TCS-Anthropic alliance is a reminder that the disruption is not limited to Silicon Valley startups. India's largest IT firms — TCS, Infosys, Wipro, HCL Tech — together employ more than 1.5 million people, and their strategic bets on AI will shape the demand for H-1B workers, the structure of onshore delivery teams and the nature of work itself.

The Indian government has taken note. At VivaTech 2026 in Paris next week, India will be the official AI Partner Country, showcasing deep-tech startups from IIT Madras and other institutions. The pitch is clear: India wants to be an AI producer, not just an AI consumer.

But for the generation of IT workers who expected predictable careers of incremental promotions and onsite postings, the message from TCS and Anthropic is blunter. The industry is moving fast. Those who do not move with it risk being left behind.

## What's Next

TCS has not disclosed the financial terms of the partnership or the timeline for the Claude rollout across its workforce. The company said it would begin with associates working in regulated industries and expand from there.

Anthropic, which confidentially filed its S-1 registration statement with the SEC last week ahead of a potential IPO at a valuation approaching $1 trillion, is rapidly building its enterprise footprint in Asia through partnerships with India's largest outsourcers.

The race is on. For India's IT sector, the question is no longer whether AI will change the business — it is whether the business can change fast enough."""

    return {
        "headline": "TCS Just Partnered With Anthropic. Fifty Thousand Indian IT Workers Are Getting an AI Co-Pilot.",
        "subheadline": "India's largest IT exporter is betting on an AI alliance that signals the end of brute-force hiring — and the beginning of something riskier.",
        "body": body,
        "slug": "tcs-anthropic-partnership-claude-50000-workers-india-it-sector-20260611",
        "category": "news",
        "image_url": image_url,
        "image_caption": "Tata Consultancy Services headquarters — India's largest IT exporter",
        "image_attribution": attribution or "",
        "sources": ["Reuters", "TCS Annual General Meeting 2026", "Anthropic SEC Filing"]
    }


# ══════════════════════════════════════════════════════════════════
# ARTICLE 2: India Fertiliser Subsidy Doubles
# ══════════════════════════════════════════════════════════════════
def article_fertiliser_subsidy():
    print("\n═══ Article 2: Fertiliser Subsidy Doubles ═══")
    commons = fetch_wikimedia_commons("India agriculture fertilizer")
    commons2 = fetch_wikimedia_commons("Indian farming urea field")
    pexels = fetch_pexels("India agriculture farming field")
    image_url, attribution = best_image(commons + commons2, pexels)

    body = """India's fertiliser ministry has requested a doubling of its budgeted subsidy allocation for the current fiscal year, barely three months into the spending cycle — a striking admission that the economic fallout from the Iran war is far exceeding what New Delhi had anticipated.

The demand, confirmed by a senior government official to Reuters, comes as India's oil-and-gas import bill surged 53 per cent in April compared to March, and the government has already spent 1.2 trillion rupees ($12.6 billion) compensating oil refiners and retailers for holding down fuel prices during the first 78 days of the conflict.

"Department of fertiliser has already asked for doubling of fertiliser subsidy with barely three months into the financial year," the official said. "We are ramping up domestic capacity to reduce imports."

## Supply Chains Under Pressure

India is one of the world's largest importers of fertilisers, including urea and di-ammonium phosphate, as well as liquefied natural gas — a key feedstock for urea production. The country also imports roughly 90 per cent of its crude oil, making it among the most exposed nations to prolonged disruptions in global energy supply chains.

The war, which began on February 28 with the US-Israeli strikes on Iran, has sent benchmark international oil prices surging to nearly $120 per barrel. While prices have eased somewhat, they remain about 30 per cent higher overall. Natural gas prices have risen 75 per cent over the same period.

For Indian farmers, the calculus is simple: fertiliser prices are set by the government, but the cost of producing and importing that fertiliser has risen sharply. The subsidy covers the gap. When the gap doubles, so does the bill.

## The Fiscal Ledger

The fertiliser demand is just one line item in what is becoming a much larger fiscal burden. India's balance of payments deficit was $25.2 billion in 2025-26, or 0.6 per cent of GDP. HSBC had forecast it could balloon to $65 billion in 2026-27 before the Reserve Bank of India announced a series of measures on June 6 to encourage foreign inflows and defend the rupee.

Those measures — which include bearing the full hedging cost on three- to five-year non-resident Indian deposits and scrapping capital gains tax on foreign portfolio investments in government securities — may improve the balance by about $30 billion, according to HSBC estimates.

The rupee, Asia's second-worst-performing currency this year with a 6 per cent decline, slipped to record lows in May. The Reserve Bank sees inflation averaging 5.1 per cent this fiscal year, up from 3.48 per cent in April, and economic growth slowing to 6.6 per cent from 7.7 per cent in the previous year.

Interest rate swap markets are pricing in at least 25 basis points of rate hikes over the next three months — and more than 75 basis points over the next year.

## The Government's Response

Beyond the financial measures, India has moved to curb gold imports, urged citizens to limit foreign travel and called for greater use of public transport to reduce oil demand. The government has also ordered domestic petrochemical producers to divert output to making LPG — primarily used as cooking gas — and is considering extending import tax exemptions on 40 petrochemical products beyond their June 30 expiry date.

Despite the spiralling costs, the government insists it will not pull back on capital expenditure. "We do not see economic growth under stress yet due to strong domestic consumption," the official said.

Portfolio managers are less sanguine. "India continues to face deeper structural challenges which has weighed on foreign direct investment, employment, manufacturing expansion, consumption, and nominal GDP growth," said Sat Duhra, portfolio manager on the Asia ex-Japan equity team at Janus Henderson Investors. "The energy shock will undermine growth and pressure government finances."

Any move to rein in public-sector capex to stabilise conditions, Duhra warned, would risk further slowing growth — leaving policymakers in what he called "a difficult position."

## What It Means for NRIs

For the Indian diaspora, the economic squeeze is arriving through multiple channels at once. The rupee's decline erodes the value of remittances sent home. Rising inflation threatens the purchasing power of family members in India. And the interest rate outlook suggests that anyone with a home loan in India is about to pay more.

The silver lining is that the government's push to attract NRI deposits — with rates now reaching 7 per cent on dollar-denominated fixed deposits — creates an opportunity for those holding foreign currency. Banks including HDFC Bank, State Bank of India, AU Small Finance Bank and Yes Bank have all hiked rates since the RBI eased hedging restrictions last week.

Lenders could raise as much as $35 billion to $40 billion via these foreign currency deposits by September, according to Reuters estimates. The RBI has also opened the door for banks to guarantee offshore loans to NRIs who then place the borrowed funds as deposits.

But that opportunity exists precisely because India needs dollars badly. A country doubling its fertiliser subsidy three months into the fiscal year is a country that knows the worst may not be over."""

    return {
        "headline": "India's Fertiliser Bill Has Doubled in Three Months. The Iran War Is Draining the Treasury.",
        "subheadline": "The fertiliser ministry has asked to double its annual subsidy barely a quarter into the fiscal year — the starkest sign yet that the war's economic toll is reshaping India's books.",
        "body": body,
        "slug": "india-fertiliser-subsidy-doubles-iran-war-oil-rupee-fiscal-20260611",
        "category": "news",
        "image_url": image_url,
        "image_caption": "Indian agriculture — the sector at the heart of the government's ballooning subsidy bill",
        "image_attribution": attribution or "",
        "sources": ["Reuters", "HSBC Research", "Reserve Bank of India", "Janus Henderson Investors"]
    }


# ══════════════════════════════════════════════════════════════════
# ARTICLE 3: Telangana Student Anshul Kuncha
# ══════════════════════════════════════════════════════════════════
def article_anshul_kuncha():
    print("\n═══ Article 3: Anshul Kuncha — Philadelphia ═══")
    commons = fetch_wikimedia_commons("Philadelphia Pennsylvania skyline")
    commons2 = fetch_wikimedia_commons("North Philadelphia neighborhood")
    pexels = fetch_pexels("Philadelphia city skyline night")
    image_url, attribution = best_image(commons + commons2, pexels)

    body = """Anshul Kuncha left his apartment on a Friday night to deliver pizza. He never came home.

The 28-year-old from Gundlapochampally in Telangana's Medchal-Malkajgiri district was found lying in the courtyard of the Raymond Rosen Homes housing complex in North Philadelphia shortly after midnight on June 6, bleeding heavily from a gunshot wound to the head. Three spent shell casings were recovered inches from his body. Inside the apartment he had been sent to, police found three untouched pizza boxes and a delivery bag.

The apartment was vacant. No one had ordered the food.

"It was a trap," his sister Tanvi told Indian media. "There was no customer. He was deliberately called there to be killed."

## What Happened

Kuncha, who had lived in Philadelphia for nearly four years, was pursuing an MBA — reported to be at either Temple University or Drexel University — while working full-time at a multinational company. On weekends, he delivered pizzas for Pete's Pizza to supplement his income.

On the night of June 5, he received a delivery order for an address at the Raymond Rosen Homes complex on the 2300 block of Edgley Street. He drove there, carried the pizza boxes inside, and was followed.

Surveillance cameras operated by the Philadelphia Housing Authority captured two individuals in dark clothing trailing Kuncha after he entered the complex. One was carrying a dark backpack. The shooting itself was not caught on camera.

Philadelphia Police Chief Inspector Scott Small said the shell casings indicated that the shooter or shooters stood "very close to the victim." Kuncha's delivery vehicle was found nearby, with a pizza warmer still inside.

Police have not made any arrests. But investigators have traced the phone number used to place the order, which Small described as an "important lead."

## Nothing Was Stolen

The detail that has most troubled Kuncha's family — and the broader Indian community — is that nothing was taken. No wallet. No phone. No cash. The pizzas were untouched. If this was a robbery, it was one where the perpetrators left everything behind.

Tanvi Kuncha said her brother had been robbed once before while living in the US, losing his phone, a chain and cash. But he had never faced anything like this.

"He was kind-hearted. He never had any issues or fights with anyone, ever," said his brother Romit, speaking from Haryana. The two had spoken by phone that morning. Anshul had sounded happy.

## A Pattern of Violence

Kuncha's killing is the latest in a distressing series of violent incidents targeting Indian nationals in the United States. In recent months, Indian students and gig workers have faced robberies, assaults and fatal attacks across American cities. The incidents have fueled deep anxiety among a diaspora community that numbers more than 4.4 million people.

On social media and community forums, many have questioned whether Kuncha was targeted specifically because he was an immigrant — an isolated worker delivering food late at night in an unfamiliar neighbourhood. Others have pointed out that gig economy workers of all backgrounds face heightened risk, and that the absence of a clear motive makes speculation premature.

The Indian Consulate in New York said it was in contact with local authorities and the Kuncha family, and was extending all possible assistance. The family has appealed for the swift repatriation of his body to India so that final rites can be performed without delay.

## The Gig Economy's Hidden Cost

The story of Anshul Kuncha is, in part, the story of the gig economy's invisible underclass. He was a qualified professional — an MBA student at a respected university, employed at a multinational company — who still needed to deliver pizzas on weekends to make ends meet.

Thousands of Indian students across the United States find themselves in the same position: working delivery shifts, driving rideshares and picking up freelance gigs to cover tuition, rent and living costs that far outstrip what campus jobs or stipends provide. The hours are late, the neighbourhoods are unfamiliar, and the work puts them in situations where they are alone, carrying cash or goods, and visibly vulnerable.

For the families back home who sent their children abroad with the expectation of safety and opportunity, Kuncha's death is a shattering reminder that neither is guaranteed.

Philadelphia police have asked anyone with information to contact their tip line. No arrests have been made."""

    return {
        "headline": "A Telangana Student Delivered Pizza to a Vacant Apartment in Philadelphia. He Was Dead Within Minutes.",
        "subheadline": "Anshul Kuncha, 28, was lured to an empty housing complex by what his family calls a deliberate trap. Nothing was stolen. No arrests have been made.",
        "body": body,
        "slug": "anshul-kuncha-telangana-student-shot-philadelphia-pizza-delivery-trap-20260611",
        "category": "news",
        "image_url": image_url,
        "image_caption": "Philadelphia, Pennsylvania — where Indian MBA student Anshul Kuncha was fatally shot during a pizza delivery",
        "image_attribution": attribution or "",
        "sources": ["Philadelphia Police Department / Chief Inspector Scott Small", "India Today / IANS", "LatestLY", "Beats in Brief"]
    }


# ── Main ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("Videshi News Writer — June 11, 2026 (batch 2)")
    print("=" * 60)

    results = []
    for fn in [article_tcs_anthropic, article_fertiliser_subsidy, article_anshul_kuncha]:
        article = fn()
        if not article.get("image_url"):
            print(f"  ⚠ No image for {article['slug']} — inserting without")
        success = insert_article(article)
        results.append((article["slug"], success))

    print("\n" + "=" * 60)
    print("RESULTS:")
    for slug, ok in results:
        print(f"  {'✓' if ok else '✗'} {slug}")
    print("=" * 60)
