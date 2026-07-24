#!/usr/bin/env python3
"""NRI World Writer — 2026-06-11 06:00 UTC run
Publishes 2 fresh NRI World articles to Supabase.
"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Supabase config ──────────────────────────────────────────────
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
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

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

# ── Image pipeline ───────────────────────────────────────────────
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def compress_image(img_bytes, max_width=1200, quality=80):
    if not HAS_PIL:
        return img_bytes
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
    """Download image, compress, upload to Supabase storage. Return public URL."""
    try:
        r = requests.get(img_url, headers=UA, timeout=30)
        r.raise_for_status()
        compressed = compress_image(r.content)
        sz = len(compressed)
        print(f"  Image downloaded: {sz/1024:.0f} KB")
        if sz < 5000:
            print(f"  ⚠ Image too small ({sz} bytes), using URL directly")
            return img_url

        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        }
        up = requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{filename}",
            headers=upload_headers,
            data=compressed,
            timeout=30
        )
        if up.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✅ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({up.status_code}): {up.text[:200]}")
            return img_url
    except Exception as e:
        print(f"  ⚠ Image pipeline error: {e}")
        return img_url

# ── Articles ─────────────────────────────────────────────────────

articles = []

# ──────────────────────────────────────────────────────────────────
# ARTICLE 1: London Pai-Paralkar Family Tragedy / NRI Mental Health
# ──────────────────────────────────────────────────────────────────
art1_id = str(uuid.uuid4())
art1_slug = make_slug("london-indian-family-pai-paralkar-elephant-castle-nri-mental-health")

art1_body = """When emergency services arrived at the Highpoint tower block in Elephant and Castle shortly after 7:30 on the morning of 27 May, three bodies lay in the courtyard below the 36th floor. Rakesh Pai, 47. Aditi Paralkar, 46. Their nine-year-old son, Sid. Metropolitan Police investigators are treating the case as a suspected murder-suicide. No one else is being sought.

The details that have emerged since — from neighbours, friends, local MP Neil Coyle, the *Daily Mail*, and *People* magazine — sketch a portrait of a family that, on paper, had the diaspora dream sewn up. Rakesh, known to friends as Robin, was a project manager who had worked at Barclays, Santander, and Deutsche Bank. Aditi had held senior positions in construction consulting and had helped install cladding at Heathrow Airport. They moved to Britain in the early 2000s after degrees from reputed Indian universities, bought a flat in Clapham worth roughly half a million pounds, and built a consultancy together.

Behind the CVs lay something far harder. Sid was born with kidney disease, learning difficulties, and partial physical disability. He could not speak. For years the family shuttled between the UK and India — six years spent in India seeking treatment that never produced a breakthrough, followed by a return to London when Aditi and Rakesh concluded the medical options had run out. The family was living temporarily in the Highpoint tower, a 458-unit luxury block where two-bedroom flats rent for £3,800 a month, while planning to combine their two Clapham properties into a single family home.

"It was a huge stress for both of them, but Adi in particular struggled to cope with what was going on," a friend told the *Daily Mail*. "She had no family in the UK and also did a very demanding job, so it was very difficult for her to manage everything. It took a huge toll on her mental health, and I think it may have just got too much for her."

Another acquaintance said that while Aditi was visibly struggling, Rakesh appeared composed — the steadier half. Neighbours, however, reported hearing shouting and screaming from the apartment in the two weeks before the tragedy.

Rakesh was no recluse. He volunteered with the Alzheimer's Society and the Thomas Pocklington Trust, a charity supporting blind and partially sighted people. Friends described him as a "people's person." He and Aditi baked pastries for neighbours; Sid would knock on doors to say hello.

The case has sent a chill through Britain's Indian diaspora, and for good reason. The family's circumstances — dual careers, a sick child, no extended family within reach, the relentless grind of caregiving in a country where your safety net is a WhatsApp group, not a grandmother down the road — are not unusual. They are, for thousands of NRI families, ordinary.

Mental health support in the diaspora remains chronically underdeveloped. Community organisations that serve Indian families in Britain overwhelmingly focus on cultural events, religious observance, and language preservation. Crisis-level mental health support — particularly for caregivers of children with severe disabilities — falls through the gaps. The NHS offers resources, but culturally specific outreach is thin. The stigma around seeking help persists.

A 2024 survey by the South Asian Mental Health Alliance found that fewer than one in five British South Asians who reported mental health struggles had accessed professional help. Among first-generation immigrants, the figure dropped to one in eight. The reasons cited most often: shame, language barriers, and a belief that family problems should stay within the family.

