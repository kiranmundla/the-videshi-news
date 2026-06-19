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

body1 = """India deported far fewer of its citizens from the United States this year than last — and New Delhi wants the number on the record. At the Ministry of External Affairs' weekly briefing, spokesperson Randhir Jaiswal put the 2026 figure at 1,076 Indian nationals removed so far, against 3,567 for all of last year. He framed it as evidence that quiet diplomacy is working. The arithmetic is more complicated than that.

A two-thirds drop sounds like relief. But the year is not over, and the comparison flatters the present by leaning on a brutal 2025, when chained-and-shackled deportation flights to Amritsar became a political flashpoint in India. Measured against a normal year rather than a record one, 1,076 removals is not a small number. It is a steady drumbeat.

### The enforcement backdrop

The MEA figure lands the same week that broader U.S. enforcement data showed the scale of the machine Indians are a small slice of. The Department of Homeland Security says roughly 900,000 people have been deported by ICE this year, with removal flights hitting a new monthly high in May. DHS also claims 2.2 million "self-deportations" — a figure immigration researchers have openly questioned, with one prominent analyst calling it oversold and likely inflated by counting all foreign-born departures.

For the Indian diaspora, the takeaway is not the headline total but the composition. The 1,076 removed Indians span criminal cases, visa overstays, and the undocumented — including the human cost of the so-called "dunki" route, the irregular crossings through Latin America that have drawn thousands of young Indians, many from Punjab and Gujarat, into smuggling networks and then into ICE custody.

### Why this matters to Indian Americans

It is tempting for a settled NRI on an H-1B or a green card to read deportation news as someone else's problem. That instinct is getting riskier. The same administration driving the removal numbers is also widening denaturalization — the Justice Department has signaled plans to file at least 250 cases by October, already filing 29 this year against naturalized Americans it accuses of fraud. The line between "us" (legal, documented, secure) and "them" (undocumented, removable) is thinner than it looked a year ago.

There is also the diplomatic layer. Jaiswal stressed that bilateral talks on "migration and mobility" continue at senior levels. India is trying to expand legal professional and student pathways while cooperating on the return of undocumented citizens — a transactional bargain in which deportation cooperation becomes a chip in negotiations over H-1B access and a possible mobility framework. NRIs are, in effect, the stakes in that bargain.

### What's next

New Delhi has every incentive to keep verifying that those being removed are genuinely Indian nationals before accepting flights — the verification process is itself a brake on the pace. Expect the MEA to keep publishing comparative figures, because a falling number is good politics at home.

For the diaspora, the practical advice is unglamorous and unchanged: keep status documents current, avoid lapses, and treat any brush with the legal system as an immigration event, not just a legal one. The deportation count may be down. The apparatus producing it is not."""

