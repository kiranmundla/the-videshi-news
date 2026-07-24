#!/usr/bin/env python3
"""Immigration writer — 2026-07-11 19:00 PT run. Two articles."""

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
    return slug[:70].rstrip('-') + "-20260711"


# ═══════════════════════════════════════════════════════
# ARTICLE 1: Fed Task Force — Indian-Origin Economists
# ═══════════════════════════════════════════════════════

article1_body = """The Federal Reserve just announced who will run the five task forces charged with rethinking how America's central bank operates. Three of those panels will be led or co-led by figures of Indian origin — a concentration of diaspora talent at the apex of US monetary policymaking that would have been unimaginable a generation ago.

The task forces, created by new Fed Chairman Kevin Warsh, are meant to produce findings by year's end on everything from how the Fed manages its $7 trillion balance sheet to how artificial intelligence will reshape employment. Warsh announced the appointments on July 10, calling them "the best minds from a range of disciplines."

## Rajan on the Balance Sheet

Raghuram Rajan, the former governor of the Reserve Bank of India and one-time chief economist of the International Monetary Fund, will co-lead the balance sheet policy task force alongside Harvard's Karen Dynan and former Fed Governor Jeremy Stein.

Rajan's credentials are hard to overstate. He famously warned about the risks of financial deregulation at the 2005 Jackson Hole symposium — three years before the global financial crisis proved him right. His appointment to review Fed balance sheet policy carries particular weight: in 2022, he co-authored a paper for the Kansas City Fed's Jackson Hole conference arguing that shrinking the Fed's bloated balance sheet was an "uphill task."

For the Indian diaspora, Rajan's role is more than symbolic. A former central banker from India is now helping decide how the world's most powerful central bank manages its assets — a seat that directly influences global interest rates, dollar liquidity, and the financial plumbing that Indian-born professionals navigate every time they wire money home, service a mortgage, or hedge against rupee fluctuations.

## Chetty on Data

Raj Chetty, the Harvard economist whose work on economic mobility has reshaped how America understands inequality, will co-lead the data task force. Born in New Delhi and raised in the US, Chetty is a pioneer in using real-time, alternative data to track how households and neighbourhoods are faring — precisely the kind of insight central banks have struggled to incorporate into their models.

His Opportunity Insights project has mapped the American Dream (and its failures) with a granularity no government survey ever achieved. At the Fed, his task force will examine whether the central bank's analytical tools — many designed decades ago — are equipped for an economy increasingly shaped by gig work, immigration flows, and AI displacement.

## Sharma and the Controversy

The third Indian-origin appointment is the most politically charged. Asha Sharma, the Xbox CEO and Microsoft executive vice president, will co-lead the productivity and jobs task force alongside venture capitalist Marc Andreessen and Stanford economist Charles Jones.

Sharma's appointment landed just as she was at the centre of a firestorm. On July 6, she announced 3,200 layoffs at Xbox — roughly a fifth of the division's workforce — while Microsoft had been approved earlier this year for 2,273 H-1B visa hires. The juxtaposition drew furious commentary online, some of it explicitly targeting her Indian heritage, despite the fact that Sharma was born in Wisconsin.

Her place on a Federal Reserve task force examining "productivity and jobs" while overseeing one of the year's largest mass layoffs struck critics as tone-deaf. "It's like asking El Chapo to lead the DEA," one commenter wrote on X.

Microsoft pushed back, noting that the layoff decisions were "based on business need, not visa status" and that H-1B employees were also affected.

## What It Means for the Diaspora

The broader picture is harder to dismiss with a punchline. An Indian-origin economist who ran the RBI is reviewing how the Fed manages its balance sheet. Another is redesigning how the Fed measures economic reality. A third — however controversial — is advising on how AI will reshape the American labour market.

The review is set to conclude by year's end. Its findings will shape how the Fed communicates policy, manages trillions in assets, and thinks about employment in an AI-transformed economy. For the roughly 5.4 million Indian Americans in the US — many of them navigating the very immigration and employment systems these policies affect — the composition of these panels is not academic. It is, in a very direct sense, representation at the table where the rules are written."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Three Indian-Origin Minds Will Shape How the Federal Reserve Thinks About the Economy",
    "subheadline": "Former RBI Governor Raghuram Rajan, Harvard economist Raj Chetty, and Xbox CEO Asha Sharma will co-lead three of the Fed's five policy review task forces — a remarkable concentration of diaspora talent at the apex of US monetary power.",
    "slug": make_slug("rajan-chetty-sharma-fed-task-force-indian-origin"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Three Indian-origin figures will co-lead panels reviewing how the US Federal Reserve operates, from balance sheet policy to AI's impact on jobs — direct representation at the table where economic rules affecting millions of Indian Americans are written.",
    "tags": ["federal-reserve", "raghuram-rajan", "raj-chetty", "asha-sharma", "nri-achievement", "monetary-policy", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/finance/feds-warsh-taps-broad-group-central-bank-outsiders-oversee-review-2026-07-10/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/federal-reserve-launches-policy-review-panels-with-marc-andreessen-and-raghuram-rajan/article69790123.ece"},
        {"name": "Fox News", "url": "https://www.foxnews.com/politics/ceo-under-fire-mass-layoffs-amid-foreign-worker-hiring-spree-now-appointed-feds-task-force-jobs"},
        {"name": "Inshorts", "url": "https://inshorts.com/en/news/raghuram-rajan--xbox-s-asha-sharma-roped-in-to-review-policies-of-us-fed-1783666274063"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/d5/Raghuram_Rajan%2C_IMF_69MS040421048l.jpg",
    "image_caption": "Raghuram Rajan, former RBI Governor and IMF Chief Economist, at an IMF event",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}


# ═══════════════════════════════════════════════════════
# ARTICLE 2: NIW / EB-1A Approval Rates Plunging
# ═══════════════════════════════════════════════════════

article2_body = """Indian professionals have been filing EB-1A and EB-2 National Interest Waiver petitions at record rates, treating them as an escape route from the employer-dependent H-1B system. The latest USCIS data suggests the exit door is getting narrower.

