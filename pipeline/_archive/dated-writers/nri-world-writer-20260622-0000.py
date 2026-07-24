#!/usr/bin/env python3
"""
Videshi NRI World Writer — June 22, 2026
3 NEW articles (category: nri-world, status: review, is_editorial: False):
  1. GOPIO-CT 20th Anniversary — Connecticut chapter honors 5 leaders, gives $50k to charity
  2. Documented Dreamers — America's Children Act push; Indian-origin kids aging out at 21
  3. Indian mango season in America — kesar/alphonso demand surge + Sara Gonzales backlash
"""

import os, json, requests, urllib.parse, subprocess, io
from datetime import datetime, timezone

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"


# ─── Image sourcing functions ────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0)
                })
            if results:
                print(f"  \u2713 Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape",
            headers={"Authorization": PEXELS_KEY, "User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  \u2713 Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None


def download_and_compress(url, slug):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code != 200:
            print(f"  \u26a0 Download failed ({r.status_code}): {url[:80]}")
            try:
                tmp = f"/tmp/{slug}_src"
                subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, url], timeout=30, check=True)
                with open(tmp, "rb") as f:
                    content = f.read()
                if len(content) < 5000:
                    return None
                r_content = content
            except Exception:
                return None
        else:
            r_content = r.content
        ct = r.headers.get("Content-Type", "") if r.status_code == 200 else "image/jpeg"
        if "image" not in ct and len(r_content) < 5000:
            print(f"  \u26a0 Not an image or too small: {ct}, {len(r_content)} bytes")
            return None

        from PIL import Image
        img = Image.open(io.BytesIO(r_content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80, optimize=True)
        compressed = buf.getvalue()

        if len(compressed) < 5000:
            print(f"  \u26a0 Compressed image too small: {len(compressed)} bytes")
            return None

        print(f"  \u2713 Compressed: {len(r_content)} \u2192 {len(compressed)} bytes")

        filename = f"{slug}.jpg"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"

        requests.delete(upload_url, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY
        })

        resp = requests.post(upload_url, data=compressed, headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        }, timeout=30)

        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  \u26a0 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None

    except Exception as e:
        print(f"  \u26a0 Download/compress error: {e}")
        return None


