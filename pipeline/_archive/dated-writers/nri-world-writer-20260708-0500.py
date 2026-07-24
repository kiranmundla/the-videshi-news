#!/usr/bin/env python3
"""NRI World Writer — 2026-07-08 05:00 PDT"""
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


# ────────────────────────────────────────────
# ARTICLE 1: NZ Indian Diaspora + Modi Visit
# ────────────────────────────────────────────

art1_headline = "Three Hundred and Fifty Thousand Indian New Zealanders Are About to Meet a Prime Minister Who Took Forty Years to Arrive"

art1_subheadline = "Modi's July 10 visit to New Zealand will be the first by an Indian PM in four decades. For a diaspora that now makes up six per cent of the country and generates $350 million in GDP, it is less a diplomatic event than a recognition long overdue."

art1_body = """It has been forty years since an Indian prime minister set foot in New Zealand. Rajiv Gandhi visited in 1986, back when the Indian community there numbered in the low tens of thousands — a modest footnote in the Pacific nation's migrant ledger. When Narendra Modi arrives in Auckland on July 10 for a two-day visit at the invitation of Prime Minister Christopher Luxon, the country he encounters will look very different.

The Indian diaspora in New Zealand has grown from roughly 20,000 people at the turn of the millennium to more than 350,000 today — about six per cent of the national population. That trajectory is one of the sharpest climbs of any Indian community outside the traditional US-UK-Canada corridor. Hindi is now the fifth most-spoken language in New Zealand. Diwali celebrations in Wellington draw 30,000 people. The community has produced its first minister of Indian origin, Priyanca Radhakrishnan, who was elected to Parliament in 2017 and appointed a cabinet minister three years later.

## The Community's Weight

The numbers carry economic force. According to the New Zealand Centre for Digital Connections with India, Indian New Zealanders make up an estimated eight to ten per cent of the nation's digital workforce and generate over NZ$350 million in GDP annually. In Auckland, the country's largest city and home to the bulk of the diaspora, Indian-owned businesses span technology, healthcare, hospitality, and professional services.

Community organisations have matured alongside the population. The New Zealand Indian Central Association celebrated its centenary earlier this year, with NZICA President Veer Khar describing the body as "the collective voice of a community that now numbers more than 350,000 New Zealanders of Indian origin." It remains one of the oldest ethnic community organisations in the country — a reminder that while the diaspora's recent growth has been dramatic, its roots run back a full century.

## Excitement — and Tensions

Ahead of the visit, Indian New Zealanders have been vocal about what it means. "An Indian Prime Minister is visiting New Zealand after 40 years, so it is a very important moment," one community member told IANS. "It will strengthen the relationship between India and New Zealand, especially in the field of trade." Students have expressed hope that the visit will produce tangible outcomes for their visa and employment prospects.

But the excitement sits alongside real friction. Earlier this year, the New Zealand government under Deputy Prime Minister Winston Peters tightened immigration rules in ways that disproportionately affected Indian nationals. Student visa pathways were narrowed, work visa conditions were stiffened, and rhetoric from parts of the political establishment took a pointed turn. A Videshi report from July 3 detailed how the India-New Zealand free trade agreement was accompanied by immigration provisions that applied, in practice, almost exclusively to Indians.

For many in the diaspora, the two currents — diplomatic warmth at the top and bureaucratic chill on the ground — define the lived experience. Modi's visit, they hope, will force a reckoning between the two.

## What Is on the Table

The bilateral agenda is expected to span trade, defence, education, and technology cooperation. India-New Zealand trade remains modest relative to India's trade with other partners — New Zealand does not crack India's top twenty trading partners — but momentum is building. Commerce Minister Piyush Goyal visited New Zealand earlier this year, and Trade Minister Todd McClay has made reciprocal trips to India for free trade negotiations.

Diaspora leaders like Sunit Prakash, co-founder of the New Zealand Centre for Digital Connections with India and one of the first Indians to receive the New Zealand Order of Merit for services to IT, have urged the government to formally include ethnic and diaspora leaders in trade strategy. "We are extending our successful 'Connecting the Dots' series with proposals to accelerate Kiwi tech businesses entering India's dynamic market," Prakash said.

## A Community Between Two Worlds

For Indian New Zealanders, the visit is personal in a way that trade figures cannot capture. Many arrived in the country as students or skilled migrants in the last two decades, building lives in a place that sits at the geographic edge of the Indian diaspora's global map. Their children speak English with Kiwi accents and play rugby, but observe Diwali and Navratri. Their parents video-call family in Gujarat, Kerala, and Punjab from houses in Auckland suburbs where the nearest Hindu temple is a twenty-minute drive.

Modi's visit will last two days. The community has waited forty years. Whether the outcomes match the anticipation will depend on what follows long after the motorcade has left."""

art1_sources = json.dumps([
    {"name": "IANS", "url": "https://ianslive.in/"},
    {"name": "New Zealand Centre for Digital Connections with India via CFOTech NZ", "url": "https://cfotech.co.nz/"},
    {"name": "Sociology Institute - Indian Diaspora in NZ", "url": "https://sociology.institute/"},
    {"name": "Zealandia News - NZICA Centenary", "url": "https://zealandia.news/"},
    {"name": "Statistics New Zealand / Wikipedia", "url": "https://en.wikipedia.org/wiki/Indian_New_Zealanders"}
])


# ────────────────────────────────────────────
# ARTICLE 2: India Remittance Record $144.79B
# ────────────────────────────────────────────

