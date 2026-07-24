#!/usr/bin/env python3
"""Immigration writer — July 9, 2026 evening run."""

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

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 1: Cognizant Named by Whistleblowers in H-1B Fraud Probe
# ─────────────────────────────────────────────────────────────────────

art1_body = """The Labor Department's Inspector General has, for the first time, publicly named an Indian-origin IT company in connection with the Trump administration's sweeping H-1B fraud investigation. During a Fox Business interview on Wednesday, Inspector General Anthony D'Esposito said his office had received whistleblower reports mentioning Cognizant Technology Solutions, one of the largest IT services firms in the world.

"We have whistleblowers talking about some of the biggest companies, like Cognizant," D'Esposito told the network, "and we are going to work side by side with the president and vice president's fraud task force to exhaust every lead."

He stressed that naming the company did not amount to an allegation of wrongdoing. No formal charges have been filed, and the investigation remains in its early stages. But the mention alone sent a signal that the federal probe — announced hours later by Vice President JD Vance at a fraud-initiative event in Milwaukee — is willing to follow leads into the heart of America's IT workforce pipeline.

## What the Probe Covers

Federal investigators have already served dozens of subpoenas examining alleged abuse of both the H-1B programme and the PERM labour certification process, the gateway to employer-sponsored green cards. D'Esposito said the inquiry will determine whether these programmes have been misused through fraudulent applications, false documentation, or other violations of immigration and labour laws.

According to Department of Homeland Security assessments cited during the announcement, as many as 21 per cent of H-1B petitions may be fraudulent — a figure that, if accurate, would implicate tens of thousands of filings each year.

The Inspector General drew a direct line between visa fraud and organised crime. "This is another example where fraud is fuelling violent crime," he said, claiming that some forms of foreign labour exploitation are "tied to cartels" and "transnational gangs." Whether that characterisation applies to the IT sector's use of H-1B visas is a separate question, but the rhetoric signals the administration's intent to frame enforcement in national-security terms.

## Why Cognizant Matters

Cognizant was founded in 1994 as a technology arm of Dun & Bradstreet's India operations and is now headquartered in Teaneck, New Jersey. It employs roughly 350,000 people worldwide, a large share of them in India, and is among the top users of the H-1B programme. The company earned $19.4 billion in revenue last year.

For years, Indian IT outsourcing firms have faced scrutiny over their heavy reliance on H-1B visas to staff American client projects. Critics argue that the model depresses wages for domestic workers and places foreign employees in precarious positions where their immigration status is tied to a single employer. Defenders counter that these firms fill genuine skill gaps and that their workers earn competitive salaries under prevailing-wage rules.

Cognizant itself was found liable in a jury trial in 2023 for discriminating against non-Indian employees, a verdict the company has contested. The fraud probe opens a separate front, one focused not on who gets hired but on whether the paperwork used to hire them is legitimate.

## What This Means for Indian Workers

For the roughly 400,000 Indians holding H-1B status in the United States, the investigation creates a new layer of anxiety. Indian nationals account for approximately 71 per cent of all H-1B beneficiaries, and Indian IT firms — Infosys, TCS, Wipro, HCL, and Cognizant among them — have historically been the programme's largest corporate users.

The probe does not target individual workers. But its existence raises the stakes for anyone whose employer might face enhanced scrutiny. Workers at H-1B-dependent firms could see delays in petition processing, increased requests for evidence, or — in a worst case — disruptions to their status if an employer is found to have filed fraudulent petitions on their behalf.

The White House has confirmed the investigation is part of a broader anti-fraud campaign. For the Indian diaspora, the uncomfortable question is whether a legitimate crackdown on bad actors will end up tightening the screws on everyone else."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Cognizant Is the First Indian IT Giant Named in the Federal H-1B Fraud Probe. It Won't Be the Last.",
    "subheadline": "The Labor Department's Inspector General cited whistleblower reports mentioning the company. No charges have been filed, but the signal is unmistakable.",
    "slug": make_slug("cognizant-whistleblower-h1b-fraud-probe-dol-ig-indian-it"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian IT firms employ hundreds of thousands of H-1B workers; a federal probe into one of the largest raises the stakes for every Indian professional whose status depends on employer-sponsored petitions.",
    "tags": ["h1b", "cognizant", "fraud", "uscis", "indian-it", "dol"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Bhaskar English", "url": "https://www.bhaskarenglish.in/international/news/us-indian-it-cognizant-h1b-visa-fraud-investigation-138397033.html"},
        {"name": "Fox News", "url": "https://www.foxnews.com/politics/fury-erupts-us-brand-fires-employees-after-securing-thousands-foreign-worker-visas"},
        {"name": "New York Post", "url": "https://nypost.com/2026/07/09/us-news/vance-labor-watchdog-launch-immigration-fraud-probe-to-protect-american-jobs/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Cognizant_Chennai_11_09.JPG/1280px-Cognizant_Chennai_11_09.JPG",
    "image_caption": "Cognizant Technology Solutions campus in Chennai, India",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: DHS Expanding $4,000 H-1B Extension Fee
# ─────────────────────────────────────────────────────────────────────

art2_body = """A rule change expected to take effect this month will force the largest users of the H-1B programme to pay a $4,000 surcharge on every visa extension — a fee that currently applies only to initial petitions and employer transfers. For Indian IT outsourcing firms, the timing could not be worse.