def pick_commons(queries, min_width=900):
    for q in queries:
        commons = fetch_wikimedia_commons_images(q)
        if commons:
            pick = None
            for c in commons:
                if c["width"] >= min_width and c["original_url"].lower().endswith((".jpg", ".jpeg")):
                    pick = c
                    break
            pick = pick or commons[0]
            return pick["url"]
    return None


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  \u2713 Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ─── Article 1: GOPIO-CT 20th Anniversary ────────────────────────

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: GOPIO-CT 20th Anniversary")
    print("="*60)

    slug = "gopio-connecticut-20th-anniversary-honors-five-indian-american-leaders-charity-20260622"
    headline = "A Connecticut Diaspora Group Turned 20 by Writing Two $25,000 Checks \u2014 and Reading the Room on Immigration"
    subheadline = "GOPIO-CT marked two decades by honoring a state senator, a biotech founder, a bank CEO, an engineer and a journalist \u2014 then donated $50,000 to local charities, in a year when belonging itself was on the agenda."

    body = """For an immigrant community organization, the twentieth birthday is the one that matters. It is the point at which a chapter founded around potlucks and festival nights has either faded into nostalgia or hardened into an institution with real civic weight. The Connecticut chapter of the Global Organization of People of Indian Origin spent the evening of June 13 making clear which of those it had become.

At the Water's Edge Banquet Hall in Darien, GOPIO-CT celebrated its 20th anniversary by honoring five Indian American leaders and handing $25,000 each to two local charities \u2014 Future 5 and the Children's Learning Center of Fairfield County. The chief guest was Vishal Harsh, India's Deputy Consul General in New York, who presented the awards. The room, by the organizers' own description, was bipartisan: Connecticut state senators from both parties, an assemblyman, and a cross-section of the professionals who now make up one of the state's fastest-growing communities.

## Five Honorees, Five Sectors

The choice of honorees was itself a statement about how far the diaspora has spread across American public life. The awards went to State Senator Sujata Gadkar-Wilcox, a professor of legal studies at Quinnipiac University elected to represent the 22nd District in 2024; Dr. Anil Diwan, founder and executive chairman of the Connecticut antiviral firm NanoViricides; Nitin Mhatre, who in April became chief executive of First County Bank, a 174-year-old community institution; Hemchandra Shertukde, an engineering professor at the University of Hartford for nearly four decades; and Ajay Ghosh, a journalist whose career spans more than thirty years.

The spread \u2014 politics, biotechnology, banking, engineering, journalism \u2014 is the kind of portfolio a community uses to argue that it is woven into the fabric of a place rather than perched on top of it. "The achievements of Indian Americans have become a global benchmark," Harsh told the gathering, describing the diaspora as "a powerful testament to excellence, innovation, and global leadership."

## A Speech About Who Gets to Be American

The evening's most pointed moment came from Gadkar-Wilcox. Rather than offer the usual gratitude, she used her acceptance to make an argument about belonging at a time when immigrants \u2014 and Indians in particular \u2014 have become a recurring target of online hostility.

"Sunday family dinners have their roots in Italian culture," she said. "Similarly, when Quinnipiac University hosts a Garba dance and Diwali celebration, students from different backgrounds mark their calendars. These traditions become part of the American story because immigrants and their families are the American story." Addressing recent anti-immigrant posts on social media directly, she added: "Beyond the racism and xenophobia inherent in those comments, we have the problem of who gets to speak for the United States, who gets to say they're truly American, and who has to justify their story."

Ajay Ghosh, accepting the journalism award, struck a different but related note, warning that "journalism is facing a crisis as never before" and dedicating the honor to reporters worldwide.

## Why It Matters for the Diaspora

GOPIO-CT's arc is a useful map of what diaspora organizations become when they last. Dr. Thomas Abraham, founder president of GOPIO International, told the gathering that the Connecticut chapter had become "a model for GOPIO International in shaping the structure and activities of local chapters worldwide." The group's own framing of its evolution is telling: its mission, organizers said, has shifted "from cultural preservation to active participation in public policy, economic development, and community health initiatives."

That shift is the real story for NRIs watching from other states and other countries. The charity checks \u2014 to a youth-mentoring nonprofit and an early-childhood center, neither of them Indian organizations \u2014 signal a community spending its capital outward, on the broader town rather than only on its own. It is the move from being a guest at the table to helping set it. And in a year when the question of who counts as American is being asked loudly and often unkindly, a bipartisan banquet hall in Darien offered a quiet, well-funded answer."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Quinnipiac University")
    img_caption = "Quinnipiac University, where honoree Sujata Gadkar-Wilcox teaches legal studies; GOPIO-CT marked its 20th anniversary in Darien, Connecticut"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        img_url = pick_commons([
            "Indian American community gala banquet",
            "award ceremony banquet hall",
            "Connecticut state capitol Hartford",
            "diaspora community event"
        ])
    if not img_url:
        px = fetch_pexels_image("award ceremony gala banquet")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "An awards banquet; GOPIO-CT honored five Indian American leaders at its 20th anniversary gala"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Indian Eye \u2014 GOPIO-CT Marks 20th Anniversary, Honors Distinguished Leaders (June 19, 2026): 20th anniversary banquet at Water's Edge Banquet Hall, Darien CT on June 13, 2026; chief guest Deputy Consul General Vishal Harsh; five honorees (Sen. Sujata Gadkar-Wilcox, Dr. Anil Diwan of NanoViricides, Nitin Mhatre of First County Bank, Prof. Hemchandra Shertukde, journalist Ajay Ghosh); $25,000 each to Future 5 and Children's Learning Center of Fairfield County; quotes from Harsh, Gadkar-Wilcox, Ghosh, Dr. Thomas Abraham, President Mahesh Jhangiani",
            "GOPIO International \u2014 background on the Global Organization of People of Indian Origin, founded 1989; mission spanning civil rights, community empowerment and political participation among the worldwide Indian diaspora"
        ]),
        "diaspora_angle": "GOPIO-CT's 20-year evolution \u2014 from cultural preservation to public policy, philanthropy and civic engagement, including $50,000 in donations to non-Indian local charities \u2014 is a template for how Indian diaspora organizations across the US, UK and Canada mature into institutions, even as community leaders confront rising anti-immigrant rhetoric aimed at Indians.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 2: Documented Dreamers / America's Children Act ──────

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: Documented Dreamers / America's Children Act")
    print("="*60)

    slug = "documented-dreamers-indian-americas-children-act-aging-out-green-card-backlog-20260622"
    headline = "They Grew Up American on Paper. At 21, the Paper Runs Out \u2014 and Indians Are Most of Them."
    subheadline = "An estimated 250,000 'documented dreamers' face self-deportation when they age out of a parent's work visa. The Indian diaspora, trapped longest in the green-card backlog, is renewing its push for the America's Children Act."

    body = """Muhil Ravichandran was two years old when she arrived in the United States. She is twenty-four now, has spent almost her entire life in America, and is preparing to leave it. "Due to the green card backlog, I had aged out by the time my parents finally received their green cards," she said recently. "My future is now uncertain." Her case is not a glitch. It is exactly how the system is built to work \u2014 and it is the reason a quiet but stubborn coalition of Indian American families is back on Capitol Hill.

