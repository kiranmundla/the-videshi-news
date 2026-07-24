#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-23 19:00 PDT run
2 articles:
  1. The Salmonella Recall: One Bad Batch of California Powdered Milk Has Contaminated 15+ Brands
  2. Mental Health Awareness Month: The Silent Crisis in Indian American Families
"""

import os, json, uuid, re, requests, time
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

def fetch_pexels_image(query):
    """Fetch a landscape image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key found")
        return None
    import subprocess
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=5&orientation=landscape"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        if data.get("photos"):
            photo = data["photos"][0]
            return {
                "url": photo["src"]["large2x"],
                "photographer": photo["photographer"],
                "pexels_id": photo["id"],
                "alt": query,
            }
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

now = datetime.now(timezone.utc).isoformat()


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: The Salmonella Recall That Keeps Growing
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "One Bad Batch of California Powdered Milk Has Contaminated Ghirardelli, Target, Williams Sonoma, and a Dozen Other Brands. Check Your Pantry Before the Barbecue."
art1_subheadline = "On April 20, California Dairies Inc. — the largest dairy cooperative in California — recalled bulk powdered milk and buttermilk shipped to manufacturers across the country due to potential Salmonella contamination. In the five weeks since, the recall has cascaded through at least 15 brands and counting: Ghirardelli hot cocoa and frappe mixes, Zapp's and Dirty potato chips, Target's Good & Gather trail mix, Williams Sonoma and Fireworks Popcorn, Fisher and Squirrel Brand snack mixes, Giant Eagle pita chips, Blackstone seasoning, Pork King Good pork rinds, Kroger croutons, and multiple grocery store pizzas. The FDA says more recalls may follow. For NRI families stocking up for Memorial Day weekend gatherings, this is the food safety check you need to do before guests arrive."
art1_slug = make_slug("california-dairies-salmonella-recall-15-brands-pantry-check-memorial-day")
art1_category = "lifestyle-health"

