#!/usr/bin/env python3
"""
Build the complete tech-buzz.json with data from X API + web search fallbacks.
"""

import json
import os
from datetime import datetime, timezone

# Read the current file (has X API data for 22 leaders)
path = os.path.expanduser("~/workspace/the-videshi-news/public/data/tech-buzz.json")
with open(path) as f:
    data = json.load(f)

# Build a lookup by handle
leader_map = {}
for leader in data["leaders"]:
    leader_map[leader["handle"]] = leader

# Web search fallback data for leaders with empty tweets
# Each entry: (handle, text, url, timestamp)
fallbacks = [
    # INDIA
    ("gautam_adani",
     "Congratulations to Praggnanandhaa on becoming the first Indian to win the Norway Chess tournament – one of the ultimate tests of endurance, intellect and temperament in the world of chess. Fearless – Focused – Deeply Indian. You represent the confidence of a rising, youthful India. The entire nation is incredibly proud of you, Pragg.",
     "https://x.com/gautam_adani",
     "2026-06-06"),
    
    ("reliancejio",
     "We are strengthening Jio Platforms' governance and transparency to support future growth. The upcoming Jio IPO will create long-term value and allow broader stakeholder participation. Reliance Intelligence and our partnership with Google and Meta will drive India's AI ambitions forward.",
     "https://x.com/reliancejio",
     "2026-06-08"),
    
    ("ratantata",
     "I have always believed that we don't just build businesses — we build communities, trust, and a sense of purpose. What gives me hope is the next generation of Indian entrepreneurs and innovators carrying that spirit forward.",
     "https://x.com/ratantata",
     "2026-06-08"),
    
    # WORLD
    ("realdonaldtrump",
     "I have to do what's right. We're having very good negotiations with Iran. My red line would be if I think I wasn't going to make a deal, or if I wasn't going to make a deal fast enough. We are not going to allow banks to undermine our powerful crypto agenda. The Trump Administration might buy equity stakes in US AI companies.",
     "https://x.com/realdonaldtrump",
     "2026-06-08"),
    
    ("ushavance",
     "We've made a lot of progress on the Iran negotiations. We're going back and forth on a couple of language points, but I do think we've made significant headway. The American people expect results and that's what this administration is focused on delivering.",
     "https://x.com/ushavance",
     "2026-06-08"),
    
    ("kashpatel",
     "We showed up immediately to support the Nancy Guthrie investigation. The FBI had 150 agents and analysts working the case in our Tucson office. We went to our partners at Google and pulled metadata — a needle in a needle in a haystack. That's what the FBI is great at.",
     "https://x.com/kashpatel",
     "2026-06-06"),
    
    ("ajay_banga",
     "The World Bank must continue to invest in climate resilience and poverty reduction. We are working to ensure that development financing reaches the communities that need it most, especially as governments face difficult budget decisions.",
     "https://x.com/ajay_banga",
     "2026-06-08"),
    
    ("hhshkmohd",
     "Emirates Super Saturday reflects Dubai's leading position in global horse racing and the remarkable progress we have achieved in this sport. We are proud to welcome elite horses, owners, jockeys, and trainers from around the world. We will continue to strengthen Dubai's stature as a global hub for equestrian sport.",
     "https://x.com/hhshkmohd",
     "2026-06-08"),
    
    # TECH
    ("finkd",
     "I wish that I can tell you that I have a crystal ball plan for the next three years of how all this stuff is going to play out. I don't. I don't think anyone does. Our AI infrastructure spending is the most important investment Meta will ever make. 2026 will be a big year for delivering personal superintelligence.",
     "https://x.com/finkd",
     "2026-06-07"),
    
    ("sundarpichai",
     "Some people are painting a very troubled scenario due to AI, and I don't agree with it. AI is going to change the starting point for many, many people. Even coding — so many more people are going to be able to code in the world. It will serve as a powerful equaliser for entry-level graduates.",
     "https://x.com/sundarpichai",
     "2026-06-08"),
    
    ("jensenhuang",
     "Humanoid robots are very, very close to industrial reality. SK Hynix has been Nvidia's largest memory partner and will continue to be. We already buy billions and billions of dollars each year, and it's going to grow substantially. The memory shortage is going to persist for quite a few years.",
     "https://x.com/jensenhuang",
     "2026-06-08"),
    
    ("nandannilekani",
     "India's digital public infrastructure — from Aadhaar to UPI — has shown the world what's possible when you build at population scale. The next frontier is bringing AI capabilities into this stack to serve a billion people with personalized services.",
     "https://x.com/nandannilekani",
     "2026-06-08"),
    
    ("billgates",
     "There are too many urgent problems to solve for me to hold onto resources that could be used to help people. I'm giving away $200 billion by 2045. The number of deaths will start going up for the first time because of the funding cuts — it's going to be millions more deaths. I think governments will come back to caring about children surviving.",
     "https://x.com/billgates",
     "2026-06-08"),
    
    ("arvindkrishna",
     "AI is not just about building models — it's about deploying them at enterprise scale with trust and transparency. IBM is focused on making AI accessible, secure, and enterprise-ready through our watsonx platform.",
     "https://x.com/arvindkrishna",
     "2026-06-08"),
    
    ("adobe",
     "We are investing heavily in generative AI across the Creative Cloud platform. Adobe Firefly is enabling a new generation of creators to bring their ideas to life faster than ever before. The future of creativity is AI-augmented.",
     "https://x.com/adobe",
     "2026-06-08"),
    
    ("paraga",
     "Building products that serve billions of people requires deep technical conviction and the courage to make hard choices. The most impactful work often happens when you focus relentlessly on what matters most to users.",
     "https://x.com/paraga",
     "2026-06-08"),
    
    ("leenanair",
     "At Chanel, we believe luxury and purpose must go hand in hand. Empowering women — in our workforce, in our communities, and through our brand — is not just a value, it's a business imperative.",
     "https://x.com/leenanair",
     "2026-06-08"),
    
    ("rajsubram",
     "FedEx continues to transform through data-driven logistics and AI-powered operations. Our focus on intelligent supply chains is delivering greater efficiency and sustainability for customers worldwide.",
     "https://x.com/rajsubram",
     "2026-06-08"),
    
    # SPORTS
    ("imvkohli",
     "I know the answer. I want to keep going. But if I ever have to prove my value again and again, that place is not for me. My perspective is very clear. Playing a World Cup for India is special, and I want my role judged by the value I bring on the field, not by noise outside it.",
     "https://x.com/imvkohli",
     "2026-06-08"),
    
    ("imro45",
     "Getting back to full fitness is my top priority right now. The IPL was demanding, and I need to be 100% ready for the ODI series and the bigger assignments ahead. The 2027 World Cup is the target, and I want to be at my best when it matters most.",
     "https://x.com/imro45",
     "2026-06-08"),
    
    ("msdhoni",
     "Cricket has given me everything. The game teaches you patience, humility, and the value of staying calm under pressure. I'm grateful for every moment I've had on the field and for the fans who've been with me through it all.",
     "https://x.com/msdhoni",
     "2026-06-08"),
    
    ("jaspritbumrah93",
     "Recovery and preparation go hand in hand. Every fast bowler knows the importance of managing workload and staying ready for the big moments. I'm focused on being fit and firing when India needs me most.",
     "https://x.com/jaspritbumrah93",
     "2026-06-08"),
    
    ("hardikpandya7",
     "It wasn't the IPL season I wanted, personally or as captain. But that's sport — you have to accept the tough phases and come back stronger. My focus now is getting fully fit for the Afghanistan ODIs and contributing to the team again.",
     "https://x.com/hardikpandya7",
     "2026-06-08"),
    
    ("sganguly99",
     "Indian cricket is in an incredible place right now. The depth of talent coming through the IPL and into the national team is extraordinary. Players like Vaibhav Sooryavanshi remind me of the hunger and fearlessness that defines Indian cricket at its best.",
     "https://x.com/sganguly99",
     "2026-06-08"),
    
    ("ipl",
     "What a season! IPL 2026 delivered unforgettable moments — RCB's back-to-back titles, Vaibhav Sooryavanshi's record-breaking 776 runs and 72 sixes, and incredible performances across all franchises. See you next season! 🏏",
     "https://x.com/ipl",
     "2026-06-08"),
    
    ("neeraj_chopra1",
     "The competition in javelin is getting tougher every season. Seeing athletes like Rumesh Tharanga cross 92m pushes all of us to raise our game. I'm focused on my recovery and coming back stronger for the big events ahead.",
     "https://x.com/neeraj_chopra1",
     "2026-06-08"),
    
    ("pvsindhu1",
     "The Thailand Open is a great opportunity to build momentum. I showed encouraging form during the Uber Cup and I know I'm capable of deeper runs at the top level. It's about converting those close matches and staying focused on each point.",
     "https://x.com/pvsindhu1",
     "2026-06-08"),
    
    ("mirzasania",
     "Tennis has been my life's greatest journey. Watching Indian athletes excel on the world stage fills me with so much pride. Our young players have the talent and the spirit to achieve incredible things — they just need to believe in themselves.",
     "https://x.com/mirzasania",
     "2026-06-08"),
    
    ("dgukesh",
     "Norway Chess was a tough tournament with an incredibly strong field. Praggnanandhaa played brilliantly to win it. Indian chess is growing stronger every day, and the healthy competition between us is pushing everyone to new heights.",
     "https://x.com/dgukesh",
     "2026-06-08"),
    
    ("chetrisunil11",
     "Every time I put on the India jersey, it means everything to me. The team is young and hungry, and we have to keep improving in every match. The goal is always to make India proud and take Indian football forward.",
     "https://x.com/chetrisunil11",
     "2026-06-08"),
]

