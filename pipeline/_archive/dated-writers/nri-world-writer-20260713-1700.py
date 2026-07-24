#!/usr/bin/env python3
"""NRI World writer – 2026-07-13 17:00 PT
Two articles:
  1. Three Indian-origin leaders tapped to co-lead Federal Reserve policy task forces
  2. India-UK trade deal goes live July 15 — what changes for NRIs in Britain
"""

import json, uuid, os, sys, re, subprocess
from datetime import datetime, timezone

# ── Supabase setup ──────────────────────────────────────────────────────────

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser("~/workspace/.env.supabase"))

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
    sys.exit(1)

def make_slug(base):
    slug = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"{slug}-{today}"

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ══════════════════════════════════════════════════════════════════════════════
# Article 1: Indian-Origin Leaders Co-Lead Fed Task Forces
# ══════════════════════════════════════════════════════════════════════════════

art1_body = """\
Federal Reserve Chairman Kevin Warsh announced on July 10 the formation of five policy review task forces — and three of the fifteen people chosen to lead them are of Indian origin. Raghuram Rajan will co-chair the Balance Sheet Policy review, Raj Chetty will co-chair the Data review, and Sarah Bond, the Xbox president born Asha Sharma in India before being raised in the United States, will co-chair the Productivity and Jobs review. It is an extraordinary concentration of Indian-origin talent at the centre of American monetary policy.

## The Three Appointees

Rajan needs little introduction in diaspora circles. The former Reserve Bank of India governor and current University of Chicago Booth School professor is perhaps best known for his 2005 Jackson Hole speech warning of the financial system's fragility — a warning largely ignored until the 2008 crisis proved him right. At the Fed, he will review how the central bank manages its $7 trillion balance sheet alongside Jeremy Stein, a former Fed governor and Harvard economist.

Chetty, a Harvard economics professor, runs the Opportunity Insights lab and has spent the past decade producing granular research on economic mobility in America. His work mapping which neighbourhoods produce upward mobility — and which do not — has reshaped how policymakers think about inequality. He will lead the Data task force with Kevin Murphy of the University of Chicago, examining how the Fed collects, analyses, and publishes economic information.

Bond, who goes by Sarah Bond professionally, is the CEO of Xbox at Microsoft. Born Asha Sharma in India, she was raised in the United States and previously held senior roles at Meta and Instacart. She will co-chair the Productivity and Jobs review with Doug McMillon, the CEO of Walmart — a pairing that brings both technology-sector and retail-sector perspectives to questions about automation, labour markets, and growth.

## Why This Matters

The Fed's policy review is a periodic exercise in which the central bank re-examines its frameworks, tools, and communication strategies. The last comprehensive review concluded in 2020, producing the "average inflation targeting" framework that guided the Fed's response to the pandemic-era price surge. This round, initiated by Warsh after he took over the chairmanship, is expected to revisit that framework in light of the inflation episode and the interest-rate hiking cycle that followed.

The reviews are not academic exercises. The 2020 review directly shaped the Fed's decision to hold rates near zero even as inflation began rising in 2021, a choice that remains controversial. Whatever the 2026 task forces recommend will influence how the Fed sets rates, communicates its intentions, and manages its portfolio for years to come.

The remaining two task forces — Communications, co-chaired by Charles Jones and Marc Andreessen, and Inflation, co-chaired by Stanford's Robert Hall and Mohamed El-Erian — round out the fifteen-person leadership group. But it is the Indian-origin trio that has drawn the most attention, both for the quality of the appointees and for what their selection signals about the diaspora's reach.

## A Measure of Influence

Indian Americans have held prominent positions in U.S. economic policy before. Rajan himself served as chief economist of the International Monetary Fund. Ajay Banga leads the World Bank. Neel Kashkari runs the Minneapolis Fed. But having three Indian-origin figures simultaneously co-leading Fed review panels — covering the balance sheet, data infrastructure, and the future of work — is without recent precedent.

The appointments also reflect how the diaspora's influence has broadened beyond the technology sector. Rajan is an academic economist. Chetty is a social scientist whose work straddles economics and public policy. Bond is a corporate executive who built her career in gaming and consumer technology. They represent three distinct trajectories within the Indian-origin professional class, unified only by the fact that each has reached the top of a field that feeds directly into the Fed's work.

For the roughly 4.8 million Indian Americans watching from outside the Eccles Building, the message is straightforward: when the Federal Reserve needed people to rethink how American monetary policy works, it turned, in significant part, to the Indian diaspora.
"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Three Indian-Origin Leaders Tapped to Co-Lead Federal Reserve Policy Task Forces",
    "subheadline": "Raghuram Rajan, Raj Chetty, and Xbox CEO Sarah Bond (born Asha Sharma) will co-chair three of the Fed's five review panels — an unprecedented concentration of diaspora talent at the heart of U.S. monetary policy.",
    "slug": make_slug("indian-origin-leaders-fed-policy-task-forces"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Three Indian-origin figures simultaneously co-leading Federal Reserve policy review panels — spanning economics, data science, and corporate leadership — signals the breadth of diaspora influence in U.S. economic policymaking.",
    "tags": ["nri", "diaspora", "federal-reserve", "raghuram-rajan", "raj-chetty", "sarah-bond", "economics", "monetary-policy", "indian-american"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/finance/feds-warsh-names-heads-five-task-forces-reviewing-monetary-policy-2026-07-10/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/federal-reserve-policy-review-task-forces-warsh-f8a2e9c1"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy/raghuram-rajan-named-to-lead-fed-review-task-force"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/economy/central-banking/fed-warsh-review-task-forces-2026-07-10"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/d5/Raghuram_Rajan%2C_IMF_69MS040421048l.jpg",
    "image_caption": "Raghuram Rajan, former RBI Governor and IMF Chief Economist, will co-chair the Federal Reserve's Balance Sheet Policy review",
    "image_attribution": "Wikimedia Commons / International Monetary Fund",
    "body": art1_body.strip(),
}


# ══════════════════════════════════════════════════════════════════════════════
# Article 2: India-UK Trade Deal Goes Live July 15
# ══════════════════════════════════════════════════════════════════════════════

art2_body = """\
On July 15, two agreements that took years to negotiate will quietly go into effect and change the financial lives of tens of thousands of Indian professionals in Britain. The India-UK Comprehensive Economic and Trade Agreement — the first full free-trade deal between the two countries — and the Double Contribution Convention, a social security pact that eliminates dual contributions for Indian workers in the UK, will both take effect simultaneously.

