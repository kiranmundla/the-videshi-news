#!/usr/bin/env python3
"""
Videshi Lifestyle-Health + Markets-Finance Writer
Run: 2026-06-08
Articles:
1. AI-designed universal coronavirus vaccine (lifestyle-health)
2. Turmeric/curcumin supplement myths debunked (lifestyle-health)
3. Iran-Israel escalation crashes Asian markets, India slammed (markets-finance)
"""

import json, os, sys, time, uuid, subprocess, urllib.parse, re
import requests
from datetime import datetime, timezone

# ── Load env ──
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or '=' not in line:
                    continue
                line = line.replace('export ', '', 1)
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# ── Image sourcing helpers ──
def fetch_wikipedia_person_image(person_name):
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
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons(query, limit=5):
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
                mime = ii.get("mime", "")
                if url and "image" in mime:
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": ii.get("thumbwidth", ii.get("width", 0)),
                        "height": ii.get("thumbheight", ii.get("height", 0))
                    })
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

def fetch_pexels(query, per_page=5):
    if not PEXELS_API_KEY:
        return []
    try:
        # Use curl because Python urllib gets 403
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_API_KEY}',
             f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page={per_page}'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = []
        for p in data.get('photos', []):
            src = p.get('src', {})
            url = src.get('large2x') or src.get('large') or src.get('original')
            if url:
                photos.append({
                    "url": url,
                    "alt": p.get('alt', ''),
                    "photographer": p.get('photographer', '')
                })
        return photos
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return []

def validate_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            print(f"  ✓ Image valid: {url[:60]}... ({cl} bytes)")
            return True
        else:
            print(f"  ✗ Image invalid: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image check failed: {e}")
    return False

def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Published: {data[0].get('headline', '')[:60]}... (id: {data[0].get('id', '')[:8]})")
            return True
        print(f"  ✓ Published (raw response)")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:200]}")
        return False


# ═══════════════════════════════════════════════════════════════
# ARTICLE 1: AI-Designed Universal Coronavirus Vaccine
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("ARTICLE 1: AI-Designed Universal Coronavirus Vaccine")
print("="*60)

# Image sourcing - search Commons for coronavirus vaccine
print("\nSourcing image...")
commons_results = fetch_wikimedia_commons("coronavirus vaccine needle-free injection", limit=5)
art1_image_url = None
art1_image_caption = None
art1_image_attribution = None

# Also try Wikipedia for Jonathan Heeney (the lead researcher)
wiki_img = fetch_wikipedia_person_image("Jonathan Heeney")

# Try commons for DNA vaccine or microfluidic jet
commons2 = fetch_wikimedia_commons("DNA vaccine syringe", limit=3)
commons3 = fetch_wikimedia_commons("coronavirus SARS-CoV-2 3D", limit=3)

# Try Pexels for generic vaccine/laboratory imagery
pexels_results = fetch_pexels("vaccine laboratory research science", per_page=5)

# Pick best image
candidates = []
for c in commons_results + commons2 + commons3:
    candidates.append(("Wikimedia Commons", c["url"], c.get("title", "Coronavirus vaccine research")))
for p in pexels_results:
    candidates.append(("Pexels", p["url"], p.get("alt", "Vaccine research laboratory")))

for source, url, alt in candidates:
    if validate_image(url):
        art1_image_url = url
        art1_image_attribution = source
        if 'coronavirus' in alt.lower() or 'vaccine' in alt.lower() or 'sars' in alt.lower():
            art1_image_caption = "3D rendering of SARS-CoV-2 coronavirus particles"
        else:
            art1_image_caption = "Scientific research in a vaccine development laboratory"
        break

if not art1_image_url:
    print("  ⚠ No valid image found, using Pexels fallback")
    fallback = fetch_pexels("medical research laboratory", 3)
    for p in fallback:
        if validate_image(p["url"]):
            art1_image_url = p["url"]
            art1_image_caption = "Medical research in a laboratory setting"
            art1_image_attribution = "Pexels"
            break

