#!/usr/bin/env python3
"""NRI World Writer — 2026-06-14 12:00 UTC run
Publishes 2 articles: Bharat Innovates 2026 & Indians overtake England in Australia
"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ── Supabase config ──────────────────────────────────────────
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


# ── Image helpers ────────────────────────────────────────────
def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(img_url, filename):
    """Download, compress, upload to Supabase article-images bucket."""
    import time
    for attempt in range(3):
        try:
            r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com; contact@thevideshi.com)"}, timeout=30)
            r.raise_for_status()
            break
        except requests.exceptions.HTTPError as e:
            if r.status_code == 429 and attempt < 2:
                wait = (attempt + 1) * 5
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
    compressed = compress_image(r.content)
    size_kb = len(compressed) / 1024
    print(f"  Compressed to {size_kb:.0f} KB")

    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    resp = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
    if resp.status_code not in (200, 201):
        # Try PUT instead
        resp = requests.put(upload_url, headers=upload_headers, data=compressed, timeout=30)
    resp.raise_for_status()
    public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    print(f"  Uploaded: {public_url}")
    return public_url


# ── Timing ───────────────────────────────────────────────────
now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Bharat Innovates 2026
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_slug = make_slug("bharat-innovates-nice-modi-macron-indian-deep-tech-startups-global")

art1_body = """When Prime Minister Narendra Modi and French President Emmanuel Macron stepped onto the stage at the Palais des Expositions in Nice on June 14, the backdrop was not the usual row of flags and lecterns. It was a sprawling exhibition floor filled with 120 Indian deep-tech startups, each pitching products that a decade ago would have been unthinkable outside a Bangalore garage or an IIT lab.

Bharat Innovates 2026 is the maiden edition of what the Ministry of Education is calling a "global accelerator for the Indian education ecosystem." The three-day conclave, running through June 16, has drawn over 500 investors — venture capital firms, corporate strategists, sovereign wealth scouts — along with fifteen Indian universities and a roster of global CEOs. The timing, one day before the G7 summit begins nearby, is deliberate.

## Thirteen Sectors, One Message

The event covers thirteen sectors: advanced computing, semiconductors, space technology, defence innovation, biotechnology, healthcare, energy, climate solutions, advanced manufacturing, and more. The startups were selected by a Technical Oversight Committee headed by Ajay Kumar Sood, the Principal Scientific Adviser to the Government of India, from what officials described as a competitive national pool.

Among the founders walking the floor in Nice are Vikram Vishal of UrjanovaC, Prateek Golecha of Tricog Health (an AI-powered cardiac diagnostics startup), and Ajeet Babu PK of Gudlyf Mobility. OYO Rooms CEO Ritesh Agarwal and serial entrepreneur Ronnie Screwvala were also spotted interacting with Modi before the inauguration.

"This platform of Bharat Innovates is becoming a bridge between Indian talent and European capital," Modi said in his address. "A platform where India's young minds are receiving the opportunity to connect with European expertise."

## Why France, Why Now

The event is part of the India-France Year of Innovation, jointly launched by Modi and Macron in Mumbai earlier this year. Nice was chosen for its proximity to Sophia Antipolis, Europe's first and largest technology park — a 2,400-hectare cluster of some 2,400 companies that has served as France's answer to Silicon Valley since the 1970s.

Macron, for his part, leaned into the flattery. "India, a nation driven by research and innovation, is at the forefront of global innovation," he said, citing the Chandrayaan-3 lunar south pole landing as proof. "The feat was accomplished in record time, thereby demonstrating India's strength and innovative capability."

The diplomatic context matters. India and France have deepened defence and technology ties significantly over the past three years, and the innovation conclave is designed to extend that partnership into the commercial deep-tech space — areas where India has traditionally struggled to find non-American, non-Chinese capital.

## The Diaspora Bridge

