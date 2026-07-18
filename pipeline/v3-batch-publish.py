#!/usr/bin/env python3
"""V3 batch article publisher — writes 4 articles from researched candidates."""
import json, os, subprocess, sys, re, uuid
from datetime import datetime, timezone
from urllib.parse import quote

SUPABASE_URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def supabase_post(table, data):
    """Insert a row, return the created row."""
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
    try:
        return json.loads(r.stdout)
    except:
        print(f"  !! POST error: {r.stdout[:200]}")
        return None

def supabase_patch(table, filter_str, data):
    """Patch rows matching filter."""
    payload = json.dumps(data)
    r = subprocess.run([
        "curl", "-s", "-X", "PATCH",
        f"{SUPABASE_URL}/rest/v1/{table}?{filter_str}",
        "-H", f"apikey: {KEY}",
        "-H", f"Authorization: Bearer {KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=minimal",
        "-d", payload,
        "-w", "\n%{http_code}"
    ], capture_output=True, text=True)
    lines = r.stdout.strip().split("\n")
    return "204" in lines[-1]

def download_and_compress(url, slug):
    """Download image, compress to <=200KB, return local path."""
    ext = ".jpg"
    local = f"/tmp/{slug}{ext}"
    subprocess.run(["curl", "-sL", "-o", local, "-A", "TheVideshi/1.0 (thevideshi.com)", url],
                   capture_output=True, timeout=30)
    if not os.path.exists(local) or os.path.getsize(local) < 1000:
        print(f"  !! Download failed: {url[:80]}")
        return None
    # Compress with GraphicsMagick
    compressed = f"/tmp/{slug}_c.jpg"
    subprocess.run(["gm", "convert", local, "-resize", "1200x800>", "-quality", "82", compressed],
                   capture_output=True, timeout=15)
    if os.path.exists(compressed) and os.path.getsize(compressed) > 1000:
        # Further compress if still > 200KB
        if os.path.getsize(compressed) > 200000:
            subprocess.run(["gm", "convert", compressed, "-quality", "65", compressed],
                           capture_output=True, timeout=15)
        return compressed
    return local

def upload_to_supabase(local_path, slug):
    """Upload image to Supabase storage."""
    storage_path = f"article-images/{slug}.jpg"
    url = f"{SUPABASE_URL}/storage/v1/object/{storage_path}"
    with open(local_path, "rb") as f:
        img_bytes = f.read()
    r = subprocess.run([
        "curl", "-s", "-X", "POST", url,
        "-H", f"apikey: {KEY}",
        "-H", f"Authorization: Bearer {KEY}",
        "-H", "Content-Type: image/jpeg",
        "-H", "x-upsert: true",
        "--data-binary", "@" + local_path,
        "-w", "\n%{http_code}"
    ], capture_output=True, text=True, timeout=30)
    lines = r.stdout.strip().split("\n")
    code = lines[-1] if lines else ""
    if code in ("200", "201"):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{storage_path}"
        print(f"  ✓ Image uploaded: {storage_path}")
        return public_url
    else:
        print(f"  !! Upload failed ({code}): {r.stdout[:200]}")
        return None

def publish_article(article):
    """Publish one article to p2_articles."""
    now = datetime.now(timezone.utc).isoformat()
    slug = article["slug"]
    
    # Download and upload hero image
    image_url = None
    if article.get("image_source_url"):
        local = download_and_compress(article["image_source_url"], slug)
        if local:
            image_url = upload_to_supabase(local, slug)
    
    row = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": slug,
        "category": article["category"],
        "vertical": article["category"],
        "tags": article["tags"],
        "sources": article["sources"],
        "image_url": image_url or "",
        "image_caption": article.get("image_caption", ""),
        "image_attribution": article.get("image_attribution", ""),
        "word_count": len(article["body"].split()),
        "diaspora_angle": article.get("diaspora_angle", ""),
        "topic_id": article.get("topic_id"),
        "status": "published",
        "published_at": now,
        "article_type": "breaking",
        "is_featured": False,
        "created_at": now,
        "updated_at": now,
    }
    
    result = supabase_post("p2_articles", row)
    if result and isinstance(result, list) and len(result) > 0:
        article_id = result[0]["id"]
        print(f"  ✓ Published: {article['headline'][:60]}... (id={article_id[:8]})")
        # Update topic status
        if article.get("topic_id"):
            supabase_patch("p2_topics", f"id=eq.{article['topic_id']}",
                          {"status": "published", "last_article_id": article_id})
        return article_id
    else:
        print(f"  ✗ FAILED: {article['headline'][:60]}")
        return None


