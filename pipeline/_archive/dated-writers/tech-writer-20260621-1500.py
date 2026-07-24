#!/usr/bin/env python3
import json, os, uuid, re, io, requests, urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ---- Load env ----
for envname in [".env.supabase"]:
    env_file = Path.home() / envname
    if env_file.exists():
        for line in env_file.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

pex = Path.home() / "workspace" / ".env.pexels"
if pex.exists():
    for line in pex.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

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

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ---- Image helpers ----
def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
                         headers=UA, timeout=10)
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}'")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params, headers=UA, timeout=15)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 400:
                    continue
                results.append({"url": ii.get("thumburl") or ii.get("url", ""),
                                "title": page.get("title", ""), "width": ii.get("width", 0)})
            if results:
                print(f"  \u2713 Commons: {len(results)} for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Commons error '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    import subprocess
    try:
        url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&orientation=landscape"
        out = subprocess.run(["curl", "-sS", url, "-H", f"Authorization: {PEXELS_KEY}"],
                             capture_output=True, text=True, timeout=30).stdout
        data = json.loads(out)
        photos = data.get("photos", [])
        if photos:
            src = photos[0]["src"].get("large2x") or photos[0]["src"].get("large")
            print(f"  \u2713 Pexels for '{query}'")
            return src
    except Exception as e:
        print(f"  \u26a0 Pexels error '{query}': {e}")
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
        f"{SB_URL}/storage/v1/object/article-images/{filename}",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                 "Content-Type": "image/jpeg", "x-upsert": "true"},
        data=jpeg_bytes, timeout=60)
    if r.status_code not in (200, 201):
        print(f"    \u26a0 Supabase upload failed {r.status_code}: {r.text[:200]}")
        return None
    return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"

def download_bytes(url):
    import subprocess
    try:
        r = requests.get(url, headers=UA, timeout=40)
        if r.status_code == 200 and r.content and len(r.content) > 5000:
            return r.content
    except Exception:
        pass
    try:
        out = subprocess.run(["curl", "-sS", "-A", UA["User-Agent"], "-o", "/tmp/_img.bin", url],
                             capture_output=True, timeout=60)
        data = Path("/tmp/_img.bin").read_bytes()
        if len(data) > 5000:
            return data
    except Exception:
        pass
    return None

def source_and_host(slug, person=None, commons_queries=None, pexels_query=None):
    candidates = []
    if person:
        wi = fetch_wikipedia_person_image(person)
        if wi:
            candidates.append((wi, "Wikimedia Commons"))
    for q in (commons_queries or []):
        for r in fetch_wikimedia_commons_images(q)[:2]:
            candidates.append((r["url"], "Wikimedia Commons"))
    if pexels_query:
        px = fetch_pexels_image(pexels_query)
        if px:
            candidates.append((px, "Pexels"))
    for url, attribution in candidates:
        raw = download_bytes(url)
        if not raw:
            continue
        try:
            jpeg = compress_image(raw)
        except Exception as e:
            print(f"    \u26a0 compress failed: {e}")
            continue
        if len(jpeg) < 10000:
            continue
        final = upload_image_to_supabase(jpeg, f"{slug}.jpg")
        if final:
            print(f"  \u2705 hosted image ({attribution}): {final}")
            return final, attribution
    print("  \u26a0 No image hosted \u2014 leaving blank")
    return None, None

