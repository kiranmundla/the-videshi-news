#!/usr/bin/env python3
"""V3 Article batch insertion script for July 20, 2026 run."""
import json, subprocess, os, sys, urllib.parse
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def slugify(text):
    import re
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s[:80].strip('-')

def insert_article(article):
    """Insert article via curl and return the article ID."""
    payload = json.dumps(article)
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", payload
    ], capture_output=True, text=True)
    try:
        resp = json.loads(result.stdout)
        if isinstance(resp, list) and len(resp) > 0:
            return resp[0].get("id")
        elif isinstance(resp, dict) and resp.get("id"):
            return resp["id"]
        else:
            print(f"  ERROR inserting: {result.stdout[:200]}", file=sys.stderr)
            return None
    except:
        print(f"  ERROR parsing: {result.stdout[:200]}", file=sys.stderr)
        return None

def update_topic(topic_id, article_id):
    """Mark topic as published."""
    payload = json.dumps({"status": "published", "last_article_id": str(article_id)})
    subprocess.run([
        "curl", "-s", "-X", "PATCH",
        f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{topic_id}",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-d", payload
    ], capture_output=True, text=True)

def get_wikipedia_image(name):
    """Try to get image from Wikipedia REST API."""
    encoded = urllib.parse.quote(name.replace(' ', '_'))
    result = subprocess.run([
        "curl", "-s",
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
        "-H", "User-Agent: TheVideshi/1.0 (thevideshi.com)"
    ], capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        if data.get("originalimage", {}).get("source"):
            return data["originalimage"]["source"]
        if data.get("thumbnail", {}).get("source"):
            return data["thumbnail"]["source"]
    except:
        pass
    return None

def get_pexels_image(query):
    """Search Pexels for an image."""
    pexels_key = os.environ.get("PEXELS_API_KEY", "")
    if not pexels_key:
        return None, None
    result = subprocess.run([
        "curl", "-s",
        f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=1",
        "-H", f"Authorization: {pexels_key}"
    ], capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        if data.get("photos") and len(data["photos"]) > 0:
            photo = data["photos"][0]
            return photo["src"]["large2x"], f"Photo by {photo['photographer']} on Pexels"
    except:
        pass
    return None, None

now = datetime.now(timezone.utc).isoformat()

articles = []

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 1: Pakistan-Canada Indus Waters Treaty
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
articles.append({
    "headline": "Pakistan Seeks Canada's Help to Revive Indus Waters Treaty as 'Weaponisation of Water' Fears Grow",
    "subheadline": "Canadian Foreign Minister Anita Anand's historic visit to Pakistan marks the first by a Canadian FM in 20 years, as Islamabad seeks international backing to restore the suspended water-sharing pact with India.",
    "slug": "pakistan-canada-indus-waters-treaty-revival-2026",
    "category": "news",
    "vertical": "news",
    "article_type": "breaking",
    "status": "published",
    "published_at": now,
    "topic_id": "e8098237-6503-406f-b5db-1cc95f9f1f3f",
    "tags": ["Pakistan", "Canada", "India", "Indus Waters Treaty", "Anita Anand", "geopolitics", "water dispute"],
    "sources": ["https://www.reuters.com", "https://timesofindia.indiatimes.com", "https://www.dawn.com", "https://www.canada.ca"],
    "word_count": 680,
    "diaspora_angle": "The Indus Waters Treaty suspension directly affects India-Pakistan relations, with implications for regional stability that concerns the Indian diaspora worldwide.",
    "body": """<div class="key-takeaways"><ul>
<li>Canadian Foreign Minister Anita Anand visited Islamabad in the first such visit by a Canadian FM in two decades, as Pakistan seeks international support to restore the Indus Waters Treaty.</li>
<li>India suspended the 1960 World Bank-brokered treaty after the Pahalgam terror attack in Kashmir that killed 26 people, demanding Pakistan dismantle cross-border terror infrastructure.</li>
<li>Pakistan has described India's actions as the "weaponisation of water" and is pursuing legal options at the World Bank, the International Court of Justice, and the Permanent Court of Arbitration.</li>
<li>Canada announced over $47 million in aid and security initiatives during the visit, signaling a deepening bilateral relationship between Ottawa and Islamabad.</li>
</ul></div>

<h2>A Historic Visit Amid Regional Tensions</h2>
<p>Canadian Foreign Minister Anita Anand traveled to Islamabad this week in a visit that carries both symbolic and strategic weight — the first by a Canadian foreign minister in approximately two decades. The trip came as Pakistan intensifies its diplomatic campaign to restore the Indus Waters Treaty, a six-decade-old water-sharing agreement with India that has been suspended since the deadly Pahalgam terror attack in Kashmir.</p>

<p>During the visit, Pakistan's Deputy Prime Minister and Foreign Minister Mohammad Ishaq Dar pressed Canada for support in reviving the treaty, describing India's suspension as a dangerous precedent. "Shared waters must never be weaponized. They should remain a bridge between nations, guided by cooperation, dialogue, and respect for international law," Dar said at a recent international seminar on the treaty.</p>

<h2>The Treaty Suspension and Its Fallout</h2>
<p>India suspended the 1960 World Bank-brokered Indus Waters Treaty following the Pahalgam attack in Kashmir, in which 26 people were killed. New Delhi stated the suspension would remain in effect until "Pakistan credibly and irrevocably abjures its support for cross-border terrorism." Pakistan denies any involvement in the attack.</p>

<p>Under the original treaty, Pakistan was allocated roughly 80 percent of the water from the western rivers of the Indus system — the Indus, Jhelum, and Chenab. The suspension has deepened Pakistan's domestic water crisis, with the country already classified as water-stressed. Pakistani officials have warned that any attempt to divert water flows would be considered "an act of war."</p>

<blockquote class="pull-quote">
<p>"Water is not a bargaining chip. It is a matter of life and peace in South Asia."</p>
<cite>— Pakistan Institute of Strategic Studies, at the ISSI-CLAS Joint Seminar</cite>
</blockquote>

<h2>Pakistan's Legal Strategy</h2>
<p>Islamabad is pursuing multiple legal avenues to challenge the suspension. According to Pakistan's Minister of State for Law and Justice Aqeel Malik, the country is preparing at least three different legal actions, including raising the issue at the World Bank — the treaty's original facilitator — filing at the Permanent Court of Arbitration in The Hague, and potentially taking the matter to the International Court of Justice, alleging India has violated the 1969 Vienna Convention on the Law of Treaties.</p>

<p>"Legal strategy consultations are almost complete," Malik told Reuters, adding that decisions on which cases to pursue would be made "soon" and would likely include more than one avenue simultaneously.</p>

<h2>Canada's Expanding Role</h2>
<p>Anand's visit to Pakistan went beyond the water treaty discussion. Canada announced over $47 million in aid and security initiatives, signaling a broader deepening of ties between Ottawa and Islamabad. The two countries also discussed new avenues for trade and economic cooperation, including Canadian canola exports and a Foreign Investment Promotion and Protection Agreement.</p>

<p>The visit places Canada in a delicate diplomatic position. Ottawa has been working to rebuild its relationship with India following years of strain, while also seeking to maintain and expand its ties with Pakistan. Anand met with Indian External Affairs Minister S. Jaishankar as recently as March 2026 at the G7 Foreign Ministers' Meeting in France, where both sides reaffirmed their commitment to a bilateral roadmap.</p>

<h2>What's Next</h2>
<p>Pakistan is expected to formally pursue its legal challenges in the coming weeks. The outcome could set precedents for transboundary water disputes globally. India has shown no indication of lifting the suspension, maintaining that it remains contingent on Pakistan taking credible action against terrorism.</p>

<p>For the 240 million people in Pakistan who depend on the Indus river system for agriculture and drinking water, the stakes could not be higher. The dispute has also drawn attention from China and other South Asian states with transboundary river concerns, as Pakistan seeks to build a broader coalition against what it calls India's "hydro-terrorism."</p>""",
    "image_url": None,  # Will be set below
    "image_caption": "The Indus River flows through Pakistan's agricultural heartland. Pakistan and India have been locked in a dispute over the 1960 Indus Waters Treaty since India suspended it following the Pahalgam attack.",
    "image_attribution": "Pexels"
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 2: ICICI Bank Workforce Decline
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
articles.append({
    "headline": "ICICI Bank Trims Over 5,100 Jobs in FY26, Leading Workforce Cuts Across India's Private Banks",
    "subheadline": "India's second-largest private lender saw its employee count drop to 124,029 as automation reshapes banking operations, even as the bank added 528 new branches.",
    "slug": "icici-bank-workforce-decline-fy26-private-banks",
    "category": "markets-finance",
    "vertical": "markets-finance",
    "article_type": "breaking",
    "status": "published",
    "published_at": now,
    "topic_id": "c7cdad2a-8b50-488c-bcce-5f2a143f5ac3",
    "tags": ["ICICI Bank", "banking", "automation", "India economy", "HDFC Bank", "Axis Bank", "jobs"],
    "sources": ["https://www.thehindubusinessline.com", "https://niftytrader.in", "https://www.livemint.com"],
    "word_count": 620,
    "diaspora_angle": "NRI investors with significant holdings in Indian private bank stocks should monitor how automation-driven workforce changes affect profitability and service quality.",
    "body": """<div class="key-takeaways"><ul>
<li>ICICI Bank's permanent workforce fell by 5,148 employees in FY26 to 124,029, the steepest decline among India's major private banks.</li>
<li>HDFC Bank cut 3,343 jobs, Axis Bank reduced headcount by 3,153, and Kotak Mahindra Bank trimmed 1,269 positions during the same period.</li>
<li>The reductions came even as banks expanded their branch networks — ICICI alone added 528 new branches, taking its total to 7,511.</li>
<li>Automation of routine banking tasks such as account opening, loan processing, and customer service is driving the structural shift.</li>
</ul></div>

<h2>A Sector-Wide Shift</h2>
<p>ICICI Bank, India's second-largest private sector lender, recorded the biggest workforce reduction among its peers in the financial year ending March 2026, shedding 5,148 employees. The bank's headcount stood at 124,029 at the close of FY26, down from 129,177 a year earlier, according to its latest annual disclosures.</p>

<p>The decline continues a trend that began in FY25, when ICICI Bank had already reduced its workforce by roughly 6,000 employees. By its own admission during a May 2025 earnings call, the bank said it did not expect net additions to headcount in FY26 — a projection that proved accurate.</p>

<h2>Automation Reshapes the Branch</h2>
<p>The reductions are not a sign of business contraction. ICICI Bank added 528 branches in FY26, expanding its network to 7,511 locations. The apparent contradiction — fewer employees but more branches — reflects a fundamental restructuring of how private banks operate.</p>

<p>Routine, high-volume tasks such as account opening, loan origination and processing, payments, and basic customer service are increasingly handled through automation. This frees branch staff to focus on higher-value activities: sales, relationship management, and advisory services.</p>

<blockquote class="pull-quote">
<p>"Post a high frenzied hiring in CY23, we are seeing hiring cool down as banks redirect investment toward technology."</p>
<cite>— Asutosh Mishra, Ashika Stock Broking</cite>
</blockquote>

<h2>Peers Follow the Same Playbook</h2>
<p>ICICI Bank was not alone in trimming its workforce. HDFC Bank, India's largest private lender, saw its employee count drop by 3,343 to 211,178. The decline accelerated in the March quarter alone, with approximately 4,000 employees reduced sequentially. Notably, HDFC Bank is reshuffling its workforce composition — reducing non-supervisory staff while adding positions at junior management levels and above.</p>

<p>Axis Bank's headcount fell by about 3,153 to just over 101,300 employees. Kotak Mahindra Bank recorded a decline of 1,269, bringing its total to 74,054. All four banks continued to expand their physical branch networks during the same period.</p>

<p>In contrast, Yes Bank bucked the trend with a marginal increase to 29,573 employees from 28,687.</p>

<h2>The Bigger Picture</h2>
<p>The workforce compression mirrors a broader trend across India's banking sector. Post-pandemic hiring surges have given way to a more measured approach, as banks channel spending toward technology infrastructure. ICICI Bank's employee attrition rate had already fallen to 18 percent in FY25, the lowest among large private sector peers, reflecting improved retention even as absolute headcount declined.</p>

<p>For investors, the workforce reduction is a positive signal for operating efficiency. Lower headcount per branch, combined with growing digital transaction volumes, should improve cost-to-income ratios over time. But the transition raises questions about the quality of in-branch service and the social impact of automation in a country where banking jobs have long been a pathway to the middle class.</p>

<h2>What to Watch</h2>
<p>Analysts will be monitoring whether the pace of workforce reduction moderates in FY27 or accelerates as AI-driven tools move beyond routine tasks into areas like credit assessment and portfolio advisory. The banks' Q1 FY27 earnings calls, expected in the coming weeks, should provide updated guidance on hiring plans and technology spending trajectories.</p>""",
    "image_url": None,
    "image_caption": "ICICI Bank's corporate headquarters in Mumbai. The bank's workforce fell by over 5,100 employees in FY26 as automation transforms private banking operations across India.",
    "image_attribution": "Wikimedia Commons"
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 3: ZEE5 Multilingual Content Slate
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
articles.append({
    "headline": "ZEE5 Unveils Its Biggest Multilingual Content Slate Across Seven Languages",
    "subheadline": "India's largest homegrown streaming platform announced an expansive lineup spanning Hindi, Tamil, Telugu, Marathi, Malayalam, Kannada, and Bangla, featuring originals, franchise revivals, and AI-powered storytelling.",
    "slug": "zee5-multilingual-content-slate-seven-languages-2026",
    "category": "entertainment",
    "vertical": "entertainment",
    "article_type": "breaking",
    "status": "published",
    "published_at": now,
    "topic_id": "4a0fc03f-3ca2-4d40-b552-aed386e64d9d",
    "tags": ["ZEE5", "OTT", "streaming", "Bollywood", "Indian entertainment", "multilingual", "Varun Dhawan"],
    "sources": ["https://www.bestmediainfo.com", "https://www.bollywoodhungama.com", "https://mediabrief.com", "https://www.iwmbuzz.com"],
    "word_count": 600,
    "diaspora_angle": "ZEE5's expanded multilingual slate gives diaspora audiences access to premium content in their native languages, reinforcing cultural connections across Hindi and six regional languages.",
    "body": """<div class="key-takeaways"><ul>
<li>ZEE5 announced its most ambitious content slate yet, spanning seven languages: Hindi, Tamil, Telugu, Marathi, Malayalam, Kannada, and Bangla.</li>
<li>The Hindi lineup includes a biopic on cricketer Vinod Kambli, a new season of Rangbaaz starring Mohit Raina, and films featuring Varun Dhawan, Bobby Deol, and Kangana Ranaut.</li>
<li>Returning franchises include The Zee Horror Show revival, Rangbaaz Season 4, and audience favourites Shwetkali and Lalbazaar in Bangla.</li>
<li>ZEE5 is introducing AI-powered storytelling formats alongside traditional series, films, live sports, animation, and children's entertainment.</li>
</ul></div>

<h2>A Seven-Language Statement of Intent</h2>
<p>ZEE5 has unveiled what it calls its largest multilingual content slate to date, a sweeping lineup of original series, theatrical premieres, franchise revivals, and new formats designed to serve audiences across India's linguistic landscape. The announcement spans Hindi, Tamil, Telugu, Marathi, Malayalam, Kannada, and Bangla — essentially every major language market in the country.</p>

<p>The platform has partnered with an extensive roster of production houses, including Jio Studios, Maddock Films, Annapurna Studios, and Pen Studios, among others. Regional collaborations stretch from Thespian Films in Malayalam to KVN Productions in Kannada and Acropolis Entertainment in Bangla.</p>

<h2>Hindi Headliners</h2>
<p>The Hindi slate features several high-profile projects. Kambli, a biographical project inspired by the life of former cricketer Vinod Kambli, is among the most anticipated originals. The Scam: Leaked and Coffee King join the original series roster, while the nostalgia-driven Jeena Isi Ka Naam Hai 2.0 returns with R. Madhavan as host.</p>

<p>Franchise revivals include Rangbaaz Season 4, starring Mohit Raina and Arunoday Singh, Janaawar 2 with Bhuvan Arora, and Bakaiti Season 2 featuring Rajesh Telang and Sheeba Chaddha. ZEE5 is also resurrecting The Zee Horror Show, a cult classic from Indian television.</p>

<p>On the film side, Hai Jawani Toh Ishq Hona Hai stars Varun Dhawan, Pooja Hegde, and Mouni Roy, while Bandar features Bobby Deol and Sanya Malhotra. Other titles include Bharat Bhagya Vidhata with Kangana Ranaut and Ghamasaan featuring Arshad Warsi and Pratik Gandhi.</p>

<h2>Regional Markets Get Premium Treatment</h2>
<p>In Tamil, audiences can expect the return of Koose Munisamy Veerappan and new originals like Ananthakaalam and Thee Kural. The film slate is headlined by Demonte Colony 3 and Hi!, starring Nayanthara and Kavin.</p>

<p>Telugu viewers get originals such as Shrimathi starring Nivetha Thomas and the return of talk show Jayammu Nishchayammu Ra, alongside anticipated films like Venky Anil 5 and NBK111. In Kannada, Ayyana Mane returns with a new season, while Bitcoin Scam and Operation Bangara expand the originals catalog.</p>

<p>Malayalam premieres include A Queen, Malabar Cup, and Kerala Underground, an independent rap battle show. Marathi audiences get Hey Kay Navin? Season 2 and new original Aga Aai, Aaho Aai. In Bangla, audience favourites Shwetkali and Lalbazaar return with new seasons.</p>

<blockquote class="pull-quote">
<p>"This slate is our biggest statement of intent yet, bringing together some of India's most celebrated filmmakers, production houses, and performers across seven languages."</p>
<cite>— Tejkarran Singh Bajaj, Business Head, ZEE5 India</cite>
</blockquote>

<h2>AI Enters the Mix</h2>
<p>Beyond traditional content, ZEE5 is experimenting with AI-powered storytelling formats, though specific details remain sparse. The platform is also building what it describes as a "future-ready entertainment platform" with deeper personalization and smarter technology.</p>

<p>The announcement comes as India's streaming market grows increasingly competitive, with Netflix, Amazon Prime Video, Disney+ Hotstar, and JioCinema all vying for subscribers. ZEE5's bet on language-specific content reflects a growing industry consensus that India's OTT growth will come from regional audiences, not just Hindi-speaking metros.</p>""",
    "image_url": None,
    "image_caption": "ZEE5 logo displayed at a media event. The platform announced its largest content slate spanning seven Indian languages with originals, franchise revivals, and AI-powered formats.",
    "image_attribution": "ZEE5/Bollywood Hungama"
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 4: Dr Dangs Lab Cancer Detection
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
articles.append({
    "headline": "India Gets Its First Multi-Cancer Blood Test as Dr Dangs Lab Partners With Zydus and Guardant Health",
    "subheadline": "The Shield test can screen for 10 common cancers from a single blood draw, marking a significant step toward early detection in a country where most cancers are diagnosed at advanced stages.",
    "slug": "dr-dangs-lab-guardant-health-shield-cancer-test-india",
    "category": "health",
    "vertical": "health",
    "article_type": "breaking",
    "status": "published",
    "published_at": now,
    "topic_id": "47d837b3-aef5-4237-a36f-7f17b23e1a2f",
    "tags": ["cancer screening", "Guardant Health", "Zydus Lifesciences", "Dr Dangs Lab", "healthcare", "India"],
    "sources": ["https://www.devdiscourse.com", "https://www.thehindubusinessline.com", "https://www.pharmabiz.com", "https://medicaldialogues.in"],
    "word_count": 580,
    "diaspora_angle": "NRIs with family in India can now access advanced multi-cancer screening through a simple blood test, potentially enabling early detection for parents and relatives back home.",
    "body": """<div class="key-takeaways"><ul>
<li>Dr Dangs Lab has signed a strategic partnership with Zydus Lifesciences to offer the Shield multi-cancer detection test nationwide, making it the first laboratory in India to do so.</li>
<li>The Shield test, developed by U.S.-based Guardant Health, screens for 10 common cancers — including breast, lung, colorectal, and pancreatic — from a single blood draw.</li>
<li>India's cancer burden is projected to rise to 2.08 million cases by 2040, a 57.5% increase from 2020, with most cases still diagnosed at advanced stages.</li>
<li>The test has received Breakthrough Device Designation from the U.S. FDA, recognizing its potential for more effective screening than existing methods.</li>
</ul></div>

<h2>A Blood Test for 10 Cancers</h2>
<p>Dr Dangs Lab, one of India's established diagnostic laboratories, has partnered with Zydus Lifesciences to become the first lab in the country to offer Guardant Health's Shield multi-cancer detection test on a nationwide basis. The announcement follows a similar partnership between Zydus and Apollo Hospitals earlier this month, signaling a rapid rollout of the technology across India's healthcare landscape.</p>

<p>The Shield test is a methylation-based blood test that can detect signals associated with 10 common cancers — bladder, breast, colorectal, esophageal, gastric, liver, lung, ovarian, pancreatic, and prostate — through a single blood draw. It is designed for individuals aged 45 and above who are at average risk for cancer.</p>

<h2>Why It Matters for India</h2>
<p>India diagnosed over 1.41 million new cancer cases in 2022, according to the Indian Council of Medical Research, and that number is projected to rise to 2.08 million by 2040 — a 57.5 percent increase from 2020. Breast cancer remains the leading cause of cancer-related mortality among women, while oral cancer is the most prevalent form among men.</p>

<p>The critical challenge is timing. Most cancers in India are diagnosed at advanced stages, when treatment options are limited and survival rates drop significantly. Conventional screening methods are largely organ-specific — mammograms for breast cancer, colonoscopies for colorectal cancer — and screening rates remain low and uneven across the country.</p>

<p>A single blood test that screens for multiple cancer types simultaneously could change that calculus, particularly for populations who may not have access to or awareness of individual screening programs.</p>

<h2>The Technology Behind Shield</h2>
<p>Shield works by analyzing cell-free DNA in the blood for methylation patterns associated with cancer. The test has received Breakthrough Device Designation from the U.S. Food and Drug Administration, a recognition reserved for devices that offer significant advantages over existing options. In clinical studies, Shield detected 83 percent of colorectal cancers, though the company notes that colonoscopy should remain the prioritized screening option where available.</p>

<blockquote class="pull-quote">
<p>"The future of medicine lies not only in treating disease, but in preventing it and detecting it at its earliest, most treatable stages."</p>
<cite>— Dr. Prathap C. Reddy, Chairman, Apollo Hospitals Group</cite>
</blockquote>

<h2>Expanding Access</h2>
<p>Zydus Lifesciences holds the exclusive rights to commercialize Shield in India. The partnership with Dr Dangs Lab follows the Zydus-Apollo Hospitals MoU signed earlier in July, creating a two-track distribution strategy — through hospital networks and independent diagnostic laboratories. Zydus is already one of India's leading oncology drug manufacturers, with an expanding pipeline of biosimilars and targeted therapies.</p>

<p>The test's pricing in India has not been publicly disclosed, and affordability will be a key factor in determining how widely it is adopted. For NRIs concerned about cancer screening for aging parents back home, the availability of a simple blood-based test that covers 10 cancer types through established labs and hospital networks represents a meaningful improvement in access to preventive care.</p>""",
    "image_url": None,
    "image_caption": "A laboratory technician processes blood samples for diagnostic testing. Dr Dangs Lab has become the first laboratory in India to offer Guardant Health's multi-cancer detection blood test nationwide.",
    "image_attribution": "Pexels"
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 5: Rohit Sharma Retirement
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
articles.append({
    "headline": "Rohit Sharma Dismisses Retirement Talk After Stunning Lord's Century: 'Let the Noise Be There'",
    "subheadline": "The former India captain scored 138 off 110 balls at Lord's, ending a lean run of 11 ODIs without a century, as the BCCI firmly denied reports that the third ODI would be his last international match.",
    "slug": "rohit-sharma-retirement-lords-century-odi-england-2026",
    "category": "sports",
    "vertical": "sports",
    "article_type": "breaking",
    "status": "published",
    "published_at": now,
    "topic_id": "378ce400-72e7-4e79-b461-73a60e4eee2e",
    "tags": ["Rohit Sharma", "cricket", "BCCI", "ODI", "England tour", "Lords", "retirement"],
    "sources": ["https://www.reuters.com", "https://www.cricketcountry.com", "https://www.cricbuzz.com", "https://www.insidesport.in"],
    "word_count": 590,
    "diaspora_angle": "Rohit Sharma remains one of the most followed cricketers among the Indian diaspora, and his ODI future directly affects India's planning for the 2027 World Cup.",
    "body": """<div class="key-takeaways"><ul>
<li>Rohit Sharma scored a blistering 138 off 110 balls in the third ODI at Lord's, ending a lean run of 11 ODIs without a century, though India lost the match and the series 2-1 to England.</li>
<li>The BCCI firmly denied reports that the Lord's match would be Rohit's final international appearance, with Secretary Devajit Saikia stating he remains part of India's ODI plans.</li>
<li>Rohit dismissed retirement speculation, saying: "The noise since I made my debut was there. And till the time I'm going to stay here, it's always going to be there."</li>
<li>India next travel to Zimbabwe for a T20I series from July 23-26 before touring Sri Lanka for Tests in August.</li>
</ul></div>

<h2>A Century to Silence the Doubters</h2>
<p>Rohit Sharma answered retirement speculation the way he knows best — with the bat. The 39-year-old former India captain struck 138 off 110 balls in the third and deciding ODI against England at Lord's on Sunday, a vintage display of aggressive strokeplay that briefly made India's unsuccessful chase of 310 look achievable.</p>

<p>The century — his 34th in ODIs — ended a lean stretch of 11 innings without reaching three figures, a drought that had fuelled growing questions about his place in the team ahead of the 2027 ODI World Cup in South Africa, Zimbabwe, and Namibia.</p>

<p>Despite Sharma's heroics, India fell 27 runs short, conceding the series 2-1. But it was the off-field narrative that dominated the post-match conversation.</p>

<h2>BCCI Shuts Down Retirement Reports</h2>
<p>The retirement speculation had intensified during the second ODI in Cardiff, when reports emerged suggesting that head coach Gautam Gambhir and chief selector Ajit Agarkar had privately conveyed to Sharma that he was no longer part of India's long-term plans for the 2027 World Cup. The reports claimed the management was eager to integrate younger options — most notably Yashasvi Jaiswal — at the top of the order alongside captain Shubman Gill.</p>

<p>The BCCI moved quickly to quash the narrative. Secretary Devajit Saikia issued a direct statement denying any truth to reports of an impending farewell. "Neither the Lord's match nor the series will be Rohit Sharma's last," Saikia stated, adding that Sharma "remains an essential fixture of the ODI squad" for as long as the selectors retain him.</p>

<p>Gill backed that message in his post-match press conference: "Rohit Sharma has not told us anything. No discussion in the team; it's all media talk."</p>

<h2>'Let the Noise Be There'</h2>
<p>Rohit himself addressed the speculation with characteristic composure. Speaking to the team's social media channel after the Lord's innings, he drew a clear line between his job and the commentary surrounding it.</p>

<blockquote class="pull-quote">
<p>"My job is with the bat — come and play, represent my country, represent the team. The noise since I made my debut was there. If there's no noise, there's no fun."</p>
<cite>— Rohit Sharma, after the Lord's ODI</cite>
</blockquote>

<p>In 288 ODIs, Sharma has amassed 11,895 runs at an average of 49, with 34 centuries — including three double centuries. He retired from T20 Internationals after leading India to the T20 World Cup title in Barbados in June 2025 but has continued to play ODIs.</p>

<h2>What's Next for India</h2>
<p>India travel to Zimbabwe for a three-match T20I series from July 23-26 — a squad where Sharma is unlikely to feature given his T20I retirement. The focus then shifts to a Test series in Sri Lanka in August, where his inclusion will further clarify his standing across formats.</p>

<p>For now, at 39, Rohit Sharma has made his position clear: he is not going anywhere. The only remaining question is whether his body and form will cooperate through to the 2027 World Cup — and Sunday's Lord's century suggested both are still firmly on his side.</p>""",
    "image_url": None,
    "image_caption": "Rohit Sharma celebrates after reaching his century at Lord's during the third ODI against England. The 39-year-old dismissed retirement speculation after scoring 138 off 110 balls.",
    "image_attribution": "Reuters"
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 6: India Green Hydrogen
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
articles.append({
    "headline": "India's ₹10 Lakh Crore Green Hydrogen Opportunity: The Missing Link in the Energy Transition",
    "subheadline": "From electrolysers to export terminals, India's National Green Hydrogen Mission is unlocking a massive investment wave — but key gaps in infrastructure and cost competitiveness remain.",
    "slug": "india-green-hydrogen-10-lakh-crore-opportunity-2026",
    "category": "technology",
    "vertical": "technology",
    "article_type": "breaking",
    "status": "published",
    "published_at": now,
    "topic_id": "673c6778-7351-4549-83cc-91108ff0e800",
    "tags": ["green hydrogen", "India", "clean energy", "NTPC", "Adani", "electrolysers", "National Green Hydrogen Mission"],
    "sources": ["https://www.financialexpress.com", "https://energetica-india.net", "https://solarquarter.com", "https://knnindia.co.in"],
    "word_count": 640,
    "diaspora_angle": "India's green hydrogen sector represents a major emerging investment opportunity for NRI investors, with government-backed production incentives and an estimated ₹10 lakh crore in capital deployment by 2030.",
    "body": """<div class="key-takeaways"><ul>
<li>India's National Green Hydrogen Mission targets 5 million tonnes of annual production and 20 GW of electrolyser capacity by 2030, representing an estimated ₹10 lakh crore ($120 billion) investment opportunity.</li>
<li>The ₹17,000 crore SIGHT programme and production-linked incentives are driving down costs, with green hydrogen expected to fall from $5/kg today to $0.8-$3.3/kg by 2030.</li>
<li>Key players include NTPC (pilot projects in Gujarat and Leh), Adani Green Energy (targeting 3 GW by 2030), and Reliance Industries, along with new BESS manufacturing facilities in Bengaluru and Pune.</li>
<li>India's abundant solar resources give it a potential competitive advantage in producing the world's lowest-cost green hydrogen, but electrolyser capacity remains under 1 GW against a 20 GW target.</li>
</ul></div>

<h2>The Scale of the Opportunity</h2>
<p>India is betting big on green hydrogen. The National Green Hydrogen Mission, launched in January 2023, aims to produce 5 million tonnes of green hydrogen annually and build 20 GW of electrolyser manufacturing capacity by 2030. According to a report by Avener Capital, this mission unlocks an estimated ₹10 lakh crore in investment — making it one of the largest clean energy buildouts in the developing world.</p>

<p>The ambition is clear: reduce fossil fuel imports by ₹1 lakh crore, cut 50 million metric tonnes of greenhouse gas emissions, and position India as a global green hydrogen exporter. But between ambition and execution, significant gaps remain.</p>

<h2>The Cost Challenge</h2>
<p>Green hydrogen currently costs between $3.80 and $5.80 per kilogram in India — well above the threshold where it can compete with natural gas or grey hydrogen in industrial applications. The government projects costs will fall to $0.80-$3.30/kg by 2030, driven by declining renewable energy prices, lower capital expenditure on electrolysers, and tax reforms.</p>

<p>The ₹17,000 crore Strategic Interventions for Green Hydrogen Transition (SIGHT) programme is the primary policy lever. The Solar Energy Corporation of India (SECI) has already awarded 8.58 lakh MTPA of green hydrogen production and 2.3 GW of electrolyser manufacturing under this initiative. Production-linked incentives of ₹5,258 crore for hydrogen and ₹4,440 crore for electrolysers are being distributed over three years.</p>

<h2>Who's Building What</h2>
<p>NTPC, India's largest power utility, is leading the public sector charge with multiple pilot projects: hydrogen-blended natural gas at its Kawas plant in Gujarat, a green hydrogen filling station in Leh, and hydrogen with carbon capture at Vindhyachal. Its renewable subsidiary, NTPC Green Energy, is expanding rapidly into hydrogen production.</p>

<p>Adani Green Energy, India's largest renewable energy company, is piloting green hydrogen blending with natural gas in Ahmedabad and targeting 3 GW of green hydrogen capacity by 2030. The company's 17.2 GW of operational renewable capacity provides the feedstock for hydrogen production.</p>

<p>Meanwhile, battery energy storage is scaling up in parallel. Midwest Energy recently commissioned a 1.2 GWh BESS manufacturing facility in Bengaluru, targeting ₹1,000 crore in annual revenue. AmpereHour Energy opened a facility in Pune with 5 GWh planned capacity, and Waaree ESS launched a 5.15 GWh BESS container manufacturing plant.</p>

<blockquote class="pull-quote">
<p>"India has a competitive advantage: abundant solar resources mean low-cost renewable electricity, which means potentially the lowest-cost green hydrogen in the world."</p>
<cite>— Motilal Oswal Research</cite>
</blockquote>

<h2>The Gap Between Target and Reality</h2>
<p>India's current electrolyser capacity is under 1 GW — against a target of 20 GW by 2030. The Council on Energy, Environment and Water estimates the country will need to deploy 135 GW of additional renewable energy capacity and invest ₹7.6 lakh crore in renewables alone to hit its hydrogen production targets.</p>

<p>Port infrastructure is another bottleneck. Key ports like Kandla, Tuticorin, and Kakinada are being developed to support green hydrogen and ammonia exports, but construction timelines remain uncertain.</p>

<h2>What to Watch</h2>
<p>For investors, the green hydrogen theme in India is a long-duration play. Near-term catalysts include the next round of SECI tenders, state-level policy announcements from Maharashtra, Gujarat, and Karnataka, and quarterly updates from NTPC and Adani on project commissioning timelines. The Budget for FY27, expected in February, will signal whether the government plans to scale up the ₹600 crore annual allocation — a figure that many analysts consider inadequate given the mission's ambitions.</p>""",
    "image_url": None,
    "image_caption": "Solar panels at a renewable energy installation in Rajasthan. India's abundant solar resources are central to its ambition to produce the world's cheapest green hydrogen by 2030.",
    "image_attribution": "Pexels"
})

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Now source images and insert
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print(f"\n{'='*60}")
print(f"INSERTING {len(articles)} ARTICLES")
print(f"{'='*60}\n")

# Image sourcing
image_queries = [
    ("Indus River Pakistan", "Indus River"),  # Article 1
    ("ICICI Bank", "ICICI Bank"),  # Article 2
    None,  # Article 3 - skip, use None
    ("blood test laboratory", "blood test cancer screening"),  # Article 4
    ("Rohit Sharma", "Rohit Sharma cricket"),  # Article 5
    ("solar energy India", "solar panels India renewable"),  # Article 6
]

for i, article in enumerate(articles):
    # Try to get image
    if image_queries[i] is not None:
        wiki_name, pexels_query = image_queries[i]
        # Try Wikipedia first
        img = get_wikipedia_image(wiki_name)
        if img:
            article["image_url"] = img
            article["image_attribution"] = "Wikimedia Commons"
            print(f"  Image ({article['category']}): Wikipedia ✓")
        else:
            # Try Pexels
            img, attr = get_pexels_image(pexels_query)
            if img:
                article["image_url"] = img
                article["image_attribution"] = attr or "Pexels"
                print(f"  Image ({article['category']}): Pexels ✓")
            else:
                print(f"  Image ({article['category']}): No image found")
    else:
        print(f"  Image ({article['category']}): Skipped")

# Insert articles
results = []
for article in articles:
    # Remove None image_url
    if article.get("image_url") is None:
        article.pop("image_url", None)
        article.pop("image_caption", None)
        article.pop("image_attribution", None)
    
    topic_id = article.pop("topic_id")
    
    art_id = insert_article(article)
    if art_id:
        update_topic(topic_id, art_id)
        results.append({
            "id": art_id,
            "headline": article["headline"],
            "category": article["category"],
            "slug": article["slug"]
        })
        print(f"  ✓ [{article['category']}] {article['headline']}")
    else:
        print(f"  ✗ [{article['category']}] {article['headline']} — FAILED")

print(f"\n{'='*60}")
print(f"RESULTS: {len(results)}/{len(articles)} articles published")
for r in results:
    print(f"  [{r['category']}] {r['headline']}")
print(f"{'='*60}")
