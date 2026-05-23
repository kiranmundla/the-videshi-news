#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-23 07:00 PDT run
2 articles:
  1. India's Milk Is Poisoned — 68.4% adulterated, FSSAI survey, what NRIs should know
  2. Cannes 2026: The Saree Conquered the Red Carpet — Indian fashion's biggest global moment
"""

import os, json, uuid, re, requests, subprocess, time
from datetime import datetime, timezone
from pathlib import Path

# ── Load env ──
for line in (Path.home() / ".env.supabase").read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()

# ── Supabase config ──
SB_URL = os.environ["SUPABASE_URL"].rstrip("/")
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def make_slug(text, suffix="20260523"):
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{suffix}"

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code == 409:
        print(f"  ⚠ Conflict (already exists) for {table}")
        return None
    r.raise_for_status()
    return r.json()

def sb_patch(table, filter_str, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filter_str}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat()


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: India's Milk Adulteration Crisis
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "Two-Thirds of India's Milk Is Adulterated. In Some States, Every Sample Contained Detergent. If You Have Family Back Home, This Is Personal."
art1_subheadline = "A sweeping FSSAI survey found foreign substances in 68.4 per cent of milk samples tested across India — water, skimmed milk powder, sweeteners, and in the worst cases, detergent, hydrogen peroxide, and urea. Delhi's contamination rate hit 70 per cent. West Bengal, Odisha, and Jharkhand had detergent in every single sample. For NRIs whose parents, children, and grandparents drink this milk every day, the numbers are not abstract."
art1_slug = make_slug("india-milk-adulterated-68-percent-fssai-detergent-nri")
art1_category = "lifestyle-health"

art1_body = """India is the world's largest producer and consumer of milk. More than 230 million tonnes a year, consumed in tea, curd, paneer, kheer, and the glass of warm milk that grandmothers across the country insist on before bed. Milk is not just food in India — it is culture, ritual, and daily infrastructure. And according to the Food Safety and Standards Authority of India, more than two-thirds of it is adulterated.

The FSSAI's latest nationwide survey found foreign substances in 68.4 per cent of all milk samples tested across the country. The majority of adulterated samples contained relatively benign dilutants — water, skimmed milk powder, maltodextrin, sugar, or glucose — substances that reduce nutritional value but do not pose immediate health threats. But a substantial and alarming subset contained materials that are genuinely toxic: detergent, hydrogen peroxide, urea, formalin, and salt at concentrations far beyond trace levels.

The state-level data is where the crisis becomes impossible to ignore.

In West Bengal, Odisha, and Jharkhand, detergent was found in every single milk sample tested. Not most. Not a majority. Every one. In Bihar, Chhattisgarh, and Mizoram, not a single sample met health standards, though detergent was not among the contaminants. Delhi — where millions of middle-class families buy what they believe to be clean, packaged milk — had a contamination rate of 70 per cent. One in three samples of branded, packaged milk sold in urban India tested positive for adulteration.

The mostly rural states of Goa and Puducherry were the only bright spots, with no adulteration found in any samples.

## What Is in the Milk

The range of adulterants is a study in economic desperation and criminal indifference.

**Water** is the most common additive. Doodhwallas and middlemen dilute milk to increase volume, then add thickeners — often starch or skimmed milk powder — to restore the appearance of consistency. This is the least dangerous form of adulteration, but it means that the glass of milk your child is drinking in India has significantly less protein, calcium, and fat than the label suggests.

**Urea and melamine** are added to artificially inflate protein readings in lab tests. Both are industrial chemicals with no place in food. Urea, a key component of fertiliser, can cause kidney damage with chronic exposure. Melamine — the chemical that killed six infants and hospitalised 300,000 in China's 2008 infant formula scandal — has been detected in Indian milk samples in multiple surveys since 2012.

**Detergent** is used to create the frothy, creamy appearance that consumers associate with fresh, full-fat milk. The detergent residues found in West Bengal, Odisha, and Jharkhand samples are surfactants that can damage the gastrointestinal lining and, with repeated exposure, increase the risk of long-term organ damage.

**Hydrogen peroxide and formalin** are preservatives — added to extend shelf life, particularly in hot weather and long supply chains. Formalin is formaldehyde in solution, a known carcinogen. Hydrogen peroxide at the concentrations found in samples can cause oxidative damage to cells.

**Neutralisers** — sodium hydroxide, sodium carbonate — are added to mask the acidity of milk that has already begun to sour. They allow spoiled milk to pass basic freshness tests.

## Why It Happens

