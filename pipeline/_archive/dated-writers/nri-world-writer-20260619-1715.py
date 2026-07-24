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

body1 = """The phone calls started within hours. By the morning of June 18th, relationship managers at India's largest banks were fielding the same request, over and over, from non-resident clients in Dubai, New Jersey and Singapore: can I close my old dollar deposit and open a new one at the higher rate?

For most of the past decade, a Foreign Currency Non-Resident (Bank) deposit — an FCNR(B), in the alphabet soup of NRI banking — was a sleepy instrument. You parked dollars or pounds in an Indian bank, earned a little over 3%, and avoided any exposure to the rupee's long slide. Safe, dull, forgettable. That changed on June 17th, when the Reserve Bank of India temporarily scrapped the interest-rate ceiling on fresh FCNR(B) deposits of three-to-five-year tenor, and on Non-Resident External (NRE) rupee deposits of three years and above. Banks responded almost immediately, lifting dollar deposit rates into the 6% to 7.1% range — roughly double what was on offer a week earlier.

## Why Delhi suddenly wants your dollars

The move is not generosity; it is arithmetic. The rupee has been under pressure from elevated crude prices and jittery global markets, and the RBI is hunting for foreign-currency inflows to shore up reserves and steady the currency. The central bank has pulled this lever before. The FCNR(B) framework was last deployed aggressively during the 2013 "taper tantrum," when a special swap window drew in some $34 billion almost overnight. This time, bankers cited in the Indian press estimate the new measures could pull in anywhere from $50 billion to $70 billion before the window shuts on September 30th.

Crucially, the RBI is also bearing the cost of currency hedging through a concessional swap facility announced on June 5th. That is what lets banks offer 7% on dollar deposits without taking a bath on their own books — the central bank, in effect, is subsidising the courtship of diaspora savings.

## The catch for existing depositors

For NRIs already holding FCNR(B) money, the new rates are maddeningly out of reach. The RBI's relaxation applies only to fresh deposits and to deposits renewed on maturity during the window. An existing three-year deposit booked last year at 3.35% keeps earning 3.35%. That asymmetry is precisely what set off the scramble.

Several banks have now formally asked the RBI for permission to let existing customers prematurely break and rebook their deposits under the new framework, according to a report in The Economic Times. Until regulators clarify, depositors face a familiar trade-off: premature withdrawal usually carries a penalty and forfeited interest, which may or may not be worth swallowing to lock in a rate two-to-three points higher for the next several years.

One more line of fine print matters for the diaspora's tax planners: transfers from an NRO account — where rupee income earned in India is parked — into an NRE account will not qualify for the exemption. The incentive is aimed squarely at fresh foreign currency arriving from abroad, not at reshuffling money already inside the country.

## What it means for the diaspora

For the roughly 35 million people of Indian origin living overseas, this is one of those moments when the macro and the personal collide. Remittances and deposits from the diaspora are not charity to the old country; they are a quietly load-bearing pillar of India's external accounts. When the rupee wobbles, Delhi reaches, almost reflexively, for the savings of its citizens abroad.

For the individual NRI, the calculus is less patriotic and more practical. A 7% dollar return, unhedged against rupee risk, is a genuinely attractive yield in a world where American money-market funds pay around 4% and falling. For three-to-five-year horizons — a child's future tuition, a planned return to India, a retirement corpus — the math is suddenly compelling. The risk is concentration: betting on the stability of one banking system, in one country, for one currency.

The window is the point. It closes on September 30th, and the RBI has given no signal it will extend. Whatever the diaspora decides — break and rebook, wait for regulatory clarity, or sit tight — the decision has a deadline. For a community long used to thinking of Indian deposits as a sentimental tether rather than a sharp financial instrument, the next hundred days are a reminder that the tether occasionally pays interest."""

