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

body1 = """The most striking thing about the gathering in the House of Lords on 19 June was not the speeches. It was the venue. The NRI Association of UK had managed to convene parliamentarians, diplomats, business chiefs and community organisers in the upper chamber of the British Parliament to talk about India's economic plans for 2047 — and nobody in the room seemed to find that arrangement strange.

That, in a sentence, is how far the Indian diaspora in Britain has travelled.

The forum carried the title "Viksit Bharat 2047", borrowing the slogan that frames New Delhi's ambition to become a developed economy by the centenary of independence. For a domestic Indian audience the phrase is political wallpaper. Exported to Westminster, it became something else: a hook on which the diaspora could hang its own argument about where it fits between two countries.

## The "living bridge", again

Speakers including Lord Rami Ranger, Lord Graham Brady and Meenakshi Singh returned repeatedly to a now-familiar metaphor — the diaspora as a "living bridge" between India and the United Kingdom. The phrase has been doing heavy lifting in Anglo-Indian diplomacy for years, and there is a reason it survives. It flatters both governments while committing neither to anything specific.

But the bridge talk lands differently in mid-2026, because there is finally freight to carry across it. The proposed India–UK free trade agreement, long stalled and frequently declared imminent, hovered over the entire evening. A deal that lowers tariffs and loosens services trade would turn the diaspora's networks — its lawyers, its mid-market exporters, its second-generation founders — from sentimental assets into commercial ones.

## Why the address matters

It is easy to be cynical about an evening of mutual congratulation in a wood-panelled room. Most diaspora events are, by design, inward-facing: a regional association's gala, a temple anniversary, a community awards night where the community talks to itself.

The Lords forum was the opposite. It was staged in an institution of the British state, attended by people who make British law, and pitched around a question — India's development trajectory — that is fundamentally about money and influence rather than nostalgia. For a community whose grandparents arrived to work in foundries and corner shops, holding court in Parliament about a $5-trillion-plus economy is not a small symbolic shift.

The British-Indian population is now routinely cited as the country's most economically successful ethnic minority, a point made bluntly in a Policy Exchange report this month. Events like the Viksit Bharat forum are where that statistical success starts converting into political voice.

## The catch in the bridge metaphor

There is a tension the evening's warm rhetoric mostly avoided. A "living bridge" implies traffic flowing both ways, but the diaspora's relationship with India has grown more complicated than the brochures admit. Younger British Indians, born and raised in Birmingham or Leicester, increasingly experience India as a country they visit rather than one they are from. Their attachment is real but conditional, and it is not obvious that "Viksit Bharat 2047" — a vision they will witness largely from abroad — speaks to them the way it speaks to their parents.

New Delhi understands the stakes. The government has spent two decades building diaspora-engagement machinery, from the Pravasi Bharatiya Divas conventions to OCI cards to investment schemes aimed squarely at non-resident wallets. The Lords forum was, in part, that same outreach conducted on British soil and in British institutions.

## What's next

The immediate test is the FTA. If it is signed and the diaspora's businesses see tangible gains — easier movement of professionals, lower friction for exporters, recognition of qualifications — the "living bridge" stops being a metaphor and becomes infrastructure. If the deal slips again, the forum will be remembered as one more pleasant evening of speeches.

For Britain's Indians, the more durable shift may be internal. A community that once asked to be included is now hosting the conversation. Whether the destination is Viksit Bharat or simply a more confident place in British public life, the diaspora has decided it is done waiting at the gate.

**Sources:** GKToday; Srishti IAS; *The Indian Eye*."""

