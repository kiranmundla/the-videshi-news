#!/usr/bin/env python3
"""Post 4 Videshi articles to X as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
from datetime import datetime, timezone

import requests
import tweepy

# --- Load env files ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                env[key] = val
    return env

twitter_env = load_env("~/workspace/.env.twitter")
supabase_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env.get("X_CONSUMER_KEY") or twitter_env.get("TWITTER_CONSUMER_KEY") or twitter_env.get("API_KEY")
CONSUMER_SECRET = twitter_env.get("X_CONSUMER_SECRET") or twitter_env.get("TWITTER_CONSUMER_SECRET") or twitter_env.get("API_SECRET")
ACCESS_TOKEN = twitter_env.get("X_ACCESS_TOKEN") or twitter_env.get("TWITTER_ACCESS_TOKEN") or twitter_env.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = twitter_env.get("X_ACCESS_TOKEN_SECRET") or twitter_env.get("TWITTER_ACCESS_TOKEN_SECRET") or twitter_env.get("ACCESS_TOKEN_SECRET")
SUPABASE_SERVICE_ROLE_KEY = supabase_env.get("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

# --- Setup tweepy ---
auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

sb_headers = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json"
}

# --- Tweet log ---
log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
tweet_log = {}
if os.path.exists(log_path):
    with open(log_path) as f:
        tweet_log = json.load(f)

# --- Articles and composed posts ---
articles_to_post = [
    {
        "id": "0376ff1d-8c52-46dc-8cd9-0141ea10318a",
        "slug": "india-maha-water-mission-200-crore-isro-mou-satellite-water-management-startups-20260601",
        "headline": "India Just Launched a ₹200 Crore Fund for Water Tech Startups and Signed an MoU With ISRO to Monitor Water From Space.",
        "category": "news",
        "image_url": "https://images.pexels.com/photos/29277511/pexels-photo-29277511.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "post_text": """🇮🇳 NEWS | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

INDIA BETS ₹200 CRORE ON WATER TECH — AND ROPES IN ISRO TO WATCH FROM ORBIT

India just made its biggest move yet on water innovation. The government launched the MAHA Water Mission — a ₹200 crore, five-year programme that will fund consortia of universities, national labs, startups, and MSMEs to develop and deploy water technology solutions. Each selected consortium can receive up to ₹20 crore.

The programme was unveiled at a national workshop at Dr. Ambedkar International Centre in New Delhi. It's jointly run by the Anusandhan National Research Foundation and the Ministry of Jal Shakti, and targets five priority areas: water resource management, drinking water quality, ecological health, water use efficiency, and climate resilience.

The bigger headline? ISRO signed an MoU to bring satellite-based monitoring to India's water infrastructure — meaning groundwater tracking and flood forecasting will now have eyes in space. An open call for research proposals and a separate startup track through the BHARAT-WIN Portal are both live now.

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

