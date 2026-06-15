#!/usr/bin/env python3
"""
Videshi News Writer — 2026-06-15 PM5 batch (scheduled videshi-writer-news, 18:30 UTC run)
3 fresh articles, distinct from all earlier 2026-06-15 batches:
  1. HCLTech buys 10.5% of Sarvam AI at $1.5bn valuation — sovereign AI bet (tech)
  2. Bharat Innovates 2026 opens in Nice — Modi+Macron, 120 startups, 500 investors (innovation economy)
  3. Supreme Court stays all HC cases on Transgender Amendment Act 2026, will hear itself (rights/law)
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
# ARTICLE 1: HCLTech buys 10.5% of Sarvam AI at $1.5bn valuation
# ========================================================================
def write_article_1():
    print("\n" + "=" * 60)
    print("ARTICLE 1: HCLTech buys 10.5% of Sarvam AI")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "HCL Technologies office building Noida",
        ["hcl", "noida", "office", "building", "technologies", "campus"],
        "HCLTech, the Indian IT giant taking a strategic stake in homegrown AI startup Sarvam")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "artificial intelligence India technology data center",
            ["data center", "server", "artificial intelligence", "technology", "computing"],
            "India's bid to build sovereign AI gets a major boost as HCLTech backs Sarvam")
    if not image_url:
        px = fetch_pexels_image("artificial intelligence data server technology")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "Servers powering artificial intelligence systems", "Pexels"

    slug = "hcltech-buys-stake-sarvam-ai-1-5-billion-sovereign-ai-bet-20260615"

    body = """India just minted a new artificial-intelligence champion \u2014 and one of its oldest IT houses is betting big that the future of the technology will be built in Bengaluru, not borrowed from Silicon Valley. HCLTech, India's third-largest software exporter, announced on Monday that it will buy a 10.5 percent stake in homegrown generative-AI startup Sarvam AI for \u20b914.27 billion ($150.7 million) in cash, leading the firm's Series B funding round and valuing the three-year-old company at $1.5 billion.

For the diaspora that powers so much of India's technology story \u2014 the engineers in Seattle, the founders in the Bay Area, the venture capitalists writing checks from Menlo Park \u2014 the deal is a signal that the question of whether India can build frontier AI of its own is no longer hypothetical.

## The Deal

HCLTech said it will acquire 41,421 equity shares in Sarvam and fund the startup's research and development into next-generation models for agentic AI, coding and cybersecurity. The Series B round raised $234 million in its first close, out of a targeted $300 million, and was co-led by Bessemer Venture Partners, with continued participation from existing backers Khosla Ventures and Peak XV Partners \u2014 the firm formerly known as Sequoia Capital India.

For HCLTech, the investment is strategic rather than purely financial. The company said the stake will let it develop bespoke language models and AI solutions for its global client base, and \u2014 crucially \u2014 accelerate "sovereign AI" offerings for governments and regulated industries that cannot or will not route sensitive data through American or Chinese models.

Sarvam is no stranger to global tech. In 2024, Microsoft partnered with the startup to support voice-based generative AI applications, a tie-up that underscored Sarvam's focus on building models that work across India's dozens of languages.

## Why "Sovereign AI" Is Suddenly the Phrase of the Year

The timing is no accident. The deal lands just as India confronts the hard limits of depending on foreign AI infrastructure. Indian firms have spent the past month grappling with restricted access to the most advanced American models, and policymakers and technologists alike have converged on a single conclusion: a country of 1.4 billion people, with the world's largest pool of software talent, cannot outsource the foundational layer of the next computing era.

"Sovereign AI" \u2014 the idea that a nation should control its own models, data and compute rather than rent them from abroad \u2014 has moved from think-tank jargon to boardroom strategy. Sarvam, which builds India-first foundation models tuned to Indian languages and use cases, sits squarely at the centre of that ambition. HCLTech's money and enterprise reach give those models a path into real deployments: banks, government departments, hospitals and the regulated sectors where data cannot leave the country.

## A New Template for Indian Tech

The structure of the deal is itself telling. Rather than a pure venture bet, an established IT services giant is taking a strategic stake in a young model-builder \u2014 marrying Sarvam's research with HCLTech's distribution muscle and its roster of Fortune 500 clients. It is a template that could reshape how India's legacy IT industry, long criticised as a low-margin "body shop" business, reinvents itself for the AI age.

The numbers around Sarvam tell their own story of how fast Indian deep tech is maturing. A $1.5 billion valuation for a company barely three years old, a $300 million target round, and a marquee investor syndicate spanning American and Indian funds \u2014 this is the kind of capital formation that, until recently, flowed almost exclusively to startups headquartered in California.

## Why It Matters to the Diaspora

