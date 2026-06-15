#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-15 PM batch (scheduled videshi-writer-news, 12:30 UTC run)
3 fresh articles (distinct from the 10:45 UTC and earlier batches):
  1. DGS restricts Indian seafarer deployment to Gulf conflict zones (diaspora-safety)
  2. India's GCC boom — N-able opens Bengaluru center, 2.36M GCC workforce (tech/economy)
  3. US embassy assures Indian students more visa appointments amid opening-day rush (immigration)
"""

import json, os, subprocess, re, time, datetime, urllib.parse, requests

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                key = key.strip().replace('export ', '')
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}


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
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=8):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers=UA, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                width = ii.get("width", 0)
                if url and "image" in mime and width > 300:
                    results.append({"url": url, "title": page.get("title", ""),
                                    "width": width, "height": ii.get("height", 0)})
            print(f"  \u2713 Wikimedia Commons: {len(results)} results for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        print("  \u26a0 No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape"],
            capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        for photo in data.get("photos", []):
            url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
            if url:
                print(f"  \u2713 Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error: {e}")
    return None


def validate_image(url):
    try:
        r = requests.get(url, timeout=12, stream=True, allow_redirects=True, headers=UA)
        ct = r.headers.get("Content-Type", "")
        chunk = r.raw.read(12000)
        if r.status_code == 200 and "image" in ct and len(chunk) > 5000:
            print(f"  \u2713 Image validated: {r.status_code}, {ct}, {len(chunk)}+ bytes")
            return True
        print(f"  \u2717 Image validation failed: {r.status_code}, {ct}, {len(chunk)} bytes")
    except Exception as e:
        print(f"  \u2717 Image validation error: {e}")
    return False


def pick_commons_image(query, keywords, caption):
    for img in fetch_wikimedia_commons_images(query, 8):
        tl = img["title"].lower()
        if any(kw in tl for kw in keywords) and validate_image(img["url"]):
            return img["url"], caption, "Wikimedia Commons"
    return None, "", ""


def insert_article(article):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=20)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  \u2713 Inserted: {result[0].get('slug', 'unknown')}")
            return True
        print("  \u2713 Inserted (no body returned)")
        return True
    print(f"  \u2717 Insert failed: {r.status_code} \u2014 {r.text[:300]}")
    return False


def finalize(article, image_url, image_caption, image_attribution):
    if image_url:
        article["image_url"] = image_url
        article["image_caption"] = image_caption
        article["image_attribution"] = image_attribution
    else:
        print("  \u26a0 No valid image found \u2014 inserting without image")
    return insert_article(article)


# ========================================================================
# ARTICLE 1: DGS restricts seafarer deployment to Gulf
# ========================================================================
def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: DGS restricts seafarer deployment to Gulf")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Strait of Hormuz oil tanker", ["tanker", "hormuz", "oil", "ship", "strait"],
        "An oil tanker in the Strait of Hormuz, where multiple Indian-crewed vessels have come under attack")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "oil tanker Gulf of Oman", ["tanker", "oman", "gulf", "ship", "vessel"],
            "A commercial tanker in the Gulf of Oman, the waters where the MT Settebello was struck")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "merchant ship seafarer", ["ship", "merchant", "vessel", "cargo", "tanker"],
            "A merchant vessel; India has restricted seafarer deployment to Gulf conflict zones")
    if not image_url:
        px = fetch_pexels_image("oil tanker ship ocean")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "An oil tanker at sea", "Pexels"

    slug = "india-dgs-restricts-seafarer-deployment-gulf-conflict-zones-settebello-20260615"

    body = """India crews the world's ships. Indian seafarers make up roughly 12 per cent of the global maritime workforce \u2014 more than 250,000 sailors who keep oil, gas and cargo moving across the planet's most dangerous waters. This week, for the first time in the current Gulf crisis, New Delhi told them to stop sailing into the line of fire.

The Directorate General of Shipping (DGS) has advised all shipping companies and maritime recruitment agencies to restrict the deployment of Indian seafarers to conflict areas "until further orders." The directive, issued in a security circular over the weekend, came days after three Indian seafarers aboard the Palau-flagged tanker MT Settebello were killed in a US military strike off the coast of Oman on June 10.

## A Deadly Week at Sea

The Settebello was not an isolated incident. In the span of a single week, three vessels carrying Indian crews came under attack as they tried to navigate \u2014 or bypass \u2014 the US-imposed blockade on shipping bound for Iran. The MT Marivex, also Palau-flagged with 24 Indian crew members aboard, was disabled by an F/A-18 Super Hornet from the USS Abraham Lincoln after the crew failed to comply with US directions; a fire broke out but all aboard survived. A third vessel, the MV Jalveer, was likewise affected.

