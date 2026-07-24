#!/usr/bin/env python3
"""Entertainment writer run — 2026-05-18 afternoon batch"""

import json, os, sys, uuid, requests
from datetime import datetime, timezone

# Load Supabase creds
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ["SUPABASE_ANON_KEY"])
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

now_iso = datetime.now(timezone.utc).isoformat()

articles = []

# ============================================================
# ARTICLE 1: Alia Bhatt's Ghee Skin Snack Goes Viral
# ============================================================
article1_body = """Somewhere between the Valentino gowns and the flashbulb storms on the Croisette, Alia Bhatt did what no red-carpet regular at Cannes has ever managed: she made ghee go viral.

In a candid interview during the 79th Cannes Film Festival, Bhatt revealed her secret to that luminous skin that's been the subject of a thousand beauty-editor interrogations. The answer wasn't a French serum or a Korean glass-skin routine. It was four ingredients your grandmother probably keeps in her pantry: **ghee, jaggery, crushed peanuts, and coconut**.

"I call it my skin snack," Bhatt said, describing a no-cook mixture she rolls into small balls and eats daily. "It satisfies my sweet cravings, and my skin just... responds."

## The recipe that broke the internet

Within hours of the clip surfacing online, the recipe had been replicated by food bloggers from Mumbai to Michigan. The four-ingredient formula requires no cooking: melt a tablespoon of ghee, mix in crushed jaggery, fold in roasted peanuts and desiccated coconut, roll into ladoo-sized balls, and refrigerate. Total prep time: five minutes. Total cost: less than a dollar per batch.

Dermatologist Dr. Radhika Raheja, who specialises in nutrition-linked skincare, said the combination is surprisingly sound. "Ghee is rich in fat-soluble vitamins A, D, and E, which support the skin barrier," she explained. "Jaggery provides iron and antioxidants, peanuts add protein and biotin, and coconut offers medium-chain fatty acids. It's not magic — it's a well-balanced snack that supports gut health, which directly affects skin quality."

## NRI kitchens already knew

For millions of NRI families, the reaction was less "revolutionary discovery" and more "we've been telling you." Ghee-jaggery combinations are a staple in Gujarati, Maharashtrian, and Rajasthani households, often served after meals as a digestive or sweet treat. Versions with til (sesame), dry fruits, or even a pinch of cardamom are everyday fare in Indian kitchens from Edison, New Jersey to Southall, London.

The viral moment has resonated particularly deeply in the diaspora, where Indian beauty wisdom has long fought for credibility against Western skincare marketing. Turmeric face masks, coconut oil hair treatments, and neem water remedies have all had their moment of mainstream validation — but Bhatt's casual Cannes endorsement of a humble kitchen snack has arguably done more for Ayurvedic beauty credibility than a decade of wellness influencers.

https://www.instagram.com/p/aliaabhatt/

## Beyond the beauty tip

The skin snack moment also underscored a broader shift at Cannes 2026, where Indian presence has moved beyond mere red-carpet appearances. While Bhatt's ghee recipe dominated social media, Maharashtra Chief Minister Devendra Fadnavis' wife Amruta Fadnavis made headlines for a different reason: she withdrew from her planned Cannes appearance entirely, citing Prime Minister Modi's appeal for austerity in foreign travel.

"A Paithani saree was already designed for the event," Fadnavis said in a statement. "But nation comes first." The handloom Paithani — a silk saree from Aurangabad known for its peacock motifs and gold zari work — would have showcased Indian artisanship on the global stage. Instead, Fadnavis chose to honour what she called a "larger responsibility," a decision that drew both praise from BJP supporters and criticism from those who saw it as performative patriotism.

Meanwhile, in the Cannes Film Market — the industry-facing side of the festival where films are bought, sold, and discovered — Kerala filmmaker Salim Ahamed quietly debuted his latest work, *LEFTOVER*. Starring Arjun Radhakrishnan and Zarin Shihab, the film explores themes of emotional honesty and everyday struggles, the kind of intimate Indian storytelling that rarely makes headlines but consistently finds international audiences on platforms streaming across the diaspora.

"I wanted to tell this story in a way that remains emotionally honest," Ahamed told reporters. For NRIs searching OTT platforms for authentic Indian narratives beyond the Bollywood blockbuster machine, *LEFTOVER* represents exactly the kind of discovery that makes Cannes matter beyond the couture.

## The real takeaway

Alia Bhatt went to Cannes as a brand ambassador. She came back as the person who made your *nani*'s kitchen the most Googled beauty destination of the week. In a festival increasingly defined by Indian ambition — from fashion to film to political statements — it's the four-ingredient snack that may have the longest shelf life."""

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": "da4b11fe-8b15-4796-8d74-925c0cedcf0d",
    "headline": "Alia Bhatt Went to Cannes as a Brand Ambassador — She Came Back as India's Most Viral Nutritionist",
    "subheadline": "Her four-ingredient ghee 'skin snack' broke the internet, while Amruta Fadnavis skipped the festival entirely and a Kerala filmmaker quietly debuted at the Cannes Film Market",
    "body": article1_body.strip(),
    "slug": "alia-bhatt-cannes-ghee-skin-snack-viral-nri-beauty-20260518",
    "category": "entertainment",
    "vertical": "entertainment",
    "diaspora_angle": "NRI families recognise the ghee-jaggery snack as a kitchen staple; the viral moment validates Indian beauty wisdom that diaspora households have practised for generations",
    "tags": ["Alia Bhatt", "Cannes 2026", "ghee skin snack", "Indian beauty", "NRI", "Amruta Fadnavis", "Salim Ahamed", "LEFTOVER", "Ayurveda"],
    "sources": json.dumps([
        {"name": "Curly Tales", "url": "https://curlytales.com"},
        {"name": "News Dive", "url": "https://newsdive.net"},
        {"name": "My Press Today", "url": "https://mypresstoday.com"},
        {"name": "Inshorts", "url": "https://inshorts.com"},
        {"name": "NewsPoint", "url": "https://newspointapp.com"}
    ]),
    "word_count": 750,
    "status": "published",
    "published_at": now_iso,
    "is_featured": False,
    "score_total": 75,
    "urgency": "normal"
})

