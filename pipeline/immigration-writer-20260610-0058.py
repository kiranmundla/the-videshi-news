#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-06-10 00:58 PDT run."""

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

articles = [
    # ── Article 1: Modi-Trump G7 bilateral ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Modi Will Raise H-1B Visas With Trump at the G7 — Here's What That Means for 730,000 Indian Workers",
        "subheadline": "India's prime minister is expected to press the visa issue alongside trade and energy talks when the two leaders meet on the sidelines of the G7 summit in France next week.",
        "slug": make_slug("modi-trump-g7-h1b-visa-bilateral-france"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For the estimated 730,000 Indian nationals currently on H-1B visas in the United States, the Modi-Trump G7 sidebar could shape the next phase of work visa policy — from the contested $100,000 fee (just struck down in one court, upheld in another) to the Chip Roy bill proposing a two-year visa cap. New Delhi raising the issue at the highest diplomatic level signals that India views the visa crackdown as a bilateral irritant, not a domestic American matter.",
        "tags": ["modi", "trump", "g7", "h1b", "bilateral", "trade", "india-us"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/americas/indias-modi-trump-likely-meet-g7-discuss-trade-visas-source-says-2026-06-10/"},
            {"name": "Fox News", "url": "https://www.foxnews.com/politics/federal-judge-strikes-down-trumps-100k-h-1b-visa-fee-ruling-unconstitutional-tax"},
            {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/09/trump-h1b-visa-fee-struck-down/84173405007/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/1b/Trump-Modi_Bilateral_Meeting.jpg",
        "image_caption": "Prime Minister Narendra Modi and President Donald Trump during a bilateral meeting",
        "image_attribution": "Wikimedia Commons",
        "body": """When Narendra Modi lands in France for the G7 summit on June 13, the expected bilateral with Donald Trump will not be limited to tariffs and energy. According to an Indian government source with direct knowledge of the agenda, H-1B visas are on the table.

That single line in the briefing note carries weight disproportionate to its brevity. India's decision to put immigration policy into a head-of-state conversation — rather than leaving it to bureaucratic channels — reflects a calculation in New Delhi that the cumulative pressure on Indian workers in America has crossed from inconvenience into strategic concern.

## The backdrop is unusually chaotic

In the past month alone, the American immigration landscape has produced a set of contradictions that would confuse a constitutional lawyer, let alone the average H-1B holder tracking policy from a cubicle in Sunnyvale.

A federal judge in Boston struck down Trump's $100,000 fee on new H-1B petitions, calling it an unconstitutional tax imposed without congressional authorisation. A federal judge in Washington had already upheld the same fee. The circuit split virtually guarantees the issue will land at the Supreme Court — but not before confusion reigns for at least another year.

Meanwhile, Congressman Chip Roy introduced the American White-Collar Worker Jobs Act of 2026, a bill that would shrink H-1B visas from six years to two, kill dual intent (the provision that lets H-1B holders pursue green cards), eliminate OPT for international graduates, and impose a seven-per-cent country cap on the H-1B programme itself. If enacted, that last provision alone would slash Indian allocations by roughly 90 per cent.

## What Modi can realistically achieve

Diplomatic conversations about immigration rarely produce immediate policy changes, and nobody in New Delhi expects Trump to reverse course over a handshake in Evian-les-Bains. But the meeting serves several purposes.

First, it elevates the issue. When a prime minister personally raises H-1B policy, it becomes harder for Washington to treat subsequent enforcement actions as purely domestic. Second, the conversation comes at a moment when both sides have leverage: India and the United States are moving toward the first tranche of a bilateral trade deal, expected by mid-July. Trade Minister Piyush Goyal said last week that talks are progressing. Washington's proposed 12.5 per cent additional tariff on Indian goods — based on forced-labour allegations India flatly rejects — gives New Delhi something to negotiate against.

Third, the timing follows Marco Rubio's visit to India last month, which covered visas alongside maritime security and energy. The G7 sidebar would continue that thread at a higher level.

## Why this matters for Indian Americans

For the diaspora, the significance is partly practical and partly symbolic. Practically, the $100,000 fee — even with its legal status in limbo — has already suppressed new H-1B petitions. USCIS reported just 85 payments as of February, a fraction of the tens of thousands of annual filings. Employers are pulling back, and Indian IT services firms face a potential $2.25 billion annual exposure if the fee survives appeal.

Symbolically, India treating H-1B policy as a bilateral issue validates what every Indian worker in America already knows: these are not abstract policy debates. They are decisions about whether families stay together, whether careers continue, and whether the promise that brought hundreds of thousands of skilled workers to America still holds.

The G7 sidebar will not resolve any of this. But it will make it harder to ignore."""
    },
    # ── Article 2: 21 Indian students deported ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Twenty-One Indian Students Turned Away at Three US Airports in a Single Day",
        "subheadline": "Students from Andhra Pradesh and Telangana were detained, questioned, and sent home from Atlanta, Chicago, and San Francisco — now facing a five-year re-entry ban.",
        "slug": make_slug("21-indian-students-deported-airports-andhra-telangana"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For Indian families who have invested lakhs in American university admissions, this incident is a gut punch. The students believed they had completed all visa requirements and were ready to enrol at universities in Missouri and South Dakota. The five-year ban for those deemed inadmissible transforms a single bad day at immigration into half a decade of lost opportunity — and there is no appeals process at the port of entry.",
        "tags": ["f1-visa", "students", "deportation", "airports", "telangana", "andhra-pradesh"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/for-21-indian-students-in-us-a-single-day-matters-deported-back/"},
            {"name": "College Chalo", "url": "https://www.collegechalo.com/news/trump-visa-crackdown-international-student-visas"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37847918/pexels-photo-37847918.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Travelers undergoing screening at a US airport terminal",
        "image_attribution": "Pexels",
        "body": """They had their I-20 forms. They had their visa stamps. They had acceptance letters from universities in Missouri and South Dakota. What twenty-one students from Andhra Pradesh and Telangana did not have, apparently, was whatever a Customs and Border Protection officer at the gate decided they needed.

In a single day, all twenty-one were denied entry at three separate airports — Atlanta, Chicago, and San Francisco — after what reports describe as brief document inspections by US Immigration and Customs Enforcement. The students were held in cramped quarters and, according to accounts relayed to Indian media, told they would face jail if they objected.

They are now back in India, their American university plans in ruins. Worse, they face a five-year ban on re-entry — the standard consequence for anyone found inadmissible at a US port of entry.

## What went wrong

The precise documentation deficiency has not been publicly detailed, which is itself part of the problem. At a port of entry, CBP officers have broad discretion to deny admission if they determine a traveller's documents are insufficient, their stated purpose seems inconsistent, or their financial support appears inadequate. There is no judge, no hearing, and no appeal. The officer's decision is final.

Reports indicate the primary reason cited was "lack of proper documentation," a catch-all that could mean anything from a missing financial affidavit to a discrepancy between the university programme dates and the visa validity. For students who believed they had followed every step correctly, the ambiguity is maddening.

## The five-year shadow

Being turned away at a US airport is not the same as an overstay or a visa violation. It is, in immigration terms, a finding of inadmissibility — and it carries a five-year bar on future US entry. For a twenty-year-old student, that means no re-applying until age twenty-five. The window for a US degree, the OPT work experience that follows, and the career trajectory that depends on both — all of it shifts by half a decade, if it survives at all.

The ban also complicates applications to other countries. Canada, the UK, and Australia all ask whether an applicant has ever been refused entry to another country. A US inadmissibility finding becomes a flag on every future immigration form.

## A pattern, not an anomaly

This is not an isolated incident. The Trump administration has revoked more than 6,000 international student visas since the beginning of 2026, according to data tracked by education policy monitors. The grounds vary — social media posts deemed objectionable, participation in protests, or simply falling outside the narrowing window of acceptable student behaviour.

Graduate enrolments from India are already down 15 per cent year over year, according to Open Doors 2024/25 data. New enrolments have dropped 7 per cent. The numbers were sliding before these twenty-one students boarded their flights. They will slide further after.

## What Indian families should know

Immigration attorneys consistently advise students to carry far more documentation than they believe necessary: original financial statements, sponsor affidavits, university correspondence confirming enrolment, housing arrangements, and return-trip evidence. Having the visa stamp is necessary but not sufficient — the port of entry is a separate and sovereign checkpoint.

For the twenty-one students now back in Hyderabad and Vijayawada, that advice comes too late. For the roughly 200,000 Indian students currently in the US — and the next cohort preparing to leave — it is a warning written in someone else's misfortune."""
    },
    # ── Article 3: 10 Indian nationals indicted for visa fraud ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Ten Indian Nationals Indicted in Boston for Staging Armed Robberies to Game the US Visa System",
        "subheadline": "A federal grand jury says the defendants staged fake convenience-store holdups so clerks could file fraudulent crime-victim immigration applications.",
        "slug": make_slug("boston-10-indicted-staged-robberies-visa-fraud-patel"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For the vast majority of Indian immigrants navigating the legal system in good faith — waiting years for green cards, paying thousands in filing fees, following every rule — cases like this are corrosive. They hand ammunition to restrictionists who argue that the immigration system is riddled with fraud, and they taint an entire community's reputation for the actions of a few.",
        "tags": ["visa-fraud", "boston", "indictment", "u-visa", "crime"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/us-visa-fraud-conspiracy-10-indian-nationals-indicted/"},
            {"name": "US Attorney's Office, District of Massachusetts", "url": "https://www.justice.gov/usao-ma"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16151491/pexels-photo-16151491.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A federal government building in Washington, DC",
        "image_attribution": "Pexels",
        "body": """The scheme was audacious in its simplicity and depressing in its cynicism. Ten Indian nationals have been indicted by a federal grand jury in Boston for conspiring to stage armed robberies of convenience stores — not to steal anything, but to generate fake crime reports that store clerks could use on immigration applications.

The United States Attorney's Office for the District of Massachusetts laid out the conspiracy in an indictment that reads like a screenplay pitched by someone who has watched too many insurance-fraud documentaries. The defendants — nine of them surnamed Patel, ranging in age from 28 to 52 — allegedly organised fake holdups at convenience stores where fellow Indian nationals worked as clerks. The "victims" would then file police reports and use the documented crime as the basis for immigration petitions, likely under the U-visa programme, which grants temporary legal status to crime victims who cooperate with law enforcement.

## How the U-visa pipeline was exploited

The U-visa was created by Congress in 2000 to protect undocumented immigrants who are victims of serious crimes — domestic violence, trafficking, assault — and who assist police in investigating those crimes. It grants up to four years of legal status and a path to a green card. In a system where legal pathways can take decades, the U-visa's relative speed has made it a target.

The Boston defendants appear to have reverse-engineered the process: create the crime, file the report, claim victim status, and petition for legal residency. The scheme was organised by Rambhai Patel and aided by getaway driver Balwinder Singh, both of whom were charged in December 2023 and convicted in May 2025. The ten newly indicted defendants were previously charged by criminal complaint in March 2026 and released on conditions. Two — Rameshbhai Patel and Ronakkumar Patel — have since been taken into immigration custody.

Most of the accused were residing unlawfully in the United States. One had already been deported to India. All face deportation upon completion of any sentence.

## The collateral damage

The immediate legal consequences for the defendants are straightforward: federal conspiracy charges, potential prison time, and near-certain deportation. The broader consequences are more insidious.

Every high-profile fraud case involving Indian nationals gives political cover to those arguing for tighter restrictions on all Indian immigration. The U-visa programme itself is already under scrutiny — critics have long argued it is susceptible to fabricated claims, and cases like this validate their concerns. When Congress debates immigration reform, the Boston indictment will appear in someone's exhibit binder.

For the roughly 4.8 million Indian Americans in the United States, the vast majority of whom arrived and remain through entirely legal channels, this is a familiar frustration. The actions of ten people in a convenience-store staging scheme become a data point in a policy argument that affects millions.

## What the case reveals about desperation

The more uncomfortable question the indictment raises is about the system itself. The defendants were, by most accounts, people living in the shadows of American immigration law — undocumented, without a realistic path to legal status, and apparently willing to risk federal conspiracy charges for a shot at a U-visa.

That does not excuse the fraud. Staging fake armed robberies wastes police resources, undermines a programme designed to protect genuine crime victims, and — as the convictions of the scheme's organisers demonstrate — carries serious prison time. But it does illuminate the gap between immigration demand and legal supply that turns otherwise ordinary people into defendants in a federal courthouse.

The U-visa programme processes roughly 10,000 petitions per year against a cap that Congress has not raised since 2000. The EB-2 green card queue for Indian nationals stretches beyond a decade. The H-1B lottery rejects the majority of applicants. In a system defined by scarcity, fraud is not surprising. It is, regrettably, predictable."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