The US blockade of Iranian ports began in April after Tehran sharply curtailed shipping through the Strait of Hormuz, the chokepoint that once carried a fifth of the world's oil and liquefied natural gas. Washington's Central Command insists the restrictions apply only to vessels going to or from Iran, not those transiting the strait to other destinations. But the practical effect has been a war zone for the merchant mariners who crew these tankers \u2014 a disproportionate number of them Indian.

According to the International Maritime Organisation, there have been 46 attacks in and around the Strait of Hormuz since February 28, resulting in 14 casualties. IMO Secretary General Arsenio Dominguez condemned the attacks as "simply unacceptable."

## What the Circular Says

The DGS directive is unambiguous in intent but careful in its carve-outs. "This Directorate further reiterates that all RPSL companies and shipping companies (maritime recruitment and placement agencies) are advised to restrict deployment or send Indian seafarers to conflict areas until further orders," the circular states. "However, companies may carry out crew change in emergency situations with the consent of crew members."

Masters of vessels operating in or transiting the Gulf region \u2014 including the Strait of Hormuz and adjoining waters \u2014 have been told to maintain heightened security awareness, monitor navigational warnings, and implement all applicable ship and company security procedures. The Ministry of Ports, Shipping and Waterways issued a parallel advisory urging "the highest degree of vigilance and caution while operating in the conflict zone."

The DGS said it is monitoring the situation in coordination with the shipping ministry, the Ministry of External Affairs, the Indian Navy and Indian missions abroad.

## A Government Under Pressure

The restriction follows mounting public anger. After the Settebello deaths, India took the rare step of lodging a second formal protest with the United States, summoning the US charg\u00e9 d'affaires to convey "deep concern over the use of lethal and deadly force against civilian shipping." For the families of the dead, protests have not been enough. Sushila Devi, widow of Shivanand Chaurasia \u2014 the sole earner for his family of four \u2014 told reporters from her home in Deoria: "If he had told us about the dangers, I would have called him back. The government should not allow people to go there."

That sentiment has driven calls on Prime Minister Narendra Modi to go beyond diplomatic protests. The deployment restriction is the government's most concrete operational response yet, though it stops short of a full ban and leaves emergency crew changes to the discretion of the companies and the consent of the sailors themselves.

## Why It Matters to the Diaspora

For the Indian diaspora, the seafaring workforce is family in the most literal sense. These are men \u2014 overwhelmingly from coastal and northern Indian towns \u2014 whose remittances sustain entire households. The maritime sector is one of the largest and least visible pillars of India's overseas labour economy, and the Gulf is its most heavily trafficked corridor.

The restriction also raises a harder question that NRI maritime families have been asking for weeks: who protects the workers when the world's shipping lanes become battlegrounds? With the blockade showing no sign of lifting and the Iran conflict grinding into its fourth month, the DGS advisory may be the first of many measures \u2014 and the seafarers caught between a blockade and a paycheck are left waiting for clarity.

**Sources:** The Hindu BusinessLine, Reuters, Press Trust of India / IANS, Ministry of Ports Shipping and Waterways advisory, International Maritime Organisation"""

    article = {
        "headline": "India Tells Its Sailors to Stop Going Into the Gulf. Three Were Just Killed There.",
        "subheadline": "After the MT Settebello strike off Oman, the Directorate General of Shipping has restricted Indian seafarer deployment to conflict zones \u2014 a rare operational step as families demand more than protests.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-safety",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Indian seafarers make up ~12% of the global maritime workforce; their remittances sustain coastal and northern Indian households, and the Gulf is their most-trafficked and now most-dangerous corridor.",
        "sources": ["The Hindu BusinessLine", "Reuters", "Press Trust of India / IANS", "Ministry of Ports, Shipping and Waterways", "International Maritime Organisation"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 2: India GCC boom
# ========================================================================
def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: India GCC boom")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Bengaluru IT park", ["bengaluru", "bangalore", "tech", "park", "it", "office"],
        "Bengaluru, India's premier technology hub and the centre of its GCC boom")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Bangalore skyline", ["bangalore", "bengaluru", "skyline", "city", "building"],
            "The Bengaluru skyline, home to hundreds of global capability centres")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "office building India technology", ["office", "building", "india", "tech", "tower"],
            "An office tower in India's technology sector")
    if not image_url:
        px = fetch_pexels_image("modern office building bangalore tech park")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "A modern technology office campus", "Pexels"

    slug = "india-gcc-boom-bengaluru-n-able-2-36-million-workforce-2026-20260615"

    body = """While Washington fights over H-1B fees and India's IT giants warn of shrinking visa allotments, a quieter and far larger shift is reshaping where global technology work actually happens. It is not moving to America. It is staying in India \u2014 and the rest of the world is coming to it.

