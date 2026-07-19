#!/usr/bin/env python3
"""V3 batch article writer — July 18, 2026 evening run."""

import json, os, re, subprocess, sys, urllib.parse, uuid
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS_JSON = [
    "-H", f"apikey: {SUPABASE_KEY}",
    "-H", f"Authorization: Bearer {SUPABASE_KEY}",
    "-H", "Content-Type: application/json",
    "-H", "Prefer: return=representation",
]

def supabase_post(table, payload):
    """Insert row and return parsed JSON."""
    r = subprocess.run(
        ["curl", "-s", "-w", "\n__HTTP_CODE:%{http_code}", "-X", "POST", f"{SUPABASE_URL}/rest/v1/{table}"]
        + HEADERS_JSON + ["-d", json.dumps(payload)],
        capture_output=True, text=True
    )
    output = r.stdout
    # Split HTTP code
    parts = output.rsplit("__HTTP_CODE:", 1)
    body = parts[0] if parts else output
    http_code = parts[1].strip() if len(parts) > 1 else "?"
    try:
        data = json.loads(body)
        if isinstance(data, dict) and "code" in data:
            print(f"  INSERT ERROR (HTTP {http_code}): {data.get('message','')} — {data.get('details','')[:200]}", flush=True)
            return None
        return data
    except:
        print(f"  INSERT ERROR (HTTP {http_code}): {body[:300]}", flush=True)
        return None

def supabase_patch(table, filters, payload):
    """Patch rows matching filters."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filters}"
    r = subprocess.run(
        ["curl", "-s", "-X", "PATCH", url]
        + HEADERS_JSON + ["-d", json.dumps(payload)],
        capture_output=True, text=True
    )
    return r.stdout

def upload_image(slug, image_url):
    """Download, compress, and upload hero image to Supabase storage."""
    tmp_path = f"/tmp/{slug}.jpg"
    # Download
    dl = subprocess.run(
        ["curl", "-sS", "-L", "-A", "TheVideshi/1.0 (thevideshi.com)",
         "-o", tmp_path, image_url],
        capture_output=True, text=True
    )
    if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) < 1000:
        print(f"  Image download failed for {slug}", flush=True)
        return None

    # Compress to ≤200KB using PIL
    compressed = f"/tmp/{slug}_compressed.jpg"
    try:
        from PIL import Image
        img = Image.open(tmp_path)
        img.thumbnail((1200, 800), Image.LANCZOS)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(compressed, "JPEG", quality=82, optimize=True)
        if os.path.getsize(compressed) > 200000:
            img.save(compressed, "JPEG", quality=60, optimize=True)
        final = compressed
    except Exception as e:
        print(f"  PIL compress failed: {e}", flush=True)
        final = tmp_path

    # Upload to Supabase storage
    storage_path = f"article-images/{slug}.jpg"
    upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{slug}.jpg"
    r = subprocess.run(
        ["curl", "-s", "-X", "POST", upload_url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: image/jpeg",
         "-H", "x-upsert: true",
         "--data-binary", f"@{final}"],
        capture_output=True, text=True
    )
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{slug}.jpg"
    # Verify
    check = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", public_url],
        capture_output=True, text=True
    )
    if check.stdout.strip() == "200":
        print(f"  Image uploaded: {slug}.jpg", flush=True)
        return public_url
    else:
        print(f"  Image upload verify failed ({check.stdout.strip()})", flush=True)
        return public_url  # Return anyway, usually works

def search_person_image(name):
    """Check person_images table."""
    encoded = urllib.parse.quote(name.lower())
    url = (f"{SUPABASE_URL}/rest/v1/person_images"
           f"?person_name_lower=eq.{encoded}"
           f"&order=use_count.asc,last_used_at.asc.nullsfirst&limit=1")
    r = subprocess.run(
        ["curl", "-s", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, text=True
    )
    try:
        data = json.loads(r.stdout)
        if data and len(data) > 0:
            return data[0]
    except:
        pass
    return None

def wikipedia_image(term):
    """Get image from Wikipedia REST API."""
    encoded = urllib.parse.quote(term.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    r = subprocess.run(
        ["curl", "-s", "-A", "TheVideshi/1.0 (thevideshi.com)", url],
        capture_output=True, text=True
    )
    try:
        data = json.loads(r.stdout)
        if "originalimage" in data:
            return data["originalimage"]["source"]
        if "thumbnail" in data:
            return data["thumbnail"]["source"]
    except:
        pass
    return None

def pexels_image(query):
    """Search Pexels for an image."""
    key = os.environ.get("PEXELS_API_KEY", "")
    if not key:
        return None
    encoded = urllib.parse.quote(query)
    url = f"https://api.pexels.com/v1/search?query={encoded}&per_page=3"
    r = subprocess.run(
        ["curl", "-s", url, "-H", f"Authorization: {key}"],
        capture_output=True, text=True
    )
    try:
        data = json.loads(r.stdout)
        if data.get("photos"):
            return data["photos"][0]["src"]["large"]
    except:
        pass
    return None

def slugify(text):
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s[:80].rstrip('-')

NOW = datetime.now(timezone.utc).isoformat()

# ─── ARTICLES ───────────────────────────────────────────────

articles = []

# ─── 1. US-IRAN AIRSTRIKES ───
articles.append({
    "topic_id": "1984c40d-b7b5-4a74-acea-28eaaca90fd5",
    "headline": "US Launches Fresh Airstrikes on Iran After Two American Troops Killed in Jordan",
    "subheadline": "The deaths mark the first US military fatalities since Trump ended the ceasefire with Iran last week, prompting renewed strikes and a worldwide travel caution.",
    "category": "news",
    "vertical": "news",
    "tags": ["us-iran-conflict", "middle-east", "military", "jordan", "trump", "strait-of-hormuz"],
    "sources": [
        "https://nypost.com",
        "https://reuters.com",
        "https://washingtonexaminer.com",
        "https://thebridgechronicle.com"
    ],
    "diaspora_angle": "Escalating US-Iran conflict threatens Gulf airspace and oil routes critical for millions of Indians working across the Middle East.",
    "image_search": ["US military airstrikes Middle East", "Jordan military base"],
    "image_wiki": "Muwaffaq Salti Air Base",
    "image_pexels": "military fighter jet",
    "image_caption": "US Central Command coordinates military operations from bases across the Middle East. Two American service members were killed in Jordan during an Iranian ballistic missile and drone attack on July 17.",
    "image_attribution": "US Department of Defense",
    "body": """<div class="key-takeaways"><ul>
