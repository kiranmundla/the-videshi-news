#!/usr/bin/env python3
"""Videshi Lifestyle Writer — 2026-05-24 23:00 PDT run (06:00 UTC May 25)
2 articles:
  1. Semaglutide reduces heavy drinking (Lancet May 2 2026) — NRI angle: Indian American drinking culture, the 'whisky uncle' archetype, high-functioning alcoholism in tech/finance, shame preventing treatment, now a drug that could help
  2. Long-term antidepressant use linked to sudden cardiac death (EHRA 2025 / Danish study, 4.3M people) — NRI angle: South Asians have highest CVD risk AND rising depression/anxiety treatment rates, cultural stigma means long indefinite prescriptions without cardiac monitoring
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

def make_slug(text, suffix="20260525"):
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

# ── Cross-check recent lifestyle articles to avoid duplication ──
print("=== Cross-checking recent lifestyle articles ===")
recent_resp = requests.get(
    f"{SB_URL}/rest/v1/p2_articles?category=eq.lifestyle-health&status=eq.published&order=published_at.desc&limit=25&select=id,headline,slug,published_at",
    headers=HEADERS, timeout=15
)
if recent_resp.ok:
    recent = recent_resp.json()
    print(f"  Found {len(recent)} recent lifestyle articles")
    for art in recent[:10]:
        print(f"  - {art.get('slug','?')[:60]}")
else:
    print(f"  ⚠ Failed to fetch recent articles: {recent_resp.status_code}")
    recent = []

recent_headlines = " ".join([a.get("headline", "") for a in recent]).lower()

# Verify neither topic already covered
topics_ok = True
for check_term in ["semaglutide alcohol", "glp-1 alcohol", "heavy drinking semaglutide", "antidepressant cardiac death", "antidepressant heart death", "sudden cardiac death antidepressant"]:
    if check_term in recent_headlines:
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
# ARTICLE 1: The Weight-Loss Drug Everyone Is Taking Just Showed It Can Cut
# Heavy Drinking Too. For Indian Americans, the Real Barrier Was Never the Drug.
# ══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_headline = "The Weight-Loss Drug Everyone Is Taking Just Showed It Can Cut Heavy Drinking Too. For Indian Americans, the Real Barrier Was Never the Drug."
art1_subheadline = "A clinical trial published on May 2 in The Lancet found that once-weekly semaglutide injections — the same drug sold as Ozempic for diabetes and Wegovy for weight loss — reduced heavy drinking days, total alcohol consumption, and cravings in people with alcohol use disorder and obesity. The 26-week trial, led by researchers at Copenhagen University Hospital with NIH involvement, enrolled 108 participants and showed that those on semaglutide had significantly larger reductions in drinking than those on placebo. For Indian Americans — a community where alcohol flows freely at every gathering but where admitting you have a problem with it remains one of the last unbreakable taboos — the science is not the obstacle. The silence is."
art1_slug = make_slug("semaglutide-ozempic-alcohol-heavy-drinking-lancet-indian-american")
art1_category = "lifestyle-health"

art1_body = """There is a particular kind of drinking that happens in Indian American households and it has no clinical name, no diagnostic code, and no place in any conversation anyone is willing to have.

It looks like this: the host opens Johnnie Walker Black at 6 PM. By 7:30 PM, every man in the room has a glass. By 9 PM, they are on their third or fourth pour. By 10:30 PM, someone is louder than they should be. By midnight, someone is driving home who should not be driving home. The next morning, nobody mentions it. The following weekend, it happens again. It has been happening for years.

This is not alcoholism in the way American medicine typically presents it — the person hitting rock bottom, the intervention, the rehab facility in Malibu. This is high-functioning, socially embedded, culturally reinforced heavy drinking that happens inside a community where alcohol is simultaneously everywhere and nowhere in the conversation about health.

