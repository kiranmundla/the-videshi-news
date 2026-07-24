#!/usr/bin/env python3
"""Immigration writer — July 14, 2026 02:00 UTC run."""

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

# ─────────────────────────────────────────────────────────────
# ARTICLE 1: Xbox Layoffs + H-1B Scapegoating + Asha Sharma
# ─────────────────────────────────────────────────────────────

article1_body = """Xbox just announced the largest layoffs in gaming industry history — 3,200 positions across Microsoft's gaming division, with 1,600 eliminated on July 6 and the rest scheduled through June 2027. Within days, the restructuring became something else entirely: a flashpoint in America's bitter H-1B debate, and a case study in how quickly Indian-American identity can be weaponised in the age of nativist politics.

## The Layoffs That Lit the Fuse

CEO Asha Sharma framed the cuts as a long-overdue reckoning. "Our business today is not healthy," she wrote in an internal memo. "We are operating at margins that are 3–10x lower than comparable platform and publishing businesses." Four studios — Compulsion Games, Double Fine Productions, Ninja Theory, and Undead Labs — were spun off or put up for sale.

None of that was particularly unusual. Microsoft has shed more than 15,000 positions across its gaming division since the Activision Blizzard acquisition in 2023. What happened next was.

## The Scapegoating

Within hours, a narrative took hold on X: Microsoft had fired Americans to hire cheaper foreign workers on H-1B visas. Screenshots of Microsoft's H-1B application numbers circulated alongside claims that Sharma — an Indian-origin executive — was personally orchestrating a replacement scheme. Rep. Riley Moore of West Virginia called for an outright end to the H-1B programme. "This is INSANE," he posted. "It's long past time to end the H-1B scam."

The accusations were false on multiple fronts.

Microsoft Chief Communications Officer Frank Shaw responded on X on July 10, clarifying that the H-1B figures critics cited applied to all of Microsoft — a company with 220,000 employees globally — and included routine visa renewals alongside new applications. The numbers represented a small fraction of the total workforce. Shaw also noted that most of the Xbox positions being eliminated were based outside the United States, which made the "replacing Americans with foreigners" framing logically incoherent.

## The Racial Targeting

A subset of critics went further, directing explicitly racist attacks at Sharma. Posts on X falsely portrayed her as a foreign executive cutting American jobs. One widely shared post claimed her "one function is to purge white Americans and replace them with Indian cheap foreign labor."

Sharma was born in Wisconsin. She holds a Bachelor of Science from the University of Minnesota's Carlson School of Management. Before joining Microsoft, she served as COO of Instacart and as VP of Product at Meta, overseeing Messenger, Instagram Direct, and platform services. She is a second-degree black belt in taekwondo.

Shaw addressed the racial dimension directly, stressing Sharma's American upbringing and education.

## The Timing

The backlash did not emerge in a vacuum. The same week as the Xbox layoffs, Vice President JD Vance and Labor Department Inspector General Anthony D'Esposito announced a major H-1B fraud investigation, with D'Esposito citing "whistleblowers talking about some of the biggest companies" and naming Cognizant, the India-founded IT services firm, specifically. The investigation followed Trump's attempt to impose a $100,000 H-1B application fee — struck down by a federal judge in June as an unconstitutional tax.

The convergence of events created a political atmosphere in which any corporate restructuring involving an Indian-origin executive became automatically suspect.

## What This Means for Indian Americans

For the estimated 600,000 H-1B visa holders in the United States — 73 percent of whom are Indian nationals, according to Pew Research — the Xbox episode is a warning. The distinction between "Indian-American born in Wisconsin" and "Indian worker on an H-1B" is collapsing in public discourse. The same week Sharma was racially targeted, the Federal Reserve appointed her to co-lead its Productivity and Jobs Task Force alongside Marc Andreessen and Stanford economist Charles Jones, a recognition of her expertise in AI and technology management.

The irony is difficult to miss. America's central bank trusts an Indian-American executive to shape policy on the future of work. A segment of the American public views the same person as a symbol of foreign takeover.

For Indian professionals navigating the H-1B system — already contending with the new wage-weighted lottery, consulate backlogs stretching into 2027, and the DOL's expanding fraud probe — the lesson is uncomfortable: in the current climate, your identity can become a liability regardless of your passport."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Xbox's Biggest Layoffs Ever Became a Referendum on Indian-American Identity",
    "subheadline": "CEO Asha Sharma was born in Wisconsin. It didn't matter. The H-1B backlash came anyway.",
    "slug": make_slug("xbox-layoffs-asha-sharma-h1b-backlash-indian-american-identity"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian-American tech executive racially targeted during layoffs, exposing how H-1B backlash is collapsing the distinction between Indian immigrants and Indian Americans born in the US.",
    "tags": ["h1b", "xbox", "microsoft", "asha-sharma", "racism", "indian-american", "tech-layoffs"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "GameRant", "url": "https://gamerant.com/xbox-layoffs-h1b1-visa-replacements-accusations-response/"},
        {"name": "Fox News", "url": "https://www.foxnews.com/politics/ceo-under-fire-mass-layoffs-amid-foreign-worker-hiring-spree-now-appointed-feds-task-force-jobs"},
        {"name": "New York Post", "url": "https://nypost.com/2025/07/10/business/fury-erupts-as-microsoft-division-fires-1600-after-thousands-of-foreign-worker-visas-approved/"},
        {"name": "The Sun (UK)", "url": "https://www.thesun.co.uk/tech/35297645/microsoft-to-axe-4800-jobs-xbox-worst-hit/"},
        {"name": "Engadget", "url": "https://www.engadget.com/gaming/xbox/days-after-announcing-mass-layoffs-xbox-ceo-asha-sharma-tapped-to-advise-the-federal-reserve-on-jobs-165059681.html"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Asha_Sharma_CEO_of_XBOX_at_2026_XBOX_Showcase.jpg/330px-Asha_Sharma_CEO_of_XBOX_at_2026_XBOX_Showcase.jpg",
    "image_caption": "Asha Sharma, CEO of Xbox, at the 2026 Xbox Showcase",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}

# ─────────────────────────────────────────────────────────────
# ARTICLE 2: Three Indian-Origin Leaders Lead Fed Task Forces
# ─────────────────────────────────────────────────────────────

article2_body = """The Federal Reserve just named the leaders of five task forces that will shape how America's central bank operates for the next generation. Three of the five are Indian-origin.

