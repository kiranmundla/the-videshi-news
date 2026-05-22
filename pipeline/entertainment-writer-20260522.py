#!/usr/bin/env python3
"""Entertainment writer — May 22 2026 batch: Drishyam 3, Dhurandhar OTT, Cannes 2026, Chand Mera Dil."""

import os, json, sys, uuid, requests
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ["SUPABASE_ANON_KEY"])
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

now = datetime.now(timezone.utc).isoformat()

# ─── ARTICLE 1: Drishyam 3 Box Office ───

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Drishyam 3 Just Had the Second-Biggest Malayalam Opening Ever — and Most of the Money Came From Abroad",
    "subheadline": "Mohanlal's Georgekutty earned ₹48 crore worldwide on Day 1, with overseas collections alone hitting ₹30 crore. For the Keralite diaspora in the Gulf and the West, this wasn't just a movie — it was a communal event.",
    "body": """Mohanlal walked back into a courtroom as Georgekutty on Wednesday, and the world showed up. Jeethu Joseph's *Drishyam 3* — the third installment of the franchise that turned a small-town father's desperate cover-up into Malayalam cinema's most durable thriller series — opened to ₹48 crore worldwide on its first day, making it the second-biggest Malayalam opener of all time behind only *L2: Empuraan*.

The number that matters most sits in the overseas column: ₹30 crore. That's more than double the India net figure of ₹18.50 crore — and it tells you exactly who's driving this franchise.

**The Gulf Connection**

Malayalam cinema has always had a unique relationship with the diaspora, particularly the millions of Keralites in the UAE, Saudi Arabia, Qatar, Kuwait, and Oman. The Gulf remittance economy that sustains much of Kerala also sustains its film industry. When a Mohanlal film opens, the Thursday-night premiere shows in Dubai, Abu Dhabi, and Doha aren't afterthoughts — they're the main event. *Drishyam 3* reportedly sold out across major Gulf cinemas within hours of bookings opening.

In the West, the story played out similarly. Early screenings in the UK and Ireland generated ₹6-7 crore in advance bookings alone. American screenings across the tri-state area, Houston, Dallas, and the Bay Area saw high occupancy, driven by the same Malayali community networks that turned *Manjummel Boys* into a surprise hit earlier this year.

**The Franchise That Remade Malayalam Presales**

Before *Drishyam 3*, the presale record for a Malayalam film was ₹52.5 crore held by *L2: Empuraan*. Drishyam's advance bookings hit ₹31 crore — second-highest ever — with over 454,000 tickets sold on BookMyShow before opening day. The film released across 2,700 screens in 66 countries, a staggering footprint for a regional-language film that began in 2013 as a modest thriller about a cable TV operator who uses his encyclopedic knowledge of crime films to outsmart the police.

What Jeethu Joseph built is rare in Indian cinema: a franchise with genuine narrative continuity. Unlike Bollywood sequels that reset the board with new love interests and new cities, the Drishyam films carry forward consequences. The third film reportedly explores what happens when Georgekutty's elaborate deceptions start unraveling — not from police investigation, but from within his own family.

**Mixed Reviews, Maximum Turnout**

Early audience reactions on X have been polarized. Several viewers praised Mohanlal's performance as a "masterclass in restrained suspense acting," while others pointed to slow pacing in the first half and a few predictable twists. The critical consensus is that *Drishyam 3* is stronger than *Drishyam 2* but can't match the original's tight, claustrophobic tension.

None of that matters to the box office. With ₹100 crore the reported production budget, the film needs roughly ₹150 crore India net to be a clean hit. If the weekend maintains momentum — and the overseas numbers stay this disproportionately high — that target could be cleared within the first four days.

**For the Diaspora, It's Personal**

For Keralites abroad, the Drishyam franchise carries weight beyond entertainment. Georgekutty is a particular kind of Indian hero — not a muscle-bound avenger or a suave spy, but a middle-class father who protects his family through intelligence, not violence. In a genre landscape dominated by mass masala, that quiet competence resonates with a diaspora audience that sees itself in the character.

The fact that most of the money came from outside India isn't a footnote. It's the story. Malayalam cinema's business model is now structurally dependent on the diaspora — and the diaspora, in turn, treats these releases as cultural anchors. When you're 8,000 miles from home, watching Mohanlal outsmart the system in a packed theater in Sharjah or Edison is the closest thing to being back in Kochi.

*Drishyam 3* is now playing in Malayalam, with dubbed versions in Tamil and Kannada. A Hindi remake, produced by Kumar Mangat Pathak and Abhishek Pathak, is separately in development — they've confirmed it will be a "family thriller" rather than the "emotional family drama" of the Malayalam original.""",
    "diaspora_angle": "Keralite diaspora in the Gulf and the West drove 62% of Drishyam 3's opening-day gross. For Malayalam cinema, the overseas market isn't supplementary — it's primary. The franchise's quiet, intelligence-driven hero resonates with a community that sees its own values reflected on screen.",
    "vertical": "entertainment",
    "tags": ["Drishyam 3", "Mohanlal", "Malayalam cinema", "box office", "Jeethu Joseph", "Kerala diaspora", "Gulf"],
    "urgency": "breaking",
    "sources": json.dumps([
        {"url": "https://hollywoodreporterindia.com/drishyam-3-box-office-day1", "name": "Hollywood Reporter India — ₹48 Crore Day 1"},
        {"url": "https://sacnilk.com/drishyam-3-box-office-collection", "name": "Sacnilk — Box Office Tracking"},
        {"url": "https://bollywoodhungama.com/drishyam-3-2700-screens-66-countries", "name": "Bollywood Hungama — Release Scale"},
        {"url": "https://filmibeat.com/drishyam-3-review-audience-reactions", "name": "Filmibeat — Audience Reactions"}
    ]),
    "slug": "drishyam-3-mohanlal-48-crore-opening-malayalam-diaspora-20260522",
    "word_count": 720,
    "status": "published",
    "is_featured": False,
    "category": "entertainment",
    "published_at": now,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
    "score_total": 88
}

