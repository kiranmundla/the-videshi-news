#!/usr/bin/env python3
"""Immigration writer for The Videshi — 2026-06-06 12:00 UTC run."""

import json, os, uuid, re, io, time, requests
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ── Load env ──────────────────────────────────────────────────────────────
for env_file in [Path.home() / "workspace" / ".env.supabase", Path.home() / "workspace" / ".env.pexels"]:
    if env_file.exists():
        for line in env_file.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

SB_URL  = os.environ["SUPABASE_URL"]
SB_KEY  = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey":        SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation",
}

UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

# ── Helpers ───────────────────────────────────────────────────────────────
def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def compress_image(img_bytes, max_width=1200, quality=80):
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
    print(f"  Downloading: {img_url[:80]}...")
    r = requests.get(img_url, headers=UA, timeout=30)
    r.raise_for_status()
    raw = r.content
    if len(raw) < 5000:
        raise ValueError(f"Image too small ({len(raw)} bytes)")
    compressed = compress_image(raw)
    print(f"  Compressed: {len(raw)} → {len(compressed)} bytes")

    upload_headers = {
        "apikey":        SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type":  "image/jpeg",
        "x-upsert":     "true",
    }
    up = requests.post(
        f"{SB_URL}/storage/v1/object/article-images/{filename}",
        headers=upload_headers,
        data=compressed,
        timeout=30,
    )
    up.raise_for_status()
    return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# ══════════════════════════════════════════════════════════════════════════
# ARTICLE 1 — Project Firewall Enforcement Spike
# ══════════════════════════════════════════════════════════════════════════

art1_slug = make_slug("project-firewall-ai-powered-h1b-dragnet-48-percent-increase")
art1_id   = str(uuid.uuid4())

# Image: Wikimedia Commons — Frances Perkins Building (DOL HQ)
art1_img_src = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/"
    "Frances_Perkins_Building_of_the_United_States_Department_of_Labor_"
    "in_Washington%2C_D.C._-_5.jpg/1200px-Frances_Perkins_Building_of_the_"
    "United_States_Department_of_Labor_in_Washington%2C_D.C._-_5.jpg"
)

print(f"\n🖼  Sourcing image for Article 1: {art1_slug}")
try:
    art1_img = upload_to_supabase(art1_img_src, f"{art1_id}.jpg")
    art1_img_attr = "Wikimedia Commons"
    art1_img_cap = "The Frances Perkins Building, headquarters of the U.S. Department of Labor in Washington, D.C."
    print(f"  ✅ Uploaded: {art1_img}")
except Exception as e:
    print(f"  ⚠ Image upload failed: {e}")
    art1_img = ""
    art1_img_attr = ""
    art1_img_cap = ""

art1_body = """The Labor Department is no longer waiting for complaints. It is hunting.

Since launching Project Firewall in September 2025, the department has seen a 48 percent increase in its caseload of H-1B investigations, according to a DOL official speaking to Bloomberg Law. Immigration attorneys say the shift is unmistakable: site visits are more frequent, information requests broader, and the government is now deploying artificial intelligence to catch employers in inconsistencies they might never have noticed themselves.

## From complaint box to dragnet

For most of the H-1B program's 36-year life, the DOL's enforcement mechanism was reactive. A worker filed a complaint. An investigator opened a case. The employer produced a file. The file was either in order or it wasn't.

Project Firewall changed that calculus entirely. Labor Secretary Lori Chavez-DeRemer now personally certifies investigations when "reasonable cause" exists — a standard the department has declined to define, giving investigators wide latitude to launch probes based on filings, referrals, or their own analysis.

The result is a compliance environment where employers cannot predict what triggers scrutiny. Attorney Nandini Nair, who represents clients in the IT consulting sector, told Bloomberg Law that some companies are now receiving site visits every time they file a new H-1B petition. Investigators start by asking about one employee, she said, then request immigration and payroll records for the entire workforce.

"The scope has increased tremendously," Nair said.

## The Palantir factor

What makes the new enforcement regime qualitatively different from any prior crackdown is technology. The Department of Homeland Security has contracted with Palantir Technologies to build AI-powered data analysis tools for immigration enforcement. That technology is now being shared across agencies.

USCIS quietly altered its Form I-129 this year to collect new data points from employers: education requirements, years of experience, technical skills, supervisory responsibilities. Immigration attorney Brian Coughlin of Fisher Phillips noted that these questions map directly to the criteria the DOL uses to calculate prevailing wages — data USCIS never collected before.

The implication is stark. Every answer an employer gives on a visa petition is now cross-referenced against its labor condition applications, prior filings, and real-time site visit data. Any mismatch — a job title described as "senior" on the I-129 but classified at a Level II wage on the LCA, for instance — can trigger a referral.

Coughlin called the development "potentially catastrophic" for employers. "What used to be a lot of disparate filings made for an individual over the course of years is now all going to be one cohesive narrative that needs to work together," he said.

## Who is in the crosshairs

Investigators are concentrating on two categories: H-1B-dependent employers (where a large share of the workforce holds H-1B status) and third-party placement firms that station workers at client sites. Both models are overwhelmingly associated with Indian IT services — the staffing architecture that companies like TCS, Infosys, and Cognizant built their American operations around.

The DOL is also proposing new prevailing wage levels that would push required H-1B salaries higher, adding another compliance layer. Jorge Lopez, chair of the Global Mobility & Immigration Practice Group at Littler Mendelson, warned that full enforcement actions may not begin in earnest until the second half of 2026. "A lot of this is just kicking off," he said.

## What this means for Indian H-1B workers

For the estimated 600,000-plus Indian nationals currently on H-1B status, the enforcement spike creates an indirect but real threat. Workers whose employers are investigated may face disruptions — delayed extensions, revoked petitions, or sudden job loss if an employer is debarred from the program.

The 60-day grace period after job loss is already one of the most precarious windows in American immigration law. An enforcement action that shutters an employer's H-1B program could push dozens of workers into that window simultaneously, with no guarantee of finding a new sponsor in time.

For workers at consulting and staffing firms — the category most heavily targeted — the practical advice from attorneys is blunt: ensure your job duties, work location, and compensation exactly match what your employer declared on your petition. If they don't, you may be the one who pays the price when an investigator shows up unannounced.

The era of the complaint-driven audit is over. The AI-powered dragnet has arrived."""

