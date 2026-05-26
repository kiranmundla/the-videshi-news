#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-26 ~15:30 PDT batch
Topics: 1) Sam Altman admits he was "pretty wrong" about AI job losses — while Standard Chartered cuts 7,800 jobs in Chennai/Bengaluru and calls workers "lower-value human capital"
        2) Trump raised the refugee ceiling by 10,000 — exclusively for white South Africans. Only 3 non-South African refugees admitted all fiscal year. Indian asylum seekers wait years.
"""

import json, os, uuid, re, requests, urllib.parse
from datetime import datetime, timezone, timedelta
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

def sb_get(table, params):
    r = requests.get(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_patch(table, params, data):
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(f"{SB_URL}/rest/v1/{table}", headers=h, params=params, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(slug_base, date_suffix="20260526"):
    slug = slug_base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

pexels_env = Path.home() / "workspace" / ".env.pexels"
PEXELS_KEY = None
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.split("=", 1)[1].strip()

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=15
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    url = photos[0]["src"]["large2x"]
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    try:
        img_data = requests.get(image_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}).content
        content_type = "image/jpeg"
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        h = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        r = requests.post(upload_url, headers=h, data=img_data, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return image_url

# --- Dedup check ---
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-23T00:00:00Z",
    "order": "published_at.desc",
    "limit": "80"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc)
now_iso = now.isoformat().replace('+00:00', 'Z')

articles = []

# ============================================================
# ARTICLE 1: Sam Altman admits AI jobs apocalypse fears were wrong — while Standard Chartered cuts 7,800 in India
# ============================================================
slug1 = make_slug("altman-wrong-ai-jobs-apocalypse-standard-chartered-india-cuts")
if slug1 not in existing_slugs and not any("altman" in h and "jobs" in h for h in existing_headlines_lower):
    headline1 = "Sam Altman Just Said He Was 'Pretty Wrong' About AI Killing Jobs. Standard Chartered Is Cutting 7,800 in Chennai and Bengaluru."
    subheadline1 = "The OpenAI CEO told an Australian conference he's 'delighted to be wrong' about a jobs apocalypse. The same week, a British bank announced it was replacing 'lower-value human capital' with AI — and most of those jobs are in India."
    body1 = """Sam Altman says the jobs apocalypse isn't coming. The people in Chennai and Bengaluru who are about to lose their jobs would like a word.

Speaking virtually at a Commonwealth Bank of Australia conference in Sydney on Tuesday, the OpenAI CEO said he had been "pretty wrong" about the social and economic implications of artificial intelligence. He said he and his executives had been "roughly right" on the technology but had overestimated how quickly AI would eliminate white-collar jobs.

"I'm delighted to be wrong about this," Altman told CBA CEO Matt Comyn. "I thought there would have been more impact on entry-level white-collar jobs being eliminated by now than has actually happened."

He said he had tried using AI to respond to his Slack and email messages, labelling them "this is Sam's AI," but had reverted to answering some himself. "We really do care about our interactions with people," he said. "I don't think we're going to have the kind of jobs apocalypse that some of the companies in our space advocate or talk about."

## The Same Week, Across the World

The same week Altman delivered that assessment, Standard Chartered CEO Bill Winters stood in front of investors in Hong Kong and announced the bank would eliminate approximately 7,800 back-office positions by 2030 — and most of them are in India.

"It's not cost-cutting," Winters said. "It's replacing in some cases lower-value human capital with the financial capital and the investment capital we're putting in."

The phrase "lower-value human capital" triggered such backlash that Winters was forced to issue two separate apologies. "I clearly upset some colleagues," he said in a follow-up post. "For that I am sorry."

The most affected roles will be in Standard Chartered's back-office centres in Chennai and Bengaluru — two of India's largest global technology hubs. Human resources, compliance, and data processing functions are among those being targeted for AI replacement.

## The Numbers Don't Agree With Altman

Altman's reassurance lands in a landscape that contradicts it. At the Reuters India Summit last week, executive after executive described a fundamental shift in how multinational companies hire in India.

Lalit Ahuja, CEO of ANSR, which helps firms build and run global capability centres, said growth and scale in India "from a people standpoint will taper over time." Companies, he said, are "hiring fewer people, just as a matter of abundant caution."

Deena Dayalan, global head of digital operations at Kimberly-Clark, was more direct: "The zero-to-two-years experience category will go away is my assumption in the next few years."

A Nasscom-Zinnov report found that 73 percent of HR leaders at global capability centres flagged a widening skills gap. And 40 percent of employers now prefer demonstrable AI skills or certifications over degrees.

TeamLease Services, one of India's largest staffing firms, said companies are being advised to keep 20 to 30 percent of their workforce on outsourced or variable models — effectively making a large share of India's white-collar workforce disposable.

## The Cockroach Janta Party

The anxiety has spilled into Indian internet culture. A Deloitte Global survey found that Gen Z respondents in India reported higher financial stress due to job insecurity and rising costs, with many postponing major life decisions like buying homes.

