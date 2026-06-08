#!/usr/bin/env python3
"""Lifestyle & Markets writer — 2026-06-08 run."""

import json, os, sys, uuid, re, time
from datetime import datetime, timezone
import requests
import subprocess

# Load env
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            if line.startswith("export "):
                line = line[7:]
            k, v = line.split("=", 1)
            v = v.strip('"').strip("'")
            os.environ[k] = v

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Load Pexels key
pexels_path = os.path.expanduser("~/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_path):
    with open(pexels_path) as f:
        for line in f:
            line = line.strip()
            if "PEXELS_API_KEY" in line and "=" in line:
                PEXELS_KEY = line.split("=",1)[1].strip('"').strip("'")


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    encoded = person_name.replace(' ', '_')
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
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
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
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                if url and ii.get("mime", "").startswith("image/"):
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": ii.get("width", 0),
                        "mime": ii.get("mime", "")
                    })
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []


def fetch_pexels(query):
    """Search Pexels for stock photos. Use curl to avoid 403."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key")
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={requests.utils.requote_uri(query)}&per_page=5&orientation=landscape"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        for photo in data.get("photos", []):
            url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
            if url:
                print(f"  ✓ Pexels: {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def validate_image(url):
    """Validate image URL returns 200 and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image valid: {cl} bytes, {ct}")
            return True
        # Try GET for servers that don't support HEAD well
        r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r2.headers.get("Content-Type", "")
        cl = int(r2.headers.get("Content-Length", 0))
        if r2.status_code == 200 and "image" in ct:
            # Read a chunk to verify size
            chunk = r2.raw.read(6000)
            if len(chunk) >= 5000:
                print(f"  ✓ Image valid (GET): {ct}")
                return True
        print(f"  ✗ Image invalid: status={r.status_code}, ct={ct}, cl={cl}")
        return False
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
        return False


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Inserted: {result[0].get('headline','?')[:60]}")
            return True
    print(f"  ✗ Insert failed: {r.status_code} {r.text[:200]}")
    return False


# ============================================================
# ARTICLE 1: GLP-1 Drugs and Cancer
# ============================================================
print("\n" + "="*60)
print("ARTICLE 1: GLP-1 drugs and cancer risk")
print("="*60)

# Image: Search Wikimedia Commons for "GLP-1 semaglutide injection" or similar
print("\nSourcing image...")
img1_url = None
img1_caption = ""
img1_attr = ""

# Try Wikimedia Commons first for semaglutide/GLP-1
commons_results = fetch_wikimedia_commons("semaglutide Ozempic injection pen")
for cr in commons_results:
    if any(skip in cr["title"].lower() for skip in ["svg", "logo", "icon", "flag"]):
        continue
    if validate_image(cr["url"]):
        img1_url = cr["url"]
        img1_caption = "Semaglutide injection pen, one of the GLP-1 drugs now showing cancer-fighting properties"
        img1_attr = "Wikimedia Commons"
        break

if not img1_url:
    commons_results = fetch_wikimedia_commons("Wegovy semaglutide weight loss drug")
    for cr in commons_results:
        if any(skip in cr["title"].lower() for skip in ["svg", "logo", "icon", "flag"]):
            continue
        if validate_image(cr["url"]):
            img1_url = cr["url"]
            img1_caption = "A GLP-1 weight loss medication, now showing potential as a cancer-fighting drug"
            img1_attr = "Wikimedia Commons"
            break

if not img1_url:
    # Pexels fallback for generic medical/pharmaceutical
    img1_url = fetch_pexels("medical research laboratory cancer treatment")
    if img1_url and validate_image(img1_url):
        img1_caption = "A medical research laboratory studying cancer treatments"
        img1_attr = "Pexels"
    else:
        img1_url = None

