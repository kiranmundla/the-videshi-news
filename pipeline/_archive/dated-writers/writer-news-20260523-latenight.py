#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-23 late-night batch
Topics: Rubio's India visit + Iran war impact on Indian Gulf workers
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Supabase config ──
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

def sb_patch(table, filters, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filters}", headers={**HEADERS, "Prefer": "return=minimal"}, json=data, timeout=30)
    return r.status_code

def make_slug(headline, date_suffix="20260523"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Rubio's India Visit — Repairing Strained Ties
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "America's Top Diplomat Just Landed in India to Fix a Relationship That Trump's Own Tariffs Broke. The NRI Community Is Watching Closely.",
    "subheadline": "Secretary of State Marco Rubio begins a four-day tour through Kolkata, Agra, Jaipur, and New Delhi on Saturday — the highest-level U.S. visit to India in months. On the agenda: trade talks that have stalled since February, energy deals to wean India off Russian oil, a Quad meeting that analysts are calling an 'unannounced downgrade,' and the growing shadow of Pakistan's rising influence in Washington.",
    "slug": make_slug("rubio-india-visit-tariffs-quad-nri"),
    "category": "news",
    "vertical": "diplomacy",
    "diaspora_angle": "For the 4.4 million Indian Americans in the US, the Rubio visit is a litmus test for the relationship they straddle. Tariff uncertainty affects Indian IT exports and the companies many NRIs work for. The stalled trade deal has implications for everything from H-1B visa processing times to pharmaceutical imports. And the Quad's quiet downgrade under Trump raises questions about whether the Indo-Pacific framework that many diaspora foreign-policy voices championed is losing steam.",
    "tags": ["Marco Rubio", "India", "US-India relations", "tariffs", "Quad", "Modi", "trade deal", "Pakistan", "Iran war", "energy", "NRI", "diplomacy"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters — Rubio's trip to India signals US need to repair ties", "url": "https://www.reuters.com/world/china/rubios-trip-india-signals-us-need-repair-ties-2026-05-23/"},
        {"name": "The Indian Eye — US State Secretary Marco Rubio to visit India from May 23 to 26", "url": "https://theindianeye.com/us-state-secretary-marco-rubio-to-visit-india-from-may-23-to-26/"},
        {"name": "Reuters — Rubio sees progress in Iran talks, more work to be done", "url": "https://www.reuters.com/world/us/us-secretary-state-rubio-sees-progress-iran-talks-more-work-be-done-2026-05-22/"}
    ]),
    "score_total": 92,
    "status": "published",
    "published_at": now,
    "body": """When the most senior American diplomat to visit India in months touches down in Kolkata on Saturday morning, he will be arriving in a country that has spent the last three months wondering whether Washington still considers it a priority.

Secretary of State Marco Rubio's four-day tour — Kolkata, Agra, Jaipur, then New Delhi for a Quad foreign ministers' meeting — is the Biden-era "indispensable partnership" playbook executed under very different circumstances. The itinerary is diplomatic theatre at its most careful: cultural stops in India's intellectual and heritage capitals before the hard conversations begin in the national capital. The message is meant to be "we value India beyond the transactional." Whether New Delhi buys it is another matter entirely.

## What Broke

The fracture lines are not subtle. In his second term, President Trump welcomed Prime Minister Narendra Modi to the White House early and warmly — then imposed tariffs of up to 50% on Indian goods, the steepest levied on any major U.S. partner. Half of that rate was explicitly linked to India's continued purchases of Russian oil, a punitive measure that infuriated New Delhi.

In February, the two sides announced a "framework for an interim agreement" that would bring the effective tariff rate down to 18%. Then the U.S. Supreme Court struck down Trump's tariff authority in late February, dropping the rate to 10% overnight — and India, suddenly in a better position, slowed the negotiations. Washington interpreted this as foot-dragging. New Delhi called it strategic patience.

"I do not expect Secretary Rubio will have much impact in changing the downward trajectory," said Richard Rossow of the Center for Strategic and International Studies. "The lack of a trade agreement — more than three months after the announcement of the interim deal — clouds other areas of engagement."

Meanwhile, the geopolitical landscape has shifted in ways that make India uncomfortable. Pakistan has emerged as a key American interlocutor in efforts to end the Iran war, with Islamabad facilitating back-channel communications that have given it renewed leverage in Washington. Trump's visit to Beijing this month amplified Indian anxieties further. The U.S. is simultaneously courting India's two most sensitive rivals, and the diplomatic bandwidth for New Delhi's concerns is shrinking.

## The Energy Equation

Rubio told reporters on Thursday that energy would be a centrepiece of his India conversations. "We want to sell them as much energy as they'll buy," he said — a blunt framing that reflects both commercial ambition and strategic calculation.

The Iran war has scrambled global energy markets. With the Strait of Hormuz effectively blockaded and Brent crude above $111 a barrel, India's energy import bill has ballooned. The U.S. sees an opportunity to displace Russian crude — which still accounts for roughly 35% of India's oil imports — with American LNG and shale oil. India sees an opportunity to negotiate from strength, with multiple suppliers competing for its market.

The gap between "we want to sell" and "we'll buy on our terms" is where the real negotiation lies. India has historically resisted single-source energy dependency, and swapping Russian crude for American crude without significant price concessions would be politically untenable for Modi, who has framed energy diplomacy as sovereign pragmatism.

## The Quad's Quiet Downgrade

Perhaps the most telling signal of the visit is what will not happen: there will be no leader-level Quad summit. India has been pressing the White House to schedule a Trump visit to Delhi for a Quad leaders' meeting — the kind of high-profile engagement that would signal strategic continuity. So far, the White House has not responded.

Rubio's meeting with Quad foreign ministers — from India, Japan, and Australia — will be the third such gathering without a leader-level engagement. Rossow described it as an "unannounced downgrade" of the grouping, which was formed specifically as a democratic counter to China's growing influence in the Indo-Pacific.

The U.S. Embassy in New Delhi pushed back gently, posting on X that the Quad stands "together for a free and open Indo-Pacific... from supporting regional security to diversifying critical minerals supply chains." But the rhetoric rings hollow without the presidential-level commitment that gave the Quad its strategic weight during the Biden years.

## What the Diaspora Is Watching

For the 4.4 million Indian Americans — the highest-earning and one of the fastest-growing ethnic groups in the United States — the state of U.S.-India relations is not abstract geopolitics. It is personal.

Tariff uncertainty directly affects the Indian IT services companies — TCS, Infosys, Wipro, HCL — that employ tens of thousands of workers in the U.S. and process hundreds of thousands of visa applications annually. A stalled trade deal means stalled regulatory harmonization, which means continued uncertainty around H-1B processing, pharmaceutical approvals, and cross-border investment flows.

The NRI foreign-policy community — think tanks, PACs, and lobbying groups that have spent two decades building bipartisan support for the U.S.-India relationship — is watching the Quad's trajectory with particular concern. The Indo-Pacific framework was their signature achievement, a strategic architecture that elevated India's role in American foreign policy beyond the transactional. Its quiet erosion under Trump threatens that entire project.

Ambassador Sergio Gor, dubbed "the India whisperer" by the Atlantic Council's Michael Kugelman, has been working to reset ties since arriving in New Delhi in January. Gor is a personal friend of Trump's and a former White House adviser — the kind of appointment that signals the relationship matters, even when the policy signals are mixed.

## What Comes Next

Rubio will meet Modi and External Affairs Minister S. Jaishankar in New Delhi early next week. The agenda is dense: trade, defense procurement, energy, counterterrorism cooperation, and the broader Indo-Pacific strategy. The question is whether any of it translates into concrete deliverables — a finalized trade agreement, a defense deal, a Quad summit date — or whether it remains, as one Indian diplomat put it privately, "a very expensive listening tour."

The answer matters beyond the bilateral relationship. India is the world's most populous country, its fastest-growing major economy, and — depending on who you ask in Washington — either America's most important strategic partner in Asia or a frustrating fence-sitter that refuses to pick sides. Rubio's visit will not resolve that tension. But it will reveal whether the Trump administration considers it worth managing — or is content to let it drift."""
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Iran War's Human Cost — Indian Sailors & Gulf Workers
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "Twenty Thousand Sailors Are Trapped in the Persian Gulf. The Ones Reuters Found Were Indian — Praying Between Missile Strikes, Eating One Meal of Rice a Day.",
    "subheadline": "Three months into the Iran war, more than 20,000 mariners are stranded on 2,000 vessels in the Gulf. Separately, 1.1 million Indians have returned from the region since hostilities began. From a stranded captain off Dammam to a jeweller sleeping in his cousin's tea stall in Kanpur, the war is dismantling the Gulf economy that a generation of Indians was built on.",
    "slug": make_slug("indian-sailors-stranded-gulf-iran-war-hormuz"),
    "category": "news",
    "vertical": "diaspora",
    "diaspora_angle": "India has 9 million workers in the Gulf out of 19 million overseas Indians. The Strait of Hormuz blockade and Gulf economic slowdown are hitting Indian families directly — from Kerala's remittance economy to Kanpur's leather factories. This is the largest disruption to the Indian overseas workforce since the Gulf War evacuations of 1990.",
    "tags": ["Iran war", "Strait of Hormuz", "Indian sailors", "Gulf workers", "remittances", "Kerala", "Kanpur", "shipping", "NRI", "Saudi Arabia", "blockade", "employment"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters — Iran's intensified closure of Strait of Hormuz piles misery on stranded sailors", "url": "https://www.reuters.com/world/asia-pacific/irans-intensified-closure-strait-hormuz-piles-misery-stranded-sailors-2026-05-22/"},
        {"name": "Reuters — India's job engine strains as Iran war hits remittances and trade", "url": "https://www.reuters.com/world/india/indias-job-engine-strains-iran-war-hits-remittances-trade-2026-05-22/"},
        {"name": "Reuters — France readies UN resolution on Hormuz as vote on US text stalls", "url": "https://www.reuters.com/world/france-readies-un-resolution-hormuz-vote-us-text-stalls-2026-05-22/"}
    ]),
    "score_total": 90,
    "status": "published",
    "published_at": now,
    "body": """The phone call came from somewhere in the Persian Gulf, on a cargo ship that had not moved in eleven weeks. Indian sailor Salman Siddiqui's voice was steady but stripped of the optimism that characterised his first weeks at anchor. "The only thing we do here is plan how to spend the night and pray to God that we do not get hit during an attack," he told Reuters.

Siddiqui is one of more than 20,000 mariners trapped on approximately 2,000 vessels in the Gulf, caught in the crossfire of a war they have no part in and a blockade they cannot escape. When Tehran closed the Strait of Hormuz after U.S.-Israeli strikes on Iran began on February 28, it sealed the world's most important oil chokepoint — and with it, the fates of thousands of sailors whose ships happened to be on the wrong side of the waterway.

Three months later, Iran is not easing its grip. On Wednesday, the newly created Persian Gulf Strait Authority published a map reaffirming Tehran's claims to a wide stretch of water on either side of the chokepoint — a signal that the blockade is hardening into something more permanent, and that the sailors' ordeal is far from over.

## Life on a Stranded Ship

When a Reuters team travelled on a resupply boat to vessels moored off the Saudi coast this week, sailors on a tanker gathered by the handrail to wave — a rare moment of contact with the outside world. For nearly three months, these men have lived isolated lives: tiny living quarters, communal dining areas, and scorching, sun-baked decks under Gulf temperatures that now regularly exceed 45°C.

Captain Mohit Kohli, who commanded a large German-owned cargo vessel trapped in the Gulf after sailing from Singapore, described the transformation aboard his ship. "The crew who was usually loud and happy were now silent. Meals got shorter. Conversations were more guarded," he told Reuters after finally returning to India this month. His ship was fortunate — the German owners arranged a relief crew. Many others have not been so lucky.

Mohamed Arrachedi, network coordinator for the Arab World and Iran at the International Transport Workers' Federation, described cases of pay delays, refusals to repatriate sailors, and a catastrophic lack of provisions. Some seafarers called him in tears. The ITF has been contacted by more than 2,000 sailors seeking help since the war began — and those are only the ones who can get a phone signal.

Some sailors earn between $100 and $200 a month. Some have not been paid since last year. Ship owners are refusing to repatriate them, or offering repatriation only if they forfeit their back pay. Some survive on a single meal of rice or lentils per day, with brief moments of internet connection to contact loved ones.

"They need a collective intervention because they are key for our economies, for the supply chains, but also because they are active seafarers and they are civilians," Arrachedi said.

## The Scale of the Indian Exodus

The stranded sailors are the most visible edge of a much larger disruption. According to India's foreign ministry, approximately 1.1 million Indians — including workers, passengers, and other travellers — returned from the Gulf region between the start of hostilities on February 28 and the end of April. The ministry has not responded to subsequent queries about updated figures.

Of India's nearly 19 million overseas workers, roughly 9 million are in the Gulf. The World Bank estimates that economic growth in the Gulf region will slow to 1.3% in 2026, down from 4.4% in 2025 — a collapse that is already translating into hiring freezes, project cancellations, and mass layoffs.

Mohammad Qureshi, 32, worked at a jewellery shop in Saudi Arabia until January, earning about 30,000 rupees ($311) a month — enough to build a small home and help pay for his sister's wedding. Now he earns barely a third of that at his cousins' tea stall in Kanpur, unable to return to the Gulf. "Life in Saudi was easy and the money was good," he said. "Life is difficult here. I pray the war ends soon so we can go back."

At Hayat Placement Services in Kanpur, recruiter Gautam Bhatnagar said the pipeline had collapsed. "Earlier, we used to place five to 10 candidates every month. Now we are lucky if we can place even one or two."

## Kerala's Remittance Economy Under Threat

The ripple effects are most acute in southern Kerala, where Gulf remittances have shaped the local economy for decades. Thomas Cherian, 50, spent 18 years working for a construction firm in Saudi Arabia before returning on leave in December. He was due back in March, but the company halted its project and laid off approximately 600 Indian workers. If he cannot return by end of June, his visa will lapse.

Ajith Kolassery, CEO of NORKA Roots — an agency of Kerala's Non-Resident Keralites Affairs Department — said there has been no mass return yet, but the trajectory is alarming. "If the conflict continues, financial stress in Gulf economies could lead to large-scale repatriation, adding pressure to Kerala's already strained job market."

India's overseas remittances stood at $102.5 billion in April-December 2025, up from $92.4 billion a year earlier. The Reserve Bank of India has not responded to queries about the Iran war's impact on remittance flows, but economists expect a significant decline in the January-June 2026 data.

## The Double Blow to Indian Manufacturing

The Gulf disruption is only half the story. The Strait of Hormuz blockade has driven up fuel, gas, logistics, and shipping costs across Indian manufacturing — particularly in export-oriented sectors.

In Kanpur, which accounts for roughly a quarter of India's $6 billion annual leather exports and employs about 500,000 people, the impact is already severe. Taj Alam, owner of Kings International — a leather factory supplying saddlery overseas and sports goods to Decathlon — said his facility, which once employed over 500 workers and processed 200 hides a day, is now running at half capacity with half its workforce.

"The outlook will remain bleak until the Strait of Hormuz stabilises," Alam said. "Why invest when the future looks uncertain?"

India's unemployment rate rose to 5.2% in April from 4.9% in February, but urban youth joblessness remains far higher at nearly 14%. With 400 million Indians aged 15-29, the combination of returning Gulf workers, weakened manufacturing, and AI-driven automation is creating what K.E. Raghunathan, national chairman of the Association of Indian Entrepreneurs, calls a structural narrowing of traditional employment avenues.

## What Comes Next

Saudi Arabia's ports authority has helped hundreds of vessels resupply with food, water, fuel, and medicines, and has aided more than 500 sailors in transferring from their ships. "Seafarers stuck on a vessel in uncertain waters — the most important thing in the world is knowing that there is a shore open to reach," said Suliman Almazroua, president of the Saudi Ports Authority.

But these are palliative measures in a crisis that requires a geopolitical solution. France is preparing a UN Security Council resolution on the Strait of Hormuz, though a U.S.-Bahraini text has been stalled for weeks as China and Russia signal potential vetoes. Until the strait reopens, the 20,000 sailors remain at anchor, the 9 million Gulf workers remain at risk, and the remittance economy that sustains millions of Indian families remains under siege.

For the Indian diaspora watching from abroad, the Gulf has always been more than a job market. It is where a generation of Indians — from Kerala nurses to Kanpur leather workers to Rajasthan jewellers — built the economic foundation that allowed their families back home to send children to school, build homes, and enter the middle class. The Iran war is not just disrupting trade routes. It is threatening the social contract that made the Indian Gulf migration one of the great economic stories of the last half-century."""
})