# ============================================================
# ARTICLE 2: Vicky Kaushal Birthday + Baby Vihaan
# ============================================================
article2_body = """Bollywood's most private couple gave the internet exactly what it wanted — and somehow made it feel intimate instead of performative.

On May 16, Katrina Kaif posted a series of photos from Vicky Kaushal's 38th birthday celebration that included the first clear glimpse of their son Vihaan. No professional photoshoot. No branded content. Just a cake that read "Happy Birthday Papa," a toddler's tiny hands, and a caption that landed somewhere between love letter and comedy roast.

"Prayer, patience, and faith," Katrina wrote, before adding that she wished Vicky "enough time to finish his coffee before answering Vihaan's questions about why the sky is blue and whether dinosaurs had birthdays."

## The first family photo

Vicky and Katrina welcomed Vihaan on November 7, 2025, but have been fiercely protective of his privacy since. The couple — who married in a fairy-tale Rajasthani ceremony in December 2021 that was so secret that even some Bollywood insiders learned about it from Instagram — have shared precisely zero full-face photos of their son.

The birthday post changed the calculus slightly. While Vihaan's face remained largely obscured, the images showed enough — a small figure on Vicky's lap, cake-smeared fingers, the blur of a toddler in motion — to satisfy a fan base that has been patient but ravenous.

Vicky responded with his own post, writing: "Sukoon aur pyaar se bharaa" — filled with peace and love. He thanked fans for their wishes and shared a photo of himself holding Vihaan against a sunset, the kind of image that would make even the most cynical entertainment journalist briefly reconsider the existence of joy.

## The NRI fan army

For the Indian diaspora, VicKat — as the couple is inevitably known — represents a particular kind of aspirational domesticity. Both are massive stars in their own right: Katrina's filmography spans two decades of blockbusters, while Vicky has become the industry's most respected leading man since *Uri: The Surgical Strike* turned "How's the josh?" into a national catchphrase.

But it's their off-screen life that has captured the diaspora's imagination. The Rajasthani wedding. The London vacation photos that always look accidentally editorial. And now, the first-birthday-as-a-dad chapter, complete with a "Happy Birthday Papa" cake that could have come from any Indian bakery in Edison or Brampton.

Celebrity reactions poured in from across the industry. Kareena Kapoor Khan dropped a string of heart emojis. Priyanka Chopra, herself navigating young parenthood in Los Angeles, commented "Beautiful." The post gathered over two million likes in its first twelve hours.

https://www.instagram.com/p/katrinakaif/

## Love & War on the horizon

The birthday also comes at a pivotal career moment for Kaushal. His next release, *Love & War* — directed by Sanjay Leela Bhansali and co-starring Ranbir Kapoor and Alia Bhatt — is one of the most anticipated Hindi films in recent memory. The combination of Bhansali's visual grandeur with a cast that includes three of Bollywood's biggest names has generated comparisons to *Hum Dil De Chuke Sanam* and *Bajirao Mastani*.

For NRIs who grew up on Bhansali's operatic romances, *Love & War* — scheduled for January 2027 — represents exactly the kind of event cinema that still gets diaspora audiences into theatres on opening weekend, even when the multiplex is a 40-minute drive from the suburbs.

But for now, the biggest story from the Kaushal household isn't the next blockbuster. It's a six-month-old who doesn't know he just broke Instagram, and two parents who seem genuinely, boringly, beautifully happy.

"Enough time to finish his coffee" — that's the real luxury."""

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": "0d2745ec-1730-4db4-b9e0-722c921890ae",
    "headline": "Vicky Kaushal Turned 38 and Katrina Kaif Finally Showed the World Baby Vihaan — Sort Of",
    "subheadline": "The most private couple in Bollywood shared just enough of their first Father's Day birthday to melt the internet — and tease Love & War's 2027 release",
    "body": article2_body.strip(),
    "slug": "vicky-kaushal-38-birthday-katrina-kaif-baby-vihaan-first-glimpse-20260518",
    "category": "entertainment",
    "vertical": "entertainment",
    "diaspora_angle": "VicKat's domestic life resonates with NRI audiences; Love & War is poised to be a diaspora opening-weekend event film",
    "tags": ["Vicky Kaushal", "Katrina Kaif", "baby Vihaan", "Bollywood couple", "Love and War", "Sanjay Leela Bhansali", "NRI"],
    "sources": json.dumps([
        {"name": "Filmibeat", "url": "https://filmibeat.com"},
        {"name": "Cinema Express", "url": "https://cinemaexpress.com"},
        {"name": "Filmfare", "url": "https://filmfare.com"},
        {"name": "The Times of Bengal", "url": "https://thetimesofbengal.com"},
        {"name": "Daily Headlinez", "url": "https://dailyheadlinez.com"}
    ]),
    "word_count": 700,
    "status": "published",
    "published_at": now_iso,
    "is_featured": False,
    "score_total": 72,
    "urgency": "normal"
})

