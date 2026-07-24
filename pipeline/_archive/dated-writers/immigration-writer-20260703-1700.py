#!/usr/bin/env python3
"""
Immigration writer — July 3 2026, 5:00 PM PT
Two articles:
1. America turns 250, and Indian immigrants are still waiting
2. Indian-founded unicorns vs. shrinking H-1B pipeline
"""
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

# ── Article 1 ─────────────────────────────────────────────────────────────────

article1_body = """America's semiquincentennial lands on a Friday this year. Fireworks will arc over the National Mall, speeches will invoke the founders, and somewhere in the suburbs of New Jersey or the cul-de-sacs of Cupertino, an Indian engineer on an H-1B visa will watch the celebrations from a country that will not grant him permanent residency for another two decades.

The dissonance is hard to miss. The United States turns 250 on July 4, 2026 — a quarter-millennium built, in large and measurable part, by people who came from somewhere else. Immigrants or their children founded or co-founded 59 per cent of America's billion-dollar startup companies, according to the National Foundation for American Policy. Indian-born entrepreneurs alone account for 96 of those unicorns, more than any other country. The collective valuation of immigrant-founded startups stands at $5 trillion, exceeding the total stock market capitalisation of the United Kingdom.

And yet the anniversary arrives at the most hostile moment for legal immigration in modern American history.

## The ledger

Consider what has happened in the twelve months leading up to this birthday. EB-2 India — the employment-based green card category that covers most Indian tech professionals — went dark in the July 2026 Visa Bulletin. No green cards will be issued in that category through the end of the fiscal year in September. EB-1 India, the category for those with "extraordinary ability," retrogressed to October 2022. The backlog for an Indian-born engineer filing today stretches past 2040 at current rates.

The administration imposed a $100,000 fee on new H-1B petitions — a federal judge struck it down in June as an unconstitutional tax, but the White House has promised to appeal. H-1B registrations for FY2027 dropped 38.5 per cent year-on-year as the new wage-weighted lottery reshaped who gets selected. Indian IT companies saw their H-1B approval counts fall 40 per cent. Naturalization fees rose 75 per cent. USCIS even cancelled its traditional Fourth of July naturalization ceremonies for the 250th anniversary — the one day that was supposed to be about welcoming new Americans.

F-1 visa grants to Indian students fell 69 per cent. The pipeline that feeds the H-1B system, which in turn feeds the green card queue, which in turn produces the founders and executives who run America's most valuable companies, is contracting at every stage.

## Who built this

The Reuters columnist Hugo Dixon put it plainly this week: "The not-so-secret formula to 250 years of U.S. success is immigration." Enslaved Africans built the southern economy. European migrants powered northern industry. Asian workers constructed the railroads and western cities. Latin American and Caribbean arrivals supplied the backbone of agriculture and manufacturing.

The Indian chapter of that story is more recent but no less consequential. Jay Chaudhry, born in a Himachal Pradesh village without running water, founded Zscaler — now worth more than many S&P 500 companies. Vinod Khosla, an IIT Delhi graduate, co-founded Sun Microsystems and reshaped venture capital. Aravind Srinivas, who arrived as a student, built Perplexity AI to a $20 billion valuation in three years. Six Indian-born founders have each built two or more billion-dollar companies: Mohit Aron, Jyoti Bansal, Ashutosh Garg, Arvind Jain, Sachin Nayyar, and Ajeet Singh.

Seventy-six of the 96 Indian unicorn founders first entered the United States on student visas. They took the path that is now being narrowed: F-1 to OPT to H-1B to green card to company. Remove any link in that chain and the next Jay Chaudhry stays in Himachal Pradesh.

## The mood in the diaspora

Indian Americans are not, for the most part, at risk of deportation. They are not the targets of ICE worksite raids. They hold valid visas, pay taxes, and show up at PTA meetings. But they are trapped in a bureaucratic limbo that the 250th anniversary makes painfully visible.

A software engineer who arrived in 2010 and filed for a green card in 2012 is still waiting. His American-born children are in high school. He has changed jobs three times, each time navigating the transfer of his pending petition. His wife, on an H-4 dependent visa, only recently gained the right to work — a right the administration has tried to revoke. He watches the Fourth of July fireworks as a taxpaying, law-abiding, decade-and-a-half resident of a country that classifies him as a temporary visitor.

There are roughly a million Indians in that queue. The per-country cap, a relic of the 1990 Immigration Act, limits any single nation to seven per cent of employment-based green cards regardless of demand. A country that sends the most unicorn founders, the most STEM graduate students, and the most H-1B workers gets the same allocation as Iceland.

## What 250 means

Countries celebrate their birthdays to remind themselves what they are. At 250, the United States is being asked — by its own history, its own data, its own $5 trillion of immigrant-built wealth — whether it still believes in the proposition that brought these people here.

The answer, at the moment, is ambiguous. The laws say yes. The backlogs say wait. The fees say pay more. The rhetoric says you are not wanted. The NFAP data says you built this.

Indian Americans will light sparklers tomorrow, grill kebabs alongside hamburgers, and explain to their children what the Fourth of July means. Some of them will wonder, not for the first time, whether it means what it says."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "America Turns 250. A Million Indians Are Still Waiting for Green Cards",
    "subheadline": "The country celebrates its semiquincentennial on the backs of immigrants who built $5 trillion in startup wealth — and still cannot become permanent residents.",
    "slug": make_slug("america-250th-birthday-indian-immigrants-green-card-wait"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian Americans are among the most successful immigrant communities in US history, yet face the longest green card backlogs — a contradiction that America's 250th birthday makes impossible to ignore.",
    "tags": ["immigration", "green-card", "h1b", "july-4", "america-250", "indian-diaspora", "nfap", "unicorns"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "National Foundation for American Policy", "url": "https://nfap.com/"},
        {"name": "Reuters - Hugo Dixon", "url": "https://www.reuters.com/"},
        {"name": "LiveMint - NFAP Study", "url": "https://www.livemint.com/news/world/indian-immigrants-built-96-unicorns-in-america-now-worth-more-than-germanys-stock-market-11780642420018.html"},
        {"name": "VisaVerge - July 2026 Visa Bulletin", "url": "https://www.visaverge.com/"},
        {"name": "USCIS", "url": "https://www.uscis.gov/"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6133108/pexels-photo-6133108.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "The Statue of Liberty and American flag in New York City",
    "image_attribution": "Pexels",
    "body": article1_body
}

# ── Article 2 ─────────────────────────────────────────────────────────────────

article2_body = """There is a number that should hang in every congressional office considering immigration legislation: 96. That is how many American billion-dollar companies were founded or co-founded by Indian-born immigrants, according to the National Foundation for American Policy's latest analysis of 775 US unicorns. India leads every other country by a wide margin — Israel is second with 60, the United Kingdom third with 47.