art1_body = """The first vaccine designed entirely by artificial intelligence has passed its first human trial with a clean safety record, marking what researchers are calling a fundamental shift in how the world prepares for pandemics.

The Phase I trial, conducted at NHS clinical research facilities in Southampton and Cambridge, tested a universal Sarbecovirus vaccine on 39 healthy volunteers aged 18 to 50. The vaccine, called pEVAC-PS, produced no serious or unexpected adverse events at any of the four dose levels tested. Results were published this month in the *Journal of Infection*.

What makes this vaccine different from anything that came before is its origin. Instead of using antigens from a known virus strain — the standard approach that has left seasonal flu shots and COVID boosters perpetually one step behind — Cambridge researchers used machine learning to design what they call a "super-antigen." The AI was trained on every available genetic sequence for Sarbecoviruses logged by surveillance programs worldwide, then designed an antigen containing features common to the entire virus family, including strains that have not yet emerged.

"We've converted vaccine development from being reactive to being future-proof," said Professor Jonathan Heeney from Cambridge's Lab of Viral Zoonotics, the scientific lead. "It means we can escape the constant cycle of chasing virus variants circulating in humans and updating the vaccines to try to catch up, like a dog chasing its tail."

## The Needle-Free Factor

The vaccine was delivered through a microfluidic jet — a needle-free system that uses a high-pressure stream of liquid to push vaccine material directly into skin cells. No syringes, no needles, no cold chain.

That last point matters enormously. Because pEVAC-PS is DNA-based, it can be manufactured and stabilised in powder form. It does not require refrigeration for transport or storage. For a country like India, where the logistics of vaccinating 1.4 billion people during recurring outbreaks has strained public health infrastructure to its limits, this could be transformative.

During the COVID-19 pandemic, India's vaccination campaign — the largest in history — was repeatedly slowed by cold-chain failures in rural and semi-urban areas. Vaccines spoiled in transit. Clinics ran out of supply while neighbouring districts had surplus. A shelf-stable, needle-free alternative would bypass most of these bottlenecks entirely.

## What It Means for the Next Pandemic

The trial volunteers showed immune responses not only to SARS-CoV-2 and the original SARS virus, but also to related bat coronaviruses that have the potential to jump to humans. This is precisely the category of threat that epidemiologists warn about most — the virus circulating silently in animal populations that could trigger the next pandemic without warning.

"This new class of universal vaccines is future-proofed," said Professor Saul Faust from the University of Southampton, the trial's chief investigator. "If we can develop and clinically advance this new class of vaccines before a virus outbreak begins, millions of lives could be saved, lockdowns avoided and the economy preserved."

The technology is not limited to coronaviruses. The same AI platform can be pointed at other virus families — Ebola, influenza, or entirely new threats. DIOSynVax, the Cambridge spin-out commercialising the research, is already planning a Phase II trial with over 200 participants to assess the vaccine's ability to generate strong, broadly protective immune responses in a wider and more diverse population.

## The Diaspora Angle

For NRIs watching from the United States, the United Kingdom, and Canada, the implications are personal. Many have elderly parents in India who struggled to access vaccines during COVID waves. A single universal vaccine that protects against current and future coronavirus variants — one that does not need refrigeration and does not need a needle — could mean never going through that again.

India's Serum Institute, the world's largest vaccine manufacturer by volume, has previously partnered with Western universities on vaccine production. A partnership on this platform, if it materialises, could position India as the primary global distributor of the next generation of pandemic-proof vaccines.

The trial ran between December 2021 and September 2023. Its results, now peer-reviewed and published, represent the first proof that an entirely AI-designed vaccine can be safely administered to humans. Phase II begins later this year.

*Sources: University of Cambridge, Journal of Infection, Medical Xpress, Gizmodo, Interesting Engineering*"""

