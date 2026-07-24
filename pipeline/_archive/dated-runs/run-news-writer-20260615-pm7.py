#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-15 PM7 batch (scheduled videshi-writer-news, 22:30 UTC run)
3 fresh articles, distinct from all earlier 2026-06-15 batches (Gulf/oil/markets/immigration saturated):
  1. Form 16 becomes Form 130: India's new salary TDS certificate under the Income-tax Act 2025 (personal-finance)
  2. UK charges Indian captain Ajay Pant of Russian shadow-fleet tanker Smyrtos (diaspora-safety / maritime labour)
  3. Australia's Indian diaspora beyond the model minority: social cohesion amid anti-immigration pushback (diaspora-rights)
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


def finalize(article, image_url, image_caption, image_attribution):
    if image_url:
        article["image_url"] = image_url
        article["image_caption"] = image_caption
        article["image_attribution"] = image_attribution
    else:
        print("  \u26a0 No valid image found \u2014 inserting without image")
    return insert_article(article)


# ========================================================================
# ARTICLE 1: Form 16 becomes Form 130 — new salary TDS certificate
# ========================================================================
def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: Form 16 becomes Form 130")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Income Tax Department India building office",
        ["income tax", "aaykar", "tax", "office", "building", "bhavan", "department"],
        "An Income Tax Department office in India, where the new Form 130 replaces the decades-old Form 16 from the 2026-27 tax year")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Indian rupee currency notes money",
            ["rupee", "currency", "note", "money", "banknote", "india"],
            "Indian rupee notes; salaried taxpayers will receive the new Form 130 TDS certificate from the 2026-27 tax year")
    if not image_url:
        px = fetch_pexels_image("tax documents calculator paperwork desk")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "Tax paperwork on a desk, as India transitions from Form 16 to the new Form 130 salary TDS certificate", "Pexels"

    slug = "form-16-becomes-form-130-india-new-salary-tds-certificate-income-tax-act-2025-20260615"

    body = """For nearly four decades, the arrival of Form 16 each June has been a small, familiar ritual of Indian working life \u2014 the single sheet of paper that told you how much you earned, how much tax your employer had quietly shaved off, and which you then dutifully fed into your income-tax return. That ritual is now on its last lap. From the 2026-27 tax year, Form 16 will be replaced by a redesigned document called Form 130, the most visible consumer-facing change in the sweeping new Income-tax Act, 2025.

The shift was confirmed this week as employers across the country issued the final batch of old-style Form 16 certificates ahead of the June 15 deadline. For income earned in the financial year just ended (2025-26), the familiar Form 16 still applies. But the salary slips and tax certificates that follow will carry a new name, a new structure, and a new statutory basis.

## What Actually Changes

At its core, Form 130 does the same job Form 16 always did: it is the annual certificate of tax deducted at source on salary, issued by an employer and used to file your return. What changes is the architecture around it.

Form 16 had two parts \u2014 Part A with employer and employee details and a TDS summary, and Part B with the detailed salary computation. Form 130 has three. Part A carries the identity details, Part B summarises income paid and tax deducted, and a new Part C holds the full computation, split into Annexure I for salaried employees and Annexure II for senior citizens drawing pension and interest income. That last addition matters: for the first time, specified banks can issue the certificate directly to eligible senior citizens on their interest income, folding a group that previously sat awkwardly outside the system into the same framework.

The deeper change is conceptual. The Income-tax Act, 2025 retires the dual language of "Financial Year" and "Assessment Year" \u2014 a distinction that has confused taxpayers for generations \u2014 in favour of a single, simplified "Tax Year." The quarterly TDS return employers file, long known as Form 24Q, becomes Form 138, and Form 130 is system-generated only after that return is processed and downloaded from the TRACES portal. As tax authorities have stressed, a certificate prepared outside the system will not be legally valid.

## Why It Matters to the Diaspora

For the millions of non-resident Indians who still hold salaried roles, rental income, or financial ties in India, the renumbering is more than cosmetic. The entire form ecosystem they have learned to navigate has been relabelled in one stroke. Form 16A, the certificate for non-salary TDS that NRIs encounter most often \u2014 on rent, interest, and professional fees \u2014 becomes Form 131. Form 26AS, the master tax-credit statement that every NRI checks before filing, is now Form 168. Form 12BB, used to declare deductions, becomes Form 124.

This is precisely the kind of bureaucratic reset that trips up diaspora taxpayers, who often file from abroad without a chartered accountant looking over their shoulder. An NRI who earned salary in India during a partial year of residency, or who collects rent on a flat in Pune or Bengaluru, will from next year receive documents that look unfamiliar even though the underlying numbers are the same. The risk is not in the substance but in the confusion: mismatched form names, auto-populated entries pulled from the renamed annual information statement, and the temptation to assume nothing has changed.

## What NRIs Should Do Now

Tax advisers offering early guidance make three points. First, for this filing season \u2014 covering income earned in 2025-26 \u2014 nothing changes; the old forms apply, and returns should be filed as usual. Second, from the 2026-27 tax year onward, NRIs should expect the new nomenclature and reconcile the renamed annual information statement (now Form 168) against salary records and bank statements before filing, exactly as they did with Form 26AS, to avoid the automated notices that flow from mismatches. Third, anyone relying on an Indian employer or tenant to deduct and deposit tax should confirm that those parties are filing the new quarterly return (Form 138), because Form 130 cannot be generated until they do.

The Income-tax Act, 2025 replaces a law that had stood for more than sixty years, and the government has framed the transition as largely administrative \u2014 a tidying of language rather than a change in liability. For the diaspora, that is the reassuring part. The unglamorous truth is that the most common way overseas Indians fall foul of the tax department is not evasion but paperwork, and a year in which every familiar form has been renamed is a year to read the fine print twice.

**Sources:** SCC Times, Mint (LiveMint), ClearTax, Zoho Payroll India"""

    article = {
        "headline": "India Just Renamed the One Tax Form Every Salaried Person Knows. Form 16 Is Now Form 130.",
        "subheadline": "The decades-old salary TDS certificate gets a three-part redesign and a new statutory basis under the Income-tax Act, 2025 \u2014 and for NRIs filing from abroad, every familiar form they rely on has quietly been relabelled.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "personal-finance",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Millions of NRIs with salary, rent, or financial ties in India rely on forms like Form 16, Form 16A and Form 26AS to file from abroad without an accountant \u2014 and the Income-tax Act, 2025 has renamed all of them at once (to Form 130, 131 and 168), making the 2026-27 tax year a minefield of paperwork confusion even though the underlying liability is unchanged.",
        "sources": ["SCC Times", "LiveMint", "ClearTax", "Zoho Payroll India"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 2: UK charges Indian captain of Russian shadow-fleet tanker
# ========================================================================
def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: Indian captain of shadow-fleet tanker charged")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "oil tanker ship sea crude",
        ["tanker", "oil", "ship", "crude", "vessel", "sea"],
        "A crude oil tanker at sea; British commandos seized the shadow-fleet tanker Smyrtos in the English Channel")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Royal Marines Royal Navy boarding vessel",
            ["royal marine", "royal navy", "boarding", "commando", "marine", "navy"],
            "Royal Marine commandos; British forces boarded the Smyrtos in a first-of-its-kind interdiction")
    if not image_url:
        px = fetch_pexels_image("oil tanker cargo ship ocean")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "An oil tanker at sea, the kind of vessel that crews Russia's sanctioned shadow fleet", "Pexels"

    slug = "uk-charges-indian-captain-ajay-pant-russian-shadow-fleet-tanker-smyrtos-sanctions-20260615"

    body = """In the early hours of Sunday, June 14, Royal Marine commandos and British law-enforcement officers fast-roped onto the deck of an oil tanker in the English Channel. The vessel, the Cameroonian-flagged Smyrtos, was part of what Western governments call Russia's "shadow fleet" \u2014 the secretive armada of ageing tankers that move sanctioned Russian crude around the world and help fund the war in Ukraine. By Monday evening, the ship's captain had been charged. His name is Ajay Pant. He is 38 years old. And he is an Indian national.

The case has thrown an uncomfortable spotlight on a fact that rarely makes headlines: a vast share of the world's merchant seafarers, including those crewing the most legally treacherous vessels afloat, are Indian. Of the Smyrtos's 25 crew members, multiple were Indian citizens, and it was Pant, as master, who now faces a charge of contravening UK sanctions by "directly or indirectly supplying or delivering by ship prohibited oil or oil products from Russia to a third country." He was due to appear at Southampton Magistrates' Court on Tuesday and could face up to ten years in prison if convicted.

## A First-of-Its-Kind Seizure

Britain's National Crime Agency said the six-hour operation \u2014 the first UK-led interdiction of its kind \u2014 was months in the planning. New Defence Secretary Dan Jarvis told MPs the action "deals another blow to Putin," noting that the UK has sanctioned more than 550 shadow-fleet vessels and that nearly 200 have been forced to anchor as a result. The Smyrtos is now held off the Dorset coast.

The vessel's profile reads like a case study in sanctions evasion. It is owned by a Hong Kong-registered company that controls several sanctioned tankers, and its management company is listed in the Indian state of Tamil Nadu. For the past year, according to trade-tracking data, the Smyrtos had been shuttling crude between Russia's Pacific ports and China, at one point conducting a "dark" ship-to-ship transfer with another sanctioned vessel. Pant himself had, just a week before the seizure, posted a video to social media from the Baltic Sea showing a drone being shot down near St Petersburg, captioned "Welcome to Russia."

## The Indians Who Crew the Shadow Fleet

The charge against Pant is the sharp end of a much larger and largely invisible story. Indians make up one of the single largest national groups among the world's roughly 1.9 million merchant seafarers, prized by global shipping for their training, English fluency and willingness to take long, hard postings. That same labour pool has increasingly been drawn \u2014 sometimes knowingly, often not \u2014 into the shadow fleet, where pay can be higher precisely because the legal and physical risks are greater.

Those risks are no longer hypothetical. The seizure comes in the same month that three Indian sailors were killed in a US strike on a tanker off Oman, and as the Indian government's Directorate General of Shipping moves to restrict deployment of Indian crews into the most dangerous waters of the Gulf. An Indian seafarer today can find himself a casualty of one conflict or a criminal defendant in another, depending on which cargo his employer chose to carry \u2014 decisions made far above his pay grade, in shipping offices and shell companies he will never see.

## Why It Matters to the Diaspora

For the diaspora, the Pant case is a warning about the legal exposure of a workforce that India has long celebrated as a source of foreign-exchange remittances but rarely protected with matching vigour. A ship's master is legally responsible for his vessel's conduct, even when ownership is buried under flags of convenience and offshore holding companies engineered specifically to obscure who is really in charge. When the sanctions net closes, it is the Indian officer on the bridge \u2014 not the unnamed beneficial owner \u2014 who is led off in handcuffs.

The episode raises hard questions for New Delhi. Does an Indian seafarer recruited onto a vessel whose true cargo and ownership are concealed deserve consular support, legal aid and a presumption that he may have been a pawn rather than a principal? Or is he simply on his own in a foreign court? As Western navies escalate their campaign against the shadow fleet \u2014 and British officials have made clear this seizure is "just the beginning" \u2014 more Indian seafarers are likely to find themselves on the wrong side of sanctions law. For a community whose merchant mariners quietly send billions home each year, the safety net behind that lifeline is about to be tested in courtrooms far from home.

**Sources:** Reuters, The Times (London), The Sun"""

    article = {
        "headline": "British Commandos Seized a Russian Shadow-Fleet Tanker. The Captain They Charged Is Indian.",
        "subheadline": "Ajay Pant, 38, faces up to ten years in a UK prison for breaching sanctions \u2014 a case that exposes how India's vast merchant-seafarer workforce is being drawn, often unknowingly, into the most legally dangerous corner of global shipping.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-safety",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Indians are one of the largest national groups among the world's merchant seafarers, and the charging of Captain Ajay Pant shows how that workforce \u2014 long celebrated by India for its remittances but rarely protected \u2014 is being pulled into the Russian shadow fleet, where the Indian officer on the bridge, not the hidden beneficial owner, is the one who ends up in handcuffs.",
        "sources": ["Reuters", "The Times (London)", "The Sun"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 3: Australia's Indian diaspora beyond the model minority
# ========================================================================
def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: Australia's Indian diaspora and social cohesion")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Diwali festival Australia Sydney Indian community",
        ["diwali", "deepavali", "festival", "sydney", "melbourne", "australia", "indian"],
        "An Indian community Diwali celebration in Australia, now home to the country's largest overseas-born population")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Sydney Opera House Australia skyline",
            ["sydney", "opera house", "australia", "harbour", "skyline", "melbourne"],
            "Sydney, Australia, where Indians have become the largest overseas-born community for the first time")
    if not image_url:
        px = fetch_pexels_image("indian community festival celebration diaspora")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "An Indian cultural celebration; Indians are now Australia's largest overseas-born community", "Pexels"

    slug = "australia-indian-diaspora-beyond-model-minority-social-cohesion-anti-immigration-20260615"

    body = """India has overtaken England as the single largest source of Australia's overseas-born population \u2014 the first time in the nation's history that a non-British migrant group has held that place. It is a milestone heavy with symbolism for a country whose modern identity was built on British settlement. But a growing body of research, and a wave of anti-immigration street protests, suggests the more important question is no longer how many Indians have arrived. It is whether Australia knows how to live with them.

A recent analysis from the Lowy Institute's Interpreter, written by researchers at the Australia India Institute, argues that the very framing that once flattered the community \u2014 the "model minority," prosperous, educated, seamlessly integrated \u2014 has become a trap. "Reducing what is now Australia's largest overseas-born community to an economic asset is corroding the foundations of social trust," the authors write, warning that a community celebrated only for what it earns becomes dangerously easy to recast, when politics sours, as a pressure on housing, jobs and national identity.

## From Asset to Outsider

That recasting is already underway. Over the past year, "March for Australia" rallies \u2014 anti-immigration demonstrations that Australian government ministers have linked to neo-Nazi networks and condemned for "spreading hate" \u2014 have drawn thousands across Sydney, Melbourne, Brisbane and other cities. Promotional material for the marches singled out Indian migrants directly, including a widely shared flyer claiming more Indians had come to Australia in five years than Greeks and Italians did in a century. An independent fact-check found the claim flatly false: cumulative Greek and Italian migration over earlier decades far exceeded Indian arrivals. But the falsehood travelled regardless, doing the work that disinformation is designed to do.

The Indian community now numbers well over 800,000 people and accounts for more than 3 percent of Australia's population. Yet the Lowy analysis argues that researchers and policymakers still treat it as a monolith \u2014 a single bloc to be measured by income and "integration" \u2014 when in reality it is sharply stratified by class, caste, language, religion, visa status and generation. The experience of a temporary student visa-holder squeezed by the cost of living bears little resemblance to that of a settled permanent resident, or an Australian-born child of Indian parents negotiating identity and belonging.

## The Cohesion Gap

The danger, the researchers argue, is a "blind spot" in how Australia understands its largest migrant community: plenty of data on what Indians earn and how well they assimilate, almost none on how they feel, whether they trust public institutions, and how they connect with other migrant groups. Into that vacuum step the prejudicial campaigns. "Without these insights, policy will continue to be shaped by prejudicial public campaigns designed to divide," they write.

Australia's own government frames the goal, in the words of Assistant Minister Julian Hill, as building "bridging" social capital \u2014 the ties that connect different communities to one another, rather than just celebrating diversity within them. The harder work, the analysis suggests, is not representation at festivals and citizenship ceremonies, but sustained engagement that lets a diverse diaspora trust the society around it and be trusted in return. Where that fails, communities used for "narrow strategic gain without corresponding investment in their wellbeing" become more vulnerable to social division and even foreign interference.

## Why It Matters to the Diaspora

For Indians weighing Australia as a destination \u2014 and for the hundreds of thousands already there \u2014 this is the uncomfortable subtext beneath an otherwise triumphant headline. Becoming the largest overseas-born group is a marker of how far the community has come; it is also precisely what makes it the most visible target when anti-immigration sentiment rises. The "model minority" label, so often worn as a badge of pride, offers no protection. It can flip overnight into resentment, because a community defined purely by its economic contribution is judged the moment that contribution is questioned.

The episode is a case study in a pattern the global Indian diaspora knows well, from Britain to Canada to the United States: acceptance built on usefulness is conditional, and conditional acceptance is fragile. The lesson the Australian researchers draw \u2014 that belonging has to be built on civic trust, not transactional value \u2014 applies far beyond Australia's shores. For a diaspora that now spans more than 35 million people, the question of how to be seen as fully part of the societies they help build, rather than perpetual guests judged by their output, may be the defining challenge of the next generation.

**Sources:** Lowy Institute (The Interpreter), AAP FactCheck, The Sydney Morning Herald"""

    article = {
        "headline": "Indians Are Now Australia's Largest Migrant Group. That Is Exactly Why They Are Under Attack.",
        "subheadline": "A milestone of belonging has collided with a wave of anti-immigration protests \u2014 and researchers warn that the 'model minority' label Indian-Australians wear with pride offers no protection when politics turns against them.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-rights",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Indians becoming Australia's largest overseas-born community is a milestone of belonging that also makes them the most visible target of rising anti-immigration sentiment \u2014 and the lesson, that acceptance built on economic usefulness is fragile and conditional, applies to the entire 35-million-strong global diaspora from Britain to Canada to the US.",
        "sources": ["Lowy Institute (The Interpreter)", "AAP FactCheck", "The Sydney Morning Herald"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# MAIN
# ========================================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"VIDESHI NEWS WRITER (PM7) \u2014 {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")

    results = []
    results.append(("Form 16 becomes Form 130", write_article_1()))
    results.append(("Indian captain shadow-fleet tanker", write_article_2()))
    results.append(("Australia Indian diaspora cohesion", write_article_3()))

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        print(f"  {'\u2713 SUCCESS' if success else '\u2717 FAILED'}: {name}")
    print(f"{'='*60}\n")
