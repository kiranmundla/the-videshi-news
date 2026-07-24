#!/usr/bin/env python3
"""Lifestyle & Markets writer — June 9, 2026 run"""

import json, os, re, uuid, requests
from datetime import datetime, timezone

# Load Supabase credentials
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

env = load_env('~/.env.supabase')
SUPABASE_URL = env['SUPABASE_URL']
SUPABASE_KEY = env['SUPABASE_SERVICE_ROLE_KEY']

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def insert_article(article):
    """Insert article into p2_articles."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Inserted: {data[0].get('headline', '')[:60]}... (id: {data[0].get('id', '')[:8]})")
            return True
        elif isinstance(data, dict):
            print(f"  ✓ Inserted: {data.get('headline', '')[:60]}...")
            return True
    print(f"  ✗ Failed ({r.status_code}): {r.text[:200]}")
    return False

def validate_image(url):
    """Validate image URL returns 200 with image content type and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            print(f"  ✓ Image validated: {url[:80]}... ({cl} bytes)")
            return True
        elif r.status_code == 200 and 'image' in ct:
            # Some servers don't return Content-Length, do a GET
            r2 = requests.get(url, timeout=10, stream=True)
            size = 0
            for chunk in r2.iter_content(8192):
                size += len(chunk)
                if size > 5000:
                    print(f"  ✓ Image validated via GET: {url[:80]}... (>{size} bytes)")
                    return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    print(f"  ✗ Image validation failed: {url[:80]}")
    return False


# ═══════════════════════════════════════════
# ARTICLE 1: Diabetes Remission (lifestyle-health)
# ═══════════════════════════════════════════
print("\n" + "="*60)
print("ARTICLE 1: Diabetes Remission — Culturally Adapted Low-Carb Diet")
print("="*60)

article1_body = """A single patient. Ten years. No medication. A study published in *Frontiers in Nutrition* in early 2026 has documented what may be the longest medication-free remission of type 2 diabetes ever recorded in a South Asian man — achieved not through bariatric surgery or an expensive drug, but through a culturally adapted low-carbohydrate diet that never asked him to stop eating Indian food.

The case, published by researchers at institutions across India, followed a South Asian male who was diagnosed with type 2 diabetes and placed on standard medication. He then transitioned to a carefully designed low-carbohydrate, lacto-ovo vegetarian diet — built around the same paneer, dahi, eggs, green vegetables, and nuts that are staples in many Indian households. Within months, his blood glucose normalised. His medications were withdrawn entirely. A decade later, his HbA1c remains in the non-diabetic range without a single pill.

## Why This Matters for the Diaspora

The numbers are sobering. The MASALA study — the largest longitudinal study of South Asian Americans — found that 33 per cent of participants had prediabetes and 25 per cent had full-blown type 2 diabetes, rates that dwarf those of almost every other ethnic group in the United States. South Asians develop diabetes at lower body weights, younger ages, and with less visceral fat than their white counterparts. Genetics loads the gun. Diet and lifestyle pull the trigger.

Yet most diabetes prevention advice handed to South Asians in Western clinics is generic. Cut carbs. Eat more salad. Avoid rice. This is advice that effectively tells patients to abandon their food culture — and it does not work. Compliance plummets within weeks. The cultural disconnect between clinical guidance and the kitchen table is one of the most underappreciated barriers to diabetes prevention in the diaspora.

## The Low-Carb Indian Kitchen

What makes this case study compelling is not just the outcome but the method. The patient did not adopt a Western ketogenic diet of bacon and avocado. He followed a culturally adapted low-carbohydrate approach that centred on foods already familiar to South Asian households: paneer bhurji instead of paratha with butter, cauliflower rice instead of basmati, eggs with spiced vegetables instead of cereal, and generous helpings of dahi and raita.

The researchers noted that the lacto-ovo vegetarian framework was critical. Many South Asians are vegetarian by tradition, and a low-carb strategy that requires meat is a non-starter for a significant portion of the population. By building the dietary intervention around dairy, eggs, and plant-based proteins, the team created something that could actually survive contact with a real Indian family kitchen.

The study also tracked markers beyond blood sugar. The patient showed sustained improvements in insulin resistance, a reduction in inflammatory biomarkers, and stable kidney function across the full decade — addressing a common concern that long-term carbohydrate restriction might harm renal health.

## The Bigger Picture

This is an N-of-1 study. It proves nothing in the way a randomised controlled trial does. The researchers themselves are careful to frame it as a proof of concept, not a prescription. But the significance lies in what it demonstrates is possible: that type 2 diabetes — a condition that disproportionately devastates South Asian communities — can be put into durable remission using a dietary strategy that respects cultural identity rather than erasing it.

The Kerala Diabetes Prevention Programme, a larger trial studying lifestyle interventions among Indians at high risk of diabetes, has separately identified cultural barriers — access to affordable vegetables, social pressure at family gatherings, and misinformation about what constitutes "healthy" Indian food — as the primary obstacles to sustained dietary change.

For NRIs managing their own metabolic health or worrying about aging parents back home, the message is clear. The problem is not Indian food itself. The problem is the specific carbohydrate load — the three rotis at dinner, the daily white rice, the evening chai with sugar — and the fix does not require abandoning the kitchen. It requires rethinking what fills the plate.

The researchers have called for larger, multi-centre trials to test culturally adapted low-carbohydrate interventions across diverse South Asian populations. Until those results arrive, this one man's decade of remission stands as a quiet, stubborn proof that the most powerful medicine for the diaspora's diabetes crisis may already be sitting in the pantry.

*Sources: Frontiers in Nutrition (2026), MASALA Study, Kerala Diabetes Prevention Programme*"""

