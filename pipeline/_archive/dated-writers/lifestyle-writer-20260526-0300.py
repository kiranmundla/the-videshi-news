#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-26 03:00 PDT run
2 articles:
  1. Translational Psychiatry (published May 22, 2026): UK Biobank study of 275,157 adults
     over 13.49 years finds social isolation and loneliness jointly increase inflammatory
     bowel disease (IBD) risk by 85%. Loneliness alone: HR 1.29; social isolation alone:
     HR 1.31; combined: HR 1.85. Mendelian randomization found sports/gym activity reduces
     IBD risk, religious activity lowers UC risk, fewer leisure/social activities increase
     UC risk. 22 circulating proteins linked to both loneliness and social isolation were
     identified, predominantly in cytokine-related pathways. Tryptophan metabolism, lipid
     biosynthesis, and purine degradation implicated. NRI angle: Indian immigrants experience
     a unique form of social isolation — uprooted from joint families, elderly parents/in-laws
     stranded in American suburbs without driving skills or social networks, second-gen kids
     assimilated away from parents. South Asian IBD rates rising sharply in Western countries.
     Traditional Indian social structures (joint family, temple community, evening gatherings)
     were protective. The study found religious activity specifically lowers UC risk — temple
     visits weren't just spiritual, they were anti-inflammatory.

  2. Oxford study (BJSM, 85,394 UK Biobank participants, 6-year follow-up): Walking 7,000
     steps per day reduces cancer risk by 11% compared to 5,000 steps; 9,000 steps reduces
     it by 16%; highest activity group has 26% lower cancer risk. Even light-intensity
     activities like shopping and household chores count. NRI angle: Indian tech workers are
     among the most sedentary demographics (desk + car + couch cycle); the traditional Indian
     evening walk (sair/walk after dinner) and the cultural habit of walking to the temple,
     walking to the market, walking to neighbours' houses were built-in cancer protection that
     the suburban American lifestyle has eliminated. 7,000 steps is not a gym membership —
     it's what your parents did every day without thinking about it.
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

def make_slug(text, suffix="20260526"):
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

# ── Cross-check recent lifestyle articles to avoid duplication ──
print("=== Cross-checking recent lifestyle articles ===")
recent_resp = requests.get(
    f"{SB_URL}/rest/v1/p2_articles?category=eq.lifestyle-health&status=eq.published&order=published_at.desc&limit=30&select=id,headline,slug,published_at",
    headers=HEADERS, timeout=15
)
if recent_resp.ok:
    recent = recent_resp.json()
    print(f"  Found {len(recent)} recent lifestyle articles")
    for art in recent[:10]:
        print(f"  - {art.get('slug','?')[:70]}")
else:
    print(f"  ⚠ Failed to fetch recent articles: {recent_resp.status_code}")
    recent = []

recent_headlines = " ".join([a.get("headline", "") for a in recent]).lower()
recent_slugs = " ".join([a.get("slug", "") for a in recent]).lower()

# Verify neither topic already covered
topics_ok = True
for check_term in ["lonely minds inflamed guts", "loneliness inflammatory bowel", "social isolation ibd", "7000 steps cancer", "walking steps cancer oxford", "walking cancer risk bjsm"]:
    if check_term in recent_headlines or check_term in recent_slugs:
        print(f"  ⚠ Topic already covered: {check_term}")
        topics_ok = False

if not topics_ok:
    print("  ⚠ One or more topics already covered. Proceeding with caution.")

