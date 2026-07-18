#!/usr/bin/env python3
"""V3 Writer Batch — Write 5 articles from researched candidates."""

import json, os, subprocess, sys, uuid, re
from datetime import datetime, timezone
from urllib.parse import quote

SUPABASE_URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def supabase_post(table, data):
    """Insert a row and return the inserted row."""
    payload = json.dumps(data)
    r = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/{table}",
        "-H", f"apikey: {KEY}",
        "-H", f"Authorization: Bearer {KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", payload
    ], capture_output=True, text=True)
    return json.loads(r.stdout) if r.stdout.strip() else None

def supabase_patch(table, filters, data):
    """Patch rows matching filters."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filters}"
    payload = json.dumps(data)
    r = subprocess.run([
        "curl", "-s", "-X", "PATCH", url,
        "-H", f"apikey: {KEY}",
        "-H", f"Authorization: Bearer {KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=minimal",
        "-d", payload,
        "-w", "\n%{http_code}"
    ], capture_output=True, text=True)
    lines = r.stdout.strip().split("\n")
    return lines[-1] if lines else "0"

def download_and_upload_image(image_url, slug):
    """Download image, compress, upload to Supabase storage."""
    tmp_path = f"/tmp/hero_{slug}.jpg"
    
    # Download
    r = subprocess.run([
        "curl", "-sL", "-o", tmp_path,
        "-H", "User-Agent: TheVideshi/1.0 (thevideshi.com)",
        "-w", "%{http_code}",
        image_url
    ], capture_output=True, text=True)
    
    if "200" not in r.stdout:
        print(f"  ⚠ Download failed ({r.stdout.strip()}) for {image_url[:80]}")
        return None
    
    # Compress with GraphicsMagick
    compressed = f"/tmp/hero_{slug}_c.jpg"
    subprocess.run([
        "gm", "convert", tmp_path,
        "-resize", "1200x800>",
        "-quality", "82",
        compressed
    ], capture_output=True)
    
    # Check size
    size = os.path.getsize(compressed)
    if size > 200000:
        subprocess.run([
            "gm", "convert", compressed,
            "-quality", "65",
            compressed
        ], capture_output=True)
    
    # Upload to Supabase storage
    storage_path = f"article-images/{slug}.jpg"
    host = SUPABASE_URL.replace("https://", "")
    upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{slug}.jpg"
    
    r = subprocess.run([
        "curl", "-s", "-X", "POST", upload_url,
        "-H", f"apikey: {KEY}",
        "-H", f"Authorization: Bearer {KEY}",
        "-H", "Content-Type: image/jpeg",
        "-H", "x-upsert: true",
        "--data-binary", f"@{compressed}",
        "-w", "\n%{http_code}"
    ], capture_output=True, text=True)
    
    lines = r.stdout.strip().split("\n")
    code = lines[-1] if lines else "0"
    
    if code in ("200", "201"):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{slug}.jpg"
        print(f"  ✓ Image uploaded: {slug}.jpg ({os.path.getsize(compressed)//1024}KB)")
        return public_url
    else:
        print(f"  ⚠ Upload failed ({code}): {r.stdout[:200]}")
        return None

def make_slug(headline, date_str):
    """Generate article slug from headline."""
    slug = re.sub(r'[^a-z0-9\s-]', '', headline.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:80].rstrip('-')
    return f"{slug}-{date_str}"

def count_words(html):
    """Count words in HTML body."""
    text = re.sub(r'<[^>]+>', ' ', html)
    return len(text.split())

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
DATE_SLUG = "20260718"

# ═══════════════════════════════════════════════════════
# ARTICLE 1: India's Top Banks Post Strong Q1 FY27 Results
# ═══════════════════════════════════════════════════════

art1_headline = "India's Top Banks Post Strong Q1 Results as ICICI Leads With 16 Percent Profit Jump"
art1_subheadline = "ICICI Bank, HDFC Bank, PNB, Axis Bank and Kotak Mahindra all reported profit growth in the April-June quarter, signalling broad-based strength across the banking sector."
art1_category = "markets-finance"
art1_topic_id = "c4c21c3a-3a2e-4b22-8fa8-3b9e75f6d7a1"  # placeholder, will use actual

art1_body = """<!-- data-card -->
<div class="key-takeaways"><ul>
<li>ICICI Bank profit rose 16% to ₹14,805 crore with loan growth of 19.6% and improving asset quality.</li>
<li>HDFC Bank posted ₹190.6 billion profit, up 5%, with adjusted growth of 9.8% excluding one-time gains from a year ago.</li>
<li>Punjab National Bank's profit surged more than three-fold to over ₹5,200 crore as margins expanded and bad loans fell.</li>
<li>Axis Bank, Kotak Mahindra and YES Bank all reported double-digit profit growth, with YES Bank earning multiple credit rating upgrades.</li>
</ul></div>

