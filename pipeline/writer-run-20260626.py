#!/usr/bin/env python3
"""Writer run for June 26, 2026 — two news articles."""
import json, os, subprocess, datetime, re

# Load env
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def insert_article(article):
    """Insert article into p2_articles via Supabase REST API."""
    payload = json.dumps(article)
    result = subprocess.run(
        [
            "curl", "-sS",
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            "-X", "POST",
            "-H", f"apikey: {SUPABASE_KEY}",
            "-H", f"Authorization: Bearer {SUPABASE_KEY}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=representation",
            "-d", payload,
        ],
        capture_output=True, text=True, timeout=30,
    )
    print(f"  HTTP response: {result.stdout[:300]}")
    if result.returncode != 0:
        print(f"  STDERR: {result.stderr[:200]}")
    return result.stdout

now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ────────────────────────────────────────────────────────────────
# ARTICLE 1: Amazon's $48B India Bet
# ────────────────────────────────────────────────────────────────

article1_body = """Andy Jassy walked into the prime minister's office this week with numbers that are hard to ignore. Amazon, he announced, would pour an additional $13 billion into India's AI and cloud infrastructure by 2030 — raising the company's total planned investment in the country to $48 billion.

The fresh capital, disclosed after Jassy met Prime Minister Narendra Modi in New Delhi on Thursday, will fund a major expansion of Amazon Web Services data centres in Mumbai and Hyderabad, giving Indian startups, enterprises and government agencies access to custom AI chips, managed AI services and developer tools.

"As we grow Amazon in India, our business priorities continue to align with India's priorities of democratising access to AI, digitising small businesses, creating jobs, and enabling exports," Jassy said, adding that the company intended to be "a long-term partner in India's growth story."

## The Scale of the Wager

The $48 billion figure is cumulative, covering 2026 to 2030. It follows an initial $15 billion commitment made in 2023 and a $35 billion pledge last December. Across all its businesses — cloud, e-commerce, logistics and entertainment — Amazon's investments in India since 2010 now exceed $88 billion.

More than $21 billion of the 2026–2030 total is earmarked specifically for AI and cloud infrastructure. Amazon did not break down how the remainder would be deployed, though the company signalled aggressive expansion plans across its consumer-facing businesses: more than 20 new fulfilment centres and over 100 last-mile delivery stations are slated to open this year alone, with a focus on reaching Tier III and Tier IV cities.

## A Hyperscaler Arms Race

Amazon is not betting alone. India has become ground zero for a hyperscaler arms race, with the world's largest tech companies committing tens of billions to build the computing infrastructure that will power the next decade of AI.

Microsoft pledged $17.5 billion for India by 2029, its largest single-country commitment in Asia. Google earmarked $15 billion to build data centre capacity in southern India over five years. And domestic players are not standing still: Reliance Industries, the Adani Group and investors from Australia's AirTrunk to the Canada Pension Plan Investment Board have all entered the data centre race.

New Delhi has actively courted this capital with policy incentives, including tax exemptions for foreign cloud providers whose global workloads run from Indian data centres. The government's pitch is straightforward: India offers 1.4 billion consumers, a rapidly digitising economy and one of the world's largest pools of engineering talent.

## Quick Commerce, Too

Beyond infrastructure, Amazon is also expanding its quick-commerce service, Amazon Now, to more than 300 cities and towns — a direct challenge to Blinkit, Swiggy's Instamart, Zepto and Walmart-backed Flipkart, which announced plans to open 1,500 micro-fulfilment centres by year's end. The quick-commerce battle is separate from the cloud story but underscores the same thesis: India's consumer market is too large and too dynamic to leave to competitors.

## The Diaspora Connection

For the Indian diaspora, Amazon's deepening commitment has implications that extend beyond stock tickers and data centre locations. The company already supports 2.8 million jobs in India and has trained over 10 million Indians in cloud computing skills. It now aims to support 3.8 million jobs by 2030 and enable $80 billion in cumulative e-commerce exports.

For NRIs in the tech industry — many of whom built their careers on AWS — the expansion creates new bridges between their professional lives abroad and the Indian economy. Indian-origin professionals hold senior positions across Amazon's global operations, and the company has been among the largest sponsors of H-1B visas for Indian workers.

The larger signal is structural. When the three biggest cloud providers collectively commit more than $80 billion to one country's digital infrastructure, they are not simply building data centres. They are embedding India into the global AI supply chain — a chain that Indian engineers and entrepreneurs, at home and abroad, are increasingly well-positioned to climb.

*Sources: TechCrunch, Barron's, Storyboard18, Amazon official announcement*"""

