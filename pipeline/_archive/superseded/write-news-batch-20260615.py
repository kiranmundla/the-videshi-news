#!/usr/bin/env python3
"""
Videshi News Writer - News batch for June 15, 2026
Articles:
1. NEET Re-Exam crisis (exam integrity, CBI arrests, IAF transport)
2. India's extreme heat as economic emergency (Kanpur, productivity, GDP risk)
3. Sovereign AI: India building alternatives after Anthropic cutoff
"""

import os, json, requests, time, re, urllib.parse
from datetime import datetime, timezone

# Load env
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ── Image sourcing functions ──

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
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
            for page_id, page in pages.items():
                for ii in page.get("imageinfo", []):
                    mime = ii.get("mime", "")
                    if mime.startswith("image/") and "svg" not in mime:
                        url = ii.get("thumburl") or ii.get("url")
                        if url:
                            results.append({
                                "url": url,
                                "title": page.get("title", ""),
                                "width": ii.get("thumbwidth", ii.get("width", 0)),
                                "height": ii.get("thumbheight", ii.get("height", 0))
                            })
            print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query, per_page=5):
    """Search Pexels for images. Use curl-style approach."""
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": per_page, "orientation": "landscape"},
            headers={"Authorization": PEXELS_API_KEY},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                best = photos[0]
                url = best["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def validate_image_url(url):
    """Verify image URL returns 200 and is > 5KB."""
    try:
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        else:
            print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
            # Try reading body size if Content-Length is missing
            if r.status_code == 200 and "image" in ct and cl == 0:
                body = r.content
                if len(body) > 5000:
                    print(f"  ✓ Image validated (body read): {len(body)} bytes")
                    return True
            return False
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
        return False


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=15
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Article inserted: {data[0].get('id', 'unknown')}")
            return data[0]
        print(f"  ✓ Article inserted (raw): {r.text[:100]}")
        return data
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ── ARTICLE 1: NEET Re-Exam Crisis ──

def write_neet_article():
    print("\n=== ARTICLE 1: NEET Re-Exam ===")
    
    # Image: search for NEET exam / Indian students exam
    commons_results = fetch_wikimedia_commons_images("NEET India medical exam students", 5)
    image_url = None
    image_caption = ""
    image_attribution = ""
    
    # Try Wikimedia Commons first
    for img in commons_results:
        if validate_image_url(img["url"]):
            image_url = img["url"]
            image_caption = "Students waiting outside an examination centre in India"
            image_attribution = "Wikimedia Commons"
            break
    
    # Fallback to Pexels
    if not image_url:
        pexels_url = fetch_pexels_image("Indian students examination hall")
        if pexels_url and validate_image_url(pexels_url):
            image_url = pexels_url
            image_caption = "Students at an examination centre in India"
            image_attribution = "Pexels"
    
    if not image_url:
        # More generic search
        pexels_url = fetch_pexels_image("university exam students India")
        if pexels_url and validate_image_url(pexels_url):
            image_url = pexels_url
            image_caption = "Students preparing for competitive examinations in India"
            image_attribution = "Pexels"
    
    body = """India will deploy Indian Air Force aircraft and Central Reserve Police Force personnel to transport question papers for the NEET-UG re-examination on June 21, marking the most militarised security operation ever mounted for a civilian entrance exam in the country's history.

The extraordinary measures follow the cancellation of the original NEET-UG 2026 exam after the Central Bureau of Investigation confirmed that a paper leak had compromised the test taken by over 22 lakh medical aspirants. The CBI has so far arrested 13 people in connection with the scandal, including a Pune school headmistress who confessed to leaking the physics section from memory after being appointed as a subject expert by the National Testing Agency.

## How the Leak Unravelled

The first signs of trouble emerged when a document circulated on messaging apps bore an uncanny resemblance to the actual question paper. The NTA initially dismissed the claims, but mounting evidence forced the government's hand.

Manisha Sanjay Havaldar, headmistress of a Pune school, was arrested on May 22 after the CBI established that she had recalled physics questions from memory and shared them with a student. The questions were then circulated via a messaging app at the request of another suspect, Mandhare. During raids on Havaldar's home, investigators recovered NEET question papers, NTA identity card copies, and cash. She admitted to using the school computer to print the leaked material and subsequently burning her handwritten notes and erasing chat histories.

The student who obtained the physics questions was arrested four days later. Investigations have since expanded to Nagpur, where candidates allegedly travelled to Pune the day before the exam to review the leaked questions in a private session.

## The Government's Response

Cabinet Secretary T V Somanathan chaired multiple coordination meetings with state chief secretaries, warning that "the full might and weight of law will fall on any person trying in any manner to distort, disrupt, or tamper with the integrity or smooth conduct of the re-examination."

The security architecture for June 21 is unprecedented. The Ministry of Home Affairs has directed the CRPF and CISF to guard question paper transportation, with the Indian Air Force providing airlift capability to minimise the chain of custody. Around 5,400 examination centres and nearly one lakh classrooms will be used, with the government pushing to hold the exam in government institutions wherever possible.

The NTA has also warned students against engaging with fresh claims of leaked papers circulating on social media. "These claims are false, fraudulent, and intended to mislead," the agency said, adding that it was filing formal complaints with law-enforcement and cyber-crime authorities.

## A Crisis of Trust

For the 22 lakh students preparing to retake the exam, the emotional toll has been severe. Many had already completed their Class 12 board exams and were expecting results that would determine their medical college admissions.

"I came out of the NEET exam feeling happy and confident," one aspirant told PTI. "Then suddenly, the news came that the exam had been cancelled. When I reopened my books, I was not feeling like studying. Sleep issues have started because all-nighters are again happening. I don't trust the system now."

The Chinese Embassy in India inadvertently inflamed the debate by posting about the integrity of China's Gaokao university entrance exam, drawing sharp backlash from Indian social media users who pointed out China's own history of organised exam cheating.

## What NRIs Should Know

For diaspora families with children or relatives preparing for medical entrance exams in India, the NEET scandal strikes at the heart of a system millions depend on. The CBI investigation is ongoing, the Supreme Court has heard petitions seeking the NTA's dissolution, and the June 21 re-exam will be watched as a referendum on whether India's examination infrastructure can be trusted.

Education Minister Dharmendra Pradhan has described the controversies as "deeply unfortunate" and vowed that no one responsible would be spared. Whether that promise holds will determine not just the fate of this year's medical aspirants, but the credibility of competitive examinations that remain the primary ladder of social mobility in India."""

    article = {
        "headline": "India Will Deploy Air Force Planes to Guard Its Medical Exam. Here Is How the NEET Scandal Unravelled.",
        "subheadline": "The CBI has arrested 13 people, a headmistress confessed to leaking the physics paper, and 22 lakh students must now retake the test under military-grade security on June 21.",
        "body": body.strip(),
        "slug": "neet-reexam-june-21-cbi-arrests-iaf-security-paper-leak-crisis-20260615",
        "category": "news",
        "vertical": "education",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "diaspora_angle": "NRI families with children or relatives preparing for medical entrance exams face uncertainty about the integrity of India's examination system.",
        "sources": json.dumps([
            "Press Information Bureau India",
            "Careers360",
            "PTI / Press Trust of India",
            "India Today",
            "Wikipedia / NEET 2026 controversy"
        ]),
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    
    return insert_article(article)


# ── ARTICLE 2: India's Heat Crisis ──

def write_heat_article():
    print("\n=== ARTICLE 2: India Heat Crisis ===")
    
    # Image: Kanpur factory, Indian heat, workers
    commons_results = fetch_wikimedia_commons_images("Kanpur factory workers India", 5)
    image_url = None
    image_caption = ""
    image_attribution = ""
    
    for img in commons_results:
        if validate_image_url(img["url"]):
            image_url = img["url"]
            image_caption = "Workers at a factory in Kanpur, Uttar Pradesh"
            image_attribution = "Wikimedia Commons"
            break
    
    if not image_url:
        commons_results = fetch_wikimedia_commons_images("India heatwave workers summer", 5)
        for img in commons_results:
            if validate_image_url(img["url"]):
                image_url = img["url"]
                image_caption = "Workers navigate extreme heat in an Indian city"
                image_attribution = "Wikimedia Commons"
                break
    
    if not image_url:
        pexels_url = fetch_pexels_image("Indian factory workers heat")
        if pexels_url and validate_image_url(pexels_url):
            image_url = pexels_url
            image_caption = "Workers in the heat at an Indian manufacturing facility"
            image_attribution = "Pexels"
    
    if not image_url:
        pexels_url = fetch_pexels_image("India heat wave summer factory")
        if pexels_url and validate_image_url(pexels_url):
            image_url = pexels_url
            image_caption = "Extreme heat conditions in India's industrial belt"
            image_attribution = "Pexels"
    
    body = """In the leather workshops of Kanpur, the centre of India's leather industry, production has dropped 40 per cent. Temperatures have crossed 46°C. Workers are drinking oral rehydration salts twice a day. Some are falling sick. Others are abandoning the factory floor and returning to their villages.

"My productivity is down 40 per cent," AKI CEO Asad K. Iraqi told Bloomberg, his brow glistening with sweat. "Workers can't survive in this heat without proper hydration and cooling." He has invested in additional cooling systems, but says it is not enough.

The scene in Kanpur is not an isolated crisis. It is playing out across India's manufacturing belt, construction sites, and delivery routes, and it is becoming clear that extreme heat is no longer just a public health emergency. It is a structural economic constraint that could shave percentage points off India's growth for years to come.

## The Numbers Are Worse Than Anyone Expected

A paper published in the journal *Economic Modelling* by researchers at the Centre for Social and Economic Progress and Delhi School of Economics has reframed the debate. Their central finding is that a 1°C annual rise in temperature variation reduces India's economic growth by 3.89 percentage points on average — nearly double earlier estimates that relied on national averages.

The World Bank projects that lost labour from rising heat and humidity could jeopardise 2.5 to 4.5 per cent of India's GDP by 2030. About 75 per cent of India's workforce — roughly 380 million people — is engaged in heat-exposed labour, from agriculture and construction to the exploding gig economy of food delivery and courier services.

For the gig workers who now form the backbone of India's urban services economy, the heat is not seasonal discomfort. It is a direct assault on income. Delivery riders, two-wheeler drivers, and courier staff must stay on the road through punishing heat because their pay depends on completing trips. The International Labour Organization has estimated that India will be among the worst-affected countries as heat stress erodes working hours globally.

## Regional Inequality Is Widening

The damage is not evenly distributed. India's northern plains and southeastern coast face the sharpest productivity losses, while Himalayan regions see more modest impacts. Under high-emission scenarios, a majority of India's population is projected to experience frequent "Caution" level heat conditions during summer, with the more dangerous "Extreme Caution" threshold increasingly being reached in densely populated northeastern regions.

The research suggests that climate change is not just reducing output — it is actively widening the gap between India's richer and poorer states. States with greater heat exposure tend to have weaker infrastructure, less air conditioning, and fewer resources to adapt, creating a self-reinforcing cycle of climate vulnerability and economic stagnation.

## What This Means for the Diaspora

For NRIs with investments in Indian manufacturing, infrastructure, or real estate, the heat crisis introduces a risk that does not appear on any quarterly earnings call. Make in India depends on a workforce that can show up and produce, and extreme heat is making that harder every summer.

For families back home, the consequences are immediate: elderly relatives navigating cities without adequate cooling, children attending schools with minimal ventilation, and breadwinners in the informal sector losing workdays to heat illness.

India's summer arrived early this year. Jackets were packed away by mid-February. In Delhi, the temperature touched 31°C on February 16. The pattern is clear: summers are starting sooner, lasting longer, and hitting harder. Until India treats heat as the macroeconomic emergency it has become — not just a weather event — the costs will keep compounding."""

    article = {
        "headline": "India's Factories Are Losing 40 Per Cent of Their Output to Heat. The Economic Cost Could Hit 4.5 Per Cent of GDP.",
        "subheadline": "In Kanpur, workers are collapsing or returning to their villages. New research shows the growth hit from rising temperatures is nearly double what economists previously believed.",
        "body": body.strip(),
        "slug": "india-extreme-heat-factory-productivity-40-percent-drop-gdp-economic-crisis-20260615",
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "diaspora_angle": "NRIs with investments in Indian manufacturing and families back home face growing risks from a heat crisis that is cutting factory output and threatening the health of vulnerable relatives.",
        "sources": json.dumps([
            "Bloomberg",
            "Economic Modelling journal (Centre for Social and Economic Progress / Delhi School of Economics)",
            "World Bank",
            "International Labour Organization",
            "Outlook Business",
            "Policy Circle"
        ]),
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    
    return insert_article(article)


# ── ARTICLE 3: Sovereign AI ──

def write_sovereign_ai_article():
    print("\n=== ARTICLE 3: Sovereign AI ===")
    
    # Image: Sarvam AI / Pratyush Kumar - try Wikipedia
    image_url = None
    image_caption = ""
    image_attribution = ""
    
    # Try Wikimedia Commons for IndiaAI, AI India
    commons_results = fetch_wikimedia_commons_images("IndiaAI Mission artificial intelligence India 2026", 5)
    for img in commons_results:
        title_lower = img.get("title", "").lower()
        if validate_image_url(img["url"]):
            image_url = img["url"]
            image_caption = "India's IndiaAI Mission is accelerating sovereign AI development"
            image_attribution = "Wikimedia Commons"
            break
    
    if not image_url:
        commons_results = fetch_wikimedia_commons_images("Sarvam AI Bengaluru artificial intelligence startup", 5)
        for img in commons_results:
            if validate_image_url(img["url"]):
                image_url = img["url"]
                image_caption = "India's AI startup ecosystem in Bengaluru is building sovereign alternatives"
                image_attribution = "Wikimedia Commons"
                break
    
    if not image_url:
        pexels_url = fetch_pexels_image("artificial intelligence data center server")
        if pexels_url and validate_image_url(pexels_url):
            image_url = pexels_url
            image_caption = "AI data centre infrastructure is at the heart of the sovereign AI debate"
            image_attribution = "Pexels"
    
    body = """On June 12, the United States government issued an export control order directing Anthropic to suspend all access to its most powerful AI models — Fable 5 and Mythos 5 — for every foreign national, whether inside or outside America. The ban extends even to foreign-national employees working at the company.

For India's technology sector, it was the clearest signal yet that the country cannot afford to build its future on AI systems controlled by a handful of American companies subject to the whims of American export policy.

## The Block and Its Fallout

Anthropic said it received the directive on June 12 and immediately complied, disabling Fable 5 and Mythos 5 for all foreign nationals. Access to the company's other AI systems remains unaffected, but the damage was done. Anthropic and OpenAI have both described India as their second-largest market after the United States.

"It completely changes things," said Aakrit Vaish, founder of Indian AI venture platform Activate, in an interview with TechCrunch. "I think this materially changes the way all of us should be thinking about sovereign AI in India."

Vaish said he woke up on the morning after the announcement "shocked and confused" and now plans to encourage companies in his portfolio to reduce their dependence on a small number of frontier AI providers. Vijay Rayapati, co-founder of Atomicwork, whose product engineering team is based in Bengaluru, warned that startups with teams spanning multiple countries face immediate risk if access to advanced AI systems becomes subject to geopolitical restrictions.

The suspension also threatens India's cybersecurity posture. Mythos is described as highly capable at finding and patching cybersecurity vulnerabilities, and Indian entities had joined Anthropic's "Project Glasswing" to access it. That access may now be disrupted.

## India's Answer: Sarvam AI and the IndiaAI Mission

India is not starting from scratch. Bengaluru-based Sarvam AI has raised approximately $300 million at a $1.5 billion valuation, making it India's largest pure-play AI startup funding round. HCLTech is leading the round with a $150 million investment, joined by Bessemer Venture Partners, Nvidia, Amazon, and Prosperity7 Ventures.

Sarvam's co-founders, Vivek Raghavan and Pratyush Kumar, unveiled their flagship model at Prime Minister Modi's AI summit in February. The company has trained a 105-billion-parameter large language model optimised for Indian languages, capable of handling code-mixed speech and dialectal variations that global models consistently struggle with.

"Today we show we can bring our own AI to a billion Indians," Kumar said at the unveiling.

The government has backed the push through the IndiaAI Mission, selecting 12 companies to build indigenous foundation models and providing compute subsidies — Sarvam alone has received 4,096 Nvidia H100 GPUs through the programme. Zoho founder Sridhar Vembu, who serves on the National Security Advisory Board, has urged the country to embrace smaller Indian and open-source models. T.V. Mohandas Pai has called for an annual ₹50,000 crore deep-tech fund and a ₹2,00,000 crore guarantee fund for hyperscale cloud, hardware, and chip manufacturing.

## The Strategic Gap Remains

The debate is not whether India should pursue sovereign AI — that question has been settled. The debate is whether it can move fast enough. India's ability to train frontier models still lags China, which itself trails the United States. The bottleneck is not just funding but access to advanced GPUs, data-centre capacity, and reliable power. Competing at the frontier could cost upward of $100 billion.

Not everyone agrees India should try to match American frontier capabilities dollar for dollar. Nandan Nilekani, the Infosys co-founder, and N. Chandrasekaran, chairman of Tata Sons, have argued India should focus on building AI-powered applications and enterprise solutions rather than pursuing frontier model training. The HCLTech investment in Sarvam represents a middle path: using an Indian company's models as the foundation for enterprise AI services sold to global clients.

## What NRIs Should Watch

For Indian technologists working in the United States, the Anthropic cutoff is personal. Many work at companies that depend on these models, and the export controls apply based on nationality, not location. For NRI investors, the sovereign AI theme is opening a new asset class: Sarvam's valuation jumped from $110 million to $1.5 billion in under three years, and the IndiaAI Mission is seeding dozens more startups.

The era of assuming that American AI would always be available to India is over. What comes next will depend on whether India can translate its alarm into infrastructure before the next export control order arrives."""

    article = {
        "headline": "Washington Has Cut Off India From Anthropic's Best AI. Bengaluru Is Building Its Own.",
        "subheadline": "The US blocked Fable 5 and Mythos 5 for all foreign nationals. India's Sarvam AI has raised $300 million and trained a 105-billion-parameter model for Indian languages. The sovereign AI race is on.",
        "body": body.strip(),
        "slug": "anthropic-fable-mythos-blocked-india-sarvam-ai-sovereign-model-indiaai-mission-20260615",
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "diaspora_angle": "Indian technologists in the US face export controls based on nationality, while NRI investors see a new asset class emerging in India's sovereign AI ecosystem.",
        "sources": json.dumps([
            "TechCrunch",
            "Outlook Business",
            "The Hindu BusinessLine",
            "Moneycontrol",
            "AInvest",
            "Bloomberg"
        ]),
        "published_at": datetime.now(timezone.utc).isoformat()
    }
    
    return insert_article(article)


# ── Main ──

if __name__ == "__main__":
    print("Starting Videshi News Writer - News batch")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    
    results = []
    
    r1 = write_neet_article()
    results.append(("NEET Re-Exam", r1))
    time.sleep(1)
    
    r2 = write_heat_article()
    results.append(("Heat Crisis", r2))
    time.sleep(1)
    
    r3 = write_sovereign_ai_article()
    results.append(("Sovereign AI", r3))
    
    print("\n=== SUMMARY ===")
    for name, r in results:
        status = "✓ INSERTED" if r else "✗ FAILED"
        article_id = r.get("id", "?") if isinstance(r, dict) else "?"
        print(f"  {status}: {name} (id={article_id})")
    
    print("\nDone.")
