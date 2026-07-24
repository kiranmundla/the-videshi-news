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
        "headline": "India Just Doubled the Equity Limit for Every NRI Investor. The Real Target Is the $40 Billion Gap.",
        "subheadline": "The RBI raised individual NRI investment caps from 5 to 10 per cent and opened the same door to all overseas Indians for the first time, part of a coordinated blitz to shore up the rupee.",
        "slug": make_slug("rbi-doubles-nri-oci-equity-investment-limit-pis"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "NRIs and OCIs who invest in Indian equities through the Portfolio Investment Scheme just had their individual caps doubled. For the first time, any overseas Indian — not just NRIs and OCIs — can buy listed Indian shares through PIS. This changes the calculus for every diaspora investor with an Indian brokerage account.",
        "tags": ["nri", "diaspora", "rbi", "investment", "equities", "oci", "pis"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/invest/rbi-proposes-higher-investment-limits-in-equity-instruments-for-nris-ocis-and-other-overseas-indians"},
            {"name": "IANS Live", "url": "https://ianslive.in"},
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/law-order/3354001-india-opens-wider-door-for-foreign-investment-in-markets"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/da/Sanjay_Malhotra_RBI.jpg",
        "image_caption": "RBI Governor Sanjay Malhotra at a press conference in Mumbai",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """On the same morning that global markets were digesting the latest fallout from the West Asia conflict, India's central bank quietly rewired the investment plumbing for 35 million overseas Indians.

RBI Governor Sanjay Malhotra, wrapping up the Monetary Policy Committee's June meeting on Friday, announced that individual NRI and OCI investment limits in listed Indian equities would be raised from 5 per cent to 10 per cent of a company's paid-up capital. The aggregate cap for all NRIs in a single company jumps from 10 per cent to 24 per cent. And for the first time, the same Portfolio Investment Scheme route — previously reserved for NRIs and Overseas Citizens of India — would be thrown open to all Persons Resident Outside India.

The numbers matter, but the signal matters more. India is not tweaking a regulation. It is asking its diaspora to help plug a $40-to-50 billion hole in the balance of payments.

## What changed, exactly

Under the old rules, an individual NRI or OCI could hold up to 5 per cent of a listed Indian company's equity through the PIS route — a dedicated channel that lets overseas Indians buy and sell shares on Indian exchanges without registering with SEBI. The aggregate ceiling for all NRIs combined stood at 10 per cent, though companies could raise it to 24 per cent by passing a special resolution.

Friday's changes, notified simultaneously by the RBI and the Finance Ministry through the Foreign Exchange Management (Non-Debt Instruments) (Third Amendment) Rules, 2026, double the individual limit to 10 per cent and automatically raise the aggregate to 24 per cent. More significantly, Individual Persons Resident Outside India — a broader category that includes people of non-Indian origin living abroad — now get access to PIS at par with NRIs and OCIs.

"The reform has a way of boosting currency reserves while giving Indians an opportunity to participate in the growth of the nation," said Vivek Iyer, Partner and Financial Risk Advisory Leader at Grant Thornton Bharat. He expects increased capital inflows within two months.

## The bigger package

The equity liberalisation was one piece of a coordinated Friday blitz. The Finance Ministry separately scrapped long-term capital gains tax on foreign institutional investments in government securities through an Ordinance. The RBI expanded the basket of "specified securities" under the Fully Accessible Route — the channel that lets overseas investors buy certain government bonds without any cap — to include all new 15-, 30-, and 40-year issuances. Concentration limits and short-term investment caps for foreign portfolio investors under the General Route were removed entirely.

Add in a concessional forex swap facility for public-sector external commercial borrowings, a similar hedging-cost subsidy for banks raising FCNR(B) deposits, and the restoration of the nine-month window for export proceeds realisation, and the message is clear: India wants dollars, and it wants them now.

Reuters reported analysts at HDFC Bank estimating the combined measures could help bridge a $40-to-50 billion gap on the balance of payments estimated for FY27. Union Bank of India's chief economic adviser Kanika Pasricha put the minimum at $30 billion over four months, with "chances of a large upside."

## What it means for NRI investors

For the typical NRI investor in Houston or London or Dubai with an Indian brokerage account, the immediate change is headroom. The old 5 per cent cap occasionally bit — particularly in mid-cap companies where a handful of NRI investors could collectively approach the 10 per cent aggregate ceiling, triggering a freeze on new purchases.

The new structure doubles that space and, critically, removes the need for a company's general body to pass a special resolution before the 24 per cent aggregate applies. That resolution requirement, while rarely denied, added bureaucratic friction that deterred some institutional-scale NRI investors.

"Reduced compliance burden and quicker onboarding procedure should promote greater involvement from NRIs and OCIs," said Anand K Rathi, Co-Founder of MIRA Money. "The revamped structure also offers a more simple method for foreign individual investors to acquire Indian shares, which might expand the investor base."

## The rupee context

None of this is happening in a vacuum. The rupee has been under sustained pressure from elevated crude oil prices driven by the West Asia conflict. As the world's third-largest oil importer, India's trade deficit widens when crude spikes, and the resulting demand for dollars pushes the currency lower. The RBI has been intervening in the forex market to smooth volatility, but intervention depletes reserves.

NRI and OCI investors offer something that hot-money FII flows do not: patient capital. "FII flows can sometimes be very sharp and tactical," said Ajay Kumar Yadav, Group CEO at Wise Finserv. "But NRI and OCI investors often have an emotional and financial connection with India. Many of them invest with a longer-term mindset. This type of patient capital can act as a useful support for Indian markets over time."

Whether the diaspora responds with the kind of capital flow India needs remains to be seen. But the door is wider than it has ever been, and the welcome mat has been rolled out in a way that suggests New Delhi knows exactly who it is hoping walks through it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Four Players of Indian Origin Will Take the Pitch at the FIFA World Cup. India Still Won't Be There.",
        "subheadline": "A Keralite teenager in Qatar's squad, a Sikh midfielder who played for Bayern Munich, a Tamil-heritage winger from Melbourne, and a Nantes veteran with Indian roots in the DR Congo shirt — the diaspora's football footprint has never been larger.",
        "slug": make_slug("indian-origin-footballers-fifa-world-cup-2026"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For diaspora Indians who grew up playing football in suburban American and European leagues while being told the sport had no future for people who looked like them, these four players represent something the AIFF's ranking never could: proof of concept.",
        "tags": ["nri", "diaspora", "football", "fifa", "world-cup", "sports"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "RevSportz", "url": "https://revsportz.in/from-kerala-to-north-america-indian-origin-footballers-set-to-grace-the-fifa-world-cup-2026/"},
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/who-are-the-4-indianorigin-players-in-fifa-world-cup-2026"},
            {"name": "SRK Nation Sports", "url": "https://srknationsports.com/indian-diaspora-poised-for-historic-representation-at-fifa-world-cup-2026/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/bd/Sarpreet_Singh_Training_2019-07-28_FC_Bayern_Munich.png",
        "image_caption": "Sarpreet Singh during training with FC Bayern Munich in 2019",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """When the 2026 FIFA World Cup kicks off in North America on June 11, four players with roots tracing back to the Indian subcontinent will be in the squads. It is the most Indian-origin representation the tournament has ever seen, and the first time any have appeared since Vikash Dhorasoo wore the French shirt in Germany twenty years ago.

Their stories stretch from Thalassery to Toronto, from the Aspire Academy in Doha to the youth pitches of Melbourne. None of them play for India. That, depending on how you look at it, is either the point or the problem.

## Tahsin Mohammed — Qatar

The most compelling narrative belongs to the youngest of the four. Tahsin Mohammed is 19 years old, born and raised in Qatar to Keralite parents. His father, Jamshid, played football at Calicut University and hails from Thalassery. His mother, Shaima, comes from Valapattanam in Kannur district.

Tahsin came up through the Aspire Academy — Qatar's state-funded talent factory — before progressing to Al-Duhail in the Qatar Stars League. At 17, he became the first player of Indian origin to feature in the league. His trajectory through Qatar's youth setup earned him a place in Julen Lopetegui's 26-man senior squad for the World Cup.

Qatar are drawn in Group B alongside Switzerland, Canada, and Bosnia and Herzegovina. Among Indian football communities on social media, Tahsin is already the most closely tracked player at the tournament.

## Sarpreet Singh — New Zealand

Sarpreet Singh needs less introduction. The New Zealand midfielder, born to a Sikh family of Indian descent, made headlines in 2019 when he signed for Bayern Munich, becoming the first player of Indian ancestry to appear in the Bundesliga.

His career since has traced an arc through Germany, Portugal, and Serbia before a loan spell back at Wellington Phoenix in the A-League. A serious knee injury during a league match this year threatened to end his World Cup hopes. Weeks of rehabilitation and a race against the selection deadline followed. He made it.

Singh is 27 now, his Bayern days behind him, but his name still carries weight in a community that treats every diaspora achievement in European football as evidence that the ceiling can be broken.

## Nishan Velupillay — Australia

Nishan Velupillay is 25, a winger at Melbourne Victory, and the first footballer of Tamil heritage to reach the FIFA World Cup. His father, Sasinath, has Tamil roots; his mother, Gillian, is Anglo-Indian.

Velupillay's international breakthrough came in October 2024 when he scored on his debut for Australia against China in a World Cup qualifier. Three more qualifying goals followed. Under Tony Popovic, he has become a trusted option on the wing, and he will face Turkey, the United States, and Paraguay in Group D.

For Tamil diaspora communities across South-East Asia, Australia, and North America, Velupillay's inclusion carries a particular resonance. Tamil Nadu has a domestic football culture that never scaled; seeing a player of Tamil heritage at the World Cup, wearing the Socceroos shirt, lands differently than another cricket statistic.

## Samuel Moutoussamy — DR Congo

The fourth player with Indian heritage is Samuel Moutoussamy, a 29-year-old defensive midfielder named in the Democratic Republic of Congo's squad. Born in France, Moutoussamy has family links to India through his broader heritage.

He is the most experienced of the four. Over 140 appearances for Nantes, including a Coupe de France winner's medal in 2021-22, and more than 50 international caps for DR Congo. He is expected to play a key role in midfield when the Leopards open their World Cup against Portugal.

## What this means — and what it does not

Shashi Tharoor, the Congress MP who rarely misses a chance to comment on diaspora milestones, called their inclusion "a proud moment for football fans of Indian descent worldwide." He is not wrong. But the compliment contains its own sting.

India's national team, ranked 126th in the world by FIFA, has never come close to qualifying for a World Cup. The All India Football Federation's development pipeline has produced exactly zero players capable of competing at this level in the modern era. The diaspora's four World Cup representatives developed in Qatar, New Zealand, Australia, and France — not in India.

The tension is real: these players are proof that Indian-origin athletes can thrive at the highest level when placed in competent developmental ecosystems. Their success is a testament to the footballing infrastructure of their adopted countries and a quiet indictment of the one they are connected to by blood.

For now, Indian football fans will do what they have always done — adopt borrowed heroes and cheer from a distance. The difference, this time, is that the heroes share their last names."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
