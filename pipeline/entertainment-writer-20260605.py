#!/usr/bin/env python3
"""Entertainment writer for The Videshi — 2026-06-05 batch"""

import json, os, sys, uuid, requests
from datetime import datetime, timezone

# Load Supabase creds
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            key = key.replace("export ", "").strip()
            val = val.strip().strip('"').strip("'")
            os.environ[key] = val

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def publish_article(article):
    """Insert an article into Supabase"""
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Published: {data[0].get('headline', '')[:60]}... (id: {data[0].get('id', '')})")
        else:
            print(f"  ✓ Published: {article['headline'][:60]}...")
        return True
    else:
        print(f"  ✗ FAILED ({resp.status_code}): {resp.text[:200]}")
        return False

now_utc = datetime.now(timezone.utc).isoformat()

articles = []

# ============================================================
# ARTICLE 1: Aamir Khan confirms wedding with Gauri Spratt
# ============================================================
articles.append({
    "headline": "Aamir Khan Will Marry Gauri Spratt on July 5. It Will Be a Registered Marriage at Home.",
    "subheadline": "The actor confirmed the date to Variety India. No grand reception, no industry guest list — just two families, a handful of friends, and a quiet signing at his Mumbai residence.",
    "slug": "aamir-khan-gauri-spratt-wedding-july-5-registered-marriage-home-nri-20260605",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "is_editorial": False,
    "published_at": now_utc,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/65/Aamir_Khan_at_the_success_bash_of_Secret_Superstar.jpg",
    "image_caption": "Aamir Khan at a film event in Mumbai",
    "image_attribution": "Wikimedia Commons",
    "body": """Aamir Khan has confirmed he is getting married for the third time.

The 60-year-old actor told Variety India this week that he and his partner Gauri Spratt will formalise their relationship on July 5, 2026. "The news about the marriage is true. It's on July 5," he said, bringing months of speculation to a definitive end.

The ceremony will not be the kind Bollywood is used to producing. There will be no multi-day celebrations across five-star ballrooms. No curated guest list running into hundreds. No designer mandap or an army of wedding planners. Instead, according to sources close to the family, Aamir and Gauri will hold a registered marriage at his Mumbai residence with only their two families and a small circle of close friends present. A grand industry reception is not being planned.

## A Relationship Built Over Twenty-Five Years

The couple's story reaches further back than most of their fans realise. Aamir and Gauri first met nearly 25 years ago, long before their relationship became romantic. They were friends for decades, lost touch, and reconnected in recent years. What followed was a slow, deliberate progression from friendship to partnership.

On the occasion of his 60th birthday in March 2025, Aamir surprised the media by introducing Gauri as his partner. At the time, he was careful to manage expectations, saying that marriage was not a pressing issue. But by June 2026, his position had evolved. "Now we both feel we are ready to take our relationship to the next level," he told Variety India.

In a separate conversation with Raj Shamani's podcast, Aamir offered a rare window into the emotional journey that led him to this point. "Before I met Gauri, I felt like I had aged, and who will I find at this age," he said. "Also, my therapy started, and I understood that I need to love myself first and make myself healthy. So I worked on that."

## Gauri Spratt's Quietly Remarkable Story

Gauri, 47, is originally from Bengaluru and works in the fashion, beauty, and wellness industry. She has a seven-year-old son named Quinn from a previous marriage. What makes her family story particularly striking is the thread that runs through it: her grandfather, Philip Spratt, was a British-born Communist who sailed to India in the 1920s to support the independence movement and eventually made the country his permanent home. He chose India not by birth but by conviction. There is something poetically fitting about his granddaughter now building a life in Mumbai with one of its most prominent citizens.

Both families are said to be fully supportive of the marriage, which those close to the couple describe as a formalisation of a reality that has been in place for over a year. "They have built a happy, stable life together and decided to mark it formally with their families present," a source told Filmfare.

## What This Means for the Diaspora

For NRIs who grew up watching Aamir Khan navigate love, loss, and identity across decades of cinema — from Dil Chahta Hai to Laal Singh Chaddha — this announcement carries a personal resonance. His willingness to speak openly about therapy, ageing, and the courage it takes to love again after two divorces is a kind of vulnerability that Bollywood's leading men rarely model in real life.

That the wedding itself will be a registered ceremony rather than a production is its own kind of statement. In an industry where weddings regularly double as brand activations, Aamir and Gauri are choosing privacy over performance.

## His Previous Marriages

Aamir's first marriage was to his childhood sweetheart, Reena Dutta, in 1986. They have two children — actor Junaid Khan and Ira Khan — and divorced in 2002. In 2005, he married filmmaker Kiran Rao, with whom he has a son, Azad Rao Khan. That marriage ended amicably in 2021, and the two continue to co-parent Azad.

With July 5 now confirmed, the only remaining question is whether Mr. Perfectionist — a man who has always done things on his own terms — will manage to keep his own wedding as quiet as he intends.

*Sources: Variety India, Bollywood Hungama, Filmfare, Pinkvilla*""",
    "sources": json.dumps([
        {"name": "Variety India", "url": "https://variety.com"},
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
        {"name": "Filmfare", "url": "https://www.filmfare.com"},
        {"name": "Pinkvilla", "url": "https://www.pinkvilla.com"}
    ])
})