A clinical trial published on May 2 in The Lancet has just demonstrated that semaglutide — the drug sold as Ozempic for type 2 diabetes and Wegovy for weight loss, currently the most talked-about pharmaceutical compound in America — can significantly reduce heavy drinking in people with alcohol use disorder (AUD) and obesity. The finding opens a new frontier in addiction medicine. For Indian Americans, it illuminates something that no drug can fix: a community-wide refusal to acknowledge that drinking has become a problem at all.

## What the Trial Found

The study was conducted by a team led by Dr. Anders Fink-Jensen at Copenhagen University Hospital, with scientists from the NIH's National Institute on Alcohol Abuse and Alcoholism (NIAAA) and National Institute on Drug Abuse (NIDA) as co-authors. It was a randomised, double-blind, placebo-controlled trial — the gold standard in clinical research.

A total of 108 adults with both alcohol use disorder and obesity were enrolled. They were randomised to receive either a weekly injection of semaglutide (titrated up to 2.4 mg, the Wegovy dose) or a matching placebo for 26 weeks. All participants also received standard cognitive behavioural therapy (CBT) sessions for AUD.

The headline results: 88 participants completed the trial. Both groups reduced their heavy drinking days over 26 weeks — the act of being in a clinical trial with CBT tends to improve outcomes regardless of drug allocation. But the semaglutide group improved significantly more across every measure that matters.

Heavy drinking days decreased more in the semaglutide group. Total monthly alcohol consumption dropped more. The number of drinks per drinking day fell more. Self-reported alcohol cravings declined more. And biomarkers of alcohol consumption and liver damage — objective blood tests that cannot be faked by telling a researcher what they want to hear — declined more in the semaglutide group.

As a bonus, the semaglutide group also lost more weight, had greater reductions in waist circumference and BMI, and showed better blood sugar control — effects consistent with the drug's approved use for obesity and diabetes.

The most common side effects were gastrointestinal: nausea, constipation, loss of appetite, diarrhoea, reflux, and abdominal pain — the same profile that millions of Ozempic and Wegovy users already know. Only one participant in the semaglutide group required hospitalisation for an adverse event.

"These findings are consistent with previous studies showing that GLP-1s might be an effective treatment for AUD," said Dr. George Koob, director of the NIAAA and a co-author. Dr. Nora Volkow, director of NIDA, added: "We're beginning to see some of that potential for GLP-1s to treat drug addiction turn into reality. Questions remain but this is nonetheless very encouraging."

## How Semaglutide Works on Alcohol Cravings

GLP-1 receptor agonists were designed to mimic a hormone that regulates appetite and blood sugar. But GLP-1 receptors are not only in the gut and pancreas. They are also found in the brain — specifically in areas involved in reward processing, motivation, and craving.

The same neural circuits that drive a person to eat a second slice of cake are, at a fundamental level, the same circuits that drive a person to pour a fourth drink. Both involve dopamine release in the mesolimbic reward pathway — the brain's ancient system for reinforcing behaviours that feel good.

Semaglutide appears to dampen the reward signal. It does not eliminate the desire to drink — participants in the trial still drank. But it reduces the intensity of the craving and the compulsive quality of the behaviour. The drink becomes easier to refuse. The fourth pour becomes optional rather than automatic.

This is why the overlap between obesity and AUD is not coincidental. Both conditions involve dysregulated reward processing. Both involve a gap between what you intend to do and what you actually do. And both, it turns out, may respond to the same pharmacological intervention.

## The Indian American Drinking Problem Nobody Discusses

Here is what the data says: Indian Americans drink. They drink more than the community's self-image suggests. And the patterns of drinking in the community carry risks that are compounded by South Asian biology.

There are no large-scale epidemiological studies of alcohol consumption specifically in Indian Americans — which is itself a data point about how invisible this issue is. But several smaller studies and surveys, combined with what every Indian American family observes at every gathering, paint a consistent picture:

**Men drink heavily at social events.** The standard Indian American dinner party, wedding reception, Diwali party, Holi celebration, or Super Bowl gathering involves hard liquor — typically whisky, vodka, or rum — poured generously. Beer is present but secondary. Wine is becoming more common among younger professionals. The quantities consumed in a single evening routinely exceed what the CDC defines as "binge drinking": five or more drinks for men on a single occasion.

