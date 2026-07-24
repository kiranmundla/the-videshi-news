#!/usr/bin/env python3
"""Videshi Entertainment Writer — 2026-05-25 06:30 PDT run"""
import json, os, sys, uuid, subprocess, re
from datetime import datetime, timezone

# --- Supabase credentials ---
SUPABASE_URL = ""
SUPABASE_KEY = ""
for env_path in [os.path.expanduser("~/.env.supabase"), os.path.expanduser("~/workspace/.env.supabase")]:
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    v = v.strip('"').strip("'")
                    if k == "SUPABASE_URL" and not SUPABASE_URL:
                        SUPABASE_URL = v
                    if k == "SUPABASE_SERVICE_ROLE_KEY" and not SUPABASE_KEY:
                        SUPABASE_KEY = v

print(f"URL: {SUPABASE_URL[:30]}... Key length: {len(SUPABASE_KEY)}")

def check_duplicate(slug):
    """Check if slug already exists"""
    cmd = [
        "curl", "-s",
        f"{SUPABASE_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id,headline&limit=1",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        if data and len(data) > 0:
            print(f"  ⚠️  DUPLICATE: {slug}")
            return True
    except:
        pass
    return False

def insert_article(article):
    """Insert article via curl"""
    if check_duplicate(article["slug"]):
        return None

    tmp_path = "/tmp/videshi-ent-article.json"
    with open(tmp_path, "w") as f:
        json.dump(article, f)

    cmd = [
        "curl", "-s", "-w", "\n%{http_code}",
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        "-X", "POST",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", f"@{tmp_path}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")
    status = lines[-1] if lines else "?"
    body = "\n".join(lines[:-1]) if len(lines) > 1 else ""
    title = article['headline'][:70]
    if status in ("200", "201"):
        print(f"  ✅ Inserted ({status}): {title}...")
        return json.loads(body) if body else True
    else:
        print(f"  ❌ Error ({status}): {title}...")
        print(f"  Response: {body[:500]}")
        return None

def decay_scores():
    """Decay older entertainment articles"""
    from datetime import timedelta
    now_utc = datetime.now(timezone.utc)
    week_ago = (now_utc - timedelta(days=7)).isoformat()
    three_days = (now_utc - timedelta(days=3)).isoformat()

    # 7+ days old, score > 35
    cmd = [
        "curl", "-s", "-w", "\n%{http_code}",
        f"{SUPABASE_URL}/rest/v1/p2_articles?category=eq.Entertainment&published_at=lt.{week_ago}&score_total=gt.35",
        "-X", "PATCH",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=minimal",
        "-d", json.dumps({"score_total": 35})
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    status7 = r.stdout.strip().split("\n")[-1]

    # 3-7 days old, score > 50
    cmd2 = [
        "curl", "-s", "-w", "\n%{http_code}",
        f"{SUPABASE_URL}/rest/v1/p2_articles?category=eq.Entertainment&published_at=lt.{three_days}&published_at=gt.{week_ago}&score_total=gt.50",
        "-X", "PATCH",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=minimal",
        "-d", json.dumps({"score_total": 50})
    ]
    r2 = subprocess.run(cmd2, capture_output=True, text=True)
    status3 = r2.stdout.strip().split("\n")[-1]
    print(f"  Score decay: 7d+ → 35 (HTTP {status7}), 3-7d → 50 (HTTP {status3})")

now = datetime.now(timezone.utc).isoformat()

# ============================================================
# ARTICLE 1: Don 3 — Farhan Akhtar vs Ranveer Singh at FWICE
# ============================================================
article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Ranveer Singh Walked Out of Don 3 After Dhurandhar Made Him Bollywood's Biggest Star. Now Farhan Akhtar Wants ₹40 Crore. The Film Industry's Apex Body Is Deciding Today.",
    "subheadline": "FWICE will announce its ruling at 4 PM IST after Farhan Akhtar escalated the Don 3 dispute through IFTDA. Ranveer has reportedly offered ₹10 crore plus a profit-share stake in Pralay. The Don franchise — India's most iconic gangster saga — has no lead actor, no shoot date, and no resolution.",
    "slug": "don-3-farhan-akhtar-ranveer-singh-fwice-40-crore-dispute-ruling-20260525",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "breaking",
    "status": "published",
    "published_at": now,
    "score_total": 78,
    "tags": ["Don 3", "Ranveer Singh", "Farhan Akhtar", "FWICE", "Excel Entertainment", "Dhurandhar", "Pralay", "Bollywood dispute", "Don franchise"],
    "diaspora_angle": "The Don franchise is one of Bollywood's deepest cultural touchstones for the diaspora — from Amitabh Bachchan's 1978 original to Shah Rukh Khan's 2006 reinvention. For NRIs who grew up with 'Don ko pakadna mushkil hi nahi, namumkin hai,' the fact that the franchise's third chapter has collapsed into a ₹40 crore legal battle is both surreal and symbolic of how power has shifted in Bollywood's post-Dhurandhar era.",
    "sources": [
        {"url": "https://www.zoomtventertainment.com/bollywood/farhan-akhtar-fwice-don-3-case-ranveer-singh-exit-article-154386645", "name": "Zoom TV"},
        {"url": "https://www.latestly.com/entertainment/bollywood/don-3-row-farhan-akhtar-takes-ranveer-singh-dispute-to-fwice-decision-expected-to-be-taken-today-report-7445307.html", "name": "LatestLY"},
        {"url": "https://bharathorizon.com/farhan-akhtar-files-complaint-against-ranveer-singh-over-don-3-exit", "name": "Bharat Horizon"},
        {"url": "https://presspost.in/farhan-akhtar-approaches-film-body-over-don-3-row-linked-to-ranveer-singh", "name": "PressPost"}
    ],
    "image_search_query": "Don 3 Bollywood film dispute gangster franchise courtroom",
    "image_entities": ["Ranveer Singh", "Farhan Akhtar", "Don franchise"],
    "image_must_show": "Dramatic Bollywood industry dispute or gangster film aesthetic",
    "word_count": 780,
    "body": """The Federation of Western India Cine Employees will hold a press conference at 4 PM IST today to announce its ruling on Farhan Akhtar's formal complaint against Ranveer Singh. The complaint, filed through the Indian Film and Television Directors' Association, alleges that Singh's abrupt exit from *Don 3* caused Excel Entertainment financial losses exceeding ₹40 crore in pre-production costs.

This is not a rumour cycle. This is the film industry's apex body — representing over 500,000 workers — being asked to formally adjudicate a dispute between two of Bollywood's biggest names over one of its most iconic franchises.

## How It Got Here

The timeline is damning.

In 2023, Ranveer Singh was confirmed as the new Don — the franchise's third lead actor after Amitabh Bachchan (1978) and Shah Rukh Khan (2006, 2011). Kiara Advani signed on as the female lead. Vikrant Massey was reportedly set as the antagonist. The script was locked. Pre-production was underway. Excel Entertainment, led by Farhan Akhtar and Ritesh Sidhwani, had committed serious money.

Then *Dhurandhar* happened.

Released in early 2026, Aditya Dhar's espionage thriller became the highest-grossing Bollywood film of all time. Ranveer Singh went from star to institution overnight. And in the aftermath of that success, according to multiple industry reports, he walked out of *Don 3*.

The specifics of the exit remain disputed. Industry sources told Zoom TV that Singh had requested "late-stage modifications to the script" that didn't sit well with Akhtar. A separate line of reporting suggests that Ranveer grew cold on the project after learning that Akhtar had briefly considered replacing him with Hrithik Roshan during a career lull before Dhurandhar — a plan that was dropped once the film became a phenomenon. Hrithik himself publicly denied being approached.

Whatever the precise trigger, the result was unambiguous: by December 2025, Ranveer Singh was out.

## The Money

Excel Entertainment's claim is straightforward: they spent ₹40 crore on pre-production for a film that never shot a single frame. They want that money back.

In April, a Free Press Journal report indicated that Singh offered to return approximately ₹10 crore. The gap between ₹10 crore and ₹40 crore is where the dispute has festered for five months.

The most intriguing development came via Zoom TV: Ranveer has reportedly offered Farhan and Ritesh a profit-share stake in *Pralay*, his next film with director Aditya Dhar. The percentage hasn't been disclosed, but the structure is creative — essentially asking Excel to accept equity in a future hit rather than cash today.

The matter first went to the Producers Guild of India, which advised both parties to settle amicably and avoid litigation. That didn't work. Farhan then filed formally with FWICE through IFTDA. Today's press conference is the result.

## What FWICE Can Actually Do

FWICE is not a court. It cannot compel payment or enforce contracts. But in Bollywood's ecosystem — where relationships, reputation, and informal power structures matter more than legal filings — an FWICE ruling carries real weight.

If the body sides with Farhan, it creates reputational pressure on Ranveer. If it sides with Ranveer, it signals that actors can exit committed projects without full financial consequence. Either outcome sets a precedent that will be studied by every producer and talent agency in Mumbai.

The bigger question is whether FWICE's ruling actually resolves anything, or merely adds another chapter to what has become Bollywood's most public behind-the-scenes feud.

## What Happened to the Franchise

As of today, *Don 3* has no lead actor, no confirmed shoot date, and no release timeline.

Kiara Advani was replaced by Kriti Sanon at some point during the production limbo — reportedly due to "personal circumstances." With the male lead now vacant, Kriti's involvement is also uncertain.

Farhan told *The Hollywood Reporter India* that the script is "something he hopes to explore in the future" — filmmaker code for "this film is shelved until further notice."

The irony is thick. The Don franchise has survived a lead-actor transition once before, when Shah Rukh Khan inherited the role from Amitabh Bachchan. That transition took two decades and produced two commercially successful films. This time, the transition didn't even survive pre-production.

## Why the Diaspora Should Pay Attention

For NRIs who grew up with *Don* — whether it was Amitabh's raw intensity in 1978 or Shah Rukh's sleek reinvention in 2006 — the franchise is more than a film series. "Don ko pakadna mushkil hi nahi, namumkin hai" isn't just a dialogue; it's cultural DNA.

The collapse of *Don 3* into a ₹40 crore legal dispute is symbolic of a larger shift in Bollywood's power dynamics. Before *Dhurandhar*, actors worked within the ecosystem that producers built. After *Dhurandhar*, an actor walked away from one of Bollywood's most prestigious franchises because he could.

Today's FWICE ruling won't resurrect the film. But it will signal whether Bollywood's institutions can still hold its biggest stars accountable — or whether the era of actor supremacy that *Dhurandhar* inaugurated is now beyond anyone's control."""
}

# ============================================================
# ARTICLE 2: Padma Awards 2026 — India Honors Its Icons Today
# ============================================================
article2 = {
    "id": str(uuid.uuid4()),
    "headline": "India Is Giving Dharmendra a Padma Vibhushan Today. He Died Before He Could Receive It. For Every NRI Who Grew Up With Sholay on Sunday Afternoons, This One Hurts.",
    "subheadline": "President Murmu presents 131 Padma Awards at Rashtrapati Bhavan on May 25. Mammootty receives the Padma Bhushan. Alka Yagnik — who lost most of her hearing to a rare sensory disorder — gets the same honour. R. Madhavan and Satish Shah are honoured with Padma Shris. The ceremony is both a celebration and a memorial.",
    "slug": "padma-awards-2026-dharmendra-vibhushan-mammootty-alka-yagnik-madhavan-satish-shah-20260525",
    "category": "Entertainment",
    "vertical": "entertainment",
    "urgency": "developing",
    "status": "published",
    "published_at": now,
    "score_total": 76,
    "tags": ["Padma Awards 2026", "Dharmendra", "Mammootty", "Alka Yagnik", "R. Madhavan", "Satish Shah", "Prosenjit Chatterjee", "Padma Vibhushan", "Padma Bhushan", "Indian cinema"],
    "diaspora_angle": "For the Indian diaspora, Padma Awards are a rare moment when India formally recognizes the people who shaped our childhoods — often decades after they should have been recognized. Dharmendra's posthumous Padma Vibhushan will be received by a family without its patriarch. Alka Yagnik's Padma Bhushan comes after she revealed she can barely hear the songs that defined two generations. Satish Shah's posthumous Padma Shri honours a man whose Sarabhai vs Sarabhai taught NRIs what 'Gujarati humor' meant. Every name on this list is someone your parents had an opinion about.",
    "sources": [
        {"url": "https://glamsham.com/bollywood/news/padma-awards-2026-to-honour-dharmendra-mammootty-alka-yagnik-and-other-entertainment-icons/", "name": "GlamSham"},
        {"url": "https://www.zoomtventertainment.com/bollywood/padma-awards-2026-dharmendra-mammootty-alka-yagnik-may-25", "name": "Zoom TV"},
        {"url": "https://trends.glance.com/padma-shri-unsung-heroes-2026", "name": "Glance"}
    ],
    "image_search_query": "Padma Awards 2026 India ceremony Rashtrapati Bhavan honours",
    "image_entities": ["Dharmendra", "Mammootty", "Alka Yagnik", "Rashtrapati Bhavan"],
    "image_must_show": "Indian national awards ceremony or prestigious honour imagery",
    "word_count": 750,
    "body": """At Rashtrapati Bhavan today, President Droupadi Murmu will present 131 Padma Awards — India's highest civilian honours for exceptional service in arts, science, medicine, and public life. Among the 5 Padma Vibhushans, 13 Padma Bhushans, and 113 Padma Shris, a handful of names will make every Indian in the diaspora pause.

Because these are not just award recipients. They are the people who raised us.

## Dharmendra: Padma Vibhushan (Posthumous)

Dharmendra — born Dharam Singh Deol in Sahnewal, Punjab — will receive India's second-highest civilian honour posthumously. His family will collect the award from the President's hands. He won't be there.

For anyone who grew up in an Indian household, Dharmendra was not a choice. He was a given. *Sholay* on every Sunday afternoon. *Chupke Chupke* whenever someone needed cheering up. *Phool Aur Patthar* when your mother wanted to explain what "real acting" looked like. He was the handsome Jat from Punjab who became Hindi cinema's most beloved everyman — the man who made masculinity feel gentle before anyone knew that was supposed to be revolutionary.

He worked for over six decades. He appeared in more than 300 films. He received a Filmfare Lifetime Achievement Award in 1997. The Padma Vibhushan comes now — after a career that spanned from the Nehru era to the Modi era, after a life that ended before India's bureaucracy could catch up with what every Indian already knew.

The timing is painful and predictable. India's civilian honours have a long history of arriving late. Dharmendra deserved this honour while he could hold it.

## Mammootty: Padma Bhushan

Malayalam cinema's most enduring star receives his second Padma honour — he was awarded the Padma Shri in 1998. Mammootty has worked in Malayalam, Tamil, and Hindi cinema across a career that has produced some of Indian cinema's most complex performances.

For the Malayali diaspora specifically, Mammootty is not just an actor — he is the cultural ambassador of Kerala to the rest of India and to the world. His films travel with the community. His face on a Padma Bhushan citation is a recognition that Malayalam cinema, so often overlooked by Bollywood-centric award bodies, produces artists of the highest calibre.

At this stage of his career, the award is less about what he has done and more about what it says that it took this long.

## Alka Yagnik: Padma Bhushan

This one carries a particular weight.

Alka Yagnik is the voice of two generations of Bollywood. "Taal Se Taal Mila," "Kuch Kuch Hota Hai," "Bole Chudiyan," "Didi Tera Devar Deewana" — name an era of Hindi cinema from the 1980s through the 2000s, and she is the voice that defined it. She holds the record for most songs on YouTube to cross 1 billion views: four. Her cumulative plays exceed 40 billion.

In June 2024, she revealed that she had been diagnosed with a rare sensory neural nerve hearing loss — she can barely hear without hearing aids. The woman who sang the soundtrack of our lives was losing access to her own voice.

The Padma Bhushan arrives in that context. It is deserved. It is overdue. And it is bittersweet in a way that few civilian honours have been. For every NRI who played "Taal Se Taal Mila" at their wedding reception, this moment matters.

## The Others Who Matter

**R. Madhavan — Padma Shri.** Known universally as "Maddy," the actor behind *Rehnaa Hai Terre Dil Mein*, *3 Idiots*, and *Rocketry: The Nambi Effect*. He won a National Award for *Rocketry* in 2023, a film he also directed, produced, and spent seven years making. For NRIs, Madhavan has always been the relatable one — the actor who looks like someone you'd know, who speaks the way educated middle-class India speaks, who pursued science before cinema.

**Satish Shah — Padma Shri (Posthumous).** The comic genius of *Sarabhai vs Sarabhai*, *Yeh Jo Hai Zindagi*, *Main Hoon Na*, and *Hum Aapke Hain Koun*. His timing was impeccable. His range — from buffoon to menace to tenderness — was underappreciated. Another posthumous honour. Another reminder that India's recognition machinery moves slower than its artists.

**Prosenjit Chatterjee — Padma Shri.** Bengali cinema's biggest star, with more than 350 films over nearly five decades. For the Bengali diaspora, Prosenjit is their Amitabh — the actor who made staying in Kolkata feel like a choice, not a consolation.

## What These Awards Mean to the Diaspora

Padma Awards don't come with money. They don't come with creative freedom or better roles. What they do is place names into the official record — India's formal acknowledgement that these individuals shaped the nation's cultural identity.

For NRIs watching from across the world, today's ceremony is a moment to feel connected to an India that still values the people who made us who we are. Even if it values them a few years too late."""
}

# ============================================================
# DECAY + INSERT
# ============================================================
print("\n📉 Applying score decay...")
decay_scores()

print("\n📝 Inserting entertainment articles...")
inserted = 0
for article in [article1, article2]:
    result = insert_article(article)
    if result:
        inserted += 1

print(f"\n✅ Entertainment writer complete: {inserted} articles inserted")