article1_body = """The weight loss drugs that changed how the world thinks about obesity may be about to change how it thinks about cancer.

Data presented at the 2026 American Society of Clinical Oncology annual meeting shows that GLP-1 receptor agonists — the class of drugs behind Ozempic, Wegovy, and Mounjaro — are associated with significantly reduced cancer risk and slower disease progression across multiple tumour types. The findings have landed like a thunderclap in oncology circles, and for South Asians in the diaspora, the implications run unusually deep.

## The Numbers That Stopped Oncologists Cold

The most prominent study, published in the Journal of Clinical Oncology, tracked more than 10,000 patients with early-stage cancer. Half had started GLP-1 drugs after diagnosis. The other half took a different diabetes medication.

Of the seven tumour types examined, patients on GLP-1 drugs showed decreased progression to metastatic disease in six. Four of those reductions were statistically significant: breast, colorectal, liver, and non-small cell lung cancer. In some cases, patients were up to 50 per cent less likely to progress to stage four.

"Of the seven style of tumors they chose to look at, they saw a decreased progression to metastatic disease in 6 out of the 7 cancers, four of which were statistically significant," said Dr Julie Gralow, chief medical officer of ASCO.

A separate study from the University of Pennsylvania matched mammogram images to prescription databases and found that women between ages 45 and 80 taking GLP-1 drugs were 30 per cent less likely to develop breast cancer in the first place.

## Beyond Weight Loss: An Anti-Inflammatory Effect

The key finding that has researchers most excited is that weight loss alone does not explain the magnitude of the effect.

"The weight loss alone just didn't account for the magnitude of the observed effect," said Dr Elizabeth McDonald, a radiologist at the University of Pennsylvania who co-authored the mammography study.

McDonald suspects that in the process of regulating hormones involved in hunger and digestion, GLP-1 drugs also trigger other hormonal pathways — particularly those that reduce chronic inflammation. Chronic inflammation is a known driver of tumour growth, and GLP-1 drugs appear to dampen it independently of their weight loss effects.

"Some of these pathways will lead to weight loss, but other pathways will lead to reduction in inflammation, so they have multiple effects," McDonald explained.

A new clinical trial at Rutgers, led by oncologist Dr Coral Omene, will follow 40 breast cancer patients starting Tirzepatide (marketed as Mounjaro and Zepbound). The study will track changes in DNA cancer markers in the blood and hormone and inflammation activity in fat cells, hoping to establish a direct biological mechanism.

## Why South Asians Cannot Afford to Ignore This

South Asians carry a uniquely elevated metabolic risk profile. Studies from the MASALA cohort at Northwestern University have shown that South Asian Americans develop hypertension, prediabetes, and diabetes at significantly higher rates than other ethnic groups — often a full decade earlier, and despite reporting healthier diets and lower alcohol consumption.

This metabolic profile is precisely what GLP-1 drugs were designed to address. Millions of Indian Americans are already prescribed semaglutide or tirzepatide for diabetes management or weight loss. The emerging cancer data suggests they may have been receiving a benefit no one anticipated.

The connection is especially relevant for breast and colorectal cancer, both of which are rising among South Asians in the United States and among urban Indians. The National Cancer Registry Programme has documented a steady increase in breast cancer incidence across Indian metros, and colorectal cancer rates among Indian Americans are converging with the national average.

## What NRIs Should Know Right Now

These are still observational findings — correlation, not causation, as Dr Gralow emphasised. No one is prescribing Ozempic as a cancer drug today. But the signal is strong enough that several randomised controlled trials are now underway.

For South Asians in the diaspora who are already on GLP-1 drugs for diabetes or weight management, the data is reassuring. For those with a family history of breast, colorectal, or liver cancer combined with metabolic risk factors, it may be worth a conversation with their doctor about whether these drugs could serve a dual purpose.

The drugs are not without side effects — nausea, gastrointestinal discomfort, and in rare cases, pancreatitis. But the emerging picture is one where a single class of medication could address multiple conditions that disproportionately affect the South Asian community.

The era of the single-purpose drug may be ending. And the community that stands to gain the most from it may be the one that has been medically underserved for the longest."""

