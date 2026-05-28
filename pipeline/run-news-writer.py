#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-28 evening run)
Writes 3 fresh news articles with proper image sourcing.
"""

import json, os, sys, uuid, re, subprocess, urllib.parse
from datetime import datetime, timezone

import requests

# --- Environment ---
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# --- Helpers ---

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Prefer originalimage (higher res), fall back to thumbnail AS-IS
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels using curl (Python urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5",
                 "-H", f"Authorization: {PEXELS_API_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(image_url, timeout=30, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {r.status_code}")
            return None
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image: {content_type}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return None

        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        ur = requests.post(upload_url, data=r.content, headers=upload_headers, timeout=30)
        if ur.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed: {ur.status_code} {ur.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return None


def insert_article(article):
    """Insert an article into p2_articles."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, json=article, headers=HEADERS, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else data.get("id")
        print(f"  ✓ Article inserted: {article['slug']}")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} — {r.text[:300]}")
        return None


def sb_patch(table, filters, payload):
    """Patch a Supabase record."""
    filter_str = "&".join(f"{k}={v}" for k, v in filters.items())
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filter_str}"
    r = requests.patch(url, json=payload, headers=HEADERS, timeout=30)
    return r.status_code in (200, 204)


# --- Articles ---

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

ARTICLES = [
    {
        "headline": "India Says Pernod Ricard Hid the Age of Its Scotch to Dodge $314 Million in Tariffs",
        "subheadline": "Investigators allege the French spirits giant used secret codenames for its imported malts to confuse customs. The bill could top $600 million with penalties.",
        "slug": "india-pernod-ricard-scotch-whisky-tariff-314-million-codenames-20260528",
        "category": "news",
        "body": """India's customs investigators have concluded that Pernod Ricard, the French spirits conglomerate behind Chivas Regal and Absolut Vodka, deliberately withheld the age and composition of its Scotch whisky imports to pay lower tariffs — and the company now faces a $314 million tax bill that could double with penalties.

## The Accusation

According to hundreds of pages of investigation reports and submissions filed at the Delhi High Court, Indian authorities allege that Pernod's UK subsidiary Chivas Brothers shipped bulk Scotch concentrates to India at artificially low declared values. The concentrates are blended with water and caramel in India to produce popular brands like Royal Stag.

The investigators say Pernod undervalued its imports by 67.49 percent, sharply reducing the 150 percent tariff India imposes on such goods. The scheme, they allege, involved introducing new India-only internal codenames for the malts starting in 2011 — labels like "RFM" (Rich Fruity Malt) and "HMW" (Heavy Malt Whisky) — even though the final product remained identical.

"Simple products of Scotland, manufactured using common and prescribed methods by Scotch Whisky Regulations in the UK, were complicated just to avoid comparison with similar goods imported," the authorities stated in their filing.

## Pernod Fights Back

The French company denies all wrongdoing. In its Delhi High Court challenge, Pernod argues that investigators cherry-picked comparison data, selectively benchmarking its prices against Allied Blenders and Distillers (ABD) while ignoring dozens of other companies that imported similar concentrates at lower prices.

Pernod says the comparison is flawed because its import volumes were 15 times larger than ABD's, and that it was denied access to the complete pricing data used by investigators — a "gross violation of the doctrine of natural justice."

"Pernod India rejects any suggestion of wrongdoing," the company said in a statement, adding that it has been "fully compliant" and is "addressing this matter through the appropriate legal channels."

## The Numbers

The stakes are enormous. The tax demand currently stands at nearly 30 billion rupees ($314 million). Under Indian law, penalties could push the total payout past $600 million — roughly a fifth of Pernod's Indian revenue of $2.9 billion and three times its profit from the country.

India is Pernod Ricard's largest market by volume, contributing about 10 percent of the company's worldwide sales. The company operates 24 production sites across the country and recently announced plans for its largest malt distillery in Asia, in Maharashtra.

## Why NRIs Should Care

The case lands at a politically charged moment. India has been gradually reducing its 150 percent import tariff on Scotch under pressure from the UK and as part of a broader free trade agreement push. For the Indian diaspora, the dispute raises questions about whether India's regulatory environment is becoming more or less hospitable to foreign investment — a question that matters whether you are sending money home, investing in Indian markets, or watching from afar as India courts $500 billion in American trade over the next five years.

Prolonged tax disputes have historically frustrated foreign investors in India, and this case — which began in 2014 and only produced a final demand order in September 2025 — is a textbook example. If Pernod loses, it would be one of the largest tax penalties imposed on a foreign consumer goods company in India.

The Delhi High Court's decision will set a precedent not just for spirits but for how India handles transfer pricing and customs valuations across industries. For a country selling itself as an alternative to China for global manufacturing, the outcome matters.""",
        "sources": json.dumps(["Reuters", "Delhi High Court filings", "The Drinks Business"]),
        "person_image": None,  # Topic article, use Pexels
        "pexels_query": "scotch whisky barrels warehouse",
        "pexels_fallback": "whisky bottles bar shelf",
        "image_attribution": "Pexels",
    },
    {
        "headline": "Britain Will Block Indian Billionaire Sunil Mittal From Taking Control of BT. Here Is Why.",
        "subheadline": "The UK government says Openreach — which supplies fibre broadband to 22 million homes — is too important to let a foreign investor hold more than 25 percent.",
        "slug": "uk-block-sunil-bharti-mittal-bt-stake-25-percent-national-security-20260528",
        "category": "news",
        "body": """The British government will block any attempt by Indian billionaire Sunil Bharti Mittal to increase his stake in BT Group beyond 25 percent, the Financial Times reported on Thursday, citing people familiar with the matter. The decision marks a sharp line around one of the UK's most sensitive pieces of national infrastructure.

## What Happened

Bharti Enterprises, Mittal's conglomerate, bought a 24.5 percent stake in BT in 2024 from Franco-Israeli telecoms magnate Patrick Drahi and has since edged up to 24.95 percent — just below the threshold that would trigger a formal review under the UK's National Security and Investment Act.

Officials told the FT that ministers view BT's network arm, Openreach, as critical national infrastructure. Openreach supplies fibre broadband to more than 22 million homes across Britain and is central to the country's digital connectivity strategy. Any stake increase above 25 percent would require government approval, and that approval will not come, according to the report.

A British government figure said the stance is not aimed at Bharti or India specifically but reflects a broader policy position on "resilience and sovereign capability" over critical infrastructure. Officials have been signalling their position early to avoid friction later.

## Mittal's Quiet Influence

Even without crossing the 25 percent line, Mittal has been building significant influence inside BT. He has developed a close relationship with CEO Allison Kirkby, secured two board seats, and held multiple strategy meetings in recent months. People close to BT's board say Mittal has indicated no immediate plans to raise the stake further — but directors remain aware of his "broader ambitions."

Mittal's footprint in Britain extends well beyond BT. He worked with the UK government on the 2020 rescue of failed satellite venture OneWeb, and his Airtel Africa subsidiary is exploring a London listing for its mobile money business after the Iran war disrupted an earlier Middle East flotation plan.

## The Bigger Picture

The decision places Britain alongside a growing number of countries tightening foreign ownership rules around telecommunications and digital infrastructure. The EU recently proposed a Cloud and AI Development Act to expand European data-centre capacity and reduce reliance on foreign providers. Australia, Japan, and Canada have all blocked or scrutinized major telecoms acquisitions in recent years.

For Indian investors and the diaspora, the BT case is a reminder that even friendly governments will draw hard lines around infrastructure that they consider sovereign. India's own outbound investment ambitions — Bharti, the Tata Group, Reliance Industries — increasingly bump up against national security reviews in the West.

## What It Means for NRIs

Mittal is one of the most prominent Indian-origin businessmen in the world. He is the chairman of Bharti Airtel, India's second-largest telecom operator, and has been a bridge figure between Indian capital and Western markets for decades. The UK's decision to cap his influence in BT — despite his track record as a constructive, long-term investor — signals a shift in how Western governments view Indian capital in critical sectors.

For NRIs in Britain especially, the question is whether this kind of sovereign gatekeeping applies evenly or disproportionately affects Indian investors. The UK government insists the policy is nationality-blind. But the optics of blocking India's biggest telecoms billionaire from the UK's biggest telecoms company — while BT's share price languishes and the company desperately needs capital — will be hard to separate from broader anxieties about foreign ownership in a post-Brexit Britain.

Bharti Enterprises, BT, and the UK government all declined to comment.""",
        "sources": json.dumps(["Reuters", "Financial Times", "Traders Union"]),
        "person_image": "Sunil Bharti Mittal",
        "pexels_query": None,
        "pexels_fallback": None,
        "image_attribution": "Wikimedia Commons",
    },
    {
        "headline": "American Airlines Will Double Its India Tech Hub to 800 People. It Is Not Alone.",
        "subheadline": "The airline joins Southwest, JPMorgan, Nvidia, and 2,100 other companies running core engineering out of India. The GCC industry now generates $100 billion a year.",
        "slug": "american-airlines-india-hyderabad-gcc-tech-hub-double-800-employees-20260528",
        "category": "news",
        "body": """American Airlines plans to double the headcount at its Hyderabad technology hub to about 800 employees by early 2027, Reuters reported on Wednesday, in the latest sign that India's global capability centre industry has moved far beyond back-office cost-cutting.

## The Expansion

American Airlines set up its Hyderabad hub in 2024 with about 400 staff focused on software engineering, artificial intelligence, and cybersecurity. The plan is to double that within a year. The company said teams in Fort Worth, Phoenix, and Hyderabad "work closely with the business to digitize processes, deploy new tools that improve speed to market, and build a more resilient airline."

The airline is not alone. Southwest Airlines announced last week that it will expand its own Hyderabad GCC to about 1,000 employees over the next few years. The two carriers join a rapidly growing list of American corporations scaling serious technical operations in India.

## The GCC Boom

Global capability centres are no longer the glorified call centres of the early 2000s. They now handle core functions including engineering, research and development, finance, and operations. JPMorgan Chase, Walmart, McDonald's, Nvidia, and Eli Lilly have all expanded technology operations in India as costs rise elsewhere and macroeconomic uncertainties persist.

The numbers are staggering. India now hosts more than 2,100 GCCs employing about 2.36 million people and generating nearly $100 billion in annual revenue, according to a 2026 Nasscom-Zinnov report. That revenue figure has roughly doubled in five years.

Hyderabad and Bengaluru remain the two dominant cities, but Chennai, Pune, and Gurugram are gaining ground. The talent pipeline is the draw: India produces roughly 1.5 million engineering graduates a year, and labour costs — while rising — remain a fraction of equivalent roles in the United States or Western Europe.

## What Changed

The shift from back-office to core engineering happened gradually, then all at once. A decade ago, most Indian GCCs handled payroll processing, IT support, and data entry. Today, JPMorgan's Mumbai centre runs quantitative trading models. Nvidia's Bengaluru team works on GPU architecture. Google's Hyderabad campus builds core Search and Android features.

Three forces accelerated the transformation. First, the pandemic proved that critical engineering could be done remotely — and India's timezone overlap with both US coasts made it an ideal bridge. Second, the artificial intelligence boom created a global talent shortage that India was uniquely positioned to fill. Third, the Iran war and broader geopolitical instability pushed companies to diversify their operations across multiple geographies.

## Why NRIs Should Pay Attention

For Indian Americans working in technology, the GCC boom has complex implications. On one hand, it validates India's engineering talent and creates opportunities for diaspora professionals to work across both markets — managing US-India teams, building reverse-mentorship relationships, or even returning to India for senior roles that now carry real technical authority.

On the other hand, it accelerates the same labour-cost arbitrage that has been a source of anxiety in American workplaces for two decades. If American Airlines can get an AI engineer in Hyderabad for a third of what it pays in Dallas, the long-term pressure on US-based tech salaries is real. The H-1B debate — already heated — becomes even more charged when the alternative is not to bring workers to America but to move the work to India.

The GCC industry also reshapes the "brain drain" narrative. For years, India's best engineers left for Silicon Valley. Now, a growing number are staying — or returning — because the work has come to them. The salaries are not Valley-level, but they are excellent by Indian standards, and the quality of life in cities like Hyderabad and Bengaluru is increasingly competitive.

For the diaspora, the message is clear: India's role in the global technology ecosystem is no longer supplementary. It is structural. And the companies building there are not doing it to save money on helpdesk tickets. They are doing it because that is where the engineers are.""",
        "sources": json.dumps(["Reuters", "Nasscom-Zinnov 2026 Report", "Finimize"]),
        "person_image": None,
        "pexels_query": "technology office workers India",
        "pexels_fallback": "software developers office team",
        "image_attribution": "Pexels",
    },
]