art1 = {
    "id":              art1_id,
    "headline":        "Forty-Eight Percent More Investigations — Project Firewall Is Using AI to Hunt H-1B Employers",
    "subheadline":     "The Labor Department's enforcement initiative has shifted from complaint-driven to AI-powered, with Palantir technology cross-referencing every filing employers have ever made.",
    "slug":            art1_slug,
    "category":        "immigration",
    "vertical":        "immigration",
    "diaspora_angle":  "Indian IT consulting and staffing firms — the backbone of H-1B sponsorship for Indian workers — are the primary enforcement targets. Workers at these firms face indirect but real risk of disruption if employers are investigated or debarred.",
    "tags":            ["h1b", "project-firewall", "dol", "enforcement", "palantir", "ai"],
    "urgency":         "high",
    "sources":         json.dumps([
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/financial-accounting/employers-see-spike-in-labor-department-immigration-enforcement"},
        {"name": "Mondaq (GDSC Law)", "url": "https://www.mondaq.com/unitedstates/work-visas/1531164/us-department-of-labor-launches-project-firewall"},
        {"name": "Boundless Immigration", "url": "https://www.boundless.com/immigration-resources/project-firewall-h1b-enforcement/"},
    ]),
    "score_total":     82,
    "status":          "published",
    "published_at":    now,
    "image_url":       art1_img,
    "image_caption":   art1_img_cap,
    "image_attribution": art1_img_attr,
    "is_editorial":    False,
    "body":            art1_body,
}

# ══════════════════════════════════════════════════════════════════════════
# ARTICLE 2 — Wage-Weighted H-1B Lottery: First Season Results
# ══════════════════════════════════════════════════════════════════════════

art2_slug = make_slug("wage-weighted-h1b-lottery-first-season-indian-workers-odds")
art2_id   = str(uuid.uuid4())

# Image: Pexels — passport with visa stamps
art2_img_src = "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&w=1200"

print(f"\n🖼  Sourcing image for Article 2: {art2_slug}")
try:
    art2_img = upload_to_supabase(art2_img_src, f"{art2_id}.jpg")
    art2_img_attr = "Pexels"
    art2_img_cap = "An open passport displaying travel and visa stamps at an immigration checkpoint"
    print(f"  ✅ Uploaded: {art2_img}")
except Exception as e:
    print(f"  ⚠ Image upload failed: {e}")
    art2_img = ""
    art2_img_attr = ""
    art2_img_cap = ""

