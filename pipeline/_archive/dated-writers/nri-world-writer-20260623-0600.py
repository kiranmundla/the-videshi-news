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

article1_body = """India has spent decades describing its diaspora as a strategic asset — 31 million people, the largest overseas community in the world, a reliable source of remittances, soft power and the occasional ministerial photo-op. What it has never quite had is a phone book.

That is the gap the Ministry of External Affairs is now trying to close. This week it launched the **Global Pravasi Rishta** portal and a companion mobile app, pitched as a permanent, two-way channel between the government in Delhi, its missions abroad, and the people those missions are meant to serve. The promise is less about ceremony and more about plumbing: a single place where an NRI in Houston or a PIO in Nairobi can register once and stay connected.

## What it actually does

The portal is not another grievance desk. Officials have been at pains to point out what it is *not*: passport applications still go through Passport Seva, consular complaints still route through MADAD. Global Pravasi Rishta sits above all of that, as a relationship layer rather than a service window.

Registration is open to NRIs, OCI and PIO cardholders alike — a deliberately wide net. Once enrolled, a member can:

- receive real-time alerts and advisories from their local Indian mission
- get invitations to consulate-organised events, from Republic Day receptions to investment roadshows
- be reached quickly during a crisis or evacuation
- learn about government schemes aimed at the diaspora
- respond to surveys and policy consultations, and receive mission newsletters

"The Government recognises the importance of the India diaspora and has been engaging with them in various ways," said Minister of State for External Affairs V. Muraleedharan at the launch. The portal, he added, is meant to connect with the overseas community "not just ceremonially but at every step."

## The unspoken logic: a crisis register

Strip away the language of *rishta* — relationship, kinship — and a more practical motive emerges. Every recent overseas emergency, from the evacuation of students out of Ukraine to repatriation flights during the pandemic, exposed the same weakness: the government did not reliably know who was where. Missions scrambled to assemble contact lists in the middle of the emergency itself.

A standing, self-updating register of diaspora members solves exactly that problem. Indian embassies from Muscat to Madrid to São Paulo have, over the past weeks, posted near-identical appeals urging their communities to sign up — country and mission selectable from a dropdown — precisely so that the next "unforeseen emergency," in the words of the Consulate in Bali, finds a list already built.

## What it asks of the diaspora

For the individual NRI, the value proposition is real but modest. The portal will not shorten a visa queue or unfreeze an NRO account. What it offers is visibility — the assurance that your mission knows you exist, and a faster tap on the shoulder when something matters.

The catch, as ever with diaspora engagement schemes, is uptake. The Indian government has launched diaspora-facing platforms before, with mixed adoption; a portal is only as useful as the number of people who bother to register and keep their details current. For a community that already juggles OCI renewals, FATCA disclosures and the annual ritual of proving it is alive to one bureaucracy or another, "one more registration" is a hard sell unless the payoff is visible.

Still, the direction of travel is clear. India increasingly treats its diaspora not as a sentimental abstraction to be toasted once a year at Pravasi Bharatiya Divas, but as a distributed constituency to be mapped, messaged and, when useful, mobilised. Global Pravasi Rishta is the database that ambition requires.

Whether the diaspora signs up in the numbers Delhi hopes for is now the open question — and the answer will say a good deal about how the relationship is felt from the other side.

Members can register at the official portal, pravasirishta.gov.in, selecting their country and local mission."""

