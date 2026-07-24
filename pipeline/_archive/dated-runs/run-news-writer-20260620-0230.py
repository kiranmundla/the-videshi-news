#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-20 02:30 UTC run (scheduled videshi-writer-news)
3 fresh articles distinct from all 2026-06-18/19/20 published news topics
(monsoon, $100K H-1B fee, India-US trade deal, IT-stock crash, Jio/NSE IPO,
GIFT City dollars, foreigner registration rules, India-Canada CEPA, RBI NRI
deposits, AAPI physician fee, Hormuz reopening, UAE consular operator, fuel
losses, PM-VBRY, OCI overhaul, Mumbai water, defence production, rupee,
remittances, Yoga Day, US student collapse, anti-Hindu hate, Anil Menon,
men's World Cup PIO players, DHS duration-of-status, VivaTech, Iran war,
UK-India clean energy, Warsh Fed, Modi Paris, EU-India FTA, Carnegie reverse
brain drain, women's T20 WC, NY Independence Day resolution):

  1. The dark side of the H-1B dream — a Telugu worker's labor-trafficking
     lawsuit exposes the "pay-to-stay" exploitation underneath the visa
  2. America's tech jobs are quietly moving to Bengaluru — US firms open
     Global Capability Centers as the GCC workforce nears 2.4 million
  3. "Vetting never stops" — the US Embassy warns Indian visa holders that
     screening continues even after a visa is granted
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
load_env(os.path.expanduser('~/workspace/.env.pexels'))

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
                if url and "image" in mime and width > 300 and not url.lower().endswith(".svg"):
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
        r = requests.get(url, timeout=15, stream=True, allow_redirects=True, headers=UA)
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


def wc(body):
    return len(re.sub(r'[#*>\n]', ' ', body).split())


def finalize(article, image_url, image_caption, image_attribution):
    if image_url:
        article["image_url"] = image_url
        article["image_caption"] = image_caption
        article["image_attribution"] = image_attribution
    else:
        print("  \u26a0 No valid image found \u2014 inserting without image")
    article["word_count"] = wc(article["body"])
    print(f"  word_count={article['word_count']}")
    return insert_article(article)


# ========================================================================
# ARTICLE 1: H-1B labor trafficking lawsuit — the "pay-to-stay" underside
# ========================================================================
def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: H-1B labor trafficking lawsuit")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "United States federal courthouse building",
        ["courthouse", "federal", "court"],
        "A US federal courthouse; an Indian H-1B worker's labor-trafficking suit moves through the courts")
    if not image_url:
        image_url, image_attribution = fetch_pexels_image("courthouse justice law"), "Pexels"
        if image_url and validate_image(image_url):
            image_caption = "A courthouse; an H-1B worker has filed a labor-trafficking lawsuit against his employer"
        else:
            image_url = None

    slug = "h1b-labor-trafficking-lawsuit-telugu-worker-pay-to-stay-michigan-green-card-20260620"

    body = """The H-1B visa has long been sold as a ladder: a job offer, a work permit, and somewhere up the rungs, a green card and citizenship. A lawsuit now winding through a Michigan federal court describes what happens when the ladder is turned into a trap \u2014 and it points to an exploitation that rarely makes headlines, carried out not by faceless corporations but, in this case, within the Indian-American community itself.

According to a complaint filed by the Banias Law firm, an Indian H-1B contract worker says he paid his employer close to $100,000 over several years simply to keep the job that anchored his path to permanent residency. The plaintiff and the defendants are both of Indian origin, part of the same Telugu community \u2014 a detail that has made the case especially uncomfortable reading for a diaspora that prides itself on mutual uplift.

## The Mechanics of a Trap

The arrangement, as alleged, was a textbook case of what immigration lawyers call "pay-to-stay." The plaintiff was hired by a private company, kept on the payroll to satisfy H-1B regulations, and successfully sponsored for the visa. For a time, the system worked as advertised. Then, the suit claims, the demands began.

The defendants allegedly started requiring the worker to effectively fund his own salary \u2014 paying money back to his employer \u2014 while refusing to provide pay stubs. That refusal was not incidental. For an H-1B holder, pay stubs are the documentary lifeline needed to transfer to a new sponsoring employer; without them, the worker is frozen in place, unable to leave without jeopardizing his status. The complaint alleges the employer withheld those documents unless the plaintiff kept paying.

When the worker pushed back, the suit says, the response escalated from financial pressure to threats: warnings that he would be reported to Immigration and Customs Enforcement, and threats reaching as far as his father back in India. The complaint frames these acts \u2014 forcing a person to pay for his own employment, withholding documents to prevent escape, and threatening deportation \u2014 as labor trafficking, forced labor and document withholding, all of them crimes under US law.

## Why the Visa Makes Exploitation Possible

The case is a single lawsuit, and its allegations remain to be tested in court. But immigration advocates have long warned that the structure of the H-1B visa itself creates the conditions for this kind of abuse. Because the visa is tied to a specific employer, the sponsor holds enormous leverage over a worker whose entire future \u2014 his job, his family's stability, his green-card timeline \u2014 depends on staying in the employer's good graces. For Indians, who account for the overwhelming majority of H-1B holders and face green-card backlogs stretching decades, that leverage is magnified. The longer the wait, the more a worker has to lose by walking away.

That imbalance has produced a shadow economy of "benching" without pay, inflated training fees, and side payments that the formal system is poorly equipped to police. Reports of small staffing firms \u2014 some run by earlier immigrants who navigated the same system \u2014 squeezing newer arrivals have circulated for years, usually in whispers rather than courtrooms.

## A Painful Mirror for the Diaspora

What makes this case resonate is that it cuts against the diaspora's preferred story about itself. The Indian-American community is routinely celebrated \u2014 by its own organizations and by Indian and American leaders alike \u2014 as a model of professional excellence and solidarity. A lawsuit alleging that one Indian immigrant trafficked another, exploiting shared community ties to do it, complicates that narrative in ways that are hard to look away from.

It also lands at a charged moment. The H-1B program is already under political siege, with a revived $100,000 fee, proposed legislation to scrap the lottery, and rhetoric on all sides about fraud and abuse. Cases like this one risk being weaponized by those who want to dismantle the program entirely \u2014 even as advocates argue the real lesson is the opposite: that the visa needs reform to protect workers, not abolition that would punish them.

## Why It Matters to the Diaspora

For the hundreds of thousands of Indians on H-1B visas, the lawsuit is a reminder of how precarious "the American dream" can be when it hangs on a single employer's signature. It is a warning to newer arrivals to document everything, know their rights, and treat demands for side payments or withheld pay stubs as red flags rather than the cost of doing business. And it is a challenge to the community's advocacy groups, which have rallied energetically against the $100,000 fee, to turn the same energy toward the quieter exploitation happening within. The dream is real for millions \u2014 but this case is a sobering account of what the system allows when no one is watching.

**Sources:** Tupaki, Banias Law firm complaint, The Daily Caller, The Indian Eye"""

    article = {
        "headline": "An H-1B Worker Says He Paid $100,000 to Keep His Job. His Lawsuit Exposes the Visa's Dark Side.",
        "subheadline": "A Telugu contract worker's labor-trafficking suit in Michigan alleges 'pay-to-stay' exploitation, withheld pay stubs and threats of ICE \u2014 a painful mirror for a diaspora that celebrates its own success.",
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Because the H-1B visa is tied to one employer and Indians face decades-long green-card backlogs, the sponsor holds outsized power \u2014 and this lawsuit shows how that power can curdle into forced labor, a warning to the hundreds of thousands of Indians whose American future hangs on a single signature.",
        "sources": ["Tupaki", "Banias Law firm", "The Daily Caller", "The Indian Eye"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 2: India's GCC boom — US tech jobs moving to Bengaluru
# ========================================================================
def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: India GCC boom / US firms in Bengaluru")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Bengaluru technology park office building India",
        ["itpl", "tech", "park", "bangalore", "bengaluru", "office", "sigma"],
        "A technology park in Bengaluru, the centre of India's booming Global Capability Center industry")
    if not image_url:
        image_url, image_attribution = fetch_pexels_image("modern office building technology campus"), "Pexels"
        if image_url and validate_image(image_url):
            image_caption = "A modern technology campus; India's GCC workforce is set to near 2.4 million by end-2026"
        else:
            image_url = None

    slug = "india-gcc-boom-us-firms-bengaluru-global-capability-centers-2-4-million-workforce-20260620"

    body = """While Washington argues over how to keep skilled Indians out of America, American companies are quietly moving in the opposite direction \u2014 setting up shop in India and hiring Indian talent by the thousands, on Indian soil. The latest example arrived this week in Bengaluru, and it captures a structural shift in the global technology economy that the H-1B debate often obscures.

US cybersecurity firm N-able, which provides IT management and data-protection software to more than 500,000 organizations worldwide, opened a Global Capability Center (GCC) in Bengaluru and announced plans to expand its India workforce by at least 50 percent by the end of 2026. The center already employs more than 100 people. Crucially, CEO John Pagliuca said the move was driven primarily by access to talent, not cost-cutting. "The reason we're in Bengaluru is capability," he told Reuters. "Our priority is to build for the long term, with the right people and a strong foundation, not to pursue a short-term headcount play."

## A Workforce Approaching the Size of a Major City

N-able is a single data point in a much larger wave. India's GCC workforce is projected to reach 2.36 million employees by the end of 2026, according to a report from industry body Nasscom and consultancy Zinnov, with artificial intelligence and cybersecurity driving much of the demand. These are not the back-office call centers of the 2000s. Today's GCCs are doing frontier work \u2014 AI engineering, applied machine learning, cloud security and threat research \u2014 the very high-end roles that the H-1B program was designed to bring into the United States.

The skills Pagliuca named as hardest to source \u2014 AI engineering, cloud security, threat research \u2014 are precisely the ones in shortest supply globally. That India can now supply them in volume, at scale, and inside its own borders is rewriting the logic of where innovation happens. The Bengaluru team, Pagliuca said, will play a key role in developing defensive AI capabilities, including automated threat detection and faster response times, as cybercriminals increasingly weaponize generative AI.

## The Mirror Image of the Visa Fight

The timing is hard to ignore. As the US tightens the H-1B route \u2014 with a revived $100,000 fee, proposed bills to scrap the lottery, and longer visa-vetting \u2014 the practical effect may be less to keep jobs in America than to accelerate their migration to India. If a company cannot easily bring an Indian engineer to Texas, it can open an office in Bengaluru and hire ten. The work gets done; it simply gets done somewhere else.

For India, this is the optimistic flip side of the "reverse brain drain" story. The same forces nudging some Indian Americans to consider leaving the US are also pulling global capital and high-value jobs toward India's metros. Bengaluru, Hyderabad and Pune are absorbing returning talent and creating roles that did not exist a decade ago. The country is increasingly not just exporting workers but importing the work itself.

## A Contested Market, Not a Free Lunch

The boom is real but not frictionless. Bengaluru's market for AI and cybersecurity professionals is fiercely contested, with multinationals and homegrown firms chasing the same scarce talent. Salaries for top engineers have climbed sharply, attrition is high, and the easy cost advantage that first drew companies to India has narrowed considerably. Firms now compete on the quality of work and the chance to drive global innovation, not merely on cheaper labor \u2014 a sign of how far the sector has matured.

There are strategic questions, too. As more of the world's critical software and security work concentrates in a handful of Indian cities, questions of infrastructure, talent pipelines and resilience grow more pressing. India's challenge is no longer attracting GCCs \u2014 it is sustaining the talent depth to keep them growing.

## Why It Matters to the Diaspora

For the Indian diaspora, the GCC boom reframes the entire migration conversation. For decades, ambition meant leaving \u2014 boarding a flight to a US campus or a Silicon Valley cubicle. Increasingly, the cutting-edge job is available in Bengaluru or Hyderabad, working for the same American company, without the visa lottery, the green-card backlog, or the question of belonging. For NRIs weighing a return, it means a homecoming no longer has to be a career sacrifice. And for the next generation of Indian engineers, it signals that the center of gravity in global technology is shifting eastward \u2014 and that the most consequential work of their careers may well happen at home.

**Sources:** Reuters, Nasscom, Zinnov, The Economic Times"""

    article = {
        "headline": "America's Tech Jobs Are Quietly Moving to Bengaluru. India's 'Capability Center' Workforce Is Nearing 2.4 Million.",
        "subheadline": "As Washington tightens the H-1B route, US firms like N-able are opening Global Capability Centers in India and hiring frontier AI and cybersecurity talent on Indian soil \u2014 the mirror image of the visa fight.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "The GCC boom rewrites the migration calculus for the diaspora: the cutting-edge job for an American company is increasingly available in Bengaluru or Hyderabad, without the visa lottery or green-card backlog \u2014 meaning a homecoming no longer has to be a career sacrifice.",
        "sources": ["Reuters", "Nasscom", "Zinnov", "The Economic Times"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 3: US Embassy warns visa vetting never stops
# ========================================================================
def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: US Embassy continuous visa vetting warning")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Embassy of the United States New Delhi",
        ["embassy", "delhi"],
        "The US Embassy in New Delhi, which has warned that visa screening continues even after a visa is granted")
    if not image_url:
        image_url = fetch_wikipedia_person_image("Embassy of the United States, New Delhi")
        if image_url and validate_image(image_url):
            image_caption = "The US Embassy in New Delhi"
            image_attribution = "Wikimedia Commons"
        else:
            image_url, image_attribution = fetch_pexels_image("passport visa document airport"), "Pexels"
            if image_url and validate_image(image_url):
                image_caption = "A passport and visa documents; US screening continues even after a visa is issued"
            else:
                image_url = None

    slug = "us-embassy-india-warns-visa-screening-continues-after-granted-vetting-never-stops-20260620"

    body = """For most travelers, the moment the visa sticker lands in the passport feels like the finish line \u2014 the vetting done, the approval secured. The US Embassy in India has just told Indian visa holders to think again. In a public advisory, the mission warned that screening and vetting continue even after a visa has been granted, a message that has landed heavily on a community that sends more applicants to US consulates than almost any other.

"We use all available information in our visa screening and vetting to identify visa applicants who are inadmissible to the United States, including those who pose a threat to U.S. national security," the embassy said. The key phrase, immigration lawyers noted, is that this process does not end at issuance. A visa, in the government's framing, is a continuously reviewed privilege \u2014 one that can be revoked if new information surfaces at any point before or after travel.

## What "Continuous Vetting" Means in Practice

The advisory formalizes a posture that has been tightening for months. Under continuous vetting, US authorities can re-examine a visa holder's record \u2014 including social-media activity, travel history and any new derogatory information \u2014 well after the interview is over. If something raises a flag, the visa can be cancelled, sometimes without the holder learning of it until they attempt to board a flight or pass through a port of entry.

The embassy paired the warning with a reminder about the breadth of information it draws on, signaling that applicants' digital footprints remain relevant long after they have answered the consular officer's questions. For a generation of Indian students and professionals who live much of their lives online, that is a consequential shift in how the relationship with the US government works: the file never fully closes.

## India Is Not on the Ban List \u2014 But the Mood Is Cautious

The warning arrives against a noisy backdrop. Washington has rolled out a sweeping travel ban barring nationals of 12 countries outright and partially restricting seven others, most of them in the Middle East and Africa. India, importantly, is not on either list. The US continues to process Indian applications across all categories \u2014 B1/B2 tourist, H-1B work and F1 student visas \u2014 and has assured students that thousands of appointment slots remain available for the July and August intake.

But reassurance and unease are coexisting uncomfortably. Indian applicants still face interview backlogs stretching 10 to 12 months at many consulates, a rise in 221(g) administrative-processing notices that put approvals on indefinite hold, and now an explicit reminder that even an approved visa is not a settled matter. For families who have paid tuition, booked flights and signed housing leases, the message reads less as routine policy and more as a caution to keep their heads down.

## A Chilling Effect on Everyday Life

The practical anxiety is not abstract. A recent survey of Indian Americans found a sizable share now avoid posting about politics online, hesitate to leave and re-enter the country, or decline to display political signs \u2014 behaviors researchers attribute to a fear of drawing official scrutiny. An advisory confirming that vetting is continuous and that "all available information" is in play is likely to deepen that caution, particularly among students and temporary workers whose status is most fragile.

Immigration attorneys advise visa holders to keep documentation current, avoid any appearance of status violations, and treat their online presence with the same care they would a consular interview. The guidance is not new \u2014 but the embassy's decision to say it out loud changes the temperature.

## Why It Matters to the Diaspora

For the Indian diaspora, the warning is a reminder that the visa is a beginning, not an end. Hundreds of thousands of Indians enter the US each year on student, work and visitor visas, and the message from the embassy reframes that status as provisional in a way many had not fully internalized. It raises the stakes on everything from social-media posts to international travel, and it adds a layer of permanent low-grade vigilance to lives already navigating backlogs and policy whiplash. The American door remains open to Indians \u2014 but the embassy has made clear that what lies beyond it is a corridor still being watched.

**Sources:** The Indian Eye, India Tribune, US Embassy New Delhi advisory, Carnegie Endowment for International Peace"""

    article = {
        "headline": "The US Embassy Just Told Indian Visa Holders: The Vetting Never Stops \u2014 Even After You're Approved",
        "subheadline": "A new advisory warns that screening continues after a visa is granted and that 'all available information' stays in play \u2014 deepening unease for a community already facing backlogs and 221(g) holds.",
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "For the hundreds of thousands of Indians who enter the US each year on student, work and visitor visas, the embassy's warning reframes an approved visa as a continuously reviewed privilege \u2014 raising the stakes on social-media posts, travel and everyday life.",
        "sources": ["The Indian Eye", "India Tribune", "US Embassy New Delhi", "Carnegie Endowment for International Peace"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# MAIN
# ========================================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"VIDESHI NEWS WRITER \u2014 {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")

    results = []
    results.append(("H-1B labor trafficking lawsuit", write_article_1()))
    results.append(("India GCC boom / US firms Bengaluru", write_article_2()))
    results.append(("US Embassy continuous visa vetting", write_article_3()))

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        print(f"  {'\u2713 SUCCESS' if success else '\u2717 FAILED'}: {name}")
    print(f"{'='*60}\n")