▸ ₹200 crore fund over 5 years, up to ₹20 crore per consortium
▸ ISRO MoU brings satellite data to groundwater and flood monitoring
▸ Open call for proposals live now — startups and MSMEs eligible
▸ Five focus areas including climate resilience and circular economy

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/india-maha-water-mission-200-crore-isro-mou-satellite-water-management-startups-20260601

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    },
    {
        "id": "fefa2f8f-b497-44ed-a6f0-564033cafa22",
        "slug": "rajya-sabha-27-seats-nominations-begin-june-18-polling-jharkhand-nda-india-bloc-20260601",
        "headline": "India Just Began Nominations for 27 Rajya Sabha Seats. The Votes Will Be Cast on June 18.",
        "category": "news",
        "image_url": "https://images.pexels.com/photos/2573473/pexels-photo-2573473.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "post_text": """🇮🇳 NEWS | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

27 RAJYA SABHA SEATS UP FOR GRABS — NOMINATIONS OPEN, VOTING ON JUNE 18

The Election Commission formally started the clock on one of India's biggest upper house elections this year. Nominations opened today for 27 Rajya Sabha seats and multiple state Legislative Council seats, with polling day set for June 18.

The elections cover 24 biennial vacancies across 10 states — Andhra Pradesh and Gujarat with 4 each, Karnataka with 4, Madhya Pradesh and Rajasthan with 3 each, Jharkhand with 2, and one each in Manipur, Meghalaya, Arunachal Pradesh, and Mizoram. Three by-elections in Maharashtra, Tamil Nadu, and Odisha round out the count. Candidates have until June 8 to file nominations, scrutiny is on June 9, and the withdrawal deadline is June 11.

The real contest is in Jharkhand, where both the ruling JMM-led INDIA bloc and the BJP are eyeing both seats. The state's fractured arithmetic — with 47 ruling coalition MLAs, 31 BJP, and smaller parties holding the balance — makes this the one race where the outcome isn't already written.

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

▸ 27 Rajya Sabha seats across 10 states, polling June 18
▸ Nomination deadline: June 8; withdrawal deadline: June 11
▸ Jharkhand is the key battleground — both alliances want both seats
▸ By-elections in Maharashtra, Tamil Nadu, and Odisha also scheduled

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/rajya-sabha-27-seats-nominations-begin-june-18-polling-jharkhand-nda-india-bloc-20260601

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    },
    {
        "id": "5c081a2d-c597-4317-a2ab-3b0e6f2bbb29",
        "slug": "delhi-saket-building-collapse-six-dead-owner-absconding-fir-culpable-homicide-20260601",
        "headline": "A Building Near Delhi's Saket Metro Collapsed on Saturday. Six People Are Dead and the Owner Is Missing.",
        "category": "news",
        "image_url": "https://images.pexels.com/photos/15861615/pexels-photo-15861615.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "post_text": """🇮🇳 NEWS | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

SIX DEAD IN DELHI BUILDING COLLAPSE NEAR SAKET METRO — OWNER ON THE RUN

A three-storey commercial building near the Saket Metro Station in south Delhi collapsed on Saturday evening, killing six people and injuring eight others. The building on Western Marg in Saidulajab housed a coaching institute, cafes, offices, and a ground-floor canteen that served students preparing for medical entrance exams. Construction work was reportedly underway on the upper floors when the structure gave way around 6 PM.

NDRF, Delhi Fire Services, and DDMA teams worked through the night with heavy machinery, hydraulic cutters, and sniffer dogs, pulling nine survivors from the rubble. Among the six killed was Parvati, who ran the canteen — she had initially escaped but went back inside to help trapped students. The building owner, Kuldeep, is absconding. An FIR for culpable homicide not amounting to murder has been filed.

The Delhi government has ordered a structural audit of all buildings in the area and launched a compensation package: ₹10 lakh per victim's family, ₹5 lakh for seriously injured, and ₹1 lakh for minor injuries.

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

▸ 6 dead, 8 injured in Saket-area building collapse on May 30
▸ Building owner Kuldeep absconding; FIR filed under culpable homicide
▸ Canteen worker Parvati died after going back in to help trapped students
▸ Delhi govt orders structural audit, ₹10 lakh compensation per victim's family

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/delhi-saket-building-collapse-six-dead-owner-absconding-fir-culpable-homicide-20260601

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    },
    {
        "id": "594a6490-b89d-4417-a70b-44145a27e183",
        "slug": "ultra-hni-migration-nri-property-selling-kotak-bank-report-20260601",
        "headline": "One in Five of India's Ultra-Rich Wants to Move Abroad. The Rest Are Trying to Figure Out How to Sell the House They Left Behind.",
        "category": "nri-world",
        "image_url": "https://images.pexels.com/photos/30608874/pexels-photo-30608874.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "post_text": """🌏 NRI WORLD | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

ONE IN FIVE OF INDIA'S ULTRA-RICH WANTS OUT — AND NRIS CAN'T SELL THE HOUSE THEY LEFT BEHIND

There are two kinds of NRI property stories. The aspirational one: a tech exec in the Bay Area buying a ₹15 crore flat in Gurugram as an investment hedge. The exhausting one: a family in New Jersey spending three years trying to sell ancestral land in Jalandhar, fighting forged Power of Attorney documents and a legal system that moves at geological speed.

Both are getting more common. A new Kotak Wealth report says one in five ultra-high-net-worth Indians — those with assets over ₹25 crore — is either migrating or planning to. Most intend to settle permanently abroad while keeping their Indian passports. Professionals show higher migration tendencies than entrepreneurs, and the 36-40 and 61+ age brackets are overrepresented.

India's Ultra-HNI population is expected to hit 4.3 lakh by 2028, with combined wealth of ₹359 trillion. Nearly a third already hold global assets — real estate in Dubai, London, Singapore. For NRIs already abroad, selling Indian property remains a maze of FEMA rules, TDS obligations, and repatriation limits that trip up even the well-advised.

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

▸ 1 in 5 Indian Ultra-HNIs (₹25 cr+ assets) planning to emigrate — Kotak report
▸ Ultra-HNI population projected to reach 4.3 lakh by 2028
▸ NRIs face FEMA, TDS, and repatriation hurdles when selling Indian property
▸ Professionals migrate more than entrepreneurs; 36-40 age bracket most mobile

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/ultra-hni-migration-nri-property-selling-kotak-bank-report-20260601

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    }
]

