#!/usr/bin/env python3
"""Videshi Lifestyle + Markets Writer — 2026-05-26 23:11 PDT run
2 articles:
  1. [markets-finance] RBI's NRI Dollar Play: FCNR deposits, NRI bonds,
     $5B swap auction (conducted May 26), reviving the 2013 playbook.
     The rupee hit 96.96 record low, RBI spending $1B/day.
     NRI angle: You are about to be directly solicited to park your
     dollars in India. Here's what FCNR-B deposits mean, the 2013
     precedent, the remittance windfall, and the property arbitrage.

  2. [lifestyle-health] Finasteride (Propecia) persistent side effects:
     MHRA 2026 strengthened warnings, case study of 26-year-old with
     18-month persistent sexual dysfunction. Indian men have among the
     highest rates of male pattern baldness globally, hair transplant
     tourism is massive, and finasteride is prescribed casually.
     NRI angle: The drug your dermatologist prescribed for hair loss
     in your 20s may have lasting side effects. UK regulator just
     strengthened warnings. What Indian American men need to know.
"""

import os, json, uuid, re, requests, time, subprocess
from datetime import datetime, timezone
from pathlib import Path

# ── Load env ──
for line in (Path.home() / ".env.supabase").read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()

# ── Pexels env ──
pexels_path = Path.home() / "workspace/.env.pexels"
PEXELS_KEY = None
if pexels_path.exists():
    for line in pexels_path.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if "PEXELS" in k.upper():
                PEXELS_KEY = v.strip()

# ── Supabase config ──
SB_URL = os.environ["SUPABASE_URL"].rstrip("/")
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def make_slug(text, suffix="20260527"):
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
    if not r.ok:
        print(f"  ✗ Error {r.status_code}: {r.text[:300]}")
        r.raise_for_status()
    return r.json()

def sb_patch(table, filters, data):
    qs = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(
        f"{SB_URL}/rest/v1/{table}?{qs}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json=data, timeout=15
    )
    r.raise_for_status()
    return r