Raghuram Rajan, Raj Chetty, and Asha Sharma — a former central bank governor, a pioneering economist, and a technology executive — will co-lead panels on balance sheet policy, data and liquidity, and productivity and jobs, respectively. The appointments, announced by Fed Chairman Kevin Warsh, represent the most significant concentration of Indian-origin intellectual leadership in the history of America's most powerful economic institution.

## Who They Are and What They'll Do

**Raghuram Rajan** will co-lead the Balance Sheet Policy task force, which will "examine the costs, benefits, and institutional implications" of the Fed's balance sheet regime. Rajan currently serves as the Katherine Dusak Miller Distinguished Service Professor of Finance at the University of Chicago's Booth School of Business. He was the 23rd Governor of the Reserve Bank of India from 2013 to 2016 and served as Chief Economist of the International Monetary Fund from 2003 to 2006. He is best known for his prescient 2005 warning at the Jackson Hole conference about growing risks in the financial system — a warning dismissed by then-Treasury Secretary Lawrence Summers as "misguided" three years before the financial crisis proved Rajan right.

**Raj Chetty**, the William A. Ackman Professor of Public Economics at Harvard University, will co-lead the panel on Liquidity Dependence. Chetty directs Opportunity Insights, a research lab that has fundamentally changed how economists study social mobility and economic opportunity in America. His co-chairs include Harvard economics professor Jeremy Stein, former Walmart president Doug McMillon, and University of Chicago economics professor Kevin Murphy. Chetty's family emigrated from India; he grew up to become one of the most cited economists in the world.

**Asha Sharma**, CEO of Microsoft's gaming division Xbox, will co-lead the Productivity and Jobs task force, which will assess "the economic impact of new general-purpose technologies, including artificial intelligence." Her co-chairs are Marc Andreessen, co-founder of venture capital firm Andreessen Horowitz, and Stanford University economics professor Charles I. Jones. Sharma's appointment carries particular significance — and controversy — given that it was announced days after she oversaw the elimination of 3,200 Xbox positions.

