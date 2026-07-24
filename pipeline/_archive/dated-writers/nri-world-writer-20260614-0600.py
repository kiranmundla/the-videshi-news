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
        "headline": "India Just Opened Its Stock Markets to Every Foreigner on the Planet. NRIs Are No Longer Special.",
        "subheadline": "A quiet FEMA amendment published on June 12 replaces the phrase 'NRI or OCI' with 'any individual residing outside India,' dismantling a decades-old investment privilege the diaspora once had to itself.",
        "slug": make_slug("fema-amendment-nri-oci-foreign-individual-india-stock-market"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "NRIs and OCIs who long enjoyed exclusive retail access to Indian equities now share that privilege with every foreign individual — a levelling that could reshape how diaspora investors think about their edge in India's capital markets.",
        "tags": ["nri", "diaspora", "fema", "investment", "india-stock-market", "oci"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "TaxScan", "url": "https://taxscan.in/"},
            {"name": "CA Club India", "url": "https://caclubindia.com/"},
            {"name": "Reuters", "url": "https://reuters.com/"},
            {"name": "Ministry of Finance Gazette Notification", "url": "https://egazette.gov.in/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg",
        "image_caption": "The Bombay Stock Exchange building in Mumbai's Dalal Street financial district",
        "image_attribution": "Wikimedia Commons",
        "body": """For twenty-five years, the Portfolio Investment Scheme was the diaspora's private door into Dalal Street. Non-Resident Indians and Overseas Citizens of India could buy and sell shares on Indian exchanges while the rest of the world's retail investors were locked out, funnelled into the more cumbersome Foreign Portfolio Investor route or forced to look from the sidelines entirely.

On June 12, the Ministry of Finance published a three-page gazette notification that effectively ended that exclusivity. The Foreign Exchange Management (Non-Debt Instruments) (Third Amendment) Rules, 2026, replace the words "a non-resident Indian or an overseas citizen of India" with "an individual person resident outside India" across the relevant chapters of India's investment rulebook. It is a small edit with large consequences.

## What actually changed

The amendment rewrites Rule 9 and the entirety of Chapter V of the FEMA Non-Debt Instruments Rules, 2019. The old heading — "Investment by Non-Resident Indian or an Overseas Citizen of India" — now reads "Investment by an Individual Person Resident Outside India Including a Non-Resident Indian or an Overseas Citizen of India." The operative Rule 12 now permits any individual residing outside India to purchase or sell equity instruments of listed Indian companies on a repatriation basis, subject to the conditions in Schedule III.

In practical terms, a British software engineer with no Indian heritage, a Japanese retiree with a brokerage account, or a Nigerian entrepreneur with dollar savings can now invest in Indian listed equities through the same channels that were built for the diaspora. The aggregate and individual holding limits still apply — the February 2026 budget had already doubled the individual PIS cap from 5 to 10 per cent and raised the aggregate ceiling to 24 per cent — but the question of *who* qualifies is no longer defined by passport or ancestry.

## The China clause

One carve-out survived the broadening. Investments originating from countries that share a land border with India — China, Pakistan, Bangladesh, Myanmar, Nepal, and Bhutan — still require prior government approval if they result in a change of ownership or control, or if the beneficial owner is a citizen of those nations. This mirrors the existing Press Note 3 restrictions on FDI that have been in place since 2020, originally introduced to prevent opportunistic acquisitions during the pandemic.

## Why now

The timing is not accidental. India's balance of payments has been under persistent strain. The rupee is down roughly 6 per cent against the dollar this year and hit record lows in May. Net foreign portfolio investment turned negative in FY25, with $16.5 billion leaving the country. Net FDI barely touched $1 billion. Widening the investor base for listed equities is one part of a broader effort — alongside the RBI's FCNR deposit sweeteners announced the same week — to pull more foreign capital into Indian markets and take some pressure off the currency.

## What it means for NRIs

The diaspora's practical access is not diminished. NRIs and OCIs retain every route they had before — the PIS scheme, NRE and NRO accounts, the recently enhanced FCNR deposit rates, and the GIFT City infrastructure that is slowly maturing into a credible offshore wealth hub. What has changed is their relative position: the regulatory moat that once separated diaspora retail investors from the rest of the world's individuals has been drained.

For the NRI investor who relied on cultural familiarity and regulatory exclusivity as twin advantages, the message from New Delhi is blunt. India wants your money, but it wants everyone else's too. The pitch to the diaspora is no longer "you are the only ones who can do this." It is "you happen to understand this market better than anyone. Use that."

Whether that shift matters in practice — whether a meaningful number of non-Indian individuals will actually navigate Schedule III's conditions and open accounts at Indian depositories — is an open question. The infrastructure is not yet frictionless for outsiders. But the signal is unmistakable: India's capital markets are no longer the diaspora's private preserve."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "From the Lincoln Memorial to Times Square: How Yoga Day 2026 Became the Diaspora's Biggest Public Ritual",
        "subheadline": "The Indian Embassy will host its flagship Yoga Day celebration at the Lincoln Memorial on June 19, while Padma Shri HR Nagendra — Modi's personal yoga guru — headlines the Times Square event on June 21.",
        "slug": make_slug("yoga-day-2026-lincoln-memorial-times-square-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "International Day of Yoga has evolved from a UN calendar date into the Indian diaspora's most visible annual public gathering in the West — a rare moment when thousands of Indian Americans occupy iconic American landmarks to practise something unmistakably Indian.",
        "tags": ["nri", "diaspora", "yoga-day", "indian-embassy", "washington-dc", "new-york", "cultural"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
            {"name": "Indian Embassy Washington DC (X)", "url": "https://x.com/IndianEmbassyUS"},
            {"name": "United Nations", "url": "https://www.un.org/en/observances/yoga-day"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8172947/pexels-photo-8172947.jpeg",
        "image_caption": "A group practising yoga outdoors in a park setting",
        "image_attribution": "Pexels",
        "body": """The venue announcements arrived within days of each other. The Indian Embassy in Washington posted on X that the Lincoln Memorial — the same marble steps where Martin Luther King delivered his most famous speech — would host the 2026 International Day of Yoga on Friday, June 19. Separately, organisers in New York confirmed that Times Square would once again be transformed into a mass yoga studio on June 21, the solstice itself, with Padma Shri HR Nagendra as the chief guest.

Taken together, the two events mark a subtle escalation. What began in 2015 as a UN-endorsed observance pushed through by Prime Minister Narendra Modi's government has, over eleven years, become something the diaspora owns as much as New Delhi does: a public, unapologetic display of Indian cultural identity at the heart of American civic space.

## The Lincoln Memorial gambit

The choice of location is deliberate and loaded. The Lincoln Memorial is not a park or a convention centre. It is a national shrine, a site associated with American ideals of freedom and equality. Hosting a yoga session on its steps is a statement about the Indian community's place in the American story — and the diplomatic apparatus behind it is not shy about saying so.

"We're celebrating #InternationalDayOfYoga2026 at the iconic Lincoln Memorial on Friday, June 19, 2026," the embassy announced, pairing the invitation with a quote from Modi: "Yoga is the pause button that humanity needs to breathe, balance, and become whole again."

The Washington event is expected to draw several hundred participants, including embassy staff, members of the Indian-American community, congressional aides, and yoga practitioners with no connection to India at all — which, in a way, is the point. The soft power of yoga lies in its having transcended its origins.

## Nagendra at Times Square

The New York celebration carries a different weight. HR Nagendra, the 82-year-old president of Bengaluru's S-VYASA (Swami Vivekananda Yoga Anusandhana Samsthana) university, is no ordinary guest of honour. He is the man who designs Modi's personal yoga practice. A former NASA researcher who pivoted to yoga science in the 1980s, Nagendra has spent four decades building the evidence base for yoga as a clinical intervention — work that earned him the Padma Shri in 2016.

His presence at Times Square is meant to anchor this year's global theme: "Yoga for Healthy Aging." It is a theme that resonates differently in the diaspora than it does in India. For first-generation NRIs — many now in their sixties and seventies, navigating the American healthcare system while worrying about ageing parents back home — the idea that a practice from their childhood could also be a medically validated longevity tool carries a particular poignancy.

## More than mats and mantras

The numbers tell a story of quiet growth. The Times Square event has drawn between 3,000 and 20,000 participants in previous years, depending on the weather and the political moment. Yoga studios across the US and UK now mark June 21 with special classes and community sessions, often organised by Indian-American associations in partnership with local governments. In 2024, the Mayor of Cary, North Carolina, officially proclaimed June 21 as International Day of Yoga in the city — one of dozens of similar proclamations across American municipalities.

For the diaspora, Yoga Day serves a function that Diwali and Holi celebrations do not quite match. Those festivals are joyful but contained — they happen in temples, community halls, parking lots roped off for the occasion. Yoga Day puts Indian culture in American public space, on iconic American ground, and invites non-Indians to participate as equals rather than spectators. It is, in the language of cultural diplomacy, the softest of soft power.

## The politics beneath the asana

None of this is apolitical. Yoga Day was Modi's initiative at the UN General Assembly in 2014, and the BJP's cultural apparatus has always treated it as a vehicle for Hindu civilisational pride. Critics within the Indian-American community — including some secular and Muslim organisations — have periodically pushed back against what they see as the Hinduisation of a practice that has been deliberately marketed as universal.

That tension has not gone away. But it has been domesticated by repetition. For most of the 5.2 million Indian Americans, Yoga Day is now simply a thing that happens in June — a date on the calendar when it is acceptable, even encouraged, to be visibly Indian in a way that the American mainstream not only tolerates but actively joins."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Dame Parveen Kumar Gets the GBE. She Is Now One of Britain's Most Decorated Indian-Born Citizens.",
        "subheadline": "The 2026 King's Birthday Honours list, published on June 12, names at least eight British Indians — but the headline belongs to a gastroenterologist from Lahore who spent 40 years in the NHS.",
        "slug": make_slug("uk-birthday-honours-2026-british-indians-parveen-kumar-gbe"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Birthday Honours remain the most visible annual scoreboard for British Indian professional achievement — and the 2026 list, with a GBE at the top, signals that the community's influence now reaches the highest tiers of the British establishment.",
        "tags": ["nri", "diaspora", "uk", "birthday-honours", "parveen-kumar", "british-indian"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "UK Government - Birthday Honours 2026", "url": "https://www.gov.uk/government/publications/birthday-honours-list-2026"},
            {"name": "Wikipedia - 2026 Birthday Honours", "url": "https://en.wikipedia.org/wiki/2026_Birthday_Honours"},
            {"name": "LatestLY", "url": "https://www.latestly.com/"},
            {"name": "Asian Voice", "url": "https://asian-voice.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/7f/Dame_Parveen_Kumar_%28cropped%29.jpg",
        "image_caption": "Dame Parveen Kumar, elevated to GBE in the 2026 Birthday Honours",
        "image_attribution": "Wikimedia Commons",
        "body": """The letter after a British Indian's name is, in certain circles, the most reliable measure of how far they have travelled from the airport arrivals hall. An MBE says you have been noticed. An OBE says you matter. A CBE says you sit at tables where decisions are made. A DBE or KBE — the damehood or knighthood — says the establishment considers you one of its own.

A GBE says something else entirely. The Knight or Dame Grand Cross of the Order of the British Empire is the highest rank in the order, reserved for the kind of contribution that has shaped an entire field. On June 12, when the 2026 King's Birthday Honours list was published from Buckingham Palace, that distinction went to Dame Parveen June Kumar — already a Dame Commander — for services to global medical education and health.

## The woman behind the textbook

Kumar's name may not ring bells outside medicine, but inside it, she is everywhere. Born in Lahore, she trained at St Bartholomew's Hospital in London and spent over four decades as a consultant gastroenterologist and physician at Barts and the London Hospitals and the Homerton University Hospital. She is Professor Emerita of Medicine and Education at Barts and the London School of Medicine and Dentistry, Queen Mary University of London.

Her textbook, *Kumar and Clark's Clinical Medicine* — co-authored with Michael Clark — is one of the most widely used medical textbooks in the English-speaking world. First published in 1987, it has gone through ten editions and been translated into multiple languages. For generations of medical students in India, Pakistan, and across the Commonwealth, "Kumar and Clark" is not just a reference book; it is the reference book. The irony is thick: a woman born in undivided India wrote the textbook that trained doctors across the former British Empire.

## The wider list

Kumar was not alone. The 2026 Birthday Honours named several other British Indians across multiple tiers of recognition.

**Yasmin Akhtar Khan** received a CBE for services to ending domestic abuse and violence against women. Khan is the Chief Executive of the Halo Project, a charity that works with victims of honour-based violence, forced marriage, and domestic abuse — issues that disproportionately affect South Asian women in Britain. Her CBE is a recognition both of the work and of the community's willingness to confront its own difficult truths.

**Vishal Kumar Marria** received a CBE for services to technology, economic crime prevention, and the data and AI sector. Marria has built a career at the intersection of financial technology and fraud detection — a field where British Indian entrepreneurs have become increasingly visible.

**Professor Monder Ram** was honoured with a CBE for services to ethnic minority business and entrepreneurship. Ram, who already held an OBE, is the founder and director of the Centre for Research in Ethnic Minority Entrepreneurship — an institution that has produced some of the most cited academic work on how immigrant communities build businesses in Britain.

**Kunal Patel** received a CBE for public service in his role as Deputy Principal Private Secretary to the Prime Minister — a position that places him at the centre of Downing Street's daily operations.

**Sarbjit Singh Uppal** was appointed a Companion of the Order of St Michael and St George (CMG) for services to national security, in his role as a director at the Foreign, Commonwealth and Development Office.

At the MVO level, **Jagjivan Singh Khangura**, an inspector in the Metropolitan Police Service, was recognised for services to royalty and specialist protection — a reminder that British Indian service extends well beyond boardrooms and lecture halls.

## What the GBE means

The GBE is exceptionally rare. In most years, only a handful are awarded across all fields. For a British Indian woman — born in what is now Pakistan, trained in London, published globally — to receive it is a marker of how far the community has come since the Windrush generation and the early waves of South Asian migration in the 1960s and 1970s.

Kumar's career also illustrates a pattern familiar to the diaspora: quiet, sustained excellence that accumulates honours over decades rather than arriving in a single headline. She was made a CBE in 2001, a DBE in 2017, and now a GBE in 2026. Each upgrade reflected not a single achievement but a body of work that kept growing — new editions of the textbook, new advisory roles, new contributions to global health education.

For the 1.8 million people of Indian origin living in Britain, the Birthday Honours are a peculiarly British ritual — monarchical, hierarchical, and slightly absurd in their attention to rank. But they are also real. They open doors, confer legitimacy, and signal to the next generation that the ceiling, if it exists at all, is very high indeed."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
