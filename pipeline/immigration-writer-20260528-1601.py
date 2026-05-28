#!/usr/bin/env python3
"""Immigration writer — 2026-05-28 run. Two articles."""
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
    {
        "id": str(uuid.uuid4()),
        "headline": "29% Fewer Student Visas, 627,000 Indians in Limbo — Brookings Just Scored the Damage",
        "subheadline": "A comprehensive Brookings Institution report puts hard numbers on the collapse of America's high-skill immigration pipeline, and the Indian diaspora is absorbing the worst of it.",
        "slug": make_slug("brookings-talent-pipeline-collapse-indian-diaspora"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians comprise 627,000 of the 1.2 million people stuck in green card backlogs — more than half the total. The pipeline that brought most Indian tech workers to America (F-1 → OPT → H-1B → EB green card) is being squeezed at every stage simultaneously.",
        "tags": ["immigration", "brookings", "f1-visa", "h1b", "green-card-backlog", "indian-diaspora", "opt"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"},
            {"name": "NAFSA", "url": "https://www.nafsa.org/policy-and-advocacy/policy-resources/nafsa-international-student-economic-value-tool-v2"},
            {"name": "Shusterman Law / Visa Bulletin Data", "url": "https://www.shusterman.com/visa-bulletin-predictions/"},
            {"name": "FWD.US", "url": "https://www.fwd.us/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20417783/pexels-photo-20417783.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "The US Capitol, where the legislative framework governing immigration caps has remained largely unchanged since 1990.",
        "body": """Brookings doesn't do alarmism. When the think tank's Center for Economic Security and Opportunity publishes a 28-minute read titled "How the Trump Administration Is Eroding the Immigrant Talent Pipeline," and the data inside reads like an autopsy report, it's worth paying attention.

Published on May 21, the paper — authored by Tara Watson, Matthew Wich, and Johnny Willing — is the most comprehensive accounting yet of what's happening to America's high-skill immigration system under the current administration. The short version: every stage of the pipeline that brings skilled foreign workers to America is now under simultaneous pressure, and India is taking the biggest hit.

## The Numbers That Matter

Start with students. Brookings projects a **29% decline in new F-1 visa issuances** in 2025, based on State Department data through the first eight months of the calendar year. A separate IIE survey of 828 universities found 17% fewer international students began studies in fall 2025 compared to the prior year. NAFSA estimates the economic fallout: $1.1 billion in lost revenue and nearly 23,000 American jobs eliminated in the 2025-2026 academic year. California and New York — the two states hosting the most international students — face projected losses of $161.9 million and $152.5 million respectively.

Then there's the green card backlog. Brookings estimates **approximately 1.2 million immigrants and their families are stuck waiting for employment-based green cards**. Of those, roughly 627,000 were born in India. That's not a rounding error. That is more than half the entire backlog concentrated in one country, a consequence of the 7% per-country cap on EB visas that has remained unchanged since 1990, even as Indian-origin applicants came to dominate the STEM workforce.

The H-1B system is being reshaped from the inside. A $100,000 fee imposed on new H-1B petitions last September — ostensibly to prevent wage suppression — has been paid by only about 85 companies so far, according to news reports cited in the Brookings paper. The fee is being challenged in court by, among others, the U.S. Chamber of Commerce. Meanwhile, a new wage-weighted lottery system replaced the random selection process in late December, taking effect for the FY2027 cycle that opened March 4, 2026. The cap was reached in just 25 days.

## Where India Fits

For Indian professionals, these aren't abstract data points. They describe the actual architecture of a career in America.

The typical path runs like this: arrive on an F-1 student visa, work for 12 months (or three years, with a STEM extension) under OPT after graduation, get sponsored for an H-1B, then wait — in some cases, more than a decade — for an employment-based green card. Brookings notes that about 40% of initial H-1B approvals go to former F-1 holders. Roughly three-quarters of new EB green cards are issued through "adjustments of status" to people already in the country on temporary visas.

Squeeze any one stage and the downstream effect compounds. Squeeze all of them at once, and you get what the paper describes: a systemic erosion of the pathway that brought hundreds of thousands of Indian engineers, researchers, and entrepreneurs to the United States.

The report documents the specific pressure points: a January 2026 travel ban blocking new visas for 38 countries (affecting 5% of F-1 issuances), a proposed rule to cap F-1 stays at four years (problematic for doctoral students), the revocation of 8,000 student visas since January 2025, a social media vetting requirement for visa applicants, and the USCIS director's stated intention to curtail or end the OPT program entirely.

## The Competition Is Watching

Perhaps the most strategically important section of the Brookings paper covers what other countries are doing while America tightens. China launched its K-visa — a direct analog to the H-1B — in late 2025. Canada and Germany have expanded skilled immigration pathways. Research cited in the paper suggests that increased American restrictions on H-1B holders may lead to greater offshoring from multinational corporations, "particularly to China, India, and Canada."

For the Indian professional weighing a career in America versus Bangalore, Toronto, or Berlin, the calculation has shifted. The Brookings data doesn't say the American dream is dead for skilled Indians. It says the pipeline that delivered it is being dismantled, one regulation at a time, and nobody in Washington appears to have a plan for what comes after.

## What This Means for NRIs

If you're an Indian professional on an H-1B tracking your EB-2 priority date, or a parent whose child is considering an American university, the Brookings report is the closest thing to a comprehensive risk assessment available. The 627,000 Indians in the green card backlog aren't going anywhere fast — the June 2026 visa bulletin just retrogressed EB-2 India by more than ten months. The 29% F-1 decline means the next generation of the Indian-American professional class is already shrinking before it arrives.

The $42.9 billion that international students contributed to the American economy last year, the 350,000 jobs they supported, the 36% of total U.S. innovation attributed to immigrants since 1990 — these are not figures that survive a policy environment where every rung of the ladder is being sawed through simultaneously. Brookings has done the math. The question is whether anyone in a position to act is reading it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "290,000 Students, One Confirmation Hearing, and the Quiet Death of OPT",
        "subheadline": "The USCIS director told Congress he wants to end Optional Practical Training. DHS is 'reevaluating' it. A bill to kill it is in play. For Indian graduates, the clock is ticking.",
        "slug": make_slug("opt-end-uscis-edlow-indian-students-work-rights"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian students are the second-largest group on OPT (behind China) and the most likely to use it as a bridge to H-1B sponsorship. Ending OPT would eliminate the primary mechanism by which Indian STEM graduates transition from student to worker in the American economy.",
        "tags": ["immigration", "opt", "stem-opt", "f1-visa", "indian-students", "uscis", "work-authorization"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"},
            {"name": "AILA (American Immigration Lawyers Association)", "url": "https://www.aila.org/"},
            {"name": "Institute of International Education (IIE)", "url": "https://www.iie.org/"},
            {"name": "Sen. Schmitt (R-MO) / DHS correspondence", "url": "https://www.schmitt.senate.gov/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7972710/pexels-photo-7972710.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Graduates celebrating — but for international students, the post-graduation work pipeline is under existential threat.",
        "body": """Joseph Edlow didn't mumble. During his confirmation hearing to lead U.S. Citizenship and Immigration Services, the man now running America's immigration bureaucracy told Congress plainly that he would seek to "effectively end" the Optional Practical Training program. That was before he took office. Now he's in the chair, and the machinery is moving.

DHS has since sent a letter to Senator Eric Schmitt confirming that the department "is reevaluating whether the current regulatory framework — including the scope and duration of practical training — appropriately serves U.S. labor market, tax, and national security interests and remains aligned with congressional intent." In Congress, a separate bill to abolish the OPT program has entered the legislative pipeline. None of this is hypothetical. The only open question is timing.

## What OPT Actually Does

Optional Practical Training allows F-1 student visa holders to work in the United States for 12 months after graduating. STEM degree holders can extend that by an additional 24 months, for a total of three years of post-graduation employment. The program is popular: according to Brookings, 72% of international graduates participate in OPT after completing their degrees. In the 2024-2025 academic year, more than 290,000 students were on OPT — a record.

The numbers matter because OPT is not a standalone program. It is the connective tissue between studying in America and working in America. About 40% of initial H-1B visa approvals go to people who were previously on F-1 or F-2 visas. OPT is how most of them stay employed during the gap between graduation and H-1B sponsorship. Remove it, and the path from Indian student to Indian-American engineer doesn't just get harder. For many, it disappears entirely.

## The Indian Stakes

Indian and Chinese students together account for about 43% of all F-1 visas issued. Of the 1.18 million international students in the U.S. in the 2024-2025 academic year, 488,000 — the largest share, at 41% — were pursuing graduate degrees. Indian graduate students, concentrated in STEM and business programs at American universities, are among the heaviest users of OPT and its STEM extension.

The value proposition for these students has always been straightforward: pay full tuition (82% of international undergrads and 59% of international graduate students fund their education through personal and family sources), graduate, work on OPT, find an employer willing to sponsor an H-1B, and eventually join the green card queue. The total investment — measured in tuition dollars, years away from home, and career risk — typically runs well into six figures before the first paycheck arrives.

Ending OPT doesn't just remove one step from this sequence. It breaks the economic logic that made the sequence worth starting. An employer that can't evaluate a candidate for 12 months on OPT before committing to an H-1B sponsorship has far less incentive to recruit from international graduate programs. A student who can't work in America after graduation has far less reason to choose an American university over one in Canada, Australia, or the UK — all of which offer clearer post-study work pathways.

## The Ripple Effects

The Brookings paper released last week quantified what happens when you erode the talent pipeline: a projected 29% decline in new F-1 visa issuances in 2025, $1.1 billion in lost economic contribution, and nearly 23,000 American jobs eliminated. And that's with OPT still intact.

If OPT is curtailed or ended, those numbers get significantly worse. International students contributed $42.9 billion to the U.S. economy in the most recent academic year, according to NAFSA. A meaningful share of that contribution depends on the expectation of post-graduation employment. Strip the expectation, and you strip the enrollment. Strip the enrollment, and you strip the revenue — from universities, from local economies, from the tax base that helps fund Social Security and Medicare. A 2025 Cato Institute report estimated that college-educated immigrants paid $8.8 trillion more in taxes than they received in benefits between 1994 and 2023.

## What to Watch

The regulatory timeline is the critical variable. DHS said it would "provide more clarity in the coming months" about its OPT reevaluation. That language is consistent with a proposed rule appearing in the Federal Register before the end of 2026, followed by a notice-and-comment period. Any final rule would face immediate legal challenges — the Supreme Court recently declined to review a lawsuit challenging OPT's legal authority, affirming DHS's power to grant such work authorization. But a regulatory rollback by the agency itself is a different legal animal.

For Indian students currently on OPT or planning to enter it, the practical advice is unchanged: move fast. File extensions early. Build employer relationships that lead to H-1B sponsorship before the regulatory window closes. For those still deciding whether to pursue an American degree, the calculus now includes a variable it never had before — the real possibility that by the time you graduate, the right to work afterward may no longer exist.

Edlow was clear about his intentions. DHS is reevaluating. Congress has a bill. The only institution that hasn't weighed in is time, and for 290,000 students, it's running out."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