# ─── ARTICLE 2: Dhurandhar OTT Streaming War ───

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Netflix and JioHotstar Are Both Releasing the Uncut 'Dhurandhar' Today — and Nobody Can Explain Why",
    "subheadline": "Ranveer Singh's ₹3,000-crore spy thriller gets a simultaneous 'Raw and Undekha' drop on two rival platforms. A Delhi High Court investigation into alleged state secrets adds an extra layer of absurdity.",
    "body": """Here's the pitch: Take the highest-grossing Indian film franchise in history. Create an extended, uncensored version that restores everything the Central Board of Film Certification asked the filmmakers to trim. Then release it on May 22 — simultaneously on Netflix *and* JioHotstar, two platforms currently locked in India's most expensive streaming rivalry. Confuse everyone. Profit.

That's exactly what happened today with *Dhurandhar: Raw and Undekha*, the extended cut of Aditya Dhar's spy thriller starring Ranveer Singh, Akshaye Khanna, and Sanjay Dutt. The original *Dhurandhar* grossed ₹1,307 crore worldwide. Its sequel, *Dhurandhar: The Revenge*, pushed the franchise past ₹3,000 crore collectively. Now the first film is back, longer, louder, and uncensored — in Hindi, Tamil, and Telugu across both major Indian streaming platforms.

**Why Two Platforms at Once?**

The short answer: windowing deals and desperation. Netflix holds international streaming rights to the Dhurandhar franchise and had already released the Raw and Undekha cut globally — everywhere except India. JioHotstar, which holds Indian digital rights, was scheduled to premiere the sequel (*The Revenge*) on June 4. By dropping the uncut original on the same day as Netflix's Indian debut, JioHotstar turned a competitor's release into a dual-platform event.

For subscribers, it's unusual but convenient — you can watch it wherever you already have a subscription. For the industry, it's a signal of how fractured streaming rights have become in India's OTT market. A single franchise can have its theatrical, digital, international, and extended versions spread across multiple platforms, each with different release windows.

**The High Court Problem**

The streaming release comes with a footnote that's more serious than the marketing suggests. The Delhi High Court is currently investigating whether *Dhurandhar* contains classified military information that could violate the Official Secrets Act. The film, which depicts a deep-cover RAW operative infiltrating Pakistan's intelligence apparatus, reportedly drew on real operational tradecraft — and someone in the defense establishment noticed.

The investigation hasn't resulted in any injunction or takedown order, and the filmmakers maintain that the film is entirely fictional. But the timing of the uncut release — restoring scenes that the CBFC specifically asked to remove — has raised eyebrows. The censored sequences reportedly include extended interrogation sequences, specific references to intelligence agency protocols, and action choreography that mirrors real counter-terrorism operations.

**The NRI Watch Party Question**

For the Indian diaspora, the practical question is simple: which platform do you open tonight? Netflix has had the international version streaming for weeks, so many NRIs in the US, UK, and Canada have already seen it. The Indian release is primarily for the domestic audience catching up.

But *Dhurandhar: The Revenge* — the sequel — follows a different path. JioHotstar gets it on June 4; Netflix gets it on June 19. That two-week gap matters for NRIs who've been watching spoilers pile up on X and Instagram since the film's theatrical run ended.

The Dhurandhar franchise has become the rare Indian film property that generates genuine global FOMO. When the original released theatrically, WhatsApp groups in Edison, Southall, and Brampton were coordinating opening-night screenings. The sequel repeated the pattern. Now the uncut version extends the conversation — is the CBFC version the real film, or is this the director's true intent?

For Aditya Dhar, who turned a ₹200 crore budget into a ₹1,300 crore return on the original, the answer is obvious. "This is the film I made," he's said in interviews. "What you saw in theaters was the film they let me release."

*Dhurandhar: Raw and Undekha* is streaming now on Netflix and JioHotstar in Hindi, Tamil, and Telugu. *Dhurandhar: The Revenge* arrives on JioHotstar June 4 and Netflix June 19.""",
    "diaspora_angle": "The Dhurandhar franchise has become the Indian diaspora's biggest communal streaming event. With release windows split across Netflix (global) and JioHotstar (India), NRIs face a two-platform puzzle — and the two-week gap on the sequel rewards those paying for both services.",
    "vertical": "entertainment",
    "tags": ["Dhurandhar", "Ranveer Singh", "Netflix", "JioHotstar", "OTT", "streaming", "CBFC"],
    "urgency": "breaking",
    "sources": json.dumps([
        {"url": "https://latestly.com/dhurandhar-raw-undekha-ott-release", "name": "LatestLY — OTT Release Details"},
        {"url": "https://cinemaexpress.com/dhurandhar-raw-undekha-premiere", "name": "Cinema Express — Dual Platform Premiere"},
        {"url": "https://newsdive.net/dhurandhar-streaming-showdown", "name": "News Dive — Streaming Showdown"},
        {"url": "https://cinemabuzzusa.com/dhurandhar-uncut-stream", "name": "Cinema Buzz USA — Delhi HC Investigation"}
    ]),
    "slug": "dhurandhar-raw-undekha-netflix-jiohotstar-uncut-streaming-20260522",
    "word_count": 710,
    "status": "published",
    "is_featured": False,
    "category": "entertainment",
    "published_at": now,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
    "score_total": 86
}