<h2>Super Saturday for Indian Banking</h2>

<p>India's banking heavyweights delivered a decisive earnings day on Saturday, with five of the country's largest private and public sector lenders reporting strong April-June quarter results that underscored broad-based profitability across the sector.</p>

<p>ICICI Bank, the country's second-largest private lender by market capitalisation, led the pack with a 15.9 percent year-on-year jump in standalone profit after tax to ₹14,805 crore. Net interest income grew 12.7 percent to ₹24,384 crore, and the bank's net interest margin held at 4.36 percent — marginally above the year-ago level of 4.34 percent. Fee income surged 23.5 percent to ₹7,286 crore.</p>

<blockquote class="pull-quote">
<p>"The bank's loan book grew 19.6 percent year-on-year, with business banking expanding 28.2 percent and the rural portfolio rising 35.4 percent."</p>
<cite>— ICICI Bank Q1 FY27 filing</cite>
</blockquote>

<p>Asset quality continued to improve. ICICI's gross NPA ratio fell to 1.38 percent from 1.67 percent a year earlier, while the net NPA ratio stood at 0.35 percent. The capital adequacy ratio remained comfortable at 16.84 percent.</p>

<h2>HDFC Bank's Adjusted Growth Stronger Than Headline</h2>

<p>HDFC Bank, India's largest private lender, reported a standalone profit of ₹190.6 billion, up 5 percent year-on-year. The headline figure understated the underlying performance: non-interest income fell 41 percent due to one-time gains from the HDB Financial Services IPO booked in the year-ago quarter. Excluding that, adjusted profit grew approximately 9.8 percent.</p>

<p>Net interest income rose 6.7 percent to ₹335.3 billion, with NIM at 3.26 percent. Gross advances climbed 15.4 percent to ₹30,608 billion. Asset quality remained stable with gross NPA at 1.17 percent and net NPA at 0.4 percent. The bank's CASA ratio, however, slipped to 32 percent from 34 percent as depositors continued shifting to higher-yielding term deposits.</p>

<h2>PNB Profit Triples, YES Bank Earns Rating Upgrades</h2>

<p>Among public sector banks, Punjab National Bank delivered the most dramatic turnaround. PNB's Q1 FY27 net profit surged more than three-fold to over ₹5,200 crore, driven by margin expansion and a sharp decline in non-performing assets.</p>

<p>Axis Bank reported a 22.5 percent rise in net profit to ₹7,114 crore as lower provisions offset weaker non-interest income. Kotak Mahindra Bank's standalone profit jumped 26 percent to ₹4,123 crore, with provisions falling 45 percent year-on-year as gross NPA improved to 1.18 percent.</p>

<p>YES Bank, once a symbol of India's banking troubles, continued its recovery with a 33.7 percent profit rise to ₹1,071 crore. The quarter brought a cascade of credit rating upgrades — Moody's moved the bank to Ba1, CARE raised it to AA+, and S&P Global assigned an inaugural BB+ international rating. Gross NPA fell to 1.3 percent, and retail slippages hit a 10-quarter low.</p>

<h2>What It Means for NRI Investors</h2>

<p>The results carry direct implications for the millions of NRIs holding Indian bank stocks and deposits. ICICI Bank, HDFC Bank and Kotak Mahindra are among the most widely held Indian equities in overseas portfolios. The strong loan growth numbers across banks — ranging from 12 to 19 percent — signal a healthy domestic credit cycle that supports broader economic growth.</p>

<p>The RBI's recent rate-cutting cycle has begun compressing margins, but banks have so far managed the transition without significant earnings damage. The key variable to watch remains asset quality: while current numbers look clean, any stress from the unsecured lending pullback could surface in coming quarters.</p>

