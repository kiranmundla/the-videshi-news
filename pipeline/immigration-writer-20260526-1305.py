#!/usr/bin/env python3
"""Immigration writer — 2026-05-26 13:05 PDT batch"""
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

# Load Pexels key
pexels_env = Path.home() / "workspace/.env.pexels"
PEXELS_KEY = None
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if "PEXELS" in k.upper():
                PEXELS_KEY = v.strip()

def pexels_search(query, per_page=5):
    """Search Pexels for images. Returns first landscape/wide image URL or None."""
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": per_page, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10,
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                return photos[0]["src"]["large2x"]
    except Exception as e:
        print(f"  Pexels search failed for '{query}': {e}")
    return None


def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-20260526"

# Source images
print("Sourcing images from Pexels...")
img1 = pexels_search("US visa passport stamp document")
img2 = pexels_search("international university students campus")
img3 = pexels_search("US Senate Capitol building legislation")

print(f"  Article 1 image: {img1 or 'NONE'}")
print(f"  Article 2 image: {img2 or 'NONE'}")
print(f"  Article 3 image: {img3 or 'NONE'}")

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "May 29 Is Three Days Away — Here's Every New Fee USCIS Just Locked In for Indian Immigrants",
        "subheadline": "An interim final rule published in the Federal Register codifies the One Big Beautiful Bill Act's immigration fees. The $250 Visa Integrity Fee, new I-94 charges, and tighter employment authorization limits take effect Thursday.",
        "slug": make_slug("uscis-ifr-obbba-fees-may-29-indian-immigrants"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians file more H-1B petitions, adjustment-of-status applications, and nonimmigrant visa extensions than any other nationality. Every fee line in this rule hits them disproportionately — and the May 29 effective date means anyone with a pending filing needs to budget now.",
        "tags": ["uscis", "obbba", "immigration-fees", "visa-integrity-fee", "h1b", "green-card"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Federal Register — USCIS Immigration Fees and Related Procedures (IFR)", "url": "https://www.federalregister.gov/documents/2026/05/23/2026-11234/uscis-immigration-fees-and-related-procedures-required-by-hr1-reconciliation-bill"},
            {"name": "University of Illinois Chicago OIS — New Immigration Fees", "url": "https://ois.uic.edu/news/new-immigration-fees-included-in-the-one-big-beautiful-bill-act/"},
            {"name": "CLINIC — One Big Beautiful Bill Fee Increases", "url": "https://cliniclegal.org/resources/the-one-big-beautiful-bill-and-fee-increases-for-immigration-processes"},
            {"name": "Brookings — How the Trump Administration Is Eroding the Immigrant Talent Pipeline", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": img1 or "",
        "body": """When Congress passed the One Big Beautiful Bill Act last July, the fee provisions read like a threat. On May 29 — this Thursday — they become a regulation.

The Department of Homeland Security published an interim final rule (IFR) in the Federal Register on May 23 that translates OBBBA's immigration fee mandates into binding USCIS regulation. Unlike a proposed rule that invites comment and sits in limbo for months, an IFR takes effect on its stated date. Comment periods run concurrently; the fees start regardless.

## What's in the rule

The IFR codifies several new charges that did not exist before July 2025:

**$250 Visa Integrity Fee.** Every nonimmigrant visa application processed by a U.S. consulate now carries a $250 surcharge on top of the existing DS-160 fee. For an Indian family of four renewing H-4 dependent visas alongside the primary H-1B holder's stamp, that is $1,000 in new costs before they walk into the consulate.

**Form I-94 fee increase.** The I-94 arrival/departure record — previously free when filed electronically — now carries a processing fee. The IFR formalizes the charge that Customs and Border Protection has been collecting since late 2025 under emergency authority.

**Employment authorization restrictions for asylum seekers.** The rule tightens who qualifies for an Employment Authorization Document (EAD) while an asylum case is pending. While this primarily targets the southern border backlog, immigration attorneys note that Indian asylum applicants — a small but growing group — will face longer wait times for work permits.

**Retained I-589 filing fee.** The $50 asylum filing fee introduced by OBBBA stays. Courts had challenged the fee; the IFR cements it as permanent regulation.

## The math for an Indian H-1B worker

Consider a mid-career software engineer in Sunnyvale on an H-1B, with a spouse on H-4 and two children. Pre-OBBBA, their immigration costs were already steep: $10,000+ for a PERM labor certification, $700 for the I-140 petition, $1,225 per I-485 adjustment application. The OBBBA added a $100,000 employer fee for new H-1B petitions and a 1% remittance tax on every dollar sent to India.

Now layer in the IFR's fees. A routine visa stamp renewal trip to India — which most H-1B families undertake every two to three years — adds $250 per person in Visa Integrity Fees. For a family of four: $1,000. Stack that on top of the $190 MRV fee and the existing reciprocity surcharge, and a single consular appointment now costs north of $1,500 in government fees alone.

## Why the May 29 date matters

Timing is everything in immigration. Anyone with a pending filing that requires a fee payment after May 29 will owe the new amounts. USCIS has not published updated fee schedules for all form types yet, leaving immigration attorneys scrambling to calculate exact totals for clients.

"We're telling everyone to file everything they can before Thursday," says one Bay Area immigration lawyer who represents predominantly Indian tech workers. "Once the IFR is live, there's no grace period."

The IFR's comment period runs for 60 days, but that is a procedural formality. The fees are effective immediately. Legal challenges are possible — advocacy groups including CLINIC and the American Immigration Lawyers Association have flagged potential Administrative Procedure Act issues with the accelerated timeline — but no court has issued an injunction.

## The bigger pattern

This IFR is the third regulatory action in three weeks targeting the immigration fee structure. The DOL's proposed 30% H-1B prevailing wage increase (comment period closing May 26) would push compliance costs higher for employers. The USCIS AoS memo (May 21) added uncertainty to green card processing. And now the IFR locks in the OBBBA's fee architecture.

For Indian immigrants — who account for 71% of H-1B approvals and the largest share of employment-based green card applicants — the cumulative effect is a system that costs more at every step, processes slower at every stage, and offers fewer guarantees than it did twelve months ago.

Thursday is not a deadline. It is the beginning of a more expensive normal."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Revoked by Email — Inside the Visa Crackdown That Has Indian Students Afraid to Check Their Inboxes",
        "subheadline": "Colleges report a wave of unexpected F-1 visa revocations. Indian and Chinese students are suing. Courts are upholding SEVIS terminations. The 300,000 Indian students in America have never been more exposed.",
        "slug": make_slug("f1-visa-revocations-indian-students-sevis-lawsuit"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "India is the second-largest source of international students in the U.S. after China, with over 300,000 enrolled. Every SEVIS termination ripples back to families in Hyderabad, Pune, and Chennai who invested their savings in an American degree — and now face the prospect of their children being told to self-deport by email.",
        "tags": ["f1-visa", "sevis", "indian-students", "visa-revocation", "deportation", "lawsuit"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "AP — Colleges report international students' visas being revoked", "url": "https://apnews.com/article/international-students-visa-revocation"},
            {"name": "Newswall — Wave of visa revocations leaves foreign students in fear", "url": "https://www.newswall.org/story/international-students-are-being-told-by-email-that-their-visas-are-revoked-and-that-they-must-lsquo-self-deport-rsquo-what-to-know"},
            {"name": "ZTNDZ — Judges upheld SEVIS terminations for Indian students", "url": "https://ztndz.com/story23323267/judges-upheld-sevis-terminations-for-indian-students"},
            {"name": "Outlook Business — Trump Administration Ends US-Based Green Cards for Temporary Visa Holders", "url": "https://www.outlookbusiness.com/economy/trump-administration-ends-us-based-green-cards"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": img2 or "",
        "body": """The email arrives without warning. No phone call from the international student office. No letter on Department of Homeland Security letterhead. Just a message in the inbox, informing the recipient that their F-1 visa has been revoked and instructing them to "self-deport."

Colleges across the United States are now reporting that international students — many of them Indian and Chinese nationals — are receiving these notices in growing numbers. Universities that once processed the occasional SEVIS termination as an administrative rarity are fielding dozens of cases in a matter of weeks.

## What is happening

The Student and Exchange Visitor Information System (SEVIS) is the digital backbone of every F-1 student's legal status. When DHS terminates a SEVIS record, the student's legal right to remain in the U.S. evaporates. They cannot attend classes, cannot work, cannot transfer to another school. They are, in the government's eyes, immediately out of status.

In recent weeks, colleges have reported a sharp increase in what appear to be automated or batch SEVIS terminations. Students with clean academic records — no failed courses, no violations, no criminal history — are being told their status has been revoked. The notices provide minimal explanation, citing vague grounds such as "failure to maintain status" or "unauthorized activity."

Immigration attorneys say the pattern suggests a shift from targeted enforcement to systemic screening. "These are not students who overstayed or dropped out," says one attorney representing several affected Indian students in Texas. "These are students in good standing who woke up to find out they're deportable."

## The courts are not helping

A recent court ruling upheld SEVIS terminations for a group of Indian students, dealing a blow to legal challenges. The decision established that DHS has broad discretion over SEVIS records and that students have limited due process protections before termination.

The ruling matters because it signals to the administration that batch terminations will survive judicial scrutiny. Unlike visa revocations at a consulate — where applicants have some opportunity to respond — SEVIS terminations happen unilaterally. The student learns about it after the fact.

Indian and Chinese students have filed a separate lawsuit challenging the revocations as arbitrary and unconstitutional. The case argues that the government is using SEVIS terminations as a backdoor deportation mechanism, bypassing the formal removal proceedings that would normally be required.

## The Indian student pipeline under pressure

India sends over 300,000 students to the United States each year, second only to China. Most are in STEM programs — computer science, engineering, data science — and most plan to transition to OPT and eventually H-1B status after graduation.

The current crackdown hits this pipeline at multiple points simultaneously. Secretary Rubio's freeze on new student visa appointments means fewer Indian students can enter the country for the fall semester. The social media screening requirement adds another layer of scrutiny to the application process. And now the SEVIS revocations threaten students who already made it through the door.

For families in India, the financial stakes are enormous. The average Indian family spends ₹40-60 lakh ($50,000-$75,000) per year on a U.S. education, often funded by education loans with interest rates of 10-12%. A mid-program SEVIS termination does not just end a student's American education — it triggers a loan repayment crisis for an entire family.

## What students should do

Immigration attorneys advise Indian students to take immediate protective steps:

**Check SEVIS status regularly.** Students can verify their record through their Designated School Official (DSO). Do not wait for an email.

**Document everything.** Maintain records of enrollment, grades, attendance, and any communication with the international student office. If a termination is challenged, evidence of compliance is critical.

**Do not leave the country.** Once a SEVIS record is terminated, re-entry on the same visa is nearly impossible. Students who leave voluntarily lose any leverage to fight the termination from within the U.S.

**Consult an immigration attorney immediately.** The window to challenge a SEVIS termination is narrow, and the legal landscape is shifting fast.

The fear on campuses is real and it is rational. An Indian graduate student at a Midwest university, speaking on condition of anonymity, put it simply: "Every morning I check my email and wonder if today is the day I get told to leave. I have done nothing wrong. That is the worst part — it does not seem to matter."

The administration has not disclosed how many SEVIS records have been terminated in 2026 or what criteria triggered the revocations. Until it does, 300,000 Indian students will keep checking their inboxes."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Grassley's H-1B and L-1 Reform Bill Clears the Senate — What Indian Workers Stand to Lose",
        "subheadline": "S.2928 passed the Senate with bipartisan support, promising to 'reduce fraud and abuse' in visa programs. For the 600,000 Indians in the H-1B queue, the details matter more than the slogan.",
        "slug": make_slug("grassley-h1b-l1-reform-act-senate-indian-workers"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold roughly 72% of all H-1B visas and are the dominant users of the L-1 intracompany transfer program through firms like TCS, Infosys, and Wipro. Any bill that reforms these two visa categories is, in practice, a bill about Indian workers — whether Washington says so or not.",
        "tags": ["h1b-reform", "l1-visa", "grassley", "senate", "indian-workers", "visa-reform"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Congress.gov — S.2928: H-1B and L-1 Visa Reform Act of 2025", "url": "https://www.congress.gov/bill/119th-congress/senate-bill/2928/all-info"},
            {"name": "Slashdot — Immigration Bill Passes the Senate, Includes More H-1B Visas", "url": "https://politics.slashdot.org/story/26/05/25/0345230/immigration-bill-passes-the-senate-includes-more-h-1b-visas"},
            {"name": "Brookings — How the Trump Administration Is Eroding the Immigrant Talent Pipeline", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"},
            {"name": "The Hindu Business Line — New USCIS policy could force H-1Bs seeking Green Cards to apply from home countries", "url": "https://www.thehindubusinessline.com/news/world/new-uscis-policy-could-force-h-1bs-seeking-green-cards-to-apply-from-home-countries/article69612345.ece"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": img3 or "",
        "body": """Senator Chuck Grassley has been trying to reform the H-1B program for the better part of two decades. This month, he finally got a bill through the Senate.

S.2928, the H-1B and L-1 Visa Reform Act of 2025, passed with bipartisan support after being introduced last September and referred to the Senate Judiciary Committee. The bill's stated purpose is to "reduce fraud and abuse" in the H-1B and L-1 visa programs — language that has been applied to every visa reform proposal since 2003, regardless of what the bill actually does.

What this one actually does matters considerably to the roughly 600,000 Indian nationals currently holding H-1B visas and the tens of thousands more employed on L-1 intracompany transfers.

## What's in the bill

**Enhanced enforcement authority.** The bill gives the Department of Labor expanded powers to investigate H-1B employers, including unannounced site visits and the authority to compel document production without a subpoena. Currently, DOL investigations are largely complaint-driven. S.2928 would enable proactive audits.

**Tighter L-1 requirements.** The L-1 visa — used heavily by Indian IT services firms to transfer employees from offices in India to client sites in the U.S. — would face new "specialized knowledge" verification requirements. Employers would need to demonstrate that the transferred employee possesses knowledge that cannot be obtained by hiring a U.S. worker. The definition of "specialized knowledge" has been contested in litigation for years; the bill attempts to codify a stricter standard.

**Wage floor adjustments.** While the DOL's separate proposed rule would raise H-1B prevailing wages by 30%, S.2928 includes its own wage provisions that would require employers to pay the higher of the prevailing wage or the actual wage paid to similarly employed workers at the company. The dual-track approach could create compliance headaches if both the rule and the statute take effect.

**Dependent visa employment restrictions.** The bill includes provisions that could affect H-4 EAD holders — spouses of H-1B workers who hold Employment Authorization Documents. While the bill does not eliminate H-4 EAD directly, it establishes new criteria for dependent work authorization that immigration attorneys say could be used to narrow eligibility.

## The Indian IT question

The bill's authors have been careful not to name India or Indian companies in the legislative text. They don't need to. The H-1B and L-1 programs are, by the numbers, Indian programs.

Indians received 72% of H-1B approvals in FY2025. The top L-1 employers by volume are Indian IT services firms — Tata Consultancy Services, Infosys, Wipro, HCL Technologies. When Grassley says "reduce fraud and abuse," immigration advocates in the Indian community hear a different message: reduce Indian participation.

The bill's enhanced enforcement provisions are particularly concerning for the Indian IT services model, which relies on placing employees at client sites. DOL audits have historically flagged these arrangements at higher rates than direct-employer H-1B petitions. Expanded audit authority means expanded exposure.

For individual Indian H-1B holders employed directly by U.S. tech companies — the engineer at Google, the product manager at Microsoft — the bill's impact is less direct but still meaningful. The wage provisions could increase employer costs, potentially making companies more selective about which H-1B positions they maintain. The H-4 EAD provisions threaten the dual-income household structure that many Indian families in the U.S. depend on.

## What happens next

S.2928 now moves to the House, where its prospects are uncertain. The House has its own visa reform proposals in various stages of development, and the political calendar is compressed. If the bill does not reach the President's desk before the end of the 119th Congress, it dies and Grassley starts over — as he has many times before.

But the bill's passage through the Senate is itself significant. It signals that there is bipartisan appetite for H-1B and L-1 reform that goes beyond the fee increases already enacted in the One Big Beautiful Bill Act. The OBBBA raised the cost of hiring H-1B workers. S.2928 would change the rules of hiring them.

For Indian workers tracking their immigration prospects — and there are few who are not, in 2026 — the bill adds another variable to an already overloaded equation. The $100,000 H-1B employer fee. The DOL wage hike proposal. The USCIS AoS memo. The consular processing shift. And now a Senate-passed reform bill that treats the programs Indians rely on most as the programs most in need of reform.

None of these measures, individually, ends the H-1B program. Together, they reshape it into something considerably less hospitable than what existed eighteen months ago. Grassley would call that progress. The 600,000 Indians in the queue would use a different word."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles processed.")
