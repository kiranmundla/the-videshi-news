#!/usr/bin/env python3
"""NRI World writer — 3 fresh articles, 2026-06-24 noon run.
Inserts into Supabase p2_articles with status='review', category='nri-world'.
Images sourced (Wikipedia/Commons/Pexels), compressed, re-uploaded to Supabase storage.
"""
import os, io, re, json, requests, urllib.parse
from PIL import Image

# ---- env ----
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

# ---------- image helpers (copied from IMAGE-SOURCING-RULES.md) ----------
def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:70]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error {person_name}: {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=8):
    params = {"action": "query", "generator": "search", "gsrsearch": search_query,
              "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
              "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1200", "format": "json"}
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                         headers=UA, timeout=15)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml" or ii.get("width", 0) < 500:
                    continue
                results.append({"url": ii.get("thumburl") or ii.get("url", ""),
                                "title": page.get("title", ""),
                                "width": ii.get("width", 0), "height": ii.get("height", 0)})
            if results:
                print(f"  ✓ Commons: {len(results)} imgs for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error {search_query}: {e}")
    return []

def fetch_pexels(query, n=5):
    if not PEXELS_KEY:
        return []
    try:
        r = requests.get("https://api.pexels.com/v1/search",
                         headers={"Authorization": PEXELS_KEY},
                         params={"query": query, "per_page": n, "orientation": "landscape"},
                         timeout=15)
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            out = [{"url": p["src"]["large2x"] + "" , "raw": p["src"]["original"] + "?auto=compress&cs=tinysrgb&w=1200",
                    "w": p["width"], "h": p["height"]} for p in photos]
            if out:
                print(f"  ✓ Pexels: {len(out)} imgs for '{query}'")
            return out
    except Exception as e:
        print(f"  ⚠ Pexels error {query}: {e}")
    return []

def download(url):
    try:
        r = requests.get(url, headers=UA, timeout=30)
        if r.status_code == 200 and len(r.content) > 8000:
            return r.content
        # curl fallback for wikimedia 429
        import subprocess
        out = subprocess.run(["curl", "-sS", "-A", UA["User-Agent"], "-o", "/tmp/_img.bin", url],
                             capture_output=True, timeout=40)
        with open("/tmp/_img.bin", "rb") as f:
            data = f.read()
        if len(data) > 8000:
            return data
    except Exception as e:
        print(f"  ⚠ download error: {e}")
    return None

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

def upload_image_to_supabase(jpeg_bytes, filename):
    r = requests.post(
        f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}",
        headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
                 "Content-Type": "image/jpeg", "x-upsert": "true"},
        data=jpeg_bytes, timeout=60)
    if r.status_code not in (200, 201):
        print(f"    ⚠ upload failed {r.status_code}: {r.text[:160]}")
        return None
    return f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"

def source_and_store(candidates, slug):
    """candidates: list of dicts with 'url'. Try each until one uploads."""
    for c in candidates:
        u = c.get("raw") or c.get("url")
        if not u:
            continue
        raw = download(u)
        if not raw:
            continue
        try:
            jpg = compress_image(raw)
        except Exception as e:
            print(f"    ⚠ compress fail: {e}")
            continue
        if len(jpg) < 10000:
            continue
        pub = upload_image_to_supabase(jpg, f"{slug}.jpg")
        if pub:
            print(f"  ✓ stored hero: {pub}")
            return pub
    return None

# ---------- articles ----------
ARTICLES = []