art1_slug = "ai-designed-universal-coronavirus-vaccine-first-human-trial-needle-free-india-diaspora-20260608"

article1 = {
    "headline": "The First Vaccine Designed Entirely by AI Just Passed Its Human Trial. It Needs No Needle and No Refrigerator.",
    "subheadline": "Cambridge researchers used machine learning to build a 'super-antigen' that targets every known coronavirus — and the ones that haven't emerged yet. For India, the implications go beyond science.",
    "body": art1_body,
    "slug": art1_slug,
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": art1_image_url,
    "image_caption": art1_image_caption,
    "image_attribution": art1_image_attribution,
    "sources": json.dumps([
        {"name": "University of Cambridge / Journal of Infection", "url": "https://medicalxpress.com/news/2026-06-ai-universal-vaccine-human-trial.html"},
        {"name": "Gizmodo", "url": "https://gizmodo.com/researchers-are-using-ai-to-create-vaccines-and-its-working-2000616284"},
        {"name": "Interesting Engineering", "url": "https://interestingengineering.com/health/computer-designed-universal-vaccine-early-human-trial-success"},
        {"name": "IFL Science", "url": "https://www.iflscience.com/a-universal-vaccine-for-coronaviruses-fully-designed-by-ai-in-a-world-first-just-completed-phase-1-humans-trials-78189"}
    ])
}

if art1_image_url:
    print(f"\nInserting Article 1...")
    insert_article(article1)
else:
    print("  ✗ Skipping Article 1 — no valid image")


# ═══════════════════════════════════════════════════════════════
# ARTICLE 2: Turmeric/Curcumin Myths Debunked
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("ARTICLE 2: Turmeric/Curcumin Supplement Myths Debunked")
print("="*60)

print("\nSourcing image...")
# Search Wikimedia Commons for turmeric
commons_turmeric = fetch_wikimedia_commons("turmeric powder curcumin spice", limit=5)
pexels_turmeric = fetch_pexels("turmeric powder golden spice", per_page=5)

art2_image_url = None
art2_image_caption = None
art2_image_attribution = None

candidates2 = []
for c in commons_turmeric:
    candidates2.append(("Wikimedia Commons", c["url"], c.get("title", "")))
for p in pexels_turmeric:
    candidates2.append(("Pexels", p["url"], p.get("alt", "")))

for source, url, alt in candidates2:
    if validate_image(url):
        art2_image_url = url
        art2_image_attribution = source
        art2_image_caption = "Turmeric root and powder, a staple of South Asian cooking and traditional medicine"
        break