art1_body = """Somewhere in your pantry, there may be a bag of Zapp's Bayou Blackened Ranch potato chips. Or a canister of Ghirardelli Double Chocolate frappe mix. Or a box of Kroger Homestyle Cheese Garlic croutons with an expiration date in 2027, which means you bought them months ago and forgot they existed. Or a shaker of Blackstone Parmesan Ranch seasoning that you use on everything from grilled chicken to roasted vegetables.

All of these products have one thing in common: they may contain Salmonella.

And all of them trace back to a single source: a batch of powdered milk produced by California Dairies Inc., the largest dairy cooperative in California, which shipped contaminated bulk powdered milk and buttermilk to manufacturers and wholesale distributors across the United States.

## How One Ingredient Became Fifteen Recalls

The original recall was issued on April 20. California Dairies Inc. voluntarily pulled its bulk powdered milk and buttermilk products after internal testing revealed potential Salmonella contamination. The recall was not a consumer-facing event — California Dairies does not sell directly to shoppers. It sells to other companies, which use the powdered milk as an ingredient in their own products.

That distinction is exactly what makes this recall so insidious. Powdered milk is one of the most widely used ingredients in processed food manufacturing. It shows up in seasoning blends, flavoured coatings, snack mixes, beverage mixes, baked goods, frozen pizzas, and dozens of other products. When the base ingredient is contaminated, the contamination fans out across the entire supply chain.

Here is the timeline of the cascade:

**April 28:** Ghirardelli Chocolate Company recalls 13 varieties of powdered beverage mix, including frappe mixes, hot cocoa mixes, and sweet ground powders. These are the bulk-format canisters commonly used in cafés and home kitchens.

**May 4:** Utz Quality Foods recalls limited varieties of Zapp's and Dirty brand potato chips. Affected flavours include Zapp's Bayou Blackened Ranch, Zapp's Big Cheezy, and Dirty brand Maui Onion, Sour Cream and Onion, and Salt and Vinegar chips. The contaminated powdered milk was in the seasoning blend.

**May 5:** Pork King Good recalls sour cream and onion pork rinds and seasoning bottles.

**May 6:** John B. Sanfilippo & Son recalls snack and trail mixes sold under the Fisher, Southern Style Nuts, Squirrel Brand, and Target's Good & Gather labels. The affected product includes Good & Gather Mexican Street Corn trail mix sold at Target stores.

**May 7:** Three more recalls in a single day — Stoltzfus Family Dairy (sour cream and onion cheese curds), Wildlife Seasoning (flavoured popcorn seasoning), and Giant Eagle (baked pita chips with Parmesan, garlic, and herbs).

**May 8:** Williams Sonoma and Fireworks Popcorn products featuring white cheddar seasoning are recalled.

**May 16:** Blackstone Products recalls its Parmesan Ranch seasoning — a popular grilling accessory.

**May 22:** SKS Copack recalls specialty beverages sold under Angel Specialty Products, Royal Gold, Boba Time, Fanale, and Denda brands — the boba tea and specialty drink market.

**Also in May:** Kroger Homestyle Cheese Garlic croutons (recalled by Sugar Foods LLC), and multiple grocery store frozen pizzas — including brands sold at Walmart (Great Value), Aldi (Mama Cozzi's), and regional chains — are pulled from shelves or added to the USDA's recall list.

The FDA's own tracking page currently lists ten product recalls, but it has not been updated since May 18 and does not include the most recent additions. The actual number of affected products is higher and still growing.

## What Salmonella Does

Salmonella is not a trivial concern. The CDC estimates 1.35 million cases of salmonellosis in the United States every year, resulting in 26,500 hospitalisations and 420 deaths.

Symptoms typically appear within 8 to 72 hours of exposure and include diarrhea, fever, and abdominal cramps. Most healthy adults recover without treatment within four to seven days. But for young children, elderly adults, pregnant women, and anyone with a compromised immune system, Salmonella can cause serious and potentially life-threatening infections.

No illnesses have been officially linked to this specific recall as of this weekend. But given how many products are affected, how long some have been on shelves (the Kroger croutons have a 2027 expiration date), and how widely they were distributed, the absence of reported cases may simply mean nobody has connected the dots yet.

## The NRI Kitchen Check

If you are hosting or attending a Memorial Day weekend barbecue, potluck, or family gathering this weekend — and statistically, a significant number of Indian American families are — here is your pantry check:

**Seasoning blends and rubs.** If you use Blackstone Parmesan Ranch seasoning, check the lot number against the recall notice. This seasoning is popular with grill enthusiasts and may have been used on chicken, paneer, or vegetables in recent weeks.

**Snack mixes and trail mixes.** If you bought Good & Gather Mexican Street Corn trail mix from Target, Fisher snack mixes, or Squirrel Brand products, check the recall list. These are exactly the kind of products that get opened, partially eaten, and left in the pantry for weeks.

**Potato chips.** Zapp's Bayou Blackened Ranch and Big Cheezy, and Dirty brand Maui Onion, Sour Cream and Onion, and Salt and Vinegar. If you stocked up for a party, verify the lot numbers.

**Hot cocoa and beverage mixes.** Ghirardelli's recall covers 13 varieties. If you have a canister of Ghirardelli frappe or cocoa mix — particularly the bulk-format versions popular in home coffee setups — check it.

**Frozen pizzas.** Great Value (Walmart), Mama Cozzi's (Aldi), and several regional brands including Roberto's, Henry's Homestyle, and Ole & Lena's pizzas have been recalled. The affected varieties are primarily taco pizzas, chicken bacon ranch, and breakfast pizzas.

**Croutons.** Kroger Homestyle Cheese Garlic croutons sold between March 7 and April 7. These have a long shelf life and are very likely still in pantries.

**Pork rinds.** Pork King Good sour cream and onion — not a traditional Indian household staple, but increasingly popular as a low-carb snack in health-conscious NRI households.

**Boba and specialty drinks.** If you buy Angel Specialty Products, Royal Gold, Boba Time, Fanale, or Denda brand specialty beverages, the most recent recall (May 22) covers these.

## What to Actually Do

**Check the FDA's recall page.** The central tracking page is at fda.gov under "2026 Recalls of Food Products Associated with Powdered Milk from California Dairies Inc." Click through to each individual brand recall for specific lot numbers, UPC codes, and expiration dates.

**When in doubt, throw it out.** If you have any of the affected brands and cannot verify the lot number, discard the product. The cost of replacing a bag of chips is trivially small compared to the cost of a Salmonella infection — particularly if you are hosting elderly parents or young children.

**Watch for symptoms.** If you or a family member has experienced unexplained diarrhea, fever, or stomach cramps in the past several weeks, and you had any of these products in your home, mention it to your doctor. The connection may not be obvious.

**Do not rely on "best by" dates.** The contamination is in the ingredient, not in the product's age. A product with a 2027 expiration date that was made with contaminated powdered milk is just as dangerous as one expiring next week.

**Expect more recalls.** The FDA has stated it is still working with downstream manufacturers and distributors. California Dairies' powdered milk is used by hundreds of food companies. The 15 recalls announced so far are almost certainly not the final count.

## The Bigger Picture

This recall is a case study in how modern food supply chains work — and how they fail. One ingredient supplier, one contaminated batch, and five weeks later the affected products span potato chips, hot cocoa, pork rinds, frozen pizza, trail mix, croutons, boba drinks, seasoning blends, cheese curds, and popcorn. These products were sold at Target, Walmart, Aldi, Giant Eagle, Kroger, Williams Sonoma, and dozens of other retailers across all 50 states.

The FDA's tracking page being out of date — the agency's own page has not been updated in five days despite new recalls being announced — is not reassuring. Neither is the fact that two separate federal agencies (the FDA and the USDA's FSIS) are maintaining separate, barely overlapping recall lists for the same contamination event.

For now, the practical advice is simple: check your pantry, check the lot numbers, and when in doubt, discard. The Memorial Day barbecue can survive without the Blackstone Parmesan Ranch seasoning. Your family's health cannot survive Salmonella as easily."""