# ============================================================
# ARTICLE 1: India vs England 3rd ODI Lord's
# ============================================================
print("=" * 60)
print("ARTICLE 1: India vs England Lord's ODI Decider")
print("=" * 60)

article1 = {
    "headline": "India vs England Series Decider at Lord's: Rohit Sharma's Farewell, Sundar's Injury and Everything at Stake",
    "subheadline": "The three-match ODI series heads to Lord's on Sunday locked at 1-1, with Rohit Sharma's parents reportedly in London for what could be his final international match.",
    "category": "sports",
    "tags": ["cricket", "india vs england", "odi", "lord's", "rohit sharma", "virat kohli", "jasprit bumrah", "joe root"],
    "sources": ["https://cricketaddictor.com", "https://reuters.com", "https://thesportstak.com"],
    "image_source_url": "https://upload.wikimedia.org/wikipedia/commons/7/77/Lords-Cricket-Ground-Pavilion-06-08-2017.jpg",
    "image_caption": "The historic Lord's Cricket Ground Pavilion in London, home of the Marylebone Cricket Club. India and England meet at the venue on Sunday for a series-deciding third ODI.",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "The series decider at Lord's is appointment viewing for Indian cricket fans worldwide, with Rohit Sharma potentially playing his last international match.",
    "topic_id": "16e0e8b2-4f7a-4deb-ae6e-8107e2e14576",
    "slug": "india-vs-england-3rd-odi-lords-series-decider-rohit-sharma-farewell-20260718",
    "body": """<div class="key-takeaways"><ul>
<li>India and England meet at Lord's on Sunday for the series-deciding 3rd ODI, locked at 1-1 after India won in Birmingham and England levelled in Cardiff.</li>
<li>Rohit Sharma's parents have reportedly travelled to London, fuelling speculation that the match could be his ODI farewell after averaging just 30 in eight ODIs this year.</li>
<li>Washington Sundar has been ruled out with a hamstring injury sustained in Cardiff; left-arm spinner Kuldeep Yadav is expected to replace him.</li>
<li>Lord's famous 2.5-metre slope will challenge batters early before conditions ease, with a competitive first-innings target expected in the 270-280 range.</li>
</ul></div>

<h2>A Series Decider With Extra Stakes</h2>

<p>When India walk out at Lord's on Sunday morning, the stakes will extend well beyond a bilateral trophy. The three-match ODI series against England is level at 1-1 — India dominated the opener in Birmingham by six wickets behind Shubman Gill's commanding 80, while England hit back in Cardiff where Joe Root's unbeaten 99 guided a clinical four-wicket chase.</p>

<p>But the subtext is what makes this match unmissable. Reports from multiple Indian cricket outlets indicate that Rohit Sharma's parents have arrived in London, a detail that has sent a wave of emotion through Indian cricket circles. The BCCI has already informed Rohit that he is no longer in India's ODI plans beyond this England series, and the 39-year-old's form has done little to challenge that decision — he has managed just one half-century across eight ODIs in 2026, averaging around 30.</p>

<blockquote class="pull-quote">
<p>"The series is locked, the stage is Lord's, and there's a feeling this could be the end of an era. Indian cricket doesn't get many moments bigger than this."</p>
</blockquote>

<h2>India's Bowling Reshuffle</h2>

<p>India's preparations took a hit when Washington Sundar was ruled out with a right hamstring injury sustained during the Cardiff match. The BCCI confirmed on Saturday that the 26-year-old all-rounder will undergo further scans to determine the extent of the damage and will miss the remainder of the tour.</p>

<p>Harsh Dubey has been added to the squad as a replacement, according to Reuters, though Kuldeep Yadav is the more likely choice to slot into the playing XI. Kuldeep's wrist spin gives India a different option in the middle overs — a phase where England, led by Root and Harry Brook, have been particularly aggressive this series.</p>

<p>Jasprit Bumrah will spearhead the pace attack alongside Prasidh Krishna and the impressive young left-arm seamer Gurnoor Brar. Bumrah's ability to strike in the powerplay — he dismissed Ben Duckett with the first ball of England's chase in Cardiff — remains India's most reliable weapon with the new ball.</p>

<h2>Lord's Slope: The Great Equaliser</h2>

<p>Lord's is unlike any other ground in world cricket. The famous 2.5-metre slope running across the pitch offers early seam movement and sharp swing during the powerplay, before the surface flattens out and rewards patient strokeplay. Spinners tend to play a supporting role in the middle overs rather than a match-defining one.</p>

<p>Teams batting first at Lord's in recent ODIs have typically needed 270-280 to feel secure, and the toss could be pivotal. Overcast conditions are forecast for the afternoon — temperatures between 21°C and 23°C with no rain expected — which could bring the England seamers into the game if India are chasing under cloud cover.</p>

<h2>Key Matchups and Players to Watch</h2>

<p>The contest between Virat Kohli and Adil Rashid has been one of ODI cricket's most compelling duels. Kohli has scored 126 runs off 145 balls against the leg-spinner in the format but has fallen to him five times — a vulnerability England will look to exploit in the middle overs. Kohli scored 65 in Cardiff and has accumulated 547 runs at an average of 91.17 across his last 10 ODI innings.</p>

<p>For England, Root has been the anchor. His unbeaten 99 in Cardiff extended a remarkable run — he averages 65.88 over his last 10 ODI matches and has scored five consecutive half-centuries. The veteran's ability to pace a chase could be decisive if England bat second.</p>

<p>Shubman Gill, captaining the side, carries stellar 2026 numbers into the decider: 484 runs at an average of 96.80 and a strike rate of 114.42, including four fifties and a century. His composure under pressure will be tested at a ground steeped in history.</p>

<h2>What's at Stake</h2>

<p>Beyond the trophy, Sunday's match carries selection implications for both sides heading into the busy winter schedule. India's performance at Lord's will shape the conversation around their middle-order balance and spin options ahead of the Test series that follows in August.</p>

<p>For Indian fans watching from living rooms in New Jersey, pubs in London and early-morning streams in Sydney, the moment is weighted with something more personal. If Rohit Sharma does walk out at Lord's one final time, it will mark the end of a career that delivered India a T20 World Cup, 264 in an ODI, and 10,000 runs in the format. Not a bad place to say goodbye.</p>

<p><strong>Match details:</strong> England vs India, 3rd ODI, Sunday July 19, 2026, 11:00 AM local time (3:30 PM IST), Lord's, London. Live on Sony Sports Network and JioHotstar.</p>"""
}