For the roughly 75,000 Indian professionals and more than 900 Indian companies operating in Britain, the social security provision alone is worth real money: an estimated 25 per cent of salary that was previously lost to paying into both countries' systems at once.

## The Social Security Savings

The Double Contribution Convention is the less glamorous of the two agreements, but for individual workers it is the more consequential. Under the current system, an Indian citizen working in the UK must contribute to Britain's National Insurance scheme while also remaining liable for India's social security contributions. The new pact exempts Indian workers from UK National Insurance payments for up to five years — extended from three years in the original proposal — provided they remain covered by India's system.

The arithmetic is significant. National Insurance contributions in Britain run at 8 per cent of earnings for employees and 13.8 per cent for employers. For a software engineer earning £80,000 a year, the personal savings amount to roughly £6,400 annually. Employers, too, see their costs fall, which may make it marginally easier to sponsor Indian workers. India's Commerce Minister Piyush Goyal, who led the trade negotiations, has called the DCC "a recognition that our workers should not be penalised for their mobility."

## What the Trade Deal Covers

The CETA itself is broader. It grants 99 per cent duty-free access for Indian goods entering the UK — a significant expansion from the current regime, which applies tariffs of up to 14 per cent on categories like textiles, gems, and marine products. For British exporters, India has offered reduced tariffs on Scotch whisky, certain automotive components, and medical devices.

Two provisions are aimed squarely at the diaspora. First, a new mobility pathway creates 1,800 annual slots for Indian chefs, yoga instructors, and classical musicians to work in Britain under dedicated visa categories. The provision reflects lobbying by Britain's Indian restaurant sector, which has struggled with staffing shortages since Brexit curtailed the supply of European workers. Second, the deal opens 137 service sub-sectors to Indian professionals, including information technology, engineering, and financial services — sectors where Indian firms already have a significant presence.

Prime Minister Narendra Modi called the agreement a "historic milestone" and said it would help India reach its target of $100 billion in bilateral trade with the UK by 2030. Current annual trade between the two countries stands at about $42 billion.

## What NRIs in Britain Should Know

The practical implications break down by category. Indian nationals on Tier 2 (Skilled Worker) visas will be eligible for the DCC exemption from July 15, though they will need to apply through India's Employees' Provident Fund Organisation and present a certificate of coverage to HMRC. The process is expected to take several weeks to operationalise, so immediate savings may not appear in the first pay packet.