# ============ ARTICLES ============
articles_meta = [
    {
        "headline": "Accenture Lost a Fifth of Its Value in a Day. The Tremor Is Already Reaching Bengaluru and New Jersey.",
        "subheadline": "The consulting giant's worst single-day fall ever was triggered by softening demand and the fear that AI is eating billable hours. For the Indians who staff the IT-services machine, the read-across to TCS, Infosys and Cognizant is the real story.",
        "slug_base": "accenture-stock-crash-q3-ai-indian-it-services-tcs-infosys-cognizant-nri",
        "diaspora_angle": "Indian-origin technologists are the backbone of the global IT-services trade \u2014 in Accenture's and Cognizant's American offices on H-1B visas, in the Bengaluru, Hyderabad and Pune delivery centres that feed them, and in the Indian-listed giants TCS, Infosys and Wipro that report results in July. When the sector's bellwether warns of weakening demand, it is their job security and their next visa renewal on the line.",
        "tags": ["accenture", "it-services", "ai", "tcs", "infosys", "cognizant", "h1b"],
        "urgency": "high",
        "score_total": 84,
        "vertical": "tech",
        "sources": [
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/accenture-stock-acn-fiscal-q3-2026-earnings/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/accenture-stock-price-earnings-worst-day"},
            {"name": "Stocktwits", "url": "https://stocktwits.com/news-articles/markets/equity/accenture-acn-stock-q3-earnings-bookings-guidance"},
        ],
        "image": {"person": None,
                  "commons": ["Accenture office building", "Accenture logo building"],
                  "pexels": "modern corporate office glass tower"},
        "image_caption": "Accenture's shares suffered their worst single-day drop on record after weak bookings and a lowered forecast",
        "image_attribution": "Pexels",
        "body": """Accenture is not a household name in the way Apple or Google are, but for the global business of Indian technology it is something more important: a barometer. So when its shares fell almost 18% on June 18th \u2014 the worst single-day drop in the company's history, lopping roughly $28 off a stock that opened near $156 \u2014 the tremor was felt well beyond Dublin, where the firm is incorporated, and well beyond the Wall Street desks that dumped it. It was felt in Bengaluru, in Hyderabad, and in the New Jersey and Texas offices where hundreds of thousands of Indian engineers turn corporate IT budgets into pay cheques.

The numbers themselves were not catastrophic. Third-quarter revenue came in at $18.72 billion, up 6% on the year and only a rounding error below estimates. Earnings of $3.80 a share actually beat expectations. What spooked investors was everything pointing forward. New bookings \u2014 the pipeline of future work \u2014 fell to $19.32 billion, down from a year earlier and well short of the roughly $20.6 billion analysts wanted. The company trimmed the top of its full-year revenue forecast to 3\u20134% growth, and guided the current quarter to a range whose midpoint implies revenue actually shrinking from last year.

## The fear beneath the figures

The deeper anxiety is structural, and it has a three-letter name: AI. Roughly half of Accenture's revenue comes from consulting \u2014 the labour-intensive work of helping big companies build software and stitch their systems together. That is precisely the kind of work that AI coding tools threaten to do faster and with fewer billable hours. Accenture's consulting revenue grew just 1% in local-currency terms last quarter, giving the bears something concrete to point at.

Chief executive Julie Sweet insists the opposite is true \u2014 that helping enterprises actually deploy AI is messy, expensive work that Accenture is well placed to sell. She also acknowledged a more immediate drag: the conflict in the Middle East has disrupted business in the region and, more broadly, spooked corporate clients into tightening their wallets. Wall Street was unconvinced. Morgan Stanley had already downgraded the stock days earlier, warning that massive AI investments were draining resources from traditional IT services; William Blair followed, citing "weakening forward demand." The stock is now down roughly half from where it started the year and trades at a price-to-earnings ratio of about 11, a level it has not seen in years.

## Why the diaspora should read past the ticker

For the Indian technologist, Accenture's miss is less an investment story than a weather report. The same chill that hit Accenture rolled straight through its peers on the day: Cognizant fell around 9%, Infosys's American shares dropped about 8%, and Wipro slid too. These are not abstractions \u2014 they are among the largest employers of Indian talent on either side of the Pacific. Cognizant alone has built much of its business on bringing Indian engineers to American clients, a model the sector has run for two decades.

And the timing is pointed. India's listed IT champions \u2014 Tata Consultancy Services, Infosys, HCLTech and Wipro \u2014 report their own June-quarter results in July. Accenture, whose fiscal calendar runs ahead of theirs, is traditionally read as a preview. A weak Accenture print has historically foreshadowed cautious guidance from the Indian majors, and this one lands amid a broader reckoning: TCS and Wipro have both struck deals with Anthropic this month, racing to show clients they can deliver AI rather than be displaced by it.

## The two clocks

For an H-1B holder at Cognizant or Accenture in the United States, two clocks now tick in uncomfortable sync. One is the demand cycle \u2014 fewer signed deals can mean fewer staffed seats, and the IT-services model has thin room for idle benches. The other is the immigration clock, which runs on its own merciless schedule should a role disappear. The sector that carried a generation of Indian families into the American middle class is being asked, in real time, to prove it adds value that software cannot replicate.

None of this means the machine is breaking. Accenture still generated $12.5 billion in trailing free cash flow, up 28% on the year, and a P/E of 11 for a profitable market leader strikes some analysts as a buying opportunity rather than a death knell. But the market has decided, for now, to treat the AI threat to consulting as real until proven otherwise. For the people who do the work \u2014 in Bengaluru's tech parks and in offices from Dallas to Edison \u2014 the safest posture is the oldest one: keep the skills current, keep the network warm, and watch the bookings line as closely as the share price."""
    },
    {
        "headline": "Mukesh Ambani Just Filed the Paperwork for India's Biggest IPO Ever. The NRI Question Is Whether to Believe the $180 Billion Price Tag.",
        "subheadline": "Jio Platforms, the telecom-and-tech engine inside Reliance, has approved its draft prospectus for a listing brokerages value near $180 billion. For diaspora investors who have watched India's IPO boom from afar, this is the one they will actually be able to buy.",
        "slug_base": "jio-platforms-ipo-drhp-reliance-ambani-180-billion-nri-investors",
        "diaspora_angle": "Jio is the company that put a cheap smartphone and a data connection in the hands of nearly every relative back home; for NRIs it is both a daily touchstone and, soon, the most accessible bet on India's digital decade. A listing this size sets the benchmark against which every other Indian tech IPO \u2014 the ones diaspora money has been quietly chasing \u2014 will be measured.",
        "tags": ["reliance-jio", "ipo", "mukesh-ambani", "telecom", "nri-investors"],
        "urgency": "high",
        "score_total": 82,
        "vertical": "economy",
        "sources": [
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/companies/reliance-jio-board-approves-drhp-for-ipo-before-sebi-on-june-19/article69711000.ece"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/markets/reliance-jio-set-to-file-ipo-papers-today-says-mukesh-ambani"},
            {"name": "Exchange4media", "url": "https://www.exchange4media.com/digital-news/reliance-agm-2026-jio-ipo-prospectus-to-be-filed-today-137000.html"},
        ],
        "image": {"person": "Mukesh Ambani",
                  "commons": ["Mukesh Ambani", "Reliance Jio store India"],
                  "pexels": "mumbai stock exchange skyline india"},
        "image_caption": "Mukesh Ambani told Reliance's 49th AGM that the Jio listing would show India can build technology companies of global scale",
        "image_attribution": "Wikimedia Commons",
        "body": """It was, in Mukesh Ambani's own words, a "deeply emotional" moment. Speaking to shareholders at Reliance Industries' 49th annual general meeting on June 19th, the chairman announced that the board of Jio Platforms had approved its Draft Red Herring Prospectus \u2014 the formal first step toward a stock-market listing \u2014 and would file it with India's market regulator that same day. After years of speculation, the largest IPO in Indian corporate history is now officially in motion.

The scale is hard to overstate. Brokerages peg Jio Platforms' value at around $180 billion, with estimates running from roughly $130 billion to $182 billion. The offering itself is a fresh issue of up to 27 crore (270 million) new shares, with the company expected to raise somewhere between $4 billion and $4.5 billion. Notably, there is no offer-for-sale component \u2014 the part where existing backers cash out \u2014 reportedly because investors could not agree on a valuation for it. That detail matters: it means every rupee raised flows into Jio rather than into the pockets of early shareholders.

## What you are actually buying

Jio is not just a phone network, though it is the country's largest, having migrated hundreds of millions of Indians onto cheap 4G and now 5G over the past decade. It is the digital spine of Reliance's consumer empire \u2014 telecom, broadband, a sprawling apps business, and increasingly an artificial-intelligence ambition that Ambani has placed at the centre of his pitch. India, he told the meeting, "should be a creator of AI and not a mere consumer." Akash Ambani, who chairs the telecom arm, laid out plans to move every Jio subscriber to its top-tier 5G by 2030 and to build toward 6G.

The financials underpinning the story are solid rather than spectacular. For the year to March 2026, Jio Platforms posted profit up 15% to roughly \u20b930,053 crore on revenue up about 14.5% to \u20b91,46,885 crore. Ambani also flagged a striking data point: Jio leapt from a global patent-innovation rank of 340 to 20 in a single year, by one international measure \u2014 the only Indian company in that top tier.

## The mechanics that make it possible

A mega-listing of this size was, until recently, awkward under Indian rules that forced large companies to float a meaningful slice of equity. A regulatory change in March 2026 eased that: companies with a post-issue market value above \u20b95 lakh crore can now offer as little as 2.5% of their shares to the public. That tweak is what allows Reliance to put a colossal valuation on the market while diluting only a sliver of ownership \u2014 and to keep the family firmly in control. Fittingly, the listing process is being led by the next generation: Isha, Akash and Anant Ambani.

## Why this is the diaspora's IPO

For non-resident Indians, the Jio listing carries a resonance that a typical Indian IPO does not. This is the company whose SIM card sits in the phone of nearly every relative back home, whose data plans rewired how families stay in touch across oceans, and whose apps stream the cricket and the cinema that knit the diaspora to India. Owning a piece of it is, for many, less a financial decision than an emotional one \u2014 which is precisely the kind of sentiment that can push a hot listing's price past what the fundamentals justify.

A note of discipline is therefore in order. NRIs can participate in Indian IPOs, but the routes are specific \u2014 through an NRE or NRO account and the right category of application \u2014 and the rules on repatriation differ depending on which one is used. More importantly, a $180 billion valuation is a demanding one. It prices Jio not as a mature telecom utility but as a high-growth technology platform, and it leaves little margin for the AI bets to disappoint. The recently dropped offer-for-sale, and the haggling over valuation that reportedly killed it, are a quiet reminder that even sophisticated insiders disagree on what this company is worth.

Ambani framed the listing as proof that "India can build technology companies of global scale, global capability and global value." He is almost certainly right that it is a milestone for Indian capitalism. Whether it is a milestone for any individual portfolio is a separate question \u2014 and one each investor, here or abroad, will have to answer with a cooler head than the occasion invites. The draft prospectus is filed; the harder reading begins now."""
    },
    {
        "headline": "A Judge Killed Trump's $100,000 H-1B Fee. Four Days Later, It Was Back. Welcome to the Whiplash.",
        "subheadline": "A Boston court vacated the six-figure visa charge as an unlawful tax \u2014 then paused its own ruling pending appeal. For the Indian engineers and students who make up most of the H-1B pool, the lesson is that the uncertainty itself has become the policy.",
        "slug_base": "h1b-100000-fee-struck-down-stayed-appeal-indian-tech-workers-nri",
        "diaspora_angle": "Indians account for roughly 71% of approved H-1B visas \u2014 the single largest group by far \u2014 so any swing in the program's cost or legality lands hardest on Indian engineers, doctors and graduate students. The on-again, off-again fight over a $100,000 fee has turned career and family planning into a guessing game for the very people the diaspora pipeline depends on.",
        "tags": ["h1b", "immigration", "visa", "indian-tech-workers", "trump"],
        "urgency": "high",
        "score_total": 80,
        "vertical": "tech",
        "sources": [
            {"name": "SHRM", "url": "https://www.shrm.org/topics-tools/employment-law-compliance/federal-court-strikes-down-100k-h1b-fee"},
            {"name": "Bloomberg Tax", "url": "https://news.bloombergtax.com/daily-tax-report/dhs-says-trump-h-1b-fee-isnt-a-tax-should-continue-on-appeal"},
            {"name": "Associated Press via Montana Public Radio", "url": "https://www.mtpr.org/2026-06-08/federal-judge-strikes-down-trumps-100000-fee-on-new-h-1b-visas"},
        ],
        "image": {"person": None,
                  "commons": ["United States visa passport", "H-1B visa document", "US immigration visa stamp"],
                  "pexels": "passport visa immigration document desk"},
        "image_caption": "The fate of the $100,000 H-1B fee now rests with a federal appeals court in Boston",
        "image_attribution": "Pexels",
        "body": """For a few days in June, hundreds of thousands of Indian technology workers got to exhale. On June 8th, a federal judge in Boston struck down the Trump administration's $100,000 fee on new H-1B visas, calling it exactly what its critics had argued it was: an unlawful tax that the president had no authority to impose without Congress. Four days later, the same judge paused his own ruling. The fee, for now, lives on. If that sequence reads like whiplash, that is because it is \u2014 and the whiplash, more than any single ruling, is now the thing reshaping how Indians plan their American lives.

## How the fee landed, and how it fell

The charge began with a presidential proclamation in September 2025, which slapped a $100,000 price tag on new H-1B petitions \u2014 a roughly twenty-fold jump from the few thousand dollars employers typically paid. The administration cast it as a tool to stop companies from using the visa to "replace, rather than supplement, American workers." The effect was immediate and chilling: by mid-February, only 85 of the six-figure payments had actually been made, court filings showed, as employers froze hiring and confused workers scrambled for advice.

Twenty Democratic state attorneys general, led by California, sued. U.S. District Judge Leo Sorokin \u2014 an Obama appointee \u2014 agreed with them. "The substance and application of the $100,000 payment reveal that it is a tax, regardless of what the payment is called," he wrote, vacating the fee in its entirety and citing the Supreme Court's February ruling that struck down the president's emergency tariffs on similar reasoning: the executive cannot tax by decree.

## And how it came back

The relief lasted barely a long weekend. On June 12th Sorokin agreed to stay his own decision while a higher court weighs the matter, and on the following Thursday the Department of Homeland Security filed with the U.S. Court of Appeals for the First Circuit, arguing the fee is not a tax at all and falls squarely within the president's power to restrict entries he deems "detrimental" to the country. "Every day that passes more aliens can petition and enter the country," the department warned, asking to keep collecting the fee during the appeal. The White House says it is confident the ruling will be reversed.

To complicate matters further, this is only one of at least three lawsuits. The U.S. Chamber of Commerce is fighting the fee in the D.C. Circuit; religious and labour groups have sued in Northern California. With three appellate circuits potentially issuing conflicting rulings, the dispute looks destined for the Supreme Court \u2014 unless the fee simply expires, as scheduled, in September 2026 before the courts finish.

## Why Indians are the story

No group has more at stake. Indians have accounted for roughly 71% of approved H-1B beneficiaries in recent years \u2014 not a plurality but an overwhelming majority. The visa is the workhorse that carries Indian software engineers into Silicon Valley, Indian doctors into rural American hospitals, and Indian graduate students from campus into careers. A $100,000 toll does not merely raise costs; it functionally prices out start-ups, hospitals and smaller employers that cannot absorb it, while leaving the trillion-dollar tech giants relatively unbothered. Analysts have warned it could push research and engineering jobs out of the United States and toward Toronto, London and Bengaluru.

For the individual, though, the deeper damage is not the dollar figure but the unpredictability. An engineer weighing a job change, a student deciding whether to bank on the H-1B lottery after graduation, a family debating whether to buy a house \u2014 all of them now make those decisions against a rule that was law, then wasn't, then was again, all inside a single fortnight. As one think-tank report on the saga put it, the volatility has become a greater concern than the fee itself.

## The practical read

Until the First Circuit rules, the fee technically applies to new petitions requiring consular processing \u2014 but its survival is genuinely uncertain, and existing visa holders were never subject to it. For Indians already in the United States on H-1B status, the immediate situation is unchanged; the fight is over new entrants. The sensible posture is the one the diaspora has been forced to adopt repeatedly over the past year: assume nothing is settled, keep documentation airtight, build relationships with employers large enough to weather the cost, and treat every headline as provisional. In American immigration policy right now, the only reliable constant is that today's ruling may not survive the week."""
    },
]