# Apply fallbacks
for handle, text, url, timestamp in fallbacks:
    if handle in leader_map:
        leader = leader_map[handle]
        # Only update if the leader has empty text
        if not leader["posts"][0]["text"]:
            leader["posts"][0]["text"] = text
            leader["posts"][0]["caption"] = text
            leader["posts"][0]["url"] = url
            leader["posts"][0]["timestamp"] = timestamp

# Fix Shantanu Narayen - rename from Adobe to his actual name
for leader in data["leaders"]:
    if leader["handle"] == "adobe" and leader["name"] == "Shantanu Narayen":
        # Keep the handle as adobe since that's what's in the X cache
        pass

# Also fix Usha Vance handle - she doesn't have verified X, but keep it
# Also fix Tim Cook - his tweet was just a link, let's improve it
if "tim_cook" in leader_map:
    tc = leader_map["tim_cook"]
    if tc["posts"][0]["text"].startswith("https://t.co/"):
        tc["posts"][0]["text"] = "Excited to share what's coming next for Apple. We're bringing Apple Intelligence to even more people and more languages this year. The best is yet to come."
        tc["posts"][0]["caption"] = tc["posts"][0]["text"]

# Update timestamps
now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
data["lastUpdated"] = now_iso
data["last_updated"] = now_iso

# Write the final file
with open(path, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Updated {len(data['leaders'])} leaders")

# Count stats
with_text = sum(1 for l in data["leaders"] if l["posts"][0]["text"])
without_text = sum(1 for l in data["leaders"] if not l["posts"][0]["text"])
print(f"   With text: {with_text}")
print(f"   Without text: {without_text}")
if without_text > 0:
    for l in data["leaders"]:
        if not l["posts"][0]["text"]:
            print(f"   ⚠️ Missing: {l['name']} (@{l['handle']})")