None of this excuses what happened at Highpoint Tower. But it should unsettle anyone who recognises the contours of the Pai-Paralkar family's life in their own. The couple who moved continents for treatment, who came back to a country where their closest support was colleagues and neighbours, who held demanding jobs while caring for a child whose condition would never improve — that family is not an outlier. It is a pattern.

Southwark Labour MP Neil Coyle, in a letter to residents of the building, called the deaths "a terrible tragedy." The investigation continues.

If you or someone you know is in crisis, contact the Samaritans (UK) at 116 123, the iCall helpline (India) at +91 9152987821, or the 988 Suicide and Crisis Lifeline (US) by calling or texting 988."""

print("=" * 60)
print("ARTICLE 1: London Pai-Paralkar Family Tragedy")
print("=" * 60)

# Image: Elephant and Castle area from Wikimedia Commons
img1_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Elephant_%5E_Castle%2C_looking_South_-_geograph.org.uk_-_3448520.jpg/1280px-Elephant_%5E_Castle%2C_looking_South_-_geograph.org.uk_-_3448520.jpg"
img1_url = upload_to_supabase(img1_source, f"{art1_id}.jpg")

articles.append({
    "id": art1_id,
    "headline": "They Had Careers, a Flat in Clapham, and a Son Who Could Not Speak. On the Morning of 27 May, All Three Fell from the 36th Floor.",
    "subheadline": "The deaths of Rakesh Pai, Aditi Paralkar, and their nine-year-old son Sid in a London tower block have forced a reckoning with the mental health crisis hiding in plain sight across the Indian diaspora.",
    "slug": art1_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The Pai-Paralkar tragedy exposes the invisible mental health crisis among NRI families: the absence of extended family support, the stigma around seeking help, and the grinding isolation of caregiving for a severely disabled child thousands of miles from home.",
    "tags": ["nri", "diaspora", "mental-health", "uk", "london", "caregiving"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "LiveMint", "url": "https://www.livemint.com/news/world/indian-family-jumps-to-death-from-36th-floor-flat-of-londons-skyscraper-heres-what-happened-11781067782034.html"},
        {"name": "People Magazine", "url": "https://people.com/couple-son-9-severe-illnesses-fall-high-rise-suspected-murder-suicide-11722476"},
        {"name": "The Sun", "url": "https://www.thesun.co.uk/news/35045831/family-killed-suicide-plunge-36th-floor-tower-block/"},
        {"name": "ConnectMyIndia", "url": "https://nri.connectmyindia.com/montreal/news/article/indian-family-found-dead-after-fall-from-london-high-rise-apartment-3813/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": img1_url,
    "image_caption": "The Elephant and Castle skyline in south London, where the Pai-Paralkar family lived in the Highpoint tower block",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
})

# ──────────────────────────────────────────────────────────────────
# ARTICLE 2: Rohan Chhetri Wins Armory Square Translation Prize
# ──────────────────────────────────────────────────────────────────
art2_id = str(uuid.uuid4())
art2_slug = make_slug("rohan-chhetri-armory-square-prize-parijat-shirishko-phool-translation")

art2_body = """Rohan Chhetri has spent most of his adult life moving between languages. Born in West Bengal to a Nepali-Indian family, educated in Mumbai and Syracuse, and now teaching at Case Western Reserve University in Cleveland, he has written three poetry collections, co-edited an anthology of an overlooked Asian American master, and translated a Nepali poet's selected works into English. His latest project — translating Parijat's *Shirishko Phool* — has just won the 2026 Armory Square Prize for South Asian Literature in Translation, and the result may be the most significant South Asian literary translation of the decade.

The award was announced during Himal Southasian's annual Fiction Fest. Chhetri's English rendering of the novel, titled *Flowers of the Siris Tree*, will be published by Open Letter Books in 2028. The jury praised the translation for capturing the psychological depth and emotional texture of the original — no small feat, given that the novel is widely considered the most important work in modern Nepali literature.

*Shirishko Phool*, written in 1964, won the Madan Puraskar — Nepal's highest literary award — making Parijat the first woman to receive it. The novel tells the story of Suyog Bir Singh, a retired soldier in middle age whose life has emptied out after the Second World War. He develops a desperate, unexpressed infatuation with Sakambari, the sister of a drinking companion. She is the complete antithesis of the traditional Nepali heroine: cynical, sometimes cruel, short-haired, chain-smoking. The psychological core of the story is Suyog's memory of his sexual exploitation of Burmese women during military service — a guilt that colours every subsequent relationship.