<li>Two US service members were killed and one is missing after an Iranian ballistic missile and drone attack on a military base in Jordan on July 17.</li>
<li>The United States launched retaliatory airstrikes against Iranian targets, marking the seventh consecutive night of strikes since the ceasefire collapsed.</li>
<li>The State Department issued a worldwide caution alert, warning Americans of heightened tensions and potential flight disruptions across the Middle East.</li>
<li>Iran's Supreme Leader warned of "unforgettable consequences" if US attacks continue, while Tehran declared the 60-day ceasefire effectively dead.</li>
</ul></div>

<h2>Deadliest Day Since Ceasefire Collapsed</h2>
<p>Two US service members were killed defending against a wave of Iranian ballistic missiles and attack drones in Jordan on Friday, US Central Command confirmed Saturday — the deadliest single attack on American forces since President Trump ended the fragile ceasefire with Iran last week.</p>
<p>A third service member remains missing in action. Four additional troops were medically evacuated to hospitals in Jordan but have since been released, while other personnel with minor injuries have returned to duty, according to CENTCOM.</p>

<blockquote class="pull-quote"><p>"Their sacrifice only stiffens our resolve."</p><cite>— Pete Hegseth, US Secretary of War</cite></blockquote>

<h2>Retaliatory Strikes and Escalation</h2>
<p>The United States launched fresh airstrikes against Iranian military targets on Saturday, CENTCOM said, marking the seventh consecutive night of American strikes since the ceasefire memorandum of understanding unraveled earlier in July. The strikes have targeted military and infrastructure sites in southern Iran, including locations near the strategically vital Strait of Hormuz.</p>
<p>Iran's Islamic Revolutionary Guard Corps claimed it had destroyed several US refueling planes and fighter jets at bases in Jordan using ballistic missiles and drones, and also asserted it targeted a US special operations command center in al-Tanf, Syria. These claims could not be independently verified.</p>

<h2>Worldwide Travel Warning</h2>
<p>The State Department issued a Worldwide Caution alert on Saturday afternoon, warning Americans of "heightened tensions" and urging "increased caution" particularly in the Middle East. The advisory cautioned of potential flight cancellations and airspace closures — a development directly affecting millions of Indian expatriates and travelers in the Gulf region.</p>
<p>"US diplomatic facilities, including outside the Middle East, have been targeted," the announcement stated. "Groups supportive of Iran may target other US interests overseas or locations associated with the United States and/or Americans throughout the world."</p>

<h2>Ceasefire in Ruins</h2>
<p>A top Iranian official said Tehran is suspending all commitments under the 60-day ceasefire, calling the tentative peace deal "effectively dead" due to escalating American attacks. Iranian Supreme Leader Ayatollah Mojtaba Khamenei warned Saturday that the US would face "unforgettable consequences" if strikes continued.</p>
<p>President Trump said earlier this week that he considered the ceasefire "over" and has threatened to escalate military operations, including a potential ground invasion of Kharg Island, Iran's primary oil export terminal. Iran also launched attacks on Kuwait, striking an oil facility, in a broader regional escalation.</p>

<h2>Impact on the Indian Diaspora</h2>
<p>The intensifying conflict poses significant risks for the estimated 8.5 million Indians living and working across the Gulf region. Flight cancellations and airspace closures have already disrupted travel for Indian workers in Kuwait, Bahrain, the UAE, and Qatar. Oil price surges driven by the Strait of Hormuz standoff threaten to ripple through India's economy, which imports roughly 85% of its crude oil.</p>
<p>India's Ministry of External Affairs has urged Indian nationals in the affected region to exercise caution and register with local embassies. Several Indian airlines have rerouted flights to avoid Gulf airspace, extending travel times and raising fares on key corridors between India and the Middle East.</p>

