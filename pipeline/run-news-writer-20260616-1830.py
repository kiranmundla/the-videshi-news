#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-16 18:30 UTC run (scheduled videshi-writer-news)
3 fresh articles, distinct from all 2026-06-15/16 published topics (H-1B fee ruling,
trade deal tranche, domestic renewal pilot, Iran ceasefire, oil/markets rally, Modi-
Trump meet, Canada deportations, birth tourism, NRI deposit rates, ultra-rich exodus,
Modi-Slovakia, Rubio racism remarks):
  1. DoJ denaturalization wave reaches Indian-origin citizens (Neeraj Sharma / H-1B
     fraud); 100-200 referrals/month in FY2026 — diaspora-rights
  2. Bangladesh-India diplomatic row: PM adviser Zahed Ur Rahman stopped at Delhi
     airport during IORA meet — geopolitics
  3. India's GCC boom: N-able opens Bengaluru center, workforce to hit 2.36M by
     end-2026 — tech/economy
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
# ARTICLE 1: DoJ denaturalization wave reaches Indian-origin citizens
# ========================================================================
def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: Denaturalization wave reaches Indian-origin citizens")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "United States Department of Justice building Washington",
        ["department of justice", "justice", "robert f. kennedy", "doj", "main justice"],
        "The U.S. Department of Justice in Washington, which has filed a fresh wave of denaturalization cases")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "United States naturalization certificate citizenship oath",
            ["naturalization", "citizenship", "oath", "certificate"],
            "A U.S. naturalization ceremony; the DoJ is moving to revoke the citizenship of naturalized Americans")
    if not image_url:
        px = fetch_pexels_image("american flag courthouse law justice")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "An American flag outside a courthouse; the DoJ is pursuing civil denaturalization cases", "Pexels"

    slug = "doj-denaturalization-wave-indian-origin-citizens-h1b-fraud-neeraj-sharma-20260616"

    body = """For three decades, having your U.S. citizenship revoked was a remote, almost theoretical risk \u2014 something that happened to a handful of war criminals and identity frauds each year. That era is ending. The Justice Department's expanding denaturalization drive has now reached Indian-origin Americans, and the case of a New Jersey staffing executive accused of H-1B visa fraud has put the diaspora squarely inside the widening net.

On June 8, the DoJ filed civil denaturalization actions in federal district courts against 17 naturalized citizens accused of serious offenses ranging from sexual abuse and wire fraud to drug distribution. Among them is Neeraj Sharma, 50, a native of India and the owner and chief executive of Magnavision LLC, a staffing company based in New Jersey. The government is moving to strip the citizenship he was granted in December 2017.

## The Case Against Neeraj Sharma

According to the complaint, Sharma signed and filed eleven fraudulent H-1B visa petitions with U.S. Citizenship and Immigration Services. Each petition, prosecutors allege, falsely claimed that the visa beneficiaries would be employed at a particular global financial institution, and included letters on official corporate letterhead bearing forged executive signatures. He was later convicted of fraud and misuse of visas under federal law for conduct dating from 2015 to 2017.

The denaturalization filing argues that Sharma illegally procured his citizenship in three ways: by failing to disclose his unlawful acts, by providing false testimony, and by concealing a material fact through willful misrepresentation. When he applied to naturalize in 2017, the government says, he swore under penalty of perjury that he had never committed an undisclosed crime, never given false information to officials, and never lied to obtain an immigration benefit \u2014 statements the conviction directly contradicts.

## A Rare Tool, Now Used at Scale

What makes this moment different is not the legal mechanism but its sheer volume. Under the Immigration and Nationality Act, a naturalized citizen's status can be revoked if it was illegally procured or obtained through concealment or willful misrepresentation \u2014 a power the Supreme Court has long upheld. Between 1990 and 2017, the government filed an average of just 11 denaturalization cases a year, under both Republican and Democratic administrations.

That restraint is gone. USCIS guidance issued in December 2025 reportedly directed field offices to supply the DoJ's Office of Immigration Litigation with 100 to 200 denaturalization case referrals every month in fiscal 2026 \u2014 a pace that, if sustained, would dwarf the entire historical record. In May, the department moved against a dozen people, including India-born Debashis Ghosh, accused of orchestrating a $2.5 million investment fraud. The June batch of 17 is the latest escalation.

## "A Privilege, Not a Right"

The administration has framed the campaign in stark moral terms. "American citizenship is a privilege, and it must be earned honestly," Homeland Security Secretary Markwayne Mullin said. "If you come here, break our laws, and lie in your immigration proceedings, you forfeit that privilege." Officials argue that pursuing fraud cases protects the integrity of the system and honors law-abiding citizens, native-born and naturalized alike.

Critics see something more troubling. Senator Dick Durbin questioned why, "with all of the challenges facing America, we are talking about the denaturalization of citizens." Immigration lawyers warn that the civil process carries fewer protections than criminal proceedings \u2014 there is no guaranteed right to an attorney, and the burden of proof is lower \u2014 raising the prospect that long-settled Americans could lose their status over old or contested paperwork.

## Why It Matters to the Diaspora

For the Indian-American community, naturalization has always been the finish line \u2014 the moment when a temporary visa, a green card, and years of waiting finally hardened into something permanent and unassailable. The denaturalization surge unsettles that certainty. While the cases announced so far involve people with criminal convictions or serious fraud allegations, the scale of the referral pipeline means the legal machinery is now built to process citizens, not just immigrants.

The practical lesson for the diaspora is sobering: the accuracy of every form, every interview answer, and every disclosure made during the naturalization journey now carries consequences that can reach back years or decades. Immigration attorneys are advising naturalized citizens to retain their records and seek counsel if old applications contained errors. For a community built on the promise that American citizenship is forever, the message from Washington is that, increasingly, it may not be \u2014 and that the people most exposed are precisely those who arrived through the visa programs the diaspora knows best.

**Sources:** U.S. Department of Justice, USA TODAY, The Indian Eye"""

    article = {
        "headline": "The US Is Stripping Citizenship at a Record Pace. An Indian H-1B Case Just Joined the List.",
        "subheadline": "The Justice Department filed denaturalization actions against 17 naturalized citizens, including New Jersey staffing executive Neeraj Sharma over forged H-1B petitions \u2014 part of a drive that now targets 100 to 200 cases a month.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-rights",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Naturalization is the finish line for most Indian-American families, and a denaturalization drive scaled to 100-200 referrals a month \u2014 now including an H-1B fraud case against an India-born citizen \u2014 means the accuracy of every form and interview answer from the naturalization journey can carry consequences years later, unsettling the long-held assumption that US citizenship, once granted, is permanent.",
        "sources": ["U.S. Department of Justice", "USA TODAY", "The Indian Eye"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 2: Bangladesh-India diplomatic row over Delhi airport detention
# ========================================================================
def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: Bangladesh-India row over Delhi airport detention")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Indira Gandhi International Airport Terminal 3 Delhi",
        ["indira gandhi", "terminal 3", "delhi airport", "igi airport", "new delhi airport"],
        "Indira Gandhi International Airport in New Delhi, where a Bangladeshi PM adviser was held for hours")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "airport immigration terminal international arrivals",
            ["airport", "terminal", "immigration", "arrivals", "departure"],
            "An international airport terminal; a Bangladeshi PM adviser was stopped at immigration in New Delhi")
    if not image_url:
        px = fetch_pexels_image("airport terminal international arrivals immigration")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "An airport arrivals hall; a Bangladeshi PM adviser was detained at Delhi airport", "Pexels"

    slug = "bangladesh-india-diplomatic-row-pm-adviser-zahed-rahman-delhi-airport-iora-20260616"

    body = """A bureaucratic snag at a New Delhi immigration counter has flared into the latest diplomatic rift between India and Bangladesh \u2014 a reminder of how fragile relations remain between the South Asian neighbours nearly two years after the upheaval that reshaped Dhaka's government. Bangladesh has summoned a senior Indian diplomat to protest the treatment of a top adviser to Prime Minister Tarique Rahman, who was stopped and questioned for hours at Indira Gandhi International Airport.

Dr Zahed Ur Rahman, the Prime Minister's adviser on policy and strategy affairs, had travelled to New Delhi on June 14 as part of a Bangladeshi delegation to attend the 28th meeting of senior officials of the Indian Ocean Rim Association (IORA) \u2014 a conference India was hosting on June 15 and 16. Instead of clearing immigration, he found his name flagged on a security-related watchlist and was held for verification.

## What Happened at the Airport

According to Bangladeshi officials, Zahed was kept waiting for about two hours at the airport. He was not carrying a diplomatic passport; he travelled on a regular Bangladeshi green passport with a SAARC visa. Sources close to him told local media he was subjected to "undue harassment." Indian authorities eventually cleared him after identifying and resolving the discrepancy \u2014 reports suggest his name had been removed from a social-media-related blacklist but remained on an immigration watchlist, triggering the alert.

By then, the damage was done. Rather than continue with the visit and attend the IORA meeting, Zahed chose to return home. In a circuitous and pointed journey, he left New Delhi for Colombo on an Air India flight, then flew on to Dhaka aboard a SriLankan Airlines flight the next morning \u2014 returning to Bangladesh via a third country rather than completing his trip in India.

## Dhaka's Protest

The Bangladeshi response was swift. The Ministry of Foreign Affairs summoned India's Deputy High Commissioner and Charg\u00e9 d'Affaires, Pawan Badhe, to convey Dhaka's displeasure. Foreign Minister Khalilur Rahman called the episode "unexpected and unfortunate," telling reporters the ministry was "taking appropriate steps." India's foreign ministry, for its part, offered no immediate public response.

The incident reverberated through Bangladesh's parliament. A Jamaat-e-Islami lawmaker raised the matter on a point of order, describing it as an "extremely sensitive and serious matter" linked to national dignity and demanding a ministerial statement. The Speaker ruled it inadmissible as a point of order but left the door open for a formal notice \u2014 a sign of how quickly the airport episode became a political flashpoint at home.

## A Relationship Under Strain

The friction did not appear out of nowhere. Although ties improved somewhat after Tarique Rahman's election victory earlier this year, relations have been strained since the 2024 uprising that toppled former prime minister Sheikh Hasina, who has remained in India ever since despite repeated extradition requests from Dhaka. That unresolved standoff continues to colour nearly every interaction between the two governments.

The two countries have also clashed over migration. Bangladesh has accused Indian authorities of trying to "push in" undocumented migrants across the border without following agreed repatriation procedures, and said its border guards have foiled several such attempts. The issue surfaced during recent talks between the Border Guard Bangladesh and India's Border Security Force in New Delhi; both sides agreed to strengthen intelligence-sharing and coordinate patrols, but the migrant dispute remains a live source of tension.

## Why It Matters to the Diaspora

For the millions of people of Bangladeshi and Indian origin who move between the two countries \u2014 and for the broader South Asian diaspora that watches the region's politics closely \u2014 the episode is a cautionary tale about how watchlists and administrative errors can ensnare even senior officials. If a prime ministerial adviser travelling for an official conference can be held for hours over a stale database entry, ordinary travellers have reason to worry about the opacity of these systems.

The deeper concern is the trajectory of India-Bangladesh relations themselves. Stable ties between New Delhi and Dhaka underpin everything from cross-border trade and remittances to the security of the eastern frontier and the rhythms of family visits across one of the world's most densely populated borders. Each new row \u2014 over Hasina, over migrants, and now over an airport detention \u2014 chips away at the trust the diaspora depends on. The IORA theme this year was "Innovation, Openness, Resilience and Adaptability." The irony was not lost on Dhaka.

**Sources:** Reuters, The Business Standard, The News (Pakistan)"""

    article = {
        "headline": "A Two-Hour Hold at Delhi Airport Just Sparked an India-Bangladesh Diplomatic Row",
        "subheadline": "Bangladesh summoned an Indian diplomat after PM adviser Zahed Ur Rahman was flagged on a watchlist and detained for hours en route to an IORA conference \u2014 then flew home via Colombo rather than complete his visit.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Stable India-Bangladesh ties underpin cross-border trade, remittances, and family travel across one of the world's busiest borders, so each new rupture \u2014 over Sheikh Hasina's asylum, alleged migrant push-ins, and now an airport detention triggered by a stale watchlist entry \u2014 erodes the trust the South Asian diaspora relies on and shows how opaque security databases can ensnare even senior travellers.",
        "sources": ["Reuters", "The Business Standard", "The News (Pakistan)"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 3: India's GCC boom — N-able Bengaluru, 2.36M workforce
# ========================================================================
def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: India's GCC boom — N-able Bengaluru center")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Bengaluru Bangalore technology park skyline office",
        ["bengaluru", "bangalore", "tech park", "electronic city", "skyline", "manyata", "itpl"],
        "Bengaluru's technology corridor; global firms are expanding their capability centers in the city")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "office building India technology corporate campus",
            ["office", "building", "campus", "corporate", "tech park", "infosys", "wipro"],
            "An Indian technology campus; the country's GCC workforce is projected to hit 2.36 million by end-2026")
    if not image_url:
        px = fetch_pexels_image("modern office technology workspace developers")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "A modern technology office; India's Global Capability Center workforce is booming", "Pexels"

    slug = "india-gcc-boom-nable-bengaluru-center-236-million-workforce-2026-20260616"

    body = """While Washington debates visa fees and Silicon Valley trims its headcount, a quieter and arguably more consequential story is unfolding in Bengaluru: the world's biggest companies are no longer just outsourcing work to India \u2014 they are building their core capabilities there. The latest entrant is N-able, a U.S.-based cybersecurity firm that opened a Global Capability Center (GCC) in the city this week and plans to expand its India workforce by at least 50 percent by the end of 2026.

N-able, which provides IT management, cybersecurity, and data-protection software to more than 500,000 organisations worldwide, said its new Bengaluru center already employs more than 100 people. And in a telling shift from the old offshoring playbook, chief executive John Pagliuca was emphatic that the move was about talent, not cost. "The reason we're in Bengaluru is capability," he told Reuters. "Our priority is to build for the long term, with the right people and a strong foundation, not to pursue a short-term headcount play."

## From Cost Center to Capability Center

That distinction is the heart of India's GCC transformation. For two decades, multinationals sent back-office and support functions to India to save money. Today's GCCs are different: they house high-end engineering, applied machine learning, cloud security, and threat research \u2014 the kind of work that sits at the center of a company's product, not its periphery. Pagliuca said skills in AI engineering, cloud security, and threat research are among the hardest to source anywhere in the world, and that the Bengaluru team would help develop defensive AI capabilities including automated threat detection and faster incident response.

The scale of the trend is staggering. India's GCC workforce is projected to reach 2.36 million employees by the end of 2026, according to a report by industry body Nasscom and the consultancy Zinnov, with AI and cybersecurity driving much of the demand. What began as a handful of captive units has become a parallel technology economy \u2014 one increasingly capable of leading global innovation rather than merely supporting it.

## The Talent War Heats Up

The boom is not without friction. Bengaluru may be India's premier technology hub, but the market for AI and cybersecurity professionals is fiercely contested, with multinationals and homegrown technology firms competing for the same scarce talent. N-able said it is relying on competitive pay packages and the promise of meaningful, globally significant work \u2014 plus clear local career paths \u2014 to attract and keep high-calibre engineers.

That competition is a feature, not a bug, for India's tech workforce. As more global firms plant capability centers in the country, salaries rise, roles grow more sophisticated, and Indian engineers gain access to frontier projects without leaving home. The same dynamic that makes hiring hard for companies is steadily raising the ceiling for the professionals they are chasing.

## A Counterweight to the Visa Squeeze

The timing is striking. The GCC surge is accelerating precisely as the traditional path to a U.S. tech career grows more expensive and uncertain \u2014 a $100,000 H-1B fee fought over in the courts, a weighted lottery favouring high earners, and expanded consular vetting. For a generation of Indian engineers, the calculus is shifting: why navigate an increasingly hostile visa regime when a global-tier role at a multinational is available in Bengaluru, Hyderabad, or Pune?

This is the deeper significance of N-able's announcement and the many like it. The work that once required relocating to California is increasingly being done in India, by Indians, for the same global employers \u2014 and at the cutting edge rather than the back office. The center of gravity in global technology is not shifting away from these companies; it is shifting toward where their talent already lives.

## Why It Matters to the Diaspora

For the Indian diaspora in the United States, the GCC boom is a double-edged development. On one hand, it validates the technical reputation that the community spent decades building \u2014 the same skills that powered Silicon Valley are now anchoring a homegrown industry worth millions of jobs. On the other, it signals that the one-way migration story that defined the diaspora may be giving way to something more circular.

Increasingly, ambitious engineers can build world-class careers without ever boarding a flight to San Francisco, and some members of the diaspora are themselves returning to lead these centers. For NRIs weighing whether to stay, return, or split their lives across two countries, the message is that India is no longer just home \u2014 it is becoming a genuine alternative destination for the most advanced technology work in the world. The bridge between the two economies is starting to carry traffic in both directions.

**Sources:** Reuters, Nasscom-Zinnov GCC report, The Business Standard"""

    article = {
        "headline": "Another Global Tech Firm Just Chose Bengaluru Over the Bay Area. India's Capability Centers Are Booming.",
        "subheadline": "Cybersecurity firm N-able opened a Bengaluru capability center and will grow its India team 50 percent by end-2026 \u2014 part of a GCC wave projected to employ 2.36 million people and built on talent, not cost.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "The Global Capability Center boom \u2014 2.36 million jobs projected by end-2026, now doing frontier AI and cybersecurity work rather than back-office support \u2014 is rewriting the diaspora's one-way migration story: as the US visa path grows costlier and more uncertain, Indian engineers can build world-class careers at home, and some NRIs are returning to lead these centers, turning the bridge between the two economies into two-way traffic.",
        "sources": ["Reuters", "Nasscom-Zinnov GCC report", "The Business Standard"],
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
    results.append(("Denaturalization wave / Indian-origin", write_article_1()))
    results.append(("Bangladesh-India airport row", write_article_2()))
    results.append(("India GCC boom / N-able Bengaluru", write_article_3()))

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        print(f"  {'\u2713 SUCCESS' if success else '\u2717 FAILED'}: {name}")
    print(f"{'='*60}\n")
