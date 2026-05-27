#!/usr/bin/env python3
"""Sports writer — 2026-05-26 17:00 PDT (00:00 UTC May 27): 2 articles + score decay.

Article 1: Federation Cup Day 4 finale — javelin miss, Kujur's 0.03s heartbreak,
           Samardeep upsets Toor, CWG Glasgow qualification picture
Article 2: SRH "2026 is the new 2016" — the only team to ever win IPL after taking
           the Eliminator route, now facing RR on Wednesday
"""

import os, json, uuid, requests, subprocess, sys, urllib.parse
from datetime import datetime, timezone, timedelta

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


# ── Image sourcing: Wikipedia first (MANDATORY for person articles) ──

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")

    # Try alternate name forms with disambiguation
    alternates = []
    if "(" not in person_name:
        alternates = [
            f"{person_name} (cricketer)",
            f"{person_name} (Indian cricketer)",
            f"{person_name} (athlete)",
        ]
    for alt in alternates:
        encoded_alt = urllib.parse.quote(alt.replace(' ', '_'))
        try:
            r2 = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_alt}",
                headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
                timeout=10,
            )
            if r2.status_code == 200:
                data2 = r2.json()
                img2 = data2.get("originalimage", {}).get("source") or data2.get("thumbnail", {}).get("source")
                if img2:
                    print(f"  ✓ Wikipedia image found for '{alt}': {img2[:80]}...")
                    return img2
        except Exception:
            pass
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels — ONLY as fallback when Wikipedia returns nothing."""
    pexels_key = ""
    try:
        with open(os.path.expanduser("~/workspace/.env.pexels")) as f:
            for line in f:
                if line.startswith("PEXELS_API_KEY="):
                    pexels_key = line.strip().split("=", 1)[1].strip('"').strip("'")
    except Exception:
        pass
    if not pexels_key:
        print("  WARN: No Pexels key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": pexels_key},
                params={"query": q, "per_page": 1, "orientation": "landscape"},
                timeout=15,
            )
            if r.status_code == 200 and r.json().get("photos"):
                img_url = r.json()["photos"][0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{q}': {img_url[:60]}...")
                return img_url
        except Exception as e:
            print(f"  WARN: Pexels fetch failed for '{q}': {e}")
    return None


def download_image(url, dest_path):
    """Download an image URL to a local path."""
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code == 200 and len(r.content) > 1000:
            with open(dest_path, "wb") as f:
                f.write(r.content)
            print(f"  Image downloaded: {dest_path} ({len(r.content)} bytes)")
            return True
        else:
            print(f"  WARN: Download failed or too small: {r.status_code}, {len(r.content)} bytes")
    except Exception as e:
        print(f"  WARN: Download error: {e}")
    return False


def upload_image(article_id, local_path):
    """Upload image to Supabase storage."""
    bucket = "article-images"
    filename = f"{article_id}.jpg"
    with open(local_path, "rb") as f:
        img_data = f.read()
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
    upload_headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(upload_url, headers=upload_headers, data=img_data)
    if r.status_code >= 400:
        print(f"  WARN: image upload failed for {article_id}: {r.status_code} {r.text[:300]}")
        return ""
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
    print(f"  Image uploaded: {public_url}")
    return public_url


def update_article_image(article_id, image_url, attribution="Wikimedia Commons"):
    """Patch article with image URL and attribution."""
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=HEADERS,
        json={"image_url": image_url, "image_attribution": attribution},
    )
    print(f"  Image URL + attribution patch: {r.status_code}")


def insert_article(article):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS, json=article)
    if r.status_code >= 400:
        print(f"  ERROR inserting {article.get('slug','?')}: {r.status_code} {r.text[:500]}")
    r.raise_for_status()
    return r.json()


def decay_scores():
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=18)).strftime('%Y-%m-%dT%H:%M:%S')
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&published_at=lt.{cutoff}&score_total=gt.0&select=id,score_total",
        headers={**HEADERS, "Prefer": "return=representation"},
    )
    if r.status_code >= 400:
        print(f"  Decay fetch error: {r.status_code}")
        return 0
    articles = r.json()
    count = 0
    for a in articles:
        new_score = max(0, a["score_total"] - 5)
        rp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{a['id']}",
            headers=HEADERS,
            json={"score_total": new_score},
        )
        if rp.status_code < 400:
            count += 1
    return count


# ── ARTICLE 1: Federation Cup Day 4 finale ──

a1_id = str(uuid.uuid4())
a1 = {
    "id": a1_id,
    "headline": "India's Best Javelin Throwers Could Not Reach Eighty-Two Metres. Their Fastest Sprinter Missed the Commonwealth Games by Three Hundredths of a Second. A Shot Putter Nobody Expected Won Gold. The Federation Cup's Final Day Was the Cruelest.",
    "subheadline": "The 29th National Senior Athletics Federation Cup concluded at Birsa Munda Stadium in Ranchi on Sunday with a final day that produced as much heartbreak as heroism. Shivam Lohakare threw 81.71 metres in the javelin — a personal best, four throws beyond 80 metres, and still 0.90 metres short of the Commonwealth Games qualification standard. Animesh Kujur won the 200-metre gold in 20.64 seconds and walked off the track in silence: the CWG mark was 20.61. He missed it by 0.03 seconds. Meanwhile, Samardeep Singh Gill stunned two-time Asian Games gold medallist Tajinderpal Singh Toor in the shot put with a 20.46-metre throw — his first ever beyond 20 metres — and Praveen Chithravel sealed his Glasgow ticket with a 17.08-metre triple jump. The four-day meet that produced three national records and India's fastest-ever 100-metre sprinter ended with its most consequential event — the javelin — falling silent.",
    "slug": "federation-cup-day-4-javelin-miss-kujur-200m-heartbreak-samardeep-toor-upset-cwg-glasgow-20260526",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "The Commonwealth Games in Glasgow in July will be the biggest stage for Indian athletics between now and the 2028 Los Angeles Olympics. For the Indian diaspora in the UK and Scotland, Glasgow 2026 is a home Games — the nearest a major multi-sport event gets to the British-Indian communities of London, Birmingham, Leicester, and Edinburgh. The Federation Cup was the sole trial. Every qualification standard met or missed at Birsa Munda Stadium in Ranchi on Sunday directly determines whether those diaspora fans will have athletes to cheer in Glasgow. Praveen Chithravel's 17.08-metre triple jump means NRIs in Glasgow can buy tickets for the triple jump final. Samardeep Singh Gill's shot put breakthrough means they can add the shot put. Animesh Kujur's 0.03-second 200-metre miss means they cannot buy tickets for the 200-metre final — at least not with an Indian sprinter in it. The javelin's collective failure to reach 82.61 metres means that unless selectors grant discretionary picks, the event Neeraj Chopra made India's most popular track-and-field discipline will have no Indian representative in Glasgow. The Federation Cup matters to the diaspora because Glasgow is where the results become personal.",
    "tags": ["Federation Cup 2026", "Ranchi", "Birsa Munda Stadium", "Shivam Lohakare", "Animesh Kujur", "Samardeep Singh Gill", "Tajinderpal Singh Toor", "Praveen Chithravel", "Abdulla Aboobacker", "Neeraj Chopra", "Commonwealth Games 2026", "Glasgow", "Athletics", "Javelin Throw", "Shot Put", "Triple Jump", "200m Sprint", "Yashas Palaksha", "Vithya Ramraj"],
    "urgency": "daily",
    "sources": [
        "https://revsportz.in/javelin-fails-to-deliver-kujur-misses-cwg-mark-samardeep-upsets-toor-on-final-day-of-federation-cup-2026/",
        "https://www.newspointapp.com/english/sports/federation-cup-day-4-shivam-lohakare-shines-in-javelin-animesh-kujur-misses-200m-cwg-mark-narrowly-aninews/articleshow/14504820170fe29bfa8e0f9d251c334e1cbaa477",
        "https://mykhel.com/athletics/federation-cup-2026-live-updates-results-scores-medals-day-1-ranchi-236301.html",
        "https://indiasportshub.com/athletics/animesh-kujur-reclaims-national-record-in-historic-night-for-indian-sprinting-at-federation-cup-2026/"
    ],
    "word_count": 880,
    "score_total": 68,
    "body": """The Federation Cup is not a glamorous event. It is held at a state athletic stadium in Ranchi, a city that most of the Indian sporting press associates with MS Dhoni's home rather than track and field. The stands are sparse. The broadcast is a YouTube stream. The timing equipment is adequate but not world-class.