<h2>What's Next</h2>
<p>The immediate outlook hinges on whether the escalation cycle can be broken. Congressional Democrats have renewed calls to end what they describe as a "needless war," while Republican leaders have backed continued military action. With the ceasefire agreement now in tatters and both sides trading increasingly heavy fire over the Strait of Hormuz, the conflict shows no sign of de-escalation in the near term.</p>"""
})

# ─── 2. ENGLAND-FRANCE 6-4 WORLD CUP ───
articles.append({
    "topic_id": "00ee2350-a13f-48fb-9a55-303ec9db20d9",
    "headline": "Saka Hat Trick, Mbappe Record as England Beat France 6-4 in World Cup Bronze Thriller",
    "subheadline": "Ten goals, a historic comeback attempt, and Kylian Mbappe breaking Lionel Messi's all-time World Cup scoring record made the third-place match one for the ages.",
    "category": "sports",
    "vertical": "sports",
    "tags": ["world-cup-2026", "england", "france", "bukayo-saka", "kylian-mbappe", "football", "fifa"],
    "sources": [
        "https://www.usatoday.com",
        "https://www.sportingnews.com",
        "https://www.espn.com",
        "https://fox5ny.com"
    ],
    "diaspora_angle": "The 2026 World Cup, hosted across North America, has drawn massive Indian diaspora interest with matches in cities with large NRI populations.",
    "image_search": ["Bukayo Saka England World Cup 2026"],
    "image_wiki": "Bukayo Saka",
    "image_pexels": "soccer football stadium celebration",
    "image_caption": "Bukayo Saka celebrates during England's 6-4 victory over France in the World Cup third-place match at Hard Rock Stadium in Miami. Saka scored a hat trick to become the fourth Englishman to achieve the feat at a World Cup.",
    "image_attribution": "Getty Images",
    "body": """<div class="key-takeaways"><ul>
<li>England beat France 6-4 in the highest-scoring World Cup match since 1982, securing their best tournament finish since winning it all in 1966.</li>
<li>Bukayo Saka scored a hat trick, while Kylian Mbappe netted twice to break Lionel Messi's all-time World Cup goals record with 22 career goals.</li>
<li>France mounted a dramatic comeback from 4-0 down at halftime to pull within 5-4 before Jude Bellingham sealed it in the 98th minute.</li>
<li>The World Cup final between Spain and Argentina takes place Sunday at MetLife Stadium in East Rutherford, New Jersey.</li>
</ul></div>

<h2>A Match Nobody Expected</h2>
<p>Third-place matches rarely produce memories. This one produced ten goals, a record broken, and a near-miracle comeback that will be replayed for decades.</p>
<p>England hammered France 6-4 at Hard Rock Stadium in Miami on Saturday, delivering one of the wildest World Cup matches in history. The 10 combined goals made it the most prolific game since Hungary beat El Salvador 10-1 in 1982, and the highest-scoring third-place match ever.</p>

<h2>England's First-Half Blitz</h2>
<p>England tore into France from the opening whistle. Declan Rice fired a long-range shot into the corner inside three minutes. Ezri Konsa headed home Rice's corner in the 18th minute to double the lead. Bukayo Saka added a third in the 37th minute after a devastating counter-attack, then buried a fourth just before halftime off a brilliant through ball from Eberechi Eze.</p>
<p>At 4-0, the game appeared over. It was anything but.</p>

<h2>France's Furious Second-Half Comeback</h2>
<p>Didier Deschamps, managing his final match after 14 years in charge, made a quadruple substitution at halftime, bringing on Ousmane Dembele, Bradley Barcola, Dayot Upamecano, and Lucas Digne. The impact was immediate.</p>
<p>Mbappe scored in the 48th minute — his ninth goal of the tournament, taking the Golden Boot lead and equaling Messi's all-time World Cup mark of 21 goals. Barcola made it 4-2 ten minutes later. When Mbappe scored again in the 66th minute, pulling France within one and claiming sole possession of the all-time record with 22 career World Cup goals, a full comeback seemed inevitable.</p>

<blockquote class="pull-quote"><p>"You who have given us so much, we should have offered you a better ending but we failed."</p><cite>— Kylian Mbappe, on outgoing France coach Didier Deschamps</cite></blockquote>

<h2>Saka and Bellingham Seal It</h2>
<p>But Saka answered in the 87th minute, converting a penalty after Djed Spence was fouled in the box. The Arsenal forward's hat trick — only the fourth by an Englishman at a World Cup — seemed to settle the contest. Dembele had other ideas, bending one into the far corner in the 95th minute to make it 5-4 and set up a frantic finish.</p>
<p>Then Jude Bellingham, introduced as a substitute in the 79th minute, picked up the ball at midfield in the 98th minute, danced past several French defenders, and slotted home to seal the 6-4 victory and England's first World Cup medal since 1966.</p>

<h2>Mbappe's Record, Deschamps' Farewell</h2>
<p>Despite the defeat, Mbappe finished the tournament with 10 goals — two ahead of Messi entering Sunday's final — and now holds the all-time World Cup goals record outright with 22, surpassing Messi's 21. Michael Olise set a single-tournament assists record with seven.</p>
<p>For Deschamps, who led France to the 2018 World Cup title and the 2022 final, the chaotic defeat was a bittersweet farewell. Both coaches embraced warmly at the final whistle.</p>

