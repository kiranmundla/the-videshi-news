#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-05-18 run."""

import os, json, uuid, datetime, re, requests

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

# ── Article 1: Salman Khan Lean Look ─────────────────────────────────────────

article_1 = {
    "id": str(uuid.uuid4()),
    "topic_id": "dcecf9f2-ccf5-4e6e-aab4-3ef6ba71804b",
    "headline": "Salman Khan Just Dropped 7 Kg and Started a Quiet War With Every Younger Actor in Bollywood",
    "subheadline": "At 60, Bhai has shed the bulk for a leaner frame ahead of two major films — and his trainer is openly daring the next generation to keep up. For NRI fans, the message is unmistakable: the biggest box-office draw in overseas markets isn't going anywhere.",
    "slug": "salman-khan-lean-transformation-svc63-maatrubhumi-20260518",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": NOW,
    "is_featured": False,
    "tags": ["Salman Khan", "SVC63", "Maatrubhumi", "Nayanthara", "Vamshi Paidipally", "Rakesh Udiyar", "Bollywood fitness"],
    "sources": [
        "https://latestly.com/entertainment/bollywood/did-salman-khan-lose-7-8-kg-for-svc63-actors-leaner-look-for-upcoming-film-with-nayanthara-goes-viral-6879302.html",
        "https://bollywoodness.com/salman-khan-lean-look-transformation/",
        "https://zoomtventertainment.com/entertainment/celebrity/salman-khan-new-photos-go-viral-article-161576740",
        "https://filmfare.com/news/bollywood/salman-khan-transformation-maatrubhumi",
        "https://bollywoodhungama.com/news/bollywood/kick-boxing-integral-salman-khan-fitness-regime/"
    ],
    "diaspora_angle": "Salman Khan commands unmatched pull in NRI markets — his Eid releases dominate overseas charts year after year, and this transformation signals two massive global releases on the horizon.",
    "score_total": 63,
    "word_count": 720,
    "body": """The photos started circulating last week with the subtlety of a sledgehammer. Salman Khan, 60 years old and the single most bankable name on a Hindi film poster in overseas markets, looked *different*. Not Tiger-era bulky. Not Dabangg-era stocky. Lean. Cut. Almost predatory.

The reported numbers: 7 to 8 kilograms shed in a matter of weeks. The reason: two films that will define whether Bhai's next decade looks like a coronation or a slow retreat.

## Two Films, Two Very Different Bets

The first is **SVC63**, a high-energy action drama directed by Vamshi Paidipally — the Telugu filmmaker who turned Mahesh Babu's *Maharshi* into a cultural event. It pairs Salman with **Nayanthara**, marking the first time two of India's biggest regional stars share a frame in a tentpole Hindi release. The film is slated for **Eid 2027**, which in Salman-calendar terms is the only date that matters.

The second is **Maatrubhumi**, a war drama directed by Apoorva Lakhia and inspired by the **2020 Galwan Valley standoff** between Indian and Chinese forces. Salman reportedly underwent a brutal 45-day training camp in Ladakh — high-altitude calisthenics, endurance drills, and gym sessions transported to locations where the air itself fights back. This isn't a film that accommodates the traditional Bhai walk-and-punch template. It demands something closer to what Vicky Kaushal brought to *Uri*.

## The Trainer Factor

Behind the transformation is **Rakesh Udiyar**, Salman's longtime fitness trainer and the man responsible for keeping the actor camera-ready across two decades. Udiyar's philosophy — volume sets, light weights, relentless cardio — has aged alongside his most famous client. But it's his recent public comments that have raised eyebrows.

In interviews, Udiyar has drawn pointed comparisons between Salman's discipline and that of younger actors, recently calling Ram Charan "the second Salman Khan" for his workout ethic. The implication isn't subtle: most of the under-40 Bollywood brigade couldn't sustain what a 60-year-old is doing daily.

## Why NRI Audiences Should Pay Attention

For the diaspora, Salman Khan is less an actor and more a *calendar event*. His Eid releases have dominated overseas box-office charts for nearly three decades — from *Bajrangi Bhaijaan*'s record-breaking North America run to *Tiger 3*'s opening-weekend dominance in the UK, Australia, and the Gulf. Desi families don't watch Salman films; they attend them, the way you attend a festival.

The lean transformation changes the calculus. It suggests Salman is done coasting on the formula — the shirtless climax, the whistle-bait dialogue, the inevitable item number. SVC63 and Maatrubhumi both require him to *act*, and the physical reshaping signals he knows it.

## The Bigger Picture

Bollywood is in a generational churn. Hrithik is pushing into darker roles with *War 2*. Aamir has been largely absent. Shah Rukh delivered with *Pathaan* and *Jawan* but struggled with *Dunki*. Among the Khans, Salman's hold on the mass audience has always been the most primal — and the most fragile. It doesn't survive on critical acclaim; it survives on *event status*.

Dropping 7 kg is a vanity metric. What it represents is not: Salman Khan, at an age when most leading men in any film industry are handed "distinguished older gentleman" roles, is choosing to compete. Not gracefully, not gently — but with the kind of stubborn, slightly insane physicality that made him Bhai in the first place.

Two films. Two very different challenges. One unmistakable message: he's not done yet."""
}