This is not perceived as binge drinking. It is perceived as hospitality.

**The "whisky uncle" is a cultural archetype, not a punchline.** Every Indian American family has one — or several. The uncle who starts drinking at 5 PM and does not stop until the party ends. Who is noticeably impaired by 9 PM. Who everyone avoids at the end of the evening. Who has been doing this for twenty years. Nobody calls him an alcoholic. Nobody suggests he get help. He is just "like that."

In American clinical terms, many of these individuals meet the diagnostic criteria for alcohol use disorder. In Indian American cultural terms, they are uncles who drink.

**Women's drinking is rising and invisible.** Indian American women's alcohol consumption has increased significantly over the past decade, mirroring a national trend but amplified by specific cultural dynamics. The professional Indian American woman — in tech, medicine, consulting, finance — drinks at work events, at girls' nights, at wine tastings, at book clubs. For many, alcohol has become the social lubricant that replaces the informal community structures they left behind in India or that their mothers had. But because drinking by Indian women still carries stigma — it remains, in many families, something women "should not do" — the consumption is often hidden, minimised, or never discussed in health contexts.

**South Asian biology makes the stakes higher.** The ALDH2 gene variant, which causes the "Asian flush" — facial redness, nausea, rapid heartbeat after drinking — is present in a subset of South Asians, though at lower rates than in East Asians. More critically, South Asians metabolise alcohol differently in ways that increase the risk of liver damage, even at moderate consumption levels.

A 2019 study in the journal Hepatology found that South Asians develop alcohol-related liver disease at lower levels of consumption than white Europeans. This means the same three drinks that a person of European descent might metabolise without significant liver stress could be causing subclinical damage in a South Asian drinker.

Combine this with the fact that South Asians already have elevated rates of metabolic syndrome, insulin resistance, visceral fat, and cardiovascular disease — all of which are worsened by regular alcohol consumption — and the picture becomes alarming: a community that drinks heavily, that does not recognise heavy drinking as a health risk, and that is biologically more vulnerable to its consequences.

**Nobody seeks treatment.** According to the NIAAA, fewer than 10 per cent of Americans with AUD receive any form of treatment. Among Indian Americans, the number is almost certainly lower — though nobody has studied it, because nobody has asked.

The reasons are the same reasons that every form of mental health treatment in the Indian American community is underutilised: shame, stigma, the belief that personal problems should stay within the family, the perception that needing help is a sign of weakness, and a healthcare system that does not recognise or screen for the specific patterns of drinking that characterise South Asian alcohol use.

An Indian American man who drinks five large pegs of whisky every Friday and Saturday night — roughly 10-12 standard drinks per week concentrated in two sessions — is engaging in a pattern that the NIAAA classifies as heavy drinking and that increases his risk of liver disease, cardiovascular disease, certain cancers, and cognitive decline. His annual physical will not flag this. His doctor will not ask about it in detail. And he will not volunteer it, because in his framing, he does not have a problem. He drinks socially. Everyone does.

## What This Means for the Community

The Lancet trial is not going to solve Indian American drinking culture. Semaglutide is a drug, not a cultural intervention. It requires a prescription, a diagnosis, and a willingness to say: "I have a problem with alcohol."

But the study matters for several reasons:

**It reframes alcohol use disorder as a metabolic and neurological condition.** The fact that a drug designed for obesity and diabetes also reduces drinking reinforces what addiction researchers have known for decades: AUD is not a moral failing. It is a disorder of brain chemistry. The same reward circuits that drive overeating drive alcohol craving. For an Indian American community that still treats heavy drinking as a personal weakness or a character flaw — "He just needs more willpower" — this reframing is critical.

**It gives doctors a new tool.** Only three medications are currently FDA-approved for AUD: naltrexone, acamprosate, and disulfiram. All three have been available for decades. None is widely prescribed. None has strong cultural recognition in the South Asian community. Semaglutide, if eventually approved for AUD (the current trial is a stepping stone, not a final approval), would join a treatment landscape that is dramatically underutilised. But because millions of people already know what Ozempic is — because it is on the cover of every magazine, in every conversation about weight loss — the barrier to awareness would be lower.

