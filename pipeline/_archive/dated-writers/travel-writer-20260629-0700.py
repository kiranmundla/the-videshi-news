#!/usr/bin/env python3
"""Travel writer — 2026-06-29 07:00 PDT batch."""

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

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


articles = [
    # ── Article 1: Europe EES Chaos ──────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Europe's New Border System Is Causing Six-Hour Queues — and NRIs Are Caught in the Middle",
        "subheadline": "The EU's Entry/Exit System went live in April. Rome's airports are already threatening to suspend it before the summer crush arrives.",
        "slug": make_slug("europe-ees-border-system-queues-nri-summer-travel"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Millions of NRIs transit through Frankfurt, Amsterdam, Paris CDG and Rome every summer on India-bound flights — and this year the new biometric border checks could add hours to their layovers.",
        "tags": ["travel", "europe", "visa", "airports", "schengen", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/italy-europe-entry-exit-system-ees-airport-disruption/"},
            {"name": "The Sun", "url": "https://www.thesun.co.uk/travel/35009751/two-european-airports-scrap-entry-rules-disaster/"},
            {"name": "AFAR", "url": "https://www.afar.com/magazine/japan-triples-departure-tax"},
            {"name": "ACI Europe", "url": "https://www.aci-europe.org/"},
            {"name": "Breaking Travel News", "url": "https://www.breakingtravelnews.com/news/article/lufthansa-group-welcomes-visa-free-airport-transit-for-indian-nationals-via-germany/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2612113/pexels-photo-2612113.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "Crowded airport terminal with travellers queuing at border control",
        "image_attribution": "Pexels",
        "body": """Europe has a new gatekeeper, and it is not handling the summer rush well.

The European Union's Entry/Exit System — EES for short — went fully operational across all Schengen countries in April 2026. The system replaces manual passport stamps with digital registration: fingerprints, facial scans, and a biometric record that tracks when non-EU nationals enter and leave the bloc. Every Indian passport holder, every Green Card–toting NRI connecting through Frankfurt or Amsterdam, every OCI cardholder transiting Paris Charles de Gaulle is now subject to it.

The problem is that the infrastructure cannot keep up with the people.

## Six-Hour Queues and Broken Kiosks

At major European hubs — Rome Fiumicino, Paris CDG, Frankfurt, Amsterdam Schiphol, Athens, Lisbon — travellers have reported queues stretching to six hours at passport control since the system launched. The self-service EES kiosks that were supposed to speed up the process "don't work," according to Olivier Jankovec, head of ACI Europe, the airports industry group. Biometric errors, system overloads, and cascading delays during peak hours have turned what was meant to be a modern, frictionless border into the longest bottleneck in European aviation.

Rome's airport operator has had enough. Aeroporti di Roma CEO Marco Troncone told the Financial Times that both Fiumicino and Ciampino airports may suspend EES checks entirely during the summer peak. "The process proves to be incompatible with the peak volumes that we are going to face," he said, rating his concern an "eight or nine" out of ten. "The only way is to open up the valve."

Fiumicino alone handles over five million passengers a month in summer — up to 180,000 in a single day. If the system buckles there, the ripple effects hit connecting flights across the continent.

## Why NRIs Should Care

For the average Indian American flying to India this summer, Europe is not the destination — it is the layover. Millions of NRIs connect through European hubs on carriers like Lufthansa, Air France-KLM, SWISS, and Turkish Airlines. A two-hour Frankfurt transit that once involved little more than walking between gates now requires clearing the full EES biometric enrollment on your first post-April visit.

The timing is particularly galling. Germany waived its airport transit visa requirement for Indian nationals just weeks ago, on June 3 — a move Lufthansa celebrated as a way to "make journeys via key German hubs more seamless." France had done the same in April. Both policy changes were meant to make European connections easier for Indians. The EES queues have wiped out much of that gain.

There is one small consolation: the EES enrollment is a one-time affair. Once your biometrics are registered, subsequent entries should be faster — the system checks you against the database rather than enrolling you afresh. But "should" is doing a lot of heavy lifting given the current state of the kiosks.

## What You Can Actually Do

If you are flying through a European hub this summer, assume the worst and plan accordingly:

- **Build a three-hour minimum connection.** Athens airport is already advising passengers to arrive at least two and a half hours before departure just for the border-processing stage. A tight 90-minute layover at Schiphol is now a gamble.
- **Fly nonstop when you can.** Air India, United, and Delta all fly nonstop between major US cities and India. The routes cost more and some are operating reduced schedules this summer, but skipping the European transit eliminates the EES variable entirely.
- **Carry all documents in paper.** The system cross-references your visa and passport. If a kiosk fails, a CBP-style officer processes you manually — and they will want to see everything.
- **Check airline advisories.** KLM and British Airways have begun adjusting check-in timings at affected hubs. Your airline may contact you with revised boarding guidance.

## The Bigger Picture

The EU designed the EES to replace its aging passport-stamp system and to better track visa overstays. In principle, it is a sensible modernization. In practice, rolling it out just before Europe's busiest travel season — when airports are already straining under record passenger volumes — has been, in the words of one industry executive, flirting with "disaster."

ETIAS, the EU's separate pre-travel authorization system (similar to America's ESTA), has been pushed to late 2026 at the earliest. When it arrives, it will add yet another layer of screening for Indian travellers visiting Europe — a €20 online application required before boarding.

For now, the message for NRI summer travellers is straightforward: Europe's borders are digital, but they are not yet fast. Pack patience alongside your passport.""",
    },

    # ── Article 2: Japan Travel Gets Expensive July 1 ────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Japan Triples Its Exit Tax Tomorrow — but the Weak Yen and New Nonstops Give NRI Travellers a Reason to Go Anyway",
        "subheadline": "Visa fees quintuple, the 'Sayonara Tax' jumps to ¥3,000, and Kyoto is taxing luxury hotels. Yet the yen is at ¥158 to the dollar, Air India just launched Mumbai-Tokyo, and the Shinkansen is rolling out private cabins.",
        "slug": make_slug("japan-sayonara-tax-triples-visa-fees-nri-travel-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "With Air India launching Mumbai-Tokyo Haneda, JAL flying Delhi-Narita, and Japan hitting a record 300,000 Indian visitors last year, the India-Japan travel corridor has never been stronger — making the new fees a practical concern for a growing NRI audience.",
        "tags": ["travel", "japan", "visa", "airlines", "air-india", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CNN Travel", "url": "https://www.cnn.com/travel/japan-bullet-train-private-rooms-sayonara-tax/index.html"},
            {"name": "AFAR", "url": "https://www.afar.com/magazine/japan-triples-departure-tax"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/japan-visa-fee-increase-tourism-immigration-reform/"},
            {"name": "AeroRoutes", "url": "https://aeroroutes.com/2026/03/05/air-india-adds-mumbai-tokyo-service-from-june-2026/"},
            {"name": "Parade", "url": "https://parade.com/living/japan-tourist-taxes-2026"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/33172481/pexels-photo-33172481.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "Tokyo Tower rises behind the historic Zojoji Temple under a clear summer sky",
        "image_attribution": "Pexels",
        "body": """Starting July 1, the cost of visiting Japan goes up — in several directions at once.

The country's departure levy, informally known as the "Sayonara Tax," will triple from ¥1,000 to ¥3,000 (roughly $6 to $19). Japan's single-entry tourist visa fee — the one Indian passport holders must pay — has already jumped from ¥3,000 to ¥15,000, the largest increase in nearly five decades. And cities like Kyoto are layering on their own tiered accommodation taxes, with higher nightly surcharges for luxury stays.

For the 300,000-plus Indians who visited Japan in 2025 — a record — and the diaspora travellers who increasingly add Tokyo, Kyoto, and Osaka to their Asia itineraries, the math just changed.

## What Exactly Is Changing

**The Sayonara Tax** was introduced in 2019 at ¥1,000 per person. It is baked into your airfare, so you never pay it in person — but you feel it in the ticket price. From tomorrow, it triples. The government says the revenue will fund overtourism countermeasures, airport infrastructure (including more facial-recognition gates to speed up passport control), and promotion of less-visited regions.

**Visa fees** are the bigger hit for Indian travellers. A single-entry tourist visa now costs ¥15,000 (about $100 or ₹8,400), up from ¥3,000. Multiple-entry visas have risen proportionally. Japan also ended walk-in visa applications in four Indian cities — Chennai, Hyderabad, Kochi, and Puducherry — in March, making prior appointments mandatory. Processing takes 3–7 working days.

**Local taxes** are multiplying. Kyoto now charges a tiered accommodation tax that hits luxury stays hardest. Hiroshima has added a nightly fee. Gifu and Toba have introduced flat per-night levies. The Japan Rail Pass, the workhorse of tourist transit, is also due for another price increase later this year.

Add it all up, and a family of four visiting Japan for ten days will pay roughly $80 more in taxes and fees than they would have in 2025 — before accommodation surcharges.

## The Silver Lining: A Weak Yen and Better Flights

Japan's fees are rising, but its currency is not. The yen has hovered around ¥158–160 to the dollar through 2026, making Japan considerably more affordable than it was five years ago when the rate was closer to ¥110. A mid-range daily budget of ¥25,000–40,000 per person works out to just $165–265 — roughly on par with a Bangkok trip at a significantly higher quality tier.

The air connectivity between India and Japan has never been stronger. Air India launched four-weekly nonstop flights between Mumbai and Tokyo Haneda on June 15, using Boeing 787-8 Dreamliners. That supplements its existing daily Delhi-Haneda service. Japan Airlines has been operating Delhi-Narita since January 2026, with an expanded codeshare with IndiGo that connects Tokyo to dozens of Indian cities via Delhi and Bengaluru.

For NRIs in the US, the options are even wider. United, ANA, JAL, Delta, and several Gulf carriers fly nonstop or one-stop to Tokyo from every major American hub. The weak yen means your dollar stretches further on the ground — even if the entry paperwork costs more.

## The Shinkansen Gets a Premium Upgrade

Japan's rail system is also making a play for high-end travellers. Starting this October, select Tokaido Shinkansen services between Tokyo and Kyoto/Osaka will offer "Supreme Class" — private cabins with lockable doors, adjustable lighting and climate, and small sofas in the largest rooms. A new sleeper car service called "Luna Azul" (blue moon) will debut in 2027 on the Tohoku route to northeast Japan, offering lie-flat seats.

For NRI families who typically do a Tokyo-Kyoto-Osaka loop, the Supreme Class cabins could be worth the splurge — particularly if you are travelling with elderly parents who find economy-class bullet trains tiring.

## The NRI Calculation

Japan is not becoming unaffordable. It is becoming more deliberately priced. The government has been transparent: record tourism is straining infrastructure, and visitors should contribute more to maintaining it. That is a reasonable ask for a country where temples are being overrun, Shinkansen platforms are dangerously crowded, and Kyoto's geisha district has had to ban tourist photography.

For Indian and NRI travellers, the practical takeaway is:

- **Budget an extra ₹10,000–15,000 per person** for visa fees, departure tax, and local levies compared to pre-2026 trips.
- **Book the Japan Rail Pass before you depart** — it cannot be purchased inside Japan, and locking in the current price protects you from the late-2026 hike.
- **Apply for your visa early.** Walk-in processing is gone in most South Indian cities. Book a VFS appointment at least three weeks ahead of travel.
- **Consider the shoulder season.** October and November — after the summer peak but before winter — offer lower hotel rates, thinner crowds, and some of the most beautiful foliage in the world. The new Shinkansen Supreme Class will be live by then.

The yen giveth, the tax man taketh. On balance, Japan in 2026 remains a strong-value destination for the Indian diaspora — just one that requires a bit more planning than it did last year.""",
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