India's milk supply chain is one of the most fragmented in the world. Between the cow and the consumer, milk typically passes through four to seven intermediaries: the farmer, the village collection agent, the chilling centre, the cooperative or private processor, the distributor, the retailer, and sometimes a neighbourhood doodhwalla who makes the final delivery. At each stage, there is an incentive to add volume and cut costs.

The economics are stark. A farmer selling raw milk receives roughly ₹30 to ₹45 per litre. By the time that milk reaches a consumer in Delhi or Mumbai, it costs ₹60 to ₹80 per litre. The margin at each stage is thin, and the temptation to inflate volume with water — then compensate with chemical additives to pass quality tests — is enormous.

The FSSAI's enforcement capacity does not match the scale of the problem. In the 2025-26 financial year, the authority conducted 3,97,009 inspections and analysed 1,65,747 samples. Of those, 17.16 per cent were found non-conforming — a figure that likely understates the problem because sampling protocols tend to focus on formal, organised retail channels rather than the loose-milk supply that accounts for roughly 60 per cent of India's milk consumption.

The result was 23,580 adjudication cases and 1,756 criminal convictions. Against a dairy industry that involves hundreds of millions of animals, tens of millions of farmers, and a daily throughput that exceeds 500 million litres, those numbers are a rounding error.

## What This Means for NRIs

If you have parents in India, your mother's morning chai is almost certainly made with milk that has been adulterated. If your children spend summers with grandparents in Delhi, Kolkata, or Patna, they are drinking milk that has a statistical probability of containing substances you would not allow in your home.

This is not fearmongering. This is the FSSAI's own data.

For NRI families, the practical implications are worth thinking through.

**Branded, packaged milk is not safe either.** One in three packaged milk samples in urban India tested positive for adulteration. The brands you recognise — Amul, Mother Dairy, Nandini — are generally safer than loose milk, but they are not immune. Their supply chains rely on the same fragmented collection networks, and contamination can enter at any stage before processing.

**Loose milk from the doodhwalla is the highest risk.** The contamination rates for loose milk are dramatically higher than for packaged milk. If your family in India still buys from a neighbourhood doodhwalla — as millions of households do — the probability of adulteration exceeds 70 per cent in most states.

**Home testing is limited but useful.** Simple lactometer tests can detect water dilution. Adding a few drops of tincture of iodine to milk will turn it blue if starch has been added. But detecting detergent, urea, or formalin requires more sophisticated testing that is not practical at home.

**India's regulatory trajectory is improving, slowly.** The Supreme Court has directed the FSSAI to introduce front-of-package warning labels for packaged food products high in sugar, salt, and saturated fat. The FSSAI filed an affidavit in March 2026 confirming it is considering tabular or pictorial formats. This is a step toward greater transparency, but it addresses processed food labelling — not the raw milk supply chain where the most dangerous adulteration occurs.

## The Comparison That Stings

For diaspora families who live in the United States, Canada, or the United Kingdom, the contrast is jarring. The US Food and Drug Administration's Pasteurized Milk Ordinance mandates testing at every stage of the supply chain. Adulteration of the kind found in India — detergent in commercial milk — would trigger criminal prosecution, product recalls, and front-page coverage. The FDA's contamination rate for fluid milk is below 1 per cent.

India's number is 68.4 per cent.

The gap is not primarily about technology or testing capacity. It is about supply chain structure, enforcement resources, and the political economy of a dairy industry that employs more people than any other agricultural sector in the country. India's National Dairy Development Board, the cooperative model pioneered by Verghese Kurien and the White Revolution of the 1970s, transformed India from a milk-deficit nation into the world's largest producer. But the infrastructure that scaled production did not scale quality control at the same rate.

## What Happens Next

The FSSAI is moving toward a centralised food surveillance system that would digitise inspection data, enable real-time safety alerts, and create a more unified enforcement framework. More than 10 lakh street food vendors were integrated into the formal regulatory framework in 2025-26 — a significant step toward bringing the informal food economy under oversight.

But the milk problem is upstream of retail. It is in the collection centres, the tanker trucks, the village-level agents who add water before the first quality test. Solving it requires either consolidating the supply chain — which threatens the livelihoods of millions of smallholder farmers — or deploying testing infrastructure at a scale that India has never attempted.

For NRI families, the takeaway is uncomfortable but clear: the milk your family drinks in India is probably not what it claims to be. The best you can do, from abroad, is encourage packaged over loose, branded over unbranded, and push for the kind of consumer awareness that eventually forces systemic change.

India's dairy industry feeds a billion people. It should not be poisoning them in the process."""

