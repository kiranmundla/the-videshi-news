#!/usr/bin/env python3
"""
Lifestyle-Health + Markets-Finance writer for The Videshi.
Produces 2 lifestyle-health articles + 1 markets-finance article.
"""

import os, json, uuid, re, time, requests, urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

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

def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels using curl (urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                # Pick best photo (landscape, large enough)
                for photo in photos:
                    src = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                    if src:
                        print(f"  ✓ Pexels image found for '{q}': {src[:80]}...")
                        return src
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        # Download
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=30)
        if r.status_code != 200:
            print(f"  ⚠ Image download failed ({r.status_code}): {image_url[:80]}")
            return image_url  # Fall back to direct URL if it's a permanent source
        
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            print(f"  ⚠ Not an image ({content_type}): {image_url[:80]}")
            return image_url
        
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small ({len(r.content)} bytes): {image_url[:80]}")
            return image_url
        
        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': content_type,
            'x-upsert': 'true'
        }
        up = requests.post(upload_url, headers=upload_headers, data=r.content, timeout=30)
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({up.status_code}): {up.text[:200]}")
            # If source is permanent (Wikipedia/Pexels), use direct URL
            if 'upload.wikimedia.org' in image_url or 'images.pexels.com' in image_url:
                return image_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if 'upload.wikimedia.org' in image_url or 'images.pexels.com' in image_url:
            return image_url
        return None

def generate_slug(headline, date_str):
    """Generate a URL-friendly slug from headline."""
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug).strip('-')
    slug = slug[:80].rstrip('-')
    return f"{slug}-{date_str}"

def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) else data['id']
        print(f"  ✓ Article inserted: {art_id}")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None

def update_article(art_id, updates):
    """Update article in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{art_id}"
    r = requests.patch(url, headers=HEADERS, json=updates, timeout=30)
    if r.status_code in (200, 204):
        print(f"  ✓ Article updated: {art_id}")
    else:
        print(f"  ⚠ Update failed ({r.status_code}): {r.text[:200]}")

# ============================================================
# ARTICLE 1: Anxiety Medication Disparities (lifestyle-health)
# ============================================================

def write_article_1():
    print("\n=== ARTICLE 1: Anxiety Medication Disparities ===")
    date_str = datetime.now(timezone.utc).strftime('%Y%m%d')
    
    headline = "Asian Americans Have the Lowest Rate of Anxiety Medication Use in the Country. A National Study of 29,000 Adults Found That Cultural Stigma Is Only Part of the Explanation."
    subheadline = "A May 2026 Frontiers study found that even after controlling for income, insurance, and education, Asian adults had 45 per cent lower odds of taking anxiety medication than White adults. For South Asian families where mental health is still discussed in whispers, the treatment gap is likely even wider."
    slug = generate_slug("asian-americans-lowest-anxiety-medication-use-cultural-stigma-south-asian-nri", date_str)
    
    body = """Your cousin in New Jersey has been having panic attacks for two years. She has insurance. She has a therapist's number saved in her phone. She has not called it. If you grew up in a South Asian household, you know exactly why.

A study published in *Frontiers in Public Health* in May 2026 has put numbers on what most Indian Americans already sense but rarely discuss. Analysing data from 29,466 adults in the 2023 National Health Interview Survey, researchers found that Asian Americans who had been diagnosed with an anxiety disorder were far less likely than any other racial group to be taking medication for it. The gap is not small. Non-Hispanic White adults reported a medication use rate of 64.3 per cent. For Asian adults, the number was 45.1 per cent.

## The Odds Are Not in Your Favour

