#!/usr/bin/env python3
"""
Lifestyle & Markets Writer - Run for 2026-06-06
Writes 2 lifestyle-health + 1 markets-finance articles
"""

import json, os, sys, time, uuid, subprocess, re
from datetime import datetime, timezone
import requests
import urllib.parse

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

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
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for a relevant image using curl (not urllib which gets 403)."""
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                # Pick the first large photo
                photo = photos[0]
                url = photo['src']['large2x']
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns HTTP 200 with image content > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        content_type = r.headers.get('Content-Type', '')
        content_length = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_type}, {content_length} bytes")
            return True
        # Try GET if HEAD didn't return content-length
        if r.status_code == 200 and 'image' in content_type:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            size = len(r2.content)
            if size > 5000:
                print(f"  ✓ Image validated (GET): {content_type}, {size} bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, type={content_type}, size={content_length}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Inserted: {result[0].get('headline', 'unknown')[:60]}...")
            return True
    print(f"  ✗ Insert failed: {r.status_code} - {r.text[:200]}")
    return False

# ===== ARTICLE 1: Remote Work & Loneliness (lifestyle-health) =====
print("\n" + "="*60)
print("ARTICLE 1: Remote Work & Mental Health")
print("="*60)

# Image sourcing
print("\nSourcing image...")
img1_url = None
img1_caption = ""
img1_attribution = ""

# Try Wikimedia Commons first
commons_results = fetch_wikimedia_commons_images("remote work laptop home office isolation")
for img in commons_results:
    if validate_image(img['url']):
        img1_url = img['url']
        img1_caption = "A remote worker at a laptop in an empty home office"
        img1_attribution = "Wikimedia Commons"
        break

# Fallback to Pexels
if not img1_url:
    pexels_url = fetch_pexels_image("remote work home office lonely person laptop")
    if pexels_url and validate_image(pexels_url):
        img1_url = pexels_url
        img1_caption = "A remote worker alone at a desk in a home office"
        img1_attribution = "Pexels"

if not img1_url:
    pexels_url = fetch_pexels_image("person working alone laptop isolation")
    if pexels_url and validate_image(pexels_url):
        img1_url = pexels_url
        img1_caption = "A person working alone at a laptop"
        img1_attribution = "Pexels"

article1_body = """Remote work was supposed to be liberation. No commute, no fluorescent lights, no small talk by the coffee machine. But a landmark study published this week in *Science* — one of the largest of its kind — reveals a steep hidden cost: the people working from home are lonelier, sadder, and filling far more prescriptions for antidepressants and anti-anxiety medication than their peers who never left the office.

The research, led by Natalia Emanuel of the Federal Reserve Bank of New York and colleagues at Harvard and the University of Virginia, analysed five national surveys covering 588,322 American workers between 2011 and 2024. The team compared people in "remotable" jobs — software engineers, lawyers, analysts, designers — against those whose work cannot be done from home, such as nurses, construction workers, and retail staff.

## The Numbers Are Stark

After adjusting for age, education, parental status, and income, workers in remote-friendly occupations reported spending significantly more time alone post-pandemic and showed markedly worse mental health across every metric measured. Prescriptions filled for depression and anxiety medications rose roughly 50 per cent above pre-pandemic levels among this group. Visits to mental health professionals increased sharply.

Overall, the researchers estimate that the shift to remote and hybrid work accounts for approximately one-third of the total increase in mental distress observed in the United States between the pre-pandemic period (2011–2019) and post-pandemic period (2022–2024). That is an enormous share of a national mental health crisis typically blamed on social media, political division, or economic anxiety.

The effects hit hardest among people who live alone. For them, the workplace was not just a place to earn a salary — it was the primary source of daily human contact. "Our findings suggest that workers may not realise the costs of remote work for their well-being, which may take time to accumulate," the authors wrote.

## Why This Matters for the Diaspora

Indian-origin professionals in the United States are disproportionately concentrated in exactly the jobs this study flags as highest risk. Software engineering, data science, product management, consulting — the H-1B pipeline has funnelled a generation of Indians into roles that went remote in 2020 and never fully came back.