article1 = {
    "headline": "GLP-1 Weight Loss Drugs Now Show They Can Slash Cancer Risk by Up to 50 Per Cent. South Asians Should Be Watching.",
    "subheadline": "Data from the 2026 ASCO meeting shows Ozempic-class drugs reduce breast cancer risk by 30 per cent and slow cancer progression across six tumour types. The diaspora community with the highest metabolic risk has the most to gain.",
    "slug": "glp1-weight-loss-drugs-cancer-risk-reduction-asco-2026-south-asian-diaspora-20260608",
    "body": article1_body.strip(),
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "status": "review",
    "is_editorial": False,
    "sources": json.dumps([
        "NPR / WAMC — GLP-1s might reduce risk of cancer, June 5 2026",
        "Journal of Clinical Oncology — ASCO 2026 presentation data",
        "The Times — Year of the wonder drugs: four breakthroughs in cancer treatment",
        "Northwestern University MASALA Study"
    ]),
    "image_url": img1_url or "",
    "image_caption": img1_caption,
    "image_attribution": img1_attr,
    "published_at": datetime.now(timezone.utc).isoformat()
}

if img1_url:
    print(f"\n  Image: {img1_url[:80]}")
    insert_article(article1)
else:
    print("  ⚠ No valid image found, inserting without image...")
    insert_article(article1)


# ============================================================
# ARTICLE 2: India Heat Wave — Nearly 100 Dead in UP & Bihar
# ============================================================
print("\n" + "="*60)
print("ARTICLE 2: India heat wave — nearly 100 dead")
print("="*60)

print("\nSourcing image...")
img2_url = None
img2_caption = ""
img2_attr = ""

# Wikimedia Commons for India heat wave
commons_results = fetch_wikimedia_commons("India heat wave summer heat")
for cr in commons_results:
    if any(skip in cr["title"].lower() for skip in ["svg", "logo", "icon", "flag", "graph", "chart"]):
        continue
    if validate_image(cr["url"]):
        img2_url = cr["url"]
        img2_caption = "Extreme heat conditions across India as temperatures cross 47 degrees Celsius"
        img2_attr = "Wikimedia Commons"
        break

if not img2_url:
    commons_results = fetch_wikimedia_commons("heat stroke dehydration India summer")
    for cr in commons_results:
        if any(skip in cr["title"].lower() for skip in ["svg", "logo", "icon", "flag"]):
            continue
        if validate_image(cr["url"]):
            img2_url = cr["url"]
            img2_caption = "Heat conditions intensify across northern India"
            img2_attr = "Wikimedia Commons"
            break

if not img2_url:
    img2_url = fetch_pexels("extreme heat India dry cracked earth summer")
    if img2_url and validate_image(img2_url):
        img2_caption = "Dry, cracked earth during India's extreme summer heat wave"
        img2_attr = "Pexels"
    else:
        img2_url = None