After adjusting for age, sex, income, insurance status, education, BMI, marital status, and geographic region, Asian adults still had 45 per cent lower odds of using anxiety medication compared with White adults (odds ratio 0.55, 95 per cent confidence interval 0.32–0.93). The disparity persisted even though the Asian subsample was younger (average age 38.5), more insured (79.3 per cent), wealthier (higher poverty ratio of 5.27 versus 4.33), and more educated (35.6 per cent with a bachelor's degree) than the overall sample.

In other words: having money, having insurance, and having a degree did not close the gap. Something else is going on.

## The Paradox of High Education, Low Treatment

The researchers call it the "paradox of high education but low utilisation." Asian Americans are the fastest-growing racial group in the United States and among the most educated. But only 8.6 per cent seek mental health services, compared with nearly 18 per cent of the general population. The study found that education, far from predicting higher medication use, actually had a negative association. The more educated you are, the less likely you are to take anxiety medication — a pattern that is especially pronounced among Asian Americans.

For South Asian families, this paradox is not abstract. It is the engineer in Sunnyvale who manages a panic disorder with breathing exercises learned from YouTube because telling his parents would mean admitting weakness. It is the medical resident who can diagnose generalised anxiety disorder in a patient but cannot bring herself to seek treatment for her own.

## What the Data Cannot Capture

The study's Asian subsample was 87 adults — a small number that limits statistical power for within-group analysis. But even with that constraint, the researchers observed something striking: among White adults, anxiety medication use increased steadily with age. Among Asian adults, it declined. Older Asian Americans were less likely to be taking medication than younger ones, a pattern that directly contradicts the trend in every other racial group.

The researchers attribute this to what qualitative and community-based studies have consistently found: strong stigma surrounding psychiatric medication in older generations of Asian Americans. The older the generation, the deeper the resistance.

For South Asians specifically, this maps onto a familiar cultural landscape. Mental illness is a private family matter, not a medical one. The phrase "log kya kahenge" — what will people say — is not just a social anxiety. It is a clinical barrier. A 2023 Emory University dissertation found that middle-aged immigrant South Asian American women faced compounding barriers to mental health treatment: acculturative stress, cultural stigma, and structural obstacles that persisted even in well-resourced communities.

## The Model Minority Trap

The study adds to a growing body of evidence that the "model minority" framing of Asian Americans actively harms their health outcomes. By portraying Asian Americans as uniformly successful and resilient, the myth excludes them from public health research, policy attention, and targeted intervention. The researchers note that most existing studies do not even separate medication use from broader mental health service patterns for Asian Americans, creating a blind spot in the clinical literature.

This blind spot is particularly dangerous for South Asians. The MASALA study (Mediators of Atherosclerosis in South Asians Living in America) has already established that South Asians face twofold higher coronary heart disease risk. The stress pathways that contribute to cardiovascular disease are not separate from the anxiety pathways that go untreated. Chronic untreated anxiety is not just a quality-of-life issue. It is a cardiovascular risk factor.

## What NRIs Can Do

The researchers recommend culturally responsive anxiety treatments designed specifically for Asian communities. But for NRIs reading this in the Bay Area, New Jersey, or Houston, the intervention starts closer to home.

If your parents dismiss anxiety as "just stress," they are not being callous. They are operating within a framework where mental illness carries social consequences that are, to them, more tangible than the illness itself. If your college-age child is struggling with anxiety but refuses medication, they may be absorbing a message about self-reliance that came from you, not from their therapist.

The study's most important finding is not that Asian Americans underuse anxiety medication. It is that income, insurance, and education — the three things immigrant families sacrifice everything to secure — do not fix the gap. The barrier is cultural, and cultural barriers require cultural solutions: therapists who speak your language, community mental health programmes that do not pathologise distress, and families that treat a prescription for anxiety the same way they treat a prescription for blood pressure.

Your cousin in New Jersey still has that number saved in her phone. The question is whether anyone in her family will tell her it is okay to call.

*Sources: Shah et al., Frontiers in Public Health, May 2026 (doi: 10.3389/fpubh.2026.1803386); 2023 National Health Interview Survey; Emory University dissertation on South Asian American women's mental health treatment barriers.*"""

    article = {
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': slug,
        'category': 'lifestyle-health',
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'sources': json.dumps([
            {"name": "Frontiers in Public Health", "url": "https://doi.org/10.3389/fpubh.2026.1803386"},
            {"name": "2023 National Health Interview Survey (NHIS)", "url": "https://www.cdc.gov/nchs/nhis/index.htm"},
            {"name": "Emory University — South Asian Women Mental Health", "url": "https://etd.library.emory.edu/concern/etds/tm70mw610"}
        ])
    }
    
    art_id = insert_article(article)
    if not art_id:
        return
    
    # Image: Pexels — therapy session, mental health, South Asian context
    img_url = fetch_pexels_image("south asian woman therapy session", "mental health counseling diverse")
    if img_url:
        filename = f"{art_id}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        if final_url:
            update_article(art_id, {
                'image_url': final_url,
                'image_attribution': 'The Videshi'
            })
    
    print(f"  ✓ Article 1 done: {headline[:60]}...")
    return art_id

# ============================================================
# ARTICLE 2: Mentally Active vs Passive Sitting & Dementia
# ============================================================

def write_article_2():
    print("\n=== ARTICLE 2: Sitting Type and Dementia Risk ===")
    date_str = datetime.now(timezone.utc).strftime('%Y%m%d')
    
    headline = "A 19-Year Study of 20,000 Adults Found That the Type of Sitting Matters More Than the Amount. Mentally Active Sitting Cuts Dementia Risk. Passive Sitting Raises It."
    subheadline = "Researchers tracked sedentary behaviour for nearly two decades and found that replacing one hour of TV-watching with reading or puzzles was associated with a significant reduction in dementia risk. For Indian tech workers who sit 10 hours a day and come home to Netflix, the distinction is not academic."
    slug = generate_slug("mentally-active-passive-sitting-dementia-risk-19-year-study-indian-tech-workers", date_str)
    
    body = """You sit at a desk for eight hours writing code. You sit on the train for 45 minutes reading the news. You sit on the couch for two hours watching a show. To your Fitbit, all three activities look identical. To your brain, they are not even close.

A 19-year cohort study published in the *American Journal of Preventive Medicine* in March 2026 has found that what you do while sitting may matter more for dementia risk than how long you sit. Researchers tracked over 20,000 adults and discovered that replacing mentally passive sedentary behaviour — television, scrolling, staring — with mentally active sedentary behaviour — reading, puzzles, office work, studying — was associated with a significant reduction in dementia risk.

## The Distinction Your Brain Makes

The study, led by André O. Werneck and colleagues, followed participants for up to 19 years, tracking their cognitive outcomes against their sedentary behaviour patterns. The key finding: mentally active sitting and mentally passive sitting have opposite associations with dementia. One hour of passive sitting replaced by one hour of active sitting corresponded to a measurable reduction in dementia incidence.

Previous research had already established that prolonged sitting increases dementia risk. But this study upends the assumption that all sitting is equally harmful. The brain, it turns out, distinguishes between being parked in front of a television and being parked in front of a book. The former is neurologically idle. The latter is not.

## Why This Matters for Indian Tech Workers

If you work in tech — and a disproportionate number of Indian Americans do — your day is a study in sedentary behaviour. You sit in a car or on a train. You sit at a desk. You sit in meetings. You sit at lunch. Then you go home and sit on a couch. The total daily sitting time for a typical software engineer in the Bay Area, Seattle, or Hyderabad can easily exceed 12 hours.

The good news from this study is that the eight or nine hours you spend coding, debugging, designing, or problem-solving are not the same as the two or three hours you spend watching Netflix afterward. Your work is mentally demanding. Your evening entertainment may not be.

This does not mean your desk job is healthy. Prolonged sitting still carries cardiovascular and metabolic risks. But for dementia specifically, the type of cognitive engagement during sedentary time appears to be a modifiable risk factor — one that most public health guidance does not yet distinguish.

## The Evening Hours Are the Danger Zone

For Indian families, the pattern has a generational dimension. Your parents, retired or semi-retired, may spend four to six hours a day watching television — serials, news channels, cricket replays. This study suggests that those hours carry a different neurological cost than the same amount of time spent reading, doing crosswords, learning a new language, or even playing cards.

The researchers specifically found that replacing mentally passive sedentary behaviour with mentally active alternatives was protective. This is not about reducing total sitting time, though that helps. It is about changing what happens during the sitting.

A separate cross-sectional study of 1,132 Chinese nurses, published in *Frontiers in Public Health*, found that nurses with more than four hours per day of mentally active sedentary behaviour had 47 per cent lower odds of burnout compared with those who had less than one hour. The cognitive engagement hypothesis extends beyond dementia to mental health more broadly.

## The Practical Implications

The study suggests a deceptively simple intervention: swap passive screen time for active engagement. Read instead of scrolling. Do a puzzle instead of watching a reel. Play chess on your phone instead of watching someone else play a video game. The brain treats these activities differently, and over 19 years, the cumulative difference appears to matter.

For NRI parents encouraging their children to "take a break from screens," the nuance is important. Not all screen time is passive. Reading on a Kindle is mentally active. Watching YouTube shorts is not. Coding on a laptop is mentally active. Scrolling Instagram is not. The medium is less important than the cognitive demand.

For older adults — including parents back home — the implications are more urgent. South Asians already face elevated risk for cognitive decline, driven by higher rates of diabetes, cardiovascular disease, and metabolic syndrome. Adding four hours of passive television to that risk profile is a compounding factor that is entirely within the family's control to change.

## What the Study Does Not Say

The researchers are careful to note that while the associations are significant, the interaction terms between sedentary type and dementia were not all statistically significant at conventional thresholds. The predicted probability plots showed meaningful trends, but this is observational data over 19 years, not a randomised controlled trial. Confounders exist.

What the study does establish is that decades of sedentary behaviour research that treated all sitting as equal were missing something important. Your brain does not care whether you are sitting or standing. It cares whether you are thinking.

Your mother's evening habit of watching three hours of serials and your father's evening habit of reading the newspaper for three hours may look the same from the outside. This study suggests they are not.

*Sources: Werneck et al., American Journal of Preventive Medicine, March 2026 (doi: 10.1016/j.amepre.2026.108317); Frontiers in Public Health — mentally active vs passive sedentary behaviour and burnout among nurses, 2026.*"""

    article = {
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': slug,
        'category': 'lifestyle-health',
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'sources': json.dumps([
            {"name": "American Journal of Preventive Medicine", "url": "https://doi.org/10.1016/j.amepre.2026.108317"},
            {"name": "Frontiers in Public Health — Sedentary Behaviour and Burnout", "url": "https://www.frontiersin.org/journals/public-health"}
        ])
    }
    
    art_id = insert_article(article)
    if not art_id:
        return
    
    # Image: Pexels — reading book couch, elderly reading
    img_url = fetch_pexels_image("elderly person reading book couch", "senior reading newspaper")
    if img_url:
        filename = f"{art_id}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        if final_url:
            update_article(art_id, {
                'image_url': final_url,
                'image_attribution': 'The Videshi'
            })
    
    print(f"  ✓ Article 2 done: {headline[:60]}...")
    return art_id

# ============================================================
# ARTICLE 3: India Gold Import Duty Doubled (markets-finance)
# ============================================================

def write_article_3():
    print("\n=== ARTICLE 3: India Gold Import Duty Doubled ===")
    date_str = datetime.now(timezone.utc).strftime('%Y%m%d')
    
    headline = "India Just Doubled the Import Duty on Gold to 15 Per Cent. Modi Asked the Nation to Stop Buying It. If You Are Planning a Wedding, Your Budget Just Changed."
    subheadline = "The largest gold import duty hike in over a decade has cratered demand, widened smuggling incentives, and sent jewellers scrambling. For NRIs who buy gold for weddings, festivals, and investment, the new math is punishing — but there are windows."
    slug = generate_slug("india-gold-import-duty-15-percent-modi-stop-buying-wedding-nri", date_str)
    
    body = """On May 13, 2026, India more than doubled its customs duty on gold from 6 per cent to 15 per cent. Two days later, Prime Minister Narendra Modi made a public appeal asking Indians to stop buying gold for a year. The combination of policy and persuasion has sent the Indian gold market into its sharpest disruption in over a decade.

If you are an NRI planning to buy gold for a wedding, a festival, or an investment, the landscape has changed fundamentally.

## The Numbers Behind the Shock

India imported 720 tonnes of gold in the fiscal year 2025-26, racking up a bill of $71.98 billion — an all-time record. Gold imports rose 24 per cent year-on-year in dollar terms, even as volume dipped marginally. Silver imports jumped 150 per cent to $12 billion. Together, precious metals are the second-largest contributor to India's current account deficit after crude oil.

With the Iran war driving oil prices up roughly 45 per cent since February, India's foreign exchange reserves are under extraordinary pressure. The rupee has weakened past ₹95 to the dollar. The government's response was blunt: make gold more expensive to import, and ask people to stop buying it.

The World Gold Council estimates that the duty hike alone will reduce combined jewellery and bar-and-coin demand by 50 to 60 tonnes in 2026 — roughly 10 per cent below 2025 levels. Crisil Ratings projects that gold jewellery retail volumes will fall 13 to 15 per cent in fiscal year 2026-27, pushing demand to its lowest level in a decade, excluding the pandemic year.

## The Domestic Market Is Already Dislocating

Within days of the duty hike, domestic gold prices began trading at steep discounts to landed prices. According to Kavita Chacko, Research Head for India at the World Gold Council, the domestic discount widened from an average of $14 per ounce before the hike to nearly $150 per ounce — roughly ₹450 per gram.

The discount exists because dealers who had imported gold at the lower 6 per cent duty are now offloading their inventory at reduced margins. "Jewellers are passing the benefits to consumers by even cutting making charges to spur demand," said N. Anantha Padmanabhan, Managing Director of Chennai-based NAC Jewellers.

But the discounts are temporary. Once pre-duty inventory is absorbed, the full 15 per cent duty will be reflected in domestic prices. Gold in the Mumbai spot market ended a recent week at ₹1,58,534 per 10 grams. At the new duty rate, future imports will add significantly more to the landed cost.

## Smuggling Will Surge — History Guarantees It

The World Gold Council's own data shows a consistent pattern: every time India has raised gold import duties since 2013, unofficial or smuggled gold inflows have increased. When duties were lowered, smuggling declined sharply.

A 15 per cent import duty, combined with 3 per cent GST, creates an 18 per cent wedge between international gold prices and India's domestic price. That wedge is a direct incentive for grey-market operators. The 2013 gold import restrictions, which similarly sought to contain the current account deficit, led to a surge in gold smuggling through airports, ports, and border crossings. Industry observers expect a repeat.

"Higher import duties widen the domestic-international price gap and increase the incentive for smuggling," Chacko said.

## What This Means for NRI Gold Buyers

For NRIs, gold is not just an investment. It is wedding infrastructure. A South Indian wedding without gold is incomplete. A Gujarati wedding without gold sets is unthinkable. The typical NRI family buying gold for a wedding in India now faces a substantially higher landed cost.

**The immediate window:** If you are buying gold in the next few weeks, the pre-duty inventory discounts being offered by dealers represent a brief opportunity. Making charges are being cut. Large chain stores are offering incentives. But this window closes once the old inventory is absorbed.

**The duty-free allowance:** Indian customs rules allow incoming passengers to bring gold duty-free up to certain limits (currently ₹50,000 for men and ₹1 lakh for women in jewellery). Beyond that, the 15 per cent duty applies. For NRIs who previously carried gold jewellery purchased abroad into India for weddings, the calculus has shifted — buying outside India and carrying it in may now save more than it used to, provided you stay within the duty-free limit.

**The investment angle:** Gold ETFs listed in India are not directly affected by import duty in the same way physical gold is, but the price of the underlying asset reflects the domestic premium. For NRIs with Indian demat accounts, gold ETFs and sovereign gold bonds (SGBs) — which the government has promoted as alternatives to physical gold — offer exposure without the duty markup. However, no new SGB issuances have been announced since 2023, and the existing ones trade at varying premiums.

**The remittance angle:** If you send dollars home and your family converts them to gold, the effective cost of gold has jumped not just because of the duty hike but also because of the rupee's depreciation. A 15 per cent duty on top of a 10 per cent rupee decline means the dollar cost of Indian gold is roughly 25 per cent higher than it was a year ago.

## Modi's Appeal — Unprecedented, But Not Unbacked

A sitting Prime Minister publicly asking citizens to stop buying gold is extraordinary. Modi's appeal is not legally binding, but it carries social weight, particularly among older generations and in rural areas where gold buying is seasonal and ceremonial.

Industry insiders report that Modi's statement has had a measurable chilling effect. "There is virtually no demand," said C.A. Surendra Mehta, spokesperson of the Indian Bullion and Jewellers Association. Smaller retailers, already stretched by record prices, are the most vulnerable. Mid-sized and regional players continue to see buying from affluent customers but are tightening inventory cycles.

For the wedding season, the appeal creates an awkward social dynamic. Families who reduce gold purchases may face questions. Families who maintain them may feel they are acting against a national imperative. The cultural negotiation is real and uncomfortable.

## The Bigger Picture

India's gold problem is a structural feature, not a temporary aberration. Indians buy gold because it is a store of value in a country with a history of currency depreciation, inflation, and limited access to diversified financial instruments. The government has tried everything — gold monetisation schemes, sovereign gold bonds, import duty adjustments — and none of it has fundamentally changed behaviour.

The 15 per cent duty is the most aggressive intervention yet. Whether it works depends on whether the global gold price stabilises, whether the rupee recovers, and whether the Iran war winds down. If gold continues its run toward $5,000 an ounce and the rupee stays above 95, the combined effect on Indian demand will be historic.

For NRIs, the advice is straightforward: if you need gold for a wedding or ceremony in the next six months, buy soon and buy smart. If you are investing, consider financial gold products over physical. And if your mother calls from India to discuss gold prices, she is not making small talk. She is doing portfolio management.

*Sources: World Gold Council India data; Crisil Ratings report on gold jewellery volumes; Reuters — India gold import duty hike; The Hindu Business Line — gold discounts post duty hike; Ministry of Commerce and Industry trade data.*"""

    article = {
        'headline': headline,
        'subheadline': subheadline,
        'body': body,
        'slug': slug,
        'category': 'markets-finance',
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'sources': json.dumps([
            {"name": "World Gold Council — India Gold Market Update", "url": "https://www.gold.org/goldhub/data/gold-demand-trends"},
            {"name": "Crisil Ratings — Gold Jewellery Volumes FY27", "url": "https://www.crisil.com"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/markets/gold/gold-offered-at-450g-to-indian-consumers-after-import-duty-hike/article71016944.ece"},
            {"name": "Reuters — India Gold Import Policy", "url": "https://www.reuters.com"}
        ])
    }
    
    art_id = insert_article(article)
    if not art_id:
        return
    
    # Image: Pexels — Indian gold jewelry, wedding gold
    img_url = fetch_pexels_image("Indian gold jewelry wedding", "gold necklace traditional Indian")
    if img_url:
        filename = f"{art_id}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        if final_url:
            update_article(art_id, {
                'image_url': final_url,
                'image_attribution': 'The Videshi'
            })
    
    print(f"  ✓ Article 3 done: {headline[:60]}...")
    return art_id


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("The Videshi — Lifestyle-Health + Markets-Finance Writer")
    print(f"Run time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    
    results = []
    
    a1 = write_article_1()
    if a1:
        results.append(('lifestyle-health', a1))
    
    a2 = write_article_2()
    if a2:
        results.append(('lifestyle-health', a2))
    
    a3 = write_article_3()
    if a3:
        results.append(('markets-finance', a3))
    
    print(f"\n{'=' * 60}")
    print(f"DONE — Published {len(results)} articles:")
    for cat, aid in results:
        print(f"  [{cat}] {aid}")
    print(f"{'=' * 60}")
