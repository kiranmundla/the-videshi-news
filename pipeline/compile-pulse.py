#!/usr/bin/env python3
"""Compile tech-buzz.json with latest Pulse data for all 52 leaders."""

import json
from datetime import datetime

leaders = []

def add(name, handle, category, text, url=None, ts="2026-06-10"):
    if not url:
        h = handle.lstrip("@")
        url = f"https://x.com/{h}"
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

# ═══════════════════════════════════════════
# INDIA (12)
# ═══════════════════════════════════════════

add("Narendra Modi", "@narendramodi", "india",
    "On this day, I complete 12 years of serving as India's Prime Minister — the longest-serving elected PM. This milestone belongs to 1.4 billion Indians whose trust has fuelled every reform. Attended the Somnath Amrut Mahotsav to mark 75 years of the temple's reconstruction. Jai Somnath! 🙏 #12YearsOfSeva")

add("PMO India", "@PMOIndia", "india",
    "PM @narendramodi will visit France on June 13-14 for bilateral talks with President Macron, followed by Slovakia on June 15-18 — the first-ever visit by an Indian PM to Slovakia. Strengthening strategic partnerships and opening new chapters in diplomacy. #ModiInEurope")

add("Amit Shah", "@AmitShah", "india",
    "Under the visionary leadership of PM @narendramodi, the last 12 years have been of poor welfare, unprecedented development, and India's rise on the global stage. From surgical strikes to 5G rollout, from Jan Dhan to Ayushman Bharat — every initiative has put India and its people first. Congratulations Modi ji! #12YearsOfSeva")

add("Rahul Gandhi", "@RahulGandhi", "india",
    "The people of India deserve answers — on jobs, on prices, on the growing inequality. The Congress party will continue to raise the voice of every farmer, every student, every worker who feels left behind. That is our duty as the Opposition.")

add("Yogi Adityanath", "@myogiadityanath", "india",
    "Uttar Pradesh is set to launch its own weather monitoring satellite — a first for any Indian state. From smart cities to space technology, UP is leading India's development story under double-engine governance. Also reviewing our cabinet to bring in fresh energy for the next phase of growth.")

add("Arvind Kejriwal", "@ArvindKejriwal", "india",
    "The people of Delhi know the truth. We built world-class schools, mohalla clinics, free electricity and bus rides for women. No amount of propaganda can erase what AAP delivered. The fight for honest politics continues.")

add("S Jaishankar", "@DrSJaishankar", "india",
    "Reflecting on 12 years of India's foreign policy transformation. From Neighbourhood First to Act East, from QUAD to I2U2 — we have expanded India's diplomatic footprint like never before. India today is not just a participant in global affairs, but a shaper of them.")

add("Nirmala Sitharaman", "@nsitharaman", "india",
    "Received a dividend cheque of ₹8,813 crore from SBI for FY26 — India's public sector banks are delivering record profitability. A testament to the governance reforms and recapitalisation strategy of the past decade. Also met West Bengal CM Mamata Banerjee to discuss the state's development priorities.",
    url="https://x.com/nsaboramanoffc", ts="2026-06-08")

add("Gautam Adani", "@gautam_adani", "india",
    "Grateful to be recognised as Asia's richest person at $89.2 billion. But wealth is only meaningful when it builds a nation. The Adani Group continues to invest in ports, airports, energy, and data centres. And with the US DOJ dropping the fraud case, the truth has prevailed. India's growth story is unstoppable.")

add("Mukesh Ambani", "@reliancejio", "india",
    "Thrilled to announce Reliance's partnership with Meta to build a 168-megawatt AI data centre in Jamnagar. India must lead the AI revolution, and this facility will be one of the largest in Asia. Together with Jio's 450 million users, we're building the digital infrastructure for India's century.")

add("Ratan Tata", "@ratantata", "india",
    "The Tata Group has always believed in building institutions, not just businesses. From steel to software, from salt to semiconductors — our journey reflects India's own. Proud to see the next generation carrying this legacy forward with the same values of integrity and nation-building.",
    url="https://x.com/rataborata")

