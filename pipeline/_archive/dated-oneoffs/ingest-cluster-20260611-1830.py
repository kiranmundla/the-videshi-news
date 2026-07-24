#!/usr/bin/env python3
"""
Cluster 80 unprocessed signals into topics, insert to Supabase, mark processed.
Run: 2026-06-11 18:30 UTC
"""
import json, subprocess, os, sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run_db(cmd, *args):
    result = subprocess.run(
        ["python3", "videshi-db.py", cmd] + list(args),
        capture_output=True, text=True,
        env={**os.environ}
    )
    if result.stdout.strip():
        try:
            return json.loads(result.stdout.strip())
        except:
            print(f"  DB output: {result.stdout.strip()[:200]}")
    if result.stderr.strip():
        print(f"  DB stderr: {result.stderr.strip()[:200]}")
    return None

# Define topic clusters from unprocessed signals
clusters = [
    {
        "title": "Trump calls off Iran strikes, cites progress in nuclear talks",
        "vertical": "politics",
        "category": "news",
        "urgency": "breaking",
        "diaspora": 85,
        "significance": 95,
        "source_avail": 90,
        "keywords": ["Trump", "Iran", "strikes", "nuclear talks", "Hormuz", "ceasefire", "diplomacy"],
        "signals": [
            "00f7ecff-5175-44fd-b08c-a09f94befada",
        ]
    },
    {
        "title": "Iran's economy holds up after 100 days of US-Israel war",
        "vertical": "economy",
        "category": "news",
        "urgency": "same_day",
        "diaspora": 70,
        "significance": 75,
        "source_avail": 80,
        "keywords": ["Iran", "economy", "sanctions", "war", "oil", "resilience"],
        "signals": [
            "7f4e6470-80cd-4726-9ffb-ed7147a579e3",
        ]
    },
    {
        "title": "TCS ties up with Anthropic for AI adoption across enterprise",
        "vertical": "tech",
        "category": "technology",
        "urgency": "same_day",
        "diaspora": 90,
        "significance": 80,
        "source_avail": 85,
        "keywords": ["TCS", "Anthropic", "AI", "enterprise", "adoption", "Claude", "Indian IT"],
        "signals": [
            "712f3e75-e75f-40e3-8f2f-a197487d24e6",
        ]
    },
    {
        "title": "Real Madrid announce Jose Mourinho as manager for 2026/27 season",
        "vertical": "sports",
        "category": "sports",
        "urgency": "same_day",
        "diaspora": 55,
        "significance": 80,
        "source_avail": 90,
        "keywords": ["Mourinho", "Real Madrid", "manager", "football", "La Liga"],
        "signals": [
            "1f42c266-a7c3-420a-b4df-bd78dadcf555",
        ]
    },
    {
        "title": "Indian comedians spark national debate — Pranit More, Samay Raina controversy",
        "vertical": "entertainment",
        "category": "entertainment",
        "urgency": "same_day",
        "diaspora": 80,
        "significance": 65,
        "source_avail": 75,
        "keywords": ["comedians", "Pranit More", "Samay Raina", "controversy", "standup", "cancel culture"],
        "signals": [
            "5477ff95-af9d-4612-94c6-c59778db704e",
        ]
    },
    {
        "title": "Riva Arora on casting couch in Bollywood, reveals safe environment on Uri set",
        "vertical": "entertainment",
        "category": "entertainment",
        "urgency": "same_day",
        "diaspora": 70,
        "significance": 60,
        "source_avail": 75,
        "keywords": ["Riva Arora", "casting couch", "Bollywood", "Aditya Dhar", "Uri", "MeToo"],
        "signals": [
            "d703ecb2-43b6-4bf7-997d-fd2a8c53f426",
        ]
    },
    {
        "title": "Delhi moves to regulate coaching centres with new safety and fee norms",
        "vertical": "education",
        "category": "news",
        "urgency": "same_day",
        "diaspora": 70,
        "significance": 70,
        "source_avail": 80,
        "keywords": ["Delhi", "coaching centres", "regulation", "safety", "education", "Kota"],
        "signals": [
            "80770ede-61b4-4526-a0e1-27c6f8459a48",
        ]
    },
    {
        "title": "Delhi heat respite as rain arrives, Gurgaon unveils Rs 5 crore cool roofs plan",
        "vertical": "science",
        "category": "lifestyle-health",
        "urgency": "daily",
        "diaspora": 60,
        "significance": 60,
        "source_avail": 80,
        "keywords": ["Delhi", "heat", "rain", "cool roofs", "Gurgaon", "urban heat"],
        "signals": [
            "51382c4c-b034-420a-bf43-8ca641dbddbb",
            "8c4cc309-fc42-42e3-84cb-463f95ad0b35",
            "ffb55264-da1d-4028-8127-85766bdff47b",
        ]
    },
    {
        "title": "CBI secures extradition of two fugitives from Georgia and Thailand",
        "vertical": "politics",
        "category": "news",
        "urgency": "same_day",
        "diaspora": 65,
        "significance": 65,
        "source_avail": 75,
        "keywords": ["CBI", "extradition", "fugitives", "Georgia", "Thailand", "law enforcement"],
        "signals": [
            "8f95abfc-0a86-463a-80f0-64a968b8e24a",
        ]
    },
    {
        "title": "Air India crash survivor recalls emergency call that saved his life",
        "vertical": "politics",
        "category": "news",
        "urgency": "same_day",
        "diaspora": 80,
        "significance": 75,
        "source_avail": 80,
        "keywords": ["Air India", "crash", "survivor", "Arunachal Pradesh", "aviation safety"],
        "signals": [
            "ae163521-feb9-4068-95e1-c35f3b5e8170",
        ]
    },
    {
        "title": "Omar Abdullah meets PM Modi, seeks early J&K statehood restoration",
        "vertical": "politics",
        "category": "news",
        "urgency": "same_day",
        "diaspora": 70,
        "significance": 75,
        "source_avail": 85,
        "keywords": ["Omar Abdullah", "PM Modi", "J&K", "statehood", "Article 370"],
        "signals": [
            "337347b4-da4b-47e2-8b50-99000d5375d4",
        ]
    },
    {
        "title": "Five budget flight round-trips under Rs 20,000 from Delhi",
        "vertical": "diaspora",
        "category": "travel",
        "urgency": "daily",
        "diaspora": 75,
        "significance": 55,
        "source_avail": 70,
        "keywords": ["budget flights", "Delhi", "travel deals", "airlines", "cheap flights"],
        "signals": [
            "b119510f-399a-417e-8304-ae21452f737e",
        ]
    },
    {
        "title": "Baikunth Nath Bhutia: India must follow Uzbekistan football model, not Europe",
        "vertical": "sports",
        "category": "sports",
        "urgency": "daily",
        "diaspora": 65,
        "significance": 60,
        "source_avail": 70,
        "keywords": ["Bhutia", "India football", "Uzbekistan", "development model", "FIFA"],
        "signals": [
            "51e31286-3c71-4908-a55c-77d5395ef2f4",
        ]
    },
    {
        "title": "Delhi crime wave: daring Rs 1.5 crore heist, gym firing, Lawrence gang claims",
        "vertical": "politics",
        "category": "news",
        "urgency": "same_day",
        "diaspora": 55,
        "significance": 65,
        "source_avail": 80,
        "keywords": ["Delhi", "crime", "heist", "Lawrence Bishnoi", "gym firing", "robbery"],
        "signals": [
            "5e668915-f220-43cc-9e19-0f15abbd9b9b",
            "af5bf3e5-a16d-405b-bbaa-a04c25a81adc",
            "914d2a87-060d-4ddf-921a-800543a0f7dd",
        ]
    },
    {
        "title": "Simhastha Kumbh countdown begins with Dhwajstambh shilanyas at Ramkund",
        "vertical": "culture",
        "category": "lifestyle-health",
        "urgency": "daily",
        "diaspora": 70,
        "significance": 60,
        "source_avail": 70,
        "keywords": ["Simhastha", "Kumbh", "Ramkund", "Hindu pilgrimage", "Nashik"],
        "signals": [
            "4564bc7d-8d95-45e4-b900-35980b7ee7db",
        ]
    },
    {
        "title": "Sambhavna Seth brings newborn twins home after six days",
        "vertical": "entertainment",
        "category": "entertainment",
        "urgency": "daily",
        "diaspora": 55,
        "significance": 45,
        "source_avail": 70,
        "keywords": ["Sambhavna Seth", "twins", "Bollywood", "celebrity baby"],
        "signals": [
            "a473b21f-b809-402b-ae2b-dd0f639702d5",
        ]
    },
    {
        "title": "AAP wins Bathinda and Barnala mayoral elections in Punjab",
        "vertical": "politics",
        "category": "news",
        "urgency": "same_day",
        "diaspora": 65,
        "significance": 60,
        "source_avail": 75,
        "keywords": ["AAP", "Punjab", "mayors", "Bathinda", "Barnala", "elections"],
        "signals": [
            "42df2350-dd6a-4965-a627-7ff4a34af373",
            "a40005aa-580c-41be-af65-8cc4d3d96fac",
        ]
    },
    {
        "title": "Ranveer Singh–Don 3 row: producer Ashoke Pandit speaks out",
        "vertical": "entertainment",
        "category": "entertainment",
        "urgency": "daily",
        "diaspora": 60,
        "significance": 55,
        "source_avail": 70,
        "keywords": ["Ranveer Singh", "Don 3", "Ashoke Pandit", "Bollywood", "producer"],
        "signals": [
            "46489291-e137-4450-b680-5f56590fee44",
        ]
    },
    {
        "title": "R Madhavan's 33-year marriage: lessons on lasting relationships",
        "vertical": "entertainment",
        "category": "lifestyle-health",
        "urgency": "daily",
        "diaspora": 65,
        "significance": 50,
        "source_avail": 70,
        "keywords": ["R Madhavan", "marriage", "relationships", "Bollywood"],
        "signals": [
            "3d1068ee-34d0-48a9-b774-aa2f9171258c",
        ]
    },
    {
        "title": "BEST bus crash in Dadar: probe hits technical block over vehicle damage",
        "vertical": "politics",
        "category": "news",
        "urgency": "daily",
        "diaspora": 50,
        "significance": 55,
        "source_avail": 70,
        "keywords": ["BEST bus", "Dadar", "crash", "Mumbai", "transport"],
        "signals": [
            "ee6593d2-0a92-4525-b7d6-131d1cd33a02",
        ]
    },
    {
        "title": "India U-19 captain from Gwalior: the boy who holds a bat the right way",
        "vertical": "sports",
        "category": "sports",
        "urgency": "daily",
        "diaspora": 60,
        "significance": 55,
        "source_avail": 70,
        "keywords": ["India U-19", "captain", "Gwalior", "cricket", "youth"],
        "signals": [
            "e3956994-c712-4f9f-bc80-5a18907f5bcd",
        ]
    },
    {
        "title": "Marathwada water crisis: tankers cross 400 mark amid severe scarcity",
        "vertical": "politics",
        "category": "news",
        "urgency": "daily",
        "diaspora": 55,
        "significance": 60,
        "source_avail": 70,
        "keywords": ["Marathwada", "water crisis", "tankers", "scarcity", "drought"],
        "signals": [
            "8cc91a7d-317f-4338-97e6-4fdd634f0c83",
        ]
    },
    {
        "title": "Supreme Court to hear Meenakshi Natarajan plea against Rajya Sabha nomination rejection",
        "vertical": "politics",
        "category": "news",
        "urgency": "same_day",
        "diaspora": 55,
        "significance": 65,
        "source_avail": 80,
        "keywords": ["Supreme Court", "Natarajan", "Rajya Sabha", "Congress"],
        "signals": [
            "402e84a2-e09c-4051-b64c-dfe9e5c301de",
        ]
    },
    {
        "title": "Delhi government names Hindi literary awards after freedom fighters",
        "vertical": "culture",
        "category": "news",
        "urgency": "daily",
        "diaspora": 50,
        "significance": 45,
        "source_avail": 65,
        "keywords": ["Delhi", "Hindi", "literary awards", "freedom fighters", "nationalism"],
        "signals": [
            "a27addb9-9ec7-496e-b498-33c8e0feea03",
        ]
    },
    {
        "title": "FDA cracks down on adulteration and gutkha trade in Marathwada",
        "vertical": "politics",
        "category": "lifestyle-health",
        "urgency": "daily",
        "diaspora": 55,
        "significance": 55,
        "source_avail": 65,
        "keywords": ["FDA", "adulteration", "gutkha", "Marathwada", "food safety"],
        "signals": [
            "8021c956-ea77-41fb-baea-c93e04f4e563",
        ]
    },
    {
        "title": "Sachin Pilot says Gehlot 'same affection as for his son' after 'accept mistake' remarks",
        "vertical": "politics",
        "category": "news",
        "urgency": "daily",
        "diaspora": 55,
        "significance": 55,
        "source_avail": 75,
        "keywords": ["Sachin Pilot", "Gehlot", "Congress", "Rajasthan", "politics"],
        "signals": [
            "fa76ec5a-4aa2-4954-9c55-f4e8ebdbfa50",
        ]
    },
    {
        "title": "Heart of the Beast trailer: Brad Pitt's new survival film",
        "vertical": "entertainment",
        "category": "entertainment",
        "urgency": "daily",
        "diaspora": 45,
        "significance": 55,
        "source_avail": 75,
        "keywords": ["Brad Pitt", "Heart of the Beast", "trailer", "Hollywood"],
        "signals": [
            "a75b017f-919c-45e9-bcd2-03a89639f953",
        ]
    },
    {
        "title": "Juhu high-rise fire: eight rescued including four senior citizens",
        "vertical": "politics",
        "category": "news",
        "urgency": "daily",
        "diaspora": 50,
        "significance": 50,
        "source_avail": 70,
        "keywords": ["Juhu", "fire", "high-rise", "Mumbai", "rescue"],
        "signals": [
            "221e79b0-b5f3-4825-bcd9-befc964296ef",
        ]
    },
    {
        "title": "Bhagyashree on turning down Bollywood's biggest offers after Yash Chopra's scolding",
        "vertical": "entertainment",
        "category": "entertainment",
        "urgency": "daily",
        "diaspora": 60,
        "significance": 45,
        "source_avail": 70,
        "keywords": ["Bhagyashree", "Yash Chopra", "Bollywood", "Maine Pyar Kiya"],
        "signals": [
            "eaeab8ff-1495-433a-8a43-59fa477f26fe",
        ]
    },
    {
        "title": "Gujarat HC questions government over colour-blind forest guard's sacking",
        "vertical": "politics",
        "category": "news",
        "urgency": "daily",
        "diaspora": 55,
        "significance": 55,
        "source_avail": 70,
        "keywords": ["Gujarat", "high court", "colour blindness", "disability", "discrimination"],
        "signals": [
            "9134cbfb-98b2-430c-a3a4-64d95fecbd47",
        ]
    },
    {
        "title": "Pawan Kalyan's PKCW confirms OG2 sequel is happening",
        "vertical": "entertainment",
        "category": "entertainment",
        "urgency": "daily",
        "diaspora": 55,
        "significance": 50,
        "source_avail": 70,
        "keywords": ["Pawan Kalyan", "OG2", "Telugu", "sequel"],
        "signals": [
            "47b0d1c5-9ec6-4b11-a46b-238acdefd9ec",
        ]
    },
    {
        "title": "Nirav Modi bank fraud case: Mumbai court allows CBI to transfer Rs 322 crore case",
        "vertical": "economy",
        "category": "news",
        "urgency": "daily",
        "diaspora": 65,
        "significance": 65,
        "source_avail": 75,
        "keywords": ["Nirav Modi", "bank fraud", "CBI", "Mumbai court", "PNB"],
        "signals": [
            "4a737583-47a7-44c7-b192-86fd1a2be8b3",
        ]
    },
    {
        "title": "Bijwasan rail project gets nod to fell 1,254 trees in Delhi after fine",
        "vertical": "politics",
        "category": "news",
        "urgency": "daily",
        "diaspora": 45,
        "significance": 50,
        "source_avail": 65,
        "keywords": ["Delhi", "trees", "rail project", "Bijwasan", "environment"],
        "signals": [
            "cd6b1e6a-34ef-49c7-afeb-efa8f2df9449",
        ]
    },
    {
        "title": "MCD to improve parking payments system to curb misuse in Delhi",
        "vertical": "politics",
        "category": "news",
        "urgency": "daily",
        "diaspora": 40,
        "significance": 40,
        "source_avail": 60,
        "keywords": ["MCD", "parking", "Delhi", "payments"],
        "signals": [
            "0adc4680-05c8-4275-89d1-2c37f0e3f388",
        ]
    },
    {
        "title": "ARUNACHAL: APFRA law 'for all, not against any religion', says BJP MP",
        "vertical": "politics",
        "category": "news",
        "urgency": "daily",
        "diaspora": 50,
        "significance": 50,
        "source_avail": 65,
        "keywords": ["APFRA", "Arunachal Pradesh", "conversion", "BJP", "religion"],
        "signals": [
            "dfd91427-0395-4e72-a62d-2e82c97f2cdc",
        ]
    },
]