For NRIs, the Sarvam deal is more than a funding headline. A vast share of the world's AI talent is of Indian origin \u2014 running labs at OpenAI, Google, Microsoft and Anthropic, and founding startups across Silicon Valley. The rise of a credible, well-capitalised Indian AI champion creates, for the first time, a serious reverse-migration pull: a reason for that talent to build in India, or to invest in it, rather than only abroad.

It also reframes the diaspora's relationship with the homeland's tech economy. Many overseas Indians are angel investors and limited partners in the very funds \u2014 Peak XV, Khosla, Bessemer \u2014 now backing Sarvam. The sovereign-AI push gives them a thesis that is both patriotic and commercial: that India's next great technology companies will be built at home, for Indian languages and Indian institutions, and that the diaspora can be early to the trade rather than late. Whether Sarvam becomes India's answer to OpenAI is far from settled \u2014 but a $1.5 billion valuation says the market is no longer waiting to find out.

**Sources:** Reuters, HCLTech and Sarvam AI company statements"""

    article = {
        "headline": "HCLTech Just Bet $150 Million on India Building Its Own AI. Sarvam Is Now Worth $1.5 Billion.",
        "subheadline": "The IT giant's 10.5 percent stake in the three-year-old startup is a wager that India's 'sovereign AI' future will be built in Bengaluru, not rented from Silicon Valley.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "tech",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "A huge share of the world's AI talent is of Indian origin and many NRIs are angel investors and LPs in the very funds backing Sarvam \u2014 so a credible, well-capitalised Indian AI champion creates a real reverse-migration and investment pull for the diaspora to build in and invest in India rather than only abroad.",
        "sources": ["Reuters", "HCLTech company statement", "Sarvam AI"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 2: Bharat Innovates 2026 opens in Nice
# ========================================================================
def write_article_2():
    print("\n" + "=" * 60)
    print("ARTICLE 2: Bharat Innovates 2026 opens in Nice")
    print("=" * 60)

    image_url = fetch_wikipedia_person_image("Narendra Modi")
    image_caption = ""
    image_attribution = ""
    if image_url and validate_image(image_url):
        image_caption = "PM Narendra Modi, who co-launched Bharat Innovates 2026 with France's Emmanuel Macron in Nice"
        image_attribution = "Wikimedia Commons"
    else:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Palais des Expositions Nice France",
            ["nice", "palais", "expositions", "france", "building"],
            "The Palais des Expositions in Nice, venue for Bharat Innovates 2026")
        if not image_url:
            image_url, image_caption, image_attribution = pick_commons_image(
                "Narendra Modi Emmanuel Macron",
                ["modi", "macron", "india", "france"],
                "PM Modi and President Macron, who jointly launched Bharat Innovates 2026 in Nice")
        if not image_url:
            px = fetch_pexels_image("startup innovation technology conference")
            if px and validate_image(px):
                image_url, image_caption, image_attribution = px, "A technology and innovation showcase", "Pexels"

    slug = "bharat-innovates-2026-nice-modi-macron-startups-global-investors-20260615"

    body = """India took its startup story to the French Riviera this week, and the message it carried was a deliberate one: the country no longer wants to be seen as the place that consumes the world's technology, but as the place that creates it. Prime Minister Narendra Modi and French President Emmanuel Macron jointly inaugurated Bharat Innovates 2026 at the Palais des Expositions in Nice, launching a three-day conclave that brings 120 Indian deep-tech startups face to face with more than 350 global investors and venture capitalists.

"The question is no longer if India innovates, but who will innovate with India," Macron told the gathering \u2014 a line that captures the ambition behind the event, and one that resonates loudly with an Indian diaspora that has spent decades building other countries' technology.

## What Bharat Innovates Is

Organised by India's Ministry of Education as part of the India-France Year of Innovation, Bharat Innovates is a bilateral technology showcase built as a matchmaking platform for funding, market entry and cross-border technology transfer. The maiden edition, running June 14 to 16, features 120 startups vetted by a Technical Oversight Committee led by India's Principal Scientific Adviser Ajay Kumar Sood, drawn from nearly 3,000 applicants, alongside more than 15 premier institutions including the IITs, IISc and BITS Pilani.

The startups span 13 strategic sectors: advanced computing, semiconductors, space technology, biotechnology, healthcare, energy, advanced manufacturing, defence and climate tech among them. According to a startup compendium released ahead of the event, the featured firms have collectively raised over $1.5 billion, hold more than 1,500 patents, and include two already-listed companies \u2014 drone-maker ideaForge and electric-vehicle firm Ather Energy.

## The Diaspora's Stage

For the global Indian community, the symbolism is hard to miss. Founders from Tier-2 cities described being selected as a point of pride. "Coming from a Tier-2 city like Madurai and being selected for this platform is a matter of pride," said one entrepreneur whose firm is building hydrogen cylinders half the weight and cost of conventional ones. Others spoke of carbon-capture breakthroughs and AI-driven diagnostics built in India and now pitched to the world.