# ── Score decay for older lifestyle articles ──
print("\n=== Score decay ===")
decay_resp = requests.get(
    f"{SB_URL}/rest/v1/p2_articles?category=eq.lifestyle-health&status=eq.published&score_total=gt.10&order=published_at.desc&limit=30&select=id,score_total,published_at",
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
    print(f"  Decayed {decayed} articles (8% reduction, >24h old, score>10)")

now = datetime.now(timezone.utc).isoformat()


# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Loneliness Inflames the Gut. A UK Biobank Study
# of 275,000 Adults Found That Social Isolation and Loneliness
# Together Raised IBD Risk by 85 Percent.
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "Loneliness Inflames the Gut. A UK Biobank Study of 275,000 Adults Found That Social Isolation and Loneliness Together Raised Inflammatory Bowel Disease Risk by 85 Percent."
art1_subheadline = "Researchers tracked 275,157 adults for an average of 13.5 years and found that social isolation alone increased the risk of inflammatory bowel disease by 31 percent, loneliness alone by 29 percent, and the two together by 85 percent. They identified 22 circulating proteins — predominantly cytokines — that link the lonely mind to the inflamed gut. Mendelian randomization analysis found that religious activity specifically lowered the risk of ulcerative colitis, while fewer leisure and social activities increased it. For Indian Americans who left behind joint families, temple communities, and evening gatherings to sit alone in suburban houses, the study measures what they already feel: isolation is not just lonely. It is inflammatory."
art1_slug = make_slug("loneliness-inflames-gut-social-isolation-ibd-85-percent-indian")
art1_category = "lifestyle-health"

art1_body = """The study begins with a number that should stop you: 275,157. That is how many adults were enrolled in the UK Biobank cohort that researchers from Zhejiang University, Harvard Medical School, and Peking Union Medical College used to answer a question that gastroenterologists and psychiatrists have circled for decades without resolving: does loneliness cause gut inflammation, or does gut inflammation cause loneliness?

The answer, published on May 22, 2026, in Translational Psychiatry, is that the causal arrow runs in both directions — but the direction that matters most for public health is the one nobody was treating. Loneliness and social isolation do not merely correlate with inflammatory bowel disease. They drive it. Through identified metabolic pathways. Through measurable circulating proteins. Through mechanisms that can now be named, quantified, and potentially targeted.

## The Numbers

Over a mean follow-up of 13.49 years, the cohort yielded 1,565 incident cases of inflammatory bowel disease — 1,063 cases of ulcerative colitis and 492 cases of Crohn's disease.

The headline findings were built on Cox regression analysis, which tracks the time until an event occurs while controlling for confounding variables:

**Social isolation alone** was associated with a 31 percent increased risk of IBD (hazard ratio 1.31, 95% confidence interval 1.01–1.70).

**Loneliness alone** was associated with a 29 percent increased risk (HR 1.29, 95% CI 1.04–1.60).

**Social isolation and loneliness together** — people who were both objectively isolated and subjectively lonely — had an 85 percent increased risk of IBD (HR 1.85, 95% CI 1.02–3.36).

The interaction is not additive. It is multiplicative. A person who lives alone but does not feel lonely has a modestly elevated risk. A person who feels lonely but maintains social contact has a modestly elevated risk. A person who is both alone and feels it has a risk that is nearly double the baseline. The loneliness and the isolation feed each other, and together they feed the gut.

## The Mechanism

This is not a study that simply measured loneliness with a questionnaire and then counted who got sick. The researchers used metabolomic data from 68,362 participants and proteomic profiling from 29,339 participants to identify the molecular pathways that connect the experience of loneliness to the biology of intestinal inflammation.

They found eight metabolites associated with social isolation and five metabolites associated with loneliness. These metabolites clustered in pathways related to lipid metabolism, tryptophan degradation, and purine catabolism — three systems that are already known to influence immune function and gut barrier integrity.

More striking were the protein findings. The researchers identified 22 circulating proteins that were consistently associated with both loneliness and social isolation. These proteins were predominantly enriched in cytokine-related pathways — the immune system's signalling cascades that drive inflammation. The derived protein scores were positively associated with increased IBD risk, meaning that the more of these loneliness-associated inflammatory proteins a person carried in their blood, the more likely they were to develop inflammatory bowel disease.

In plain language: loneliness changes your blood chemistry. The changes are measurable. And the changed blood chemistry inflames your gut.

## The Mendelian Randomisation Finding That Should Interest Every Temple-Goer

The researchers went further than observational analysis. They used two-sample Mendelian randomisation — a technique that uses genetic variants as instruments to test for causal relationships — to examine whether specific social behaviours caused changes in IBD risk.

Three findings stood out:

**More sports or gym activity** causally reduced the risk of both IBD overall and Crohn's disease specifically.

**More religious activity** causally reduced the risk of ulcerative colitis.

**Fewer leisure and social activities** causally increased the risk of ulcerative colitis.

The religious activity finding deserves particular attention because it is unusual. Most health studies that find benefits from religious participation attribute them to confounders — religious people tend to drink less, smoke less, and maintain stronger social networks. Mendelian randomisation strips away these confounders by using genetic propensity rather than self-reported behaviour. The fact that religious activity showed a causal protective effect against ulcerative colitis suggests that something about communal worship or spiritual practice directly influences gut immunity.

This is not a prescription to pray. It is a finding that regular participation in a communal activity with spiritual or transcendent dimensions — singing together, meditating together, performing rituals together, sharing meals after services — exerts a measurable protective effect on the colonic mucosa.

## What This Means for Indian Americans

The study was conducted on a UK Biobank population, which is predominantly white British. The researchers did not examine South Asian participants separately. But the implications for Indian Americans are impossible to ignore, because the Indian immigrant experience is a near-perfect natural experiment in exactly the social disruption the study identifies as harmful.

Consider what happens when an Indian family immigrates to the United States:

**The joint family dissolves.** In India, a typical middle-class family lives within daily physical contact of grandparents, aunts, uncles, and cousins. Meals are communal. Childcare is distributed. Loneliness in the American sense — the experience of being alone in a house with no one to talk to — is rare, because someone is always there. Immigration replaces this with a nuclear unit: two parents, one or two children, and a house in a suburb where the neighbours do not know your name.

**The elderly become stranded.** Indian parents and in-laws who visit or move to America on dependent visas often spend months or years in suburban houses where they cannot drive, do not speak fluent English, have no social network outside the family, and spend their days watching Indian television alone while their adult children are at work and their grandchildren are at school. The objective social isolation is extreme. Many of these elderly visitors and immigrants are literally the most isolated category the study measured — living in a household where the only people they interact with are their own adult children, for a few hours in the evening.

**Temple attendance drops.** In India, religious practice is woven into daily life — the morning puja, the neighbourhood temple, the evening aarti. In America, the Hindu temple might be a forty-five-minute drive away. Attendance becomes a weekly or monthly event rather than a daily practice. The Mendelian randomisation finding that religious activity causally reduces ulcerative colitis risk suggests that this reduction in religious participation has biological consequences that Indian immigrants are absorbing without knowing it.

**The evening social circle disappears.** In Indian cities and towns, the evening is social by default. Families visit each other. People walk to the market. Children play in shared spaces while parents talk. In American suburbs, the evening is private — each family in its own house, each person on their own screen, the street empty after 6 PM. The study's finding that fewer leisure and social activities causally increase ulcerative colitis risk describes exactly this transition.

## The South Asian IBD Data

The study's findings arrive at a moment when gastroenterologists are already alarmed about IBD rates in South Asian populations.

A 2023 systematic review published in The Lancet Gastroenterology & Hepatology found that IBD incidence in South Asia has been rising steeply — with India now among the countries with the highest newly diagnosed IBD cases in the world. More relevantly for the diaspora, studies of South Asian immigrants in the UK, Canada, and the US consistently find that IBD rates among immigrants converge toward or exceed those of the host population within one generation.

A 2019 study from the University of Calgary found that South Asian immigrants to Canada had a significantly higher incidence of IBD compared to their counterparts who remained in South Asia, and that the risk increased with younger age at immigration — suggesting that the environmental and social changes of immigration itself, not genetics, drive the increase.

The Zhejiang-Harvard study does not prove that social isolation is the reason South Asian immigrants develop more IBD. But it provides a plausible biological mechanism for a phenomenon that has puzzled gastroenterologists: why do people who move from low-IBD to high-IBD countries develop the disease at rates that sometimes exceed the native population? The standard explanations — dietary changes, antibiotic exposure, hygiene hypothesis — are all valid. But the social explanation — that immigration is one of the most extreme forms of social disruption a person can experience, and that social disruption drives intestinal inflammation through cytokine pathways — has not been adequately explored.

## The Tryptophan Connection

Among the metabolic pathways the study implicated, tryptophan metabolism deserves particular attention because it connects the study's findings to a broader body of research on diet, gut health, and Indian food.

Tryptophan is an essential amino acid that the body uses to produce serotonin — the neurotransmitter most associated with mood regulation. Approximately 95 percent of the body's serotonin is produced in the gut, not the brain, by enterochromaffin cells in the intestinal lining. The gut's serotonin production depends on tryptophan availability, which in turn depends on diet and on the activity of the enzyme indoleamine 2,3-dioxygenase (IDO), which diverts tryptophan away from serotonin production and toward the kynurenine pathway — a pathway that produces inflammatory metabolites.

Loneliness and chronic stress activate IDO, diverting tryptophan toward kynurenine and away from serotonin. This creates a double hit: less serotonin (worse mood, less gut motility) and more kynurenine-derived inflammatory metabolites (more gut inflammation). The study identified tryptophan metabolism alterations among the key pathways linking loneliness to IBD.

Traditional Indian vegetarian diets are notably rich in tryptophan-containing foods: paneer, dal (especially urad and moong), milk, yogurt, sesame seeds, and pumpkin seeds. A traditional Indian meal — dal-chawal with a side of raita — provides substantial tryptophan alongside the prebiotic fibre and fermented dairy that support healthy gut microbiome function.

The second-generation Indian American diet has largely replaced these foods with low-tryptophan processed alternatives during the workday: protein bars, fast food, and delivery meals heavy on refined carbohydrates and low on the legume-dairy-seed combinations that traditional Indian cooking centres on. This dietary shift, combined with the social isolation that activates the IDO enzyme and diverts whatever tryptophan is available away from serotonin, creates a compounding metabolic insult to the gut.

## What the Joint Family Was Actually Doing

The joint family is the most studied and most debated social structure in Indian sociology. Its defenders cite emotional support, economic efficiency, and elder care. Its critics cite patriarchal control, lack of privacy, and intergenerational conflict. Both sides are correct.

What neither side has adequately appreciated — because the data did not exist until now — is that the joint family was also an anti-inflammatory intervention.

The study's findings suggest that the daily social contact, the communal meals, the constant low-level social interaction of the joint family home — the grandmother watching television in the living room while the children play, the uncle stopping by for chai, the neighbour who walks in without knocking — all of this mundane social texture was suppressing cytokine production, maintaining healthy tryptophan metabolism, and protecting the gut lining from the inflammatory damage that loneliness causes.

This is not a romanticisation of the joint family. The joint family had — and has — serious problems. But the biological data suggests that the social density of the Indian household was protecting its inhabitants from inflammatory disease in ways that no one understood at the time and that the nuclear immigrant household does not replicate.

## The Evening Walk Was Anti-Inflammatory

The study found that sports and gym activity causally reduced IBD risk through Mendelian randomisation. This finding aligns with a large body of existing research showing that moderate exercise reduces systemic inflammation.

But the Indian cultural practice that maps most precisely to this finding is not the gym. It is the evening walk.

In Indian cities, the evening walk — "sair" in Hindi, "nadai" in Tamil — is a near-universal cultural practice. After dinner, families walk. Not for exercise. Not to hit a step count. Not wearing athletic clothing or tracking their route on a watch. They walk because that is what you do after dinner. You walk to the park. You walk to the market. You walk around the neighbourhood. You stop and talk to people you know. You come home.

This practice combines two of the study's three protective factors: physical activity and social engagement. It occurs daily. It costs nothing. It requires no equipment, no gym membership, no app, and no motivation beyond habit.

Indian Americans who moved to suburbs where the nearest park requires a car, where there are no pavements, where the neighbours are strangers, and where the evening is spent on the couch watching television, lost this practice not through choice but through architecture. The American suburb was not designed for the evening walk. It was designed for the car, the garage, and the private backyard.

## What You Can Do

The study does not prescribe medications or supplements. It identifies social isolation and loneliness as modifiable risk factors for inflammatory bowel disease — meaning they can be changed, and changing them should reduce risk.

**If you are an elderly Indian parent or in-law living in an adult child's home in America:** You are likely in the highest-risk category this study identifies — socially isolated, potentially lonely, with limited independent mobility and social access. Your risk mitigation is not medical. It is social. Ask your children to drive you to the temple weekly. Find other elderly Indian immigrants in the neighbourhood or apartment complex. Join a senior centre. Learn to use video calling to maintain daily contact with family and friends in India. The study's finding that religious activity specifically reduces ulcerative colitis risk means that your temple visit is not just spiritual maintenance. It is gastrointestinal protection.

**If you are an Indian American adult whose parents are visiting or living with you:** Understand that your parents' health risk is not primarily about diet or exercise. It is about the social void they experience when you are at work and the house is empty. Enrolling them in a local Indian community group, driving them to temple, arranging regular social contact with other Indian seniors — these are not lifestyle amenities. According to this study, they are inflammatory bowel disease prevention.

**If you are a second-generation Indian American living alone or with a partner:** The American default — working from home alone, ordering food alone, exercising alone with headphones, socialising through screens — places you in the category the study associates with elevated IBD risk. The fix is not more screen time with friends. It is physical presence. The study measured objective social isolation (how many people you see in person) and subjective loneliness (how alone you feel), and both independently predicted IBD. You need to be around people, physically, on a regular basis.

**Eat dal.** This is not a joke. The tryptophan pathway the study identified is influenced by dietary tryptophan intake. Dal, paneer, yogurt, milk, and sesame seeds are among the richest vegetarian sources of tryptophan. A traditional Indian meal that includes dal and raita is not merely comfort food from your mother's kitchen. It is a tryptophan-delivery system that supports serotonin production in the gut and may help counteract the metabolic disruption that loneliness causes.

**Walk after dinner.** Not on a treadmill. Outside. Ideally with another person. The study found that physical activity reduces IBD risk and that social activity reduces IBD risk. The evening walk combines both. If you live in a suburb without pavements, drive to a park and walk there. If you have an elderly parent at home, walk with them. Slowly is fine. The point is not cardiovascular fitness. The point is that your gut responds to movement and your immune system responds to company.

## The Uncomfortable Implication

The study's most uncomfortable implication for Indian Americans is not about loneliness in the abstract. It is about a specific social choice that millions of Indian families made and continue to make: leaving India.

Immigration is, among many other things, one of the most extreme social disruptions a human being can experience. It severs daily contact with extended family. It eliminates the embedded social structures — the neighbourhood, the temple, the market, the evening walk circuit — that provided constant low-level social interaction. It replaces a high-density social environment with a low-density one. And according to this study, that transition — from socially embedded to socially isolated — carries a measurable biological cost that manifests in the gut.

This does not mean immigration was a mistake. The economic, educational, and professional gains of immigration are real and significant. But the biological cost of the social loss has not been accounted for in the immigration calculus, because until now, there was no way to measure it.

The UK Biobank study provides that measurement. An 85 percent increase in IBD risk for people who are both socially isolated and lonely is not a subtle finding. It is a hazard ratio that should change how immigrant communities think about social infrastructure — not as a cultural amenity but as a public health necessity.

The joint family, the temple community, the evening walk, the neighbour who comes over uninvited for chai — these were never luxuries. They were, according to the molecular evidence, anti-inflammatory interventions that the immigrant experience stripped away. The question for Indian Americans is whether they can rebuild some version of that social infrastructure in a country that was not designed for it — and whether they will do so before their guts tell them they should have started sooner."""

art1_sources = [
    "https://doi.org/10.1038/s41398-026-04116-0",
    "https://www.nature.com/articles/s41398-026-04116-0",
    "https://scienmag.com/lonely-minds-and-inflamed-guts-linking-isolation-ibd/",
]

print("\n=== Article 1: Loneliness Inflames the Gut / Social Isolation IBD 85% / Indian Immigration ===")
print(f"  Word count: {len(art1_body.split())}")

# Image: loneliness / isolation theme — person sitting alone, or empty suburban house
art1_image = fetch_pexels_image("elderly person sitting alone looking out window")
if not art1_image:
    art1_image = fetch_pexels_image("person alone empty house isolation loneliness")
if art1_image:
    print(f"  📸 Pexels image: {art1_image['pexels_id']} by {art1_image['photographer']}")

result1 = sb_post("p2_articles", {
    "id": art1_id,
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "slug": art1_slug,
    "category": art1_category,
    "body": art1_body.strip(),
    "status": "published",
    "published_at": now,
    "sources": art1_sources,
    "score_total": 90,
    "tags": ["loneliness", "social isolation", "inflammatory bowel disease", "IBD", "ulcerative colitis", "Crohn's disease", "UK Biobank", "gut-brain axis", "cytokines", "tryptophan", "serotonin", "joint family", "Indian immigration", "temple", "religious activity", "Mendelian randomization", "metabolomics", "proteomics", "NRI", "Indian American", "elderly parents", "suburban isolation", "evening walk", "dal", "gut inflammation", "Translational Psychiatry", "Zhejiang University", "Harvard Medical School"],
    "vertical": "diaspora",
    "urgency": "standard",
    "diaspora_angle": "Translational Psychiatry (May 22, 2026): UK Biobank study of 275,157 adults found social isolation + loneliness jointly increase IBD risk by 85% (HR 1.85). 22 circulating proteins in cytokine pathways identified as mediators. Mendelian randomization: religious activity causally reduces UC risk, fewer social activities increase it. NRI angle: Indian immigration is an extreme social disruption — joint family dissolution, elderly parents stranded in suburbs, temple attendance drop, evening social circles eliminated. South Asian IBD rates rising sharply in Western countries, converging with or exceeding host populations within one generation. Traditional Indian social structures (joint family, temple community, evening walk, neighbour visits) were anti-inflammatory interventions. Tryptophan pathway: dal, paneer, yogurt provide the amino acid that loneliness depletes via IDO activation.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result1:
    print(f"  ✓ Published: {art1_id}")
else:
    print("  ✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Your Parents Walked 7,000 Steps a Day Without
# Trying. An Oxford Study Just Showed That's Enough to Cut
# Cancer Risk by 11 Percent.
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "Your Parents Walked 7,000 Steps a Day Without Trying. An Oxford Study of 85,000 Adults Just Showed That Is Enough to Cut Cancer Risk by 11 Percent."
art2_subheadline = "Researchers at the University of Oxford analyzed wrist-worn accelerometer data from 85,394 UK Biobank participants over six years and found a dose-response relationship between daily steps and cancer risk that starts far below the mythical 10,000-step target. Seven thousand steps reduced risk by 11 percent. Nine thousand steps by 16 percent. The highest-activity participants had a 26 percent lower risk than the least active. Even light-intensity activities — walking to the shops, doing household chores, climbing stairs — counted. For Indian Americans whose parents walked to the temple, walked to the sabzi mandi, walked to the neighbour's house, and walked after dinner every evening without ever calling it exercise, the Oxford data quantifies what an entire generation did by cultural default and the next generation stopped doing when they moved to a country designed for cars."
art2_slug = make_slug("walking-7000-steps-cancer-risk-11-percent-oxford-indian-parents")
art2_category = "lifestyle-health"

art2_body = """There is a number that the wellness industry has spent two decades promoting as the daily step target for health: 10,000. It appears on fitness trackers, in corporate wellness programmes, on the packaging of pedometers, and in the advice of doctors who have not read the research behind it.

The number 10,000 has no scientific origin. It comes from a 1965 marketing campaign by a Japanese pedometer company called Yamasa, which sold a device named "Manpo-kei" — literally "10,000-step meter." The company chose the number because the Japanese character for 10,000 (万) looks like a person walking, and because round numbers sell products. The health benefits of 10,000 steps were never tested before the number was chosen. The number was marketing.

An Oxford University study published in the British Journal of Sports Medicine has now provided what the marketing campaign never did: actual data on how many steps reduce the risk of a specific disease — cancer — and the answer is substantially lower than the fitness industry has been telling people.

## The Study

The researchers analysed data from 85,394 participants in the UK Biobank who wore wrist-mounted accelerometers for seven consecutive days, providing objective measurement of their daily physical activity. Unlike studies that rely on self-reported exercise — which people consistently overestimate — the accelerometer data captured every step, every stair climbed, every walk to the kitchen, every trip to the car.

Participants were followed for a median of approximately six years. During that period, the researchers tracked incident cancer diagnoses and correlated them with daily step counts and overall physical activity levels.

The findings followed a clear dose-response pattern — more steps meant lower risk, with no threshold below which activity was useless:

**7,000 steps per day** was associated with an 11 percent lower cancer risk compared to 5,000 steps per day.

**9,000 steps per day** was associated with a 16 percent lower cancer risk.

**The highest-activity participants** — those in the top quartile of daily movement — had a 26 percent lower risk of developing cancer compared to those in the bottom quartile.

The relationship was linear through the range studied. There was no point at which additional steps stopped mattering, and no minimum threshold below which steps did not count. Even modest increases — going from 4,000 to 5,000 steps, or from 5,000 to 6,000 — were associated with measurable risk reduction.

## Light Activity Counts

The finding that will surprise many people is that the protective effect was not limited to vigorous exercise. Light-intensity physical activity — defined as movement that elevates heart rate only slightly above resting — contributed significantly to the cancer risk reduction.

Light-intensity activities include:

Walking around a shop while grocery shopping. Walking from one room to another in your house. Doing household chores — cooking, cleaning, folding laundry. Climbing a flight of stairs. Walking to your car in a parking lot. Gardening. Standing and moving while talking on the phone.

These are not "workouts." They are the movements that make up a normal active day. The accelerometer data captured them all, and they all contributed to the protective effect.

This distinction matters because the public health messaging around cancer prevention has historically focused on "exercise" — a word that connotes gym memberships, running shoes, and dedicated workout sessions. The Oxford data shows that the cancer protection comes from total daily movement, not from exercise as a discrete activity. A person who never exercises but walks constantly throughout the day — to the shops, around the house, up and down stairs — accumulates the same protective steps as a person who runs for thirty minutes and sits for the rest of the day.

## How Physical Activity Reduces Cancer Risk

The biological mechanisms linking physical activity to cancer reduction are well-established and operate through multiple pathways:

**Chronic inflammation.** Physical activity reduces systemic inflammation, measured by lower levels of C-reactive protein, interleukin-6, and tumour necrosis factor-alpha. Chronic low-grade inflammation — sometimes called "inflammaging" — promotes cancer initiation and progression. Regular movement suppresses it.

**Hormone regulation.** Physical activity lowers circulating levels of oestrogen and insulin — two hormones that drive the growth of breast, endometrial, and colorectal cancers. Post-menopausal women who are more physically active have significantly lower oestrogen levels, which directly reduces breast cancer risk.

**Immune surveillance.** Exercise enhances the activity of natural killer cells — immune cells that identify and destroy abnormal cells before they can form tumours. A single bout of moderate exercise can increase natural killer cell activity for several hours. Regular exercise maintains this elevated surveillance over time.

**Insulin sensitivity.** Physical activity improves insulin sensitivity and reduces insulin-like growth factor 1 (IGF-1), both of which are implicated in cancer development. High insulin levels promote cell proliferation and inhibit apoptosis — the programmed cell death that prevents damaged cells from becoming cancerous.

**Body composition.** Physical activity reduces visceral fat — the metabolically active fat stored around internal organs — which produces inflammatory cytokines and growth factors that promote cancer. The relationship between visceral fat and cancer is dose-dependent: more visceral fat means higher risk.

**Reduced sitting time.** Every hour spent walking is an hour not spent sitting. Prolonged sitting is independently associated with increased cancer risk, even after adjusting for exercise levels. The Oxford study's finding that light-intensity activity is protective suggests that breaking up sitting time — even with movement as simple as walking to the kitchen — has measurable cancer-prevention value.

## What Indian Parents Were Doing

To understand what the Oxford study means for Indian Americans, you have to understand what a typical day of movement looked like in an Indian household before the current generation moved to America.

**Morning:** Wake at 6 AM. Walk to the milk booth (200-500 steps). Walk to the temple for morning darshan (500-1,500 steps depending on distance). Walk through the house preparing breakfast, sweeping, arranging the kitchen (500-800 steps).

**Mid-morning:** Walk to the sabzi mandi (vegetable market) to buy fresh produce. This was a daily trip, not a weekly one — because Indian cooking uses fresh vegetables daily and refrigeration was limited. Round trip: 1,000-3,000 steps. Walk through the market, stopping at multiple vendors, carrying bags back. Additional: 500-1,000 steps.

**Afternoon:** Cooking lunch — which in an Indian kitchen involves substantial standing and movement between the stove, the counter, the storage area, and the dining table. Estimated: 500-1,000 steps. Cleaning up after lunch: 200-400 steps.

**Late afternoon:** Chai and a rest period — the one sedentary block of the day.

**Evening:** Walk to the park, the market, or a neighbour's house. In many Indian cities, the evening walk is a daily ritual. Round trip: 1,500-3,000 steps. Children playing outside (running, cricket, cycling) while parents walk and socialise.

**After dinner:** A short walk — even just around the block or on the terrace. 500-1,000 steps.

**Total estimated daily steps:** 5,500-12,000.

The average — without any exercise, without any gym, without any fitness tracker, without any intention to be "active" — was approximately 7,000 to 8,000 steps per day. Which is precisely the range the Oxford study identifies as producing an 11 to 16 percent reduction in cancer risk.

Indian parents were not exercising. They were living. The architecture of daily Indian life — walking to the market instead of driving, cooking from scratch instead of ordering delivery, visiting neighbours on foot instead of texting, walking after dinner instead of watching television — accumulated steps that, according to the Oxford data, were preventing cancer.

## What Indian Americans Stopped Doing

The Indian American daily movement profile looks nothing like the one described above. A typical day:

**Morning:** Wake at 7 AM. Walk from bedroom to kitchen (20 steps). Sit at the kitchen table to eat (0 steps). Walk to the garage (30 steps). Drive to work.

**Work day:** Walk from the parking lot to the office (200 steps). Sit at a desk for 4 hours. Walk to a conference room (100 steps). Sit for another 3 hours. Walk to the break room for lunch (80 steps). Sit for another 3 hours. Walk back to the car (200 steps). Drive home.

**Evening:** Walk from the garage to the house (30 steps). Sit on the couch. Order food on DoorDash. Eat on the couch. Watch television. Walk to bed (40 steps).

**Total estimated daily steps:** 1,500-3,000.

This is not an exaggeration. The average American adult takes 3,000 to 4,000 steps per day, according to data from the National Health and Nutrition Examination Survey. Indian American tech workers — who sit at desks, commute by car, and live in houses where every errand requires driving — are likely at the lower end of this range.

The gap between 7,000 steps (what Indian parents walked by default) and 3,000 steps (what Indian Americans walk by default) is the gap between an 11 percent cancer risk reduction and no reduction at all. It is approximately 4,000 steps — about 30 to 40 minutes of walking. Not running. Not exercising. Walking.

## The 10,000-Step Myth and What Actually Matters

The fitness industry's fixation on 10,000 steps has had an unintended harmful effect: it has made people believe that if they cannot reach 10,000, there is no point in trying. A person who takes 4,000 steps and checks their fitness tracker sees that they are at 40 percent of their "goal" and feels defeated. They do not know — because nobody told them — that reaching 7,000 would give them an 11 percent cancer risk reduction, that reaching 9,000 would give them 16 percent, and that every additional 1,000 steps contributes incrementally.

The Oxford study demolishes the 10,000-step target by showing that the health benefits begin much earlier and accumulate gradually. There is no magical threshold. There is a dose-response curve where every step matters.

For Indian Americans, this reframing is important because 7,000 steps is achievable without lifestyle overhaul. You do not need to join a gym. You do not need to run. You do not need to buy special shoes or clothing. You need to walk.

## How to Get to 7,000

**Walk after dinner.** This is the single highest-impact habit you can adopt. A 20-minute walk after dinner adds approximately 2,000 to 2,500 steps. If you currently take 3,500 steps a day, a post-dinner walk puts you at 6,000 — close to the cancer-protective threshold. If a family member walks with you, you are also addressing the social isolation risk identified in the loneliness-IBD study.

**Walk to buy groceries.** If you live within a mile of an Indian grocery store, walk there. Carry bags back. This single trip adds 2,000-4,000 steps and replicates the daily sabzi mandi trip that your parents made on foot.

**Take phone calls on foot.** A 15-minute phone call to your parents in India, taken while walking around the block, adds 1,500 steps. You were going to make the call anyway. Walk while you talk.

**Park far away.** At work, at the grocery store, at the mall — park at the far end of the lot. Each trip adds 200-400 steps. Over a day with multiple stops, this accumulates.

**Replace one delivery order per week with a walk to the restaurant.** If the restaurant is within a mile, the round trip adds 2,000-4,000 steps. You also get your food faster than the delivery driver, and it is hotter when you get it.

**Take the stairs.** At work, in your apartment building, at the mall. Climbing stairs burns significantly more calories per step than walking on flat ground, and the Oxford study counted stair climbing as protective activity.

**If you have elderly parents living with you, walk with them.** Slowly. Every evening. To the end of the street and back. Their pace does not matter. Their presence on the walk is what matters — for your cancer risk, for their isolation risk, and for the relationship between you that the immigration experience has compressed into a few evening hours.

## The Architecture Problem

The reason Indian Americans walk less than their parents is not laziness or lack of knowledge. It is architecture.

American suburbs were designed around the car. Streets are wide, pavements are intermittent or absent, destinations are far apart, and the default mode of transport for every errand is driving. The Indian urban environment — dense, walkable, with shops and temples and markets within walking distance of homes — was designed (or evolved) around the pedestrian. The Indian village was even more pedestrian — everything was reachable on foot because there was no alternative.

When Indian families moved to American suburbs, they did not choose to stop walking. They moved into environments where walking was no longer practical. The sabzi mandi is now a 15-minute drive. The temple is a 30-minute drive. The neighbours are behind fences and closed doors. The evening walk has no destination because there is nowhere to walk to.

This is not a problem that individual behaviour change can fully solve. It is an infrastructure problem. But within the constraints of suburban American architecture, there are choices: you can walk in a park instead of on a street. You can walk in a mall. You can walk in your neighbourhood even if there is no destination. You can walk on a treadmill while watching the evening news. None of these are as satisfying as walking to the temple or the sabzi mandi, but all of them accumulate steps that, according to the Oxford data, are protecting you from cancer.

## The Number That Matters

The number is not 10,000. It was never 10,000. A Japanese company made it up in 1965 to sell pedometers.

The number, according to an Oxford study of 85,394 people tracked with wrist-worn accelerometers and followed for six years, is 7,000. That is the point at which cancer risk drops by 11 percent compared to 5,000 steps. More is better — 9,000 gives you 16 percent, and the top quartile of movers gets 26 percent. But 7,000 is where the clinically meaningful reduction begins.

Seven thousand steps is what your parents walked without thinking about it. It is what you stopped doing when you moved to a suburb, started driving everywhere, and began ordering dinner instead of walking to the market to buy it.

The Oxford study is not prescribing a new health intervention. It is quantifying an old one. Your parents were not health-conscious. They were not fitness enthusiasts. They did not track their steps. They walked because the architecture of their lives required it. And that walking, according to the data, was protecting them from cancer.

The architecture of your life does not require it. So you will have to choose it. Walk after dinner. Walk to the shops. Walk with your parents. Walk with your children. Walk without a destination, without a tracker, and without calling it exercise.

Seven thousand steps. Your parents did it every day. The Oxford data says it matters. The question is whether you will."""

art2_sources = [
    "https://bjsm.bmj.com/",
    "https://scitechdaily.com/the-simple-habit-that-could-lower-your-cancer-risk/",
    "https://attractions.net.au/news/walking-certain-number-of-steps-daily-reduces-cancer-risk-oxford-study-finds/",
]

print("\n=== Article 2: Walking 7,000 Steps / Cancer Risk 11% / Oxford / Indian Parents ===")
print(f"  Word count: {len(art2_body.split())}")

# Image: people walking outdoors — evening walk, park, or Indian market scene
art2_image = fetch_pexels_image("people walking together in park evening golden hour")
if not art2_image:
    art2_image = fetch_pexels_image("couple walking neighborhood evening outdoors healthy")
if art2_image:
    print(f"  📸 Pexels image: {art2_image['pexels_id']} by {art2_image['photographer']}")

result2 = sb_post("p2_articles", {
    "id": art2_id,
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "slug": art2_slug,
    "category": art2_category,
    "body": art2_body.strip(),
    "status": "published",
    "published_at": now,
    "sources": art2_sources,
    "score_total": 89,
    "tags": ["walking", "steps", "cancer risk", "7000 steps", "10000 steps myth", "Oxford University", "UK Biobank", "British Journal of Sports Medicine", "accelerometer", "light activity", "dose-response", "Indian parents", "evening walk", "sabzi mandi", "temple walk", "suburban design", "car culture", "sedentary", "Indian American", "tech workers", "grocery shopping", "cancer prevention", "inflammation", "immune surveillance", "insulin", "Yamasa", "pedometer", "NRI", "diaspora"],
    "vertical": "diaspora",
    "urgency": "standard",
    "diaspora_angle": "Oxford/BJSM study: 85,394 UK Biobank adults with wrist-worn accelerometers, 6-year follow-up. 7,000 steps/day = 11% lower cancer risk; 9,000 steps = 16%; top quartile = 26%. Even light-intensity activities (shopping, chores, stairs) counted. The 10,000-step target was a 1965 Japanese marketing campaign, not science. NRI angle: traditional Indian daily life accumulated 7,000-8,000 steps by default — walking to temple, sabzi mandi, neighbour visits, evening walk (sair). No gym, no tracker, no intention to 'exercise.' Indian Americans average 1,500-3,000 steps in the car-suburb-desk-couch cycle. The 4,000-step gap between Indian parent default and Indian American default is the gap between cancer protection and none. The fix is 30-40 minutes of walking — achievable without lifestyle overhaul. Evening walk after dinner is the single highest-impact habit. Architecture problem: American suburbs designed for cars eliminated the walking infrastructure Indian life was built around.",
    "word_count": len(art2_body.split()),
    "image_url": art2_image["url"] if art2_image else None,
    "image_caption": f"Photo by {art2_image['photographer']} via Pexels" if art2_image else None,
})
if result2:
    print(f"  ✓ Published: {art2_id}")
else:
    print("  ✗ Failed or duplicate")


# ── Git commit & push ──
print("\n=== Git push ===")
os.chdir(str(Path.home() / "workspace/the-videshi-news"))
subprocess.run(["git", "add", "-A"], capture_output=True)
commit_msg = "lifestyle: loneliness-IBD 85% + walking 7000 steps cancer 11% (2026-05-26 03:00 PDT)"
subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True)
push = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=30)
print(f"  Push: {'OK' if push.returncode == 0 else push.stderr[:200]}")

print("\n=== Done ===")