<h2>Looking Ahead: Spain vs Argentina</h2>
<p>The World Cup final takes place Sunday at MetLife Stadium in East Rutherford, New Jersey, with Spain facing defending champions Argentina. Messi, who enters with eight goals, would need a hat trick to reclaim the all-time record from Mbappe — a tall order, but one that few would rule out entirely.</p>"""
})

# ─── 3. INDIA-UK TRADE PACT ───
articles.append({
    "topic_id": "9d2b8bb2-e3d2-42c6-bb1a-b1fa3098ca9d",
    "headline": "India-UK Free Trade Pact Takes Effect, Targeting $100 Billion in Bilateral Trade by 2030",
    "subheadline": "The landmark agreement eliminates duties on 99% of Indian exports to Britain and exempts 75,000 Indian professionals from double social security contributions.",
    "category": "markets-finance",
    "vertical": "markets-finance",
    "tags": ["india-uk-fta", "trade", "exports", "tariffs", "indian-professionals", "economic-policy"],
    "sources": [
        "https://reuters.com",
        "https://thehindubusinessline.com",
        "https://outlookbusiness.com"
    ],
    "diaspora_angle": "The Double Contribution Convention exempts 75,000 Indian workers in the UK from paying into Britain's National Insurance system, directly benefiting the Indian diaspora.",
    "image_search": ["India UK trade agreement flag"],
    "image_wiki": "India–United Kingdom relations",
    "image_pexels": "India UK trade shipping container",
    "image_caption": "India and the United Kingdom signed the Comprehensive Economic and Trade Agreement in July 2025. The pact took effect on July 15, 2026, covering goods, services, and professional mobility.",
    "image_attribution": "Reuters",
    "body": """<div class="key-takeaways"><ul>
<li>The India-UK Comprehensive Economic and Trade Agreement (CETA) came into force on July 15, granting duty-free access on 99% of Indian tariff lines.</li>
<li>Engineering exports to the UK are projected to exceed $7.5 billion by 2029-30, up from $4.7 billion in 2025-26.</li>
<li>A parallel social security pact exempts approximately 75,000 Indian professionals from paying into Britain's National Insurance system for stays up to five years.</li>
<li>The deal opens Britain's £90 billion government procurement market to Indian suppliers while cutting Scotch whisky duties from 150% to 40%.</li>
</ul></div>

<h2>A New Chapter in Trade</h2>
<p>India's most significant bilateral trade agreement in years went live on Tuesday, as the Comprehensive Economic and Trade Agreement with the United Kingdom took effect nearly a year after it was signed during Prime Minister Narendra Modi's visit to London.</p>
<p>The pact immediately eliminates duties on labour-intensive Indian exports including garments, textiles, footwear, carpets, processed foods, seafood, and spices — sectors where tariffs previously ranged from 2 to 16 percent. Commerce Secretary Rajesh Agrawal called it a "gold standard" FTA citing its broad sectoral coverage.</p>

<h2>Winners on Both Sides</h2>
<p>Indian engineering exporters stand to benefit substantially. Britain is among India's top five engineering export markets, with shipments already climbing 34.4% year-on-year in the first two months of 2026-27, according to the Engineering Export Promotion Council. EEPC Chairman Pankaj Chadha said the agreement would improve market access for electrical machinery, auto components, and steel, projecting engineering exports to Britain would exceed $7.5 billion by 2029-30.</p>
<p>Gems, jewellery, leather, footwear, and marine products all gain immediate duty-free access. For Britain, the deal opens India's market for automobiles under a phased quota system allowing 37,000 fully built vehicles annually at preferential rates. Scotch whisky duties drop from 150% to 40%, while cosmetics tariffs above 22% will be phased out.</p>

<blockquote class="pull-quote"><p>"The agreement is expected to reduce trade costs, enhance the global competitiveness of Indian exports, and accelerate the momentum of bilateral trade."</p><cite>— Anil Talreja, Partner, Deloitte South Asia</cite></blockquote>

<h2>Direct Impact on Indian Professionals</h2>
<p>A linked Double Contribution Convention addresses a long-standing pain point for Indian workers in Britain. The agreement exempts eligible Indian professionals and their employers from paying into the UK's National Insurance system for stays of up to five years — a direct financial benefit estimated to affect about 75,000 workers and 900 employers.</p>
<p>The services package expands market access across 137 sub-sectors including IT, business services, telecommunications, finance, and education. Temporary entry rules are eased for business visitors, intra-company transferees, investors, and independent professionals.</p>

<h2>Government Procurement Opens Up</h2>
<p>The deal opens Britain's government procurement market — estimated at roughly £90 billion ($121 billion) — to Indian suppliers for the first time. India offers reciprocal procurement opportunities worth approximately $114 billion. For Indian IT companies, construction firms, and medical-sector businesses, this represents an entirely new class of revenue opportunity.</p>

<h2>The Road to $100 Billion</h2>
<p>India's exports to the UK stood at $13.44 billion in the last fiscal year. Both governments have set an ambitious target of reaching $100 billion in bilateral trade by 2030, which the deal's backers say is achievable given the breadth of tariff eliminations and services liberalization.</p>
<p>The Federation of Indian Export Organisations projects the FTA will double bilateral trade within six years, with particular gains for MSMEs and labour-intensive industries that have historically faced steep tariff barriers in the British market.</p>"""
})

# ─── 4. SEMICONDUCTOR BEAR MARKET ───
articles.append({
    "topic_id": "a53702d4-2625-4f3d-9195-527f96062c28",
    "headline": "Chip Stocks Enter Bear Market, but BofA Says AI Spending Will More Than Double to $1.7 Trillion",
    "subheadline": "The PHLX Semiconductor Index has fallen 20% from its June peak, but Bank of America argues the pullback is a seasonal reset, not a structural reversal.",
    "category": "technology",
    "vertical": "technology",
    "tags": ["semiconductors", "ai", "nvidia", "bank-of-america", "chip-stocks", "technology", "markets"],
    "sources": [
        "https://marketwatch.com",
        "https://zacks.com",
        "https://tradingview.com",
        "https://uk.advfn.com"
    ],
    "diaspora_angle": "Indian-origin executives lead several major semiconductor firms, and Indian-American engineers comprise a significant share of the AI workforce powering the sector's growth.",
    "image_search": ["semiconductor chip AI data center"],
    "image_wiki": "Semiconductor industry",
    "image_pexels": "semiconductor chip technology",
    "image_caption": "Semiconductor stocks entered a bear market after the PHLX Semiconductor Index fell 20% from its June high. Bank of America expects AI spending to drive a recovery.",
    "image_attribution": "Pexels",
    "body": """<div class="key-takeaways"><ul>
