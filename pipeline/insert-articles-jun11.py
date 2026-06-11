#!/usr/bin/env python3
"""Insert 3 articles for The Videshi - June 11, 2026 batch"""

import json
import os
import subprocess
import uuid
from datetime import datetime, timezone

# Load Supabase credentials
env = {}
with open(os.path.expanduser("~/.env.supabase")) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k] = v

SUPABASE_URL = env["SUPABASE_URL"]
SUPABASE_KEY = env["SUPABASE_SERVICE_ROLE_KEY"]

now = datetime.now(timezone.utc).isoformat()

articles = []

# ============================================================
# ARTICLE 1: Microplastics in the Brain
# ============================================================
articles.append({
    "id": str(uuid.uuid4()),
    "title": "Microplastics Are Accumulating in Human Brains at Alarming Rates — And the Diaspora Should Pay Attention",
    "subheadline": "A landmark Nature Medicine study finds plastic concentrations in brain tissue up to 30 times higher than in other organs, with dementia patients showing the greatest burden",
    "slug": "microplastics-brain-accumulation-dementia-risk-diaspora",
    "category": "lifestyle-health",
    "status": "review",
    "is_editorial": False,
    "hero_image": "https://upload.wikimedia.org/wikipedia/commons/e/e2/Microplastics-in-ocean_%28OWID_0661%29.png",
    "hero_image_alt": "Visualization of microplastic distribution in the world's oceans",
    "published_at": now,
    "body": """The plastic water bottle you drank from this morning, the takeaway container from last night's dinner, the synthetic fibers in your athleisure — tiny fragments from all of them may already be lodged in your brain. A sweeping new study published in *Nature Medicine* has found that micro- and nanoplastic concentrations in human brain tissue are **7 to 30 times greater** than in the liver or kidneys, raising urgent questions about neurological health that hit especially close to home for the Indian diaspora.

## What the Research Found

The study, led by **Alexander J. Nihart** and a team at the University of New Mexico, used pyrolysis gas chromatography–mass spectrometry (Py-GC/MS) to analyze brain tissue samples collected between 2016 and 2024. The findings were striking on multiple fronts.

First, brain tissue contained dramatically higher concentrations of micro- and nanoplastics (MNPs) compared to other organs. **Polyethylene** — the plastic used in grocery bags, food packaging, and water bottles — was the most commonly detected polymer. Second, samples from **2024 contained significantly more plastic** than those from 2016, suggesting that brain accumulation is accelerating in real time. Third, and perhaps most alarming, brain tissue from **patients with dementia** showed even higher plastic concentrations than tissue from neurologically healthy individuals.

A separate study published in *JAMA Network Open* corroborated these findings by detecting microplastics on the **olfactory bulb**, the brain structure responsible for smell — and one of the first regions affected in Alzheimer's disease. Together, the research paints a picture of plastic particles breaching the blood-brain barrier and potentially contributing to neurodegenerative disease.

## Why This Matters for the Diaspora

For South Asians in the United States, United Kingdom, and Canada, the findings carry particular weight. The diaspora sits at the intersection of two plastic-heavy cultures.

**In India**, plastic packaging is ubiquitous. Street food served in thin polyethylene bags, water stored in plastic tanks, chai poured into disposable cups — daily life involves constant contact with low-grade plastics that shed microparticles, especially when heated. Families visiting home or receiving shipments of Indian snacks and spices are often consuming products packaged in materials that would not pass Western food-safety standards.

**In the West**, the sources are different but no less pervasive. Takeaway culture — especially the post-pandemic surge in delivery — means meals arrive in polystyrene and polypropylene containers. Bottled water, which many NRI families rely on during travel, is a documented source of nanoplastics. A 2024 Columbia University study found roughly **240,000 nanoplastic particles per liter** of bottled water, most small enough to cross cell membranes.

The South Asian dietary pattern of reheating food in plastic containers — common in busy diaspora households juggling work and family — is another risk multiplier. Microwaving plastic releases microparticles at rates orders of magnitude higher than room-temperature storage.

## What Can Be Done

Researchers caution that the science is still emerging, and no one is suggesting panic. But the direction of the evidence is clear enough to warrant practical changes.

**Switch to glass or steel containers** for food storage and reheating. Many Indian kitchens already have steel tiffins and brass vessels — a return to tradition that happens to be scientifically sound. **Filter tap water** rather than relying on bottled water; reverse-osmosis systems, common in Indian households, are effective at removing microparticles. **Avoid heating food in plastic** of any kind, including containers labeled "microwave safe," which refers to structural integrity, not chemical safety. **Reduce single-use plastic** where possible — cloth bags for groceries, steel bottles for water, beeswax wraps for leftovers.

## The Bigger Picture

The Nature Medicine study is part of a growing body of research that has found microplastics in human blood, lungs, placentas, and now — in troubling concentrations — the brain. The correlation with dementia does not yet prove causation, but the researchers note that plastic particles can trigger **neuroinflammation**, disrupt cellular function, and serve as carriers for other toxic chemicals like phthalates and bisphenol A.

For a diaspora community already navigating elevated rates of cardiovascular disease and Type 2 diabetes, adding neurological risk from environmental plastic exposure is a sobering reminder that health is shaped by the materials we surround ourselves with — not just the food we eat.

The plastic in your brain got there without your permission. What you do about the next bottle, the next container, the next bag is still your call.

*Sources: Nature Medicine (Nihart et al., 2026); JAMA Network Open (olfactory bulb microplastics study); Columbia University nanoplastics in bottled water (2024)*""",
    "sources": json.dumps(["Nature Medicine", "JAMA Network Open", "Columbia University"]),
})

