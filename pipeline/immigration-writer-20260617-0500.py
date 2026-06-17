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

body1 = """For two decades the H-1B leaderboard read like a roll call of Indian outsourcing: Infosys, TCS, Wipro, Cognizant, all near the top, all moving tens of thousands of engineers from Bengaluru and Hyderabad to client sites in New Jersey and Texas. That order has now flipped. For the first time, the four American technology giants — Amazon, Meta, Microsoft and Google — hold the top spots for approved H-1B petitions for initial employment, according to an analysis of US Citizenship and Immigration Services data by the National Foundation for American Policy.

Amazon led the field with 4,644 approvals in FY25, followed by Meta with 1,555, Microsoft with 1,394 and Google with 1,050. By contrast, only three Indian companies cracked the top 25 employers. The seven largest Indian IT services firms together secured just 4,573 H-1B petitions for initial employment — a 70% collapse from FY15 and 37% below the prior year.

## The AI hiring machine

The NFAP report ties the surge in big-tech sponsorship directly to the roughly $380 billion the four firms poured into artificial intelligence and related infrastructure in 2025. When a company is building data centres and racing to staff frontier-model teams, it reaches for the narrow pool of people who can do the work — and a large share of that pool was trained in India or graduated from American universities on F-1 visas.

A caveat worth keeping in mind: these numbers count petitions, not people. A single H-1B holder can be approved more than once in a year if they change worksites, so the figures overstate headcount. Still, the directional story is unambiguous. The visa is increasingly a tool for American product companies hiring directly, not for staffing firms placing contractors.

## Why the Indian IT model broke

The decline at TCS, Infosys and their peers is not an accident of one bad lottery. It is the visible result of a deliberate pivot. Years of tighter scrutiny, denial spikes, fee increases and the threat of outsourcing penalties made the old labour-arbitrage model — fly in a low-cost engineer, bill a US client — expensive and legally fragile. The firms responded by hiring locally in America, leaning on US-based subcontractors, and shifting more work offshore to delivery centres in India. Renewals for existing workers remain strong, with over 291,000 approvals, signalling a strategy of holding onto the people already here rather than sponsoring new arrivals.

## Why this matters to Indian Americans

For the Indian diaspora, the shift is double-edged. The good news: Indians remain the overwhelming beneficiaries of the H-1B, accounting for more than 70% of approved petitions. The route to America is still wide open for the right candidate.

The bad news is who that candidate now needs to be. The new gatekeepers are product companies hiring for elite engineering and AI roles, often at wage levels that sail through the administration's new salary-weighted lottery. That favours graduates of top programmes and people with specialised, in-demand skills. It is far less forgiving of the generalist IT consultant who, a decade ago, could count on an Infosys or Cognizant petition as a reliable on-ramp.

For families already in the US, the trend reshapes career math. If you are an H-1B holder at a staffing firm watching your employer pull back from sponsorship, the safer harbour is increasingly a direct-hire role at a company still filing in volume. For the next generation — Indian students weighing a US master's degree — the message is that the degree alone no longer guarantees a sponsor. The field has narrowed to those who can land a job at a company building AI, and those companies can afford to be choosy.

The era when an Indian IT badge was the most common path to an American work visa is ending. What replaces it is a smaller, higher-stakes funnel — one that rewards specialised talent and leaves the middle of the market with fewer options than at any point in a generation."""

