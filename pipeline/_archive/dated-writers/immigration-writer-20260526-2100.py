#!/usr/bin/env python3
"""Immigration writer for The Videshi — 2026-05-26 21:00 PDT run."""
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
        "headline": "Washington Blinks — USCIS Walks Back Green Card Panic, But the Relief Is Thinner Than It Looks",
        "subheadline": "A USCIS spokesman now says H-1B holders who show 'economic benefit' can stay in the US during green card processing. Immigration lawyers say the vague criteria create a new kind of uncertainty.",
        "slug": make_slug("uscis-walks-back-green-card-panic-economic-benefit"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian professionals hold 71% of all H-1B visas and face the longest green card backlogs of any nationality. The May 26 clarification directly determines whether hundreds of thousands of them can remain employed in the US or must uproot their families for consular processing abroad.",
        "tags": ["h1b", "uscis", "green-card", "adjustment-of-status", "pm-602-0199"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Global Net News", "url": "https://globalnet.news/us-immigration-agency-clarifies-green-card-application-rules-for-h-1b-visa-holders/"},
            {"name": "Diaspora Messenger", "url": "https://diasporamessenger.com/2026/05/powerful-relief-uscis-clarifies-rules-for-h-1b-visa-holders-2/"},
            {"name": "H-1B Founders Community", "url": "https://community.h1bfounders.com/p/uscis-green-card-memo-explained-for"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
        "body": """Five days after USCIS dropped a six-page memo that sent Indian WhatsApp groups into a spiral, Washington is doing what Washington does best: walking it back just enough to quiet the noise without actually fixing anything.

On May 26, USCIS spokesperson Zach Kahler told reporters that H-1B visa holders pursuing green cards will not necessarily be forced to leave the country. "People who present applications that provide an economic benefit or otherwise are in the national interest will likely be able to continue on their current path," Kahler said — a markedly softer tone than his earlier statement that any foreign national seeking a green card would "generally need to return to their home country."

## What Changed — and What Didn't

The original Policy Memorandum PM-602-0199, issued May 21, reclassified adjustment of status — the process of applying for a green card from inside the US — as an "extraordinary act of administrative grace." The language was designed to give USCIS officers broad discretion to push applicants toward consular processing abroad, rather than letting them stay put while their cases are decided.

The May 26 clarification doesn't rescind the memo. It doesn't revise it. It offers three conditions under which an applicant might be spared: demonstrating **economic benefit** to the US, serving the **national interest**, or presenting **individualized circumstances** that an officer deems compelling.

That last category — "individualized circumstances" — has no published criteria. USCIS has not defined what qualifies. Immigration attorneys say this is the kind of bureaucratic ambiguity that produces inconsistent outcomes and punishes applicants who can't afford expensive legal representation.

## The Panic Was Real — and Partly Justified

The original memo triggered genuine alarm across the Indian professional community. Indians account for roughly 71% of approved H-1B petitions and face green card backlogs stretching decades in the EB-2 and EB-3 categories. For many, adjustment of status isn't a preference — it's the only viable option. Leaving the US to process through a consulate triggers a 10-year unlawful presence bar for anyone who has overstayed, and even those in valid status face months-long delays at understaffed consulates in India.

"When you're scared, read the firms doing the filings, not the guy farming your fear for views," wrote the H-1B Founders community in a widely shared analysis. The post noted that the memo "does not cancel adjustment of status" and that dual-intent visa holders — H-1B, L-1, O-1 — retain their legal right to pursue permanent residency from within the US.

But dismissing the panic entirely would be a mistake. Immigration attorney Rachel Girod, a partner at Eldridge Crandell, told Bloomberg Law that "they're implying that it's a negative factor to even just be applying for adjustment of status." The memo, she noted, selectively cites decades-old case law to justify a more restrictive approach.

## What "Economic Benefit" Actually Means for Indian H-1B Holders

The "economic benefit" standard sounds reassuring until you think about who it leaves out. A senior AI engineer at Google or a cardiologist at Johns Hopkins can make a strong case. But the H-1B program covers a broad swath of skilled workers — analysts, QA engineers, accountants, supply chain managers — whose contributions are real but harder to frame as nationally significant.

Immigration experts warn that the vague criteria create a two-tier system: one for high-profile applicants whose employers will fight for them, and another for everyone else. The mid-career software developer at a mid-size consulting firm — exactly the kind of worker who fills thousands of H-1B slots — may struggle to meet a "national interest" bar that was never meant to apply to adjustment of status in the first place.

## The Indian Consulate Bottleneck

Even if the walk-back holds, the consular processing alternative remains deeply impractical for Indian nationals. India has four US consulates handling over 1.2 million visa appointments annually. Wait times at Mumbai and Delhi routinely stretch to months. Sending hundreds of thousands of green card applicants into that queue — while simultaneously asking them to leave their US jobs — would create a logistical catastrophe.

Sridhar Vembu, CEO of Zoho, waded into the debate with a different prescription: "Please come home. Self-respect should dictate your course." His comments drew sharp responses from professionals who have spent years building lives, mortgages, and careers in the US and view the "just go home" framing as tone-deaf to the structural traps of the immigration system.

## What to Do Now

Immigration attorneys are advising clients to do three things: maintain scrupulously clean visa status, strengthen their I-485 applications with evidence of economic contribution and community ties, and — critically — not withdraw pending applications. The memo is guidance, not law. It has not changed eligibility requirements, and withdrawing a pending case could have consequences that are difficult to reverse.

The relief is real but conditional. Washington blinked — but it hasn't looked away."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A 1967 Court Case, a Six-Page Memo, and the Weakest Legal Foundation in Modern Immigration Law",
        "subheadline": "Immigration lawyers are lining up to challenge PM-602-0199 in federal court. Meanwhile, USCIS is already issuing a new kind of evidence request that asks green card applicants to justify their right to stay.",
        "slug": make_slug("pm-602-0199-legal-challenge-court-1967-case-law"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B holders with pending I-485 applications are receiving discretion-based Requests for Evidence — a new category of bureaucratic burden that demands they prove their value to the US. With EB-2 India backlogs stretching decades, knowing the legal vulnerabilities of this memo is essential for anyone deciding whether to keep fighting or give up.",
        "tags": ["uscis", "pm-602-0199", "adjustment-of-status", "legal-challenge", "rfe", "green-card", "immigration-law"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Hamilton Immigration Law", "url": "https://www.hamiltonimmigration.law/post/uscis-s-new-adjustment-of-status-memo-will-probably-come-to-nothing"},
            {"name": "Massa Viana Law", "url": "https://massavianalaw.com/uscis-adjustment-of-status-memo-pm-602-0199/"},
            {"name": "Capitol Immigration Law Group", "url": "https://cilawgroup.com/"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6077326/pexels-photo-6077326.jpeg",
        "body": """The entire legal architecture of USCIS Policy Memorandum PM-602-0199 — the document that has thrown hundreds of thousands of green card applications into doubt — rests on a single word from a 1967 court case about a man who was married to two women at the same time.

That case, *Chen v. Foley*, decided by the Sixth Circuit nearly six decades ago, used the word "extraordinary" to describe adjustment of status. The Board of Immigration Appeals repeated it in *Matter of Blas* in 1974. A string of subsequent cases quoted the same phrase. USCIS built its May 21 memo on that foundation, citing 33 cases to argue that adjusting status inside the US has always been an exceptional privilege rather than a routine process.

Immigration lawyers who have actually read those 33 citations are not impressed.

## Built on Dicta, Not Law

"The memo isn't built on a real foundation," writes Hamilton Immigration Law in a detailed legal analysis. "It found one favorable line in a 1967 case and stacked up every later case that quoted it — but quoting something over and over doesn't make it the law."

The problem runs deeper than stale citations. Most of the cases USCIS relies on involved applicants convicted of drug trafficking, alien smuggling, heroin importation, or marriage fraud. The memo extracts language from those extreme situations and applies it to everyone — including people with clean records, stable families, and decades of tax-paying employment.

More damaging: the entire legal landscape shifted in 1996 when Congress passed IIRAIRA, which added 3-, 5-, and 10-year unlawful presence bars. Before those bars existed, consular processing was genuinely the default path. After 1996, adjustment of status became the safer route for many applicants precisely because leaving the US could trigger a decade-long ban on return. Citing congressional intent from the 1970s to interpret a system Congress fundamentally overhauled in 1996 is, as Hamilton puts it, "exactly the kind of error a first-year law student gets flagged for."

## The Dual-Intent Contradiction

The memo's logic collapses when it meets Congress's own visa categories. H-1B, L-1, and O-1 visas carry what immigration law calls "dual intent" — the holder is admitted to the US with the explicit understanding that they may pursue permanent residency. Congress built these categories knowing that the people who hold them would adjust status.

If adjustment were truly the extraordinary relief the memo claims, why did Congress design entire visa categories that presuppose it? Massa Viana Law frames the contradiction bluntly: "You do not build an elaborate architecture of exemptions, forgiveness provisions, and expansions for a relief you intend officers to deny as a matter of course."

Congress went further. Section 245(k) of the Immigration and Nationality Act forgives up to 180 days of status violations for employment-based applicants. Section 245(i) and the LIFE Act of 2000 expanded adjustment to cover people who had never been formally admitted at all. These are not the statutory choices of a legislature that viewed adjustment as extraordinary.

## The RFEs Are Already Landing

While the legal debate plays out, USCIS has already begun translating the memo into action. Immigration attorneys report receiving a new category of Requests for Evidence on pending I-485 applications — not alleging ineligibility or any adverse factor, but asking applicants to affirmatively build a case for why they deserve "a favorable exercise of discretion."

The RFE language reads like a loyalty test:

- Family ties within the United States
- Residence of long duration in this country
- Hardship to the applicant or family if relief is not granted
- Education and fluency in English
- Service in the US armed forces
- History of employment and business ties
- Evidence of value and service to the community
- Proof of paying taxes

Attorneys say this is the *Matter of Marin / Matter of Mendez-Moralez* equities framework — a balancing test the Board of Immigration Appeals has used for decades. What is new is USCIS asking eligible applicants to prove their worth before any adverse finding has been made, with hard deadlines. The earliest response deadlines are August 12, 2026.

## Why Lawyers Expect It to Be Struck Down

The legal vulnerabilities are numerous. Under the Administrative Procedure Act, an agency cannot change an established policy without a reasonable explanation. Domestic adjustment of status is not a boutique procedure — in fiscal year 2025, USCIS approved roughly 745,000 I-485 applications. Recharacterizing that volume as "extraordinary" strains credibility.

The memo is deliberately labeled as "guidance" rather than a binding rule, which lets USCIS avoid the notice-and-comment rulemaking process. But that label cuts both ways: if it is merely guidance, officers are not obligated to follow it. Hamilton Immigration Law notes that USCIS issued a similar naturalization memo last year suggesting applicants would need to prove they were valuable members of society. "As far as anyone can tell, nothing changed — naturalizations are still adjudicated the way they always were."

Multiple law firms — including Massa Viana Law, Capitol Immigration Law Group, and others — have publicly stated they are preparing federal court challenges if USCIS begins denying applications based on the memo's discretionary framework.

## What This Means for Indian Green Card Applicants

For the estimated 627,000 Indians in the employment-based green card backlog, the practical takeaway is this: the memo is legally vulnerable, likely to face court challenges, and may be largely ignored by frontline officers — just as the naturalization memo was. But the RFEs are real, and the deadlines are enforceable.

Attorneys advise three steps. First, front-load every pending I-485 with positive discretionary evidence: employment records, tax returns, community involvement, family ties, property ownership. Second, if an RFE arrives, respond comprehensively and on time — it is an evidence request, not a denial. Third, do not withdraw pending applications based on panic. The memo does not change statutory eligibility, and a withdrawal is difficult to undo.

The system got tighter. It did not close. But the burden of proving that is now on you."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