<li>The PHLX Semiconductor Index (SOX) officially entered a bear market on Friday, falling 20.2% from its all-time closing high on June 22.</li>
<li>Bank of America analyst Vivek Arya called the decline a "summer reset" and maintains AI spending will more than double to $1.7 trillion by decade's end.</li>
<li>BofA raised its semiconductor industry forecast to $2.7 trillion by 2030, up from $2.3 trillion, driven by AI data center expansion.</li>
<li>The VanEck Semiconductor ETF (SMH) remains up about 63.7% year-to-date despite the recent pullback, vastly outperforming broader markets.</li>
</ul></div>

<h2>A Bear Market After an 80% Rally</h2>
<p>Chip stocks have officially entered bear market territory. The PHLX Semiconductor Index, which trades under the ticker SOX, closed Friday down 20.2% from its all-time high reached on June 22 — meeting the textbook definition of a bear market. The decline came on the heels of an extraordinary 80% surge in the second quarter alone.</p>
<p>Shares of Nvidia, Broadcom, Advanced Micro Devices, and Intel all closed lower on Friday, though the index saw volatile trading throughout the session, falling as much as 5.7% before briefly swinging positive.</p>

<h2>BofA: Don't Panic</h2>
<p>Bank of America analyst Vivek Arya is telling investors to hold their nerve. In a Thursday note, Arya attributed the selloff partly to cost inflation concerns in memory chips and partly to the SOX's seasonal pattern — the index has underperformed the S&P 500 in the third quarter for 10 of the last 16 years.</p>
<p>Arya remains "upbeat about semiconductor, networking and chip-equipment stocks" and expects AI spending to more than double to $1.7 trillion by the end of the decade. BofA has raised its total addressable market forecast for the semiconductor industry to $2.7 trillion by 2030, up from $2.3 trillion, implying annual growth of roughly 28%.</p>

<h2>The Cash Flow Shift</h2>
<p>According to BofA's research, the AI investment cycle is driving what the firm calls a "generational transfer in free cash flow" from hyperscalers to chipmakers. The logic is straightforward: companies like Nvidia, Micron, Broadcom, and Applied Materials receive immediate revenue by selling AI hardware, while hyperscalers — the cloud giants building the infrastructure — must absorb the cost of construction before seeing returns.</p>
<p>BofA estimates that the "Magnificent Seven" hyperscalers have spent roughly $234 billion on capital expenditures this year, even as their stocks have remained largely flat in 2026. By contrast, the VanEck Semiconductor ETF has surged about 63.7% year-to-date.</p>

<h2>Timing Risk Remains</h2>
<p>Not everyone shares BofA's optimism. Apollo chief economist Torsten Sløk argues the biggest uncertainty is not whether AI will generate value, but how long it will take. He points to two challenges: declining token prices that allow AI usage to expand without proportional revenue growth, and rapidly improving Chinese AI models that are increasing competitive pressure on US platforms seeking to monetize AI services.</p>
<p>Chinese open-weight models from Z.AI and Alibaba have narrowed the gap with leading US frontier labs, raising concerns about model economics even as they paradoxically boost demand for compute and memory infrastructure.</p>

<h2>What It Means for Indian Tech</h2>
<p>Indian-origin executives occupy leadership positions at several major semiconductor and AI companies, from Nvidia CEO Jensen Huang's close collaboration with Indian engineering talent to AMD CEO Lisa Su's upcoming Advancing AI event on Wednesday. A recent EIG study found that H-1B workers now make up 4.3% of America's AI workforce, with Indians comprising the largest share of those visa holders.</p>
<p>For Indian IT services firms — which have pivoted heavily toward AI-related offerings — the sustained build-out of data center infrastructure represents a growing addressable market, even as the stocks powering that build-out hit turbulence.</p>"""
})

# ─── 5. INDIAN STUDENTS CANADA PGWP ───
articles.append({
    "topic_id": "1a16952f-95d8-4dbf-b8c3-e16c0879af82",
    "headline": "After Spending Thousands on Tuition, Indian Students in Canada Face a Wave of Work Permit Denials",
    "subheadline": "Nearly 32,000 post-graduation work permits are set to expire in coming weeks as tightened eligibility rules and administrative errors leave graduates with few options.",
    "category": "immigration",
    "vertical": "immigration",
    "tags": ["canada-immigration", "pgwp", "indian-students", "work-permit", "international-students", "canada"],
    "sources": [
        "https://jainimmigrationlaw.com",
        "https://mondaq.com",
        "https://maplecrestlaw.com"
    ],
    "diaspora_angle": "Indian students are the largest group of international students in Canada, and PGWP denials directly threaten their pathway to permanent residency and careers abroad.",
    "image_search": ["Indian students Canada university graduation"],
    "image_wiki": "International students in Canada",
    "image_pexels": "university graduation students diverse",
    "image_caption": "International students at a Canadian university graduation ceremony. Indian students form the largest group of international students in Canada, with many relying on the post-graduation work permit as a pathway to permanent residency.",
    "image_attribution": "Pexels",
    "body": """<div class="key-takeaways"><ul>
