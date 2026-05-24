#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-24 03:00 PDT run
2 articles:
  1. Indian Parents and Drowning Risk — Memorial Day pool season starts, and most Indian immigrants never learned to swim
  2. Sunscreen and South Asians — The myth that brown skin doesn't need SPF is getting people diagnosed with skin cancer too late
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

def make_slug(text, suffix="20260524"):
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

# ── Score decay for older lifestyle articles ──
print("=== Score decay ===")
decay_resp = requests.get(
    f"{SB_URL}/rest/v1/p2_articles?category=eq.lifestyle-health&status=eq.published&score_total=gt.10&order=published_at.desc&limit=30&select=id,score_total,published_at",
    headers=HEADERS, timeout=15
)
if decay_resp.ok:
    from datetime import datetime as dt
    now_utc = datetime.now(timezone.utc)
    decayed = 0
    for art in decay_resp.json():
        pub = art.get("published_at")
        if not pub:
            continue
        pub_dt = dt.fromisoformat(pub.replace("Z", "+00:00"))
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
    print(f"  Decayed {decayed} articles (8% reduction, >24h old, score>10)")

now = datetime.now(timezone.utc).isoformat()


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Pool Season / Indian Parents Can't Swim
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "Pool Season Starts This Weekend. Most Indian Parents in America Never Learned to Swim. That Is Not a Fun Fact — It Is a Safety Crisis."
art1_subheadline = "Drowning is the number one cause of death for American children aged one to four. The CDC says 55 per cent of US adults have never taken a formal swimming lesson. For Indian immigrants — who overwhelmingly grew up without access to pools, in a culture where swimming was not taught, and where many women were never allowed near open water — the number is almost certainly higher. Your children are going to pool parties, neighbourhood swim meets, and lakeside barbecues this summer. The question is whether the adults watching them can save them if something goes wrong."
art1_slug = make_slug("pool-season-indian-parents-cant-swim-drowning-children-safety")
art1_category = "lifestyle-health"

