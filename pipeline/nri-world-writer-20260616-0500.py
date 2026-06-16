#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
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

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Forbes Counted America's 250 Most Successful Immigrants. Twenty-Six of Them Are Indian.",
        "subheadline": "As the United States nears its 250th birthday, the list reads like a roll call of who actually runs Silicon Valley — and a quiet rebuttal to the politics of the moment.",
        "slug": make_slug("forbes-2026-250-greatest-immigrants-26-indian-origin-leaders"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "More than one in ten of the most successful living immigrants in the US are of Indian origin — a measure of how far the diaspora has traveled from student visas to the C-suite, and of what is at stake as immigration politics hardens.",
        "tags": ["nri", "diaspora", "forbes", "indian-american", "tech", "business"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "India-West", "url": "https://indiawest.com/forbes-2026-honors-26-indian-origin-leaders/"},
            {"name": "Forbes", "url": "https://www.forbes.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg/1280px-MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "image_caption": "Microsoft chief executive Satya Nadella, one of 26 Indian-origin leaders named to Forbes' 2026 list of America's greatest living immigrants.",
        "image_attribution": "Wikimedia Commons",
        "body": """Forbes set out to name the 250 most successful living immigrants in the United States, timed to the country's 250th anniversary. Twenty-six of them — better than one in ten — trace their roots to India.

It is a number worth sitting with. The Indian-born population of the United States is roughly 2.7 million, a little under one percent of the country. On a list meant to capture the immigrants who have most shaped American business, science, and public life, that sliver of the population claimed more than a tenth of the seats.

## The usual suspects, and then some

The marquee names are the ones the diaspora has long pointed to with a certain proprietary pride. Satya Nadella, who turned Microsoft from a stalling software giant into a cloud-and-AI powerhouse. Sundar Pichai, who runs Alphabet. Arvind Krishna at IBM, Shantanu Narayen at Adobe, Nikesh Arora at Palo Alto Networks, Sanjay Mehrotra at Micron. Between them, these men preside over companies worth several trillion dollars and a meaningful share of the infrastructure the modern internet runs on.

But the list goes deeper than the chief executives whose faces appear on conference stages. Forbes also named Vinod Khosla, the venture capitalist who has bankrolled a generation of startups; Indra Nooyi, the former PepsiCo chair who remains one of the most cited role models in corporate India and its diaspora; and Abhijit Banerjee, the Nobel laureate economist. There are founders most Americans have never heard of but whose work they touch daily: Jyoti Bansal, who built the software-monitoring firm AppDynamics; Neha Narkhede, a co-creator of the data pipeline Apache Kafka; Aman Narang of the restaurant-software company Toast.

And there are the quieter categories — philanthropy, media, healthcare, aviation. Neerja Sethi, the IT-services billionaire and donor. Padma Lakshmi, the author and television host. Rakesh Gangwal, who co-founded the airline that became India's largest. Romesh Wadhwani and Kavitark Ram Shriram, whose names now adorn buildings on American campuses.

## What the list actually measures

It is tempting to read a ranking like this as a feel-good story, and the diaspora press has duly read it that way. But the more interesting fact is structural. The Indian-American community is the most educated and among the highest-earning of any group in the United States; roughly four in five hold a bachelor's degree or more. The pipeline that produced these 26 names — top engineering schools in India, graduate programs in America, and then the long climb through corporate and venture hierarchies — has been running for four decades. The Forbes list is, in effect, that pipeline's output finally cashed out at the very top.

It also lands at an awkward political moment. The same year Forbes celebrated immigrant achievement, the cost of an H-1B petition for some new hires climbed to six figures, student-visa denials hit a decade high, and Indian enrollment at American universities fell nearly seven percent — the sharpest drop in a decade. The men and women on this list arrived, for the most part, in an era when the door swung more freely. Whether the next Nadella or Narkhede chooses America at all is now an open question, and one that university recruiters and immigration lawyers are watching with visible anxiety.

## A mirror the diaspora likes

For the community itself, the list functions as a kind of mirror — and the diaspora rarely tires of looking. Indian-American media outlets reproduced the names in full within hours, organizations issued congratulations, and the usual debate resurfaced about whether such lists flatter a thin elite while ignoring the taxi drivers, motel owners, and small-shop families who make up the broader population.

Both things are true. The 26 names are genuinely exceptional, and they are not representative. What they do capture is the distance the community has traveled in a single working lifetime: from a population that was, in the 1970s, small enough to fit into a handful of professional associations, to one that now supplies a measurable fraction of the people Forbes deems essential to the American century's next chapter.

The United States is about to mark 250 years. On the evidence of this list, a good deal of its recent reinvention was carried out by people who were not born here — and a striking number of them were born in India."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The RBI Just Made Parking Dollars in India Pay Again. For NRIs, the Math Hasn't Looked This Good Since 2013.",
        "subheadline": "A quiet swap facility has pushed FCNR deposit rates as high as 7.1%, opening a gap of up to 300 basis points over American CDs. The catch is in the fine print — and in your tax residency.",
        "slug": make_slug("rbi-fcnr-deposit-rates-nri-dollars-india-swap-window"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For the millions of NRIs who hold dollars and wonder where to keep them, India has suddenly become the most rewarding option in years — but the answer of whether to bite depends entirely on which country's taxman you answer to.",
        "tags": ["nri", "diaspora", "fcnr", "rbi", "banking", "investment"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Mint", "url": "https://www.livemint.com/money/personal-finance/fcnr-deposits-for-nris-fixed-deposit-india-rbi-us-dollar-11781510750823.html"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "image_url": "https://images.pexels.com/photos/15633962/pexels-photo-15633962.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "US dollar bills spread out. A new RBI swap window has pushed FCNR deposit rates for NRIs as high as 7.1%.",
        "image_attribution": "Pexels",
        "body": """The Reserve Bank of India has done something it had not done in years: it made keeping your dollars in India genuinely worth it.

In the second week of June, the central bank opened a special swap facility that lets banks raise foreign-currency non-resident deposits — known as FCNR(B) — without eating the cost of protecting themselves against a falling rupee. The effect was immediate. Within a week, HDFC Bank, ICICI Bank, Axis Bank and Bank of Baroda all hiked their rates, with peak offers on three-to-five-year dollar deposits hitting 6%. ICICI and Axis moved by as much as 310 and 305 basis points respectively. At smaller banks, rates now reach 7.1%.

To understand why this matters, you have to understand the plumbing.

## Why the rate jumped

When an NRI deposits dollars in an FCNR account, the bank converts them to rupees and lends them out in India at a higher rate than it pays the depositor. The problem is the gap in between: if the rupee weakens before the deposit matures, the bank loses on the round trip. So banks hedge that currency risk — and hedging, by one estimate from Federal Bank, costs roughly 2.9% to 3% a year. That cost came straight out of the rate offered to NRIs. A bank paying residents 6.5% on a rupee deposit could offer its NRI customers only about 3.5% once hedging was netted out.

The RBI's swap window now absorbs that hedging cost. "Recent regulatory measures have meaningfully optimised hedging economics for banks, enabling us to offer significantly higher rates to NRI customers," said Uttam Tibrewal, deputy chief executive of AU Small Finance Bank. SBI's economists expect the facility to pull in $40-45 billion.

One important caveat: the swap covers only US dollar deposits. Rates on FCNR accounts denominated in pounds, euros, Canadian dollars, Australian dollars or Singapore dollars have not moved.

## The gap that makes NRIs look twice

The reason this has set the diaspora's WhatsApp groups buzzing is comparison. In the United States, three-to-five-year certificates of deposit at the five biggest banks currently yield between 0.03% and 2%. Even smaller US banks and credit unions top out around 4.2% on similar terms. Indian FCNR deposits at comparable banks now sit roughly 300 basis points higher, near 7%.

"The yield gaps are now almost 200 to 300 basis points," said Himanshu Pandya, a Sebi-registered investment adviser, noting the spread used to be a mere 25 to 50 basis points.

The deposits are accessible, too — they start at $500 to $1,000 — and the interest is tax-free in India. They carry a one-year lock-in, and the headline rates apply only to the three-to-five-year tenures.

## Where you live changes everything

Here is the part the headline rate hides. "The interest is tax-free in India, but a US-resident NRI still reports it to the IRS, while an NRI in the UAE keeps the full rate," said Animesh Hardia of 1 Finance. "The same deposit is a strong proposition in the Gulf and a more modest one in America."

The arithmetic bears him out. In the US, foreign interest income is added to total income and taxed at slab rates that run from 10% to 37%. For an NRI in the 20-24% band, a 7% FCNR rate nets out to roughly 4.8-5.5% after American tax. Still respectable against post-tax US CDs, but no longer the runaway bargain it looks like on paper. For an NRI in tax-free Dubai or Abu Dhabi, the full 7% lands in the pocket.

## The leverage temptation — and why advisers say no

Inevitably, talk has turned to leverage, echoing a similar RBI window in 2013. The pitch: put in $100,000 of your own, borrow $900,000, and a 7% deposit against a 5% loan can manufacture returns of 17-27% on your own capital. Brokerages have circulated the math.

Advisers are nearly unanimous in waving people off. The deposit pays a fixed rate while the overseas loan typically floats, so a small rise in global borrowing costs can wipe out the spread. A standby letter of credit to secure the loan costs another 0.5-1% a year before fees. And borrowing rates today, at 4-5%, are far higher than the 1-1.5% of 2013. "I am advising against leveraging," said Rahul Agarwal of Advent Financial. Leverage, the consensus goes, is a game for private-banking ultra-wealthy clients, not the salaried NRI.

For everyone else, the advice is simpler. Use disposable savings, lock in a three-to-five-year deposit, and let the structured-product crowd worry about the rest. It is, for once, a window that rewards patience over cleverness."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "He Built Windows NT and Brought Pro Cricket to Seattle. The US House Just Read His Name Into the Record.",
        "subheadline": "Sivaramakrishnan 'Soma' Somasegar rose from a Louisiana State graduate student to a Microsoft senior vice president. His Congressional tribute is a snapshot of how the Indian-American story has matured.",
        "slug": make_slug("soma-somasegar-us-congress-tribute-microsoft-seattle-cricket"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "A first-generation immigrant honored on the floor of the US House is a marker of how thoroughly the Indian-American community has woven itself into the institutions — corporate, civic, and now legislative — of its adopted home.",
        "tags": ["nri", "diaspora", "microsoft", "seattle", "indian-american", "cricket"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "PTI / Swadesi", "url": "https://swadesi.com/news/us-congress-remembers-indian-american-tech-leader-s-somasegar-mqbtcbl9"},
            {"name": "India Abroad", "url": "https://www.youtube.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "image_url": "https://images.pexels.com/photos/29123790/pexels-photo-29123790.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The Seattle skyline at twilight. Soma Somasegar spent his career in the Pacific Northwest's tech and venture community.",
        "image_attribution": "Pexels",
        "body": """It is not every immigrant who gets his name read into the record of the United States House of Representatives. Sivaramakrishnan Somasegar — "Soma" to nearly everyone who knew him — did, this week, more than a year after his death.

Congresswoman Suzan DelBene of Washington's first district rose on the House floor to pay tribute to the Indian-American technologist, entrepreneur and venture capitalist, who died on 19 May at the age of 59. "Soma was an incredible technologist, entrepreneur, leader, and friend in our community," she said.

## From Louisiana State to the heart of Microsoft

The arc DelBene traced is, in its broad strokes, a familiar one to the diaspora — and that is precisely why it resonates. Born and raised in southern India, Somasegar came to the United States to attend Louisiana State University, the way tens of thousands of Indian students still do each year. In 1989 he joined Microsoft, then a company on the cusp of its decade of dominance.

He arrived in time to work on Windows NT, the operating-system kernel that DelBene called "one of the most important projects in the company's history" — the foundation on which Microsoft's enterprise empire was eventually built. Over the next quarter-century Soma climbed, in DelBene's words, "through his remarkable management skills, dedication, and work ethic" to senior leadership, serving as a senior vice president until 2015. For much of that run he oversaw the developer division, the part of Microsoft that builds the tools other programmers use — an unglamorous but foundational corner of the software world.

## The second act: backing the next generation

What distinguished Soma, in the telling of those who knew him, was the second act. After leaving Microsoft he became a managing director at Madrona Venture Group, one of the Pacific Northwest's most important venture firms, where he spent the next decade backing startups and, as DelBene put it, helping "strengthen the region's innovation ecosystem."

This is the part of the immigrant trajectory that the headline lists of chief executives tend to miss. The most consequential thing a successful first-generation immigrant often does is not the job that made his name but the capital, mentorship and doors he opens afterward. Soma guided "countless startups," DelBene said — a quiet multiplier effect that rarely makes news but shapes whole regional economies.

## Cricket on Puget Sound

And then there is the detail that made the tribute land with the diaspora in particular. Soma was a co-founder of the Seattle Orcas, the franchise that brought professional cricket to the Pacific Northwest as part of America's nascent Major League Cricket. "He helped bring professional cricket to the Pacific Northwest and shared his love of the sport with many in our region," DelBene said.

For an immigrant community whose relationship to the game is almost umbilical, that is no small thing. Cricket has long been the diaspora's portable homeland — played in suburban parks, watched on phones at odd hours, argued about across continents. To have helped plant a professional franchise on American soil is to have given the next generation a place to belong without leaving. It is the kind of institution-building that turns a community of expatriates into a permanent part of the landscape.

## What a Congressional tribute signals

There is a reason these floor tributes matter beyond the family they comfort. A generation ago, the Indian-American community was woven into American corporate life but largely absent from its civic and legislative one. That a Washington congresswoman would devote House time to an Indian-born software executive — invoking not just his career but his community service and his sport — is a small but real marker of how thoroughly that has changed. DelBene, who worked alongside Soma at Microsoft before entering politics, was speaking of a colleague and a constituent, not a stranger.

"His family, friends, and colleagues will cherish his kindness and wisdom for years to come," she closed, asking her colleagues to join in honoring his legacy.

Soma's story is not the billionaire-founder narrative the diaspora's boosters prefer to tell. It is something more durable: an engineer who did foundational work, then spent his later years widening the ladder for others and rooting a beloved game in unfamiliar soil. That the United States Congress paused to say so is its own kind of arrival."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        wc = len(art['body'].split())
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