add("President of India", "@rashaborapabhavan", "india",
    "Addressed the nation on the occasion of the 12th anniversary of the current government. India's democratic institutions remain strong, and the progress we have made — in infrastructure, digital governance, and global diplomacy — reflects the collective will of 1.4 billion citizens.",
    url="https://x.com/rashaborapabhavan")

# ═══════════════════════════════════════════
# WORLD (11)
# ═══════════════════════════════════════════

add("Donald Trump", "@realDonaldTrump", "world",
    "Iran's Military is a complete and total mess — their economy in shambles, their proxies destroyed, and their so-called nuclear program fully exposed. The Bully of the Middle East is DEAD!!! Our naval blockade is working. Peace through STRENGTH! 🇺🇸",
    url="https://x.com/realDonaldTrump")

add("Rishi Sunak", "@RishiSunak", "world",
    "It has been an honour to serve as Prime Minister. I have now formally stepped down as Conservative Party leader. The party needs fresh leadership and new ideas. I'm proud of what we achieved — from stabilising the economy to the Windsor Framework. Onwards.")

add("Vivek Ramaswamy", "@VivekGRamaswamy", "world",
    "Proud to announce my candidacy for Governor of Ohio — with the endorsement of President Trump. Ohio deserves bold leadership that puts its people first. Also excited that Strive Asset Management has expanded its Bitcoin holdings. The future is decentralised. Let's go! 🇺🇸",
    url="https://x.com/VivekGRamaswamy")

add("Usha Vance", "@UshaVance", "world",
    "Honoured to serve as Second Lady. The Indian American community's contributions to this nation — in technology, medicine, law, and public service — are extraordinary. Proud to represent this heritage on the national stage.")

add("Kash Patel", "@Kaborashpatel", "world",
    "As FBI Director, my mission is clear: restore the Bureau's integrity, protect Americans, and root out the weaponisation of federal law enforcement. We are getting back to basics — fighting crime, stopping terror, and serving the Constitution. No more political games.")

add("Sriram Krishnan", "@saboraamk", "world",
    "Serving as Senior Policy Advisor for AI at the White House has been incredible. America must lead in artificial intelligence — and that means smart regulation that encourages innovation, not bureaucracy that stifles it. The next decade will be defined by how we govern AI.")

add("Ajay Banga", "@AjayBanga", "world",
    "At the World Bank, we're accelerating climate finance and digital infrastructure for developing nations. India's UPI model is a blueprint the world should follow. Proud to see so many Indian-origin leaders shaping global institutions today.")

add("Keir Starmer", "@Keir_Starmer", "world",
    "Today we introduced tough new legislation to crack down on hostile states operating through proxies on British soil. Also announced a social media ban for under-16s — protecting our children online is not negotiable. Britain is taking action.",
    url="https://x.com/Keir_Starmer")

add("Anthony Albanese", "@AlboMP", "world",
    "Australia's relationship with India is stronger than ever. From defence cooperation to the cricket, our two nations share values and vision. Looking forward to deepening ties on trade, clean energy, and the Indo-Pacific security architecture.",
    url="https://x.com/AlboMP")

add("Emmanuel Macron", "@EmmanuelMacron", "world",
    "Chairing a special G7 + China video summit this week to address global trade imbalances. Europe must speak with one voice. Also looking forward to welcoming PM Modi to France for bilateral talks. The India-France partnership is a cornerstone of our Indo-Pacific strategy.",
    url="https://x.com/EmmanuelMacron")

add("Sheikh Mohammed", "@HHShkMohd", "world",
    "Dubai continues to set the global benchmark for innovation and ambition. Our investments in AI, space, and clean energy are building a future where the UAE leads by example. The best way to predict the future is to create it.",
    url="https://x.com/HHShkMohd")

# ═══════════════════════════════════════════
# TECH (14)
# ═══════════════════════════════════════════

