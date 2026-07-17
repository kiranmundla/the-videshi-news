#!/usr/bin/env python3
"""V2 batch writer — insert articles into p2_articles."""
import json, os, sys, subprocess, requests, urllib.parse, uuid, re
from datetime import datetime, timezone

# Load env
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def sb_insert(article):
    """Insert article into p2_articles via REST API."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    hdrs = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    r = requests.post(url, headers=hdrs, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            return data[0]
        return data
    print(f"  ✗ Insert failed {r.status_code}: {r.text[:300]}")
    return None

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
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
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
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                })
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

def make_slug(headline, max_len=80):
    """Generate URL slug from headline."""
    slug = re.sub(r'[^a-z0-9\s-]', '', headline.lower())
    slug = re.sub(r'[\s]+', '-', slug.strip())
    slug = slug[:max_len].rstrip('-')
    date_suffix = datetime.now(timezone.utc).strftime('%Y%m%d')
    return f"{slug}-{date_suffix}"


# ── Article 1: H-1B Fraud Investigation ──────────────────────────────────────

article1 = {
    "headline": "H-1B Fraud Probe Escalates: DOL Inspector General Prepares Search Warrants as Political Pressure Mounts",
    "subheadline": "The Department of Labor's Office of Inspector General is writing affidavits for search warrants in what officials call 'the most aggressive action against foreign labor fraud' — a move that could reshape how hundreds of thousands of Indian professionals work in America.",
    "category": "immigration",
    "article_type": "standard",
    "status": "published",
    "is_featured": True,
    "body": """The U.S. Department of Labor's Office of Inspector General has dramatically escalated its investigation into H-1B visa fraud, with officials confirming they are actively preparing affidavits to obtain search warrants — a sign that criminal proceedings may be imminent.

## A Multi-Agency Crackdown

Inspector General Anthony D'Esposito, who is leading the probe, confirmed to the New York Post that his team has identified specific areas of abuse. "We have areas where we're already in the process of writing up affidavits to swear out search warrants," he said.

The investigation operates under Vice President JD Vance's Task Force to Eliminate Fraud, created by executive order in March 2026. The DOL OIG is working alongside the Department of Justice and Department of Homeland Security, making it one of the broadest inter-agency probes into employment-based visa fraud in recent memory.

D'Esposito's language has been unusually pointed for a federal inspector general. "This isn't just paperwork fraud — it's the exploitation of vulnerable workers, forced labor, the displacement of American workers, and abusive human trafficking," he said in a statement. "My top priorities are exposing fraud, protecting American workers, and putting criminals in cuffs."

## The Political Dimension

The investigation comes amid intensifying political rhetoric against the H-1B program. Representative Riley Moore (R-WV) told Fox News he believes "the H-1B visa program is a scam" and revealed growing bipartisan support in Congress for abolishing or radically restructuring it.

"We shipped all our manufacturing jobs overseas and people were told to 'learn how to code,'" Moore said. "Well, now they're being replaced with the H-1B visa workers on the coding jobs as well."

The political firestorm was further fueled when Microsoft's Xbox gaming division laid off 1,600 workers — while the parent company had been approved for 2,273 H-1B visas in the current fiscal year alone. The juxtaposition galvanized critics who argue the program has been stretched far beyond its original intent of filling genuine skills gaps.

## What It Means for Indian Professionals

Indian nationals receive approximately 70 percent of all approved H-1B petitions, according to federal data. Any systemic changes to the program would disproportionately affect the Indian diaspora, which has relied on H-1B as a primary pathway into the American workforce for decades.

The Department of Homeland Security has previously suggested that as many as one-fifth of H-1B petitions may be fraudulent — though immigration attorneys dispute this figure and argue that the vast majority of Indian H-1B holders are legitimate professionals filling critical roles in technology, healthcare, and engineering.

The investigation's scope extends to the PERM labor certification program, which is the first step in employer-sponsored green card applications. Any tightening of PERM processing could compound the already decades-long green card backlog that Indian nationals face, with some applicants looking at wait times exceeding 100 years.

## A Broader Generational Argument

D'Esposito framed the investigation in generational terms. "H-1B abuse isn't just about jobs. It's about whether young Americans still believe they have a fair shot at the American dream," he said. "When you grew up in a household where you're constantly hearing that we're not good enough — that the foreign labor is not only cheaper, but they are more sophisticated, they're more talented — what does that do?"

Census data shows a record 25 million Americans under 35 are currently living with their parents, a statistic that officials are connecting to broader economic anxieties about job displacement.

For Indian H-1B holders and those aspiring to work in the United States, the coming weeks could prove pivotal. The trajectory of this investigation — from subpoenas to search warrants to potential indictments — will likely determine whether the program undergoes incremental reform or faces the existential threat that some in Congress are now openly advocating.

