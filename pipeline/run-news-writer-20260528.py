#!/usr/bin/env python3
"""The Videshi — News Writer (2026-05-28 batch)
Three articles on fresh, uncovered stories with strong India/diaspora angles.
"""

import json, os, re, sys, time, uuid, urllib.parse
import requests

# ── env ──────────────────────────────────────────────────────────────────
with open(os.path.expanduser("~/.env.supabase")) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

with open(os.path.expanduser("~/workspace/.env.pexels")) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ["PEXELS_API_KEY"]

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── image helpers ────────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Search Pexels for a relevant image. Returns URL or None."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                headers={"Authorization": PEXELS_KEY},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                for p in photos:
                    url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                    if url:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Verify URL returns a real image > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        # Some servers don't return Content-Length on HEAD, try GET with range
        if "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def sb_insert(table, payload):
    """Insert into Supabase and return the record."""
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=payload,
    )
    if r.status_code in (200, 201):
        data = r.json()
        return data[0] if isinstance(data, list) else data
    print(f"  ✗ Insert error ({r.status_code}): {r.text[:600]}")
    return None


def sb_patch(table, filters, payload):
    """Patch a Supabase row."""
    params = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(
        f"{SB_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=payload,
    )
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch error ({r.status_code}): {r.text[:300]}")
    return False