The latest data point arrived on Monday, when US cybersecurity firm N-able opened a Global Capability Center (GCC) in Bengaluru and announced plans to expand its India workforce by at least 50 per cent before the end of 2026. The center, which already employs more than 100 people, is a small piece of a very large trend. India's total GCC workforce is projected to reach 2.36 million employees by the end of 2026, according to a report from industry body Nasscom and consultancy Zinnov, with artificial intelligence and cybersecurity driving much of the demand.

## What a GCC Actually Is \u2014 and Why It Matters

A Global Capability Center is an offshore hub that a multinational company owns and operates directly, rather than outsourcing work to a third-party vendor. The distinction is crucial. The old model sent India low-end, cost-driven contract work \u2014 call centers, basic coding, back-office processing. The GCC model embeds core engineering, research, product design and high-end functions inside the company itself.

N-able's CEO John Pagliuca made the shift explicit. "The reason we're in Bengaluru is capability," he told Reuters. "Our priority is to build for the long term, with the right people and a strong foundation, not to pursue a short-term headcount play." He stressed that the move was driven by access to talent, not cost reduction \u2014 a sentence that would have been almost unimaginable from a Western tech executive a decade ago.

The skills N-able is hunting for tell the story: AI engineering, applied machine learning, cloud security and threat research. These are among the hardest roles to fill anywhere in the world, and India is now where companies expect to find them.

## The AI and Cybersecurity Engine

The timing is not coincidental. As cybercriminals increasingly weaponise generative AI to launch sophisticated, automated attacks, the demand for defensive AI capability has exploded. Pagliuca said the Bengaluru team will play a central role in developing automated threat detection, monitoring and faster response systems \u2014 the kind of frontier work that GCCs were once assumed to keep at headquarters.

That said, Bengaluru is no longer a buyer's market for employers. The competition for AI and cybersecurity professionals is fierce, with multinationals and homegrown technology firms chasing the same limited pool of talent. To attract top candidates, N-able said it is offering competitive packages and the chance to drive global innovation while building local career paths \u2014 a recognition that Indian engineers now have leverage they did not have before.

## A Counterweight to the Visa Squeeze

For the diaspora, the GCC boom carries a layered significance. On one hand, it represents opportunity coming home: high-value, globally connected careers that no longer require relocating to the United States or the United Kingdom. As American immigration policy grows more hostile \u2014 H-1B fee hikes, green-card backlogs stretching decades, and an EB-5 investor visa pipeline that has run dry for Indians \u2014 the GCC offers an alternative path to working for a global company without leaving India.

On the other hand, it reflects a structural rebalancing of the tech economy that the diaspora has long anticipated. The generation of Indian engineers who emigrated in the 1990s and 2000s did so because the best work was abroad. Their children and the engineers behind them increasingly find that the best work is at home \u2014 inside the Bengaluru, Hyderabad and Pune campuses of the same multinationals that once only hired in California.

The 2.36 million figure is worth sitting with. It is larger than the entire population of many countries, and it represents a concentration of global technology talent on Indian soil that has no historical precedent. For NRIs weighing whether to return, for parents advising children on careers, and for anyone tracking where the center of gravity in global tech is heading, the answer is increasingly clear. It is moving east.

**Sources:** Reuters, Nasscom\u2013Zinnov GCC report 2026, N-able Inc. statements"""

    article = {
        "headline": "The World's Tech Giants Are Building in Bengaluru, Not Hiring in California. India's GCC Workforce Is Headed for 2.36 Million.",
        "subheadline": "As US visa policy tightens, multinationals are pouring high-end AI and cybersecurity work into India-based capability centres. N-able's new Bengaluru hub is the latest sign of where global tech is moving.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "As H-1B fees rise and green-card backlogs stretch decades, GCCs let Indian engineers build global careers without emigrating \u2014 reshaping the calculus NRIs and their families make about returning home.",
        "sources": ["Reuters", "Nasscom\u2013Zinnov GCC report 2026", "N-able Inc."],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 3: US embassy assures Indian students more visa slots
# ========================================================================
def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: US embassy assures Indian students more visa slots")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Embassy of the United States New Delhi", ["embassy", "united states", "new delhi", "consulate"],
        "The US Embassy in New Delhi, which reopened student visa appointment scheduling this week")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "United States passport visa", ["visa", "passport", "united states", "document"],
            "A US visa; Indian students are the largest group of international students in the US")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "university campus students", ["university", "campus", "students", "college"],
            "A US university campus")
    if not image_url:
        px = fetch_pexels_image("university campus students graduation")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "International students on a university campus", "Pexels"

    slug = "us-embassy-india-assures-more-student-visa-appointments-opening-day-rush-20260615"

    body = """For tens of thousands of Indian students with US college admissions in hand, the past two days have been an exercise in refreshing a webpage and praying. When the US Embassy in India reopened student visa appointment scheduling on June 14, demand was so intense that the portal buckled \u2014 and applicants were left staring at error messages with their August enrolment dates ticking closer.