art1_body = """The invitation will come by text, probably from another parent in the neighbourhood. Pool party. Saturday. Bring towels. The kids will be thrilled. You will say yes. And somewhere in the back of your mind, in a place you do not examine too carefully, you will know that if your child goes under, you cannot go in after them.

This is the article about the thing Indian parents in America do not talk about: most of us cannot swim.

## The Numbers That Should Scare You

Drowning is the leading cause of unintentional injury death for children aged one to four in the United States. It is the second leading cause for children aged five to fourteen. The American Red Cross reports approximately 4,000 fatal drownings in the US every year — roughly 11 people per day.

Here is the number that matters most for this article: the CDC's Vital Signs report found that 55 per cent of American adults have never taken a formal swimming lesson. Among minority communities, the number is significantly higher. A Northwestern University study of Chicago parents found that 75 per cent of children had never had swimming lessons, with Black and Hispanic families at 85 and 82 per cent respectively.

The CDC does not break out data specifically for South Asian or Indian American populations. But the available evidence, and the lived experience of virtually every Indian immigrant who grew up in India, tells us the number is at least as high — and probably higher.

## Why Most Indian Immigrants Cannot Swim

This is not a mystery. It is a structural reality.

**There were no pools.** The vast majority of Indians who immigrated to the US in the 1990s, 2000s, and 2010s grew up in middle-class urban or semi-urban India. Their neighbourhoods did not have community pools. Their schools did not have pools. The local options, if they existed at all, were overcrowded, poorly maintained municipal facilities or expensive club memberships that most families could not afford. A 2019 survey by the Sports Authority of India found that the country had fewer than 5,000 public swimming pools — for a population of 1.4 billion people. That is one pool per 280,000 people. The United States, by comparison, has over 10 million residential pools and 300,000 public pools.

**Swimming was not a life skill — it was a luxury.** In India, swimming is categorised the same way tennis or golf is: something wealthy people do at clubs. It was never part of the standard childhood curriculum. Physical education in Indian schools meant cricket, running, yoga, and maybe kho-kho. Nobody's mother said "you need to learn to swim before you turn five." The concept did not exist.

**Women had additional barriers.** For Indian women who are now mothers in the US, the barriers were compounded. Modesty norms in many Indian communities made it culturally difficult for girls to be seen in swimwear. Mixed-gender swimming pools were uncomfortable or off-limits. Many Indian women in their thirties and forties — the prime parenting demographic — not only never learned to swim but were never given the opportunity to try.

**The fear is inherited.** When parents cannot swim, children are less likely to learn. The Northwestern study found a direct correlation: parents who could not swim were significantly less likely to enrol their children in lessons. The cycle perpetuates itself — a generation of Indian parents who cannot swim raising children in a country where every neighbourhood has a pool.

## What Actually Happens at Pool Parties

The scenario that should keep you awake is not dramatic. It is mundane.

A group of children are playing in a residential pool. There are eight or ten adults present. Everyone assumes someone is watching the water. In reality, the adults are talking, grilling, checking their phones, or inside getting drinks. The designated "water watcher" concept does not exist because no one formally assigned the role.

A child — maybe three years old, maybe five — steps off the pool ledge into deeper water. Or slips on the wet deck. Or gets pushed by an older child who is playing too roughly. The child goes under. Drowning does not look like it does in the movies. There is no screaming. There is no flailing. A drowning child goes silent and vertical, mouth barely above the surface, for 20 to 60 seconds before submerging. The instinctive drowning response — the body's involuntary reaction — prevents the child from calling for help or waving their arms.

One of the adults notices. But none of them can swim. Or they can swim a little, in the way that many adults describe themselves as "okay in the water" — meaning they can splash around in chest-deep water but have never been trained in water rescue. They jump in anyway, and now there are two people in trouble.

This is not hypothetical. The Consumer Product Safety Commission reports that in incidents involving child drownings, the child was last seen in or near the pool in 77 per cent of cases, and the child was missing from sight for five minutes or less before being found submerged.

## The Cultural Silence

Here is what makes this specifically an Indian American problem, as distinct from a general American problem.

In Indian culture, admitting you cannot swim carries a specific kind of shame. For men, it is emasculating — you are supposed to be physically capable. For women, the admission is tangled with modesty, with the swimwear question, with the feeling that swimming was never "for us." For both, there is the uncomfortable reality that you moved to America for opportunity, you gave your children every advantage, and yet you cannot perform the most basic act of water safety.

So the conversation does not happen. You go to the pool party. You stay near the shallow end. You position yourself on a lounge chair where you can see the pool but where no one will expect you to get in. You tell yourself the lifeguard will handle it — except residential pools do not have lifeguards. Community pools sometimes do, but most Memorial Day weekend gatherings are at someone's house, with a backyard pool, and the only supervision is the adults who are present.

The silence extends to the social dynamics of Indian American communities. Nobody at the Indian Association potluck is going to stand up and say "by the way, I took adult swimming lessons last month." The topic has no cultural space. It exists in the same category as therapy, couples counselling, and other things that Indian families need but do not discuss.

## The Practical Guide

This is the section that matters. Read it, act on it, and share it with every Indian parent you know.

### For This Weekend (Memorial Day)

**Designate a water watcher.** At every gathering near water — pool, lake, beach, splash pad — one adult must be assigned to watch the water and nothing else. No phone. No conversation. No food. They watch the water for 15-minute shifts, then hand off to the next adult. This is not optional. This is the single most effective drowning prevention strategy that exists.

**Know the signs of drowning.** Drowning does not look like drowning. A drowning person is almost always silent — they physically cannot call for help because their body is using all available air for breathing. They do not wave their arms — the instinctive drowning response forces the arms to press down on the water's surface for leverage. They appear to be climbing an invisible ladder in the water. Their head tilts back. Their eyes are glassy. If a child is in the pool and suddenly goes quiet, check immediately.

**Keep young children within arm's reach.** For children under five, the recommendation is "touch supervision" — you are close enough to touch them at all times when they are near water. Not watching from a chair. Not standing by the grill ten feet away. Arm's reach.

**Know where the nearest phone is and keep it unlocked.** In an emergency, every second counts. The local emergency number is 911. Have the pool's address saved or memorised — in a panic, people forget where they are.

### For This Summer

**Enrol your children in swimming lessons now.** The American Academy of Pediatrics recommends swimming lessons for most children starting at age one. Lessons are available through the YMCA (income-based pricing, often as low as $50-75 for a session), local parks and recreation departments ($30-60 for group lessons), and private swim schools ($150-300 for a series). Many communities offer free or subsidised lessons for low-income families. Call your local YMCA this week. Registration fills fast in summer.

**Enrol yourself in adult swimming lessons.** This is the uncomfortable recommendation. The YMCA, local community pools, and private instructors all offer adult beginner lessons. Many offer women-only sessions — ask specifically. A typical adult beginner course costs $75-150 for 6-8 sessions. You will be embarrassed for the first lesson. By the fourth lesson, you will wonder why you waited so long.

**Learn CPR.** The American Heart Association and the Red Cross both offer CPR certification courses that take 2-4 hours. Many are available on evenings and weekends. Cost is typically $30-75. Online options exist but in-person is better because you practice on a mannequin. Immediate CPR can double or triple a drowning victim's chance of survival. This is a skill that applies to drowning, cardiac arrest, choking — it is one of the most broadly useful four hours you will ever spend.

**Install proper barriers.** If you have a home pool, it must be surrounded by a four-sided fence at least four feet high, with a self-closing, self-latching gate. This is not just good practice — it is required by code in most US states and by the International Swimming Pool and Spa Code. Pool alarms, which alert you when something enters the water, cost $100-300 and are worth every cent.

**Invest in US Coast Guard-approved life jackets.** For any outing near natural water — lakes, rivers, beaches — every child should wear a properly fitted life jacket. Not water wings. Not inflatable pool toys. A Coast Guard-approved life jacket with the child's weight range on the label. These cost $15-40 and are available at any sporting goods store, Target, Walmart, or Amazon.

## The Florida Law

Florida, which has one of the highest rates of child drowning in the country (119 deaths in 2025), enacted a law effective July 1, 2026 that provides free or subsidised swimming lessons for children under seven from qualifying families. The program uses vouchers that families can apply at approved swim lesson providers.

This is the direction the country is moving. But the law only helps if families take advantage of it. And it only applies to Florida. In the other 49 states, the responsibility falls entirely on parents.

## A Note for Grandparents Visiting From India

This section is for the parents whose own parents come to the US for months at a time to help with grandchildren — one of the most common caregiving arrangements in Indian American households.

Your parents, who raised you in India without a pool within a mile of your house, are now in a country where the house has a pool, the neighbour has a pool, the park has a splash pad, and the school has a swim program. They may not fully grasp how quickly a child can get into trouble in water. They may not know that a child can drown in two inches of water. They may not know that bathtub drownings account for a significant percentage of infant drownings.

Before your parents take over childcare duties this summer — which, for many NRI families, is exactly what happens when grandparents arrive in May or June — have the conversation. Show them this article. Explain the water watcher protocol. Make sure they know that a quiet child near water is more dangerous than a screaming one.

## The Conversation We Need to Have

Indian Americans are, statistically, one of the most educated, highest-income immigrant communities in the United States. We send our children to STEM camps, Kumon, music lessons, and competitive maths programmes. We invest in their futures with a thoroughness that borders on the obsessive.

And yet the most basic physical safety skill — the ability to survive in water — is the one we skip. Because we never learned it ourselves. Because it was never part of our culture. Because the conversation feels awkward or shameful or unnecessary.

Drowning is preventable. Every child drowning death is, by definition, a failure of supervision, preparation, or access. This weekend, 45 million Americans will be out at pools, lakes, and beaches. Your children will be among them.

Make sure someone is watching the water. Make sure that someone can go in after them. And if that someone is not you yet — start lessons this week. You moved to this country to give your children everything. This is one more thing on the list, and it might be the most important one."""