def fetch_pexels_image(query, fallback_query=None):
    """Fetch a landscape image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-s", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            if data.get("photos"):
                photo = data["photos"][0]
                return {
                    "url": photo["src"]["large2x"],
                    "photographer": photo["photographer"],
                    "pexels_id": photo["id"],
                    "alt": q,
                }
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    """Download image from URL and upload to Supabase Storage bucket 'article-images'."""
    try:
        img_resp = requests.get(image_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if img_resp.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {img_resp.status_code}")
            return None
        img_bytes = img_resp.content
        content_type = img_resp.headers.get("Content-Type", "image/jpeg")
        if "svg" in content_type:
            print(f"  ⚠ Skipping SVG image")
            return None
        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        up_resp = requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{filename}",
            headers=upload_headers, data=img_bytes, timeout=30
        )
        if up_resp.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Image uploaded: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {up_resp.status_code} {up_resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Image upload error: {e}")
        return None


# ── Cross-check recent articles to avoid duplication ──
print("=== Cross-checking recent articles ===")
for cat in ["markets-finance", "lifestyle-health"]:
    recent_resp = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?category=eq.{cat}&status=eq.published&order=published_at.desc&limit=15&select=headline,slug",
        headers=HEADERS, timeout=15
    )
    if recent_resp.ok:
        recent = recent_resp.json()
        print(f"\n  Recent {cat} ({len(recent)}):")
        for art in recent[:8]:
            print(f"  - {art.get('slug','?')[:70]}")


# ── Score decay for older articles ──
print("\n=== Score decay ===")
for cat in ["lifestyle-health", "markets-finance"]:
    decay_resp = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?category=eq.{cat}&status=eq.published&score_total=gt.10&order=published_at.desc&limit=30&select=id,score_total,published_at",
        headers=HEADERS, timeout=15
    )
    if decay_resp.ok:
        now_utc = datetime.now(timezone.utc)
        decayed = 0
        for art in decay_resp.json():
            pub = art.get("published_at")
            if not pub:
                continue
            pub_dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
            age_hours = (now_utc - pub_dt).total_seconds() / 3600
            if age_hours > 24 and art["score_total"] > 10:
                new_score = max(10, int(art["score_total"] * 0.92))
                if new_score != art["score_total"]:
                    requests.patch(
                        f"{SB_URL}/rest/v1/p2_articles?id=eq.{art['id']}",
                        headers={**HEADERS, "Prefer": "return=minimal"},
                        json={"score_total": new_score},
                        timeout=10
                    )
                    decayed += 1
        print(f"  [{cat}] Decayed {decayed} articles (8% reduction, >24h old, score>10)")


now = datetime.now(timezone.utc).isoformat()


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: [markets-finance] India Wants Your Dollars Back
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "India Wants Your Dollars. The RBI Is Dusting Off the 2013 Playbook — NRI Bonds, FCNR Deposits, Emergency Swaps — to Stop the Rupee From Hitting 100. If You Have a Dollar Account, You Are About to Be Courted."
art1_subheadline = "The Reserve Bank of India conducted a $5 billion dollar-rupee swap auction on May 26, 2026 — the same day the rupee was trading near its record low of 96.96 per dollar. But the swap is only one weapon in an escalating arsenal. Sources familiar with the central bank's thinking told multiple outlets that the RBI is actively evaluating the launch of Foreign Currency Non-Resident (FCNR) deposit schemes, the issuance of NRI bonds, and additional swap operations to mobilise dollar inflows from the Indian diaspora. The last time India took these steps was during the 2013 taper tantrum crisis, when the rupee fell to 68.85 against the dollar and the RBI raised $34 billion from NRIs in three months through FCNR-B deposits offered at subsidised rates. That 2013 operation is widely credited with stabilising the currency and averting a balance-of-payments crisis. India's current predicament is arguably worse: the Iran war has pushed Brent crude above $100 per barrel, foreign portfolio investors have sold $23 billion of Indian equities in 2026, the rupee has fallen 6 percent since January, the RBI is spending an estimated $1 billion per day in the spot market to prevent further collapse, and fuel prices have been hiked four times in May alone — a cumulative increase of ₹7.5 per litre. For the estimated 32 million members of the Indian diaspora — particularly the 4.5 million Indian Americans who hold dollar-denominated savings, earn dollar salaries, and send an estimated $30 billion in remittances to India each year — the coming weeks may present a once-in-a-decade financial decision. The RBI is about to ask you for your dollars. Understanding what FCNR deposits are, how the 2013 scheme worked, what the current remittance and property arbitrage looks like, and whether parking your dollars in India makes financial sense requires more than a headline. It requires context."
art1_slug = "rbi-nri-bonds-fcnr-deposits-2013-playbook-rupee-dollar-crisis-20260527"
art1_category = "markets-finance"

art1_body = """The Reserve Bank of India is running out of conventional weapons to defend the rupee. So it is reaching for the unconventional ones — and the next target audience is you.

On May 26, 2026, the RBI conducted a $5 billion USD/INR buy-sell swap auction with a three-year tenor. Banks sold dollars to the RBI and agreed to buy them back in 2029. The mechanism injects rupee liquidity into the banking system while allowing the RBI to shore up its foreign exchange reserves, which have been depleted by months of aggressive dollar sales in the spot market.

But the swap is a structural plumbing tool — not a rescue. The real rescue, if it comes, will look a lot like September 2013. And it will be addressed directly to the Indian diaspora.

## What the RBI Is Considering

According to sources cited by Bloomberg and multiple Indian financial outlets, the Reserve Bank is evaluating three NRI-focused measures:

**1. FCNR-B Deposits at Subsidised Rates.** Foreign Currency Non-Resident (Banks) deposits — or FCNR-B — allow NRIs to park foreign currency (dollars, euros, pounds, yen, Canadian or Australian dollars) in Indian banks for 1 to 5 years. The deposits are denominated in foreign currency and repaid in the same currency, so the depositor bears zero exchange-rate risk. Under normal conditions, the interest rates on FCNR-B deposits are modest — typically 1 to 3 percent for dollar deposits, set by individual banks within RBI guidelines. But in 2013, the RBI allowed banks to offer rates **above** the LIBOR/SOFR benchmark, and separately promised to provide subsidised dollar-rupee swaps to banks to cover their foreign-exchange exposure. The result: banks could offer NRIs rates as high as 5.5 percent on 3-year dollar deposits — significantly above what US banks were paying on CDs at the time.

