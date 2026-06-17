#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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
        "headline": "There Are 230,000 Green Cards Gathering Dust. A White House Adviser Wants Them Back in Play",
        "subheadline": "A member of the President's Asian American advisory commission is pushing to recapture employment-based green cards unused since 1992 — the kind of arithmetic that could shave years off the Indian backlog without Congress raising a single cap.",
        "slug": make_slug("green-card-recapture-bhutoria-advisory-commission-india-backlog"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold the longest employment-based green card queue in the country; recapturing the roughly 230,000 visas that bureaucracy let lapse since 1992 is one of the few levers that could move their priority dates without new legislation.",
        "tags": ["green-card", "eb-2", "eb-3", "recapture", "backlog", "uscis"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — Advisory panel recommends recapturing unused green cards", "url": "https://theindianeye.com/"},
            {"name": "IndiaWest — EB-5 Visa Limit Reached For Indians Until October", "url": "https://www.indiawest.com/"},
            {"name": "Travelobiz — US Stops Issuing EB-2 Green Cards for Indians Until October 2026", "url": "https://travelobiz.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7821472/pexels-photo-7821472.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A US permanent resident card, the document at the center of the employment-based backlog debate.",
        "image_attribution": "Pexels",
        "body": """The most consequential idea in Indian immigration this month did not come from Congress or a courtroom. It came from a recommendation memo.

Ajay Bhutoria, an Indian American who sits on the President's Advisory Commission on Asian Americans, Native Hawaiians and Pacific Islanders, has proposed that the federal government recapture every employment-based green card that went unused between 1992 and 2025 — a stockpile he puts at more than 230,000 visas — and process them in phases, over and above the annual ceiling of 140,000.

It sounds like accounting. For the Indians stuck in the world's longest green card line, it is closer to oxygen.

## How the cards went missing

Congress caps employment-based green cards at 140,000 a year. The catch is that the cap is a ceiling, not a guarantee. In years when consulates were slow, when paperwork jammed, when government shutdowns froze processing, the United States simply failed to hand out all the cards it was legally allowed to issue. Under the way the law has historically been read, those unused numbers do not roll over. They evaporate.

Bhutoria's pitch is to claw them back. The Department of Homeland Security and the State Department, he argues, should recapture the lapsed numbers from 1992 through 2025 and release a slice each fiscal year on top of the normal allotment. The framing matters: this is not amnesty, not a new category, not an expansion of the cap. It is the government collecting visas it already authorized and then wasted.

## Why this lands hardest on Indians

The timing is brutal, which is exactly why the recommendation is getting attention now. The State Department has already exhausted the EB-2 allocation for Indians for fiscal 2026, and as of early June it stopped issuing EB-5 investor green cards to Indian applicants too, with both categories frozen until new numbers arrive on October 1. The latest bulletin still lists India's EB-2 Final Action Date at September 1, 2013 — meaning a worker who filed thirteen years ago is only now near the front.

For a software engineer who landed at SFO in 2019 on an H-1B, the math of the existing system is a quiet life sentence: decades of waiting, children aging out of dependent status, no ability to switch jobs without restarting the clock. A recapture pool would not erase the per-country cap that creates the bottleneck, but it would add real numbers to the categories where Indians are most stacked up. Even a few tens of thousands of extra green cards a year would pull priority dates forward in a way that no amount of patient queuing can.

## The catch in the fine print

Recapture is not a new idea, and that is both its strength and its weakness. Versions of it have been folded into stalled immigration bills for two decades, and a recapture provision is part of at least one green card bill currently floating through Congress aimed at Indian doctors and nurses stuck behind the per-country wall. The appeal of doing it through the advisory commission route is that it frames recapture as an administrative cleanup rather than a legislative fight — something the executive branch might attempt on its own reading of the statute.

Whether it survives that reading is the open question. Recapture done by agency action, without Congress, would almost certainly draw a lawsuit, and the current administration has shown little appetite for expanding legal immigration channels. An advisory commission recommendation is exactly that — advice. It commits no agency to anything.

## What to actually watch

For diaspora families, the signal to track is not the memo itself but whether DHS or the State Department picks it up in any rulemaking, or whether a recapture clause attaches to a moving piece of legislation rather than a dead one. The unused-visa pool is real and the legal authority is at least arguable. The history of recapture, though, is a history of good arithmetic colliding with bad politics.

Until then, the 230,000 cards remain what they have been for thirty years: counted, authorized, and going nowhere. The recommendation is a reminder that the backlog is not a natural disaster. It is a filing error the size of a small country's population — and someone in the building has finally proposed fixing it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The US Trade Chief Lands in Delhi June 23. The One Thing Indians Care About May Not Be on the Table",
        "subheadline": "Jamieson Greer flies in to close an interim trade deal worth hundreds of billions. Tariffs, agriculture and energy dominate the agenda — but the movement of Indian professionals, India's single biggest ask, keeps slipping off it.",
        "slug": make_slug("ustr-greer-india-trade-deal-professional-mobility-h1b-absent"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Every India-US trade round raises diaspora hopes that worker mobility, visa predictability or a totalization deal will finally be bargained in — and every round so far has left them out, leaving H-1B families to depend on courts and proclamations instead of treaty text.",
        "tags": ["india-us-trade", "h1b", "mobility", "totalization", "bilateral", "visas"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — US Trade Representative Greer to visit India on June 23-24 for talks", "url": "https://www.reuters.com/"},
            {"name": "The Hindu BusinessLine — USTR Greer to visit India to finalise interim trade deal", "url": "https://www.thehindubusinessline.com/"},
            {"name": "Livemint — India-US trade deal talks resume next week", "url": "https://www.livemint.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8061944/pexels-photo-8061944.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A US passport and travel documents — worker mobility remains India's chief unmet ask in trade talks.",
        "image_attribution": "Pexels",
        "body": """US Trade Representative Jamieson Greer is due in New Delhi on June 23, with his team landing a day earlier, to put what Indian officials call "final touches" on an interim trade deal that has been inching forward since February. Commerce Minister Piyush Goyal expects the first tranche signed by mid-July. The numbers being thrown around are enormous: a pledge to more than double bilateral trade to $500 billion by 2030, tariffs on Indian goods sliding from a punishing 50% toward 18%, preferential access for Indian exporters over their competitors.

For the Indian diaspora in America, the more revealing detail is what the negotiators are not discussing.

## The agenda Indians can recite by heart

Read the official briefings and the contours are familiar. The US wants market access for industrial and agricultural goods, lower Indian tariffs, more energy purchases. India wants preferential tariff treatment and relief from the threat of fresh levies — including a proposed 12.5% surcharge tied to forced-labor import rules. Agriculture and dairy remain the sore spots. Energy is the sweetener.

Notice the category that does not appear: the movement of people. Services. Professional mobility. The predictability of work visas. These are, by any honest measure, India's largest stake in the relationship — the H-1B pipeline, the Indian IT firms that built their model on rotating engineers through American offices, the students who become workers who become taxpayers. And they sit almost entirely outside the trade text.

## Why mobility keeps falling off the table

There is a structural reason for the omission, and it is worth understanding rather than resenting. In the American system, immigration and trade live in different buildings. A trade deal is negotiated by USTR and ratified or implemented through trade authority; visa numbers and categories are set by Congress and administered by DHS and the State Department. A USTR negotiator cannot promise India more H-1Bs any more than he can promise lower interest rates. The lever simply is not his to pull.

That division is why India's repeated efforts to bundle "mode 4" services — the trade-speak term for sending workers across borders to deliver a service — into trade negotiations have gone nowhere for two decades. Washington treats the supply of foreign labor as a domestic political question, not a tradable concession. New Delhi treats it as the whole point.

## The totalization ghost

Hovering behind all of this is an even older grievance: the absence of a US-India social security totalization agreement. The United States has signed such agreements with 25 countries, sparing their workers from paying into a retirement system they will likely never draw from. India is not one of them. The result is that Indian professionals on temporary visas pour billions into US Social Security through mandatory payroll deductions, then leave without ever qualifying for benefits — an estimated multi-billion-dollar transfer that India has wanted addressed for years.

A totalization deal is, technically, separate from trade. But it is exactly the kind of concrete, dollars-and-cents win for the diaspora that a warming bilateral relationship could in theory deliver. It has not come up in any of the leaks from this round either.

## What the diaspora should take from it

None of this means the trade deal is bad for Indians in America. A stronger India-US economic relationship is, broadly, good for a community that straddles both economies. But it pays to be clear-eyed about what mid-July will and will not produce.

The deal will likely cut tariffs and boost goods trade. It will not make the H-1B lottery less of a casino, will not shorten a single green card queue, and will not refund the Social Security contributions of a departing engineer. For those things, the diaspora remains dependent on the machinery it has been watching all spring — courts striking down fees, proclamations reinstating them, agency memos, and the occasional advisory recommendation.

Greer's visit is a milestone for trade. For the millions of Indians whose American futures hinge on visa policy, it is a reminder that the conversation they most need is happening in a different room — if it is happening at all."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Half of South Asian Adults Now Know Someone Carrying Their Papers Everywhere. That Statistic Should Worry America",
        "subheadline": "A new AAPI Data/AP-NORC poll finds most Asian American adults no longer see the US as a great country for immigrants — and South Asians, more foreign-born than any other group, are feeling the chill most sharply.",
        "slug": make_slug("aapi-poll-south-asians-carrying-documents-immigrant-anxiety"),
        "category": "immigration",
        "vertical": "diaspora-sentiment",
        "diaspora_angle": "South Asians are the most foreign-born slice of Asian America, which is precisely why a climate where even green card holders feel compelled to carry proof of status lands hardest on Indian families — the polling puts hard numbers on an anxiety the community has been describing anecdotally for months.",
        "tags": ["aapi", "south-asian", "immigration", "green-card", "diaspora", "poll"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "AP via Audacy — Most AAPI adults say the US is no longer a great country for immigrants", "url": "https://www.audacy.com/"},
            {"name": "AP via Reflector — How AAPI adults are being affected by Trump's immigration crackdown", "url": "https://www.reflector.com/"},
            {"name": "Associated Press — AAPI adults think Trump has done more harm than good on immigration", "url": "https://www.ap.org/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6963039/pexels-photo-6963039.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A family reviews paperwork at home — documentation anxiety has spread to immigrants with legal status.",
        "image_attribution": "Pexels",
        "body": """Here is a number that does not show up in any visa bulletin. About half of South Asian adults in the United States now say they know someone who, over the past year, started carrying proof of legal status or citizenship with them — wallet documentation, green cards treated like a second driver's license, just in case.

That figure, from a new AAPI Data and AP-NORC survey, runs well ahead of the roughly four in ten across Asian Americans as a whole. And it captures something the immigration debate usually misses: the people most rattled by the current climate are often not the undocumented. They are the legal permanent residents and naturalized citizens who did everything the system asked and still feel watched.

## The poll's leading edge

The survey's headline finding is bleak enough on its own — most AAPI adults no longer believe the United States is a great country for immigrants, a sentiment Karthick Ramakrishnan, the executive director of AAPI Data, calls "a warning sign" coming from a group that has historically bought into the American immigrant story more than most.

But it is the documentation detail that should resonate in Indian American households. South Asians are, the survey notes, far more likely to be foreign-born than East Asian or Southeast Asian Americans. That demographic fact is usually framed as a strength — the freshness of the immigrant drive, the density of first-generation strivers. In the current environment it doubles as exposure. When a larger share of your community arrived on a plane rather than in a delivery room, a larger share of your community has a status, a stamp, a card that can theoretically be questioned.

Many of those people, Ramakrishnan notes, already hold green cards or are naturalized citizens. They are, legally, as American as anyone. They are carrying their papers anyway, because the feeling — that "their presence and their status in this country is under question" — does not check immigration files before it sets in.

## Why legal status stopped feeling like safety

The anxiety is not free-floating. It has been fed by a year of policy whiplash that this publication has tracked story by story: a $100,000 H-1B fee struck down by a federal judge and then reinstated days later, a policy that would have barred immigrants from dozens of Asian and African countries from final decisions on green cards and work permits before a court blocked it, intensified consular vetting that now combs applicants' social media. Each individual fight may end in the immigrant's favor. The cumulative effect is a sense that the ground can shift under your feet regardless of which document you hold.

For Indian families, the texture is specific. International students putting off trips home to see parents because they are unsure they will be let back in. Spouses on H-4 status watching the EAD program that lets them work drift toward rescission. Parents on green cards quietly photographing their documents in case the original is ever demanded. None of this is illegal behavior responding to enforcement. It is lawful residents managing dread.

## The cost of a chilled welcome

There is a hard-headed argument buried in the soft data, and Indian Americans of all people are positioned to make it. This is the most highly educated, highest-earning immigrant group in the country, overrepresented in medicine, technology and entrepreneurship. A separate Pew study this spring found that a third of Indian adults in the US would consider moving to India, with recent arrivals far likelier to say so than long-settled ones.

Put those two findings side by side and the warning sharpens. The community most capable of leaving is also the one most recently arrived, most foreign-born, and now most likely to feel unwelcome. A country that makes its green card holders carry their papers out of fear is not just bruising feelings. It is testing the patience of exactly the people it spent a generation competing to attract.

The poll does not predict an exodus. Sentiment is not a suitcase. But it does measure, in plain numbers, how much the welcome has cooled — and which community is feeling the draft first."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n{len(inserted)}/{len(articles)} inserted")