The surcharge, formally known as the Public Law 114-113 fee or the 9/11 Response fee, applies to a specific category of employer: those with more than 50 employees in the United States where more than half the workforce holds H-1B or L-1 status. In practice, that description fits a small number of companies, nearly all of them Indian IT services firms. Infosys, TCS, Wipro, HCL Technologies, and Cognizant have each appeared on the list in recent years.

Until now, the $4,000 fee (and a parallel $4,500 charge for L-1 extensions) was triggered only when the separate $500 Fraud Prevention and Detection fee also applied — meaning initial grants of status and changes of employer. Extensions with the same employer were exempt. The new rule, proposed by Customs and Border Protection under a reinterpretation of ambiguous statutory language, extends the surcharge to all H-1B and L-1 extension petitions filed by covered employers.

## The Maths for Indian IT

Consider a mid-sized Indian IT firm with 3,000 H-1B workers in the United States, each typically extending their visa every three years. Under the old rule, the firm paid the $4,000 surcharge only when it first brought a worker in or when a worker switched from another company. Under the new rule, every three-year renewal carries the charge too.

For a firm extending 1,000 workers in a given year, that is an additional $4 million in filing costs — on top of the base I-129 fee ($780 under the new fee schedule, up from $460), the ACWIA training fee ($1,500 for firms with more than 25 employees), the Asylum Program fee ($600), and whatever premium-processing charges the employer elects to pay. The total cost to extend a single H-1B worker at an H-1B-dependent firm now approaches $8,000.

For Infosys and TCS — each of which have been approved for more than 10,000 H-1B positions in recent fiscal years — the aggregate annual cost increase runs into the tens of millions.

## The Bigger Regulatory Picture

The fee expansion does not arrive in isolation. According to regulatory agendas published by the Departments of Homeland Security, Labor, and State, several other changes are in the pipeline:

An August 2026 proposed rule will tighten requirements for third-party client placements, the staffing model that Indian IT companies rely on most heavily. Employers will need to demonstrate a genuine employer-employee relationship and verify specialty-occupation duties at every client worksite. Companies with past compliance violations will face heightened scrutiny.

The Department of Labor is separately drafting a proposal to raise prevailing-wage floors for H-1B and employment-based green card petitions, which would increase the minimum salary at which an Indian IT firm can place a Level 1 (entry-level) worker.

And the PERM labour certification process — the first step in the employer-sponsored green card pipeline — is also slated for revision, with tighter recruitment standards and new restrictions on layoffs during the certification period.

## Why This Matters to Indian Professionals

The fee increase does not come out of workers' pockets directly. Federal law requires employers to pay H-1B filing costs. But the indirect effects are real. Higher costs give employers one more reason to shift work offshore rather than extend an American-based worker's visa. For Indian professionals on their second or third H-1B term, often deep into a green-card backlog that stretches decades, the risk is that their employer decides the maths no longer work.

The firms most affected by the surcharge are also the firms most likely to employ Indians in their first American job. If those companies pull back, the pipeline narrows — not just for new arrivals, but for the ecosystem of transfers, extensions, and eventual sponsorships that keeps hundreds of thousands of Indian professionals in the country.