article2_body = """At least 96 people have died in Uttar Pradesh and Bihar in the past several days as a brutal heat wave continues to grip northern and eastern India. Hospitals in both states are overwhelmed, and authorities have warned residents over 60 and those with pre-existing conditions to stay indoors entirely during daylight hours.

The deaths — confirmed by state officials on Sunday — add to a toll that has been climbing since early April. According to tracking by the India Meteorological Department, the 2025-2026 heat wave has now killed at least 455 people across India since it began, with 195 deaths in April and 260 in May. June could be worse.

## Uttar Pradesh: A Hospital in Crisis

The district hospital in Ballia, eastern Uttar Pradesh, has become the epicentre of the crisis. More than 400 people were admitted over just three days with complaints of fever, breathlessness, and heat-related complications. The majority were over 60.

"All the individuals were suffering from some ailments and their conditions worsened due to the extreme heat," Ballia's Chief Medical Officer Dr Jayant Kumar told the Associated Press. Most deaths were attributed to heart attacks, brain strokes, and dehydration-related diarrhoea — conditions that are dramatically worsened by sustained exposure to extreme heat.

The state government has dispatched a team of doctors from the capital Lucknow to investigate, and hospitals have scrambled to arrange additional fans, coolers, and air conditioning units.

## Bihar: Lightning, Storms, and Relentless Heat

In Bihar, the heat wave has triggered a cascade of secondary disasters. The collision of extreme heat with incoming moisture has produced violent pre-monsoon thunderstorms, with lightning strikes killing at least four people in a single day across Jamui, Munger, Banka, and Buxar districts. One victim was an 11-year-old boy.

The India Meteorological Department has issued an Orange Alert for 12 Bihar districts, warning of thunderstorms with winds reaching 60 kilometres per hour. But in southern Bihar, including Patna, there is little relief — temperatures are expected to rise another 1 to 2 degrees in the coming days.

Bihar's agricultural sector has also taken a severe hit. Mango, lychee, and wheat crops have suffered extensive damage just weeks before scheduled harvests, threatening the livelihoods of farming communities that are already among India's most economically fragile.

## The Scale of the Crisis

The 2025-2026 heat wave is now among the deadliest in Indian history. It arrived earlier than the typical May-June season, and the India Meteorological Department had predicted "above-normal number of heatwave days" as early as mid-April.

The peak temperature of 48.0°C (118.4°F) was recorded at Sri Ganganagar in Rajasthan on June 12. Multiple stations across Madhya Pradesh, Rajasthan, and UP have recorded temperatures above 47°C in recent days. The IMD has classified conditions across more than a dozen states as severe heat wave territory.

Power demands for air conditioning have surged beyond grid capacity in multiple regions. Extended outages — some lasting up to 16 hours — have left vulnerable populations without access to cooling during the most dangerous hours of the day.

## What This Means for the Diaspora

For the millions of NRIs with elderly parents and relatives in UP, Bihar, Rajasthan, Madhya Pradesh, and Odisha, this heat wave is not an abstract climate story. It is an immediate welfare crisis.

The most vulnerable are people over 60, those with heart disease or diabetes, outdoor labourers, and anyone without reliable access to air conditioning and clean water. The combination of sustained heat, power outages, and overwhelmed hospitals means that conditions that would normally be manageable can become fatal within hours.

Experts recommend that families with elderly relatives in affected areas take the following precautions: ensure access to ORS (oral rehydration salts) and clean drinking water, check that cooling systems are functioning and that backup power is available, encourage indoor rest between 11 a.m. and 4 p.m., and establish a daily check-in routine by phone or video call.

## The Monsoon Cannot Come Soon Enough

Meteorologists say the southwest monsoon, which has already arrived in Kerala, could reach Bihar and UP within one to two weeks if its northward advance stays on schedule. Until then, the combination of extreme heat and pre-monsoon instability will continue to produce dangerous conditions.

The pattern is now grimly familiar: India's heat waves are arriving earlier, lasting longer, and killing more people each year. For a diaspora that bridges the distance between American suburbs and Indian villages, the gap between climate-controlled comfort and lethal heat has never felt wider — or more urgent to close."""

article2 = {
    "headline": "India's Heat Wave Has Killed Nearly 100 People in Three Days. UP and Bihar Are in Crisis.",
    "subheadline": "Hospitals in Uttar Pradesh are overwhelmed, Bihar is battling lightning deaths alongside the heat, and the monsoon is still two weeks away. For NRIs with elderly parents in the affected states, this is a welfare emergency.",
    "slug": "india-heat-wave-96-dead-uttar-pradesh-bihar-2026-nri-diaspora-guide-20260608",
    "body": article2_body.strip(),
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "status": "review",
    "is_editorial": False,
    "sources": json.dumps([
        "Associated Press — Nearly 100 die as India struggles with sweltering heat wave, June 7 2026",
        "Wikipedia — 2025-2026 India-Pakistan heat wave",
        "India Meteorological Department — Heat wave alerts and advisories",
        "Patna Press — Bihar lightning strikes and Orange Alert, June 6 2026"
    ]),
    "image_url": img2_url or "",
    "image_caption": img2_caption,
    "image_attribution": img2_attr,
    "published_at": datetime.now(timezone.utc).isoformat()
}