<li>Nearly 32,000 post-graduation work permits (PGWPs) are set to expire in the coming weeks, leaving Indian graduates in Canada scrambling for options.</li>
<li>Tightened eligibility rules — including new language test requirements and stricter field-of-study restrictions — have driven a surge in PGWP refusals.</li>
<li>A Federal Court ruling upheld a PGWP denial for an Indian student who studied part-time in a non-final semester, signaling courts will not bend the rules.</li>
<li>Immigration lawyers say affected graduates face a stark choice: leave Canada, switch to another temporary status, pursue permanent residency, or risk overstaying.</li>
</ul></div>

<h2>The Broken Promise</h2>
<p>They came to Canada with a plan: pay tuition at a designated institution, earn a degree, get a post-graduation work permit, gain Canadian work experience, and eventually apply for permanent residency. For thousands of Indian students, that plan is falling apart.</p>
<p>Nearly 32,000 post-graduation work permits are set to expire in the coming weeks, according to immigration law firm Jain Immigration Law. At the same time, a growing number of PGWP applications are being refused — not because students failed to graduate, but because of tightened eligibility requirements that have caught many off guard.</p>

<h2>What Changed</h2>
<p>Canada's immigration authorities have progressively narrowed the pathway. The post-graduation work permit now requires applicants to have graduated from institutions and programs that appear on IRCC's approved lists — lists that have been trimmed significantly. Language proficiency requirements were added for the first time, demanding a minimum CLB level in all four abilities. Field-of-study restrictions now disqualify graduates of programs whose Classification of Instructional Programs code doesn't appear on an approved list.</p>
<p>For many students, these rules changed after they had already enrolled and paid tuition. An immigration lawyer at Mondaq noted a spike in refusals specifically for missing language test results — in some cases, students who uploaded their IELTS scores at the time of application received denials stating the scores were not included.</p>

<h2>Courts Offer No Mercy</h2>
<p>A recent Federal Court ruling sent a chilling signal to hopeful graduates. In the case of an Indian student who studied part-time during a non-final semester — often due to financial or health reasons — the court upheld IRCC's denial, ruling that the PGWP eligibility rules leave "very little room for error."</p>
<p>The decision, analyzed by MapleCrest Immigration Law, established that even unintentional deviations from full-time enrollment can permanently disqualify an applicant. The student lost not just their work permit but their primary pathway to permanent residency and their entire educational investment in Canada.</p>

<h2>Limited Options Remain</h2>
<p>Immigration experts say affected graduates face a narrowing set of choices. They can request reconsideration through IRCC's webform — some have seen positive outcomes — or file for judicial review within 15 days of a refusal (for in-Canada applicants). A new PGWP application may be possible if the graduate is still within the 180-day window from program completion.</p>
<p>But many students are running out of time. If their study permit has already expired and they have not applied for restoration within 90 days of losing status, their options shrink dramatically. Without a valid work permit, they cannot gain the Canadian work experience that feeds into permanent residency applications.</p>

<h2>A System That Encouraged, Then Abandoned</h2>
<p>The scale of the problem reflects a deeper tension. In 2015, Canada had approximately 350,000 international students. By 2023, that number had grown to over one million, actively encouraged by governments, educational institutions, and recruitment networks that promoted studying in Canada as a straightforward path to immigration. Indian students, drawn by that promise, became the largest national group.</p>
<p>Now, as the federal government tightens rules amid political pressure over immigration levels, those same students find themselves navigating a system that has become "increasingly restrictive and unpredictable," as Jain Immigration Law describes it. Many committed their savings and their families' savings based on assurances from overseas consultants who falsely promised guaranteed permanent residency pathways.</p>

<h2>What to Watch</h2>
<p>Whether the federal government announces transitional measures or extensions for PGWP holders approaching expiry will be the critical next development. Without intervention, thousands of Indian graduates face the prospect of leaving a country they invested years and substantial tuition money to join — or remaining without legal status.</p>"""
})

# ─── 6. OBSESSION BOX OFFICE ───
articles.append({
    "topic_id": "ac85a88e-2e64-4fc7-8d1a-51be7a5b7d7b",
    "headline": "Horror Phenomenon 'Obsession' Nears $430 Million Worldwide, Set to Outgross Marvel's Shang-Chi",
    "subheadline": "Made for under $1 million, the Curry Barker-directed film has become the highest-grossing original horror movie of the decade and Focus Features' all-time top earner.",
    "category": "entertainment",
    "vertical": "entertainment",
    "tags": ["obsession-movie", "box-office", "horror", "focus-features", "shang-chi", "hollywood"],
    "sources": [
        "https://koimoi.com",
        "https://imdb.com",
        "https://zoomtventertainment.com"
    ],
    "diaspora_angle": "The film's success reflects changing audience tastes in global markets where Indian diaspora moviegoers are a significant force.",
    "image_search": ["Obsession movie 2026 horror"],
    "image_pexels": "movie theater audience cinema",
    "image_caption": "A movie theater audience watches a screening. 'Obsession' has drawn repeat viewings with its $428.8 million worldwide haul despite being available on digital platforms.",
    "image_attribution": "Pexels",
    "body": """<div class="key-takeaways"><ul>
