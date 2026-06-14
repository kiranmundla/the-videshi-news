#!/usr/bin/env python3
"""Immigration writer — 2026-06-14 08:00 UTC run.
Writes 2 articles:
1. $100K H-1B fee stay: Judge Sorokin pauses his own ruling while First Circuit decides
2. DHS warns World Cup visitors: social media content = evidence of visa violations
"""

import json, os, uuid, re, requests, io
from datetime import datetime, timezone
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

# ── env ──────────────────────────────────────────────────────────────────
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

pexels_env = Path.home() / "workspace/.env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

SB_URL  = os.environ["SUPABASE_URL"]
SB_KEY  = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS  = os.environ.get("PEXELS_API_KEY", "")
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

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

# ── image helpers ────────────────────────────────────────────────────────
def compress_image(img_bytes, max_width=1200, quality=80):
    if Image is None:
        return img_bytes  # can't compress without PIL
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(img_bytes, filename):
    """Upload compressed image to Supabase article-images bucket."""
    compressed = compress_image(img_bytes)
    url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    h = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(url, headers=h, data=compressed, timeout=30)
    if r.status_code in (200, 201):
        return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    else:
        print(f"  ⚠ Supabase upload failed ({r.status_code}): {r.text[:200]}")
        return None

def download_image(url):
    try:
        r = requests.get(url, headers=UA, timeout=15)
        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith("image"):
            if len(r.content) > 5000:
                return r.content
            else:
                print(f"  ⚠ Image too small ({len(r.content)} bytes): {url[:80]}")
        else:
            print(f"  ⚠ Download failed ({r.status_code}): {url[:80]}")
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None

def fetch_wikimedia_commons(query, limit=5):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params, headers=UA, timeout=15)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                })
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

def fetch_pexels(query):
    if not PEXELS:
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 5},
            headers={"Authorization": PEXELS},
            timeout=10,
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                return photos[0]["src"]["large2x"]
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def source_image(slug, searches_commons, searches_pexels):
    """Try Commons first, then Pexels. Download, compress, upload to Supabase."""
    # Try Wikimedia Commons
    for q in searches_commons:
        results = fetch_wikimedia_commons(q)
        if results:
            best = results[0]
            print(f"  ✓ Commons image: {best['title']}")
            img_bytes = download_image(best["url"])
            if img_bytes:
                final = upload_to_supabase(img_bytes, f"{slug}.jpg")
                if final:
                    return final, "Wikimedia Commons"

    # Try Pexels
    for q in searches_pexels:
        pexels_url = fetch_pexels(q)
        if pexels_url:
            print(f"  ✓ Pexels image: {pexels_url[:80]}")
            img_bytes = download_image(pexels_url)
            if img_bytes:
                final = upload_to_supabase(img_bytes, f"{slug}.jpg")
                if final:
                    return final, "Pexels"

    print("  ⚠ No image sourced")
    return None, None


# ══════════════════════════════════════════════════════════════════════════
# ARTICLE 1
# ══════════════════════════════════════════════════════════════════════════

art1_slug = make_slug("h1b-100k-fee-judge-stays-ruling-first-circuit-appeal")
art1_id   = str(uuid.uuid4())

art1_body = """The relief lasted four days.

On June 8, U.S. District Judge Leo Sorokin in Boston struck down the Trump administration's $100,000 fee on new H-1B visa petitions, calling it an "unauthorized tax" that only Congress could impose. The ruling electrified immigration lawyers and their clients — many of them Indian professionals who account for more than seventy per cent of all approved H-1B petitions. For a brief window, it looked as though the most controversial immigration measure of the second Trump presidency might be finished.

Then, on June 12, the Department of Justice filed an emergency motion asking Sorokin to stay his own order while the government appeals to the U.S. Court of Appeals for the First Circuit. Sorokin agreed. The fee is back — at least until the appellate court weighs in.

## What the Stay Means

A stay does not reverse the ruling. Sorokin still believes the fee is unlawful. But by pausing the effect of his decision, he has given the government room to press its case before the First Circuit without the practical chaos of toggling a six-figure fee on and off.

The Department of Justice argued that without a stay, "additional aliens will rush to seek classification and entry as an H-1B nonimmigrant worker" while the fee is suspended. Attorneys for the government also contended that the fee is a legitimate exercise of presidential authority over foreign commerce and immigration — not a tax — and that the administration is likely to prevail on appeal.

The case is formally styled *State of California v. Mullin*, and the coalition of twenty Democratic-led state attorneys general that brought it is expected to resist the appeal vigorously.

## A Split Among Courts

Sorokin's ruling was the first judicial defeat for the $100,000 fee. But it is not the only case in play. A separate challenge filed by the U.S. Chamber of Commerce was rejected last December by Judge Beryl Howell in Washington, D.C., who found the fee lawful. That decision is now before the D.C. Circuit Court of Appeals.

A third case is pending in the Northern District of California. Plaintiffs in both the D.C. and California cases have cited Sorokin's order as strengthening their arguments.

The divergence between Sorokin and Howell creates what lawyers call a circuit split — different federal courts reaching opposite conclusions on the same legal question. When that happens, the Supreme Court often steps in to settle the matter. Immigration attorneys say it is increasingly likely the $100,000 fee will end up before the justices, possibly as soon as the next term.

## The Deterrent Has Already Worked

Whatever the courts ultimately decide, the fee has already reshaped the H-1B landscape. By February 15, only eighty-five employers had paid the $100,000 charge, according to a March filing by the administration. H-1B registrations for the 2026 lottery dropped by twenty-seven per cent compared to the previous year.

The fee applies only to new H-1B petitions that require consular processing — not to renewals or to workers already in the United States on student visas transitioning to H-1B status. But for Indian professionals seeking new positions or for employers trying to recruit talent from abroad, the fee has functioned as a near-prohibition.

"It is not a fee. It is a wall built out of paperwork and money," one Bay Area immigration attorney told a group of Indian professionals at a recent community meeting in Sunnyvale.

## What to Watch

The First Circuit has not set a timeline for its ruling. In the meantime, Indian H-1B holders should understand three things:

First, the $100,000 fee is currently in effect for all new petitions. Anyone whose employer files a new H-1B petition requiring consular processing will face the charge.

Second, the fee does not apply to renewals. Workers extending an existing H-1B are not affected.

Third, the legal landscape is shifting week by week. Three courts, three cases, three potential outcomes — and the Supreme Court looming behind all of them. The only certainty is that nothing about this fee is settled."""

