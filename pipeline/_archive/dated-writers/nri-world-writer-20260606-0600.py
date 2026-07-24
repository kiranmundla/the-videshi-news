#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
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

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A 17-Year-Old in Ontario Found the Flaw That Medical Science Missed for 53 Years. The Fix Fits in a Formula.",
        "subheadline": "Gurnoor Kaur's EigenPulse corrects a mathematical error in pulse oximeters that has been misreading oxygen levels in darker-skinned patients since the 1970s. She is 17.",
        "slug": make_slug("gurnoor-kaur-eigenpulse-oximeter-racial-bias-canada-science-fair"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "A Punjab-origin student in Canada solved a medical device flaw that disproportionately harms patients with darker skin — a problem the global medical establishment had accepted as intractable for decades. Her story illustrates how diaspora youth, straddling multiple worlds, bring perspectives that established institutions miss.",
        "tags": ["nri", "diaspora", "science", "canada", "healthcare", "innovation", "youth"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Dainik Bhaskar English", "url": "https://www.bhaskarenglish.in/local/punjab/news/17-year-old-punjab-origin-girl-solves-oximeter-racial-bias-138096917.html"},
            {"name": "Youth Science Canada", "url": "https://youthscience.ca"},
            {"name": "Waterloo Region DSB", "url": "https://www.wrdsb.ca/blog/2025/05/09/grade-10-innovator-represents-canada-on-the-world-stage/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/6285400/pexels-photo-6285400.jpeg",
        "image_caption": "A pulse oximeter measuring blood oxygen levels on a patient's finger",
        "image_attribution": "Pexels",
        "body": """For more than half a century, the pulse oximeter has been one of medicine's most trusted instruments — a small clip on the finger that tells doctors whether a patient is getting enough oxygen. It is used billions of times a year, in emergency rooms, ICUs, and home monitoring kits on every continent. And for 53 of those years, it has been quietly lying to doctors about patients with darker skin.

The device works by shining red and infrared light through the fingertip and measuring how much each wavelength is absorbed by haemoglobin in the blood. Oxygenated haemoglobin absorbs more infrared; deoxygenated haemoglobin absorbs more red. The ratio between the two gives the oxygen saturation reading. It is elegant, non-invasive, and — for millions of people — systematically inaccurate.

Studies published over the past decade, accelerated by COVID-19 mortality disparities, have confirmed what clinicians long suspected: conventional oximeters overestimate oxygen levels in patients with darker skin tones by two to five percentage points. The difference sounds small. In practice, it means patients who need supplemental oxygen or ICU admission are sent home. Data from American hospitals has linked this bias to measurably higher mortality rates among Black patients.

The global response, until now, has been to throw more data at the problem. The prevailing assumption was that the devices were calibrated on predominantly fair-skinned populations, and that better training datasets would fix the error. Researchers spent years collecting readings from diverse patient groups. The readings got marginally better. The fundamental problem persisted.

## The formula, not the data

Enter Gurnoor Kaur, a Grade 11 student at a high school in Ontario's Waterloo region, whose parents emigrated from Punjab. Kaur came to the oximeter problem sideways. She had been building an AI-powered platform called SynaptiQ to detect hospital-induced delirium — a project that had already sent her to the Regeneron International Science and Engineering Fair in 2025 as one of eight students representing Canada.

While testing SynaptiQ's physiological monitoring, she noticed the error patterns. Heart rate and oxygen readings were accurate for lighter-skinned patients but diverged sharply for those with darker complexions. Rather than accept the industry consensus that more data was the answer, Kaur went back to first principles.

She spent months working through university-level physics and mathematics textbooks, tracing the signal processing chain inside pulse oximeters from photon to screen. What she found was not a data problem. It was a mathematical one.

The traditional oximeter relies on a calculation framework derived from the Beer-Lambert Law, using what engineers call the "Ratio of Ratios" to convert light absorption into an oxygen percentage. That framework treats melanin — the pigment that determines skin colour — as a fixed constant that affects both wavelengths equally. In darker skin, it does not. Melanin scatters light in ways that are wavelength-dependent, and the standard cardiac model had simply omitted the relevant term from its equations. Remove that assumption, and the instability in the calculation becomes obvious.

## EigenPulse

Kaur's solution, which she named EigenPulse, adds a correction factor that dynamically adjusts for melanin-induced light scattering based on the spectral characteristics of the skin it is measuring. In plain terms, her formula tells the sensor to subtract the scattering artefact before computing the oxygen ratio, so the reading reflects only blood oxygen regardless of skin colour.

The elegance of the fix is that it does not require new hardware. EigenPulse is a software-level correction — a revised mathematical model that can, in principle, be applied to the signal processing firmware of existing devices.

At the 64th Canada-Wide Science Fair, held in Edmonton, Alberta, Kaur presented EigenPulse before a judging panel of more than 250 scientists, professors, and physicians. She was awarded the Best Project Award for Innovation — the fair's highest honour — selected from 344 projects submitted by 390 of Canada's top young researchers.

"When an 11th-grade student identifies and fixes a gap in medical technology that has claimed many lives for over three decades, it proves what young people can achieve when their curiosity is given the right direction and support," said Reni Barlow, Executive Director of Youth Science Canada. "Gurnoor has made our country proud."

## What comes next

Kaur's work now faces the long road from science fair to clinical deployment. Medical device regulation in both Canada and the United States requires extensive validation studies before firmware changes can be approved, and device manufacturers have their own timelines and incentive structures. The FDA issued guidance on pulse oximeter accuracy disparities in 2023, but binding standards have yet to materialise.

Still, the significance of Kaur's contribution is difficult to overstate. Where the medical establishment spent decades assuming the problem was insufficient data, a teenager from a Punjabi immigrant family in Ontario identified it as a missing term in a 53-year-old equation. The data was never going to fix a formula that was wrong from the start.

For the diaspora, the story carries a particular resonance. Kaur's perspective — shaped by moving between cultures, by noticing whose bodies medical technology was designed for and whose it was not — is precisely the kind of insight that emerges when communities straddle worlds. It is also a reminder that the diaspora's contributions to their adopted countries extend well beyond the boardroom and the ballot box. Sometimes they extend to the mathematics that keeps people alive."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Restaurant Empires Are Crossing Borders. The Target Is Not Expats — It Is Everyone.",
        "subheadline": "From Sanjeev Kapoor's Yellow Chilli in Silicon Valley to Dishoom eyeing Manhattan and Bulbul opening in London, a wave of Indian restaurant chains is betting that Indian cuisine can go genuinely mainstream.",
        "slug": make_slug("indian-restaurant-chains-global-expansion-yellow-chilli-dishoom"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian cuisine abroad has long been shaped by diaspora-run independents — the corner curry houses, the family-owned dosa joints, the biryani spots that serve as cultural anchors for NRI communities. The new wave of branded Indian restaurant chains entering the US, UK, and Gulf markets represents a shift from community comfort food to global mainstream ambition, powered by diaspora demand but no longer limited to it.",
        "tags": ["nri", "diaspora", "food", "restaurants", "business", "culture"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Restaurant Business Online", "url": "https://www.restaurantbusinessonline.com/emerging-brands/3-restaurant-concepts-set-invade-us"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2023/05/18/can-indian-cuisine-be-mainstream-cuisine-farzi-cafe-opens-first-outlet-in-us-with-the-vision/"},
            {"name": "Curly Tales", "url": "https://curlytales.com/londons-famous-indian-restaurant-dishoom-could-be-coming-to-nyc-in-2026/"},
            {"name": "London The Inside", "url": "https://londontheinside.com/best-new-restaurants-2026/"}
        ]),
        "score_total": 74,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Sanjeev_kapoor_at_the_Launch_of_new_restaurant_%27Arola%27_at_J_W_Marriott.jpg",
        "image_caption": "Celebrity chef Sanjeev Kapoor, whose Yellow Chilli chain is opening its first US location in Santa Clara",
        "image_attribution": "Wikimedia Commons",
        "body": """For decades, the story of Indian food abroad followed a predictable script. An immigrant family opens a restaurant. The menu covers the greatest hits — butter chicken, lamb rogan josh, garlic naan — calibrated to local palates. The regulars are mostly desi. The Yelp reviews call it "hidden gem." The owners work punishing hours. Some thrive. Many close within five years. The cuisine, for all its depth and regional variety, remains locked in a category that mainstream diners visit occasionally but rarely make a habit of.

That script is being rewritten. A new generation of Indian restaurant brands — backed by serious capital, professional management teams, and menus designed for crossover appeal — is pushing into the United States, the United Kingdom, and the Gulf with an ambition that goes well beyond serving the diaspora. They want to do for Indian cuisine what Nobu did for Japanese and Nando's did for Portuguese: make it a category that competes for the Tuesday night dinner, not just the special occasion.

## The names to know

The most prominent entrant is Sanjeev Kapoor's Yellow Chilli, arguably the most recognisable name in Indian home cooking. Kapoor, who hosted the long-running television show *Khana Khazana* and commands celebrity-chef status in every Indian household, is opening the chain's first American location in Santa Clara, California — squarely in the heart of the South Bay, where the Indian-American population is large, affluent, and discerning. The restaurant is slated to open at Monticello Apartment Homes, a planned community developed by the Irvine Company, with local operator Yogesh Gupta managing the US franchise.

Yellow Chilli positions itself as a "gastronomic tour of India" at moderate prices, with a menu that includes Kapoor's signature Lalla Mussa Dal — black and green lentils slow-cooked overnight with spices, cream, ghee, and butter — and Puran Singh da Tariwala Murgh, a chicken curry inspired by roadside dhaba cooking along the Ambala-Delhi highway. There are currently about 30 Yellow Chilli locations in India, with five more in the UAE and Oman. SK Restaurants, the Mumbai-based franchisor, oversees six other concepts and has signalled that the US market is a long-term priority.

Meanwhile, JKS Restaurants — the London-based group behind Michelin-starred Gymkhana, the Iranian-inflected Berenjak, and the meat-forward Brigadiers — has signed a 15-year lease for a 7,900-square-foot space at 1245 Broadway in Manhattan's NoMad district. It will be JKS's first owner-operated restaurant outside the UK, a deliberate step up from the licensing arrangements that brought Gymkhana to Riyadh and Berenjak to DUMBO House in New York.

"We think there's a huge opportunity for Indian restaurant growth in the US," Josh Kirk, JKS's commercial director, told the industry press. "We could have gone down the licensing franchise route, but the opportunity is so big, and we have worked so hard to retain control over the brand, so our view is to build our own team out there."

London itself is getting another notable arrival: Bulbul, from chef-restaurateur Rohan D'Souza and Twinkle Keswani, who was named Young Restaurateur of the Year by *The Economic Times* in 2023. Opening near Blackfriars this summer, Bulbul promises dishes that rarely travel beyond their home regions — Forest Pepper Crab Dosa from Tamil Nadu, Goan Shrimp Balchao on melba toast, Nilgiri Beef Short Rib Korma. The pair spent months travelling across India, embedding in local kitchens and markets, to build a menu that treats Indian cuisine as a continent of flavours rather than a single tradition.

And then there is Dishoom, the Bombay Irani cafe concept that has become London's most-loved Indian restaurant chain, which has been scouting locations in New York for a permanent outpost. CEO Brian Trollip confirmed the chain is actively pursuing a site in Manhattan, after a sold-out pop-up at Pastis proved that New Yorkers will queue for okra fries and keema pau with the same devotion Londoners have shown for a decade.

## Beyond the curry house

What distinguishes this wave from earlier attempts is not just scale but positioning. These are not restaurants designed primarily for the homesick — they are designed for the curious. Yellow Chilli's pricing is set to compete with Olive Garden and Cheesecake Factory, not with the independent Indian restaurants that already serve every American suburb. JKS is targeting the fine-dining corridor where Indian food has historically been absent. Bulbul is betting that regional specificity — the kind that French and Italian cuisine have long enjoyed — can work for Indian cooking too.

The timing is not accidental. The Indian-American population has reached 4.4 million and holds disproportionate purchasing power. Indian food content dominates social media algorithms. And the economics of the restaurant industry have shifted: the old model of a single owner-operator kitchen is being replaced by multi-unit, brand-driven concepts that can absorb real estate costs and marketing budgets that independents cannot.

## What the diaspora built

None of this would be possible without the foundation the diaspora laid. The thousands of family-run Indian restaurants across the English-speaking world — the ones that introduced their neighbours to tandoori chicken and saag paneer and mango lassi — created the baseline familiarity that these chains now build on. The diaspora did not just send remittances home. It exported a cuisine. The branded chains arriving now are, in a sense, the second act of a project that began in community kitchens.

The risk, of course, is that mainstreaming comes at the cost of authenticity — that the menu engineering required to hit a certain price point and appeal to a broad audience will sand away exactly the qualities that make Indian food compelling. Zorawar Kalra, whose Farzi Cafe opened its first US location in Bellevue, Washington, has spoken candidly about walking this line: "The biggest challenge is retaining top talent," he says, acknowledging that building a globally consistent kitchen culture is harder than designing a menu.

Whether these chains succeed commercially will depend on execution. Whether they matter culturally is already clear. For the first time, Indian cuisine is being treated not as a niche ethnic category but as a global platform — one that can support fine dining and casual chains, regional menus and fusion concepts, with the same range and ambition that Japanese, Mexican, and Italian food have long enjoyed. The diaspora built the runway. The planes are now taking off."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