**2. NRI Bonds.** A sovereign or quasi-sovereign bond denominated in dollars, issued specifically to the Indian diaspora. India has done this before — the Resurgent India Bonds in 1998 and the India Millennium Deposits in 2000. These instruments raised $4.2 billion and $5.5 billion respectively. An NRI bond in 2026 would likely offer a coupon above US Treasury yields, with the implicit backing of the Indian government. For NRIs with significant dollar savings who are already sending money to India, this would be a formalised, higher-yielding alternative.

**3. Additional Buy-Sell Swaps.** Beyond the $5 billion auction already conducted, the RBI may schedule additional swaps to keep rupee liquidity flowing even as it sells dollars in the spot market. The May 26 swap is seen as a rollover of earlier swap positions, but analysts at DBS and IFA Global believe additional swaps are likely in June if the rupee remains under pressure.

No final decision has been taken on any of these measures. But the mere fact that they are under evaluation — and that the information has been deliberately leaked to financial media — is itself a signal. The RBI wants the market to know that NRI dollar mobilisation is on the table.

## The 2013 Precedent

The closest parallel to India's current situation is the "taper tantrum" of 2013, when the US Federal Reserve signalled that it would reduce its bond-buying programme. Capital flooded out of emerging markets. The rupee fell from 54 to nearly 69 per dollar between May and August 2013.

On September 4, 2013, RBI Governor Raghuram Rajan — who had taken charge just three days earlier — announced a special FCNR-B deposit window. Banks were permitted to accept deposits at rates up to 400 basis points above LIBOR for 3-year tenors, and the RBI offered a separate concessional swap window to hedge the banks' dollar-rupee exposure. The combination meant that NRIs could earn 5 to 5.5 percent on dollar deposits with zero exchange-rate risk, while Indian banks got cheap dollar funding and the RBI replenished its reserves.

In three months, Indian banks raised approximately **$34 billion** through the FCNR-B window. The rupee stabilised and eventually recovered to below 62 per dollar by the time the deposits started maturing in 2016.

The 2013 FCNR-B operation is studied in central banking textbooks as one of the most successful currency defence mechanisms ever deployed by an emerging market. The reason it worked was simple: there were enough NRI dollars available, the rates were attractive enough to make the transfer worthwhile, and the zero-exchange-rate-risk structure removed the single biggest objection NRIs had about parking money in India.

## What Is Different in 2026

Several factors make the current crisis more complex than 2013.

**Oil is the driver, not capital flows.** In 2013, the rupee fell because foreign investors pulled money out of Indian bonds and stocks. That problem was solvable — once sentiment turned, the money came back. In 2026, the rupee is falling because India's oil import bill has structurally increased. Brent crude is above $100 per barrel. India imports over 85 percent of its oil. The Iran war has disrupted shipping through the Strait of Hormuz, forcing Indian refiners to source crude from Latin America and Africa at higher costs and longer lead times. Even if FCNR deposits raise $30 billion, the oil import bill will continue to drain dollars every month. The deposits buy time; they do not fix the underlying problem.

**Interest rates are higher globally.** In 2013, US interest rates were near zero. A 5 percent FCNR-B rate was enormously attractive. In May 2026, the US 10-year Treasury yields approximately 4.8 percent, and high-yield savings accounts in the US offer 4.5 to 5 percent. The RBI would need to offer FCNR-B rates significantly above 5 percent — perhaps 6 to 7 percent — to make the proposition attractive enough to move large sums. That increases the cost to Indian banks and, ultimately, to the RBI.

**The rupee's decline is steeper.** The rupee fell 28 percent in 2013 (from 54 to 69). In 2026, the rupee has fallen from roughly 88 in January to 97 in May — about 10 percent. But the speed of the decline, combined with the oil-driven structural deficit, has spooked markets more than the absolute numbers suggest. DBS has revised its rupee forecast range to 95–100 for the remainder of 2026. Analysts at multiple banks have not ruled out 100.