An earlier English translation, titled *The Blue Mimosa*, has been taught at the University of Maryland and is referenced in feminist and post-colonial literary criticism worldwide. But that translation dates to the 1970s. Chhetri's new version, according to the jury, brings a contemporary sensibility to the text while preserving its starkness.

The Armory Square Prize was established in 2022 by Armory Square Ventures, a New York State venture capital firm, and its co-founders Pia Sawhney and Jason Grunebaum, a Hindi literary translator who teaches at the University of Chicago. The prize was created to address a conspicuous gap: despite the wealth of literary output in South Asian languages, the number of translations into English has been, as Sawhney put it, "startlingly thin." Winners receive book publication through Open Letter Books, one of the few American university presses dedicated to literature in translation.

Chhetri's own literary career has moved fluently between creation and translation. His debut poetry collection, *Slow Startle*, won the Emerging Poets Prize in 2015. His second, *Lost, Hurt, or in Transit Beautiful*, won the Kundiman Poetry Prize in 2018 and was published by HarperCollins in India, Tupelo Press in the US, and Platypus Press in the UK. A recipient of a 2021 PEN/Heim Grant for translation, he published *The Dust Draws Its Face on the Wind*, a translation of the Nepali poet Avinash Shrestha's selected poems, through HarperCollins India in 2024. His poems have appeared in *The Paris Review*, *Poetry London*, and the Academy of American Poets' *Poem-a-Day* series, and have been translated into Turkish, Greek, and French.

At Case Western Reserve, where he serves as the Anisfield-Wolf Distinguished Visiting Writer, his academic work focuses on the transnational connections between Indian and Caribbean Anglophone poetry and on translation theory. It is a body of work that straddles the boundaries the diaspora itself straddles — between languages, between literary traditions, between the country where the stories were born and the country where they are read.

Parijat — born Bishnu Kumari Waiba — never left Nepal. She remained unmarried, dealt with severe physical disabilities, and died in 1993 at fifty-six. She wrote ten novels, three poetry collections, and was instrumental in Nepal's progressive literary movement. Her work has been studied through feminist, post-colonial, and ecocritical lenses, but its reach in English has been limited by the scarcity of quality translations.

That is precisely the gap the Armory Square Prize was designed to close. And in selecting Chhetri's translation of *Shirishko Phool*, the jury has ensured that one of South Asia's most radical novels will meet a new generation of English-language readers — many of them, no doubt, children of the diaspora who have heard the title but never read the book.

*Flowers of the Siris Tree* is scheduled for publication by Open Letter Books in 2028."""

print("\n" + "=" * 60)
print("ARTICLE 2: Rohan Chhetri Armory Square Prize")
print("=" * 60)

# Image: Parijat writer from Wikipedia
img2_source = "https://upload.wikimedia.org/wikipedia/commons/4/4b/Parijat_Nepali_writer.jpg"
img2_url = upload_to_supabase(img2_source, f"{art2_id}.jpg")

articles.append({
    "id": art2_id,
    "headline": "An Indian Poet Just Won America's Top South Asian Translation Prize. The Novel He Translated Changed Nepali Literature Forever.",
    "subheadline": "Rohan Chhetri's English rendering of Parijat's 1964 masterpiece Shirishko Phool has won the 2026 Armory Square Prize, bridging one of the diaspora's most enduring literary blind spots.",
    "slug": art2_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Chhetri's career — born in West Bengal, educated in Mumbai and Syracuse, teaching in Cleveland — embodies the transnational literary life the diaspora makes possible. His translation brings one of South Asia's most important novels to a new generation of English-speaking diaspora readers who may have heard the title but never read the book.",
    "tags": ["nri", "diaspora", "literature", "translation", "poetry", "nepali"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "ConnectMyIndia", "url": "https://nri.connectmyindia.com/chicago/news/article/indian-origin-writer-rohan-chhetri-wins-2026-armory-square-translation-prize-3815/"},
        {"name": "GoodReads", "url": "https://www.goodreads.com/author/show/15328440.Rohan_Chhetri"},
        {"name": "Case Western Reserve University", "url": "https://english.case.edu/faculty/rohan-chhetri/"},
        {"name": "Armory Square Ventures", "url": "https://armorysv.com/translation-prize"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": img2_url,
    "image_caption": "Parijat, the Nepali writer whose 1964 novel Shirishko Phool is the subject of Chhetri's prize-winning translation",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body
})

# ── Insert articles ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("INSERTING ARTICLES")
print("=" * 60)

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
