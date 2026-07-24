#!/usr/bin/env python3
"""Immigration writer — July 8, 2026 02:00 UTC run"""
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
        "headline": "Microsoft Just Cut 4,800 Jobs. For Indian H-1B Workers, the 60-Day Clock Starts Again",
        "subheadline": "The software giant's latest layoffs, driven by a $190 billion AI spending binge, put hundreds of Indian visa holders on a familiar and brutal countdown — find a new sponsor in two months or leave the country.",
        "slug": make_slug("microsoft-4800-layoffs-h1b-indian-workers-60-day-clock"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Microsoft is among the top H-1B sponsors in the US, with over 6,000 approved petitions in FY2025. Indians account for roughly 70% of all H-1B beneficiaries. Every round of Big Tech layoffs disproportionately puts Indian workers on a 60-day countdown to find new sponsorship or leave lives built over decades.",
        "tags": ["h1b", "microsoft", "layoffs", "tech", "immigration", "60-day-grace-period"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/microsoft-cut-about-6000-jobs-2026-07-07/"},
            {"name": "TheStreet", "url": "https://www.thestreet.com/technology/how-many-employees-does-microsoft-have"},
            {"name": "NY Post", "url": "https://nypost.com/2026/07/07/business/microsoft-lays-off-nearly-5k-workers-most-of-them-at-xbox/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/enterprise/after-years-in-us-now-indian-h-1b-techies-fears-forced-exits"},
            {"name": "USCIS Data", "url": "https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Microsoft_Redmond_Campus_redevelopment_aerial_view%2C_Sept._2021.jpg/1280px-Microsoft_Redmond_Campus_redevelopment_aerial_view%2C_Sept._2021.jpg",
        "image_caption": "Aerial view of the Microsoft campus in Redmond, Washington",
        "image_attribution": "Wikimedia Commons",
        "body": """Microsoft announced on Monday that it is cutting approximately 4,800 jobs — about 2.1 per cent of its global workforce — in a restructuring that spans its commercial operations and Xbox gaming division. The move comes as the company pours a staggering $190 billion into artificial intelligence infrastructure this fiscal year, a sum that has forced it to make hard choices about where its humans fit.

For the thousands of Indian nationals on H-1B visas at Microsoft, the news lands with a particular weight. It triggers a 60-day grace period that has become grimly familiar to the Indian tech diaspora: find a new employer willing to sponsor your visa within two months, or prepare to leave a country where you may have lived for a decade, bought a home, and enrolled your children in school.

## The Numbers Tell a Bleak Story

Microsoft was approved for more than 6,000 H-1B workers in fiscal year 2025 alone, making it one of the programme's largest sponsors. Indians account for roughly 70 per cent of all approved H-1B beneficiaries — approximately 283,772 of 406,348 approved petitions in FY2025, according to USCIS and Department of Homeland Security data.

The company's chief people officer, Amy Coleman, said in a memo to staff that AI was "changing how work gets done" but insisted that "the roles eliminated today are not being replaced by AI." That distinction offers cold comfort to a visa holder whose work authorisation is tethered to a job that no longer exists.

Microsoft's Xbox chief, Asha Sharma, was blunter about the gaming division's troubles. "Our business today is not healthy," she wrote, noting that Xbox operates at margins three to ten times lower than comparable publishers. Some 1,600 gaming roles were cut immediately, with another 1,600 slated for elimination over the rest of the fiscal year.

## A Broader Pattern That Won't Stop

Microsoft's layoffs are not an isolated event. According to Challenger, Gray & Christmas, the first three months of 2026 brought 52,050 tech layoffs — a 40 per cent jump from the same period last year. Data from Layoffs.fyi shows more than 110,000 tech employees across 144 companies have lost their jobs in 2026 so far. Meta cut 8,000 roles. Amazon trimmed its workforce. LinkedIn followed suit. And yet USCIS data shows these same firms remain among the top H-1B sponsors.

https://x.com/unusual_whales/status/1941523697285128192

The cruel arithmetic is straightforward: Big Tech companies simultaneously sponsor thousands of H-1B workers and lay off thousands of employees, creating a revolving door of immigration precarity that disproportionately affects Indians.

## The 60-Day Trap

Under USCIS rules, a laid-off H-1B worker has up to 60 days from their last working day — not their final pay date — to take one of four actions: find a new employer to file an H-1B transfer petition, change to a different visa status, file for adjustment of status, or apply for a "compelling circumstances" employment authorisation document.

That window is proving brutal in the current environment. The new wage-weighted H-1B lottery makes it harder for mid-level engineers to secure fresh sponsorship. The now-blocked $100,000 fee, while struck down by a federal judge last month, has left a chill on employer willingness to sponsor. And the social media vetting requirements that now accompany every immigration application add weeks to processing times.

"I no longer think in months," a 30-year-old Indian software engineer recently laid off from a major tech firm told The Indian Express. "I'm just focused on the number of days remaining."

## What Your Options Actually Look Like

Immigration attorneys outline a narrow set of realistic moves for affected H-1B workers:

**File an H-1B transfer immediately.** A new employer can file a petition, and under the portability provision, you can begin work as soon as USCIS receives it — without waiting for approval. This is the strongest option, but it requires finding an employer willing to sponsor in a frozen hiring market.

**Switch to B-1/B-2 status.** USCIS has clarified that job searching and interviewing are permissible B-1/B-2 activities. You cannot work, but you can buy time while looking for a sponsor.

**Explore O-1 or EB-1A self-petition routes.** Workers with extraordinary ability may be able to self-petition, bypassing employer sponsorship entirely. Approval rates for EB-1A remain around 67 per cent, but the evidentiary bar is high.

**Consider the 180-day I-485 portability rule.** If your I-485 adjustment of status application has been pending for more than 180 days and your I-140 is approved, you may be able to change employers without restarting the green card process.

## The Rethink Has Already Begun

A poll on Blind, the anonymous professional network widely used by tech workers, suggested that nearly half of Indian professionals in the United States would consider returning to India if they lost their jobs. Others are exploring Canada's Global Talent Stream, the UK's High Potential Individual visa, Germany's Opportunity Card, and Australia's Global Talent visa as alternatives.

India's own technology sector has been quietly capitalising on this uncertainty. The country now hosts more than 1,700 Global Capability Centres — over half the global total — and the reverse flow of talent from Silicon Valley to Bengaluru and Hyderabad has accelerated.

For the Indian H-1B workers at Microsoft who just received the news, none of this makes Monday morning any easier. The clock is ticking, and 60 days is not very long at all."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Your Company Just Got Acquired. Your Visa Might Not Survive the Deal",
        "subheadline": "A new wave of immigration enforcement has turned routine corporate acquisitions into existential threats for H-1B, L-1, and STEM OPT workers — and most of them have no idea until it is too late.",
        "slug": make_slug("company-acquired-visa-risk-ma-h1b-immigration"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals dominate H-1B and L-1 visa categories at US tech companies. When their employer is acquired, their immigration status can be disrupted or destroyed overnight — and in the current enforcement environment, a sloppy merger can reset years of green card progress or terminate work authorisation entirely.",
        "tags": ["h1b", "immigration", "ma-deals", "corporate-acquisition", "visa-compliance", "green-card"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/transactional/why-immigration-is-new-front-line-ma-due-diligence-2026-07-07/"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/mergers-and-acquisitions/deals-get-tougher-immigration-status-scrutiny-from-lawyers"},
            {"name": "JD Supra", "url": "https://www.jdsupra.com/legalnews/immigration-considerations-in-m-a-and-6117289/"},
            {"name": "ABA Business Law Today", "url": "https://www.americanbar.org/groups/business_law/resources/business-law-today/2026-february/immigration-due-diligence/"},
            {"name": "Fisher Phillips", "url": "https://www.fisherphillips.com/en/news-insights/6-main-workplace-immigration-considerations-ma-transactions.html"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7109292/pexels-photo-7109292.jpeg",
        "image_caption": "Business professionals finalising a corporate deal over financial documents",
        "image_attribution": "Pexels",
        "body": """When Priya Sharma's employer, a mid-size enterprise software company in the Bay Area, was acquired by a larger rival in late 2025, she assumed the transition would be seamless. Her H-1B was valid, her I-140 had been approved, and her PERM labour certification was five years old. She had done everything by the book.

Then the acquiring company's lawyers discovered that the new entity operated under a different Federal Employer Identification Number. Her H-1B needed to be re-filed. Her PERM was tied to the old employer. And her green card clock, which had been running since 2020, effectively reset to zero.

Her case is not unusual. It is, according to a growing body of legal analysis, the new normal.

## The Problem No One Talks About in the Deal Room

A detailed Reuters analysis published this week describes immigration compliance as "one of the highest-risk, yet most consistently underestimated, integration challenges in corporate transactions." The piece, written by practitioners who advise on M&A deals, lays bare a reality that most Indian tech workers never consider: when your company changes hands, your visa does not automatically come along for the ride.

The legal framework is deceptively complex. Under the Immigration and Nationality Act, a "qualifying successor" can inherit approved H-1B petitions, some pending green card cases, and Labour Condition Applications without starting over. But the exception is narrower than it appears. Any "material change" to job duties, title, or work location triggers the need for a new USCIS petition and a new Department of Labour LCA — before the employee begins working at the new site.

In plain terms: if the acquisition changes your reporting structure, your office location, or your job description in any meaningful way, your existing H-1B authorisation may no longer be valid. And you might not find out until it is too late.

## L-1 Workers Face the Worst of It

For Indian workers on L-1 intracompany transfer visas, the risks are even more acute. L-1 eligibility depends entirely on a qualifying corporate relationship between a US entity and a foreign affiliate, subsidiary, or parent. If an acquisition severs or alters that relationship, L-1 eligibility is destroyed — immediately.

"Those employees must either transition to another visa category before the acquisition is executed or cease working," the Reuters analysis notes. There is no grace period. There is no portability provision equivalent to the H-1B's.

Indian IT services companies like TCS, Infosys, and Wipro have historically used L-1 visas to rotate employees between Indian and American offices. As these firms increasingly partner with or are acquired by American companies, the L-1 vulnerability becomes a material business risk.

## STEM OPT: The Forgotten Population

Indian graduates working under the 24-month STEM Optional Practical Training programme — the extension that allows F-1 visa holders to work in the United States for up to three years after graduation — face a separate set of traps.

STEM OPT requires the employer to be enrolled in E-Verify, to execute a formal training plan with the student, and to report any material changes, including changes to the employer's Federal Employer Identification Number, to the student's school. A gap in E-Verify participation during an acquisition transition can "jeopardize STEM OPT authorisation entirely," according to the Reuters analysis.

For the thousands of Indian STEM graduates who rely on OPT as their bridge to the H-1B lottery, this is not a theoretical risk. It is a ticking clock they cannot control.

## The Green Card Trap

Perhaps the cruellest consequence of a poorly managed acquisition falls on workers with pending green card applications. Labour certifications under the PERM regulations, immigrant petitions (I-140), and adjustment of status applications can all be invalidated by changes in legal entity, geographic location, or job duties.

For Indian nationals, who face per-country caps that stretch the EB-2 green card wait to over a decade and the EB-3 wait to priority dates from January 2014, this is catastrophic. A change of employer that resets the PERM process means restarting a queue that may take another 12 years to clear.

The one exception: if your I-485 adjustment of status has been pending for more than 180 days and your I-140 has been approved, the AC21 portability provision allows you to change employers without losing your place in line. But this protection only kicks in at a late stage that most Indian applicants have not yet reached.

## The Enforcement Environment Has Changed

What transforms these longstanding legal vulnerabilities into urgent threats is the current enforcement climate. Immigration and Customs Enforcement has expanded site visits. The Department of Labour has announced plans to investigate companies' H-1B practices. USCIS has increased scrutiny of employer compliance, and the government recently reclassified many technical I-9 violations — such as failure to date certain sections — as substantive violations that cannot be cured during an audit and carry fines of $288 to $2,861 per violation.

Bloomberg Law has reported that immigration compliance has "transformed from another checklist item to something that can delay deals or tank them altogether." Immigration attorney Mary Kate Fernandez of Adams & Reese put it more directly: "It definitely has the potential to kill a deal."

For the acquiring company, inherited I-9 deficiencies, unauthorised workers, or visa holders whose actual employment diverges from their petitions become immediate liability. For the Indian worker caught in the middle, the deal they had no say in may have just ended their American career.

## What You Should Do Before It Happens

Immigration attorneys recommend that H-1B and L-1 workers take proactive steps well before any acquisition closes:

**Know your petition details.** Keep copies of your H-1B approval notice (I-797), LCA, and any PERM documentation. Understand what entity filed your petition and what FEIN it is tied to.

**Ask questions early.** If your company announces an acquisition or merger, ask HR directly whether the new entity qualifies as a successor-in-interest and whether new petitions will need to be filed.

**Protect your green card.** If you have an approved I-140, confirm whether your priority date is portable under AC21. If you do not yet have an approved I-140, discuss with an immigration attorney whether accelerating the process is advisable.

**Monitor your STEM OPT.** If you are on OPT, verify that the new employer is enrolled in E-Verify and that your training plan has been updated to reflect the new entity.

**Document everything.** In the current enforcement environment, the paper trail matters more than ever. Keep records of every change in your employment terms, work location, and reporting structure.

The M&A wave is not slowing down — Deloitte expects both the value and number of deals to increase over the next year. For the hundreds of thousands of Indian workers whose immigration status is tied to their employer, each deal announcement is now a reason to check the fine print."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