<p>Reliance Industries, which also reported on the same day, saw profit fall 22 percent due to a one-time stake sale comparison, though revenue jumped 25 percent to ₹3.11 lakh crore. The results set the tone for a busy earnings season ahead, with more large-cap companies expected to report in the coming week.</p>"""

# ═══════════════════════════════════════════════════════
# ARTICLE 2: Cyclospora Outbreak Sweeps US
# ═══════════════════════════════════════════════════════

art2_headline = "Cyclospora Parasite Outbreak Sickens Thousands Across the US With Taco Bell Lettuce Under Scrutiny"
art2_subheadline = "More than 5,100 possible cases of cyclosporiasis have been reported across 30 states, with shredded iceberg lettuce from a Mexican supplier linked to infections at Taco Bell."
art2_category = "health"
art2_topic_id = None  # Will find or skip

art2_body = """<!-- data-card -->
<div class="key-takeaways"><ul>
<li>Over 5,100 possible cyclosporiasis cases are under investigation across more than 30 US states, with at least 140 hospitalisations.</li>
<li>The CDC and FDA have linked the outbreak to shredded iceberg lettuce served at Taco Bell restaurants in five states, traced to Taylor Farms' facility in Mexico.</li>
<li>Michigan is hardest hit with more than 4,000 cases; Ohio has reported nearly 200. Symptoms include severe watery diarrhea lasting weeks.</li>
<li>Taylor Farms is removing all iceberg lettuce sourced from central Mexico, and Taco Bell has pulled the affected supplier's product nationwide.</li>
</ul></div>

<h2>Outbreak Grows Into One of the Largest in Years</h2>

<p>A parasitic outbreak that began with scattered reports in the Midwest has ballooned into one of the largest foodborne illness events in recent US history, with the Centers for Disease Control and Prevention reporting more than 5,100 possible cases under investigation across at least 30 states.</p>

<p>The illness, caused by the microscopic parasite Cyclospora cayetanensis, produces severe watery diarrhea, stomach cramps, bloating and fatigue. Unlike common stomach bugs that resolve in days, cyclosporiasis symptoms can persist for weeks or even months without treatment.</p>

<p>Michigan has emerged as the epicentre, recording more than 4,000 cases as of Thursday. Ohio has reported nearly 200, while Indiana, Kentucky, West Virginia, New York, Illinois, North Carolina and Texas have all seen increases. At least 140 people have required hospitalisation. No deaths have been reported.</p>

<h2>Taylor Farms Lettuce at Taco Bell Identified as Likely Source</h2>

<p>Federal investigators have zeroed in on shredded iceberg lettuce supplied by California-based Taylor Farms to Taco Bell restaurants in Indiana, Kentucky, Michigan, Ohio and West Virginia. The lettuce was produced as five-pound bags at Taylor Farms' facility in Guanajuato, Mexico, according to an industry source who spoke to Reuters.</p>

<p>Taylor Farms announced Friday it is removing all iceberg lettuce sourced from central Mexico from distribution. The company said no Taylor Farms-branded salads or kits are associated with the outbreak, and that its branded salad kits do not contain iceberg lettuce.</p>

<p>Taco Bell responded by voluntarily removing the affected lettuce from its supply chain nationwide. "The affected ingredient from our supplier is being indefinitely removed from our supply chain nationwide and will be replaced within 24 hours in select states," the company said in a statement.</p>

<blockquote class="pull-quote">
<p>"We are proud to have consistently acted quickly and proactively to protect our guests."</p>
<cite>— Taco Bell statement</cite>
</blockquote>

<p>The scope of the impact extends beyond Taco Bell. Taylor Farms supplies lettuce to major restaurant chains including McDonald's, Chipotle, Olive Garden, Subway, Wendy's, and Burger King, as well as grocery chains such as Walmart, Costco and Kroger. However, the CDC has not issued warnings for any locations beyond the five-state Taco Bell cluster.</p>

<h2>What Diaspora Communities Should Know</h2>

<p>Health experts recommend washing all fresh produce thoroughly for at least one minute, though this may not remove all Cyclospora spores. Cooking fruits and vegetables to an internal temperature of at least 158°F (70°C) can kill the parasite. The illness does not typically spread directly from person to person.</p>

<p>People with weakened immune systems should be especially cautious and may want to avoid foods previously linked to outbreaks, including raspberries, basil, salad mixes, cilantro and lettuce. Anyone experiencing diarrhea lasting longer than 48 hours should seek medical attention for testing and possible antibiotic treatment.</p>

<p>The outbreak has raised questions about food safety oversight for imported produce. Taylor Farms was previously implicated in a 2013 Cyclospora outbreak linked to its Mexican farm operations that sickened more than 240 people, and in a 2024 E. coli outbreak tied to onions supplied to McDonald's. The FDA has not yet commented on potential regulatory action.</p>"""