# ============ INSERT ============
inserted = []
for meta in articles_meta:
    print(f"\n=== {meta['headline'][:70]} ===")
    slug = make_slug(meta["slug_base"])
    img = meta.get("image", {})
    image_url, attribution = source_and_host(
        slug,
        person=img.get("person"),
        commons_queries=img.get("commons"),
        pexels_query=img.get("pexels"),
    )
    if not attribution:
        attribution = meta.get("image_attribution", "")

    record = {
        "id": str(uuid.uuid4()),
        "headline": meta["headline"],
        "subheadline": meta["subheadline"],
        "slug": slug,
        "body": meta["body"],
        "category": "technology",
        "vertical": meta["vertical"],
        "tags": meta["tags"],
        "diaspora_angle": meta["diaspora_angle"],
        "sources": json.dumps(meta["sources"]),
        "urgency": meta["urgency"],
        "score_total": meta["score_total"],
        "is_editorial": False,
        "status": "review",
        "published_at": now,
    }
    if image_url:
        record["image_url"] = image_url
        record["image_caption"] = meta["image_caption"]
        record["image_attribution"] = attribution
    try:
        res = sb_post("p2_articles", record)
        wc = len(meta["body"].split())
        print(f"  \u2705 inserted ({wc} words) slug={slug} img={'yes' if image_url else 'NO'}")
        inserted.append((meta["headline"], slug, image_url is not None, wc))
    except Exception as e:
        print(f"  \u274c insert failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"     {e.response.text[:400]}")

print("\n========== SUMMARY ==========")
for h, s, has_img, wc in inserted:
    print(f"  [{wc}w] {'IMG' if has_img else '\u2014  '} {h[:60]}")
    print(f"        slug: {s}")
print(f"\n  {len(inserted)}/{len(articles_meta)} articles inserted.")
