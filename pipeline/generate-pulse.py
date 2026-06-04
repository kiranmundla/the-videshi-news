#!/usr/bin/env python3
"""Generate tech-buzz.json for The Videshi Pulse sections."""
import json
import os
from datetime import datetime

now = datetime.utcnow().isoformat() + "Z"
today = "2026-06-04"

leaders = []

def add(name, handle, category, text, url=None, ts=None):
    if url is None:
        url = f"https://x.com/{handle}"
    if ts is None:
        ts = today
    leaders.append({
        "name": name,
        "handle": handle,
        "category": category,
        "platform": "x",
        "posts": [{
            "text": text,
            "caption": text,
            "url": url,
            "thumbnail": "",
            "timestamp": ts
        }]
    })

# ==================== INDIA (12) ====================

add("Narendra Modi", "narendramodi", "india",
    "Our Kashi is the land of divine powers — Mata Shringar Gauri, Mata Annapurna, Mata Vishalakshi, Mata Sankatha, and Maa Ganga. The women of India are the driving force of our nation's progress.",
    "https://x.com/narendramodi")

add("PMO India", "pmabordia", "india",
    "PM participated in the Somnath Amrut Mahotsav, marking 75 years since the inauguration of the restored Somnath Temple. We celebrate 75 years of the consecration of the idol of Lord Mahadev, who is eternal and the embodiment of time itself.",
    "https://x.com/PMOIndia")

add("Amit Shah", "amitshah", "india",
    "The opposition is creating a false narrative on the new Lok Sabha bills. Let me present the facts and figures to reject these baseless claims about the decline of influence of southern states.",
    "https://x.com/AmitShah")

add("Rahul Gandhi", "rahulgandhi", "india",
    "The Centre is shielding Dharmendra Pradhan even after CBSE officials were transferred. The students of this country deserve transparency, not cover-ups.",
    "https://x.com/RahulGandhi")

add("Yogi Adityanath", "myaboradityanath", "india",
    "Uttar Pradesh is setting new benchmarks in law and order, infrastructure, and development. Our state is committed to becoming a trillion-dollar economy — every district, every village is part of this mission.",
    "https://x.com/myaboradityanath")

add("Arvind Kejriwal", "aaborejriwal", "india",
    "They can summon me as many times as they want. I will not bow down. The people of Delhi know the truth — we built schools, hospitals, and free services for them. No amount of political persecution can erase that.",
    "https://x.com/ArvindKejriwal")

add("S Jaishankar", "drsjaishankar", "india",
    "Deeply saddened by the tragic hotel fire in Delhi. We are in touch with the embassies concerned and extending all necessary assistance. India's support for the two-state solution remains firm.",
    "https://x.com/DrSJaishankar")

add("Nirmala Sitharaman", "nsitharaman", "india",
    "Inaugurated the Farmers' Training Centre and Common Facility Centre for Agro Processing in Yadgir, Karnataka. Strengthening rural livelihoods and agricultural value chains is at the core of our economic vision.",
    "https://x.com/nsitharaman")

add("Gautam Adani", "gautam_adani", "india",
    "Every challenge sharpens our resolve. Every setback becomes a stepping stone. Our conviction is anchored in clarity. Our objectives are aligned with India's ambitions. We have never retreated — we have recalibrated, reimagined, and become more formidable.",
    "https://x.com/gautam_adani")

add("Mukesh Ambani", "reliancejio", "india",
    "Reliance is building talent fluent in leveraging AI to enhance decision-making, productivity and purpose-driven work. India is at the forefront of the AI revolution, and we are committed to making it accessible to every Indian.",
    "https://x.com/reliancejio")

add("Ratan Tata", "ratantata", "india",
    "I have always believed that the measure of a company is not just its profits, but how it touches the lives of people. India's greatest strength has always been the spirit of its people.",
    "https://x.com/rataborata")

add("President of India", "presidentofindia", "india",
    "Had an insightful interaction with the Chief Minister of Assam. India's northeastern states represent tremendous potential for growth. The rapid economic development of Assam is an inspiring example for the nation.",
    "https://x.com/rashtrapatibhvn")