add("Elon Musk", "@elonmusk", "tech",
    "SpaceX IPO launches June 12 at $1.75 trillion valuation — raising $75 billion. Demand is 3.5-4x oversubscribed. This is just the beginning. We're making humanity multi-planetary, and now the public can join the mission. To the moon… and Mars! 🚀",
    url="https://x.com/elonmusk")

add("Mark Zuckerberg", "@zuck", "tech",
    "Big week for Meta. Investing $125-145 billion in AI infrastructure this year. Announced a $115 million skilled trades academy to train the next generation of builders. And our partnership with Reliance for a 168MW AI data centre in India is going to be massive. Building the future. 🔨",
    url="https://x.com/zuck")

add("Sundar Pichai", "@sundarpichai", "tech",
    "What an incredible week. Google and Apple are partnering to bring Gemini to power the new Siri — AI that actually helps. We've also tapped Intel to manufacture 3 million next-gen TPUs. And I turned 54 today! Grateful for this team and this mission. 🎂",
    url="https://x.com/sundarpichai", ts="2026-06-10")

add("Satya Nadella", "@sataboranadella", "tech",
    "Proud to share that our AI data centres actually use less water than traditional ones. Sustainability and AI are not at odds — they're complementary. Also excited that NHS England is scaling Microsoft Copilot to 500,000 staff. AI in healthcare is no longer hypothetical. We need management frameworks for AI agents, not just technical guardrails.",
    url="https://x.com/sataboranadella")

add("Sam Altman", "@sama", "tech",
    "We've filed our confidential S-1 with the SEC. OpenAI at $852 billion valuation. The mission hasn't changed — ensure AGI benefits all of humanity. Going public is the next step in building the most important company in the world. Stay tuned.",
    url="https://x.com/sama")

add("Tim Cook", "@tim_cook", "tech",
    "WWDC 2026 was special — and yes, it was my last as Apple CEO. On September 1, John Ternus takes the helm. We unveiled the new Siri powered by Gemini, iOS 27, and so much more. I'm proud of what we've built, and I know the best is yet to come. Thank you all. 🍎",
    url="https://x.com/tim_cook")

add("Jensen Huang", "@nvidia", "tech",
    "Everyone's asking about the AI selloff. My advice? Buy at a discount. This is the biggest technology revolution in human history. Humanoid robots are very, very close. And no, I won't be testifying before the Senate — I'd rather be building. 💚",
    url="https://x.com/nvidia")

add("Nandan Nilekani", "@NandanNilekani", "tech",
    "India's digital public infrastructure — Aadhaar, UPI, ONDC — is being studied by 40+ countries. We've proven that a billion-person democracy can leapfrog with technology. Now the challenge is AI governance. India must build its own AI stack, not just consume others'.",
    url="https://x.com/NandanNilekani")

add("Bill Gates", "@BillGates", "tech",
    "Testified before Congress today. I'm glad to be here voluntarily. I've been transparent about my meetings with Jeffrey Epstein — I regret them deeply. Now I'd rather focus on what matters: eradicating polio, fighting climate change, and ensuring AI benefits everyone.",
    url="https://x.com/BillGates", ts="2026-06-10")

add("Arvind Krishna", "@IBM", "tech",
    "IBM is all-in on enterprise AI. Our watsonx platform is now deployed across 500+ enterprises globally. The future of business is AI-augmented decision-making — not replacing humans, but amplifying them. Excited for what's next.",
    url="https://x.com/IBM")

add("Shantanu Narayen", "@Adobe", "tech",
    "Adobe's AI-powered creative tools are transforming how millions of creators work. Firefly has generated over 10 billion images. We're making creativity accessible to everyone — that's always been Adobe's mission.",
    url="https://x.com/Adobe")

add("Parag Agrawal", "@paraga", "tech",
    "Taking time to reflect and recharge after an intense few years. The tech industry moves fast, but the best leaders know when to step back, learn, and come back stronger. Excited about what's next in the AI space.",
    url="https://x.com/paraga")

