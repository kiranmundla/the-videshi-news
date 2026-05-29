#!/usr/bin/env python3
"""
The Videshi News Writer — 2026-05-29 batch
Writes 3 fresh news articles with India/diaspora angle.
"""

import os, json, sys, time, re, uuid
import requests
from datetime import datetime, timezone

# Load Supabase credentials
def load_env(path):
    env = {}
    try:
        with open(os.path.expanduser(path)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    key = key.replace('export ', '').strip()
                    val = val.strip().strip('"').strip("'")
                    env[key] = val
                    os.environ[key] = val
    except FileNotFoundError:
        print(f"ERROR: {path} not found")
        sys.exit(1)
    return env

load_env('~/.env.supabase')
SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# Load Pexels key
try:
    load_env('~/workspace/.env.pexels')
    PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
except:
    PEXELS_KEY = ''

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
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

def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels. Returns image URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key available")
        return None
    
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-sS', f'https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=5&orientation=landscape',
                 '-H', f'Authorization: {PEXELS_KEY}'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                img_url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image found for '{q}': {img_url[:80]}...")
                return img_url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate that image URL returns 200 with image content-type and >5KB."""
    if not url:
        return False
    try:
        r = requests.get(url, timeout=10, stream=True, 
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct:
            if cl > 5000:
                print(f"  ✓ Image validated: {cl} bytes, {ct}")
                return True
            # Read first chunk to verify size
            chunk = r.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via read: {ct}")
                return True
        print(f"  ⚠ Image check: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ⚠ Image validation failed: {e}")
    return False

def publish_article(article):
    """Publish article to Supabase."""
    print(f"\n📝 Publishing: {article['headline']}")
    
    # Check for banned image sources
    img = article.get('image_url', '')
    if img:
        banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=', 'ccb=']
        if any(b in img for b in banned):
            print(f"  ❌ BANNED image source detected, removing: {img[:60]}")
            article['image_url'] = None
            article['image_caption'] = None
            article['image_attribution'] = None
    
    # Validate required fields
    hl = article.get('headline', '')
    if len(hl) < 20 or len(hl) > 200:
        print(f"  ⚠ Headline length issue: {len(hl)} chars")
    
    sub = article.get('subheadline', '')
    if len(sub) < 15:
        print(f"  ⚠ Subheadline too short: {len(sub)} chars")
        return None
    
    body = article.get('body', '')
    word_count = len(body.split())
    if word_count < 400:
        print(f"  ❌ Body too short: {word_count} words (minimum 400)")
        return None
    
    slug = article.get('slug', '')
    if not slug or slug == str(uuid.uuid4()):
        print(f"  ❌ Invalid slug")
        return None
    
    # Validate image
    if article.get('image_url') and not validate_image(article['image_url']):
        print(f"  ⚠ Image failed validation, removing")
        article['image_url'] = None
        article['image_caption'] = None
    
    payload = {
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': slug,
        'category': 'news',
        'vertical': 'news',
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'sources': json.dumps(article.get('sources', [])),
        'image_url': article.get('image_url'),
        'image_caption': article.get('image_caption'),
        'image_attribution': article.get('image_attribution'),
    }
    
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}
    
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers=HEADERS,
            json=payload,
            timeout=15
        )
        if r.status_code in (200, 201):
            result = r.json()
            if isinstance(result, list) and result:
                aid = result[0].get('id', 'unknown')
                print(f"  ✅ Published! ID: {aid}, slug: {slug}, words: {word_count}")
                return aid
            else:
                print(f"  ✅ Published! slug: {slug}, words: {word_count}")
                return 'ok'
        else:
            print(f"  ❌ Publish failed: {r.status_code} {r.text[:200]}")
            return None
    except Exception as e:
        print(f"  ❌ Publish error: {e}")
        return None


# ============================================================
# ARTICLE 1: India Sends Medical Supplies to Africa CDC Amid Ebola
# ============================================================
print("\n" + "="*60)
print("ARTICLE 1: India's Ebola Health Diplomacy")
print("="*60)

# Image: Try Jaishankar on Wikipedia, then Pexels for medical supplies
img1 = fetch_wikipedia_person_image("S. Jaishankar")
if not img1:
    img1 = fetch_pexels_image("medical supplies humanitarian aid", "medical relief packages")

article1 = {
    'headline': "India Just Sent Its First Medical Shipment to Fight Ebola in Africa. While America Builds Quarantine Camps, India Sends Cures.",
    'subheadline': "New Delhi dispatched diagnostics, therapeutics, and protective equipment to the Africa CDC in Uganda as the Bundibugyo outbreak tops 900 suspected cases and the US faces a court order blocking its controversial Kenya quarantine facility.",
    'slug': 'india-medical-supplies-africa-cdc-ebola-outbreak-health-diplomacy-20260529',
    'image_url': img1,
    'image_caption': "India's External Affairs Minister S. Jaishankar has championed the country's health diplomacy response to the Ebola crisis" if img1 and 'wikipedia' in str(img1).lower() else "India dispatched its first tranche of medical supplies to the Africa CDC in Uganda this week",
    'image_attribution': 'Wikimedia Commons' if img1 and 'wikipedia' in str(img1).lower() or img1 and 'wikimedia' in str(img1).lower() else 'Pexels',
    'sources': ["Nation Press", "Reuters", "World Health Organization", "CNN"],
    'body': """India confirmed on Friday that it has delivered its first consignment of medical supplies to the Africa Centres for Disease Control and Prevention in Uganda, stepping into a global health emergency that has now killed at least 223 people and infected more than 900 across the Democratic Republic of Congo and Uganda.

The announcement, made by Ministry of External Affairs spokesperson Randhir Jaiswal at the weekly briefing in New Delhi, marks India's most visible health diplomacy intervention since the COVID-19 pandemic — and it comes at a moment when the world's richest country is drawing fierce criticism for its own Ebola response.

## What India Sent

The consignment includes diagnostics, therapeutics, infection prevention and control materials, and case management support. The supplies were handed over by India's High Commissioner in Uganda to the Africa CDC's Eastern Africa Regional Coordinating Centre, and are being routed to affected communities in eastern DRC — the epicentre of the ongoing Bundibugyo Ebola outbreak.

"We have sent medical supplies to the Africa CDC," Jaiswal said. "We look forward to further helping in whatever manner we can with the countries and with the Africa CDC in dealing with this public health emergency."

External Affairs Minister S. Jaishankar had earlier flagged India's commitment on X, signalling that the response carries weight at the highest levels of government.

## The Outbreak by the Numbers

The World Health Organization reported on Friday that suspected cases have risen to 906, with 223 suspected deaths under investigation. The Bundibugyo strain — a rare form of Ebola for which there is no approved vaccine or cure — has a fatality rate of 30 to 50 percent among confirmed cases.

The WHO declared the outbreak a Public Health Emergency of International Concern on May 17, triggering a global response. India immediately issued travel advisories for Congo, Uganda, and South Sudan, and intensified screening at international airports.

India also quarantined its first suspected Ebola case — a Ugandan woman in Bengaluru — earlier this week, though results are still pending.

## The Serum Institute Connection

India's response is not limited to government-to-government aid. The Serum Institute of India, the Pune-based vaccine manufacturer that produced over a billion COVID shots, is developing a Bundibugyo-specific vaccine — ChAdOx1 Bundibugyo — in partnership with Oxford University. The WHO said this week that the candidate could be available for clinical trials within two to three months, making it one of the fastest paths to a vaccine.

The Serum Institute's involvement connects India's pharmaceutical muscle to the frontlines of the crisis. For a country that bills itself as the "pharmacy of the world," the Ebola response is both a humanitarian obligation and a strategic positioning play.

## America's Controversial Alternative

The contrast with Washington's approach could not be sharper. On Thursday, the White House announced it was setting up a 50-bed quarantine facility at Laikipia Air Base in Kenya — not to treat Africans, but to isolate American citizens exposed to Ebola so they would not be brought back to U.S. soil.

"The United States' highest priority remains protecting the health and security of the American people by working to prevent the Ebola outbreak from reaching our shores," a State Department spokesperson said.

The plan sparked immediate outrage in Kenya. The Katiba Institute, a civil society group, filed an emergency lawsuit, and a Kenyan high court on Thursday evening ordered a temporary suspension of the facility. Justice Patricia Nyaundi ruled that no one exposed to or infected with Ebola could be admitted under the arrangement until the case is fully heard. The next hearing is scheduled for June 2.

Kenyan doctors were blunt. "We are utterly disgusted by the government's apparent willingness to trade national biosecurity and the lives of its citizens for foreign aid," the Kenya Medical Practitioners, Pharmacists and Dentists Union said.

## What It Means for the Diaspora

For the estimated 4.5 million Indian Americans and millions more NRIs worldwide, the Ebola crisis carries both practical and symbolic weight. Practically, India's travel advisory means direct flights to East Africa require additional screening, and Indian workers in the region face heightened health protocols.

Symbolically, India's pivot to health diplomacy — sending cures rather than building camps — reinforces a narrative that New Delhi has cultivated since the pandemic: that India is a net provider of global public health goods, not a gatekeeper.

The contrast with the American approach will not be lost on diaspora voters, many of whom are watching Washington's handling of the crisis with growing unease.

## What Happens Next

The WHO is prioritising three experimental treatments — Mapp Biopharmaceutical's MBP134, Regeneron's maftivimab, and Gilead's remdesivir — for clinical trials. The most promising vaccine candidate, rVSV Bundibugyo from the International AIDS Vaccine Initiative, is still seven to nine months away from trial readiness.

India has indicated that Friday's delivery is only the "first tranche," suggesting more supplies are forthcoming. With the India-Africa Forum Summit postponed indefinitely due to the outbreak, New Delhi's medical response is now doing the diplomatic heavy lifting that the summit was supposed to accomplish.

For a country that sent vaccines to 25 African nations during COVID, the playbook is familiar. The stakes, with a 50 percent fatality rate, are considerably higher."""
}

result1 = publish_article(article1)


# ============================================================
# ARTICLE 2: RBI to Hold Rates in June, Hike Expected by Year-End
# ============================================================
print("\n" + "="*60)
print("ARTICLE 2: RBI Rate Decision")
print("="*60)

# Image: Try RBI Governor on Wikipedia
img2 = fetch_wikipedia_person_image("Sanjay Malhotra (banker)")
if not img2:
    img2 = fetch_wikipedia_person_image("Reserve Bank of India")
if not img2:
    img2 = fetch_pexels_image("Indian currency rupee bank", "central bank interest rates")

article2 = {
    'headline': "The RBI Will Hold Rates Next Week. But a Majority of Economists Now Expect a Hike Before December.",
    'subheadline': "With oil prices still 30 percent above pre-war levels and the rupee down 6 percent for the year, the central bank's rate-cut cycle may already be over — and the reversal could reshape everything from home loans to NRI fixed deposits.",
    'slug': 'rbi-hold-rates-june-hike-expected-year-end-oil-rupee-nri-deposits-20260529',
    'image_url': img2,
    'image_caption': "The Reserve Bank of India's Monetary Policy Committee meets June 5 to decide on interest rates",
    'image_attribution': 'Wikimedia Commons' if img2 and ('wikipedia' in str(img2).lower() or 'wikimedia' in str(img2).lower()) else 'Pexels',
    'sources': ["Reuters", "STCI Primary Dealer", "IIFL Capital"],
    'body': """The Reserve Bank of India will almost certainly hold its benchmark repo rate at 5.25 percent when its Monetary Policy Committee meets on June 5, according to a Reuters poll of 56 economists. But the more important signal buried in the survey is this: a majority now expect at least one rate hike before the year is out.

That shift — from "how many more cuts?" to "when does the tightening start?" — marks a potential turning point for India's economy, and for every NRI with money parked in Indian banks.

## The Numbers

Nearly 80 percent of economists — 44 of 56 — expect the MPC to hold rates unchanged next week. But among the rest, 11 forecast a 25-basis-point hike and one predicted a bigger 50-basis-point increase. In the April poll, only one respondent had predicted a June hike.

India's headline inflation remains benign at 3.48 percent in April — below the RBI's 4 percent medium-term target for over a year. That is the argument for patience. But the forces pushing the other way are accumulating fast.

## The Oil Problem

Crude oil prices have fallen 15 percent in May — the biggest monthly drop since March 2020 — on hopes that a US-Iran ceasefire extension will reopen the Strait of Hormuz. But even after the decline, Brent crude at around $92 a barrel remains roughly 30 percent above pre-war levels.

India is the world's third-largest crude importer. Every dollar increase in oil prices costs the Indian economy an estimated $1.5 billion annually. The war premium on oil has already fed into wholesale price inflation, which accelerated sharply in April, and threatens to push consumer prices higher in the months ahead.

"With growth facing downside risks while inflation faces strong upside pressures, we expect the RBI to hold rates steady in June, as supply shocks perceived as temporary might not warrant an interest rate action immediately," said Aditya Vyas, chief economist at STCI Primary Dealer.

The key word is "immediately." The market is no longer debating whether rates will rise — only when.

## The Rupee Factor

The Indian rupee has fallen roughly 6 percent against the dollar in 2026, weighed down by foreign capital outflows, elevated oil import bills, and a lack of the AI-related investment flows that have boosted markets in the US, Japan, and South Korea.

A weaker rupee makes imports more expensive, adding to inflationary pressure. It also makes Indian assets cheaper for foreign investors — but only if they believe the currency has found a floor. For now, the outflows continue.

Foreign investors have been net sellers of Indian equities for much of 2026, and India's weight in the MSCI Emerging Markets index is expected to drop to 11.2 percent after the latest rebalancing — down from a peak of roughly 20 percent in July 2024.

## What This Means for NRIs

For the millions of NRIs with Non-Resident External (NRE) and Non-Resident Ordinary (NRO) fixed deposits in Indian banks, the rate outlook matters directly.

If the RBI moves to hike rates later this year, NRE fixed deposit rates — which are already competitive at 6.5 to 7.5 percent for one-year terms — could climb further. That would widen the interest rate differential with US and UK deposits, making Indian FDs more attractive for parking overseas earnings.

But a weaker rupee partially offsets the higher yields. An NRI earning 7 percent on an Indian FD but losing 6 percent on currency depreciation is netting barely 1 percent in dollar terms. The calculus only works if the rupee stabilises.

For those with home loans in India — and many NRIs hold property — a rate hike would mean higher EMIs. Most Indian home loans are floating-rate, meaning any increase is passed through automatically.

## The Bigger Picture

The RBI cut rates three times between December 2025 and April 2026, bringing the repo rate down from 6.00 percent to 5.25 percent. That easing cycle was designed to support an economy navigating the fallout from the Iran war, weak capital flows, and sluggish private investment.

But the war has lasted longer than anyone expected. Oil prices, while down from their March peak, remain elevated. And wholesale inflation is now flashing warning signs that the cost pressures will eventually reach consumers.

"Interest rates are not a good tool to counter large supply shocks," Vyas cautioned. "Also, I do not think the RBI MPC will increase rates to defend the rupee since it is beyond the remit of the MPC."

Not everyone agrees. Several economists in the Reuters poll argue that the RBI may need to act pre-emptively to anchor inflation expectations — especially if the Iran-US ceasefire talks collapse and oil surges again.

## The June 5 Decision

The MPC's June meeting will almost certainly deliver a hold. Governor Sanjay Malhotra, who took over earlier this year, has signalled a data-dependent approach. The real question is what the post-meeting statement says about the path ahead.

If the RBI shifts its policy stance from "accommodative" to "neutral," markets will read it as a clear signal that the next move is up, not down. That single word change would ripple through bond markets, bank lending rates, and NRI deposit calculations within hours.

For an economy that was enjoying the tailwinds of rate cuts just two months ago, the reversal — if it comes — would be remarkably swift. The Iran war did not just disrupt oil markets. It may have ended India's easing cycle before it was supposed to finish."""
}