For Indian businesses operating in the UK, the tariff reductions on goods entering Britain take effect immediately. Companies that import textiles, leather goods, or processed foods from India will see their costs fall. In the other direction, British firms exporting to India will benefit from reduced duties, though India's tariff schedule is being phased in over a five-to-seven-year period for sensitive categories.

The 1,800 mobility slots for chefs, yoga instructors, and musicians represent a new category entirely. Applications will be handled through the UK's points-based immigration system, with a separate allocation from the general Skilled Worker visa pool. Details on the application process are expected from the UK Home Office before the July 15 effective date.

## The Bigger Picture

The India-UK deal is the first major trade agreement India has signed with a Western economy since its 2011 pact with Japan. Negotiations began in January 2022 and stalled repeatedly over issues including intellectual property protections, dairy tariffs, and the mobility provisions. That it reached the finish line at all is partly a function of post-Brexit Britain's need for new trade relationships and partly a reflection of India's growing leverage as the world's fifth-largest economy.

For the Indian diaspora in Britain — a community of 1.8 million that includes everyone from NHS doctors to corner-shop owners to City of London bankers — the deal's most tangible effect will be the social security savings. The rest is infrastructure: lower trade barriers, more mobility pathways, and a formal framework that acknowledges India and Britain's economic relationship has outgrown the colonial-era templates that still, in some ways, defined it.
"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India-UK Trade Deal Goes Live on July 15 — What Changes for NRIs in Britain",
    "subheadline": "The new trade pact eliminates dual social security contributions for Indian workers in the UK, saves them roughly 25 per cent of salary, and opens 1,800 annual mobility slots for chefs, yoga instructors, and classical musicians.",
    "slug": make_slug("india-uk-trade-deal-nri-impact"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "75,000+ Indian professionals in Britain stand to save roughly 25 per cent of salary through the social security pact, while new mobility pathways and tariff reductions reshape the economic relationship between the diaspora's two largest host countries.",
    "tags": ["nri", "diaspora", "india-uk", "trade-deal", "ceta", "social-security", "piyush-goyal", "immigration", "britain"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Livemint", "url": "https://www.livemint.com/economy/india-uk-free-trade-agreement-takes-effect-july-15-2026"},
        {"name": "Press Information Bureau", "url": "https://pib.gov.in/PressReleasePage.aspx?PRID=2131205"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy/india-uk-ceta-double-contribution-convention-july-15"},
        {"name": "Inshorts / IANS", "url": "https://inshorts.com/en/news/indiauk-trade-deal-takes-effect-july-15"},
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/The_Minister_for_Commerce_and_Industry%2C_Shri_Piyush_Goyal_and_the_Secretary_of_State_for_Business_and_Trade%2C_Mr._Jonathan_Reynolds_at_the_signing_of_the_Comprehensive_Economic_and_Trade_Agreement.jpg/1280px-thumbnail.jpg",
    "image_caption": "India's Commerce Minister Piyush Goyal and UK Trade Secretary Jonathan Reynolds at the signing of the India-UK Comprehensive Economic and Trade Agreement",
    "image_attribution": "Wikimedia Commons / Government of India (GODL-India)",
    "body": art2_body.strip(),
}


# ── Insert into Supabase ────────────────────────────────────────────────────

def insert_article(article, label):
    payload = json.dumps(article, ensure_ascii=False)
    result = subprocess.run(
        [
            "curl", "-sS", "-X", "POST",
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            "-H", f"apikey: {SUPABASE_KEY}",
            "-H", f"Authorization: Bearer {SUPABASE_KEY}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=representation",
            "-d", payload,
        ],
        capture_output=True, text=True, timeout=30,
    )
    status_ok = '"id"' in result.stdout and '"headline"' in result.stdout
    if status_ok:
        print(f"✅ {label}: inserted — slug={article['slug']}")
    else:
        print(f"❌ {label}: FAILED")
        print(f"   stdout: {result.stdout[:500]}")
        print(f"   stderr: {result.stderr[:300]}")
    return status_ok


ok1 = insert_article(art1, "Art1 (Fed Task Forces)")
ok2 = insert_article(art2, "Art2 (India-UK Trade Deal)")

print(f"\nDone: {int(ok1) + int(ok2)}/2 articles inserted.")
if not (ok1 and ok2):
    sys.exit(1)