The $5 trillion question is whether the system that produced those founders still works. The evidence suggests it is breaking down.

## The pipeline that was

The path was never easy, but it was legible. An Indian student arrived on an F-1 visa, earned a master's or PhD in computer science or electrical engineering, moved to Optional Practical Training, entered the H-1B lottery, and — if selected — began the long march toward a green card. Along the way, some started companies. Perplexity AI's Aravind Srinivas took that route. So did Arvind Jain of Glean, Ashutosh Garg of Eightfold AI, and Mohit Aron of Cohesity.

NFAP found that 76 of the 96 Indian unicorn founders first arrived as international students. Across all countries, 233 former international students went on to found or co-found billion-dollar companies. Companies founded by student-visa alumni employ an average of 1,123 people each.

The pipeline was working. It is now being dismantled at every junction.

## Every junction, simultaneously

Start at the entry point. F-1 visa grants to Indian students fell 69 per cent, according to State Department data. Administrative processing delays at Mumbai and Hyderabad consulates run four to six months for STEM applicants. The Department of Homeland Security has proposed eliminating "Duration of Status" for student visas, replacing open-ended stays with fixed four-year terms and mandatory USCIS extensions.

Move to the next stage. H-1B registrations for FY2027 dropped 38.5 per cent to 211,600 eligible entries, down from 343,981 the prior year. The new wage-weighted lottery, which took effect for the FY2027 cycle, gives four entries to Level IV wage positions and one to Level I. The stated goal is to prioritise higher-skilled workers. The practical effect is to compress the already-narrow path for early-career immigrants — exactly the stage at which most future founders are working their first American job.

A record 71.5 per cent of selected FY2027 applicants hold US advanced degrees. That sounds like the system is working as intended until you realise the pool is dramatically smaller. The Brookings Institution reported that 2025 marked the first year of net negative migration in the United States in half a century.

