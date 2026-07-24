#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-24 07:00 PDT run
2 articles:
  1. Teen Creatine / Looksmaxxing — U Michigan study: creatine use up 90% in boys, 168% in girls; NRI parenting angle
  2. US Measles 2026 — 1,952 cases in 25 states, Bangladesh 512 deaths; NRI vaccination gaps, summer travel risk
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
# ARTICLE 1: Teen Creatine / Looksmaxxing
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "Your Teenager Is Taking Creatine. A New Study Says Use Among American Teens Has Nearly Doubled — and Indian Parents Are the Last to Find Out."
art1_subheadline = "A University of Michigan study of 875,000 students published in the Annals of Epidemiology found creatine use rose 90 per cent among boys and 168 per cent among girls between 2019 and 2024. Steroid use fell by half. The shift is driven by 'looksmaxxing' — a social media culture that treats the male body as a project to be optimised through supplements, gym routines, and aesthetic procedures. For Indian American parents who monitor screen time but have no idea what is in their child's gym bag, this is the article you did not know you needed."
art1_slug = make_slug("teenager-creatine-looksmaxxing-study-indian-parents-supplement")
art1_category = "lifestyle-health"

art1_body = """You know your teenager's GPA. You know their SAT prep schedule. You know how many AP classes they are taking and whether their college counsellor thinks the essay needs another draft. You may even know what they had for lunch.

You almost certainly do not know that they have been taking creatine for the past three months.

A study published this month in the Annals of Epidemiology, led by researcher Philip Veliz at the University of Michigan, analysed data from nearly 875,000 eighth-, tenth-, and twelfth-graders across the United States. The finding: creatine use among teenage boys rose from just under 9 per cent to nearly 17 per cent between 2019-2020 and 2023-2024 — a 90 per cent increase. Among girls, use rose from roughly 1 per cent to more than 3 per cent, a 168 per cent increase.

At the same time, steroid use fell from around 2 per cent to less than 1 per cent among all respondents.

The researchers attribute both trends to a single force: social media.

## What Is Looksmaxxing — and Why Your Child Knows More About It Than You Do

Looksmaxxing is a subculture that originated on male-dominated internet forums and has migrated to TikTok, YouTube, and Instagram, where it has exploded among teenagers. The core premise is that physical appearance can be systematically optimised through a combination of gym training, supplements, skincare routines, facial exercises (called "mewing"), posture correction, and — at the extreme end — surgical procedures.

The typical looksmaxxing content creator is a young man, usually between 16 and 25, who films himself going through his daily "protocol": wake up, take supplements (creatine, protein powder, sometimes turkesterone or ashwagandha), go to the gym, do a specific jaw exercise, apply retinol, track calories. The aesthetic is clinical. The language is optimisation. The underlying message is that your body, as it naturally exists, is a draft that needs editing.

For teenage boys, this content fills the same psychological space that diet culture has occupied for teenage girls for decades. But it has arrived in a format — short-form video, algorithmic recommendation — that makes it far more pervasive than anything that came before.

If your child has a TikTok or Instagram account and is between 13 and 18, they have been exposed to looksmaxxing content. The algorithm guarantees it. The only question is how deeply it has landed.

## Why This Matters Specifically for Indian American Families

The conversation about body image in Indian American households operates on a completely different axis than the one their children encounter online.

**Indian parents worry about food, not supplements.** The typical Indian parent's nutritional concern is whether the child is eating enough dal, drinking enough milk, and avoiding too much junk food. Supplements occupy a blind spot. In India, the supplement industry was largely limited to Horlicks, Bournvita, and Chyawanprash — things mothers bought for "growth" and "immunity." The idea that a 15-year-old would independently purchase and consume a performance supplement from Amazon is outside most Indian parents' mental model.

**The desi gym culture gap.** For first-generation Indian immigrant parents, going to the gym was not part of their upbringing. Exercise meant morning walks, yoga, or cricket. Bodybuilding was something they associated with Bollywood actors or professional wrestlers — not with their child who just started tenth grade. When a teenager says "I'm going to the gym," many Indian parents hear "exercise" and feel positive about it. They do not ask what supplements are involved because they do not know to ask.

**The body-image conversation never happened.** Indian American families are among the least likely to have direct conversations about body image with their sons. With daughters, there may be anxious discussions about weight, skin colour, or appearance — though these too are often handled through cultural assumptions rather than open dialogue. With sons, the body-image conversation barely exists. Indian parents assume their boys are worried about grades, not about whether their jawline is "defined" enough. The looksmaxxing movement is exploiting a conversational vacuum.

**Height and build anxiety is already there.** Here is the uncomfortable part: Indian American teenagers already carry specific body-image pressures that make them susceptible to looksmaxxing ideology. South Asian men are, on average, shorter than their white and Black American peers. The average height for Indian-origin men in the US is approximately 5 feet 7 inches, compared with 5 feet 9.5 inches for white American men. In a high school environment where height and build are social currency, the gap is felt daily — in sports, in dating, in simply standing next to friends. Looksmaxxing content promises that even if you cannot change your height, you can change everything else: muscle mass, body fat percentage, jawline, posture, skin quality. For a South Asian teenager who already feels physically smaller than his peers, this message is potent.

## What Creatine Actually Does — and What It Does Not Do

Creatine monohydrate is one of the most studied sports supplements in the world. According to Harvard Medical School, it is formed from three amino acids — arginine, glycine, and methionine — and contributes to rapid energy production during high-intensity exercise. It may hasten muscle recovery after strenuous workouts.

Here is what it does not do: creatine does not directly build muscle. It allows you to train harder, which may lead to more muscle growth over time, but it is not a steroid and does not have the same mechanism of action.

The International Society of Sports Nutrition considers creatine safe for adults at recommended doses (typically 3-5 grams per day after a loading phase). However, there is limited research on long-term creatine use in adolescents, and the American Academy of Pediatrics has not endorsed its use for teenagers.

The practical concerns for teens include:

**Dosing.** Teenagers frequently take more than the recommended dose, operating on the assumption that more is better. Creatine at excessive doses can cause gastrointestinal distress, water retention, and — in rare cases — kidney stress, particularly in individuals who are not drinking adequate water.

**Stacking.** Creatine is almost never used alone in the looksmaxxing community. It is typically combined with pre-workout supplements (which contain high doses of caffeine, sometimes 300-400 mg per serving — equivalent to three to four cups of coffee), protein powder, and sometimes more exotic supplements like turkesterone, tongkat ali, or ashwagandha. The interactions between these supplements in adolescent bodies are poorly studied.

**The gateway concern.** This is what the Michigan study's lead author, Philip Veliz, flagged as the open question: "What is yet to be determined is whether this will eventually translate into steroid use as they age into young adulthood." The trajectory from legal supplements to illegal performance-enhancing drugs is well-documented in adult populations. Whether the same trajectory applies to teens who start with creatine at 15 is unknown.

## The Products in Your Child's Gym Bag

If you are an Indian parent reading this and wondering whether your teenager is using supplements, here is what to look for:

**Creatine monohydrate:** Usually a white powder in a tub or bag. Common brands include Optimum Nutrition, MuscleTech, Thorne, and Transparent Labs. A tub costs $20-40 on Amazon. Your teenager may have ordered it without you noticing — or may be getting it from a friend at school.

**Pre-workout:** A flavoured powder mixed with water and consumed before exercise. The container is usually brightly coloured with aggressive branding. Common brands include C4, Ghost, Gorilla Mode, and Bucked Up. The caffeine content can be extreme — up to 400 mg per serving in some products. For context, the American Academy of Pediatrics recommends that adolescents consume no more than 100 mg of caffeine per day.

**Protein powder:** This is the most mainstream supplement and the least concerning. Whey protein is well-studied and generally safe. However, some protein powders marketed to the fitness community contain added creatine, BCAAs, or other ingredients.

**Turkesterone and ecdysteroids:** These are marketed as "natural steroids" and are popular in looksmaxxing circles. They are plant-derived compounds with limited human research. Your teenager may be taking them because an influencer on TikTok said they work.

## What Indian Parents Should Actually Do

This is the practical section. Read it without panic.

**Step 1: Look, then talk.** Before having a conversation, check your teenager's room, gym bag, and Amazon order history (if you have access). You are not looking for drugs — you are looking for supplement containers. Know what you are dealing with before you start the conversation.

**Step 2: Do not shame.** If your teenager is taking creatine, it means they care about their physical fitness and are trying to improve their body. That impulse is healthy. The execution may need guidance, but the motivation is not something to punish. If you come in with anger or shame — "what is this powder, are you taking drugs?" — the conversation is over before it starts.

**Step 3: Ask about the source.** "Who told you about this?" is a more useful question than "why are you taking this?" The answer will tell you whether your teenager is following a certified trainer, a friend at school, or a 22-year-old TikTok influencer with no credentials. The source matters more than the supplement.

**Step 4: Consult the paediatrician.** If your teenager wants to use supplements, make it a joint project. Schedule a visit to their paediatrician. Discuss the specific supplements they want to take. Get bloodwork done. The paediatrician can assess kidney function, liver function, and overall health, and provide evidence-based guidance. This turns a potential conflict into a health conversation — and it removes the secrecy.

**Step 5: Talk about body image directly.** This is the hardest step for Indian parents, and the most important one. Ask your son — or daughter — what they want to change about their body and why. Ask them what content they are consuming about fitness and appearance. Ask them if they feel pressure to look a certain way. You may be surprised by the answers. South Asian teenagers carry body-image pressures that their parents never had to navigate at the same age, in the same social environment, with the same algorithmic amplification.

**Step 6: Monitor, do not ban.** Banning supplements outright is likely to drive the behaviour underground. A better approach is informed oversight: you know what they are taking, how much, and why. You have a paediatrician in the loop. You check in regularly. The goal is not control — it is communication.

## The Bigger Picture

The Michigan study is not about creatine. It is about a generation of teenagers who have outsourced their self-image to social media algorithms, and who are using supplements as the most accessible tool to close the gap between who they are and who the algorithm tells them they should be.

For Indian American families, the looksmaxxing trend intersects with existing cultural pressures in ways that are specific and under-discussed. Indian parents who grew up worrying about academic performance are raising children who worry about jawline definition. The shift is disorienting — but it is happening whether parents are aware of it or not.

Creatine, on its own, is probably fine for most healthy teenagers at appropriate doses. The concern is what it represents: a culture of physical optimisation that is unsupervised, algorithmically driven, and operating entirely outside parental awareness.

The conversation does not start with supplements. It starts with asking your teenager how they feel about their body. For many Indian families, that will be the first time anyone has ever asked."""

