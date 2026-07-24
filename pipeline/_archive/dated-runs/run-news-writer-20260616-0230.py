#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-16 02:30 UTC run (scheduled videshi-writer-news)
3 fresh articles, distinct from all 2026-06-15 batches (Iran/Gulf/oil/markets-rally/
immigration-visa/AI-offshoring/Modi-Macron/exam-scandal all saturated):
  1. Canada deportations: India now #1 removed nationality (Q1 2026 CBSA data) — diaspora-safety
  2. Reverse brain drain: 40% of Indian-Americans weighing exit + returning-NRI trend — diaspora-rights
  3. India lets fiscal deficit widen to 4.8% of GDP as Iran war drives up energy bill — economy
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
# ARTICLE 1: Canada deportations — India now #1 removed nationality
# ========================================================================
def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: Canada deportations — India now #1")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Toronto Pearson International Airport terminal",
        ["pearson", "airport", "terminal", "toronto", "yyz"],
        "Toronto Pearson International Airport, a primary point of departure for removals from Canada")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Canada Border Services Agency",
            ["border services", "cbsa", "canada border", "customs", "agency"],
            "A Canada Border Services Agency facility; the CBSA carries out removals of inadmissible foreign nationals")
    if not image_url:
        px = fetch_pexels_image("airport departure terminal travelers luggage")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "An international airport departure hall", "Pexels"

    slug = "india-now-top-deported-nationality-canada-cbsa-q1-2026-removals-20260616"

    body = """For the first time since 2020, Indians are the single largest group of people being deported from Canada \u2014 and the gap is no longer close. According to data from the Canada Border Services Agency, 1,712 Indian citizens were removed from the country between January and March 2026, accounting for nearly one in three of all deportations carried out in the quarter. It is a figure that has quietly reordered Canada's enforcement map and put a generation of Indian students, workers, and asylum seekers on notice.

The number is striking against what came before. Mexican nationals, who had topped Canada's removals list every year from 2021 through 2025, recorded just 743 deportations in the same quarter. In 2025, the picture was almost reversed: Mexico led with 4,837 removals for the full year, while India ranked second at 3,779. By the opening months of 2026, Indians made up 32.5 percent of the 5,260 people removed \u2014 a sharper concentration than any nationality has held in recent memory.

## A Pipeline That Keeps Filling

The quarterly spike is not the whole story. The CBSA's "removal in progress" inventory \u2014 the backlog of people under active deportation orders \u2014 now lists 6,980 Indian nationals, the largest single-country caseload on the books and just over 22 percent of the agency's total pending file of 31,482. Mexico, by comparison, sits at 5,311. At the current pace, removals of Indian citizens in 2026 could nearly double the previous year's total.

Officials and analysts attribute the surge to a convergence of factors rather than a single cause: a record volume of claims and applications from Indian nationals working through the system, the processing outcomes of those claims, and a markedly tougher enforcement posture under Prime Minister Mark Carney's government, which has framed immigration reform as essential to balancing population growth against a housing crisis. A significant share of the removals are tied to refused refugee and asylum claims under recent policy changes. The CBSA also noted that part of the first-quarter increase reflected Indian nationals removed in connection with extortion-related violence \u2014 a politically sensitive thread given the diplomatic friction between Ottawa and New Delhi over crime networks operating across the diaspora.

## The Students Caught in the Middle

What makes the data land so heavily on the community is the sheer size of the Indian footprint in Canada. Indian nationals are the country's largest international student population and one of its biggest pools of temporary foreign workers, staffing manufacturing lines, food production, hospitality, caregiving, and trucking \u2014 the very sectors Canada has long said it cannot fill. India is also among the top source countries for both refugee claims and visitor visa applications.

That breadth means the enforcement squeeze is not falling on a narrow band of rule-breakers. It is reaching the same population that arrived believing the study-to-work-to-permanent-residency ladder was secure. As Canada slashed generic temporary visa quotas by an estimated 43 percent in its 2026 immigration plan and pivoted Express Entry toward narrow, category-based draws in healthcare, STEM, and skilled trades, the off-ramp to permanent residency narrowed for tens of thousands who came on study or work permits. When those permits expire without a renewal or a PR pathway, status lapses \u2014 and a lapsed status is how many of these removal files begin.

## Why It Matters to the Diaspora

For Indian families weighing Canada \u2014 and for the hundreds of thousands already there \u2014 the numbers carry a blunt message: the country remains a real opportunity, but the margin for error has collapsed. The era of volume-driven, speculative applications is over. Securing and keeping status now demands exact alignment with provincial labour shortages, verified employer backing, and meticulous compliance, with little tolerance for the gaps that were once quietly overlooked.

The trend also feeds a larger reckoning already underway in the community. A viral account from a Bengaluru couple who concluded they had "wasted three years moving abroad" struck a nerve precisely because it was not an outlier. Across 2026, more non-resident Indians are choosing to return home from Canada, citing the punishing cost of living in Toronto and Vancouver, the strain of distance from ageing parents, and an India whose digital infrastructure, salaries, and opportunity now compete in ways they did not a decade ago. For some, that return is voluntary. For a growing number, as the CBSA figures show, it is not.

The deeper lesson echoes one the global Indian diaspora has heard from Britain to the United States: the welcome extended to migrants is conditional, and the conditions are tightening everywhere at once. Canada has not closed its door. But it is checking, far more carefully than before, who is still allowed to stand inside it.

**Sources:** Canada Border Services Agency (immigration removal statistics), VisaVerge, Inshorts"""

    article = {
        "headline": "Indians Are Now the Most Deported Nationality From Canada. The Numbers Are Not Close.",
        "subheadline": "CBSA data shows 1,712 Indian citizens removed in the first quarter of 2026 \u2014 nearly one in three of all deportations \u2014 with another 6,980 cases pending, the largest single-country backlog on record.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-safety",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Indians are Canada's largest international student and temporary-worker population, so a removals surge that has pushed them to the top of the CBSA's deportation list \u2014 1,712 in Q1 2026, with 6,980 cases pending \u2014 lands directly on the same study-to-PR pipeline that drew them, a warning that the margin for any lapse in status has collapsed.",
        "sources": ["Canada Border Services Agency", "VisaVerge", "Inshorts"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 2: Reverse brain drain — Indian-Americans weighing exit
# ========================================================================
def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: Reverse brain drain — Indian-Americans weighing exit")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Bangalore skyline city India technology",
        ["bangalore", "bengaluru", "skyline", "city", "tech", "cbd", "ubc"],
        "The Bengaluru skyline; India's tech capital is among the destinations drawing returning non-resident Indians")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Kempegowda International Airport Bangalore terminal",
            ["kempegowda", "airport", "terminal", "bangalore", "bengaluru"],
            "Kempegowda International Airport in Bengaluru, a gateway for non-resident Indians returning home")
    if not image_url:
        px = fetch_pexels_image("modern indian city skyline business district")
        if px and validate_image(px):
            image_url, image_attribution = px, "Pexels"
            image_caption = "A modern Indian city skyline, symbol of the opportunity drawing some non-resident Indians home"

    slug = "reverse-brain-drain-indian-americans-weighing-exit-carnegie-survey-returning-nris-20260616"

    body = """For half a century, the story of Indian-Americans was a one-way arrow. They arrived as students and engineers, stayed as citizens and founders, and rose to run some of the most powerful companies on earth. The United States was the destination, and the only open question was how high a newcomer could climb. That arrow has begun, for the first time, to point both ways.

A 2026 Indian American Attitudes Survey by the Carnegie Endowment for International Peace, conducted with YouGov among 1,000 Indian-American adults, found that roughly one in three has thought about leaving the United States \u2014 and that among those open to a move, a striking share would consider not just India but other countries entirely. The finding has rippled through policy circles precisely because the community in question is the textbook American success story: highly educated, prosperous, and increasingly visible in public life. When even this group begins eyeing the exits, it is read less as personal restlessness than as a structural signal.

## A Convergence of Grievances

The survey's authors \u2014 Milan Vaishnav, Sumitra Badrinathan, Devesh Kapur, and Andy Robaina \u2014 framed the moment as a "convergence of cross-pressures" rather than a single rupture. Frustration with the direction of American politics ranked high, alongside the rising cost of living. Many respondents pointed to discomfort with what they described as a more exclusionary national narrative and the tone of domestic politics. And looming over all of it was the structural grievance the community knows best: the grinding, multi-decade wait for permanent residency that traps even the most accomplished in visa limbo.

The political backdrop is unambiguous. Seventy-one percent of Indian-Americans disapprove of President Donald Trump's handling of his job, with more than half "strongly" disapproving \u2014 a sharper rejection than the U.S. public at large. There are now more than 5.2 million people of Indian origin in the United States, and one year into Trump's second term, the report concluded, they are "confronting a convergence of cross-pressures that has recast their position in America's social and political landscape."

## From "Settle Permanently" to "Optimize Globally"

What analysts find most telling is the shift in mentality the data exposes. For earlier generations, migration meant settling permanently \u2014 a final destination reached after everything was left behind. The emerging posture is different: migration as a global optimization problem, in which talented professionals weigh the United States, India, Canada, the Gulf, and beyond as competing options rather than treating America as the obvious endpoint.

That reframing is what makes the trend hard to dismiss as a passing mood. Push and pull forces are converging at once. On the American side: immigration paralysis, cost, and identity friction. On the other: India's rapid growth, the maturation of its cities and salaries, the pull of family, and the simple familiarity of home. Where green-card backlogs once functioned as golden handcuffs that kept people in place, a more confident India has loosened their grip.

## The Numbers Showing Up at the Airport

The sentiment is no longer only theoretical. Across 2026, more non-resident Indians have been packing up and returning, citing the unaffordability of cities like Toronto and the San Francisco Bay Area, the strain of distance from ageing parents, and an India whose digital infrastructure, UPI-driven convenience, and rising pay now rival what Western incomes deliver once cost of living is stripped out. A viral essay from a Bengaluru couple who decided they had "wasted three years moving abroad" became a lightning rod not because it was extreme but because so many recognised themselves in it.

This is not the first time observers have spoken of a "reverse brain drain." Two decades ago, India's services boom drew home tens of thousands of returnees, with Bengaluru alone counting an estimated 40,000 returned non-resident Indians. What is different now is the breadth of the alternatives and the depth of the discontent in the destination country itself.

## Why It Matters to the Diaspora

For the diaspora, the survey is a mirror held up at an uncomfortable angle. It reflects a community that has achieved extraordinary success yet feels, increasingly, that its belonging is contingent \u2014 valued for what it contributes, scrutinised when politics sours, and tethered to a residency system that has not kept pace with its lives. The question the report poses is pointed: not whether the United States can afford to lose a meaningful slice of its Indian-American talent, but what it becomes if the world's most ambitious people stop believing it is the place where dreams come true.

For India, the same numbers read as opportunity \u2014 a chance to win back the prodigies it once lost, provided it can offer not just competitive pay but the institutions, infrastructure, and quality of life that make staying a genuine choice rather than a reluctant compromise. The arrow is no longer fixed in one direction. Where it ultimately points will be decided, on both shores, by far more than politics.

**Sources:** Carnegie Endowment for International Peace (2026 Indian American Attitudes Survey), American Kahani, Business Standard"""

    article = {
        "headline": "One in Three Indian-Americans Has Thought About Leaving the US. The Arrow Is Now Pointing Both Ways.",
        "subheadline": "A Carnegie Endowment survey finds the community that defined the American success story is quietly weighing the exits \u2014 driven by political alienation, cost of living, and an endless wait for green cards \u2014 just as a more confident India draws its talent home.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "diaspora-rights",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "When the United States' most successful immigrant community \u2014 5.2 million strong, Silicon Valley's backbone \u2014 starts treating migration as a global optimization problem rather than a one-way move, it reshapes the calculus for every NRI weighing whether to stay, leave, or return, and signals that belonging built on economic usefulness has limits even at the very top.",
        "sources": ["Carnegie Endowment for International Peace", "American Kahani", "Business Standard"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 3: India lets fiscal deficit widen to 4.8% as Iran war bites
# ========================================================================
def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: India fiscal deficit widening to 4.8%")
    print("=" * 60)

    # Named person → Wikipedia first
    wiki = fetch_wikipedia_person_image("Nirmala Sitharaman")
    image_url = image_caption = image_attribution = None
    if wiki and validate_image(wiki):
        image_url = wiki
        image_caption = "Finance Minister Nirmala Sitharaman, who warned of uncertainty over forex, oil and fertiliser prices and a rain shortfall"
        image_attribution = "Wikimedia Commons"
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Reserve Bank of India building Mumbai",
            ["reserve bank", "rbi", "north block", "finance ministry", "mumbai", "secretariat"],
            "India's finance and central-banking apparatus, as the government braces for a wider budget deficit")
    if not image_url:
        px = fetch_pexels_image("indian rupee currency money finance")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "Indian rupee notes amid pressure on government finances", "Pexels"

    slug = "india-fiscal-deficit-widen-4-8-percent-gdp-iran-war-energy-subsidy-costs-20260616"

    body = """India is quietly preparing to spend more than it promised. Officials say the government is willing to let its budget deficit widen to as much as 4.8 percent of gross domestic product this year \u2014 up from the 4.3 percent target set in February \u2014 as the war in the Gulf drives up the cost of the energy and fertiliser subsidies that cushion Indian households and farmers. It is a half-percentage-point slip that, in an economy the size of India's, runs into trillions of rupees, and it captures how a conflict thousands of miles away has reached straight into New Delhi's ledger.

The willingness to let the deficit run wider, first reported by Bloomberg News citing an official familiar with the matter, marks a notable shift in tone for a government that has spent years burnishing its fiscal-discipline credentials. Finance Minister Nirmala Sitharaman acknowledged the strain directly on Monday, listing a thicket of pressures: uncertainty over foreign exchange, volatile crude oil and fertiliser prices, and a shortfall of rains this year that threatens the farm economy. Each of those, on its own, is manageable. Arriving together, they are reshaping the arithmetic of the budget.

## The Oil at the Heart of It

The mechanism is brutally simple. India imports roughly 90 percent of the crude oil it consumes and a large share of its cooking gas, much of it routed through the Strait of Hormuz. When the war in the Gulf choked that waterway and pushed prices up, every barrel grew more expensive and so did the subsidies the government uses to shield consumers from the full blow. State-owned fuel retailers raised pump prices four times in May, and even that did not fully pass on the cost. Sixteen India-bound ships carrying fertiliser \u2014 urea, di-ammonium phosphate, ammonia, and sulfur \u2014 were left stranded in the Strait of Hormuz, threatening input supplies just as the summer sowing season demands them.

There is, however, a thread of relief running through the gloom. The preliminary U.S.-Iran agreement to end the war and reopen the Strait of Hormuz sent Brent crude tumbling more than 5 percent to about $82.80 a barrel, its lowest since March, and Indian markets rallied on the news. The Chief Economic Adviser, V. Anantha Nageswaran, has said fuel retailers may not have to pass on much more of the higher costs if global prices settle lower for the year as financial markets expect. But the reopening only restores the prewar status quo, and shippers say traffic will resume only once safety is assured \u2014 leaving the government to budget for uncertainty rather than relief.

## Courting the Dollars to Plug the Gap

To offset the pressure on its currency and its accounts, New Delhi has been moving aggressively to pull foreign money in. The Reserve Bank of India recently exempted foreign institutional investors from capital gains tax on government securities and issued detailed guidelines on hedging benefits for lenders raising non-resident deposits and for state firms borrowing overseas. The early returns are visible: overseas investors net bought 155.5 billion rupees of Indian bonds in just six sessions in June, and the 10-year benchmark yield fell to 6.90 percent. The rupee, battered earlier in the year, firmed to about 94.71 to the dollar.

The bigger prize is structural. Investors say the tax changes strengthen India's bid for inclusion in the Bloomberg Global Aggregate Index \u2014 a step that, like the country's earlier entry into JPMorgan's emerging-market debt index, could bring durable, predictable inflows for years. Bloomberg Index Services is expected to seek investor feedback this month on adding Indian government bonds to its flagship benchmark. For a government bracing for a wider deficit, locking in that kind of long-term foreign demand is the surest way to keep borrowing costs from spiralling as it spends more.

## Why It Matters to the Diaspora

For non-resident Indians, this is the rare macro story that touches the wallet on both sides. A wider deficit and an uncertain rupee shape the returns on everything NRIs hold back home \u2014 from NRE and NRO deposits to property and bonds \u2014 and the RBI's new measures to court overseas money, including the easing around non-resident deposits, are aimed squarely at the diaspora's savings. A firmer rupee and lower bond yields lift the value of remittances and investments sent home; a slipping currency erodes them.

The deeper signal is about confidence. India is betting it can absorb a temporary fiscal stretch because the war that caused it appears to be ending and because foreign capital is once again flowing toward its markets. For the diaspora deciding where to park savings, send money, or invest in the country's growth story, the question is whether that bet holds \u2014 whether the deficit proves a one-year war premium or the start of a looser fiscal era. The next budget, and the path of oil once the Strait of Hormuz fully reopens, will give the answer.

**Sources:** Reuters, Bloomberg News, NDTV"""

    article = {
        "headline": "India Is Ready to Break Its Own Budget Promise. The Reason Is Sitting in the Strait of Hormuz.",
        "subheadline": "New Delhi will let its fiscal deficit widen to as much as 4.8 percent of GDP \u2014 above February's 4.3 percent target \u2014 as the Gulf war drives up energy and fertiliser subsidy costs, even as a fragile peace deal offers the first hint of relief.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "A wider Indian deficit and an uncertain rupee directly shape what NRIs earn on NRE/NRO deposits, property, and bonds back home \u2014 and the RBI's push to plug the gap by courting overseas money, including new hedging benefits on non-resident deposits, is aimed squarely at the diaspora's savings, making the value of every remittance and investment hinge on whether this fiscal bet holds.",
        "sources": ["Reuters", "Bloomberg News", "NDTV"],
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
    results.append(("Canada deportations India #1", write_article_1()))
    results.append(("Reverse brain drain Indian-Americans", write_article_2()))
    results.append(("India fiscal deficit 4.8%", write_article_3()))

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        print(f"  {'\u2713 SUCCESS' if success else '\u2717 FAILED'}: {name}")
    print(f"{'='*60}\n")