article2_body = """Every so often the Indian-American community produces a number designed to be quoted at galas, and this one is built for it: a community that makes up roughly 1.5% of the United States population pays about **5-6% of all individual income taxes** collected in the country.

The figure comes from the first comprehensive, data-driven accounting of the diaspora's footprint in America, compiled by Indiaspora, the non-profit network founded by Silicon Valley investor M.R. Rangaswami. Titled around the theme *"Every town is my town, and all the people in the world are my kin,"* the report tries to convert a familiar feeling — that Indian-Americans punch above their weight — into balance-sheet arithmetic.

## The numbers, briefly

The headline tax statistic is the one that travels, but the report's reach is wider. Among its findings:

- Sixteen Indian-origin executives currently lead Fortune 500 companies — Satya Nadella at Microsoft, Sundar Pichai at Google, and Reshma Kewalramani, the first woman to run a major US biotech, among them. Together those companies employ some 2.7 million Americans and generate close to **$1 trillion** in revenue.
- Indians have co-founded 72 of the 648 US "unicorns" — privately held start-ups valued above $1 billion — that were operating as of 2024. Those firms employ over 55,000 people and carry a combined valuation near **$195 billion**.
- The diaspora, while around 1.5% of the population, accounts for roughly **13% of US scientific publications**, a measure of its concentration in research and academia.

The study organises the contribution across five dimensions — economic, scientific, social, cultural and civic — and was overseen by a steering committee of executives and academics, lending it a heft that earlier, anecdote-driven celebrations of diaspora success lacked.

## Why a number like this matters now

It is tempting to file this under community self-congratulation, and there is some of that. But the timing and the audience give the report a sharper edge.

The Indian-American diaspora is in the middle of an awkward season in US politics. Immigration is once again a live and contentious issue, the H-1B visa programme that built much of this professional class is under renewed scrutiny, and the community's growing political visibility has invited both pride and backlash. A report that translates presence into fiscal contribution — *we pay four times our share of income tax* — is, in that climate, less a brag than an argument.

It is the kind of evidence community organisations can hand to a sceptical lawmaker. The tax line in particular reframes a debate often conducted in the language of cost and competition into one of net contribution.

## The thing the spreadsheet leaves out

For the diaspora itself, the report lands on a more personal nerve. The numbers describe an extraordinary collective success — Fortune 500 corner offices, unicorn cap tables, an outsized slice of the nation's research output. They also describe a community whose belonging is still, in 2026, something it feels obliged to prove with a citation.

That is the quiet tension running underneath every diaspora achievement report. The first generation arrived on student visas and H-1Bs and built, often spectacularly. The second is American by birth and instinct. Yet the impulse to total up the contribution — to keep the receipt — persists, because the question of whether one fully belongs never entirely closes.

The Indiaspora report answers that question the only way data can: emphatically, and in dollars. Whether the wider American audience is keeping the same score is, as always, the harder thing to measure.

The full report is published on Indiaspora's website."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India Has 31 Million People Abroad. Until This Week, It Didn't Have a Working Phone Book.",
        "subheadline": "Delhi's new Global Pravasi Rishta portal isn't a grievance desk — it's the diaspora register the government wished it had during every recent overseas crisis.",
        "slug": make_slug("global-pravasi-rishta-portal-mea-diaspora-register-nri-oci-connect"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "A single MEA portal that lets every NRI, OCI and PIO register once with their local Indian mission — for event invites, scheme info, and faster contact in a crisis or evacuation.",
        "tags": ["nri", "diaspora", "oci", "pravasi-rishta", "mea", "consular"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/indias-external-affairs-ministry-launches-global-pravasi-rishta-portal-for-nri-connect/"},
            {"name": "Embassy of India, Muscat", "url": "https://indemb-oman.gov.in/"},
            {"name": "Global Pravasi Rishta Portal (Govt. of India)", "url": "https://pravasirishta.gov.in/home"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16100484/pexels-photo-16100484.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Members of the Indian diaspora gather at a community celebration",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian-Americans Are 1.5% of the Country. They Pay 5-6% of Its Income Taxes.",
        "subheadline": "A first-of-its-kind Indiaspora report puts hard numbers on diaspora success — and arrives just as the community's place in US politics turns contentious.",
        "slug": make_slug("indiaspora-report-indian-americans-income-tax-fortune-500-unicorns"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "A data-driven case for belonging: the report reframes Indian-American immigration debates in the language of net fiscal and economic contribution, just as H-1B scrutiny intensifies.",
        "tags": ["nri", "diaspora", "indiaspora", "indian-american", "fortune-500", "h1b"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/small-community-big-contributions-as-indian-americans-pay-about-5-6-of-all-income-taxes-in-the-us/"},
            {"name": "Indiaspora", "url": "https://indiaspora.org/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8068807/pexels-photo-8068807.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A culturally diverse team in a business meeting",
        "image_attribution": "Pexels",
        "body": article2_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   {art['slug']}: {wc} words")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
