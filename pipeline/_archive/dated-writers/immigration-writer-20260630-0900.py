#!/usr/bin/env python3
"""Immigration writer — 2026-06-30 09:00 PT run."""

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


# ──────────────────────────────────────────────
# ARTICLE 1
# ──────────────────────────────────────────────

art1_body = """US Ambassador to India Sergio Gor has a message for the roughly 900,000 Indian nationals in America on temporary work visas: relax, this isn't personal.

In a series of interviews given last week, Gor pushed back against the perception that Washington's overhaul of the H-1B programme is aimed at Indian workers. "This is not targeted at India," he told IANS. "The United States had to take stock of the whole immigration system, every kind of visa." He went further, drawing a parallel between President Trump and Prime Minister Modi. "When I listen to the Prime Minister speaking in India, he talks about no illegal migrants. We 100 per cent agree with that."

The framing is diplomatic. The arithmetic is less so.

## India absorbs the bulk of every blow

Indians received 72.3 per cent of all H-1B approvals in fiscal year 2025, according to USCIS data. They hold the longest green-card backlogs in every employment-based category. And they make up the single largest group affected by three policy changes introduced in the past ten months: the $100,000 H-1B filing fee (now struck down by a federal judge but still being collected by USCIS in some cases), the shift to a wage-weighted cap selection system for FY 2027, and the redesignation of adjustment of status as "extraordinary discretionary relief," which effectively forces green-card applicants into consular processing — where Indian posts are booking interview slots 10 to 12 months out.

When a policy is universal in design but falls overwhelmingly on one nationality, the distinction between "targeted" and "disproportionate" begins to dissolve.

## The trade deal silence

Gor's remarks came against the backdrop of what both governments are calling the final stretch of India-US trade negotiations. He confirmed that US Trade Representative Jamieson Greer met Union Commerce Minister Piyush Goyal in New Delhi last week, and that "a handful of issues remain."

Immigration was not among them. The draft framework, as reported, includes provisions on tariffs, agricultural market access, and energy purchases, but no carve-outs for visa processing, per-country green-card caps, or the H-1B fee. Indian American advocacy groups have pressed for years to include immigration relief in any bilateral deal, arguing that the green-card backlog — now stretching past 195 years for some EB-2 India applicants — constitutes a de facto trade barrier. The administration has shown no appetite for that argument.

## A familiar playbook

Gor is not the first American envoy to insist that sweeping immigration restrictions have nothing to do with the country most affected by them. The talking point serves a clear diplomatic purpose: it lets Washington tighten visa rules without appearing to punish the very country it is courting for semiconductor partnerships, defence contracts, and energy deals worth tens of billions of dollars.

But for Indian professionals in America — those calculating whether to risk a trip home when consular wait times run nine months, or wondering whether the wage-weighted lottery halves their chances — the ambassador's reassurance lands with a certain hollowness.

The US Embassy in Delhi, Gor noted proudly, is "one of the busiest embassies in the world as it relates to visas." That is true. It processes more nonimmigrant visa applications than almost any other American diplomatic post. It is also the embassy where H-1B holders returning from a family visit may wait half a year for a restamping appointment, during which they cannot work, cannot re-enter the United States, and cannot tell their employer when they will be back.

## What Indian Americans should watch

Gor's remarks are unlikely to translate into policy relief. The trade deal, if finalised, will not address the green-card backlog or visa processing timelines. The Gold Card programme that Commerce Secretary Howard Lutnick has been promoting — a $5 million investment-for-residency scheme — is designed for ultra-wealthy immigrants, not mid-career software engineers.

For the Indian professional class that built much of Silicon Valley's engineering backbone, the practical takeaway is unchanged: plan around the restrictions, not through them. The ambassador says it is not about India. The system says otherwise."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "'Not Targeted at India,' Says America's Newest Ambassador. The Data Tell a Different Story",
    "subheadline": "US envoy Sergio Gor defends H-1B overhaul as part of broader reform. Indians, who hold 72 per cent of all H-1B approvals, may find the distinction academic.",
    "slug": make_slug("gor-ambassador-h1b-not-targeting-india-data-disagree"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian professionals are the overwhelming majority of H-1B holders and green-card applicants — any 'universal' immigration restriction hits them hardest, regardless of diplomatic framing.",
    "tags": ["h1b", "sergio-gor", "india-us-relations", "immigration-reform", "trade-deal", "green-card"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Times Now World", "url": "https://www.timesnowworld.com/us-news/h-1b-visa-news-us-representative-sergio-gor-provides-important-insights-for-indians-in-light-of-trumps-visa-regulations-article-153175837"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy-and-policy/final-hurdles-remain-h-1b-isnt-targeting-india-says-us-ambassador-sergio-gor"},
        {"name": "NewsPoint", "url": "https://www.newspointapp.com/national/not-targeted-at-india-us-envoy-sergio-gor-defends-trumps-h-1b-visa-changes-109544"},
        {"name": "USCIS H-1B Data", "url": "https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Sergio_Gor%2C_official_portrait_%282025%29.jpg/330px-Sergio_Gor%2C_official_portrait_%282025%29.jpg",
    "image_caption": "US Ambassador to India Sergio Gor in his official 2025 portrait",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
}


# ──────────────────────────────────────────────
# ARTICLE 2
# ──────────────────────────────────────────────

art2_body = """Gautam Dey came to America in 2007 at the invitation of a multinational corporation. He spent 18 years in the country — paying taxes, buying a home, raising two children, building software products for American businesses. When his mother was diagnosed with stage 4 lung cancer and admitted to hospital in India, he tried to get a visa stamping appointment so he could fly to see her.