art2_headline = "India Just Received a Record $145 Billion From Its Diaspora. For the First Time, America Sent the Most."

art2_subheadline = "Inward remittances hit $144.79 billion in FY26, up from $124.55 billion the year before. The bigger story is where the money is coming from — and what the shift says about who the Indian diaspora has become."

art2_body = """For decades, the story of Indian remittances was a Gulf story. Blue-collar workers in Saudi Arabia, the UAE, and Qatar wired money home to families in Kerala, Andhra Pradesh, and Bihar. The sums were modest individually but enormous in aggregate, and they kept entire local economies running.

That story is no longer the whole story. Reserve Bank of India data confirms that net inward remittances to India reached $144.79 billion in FY26 — a record, and a sharp jump from $124.55 billion in FY25 and $106.63 billion just two years before that. More striking than the headline number is the source: the United States now accounts for 27.7 per cent of gross remittance inflows into India, making it the single largest source of money sent home by the diaspora.

## The Composition Shift

The UAE, long the dominant corridor, has slipped to second at 19.2 per cent. The United Kingdom follows at 10.8 per cent, Saudi Arabia at 6.7 per cent, and Singapore at 6.6 per cent. Together, these five countries account for more than seventy per cent of all money flowing into India from its citizens abroad.

The pattern tells a structural story. Since the Covid-19 pandemic, India's dependence on remittances from the Gulf Cooperation Council countries has gradually declined, reflecting what economists describe as a generational shift in the diaspora's profile. More Indians are migrating as software engineers, healthcare professionals, and finance workers to advanced economies — the US, UK, Canada, Australia, Singapore — rather than as construction and hospitality workers to the Gulf. Their individual remittances are larger, their employment more stable, and their financial ties to India more complex, extending beyond simple wire transfers to property purchases, mutual fund SIPs, and FCNR deposits.

## Resilience Despite Conflict

The FY26 numbers are especially notable because they defied predictions. The escalation of conflict in West Asia raised serious concerns about a disruption to remittance flows, particularly from the GCC region. Production activity in the Gulf was affected, contract renewals slowed, and some workers were returned to India — particularly impacting communities in Kerala.

Yet the data showed the opposite. Net inflows in the fourth quarter of FY26 averaged $13.7 billion per month, and April alone saw $16 billion — suggesting that NRIs in the Gulf, if anything, accelerated transfers as a hedge against regional instability.

"Inward remittances were particularly strong in Q4 FY26, with a notable increase in flows from Gulf-based NRIs," one banker told the India Press Agency. "The rise appears to have been driven not only by underlying growth in the NRI population and remittance base, but also by geopolitical uncertainty in West Asia."

Gaura Sen Gupta, chief economist at IDFC First Bank, offered a measured outlook: "While the escalation in West Asia did raise concerns, the data so far does not suggest any meaningful disruption. Some normalisation cannot be ruled out, but we do not expect a sharp decline."

## What It Means for NRIs

For the nearly five million Indians in the United States — the diaspora's largest and most economically powerful cluster — the shift in remittance dominance is a data point confirming what most already know: their financial relationship with India has become the single largest channel of economic connection between the two countries, larger than many bilateral aid programmes and more durable than any trade deal.

That relationship extends well beyond family support. NRI deposits in Indian banks, investments in Indian equities, and purchases of Indian real estate together constitute a capital flow that the RBI has deliberately courted. The central bank's recent FCNR(B) deposit scheme, offering rates as high as seven per cent on dollar deposits, is a direct play for this money — and the remittance data suggests the play is working.

The RBI projects that inward remittances will remain near FY26 levels in FY27, at $135-$140 billion. If they do, India will have cemented its position as the world's largest recipient of remittances — a distinction it has held for years but never at this scale.

For NRIs, the numbers are a reminder of something that is easy to forget amid the daily grind of mortgage payments, tuition bills, and 401(k) contributions in their adopted countries: collectively, the money they send home is not charity. It is one of the largest single drivers of India's balance of payments, and it gives the diaspora an economic leverage that no lobby group or cultural organisation can match."""

art2_sources = json.dumps([
    {"name": "Reserve Bank of India / India Press Agency", "url": "https://ipanewspack.com/"},
    {"name": "SBI Research via The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
    {"name": "RBI Bulletin / The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
    {"name": "Wikipedia - Remittances to India", "url": "https://en.wikipedia.org/wiki/Remittances_to_India"}
])


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "slug": make_slug("nz-indian-diaspora-modi-visit-40-years-350000"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "New Zealand's Indian community — now 350,000 strong and six per cent of the population — awaits the first visit by an Indian PM in 40 years, navigating between diplomatic warmth and tightening immigration rules.",
        "tags": ["nri", "diaspora", "new-zealand", "modi", "community"],
        "urgency": "medium",
        "sources": art1_sources,
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17824133/pexels-photo-17824133.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Auckland skyline at dusk with the Sky Tower, home to the largest concentration of Indian New Zealanders",
        "image_attribution": "Pexels",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "slug": make_slug("india-remittance-record-145-billion-america-largest-source"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "America is now the single largest source of remittances to India, overtaking the Gulf — a data-driven confirmation of the diaspora's shift from blue-collar Gulf workers to white-collar US professionals.",
        "tags": ["nri", "diaspora", "remittance", "finance", "rbi"],
        "urgency": "medium",
        "sources": art2_sources,
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/14907377/pexels-photo-14907377.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Indian rupee currency notes — India received a record $144.79 billion in remittances in FY26",
        "image_attribution": "Pexels",
        "body": art2_body,
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