None of that mattered this week. The 29th National Senior Athletics Federation Cup was the sole selection trial for the 2026 Commonwealth Games in Glasgow. Every Indian athlete who wanted to compete in Scotland had four days at Birsa Munda Stadium to prove they deserved to go. On the final day, several of them proved it. Several others came agonisingly close.

## The javelin's collective failure

India has become a javelin country. Neeraj Chopra's Olympic gold in Tokyo, his World Championship gold in Budapest, and his national record of 90.23 metres have turned a field event into a prime-time spectacle. When Indian fans think of athletics, they think of the javelin.

On Sunday in Ranchi, the javelin thought about disappointing them.

Shivam Lohakare won gold with 81.71 metres — a personal best that included four throws beyond 80 metres. It was, by any national standard, an excellent performance. It was also 0.90 metres short of the Commonwealth Games qualification mark of 82.61 metres. Lohakare is 24 years old. He threw consistently. He competed with discipline. The distance was simply not enough.

Yashvir Singh took silver with 80.80 metres. Rohit Yadav claimed bronze with 80.40 metres. Neither approached the Glasgow standard.

The most painful absence belonged to Sachin Yadav, the Asian Championships silver medallist who threw 86.27 metres at last year's World Championships in Tokyo. Yadav finished fifth with 79.07 metres — seven metres below his best. The gap between what he can do and what he did in Ranchi is the size of a small apartment.

