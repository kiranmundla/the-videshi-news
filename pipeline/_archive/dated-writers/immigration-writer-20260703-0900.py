#!/usr/bin/env python3
"""
Immigration Writer — July 3, 2026 09:00 PT
2 articles for The Videshi immigration section.
"""

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


# ============================================================
# ARTICLE 1: ICE Worksite Enforcement Surge
# ============================================================

art1_body = """Ten thousand people in five days. That is the pace Immigration and Customs Enforcement set in late June 2026, arresting roughly 2,000 individuals per day in a surge that pushed total ICE detention numbers to 39,000 — up from 30,000 in previous months. And if a CNN report is to be believed, the next phase will hit closer to home for anyone holding a work visa: the Trump administration is planning to dramatically expand worksite immigration enforcement.

The shift is significant. For much of the past year, the administration's enforcement apparatus focused on neighbourhood sweeps and high-profile city operations. Workplaces were largely spared, with Trump himself at times suggesting that farms and industries employing migrants should be protected. That ambiguity created whiplash within ICE, where agents received contradictory orders about whether to conduct workplace raids.

Now the direction appears settled. Homeland Security Secretary Markwayne Mullin declared at a New York press conference that the government is "deporting on average over 3,200 individuals a day" and "surging every day." The administration has hired thousands of additional agents, opened new detention centres, and secured $170 billion in funding through September 2029 — a massive increase over ICE's existing $19 billion annual budget.

## What worksite enforcement actually looks like

The new push will go beyond large-scale factory raids. According to officials familiar with the plans, DHS intends to expand "paperwork enforcement" — auditing employer records, issuing subpoenas, and imposing fines on businesses that hire workers without proper authorisation.

This is not entirely new territory. ICE's Homeland Security Investigations (HSI) directorate has already subpoenaed records from roughly 1,200 businesses and proposed close to $1 million in fines since January 2025. But the scale is about to increase. Mark Krikorian, executive director of the Center for Immigration Studies and a supporter of the crackdown, put it bluntly: "There's no way to do mass deportation and there's no way to encourage significant self-deportation without it."

Previous worksite operations have ranged from small raids — four arrests at a Pennsylvania business, 11 in Louisiana — to the September 2025 mega-operation at a Hyundai battery plant in Georgia, where 475 workers were detained in a single day, most of them South Korean nationals found to be in violation of visa terms.

## Why Indian professionals should be paying attention

The conventional assumption among H-1B holders has been that worksite enforcement targets undocumented workers, not visa holders in legal employment. That assumption is increasingly outdated.

ICE agents have already detained individuals with valid green cards and legal visas during neighbourhood sweeps. The Georgia battery plant raid demonstrated that visa-term violations — not just undocumented status — are squarely in the enforcement crosshairs. For the roughly 600,000 Indian nationals currently on H-1B visas, this raises uncomfortable questions.

An H-1B holder working at a client site different from the one listed on their petition. A worker whose job duties have evolved beyond the original Labour Condition Application. An employee whose employer has not updated USCIS about a material change in employment conditions. Any of these commonplace situations could, in a heightened enforcement environment, attract scrutiny.

The risk is compounded by the administration's pattern of using enforcement as leverage in broader policy debates. With the India-US trade deal in its final stages and H-1B visa fees a persistent irritant in bilateral relations, worksite operations targeting industries that employ large numbers of Indian workers could serve multiple policy objectives simultaneously.

## The employer side

Companies are also recalculating. The House Small Business Committee released a report warning that ICE raids are "gutting the workforce" and "threatening Main Street," citing exacerbated labour shortages in construction, agriculture, and logistics. For tech companies and consulting firms that sponsor H-1B workers, the calculus now includes the reputational and operational risk of an ICE audit.

Some firms are already responding by shifting work to India's booming Global Capability Centres. Others are tightening internal compliance. The practical advice for anyone on a work visa: ensure your petition details match your actual employment conditions, keep copies of all immigration documents at home (not just at the office), and know the difference between a legitimate audit request and an overreach.

The administration has signalled no intention of slowing down. "This is going to inconvenience some people," Krikorian acknowledged. For tens of thousands of Indian professionals, the inconvenience may be rather more than that."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "ICE Arrested 10,000 People in Five Days. Worksite Raids Are Next",
    "subheadline": "The Trump administration is planning to expand immigration enforcement directly into workplaces — auditing employers, issuing subpoenas, and raiding job sites. For H-1B holders, the threat is no longer abstract.",
    "slug": make_slug("ice-worksite-raids-enforcement-surge-indian-h1b"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "H-1B holders and their employers face increasing scrutiny as ICE shifts from neighbourhood sweeps to worksite enforcement, raising the risk for anyone whose petition details do not perfectly match their actual employment.",
    "tags": ["ice", "worksite-enforcement", "h1b", "deportation", "immigration-enforcement"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "CNN", "url": "https://www.cnn.com/2026/07/02/politics/worksite-immigration-enforcement-raids-trump"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/us/trump-set-expand-immigration-crackdown-2026-despite-brewing-backlash-2025-12-20/"},
        {"name": "ICE.gov", "url": "https://www.ice.gov/news/releases/ice-arrests-over-1k-illegal-workers-proposes-1m-fines"},
        {"name": "House Small Business Committee", "url": "https://democrats-smallbusiness.house.gov/news/documentsingle.aspx?DocumentID=404397"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/U.S._Immigration_and_Customs_Enforcement_%28ICE%29_Enforcement_and_Removal_Operations%27_%28ERO%29_officers_in_Chicago%2C_January_2025.jpg/1280px-U.S._Immigration_and_Customs_Enforcement_%28ICE%29_Enforcement_and_Removal_Operations%27_%28ERO%29_officers_in_Chicago%2C_January_2025.jpg",
    "image_caption": "ICE Enforcement and Removal Operations officers during an operation in Chicago, January 2025",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}


# ============================================================
# ARTICLE 2: India's GCC Boom — The H-1B Alternative
# ============================================================

art2_body = """For years, the pipeline ran in one direction: Indian engineers studied hard, landed a US job, filed for an H-1B visa, and waited — sometimes for decades — for a green card. In 2026, that pipeline is being rerouted. India's Global Capability Centres have hired 227,991 people in the first six months of the year alone, and full-year projections now exceed 510,000 — the first time annual GCC recruitment has crossed the five-lakh mark.