# All signal IDs from the 80 unprocessed
all_signal_ids = [
    "1f42c266-a7c3-420a-b4df-bd78dadcf555",
    "5477ff95-af9d-4612-94c6-c59778db704e",
    "4564bc7d-8d95-45e4-b900-35980b7ee7db",
    "1348fada-1684-4b22-9f43-007fc7b59969",
    "8cc91a7d-317f-4338-97e6-4fdd634f0c83",
    "d703ecb2-43b6-4bf7-997d-fd2a8c53f426",
    "0a4ef0b1-67be-40d3-9978-6d98591a9111",
    "51382c4c-b034-420a-bf43-8ca641dbddbb",
    "cd6b1e6a-34ef-49c7-afeb-efa8f2df9449",
    "a27addb9-9ec7-496e-b498-33c8e0feea03",
    "f3afaa3f-222f-401e-8029-e869058d3072",
    "78138f89-9d9f-4d1e-9a4f-72811b8a2522",
    "80770ede-61b4-4526-a0e1-27c6f8459a48",
    "ca857f7f-7d95-48f1-913e-47e12e91cc1d",
    "8021c956-ea77-41fb-baea-c93e04f4e563",
    "8c4cc309-fc42-42e3-84cb-463f95ad0b35",
    "8f95abfc-0a86-463a-80f0-64a968b8e24a",
    "00f7ecff-5175-44fd-b08c-a09f94befada",
    "0adc4680-05c8-4275-89d1-2c37f0e3f388",
    "90230342-c623-4d26-b3b1-6b4d2ba8358b",
    "dfd91427-0395-4e72-a62d-2e82c97f2cdc",
    "c90522f3-6edc-46ea-be9b-03bb21a686f1",
    "d33f715f-7ebc-4ce0-80eb-12ea6f19650a",
    "7c19545d-c055-43ad-b55e-8ed56224d1f8",
    "e6c0ae43-0968-4e65-b0d9-5825d89de84d",
    "47ad8f8b-9a97-4d8c-ad1a-0fd600ae8c96",
    "f6042f47-52f4-4330-a4df-1902bf372d58",
    "a73685c5-38a1-45a8-987e-723f6584b0c6",
    "a473b21f-b809-402b-ae2b-dd0f639702d5",
    "51e31286-3c71-4908-a55c-77d5395ef2f4",
    "d9f3eed7-1d5a-4579-9d11-8d3435c741f9",
    "a0a2c857-e8bf-4384-84f3-8e96eb86cc4a",
    "3b5825c1-097d-49f1-8a0f-fbdff138ddd4",
    "f898045d-4f48-41d8-9532-44a080b8de3c",
    "4d6d7a89-c40e-40c5-afab-0b7a734f5dfa",
    "af5bf3e5-a16d-405b-bbaa-a04c25a81adc",
    "671f696f-0202-4982-b781-fff2d541ba65",
    "65b2e008-cf8c-4cc0-9064-df5c31fd747f",
    "5e668915-f220-43cc-9e19-0f15abbd9b9b",
    "914d2a87-060d-4ddf-921a-800543a0f7dd",
    "54c97e1d-8e19-49e3-8e4d-0de27a081698",
    "c41f12df-a4f9-44ec-a854-892d74c52673",
    "7471d983-1125-4680-8e07-6f81f69a8e3d",
    "93ff818a-300e-41ae-a16d-7cd6fa5f2ba1",
    "19a51ccd-7a55-4139-9d34-bbfd601afec6",
    "af01f0ca-e378-4e4b-accb-6b1f56f9ef48",
    "d95fde9b-9e04-4a00-958c-6721eca41715",
    "aebb8d07-bc87-43d8-befc-7f38f0fc8a59",
    "32efab5b-5a36-4cb4-9077-4a62162f1296",
    "4a737583-47a7-44c7-b192-86fd1a2be8b3",
    "bee22476-4a30-4066-a6aa-239dbc23ed47",
    "7f4e6470-80cd-4726-9ffb-ed7147a579e3",
    "b119510f-399a-417e-8304-ae21452f737e",
    "f4e26c4d-08ba-40f4-ab38-d48914fd366c",
    "46489291-e137-4450-b680-5f56590fee44",
    "ee6593d2-0a92-4525-b7d6-131d1cd33a02",
    "ce68cb39-d61a-4294-b012-efdd179e9367",
    "acd7791d-5468-4433-a4f6-6403a5a0dc6e",
    "ffb55264-da1d-4028-8127-85766bdff47b",
    "ae163521-feb9-4068-95e1-c35f3b5e8170",
    "fa76ec5a-4aa2-4954-9c55-f4e8ebdbfa50",
    "a75b017f-919c-45e9-bcd2-03a89639f953",
    "221e79b0-b5f3-4825-bcd9-befc964296ef",
    "eaeab8ff-1495-433a-8a43-59fa477f26fe",
    "42df2350-dd6a-4965-a627-7ff4a34af373",
    "3d1068ee-34d0-48a9-b774-aa2f9171258c",
    "195be20b-c556-41dc-8a49-8b202357cc99",
    "712f3e75-e75f-40e3-8f2f-a197487d24e6",
    "755f9ea8-7594-4fe6-9f6c-b59c8a40e2aa",
    "58d6d6ba-00c4-4c1b-a5a0-59f77322c1f2",
    "9134cbfb-98b2-430c-a3a4-64d95fecbd47",
    "93254228-b11e-43d5-9fe6-105e57142aa6",
    "a40005aa-580c-41be-af65-8cc4d3d96fac",
    "337347b4-da4b-47e2-8b50-99000d5375d4",
    "a9fc60db-0ae3-40fb-aed9-e599b8fea931",
    "5e10a808-7d82-4615-904a-8f8891fbc225",
    "7324bfe4-e646-4c66-976a-a1025293fe0b",
    "402e84a2-e09c-4051-b64c-dfe9e5c301de",
    "47b0d1c5-9ec6-4b11-a46b-238acdefd9ec",
    "e3956994-c712-4f9f-bc80-5a18907f5bcd",
]

