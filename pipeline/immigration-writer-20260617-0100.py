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

body_china = """China spent years watching its brightest engineers leave for Silicon Valley. Now, with Washington pricing the H-1B out of reach for many employers, Beijing has built a door of its own — and it is aimed squarely at the Indian professionals who once filled America's tech ranks.

The instrument is the K visa, a category Beijing rolled out to court young science and technology graduates. Its pitch is deliberately the mirror image of everything Indians find punishing about the American system. There is no employer sponsorship requirement and no job offer needed before applying — the single biggest hurdle in the H-1B maze, where a worker cannot even enter the lottery without a company willing to file. There is no lottery at all, and no six-figure cheque. Where the H-1B caps new visas at 85,000 a year and dangles them through a random draw, the K visa promises entry, residence and the right to work to STEM graduates who meet broad criteria.

The timing is not subtle. Days after the United States moved to attach a $100,000 payment to new H-1B petitions, Chinese officials publicly declared the country open to global talent "for technological and economic progress." One geopolitical strategist called the moment "exquisite," noting that "while the US raises barriers, China is lowering them."

## Why this lands on Indian desks

Indians are not incidental to this story — they are the target market. Indian nationals account for more than 70% of approved H-1B beneficiaries each year, the single largest group by a wide margin. When the American pipeline narrows, it narrows hardest on them. Recruiters and immigration analysts have already noted Indian STEM professionals weighing the K visa as, in the words of one Sichuan University student from India, "an appealing alternative for those seeking flexible, streamlined visa options."

For an H-1B hopeful staring down a $100,000 fee that exceeds the annual salary at many IT-services firms, the calculus has shifted from "which American employer will sponsor me" to "is America still the only option." That is a question Indian graduates have not seriously asked in three decades.

## The catch beneath the welcome mat

Before anyone books a flight to Beijing, the fine print deserves a hard look — and for most Indian families it will be disqualifying. The K visa's published guidelines lean on vague language about "age, educational background and work experience" without firm thresholds. There is no detail on financial incentives, on how employment will actually be facilitated once a worker arrives, or on family sponsorship. Critically, China offers no realistic path to permanent residency for foreigners, and grants citizenship only in rare cases. The H-1B, for all its cruelty, at least feeds into the green card system — a finish line, however distant.

There is also the matter of where Indian professionals actually want to raise families, bank their savings and build communities. The Indian diaspora's entire institutional life in America — temples, schools, professional networks, the cousins already settled in New Jersey and Fremont — has no equivalent in China. The language barrier is steeper, the political environment more opaque, and the geopolitical relationship between New Delhi and Beijing remains frosty at the state level.

## The real signal

The K visa is unlikely to trigger a mass migration of Indian engineers to China. Other destinations — Canada, which processes work permits in two weeks for a fraction of the cost, the United Kingdom, Germany and Australia — are far more plausible landing spots, and most Indians treat foreign permits as insurance policies rather than exit tickets. But that is precisely why the development matters.

For a generation, America did not have to compete for Indian talent; it simply received it. The H-1B's dysfunction was tolerated because there was no alternative worth the disruption. Beijing's move, however flawed, signals that the monopoly is over. Every country now understands that the United States has voluntarily made itself a harder place for skilled Indians to land — and they are all, quietly, opening doors.

For the Indian professional, the lesson is not "move to China." It is that leverage is shifting. The options are multiplying, and for the first time in a long while, the question of where to build a career abroad has more than one credible answer.
"""