body2 = """The H-1B has always carried a fraud problem at its margins, and the Justice Department has just signalled that the consequences can now reach all the way back to citizenship itself. The DOJ announced it has filed denaturalization actions in federal district courts against 17 individuals accused of serious offences — among them Neeraj Sharma, an India-born former staffing executive in New Jersey whose case reads as a cautionary tale for every entrepreneur who has cut corners on a visa petition.

According to the department, Sharma owned and ran Magnavision LLC, a Piscataway-based staffing company. As its officer, he signed and filed eleven fraudulent H-1B petitions with USCIS. Each falsely claimed the visa beneficiaries would be employed by a particular global financial institution, and each included letters on official corporate letterhead carrying forged signatures of that institution's executives.

## From fraud to forfeited citizenship

The mechanism the government is using is denaturalization — stripping citizenship from someone who, prosecutors argue, never should have received it. Under the Immigration and Nationality Act, a naturalized citizen's status can be revoked if it was illegally procured or obtained through concealment or willful misrepresentation of a material fact.

Sharma applied for naturalization in 2017. Under penalty of perjury, the DOJ says, he falsely asserted that he had never committed a crime for which he was not arrested, never given US officials false or misleading information, and never lied to a government official to obtain an immigration benefit. On the strength of those statements USCIS approved his application, and he became a citizen in December 2017. The denaturalization suit argues those statements were lies, and that the citizenship rests on the same fraudulent foundation as the visa petitions beneath it.

## The body-shop reckoning

Sharma's case sits inside a larger pattern the government has been pursuing: the so-called "desi body shops," small staffing firms that game the H-1B system by inventing jobs, fabricating client relationships and shuffling workers between projects that may not exist. In April, USCIS fraud detection led to two guilty pleas in a separate Sacramento conspiracy in which petitioners falsely claimed workers would be placed at the University of California. The denaturalization filings raise the ceiling on the penalties: it is no longer only the visa or the green card at risk, but naturalized citizenship years after the fact.

## Why this matters to Indian Americans

For the vast majority of the diaspora who filed honestly, the headline risk here is reputational, not legal. India-born nationals are the largest group of H-1B beneficiaries and the largest group of employment-based naturalized citizens, which means they are also the most exposed when "H-1B fraud" becomes a recurring phrase in DOJ press releases. Each case feeds a political narrative that the whole programme is rotten — a narrative already powering bills in Congress to gut it.

There is also a concrete lesson for anyone who came through a small staffing firm. If your original petition contained misstatements you did not catch — a client you never worked for, a job description that did not match reality — those facts do not expire when you naturalize. The government's willingness to reopen citizenship a decade later means the paper trail of your earliest filings still matters. Keep your own records: offer letters, pay stubs, project assignments, anything that documents that the work you were petitioned for was real.

The broader message is sobering but narrow. Honest applicants are not the target. But the administration has made clear that immigration fraud now has no statute of comfort — and for a community whose American story so often runs through the H-1B, that is a line worth understanding precisely."""