# ═══════════════════════════════════════════════════════
# ARTICLE 3: Sitharaman FCNR NRI Outreach
# ═══════════════════════════════════════════════════════

art3_headline = "Sitharaman Asks Banks to Intensify NRI Outreach as FCNR Deposit Scheme Targets $50 Billion"
art3_subheadline = "India's finance minister urged public sector banks to ramp up engagement with the diaspora as the RBI's special foreign currency deposit programme gains traction with $10 billion raised so far."
art3_category = "nri-world"
art3_topic_id = None

art3_body = """<!-- data-card -->
<div class="key-takeaways"><ul>
<li>Finance Minister Nirmala Sitharaman urged public sector banks to step up NRI engagement to sustain foreign currency deposit inflows under the FCNR(B) scheme.</li>
<li>The RBI's special FCNR programme has raised $10 billion so far, with a potential target of up to $50 billion before the September 30 deadline.</li>
<li>NRIs in Singapore, Hong Kong, the Gulf, the UK and the US have shown significant interest, with banks offering attractive returns on 3-5 year deposits.</li>
<li>Experts at a global ICAI webinar estimated NRIs could channel $70-80 billion into India through FCNR deposits, calling it a "once-in-a-generation opportunity."</li>
</ul></div>

<h2>A Direct Play for Diaspora Dollars</h2>

<p>Finance Minister Nirmala Sitharaman chaired a meeting with managing directors and CEOs of public sector banks on July 13 to review progress under the Reserve Bank of India's special foreign currency deposit scheme — and her message was blunt: reach more NRIs, faster.</p>

<p>The meeting, which also included the RBI Deputy Governor, the Chief Economic Advisor and secretaries from multiple government departments, assessed the initial response to the FCNR(B) deposit programme, External Commercial Borrowings (ECBs) and Overseas Foreign Currency Borrowings (OFCBs). The combined measures are expected to attract up to $50 billion.</p>

<blockquote class="pull-quote">
<p>"The Union Finance Minister appreciated the encouraging initial response and called on banks to intensify outreach to the NRI diaspora, introduce innovative deposit products and sustain the mobilisation momentum during the remaining period of the schemes."</p>
<cite>— Finance Ministry statement</cite>
</blockquote>

<h2>How the Scheme Works</h2>

<p>The FCNR(B) — Foreign Currency Non-Resident (Bank) — scheme allows NRIs, Overseas Citizens of India and Persons of Indian Origin to deposit overseas earnings in major foreign currencies within Indian banks, operating like fixed deposits but without currency conversion to rupees.</p>

<p>In a significant move to boost inflows, the RBI withdrew the interest rate ceiling on fresh FCNR(B) deposits with maturities of three to five years until September 30, 2026. This allows banks to offer more competitive rates than they normally could. The central bank also introduced a concessional foreign exchange swap facility that reduces hedging costs for banks accepting these deposits.</p>

<p>The backdrop is clear: net FCNR(B) inflows collapsed to just $946 million in FY26 from $7.1 billion in FY25, as the Iran conflict rattled currency markets. The government needs to shore up India's foreign exchange reserves and stabilise the rupee.</p>

<h2>NRIs in Singapore, Gulf and US Showing Strong Interest</h2>

<p>Bank chiefs told Sitharaman that NRIs in Singapore, Hong Kong, West Asia, the United Kingdom and the United States have shown significant interest in the enhanced deposit rates. Around $10 billion has been raised so far, according to ICAI Singapore Chapter Chairman Sanjay Gattani.</p>

<p>A global webinar organised by the ICAI's Singapore Chapter on July 15 drew nearly 1,800 participants, including chartered accountants, NRIs, accredited investors and finance professionals. Senior representatives from HDFC Bank, HSBC and State Bank of India explained the framework, taxation aspects and regulatory requirements.</p>

<p>Gattani estimated that NRIs have the potential to channel $70-80 billion in foreign currency inflows into India under FCNR. "This is a testament to the trust that the global Indian community continues to place in India's economic future," he said.</p>

<h2>What NRIs Should Consider</h2>

<p>The window is limited. FCNR(B) deposits under the special scheme must be mobilised by September 30, 2026, while ECBs and OFCBs remain open until December 31, 2026. With banks competing to offer attractive rates — particularly on five-year deposits — this represents an unusual opportunity for NRIs looking for relatively safe exposure to Indian interest rates without taking on rupee risk during the deposit term.</p>

<p>The deposits are denominated in foreign currencies, so principal is returned in the same currency at maturity. Interest rates currently being offered are above what most international banks provide for comparable maturities, making the risk-return proposition attractive for diaspora investors with idle dollar or pound holdings.</p>"""