**NRI remittances are already at record highs.** India received approximately $125 billion in remittances in 2025, the highest of any country in the world. A significant portion of that comes from the US, UAE, UK, Canada, and Australia. The remittance channel is already flowing. The question is whether an FCNR-B scheme can redirect some of those flows from current-account remittances (money sent for family expenses, property EMIs, medical bills) into term deposits that the RBI can count on for 3 to 5 years.

## What the Weak Rupee Means for You Right Now

If you are an Indian American earning in dollars and spending in both dollars and rupees, the rupee's fall has created asymmetric effects across different financial decisions.

**Remittances.** Every dollar you send to India today buys approximately ₹96–97 — roughly 10 percent more than it did in January. If you regularly send money for parents' expenses, household staff salaries, EMIs, or SIP contributions, the weak rupee is effectively a 10 percent raise for your Indian-side obligations. This is the most immediate and tangible benefit.

**Property purchases.** Indian real estate priced in rupees has become cheaper in dollar terms. A flat that costs ₹1 crore is approximately $103,000 at today's rate, compared to $113,600 at the January rate of 88. That is a $10,600 discount from currency movement alone — before any negotiation on the property price. For NRIs considering property purchases in India, the current exchange rate represents one of the most favourable windows in recent memory. But the risk is that the rupee may weaken further, which would make a purchase now look less optimal in hindsight. Nobody can time currencies.

**Indian stock investments.** The Nifty 50 has fallen approximately 6 percent since the Iran war began. Combined with the 10 percent rupee depreciation, Indian equities are roughly 15 percent cheaper in dollar terms than they were in January. Foreign portfolio investors have been selling; they have pulled $23 billion from Indian markets in 2026. History suggests that FPI selling in India is often a contrarian buying signal for long-term investors. But the oil shock and its inflationary consequences add genuine fundamental risk that did not exist in prior selloffs.

**NRE and NRO deposits.** Non-Resident External (NRE) accounts offer rupee-denominated deposits where the principal and interest are freely repatriable. Current NRE fixed deposit rates range from 6.5 to 7.5 percent for 1-year tenors, depending on the bank. The catch: if you deposit dollars into an NRE account at ₹97 per dollar and the rupee strengthens back to ₹90 by the time the deposit matures, you lose approximately 7 percent on currency conversion when you repatriate — more than offsetting the interest earned. This is the exchange-rate risk that FCNR-B deposits are designed to eliminate.

## The Decision Framework

If the RBI does launch a subsidised FCNR-B window — and the signals suggest it will — here is how to evaluate it:

**Attractive if:** The FCNR-B rate is at least 150 basis points above what your US savings account or CD is paying. If US CDs offer 4.5 percent and the FCNR-B offers 6 percent or above for a 3-year term, the additional yield is meaningful on large sums. The zero exchange-rate risk means your $100,000 deposit is returned as $100,000 plus interest, regardless of where the rupee trades in 3 years.

**Less attractive if:** You need the money within 3 years (premature withdrawal penalties apply and may forfeit the rate premium), you are uncomfortable with Indian bank credit risk (FCNR-B deposits are held by scheduled commercial banks, not the RBI itself; though the largest banks — SBI, HDFC, ICICI — carry implicit sovereign backing), or you believe US rates will rise further and lock-in now means missing higher yields later.

**Not relevant if:** You do not have significant dollar savings to deploy. The FCNR-B window is designed for deposits of $10,000 and above. It is not a retail savings product — it is a capital flows tool that happens to offer attractive terms to the diaspora.

## The Bigger Picture

The RBI's NRI dollar mobilisation efforts — whether through FCNR-B deposits, NRI bonds, or other instruments — are not charity. They are a transaction. India needs dollars. You have dollars. The RBI is offering you a premium to lend those dollars to the Indian banking system for a fixed period.