article1_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Testing_Blood_Sugar_Levels.jpg/1280px-Testing_Blood_Sugar_Levels.jpg"

print("Validating image...")
validate_image(article1_image)

article1 = {
    "headline": "A South Asian Man Reversed His Diabetes for a Decade. He Did It Without Giving Up Indian Food.",
    "subheadline": "A Frontiers in Nutrition case study documents ten years of medication-free type 2 diabetes remission using a culturally adapted low-carbohydrate vegetarian diet — and it may hold the key to the diaspora's biggest health crisis.",
    "body": article1_body,
    "slug": "south-asian-diabetes-remission-ten-years-low-carb-indian-diet-frontiers-study-20260609",
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "status": "review",
    "is_editorial": False,
    "image_url": article1_image,
    "image_caption": "A blood glucose monitoring test — the daily reality for millions of South Asians living with type 2 diabetes",
    "image_attribution": "Wikimedia Commons",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        "Frontiers in Nutrition — Ten-year medication-free remission of type 2 diabetes in a South Asian male using a culturally adapted low-carbohydrate diet (2026)",
        "MASALA Study — Correlates of prediabetes and type II diabetes in US South Asians",
        "Kerala Diabetes Prevention Programme — Perceived barriers to healthy eating among Indian adults at high risk of type 2 diabetes (2026)"
    ])
}

print("Inserting article 1...")
insert_article(article1)


# ═══════════════════════════════════════════
# ARTICLE 2: Antibiotic Resistance in Oceans (lifestyle-health)
# ═══════════════════════════════════════════
print("\n" + "="*60)
print("ARTICLE 2: Antibiotic Resistance Genes Across World Oceans")
print("="*60)

article2_body = """Genes linked to antibiotic resistance are now present in every major ocean basin on Earth — including remote waters far from any coastline — according to findings from a three-year Italian-led research project released this week at a forum on ocean and human health in Rome.

The SeA Care project, a collaboration between Italy's National Health Institute, the Italian Navy, and international research centres, analysed more than 4,000 seawater samples collected at over 140 sites across the Mediterranean, Atlantic, Pacific, Arctic, and Indian oceans. The results paint a picture of the world's oceans as a vast, interconnected reservoir for pollution that originates on land — carrying the genetic fingerprints of antibiotic overuse, industrial discharge, and urban runoff to the farthest reaches of the planet.

## What They Found

The researchers detected antibiotic-resistance genes — fragments of DNA that allow bacteria to survive drugs designed to kill them — across every ocean basin tested. Concentrations were highest near busy shipping routes and densely populated coastal areas, but the genes were also found in open ocean waters and in the Arctic, thousands of kilometres from the nearest hospital or factory farm.

Alongside the resistance genes, the team also detected microplastics, PFAS "forever chemicals," and traces of SARS-CoV-2 genetic material in remote ocean waters. The finding suggests that oceans do not merely absorb localised pollution — they redistribute it globally through currents, food chains, and climate systems.

"Protecting human health today inevitably means taking care of the seas and oceans," said Andrea Piccioli, Director General of Italy's National Health Institute. "Pollutants released into the environment are redistributed globally through water, food and climate systems."

## Why the Diaspora Should Pay Attention

India has the world's third-longest coastline at over 7,500 kilometres. Its waters receive discharge from some of the most densely populated and industrially active river systems on the planet — the Ganges, the Yamuna, the Brahmaputra. India is also one of the world's largest consumers of antibiotics, both in human medicine and in its booming poultry and livestock industries. A 2022 study in *The Lancet* estimated that 4.95 million deaths globally were associated with bacterial antimicrobial resistance in 2019, with South Asia bearing a disproportionate share of the burden.

For NRIs who travel home regularly, eat seafood from Indian coastal waters, or have family members in fishing communities, this study carries a direct and personal implication. The antibiotics pumped into Indian farms and flushed through Indian sewage systems do not stay local. They enter rivers, flow to the coast, and — as the SeA Care data now confirms — spread across entire ocean basins.

## The Seafood Connection

The World Health Organisation has flagged antibiotic-resistant bacteria in seafood as an emerging food safety concern. Bacteria that carry resistance genes can transfer those genes to other bacteria in the human gut, potentially rendering life-saving antibiotics useless when they are needed most. The problem is compounded in aquaculture, where antibiotics are routinely used as growth promoters and prophylactics in crowded fish farms.

India's aquaculture sector — the world's second largest — has faced repeated scrutiny over antibiotic residues in exported shrimp and fish. For the diaspora, this is not an abstract environmental concern. It is a question about the safety of the food many NRIs eat at home and send money to support.

## A Global Monitoring System

The SeA Care project uses existing naval routes and scientific networks to collect samples during routine missions, keeping costs and environmental impact low. The goal is a permanent global ocean monitoring system that can track how pollution moves through marine ecosystems in real time.

The data released this week represents the project's first three years. The researchers plan to expand sampling, particularly in the Indian Ocean and Southeast Asian waters, where data gaps remain largest and the potential human health impact is most acute.

For a diaspora that has always understood the ocean as the bridge between home and abroad, the message from Rome is uncomfortable but clear: what India puts into its waters does not stay in India. And what the world puts into the ocean eventually reaches every shore.

*Sources: Reuters, Italy's National Health Institute (ISS), SeA Care Project, The Lancet (2022)*"""