# ── Insert articles ──
print(f"\n{'='*60}")
print(f"Publishing {len(articles)} articles...")
for a in articles:
    try:
        res = sb_post("p2_articles", a)
        print(f"  ✓ [{a['category']}] {a['headline'][:80]}...")
        print(f"    ID: {a['id']}, Slug: {a['slug']}")
    except Exception as e:
        print(f"  ✗ FAILED: {a['headline'][:60]}... — {e}")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY — age out older articles
# ══════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print("Running score decay...")
try:
    resp = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?status=eq.published&score_total=gt.30&select=id,score_total,published_at",
        headers=HEADERS, timeout=30
    )
    all_arts = resp.json()
    from datetime import timedelta
    now_dt = datetime.now(timezone.utc)
    decayed = 0
    for art in all_arts:
        pub = datetime.fromisoformat(art["published_at"].replace("Z", "+00:00"))
        age_hours = (now_dt - pub).total_seconds() / 3600
        if age_hours > 48:
            new_score = max(30, int(art["score_total"] * 0.97))
            if new_score < art["score_total"]:
                sb_patch("p2_articles", f"id=eq.{art['id']}", {"score_total": new_score})
                decayed += 1
    print(f"  Decayed {decayed} articles (of {len(all_arts)} eligible)")
except Exception as e:
    print(f"  Score decay error: {e}")

print(f"\n{'='*60}")
print("Writer batch complete!")
