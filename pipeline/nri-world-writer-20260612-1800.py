#!/usr/bin/env python3
"""NRI World Writer — 2026-06-12 18:00 UTC batch"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ── Supabase credentials ──
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
    """Download, compress, and upload image to Supabase storage."""
    import time
    for attempt in range(3):
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=30)
        if r.status_code == 429:
            wait = 5 * (attempt + 1)
            print(f"  Rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        r.raise_for_status()
        break
    else:
        r.raise_for_status()
    compressed = compress_image(r.content)
    size_kb = len(compressed) / 1024
    print(f"  Image compressed: {size_kb:.0f} KB")

    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    resp = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
    resp.raise_for_status()
    public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    print(f"  Uploaded: {public_url}")
    return public_url

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ────────────────────────────────────────────────
# ARTICLE 1: BAPS Paris Temple — First Hindu Temple in France
# ────────────────────────────────────────────────

art1_id = str(uuid.uuid4())
art1_slug = make_slug("baps-paris-temple-france-first-hindu-mandir-diaspora-europe")

art1_body = """France has never had a traditionally built Hindu temple. In September, that changes.

The BAPS Swaminarayan Hindu Mandir in Bussy-Saint-Georges, a suburban commune twenty-five kilometres east of central Paris, will open its doors from 2 to 14 September 2026 with a thirteen-day *Festival of Culture* — a marathon of Vedic ceremonies, cultural performances, and public celebrations that its organisers expect will draw tens of thousands of devotees and curious visitors from across Europe and beyond.

## Fifty-six years in the making

The temple traces its origins to a layover at Le Bourget Airport in July 1970, when Yogiji Maharaj, then head of the BAPS Swaminarayan Sanstha, paused on a stopover and envisioned a spiritual home for Hindus in France. Nearly two decades later, in 1988, his successor Pramukh Swami Maharaj blessed the land in Bussy-Saint-Georges by showering flowers from the sky — a gesture that, in the BAPS tradition, marks a site as sanctified.

Construction officially began in June 2024 with the laying of a foundation stone during a traditional Hindu ceremony. The stones themselves were hand-carved in India using techniques codified in the ancient *Shilpa Shastra*, the same architectural canon that guided the construction of the BAPS Abu Dhabi Mandir, which opened to global fanfare in February 2024.

## A spiritual home for Europe's Indian diaspora

For the estimated 700,000 people of Indian origin living in France, and the millions more across Western Europe, the mandir fills a conspicuous gap. The continent already has major BAPS temples in London (the Neasden Mandir, which opened in 1995) and the newer Abu Dhabi complex. But France, despite hosting one of the largest South Asian populations in continental Europe, has never had a traditionally designed stone temple — only community prayer halls and converted spaces.

The Paris mandir will span approximately 5,000 square metres across multiple floors. The ground level will house a community hall, library, exhibition centre, and dining area designed to serve visitors regardless of faith. The upper floor will contain the main prayer hall, where carved stone *murtis* of Shiva and Parvati, Ganesh, Ram and Janki, Krishna and Radha, Hanuman, and the Swaminarayan tradition's central deities will be installed in a ceremony known as *murti-pratishtha*.

## London to Paris on two wheels

The build-up has already spawned its own set of community events. In early June, fifteen cyclists aged eighteen to seventy-five completed a 315-kilometre charity ride from London to Paris in support of the mandir project. They departed from South London, rode through the English countryside to Newhaven, crossed the Channel by ferry, and pedalled through three days of northern French countryside before arriving at the Eiffel Tower. There, eleven local riders joined them for the final leg to Bussy-Saint-Georges, where swamis and hundreds of devotees greeted them.

"This whole journey was exceptionally well organised, with every detail carefully planned," one participant said. "Completing the challenge was only possible because of the commitment, encouragement, and teamwork of everyone involved."

## What to expect in September

The *Festival of Culture* will include a *Jal Yatra* — a boat procession along the River Seine — as well as a *Nagar Yatra* through central Paris, a *Palkhi Yatra* through Bussy-Saint-Georges, daily Vedic fire ceremonies, a women's convention, a *kirtan aradhana* (musical tribute), and the formal dedication assembly presided over by Mahant Swami Maharaj, the current spiritual head of BAPS. Registration is mandatory and can be completed at bapsmandirparis.fr.