Neeraj Chopra did not compete. He continues rehabilitation for a back injury before heading to Switzerland for an extended training camp. His absence left a hole in the field that nobody could fill.

Unless the Athletics Federation of India grants discretionary selections — which it has done in the past for athletes with strong international records — India may send no javelin thrower to Glasgow. The event that Chopra made India's signature will go unrepresented.

## Three hundredths of a second

Animesh Kujur had already secured his Glasgow ticket in the 100 metres. On Day 2, he ran 10.15 seconds — a personal best and a national record that lasted exactly one race before Gurindervir Singh broke it with 10.09 the following day.

On Sunday, Kujur entered the 200-metre final looking to add a second event to his Commonwealth Games programme. The qualification standard was 20.61 seconds. He ran 20.64 seconds. He won the gold medal. He missed Glasgow by 0.03 seconds.

Three hundredths of a second is the time it takes to blink. It is the difference between running in Glasgow and watching from home. Kujur walked off the track having won the race but lost the result that mattered.

Jishnu Prasad finished second in 20.98 seconds. Abhay Singh was third in 21.01 seconds. Neither was close to the standard. Indian men's 200-metre sprinting has one elite performer, and he was three hundredths short.

## The upset nobody predicted

The men's shot put was supposed to belong to Tajinderpal Singh Toor. The two-time Asian Games gold medallist has been India's dominant shot putter for the better part of a decade. His personal best of 21.49 metres, set at the 2022 Asian Games in Hangzhou, remains the national record.

On Sunday, Toor threw 20.07 metres. It was enough for silver. It was not enough to hold off Samardeep Singh Gill, a 25-year-old from Madhya Pradesh who had never thrown beyond 20 metres in competition.