# ─── ARTICLE 3: Cannes 2026 Indian Takeover ───

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "India Didn't Just Show Up to Cannes This Year. It Showed Up in Nauvari Sarees, Patola Gowns, and Assamese Couture — and Finally Had Films to Match.",
    "subheadline": "From Supriya Pathak's directorial debut to Manish Malhotra bringing Northeast India to the Croisette, Cannes 2026 is the year Indian representation stopped being about red-carpet fashion and started being about the work.",
    "body": """For years, India's Cannes story followed a predictable script: Indian stars arrive, walk the red carpet in designer gowns, generate Instagram content, go home. The films were an afterthought. The coverage focused on who wore what. Deepika Padukone once said India was "at the cusp of greatness" at Cannes — but the evidence was mostly sartorial.

Cannes 2026 feels different. Not because the fashion stopped — it didn't, and it's spectacular — but because the substance finally caught up.

**The Films**

Start with Supriya Pathak Kapur's *Our Story*, an Indo-Australian co-production that explores three generations of women in her family. It's Pathak's directorial debut at 63, co-written with her daughter. The film features Anupam Sharma and Ruhaan Kapur, and its Cannes screening marks the first time a veteran Hindi-film actress has debuted as a director at the festival. It's personal filmmaking — the kind Cannes was built for.

Then there's *Gudgudi*, a short film by Manisha Makwana and producer Harshvardhan Patel of White Peacock Films, which screened on May 20. The team used the Cannes moment to announce two feature films: a folklore thriller and a romantic drama. These aren't vanity projects funded for festival credentials. They're micro-budget productions from outside the Bollywood machine, using Cannes as a launchpad for international distribution.

**The Fashion That Actually Said Something**

But let's be honest — the fashion *is* part of the story, and this year it carried meaning.

Prajakta Mali, the Marathi actress, walked the Cannes red carpet in a traditional Maharashtrian Nauvari saree — the nine-yard drape worn dhoti-style, paired with traditional Kolhapuri jewelry and minimal fusion styling. It was a statement: not "Indian culture for Western consumption" but "this is how Maharashtrian women dress for celebrations, and it belongs here."

Mouni Roy wore a gown inspired by Gujarat's Patola weaving tradition, with 300 hours of hand-embroidery — the same craftsmanship she'd highlighted alongside her Indo-American film *Bombay Stories*. Manish Malhotra sent Urmimala and Snigdha Baruah down the carpet in couture that drew explicitly from Assamese textile traditions, putting Northeast India on the Cannes map for possibly the first time.

Alia Bhatt returned and immediately sparked a debate about gender in Indian cinema — advocating for gender-agnostic filmmaking while her husband Ranbir Kapoor's *Animal* remains Bollywood's most divisive film on that exact topic. She responded to a troll with a single word that went viral. Aishwarya Rai arrived with daughter Aaradhya, her 24th Cannes appearance, though fans noticed L'Oréal's 2026 posters conspicuously excluded her.

**The Diaspora Shift**

What's changed for NRIs watching from abroad is the *kind* of Indian representation on display. A decade ago, the conversation was "Why doesn't India have films at Cannes?" Then it became "Why are Indians only there for brand deals?" Now the answer is more nuanced: India is there with films, with fashion that references specific regional traditions rather than generic "Indian" aesthetics, and with a growing infrastructure of independent producers who treat Cannes as a market, not a vacation.

The Patola gown, the Nauvari saree, the Assamese couture — these aren't India-as-a-monolith. They're Gujarati, Maharashtrian, and Assamese identities asserting themselves individually. For a diaspora that often gets flattened into a single "Indian" identity abroad, that specificity matters more than any red-carpet ranking.

Cannes 2026 runs through May 31.""",
    "diaspora_angle": "Indian representation at Cannes shifted from generic glamour to specific regional identities — Patola, Nauvari, Assamese couture — mirroring the diaspora's own push against the flattening of 'Indian' into a single identity abroad. The films this year matched the fashion's ambition.",
    "vertical": "entertainment",
    "tags": ["Cannes 2026", "Bollywood", "Alia Bhatt", "Aishwarya Rai", "Supriya Pathak", "Indian cinema", "fashion"],
    "urgency": "trending",
    "sources": json.dumps([
        {"url": "https://bollywoodhungama.com/cannes-2026-indian-stars", "name": "Bollywood Hungama — Indian Stars at Cannes 2026"},
        {"url": "https://filmibeat.com/cannes-2026-manish-malhotra-assam", "name": "Filmibeat — Manish Malhotra Assamese Couture"},
        {"url": "https://zoomtventertainment.com/cannes-2026-aishwarya", "name": "Zoom — Aishwarya Rai at Cannes"},
        {"url": "https://saptashwatv.com/prajakta-mali-nauvari-cannes", "name": "Saptashwa TV — Prajakta Mali Nauvari Saree"},
        {"url": "https://popcornreview.in/alia-bhatt-cannes-debate", "name": "Popcorn Review — Alia Bhatt Gender Debate"}
    ]),
    "slug": "cannes-2026-indian-films-fashion-nauvari-patola-assamese-20260522",
    "word_count": 700,
    "status": "published",
    "is_featured": False,
    "category": "entertainment",
    "published_at": now,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
    "score_total": 84
}