For the Indian diaspora in Europe, the event carries a subtler significance. Several of the investors and mentors present in Nice are NRIs who have spent decades building careers in European technology and finance. The conclave gives them a structured way to connect with Indian innovation without navigating the usual bureaucratic friction.

"Getting visibility at a level where the Prime Minister of India and the President of France are present puts a spotlight on what we do," said Golecha of Tricog Health. "This not only creates business opportunities but also provides a great opportunity to create impact on the ground."

Whether Bharat Innovates becomes an annual fixture — a Davos for Indian deep tech, as some are already calling it — depends on whether the deals signed in Nice translate into shipped products and scaled businesses. For now, 120 startups have the attention of 500 investors and two heads of state. That is not a bad start."""

print("─── Article 1: Bharat Innovates 2026 ───")
# Image: Modi and Macron from Wikimedia Commons
art1_img_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_welcomes_the_President_of_France%2C_Mr._Emmanuel_Macron_at_Lok_Bhavan%2C_Mumbai.jpg/1280px-Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_welcomes_the_President_of_France%2C_Mr._Emmanuel_Macron_at_Lok_Bhavan%2C_Mumbai.jpg"
print(f"  Downloading image from Wikimedia Commons...")
art1_img_url = upload_to_supabase(art1_img_source, f"{art1_id}.jpg")

art1_data = {
    "id": art1_id,
    "headline": "Modi and Macron Open Bharat Innovates in Nice. The Real Story Is the 120 Startups Behind Them.",
    "subheadline": "India's maiden deep-tech showcase brings 120 startups, 500 investors, and 13 sectors to the French Riviera — one day before the G7.",
    "slug": art1_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The conclave gives NRI investors and entrepreneurs in Europe a structured way to connect with Indian innovation, while showcasing India's deep-tech ecosystem to global capital for the first time at this scale.",
    "tags": ["nri", "diaspora", "innovation", "france", "modi", "startups", "deep-tech"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Livemint", "url": "https://www.livemint.com/news/india/pm-modi-reflects-on-india-france-ties-as-he-jointly-inaugurated-bharat-innovates-conclave-with-macron-11781432890879.html"},
        {"name": "IANS", "url": "https://ianslive.in/"},
        {"name": "Careers360", "url": "https://news.careers360.com/modi-macron-launch-bharat-innovates-2026"},
        {"name": "YourStory", "url": "https://yourstory.com/2026/06/deeptech-focus-pm-modi-france-visit-tcs-anthropic"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art1_img_url,
    "image_caption": "Prime Minister Narendra Modi with French President Emmanuel Macron at a bilateral meeting in Mumbai",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}

try:
    sb_post("p2_articles", art1_data)
    print(f"✅ {art1_slug}")
except Exception as e:
    print(f"❌ {art1_slug}: {e}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Indians overtake England in Australia
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_slug = make_slug("indians-overtake-england-australia-largest-overseas-born-abs-data")

art2_body = """The numbers, when they finally arrived, were almost comically close. India: 971,020. England: 970,950. A margin of seventy people.

But the milestone they mark is not close at all. According to the Australian Bureau of Statistics, India has overtaken England as the largest source of overseas-born residents in Australia — the first time a non-British-origin group has held that position since records began in 1891. After 134 years atop the demographic leaderboard, England has been displaced by a country that barely registered on Australia's migration charts two decades ago.

## Five Hundred Thousand in a Decade

The shift has been swift. In 2015, Australia counted roughly 449,000 India-born residents. By June 2025, that number had surged to 971,000 — an increase of 522,000 people in ten years. The English-born population, by contrast, has been on a slow decline from its peak of just over one million in 2013, as the large wave of post-World War II migrants ages out.

Australia's total overseas-born population now stands at 8.8 million, or 32 per cent of the country's 27.6 million residents — the highest proportion since 1892. China (732,000), New Zealand (638,000), and the Philippines (413,000) round out the top five.