# ============================================================
# ARTICLE 2: Pahlaj Nihalani passes away at 76
# ============================================================
articles.append({
    "headline": "Pahlaj Nihalani Has Died at 76. Govinda Broke Down at His Funeral. The Industry He Built Around Himself Came to Say Goodbye.",
    "subheadline": "The producer who launched Govinda, bankrolled Aankhen, and ran the CBFC during its most controversial years died in Mumbai after battling liver cirrhosis for four months. The tributes tell the story of a man who opened doors.",
    "slug": "pahlaj-nihalani-death-76-govinda-funeral-cbfc-producer-legacy-nri-20260605",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "is_editorial": False,
    "published_at": now_utc,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Lachhman_Chatnani%2CRam_Jawhrani%2CAnthony_Arun_Biswas%2CPahlaj_Nihalani%2CGovinda%2CChandru_Punjabi_From_The_Govinda_graces_Mother_Teresa_International_Award_%2815%29.jpg",
    "image_caption": "Pahlaj Nihalani with Govinda at the Mother Teresa International Award ceremony",
    "image_attribution": "Wikimedia Commons",
    "body": """Pahlaj Nihalani, the veteran Bollywood producer and former chairman of the Central Board of Film Certification, died on June 4, 2026, at Mumbai's Nanavati Hospital. He was 76.

The cause was liver cirrhosis, which had kept him in and out of hospitals for four months. His family confirmed the news in a statement: "With profound grief, we inform you of the passing of our beloved Pahlaj Nihalani on 4th June 2026."

The cremation was held the same afternoon at the Santacruz Hindu Crematorium. By the time the industry arrived, the grief was already visible. Govinda, the actor whose career Nihalani helped create, broke down in tears at the funeral. Malaika Arora and her sister Amruta were among the first to reach the family's residence. Farhan Akhtar, David Dhawan and his son Varun Dhawan, Shatrughan Sinha, Anees Bazmee, Ramesh Taurani, and Neha Dhupia all came to pay their respects.

## The Man Who Made Govinda

Nihalani's name will always be tethered to Govinda's rise. He produced several of the actor's most commercially successful films in the late 1980s and 1990s — Shola Aur Shabnam, Aankhen, and later Rangeela Raja. These were not prestige pictures. They were the kind of crowd-pleasing, mass-market entertainers that filled single-screen theatres across India and were the backbone of the home-video market that NRI families in the Gulf, UK, and US relied on to stay connected to Bollywood.

Govinda's tribute reflected that debt. "Pahlaj Nihalani Ji was a foundational figure for us," the actor said. "For me and for numerous other artists who overcame the challenges of hardship, he provided essential support, allowing us to establish ourselves as artists in this country."

## A Career That Spanned Four Decades

Nihalani began producing films in the early 1980s with Haathkadi. Through the next two decades, he backed Aandhi-Toofan, Ilzaam, Aag Hi Aag, Paap Ki Duniya, and the hit comedy Aankhen. His filmography was not art-house, but it was relentlessly commercial, and it kept an entire ecosystem of actors, directors, technicians, and distributors working. He was also president of the Association of Pictures and TV Programme Producers for 29 years, making him one of the industry's longest-serving trade body leaders.

His last film as a producer was Julie 2, released in 2017.

## The CBFC Years

For many Indians, Nihalani became most recognisable not as a producer but as the man who ran the censor board from January 2015 to August 2017. His tenure was defined by conflict. He ordered cuts to films that filmmakers saw as arbitrary, demanded the removal of words and scenes that had cleared previous boards, and became a lightning rod for national debates about censorship, artistic freedom, and the limits of state control over cinema.

His critics called him authoritarian. His supporters said he was enforcing rules that had been ignored for years. Either way, his time at the CBFC was the most publicly contentious period in the body's modern history, and it ended with his replacement by lyricist Prasoon Joshi.

For the diaspora audience that had grown up watching the films he produced, the CBFC chapter was a jarring pivot from the man who had given them Aankhen and Shola Aur Shabnam.

## How the Industry Responded

The tributes from the industry were not performative. They carried the texture of real relationships.

Suniel Shetty, whose early career Nihalani supported, wrote: "Pahlaj ji was among the first to have faith in me. When I was trying to find my place in the industry, he opened doors, guided me, and consistently supported me with kindness and encouragement."

Sunny Deol called him "a very dear friend, family, a gem of a person always ready to help anyone." Anil Kapoor, Kangana Ranaut, Shatrughan Sinha, Sanjay Gupta, and filmmaker Anees Bazmee all posted tributes. Bazmee, who had worked closely with Nihalani over many years, described the loss as personal: "This is very sad news. We have worked together for a long time and were very close to each other."

Moshumi Chatterjee, who collaborated with him decades ago, said simply: "He has given us so many remarkable films. He contributed immensely to the entertainment industry."

## He Leaves Behind a Complex Legacy

Nihalani is survived by his wife Nita and three sons — Vishal, Deepesh, and Chirag. His legacy is complicated in the way that most long careers in Indian cinema are: simultaneously built on populist entertainment and marked by a period of polarising public authority. But on the day he died, it was the first part of the story — the producer who believed in people and put his money where his faith was — that the industry chose to remember.

*Sources: Filmfare, Bollywood Hungama, Zoom TV, Cinema Express, Devdiscourse*""",
    "sources": json.dumps([
        {"name": "Filmfare", "url": "https://www.filmfare.com"},
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
        {"name": "Zoom TV", "url": "https://www.zoomtventertainment.com"},
        {"name": "Cinema Express", "url": "https://www.cinemaexpress.com"},
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com"}
    ])
})

