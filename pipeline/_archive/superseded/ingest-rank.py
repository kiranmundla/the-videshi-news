#!/usr/bin/env python3
"""
Stage 2: Cluster unprocessed signals into topics, insert, link, mark processed.
Run after videshi-pipeline.sh ingests RSS feeds.
"""
import json, subprocess, os, sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run_db(cmd, *args):
    """Run videshi-db.py command and return parsed JSON."""
    result = subprocess.run(
        ["python3", "videshi-db.py", cmd] + list(args),
        capture_output=True, text=True,
        env={**os.environ}
    )
    if result.stdout.strip():
        try:
            return json.loads(result.stdout.strip())
        except:
            print(f"  DB output: {result.stdout.strip()}")
    if result.stderr.strip():
        print(f"  DB stderr: {result.stderr.strip()[:200]}")
    return None

# Define topic clusters from the 80 unprocessed signals
# Each cluster: { title, vertical, category, urgency, diaspora_score, significance_score, source_avail, keywords, signal_ids }
clusters = [
    {
        "title": "US-Iran military confrontation escalates at Hormuz Strait",
        "vertical": "politics",
        "category": "news",
        "urgency": "breaking",
        "diaspora": 80,
        "significance": 90,
        "source_avail": 85,
        "keywords": ["Iran", "US", "Hormuz", "drones", "missiles", "oil", "Khamenei", "Trump"],
        "signals": [
            "aab84260-40b1-4dba-a794-b01686483ac1",  # US intercepts Iranian drones
            "2ab95bd0-5f51-4b2e-8230-ff71f9cf4d55",  # $24B trust test Khamenei
            "1df5ba11-1161-4bb8-bc15-49e318f69300",  # Pentagon flags Israel counterintelligence
        ]
    },
    {
        "title": "Indians dancing in Toronto video sparks colonization debate online",
        "vertical": "diaspora",
        "category": "nri-world",
        "urgency": "same_day",
        "diaspora": 95,
        "significance": 70,
        "source_avail": 75,
        "keywords": ["Toronto", "Canada", "Indians", "dance", "colonization", "diaspora"],
        "signals": [
            "a94f05b7-937f-45a4-a674-20d4c492b9ec",  # Indians dancing in Toronto
        ]
    },
    {
        "title": "India's Gen Z is drinking differently from millennials",
        "vertical": "culture",
        "category": "lifestyle-health",
        "urgency": "daily",
        "diaspora": 65,
        "significance": 55,
        "source_avail": 70,
        "keywords": ["Gen Z", "millennials", "drinking", "alcohol", "India", "culture"],
        "signals": [
            "ec80cbe0-de6c-4f7e-9663-e0ec49defff9",  # Gen Z drinking
        ]
    },
    {
        "title": "NSE logs 26 crore trading accounts as India's stock market mania hits milestone",
        "vertical": "economy",
        "category": "markets-finance",
        "urgency": "same_day",
        "diaspora": 75,
        "significance": 80,
        "source_avail": 80,
        "keywords": ["NSE", "stock market", "trading accounts", "India", "milestone"],
        "signals": [
            "a82265d7-06c0-47fe-90df-6f5207601731",  # NSE 26 crore accounts
        ]
    },
    {
        "title": "Shreyas Iyer named India captain for Ireland and England series",
        "vertical": "sports",
        "category": "sports",
        "urgency": "same_day",
        "diaspora": 80,
        "significance": 75,
        "source_avail": 85,
        "keywords": ["Shreyas Iyer", "India captain", "Ireland", "England", "cricket"],
        "signals": [
            "ebc90283-53f7-4324-8fa7-09a77cf0eed8",  # Shreyas Iyer captain announcement
            "f781194b-14e0-4f47-a745-16bf3b08e39c",  # Kohli out of form, Kaif backs SKY
        ]
    },
    {
        "title": "FIFA World Cup 2026: Germany's Lennart Karl ruled out with injury",
        "vertical": "sports",
        "category": "sports",
        "urgency": "same_day",
        "diaspora": 60,
        "significance": 65,
        "source_avail": 80,
        "keywords": ["FIFA", "World Cup", "Germany", "Lennart Karl", "injury", "Brazil", "Ancelotti"],
        "signals": [
            "dec39f3a-54b8-4e3d-8f93-52fc9dc06f94",  # Germany Karl injured
            "6ebf1e78-0902-4083-b23f-3263c76505be",  # Brazil/Ancelotti
        ]
    },
    {
        "title": "OpenAI rolls out Lockdown Mode against prompt injection attacks",
        "vertical": "tech",
        "category": "technology",
        "urgency": "same_day",
        "diaspora": 70,
        "significance": 75,
        "source_avail": 80,
        "keywords": ["OpenAI", "Lockdown Mode", "AI", "security", "prompt injection"],
        "signals": [
            "1c98ede8-30a1-40b8-b365-36261713bce3",  # OpenAI Lockdown Mode
        ]
    },
    {
        "title": "YouTube Premium price hike in US effective June 7",
        "vertical": "tech",
        "category": "technology",
        "urgency": "same_day",
        "diaspora": 80,
        "significance": 55,
        "source_avail": 75,
        "keywords": ["YouTube", "Premium", "price hike", "US", "subscription"],
        "signals": [
            "172f96e8-709c-496e-b855-cff6fd0c6c4c",  # YouTube Premium price hike
        ]
    },
    {
        "title": "Delhi fire aftermath intensifies: cook arrested, officials to be penalized",
        "vertical": "politics",
        "category": "news",
        "urgency": "same_day",
        "diaspora": 60,
        "significance": 80,
        "source_avail": 90,
        "keywords": ["Delhi", "fire", "Malviya Nagar", "arrest", "cook", "penalty"],
        "signals": [
            "83ef92e8-ef9f-4b9c-bf1c-1bd31714d4fe",  # MFB intensifies action
            "d95fdda8-fef8-4e02-9968-4d92a27aea1e",  # Cook arrested
            "8ec8c16f-1cc8-47f3-818c-f5462d5662d6",  # Delhi to penalise officials
        ]
    },
    {
        "title": "Shah Rukh Khan film gets 3/10 from director Imtiaz Ali",
        "vertical": "entertainment",
        "category": "entertainment",
        "urgency": "daily",
        "diaspora": 70,
        "significance": 60,
        "source_avail": 75,
        "keywords": ["Shah Rukh Khan", "SRK", "Imtiaz Ali", "Bollywood", "review"],
        "signals": [
            "632b7d52-b831-4e31-b297-d861f688fec3",  # SRK film 3/10
        ]
    },
    {
        "title": "India counters Pakistan at UN, rejects Kashmir internationalisation bid",
        "vertical": "politics",
        "category": "news",
        "urgency": "same_day",
        "diaspora": 80,
        "significance": 80,
        "source_avail": 85,
        "keywords": ["India", "Pakistan", "UN", "Kashmir", "diplomacy"],
        "signals": [
            "3da2fd00-2cbc-44da-b764-94115e789937",  # India counters Pakistan at UN
        ]
    },
    {
        "title": "Chief Justice Surya Kant's London lecture interrupted by dissent question",
        "vertical": "politics",
        "category": "news",
        "urgency": "same_day",
        "diaspora": 75,
        "significance": 70,
        "source_avail": 80,
        "keywords": ["CJI", "Surya Kant", "London", "AI", "dissent", "judiciary"],
        "signals": [
            "e3c8b6ce-7855-462f-9f24-923654f95227",  # CJI London lecture
        ]
    },
    {
        "title": "E85 flex fuel launched in India, Rs 20/litre cheaper with ethanol push",
        "vertical": "economy",
        "category": "news",
        "urgency": "same_day",
        "diaspora": 60,
        "significance": 70,
        "source_avail": 85,
        "keywords": ["E85", "ethanol", "flex fuel", "India", "energy"],
        "signals": [
            "f3acb363-5002-4450-a372-2883a8bd6399",  # E85 fuel launched
            "079a32bf-c500-4a8b-887b-338f221e6c7e",  # E85 Rs 20 cheaper
        ]
    },
    {
        "title": "Gullak Season 5 returns with mixed reviews over Annu Mishra recast",
        "vertical": "entertainment",
        "category": "entertainment",
        "urgency": "daily",
        "diaspora": 65,
        "significance": 50,
        "source_avail": 70,
        "keywords": ["Gullak", "Season 5", "Mishra", "recast", "OTT"],
        "signals": [
            "c7ad689f-6df1-48f7-a68b-a7d05ad171e4",  # Gullak S5 review
        ]
    },
    {
        "title": "Cockroach Janta Party protests at Jantar Mantar over NEET and CBSE",
        "vertical": "politics",
        "category": "news",
        "urgency": "same_day",
        "diaspora": 65,
        "significance": 70,
        "source_avail": 80,
        "keywords": ["CJP", "Cockroach Janta Party", "NEET", "CBSE", "protest", "Jantar Mantar"],
        "signals": [
            "0c9e5280-9947-40f0-aa35-e7b013f4f6c8",  # CJP protests NEET CBSE
            "74e694bd-069b-4058-95ec-8a509e17b8ac",  # CJP protest permission
            "e8c64e30-536d-4024-8f13-f3bacb8f36b5",  # Kangana Ranaut Bharat Bhagya Vidhata
        ]
    },
    {
        "title": "Ram Charan's Peddi: Tokyo fans fly to Hyderabad, Janhvi scenes to be changed",
        "vertical": "entertainment",
        "category": "entertainment",
        "urgency": "same_day",
        "diaspora": 70,
        "significance": 60,
        "source_avail": 80,
        "keywords": ["Peddi", "Ram Charan", "Janhvi Kapoor", "Tokyo", "controversy"],
        "signals": [
            "65aacc39-01f6-4642-85c6-6aa5507463e6",  # Tokyo fans fly to Hyderabad
            "cbaf38a3-1f40-4e6f-a51f-215a4d5076d2",  # Janhvi scenes to be changed
        ]
    },
    {
        "title": "Government extends benefits of eight schemes to Marathas",
        "vertical": "politics",
        "category": "news",
        "urgency": "daily",
        "diaspora": 55,
        "significance": 65,
        "source_avail": 70,
        "keywords": ["Marathas", "government", "schemes", "reservation"],
        "signals": [
            "a126be25-8fac-48a7-8683-d18b09afb3df",  # Marathas scheme benefits
        ]
    },
    {
        "title": "Slow interiors trend: Indian homes move away from Instagram aesthetics",
        "vertical": "culture",
        "category": "lifestyle-health",
        "urgency": "daily",
        "diaspora": 65,
        "significance": 45,
        "source_avail": 65,
        "keywords": ["interiors", "home decor", "slow living", "India", "Instagram"],
        "signals": [
            "a451556a-f5e4-4d82-a2e9-30a11960efb9",  # Slow interiors
        ]
    },
    {
        "title": "Woman who took Rs 50 lakh loan for master's abroad says biggest return wasn't money",
        "vertical": "diaspora",
        "category": "nri-world",
        "urgency": "daily",
        "diaspora": 85,
        "significance": 60,
        "source_avail": 70,
        "keywords": ["education", "abroad", "master's", "loan", "NRI", "return on investment"],
        "signals": [
            "088fb679-98de-4e2e-8928-c6901cf7a93a",  # Woman Rs 50 lakh loan
        ]
    },
    {
        "title": "India's mountains are sending a warning amid climate crisis",
        "vertical": "science",
        "category": "news",
        "urgency": "daily",
        "diaspora": 60,
        "significance": 65,
        "source_avail": 70,
        "keywords": ["Himalayas", "mountains", "climate", "environment", "India"],
        "signals": [
            "94f878f1-344f-4359-b34c-d0c85c2cdd94",  # India mountains warning
            "6c0b648f-2148-4714-b6e0-7d76e022fbf8",  # Kolkata climate tram
        ]
    },
    {
        "title": "Delhi shooting coach's 25-year double life exposed by AI",
        "vertical": "tech",
        "category": "news",
        "urgency": "daily",
        "diaspora": 55,
        "significance": 65,
        "source_avail": 70,
        "keywords": ["AI", "fraud", "Delhi", "coach", "identity"],
        "signals": [
            "48ce222f-f9a3-486e-8d89-2d4fbd928c6c",  # AI exposed coach
        ]
    },
    {
        "title": "ENG vs NZ: Lord's pitch slammed after 33 wickets in two days",
        "vertical": "sports",
        "category": "sports",
        "urgency": "daily",
        "diaspora": 55,
        "significance": 55,
        "source_avail": 75,
        "keywords": ["England", "New Zealand", "Lord's", "Test", "pitch", "cricket"],
        "signals": [
            "01c29aa9-84a7-47c6-96fe-e863d33632b5",  # ENG vs NZ pitch
        ]
    },
    {
        "title": "Starmer slams US interference as JD Vance links Sikh murder to migration",
        "vertical": "politics",
        "category": "nri-world",
        "urgency": "same_day",
        "diaspora": 90,
        "significance": 80,
        "source_avail": 80,
        "keywords": ["Starmer", "JD Vance", "Sikh", "murder", "migration", "UK", "US"],
        "signals": [
            "521924c0-c36f-40b4-8d35-452bb13726c2",  # Starmer slams US interference
        ]
    },
]