body2 = """On the weekend of June 19th, the Greater Philadelphia Expo Center at Oaks, Pennsylvania, will fill with the sound of a community that refuses to assimilate quietly. Thousands of Telugu families from across the United States are converging for the second Mana American Telugu Association (MATA) convention — two days of devotional ceremony, film-star cameos, business forums and a grand finale concert by the composer Devi Sri Prasad. It is, on paper, a cultural festival. It is also a census of one of America's most organised diaspora sub-communities.

## A language, exported

The Telugu-speaking diaspora is a study in how granular Indian identity abroad has become. Indians in America are not a monolith; they fracture, productively, along the same linguistic lines that define India itself. Telugus — from the states of Andhra Pradesh and Telangana — have built a dense web of overlapping national bodies: TANA, founded in 1977 and among the oldest Indo-American organisations; the American Telugu Association; the Telangana American Telugu Association; and now MATA, the newest entrant, built around the slogan "Seva, Samskruthi, Samanathvam" — service, culture, equality.

That so many bodies can each draw thousands of attendees says something about scale. TANA's biennial convention in Dallas earlier this year expected some 10,000 visitors. The American Telugu Association has booked the Baltimore Convention Center for late July. TTA's mega-convention lands in Charlotte in mid-July. For a single linguistic community to sustain four competing national conventions in one summer is not fragmentation so much as abundance.

## More than nostalgia

It would be easy to dismiss these gatherings as nostalgia theatre — sari stalls, kalyanam ceremonies, a Tollywood playback singer flown in for the banquet. That misreads them. The conventions have become functional infrastructure for a community managing the practical business of living between two worlds.

The programmes tell the story. Alongside the Sri Bhadradri Sita Rama Kalyanam ceremony and the celebrity appearances, MATA's schedule lists business and startup forums, immigration sessions, and youth, women and leadership tracks. The American Telugu Association has paired its convention work with SAT-prep courses, IT training, startup competitions across six cities, and seminars for small businesses and women entrepreneurs in non-IT sectors. These are not afterthoughts bolted onto a party; for many attendees they are the reason to come.

## The second-generation problem

The deeper anxiety running beneath the music is generational. The founders of these associations arrived in the 1970s and 1980s, often as engineers and doctors, and built community from scratch. Their children, raised on American soil, speak Telugu unevenly and feel the pull of the homeland more faintly. Every convention now wrestles, explicitly, with the question of whether the language and its rituals survive the handover.

That is why the youth showcases and the kalyanam ceremonies share a stage with the matrimony desks and networking lounges. The conventions are an attempt to make heritage legible — and appealing — to teenagers who have never lived in Hyderabad and may never want to. Gregory Hancock Dance Theatre, a non-Indian American troupe, is performing a piece titled "Celebrating Telugu Legacy in America" at a rival convention this summer; the symbolism, of an outside company interpreting the diaspora's heritage back to it, is hard to miss.

## Soft power, retail edition

For the Indian state, these gatherings are a gift. Consulates send deputy consuls-general to keynote them; ministers route through them on US visits. The diaspora's appetite for organised cultural expression doubles as the most efficient soft-power channel India possesses, requiring no government budget and reaching directly into the living rooms of affluent, politically engaged Indian-Americans.

But the conventions belong to the community, not the state. They are built by volunteers, funded by ticket sales and local sponsors, and animated by a stubborn refusal to let a language spoken by 80 million people in India thin out to nothing among a few hundred thousand in America. On the weekend of June 19th in suburban Philadelphia, that refusal will look, sound and taste like a celebration. Underneath, it is something closer to maintenance work — the unglamorous, recurring labour of keeping an identity alive a long way from home."""