art2_body = """Every Indian kitchen has it. Your grandmother swore by it. When you fell sick as a child, haldi doodh was the first prescription — not from a doctor, but from the person who knew better. Turmeric has been woven into South Asian life for thousands of years, and in the last two decades, the Western wellness industry caught on. Curcumin supplements became a multi-billion-dollar market. Golden milk went from your nani's remedy to a $7 latte at Whole Foods.

But a major investigation published in *New Scientist* this month lays out an uncomfortable body of evidence: the scientific case for curcumin as a medical treatment is built on shakier ground than most people realise, and the supplements themselves may be causing real harm.

## The Researcher Who Started It All

Much of curcumin's modern medical reputation traces back to one man: Bharat Aggarwal, a biochemist at the University of Texas MD Anderson Cancer Center. Starting in the early 2000s, Aggarwal published over 100 papers showing that curcumin reduces inflammation and kills "almost all types" of tumour cells. His work sparked a global research frenzy. US health agencies have since spent more than $275 million on curcumin research.

The problem: in 2012, the Office of Research Integrity at the US Department of Health and Human Services flagged allegations of potentially fraudulent results in at least 65 of Aggarwal's papers. He left MD Anderson after an internal investigation. Thirty of his papers have now been retracted from scientific journals. His remaining papers, numbering in the hundreds, are still regularly cited in new research.

## The Chemistry Does Not Work

Even without the fraud allegations, curcumin has a fundamental problem: it barely enters your bloodstream. A 2017 review in the *Journal of Medicinal Chemistry* concluded that curcumin is "an unstable, reactive, nonbioavailable compound and, therefore, a highly improbable lead" for any therapeutic use. The researchers called it "a missile that continually blows up on the launch pad."

A Dutch study published last year confirmed this in humans. Even volunteers taking high doses of "enhanced" curcumin formulations — the kind that add piperine from black pepper or use nanoparticle delivery systems — had blood concentrations more than 100 times lower than those that show activity against cancer cells in a petri dish.

This likely explains why curcumin has failed to show convincing benefits in rigorous clinical trials for cancer, arthritis, or any other condition it has been tested against.

## The Supplement Risk Nobody Talks About

Here is where it gets personal for the diaspora.

According to the US National Institute of Diabetes and Digestive and Kidney Diseases, turmeric has become "the most common cause of clinically apparent, herbal-related liver injury in the United States." Most cases are attributed to highly bioavailable curcumin formulations — precisely the enhanced supplements marketed as superior to plain turmeric.

Symptoms include yellowing of the skin, dark urine, and nausea. Most cases resolve when the supplement is stopped. A small number of people have died of liver failure.

The distinction matters: turmeric in your dal or sabzi is safe. The spice contains only about five per cent curcumin, mixed with fibre and other compounds, and is consumed in small quantities alongside a full meal. Concentrated curcumin supplements are an entirely different product, digested differently, and carrying different risks.

## The Contamination Problem

There is another risk that hits closer to home. Between 2011 and 2016, more than a dozen brands of ground turmeric spice in the United States were voluntarily recalled after testing revealed they contained lead chromate — added to enhance the spice's yellow colour. Children who regularly ate food made with these products were found to have dangerously high lead levels in their blood.

In Norway and Sweden, a turmeric supplement that caused liver problems and some deaths was found to be adulterated with nimesulide, a pain medication banned in several countries.

## What This Means for Desi Families

None of this means you should stop cooking with turmeric. The spice is safe in food, adds genuine flavour, and remains a cornerstone of cuisines that have sustained generations. Haldi doodh on a cold night is still comforting, and comfort has its own value.

But the curcumin supplement industry — worth an estimated $400 million in the US alone — has built its empire on research that is partially retracted, on a compound that barely reaches your bloodstream, and on formulations that are now the leading cause of herbal liver injury in America.

If your parents or grandparents in India or the US are taking curcumin supplements on the advice of a WhatsApp forward or an Instagram wellness influencer, this is worth a conversation. The turmeric in the masala dabba is fine. The capsules in the medicine cabinet may not be.

*Sources: New Scientist, Journal of Medicinal Chemistry, US National Institute of Diabetes and Digestive and Kidney Diseases, Retraction Watch*"""

art2_slug = "turmeric-curcumin-supplements-debunked-liver-injury-fraud-south-asian-diaspora-20260608"

article2 = {
    "headline": "The Curcumin Supplement Industry Was Built on Retracted Research. It Is Now the Leading Cause of Herbal Liver Injury in America.",
    "subheadline": "Your grandmother's haldi doodh was never the problem. But the $400 million curcumin capsule market may be — and the science behind it is falling apart.",
    "body": art2_body,
    "slug": art2_slug,
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": art2_image_url,
    "image_caption": art2_image_caption,
    "image_attribution": art2_image_attribution,
    "sources": json.dumps([
        {"name": "New Scientist", "url": "https://www.newscientist.com/article/2528418-do-turmeric-and-curcumin-have-any-actual-health-benefits/"},
        {"name": "Journal of Medicinal Chemistry (2017)", "url": "https://pubs.acs.org/doi/10.1021/acs.jmedchem.6b00975"},
        {"name": "Retraction Watch", "url": "https://retractionwatch.com"},
        {"name": "US NIDDK LiverTox", "url": "https://www.ncbi.nlm.nih.gov/books/NBK548561/"}
    ])
}