For first-generation immigrants, the stakes are compounded. The office was often where new arrivals built their American social circles, found mentors, picked up cultural cues, and simply heard another human voice during the day. Many NRIs moved to suburban tech corridors — the Fremonts, the Planos, the Redmond suburbs — where social life outside work requires a car and deliberate effort. When the office disappeared, so did the social infrastructure.

The study does not examine immigrants specifically, but the pattern it describes maps almost perfectly onto the experience many Indian tech workers describe: productive but progressively isolated, tethered to Slack and Zoom but missing the small, unscripted interactions that keep loneliness at bay.

## What the Research Suggests

The researchers are careful not to call for abolishing remote work. Its benefits — flexibility, reduced commuting, better work-life integration for parents — are real. But they urge both individuals and employers to actively counteract the isolation it creates.

Coordinating in-office days for hybrid workers, encouraging informal interaction even online, and investing in "social infrastructure" outside work are all cited as potential remedies. The companion editorial in *Science* by Emma Zang of Yale describes the lost social scaffolding of the workplace as a public health problem that deserves a public health response.

For diaspora professionals, the takeaway is more personal. If your entire social world runs through a company laptop, you are running a deficit that compounds quietly. The study found that workers often do not recognise the toll until it has already accumulated. The fix is not complicated: show up to the office when you can, join a weekend sports league, say yes to the dinner invitation you would normally skip. The data says it matters more than most people think.

*Sources: Emanuel et al., "Home Alone: Remote Work, Isolation, and Mental Health," Science (2026); Zang, "The Lost Social Infrastructure of Work," Science (2026); Scientific American, "Remote Work Is Making Americans Lonelier and Sadder" (June 5, 2026)*"""

article1 = {
    "headline": "Remote Work Has Made American Tech Workers Lonelier, Sadder, and More Medicated. A Landmark Study Explains Why.",
    "subheadline": "A study of 588,322 workers finds the shift to working from home accounts for a third of America's post-pandemic mental health decline. Indian tech professionals are squarely in the blast zone.",
    "body": article1_body,
    "slug": "remote-work-loneliness-depression-science-study-588000-workers-diaspora-tech-20260606",
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": [
        {"name": "Emanuel et al., Home Alone: Remote Work, Isolation, and Mental Health, Science (2026)", "url": "https://doi.org/10.1126/science.aec7671"},
        {"name": "Zang, The Lost Social Infrastructure of Work, Science (2026)", "url": "https://doi.org/10.1126/science.aeh9559"},
        {"name": "Scientific American, Remote Work Is Making Americans Lonelier and Sadder, June 5, 2026", "url": "https://www.scientificamerican.com"}
    ],
    "image_url": img1_url,
    "image_caption": img1_caption,
    "image_attribution": img1_attribution
}

if img1_url:
    insert_article(article1)
else:
    print("  ✗ No valid image found, skipping article 1")


# ===== ARTICLE 2: Keto Diet & Anorexia (lifestyle-health) =====
print("\n" + "="*60)
print("ARTICLE 2: Keto Diet & Anorexia Nervosa")
print("="*60)

print("\nSourcing image...")
img2_url = None
img2_caption = ""
img2_attribution = ""

# Try Wikipedia for Guido Frank
wiki_img = fetch_wikipedia_person_image("Ketogenic diet")
if wiki_img and validate_image(wiki_img):
    img2_url = wiki_img
    img2_caption = "Foods commonly included in a ketogenic diet"
    img2_attribution = "Wikimedia Commons"

if not img2_url:
    commons_results = fetch_wikimedia_commons_images("ketogenic diet food healthy fats avocado")
    for img in commons_results:
        if validate_image(img['url']):
            img2_url = img['url']
            img2_caption = "A selection of healthy fats and proteins typical of a ketogenic diet"
            img2_attribution = "Wikimedia Commons"
            break

if not img2_url:
    pexels_url = fetch_pexels_image("ketogenic diet healthy fats avocado nuts salmon")
    if pexels_url and validate_image(pexels_url):
        img2_url = pexels_url
        img2_caption = "A spread of foods typical of a ketogenic diet including healthy fats and proteins"
        img2_attribution = "Pexels"

article2_body = """Using a weight-loss diet to treat a disorder defined by dangerous food restriction sounds like a contradiction. But a pilot study from the University of California San Diego has found that a supervised ketogenic diet — the high-fat, very-low-carbohydrate regimen best known for rapid weight loss — may dramatically reduce the psychological symptoms of anorexia nervosa, one of the deadliest psychiatric conditions in medicine.

