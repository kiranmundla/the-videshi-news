#!/usr/bin/env python3
"""Travel writer — July 3, 2026 batch: Europe visa revolution articles."""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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

# ─────────────────────────────────────────────
# Article 1: Germany/France transit visa waiver
# ─────────────────────────────────────────────

art1_body = """Germany and France have both scrapped the airport transit visa for Indian passport holders — and if you're an NRI who routes through Frankfurt or Paris on the way home, this changes the economics and logistics of every trip.

## What changed

Germany removed its Type A transit visa requirement for Indian nationals on June 3, 2026, following publication in the Federal Law Gazette. The policy was announced during Chancellor Friedrich Merz's January visit to India and formalised five months later. France had already made the same move in April 2026.

Previously, an Indian passport holder connecting through Frankfurt, Munich, or Charles de Gaulle — even without leaving the international transit zone — needed a Schengen airport transit visa. The process cost roughly €90, required confirmed onward tickets, travel insurance, passport photos, and up to 15 business days of processing. A missed appointment or delayed visa could ground an entire itinerary.

That requirement is now gone. Indian travellers transiting airside through five German airports (Frankfurt, Munich, Berlin-Brandenburg, Hamburg, and Düsseldorf) and French airports no longer need to apply for, pay for, or carry a separate transit visa.

## Why NRIs should care

The Delhi–SFO, Mumbai–JFK, and Hyderabad–Chicago corridors all have competitive one-stop options through Frankfurt and Paris on Lufthansa, Air France, and their Star Alliance and SkyTeam partners. Until now, Indians travelling on their Indian passport — including OCI cardholders who fly on both documents — faced an extra paperwork hurdle that US, Canadian, and Japanese passport holders did not.

The change doesn't just save €90. It eliminates two to three weeks of visa lead time, removes the risk of a transit visa denial disrupting a booked itinerary, and opens up last-minute rebooking through European hubs that was previously impractical.

For NRI families visiting India with elderly parents who hold Indian passports, the waiver is especially welcome. A grandparent joining the family for a summer trip via Lufthansa can now transit through Frankfurt without a side quest to the German consulate.

## The Schengen visa cascade — multi-year passes for repeat travellers

Separately, the EU has introduced a "cascade" regime specifically for Indian nationals. Under rules adopted by the European Commission, Indians who have obtained and lawfully used two Schengen visas within the previous three years can now apply for a two-year, multiple-entry visa. After using that two-year visa, they become eligible for a five-year, multiple-entry Schengen visa — provided their passport has sufficient remaining validity.

During the validity period, holders travel freely across all 29 Schengen countries for stays of up to 90 days in any 180-day window. For NRIs who visit Europe once or twice a year — a ski trip in winter, a family holiday in summer — this effectively means one visa application every five years instead of one per trip.

More than 51 per cent of all Schengen visas issued in 2025 were already multiple-entry, reflecting how the system has shifted toward rewarding established travel history over one-off applications.

## What's coming: ETIAS in late 2026

One complication on the horizon: the European Travel Information and Authorisation System (ETIAS) is expected to launch in the fourth quarter of 2026. ETIAS is a pre-travel digital authorisation — similar to the US ESTA — required of visa-exempt travellers entering the Schengen Area.

For Indian passport holders, who still require Schengen visas, ETIAS itself is not directly relevant. But the EU's Entry/Exit System (EES), which replaces manual passport stamping with biometric registration, is already live and applies to all non-EU travellers on short stays. First-time arrivals must register fingerprints and facial images at the border — a process that has been adding significant time at major airports including Frankfurt, Paris CDG, Rome, and Madrid.

NRIs travelling on US passports through Europe may face ETIAS requirements and should budget for the €20 fee and a slightly longer immigration queue when the system goes live.

## The practical checklist

For Indian passport holders transiting through Germany or France, the new rules are straightforward but come with fine print:

- **Airside only.** The exemption covers staying within the international transit zone. If your itinerary requires changing terminals, collecting checked bags, staying overnight, or entering the Schengen zone, you still need a regular Schengen visa.
- **Non-Schengen destinations.** The transit waiver applies when your final destination is outside the Schengen Area — the US, UK, Canada, or any non-Schengen country.
- **German airports with transit zones.** Only Frankfurt, Munich, Berlin-Brandenburg, Hamburg (4:30 AM–11:30 PM), and Düsseldorf (6 AM–9 PM, by airline arrangement) have international transit areas.
- **Build your Schengen history.** If you travel to Europe at all, apply for your first Schengen visa through a country with a strong Indian approval rate — Germany, Switzerland, Italy, and Belgium all recorded relatively high issuance rates in 2025.
- **Watch passport validity.** Multi-year Schengen visas cannot exceed your passport's expiry date. Renew your passport before applying if it has fewer than three years left.

Between the transit visa waivers and the multi-year cascade, Europe has quietly become meaningfully easier for Indian passport holders in 2026. The days of paying €90 to sit in a Frankfurt departure lounge for two hours are, mercifully, over."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Germany and France Dropped Transit Visas for Indians — What It Means for NRIs Flying Through Europe",
    "subheadline": "Frankfurt and Paris are now hassle-free layover hubs for Indian passport holders, and a new EU visa cascade lets frequent travellers get five-year Schengen visas.",
    "slug": make_slug("germany-france-transit-visa-waiver-india-nri-europe"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs flying between the US and India often connect through Frankfurt and Paris — these transit visa waivers save €90 per trip and eliminate weeks of paperwork for anyone travelling on an Indian passport.",
    "tags": ["travel", "visa", "europe", "schengen", "germany", "france", "transit"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "German Embassy / MEA India", "url": "https://x.com/MEAIndia/status/1929507000000000000"},
        {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/destinations/international/germany-removes-airport-transit-visa-rule-for-indians"},
        {"name": "iVisa", "url": "https://www.ivisa.com/germany-transit-visa-waiver"},
        {"name": "EU EEAS", "url": "https://www.eeas.europa.eu/eeas/european-union-adopts-more-favourable-schengen-visa-rules-indians_en"},
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/belgium-partners-france-italy-spain-schengen-bloc-eu-digital-visa-system/"},
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Frankfurt_Flughafen%2C_Terminal_1%2C_Abflughalle_B.jpg/1280px-Frankfurt_Flughafen%2C_Terminal_1%2C_Abflughalle_B.jpg",
    "image_caption": "Frankfurt Airport Terminal 1 departure hall, one of Europe's busiest transit hubs",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
}

# ─────────────────────────────────────────────
# Article 2: Switzerland overtakes as #1 Schengen destination for Indians
# ─────────────────────────────────────────────

art2_body = """For the first time, Switzerland has overtaken France and Germany as the most popular Schengen destination among Indian visa applicants. The shift, revealed in the European Commission's latest visa data for 2025, reflects a deeper change in how Indians — and especially NRIs planning European side trips — think about continental travel.

