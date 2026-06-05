#!/usr/bin/env python3
"""
Videshi Lifestyle & Markets Writer — Run 2026-06-05
Produces 1 lifestyle-health article + 1 markets-finance article.
"""

import json, os, sys, uuid, requests, io
from datetime import datetime, timezone
from PIL import Image

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
UA = "TheVideshi/1.0 (thevideshi.com)"

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def download_image(url):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
    r.raise_for_status()
    ct = r.headers.get('Content-Type', '')
    if not ct.startswith('image/'):
        raise ValueError(f"Not an image: {ct}")
    if len(r.content) < 5000:
        raise ValueError(f"Image too small: {len(r.content)} bytes")
    return r.content

def upload_to_supabase(img_bytes, filename):
    """Upload image to Supabase storage bucket 'article-images'."""
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
    if r.status_code not in (200, 201):
        # Try PUT for upsert
        r = requests.put(url, headers=headers, data=img_bytes, timeout=30)
    r.raise_for_status()
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
    print(f"  ✓ Uploaded to Supabase: {public_url}")
    return public_url

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) else data.get('id', 'unknown')
        print(f"  ✓ Inserted article: {article['headline'][:60]}... (ID: {art_id})")
        return art_id
    else:
        print(f"  ✗ Failed to insert: {r.status_code} {r.text[:200]}")
        return None

# ─────────────────────────────────────────────────────
# ARTICLE 1: Lifestyle-Health — Meditation brain changes
# ─────────────────────────────────────────────────────

article1_slug = "meditation-brain-changes-two-minutes-peak-seven-nimhans-isha-yoga-south-asian-20260605"
article1_headline = "Your Brain Starts Changing Within Two Minutes of Meditation. By Seven Minutes, It Peaks."
article1_subheadline = "A study from India's NIMHANS, using the Isha Yoga breath-watching tradition, shows measurable neural shifts happen faster than anyone assumed. For time-starved diaspora professionals, the science says even brief practice works."

article1_body = """India gave the world meditation more than five thousand years ago. Now a team of Indian neuroscientists has produced some of the most precise evidence yet for why even a few minutes of it rewires the brain.

A study published in the journal *Mindfulness* by researchers at the National Institute of Mental Health and Neuro Sciences (NIMHANS) in Bengaluru has mapped, minute by minute, exactly when and how the brain changes during a single session of breath-watching meditation drawn from the Isha Yoga tradition. The findings are striking: measurable neural changes begin within two minutes and reach peak intensity at around seven minutes — regardless of whether the practitioner is a complete novice or a seasoned meditator with years of silent retreats behind them.

## What the Study Did

Lead researcher Malipeddi Saketh and his colleagues recruited 103 participants across three groups: 28 people who had never meditated, 33 novice practitioners who had completed Isha Yoga's foundational Shambhavi Mahamudra training, and 42 advanced meditators who had completed an intensive eight-day silent retreat called Samyama.

Each participant sat in a temperature-controlled, soundproof room at NIMHANS with a 128-electrode EEG net recording their brainwaves at 1,000 measurements per second. They performed a simple breath-watching meditation — focusing on the natural flow of their breathing and gently returning attention when the mind wandered.

Rather than averaging brainwave data over the full session (the standard approach that flattens out moment-to-moment detail), the researchers tracked changes in one-minute intervals against the first 30 seconds as a baseline.

## The Seven-Minute Threshold

The results revealed a consistent temporal pattern across all three groups. Around the two-to-three-minute mark, participants showed increases in theta, theta-alpha, alpha, and beta1 brainwave power — frequencies associated with deep relaxation, calm focus, and sustained attention. Simultaneously, delta power (linked to drowsiness and mind-wandering) and gamma1 power (associated with active sensory processing) decreased.

These shifts peaked between seven and ten minutes into the session, suggesting the brain transitions into what researchers describe as a stable state of "relaxed alertness." After this peak, the neural signatures plateaued rather than continuing to intensify.

"One surprising finding was the consistency of the temporal pattern across multiple EEG measures," Saketh said. "We observed that several neural changes appeared to intensify around a similar time window rather than increasing linearly throughout the session."

## Beginners and Experts Differ in Interesting Ways

While the general pattern held across all groups, the details varied. Novice meditators showed delta and beta1 wave changes as early as the one-minute mark. Advanced meditators displayed a distinctive theta wave pattern: a brief initial decrease at one minute — interpreted as rapid neural reorganisation — before a sustained rise from the second minute onward.

The most revealing finding was that advanced practitioners carried distinct neural signatures from the very start of each session. Even during the first 30 seconds, before any deliberate practice began, they showed significantly higher theta and theta-alpha power than the other groups. This suggests long-term practice produces lasting structural or functional changes in the brain that persist outside meditation.

## Why This Matters for the Diaspora

For the millions of South Asians living abroad — many of them working long hours in demanding professional environments — the practical message is powerful. You do not need a 45-minute session, a silent retreat, or a teacher sitting beside you to access real neurological benefit. Seven minutes of focused breathing produces measurable changes in brain dynamics.

This is particularly relevant given the mental health landscape of the diaspora. Studies consistently show that South Asian immigrants in the United States, United Kingdom, and Canada face elevated rates of anxiety and depression, compounded by professional stress, cultural dislocation, and the quiet weight of intergenerational expectations. Yet mental health help-seeking remains stigmatised in many South Asian communities, with surveys indicating less than a third of South Asian Americans would consider professional therapy.

Meditation — especially the kind rooted in traditions many diaspora families already recognise — offers a scientifically validated, culturally familiar entry point. The NIMHANS study, conducted at one of India's most prestigious neuroscience institutions using a practice from the Isha Yoga lineage, adds institutional credibility within a framework the community already respects.

## The Broader Scientific Context

The study builds on a growing body of research linking meditation to neuroplasticity. A separate 2026 study from the University of California San Diego, published in *Communications Biology*, found that a seven-day residential retreat combining meditation with other mind-body techniques produced measurable changes in both brain activity and blood biology, activating pathways involved in brain flexibility, metabolism, and immune function.

And a seven-year follow-up from UC Davis's Shamatha Project showed that sustained attention gains from intensive meditation training persisted years after the retreat ended — suggesting these are not fleeting effects but durable changes in how the brain allocates resources.

The NIMHANS contribution is distinctive because it pinpoints the temporal dynamics — the when, not just the whether — and does so using a practice that emerged from Indian tradition and was tested on Indian participants in an Indian laboratory.

## What Comes Next

The research team plans to extend the work by combining EEG with MRI and autonomic measures to understand how short-term brain changes relate to long-term psychological and behavioural outcomes. They are particularly interested in identifying neural markers of advanced meditative states, including non-dual awareness and equanimity.

For now, the practical takeaway is simple and scientifically grounded: sit down, close your eyes, watch your breath. By the time two minutes pass, your brain has already begun to change. By seven minutes, it has reached its peak shift for that session. That is a powerful return on a very small investment of time — and a reminder that one of India's oldest exports may also be its most practical."""

