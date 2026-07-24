#!/usr/bin/env python3
"""
Immigration writer — 2026-06-27 09:05 PT
Two articles:
1. India-US Trade Deal + Ambassador Gor H-1B reassurance
2. Trump India visit 2027 + diplomatic relationship reset
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


# ──────────────────────────────────────────────
# ARTICLE 1: Trade Deal + H-1B Reassurance
# ──────────────────────────────────────────────

article1_body = """When US Ambassador to India Sergio Gor told Outlook Business this week that the ongoing review of the H-1B visa programme is "part of a broader overhaul" of America's immigration system — not a measure "specifically directed at India" — the reassurance landed on an audience that has heard plenty of reassurances before.

What made this one different is what came with it. Gor confirmed that the India-US Bilateral Trade Agreement is now down to finalising "the language that ultimately both sides will sign." In New Delhi last week, US Trade Representative Jamieson Greer and Commerce Minister Piyush Goyal wrapped up three days of intensive negotiations that, by both sides' accounts, were "very productive."

## A deal measured in 'last inches'

The BTA has been in the works since February 2026, when Modi and Trump agreed on a framework during the first high-level contact of Trump's second term. India wants a tariff of around 18 per cent on its goods — lower than the rates facing Bangladesh, Vietnam, and other Asian competitors. In exchange, New Delhi would lower trade barriers and absorb more American goods.

The US Supreme Court's invalidation of Trump's sweeping reciprocal tariffs complicated the legal framework this spring, but negotiators are now working around it. "We're on the last inches of getting it done, and it's very positive," Secretary of State Marco Rubio told IANS on Saturday. India's trade minister Piyush Goyal echoed the sentiment from London: "The day that happens, the deal is on."

US Deputy Assistant Secretary Bethany Poulos Morrison put the ambition in numbers. Washington is "driving towards the goal of Mission 500 — $500 billion in trade by 2030, with a real sense of urgency," she said, noting that 2025 was already a "historic year" for bilateral trade.

## Where immigration enters the fine print

The trade deal explicitly covers strategic sectors — information technology, digital infrastructure, artificial intelligence, semiconductor supply chains — that employ the largest share of Indian H-1B holders. When the US Embassy in India posted on X that the partnership includes "energy security to tech talent exchanges," it was acknowledging what every immigration attorney in the Bay Area already knows: the people are part of the equation.

India has been pushing for several immigration-adjacent concessions alongside the BTA. Chief among them is a totalization agreement — a social security pact that would let short-term workers avoid contributing to the host country's retirement system. The US has 30 such agreements with other countries. India, despite sending more skilled workers to America than any other nation, is not among them. Indian IT companies estimate the pact would save them roughly $4 billion a year in US Social Security contributions. For the 7,300 tech workers who returned to India in the first half of 2026, it could mean the difference between recovering some retirement savings and losing them entirely.

Meanwhile, the structural numbers keep shifting. The H-1B headcount at India's big four IT firms — TCS, Infosys, Wipro, and HCL — has halved since 2017, from 34,507 to 17,997, according to USCIS data. The $100,000 filing fee (struck down by a federal judge this month but under government appeal) and the new wage-weighted lottery have accelerated the retreat. Subcontractor costs at the same firms have jumped more than 20 per cent year-on-year as companies scramble for local substitutes.

## What the deal won't fix

A trade agreement is not an immigration bill. Nothing in the interim deal is expected to reduce the EB-2 India green card backlog — which the July visa bulletin marked "Unavailable" — or restore the domestic visa renewal pilot that Biden launched and Trump killed. The trade framework does not bind USCIS adjudicators, and it will not stop the proposed four-year cap on student visas from taking effect.

But for the Indian professional navigating the current maze — a consulate backlog measured in months, a lottery now ranked by salary, a self-petition approval rate at a record low — the trade deal carries a different kind of weight. It signals that Washington views the Indian talent pipeline as a commercial asset worth protecting, not a regulatory gap worth closing. Gor's reassurance that H-1B changes are not "directed at any particular country" is diplomatic shorthand. The trade deal is where that claim gets tested."""


article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Trade Deal Is in Its 'Last Inches.' For H-1B Workers, That Could Be the Point",
    "subheadline": "US Ambassador Sergio Gor says the H-1B overhaul isn't targeting India, as Washington and New Delhi race to close a bilateral trade agreement that explicitly includes tech talent mobility.",
    "slug": make_slug("india-us-trade-deal-bta-h1b-gor-greer-mission-500-tech-talent"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The India-US trade deal explicitly covers tech talent exchanges — if it includes formal commitments on H-1B pathways or a totalization agreement, it would be the first time trade policy offered structural protection for Indian professionals in America.",
    "tags": ["h1b", "india-us-trade-deal", "bta", "sergio-gor", "jamieson-greer", "mission-500", "uscis", "totalization"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/final-hurdles-remain-h-1b-isnt-targeting-india-says-us-ambassador-sergio-gor"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-says-very-close-trade-deal-with-us-2026-06-25/"},
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/politics/3391547-trump-upcoming-india-visit-strengthening-bilateral-ties"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/india-hopes-to-pursue-social-security-pact-with-us-simultaneously-with-trade-deal/article69233811.ece"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sergio_Gor%2C_official_portrait_%282025%29.jpg",
    "image_caption": "US Ambassador to India Sergio Gor in his official 2025 portrait",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}


