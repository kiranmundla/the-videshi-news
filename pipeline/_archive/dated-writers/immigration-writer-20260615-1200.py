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

body1 = """The EB-2 India queue went dark on May 22. Now the question every green-card holder-in-waiting is asking is which category falls next — and the State Department has already telegraphed the answer.

With the July 2026 Visa Bulletin due to land in mid-June, immigration lawyers are reading the June bulletin's warning sections like tea leaves. The picture they see is the most contractionary month of the fiscal year, and it lands hardest on Indians.

## The EB-2 India door is already shut

On May 22, the Visa Office posted a one-line notice with enormous consequences: "India per-country limit reached in the EB-2 category." Once a per-country annual limit is hit, the rule is mechanical — the affected cell lists as "U" (Unavailable) on both the Final Action and Dates for Filing charts through September 30. There is no discretion left, no analyst forecast required. EB-2 India is closed until October 1, when FY-2027 numbers reset.

For the hundreds of thousands of Indian professionals sitting in the EB-2 backlog, the practical effect is narrow but real. A pending I-485 is not denied — it simply cannot be approved until a visa number frees up. Work permits, advance parole, H-1B portability, and AC21 job-change protections all keep running during the freeze. But anyone hoping their priority date would finally become current this summer now waits another fiscal year, minimum.

The cruel twist: downgrading from EB-2 to EB-3 offers no escape. EB-3 India sits around December 15, 2013 — years behind where most EB-2 India priority dates fall.

## EB-1 India and EB-5 are the next dominoes

The June bulletin's Section E already retrogressed EB-1 India by more than three months, to December 15, 2022, and warned that "further retrogressions, or making the categories unavailable, may be necessary." With EB-2 India exhausted, EB-1 — the elite category for executives, researchers, and extraordinary-ability applicants — becomes the next pressure point. Most attorney forecasts place July's EB-1 India date somewhere between August and October 2022, a further pull-back of two to five months. An outright "U" listing before September 30 is plausible.

The sharpest warning, though, sits in Section H, aimed at EB-5 Unreserved India — the investor green-card route. Where the bulletin used vague "coming months" language for EB-2 China and EB-3 Philippines, it told EB-5 Unreserved India that action was coming "the next month." That timing-specific phrasing is the State Department's way of signaling an imminent move. The likely July outcome: either a retrogression of EB-5 Unreserved India from May 1, 2022 back into late 2020 or early 2021, or an outright freeze through September 30. The EB-5 set-aside categories — Rural, High Unemployment, and Infrastructure — are statutorily walled off and remain Current, which is exactly why immigration advisers have been steering Indian investors toward them.

## Why this matters for the Indian diaspora

No diaspora is more exposed to the green-card backlog than Indians. Decades of per-country caps stacked against a country that supplies the largest share of H-1B workers have produced waits measured in decades, not years. Every retrogression compounds an already generational problem.

The forecasts also expose how fragile this year's earlier "good news" was. Indian EB-2 dates leapt forward through the winter — but a former State Department official has argued those advances were "completely artificial," driven by reduced demand from 75 countries under current visa-processing policy. When that policy ends, the warning goes, there will be a "boomerang effect" sending India back to its low per-country limits. This summer's freeze may be the front edge of that correction.

There is one piece of genuine relief embedded in the calendar. October 1 resets every employment-based category. EB-2 India reopens, EB-1 India gets fresh numbers, and the queue starts moving again under FY-2027 quotas. For a worker whose I-485 has been pending for years, the freeze is a frustrating pause — not a denial, and not the end of the line.

The practical advice from immigration counsel is unchanged and unglamorous: lock in your priority date, file for adjustment of status whenever your category is current even briefly, and keep your EAD and advance parole renewed. You cannot control the bulletin. You can control whether you are ready the moment the door opens."""