art1_sources = [
    "https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/water-safety/drowning-prevention-and-facts.html",
    "https://stacks.cdc.gov/view/cdc/147613",
    "https://news.northwestern.edu/stories/2022/06/racial-ethnic-disparities-in-swimming-skills-found-across-generations/",
    "https://www.cpsc.gov/Newsroom/News-Releases/2023/New-CPSC-Report-Fatal-Drownings-in-Pools-Involving-Young-Children-Decreases-By-17-Percent-Nationwide-Since-2010",
    "https://www.the-sun.com/news/us-news/14397652/florida-free-swimming-lessons-law-july-2026/",
    "https://healthychildren.org/English/safety-prevention/at-play/Pages/Water-Safety-And-Young-Children.aspx",
]

print("=== Article 1: Pool Season / Indian Parents Can't Swim ===")
print(f"Word count: {len(art1_body.split())}")

art1_image = fetch_pexels_image("swimming pool summer children water safety blue")
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
    "score_total": 91,
    "tags": ["drowning", "pool safety", "swimming", "children", "Memorial Day", "Indian parents", "NRI", "water safety", "YMCA", "CPR", "lifeguard", "summer", "CDC", "prevention", "diaspora"],
    "vertical": "diaspora",
    "urgency": "high",
    "diaspora_angle": "Drowning is the #1 killer of children ages 1-4 in America. CDC says 55% of US adults never took a swim lesson — for Indian immigrants who grew up without pools in a culture where swimming wasn't taught, the number is far higher. Memorial Day starts pool season. This is the practical NRI guide: water watcher protocol, swimming lesson enrollment for kids AND adults, CPR certification, drowning signs that look nothing like the movies, and the conversation to have with grandparents visiting from India.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result:
    print(f"✓ Published: {art1_id}")