# --- Post each article ---
posted = 0
errors = []
tweet_urls = []

for i, article in enumerate(articles_to_post):
    print(f"\n{'='*50}")
    print(f"Posting article {i+1}/4: {article['slug'][:60]}...")
    
    # Download image
    media_id = None
    tmp_path = None
    try:
        img_resp = requests.get(article["image_url"], timeout=15)
        img_resp.raise_for_status()
        # Determine extension
        content_type = img_resp.headers.get("content-type", "image/jpeg")
        ext = ".jpg" if "jpeg" in content_type or "jpg" in content_type else ".png"
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=ext)
        with os.fdopen(tmp_fd, 'wb') as f:
            f.write(img_resp.content)
        print(f"  ✓ Image downloaded ({len(img_resp.content)} bytes)")
        
        media = api_v1.media_upload(filename=tmp_path)
        media_id = media.media_id
        print(f"  ✓ Image uploaded to X (media_id={media_id})")
    except Exception as e:
        print(f"  ⚠ Image failed: {e} — posting without image")
        media_id = None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
    
    # Post tweet
    try:
        kwargs = {"text": article["post_text"]}
        if media_id:
            kwargs["media_ids"] = [media_id]
        
        response = client.create_tweet(**kwargs)
        tweet_id = response.data['id']
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✓ Posted! {tweet_url}")
        tweet_urls.append(tweet_url)
        
        # Update Supabase
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
            headers=sb_headers,
            json={"tweeted_at": now_utc},
            timeout=15
        )
        if patch_resp.status_code < 300:
            print(f"  ✓ Supabase updated (tweeted_at={now_utc})")
        else:
            print(f"  ⚠ Supabase update failed: {patch_resp.status_code} {patch_resp.text}")
        
        # Log tweet
        tweet_log[str(tweet_id)] = {
            "article_id": article["id"],
            "slug": article["slug"],
            "posted_at": datetime.utcnow().isoformat() + "Z"
        }
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'w') as f:
            json.dump(tweet_log, f, indent=2)
        
        posted += 1
        
    except Exception as e:
        err_msg = f"Article {article['slug'][:40]}: {e}"
        errors.append(err_msg)
        print(f"  ✗ FAILED: {e}")
    
    # Wait between posts
    if i < len(articles_to_post) - 1:
        print("  ⏳ Waiting 30 seconds...")
        time.sleep(30)

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: {posted}/4 articles posted to X")
if tweet_urls:
    print("Tweet URLs:")
    for url in tweet_urls:
        print(f"  {url}")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  ✗ {e}")