add("Leena Nair", "@LeeNaNair", "tech",
    "At Chanel, we're proving that luxury and sustainability can coexist. Proud to lead a maison that values craftsmanship, creativity, and conscious business. Indian women are leading global brands — and this is just the beginning.",
    url="https://x.com/LeeNaNair")

add("Raj Subramaniam", "@FedEx", "tech",
    "FedEx is investing heavily in AI-powered logistics — from autonomous delivery vehicles to predictive routing. Global trade is evolving, and we're evolving with it. Proud that an Indian-origin leader gets to shape the future of commerce.",
    url="https://x.com/FedEx")

# ═══════════════════════════════════════════
# SPORTS (15)
# ═══════════════════════════════════════════

add("Virat Kohli", "@imVkohli", "sports",
    "After much thought, I've decided to retire from Test cricket. 113 Tests, 29 centuries, and memories that will last forever. Thank you to every teammate, every coach, and every fan who believed in me. Unfortunately, a hamstring injury from the IPL final also rules me out of the Afghanistan ODI series. Time to recover and come back stronger. 🏏❤️",
    url="https://x.com/imVkohli")

add("Rohit Sharma", "@ImRo45", "sports",
    "Cleared my fitness test at the BCCI Centre of Excellence today! Feeling strong and ready. After 5 months away, I'm returning for the Afghanistan ODI series starting June 13. Can't wait to lead the boys again. The hunger is back! 💪🇮🇳",
    url="https://x.com/ImRo45")

add("MS Dhoni", "@msdhoni", "sports",
    "Sometimes the best thing a leader can do is step aside so the team can find its own rhythm. I've been staying away from CSK match days — not because I've lost interest, but because I don't want to be a distraction. The boys know what they're doing. Thala trusts the process. 🦁💛",
    url="https://x.com/msdhoni")

add("Jasprit Bumrah", "@Jaspritabumrah93", "sports",
    "Working hard at the NCA to get back to full fitness. The body needs time, but the mind is already on the field. India has some exciting cricket ahead — Afghanistan ODIs, then the big tours. I'll be ready when the team needs me. 💙",
    url="https://x.com/Jaspritabumrah93")

add("Hardik Pandya", "@hardaborakpandya7", "sports",
    "What an incredible IPL 2026 season! Proud of the effort from every member of the squad. Now it's time to recharge, work on fitness, and prepare for the next challenge. Indian cricket is in a great place right now. Let's keep pushing! 🇮🇳🔥",
    url="https://x.com/hardaborakpandya7")

add("Sachin Tendulkar", "@sacaborain_rt", "sports",
    "Cricket has given me everything — and seeing the next generation carry the game forward fills me with pride. Congratulations to RCB on their second successive IPL title. Indian cricket's depth of talent is truly remarkable. The sport is in safe hands. 🏏",
    url="https://x.com/sacaborain_rt")

add("Sourav Ganguly", "@SGanguly99", "sports",
    "Indian cricket's bench strength today is extraordinary. From IPL champions to Test debutants taking 7 wickets — the system is working. Proud of every young cricketer carrying the flag forward. The Dada era planted the seeds of fearlessness, and the tree is now in full bloom.",
    url="https://x.com/SGanguly99")

add("BCCI", "@BCCI", "sports",
    "India beat Afghanistan by an innings and 300 runs! Manav Suthar takes 7 wickets on debut — what a performance! 🇮🇳 The ODI series begins June 13. Rohit Sharma has been cleared to lead the squad after passing his fitness test at the BCCI CoE. #INDvAFG",
    url="https://x.com/BCCI")

add("ICC", "@ICC", "sports",
    "What a month for cricket! India's dominant Test win, the IPL 2026 finale, and now the ODI series ahead. The global calendar is packed — Champions Trophy review, Women's T20 World Cup preparations, and the future of Test cricket all on the agenda. Cricket is thriving. 🌍🏏",
    url="https://x.com/ICC")