body2 = """The wait to put a stamp in a passport at a U.S. consulate in India has quietly gotten worse, and the one escape valve that used to exist has closed. According to a fresh advisory from immigration firm Fragomen, appointment backlogs for H, L and other employment-based nonimmigrant visas have stretched to 75 to more than 125 days across Chennai, Hyderabad, Kolkata, Mumbai and New Delhi.

The detail that stings most is Kolkata. It was long the insider's shortcut — a post with a 13-day wait when the big metros were jammed. That backdoor is now bolted shut: Kolkata's wait has ballooned to 126 days. There is no longer a fast lane.

### A backlog with a single cause

The diagnosis is not mysterious. Demand for U.S. visas has climbed over recent months while consular staffing at the U.S. mission to India has not moved. Layered on top is the State Department's expanded "online presence" review — the social-media vetting requirement extended to H-1B and H-4 applicants — which forces officers to spend more time per case and conduct fewer interviews each day. More applicants, more scrutiny per applicant, the same number of officers. The queue was the inevitable result.

Notably, the pain is concentrated on workers. Fragomen pegs B-1/B-2 visitor and F-1 student visa waits at just four to 22 days. It is the employment categories — the heart of the Indian professional diaspora — bearing the brunt.

### Why this matters to Indian Americans

For an H-1B holder in Texas or California weighing a summer trip home, this is the difference between a vacation and a career interruption. If your visa stamp has expired and you travel to India for stamping, a 125-day appointment wait means roughly four months stranded abroad — months in which an employer cannot legally keep your role open indefinitely, remote work from outside the U.S. runs into payroll and tax complications, and an H-4 spouse and children face the same limbo.

The third-country workaround that some have used — applying as a Third-Country National at a consulate outside India — still exists but is shrinking. It carries extra travel cost, may require a separate visa for the transit country, and consulates increasingly restrict eligibility for non-residents. It is a gamble, not a guarantee.

### What's next

Relief, if it comes, is structural and slow. The Trump administration's domestic visa-renewal pilot — slated to begin in December and aimed squarely at Indian H-1B holders already inside the U.S. — is the real fix, because it lets workers renew without leaving the country at all. Until that federal register notice publishes and the program scales, the calculus for diaspora workers is blunt: if your stamp is valid, do not let it lapse; if it has expired, think very hard before booking that flight home.

The consular bottleneck is not a glitch to be cleared in a few weeks. It is the predictable output of more demand, more vetting, and flat staffing — and it will outlast this travel season."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India Deported a Third as Many Citizens From the US This Year. New Delhi Calls It Progress",
        "subheadline": "The MEA put the 2026 figure at 1,076 against last year's 3,567 — but the comparison leans on a record year, and the enforcement machine behind it is only getting bigger.",
        "slug": make_slug("india-us-deportations-1076-mea-2026-enforcement-diaspora"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Settled NRIs once read deportation news as someone else's problem, but with denaturalization cases widening and removals used as a chip in US-India mobility talks, the diaspora is increasingly part of the bargain.",
        "tags": ["deportation", "ice", "mea", "denaturalization", "us-india", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Livemint — How Trump's immigration crackdown is affecting Indians: 1,076 deportations in 2026", "url": "https://www.livemint.com/news/india/how-trumps-immigration-crackdown-is-affecting-indians-1076-deportations-in-2026"},
            {"name": "Washington Examiner — Nearly 900,000 deported by ICE under Trump as flights soared in May", "url": "https://www.washingtonexaminer.com/news/"},
            {"name": "CNN — Trump administration ramps up effort to revoke citizenship from naturalized Americans", "url": "https://www.cnn.com/2026/06/18/politics/denaturalization-trump-citizenship"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/392265/pexels-photo-392265.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A departures hall at a busy international airport, the funnel for removal flights.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Visa-Stamping Shortcut Just Closed: Kolkata's Wait Jumps to 126 Days as Indian Backlogs Deepen",
        "subheadline": "H and L appointment waits now run 75 to 125-plus days across every major Indian consulate, and the social-media vetting mandate means the queue isn't clearing soon.",
        "slug": make_slug("us-consulate-india-visa-backlog-kolkata-126-days-h1b-stamping"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For an H-1B holder with an expired stamp, a 125-day appointment wait turns a trip home into four months stranded abroad — long enough to lose the job the visa was for.",
        "tags": ["h1b", "consulate", "visa-stamping", "h4", "social-media-vetting", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fragomen — Update on Visa Appointment Backlogs at U.S. Consulates in India", "url": "https://www.fragomen.com/insights/update-on-visa-appointment-backlogs-at-u-s-consulates-in-india.html"},
            {"name": "VisaVerge — U.S. H-1B Visa Backlog Pushes Interview Slots Into 2027", "url": "https://www.visaverge.com/news/u-s-h-1b-visa-backlog-pushes-interview-slots-into-2027/"},
            {"name": "Reddy Neumann Brown PC — Consulates Pushing H-1B & H-4 Interviews to Mid-2026", "url": "https://www.rnlawgroup.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/US_Embassy_New_Delhi.jpg/1280px-US_Embassy_New_Delhi.jpg",
        "image_caption": "The U.S. Embassy in New Delhi, where visa demand has outpaced flat consular staffing.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": body2
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   words={wc} | {art['headline'][:60]}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