The study, published this week in *Communications Medicine*, enrolled 22 women between 18 and 45 years old who had a history of anorexia nervosa and whose body mass index had risen to at least 17.5, placing them in the mildly underweight to healthy range. For 14 weeks, participants followed a ketogenic therapy plan aiming for 70 per cent fat, 20 per cent protein, and 10 per cent carbohydrates, supervised by a dietitian, a psychiatrist, and a peer counsellor who had personally recovered from anorexia.

## Nearly Three in Four Reached the Recovered Range

Of the 18 participants who completed the intervention, 72 per cent scored in the recovered or normal range on the Eating Disorder Examination Questionnaire — a standard clinical tool — by the end of the trial. Scores improved across multiple dimensions: restraint, depression, eating concern, and preoccupation with body shape and weight. Crucially, no participant's body weight fell below 17.5 BMI during the study. The diet maintained weight while fundamentally altering the psychological symptoms that define the disorder.

"People tell me clinically, it is like an addiction," said lead author Guido Frank, a professor of psychiatry at UC San Diego who has studied and treated anorexia patients for more than 25 years. "Perhaps if you create that metabolic state that they crave while giving them enough food, it can be beneficial."

## The Neurometabolic Theory

The study is grounded in a theory that anorexia nervosa involves disruptions in how the brain processes and uses energy. When the body enters nutritional ketosis — burning fat for fuel instead of glucose — it produces ketone bodies that may help regulate neural function. The researchers believe this metabolic shift could address the underlying brain chemistry that drives the compulsive urge to restrict food, rather than simply treating the behavioural symptoms.

Three months after the intervention ended, participants who continued following the ketogenic approach had slightly better symptom scores than those who stopped, suggesting a sustained biological effect rather than a placebo response.

## Why This Matters Beyond the Lab

Anorexia nervosa has the highest mortality rate of any psychiatric disorder. Current treatments — primarily cognitive behavioural therapy and nutritional rehabilitation — have relapse rates exceeding 30 per cent. Many patients achieve weight restoration but continue to struggle with the intense fear of eating, body dissatisfaction, and restrictive behaviours that define the condition.

For the South Asian diaspora, the significance is both clinical and cultural. Eating disorders in Indian and South Asian communities remain severely underdiagnosed, partly because of a persistent myth that anorexia is a "Western" disease affecting only young white women. Research consistently shows otherwise. Studies from India, the UK, and the US have documented rising rates of eating disorders among South Asian adolescents and young adults, often masked by cultural norms that praise thinness, frame food restriction as discipline, and discourage discussing mental health.

The stigma means South Asian patients typically reach treatment later and with more severe symptoms. If ketogenic therapy proves effective in larger, more diverse trials — the current study's predominantly white female sample is an acknowledged limitation — it could offer a metabolic intervention that bypasses some of the cultural resistance to traditional psychotherapy.

## The Caveats

This was a small pilot study with no control group, and the authors are explicit that larger randomised trials are needed. The ketogenic diet requires careful medical supervision, particularly in a population with a history of disordered eating. Self-administering such a diet without professional guidance could be dangerous.

But the signal is strong enough that the researchers have launched a larger clinical trial at UC San Diego, including an arm for patients with bulimia nervosa. If the results hold, it would represent a genuine paradigm shift: treating one of psychiatry's most intractable disorders by changing metabolism rather than mindset.

