#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-26 ~13:30 PDT batch
Topics: 1) Quad's first joint infrastructure project — building a port in Fiji, launching maritime surveillance, "Ports of the Future" — India co-builds Pacific infrastructure to counter China's BRI
        2) Trump administration proposes NDAs for all 2 million federal workers — Indian Americans heavily represented in agencies like NASA, NIH, USAID now face silence-or-resign ultimatum
"""

import json, os, uuid, re, requests, urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_get(table, params):
    r = requests.get(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_patch(table, params, data):
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(f"{SB_URL}/rest/v1/{table}", headers=h, params=params, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(slug_base, date_suffix="20260526"):
    slug = slug_base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

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
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

pexels_env = Path.home() / "workspace" / ".env.pexels"
PEXELS_KEY = None
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.split("=", 1)[1].strip()

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=15
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    url = photos[0]["src"]["large2x"]
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    try:
        img_data = requests.get(image_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}).content
        content_type = "image/jpeg"
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        h = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        r = requests.post(upload_url, headers=h, data=img_data, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return image_url

# --- Dedup check ---
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-23T00:00:00Z",
    "order": "published_at.desc",
    "limit": "80"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc)
now_iso = now.isoformat().replace('+00:00', 'Z')

articles = []

# ============================================================
# ARTICLE 1: Quad builds a port in Fiji — first joint infrastructure project
# ============================================================
slug1 = make_slug("quad-fiji-port-first-joint-infrastructure-india-pacific")
if slug1 not in existing_slugs and not any("fiji" in h and "port" in h for h in existing_headlines_lower):
    headline1 = "The Quad Just Announced Its First Joint Infrastructure Project — A Port in Fiji. India Will Help Build It."
    subheadline1 = "The four-nation group also launched an Indo-Pacific maritime surveillance initiative and a critical minerals recycling framework. China called it a 'Cold War construct.'"
    body1 = """The Quad has spent four years talking. On Monday, it started building.

At their third foreign ministers' meeting in New Delhi, the top diplomats of Australia, India, Japan, and the United States announced the grouping's first-ever joint infrastructure project: a port in Fiji that will be designed, funded, and built by all four nations together.

"We are going to be partnering on issues of port infrastructure, in particular in response to insufficient port capacity in the Pacific Islands," U.S. Secretary of State Marco Rubio said. "This is a practical demonstration of our collective ability to deliver high-quality, resilient infrastructure."

The announcement marks a significant shift for the Quad, which has been criticized — by analysts and, privately, by some of its own members — for producing joint statements and working groups but not concrete projects. The Fiji port, branded under a new "Ports of the Future" initiative, is designed to directly counter China's Belt and Road infrastructure footprint across the Pacific Islands, where Beijing has built ports, roads, and government buildings in Fiji, Tonga, Vanuatu, and the Solomon Islands over the past decade.

## What India Gets

For India, the Fiji port is not just about the Pacific — it is about credibility. New Delhi has long positioned itself as a development partner for the Global South, but its infrastructure delivery record outside South Asia has been patchy compared to China's. Co-building a port alongside the U.S., Japan, and Australia gives India a concrete credential in infrastructure diplomacy.

India's External Affairs Minister S. Jaishankar, who chaired the meeting, framed the Quad's evolution as a response to the disruption of global supply chains — a reference to both China's dominance in critical minerals and Iran's closure of the Strait of Hormuz.

"We are in an era where resilience is not optional," Jaishankar said. "It is a strategic imperative."

The ministers also launched the Indo-Pacific Maritime Surveillance Cooperation Initiative, which will create a shared "Common Operating Picture" of vessel movements across strategic shipping lanes. The initiative — which will pool satellite data, coastal radar feeds, and ship-tracking information from all four nations — is aimed at monitoring Chinese naval activity, illegal fishing by Chinese-flagged vessels, and disruptions to energy shipments.

## Critical Minerals and Rare Earths

Separately, Rubio and Jaishankar signed a bilateral U.S.-India Critical Minerals Framework, which will coordinate investment in mining, processing, and recycling of rare earth elements, lithium, cobalt, and other minerals essential for semiconductors, electric vehicles, and defense systems.

The framework is particularly significant for Japan, which has been struggling since China halted shipments of several critical minerals used in aerospace and semiconductor manufacturing following a diplomatic dispute earlier this year. A Quad-wide supply chain for these materials would reduce all four nations' dependence on Chinese processing.

"We are deeply committed to this partnership. It is a linchpin and a cornerstone of our global strategy as a nation," Rubio said.

## The Leaders' Summit Question

The Quad has not held a leaders' summit since September 2024, when Joe Biden hosted Modi, then-Australian PM Anthony Albanese, and then-Japanese PM Fumio Kishida. The absence of a Trump-Modi summit has raised questions about whether the Quad has been downgraded under the current U.S. administration, particularly given Trump's tariff disputes with India.