# ── Articles ─────────────────────────────────────────────────────────────
articles = [
    # ── ARTICLE 1: India Rice Exports ──
    {
        "headline": "India's Basmati Exports to the Gulf Dropped 7 Percent. The Iran War Made the World's Biggest Rice Exporter a Bystander.",
        "subheadline": "Cargoes bound for Iran, Iraq, Qatar and Saudi Arabia sit in limbo as freight costs soar and buyers hold back on new deals. Non-basmati shipments to Africa are slipping too.",
        "slug": "india-basmati-rice-exports-gulf-drop-7-percent-iran-war-shipping-20260528",
        "category": "news",
        "body": """India's rice exports in the first four months of 2026 fell 1.3 percent from a year ago, according to two government officials who spoke to Reuters on condition of anonymity. The headline number barely registers. The story underneath it does.

## The Gulf Pipeline Is Broken

Basmati rice — the fragrant, long-grain variety that India dominates globally — saw exports fall 7 percent to 2.3 million metric tons between January and April. The damage is concentrated in the Gulf, where India's most lucrative buyers sit: Iran, Iraq, Qatar and Saudi Arabia.

Cargoes bound for those markets remain delayed in transit. Neither buyers nor exporters are signing new deals. A New Delhi-based exporter told Reuters that shipments would stay below typical levels until the Iran war ends — a timeline that, as of this week's fresh air strikes near the Strait of Hormuz, remains entirely uncertain.

India accounts for more than 40 percent of global rice exports, shipping more than Thailand, Vietnam and Pakistan combined. When India's rice trade seizes up, the effects cascade across continents.

## How the War Changed the Math

The U.S.-Israeli airstrikes that began the war on Iran at the end of February disrupted maritime traffic through the Strait of Hormuz — the narrow chokepoint through which roughly a fifth of the world's oil and a significant share of South Asian food exports pass.

Shipping insurance premiums spiked. Freight costs followed. The result: Indian exporters found it increasingly expensive to send rice to the Gulf, and Gulf buyers found it increasingly risky to place orders.

Iran was India's largest basmati market until last year, when Saudi Arabia overtook it. Both remain critical. Together with Iraq and the UAE, they absorb the vast majority of India's premium rice output.

## Africa Feels It Too

Non-basmati rice exports — the cheaper varieties that go to Bangladesh, Benin, Ivory Coast, Guinea and Cameroon — edged up marginally to 6.09 million tons from 6.03 million. But an exporter in Kakinada, southeastern India, told Reuters that rising freight and insurance costs were already weighing on demand from African buyers.

India competes with Thailand, Vietnam, Myanmar and Pakistan in these markets. Any sustained cost disadvantage pushes buyers toward alternatives.

## What This Means for the Diaspora

For NRIs across the Gulf — and there are an estimated 9 million Indians living in GCC countries — the disruption is not abstract. Basmati rice is a staple, a cultural anchor, and a grocery-line item that has gotten measurably harder to source and more expensive to buy.

Indian grocery stores in Dubai, Doha and Riyadh have already reported intermittent shortages of specific basmati brands. Prices have risen even as Indian domestic prices fell more than 5 percent this year following a record harvest — a painful paradox where surplus at home cannot reach demand abroad.

## The Bigger Picture

India's rice export infrastructure was not built for war. The Strait of Hormuz was supposed to be a shipping lane, not a frontline. The current disruption exposes how dependent India's agricultural export economy is on a single maritime corridor — and how quickly geopolitics can sever the link between an Indian paddy field and a Gulf kitchen.

The government has not announced any specific relief measures for affected exporters. For now, the rice sits — in warehouses, on ships, and in a strategic limbo that neither Delhi nor the market can resolve without a ceasefire that keeps slipping further away.

*Sources: Reuters, The Hindu Business Line, India Shipping News*""",
        "sources": "Reuters, The Hindu Business Line, India Shipping News",
        "image_search": ("basmati rice sacks export", "rice grain harvest India"),
        "person_image": None,
    },

    # ── ARTICLE 2: Taiwan Nuclear Escalation / Shangri-La ──
    {
        "headline": "A War Over Taiwan Would Go Nuclear. That Warning Just Landed as Asia's Biggest Defense Summit Opens.",
        "subheadline": "A 156-page IISS assessment says U.S. and Chinese forces lack the guard rails to prevent nuclear escalation in a Taiwan conflict. The finding drops two days after India hosted the Quad in New Delhi.",
        "slug": "iiss-taiwan-nuclear-war-risk-shangri-la-dialogue-india-quad-20260528",
        "category": "news",
        "body": """A conflict between the United States and China over Taiwan would risk escalating to a nuclear exchange, with both militaries likely to launch sweeping operations targeting each other's command and communications infrastructure. That is the central finding of a strategic assessment released Thursday by the International Institute for Strategic Studies, timed to land hours before Asia's biggest annual defense summit opens in Singapore.

## The IISS Assessment

The 156-page document, published ahead of the Shangri-La Dialogue running May 29 to 31, warns that the world is on the cusp of a new nuclear arms race "with the Asia-Pacific at its core."

The assessment is blunt about the absence of safeguards. "There is currently little public evidence to suggest that both militaries understand the necessary guard rails to prevent, or rules of engagement that would restrict, both sides potentially targeting each other's key command, control, communications, computers, intelligence, surveillance and reconnaissance nodes," the report states.

Translation: in a real shooting war over Taiwan, neither Washington nor Beijing has a reliable way to stop things from going nuclear.

China has never ruled out the use of force to take control of Taiwan. Its government says it prefers "peaceful reunification." Taiwan's government rejects Beijing's sovereignty claims entirely.

## The Nuclear Math

The raw numbers still favor the United States and Russia. The Federation of American Scientists estimates that Russia fields roughly 4,400 active warheads, the U.S. about 3,700, and China approximately 620. But a December Pentagon report concluded that China is on track to field 1,000 warheads by 2030 — and that it is expanding and improving its nuclear capabilities faster than any other power.

The IISS report notes that this is no longer just about the two superpowers. Regional states across the Asia-Pacific are expanding their own nuclear arsenals, while non-nuclear states are pursuing long-range conventional-strike capabilities that blur the line between conventional and strategic deterrence.

## Why This Matters for India

India sits at the intersection of nearly every tension line in this assessment.

Two days before the IISS published its warning, New Delhi hosted the 11th Quad Foreign Ministers' Meeting. External Affairs Minister S. Jaishankar welcomed U.S. Secretary of State Marco Rubio, Australia's Penny Wong and Japan's Toshimitsu Motegi for what became the Quad's most operationally concrete session yet.

The group unveiled its first joint infrastructure project — a port in Fiji — and launched the Indo-Pacific Maritime Surveillance Collaboration, a shared surveillance framework covering strategic shipping lanes. A Quad Critical Minerals Initiative was formalized. More than $25 million was committed to undersea cable projects.

None of this is accidental. The Quad exists, in large part, because of exactly the scenario the IISS just war-gamed: a China that is militarily assertive, nuclear-capable, and increasingly willing to challenge the status quo around Taiwan and in the South China Sea.

## The Shangri-La Context

U.S. Defense Secretary Pete Hegseth will speak at the Singapore conference on Saturday. China has sent a delegation from the PLA National Defence University, headed by Meng Xiangqing — but for the second consecutive year, Defense Minister Dong Jun will not attend.

The event follows a summit between Xi Jinping and Donald Trump in Beijing earlier this month that left Taipei visibly nervous about the durability of U.S. commitments to Taiwan's defense.

India, which has steadily deepened its defense ties with both the U.S. and Japan while managing a complex relationship with Beijing, will be watching closely. The IISS assessment validates what Indian strategic planners have argued for years: that the Indo-Pacific is not a peripheral theater but the central one — and that India's choices in this space carry nuclear-age consequences.

## What Comes Next

The Shangri-La Dialogue has historically been the venue where Asian security anxieties get aired publicly. This year's edition arrives with the Iran war still burning, a Taiwan flashpoint the IISS now frames in explicitly nuclear terms, and an India that just demonstrated — through the Quad meeting — that it intends to be at the table, not watching from the sidelines.

The 156 pages are a warning. Whether anyone at the conference acts on it is another question entirely.

*Sources: Reuters, IISS Strategic Assessment 2026, U.S. State Department, Australian Foreign Ministry*""",
        "sources": "Reuters, IISS Strategic Assessment 2026, U.S. State Department, Australian Foreign Ministry",
        "image_search": ("Shangri-La Dialogue Singapore defense summit", "Asia Pacific military naval ships"),
        "person_image": None,
    },

    # ── ARTICLE 3: USCIS Green Card Clarification for H-1B ──
    {
        "headline": "USCIS Says H-1B Workers Can Stay in the US for Green Cards. The Fine Print Is Doing a Lot of Heavy Lifting.",
        "subheadline": "After weeks of panic over a return-home mandate, the agency now says workers who provide 'economic benefit' can remain. It has not defined what that means. Indian professionals — 71 percent of all H-1B holders — are the most exposed.",
        "slug": "uscis-h1b-green-card-stay-us-clarification-fine-print-indian-workers-20260528",
        "category": "news",
        "body": """On May 22, USCIS dropped a policy bomb: foreign nationals in the United States on temporary visas who want a green card must return to their home country to apply, except in "extraordinary circumstances." Six days later, on May 26, the same agency walked it back — partially, ambiguously, and with enough caveats to keep immigration lawyers billing through the summer.

## What USCIS Actually Said

Spokesperson Zach Kahler's updated statement introduced three conditions under which H-1B holders might avoid the return-home requirement:

**Economic benefit.** If your role contributes positively to the U.S. economy, you can likely stay.

**National interest.** If your position serves the broader national interest, same deal.

**Individualized circumstances.** Everyone else gets a case-by-case review, with no publicly available criteria for how those cases will be decided.

The problem, which immigration attorneys spotted immediately, is that none of these terms have been formally defined. "Economic benefit" could mean a software engineer at Google or it could mean anyone with a job. "National interest" could mean a defense contractor or it could mean a nurse in a shortage area. USCIS has not said.

## The Numbers That Matter

Indian nationals account for approximately 71 percent of all approved H-1B petitions. That is not a rounding error — it is the structural reality of America's skilled-immigration pipeline. When USCIS changes H-1B rules, it is changing rules that disproportionately affect Indians, regardless of whether the policy is "targeted."

The broader context makes the clarification feel even more precarious. H-1B registrations dropped 38.5 percent in fiscal year 2027, from 343,981 to 211,600. USCIS itself attributes this to stricter selection filters favoring advanced degrees and higher salaries. India's six largest IT firms — TCS, Cognizant, Infosys, HCL, Wipro and Tech Mahindra — received a combined 11,041 H-1B visas as of March 2026, down 40 percent from the prior year.

A proposed Department of Labor rule would raise minimum prevailing wages for H-1B workers by up to 33 percent for entry-level positions — from $73,279 to $97,746. The comment period closed May 26, the same day USCIS issued its green card clarification.

## What Rubio Said — and What the Data Says

When Secretary of State Marco Rubio visited New Delhi last week, he insisted the visa overhaul is a global modernization effort, not an India-specific measure. "The changes that are happening now are not India-specific; it is global, it's being applied across the world," Rubio told reporters alongside External Affairs Minister Jaishankar.

The statistics tell a different story. When 71 percent of affected visa holders come from one country, a "global" policy has a very specific address. Indian IT companies absorbed the steepest declines. TCS alone lost 3,242 approvals year-over-year. The only major Indian firm to gain was Infosys, with 3,195 approvals.

## The Return-Home Nightmare Scenario

For Indian H-1B holders, the original May 22 policy was not just an inconvenience — it was an existential threat. India and China face green card backlogs spanning multiple decades. An Indian national in the EB-2 category who is told to return home to apply is not going home for a few weeks. They may be going home for years.

The EB-2 India category is already frozen for fiscal year 2026, with final approvals paused until October. The backlog means that even with priority dates, the wait can stretch to 10 to 15 years.

The May 26 clarification softens the worst fears, but does not resolve them. An H-1B holder who loses their job still faces a 60-day window to find new sponsorship or leave the country. The "economic benefit" exception does not appear to cover the unemployed.

## The Sridhar Vembu Question

Zoho CEO Sridhar Vembu added fuel to the debate by publicly urging Indian professionals in the U.S. to consider returning home. "Please come home… self-respect should dictate your course," he wrote. The response was polarized — some applauded the sentiment, others pointed out that uprooting a career, a family, children's education, and a decade of investment is not a question of self-respect but of structural reality.

## Where This Leaves Things

The USCIS clarification is a band-aid on a policy wound that is still bleeding. Indian professionals — the single largest group in the H-1B ecosystem — have been told they can probably stay, under conditions that have not been specified, subject to reviews that have no published criteria, in a regulatory environment that changed twice in four days.

For the estimated 300,000-plus Indian H-1B holders in the United States, the message is clear: plan for uncertainty, document everything, and do not assume that today's clarification will be tomorrow's policy.

*Sources: USCIS, LiveMint, Global Net News, Reuters*""",
        "sources": "USCIS, LiveMint, Global Net News, Reuters",
        "image_search": ("US visa passport immigration", "H-1B visa United States"),
        "person_image": None,
    },
]