The rule is expected to be published as a final regulation this month. Public comments on the proposed version closed earlier this year. No legal challenges have been announced, though the statutory basis for extending the fee to extensions — CBP's reading of an ambiguous provision in Public Law 114-113 — may invite the same separation-of-powers arguments that recently killed the $100,000 H-1B fee in federal court."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Every H-1B Extension Will Now Cost Indian IT Firms an Extra $4,000. The Rule Takes Effect This Month.",
    "subheadline": "The 9/11 Response surcharge, once limited to new hires, is being expanded to cover renewals. For H-1B-dependent employers, the annual bill could rise by tens of millions.",
    "slug": make_slug("h1b-dependent-employer-extension-fee-4000-indian-it"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian IT firms employ a disproportionate share of H-1B workers in the US; the fee expansion could accelerate offshoring and narrow the pipeline for new Indian arrivals and those stuck in the green-card backlog.",
    "tags": ["h1b", "uscis", "fees", "indian-it", "infosys", "tcs", "outsourcing"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/why-1-lakh-indian-h-4-visa-holders-could-face-job-disruptions-in-the-us"},
        {"name": "Fragomen", "url": "https://www.fragomen.com/insights/united-states-dhs-proposes-expansion-of-9-11-response-fee.html"},
        {"name": "DavidsonMorris", "url": "https://www.davidsonmorris.com/h-1b-visa-costs/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/USCIS_HQ_Groundbreaking_Ceremony_%2838096356021%29.jpg/1280px-USCIS_HQ_Groundbreaking_Ceremony_%2838096356021%29.jpg",
    "image_caption": "Officials at the USCIS headquarters groundbreaking ceremony in Camp Springs, Maryland",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 3: USCIS Ombudsman — H-1B Extension Delays
# ─────────────────────────────────────────────────────────────────────

art3_body = """The USCIS Ombudsman has told immigration stakeholders what most Indian H-1B workers already know: the agency's processing times for visa extensions have become, in the Ombudsman's own words, one of its "most significant problems."

In a recent teleconference, the Ombudsman confirmed that H-1B extension petitions are routinely taking eight to ten months to adjudicate at the Vermont and California service centres. The agency's annual report to Congress, released in June, documented the same delays for Employment Authorization Documents. Together, the two backlogs are creating a quiet crisis for hundreds of thousands of foreign workers and their employers — one that is measured not in policy debates but in missed paycheques and expired driver's licences.

## The 240-Day Cliff

Federal law offers H-1B workers a safety net: if an employer files a timely extension petition, the worker receives an automatic 240-day extension of status and work authorisation while USCIS processes the case. The provision was designed for a world in which most extensions were decided within months.

That world no longer exists. With processing times now stretching to eight, nine, and in some cases more than ten months, workers are regularly hitting day 241 with no decision on their petition. At that point, the automatic extension expires. The employer must remove the worker from payroll. Benefits end. The worker cannot legally work, even though they filed everything correctly and on time.

The consequences cascade. Without active work authorisation, many states will not renew a driver's licence, regardless of whether a timely extension is pending. Health insurance tied to employment lapses. And the worker, still lawfully present in the United States, is forced into a limbo that can last weeks or months — unable to earn, unable to drive, unable to do much of anything except wait.

## Who Gets Hurt

The delays fall hardest on Indian nationals, who account for roughly 73 per cent of all H-1B workers. Many are in their second or third extension cycle, deep into an employment-based green-card backlog that — for Indians in the EB-2 category — currently stretches back to July 2014, more than twelve years. These are not newcomers. They are mid-career professionals who have lived and worked in the United States for a decade or longer, paid taxes, bought homes, and enrolled children in school.

For their employers, the delays create operational headaches that premium processing — available for an additional $1,225 — only partially solves. Even premium cases can be delayed by requests for evidence, and not every employer is willing to pay the surcharge for every extension. Small and mid-sized firms, which lack the in-house immigration teams of the Fortune 500, are especially vulnerable.

USCIS has acknowledged the problem and transferred some extension workload from the overburdened Vermont centre to the Nebraska Service Center. It is too early to tell whether that shift will meaningfully reduce wait times.

## The Systemic Roots

The delays are not solely a staffing problem. They reflect a system under pressure from multiple directions. Enhanced vetting requirements — including the expanded social-media review that took effect for H-1B applicants in December 2025 — have added adjudication time at both USCIS and consular posts. The agency is simultaneously processing a record number of "continuing employment" petitions: 273,026 approved in the first nine months of fiscal year 2026, on pace to surpass 291,000 for the full year.

Meanwhile, the political environment has made USCIS adjudicators more cautious. Requests for evidence have increased. Denials have ticked up. Each additional step adds days or weeks to a case that, under the old regime, might have been approved in three months.

## What Workers and Employers Can Do

The Ombudsman's advice is unsurprising but worth repeating: file early. H-1B extensions can be submitted up to six months before the current period expires. For workers whose employers typically wait until the last quarter, that gap can be the difference between a smooth renewal and a payroll interruption.

Beyond that, the options are limited. Premium processing buys speed but not certainty. Mandamus lawsuits — in which workers sue USCIS in federal court to force a decision — have increased, but they are expensive and slow, often taking longer than simply waiting for the adjudication.

For the Indian diaspora, the Ombudsman's candid assessment is at least an acknowledgement that the system is failing. Whether it leads to systemic reform or merely a reshuffling of caseloads between service centres remains an open question — one that tens of thousands of Indian families will be watching from day 241."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The USCIS Ombudsman Just Called H-1B Extension Delays the Agency's Biggest Problem. Workers Are Losing Jobs at Day 241.",
    "subheadline": "Processing times at some service centres now exceed eight months, pushing past the 240-day grace period and forcing employers to pull workers off payroll.",
    "slug": make_slug("uscis-ombudsman-h1b-extension-delays-240-day-cliff"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian nationals make up 73% of H-1B workers; those in the decade-long EB-2 green-card backlog are most exposed to extension delays that can cost them their jobs, insurance, and ability to drive.",
    "tags": ["h1b", "uscis", "processing-delays", "ombudsman", "extension", "240-day"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Fragomen", "url": "https://www.fragomen.com/insights/uscis-ombudsman-highlights-h-1b-processing-delays.html"},
        {"name": "Outlook Money", "url": "https://www.outlookmoney.com/personal-finance/news/h-1b-visa-renewals-reach-record-high-despite-stricter-us-policies"},
        {"name": "ImmIVA", "url": "https://www.immiva.com/h4-ead-processing-time/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/USCIS_HQ_Groundbreaking_Ceremony_%2838096348641%29.jpg/1280px-USCIS_HQ_Groundbreaking_Ceremony_%2838096348641%29.jpg",
    "image_caption": "USCIS headquarters groundbreaking ceremony in Camp Springs, Maryland",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}

# ─────────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