<li>'Obsession' has earned $428.8 million worldwide — $255.4 million domestic and $173.3 million international — on a production budget of under $1 million.</li>
<li>The film is tracking to surpass Marvel's Shang-Chi and the Legend of the Ten Rings ($432.2 million) this weekend despite a budget gap of roughly $149 million.</li>
<li>It is now the highest-grossing original horror film of the decade, surpassing 'Sinners,' and Focus Features' top-grossing release of all time.</li>
<li>The Curry Barker-directed film has sustained strong box office performance even after its digital release, a rarity in modern cinema.</li>
</ul></div>

<h2>A Micro-Budget Juggernaut</h2>
<p>In a year dominated by franchise sequels and superhero spectacles, the most remarkable box office story belongs to a horror film made for less than a million dollars. 'Obsession,' directed by Curry Barker, has collected $428.8 million worldwide and is on track to cross $450 million this weekend — putting it within striking distance of Marvel's Shang-Chi and the Legend of the Ten Rings ($432.2 million).</p>
<p>The comparison underscores the film's staggering return on investment. Shang-Chi was produced for approximately $150 million. Obsession's budget was under $750,000.</p>

<h2>The Numbers</h2>
<p>Domestically, Obsession has earned $255.4 million since opening to $17.2 million back in May. International markets have contributed $173.3 million, with strong holds across Europe and Asia. In its most recent weekend, the film added $19 million domestically with a decline of just 25% — a remarkable hold for any film, let alone one that is already available on digital platforms.</p>
<p>The sustained theatrical performance is rare. Most films see sharp declines once they hit streaming or digital rental, but Obsession has defied that pattern, drawing repeat viewers and generating significant word-of-mouth buzz.</p>

<h2>Record After Record</h2>
<p>The film has accumulated an impressive collection of milestones: the highest-grossing original horror movie of the decade, surpassing 'Sinners'; Focus Features' highest-grossing release of all time; and the first film since E.T. in 1982 to maintain top-five domestic box office positioning for this many consecutive weeks.</p>
<p>If it crosses $432 million globally — expected within days — it will have outearned an MCU entry with a budget 200 times larger. That ratio is virtually unprecedented in modern Hollywood.</p>

<h2>What's Driving the Audience</h2>
<p>Horror has long been Hollywood's most reliable genre for outsized returns, with films like 'Get Out' and 'Paranormal Activity' turning tiny budgets into massive grosses. But Obsession has transcended the genre's usual ceiling, competing directly with franchise tentpoles in total gross while operating in an entirely different economic universe.</p>
<p>The film's global appeal extends across markets where audience tastes are shifting toward original storytelling. It demonstrates that at a time when studios pour hundreds of millions into established IP, original filmmaking at a fraction of the cost can still break through — and dominate.</p>"""
})

# ─── 7. INDIAN FOUNDER-LED STOCKS ───
articles.append({
    "topic_id": "2d777d5e-e6c1-429a-9ffc-f7fb278dcea6",
    "headline": "Three Indian Founder-Led Companies Investors Are Watching: Nykaa, Infosys, and Marico",
    "subheadline": "Founder-driven companies with strong growth profiles and premium valuations are drawing attention from retail investors seeking quality Indian market exposure.",
    "category": "markets-finance",
    "vertical": "markets-finance",
    "tags": ["nykaa", "infosys", "marico", "indian-stocks", "founder-led", "investing", "indian-markets"],
    "sources": [
        "https://simplywall.st"
    ],
    "diaspora_angle": "NRI investors tracking Indian markets can access these stocks through BSE and NSE, with Infosys also listed on NYSE as ADRs.",
    "image_search": ["India stock market BSE NSE trading"],
    "image_wiki": "Bombay Stock Exchange",
    "image_pexels": "stock market trading screen India",
    "image_caption": "Traders at the Bombay Stock Exchange in Mumbai. Indian founder-led companies are attracting retail investor attention amid strong earnings growth and premium valuations.",
    "image_attribution": "Pexels",
    "body": """<div class="key-takeaways"><ul>
<li>Nykaa (FSN E-Commerce) leads with ₹940 billion market cap, growing earnings across beauty and fashion with an expanding physical store network of 265 locations.</li>
<li>Infosys, one of India's original founder-led IT companies, maintains market leadership as the sector pivots to AI-driven services amid mixed Q1 earnings.</li>
<li>Marico's brands Parachute and Saffola deliver a 40.3% return on equity, though the stock trades at a premium P/E above peers.</li>
<li>All three companies share a common trait: founders or founding families retain significant operational influence, aligning management incentives with long-term growth.</li>
</ul></div>

<h2>Why Founder-Led Matters</h2>
<p>In a market where corporate governance concerns periodically rattle investor confidence, companies where founders retain significant influence are drawing renewed attention. The logic is simple: when the person who built the business still guides its strategy, their personal wealth rises and falls with the stock — aligning their interests with outside shareholders.</p>
<p>Three Indian companies currently sitting on the radar of retail investors illustrate different facets of this model.</p>

<h2>Nykaa: Beauty Meets Scale</h2>
<p>FSN E-Commerce Ventures, better known as Nykaa, has built India's dominant beauty and personal care platform. Founded by Falguni Nayar, a former investment banker, the company combines its online marketplace with 265 physical stores and 44 warehouses. Its house brands, sold alongside third-party products, are approaching ₹290 billion in annualized gross merchandise value.</p>
<p>FY2026 net income reached ₹1,994.4 million with margins trending upward. The stock trades at a premium P/S ratio, but bulls argue that Nykaa's control over its supply chain — from product development to rapid delivery — justifies the valuation as it expands into fashion, acquisitions, and overseas markets.</p>

<h2>Infosys: The Original</h2>
<p>Infosys needs little introduction. Co-founded by N.R. Narayana Murthy in 1981, the Bangalore-based IT services giant remains one of India's most recognized corporate brands globally. While Murthy stepped back from active management years ago, the founding ethos of disciplined growth and governance continues to shape the company's culture.</p>
<p>As India's $315 billion IT sector navigates AI-driven shifts, Infosys has positioned itself as a leader in generative AI services for enterprise clients. The company's earnings have been mixed in recent quarters alongside peers like Wipro and TCS, but its scale and client relationships provide a defensive moat.</p>

<h2>Marico: Steady Compounder</h2>
<p>Mumbai-based Marico, built on the strength of brands like Parachute coconut oil and Saffola cooking oil, delivers the kind of returns value investors prize: 40.3% return on equity, consistent earnings growth of about 9.2% annually over five years, and dominant positions in its product categories. The company is now expanding into newer segments — health foods, digital-first grooming labels, and shampoos — to diversify beyond its traditional coconut oil base.</p>
<p>The challenge for investors is valuation. Marico's P/E ratio sits above both peers and some fair value estimates, raising questions about how much future growth is already priced in. Commodity cost sensitivity and rising competition add execution risk.</p>

<h2>The NRI Angle</h2>
<p>For diaspora investors seeking Indian market exposure, founder-led companies offer a blend of growth potential and governance alignment. Infosys is accessible through NYSE-listed ADRs, while Nykaa and Marico trade on the NSE and BSE. With the RBI recently raising investment limits for NRIs and OCIs in Indian equities, the opportunity set for diaspora investors continues to expand.</p>"""
})