# ═══════════════════════════════════════════════════════
# ARTICLE 4: MP UCC Bill
# ═══════════════════════════════════════════════════════

art4_headline = "Madhya Pradesh to Table Uniform Civil Code Bill Next Week as CM Yadav Says Only One Marriage Will Be Recognised"
art4_subheadline = "Chief Minister Mohan Yadav announced the UCC bill will be introduced during the Assembly's monsoon session starting July 20, making MP the potential second state after Uttarakhand to implement the code."
art4_category = "news"
art4_topic_id = None

art4_body = """<!-- data-card -->
<div class="key-takeaways"><ul>
<li>Madhya Pradesh CM Mohan Yadav announced the UCC bill will be tabled during the monsoon session starting July 20, with the government aiming to pass it in the five-day session.</li>
<li>Under the proposed law, only monogamous marriages will be recognised — Yadav said those with multiple marriages will not have the "legal right to reside" in the state.</li>
<li>The draft borrows approximately 90 percent of its provisions from the Gujarat UCC model, covering marriage, divorce, inheritance, wills and live-in relationships.</li>
<li>If passed, Madhya Pradesh would become the second Indian state after Uttarakhand to implement a Uniform Civil Code.</li>
</ul></div>

<h2>UCC Bill Headed to Assembly Floor</h2>

<p>Madhya Pradesh Chief Minister Mohan Yadav has confirmed that his government will introduce a Uniform Civil Code bill during the state Assembly's monsoon session, which begins on July 20 and is scheduled to run for five days. The BJP government aims to get the bill passed within the same session.</p>

<p>"Under the new UCC law, only those having one marriage will have the right to reside in Madhya Pradesh," Yadav said while addressing a gathering after inaugurating newly constructed schools in Katni district on Friday. He said the law would apply to people of all religions.</p>

<blockquote class="pull-quote">
<p>"With the blessings of Lord Ram, Madhya Pradesh is moving towards one nation, one Constitution, one flag and one law."</p>
<cite>— Mohan Yadav, Chief Minister of Madhya Pradesh</cite>
</blockquote>

<h2>Gujarat Model With Tribal Modifications</h2>

<p>The draft legislation draws heavily from the Gujarat Uniform Civil Code enacted earlier in 2026. According to sources familiar with the drafting process, approximately 90 percent of the provisions have been adopted from the Gujarat model, which brings family laws — including marriage, divorce, inheritance, wills and live-in relationships — under a single legal framework.</p>

<p>One significant adaptation concerns tribal communities. Tribals who have converted to other religions will fall under the UCC's purview, while those following traditional tribal customs and customary beliefs will be exempt.</p>

<p>Religious marriage ceremonies will not be abolished. The Gujarat model, which MP is following, explicitly allows marriages to be solemnised according to any community's traditions — including Hindu pheras, Muslim Nikah, Sikh Anand Karaj and Christian church ceremonies. However, the legal rights and obligations arising from marriage will be uniform regardless of religion.</p>

<p>Every marriage will require mandatory registration within 60 days of the ceremony. The requirement applies even if one spouse is a resident of the state and the marriage took place elsewhere.</p>

<h2>Political Significance and Opposition</h2>

<p>The UCC has been a core BJP electoral promise and part of the party's broader national agenda. Uttarakhand became the first Indian state to implement its version, and Gujarat followed with its own legislation in 2026. Madhya Pradesh passing the bill would add a third BJP-governed state to the list, building momentum for the party's long-standing demand for a nationwide code.</p>

<p>A high-level committee headed by former Supreme Court Justice Ranjana Prakash Desai has been touring the state to gather public opinion. The government has maintained that the consultation process received positive responses, including from members of the Muslim community.</p>

<p>The announcement carries weight beyond state boundaries. For the Indian diaspora, the UCC debate touches on fundamental questions of personal law reform that have implications for property inheritance, marriage recognition and family law that frequently arise in cross-border legal situations involving NRIs.</p>"""

# ═══════════════════════════════════════════════════════
# ARTICLE 5: Delhi-Rishikesh Namo Bharat
# ═══════════════════════════════════════════════════════

art5_headline = "Delhi-Rishikesh Namo Bharat Rail Extension Gets Green Light, Promising Three-Hour Travel Time"
art5_subheadline = "The 150-kilometre high-speed rail corridor from Meerut to Rishikesh has received in-principle approval from three governments, with a detailed project report survey set to begin soon."
art5_category = "travel"
art5_topic_id = None

