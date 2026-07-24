#!/usr/bin/env python3
"""Videshi NRI World Writer — 2026-06-10 04:57 PDT run."""
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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── ARTICLE 1: Berlin Sri Ganesha Temple ─────────────────────────────────────

art1_body = """The crane lowered its load onto the seventeen-metre vimana just after noon on 7 June, pouring a stream of water drawn from the Ganges and from Berlin over the tower's spire. Below, several hundred devotees watched the consecration ceremony that capped a five-day Maha Kumbhabhishekam festival — and, more to the point, twenty-one years of planning, fundraising, and construction.

The Sri Ganesha Hindu Temple, rising beside Hasenheide Park in Berlin's Neukölln district, is now one of the largest Hindu temples in Europe. Its intricately carved gopuram, fashioned from black granite quarried in Tamil Nadu and hand-finished by Indian stonemasons, stands out against the Berlin skyline like nothing else in the neighbourhood. And that, its builders say, is precisely the idea.

"This is for the newcomers from India, the students, the IT workers — together with the German population, not just alone," one devotee told reporters at the opening. "Together with happy dancing and music celebrations."

## From cellar prayers to a gopuram on the skyline

The temple's story begins on 24 September 2005, when a small Tamil Hindu community in Berlin laid the first stone. Most of them traced their roots to southern India and Sri Lanka — part of a broader wave of Tamil migration to Germany that started in the late 1970s, when Sri Lankan Tamils arrived as asylum seekers amid the island's civil war. By the mid-1980s, Germany was receiving thousands of Sri Lankan refugees every year.

In those early decades, Hindu worship in Germany happened in basements, rented flats, and converted warehouses. The Tamil diaspora slowly built up, founding roughly thirty-four temples across the country, most of them concentrated in North Rhine-Westphalia. The Berlin temple, however, was always intended to be something grander.

Construction began in earnest in 2009. By 2015, the first gopuram tower was visible above the rooftops, and the distinctive silhouette of South Indian temple architecture — never before seen in the German capital — began to draw attention. The project was funded entirely through donations and voluntary labour. No government grants, no corporate sponsors. Just seva.

## A diaspora that nearly doubled in six years

The temple's opening arrives at a moment when India's footprint in Germany is growing fast. According to recent data, approximately 260,000 Indians were living in Germany as of 2026, up from around 151,000 at the end of 2020 — a roughly seventy per cent increase in six years. Tamils remain the largest Indian ethnic group in the country, followed by Bengalis and Telugus.

Much of the newer migration is driven by Germany's chronic labour shortages. Indian IT professionals, engineers, and healthcare workers have streamed into Berlin, Munich, and Frankfurt, lured by the country's blue card system and a tech sector desperate for talent. But the Tamil community that built the Sri Ganesha Temple represents an older, more settled layer of the diaspora — one that has spent decades putting down roots.

"I feel so proud," a devotee said at the opening, watching a Malakamba demonstration in the temple courtyard. "The big Indian temple, Ganesha temple, is inaugurating today. And to see our Indian sports, especially Malakamba — it's our ancient Indian sports."

## Open to everyone who walks in

The temple is run by ten volunteer board members and three pujaris, and is recognised as a registered non-profit by the German tax authority. Its doors at Hasenheide 106 are open every day from 4 pm to 6 pm, with morning and evening aarti. Architecturally, it follows the South Indian tradition, with a grand central sanctuary and subsidiary towers of ten and twelve metres flanking the main seventeen-metre vimana.

What stands out is the temple's deliberate inclusivity. It welcomes every Hindu current — Vaishnava, Shaiva, Shakta, Smarta — and explicitly invites non-Hindus: Berlin families, students, mixed-faith couples, school groups on open days. In a city where religious institutions increasingly serve as community centres, the Sri Ganesha Temple is positioning itself as a cultural bridge between India and Germany.

The smaller Sri Mayurapathy Murugan Tempel, which opened in Berlin's Britz neighbourhood in 2014, had been the city's first Hindu temple. But the Sri Ganesha Temple operates on a different scale — a landmark that signals the Indian diaspora in Germany has moved beyond survival mode and into permanence.

Twenty-one years is a long time to build a temple. Then again, the best ones always take a while."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Twenty-One Years and a Ton of Tamil Granite Later, Berlin Has One of Europe's Largest Hindu Temples",
    "subheadline": "The Sri Ganesha Temple in Neukölln, funded entirely by donations and seva, opened its doors on June 7 after two decades of construction — a milestone for Germany's fastest-growing diaspora.",
    "slug": make_slug("berlin-sri-ganesha-hindu-temple-europe-largest-neukolln-tamil-diaspora"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Germany's Indian population has surged 70% since 2020 to 260,000, and the Sri Ganesha Temple — built entirely by the Tamil diaspora through donations and voluntary labour — is the most visible symbol yet that the community has moved from survival to permanence.",
    "tags": ["nri", "diaspora", "germany", "hindu-temple", "tamil", "berlin", "europe"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com"},
        {"name": "CurlyTales", "url": "https://curlytales.com"},
        {"name": "NewKerala", "url": "https://newkerala.com"},
        {"name": "Hindu Existence / HENB", "url": "https://hinduexistence.org"},
        {"name": "TeraTern (Indian diaspora statistics)", "url": "https://terratern.com"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/%2820260607_143234213%29_Sri_Ganesha_Hindu_Temple_Berlin.jpg/1280px-%2820260607_143234213%29_Sri_Ganesha_Hindu_Temple_Berlin.jpg",
    "image_caption": "The Sri Ganesha Hindu Temple in Berlin's Neukölln district on its consecration day, 7 June 2026",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}

# ── ARTICLE 2: London Indian Film Festival 2026 ──────────────────────────────

art2_body = """When Lagaan premiered in 2001, the idea that a three-hour-forty-minute Hindi film about a colonial cricket match could earn an Academy Award nomination struck most people outside India as improbable. A quarter-century later, its star will sit down at BFI Southbank to discuss exactly how it happened — and what it meant for a generation of diaspora audiences who watched it in packed cinemas across Britain, often with subtitles they did not need.

