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

dhume_body = """A think tank does not usually telegraph its priorities through a single hire. The Council on Foreign Relations did exactly that on June 3, when it named Sadanand Dhume a senior fellow for India, Pakistan, and South Asia in its David Rockefeller Studies Program. The appointment says less about one journalist's career than about where America's foreign-policy establishment thinks the next decade of strategic attention will go.

Dhume is not an obvious institutional pick. For years he wrote the *Wall Street Journal*'s biweekly "East Is East" column, a perch from which he argued, more often than his readers in New Delhi liked, that India's economic promise was being throttled by its own bureaucracy and that its foreign policy frequently overpromised. He arrives at CFR from the American Enterprise Institute, a conservative-leaning shop, and brings a reporter's instinct for the uncomfortable detail rather than the diplomat's instinct for the smooth one.

## A reporter, not a diplomat

"Sadanand's distinctive experience as a reporter and scholar covering South Asia will provide integral insight into this important and dynamic region and implications for U.S. foreign policy there," said Shannon K. O'Neil, CFR's senior vice president, in the statement announcing the move.

The phrasing matters. CFR has been steadily building South Asia capacity, and Dhume's hire fits a pattern of betting on analysts who challenge the consensus rather than reinforce it. His research will focus on the region's political economy and foreign policy — the unglamorous machinery of trade rules, capital flows, and bilateral friction that increasingly defines whether the much-touted U.S.-India partnership delivers anything beyond summit photographs.

## The diaspora's quiet pipeline

For the Indian diaspora, Dhume's trajectory is a familiar one, even if its destination is rarer. He earned a bachelor's in sociology from the University of Delhi, then a master's in journalism from Columbia and a master's in public affairs from Princeton — the standard immigrant escalator of credentialing, but pointed at the interpretive professions rather than the engineering and medicine that absorb most Indian-American talent.

That distinction is the story. The diaspora has supplied America with an abundance of doctors, founders, and CEOs. It has supplied far fewer people whose job is to tell Washington what to think about the subcontinent. The think-tank world, the op-ed pages, the congressional testimony rooms — these are the venues where India's image in American policy is actually manufactured, and they have long been thin on Indian-origin voices who can speak with both insider fluency and outsider candor.

Dhume has testified before Congress on U.S.-India relations and appeared on CNN, the BBC, PBS, NPR, and Al Jazeera. His forthcoming book, *Tinderbox: The Unpredictable Rise and Uncertain Future of Modern India*, promises the kind of argument — that India's ascent is neither guaranteed nor linear — that diaspora audiences often find bracing precisely because it refuses the triumphalist script.

## Why the timing is loaded

The appointment lands at an awkward moment for the relationship Dhume will analyze. Washington is hedging its bets on New Delhi even as it courts it; Beijing is pressing along the Himalayan frontier; and India's own political class has grown warier of foreign entanglement. A senior fellow whose columns have needled all three capitals is, in that light, less a safe choice than a deliberate one.

For NRIs who follow these debates from Silicon Valley boardrooms or New Jersey dinner tables, the elevation of a diaspora analyst to one of America's most influential foreign-policy institutions is its own kind of milestone — a sign that the community's influence is migrating from the spreadsheet to the seminar room. Whether Dhume's contrarian streak survives contact with CFR's institutional caution is the question worth watching. The think tank, by hiring him, has bet that it will."""