Gill's winning throw was 20.46 metres — a personal best by a significant margin and comfortably beyond the CWG qualification standard of 20.36 metres. It was the breakthrough performance of the entire Federation Cup: a young athlete choosing the biggest day of his career to produce the biggest throw of his life.

Toor's 20.07 metres fell below the Glasgow standard. The man who has represented India at two Olympics and two Asian Games may not make the Commonwealth Games squad. The man who beat him will.

## The confirmation and the double

Praveen Chithravel entered the triple jump as the defending champion and national record holder. He left as a Commonwealth Games qualifier. His winning jump of 17.08 metres was well beyond the 16.89-metre standard, and he won by 45 centimetres over 2022 Commonwealth Games silver medallist Abdulla Aboobacker, who managed 16.63 metres.

Chithravel is one of the few Indian field athletes who has been consistently competitive on the international circuit. His qualification was expected. He delivered it with the minimum of drama and the maximum of professionalism.

In the 400-metre hurdles, Yashas Palaksha clocked 49.00 seconds to edge out Santhosh Kumar T by six hundredths of a second. Both breached the CWG standard of 50.27 seconds. It was the best head-to-head race of the final day — two athletes pushing each other to times neither might have reached alone.

On the women's side, Vithya Ramraj completed a double by adding the 400-metre hurdles gold in 56.61 seconds to the flat 400-metre title she had won earlier in the competition. Neither time met the CWG standard of 54.67 seconds, but the ambition was evident.

## What the four days produced

The Federation Cup's four days in Ranchi rewrote the record books on Days 2 and 3 and tested the nerves on Day 4. The full picture: Gurindervir Singh ran 10.09 seconds to become the fastest Indian man in history. Vishal TK became the first Indian to score over 8,000 points in the decathlon. Tejaswin Shankar and Saurabh Dev both cleared 5.45 metres in the pole vault, breaking the national record twice in ninety minutes. Krishna Jayasankar qualified for Glasgow in the women's shot put with 17.35 metres.

And then, on the final day, the javelin — India's most celebrated athletics event — could not produce a single Glasgow-qualifying throw. Animesh Kujur missed the 200-metre standard by a margin so small it is invisible to the naked eye. Samardeep Singh Gill announced himself by dethroning a champion.

The Commonwealth Games begin on July 23 in Glasgow. India will send a squad that includes sprinters, jumpers, and at least one shot putter who had never thrown 20 metres before Sunday. Whether it includes a javelin thrower depends on what the selectors decide next.