art1_sources = [
    "https://www.drugs.com/news/teens-turning-creatine-not-steroids-looksmaxxing-130073.html",
    "https://nursing.umich.edu/faculty-staff/philip-veliz",
    "https://www.health.harvard.edu/exercise-and-fitness/the-truth-about-creatine",
    "https://www.aap.org/en/patient-care/sports-medicine/sports-nutrition/",
    "https://jissn.biomedcentral.com/articles/10.1186/s12970-017-0173-z",
    "https://nutritioninsight.com/news/looksmaxxing-trend-boosts-creatine-use-while-steroid-use-drops-among-us-teens.html",
]

print("=== Article 1: Teen Creatine / Looksmaxxing ===")
print(f"  Word count: {len(art1_body.split())}")

art1_image = fetch_pexels_image("teenager gym workout fitness supplements dumbbells")
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
    "score_total": 89,
    "tags": ["creatine", "looksmaxxing", "teens", "supplements", "gym culture", "body image", "Indian parents", "NRI", "social media", "TikTok", "health", "parenting", "diaspora"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "U Michigan study: creatine up 90% in boys, 168% in girls (2019-2024), driven by looksmaxxing. Indian American parents are in a blind spot — supplements aren't on the cultural radar, the gym-body conversation never happens with sons, and South Asian teens carry specific height/build anxieties that make them susceptible. Practical guide: what to look for, how to talk about it without shaming, when to involve the paediatrician.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result:
    print(f"  ✓ Published: {art1_id}")
else:
    print("  ✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: US Measles Outbreak 2026 / NRI Vaccination Gaps
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "The US Has Nearly 2,000 Measles Cases in 2026. Bangladesh Has 512 Deaths. If You Are an NRI Flying Home This Summer With Children, This Is the Article to Read Before You Book."
art2_subheadline = "The CDC reports 1,952 confirmed measles cases across 25 US states this year, with 93 per cent in unvaccinated individuals. South Carolina's record-breaking outbreak only just ended. Bangladesh, where many NRIs transit or have family connections, has recorded 62,507 suspected cases and 512 deaths since March. India has tightened airport screening. The MMR vaccine is 97 per cent effective with two doses — but the national vaccination rate has fallen to 92.5 per cent, below the 95 per cent threshold for herd immunity. Summer is when NRI families fly. This is what you need to verify before you leave."
art2_slug = make_slug("measles-outbreak-2026-nri-vaccination-children-summer-travel")
art2_category = "lifestyle-health"

art2_body = """There is a sentence in this article that may make you angry. Here it is: your child may not be fully vaccinated against measles, and you may not know it.

You are reading this because you are the kind of parent who reads health articles. You are almost certainly not anti-vaccine. You took your child to every well-visit. You followed the paediatrician's schedule. You kept the immunisation card in the folder with the passport and the birth certificate.

And yet — depending on your child's age, when they arrived in the US, whether they were born abroad, and whether they missed a dose during the pandemic — there is a real chance that their measles protection is incomplete. This matters more in 2026 than it has in any year this century.

## The Numbers You Need to Know

**United States:** The CDC has confirmed 1,952 measles cases across 25 states as of May 21, 2026. Ninety-three per cent of those cases involved unvaccinated or under-vaccinated individuals. Twenty-nine separate outbreaks have been identified. South Carolina's outbreak — the largest in decades — was declared over only this month, after the state recorded a 31 per cent surge in MMR vaccinations in response to the crisis. The national MMR vaccination rate has fallen to 92.5 per cent, below the 95 per cent threshold required for herd immunity.

**Bangladesh:** Since March 2026, Bangladesh has recorded 62,507 suspected measles cases and 512 confirmed deaths. The vast majority of deaths are children under five. The World Health Organization attributed the outbreak to declining routine immunisation coverage and launched an emergency vaccination campaign targeting children aged 6 to 59 months across 30 districts.

**India:** The government has tightened airport screening and directed state health authorities to ramp up surveillance, particularly at international airports with connections to affected regions. India's own measles vaccination coverage — approximately 93 per cent for the first dose but only 83 per cent for the second dose nationally — leaves significant pockets of vulnerability.

**Europe:** A measles outbreak in Alcantarilla, Spain (Murcia region), doubled in cases this week, with eight confirmed cases including a baby. The UK recorded over 6,000 cases in the 2025-2026 period. The European Centre for Disease Prevention and Control has warned that summer travel will accelerate transmission across borders.

## Why NRI Families Are Specifically at Risk

This is not a general measles article. This is specifically about the gaps that affect families who move between countries.

**The two-dose problem.** The MMR (measles, mumps, rubella) vaccine requires two doses for full protection: the first at 12-15 months and the second at 4-6 years. The first dose provides about 93 per cent protection. Two doses provide 97 per cent protection. If your child received the first dose but missed the second — which is common for families who relocated between countries during the pandemic years of 2020-2022 — they have a meaningful gap in immunity.

**Born in India, vaccinated on a different schedule.** India's Universal Immunisation Programme administers the first dose of measles vaccine at 9 months and the second (MR or MMR) at 16-24 months — different timing than the US schedule. Children born in India who immigrated to the US may have received their vaccines on the Indian schedule, which is medically sound, but may not align with the documentation that US schools require. Some parents assume that because the child was vaccinated in India, everything is covered. It may be — but verify it. Some children vaccinated before 12 months in India may need a booster under US guidelines because the immune response at 9 months is less robust.

**The pandemic gap.** Between March 2020 and mid-2021, routine paediatric vaccination schedules were disrupted worldwide. The WHO estimates that 67 million children globally missed or received delayed routine vaccinations during this period. If your child was between one and six years old during the pandemic, there is a non-trivial chance they missed the second MMR dose. Many parents intended to catch up and never did.

**Travel to high-risk regions.** NRI families travel. That is one of the defining characteristics of the diaspora — the annual or biannual trip to India, often with stopovers in the Gulf or Southeast Asia. In summer 2026, many families will be transiting through airports in countries with active measles transmission. A single measles-infected person can infect 12-18 others in a susceptible population. An airplane cabin is exactly the kind of enclosed, prolonged-contact environment where measles spreads most efficiently.

**Adult immunity gaps.** This is the one that surprises most people: measles immunity can wane in adults, particularly those who received only one dose of the vaccine (the standard before 1989 in many countries, including India). If you were born in India in the 1970s or 1980s, you may have received only one dose of measles vaccine — or you may have received a vaccine with lower efficacy than the current MMR. Natural infection provides lifelong immunity, but if you never had measles and received only one dose, your protection may be incomplete. The CDC recommends that adults born after 1957 who lack evidence of immunity receive at least one dose of MMR. International travellers should have two doses.

## What Measles Actually Does

Measles is not a mild childhood illness. It is one of the most contagious diseases known to medicine.

The virus spreads through respiratory droplets and can remain suspended in the air for up to two hours after an infected person has left a room. If you are unvaccinated and walk into a room where a measles patient was two hours ago, you can still be infected.

Symptoms begin 10-14 days after exposure: high fever (often above 104°F), cough, runny nose, red eyes, and the characteristic rash that starts on the face and spreads downward. In uncomplicated cases, the illness lasts 7-10 days.

In complicated cases — which occur in about 30 per cent of measles patients — the consequences include pneumonia (the leading cause of measles death), encephalitis (brain inflammation, occurring in approximately 1 in 1,000 cases, which can cause permanent brain damage), and subacute sclerosing panencephalitis (SSPE), a fatal degenerative brain disease that can appear 7-10 years after infection.

Before widespread vaccination, measles killed approximately 2.6 million people per year worldwide. It still kills more than 100,000 people per year, almost all of them children in low-income countries.

This is not chicken pox. This is not a disease you want your child to "get through."

## The Practical Checklist Before You Fly This Summer

This section is the reason this article exists. Print it. Share it in your family WhatsApp group. Do every item before you board a plane.

### For Your Children

**1. Pull the immunisation records.** Every child in the US has an immunisation record, either with the paediatrician, through the state's immunisation information system (IIS), or in the school health file. Pull it. Check specifically for two doses of MMR. Do not assume. Verify.

**2. If they have only one dose, schedule the second now.** The second dose can be given as early as 28 days after the first dose, so there is time before most summer travel. Call the paediatrician's office Monday morning. Many pharmacies (CVS, Walgreens) also administer MMR to children aged 3 and older. Cost with insurance: typically $0 (preventive care). Cost without insurance: $80-130.

**3. For infants 6-11 months travelling internationally.** The CDC recommends that infants aged 6-11 months receive one dose of MMR before international travel. This dose does not count toward the routine two-dose schedule — the child will still need the standard doses at 12-15 months and 4-6 years. But it provides protection during the trip.

**4. For children born outside the US.** If your child was born in India or another country, bring their vaccination records (original, not a copy) to your US paediatrician and ask them to reconcile the records with the US schedule. The paediatrician may recommend additional doses depending on the child's age and what vaccines were given abroad.

### For Adults

**5. Check your own status.** If you were born after 1957, you need at least one documented dose of MMR or evidence of immunity (a blood test showing measles antibodies, called a titre). If you are travelling internationally, the CDC recommends two doses. Most adults who grew up in India in the 1970s-1990s either had measles as a child (lifelong immunity) or received one dose of the vaccine (may have waned). If you are unsure, a titre test costs $50-100 at most labs and gives you a definitive answer.

**6. For pregnant women.** The MMR vaccine cannot be given during pregnancy (it is a live vaccine). If you are pregnant and planning to travel to an area with active measles, consult your OB-GYN immediately. You should avoid travel to high-risk areas if possible. If you have already been exposed, immunoglobulin may be given within six days of exposure for partial protection.

### For Grandparents Visiting or Being Visited

**7. Grandparents travelling from India to the US.** Many older Indians have natural immunity from childhood measles infection. But if they are unsure, a titre test before travel is worth the peace of mind. If they are flying through Dubai, Doha, or another Gulf hub — where travellers from Bangladesh, Pakistan, and sub-Saharan Africa transit in large numbers — the exposure risk in the airport is real.

**8. Grandparents being visited in India.** If you are bringing your US-born children to visit grandparents in India, verify the children's vaccination status before departure. India's second-dose coverage (83 per cent nationally) means your children will be in an environment with lower population immunity than the US.

## The Anti-Vaccine Influence You May Not Realise Is Reaching You

Here is the uncomfortable section. The anti-vaccine movement in the US is not just a white evangelical phenomenon. It has made inroads into every community, including the Indian American community, through:

**WhatsApp groups.** Family and community WhatsApp groups regularly circulate vaccine misinformation. The misinformation is often in Hindi or the family's regional language, which makes it feel more trustworthy and harder for English-language fact-checkers to counter. Common claims: MMR causes autism (definitively debunked by studies involving millions of children), natural immunity is better (true for survivors, but measles kills 1-2 per 1,000 children who contract it), and Indian children do not need American vaccine schedules (the virus does not check nationality).

**Naturopathy and Ayurveda communities.** Some wellness-oriented Indian American communities have adopted a scepticism toward "Western medicine" that extends to vaccines. This is not representative of Ayurveda as a whole — India's own government runs one of the world's largest vaccination programmes. But the wellness-to-anti-vax pipeline is real, and it operates in Indian American spaces just as it does in other communities.

**The RFK Jr. effect.** Robert F. Kennedy Jr.'s appointment as Secretary of Health and Human Services has, regardless of the administration's official position on vaccines, normalised vaccine questioning in ways that have trickled into every community. Indian Americans who follow American politics — which is a high percentage — have been exposed to this messaging.

The antidote is not argument. It is information. The MMR vaccine has been given to billions of people over more than 50 years. It is 97 per cent effective with two doses. The disease it prevents is genuinely dangerous. The choice is not between the vaccine and nothing — it is between the vaccine and a virus that was killing millions of people per year before the vaccine existed.

## Before You Board

Summer 2026 is not a normal travel year for measles. The US has more cases than it has had in decades. Bangladesh is in the middle of the worst measles outbreak in its modern history. India is screening at airports. Europe has active outbreaks in tourist destinations.

You are going to fly this summer. Your parents are going to fly this summer. Your children are going to fly this summer.

Check the records. Get the doses. Know that measles is airborne, that it lives in the air for two hours, that one person can infect 18 others, and that the vaccine is the only reliable protection that exists.

The paediatrician's office opens Monday morning. Call first thing."""

art2_sources = [
    "https://www.cdc.gov/measles/data-research/index.html",
    "https://en.wikipedia.org/wiki/2026_Bangladesh_measles_outbreak",
    "https://www.reuters.com/world/asia-pacific/suspected-confirmed-measles-deaths-top-500-bangladesh-2026-05-20/",
    "https://nbcpalmsprings.com/2026/05/south-carolinas-record-breaking-measles-outbreak-declared-over/",
    "https://www.who.int/news-room/events/detail/2026/05/19/default-calendar/seventy-ninth-world-health-assembly",
    "https://kffhealthnews.org/news/article/colorado-charts-vaccine-course-federal-pullback/",
    "https://www.thesun.co.uk/health/35411736/urgent-holiday-warning-measles-outbreak-spanish-tourist-hotspot/",
]

print("\n=== Article 2: US Measles 2026 / NRI Vaccination Gaps ===")
print(f"  Word count: {len(art2_body.split())}")

art2_image = fetch_pexels_image("family airport travel suitcase international departure")
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
    "score_total": 92,
    "tags": ["measles", "vaccination", "MMR", "CDC", "NRI", "travel", "children", "Bangladesh", "India", "health", "summer", "airport", "diaspora", "anti-vaccine", "public health"],
    "vertical": "diaspora",
    "urgency": "high",
    "diaspora_angle": "1,952 US measles cases in 2026, 93% unvaccinated. Bangladesh: 512 deaths, 62K cases. NRI families face specific gaps: kids born in India on different vaccine schedule, pandemic-era missed second doses, adults with only one dose from 1970s-80s India, and summer travel through high-risk hubs. Practical checklist: pull records, verify two MMR doses, schedule catch-ups, infant travel dose for 6-11 months, adult titre test, grandparent guidance.",
    "word_count": len(art2_body.split()),
    "image_url": art2_image["url"] if art2_image else None,
    "image_caption": f"Photo by {art2_image['photographer']} via Pexels" if art2_image else None,
})
if result:
    print(f"  ✓ Published: {art2_id}")
else:
    print("  ✗ Failed or duplicate")


# ── Git commit & push ──
print("\n=== Git push ===")
import subprocess as sp
os.chdir(str(Path.home() / "workspace/the-videshi-news"))
sp.run(["git", "add", "-A"], check=True)
sp.run(["git", "commit", "-m", "lifestyle-writer: creatine looksmaxxing + measles NRI vaccination (2026-05-24 07:00 PDT)"], check=True)
push = sp.run(["git", "push"], capture_output=True, text=True, timeout=30)
print(push.stdout or push.stderr)

print("\n✅ Lifestyle writer 07:00 PDT run complete")