The frustration has coalesced into an online movement called the Cockroach Janta Party — a sardonic political identity adopted by young Indians who feel the economy has no place for them. The name is a deliberate provocation: cockroaches survive everything, which is what they feel they must do.

## What It Means for the Diaspora

For Indian engineers in the United States on H-1B visas, Altman's "no apocalypse" framing rings hollow. Over 178,000 tech workers have been laid off in 2026, and for each Indian engineer on an H-1B, a layoff triggers a 60-day clock to find a new job or leave the country.

For Indians in India, the picture is equally unsettling. The country's $315 billion technology services sector — which employs roughly 5.4 million people and powers consumption in cities from Bengaluru to Hyderabad to Pune — is being told to do more with fewer people.

Even companies that are still hiring signalled that the old playbook is dead. Southwest Airlines, which is scaling its Hyderabad technology centre to 1,000 employees, explicitly said it was not building a traditional back-office hub. "We don't want to just do a lift and shift," said Krishna Kallepalli, the airline's India innovation head.

Microsoft India president Puneet Chandok put it simply: "The biggest challenge is to get the right talent with the right AI skill."

Sam Altman can afford to be delighted he was wrong. The 7,800 people in Chennai and Bengaluru whose jobs are being eliminated to make room for the technology his company built cannot."""
    article1 = {
        "id": str(uuid.uuid4()),
        "slug": slug1,
        "headline": headline1,
        "subheadline": subheadline1,
        "body": body1,
        "category": "news",
        "vertical": "technology",
        "diaspora_angle": "Indian H-1B workers face 60-day clocks after layoffs while Altman downplays the impact. India's $315B tech services sector — employer of 5.4 million — is being told to do more with fewer people. Standard Chartered's 7,800 cuts hit Chennai and Bengaluru directly. GCC entry-level hiring in India is collapsing, threatening the consumption economy NRI families depend on.",
        "tags": ["sam altman", "openai", "ai", "jobs", "standard chartered", "chennai", "bengaluru", "india", "outsourcing", "h1b", "nri", "technology"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — OpenAI's Altman says AI unlikely to lead to 'jobs apocalypse'", "url": "https://www.reuters.com/world/asia-pacific/openais-altman-says-ai-unlikely-lead-jobs-apocalypse-2026-05-26/"},
            {"name": "Reuters — In the AI age, firms chase growth but with fewer workers", "url": "https://www.reuters.com/world/india/ai-age-firms-chase-growth-with-fewer-workers-2026-05-26/"},
            {"name": "Reuters — Standard Chartered CEO apologises for 'upset caused' by AI comments", "url": "https://www.reuters.com/business/finance/stanchart-ceo-apologises-upset-caused-by-ai-comments-2026-05-22/"},
            {"name": "Reuters — Global firms rethink GCC hiring in India as AI shifts skill demand", "url": "https://www.reuters.com/world/india/global-firms-rethink-gcc-hiring-india-ai-shifts-skill-demand-2026-05-25/"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now_iso,
        "image_attribution": None,
        "image_url": None,
    }
    # Image sourcing — Sam Altman is the central figure. Wikipedia first.
    img_url = fetch_wikipedia_person_image("Sam Altman")
    if not img_url:
        img_url = fetch_pexels_image("artificial intelligence office workers", "technology corporate office India")
    if img_url:
        filename = f"{article1['id']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        article1["image_url"] = final_url
        article1["image_attribution"] = "Wikimedia Commons" if "wikipedia" in (img_url or "").lower() or "wikimedia" in (img_url or "").lower() or "upload.wikimedia" in (img_url or "").lower() else "The Videshi"
    sb_post("p2_articles", article1)
    articles.append(slug1)
    print(f"✓ Published: {headline1}")
else:
    print(f"⊘ Skipped (dedup): Altman AI jobs article")

# ============================================================
# ARTICLE 2: Trump raised refugee ceiling by 10,000 — exclusively for white South Africans
# ============================================================
slug2 = make_slug("trump-refugee-ceiling-10000-white-south-africans-only")
if slug2 not in existing_slugs and not any("refugee" in h and "south africa" in h for h in existing_headlines_lower):
    headline2 = "Trump Just Raised the Refugee Ceiling by 10,000. Every Single Slot Is Reserved for White South Africans."
    subheadline2 = "Only three non-South African refugees have been admitted to the United States all fiscal year. Indian asylum seekers — including those fleeing religious persecution — are not part of the program."
    body2 = """The United States refugee program now has a hierarchy. White South Africans are at the top. Everyone else is frozen out.

President Trump signed a presidential determination on May 21 increasing the U.S. refugee admissions ceiling by 10,000 — from 7,500 to 17,500 — for the current fiscal year. But the increase is reserved exclusively for white South Africans of Afrikaner ethnicity, whom the administration says face an emergency situation due to "incitement of racially motivated violence" by South Africa's government and political parties.

Reuters reviewed the signed document. South Africa's foreign ministry flatly rejected the premise.

"The assertion that white Afrikaners, in particular, endure systemic persecution is entirely without foundation," said foreign ministry spokesperson Chrispin Phiri.

