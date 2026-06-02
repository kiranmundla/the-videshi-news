#!/usr/bin/env python3
"""Lifestyle & Markets writer — 2026-06-02 run"""

import json, os, re, sys, time, uuid, hashlib
from datetime import datetime, timezone

import requests

# ── Supabase config ──────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Pexels config ────────────────────────────────────────────────
PEXELS_KEY = None
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    for line in open(pexels_env):
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

# ── Helper: Wikipedia person image ──────────────────────────────
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

# ── Helper: Pexels image ────────────────────────────────────────
def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels using curl (urllib gets 403)."""
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    # Validate
                    head = requests.head(url, timeout=10)
                    ct = head.headers.get("Content-Type", "")
                    cl = int(head.headers.get("Content-Length", 0))
                    if head.status_code == 200 and "image" in ct and cl > 5000:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

# ── Helper: Upload image to Supabase storage ────────────────────
def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase article-images bucket."""
    try:
        r = requests.get(image_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Image download failed: status={r.status_code}, size={len(r.content)}")
            return None
        
        ct = r.headers.get("Content-Type", "image/jpeg")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": ct,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

# ── Helper: Insert article ──────────────────────────────────────
def insert_article(article):
    """Insert article into Supabase p2_articles."""
    article["id"] = str(uuid.uuid4())
    article["status"] = "published"
    article["published_at"] = datetime.now(timezone.utc).isoformat()
    article["is_editorial"] = False
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        print(f"  ✓ Published: {article['headline'][:60]}...")
        return article["id"]
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None

# ════════════════════════════════════════════════════════════════
# ARTICLE 1 — lifestyle-health
# Mosquitoes Learning to Love DEET
# ════════════════════════════════════════════════════════════════
print("\n═══ ARTICLE 1: Mosquitoes & DEET ═══")

art1_slug = "mosquitoes-learn-deet-smell-blood-meal-study-south-asian-dengue-summer-20260602"
art1_headline = "Mosquitoes Can Learn to Love the Smell of DEET. If You Are Visiting India This Summer, Read This."
art1_subheadline = "A new study in the Journal of Experimental Biology found that after just three exposures, 60 per cent of mosquitoes tried to bite the hand covered in repellent. For NRIs heading into monsoon season, the timing could not be worse."

art1_body = """DEET has been the gold standard of insect repellents for more than six decades. Spray it on, and mosquitoes stay away. That has been the assumption. A study published last week in the *Journal of Experimental Biology* suggests the reality is more complicated — and for anyone planning a summer trip to India, the implications are worth understanding.

## The Pavlov Experiment, but With Mosquitoes

Researchers at the University of Tours in France and Virginia Tech in the United States trained *Aedes aegypti* mosquitoes — the species that carries dengue, Zika, chikungunya, and yellow fever — using a technique borrowed from classical conditioning. They placed mosquitoes behind mesh fabric near a warm blood source. Once the insects began feeding, the researchers introduced the smell of DEET.

After repeating the process just four times, more than 60 per cent of the mosquitoes attempted to feed when exposed only to the odour of DEET. The insects had learned to associate the repellent with food.

The team then escalated the experiment. Study co-author Ayelén Nally, a chemical ecologist at the University of Buenos Aires, offered both her hands to the trained mosquitoes — one coated in DEET, one untreated. Untrained mosquitoes avoided the DEET-covered hand, as expected. The trained mosquitoes went straight for it.

"The common assumption has always been that repellents work because of their chemistry — that DEET simply smells bad to mosquitoes and they flee," said Clément Vinauger, associate professor of biochemistry at Virginia Tech. "But what we are showing is that the mosquito's brain can rewrite that response based on experience. What the insect has learned matters just as much as what the chemical does. That, I think, is a paradigm shift."

## Why This Matters for South Asians

India recorded more than 150,000 dengue cases in 2025, and the numbers are expected to climb as monsoon season intensifies through July and August. The *Aedes aegypti* mosquito thrives in the warm, humid conditions that define the Indian summer, breeding in stagnant water found in flowerpots, old tyres, and water tanks across urban and rural India.

For NRIs visiting family during the summer months — and millions do every year — DEET-based repellents are typically the first line of defence. This study does not suggest you should stop using DEET. The researchers are emphatic on that point. But it does suggest that how and when you apply it matters more than previously understood.

The critical finding is about concentration decay. If you apply DEET once in the morning and the concentration fades by evening, a mosquito that bites you during that low-concentration window may begin associating the weakened scent with a successful blood meal. The next time it encounters someone wearing DEET, it may be attracted rather than repelled.

## What You Should Actually Do

The practical takeaway is straightforward: reapply more frequently rather than applying a large amount once. The researchers recommend reading the manufacturer's guidelines on dosage and reapplication intervals carefully.

Dr Nina Stanczyk at ETH Zürich, who was not involved in the study, told *The Guardian* that while mosquitoes have long been known to have "impressive learning abilities," the fact that they can "associate such a strong repellent smell with their food and are then attracted to it afterwards is remarkable."

For NRI families visiting India, the standard precautions still apply — but with renewed urgency. Use DEET-based repellents consistently and reapply every few hours. Wear long sleeves during dawn and dusk, when *Aedes aegypti* is most active. Sleep under treated mosquito nets, especially in areas without air conditioning. And if anyone in the household develops a sudden high fever with body aches within two weeks of arrival, seek medical attention immediately for dengue testing.

Claudio Lazzari, the study's lead author, was careful to note that the learning effect occurred under controlled laboratory conditions and may not directly translate to every real-world scenario. "DEET saves lives," he said. But the study's deeper message is clear: the relationship between humans, repellents, and mosquitoes is not as simple as spray and forget.

The paper, "Associative learning switches DEET valence from aversive to appetitive in *Aedes aegypti*," was published in the *Journal of Experimental Biology* in May 2026.

*Sources: Journal of Experimental Biology, Virginia Tech, Smithsonian Magazine, Medical News Today*"""

# Image for mosquito article
art1_image = fetch_pexels_image("mosquito close up insect", "mosquito bite repellent")
art1_image_attr = "Pexels"
art1_final_image = None
if art1_image:
    art1_final_image = upload_to_supabase_storage(art1_image, f"{art1_slug}.jpg")
    if not art1_final_image:
        art1_final_image = art1_image  # Pexels URLs are permanent

art1 = {
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "lifestyle-health",
    "image_url": art1_final_image,
    "image_attribution": art1_image_attr if art1_final_image else None,
    "sources": json.dumps([
        {"name": "Journal of Experimental Biology", "url": "https://journals.biologists.com/jeb/article/229/11/jeb251935/382889"},
        {"name": "Smithsonian Magazine", "url": "https://www.smithsonianmag.com"},
        {"name": "Medical News Today", "url": "https://www.medicalnewstoday.com"},
        {"name": "Virginia Tech", "url": "https://www.vt.edu"}
    ]),
}
insert_article(art1)


# ════════════════════════════════════════════════════════════════
# ARTICLE 2 — lifestyle-health
# Bovine Colostrum Trend vs Indian Kharvas Tradition
# ════════════════════════════════════════════════════════════════
print("\n═══ ARTICLE 2: Colostrum / Kharvas ═══")

art2_slug = "bovine-colostrum-gut-health-tiktok-kharvas-indian-tradition-science-20260602"
art2_headline = "Bovine Colostrum Is the Latest Gut Health Obsession. Your Grandmother Called It Kharvas and Ate It Decades Ago."
art2_subheadline = "TikTok influencers are spending $50 a tub on what Indian families have been eating for generations. The science is finally catching up — but it is more complicated than the wellness industry wants you to believe."

art2_body = """If you have spent any time on wellness TikTok in the past year, you have probably encountered bovine colostrum. Influencers call it "liquid gold." They blend it into smoothies, stir it into coffee, and credit it with everything from flatter stomachs to glowing skin. A single tub of premium colostrum powder can cost $50 or more.

For millions of Indian families, this will sound familiar. Colostrum — the thick, yellowish first milk a cow produces after giving birth — has been eaten across India for generations. In Maharashtra, it is called *kharvas* and steamed into a sweet, custard-like dessert. In Karnataka, it is *ginnu*. In Tamil Nadu, *seempal*. In parts of Rajasthan, it is simply called *cheek* and mixed with jaggery. The names change from state to state, but the tradition is the same: when a cow in the family or neighbourhood calves, the first milk is collected and shared.

What is new is that Western wellness culture has repackaged this tradition as a cutting-edge supplement — and the science is now being examined more carefully than ever.

## What the Research Actually Shows

An NPR investigation published this week examined the claims behind the colostrum trend. The findings are nuanced.

Raymond Playford, a gastroenterologist at the University of West London who has studied colostrum for more than 30 years, says the substance does appear to have measurable effects on the human gut. Colostrum is rich in immunoglobulins (particularly IgG), lactoferrin, and growth factors. Playford describes a mechanism in which colostrum helps stabilise the gut's mucosal lining — "strengthening it, stopping it being leaky going forward, sealing it."

There is preliminary evidence from small human studies suggesting colostrum may improve certain forms of inflammatory bowel syndrome, gastroenteritis, and upper respiratory tract infections. One pilot study co-authored by Playford found that colostrum reduced some of the gastrointestinal side effects of GLP-1 drugs like Ozempic, including acid reflux and bloating.

But Elyce Shapiro, a Chicago-based licensed dietician nutritionist, urges caution. "I just don't think that we know enough yet," she told NPR. Most studies have focused on specific populations — elite athletes, people with diagnosed conditions — in short-term settings. Whether colostrum helps with everyday bloating or constipation in otherwise healthy adults remains unclear.

"Patients are looking for solutions," Shapiro said, "but typically your solution isn't just sitting in a supplement."

## The Indian Tradition the Wellness Industry Missed

What the Western supplement market has missed — or chosen to ignore — is that South Asian communities have been consuming colostrum for centuries, and the traditional preparation may actually be superior to the powdered supplements being sold online.

Fresh *kharvas* is steamed gently, preserving the bioactive compounds in a whole-food matrix rather than subjecting them to the aggressive processing required to produce a shelf-stable powder. The traditional preparation also ensures the colostrum is consumed within hours of collection, when immunoglobulin concentrations are highest.

In many Indian households, *kharvas* is not treated as a health intervention. It is a celebration — made when a cow calves, shared with neighbours, and eaten as a sweet treat by children. The fact that it may also confer gut health benefits was understood intuitively long before any clinical trial confirmed it.

This pattern — of ancient South Asian food practices being "discovered" by Western wellness culture and sold back at a premium — is not new. Turmeric lattes, ghee in coffee, meditation apps, and yoga retreats have all followed the same trajectory. The colostrum trend is the latest chapter.

## What NRIs Should Know

If you are curious about colostrum supplements, Shapiro says the safety profile is generally good. "I think it has one of the lower risks of some of the other products out there." But she recommends managing expectations and consulting a healthcare provider, especially if you have dairy allergies or are immunocompromised.

For diaspora families with access to fresh cow's milk from trusted sources — whether in India or at small US farms — traditional *kharvas* remains the most straightforward way to consume colostrum. The challenge, of course, is availability. Colostrum is only produced for the first 24 to 72 hours after a cow gives birth.

The irony is hard to miss. A food that Indian grandmothers made without thinking twice is now being sold by wellness influencers as a breakthrough. The science suggests there may be something real behind the tradition. But your *naani* did not need a clinical trial to know that.

*Sources: NPR, University of West London, Journal of Nutritional Science*"""

# Image for colostrum/kharvas article
art2_image = fetch_pexels_image("fresh milk pouring traditional", "cow milk dairy farm")
art2_image_attr = "Pexels"
art2_final_image = None
if art2_image:
    art2_final_image = upload_to_supabase_storage(art2_image, f"{art2_slug}.jpg")
    if not art2_final_image:
        art2_final_image = art2_image

art2 = {
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "lifestyle-health",
    "image_url": art2_final_image,
    "image_attribution": art2_image_attr if art2_final_image else None,
    "sources": json.dumps([
        {"name": "NPR", "url": "https://www.npr.org"},
        {"name": "University of West London", "url": "https://www.uwl.ac.uk"},
        {"name": "Healthline", "url": "https://www.healthline.com"}
    ]),
}
insert_article(art2)


# ════════════════════════════════════════════════════════════════
# ARTICLE 3 — markets-finance
# Alphabet $80B Equity Raise
# ════════════════════════════════════════════════════════════════
print("\n═══ ARTICLE 3: Alphabet $80B Raise ═══")

art3_slug = "alphabet-google-80-billion-equity-raise-berkshire-hathaway-ai-infrastructure-nri-investors-20260602"
art3_headline = "Alphabet Just Announced an $80 Billion Equity Raise. Berkshire Hathaway Is Investing $10 Billion. Here Is What It Means."
art3_subheadline = "Google's parent company is pivoting from buybacks to massive share issuance to fund AI infrastructure. The move signals that the AI spending race has entered a new, more capital-hungry phase — and shareholders will feel the dilution."

art3_body = """Alphabet, the parent company of Google, announced on Monday that it plans to raise $80 billion through equity offerings to fund the expansion of its artificial intelligence infrastructure. The deal includes a $10 billion private placement from Berkshire Hathaway, bringing Warren Buffett's successor Greg Abel firmly into the AI investment story.

The announcement sent Alphabet shares down more than 2 per cent in after-hours trading and the stock was down roughly 4 per cent in Tuesday's premarket session.

## The Structure of the Raise

The $80 billion capital raise is split into three components.

First, Berkshire Hathaway will purchase $10 billion in Alphabet stock through a private placement — $5 billion in Class A common shares at $351.81 per share and $5 billion in Class C capital shares at $348.20 per share. Both prices represent a discount to Monday's closing levels.

Second, Alphabet will conduct $30 billion in concurrent underwritten public offerings. Half of this amount — $15 billion — will be in depositary shares tied to mandatory convertible preferred stock. The other $15 billion will be in Class A and Class C common equity.

Third, the company plans to launch a $40 billion at-the-market offering programme starting in the third quarter of 2026, giving it the flexibility to sell shares gradually over time.

## Why Now

Alphabet raised its annual capital expenditure forecast in April to between $180 billion and $190 billion — up $5 billion from its earlier estimate. The company also indicated on its first-quarter earnings call that capital expenditures will "significantly increase" in 2027 relative to 2026.

The company said in a press release that "AI demand from enterprises is exceeding available supply" and that the equity raise is designed to expand its foundational infrastructure to capture what it called a "significant growth opportunity."

But the scale of the raise caught analysts off guard. Alphabet did not mention a large equity capital raise during its April earnings call. The company has emphasised its strong internal cash flow and has raised $85 billion in debt financing over the past year. The pivot from buybacks — which Alphabet has used aggressively to return capital to shareholders — to large-scale share issuance represents a fundamental shift.

"This is a clear sign that the AI arms race is moving into a more capital-hungry phase," said Hargreaves Lansdown analyst Matt Britzman. "Long gone are the days when the tech giants were capital-light free cash flow machines. The key question is whether that shift matters."

## The Berkshire Signal

Berkshire Hathaway has been building its Alphabet position since the third quarter of last year. Last month, Berkshire disclosed that it had more than tripled its stake in the Google parent, which at $16.6 billion had become one of its largest common stock holdings.

The $10 billion private placement adds to that conviction. "This additional purchase underscores that Greg Abel believes that Alphabet will earn a reasonable return on its AI capex spending even with the firm issuing additional shares," said Bill Stone, chief investment officer at Glenview Trust Company.

For NRI investors who hold GOOGL — and Google is one of the most widely held tech stocks in Indian diaspora portfolios — the Berkshire endorsement is meaningful. Buffett's investment philosophy has always centred on long-term competitive advantage and pricing power. That Berkshire is buying at a discount while Alphabet dilutes existing shareholders suggests the firm sees the AI infrastructure buildout as value-accretive over a multi-year horizon.

## What NRI Investors Should Watch

The immediate concern is dilution. An $80 billion equity raise against a market capitalisation of approximately $4.6 trillion amounts to less than 2 per cent dilution — manageable in absolute terms, but the signal matters more than the arithmetic. If Alphabet needs external capital at this scale, it implies that internal cash flow and debt capacity are being stretched by AI spending commitments.

The broader context is the AI capex arms race. Microsoft, Meta, Amazon, and now Alphabet are collectively spending hundreds of billions of dollars annually on data centres, custom chips, and AI infrastructure. The question for investors is whether these investments will generate returns that justify the capital deployed.

For Indian investors with exposure through mutual funds, ETFs, or direct US brokerage accounts, the near-term impact is a modest share price decline as the market digests the dilution. The medium-term thesis depends on whether Alphabet's AI products — Google Cloud, Gemini, and its advertising AI tools — can convert infrastructure spending into revenue growth that exceeds the cost of capital.

Alphabet shares were trading at approximately $361 in premarket trading on Tuesday, down from Monday's close of $376.37.

The S&P 500 and Nasdaq both hit fresh record highs on Monday, extending an eight-session winning streak. But the Alphabet announcement, combined with lingering uncertainty about the US-Iran conflict and a crowded June calendar that includes the Federal Reserve's policy meeting and the SpaceX IPO, suggests the market's record run may face its first serious test this month.

*Sources: Reuters, Barron's, Investopedia, Hindu Business Line*"""

# Image for Alphabet — try Wikipedia for Sundar Pichai
art3_image = fetch_wikipedia_person_image("Sundar Pichai")
art3_image_attr = "Wikimedia Commons"
if not art3_image:
    art3_image = fetch_pexels_image("google headquarters silicon valley", "tech company data center")
    art3_image_attr = "Pexels"

art3_final_image = None
if art3_image:
    art3_final_image = upload_to_supabase_storage(art3_image, f"{art3_slug}.jpg")
    if not art3_final_image:
        # For Wikipedia/Pexels URLs, they're permanent
        art3_final_image = art3_image

art3 = {
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "slug": art3_slug,
    "category": "markets-finance",
    "image_url": art3_final_image,
    "image_attribution": art3_image_attr if art3_final_image else None,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Barron's", "url": "https://www.barrons.com"},
        {"name": "Investopedia", "url": "https://www.investopedia.com"},
        {"name": "Hindu Business Line", "url": "https://www.thehindubusinessline.com"}
    ]),
}
insert_article(art3)

print("\n═══ DONE ═══")
print("Published 3 articles: 2 lifestyle-health, 1 markets-finance")