Move further down the chain. EB-2 India — the green card category most Indian H-1B holders file under — is unavailable through September 2026. No final approvals until the next fiscal year. EB-1 India retrogressed to October 2022. The per-country cap means an Indian applicant filing today could wait until the 2040s.

## What the data says about what America loses

The NFAP study is blunt about the stakes. Immigrant-founded unicorns are collectively valued at $5 trillion, exceeding the stock market capitalisation of every country except six. SpaceX alone, co-founded by South Africa-born Elon Musk, is valued at $1.5 trillion. Anthropic sits at $965 billion. OpenAI at $852 billion.

Among Indian-founded companies, the standout valuations include Perplexity AI at $20 billion, Cohesity, Rubrik, Glean, and Eightfold AI. Six Indian founders have each built two or more billion-dollar companies — 40 per cent of all immigrant repeat founders identified in the study.

Stuart Anderson, NFAP's executive director, framed the finding carefully: "Immigration restrictions could threaten America's technological leadership and competitiveness." The entrepreneurs in the study "typically came from modest means, including as children or international students, before achieving the American Dream."

Jay Chaudhry, founder of Zscaler, arrived from a village in Himachal Pradesh without electricity. His net worth is now $13.1 billion. Vinod Khosla, an IIT Delhi alumnus, is worth $9.2 billion. The father of Hippocratic AI founder Munjal Shah arrived in the US carrying $16 on a steamship.

## The October summit and what it signals

The One Way Summit, scheduled for October 28-29 in San Francisco, will bring together over a thousand immigrant founders, investors, and technology leaders. Its timing — weeks after the new fiscal year begins and the H-1B cap resets — is deliberate. Khosla is among the speakers.

The conference exists because a constituency that built $5 trillion in American enterprise value has no organised political voice on immigration. Indian Americans vote, donate, and run companies, but they have not coalesced around the green card backlog the way other groups have around their issues. The summit is an attempt to change that.

## The arithmetic of self-harm

International students account for 80 per cent of full-time graduate enrolments in computer science at American universities, 75 per cent in electrical engineering, and 62 per cent in mathematics and statistics. These are not students taking American seats. These are students filling seats that American students are not applying for, at a scale that keeps entire departments running.

Every tightened visa rule, every fee increase, every months-long consular delay is a signal. Canada, the UK, Australia, and — increasingly — India's own GCC ecosystem are reading that signal clearly. A country that restricts the pipeline that produced 96 billion-dollar companies is not protecting its workforce. It is liquidating its future.

The founders are still out there — in IIT lecture halls, in Delhi co-working spaces, in Bangalore apartments writing code at 2 AM. The question is whether they will still come to America to build, or whether they will build somewhere else. At 96 unicorns, the answer has been America. At the current trajectory, the next NFAP study might tell a different story."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Indian Immigrants Built 96 US Unicorns. The Visa Pipeline That Made It Possible Is Collapsing",
    "subheadline": "NFAP data shows India leads all nations with 96 billion-dollar company founders, but H-1B registrations have dropped 38.5 per cent and the green card queue has gone dark.",
    "slug": make_slug("indian-founders-96-unicorns-h1b-pipeline-collapsing-nfap"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "76 of 96 Indian unicorn founders arrived on student visas — the exact pathway now being narrowed by Duration of Status changes, F-1 declines, and the weighted H-1B lottery.",
    "tags": ["nfap", "unicorns", "indian-founders", "h1b", "f1-visa", "startup", "immigration", "silicon-valley"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "National Foundation for American Policy (NFAP)", "url": "https://nfap.com/"},
        {"name": "LiveMint", "url": "https://www.livemint.com/news/world/indian-immigrants-built-96-unicorns-in-america-now-worth-more-than-germanys-stock-market-11780642420018.html"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
        {"name": "DevDiscourse", "url": "https://www.devdiscourse.com/article/business/3944244-immigrant-entrepreneurs-ignite-us-innovation-amid-tightening-visa-policies"},
        {"name": "VisaVerge - H-1B FY2027 Data", "url": "https://www.visaverge.com/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8344741/pexels-photo-8344741.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "A diverse team of professionals collaborating in a modern tech office",
    "image_attribution": "Pexels",
    "body": article2_body
}

# ── Insert ────────────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
