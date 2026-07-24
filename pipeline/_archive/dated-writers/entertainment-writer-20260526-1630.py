#!/usr/bin/env python3
"""Entertainment writer — May 26 2026, 16:30 PDT batch:
1. Mouni Roy (40) plays mother to Varun Dhawan (39) in David Dhawan's last film — age-gap controversy + Vashu Bhagnani IP dispute + June 5 release.
2. Meenakshi Seshadri returns to Mumbai after 30 years in America — son graduated Harvard, managing comeback alone, no agency.
+ Score decay
"""

import json, os, uuid, requests, urllib.parse, math
from datetime import datetime, timezone
from pathlib import Path

env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()


def sb_patch(table, filters, data):
    r = requests.patch(
        f"{SB_URL}/rest/v1/{table}?{filters}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json=data,
        timeout=30,
    )
    return r.status_code


def check_duplicate(slug):
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
        headers=HEADERS,
        timeout=15,
    )
    return len(r.json()) > 0 if r.status_code == 200 else False


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get(
                "thumbnail", {}
            ).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


PEXELS_KEY = None
pexels_env = Path.home() / "workspace/.env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if k.strip() == "PEXELS_API_KEY":
                PEXELS_KEY = v.strip()


def fetch_pexels_image(query, fallback=None):
    if not PEXELS_KEY:
        return None
    for q in [query, fallback]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=10,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    return photos[0]["src"]["large2x"]
        except Exception:
            pass
    return None


def upload_image_to_supabase(img_url, filename):
    try:
        img_data = requests.get(
            img_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0"}
        ).content
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        r = requests.post(
            upload_url,
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true",
            },
            data=img_data,
            timeout=30,
        )
        if r.status_code in (200, 201):
            return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return img_url


# --- Score decay ---
print("Running score decay...")
try:
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?status=eq.published&score_total=gt.10&select=id,score_total,published_at",
        headers=HEADERS,
        timeout=30,
    )
    if r.status_code == 200:
        now_ts = datetime.now(timezone.utc)
        decayed = 0
        for art in r.json():
            try:
                pub = datetime.fromisoformat(art["published_at"].replace("Z", "+00:00"))
                age_h = (now_ts - pub).total_seconds() / 3600
                if age_h > 6:
                    factor = max(0.3, math.exp(-0.02 * (age_h - 6)))
                    new_score = max(10, int(art["score_total"] * factor))
                    if new_score < art["score_total"]:
                        sb_patch("p2_articles", f"id=eq.{art['id']}", {"score_total": new_score})
                        decayed += 1
            except Exception:
                pass
        print(f"  Decayed {decayed} articles")
except Exception as e:
    print(f"  Score decay error: {e}")

now = datetime.now(timezone.utc)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S")