Adjudication numbers through the fourth quarter of fiscal year 2025, compiled by Greenberg Traurig and analysed by the immigration data firm Boundless, show approval rates falling sharply across both self-petition categories — precisely the ones that Indian professionals have been flocking to as H-1B restrictions tighten.

## The Numbers

The EB-2 NIW category — which lets applicants bypass the labour certification process by arguing their work serves the national interest — has seen approval rates collapse from a pandemic-era peak of roughly 96 per cent in FY2022 to just 55.2 per cent for full-year FY2025. The fourth quarter alone dropped to 35.7 per cent. Barely one in three petitions cleared the bar in the most recent quarter on record.

EB-1A, the "extraordinary ability" category that allows self-petitioning without any employer sponsorship, has held up better but still declined — from the low-to-mid 70s in prior years to 66.9 per cent for FY2025 overall, with the fourth quarter at roughly 53 per cent.

The O-1 nonimmigrant visa for extraordinary ability, by contrast, remains above 90 per cent. That distinction matters: the O-1 is a temporary work visa, not a path to permanent residence. Indians who need a green card cannot substitute one for the other.

## Why Approvals Are Falling

In NIW cases, USCIS is applying the *Matter of Dhanasar* framework — the three-part test that governs national interest waivers — with noticeably more rigour. Adjudicators are placing greater weight on measurable, demonstrated impact on the United States, rather than forward-looking promises or broad claims about working in an important sector.

Healthcare, core STEM, and national-security-adjacent fields continue to perform well. But cases in technology, consulting, and general business — exactly where many Indian professionals work — are facing stiffer headwinds. The agency appears to be looking for contributions that demonstrably extend beyond a single employer, backed by concrete evidence rather than recommendation letters with generic praise.

For EB-1A, the issue is the two-step "final merits" analysis. Meeting three of the ten criteria — the threshold for initial consideration — is no longer enough. Adjudicators are treating the three-criteria bar as a starting gate, not a finish line, and then asking whether the evidence demonstrates sustained national or international acclaim at the top of the field.

## A Court Challenge

That approach is now being tested in court. In *Mukherji v. Miller*, decided in January 2026 in the District of Nebraska, a federal judge questioned whether USCIS had properly adopted the two-step framework and ordered a petition approved after the agency conceded the petitioner met five of the ten criteria.

The ruling is narrow — it applies only to that case, and USCIS has not changed its guidance. But immigration attorneys say it provides a useful precedent for applicants who receive vague or conclusory denials on strong records. The petitioner's name suggests Indian origin, and the case has circulated widely in Indian professional immigration communities.

## The Collision Course

The timing creates an uncomfortable dynamic. Indian professionals have been surging into self-petition categories — EB-1A filings rose more than 50 per cent in Q1 2025 alone, according to CXOToday — driven by the Trump administration's $100,000 H-1B fee proposal, tighter third-party placement rules, and a general sense that employer-dependent immigration is becoming untenable.

But they are filing into a system that is simultaneously raising the bar. The result is a growing gap between effort and outcome: more applications, more legal fees, more documentation — and a lower probability of success.

## What It Means — and What to Do

Immigration attorneys are advising a dual-filing strategy. Applicants who may qualify for both EB-1A and NIW should consider filing both concurrently, creating multiple shots at approval while preserving priority dates. Filing an NIW first can also secure an approved I-140 petition, which allows indefinite H-1B extensions beyond the normal six-year limit under the AC21 Act — a critical lifeline for Indian nationals stuck in decades-long green card backlogs.

The practical takeaway is blunt: self-petition is still viable, but the bar has moved. Generic cases with broad claims and form-letter recommendations are being rejected at rates that would have seemed extraordinary two years ago. What gets approved now is specificity — narrow endeavours, independent evidence, verifiable metrics, and a clear articulation of why the work benefits the United States.

For the hundreds of thousands of Indian professionals weighing their immigration options in a system that seems to offer fewer stable paths by the month, the data is a reality check. The escape route exists. It just demands more to use it than it did a year ago."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "The Self-Petition Escape Route Is Narrowing. USCIS Approval Rates Tell the Story",
    "subheadline": "EB-2 NIW approvals have fallen from 96 per cent to 35 per cent in three years. EB-1A is dropping too. Indian professionals are filing at record rates into a system that is simultaneously raising the bar.",
    "slug": make_slug("eb1a-niw-approval-rates-falling-indian-self-petition"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian professionals have been surging into self-petition green card categories as an escape from the H-1B system, but USCIS approval rates are plunging — creating a collision between record filings and a tightening adjudication environment.",
    "tags": ["eb-1a", "niw", "green-card", "uscis", "self-petition", "h1b-alternative", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Greenberg Traurig / Mondaq", "url": "https://www.mondaq.com/unitedstates/work-visas/1801714/what-recent-uscis-data-means-for-eb-2-niw-eb-1a-petitioners"},
        {"name": "Boundless", "url": "https://www.boundless.com/research/uscis-q3-2025-data-shows-eb-1a-filings-remain-strong/"},
        {"name": "CXOToday", "url": "https://cxotoday.com/specials/eb-1a-visa-filings-surge-as-indian-professionals-shift-away-from-h-1b/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A passport open to pages filled with travel and visa stamps",
    "image_attribution": "Pexels",
    "body": article2_body
}


# ═══════════════════════════════════════════════════════
# INSERT
# ═══════════════════════════════════════════════════════

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
