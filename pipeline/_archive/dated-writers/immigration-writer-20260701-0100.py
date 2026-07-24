#!/usr/bin/env python3
"""Immigration writer — 2026-07-01 01:00 PT run. Three articles."""
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


# ── Article 1: China K Visa ──────────────────────────────────────────────

art1_body = """The United States charges companies $100,000 for a new H-1B petition. China charges nothing for its K visa and does not require a job offer. The contrast is not subtle, and Beijing knows it.

China's K visa programme, which launched in October 2025, targets young STEM graduates with a deal that would have seemed improbable a decade ago: multiple entries, longer stays, and no employer sponsorship required. It supplements Beijing's existing R visa for senior professionals, but strips away the barriers that made China a second-choice destination for globally mobile engineers.

"The symbolism is powerful: while the U.S. raises barriers, China is lowering them," Matt Mauntel-Medici, an Iowa-based immigration attorney, told Reuters when the programme launched.

The timing is not accidental. Days before the K visa went live, the Trump administration announced the $100,000 H-1B fee — a move that sent Indian professionals scrambling. Some booked last-minute flights home. Others cancelled travel altogether, terrified they would not get back in.

## The Indian Professional Who Looked East

Vaishnavi Srinivasagopalan, an Indian IT professional who has worked in both India and the United States, told the Associated Press she had been looking for opportunities in China. Her father once worked at a Chinese university, and the K visa could turn her interest into a career.

"It is a good option for people like me to work abroad," she said.

She is not alone. Bikash Kali Das, an Indian master's student at Sichuan University, said the H-1B route that Indian students once counted on is no longer reliable. "Students studying in the U.S. hoped for an H-1B visa, but currently this is an issue," he told the AP.

## Not Just China

Beijing is hardly the only capital reading the room. South Korea, Germany, and New Zealand have all loosened visa rules for skilled migrants in the past year. Canada has long positioned itself as the friendly alternative for Indian tech workers, and its Express Entry system continues to draw applicants who once would have aimed solely for Silicon Valley.

The Information Technology and Innovation Foundation, a Washington think tank, warned in a recent report that the combination of the $100,000 fee and China's K visa "could be detrimental to U.S. efforts to attract top STEM talent." The foundation noted that temporary visa holders accounted for 58 per cent of all computer science doctorates and 51 per cent of engineering doctorates awarded in the U.S. in 2024.

## The Backlash Inside China

The K visa has not been universally welcomed at home. China's domestic job market is brutally competitive, with youth unemployment stubbornly high, and the prospect of imported foreign workers has triggered a furious backlash on social media.

"Attracting foreign talent with the K visa is a good thing, but it comes at the worst time," wrote Xiang Dongliang, a popular Chinese commentator whose readers frequently complain about poor job prospects.

India's media, meanwhile, offered a different read. "Beijing's pitch is clear: skip the drama, pack your bags and we'll give you ample opportunities," said anchor Palki Sharma Upadhyay on Firstpost.

## What This Means for Indian Americans

For the roughly 600,000 Indians on H-1B visas in the United States, the K visa is not a realistic alternative today. Language barriers, limited citizenship pathways, and China's opaque regulatory environment make it a hard sell for someone settled in San Jose or Austin.

But that misses the larger point. The K visa matters not because Indian H-1B holders are about to move to Shenzhen, but because it signals that the global market for high-skilled talent has shifted. Countries are competing. The United States is not.

Every barrier Washington erects — the $100,000 fee, the wage-weighted lottery, the social media vetting, the nine-month consulate queues — makes the calculus slightly different for the next generation of IIT graduates deciding where to build a career. America's monopoly on aspiration is no longer guaranteed."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "China's K Visa Wants India's Best Engineers. Washington Barely Noticed",
    "subheadline": "Beijing launched a no-fee, no-job-offer visa for STEM talent just as the U.S. made the H-1B unaffordable. The global talent race is on, and America is not running.",
    "slug": make_slug("china-k-visa-indian-engineers-global-talent-race"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B holders face a $100,000 fee and years-long backlogs while China, Canada, Germany, and South Korea roll out easier paths for STEM talent — reshaping where the next generation of Indian engineers choose to build careers.",
    "tags": ["h1b", "china", "k-visa", "immigration", "stem", "talent-war"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/chinas-new-k-visa-beckons-foreign-tech-talent-us-hikes-h-1b-fee-2025-09-29/"},
        {"name": "Associated Press", "url": "https://apnews.com/article/china-k-visa-h1b-trump-foreign-workers"},
        {"name": "ITIF", "url": "https://itif.org/publications/2025/12/09/china-welcomes-stem-talent-while-the-united-states-pushes-it-away/"},
        {"name": "Marketplace / APM", "url": "https://www.marketplace.org/2025/10/17/chinas-h1b-talent-visa-gets-praise-abroad-and-backlash-at-home/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "An open passport displaying travel stamps from multiple countries",
    "image_attribution": "Pexels",
    "body": art1_body,
}


# ── Article 2: Social Media Vetting ──────────────────────────────────────

art2_body = """Your next H-1B visa interview may begin long before you sit down across from a consular officer. It starts the moment someone in the State Department opens your LinkedIn profile.

