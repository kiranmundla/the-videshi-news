#!/usr/bin/env python3
"""Sports writer for The Videshi - June 10, 2026 batch"""

import json
import os
import uuid
import requests
from datetime import datetime, timezone

# Load env
def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                val = val.strip().strip('"').strip("'")
                os.environ[key.strip()] = val

load_env('~/.env.supabase')

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Inserted: {data[0].get('slug')} (id={data[0].get('id')})")
            return True
    print(f"  ✗ Error: {r.status_code} - {r.text[:300]}")
    return False

now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

articles = []

# ============================================================
# ARTICLE 1: Gill's ODI Captaincy Challenge
# ============================================================
articles.append({
    'id': str(uuid.uuid4()),
    'headline': "Gill Has Won Every Test He Has Captained. In ODIs, He Has Lost Every Series.",
    'subheadline': "As India assembles in Mohali for the first bilateral ODI series against Afghanistan, the real question is not about the opponents — it is about what happens inside the dressing room before the 2027 World Cup.",
    'body': """Shubman Gill has a problem that most young captains would envy — and dread in equal measure. At 26, he has led India to their biggest-ever Test victory, an innings-and-300-run demolition of Afghanistan that ended on Monday in New Chandigarh. In the longest format, his record is unblemished. In ODIs, it is the opposite.

Since taking over as India's full-time ODI captain last October, Gill has presided over series defeats in Australia and at home against New Zealand. The only ODI series India won during this stretch — against South Africa — came when Gill was sidelined with a neck injury. The paradox is hard to ignore.

Now, as India's ODI squad assembles in Mohali this week ahead of the three-match series against Afghanistan starting Saturday in Dharamsala, the conversation has shifted from the pitch to the dressing room.

## Two Formats, Two Different Captains

In Tests, Gill inherited a squad in transition. Rohit Sharma, Virat Kohli, and Ravichandran Ashwin had all retired from the format, leaving him to build from scratch with a group of hungry young players who had nothing to prove to anyone but themselves. The results have been emphatic.

The ODI setup is a different animal entirely. Rohit, now 39, remains in the squad and firmly believes he can lead India one better than the 2023 World Cup final heartbreak. Kohli, turning 38 in November, recently made it clear he does not want to be in an environment where he is made to prove his value. Though Kohli will miss the Afghanistan series due to a hamstring injury sustained during the IPL final, his shadow looms large.

Sources close to the BCCI told the Times of India that several senior players have been in constant touch with the board's power centres to get clarity about their roles in the lead-up to the 2027 World Cup in South Africa.

## Gambhir's Unfinished Business

Head coach Gautam Gambhir has stamped his authority on India's T20I and Test setups. The T20 World Cup triumph in March bore his fingerprints across every selection and tactical decision, and chief selector Ajit Agarkar was fully aligned. But in ODIs, Gambhir has largely let things take their course.

"With such big players in the team, Gill needs to have a stronger say in the dressing room," a BCCI source said. "Gambhir hasn't got involved in the planning as intently as he has done in the other two formats."

The Afghanistan series, then, is not really about Afghanistan. It is the formal onset of India's 2027 World Cup preparation, and the first real test of whether Gill and Gambhir can align a dressing room that includes two former captains with very different ideas about their futures.

## The Series Itself

India's ODI squad reflects the tension between continuity and renewal. Gill leads, with Shreyas Iyer as vice-captain. Rohit and Hardik Pandya, both cleared fit by the BCCI's Centre of Excellence after IPL injuries, will join the squad. Yashasvi Jaiswal comes in as Kohli's replacement.

Three uncapped players — left-arm seamer Prince Yadav, towering pacer Gurnoor Brar, and Ranji Trophy sensation Harsh Dubey — are in the 15, offering Gill the chance to shape the squad's next cycle. This is the first-ever bilateral ODI series between India and Afghanistan, moving beyond their sole previous meeting at the 2023 World Cup in Delhi.

The matches are in Dharamsala (June 13), Lucknow (June 17), and Chennai (June 20), all starting at 1:30 PM IST.

## The Diaspora Watches

For NRI cricket fans, the series offers a window into what Indian cricket will look like by the time the World Cup arrives in South Africa. The transition from the Rohit-Kohli era has been gradual and occasionally awkward. Gill's Test captaincy has shown he can lead with clarity when given a clean slate. Whether he can do the same with two legends still in the room — and a coach who has not yet fully engaged in the ODI project — is the question that makes this series worth watching, regardless of the opposition.

The scorecards will take care of themselves. What happens in Mohali this week, before a ball is bowled, may matter more.

*Sources: Times of India, CricTracker, Star Sports*""",
    'slug': 'shubman-gill-odi-captaincy-challenge-india-afghanistan-bilateral-series-2027-world-cup-nri',
    'category': 'sports',
    'vertical': 'sports',
    'image_url': 'https://upload.wikimedia.org/wikipedia/commons/3/34/Shubman_Gill_2023_%28cropped%29.jpg',
    'image_caption': "Shubman Gill, India's ODI captain, faces his biggest leadership test yet",
    'image_attribution': 'Wikimedia Commons',
    'status': 'review',
    'is_editorial': False,
    'published_at': now,
    'sources': json.dumps(['Times of India', 'CricTracker', 'Star Sports', 'ICC'])
})