# ============================================================
# ARTICLE 2: Smartphones at 13 — Sleep, Depression, Obesity
# ============================================================
articles.append({
    "id": str(uuid.uuid4()),
    "title": "Getting a Smartphone at 13 Wrecks Sleep by 14 — A New Study That Every Desi Parent Needs to Read",
    "subheadline": "A JAMA Pediatrics study of nearly 2,000 teens links smartphone acquisition age to insufficient sleep, depression, and obesity — findings that collide directly with South Asian parenting norms",
    "slug": "smartphone-age-13-sleep-depression-obesity-teens-study",
    "category": "lifestyle-health",
    "status": "review",
    "is_editorial": False,
    "hero_image": "https://images.pexels.com/photos/10387709/pexels-photo-10387709.jpeg?auto=compress&cs=tinysrgb&w=800",
    "hero_image_alt": "Teenager using a smartphone at night, illuminated by screen glow",
    "published_at": now,
    "body": """The argument plays out in South Asian households across the English-speaking world with reliable frequency: a 12- or 13-year-old insists they need a phone, parents weigh safety and social pressure against screen-time anxiety, and eventually a device lands in the child's hands. A major new study published in *JAMA Pediatrics* on June 8, 2026, now gives that debate a hard empirical edge — and the results should give every desi parent pause.

## The Study

Researchers from the **Children's Hospital of Philadelphia (CHOP)**, **UC Berkeley**, and the **University of Pennsylvania** — led by **Ziv Bren** with senior author **Ran Barzilay** — tracked **1,959 adolescents** from the Adolescent Brain Cognitive Development (ABCD) study, the largest long-term study of brain development in the United States.

The headline finding: teens who received their first smartphone at age 13 had a **significantly higher risk of insufficient sleep** by age 14. Those who got a phone even earlier — before age 12 — faced compounding risks, including elevated rates of **depression** and **obesity**.

The mechanism is not mysterious. Smartphones are sleep thieves. A separate finding from the same journal found that **more than 50 percent of teenagers** use their phones between 10 p.m. and 6 a.m. on school nights. The blue light suppresses melatonin. The social media notifications trigger dopamine loops. The phone becomes the last thing a teen sees before sleep and the first thing they reach for at 2 a.m. — and the developing adolescent brain pays the price.

## The South Asian Context

These findings land differently in diaspora families, where the smartphone often serves functions that go beyond social media.

**Academic pressure starts early.** In many Indian-American and British-Indian households, children are managing tutoring apps, Khan Academy sessions, and group chats for math olympiad prep by middle school. The phone becomes an academic tool — and that framing makes it harder for parents to impose bedtime restrictions. "He needs it for homework" is a sentence that ends many screen-time conversations before they start.

**Family connectivity is a factor.** For NRI families with grandparents in India, the smartphone is a lifeline. WhatsApp video calls with Nani and Dada happen on the child's schedule, often in the evening hours that overlap with India's morning. The phone isn't just entertainment — it's emotional infrastructure.

**Late-night studying is normalized.** South Asian academic culture often valorizes the late-night study session. A teenager studying until midnight is seen as disciplined, not sleep-deprived. But the JAMA data suggests that the phone in the room — even when ostensibly used for studying — is the variable that disrupts sleep architecture. It is not the studying that is the problem. It is the device.

**Parental screen habits matter too.** The study's authors note that adolescent phone behavior mirrors household norms. In many diaspora homes, parents themselves are on WhatsApp groups, YouTube, or Indian news apps late into the night. Children absorb these patterns. Setting a "phones off at 9 p.m." rule is hard to enforce when the adults aren't following it.

## What the Data Actually Says

The ABCD study is unusually rigorous. It followed the same cohort over multiple years, used validated sleep and mental-health assessments, and controlled for socioeconomic variables. The findings are not about correlation between phone *use* and poor outcomes — they are about the **age of first phone acquisition** as an independent risk factor.

That distinction matters. It means the debate is not just about screen-time limits or parental controls. It is about whether a 12-year-old's brain is ready for the cognitive and emotional load of a device that offers unlimited access to social comparison, algorithmic content, and 24/7 connectivity.

The researchers did not recommend a specific "right age" for a first smartphone, but the data clearly suggests that **delaying acquisition past 13** is associated with meaningfully better sleep and mental-health outcomes at 14.

## Practical Steps for Families

Sleep researchers and pediatricians offer consistent guidance that aligns with the JAMA findings.

**Charge phones outside the bedroom.** This single intervention eliminates the 2 a.m. scroll. A charging station in the kitchen or living room, used by everyone in the family, normalizes the practice. **Set a household digital curfew** — not just for children, but for adults. The study's finding that parental behavior shapes teen behavior means this is a family commitment, not a top-down rule. **Consider a basic phone first.** For families that want their child reachable for safety, a phone without social media apps or a browser achieves that goal without the sleep-disrupting features. Several companies now make "dumb phones" designed for exactly this use case. **Talk about sleep as a health metric**, not a convenience. South Asian families that track academic performance meticulously often ignore sleep data. Framing sleep as essential to cognitive performance — "you'll score better on the SAT with eight hours" — can land in a way that "put the phone down" cannot.

## The Bigger Picture

The JAMA Pediatrics study arrives at a moment when the U.S. Surgeon General has called for warning labels on social media platforms and multiple states are considering legislation to restrict minors' smartphone access. For diaspora families navigating two cultures' expectations — American social norms where "everyone has a phone" and Indian academic norms where "the phone is for studying" — the findings offer something rare: clear, longitudinal data on a decision most families make in a fog of competing pressures.

The phone can wait. The teenage brain cannot.

*Sources: JAMA Pediatrics (Bren, Barzilay et al., June 8, 2026); ABCD Study; JAMA Pediatrics (teen nighttime phone use data)*""",
    "sources": json.dumps(["JAMA Pediatrics", "ABCD Study", "CHOP/UC Berkeley/UPenn"]),
})