Modi framed the relationship between the two countries as one "driven by shared vision, along with shared interest," and pointed to the transformative potential of AI and satellite technology for rural development, advanced manufacturing for sustainable living, and green hydrogen and battery technologies for clean growth. The event sits alongside Modi's participation in the G7 summit at Evian and the VivaTech showcase in Paris, knitting India's innovation pitch into a broader diplomatic swing through France.

## Why Now

The conclave arrives at a moment when India is consciously trying to move up the technology value chain. For years, the diaspora's role was to staff the engineering teams of American and European giants. Bharat Innovates is an attempt to flip that script \u2014 to position Indian startups not as service providers but as technology contributors and partners, and to route global capital directly into Indian deep tech rather than into the offshore back-offices of foreign firms.

Macron, for his part, praised India's innovation ecosystem and reiterated France's support for the Make in India initiative, pointing to opportunities in artificial intelligence, clean energy, climate solutions and civil nuclear technology, including small modular reactors. Both leaders described innovation and technology as central pillars of the next decade of the India-France partnership.

## Why It Matters to the Diaspora

For NRIs, Bharat Innovates is a tangible bridge between the homeland and the global Indian community that has long been its quiet engine. Many overseas Indians are now venture investors, corporate leaders and researchers \u2014 exactly the audience the event was built to court. A platform that puts 120 vetted Indian startups in front of 350-plus global funds is, in effect, an invitation to the diaspora to back the next generation of Indian companies at the earliest stage.

It also speaks to a shift in identity. The diaspora has historically taken pride in individual success abroad \u2014 the CEO, the unicorn founder, the chip designer. Bharat Innovates offers a different kind of pride: the prospect that India itself becomes the place where breakthrough technology is built, and that overseas Indians can be partners in that creation rather than spectators to it. For a community that has always straddled two worlds, an event that explicitly fuses Indian talent with global capital is exactly the kind of bridge it has been waiting for.