body3 = """India has decided that its 35 million emigrants are not merely a source of remittances and reflected glory. They are a sales force. In a cluster of overlapping campaigns rolled out this month, New Delhi and its corporate partners are recasting the diaspora as the country's most credible tourism marketers — unpaid, emotionally invested, and embedded in precisely the affluent foreign markets India wants to reach.

## "Bring five friends"

The centrepiece is the "Chalo India Global Diaspora Campaign," launched by Prime Minister Narendra Modi with a deceptively simple ask: every overseas Indian should persuade five non-Indian friends to visit India. A dedicated website lets diaspora members register and, in effect, enlist. The pitch leans on a real asset — the diaspora's social capital. An Indian-origin colleague in London or Toronto vouching for a trip to Rajasthan is worth more than any glossy tourism-board advertisement, and India knows it.

The campaign has been paired with a 1,400-crore-rupee programme of 52 tourism projects under the Swadesh Darshan scheme, and with parallel diaspora outreach abroad. The High Commission of India in London has flagged off two initiatives at once: "Chalo India" to drive tourism, and "Living Bridges" to celebrate the contributions of people of Indian origin to British life.

## The corporate arm

Where the government supplies the rhetoric, industry supplies the funnel. MakeMyTrip, India's largest online travel company, has launched "India: The Homecoming," a campaign explicitly aimed at the diaspora and built atop a platform now accessible in more than 150 countries, including Britain, Germany, Japan and France. Rajesh Magow, the company's group chief executive, framed it as an effort to "reignite pride and nostalgia among Indians abroad" — and, not incidentally, to route their bookings through his platform, now offering multiple currencies and coverage of more than 2,000 Indian cities.

The commercial logic is plain. The diaspora travels to India anyway, for weddings, funerals and family obligations that no marketing campaign created. Capturing those bookings, and then nudging the traveller toward an extra few days of leisure tourism — and toward bringing along non-Indian friends — is found money for an industry recovering its footing.

## Why the diaspora is the ideal target

There is a cold demographic sense to all this. The Indian diaspora is the largest in the world, disproportionately wealthy, and concentrated in high-spending source markets. It needs no persuading that India is worth visiting; the homeland connection does the heavy lifting. What it can be persuaded to do is convert latent affection into bookings, and to act as a trust broker for first-time foreign visitors who might otherwise be deterred by India's reputation for chaos.

Philanthropy follows a similar pattern. India Giving Day 2026 raised $5.6 million through a diaspora-focused #PowerOfUs campaign, with more than 65 events across the United States. The machinery being built for tourism — the registries, the chapter networks, the consular events — is the same machinery that mobilises diaspora money for causes back home. The diaspora is being asked, gently and repeatedly, to be both ambassador and donor.

## The ambivalence underneath

For the diaspora itself, the campaigns land in complicated emotional territory. The pitch flatters — you are India's best face to the world — while quietly instrumentalising a relationship that many emigrants experience as private and unresolved. Not every NRI wants to be a brand ambassador for a homeland they left, sometimes for reasons that were not entirely nostalgic.

There is also the question of what India is selling. "Living Bridges" celebrates diaspora contributions abroad; "Chalo India" asks the diaspora to sell India to outsiders. Both rest on an image of a confident, rising country that the diaspora is invited to co-author. For Indians abroad navigating their own dual identities — neither fully here nor fully there — being cast as the nation's narrator is a role that comes with weight as well as flattery.

Whether the campaigns move the needle on visitor numbers will not be clear for months. What is already clear is the strategic bet underneath them: that the most valuable thing India's diaspora exports is not money, but credibility — and that credibility, unlike a remittance, can be spent again and again."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Doubled the Rate on NRI Dollar Deposits. Now the Diaspora Is Racing to Break Its Old Ones.",
        "subheadline": "The RBI has lifted rate caps on fresh NRE and FCNR(B) deposits until September 30th, pushing dollar yields to 7%. Existing depositors are stuck at the old rates — and scrambling to rebook.",
        "slug": make_slug("nri-fcnr-deposits-rate-cap-break-rebook-scramble"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Millions of NRIs hold dollar and rupee deposits in Indian banks; the RBI's temporary rate-cap removal turns a sleepy savings instrument into a time-limited 7% opportunity — but only for fresh money, forcing existing depositors to weigh premature-withdrawal penalties before the September 30th window shuts.",
        "tags": ["nri", "diaspora", "fcnr", "nre-deposits", "rbi", "nri-banking", "remittances"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Business — Why NRIs Are Rushing to Break Old Deposits", "url": "https://www.outlookbusiness.com/"},
            {"name": "The Hindu BusinessLine — RBI withdraws FCNR(B) rate ceiling", "url": "https://www.thehindubusinessline.com/"},
            {"name": "CAclubindia — RBI Removes Interest Rate Caps on NRE and FCNR(B) Deposits", "url": "https://www.caclubindia.com/"},
            {"name": "Outlook Money — RBI Removes Rate Caps On Select NRI Deposits Till September 30", "url": "https://www.outlookmoney.com/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/14907377/pexels-photo-14907377.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Indian rupee banknotes; the RBI has temporarily lifted interest-rate caps on NRE and FCNR(B) deposits to draw foreign-currency inflows.",
        "image_attribution": "Pexels",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Four Telugu Conventions in One Summer: How a Language Spoken 8,000 Miles Away Refuses to Fade in America",
        "subheadline": "Thousands of Telugu families gather near Philadelphia this weekend for the MATA convention — one of four rival national gatherings this summer, and a working census of one of America's most organised diaspora communities.",
        "slug": make_slug("mata-telugu-convention-philadelphia-diaspora-language-survival"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Telugu-American community sustains four competing national conventions in a single summer — a feat of organisation driven by a generational anxiety over whether language, ritual and identity survive the handover to children raised entirely on American soil.",
        "tags": ["nri", "diaspora", "telugu", "mata", "tana", "community", "cultural-festival", "indian-american"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "MATA 2nd Convention 2026 — Official Promo (Philadelphia, June 19-20)", "url": "https://www.youtube.com/"},
            {"name": "South Asian Herald — American Telugu Association Picks Baltimore for 2026 Convention", "url": "https://southasianherald.com/"},
            {"name": "TeluguOne — 19th TANA Convention Advanced Registration Opened", "url": "https://www.teluguone.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/35736415/pexels-photo-35736415.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An Indian classical dancer in performance; Telugu-American conventions pair cultural showcases with business, immigration and youth forums.",
        "image_attribution": "Pexels",
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Has a New Job for Its 35 Million Emigrants: Sell the Country to Their Foreign Friends",
        "subheadline": "From Modi's 'Chalo India' campaign to MakeMyTrip's 'India: The Homecoming,' New Delhi is recasting the diaspora as an unpaid, emotionally invested tourism sales force. The flattery comes with weight.",
        "slug": make_slug("chalo-india-diaspora-tourism-ambassadors-makemytrip-homecoming"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "A cluster of government and corporate campaigns is asking overseas Indians to convert homeland affection into tourism bookings and to act as trust brokers persuading non-Indian friends to visit — instrumentalising a relationship many emigrants experience as private and unresolved.",
        "tags": ["nri", "diaspora", "chalo-india", "tourism", "makemytrip", "soft-power", "modi"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian EYE — PM Modi launches 'Chalo India Global Diaspora Campaign'", "url": "https://theindianeye.com/"},
            {"name": "IndianDiaspora.org — MakeMyTrip and Tourism Ministry Launch 'India: The Homecoming'", "url": "https://www.indiandiaspora.org/"},
            {"name": "South Asian Herald — India Giving Day 2026 Raises $5.6 Million", "url": "https://southasianherald.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17423832/pexels-photo-17423832.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The Taj Mahal at Agra; India's tourism campaigns are enlisting the diaspora to bring non-Indian friends to visit.",
        "image_attribution": "Pexels",
        "body": body3
    }
]

for art in articles:
    wc = len(art["body"].split())
    if wc < 400:
        print(f"⚠️  {art['slug']}: only {wc} words — skipping")
        continue
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