aia_body = """Founded in 1967, the Association of Indians in America — New York Chapter is older than most of the people it now honors. When a few dozen recent immigrants set it up nearly six decades ago, the Indian-American population was a rounding error in the U.S. census. On the evening of its 2026 Annual Benefit Gala at Terrace on the Park in Flushing, the room held more than 300 guests, a state comptroller at the podium, and seven honorees whose résumés would have been unimaginable to the organization's founders.

That distance — from a handful of newcomers finding their footing to an establishment dispensing awards to Padma Bhushan recipients — is the real subject of these galas, even when the speeches are about the honorees.

## The "Ratnas"

AIA-NY recognized seven individuals as "Ratnas," or jewels of the community, a framing that deliberately borrows the vocabulary of Indian classical honor and transplants it onto American achievement. The list reads like a cross-section of where the diaspora has concentrated its ambition.

Dr. Dattatreyudu Nori, an oncologist with more than five decades at institutions including Memorial Sloan Kettering, was honored after a year in which he received both the Padma Shri and Padma Bhushan. Dr. Sahil Khera of Mount Sinai Heart has performed more than 2,000 structural heart procedures. Dr. Aprajita Mattoo of NYU Langone has played a role in the historic pig-to-human kidney transplant trials, a frontier of xenotransplantation that could one day ease the organ shortage.

The honorees were not only physicians. Manish Dhadda, co-founder of the jewelry house VIBHOR, was recognized for blending entrepreneurship with philanthropy. Jessica Kalra, an attorney whose background includes a stint in Senator Hillary Clinton's office, advises the American Punjabi Society. Dr. Jagat Rawal kept his Queens medical practice open through the pandemic and now leads physician education at AAPI-QLI.

## The youngest jewel

The honoree who arguably said the most about the community's trajectory was its youngest. Pulkita Kini, currently pursuing an MBA at Harvard Business School with prior stints at Microsoft and Cloudflare, is building Tara AI, a venture meant to help publishers control and monetize their content in the age of artificial intelligence.

A second-generation technologist working on the frontier of AI, honored in the same room as a five-decade oncologist, captures the generational handoff these organizations are quietly managing. The founders' generation built institutions to preserve identity in an unfamiliar country. The next generation is being asked to inherit them while also racing ahead into industries the founders could not have named.

## The festival underneath the gala

AIA-NY is best known not for its galas but for its Deepavali Festival, which it has staged in New York for 38 years. At the gala, the organization announced its 39th edition — scheduled for October 3 at Overlook Beach in Babylon, Long Island, with a rain date of October 10 — complete with live fireworks underwritten by a community sponsor.

That continuity is the point. A spelling bee, an awards dinner, a fireworks display over a Long Island beach — individually they are small. Collectively they are the infrastructure by which a diaspora keeps a culture legible to its own children, in a country that did not, until recently, mark Diwali on any official calendar. New York City has now declared the festival a public-school holiday, a recognition that the founders of 1967 would likely have found astonishing.

## Why these rituals endure

It is easy to be cynical about community galas — the proclamations from state senators, the citations from county executives, the procession of honorees. But the cynicism misses what the events actually do. They convert individual success into collective memory, and they hand the next generation a template for how to belong without disappearing.

President Beena Kothari put it plainly in her closing remarks, thanking the volunteers "working tirelessly behind the scenes." The honorees stand at the podium; the organization that put them there is the quieter achievement. After 59 years, AIA-NY's real product is not the awards. It is the fact that there is still a room full of people who show up to give them."""