They are called "documented dreamers," and the name captures the cruelty of their situation. Unlike the better-known DACA recipients, these young people never crossed a border without papers. They entered legally, as the dependent children of parents on long-term work visas \u2014 H-1B, L-1, E-1, E-2. They grew up here, attended American schools, graduated from American universities. They did everything right. And precisely because they maintained legal status, they qualify for none of the protections extended to undocumented arrivals.

## The Trap at 21

The mechanism is brutally simple. A dependent child holds legal status under a parent's visa until the day they turn 21. In a functioning system, the family would have its green cards long before then. But for Indians, the employment-based green-card backlog stretches not years but decades, a queue lengthened by per-country caps that treat the world's most populous nations the same as its smallest. So the child turns 21 while the family is still waiting in line \u2014 and "ages out." At that point they must find a new visa, leave the country, or fall out of status entirely.

An estimated 250,000 children and young adults are living in the United States as dependents of long-term visa holders, and Indian families, who dominate the employment-based backlog, make up a disproportionate share. "It is time to permanently end the aging out," said Dip Patel, founder of Improve the Dream, the organization that has carried this fight for years. He has called the bill at the center of it the most bipartisan immigration measure in Congress.

## A Bill That Keeps Getting Reintroduced

That bill is the America's Children Act. Reintroduced with sponsors from both parties \u2014 including Indian American Congressmen Raja Krishnamoorthi and Ami Bera \u2014 it would do something most Americans assume the law already does: let children who were raised and educated in the United States keep their place in line. It would lock in a child's age on the date their parents filed for a green card, so that bureaucratic delay alone could not strip a young adult of the only home they have known. It would offer permanent residency to those who spent at least ten years in the country, eight of them as dependents, and graduated from an American university.

The politics are unusually favorable on paper. The measure has drawn Republican and Democratic co-sponsors in roughly equal number, a rarity for anything touching immigration. Yet it has been introduced, and reintroduced, across multiple Congresses without passing \u2014 a casualty of the broader gridlock that swallows every immigration bill regardless of merit. Each year it stalls, another cohort of documented dreamers crosses the age-21 threshold and runs out of options.

## Why It Matters for the Diaspora

For NRI families, this is the part of the American dream that the brochures leave out. A parent arrives on an H-1B, builds a career, raises children who think of themselves as American in every way that counts \u2014 and then watches those children pushed toward the exit by a backlog the family never created and cannot escape. The cost is not only personal. Economists and the bill's sponsors make the blunter argument: the United States spends years educating these young people, then hands them to global competitors at the moment they become most valuable.