art2_body = """The random H-1B lottery is dead. In its place, a system that gives the highest-paid applicants four times the odds of everyone else — and the first results are already reshaping how Indian professionals and their employers approach the program.

On February 27, 2026, the Department of Homeland Security's wage-weighted selection rule took effect, replacing the pure random draw that had governed H-1B cap allocation since 2020. The FY2027 cap season opened on March 4. By March 31 — just 25 days later — the cap was hit, confirming that demand remains ferocious even in the most hostile policy environment the program has ever faced.

## How the math actually works

Under the old system, every H-1B registration got one ticket in the lottery. An entry-level software developer offered $70,000 had the same odds as a principal engineer offered $250,000. With roughly 470,000 registrations competing for 85,000 cap numbers in recent years, selection rates hovered around 29 to 30 percent regardless of salary or seniority.

The new system assigns multiple tickets based on the DOL's four-tier Occupational Employment and Wage Statistics (OEWS) framework:

- **Wage Level IV** (highly experienced): 4 entries
- **Wage Level III** (qualified): 3 entries
- **Wage Level II** (some experience): 2 entries
- **Wage Level I** (entry-level): 1 entry

This creates a probability cliff. A Level IV registration effectively competes as though four separate applications were filed. A Level I registration has one-quarter the relative odds. The system does not guarantee selection at any level — it is still a lottery — but the deck is now stacked in a way that fundamentally alters strategy.

## The Indian worker's dilemma

Indian nationals make up roughly 72 percent of all H-1B beneficiaries, and a disproportionate share of them enter the system at Wage Levels I and II. This is not because Indian workers are less skilled — it is because the staffing and consulting model that dominates Indian IT sponsorship tends to classify positions at lower wage levels, partly to manage costs and partly because workers are placed in geographic regions with lower prevailing wages.

Under the new system, those placements carry a selection penalty. An Indian IT consultant classified at Level I in a Midwest market now has roughly one-quarter the selection probability of a Level IV machine learning engineer at a Bay Area tech firm.

The $100,000 fee on new consular H-1B petitions compounds the problem. Workers already in the U.S. in valid nonimmigrant status are exempt from the fee, creating a two-tier system where the cheapest path to an H-1B is also the one with the best lottery odds — and that path runs through American universities, not Indian staffing firms.

## What employers are doing differently

Immigration attorneys report that employers began overhauling their H-1B registration strategies months before the cap season opened. The key changes are structural:

First, employers must now perform detailed wage and occupational analysis before registration, not after selection. Under the old random system, registration was largely procedural. Now, the SOC code, work location, and corresponding OEWS wage level directly determine selection weight. Getting the classification wrong does not just risk a petition denial — it reduces the odds of being selected in the first place.

Second, employers sponsoring workers at multiple locations face a punitive rule: if the same beneficiary is registered by multiple employers at different wage levels, USCIS uses the lowest level for weighting. This closes a potential gaming strategy and creates an incentive to consolidate around the highest-paying offer.

Third, the prevailing wage must be defensible through petition. USCIS has altered the I-129 form to collect education, experience, and skills data that maps to DOL wage calculations. Any inconsistency between the wage level claimed at registration and the duties described in the petition will be flagged — automatically, via the new AI-powered cross-referencing systems the government has deployed.

## The early signals

USCIS has not yet published detailed FY2027 selection statistics by wage level, but the speed at which the cap was reached — 25 days — suggests that employers front-loaded their registrations. Immigration law firms report that their clients overwhelmingly shifted registrations toward Level III and IV positions, either by restructuring job descriptions or by prioritizing sponsorship of more senior candidates.

For Indian professionals early in their careers — recent graduates on OPT, junior engineers, entry-level analysts — the message is clear. The lottery that was already difficult at 30 percent odds is now significantly harder at Level I, and the alternative pathways (EB-1A, NIW, O-1) each carry their own escalating uncertainty.

The wage-weighted lottery was designed to "generally favor the allocation of H-1B visas to higher-skilled and higher-paid" workers, as DHS stated in its final rule. Whether it achieves that goal or simply prices out an entire generation of early-career Indian talent is the question the first full season of data will eventually answer."""

art2 = {
    "id":              art2_id,
    "headline":        "Four Times the Odds or One-Quarter the Chance — The Wage-Weighted H-1B Lottery Just Ran Its First Season",
    "subheadline":     "The new system gives Level IV applicants four lottery entries for every one that an entry-level worker gets. For Indian IT consulting, the math is brutal.",
    "slug":            art2_slug,
    "category":        "immigration",
    "vertical":        "immigration",
    "diaspora_angle":  "Indian IT consulting's staffing model classifies workers at lower wage levels, which now carry a direct selection penalty under the weighted lottery. Early-career Indian professionals face dramatically reduced odds.",
    "tags":            ["h1b", "lottery", "wage-weighted", "uscis", "indian-it", "fy2027"],
    "urgency":         "high",
    "sources":         json.dumps([
        {"name": "Dworsky Law", "url": "https://dworskylaw.com/the-new-h-1b-lottery-how-the-wage-weighted-system-changes-your-chances-for-fy-2027/"},
        {"name": "Nixon Peabody LLP", "url": "https://www.nixonpeabody.com/insights/alerts/2025/12/30/h-1b-weighted-selection-process-announced-for-fiscal-year-2027"},
        {"name": "Brookings Institution", "url": "https://www.brookings.edu/articles/how-the-trump-administration-is-eroding-the-immigrant-talent-pipeline/"},
    ]),
    "score_total":     80,
    "status":          "published",
    "published_at":    now,
    "image_url":       art2_img,
    "image_caption":   art2_img_cap,
    "image_attribution": art2_img_attr,
    "is_editorial":    False,
    "body":            art2_body,
}

# ── Publish ───────────────────────────────────────────────────────────────
articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"\n✅ Published: {art['slug']}")
        print(f"   Headline: {art['headline']}")
    except Exception as e:
        print(f"\n❌ Failed: {art['slug']}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text[:300]}")

print("\n🏁 Immigration writer complete.")