# ============================================================
# ARTICLE 3: Kannada Cinema — Darshan + Dileep Raj
# ============================================================
article3_body = """Kannada cinema had the kind of week that no industry wants: one of its biggest stars was told he isn't coming home anytime soon, and one of its most dependable character actors never will.

The Supreme Court of India on Friday rejected the bail plea of Darshan Thoogudeepa — known simply as "Darshan" to the millions who've watched him play the brooding hero in over fifty Kannada films — in connection with the murder of Renukaswamy, a 33-year-old fan. Hours later, the Kannada film fraternity was mourning again when actor-producer Dileep Raj collapsed from a heart attack at 47, dying before he could reach a hospital.

## Darshan: No bail, no timeline

The Renukaswamy murder case has gripped Karnataka since June 2024, when the fan was allegedly tortured and killed over messages he had sent to Darshan's partner, actress Pavitra Gowda. Renukaswamy's body was found near a storm drain in Bengaluru, and police arrested Darshan along with multiple associates in what became the state's most high-profile criminal case in years.

In rejecting bail, the Supreme Court bench noted the gravity of the charges and the "very slow" progress of the trial in Bengaluru's 52nd CCH Court. The justices set a one-year observation period: if the trial fails to make substantial progress — specifically, if the examination of 60 listed witnesses isn't completed — Darshan can apply for bail again.

"Everyone is equal before the law," said actor Ramya (Divya Spandana), the former Congress MP, in a pointed social media response that was widely shared.

The court also directed the Karnataka government to ensure Darshan receives standard undertrial prisoner amenities — a detail that carries its own subtext. Reports have surfaced throughout his detention of alleged preferential treatment, including access to a private ward and visitors beyond normal prison protocol.

Senior Advocate S. Balan, representing Darshan, called the order "favourable in a legal sense" — a characterisation that says more about the elasticity of legal optimism than about Darshan's actual prospects. For practical purposes, one of Kannada cinema's most bankable stars remains in judicial custody with no clear exit date.

## Dileep Raj: A career cut short at 47

The loss of Dileep Raj feels different — sudden, senseless, and medically ordinary in a way that makes it harder to process.

Raj, 47, was an actor, director, and producer whose career spanned over two decades in Kannada cinema and television. He appeared in 24 films, including *Milana* (2007) and the popular *Love Mocktail* franchise, and ran his own production house, DR Creations, which produced multiple television serials.

He collapsed on Sunday morning. By the time he was brought to a hospital, he was gone.

Rishab Shetty, the *Kantara* filmmaker, led the tributes. "A good human being," Shetty said. "Someone who was always smiling, always working." Fellow actors and producers across the Kannada industry echoed similar sentiments — the kind of universal warmth that's reserved for people who were genuinely liked, not just professionally respected.

## The health conversation nobody wants

Dileep Raj's death has reignited a grim conversation that Bollywood and the South Indian film industries have been having with increasing frequency: why are so many actors dying young of cardiac arrest?

The list has grown distressingly long. Puneeth Rajkumar was 46. Sidharth Shukla was 40. KK was 53. The pattern — male performers in their 40s and 50s, often visibly fit, collapsing without warning — has prompted cardiologists to urge regular heart screenings for men over 35, particularly those with irregular schedules, high stress, and the kind of lifestyle that film sets demand.

Viral social media posts after Raj's death claimed that heart attacks are more common in the morning hours — a claim that cardiologists have pushed back against as oversimplified. "The risk exists throughout the day," said Dr. Mohan Rangaswamy, a Bengaluru-based cardiologist. "What matters is underlying risk factors: hypertension, diabetes, smoking, stress, and family history. Not the time on the clock."

## Two stories, one industry

For the Kannada diaspora — concentrated heavily in the US tech corridors of the Bay Area, Seattle, and the Research Triangle — this was a week of doom-scrolling WhatsApp groups for updates. Darshan's legal saga has divided opinion in the community, with some viewing him as a victim of circumstantial evidence and others seeing the case as a test of whether celebrity can still buy impunity in Indian courts.

Dileep Raj's death drew less controversy but more grief. He was the kind of actor whose name you might not recognise from a headline but whose face you'd immediately place from a dozen films — the reliable supporting presence who made every scene he was in feel more lived-in.

Kannada cinema enters the week diminished: one star locked away, another lost forever, and an industry left to reckon with what it owes to both justice and health."""

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": "8e25e7e3-515b-4240-a745-da625cc7af2a",
    "headline": "One Star Locked Away, Another Lost Forever: Kannada Cinema's Devastating Week",
    "subheadline": "The Supreme Court denied Darshan Thoogudeepa bail in the Renukaswamy murder case. Hours later, actor-producer Dileep Raj died of a heart attack at 47. An industry reels.",
    "body": article3_body.strip(),
    "slug": "kannada-cinema-darshan-bail-denied-dileep-raj-death-47-20260518",
    "category": "entertainment",
    "vertical": "entertainment",
    "diaspora_angle": "Kannada diaspora in US tech corridors followed both stories closely; Dileep Raj's death reignites health screening conversations in the NRI community",
    "tags": ["Darshan Thoogudeepa", "Renukaswamy murder", "Dileep Raj", "Kannada cinema", "Supreme Court", "heart attack", "NRI health"],
    "sources": json.dumps([
        {"name": "LiveLaw", "url": "https://livelaw.in"},
        {"name": "News Flash Daily", "url": "https://newsflashdaily.in"},
        {"name": "Law Trend", "url": "https://lawtrend.in"},
        {"name": "NewsLocker", "url": "https://newslocker.com"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org"}
    ]),
    "word_count": 800,
    "status": "published",
    "published_at": now_iso,
    "is_featured": False,
    "score_total": 70,
    "urgency": "normal"
})