art5_body = """<!-- data-card -->
<div class="key-takeaways"><ul>
<li>The Namo Bharat RRTS corridor will be extended from Modipuram in Meerut to Lakshman Jhula in Rishikesh, covering 150 kilometres across two states.</li>
<li>Travel time between Delhi and Rishikesh would drop from roughly six hours by road to about three hours by train, running at speeds up to 160 kmph.</li>
<li>Uttarakhand, Uttar Pradesh and the NCRTC have all given in-principle approval. A survey for the detailed project report is set to begin soon.</li>
<li>Combined with the under-construction Rishikesh-Karnaprayag railway, NCR residents could eventually reach Char Dham destinations in 5-6 hours instead of 11-13.</li>
</ul></div>

<h2>Three Governments Align on High-Speed Corridor</h2>

<p>The Namo Bharat Regional Rapid Transit System, which currently connects Delhi and Meerut at speeds of up to 160 kilometres per hour, is set for a major expansion that would bring Rishikesh within three hours of the national capital.</p>

<p>The proposed 150-kilometre extension from Modipuram station in Meerut to Lakshman Jhula in Rishikesh has received in-principle agreement from the governments of Uttarakhand and Uttar Pradesh, along with the National Capital Region Transport Corporation (NCRTC), which operates the existing Namo Bharat service.</p>

<p>Uttarakhand Chief Minister Pushkar Singh Dhami said the expansion would improve connectivity between Delhi-NCR and the state while creating new opportunities in tourism, pilgrimage travel and regional development. "The Namo Bharat train extension to Rishikesh will give new dimension to connectivity," Dhami said.</p>

<h2>The Route</h2>

<p>The corridor will originate at Modipuram in Meerut and pass through Muzaffarnagar before entering Uttarakhand. Within the state, it will connect Roorkee, Haridwar — including the Har Ki Pauri area — and terminate near Lakshman Jhula in Rishikesh. Of the total alignment, 72 kilometres will fall within Uttar Pradesh and 78 kilometres in Uttarakhand.</p>

<p>Currently, the journey between Delhi and Rishikesh by road takes approximately five to six hours depending on traffic and weather. With the Namo Bharat trains operating at their design speed of 160 kmph, that travel time would compress to about two-and-a-half to three hours.</p>

<p>To expedite the project, Uttarakhand has appointed Additional Secretary Reena Joshi as its nodal officer, and the NCRTC has designated its own counterpart. A survey for the detailed project report is expected to commence soon. The Uttarakhand government has requested approximately ₹750 crore for the infrastructure needed, including advanced power systems and underground cables in environmentally sensitive areas.</p>

<h2>Char Dham in Half the Time</h2>

<p>The extension gains additional strategic significance when paired with the Rishikesh-Karnaprayag railway line currently under construction. Together, the two rail projects could slash travel time from Delhi NCR to the Char Dham pilgrimage destinations from 11-13 hours to about 5-6 hours.</p>

<p>From Karnaprayag — a natural base camp along NH-7 — Badrinath is approximately 119 kilometres away, Kedarnath (Gaurikund base camp) about 125 kilometres, and Gangotri and Yamunotri roughly 300 kilometres each.</p>

<h2>What It Means for Travellers</h2>

<p>For the millions of Indian diaspora members who return home for pilgrimages and Himalayan getaways, the project promises a transformation in accessibility. Rishikesh, already India's yoga and adventure sports capital, sees heavy international tourist traffic. Faster rail access from Delhi — where most international flights land — would make weekend trips from the capital viable and reduce the gruelling road journeys that currently deter many visitors.</p>

<p>The project is still in its planning stage, with construction timelines dependent on the detailed project report findings. But the alignment of three state governments and the existing operational success of the Delhi-Meerut Namo Bharat corridor suggests the extension has strong political and institutional backing to move forward.</p>"""

# ═══════════════════════════════════════════════════════
# Now write all articles to DB
# ═══════════════════════════════════════════════════════