**Sources:** Prime Minister's Office (pmindia.gov.in), The Bridge Chronicle, IANS"""

    article = {
        "headline": "Modi and Macron Just Put 120 Indian Startups in Front of the World's Investors. The Pitch: Innovate With India.",
        "subheadline": "Bharat Innovates 2026 opened in Nice with a deliberate message \u2014 India wants to be seen as a creator of technology, not a consumer of it, and the diaspora is its target audience.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "innovation-economy",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "Many overseas Indians are now venture investors, corporate leaders and researchers \u2014 precisely the audience Bharat Innovates was built to court; the event is in effect an invitation to the diaspora to back the next generation of Indian deep-tech companies at the earliest stage and to be partners in India's rise rather than spectators.",
        "sources": ["Prime Minister's Office (pmindia.gov.in)", "The Bridge Chronicle", "IANS"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# ARTICLE 3: SC stays HC cases on Transgender Amendment Act 2026
# ========================================================================
def write_article_3():
    print("\n" + "=" * 60)
    print("ARTICLE 3: SC stays HC cases on Transgender Amendment Act")
    print("=" * 60)

    image_url, image_caption, image_attribution = pick_commons_image(
        "Supreme Court of India building New Delhi",
        ["supreme court", "india", "new delhi", "court", "building"],
        "The Supreme Court of India, which stayed all High Court challenges to the Transgender Amendment Act 2026")
    if not image_url:
        image_url, image_caption, image_attribution = pick_commons_image(
            "Supreme Court India",
            ["supreme court", "india", "court", "judiciary", "building"],
            "India's Supreme Court will hear the constitutional challenge to the Transgender Amendment Act itself")
    if not image_url:
        px = fetch_pexels_image("courthouse justice law india")
        if px and validate_image(px):
            image_url, image_caption, image_attribution = px, "A courthouse representing the judicial process", "Pexels"

    slug = "supreme-court-stays-high-court-cases-transgender-amendment-act-2026-20260615"

    body = """India's Supreme Court stepped in on Monday to take control of one of the most consequential constitutional fights of the year, staying every High Court proceeding that challenges the Transgender Persons (Protection of Rights) Amendment Act, 2026, and signalling that it may decide the question of who gets to define a person's gender itself.

The move, by a bench led by Chief Justice of India Surya Kant alongside Justice V. Mohana, consolidates a legal battle that strikes at a principle the same court enshrined a decade ago: that a person's right to self-identify their gender is a constitutional guarantee, not a privilege the State can grant or withdraw.

## What the Court Did

The bench was hearing a transfer petition filed by the Union Government, represented by Solicitor General Tushar Mehta, who argued that multiple challenges to the Amendment Act were pending across different High Courts even as the Supreme Court was already examining the law's constitutional validity. "Constitutional validity of a Central Act is challenged, of which Your Lordships are seized," Mehta submitted.

The court issued notice on the transfer plea and ordered that "further proceedings in the High Courts shall remain stayed." The Chief Justice made the reasoning plain: "Better it is that all the matters are taken up. Either we will give it to one High Court or we ourselves will decide instead of having a scattered opinion." Mehta indicated he could persuade the court to place the matter before a three-judge bench, noting that High Courts "may find it difficult to take a view contrary to" the landmark NALSA judgment.

The court declined, however, to stay the legislation itself in the interim \u2014 the Chief Justice had earlier made clear that "there was no question of staying anything."

## The Heart of the Challenge

At issue is the amended definition of "transgender person." Petitioners \u2014 including Laxmi Narayan Tripathi, a prominent transgender-rights activist who was part of the original litigation behind the 2014 NALSA ruling, and a corporate leader on the National Council for Transgender Persons \u2014 argue that the 2026 amendment guts the right to self-identification that the Supreme Court itself recognised.

Filed under Article 32 of the Constitution, the lead petition contends that the amendment inflicts "irreparable constitutional injury" by violating rights under Articles 14, 15, 19 and 21. It poses a single, sharp question: can the State legally define a person's gender identity in place of their own self-perception?

The petitioners say the new law replaces the self-identification standard with a restrictive framework built on biological conditions and socio-cultural categories \u2014 a shift they argue effectively "erases" transgender people who do not fit specified categories such as hijra or intersex persons. They also challenge the amendment's requirement of certification by a medical board before a person can be recognised as transgender, arguing it reintroduces the very "medical gatekeeping" the Supreme Court expressly rejected in 2014.

## Why It Reaches Beyond India's Borders

The case is, on its surface, a domestic constitutional dispute. But its implications travel. India's NALSA judgment is cited around the world as a landmark in transgender rights jurisprudence, and a reversal of its core principle by ordinary legislation would reverberate through the global conversation on gender self-determination.

For the millions of people of Indian origin abroad, the stakes are also personal and practical. Overseas Citizens of India and Persons of Indian Origin who are transgender \u2014 and who travel to India to visit family, marry, or settle \u2014 would face the new regime's documentation and medical-certification requirements. A legal framework that ties gender recognition to a medical board's approval rather than self-perception directly shapes how diaspora transgender individuals navigate Indian institutions, from passports to property to hospitals.

## What Happens Next

By consolidating the challenges, the Supreme Court has set up a single, definitive reckoning rather than a patchwork of conflicting High Court rulings. The bench indicated it would seek the assistance of the petitioners, including a doctor among them whose challenge it called "comprehensive," and left open whether it will refer the matter to a larger three-judge bench. Until it decides, the amended law remains in force even as every lower-court challenge is frozen.

## Why It Matters to the Diaspora

For the Indian diaspora \u2014 and especially its LGBTQ+ members \u2014 the case is a barometer of how the homeland balances legislative power against constitutional rights. Many overseas Indians look to the Supreme Court as the guarantor of the liberal constitutional values that drew global praise after the NALSA and Section 377 judgments. How the court resolves this challenge will tell the diaspora whether those gains are durable or reversible, and will directly affect transgender OCI and PIO holders who must engage with Indian law. In a community that prides itself on India's reputation as a rights-respecting democracy, few cases carry as much symbolic weight.

**Sources:** LawBeat, Bar and Bench"""

    article = {
        "headline": "India's Supreme Court Just Seized Control of the Fight Over Who Can Define a Person's Gender",
        "subheadline": "The court stayed every High Court challenge to the Transgender Amendment Act 2026 and signalled it may decide itself whether the State can override the right to self-identify that it enshrined in 2014.",
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "rights-and-law",
        "status": "review",
        "is_editorial": False,
        "diaspora_angle": "India's NALSA judgment is cited worldwide as a landmark in transgender rights, and transgender OCI/PIO holders who travel to or settle in India would face the new law's medical-certification regime \u2014 so for the diaspora, and especially its LGBTQ+ members, the case is a barometer of whether the homeland's constitutional rights gains are durable or reversible.",
        "sources": ["LawBeat", "Bar and Bench"],
        "published_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return finalize(article, image_url, image_caption, image_attribution)


# ========================================================================
# MAIN
# ========================================================================
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"VIDESHI NEWS WRITER (PM5) \u2014 {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")

    results = []
    results.append(("HCLTech \u00d7 Sarvam AI", write_article_1()))
    results.append(("Bharat Innovates 2026 Nice", write_article_2()))
    results.append(("SC stays Transgender Act HC cases", write_article_3()))

    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        print(f"  {'\u2713 SUCCESS' if success else '\u2717 FAILED'}: {name}")
    print(f"{'='*60}\n")