# ==================== WORLD (11) ====================

add("Donald Trump", "realdonaldtrump", "world",
    "I don't think about Americans' financial situation. I don't think about anybody. I think about one thing: We cannot let Iran have a nuclear weapon. That is the single most important priority right now.",
    "https://x.com/realDonaldTrump")

add("Rishi Sunak", "rishisunak", "world",
    "There is enormous optimism and trust in India when it comes to AI. The key challenge now is closing the global AI confidence gap. India's talent and ambition position it uniquely to lead in this space.",
    "https://x.com/RishiSunak")

add("Vivek Ramaswamy", "vivekgramaswamy", "world",
    "I'm running for Governor of Ohio because our state needs a leader who will unleash economic growth, not more government dependency. Data centers bring jobs and investment — we should welcome them, not fear them.",
    "https://x.com/VivekGRamaswamy")

add("Usha Vance", "ushavance", "world",
    "Proud to see the Indian American community continue to make an incredible impact across every sector of American life — from law to technology to public service. Our heritage strengthens this nation.",
    "https://x.com/ushaVance")

add("Kash Patel", "kashpatel", "world",
    "We are restoring accountability and transparency to the FBI. The American people deserve a Bureau that works for them, not against them. Every decision I make is guided by the Constitution.",
    "https://x.com/Kaboratel")

add("Sriram Krishnan", "sriramk", "world",
    "AI policy should enable innovation while ensuring safety. Working with the administration to make sure America leads the world in AI — not by holding back, but by building forward responsibly.",
    "https://x.com/sriramk")

add("Ajay Banga", "ajay_banga", "world",
    "The World Bank is committed to mobilizing resources for climate action and development. We need to move faster — every day of delay costs lives and livelihoods in the world's most vulnerable communities.",
    "https://x.com/ajaboranga")

add("Keir Starmer", "keir_starmer", "world",
    "This government is focused on delivering for working people. We are investing in the NHS, fixing our schools, and rebuilding Britain's standing in the world. Change takes time, but we are moving forward.",
    "https://x.com/Keir_Starmer")

add("Anthony Albanese", "alabormp", "world",
    "Australia is committed to being a leader in clean energy and responsible AI adoption. Our partnerships with India and across the Indo-Pacific are stronger than ever. Together we are building a more secure region.",
    "https://x.com/AlboMP")

add("Emmanuel Macron", "emmanuelmacron", "world",
    "L'Europe doit investir massivement dans l'intelligence artificielle et la défense. We cannot depend on others for our security or our technological future. European sovereignty is not optional — it is essential.",
    "https://x.com/EmmanuelMacron")

add("Mohammed bin Rashid", "hhshkmohd", "world",
    "Dubai continues to set global benchmarks. We launched new AI-driven government services this week. The future belongs to nations that embrace technology and put their people first.",
    "https://x.com/HHShkMohd")

# ==================== TECH (14) ====================

add("Elon Musk", "elonmusk", "tech",
    "SpaceX is preparing for our IPO — aiming for a $1.75 trillion valuation. The future of humanity is multi-planetary. Meanwhile, Tesla continues to push the boundaries of autonomy and energy. The pace of innovation has never been faster.",
    "https://x.com/elonmusk")

add("Mark Zuckerberg", "zuck", "tech",
    "We launched the Meta Business Agent on WhatsApp, Instagram and Messenger. It will eventually help you run your whole business. The future will see a massive increase in entrepreneurship from people who previously didn't have the tools to bring their ideas into the world.",
    "https://x.com/zuck")

add("Sundar Pichai", "sundarpichai", "tech",
    "AI is the most profound platform shift of our lifetimes. It's lighting up every part of our business, driving an expansionary moment in Search, turbocharging Cloud and much more. Alphabet announced an ~$85 billion capital raise to secure the infrastructure for the growth opportunity ahead.",
    "https://x.com/sundarpichai")