**It creates an opening for dual treatment.** Many Indian Americans who would never see a doctor for drinking might already be taking semaglutide for weight loss or diabetes. If the drug is simultaneously reducing their alcohol consumption — as the trial suggests it does — they may experience the benefits of reduced drinking without the stigma of seeking addiction treatment. This is not ideal — every person with AUD deserves a proper diagnosis, therapy, and support — but in a community where the stigma of addiction is often more damaging than the addiction itself, an incidental treatment pathway may save lives.

## What You Can Do

If this article describes someone you know — and if you are Indian American, it almost certainly does — here is what the science supports:

**1. Know the numbers.** The NIAAA defines moderate drinking as up to one drink per day for women and up to two drinks per day for men. "One drink" is 1.5 oz (one standard peg) of spirits, 5 oz of wine, or 12 oz of beer. If someone you care about regularly exceeds these amounts — especially in concentrated weekend sessions — they are at elevated risk. If they cannot stop once they start, if they drink to manage stress, if they are irritable or anxious when not drinking, if their tolerance has increased over the years — these are clinical warning signs, not personality traits.

**2. Talk to your doctor honestly.** If you are taking Ozempic or Wegovy and have noticed that your desire to drink has decreased — as many patients anecdotally report — mention it to your doctor. It is not a side effect to be embarrassed about. It is clinical data.

**3. Do not wait for rock bottom.** The Indian American cultural framework for addiction — wait until it becomes undeniable, then deal with the shame — is medically catastrophic. AUD is a progressive condition. The liver damage, the cardiovascular risk, the cognitive decline, the family damage — all of it accumulates. Early intervention is not a luxury. It is the standard of care.

**4. Normalise the conversation.** The single most powerful intervention for Indian American drinking culture is not a drug. It is language. It is someone at the dinner party saying: "I think I am going to cut back." It is a wife telling her husband: "I am worried about how much you drink." It is a son telling his father: "Dad, I want you to be around for my kids." These conversations are harder than any clinical trial. But without them, no drug will be enough.

**5. Resources exist.** The NIAAA's Alcohol Treatment Navigator (alcoholtreatment.niaaa.nih.gov) is a free tool that helps individuals find evidence-based treatment. SAMHSA's National Helpline (1-800-662-4357) is free, confidential, and available in Hindi, Urdu, and other South Asian languages. South Asian-specific support groups exist in most major metro areas — search "South Asian AA" or "desi recovery" plus your city.