## The Immigration Irony

The appointments arrived during the most hostile week for Indian immigration policy in recent memory. Vice President Vance announced a major H-1B fraud investigation. The Department of Labor issued dozens of subpoenas targeting employers, with the Inspector General specifically naming Cognizant, the India-founded IT services firm, as a company facing whistleblower allegations. On social media, Rep. Riley Moore called to "end the H-1B scam."

The juxtaposition is difficult to overstate. The same country that is investigating whether Indian workers belong in its offices has just asked three Indian-origin thinkers to redesign the machinery of its monetary policy. Rajan, who first came to America as a student at MIT, is now trusted to evaluate how the world's most important central bank manages its $7 trillion balance sheet. Chetty, the child of immigrants, literally maps the pathways through which American children succeed or fail. Sharma, whose parents immigrated from India, is charged with advising the Fed on whether artificial intelligence will destroy or create jobs.

## What the Fed Actually Wants

Warsh described the review as a response to structural economic change. "The U.S. economy has changed significantly over the last generation, and never more so than right now," he said. "Each task force will carefully consider whether policymakers' means and methods, analytical tools, and policy approaches can be improved upon."

The task forces will operate independently and are expected to produce recommendations by the end of 2026. Their scope is unusually broad — covering everything from the Fed's massive bond holdings to its data infrastructure to the macroeconomic implications of AI. The fact that Warsh chose three Indian-origin leaders for three of five panels speaks to a simple reality: at the highest levels of American economic thought, the Indian diaspora is not a peripheral presence. It is the centre.

## Why This Matters to the Diaspora

For the roughly 4.4 million Indian Americans — and the hundreds of thousands navigating the visa system — the Fed appointments are a counterweight to the nativist surge. They do not erase the DOL investigations, the consulate backlogs, the H-1B fee battles, or the racial targeting of executives like Sharma. But they document something the political debate consistently ignores: the Indian diaspora's contribution to American institutional capacity is not marginal. It is structural.

Rajan warned about 2008 before anyone else did. Chetty's work reshaped how America understands opportunity. Sharma ran AI products before being handed the gaming industry's largest company. When the Fed needed its best minds for a generational review, it looked — in three of five cases — at people whose families made the same journey that today's H-1B applicants are trying to make."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "The Fed Just Asked Three Indian-Origin Thinkers to Redesign American Monetary Policy",
    "subheadline": "Raghuram Rajan, Raj Chetty, and Asha Sharma will lead task forces covering the Fed's balance sheet, data infrastructure, and the AI economy.",
    "slug": make_slug("fed-reserve-rajan-chetty-sharma-indian-origin-task-forces"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Three Indian-origin leaders appointed to lead Federal Reserve task forces in the same week that political rhetoric questioned whether Indian workers should be in America at all — a stark reminder of the diaspora's structural role in American institutions.",
    "tags": ["raghuram-rajan", "raj-chetty", "asha-sharma", "federal-reserve", "indian-diaspora", "immigration", "monetary-policy"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy/raghuram-rajan-among-three-indians-to-head-us-monetary-policy-task-forces-check-details"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/finance/feds-warsh-taps-broad-group-central-bank-outsiders-oversee-review-2026-07-10/"},
        {"name": "Inshorts", "url": "https://inshorts.com/en/news/raghuram-rajan-xboxs-asha-sharma-roped-in-to-review-policies-of-us-fed-1720609320095"},
        {"name": "Engadget", "url": "https://www.engadget.com/gaming/xbox/days-after-announcing-mass-layoffs-xbox-ceo-asha-sharma-tapped-to-advise-the-federal-reserve-on-jobs-165059681.html"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Raghuram_Rajan%2C_IMF_69MS040421048l.jpg/330px-Raghuram_Rajan%2C_IMF_69MS040421048l.jpg",
    "image_caption": "Raghuram Rajan, former RBI Governor, now co-leading the Federal Reserve's Balance Sheet Policy task force",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body,
}

# ─────────────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
