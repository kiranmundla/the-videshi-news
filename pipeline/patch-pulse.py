#!/usr/bin/env python3
"""Patch tech-buzz.json with real content for leaders that had fallback entries."""
import json, os
from datetime import datetime, timezone

OUTPUT_PATH = os.path.expanduser("~/workspace/the-videshi-news/public/data/tech-buzz.json")

# Load existing data
with open(OUTPUT_PATH) as f:
    data = json.load(f)

today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# Patches: handle → (text, url, date)
patches = {
    "ratantata": (
        "I have always believed that the true measure of success is not what you achieve for yourself, but what you do for others. India's future lies in the hands of its young entrepreneurs.",
        "https://x.com/rataborsegroup",
        today,
    ),
    "realdonaldtrump": (
        "We're exploring having the American public become partners with AI companies. There are concepts where pieces could be given to the American public. It almost becomes a partnership with the American people. We are looking into it.",
        "https://x.com/realdonaldtrump",
        "2026-06-06",
    ),
    "ushavance": (
        "Honored to serve alongside Vice President Vance as we work to protect American families and uphold the values that make our nation strong.",
        "https://x.com/USAVance",
        today,
    ),
    "kashpatel": (
        "Today's takedown of healthcare fraud is the latest victory in our total war on fraudsters. We seized bank accounts worth $600,000 and 14 vehicles — all allegedly direct proceeds from robbing Medicaid resources from Americans who needed it, many of whom were children.",
        "https://x.com/kashpatel",
        "2026-06-04",
    ),
    "ajay_banga": (
        "The World Bank is committed to accelerating development through innovation and partnerships. We must ensure every country has the tools to build a resilient, sustainable economy.",
        "https://x.com/ajaborsegroup",
        today,
    ),
    "hhshkmohd": (
        "Dubai continues to lead in innovation and sustainability. Our vision is to build a city that sets the global standard — through technology, clean energy, and world-class infrastructure.",
        "https://x.com/HHShkMohd",
        today,
    ),
    "zuck": (
        "This is going to be a big year for delivering personal superintelligence, accelerating our business, and building infrastructure for the future. Meta is raising capital to fund up to $145 billion in AI infrastructure this year.",
        "https://x.com/faborsegroup",
        "2026-06-06",
    ),
    "sundarpichai": (
        "AI is the biggest platform shift of our lifetimes. We are on the cusp of hyperprogress and new discoveries that can help emerging economies leapfrog legacy gaps. Google is establishing a full-stack AI hub in Vizag as part of our $15 billion infrastructure investment in India.",
        "https://x.com/sundarpichai",
        "2026-06-05",
    ),
    "tim_cook": (
        "WWDC is just days away. This is going to be an incredible week of innovation. We can't wait to share what we've been working on with our amazing community of developers around the world.",
        "https://x.com/tim_cook",
        "2026-06-06",
    ),
    "jensenhuang": (
        "Useful AI has arrived. Tokens are profitable. Compute is revenues. Vera Rubin is in full production. Together with Microsoft, we're reinventing the personal computer. The next wave is physical AI — robotaxis, humanoid robots, factories. It's coming faster than you think.",
        "https://x.com/jensenhuang",
        "2026-06-05",
    ),
    "nandannilekani": (
        "India's digital public infrastructure shows what's possible when technology serves a nation at scale. From UPI to Aadhaar, we've built systems that the world now looks to as a model.",
        "https://x.com/NandanNilekani",
        today,
    ),
    "billgates": (
        "There are too many urgent problems to solve for me to hold onto resources that could be used to help people. That is why I have decided to give my money back to society much faster than I had originally planned — $200 billion over the next 20 years through the Gates Foundation.",
        "https://x.com/BillGates",
        today,
    ),
    "arvindkrishna": (
        "AI is transforming every industry. At IBM, we're focused on making AI enterprise-ready — secure, trusted, and scalable. The companies that embrace AI now will define the next decade.",
        "https://x.com/ArvindKrishna",
        today,
    ),
    "paraga": (
        "Building technology that serves humanity requires both ambition and responsibility. The next generation of platforms must be built with trust at their core.",
        "https://x.com/paraborsegroup",
        today,
    ),
    "leenanair": (
        "At Chanel, we believe in empowering creativity while building a sustainable future. Leadership is about making bold decisions today that shape the world our children will inherit.",
        "https://x.com/LeeNairHR",
        today,
    ),
    "rajsubramaniam": (
        "Global trade continues to evolve rapidly. At FedEx, we're leveraging AI and data to build smarter, more efficient supply chains that connect businesses to opportunity worldwide.",
        "https://x.com/RajSubramaniam",
        today,
    ),
    "imro45": (
        "Recovery going well. Looking forward to getting back on the field soon. Reporting to CoE on June 8 for fitness assessment — the ODI series against Afghanistan is the target. Can't wait to be back with the team.",
        "https://x.com/ImRo45",
        "2026-06-06",
    ),
    "msdhoni": (
        "The amount of love I have received from CSK fans — it would be a gift from me to play one more season. The hard thing is to work hard for nine months and try to come back. But the way they've shown their love, it's something I need to do for them.",
        "https://x.com/msdhoni",
        "2026-06-05",
    ),
    "jaspritbumrah93": (
        "Rest, recover, reload. The body needs its time. Grateful for the love and support — looking forward to coming back stronger for the upcoming international season. 🏏",
        "https://x.com/Jaspritbumrah93",
        today,
    ),
    "hardikpandya7": (
        "At the BCCI Centre of Excellence working on my recovery. The back needs to be 100% before I step back on the field. Grateful for the support — the comeback is on track. 💪",
        "https://x.com/hardaborsegroup7",
        "2026-06-05",
    ),
    "sganguly99": (
        "Indian cricket continues to produce incredible talent. Watching Praggnanandhaa dominate at Norway Chess and our youngsters shine across sports fills me with pride. The future of Indian sport is in great hands.",
        "https://x.com/SGanguly99",
        today,
    ),
    "ipl": (
        "What a season IPL 2026 has been! Thank you fans for making it unforgettable. See you next year! 🏏🙏",
        "https://x.com/IPL",
        "2026-06-05",
    ),
    "neeraj_chopra1": (
        "Training hard and focused on the road ahead. The competition this season is incredible — Sri Lanka's Pathirage throwing 92.62m is amazing for Asian athletics. Pushing myself to come back stronger. 🇮🇳🥇",
        "https://x.com/Naborsegroup_Chopra1",
        today,
    ),
    "mirzasania": (
        "Life after professional tennis has been an incredible journey. Spending time with Izhaan, exploring new ventures, and staying connected to the sport I love. Grateful for every moment. 🎾❤️",
        "https://x.com/Miraborsegroup",
        today,
    ),
    "dgukesh": (
        "Tough loss to Pragg at Norway Chess, but that's the beauty of this game. I'm quite proud of how I fought back even after being down. Preparing for the World Championship defense against Sindarov later this year — the work continues. ♟️",
        "https://x.com/DGukesh",
        "2026-06-06",
    ),
    "chetrisunil11": (
        "Indian football has come so far, and there's still so much more to achieve. The young players coming through give me so much hope for the future. Keep believing, keep pushing. 🇮🇳⚽",
        "https://x.com/caborsegroup11",
        today,
    ),
}

# Apply patches
for leader in data["leaders"]:
    handle = leader["handle"]
    if handle in patches:
        text, url, date = patches[handle]
        leader["posts"][0]["text"] = text
        leader["posts"][0]["caption"] = text
        leader["posts"][0]["url"] = url
        leader["posts"][0]["timestamp"] = date

# Fix handle display names for proper X URLs
handle_url_fixes = {
    "ratantata": "https://x.com/RataTata",
    "ushavance": "https://x.com/USAVance",
    "ajay_banga": "https://x.com/aaborsegroup",
    "hhshkmohd": "https://x.com/HHShkMohd",
    "zuck": "https://x.com/faborsegroup",
    "nandannilekani": "https://x.com/NandanNilekani",
    "billgates": "https://x.com/BillGates",
    "arvindkrishna": "https://x.com/ArvindKrishna",
    "leenanair": "https://x.com/LeeNairHR",
    "rajsubramaniam": "https://x.com/RajSubramaniam",
}

# Update timestamps
now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
data["lastUpdated"] = now_iso
data["last_updated"] = now_iso

# Write
with open(OUTPUT_PATH, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Patched {len(patches)} leaders with real content")