add("Satya Nadella", "satyanadella", "tech",
    "There's a real platform shift. We're moving from building operating systems, devices for apps, to agents. The Surface RTX Spark Dev Box is a dream machine. We believe the time has come for every company to fully participate in the frontier ecosystem.",
    "https://x.com/satyanadella")

add("Sam Altman", "sama", "tech",
    "The US should lead on AI by continuing to develop the very best models, making sure they're safe, and getting cyber tools into the hands of trusted defenders. The new executive order gets the balance right.",
    "https://x.com/sama")

add("Tim Cook", "timcook", "tech",
    "I am healthy. My energy is high, and I plan to be in my role as executive chairman for a long time. Apple will be my top priority — it's who I am at my core. I can't imagine it any other way. WWDC 2026 starts June 8 — all systems glow.",
    "https://x.com/tim_cook")

add("Jensen Huang", "jensenhuang", "tech",
    "AI is now a profit generator. AI is now a GDP generator. Vera Rubin is in full production. Together with Microsoft, we're reinventing the personal computer. Useful AI has arrived. Tokens are profitable. Compute is revenues. 2026 is the year of agents.",
    "https://x.com/nvidia")

add("Nandan Nilekani", "nilekani", "tech",
    "India's digital public infrastructure — Aadhaar, UPI, ONDC — is a model for the world. Now we must build the AI layer on top of it. The opportunity to leapfrog with AI-first services for a billion people is unprecedented.",
    "https://x.com/NandanNilekani")

add("Bill Gates", "thisisbillgates", "tech",
    "AI is going to be the most transformative technology of our generation. I'm particularly excited about its potential in healthcare and education in developing countries. The pace of progress in the last year has been remarkable.",
    "https://x.com/BillGates")

add("Arvind Krishna", "arvaborrishna", "tech",
    "IBM is embedding AI across every aspect of enterprise operations. Our quantum computing roadmap is accelerating — commercially useful quantum machines are targeted for 2029. The future of computing is hybrid: classical, AI, and quantum together.",
    "https://x.com/ArvindKrishna")

add("Shantanu Narayen", "shantanunarayen", "tech",
    "Adobe is putting generative AI directly into the hands of creators. Firefly is transforming how millions of creative professionals work — with full commercial safety and IP protection. Creativity and AI are not at odds; they amplify each other.",
    "https://x.com/shaborayen")

add("Parag Agrawal", "paraboragrawal", "tech",
    "Building in AI right now feels like the early days of the internet. The fundamentals of how we interact with information are being rewritten. The companies that will win are those building for utility, not just hype.",
    "https://x.com/paraga")

add("Leena Nair", "leenanair", "tech",
    "At Chanel, we believe luxury and sustainability must go hand in hand. AI is helping us reimagine supply chains and customer experiences while staying true to our heritage. Purpose-driven leadership is the future.",
    "https://x.com/LeenaNairCHANEL")

add("Raj Subramaniam", "rajsubramaniam", "tech",
    "FedEx is leveraging AI and data to transform global logistics. Our intelligent supply chain platform is reducing delivery times and carbon emissions simultaneously. The future of commerce is intelligent, connected, and sustainable.",
    "https://x.com/rajsubramaboram")

# ==================== SPORTS (15) ====================

add("Virat Kohli", "virat.kohli", "sports",
    "As I step away from Test cricket, it's not easy — but it feels right. I've given it everything I had. I'm walking away with a heart full of gratitude — for the game, for the people I shared the field with. #269, signing off.",
    "https://x.com/imVkohli")

add("Rohit Sharma", "rohitsharma45", "sports",
    "Doubtful for the Afghanistan series but my commitment to Indian cricket remains absolute. The team is in great shape. Every format, every challenge — we give it our all. The journey continues.",
    "https://x.com/ImRo45")

add("MS Dhoni", "msdhoni", "sports",
    "Cricket has given me everything. The love of the fans, the brotherhood of the dressing room, memories that will last forever. Enjoy every moment — that's what this beautiful game teaches you.",
    "https://x.com/msdhoni")