The Federation Cup is over. The selection meetings are about to begin. That is where the final heartbreaks — or reprieves — will be determined.""",
}


# ── ARTICLE 2: SRH "2026 is the new 2016" — the Eliminator route ──

a2_id = str(uuid.uuid4())
a2 = {
    "id": a2_id,
    "headline": "Only One Team in IPL History Has Won the Title After Taking the Eliminator Route. It Was Sunrisers Hyderabad. It Was 2016. On Wednesday, They Start the Same Journey Again.",
    "subheadline": "RCB's 92-run demolition of Gujarat Titans in Qualifier 1 on Tuesday confirmed the IPL 2026 bracket: the defending champions are in the final, and everyone else must take the long way. For Sunrisers Hyderabad, that means the Eliminator against Rajasthan Royals at the Maharaja Yadavindra Singh International Cricket Stadium in New Chandigarh on Wednesday evening. Win, and they face Gujarat Titans in Qualifier 2 on Friday. Win that, and they face RCB in the final on Sunday in Ahmedabad. Lose either, and they go home. The internet has already given this storyline a name: 2026 is the new 2016. In 2016, SRH finished third in the league phase, won the Eliminator, won the Qualifier, and won the final — the only team in eighteen seasons of the IPL to win the title through the Eliminator bracket. Pat Cummins, Heinrich Klaasen, and Travis Head are about to find out whether history can repeat at a venue where teams batting first have scored 250.",
    "slug": "srh-2026-new-2016-eliminator-route-ipl-history-pat-cummins-klaasen-rr-wednesday-20260526",
    "category": "Sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "diaspora_angle": "For the Indian diaspora — particularly the Hyderabadi communities in the US, UK, and Gulf — SRH's Eliminator run is personal in a way that neutral cricket analysis rarely captures. Hyderabad is one of the largest source cities for Indian emigration to the US tech sector. The SRH fanbase in the Bay Area, Seattle, New Jersey, and the DC corridor is anchored in Hyderabadi identity: the city's food, language, and cricket. The 2016 title — won under David Warner, in a season where Hyderabad's scrappy bowling and clutch batting defined the campaign — remains a foundational memory. For NRIs who watched the 2016 final at 4 AM Pacific time and celebrated with biryani and Irani chai, the phrase '2026 is the new 2016' is not a meme. It is a hope. Wednesday's Eliminator against Rajasthan Royals starts at 7:30 PM IST, which is 7:00 AM Pacific, 10:00 AM Eastern, and 3:00 PM BST. If SRH win, Qualifier 2 is Friday at the same times. If they make the final, it is Sunday in Ahmedabad — a three-match sprint across five days, each one an early morning for the American diaspora and a teatime event for the UK contingent.",
    "tags": ["Sunrisers Hyderabad", "IPL 2026", "Eliminator", "Rajasthan Royals", "Pat Cummins", "Heinrich Klaasen", "Travis Head", "Jofra Archer", "Yashasvi Jaiswal", "David Warner", "IPL 2016", "New Chandigarh", "Mullanpur", "Abhishek Sharma", "Ishan Kishan", "Riyan Parag", "Ravindra Jadeja", "SRH", "RR", "IPL Playoffs", "RCB"],
    "urgency": "daily",
    "sources": [
        "https://www.crictracker.com/cricket-match-predictions/ipl-2026-eliminator-srh-vs-rr-match-prediction-who-will-win-todays-ipl-match-between-sunrisers-hyderabad-vs-rajasthan-royals/",
        "https://www.crictracker.com/ipl/stats-approaching-milestones-and-player-records-ipl-2026-eliminator-sunrisers-hyderabad-vs-rajasthan-royals/",
        "https://m.cricbuzz.com/cricket-news/ipl",
        "https://www.sportingnews.com/in/ipl/news/rcb-vs-gt-rajat-patidar-inspires-royal-challengers-bengaluru-to-ipl-final-2026-after-beating-titans/"
    ],
    "word_count": 910,
    "score_total": 75,
    "body": """The IPL has been played eighteen times. In those eighteen seasons, eleven different teams have reached the final. Ten of them got there through Qualifier 1 or Qualifier 2 — the route reserved for the top two finishers in the league phase. The arithmetic of the double-elimination format is designed to reward regular-season consistency. Finish first or second, and you get two chances. Finish third or fourth, and you get one.

Only one team in IPL history has won the trophy after entering the bracket at the Eliminator — the first match, the one where you lose and go home. That team was Sunrisers Hyderabad. The year was 2016. The parallel is already trending.

## The 2016 blueprint

In 2016, Sunrisers Hyderabad finished third in the league phase. They entered the Eliminator against Kolkata Knight Riders at the Feroz Shah Kotla in Delhi and won by 22 runs. They played Gujarat Lions in Qualifier 2 at the same venue and won by four wickets. They played Royal Challengers Bengaluru in the final at the Chinnaswamy in Bangalore and won by eight runs.

Three knockout matches. Three wins. Three different opponents. Zero second chances.

David Warner scored 848 runs that season — the most by any batsman in a single IPL campaign at the time. Bhuvneshwar Kumar took 23 wickets. Ben Cutting scored 39 off 15 balls in the final, a cameo that turned a losing position into a title. Yuvraj Singh provided the experience. Mustafizur Rahman provided the mystery.