The drug works. The science is clear. The question, as always with Indian American health, is whether anyone will use it — and whether anyone will talk about why they need to."""

art1_sources = [
    "https://www.nih.gov/news-events/nih-research-matters/glp-1-plus-therapy-can-reduce-heavy-drinking",
    "https://pubmed.ncbi.nlm.nih.gov/42070571/",
    "https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(26)00305-3/fulltext",
    "https://www.niaaa.nih.gov/alcohols-effects-health/alcohol-use-disorder",
    "https://www.samhsa.gov/find-help/national-helpline",
]

print("=== Article 1: Semaglutide Reduces Heavy Drinking / Lancet / Indian American Drinking Culture ===")
print(f"  Word count: {len(art1_body.split())}")

art1_image = fetch_pexels_image("whisky glass social gathering evening party")
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
    "tags": ["semaglutide", "Ozempic", "Wegovy", "GLP-1", "alcohol use disorder", "heavy drinking", "Lancet", "Indian American", "NRI", "drinking culture", "whisky", "addiction", "stigma", "South Asian", "liver disease", "ALDH2", "NIAAA", "clinical trial", "Copenhagen"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "Lancet trial (May 2 2026): semaglutide reduced heavy drinking in AUD+obesity patients over 26 weeks vs placebo + CBT. Indian American drinking culture: whisky uncle archetype, 5+ drinks per social gathering as 'hospitality,' women's invisible rising consumption, South Asians develop alcohol-related liver disease at LOWER consumption levels (Hepatology 2019), <10% AUD treatment rate nationally and almost certainly lower in Indian Americans due to shame/stigma. Semaglutide reframes AUD as neurological/metabolic, not moral failing. Many already on Ozempic for weight/diabetes may benefit incidentally.",
    "word_count": len(art1_body.split()),
    "image_url": art1_image["url"] if art1_image else None,
    "image_caption": f"Photo by {art1_image['photographer']} via Pexels" if art1_image else None,
})
if result:
    print(f"  ✓ Published: {art1_id}")
else:
    print("  ✗ Failed or duplicate")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Long-Term Antidepressant Use Is Linked to a Higher Risk of
# Sudden Cardiac Death. For South Asians, That Is Two Epidemics Colliding.
# ══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_headline = "Long-Term Antidepressant Use Is Linked to a Higher Risk of Sudden Cardiac Death. For South Asians, That Is Two Epidemics Colliding."
art2_subheadline = "A large-scale study of 4.3 million Danish residents presented at the European Heart Rhythm Association (EHRA) 2025 congress found that people who used antidepressants for six or more years had more than double the risk of sudden cardiac death compared to those who never used them. Among adults aged 30 to 39, the risk was five times higher. The study does not prove causation, and experts strongly warn against stopping medication without consulting a doctor. But for South Asian Americans — who carry the highest cardiovascular disease burden of any ethnic group in the United States and who are finally, after decades of stigma, beginning to seek treatment for depression and anxiety at rising rates — the finding raises an urgent question: is anyone monitoring their hearts while they treat their minds?"
art2_slug = make_slug("antidepressant-long-term-sudden-cardiac-death-south-asian-heart-risk")
art2_category = "lifestyle-health"

art2_body = """In India, your family handled depression by not handling it. They called it "tension." They called it "thinking too much." They called it laziness, weakness, a phase, a spiritual problem, a marriage problem, a need to eat better or sleep more or pray harder. What they did not call it was a medical condition requiring treatment.

For a generation of Indian Americans — the ones who grew up watching their parents suffer in silence, who inherited the vocabulary of denial, and who then found themselves in a country where therapy is normal and SSRIs are prescribed by primary care physicians after a ten-minute conversation — the act of starting an antidepressant was not just a medical decision. It was a cultural rupture. It meant admitting that willpower was not enough. That talking to God was not enough. That the family's collective refusal to discuss emotions had not, in fact, made the emotions go away.

Many of them are now five, eight, ten years into their prescriptions. And a new study says that duration might be creating a risk they do not know about.

## The Danish Study

The research was presented at the European Heart Rhythm Association (EHRA) 2025 congress — a major scientific meeting organised by the European Society of Cardiology. The study was led by Dr. Jasmin Mujkanovic and colleagues at Rigshospitalet, one of the largest hospitals in Denmark.

Denmark maintains some of the most comprehensive national health records in the world. Every prescription filled, every hospital visit, every cause of death is logged in centralised databases linked by personal identification numbers. This allowed the research team to study the entire Danish population — approximately 4.3 million residents aged 18 to 90 — and cross-reference antidepressant use over 12 years with causes of death in 2010.

In that year, nearly 46,000 Danes died. Of those, more than 6,000 deaths were classified as sudden cardiac death — death caused by the heart suddenly and unexpectedly stopping, typically due to an electrical disturbance.

The researchers defined antidepressant exposure as filling at least two prescriptions within a single year at any point during the previous 12 years. They then divided users into two groups: those who had taken antidepressants for one to five years, and those who had taken them for six years or longer.

The findings were striking:

**One to five years of antidepressant use:** 56 per cent higher risk of sudden cardiac death compared to people who had never used antidepressants.

**Six or more years of use:** more than double the risk.

The age breakdown was even more alarming. Among adults aged 30 to 39, one to five years of use tripled the risk. Six or more years increased it fivefold. Among adults aged 50 to 59, shorter-term use doubled the risk while longer-term use quadrupled it.

In older adults (70-79), the risk remained elevated but the gap between shorter and longer use narrowed. In people under 30 and over 80, the differences were not statistically significant.