# ============================================================
# ARTICLE 2: India Wins 102 Gold at Inaugural World Yogasana Championships
# ============================================================
articles.append({
    'id': str(uuid.uuid4()),
    'headline': "India Won 102 Gold Medals. The Nearest Country Won Three. Yogasana Is Now a Global Sport.",
    'subheadline': "The inaugural World Yogasana Championship in Ahmedabad drew 522 athletes from 79 countries. India's dominance was total — but the real story is the ancient practice's sprint toward Olympic recognition.",
    'body': """When the first-ever World Yogasana Championship concluded at the EKA Arena in Ahmedabad on Sunday, India's medal haul read like a misprint: 102 gold, 8 silver, 4 bronze. Japan, the nearest rival, had three gold. Argentina's entire delegation consisted of one athlete — Nabila Barraza from Lionel Messi's hometown — who walked away with two gold and three silver.

The numbers tell only part of the story. The championship, held from June 4 to 8, was a five-day exercise in turning an ancient Indian spiritual practice into a globally competitive sporting discipline — one with a formal Code of Points, age-grouped categories, and a stated pathway toward Olympic recognition.

## From Ashram to Arena

Yogasana as a competitive sport is a relatively recent phenomenon. The discipline involves athletes performing defined postures — asanas — judged on precision, difficulty, form, and control. Think of it as the intersection of gymnastics and meditation, scored like figure skating.

India had already signalled its intent at the Asian Yogasana Sport Championship in Delhi in April 2025, where the team swept 83 gold medals. The World Championship was the next logical step, and its scale surprised even organisers: 522 athletes from 79 countries, with 31 nations winning at least one medal.

Prime Minister Narendra Modi inaugurated the event via video conference, calling yoga "India's timeless gift to humanity." The venue, Ahmedabad's EKA Arena, will also host events at the 2030 Commonwealth Games — a connection that underscores the ambitions behind the championship.

## The Competition Itself

India fielded a 122-member contingent across six age categories, ranging from Sub-Junior (10–14 years) to Senior C (45–55 years). Events tested artistic, rhythmic, and strength-based yogasana skills in both individual and pairs routines.

Beyond India's dominance, the medal table revealed genuine global interest. Nepal emerged as the second most successful contingent by total medals (52, including 36 silver), while Uzbekistan claimed 25 medals. Athletes from 31 countries medalled — a respectable spread for an inaugural edition of any discipline.

The championship was backed by the Ministry of Youth Affairs and Sports, the Ministry of Ayush, the Sports Authority of India, and the Gujarat state government. World Yogasana, the international governing body, organised the event alongside Yogasana Bharat, its Indian affiliate.

## The American Connection

What gives the championship particular diaspora resonance is that it was preceded by the United States Yogasana Championship in Connecticut, which served as the selection platform for Team USA. The event was supported by the Consulate General of India in New York, the Hindu Diaspora Foundation, and the Hindu Temple Society of North America.

For the millions of Indian-Americans who practice yoga — often in forms far removed from competitive asana — the spectacle of their cultural heritage becoming a medal sport on the world stage carries a specific kind of pride. It is one thing for yoga to be mainstream wellness in Brooklyn and Bangalore alike. It is another for it to have a Code of Points, a world championship, and Olympic aspirations.

## The Road to the Olympics

The organisers have been explicit about the goal: Olympic recognition. Yogasana was included as a demonstration sport at the Khelo India Youth Games in 2023, and the World Championship in Ahmedabad is designed to build the institutional infrastructure — a global governing body, standardised rules, international participation — that the International Olympic Committee requires before considering a new discipline.

Whether yogasana can bridge the gap from demonstration sport to Olympic programme is an open question. But after 522 athletes from 79 countries competed across five days in a purpose-built arena, the trajectory is unmistakable.

The ancient practice has new ambitions. India, unsurprisingly, is leading the way.

*Sources: The Bridge, IANS, World Yogasana, The Indian Eye*""",
    'slug': 'india-102-gold-inaugural-world-yogasana-championship-ahmedabad-olympic-recognition-nri',
    'category': 'sports',
    'vertical': 'sports',
    'image_url': 'https://upload.wikimedia.org/wikipedia/commons/6/63/EKA_Arena_Stadium%28TransStadia%29.jpg',
    'image_caption': "EKA Arena in Ahmedabad, venue of the inaugural World Yogasana Championship",
    'image_attribution': 'Wikimedia Commons',
    'status': 'review',
    'is_editorial': False,
    'published_at': now,
    'sources': json.dumps(['The Bridge', 'IANS', 'World Yogasana', 'The Indian Eye'])
})

# Insert all articles
print(f"\n📝 Inserting {len(articles)} sports articles...\n")
success = 0
for i, article in enumerate(articles, 1):
    print(f"Article {i}: {article['headline'][:70]}...")
    if insert_article(article):
        success += 1

print(f"\n✅ Done: {success}/{len(articles)} articles inserted successfully")