The 2016 SRH squad was not the most talented in the tournament. They were the most resilient. They won the three matches that mattered most by treating each one as a final.

## Why the internet says 2026 is the new 2016

The structural parallels are significant enough that the comparison has moved from social media joke to genuine analytical framework.

In 2016, SRH finished third. In 2026, SRH finished third — 16 points, behind RCB and Gujarat Titans on 18 each.

In 2016, the Eliminator was at a neutral venue. In 2026, the Eliminator is at the Maharaja Yadavindra Singh International Cricket Stadium in New Chandigarh — neutral territory for both SRH and Rajasthan Royals.

In 2016, SRH's strength was an elite pace attack led by Bhuvneshwar Kumar and a dominant overseas batsman in Warner. In 2026, SRH's strength is a power-hitting middle order led by Heinrich Klaasen and the captaincy of Pat Cummins — an Australian all-rounder who leads from the front with both bat and ball.

The differences are equally important. The 2016 IPL was played before the Impact Player rule. The 2026 version allows a twelfth man to substitute in during the match, and SRH have used Travis Head as their Impact Player to devastating effect — the Australian opener has functioned as a floating tactical weapon, available to bat or bowl depending on match situation.

## Klaasen's 606 and what it means

Heinrich Klaasen's 606 runs this season from number four represent the most prolific middle-order campaign in T20 franchise cricket history. The South African has scored at an average of 50.5 and a strike rate of 171.1, numbers that place him in a statistical category of his own.

But Klaasen's importance to SRH extends beyond the runs. He is the reason opposition captains bowl their best spells between overs 12 and 16. He is the reason field placements change when he walks to the crease. He is the reason SRH's lower order — Nitish Kumar Reddy, Shivang Kumar, the tail — faces less pressure than it should, because Klaasen absorbs the bowling attack's resources.

In the playoffs, the quality of bowling improves. The margins shrink. Klaasen has not played an IPL knockout match before Wednesday. His entire tournament career — 606 runs, a strike rate north of 170, the most feared T20 middle-order bat on the planet — has been accumulated in league matches. The Eliminator is different. The bowlers are better. The pressure is heavier. The ground is smaller.

## What Rajasthan Royals bring

Rajasthan Royals qualified for the playoffs on net run rate, not dominance. They won nine and lost five in the league phase. They are the fourth-best team in the tournament. They are here because the format allows four teams, not because they overwhelmed anyone.

But the Royals have Jofra Archer. The England fast bowler has taken 21 wickets this season and scored 32 off 15 balls with the bat in his last match. Archer bowls at 150 kilometres per hour. He has the yorker, the bouncer, the slower ball, and the temperament of a man who has bowled death overs in World Cup finals.

Yashasvi Jaiswal opens the batting with the controlled aggression of a future India captain. Riyan Parag captains with the energy of a 24-year-old who has nothing to lose. Ravindra Jadeja — acquired mid-season after his retirement from Indian domestic cricket — provides the kind of match experience that money cannot buy and statistics cannot measure.

SRH have beaten RR twice this season — by 57 runs in Hyderabad and by five wickets in Jaipur. The head-to-head record across all IPL seasons is 14-9 in SRH's favour. But head-to-head records in the regular season tell you what happened in matches where losing was survivable. In the Eliminator, losing is terminal.

## The venue and the pitch

The Maharaja Yadavindra Singh International Cricket Stadium in New Chandigarh has already produced a 250-plus total this season. The boundaries are short. The outfield is fast. Batting is easier in the second innings when the dew settles — which is why the toss, ordinarily a coin flip of modest importance, becomes a strategic decision that could determine the match.

If Cummins wins the toss, he will almost certainly bowl first. If Parag wins it, he will do the same. Both captains know that chasing at New Chandigarh is preferable to defending. The question is which team's bowling attack can contain the other's batting in conditions that favour the bat.

## Three matches in five days

The Eliminator is on Wednesday. Qualifier 2 is on Friday. The final is on Sunday in Ahmedabad. If SRH win all three, they will have played three knockout matches in five days — the same sprint that the 2016 squad completed.