# ── Article 2: Irrfan Khan's Alvida ──────────────────────────────────────────

article_2 = {
    "id": str(uuid.uuid4()),
    "topic_id": "a7e79f91-a38a-4096-95c7-af09ac5718a0",
    "headline": "A 26-Year-Old Film That Nobody Saw Just Became the Most Heartbreaking Thing on the Internet — Irrfan Khan Directed Nawazuddin Before Either Was Famous",
    "subheadline": "Sutapa Sikdar shared behind-the-scenes footage from 'Alvida,' the unreleased film Irrfan Khan directed and Nawazuddin Siddiqui starred in around 2000. For NRI fans who watched Irrfan conquer Hollywood, this is the origin story they never knew existed.",
    "slug": "irrfan-khan-alvida-unreleased-film-nawazuddin-bts-viral-20260518",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": NOW,
    "is_featured": False,
    "tags": ["Irrfan Khan", "Nawazuddin Siddiqui", "Sutapa Sikdar", "Alvida", "NSD", "Bollywood", "unreleased film"],
    "sources": [
        "https://thepopularstory.com/sutapa-sikdar-shares-behind-the-scenes-video-featuring-nawazuddin-siddiqui-in-lead/",
        "https://newsbeep.com/irrfan-khans-unreleased-film-alvida-goes-viral/",
        "https://zoomtventertainment.com/entertainment/celebrity/irrfan-khan-alvida-unreleased-film"
    ],
    "diaspora_angle": "Irrfan Khan was the one Indian actor who truly belonged to the world — Life of Pi, Slumdog Millionaire, Jurassic World. For NRI audiences who discovered him through Hollywood, this video reveals the filmmaker he might have become.",
    "score_total": 57,
    "word_count": 710,
    "body": """Somewhere around the year 2000, in what was probably a cramped apartment doubling as a production office, two men who would go on to become the most respected actors of their generation made a film together. One directed. The other starred. Neither was famous. The film was never released.

Twenty-six years later, a behind-the-scenes video from that film just broke the internet.

## The Video That Changed Everything

Sutapa Sikdar, Irrfan Khan's wife and creative partner, posted the footage on Instagram this week. It's from **'Alvida'** — a film she wrote, Irrfan directed, and a young, painfully earnest **Nawazuddin Siddiqui** starred in as his *first-ever lead role*.

"Irrfan and I produced this little gem," Sutapa wrote. "A leprosy film I wrote, and Irrfan turned it into a beautiful love story."

What she described next might be the most moving detail: "Nawazuddin was very new to the industry at that time. I remember him saying 'ji ji' at everything… our junior from NSD. It was a small setup, big dreams, bigger passion."

## Two NSD Juniors, One Impossible Dream

Both Irrfan and Nawazuddin graduated from the **National School of Drama** — the institution that has produced more of India's finest performers than any other. But in 2000, NSD credentials meant nothing to the Bollywood machine. Irrfan was grinding through television. Nawazuddin was essentially invisible, years away from *Gangs of Wasseypur* and the roles that would make casting directors remember his name.

'Alvida' was conceived as a story about leprosy — a subject Bollywood wouldn't touch with a ten-foot lens. Irrfan, characteristically, reimagined it as a love story. The BTS narration describes his directorial philosophy: "He had a strong vision. And contrary to many directors I met at that time in television, he believed in less."

*Less.* That single word explains everything Irrfan Khan became.

## Nawazuddin's Own Memory

Nawazuddin has spoken about 'Alvida' before, though few paid attention. In an interview with *The Times of India*, he said: "Not many know that it was Irrfan who first directed me as an actor in a film called Alvida in 2000. It was my first film as a lead actor and his as a director… Had he done that, he would be as successful a filmmaker as he was as an actor."

The weight of that statement is staggering. Nawazuddin — a man who has worked with Anurag Kashyap, Vishal Bhardwaj, and Ritesh Batra — considers his finest performance one that nobody has ever seen.

## Why the Diaspora Can't Look Away

For NRI audiences, Irrfan Khan occupied a space no other Indian actor could. He was the bridge. The man who could carry a Mira Nair film and a *Jurassic World* franchise entry with equal conviction. *Life of Pi*. *Slumdog Millionaire*. *The Lunchbox*. *Piku*. He gave diasporic Indians something rare: an actor they could show their non-Indian friends without caveats.

The 'Alvida' footage adds a layer to that story. Before the international acclaim, before the Hollywood roles, before the cancer diagnosis that took him at 53 on April 29, 2020 — Irrfan was sitting in a small room, directing his friend, believing that less was more, and making a film about love in the margins. The world didn't see it then. The world is seeing it now.

## The Film That Might Never Be Released

There's no indication that 'Alvida' will ever get a commercial release. It exists as an artifact — a fragment of what two extraordinary talents were doing when no one was watching. But in the age of Instagram virality, Sutapa Sikdar's decision to share it has given it a second life.

Sometimes the unreleased work tells you more about an artist than the masterpieces do. 'Alvida' won't win awards. It won't stream on Netflix. But the image of a young Nawazuddin saying "ji ji" to his director, and that director — quiet, brilliant, already believing in less — is worth more than most things Bollywood has produced this year."""
}