article1 = {
    "headline": "Amazon Just Raised Its India Bet to $48 Billion. Most of the New Money Is Going to AI.",
    "subheadline": "CEO Andy Jassy met Modi in New Delhi and announced $13 billion in fresh capital for data centres in Mumbai and Hyderabad — the latest move in a hyperscaler arms race that is turning India into a global AI hub.",
    "slug": "amazon-48-billion-india-investment-jassy-modi-ai-data-centres-aws-mumbai-hyderabad-20260626",
    "body": article1_body,
    "category": "news",
    "vertical": "tech-investment",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/07/Andy_Jassy.jpg",
    "image_caption": "Amazon CEO Andy Jassy, who met PM Modi in New Delhi to announce the investment",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/25/amazon-ups-india-bet-with-fresh-13b-ai-infrastructure-investment/"},
        {"name": "Barron's", "url": "https://barrons.com"},
        {"name": "Storyboard18", "url": "https://storyboard18.com"},
        {"name": "Amazon official announcement", "url": "https://www.aboutamazon.in"}
    ]),
    "diaspora_angle": "Amazon employs hundreds of thousands of Indian-origin workers globally and plans to support 3.8 million jobs in India by 2030, creating new career bridges for NRIs in cloud and AI.",
    "published_at": now_utc,
}

# ────────────────────────────────────────────────────────────────
# ARTICLE 2: DHS Crackdown on Immigration Fraud
# ────────────────────────────────────────────────────────────────

article2_body = """The Department of Homeland Security has opened an unprecedented front against immigration fraud — and Indian nationals are at the centre of its first two test cases.

In the space of a single week, federal authorities levied a quarter-million-dollar fine against a California attorney accused of filing mass-produced asylum claims on behalf of Indian clients, and secured a guilty plea from an Indian national in Boston who helped stage armed robberies so that fake "victims" could apply for visas.

The cases are unrelated in detail but connected in message: Washington is no longer content to deport individual fraud cases. It is going after the infrastructure — the lawyers, the fixers, the organised networks — that makes systemic immigration fraud possible.

## The $255,000 Fine

On June 22, Homeland Security Investigations issued five notices of intent to fine Vinod Doddamani, an Indian-American immigration attorney based in California, a total of $255,232 — the maximum allowed by law.

According to DHS, Doddamani operates a nationwide practice representing mostly Indian nationals in asylum proceedings. Across 32 cases, the agency alleges, he filed 64 documents that were "identical or nearly identical in language and substance," containing the same factual narratives about alleged persecution — a hallmark, investigators say, of boilerplate fraud rather than genuine individual claims.

"Our message to immigration attorneys is clear: if you engage in fraud, you will be held accountable," DHS General Counsel James Percival said in a statement. ICE posted on X that "the days of attorneys abusing and defrauding our immigration system are OVER."

The action is the first time DHS has used a May directive — authored by Percival — to pursue financial penalties against attorneys accused of filing fraudulent asylum claims. Until now, ICE had depended on immigration judges and criminal fraud statutes to deter the practice. The new policy gives ICE attorneys their own enforcement tools.

Doddamani has not been found liable. The notices of intent to fine are the start of an administrative process, not a final determination. He has not commented publicly.

## The Staged Robberies

Three days after the Doddamani announcement, an entirely separate fraud case reached its latest chapter in federal court in Boston.

Mitul Patel, a 40-year-old Indian national living in Worcester, Massachusetts, pleaded guilty on June 24 to conspiracy to commit visa fraud. He was one of 11 Indian nationals charged in March 2026 in what prosecutors described as an elaborate scheme to manufacture eligibility for U visas — a category reserved for victims of certain violent crimes who have assisted law enforcement.

The scheme, led by Rambhai Patel (no relation to Mitul), worked like this: organisers would stage armed robberies at convenience stores and liquor shops across Massachusetts and other states. The "robber" — typically Rambhai Patel — would walk in with a weapon, threaten clerks and flee with cash from the register, all captured on the store's surveillance cameras. The clerks, who had paid up to $20,000 each for the privilege, would then wait five minutes, call police and file U visa applications claiming they were crime victims.

Between March 2023 and the ring's exposure, at least six stores were used for staged holdups. Rambhai Patel earned approximately $850,000 from the operation, all of which he was ordered to forfeit after his conviction in 2025. Mitul Patel is scheduled for sentencing on July 29.

## The Broader Pattern

These cases do not exist in a vacuum. Over the past year, the Trump administration has waged an escalating campaign against what it characterises as systemic fraud in the immigration system — one that has increasingly turned its spotlight on Indian nationals.

Earlier this year, ICE revealed a separate investigation into "phantom employees" and fraudulent student visa schemes involving thousands of foreign students, many of them Indian. The H-1B visa programme, which Indians dominate with 71 per cent of all visas issued, has been subjected to higher fees and tighter scrutiny. And the administration's broader asylum crackdown — including a blanket requirement to exhaust five years of domestic remedies before seeking international arbitration — has disproportionately affected Indian applicants.

## What the Diaspora Should Know

For the estimated 4.8 million Indian Americans and the hundreds of thousands of Indian nationals on temporary visas, the message from these cases is double-edged.

On one hand, the crackdown targets genuine fraud — the kind that harms legitimate applicants by overwhelming the system and inviting suspicion on everyone. Immigration attorneys, diaspora advocacy groups and even the U.S.-India Strategic Partnership Forum have long argued that fraud erodes the credibility of Indian applicants who follow the rules.

On the other, the administration's rhetoric — "the days of abusing our immigration system are OVER" — does not always distinguish between organised fraud rings and the systemic challenges that push people toward desperate measures. Legal experts warn that the new enforcement tools could chill legitimate asylum claims, particularly from Indian applicants fleeing religious or political persecution.

The diaspora's challenge is familiar but sharpening: build political power to shape the rules, while ensuring that a few high-profile fraud cases do not define how America sees its largest source of skilled immigrants.

*Sources: U.S. Department of Justice, DHS official statement, Fox News, News Dive, The Texas Insider, Worcester Telegram*"""