article1_sources = json.dumps([
    "Saketh M. et al., 'Temporal EEG Signatures of Meditation Experience: Peak Brainwave Changes at 7 Minutes During Isha Yoga Breath Watching,' Mindfulness (2026)",
    "PsyPost, 'Brain changes during meditation begin within minutes and peak around the 7-minute mark, study finds' (May 2026)",
    "Patel H.H. et al., University of California San Diego, 'Mind-body retreat produces changes in brain activity and blood biology,' Communications Biology (2026)",
    "UC Davis Shamatha Project, 'Seven-Year Follow-Up Shows Lasting Cognitive Gains From Meditation,' Journal of Cognitive Enhancement"
])

# ─────────────────────────────────────────────────────
# ARTICLE 2: Markets-Finance — India IPO exits
# ─────────────────────────────────────────────────────

article2_slug = "foreign-firms-india-ipo-boom-ofs-exit-5-billion-nri-investors-20260605"
article2_headline = "Foreign Firms Are Using India's IPO Boom to Send $5 Billion Back to HQ. NRI Investors Should Understand Why."
article2_subheadline = "Five of six foreign companies that listed Indian units since 2024 raised zero new capital. The IPOs were structured purely as exits. For NRIs holding these stocks — or eyeing the next wave — the pattern matters."