glo_body = """The most consequential moment at a New Jersey banquet hall last month was not an award. It was the unveiling of a website. At the inaugural "Icons of Impact" Gala hosted by the Global Indian Diaspora Alliance, or GLO-INDIA, Ambassador Binaya S. Pradhan, India's Consul General in New York, introduced the India–USA Trade Facilitation Portal — a government-backed digital platform meant to grease the wheels of bilateral commerce. For a gala built around honoring people, it was a telling choice of centerpiece.

The subtext was clear enough. The Indian diaspora in America is no longer being asked merely to celebrate its own success. It is being recruited as infrastructure for a $500 billion ambition.

## Mission 500

Pradhan, addressing roughly 200 guests, framed the portal around a target both governments have embraced: "Mission 500," the goal of more than doubling India-U.S. bilateral trade to $500 billion by 2030. He noted that trade between the two countries reached a record $241 billion over the past year, making the United States India's largest trading partner for the fourth consecutive year.

"The partnership between India and the United States is in one of its strongest chapters yet," the ambassador said.

The portal itself is described as a first-of-its-kind platform developed by the Consulate General in New York — a single digital front door for businesses trying to navigate the friction of cross-border trade. Whether it lives up to that billing will depend on execution that no gala can guarantee. But the venue for its launch was not accidental.

## The diaspora as a trade lever

GLO-INDIA claims a network of more than 18,000 members across five continents, and its president, H.S. Panaser, used the evening to position the organization as a connective tissue between Indian-origin professionals and the institutions of both countries. That is a familiar pitch. What is newer is the explicit fusion of community networking with state-backed economic policy.

The honorees reflected the strategy. Among them: Roop Singh, CEO of the Irish firm Version 1 and a former Birla Group chief executive; Ajit Mannon, Johnson & Johnson's global chief of commercial data, digital, and AI; Dr. Navneet Puri, a former Pfizer board director; and Dr. Badri Narayanan Gopalakrishnan, an economist. These are not ceremonial figures. They are precisely the people who sit at the intersection of capital, technology, and the two economies a trade portal hopes to bind together.

## When community organizations meet statecraft

For the diaspora, this convergence cuts two ways. On one hand, it elevates community organizations from cultural clubs into players with a seat near actual policy. Messages of congratulation arrived from the governors of both New Jersey and New York; state senators and mayors presented proclamations. That access is real, and for a community long accustomed to being courted only at election time, it represents a maturation.

On the other hand, it raises a quieter question about whose interests these platforms ultimately serve. A trade portal launched by a foreign consulate at a diaspora gala blurs a line that diaspora organizations have historically been careful about — the line between cultural belonging and the economic agenda of the ancestral state. NRIs who attended for the community recognition may find themselves enlisted, gently, into a bilateral commercial project.

## The morning after

None of this diminishes the evening's stated purpose. The lamp was lit, the anthems of both nations were sung, and eleven leaders were honored for genuine accomplishment across medicine, agriculture, pharmaceuticals, and public service. Community galas are, at their best, a way of telling a scattered people that their achievements are seen.

But the most revealing artifact of the night was the portal. It signals that the Indian diaspora's role in the U.S.-India relationship is shifting from symbolic to structural — from waving flags at a visiting prime minister to being treated as a working channel for trade. For a community that has spent decades proving it belongs, that is a promotion. It is also, depending on how it is used, a responsibility worth scrutinizing."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Contrarian WSJ Columnist Just Joined America's Top Foreign-Policy Club. CFR Picked Him on Purpose.",
        "subheadline": "The Council on Foreign Relations named Sadanand Dhume a senior fellow for South Asia. The hire reveals where Washington thinks the next decade of strategic attention is heading.",
        "slug": make_slug("sadanand-dhume-cfr-senior-fellow-south-asia-diaspora-policy"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The diaspora has supplied America with abundant doctors, founders, and CEOs, but few people whose job is to shape how Washington thinks about the subcontinent. Dhume's elevation signals the community's influence migrating from the spreadsheet to the seminar room and the congressional testimony chair.",
        "tags": ["nri", "diaspora", "sadanand-dhume", "cfr", "us-india", "policy", "academia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Council on Foreign Relations", "url": "https://www.cfr.org/news-releases/cfr-welcomes-sadanand-dhume-senior-fellow-india-pakistan-and-south-asia"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/council-on-foreign-relations-appoints-sadanand-dhume-as-senior-fellow-for-south-asia/"},
            {"name": "South Asian Herald", "url": "https://southasianherald.com/sadanand-dhume-joins-council-on-foreign-relations-as-senior-fellow-for-south-asia/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/en/6/65/Sadanand_Dhume_crop.jpg",
        "image_caption": "Sadanand Dhume, newly appointed senior fellow for India, Pakistan, and South Asia at the Council on Foreign Relations",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": dhume_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Fifty-Nine Years On, America's Oldest Indian Association Handed Out Jewels — Including One to a Harvard MBA Building an AI Startup",
        "subheadline": "AIA-NY's 2026 Benefit Gala honored seven 'Ratnas' spanning five decades of oncology to the frontier of artificial intelligence. The generational handoff was the real story.",
        "slug": make_slug("aia-ny-benefit-gala-2026-ratnas-oldest-indian-association-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Community galas convert individual immigrant success into collective memory and hand the next generation a template for belonging without disappearing. After 59 years, AIA-NY's real product is not the awards but the fact that a room still fills to give them — and that New York now marks Diwali as a public-school holiday.",
        "tags": ["nri", "diaspora", "aia-ny", "new-york", "community", "diwali", "indian-american"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/11/aia-ny-hosts-grand-annual-benefit-gala-2026-to-honor-individuals-for-outstanding-contributions/"},
            {"name": "Association of Indians in America - NY Chapter", "url": "https://www.aiany.org/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/19793999/pexels-photo-19793999.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An Indian community celebration on stage, evoking the awards galas that anchor diaspora organizations in the United States",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": aia_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "At a New Jersey Gala, India Launched a Trade Portal and Quietly Recruited the Diaspora Into a $500 Billion Bet",
        "subheadline": "GLO-INDIA's inaugural 'Icons of Impact' Gala honored eleven leaders. The night's most revealing artifact was a website built to double U.S.-India trade by 2030.",
        "slug": make_slug("glo-india-icons-impact-gala-trade-portal-mission-500-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Indian diaspora in America is shifting from symbolic to structural in the U.S.-India relationship — from waving flags at a visiting prime minister to being treated as a working channel for trade. That is a promotion, and also a responsibility worth scrutinizing, as the line blurs between cultural belonging and the ancestral state's economic agenda.",
        "tags": ["nri", "diaspora", "glo-india", "us-india-trade", "mission-500", "new-jersey", "consulate"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Panorama", "url": "https://www.theindianpanorama.news/global-indian-diaspora-alliance-glo-india-hosts-landmark-icons-of-impact-gala-in-new-jersey-honoring-leadership-and-legacy/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/ambassador-pradhan-cites-new-trade-portal-as-central-to-mission-500-at-glo-india-gala/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/19793934/pexels-photo-19793934.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A diaspora community gathering on stage, the kind of gala where business, diplomacy, and culture increasingly converge",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": glo_body,
    },
]

# word count check
for art in articles:
    wc = len(art["body"].split())
    print(f"WORDS [{art['slug'][:40]}]: {wc}")

print("---")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