*Sources: New York Post, Fox News, Daily Caller, U.S. Department of Labor OIG*""",
    "sources": [
        {"url": "https://nypost.com/2026/07/15/business/labor-dept-h-1b-visa-crackdown-about-more-than-fraud/", "name": "New York Post"},
        {"url": "https://www.foxnews.com/politics/demand-end-scam-visa-program-replacing-american-workers-surges", "name": "Fox News"},
        {"url": "https://dailycaller.com/2026/07/16/foreign-owned-bank-h1b-visa-fraud/", "name": "Daily Caller"},
        {"url": "https://www.dol.gov/agencies/oig/", "name": "U.S. DOL OIG"}
    ],
    "tags": ["H-1B visa", "fraud investigation", "DOL", "JD Vance", "immigration reform"],
    "urgency": "breaking",
    "newsworthiness": 32,
    "diaspora_impact": 19,
    "prominence": 22,
    "diaspora_angle": "Indian nationals hold 70% of H-1B visas; this investigation could reshape the primary pathway for Indian professionals into the US workforce and compound the already decades-long green card backlog.",
    "image_search_query": "H-1B visa United States Capitol",
    "image_must_show": "US government building or immigration-related imagery",
    "vertical": "diaspora",
}

# ── Article 2: F-1 Student Visa Rule Changes ──────────────────────────────────

article2 = {
    "headline": "Proposed F-1 Visa Rule Changes Could Shut Down 'Day 1 CPT' Pathway for Thousands of Indian Students",
    "subheadline": "New federal proposals would tighten student visa regulations, cut grace periods in half, and potentially end the workaround that thousands of Indian graduates rely on after repeated H-1B lottery rejections.",
    "category": "immigration",
    "article_type": "standard",
    "status": "published",
    "is_featured": True,
    "body": """A proposed overhaul of F-1 student visa regulations could fundamentally alter the path that thousands of Indian students and graduates take to remain in the United States, according to immigration experts who warn the changes would close one of the most widely used workarounds in the system.

## The Day 1 CPT Lifeline at Risk

Under current rules, Indian graduates who fail to secure an H-1B visa through the annual lottery can re-enroll in another academic program and continue working legally through Curricular Practical Training (CPT) — a pathway commonly known as "Day 1 CPT" because it allows work authorization from the first day of enrollment.

Immigration attorney Emily Goldman warned that the proposed framework would make this route significantly narrower. "For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorization to continue working,'" she told The Indian Eye.

The change would affect a substantial population. Indian students form one of the largest international student groups in the United States and account for a significant share of H-1B lottery applicants. Many who enter the lottery multiple times without success currently rely on Day 1 CPT as their only legal option to continue working.

## Grace Period Cut in Half

The proposals also include reducing the post-status grace period for F-1 students from 60 days to 30 days. This window is the time graduates have after their visa status ends to either secure alternative immigration status or prepare to leave the country.

Cutting it by half would leave graduates with significantly less time to explore options like H-1B sponsorship, O-1 visas for extraordinary ability, or other employment-based pathways. For students whose companies are working through the sponsorship process, the compressed timeline could mean the difference between staying legally and becoming undocumented.

## Impact on US Tech and AI Workforce

Goldman noted that the effects would extend far beyond individual students. "There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent," she said.

Foreign nationals make up a substantial portion of the U.S. artificial intelligence talent pool. Indian professionals working in AI, machine learning, software engineering, and data science could face significant uncertainty if existing immigration pathways become more restrictive.

Companies may respond in several ways: becoming more cautious about hiring international graduates, seeking alternative immigration solutions like cap-exempt H-1B programs at universities and research institutions, or pursuing O-1 visas for highly accomplished professionals.

"The companies will either struggle because they won't have the talent or they will have to get creative and find alternate solutions," Goldman added.

## A Tightening Landscape

The proposed F-1 changes come alongside the separate H-1B fraud investigation being conducted by the Department of Labor's Inspector General and a broader political push to reduce reliance on foreign workers.

Under the proposed framework, many routine changes of status that were previously handled at the school level through SEVP (Student and Exchange Visitor Program) would require formal immigration filings with USCIS — adding cost, complexity, and processing delays to transitions that were once straightforward.

For Indian families who have invested heavily in U.S. education — often spending $50,000 to $100,000 or more per year on tuition and living expenses — the narrowing of post-graduation pathways raises fundamental questions about the return on that investment.

Immigration attorneys are advising current students and recent graduates to consult with legal counsel promptly about their individual situations, as the timeline for implementation remains unclear.