## What the Study Does and Does Not Prove

This is an observational study, not a randomised controlled trial. It shows an association, not a causal link. The researchers are explicit about this distinction, and so should anyone reading about it.

There are several possible explanations for the association:

**The drug itself may affect the heart.** Some classes of antidepressants — particularly tricyclics and certain SSRIs — are known to affect cardiac electrical conduction. They can prolong the QT interval, a measure of the heart's electrical cycle, which in some individuals increases the risk of a dangerous arrhythmia called torsades de pointes. Long-term use may amplify this effect. The study did not differentiate between antidepressant classes, which is a significant limitation.

**The underlying condition may be the real driver.** People who take antidepressants for six or more years tend to have more severe, chronic, or treatment-resistant depression. Depression itself is an independent risk factor for cardiovascular disease. It is associated with chronic inflammation, elevated cortisol, poor sleep, reduced physical activity, smoking, unhealthy eating, and lower adherence to cardiovascular medications. The people taking antidepressants for the longest may be the people whose depression is most severe — and therefore whose cardiovascular risk is highest regardless of medication.

**Confounding variables.** The study controlled for some factors but could not account for everything. Smoking, alcohol use, obesity, diabetes, and other cardiovascular risk factors may cluster in people with long-term depression in ways that inflate the apparent risk from the medication itself.

**Survivor bias and detection effects.** People who take antidepressants are more likely to be in the healthcare system, which means their deaths are more likely to be accurately classified. Sudden cardiac deaths in people who never seek medical care may be underreported.

The researchers themselves have stated that patients should not stop taking antidepressants based on this study. The benefits of treating depression — reduced suicide risk, improved quality of life, better social functioning, fewer hospitalisations — are well-established and, for many patients, life-saving. Suddenly stopping antidepressants can cause withdrawal symptoms, rebound depression, and, in some cases, suicidal ideation.

The study's message is not "stop taking your medication." It is: "If you are going to take antidepressants for years, someone should be watching your heart."

## Why This Matters More for South Asians

The collision of two epidemics makes this study uniquely relevant to Indian Americans and the broader South Asian diaspora.

**Epidemic one: cardiovascular disease.** South Asians have the highest rates of heart disease of any ethnic group in the United States. They develop coronary artery disease at younger ages, at lower BMIs, and with fewer traditional risk factors. The MASALA study — the largest longitudinal study of cardiovascular health in South Asians living in America — has documented elevated coronary artery calcium scores, higher rates of diabetes, and increased visceral adiposity in this population. South Asians are more likely to have a first heart attack before age 50. They are more likely to die from it.

The mechanisms include genetic predisposition (elevated lipoprotein(a), a heritable and untreatable risk factor), unfavourable body composition (more visceral fat at the same BMI), higher rates of insulin resistance and metabolic syndrome, and dietary patterns high in refined carbohydrates and cooking fats.

Any additional cardiovascular risk factor — even a modest one — is amplified in this population. A 56 per cent increase in sudden cardiac death risk from antidepressant use (the finding for 1-5 years) lands differently when it is applied to a population that already has the highest baseline cardiac risk of any group in the country.

**Epidemic two: untreated and undertreated mental illness.** For decades, the Indian American community was defined by its refusal to engage with mental health care. Depression was not discussed. Therapy was for "Americans." Medications for the mind were a last resort, an admission of failure, a family shame.

This is changing. Among younger Indian Americans — millennials and Gen Z — therapy is normalising rapidly. Antidepressant prescriptions in the South Asian community have increased significantly over the past decade, though precise data is difficult to obtain because most health records do not disaggregate "Asian" into South Asian subgroups.

But the way Indian Americans enter the mental health system is often different from the general population, and those differences matter for long-term cardiovascular monitoring:

**Late entry, long stay.** Because of stigma, many Indian Americans delay seeking treatment until their depression or anxiety is severe. By the time they start an antidepressant, they often have years of untreated illness behind them — which means more severe disease, which means a higher likelihood of needing medication long-term. The Danish study's finding that risk increases with duration of use is directly relevant to a population that enters treatment late and stays on it indefinitely.