articles = [
    {
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "body": art1_body,
        "category": art1_category,
        "image_source": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/BSE_building_at_Dalal_Street.JPG/1200px-BSE_building_at_Dalal_Street.JPG",
        "image_caption": "The Bombay Stock Exchange building on Dalal Street in Mumbai. India's top banks reported strong Q1 FY27 earnings on Saturday with ICICI Bank leading private lenders with a 16 percent profit increase.",
        "image_attribution": "Wikimedia Commons",
        "tags": ["ICICI Bank", "HDFC Bank", "PNB", "Axis Bank", "Kotak Mahindra", "Q1 results", "banking", "earnings"],
        "sources": ["https://www.thehindubusinessline.com/markets/stock-markets/q1-results-today-live-updates-hdfc-bank-icici-bank-axis-bank-kotak-mahindra-bank-pnb-idbi-bank-yes-bank-jk-cement-india-cement-results-18-july-2026/article71237100.ece"],
        "diaspora_angle": "Indian bank stocks are widely held by NRI investors; strong results support portfolio positions in ICICI, HDFC and Kotak Mahindra.",
    },
    {
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "body": art2_body,
        "category": "health",
        "image_source": "PEXELS_SEARCH:food safety lettuce",
        "image_caption": "Fresh lettuce leaves displayed at a grocery store. Federal investigators have linked shredded iceberg lettuce from a Mexican facility to a cyclosporiasis outbreak affecting more than 5,100 people across the United States.",
        "image_attribution": "Pexels",
        "tags": ["cyclospora", "food safety", "Taco Bell", "Taylor Farms", "parasite outbreak", "health", "FDA", "CDC"],
        "sources": ["https://www.reuters.com", "https://www.usatoday.com", "https://www.wsj.com"],
        "diaspora_angle": "Directly affects Indians living in the US who eat at chain restaurants and buy produce from major grocery stores.",
    },
    {
        "headline": art3_headline,
        "subheadline": art3_subheadline,
        "body": art3_body,
        "category": "nri-world",
        "image_source": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/Am_11._April_2025_empfing_Au%C3%9Fenministerin_Beate_Meinl-Reisinger_die_indische_Finanzministerin_Nirmala_Sitharaman_in_Wien_%2854445397025%29_%28cropped%29.jpg/1200px-Am_11._April_2025_empfing_Au%C3%9Fenministerin_Beate_Meinl-Reisinger_die_indische_Finanzministerin_Nirmala_Sitharaman_in_Wien_%2854445397025%29_%28cropped%29.jpg",
        "image_caption": "Union Finance Minister Nirmala Sitharaman at an official engagement in 2025. Sitharaman urged public sector banks to step up engagement with NRIs to boost foreign currency deposit inflows under the FCNR scheme.",
        "image_attribution": "Wikimedia Commons",
        "tags": ["Nirmala Sitharaman", "FCNR", "NRI", "foreign currency", "RBI", "banking", "deposits", "diaspora"],
        "sources": ["https://www.thehindubusinessline.com", "https://www.outlookbusiness.com", "https://www.caclubindia.com"],
        "diaspora_angle": "Directly targets NRIs: enhanced FCNR deposit rates and government push for diaspora investment in India.",
    },
    {
        "headline": art4_headline,
        "subheadline": art4_subheadline,
        "body": art4_body,
        "category": "news",
        "image_source": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Mohan_Yadav%2C_Chief_Minister_of_Madhya_Pradesh.jpg/800px-Mohan_Yadav%2C_Chief_Minister_of_Madhya_Pradesh.jpg",
        "image_caption": "Madhya Pradesh Chief Minister Mohan Yadav at an official event. Yadav announced that only monogamous marriages will be legally recognised under the state's proposed Uniform Civil Code.",
        "image_attribution": "Wikimedia Commons",
        "tags": ["UCC", "Uniform Civil Code", "Madhya Pradesh", "Mohan Yadav", "personal law", "marriage law", "BJP"],
        "sources": ["https://indianewsstream.com", "https://bhaskarenglish.in", "https://news89.com"],
        "diaspora_angle": "UCC reform affects NRI property inheritance, marriage recognition and cross-border family law matters.",
    },
    {
        "headline": art5_headline,
        "subheadline": art5_subheadline,
        "body": art5_body,
        "category": "travel",
        "image_source": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Namo_Bharat_Trains_together.jpg/1200px-Namo_Bharat_Trains_together.jpg",
        "image_caption": "Namo Bharat RRTS trains at a station on the Delhi-Meerut corridor. The high-speed rail service will be extended to Rishikesh, reducing travel time from Delhi to approximately three hours.",
        "image_attribution": "Wikimedia Commons",
        "tags": ["Namo Bharat", "RRTS", "Delhi", "Rishikesh", "rail", "infrastructure", "Uttarakhand", "travel"],
        "sources": ["https://www.livemint.com", "https://www.nativeplanet.com", "https://www.newkerala.com", "https://www.magicbricks.com"],
        "diaspora_angle": "Faster Delhi-Rishikesh connectivity benefits returning NRIs who visit for yoga retreats, pilgrimages and Himalayan holidays.",
    },
]