article2_body = """India was the world's second-largest IPO market in 2025, with 367 listings raising $21.8 billion. The pipeline for 2026 is even deeper, with a record $26 billion worth of IPOs awaiting regulatory approval. To anyone tracking the numbers, the Indian public market looks like a machine for growth capital.

But a Reuters analysis published this week reveals a pattern that complicates that narrative considerably: for foreign companies listing their Indian units, the IPO boom is not about raising money to expand. It is about taking money out.

## The Numbers Tell the Story

Of the six foreign-based companies that listed their Indian subsidiaries on the Bombay Stock Exchange since 2024, only one — Britain's Bupa, through its unit Niva Bupa Health Insurance — structured the IPO to include fresh fundraising. And even there, the fresh component ($84 million) was dwarfed by the secondary offering ($146 million) that allowed existing shareholders to cash out.

The other five — the Indian units of Hyundai Motor, LG Electronics, Italy's Carraro, Norway's Orkla, and America's Tenneco Clean Air — were structured purely as offer-for-sale (OFS) IPOs. In an OFS, existing shareholders sell their holdings to the public. No new capital flows into the company. Every rupee raised goes to the parent.

In total, foreign parents pocketed nearly $5 billion through these secondary-offering IPOs, with Hyundai and LG accounting for more than 80 per cent of the take. According to Prime Database, for every dollar raised in these IPOs collectively, more than $59 left the country.

And the trend is accelerating. Walmart's Indian payments arm PhonePe is planning a $1 billion IPO that will follow the OFS route. Modern Times Group's $335 million IPO of its Indian gaming unit will do the same. Coca-Cola announced this week that its planned listing of its Indian bottler will include the American parent selling a portion of its stake. Banking sources say Carlsberg's Indian IPO will also raise no new funds.

## The Valuation Arbitrage

The economic logic is straightforward, and it runs on a single insight: Indian-listed subsidiaries consistently trade at enormous premiums to their foreign parents.

Nestle India carries a price-to-earnings ratio of nearly 77 times, versus 22 times for its Swiss parent. LG Electronics India, listed last year, trades at nearly 59 times earnings against 44 times for its South Korean parent. When Hyundai listed its Indian unit in 2024, the subsidiary was valued at approximately $18 billion — roughly 40 per cent of Hyundai Motor's entire global market capitalisation.

"What's driving this is smart capital allocation — asset owners capitalising on cross-market valuation arbitrage," said Abhishek Gang, a director at U.S.-based investment bank Houlihan Lokey.

For the parent companies, the calculation is irresistible. Sell a minority stake in your Indian subsidiary at Indian multiples, take the cash back to headquarters where your shares trade at a fraction of those multiples, and the transaction looks like financial alchemy.

## The Rupee Problem

The OFS trend intersects uncomfortably with another story NRI investors know well: the rupee's persistent weakness.

The Indian currency has fallen 13 per cent against the US dollar since 2024 and 6 per cent in 2026 alone, under pressure from the Iran-war-driven oil shock, heavy foreign portfolio outflows, and now IPO-linked capital repatriation. Foreign portfolio investors have sold more than $23 billion of their Indian equity holdings so far this year, surpassing 2025's full-year record outflows of $18.9 billion.

In January, MUFG Bank's analysis identified the IPO market as "one important contributor to Indian rupee weakness." Axis Bank's Tanay Dalal called IPO-linked capital outflows a "steady, though not abrupt, depreciation bias on the rupee."

India's Chief Economic Advisor V. Anantha Nageswaran has warned that IPOs had "increasingly become exit vehicles for early investors rather than mechanisms for raising long-term capital," adding bluntly: "This undermines the spirit of public markets."

## What This Means for NRI Investors

For NRIs considering Indian equity exposure — whether through direct investment, GIFT City, or mutual funds — the pattern deserves close attention.

First, not every IPO is an investment opportunity. When the structure is pure OFS, you are buying shares from someone who has decided to sell, not from a company that needs capital to grow. The company's future operations receive nothing from the listing. That does not automatically make the stock a bad buy, but it does change the incentive structure on day one.

Second, the valuation premium that Indian subsidiaries command over their parents is real but potentially fragile. It is sustained by domestic liquidity, a growing base of retail investors (India's demat accounts have crossed 150 million), and a bull market mindset that has survived multiple corrections. But if India's growth trajectory hits sustained headwinds — from higher oil, tighter monetary policy, or slowing consumption — those premium multiples could compress.

Third, the rupee effect magnifies the risk for NRIs earning in dollars, pounds, or dirhams. Even if the stock price holds steady in rupee terms, a weakening currency erodes the dollar-equivalent return. And the very mechanism of OFS IPOs contributes to that weakness by adding to capital outflows.

Fourth, the structural trend tells you something about how global capital views India right now. Foreign firms are not doubling down. They are monetising. That is not a crisis signal — India's domestic investment story remains strong — but it is a signal that the smart money from Seoul, Stockholm, and Atlanta is taking profit at Indian valuations rather than deploying fresh capital at them.

## The Regulatory Question

Government officials and regulators have not moved to curb the OFS trend. India's securities regulator, SEBI, approved these structures without public objection. But the Chief Economic Advisor's warning — that public markets are becoming exit ramps rather than capital-raising platforms — suggests the conversation is shifting.

For NRIs watching from abroad, the bottom line is this: India's IPO boom is real, and the opportunities within it are real. But the next time a high-profile foreign subsidiary lists in Mumbai, ask the simplest question first. Where does the money go?

If the answer is "back to headquarters," adjust your expectations accordingly."""