id1 = publish_article(article1)

# ============================================================
# ARTICLE 2: Kanwal Rekhi — The Groundbreaker
# ============================================================
print("\n" + "=" * 60)
print("ARTICLE 2: Kanwal Rekhi — The Groundbreaker")
print("=" * 60)

article2 = {
    "headline": "From IIT Bombay to NASDAQ: Kanwal Rekhi's 'The Groundbreaker' Charts the Blueprint of Indian American Entrepreneurship",
    "subheadline": "The first Indian American founder to take a venture-backed company public on NASDAQ has published a memoir tracing his journey from Kanpur to co-founding TiE, the world's largest entrepreneur network.",
    "category": "nri-world",
    "tags": ["kanwal rekhi", "tie", "silicon valley", "iit bombay", "nasdaq", "indian american", "entrepreneurship", "book"],
    "sources": ["https://southasianherald.com", "https://founderthesis.com"],
    "image_source_url": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Kanwal_Rekhi.jpg",
    "image_caption": "Kanwal Rekhi, co-founder of TiE and the first Indian American to take a venture-backed company public on NASDAQ. He is currently on a US book tour for his memoir 'The Groundbreaker.'",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "Rekhi's story is foundational to Indian American entrepreneurship — he paved the way for generations of diaspora founders in Silicon Valley and co-founded TiE to mentor them.",
    "topic_id": None,
    "slug": "kanwal-rekhi-groundbreaker-book-iit-bombay-nasdaq-tie-silicon-valley-20260718",
    "body": """<div class="key-takeaways"><ul>
<li>Kanwal Rekhi, the first Indian American founder to take a venture-backed company public on NASDAQ, has published "The Groundbreaker," a memoir about his journey from Kanpur to Silicon Valley.</li>
<li>Rekhi co-founded Excelan in the 1980s, commercialised Ethernet and TCP/IP when the industry dismissed the combination, and listed the company on NASDAQ in 1987 with $22 million in revenue.</li>
<li>He co-founded TiE (The IndUS Entrepreneurs) in 1992, now the world's largest entrepreneur network with over 60 chapters globally, to mentor the next generation of founders.</li>
<li>Now on a US book tour with stops including a Washington D.C. launch with Congressman Ro Khanna, Rekhi says India needs 10 million entrepreneurs by 2047 to eliminate poverty.</li>
</ul></div>

<h2>$8, a Stutter, and a Contrarian Bet</h2>

<p>Kanwal Rekhi arrived in the United States in 1967 with $8 in his pocket and a stutter he had carried since childhood. Born in 1945 in what is now Pakistan, raised in Kanpur and educated at IIT Bombay, he was part of India's first wave of IIT graduates to cross the Atlantic — answering President Kennedy's call for engineers to fuel America's space race against the Soviet Union.</p>

<p>The early years were brutal. Rekhi was laid off three times in quick succession, moved from New Jersey to Florida to Silicon Valley, and spent years navigating an industry that did not know what to make of an Indian engineer with ambitions beyond a technical role. "There were no mentors, no role models," Rekhi told the South Asian Herald in an interview in Washington D.C. in June. "I transitioned from engineer to entrepreneur and then to CEO largely on my own."</p>

<p>That journey is the backbone of his new book, "The Groundbreaker: Entrepreneurship, the American Dream, and the Rise of Modern India," published earlier this year and now the subject of a multi-city book tour across the United States and India.</p>

<h2>The TCP/IP Bet That Built the Internet's Backbone</h2>

<p>In the early 1980s, with career advancement options dwindling, Rekhi co-founded Excelan to build networking hardware. The company's bet was deeply contrarian: at a time when virtually every networking engineer in Silicon Valley considered TCP/IP — the military protocol developed for slow, error-prone networks — ill-suited for Ethernet, Rekhi built a board-level Ethernet implementation and bundled TCP/IP directly onto it.</p>

<blockquote class="pull-quote">
<p>"The conventional wisdom was that TCP/IP was ill-suited for Ethernet. My logic was: if there are no errors, there are no retransmissions. TCP/IP has no inherent limit on speed. I was the only person who bet on it."</p>
<cite>— Kanwal Rekhi</cite>
</blockquote>

<p>He was right. But the company nearly died anyway. The first CEO went hands-off, the board fired him, and Rekhi stepped in with a pricing turnaround — replacing à la carte component pricing with a single bundled solution at $14,995, exactly half of Digital Equipment Corporation's $30,000 equivalent. Gross margins soared to 80-90 percent. In 1987, Excelan became the first company founded by an Indian American to IPO on NASDAQ, with $22 million in revenue and a valuation of roughly $125 million.</p>

<p>One detail from the book stands out: weeks before the IPO, the board temporarily replaced Rekhi with a white CEO because, as he recounts, "there was a fear an Indian CEO may not play well on Wall Street." The replacement was fired six months later. In 1989, Excelan merged with Novell in a deal worth $210 million. Novell's stock surged tenfold within a year, eventually reaching a $12 billion market cap.</p>

<h2>Building TiE: From Dinner Group to Global Network</h2>

<p>After Novell, Rekhi could have retreated into comfortable retirement. Instead, a 1991 meeting at the Indian Consulate in San Francisco — where a group of successful Indian professionals in Silicon Valley were urged to consider entrepreneurship in India during the country's economic liberalisation — planted the seed for something bigger.</p>

<p>"We realized that many of us had traveled very lonely entrepreneurial paths without mentors, role models, or support systems," Rekhi said. "We decided to create an organization that would help the next generation."</p>

<p>That organisation became TiE — The IndUS Entrepreneurs — founded in 1992. Today, TiE has more than 60 chapters across the United States, India and other countries, making it the world's largest entrepreneur network. Its alumni include founders who have collectively built hundreds of billions of dollars in enterprise value. Rekhi has personally backed over 200 startups through his investment firm Silicon Valley Quad.</p>

<h2>10 Million Entrepreneurs by 2047</h2>

<p>At 81, Rekhi remains urgently focused on India's future. His headline ambition is to help create 10 million entrepreneurs in India by the centenary of independence in 2047 — a number he considers essential to eliminating poverty in a country without vast natural resources.</p>

<p>"The most effective way to address poverty is through wealth creation, and in countries without vast natural resources, entrepreneurship is one of the most powerful drivers," he said. India currently forms around 10,000 new companies a month, a figure Rekhi wants to see multiplied five- or tenfold through continued policy liberalisation and investment incentives.</p>

<p>The D.C. book launch, held on June 4 with Congressman Ro Khanna as chief guest, brought Rekhi's story to the heart of American power — a fitting venue for a man who has spent six decades proving that the distance between Kanpur and NASDAQ is shorter than anyone thought.</p>"""
}

