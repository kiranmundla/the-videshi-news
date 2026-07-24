#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
    env_file = Path.home() / "workspace" / ".env.supabase"
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

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Meta Just Made a CRED Founder the Boss of WhatsApp. The Real Prize Is the 500 Million Indians Who Already Live There.",
        "subheadline": "Kunal Shah, who built CRED into India's slickest fintech, takes over the world's biggest messaging app alongside Meta's $900 million bet on his company. The job is to finally make WhatsApp pay — and India is the test lab.",
        "slug": make_slug("kunal-shah-whatsapp-meta-cred-900-million-payments-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Most NRIs run their entire Indian lives through WhatsApp — family groups, the neighbourhood kirana, airline alerts — so a payments-and-commerce overhaul led by a founder who understands Indian consumer behaviour will reshape how the diaspora moves money and shops across borders.",
        "tags": ["whatsapp", "meta", "cred", "kunal-shah", "fintech", "indian-tech", "upi"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/whatsapps-pick-indian-fintech-founder-signals-scale-payment-ambitions-2026-06-23/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/kunal-shah-to-lead-whatsapp-as-meta-pumps-900-mn-into-cred/article.ece"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/start-up/900-mn-founder-shift-and-payments-gap-what-metas-cred-deal-is-really-about"},
            {"name": "TechRepublic", "url": "https://www.techrepublic.com/article/news-meta-cred-investment-whatsapp/"}
        ]),
        "score_total": 86,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/83/Kunal_Shah_in_FreeCharge_T-Shirt_%28cropped%29.jpg",
        "image_caption": "Kunal Shah, CRED founder and the incoming global head of WhatsApp.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Kunal Shah does not have an engineering degree, never worked at a Silicon Valley giant, and built his career almost entirely inside India. On Monday, Meta handed him the keys to the world's largest messaging platform.

The 47-year-old founder of CRED will become the global head of WhatsApp, succeeding Will Cathcart. The appointment arrived bundled with a $900 million Meta investment in CRED itself, the Bengaluru credit-card and payments company Shah started in 2018. The deal hands Meta roughly a 20% stake and values CRED at about $4.5 billion — a recovery from the $3.5 billion trough it slid to after the 2022 funding boom faded, though still short of its $6.4 billion peak.

For a company that usually promotes from its engineering bench, the choice is revealing. Chief Product Officer Chris Cox, in an internal memo, said Meta wanted a leader with "an intuitive grasp of the immense, global product potential for WhatsApp." Translated: Meta has given up trying to make WhatsApp pay using the playbook that built Facebook and Instagram, and is betting instead on someone who understands how Indians actually use their phones to move money.

## The problem Shah is hired to solve

WhatsApp's scale is not the issue. India alone has more than 500 million users, making it the app's single largest market. Businesses there already run customer service, order updates, and "Click-to-WhatsApp" ad campaigns through it. The trouble is the last step. As one widely shared observation from an Indian marketer put it, you can do almost everything with a brand on WhatsApp — except actually pay. That final tap still happens on Google Pay or PhonePe, the two apps that together dominate India's UPI rails.

That is the gap Meta is paying nine figures to close. Industry analysts expect India to be the primary laboratory. "His role will be to monetise WhatsApp globally, and India will be where most of the experimentation will happen," said Satish Meena of Datum Intelligence. CRED already processes more than 40% of India's credit-card bill payments and runs a lending book with $2.5 billion in assets across 17 million monthly active users. Shah's instinct for high-trust, high-engagement consumer finance is precisely what WhatsApp's commerce ambitions have lacked.

## Why the diaspora should pay attention

For Indian Americans, this is not abstract platform strategy — it touches the app they open most. The NRI relationship with India runs through WhatsApp: the family group that never sleeps, the property manager in Pune, the jeweller in Surat, the parents' pharmacy. If WhatsApp becomes a genuine payments and commerce layer, the friction of sending money home, paying an Indian vendor, or buying from a small Indian seller could collapse into the same thread where the conversation already happens.

There is a competitive subtext too. Meta now holds a stake in CRED, one of India's top-ten UPI providers, giving it a foothold in a market that PhonePe and Google Pay have locked down. A more aggressive WhatsApp Pay backed by Shah's commerce instincts could reshape the duopoly — and the diaspora, which sends tens of billions of dollars in remittances to India each year, sits squarely in the path of whatever payments rails win.

Shah is keeping his roughly 20% CRED stake but stepping away from operations; chief financial officer Miten Sampat takes over as interim CEO as the company prepares for an eventual IPO. Notably, Meta says it gets no access to CRED's customer data despite the investment — a guardrail Shah was careful to emphasise.

## What's next

Shah will start from India and travel before eventually basing himself at Meta's Menlo Park headquarters. Expect the first visible experiments — richer business messaging, in-chat payments, commerce tools — to debut in India before anywhere else.

