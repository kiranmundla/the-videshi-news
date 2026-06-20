#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
for cand in [Path.home()/".env.supabase", Path.home()/"workspace"/".env.supabase"]:
    if cand.exists():
        for line in cand.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
        break

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

body1 = """The H-1B lottery, the annual coin-flip that has decided the American futures of hundreds of thousands of Indians for two decades, is being quietly retired. In its place comes a system that does not pretend to treat everyone equally — and that is precisely the point.

Under a Department of Homeland Security final rule that took effect on February 27, 2026, and governs the FY 2027 cap season already underway, registrations are no longer drawn at random. Each unique beneficiary is now entered into the selection pool a number of times tied to the Department of Labor wage level the job offer meets: four entries for a Level IV (highest-paid) position, three for Level III, two for Level II, and a single entry for Level I. The arithmetic is blunt. A senior architect earning a top-percentile wage is four times more likely to be picked than a fresh graduate offered an entry-level salary for the same occupation.

## Why the wage level is the whole game

For Indian applicants, the wage level is not a footnote — it is the new gatekeeper. The largest single bloc of H-1B beneficiaries every year is Indian, and a disproportionate share of them are recent master's graduates moving from STEM OPT into their first professional role. Those first jobs are overwhelmingly classified at Level I or Level II. Under random selection, a new graduate and a 15-year veteran had identical odds. Under weighted selection, the graduate's single entry competes against the veteran's four.

DHS received 2,731 public comments objecting to exactly this outcome and finalized the rule without changing a word of the regulatory text. The agency rejected carve-outs for new graduates, for U.S. degree holders, and for small employers, arguing that entry-level candidates would retain "meaningful — though reduced" chances. The honesty is almost disarming: reduced is the operative word.

## The mechanics employers cannot game

The rule closes the obvious loopholes before they open. Employers must declare the SOC code, the worksite, and the wage level at the registration stage, not later. If a position spans multiple sites, the *lowest* applicable wage level is used. If several employers register the same person, the beneficiary is assigned the lowest wage level offered among them. And the wage level locked in at registration must match the petition that follows — inflate the number to win the draw, and the petition that arrives in April will not survive scrutiny.

That consistency mandate matters for the staffing-and-consultancy model that has historically driven Indian H-1B volume. Body shops thrived on submitting large numbers of entry-level registrations and playing the odds. Weighted selection plus the separate $100,000 consular fee — currently tangled in litigation but still casting a long shadow — makes that strategy close to unworkable.

## What it means for an Indian professional right now

If you are early-career, the message is uncomfortable but clear: your selection odds are now a function of your salary, and the cleanest way to improve them is to negotiate a job classified at a higher wage level, or to target employers and metros where the prevailing wage for your role sits higher. Geography is now strategy — the same software role carries different OEWS wage thresholds in different cities.

If you are mid-career and well-paid, the rule is, bluntly, good news. Your three or four entries now compete against a thinner field as body-shop registrations collapse, and the overall selection rate for higher-wage candidates is expected to rise.

There is one more wrinkle Indians should not miss. Selection is not approval. A registration drawn from the weighted pool still becomes a full petition that must prove specialty-occupation eligibility — and the Level I wage that already drew extra Requests for Evidence on the petition side now also buys you the fewest lottery entries on the front end. The disadvantage compounds.

## The bigger picture

Washington has framed this as protecting American wages. For the Indian diaspora, the practical effect is a structural tilt away from the young graduate and toward the established professional — a reordering of who gets to stay. The lottery was capricious but blind. Its replacement is deliberate, and it has decided that in the contest for 85,000 visas, a higher salary is now the surest ticket.

For an entire generation of Indian students who built their American plans around the master's-degree-to-H-1B pipeline, the ground has shifted under the most important roll of the dice they will ever make."""