if art2_image_url:
    print(f"\nInserting Article 2...")
    insert_article(article2)
else:
    print("  ✗ Skipping Article 2 — no valid image")


# ═══════════════════════════════════════════════════════════════
# ARTICLE 3: Iran-Israel Escalation Crashes Markets
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("ARTICLE 3: Iran-Israel Escalation Crashes Asian Markets")
print("="*60)

print("\nSourcing image...")
# Wikimedia for Bombay Stock Exchange or trading floor
commons_market = fetch_wikimedia_commons("Bombay Stock Exchange building", limit=5)
commons_market2 = fetch_wikimedia_commons("stock market trading India", limit=3)
pexels_market = fetch_pexels("stock market red decline trading screen", per_page=5)

art3_image_url = None
art3_image_caption = None
art3_image_attribution = None

candidates3 = []
for c in commons_market + commons_market2:
    candidates3.append(("Wikimedia Commons", c["url"], c.get("title", "")))
for p in pexels_market:
    candidates3.append(("Pexels", p["url"], p.get("alt", "")))

for source, url, alt in candidates3:
    if validate_image(url):
        art3_image_url = url
        art3_image_attribution = source
        if 'bombay' in alt.lower() or 'bse' in alt.lower() or 'mumbai' in alt.lower():
            art3_image_caption = "The Bombay Stock Exchange building in Mumbai"
        else:
            art3_image_caption = "Stock market displays showing declining indices during Monday's broad selloff"
        break