For diaspora families in the United States and Canada already planning European summer trips, the September window offers a rare convergence: a once-in-a-generation spiritual milestone in one of the world's great cities. Travel operators — including at least one New Jersey-based agency specialising in BAPS pilgrimages — are already packaging multi-country Europe tours that include the inauguration.

## A pattern of ambition

The Paris mandir is part of a broader push by the BAPS Swaminarayan Sanstha to establish traditionally carved stone temples in global capitals. The Abu Dhabi mandir, which sits on twenty-seven acres of land gifted by the UAE government, attracted more than two million visitors in its first year. The London Neasden Mandir, built from 5,000 tonnes of Italian Carrara marble and Indian limestone, has become a fixture in the city's cultural landscape.

The Paris project completes a kind of triangle across three continents — and signals that for the Indian diaspora in Europe, the era of making do with rented halls and provisional spaces may finally be ending."""

# ────────────────────────────────────────────────
# ARTICLE 2: Singapore blocks anti-Indian xenophobic posts
# ────────────────────────────────────────────────

art2_id = str(uuid.uuid4())
art2_slug = make_slug("singapore-blocks-anti-indian-posts-xenophobia-china-platform")

art2_body = """Of all the claims that could animate a culture war in Singapore, "overrun by Indians" is among the more combustible. The city-state's government treated it accordingly.

On 6 June, Singapore's Ministry of Home Affairs ordered YouTube, Facebook, and X to block access to fourteen posts that, in the Ministry's telling, "target the Indian community and undermine Singapore's model of multiculturalism." The police issued the directions under the Online Criminal Harms Act, a 2023 law that gives authorities the power to compel platforms to disable content deemed harmful to Singapore's social fabric.

## What the posts said

According to the Ministry, the content selectively used footage of crowded streets in Little India and images of Hindu devotees at a religious festival in Pagoda Street to construct the narrative that Singapore was being "overrun" by its Indian population. A secondary strand argued that Singapore's multiracial policy was a "facade meant to appeal to Western values" and that the country's stability owed itself to its majority Chinese demographics rather than any deliberate commitment to pluralism.

The posts were not produced in Singapore. Investigations by the Ministry traced the content to a China-based platform, from where it spread to other sites and social networks. Law Minister Edwin Tong, who also serves as Second Minister for Home Affairs, told reporters that there was "no evidence at present to suggest that these posts were part of a coordinated campaign by any government." The content, he said, was "likely generated organically by various foreign netizens."

## A multiracial compact under pressure

Singapore's ethnic composition — roughly 75 per cent Chinese descent, 15 per cent Malay, and 7 to 9 per cent Indian origin — is the product of deliberate policy choices dating to independence in 1965. The government has long enforced ethnic quotas in public housing estates to prevent the formation of ethnic enclaves, mandated mother-tongue education in four official languages, and maintained a public philosophy of racial harmony that pervades everything from national service to school textbooks.

For the Indian community specifically, which numbers around half a million, the compact has produced visible achievements: Indian Singaporeans hold senior positions in government, business, and academia, and Little India functions as both a commercial district and cultural anchor. But tensions simmer beneath the surface, occasionally breaking into public view. Online commentary about "too many Indians" in the tech sector or complaints about the smell of Indian cooking in HDB corridors periodically surface — usually swiftly condemned by the state but never entirely stamped out.

## A warning shot to platforms

Tong's public statement struck a careful balance. He affirmed that "every community in Singapore here is valued and everyone has an equal place" while noting that the government "does not tolerate any narratives that seek to undermine Singapore's racial harmony, especially when it is propagated by foreigners." The Ministry added that "any attempt to pit one community against another here must be firmly rejected" and that "attacks coming from a foreign source are doubly unacceptable."

The directive is notable for its speed and specificity. Unlike broader content-moderation frameworks that operate through after-the-fact reporting, the OCHA gives Singapore's police the power to issue disabling directions directly to platforms — a mechanism that critics of the law have warned could chill legitimate speech but that, in this instance, was deployed against content the government characterised as racially inflammatory.

## What it means for the diaspora

For Indians living elsewhere in Southeast Asia, the Singapore government's response offers a counterpoint to less protective environments. In Malaysia, where ethnic Indians constitute roughly 7 per cent of the population, periodic anti-Indian sentiment tends to surface with less official pushback. In Australia, where hate crimes against Indian students made international headlines in 2009-2010, responses were slower and less coordinated.