The numbers tell the fuller story. The Trump administration has admitted only three non-South African refugees in the entire fiscal year — which began in October 2025. Three people, from everywhere in the world that is not South Africa, in eight months.

Meanwhile, 6,000 white South Africans had already been admitted through the end of April, under a program Trump launched in early 2025 when he simultaneously froze refugee admissions from every other country on Earth.

## What This Means for Indians

India is one of the largest sources of asylum seekers in the United States. Thousands of Indians — many of them religious minorities, Dalits, journalists, and political dissidents — have pending asylum cases that have been frozen under the Trump administration's near-total shutdown of the refugee system.

The backlog of pending asylum cases in immigration courts has swelled to over 3.8 million. Indians make up a growing share, particularly Sikhs and Christians from Punjab, Gujarat, and other states who have documented claims of persecution.

The refugee ceiling is a separate mechanism from asylum, but it signals the administration's priorities. The message is unmistakable: there is capacity in the system for 10,000 additional people — but only if they are white, and only if they are from one specific country.

## The Legal and Moral Framework

The Refugee Act of 1980 requires the president to set an annual ceiling for refugee admissions in consultation with Congress, based on "humanitarian concerns" and the "national interest." The law does not contemplate a racial or ethnic filter.

Previous administrations — both Republican and Democratic — set refugee ceilings that allocated slots by region: Africa, East Asia, Europe, Latin America, the Near East and South Asia. Within each region, individual cases were evaluated based on the severity of persecution.

Trump's approach eliminates that framework entirely. The ceiling increase does not allocate any slots to Africa broadly, or to any other region. It is a single carve-out for one ethnic group in one country.

Immigration attorneys have noted the legal vulnerability. "The Refugee Act does not authorize the president to create an ethnicity-specific refugee program," said one former USCIS official who spoke on condition of anonymity. "This will be challenged."

## A Pattern

The refugee carve-out does not exist in isolation. It is part of a broader set of moves by the Trump administration that have reshaped who gets to come to the United States:

The administration has proposed making all two million federal employees sign NDAs that would criminalize speaking to journalists — disproportionately affecting the roughly 100,000 Indian Americans in government. It has ordered green card applicants to undergo consular processing in India rather than adjusting status domestically, adding years to an already decades-long backlog. And it has expanded Ebola-related travel restrictions that apply to green card holders returning from affected countries.

In each case, the underlying logic is the same: tighten the pathway for some, widen it for others.

## What the Diaspora Should Know

The Indian American community is the second-largest immigrant group in the United States. But unlike the white South African program, there is no fast-track for Indians fleeing persecution, no emergency designation for families separated by decades-long green card backlogs, and no presidential determination reserving refugee slots for any South Asian group.

For the Indian family in Houston whose asylum case has been pending for four years, the math is straightforward: 10,000 slots were just created. None of them are for you.

South Africa's government has called the persecution claims baseless. The administration has not listed specific examples of incitement. The State Department declined to confirm the ceiling increase to Reuters, but said the program was "a Trump priority."

The refugee ceiling is, by definition, the upper limit of America's compassion. This administration has decided who that compassion is for."""
    article2 = {
        "id": str(uuid.uuid4()),
        "slug": slug2,
        "headline": headline2,
        "subheadline": subheadline2,
        "body": body2,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "Indian asylum seekers — Sikhs, Christians, Dalits, journalists, political dissidents — have pending cases frozen while 10,000 refugee slots are created exclusively for white South Africans. 3.8M asylum cases backlogged. Combined with consular processing orders, NDA proposals, Ebola travel restrictions, the immigration pathway for Indians is being systematically narrowed.",
        "tags": ["trump", "refugees", "south africa", "asylum", "indian american", "immigration", "racism", "nri", "green card"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Trump raises refugee ceiling by 10,000 to bring in more white South Africans", "url": "https://www.reuters.com/world/us/trump-raises-refugee-ceiling-by-10000-bring-more-white-south-africans-2026-05-26/"},
            {"name": "Reuters — Trump administration proposes NDAs for federal workers", "url": "https://www.reuters.com/world/us/trump-administration-proposes-ndas-federal-workers-crack-down-leaks-journalists-2026-05-26/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now_iso,
        "image_attribution": None,
        "image_url": None,
    }
    # Image sourcing — about Trump (person). Wikipedia first.
    img_url = fetch_wikipedia_person_image("Donald Trump")
    if not img_url:
        img_url = fetch_pexels_image("US immigration office federal building", "American flag government building")
    if img_url:
        filename = f"{article2['id']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        article2["image_url"] = final_url
        article2["image_attribution"] = "Wikimedia Commons" if "wikipedia" in (img_url or "").lower() or "wikimedia" in (img_url or "").lower() or "upload.wikimedia" in (img_url or "").lower() else "The Videshi"
    sb_post("p2_articles", article2)
    articles.append(slug2)
    print(f"✓ Published: {headline2}")
else:
    print(f"⊘ Skipped (dedup): Trump refugee ceiling article")

print(f"\nDone. Published {len(articles)} articles: {articles}")