Since December 15, 2025, the U.S. Department of State has required all H-1B and H-4 visa applicants to set their social media accounts to "public." Consular officers now conduct a formal "online presence review" before interviews — scrolling through LinkedIn profiles, Facebook posts, Instagram feeds, and anything else that surfaces in a search of the applicant's name.

The policy is not new in concept. The DS-160 visa application form has asked for social media handles for years. What changed is the scope, the scrutiny, and the consequences.

## What Officers Are Looking For

A State Department cable, reviewed by multiple immigration attorneys and reported by Bloomberg Law, instructs consular officers to review LinkedIn profiles and resumes for evidence of work involving "activities such as misinformation, disinformation, fact-checking, compliance and online safety, among others."

If an officer concludes that an applicant was "responsible for, or complicit in, censorship or attempted censorship of protected expression in the United States," the guidance directs them to pursue an ineligibility finding under the Immigration and Nationality Act.

Beyond ideology, officers are looking for practical red flags: inconsistencies between a LinkedIn profile and the DS-160 form, undisclosed employment, job titles that do not match the petition, gaps in work history, and any indication that the applicant intends to settle permanently rather than work temporarily.

Brad Bernstein, an immigration attorney, told Livemint that officials also flag signs that social media posts were deleted after the visa application was submitted — a move that "could raise credibility or misrepresentation concerns."

## Thousands of Appointments Cancelled

The expanded vetting hit Indian consulates like a freight train. Chennai and Hyderabad — two of the highest-volume posts for H-1B processing — cancelled thousands of appointments in December 2025, rescheduling many as far out as April and May 2026.

"Due to operational constraints related to processing these visas and to ensure that no applicants issued a visa pose a threat to U.S. national security or public safety, the U.S. Consulate in Chennai must reduce the number of applicants each day," read one email reviewed by Bloomberg Law.

The U.S. Embassy in India posted on X that arriving at previously scheduled appointment times "will result in your being denied admittance to the Embassy or Consulate."

The ripple effects were immediate. Google's external immigration counsel, BAL Immigration Law, sent an email urging affected employees to avoid international travel due to "severe appointment backlogs at diplomatic missions" and warning them not to "risk an extended stay outside the US." Apple issued similar guidance.

## The India Problem

Indians account for roughly 71 per cent of all approved H-1B petitions. Combined with the September 2025 rule restricting H-1B holders to visa interviews at consulates in their home country (no more third-country stamping in Canada or Mexico), the social media vetting creates a bottleneck with a distinctly Indian shape.

An H-1B worker whose visa expires faces a grim sequence: book a flight to India, wait weeks or months for a consulate appointment, submit to a social media review that could itself trigger "administrative processing" lasting additional weeks, and hope that nothing on a LinkedIn post from 2019 raises a flag. If something does, there is no appeal — just a 221(g) notice and an open-ended wait.