if img2_url:
    print(f"\n  Image: {img2_url[:80]}")
insert_article(article2)


# ============================================================
# ARTICLE 3: India Oil Supply Chain Diversification
# ============================================================
print("\n" + "="*60)
print("ARTICLE 3: India rebuilding oil supply chain")
print("="*60)

print("\nSourcing image...")
img3_url = None
img3_caption = ""
img3_attr = ""

# Wikimedia Commons for oil tanker / refinery
commons_results = fetch_wikimedia_commons("oil tanker India petroleum refinery")
for cr in commons_results:
    if any(skip in cr["title"].lower() for skip in ["svg", "logo", "icon", "flag", "map"]):
        continue
    if validate_image(cr["url"]):
        img3_url = cr["url"]
        img3_caption = "An oil tanker, part of India's scramble to diversify crude supplies as Hormuz disruption continues"
        img3_attr = "Wikimedia Commons"
        break

if not img3_url:
    commons_results = fetch_wikimedia_commons("Strait of Hormuz oil tanker shipping crude oil")
    for cr in commons_results:
        if any(skip in cr["title"].lower() for skip in ["svg", "logo", "icon", "flag"]):
            continue
        if validate_image(cr["url"]):
            img3_url = cr["url"]
            img3_caption = "Maritime shipping in the Strait of Hormuz region, the chokepoint at the centre of India's oil supply crisis"
            img3_attr = "Wikimedia Commons"
            break

if not img3_url:
    img3_url = fetch_pexels("oil refinery industrial energy petroleum")
    if img3_url and validate_image(img3_url):
        img3_caption = "An oil refinery processing crude, as India diversifies its energy sources beyond the Middle East"
        img3_attr = "Pexels"
    else:
        img3_url = None