# === Article 1: India Day Parade USA 2026 curtain raiser ===
a1_body = """On a warm June evening in Mineola, more than 250 people pressed into the Theodore Roosevelt Executive and Legislative Building, with latecomers left standing along the walls. The occasion was not the parade itself but its prelude: the curtain raiser for the 15th India Day Parade USA, the Long Island procession that has become one of the New York region's most visible expressions of Indian-American identity.

The parade, set for Sunday, August 23, in Hicksville, will this year carry unusual weight. It is timed to commemorate the 80th anniversary of India's independence, a milestone that organizers are using to broaden the event from a cultural showcase into something closer to a community institution. "The India Day Parade has become one of the region's most significant celebrations of Indian heritage," said Pradeep Tandon, the general secretary, in a welcome address that thanked sponsors, volunteers and the elected officials who turned out.

**A parade that doubles as politics**

What distinguishes the Long Island event from a simple festival is the roster of public officials who attend. The curtain raiser drew New York State Senator Steven Rhoads, Town of North Hempstead Supervisor Jennifer DeSena, Assemblyman Jake Blumencranz, and Nassau County Comptroller Elaine Phillips. Tsewang Gyaltson, the consul for community affairs at the Consulate General of India in New York, represented the home government.

That mix is the point. For a diaspora that has spent four decades moving from immigrant enclave to suburban mainstream, the presence of county and state officials at an Indian cultural event signals a kind of arrival. The parade functions as an annual audit of the community's political standing, a moment when local representatives compete to be seen alongside a voting bloc that has grown both more numerous and more organized.

**The architecture of a volunteer event**

The organization behind the parade is striking for its longevity. Founder Bobby Kalote, who chairs the Nassau County Commission on Human Rights, has steered the procession from a modest gathering into what he and others describe as one of Long Island's premier cultural celebrations. Presidents Deepak Bansal and Vimal Goyal, who have led the group for three years, used the evening to call on businesses, families and community organizations to take part.

Goyal also singled out Venus Bhasin, a longtime fundraiser, for recognition he said was overdue. The gesture captured a recurring theme in diaspora institutions: they run almost entirely on unpaid labor, and their sustainability depends on honoring the handful of people who keep the machinery turning year after year. Special recognition went to community figures including Dr. Tarun Wasil, Shashi Malik, Dincil George of the Queens Parade, and Acharya Ji of Arya Samaj.

**Culture as the connective tissue**

The evening was not all logistics. Young performers Vaishavi Randev and Arshdeep Kaur danced; singer Anil Dua offered patriotic numbers; and Khuda Baksh, a finalist on Indian Idol Season 9, drew the audience into singing and dancing along. For second-generation attendees, these performances do quiet work, transmitting language, music and ritual to children who are growing up American but are being invited to claim an Indian inheritance too.

That generational question runs through Bansal's remarks. He framed the parade as a tool for engaging younger Indian-Americans, urging the community to "preserve cultural traditions, engage younger generations, and showcase the beauty and diversity of India." It is a familiar anxiety in mature diasporas: the founders who built these institutions are aging, and the question of who inherits them is unresolved.

**What's next**

The parade will originate in Hicksville on August 23, the culmination of a summer of preparation. For the organizers, the eightieth-anniversary framing is an opportunity to draw a larger crowd and a longer list of sponsors. For the wider Indian-American community on Long Island, the event is a reminder that belonging in America is not only a private achievement but a public performance, staged each August down a suburban street, witnessed by neighbors and courted by politicians. The curtain raiser was, in that sense, a rehearsal for a community telling its own story on its own terms."""

ARTICLES.append({
    "headline": "On Long Island, a Parade Becomes a Measure of How Far Indian-Americans Have Come",
    "subheadline": "The curtain raiser for the 15th India Day Parade drew 250 people and a row of elected officials, evidence of a diaspora moving from enclave to mainstream.",
    "slug": "india-day-parade-usa-2026-curtain-raiser-long-island-hicksville-diaspora-20260624",
    "body": a1_body,
    "diaspora_angle": "The Long Island India Day Parade shows how a maturing Indian-American community converts cultural celebration into political visibility, while wrestling with how to pass its volunteer-built institutions to a second generation growing up American.",
    "tags": ["nri", "diaspora", "usa", "new-york", "community", "india-day-parade", "culture"],
    "sources": [
        {"name": "The Indian EYE — 15th India Day Parade USA 2026: Curtain Raiser Draws A Full House", "url": "https://theindianeye.com/2026/06/22/15th-india-day-parade-usa-2026-curtain-raiser-draws-a-full-house-kicking-off-preparations-for-a-grand-celebration-of-indias-80th-independence-anniversary/"},
        {"name": "The Indian EYE — IDP USA India Day Parade of Long Island", "url": "https://theindianeye.com/"},
    ],
    "image_caption": "Indian-Americans celebrate Independence Day with a flag-raising procession in New York.",
    "image_attribution": "Wikimedia Commons",
    "image_commons_queries": ["India Day Parade New York", "Indian Independence Day flag United States", "India Day Parade Madison Avenue"],
    "image_pexels_queries": ["indian independence day flag celebration", "india flag parade crowd"],
    "score_total": 71,
    "urgency": "medium",
})