body2 = """The scheme reads like a screenplay. Ten Indian nationals, scattered across Massachusetts, Kentucky, Ohio, and Mississippi, allegedly staged armed robberies of convenience stores — not to steal cash, but to manufacture crime victims who could then apply for U.S. visas.

A federal grand jury in Boston has indicted all ten on one count each of conspiracy to commit visa fraud, U.S. Citizenship and Immigration Services confirmed. They were first charged by criminal complaint in March; the indictment elevates the case toward trial.

## How the alleged scheme worked

The mechanism abused the U visa — a humanitarian category Congress created for victims of serious crimes who cooperate with law enforcement. A genuine victim of a violent robbery who helps police can petition for U nonimmigrant status, a pathway to legal residence designed to encourage immigrants to report crime without fear of deportation.

Prosecutors say the defendants weaponized that compassion. The alleged conspiracy involved orchestrating fake armed robberies of convenience and liquor stores so that the store clerks — co-conspirators in on the plan — could file U visa applications claiming to be traumatized victims of violent crime. The indictment names Jitendrakumar Patel, Maheshkumar Patel, Sanjaykumar Patel, Rameshbhai Patel, and others; one defendant, Dipikaben Patel, has already been deported to India.

This is not an isolated case. In August 2025, an Indian national named Rambhai Patel was sentenced to roughly 20 months and ordered to forfeit $850,000 for running a near-identical operation — at least 18 staged robberies across the country, including five in Massachusetts, with clerks paying thousands of dollars to be "robbed." The Boston indictment suggests investigators believe the model was franchised.

## A widening enforcement net

The timing is not coincidental. The case lands amid an aggressive federal push against immigration fraud committed by Indian nationals. In the same window, the Department of Justice filed denaturalization actions against 17 individuals, including New Jersey IT-staffing executive Neeraj Sharma, who was stripped of citizenship after filing eleven fraudulent H-1B petitions with forged corporate letterhead. Separately, two Indian nationals pleaded guilty to a multi-million-dollar robocall scam run out of a call center in Ahmedabad.

USCIS has made clear it views fraud detection as a priority, touting its "pivotal assistance" to the Boston investigation. Guidance issued in December 2025 reportedly directed field offices to refer 100 to 200 denaturalization cases per month to the DOJ in fiscal 2026 — a sharp escalation from the historical average of about 11 denaturalization filings a year.

## Why this matters for the Indian diaspora

For the overwhelming majority of Indian Americans who built their lives here through legitimate H-1B sponsorships, student visas, and years in the green-card queue, these cases are a liability they did not ask for. Fraud rings like the staged-robbery conspiracy hand ammunition to the loudest critics of legal immigration, who rarely distinguish between a criminal scheme and a software engineer on a decade-long EB-2 wait.

The reputational cost is real and measurable. Every "Indian nationals indicted" headline feeds a narrative that the visa system is riddled with abuse — the same narrative invoked to justify the $100,000 H-1B fee and tighter scrutiny across the board. When USCIS deploys fraud-detection algorithms and ramps up denaturalization referrals, the dragnet does not stop at the guilty; it raises the burden of proof and the anxiety level for everyone.

There is also a sobering legal lesson buried in the Sharma denaturalization. Citizenship obtained while concealing a crime can be revoked years later. For a community that often treats naturalization as the final, irreversible milestone of the immigrant journey, the message from this enforcement wave is blunt: the finish line can be moved if the race was run dishonestly. The vast majority have nothing to fear — but the cases are a reminder that the system's tolerance for shortcuts has collapsed."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "EB-2 India Is Already Frozen. The July Visa Bulletin Will Decide Which Category Goes Dark Next",
        "subheadline": "With EB-2 India unavailable through September 30, immigration lawyers say EB-1 India and EB-5 Unreserved India are the State Department's next targets.",
        "slug": make_slug("july-2026-visa-bulletin-eb1-eb5-india-retrogression-forecast"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "No group is more exposed to the employment-based green-card backlog than Indians, and the July bulletin's forecast freezes threaten the EB-1 and EB-5 routes that Indian professionals and investors were counting on as alternatives to the now-shut EB-2 queue.",
        "tags": ["visa-bulletin", "green-card", "eb2-india", "eb1", "eb5", "uscis", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "VisaVerge — July 2026 Visa Bulletin: Complete Analysis & Forecast", "url": "https://www.visaverge.com/visa-bulletin/july-2026-visa-bulletin-complete-analysis-and-forecast/"},
            {"name": "U.S. Department of State — Visa Bulletin For June 2026", "url": "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"},
            {"name": "WR Immigration — June 2026 Visa Bulletin Analysis", "url": "https://wolfsdorf.com/june-2026-visa-bulletin/"},
            {"name": "AInvest — US EB-5 Visa Cap Reached for Indian Applicants", "url": "https://www.ainvest.com/news/us-eb-5-visa-cap-reached-indian-applicants-new-issuances-paused-october/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8441786/pexels-photo-8441786.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "An applicant fills out a U.S. immigration form, the paperwork at the heart of the employment-based green-card queue.",
        "image_attribution": "Pexels",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Ten Indian Nationals Staged Armed Robberies to Fake Their Way to Visas, Boston Grand Jury Says",
        "subheadline": "The alleged U-visa scheme lands amid a sharp federal escalation against immigration fraud by Indian nationals, from staged crimes to denaturalization.",
        "slug": make_slug("staged-robbery-u-visa-fraud-ring-ten-indian-nationals-boston-indictment"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Fraud rings like this hand ammunition to critics of legal immigration and raise scrutiny on the millions of Indian Americans who came through legitimate channels, even as USCIS ramps up fraud-detection algorithms and denaturalization referrals.",
        "tags": ["visa-fraud", "u-visa", "uscis", "denaturalization", "immigration", "doj"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "U.S. Department of Justice — Ten Indian Nationals Indicted for Visa Fraud Conspiracy", "url": "https://www.justice.gov/usao-ma/pr/ten-indian-nationals-indicted-visa-fraud-conspiracy"},
            {"name": "USCIS — Ten Indian Nationals Indicted for Visa Fraud Conspiracy", "url": "https://www.uscis.gov/newsroom/news-releases"},
            {"name": "USCIS — Indian National Sentenced for Visa Fraud Conspiracy (Aug 2025)", "url": "https://www.uscis.gov/newsroom/news-releases"},
            {"name": "Washington Examiner — DOJ denaturalization surge", "url": "https://www.washingtonexaminer.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6077326/pexels-photo-6077326.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A judge's gavel in a courtroom, where the Boston visa-fraud indictment now heads toward trial.",
        "image_attribution": "Pexels",
        "body": body2
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   words={wc} | {art['slug']}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