# Find the topic_id for IIT Bombay alum NASDAQ candidate
candidates = json.load(open("/tmp/v3-candidates.json"))["candidates"]
for c in candidates:
    title = c.get("title", "")
    if "IIT Bombay" in title and "NASDAQ" in title:
        article2["topic_id"] = c["topic_id"]
        break

id2 = publish_article(article2)

# ============================================================
# ARTICLE 3: GlobalFoundries + Fermionic
# ============================================================
print("\n" + "=" * 60)
print("ARTICLE 3: GlobalFoundries + Fermionic RF Chips")
print("=" * 60)

# Get Pexels image for semiconductor
pexels_key = os.environ.get("PEXELS_API_KEY", "")
pexels_url = None
if pexels_key:
    r = subprocess.run(["curl", "-sL",
        "https://api.pexels.com/v1/search?query=semiconductor+chip+circuit&per_page=1",
        "-H", f"Authorization: {pexels_key}"],
        capture_output=True, text=True, timeout=10)
    try:
        photos = json.loads(r.stdout).get("photos", [])
        if photos:
            pexels_url = photos[0]["src"]["large"]
            pexels_photographer = photos[0].get("photographer", "Pexels")
    except:
        pass

article3 = {
    "headline": "GlobalFoundries to Manufacture First RF Chips Designed by Indian Startup Fermionic, Marking Semiconductor Milestone",
    "subheadline": "Fermionic's radio frequency chips for radar, satellite and telecom applications will be the first Indian-designed semiconductors manufactured by the global chipmaker that produces for Qualcomm, MediaTek and Broadcom.",
    "category": "technology",
    "tags": ["fermionic", "globalfoundries", "semiconductor", "rf chips", "india", "design linked incentive", "make in india"],
    "sources": ["https://communicationstoday.co.in", "https://electronicsforyou.biz", "https://dqindia.com"],
    "image_source_url": pexels_url or "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Silicon_chip_3d.png/1280px-Silicon_chip_3d.png",
    "image_caption": "A semiconductor chip on a circuit board. Indian startup Fermionic has partnered with GlobalFoundries to manufacture its RF chip designs for radar, satellite and telecom applications.",
    "image_attribution": "Pexels" if pexels_url else "Wikimedia Commons",
    "diaspora_angle": "The partnership signals India's growing capability in semiconductor design, a sector where Indian-origin engineers have long dominated at global firms like Qualcomm and Broadcom but India itself has lagged in domestic chip development.",
    "topic_id": None,
    "slug": "globalfoundries-fermionic-rf-chips-indian-semiconductor-milestone-20260718",
    "body": """<div class="key-takeaways"><ul>
<li>GlobalFoundries will manufacture radio frequency (RF) chips designed by Indian startup Fermionic under a commercial partnership — the first time an Indian-designed semiconductor will be produced by the global chipmaker.</li>
<li>Fermionic, founded in 2020 and backed by the government's Design Linked Incentive (DLI) scheme, is developing chips for radar, satellite communications, telecom infrastructure and defence applications.</li>
<li>GlobalFoundries produces chips for global majors including Qualcomm, MediaTek and Broadcom, making this partnership a significant validation of Indian semiconductor design capability.</li>
<li>India's semiconductor market is projected to reach $150 billion by 2030, and the government has allocated over ₹76,000 crore to incentivise domestic chip development.</li>
</ul></div>

<h2>From Prototypes to Production-Grade Silicon</h2>

<p>GlobalFoundries Engineering Private Limited (GF India) and Fermionic, a Pune-based fabless semiconductor startup, announced a commercial partnership under which GlobalFoundries will manufacture Fermionic's radio frequency (RF) chips. The deal, announced in June 2026, marks the first time an Indian-designed semiconductor will be produced by the global chipmaker that counts Qualcomm, MediaTek and Broadcom among its manufacturing clients.</p>

<p>The significance is hard to overstate. India has long been a powerhouse in chip design — thousands of Indian-origin engineers work at leading semiconductor firms worldwide — but domestic chip manufacturing and even fabless design-to-production pipelines have remained nascent. Fermionic's partnership with GlobalFoundries represents a tangible step from academic research and government-backed prototyping to commercial-grade production.</p>

<blockquote class="pull-quote">
<p>"Our collaboration with GlobalFoundries India enables us to deliver complex, production-grade RF silicon — not just prototypes — and build the confidence required by our customers in strategic applications."</p>
<cite>— Gautam Kumar Singh, CEO of Fermionic</cite>
</blockquote>

<h2>What Fermionic Is Building</h2>

<p>Fermionic, founded in June 2020 by Gautam Kumar Singh and Prasun Kali Bhattacharyya, is developing high-performance RF and millimetre-wave (mmWave) chips for radar, satellite communications, telecom infrastructure and adjacent applications. Its product roadmap includes beamformers, phased-array transceivers, RF switches, high-linearity power amplifier chains and integrated front-end ICs optimised for intelligent sensing, adaptive communications and AI-enabled RF systems.</p>

<p>These are not consumer gadgets. The applications are primarily strategic — think radar systems for defence, satellite links for remote connectivity, and the 5G base station infrastructure that will underpin India's next-generation telecom networks. The startup raised $6 million in its first external funding round, having previously bootstrapped its operations, and counts participation in the Qualcomm Semiconductor Mentorship Program among its early validations.</p>

<h2>Government's DLI Scheme Bears Fruit</h2>

<p>Fermionic is part of an early cohort of Indian fabless companies supported under the government's Design Linked Incentive (DLI) scheme, a component of the broader Semicon India programme that has allocated over ₹76,000 crore (roughly $9 billion) to incentivise semiconductor development in the country. The DLI specifically targets chip design startups, offering financial support to bridge the gap between prototype and production.</p>

<p>India's semiconductor market is projected to reach $150 billion by 2030, growing at a 24 percent compound annual growth rate from $33 billion in 2023. But the country currently imports virtually all of its chips. The government's multi-pronged strategy — combining design incentives with manufacturing partnerships (including a joint venture with Tower Semiconductor for a fabrication plant in Gujarat) — aims to change that equation over the next decade.</p>

<h2>Why GlobalFoundries Matters</h2>

<p>GlobalFoundries, headquartered in Malta, New York, is the world's third-largest contract chipmaker by revenue and operates fabrication facilities across the US, Germany and Singapore. Unlike Taiwan's TSMC, which focuses on cutting-edge sub-5nm chips for Apple and Nvidia, GlobalFoundries specialises in mature-node and specialty technologies — including RF, power management and automotive chips — where India's defence and telecom sectors have the most immediate demand.</p>

<p>For Fermionic, the partnership provides more than manufacturing capacity. Singh emphasised that the startup needed "more than a manufacturing vendor — we needed a partner who understands RF complexity and can support production-grade execution." GF India's hands-on engineering engagement was central to making the deal work.</p>

<h2>The Road Ahead for Indian Chipmakers</h2>

<p>Fermionic is not alone. Other Indian fabless startups in the semiconductor ecosystem include Saankhya Labs, Signalchip and Terminus Circuits, several of which have tied up with global majors including Qualcomm, Intel and NXP. The talent pipeline is deep — IITs and other engineering institutions produce thousands of chip design engineers annually, many of whom have historically migrated to jobs at US and European firms.</p>

<p>The challenge now is keeping enough of that talent and capital at home to build a self-sustaining ecosystem. Fermionic's deal with GlobalFoundries is one proof point. If the chips perform in production and attract orders from defence and telecom customers, it could catalyse a wave of similar partnerships — and begin to close the gap between India's design talent and its manufacturing ambitions.</p>"""
}