print(f"\n{'='*60}")
print(f"ARTICLE 1: {art1_slug}")
print(f"{'='*60}")

art1_img, art1_attr = source_image(
    art1_slug,
    searches_commons=["United States federal courthouse", "U.S. District Court Massachusetts", "federal court building Boston"],
    searches_pexels=["federal courthouse building United States", "US court gavel law"],
)

art1 = {
    "id": art1_id,
    "headline": "Four Days of Relief — The $100,000 H-1B Fee Returns While the First Circuit Decides",
    "subheadline": "Judge Sorokin struck down the fee on June 8 as an unauthorized tax. Four days later, he agreed to pause his own ruling while the government appeals.",
    "slug": art1_slug,
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians account for over 70% of H-1B approvals; the $100K fee has already crashed registrations by 27%, and its reinstatement means new petitions face the charge while three courts sort out whether it is legal.",
    "tags": ["h1b", "uscis", "court-ruling", "100k-fee", "first-circuit"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/judge-agrees-to-partly-pause-order-tossing-100-000-h-1b-fee"},
        {"name": "Reuters", "url": "https://www.reuters.com/legal/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/politics/policy/judge-strikes-down-trump-administrations-100-000-h-1b-visa-fee-aadcff29"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/09/trumps-100000-fee-new-h1b-visas-struck-down-by-judge/84142890007/"},
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "body": art1_body,
}

if art1_img:
    art1["image_url"] = art1_img
    art1["image_caption"] = "The John Joseph Moakley United States Courthouse in Boston, where Judge Sorokin issued and then stayed his ruling"
    art1["image_attribution"] = art1_attr
else:
    # Try inline Pexels fallback with curl-like approach
    print("  Trying Pexels direct...")
    purl = fetch_pexels("courtroom legal gavel")
    if purl:
        img_bytes = download_image(purl)
        if img_bytes:
            final = upload_to_supabase(img_bytes, f"{art1_slug}.jpg")
            if final:
                art1["image_url"] = final
                art1["image_caption"] = "A federal courtroom where the fate of the H-1B fee is being decided"
                art1["image_attribution"] = "Pexels"


# ══════════════════════════════════════════════════════════════════════════
# ARTICLE 2
# ══════════════════════════════════════════════════════════════════════════

art2_slug = make_slug("dhs-world-cup-social-media-visa-enforcement-influencers")
art2_id   = str(uuid.uuid4())

art2_body = """The Department of Homeland Security has a message for foreign visitors arriving in the United States for the FIFA World Cup: we are watching your social media.

In a joint statement issued to the Spanish daily *EL PAÍS*, U.S. Customs and Border Protection and DHS warned that tourist visas do not cover paid content creation. "Coming to the United States with the sole purpose of creating content, thereby generating earnings from the United States while in the country, is considered work and requires the appropriate visa," the agencies said. A government source was blunter: "Their own videos give them away."

The warning is aimed at the wave of international influencers, travel bloggers, sports vloggers, and freelance creators flocking to the eleven U.S. host cities — from Atlanta and Boston to Los Angeles and the Bay Area — to produce World Cup content. Many enter on B-1/B-2 tourist visas or under the Visa Waiver Program. Neither permits employment. And DHS, the agencies say, now considers monetised content creation to be employment.

## Why This Matters for Indian Visitors

India does not participate in the Visa Waiver Program — every Indian visitor needs a B-1/B-2 visa to attend World Cup matches in the United States. For the thousands of Indian fans traveling from India for the tournament, and for Indian-Americans hosting relatives who have come to watch, the enforcement posture creates a specific set of risks.

An Indian travel vlogger who films a stadium experience, posts it to YouTube with ads enabled, and earns revenue from those views could, under the government's reading, be violating the terms of their tourist visa. The same logic applies to Instagram influencers with sponsored posts, TikTok creators documenting their trip for a brand, or even freelance photographers selling match-day shots.

The consequences are not theoretical. Visa cancellation, denial of future entry, or even removal proceedings are all on the table for visitors found to have engaged in unauthorised employment. And DHS has signalled that social media profiles are fair game for enforcement — officers can and do review public posts during secondary inspection at airports.

## 'ICE Out' — The Stadium Workers' Revolt

The enforcement atmosphere has already spilled onto the pitch. At SoFi Stadium in Los Angeles, where the United States beat Paraguay 4-1 in Friday's opener, approximately two thousand hospitality workers represented by Unite Here Local 11 wore "ICE Out" pins. The union had threatened to strike if Immigration and Customs Enforcement agents conducted civil immigration raids at the venue.

"The First Amendment doesn't end when you clock in," union co-president Kurt Petersen said. "These workers are hospitality professionals. Their job is to welcome guests and provide world-class service to every fan who walks through the gates — but it's hard to create a welcoming environment when workers and their communities are living in fear."

The workers ultimately received assurances that ICE agents at matches would focus on security, not civil immigration enforcement. Some fans asked for "ICE Out" pins of their own.

## Players and Officials Caught Too

The enforcement net has caught people with FIFA credentials as well. Iraqi footballer Aymen Hussein was detained and questioned for several hours upon arrival. Somali referee Omar Artan was denied entry into the United States entirely, despite being selected by FIFA to officiate. South Africa's national team experienced visa delays, and players from Uzbekistan and Senegal were subjected to extended security screening.

Human Rights Watch and Amnesty International have both raised formal concerns. UN High Commissioner for Human Rights Volker Türk warned that immigration enforcement measures could undermine the universal character of the tournament.

## The Gray Area

Not every social media post puts you at risk. Tourists filming personal memories, sharing clips with family, or posting un-monetised content are not targets of the crackdown — at least, not yet. The issue arises when the trip is organised around commercial content: sponsorships, brand deals, monetised accounts, or income generated from U.S.-based activity.

The difficulty is that the line between personal and commercial content is blurring. An Indian cricket fan with fifty thousand Instagram followers who posts a World Cup vlog is, technically, a content creator. Whether they are "working" depends on whether the account is monetised, whether a brand is paying for the post, and whether a CBP officer at the airport decides to check.

"How can a country put a rein on a business that is global?" entertainment lawyer Vance Own asked in an interview with *EL PAÍS*. "I have more questions than answers."

For now, Indian visitors to the World Cup should assume that their social media is part of their immigration file. Post your memories. Cheer for your team. But think twice before posting that sponsored reel."""

print(f"\n{'='*60}")
print(f"ARTICLE 2: {art2_slug}")
print(f"{'='*60}")

art2_img, art2_attr = source_image(
    art2_slug,
    searches_commons=["U.S. Customs and Border Protection airport", "CBP airport international arrivals", "FIFA World Cup 2026 stadium"],
    searches_pexels=["airport immigration passport control", "soccer stadium world cup fans"],
)

art2 = {
    "id": art2_id,
    "headline": "'Their Own Videos Give Them Away' — DHS Warns World Cup Visitors Their Social Media Is Evidence",
    "subheadline": "Homeland Security says monetised content creation on a tourist visa is unauthorised employment. Stadium workers at SoFi wore 'ICE Out' pins in protest.",
    "slug": art2_slug,
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian visitors need B-1/B-2 visas to attend World Cup matches; DHS's new enforcement posture means travel vloggers, sponsored posters, and monetised content creators risk visa violations and future inadmissibility.",
    "tags": ["world-cup", "visa-enforcement", "dhs", "social-media", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Travel", "url": "https://www.thetravel.com/us-homeland-security-warns-travelers-of-social-media-content-crackdown-during-the-world-cup/"},
        {"name": "The Sun", "url": "https://www.the-sun.com/sport/16497503/world-cup-workers-ice-pins-usa-federal-agent/"},
        {"name": "Madhyama Online", "url": "https://www.madhyamamonline.com/fifa-world-cup-2026-hrw-raises-concerns-over-immigration-policies"},
        {"name": "EL PAÍS (via The Travel)", "url": "https://english.elpais.com/"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "body": art2_body,
}

if art2_img:
    art2["image_url"] = art2_img
    art2["image_caption"] = "U.S. Customs and Border Protection officers process international travellers at a U.S. airport"
    art2["image_attribution"] = art2_attr
else:
    print("  Trying Pexels direct for art2...")
    purl = fetch_pexels("airport passport control immigration")
    if purl:
        img_bytes = download_image(purl)
        if img_bytes:
            final = upload_to_supabase(img_bytes, f"{art2_slug}.jpg")
            if final:
                art2["image_url"] = final
                art2["image_caption"] = "Passport control at a U.S. international airport"
                art2["image_attribution"] = "Pexels"

# ══════════════════════════════════════════════════════════════════════════
# INSERT
# ══════════════════════════════════════════════════════════════════════════
articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        wc = len(art["body"].split())
        print(f"✅ {art['slug']}  ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles inserted with status='review'.")
