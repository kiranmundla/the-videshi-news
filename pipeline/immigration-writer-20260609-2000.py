#!/usr/bin/env python3
"""Immigration writer — 2026-06-09 20:00 UTC run"""

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
        "headline": "Three Hundred and Thirty-Eight — That's How Many People Want Trump's Million-Dollar Gold Card",
        "subheadline": "Nine months after launch, the programme meant to replace EB-5 has attracted fewer applicants than a mid-tier Costco opening. India's wealthy are not impressed.",
        "slug": make_slug("trump-gold-card-338-applicants-india-wealthy-eb5"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "India has historically been among the top four sources of EB-5 investor visa applicants. The Gold Card, priced at five to twenty-five times the EB-5 minimum, is forcing wealthy Indians to recalculate: pay a million dollars for a card Commerce Secretary Lutnick admits has yielded exactly one approval, or stick with EB-5 before its September 2027 reauthorisation deadline and risk the programme being killed entirely.",
        "tags": ["gold-card", "eb-5", "immigration", "investor-visa", "trump"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wikipedia — Trump Gold Card", "url": "https://en.wikipedia.org/wiki/Trump_Gold_Card"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com"},
            {"name": "Manifest Law — Gold Card Guide", "url": "https://manifestlaw.com"},
            {"name": "DHS data via Wikipedia", "url": "https://en.wikipedia.org/wiki/Trump_Gold_Card"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg",
        "image_caption": "A US visa stamp on a passport document page",
        "image_attribution": "Pexels",
        "body": """When Donald Trump unveiled his Gold Card programme last September, he predicted it would "sell like crazy." He imagined a million buyers, $5 trillion flowing into the Treasury, and a gleaming replacement for the EB-5 investor visa that he and Commerce Secretary Howard Lutnick had dismissed as "poorly overseen, poorly executed."

Nine months later, the numbers are in — and they are brutal.

As of May 2026, exactly 338 individuals have applied for a Trump Gold Card. Of those, 165 have paid the non-refundable $15,000 processing fee. And the total number of people actually approved? One. That person is widely assumed to be rapper Nicki Minaj, who received her card free of charge as a presidential gift — making the programme's organic approval rate, for all practical purposes, zero.

## The price nobody wants to pay

The Gold Card's sticker price tells the story. Individual applicants must contribute $1 million to the Department of Commerce. Corporations sponsoring an employee pay $2 million. The top-tier "Platinum" option runs to $5 million. Even before making the contribution, every applicant hands over a $15,000 fee — non-refundable regardless of outcome. Family members cost an additional $1 million each, plus another $15,000 per person.

Compare that to the EB-5 programme it is meant to replace. A targeted employment area investment under EB-5 requires $800,000 — less than the Gold Card's base contribution — and comes with decades of case law, a network of regional centres, and a clear path to conditional and then permanent residency. The Gold Card offers expedited processing through the EB-1A and EB-2 National Interest Waiver categories, treating the financial contribution as proof of "extraordinary ability." Immigration lawyers have questioned whether that legal theory will survive its first serious court challenge.

## Why India's wealthy are steering clear

India has consistently ranked among the top four nationalities for EB-5 filings. Wealthy Indian families — software entrepreneurs in Bengaluru, real estate developers in Mumbai, pharmaceutical executives in Hyderabad — have been among the programme's most enthusiastic users, drawn by a green card path that does not depend on the H-1B lottery or the EB-2 India backlog that now stretches past a decade.

The Gold Card, at least in theory, should appeal to the same demographic. But immigration advisers working with Indian high-net-worth clients say the interest has been close to nil.

The maths simply does not work, according to several advisers. An Indian family of four would face a $4 million contribution plus $60,000 in processing fees — for a programme with no track record, one confirmed approval, and an uncertain legal foundation. The EB-5, by contrast, has been operating since 1990 and offers the investment back (at least in theory) once the job-creation requirement is met. The Gold Card contribution is a gift, not an investment. It does not come back.

There is also the question of alternatives. The UAE's Golden Visa requires an investment of roughly Rs 4 crore — a fraction of the Gold Card's cost — and offers proximity to India, no income tax, and a large existing Indian expatriate community. Portugal, Greece, and Spain have similar programmes at lower price points.

## The EB-5 deadline looms

What makes the situation urgent for Indian investors is the calendar. The EB-5 programme is authorised through September 30, 2027. Applications filed before September 30, 2026, are grandfathered under current rules, meaning investors who act now lock in today's requirements regardless of what Congress does next year.

Lutnick has repeatedly said the Gold Card is meant to replace EB-5 entirely. If that happens and the Gold Card remains the only game in town, Indian investors who waited will face a programme that costs five times more and has produced exactly one approval in nine months.

The smart money, for now, appears to be filing EB-5 petitions while the window is still open — and watching the Gold Card from a safe distance.

## What comes next

The administration has shown no sign of abandoning the programme. Trump continues to promote it as a revenue generator, and the official website at trumpcard.gov remains open for applications. But with 338 applicants against a presidential forecast of "maybe a million," the Gold Card's credibility problem is compounding with every quarter that passes.

For Indian professionals already navigating a system that charges $100,000 for an H-1B petition (a fee that a federal judge struck down just yesterday), demands 501-day PERM processing waits, and retrogresses EB-2 dates backward, the Gold Card looks less like a fast lane and more like a toll bridge to nowhere."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Harvard Can No Longer Enrol Foreign Students — and Every Indian F-1 Holder Should Be Watching",
        "subheadline": "The administration's revocation of Harvard's international student certification is the most aggressive federal move against a university's visa programme in modern history. The ripple effects reach far beyond Cambridge.",
        "slug": make_slug("harvard-sevp-revoked-indian-students-f1-visa-impact"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian students are the single largest international student cohort in the United States and among the most represented at elite institutions like Harvard. The SEVP revocation — combined with a 17% drop in new international enrolments and a 50% decline in Indian student visas — signals a federal willingness to use the student visa system as a pressure tool that could affect every Indian family with a child studying in America or planning to apply.",
        "tags": ["f1-visa", "harvard", "sevp", "indian-students", "international-students"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye / CNN", "url": "https://theindianeye.com"},
            {"name": "GoElite — 17% enrollment drop", "url": "https://goelite.com"},
            {"name": "Careers360 — Student visa numbers", "url": "https://studyabroad.careers360.com"},
            {"name": "IIE Fall 2025 Snapshot", "url": "https://goelite.com"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/92/Harvard_Science_Center_from_the_Yard.jpg",
        "image_caption": "Harvard Science Center viewed from Harvard Yard",
        "image_attribution": "Wikimedia Commons",
        "body": """The Department of Homeland Security did something last week that no administration has done to a major American university in living memory: it revoked Harvard's Student and Exchange Visitor Programme certification, the federal approval that allows a university to enrol international students.

The practical effect is immediate and severe. Harvard can no longer issue I-20 forms to incoming foreign students. Current international students — more than a quarter of Harvard's student body — must transfer to another institution or lose their legal immigration status.

"Harvard can no longer enroll foreign students and existing foreign students must transfer or lose their legal status," the DHS stated.

## The backstory

The revocation stems from a months-long standoff between Harvard's administration and the Trump White House. In April, DHS demanded that Harvard turn over conduct records of its foreign students. The university refused, citing privacy protections and academic freedom. Homeland Security Secretary Kristi Noem responded by directing her department to terminate Harvard's SEVP certification.

The White House framed the decision in stark terms. "Enrolling foreign students is a privilege, not a right," a spokesperson said, accusing Harvard's leadership of turning "their once-great institution into a hot-bed of anti-American, anti-Semitic, pro-terrorist agitators."

Harvard's professors have warned that a mass exodus of foreign students threatens to gut the institution's research capacity. International students are disproportionately represented in STEM doctoral programmes, where they often form the backbone of laboratory work funded by federal grants.

## The numbers behind the fear

The Harvard decision does not exist in isolation. It lands in the middle of the sharpest decline in international student enrolment the United States has seen in decades.

The Institute of International Education's Fall 2025 Snapshot, drawing on data from more than 825 colleges and universities, found a 17% drop in new international student enrolments. Among institutions that reported declines, 96% cited visa issues as the primary cause — not cost, not curriculum, not competing destinations.

The damage is concentrated among Indian students. Data from the International Trade Administration shows student visa arrivals hit a four-year low in August 2025, with Indian F-1 approvals dropping roughly 50% compared to the 2023 peak of over 100,000. The January-to-August 2025 window saw a 19% decline in total arrivals — the lowest August intake since the pandemic year of 2021.

F-1 visa approvals fell 12% between January and April 2025 and 22% in May alone. Modelling by NAFSA suggested June could see declines of 80-90% if the trends held, owing partly to a visa interview pause from late May to mid-June during peak issuance season.

## Why Indian families should pay attention

India sends more students to American universities than any other country. Those students — concentrated in computer science, engineering, data science, and business analytics — are not just pursuing degrees. They are building the first rung of an immigration ladder that typically runs F-1 to OPT to H-1B to green card. Every disruption to the student visa system shakes the entire structure.

The Harvard revocation is not about Harvard. It is about the precedent. If the federal government can strip SEVP certification from the most prestigious university in the country over a records dispute, it can do the same to any institution. University administrators across the country are watching and recalculating their own risk exposure.

For Indian families with children currently studying in America, the immediate question is whether their university could face similar pressure. For families planning to send children in the coming admission cycle, the question is whether the American higher education system can still be trusted as a stable destination.

## The social media screening factor

Adding to the unease, new visa rules now require enhanced screening of students' social media accounts. Processing delays have followed. Indian students — many of whom are active on Instagram, X, and LinkedIn — report receiving 221(g) administrative processing slips at higher rates than in previous years. The screening adds weeks or months to what was already a stressful visa timeline.

Several recent reports document cases of students receiving revocation notices or denials based on social media content that immigration officers deemed inconsistent with stated visa purposes. The vetting is opaque: students are rarely told which posts triggered the review.

## The bigger picture

The Harvard SEVP revocation, the 17% enrolment drop, the 50% Indian visa decline, and the social media screening regime are not unrelated events. They are components of a deliberate recalibration of who gets to study in America and on what terms.

For the Indian diaspora, the implications extend beyond education. The F-1 pipeline feeds the H-1B workforce, which feeds the green card queue, which feeds the naturalisation track. Constrict the pipeline at the student end and every downstream category feels the pressure — fewer OPT workers, fewer H-1B lottery entries, fewer EB-2 petitions, fewer future citizens.

The families who invested lakhs in coaching centres, standardised test preparation, and application consultants are recalculating. Canada, the UK, Australia, and Germany are all aggressively courting the students America is turning away. The question is whether that shift becomes permanent."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
