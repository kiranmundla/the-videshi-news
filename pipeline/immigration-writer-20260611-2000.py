#!/usr/bin/env python3
"""
Immigration article writer for The Videshi — June 11, 2026 evening batch.
Inserts 2 articles into Supabase with status: "review", is_editorial: false.
"""

import os
import json
import requests
from datetime import datetime, timezone

# Load Supabase env
with open(os.path.expanduser("~/.env.supabase")) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

now_iso = datetime.now(timezone.utc).isoformat()

articles = [
    {
        "headline": "The Bill That Would Kill the H-1B Lottery — and the Green Card Path With It",
        "subheadline": "Rep. Chip Roy's American White-Collar Worker Jobs Act proposes the most sweeping overhaul of the H-1B programme in its 36-year history, threatening to upend the immigration calculus for hundreds of thousands of Indian professionals.",
        "slug": "chip-roy-bill-end-h1b-lottery-green-card-20260611",
        "category": "immigration",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "score_total": 82,
        "published_at": now_iso,
        "image_url": "https://images.pexels.com/photos/20417783/pexels-photo-20417783.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The US Capitol, where Congress will debate a sweeping H-1B overhaul bill",
        "image_attribution": "Photo by Ivan Dražić on Pexels",
        "diaspora_angle": "Indian professionals hold 73% of all H-1B visas — this bill would dismantle the lottery, end OPT for F-1 students, and sever the H-1B-to-green-card pathway that has been the backbone of NRI career planning for decades.",
        "sources": json.dumps([
            {
                "name": "Travel And Tour World",
                "url": "https://www.travelandtourworld.com/news/article/unfvlf3u9z00/",
                "date": "2026-06-09"
            },
            {
                "name": "Reuters",
                "url": "https://www.reuters.com/world/us/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/",
                "date": "2026-06-09"
            },
            {
                "name": "Fox News",
                "url": "https://www.foxnews.com/politics/federal-judge-strikes-down-trumps-100k-h-1b-visa-fee-ruling-unconstitutional-tax",
                "date": "2026-06-09"
            }
        ]),
        "body": """On June 5, Representative Chip Roy of Texas introduced legislation that, if enacted, would amount to the most radical restructuring of America's H-1B visa programme since its creation in 1990. The American White-Collar Worker Jobs Act of 2026 does not merely tinker with fee schedules or tweak selection criteria. It proposes to abolish the annual H-1B lottery outright, eliminate the Optional Practical Training programme that allows international students to work after graduation, and — most consequentially for Indian professionals — sever the long-standing pathway from H-1B status to a green card.

The timing is deliberate. The bill lands in a Congress already consumed by immigration battles, just days after a federal judge struck down the Trump administration's $100,000 H-1B fee as an unconstitutional tax. It arrives as the first wage-weighted H-1B lottery — finalised by the Department of Homeland Security in December 2025 — has already reshaped the FY 2027 selection cycle. And it drops into an environment where Indian tech workers, who hold roughly 73 per cent of all H-1B visas according to Pew Research Centre data, are watching each policy shift with acute personal stakes.

## What the bill would do

The legislation's centrepiece is the replacement of the randomised lottery with a merit-and-wage-based selection framework. Under the current system, USCIS receives far more petitions than the 85,000 annual cap allows — 65,000 general visas plus 20,000 for holders of advanced US degrees — and picks winners essentially at random. Roy's bill would instead rank applicants by offered salary and skill level, favouring those at the top of the wage distribution.

But the bill goes further than selection reform. It would mandate that employers demonstrate credible efforts to recruit American workers before filing an H-1B petition — a strengthened version of existing labour condition attestation requirements that critics say have long been toothless. Companies that have conducted recent layoffs would be barred from seeking H-1B visas entirely, a provision aimed squarely at the tech industry practice of replacing domestic staff with lower-cost visa holders.

The OPT programme, which allows F-1 international students to work in the US for up to three years after graduation in STEM fields, would be eliminated. For the roughly 200,000 students currently on OPT — many of them Indian — this would close the primary bridge between a student visa and an H-1B petition.

Most dramatically, the bill would phase out the use of H-1B status as a stepping stone to permanent residency. For decades, the typical trajectory for an Indian tech professional has been F-1 student visa, OPT work authorisation, H-1B sponsorship, and eventually an employer-sponsored green card. Roy's bill would break that chain at its final link.

## The broader legislative landscape

The bill does not exist in isolation. Congress is simultaneously debating the PROTECT Act, which would codify the $100,000 H-1B fee that Judge Leo Sorokin of the US District Court in Massachusetts struck down on June 8. Representative Mike Kennedy has introduced his own bill seeking to bypass the ruling through legislation. At least four other bills targeting the H-1B programme in various ways are circulating in the House.

Meanwhile, the DHS wage-weighted selection rule is already operational. Under that rule, finalised last December, wages are sorted into four levels using federal occupational data, and applicants in higher wage brackets receive multiple entries into the lottery — effectively weighting the system toward senior, better-compensated positions. The first selections under this framework were issued in spring 2026.

"For its nearly forty-year history, the H-1B visa has been abused," Roy said upon introducing the bill, framing the reforms as essential worker protection. Opponents counter that the programme generates $86 billion in annual economic output and $35 billion in federal and payroll taxes, according to figures cited by the Arizona Attorney General's office in its successful challenge to the $100,000 fee.

## What this means for the diaspora

For Indian professionals in the US, the bill represents a potential existential threat to the immigration model that has sustained a generation of NRI career trajectories. The H-1B-to-green-card pipeline is not merely a bureaucratic convenience — it is the organising principle around which hundreds of thousands of families have structured years of professional decisions, financial commitments, and personal sacrifices.

The elimination of OPT would hit prospective students hardest. Indian students represent the second-largest international student population in the US, and many factor post-graduation work eligibility into their decision to study in America. Without OPT, the cost-benefit analysis of a US education shifts significantly — particularly for families taking on ₹50-75 lakh in education loans.

Industry reaction has been predictably divided along familiar lines. Tech companies that depend heavily on H-1B talent — Amazon received 19,301 approvals between 2024 and mid-2025, Microsoft 9,914, and Apple 8,075 — have pushed back against further restrictions. Immigration advocacy groups warn that the bill could drive global talent to Canada, the UK, and Australia, which have been actively courting skilled Indian professionals.

## What comes next

The bill must clear committee review, potential amendments, and approval by both houses of Congress before becoming law — a process that typically grinds slowly, if it moves at all. Single-sponsor bills with this degree of ambition frequently die in committee. But the political momentum behind H-1B reform is stronger than at any point in the programme's history, and even bills that fail outright can shape the regulatory landscape by establishing policy markers.

For now, the practical impact on Indian professionals is atmospheric rather than immediate. No visas are being revoked; no OPT authorisations are being cancelled. But the direction of travel is unmistakable, and the diaspora would be wise to plan accordingly. The era of assuming a stable, decades-long American career trajectory may be drawing to a close — not through a single dramatic act, but through the steady accumulation of legislative and regulatory pressure that makes the path narrower with each passing session of Congress.""",
    },
    {
        "headline": "The Great Prepayment: Why Indian Students in America Are Racing to Clear Their Education Loans",
        "subheadline": "Amid tightening visa rules and a volatile US job market, a growing number of Indian borrowers are fast-tracking loan repayments — a quiet signal that the diaspora's long-term bet on America is being hedged.",
        "slug": "indian-students-education-loan-prepayment-us-20260611",
        "category": "immigration",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "score_total": 76,
        "published_at": now_iso,
        "image_url": "https://images.pexels.com/photos/35487174/pexels-photo-35487174.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Graduates celebrating — but many Indian students now prioritise clearing debt over long-term US plans",
        "image_attribution": "Photo by Saad Bin Hasan on Pexels",
        "diaspora_angle": "Indian students — the second-largest international student group in the US — are abandoning the traditional plan of settling in America long-term. Instead, they're aggressively paying off ₹50-75 lakh education loans to stay financially flexible if forced to return to India.",
        "sources": json.dumps([
            {
                "name": "The Hindu Business Line",
                "url": "https://www.thehindubusinessline.com/news/education/indian-students-in-us-fast-track-education-loan-repayments-amid-visa-job-worries/article71083348.ece",
                "date": "2026-06-10"
            },
            {
                "name": "Travel And Tour World",
                "url": "https://www.travelandtourworld.com/news/article/unfvlf3u9z00/",
                "date": "2026-06-09"
            },
            {
                "name": "Reuters",
                "url": "https://www.reuters.com/world/us/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/",
                "date": "2026-06-09"
            }
        ]),
        "body": """The numbers tell one story. The behaviour tells another. Gross non-performing assets in India's education loan portfolio stand at a relatively modest 2 per cent, according to the Ministry of Finance — a figure that suggests borrowers are keeping up with their obligations. But behind that reassuring statistic lies a more revealing trend: Indian students who took on hefty loans to study in the United States are not merely keeping up. They are paying ahead, aggressively and anxiously, in a race to clear their debts before circumstances force them home.

According to bankers at State Bank of India, India's largest lender, a growing number of education loan borrowers have accelerated their repayments over the past year, opting for higher monthly instalments and making lump-sum payments well before they are due. The typical repayment timeline for an Indian student who secures a US job after graduation is five to six years. That window is compressing.

"Most education loans come with a moratorium period of 12 to 18 months after completion of studies," a senior SBI official told The Hindu Business Line. "Of late, we have been witnessing early repayments through higher instalments as well as bulk payments, which is a welcome trend from the portfolio quality perspective."

What the banks call a welcome trend, the borrowers call survival planning.

## The arithmetic of anxiety

Consider the maths that keeps Indian graduates awake at night. A ₹50 lakh education loan — roughly $59,000 at current exchange rates, and a common figure for a two-year master's programme at a mid-tier US university — can swell to ₹75 lakh over three years of standard repayment once interest compounds. On a US tech salary, that is manageable. On an Indian tech salary, it can be crippling.

"It will be very difficult to repay my education loan if I suddenly have to return to India, as compensation packages back home may not allow me to set aside enough funds for quick repayment," one technology professional, who joined a US company six months after completing his post-graduation, told The Hindu Business Line. His immediate goal, he said, is to clear the loan entirely and remain "prepared" to return to India if circumstances warrant.

The wage gap explains the urgency. An entry-level software engineer in the US earns roughly $90,000-120,000 annually. The same profile in Bengaluru or Hyderabad commands ₹12-18 lakh — between $14,000 and $21,000. A loan that represents six months of American earnings becomes three to four years of Indian ones. The prepayment impulse is not financial prudence. It is insurance against a scenario that, until recently, most Indian students considered unthinkable.

## A generation recalibrating

The shift in repayment behaviour is the financial expression of a deeper psychological recalibration. For two decades, the standard NRI career arc was understood to be essentially one-directional: study in the US, secure OPT work authorisation, land an H-1B visa, file for a green card, settle permanently. Each stage was difficult and uncertain, but the overall trajectory was assumed to be forward.

That assumption is eroding. "Unlike earlier, I no longer think it is practical to plan for a long-term or permanent stay in the US," a woman software engineer who recently began working in America told The Hindu Business Line. "Many of us want to work here, repay our loans as quickly as possible and eventually return to India for work."

The policy environment validates her caution. In the past year alone, the Trump administration has imposed a $100,000 H-1B fee (struck down by a federal judge on June 8), implemented wage-weighted visa selection that disadvantages mid-career applicants, enhanced social media vetting for student visa holders, revoked SEVP certification for multiple universities, and deported international students for minor compliance issues. Congress is debating bills that would eliminate the H-1B lottery, end Optional Practical Training, and sever the visa-to-green-card pathway entirely.

## Parents step in

Perhaps the most telling indicator is the behaviour of parents. According to a Punjab National Bank official, some Indian families have begun servicing education loans even before their children secure employment — a departure from the traditional pattern where the moratorium period provided breathing room.

The logic is straightforward but bleak. If the student cannot find a job in the US, or finds one and then loses it during a downturn, or faces a visa complication that forces a return, every month of accrued interest becomes a burden that falls on the family. Better to start paying immediately, absorb the cost while the student is job-hunting, and reduce the overall interest exposure.

This parental intervention reflects a broader shift in how Indian families evaluate the American education investment. A decade ago, a US master's degree was treated as an asset with near-guaranteed returns — the high salary would eventually cover the loan, and the green card would provide the stability to build a career. Today, families are increasingly treating it as a high-risk, high-reward gamble that needs to be de-risked as quickly as possible.

## The macro picture

India is the second-largest source of international students in the US, behind China, with over 330,000 students enrolled in American institutions. Education loans disbursed to students heading abroad have grown rapidly — SBI alone processed over ₹30,000 crore in such loans by FY2025.

The banking system's relatively low NPA rate in education loans is, paradoxically, partly a product of the anxiety driving prepayments. Students are not defaulting because they are paying faster, not because the underlying risk has diminished. If the policy environment deteriorates further and a significant number of Indian graduates are forced to return before clearing their loans, the stress on bank portfolios could materialise quickly.

For now, though, the banks are content with the trend and the students are coping as best they can. The great prepayment is not a crisis. It is something quieter and more unsettling — a generation of Indian professionals recalculating the expected value of an American career in real time, and voting with their EMI payments.""",
    },
]

# Insert articles
for article in articles:
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        if isinstance(data, list) and data:
            row = data[0]
            print(f"✅ Inserted: '{row.get('headline', article['headline'])}' (id={row.get('id', 'N/A')}, slug={row.get('slug', article['slug'])})")
        else:
            print(f"✅ Inserted: '{article['headline']}' — response: {resp.text[:200]}")
    else:
        print(f"❌ FAILED: '{article['headline']}' — {resp.status_code}: {resp.text[:300]}")

print(f"\nDone. {len(articles)} articles submitted with status='review', is_editorial=false.")
