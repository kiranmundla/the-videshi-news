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
        "headline": "Ninety-Six Unicorns and Counting. Indian Immigrants Are Building More Billion-Dollar Startups Than Any Other Group in America.",
        "subheadline": "A new report from the National Foundation for American Policy finds that Indian-born entrepreneurs have founded or co-founded 96 privately held unicorn companies in the United States — more than Israel, Britain, and China combined.",
        "slug": make_slug("indian-immigrants-96-unicorn-startups-nfap-report"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian immigrants' dominance of American startup culture reflects decades of diaspora entrepreneurship and the compounding effects of networks built by generations of NRIs in Silicon Valley and beyond.",
        "tags": ["nri", "diaspora", "startups", "entrepreneurs", "silicon-valley", "unicorns"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "National Foundation for American Policy", "url": "https://nfap.com/"},
            {"name": "ConnectMyIndia", "url": "https://nri.connectmyindia.com/montreal/news/article/immigrants-drive-majority-of-us-unicorn-startups-indians-lead-the-pack-3809/"},
            {"name": "Forbes", "url": "https://www.forbes.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7413920/pexels-photo-7413920.jpeg",
        "image_caption": "A startup team pitching during a business presentation in a modern office",
        "image_attribution": "Pexels",
        "body": """The numbers tell a story that Indian families in Cupertino, Jersey City, and Plano have lived for years: if you want to build something worth a billion dollars in America, it helps to have been born in India.

A report released by the National Foundation for American Policy — a nonpartisan think tank based in Arlington, Virginia — has found that immigrants are behind 455 of America's 775 privately held unicorn startups, companies valued at one billion dollars or more. That is 59 percent of the entire roster. And Indian-born entrepreneurs sit at the top of the list, having founded or co-founded 96 of those companies.

No other country comes close. Israel produced 60 immigrant-founded unicorns. The United Kingdom contributed 47. China accounts for 41, Canada for 30, Russia for 23, and France for 21. India's lead is not marginal — it is nearly double the second-place country.

## The Names Behind the Numbers

The flagship example is Aravind Srinivas, the Indian-origin co-founder of Perplexity AI, the search startup that has muscled its way into a market long dominated by Google. The company carries a valuation of 20 billion dollars, making it one of the most valuable privately held firms in the country.

But Srinivas is hardly an outlier. The report identifies at least 15 immigrants who have founded two or more unicorn companies. Several are Indian-born: Mohit Aron (Cohesity, Nutanix), Jyoti Bansal (AppDynamics, Harness), Ashutosh Garg (Bloomreach), Arvind Jain (Glean), Sachin Nair, and Ajit Singh. Each built companies that now employ hundreds, sometimes thousands, of Americans.

The economic footprint is substantial. Each immigrant-founded unicorn has created an average of 833 jobs, according to the report. Taken together, these companies represent a combined valuation exceeding five trillion dollars.

## A Diaspora Built for Entrepreneurship

The dominance of Indian founders is not accidental. It sits at the confluence of several forces that NRIs know intimately: the selectivity of American immigration (H-1B visa holders tend to be highly skilled engineers and MBAs), dense professional networks in Silicon Valley and the Northeast, a cultural emphasis on technical education, and a community infrastructure that informally mentors new arrivals.

Indian-origin professionals already hold the top positions at some of America's largest public companies — Alphabet, Microsoft, IBM, Adobe, and FedEx among them. But the unicorn data suggests something different from corporate ladder-climbing. These are founders: people who started from zero, raised capital, recruited teams, and built companies that the market valued at a billion dollars or more. That is a more radical form of economic participation, and Indians are doing more of it than anyone else.

## Why NRIs Should Pay Attention

The report arrives at a moment when immigration policy in the United States is deeply contested. Visa backlogs for Indian nationals stretch years, sometimes decades. Proposals to restrict H-1B eligibility or tighten green card timelines resurface regularly.

Yet the data makes an uncomfortable counterargument for restrictionists: immigrants are not competing for a fixed number of jobs — they are creating new ones. The 455 immigrant-founded unicorns collectively employ hundreds of thousands of workers across the country.

For the diaspora, the findings are also a mirror. The 96-unicorn figure reflects a community that has moved well beyond the first-generation survival narrative of long hours and remittances. This is a generation — and now a second generation — that is shaping the industries the world will run on: artificial intelligence, cloud computing, cybersecurity, fintech.

The question is no longer whether Indians can build in America. The data settled that years ago. The question is whether America's immigration system will continue to let them."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "From the Lincoln Memorial to Times Square, India Is Turning America's Most Famous Landmarks Into Yoga Studios",
        "subheadline": "The Indian Embassy and consulate will host the 12th International Day of Yoga at two of Washington and New York's most iconic sites, with PM Modi's personal yoga guru headlining the celebrations.",
        "slug": make_slug("international-yoga-day-2026-lincoln-memorial-times-square"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The annual Yoga Day celebrations have become the Indian diaspora's most visible cultural export — a soft power projection that diaspora organizations have spent a decade building through diplomatic partnerships and community organizing across American cities.",
        "tags": ["nri", "diaspora", "yoga", "yoga-day", "lincoln-memorial", "times-square", "cultural-diplomacy"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/indian-embassy-to-celebrate-international-day-of-yoga-2026-at-lincoln-memorial/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/pm-modis-yoga-guru-to-lead-times-square-yoga-day-event/"},
            {"name": "NewKerala", "url": "https://www.newkerala.com/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/International_Yoga_Day_2023_celebrations_in_Munich_05.jpg/1280px-International_Yoga_Day_2023_celebrations_in_Munich_05.jpg",
        "image_caption": "International Day of Yoga celebrations with participants practicing outdoors",
        "image_attribution": "Wikimedia Commons",
        "body": """On June 19, several hundred yoga practitioners will unroll their mats on the steps of the Lincoln Memorial in Washington, D.C. Two days later, thousands more will do the same in the middle of Times Square. Both events are organized by Indian diplomatic missions. Neither is a coincidence.

The Indian Embassy in Washington announced the Lincoln Memorial event in a post on X, framing it as a flagship celebration of the 12th International Day of Yoga. The Consulate General of India in New York will host the Times Square gathering on June 21 — the official date designated by the United Nations in 2014, following a resolution co-sponsored by 177 nations at the urging of Prime Minister Narendra Modi.

This year's theme is "Yoga for Healthy Aging," a focus that positions the ancient discipline not merely as exercise but as a public health strategy for extending life and mobility.

## The Guru in the Room

The headliner at Times Square will be Padma Shri H.R. Nagendra, the 82-year-old president of S-VYASA University in Bengaluru and widely described as the yoga guru who guides Modi's personal practice. Nagendra holds a doctorate in mechanical engineering from the Indian Institute of Science and spent years at NASA before pivoting to yoga research — a biography that neatly bridges the diaspora's twin affinities for hard science and spiritual tradition.

Accompanying Nagendra will be Dr. N.K. Manjunath, the university's vice chancellor. Before the main event, the pair will inaugurate a three-day Yoga and Wellness Retreat at the YO1 Longevity and Health Resort in Monticello, New York, running from June 12 to 14. The retreat will include sessions on stress management, healthy aging, and holistic wellness.

Among the distinguished speakers confirmed for the Monticello retreat are Dr. Samin K. Sharma, Director of Interventional Cardiology at Mount Sinai Hospital, and Dr. Raj Bansal, founder of one of the largest Accountable Care Organizations in the United States.

## A Decade of Diaspora Diplomacy

The organizational muscle behind the celebrations comes from a network of Indian-American associations that have spent years embedding yoga into American civic life. The Rajasthan Association of North America, BRUHUD NY Seniors, and Jaipur Foot USA are co-hosting the New York events.

Central to this effort is Prem Bhandari, chairman of Jaipur Foot USA and president of RANA New York. Bhandari has organized yoga programs at the United Nations headquarters and on Capitol Hill for over a decade. He described Nagendra's visit as a milestone. "Yoga is India's timeless gift to humanity," Bhandari said. "After a decade of promoting yoga across the US with diplomatic missions and institutions, we are deeply honoured to welcome Padma Shri HR Nagendra."

Nagendra, for his part, credited Bhandari with helping bring "the timeless wisdom of yoga to people from all walks of life."

## What It Means for the Diaspora

The International Day of Yoga is arguably the Indian community's most successful cultural export. Unlike Diwali, which remains largely celebrated within South Asian circles in most American cities, yoga has long crossed ethnic lines. The UN designation gave it diplomatic heft, and Indian missions have used the annual observance to project soft power in ways few other countries have managed with a cultural practice.

For Indian Americans, the celebrations are both a point of pride and a rare moment of visibility that is not tied to tech earnings or immigration policy. When several thousand New Yorkers roll out mats in the middle of Times Square under the banner of a practice that originated in the subcontinent, the diaspora sees its heritage — not its visa status — on the marquee.

Whether that translates into anything beyond a single day of Sun Salutations is an open question. But after twelve years, the machinery of Yoga Day has become self-sustaining. The mats keep coming out. The landmarks keep getting bigger."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A 28-Year-Old From Telangana Was Delivering Pizzas in Philadelphia. He Never Made It Back to His Car.",
        "subheadline": "Kuncha Anshul was shot dead by masked assailants while completing a late-night delivery order in North Philadelphia. His family in Medchal is now fighting to bring his body home.",
        "slug": make_slug("telangana-man-killed-pizza-delivery-philadelphia-anshul"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The killing adds to a pattern of violence against young Indian workers in the United States who take on gig and delivery jobs to supplement their income — exposing them to the dangers of American urban gun violence that few are prepared for when they arrive.",
        "tags": ["nri", "diaspora", "community-safety", "philadelphia", "telangana", "gun-violence"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "ConnectMyIndia", "url": "https://nri.connectmyindia.com/montreal/news/article/telangana-youth-shot-dead-during-pizza-delivery-in-philadelphia-family-seeks-repatriation-of-body-3810/"},
            {"name": "India Today", "url": "https://www.indiatoday.in/"},
            {"name": "NDTV", "url": "https://www.ndtv.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12304691/pexels-photo-12304691.jpeg",
        "image_caption": "Philadelphia skyline at night reflected in the Schuylkill River",
        "image_attribution": "Pexels",
        "body": """Kuncha Anshul moved to the United States in 2023. He was 28 years old, from Gundlapochampally in Telangana's Medchal Malkajgiri district. He had a job at a company called KWC in the Philadelphia area. On weekends, he drove for a pizza shop to make extra money.

In the early hours of a recent Saturday, Anshul received a delivery order: three pizzas to a residence within the Raymond Rosen Homes complex on Edgley Street in North Philadelphia. He arrived around 12:30 in the morning, stepped out of his vehicle, and was met by masked assailants who opened fire.

He was struck by multiple gunshots, including to the back of his head. He collapsed at the scene. By the time witnesses alerted police and officers arrived, there was nothing to be done. Investigators recovered three bullet casings. No arrests have been made. The motive remains unclear.

## A Family's Impossible Distance

In Telangana, Anshul's family learned about his death through channels no parent should have to navigate — phone calls across time zones, fragmented information relayed through community contacts, the slow bureaucracy of international death notification.

His sister made an emotional public appeal to the Indian government and consular authorities, asking for help in bringing Anshul's body back to India. Repatriation of remains is expensive, procedurally complex, and agonizingly slow. It requires coordination between local law enforcement, the Indian consulate, funeral homes, airlines, and often a GoFundMe campaign organized by friends or community members who barely have the bandwidth to grieve.

The family's appeal has drawn attention in Telangana, where the state government has faced recurring pressure to assist families of young people killed abroad.

## The Gig Economy's Invisible Workers

Anshul's story is not unique, and that is precisely the problem. Young Indians arrive in the United States on work visas or student visas, find that their primary income does not stretch far enough in cities where rent alone can consume most of a paycheck, and turn to the gig economy to close the gap. Pizza delivery. DoorDash. Uber. The work is flexible, pays in cash or quick deposits, and requires little more than a car and a phone.

What it also requires — and what few think about until it is too late — is driving alone to unfamiliar addresses in unfamiliar neighborhoods at hours when the streets are empty and the risks are high. Delivery workers in the United States face higher rates of robbery and assault than almost any other occupation. In cities like Philadelphia, where gun violence remains at crisis levels, a late-night delivery is a gamble every time.

Indian students and workers, many of them from small towns or suburbs in Andhra Pradesh, Telangana, Karnataka, and Gujarat, are particularly vulnerable. They may not know which neighborhoods to avoid. They may not recognize the warning signs. And unlike American-born workers who grew up with active-shooter drills and a cultural vocabulary for urban danger, they often arrive with no frame of reference for the violence they might encounter.

## What the Community Is Asking

In the days since Anshul's death, members of the Indian community in the Philadelphia area have called for greater awareness and support systems for delivery workers. Some have urged Indian associations to circulate safety guidelines — practical advice on verifying addresses, avoiding deliveries in high-crime zones after dark, and knowing when to abandon an order.

Others have pointed to the structural issue: why are young Indians in America working gig jobs at 12:30 in the morning in the first place? The answer loops back to economics. Wages at the entry-level jobs many H-1B and OPT holders take are often insufficient for the cost of living in East Coast cities. The gig economy is the gap filler. It is also the gap where people get hurt.

Anshul's family in Medchal is waiting. The investigation in Philadelphia is ongoing. And somewhere in North Philadelphia, the Raymond Rosen Homes complex sits quiet, a delivery that was never completed marked only by three bullet casings on the pavement."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