# === Article 2: International Yoga Day 2026 — UK diaspora ===
a2_body = """For one Sunday morning in June, the lawns of Britain looked briefly like the maidans of India. At the Oshwal Centre in Hertfordshire, hundreds rolled out mats for sessions that ranged from gentle stretching to "disco yoga." In Birmingham's Victoria Square, the Consulate General of India staged a mass session in the open air. In Slough, the Indian Diaspora in the UK group convened at Langley Academy. The occasion was the 12th International Day of Yoga, and its observance across Britain offered a study in how a national practice becomes a diaspora export, and then a piece of cultural diplomacy.

The theme this year, set by the Indian government and echoed at the United Nations, was "Yoga for Healthy Ageing," a deliberately practical frame that ties an ancient discipline to one of the developed world's most pressing problems: how to keep growing older populations mobile, independent and mentally well. The World Health Organization's Decade of Healthy Ageing supplies the policy backdrop; yoga, adaptable to almost any fitness level, supplies an accessible answer.

**A network, not a single event**

What stands out in Britain is not one marquee gathering but the density of the network. Indian missions, led in the UK by High Commissioner Vikram Doraiswami, coordinated events across London and beyond, but the actual organizing fell to a constellation of community bodies. The Oshwal Association, rooted in the Jain community, ran a five-hour programme of sessions for all ages. The Consulate General in Birmingham built a weeks-long run-up of curtain-raiser sessions, from "saree yoga" to mindfulness workshops led by the Brahma Kumaris, the Isha Foundation and the Art of Living.

This is the diaspora's organizational muscle on display. The same associations that run temples, language classes and festival celebrations can, on a single weekend, mobilize thousands for a coordinated cultural event. For a community often described in economic terms, by income, education or professional success, the yoga celebrations reveal a parallel infrastructure of civic and religious organization that rarely makes headlines.

**Soft power, gently applied**

Yoga occupies an unusual place in India's projection of itself abroad. Since Prime Minister Narendra Modi proposed the day at the UN in 2014, and the body adopted it with the support of 175 co-sponsoring nations, the practice has become India's most successful cultural export of the modern era, recognizable, uncontroversial and welcomed in places where harder forms of influence are resisted.

The British case shows how this works in practice. The events are organized by Indian missions and diaspora groups, but they draw participants well beyond the community, from local councillors to curious neighbors. Yoga becomes a bridge: a thing that is unmistakably Indian in origin yet has been thoroughly absorbed into Western wellness culture. When a High Commissioner leads a session in a public square, he is doing diplomacy that needs no translation.

**The diaspora as carrier**

There is a deeper point about who actually moved yoga from India to the world. It was not principally governments but migrants, the teachers, doctors, engineers and homemakers who carried the practice into suburban studios and community halls across decades, long before it became state policy. The 2026 celebrations, with their thicket of local associations, are a reminder that diaspora communities are not passive recipients of culture from the homeland but active transmitters of it, reshaping a tradition for new audiences and handing it onward.

**What's next**

The "Healthy Ageing" theme has a particular resonance for Britain's Indian community, among the most established of the country's South Asian populations, with a first generation now firmly in its later years. For families navigating elderly parents and the pressures of caregiving, a practice framed around active ageing is more than symbolism. As the day passes for another year, the question for these organizations is the familiar one of any diaspora institution: whether the energy on display this Sunday can be sustained, and passed to the children who watched their parents on the mat."""