In 2013, NRIs who participated in the FCNR-B window earned 5 to 5.5 percent on dollar deposits at a time when US CDs were paying less than 1 percent. They took no exchange-rate risk. They earned a handsome premium. And they helped stabilise the Indian economy at a moment of genuine vulnerability.

Whether 2026 presents a similar opportunity depends on the terms the RBI offers, the trajectory of oil prices (which determine whether the rupee's decline is temporary or structural), and your own financial situation.

Watch for the announcement. It is coming. And when it does, the terms will tell you everything about how desperate the situation really is. The more generous the rate, the more serious the crisis.

In 2013, the premium was 400 basis points above LIBOR.

If the 2026 premium is higher, that is not good news for India. But it may be very good news for your savings account."""

art1_sources = json.dumps([
    "Reuters: India to conduct $5 billion dollar/rupee swap as FX pain persists (May 21, 2026)",
    "Madhyamam Online: RBI is evaluating multiple steps to check rupee decline (May 22, 2026)",
    "Outlook Business: RBI Explores Aggressive Measures As Rupee Nears 97 Per Dollar (May 2026)",
    "Reuters: India central bank's daily $1 billion FX defence struggles to turn rupee tide (May 2026)",
    "Livemint: RBI's surprise $5 bln swap seen cooling forward premiums (May 2026)",
    "Reuters: Rupee hits record low near 97/USD on oil, US Treasury yield strain (May 2026)",
    "Reuters: Asia's currencies are flashing oil shock alarm (May 2026)",
    "Reuters: Indian retailers raise fuel prices a fourth time (May 2026)"
])

# ── Image sourcing for Article 1 ──
print("\n=== Article 1 [markets-finance]: Image sourcing ===")
# This is about RBI/rupee policy — no person image. Use Pexels for Indian currency/RBI building
art1_img_url = None
art1_img_attr = None

# Try Pexels with specific terms
pexels_result = fetch_pexels_image("Indian rupee currency notes", "India reserve bank building")
if pexels_result:
    art1_img_url = pexels_result["url"]
    art1_img_attr = "Pexels"

if art1_img_url:
    uploaded = upload_image_to_supabase(art1_img_url, f"{art1_id}.jpg")
    if uploaded:
        art1_img_url = uploaded
    else:
        art1_img_url = None

print(f"  Image result: {art1_img_url is not None}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: [lifestyle-health] The Hair Loss Drug Your
#             Dermatologist Prescribed Has a Warning Label Now
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "The Hair Loss Drug Millions of Indian Men Take Without a Second Thought Just Got a Strengthened Warning From the UK's Drug Regulator. The Side Effects Can Persist for Years After You Stop."
art2_subheadline = "In 2026, the UK's Medicines and Healthcare products Regulatory Agency strengthened its safety warnings for finasteride — the active ingredient in Propecia and dozens of generic versions — to explicitly include depression, suicidal thoughts, and sexual dysfunction that can persist long after the drug is discontinued. A new case study published in the Journal of Psychosexual Health documents a healthy 26-year-old man who developed penile numbness, orgasm dysfunction, and reduced sensation that persisted for 18 months after he stopped taking just 1 milligram of finasteride daily for hair loss. The drug is one of only two FDA-approved treatments for male pattern baldness and is prescribed to millions globally. Indian men have among the highest rates of androgenetic alopecia in the world — studies estimate that 58 percent of Indian men experience significant hair loss by age 50. In the Indian American community, where finasteride is prescribed casually by dermatologists and primary care physicians, and where hair transplant tourism to India often involves pre- and post-operative finasteride use, the strengthened warnings raise urgent questions about informed consent, prescribing practices, and the cultural pressure that makes Indian men uniquely vulnerable to accepting pharmaceutical risk for cosmetic benefit."
art2_slug = "finasteride-propecia-hair-loss-sexual-side-effects-mhra-warning-indian-men-20260527"
art2_category = "lifestyle-health"

art2_body = """Every Indian man knows the conversation. It starts in your mid-twenties. The hairline recedes. The crown thins. An uncle mentions it at a family gathering. A colleague at work — always another desi — quietly recommends a dermatologist. The dermatologist looks at your scalp for thirty seconds and writes a prescription: finasteride, 1 mg daily. Take it indefinitely.

Most Indian men fill the prescription without reading the fine print. The drug is FDA-approved. Their friends take it. The dermatologist said it was safe. The alternative — visible hair loss in a culture that still associates a full head of hair with youth, virility, and professional credibility — feels worse than any listed side effect.

In 2026, the UK's Medicines and Healthcare products Regulatory Agency (MHRA) updated its position on that fine print. The side effects are not just listed. They are now strengthened warnings.

## What the MHRA Said

The MHRA — the UK equivalent of the FDA — completed an extensive review of finasteride and dutasteride (a related drug) and concluded that the evidence warrants strengthened warnings for three categories of adverse effects:

**Psychiatric effects:** Depression, low mood, and suicidal thoughts. The MHRA's updated guidance explicitly states that patients should be monitored for changes in mood and that treatment should be discontinued if psychiatric symptoms develop.

**Sexual dysfunction:** Erectile dysfunction, reduced libido, and ejaculatory dysfunction. These effects were already listed in the prescribing information, but the updated MHRA position emphasises that they can occur during treatment and may persist after discontinuation.

**Persistence after discontinuation:** This is the critical update. The MHRA now warns that sexual dysfunction and psychiatric effects may continue after the drug is stopped. This is not a theoretical possibility listed in small print. It is a strengthened, prominently positioned warning.

The condition in which sexual and neurological side effects persist after finasteride discontinuation has been documented in the medical literature as Post-Finasteride Syndrome (PFS). It remains controversial among some dermatologists and urologists — some argue that the reported symptoms are driven by anxiety or the nocebo effect (the expectation of side effects causing their experience). But the MHRA's decision to strengthen warnings suggests that the regulator, at least, considers the evidence sufficient to warrant formal caution.

## The Case Study

A case report published in the Journal of Psychosexual Health in May 2026 describes a 26-year-old, otherwise healthy man who was prescribed 1 mg of finasteride daily for male pattern baldness. He had no prior history of sexual dysfunction, psychiatric illness, or chronic disease.

After several months on the drug, he developed penile numbness, difficulty achieving orgasm, and reduced genital sensation. He discontinued finasteride.

Eighteen months later, the symptoms had not resolved.

The case study authors note that the patient's symptoms are consistent with the Post-Finasteride Syndrome phenotype described in larger observational studies — a cluster of sexual, neurological, and cognitive symptoms that persist for months or years after discontinuation.

A single case study is not proof of causation. But it joins a growing body of evidence — including a 2.2-million-person cohort study from Sweden that found associations between 5α-reductase inhibitors (the drug class that includes finasteride) and increased risks of depression and dementia, and a George Washington University study by Dr Michael Irwig that documented persistent sexual dysfunction in men who had discontinued finasteride.

## Why This Matters for Indian Men

The relevance of this warning to the Indian American community is not abstract. It is specific and structural.

**Prevalence of hair loss.** Indian men have among the highest rates of androgenetic alopecia (male pattern baldness) in the world. A landmark Indian dermatology study estimated that 58 percent of Indian men experience clinically significant hair loss by age 50, with onset often beginning in the early to mid-twenties. The combination of genetic predisposition and early onset means that Indian men are prescribed finasteride younger, for longer durations, and often at the most sexually active phase of their lives.

**Cultural pressure.** Hair loss in the Indian community carries social weight that is difficult to overstate. Matrimonial profiles mention hair. Job interviews in India — and, more subtly, in Indian American professional circles — are influenced by appearance in ways that are rarely acknowledged openly. The pressure to maintain a full head of hair is not vanity. It is a rational response to a cultural environment that penalises hair loss in ways that Western culture, which has increasingly normalised baldness, does not.

This cultural pressure creates a specific vulnerability: Indian men are more likely to accept pharmaceutical risk for a cosmetic outcome because the perceived cost of not treating is higher. When a 24-year-old Indian American software engineer walks into a dermatologist's office and says "I am losing my hair," the cultural subtext is: "This will affect my marriage prospects, my family's perception of me, and possibly my career." That subtext makes it harder to weigh the drug's side effects objectively.

**Hair transplant tourism.** India is one of the world's leading destinations for hair transplant surgery, with clinics in Delhi, Mumbai, Bengaluru, and Chandigarh performing thousands of follicular unit extraction (FUE) procedures each year. Many of these clinics prescribe finasteride as a pre-operative and long-term post-operative medication to slow ongoing hair loss in non-transplanted areas. Indian Americans who travel to India for hair transplants — a common practice, given that the same procedure costs $3,000 to $5,000 in India versus $15,000 to $25,000 in the US — are often prescribed finasteride by the transplant surgeon with minimal discussion of side effects. The prescription is framed as standard protocol, not as a risk-benefit decision.

**Prescribing practices in the US.** In the US, finasteride for hair loss is frequently prescribed by dermatologists and primary care physicians through teledermatology platforms — Hims, Keeps, Lemonada, Roman — that offer online consultations lasting 5 to 10 minutes. The prescription is generated after a brief questionnaire. The side-effect discussion, when it happens, is often a checkbox on a screen. Indian American men who use these platforms may never have an in-person conversation about the risks.

## What the Medical Literature Actually Shows

The data on finasteride's side effects is more nuanced than either camp — the "it's perfectly safe" prescribers or the "it ruined my life" patient advocates — typically acknowledges.

**Clinical trial data.** In the original clinical trials that led to FDA approval, sexual side effects — decreased libido, erectile dysfunction, and ejaculatory dysfunction — were reported by approximately 3.8 percent of men taking 1 mg finasteride, compared to 2.1 percent on placebo. The difference is statistically significant but modest in absolute terms. Most trial participants who reported side effects saw them resolve after discontinuation.

**Post-marketing data.** After the drug went to market and millions of men began taking it, reports of persistent side effects increased. The FDA updated the finasteride label in 2012 to include a warning about sexual side effects that continued after stopping the drug, and again in 2023 to include reports of suicidal ideation.

**Observational studies.** A 2022 study of 2.2 million people in Sweden found that users of 5α-reductase inhibitors (finasteride and dutasteride) had a modestly elevated risk of depression in the first 18 months of use. A separate analysis found a small association with dementia, though the effect attenuated after adjusting for indication bias (men taking finasteride for enlarged prostate, who are older, are inherently at higher dementia risk).

**A 2025 comparative study** of finasteride versus dutasteride found no significant difference in sexual dysfunction risk between the two drugs, but identified risk factors that increased the likelihood of side effects: older age, hypertension, mood disorders, and Hispanic/Latino ethnicity. South Asian ethnicity was not separately analysed in this study — a gap that matters, given the pharmacogenomic differences between populations in drug metabolism.

## The Informed Consent Gap

The central issue is not whether finasteride is "safe" or "dangerous." It is whether Indian American men — and Indian men globally — are making a genuinely informed decision when they start taking it.

An informed decision requires understanding:

**The absolute risk.** Approximately 2 to 4 percent of men will experience sexual side effects while taking finasteride. The risk of those effects persisting after discontinuation is lower — estimated at less than 1 percent in clinical trials, though post-marketing reports suggest the number may be higher.

**The duration of use.** Finasteride works only as long as you take it. Stop, and hair loss resumes within 6 to 12 months. This means that most men who start finasteride in their twenties will take it for decades. Long-term safety data beyond 10 years is limited.

**The alternative landscape.** Minoxidil (Rogaine) is the other FDA-approved hair loss treatment and does not carry the same systemic hormonal effects. Low-level laser therapy, platelet-rich plasma injections, and hair transplant surgery are non-pharmaceutical options. None is as convenient as a daily pill, which is partly why finasteride dominates.

**Your personal risk profile.** If you have a history of depression, anxiety, or sexual dysfunction, the risk-benefit calculus for finasteride is different than for someone with no such history. If you are taking SSRIs (which themselves affect sexual function), adding finasteride introduces a compounding variable. These conversations are not happening in 10-minute telemedicine consultations.

## What to Do If You Are Currently Taking Finasteride

Do not stop abruptly without consulting your doctor. Abrupt discontinuation is not dangerous in the way that stopping certain psychiatric medications can be, but a managed discussion with your prescriber about your risk profile, your experience on the drug, and your alternatives is better than a panicked stop.

If you have experienced any of the following while on finasteride — reduced libido, erectile difficulty, changes in ejaculation, emotional blunting, difficulty concentrating, or changes in mood — document them and discuss with your doctor. These symptoms are recognised side effects, not signs of a separate condition.

If you stopped finasteride and continue to experience sexual or cognitive symptoms, consult a urologist or endocrinologist — not just your dermatologist. Post-finasteride symptoms, if they occur, may benefit from hormonal evaluation, including testosterone, DHT, estradiol, and neurosteroid panels.

## The Conversation We Are Not Having

In the Indian American community, hair loss is discussed extensively. Treatments are shared among friends. Dermatologists are recommended. Hair transplant clinics in India are reviewed on WhatsApp groups. But the side effects of the drugs that accompany these treatments are discussed almost never.

The MHRA's strengthened warning is an opportunity to change that. Not to scare men away from a drug that helps many of them. But to ensure that every Indian man who starts finasteride does so with full knowledge of what the drug can do — both to his hair and to his body.

Your hair loss is not a medical emergency. A prescription should not feel like one either."""

art2_sources = json.dumps([
    "MHRA: Finasteride and Dutasteride updated safety warnings for psychiatric side effects and sexual dysfunction (2026)",
    "Journal of Psychosexual Health: Case study of persistent sexual dysfunction post-finasteride (May 2026)",
    "New York Post: Healthy 26-year-old had penis numbness from popular drug even after stopping (May 2026)",
    "HCPLive: Sexual Dysfunction in Those with Androgenetic Alopecia on Dutasteride Versus Finasteride (2025)",
    "Acta Psychiatrica Scandinavica: 5α-Reductase Inhibitors Associated With Increased Risk of Depression, Dementia (2022)",
    "George Washington University: Michael Irwig study on persistent sexual dysfunction from finasteride",
    "The Health Dispensary: MHRA 2026 safety warning explained"
])

# ── Image sourcing for Article 2 ──
print("\n=== Article 2 [lifestyle-health]: Image sourcing ===")
# This is about a drug/medical topic — use Pexels for specific imagery
art2_img_url = None
art2_img_attr = None

pexels_result2 = fetch_pexels_image("medicine pills prescription bottle", "hair loss treatment scalp")
if pexels_result2:
    art2_img_url = pexels_result2["url"]
    art2_img_attr = "Pexels"

if art2_img_url:
    uploaded2 = upload_image_to_supabase(art2_img_url, f"{art2_id}.jpg")
    if uploaded2:
        art2_img_url = uploaded2
    else:
        art2_img_url = None

print(f"  Image result: {art2_img_url is not None}")


# ══════════════════════════════════════════════════════════════
# PUBLISH BOTH ARTICLES
# ══════════════════════════════════════════════════════════════

articles = [
    {
        "id": art1_id,
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "slug": art1_slug,
        "body": art1_body,
        "category": art1_category,
        "vertical": "economy",
        "sources": json.loads(art1_sources),
        "status": "published",
        "published_at": now,
        "score_total": 85,
        "image_url": art1_img_url,
        "image_attribution": art1_img_attr,
    },
    {
        "id": art2_id,
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "slug": art2_slug,
        "body": art2_body,
        "category": art2_category,
        "vertical": "diaspora",
        "sources": json.loads(art2_sources),
        "status": "published",
        "published_at": now,
        "score_total": 82,
        "image_url": art2_img_url,
        "image_attribution": art2_img_attr,
    },
]

print("\n=== Publishing articles ===")
for art in articles:
    print(f"\n  [{art['category']}] {art['headline'][:80]}...")
    try:
        result = sb_post("p2_articles", art)
        if result:
            print(f"  ✓ Published: {art['slug']}")
        else:
            print(f"  ⚠ May already exist: {art['slug']}")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

print("\n=== Done ===")