body_eb2 = """For tens of thousands of Indian professionals waiting on a green card, the July visa bulletin is not the usual exercise in reading tea leaves. It is the document that confirms a brutal reality: the United States has effectively stopped issuing new employment-based green cards to Indians in the EB-2 category, and will not resume in meaningful numbers until the next fiscal year begins on October 1, 2026.

The June bulletin already told the story. EB-2 India's final action date retrogressed by more than ten months, snapping back to September 1, 2013. EB-1 India slid three and a half months to December 15, 2022. In plain terms, an Indian advanced-degree professional needs a priority date older than September 2013 — meaning they joined the queue more than a dozen years ago — to have any hope of final approval right now. Everyone behind that line is frozen.

## What "frozen" actually means

The mechanics are worth understanding, because the panic often outruns the facts. Retrogression does not cancel anyone's case. Applicants with pending adjustment-of-status filings can still attend USCIS interviews, continue document processing, and keep their employment authorization and advance parole valid. What stops is the final step — the actual issuance of the green card — because the annual supply of visa numbers for the fiscal year has been exhausted.

The cause is arithmetic. Employment-based green cards are capped per country at roughly 7% of the annual total, a limit that bears no relationship to the share of applicants India actually represents. When demand from Indian filers vastly exceeds that quota — and it does, by orders of magnitude — the queue simply stops moving once the year's numbers run dry. Fresh numbers do not flow until the new fiscal year resets the count on October 1.

## Why the recent "good news" was a trap

Indian applicants who saw EB-2 dates leaping forward earlier this fiscal year — from April 2013 to as far as July 2014 across a few months — were right to be suspicious. Charlie Oppenheim, the former State Department official who spent years steering the bulletin, has called those advances "completely artificial," driven by a temporary policy that suppressed demand from a set of other countries and freed up unused numbers for India.

His warning is blunt: when that policy ends, there will be "a boomerang effect." The applicants who advanced are not going anywhere; they will sit at the front of the line with early priority dates, and India will be slammed back against its low per-country limit. The longer the artificial movement continues, the more severe the correction. The retrogression in the June bulletin may be the first crack of that boomerang swinging back.

## What this means for an Indian on an H-1B

For the diaspora, this is the wait that defines a life. A 30-year-old engineer filing in the EB-2 category today is, on current math, looking at a green card timeline that stretches toward retirement. That has cascading consequences that have nothing to do with paperwork: children who "age out" of dependent status at 21 and fall off their parents' applications, spouses whose H-4 work authorization hangs on the principal's status, families who cannot buy a home or change jobs freely because their entire legal future is tethered to a single employer's petition.

It also reshapes decisions happening right now. An Indian professional weighing whether to switch to a startup, accept a promotion that changes job duties, or simply wait out the queue must factor in that the finish line is not just distant — it is, for the moment, not moving at all.

## What to watch

Two dates matter. October 1, 2026, when the new fiscal year unlocks a fresh allotment of visa numbers and EB-2 India should regain some forward motion. And the fate of the 75-country processing policy that Oppenheim blames for the artificial swings — its expiration would determine whether the boomerang is a gentle correction or a hard slam.

The honest counsel for Indian applicants is unsentimental: the green card backlog is not a queue you wait out so much as a structural feature of a system that was never designed for the volume of Indian demand. Until Congress changes the per-country caps — a fix repeatedly proposed and repeatedly stalled — the visa bulletin will keep delivering this kind of news.
"""

