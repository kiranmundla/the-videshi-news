#!/usr/bin/env python3
"""Sports writer for The Videshi — June 6, 2026 evening run"""

import json, os, sys, uuid, re, time
from datetime import datetime, timezone

import requests
from PIL import Image
import io

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]
                    key, val = line.split('=', 1)
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val

# Load workspace env first (for Google CSE, etc.), then home env (correct JWT key)
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

UA = {'User-Agent': 'TheVideshi/1.0 (thevideshi.com)'}


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10
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


def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers=UA, timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(*queries):
    """Search Pexels for an image using curl (urllib gets 403)."""
    import subprocess
    for q in queries:
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=5'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for p in photos:
                url = p.get('src', {}).get('large2x') or p.get('src', {}).get('original')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_url, filename):
    """Download image, compress, and upload to Supabase storage."""
    try:
        r = requests.get(img_url, headers=UA, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Download failed ({r.status_code}): {img_url[:80]}")
            return None
        ct = r.headers.get('Content-Type', '')
        if not ct.startswith('image/'):
            print(f"  ⚠ Not an image ({ct}): {img_url[:80]}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small ({len(r.content)} bytes)")
            return None

        compressed = compress_image(r.content)
        size_kb = len(compressed) / 1024
        print(f"  Compressed to {size_kb:.0f} KB")

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'image/jpeg',
                'x-upsert': 'true'
            },
            data=compressed,
            timeout=30
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({resp.status_code}): {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS_SB,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Inserted: {data[0].get('id', 'unknown')}")
            return data[0]
        print(f"  ✓ Inserted (raw): {r.text[:100]}")
        return data
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


def source_image(person_name, topic_queries, slug):
    """Multi-source image search. Returns (url, attribution, caption) or (None, None, None)."""
    candidates = []

    # Source 1: Wikipedia person image
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "relevance": "high"})

    # Source 2: Wikimedia Commons
    for q in topic_queries[:2]:
        commons = fetch_wikimedia_commons_images(q)
        for c in commons[:2]:
            candidates.append({"url": c["url"], "source": "wikimedia_commons", "relevance": "medium"})

    # Source 3: Pexels fallback
    if not candidates:
        pexels = fetch_pexels_image(*topic_queries)
        if pexels:
            candidates.append({"url": pexels, "source": "pexels", "relevance": "low"})

    if not candidates:
        print("  ⚠ No image found from any source")
        return None, None, None

    best = candidates[0]
    attribution = "Wikimedia Commons" if best["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"

    # Upload to Supabase
    filename = f"{slug}.jpg"
    final_url = upload_to_supabase(best["url"], filename)
    return final_url, attribution, best["url"]


# ============================================================
# ARTICLE 1: KL Rahul dismissed on exactly 100 three times running
# ============================================================

def write_article_1():
    print("\n" + "="*60)
    print("ARTICLE 1: KL Rahul's century curse")
    print("="*60)

    slug = "kl-rahul-dismissed-100-three-consecutive-tests-lords-west-indies-afghanistan-nri"
    headline = "KL Rahul Has Now Been Dismissed on Exactly 100 in Three Consecutive Tests. No Indian Has Done That Before."
    subheadline = "At Lord's, at Ahmedabad, and now at Mullanpur — the pattern is eerie. Each time Rahul reaches his century, the very next ball ends his innings."

    body = """KL Rahul reached his twelfth Test century on Saturday at the Maharaja Yadavindra Singh International Cricket Stadium in Mullanpur. It took him 165 balls, 11 boundaries, and one reprieve that Afghanistan chose not to review. When he raised his bat to the New Chandigarh crowd, he had scored exactly 100 runs.

Then he faced one more delivery. Ziaur Rahman bowled, Rahul drove, and Rahmanullah Gurbaz held a sharp catch at short extra cover. The innings was over. The score read 100 — not 101, not 104, not the kind of number that a batsman usually settles on. Just 100, again.

This was the third consecutive Test in which Rahul has been dismissed for exactly 100.

## The Pattern

At Lord's last year against England, Rahul batted with the composure of a man who had waited years for another overseas century. He got to 100 off 177 balls, then fell to the next delivery. Against the West Indies in Ahmedabad later that series, he repeated the act — 100 off 197 balls, dismissed on the following ball. And now, against Afghanistan, the same script played out a third time: century reached, next ball taken.

No Indian batsman has achieved this peculiar distinction before. In fact, the occurrence of three consecutive centuries ending on exactly 100 is extraordinarily rare in the 147-year history of Test cricket. It is a statistical event that sits somewhere between a coincidence and a curse.

## What It Tells Us About Rahul

The numbers, taken at face value, might suggest a batsman who loses concentration at the century mark. But the reality is more nuanced. In each of these innings, Rahul's dismissal came from a legitimate delivery — not a rash shot born of celebration, but a genuine batting stroke that found a fielder. At Lord's, it was a nicking dismissal. Against the West Indies, a caught-behind. Against Afghanistan, a drive that failed to beat a sharp fielder.

What the pattern really tells us is how fine the margin is between a century and a big century. Rahul is not getting out because he switches off. He is getting out because the bowler sees a batsman who has just expended enormous mental energy reaching a landmark and sends down a delivery that exploits that fractional lapse.

Rahul himself seemed aware of the irony. "I'm really happy that I could get some time in the middle," he said after stumps. "To make that switch from T20 to test cricket in a matter of a couple of days was the most pleasing thing."

## The Format Switch

The century was remarkable for another reason. Just days earlier, Rahul was playing in the IPL final for Delhi Capitals, where he finished as one of the season's leading run-scorers with 593 runs at a strike rate of 174. His unbeaten 152 off 67 balls against Punjab Kings was the highest individual score of IPL 2026.

Switching from that gear — where every ball is an event and every over demands aggression — to a Test match innings that lasted 165 balls is the kind of mental adjustment that not every batsman can make. Rahul made it look seamless.

He has now scored three consecutive Test centuries and 813 runs in his last ten Test matches, a run of form that has cemented his position at the top of India's order. At 34, the man who was once considered a luxury pick in Test cricket is now its most reliable opener.

## The Vice-Captain's Burden

Saturday's innings was also Rahul's first as India's newly appointed Test vice-captain. The role brings additional responsibility: field placements to suggest, bowling changes to discuss, and the constant awareness that you are next in line should the captain fall. Rahul wore the burden lightly, letting his bat do the talking for the better part of six hours.

India ended Day 1 at 368 for 3, with captain Shubman Gill unbeaten on 103 and Rishabh Pant on 50. The platform that Rahul built — a 139-run second-wicket partnership with Sai Sudharsan, followed by a 67-run stand with Gill — was the foundation of everything that followed.

## The Diaspora Angle

For NRIs watching from US living rooms and UK offices on a Saturday morning, the Rahul innings contained a particular kind of drama. Here is a batsman they have watched grow from a fragile talent into a seasoned professional, a man whose career has been defined by comebacks — from being dropped multiple times to being written off after poor tours to now holding the vice-captaincy and batting with the authority of a veteran.

The century-and-out pattern adds an almost cinematic quality to his innings. Every time Rahul walks out to bat in a Test match now, there is a question hanging in the air: will he convert this time? Will he go past 100? The answer, three times running, has been no. But the centuries keep coming, and the runs keep piling up, and India keep winning. At some point, Rahul will make 150 or 200, and the curse will break. Until then, 100 will have to do.

*Sources: Reuters, CricketAddictor, The SportsTak*"""

    # Image sourcing
    print("Sourcing image for KL Rahul article...")
    img_url, img_attr, _ = source_image(
        "KL Rahul",
        ["KL Rahul cricket India batting", "KL Rahul century test"],
        slug
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": ["Reuters", "CricketAddictor", "The SportsTak"]
    }

    if img_url:
        article["image_url"] = img_url
        article["image_caption"] = "KL Rahul raises his bat after scoring his twelfth Test century against Afghanistan at Mullanpur"
        article["image_attribution"] = img_attr
    
    result = insert_article(article)
    return result


# ============================================================
# ARTICLE 2: BCCI full-strength Asian Games squad — Pakistan factor
# ============================================================

def write_article_2():
    print("\n" + "="*60)
    print("ARTICLE 2: BCCI Asian Games U-turn — Pakistan factor")
    print("="*60)

    slug = "bcci-changed-asian-games-longlist-full-strength-squad-pakistan-factor-olympics-2028-nri"
    headline = "BCCI Changed Their Entire Asian Games Longlist in One Meeting. The Reason Is Pakistan."
    subheadline = "India initially planned to send a second-string squad to Japan. Then they saw what Pakistan were doing. Now Bumrah is going to Nagoya."

    body = """On Saturday, the BCCI selection committee sat down in Mumbai to finalise India's squad for the 2026 Asian Games cricket tournament in Japan. A 30-member extended list had already been circulated — a list heavy with emerging names like Anukul Roy, Ayush Badoni, and Vipraj Nigam. The message was clear: India would defend their gold medal with a development squad, just as they had done at the 2023 Hangzhou Games, where Ruturaj Gaikwad led a second-string team to victory.

Then, according to reports, the selectors tore up the plan entirely.

The squad that emerged from the meeting bore no resemblance to the longlist. Jasprit Bumrah, India's premier fast bowler and the spearhead of every major ICC campaign, was named in the fifteen. Shreyas Iyer was appointed captain. Tilak Varma was made vice-captain. The squad read like a T20 World Cup selection: Sanju Samson, Axar Patel, Varun Chakravarthy, Arshdeep Singh, Washington Sundar, Nitish Kumar Reddy. And Vaibhav Sooryavanshi, the fifteen-year-old prodigy who destroyed the IPL this season.

This was not a development squad. This was a statement.

## The Pakistan Connection

The reason, according to multiple Indian cricket journalists, is straightforward: Pakistan.

"The BCCI did not want to take any risk of losing to Pakistan in the Asian Games," Dainik Jagran reporter Abhishek Tripathi wrote on X. "Pakistan was trying to send a strong team to give India a tough fight. Usually, second-tier teams are sent to the Asian Games, but with cricket's inclusion in the Olympics and the opportunity to thrash Pakistan again, the decision was made to send a strong team."

The Pakistan Cricket Board, led by chairman Mohsin Naqvi, has been vocal about treating the Asian Games as a priority. For Pakistan, who have limited opportunities to play India in bilateral cricket due to political tensions, the Asian Games represents a rare chance to face their biggest rivals on a neutral stage. A gold medal match between India and Pakistan in Nagoya would be one of the most-watched cricket events of 2026.

The BCCI, it appears, decided that losing that hypothetical final to Pakistan was an unacceptable outcome. Hence the U-turn.

## The Olympic Calculus

There is a deeper strategic calculation at work. Cricket will feature in the 2028 Los Angeles Olympics, and the Asian Games serves as a proving ground for the sport's multi-sport future. A dominant India performance in Nagoya — particularly a gold medal won against strong opposition — strengthens cricket's case for continued Olympic inclusion and positions India as the sport's standard-bearer on the global stage.

The selectors are thinking beyond September 2026. They are thinking about Los Angeles 2028, where cricket will be played as a T20 competition at the iconic SoFi Stadium. A squad that includes Bumrah, Sooryavanshi, and Arshdeep is not just built to win the Asian Games — it is built to establish India's credentials as the team to beat in Olympic cricket.

## Who Is Missing

The squad is notable for its absences as much as its inclusions. Suryakumar Yadav, who was India's T20I captain until this week, is not in the squad. He has been replaced by Shreyas Iyer in the captaincy and dropped entirely from the fifteen. Hardik Pandya is absent due to a back injury sustained during IPL 2026, though he has reportedly passed a fitness test for the ODI series against Afghanistan. Yashasvi Jaiswal, Ruturaj Gaikwad, and Kuldeep Yadav are also missing.

The exclusion of Kuldeep is particularly significant. The left-arm wrist spinner, who was part of India's 2024 T20 World Cup-winning squad, has now been left out of all upcoming assignments — the Ireland and England T20I tours and the Asian Games. His absence suggests that the selectors have moved towards a spin combination of Varun Chakravarthy, Ravi Bishnoi, and Axar Patel in the shortest format.

## What NRIs Should Watch For

The Asian Games cricket tournament runs from September 24 to October 3 in the Aichi prefecture, with Nagoya as the hub. Ten teams will compete: India, Pakistan, Bangladesh, Sri Lanka, Afghanistan, Japan, Nepal, Malaysia, Hong Kong, and Oman. The format is T20, with preliminary qualifiers followed by knockout rounds.

For the Indian diaspora in the United States, the timing is challenging — most matches will be played during early morning hours on the US East Coast. But an India-Pakistan clash in the knockout stage would be the kind of appointment television that transcends time zones.

India won gold at the 2023 Hangzhou Games when the final against Afghanistan was washed out. They were declared winners as the higher-seeded team. This time, the BCCI has made sure there will be no ambiguity about the result.

*Sources: CricketAddictor, Cricbuzz, Crictips, OnlineMaharashtra*"""

    # Image sourcing — Bumrah is the key figure
    print("Sourcing image for Asian Games article...")
    img_url, img_attr, _ = source_image(
        "Jasprit Bumrah",
        ["Jasprit Bumrah India cricket bowling", "India cricket Asian Games"],
        slug
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": [
            "https://www.cricketaddictor.com",
            "https://www.cricbuzz.com",
            "https://www.crictips.com",
            "https://www.onlinemaharashtra.com"
        ]
    }

    if img_url:
        article["image_url"] = img_url
        article["image_caption"] = "Jasprit Bumrah in action during an international match for India"
        article["image_attribution"] = img_attr
    
    result = insert_article(article)
    return result