body2 = """For years the standard advice to non-resident Indians sitting on dollars was unglamorous: park the money abroad, where it earns something, rather than in India, where rupee deposits get eaten by currency risk. In June 2026 the calculus quietly flipped.

Bandhan Bank announced on 20 June that it would pay 7.1% on foreign-currency non-resident — FCNR(B) — deposits of $1 million and above for tenures of three to five years, and 7% on smaller sums. Those are dollar-denominated returns, with no rupee exposure, at rates that would have looked fanciful a year ago. Bandhan will not be the last bank to move.

## The policy behind the rate

The rate war is not an accident of competition. It is engineered.

Earlier this month the Reserve Bank of India revived a dollar-rupee forex swap facility for banks on fresh FCNR(B) deposits raised for three to five years — effectively subsidising the cost banks incur to hedge the currency risk on those dollars. The last time the RBI reached for this tool was 2013, during the "taper tantrum", when a collapsing rupee forced New Delhi to lure diaspora money home in a hurry.

The mechanics are deliberately attractive. Banks offer loans to NRIs, who then park the borrowed funds in dollar deposits with Indian lenders, amplifying the inflow. Brokerage Nomura estimates the scheme could pull in around $55 billion, with the bulk arriving in August and September. "Compared to 2013, while U.S. dollar rates are much higher, the scheme will also provide leverage to investors, which will boost returns," Nomura noted.

## Why now

The backdrop is a rupee that touched an all-time low near 97 to the dollar last month before recovering to about 94.50 as oil prices slid. India's foreign-exchange reserves have fallen from a March peak of $728.5 billion to $681.6 billion, and the RBI's short-dollar forward book has ballooned to nearly $110 billion. In plain terms: the central bank wants dollars, and the 35-million-strong diaspora is the cheapest place to find them.

A Bank of Baroda report this month confirmed the strategy is working at the margins — NRI deposit growth is reviving through the FCNR(B) route, while NRO accounts are growing fastest of all the non-resident categories.

## The fine print NRIs should read

A 7% dollar return is genuinely good. But the diaspora has been burned before by chasing headline rates, and three points deserve attention.

First, the top rate applies to deposits of $1 million and above; smaller savers get 7%, still strong but not the advertised number. Second, FCNR(B) deposits lock money up for three to five years — the currency protection comes at the price of liquidity. Third, tax treatment differs sharply by account type. FCNR(B) interest is generally tax-free in India for those who qualify as non-resident, but NRO income is taxable and subject to TDS, and US-based depositors must still reckon with FATCA and FBAR reporting on the underlying accounts regardless of how India treats them.

There is also a structural wrinkle. Banks with branches in GIFT City, India's tax-neutral finance hub, are lobbying the RBI to let those units offer the leverage loans that make the scheme so lucrative. Many Indian banks have a GIFT City presence but no foreign branches, and if leverage cannot flow through GIFT, they will have to lean on foreign lenders instead. The plumbing is still being built even as the marketing begins.

## What's next

Expect a procession of banks to match or beat Bandhan's 7.1% over the coming weeks, and expect relationship managers across the Gulf, the US and the UK to start calling. The RBI's $55-billion target is, in effect, a fundraising drive aimed at the diaspora's savings.

For NRIs, the opportunity is real but narrow. The sweet spot is money you can genuinely lock away for three years, held by someone who has read the tax treaty rather than just the rate sheet. The dollars India wants are the diaspora's to lend — at a price that, for once, is being set in the depositor's favour.

**Sources:** Tripura Star News; Reuters; *The Indian Eye* (Bank of Baroda report)."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Diaspora Used to Ask Britain to Let It In. This Week It Hosted the Conversation in the House of Lords.",
        "subheadline": "A 'Viksit Bharat 2047' forum in Parliament's upper chamber showed how far Britain's Indians have travelled — and how much now rides on a trade deal that keeps slipping.",
        "slug": make_slug("viksit-bharat-2047-house-of-lords-nri-association-uk-diaspora-living-bridge"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Britain's Indian community is now its most economically successful minority; an event in the House of Lords about India's 2047 vision marks the moment that success starts converting into political voice — with the stalled India-UK FTA the real test of whether the 'living bridge' becomes infrastructure.",
        "tags": ["nri", "diaspora", "uk", "house-of-lords", "viksit-bharat", "india-uk-fta"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "GKToday", "url": "https://www.gktoday.in/house-of-lords-hosts-viksit-bharat-2047-forum/"},
            {"name": "Srishti IAS", "url": "https://srishtiias.com/"},
            {"name": "The Indian Eye", "url": "https://www.theindianeye.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/House_of_Lords_2011.jpg/1280px-House_of_Lords_2011.jpg",
        "image_caption": "The House of Lords chamber in the Palace of Westminster, London",
        "image_attribution": "Wikimedia Commons",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Wants the Diaspora's Dollars Back. It's Offering 7.1% — and a $55 Billion Bet — to Get Them.",
        "subheadline": "A revived RBI swap scheme has touched off an FCNR deposit rate war. For NRIs the returns are real, but the fine print on lock-ins and tax is where the deal is won or lost.",
        "slug": make_slug("nri-fcnr-deposit-rate-war-rbi-forex-swap-55-billion-diaspora-dollars"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The RBI's FCNR(B) swap subsidy is, in effect, a fundraising drive aimed squarely at the 35-million-strong diaspora's savings — offering tax-advantaged dollar returns up to 7.1%, but with three-to-five-year lock-ins and FATCA/FBAR/TDS complications that NRIs must weigh before chasing the headline rate.",
        "tags": ["nri", "diaspora", "fcnr", "nre-nro", "rbi", "remittances", "banking"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Tripura Star News", "url": "https://www.tripurastarnews.com/"},
            {"name": "Reuters", "url": "https://www.reuters.com/"},
            {"name": "The Indian Eye (Bank of Baroda report)", "url": "https://www.theindianeye.com/rbi-looks-to-revive-nri-deposit-growth-through-fcnrb-route-nro-accounts-grow-fastest-bank-of-baroda-report/"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_02.jpg/1280px-Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_02.jpg",
        "image_caption": "The Reserve Bank of India headquarters in Mumbai",
        "image_attribution": "Wikimedia Commons",
        "body": body2
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  words={wc} slug={art['slug']}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