for c in candidates:
    title = c.get("title", "")
    if "GlobalFoundries" in title or "Fermionic" in title:
        article3["topic_id"] = c["topic_id"]
        break

id3 = publish_article(article3)

# ============================================================
# ARTICLE 4: Ladakh Offbeat Destinations
# ============================================================
print("\n" + "=" * 60)
print("ARTICLE 4: Offbeat Ladakh Destinations")
print("=" * 60)

article4 = {
    "headline": "Beyond Pangong and Nubra: Seven Offbeat Ladakh Destinations That Deserve a Spot on Your Bucket List",
    "subheadline": "From India's last village before the Pakistan border to the country's first Dark Sky Reserve, these hidden corners of Ladakh offer silence, culture and raw Himalayan beauty far from the tourist crowds.",
    "category": "travel",
    "tags": ["ladakh", "travel", "offbeat", "turtuk", "tso moriri", "hanle", "dark sky reserve", "india travel"],
    "sources": ["https://kashmirtravels.in", "https://outlooktraveller.com", "https://travelandtourworld.com"],
    "image_source_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Tso_Moriri%2C_Ladakh_%2834855616204%29.jpg/3840px-Tso_Moriri%2C_Ladakh_%2834855616204%29.jpg",
    "image_caption": "Tso Moriri lake in the Changthang Plateau of Ladakh, one of the highest lakes in India at 4,522 metres. The Ramsar-recognised wetland is home to black-necked cranes and Changpa nomadic herders.",
    "image_attribution": "Wikimedia Commons",
    "diaspora_angle": "For NRIs planning summer trips back to India, Ladakh's peak season (June-September) coincides with typical visit windows, and these offbeat destinations offer deeper cultural experiences beyond the well-trodden tourist loop.",
    "topic_id": None,
    "slug": "offbeat-ladakh-destinations-turtuk-hanle-tso-moriri-beyond-pangong-20260718",
    "body": """<div class="key-takeaways"><ul>
<li>Seven lesser-known Ladakh destinations — Turtuk, Hanle, Tso Moriri, Uleytokpo, Sumda Chun, Dha-Hanu and Phugtal — offer cultural depth and solitude that Pangong and Nubra's crowded circuits no longer provide.</li>
<li>Hanle, India's first Dark Sky Reserve, offers naked-eye Milky Way views so clear they can cast a shadow, with local villagers trained as astro-guides running telescope sessions for visitors.</li>
<li>Turtuk, India's last inhabited village before the Pakistan border, was captured from Pakistan in 1971 and opened to tourists only in 2010, preserving its distinct Balti culture and apricot orchards.</li>
<li>The best season for all seven destinations is June to September; border-adjacent areas require an Inner Line Permit for Indian nationals, easily arranged in Leh.</li>
</ul></div>

<h2>Why Offbeat Ladakh, Why Now</h2>

<p>Every second traveller who lands in Leh today has the same three photographs planned: the turquoise sweep of Pangong Tso, the sand dunes of Nubra Valley and a selfie at Khardung La. It is a beautiful itinerary — and also, increasingly, a crowded one. In peak season, Pangong's famous lakeside can resemble a parking lot more than a postcard.</p>

<p>But Ladakh is far bigger than its two most Instagrammed addresses. Beyond the well-worn loop lie villages where Islam and Buddhism sit side by side, plateaus where nomads still herd pashmina goats the way their ancestors did, and monasteries so remote that reaching them still requires walking, not driving. Here are seven places worth adding to your next itinerary.</p>

<h2>Turtuk: India's Last Village Before the Pakistan Border</h2>

<p>Tucked into the Shyok Valley roughly 205 km from Leh, Turtuk is unlike anywhere else in Ladakh. Until December 1971, the village belonged to Pakistan-administered territory. During the Indo-Pak war that year, the Indian Army captured it, and it has been part of India ever since. It was opened to tourists only in 2010, which is why it still feels refreshingly untouched.</p>

<p>What makes Turtuk worth the long, winding drive over Khardung La is its people. The village is home to the Balti community, whose culture fuses Central Asian, Tibetan and Ladakhi influences — distinct from the Buddhist-majority character of most of Ladakh. Locals speak Balti, an ancient dialect with strong Persian influence, and practise Islam. You can visit the modest Royal Palace Museum, walk through apricot orchards that turn the village green every summer, and taste sun-dried apricots straight from a local's kitchen. Indian travellers need an Inner Line Permit; foreign nationals require a Protected Area Permit.</p>

<h2>Hanle: Stargazing at 4,500 Metres</h2>

<p>If Turtuk is about culture, Hanle is about the cosmos. Perched at roughly 4,500 metres in the remote Changthang Plateau, Hanle is home to the Indian Astronomical Observatory (IAO), run by the Indian Institute of Astrophysics — one of the world's highest-located sites for optical, infrared and gamma-ray telescopes.</p>

<p>In December 2022, the area around Hanle was officially notified as India's first Dark Sky Reserve, spanning more than 1,000 square kilometres of high-altitude desert. Outdoor lighting is restricted, vehicle headlights are dimmed near the core zone, and street lights are capped to warm colours. For travellers, this translates into a naked-eye view of the Milky Way so sharp it can cast a faint shadow. Local villagers trained as astro-guides run homestays and telescope sessions, meaning your stargazing night directly supports the community that protects those skies. Plan around the new moon for the darkest skies.</p>

<h2>Tso Moriri: Pangong Without the Crowds</h2>

<p>Sitting deep in the Changthang Plateau at 4,522 metres, Tso Moriri is one of the highest lakes in India and, unlike Pangong, lies entirely within Indian territory — no shared border views, no crowded viewpoints, just still water and silence. The lake is part of the Tso Moriri Wetland Conservation Reserve, a Ramsar-recognised wetland sheltering migratory birds including the black-necked crane and bar-headed goose.</p>

<p>On its shores sits Korzok, one of the highest permanently inhabited villages in the world, home to a 300-year-old monastery and the Changpa — semi-nomadic herders who live in tents called "rebos" and raise the pashmina goats that produce the world's finest cashmere wool. A night here, sipping butter tea inside a Changpa tent while the lake shifts from turquoise to navy, is arguably one of the most authentic experiences left in Ladakh. The route from Leh takes 6-7 hours and closes in winter.</p>

<h2>Four More Hidden Gems</h2>

<p><strong>Uleytokpo</strong> sits between Leh and Kargil along the Indus, surrounded by orchards and dramatic cliffs. At just 70 km from Leh, it is the easiest offbeat destination on this list — popular with birdwatchers and travellers who want a peaceful base for visiting Alchi and Likir monasteries without Leh's bustle.</p>

<p><strong>Sumda Chun Monastery</strong>, dating to the 11th century, houses ancient murals and sculptures that have survived largely untouched by mass tourism. The catch: it is accessible only by a full-day trek through a narrow, dramatic gorge from the Alchi-Likir side, with no motorable road reaching its gates.</p>

<p><strong>Dha and Hanu Villages</strong>, near Kargil, are home to the Brokpa, a small Indo-Aryan community known for elaborate floral headgear and oral traditions tracing back to pre-Buddhist practices. A visit offers a genuine ethnographic encounter with one of the Himalayas' most distinct and least-documented communities.</p>

<p><strong>Phugtal Monastery</strong> in Zanskar is the showstopper. Built into a cliff face above the Tsarap Chu river, the structure appears to grow directly out of the rock — earning the nickname of a "honeycomb" clinging to the gorge. During winter, heavy snow cuts the monastery off almost entirely, with supplies carried in by mules. A 2-3 hour hike from Purne village is the shortest route; no vehicle road reaches the monastery itself.</p>

<h2>Planning Your Trip</h2>

<p>The window for all seven destinations is June to September, when roads are open and high passes are accessible. Border-adjacent areas — Turtuk, Hanle and Dha-Hanu — require an Inner Line Permit (ILP) for Indian nationals and a Protected Area Permit (PAP) for foreign travellers, both easily arranged in Leh through travel agents or online portals. Carry multiple physical copies, as checkpoints often have no internet connectivity.</p>

<p>Homestays are the backbone of offbeat Ladakh tourism. In Turtuk, Hanle, Tso Moriri and Dha-Hanu, staying with a local family is often the only accommodation option — and usually the most rewarding. Mobile coverage is patchy to non-existent, so download offline maps and treat the trip as a genuine digital detox. Most importantly, spend at least two days acclimatising in Leh before heading further out. Most of these destinations sit above 4,000 metres, and altitude sickness is the one hazard that catches every traveller, regardless of fitness.</p>"""
}

for c in candidates:
    title = c.get("title", "")
    if "Turtuk" in title or "Ladakh" in title:
        article4["topic_id"] = c["topic_id"]
        break

id4 = publish_article(article4)

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("BATCH PUBLISH COMPLETE")
print("=" * 60)
published = sum(1 for x in [id1, id2, id3, id4] if x)
print(f"Published: {published}/4 articles")
if id1: print(f"  1. [sports] {article1['headline'][:80]}")
if id2: print(f"  2. [nri-world] {article2['headline'][:80]}")
if id3: print(f"  3. [technology] {article3['headline'][:80]}")
if id4: print(f"  4. [travel] {article4['headline'][:80]}")