body3 = """The hardest part of holding an American work visa from India is increasingly not getting the visa — it is getting an appointment to have it stamped. New guidance from the immigration firm Fragomen lays out just how severe the bottleneck at US consulates in India has become, and the numbers should alarm anyone planning to travel home this year.

Foreign nationals seeking employment-based nonimmigrant visas — the H and L categories that cover most Indian tech workers and intra-company transferees — now face waits of 75 to more than 125 days to secure an interview slot across Chennai, Hyderabad, Kolkata, Mumbai and New Delhi. The cause is blunt and structural: demand for US visas has climbed steadily over recent months, but there has been no corresponding increase in consular staff at the US mission to India. Supply has not moved; demand has surged; the queue has done the rest.

## The Kolkata collapse

Nothing illustrates the squeeze better than Kolkata. Once the quiet back door for Indians in a hurry, the post had an appointment backlog of just 13 days. It is now 126 days. A consulate that immigration lawyers routinely recommended as the fastest route to a stamp has, since late August, become as slow as the rest. The escape valve has effectively closed.

There is one bright spot in the data. While H and L applicants wait months, B-1/B-2 visitor visas and F-1 student visas are moving in four to 22 days at most posts — a reminder that the crunch is concentrated in the employment categories that matter most to working professionals.

## The third-country workaround

For Indians with an urgent need to travel, Fragomen points to one alternative: applying as a third-country national, or TCN, at a US consulate outside India. An H-1B holder might, for instance, book a stamping appointment in a nearby country rather than wait out the domestic backlog.

The catch is that the workaround carries real friction. There are additional travel and accommodation costs. The applicant may need a separate visa simply to enter the third country. And TCN appointments carry their own risk — if a case is refused or placed in administrative processing abroad, the worker can be stranded outside both the US and India until it clears. It is a tool for the genuinely time-pressed, not a routine convenience.

## Why this matters to Indian Americans

For the diaspora, this is the quiet tax on an otherwise legal, settled life. A worker on a valid H-1B can live and work in the US without interruption — until they leave the country. The moment a stamp expires and a trip home becomes necessary, whether for a wedding, a parent's illness, or a long-delayed visit, the calendar turns hostile. A two-week vacation can balloon into a months-long limbo if the stamping appointment and any administrative processing run long.

The practical consequence is that thousands of Indian professionals are simply not travelling. They postpone family visits, skip funerals, and watch children grow up over video calls rather than risk being locked out of their jobs and homes. The backlog converts a routine bureaucratic step into a genuine life decision.

The medium-term fix that immigration advocates and the Indian government have pushed — a domestic visa-renewal pilot that would let workers re-stamp inside the US without leaving — remains the structural answer. Until it scales, the advice from practitioners is unglamorous but essential: if you hold an H or L visa and expect to travel in the next year, book your stamping appointment now, build in months of buffer, and treat any trip abroad as a commitment with an uncertain return date. The visa lets you stay. Leaving is the gamble."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Big Tech Just Took Over the H-1B — and Pushed India's IT Giants Off the Top",
        "subheadline": "Amazon, Meta, Microsoft and Google hold the top H-1B spots for the first time, fueled by AI hiring, as approvals for Indian outsourcers crater 70% over a decade.",
        "slug": make_slug("big-tech-tops-h1b-approvals-amazon-meta-indian-it-firms-decline"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians still win most H-1Bs, but the path now runs through elite AI roles at US product companies rather than the Indian IT firms that once served as the reliable on-ramp.",
        "tags": ["h1b", "uscis", "big tech", "indian it", "ai hiring"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "LiveMint", "url": "https://www.livemint.com/companies/news/amazon-google-meta-microsoft-top-list-of-h-1b-petition-approvals-for-1st-time-amid-ai-push-key-findings-11718000000000.html"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy-and-policy/h-1b-visa-approvals-for-indian-it-services-drop-to-decade-low-amid-tightened-us-scrutiny"},
            {"name": "National Foundation for American Policy (NFAP)", "url": "https://nfap.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/358549/pexels-photo-358549.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Modern corporate skyscrapers, home to the US technology giants now leading H-1B sponsorship",
        "image_attribution": "Pexels",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "An H-1B Lie From 2017 Just Cost a New Jersey Man His US Citizenship",
        "subheadline": "The DOJ filed denaturalization suits against 17 people, including India-born staffing executive Neeraj Sharma, accused of filing eleven fraudulent H-1B petitions with forged signatures.",
        "slug": make_slug("doj-denaturalization-h1b-fraud-neeraj-sharma-magnavision-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Denaturalization over old H-1B fraud means naturalized Indian Americans who came through small staffing firms should keep records proving their earliest petitions were legitimate.",
        "tags": ["h1b", "fraud", "denaturalization", "doj", "body shops"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/h-1b-visa-fraud-by-indian-leads-to-revocation-of-us-citizenship/"},
            {"name": "USCIS", "url": "https://www.uscis.gov/newsroom/news-releases/uscis-efforts-lead-to-two-guilty-pleas-in-h-1b-fraud-conspiracy-case"},
            {"name": "US Department of Justice", "url": "https://www.justice.gov/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29500749/pexels-photo-29500749.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A US courthouse, where the Justice Department has filed denaturalization actions against 17 individuals",
        "image_attribution": "Pexels",
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Kolkata Was the Fast Lane for a US Visa Stamp. The Wait Just Went From 13 Days to 126",
        "subheadline": "H and L visa appointment backlogs at every US consulate in India now run 75 to 125-plus days, leaving working professionals afraid to travel home — with only a costly third-country workaround.",
        "slug": make_slug("us-consulate-india-h1b-l1-appointment-backlog-kolkata-tcn-workaround"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For H-1B and L-1 Indians in the US, a trip home now risks months of limbo waiting for a stamping appointment, turning routine family visits into high-stakes decisions.",
        "tags": ["h1b", "l1", "visa stamping", "consulate", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fragomen", "url": "https://www.fragomen.com/insights/update-on-visa-appointment-backlogs-at-us-consulates-in-india.html"},
            {"name": "US Department of State - Global Visa Wait Times", "url": "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/wait-times.html"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32642490/pexels-photo-32642490.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A US passport with travel documents; visa stamping appointments in India now run months long",
        "image_attribution": "Pexels",
        "body": body3
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  words={wc} slug={art['slug']}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