def main():
    published_count = 0

    for i, art_data in enumerate(ARTICLES):
        print(f"\n{'='*60}")
        print(f"Article {i+1}: {art_data['headline'][:80]}...")
        print(f"{'='*60}")

        # --- Image sourcing ---
        image_url = None
        attribution = art_data["image_attribution"]

        if art_data.get("person_image"):
            print(f"  → Trying Wikipedia for: {art_data['person_image']}")
            image_url = fetch_wikipedia_person_image(art_data["person_image"])

        if not image_url and art_data.get("pexels_query"):
            print(f"  → Trying Pexels for: {art_data['pexels_query']}")
            image_url = fetch_pexels_image(art_data["pexels_query"], art_data.get("pexels_fallback"))
            attribution = "Pexels"

        # Upload to Supabase for permanence
        final_image_url = None
        if image_url:
            filename = f"{art_data['slug']}.jpg"
            final_image_url = upload_image_to_supabase(image_url, filename)
            if not final_image_url:
                # Fallback: use direct URL only if it's a permanent source
                if "upload.wikimedia.org" in image_url or "images.pexels.com" in image_url:
                    final_image_url = image_url
                    print(f"  → Using direct permanent URL as fallback")

        # --- Build article record ---
        article = {
            "headline": art_data["headline"],
            "subheadline": art_data["subheadline"],
            "slug": art_data["slug"],
            "category": art_data["category"],
            "vertical": art_data["category"],
            "body": art_data["body"].strip(),
            "sources": art_data["sources"],
            "image_url": final_image_url,
            "image_caption": art_data["subheadline"][:120],
            "image_attribution": attribution if final_image_url else None,
            "status": "published",
            "published_at": NOW,
            "created_at": NOW,
        }

        art_id = insert_article(article)
        if art_id:
            published_count += 1
            print(f"  ✓ Published! ID: {art_id}")
        else:
            print(f"  ✗ FAILED to publish.")

    print(f"\n{'='*60}")
    print(f"Done. Published {published_count}/{len(ARTICLES)} articles.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