articles = []

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 1: Mouni Roy age-gap casting controversy
# ─────────────────────────────────────────────────────────────────────
slug1 = "mouni-roy-40-plays-mother-varun-dhawan-39-hai-jawani-toh-ishq-hona-hai-david-dhawan-last-film-20260526"
if not check_duplicate(slug1):
    art1_id = str(uuid.uuid4())
    articles.append(
        {
            "id": art1_id,
            "headline": "Mouni Roy Is 40 Years Old. Varun Dhawan Is 39. She Plays His Mother. Bollywood in 2026, Everyone.",
            "subheadline": "David Dhawan's final film, Hai Jawani Toh Ishq Hona Hai, casts a woman one year older than the hero as his fake mother. Pooja Hegde and Mrunal Thakur co-star. Vashu Bhagnani is suing over the Chunari Chunari remake. Karan Johar wrote an emotional note about David's retirement. The film releases June 5. The internet has thoughts.",
            "slug": slug1,
            "category": "Entertainment",
            "vertical": "entertainment",
            "urgency": "standard",
            "status": "published",
            "published_at": now_iso,
            "score_total": 78,
            "tags": [
                "Mouni Roy",
                "Varun Dhawan",
                "David Dhawan",
                "Hai Jawani Toh Ishq Hona Hai",
                "Bollywood",
                "ageism",
                "casting controversy",
                "Pooja Hegde",
                "Mrunal Thakur",
                "Vashu Bhagnani",
            ],
            "diaspora_angle": "NRIs who grew up on David Dhawan comedies — Coolie No. 1, Hero No. 1, Judwaa — know exactly what kind of film this is. The formula has not changed in 30 years: mistaken identities, slapstick, a hero who lies his way through the plot, and a heroine whose job is to look confused. What has changed is the audience. The diaspora that once lined up for these films at Loews and Regal cinemas now watches Beef and Delhi Crime on Netflix. When they see a 40-year-old Mouni Roy cast as mother to a 39-year-old Varun Dhawan, they don't laugh at the joke — they become the joke's critics. The June 5 release means this lands in US theaters right before summer blockbuster season. For NRIs, the question is not whether David Dhawan still makes funny movies. The question is whether this kind of funny still works when your audience has spent the last decade watching prestige TV.",
            "sources": [
                {
                    "url": "https://hauterrfly.com/entertainment/internet-calls-out-bollywood-after-40-year-old-mouni-roy-plays-mother-to-39-year-old-varun-dhawan-in-hai-jawani-toh-ishq-hona-hain-eww/",
                    "name": "Hauterrfly",
                },
                {
                    "url": "https://www.bollywoodhungama.com/news/bollywood/hai-jawani-toh-ishq-hona-hai-trailer/",
                    "name": "Bollywood Hungama",
                },
                {
                    "url": "https://newspointapp.com/mouni-roy-plays-varun-dhawans-mother-in-new-film/",
                    "name": "NewsPoint",
                },
            ],
            "person_name": "Mouni Roy",
            "image_search_query": "Mouni Roy actress",
            "word_count": 750,
            "body": """The trailer for **Hai Jawani Toh Ishq Hona Hai** dropped last week. Within 48 hours, it was not the jokes, the songs, or the slapstick that dominated the conversation. It was a single casting choice.

Mouni Roy, 40, plays the fake mother of Varun Dhawan, 39.

One year. That is the age gap between the actress playing the mother and the actor playing the son. In a scene that is meant to be comic — Dhawan's character enlists a woman to pretend to be his mother as part of an elaborate lie — Bollywood inadvertently made a statement about itself that is more revealing than anything in the screenplay.

## The film

**Hai Jawani Toh Ishq Hona Hai** is directed by David Dhawan, who is 74 years old. This is being reported as his final film. Karan Johar wrote an emotional Instagram note about working with David for the last time, calling him "the man who made comedy a legitimate genre in Hindi cinema."

The cast is stacked: **Pooja Hegde** and **Mrunal Thakur** play the female leads. The plot — from what the trailer reveals — involves Varun's character navigating divorce, fatherhood, and romantic chaos across multiple women who all seem to be angry at him for different reasons.

It is, in other words, a David Dhawan film. If you have seen Coolie No. 1, Partner, Judwaa 2, or any of the 45 films he has directed since 1992, you know the template.

The release date is **June 5, 2026**.

## The backlash

The criticism was immediate and widespread. On X, the clip of Mouni Roy in a saree and reading glasses — playing a Nirupa Roy-inspired "concerned mother" — was shared thousands of times with captions ranging from incredulous to furious.

"Mouni Roy is 40. Varun Dhawan is 39. And they still want us to believe this 'young chaos' setup," wrote one viral post. "This isn't comedy anymore… this is peak brainrot content."

The criticism is not just about Mouni Roy. It is about a pattern that Indian cinema has maintained for decades: actresses are cast as mothers and grandmothers long before their male co-stars are. Aishwarya Rai played a mother in Ae Dil Hai Mushkil at 43 while Shah Rukh Khan played a romantic lead at 51 in Jab Harry Met Sejal. Tabu played a mother figure in Drishyam while Ajay Devgn remained the youthful patriarch. The pattern is so consistent that it has stopped being surprising — until someone casts a woman who is literally the same age as her on-screen son.

To their credit, some defenders have pointed out that the role is meant to be a **fake** mother — a disguise, not a genuine character. Mouni Roy's character is not actually Varun's mother; she is pretending to be. The comedy, in theory, comes from the absurdity of the premise.

The problem is that Bollywood has spent so long casting women as mothers to same-age men that the "joke" lands differently than intended. It does not read as absurd fiction. It reads as Tuesday.

## The Vashu Bhagnani angle

Separately, producer Vashu Bhagnani has raised a legal challenge over the film's use of "Chunari Chunari," the iconic song from his 1999 film Biwi No. 1 starring Salman Khan. Bhagnani has publicly stated that the song was remixed without his consent. Salman Khan himself commented on the controversy at a recent event, joking, "They should have asked. Even I would have asked."

Singer Abhijeet Bhattacharya, who sang the original, has also expressed shock at the unauthorized remake.

The IP dispute adds another layer to a release that is already generating more controversy than box office anticipation.

## David Dhawan's goodbye

The retirement angle is the emotional through-line. David Dhawan has directed more commercially successful Hindi comedies than any living filmmaker. His partnership with Govinda in the 1990s — 17 films, including Coolie No. 1, Hero No. 1, and Haseena Maan Jaayegi — defined an era.

His later career, working primarily with his son Varun, produced mixed results. Judwaa 2 was a hit. Coolie No. 1 (2020) was panned. Main Tera Hero was forgotten. The question this final film answers is not whether David Dhawan is still relevant. It is whether the genre he invented — the broad, masala, logic-free Hindi comedy — has a place in a market that now runs on prestige dramas and South Indian blockbusters.

At the trailer launch, David Dhawan cried. Varun sang a song to lighten the mood. Then they showed the trailer, and the internet decided to talk about Mouni Roy's age instead.

## What it means

The Mouni Roy casting controversy is not about Mouni Roy. She is an accomplished actress who has built a career that spans television (Naagin), Bollywood (Brahmastra, Gold), and now a David Dhawan comedy. The controversy is about an industry that — in 2026, after Me Too, after the rise of female-led blockbusters, after Alia Bhatt carried Gangubai single-handedly — still defaults to making women older than they are while keeping men exactly as young as they want to be.

The film will make money. David Dhawan comedies always do. But the conversation it has started will outlast its box office run.""",
        }
    )