## The numbers

Indian nationals filed more than 1.15 million Schengen visa applications in 2025, a record. Switzerland drew the largest share, displacing France and Germany, which had led for years. Across the Schengen Area, more than 51 per cent of all visas issued to Indians were multiple-entry, meaning holders could return without reapplying.

But the picture is not uniformly rosy. Roughly 181,000 Indian applications did not result in a visa being issued — about one in six. Approval rates varied sharply by country: Germany, Switzerland, Italy, and Belgium recorded stronger outcomes, while Slovenia, Greece, Austria, and the Netherlands had comparatively higher refusal rates.

## Why Switzerland?

The Swiss surge is not accidental. Several forces converged.

**Bollywood's long tail.** Switzerland has been a fixture in Hindi cinema since *Dilwale Dulhania Le Jayenge* in 1995. The Jungfraujoch observation deck — which still maintains a "Bollywood" restaurant and an SRK-Kajol cutout — draws Indian tourists who grew up watching alpine meadows as a backdrop to romance. That cultural imprint has proven remarkably durable, surviving three decades and multiple generations of moviegoers.

**Scenic rail tourism.** The Grand Train Tour of Switzerland — a 1,280-kilometre circuit linking the Glacier Express, Bernina Express, GoldenPass Panoramic, and Gotthard Panorama Express — has become a signature product for Indian visitors. The Swiss Travel Pass, which bundles trains, buses, boats, and discounted mountain excursions, simplifies logistics for a country where driving is expensive and unnecessary.

**Targeted marketing.** Switzerland Tourism has aggressively courted Indian travellers, including a winter campaign featuring Olympic gold medallist Neeraj Chopra. The push to promote winter tourism — skiing, snow activities, heated panoramic trains — directly addresses the seasonality problem: most Indians visit in summer, creating overcrowding from June to August. By marketing winter as equally appealing, the Swiss have spread demand across the year.