The numbers come from a foundit Insights Tracker report published July 1, and they tell a story that goes well beyond cost arbitrage. Nearly two in three new GCC roles created this year — 64 per cent — require AI, data science, or intelligent automation skills. This is not back-office support work. It is the same high-value engineering, product development, and machine learning work that once required an H-1B visa and a Bay Area address.

## The numbers behind the shift

India now hosts roughly 2,120 Global Capability Centres, up from about 1,600 in 2021 — a 3.4-fold increase in hiring over five years, with a compound annual growth rate of 27.4 per cent. Technology and software accounts for 35 per cent of GCC hiring, followed by banking and financial services at 21 per cent. Together, these two sectors represent more than half of all GCC recruitment.

The geography tells its own story. Bengaluru leads with 26 per cent of all GCC hiring, followed by Hyderabad (22 per cent), Pune (15 per cent), and Chennai (12 per cent). But Tier 2 cities are growing fastest, as companies discover that India's talent depth extends well beyond the traditional metros.

What is driving the acceleration? Three converging forces. First, the H-1B visa crackdown — the $100,000 fee, the weighted lottery, tighter scrutiny — has made it prohibitively expensive and risky for US companies to bring Indian engineers to America. Second, AI has raised the strategic value of the work being done in Indian GCCs from support functions to core innovation. Third, the sheer depth of India's engineering talent pool makes scaling possible in ways that no other country can match.