*Sources: The Indian Eye, immigration policy analysis*""",
    "sources": [
        {"url": "https://theindianeye.com/tighter-student-visa-rules-may-impact-indians-in-us/", "name": "The Indian Eye"},
    ],
    "tags": ["F-1 visa", "student visa", "Day 1 CPT", "Indian students", "immigration"],
    "urgency": "developing",
    "newsworthiness": 28,
    "diaspora_impact": 19,
    "prominence": 18,
    "diaspora_angle": "Indian students are one of the largest F-1 populations in the US; Day 1 CPT is the lifeline thousands rely on after H-1B lottery failures. These changes directly threaten the education-to-employment pipeline that defines Indian immigration to America.",
    "image_search_query": "university campus American students",
    "image_must_show": "University campus or student graduation scene",
    "vertical": "diaspora",
}

# ── Article 3: Iran-Houthis Red Sea Threat ─────────────────────────────────────

article3 = {
    "headline": "Iran Asks Houthis to Prepare Red Sea Closure If US Strikes: A Second Energy Chokepoint Threatens India's Lifeline",
    "subheadline": "With the Strait of Hormuz already disrupted, Iran's reported directive to its Houthi allies to stand ready to close the Bab el-Mandeb strait could cut off both of the Middle East's main oil export routes — raising the stakes for India's energy security and thousands of Indian seafarers.",
    "category": "news",
    "article_type": "standard",
    "status": "published",
    "is_featured": True,
    "body": """Iran has asked Yemen's Houthi movement to prepare to close the Red Sea oil route if the United States strikes Iranian power infrastructure, three sources told Reuters on Thursday — a threat that could simultaneously shut both of the Middle East's critical energy export chokepoints and send shockwaves through India's economy.

## A Two-Front Energy Crisis

The report comes while the Strait of Hormuz remains disrupted following the U.S.-Iran conflict that began on February 28. The Hormuz strait had carried roughly a fifth of global energy supplies before hostilities.

Now, with Saudi Arabia diverting approximately 70 percent of its energy exports through its Red Sea port of Yanbu via pipeline, the Bab el-Mandeb strait at the southern entrance of the Red Sea has become the region's critical backup route, currently carrying about 7 percent of global energy supplies.

Closing both chokepoints simultaneously would leave the Middle East's two main oil export corridors disrupted at the same time — an unprecedented scenario that analysts say could trigger an energy crisis far exceeding the disruptions seen during the Hormuz closure.

"If fighting intensifies and spills over into Red Sea export infrastructure and shipping, it will threaten the only major alternative route for oil exports from the region," said Torbjorn Solvedt, principal Middle East analyst with risk intelligence firm Verisk Maplecroft.

## Operational Preparations Already Underway

A source close to the Houthis told Reuters the group has completed preparations by deploying missiles and drones near the Bab el-Mandeb strait in Yemen's highlands overlooking Hodeidah and the Gulf of Aden. Representatives of Iran's Islamic Revolutionary Guard Corps already present in Yemen would control the decision on timing.

The operational readiness is notable because the Houthis demonstrated during the Gaza war that they could effectively disrupt Red Sea shipping, forcing major shipping companies to divert cargoes around Africa at significantly higher cost and longer transit times.

"Anybody with a firing rifle can interrupt the shipping. You don't have to have sophisticated missiles to interrupt the shipping," one regional source told Reuters.

## India at the Crossroads

For India, the threat compounds an already precarious energy situation. India imports over 80 percent of its crude oil needs, with the Middle East supplying a dominant share. The Hormuz disruption earlier this year already forced India to seek alternative suppliers and routes at higher costs.

India has also deployed significant naval assets in the region to protect shipping lanes and ensure the safety of Indian seafarers — the country supplies one of the largest maritime workforces globally, with tens of thousands of Indian sailors routinely transiting both the Hormuz and Red Sea corridors.

The escalation comes at a particularly tense moment. The Houthis fired missiles at Saudi Arabia earlier this week after accusing the kingdom of bombing an airport under their control, breaking a four-year truce. Two regional sources close to Riyadh said the kingdom was taking the combined Iran-Houthi threat "very seriously."

## Fragile Truce Collapse

The broader context is the collapse of a fragile June truce between Tehran and Washington, which has revived fears of full-scale war. The United States has threatened to strike Iranian power plants and bridges unless Tehran resumes negotiations, while Iran has signaled it could use its Houthi allies as leverage.

For the Indian diaspora and Indian businesses with Middle East exposure, the situation demands close attention. Disruption to both maritime corridors would affect not just energy prices but also the massive trade flows between India and the Gulf states, remittance corridors, and the safety of the estimated 8.5 million Indian nationals living and working in the Middle East.