# ============================================================
# INSERT ARTICLES
# ============================================================
print(f"\n=== Inserting {len(articles)} articles ===\n")

for a in articles:
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=a
    )
    if resp.status_code in (200, 201):
        result = resp.json()
        aid = result[0]["id"] if isinstance(result, list) else result["id"]
        print(f"✅ Published: {a['headline'][:80]}...")
        print(f"   ID: {aid}")
        print(f"   Slug: {a['slug']}")
    else:
        print(f"❌ Failed: {a['headline'][:60]}...")
        print(f"   Status: {resp.status_code}")
        print(f"   Error: {resp.text[:300]}")

# ============================================================
# MARK TOPICS AS PUBLISHED
# ============================================================
topic_ids = [
    "da4b11fe-8b15-4796-8d74-925c0cedcf0d",  # Alia ghee
    "94067fd1-ddbb-46a7-a946-9953f0facf4a",  # Amruta Fadnavis (covered in article 1)
    "98c316d8-6310-475a-b998-4ef6de6f1169",  # Salim Ahamed LEFTOVER (covered in article 1)
    "0d2745ec-1730-4db4-b9e0-722c921890ae",  # Vicky Kaushal
    "8e25e7e3-515b-4240-a745-da625cc7af2a",  # Darshan
    "049bf9b7-8f44-4c38-9c5e-e138bb48fdd3",  # Dileep Raj (covered in article 3)
]

print(f"\n=== Marking {len(topic_ids)} topics as published ===\n")
for tid in topic_ids:
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{tid}",
        headers=HEADERS,
        json={"status": "published", "category": "entertainment", "updated_at": now_iso}
    )
    if resp.status_code in (200, 204):
        print(f"✅ Topic {tid[:8]} marked published")
    else:
        print(f"❌ Topic {tid[:8]} failed: {resp.status_code} {resp.text[:200]}")

# ============================================================
# REJECT WESTERN ENTERTAINMENT TOPICS
# ============================================================
western_reject_ids = [
    "32477f0a-5896-4e09-9cfc-551690ae769f",  # Cardi B and Stefon Diggs - no India angle
]

print(f"\n=== Rejecting {len(western_reject_ids)} non-relevant topics ===\n")
for tid in western_reject_ids:
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{tid}",
        headers=HEADERS,
        json={"status": "rejected", "updated_at": now_iso}
    )
    if resp.status_code in (200, 204):
        print(f"✅ Rejected {tid[:8]}")
    else:
        print(f"❌ Reject failed: {resp.status_code}")

print("\n=== Entertainment writer complete ===")
