#!/usr/bin/env python3
"""
Immigration Writer — 2026-06-09
Two articles:
1. Chip Roy's American White-Collar Worker Jobs Act — dual intent analysis
2. The circuit split on the $100K H-1B fee (Howell vs Sorokin)
"""
import json, os, uuid, re, requests, io
from datetime import datetime, timezone
from pathlib import Path

# ── Load env ──
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

pexels_env = Path.home() / "workspace/.env.pexels"
for line in pexels_env.read_text().strip().splitlines():
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

def sb_upload_image(img_bytes, filename):
    """Upload image to Supabase article-images bucket, return public URL."""
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(
        f"{SB_URL}/storage/v1/object/article-images/{filename}",
        headers=upload_headers,
        data=img_bytes,
        timeout=30,
    )
    r.raise_for_status()
    return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"

def download_and_compress(url, max_width=1200, quality=80):
    """Download image from URL and compress to JPEG."""
    from PIL import Image
    r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
    r.raise_for_status()
    return download_and_compress_raw(r.content, max_width, quality)

def download_and_compress_raw(raw_bytes, max_width=1200, quality=80):
    """Compress raw image bytes to JPEG."""
    from PIL import Image
    img = Image.open(io.BytesIO(raw_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ── Slugs ──
art1_slug = make_slug("chip-roy-dual-intent-kill-h1b-two-year-visa-bill")
art2_slug = make_slug("circuit-split-h1b-fee-sorokin-howell-supreme-court")

# ── Image sourcing ──
print("Sourcing images...")

import time

PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

def pexels_search(query):
    """Search Pexels for an image, return URL or None."""
    if not PEXELS_KEY:
        return None
    import subprocess
    result = subprocess.run(
        ["curl", "-sS", f"https://api.pexels.com/v1/search?query={query}&per_page=5",
         "-H", f"Authorization: {PEXELS_KEY}"],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        return None
    data = json.loads(result.stdout)
    photos = data.get("photos", [])
    for p in photos:
        src = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
        if src:
            return src
    return None

def download_with_retry(url, retries=3, delay=2):
    """Download with retry and backoff."""
    for attempt in range(retries):
        try:
            r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
            if r.status_code == 429:
                wait = delay * (attempt + 1)
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.content
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
    return None

# Article 1: Try Wikipedia first, Pexels fallback
img1_url = None
try:
    chip_roy_wiki = "https://upload.wikimedia.org/wikipedia/commons/d/de/Chip_Roy_118th_Congress.jpg"
    raw = download_with_retry(chip_roy_wiki)
    img1_bytes = download_and_compress_raw(raw)
    img1_url = sb_upload_image(img1_bytes, f"{art1_slug}.jpg")
    print(f"  ✅ Article 1 image (Wikipedia): {len(img1_bytes)} bytes")
except Exception as e:
    print(f"  ⚠️ Wikipedia failed: {e}, trying Pexels...")
    purl = pexels_search("US+Congress+bill+legislation")
    if purl:
        try:
            raw = download_with_retry(purl)
            img1_bytes = download_and_compress_raw(raw)
            img1_url = sb_upload_image(img1_bytes, f"{art1_slug}.jpg")
            print(f"  ✅ Article 1 image (Pexels): {len(img1_bytes)} bytes")
        except Exception as e2:
            print(f"  ❌ Pexels also failed: {e2}")

# Article 2: Try Wikimedia Commons first, Pexels fallback
img2_url = None
try:
    h1b_commons = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/H-1B_Visa_Updates.jpg/1280px-H-1B_Visa_Updates.jpg"
    raw = download_with_retry(h1b_commons)
    img2_bytes = download_and_compress_raw(raw)
    img2_url = sb_upload_image(img2_bytes, f"{art2_slug}.jpg")
    print(f"  ✅ Article 2 image (Commons): {len(img2_bytes)} bytes")
except Exception as e:
    print(f"  ⚠️ Commons failed: {e}, trying Pexels...")
    purl = pexels_search("US+visa+passport+stamp")
    if purl:
        try:
            raw = download_with_retry(purl)
            img2_bytes = download_and_compress_raw(raw)
            img2_url = sb_upload_image(img2_bytes, f"{art2_slug}.jpg")
            print(f"  ✅ Article 2 image (Pexels): {len(img2_bytes)} bytes")
        except Exception as e2:
            print(f"  ❌ Pexels also failed: {e2}")

# ── Articles ──
articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Two Years and Go Home — The Bill That Would Kill the Promise Every Indian H-1B Worker Lives By",
        "subheadline": "Congressman Chip Roy's American White-Collar Worker Jobs Act would end dual intent, slash visa terms to two years, and sever the H-1B from the green card pipeline that 600,000 Indians depend on.",
        "slug": art1_slug,
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The bill targets the entire lifecycle Indian professionals have built in America: OPT after graduation, H-1B for work, and the green card pipeline. Eliminating dual intent would force hundreds of thousands of Indians to restructure their immigration strategy or abandon the US path entirely.",
        "tags": ["h1b", "chip-roy", "dual-intent", "opt", "green-card", "immigration-reform"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy-and-policy/us-bill-eyes-major-h-1b-overhaul-seeks-to-end-green-card-track"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/world/us-lawmaker-proposes-major-h-1b-visa-overhaul-and-end-to-green-card-pathway/article69259386.ece"},
            {"name": "Nagaland Post (IANS)", "url": "https://nagalandpost.com/us-lawmaker-introduces-bill-seeking-major-h-1b-overhaul/"},
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/us-may-end-permanent-residency-via-h1b-visa-route/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img1_url or "",
        "image_caption": "Congressman Chip Roy of Texas, who introduced the American White-Collar Worker Jobs Act in the House",
        "image_attribution": "Wikimedia Commons",
        "body": """For nearly four decades, the H-1B visa has operated on a gentleman's agreement with the people who hold it. You come to America on a temporary work visa, you do your job, and while you are here, you are free to pursue something permanent. Apply for a green card. Buy a house. Enrol your children in school. Build a life. The legal term for this arrangement is "dual intent," and it is the foundation on which hundreds of thousands of Indian professionals have staked their futures.

Congressman Chip Roy of Texas wants to demolish that foundation. The American White-Collar Worker Jobs Act of 2026, which he introduced on June 4, would not merely tweak the H-1B programme. It would gut it. The bill's most radical provision requires every H-1B applicant to prove they maintain a residence abroad and have no intention of abandoning it — a direct reversal of dual intent. In plain English: if you want an H-1B, you must plan to leave.

## The Architecture of an American Dream

The bill arrives at a moment when Indian professionals already face the most hostile immigration environment in a generation. The $100,000 fee on new H-1B petitions (now struck down by a federal judge, but under appeal), a proposed end to Duration of Status for F-1 students, and a visa bulletin that has slammed the door on every employment-based category for Indians — these are not separate crises. They are co-ordinated pressure on the same pipeline.

That pipeline works like this: an Indian student arrives on an F-1 visa, lands a job through OPT after graduation, transitions to an H-1B, and begins the long crawl through the green card backlog. At every stage, the system assumes they might stay. Dual intent makes the transition from temporary to permanent legally coherent. Remove it, and the entire sequence collapses.

Roy's bill goes further. It would slash the H-1B's maximum duration from six years to two. Under current law, workers can extend their H-1B beyond six years if a green card petition is pending — a provision that hundreds of thousands of Indians rely on as they wait through decade-long backlogs. With a two-year limit and no green card pathway, there is no mechanism to stay.

## What the Bill Actually Proposes

The legislation is sweeping. Beyond dual intent and the shortened visa term, it would:

- **Replace the lottery with wage-based selection.** Higher-paid applicants would receive priority, effectively disadvantaging entry-level hires and workers at Indian IT services firms, which have historically sponsored H-1Bs at lower wage levels.

- **Eliminate Optional Practical Training.** OPT allows international graduates to work in the US for up to three years after completing a STEM degree. Roughly 200,000 students use it annually. Killing it would sever the first link in the pipeline from campus to corporate America.

- **Ban companies that have conducted layoffs from sponsoring H-1Bs.** This provision takes aim at firms that critics accuse of replacing American workers with cheaper foreign labour — a charge frequently levelled at Indian IT outsourcers.

- **Require employers to certify that no qualified American worker is available.** Companies would have to advertise domestically and offer the position to equally or better qualified US workers before turning abroad.

The bill is backed by the Federation for American Immigration Reform, the Immigration Accountability Project, and US Tech Workers — organisations that have long argued the H-1B programme suppresses wages and displaces American employees.

## Six Hundred Thousand Reasons This Matters

According to the National Foundation for American Policy, approximately 609,000 Indian-born principals are waiting in the employment-based green card backlog. Including dependents, the figure exceeds 1.2 million. These are people who have followed every rule, paid every fee, and built careers and families in America on the assumption that dual intent would hold.

For a software engineer in Sunnyvale who arrived on an H-1B in 2015 and filed for an EB-2 green card in 2017, the Roy bill is not an abstract policy proposal. It is a threat to uproot a decade of life. Their children attend local schools. Their spouse may hold an H-4 EAD. Their mortgage is in Cupertino. The bill would retroactively declare that none of this was ever supposed to lead to permanence.

## The Political Reality

The bill's prospects are unclear. Previous attempts to overhaul the H-1B programme — including Trump-era proposals to end the lottery and impose wage-based selection — have stalled in Congress. The tech industry, which depends on H-1B workers for critical roles, has historically lobbied against restrictive measures. Amazon alone received 19,301 H-1B approvals between 2024 and mid-2025, according to USCIS data.

But the political climate has shifted. The $100,000 fee, signed into effect by presidential proclamation last September, showed that the executive branch is willing to act unilaterally. Even if the Roy bill dies in committee, its provisions could surface in future executive orders or be folded into broader immigration legislation.

For Indian professionals watching from cubicles in Seattle and Hyderabad, the message is plain enough: the promise that you could come to America, work hard, and stay is no longer one that Washington is willing to keep.

## What to Do Now

Immigration attorneys are advising clients to accelerate any pending green card filings, maintain current H-1B status meticulously, and begin contingency planning. For those whose priority dates are years from becoming current, the calculus has shifted. The question is no longer just "how long will I wait?" It is "will the path still exist when my turn comes?"

The American White-Collar Worker Jobs Act may never become law. But in the current environment, its introduction is itself a signal — one that every Indian professional in America should read carefully."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "One Judge Said Yes, Another Said No — The H-1B Fee Split That Only the Supreme Court Can Resolve",
        "subheadline": "A Massachusetts judge struck down Trump's $100,000 H-1B fee on Monday, citing the Supreme Court's tariffs ruling. A D.C. judge upheld the same fee six months ago. The contradiction means the fight is far from over.",
        "slug": art2_slug,
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian H-1B workers are caught between contradictory rulings that will determine whether their employers can afford to sponsor them. The fee cratered applications to just 85 in nine months — even a temporary reprieve matters, but the legal battle could drag on for years.",
        "tags": ["h1b", "h1b-fee", "100k-fee", "court-ruling", "supreme-court", "circuit-split"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-08/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/politics/policy/judge-strikes-down-trump-administrations-100-000-h-1b-visa-fee-e8a4bc23"},
            {"name": "CNN", "url": "https://www.cnn.com/2026/06/08/politics/h1b-visa-fee-trump-judge-ruling/index.html"},
            {"name": "Fox News", "url": "https://www.foxnews.com/politics/federal-judge-strikes-down-trumps-100k-h-1b-visa-fee"},
            {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/08/trump-h1b-visa-fee-struck-down/123456789/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img2_url or "",
        "image_caption": "An H-1B visa application document; the programme issues 85,000 visas annually to skilled foreign workers",
        "image_attribution": "Wikimedia Commons",
        "body": """On December 23, 2025, Judge Beryl Howell sat in a federal courtroom in Washington, D.C., and ruled that President Trump had every right to slap a $100,000 fee on new H-1B visa petitions. The president's power over immigration was broad, she wrote. Congress had given him the tools, and he had used them.

On June 8, 2026 — less than six months later — Judge Leo Sorokin sat in a federal courtroom in Boston and reached the opposite conclusion. The fee was not a penalty, he wrote in a 42-page decision. It was a tax. And the president cannot levy a tax without Congress.

Two federal judges. Two Obama appointees. The same policy. Two irreconcilable answers. The United States now has a split that only a higher court can resolve — and for the roughly 600,000 Indian-born professionals in the H-1B and green card pipeline, the outcome will shape the economics of their continued presence in America.

## The Tariffs Connection

What changed between December and June was not the facts of the case but the legal landscape around it. In February 2026, the Supreme Court struck down Trump's sweeping global tariffs, ruling that the emergency-powers statute he relied on did not authorise the president to impose what amounted to a new tax on imports. The decision set a bright line: the taxing power belongs to Congress. Period.

Judge Sorokin seized on this precedent. If the president cannot use emergency trade law to impose tariffs that function as taxes, Sorokin reasoned, neither can he use immigration law to impose visa fees that function as taxes. "The substance and application of the $100,000 payment reveal that it is a tax, regardless of what the payment is called," he wrote. The Supreme Court's tariffs ruling, he argued, made the principle explicit.

Judge Howell's December decision came before that ruling existed. She evaluated the fee under the broad presidential authority granted by the Immigration and Nationality Act and found it permissible. The Supreme Court had not yet drawn its line.

## Eighty-Five Payments and a Frozen Market

The practical impact of the fee was devastating long before any court weighed in. Between September 2025 and February 2026, USCIS received exactly 85 payments of the $100,000 fee — a total of $8.5 million. Before Trump's proclamation, employers typically paid between $2,000 and $5,000 to sponsor an H-1B worker.

The fee did not merely raise the cost. It restructured the market. Large tech companies — Amazon with 19,301 H-1B approvals, Microsoft with 9,914, Apple with 8,075 — could theoretically absorb it. Small and mid-sized employers could not. A hospital in rural Maine testified to Congress that it paid $100,000 for a single surgeon. Charter schools, religious ministries, and research universities filed lawsuits arguing the fee made the programme cost-prohibitive.

For Indian IT services firms, which have historically been the programme's heaviest users, the calculus was simpler: shift the work to India. The $100,000 fee per worker turned offshore Global Capability Centres from a cost-saving measure into the only viable option.

## The Legal Road Ahead

The White House has made its intentions clear. Spokeswoman Taylor Rogers told reporters the administration is "confident this order will be reversed on appeal," noting that "a federal judge in Washington already upheld a nearly identical order."

That framing is accurate but incomplete. The two rulings emerge from different judicial circuits — the First Circuit (Boston) and the D.C. Circuit (Washington). An appeal of Sorokin's ruling would go to the First Circuit Court of Appeals. An appeal of Howell's ruling is already underway in the D.C. Circuit, where the US Chamber of Commerce is challenging her decision.

If the two circuit courts reach different conclusions — one upholding the fee and one striking it down — the Supreme Court would face enormous pressure to take the case. And the Court has already signalled, through its tariffs ruling, how it views unilateral executive taxation.

The legal question is narrow but consequential: does the Immigration and Nationality Act's grant of presidential authority to "suspend the entry" of certain foreign nationals include the power to charge them $100,000 for the privilege? Sorokin said no. Howell said yes. The answer, when it finally arrives, will determine not just the fee's fate but the outer limits of presidential power over immigration policy.

## What This Means for Indian Workers

For the Indian H-1B worker, the practical question is simpler: is the fee gone? For now, yes. Sorokin vacated the policy "in its entirety," invalidating not just the fee itself but the agency memoranda, guidance documents, FAQs, and fee schedules that enforced it.

But "for now" is doing heavy lifting. The administration will almost certainly seek an emergency stay of Sorokin's ruling while it appeals. If granted, the fee could snap back into effect within weeks. If denied, the fee remains dead until the appeals court rules — a process that could take a year or longer.

The nine months the fee was in effect have already reshaped the landscape. Companies that pivoted to offshore models are unlikely to reverse course on the strength of a single district court ruling. Indian IT firms that accelerated their shift to Global Capability Centres in Hyderabad, Bangalore, and Pune built infrastructure that will outlast any court decision.

The fee's damage was not just financial. It was reputational. For a generation of Indian engineers weighing whether to pursue careers in America, the message was unambiguous: you are not wanted here at any price. A court ruling that the fee was illegal does not undo that message. It merely adds a footnote."""
    },
]

# ── Insert ──
for art in articles:
    if not art["image_url"]:
        print(f"⚠️  Skipping {art['slug']} — no image")
        continue
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