ARTICLES.append({
    "headline": "How a Single Sunday of Yoga Maps Britain's Indian Diaspora",
    "subheadline": "From a Jain centre in Hertfordshire to a square in Birmingham, the 12th International Day of Yoga showed the organizing muscle, and the soft power, of a community.",
    "slug": "international-yoga-day-2026-uk-diaspora-healthy-ageing-soft-power-20260624",
    "body": a2_body,
    "diaspora_angle": "Britain's coordinated Yoga Day celebrations reveal the Indian diaspora as both the original carrier of yoga to the West and a living infrastructure of community organizations now deploying it as cultural diplomacy.",
    "tags": ["nri", "diaspora", "uk", "yoga", "culture", "soft-power", "health"],
    "sources": [
        {"name": "IANS — Indian missions worldwide mark International Day of Yoga", "url": "https://www.ianslive.in/"},
        {"name": "Oshwal Association of the U.K. — International Yoga Day 2026", "url": "https://oshwal.org.uk/"},
        {"name": "United Nations — International Day of Yoga 2026", "url": "https://www.un.org/en/observances/yoga-day"},
    ],
    "image_caption": "Participants take part in an outdoor International Day of Yoga session.",
    "image_attribution": "Wikimedia Commons",
    "image_commons_queries": ["International Day of Yoga London", "International Yoga Day United Kingdom", "International Day of Yoga group", "yoga session outdoor people"],
    "image_pexels_queries": ["group yoga outdoor mats", "yoga class park people"],
    "score_total": 69,
    "urgency": "medium",
})

# === Article 3: Modi Paris diaspora address ===
a3_body = """When Narendra Modi walked onto the stage at the Salle Pleyel in Paris, the concert hall that has hosted Stravinsky and Ravel briefly belonged to a different crowd. Indians from across France, Tamils and Punjabis, Gujaratis and Bengalis, filled the seats, chanting "Modi, Modi" and "Bharat Mata Ki Jai." The Indian prime minister, on the final leg of a visit that took in France and Slovakia, had come not to sign agreements but to address the diaspora, a ritual that has become a fixture of his foreign travel.

"Paris is a city of lights, colours, ideas and innovation," Modi told the gathering, crediting the Indian community with adding to its vibrancy. The line was characteristic of the diaspora-address genre: part flattery, part argument that overseas Indians embody the country's values abroad. But beneath the warmth lay a more deliberate message about the role Modi wants the global Indian community to play.

**The diaspora as strategic asset**

Modi described the diaspora as "a great strength" of the India-France strategic partnership, and the framing was telling. Where earlier Indian governments treated emigrants with a mixture of indifference and suspicion, viewing them as having left, Modi has spent his tenure recasting them as instruments of national influence. The Ministry of External Affairs noted that he had acknowledged the community's role in "connecting Indian innovation and ideas with global markets."

This is the diaspora reimagined as a network of unofficial envoys, what Modi has elsewhere called "Rashtradoots," or ambassadors of the nation. For the roughly 30 million people of Indian origin living outside India, it is a flattering identity, and one that places expectations alongside the affection. The community is asked to be a bridge: for trade, for technology, for India's image in the world's capitals.

**Mobility and money**

The substance, where there was any, concerned the plumbing of people-to-people ties. Modi noted the growing number of Indian students, professionals and tourists choosing France, and "expressed appreciation for the steps taken to ease mobility of people." He highlighted the expanding footprint of UPI, India's instant-payment system, in France, predicting it would boost tourism in both directions.

These are not trivial matters for the diaspora. Visa regimes, qualification recognition and the portability of digital payments are the daily texture of transnational life, the difference between a community that can move fluidly between two homes and one hemmed in by friction. That a prime minister chooses to speak of payment rails to a concert hall of expatriates suggests how central this practical agenda has become.

**The performance of belonging**

The emotional register was unmistakable. Diaspora members who met Modi described themselves as moved; one, a business owner from Coimbatore now living in Paris, called it "a matter of great pride." Another said it felt "as though someone from our own family has come here." This is the real currency of these events: the sense, for people living thousands of miles from where they were born, of being seen and claimed by the homeland.

Modi leaned into that emotion while deflecting credit. "What is the greatest force behind this transformation?" he asked, recounting India's economic gains over his twelve years in office, exports up many times over, a quarter of a billion people lifted from poverty. "It is not because of Modi. It is because of the people of India." The humility was rhetorical, but the connection it forged was real enough to the audience.

**What's next**

For all the spectacle, the Paris address fits a pattern that will continue wherever Modi travels. The diaspora has become a standing audience for Indian statecraft, courted on every continent, asked to carry the country's ambitions into the boardrooms and laboratories of their adopted homes. For overseas Indians, the embrace is genuine and gratifying. The open question, as it always is with soft power, is what the homeland asks of them in return, and whether a community spread across the democracies of the West will always find its interests aligned with New Delhi's."""