## Not your father's outsourcing

The GCC of 2026 bears almost no resemblance to the IT outsourcing centres of a decade ago. Merck recently opened a centre in Bengaluru's Electronic City housing 3,300 employees in AI, digital engineering, cloud, and cybersecurity. Neelkanth Mishra, member of the Economic Advisory Council to the Prime Minister and Executive Director-Designate at the World Bank, noted that GCC revenue now constitutes a "meaningful part" of India's IT industry contribution to GDP, with services exports growing 15 per cent in dollar terms in April alone.

"Companies are no longer setting up Global Capability Centres simply to reduce costs," said Tarun Sinha, CEO of foundit. "They are building them to develop the AI, engineering and product capabilities that run their global businesses."

The data backs this up. AI, data science, and analytics is the fastest-growing function within GCCs, expanding 38 per cent year-on-year. Four technology functions — IT and software development, AI and data science, engineering and product R&D, and cloud and cybersecurity — together account for more than three-quarters of all GCC roles.

## What this means for the diaspora

For Indians in America weighing their options, the GCC boom offers something that was largely unavailable five years ago: a realistic alternative. The talent profile is telling — professionals with four to ten years of experience account for 56 per cent of GCC hiring, precisely the cohort most likely to be stuck in the green card backlog or anxious about H-1B renewals.

The career opportunities are no longer a step down. A senior AI engineer at a GCC in Hyderabad or Bengaluru can work on the same products, with the same teams, and often at comparable purchasing-power-adjusted compensation — without spending a single day worrying about visa stamps, consulate appointments, or whether a change of employer will reset a decade-long immigration queue.

This does not mean the exodus is a stampede. Compensation in absolute dollar terms remains higher in the US, and many Indian professionals have built lives, mortgages, and school enrolments that cannot be unwound on a quarterly earnings cycle. But the calculation has shifted. When an EB-2 India green card queue stretches into the 2040s, and the H-1B programme is simultaneously more expensive, more restrictive, and subject to worksite raids, the GCC alternative starts looking less like a consolation prize and more like a rational choice.

The Indian government appears to recognise this. Multiple states, including Uttar Pradesh, have rolled out dedicated GCC attraction policies. TeamLease projections suggest India could host more than 2,400 GCCs by 2030, generating $110 billion in export revenue.

For American companies, the irony is sharp: the same visa restrictions designed to "protect American workers" are accelerating the transfer of their most strategic work to India. For Indian professionals, the irony is sharper still — the country they left to build careers may end up offering better career stability than the one they moved to."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Half a Million Tech Jobs and Counting. India's GCC Boom Is Rewriting the H-1B Calculus",
    "subheadline": "India's Global Capability Centres are projected to hire over 510,000 people in 2026, with nearly two-thirds of new roles in AI and data science. For diaspora professionals stuck in visa limbo, the alternative is no longer theoretical.",
    "slug": make_slug("india-gcc-boom-510000-ai-jobs-h1b-alternative"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "For Indian professionals in the US weighing precarious H-1B renewals and a green card backlog stretching into the 2040s, India's GCC boom offers realistic high-value tech careers without immigration anxiety.",
    "tags": ["gcc", "global-capability-centres", "h1b", "reverse-migration", "india-tech", "ai-jobs"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/2-in-3-new-gcc-jobs-are-now-ai-rolesfounditinsights-tracker/article71170570.ece"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-gcc-count-grow-2400-by-2030-impact-h1-b-crackdown-minimal-says-teamlease-2025-11-12/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/gccs-now-a-meaningful-part-of-indias-it-industry-revenue-neelkanth-mishra/article71172382.ece"},
        {"name": "YourStory", "url": "https://yourstory.com/2026/04/gcc-hiring-up-q2fy26-quality-quantity"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg",
    "image_caption": "Software developers collaborating in a modern technology office",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}


# ============================================================
# Insert articles
# ============================================================

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