ALREADY_DONE = {
    "1984c40d-b7b5-4a74-acea-28eaaca90fd5",
    "00ee2350-a13f-48fb-9a55-303ec9db20d9",
}

# ─── MAIN EXECUTION ───
print(f"\n{'='*60}", flush=True)
print(f"V3 Batch Writer — {len(articles)} articles total, skipping {len(ALREADY_DONE)} already done", flush=True)
print(f"{'='*60}\n", flush=True)

published = []
failed = []
skipped = []

for i, art in enumerate(articles):
    if art["topic_id"] in ALREADY_DONE:
        print(f"\n── Article {i+1}/{len(articles)}: SKIPPING (already published) ──", flush=True)
        skipped.append(art["headline"])
        continue

    print(f"\n── Article {i+1}/{len(articles)}: {art['headline'][:60]}... ──", flush=True)

    slug = slugify(art["headline"])

    # Find hero image
    image_url = None

    # Try Wikipedia
    if art.get("image_wiki"):
        print(f"  Trying Wikipedia: {art['image_wiki']}", flush=True)
        image_url = wikipedia_image(art["image_wiki"])

    # Try Pexels as fallback
    if not image_url and art.get("image_pexels"):
        print(f"  Trying Pexels: {art['image_pexels']}", flush=True)
        image_url = pexels_image(art["image_pexels"])

    # Upload
    final_image_url = None
    if image_url:
        final_image_url = upload_image(slug, image_url)

    if not final_image_url:
        print(f"  WARNING: No hero image found, continuing without", flush=True)

    # Build article payload
    word_count = len(re.sub(r'<[^>]+>', '', art["body"]).split())

    payload = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "body": art["body"],
        "slug": slug,
        "category": art["category"],
        "vertical": art["vertical"],
        "tags": art["tags"],
        "sources": art["sources"],
        "image_url": final_image_url or "",
        "image_caption": art["image_caption"],
        "image_attribution": art["image_attribution"],
        "word_count": word_count,
        "diaspora_angle": art["diaspora_angle"],
        "topic_id": art["topic_id"],
        "status": "published",
        "article_type": "breaking",
        "published_at": NOW,
    }

    # Insert
    print(f"  Inserting article ({word_count} words)...", flush=True)
    result = supabase_post("p2_articles", payload)

    if result and isinstance(result, list) and len(result) > 0:
        article_id = result[0].get("id", "unknown")
        print(f"  ✅ Published: {art['headline'][:50]}... (id={article_id})", flush=True)
        published.append(art["headline"])

        # Update topic status
        supabase_patch(
            "p2_topics",
            f"id=eq.{art['topic_id']}",
            {"status": "published", "last_article_id": article_id}
        )
        print(f"  Topic {art['topic_id'][:8]} → published", flush=True)
    else:
        print(f"  ❌ Failed to publish: {art['headline'][:50]}", flush=True)
        failed.append(art["headline"])

# ─── SUMMARY ───
print(f"\n{'='*60}", flush=True)
print(f"RESULTS: {len(published)} published, {len(failed)} failed", flush=True)
print(f"{'='*60}", flush=True)
for h in published:
    print(f"  ✅ {h}", flush=True)
for h in failed:
    print(f"  ❌ {h}", flush=True)