article2_sources = json.dumps([
    "Reuters, 'Global firms exploit India's IPO boom to take profits back to home countries' (June 4, 2026)",
    "The Hindu BusinessLine, 'Global firms exploit India's IPO boom to take profits back to home countries' (June 4, 2026)",
    "Prime Database (Indian market research firm), IPO secondary offering data",
    "MUFG Bank analysis on IPO-linked rupee weakness (January 2026)",
    "Reuters, 'Indian shares muted ahead of crucial RBI policy decision' (June 4, 2026)"
])

# ─────────────────────────────────────────────────────
# IMAGE SOURCING AND UPLOAD
# ─────────────────────────────────────────────────────

print("\n=== IMAGE SOURCING ===\n")

# Article 1: Meditation - use Wikimedia Commons "Yoga at school" (1600x1102, JPEG)
# Actually better to use NIMHANS building or something more specific. Let me use Pexels meditation close-up
art1_image_url = None
art1_image_caption = "A person practicing breath-focused meditation outdoors at sunset"
art1_image_attribution = "Pexels"

try:
    print("Article 1: Downloading meditation image from Pexels...")
    img_url = "https://images.pexels.com/photos/8964948/pexels-photo-8964948.jpeg?auto=compress&cs=tinysrgb&w=1200"
    img_bytes = download_image(img_url)
    print(f"  Downloaded: {len(img_bytes)} bytes")
    compressed = compress_image(img_bytes)
    print(f"  Compressed: {len(compressed)} bytes")
    art1_image_url = upload_to_supabase(compressed, f"{article1_slug}.jpg")
except Exception as e:
    print(f"  ✗ Image sourcing failed: {e}")

# Article 2: IPO - use Wikimedia Commons BSE building (2291x1917, JPEG)
art2_image_url = None
art2_image_caption = "The Bombay Stock Exchange building in Mumbai, India's oldest and largest stock exchange"
art2_image_attribution = "Wikimedia Commons"

try:
    print("\nArticle 2: Downloading BSE building image from Wikimedia Commons...")
    img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg"
    img_bytes = download_image(img_url)
    print(f"  Downloaded: {len(img_bytes)} bytes")
    compressed = compress_image(img_bytes)
    print(f"  Compressed: {len(compressed)} bytes")
    art2_image_url = upload_to_supabase(compressed, f"{article2_slug}.jpg")
except Exception as e:
    print(f"  ✗ Image sourcing failed: {e}")

# ─────────────────────────────────────────────────────
# INSERT ARTICLES
# ─────────────────────────────────────────────────────

print("\n=== INSERTING ARTICLES ===\n")

now_iso = datetime.now(timezone.utc).isoformat()

# Article 1
a1 = {
    "headline": article1_headline,
    "subheadline": article1_subheadline,
    "body": article1_body,
    "slug": article1_slug,
    "category": "lifestyle-health",
    "status": "published",
    "published_at": now_iso,
    "sources": article1_sources,
    "is_editorial": False,
    "image_url": art1_image_url,
    "image_caption": art1_image_caption,
    "image_attribution": art1_image_attribution,
}
if not art1_image_url:
    del a1["image_url"]
    del a1["image_caption"]
    del a1["image_attribution"]

a1_id = insert_article(a1)

# Article 2
a2 = {
    "headline": article2_headline,
    "subheadline": article2_subheadline,
    "body": article2_body,
    "slug": article2_slug,
    "category": "markets-finance",
    "status": "published",
    "published_at": now_iso,
    "sources": article2_sources,
    "is_editorial": False,
    "image_url": art2_image_url,
    "image_caption": art2_image_caption,
    "image_attribution": art2_image_attribution,
}
if not art2_image_url:
    del a2["image_url"]
    del a2["image_caption"]
    del a2["image_attribution"]

a2_id = insert_article(a2)

print("\n=== SUMMARY ===")
print(f"Article 1 (lifestyle-health): {'✓' if a1_id else '✗'} — {article1_headline[:70]}...")
print(f"Article 2 (markets-finance):  {'✓' if a2_id else '✗'} — {article2_headline[:70]}...")
print(f"Images: Art1={'✓' if art1_image_url else '✗'} Art2={'✓' if art2_image_url else '✗'}")
print("Done.")
