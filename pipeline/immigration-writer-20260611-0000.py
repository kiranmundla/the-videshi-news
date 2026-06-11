#!/usr/bin/env python3
"""Immigration writer — 2026-06-11 00:00 UTC run."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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

# ─────────────────────────────────────────────────
# ARTICLE 1: World Cup Visa Chaos
# ─────────────────────────────────────────────────

article1_body = """The biggest football tournament in history kicks off this week across three countries — and the host nation cannot decide whether it wants the world to show up.

The 2026 FIFA World Cup, with a record 48 teams and 104 matches, was supposed to be a celebration of global sport. Instead, the run-up has become a case study in how America's immigration apparatus collides with its ambitions as a host. Referees have been turned away at airports. An entire national team has relocated its base camp across the border. Fans with tickets in hand are being denied visas. And foreign governments are now advising their citizens to carry passports at all times while inside the United States.

## A referee, a photographer, and a federation president walk into an airport

On Saturday, decorated FIFA referee Omar Abdulkadir Artan of Somalia landed at Miami International Airport and was promptly denied entry. Customs and Border Protection cited "vetting concerns" but offered no further explanation. Andrew Giuliani, executive director of the White House Task Force for the World Cup, said the denial was "for very good reasons" — and left it at that.

The same week, an Iraqi national team player was questioned for hours at Chicago's O'Hare airport. He was eventually admitted. The team's photographer was not.

Iran's situation is worse. The entire squad relocated its base camp to Mexico after the U.S. government barred players and staff from staying overnight on American soil. Visas for the players were approved just ten days before their opening match, but more than a dozen support staff — including Mehdi Taj, president of the Iranian football federation — were denied. Iran's embassy accused the U.S. of "politically biased interference in sport."

Four countries competing in the tournament — Iran, Haiti, Côte d'Ivoire, and Senegal — currently face full or partial U.S. travel bans. Across 39 nations, the State Department has suspended visa issuance entirely for 19 of them.

## Fans with tickets, no way in

The exclusions extend well beyond teams. More than 40 members of Moroccan football supporter associations have been denied visas despite holding match tickets and hotel reservations. Nationals from over 50 countries face bond requirements of $5,000 to $15,000 merely to attend — a barrier nominally waived for those who purchased tickets through the FIFA PASS programme by mid-April, but one that left thousands scrambling.

The chilling effect is tangible. Only about 20,000 fans worldwide had used FIFA PASS as of mid-May. Several foreign governments, including the United Kingdom's, now advise World Cup-bound travellers to carry documentation proving legal presence at all times while in the U.S. The spectre of ICE agents at stadiums — an unresolved question the administration has not clearly addressed — adds another layer of anxiety.

"I view the 2026 World Cup as a massive paradox," said Jules Boykoff, professor and author of *Red Card: The 2026 World Cup, Sportswashing and the FIFA Greed Machine*. "On one hand, it has more teams than ever. On the other hand, it looks more like a World Cup of exclusion than inclusion."

## FIFA blinks

Perhaps the most telling detail is FIFA's retreat. In 2025, president Gianni Infantino declared that "everyone will be welcome" and that the U.S. was "committed to a smooth travel process." Faced with the reality of denied referees and relocated teams, FIFA now says it is "not involved in host country immigration processes." David Niven, a University of Cincinnati professor who teaches on sports and politics, called it a "surrender flag."

## Why this matters to Indian Americans

For the estimated 4.4 million Indian Americans, the World Cup visa chaos is not abstract. Tens of thousands plan to attend matches in cities from Houston to New Jersey. The hostile immigration atmosphere — bond requirements, ICE patrols, social media vetting — applies indiscriminately, and Indians travelling from India on B-1/B-2 visas face the same opaque consular process now generating headlines globally.

The timing is striking. Just last week, the State Department introduced a $750 "premium" fee allowing tourist visa applicants to secure interview appointments within ten days — explicitly timed for the World Cup. The subtext is unmistakable: access is available, for a price, to those the system deems worthy. For everyone else, there is a two-year wait and a border agent's discretion.