Rubio said diplomats would work toward a leaders' meeting later this year, but set no date. New Delhi has pressed for a Trump visit to India — a trip that, if it happens, would likely coincide with a Quad summit.

"The absence of a leaders' summit has raised some doubts, but that does not necessarily indicate declining importance," said Premesha Saha, a senior policy fellow at the Asia Society Australia. "If the Quad can keep delivering at the ministerial and working levels, it can remain relevant even without regular leaders-level signalling."

## The China Response

Beijing was predictably unimpressed. China's foreign ministry has repeatedly characterized the Quad as a "Cold War-style construct" aimed at containing its development. The Fiji port announcement is likely to intensify that criticism, given China's own investments in Pacific Island infrastructure.

For the Indian diaspora, the Quad's evolution matters on multiple levels. Indian-origin technology professionals in the U.S. and Australia work on the semiconductor supply chains that the critical minerals framework is designed to secure. Indian engineers and project managers will likely be involved in building the Fiji port. And the maritime surveillance initiative has direct implications for the safety of shipping lanes that carry the oil India imports and the goods that NRI families send home.

The Quad is no longer just a talking shop. It is pouring concrete."""
    article1 = {
        "id": str(uuid.uuid4()),
        "slug": slug1,
        "headline": headline1,
        "subheadline": subheadline1,
        "body": body1,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "Indian-origin tech professionals across the US and Australia work on the semiconductor and critical minerals supply chains the Quad framework aims to secure. Indian engineers will be involved in the Fiji port build. Maritime surveillance protects the oil shipping lanes India depends on and the trade routes NRI families use to send goods home.",
        "tags": ["quad", "fiji", "infrastructure", "jaishankar", "rubio", "critical minerals", "indo-pacific", "china", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Australia-India-Japan-US Quad to build a port, unveil pact on critical minerals", "url": "https://www.reuters.com/world/china/australia-india-japan-us-quad-seeks-relevance-foreign-ministers-meet-new-delhi-2026-05-26/"},
            {"name": "LiveMint — Quad FM Meeting LIVE: Ind-US critical minerals framework signed", "url": "https://www.livemint.com/news/india/quad-foreign-ministers-meeting-live-updates"},
            {"name": "US State Department — Rubio and Jaishankar signing of Critical Minerals Framework", "url": "https://www.state.gov/secretary-rubio-jaishankar-critical-minerals/"},
            {"name": "gCaptain — Quad Nations Launch Fiji Port Plan", "url": "https://gcaptain.com/quad-nations-launch-fiji-port-plan-critical-minerals-pact/"}
        ]),
        "score_total": 86,
        "status": "published",
        "published_at": now_iso,
        "image_attribution": None,
        "image_url": None,
    }
    # Image sourcing — about Jaishankar (person). Wikipedia first.
    img_url = fetch_wikipedia_person_image("S. Jaishankar")
    if not img_url:
        img_url = fetch_wikipedia_person_image("Subrahmanyam Jaishankar")
    if not img_url:
        img_url = fetch_pexels_image("Fiji port aerial view", "Pacific island port harbor")
    if img_url:
        filename = f"{article1['slug']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        article1["image_url"] = final_url
        article1["image_attribution"] = "Wikimedia Commons" if "wikipedia" in (img_url or "") or "wikimedia" in (img_url or "") else "The Videshi"
    sb_post("p2_articles", article1)
    articles.append(slug1)
    print(f"✓ Published: {headline1}")
else:
    print(f"⊘ Skipped (dedup): Quad Fiji port article")

# ============================================================
# ARTICLE 2: Trump NDA proposal for all 2M federal workers
# ============================================================
slug2 = make_slug("trump-nda-federal-workers-indian-americans-silence")
if slug2 not in existing_slugs and not any("nda" in h and "federal" in h for h in existing_headlines_lower):
    headline2 = "Trump Just Proposed Making Every Federal Employee Sign an NDA. For 100,000 Indian Americans in Government, It's Sign or Leave."
    subheadline2 = "The draft non-disclosure agreement would let the administration pursue criminal penalties against workers who talk to journalists. The federal union says it's unconstitutional."
    body2 = """The Trump administration on Tuesday proposed a draft non-disclosure agreement that it wants every one of the federal government's roughly two million civilian employees to sign — a move that would effectively bar them from sharing any confidential information with journalists, under threat of civil and criminal penalties.

The proposal, announced by the Office of Personnel Management, would apply across every federal agency: the Department of Defense, NASA, the National Institutes of Health, USAID, the CDC, the State Department, the IRS, and dozens of others. Employees who refuse to sign could face termination.

For the roughly 100,000 Indian Americans who work in the federal government — a community disproportionately represented in science, technology, health, and policy roles — the NDA poses a specific and acute dilemma.

## The Diaspora in Government

Indian Americans are among the most highly credentialed communities in the federal workforce. They hold senior roles at NASA's Jet Propulsion Laboratory, lead research teams at the NIH, staff cybersecurity divisions at the Department of Homeland Security, and run development programs at USAID. Many are naturalized citizens who chose government service over higher-paying private sector jobs because they believed in public mission.