art3_body = """Indian markets opened sharply lower on Monday as a cascade of bad news — Iranian missiles, surging oil, and a hawkish Federal Reserve — triggered the worst pan-Asian selloff in months. For NRIs with money on both sides of the Pacific, every major holding took a hit simultaneously.

The benchmark Nifty 50 fell 1.22 per cent to 23,080.70 in early trade. The BSE Sensex dropped 1.11 per cent to 73,421.61. All 16 major sectors logged losses, with IT stocks — the bread and butter of Indian American portfolios — down 1.5 per cent and financials falling 1.3 per cent. Small-caps and mid-caps, where many retail NRI investors are concentrated, declined 1.2 to 1.3 per cent.

## What Triggered the Crash

Three forces converged overnight to create a perfect storm.

**Iran fired missiles at Israel.** On Sunday, Iran launched at least four waves of missiles at Israeli targets in retaliation for Israeli airstrikes on Beirut targeting Hezbollah. Explosions were reported in Tehran, Tabriz, and Isfahan early Monday, suggesting Israeli counter-strikes. The attack marks the first time Iran has targeted Israel since the ceasefire went into effect in early April, and it threatens to keep the Strait of Hormuz — the transit route for one-fifth of the world's oil — effectively closed.

**Oil surged past $96.** Brent crude futures jumped 3.5 per cent to $96.50 a barrel, erasing Friday's gains that had come on hopes of de-escalation. US crude hit $93.41. For India, which imports over 85 per cent of its crude oil, every dollar increase in Brent adds roughly ₹10,700 crore to the annual import bill. At $96, the fiscal math that assumed $85 oil is already broken.

**The Fed rate hike probability soared.** A stronger-than-expected May US jobs report released Friday pushed the probability of a Federal Reserve rate increase by December 2026 to 72.3 per cent, up from 45.2 per cent just a week earlier. Higher US rates reduce the appeal of emerging markets like India, accelerate foreign portfolio outflows, and pressure the already-weakened rupee.

## The Asian Contagion

India was not alone. The broader MSCI Asia ex-Japan index tumbled 2.7 per cent. South Korea's KOSPI fell 4.8 per cent — its worst session in months — led by a collapse in AI-linked chip stocks after their extended rally. Japan's Nikkei lost 3.8 per cent. Hong Kong, Taiwan, and Singapore all opened deep in the red.

The selloff reflects a broader repricing of risk that had been building for weeks. Markets had been pricing in a US-Iran peace deal, a reopening of Hormuz, and a gradual return to $80 oil. Sunday's missile exchange shattered all three assumptions simultaneously.

## What NRIs Should Watch This Week

**The rupee.** The Indian rupee was already Asia's worst-performing currency this year before Monday's selloff. A sustained oil spike above $95 combined with rising US rates could push it past the psychological ₹88 mark against the dollar, eroding the value of NRI remittances and making Indian property purchases more expensive in dollar terms.

**IT earnings guidance.** With the Nasdaq falling sharply on Friday and Indian IT stocks following on Monday, any downward earnings revisions from Infosys, TCS, or Wipro during the current quarter could compound the damage. NRIs holding RSUs in Indian IT companies face a double hit — lower stock prices and a weaker rupee.

**FII flows.** Foreign institutional investors have already pulled more out of India in 2026 than in all of last year. If this week's volatility triggers another wave of outflows, the RBI may be forced to intervene more aggressively in currency markets, drawing down reserves that are already under pressure.

**Oil and gas stocks.** While the broader market fell, oil exploration and marketing companies could see divergent moves. ONGC and Oil India may benefit from higher crude, while IOC, BPCL, and HPCL face margin compression on subsidised fuel.

**Gold and bonds.** Gold futures fell ₹3,958 to ₹1,55,589 on Monday — counter-intuitive during a geopolitical crisis, but consistent with expectations of higher US rates strengthening the dollar. NRIs holding gold ETFs or sovereign gold bonds should watch whether the safe-haven bid returns if the conflict escalates further.

The immediate question is whether Iran and Israel will escalate further or return to the negotiating table. US President Trump told the Financial Times that a deal "remains well within reach" and reportedly urged Israeli Prime Minister Netanyahu to stand down. "You've shot your missiles, that's enough. Get back to the table and make a deal," he said about Iran.

Markets will take their cue from the next 48 hours. For NRIs, the playbook is familiar: do not panic-sell into a geopolitical dip, but do not assume the worst is over either. The Strait of Hormuz is still closed. Oil is still near $100. And the Fed just got another reason not to cut rates.

*Sources: Reuters, MarketWatch, Barron's, The Hindu BusinessLine, Wall Street Journal*"""

art3_slug = "iran-israel-missiles-oil-spike-asia-selloff-india-sensex-nifty-crash-nri-guide-20260608"

article3 = {
    "headline": "Iran Fires Missiles at Israel. Oil Hits $96. Indian Markets Just Had Their Worst Monday in Months.",
    "subheadline": "A perfect storm of Middle East escalation, surging crude, and rising Fed rate expectations hammered every Asian market on Monday. Here is what NRIs need to watch this week.",
    "body": art3_body,
    "slug": art3_slug,
    "category": "markets-finance",
    "vertical": "markets-finance",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": art3_image_url,
    "image_caption": art3_image_caption,
    "image_attribution": art3_image_attribution,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/indian-shares-set-fall-oil-spike-asia-selloff-hurt-sentiment-2026-06-08/"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/livecoverage/stock-market-today-dow-futures-rise-after-worst-day-in-a-year-for-nasdaq"},
        {"name": "Barron's", "url": "https://www.barrons.com/livecoverage/stock-market-today-060826"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/stock-market-today-live-june-8-sensex-nifty-50/article69666000.ece"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/finance/commodities-futures/oil-prices-rise-amid-escalating-supply-disruption-concerns-91f4e01d"}
    ])
}

if art3_image_url:
    print(f"\nInserting Article 3...")
    insert_article(article3)
else:
    print("  ✗ Skipping Article 3 — no valid image")


print("\n" + "="*60)
print("WRITER RUN COMPLETE")
print("="*60)
