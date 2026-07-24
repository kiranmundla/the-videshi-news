#!/usr/bin/env python3
"""NRI World writer — July 5, 2026 05:00 run"""
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
        "headline": "One Hundred and Thirty Hindu Americans Walked Into Congress on the Fourth of July Eve. Seven Lawmakers Walked Out Allies.",
        "subheadline": "CoHNA's fifth Hindu Advocacy Day drew bipartisan support from both parties on Capitol Hill, blending the celebration of America's 250th birthday with an urgent pushback against rising Hinduphobia.",
        "slug": make_slug("cohna-hindu-advocacy-day-capitol-hill-america-250-hinduphobia"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Hindu Americans are building serious political muscle — 130 delegates from 15 states descended on Capitol Hill, held 50-plus meetings with Senate and House staff, visited 120 offices, and secured bipartisan condemnation of temple attacks. This is diaspora civic engagement maturing from protest to policy.",
        "tags": ["nri", "diaspora", "hindu-american", "advocacy", "hinduphobia", "capitol-hill", "america-250", "cohna"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "PR Newswire / Coalition of Hindus of North America", "url": "https://www.prnewswire.com/news-releases/hindu-advocacy-day-on-capitol-hill-celebrates-america-250-draws-bipartisan-support-from-congressional-reps-against-rising-hinduphobia-and-hate-302817658.html"},
            {"name": "Morningstar / PR Newswire", "url": "https://www.morningstar.com/news/pr-newswire/20260703cl97814/hindu-advocacy-day-on-capitol-hill-celebrates-america-250-draws-bipartisan-support-from-congressional-reps-against-rising-hinduphobia-and-hate"},
            {"name": "CoHNA Official", "url": "https://cohna.org/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Capitol_Building_Full_View.jpg/1280px-Capitol_Building_Full_View.jpg",
        "image_caption": "The United States Capitol Building in Washington, D.C., where Hindu American delegates gathered for their fifth annual advocacy day",
        "image_attribution": "Wikimedia Commons",
        "body": """The day before America turned 250, a group of Hindu Americans turned up at the place where the country's laws are made — not to celebrate, exactly, but not to protest either. They came to be counted.

The Coalition of Hindus of North America (CoHNA) held its fifth annual Hindu Advocacy Day on Capitol Hill on July 3, drawing more than 130 delegates from 15 states to Washington, D.C. Seven sitting members of Congress — from both parties — showed up to listen. Twelve Congressional staffers joined them. It was, by any measure, the organisation's largest and most politically consequential outing to date.

## Fifty meetings, one hundred and twenty doors

Before the main event even began, Hindu delegates had already fanned across the Hill. They held more than 50 scheduled meetings with the staff of Senators and members of the House. They knocked on more than 120 Congressional office doors — sometimes with appointments, sometimes without — to introduce themselves and their concerns to the people who represent them.

"We came together as Americans, sharing stories, building relationships and singing the national anthem," said Nikunj Trivedi, CoHNA's president. "American Hindus come from all walks of life — students, entrepreneurs, cab drivers, pharmacists, homemakers, retail workers, engineers, bankers and scientists. We are thinkers, teachers, writers and veterans."

The timing was no accident. With America's semiquincentennial falling the next day, CoHNA framed the event as both a celebration of the republic and a reminder that religious freedom — one of its founding promises — is under strain for one of its fastest-growing communities.

## Bipartisan alarm over temple attacks

Every lawmaker who spoke addressed the same thing: the wave of anti-Hindu vandalism that has swept across the United States in recent months, particularly in California's Bay Area, where three Hindu temples were defaced with pro-Khalistan graffiti in the space of three weeks.

Representative Buddy Carter, a Republican from Georgia, put it plainly. "Freedom of religion is one of our greatest rights," he said, condemning the temple vandalism and thanking Hindu Americans for their role in "this great experiment of democracy."

From the other side of the aisle, Representative Shri Thanedar, a Michigan Democrat and himself an Indian immigrant, urged the community to "demand respect for our contributions in science, medicine, academia, and politics."

Representative Suhas Subramanyam of Virginia, the first Indian American elected to Congress from the East Coast, spoke directly to the young Hindus in the room. "Embrace who you are as Hindus," he said. "Being different becomes cool later in life — be proud now."

Representative Sanford Bishop, one of the most senior members of the House, was unambiguous. "Hinduphobia is un-American," the Georgia Democrat declared, pointing to his state as the first to formally condemn it. His Republican colleague from Georgia, Representative Brian Jack, echoed the point: "Georgia is leading the way against Hinduphobia." A third Georgia lawmaker, Representative Rich McCormick, praised Hindu Americans as "hardworking, intelligent, family-oriented, robust — that's the American Dream."

Representative Zoe Lofgren, a California Democrat, waded into more contested territory, warning that proposed caste-based legislation risks "deepening discrimination rather than solving it" — a reference to failed attempts to add caste as a protected category in New York State law.

## The research behind the rhetoric

The event was not all speeches and handshakes. Dr. Joel Finkelstein, co-director of the Network Contagion Research Institute (NCRI) at Rutgers University, presented findings on what he described as the push to insert caste into American policymaking "despite no evidence of a pervasive caste hierarchy in American Hindu life." He urged lawmakers to demand stronger evidence before encoding activist narratives into legislation.

His colleague Prasiddha Sudhakar presented research titled "From Policy Drift to Purity Grift," tracing how a debate over immigration morphed into a coordinated campaign targeting Hindu Americans specifically. Her analysis found that what was publicly framed as "anti-Indian" sentiment was in many cases aimed squarely at Hindus — their festivals, their temples, their religious identity — and that hate incidents compounded through viral posts and "a coordinated core of prominent voices," some amplified by foreign state actors.

Political strategist Anang Mittal unveiled a Citation Integrity Dashboard, a non-partisan tool designed to evaluate whether high-profile institutional claims about Hindu Americans are actually supported by verifiable evidence.

## A veteran's testimony and a youth panel's lessons

Perhaps the most striking moment came from Ruchir Bakshi, a Hindu veteran who served combat tours in Afghanistan and Iraq with the U.S. Army. Bakshi spoke about how the Bhagavad Gita taught him that "true service means acting with discipline and integrity without attachment to outcome" — and that the same self-mastery could guide civic engagement without requiring anyone to surrender their Hindu identity.

The CoHNA Youth Action Network's Rutgers University chapter presented a panel on its multi-year journey of advocacy on campus — from fighting for representation and protesting Hinduphobic events to engaging university administrators and eventually hosting its own academic conference on Hinduism.

Allies from the Armenian and Jewish communities also spoke, alongside a city council member from Maple Grove, Minnesota, underscoring the event's interfaith dimensions.

## What comes next

"It was gratifying to see so many lawmakers — both Democrats and Republicans — unite against temple attacks and anti-Hindu hate, and speak up for religious freedom for American Hindus," said Sudha Jagannathan, CoHNA's director of government relations. "The future belongs to those who show up and advocate."

The community is growing. Indian Americans are now the largest Asian-alone group in the United States, numbering nearly 4.4 million — a 55 percent increase over the past decade. The political infrastructure is catching up. Whether that translates into durable policy protections remains the open question. But for one July afternoon on Capitol Hill, the answer, at least, was bipartisan."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Long Island's India Day Parade Turns Fifteen. The Guest List Now Includes State Senators.",
        "subheadline": "The curtain raiser for the 15th India Day Parade USA packed 250 people into a government building in Mineola — a far cry from the modest procession that started the tradition in 2011.",
        "slug": make_slug("india-day-parade-usa-15th-curtain-raiser-mineola-long-island"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "What began as a small community parade on Long Island has grown into a celebration so large it draws state senators, county comptrollers, and Indian consular officials — a measure of how deeply Indian Americans have woven themselves into suburban New York's civic fabric.",
        "tags": ["nri", "diaspora", "india-day-parade", "long-island", "new-york", "cultural-celebration", "india-independence"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/2026/06/22/15th-india-day-parade-usa-2026-curtain-raiser-draws-a-full-house-kicking-off-preparations-for-a-grand-celebration-of-indias-80th-independence-anniversary/"},
            {"name": "Swadesi", "url": "https://swadesi.com/"},
            {"name": "South Asian Herald", "url": "https://southasianherald.com/"}
        ]),
        "score_total": 65,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17999918/pexels-photo-17999918.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Indian tricolor flags waving during a patriotic celebration",
        "image_attribution": "Pexels",
        "body": """The Theodore Roosevelt Executive and Legislative Building in Mineola, New York, is designed for county hearings and zoning disputes — not for standing ovations. On a recent evening, it got both.

More than 250 people packed the government building for the curtain raiser of the 15th India Day Parade USA, the annual celebration of Indian independence and Indian American identity that has become Long Island's premier multicultural event. Additional guests stood along the walls. The parade itself — scheduled for August 23 in Hicksville — will mark both the 80th anniversary of India's independence and, more quietly, the maturation of a community that once had to explain what the tricolour meant.

## From a modest march to a political event

Fifteen years ago, the India Day Parade USA started as a modest community procession — one of several attempts by Indian Americans on Long Island to carve out visible cultural space in the suburbs. Today, the curtain raiser alone attracts sitting elected officials.

This year's guest list included New York State Senator Steven D. Rhoads, North Hempstead Town Supervisor Jennifer DeSena, New York State Assembly Member Jake Blumencranz, Nassau County Comptroller Elaine Phillips, and Consul Tsewang Gyaltson from India's Consulate General in New York. Their presence, parade organisers noted, underscored how far the event has come from its origins.

"The India Day Parade has become one of the region's most significant celebrations of Indian heritage, bringing together people from all backgrounds to honour the values of freedom, unity, diversity, and community service," said Pradeep Tandon, the parade's general secretary, in his opening remarks.

## The people who built it

The evening was as much a recognition of individual labour as a preview of August's festivities. Parade founder Bobby Kalote reflected on the organisation's journey and the volunteers, sponsors, and community leaders whose work transformed a local parade into a regional institution.

President Vimal Goyal paid special tribute to Venus Bhasin, a long-time supporter who, in Goyal's telling, had never received the recognition he deserved. "He has been a great supporter of India Day Parade USA for several years, bringing numerous sponsors and helping raise substantial funds for the organisation," Goyal said. "He is truly a devoted son of Mother India." The audience responded with what organisers described as a warm and sustained round of applause.

President Deepak Bansal emphasised the parade's role as a vehicle for intergenerational cultural transmission. "India Day Parade USA is proud to honour community leaders whose contributions have strengthened and enriched the Indian American community," he said, encouraging attendees to "engage younger generations and showcase the beauty and diversity of India."

Special recognition was also accorded to Dr. Tarun Wasil, Shashi Malik, Dincil George of the Queens Parade, and Acharya Ji of Arya Samaj — figures whose work, organisers said, had strengthened the broader ecosystem of Indian community organisations in the New York metropolitan area.

## Music, patriotism, and what comes next

The programme included performances by young artists Vaishavi Randev and Arshdeep Kaur, followed by patriotic songs from singer Anil Dua. The evening's headline act was Khuda Baksh, a finalist from Indian Idol Season 9, whose performances had the audience singing along and, by several accounts, dancing in the aisles of a building more accustomed to property tax debates.

The parade's trajectory mirrors a broader demographic story. Indian Americans are the fastest-growing major Asian group in the United States, with a 55 percent increase over the past decade to nearly 4.4 million people. In Nassau County and the broader Long Island region, that growth has translated into visible political representation, commercial presence, and — perhaps most importantly — cultural confidence.

The 15th India Day Parade USA will take place on Sunday, August 23, 2026, in Hicksville, New York. If the curtain raiser is any indication, the organisers may need a bigger venue next year.

## A parade ecosystem

The Long Island event is one of several India Day parades across the New York metropolitan area. The Federation of Indian Associations (FIA) organises its own — the 43rd edition — on Madison Avenue in Manhattan, complete with Bollywood celebrity appearances and the lighting of the Empire State Building in the Indian tricolour. The Queens Parade, led by Dincil George (who was honoured at the Mineola event), caters to its own community.

Together, they form something like an ecosystem — overlapping but distinct celebrations that collectively represent what may be the most elaborate annual display of Indian cultural identity outside India itself. That three separate parades can thrive within a 30-mile radius says more about the community's size and ambition than any census statistic."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