The bet is straightforward and risky in equal measure. Meta has the world's most-used app and has never figured out how to make it earn its keep. It just put an Indian founder, steeped in the world's most sophisticated retail-payments market, in charge of solving that. For the diaspora, the experiment will play out first in the one app they can't quit."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Hackers Dumped 630GB From the Factory That Builds a Third of India's iPhones. Apple and Tesla's Secrets Were Inside.",
        "subheadline": "Tata Electronics confirmed a ransomware breach after the group World Leaks posted more than 200,000 stolen files — including documents marked as Apple and Tesla trade secrets — on the dark web.",
        "slug": make_slug("tata-electronics-ransomware-breach-apple-tesla-world-leaks-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "India's pitch to the diaspora and the world is that it can be a trusted alternative to China for building Apple iPhones and Tesla parts — and a 630GB leak of client trade secrets from Tata's flagship plant strikes directly at that promise, with the careers and reputations of Indian engineers riding on it.",
        "tags": ["cybersecurity", "tata-electronics", "apple", "tesla", "ransomware", "iphone", "india-manufacturing"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-tata-electronics-hit-by-cyber-breach-claiming-expose-apple-tesla-trade-2026-06-23/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/tata-electronics-hit-by-ransomware-attack-claiming-to-expose-apple-tesla-trade-secrets/article.ece"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/tata-electronics-confirms-ransomware-attack-as-leaked-data-purportedly-links-to-apple-tesla"},
            {"name": "MacRumors", "url": "https://www.macrumors.com/2026/06/23/apple-files-leaked-dark-web-supplier-cyberattack/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/60504/security-protection-anti-virus-software-60504.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A cursor hovers over digital security software, illustrating the dark-web data leak.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """Tata Electronics has confirmed a cybersecurity breach after a ransomware group claimed to have published more than 200,000 of the company's files — over 630 gigabytes of data — on the dark web. Among the trove, security researchers say, are documents bearing the proprietary markings of two of Tata's most important customers: Apple and Tesla.

The company that broke the news to itself was sparing. "A few weeks ago, Tata Electronics identified a cybersecurity incident on some of our systems. Our response protocols were deployed immediately, and the incident has had no impact on our operations," it told Reuters. What it did not say is more interesting than what it did.

## What's in the dump

The group claiming responsibility, World Leaks — which has previously taken credit for a hack of Nike — posted the data on a dark-web site reachable only outside ordinary search engines. Two Indian cybersecurity researchers who reviewed the files for Reuters, Rajshekhar Rajaharia and Rakesh Krishnan, say the material has been sitting online since at least June 10.

A search for "Apple" in the cache reportedly returned 181 files and folders, including one labelled "com.apple.factorydata" and a 52-page document carrying Apple's confidential markings that purportedly details quality-inspection standards for iPhone circuit boards. There were 33 files and folders matching "Hosur" — the Tamil Nadu town where Tata runs its main iPhone assembly plant. The Tesla material is, if anything, more sensitive: a folder titled "NV36 Chargeport Controller — North America," tied to an upgraded Model Y, and a 2023 document marked "TRADE SECRET" showing drawings for Tesla's "Project Highland," the codename for its revamped Model 3. Some files carried footers explicitly claiming Apple or Tesla confidentiality.

Also in the leak, according to Rajaharia: employee emails, years of event logs, and passport copies of staff — including foreign nationals. Tata is believed to have received a ransom demand. Apple says it is investigating; a "full analysis" is underway. Neither Apple nor Tesla has commented publicly, and Reuters could not independently verify the documents' authenticity.

## Why this lands harder than a typical breach

Tata Electronics is not a peripheral vendor. It builds roughly a third of all iPhones made in India — Foxconn makes the rest — after absorbing Wistron's India operations and taking a majority stake in Pegatron's Chennai plant. It makes parts for Tesla. It has signed partnerships with Intel, Qualcomm, and ASML. In short, it is the corporate embodiment of India's argument that it can be the "China plus one" the West has been looking for.

That argument rests on trust. When Apple or Tesla moves sensitive production to India, it is wagering that Indian suppliers can protect intellectual property as well as anyone in Shenzhen or Taipei. A 630GB spill of component specs and trade-secret drawings — whatever its ultimate authenticity — is exactly the headline that rivals and skeptics will wave around. It also lands while Tata is already managing a separate health probe over alleged farmland contamination near one of its parts plants.

## The diaspora stake

For Indian Americans, the breach cuts two ways. Many work inside Apple's and Tesla's supply-chain and security teams, and a leak of this scale becomes their problem to contain. Thousands more — engineers, quality managers, plant staff — power the India operations whose reputation is now under a cloud, with employee passports reportedly among the stolen files.

More broadly, the diaspora has a rooting interest in India's manufacturing rise succeeding cleanly. Every NRI who has argued at a dinner table that India can build world-class hardware just watched that case take a hit. Whether it proves a one-off operational failure or a sign that India's electronics boom has outrun its cybersecurity will shape how confidently Apple, Tesla, and the next entrant deepen their India bets — and how many jobs follow.

## What's next

Expect Apple's forensic review to drive the story from here; its conclusions on what was genuinely exposed will matter more than the group's boasts. Tata, for its part, will need to show customers and the Indian government that this was contained — and that the country's marquee electronics champion can be trusted with the world's most valuable secrets."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's First Big Chip Plant Promises 48 Million Units Out of Assam by November. The Map Just Moved East.",
        "subheadline": "Tata Semiconductor's packaging facility in Guwahati is on track to begin exports this year, a tangible milestone for the India Semiconductor Mission as TSMC publicly backs the country's ambitions at a Bengaluru summit.",
        "slug": make_slug("tata-semiconductor-guwahati-chip-exports-india-mission-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-origin semiconductor professionals across the Bay Area and Austin have spent years asking whether India's chip mission would ever ship a real product — and the first commercial output from an Assam plant turns a slogan into a supply chain they may one day return to or invest in.",
        "tags": ["semiconductor", "tata-electronics", "india-semiconductor-mission", "assam", "chips", "tsmc", "make-in-india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/tata-semiconductor-to-export-48m-chips-from-guwahati-by-november/"},
            {"name": "Communications Today (TSMC at ISPAC)", "url": "https://www.communicationstoday.co.in/tsmc-backs-indias-semiconductor-ambitions-at-bengaluru-summit/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy-and-policy/four-chip-plants-to-start-full-scale-production-from-2026-says-vaishnaw"},
            {"name": "YourStory", "url": "https://yourstory.com/2026/01/outlook-2026-india-semiconductor-push-capacity-buyers-supply-chains"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/28215391/pexels-photo-28215391.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A close-up of a patterned silicon wafer, the building block of semiconductor production.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """For years, India's semiconductor ambition has been measured in approvals, ground-breakings, and ministerial promises. This week it got a date and a number. Tata Semiconductor's facility in Guwahati, Assam, is on track to begin chip exports by November, with an initial output target of 48 million units, the state's chief minister Himanta Biswa Sarma said at the Republic Summit in New Delhi.

The plant is an assembly, testing, marking, and packaging (ATMP) facility — the less glamorous but essential back end of chipmaking, where wafers fabricated elsewhere are cut, packaged, and tested before going into cars, appliances, and industrial electronics. It is not a fab spinning out advanced logic chips. But it is real product, leaving an Indian factory, on a clock.

## A milestone, with the usual asterisks

Union electronics minister Ashwini Vaishnaw has said four units — Micron, Tata, CG Semi, and one other — would move beyond trial runs to large-scale manufacturing in 2026. The Guwahati timeline gives that claim a concrete first data point. Industry advisers have been candid that packaging plants, not fabs, would lead. As Jaswinder Ahuja of the India Semiconductor Mission's advisory committee put it, "at least one of these ATMP facilities will go into commercial production next year." Actual wafer fabrication — the capital-hungry, technically brutal part dominated globally by TSMC, Samsung, and Global Foundries — is still a 2027-or-later story. Tata's Dholera fab, built with Taiwan's Powerchip, sits in that longer queue, and Micron's Gujarat facility has slipped amid construction delays.

The external validation arrived almost on cue. At the India Semiconductor and Packaging Conference in Bengaluru, a senior TSMC executive called India "a strategic contributor" to a global chip industry the company expects to exceed $1.5 trillion by 2030, with AI and high-performance computing driving more than half of that. For a country that has watched the world's largest chipmaker build its empire in Taiwan and Arizona, even a rhetorical endorsement carries weight.

## Why "east" matters

The geography is part of the story. Assam's chief minister framed the plant as proof that India's northeast — long defined by insurgency and underdevelopment — can host advanced manufacturing. "Assam has shed its legacy of insurgency to emerge as an upcoming semiconductor hub," Sarma said, tying it to the government's "Viksit Bharat 2047" roadmap. Whether the rhetoric outruns the reality, the investment is genuinely pushing chip jobs beyond the usual Gujarat-Bengaluru-Hyderabad triangle.

## The diaspora angle

Few communities have watched India's chip saga more closely, or more skeptically, than the Indian-origin engineers who staff the semiconductor industry in the United States. Walk the halls at NVIDIA, Intel, Qualcomm, AMD, or Applied Materials and you will find Indians at every level, many of whom have heard "India will build chips" promised for two decades. A facility actually exporting 48 million units changes the conversation from aspiration to supply chain.

That matters in three concrete ways. First, return-to-India calculations: a maturing domestic industry gives senior diaspora professionals a credible reason to consider roles back home, the way India's IT and now AI sectors did before. Second, investment: NRIs tracking Tata Group, Micron, and the broader Make-in-India electronics push now have a milestone to price in rather than a press release. Third, the strategic picture — as Washington and Beijing wage a chip war and companies hunt for supply outside China, India's progress, however incremental, expands where Indian engineers can build and where capital can flow.

## What's next

The honest read is that India is winning the easy half of the race first. Packaging and assembly are real, valuable, and job-creating — but they are not the same as fabricating leading-edge silicon, and the gap between an ATMP plant in Guwahati and a working fab in Dholera is measured in years and tens of billions of dollars. Watch two things through the rest of 2026: whether Micron and CG Semi hit their own commercial-production targets, and whether Tata's Dholera fab stays on its 2027 trajectory. The Guwahati shipments are the proof of concept. The fab is the real test."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")

print(f"\n{len(inserted)}/{len(articles)} inserted")
for h in inserted:
    print(" -", h)
