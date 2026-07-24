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
        "headline": "Nice, Bratislava, Evian, Paris: Modi's Six-Day European Tour Begins and Ends With the Diaspora",
        "subheadline": "The prime minister's France-Slovakia swing combines G7 diplomacy with startup diplomacy and a community address in Paris — the first by an Indian leader at VivaTech.",
        "slug": make_slug("modi-france-slovakia-europe-diaspora-g7-vivatech"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Modi will address the Indian community in Paris on June 18 and inaugurate Bharat Innovates in Nice — both directly aimed at diaspora entrepreneurs and professionals in Europe. The visit also raises H-1B visa and trade deal questions that affect every NRI in the US.",
        "tags": ["nri", "diaspora", "modi", "france", "slovakia", "g7", "vivatech", "europe"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indian-pm-modi-visit-france-slovakia-june-13-18-2026-06-10/"},
            {"name": "The Daily Jagran", "url": "https://www.thedailyjagran.com/"},
            {"name": "The Freedom Press (IANS)", "url": "https://thefreedompress.in/feeling-fortunate-indian-diaspora-in-france-excited-ahead-of-pm-modis-visit/"},
            {"name": "Embassy of India, Paris", "url": "https://eoiparis.gov.in/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5f/The_official_portrait_of_Shri_Narendra_Modi%2C_the_Prime_Minister_of_the_Republic_of_India.jpg",
        "image_caption": "Prime Minister Narendra Modi, who departed for France on June 13 for a six-day European tour",
        "image_attribution": "Wikimedia Commons",
        "body": """Prime Minister Narendra Modi touched down in Nice on Saturday for the opening leg of a six-day visit to France and Slovakia that blends hard geopolitics — a likely bilateral with Donald Trump at the G7 in Evian — with the softer currency of community events, startup showcases, and a diaspora address in Paris.

It is Modi's sixth visit to France, but the itinerary is unusual. Rather than heading straight to the capital, the trip begins on the Côte d'Azur, where Modi and French President Emmanuel Macron will jointly inaugurate *Bharat Innovates 2026* in Nice on June 14 — a curated expo of Indian startups, deep-tech founders, and investors designed to put India's innovation ecosystem in front of European capital.

India will have the largest national pavilion at VivaTech 2026, Europe's foremost technology gathering, when Modi attends in Paris on June 18. Between Nice and Paris, the schedule includes a state visit to Bratislava — the first ever by an Indian prime minister since Slovakia's independence in 1993 — and the G7 summit in Evian from June 15 to 17, where Modi will represent the "Global South."

## Why the diaspora is watching

For the roughly 120,000 people of Indian origin living in France, the main event is June 18. The Indian Embassy in Paris opened registration on June 2 for a community address by Modi, and slots filled quickly. In Nice, members of the diaspora told IANS they felt "fortunate" that the prime minister was visiting their city.

"It has been two years since I came to Nice. I work as a chef in a restaurant," said Shubham, a community member. "The respect for Indians has increased. Earlier, many people did not know much about India, but today, people know about us."

Beyond the feel-good, the visit carries material stakes. India and France elevated their relationship to a "Special Strategic Partnership" in February 2026, a tier that unlocks deeper cooperation on defence, nuclear energy, space, and — critically for NRI professionals — mutual recognition of qualifications and mobility frameworks.

## The G7 sideline: trade, tariffs, and H-1B

A Reuters report said Modi is likely to hold bilateral talks with Trump at Evian, with trade, energy, and H-1B visas on the agenda. Washington has proposed an additional 12.5 per cent tariff on Indian imports citing forced-labour allegations that India flatly rejects, and trade talks toward an interim bilateral deal could conclude by mid-July, according to India's trade minister Piyush Goyal.

For the hundreds of thousands of Indian professionals on H-1B visas or in the Green Card backlog, any movement on the visa question during a Modi-Trump meeting would be significant. The EB-2 India cutoff date already retrogressed in June, rattling NRI professionals who have waited years for permanent residency.

## Slovakia: the first visit

The Bratislava stop, June 14–16, is historic in a literal sense. No Indian prime minister has visited Slovakia since its 1993 independence. Modi will meet President Peter Pellegrini and Prime Minister Robert Fico, with the India-EU Free Trade Agreement — announced earlier in 2026 — providing the commercial backdrop.

"Building on the momentum of the India-EU Free Trade Agreement, the visit will further energise our Strategic Partnership with the European Union, of which Slovakia is an important and valued member," Modi said before departing.

## What it means for NRIs in Europe

The trip signals a strategic pivot. Until recently, India's diplomatic engagement with the diaspora focused overwhelmingly on the US, UK, and the Gulf. This itinerary — a startup expo in Nice, a tech summit in Paris, a first-ever visit to Bratislava — extends that engagement to continental Europe, where the Indian professional population has grown sharply in cities like Paris, Munich, Amsterdam, and Zurich.

For NRI entrepreneurs eyeing European markets, the Bharat Innovates expo and VivaTech pavilion represent a direct pipeline to investors and policy-makers. For the broader community, the Paris address is a chance to be seen — not just as a voting constituency in India, but as a "living bridge" between two innovation economies that are still, in many ways, learning to speak each other's language."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's OCI Cards Have Gone Digital. Here Is What Five Million Holders Need to Know.",
        "subheadline": "The Citizenship Amendment Rules 2026, notified on April 30, introduce e-OCI registration, mandatory online applications, biometric consent for fast-track immigration, and a ban on dual passports for minors.",
        "slug": make_slug("india-eoci-digital-citizenship-amendment-rules-2026-nri"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Every OCI card holder — over 5 million people, mostly in the US, UK, Canada, and Australia — is directly affected. Paper applications are dead. The e-OCI could eliminate the dreaded renewal queue. But mandatory biometric consent and the minor dual-passport ban raise new compliance questions.",
        "tags": ["nri", "diaspora", "oci", "e-oci", "citizenship", "digital", "mha", "passport"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Mondaq (RPV Legal)", "url": "https://www.mondaq.com/india/general-immigration/1783158/citizenship-amendment-rules-2026-oci-cardholders-digitalisation-of-registration-framework-and-dual-passport-restrictions-for-minors"},
            {"name": "Livemint", "url": "https://www.livemint.com/"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/"},
            {"name": "SCC Online", "url": "https://scconline.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/15068317/pexels-photo-15068317.jpeg",
        "image_caption": "A traveller checks their smartphone at an airport — the kind of scene where the new e-OCI could replace a physical card",
        "image_attribution": "Pexels",
        "body": """For more than a decade, the Overseas Citizen of India card has been a small blue booklet that sat in a drawer until you needed to fly to India. That era is over.

On April 30, 2026, the Ministry of Home Affairs notified the Citizenship (Amendment) Rules, 2026 — a sweeping rewrite that moves the entire OCI lifecycle online. Physical cards are still available, but the government has introduced a parallel track: **e-OCI**, a fully digital registration tied to a centralised electronic register. Every application — whether for fresh registration, renewal, transfer to a new passport, or renunciation — must now be filed through the official portal at ociservices.gov.in.

The revamped portal, inaugurated by Home Minister Amit Shah, replaces a system built in 2013 that processed roughly 2,000 applications a day across 180 Indian missions and 12 Foreigners Regional Registration Offices. The MHA expects processing times to fall below 15 working days once legacy files migrate.

## What actually changed

The amendment touches seven areas. Here is what matters most to the average OCI holder:

**Paper is dead.** The old rules required applications "in duplicate" submitted physically to an Indian Mission, Post, or the MHA's Foreigners Division. The new Rule 29(1) is unambiguous: applications must be made "electronically on the designated online portal." No other mode is recognised.

**e-OCI exists.** Under the new Rule 33, a registered OCI cardholder can receive either a physical card or an electronic OCI registration, both in the revised Form XXIX. The issuing authority maintains a digital register in Form XXX. Until now, OCI status was inseparable from the physical booklet — the e-OCI breaks that link.

**Renunciation goes online too.** A person giving up OCI status now files a declaration electronically. If they hold a physical card, the original must still be surrendered to the relevant Indian Mission or FRRO. For e-OCI holders, no physical surrender is possible or required.

**Biometric consent is mandatory.** The revised application form (Form XXVIII) includes a new clause: applicants must consent to share biometric information collected during OCI registration for the Fast Track Immigration Programme and agree to automatic enrolment. There is no opt-out. In practice, this means the biometric data you provide for your OCI card could be used at automated e-gates at Indian airports without a separate application.

**Minors cannot hold dual passports.** The amended Rule 3 introduces a continuing obligation: a minor child "cannot at any time hold the passport of any other country while also holding the Indian passport." Previously, a parent could register a child's birth at an Indian consulate and later obtain a foreign passport with no formal acknowledgment of the conflict. The new rules close that gap.

## What it means for NRIs in practice

For the typical NRI family in the US or UK, three things change immediately.

First, the renewal headache eases — if the portal works. The 2013 system was notorious for crashes, unclear document requirements, and opaque status tracking. The new portal adds auto-fill, a dashboard for partially completed applications, categorised document uploads, and an integrated payment gateway. Whether it delivers on the promise remains to be seen, but the old "submit in duplicate and wait" model is gone.

Second, the biometric consent clause deserves attention. GOPIO International, the largest diaspora advocacy organisation, has long pushed for streamlined immigration at Indian airports. The automatic Fast Track enrolment achieves that — but it also means applicants are consenting, at the point of OCI registration, to future biometric use they may not fully anticipate.

Third, the dual-passport restriction for minors could catch families off guard. Many NRI parents with US or UK citizenship obtain an Indian passport for a minor child (through the child's grandparents' citizenship) alongside a foreign passport. Under the new rules, that arrangement is explicitly prohibited. Parents must choose.

## The bigger picture

The e-OCI is part of a broader digitisation push by the MHA — the system will eventually integrate with India's Immigration, Visa & Foreigners Registration & Tracking (IVFRT) 2.0 platform, the same infrastructure that powers automated e-gates at major Indian airports. In parallel, the GOPIO convention in April passed a resolution urging India to grant full dual nationality to OCI holders and issue Aadhaar cards to NRIs who remain Indian citizens — demands the government has so far not accepted.

For five million OCI holders scattered across the globe, the message is clear: bookmark ociservices.gov.in, update your passport records, and keep your biometric consent in mind the next time you renew. The queue is digital now, but the stakes are the same."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Tomorrow, Dartmouth Hands Vivek Murthy an Honorary Doctorate. He Will Probably Talk About Loneliness Again.",
        "subheadline": "The first Indian-American U.S. Surgeon General, who served under both Obama and Biden, receives an honorary Doctor of Science as the Class of 2026 graduates in Hanover, New Hampshire.",
        "slug": make_slug("vivek-murthy-dartmouth-honorary-doctorate-indian-american"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Murthy is arguably the most prominent Indian American in US public health history. His parents immigrated from Karnataka, he was raised in Miami, and he has repeatedly credited the Indian concept of Seva — selfless service — as the force behind his work. His loneliness research, his social media youth warnings, and his Parting Prescription for America all grew from a worldview shaped between two cultures.",
        "tags": ["nri", "diaspora", "vivek-murthy", "dartmouth", "surgeon-general", "indian-american", "public-health"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Dartmouth College", "url": "https://home.dartmouth.edu/"},
            {"name": "American Bazaar", "url": "https://www.americanbazaaronline.com/2026/05/06/vivek-murthy-to-receive-dartmouth-honorary-degree/"},
            {"name": "Dartmouth Times", "url": "https://dartmouthtimes.com/"},
            {"name": "The Dartmouth", "url": "https://www.thedartmouth.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Vivek_Murthy%2C_Surgeon_General_%28profile%29.jpg",
        "image_caption": "Dr. Vivek Murthy during his tenure as U.S. Surgeon General",
        "image_attribution": "Wikimedia Commons",
        "body": """On Sunday morning, when Dartmouth's Class of 2026 gathers on the Green in Hanover, New Hampshire, one of the seven people receiving honorary degrees will be a physician who spent the better part of a decade telling America it was sick with something no drug could cure.

Dr. Vivek Murthy, the first U.S. Surgeon General of Indian descent, will be awarded an honorary Doctor of Science at Dartmouth's commencement ceremony on June 14. He joins comedian Rachel Dratch (who will deliver the commencement address), computer scientist Maria Klawe, playwright Karen Evans, philanthropist Gary Love, free-speech advocate Greg Lukianoff, and attorney Alfred Moses on the roster of honorees.

The selection is ceremonial, as these things always are. But it also represents something particular about what Indian Americans have come to symbolise in American public life: not just technical competence, but moral authority on questions the country is only beginning to ask.

## The loneliness thesis

Murthy served as Surgeon General from 2014 to 2017 under Obama, and from 2021 to 2025 under Biden — two terms in which he steadily expanded the office beyond traditional health policy. His most consequential move was declaring an "epidemic of loneliness and isolation" in 2023, framing social disconnection as a public health crisis on par with smoking or obesity.

It was not an obvious cause for America's top doctor to champion. Loneliness does not lend itself to ribbon-cutting or vaccine drives. But Murthy argued, with data, that chronic social isolation increases the risk of premature death by 26 per cent and that the condition was especially acute among young people, for whom social media had become a substitute for — not a supplement to — genuine connection.

His 2020 book, *Together: The Healing Power of Human Connection in a Sometimes Lonely World*, became a New York Times bestseller. By 2024, he had issued an advisory on the effects of social media on youth mental health, calling for warning labels on platforms. In 2025, as he left office, he released a "Parting Prescription for America" — a vision document arguing that rebuilding social infrastructure was the single most important thing the country could do for its health.

## The Karnataka-to-Miami pipeline

What makes Murthy's trajectory a diaspora story, and not merely a Washington one, is the cultural scaffolding underneath it.

Born in Huddersfield, England, to parents who emigrated from Karnataka, Murthy grew up in Miami, where his father and mother ran a medical practice. He has spoken often about watching them treat patients not just as cases but as people — a habit he traces to the Indian value of *Seva*, or selfless service, which he cites as the driving force behind both his terms as "America's Doctor."

His academic path — Harvard for his bachelor's, Yale for his MD and MBA, Brigham and Women's Hospital for his residency — follows the familiar high-achievement track of second-generation Indian Americans. What distinguishes him is the public-facing vulnerability. In a medical establishment that prizes detachment, Murthy repeatedly centred emotion, connection, and community. His loneliness thesis, in some ways, is an articulation of a worldview shaped by growing up between two cultures: one that emphasises family and collective identity, another that celebrates individual achievement and self-reliance.

## The Dartmouth connection

Dartmouth itself has no particular Indian American tradition to speak of — it is a small liberal arts college in rural New Hampshire, not an IIT feeder school. But the honorary degree reflects a broader trend: Indian Americans being recognised not only for technical achievement (the CEOs, the engineers, the startup founders) but for contributions to American civic life.

Murthy joins a list that includes the five Indian American members of Congress who, just weeks ago, jointly demanded a DOJ briefing on hate crimes against Hindus. And the AIF gala in New York that raised a record $3.8 million for development work in India. And the 96 Indian-born founders of US unicorn startups documented in the latest NFAP report.

The pattern is clear enough: the Indian diaspora in America is no longer a professional class content to succeed quietly. It is becoming a civic force — in medicine, in politics, in philanthropy, and in the kind of moral argument that Murthy has spent a decade making about what it means to be well.

The commencement ceremony begins at 9:30 a.m. on Sunday. If past form is any guide, Murthy will not talk about himself. He will talk about loneliness. And about 3,000 graduating seniors will listen, surrounded by family, wondering if he is right."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