The Indian-born cohort is young, skilled, and concentrated in the country's two largest cities. Most arrived on skilled worker visas or as international students who transitioned to permanent residency. The median age for overseas-born Australians is 43, but for recent Indian arrivals, it skews significantly younger.

## The 'Model Minority' Problem

The Lowy Institute, one of Australia's most respected think tanks, was quick to complicate the celebration. In a May analysis titled "Beyond the model minority," researcher and author argued that reducing Indians to an economic success story is "corroding the foundations of social trust."

"Existing studies on the Indian diaspora have fixated on outcomes — be it economic or sentiment-focused," the Lowy analysis noted. "The processes informing Indian diaspora participation and levels of trust in public life remain underexplored."

The critique is pointed. On one hand, Indian Australians are framed as a model minority: highly educated, economically productive, culturally cohesive. On the other, the community has been a visible target of anti-immigration sentiment that has intensified since the pandemic. In late 2025, Indian officials formally expressed concern to the Australian government about the safety of its diaspora community, following a series of anti-Indian rallies.

## A Demographic Mirror

For the 35 million-strong global Indian diaspora, the Australian data point is part of a larger pattern. Indians are now the largest immigrant group in several countries, including the United States, the United Kingdom, and Canada. Remittances from the diaspora reached approximately $120 billion in 2024, making India the world's top recipient.

But numbers alone do not capture what it means to be the largest foreign-born group in a country whose national mythology was built on British settlement. The shift challenges Australia's sense of itself — who belongs, who is a "real" Australian, and whether multiculturalism extends beyond a policy slogan.

Vasan Srinivasan, president of the Federation of Indian Associations of Victoria and a resident since 1987, put it more simply. "Back then," he told the AAP, "if you saw an Indian at Flinders St Station, you'd take them home to have lunch or dinner." That intimacy of a small community has been replaced by something larger and more complex — a community that is now, by the numbers, Australia's defining immigrant story.

The ABS data carries one more detail worth noting. The country of birth with the highest median age in Australia is Latvia, at 80 years. The youngest is Qatar, at 15. India sits somewhere in between — young enough to grow, old enough to have roots."""

print("\n─── Article 2: Indians Overtake England in Australia ───")
# Image: Sydney Opera House from Pexels
art2_img_source = "https://images.pexels.com/photos/33378301/pexels-photo-33378301.jpeg?auto=compress&cs=tinysrgb&w=1200"
print(f"  Downloading image from Pexels...")
art2_img_url = upload_to_supabase(art2_img_source, f"{art2_id}.jpg")

art2_data = {
    "id": art2_id,
    "headline": "A Margin of Seventy People: India Just Overtook England as Australia's Largest Source of Overseas-Born Residents",
    "subheadline": "For the first time since records began in 1891, a non-British-origin group tops Australia's migration charts. The Indian-born population grew by 522,000 in a decade.",
    "slug": art2_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Nearly a million Indians now call Australia home, making it the fourth-largest Indian diaspora community in the world. The milestone reshapes the conversation about belonging and identity for Indian Australians.",
    "tags": ["nri", "diaspora", "australia", "migration", "demographics", "census"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Australian Bureau of Statistics", "url": "https://www.abs.gov.au/statistics/people/population/australias-population-country-birth/latest-release"},
        {"name": "AAP News", "url": "https://aapnews.aap.com.au/"},
        {"name": "Lowy Institute", "url": "https://www.lowyinstitute.org/the-interpreter/beyond-model-minority-rethinking-australia-s-indian-diaspora"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Foreign-born_population_of_Australia"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art2_img_url,
    "image_caption": "The Sydney Opera House and harbour — home to one of Australia's largest Indian-born communities",
    "image_attribution": "Pexels",
    "body": art2_body
}

try:
    sb_post("p2_articles", art2_data)
    print(f"✅ {art2_slug}")
except Exception as e:
    print(f"❌ {art2_slug}: {e}")


print("\n═══ Done ═══")