# ============================================================
# ARTICLE 3: India's NRI Money Push
# ============================================================
articles.append({
    "id": str(uuid.uuid4()),
    "title": "India Is Rolling Out the Red Carpet for NRI Money — Here's What Changed This Week and What It Means for You",
    "subheadline": "Tax-free bond investments, subsidized FCNR deposits, higher equity limits, and surging NRI deposit rates signal Delhi's most aggressive play yet for diaspora dollars",
    "slug": "india-nri-investment-rbi-fpi-tax-free-bonds-fcnr-deposits-2026",
    "category": "markets-finance",
    "status": "review",
    "is_editorial": False,
    "hero_image": "https://upload.wikimedia.org/wikipedia/commons/a/a8/Reserve_Bank_of_India_Building.jpg",
    "hero_image_alt": "Reserve Bank of India building, the central bank driving new NRI investment policies",
    "published_at": now,
    "body": """If you are an NRI with money parked in a U.S. savings account earning 4 percent, India just made it very expensive to ignore the alternative. Over the span of four days — June 5 through June 8, 2026 — the Reserve Bank of India and the Finance Ministry rolled out a coordinated package of measures so aggressive that economists are calling it the most significant NRI-focused financial reform in over a decade. Here is what changed, what it means, and what you should be thinking about.

## The Four Big Moves

**1. Government bonds are now tax-free for foreign portfolio investors.**

The Finance Ministry issued the **Income-tax (Amendment) Ordinance, 2026**, exempting foreign portfolio investors (FPIs) from tax on interest income earned on Indian government securities (G-Secs). Previously, FPIs paid a 5 to 20 percent withholding tax depending on the instrument and treaty. That barrier is gone. Within **three days of the announcement**, over **$1 billion** in new government bond purchases were recorded — a pace that stunned even optimistic forecasters.

For NRIs, this matters because many invest through FPI-registered funds. The tax exemption makes Indian sovereign debt competitive with U.S. Treasuries on an after-tax basis for the first time, especially at India's current 10-year yield of roughly 6.8 percent versus the U.S. 10-year at 4.3 percent.

**2. The RBI is subsidizing FCNR deposits.**

In a move reminiscent of the 2013 dollar-swap window that rescued the rupee, the RBI announced it will **bear the full hedging cost** on Foreign Currency Non-Resident (FCNR) deposits with tenures of 3 to 5 years. This is a direct subsidy. Banks can now offer NRIs dollar-denominated deposits without pricing in the rupee-hedging cost — which typically eats 2 to 3 percentage points of yield. The RBI expects this single measure to attract **$35 to 40 billion** in fresh FCNR inflows.

If you have held off on FCNR deposits because the effective yield after hedging was underwhelming, that calculus has fundamentally changed.

**3. NRI equity investment limits have been raised.**

Individual NRI investment limits in listed Indian companies have been raised from **5 percent to 10 percent** of paid-up capital. The aggregate NRI limit moves from **10 percent to 24 percent**. This is significant for NRIs who invest directly in Indian equities through their Portfolio Investment Scheme (PIS) accounts. The old 5 percent cap frequently forced NRIs out of popular mid-cap stocks where the limit was already breached. The doubling of the individual cap and the near-tripling of the aggregate cap open up substantially more room.

**4. Banks are competing aggressively for NRI deposits.**

Indian banks have responded to the regulatory signal by **hiking NRI deposit rates by up to 300 basis points**. HDFC Bank is now offering **6 percent** on select NRI fixed deposits. SBI has moved to a **5.25 to 6 percent** range. AU Small Finance Bank is leading the pack at **7.1 percent** — a rate that, combined with the FCNR hedging subsidy, makes the risk-adjusted return genuinely attractive for a dollar-denominated instrument backed by Indian banking regulation.

## Why Now?

The timing is not coincidental. India is navigating a period of moderating domestic inflows — equity mutual fund inflows fell **40 percent in May** to ₹22,907 crore, the lowest in over a year. The rupee has been under pressure from a widening current account deficit and global dollar strength. And Bloomberg's decision on whether to include Indian bonds in its flagship index is expected this month — the tax exemption is widely seen as a final push to secure inclusion, which would trigger tens of billions in passive inflows.

For Delhi, NRI money solves multiple problems simultaneously. It supports the rupee without depleting forex reserves. It deepens the bond market ahead of index inclusion. And it channels diaspora savings into productive Indian assets rather than letting them sit in American bank accounts or index funds.

## What NRIs Should Consider

**FCNR deposits are the most straightforward opportunity.** If you have dollar savings earning 4 to 4.5 percent in a U.S. high-yield savings account, a 3-year FCNR deposit at 6 to 7 percent with the RBI absorbing hedging costs is a meaningful upgrade — with the caveat that your money is locked for the deposit tenure and subject to Indian banking regulation.

**The G-Sec tax exemption benefits those investing through FPI-registered funds** rather than direct NRI bond purchases. If your wealth manager offers an India sovereign debt allocation, the after-tax math just improved substantially. Direct NRE/NRO investments in government bonds were already partially tax-advantaged; the bigger shift is for pooled FPI vehicles.

**Equity limits matter most for active stock pickers.** If you use a PIS account to buy Indian equities directly, you now have twice the headroom in individual companies. For passive investors in Indian equity ETFs, the impact is indirect but positive — more NRI capital flowing into mid-caps improves liquidity and price discovery.

**Do not ignore the risks.** FCNR deposits carry repatriation risk if India faces a severe balance-of-payments crisis (as happened briefly in 2013). G-Sec yields can fall if the RBI cuts rates, producing capital gains but locking in lower reinvestment rates. And the rupee, despite current stability, remains a long-term depreciation story against the dollar — the 20-year trend is roughly 3 percent annual depreciation.

## The Bottom Line

India has never been this explicit about wanting NRI money, and the incentives have never been this generous. For diaspora families who maintain financial ties to India — which is most of them — the June 2026 package deserves a serious conversation with your financial advisor, your NRI banking relationship manager, or at minimum a fresh look at your FCNR and PIS accounts.

The window will not stay this open forever. These measures are designed to attract capital during a period of stress. When the pressure eases, the subsidies will too.

*Sources: Reserve Bank of India circulars (June 5–8, 2026); Finance Ministry Income-tax Amendment Ordinance 2026; HDFC Bank, SBI, AU Small Finance Bank NRI deposit rate announcements; Bloomberg; AMFI mutual fund flow data (May 2026)*""",
    "sources": json.dumps(["Reserve Bank of India", "Finance Ministry of India", "Bloomberg", "AMFI"]),
})

# Insert all articles
for i, article in enumerate(articles):
    print(f"\n{'='*60}")
    print(f"Inserting article {i+1}: {article['slug']}")
    print(f"Category: {article['category']}")
    print(f"Body length: {len(article['body'])} chars, ~{len(article['body'].split())} words")
    
    payload = json.dumps(article)
    
    result = subprocess.run(
        [
            "curl", "-s", "-w", "\n%{http_code}",
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            "-H", f"apikey: {SUPABASE_KEY}",
            "-H", f"Authorization: Bearer {SUPABASE_KEY}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=minimal",
            "-d", payload,
        ],
        capture_output=True, text=True
    )
    
    output = result.stdout.strip()
    lines = output.split("\n")
    status_code = lines[-1] if lines else "unknown"
    body = "\n".join(lines[:-1])
    
    if status_code == "201":
        print(f"✅ Inserted successfully (HTTP {status_code})")
    else:
        print(f"❌ Failed (HTTP {status_code})")
        print(f"Response: {body}")

print("\n" + "="*60)
print("Done! All articles submitted.")
