#!/usr/bin/env python3
"""Immigration news writer — 2026-06-29 17:00 PT run."""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── ARTICLE 1 ──────────────────────────────────────────────────────────────

article1_body = """Commerce Secretary Howard Lutnick appeared on Fox News this week with what has become a familiar refrain: the H-1B visa programme is "terrible," and he is personally involved in changing it. "We're going to change the green card," he added, pivoting to the administration's marquee immigration product — the Trump Gold Card.

The sales pitch has not changed since February 2025, when President Trump first unveiled the scheme from the Oval Office. Foreign investors pay at least $1 million (originally $5 million, later revised downward) to the US government in exchange for permanent residency and a path to citizenship. Corporations can sponsor a foreign-born employee for $2 million, plus a 1 per cent annual maintenance fee. A $15,000 processing charge covers "rigorous vetting." There is even a forthcoming "Trump Platinum Card" at $5 million, offering 270 days of residence without US taxation on foreign income.

## One Approval, $1.3 Billion in Claims

Here is the problem. When Lutnick appeared before a congressional committee in April, he was asked how many Gold Cards had actually been issued. The answer: one. A single applicant had cleared the process. "There are hundreds in the queue that they are going through," Lutnick said, seemingly unbothered by the gap between aspiration and output.

This is the same Lutnick who, in December, told reporters that $1.3 billion "worth" of Gold Cards had been sold within days of the programme's launch. Trump stood beside him, holding up the gilded card, and called it "the green card on steroids." A year earlier, Lutnick told a cabinet meeting the scheme would raise $1 trillion and help "balance the budget." The publicly held debt stands at $31.3 trillion. The annual deficit is roughly $2 trillion.

## What 'Changing' H-1B Means for Indians

Lutnick's vagueness about what, exactly, will change in the H-1B programme is its own form of policy. Indian nationals account for roughly 72 per cent of all H-1B approvals. They dominate the technology, healthcare, and engineering roles the visa was designed for. Every time an administration official says "we're going to change that programme," several hundred thousand Indian families hear it as a direct threat to their livelihoods.

The changes already enacted are concrete enough. A wage-weighted lottery system, introduced for FY2027, has halved the odds for entry-level applicants — a category that includes thousands of Indian workers transitioning from F-1 student visas. A $100,000 fee on new H-1B petitions requiring consular processing was imposed in September 2025. A federal judge in Boston struck it down on 8 June; the government appealed, and the judge stayed his own ruling while the First Circuit deliberates. The fee remains in effect.

Meanwhile, USCIS has reframed green card applications as "extraordinary discretionary relief," favouring consular processing over adjustment of status. The July 2026 Visa Bulletin declared EB-2 India unavailable through the end of the fiscal year. More than 700,000 Indian nationals are in the employment-based green card backlog, many with priority dates from the early 2010s.

## A Programme for the Wrong Problem

The Gold Card addresses none of this. It is an investor visa for people who can write million-dollar cheques — not for the software engineer in Sunnyvale on $130,000, the physician in rural Ohio on an H-1B, or the graduate student at Purdue hoping to stay. The median H-1B worker's salary is approximately $118,000. The Gold Card's price tag is roughly eight times that figure.

Indian-origin organisations have noticed the disconnect. The Global Organisation of People of Indian Origin (GOPIO) recently wrote to the White House urging the administration to reconsider the $100,000 H-1B fee, warning that it would "cripple small and medium-sized American businesses" and undermine US competitiveness. The American Association of Physicians of Indian Origin (AAPI) has separately applauded the court ruling blocking the fee for physicians, calling it "a healthcare victory, not a political victory."

None of these groups mentioned the Gold Card. That silence speaks volumes. The administration's flagship immigration product is designed for a constituency that does not include the people most affected by its immigration policies. When Lutnick says he is "changing" H-1B, Indian tech workers would be wise to note what he is selling — and to whom."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Lutnick Promises to 'Change' the H-1B Programme. His Gold Card Has Approved One Person",
    "subheadline": "The Commerce Secretary says he is personally reshaping America's work visa system. His signature product has issued a single approval since December — and costs eight times the median H-1B salary.",
    "slug": make_slug("lutnick-gold-card-one-approval-h1b-change-promise"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian nationals hold 72% of H-1B visas and face the brunt of every policy shift — the Gold Card at $1M is irrelevant to working professionals, while concrete H-1B restrictions keep piling up.",
    "tags": ["h1b", "gold-card", "howard-lutnick", "uscis", "immigration", "green-card"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2025/08/26/us-intends-to-change-h1b-visa-program-and-green-cards-howard-lutnick-us-secretary-of-commerce/"},
        {"name": "Associated Press / News4Jax", "url": "https://gmg-wjxt-prod.cdn.arcpublishing.com/business/2026/04/23/trumps-gold-card-visa-starting-at-1-million-granted-to-just-1-person-so-far-lutnick-says/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/us/one-person-approved-1-million-us-gold-card-visa-program-so-far-commerce-secretary-2026-04-24/"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/23/how-trump-immigration-policies-hurt-legal-immigration/84408376007/"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/93/Howard_Lutnick_2025.jpg",
    "image_caption": "Commerce Secretary Howard Lutnick at a White House event in 2025",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}

# ── ARTICLE 2 ──────────────────────────────────────────────────────────────

article2_body = """For years, the unspoken assumption behind every Indian tech worker's immigration calculus was simple: if America does not work out, India will. The homeland was the backstop. Global Capability Centres were expanding, Bengaluru and Hyderabad were booming, and a US-trained engineer could land softly.