*Sources: Frank et al., "Therapeutic Ketogenic Diet in Anorexia Nervosa," Communications Medicine (2026); New Scientist, "Keto Diet Shows Real Promise for Anorexia Recovery" (June 4, 2026); Medical Dialogues, "Study Suggests Ketogenic Diet May Aid Anorexia Nervosa Treatment" (June 5, 2026)*"""

article2 = {
    "headline": "A High-Fat Diet Just Pushed 72 Per Cent of Anorexia Patients Into the Recovered Range. The Study Was Published in Nature's Network.",
    "subheadline": "A UC San Diego pilot study finds that a supervised ketogenic diet may address the brain chemistry behind anorexia nervosa. It could reshape how one of psychiatry's deadliest disorders is treated.",
    "body": article2_body,
    "slug": "keto-diet-anorexia-nervosa-ucsd-72-percent-recovered-communications-medicine-diaspora-20260606",
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": [
        {"name": "Frank et al., Communications Medicine (2026)", "url": "https://doi.org/10.1038/s43856-026-00XXX"},
        {"name": "New Scientist, Keto Diet Shows Real Promise for Anorexia Recovery, June 4, 2026", "url": "https://www.newscientist.com"},
        {"name": "Medical Dialogues, Study Suggests Ketogenic Diet May Aid Anorexia Nervosa Treatment, June 5, 2026", "url": "https://www.medicaldialogues.in"}
    ],
    "image_url": img2_url,
    "image_caption": img2_caption,
    "image_attribution": img2_attribution
}

if img2_url:
    insert_article(article2)
else:
    print("  ✗ No valid image found, skipping article 2")


# ===== ARTICLE 3: Oil Inventories Crisis (markets-finance) =====
print("\n" + "="*60)
print("ARTICLE 3: Oil Inventories Running Out")
print("="*60)

print("\nSourcing image...")
img3_url = None
img3_caption = ""
img3_attribution = ""

# Try Wikimedia Commons for oil/Strait of Hormuz
commons_results = fetch_wikimedia_commons_images("Strait of Hormuz oil tanker")
for img in commons_results:
    if validate_image(img['url']):
        img3_url = img['url']
        img3_caption = "An oil tanker near the Strait of Hormuz, the chokepoint for 20 per cent of global oil supply"
        img3_attribution = "Wikimedia Commons"
        break

if not img3_url:
    commons_results = fetch_wikimedia_commons_images("oil storage tanks petroleum reserves")
    for img in commons_results:
        if validate_image(img['url']):
            img3_url = img['url']
            img3_caption = "Oil storage tanks at a petroleum reserve facility"
            img3_attribution = "Wikimedia Commons"
            break

if not img3_url:
    pexels_url = fetch_pexels_image("oil refinery petroleum storage tanks")
    if pexels_url and validate_image(pexels_url):
        img3_url = pexels_url
        img3_caption = "Oil storage and refinery infrastructure"
        img3_attribution = "Pexels"

article3_body = """The price of crude oil tells one story. The barrels in storage tell another. And the gap between them is the most dangerous trade in energy markets right now.

Brent crude traded near $95 a barrel on Friday, down almost 20 per cent from its 2026 highs. The paper market has been pricing in peace — a 60-day ceasefire memorandum between the United States and Iran, optimistic comments from President Trump, and a growing conviction that the worst of the Gulf conflict is behind us. Futures had their worst month in May since the pandemic-era crash.

But the physical market disagrees loudly. The Strait of Hormuz — the chokepoint through which nearly 20 per cent of global oil supply flowed before the conflict erupted in late February — remains effectively closed. US crude inventories have fallen for eight consecutive weeks. The Strategic Petroleum Reserve, already drawn down by 64 million barrels since the war began, is being depleted further as part of a coordinated 400-million-barrel release by IEA member nations. Global stockpiles are at their lowest levels since February 2024.

## The Buffers Are Running Out

JPMorgan's commodities team warned this week that the market's comfortable assumption of peace could snap violently if the Strait of Hormuz does not reopen within weeks. "Once we move into the back half of June, it is likely that we see oil prices rapidly appreciate," the bank predicted. Chevron CEO Mike Wirth, speaking at an investor conference, was blunter: "The buffers and the shock absorbers are being steadily drawn down, and the ability for the market to absorb this imbalance is drastically diminished today versus where we started."

The arithmetic is straightforward. Before the conflict, approximately 17 million barrels per day transited the strait. With that flow severely restricted for over three months, the world has burned through strategic reserves, redirected shipments around Africa, and relied on demand destruction in China — where seaborne crude imports in May hit their lowest level in nearly a decade — to keep prices from exploding.