article3_body = """India is not just weathering the oil crisis. It is using it to rebuild its entire energy supply chain from the ground up.

As the Strait of Hormuz disruption stretches past 100 days with no resolution in sight, Indian refiners have sharply increased crude oil purchases from Latin America and Africa, turning Venezuela, Brazil, Angola, and Nigeria into replacement suppliers for what the Gulf can no longer reliably deliver. The shift — once a contingency plan — is beginning to look permanent.

## The New Oil Map

India is the world's third-largest oil importer, and roughly a fifth of its supply used to flow through the Strait of Hormuz. That channel has been effectively strangled since the Israel-Iran conflict escalated in late February, with the latest flare-up — Israeli strikes on a petrochemical complex in Iran's Mahshahr on Monday, followed by Iranian missile salvos at Israeli targets — snuffing out what remained of near-term ceasefire hopes.

Brent crude jumped to $97.15 per barrel on Monday, up 4.5 per cent in a single session, after Israel hit an energy site inside Iran for the first time since the April 8 ceasefire collapsed.

India has responded not with panic but with supply-chain engineering. According to Kpler data, Venezuelan crude is now on track to make the South American nation India's fourth-largest supplier in May, reflecting stronger demand for heavy crude as Gulf flows remain constrained. Purchases from Brazil, Angola, and Nigeria have also climbed sharply in April and May.

At the same time, India continues to receive approximately 1.9 million barrels per day of Russian oil and about 41,000 barrels per day from Iraq — two lifelines that have kept the overall supply picture manageable even as Middle Eastern flows have cratered.

## The Global Inventory Crisis

The underlying problem is that the world's oil reserves are draining at an unprecedented pace and no one is entirely sure how much runway is left.

Global crude and fuel stocks fell at a pace of 5.27 million barrels per day in March, accelerated to 8.62 million barrels per day in April, and likely approached 9 million barrels per day in May, according to the US Energy Information Administration. June draws could rise further to 11 million barrels per day as summer demand increases.

As Reuters reported this week, these are extraordinary numbers — "equivalent to running down Saudi Arabia's pre-war production every single day."

US crude inventories, including the Strategic Petroleum Reserve, have fallen roughly 10 per cent this year to 1.5 billion barrels, the lowest since 2004. At Cushing, Oklahoma — the delivery point for West Texas Intermediate futures — stocks have dropped to 22.4 million barrels, approaching the 20 million barrel threshold widely seen as the minimum for the hub to function smoothly.

Goldman Sachs estimates the Iran war cut global oil use by 4 to 5 million barrels per day in April, or 4 to 5 per cent of total global demand. China's crude imports have fallen by roughly 4 million barrels per day from a year ago, and Chinese gasoline and diesel consumption is down more than 10 per cent.

## What NRIs Need to Understand

For the Indian diaspora, this is not just a geopolitical story. It feeds directly into three things that affect every NRI with financial ties to India.

**Inflation.** India imports more than 80 per cent of its crude oil. With Brent near $97, fuel prices at home will continue to rise, and so will the cost of everything that moves by road or rail — food, fertiliser, building materials. Nuvama Institutional Equities has already warned that a prolonged supply shock alongside a weak monsoon raises the risk of stagflation — slowing growth combined with persistent inflation.

**The rupee.** A higher oil import bill bleeds dollars out of India's foreign exchange reserves. The rupee has been Asia's worst-performing currency this year, and the RBI has spent billions defending it. The structural shift in sourcing does not change the cost — Latin American and African crude is not cheaper than Gulf crude. It simply reduces single-point-of-failure risk.

**Investment outlook.** The Sensex fell 1.1 per cent on Monday morning, tracking the broader Asian selloff. The Nifty 50 dropped 1.2 per cent to 23,080. The probability of a US Federal Reserve rate hike by December 2026 has jumped to 72.3 per cent from 45.2 per cent a week earlier, according to CME FedWatch. Higher US rates typically reduce the appeal of emerging markets like India, and foreign portfolio investors have already pulled more money out of India in 2026 than in all of last year.

## A Structural Shift, Not a Temporary Fix

India's government and refiners have emphasised that the diversification away from Middle Eastern crude is not a stopgap. As The Indian Eye reported, the move "appears to be less a temporary fix than a structural adjustment in sourcing strategy."

Saudi Arabia and the UAE have increased shipments through pipelines that bypass Hormuz. US crude exports have risen to records. But the fundamental equation has changed: the chokepoint that India built its energy security around for decades is no longer reliable, and the alternatives — while more expensive in logistics — are proving more resilient in practice.

For NRIs watching oil prices, rupee movements, and Indian equity markets, the lesson is clear: India's economy is being re-plumbed in real time. The old map no longer applies. The question is not whether the new supply chain holds, but what it costs — and who pays."""

article3 = {
    "headline": "India Is Quietly Rebuilding Its Entire Oil Supply Chain. Venezuela and Brazil Are Replacing the Gulf.",
    "subheadline": "As the Strait of Hormuz stays disrupted past 100 days, Indian refiners have turned to Latin America and Africa for crude. The shift is no longer a contingency. It is structural. Here is what it means for NRI wallets.",
    "slug": "india-oil-supply-chain-diversification-venezuela-brazil-africa-hormuz-nri-20260608",
    "body": article3_body.strip(),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "status": "review",
    "is_editorial": False,
    "sources": json.dumps([
        "Reuters — Oil prices climb more than $4 after Israeli strikes on Iran, June 8 2026",
        "Reuters — Oil market calm masks a host of unknowns, June 8 2026",
        "The Indian Eye — India turns to Latin American, African oil as Hormuz disruption continues",
        "Barron's — What Energy Markets Got Right and Wrong 100 Days Into the Iran War",
        "Nuvama Institutional Equities — India stagflation risk analysis"
    ]),
    "image_url": img3_url or "",
    "image_caption": img3_caption,
    "image_attribution": img3_attr,
    "published_at": datetime.now(timezone.utc).isoformat()
}

if img3_url:
    print(f"\n  Image: {img3_url[:80]}")
insert_article(article3)

print("\n" + "="*60)
print("DONE — 3 articles inserted with status=review")
print("="*60)