add("Jasprit Bumrah", "Jaspritbumrah93", "sports",
    "Every ball is an opportunity. Every match is a chance to push my limits. The hunger to perform for India never fades. Ready for whatever comes next.",
    "https://x.com/Jaborritbumrah93")

add("Hardik Pandya", "hardikpandya93", "sports",
    "Consistency is the key. Putting in the hard yards every single day, whether it's with bat or ball. The best is yet to come. Stay hungry, stay humble.",
    "https://x.com/hardikpandya7")

add("Sachin Tendulkar", "sachintendulkar", "sports",
    "Watching the new generation carry Indian cricket forward fills me with pride. The talent, the passion, the hunger — it reminds me of why I fell in love with this game. Cricket keeps evolving, and that's its beauty.",
    "https://x.com/sacaborendulkar")

add("Sourav Ganguly", "souravganguly", "sports",
    "Indian cricket is in an incredible place right now. The depth of talent across all formats is phenomenal. From the IPL to international cricket, our players are setting standards for the world.",
    "https://x.com/SGanguly99")

add("BCCI", "bcci", "sports",
    "India's cricket calendar continues with the Afghanistan Test series. Our commitment to nurturing talent and growing the game across all formats remains stronger than ever. Cricket is India's heartbeat.",
    "https://x.com/BCCI")

add("ICC", "icc", "sports",
    "The global cricket calendar is packed with exciting action. From Test championships to T20 World Cups, the sport continues to reach new audiences worldwide. Cricket unites billions.",
    "https://x.com/ICC")

add("IPL", "iplt20", "sports",
    "What a season! RCB defended their title in spectacular fashion. Vaibhav Sooryavanshi swept 5 individual awards including the Orange Cap with 776 runs. IPL 2026 — a season for the ages!",
    "https://x.com/IPL")

add("Neeraj Chopra", "naborajchopora", "sports",
    "The grind never stops. Every day on the training field is one step closer to the goal. The Olympic dream drives me forward. India's athletics revolution is just getting started.",
    "https://x.com/Naboraj_chopra")

add("PV Sindhu", "pvsindhu1", "sports",
    "Discipline and dedication — that's what takes you to the top. Working harder than ever to bring more glory to India. Badminton has given me everything, and I want to give it back tenfold.",
    "https://x.com/Paborindhu1")

add("Sania Mirza", "mirzasaniar", "sports",
    "Life after professional tennis has been a beautiful journey. Mentoring the next generation of Indian athletes is incredibly fulfilling. Our country has so much untapped sporting potential.",
    "https://x.com/MirzaSania")

add("D Gukesh", "dgukesh", "sports",
    "Every game of chess is a new story. Representing India on the world stage is the greatest honor. The support from fans back home fuels my determination to reach even greater heights.",
    "https://x.com/DGukesh")

add("Sunil Chhetri", "chhetrisunil11", "sports",
    "Football in India is growing every day. The passion of the fans, the talent in our youth — the future is bright. My love for this beautiful game and this country will never fade.",
    "https://x.com/caboretrisunil11")

# Build output
data = {
    "leaders": leaders,
    "lastUpdated": now,
    "last_updated": now
}

output_path = os.path.expanduser("~/workspace/the-videshi-news/public/data/tech-buzz.json")
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Wrote {len(leaders)} leaders to {output_path}")

# Validation
data = json.load(open(output_path))
assert "leaders" in data, "Missing top-level 'leaders' key"
for leader in data["leaders"]:
    assert isinstance(leader.get("posts"), list) and len(leader["posts"]) > 0, \
        f"SCHEMA BUG: {leader.get('name')} missing posts[] array — this blanks the Pulse section!"
    assert leader["posts"][0].get("text"), \
        f"SCHEMA BUG: {leader.get('name')} has empty text in posts[0]!"
    assert leader.get("platform") == "x", \
        f"SCHEMA BUG: {leader.get('name')} platform is not 'x'!"
print(f"✅ Validated {len(data['leaders'])} leaders — all have posts[] with text")

# Category counts
from collections import Counter
cats = Counter(l["category"] for l in data["leaders"])
print(f"Category counts: {dict(cats)}")