Singapore's intervention also resonates with recent incidents closer to home for NRIs. In the United States, a Carnegie Endowment survey published in early 2026 found that one in four Indian Americans had been called a racial slur since January. Three Hindu temples in the San Francisco Bay Area were vandalised with Khalistani graffiti in the space of weeks. In Belfast, anti-immigrant riots targeted Indian businesses.

What Singapore demonstrated on 6 June was a government willing to use legal tools to draw a line — swiftly, publicly, and without equivocation. Whether other countries with large Indian diaspora populations take note is another question entirely."""

# ────────────────────────────────────────────────
# Image sourcing & upload
# ────────────────────────────────────────────────

print("=== Sourcing images ===")

# Article 1: BAPS temple — use BAPS Swaminarayan Hindu Temple (Wikimedia Commons)
print("\n[Art 1] BAPS temple image...")
baps_img_url = "https://upload.wikimedia.org/wikipedia/commons/0/05/BAPS_Shri_Swaminarayan_Hindu_Mandir_Night_View.jpg"
art1_image = upload_to_supabase(baps_img_url, f"{art1_id}.jpg")

# Article 2: Singapore — use Pexels Little India Singapore
print("\n[Art 2] Singapore Little India image...")
sg_img_url = "https://images.pexels.com/photos/34278799/pexels-photo-34278799.jpeg?auto=compress&cs=tinysrgb&w=1200"
art2_image = upload_to_supabase(sg_img_url, f"{art2_id}.jpg")

# ────────────────────────────────────────────────
# Insert articles
# ────────────────────────────────────────────────

print("\n=== Inserting articles ===")

articles = [
    {
        "id": art1_id,
        "headline": "Fifty-Six Years After a Prayer at Le Bourget, France Is Getting Its First Traditional Hindu Temple",
        "subheadline": "The BAPS Swaminarayan Mandir in Bussy-Saint-Georges opens in September with a thirteen-day Festival of Culture — a milestone for Europe's Indian diaspora that began with a 1970 airport layover.",
        "slug": art1_slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Paris mandir fills a gap for hundreds of thousands of Indians across Western Europe who have lacked a traditionally built stone temple, and its September inauguration is already drawing NRI families from the US, UK, and Gulf into pilgrimage-tourism packages.",
        "tags": ["nri", "diaspora", "baps", "paris", "temple", "france", "europe", "hindu"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "BAPS Official", "url": "https://www.baps.org/News/2026/London-to-Paris-Charity-Cycle-Ride-Supports-Historic-Paris-Mandir-Opening-31532.aspx"},
            {"name": "BAPS Mandir Paris", "url": "https://bapsmandirparis.fr"},
            {"name": "Hinduism Today", "url": "https://www.hinduismtoday.com/hpi/"},
            {"name": "Arte Charpentier Architects", "url": "https://www.arte-charpentier.com"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art1_image,
        "image_caption": "A BAPS Swaminarayan temple showcasing the traditional hand-carved stone architecture being replicated in Paris",
        "image_attribution": "Wikimedia Commons",
        "body": art1_body,
    },
    {
        "id": art2_id,
        "headline": "Singapore Just Blocked Fourteen Posts Targeting Its Indian Community. The Content Likely Came from China.",
        "subheadline": "The city-state invoked its Online Criminal Harms Act to order YouTube, Facebook, and X to disable videos claiming Singapore was being 'overrun by Indians' — a rare, swift use of state power to defend diaspora communities.",
        "slug": art2_slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Singapore's decisive legal intervention to protect its Indian minority offers a sharp contrast to how other countries with large NRI populations have responded to anti-Indian sentiment — and raises questions about what legal tools are available elsewhere.",
        "tags": ["nri", "diaspora", "singapore", "xenophobia", "little-india", "multiculturalism", "online-safety"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Mint", "url": "https://www.livemint.com"},
            {"name": "Business Today Malaysia", "url": "https://www.businesstoday.com.my"},
            {"name": "Channel News Asia", "url": "https://www.channelnewsasia.com"},
            {"name": "Nestia", "url": "https://news.nestia.com"},
            {"name": "Swadesi", "url": "https://swadesi.com"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art2_image,
        "image_caption": "A street in Little India, Singapore, adorned with colourful cultural decorations",
        "image_attribution": "Pexels",
        "body": art2_body,
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print("\nDone.")