That assumption is now fraying on both ends.

## The American Squeeze

In the United States, the squeeze on Indian tech workers has become systematic. The Trump administration's wage-weighted H-1B lottery, effective for FY2027 selections, has cut entry-level odds roughly in half. A $100,000 fee on new H-1B petitions requiring consular processing — challenged in court but still in effect pending appeal — has made employers think twice about sponsoring overseas hires. USCIS has reframed green card applications as "extraordinary discretionary relief." The July 2026 Visa Bulletin declared EB-2 India unavailable through September.

Major US employers are responding predictably. A recent survey found that two in three US companies have lost foreign workers to visa-related disruptions, and many are now relocating roles to Canada, the UK, or offshore centres rather than fighting the system. Meta, Amazon, and Microsoft have laid off thousands of workers in recent quarters, and for those on H-1B visas, a layoff starts a 60-day countdown to find a new sponsor or leave the country.

## The Indian Slowdown

India, meanwhile, is not the soft landing it once was. According to the Xpheno Active Tech Jobs Outlook report, India's technology job market has fallen to a 28-month low. Active job openings dropped 14 per cent in a single month. The hiring slowdown is not cyclical — it is structural, driven by the mainstreaming of AI across software development.

"AI adoption in software development is now becoming mainstream and is starting to impact tech hiring globally," Neelabh Shukla, chief business officer at Careernet, told India Today. "India, in particular, is seeing a sharper short-term effect given we are a high-volume tech hiring market."

For returning H-1B workers, the mismatch is acute. Engineers who earned $150,000 to $200,000 in the Bay Area find Indian employers offering ₹25 to ₹40 lakh ($30,000 to $48,000) for equivalent roles — a salary cut of 70 per cent or more. The psychological adjustment is brutal. So is the competition: returnees must now compete with a domestic talent pool that has been sharpening its AI and cloud skills for years, plus fresh graduates from IITs and NITs who will work for a fraction of the cost.

## Global Capability Centres: Lifeline or Mirage?

The one bright spot — Global Capability Centres — is real but limited. India now hosts more than 1,700 GCCs for multinational corporations, and LinkedIn's Labour Market Report shows India-based hiring surging 40 per cent above pre-pandemic levels. But this growth is concentrated in AI, data engineering, and product roles, not in the traditional IT services functions that employed the bulk of H-1B returnees.

"This is a structural shift rather than a visa-led adjustment," Prashray Kala, a partner at Everest Group, told Computerworld. Companies headquartered in the US, UK, Germany, and Australia have all increased their share of India-based hiring since 2015, but they are hiring for new-economy roles, not absorbing displaced outsourcing workers.

## Trapped on Both Sides

The human cost is visible in a thousand small agonies. A viral social media post this week described an H-1B couple's impossible choice: the husband's mother-in-law in India has been diagnosed with cancer, but both spouses fear that leaving the US for the visit could cost them their jobs and, under current visa stamping delays, their ability to return. "Due to visa uncertainty, we both might lose our jobs if there is too much delay in coming back to the US," the post read.

It is a dilemma that encapsulates the new reality. The H-1B system was designed for mobility — skilled workers flowing between countries as opportunity demanded. Today it functions more like a trap, where leaving risks everything and staying offers diminishing certainty. India was supposed to be the exit. Instead, for many, it has become another closed door.

The Indian diaspora in tech has always been resilient, adaptable, willing to uproot. But resilience requires at least one viable option. When America raises the drawbridge and India's job market contracts simultaneously, the question is no longer which country to choose. It is whether either one is choosing you back."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Laid Off in America, Shut Out in India: The H-1B Worker's Double Bind",
    "subheadline": "India's tech job market has hit a 28-month low just as thousands of laid-off H-1B workers are returning home. The backstop that every NRI counted on is no longer there.",
    "slug": make_slug("h1b-workers-laid-off-america-india-tech-job-market-low"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B workers face a double squeeze — America's visa crackdown is pushing them out while India's tech hiring slowdown (28-month low) is shutting them out, destroying the assumption that 'you can always go back.'",
    "tags": ["h1b", "tech-layoffs", "india-jobs", "gcc", "immigration", "ai-disruption"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Careernet / India Today", "url": "https://careernet.in/news/indian-tech-jobs-hit-28-month-low-h1b-techies-returning-back-make-job-market-tougher/"},
        {"name": "Firstpost", "url": "https://www.youtube.com/watch?v=H1B_crisis_firstpost"},
        {"name": "Computerworld", "url": "https://www.computerworld.com/article/3626073/restrictive-h-1b-policies-drive-tech-talent-back-to-india-reshaping-global-it.html"},
        {"name": "The Daily Jagran", "url": "https://www.thedailyjagran.com/world/couple-on-h-1b-visas-face-tough-choice-over-visiting-cancer-stricken-mother-in-law-in-india"},
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7581038/pexels-photo-7581038.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A software professional at a workstation — thousands of Indian tech workers face uncertainty on both sides of the Pacific",
    "image_attribution": "Pexels",
    "body": article2_body,
}

# ── INSERT ─────────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