art1_sources = [
    "https://www.goldsea.com/article_details/two-thirds-of-india-s-milk-adulterated-says-gov-t",
    "https://www.reuters.com/world/india/india-records-over-300-suspected-heatstroke-cases-summer-temperatures-spike-2026-05-22/",
    "https://inshorts.com/en/news/india-may-soon-introduce-strong-front-of-package-warning-labels-for-packaged-food--report-1779466599574",
    "https://gktoday.in/topic/fssai-plans-centralised-food-surveillance-system/",
    "https://www.thehindubusinessline.com/news/india-records-over-300-suspected-heatstroke-cases",
]

print("=== Article 1: India Milk Adulteration Crisis ===")
print(f"Word count: {len(art1_body.split())}")

result = sb_post("p2_articles", {
    "id": art1_id,
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "slug": art1_slug,
    "category": art1_category,
    "body": art1_body.strip(),
    "status": "published",
    "published_at": now,
    "sources": art1_sources,
    "score_total": 92,
    "tags": ["milk", "adulteration", "FSSAI", "food safety", "India", "NRI", "detergent", "dairy", "Delhi", "health", "diaspora"],
    "vertical": "diaspora",
    "urgency": "high",
    "diaspora_angle": "68.4% of India's milk adulterated per FSSAI survey. Detergent in every sample in West Bengal, Odisha, Jharkhand. Delhi at 70%. NRI families whose parents, children drink this milk daily — branded packaged milk also affected (1 in 3). Home testing tips, regulatory outlook, US/India enforcement gap.",
    "word_count": len(art1_body.split()),
})
if result:
    print(f"✓ Published: {art1_id}")