On Tuesday, the embassy moved to calm the panic. "Since June 14, thousands of students have secured visa appointments for July and August," the US Embassy in India posted on social media. "Thousands of appointments remain available and we will open thousands more in the coming weeks. We appreciate your patience as we diligently work to resolve the technical issues you have encountered."

## A Familiar Scramble

The chaos was predictable. Indian students remain the single largest group of international students in the United States, and in recent years more than 140,000 F-1 student visas have been issued to Indians annually. That volume routinely overwhelms the appointment system at the US consulates in New Delhi, Mumbai, Hyderabad, Chennai and Kolkata, especially during the April-to-June crush for Fall intake.

This year the pressure was compounded by a suspension earlier in the visa cycle, which left a backlog of applicants all competing for slots the moment scheduling reopened. On Monday, as students rushed the portal, the embassy pleaded for restraint: "We are aware of the high demand for student visa appointments. Please remember, do not refresh too often, as you may be locked out of your account. Appointments remain available at all posts, and we will continue to add appointments as conditions allow."

The technical glitches \u2014 locked accounts, frozen pages, vanishing slots \u2014 turned what should have been a routine booking into a high-stakes lottery for students who have already paid tuition, secured housing and, in many cases, booked flights.

## The Stakes Are Brutally High

The financial exposure for a student who cannot get a visa in time is severe. Industry advisers have estimated potential losses ranging from \u20b912 to \u20b935 lakh \u2014 covering tuition deposits, housing payments and airfare \u2014 if a student misses their start date and the university refuses to defer enrolment. For middle-class Indian families who have often borrowed heavily to fund a US education, a missed appointment is not an inconvenience. It can be financially ruinous.

Adding to the anxiety is the rise of 221(g) administrative processing notices, which place visa approvals on indefinite hold even after a successful interview. Students who clear the appointment hurdle can still find themselves trapped in a bureaucratic limbo with no clear timeline.

## New Layers of Scrutiny

The reopening also comes with strings attached. US consulates are now conducting mandatory reviews of the online presence and social media accounts of student visa applicants \u2014 a vetting standard introduced during the current administration's broader tightening of immigration screening. The travel ban affecting nationals from several countries also remains in effect, though students holding valid US student visas are exempt.

Applicants are advised to have their files airtight before booking: the Form I-20 from a SEVP-approved school, the $350 SEVIS I-901 fee receipt, and the DS-160 confirmation page. Students can apply up to 120 days before their program start date, and advisers are urging anyone with a Fall 2026 start to grab any available slot immediately rather than waiting for a more convenient date.

## Why the Diaspora Is Watching

For the Indian diaspora, the student visa pipeline is the lifeblood of the community's growth in the United States. Today's F-1 applicants are tomorrow's H-1B workers, green-card holders and citizens \u2014 the next generation of the Indian-American story. Every disruption to that pipeline ripples through families on both sides of the ocean: parents in India financing the dream, relatives in America preparing to host arrivals, and universities counting on the tuition.

The embassy's assurance of "thousands more" appointments is welcome, but it does not erase the uncertainty. For a student whose course begins on August 20 and whose visa slot is still a refresh-and-pray gamble, a promise of more openings "in the coming weeks" is reassurance with an asterisk. The advice from those who have navigated this before is simple and unsentimental: book the first slot you can get, and keep your documents ready.

**Sources:** ANI / India Tribune, US Embassy India official statements, VisaVerge F-1 appointment guide, Livemint / Business Standard"""

    article = {
        "headline": "Indian Students Crashed the US Visa Portal on Day One. The Embassy Says Thousands More Slots Are Coming.",
        "subheadline": "After the June 14 reopening triggered a frantic rush and technical glitches, the US Embassy in India assured applicants that more appointments for July and August will open in the coming weeks.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Indian students are the largest group of international students in the US and the front of the diaspora pipeline \u2014 today's F-1 applicants become tomorrow's H-1B workers, green-card holders and citizens.",
        "sources": ["ANI / India Tribune", "US Embassy India", "VisaVerge", "Livemint / Business Standard"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# MAIN
# ========================================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"VIDESHI NEWS WRITER (PM2) \u2014 {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")

    results = []
    results.append(("Seafarer Gulf restriction", write_article_1()))
    results.append(("India GCC boom", write_article_2()))
    results.append(("US student visa slots", write_article_3()))

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        print(f"  {'\u2713 SUCCESS' if success else '\u2717 FAILED'}: {name}")
    print(f"{'='*60}\n")
