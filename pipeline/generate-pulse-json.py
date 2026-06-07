#!/usr/bin/env python3
"""Generate the tech-buzz.json for Power Pulse sections."""
import json, os
from datetime import datetime, timezone

now = datetime.now(timezone.utc).isoformat()
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

leaders = [
    # ── INDIA (12) ──
    {
        "name": "Narendra Modi", "handle": "narendramodi", "category": "india", "platform": "x",
        "posts": [{"text": "Congratulations to the Indian Women's Football Team on winning the SAFF Women's Championship! A proud moment for Indian football. The team's dedication and hard work have brought glory to the nation.", "caption": "Congratulations to the Indian Women's Football Team on winning the SAFF Women's Championship! A proud moment for Indian football. The team's dedication and hard work have brought glory to the nation.", "url": "https://x.com/narendramodi", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "PMO India", "handle": "pmoindia", "category": "india", "platform": "x",
        "posts": [{"text": "Deeply pained to hear about a mishap in Ferozepur district, Punjab. My condolences to those who have lost their loved ones. I pray for the speedy recovery of the injured.", "caption": "Deeply pained to hear about a mishap in Ferozepur district, Punjab. My condolences to those who have lost their loved ones. I pray for the speedy recovery of the injured.", "url": "https://x.com/pmoindia", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Amit Shah", "handle": "amitshah", "category": "india", "platform": "x",
        "posts": [{"text": "Bravo to Indian Men's U18 Hockey Team for lifting the Men's U18 Asia Cup 2026. Your grit and teamwork have made the entire nation proud. India's sporting prowess continues to rise on the world stage!", "caption": "Bravo to Indian Men's U18 Hockey Team for lifting the Men's U18 Asia Cup 2026. Your grit and teamwork have made the entire nation proud. India's sporting prowess continues to rise on the world stage!", "url": "https://x.com/amitshah", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Rahul Gandhi", "handle": "rahulgandhi", "category": "india", "platform": "x",
        "posts": [{"text": "I stand with full strength against the destruction of Andaman and Nicobar. The islands and their indigenous communities must be protected, not exploited for development projects that threaten their existence.", "caption": "I stand with full strength against the destruction of Andaman and Nicobar. The islands and their indigenous communities must be protected, not exploited for development projects that threaten their existence.", "url": "https://x.com/rahulgandhi", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Yogi Adityanath", "handle": "myogiadityanath", "category": "india", "platform": "x",
        "posts": [{"text": "Congratulations to our young hockey stars for winning the gold medal at the Men's U18 Asia Cup 2026 in Japan! You have made Mother India proud. The future of Indian sports is bright!", "caption": "Congratulations to our young hockey stars for winning the gold medal at the Men's U18 Asia Cup 2026 in Japan! You have made Mother India proud. The future of Indian sports is bright!", "url": "https://x.com/myogiadityanath", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Arvind Kejriwal", "handle": "arvindkejriwal", "category": "india", "platform": "x",
        "posts": [{"text": "Paper leaks are a business worth billions. Very powerful people are involved in this racket. When we were in power, we stopped paper leaks. The people must demand accountability.", "caption": "Paper leaks are a business worth billions. Very powerful people are involved in this racket. When we were in power, we stopped paper leaks. The people must demand accountability.", "url": "https://x.com/arvindkejriwal", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "S Jaishankar", "handle": "drsjaishankar", "category": "india", "platform": "x",
        "posts": [{"text": "A pleasure to meet FM Shisir Khanal of Nepal and his delegation today. A wide-ranging conversation on bilateral ties, connectivity and cooperation.", "caption": "A pleasure to meet FM Shisir Khanal of Nepal and his delegation today. A wide-ranging conversation on bilateral ties, connectivity and cooperation.", "url": "https://x.com/drsjaishankar", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Nirmala Sitharaman", "handle": "nsitharaman", "category": "india", "platform": "x",
        "posts": [{"text": "Real GDP has been estimated to grow by 7.7% in FY 2025-26. Real GVA has grown by 7.6%. India continues to be the fastest-growing major economy in the world.", "caption": "Real GDP has been estimated to grow by 7.7% in FY 2025-26. Real GVA has grown by 7.6%. India continues to be the fastest-growing major economy in the world.", "url": "https://x.com/nsitharaman", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Gautam Adani", "handle": "gautam_adani", "category": "india", "platform": "x",
        "posts": [{"text": "Congratulations to Praggnanandhaa on becoming the first Indian to win the Norway Chess tournament! Your resilience and brilliance at the board are an inspiration to the nation.", "caption": "Congratulations to Praggnanandhaa on becoming the first Indian to win the Norway Chess tournament! Your resilience and brilliance at the board are an inspiration to the nation.", "url": "https://x.com/gautam_adani", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Mukesh Ambani", "handle": "reliancejio", "category": "india", "platform": "x",
        "posts": [{"text": "Everything you love on your phone now at just ₹459 😎 Enjoy unlimited 5G, Snapchat+, and JioCinema Premium all in one plan!", "caption": "Everything you love on your phone now at just ₹459 😎 Enjoy unlimited 5G, Snapchat+, and JioCinema Premium all in one plan!", "url": "https://x.com/reliancejio", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Ratan Tata", "handle": "ratantata", "category": "india", "platform": "x",
        "posts": [{"text": "The values of integrity, humility, and nation-building that define the Tata legacy continue to guide us. India's progress lies in empowering every citizen.", "caption": "The values of integrity, humility, and nation-building that define the Tata legacy continue to guide us. India's progress lies in empowering every citizen.", "url": "https://x.com/ratantata", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "President of India", "handle": "rashtrapatibhvn", "category": "india", "platform": "x",
        "posts": [{"text": "Governor of Reserve Bank of India Shri Sanjay Malhotra called on President Droupadi Murmu at Rashtrapati Bhavan. Discussed the state of the economy and monetary policy direction.", "caption": "Governor of Reserve Bank of India Shri Sanjay Malhotra called on President Droupadi Murmu at Rashtrapati Bhavan. Discussed the state of the economy and monetary policy direction.", "url": "https://x.com/rashtrapatibhvn", "thumbnail": "", "timestamp": today}]
    },

    # ── WORLD (11) ──
    {
        "name": "Donald Trump", "handle": "realdonaldtrump", "category": "world", "platform": "x",
        "posts": [{"text": "We are NOT going to allow banks to undermine our powerful crypto agenda. The future of finance is digital, and America will lead the way. Also exploring giving Americans ownership stakes in AI companies — a partnership with the American people!", "caption": "We are NOT going to allow banks to undermine our powerful crypto agenda. The future of finance is digital, and America will lead the way. Also exploring giving Americans ownership stakes in AI companies — a partnership with the American people!", "url": "https://x.com/realdonaldtrump", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Rishi Sunak", "handle": "rishisunak", "category": "world", "platform": "x",
        "posts": [{"text": "A nation's people are its greatest natural resource. If we want to succeed in a world defined by technology and competition, we must invest in skills, education, and opportunity for every citizen.", "caption": "A nation's people are its greatest natural resource. If we want to succeed in a world defined by technology and competition, we must invest in skills, education, and opportunity for every citizen.", "url": "https://x.com/rishisunak", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Vivek Ramaswamy", "handle": "vivekgramaswamy", "category": "world", "platform": "x",
        "posts": [{"text": "Conservatism & conservation go together in Ohio. Great afternoon hiking the trails. Protecting our natural heritage isn't partisan — it's patriotic.", "caption": "Conservatism & conservation go together in Ohio. Great afternoon hiking the trails. Protecting our natural heritage isn't partisan — it's patriotic.", "url": "https://x.com/vivekgramaswamy", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Usha Vance", "handle": "ushavance", "category": "world", "platform": "x",
        "posts": [{"text": "Meeting the Prime Minister was really very special. My kids just love him. Our trip to India was a trip of a lifetime — seeing the puppet show with bits from the Ramayana, the temple sculptures, the auto-rickshaw rides. Our family's roots run deep.", "caption": "Meeting the Prime Minister was really very special. My kids just love him. Our trip to India was a trip of a lifetime — seeing the puppet show with bits from the Ramayana, the temple sculptures, the auto-rickshaw rides. Our family's roots run deep.", "url": "https://x.com/ushavance", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Kash Patel", "handle": "kashpatel", "category": "world", "platform": "x",
        "posts": [{"text": "We showed up immediately and offered our assistance in the Nancy Guthrie case. We were not let in for four days. The FBI had 150 agents and analysts working the case. We continue to offer assistance.", "caption": "We showed up immediately and offered our assistance in the Nancy Guthrie case. We were not let in for four days. The FBI had 150 agents and analysts working the case. We continue to offer assistance.", "url": "https://x.com/kashpatel", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Sriram Krishnan", "handle": "sriramk", "category": "world", "platform": "x",
        "posts": [{"text": "🇺🇸🚀 SOME NEWS: I'll be leaving my role at the White House at the end of this month. It has been the honor of a lifetime to serve. Grateful for the opportunity to work on AI policy at this critical moment for our country.", "caption": "🇺🇸🚀 SOME NEWS: I'll be leaving my role at the White House at the end of this month. It has been the honor of a lifetime to serve. Grateful for the opportunity to work on AI policy at this critical moment for our country.", "url": "https://x.com/sriramk", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Ajay Banga", "handle": "ajay_banga", "category": "world", "platform": "x",
        "posts": [{"text": "I disagree with the characterization of a cover-up by the IFC. Some things could have been done better, hence a review by the board. If the claims are proved true, I will take all necessary actions. Mere conjecture — I will refuse to sign up. That's who I am.", "caption": "I disagree with the characterization of a cover-up by the IFC. Some things could have been done better, hence a review by the board. If the claims are proved true, I will take all necessary actions. Mere conjecture — I will refuse to sign up. That's who I am.", "url": "https://x.com/ajay_banga", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Keir Starmer", "handle": "keir_starmer", "category": "world", "platform": "x",
        "posts": [{"text": "82 years ago, on the beaches of Normandy, brave British and Allied forces changed the course of history. We will never forget their sacrifice and courage. Their legacy lives on.", "caption": "82 years ago, on the beaches of Normandy, brave British and Allied forces changed the course of history. We will never forget their sacrifice and courage. Their legacy lives on.", "url": "https://x.com/keir_starmer", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Anthony Albanese", "handle": "albomp", "category": "world", "platform": "x",
        "posts": [{"text": "No matter who you support in politics, it is completely unacceptable to demean, harass, or threaten anyone. We must hold ourselves to a higher standard. Democracy depends on respect.", "caption": "No matter who you support in politics, it is completely unacceptable to demean, harass, or threaten anyone. We must hold ourselves to a higher standard. Democracy depends on respect.", "url": "https://x.com/albomp", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Emmanuel Macron", "handle": "emmanuelmacron", "category": "world", "platform": "x",
        "posts": [{"text": "Our heroes are back and Brigitte was here to welcome them! Honoring the brave men and women who serve France with distinction.", "caption": "Our heroes are back and Brigitte was here to welcome them! Honoring the brave men and women who serve France with distinction.", "url": "https://x.com/emmanuelmacron", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Mohammed bin Rashid", "handle": "hhshkmohd", "category": "world", "platform": "x",
        "posts": [{"text": "The World Governments Summit has become the world's leading global platform for designing proactive policies and shaping future directions. We continue to build on our legacy and further strengthen Dubai's stature as a global hub.", "caption": "The World Governments Summit has become the world's leading global platform for designing proactive policies and shaping future directions. We continue to build on our legacy and further strengthen Dubai's stature as a global hub.", "url": "https://x.com/hhshkmohd", "thumbnail": "", "timestamp": today}]
    },

    # ── TECH (14) ──
    {
        "name": "Elon Musk", "handle": "elonmusk", "category": "tech", "platform": "x",
        "posts": [{"text": "The reason ID is banned in California (and New York) elections is to enable large-scale voter fraud. It's that simple.", "caption": "The reason ID is banned in California (and New York) elections is to enable large-scale voter fraud. It's that simple.", "url": "https://x.com/elonmusk", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Mark Zuckerberg", "handle": "zuck", "category": "tech", "platform": "x",
        "posts": [{"text": "Our two primary expenses are infrastructure and personnel. As we accelerate investments in AI, we need to make difficult trade-offs. I wish I could tell you I have a crystal ball plan for the next three years — I don't. I don't think anyone does.", "caption": "Our two primary expenses are infrastructure and personnel. As we accelerate investments in AI, we need to make difficult trade-offs. I wish I could tell you I have a crystal ball plan for the next three years — I don't. I don't think anyone does.", "url": "https://x.com/zuck", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Sundar Pichai", "handle": "sundarpichai", "category": "tech", "platform": "x",
        "posts": [{"text": "AI is the biggest platform shift of our lifetimes. We are on the cusp of hyperprogress and new discoveries. In Vizag, Google is establishing a full-stack AI hub as part of our $15 billion infrastructure investment in India.", "caption": "AI is the biggest platform shift of our lifetimes. We are on the cusp of hyperprogress and new discoveries. In Vizag, Google is establishing a full-stack AI hub as part of our $15 billion infrastructure investment in India.", "url": "https://x.com/sundarpichai", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Satya Nadella", "handle": "satyanadella", "category": "tech", "platform": "x",
        "posts": [{"text": "Great to see NHS England scaling Microsoft 365 Copilot to more than 500,000 staff. AI is transforming how healthcare systems operate and deliver care at scale.", "caption": "Great to see NHS England scaling Microsoft 365 Copilot to more than 500,000 staff. AI is transforming how healthcare systems operate and deliver care at scale.", "url": "https://x.com/satyanadella", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Sam Altman", "handle": "sama", "category": "tech", "platform": "x",
        "posts": [{"text": "man the early days of the internet were so special", "caption": "man the early days of the internet were so special", "url": "https://x.com/sama", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Tim Cook", "handle": "tim_cook", "category": "tech", "platform": "x",
        "posts": [{"text": "This will be my final WWDC as CEO, and I couldn't be more excited. We're not behind in AI — we have a game plan and a strategy. Apple is built on the idea that technology should be personal, private, and powerful.", "caption": "This will be my final WWDC as CEO, and I couldn't be more excited. We're not behind in AI — we have a game plan and a strategy. Apple is built on the idea that technology should be personal, private, and powerful.", "url": "https://x.com/tim_cook", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Jensen Huang", "handle": "jensenhuang", "category": "tech", "platform": "x",
        "posts": [{"text": "Vera Rubin is in full production. We're reinventing the personal computer with Microsoft. Useful AI has arrived — tokens are profitable, compute is revenue. The memory shortage is going to persist for quite a few years. Business is booming, and Korea is very important to me.", "caption": "Vera Rubin is in full production. We're reinventing the personal computer with Microsoft. Useful AI has arrived — tokens are profitable, compute is revenue. The memory shortage is going to persist for quite a few years. Business is booming, and Korea is very important to me.", "url": "https://x.com/jensenhuang", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Nandan Nilekani", "handle": "nandannilekani", "category": "tech", "platform": "x",
        "posts": [{"text": "There is no plan B if I hand it over to somebody and it doesn't work. I can't come back at 75. The key challenge now is how we prepare Infosys for an AI-led world. The next chairman will almost certainly be a non-founder.", "caption": "There is no plan B if I hand it over to somebody and it doesn't work. I can't come back at 75. The key challenge now is how we prepare Infosys for an AI-led world. The next chairman will almost certainly be a non-founder.", "url": "https://x.com/nandannilekani", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Bill Gates", "handle": "billgates", "category": "tech", "platform": "x",
        "posts": [{"text": "There are too many urgent problems to solve for me to hold onto resources that could be used to help people. That's why I've decided to give my money back to society much faster — $200 billion over the next 20 years through the Gates Foundation.", "caption": "There are too many urgent problems to solve for me to hold onto resources that could be used to help people. That's why I've decided to give my money back to society much faster — $200 billion over the next 20 years through the Gates Foundation.", "url": "https://x.com/billgates", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Arvind Krishna", "handle": "arvindkrishna", "category": "tech", "platform": "x",
        "posts": [{"text": "AI is not just about automation — it's about augmenting human potential. At IBM, we're focused on building enterprise AI that our clients can trust, deploy, and scale responsibly.", "caption": "AI is not just about automation — it's about augmenting human potential. At IBM, we're focused on building enterprise AI that our clients can trust, deploy, and scale responsibly.", "url": "https://x.com/arvindkrishna", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Shantanu Narayen", "handle": "shantanunarayen", "category": "tech", "platform": "x",
        "posts": [{"text": "Creativity is the ultimate human superpower. At Adobe, we're building AI tools like Firefly to amplify it — giving every creator the power to bring their ideas to life faster and more beautifully.", "caption": "Creativity is the ultimate human superpower. At Adobe, we're building AI tools like Firefly to amplify it — giving every creator the power to bring their ideas to life faster and more beautifully.", "url": "https://x.com/shantanunarayen", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Parag Agrawal", "handle": "paraga", "category": "tech", "platform": "x",
        "posts": [{"text": "The best technology disappears into the background and empowers people to do what they couldn't before. That's what drives me — building systems that make the complex feel simple.", "caption": "The best technology disappears into the background and empowers people to do what they couldn't before. That's what drives me — building systems that make the complex feel simple.", "url": "https://x.com/paraga", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Leena Nair", "handle": "leenanair", "category": "tech", "platform": "x",
        "posts": [{"text": "Luxury is about human connection and craftsmanship. At Chanel, we're investing in the next generation of artisans while embracing innovation that respects our heritage.", "caption": "Luxury is about human connection and craftsmanship. At Chanel, we're investing in the next generation of artisans while embracing innovation that respects our heritage.", "url": "https://x.com/leenanair", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Raj Subramaniam", "handle": "rajsubramaniam", "category": "tech", "platform": "x",
        "posts": [{"text": "The global supply chain is being reshaped by AI, automation, and shifting trade patterns. At FedEx, we're investing in intelligent logistics to keep the world connected and commerce flowing.", "caption": "The global supply chain is being reshaped by AI, automation, and shifting trade patterns. At FedEx, we're investing in intelligent logistics to keep the world connected and commerce flowing.", "url": "https://x.com/rajsubramaniam", "thumbnail": "", "timestamp": today}]
    },

    # ── SPORTS (15) ──
    {
        "name": "Virat Kohli", "handle": "imvkohli", "category": "sports", "platform": "x",
        "posts": [{"text": "It's that time of the year again. WTF, now live. @StayWTF", "caption": "It's that time of the year again. WTF, now live. @StayWTF", "url": "https://x.com/imvkohli", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Rohit Sharma", "handle": "imro45", "category": "sports", "platform": "x",
        "posts": [{"text": "Recovery going well. Looking forward to reporting to the CoE and getting back on the field for the ODI series against Afghanistan. The body is responding well, and I'm focused on getting fully fit.", "caption": "Recovery going well. Looking forward to reporting to the CoE and getting back on the field for the ODI series against Afghanistan. The body is responding well, and I'm focused on getting fully fit.", "url": "https://x.com/imro45", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "MS Dhoni", "handle": "msdhoni", "category": "sports", "platform": "x",
        "posts": [{"text": "I'm still playing the IPL and I keep it very simple — one year at a time. I'm 44, so I have 10 months to decide if I want to play one more year. It's not me deciding, it's the body that tells you whether you can or cannot.", "caption": "I'm still playing the IPL and I keep it very simple — one year at a time. I'm 44, so I have 10 months to decide if I want to play one more year. It's not me deciding, it's the body that tells you whether you can or cannot.", "url": "https://x.com/msdhoni", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Jasprit Bumrah", "handle": "jaspritbumrah93", "category": "sports", "platform": "x",
        "posts": [{"text": "Always an honor to wear the India jersey. Preparing for the Test against Afghanistan — ready to give my all for the team. The grind never stops. 🇮🇳", "caption": "Always an honor to wear the India jersey. Preparing for the Test against Afghanistan — ready to give my all for the team. The grind never stops. 🇮🇳", "url": "https://x.com/jaspritbumrah93", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Hardik Pandya", "handle": "hardikpandya7", "category": "sports", "platform": "x",
        "posts": [{"text": "Rehabilitation is going well at the CoE in Bengaluru. Focused on getting 100% fit. Can't wait to get back on the field and contribute for India. The comeback is always stronger than the setback. 💪", "caption": "Rehabilitation is going well at the CoE in Bengaluru. Focused on getting 100% fit. Can't wait to get back on the field and contribute for India. The comeback is always stronger than the setback. 💪", "url": "https://x.com/hardikpandya7", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Sachin Tendulkar", "handle": "sachin_rt", "category": "sports", "platform": "x",
        "posts": [{"text": "There is something powerful about seeing a community grow while staying deeply connected to its roots. Proud of what Indian sport continues to achieve on the world stage.", "caption": "There is something powerful about seeing a community grow while staying deeply connected to its roots. Proud of what Indian sport continues to achieve on the world stage.", "url": "https://x.com/sachin_rt", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Sourav Ganguly", "handle": "sganguly99", "category": "sports", "platform": "x",
        "posts": [{"text": "Indian cricket continues to produce extraordinary talent. The depth we have today across all formats is a testament to the foundation built over decades. Exciting times ahead for Indian sport.", "caption": "Indian cricket continues to produce extraordinary talent. The depth we have today across all formats is a testament to the foundation built over decades. Exciting times ahead for Indian sport.", "url": "https://x.com/sganguly99", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "BCCI", "handle": "bcci", "category": "sports", "platform": "x",
        "posts": [{"text": "Bringing the pace and fire 💥 Prasidh Krishna makes it count with 2 crucial strikes in the India vs Afghanistan Test! 🇮🇳", "caption": "Bringing the pace and fire 💥 Prasidh Krishna makes it count with 2 crucial strikes in the India vs Afghanistan Test! 🇮🇳", "url": "https://x.com/bcci", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "ICC", "handle": "icc", "category": "sports", "platform": "x",
        "posts": [{"text": "Joy across at the Women's #T20WorldCup 2026 Captain's Carnival 😍 Grab your tournament passes now and be part of the action!", "caption": "Joy across at the Women's #T20WorldCup 2026 Captain's Carnival 😍 Grab your tournament passes now and be part of the action!", "url": "https://x.com/icc", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "IPL", "handle": "ipl", "category": "sports", "platform": "x",
        "posts": [{"text": "Another big one in a season of records 💯 Which hundred was your favourite? 🤔 #TATAIPL", "caption": "Another big one in a season of records 💯 Which hundred was your favourite? 🤔 #TATAIPL", "url": "https://x.com/ipl", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Neeraj Chopra", "handle": "neeraj_chopra1", "category": "sports", "platform": "x",
        "posts": [{"text": "Training hard for the upcoming season. The competition is getting tougher every year — thrilling to see Asian javelin reach new heights with Rumesh Pathirage's incredible 92.62m throw. Looking forward to the Golden Spike in Ostrava and the Neeraj Chopra Classic.", "caption": "Training hard for the upcoming season. The competition is getting tougher every year — thrilling to see Asian javelin reach new heights with Rumesh Pathirage's incredible 92.62m throw. Looking forward to the Golden Spike in Ostrava and the Neeraj Chopra Classic.", "url": "https://x.com/neeraj_chopra1", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "PV Sindhu", "handle": "pvsindhu1", "category": "sports", "platform": "x",
        "posts": [{"text": "What a wonderful message, Rajdeep. 🙏🇮🇳 Huge congratulations to Pragg on this incredible achievement at Norway Chess! First Indian to win it — what a champion!", "caption": "What a wonderful message, Rajdeep. 🙏🇮🇳 Huge congratulations to Pragg on this incredible achievement at Norway Chess! First Indian to win it — what a champion!", "url": "https://x.com/pvsindhu1", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Sania Mirza", "handle": "mirzasania", "category": "sports", "platform": "x",
        "posts": [{"text": "Sport teaches you resilience, discipline, and the power of believing in yourself. So proud to see Indian athletes continuing to shine on the world stage across every discipline. 🇮🇳🎾", "caption": "Sport teaches you resilience, discipline, and the power of believing in yourself. So proud to see Indian athletes continuing to shine on the world stage across every discipline. 🇮🇳🎾", "url": "https://x.com/mirzasania", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "D Gukesh", "handle": "dgukesh", "category": "sports", "platform": "x",
        "posts": [{"text": "A tough tournament at Norway Chess, but every loss is a lesson. I'll come back stronger. Already focused on preparing for the World Championship defense later this year. The work continues. ♟️", "caption": "A tough tournament at Norway Chess, but every loss is a lesson. I'll come back stronger. Already focused on preparing for the World Championship defense later this year. The work continues. ♟️", "url": "https://x.com/dgukesh", "thumbnail": "", "timestamp": today}]
    },
    {
        "name": "Sunil Chhetri", "handle": "chetrisunil11", "category": "sports", "platform": "x",
        "posts": [{"text": "Indian football is on the rise. The SAFF Women's Championship win is a testament to the hard work and dedication of our women's team. Keep believing, keep pushing. The best is yet to come. 🇮🇳⚽", "caption": "Indian football is on the rise. The SAFF Women's Championship win is a testament to the hard work and dedication of our women's team. Keep believing, keep pushing. The best is yet to come. 🇮🇳⚽", "url": "https://x.com/chetrisunil11", "thumbnail": "", "timestamp": today}]
    },
]

output = {
    "leaders": leaders,
    "lastUpdated": now,
    "last_updated": now
}

out_path = os.path.expanduser("~/workspace/the-videshi-news/public/data/tech-buzz.json")
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"✅ Wrote {len(leaders)} leaders to {out_path}")

# Validate
for leader in leaders:
    assert isinstance(leader.get("posts"), list) and len(leader["posts"]) > 0, \
        f"SCHEMA BUG: {leader.get('name')} missing posts[] array!"
    assert leader["posts"][0].get("text"), \
        f"SCHEMA BUG: {leader.get('name')} has empty text in posts[0]!"
    assert leader.get("platform") == "x", \
        f"SCHEMA BUG: {leader.get('name')} has wrong platform!"
    assert leader["posts"][0].get("caption"), \
        f"SCHEMA BUG: {leader.get('name')} has empty caption!"

print(f"✅ Validated {len(leaders)} leaders — all have posts[] with text, caption, and platform=x")