# ── Publish loop ─────────────────────────────────────────────────────────
published = 0
for i, art in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"Article {i}: {art['headline'][:70]}...")

    # Image sourcing
    img_url = None

    # Try person image first
    if art.get("person_image"):
        img_url = fetch_wikipedia_person_image(art["person_image"])

    # Pexels fallback
    if not img_url and art.get("image_search"):
        q1, q2 = art["image_search"]
        img_url = fetch_pexels_image(q1, q2)

    # Validate
    if img_url and not validate_image(img_url):
        print(f"  ⚠ Image failed validation, dropping: {img_url[:80]}")
        img_url = None

    if img_url:
        print(f"  ✓ Final image: {img_url[:80]}...")
    else:
        print(f"  ⚠ No image — publishing without image (no image > wrong image)")

    # Build payload
    payload = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": art["category"],
        "body": art["body"].strip(),
        "sources": art["sources"],
        "status": "published",
        "published_at": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
    }
    if img_url:
        payload["image_url"] = img_url
        if "upload.wikimedia.org" in img_url:
            payload["image_attribution"] = "Wikimedia Commons"
        elif "pexels.com" in img_url:
            payload["image_attribution"] = "Pexels"

    result = sb_insert("p2_articles", payload)
    if result:
        aid = result.get("id", "?")
        print(f"  ✓ Published: id={aid}, slug={art['slug']}")
        published += 1
    else:
        print(f"  ✗ FAILED to publish article {i}")

    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