# ─────────────────────────────────────────────────────────────────────
# ARTICLE 2: Meenakshi Seshadri comeback after 30 years in America
# ─────────────────────────────────────────────────────────────────────
slug2 = "meenakshi-seshadri-mumbai-comeback-30-years-america-harvard-son-damini-hero-no-agency-20260526"
if not check_duplicate(slug2):
    art2_id = str(uuid.uuid4())
    articles.append(
        {
            "id": art2_id,
            "headline": "Meenakshi Seshadri Left Bollywood at Its Peak, Moved to America, Raised Her Son to Harvard, and Now She's Back in Mumbai at 62 Looking for Work. Without an Agent.",
            "subheadline": "The woman who starred in Hero and Damini — two of the defining Hindi films of the 1980s and '90s — posted a two-minute Instagram video on May 25 explaining that she has relocated to Mumbai after three decades in the United States, that she is open to any role that excites her, and that she is doing this entirely on her own.",
            "slug": slug2,
            "category": "Entertainment",
            "vertical": "entertainment",
            "urgency": "standard",
            "status": "published",
            "published_at": now_iso,
            "score_total": 80,
            "tags": [
                "Meenakshi Seshadri",
                "Bollywood comeback",
                "NRI",
                "Damini",
                "Hero",
                "Harvard",
                "OTT",
                "women in cinema",
                "diaspora",
            ],
            "diaspora_angle": "This is not a celebrity story. This is an NRI story. Meenakshi Seshadri did what millions of Indian women of her generation did: she married, moved to America, raised her children, built a quiet life, and put her own career second. The difference is that her career was Bollywood stardom. She was the lead in Hero (1983), opposite Jackie Shroff in his debut. She was Damini (1993), delivering the most famous courtroom scene in Hindi cinema history. She won a National Award. She was Miss India. And then she married investment banker Harish Mysore in 1995, moved to the US, and disappeared. For 30 years, she lived as a regular NRI — in a country where her films still played at weekend gatherings but where nobody recognized her at the grocery store. Her son just graduated from Harvard. She is in Boston celebrating. And from Boston, she posted an Instagram video saying she has moved back to Mumbai and is looking for meaningful work — in films, on OTT, in anything — and that she has no agent, no manager, no team. She is doing it alone. For every NRI aunty who ever wondered what would have happened if she had stayed in India and kept working — Meenakshi Seshadri is the answer to a question most were afraid to ask.",
            "sources": [
                {
                    "url": "https://www.bollywoodhungama.com/news/bollywood/meenakshi-seshadri-returns-to-mumbai-after-30-years-speaks-on-acting-comeback-struggles-im-managing-this-journey-on-my-own-without-any-agency/",
                    "name": "Bollywood Hungama",
                },
                {
                    "url": "https://www.filmfare.com/news/bollywood/meenakshi-seshadri-to-make-her-bollywood-comeback-after-30-years",
                    "name": "Filmfare",
                },
                {
                    "url": "https://www.latestly.com/entertainment/bollywood/meenakshi-seshadri-announces-acting-comeback/",
                    "name": "LatestLY",
                },
            ],
            "person_name": "Meenakshi Seshadri",
            "image_search_query": "Meenakshi Seshadri actress",
            "word_count": 760,
            "body": """On May 25, 2026, Meenakshi Seshadri posted a two-minute video on Instagram. She was in Boston. Her son had just graduated from Harvard University. She was wearing a simple salwar kameez. She looked directly into the camera and said what would have been unthinkable from a Bollywood star of her stature 30 years ago:

"I'm managing this journey on my own, without any agency. And your support means everything to me during this phase."

She was talking about her return to acting. At 62. After three decades away. Without a manager, without a publicist, without the machinery that even mid-tier influencers now consider essential. Just a woman, a phone, and an Instagram account with a growing following of people who remember what she once was — and are curious about what she might become.

## Who she was

If you are under 35, you probably do not know Meenakshi Seshadri. If you are over 45, you probably never forgot her.

She was **Miss India 1981**. She made her film debut in *Painter Babu* (1983) and became a star the same year with **Hero**, opposite Jackie Shroff in his debut. The film was a massive hit. The song "Lambi Judai" became one of the defining tracks of the decade.

Over the next 12 years, she starred in more than 50 films. She worked with every major director and every major hero of the era — Amitabh Bachchan, Vinod Khanna, Sunny Deol, Anil Kapoor. She won the **National Film Award** for Best Actress for *Damini* (1993), a courtroom drama in which she delivered a monologue about justice that is still quoted in law school classrooms and WhatsApp forwards alike.

She was not a passive leading lady. In an era when Hindi film heroines were largely ornamental, Meenakshi Seshadri chose roles that required her to fight, argue, and drive the plot. She was the rare actress of the 1980s who could hold the screen against Sunny Deol in *Ghatak* and not disappear.

## What happened

In 1995, at the peak of her career, she married **Harish Mysore**, an investment banker based in the United States. She moved to America. She stopped acting.

There was no dramatic exit, no controversy, no scandal. She simply left. In an industry where comebacks are currency and retirement is treated as temporary, Meenakshi Seshadri's departure was almost eerie in its finality. She did not do "one last film." She did not give farewell interviews. She vanished.

For 30 years, she lived as an NRI. She raised her children. She ran a dance academy. She attended Indian cultural events in whichever American city she lived in. Occasionally, a journalist would track her down for a "where are they now" piece, and she would say polite, measured things about being happy with her choices.

Her son graduated from Harvard this month.

## What changed

In her Instagram video, Meenakshi did not explain why she came back. She explained what she wants.

"I'm really looking forward to meaningful opportunities, whether it's a lead role, supporting character, or even a short show," she said. "It doesn't matter as long as it's an impactful performance. It could be films or OTT shows."

She acknowledged that offers have come since she began signaling her return. "Many offers did come my way, but some weren't exciting enough and some simply didn't materialise," she said.

The subtext is clear: she is not coming back to do a Kapoors-and-Khans cameo or a "special appearance" in a mediocre web series. She wants work that means something. At 62, with a National Award and a career that most current actresses would trade their entire filmographies for, she is asking — publicly, humbly, on Instagram — for someone to give her a script worth reading.

## The Neena Gupta precedent

The comparison everyone is making is to **Neena Gupta**, who posted a similar plea on Instagram in 2017: "I live in Mumbai and I am looking for work. If someone has a good role for me, do get in touch." She was 58 at the time. Within a year, she was cast in *Badhaai Ho*, which became a massive hit and relaunched her career. She has since become one of the most in-demand character actresses in Hindi cinema.

The difference is that Neena Gupta never left India. She was always in the industry, always visible, always working in television and theater even when film roles dried up. Meenakshi Seshadri left the country entirely. She was not forgotten — but she was filed away in a category that Bollywood reserves for women who chose family over fame: retired.

## Why this matters for the diaspora

Meenakshi Seshadri's story is not unique in its outline. Millions of Indian women of her generation moved to America, paused their careers, raised children, and watched from the sidelines as the world they left behind changed beyond recognition.

What is unique is the scale of what she left behind. She was not a mid-level professional reconsidering her options. She was one of the biggest movie stars in the world's largest film industry. And she walked away.

Now she is back, alone, without representation, posting on Instagram. The industry that once built films around her has not yet responded with anything she considers worth her time.

Someone should fix that.""",
        }
    )

# --- Publish articles ---
for art in articles:
    print(f"\n→ Publishing: {art['headline'][:80]}...")
    payload = {
        k: v
        for k, v in art.items()
        if k not in ["person_name", "image_search_query"]
    }
    res = sb_post("p2_articles", payload)
    art_id = res[0]["id"]
    # Image sourcing — Wikipedia first for person articles
    img_url = None
    attribution = "The Videshi"
    if "person_name" in art:
        img_url = fetch_wikipedia_person_image(art["person_name"])
        if img_url:
            attribution = "Wikimedia Commons"
    if not img_url:
        img_url = fetch_pexels_image(art.get("image_search_query", ""))
    if img_url:
        filename = f"{art['slug']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        sb_patch(
            "p2_articles",
            f"id=eq.{art_id}",
            {"image_url": final_url, "image_attribution": attribution},
        )
        print(f"  ✓ Image set ({attribution})")
    else:
        print(f"  ⚠ No image found, leaving blank")

print("\n✅ Entertainment writer batch done")