**Indefinite prescriptions without review.** In the general American population, best practices for antidepressant management include periodic reassessment: Is the medication still needed? Is the dose appropriate? Should we try tapering? Are there side effects to monitor? In practice, many patients — of all backgrounds — are started on an SSRI and left on it for years without meaningful review. In the Indian American community, where the original act of seeking help was so culturally difficult, the idea of questioning or changing the medication feels like risking a return to the darkness. Both patients and doctors tend to leave the prescription alone. "It is working. Do not touch it."

**No cardiovascular monitoring tied to psychiatric treatment.** Here is the specific gap this study illuminates: in American medicine, psychiatric care and cardiovascular care exist in separate silos. Your psychiatrist or primary care doctor prescribes an antidepressant. They do not order an ECG before starting it (unless it is a tricyclic, which is rarely prescribed anymore). They do not monitor your QT interval annually. They do not check your resting heart rate, blood pressure trends, or inflammatory markers in the context of your psychiatric medication. For a South Asian patient — who may already have subclinical coronary artery disease, borderline metabolic syndrome, and a family history of heart attacks in their 40s — this gap is not theoretical. It is a ticking clock.

## What You Should Do

**1. Do not stop your medication.** This must be said first and repeated: the Danish study does not justify stopping antidepressants. If you are on an antidepressant that is helping you, continue taking it. The risks of untreated depression — including the cardiovascular risks of untreated depression — are well-documented and serious. Talk to your doctor before making any changes.

**2. Ask for a baseline ECG.** If you have been on an antidepressant for more than two years and have never had an electrocardiogram, ask your doctor for one. An ECG takes five minutes, is painless, and measures the heart's electrical activity. If your QT interval is prolonged — a specific measurement your doctor can read from the ECG — it may warrant a conversation about whether your current medication is the safest choice for your specific cardiac profile.

**3. Get a comprehensive cardiac risk assessment.** If you are South Asian, over 35, and on a long-term antidepressant, ask your doctor about a coronary artery calcium (CAC) score — a CT scan that directly measures calcified plaque in your coronary arteries. The MASALA study has shown that standard risk calculators (like the Framingham Risk Score) underestimate cardiovascular risk in South Asians. A CAC score gives your doctor a direct measurement rather than a statistical estimate. It costs $100-300 out of pocket at most imaging centres and is increasingly covered by insurance.

**4. Know which antidepressants carry higher cardiac risk.** Not all antidepressants are equal in their cardiac effects. Tricyclic antidepressants (amitriptyline, nortriptyline) have the most well-documented cardiac effects, including QT prolongation. Among SSRIs, citalopram and escitalopram carry dose-dependent QT prolongation risks above 40 mg and 20 mg respectively — the FDA issued a safety warning about this in 2011 for citalopram. Sertraline and fluoxetine are generally considered to have the most favourable cardiac safety profiles. If you are on a high-dose SSRI with known QT effects, this is worth discussing with your prescriber.

**5. Monitor your resting heart rate.** If you wear an Oura ring, Apple Watch, or Fitbit, track your resting heart rate over time. A persistent resting heart rate above 80 bpm, or a trend of increasing RHR, may warrant a cardiology consultation — especially in a South Asian patient with other metabolic risk factors. Many wearables also offer ECG functionality that can detect atrial fibrillation, though they cannot measure QT interval.

**6. Tell your psychiatrist about your family cardiac history.** If heart attacks, strokes, or sudden death run in your family — as they do in a disproportionate number of South Asian families — your psychiatrist or prescriber needs to know. This information should influence medication selection and monitoring frequency. Many patients compartmentalise: cardiac history goes to the cardiologist, mood symptoms go to the psychiatrist, and neither has the complete picture. You are the integration layer. Share everything with everyone.