*Sources: Reuters, Verisk Maplecroft analysis*""",
    "sources": [
        {"url": "https://www.reuters.com/world/middle-east/iran-tells-houthis-close-red-sea-2026-07-16/", "name": "Reuters"},
    ],
    "tags": ["Iran", "Houthis", "Red Sea", "energy crisis", "India oil imports", "Bab el-Mandeb"],
    "urgency": "breaking",
    "newsworthiness": 30,
    "diaspora_impact": 16,
    "prominence": 22,
    "diaspora_angle": "India imports 80%+ of crude oil from Middle East; 8.5 million Indians live in the Gulf; thousands of Indian seafarers transit both chokepoints daily. A dual closure would spike energy costs and threaten livelihoods across the diaspora.",
    "image_search_query": "Red Sea shipping oil tanker",
    "image_must_show": "Oil tanker or shipping vessel in the Red Sea region",
    "vertical": "politics",
}

# ── Source images ─────────────────────────────────────────────────────────────

print("\n=== Sourcing images ===\n")

# Article 1: H-1B — try Wikipedia for "United States Capitol" or similar
img1 = fetch_wikimedia_commons_images("H-1B visa United States Department of Labor", limit=5)
if img1:
    article1["image_url"] = img1[0]["url"]
    article1["image_caption"] = "The U.S. Department of Labor has escalated its investigation into H-1B visa fraud"
    article1["image_attribution"] = "Wikimedia Commons"
    print(f"  Art1 image: {img1[0]['title']}")
else:
    # Fallback to Wikipedia person image for DOL building
    img1_wiki = fetch_wikipedia_person_image("United States Department of Labor")
    if img1_wiki:
        article1["image_url"] = img1_wiki
        article1["image_caption"] = "The U.S. Department of Labor headquarters in Washington, D.C."
        article1["image_attribution"] = "Wikimedia Commons"
    else:
        print("  ⚠ No image for Article 1")

# Article 2: F-1 Students — try commons
img2 = fetch_wikimedia_commons_images("American university campus students", limit=5)
if img2:
    article2["image_url"] = img2[0]["url"]
    article2["image_caption"] = "Proposed F-1 visa rule changes could impact thousands of Indian students at American universities"
    article2["image_attribution"] = "Wikimedia Commons"
    print(f"  Art2 image: {img2[0]['title']}")
else:
    print("  ⚠ No image for Article 2")

# Article 3: Red Sea — try commons
img3 = fetch_wikimedia_commons_images("Bab el-Mandeb strait Red Sea shipping", limit=5)
if img3:
    article3["image_url"] = img3[0]["url"]
    article3["image_caption"] = "The Bab el-Mandeb strait, the gateway to the Red Sea that Iran's Houthi allies have been asked to prepare to close"
    article3["image_attribution"] = "Wikimedia Commons"
    print(f"  Art3 image: {img3[0]['title']}")
else:
    # Try broader search
    img3b = fetch_wikimedia_commons_images("Red Sea oil tanker shipping lane", limit=5)
    if img3b:
        article3["image_url"] = img3b[0]["url"]
        article3["image_caption"] = "Shipping in the Red Sea region faces potential disruption if Houthis close the Bab el-Mandeb strait"
        article3["image_attribution"] = "Wikimedia Commons"
        print(f"  Art3 image (fallback): {img3b[0]['title']}")
    else:
        # Try even broader
        img3c = fetch_wikimedia_commons_images("oil tanker ocean", limit=5)
        if img3c:
            article3["image_url"] = img3c[0]["url"]
            article3["image_caption"] = "Global oil shipping faces unprecedented disruption as both Middle Eastern chokepoints come under threat"
            article3["image_attribution"] = "Wikimedia Commons"
            print(f"  Art3 image (broad): {img3c[0]['title']}")
        else:
            print("  ⚠ No image for Article 3")

# ── Generate slugs and insert ─────────────────────────────────────────────────

print("\n=== Inserting articles ===\n")

now = datetime.now(timezone.utc).isoformat()

for i, article in enumerate([article1, article2, article3], 1):
    article["slug"] = make_slug(article["headline"])
    article["published_at"] = now
    article["display_score"] = (article.get("newsworthiness", 0) + 
                                 article.get("diaspora_impact", 0) + 
                                 article.get("prominence", 0))
    
    # Count words
    body_text = article.get("body", "")
    article["word_count"] = len(body_text.split())
    
    result = sb_insert(article)
    if result:
        print(f"  ✓ Article {i}: {article['headline'][:70]}...")
        print(f"    ID: {result.get('id', '?')[:12]}  Slug: {article['slug'][:50]}")
    else:
        print(f"  ✗ Article {i} FAILED: {article['headline'][:60]}")

print("\n=== Done ===")