One applicant told ANI that their Chennai appointment, originally scheduled for December 18, was cancelled after biometrics and automatically rescheduled to April 30, 2026 — four months of professional limbo.

## What You Should Do

Immigration attorneys are converging on a few practical steps:

**Do not delete anything.** The State Department has made it clear that removing or altering content after applying for a visa raises credibility concerns. Deleting a post looks worse than whatever the post said.

**Audit your LinkedIn.** Ensure that job titles, dates, and descriptions match your DS-160 and petition support letter exactly. A promotion you forgot to update, or a freelance gig you listed as full-time, can trigger a flag.

**Google yourself.** Consular officers will. Any blog post, YouTube comment, or conference bio that appears under your name is fair game.

**Set profiles to public before applying.** Locked or private accounts may be treated as non-compliance with the vetting requirement, which can itself delay or derail an interview.

**Keep your employer informed.** Companies should be building immigration delays into project timelines and identifying critical-path employees whose travel should be deferred.

The State Department insists the process applies uniformly to all nationalities. That is technically true. But when 71 per cent of H-1B holders are Indian, and the consulates grinding to a halt are Chennai and Hyderabad, the policy's disproportionate impact is a matter of arithmetic, not intent."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Your LinkedIn Profile Could Tank Your Visa Interview. The State Department Is Reading It",
    "subheadline": "New social media vetting rules have cancelled thousands of H-1B appointments at Indian consulates. Here is what officers are looking for — and what you should not delete.",
    "slug": make_slug("linkedin-social-media-vetting-h1b-visa-india-consulate"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians hold 71% of H-1B visas and are disproportionately affected by expanded social media screening at U.S. consulates — with Chennai and Hyderabad cancelling thousands of appointments and rescheduling them months out.",
    "tags": ["h1b", "social-media", "linkedin", "visa-interview", "uscis", "consulate", "india"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/h-1b-visa-interviews-delayed-in-india-amid-social-media-review"},
        {"name": "Livemint", "url": "https://www.livemint.com/news/india/h1b-visa-holders-in-limbo-what-social-media-content-can-get-you-in-trouble-red-flags-to-watch-out-for"},
        {"name": "Mondaq / Green and Spiegel", "url": "https://www.mondaq.com/unitedstates/work-visas/1573444/new-social-media-screening-rules-are-delaying-h-1b-and-h-4-visa-interviews"},
        {"name": "Nolo", "url": "https://www.nolo.com/legal-updates/2026-immigration-legal-updates.html"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/33440526/pexels-photo-33440526.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A smartphone displaying the LinkedIn logo against a keyboard background",
    "image_attribution": "Pexels",
    "body": art2_body,
}


# ── Article 3: Blanche v. Lau — Green Card Holders at the Border ─────────

art3_body = """Green card holders have always had the right to re-enter the United States. Last week, the Supreme Court made that right a little less certain.

In a 6-3 ruling in *Blanche v. Lau*, the Court held that border agents do not need to meet the high "clear and convincing evidence" standard before refusing re-entry to a lawful permanent resident suspected of committing a crime. The decision, written by Justice Clarence Thomas and joined by Chief Justice Roberts and Justices Gorsuch, Kavanaugh, Alito, and Barrett, effectively lowers the evidentiary bar that has protected green card holders at the border for decades.

The case centred on Muk Choi Lau, a green card holder who was indicted on trademark counterfeiting charges before returning to the United States from a trip abroad. Customs and Border Protection officers paroled him in — a temporary admission that falls short of the standard admission process for lawful permanent residents — rather than admitting him normally. He was later convicted and faced deportation proceedings.

## The Legal Shift

Under prior practice, a green card holder returning from abroad was treated almost like a citizen at the border. The government needed strong evidence — "clear and convincing" — to deny entry. The *Blanche v. Lau* ruling does away with that standard for cases involving suspected crimes of moral turpitude, a broad legal category that includes fraud, counterfeiting, theft, and certain financial offences.

The practical effect: border agents can now parole in or refuse a green card holder based on a lower evidentiary threshold. An indictment, or even reasonable suspicion of a qualifying crime, may be enough.

Justice Sotomayor, joined by Justices Kagan and Jackson in dissent, warned that the ruling undermined the security that permanent residency is supposed to provide.

Andrew Arthur, a fellow at the Center for Immigration Studies who specialises in immigration law, called the ruling a win for the administration's enforcement agenda. It will "strengthen CBP's legal ability to turn away or put on probation immigrants if they are suspected of being serious criminals," he wrote.

## Why Indian Green Card Holders Should Pay Attention

At first glance, this may seem irrelevant to the typical Indian American green card holder — a software engineer or physician who has never been near a counterfeiting operation. But immigration attorneys caution that the ruling's implications extend beyond the specific facts.

"Crimes of moral turpitude" is a notoriously elastic concept in immigration law. It can encompass fraud (including tax fraud), theft, embezzlement, and certain white-collar offences. A pending investigation, an unresolved tax dispute with the IRS, or even a misdemeanour charge that seemed minor domestically could, under this lowered standard, give a border agent grounds to parole rather than admit a returning green card holder.

For the roughly 700,000 Indians in the green card backlog — many of whom already hold green cards or are in the final stages — this adds a new layer of risk to international travel. Combined with the September 2025 restriction limiting visa interviews to home-country consulates, travelling to India now carries compounding uncertainties.

If a green card holder is paroled rather than admitted, they enter a legal grey zone. Parole does not confer the same rights as admission. It can be revoked, and it changes the procedural landscape for any future immigration proceedings.

## A Week of Supreme Court Immigration Rulings

The *Blanche v. Lau* decision landed in the same Supreme Court term as three other major immigration rulings. On Thursday, June 25, the Court ruled 6-3 that asylum seekers standing in Mexico have not "arrived in" the United States — meaning they cannot claim the right to an inspection until they physically cross the border. On Tuesday, June 30, the Court upheld birthright citizenship in a 6-3 ruling that struck down Trump's executive order.

Read together, the message is mixed. The Court will defend constitutional guarantees (birthright citizenship), but it will also give the executive branch wider discretion at the border and in enforcement.

## The Practical Takeaway

If you hold a green card and travel internationally, the *Blanche v. Lau* ruling changes your risk calculus in one specific way: any unresolved legal matter — even one you consider minor — could now be enough for a border agent to parole you in rather than admit you. That distinction, which sounds bureaucratic, has real consequences for your immigration status and future proceedings.

Immigration attorneys recommend that green card holders resolve any pending legal matters before travelling and carry documentation of case dispositions when re-entering the country. If you have any doubt about a past or pending issue, consult an immigration lawyer before booking a flight."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The Supreme Court Just Made It Easier to Turn Away Green Card Holders at the Border",
    "subheadline": "A 6-3 ruling in Blanche v. Lau lowers the evidentiary bar for denying re-entry to lawful permanent residents. For Indian green card holders who travel, the risk calculus just changed.",
    "slug": make_slug("scotus-blanche-lau-green-card-border-denial-indian"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "With 700,000 Indians in the green card backlog and strict home-country consulate rules already limiting travel, the Blanche v. Lau ruling adds a new risk — any unresolved legal matter could now be enough for CBP to deny re-entry.",
    "tags": ["green-card", "supreme-court", "border", "cbp", "immigration", "blanche-v-lau"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/opinion/3444038/supreme-court-must-reform-immigration-system-landmark-ruling/"},
        {"name": "Reuters", "url": "https://www.reuters.com/legal/on-immigration-supreme-court-accedes-trumps-restrictive-agenda-2026-06-27/"},
        {"name": "Daily Caller", "url": "https://dailycaller.com/2026/06/25/supreme-court-rules-illegals-outside-the-us-have-not-arrived-in-the-us/"},
        {"name": "Center for Immigration Studies", "url": "https://cis.org/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Exterior_of_Supreme_Court_Building_20240601.jpg/1280px-Exterior_of_Supreme_Court_Building_20240601.jpg",
    "image_caption": "The exterior of the United States Supreme Court building in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body,
}


# ── Insert ────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