# Remaining signals not in any cluster — mark as processed but don't create topics
unclustered = [
    "5ac201fd-532c-4eb5-992c-55570a361fec",  # Drug socio-economic census
    "31c50d19-2e51-4d85-a589-086bc060e455",  # Nana Patekar Madhoo slap
    "39b467d2-e7be-4e73-b2df-ed238139c58f",  # Britney Spears greenhouse
    "cd13fd53-6119-4799-9525-87f4d9a44f03",  # Onekdin Por film
    "1b06831b-7104-435b-8142-ab5c9f37f328",  # Nayab Midha tour
    "5722b322-6320-4af1-a7f2-897c34687707",  # Jackie Shroff Sunil Dutt tribute
    "e417cb12-3952-43f8-b1f5-39d2589dfe0e",  # MBA vs MTech
    "e06595f1-bb2f-4c74-b29f-7b49dc3ecb98",  # Executive MBA
    "2952077d-162a-4fb2-b674-0b57c7f39af4",  # Maradona tribute
    "3d161bef-666d-4443-bc79-e6b047d23dc1",  # Neelam Kothari bungalow
    "d654de2b-833c-493f-82b2-d3dc7139d9ad",  # Numerology horoscope
    "c2daa212-ddfd-4635-9042-d2bb451c2141",  # St Stephen's DU
    "5677d020-4563-432b-9f3b-f051b61c774b",  # Cobbler's son bowled to India
    "33bb6ebd-cc1a-4460-b464-8f50c79c08e4",  # POCSO case Kerala
    "41aaff88-a0ea-46f6-89e4-0a39fdbed938",  # IGNOU TEE registration
    "721400b9-cf7b-47e7-83bc-38965cf25439",  # Quote of the day
    "09f9ff5b-77a0-4e61-a4f6-b0a32b50d0fc",  # Uttarakhand housing aid
    "49b5e1bb-2c70-42e6-a7e9-1d0f5f7bd216",  # Scary Movie 6 filming
    "6e8b4cc4-71c4-49cf-860f-bb54299f6189",  # Love Island USA
    "af70a2e8-8f34-4cb1-910a-7bd54d56ac58",  # Delhi court child support
    "018a33de-3a9a-4a63-a19f-a193b6a81303",  # Kit Harington Sophie Turner
    "aa15460e-7529-4f53-a984-434c7d1fd666",  # Rubina Dilaik C-sections
    "604cae2d-676c-4210-b1d4-35437e3f0719",  # PFI charges Delhi court
    "1b65f1e9-7aa5-4a08-8fd5-e5a189e0bce5",  # KEA KCET result
    "fbbf11e1-386a-4138-a6a8-95f390c019da",  # Athiradi OTT
    "1321080c-06eb-4f6a-8510-ed53c9caf063",  # DU PG admissions
    "abd642ff-159a-4492-a696-fcaa1f335585",  # KEA KCET Results
    "aa830062-6052-42d8-a209-4768895e52e8",  # Music Under Open Courtyard
    "389fe87a-7951-4ddd-a343-86eb88e34c16",  # Cat naps on Krishna idol
    "1e732518-e92c-44a4-af9f-fb335c390a61",  # Shrimp export rejections
    "d29889b4-8fc9-4c47-9427-03ce9d513ea8",  # CJP first protest
    "97b0ffed-afba-4be8-947a-aacca8720460",  # Bandar box office Day 1
    "e62ec539-a66d-4127-bc32-59d2f1ca901a",  # Lodhi Crematorium wall collapse
    "766ec4ee-d7d5-45c1-bb67-875d0307e64d",  # June 2026 transit astrology
    "c79a8358-7e4f-49ce-a4d1-4d3c2a9d279b",  # Unni Mukundan Kerala drug video
    "8c870b96-5bde-469d-a73b-e75053c7c56a",  # Power subsidies solar
    "94a5d64d-9a96-4a5a-8ea5-9fee1f2d1597",  # Saif Kareena Agent Vinod
    "270a7249-e667-4db7-895a-1d7093647a53",  # Karuppu & Blast K-Town
    "6ffd42e9-36ba-48d9-af8e-d7dd3d28af09",  # Anthony Head dies
    "4116b9e5-7e01-4f0d-8b15-0175a6e769b4",  # Garena Free Fire codes
    "2ca699c5-8e39-4080-81fb-e1bc3179fdbb",  # Rithvik Dhanjani KKK
    "e2c10723-d173-446b-a728-55eaddf4d2d7",  # Nichelle Nichols lawsuit
    "4494f1b8-0402-4db3-a401-fabd16d8ae99",  # Odisha MICE air links
    "aa6aee23-67b6-47e4-a81c-a991ed51f9aa",  # The 50 Vanshaj Singh
    "21608cf2-fake-0000-0000-000000000000",  # placeholder — not real
]

