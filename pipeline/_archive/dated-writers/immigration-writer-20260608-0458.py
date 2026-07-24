#!/usr/bin/env python3
"""Immigration writer — 2026-06-08 batch"""

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
        "headline": "Go Home to Apply — The Rule That Could Force 118,000 Indian Green Card Seekers Out of America",
        "subheadline": "A new USCIS memo guts adjustment of status, the pathway 69 per cent of employment-based immigrants have used to become permanent residents without leaving the country. For Indians stuck in decade-long backlogs, leaving may mean never coming back.",
        "slug": make_slug("uscis-adjustment-status-ban-consular-processing-india-green-card"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals dominate the employment-based green card queue and face the longest backlogs in the system — often 10 to 30 years for EB-2 and EB-3. Forcing them to leave the US for consular processing means abandoning jobs, pulling children from schools, and gambling that a consulate in India will process their case before their employer moves on. For the roughly 862,000 Indians in the green card queue, adjustment of status was never a shortcut — it was the only way to maintain a life while waiting.",
        "tags": ["green-card", "adjustment-of-status", "uscis", "consular-processing", "immigration-policy", "h1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "NBC Palm Springs", "url": "https://www.nbcpalmsprings.com/2026/05/22/trump-administration-orders-green-card-applicants-to-leave-us"},
            {"name": "Pew Research Center", "url": "https://www.pewresearch.org/short-reads/2026/06/06/majority-of-new-green-cards-go-to-immigrants-already-living-in-us/"},
            {"name": "AInvest", "url": "https://www.ainvest.com/news/us-green-card-policy-softened-amid-business-lobbying/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy/green-card-process-changes-in-us-heres-what-it-means-for-indian-applicants"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/chair-meng-condemns-reckless-green-card-policy-change/"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/49/2023_green_card_front.jpg",
        "image_caption": "A US permanent resident card, commonly known as a green card",
        "image_attribution": "Wikimedia Commons",
        "body": """For decades, the deal was simple enough. You arrived in America on a work visa, filed your green card paperwork, and waited — sometimes for years, sometimes for decades — while continuing to live, work, and raise a family in the country you hoped would eventually call you a permanent resident. The mechanism that made this possible has a bureaucratic name: adjustment of status.

Now Washington wants to kill it.

## The memo that changed everything

The Trump administration issued a sweeping USCIS memo that will require most green card applicants to leave the United States and apply for permanent residency through consular processing in their home countries. The policy reverses a practice that has been the default pathway for employment-based immigrants since the Immigration and Nationality Act gave them the option.

USCIS spokesperson Zach Kahler framed the change as an administrative efficiency measure, arguing that requiring applicants to process from abroad "reduces the operational burden of tracking and removing those who choose to remain in the U.S. illegally after their applications are denied." The memo contains exemptions for "extraordinary circumstances," though the agency has not defined what qualifies.

The numbers tell a starker story. According to a new Pew Research Center analysis of Department of Homeland Security data, 69 per cent of all employment-based green cards issued in fiscal year 2024 — roughly 118,480 out of 170,980 — went to people already living in the United States through adjustment of status. Across all green card categories, 58 per cent of the 1.36 million permanent residency grants that year were processed domestically.

## What this means for the Indian queue

Indian nationals are not just affected by this policy — they are its primary casualties. The EB-2 and EB-3 backlogs for India stretch beyond a decade, with some estimates placing the theoretical wait at over a century for new applicants. The roughly 862,000 Indians currently in the employment-based green card queue have built entire lives around the assumption that adjustment of status would let them remain in America while their cases crawled forward.

Under the new rule, an Indian H-1B holder whose priority date finally becomes current would need to fly to India, attend a consular interview — likely in Chennai, Hyderabad, Mumbai, or New Delhi — and wait for processing before returning. Consulate appointment backlogs in India already stretch months, worsened by expanded social-media vetting that slashed daily interview capacity by as much as 40 per cent earlier this year.

The practical consequences cascade. Leaving the US means leaving a job. Most employers cannot hold a position open for the months a consular appointment might take. Children in American schools face mid-year disruptions. Spouses on H-4 visas with their own EADs lose work authorisation the moment they depart. For families that have spent a decade building stability in America, the memo does not merely change a process — it threatens to unravel everything.

## The corporate pushback

Business leaders moved fast. The US Chamber of Commerce and major technology companies pressed the administration for clarification, warning that the policy would gut their ability to retain talent in fields where skilled workers are already scarce. The lobbying appears to have had some effect: USCIS officials subsequently told business leaders that adjudicators would apply the policy "with nuance," weighing economic contributions and family circumstances before compelling applicants to leave.

But no formal guidance has been issued. The gap between a verbal reassurance to corporate lobbyists and a written policy that field officers must follow is vast — and it is exactly the kind of gap that swallows immigration cases.

Representative Grace Meng, chair of the Congressional Asian Pacific American Caucus, called the policy "reckless" and warned it would "rip apart families, spouses, and children from their parents." David Bier of the Cato Institute argued the rule would "damage American competitiveness by driving top global talent, including researchers and engineers, to foreign competitors."

## The quiet calculation

For Indian professionals weighing their options, the math has shifted. The adjustment-of-status pathway was never fast — but it was stable. You could work, pay taxes, buy a home, and raise American-born children while waiting for a bureaucracy to catch up. Consular processing introduces a variable that no amount of planning can control: the possibility that leaving America means not coming back on schedule, or at all.

Some will gamble on the "extraordinary circumstances" exemption. Others will accelerate plans to file under EB-1A or National Interest Waiver categories that may receive different treatment. A growing number, quietly, are looking at Canada's Express Entry system or the United Kingdom's High Potential Individual visa as insurance policies.

The administration says it is returning to "the original intent of the law." For the hundreds of thousands of legal immigrants who followed every rule and waited every year, the original intent now looks like a trapdoor."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Washington Says H-1B Policy Does Not Target India — the Data Suggests Otherwise",
        "subheadline": "A senior US official insists the visa system applies equally to all countries. But with Indians holding 72 per cent of H-1B visas and every recent reform landing hardest on that population, the question is whether neutral rules can produce discriminatory outcomes.",
        "slug": make_slug("us-rejects-h1b-discrimination-india-data-gap"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian tech professionals are the overwhelming majority of H-1B holders. When the US government says its policies don't target any country, that may be technically true — but every major H-1B reform in 2025-2026, from wage-weighted lotteries to the $1 million fee to country caps and social media vetting, disproportionately affects Indians. For a community that built careers around the H-1B pathway, the distinction between intent and impact is increasingly academic.",
        "tags": ["h1b", "discrimination", "india", "uscis", "immigration-policy", "country-cap"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The420.in", "url": "https://the420.in/us-rejects-discrimination-claims-over-h-1b-visa-policy/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy/us-bill-eyes-major-h1b-overhaul-seeks-to-end-green-card-track"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/world/us-lawmaker-proposes-major-h-1b-visa-overhaul-and-end-to-green-card-pathway/article69649000.ece"},
            {"name": "Nagaland Post", "url": "https://www.nagalandpost.com/index.php/us-lawmaker-introduces-bill-seeking-major-h-1b-overhaul/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/USCIS_HQ_Groundbreaking_Ceremony_%2838096348641%29.jpg/1280px-USCIS_HQ_Groundbreaking_Ceremony_%2838096348641%29.jpg",
        "image_caption": "USCIS headquarters groundbreaking ceremony in Washington, DC",
        "image_attribution": "Wikimedia Commons",
        "body": """A senior US official delivered a message last week that was clearly intended to be reassuring: the H-1B visa programme is not designed to target any specific country, and there is no preferential treatment or restriction based on nationality, race, or region. The allocation process, the official stressed, is "entirely based on eligibility, skills, and predefined qualification standards."

The statement came as tensions over US immigration policy continue to simmer, particularly among Indian professionals who make up the majority of H-1B holders and have watched a cascade of policy changes reshape the programme they depend on. The question the official's words raise is not whether US visa rules are facially neutral — they are — but whether a system can avoid discriminatory outcomes when one nationality dominates the applicant pool.

## The numbers that complicate the narrative

Indians received approximately 72 per cent of all H-1B visas issued in recent years, according to USCIS data. This concentration is not accidental — it reflects decades of recruitment by US technology companies, consulting firms, and research institutions that have drawn heavily from India's engineering talent pipeline.

But that concentration also means every H-1B reform, no matter how neutrally worded, lands with outsized force on Indian applicants. Consider the recent record:

The **wage-weighted lottery** introduced for fiscal year 2026 replaced the random selection system with one that prioritises higher-earning applicants. Indian IT services companies — Infosys, TCS, Wipro, Cognizant — tend to petition for workers at lower wage levels than, say, a Google or a Meta. The effect: Indian-dominated outsourcing firms saw their selection rates plummet relative to companies that hire fewer Indians at higher salaries.

The **$1 million petition fee** proposed as part of the administration's immigration crackdown would be devastating for companies that file hundreds or thousands of H-1B petitions annually. Those companies are overwhelmingly Indian IT firms. A boutique Swiss engineering consultancy filing three H-1B petitions barely notices. Infosys, filing thousands, faces an existential cost structure.

Congressman Chip Roy's **American White-Collar Worker Jobs Act**, introduced on June 4, proposes a 7 per cent per-country cap on H-1B allocations. Applied to the current applicant pool, this would reduce Indian H-1B issuances by roughly 90 per cent — from the dominant share to a sliver. The bill's sponsors frame it as ensuring geographic diversity. For Indian applicants, it reads as a targeted exclusion dressed in neutral language.

## The social media vetting effect

The expanded social-media vetting requirement, which took effect in December 2025, requires consular officers to review applicants' online presence before issuing visas. India's US consulates — in Hyderabad, Chennai, Mumbai, and New Delhi — process the highest volume of H-1B interviews globally. The additional time per case has cut daily interview capacity by up to 40 per cent at some posts, creating backlogs that pushed appointments from December 2025 into mid-2026.

Countries with lower H-1B application volumes — a Singapore, a United Kingdom, a Germany — absorbed the same policy with minimal disruption. The rule does not mention India. It does not need to.

## Disparate impact, familiar territory

American law distinguishes between disparate treatment (intentionally targeting a group) and disparate impact (neutral rules that disproportionately burden one group). The US official's statement addresses the first category: no one is writing "India" into the exclusion criteria. The second category is where the tension lives.

Immigration law, unlike employment law, does not have a robust disparate-impact framework. There is no statutory requirement for USCIS to assess whether a facially neutral policy falls disproportionately on one nationality. The result is a regulatory environment where every reform can be defended on process grounds while its demographic consequences go unexamined.

For the roughly 300,000 Indian nationals who filed H-1B registrations in the most recent cycle, the official's assurance that the system "is not designed to target any specific country" is technically accurate and practically beside the point. A system that draws 72 per cent of its applicants from one country and then imposes restrictions that hit volume filers, lower-wage petitions, and high-traffic consulates is, in effect, an India policy — whatever the stated intent.

## What Indian professionals are hearing

In immigration law forums, WhatsApp groups, and LinkedIn threads frequented by Indian H-1B holders, the official's statement landed with a familiar thud. The community has heard variations of this message for years: the rules are universal, the process is fair, the system does not see nationality.

What they see instead is a programme that was built on their labour, shaped by their applications, and is now being restructured in ways that consistently make their path harder. The debate over whether this constitutes discrimination depends entirely on whether you measure intent or outcome — and for someone whose visa appointment just got pushed to 2027, the distinction feels academic."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