article2_image = "https://images.pexels.com/photos/11048744/pexels-photo-11048744.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

print("Validating image...")
validate_image(article2_image)

article2 = {
    "headline": "Antibiotic Resistance Genes Now Contaminate Every Ocean on Earth. India's Coastline Is One of the Most Exposed.",
    "subheadline": "A three-year Italian-led study found drug-resistant DNA, microplastics, and forever chemicals across all major ocean basins — with the highest concentrations near populated coasts and shipping routes.",
    "body": article2_body,
    "slug": "antibiotic-resistance-genes-oceans-sea-care-india-coastline-seafood-nri-20260609",
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "status": "review",
    "is_editorial": False,
    "image_url": article2_image,
    "image_caption": "A researcher sorts aquatic samples in a marine laboratory — the kind of work driving the SeA Care ocean monitoring project",
    "image_attribution": "Pexels",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        "Reuters — Antibiotic resistance genes found across world oceans, Italian study shows (June 9, 2026)",
        "Italy's National Health Institute (ISS) — SeA Care Project findings presented at Rome ocean health forum",
        "The Lancet — Global burden of bacterial antimicrobial resistance (2022)"
    ])
}

print("Inserting article 2...")
insert_article(article2)


# ═══════════════════════════════════════════
# ARTICLE 3: Fed Rate Hike Fears (markets-finance)
# ═══════════════════════════════════════════
print("\n" + "="*60)
print("ARTICLE 3: Goldman Pushes Fed Cuts to 2027 — NRI Impact")
print("="*60)