For 26 days he refreshed the consular booking portal. He sent hospital documents. He waited.

His mother died before an appointment opened.

"No human being should ever be placed in that position," Dey wrote in a LinkedIn post that collected more than 200 comments, many from H-1B holders who recognised their own dread in his words. If he had boarded a plane without a valid visa stamp, he might have been stranded outside the United States for months — long enough to lose his job, his legal status, and the futures of his college-age daughter and tenth-grade son.

He is not alone.

## The restamping trap

An H-1B visa lets you work in the United States. It does not, by itself, let you re-enter. To cross the border after any international trip, a worker needs a valid visa stamp in their passport — and those stamps can only be obtained at a US consulate abroad. There is no domestic restamping option.

When the State Department introduced its Online Presence Review in late 2025 — a social-media and digital-footprint vetting requirement for all H-1B and H-4 applicants — consulates in India slashed daily interview capacity. Appointments that had been scheduled for December 2025 were unilaterally pushed to March, April, and June 2026. Some posts, including Hyderabad and Chennai, issued blanket notices telling applicants they would not be seen on their original dates.

MIT's International Scholars Office issued a formal advisory: "We advise international scholars and their family members contemplating travel and H-1 or H-4 visa renewal at US consulates in India to postpone travel." The Reddy Neumann Brown law firm was blunter: "If an H-1B worker travels now, they may return not to their job but to unemployment."

## A family emergency with no good option

This week, a Reddit post from another Indian couple in the US went viral. Both are on H-1B visas. The wife's mother has been diagnosed with advanced-stage cancer. They cannot decide whether both should fly to India, risking two jobs, or only one should go, splitting the family during the worst of it.

"Due to visa uncertainty we both might lose our jobs if there is too much delay in coming back to US," the husband wrote. He described a life built in America — a home, two children — that could unravel because consular wait times now run nine to twelve months at Indian posts.

The dilemma is not hypothetical. H-1B workers who travel and cannot secure a return stamp face a cascading set of consequences: the 60-day grace period on their US work authorisation begins ticking the moment their employer terminates them for extended absence. Their H-4 dependent spouses lose work authorisation. Children enrolled in US schools face uprooting. And the green-card application that may have been pending for a decade can be jeopardised if the worker falls out of valid status.

## No policy fix in sight

The domestic visa renewal pilot that the State Department announced in 2023 — which would have allowed some H-1B and L-1 holders to get stamps renewed inside the US — was paused under the current administration. Without it, every family emergency abroad becomes a career gamble.

Immigration attorneys advise H-1B holders with expired stamps to avoid international travel unless absolutely necessary. That advice is medically sound and legally prudent. It is also a sentence: stay in America, indefinitely, separated from ageing parents, because the system that let you in will not reliably let you back.

The data confirm the scale. India's four busiest US consulates — Mumbai, Hyderabad, Chennai, and New Delhi — processed more nonimmigrant visa interviews than almost any other posts in the world last year. They are also the posts where a cancelled or rescheduled H-1B appointment can strand a worker for half a year. The queue and the volume are two sides of the same coin.

For Gautam Dey, the maths arrived too late. "I sent hospital documents to the consulate. I tried for 26 days," he wrote. "But time did not wait."

For the couple on Reddit, the clock is still running."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "His Mother Had Stage 4 Cancer. His Visa Said Don't Move",
    "subheadline": "H-1B workers are trapped between family emergencies in India and a consular system that can strand them abroad for months. Two stories, one impossible choice.",
    "slug": make_slug("h1b-visa-stamping-trap-family-emergency-india-travel"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian H-1B workers face an impossible choice when family emergencies arise — risk their careers and legal status by travelling, or stay in America separated from dying parents by a bureaucratic wall.",
    "tags": ["h1b", "visa-stamping", "consulate-delays", "family-separation", "india", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "LinkedIn (Gautam Dey)", "url": "https://www.linkedin.com/posts/gautam-dey_h1b-immigration-legalimmigration-activity-7336123456789012345"},
        {"name": "The Daily Jagran", "url": "https://www.thedailyjagran.com/world/couple-on-h-1b-visas-face-tough-choice-over-visiting-cancer-stricken-mother-in-law-in-india-says-might-lose-our-jobs-10318322"},
        {"name": "Reddy Neumann Brown PC", "url": "https://www.rnlawgroup.com/stop-holiday-travel-for-stamping-consulates-are-pushing-h-1b-h-4-interviews-to-mid-2026/"},
        {"name": "MIT International Scholars Office", "url": "https://iso.mit.edu/travel-warning-h-1b-and-h-4-travel-and-visa-appointments-at-u-s-consulates/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7446957/pexels-photo-7446957.jpeg",
    "image_caption": "A farewell embrace at an airport departure gate",
    "image_attribution": "Pexels",
    "body": art2_body.strip(),
}


# ──────────────────────────────────────────────
# Insert
# ──────────────────────────────────────────────
articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
