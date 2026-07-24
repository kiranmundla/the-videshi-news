#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-07-11 07:00 PT"""
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
        "headline": "Twenty-Seven Years of H-1B Cases. Zero Fraud. The Lawyers Handling These Visas Want to See the Evidence",
        "subheadline": "Immigration attorneys with decades of H-1B experience say the fraud JD Vance described at his Milwaukee anti-fraud event is vanishingly rare. The administration's own numbers tell a murkier story.",
        "slug": make_slug("h1b-fraud-probe-immigration-lawyers-pushback-vance-rhetoric"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals hold 73 percent of all H-1B visas. When the Vice President frames the program as a vehicle for fraud and organized crime, every Indian professional on an H-1B becomes collateral damage in a political narrative — regardless of whether the evidence supports it.",
        "tags": ["h1b", "fraud", "jd-vance", "uscis", "immigration-lawyers", "cognizant", "dol"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Milwaukee Journal Sentinel", "url": "https://www.jsonline.com/story/news/politics/2026/07/10/vice-president-jd-vance-targets-alleged-h-1b-visa-fraud-in-milwaukee/90860820007/"},
            {"name": "New York Post", "url": "https://nypost.com/2026/07/09/us-news/vance-labor-watchdog-launch-immigration-fraud-probe-to-protect-american-jobs/"},
            {"name": "Fox Business", "url": "https://www.foxbusiness.com/politics/trump-admin-launches-first-major-h-1b-visa-fraud-investigation"},
            {"name": "Dainik Bhaskar English", "url": "https://bhaskarenglish.in/us-probes-indian-it-firm-cognizant-over-h-1b-visa-fraud/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/March_2026_Official_Vice_Presidential_Portrait_of_JD_Vance_%28head-and-shoulders_cropped%29.jpg/330px-March_2026_Official_Vice_Presidential_Portrait_of_JD_Vance_%28head-and-shoulders_cropped%29.jpg",
        "image_caption": "Vice President JD Vance, who announced the H-1B fraud probe at a Milwaukee anti-fraud event on July 8",
        "image_attribution": "Wikimedia Commons",
        "body": """The announcement was made for television. Vice President JD Vance stood before a crowd in Milwaukee on July 8, flanked by Department of Labor officials, and declared that the federal government had launched "a major investigation" into H-1B visa fraud. Dozens of subpoenas were already out. "American jobs ought to go to American workers," he said, "and not foreign fraudsters."

The applause was enthusiastic. The evidence was thinner.

## The Case the Government Is Making

Labor Department Inspector General Anthony D'Esposito told Fox Business that his office had uncovered "widespread schemes" in which employers and labor brokers submitted fraudulent H-1B applications, ran wage-kickback operations, and flooded the labor market with underpaid foreign workers. He said whistleblowers had named "some of the biggest companies," including Cognizant, the IT services giant founded in India and headquartered in New Jersey.

D'Esposito did not file charges against Cognizant. He clarified that no formal accusations had been made. What he offered instead was a narrative: that visa fraud is "tied to cartels" and "transnational gangs," that it places unqualified workers in medical facilities, and that Department of Homeland Security assessments have found as many as 21 percent of H-1B petitions to be fraudulent.

That last number deserves scrutiny. It comes from a 2008 USCIS assessment that sampled a subset of petitions and found issues ranging from outright fabrication to technical paperwork deficiencies. Immigration scholars have long argued that conflating procedural errors with criminal fraud inflates the statistic beyond recognition. The government has not published a comparable study since.

## What the Practitioners Say

Kelly Fortier has handled H-1B cases at Michael Best for over 20 years. She told the Milwaukee Journal Sentinel that she has "personally not seen" the kind of fraud Vance described.

"I'm not surprised by the rhetoric, but I'm disappointed in it," Fortier said. "I don't think it accurately reflects what's actually going on in the H-1B program right now."

Doris Brosnan, an employment attorney at von Briesen & Roper with 27 years of Midwest practice, was more direct. "I myself have not encountered any companies abusing the H-1B program," she said. "I can't say that there isn't any fraud. Of course, there's fraud. But the question is, 'How widespread is it, and what's the way to correct it?'"

Both attorneys pointed out that the existing system already includes site visits by USCIS officers, prevailing wage requirements, and actual wage verification — mechanisms specifically designed to catch the kind of abuse the administration is describing.

"There are efforts in place and programs in place to catch this potential fraud," Fortier said. "It's not like it's just been ignored all these years."

## The Political Backdrop

Vance's Milwaukee event was not an accident of geography. Wisconsin is a purple state where immigration plays well as a campaign issue. Republican Congressman Tom Tiffany, who is considered the frontrunner for the state's gubernatorial race, has already introduced legislation to strip universities of their H-1B cap exemption.

"If Tom Tiffany runs for governor, this is going to be a key, key issue in that governor's race," Fortier observed. "I'm not surprised Vice President Vance has kind of set the stage for that."

This is not the first time a presidential administration has targeted the H-1B program. Both Democratic and Republican administrations have tightened regulations around prevailing wages and third-party placements. But the framing has shifted. Previous reforms addressed policy mechanics. This probe is wrapped in the language of national security, organized crime, and — unmistakably — anti-immigration politics.

## What This Means for Indian Professionals

The stakes are not abstract. Indians account for 73 percent of all H-1B visa holders, according to the Pew Research Center. Most hold master's degrees. The majority work in programming, data communications, and technical support at companies like Amazon, Google, Meta, Microsoft, and Apple.

When the Vice President of the United States stands at a podium and calls the program a vehicle for "foreign fraudsters" and "violent crime," every Indian H-1B holder absorbs that characterization — whether they work at a Fortune 500 company or a university research lab.

The investigation may well uncover genuine abuse. It may produce indictments. But the lawyers who spend their careers inside the H-1B system — filing the petitions, advising the employers, navigating the audits — are asking a question the administration has not yet answered.

Where is the evidence?"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Your Company Just Got Acquired. Your Visa May Not Survive the Deal",
        "subheadline": "Immigration compliance has become a deal-breaker in corporate M&A. For the hundreds of thousands of Indian professionals on H-1B and L-1 visas, a routine acquisition can quietly destroy their work authorization.",
        "slug": make_slug("ma-deal-immigration-h1b-visa-risk-corporate-acquisition"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B holders are concentrated in the tech and consulting sectors — exactly the industries with the highest M&A activity. An acquisition that looks like good news for the company can silently jeopardize an employee's right to work in the United States.",
        "tags": ["h1b", "corporate", "merger-acquisition", "visa-compliance", "immigration-enforcement", "l1-visa"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/legalindustry/why-immigration-is-new-front-line-ma-due-diligence-2026-07-08/"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/deals-get-tougher-immigration-status-scrutiny-from-lawyers"},
            {"name": "American Bar Association", "url": "https://businesslawtoday.org/2026/02/immigration-due-diligence-a-core-requirement-in-corporate-transactions/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7876001/pexels-photo-7876001.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Business professionals reviewing contract documents during a corporate transaction",
        "image_attribution": "Pexels",
        "body": """When Thermo Fisher Scientific closes its acquisition of Clario Holdings later this year, someone in the legal team will have spent weeks on a question that used to be an afterthought: what happens to the foreign workers?

That question, according to a Reuters analysis published this week, has moved from the footnotes to the front page of M&A due diligence. And for the hundreds of thousands of Indian professionals holding H-1B, L-1, and other work visas across corporate America, the answer is more precarious than most realize.

## The Problem Nobody Planned For

The Immigration and Nationality Act was not written with Silicon Valley acquisitions in mind. Every work visa — H-1B for specialty occupations, L-1 for intracompany transfers, TN for NAFTA professionals, O-1 for extraordinary ability — is employer-specific. Change the employer, and the legal scaffolding holding up a worker's right to be in the United States can collapse.

In a stock acquisition, the employing entity survives. The new owner steps into the predecessor's immigration shoes. Approved H-1B petitions, pending green card cases, and Labor Condition Applications carry over without refiling — provided employment terms stay the same. That condition is narrower than it sounds. A change to job duties, title, or work location triggers the requirement for a new USCIS petition and a new LCA before the employee can start at the new site.

Asset acquisitions are worse. The buyer selectively acquires assets and liabilities, but immigration obligations do not transfer by default. Every affected employee's petition, labor certification, and green card case may need to be refiled from scratch. Workers are at the mercy of USCIS processing times, which can stretch for months. In the interim, they cannot legally begin work with the new employer.

## The Visa Categories That Break First

L-1 intracompany transferees are the most exposed. L-1 eligibility depends on a qualifying corporate relationship between a US entity and a foreign affiliate, subsidiary, or parent. If an acquisition severs that relationship, L-1 eligibility is destroyed instantly. The employee must transition to another visa category before the deal closes or stop working.

E-1 and E-2 treaty visas carry a different trap. These visas require the enterprise to be at least 50 percent owned by nationals of the relevant treaty country. An acquisition by a company of a different nationality eliminates treaty visa eligibility for every affected worker in one stroke.

Even F-1 students on STEM OPT are not safe. The program requires the employer to be enrolled in E-Verify, to maintain a formal training plan, and to report material changes — including a new employer identification number — to the student's school. A routine asset purchase can trigger all three.

H-1B workers fare relatively better because of the "portability" provision, which allows them to begin working for a new employer the day a transfer petition is received by USCIS, without waiting for approval. But "relatively better" is a low bar when the immigration enforcement environment has fundamentally shifted.

## The Enforcement Squeeze

The current climate has made every gap in compliance potentially lethal. Reuters reports that USCIS has expanded site visits, ICE has increased I-9 audit activity, and the Department of Labor has launched its own investigation into H-1B and PERM visa practices. Bloomberg Law reports that immigration status has transformed from a checklist item into something that can delay or kill deals entirely.

"It definitely has the potential to kill a deal," Mary Kate Fernandez, a business immigration attorney at Adams & Reese, told Bloomberg Law. "Some buyers are aggressive and buying up companies without being acquainted with workforce realities."

The US labor force lost 750,000 foreign-born workers in the first half of 2026 alone, according to Deloitte data cited in the Bloomberg Law report. For acquirers in the IT and financial sectors — the two industries most dependent on H-1B sponsorship and among the top three dealmaking sectors globally this quarter — inherited workforce irregularities become the buyer's liability the moment the deal closes.

## What Indian Professionals Should Know

If your employer announces an acquisition, merger, or restructuring, the first question is not about your stock options. It is about the deal structure.

In a stock deal, your visa status likely survives — but confirm that your job duties, title, and work location are not changing. Any "material change" requires a new filing. In an asset deal, assume nothing transfers. Your employer's immigration counsel should be mapping every affected visa before the deal closes.

Post-pandemic remote work has added another layer. Immigration attorneys report that M&A due diligence routinely surfaces H-1B workers who have been working from home states not covered by their original LCAs. An amended filing should have been made for each one. If it was not, the new owner inherits that exposure.

The practical advice from Reuters is pointed: immigration counsel must be at the table before a deal structure is chosen, not after. For the 73 percent of H-1B holders who are Indian nationals, that advice carries an urgency the legal analysis understates. Your right to work in this country is only as durable as the corporate entity that sponsors it. When that entity changes hands, everything is on the table."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