# Read candidate topic IDs from the actual candidates file
try:
    with open("/tmp/v3-candidates.json") as f:
        candidates = json.load(f)["candidates"]
    
    # Map topic IDs by matching keywords
    topic_map = {}
    for c in candidates:
        title_lower = c["title"].lower()
        if "icici" in title_lower:
            topic_map["markets-finance-banks"] = c["topic_id"]
        elif "cyclospora" in title_lower or "diarrhea" in title_lower:
            topic_map["cyclospora"] = c["topic_id"]
        elif "sitharaman" in title_lower or "nri outreach" in title_lower:
            topic_map["sitharaman"] = c["topic_id"]
        elif "mohan yadav" in title_lower or "ucc" in title_lower:
            topic_map["ucc"] = c["topic_id"]
        elif "delhi" in title_lower and "rishikesh" in title_lower:
            topic_map["rishikesh"] = c["topic_id"]
    
    # Assign topic IDs
    articles[0]["topic_id"] = topic_map.get("markets-finance-banks")
    articles[1]["topic_id"] = topic_map.get("cyclospora")
    articles[2]["topic_id"] = topic_map.get("sitharaman")
    articles[3]["topic_id"] = topic_map.get("ucc")
    articles[4]["topic_id"] = topic_map.get("rishikesh")
except Exception as e:
    print(f"Warning: couldn't load candidate topic IDs: {e}")

published_articles = []

for i, art in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Article {i+1}: {art['headline'][:70]}")
    print(f"{'='*60}")
    
    slug = make_slug(art["headline"], DATE_SLUG)
    
    # Download and upload hero image
    img_url = art["image_source"]
    if img_url.startswith("PEXELS_SEARCH:"):
        # Use Pexels API
        query = img_url.replace("PEXELS_SEARCH:", "")
        pexels_key = os.environ.get("PEXELS_API_KEY", "")
        r = subprocess.run([
            "curl", "-s",
            f"https://api.pexels.com/v1/search?query={quote(query)}&per_page=1",
            "-H", f"Authorization: {pexels_key}"
        ], capture_output=True, text=True)
        try:
            pdata = json.loads(r.stdout)
            img_url = pdata["photos"][0]["src"]["large"]
            art["image_attribution"] = f"Pexels / {pdata['photos'][0].get('photographer', 'Unknown')}"
        except:
            print("  ⚠ Pexels search failed, skipping image")
            img_url = None
    
    uploaded_url = None
    if img_url:
        uploaded_url = download_and_upload_image(img_url, slug)
    
    # Insert article
    article_data = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "body": art["body"],
        "slug": slug,
        "category": art["category"],
        "vertical": art["category"],
        "tags": art["tags"],
        "sources": art["sources"],
        "image_url": uploaded_url or "",
        "image_caption": art["image_caption"],
        "image_attribution": art["image_attribution"],
        "word_count": count_words(art["body"]),
        "diaspora_angle": art["diaspora_angle"],
        "status": "published",
        "is_featured": False,
        "published_at": NOW,
        "article_type": "breaking",
        "topic_id": art.get("topic_id"),
    }
    
    # Remove None values
    article_data = {k: v for k, v in article_data.items() if v is not None}
    
    result = supabase_post("p2_articles", article_data)
    
    if result and isinstance(result, list) and len(result) > 0:
        art_id = result[0].get("id", "unknown")
        print(f"  ✓ Published: {art['headline'][:60]}")
        print(f"    ID: {art_id}")
        print(f"    Category: {art['category']}")
        print(f"    Words: {article_data['word_count']}")
        published_articles.append({
            "id": art_id,
            "headline": art["headline"],
            "category": art["category"],
            "slug": slug,
        })
        
        # Update topic status if we have a topic_id
        if art.get("topic_id"):
            status = supabase_patch(
                "p2_topics",
                f"id=eq.{art['topic_id']}",
                {"status": "published", "last_article_id": art_id}
            )
            print(f"    Topic updated: {status}")
    else:
        print(f"  ✗ FAILED to insert: {result}")

print(f"\n{'='*60}")
print(f"SUMMARY: {len(published_articles)} articles published")
for pa in published_articles:
    print(f"  [{pa['category']}] {pa['headline'][:70]}")
print(f"{'='*60}")
