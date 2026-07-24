#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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
        "headline": "Ten Thousand Telugu Americans Are Heading to Charlotte Next Week. An Oscar Winner Will Be Waiting.",
        "subheadline": "The Telangana American Telugu Association's Mega Convention brings three days of concerts, CME sessions, dance battles, and diaspora soul-searching to the Carolina Convention Center — with a second blockbuster gathering in Baltimore right behind it.",
        "slug": make_slug("tta-mega-convention-charlotte-telugu-mm-keeravani-2026"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Telugu Americans — among the fastest-growing sub-communities in the Indian diaspora — are building conventions that rival political party gatherings in scale, blending cultural preservation with professional networking and healthcare education.",
        "tags": ["nri", "diaspora", "telugu", "convention", "charlotte", "mm-keeravani", "tta", "ata", "community"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TTA Convention Official Website", "url": "https://ttaconvention.org/"},
            {"name": "Xpat Events – TTA Mega Convention 2026", "url": "https://xpat.events"},
            {"name": "South Asian Herald – ATA 19th Conference Announcement", "url": "https://southasianherald.com"},
            {"name": "India Tribune – ATA Curtain Raiser", "url": "https://indiatribune.com"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Charlotte_Convention_Center_in_2017.jpg/1280px-Charlotte_Convention_Center_in_2017.jpg",
        "image_caption": "The Charlotte Convention Center in North Carolina, venue for the TTA Mega Convention 2026",
        "image_attribution": "Wikimedia Commons",
        "body": """Summer 2026 is shaping up as the most ambitious convention season Telugu Americans have ever attempted. Next week, from July 17 to 19, the Charlotte Convention Center will host the Telangana American Telugu Association's Mega Convention — a three-day affair with a capacity of ten thousand and a lineup that reads more like a film-industry awards night than a community gathering. The headliner: M.M. Keeravani, the Oscar-winning composer behind *RRR*'s "Naatu Naatu," performing live on stage.

For the roughly 800,000 Telugu-speaking Americans scattered across the country, these conventions have become a kind of secular pilgrimage. They are where college students compare notes on campus life, where physicians earn their continuing medical education credits, where first-generation parents watch second-generation children compete in classical dance — and where everyone eats an unreasonable quantity of biryani.

## What Charlotte Has Planned

The TTA's programming spans the full breadth of diaspora life. On the cultural front, the Hyderabad Naatyanjali classical dance competition will draw performers from across the country, while Gregory Hancock Dance Theatre — an Indiana-based company known for its cross-cultural productions — will stage a new work titled "Celebrating Telugu Legacy in America." The Paramparaa Dance showcases and performances by Threeory Band and Orange Street round out the entertainment calendar.

But the convention is not merely a cultural festival. A dedicated Continuing Medical Education track, featuring keynote speaker Dr. Duvvur Nageshwar Reddy — the Padma Vibhushan-awarded gastroenterologist and chairman of AIG Hospitals — will offer AMA PRA Category 1 credits. Topics range from heart failure management to immunotherapy in cancer treatment to perimenopause care. Business seminars and a political forum address the professional and civic dimensions of the diaspora experience.

A Women's Forum, Youth Banquet, and Matrimony Meet & Greet serve the community's social infrastructure. The TTA Awards of Excellence will honour Telugu Americans who have distinguished themselves in business, medicine, science, community service, literature, engineering, sports, and youth leadership. A traditional Srinivasa Kalyanam ceremony anchors the spiritual programming.

## A Broader Telugu Convention Season

Charlotte is only the first act. Two weeks later, from July 31 to August 2, the American Telugu Association will hold its 19th Conference and Youth Convention at the Baltimore Convention Center. The ATA raised a record $1.4 million at its kick-off event last October, and a curtain-raiser in Herndon, Virginia, drew seven hundred attendees despite difficult weather. Together, the TTA and ATA events will bring tens of thousands of Telugu Americans into convention halls within the span of a fortnight.

The scale reflects a community that has quietly become one of the most organised segments of the Indian-American population. Telugu speakers now form the second-largest Indian-language group in the United States, behind only Hindi speakers, and their associational life has kept pace. Beyond TTA and ATA, organisations like the American Progressive Telugu Association and the Telugu Association of North America maintain year-round programming — from cricket tournaments to startup competitions, SAT prep courses to yoga sessions, blood drives to clean-water projects in India's Telugu-speaking states.

## What the Conventions Mean for the Diaspora

These gatherings are not just social events. They are the closest thing the Telugu diaspora has to a parliament — places where generational questions get aired, debated, and occasionally resolved. What does it mean to raise children in English-speaking suburbs who can still hold a conversation in Telugu? How do dual-career couples navigate the demands of ageing parents in Hyderabad while building careers in Houston? Should community organisations focus on political advocacy in America or development projects in India?

The conventions do not always produce tidy answers, but they produce something arguably more valuable: a sense that the questions are shared. For a diaspora whose members are often the only Telugu-speaking family on their block, that shared recognition carries its own weight.

Tickets for the TTA Mega Convention are available through the organisation's official website and Xpat.events, the event's ticketing partner. Charlotte is expecting attendees from across the United States and Canada — and, inevitably, a few from Hyderabad who claim they are only visiting relatives."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Anti-Sikh Hate Crimes Surged 3,700 Per Cent in a Decade. Anti-Hindu Incidents Hit a Record. The Numbers Keep Getting Worse.",
        "subheadline": "FBI data for 2025 shows hate crimes against Sikhs, Hindus, and Buddhists reached their highest levels ever recorded, even as temples from California to Melbourne are being defaced with alarming regularity.",
        "slug": make_slug("fbi-anti-sikh-hindu-hate-crimes-record-2025-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For Indian Americans — especially Sikhs and Hindus whose faith is visually identifiable — the surge in hate crimes is reshaping daily decisions: whether to wear a turban to the grocery store, whether to let children walk to the gurdwara alone, and whether America still feels like home.",
        "tags": ["nri", "diaspora", "hate-crime", "sikh", "hindu", "fbi", "safety", "temple", "south-asian"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Asian Americans Advancing Justice – AAJC", "url": "https://www.advancingjustice-aajc.org/press-release/2025-fbi-hate-crime-data-reveals-threats-asian-american-communities"},
            {"name": "Sikh Coalition – FBI Hate Crime Data Analysis", "url": "https://www.sikhcoalition.org"},
            {"name": "Stop AAPI Hate – Keeping Count Report", "url": "https://stopaapihate.org"},
            {"name": "Inshorts – FBI Data on Anti-Sikh Hate Crimes", "url": "https://inshorts.com"},
            {"name": "The Indian EYE – Temple Defacement Reports", "url": "https://theindianeye.com"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/AAPI_Rally_at_the_Capitol._%2851262460082%29.jpg/1280px-AAPI_Rally_at_the_Capitol._%2851262460082%29.jpg",
        "image_caption": "An AAPI solidarity rally at the US Capitol building in Washington, DC",
        "image_attribution": "Wikimedia Commons",
        "body": """In 2015, the FBI recorded six hate crimes against Sikhs in the United States. In 2025, it recorded 226 — a surge of roughly 3,700 per cent over a single decade. Anti-Hindu incidents rose to 28, up 12 per cent from the previous year. Anti-Buddhist hate crimes climbed to 32, a 23 per cent increase. All three figures represent the highest levels ever captured in the FBI's annual hate crime statistics.

The numbers land on a community that has spent years oscillating between two contradictory American experiences: extraordinary professional success and persistent vulnerability on the street. Indian Americans are the highest-earning ethnic group in the country, yet their temples keep getting vandalised.

## The Scale of the Problem

The FBI's 2025 data, analysed by Asian Americans Advancing Justice – AAJC, paints a picture of a country where anti-Asian hate crimes remain more than double the pre-pandemic average. The agency recorded 318 anti-Asian hate crimes in 2025 — a 16 per cent decline from 2024's 379, but still roughly 2.4 times the 133-per-year average from 2013 to 2018.

Within that broader category, the targeting of specific South Asian faith communities is accelerating. Anti-Sikh hate crimes jumped 59 per cent in a single year, from 142 in 2024 to 226 in 2025. The Sikh Coalition, which has tracked these numbers since the 2012 mass shooting at a Wisconsin gurdwara that killed six worshippers, noted that Sikhs remain the third-most targeted religious group in the nation, behind only Jewish and Muslim communities.

"Sikhs clearly remain disproportionately at risk of targeted violence and discrimination," said Harman Singh, executive director of the Sikh Coalition. He pointed to multiple factors: policies affecting non-domiciled truck drivers, xenophobia driven by international affairs, broader anti-immigrant rhetoric, and what he described as "hateful online rhetoric stoked by foreign governments and their proxies."

## Temples Under Attack

The statistics acquire a visceral quality when set against recent events. In California's Bay Area, three Hindu temples were targeted in quick succession. The Swaminarayan Mandir in Newark was defaced with anti-India graffiti. Weeks later, the Sherawali Temple in Hayward — a Sikh gurdwara — was hit with pro-Khalistan graffiti in what police described as a copycat incident. A theft at the Shiv Durga temple in the same area followed shortly after.

Across the Pacific, Melbourne's Shree Swaminarayan Temple in Boronia was vandalised with the message "Go home brown c***" spray-painted in red, part of what Victoria Police called a coordinated campaign that also targeted two nearby Asian-run restaurants. The Hindu Council of Australia's Victoria chapter president, Makrand Bhagwat, said the temple was "meant to be a sanctuary of peace, devotion and unity."

The Hindu American Foundation urged all temples to install security cameras and alarm systems. The US State Department's Bureau of South and Central Asian Affairs publicly condemned the Newark defacement.

## The Online Dimension

The physical attacks are accompanied — and often preceded — by an escalating online atmosphere. Stop AAPI Hate, which monitors online spaces associated with targeted violence, reported that in August 2025 alone, there were nearly 57,200 anti-South Asian slurs detected online — the third-highest monthly total since tracking began in January 2023.

The organisation's research has identified political discourse as a key accelerant. Spikes in anti-South Asian hate have tracked political events: Vice President Kamala Harris's presidential campaign announcement, Donald Trump's second-term election victory, India-Pakistan tensions, debates over the H-1B visa programme, and the New York City mayoral campaign of Zohran Mamdani.

Sim J. Singh Attariwala, director of the anti-hate programme at Advancing Justice – AAJC, said the data "pulls back the curtain of the lived reality for many Asian American communities who continue to face targeted violence, harassment, and intimidation."

## What the Diaspora Is Doing

Community organisations have moved beyond vigils and press releases. The Sikh Coalition continues to advocate for improved federal hate-crime reporting — noting that thousands of law enforcement agencies still report zero hate crimes in their jurisdictions, suggesting significant undercounting rather than an absence of incidents. Hindus for Human Rights has called for "accountability, better reporting, and solidarity across communities."

At the local level, diaspora organisations have launched bystander-intervention training programmes. California State Senator Josh Becker hosted one such session in partnership with the Council on American-Islamic Relations and the San Mateo County AAPI Task Force, training residents to safely de-escalate hate incidents. Temple management committees across the country have been upgrading physical security — cameras, alarms, and in some cases, hired guards — while trying to preserve the open, welcoming character that defines a place of worship.

The FBI data carries a structural caveat that makes it both worse and better than it appears. Worse, because chronic underreporting means the true number of incidents is almost certainly higher. Better, because the growth in reported incidents partly reflects improved tracking — the FBI only began separately recording anti-Sikh and anti-Hindu crimes in 2015.

For the Indian diaspora, the distinction between improved counting and an actual increase matters less than the lived experience. When a teenager in a turban is attacked on the street and the Sikh Coalition calls it a hate crime, his family does not take comfort in the possibility that similar attacks went uncounted a decade ago.

Ria Chakrabarty, senior policy director at Hindus for Human Rights, framed the challenge in terms the diaspora understands. "Hindu Americans are part of the broader Asian American story," she said. "These attacks are unfolding alongside threats to Sikhs, Muslims, Buddhists, immigrants, and other communities facing a wider climate of xenophobia, religious bigotry, and supremacist politics."

The numbers suggest she is right. And that the trajectory, for now, is pointing in the wrong direction."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