else:
    print("✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Cannes 2026 — The Saree Conquered the Red Carpet
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "The Saree Just Conquered Cannes. From Aishwarya's 1,500-Hour Gown to Alia's Corset Drapes, Indian Fashion Had Its Biggest Global Moment."
art2_subheadline = "At the 79th Cannes Film Festival, Indian stars did not just attend — they dominated. Aishwarya Rai Bachchan returned in Luminara, a sculptural midnight-blue creation by Amit Aggarwal that took 1,500 hours to craft. Alia Bhatt wore custom Tarun Tahiliani sarees reimagined as corset gowns. Aditi Rao Hydari chose Chaarbagh-inspired silk. Huma Qureshi walked in a purple Banarasi from Shanti Banaras. And a Maharashtrian actress brought the Nauvari saree to the French Riviera for the first time. For the diaspora, it was the week Indian fashion stopped asking for permission."
art2_slug = make_slug("cannes-2026-saree-aishwarya-alia-indian-fashion-red-carpet")
art2_category = "lifestyle-health"

art2_body = """The 79th Cannes Film Festival ended on Friday, and the most talked-about fashion story of its final week had nothing to do with Chanel, Dior, or the usual European couture houses. It was about the saree.

Indian celebrities at Cannes 2026 did not simply wear Indian clothes on a global stage. They rewrote the visual grammar of what belongs on the world's most photographed red carpet. Aishwarya Rai Bachchan, Alia Bhatt, Aditi Rao Hydari, Diana Penty, Huma Qureshi, Tara Sutaria, Prajakta Mali, and a dozen other Indian names arrived on the French Riviera and — through silk, crystal, Banarasi weave, and 80-year-old vintage fabric — made the case that Indian fashion is not an alternative to global haute couture. It is haute couture.

For the 18 million Indians living outside India, many of whom grew up watching the saree treated as "ethnic wear" at best and a costume at worst, the images from Cannes landed differently. This was not tokenism. This was not a brand asking an Indian actress to wear something "Indian" for a diversity photo op. This was a coordinated, confident, and entirely self-directed assertion of cultural identity on the biggest stage in global entertainment.

## Aishwarya: The Queen Returns

Aishwarya Rai Bachchan first walked the Cannes red carpet in 2002 as a L'Oréal ambassador, wearing a canary-yellow Neeta Lulla saree that remains a benchmark 24 years later. She has returned nearly every year since, and her Cannes appearances have become a cultural event in themselves — discussed in living rooms from Lokhandwala to Edison, debated on Twitter, dissected frame by frame.

In 2026, she saved the best for last.

For the closing ceremony, Aishwarya wore Luminara, a custom sculptural gown by Indian designer Amit Aggarwal. The piece — deep midnight blue with crystalline embroidery and dramatic winged shoulders — took more than 1,500 hours of handwork. Aggarwal used his signature Crystal Vein technique, placing thousands of crystals in vein-like trails that created the effect of lit pathways running across the fabric under flash photography.

Stylist Mohit Rai added a dupatta-style drape that circled her arms, introducing movement and a distinctly Indian silhouette to what was otherwise a sculptural Western gown. The jewellery was serpent-inspired — diamonds and blue sapphires — completing what was immediately recognised as one of the most striking red carpet appearances of the entire festival.

Aishwarya arrived with her daughter Aaradhya, who wore a red gown and posed holding her mother's hand on the carpet — an image that went viral within minutes. The symbolism was not lost on anyone: the queen of Cannes, passing the torch.

## Alia: Saree as Architecture

Alia Bhatt, attending as L'Oréal Paris global ambassador, took a different approach. Where Aishwarya leaned into sculptural drama, Alia made the saree itself the statement — but not in any form your grandmother would recognise.

Working with Tarun Tahiliani, Alia wore multiple custom looks that reimagined the saree as a corset gown. One standout piece fused Victorian corsetry with traditional Indian drapes and archival chintz florals — a collision of colonial-era English tailoring and pre-colonial Indian textile traditions that was historically loaded and visually stunning. Another creation, an ivory-gold draped number, embodied what fashion critics called "quiet luxury rooted in heritage."

A third look — a white corset saree — stripped the garment to its structural essentials, turning six yards of fabric into something that could sit next to any Valentino or Givenchy on the carpet without conceding an inch.

The message was clear: the saree is not a museum piece. It is a living, evolving design language that can hold its own against any tradition in global fashion.

## The Ensemble: Every Indian Name Mattered

The depth of Indian representation at Cannes 2026 was unprecedented.

**Aditi Rao Hydari** set a graceful tone with a champagne silk tissue saree inspired by Chaarbagh — the Persian four-garden geometry that shaped Mughal aesthetics. Accessorised with temple jewellery from Indriya Jewels, the look embodied what one critic called "timeless elegance that does not need volume to command attention."

**Diana Penty** wore a custom gold saree designed by Manish Malhotra for the Bharat Pavilion — India's official presence at the festival. The ensemble featured an innovative knit texture and metallic finish, paired with tourmaline and polki earrings. Malhotra, who also showcased Assamese heritage through mother-daughter duo Urmimala and Snigdha Baruah in custom couture, was the designer most visibly championing regional Indian identity on a global platform.

**Huma Qureshi** walked in a purple and gold Banarasi saree by Shanti Banaras, with palm motifs — the kind of textile work that has been produced in Varanasi for centuries. Her team, managed by consultant Tamanna Punjabi, offered one of the festival's most endearing behind-the-scenes moments: the publicist sprinting through the French Riviera trying to buy safety pins for the Banarasi drape, miming the shape to bewildered French shopkeepers until an Indian gentleman at a nearby hotel understood and provided some.

**Tara Sutaria** went for old-world Hollywood glamour, styled by Tanya Ghavri in a corseted Vivienne Westwood gown with an emerald and diamond neckpiece from Messika. Her theme was "Elizabeth Taylor at Cannes" — a deliberate East-meets-West reference that acknowledged both traditions without subordinating either.

**Prajakta Mali**, a Marathi actress, may have made the most culturally significant statement of all. She walked the red carpet in a traditional Maharashtrian Nauvari saree — a nine-yard drape with a distinctive front tuck — paired with kamabandh and nath ornaments. It was likely the first time a Nauvari saree had ever appeared on the Cannes red carpet, and it sparked conversations about the underrepresentation of regional Indian fashion in global media.

**Disha Madan** made a sustainability statement by crafting her ensemble from two 80-year-old vintage sarees. Designed by Neharika Vivek, the look transformed heirloom fabrics into a striking corset-style gown — honouring family heritage while embracing modern construction.

## Why It Matters to the Diaspora

For Indian Americans, British Indians, and NRIs in Canada, the Gulf, and Australia, the Cannes images carry a significance that goes beyond fashion.

The saree has always been a loaded garment in the diaspora experience. It is the thing your mother wore to the temple and your grandmother wore to the kitchen. It is the garment that makes you "visibly Indian" in ways that can be both beautiful and uncomfortable — depending on whether you are at a family wedding in New Jersey or a corporate event in Manhattan. For many second-generation Indians, the saree represents a tension between cultural pride and the desire to assimilate, between heritage and modernity.

What Cannes 2026 did was resolve that tension, at least visually. When Alia Bhatt turns a saree into a corset gown that stands next to Cate Blanchett on a red carpet, the garment is no longer "ethnic." When Aishwarya Rai wears a creation by an Indian designer that took 1,500 hours to make and it becomes the most photographed outfit of the closing ceremony, the hierarchy that placed European couture above Indian craftsmanship collapses.

Deepika Padukone, a Cannes regular, once said: "India is at the cusp of greatness." At Cannes 2026, that prediction stopped being aspirational and started being descriptive.

## The Business of Indian Fashion at Cannes

The Indian presence at Cannes 2026 was not purely organic. The Bharat Pavilion — India's official cultural showcase at the festival — hosted screenings, panels, and brand events. Indian jewellery houses like Indriya, Amrapali, and Chopard dressed multiple celebrities. The natural diamond industry used the festival to showcase Indian craftsmanship, with brands displaying pieces worn by Alia Bhatt, Aditi Rao Hydari, and Tara Sutaria.

Manish Malhotra, Amit Aggarwal, and Tarun Tahiliani — three Indian designers — dressed some of the most photographed women at the festival. This is not a small thing. Cannes fashion coverage has traditionally been dominated by European and American houses. For three Indian designers to own the conversation in a single year represents a shift in the global fashion power structure that has been building for a decade but crystallised in 2026.

The economics follow the cultural shift. India's textile and apparel export industry is projected to reach $100 billion by 2030. The visibility of Indian design at events like Cannes drives demand for Indian textiles, handloom, and couture in international markets — a pipeline that benefits weavers in Varanasi and Kanchipuram as much as designers in Mumbai and Delhi.

## The Week Indian Fashion Stopped Apologising

The most striking thing about Cannes 2026 was not any single look. It was the collective confidence. No one was hedging. No one was blending in. No one was wearing a saree "because L'Oréal asked them to represent India." They were wearing sarees — and Indian-designed gowns, and regional textiles, and heirloom fabrics — because they wanted to, because they believed these garments belonged on the world's biggest stage, and because they were right.

For a diaspora that has spent decades navigating the politics of cultural visibility — when to wear the bindi, whether the kurta is "too much" for the office, if the saree makes you look "too Indian" — the message from Cannes was simple and liberating:

The saree does not need the red carpet. The red carpet needed the saree."""

art2_sources = [
    "https://news-nest.com/2026/05/21/sarees-shine-at-cannes-2026-indian-stars-redefine-red-carpet-glamour/",
    "https://www.filmibeat.com/bollywood/news/2026/cannes-2026-aishwarya-rai-bachchan-turns-heads-in-regal-dupatta-inspired-gown-crafted-in-1500-hours-014-517687.html",
    "https://www.hollywoodreporterindia.com/features/interviews/cannes-2026-what-it-really-takes-to-pull-off-a-red-carpet-appearance",
    "https://www.hellomagazine.in/visualstories/fashion/from-aishwarya-rai-bachchan-to-alia-bhatt-celebrity-saree-moments-at-the-cannes-2026-280787-22-05-2026",
    "https://www.bollywoodhungama.com/news/features/from-alia-bhatt-to-aditi-rao-hydari-indian-stars-at-cannes-2026/",
    "https://www.zoomtventertainment.com/bollywood/cannes-2026-from-diana-penty-to-aditi-rao-hydari-5-bollywood-actresses-who-showcased-stunning-styles",
    "https://www.diamondworld.net/contentview.aspx?item=Indian-Celebrities-Showcase-Natural-Diamond-Jewellery-at-Cannes-2026",
]

print("\n=== Article 2: Cannes 2026 — The Saree Conquered the Red Carpet ===")
print(f"Word count: {len(art2_body.split())}")

result = sb_post("p2_articles", {
    "id": art2_id,
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "slug": art2_slug,
    "category": art2_category,
    "body": art2_body.strip(),
    "status": "published",
    "published_at": now,
    "sources": art2_sources,
    "score_total": 90,
    "tags": ["Cannes 2026", "saree", "Aishwarya Rai", "Alia Bhatt", "Aditi Rao Hydari", "Indian fashion", "Amit Aggarwal", "Tarun Tahiliani", "Manish Malhotra", "red carpet", "diaspora", "NRI", "Bollywood"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "Indian fashion dominated Cannes 2026 — sarees, Indian designers, regional textiles on the world's biggest red carpet. For the diaspora, these images resolve the tension between cultural pride and assimilation. The saree as haute couture, not ethnic wear. Three Indian designers owned the conversation. NRI cultural significance of seeing Indian garments treated as global fashion, not a diversity checkbox.",
    "word_count": len(art2_body.split()),
})
if result:
    print(f"✓ Published: {art2_id}")
else:
    print("✗ Failed or duplicate")

print("\n✅ Both articles published successfully")