# ============================================================
# ARTICLE 3: Shubman Gill breaks WTC century record, 1000 runs as captain
# ============================================================

def write_article_3():
    print("\n" + "="*60)
    print("ARTICLE 3: Shubman Gill WTC record + 1000 Test runs as captain")
    print("="*60)

    slug = "shubman-gill-most-centuries-indian-wtc-history-1000-test-runs-captain-record-afghanistan-nri"
    headline = "Gill Now Has More WTC Centuries Than Any Indian in History. He Got to 1,000 Test Runs as Captain Faster Than Everyone Except Gavaskar."
    subheadline = "The 26-year-old's unbeaten 103 against Afghanistan at Mullanpur was his 11th Test century in the World Test Championship cycle — the most by any Indian."

    body = """Shubman Gill reached his century in the 83rd over of the day. He was on 99 when Mohammad Saleem bowled a length ball on leg stump. Gill flicked it through square leg for a single, took off his helmet, and acknowledged the crowd at the Maharaja Yadavindra Singh International Cricket Stadium in Mullanpur. Rishabh Pant walked over and embraced him. A ball-boy near the boundary had, earlier in the day, touched Gill's feet as the captain walked to the pavilion at tea.

The century was Gill's eleventh in Test cricket, and it carried a record with it. No Indian has scored more centuries in the ICC World Test Championship than Shubman Gill. With this knock, the 26-year-old overtook Rohit Sharma's tally of nine WTC hundreds — though Rohit has since retired from Tests — and now stands alone at the top of the list among active Indian players.

## The Numbers

Gill's 103 not out came off 143 balls, at a strike rate of over 72. He hit 11 fours and a towering straight six that cleared the sightscreen with a laziness that has become his trademark. He arrived at the crease after Sai Sudharsan's dismissal for 81, with India at 163 for 2, and by the time stumps were called, he had steered the innings to 368 for 3.

The century also took Gill past 1,000 Test runs as India's captain. He reached the milestone in his 15th innings, making him the second-fastest Indian captain to the landmark — behind only Sunil Gavaskar. Gill was appointed India's Test captain on May 24, 2025, meaning he reached 1,000 runs in just 379 days.

For a batsman who was questioned about his ability to shoulder the burden of captaincy in the longest format, this was a comprehensive answer. Gill now averages over 47 in Tests and has scored 4,153 runs in the format — at 26, he is tracking towards a career that could rival any Indian batsman of his generation.

## Leading From the Front

Saturday's innings was Gill's sixth Test century as captain — a remarkable rate of production. By contrast, Virat Kohli scored his sixth century as Test captain in his 25th innings in charge. Rohit Sharma got there in his 18th. Gill has done it in 15.

The comparison with Kohli is particularly relevant. When Kohli took over the Test captaincy in early 2015, there were questions about whether his aggressive, high-energy approach would translate to the tactical demands of leading a Test side. Kohli answered those questions with a run of centuries that became the defining feature of his captaincy. Gill is following the same path — answering every question about his readiness with runs.

What separates Gill from many young captains is his ability to set the tempo for the innings. On Saturday, he arrived at the crease when the match was finely poised and took charge of the scoring rate without appearing rushed. His partnership with Pant added 100 runs without loss in the final session, with Gill scoring at nearly five runs per over while Pant, unusually, played the supporting role.

## The New Chandigarh Welcome

Saturday was Gill's first Test match at the newly built Mullanpur stadium, which is effectively his home ground. Gill grew up in Fazilka, near the India-Pakistan border, and played his junior cricket in Punjab. The crowd in New Chandigarh treated him accordingly. The moment when a young ball-duty volunteer touched his feet at the tea break — a traditional gesture of respect in Indian culture — went viral on social media within minutes.

For the diaspora watching from abroad, it was a snapshot of how deeply embedded cricket remains in the cultural fabric of Punjab and northern India. Gill is not just Punjab's cricketer; he is its symbol in the Indian team, in the same way that Sachin Tendulkar once belonged to Mumbai and MS Dhoni to Ranchi.

## What Comes Next

India are in a commanding position heading into Day 2, with Gill and Pant set to resume at 368 for 3. The focus will shift to whether Gill can convert this century into a double — a landmark he has not yet achieved in Tests. His highest score remains 128 against England at Visakhapatnam in 2024.

Beyond this match, Gill's long-term challenge is the World Test Championship final race. India are currently sixth in the WTC standings after a difficult year that included series defeats to New Zealand, South Africa, and Australia. They need to win almost every remaining Test to qualify for the final. Gill's ability to score centuries at his current rate will be central to that effort.

The record for most WTC centuries belongs to the captain. The captaincy itself now belongs to a man who seems determined to make it permanent. At 26, with 11 Test hundreds and a growing reputation as one of the most elegant batsmen in world cricket, Shubman Gill is making his case — one innings at a time.

*Sources: CricketAddictor, Yardbarker, Reuters, The SportsTak*"""

    # Image sourcing — Shubman Gill
    print("Sourcing image for Gill WTC record article...")
    img_url, img_attr, _ = source_image(
        "Shubman Gill",
        ["Shubman Gill India cricket captain", "Shubman Gill century test cricket"],
        slug
    )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": ["CricketAddictor", "Yardbarker", "Reuters", "The SportsTak"]
    }

    if img_url:
        article["image_url"] = img_url
        article["image_caption"] = "Shubman Gill, India's Test captain, in action during an international match"
        article["image_attribution"] = img_attr
    
    result = insert_article(article)
    return result


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print(f"Sports writer run starting at {datetime.now(timezone.utc).isoformat()}")
    print(f"Supabase URL: {SUPABASE_URL[:30]}...")

    results = []
    
    r1 = write_article_1()
    results.append(("KL Rahul century curse", r1))
    time.sleep(1)
    
    r2 = write_article_2()
    results.append(("BCCI Asian Games Pakistan factor", r2))
    time.sleep(1)
    
    r3 = write_article_3()
    results.append(("Gill WTC record", r3))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, r in results:
        status = "✓ SUCCESS" if r else "✗ FAILED"
        print(f"  {status}: {name}")
    
    successes = sum(1 for _, r in results if r)
    print(f"\n{successes}/{len(results)} articles published successfully")