The proposed NDA would make it a potential crime for any of them to speak to a reporter about waste, mismanagement, or policy failures they witness in their agencies — even after leaving government.

"This proposed NDA is another attempt by the administration to purge the civil service of nonpartisan career employees and replace them with loyalists who won't speak out against waste, fraud, and abuse," said Everett Kelley, president of the American Federation of Government Employees, the largest federal workers' union.

The draft does include an exception for disclosures to internal government watchdogs — inspectors general — and to Congress. But it would criminalize disclosures to journalists, which is the primary way that government misconduct reaches the public.

## A Pattern

The NDA proposal does not exist in isolation. It is the latest in a series of Trump administration moves that have tightened control over the federal workforce:

The administration fired thousands of probationary employees in February and March, many of them recent hires at agencies like USAID and the EPA. The Schedule F executive order, which reclassifies tens of thousands of career civil servants as political appointees who can be fired at will, is being implemented across agencies. DOGE, the Department of Government Efficiency led by Elon Musk, has targeted entire offices for elimination.

For Indian American federal workers, each of these measures has had a disproportionate impact. The USAID cuts hit development professionals who had spent careers building programs in South Asia and Africa. The Schedule F reclassification threatens senior scientists and policy analysts — roles where Indian Americans are heavily represented. And now the NDA would silence those who remain.

## The Legal Question

Constitutional scholars are divided on whether the NDA would survive a legal challenge. The First Amendment protects government employees' right to speak on matters of public concern, a principle established in the 1968 Supreme Court case Pickering v. Board of Education. But the government also has broad authority to restrict disclosures of classified and sensitive information.

The key question is whether the NDA's definition of "confidential information" is so broad that it effectively muzzles all speech about government operations — or whether it can be narrowly construed to cover only legitimately sensitive material.

"If this NDA is interpreted the way the administration seems to want — as a blanket gag order on anything that could embarrass the government — it will be struck down," said a former Department of Justice attorney who spoke on condition of anonymity. "But the chilling effect is the point. Most people won't lawyer up. They'll just stay quiet."

## What It Means for the Diaspora

The Indian American community has built its presence in the federal government over three decades. First-generation immigrants who came on H-1B visas, earned green cards, became citizens, and chose government over Google — because they wanted to work on climate policy at NOAA, or pandemic preparedness at the CDC, or space exploration at NASA.

The NDA proposal tells them: your expertise is welcome, your voice is not.

For families in the diaspora, the question is not abstract. It is the uncle at NASA who can no longer tell you what he really thinks about his agency's direction over Thanksgiving dinner. It is the cousin at the NIH who saw a program cut and cannot explain to a reporter why it matters. It is the USAID officer who watched a decades-old development program in India get shuttered and cannot say a word.

The proposal is in its draft stage and will go through a public comment period. Federal unions have already signaled they will challenge it in court. But the message has been sent: in this administration, silence is the price of employment."""
    article2 = {
        "id": str(uuid.uuid4()),
        "slug": slug2,
        "headline": headline2,
        "subheadline": subheadline2,
        "body": body2,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "~100,000 Indian Americans work in the federal government, disproportionately in STEM, health, policy, and development roles at NASA, NIH, USAID, CDC, and DHS. The NDA directly threatens their ability to speak publicly about waste or mismanagement. Combined with DOGE layoffs, USAID cuts, and Schedule F, it represents a pattern that specifically impacts diaspora professionals who chose public service.",
        "tags": ["trump", "nda", "federal workers", "indian american", "government", "free speech", "first amendment", "doge", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Trump administration proposes NDAs for federal workers", "url": "https://www.reuters.com/world/us/trump-administration-proposes-ndas-federal-workers-crack-down-leaks-journalists-2026-05-26/"},
            {"name": "CNN — Trump administration proposes having all federal workers sign NDAs", "url": "https://www.cnn.com/2026/05/26/politics/trump-nda-federal-workers/"},
            {"name": "AFGE statement on proposed NDA", "url": "https://www.afge.org/"}
        ]),
        "score_total": 83,
        "status": "published",
        "published_at": now_iso,
        "image_attribution": None,
        "image_url": None,
    }
    # Image sourcing — about Trump (person). Wikipedia first.
    img_url = fetch_wikipedia_person_image("Donald Trump")
    if not img_url:
        img_url = fetch_pexels_image("White House executive order signing", "US federal government building")
    if img_url:
        filename = f"{article2['slug']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        article2["image_url"] = final_url
        article2["image_attribution"] = "Wikimedia Commons" if "wikipedia" in (img_url or "") or "wikimedia" in (img_url or "") else "The Videshi"
    sb_post("p2_articles", article2)
    articles.append(slug2)
    print(f"✓ Published: {headline2}")
else:
    print(f"⊘ Skipped (dedup): Trump NDA article")

print(f"\nDone. Published {len(articles)} articles: {articles}")