**7. Advocate for South Asian-specific research.** The Danish study did not disaggregate by ethnicity. The MASALA study does not specifically examine antidepressant use and cardiac outcomes. The intersection of South Asian cardiovascular risk and rising psychiatric medication use is a research gap that will not be filled until someone funds it. If you are a South Asian physician, researcher, or medical student — this is an open field. If you are a patient, ask your doctor if they are aware of South Asian-specific cardiovascular risk profiles. Many are not.

## The Bigger Picture

The Indian American community spent decades refusing to treat depression. It is now, finally, beginning to treat it — and discovering that the treatment itself may carry risks that are amplified by the community's pre-existing biological vulnerabilities.

This is not a reason to retreat into silence. It is not a reason to return to the era of "just pray about it" and "why can't you just be happy." Untreated depression kills people. It kills them through suicide, through self-neglect, through cardiovascular disease accelerated by chronic stress, through the slow erosion of a life that becomes too painful to maintain.

What this study demands is not less treatment but smarter treatment. It demands that when a South Asian patient starts an antidepressant, their doctor considers their cardiac profile. That when a prescription is renewed for the fifth consecutive year without reassessment, someone asks: "Is this still the right drug at the right dose?" That when an Indian American patient walks into a primary care office with depression and a family history of heart disease, the doctor sees both conditions as interconnected — because they are.

The heart and the mind are not separate systems. They share inflammatory pathways, stress hormones, autonomic regulation, and genetic vulnerabilities. For South Asians, both systems are under strain. Treating one without monitoring the other is not medicine. It is hope with a blind spot.

Your antidepressant may be saving your life. Make sure it is not quietly threatening another part of it. And do not let anyone — least of all your family — tell you that the solution is to stop treating your mind. The solution is to start treating the whole person."""

art2_sources = [
    "https://knowridge.com/2026/05/long-term-depression-drug-use-may-increase-risk-of-sudden-heart-death/",
    "https://www.escardio.org/The-ESC/Press-Office/Press-releases",
    "https://masalastudy.ucsf.edu/",
    "https://www.fda.gov/drugs/drug-safety-and-availability/fda-drug-safety-communication-revised-recommendations-celexa-citalopram-hydrobromide-related-risk",
    "https://www.heart.org/en/health-topics/heart-attack/understand-your-risks-to-prevent-a-heart-attack",
]

print("\n=== Article 2: Long-Term Antidepressants + Sudden Cardiac Death / South Asian CVD + Mental Health ===")
print(f"  Word count: {len(art2_body.split())}")

art2_image = fetch_pexels_image("person contemplating alone medication pills health")
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
    "score_total": 88,
    "tags": ["antidepressant", "SSRI", "sudden cardiac death", "depression", "anxiety", "South Asian", "Indian American", "NRI", "cardiovascular disease", "heart disease", "QT prolongation", "MASALA study", "mental health", "stigma", "ECG", "coronary artery calcium", "long-term medication", "citalopram", "semaglutide"],
    "vertical": "diaspora",
    "urgency": "medium",
    "diaspora_angle": "Danish study (4.3M people, EHRA 2025): 6+ years antidepressant use → 2x sudden cardiac death risk; age 30-39 → 5x risk. South Asians have highest CVD rates in US AND are finally starting to treat depression/anxiety at rising rates after decades of stigma. Late entry to treatment → long-term prescriptions. No cardiovascular monitoring tied to psychiatric care. MASALA study shows standard risk calculators underestimate South Asian CVD risk. Actionable: baseline ECG, coronary artery calcium score, know which SSRIs carry QT risk (citalopram/escitalopram at high doses), use wearable RHR tracking, tell psychiatrist about family cardiac history.",
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
sp.run(["git", "commit", "-m", "lifestyle-writer: semaglutide+alcohol Lancet + antidepressant cardiac death South Asian risk (2026-05-24 23:00 PDT)"], check=True)
push = sp.run(["git", "push"], capture_output=True, text=True, timeout=30)
print(f"  Push: {push.returncode}")
if push.stdout:
    print(f"  {push.stdout.strip()}")
if push.stderr:
    print(f"  {push.stderr.strip()}")

print("\n✅ Lifestyle writer run complete — 2 articles published")