ARTICLES.append({
    "headline": "In a Paris Concert Hall, Modi Recasts the Diaspora as India's Ambassadors Abroad",
    "subheadline": "Addressing overseas Indians at the Salle Pleyel, the prime minister offered affection and a quiet argument: that the community is now an instrument of national influence.",
    "slug": "modi-paris-diaspora-address-salle-pleyel-india-france-rashtradoot-20260624",
    "body": a3_body,
    "diaspora_angle": "Modi's Paris address crystallizes how his government has recast overseas Indians from emigrants who left into strategic 'Rashtradoots' expected to carry India's trade, technology and image into their adopted countries.",
    "tags": ["nri", "diaspora", "france", "modi", "soft-power", "india-france", "politics"],
    "sources": [
        {"name": "The Indian EYE — PM Modi lauds diaspora as true strength of India-France ties", "url": "https://theindianeye.com/"},
        {"name": "IANS — PM Modi given warm welcome by Indian diaspora in Paris: MEA", "url": "https://www.ianslive.in/"},
        {"name": "IANS — Paris is city of lights and colours: PM Modi to Indian diaspora", "url": "https://www.ianslive.in/"},
    ],
    "image_caption": "Indian Prime Minister Narendra Modi.",
    "image_attribution": "Wikimedia Commons",
    "image_wikipedia_person": "Narendra Modi",
    "image_commons_queries": ["Narendra Modi 2024", "Narendra Modi portrait"],
    "image_pexels_queries": [],
    "score_total": 70,
    "urgency": "medium",
})

# ---------- run ----------
def main():
    for art in ARTICLES:
        slug = art["slug"]
        print(f"\n=== {slug} ===")
        wc = len(re.findall(r"\w+", art["body"]))
        print(f"  word_count ~{wc}")

        # ---- source hero image ----
        hero = None
        if art.get("image_wikipedia_person"):
            wu = fetch_wikipedia_person_image(art["image_wikipedia_person"])
            if wu:
                hero = source_and_store([{"url": wu}], slug)
        if not hero:
            for q in art.get("image_commons_queries", []):
                cands = fetch_wikimedia_commons_images(q)
                if cands:
                    hero = source_and_store(cands, slug)
                if hero:
                    break
        if not hero:
            for q in art.get("image_pexels_queries", []):
                cands = fetch_pexels(q)
                if cands:
                    hero = source_and_store(cands, slug)
                    art["image_attribution"] = "Pexels"
                if hero:
                    break
        if not hero:
            print("  ⚠⚠ NO HERO IMAGE SOURCED — skipping insert for safety")
            continue

        # ---- insert ----
        payload = {
            "headline": art["headline"],
            "subheadline": art["subheadline"],
            "slug": slug,
            "body": art["body"],
            "category": "nri-world",
            "vertical": "nri-world",
            "status": "review",
            "is_editorial": False,
            "diaspora_angle": art["diaspora_angle"],
            "tags": art["tags"],
            "sources": art["sources"],
            "image_url": hero,
            "image_caption": art["image_caption"],
            "image_attribution": art["image_attribution"],
            "score_total": art["score_total"],
            "urgency": art["urgency"],
            "word_count": wc,
        }
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=representation"},
            data=json.dumps(payload), timeout=30)
        if r.status_code in (200, 201):
            print(f"  ✅ inserted: {r.json()[0]['id']}")
        else:
            print(f"  ❌ insert failed {r.status_code}: {r.text[:300]}")

if __name__ == "__main__":
    main()