body2 = """While Washington spends its energy raising the cost of bringing Indian talent to America, the work is quietly going the other way. India's global capability centres — the in-house offices that multinationals run on Indian soil — are absorbing precisely the high-value technology jobs that the H-1B squeeze is pushing out of the United States.

The numbers are no longer a forecast. India's offshore technology centres generated an estimated $98.4 billion in revenue in fiscal 2026, according to industry body Nasscom and consultancy Zinnov — a figure that nearly hits the level once projected for 2030. The country added or expanded more than 100 GCCs in the year, including new centres from Anthropic, Eli Lilly, FedEx, Marriott and Lufthansa. By the end of 2026, India is expected to host roughly 2,117 such centres employing 2.36 million people.

## From back office to brain trust

The old story of Indian outsourcing — call centres and back-office paperwork — is obsolete. JPMorgan Chase, McDonald's and Nvidia now route higher-value functions through their Indian capability centres: finance, R&D, core software development, and increasingly the AI engineering that sits at the centre of every corporate roadmap. The work crossing the ocean is no longer the work nobody wanted. It is the work that, a decade ago, would have justified an H-1B petition.

That shift has a direct cause. The $100,000 fee on new consular H-1B petitions, signed in September 2025, made the math of relocating a mid-salary engineer to the United States indefensible for most employers. The median H-1B salary at Indian IT firms runs between $80,000 and $120,000 — meaning the visa fee alone can exceed a year's pay. Brokerages tracking the sector were unsentimental: Emkay Global said the fee "reinforces a shift toward offshore and nearshore delivery for roles that do not require presence in the US," and Nuvama expects firms to restrict H-1B use to "absolutely critical and irreplaceable" profiles.

## The localisation that was already happening

Indian IT majors did not wait for the fee to read the room. Wipro now says 80% of its US workforce is locally hired; L&T Technology Services puts its US local-hire share above 50%. JM Financial estimates that H-1B holders make up just 1.2% to 4.1% of the total headcount at the top 10 Indian IT firms. The visa that once defined the industry's American strategy has become a rounding error in it.

The result is a margin story as much as an immigration one. Infosys, HCLTech, Tech Mahindra, Persistent and LTTS have all cited offshoring and nearshoring as drivers of improved operating margins, with HCLTech booking a 110-basis-point quarterly jump. Moving the work to Bengaluru rather than the worker to New Jersey is cheaper, faster, and no longer politically fraught.

## What it means for the diaspora

For the Indian professional, this is the immigration debate's quiet plot twist. The conventional anxiety — will I get the visa, will I keep my status, will I survive the 60-day grace period after a layoff — assumes that the career and the country are the same decision. The GCC boom severs them. A growing share of the most ambitious technology work an Indian engineer could want is now available *in India*, at globally competitive compensation, without a lottery, a consular interview, or a priority date measured in decades.

For NRIs already in America, the implications cut two ways. Those facing visa uncertainty or weighing a return now have a destination that is not a step down — the reverse-migration option has become a genuine career choice rather than a defeat. But for the diaspora's long-term influence, there is a subtler cost: each function that lands in a Bengaluru or Hyderabad capability centre instead of a US office is a future Indian-American household that never forms, a green-card line that one fewer person ever joins.

## The structural read

America is not closing the door on Indian talent so much as relocating the room. The H-1B program is being rationed toward the highest-paid; the rest of the work is finding its level in India's GCCs, where the talent already lives. The policy aimed at protecting American jobs is, with some irony, accelerating the build-out of a parallel high-end technology economy 8,000 miles away — one staffed by exactly the people the visa system is now turning back."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The H-1B Lottery Is Dead. The New System Has Already Picked Its Winners — and They're Not New Grads",
        "subheadline": "DHS's wage-weighted selection rule replaces the random draw for FY 2027, handing four lottery entries to the highest-paid and a single entry to entry-level applicants. For India's master's-to-H-1B pipeline, the odds just collapsed.",
        "slug": make_slug("h1b-wage-weighted-selection-rule-lottery-replaced-entry-level-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are the largest bloc of H-1B beneficiaries and disproportionately fill entry-level (Level I-II) roles straight out of US master's programs; the new wage-weighted lottery cuts their selection odds while favoring higher-paid mid-career professionals.",
        "tags": ["h1b", "uscis", "dhs", "wage-weighted-selection", "lottery", "immigration", "opt"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Federal Register — Weighted Selection Process Final Rule", "url": "https://www.federalregister.gov/documents/2025/12/29/2025-23853/weighted-selection-process-for-registrants-and-petitioners-seeking-to-file-cap-subject-h-1b"},
            {"name": "USCIS — FY 2027 H-1B Cap Registration", "url": "https://www.uscis.gov/newsroom/news-releases/dhs-changes-process-for-awarding-h-1b-work-visas-to-better-protect-american-workers"},
            {"name": "Mondaq — DHS Finalizes Wage-Weighted Lottery for FY 2027", "url": "https://www.mondaq.com"},
            {"name": "Lexology — DHS Weighted Selection Process Effective Feb. 2026", "url": "https://www.lexology.com"}
        ]),
        "score_total": 86,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/USCIS_HQ_Groundbreaking_Ceremony_%2838096348641%29.jpg/1280px-USCIS_HQ_Groundbreaking_Ceremony_%2838096348641%29.jpg",
        "image_caption": "U.S. Citizenship and Immigration Services, which now runs a wage-weighted H-1B selection process for the FY 2027 cap.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Washington Made the H-1B Costlier. India's Capability Centres Are Quietly Collecting the Jobs",
        "subheadline": "As the $100,000 visa fee and a wage-weighted lottery price mid-level talent out of America, India's GCCs hit $98.4 billion in revenue and added 100-plus centres in a year. The work is migrating even when the workers can't.",
        "slug": make_slug("india-gcc-boom-h1b-fee-offshoring-tech-jobs-diaspora-reverse-migration"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The H-1B squeeze is pushing high-value tech work to India's global capability centres, giving NRIs a genuine in-India career alternative — but quietly shrinking the future flow of Indians into the US green-card pipeline.",
        "tags": ["h1b", "gcc", "offshoring", "indian-it", "immigration", "reverse-migration", "tcs-infosys-wipro"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — India's offshore tech hubs hit $98.4 bln revenue in FY26", "url": "https://www.reuters.com"},
            {"name": "Outlook Business — Indian IT Firms to Boost Offshoring Amid H-1B Fee Hike", "url": "https://www.outlookbusiness.com"},
            {"name": "The Hindu BusinessLine — Indian IT majors cut H-1B dependence amid localisation push", "url": "https://www.thehindubusinessline.com"},
            {"name": "Nasscom-Zinnov GCC report 2026", "url": "https://nasscom.in"}
        ]),
        "score_total": 79,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36665297/pexels-photo-36665297.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A modern high-rise at dusk in Bengaluru, the heart of India's global capability centre boom.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body2
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']} ({wc} words): {e}")
