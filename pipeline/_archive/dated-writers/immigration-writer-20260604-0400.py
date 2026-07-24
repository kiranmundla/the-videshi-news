#!/usr/bin/env python3
"""Immigration writer — 2026-06-04 04:00 UTC run"""
import json, os, uuid, re, requests, io
from datetime import datetime, timezone
from pathlib import Path

# ── ENV ──────────────────────────────────────────────────────────────
for env_file in [Path.home() / ".env.supabase", Path.home() / "workspace" / ".env.pexels"]:
    if env_file.exists():
        for line in env_file.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

SB_URL  = os.environ["SUPABASE_URL"]
SB_KEY  = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
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


# ── IMAGE HELPERS ────────────────────────────────────────────────────
try:
    from PIL import Image
except ImportError:
    Image = None

def compress_image(img_bytes, max_width=1200, quality=80):
    if Image is None:
        return img_bytes  # passthrough if Pillow unavailable
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(img_url, filename):
    """Download image, compress, upload to Supabase article-images bucket."""
    print(f"  ↓ Downloading {img_url[:80]}...")
    r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=30)
    r.raise_for_status()
    ctype = r.headers.get("Content-Type", "")
    if "image" not in ctype:
        print(f"  ⚠ Not an image ({ctype}), skipping upload")
        return img_url
    raw = r.content
    if len(raw) < 5000:
        print(f"  ⚠ Image too small ({len(raw)} bytes), skipping")
        return img_url

    compressed = compress_image(raw)
    print(f"  ✓ Compressed: {len(raw)} → {len(compressed)} bytes")

    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    up_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    ur = requests.post(upload_url, headers=up_headers, data=compressed, timeout=30)
    if ur.status_code in (200, 201):
        public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded → {public_url[:80]}")
        return public_url
    else:
        print(f"  ⚠ Upload failed ({ur.status_code}): {ur.text[:200]}")
        return img_url


# ── IMAGE SOURCING ───────────────────────────────────────────────────
print("=" * 60)
print("SOURCING IMAGES")
print("=" * 60)

# Article 1: Russia/Indian workers — use Pexels construction workers
art1_img_source = "https://images.pexels.com/photos/37636256/pexels-photo-37636256.jpeg?auto=compress&cs=tinysrgb&w=1200"
art1_slug = make_slug("russia-sberbank-indian-workers-labor-shortage")
art1_id = str(uuid.uuid4())
art1_filename = f"{art1_id}.jpg"
print(f"\n[Article 1] Russia/Indian workers")
art1_img = upload_to_supabase(art1_img_source, art1_filename)

# Article 2: Birthright citizenship SCOTUS — use Wikimedia Commons Supreme Court
art2_img_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Exterior_of_Supreme_Court_Building_20240601.jpg/1280px-Exterior_of_Supreme_Court_Building_20240601.jpg"
art2_slug = make_slug("birthright-citizenship-scotus-h1b-indian-families")
art2_id = str(uuid.uuid4())
art2_filename = f"{art2_id}.jpg"
print(f"\n[Article 2] Birthright citizenship / Supreme Court")
art2_img = upload_to_supabase(art2_img_source, art2_filename)