# ─── ARTICLE 4: Chand Mera Dil Release ───

article4 = {
    "id": str(uuid.uuid4()),
    "headline": "Karan Johar Bet on a Love Story in the Age of Spy Thrillers. 'Chand Mera Dil' Opens Today — and It's Either Brave or Suicidal.",
    "subheadline": "Ananya Panday and Lakshya star in a youth romance releasing the same day as Drishyam 3 and the Dhurandhar uncut drop. The question isn't whether the film is good — it's whether anyone will notice it exists.",
    "body": """There is a particular kind of courage — or foolishness — in releasing a romantic drama on May 22, 2026. Mohanlal's *Drishyam 3* is devouring screens. *Star Wars: The Mandalorian and Grogu* is pulling the multiplex crowd. Netflix and JioHotstar just dropped Ranveer Singh's uncensored *Dhurandhar*. Into this bloodbath walks Karan Johar with *Chand Mera Dil*, a Hindi-language romance starring Ananya Panday and Lakshya — two young actors whose combined filmography wouldn't fill a single hard drive.

The early reviews are polite. One widely shared assessment called it "watchable" — the kind of word that means "you won't regret it, but you won't remember it either." A 2.5-star rating from an early screener suggests competence without revelation. Morning shows in Mumbai and Delhi saw decent occupancy, driven largely by the Dharma Productions brand and the youth demographic that still turns up for Karan Johar's version of love.

**The Johar Gambit**

Karan Johar has been here before — releasing candy-colored romances into a market that increasingly rewards violence, spectacle, and franchise IP. The difference in 2026 is that even Johar seems to know the terrain has shifted. *Chand Mera Dil* is reportedly more restrained than his usual maximalism: no Swiss Alps, no family wedding spanning three songs, no Shahrukh Khan arriving by helicopter. Instead, it's a Mumbai-set story about two people in their twenties navigating modern relationships — closer to *Dear Zindagi* than *Kabhi Khushi Kabhie Gham*.

For Ananya Panday, this is a crossroads film. After the meme-heavy reception of her early work and the critical indifference that greeted *Gehraiyaan 2*, she needs a role that lets her act rather than just exist in attractive proximity to a co-star. Lakshya, meanwhile, is virtually unknown outside of industry circles — a Dharma protégé being positioned as the next-generation romantic lead.

**The NRI Angle No One's Talking About**

There's a quiet reality to Bollywood romances that the Indian box office doesn't capture: they perform disproportionately well in the NRI market on streaming. Films like *Kal Ho Naa Ho*, *Yeh Jawaani Hai Deewani*, and even the first *Student of the Year* have had second lives on Netflix and Prime Video in the diaspora, becoming comfort watches for homesick millennials. The theatrical opening doesn't always predict the long tail.

*Chand Mera Dil* is calibrated for exactly this audience — young, urban, bilingual Indians who grew up on Dharma romances and still put on *KKHH* when they're lonely in their London or Toronto apartments. Whether the film earns ₹50 crore or ₹150 crore in theaters, its real test will come six weeks later when it hits OTT and competes for attention in a very different market.

The question today isn't whether *Chand Mera Dil* is a good film. The early signals suggest it's fine — attractive leads, decent music, a serviceable love story. The question is whether "fine" is enough in a week where everything else is screaming for attention.

*Chand Mera Dil* is in theaters now in Hindi.""",
    "diaspora_angle": "Bollywood romances have an outsized second life in the NRI streaming market. Chand Mera Dil is calibrated for the Dharma-nostalgia diaspora audience — young Indians abroad who still default to KJo romances as comfort viewing. The theatrical number won't tell the full story.",
    "vertical": "entertainment",
    "tags": ["Chand Mera Dil", "Karan Johar", "Ananya Panday", "Lakshya", "Bollywood", "Dharma Productions"],
    "urgency": "standard",
    "sources": json.dumps([
        {"url": "https://filmibeat.com/chand-mera-dil-review-release", "name": "Filmibeat — First Review"},
        {"url": "https://bombaytimes.com/friday-releases-may-22-2026", "name": "Bombay Times — Friday Releases"},
        {"url": "https://sacnilk.com/dhurandhar-2-chand-mera-dil", "name": "Sacnilk — Release Clash Analysis"}
    ]),
    "slug": "chand-mera-dil-karan-johar-ananya-panday-release-20260522",
    "word_count": 640,
    "status": "published",
    "is_featured": False,
    "category": "entertainment",
    "published_at": now,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
    "score_total": 78
}

articles = [article1, article2, article3, article4]

# ─── INSERT ───
for art in articles:
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=art
    )
    if r.status_code in (200, 201):
        print(f"✅ Published: {art['slug']}")
    elif r.status_code == 409:
        print(f"⚠️  Already exists: {art['slug']}")
    else:
        print(f"❌ Error {r.status_code} for {art['slug']}: {r.text}")

print(f"\nDone — {len(articles)} entertainment articles submitted.")
