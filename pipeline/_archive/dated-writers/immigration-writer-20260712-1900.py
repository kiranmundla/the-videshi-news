#!/usr/bin/env python3
"""Immigration writer — July 12, 2026 evening run."""

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
        "headline": "The $100,000 H-1B Fee Is Dead in One Court and Alive in Another. Indian Employers Are Caught in the Middle",
        "subheadline": "A Boston judge struck down Trump's visa surcharge as an unconstitutional tax. A Washington court upheld it. A third lawsuit is pending in San Francisco. The fee expires in September anyway — but nobody knows what to pay right now.",
        "slug": make_slug("100k-h1b-fee-circuit-split-indian-employers-legal-chaos"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian IT firms sponsor more H-1B workers than any other nationality, and Indian doctors staff a disproportionate share of rural American hospitals — both groups need clarity on a fee that could either cost them nothing or $100,000 per petition.",
        "tags": ["h1b", "h1b-fee", "uscis", "federal-court", "immigration-policy", "healthcare", "indian-it"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/"},
            {"name": "Associated Press via Montana Public Radio", "url": "https://www.mtpr.org/2026-06-08/federal-judge-strikes-down-trumps-100-000-fee-on-new-h-1b-visas"},
            {"name": "American Hospital Association", "url": "https://www.aha.org/news/headline/2026-03-17-house-bill-would-exempt-health-care-workers-100000-h-1b-visa-filing-fee"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/white-house-says-doctors-may-win-reprieve-from-h-1b-visa-fee"},
            {"name": "CNN", "url": "https://www.cnn.com/2025/10/20/health/h1b-visa-fee-rural-hospitals/index.html"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
        "image_caption": "A USCIS Application Support Center in Queens, New York",
        "image_attribution": "Wikimedia Commons",
        "body": """The $100,000 H-1B visa fee that Donald Trump imposed by executive proclamation in September 2025 is now simultaneously illegal and enforceable, depending on which federal courthouse you happen to be standing in.

On June 8, U.S. District Judge Leo Sorokin in Boston ruled that the fee was an unconstitutional tax that only Congress has the authority to levy. Twenty state attorneys general had sued, arguing the surcharge would cripple hospital recruitment and throttle the pipeline of skilled workers their economies depend on. Sorokin agreed, citing the Supreme Court's February decision striking down Trump's emergency tariffs under similar reasoning — the executive branch was levying revenue without legislative authorization.

"The Court finds that the Policy imposes a tax on H-1B petitions without the requisite delegation by Congress," Sorokin wrote.

The White House was not impressed. Spokeswoman Taylor Rogers said the administration is "confident" the ruling will be reversed on appeal, insisting the president has "clear legal authority to restrict entry of any class of aliens he determines is not in America's best interests."

## Three Courts, Three Outcomes

The problem is that the Boston ruling directly contradicts an earlier decision from a federal court in Washington, D.C. The U.S. Chamber of Commerce had challenged the same fee, but a judge there denied its motion for summary judgment, leaving the surcharge in effect pending appeal. That case is now before the D.C. Circuit Court of Appeals.

A third lawsuit, filed in San Francisco by religious groups and labor organizations, remains unresolved.

The result is a genuine circuit split — an increasingly common feature of immigration law under the current administration, but one with immediate practical consequences. Employers filing H-1B petitions right now face a surreal question: do they pay the $100,000 or not? The answer depends on which court's jurisdiction applies, how USCIS chooses to enforce the fee during conflicting rulings, and whether an appellate court issues a nationwide injunction before the fee's built-in September 2026 expiration date.

For Indian IT firms that collectively sponsor tens of thousands of H-1B workers annually, the confusion is not academic. At $100,000 per petition, the difference between the fee being alive or dead could amount to hundreds of millions of dollars in aggregate costs across the industry.

## Healthcare's Particular Bind

The healthcare sector has been especially vocal. According to an American Hospital Association survey, nearly 65 percent of hospitals that use the H-1B program reported pausing, delaying, or limiting recruitment after the fee was announced. Fifty-seven percent of those frozen positions were clinical roles — doctors, nurses, and specialists in communities that have no one else to fill them.

More than 92 million Americans live in regions designated as primary care Health Professional Shortage Areas. International medical graduates — a disproportionate number of whom are Indian — fill a critical share of those gaps, particularly in rural and underserved communities. A 2021 NIH study found that over 64 percent of international medical graduates practice in medically underserved areas.

Congress has noticed. In March, Representatives Mike Lawler (R-NY), Sanford Bishop (D-GA), Maria Elvira Salazar (R-FL), and Yvette Clarke (D-NY) introduced the bipartisan Physicians and the Healthcare Workforce Act, which would exempt foreign-trained healthcare workers from the $100,000 fee entirely. A hundred House members signed a separate letter urging DHS to grant the exemption administratively.

The White House hinted at flexibility. A spokesperson told Bloomberg that doctors and medical residents "could qualify for exemptions" under a national interest provision in the original proclamation. But no formal exemption has been issued, and hospitals are not inclined to file $100,000 petitions on a "could."

## What This Means for Indian Workers

The fee's legal limbo arrives at a hostile moment for Indian immigration. Vice President JD Vance announced a major H-1B fraud investigation on July 8, naming Cognizant as a company facing whistleblower allegations. The administration's proposed regulatory agenda includes raising H-1B wage thresholds, restricting third-party placements, ending the duration-of-status system for students, and limiting H-4 EAD extensions — a package that would collectively reshape employment-based immigration if finalized this fall.

Against that backdrop, the $100,000 fee's uncertain status is another layer of risk for anyone whose American career depends on employer sponsorship. The fee may expire in September, or it may be revived by an appellate ruling. It may be struck down nationwide, or it may survive in some circuits and die in others.

What it will not do is resolve itself quietly. The contradictory rulings all but guarantee that the question eventually reaches the Supreme Court — though not before thousands of H-1B petitions are filed this summer under rules that nobody can state with certainty."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "USCIS Told Laid-Off Workers They Could Job-Hunt on a Tourist Visa. Now It Is Denying Their Applications",
        "subheadline": "Immigration attorneys report a surge of denials targeting H-1B workers who followed the agency's own guidance — switching to B-2 visitor status after termination and searching for new sponsors. USCIS now calls that guidance 'archived.'",
        "slug": make_slug("uscis-b2-job-search-trap-h1b-laid-off-workers-denials"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "With 73 percent of H-1B holders being Indian nationals and more than 114,000 tech layoffs in 2026, the reversal hits Indian workers harder than any other group — many of whom followed the agency's public guidance and are now facing denial of their status change.",
        "tags": ["h1b", "uscis", "layoffs", "b2-visa", "immigration-policy", "tech-layoffs", "indian-workers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reddy Neumann Brown PC", "url": "https://www.rnlawgroup.com/is-uscis-setting-a-trap-for-h-1b-workers-filing-b-1-b-2-after-termination/"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/immigration-news/indian-tech-workers-face-harsh-reality-after-h-1b-layoffs/"},
            {"name": "Center for Immigration Studies", "url": "https://cis.org/Arthur/Should-USCIS-Be-Advising-B1-and-B2-Visa-Holders-Search-Jobs"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/us-allows-applying-for-jobs-even-on-temporary-visa/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/h-1bs-opt-and-h-4-visas-whats-changing-for-indians-under-trumps-immigration-plan"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7643739/pexels-photo-7643739.jpeg",
        "image_caption": "A professional job interview — an activity USCIS once said was permitted on a tourist visa",
        "image_attribution": "Pexels",
        "body": """In March 2023, when mass layoffs at Google, Microsoft, and Amazon left thousands of Indian H-1B holders scrambling for their next move, U.S. Citizenship and Immigration Services offered what seemed like a lifeline. In a publicly posted tweet, the agency declared: "Many people have asked if they can look for a new job while in B-1 or B-2 status. The answer is, yes. Searching for employment and interviewing for a position are permissible B-1 or B-2 activities."

Immigration attorneys passed the guidance to panicked clients. HR departments built transition plans around it. Workers who had lost their sponsoring employer and could not find a new one within the 60-day grace period filed Form I-539 to change status from H-1B to B-2, as USCIS had suggested, and continued interviewing.

Three years later, the same agency is pulling the rug out.

## The Quiet Reversal

Emily Neumann, managing partner at Reddy Neumann Brown PC — Houston's largest employment-based immigration firm — reported in a detailed analysis this year that her office has seen a surge of Requests for Evidence, Notices of Intent to Deny, and outright denials targeting exactly the people who followed USCIS's own advice.

The denials share a disturbing pattern. USCIS adjudicators acknowledge that the agency's website once described job searching as a permissible B-2 activity, then dismiss that guidance as "archived material" that is "not controlling." In other words, the agency's public statements to thousands of desperate workers now carry no weight in its own proceedings.

More troubling still, adjudicators are using a retroactive logic trap. If a worker filed for B-2 status after termination and later received a new H-1B offer — which is, after all, the entire point of continuing to job-search — USCIS is treating the subsequent H-1B petition as evidence that the worker never had "genuine B-2 intent" in the first place. The worker's success in finding a new sponsor is being wielded as proof that they lied about their intentions.

"This reasoning effectively reframes what had long been treated as a compliance pathway into a potential liability," Neumann wrote. "It discourages compliance and punishes individuals for remaining within the legal system rather than departing prematurely."

## The Law Has Not Changed

The legal basis for the reversal is thin, immigration attorneys argue. The Immigration and Nationality Act defines a B nonimmigrant as someone visiting "temporarily for business or pleasure" and specifically excludes individuals coming "for the purpose of performing skilled or unskilled labor." The operative word is *performing*. The statute does not prohibit seeking employment, attending interviews, networking, or communicating with prospective employers. It prohibits *working*.

That distinction is not semantic — it is the text of the law. Searching for a job is not the same as holding one. No new regulation has been issued. No formal policy guidance has replaced the 2023 tweets. Congress has not amended the statute. The only thing that changed is how individual USCIS officers are adjudicating cases, with no public explanation for the shift.

Under the Administrative Procedure Act, federal agencies are required to provide reasoned explanations for policy changes, particularly when individuals have relied on prior guidance to make high-stakes decisions. Calling a webpage "archived" does not meet that standard.

## The Scale of the Problem

The timing could not be worse. More than 114,000 tech workers have been laid off across nearly 150 companies in 2026, according to industry tracking data. Indians account for 73 percent of all H-1B visa holders, making them by far the most exposed group. Many are mid-career professionals with mortgages, children in American schools, and spouses on H-4 visas whose own work authorization is simultaneously under threat from separate regulatory changes.

The 60-day grace period after termination — already widely criticized as too short — has become even harder to navigate. Rajiv Khanna, a U.S.-based immigration attorney, described the pressure as "intense," noting that families must juggle mortgage payments, lease obligations, school enrollments, and immigration timelines simultaneously, all within two months.

For those who cannot secure a new H-1B sponsor in time, the B-2 route was the recognized bridge. It let them stay legally, continue interviewing, and avoid uprooting their families while they looked for the next opportunity. Now that bridge is being dismantled — quietly, without announcement, and in direct contradiction of the agency's own published position.

## What Workers Should Do Now

Immigration attorneys are not advising workers to abandon the B-2 strategy entirely, but they are warning that it requires far more documentation than it once did. Applicants should be prepared to demonstrate temporary purpose, financial self-sufficiency, ties to their home country, and a genuine plan to depart if no employment materializes.

What attorneys are asking for, above all, is transparency. If USCIS intends to prohibit job searching under B-2 classification, it should say so formally — not through a pattern of unexplained denials that upend the lives of people who trusted the agency's word.

"Transparency and predictability are essential components of due process," Neumann wrote, "particularly in a system where individuals must make time-sensitive decisions that affect their professional and personal futures."

Until that transparency arrives, every laid-off H-1B worker who follows the agency's 2023 guidance does so at their own risk."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