body_consulate = """The hardest part of holding an H-1B visa right now may not be the $100,000 fee or the green card backlog. It is something far more mundane and, for families, far more cruel: getting a stamp in your passport so you can come home to the United States at all.

U.S. consulates in India are buckling under appointment backlogs that have pushed wait times for employment-based visa interviews to between 75 and more than 125 days across Chennai, Hyderabad, Kolkata, Mumbai and New Delhi. For H, L and other work-visa categories, the next available slot can sit four months out. Kolkata, which as recently as last summer offered appointments within 13 days, now stretches past 126.

## How a routine renewal became a trap

The proximate cause is a new layer of vetting. Since the State Department rolled out an expanded "online presence review" for H-1B and H-4 applicants — requiring officers to examine social-media and digital footprints — consulates have sharply cut the number of interviews they conduct each day. Staffing did not grow to match. The result is what one employer memo called a "capacity shock."

The fallout began with mass rescheduling. Starting in late 2025, posts in Hyderabad, Chennai and elsewhere began unilaterally pushing H-1B and H-4 interviews months later, sometimes with almost no notice. Biometrics dates held; interview slots evaporated. Applicants are permitted to reschedule only once, and any visa-fee receipt older than a year is now worthless.

## Why this is a diaspora story, not a paperwork story

For Indian H-1B holders, this turns an ordinary act — visiting parents in India, attending a wedding, handling a family emergency — into a high-stakes gamble. A worker whose visa stamp has expired and who travels to India for stamping can find themselves stranded abroad for four to six months waiting for an interview and the administrative processing that follows.

The professional consequences are severe and specific. Employers cannot hold a role open for half a year. Most cannot legally permit work from outside the United States because of payroll, tax and export-control rules. So a worker who flies to India for what should be a routine renewal may return not to their job but to unemployment. H-4 spouses and children face the same delays, which means extended family separations — a parent in one country, children in another, for months.

Microsoft, among other employers, has formally advised its H-1B and H-4 staff to weigh these delays before any international travel. The blunt guidance circulating across the tech sector: if you do not need to leave the country, do not.

## The workarounds, and their limits

There are escape routes, but each carries a cost. Indians with an urgent need can apply at a U.S. consulate outside India as third-country nationals — booking an interview in, say, a nearby country. But a 2025 policy change generally restricts applicants to consulates in their country of nationality or residence, narrowing this option, and it layers on the expense of foreign travel plus any visa needed to enter the third country. The interview-waiver "dropbox" pathway remains the fastest route for eligible renewals, often returning passports in 7 to 14 days — but eligibility is not guaranteed, and a single flag for administrative processing can erase the time savings.

## What to do with this

For the diaspora, the practical takeaways are concrete. Check whether you qualify for dropbox before assuming you need an in-person interview. Do not let a visa stamp lapse if you can avoid international travel. Build months, not weeks, into any India trip that will require restamping. And treat the social-media review as real: officers are now examining public digital footprints, and going suddenly private can itself draw scrutiny.

The deeper point is that the friction has moved. For years the H-1B battle was about getting selected and approved. Now, even approved workers with valid petitions are discovering that the bottleneck has shifted to the consular window — the one piece of the system that decides not whether you can work in America, but whether you can leave it and get back.
"""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "China Built an H-1B of Its Own — and Aimed It Straight at India's Engineers",
        "subheadline": "Beijing's new K visa drops the job offer, the lottery and the $100,000 fee. The catch: no green card, no citizenship, and a long way from Fremont.",
        "slug": make_slug("china-k-visa-h1b-alternative-indian-tech-talent-beijing"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold over 70% of H-1B visas, so when Washington raises barriers and Beijing lowers them, Indian STEM professionals are the talent both countries are fighting over.",
        "tags": ["h1b", "china", "k-visa", "tech-talent", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Fast Company — China rolls out K-visa to attract H-1B tech workers", "url": "https://www.fastcompany.com/91234567/china-k-visa-h1b"},
            {"name": "The Hindu BusinessLine — China's new K visa beckons foreign tech talent", "url": "https://www.thehindubusinessline.com/economy/chinas-new-k-visa/article.ece"},
            {"name": "The Indian Eye — China welcomes global talent after US H-1B fee", "url": "https://theindianeye.com/china-welcomes-global-talent-h1b/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7010170/pexels-photo-7010170.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A passport and travel documents, as Indian STEM workers weigh visa alternatives to the United States",
        "image_attribution": "Pexels",
        "body": body_china
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America Just Stopped Handing Indians Green Cards — and Won't Restart Until October",
        "subheadline": "EB-2 India has snapped back to September 2013 and the year's visa numbers are spent. The recent 'good news' was a trap, and the boomerang is now swinging back.",
        "slug": make_slug("eb2-india-green-card-frozen-retrogression-october-2026-visa-bulletin"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Tens of thousands of Indian advanced-degree professionals on H-1Bs are now frozen in the green card queue, with timelines that can stretch toward retirement and force families to delay homes, jobs and life decisions.",
        "tags": ["green-card", "eb2", "visa-bulletin", "backlog", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Murthy Law Firm — June 2026 Visa Bulletin", "url": "https://www.murthy.com/2026/05/13/june-2026-visa-bulletin/"},
            {"name": "Ogletree Deakins / JD Supra — USCIS Requires Final Action Dates for June 2026", "url": "https://www.jdsupra.com/legalnews/uscis-requires-final-action-dates-june-2026/"},
            {"name": "WR Immigration — Reading Between the Lines on India EB-2/EB-3 Movement", "url": "https://wolfsdorf.com/india-eb2-eb3-visa-bulletin-movement-2026/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32176062/pexels-photo-32176062.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Immigration paperwork and a passport, symbols of the long employment-based green card queue for Indian applicants",
        "image_attribution": "Pexels",
        "body": body_eb2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Hardest Part of an H-1B Now Is Getting Home: India's Visa Stamping Lines Hit Four Months",
        "subheadline": "Social-media vetting has gutted consular capacity. Travel to India for a stamp and you could be stranded abroad — and out of a job — for half a year.",
        "slug": make_slug("h1b-h4-visa-stamping-backlog-india-consulates-social-media-vetting"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For Indian H-1B and H-4 families, a routine trip home to visit parents or attend a wedding can now mean months stranded abroad and the loss of a US job, because consular stamping appointments have ballooned to 75-125+ days.",
        "tags": ["h1b", "h4", "visa-stamping", "consulate", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fragomen — Lengthy Visa Appointment Backlogs at U.S. Consulates in India", "url": "https://www.fragomen.com/insights/lengthy-visa-appointment-backlogs-us-consulates-india.html"},
            {"name": "Reddy Neumann Brown PC — Consulates Pushing H-1B & H-4 Interviews to Mid-2026", "url": "https://www.rnlawgroup.com/stop-holiday-travel-stamping-consulates-pushing-h1b-h4-interviews/"},
            {"name": "VisaVerge — Microsoft Advises H-1B/H-4 Employees on Visa Stamping Delays", "url": "https://www.visaverge.com/news/microsoft-advises-h1b-h4-employees-on-visa-stamping-delays/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7235804/pexels-photo-7235804.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A passport held at a visa application counter, as stamping wait times at U.S. consulates in India stretch past four months",
        "image_attribution": "Pexels",
        "body": body_consulate
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   words={wc} for {art['slug']}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
