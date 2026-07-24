#!/usr/bin/env python3
"""NRI World Writer — 2026-07-14 17:05 PT run"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load Supabase credentials
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
        "headline": "One Hundred and Twenty Thousand Doctors, One Alliance: How Indian American Physicians Just Built a Healthcare Bridge Between Two Continents",
        "subheadline": "The India–America Health Alliance, announced at the AAPI's annual convention in Tampa, aims to connect US-based Indian-origin specialists with underserved patients in India through telemedicine, AI-powered training, and a decade-long research partnership.",
        "slug": make_slug("aapi-india-america-health-alliance-nita-ambani-tampa"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian American physicians — the largest ethnic medical community in the US, treating every seventh patient in the country — are formalising a healthcare bridge to India. The alliance turns the diaspora's professional capital into direct medical access for underserved communities back home.",
        "tags": ["nri", "diaspora", "healthcare", "aapi", "indian-american-doctors", "telemedicine", "india-us-relations"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Business Wire", "url": "https://www.businesswire.com/news/home/20260709372021/en/Nita-Ambani-Announces-IndiaAmerica-Health-Alliance-Partnership-at-AAPIs-44th-Annual-Convention-Receives-AAPI-Humanitarian-Award-2026"},
            {"name": "The Indian Eye", "url": "https://www.theindianeye.com"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/The_Prime_Minister%2C_Shri_Narendra_Modi_rededicating_Sir_H.N._Reliance_Foundation_Hospital_and_Research_Centre_to_the_Nation%2C_in_Mumbai_on_October_25%2C_2014._The_Governor_of_Maharashtra%2C_Shri_C._Vidyasagar_Rao_is_also_seen_%28cropped%29.jpg/330px-thumbnail.jpg",
        "image_caption": "Nita Ambani at the Reliance Foundation Hospital in Mumbai",
        "image_attribution": "Wikimedia Commons",
        "body": """When Nita Ambani walked onto the stage at the Tampa Convention Center on July 2 to accept the AAPI Humanitarian Award, she was not just receiving a plaque. She was stepping into a room full of the most quietly powerful diaspora community in America — one hundred and twenty thousand physicians of Indian origin who, between them, treat roughly every seventh patient in the United States.

What she announced next was bigger than the award itself.

## The Alliance

The India–America Health Alliance, a partnership between the Reliance Foundation and the American Association of Physicians of Indian Origin, is structured around three commitments that attempt to turn the diaspora's professional capital into something tangible for people who need it most.

The first pillar is access. Using Jio's 5G network, AAPI's US-based specialists will provide telemedicine consultations to patients in India's smaller towns and remote villages — places where a cardiologist or oncologist may be hundreds of kilometres away. The model is not new in concept, but the scale of the physician network backing it is unprecedented. AAPI's membership spans nearly every medical speciality practised in the United States.

The second is capacity. The alliance will train first responders in India in advanced clinical protocols, artificial intelligence applications, and real-time guidance from AAPI physicians. The aim is not to replace Indian doctors but to strengthen the frontline workforce that handles the first critical hours of emergencies in district hospitals and primary health centres.

The third is discovery. The partnership has set a target of producing up to five hundred peer-reviewed publications over the next decade — collaborative research between physicians in both countries that could reshape treatment protocols for conditions disproportionately affecting South Asian populations.

"Medicine, at its best, has no borders," Ambani said in her acceptance speech. The line earned a standing ovation.

## The Key to Tampa

The convention, AAPI's forty-fourth, carried an additional weight this year — it coincided with America's 250th anniversary, a detail the organisers wove into the programme as a reminder of where Indian American physicians sit in the country's story. Tampa Mayor Jane Castor underlined the point by presenting Ambani with the Key to the City, one of the highest civic honours a US city can bestow.

Ambani, who chairs the Reliance Foundation, has built a philanthropic portfolio that stretches across healthcare, education, sports development, environmental conservation, and disaster relief in India. The AAPI award, presented by Convention Chairman Dr Sagar Galwankar, AAPI President Dr Amit Chakrabarty, and Convention Convener Dr Raghu Juvvadi, recognised that body of work while anchoring it to the diaspora's own story.

"I accept this award with humility and deep gratitude," Ambani said. "Service is always carried by many hands — hands that heal, hands that teach, hands that comfort, hands that arrive before dawn and leave long after the world has gone to sleep."

## Why This Matters for the Diaspora

Indian-origin physicians are not a small footnote in American healthcare. They constitute roughly ten per cent of the country's active physician workforce. Nearly twelve per cent of medical students entering US schools are of Indian heritage. AAPI itself has over a hundred and thirty local chapters spread across the country.

Yet for decades, the community's contributions have largely flowed in one direction — into the American healthcare system. The India–America Health Alliance represents something different: a formalised channel for that expertise to reach back across the ocean.

The telemedicine component, in particular, addresses a gap that has frustrated Indian policymakers for years. India has roughly one doctor for every thousand people, but the distribution is wildly uneven. Urban centres are saturated with specialists; rural and semi-urban areas are chronically short. A specialist in Houston connecting via video with a patient in Chhattisgarh is not a replacement for local infrastructure, but it can be the difference between a diagnosis made in time and one that comes too late.

## The Bigger Picture

The alliance arrives at a moment when the Indian diaspora's relationship with its homeland is being redefined through institutional partnerships rather than individual remittances. The American India Foundation raised a record $3.8 million at a single gala earlier this month. Carnegie Corporation's latest list of Great Immigrants featured four Indian Americans. And the India–UK trade deal taking effect this week includes a social security pact benefiting seventy-five thousand Indian professionals.

The AAPI alliance fits that pattern — but with a sharper edge. This is not philanthropy in the traditional sense of writing cheques. It is an attempt to deploy the diaspora's most valuable asset — the clinical expertise of a hundred and twenty thousand physicians — in a structured, measurable way.

Whether the alliance delivers on its ambitious targets will depend on execution, funding commitments that have not yet been publicly detailed, and the willingness of both Indian and American regulatory systems to accommodate cross-border telemedicine at scale. But the fact that AAPI has put its institutional weight behind the effort marks a shift worth watching.

For the Indian American medical community, it answers a question many of its members have quietly carried for years: how do you give back to a country you left, using the skills that country taught you?

The alliance, for the first time, offers a formal answer."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