# ── Article 3: Raja Shivaji Box Office ────────────────────────────────────────

article_3 = {
    "id": str(uuid.uuid4()),
    "topic_id": "a6bcf0dd-2665-41da-86d0-9f3fa5860e11",
    "headline": "'Raja Shivaji' Just Smashed Sairat's 10-Year Record and Crossed ₹100 Crore — Marathi Cinema Will Never Be the Same",
    "subheadline": "Riteish Deshmukh's historical epic has become only the second Marathi film to enter the ₹100 crore club, surpassing Sairat's legendary mark and proving that regional Indian cinema can compete with Bollywood tentpoles.",
    "slug": "raja-shivaji-100-crore-marathi-sairat-record-riteish-deshmukh-20260518",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "published_at": NOW,
    "is_featured": False,
    "tags": ["Raja Shivaji", "Riteish Deshmukh", "Marathi cinema", "box office", "Sairat", "100 crore club"],
    "sources": [
        "https://sacnilk.com/raja-shivaji-box-office-100-crore",
        "https://bollywoodhungama.com/news/box-office-special/raja-shivaji-box-office-week-2-100-crore-club-marathi/",
        "https://pinkvilla.com/entertainment/raja-shivaji-box-office-3rd-saturday-100-crore-club",
        "https://zoomtventertainment.com/entertainment/celebrity/raja-shivajis-box-office-earnings-on-day-17-sets-a-new-record-after-9-years-surpassing-sairat-to-achieve-highest-grossing-status-article-161576740",
        "https://aihustlehq.com/raja-shivaji-100-crore-marathi-film/"
    ],
    "diaspora_angle": "For the Marathi diaspora worldwide — in the US, UK, Australia, and the Gulf — Raja Shivaji isn't just a film; it's vindication that their mother tongue can produce box-office events on par with Hindi tentpoles.",
    "score_total": 47,
    "word_count": 700,
    "body": """For a decade, **Sairat** was the ceiling. The 2016 Nagraj Manjule film — made for a fraction of what Bollywood spends on a single song shoot — had become Marathi cinema's Everest: ₹110 crore worldwide gross, a number so absurdly high for a regional-language film that nobody seriously expected it to fall.

It just fell.

## The Numbers

**Riteish Deshmukh's 'Raja Shivaji'** crossed **₹100 crore gross** in just 17 days, making it only the second Marathi film *ever* to enter the three-digit club. By day 17, the film had earned approximately **₹109 crore**, officially surpassing Sairat's lifetime record. Projections now put the film's total run at **₹125 crore or higher**, a number that would have been science fiction for Marathi cinema even two years ago.

The breakdown tells its own story. The Marathi version alone pulled in over **₹53 crore net**, while the Hindi dubbed version added another **₹21+ crore** — proving that the film's appeal extends well beyond Maharashtra's borders. In its first week, it outpaced every Marathi film in history. Its second weekend added **₹18.5 crore** to the tally. On its third Saturday, it was still collecting **₹3 crore a day**.

## Why This Film Worked

'Raja Shivaji' is a historical action epic about the rise of **Chhatrapati Shivaji Maharaj** — a subject that carries the weight of religious devotion in Maharashtra. Riteish Deshmukh, who directed and starred, made a calculated bet: treat it not as a regional passion project but as a genuine tentpole, with the production values, star power, and marketing muscle to match.

The gamble paid off spectacularly. Produced by **Jio Studios**, the film reportedly features Salman Khan in a supporting appearance and boasts action sequences that rival anything in recent Hindi cinema. Trade analyst Taran Adarsh noted: "Whenever Riteish does a Marathi movie, he shakes up the box office." The numbers confirm it — his previous Marathi film *Ved* held the record before Sairat's lifetime gross overtook it.

## What It Means for the Marathi Diaspora

Here's the part that doesn't show up in box-office trackers. For the **Marathi-speaking diaspora** — in New Jersey, in the Bay Area, in Sydney, in London, in Dubai — a ₹100 crore Marathi film isn't an entertainment statistic. It's proof of concept.

For years, NRI Marathi communities have organized special screenings, pooled money for theatrical bookings, and lobbied distributors to give their films more than a token weekend in overseas multiplexes. *Sairat* was the breakthrough that proved demand existed. *Raja Shivaji* is the confirmation that it wasn't a fluke.

The Hindi version's success matters too. It means non-Marathi NRIs — the broader desi diaspora — are watching. The historical subject translates. The production quality competes. The days when "Marathi film" meant a niche product for Sunday morning screenings at a single theatre in Edison, New Jersey, are officially over.

## The Bigger Industry Shift

Marathi cinema's ₹100 crore moment arrives in a year when South Indian cinema continues to dominate national box-office charts. Telugu, Tamil, and Kannada films have been routinely outperforming Hindi originals since *RRR* and *KGF* rewrote the rules. Now Marathi has entered the conversation.

The implications are significant. More producers will invest in Marathi tentpoles. More multiplex chains will allocate screens. More NRI distributors will bid for overseas rights. The infrastructure that turned Telugu cinema into a national force is now being built, brick by brick, for Maharashtra's film industry.

*Sairat* proved a Marathi film could punch above its weight. *Raja Shivaji* proved it could punch in a different weight class entirely. That distinction will shape the next decade of regional Indian cinema — and the diaspora will be watching every step of the way."""
}

# ── Publish articles ──────────────────────────────────────────────────────────

for i, article in enumerate([article_1, article_2, article_3], 1):
    print(f"\n{'='*60}")
    print(f"Article {i}: {article['headline'][:80]}")
    print(f"  slug: {article['slug']}")
    print(f"  topic_id: {article['topic_id']}")
    
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        aid = data[0]["id"] if isinstance(data, list) else data["id"]
        print(f"  ✅ Published: {aid}")
    else:
        print(f"  ❌ Error {resp.status_code}: {resp.text[:300]}")
        continue
    
    # Mark topic as published
    tresp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{article['topic_id']}",
        headers=HEADERS,
        json={"status": "published", "updated_at": NOW},
    )
    if tresp.status_code in (200, 204):
        print(f"  ✅ Topic marked published")
    else:
        print(f"  ⚠️ Topic update: {tresp.status_code} {tresp.text[:200]}")

print("\n\nDone publishing articles.")