Aamir Khan's "In Conversation" session on 16 July will serve as the closing gala of the London Indian Film Festival's 17th edition, which runs 9–19 July across London, Birmingham, Manchester, Sheffield and Bradford. A special screening of Lagaan at BFI IMAX on 12 July will precede it. The festival, supported by the BFI Audience Projects Fund through National Lottery funding, has grown into Europe's largest annual showcase of South Asian cinema.

## Nostalgia with teeth

The festival's central gala, on 11 July at BFI Southbank, reunites the full cast of Goodness Gracious Me — the BBC comedy sketch show that, in the late 1990s, did more for British Asian representation on television than any policy paper or diversity initiative could manage. Sanjeev Bhaskar, Meera Syal, Nina Wadia, Kulvinder Ghir, and creator Anil Gupta will all be on stage.

The show's characters — from the "Going for an English" sketch to the Coopers, the couple who insisted they were absolutely not Indian — became cultural shorthand for the absurdities of assimilation. For British Indians of a certain age, the reunion is not nostalgia for its own sake. It is a reckoning with how far representation has come, and where it has stalled.

## A lost film, found

The festival will also deliver the UK premiere of a 4K restoration of In Which Annie Gives It Those Ones, the 1989 film written by and starring Arundhati Roy — years before The God of Small Things made her a literary phenomenon. Directed by Pradip Krishen, the film is set in a Delhi architecture school in the mid-1970s and features a young Shah Rukh Khan in a small role.

Produced for state broadcaster Doordarshan, it aired once and then vanished from circulation for decades. The Film Heritage Foundation's restoration, which screened at the Berlinale earlier this year, gives diaspora audiences a chance to see a work that has been more rumoured about than watched. Roy's screenplay crackles with the same observational sharpness that would later define her novels; Khan's cameo, meanwhile, has become a piece of Bollywood archaeology.

## AI meets Indian cinema

Perhaps the most forward-looking entry on the programme is India's AI & Film Future, Europe's first showcase of Indian films that use artificial intelligence and other emerging technologies as creative tools. The event, also on 11 July at BFI Southbank, features short films selected by an international jury chaired by Shekhar Kapur, the director behind Elizabeth and Bandit Queen.

The panel discussion that follows will explore how AI-powered tools might democratise access to filmmaking — a subject with obvious resonance for diaspora filmmakers working with small budgets far from Mumbai. A follow-up event is scheduled for Manchester in October, in partnership with Manchester Metropolitan University.

## Why 1.8 million British Indians should care

The opening gala on 9 July will premiere 52 Blue, a coming-of-age drama directed by Ali El Arabi (Captains of Zaatari) and starring Adil Hussain and Neha Dhupia. The film screens across London, Birmingham, Sheffield, and Greater London through mid-July, with the director and cast present.

For the 1.8 million Indians living in the UK, LIFF occupies a particular niche. It is neither a mainstream festival with a token South Asian sidebar nor a community affair screened in a rented hall. It is a properly curated, BFI-backed programme that treats Indian cinema as seriously as any other national cinema — and, increasingly, as seriously as any other technology sector.

This year's edition, with its mix of heritage restoration, nostalgia, celebrity star power, and technological ambition, reflects a diaspora that is both confident enough to celebrate its past and curious enough to invest in its future. The cricket match may have ended twenty-five years ago. The story it launched is still being written."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Lagaan Turns Twenty-Five, the Goodness Gracious Me Gang Reunites, and London's Indian Film Festival Has Never Been Bigger",
    "subheadline": "The 17th edition of Europe's largest South Asian film festival spans five UK cities, brings Aamir Khan to BFI Southbank, and launches the continent's first Indian AI film showcase.",
    "slug": make_slug("liff-2026-aamir-khan-lagaan-goodness-gracious-me-reunion-ai-film"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "For 1.8 million British Indians, LIFF is the rare festival that takes South Asian cinema as seriously as any national cinema — and the 2026 edition, with its Lagaan anniversary, Goodness Gracious Me reunion, and AI showcase, captures a diaspora confident enough to celebrate its past and invest in its future.",
    "tags": ["nri", "diaspora", "uk", "liff", "aamir-khan", "lagaan", "goodness-gracious-me", "bfi", "film-festival"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://bollywoodhungama.com"},
        {"name": "SSZEE Media", "url": "https://sszeemedia.com"},
        {"name": "BollyNews UK", "url": "https://bollynewsuk.com"},
        {"name": "BizAsiaLive", "url": "https://bizasialive.com"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/65/Aamir_Khan_at_the_success_bash_of_Secret_Superstar.jpg",
    "image_caption": "Aamir Khan, whose In Conversation session closes the London Indian Film Festival 2026",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}

# ── INSERT ────────────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