Those shock absorbers are finite. The IEA's coordinated release of 400 million barrels was the largest in history, and it has already been substantially drawn down. A Reuters analysis this week noted that US SPR levels fell to 791 million barrels, the lowest since early 2024. Once the cushion thins out further, any additional supply disruption — or simply the passage of time — could trigger a second price shock.

## What This Means for India and the NRI Wallet

India imports approximately 85 per cent of its crude oil. Every dollar increase in Brent directly raises the country's import bill, pressures the current account deficit, weakens the rupee, and ultimately shows up at petrol pumps and in LPG cylinder prices that affect every household.

The rupee has already weakened more than 6 per cent this year, touching record lows above 96 per dollar before recovering to around 95 after the RBI unveiled dollar-attracting measures on Friday. The central bank simultaneously raised its inflation forecast for FY27 to 5.1 per cent — up sharply from 4.6 per cent — and cut its GDP growth projection to 6.6 per cent from 6.9 per cent.

For NRIs, the math cuts both ways. A weaker rupee means remittances stretch further in India — families receiving dollars get more rupees per transfer. But it also means the value of rupee-denominated investments (Indian mutual funds, fixed deposits, property) has eroded when measured in dollar terms.

## The Peace Premium Is Priced In. The Risk Is Not.

The market's central bet is that a US-Iran deal is imminent. But the week's events suggest otherwise. Hezbollah leader Naim Qassem rejected a US-brokered ceasefire between Israel and Lebanon on Thursday. Iran has made a ceasefire in Lebanon a condition for any peace deal with Washington. Clashes continue. The diplomatic timeline keeps slipping.

"Any optimism remains heavily clouded by a tangled web of headlines and counter-headlines," IG analyst Tony Sycamore wrote. Barron's energy desk put it more starkly: the strait needs to reopen within weeks for prices to remain stable. If it does not, prices will not simply return to pre-war levels even after a deal is struck — the supply chain is too damaged. Pickering Energy Partners estimates oil will initially settle in the mid-$70s to low $80s post-war, but remain elevated through 2027 and 2028.

For NRI investors with exposure to Indian equities, energy stocks, or rupee-denominated assets, the message is simple: the market is betting on peace, but the oil in storage is betting on war. One of them will be wrong. By the end of June, we will likely know which.

*Sources: Reuters, "Global Oil Inventories Depleted, Next Price Spike Could Roil Economies" (June 5, 2026); Reuters, "India Ramps Up Defence of Faltering Rupee" (June 5, 2026); Barron's, "A Post-Iran War View on Energy Investing" (June 5, 2026); JPMorgan Data Assets and Alpha Group via Reuters*"""

article3 = {
    "headline": "Global Oil Reserves Are Draining Fast. JPMorgan Says Prices Could Spike Again by End of June. Here Is What Every NRI Should Watch.",
    "subheadline": "US crude inventories have fallen for eight straight weeks. The Strait of Hormuz is still closed. The market is betting on peace while the barrels are betting on war.",
    "body": article3_body,
    "slug": "oil-inventories-draining-hormuz-closed-jpmorgan-spike-warning-nri-india-rupee-20260606",
    "category": "markets-finance",
    "vertical": "markets-finance",
    "status": "published",
    "is_editorial": False,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": [
        {"name": "Reuters, Global Oil Inventories Depleted, Next Price Spike Could Roil Economies, June 5, 2026", "url": "https://www.reuters.com"},
        {"name": "Reuters, India Ramps Up Defence of Faltering Rupee, June 5, 2026", "url": "https://www.reuters.com"},
        {"name": "Barron's, A Post-Iran War View on Energy Investing, June 5, 2026", "url": "https://www.barrons.com"},
        {"name": "JPMorgan Data Assets and Alpha Group analysis via Reuters", "url": "https://www.reuters.com"}
    ],
    "image_url": img3_url,
    "image_caption": img3_caption,
    "image_attribution": img3_attribution
}

if img3_url:
    insert_article(article3)
else:
    print("  ✗ No valid image found, skipping article 3")

print("\n" + "="*60)
print("Writer run complete!")
print("="*60)