result2 = publish_article(article2)


# ============================================================
# ARTICLE 3: India-South Korea Defense and Cyber Pact
# ============================================================
print("\n" + "="*60)
print("ARTICLE 3: India-South Korea Defense Pact")
print("="*60)

# Image: Try Rajnath Singh on Wikipedia
img3 = fetch_wikipedia_person_image("Rajnath Singh")
if not img3:
    img3 = fetch_pexels_image("India military defense cooperation", "India South Korea flags")

article3 = {
    'headline': "India and South Korea Just Signed a Defense and Cyber Pact in Seoul. The Indo-Pacific Chessboard Is Getting More Crowded.",
    'subheadline': "Defence Minister Rajnath Singh's visit produced an MoU on military cyber security, defence information sharing, and joint technology development — deepening a 'Special Strategic Partnership' that both sides are now treating as a pillar of Indo-Pacific stability.",
    'slug': 'india-south-korea-defense-cyber-mou-rajnath-singh-indo-pacific-20260529',
    'image_url': img3,
    'image_caption': "Defence Minister Rajnath Singh signed the new MoU with his South Korean counterpart Ahn Gyu-back in Seoul",
    'image_attribution': 'Wikimedia Commons' if img3 and ('wikipedia' in str(img3).lower() or 'wikimedia' in str(img3).lower()) else 'Pexels',
    'sources': ["The Indian Eye", "Ministry of Defence, India", "Reuters"],
    'body': """India and South Korea have signed a new Memorandum of Understanding on defence, cyber security, and defence information sharing, marking the most significant upgrade to their military relationship since the "Special Strategic Partnership" was established in 2015.

The pact was signed in Seoul during Union Defence Minister Rajnath Singh's official visit, in the presence of South Korean Defence Minister Ahn Gyu-back. It formalises cooperation that both countries have been quietly building for years but are now willing to put on paper — and on display.

## What the MoU Covers

The agreement spans three core areas. First, defence cooperation: expanded joint exercises, defence industry collaboration, and technology transfer. Second, cyber security: shared protocols for countering cyber threats and protecting critical military infrastructure. Third, information sharing: institutional mechanisms for real-time intelligence coordination in the Indo-Pacific.

Officials said the pact would help both militaries improve "situational awareness" — the diplomatic way of saying they plan to share intelligence on Chinese naval and cyber activity in the region.

## Why Now

The timing is not accidental. South Korean President Lee Jae-myung visited India just a month ago in what both governments described as a milestone. That trip set the stage for Singh's follow-up, which was designed to convert political goodwill into operational defence agreements.

The strategic logic is straightforward. India and South Korea share a growing concern about Chinese assertiveness — India on its Himalayan border and in the Indian Ocean, South Korea on the Korean Peninsula and in its maritime approaches. Both are democracies with advanced defence industries. And both have been quietly building bilateral military ties that neither wants to frame publicly as anti-China, even though the subtext is unmistakable.

"India and South Korea are fully poised to take their partnership to new heights," Singh said after the signing ceremony. His counterpart Ahn called the relationship "a crucial pillar for stability in the Indo-Pacific."

## The Defence Industry Angle

For India's defence sector, the South Korean connection is increasingly valuable. South Korea is one of the world's top arms exporters, with companies like Hanwha Aerospace, Korea Aerospace Industries, and Hyundai Rotem producing everything from howitzers and fighter jets to submarines and infantry vehicles.

India's defence modernisation push — backed by a record ₹7.84 lakh crore budget allocation for 2026-27 — needs partners who can deliver technology transfer, not just finished products. South Korea, unlike some Western suppliers, has shown a willingness to co-develop and co-produce with Indian firms.

The two sides discussed expanding cooperation in UN peacekeeping operations and defence education exchanges, signalling a desire to institutionalise the relationship beyond equipment deals.

## The Cyber Dimension

The cyber security component of the MoU may be the most consequential in the long run. India has faced an escalating series of cyber attacks on its military and critical infrastructure — from power grids to defence research labs — that Indian intelligence officials have attributed to state-sponsored actors in China and Pakistan.

South Korea, which faces daily cyber probes from North Korea, has developed sophisticated cyber defence capabilities. The new agreement allows both countries to share best practices, conduct joint cyber exercises, and build stronger institutional mechanisms for threat detection and response.

For India's military, which is still in the early stages of building a dedicated cyber command, the South Korean partnership offers a fast track to capabilities that would take years to develop independently.

## The Quad Connection

India's deepening defence ties with South Korea sit alongside its existing partnerships in the Quad (with the US, Japan, and Australia), the recently activated India-France-Australia trilateral, and expanding defence cooperation with countries like Vietnam, the Philippines, and Indonesia.

The pattern is clear: India is building a web of bilateral and minilateral defence relationships across the Indo-Pacific, each calibrated to avoid provoking China into outright confrontation while steadily constraining Beijing's freedom of action.

South Korea, while not a Quad member, has been moving closer to the grouping's orbit. Its defence industries are already major suppliers to Poland, Australia, and several Southeast Asian nations. A deeper defence-industrial relationship with India would further embed South Korea in the emerging Indo-Pacific security architecture.

## What It Means for the Diaspora

India's defence partnerships rarely make headlines in NRI communities, but they have real consequences. A stronger India-South Korea axis could accelerate technology transfer in areas like shipbuilding, aerospace, and electronics — sectors where both NRI professionals and Indian industry stand to benefit.

South Korea is also home to a small but growing Indian community, particularly in the technology and academic sectors. The defence partnership adds another layer of institutional ties between the two countries, making it easier for Indian professionals to operate in South Korea's heavily networked economy.

For the broader diaspora, the pact is another data point in India's evolution from a non-aligned state to an active security provider in the Indo-Pacific. That shift changes how India is perceived in Washington, London, and Canberra — and how Indian Americans and British Indians can leverage their dual identities in strategic conversations.

## What Happens Next

The two sides agreed to deepen strategic communication through foreign and defence ministerial dialogues, and to support task forces established to fast-track joint initiatives. Singh and Ahn also discussed a potential visit by Singh to observe a South Korean military exercise later this year.

The MoU is a framework, not a procurement deal. The real test will be whether it leads to concrete defence-industrial contracts, joint exercises with operational substance, and genuine intelligence sharing — or whether it remains a diplomatic gesture.

Given the pace of events in the Indo-Pacific, neither country has the luxury of waiting."""
}

result3 = publish_article(article3)


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*60)
print("BATCH SUMMARY")
print("="*60)
results = [
    ("India Ebola Health Diplomacy", result1),
    ("RBI Rate Decision", result2),
    ("India-South Korea Defense Pact", result3),
]
for title, r in results:
    status = "✅" if r else "❌"
    print(f"  {status} {title}: {r}")
print(f"\nCompleted at {datetime.now(timezone.utc).isoformat()}")