article2 = {
    "headline": "Washington Just Fined an Indian Immigration Lawyer $255,000 for Filing Cookie-Cutter Asylum Claims. That's Only Half the Story.",
    "subheadline": "In the same week, a separate ring of Indian nationals pleaded guilty to staging armed robberies at convenience stores so fake 'victims' could apply for U visas. Both cases signal a new phase in the crackdown on immigration fraud.",
    "slug": "dhs-fines-indian-attorney-doddamani-asylum-fraud-patel-staged-robbery-u-visa-crackdown-20260626",
    "body": article2_body,
    "category": "news",
    "vertical": "immigration",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/John_Joseph_Moakley_United_States_Courthouse_September_2024.jpg/1280px-John_Joseph_Moakley_United_States_Courthouse_September_2024.jpg",
    "image_caption": "The John Joseph Moakley United States Courthouse in Boston, where the staged robbery visa fraud case was heard",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        {"name": "U.S. Department of Justice", "url": "https://www.justice.gov"},
        {"name": "DHS official statement", "url": "https://www.dhs.gov"},
        {"name": "Fox News", "url": "https://foxnews.com"},
        {"name": "News Dive", "url": "https://newsdive.net"},
        {"name": "Worcester Telegram", "url": "https://telegram.com"}
    ]),
    "diaspora_angle": "The crackdown directly affects Indian nationals in the US asylum system and raises concerns that high-profile fraud cases could invite broader scrutiny on all Indian visa applicants.",
    "published_at": now_utc,
}

# ────────────────────────────────────────────────────────────────
# Insert both articles
# ────────────────────────────────────────────────────────────────

for i, art in enumerate([article1, article2], 1):
    print(f"\n=== Inserting Article {i}: {art['headline'][:60]}... ===")
    resp = insert_article(art)
    try:
        data = json.loads(resp)
        if isinstance(data, list) and len(data) > 0:
            print(f"  ✓ Inserted: slug={data[0].get('slug')}, id={data[0].get('id')}")
        elif isinstance(data, dict) and data.get("message"):
            print(f"  ✗ Error: {data.get('message')}")
        else:
            print(f"  Response: {resp[:200]}")
    except:
        print(f"  Raw response: {resp[:200]}")

print("\n=== Writer run complete ===")