The renewed push lands in an anxious season for Indian students and workers, with a separate rule poised to cap how long international students can stay. Together the two threads sketch the same uncomfortable picture \u2014 a country that recruits Indian talent aggressively, then makes its long-term welcome conditional and revocable. For the families living it, the America's Children Act is less a policy preference than a question of whether the place their children call home will let them stay in it."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("United States Capitol")
    img_caption = "The US Capitol, where backers of the America's Children Act are pressing Congress to protect 'documented dreamers' from aging out"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        img_url = pick_commons([
            "United States Capitol building Washington",
            "US Capitol dome",
            "graduation ceremony university students",
            "immigration rally Washington"
        ])
    if not img_url:
        px = fetch_pexels_image("US Capitol Washington")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "The US Capitol in Washington, focus of the documented-dreamers campaign"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "The Indian Eye \u2014 'Documented dreamers' of Indian diaspora in US face uncertain future (June 2026): estimated 250,000 documented dreamers; America's Children Act reintroduced; Muhil Ravichandran, 24, facing self-deportation after aging out due to green-card backlog; Dip Patel, founder of Improve the Dream",
            "Office of US Senator Dick Durbin \u2014 Durbin Joins Introduction of Bipartisan Bill Protecting Documented Dreamers: America's Children Act establishes age-out protections to keep dependents' place in the green-card line after their 21st birthday; Senate cosponsors include Susan Collins, Chris Coons, Kevin Cramer, John Curtis, Angus King, Amy Klobuchar, Lisa Murkowski; quote from Dip Patel",
            "Congresswoman Young Kim / American Immigration Council \u2014 America's Children Act detail: protects dependents of H-1B, L-1, E-1, E-2 workers; Indian American Congressmen Raja Krishnamoorthi and Ami Bera among reintroducers; over 250,000 affected; locks in child's age at green-card filing; permanent residency for those present 10 years (8 as dependents) who graduate from a US university; documented dreamers ineligible for DACA"
        ]),
        "diaspora_angle": "Indian families dominate the US employment-based green-card backlog, so their children make up a disproportionate share of the estimated 250,000 'documented dreamers' who age out of legal status at 21 \u2014 making the bipartisan America's Children Act one of the most direct legislative stakes for the Indian American community.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


# ─── Article 3: Indian mango season in America ───────────────────