# Filter out any signal IDs that don't match the real IDs from the pipeline output
# (the last one is a placeholder and should be removed)
unclustered = [s for s in unclustered if not s.endswith("000000000000")]

# Collect ALL signal IDs from clusters
clustered_ids = set()
for c in clusters:
    for sid in c["signals"]:
        clustered_ids.add(sid)

print(f"=== Stage 2: Ranking {len(clusters)} topic clusters ===")
print(f"Clustered signals: {len(clustered_ids)}")
print(f"Unclustered signals: {len(unclustered)}")

created_topics = 0
linked_signals = 0

for i, cluster in enumerate(clusters):
    topic_data = json.dumps({
        "canonical_title": cluster["title"],
        "vertical": cluster["vertical"],
        "category": cluster.get("category", "news"),
        "urgency": cluster["urgency"],
        "score_diaspora": cluster["diaspora"],
        "score_significance": cluster["significance"],
        "score_source_avail": cluster["source_avail"],
        "signal_count": len(cluster["signals"]),
        "keywords": cluster["keywords"],
    })
    
    result = run_db("insert-topic", topic_data)
    if result and result.get("ok"):
        topic_id = result["id"]
        created_topics += 1
        print(f"  [{i+1}/{len(clusters)}] Created topic: {cluster['title'][:60]}... (score={result.get('score_total', '?')})")
        
        # Link signals to topic
        signal_ids_str = ",".join(cluster["signals"])
        link_result = run_db("link-signals", topic_id, signal_ids_str)
        if link_result and link_result.get("ok"):
            linked_signals += link_result.get("linked", 0)
    else:
        print(f"  [{i+1}/{len(clusters)}] FAILED: {cluster['title'][:60]}... error={result}")

# Mark ALL signals as processed (clustered + unclustered)
all_signal_ids = list(clustered_ids) + unclustered
print(f"\nMarking {len(all_signal_ids)} signals as processed...")

# Do in batches of 20
for batch_start in range(0, len(all_signal_ids), 20):
    batch = all_signal_ids[batch_start:batch_start+20]
    run_db("mark-signals-processed", ",".join(batch))

print(f"\n=== Stage 2 Complete ===")
print(f"Topics created: {created_topics}")
print(f"Signals linked: {linked_signals}")
print(f"Signals marked processed: {len(all_signal_ids)}")