# ──────────────────────────────────────────────
# ARTICLE 2: Trump India Visit 2027
# ──────────────────────────────────────────────

article2_body = """Secretary of State Marco Rubio confirmed on Saturday that the United States is planning for President Donald Trump to visit India in early 2027. "We're working towards sometime early next year to have the president come," Rubio told India's IANS news agency, adding that he himself is likely to travel to India later this year to prepare the ground.

If the visit goes ahead, it will be Trump's second trip to India as president. His first, the "Namaste Trump" extravaganza in Ahmedabad in February 2020, drew 100,000 people to a cricket stadium and produced a made-for-television spectacle. It produced almost nothing for immigration.

This time, Indian Americans have reason to wonder whether the pageantry might come with policy.

## From 'hellhole' to hero's welcome

The diplomatic trajectory of the past year reads like a relationship on the rocks. In May 2025, Trump reposted comments calling India a "hellhole" — a remark that drew a rare rebuke from India's foreign ministry. His administration imposed tariffs as high as 50 per cent on Indian goods, including a 25 per cent punitive levy linked to India's purchases of Russian oil. Washington warmed conspicuously to Pakistan. Then came the killing of three Indian sailors in US Navy attacks on commercial ships in the Gulf, a wound that has not fully healed.

And yet, here we are. Rubio visited India for four days in May, attended a Freedom 250 celebration in New Delhi, and relayed a phone call from Trump telling 1,500 guests: "I love India. We've never been closer." A road near the US Consulate in Hyderabad was named "Donald Trump Avenue." Trump thanked India on Truth Social, calling himself "the first US President to be honoured in this way."

Rubio's framing is unapologetic: "We are big fans of PM Modi and the work he has done." Ambassador Sergio Gor, who was at the Hyderabad event, has separately confirmed that Trump "remains keen" to visit.

## What the diaspora wants from the visit

For India's 2.7 million-strong American diaspora, the question is not whether the visit will feature enthusiastic crowds — it will — but whether it produces anything concrete on immigration.

The precedent is instructive but not encouraging. Biden's 2023 state visit for Modi yielded the domestic H-1B visa renewal pilot, which let a small number of H-1B holders renew their visas without leaving the country. The programme has since been terminated under Trump. Modi's 2020 visit to Trump produced nothing on immigration at all.

The diaspora's wish list for 2027 is long and specific: a totalization agreement that would let H-1B workers combine their US Social Security credits with India's EPF contributions; consular processing reforms to clear the stamping backlog that has pushed some H-1B interview appointments to mid-2027; movement on the EB-2 India green card queue, which currently stretches decades; and clarity on the $100,000 filing fee, which a federal judge struck down this month but which the government is appealing.

## The trade deal as a vehicle

The most likely vehicle for immigration concessions is the bilateral trade agreement, which both sides describe as being in its final stages. The BTA covers market access, digital trade, supply chain resilience, and strategic sectors including IT and AI — the backbone of H-1B employment. India has signalled that it wants to pursue a totalization agreement "simultaneously" with the trade deal, according to reporting by The Hindu BusinessLine.

If any of these measures make it into the deal, they would be announced during a high-profile moment — and a presidential visit is the highest-profile moment available.

## The gap between warmth and policy

Rubio's confirmation of the visit is diplomatically significant. It places India among the small number of countries Trump has committed to visiting in his second term, alongside traditional allies in Europe and the Middle East. But the Indian American community has learned to distinguish between diplomatic warmth and policy delivery.

The US-India relationship is clearly on the mend. Trade negotiations are advancing, defence cooperation is expanding, and the Quad framework remains intact. But for the Indian professional tracking their H-1B extension, monitoring their EB-2 priority date, or weighing whether to risk a trip to India for visa stamping, the question remains: does a warmer relationship translate into a more navigable immigration system?

The visit is planned. The wish list is ready. Whether the two will meet is the open question of 2027."""


article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Trump Is Coming to India. Rubio Says So. The Diaspora Has Questions",
    "subheadline": "Secretary of State Marco Rubio confirmed a presidential visit to India in early 2027 — Trump's second as president. For 2.7 million Indian Americans, the immigration deliverables matter more than the pageantry.",
    "slug": make_slug("trump-india-visit-2027-rubio-diaspora-immigration-wish-list"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Trump's last India visit produced zero immigration wins. The 2027 trip arrives alongside a nearly-complete trade deal — Indian Americans want to know if the relationship reset will yield a totalization agreement, consulate reforms, or green card backlog relief.",
    "tags": ["trump-india-visit", "rubio", "modi", "india-us-relations", "h1b", "totalization", "green-card", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/trump-likely-visit-india-early-next-year-rubio-tells-indias-ians-2026-06-27/"},
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/politics/3391547-trump-upcoming-india-visit-strengthening-bilateral-ties"},
        {"name": "Bhaskar English", "url": "https://www.bhaskarenglish.in/international/news/us-secretary-rubio-visit-india-trump-may-visit-early-2027-modi-admirers-134488505.html"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/marco-rubio-seeks-to-repair-us-india-relations-after-trump-era-strains/article69628451.ece"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Official_portrait_of_Secretary_Marco_Rubio_%28cropped%29%282%29.jpg/3840px-Official_portrait_of_Secretary_Marco_Rubio_%28cropped%29%282%29.jpg",
    "image_caption": "US Secretary of State Marco Rubio, who confirmed Trump's planned visit to India in early 2027",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body
}


articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