def write_article_3():
    print("\n" + "="*60)
    print("ARTICLE 3: Indian mango season in America")
    print("="*60)

    slug = "indian-mango-season-america-diaspora-demand-kesar-alphonso-whatsapp-backlash-20260622"
    headline = "A $40 Box of Mangoes, a WhatsApp Group, and a Culture War the Diaspora Didn't Ask For"
    subheadline = "Indian mango season has become an annual ritual of longing and coordination for the diaspora \u2014 until a conservative commentator mocked it, and turned a fruit into a flashpoint over who belongs in America."

    body = """Every spring, a particular kind of message starts circulating in Indian American WhatsApp groups. A box has come in. The alphonsos are ready, or the kesars, or the Banganapallis. Names are taken, payments are Venmoed, a pickup is arranged in a suburban driveway. For a community scattered across American suburbs, the seasonal arrival of Indian mangoes is less a grocery transaction than a coordinated act of memory \u2014 a way of tasting a childhood that is eleven time zones away.

This year that ritual collided with the American culture war. The conservative commentator Sara Gonzales devoted a segment to mocking the phenomenon, questioning why Indian Americans organize WhatsApp groups to buy varieties like Banganapalli, and suggesting that enthusiasm for the fruit was an immigrant affectation rather than something "mainstream" Americans would want. The backlash was swift. Across social media, Indian-origin users accused her of trafficking in xenophobic stereotypes, and of doing it at a moment when Indian immigrants and H-1B workers are already absorbing a steady drumbeat of online hostility.

## Why a Mango Is Never Just a Mango

To understand why the remarks stung, it helps to understand what the fruit carries. The alphonso \u2014 the saffron-fleshed Maharashtrian variety long treated as the king of mangoes \u2014 has for decades been the diaspora's gold standard, the taste people fly home for. But the story this season is the rise of the kesar, the fragrant Gujarati variety that many in the community now seek out with equal devotion, alongside regional favorites like the kesar's northern cousins Dussehri, Langra and Chausa.

The economics are not casual. A single box of premium Indian mangoes can run $40 or more in the United States, a price inflated by airfreight, a mandatory irradiation treatment required for entry, and a short, unforgiving season. Buyers pay it anyway. That willingness \u2014 to spend luxury money on a perishable box of fruit \u2014 is precisely what outsiders find baffling and what insiders understand instantly. The premium is not for the mango. It is for the specific varietal memory it unlocks.

## A Trade Story Underneath the Culture Story

The mockery also flattened a real and growing trade. Indian mangoes have been gaining genuine mainstream traction: retailers including Costco have expanded their offerings of imported Indian varieties, and Indian diplomatic missions have leaned into the fruit as a tool of soft-power commerce. The Consulate General of India in Seattle has partnered with India's Agricultural and Processed Food Products Export Development Authority to host mango promotion events across the Pacific Northwest.

There are headwinds. Japan recently suspended imports of fresh Indian mangoes \u2014 a decision that, contrary to claims that the fruit posed a health risk, turned on deficiencies in fumigation and phytosanitary paperwork at certain export facilities, not contamination. For an export India is trying to scale, such stumbles matter. But the trajectory is upward, driven first by a diaspora that buys regardless of price and increasingly by curious American consumers discovering what the WhatsApp groups have known all along.

## Why It Matters for the Diaspora

For many Indian Americans, the dispute was never really about fruit. It was about the familiar exhaustion of having an intimate ritual held up for ridicule, of being told that something you love marks you as not-quite-American. Community advocates were blunt that the reaction reflected the same anxieties now swirling around skilled-worker visas and the rising visibility of Indians in business, technology and public life.

And yet the more durable signal may be the quieter one. A fruit that a generation ago could barely be found outside specialty shops now arrives by the pallet at warehouse clubs, is promoted by consulates, and is fought over on cable television precisely because it has become visible enough to fight over. The diaspora turned a seasonal craving into a supply chain, and the supply chain into a small cultural fact of American life. The mango, it turns out, made it. The argument over it is just the sound of arrival."""

    word_count = len(body.split())
    print(f"  Body word count: {word_count}")

    print("  Sourcing image...")
    img_url = pick_commons([
        "Alphonso mango India fruit",
        "Indian mangoes box market",
        "ripe mangoes basket India",
        "mango fruit display market"
    ])
    img_caption = "Boxes of Indian mangoes; alphonso and kesar varieties drive a seasonal buying ritual across the diaspora"
    img_attribution = "Wikimedia Commons"

    if not img_url:
        px = fetch_pexels_image("ripe mangoes fruit market")
        if px:
            img_url = px
            img_attribution = "Pexels"
            img_caption = "Ripe mangoes at market; Indian varieties command premium prices in the US"

    final_img_url = download_and_compress(img_url, slug) if img_url else None

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "status": "review",
        "is_editorial": False,
        "image_url": final_img_url or "",
        "image_caption": img_caption if final_img_url else "",
        "image_attribution": img_attribution if final_img_url else "",
        "sources": json.dumps([
            "American Bazaar \u2014 Indian mango row sparks diaspora backlash (June 2026): conservative commentator Sara Gonzales mocked Indian mangoes and the WhatsApp groups Indian Americans use to coordinate seasonal purchases; diaspora backlash over xenophobic stereotypes; Costco expanded Indian variety offerings; Consulate General of India Seattle partnered with APEDA on mango promotion events (Dussehri, Langra, Chausa, Banganapalli); Japan suspended fresh Indian mango imports over fumigation/phytosanitary deficiencies, not contamination",
            "The Packer / trade coverage \u2014 Demand for Indian mangoes in the US surges despite high costs (May 2026): premium Indian mango boxes around $40; kesar gaining ground alongside alphonso; airfreight and mandatory irradiation drive price; diaspora demand underpins a growing US import market"
        ]),
        "diaspora_angle": "The seasonal scramble for Indian mangoes \u2014 alphonso, kesar and regional varieties bought through WhatsApp groups at $40 a box \u2014 is one of the diaspora's most vivid rituals of homeland connection, and the backlash to a commentator mocking it shows how even food has become entangled with anxieties over Indian immigrants' place in America.",
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    return insert_article(article)


if __name__ == "__main__":
    ids = []
    ids.append(write_article_1())
    ids.append(write_article_2())
    ids.append(write_article_3())
    print("\n" + "="*60)
    print(f"DONE. Inserted IDs: {[i for i in ids if i]}")
    print("="*60)