# ============================================================
# ARTICLE 3: Karisma Kapoor's Brown drops on ZEE5
# ============================================================
articles.append({
    "headline": "Karisma Kapoor's Brown Is Now Streaming on ZEE5. The Reviews Say She Is the Best Thing in a Series That Cannot Keep Up with Her.",
    "subheadline": "A Kolkata-set neo-noir thriller gives the 90s star her grittiest role yet — a suspended, alcoholic cop investigating a brutal murder. Critics praise the performance but question everything around it.",
    "slug": "karisma-kapoor-brown-zee5-review-kolkata-neo-noir-thriller-nri-20260605",
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "published",
    "is_editorial": False,
    "published_at": now_utc,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/d2/KarismaKapoor02.jpg",
    "image_caption": "Karisma Kapoor at a public appearance in Mumbai",
    "image_attribution": "Wikimedia Commons",
    "body": """Brown, the seven-episode neo-noir crime thriller starring Karisma Kapoor, began streaming on ZEE5 on June 5, 2026. The series, directed by Abhinay Deo (Delhi Belly, Blackmail), is adapted from Abheek Barua's novel City of Death and is set in modern-day Kolkata.

The reviews have arrived, and they tell a consistent story: Karisma Kapoor is excellent, the series around her is not.

## The Premise

Karisma plays Rita Brown, a suspended police officer battling alcoholism and unresolved trauma. She is brought back to active duty when a young woman named Ahana is found murdered inside her home. The investigation spirals into political connections, family secrets, power structures, and personal histories. The supporting cast includes Jisshu Sengupta, veteran Helen, Soni Razdan, and Surya Sharma, who plays Rita's grief-stricken deputy Arjun Sinha.

On paper, this is a strong setup. A disgraced cop. A Kolkata that looks and feels like its own character. A murder that connects to every layer of the city's elite. The problem, according to nearly every critic who has reviewed it, is what happens between that setup and its payoff.

## What the Critics Are Saying

Bollywood Hungama gave it 2 out of 5 stars, writing that Brown "benefits from Karisma Kapoor's powerful, deeply felt performance and an atmospheric depiction of Kolkata, but the series is let down by predictable twists, inconsistent writing and a mystery that lacks the required shock value."

India Forums was similarly blunt with a 2 out of 5 rating: "Brown is so busy trying to be many things at once that it forgets to be an engaging thriller." The review noted that the narrative constantly introduces new characters, subplots, and emotional detours that add little to the central investigation. "The result is a series that constantly moves but rarely progresses."

The Hollywood Reporter India described it as "middling at best" and criticised the series for using ornate world-building to disguise a hollow core. "I like atmospheric shows as much as the next tired film critic," the review reads, "but Brown uses waves of texture and social fabric to offset a standard premise with no surprises and clichés galore."

MensXP called it "watchable" but said the execution follows familiar tropes so closely that "it fails to forge its own path." The review singled out the trailer as having revealed too many key plot points, undermining the show's suspense.

## Why Karisma Matters Here

What unites the reviews is a shared assessment of Karisma Kapoor herself. Even the harshest critics acknowledge that she delivers something genuinely new in her career — a de-glam, restrained, internalized performance that is nothing like the song-and-dance roles that defined her 1990s prime. She rolls her own cigarettes. She drinks. She carries a grief that is never explained with dialogue but is always visible in her posture and eyes.

For NRI audiences who grew up with her in Dil To Pagal Hai, Raja Hindustani, and Haseena Maan Jaayegi, Brown is Karisma's most serious attempt to prove she can operate in the prestige-OTT space that Bollywood has increasingly pivoted toward. The performance lands. The vehicle, apparently, does not.

## The Kolkata Factor

The series was shot extensively in Kolkata, and Amogh Deshpande's cinematography is one of its few universally praised elements. The city's crumbling architecture, its rain-drenched streets, and its old-money homes function as more than set dressing — they impose a mood that the script itself struggles to sustain. For diaspora viewers who have visited or have roots in West Bengal, the visual immersion will be familiar and atmospheric. But critics warn that the aesthetic ambition is not matched by narrative precision.

## The Verdict for Streaming Audiences

Brown is available now on ZEE5, which is accessible to viewers in the US, UK, Canada, and other diaspora markets through the platform's international subscription. At seven episodes, it is a compact binge — the kind of series you can finish in a weekend. Whether you should depends on what you are watching for. If it is Karisma Kapoor proving she has another act in her, Brown delivers. If it is a tightly constructed murder mystery, the reviews suggest you will spend more time admiring the wallpaper than solving the case.

*Sources: Bollywood Hungama, India Forums, Hollywood Reporter India, MensXP*""",
    "sources": json.dumps([
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com"},
        {"name": "India Forums", "url": "https://www.indiaforums.com"},
        {"name": "Hollywood Reporter India", "url": "https://www.hollywoodreporterindia.com"},
        {"name": "MensXP", "url": "https://www.mensxp.com"}
    ])
})

# ============================================================
# PUBLISH ALL
# ============================================================
print(f"\n=== Publishing {len(articles)} entertainment articles ===\n")
success_count = 0
for i, article in enumerate(articles, 1):
    print(f"[{i}/{len(articles)}] {article['headline'][:70]}...")
    if publish_article(article):
        success_count += 1
    print()

print(f"\n=== Done: {success_count}/{len(articles)} published successfully ===")