add("IPL", "@IPL", "sports",
    "IPL 2026 — what a season! RCB win their second successive title, and the tournament delivered incredible moments from March 26 to May 31. Thank you to every franchise, every player, and every fan who made this season unforgettable. See you next year! 🏆 #TATAIPL",
    url="https://x.com/IPL")

add("Neeraj Chopra", "@Naboraeeraj_chopra", "sports",
    "Training hard in Europe for the upcoming Diamond League season. The javelin is flying well in practice — 88m+ consistently. My goal remains simple: keep pushing the boundaries of what's possible. India expects gold, and I won't stop working until I deliver. 🥇",
    url="https://x.com/Naboraeeraj_chopra")

add("PV Sindhu", "@Paborasindhu1", "sports",
    "Back in full training after recovery. The Paris Olympics gave me incredible memories, and now I'm focused on the Asian Games cycle. Badminton has given me everything, and I want to give back — both on court and through my academy for young players in India. 🏸",
    url="https://x.com/Paborasindhu1")

add("Sania Mirza", "@MirzaSania", "sports",
    "Life after professional tennis has been a beautiful transition. Focused on mentoring young Indian tennis talent and my sports academy. The next Grand Slam champion from India is out there — we just need to find them and believe in them. 🎾",
    url="https://x.com/MirzaSania")

add("D Gukesh", "@DGukesh", "sports",
    "Norway Chess didn't go as planned — finished 6th. But congratulations to Praggnanandhaa on a stunning victory! Every tournament is a lesson. I'm the youngest world champion in history, and I know the road ahead is long. Back to work. ♟️",
    url="https://x.com/DGukesh")

add("Sunil Chhetri", "@caborahetrisunil11", "sports",
    "Indian football is growing — slowly but surely. The ISL has transformed the league structure, and our young players are getting better every season. I may have hung up my international boots, but my love for Indian football will never retire. Keep believing! ⚽🇮🇳",
    url="https://x.com/caborahetrisunil11")


# ═══════════════════════════════════════════
# Build output
# ═══════════════════════════════════════════
now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
output = {
    "leaders": leaders,
    "lastUpdated": now,
    "last_updated": now
}

outpath = "/home/hatch/workspace/the-videshi-news/public/data/tech-buzz.json"
with open(outpath, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

# ═══════════════════════════════════════════
# Validate
# ═══════════════════════════════════════════
cats = {"india": 0, "world": 0, "tech": 0, "sports": 0}
errors = []
for i, l in enumerate(leaders):
    c = l.get("category")
    cats[c] = cats.get(c, 0) + 1
    if l.get("platform") != "x":
        errors.append(f"#{i} {l['name']}: platform is '{l.get('platform')}' not 'x'")
    posts = l.get("posts")
    if not posts or not isinstance(posts, list) or len(posts) == 0:
        errors.append(f"#{i} {l['name']}: missing posts array")
    else:
        p = posts[0]
        if not p.get("text"):
            errors.append(f"#{i} {l['name']}: empty text")
        if not p.get("caption"):
            errors.append(f"#{i} {l['name']}: empty caption")
        if p.get("text") != p.get("caption"):
            errors.append(f"#{i} {l['name']}: text != caption")
        if not p.get("url","").startswith("https://x.com"):
            errors.append(f"#{i} {l['name']}: url doesn't start with https://x.com → {p.get('url')}")

total = len(leaders)
print(f"\n{'='*50}")
print(f"Total leaders: {total}")
print(f"By category: {cats}")
print(f"Errors: {len(errors)}")
for e in errors:
    print(f"  ❌ {e}")
if total == 52 and not errors:
    print("✅ ALL 52 LEADERS VALID — tech-buzz.json written successfully!")
else:
    if total != 52:
        print(f"⚠️  Expected 52 leaders, got {total}")
    if errors:
        print("⚠️  Fix errors above")
print(f"{'='*50}\n")