**Direct air connectivity.** Expanded services from Air India and IndiGo to European hubs, combined with transit visa waivers through Germany and France, have made reaching Switzerland cheaper and faster. Indians no longer need to fly through a single constrained gateway.

## What NRIs should know

For NRIs based in the US who visit India annually, a European stopover is increasingly common. A few practical points:

**Build your cascade.** Under the EU's new visa rules for Indian nationals, two successful Schengen trips within three years qualify you for a two-year, multiple-entry visa. Use that, and your next application can be for a five-year pass. If you're visiting Europe even occasionally, start building that history now — each approved trip makes the next one easier.

**Apply through Switzerland or Germany.** Your Schengen application should go to the country where you'll spend the most nights. But if your itinerary splits evenly, choosing a country with a high Indian approval rate — Switzerland, Germany, Italy, or Belgium — can improve your odds. The country of application can make the difference between a two-week turnaround and a rejection.

**Budget realistically.** Switzerland is the most expensive country in Europe. A 10-day trip for two costs roughly ₹5–6 lakh (about $6,000–7,000), including flights from India. The Swiss Travel Pass (from CHF 232 for three consecutive days) saves money on transport but mountain excursions — Jungfraujoch, Pilatus, Titlis — carry separate charges. Budget travellers should eat at Coop and Migros supermarkets rather than restaurants, where a simple lunch can exceed CHF 25.

**Timing matters.** July and August are peak season, with the highest prices and thickest crowds at popular spots like Interlaken and Zermatt. September and October offer quieter trails, lower hotel rates, and autumn colours. For the Bollywood pilgrimage — Jungfraujoch, the Titlis revolving cable car, Lake Lucerne — spring (April–May) is arguably the best season: the snow is still on the peaks, the wildflowers are out, and you won't queue for an hour to reach the Sphinx Observatory.

**Don't overlook the rejection rate.** One in six Indian Schengen applications was refused in 2025. The most common reasons are insufficient financial documentation, unclear travel purpose, and weak ties to the home country. NRIs should include US residence proof (green card, work visa, tax returns) alongside their Indian passport application to demonstrate both financial capacity and intention to return.

## The bigger picture

India's Schengen demand is part of a broader shift. The Indian passport now ranks 77th on the Henley Passport Index — up from 85th — with visa-free access to 56 destinations. That is still far below the US passport at 186 destinations, but the trajectory is upward. Transit visa waivers from Germany and France, multi-year Schengen cascades, and Malaysia's visa-free window for Indian nationals all point in the same direction: the Indian passport is slowly gaining ground.

For Switzerland, the Indian market is now too large to ignore. Over 775,000 Indian overnight stays were recorded in Germany alone between January and October 2025, and the German tourist office is targeting one million by the end of 2026. Switzerland, with its smaller footprint but higher per-visitor spend, is betting that India's travel class will keep coming — not just in summer, not just for the mountains, and not just because of a 30-year-old Bollywood film."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Switzerland Just Overtook France as India's Top Schengen Destination — 1.15 Million Applications and Counting",
    "subheadline": "Indian visa applications to Europe hit a record in 2025, and for the first time Switzerland drew more applicants than France or Germany — driven by Bollywood nostalgia, scenic trains, and a new multi-year visa regime.",
    "slug": make_slug("switzerland-overtakes-france-india-schengen-visa-record-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs visiting family in India often tack on a European stopover — and Switzerland's new multi-year visa cascade means frequent travellers can lock in a five-year Schengen pass after just two prior trips.",
    "tags": ["travel", "visa", "europe", "switzerland", "schengen", "tourism", "bollywood"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/switzerland-overtakes-france-germany-indian-schengen-visa-applications/"},
        {"name": "EU EEAS", "url": "https://www.eeas.europa.eu/eeas/european-union-adopts-more-favourable-schengen-visa-rules-indians_en"},
        {"name": "Livemint", "url": "https://www.livemint.com/news/india/switzerland-tourism-winter-campaign-indian-travellers-11696511432963.html"},
        {"name": "MySwitzerland.com", "url": "https://www.myswitzerland.com/en/experiences/experience-tour/grand-train-tour-of-switzerland/"},
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7938364/pexels-photo-7938364.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "The Bernina Express curves through the Swiss Alps, one of Switzerland's iconic scenic train routes",
    "image_attribution": "Pexels",
    "body": art2_body.strip(),
}

# ─────────────────────────────────────────────
# Insert
# ─────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