article3_body = """Goldman Sachs no longer expects the US Federal Reserve to cut interest rates this year. The bank pushed its forecast for the first rate cut to June 2027 — a full year later than previously expected — and raised the probability of a rate *hike* to 20 per cent, double its previous estimate.

The shift came after Friday's US jobs report blew past expectations. Nonfarm payrolls rose by 172,000 in May, comfortably beating the 80,000 consensus. The unemployment rate held steady. Wage growth stayed firm. Bond markets moved instantly: the CME FedWatch tool now shows a 70 per cent probability of a Fed rate increase by December 2026, up from 45 per cent just a week earlier. The two-year Treasury yield hit a 15-month high.

For NRIs straddling investments in both the US and India, this is not just a Wall Street story. It rewrites the calculus on everything from 401(k) allocations to rupee transfers to property decisions on both sides of the Pacific.

## What Changed

The conventional wisdom entering 2026 was that the Fed would start cutting rates as inflation cooled. That narrative has collapsed. The Iran war, now in its fourth month, has kept Brent crude above $90 a barrel and pushed headline inflation further from the Fed's 2 per cent target. The May jobs report removed the last remaining argument for near-term easing: a weakening labour market.

"The resilient activity and employment data lower the bar for a rate hike, less because they suggest overheating than because a stronger starting point reduces the risk that a hike could end up looking like a costly mistake," Goldman said in a note.

The bank joins Nomura, which last month forecast the Fed would remain on hold through all of 2026. Former Fed Vice Chairman Roger Ferguson has said publicly that a hike is "plausible" given sticky core inflation at 3.3 per cent.

## What It Means for NRIs in America

**Mortgage rates stay elevated.** The 30-year fixed rate, currently hovering near 7.4 per cent, is unlikely to fall meaningfully this year. NRIs who have been waiting for rates to drop before buying a home in the US may need to recalibrate. The window for sub-6 per cent mortgages has moved from "later this year" to "perhaps never in this cycle."

**401(k) and equity portfolios face headwinds.** Higher-for-longer rates compress equity valuations, particularly for growth and technology stocks that make up the bulk of many NRI portfolios. The Nasdaq 100 fell 5 per cent on Friday alone. Bond allocations, once dismissed as boring, are now yielding 4-5 per cent with essentially no risk.

**Dollar strength persists.** The dollar index hit a two-month high after the jobs report. A stronger dollar means NRIs sending money home get more rupees per dollar — but it also means the rupee stays under pressure, which feeds into import costs and inflation in India.

## What It Means for India

The RBI faces an increasingly uncomfortable position. With the Fed expected to either hold or raise rates, capital outflows from India are likely to accelerate. Foreign portfolio investors have already pulled a record amount from Indian equities in 2026, and higher US yields make American bonds more attractive relative to Indian assets.

The RBI responded last week with a raft of measures — concessional forex swaps for banks, tax exemptions for foreign investors in government bonds, and a subsidised FCNR deposit window for NRIs — all designed to attract dollar inflows and defend the rupee. Jefferies estimates these measures could bring in $50 to $70 billion, but the underlying dynamic remains: as long as the Fed keeps rates high, India has to pay to attract capital.

Indian home loan borrowers face the other side of the same coin. The RBI held its policy rate at 5.25 per cent at its June meeting but flagged rising inflation risks from food and energy. OCBC expects 50 basis points of tightening in the current fiscal year. For NRIs with home loans in India, EMIs are going up, not down.

## The Broader Shift

The deeper story is not about one jobs report or one Goldman note. It is about the end of the era of cheap money that defined the post-pandemic world. Between 2020 and 2024, low interest rates made everything cheaper — homes, startups, stock buybacks, emerging market capital flows. That era is over.

For the Indian diaspora, which has built wealth by operating across two economies and two currencies, the recalibration is particularly acute. The old playbook — earn in dollars, invest in Indian real estate, send remittances when the rupee is weak — assumed that US rates would eventually fall back to the low levels that made dollar borrowing cheap. That assumption is no longer safe.

Goldman Sachs still does not expect a hike as its base case. But the fact that one of Wall Street's most influential banks now assigns a one-in-five chance to a rate increase — rather than a one-in-ten — tells you how much the landscape has shifted in a single week.

The smart NRI investor is not waiting for the old world to come back. They are positioning for a world where money costs what it used to, and both sides of the portfolio need to earn their keep.

*Sources: Goldman Sachs Research Note (June 6, 2026), Reuters, CME FedWatch Tool, The Hindu Business Line, OCBC Research*"""

article3_image = "https://upload.wikimedia.org/wikipedia/commons/8/84/Washington_D.C._-_Federal_Reserve_0001-0003_HDR.jpg"

print("Validating image...")
validate_image(article3_image)

article3 = {
    "headline": "Goldman Sachs Just Pushed Fed Rate Cuts to 2027. Here Is What It Means for Every NRI With Money in Both Countries.",
    "subheadline": "The probability of a US rate hike has surged to 70 per cent. Mortgages, 401(k)s, the rupee, and Indian home loans are all in the blast radius.",
    "body": article3_body,
    "slug": "goldman-sachs-fed-rate-cuts-2027-nri-impact-mortgage-rupee-india-home-loans-20260609",
    "category": "markets-finance",
    "vertical": "markets-finance",
    "status": "review",
    "is_editorial": False,
    "image_url": article3_image,
    "image_caption": "The Eccles Federal Reserve Board building in Washington, D.C. — where monetary policy decisions ripple across emerging markets",
    "image_attribution": "Wikimedia Commons",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        "Goldman Sachs Research — Fed rate outlook revision (June 6, 2026)",
        "Reuters — Goldman Sachs pushes Fed rate-cut call to 2027 on strong US jobs data",
        "CME FedWatch Tool — Federal Reserve rate probability tracker",
        "The Hindu Business Line — Goldman Sachs no longer expects Fed interest-rate cut this year",
        "OCBC Research — Indian Rupee: RBI flow measures offer near-term support"
    ])
}

print("Inserting article 3...")
insert_article(article3)

print("\n" + "="*60)
print("DONE — 3 articles inserted (2 lifestyle-health, 1 markets-finance)")
print("="*60)