print(f"═══ Stage 2: Clustering {len(all_signal_ids)} signals into {len(clusters)} topics ═══")

# Insert topics and link signals
topics_created = 0
for i, cluster in enumerate(clusters):
    topic_data = json.dumps({
        "canonical_title": cluster["title"],
        "vertical": cluster["vertical"],
        "category": cluster["category"],
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
        score = result.get("score_total", "?")
        print(f"  [{i+1}] ✓ {cluster['title'][:60]}... → score:{score}")
        topics_created += 1

        # Link signals to topic
        signal_ids_str = ",".join(cluster["signals"])
        run_db("link-signals", topic_id, signal_ids_str)
    else:
        print(f"  [{i+1}] ✗ Failed: {result}")

# Mark ALL 80 signals as processed
print(f"\n  Marking {len(all_signal_ids)} signals as processed...")
# Do in batches of 20
for batch_start in range(0, len(all_signal_ids), 20):
    batch = all_signal_ids[batch_start:batch_start+20]
    result = run_db("mark-signals-processed", ",".join(batch))
    if result and result.get("ok"):
        print(f"    ✓ Batch {batch_start//20 + 1}: {result.get('marked', 0)} marked")
    else:
        print(f"    ✗ Batch {batch_start//20 + 1} failed: {result}")

print(f"\n═══ Complete: {topics_created} topics created, {len(all_signal_ids)} signals processed ═══")