The beautiful game has always been about who shows up. This summer, America is deciding who gets to."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Referees Denied, Teams Relocated, Fans Turned Away — Welcome to the World Cup",
    "subheadline": "The biggest sporting event in history starts this week in America, and the host country's immigration machine is already making headlines for all the wrong reasons.",
    "slug": make_slug("world-cup-visa-chaos-immigration-exclusion"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian Americans attending World Cup matches face the same hostile immigration environment — bond requirements, ICE presence at stadiums, and a consular system that now charges $750 to skip a two-year visa wait. The chilling effect extends to every NRI with family visiting from India this summer.",
    "tags": ["world-cup", "visa", "immigration", "fifa", "travel-ban", "ice"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "NPR / WAMC", "url": "https://www.wamc.org/2026-06-09/a-warm-world-cup-welcome-u-s-immigration-policies-have-chilling-effect"},
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/news/white-house/3437041/state-department-rolls-out-additional-750-fee-to-fast-track-visa-interviews/"},
        {"name": "Reuters", "url": "https://www.reuters.com/sports/soccer/iran-says-ticket-allocation-world-cup-withdrawn-days-before-tournament-2026-06-10/"},
        {"name": "Front Office Sports", "url": "https://frontofficesports.com/travel-visa-issues-hang-over-world-cup/"},
        {"name": "The Travel", "url": "https://www.thetravel.com/fifa-world-cup-fans-hesitant-travel-us-visa-bonds/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Arrowhead_world_cup_prep%2C_May_2025.jpg/1280px-Arrowhead_world_cup_prep%2C_May_2025.jpg",
    "image_caption": "Arrowhead Stadium in Kansas City being prepared for the 2026 FIFA World Cup",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip(),
}

# ─────────────────────────────────────────────────
# ARTICLE 2: Tech Layoffs and H-1B Workers
# ─────────────────────────────────────────────────

article2_body = """The number arrived without ceremony: 130,000 technology jobs eliminated in 2026 so far, and the year is not yet half over. For most displaced workers, the blow is financial and emotional. For the roughly 730,000 Indian nationals on H-1B visas in the United States, it is existential. When an H-1B holder loses a job, a 60-day clock begins — find a new sponsor, transfer status, or leave the country.

That clock is now ticking for thousands of Indian professionals across Silicon Valley, Austin, Seattle, and the Research Triangle.

## The numbers behind the pain

Meta led the year's bloodletting with 8,000 layoffs and another 7,000 reassignments, hitting engineering teams that had been among the heaviest users of H-1B sponsorship. Oracle has cut an estimated 30,000 positions — the largest single-company reduction this cycle. GitLab shed 14 per cent of its workforce, citing "AI restructuring." Intuit followed with 3,000 cuts. The list runs long: T-Mobile, Wix, Nvidia (which posted an $8 billion severance liability in its latest 10-Q filing), and dozens of smaller firms quietly trimming headcounts.

Indians hold approximately three-quarters of all active H-1B visas. The arithmetic is unforgiving: when tech companies cut, Indian workers absorb a disproportionate share.

## The sponsorship freeze

The layoff wave intersects with a hiring climate that was already hostile to visa-dependent candidates. During the nine months that President Trump's $100,000 H-1B fee was in effect — before a federal judge struck it down on June 8 — many employers simply stopped filing new petitions. Only 85 payments of the fee were ever made. Walmart and other major employers paused their participation in the programme entirely.

The fee is gone, but the chill remains. Immigration attorneys report that corporate legal departments, burned by months of uncertainty, are slow to restart sponsorship pipelines. A proposed rule to halve the post-layoff grace period from 60 days to 30 adds another dimension of risk that makes hiring managers think twice.

A story circulating on Reddit this week captures the mood. An Indian backend engineer who came to the U.S. in 2022 for a master's degree describes applying for jobs for nearly a year after his startup lost funding. Companies showed interest — until they learned he had only one remaining H-1B lottery attempt. One firm took him through five rounds of interviews before its legal team withdrew. He now weighs whether to wait out his remaining STEM OPT days in the U.S. or return to India before the momentum from callbacks fades.

"I am scared I won't get this response again from India," he wrote. "But I'm also scared of moving back permanently."

## The legislative squeeze

Congress is making the calculus worse. At least a dozen Republican lawmakers have backed four separate bills this year targeting the H-1B programme. The most aggressive — Rep. Chip Roy's American White-Collar Worker Jobs Act — would shorten the visa from six years to two, eliminate dual intent (the provision allowing H-1B holders to pursue green cards while working), kill the Optional Practical Training programme that serves as a bridge for international graduates, and cap any company's non-immigrant workforce at five per cent.

India's top IT outsourcers have already begun adjusting. Tata Consultancy Services says it now deploys "fewer people than the number of approvals each year." Cognizant has "significantly reduced the dependency on visas, while increasing local hiring and nearshore capacity." The message from corporate India is clear: the American welcome mat, always conditional, is being pulled back further.

## An inflection point, or a new normal?

Former Meta engineer Zach Wilson, who visited Bengaluru and Hyderabad earlier this year, offered a blunt assessment after the $100,000 fee was struck down: "If we can't bring the brains to America, the brains will continue building amazing things in India."

That may be true in the aggregate. But for the individual H-1B holder sitting in a Bay Area apartment, calculating whether 42 remaining days are enough to find a sponsor willing to file — the abstraction is no comfort.

The layoff wave of 2026 is not merely a cyclical downturn. It is colliding with the most restrictive immigration environment in a generation: higher fees, shorter grace periods, wage-weighted lotteries, legislative assaults on the programme's foundations, and a political climate in which "protecting American workers" has become a bipartisan applause line. For Indian tech professionals in the United States, the question is no longer whether the system is broken. It is whether the pieces can be reassembled before the next round of calendar invites arrives."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "One Hundred and Thirty Thousand Tech Jobs Gone — and the H-1B Clock Is Ticking",
    "subheadline": "The 2026 layoff wave is hitting Indian visa holders hardest, and the safety nets they relied on are fraying at every seam.",
    "slug": make_slug("tech-layoffs-2026-h1b-indian-workers-sixty-day-clock"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B holders make up 75% of the programme and are disproportionately concentrated in the tech sector now shedding 130,000+ jobs. Every layoff starts a 60-day countdown to leave the country — and proposed rules would cut that to 30 days. NRI families from Hyderabad to Pune are watching their children's American futures narrow in real time.",
    "tags": ["h1b", "tech-layoffs", "immigration", "silicon-valley", "indian-workers", "visa"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "NRI Globe", "url": "https://nriglobe.com/tech-layoffs-june-2026-h1b-indians-survival-guide/"},
        {"name": "Livemint", "url": "https://www.livemint.com/companies/is-2026-the-death-knell-for-h-1b-visa-holders-11780829488222.html"},
        {"name": "Livemint", "url": "https://www.livemint.com/news/trends/if-we-can-t-bring-the-brains-to-america-ex-meta-techie-praises-indian-talent-welcomes-h1-b-visa-court-ruling-11781019685731.html"},
        {"name": "nbot.ai", "url": "https://nbot.ai/"},
        {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/us-may-end-permanent-residency-via-h1b-visa-route/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5717791/pexels-photo-5717791.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A worker stares at declining charts on a laptop screen — a scene playing out across thousands of H-1B households in 2026",
    "image_attribution": "Pexels",
    "body": article2_body.strip(),
}

# ─────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