Pat Cummins was 22 years old in 2016 and was not part of any IPL squad. He is now 33, the captain, and the leader of a franchise that has not won the title since that year. The 2016 parallel is flattering. It is also a reminder that what SRH achieved then has not been replicated in the decade since.

Wednesday is the first step. The Eliminator starts at 7:30 PM IST. If SRH lose, the comparison dies with it. If they win, the refrain gets louder: 2026 is the new 2016.

Only the Eliminator will tell them if that is prophecy or nostalgia.""",
}


if __name__ == "__main__":
    print("=" * 60)
    print("Sports Writer — 2026-05-26 17:00 PDT (00:00 UTC May 27)")
    print("=" * 60)

    # Check for duplicate slugs first
    for art in [a1, a2]:
        slug = art["slug"]
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
            headers=HEADERS,
        )
        if r.status_code == 200 and r.json():
            print(f"  SKIP: slug already exists: {slug}")
            sys.exit(0)

    # ── Insert + image: Article 1 (Federation Cup Day 4) ──
    print("\n[1/2] Inserting: Federation Cup Day 4 finale...")
    insert_article(a1)
    print(f"  ✓ Inserted: {a1['slug']}")

    # Image: Animesh Kujur or Praveen Chithravel on Wikipedia
    img1_url = fetch_wikipedia_person_image("Animesh Kujur")
    img1_attribution = "Wikimedia Commons"
    if not img1_url:
        img1_url = fetch_wikipedia_person_image("Praveen Chithravel")
    if not img1_url:
        img1_url = fetch_wikipedia_person_image("Tajinderpal Singh Toor")
    if not img1_url:
        img1_url = fetch_wikipedia_person_image("Neeraj Chopra")
        # Neeraj is mentioned prominently as absent — his image contextualizes the javelin void
    if not img1_url:
        # Pexels fallback: specific javelin / athletics imagery
        img1_url = fetch_pexels_image("javelin throw athletics stadium", "athletics track field stadium")
        img1_attribution = "The Videshi"

    if img1_url:
        img1_path = f"/tmp/{a1_id}.jpg"
        if download_image(img1_url, img1_path):
            uploaded_url = upload_image(a1_id, img1_path)
            if uploaded_url:
                update_article_image(a1_id, uploaded_url, img1_attribution)

    # ── Insert + image: Article 2 (SRH 2026 = 2016 narrative) ──
    print("\n[2/2] Inserting: SRH '2026 is the new 2016' — Eliminator route narrative...")
    insert_article(a2)
    print(f"  ✓ Inserted: {a2['slug']}")

    # Image: Pat Cummins on Wikipedia (SRH captain, central figure)
    img2_url = fetch_wikipedia_person_image("Pat Cummins")
    img2_attribution = "Wikimedia Commons"
    if not img2_url:
        img2_url = fetch_wikipedia_person_image("Heinrich Klaasen")
    if not img2_url:
        img2_url = fetch_wikipedia_person_image("David Warner (cricketer)")
    if not img2_url:
        img2_url = fetch_pexels_image("cricket T20 stadium floodlights crowd", "cricket match evening stadium")
        img2_attribution = "The Videshi"

    if img2_url:
        img2_path = f"/tmp/{a2_id}.jpg"
        if download_image(img2_url, img2_path):
            uploaded_url = upload_image(a2_id, img2_path)
            if uploaded_url:
                update_article_image(a2_id, uploaded_url, img2_attribution)

    # ── Score decay ──
    print("\nDecaying old article scores...")
    decayed = decay_scores()
    print(f"  Decayed {decayed} articles")

    print(f"\n{'=' * 60}")
    print(f"Done. 2 articles published.")
    print(f"  1: {a1['slug']}")
    print(f"  2: {a2['slug']}")
    print(f"  IDs: {a1_id}, {a2_id}")