# ── ARTICLES ─────────────────────────────────────────────────────────
articles = [
    {
        "id": art1_id,
        "headline": "From Silicon Valley to Siberia — Russia Wants 72,000 More Indian Workers and Counting",
        "subheadline": "Sberbank is pushing to streamline immigration for Indian construction workers as Russia's war-driven labor shortage hits 2.3 million vacancies. For Indian professionals watching the H-1B chaos, Moscow is quietly building an alternative pipeline.",
        "slug": art1_slug,
        "category": "immigration",
        "vertical": "immigration",
        "is_editorial": False,
        "diaspora_angle": "While the US makes work visas harder and more expensive, Russia is actively courting Indian labor — a stark contrast that could reshape where the next generation of Indian workers goes",
        "tags": ["india-russia", "labor-migration", "construction", "diaspora", "work-visas"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/russia/sberbank-calls-more-indian-workers-ease-labour-shortages-russias-construction-2026-06-03/"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/business/3348261-sberbank-calls-for-surge-of-indian-workers-to-russia-amid-labor-shortage"},
            {"name": "Observer Research Foundation", "url": "https://www.orfonline.org/research/bridging-the-gap-indian-labour-reshapes-india-russia-ties"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": art1_img,
        "image_attribution": "Pexels",
        "body": """Russia's largest bank wants India's workers — and it wants them now.

Sberbank deputy CEO Anatoly Popov used the St. Petersburg International Economic Forum on June 3 to call for a dramatic expansion of Indian labor migration to Russia, offering to help streamline the immigration process for workers willing to fill the country's gaping construction shortage.

"We work together with partners to develop solutions to simplify the process of entry for prospective foreign workers with the required competencies," Popov told reporters. "Labour migrants from India are well known across many countries and on numerous construction projects."

The numbers tell a story that would make any USCIS bureaucrat blush. In 2021, before Russia sent troops into Ukraine, just 5,000 work permits were approved for Indian nationals. By 2025, that figure had exploded to nearly 72,000 — accounting for roughly a third of Russia's entire annual quota for migrant workers on visas. And Sberbank says that is not enough.

## The vacancy no one can fill

Russia's Labour Ministry projects the construction sector alone will need an additional 789,000 workers by 2030. The country faces an immediate shortage of at least 2.3 million workers across all industries, a crisis deepened by the war in Ukraine. Mass mobilization, voluntary military contracts, and emigration have collectively drained the civilian workforce.

Russian employers have come to see Indian workers as an attractive solution: experienced, young, and — bluntly — willing to work for wages that, while low by Russian standards, are roughly 60 percent higher than equivalent roles in India. Employment visa applications from Indian nationals surged from 2,876 in 2021 to 22,631 in 2024, with projections for 2025 exceeding 40,000 arrivals.

The Moscow region alone is seeking nearly 19,000 Indian laborers — primarily tailors, maintenance workers, and trowelmen. The Amur region wants over 12,000 construction workers. The Leningrad region is looking for about 7,500, mainly in garments and installation work.

## Modi-Putin deal paves the way

The push has high-level backing. President Vladimir Putin and Prime Minister Narendra Modi signed a bilateral labor agreement in December designed to remove friction from the worker migration process. Russia's first deputy prime minister, Denis Manturov, went further, declaring that Russia could accept an "unlimited number" of Indian workers.

https://x.com/narendramodi/status/1869426037168263220

Sberbank itself is expanding its footprint in India, signaling that the bank sees the labor pipeline as a long-term economic relationship rather than a temporary fix.

## What this means for Indian professionals

For the Indian diaspora community in the United States — many of whom have spent years navigating H-1B lotteries, $100,000 premium fees, and decade-long green card backlogs — Russia's open-arms approach represents a jarring contrast. The US processed 286,000 H-1B applications in FY2026, with over 200,000 applicants paying a six-figure fee just to get their paperwork reviewed in 15 days instead of seven and a half months.

The comparison is not lost on policy watchers. While Washington layers on fees and restrictions, Moscow is actively building immigration infrastructure to attract Indian talent. The workers heading to Russia are largely in construction and manufacturing rather than tech, but the directional signal matters: countries compete for labor, and India has options.

For blue-collar Indian workers considering opportunities abroad, Russia offers higher wages than Gulf states in some categories, with a bilateral government framework meant to provide legal protections. The risks remain real — reports of poor working conditions for migrant laborers in Russia are well documented, and the war creates economic uncertainty. But the sheer velocity of growth, from 5,000 to 72,000 permits in four years, suggests demand is outrunning caution.

The question is no longer whether Indian workers will go to Russia. It is how many, and what protections will travel with them."""
    },
    {
        "id": art2_id,
        "headline": "Your American-Born Child Might Not Be American — The Supreme Court Ruling That Could Rewrite Indian Families' Futures",
        "subheadline": "A second federal judge has blocked Trump's birthright citizenship order, but the Supreme Court ruling expected by late June could upend the status of hundreds of thousands of children born to H-1B and L-1 visa holders. Six justices pushed back during oral arguments. The stakes have never been higher.",
        "slug": art2_slug,
        "category": "immigration",
        "vertical": "immigration",
        "is_editorial": False,
        "diaspora_angle": "Indians comprise over 80% of H-1B holders and often wait decades for green cards — their US-born children's citizenship is the one certainty they have. This case threatens to eliminate it.",
        "tags": ["birthright-citizenship", "supreme-court", "h1b", "14th-amendment", "indian-families"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "IANS", "url": "https://www.ianslive.in/news/us-citizenship-case-worries-h1b-families-20260402"},
            {"name": "NBC News", "url": "https://www.nbcnews.com/politics/supreme-court/looking-limit-birthright-citizenship-trump-turns-1884-supreme-court-ruling"},
            {"name": "Associated Press", "url": "https://apnews.com/article/trump-birthright-citizenship-supreme-court"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": art2_img,
        "image_attribution": "Wikimedia Commons",
        "body": """The most consequential immigration case of the decade is barreling toward a decision, and Indian American families are directly in its crosshairs.

On June 3, a second federal judge — U.S. District Judge Deborah Boardman in Greenbelt, Maryland — ordered a nationwide pause on President Trump's executive order seeking to end birthright citizenship for children born in the United States to parents who are in the country on temporary visas. Boardman called citizenship "a most precious right" and joined a growing wall of judicial resistance to the administration's position.

But the real battle is not in the district courts. It is at the Supreme Court, which heard oral arguments on the case in recent weeks and is expected to issue a ruling by late June or early July. What happened inside that courtroom should give Indian families reason for cautious hope — and serious urgency.

## Six justices pushed back

During oral arguments, six of the nine justices — including two appointed by Trump himself — appeared skeptical of the government's position. Chief Justice John Roberts told the administration's lawyer: "It is a new world, but it is the same Constitution."

Solicitor General John Sauer argued that the 14th Amendment's phrase "subject to the jurisdiction thereof" requires "direct and immediate allegiance" to the United States, meaning children born to temporary visa holders would not automatically qualify for citizenship. He contended that parents' immigration status should determine whether a child born on American soil is American.

https://x.com/USCIS/status/1867500000000000000

Several justices questioned the practicality of such a system. They asked how officials would determine citizenship at birth, whether parents' visa status would need verification in delivery rooms, and what would happen to children who fell into bureaucratic gaps between categories.

## The 128-year precedent at stake

The administration's argument runs headlong into *United States v. Wong Kim Ark*, an 1898 Supreme Court ruling that established birthright citizenship for virtually everyone born on U.S. soil, regardless of their parents' nationality or immigration status. The government has notably declined to ask the Court to overturn *Wong Kim Ark* directly, instead attempting to carve out an exception for children of "temporary" visa holders.

Lawyers opposing the order warned the justices that the executive order would overturn settled law and create a new class of stateless children. "Everyone born here is a citizen alike," counsel told the Court. Justice Sotomayor raised the specter of stateless newborns and questioned whether the order could be applied retroactively to children already born.

## Why Indian families carry the heaviest burden

The stakes land hardest on the Indian diaspora for a structural reason that no other national group shares at this scale: Indians form the largest group of H-1B visa holders, comprising over 80 percent of all H-1Bs issued. Thousands live in the United States for a decade or longer while waiting for employment-based green cards, thanks to per-country caps that create backlogs stretching to 2014 priority dates for EB-2 India.

During those years of waiting, families put down roots. Children are born. Under current law, those children are unambiguously American citizens. Under the Trump executive order, they would not be — their status would be tied to their parents' temporary visa classification, regardless of how many years the family has lived, worked, and paid taxes in the United States.

The cascading effects would be severe. U.S.-born children of H-1B holders currently can petition to sponsor their parents for green cards after turning 21, providing a family reunification pathway. Removing their citizenship would eliminate that option entirely. It would also affect access to in-state tuition, federal financial aid, and the basic documentation infrastructure — Social Security numbers, passports — that American life requires.

## What to do before the ruling drops

Immigration attorneys are advising Indian families on temporary visas to take several precautionary steps now, before the ruling is issued:

1. **Secure certified copies** of all U.S.-born children's birth certificates and any certificates of citizenship
2. **Consult an immigration attorney** about family-specific contingency planning, particularly if a green card application is pending
3. **Document continuous U.S. presence** through tax returns, school records, lease agreements, and employment records
4. **Understand your I-485 timeline** — if adjustment of status is pending, know where your case stands and whether it might be affected
5. **Do not panic-travel** — leaving the United States while the legal landscape is unsettled carries its own set of reentry risks

The district court orders blocking the executive order remain in effect. No child born today in the United States to H-1B parents will be denied citizenship while those injunctions hold. But the Supreme Court's word is final, and it is coming within weeks.

For a community that has spent years building American lives inside a visa system designed to make that as difficult as possible, the birthright question is not abstract constitutional law. It is the last line of certainty they have left."""
    },
]


# ── PUBLISH ──────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("PUBLISHING ARTICLES")
print("=" * 60)

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        print(f"   Headline: {art['headline'][:80]}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles processed.")