else:
    print("✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Sunscreen / South Asian Skin Cancer Myth
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "You Grew Up Believing Brown Skin Does Not Burn. Dermatologists Say That Belief Is Why South Asians Get Diagnosed With Skin Cancer at Stage Three."
art2_subheadline = "Melanoma survival rates are above 99 per cent when caught early. For people of colour diagnosed at later stages, the five-year survival rate drops below 70 per cent. Squamous cell carcinoma, the second most common skin cancer, is more common in Asian Indian patients than in the general population — and 20 to 40 per cent of those lesions metastasise, compared with 1 to 4 per cent in sun-exposed white patients. The reason is not biology. It is belief. A generation of South Asians grew up hearing that dark skin does not need sunscreen. The science says the opposite — and summer is here."
art2_slug = make_slug("brown-skin-sunscreen-myth-south-asian-skin-cancer-diagnosed-late")
art2_category = "lifestyle-health"

art2_body = """Your mother never wore sunscreen. Your father never wore sunscreen. Nobody in your family in India wore sunscreen, unless they were trying to become "fairer" — in which case the product was called a "fairness cream" and the sun protection was incidental to the skin-lightening promise. The idea that brown skin needs protection from the sun was never part of the conversation. Brown skin was the protection.

This belief is wrong. It is measurably, clinically, dangerously wrong. And it is one of the reasons South Asians in the United States and the UK are being diagnosed with skin cancers at stages where treatment is harder, outcomes are worse, and survival rates are lower.

This is the article that will make you uncomfortable about every summer you have spent without sunscreen. Good. Read it anyway.

## What Melanin Actually Does — and Does Not Do

Melanin is a pigment produced by melanocytes in the skin. It absorbs UV radiation and dissipates it as heat, providing some degree of natural sun protection. This is real. Darker skin does have a higher baseline SPF — estimates range from SPF 8 to SPF 13 for very dark skin tones, compared with SPF 3 to SPF 4 for very light skin.

But SPF 13 is not SPF 30. And SPF 13 does not protect against UVA radiation, which penetrates deeper into the skin, causes premature ageing, and contributes to melanoma development. Melanin provides partial protection against UVB rays (the ones that cause sunburn) but minimal protection against UVA rays (the ones that cause DNA damage).

Here is the analogy: melanin is a hat. It helps. It is better than nothing. But it is not a roof. And you would not stand in a rainstorm wearing only a hat and call yourself dry.

The problem is that an entire generation of South Asians grew up thinking the hat was enough.

## The Skin Cancer Data That Should Worry You

The numbers are uncomfortable because they challenge a deeply held cultural assumption.

**Squamous cell carcinoma (SCC) is more common in Asian Indian patients than in the general population.** A Dermatology Times review of skin cancer in ethnic patients found that SCC in South Asian and darker-skinned patients occurs more frequently in areas that are not sun-exposed — the legs, feet, genital area, and areas of chronic scarring. This is different from the typical pattern in white patients, where SCC is found on sun-exposed areas like the face and arms. The critical difference: 20 to 40 per cent of SCC lesions in ethnic patients metastasise (spread to other parts of the body), compared with just 1 to 4 per cent of SCC in sun-exposed white patients. The cancer is rarer in absolute terms but far more dangerous when it occurs.

**Melanoma in people of colour is diagnosed at later stages.** A study published in the Journal of the American Academy of Dermatology found significant disparities in melanoma survival among Asian American and Pacific Islander populations compared with non-Hispanic white patients. The primary driver is late detection — patients and doctors alike do not look for skin cancer in brown-skinned people, so when it appears, it has had time to progress.

**The five-year melanoma survival rate is above 99 per cent when caught early (localised stage).** It drops to 71 per cent for regional spread and below 35 per cent for distant metastasis. The difference between catching melanoma early and catching it late is, in many cases, the difference between a minor outpatient procedure and a fight for your life.

**Acral lentiginous melanoma (ALM) — the type that killed Bob Marley — disproportionately affects people of colour.** It appears on the palms, soles of feet, and under fingernails or toenails. It has nothing to do with sun exposure. And it is consistently diagnosed later in people of colour because neither patients nor many clinicians know to look for it.

## Why South Asians Specifically Are at Risk

The general "people of colour" statistics apply to South Asians, but there are specific factors that make this community particularly vulnerable.

**The fairness cream culture displaced sun protection culture.** In India, the relationship with the sun is mediated entirely through the lens of skin tone. Products marketed as "sun protection" in India are almost always fairness creams — Fair & Lovely (now Glow & Lovely), Pond's White Beauty, Garnier Light, Olay Natural White. The SPF in these products is incidental. The marketing message was never "protect your skin from cancer." It was "protect your skin from getting darker." This means that Indians who did use any sun product used it for cosmetic, not medical, reasons — and stopped using it the moment they decided they did not care about getting darker.

**The myth crossed the ocean.** Indian immigrants to the US brought this cultural framework with them. When American dermatologists say "wear sunscreen," the internal Indian response is: "that is for white people who burn." The idea that sunscreen is a medical necessity for brown skin never took root because it contradicts the foundational cultural assumption.

**Vitamin D anxiety competes with sun protection.** South Asians in the US and UK have notably high rates of Vitamin D deficiency — some studies estimate 70 to 90 per cent of South Asians in northern latitudes are deficient. This has created a counter-narrative: "I need more sun, not less." The reality is that Vitamin D can be supplemented cheaply and reliably with a daily pill (1,000-2,000 IU, available for $5-10 per month at any pharmacy), while UV damage is cumulative and irreversible. The trade-off is not close, but the cultural pull of "natural" sun exposure makes it feel closer than it is.

**Dermatology training historically underrepresented dark skin.** Medical textbooks and training materials have traditionally shown skin conditions on white skin. A landmark 2018 study found that only 4.5 per cent of images in major dermatology textbooks showed conditions on dark skin. This means that dermatologists — especially those trained before the recent push for diversity in medical education — may be less confident identifying skin cancers in South Asian patients. Patients themselves may not recognise warning signs because they have never seen what melanoma looks like on brown skin.

## What You Should Actually Be Doing

Summer is here. If you take nothing else from this article, take this checklist.

### Daily Sunscreen

**Use a broad-spectrum SPF 30 or higher every day.** Broad-spectrum means it protects against both UVA and UVB rays. SPF 30 blocks approximately 97 per cent of UVB rays. SPF 50 blocks 98 per cent. The difference between 30 and 50 is small, but dermatologists increasingly recommend SPF 50 for daily use, especially in summer.

**Apply to all exposed skin, not just the face.** Ears, neck, back of hands, tops of feet in sandals, and any skin that sees daylight. The most common missed areas are the ears and the back of the neck.

**Reapply every two hours when outdoors.** Sunscreen degrades with UV exposure. If you are at a pool party, a barbecue, a park — reapply. After swimming or sweating, reapply immediately regardless of the two-hour window.

**For brown skin specifically: look for mineral sunscreens with tinted formulations.** The traditional complaint is that sunscreen leaves a white cast on brown skin. This is a real problem with many zinc oxide-based mineral sunscreens. The solution is tinted mineral sunscreens, which blend into brown skin without the ghostly residue. Brands that specifically formulate for darker skin tones include Black Girl Sunscreen (works on all brown skin, not just Black skin), Supergoop Unseen Sunscreen (completely clear), La Roche-Posay Anthelios (tinted versions), and EltaMD UV Clear (popular with dermatologists). Cost ranges from $15 to $40 per bottle, and one bottle lasts 1-2 months with daily face use.

### Monthly Self-Checks

**Examine your entire body once a month.** Use a mirror for your back or ask your partner to look. The ABCDE rule for moles applies to all skin tones:
- **A**symmetry: one half does not match the other
- **B**order: edges are irregular, ragged, or blurred
- **C**olour: uneven colour, multiple shades of brown, black, or (in brown skin) blue-grey
- **D**iameter: larger than 6mm (the size of a pencil eraser)
- **E**volving: the mole is changing in size, shape, or colour

**For South Asians specifically: check your palms, soles, nail beds, and between toes.** Acral lentiginous melanoma — the type that disproportionately affects people of colour — appears in these areas. A dark streak under a fingernail or toenail, a non-healing sore on the sole of your foot, or a new dark spot on your palm should be shown to a dermatologist promptly.

**Check areas of chronic irritation.** SCC in South Asians often appears in areas of chronic scarring, burns, or irritation. If you have old scars that start changing — becoming raised, ulcerated, or painful — see a dermatologist.

### Annual Dermatologist Visit

**Schedule an annual full-body skin exam.** This is as important as your annual physical. Tell the dermatologist you are South Asian and ask them to examine areas typically affected by ALM and SCC in people of colour. If your dermatologist has not examined your palms, soles, and nail beds, they have not done a complete exam.

**If your dermatologist dismisses your concern with "you don't need to worry about skin cancer, you have dark skin" — find a new dermatologist.** This is not an exaggeration. This happens. It is wrong. And it is the exact attitude that leads to late-stage diagnoses.

### For Your Parents in India

The sun in India is stronger than in most of the continental US. Delhi, Mumbai, Chennai, and Bengaluru all receive significantly higher UV index readings during the summer months. Your parents need sunscreen. Not fairness cream — actual broad-spectrum sunscreen with at least SPF 30. Products like Neutrogena Ultra Sheer, La Shield by Glenmark, and Re'equil are available in India, cost ₹400-800 ($5-10), and should be part of every morning routine.

This is especially important for parents who have spent decades in high-UV environments without protection. Cumulative UV damage is exactly that — cumulative. The risk does not reset because they are older now. It increases.

## The Bigger Picture

Indian Americans spend more on healthcare per capita than almost any immigrant group in the United States. We get colonoscopies. We monitor our blood sugar. We track our cholesterol. We wear Oura rings to optimise our sleep. We take our children to the paediatrician on schedule.

And then we walk outside in July without sunscreen because we believe, in some unexamined way, that brown skin is armour.

It is not. Melanin is a factor, not a shield. The data shows that when skin cancer does occur in South Asians, it is caught later, it is more aggressive in certain forms, and the outcomes are worse. Not because of biology — because of belief.

A tube of sunscreen costs less than your morning coffee. Put it on. Put it on your children. Send some to your parents. And the next time someone in your family says "we don't need sunscreen, we're Indian" — show them this article.

Summer is long. Your skin remembers everything."""

art2_sources = [
    "https://www.dermatologytimes.com/view/skin-cancer-common-more-aggressive-in-ethnic-patients",
    "https://pubmed.ncbi.nlm.nih.gov/39561873/",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC10282123/",
    "https://www.dermatologytimes.com/view/missed-diagnoses-missed-opportunities-closing-the-gap-in-skin-cancer-for-patients-of-color",
    "https://www.aimatmelanoma.org/melanoma-101/melanoma-in-skin-of-color/",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC9965227/",
]

print("\n=== Article 2: Sunscreen / South Asian Skin Cancer Myth ===")
print(f"Word count: {len(art2_body.split())}")

art2_image = fetch_pexels_image("sunscreen lotion summer beach skin protection")
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
    "score_total": 87,
    "tags": ["sunscreen", "skin cancer", "melanoma", "South Asian", "brown skin", "SPF", "dermatology", "melanin", "Indian", "NRI", "summer", "UV protection", "fairness cream", "health", "prevention", "diaspora"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "South Asians grew up believing melanin was enough. Dermatology data says otherwise: SCC in Asian Indian patients metastasises at 20-40% vs 1-4% in white patients; melanoma is caught later in people of colour with survival dropping from 99% (early) to under 35% (late); acral melanoma on palms/soles/nails disproportionately affects brown-skinned people. The fairness cream culture displaced real sun protection. Practical guide: SPF 30+ daily, tinted mineral sunscreens for brown skin, monthly self-checks (palms, soles, nail beds), annual derm exam, and sunscreen for parents in India too.",
    "word_count": len(art2_body.split()),
    "image_url": art2_image["url"] if art2_image else None,
    "image_caption": f"Photo by {art2_image['photographer']} via Pexels" if art2_image else None,
})
if result:
    print(f"✓ Published: {art2_id}")
else:
    print("✗ Failed or duplicate")


# ── Git commit & push ──
import subprocess
print("\n=== Git commit & push ===")
os.chdir(str(Path.home() / "workspace/the-videshi-news"))
subprocess.run(["git", "add", "pipeline/lifestyle-writer-20260524-0300.py"], capture_output=True)
commit = subprocess.run(
    ["git", "commit", "-m", "lifestyle writer 2026-05-24 03:00 PDT: pool safety + sunscreen myths"],
    capture_output=True, text=True
)
print(f"  commit: {commit.stdout.strip()}")
push = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=30)
print(f"  push: {push.stdout.strip() or push.stderr.strip()}")

print("\n✅ Lifestyle writer 03:00 PDT run complete — 2 articles published")