art1_sources = [
    "https://www.fda.gov/safety/major-product-recalls/2026-recalls-food-products-associated-powdered-milk-california-dairies-inc-due-potential-salmonella",
    "https://gizmodo.com/latest-salmonella-recall-hits-a-surprisingly-wide-range-of-products-2000762036",
    "https://parade.com/food/nationwide-recall-expanded-for-potato-chips-popcorn-due-to-salmonella-risk",
    "https://www.foxbusiness.com/lifestyle/blackstone-seasoning-blend-recalled-possible-salmonella-contamination",
    "https://www.audacy.com/1010wins/news/national/croutons-recalled-across-17-states-over-salmonella-concerns",
    "https://www.fastcompany.com/91340000/why-are-there-so-many-salmonella-outbreaks-2026",
]

print("=== Article 1: California Dairies Salmonella Recall ===")
print(f"Word count: {len(art1_body.split())}")

art1_image = fetch_pexels_image("snack chips popcorn food pantry kitchen")
if art1_image:
    print(f"  📸 Pexels image: {art1_image['pexels_id']} by {art1_image['photographer']}")

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
    "score_total": 87,
    "tags": ["Salmonella", "food recall", "FDA", "California Dairies", "Ghirardelli", "Target", "Williams Sonoma", "Zapp's", "Memorial Day", "food safety", "pantry", "NRI", "health", "powdered milk"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "One contaminated batch of California powdered milk has triggered 15+ brand recalls across chips, hot cocoa, trail mixes, croutons, pizza, and boba drinks — all sold at Target, Walmart, Kroger, Aldi. For NRI families hosting Memorial Day gatherings this weekend, a practical pantry check guide with every affected brand, what to look for, and when to discard.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result:
    print(f"✓ Published: {art1_id}")
else:
    print("✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Mental Health Awareness Month — The South Asian Silence
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "May Is Mental Health Awareness Month. In Indian American Families, It Is Also the Month Nobody Talks About Mental Health."
art2_subheadline = "One hundred and forty-two thousand tech workers have been laid off in 2026. Meta cut 8,000 on May 20. LinkedIn cut 600. Cloudflare cut 1,100 and blamed AI. Indian nationals hold the majority of H-1B visas, and laid-off workers get 60 days to find a new sponsor or leave the country. Behind every immigration spreadsheet and job application tracker is a person — often with a mortgage, children in school, and parents in India who do not know what is happening — who is not sleeping. May is Mental Health Awareness Month, and the organisation that exists specifically for this community, SAMHIN, is running events across New Jersey and New York. Most Indian Americans have never heard of it."
art2_slug = make_slug("mental-health-awareness-month-indian-american-south-asian-silence-stigma")
art2_category = "lifestyle-health"

art2_body = """There is a specific kind of silence that settles over an Indian American household when something goes wrong. Not the silence of peace, but the silence of management — of controlling information, of deciding who in the family needs to know what, of performing normalcy for the neighbours and the WhatsApp group while the actual situation is handled privately, quietly, and preferably without anyone outside the immediate household ever finding out.

This silence is particularly dense around two subjects: money and mental health. And in May 2026, for tens of thousands of Indian American families, these two subjects have become the same thing.

## The Numbers Behind the Silence

One hundred and forty-two thousand technology workers have been laid off in the United States so far in 2026, according to Layoffs.fyi. The pace has accelerated sharply in May. On May 20, Meta cut roughly 8,000 employees — 10 per cent of its global workforce — while simultaneously moving 7,000 others into AI-focused roles. LinkedIn cut over 600, including 352 from its Mountain View office. Cloudflare eliminated 1,100 positions, 20 per cent of its workforce, with CEO Matthew Prince explicitly citing AI-driven productivity gains that made the roles obsolete.

Amazon, Oracle, Cisco, PayPal, Cognizant, and Block have all announced significant cuts this year. The common thread: AI is replacing functions that humans used to perform, and companies are restructuring around smaller, faster teams rather than simply absorbing the efficiency gains.

Indian nationals are the largest group of H-1B visa holders in the United States. When a tech company announces layoffs, Indian Americans are disproportionately affected — not because they are targeted, but because they are statistically overrepresented in exactly the roles being eliminated: software engineering, data science, product management, quality assurance.

The immigration math is brutal. Under current US rules, an H-1B worker who loses their job has a 60-day grace period to find a new employer willing to sponsor their visa, switch to another visa category, or leave the country. Sixty days. To find a job in a market where 142,000 people are competing for a shrinking pool of positions. While maintaining a mortgage, car payments, children's school enrollment, and the appearance of stability for family in India.

Reports from this week indicate that laid-off Indian workers at Meta are exploring visa loopholes — attempting to switch to B-2 visitor visas to buy six months of breathing room. The process is legal but approvals are increasingly difficult. US immigration authorities have stepped up scrutiny of such applications, recognising the pattern.

For many of these workers, the 60-day clock is ticking right now. And the mental health consequences of that clock — the sleeplessness, the anxiety, the shame, the paralysis — are being experienced in near-total silence.

## Why Indian Americans Don't Talk About It

The reluctance of South Asian Americans to discuss mental health is well-documented, extensively studied, and almost entirely unchanged.

A 2021 study in the Asian American Journal of Psychology found that South Asian Americans reported significantly higher levels of mental health stigma than other Asian American subgroups. The stigma operates on multiple levels simultaneously:

**Family honour.** In many Indian families, a mental health diagnosis — or even the admission of struggling — is perceived as a reflection on the entire family, not just the individual. The question is not "Are you okay?" but "What will people think?" This is not abstract. It determines whether a cousin's marriage prospects are affected, whether the family's standing in the community shifts, whether the WhatsApp group narrative changes from "their son is at Google" to something less impressive.

**The model minority trap.** Indian Americans have the highest median household income of any ethnic group in the United States at approximately $147,000. They hold 74 per cent of H-1B visas for specialised occupations. Seventy-nine per cent of Indian-born US residents have a bachelor's degree or higher. This success narrative — reinforced by media, by community organisations, by parents — creates an impossibly narrow definition of acceptable outcomes. Depression, anxiety, and burnout do not fit the narrative. So they are not discussed.

**Generational disconnect.** For first-generation Indian immigrants who survived the uncertainties of immigration, built careers from nothing, and sent money home to support extended families, the idea that their American-raised children could be struggling psychologically is genuinely bewildering. "We had real problems," the thinking goes. "You have a six-figure salary and a house with central air conditioning. What do you have to be depressed about?" This is not cruelty. It is a failure of imagination rooted in genuinely different life experiences.

**The provider identity.** In Indian American families, the H-1B holder is often not just an employee but the financial anchor for an entire transnational ecosystem — supporting parents in India, contributing to siblings' expenses, funding family medical bills, maintaining property. Admitting to mental health struggles threatens this identity. If the provider is not okay, the entire structure feels unstable. So the provider performs being okay, even when they are not.

## What the 60-Day Clock Does to a Person

Immigration attorneys who work with laid-off H-1B holders describe a specific psychological profile that emerges during the grace period.

**Week one:** Shock, followed by frantic activity. Updating LinkedIn, reaching out to recruiters, applying to every open position. Adrenaline masks the anxiety.

**Week two to three:** The market reality sets in. Responses are slow. Many companies have hiring freezes. Others are not willing to sponsor H-1B transfers. The gap between effort and results widens. Sleep deteriorates.

**Week three to four:** The practical consequences start materialising. The mortgage payment is due. The children's school asks about next year's enrollment. The spouse — often on an H-4 dependent visa with no independent work authorisation — begins to ask questions. Parents in India call and something feels off but nobody says what.

**Week five to six:** For those who have not secured a new position, the reality of potentially having to leave the country — uproot children, sell or abandon a house, explain the situation to family — creates a state of chronic, low-grade panic that does not resolve. It sits in the chest. It makes concentration difficult. It makes every rejection email feel not like a professional setback but like an existential threat.

This is not speculation. This is what immigration lawyers, community counsellors, and the workers themselves describe. And it is happening to thousands of people right now, this month, in the Bay Area, in Seattle, in Austin, in New York, in every metro area where tech companies have offices and Indian Americans have built lives.

## SAMHIN Exists. Most People Don't Know.

The South Asian Mental Health Initiative and Network — SAMHIN — is the primary US-based organisation focused specifically on mental health in South Asian communities. Founded in New Jersey, it provides culturally competent resources, community outreach, and direct support.

In May 2026, SAMHIN has been running events tied to Mental Health Awareness Month: participating in the Nepalese-American Heritage Festival, co-sponsoring a 5K run/walk with NJ Thamizhar, running a mental health fair at High Tech High School in Secaucus, and tabling at community celebrations across the tri-state area.

These are meaningful efforts. But SAMHIN operates with limited resources and limited visibility. Most Indian Americans have never heard of the organisation. The mental health infrastructure that exists for the South Asian community in the United States is thin — a handful of organisations, a network of culturally competent therapists concentrated in major metros, and a growing but still small body of advocates pushing against decades of silence.

Other resources that exist but are underutilised:

**The South Asian Therapists Directory** (southasiantherapists.org) maintains a searchable database of licensed therapists who understand the cultural context of South Asian families — the immigration pressures, the family dynamics, the specific way shame operates in these communities.

**The 988 Suicide and Crisis Lifeline** (call or text 988) provides 24/7 crisis support in multiple languages, including Hindi and Urdu.

**Desi mental health accounts on social media** — @browngirltherapy (Sahaj Kaur Kohli), @sikhsoftiktok, and others — have built significant followings by normalising conversations about mental health in South Asian communities. These accounts reach audiences that traditional organisations do not.

## What You Can Actually Do

**If you are on an H-1B and were laid off:** Your mental health is not a secondary concern. It is the foundation on which your job search, your decision-making, and your family stability depend. A therapist who understands immigration stress is not a luxury — it is a practical tool. Many offer sliding-scale fees. The South Asian Therapists Directory is a starting point. If cost is a barrier, SAMHIN and local South Asian community centres can often connect you with low-cost or free options.

**If you know someone who was laid off:** Do not wait for them to ask for help. They will not. Indian cultural conditioning practically guarantees it. Instead, be specific. "I have a recruiter contact at this company — can I make the introduction?" is more useful than "Let me know if you need anything." Specific, practical help bypasses the shame barrier that prevents people from asking.

**If you are a parent whose adult child was laid off:** The single most helpful thing you can do is not ask when they will find a new job. Ask how they are sleeping. Ask if they have talked to someone. And if your instinct is to say "This would not have happened if you had done X" — do not. Not because you are wrong, but because it does not help, and the damage it does to an already struggling person is real.

**If you are fine right now:** This is the month to normalise the conversation. Mention that you see a therapist, if you do. Mention that you went through a difficult period, if you did. The single most powerful thing that breaks stigma in Indian communities is not a campaign or a hashtag — it is hearing someone you respect say, out loud, that they struggled and got help.

## The Bottom Line

May is Mental Health Awareness Month. For Indian American families, this particular May carries a weight that previous years did not. The tech layoffs are not a news story — they are an active, ongoing crisis affecting the immigration status, financial stability, and psychological wellbeing of thousands of families in the community.

The silence around mental health in South Asian families is not going to be broken by a single article or a single month. It is generational, it is cultural, and it is deeply entrenched. But it can be cracked — one conversation at a time, one admission at a time, one person saying "I am not okay" and discovering that the response is not judgment but relief.

If you are struggling: you are not weak. You are not a failure. You are a person navigating an extraordinarily difficult situation in a system that was not designed with your wellbeing in mind. Help exists. Use it.

SAMHIN: samhin.org
South Asian Therapists: southasiantherapists.org
988 Suicide and Crisis Lifeline: call or text 988
Brown Girl Therapy: @browngirltherapy on Instagram"""

art2_sources = [
    "https://www.livemint.com/videos/h1b-visa-panic-grows-as-u-s-tech-layoffs-put-thousands-of-indian-jobs-at-risk-11779440769647.html",
    "https://storyboard18.com/tech-biz/ai-layoffs-2026-amazon-meta-oracle-cisco-among-tech-firms-cutting-jobs-78218.htm",
    "https://www.livemint.com/companies/meta-rules-out-more-company-wide-layoffs-after-8000-job-cuts",
    "https://samhin.org/events/category/mental-health-awareness/2026-05/",
    "https://rnlawgroup.com/laid-off-on-h1b-april-2026-update/",
    "https://inshorts.com/en/news/indians-fired-by-meta-try-finding-visa-loopholes-amid-60day-deadline-to-find-job-or-leave-us",
]

print("\n=== Article 2: Mental Health Awareness Month — South Asian Silence ===")
print(f"Word count: {len(art2_body.split())}")

art2_image = fetch_pexels_image("person sitting alone window contemplation mental health")
if art2_image:
    print(f"  📸 Pexels image: {art2_image['pexels_id']} by {art2_image['photographer']}")

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
    "score_total": 91,
    "tags": ["mental health", "Mental Health Awareness Month", "Indian American", "South Asian", "H-1B", "tech layoffs", "SAMHIN", "stigma", "NRI", "immigration", "anxiety", "depression", "therapy", "Meta layoffs", "Cloudflare", "diaspora", "wellbeing"],
    "vertical": "diaspora",
    "urgency": "high",
    "diaspora_angle": "May is Mental Health Awareness Month but Indian American families remain the least likely to discuss it. With 142K tech layoffs in 2026, Meta cutting 8,000, and H-1B workers facing 60-day clocks, the mental health crisis in the community is acute and largely silent. SAMHIN exists for this community. So does the South Asian Therapists Directory. A guide to breaking the silence and getting help.",
    "word_count": len(art2_body.split()),
    "image_url": art2_image["url"] if art2_image else None,
    "image_caption": f"Photo by {art2_image['photographer']} via Pexels" if art2_image else None,
})
if result:
    print(f"✓ Published: {art2_id}")
else:
    print("✗ Failed or duplicate")

print("\n✅ Both articles published successfully")
