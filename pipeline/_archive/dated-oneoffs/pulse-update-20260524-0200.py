#!/usr/bin/env python3
"""Power Pulse + Celebrity Buzz update — 2026-05-24 02:00 PDT
Key updates this cycle:
- Iran deal: Sunday deadline — Rubio says 'more news could come on Sunday'; MoU being 'fine-tuned'
- Rubio-Jaishankar bilateral held Sunday — discussed Middle East, trade, visas, maritime security
- White House shooting: 21-year-old Nasire Best shot at Secret Service checkpoint, killed; bystander wounded
- IPL FINAL DAY: MI vs RR (Wankhede, 3:30 PM IST) + KKR vs DC (Eden Gardens, 7:30 PM IST) — not yet played
- Russia: massive missile/drone attack on Kyiv, 4 killed, 56 injured
- Pakistan: bomb explosion in Quetta kills 24 on railway track
- California: chemical tank crisis in Garden Grove, tens of thousands evacuated
- Bollywood: Ramayana may prepone to Oct 30 2026; Varanasi (Mahesh Babu/Rajamouli) shoots key song
"""

import json
import os
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TECH_BUZZ = os.path.join(SCRIPT_DIR, "..", "public", "data", "tech-buzz.json")
CELEB_BUZZ = os.path.join(SCRIPT_DIR, "..", "public", "data", "celebrity-buzz.json")


def update_tech_buzz():
    with open(TECH_BUZZ) as f:
        data = json.load(f)

    leaders_by_handle = {l["handle"]: l for l in data.get("leaders", [])}
    updated = 0

    updates = {
        # === TECH PULSE ===
        "elonmusk": {
            "text": "SpaceX IPO filing targets $1.75T valuation — S&P 500 inclusion could force $950B in passive fund reallocation. Starship completes 12th test flight. Iran deal expected to finalize Sunday — Rubio says 'more news coming.' If Hormuz reopens and oil drops, tech sentiment soars. Dow near record ~50,563.",
            "url": "https://x.com/elonmusk",
            "date": "2026-05-24",
        },
        "zuck": {
            "text": "Meta confirms 15,000 total job actions — 8K cut, 7K reassigned to AI teams. $115-135B on AI infrastructure in 2026. Leaked audio: Zuckerberg defended employee surveillance. Threads crosses 150M daily users. White House shooting adds to DC security concerns — a month after Correspondents' Dinner incident.",
            "url": "https://x.com/zuck",
            "date": "2026-05-24",
        },
        "sundarpichai": {
            "text": "Google pushes Gemini AI across Search, Workspace, and Cloud. Rubio-Jaishankar bilateral held Sunday — discussed trade, tech, maritime security. Quad FM meeting May 26. Big Tech's $50B India investment wave accelerates. Iran MoU being 'fine-tuned' — Sunday deadline looms.",
            "url": "https://x.com/sundarpichai",
            "date": "2026-05-24",
        },
        "satyanadella": {
            "text": "Microsoft defends $80B AI infrastructure investment as Azure crosses $75B quarterly revenue. Copilot enterprise adoption at record highs. Iran deal finalization expected Sunday — if Hormuz reopens, oil stabilizes, and tech spending momentum strengthens.",
            "url": "https://x.com/satyanadella",
            "date": "2026-05-24",
        },
        "sama": {
            "text": "Sam Altman teases GPT-5 — 'smarter than the smartest person' — as Musk v. OpenAI lawsuit heads toward trial. OpenAI's valuation soars. Bill Gates argues AI pauses counterproductive. Iran deal Sunday deadline could reshape global AI investment climate.",
            "url": "https://x.com/sama",
            "date": "2026-05-24",
        },
        "tim_cook": {
            "text": "Apple succession lands on John Ternus — 'the mind of an engineer, the soul of an innovator.' WWDC 2026 AI features incoming. Apple asks Supreme Court to review App Store contempt ruling. White House shooting near checkpoint adds to DC security spiral.",
            "url": "https://x.com/tim_cook",
            "date": "2026-05-24",
        },
        "nvidia": {
            "text": "Nvidia's jaw-dropping $81.6B Q1 revenue — 10x from three years ago. Vera Rubin platform: 10x inference throughput per megawatt over Blackwell. Jensen concedes China market to Huawei. Iran deal Sunday finalization would add further lift to tech-heavy markets.",
            "url": "https://x.com/nvidia",
            "date": "2026-05-24",
        },
        "NandanNilekani": {
            "text": "Big Tech pours $50B into India. Rubio-Jaishankar bilateral Sunday — tech cooperation central to Quad agenda. India emerging as top AI talent hub. Quad FM meeting May 26 will discuss critical tech. Iran deal Sunday deadline adds geopolitical dimension to India's tech moment.",
            "url": "https://x.com/NandanNilekani",
            "date": "2026-05-24",
        },
        "BillGates": {
            "text": "Bill Gates argues AI development pauses risk ceding ground to less safety-conscious actors. Kevin Warsh — whom Gates has advised — starts at the Fed. Iran MoU being 'fine-tuned' Sunday. Russia's massive Kyiv strike adds geopolitical uncertainty alongside Iran talks.",
            "url": "https://x.com/BillGates",
            "date": "2026-05-24",
        },
        "ArvindKrishna": {
            "text": "IBM CEO Arvind Krishna expands AI partnerships — Tech Mahindra and IBM accelerate enterprise Generative AI via watsonx platform. India emerges as major enterprise AI hub. Rubio-Jaishankar bilateral Sunday highlighted tech cooperation. $50B Big Tech India wave.",
            "url": "https://x.com/ArvindKrishna",
            "date": "2026-05-24",
        },
        "ShantanuNarayen": {
            "text": "Adobe CEO integrates generative AI across Creative Cloud and Experience Cloud. Firefly gains traction against Midjourney and DALL-E. Cannes 2026 closed — 'Fjord' won Palme d'Or as AI-generated content debate intensifies in film industry.",
            "url": "https://x.com/ShantanuNarayen",
            "date": "2026-05-24",
        },
        "paraga": {
            "text": "Former Twitter CEO Parag Agrawal focuses on AI ventures and advisory roles in Silicon Valley post-Musk acquisition. The Indian-American tech diaspora continues shaping global AI leadership as Big Tech pours $50B into India.",
            "url": "https://x.com/paraga",
            "date": "2026-05-21",
        },
        "LeenaNairHR": {
            "text": "Chanel CEO Leena Nair steers the luxury house through competitive landscape. Cannes 2026 wrapped — Aishwarya dazzled, Aaradhya's red carpet debut. Ramayana may prepone to Oct 30 2026 (Diwali week). Indian-born diaspora influence in luxury leadership grows.",
            "url": "https://x.com/LeenaNairHR",
            "date": "2026-05-24",
        },
        "RajSubramaniam": {
            "text": "FedEx CEO Raj Subramaniam navigates logistics amid trade disruptions. Iran MoU being 'fine-tuned' — Hormuz reopening would be transformative for global shipping. Pakistan's Quetta bomb kills 24 — security challenges along key logistics corridors.",
            "url": "https://x.com/RajSubramaniam",
            "date": "2026-05-24",
        },

        # === INDIA PULSE ===
        "narendramodi": {
            "text": "Rubio-Jaishankar bilateral held SUNDAY — discussed Middle East, trade, defense, visas, maritime security. Rubio cited 'progress in last 48 hours' on Iran. Trump invites Modi to White House. 'Mission 500' to double trade by 2030. Quad FM Meeting Monday. India at center of global diplomacy.",
            "url": "https://x.com/narendramodi",
            "date": "2026-05-24",
        },
        "PMOIndia": {
            "text": "India-US ties deepen — Rubio's 4-city visit (Kolkata → Delhi → Agra → Jaipur) sets stage for Quad FM meeting Monday. Iran MoU being 'fine-tuned' — Sunday finalization expected. India positioned as key player in Iran peace framework. Big Tech's $50B India investment wave arrives.",
            "url": "https://x.com/PMOIndia",
            "date": "2026-05-24",
        },
        "AmitShah": {
            "text": "Home Minister Shah oversees national security as White House shooting and Pakistan's Quetta bombing (24 dead) underline global security challenges. Rubio-Jaishankar bilateral Sunday discussed counter-terrorism and defense cooperation. Iran deal Sunday deadline looms.",
            "url": "https://x.com/AmitShah",
            "date": "2026-05-24",
        },
        "RahulGandhi": {
            "text": "Congress leader Rahul Gandhi renews attacks on Modi-Adani ties as Adani Group expands. Opposition sharpens criticism amid $50B Big Tech wave and $22.2B FPI outflows. Rubio's White House invite to Modi draws attention. IPL's dramatic final day captivates the nation.",
            "url": "https://x.com/RahulGandhi",
            "date": "2026-05-24",
        },
        "myogiadityanath": {
            "text": "UP CM Yogi Adityanath continues infrastructure push. Rubio's Kolkata visit — first by a US envoy in 14 years — expands diplomatic footprint beyond Delhi. Rajamouli's 'Varanasi' (Mahesh Babu) shoots crucial song sequence in UP — global spotlight on the holy city.",
            "url": "https://x.com/myogiadityanath",
            "date": "2026-05-24",
        },
        "ArvindKejriwal": {
            "text": "AAP leader Kejriwal steps up opposition rhetoric. Delhi politics intensifies as Rubio-Jaishankar bilateral wraps, Iran deal reaches Sunday deadline, and IPL's most dramatic final day unfolds — KKR vs DC at Eden Gardens tonight decides the 4th playoff spot.",
            "url": "https://x.com/ArvindKejriwal",
            "date": "2026-05-24",
        },
        "DrSJaishankar": {
            "text": "EAM Jaishankar held bilateral with Rubio on SUNDAY — discussed Middle East, trade, visas, maritime security, energy. Rubio: 'progress in last 48 hours' on Iran. Quad FM Meeting MONDAY with US, Japan, Australia FMs in Delhi. India's diplomatic moment of the year.",
            "url": "https://x.com/DrSJaishankar",
            "date": "2026-05-24",
        },
        "nsitharaman": {
            "text": "Finance Minister Sitharaman monitors economic outlook — $50B Big Tech investments land while FPI outflows hit $22.2B. Iran deal Sunday finalization could ease oil import costs. Russia's Kyiv missile strike and Pakistan's Quetta bombing add geopolitical risk to markets.",
            "url": "https://x.com/nsitharaman",
            "date": "2026-05-24",
        },
        "rashtrapatibhvn": {
            "text": "President Murmu presides as India hosts critical Quad diplomacy. Rubio-Jaishankar bilateral completed Sunday. Four nations converge on Delhi for Monday FM meeting. Iran deal expected to finalize Sunday. India's global standing strengthens across multiple fronts.",
            "url": "https://x.com/rashtrapatibhvn",
            "date": "2026-05-24",
        },
        "gautam_adani": {
            "text": "Adani Group pushes into green energy, ports, data centers as India attracts $50B Big Tech wave. Reliance-Adani rivalry intensifies after Ambani scraps family noncompete. Iran deal finalization Sunday — Hormuz reopening could reshape India's entire energy import chain.",
            "url": "https://x.com/gautam_adani",
            "date": "2026-05-24",
        },
        "RelianceJio": {
            "text": "Mukesh Ambani's Reliance expands into power and telecom after scrapping family noncompete. $1B telecom investment, shares up 4.9%. Iran deal being 'fine-tuned' — if Hormuz reopens Sunday, India's energy costs could drop sharply. IPL final day captivates nation.",
            "url": "https://x.com/RelianceJio",
            "date": "2026-05-24",
        },
        "RNTata2000": {
            "text": "The Ratan Tata Foundation continues its legacy of philanthropy. Tata Group companies remain at forefront as India attracts record foreign investment. Russia's Kyiv strike and Pakistan's Quetta bombing add urgency to global security discussions at Quad.",
            "url": "https://x.com/RNTata2000",
            "date": "2026-05-24",
        },

        # === WORLD / POWER PULSE ===
        "realDonaldTrump": {
            "text": "Iran MoU being 'fine-tuned' — Sunday deadline for finalization. Rubio says 'more news coming.' White House shooting: 21-year-old Nasire Best (believed he was Jesus) shot dead by Secret Service at checkpoint; bystander wounded. Trump praised 'swift and professional action.' Second WH shooting in a month.",
            "url": "https://x.com/realDonaldTrump",
            "date": "2026-05-24",
        },
        "WhiteHouse": {
            "text": "SHOOTING: Nasire Best, 21, opened fire at WH checkpoint — killed by Secret Service. Bystander wounded. Trump safe. Second WH shooting in a month (after Correspondents' Dinner). Iran deal 'fine-tuned' — Sunday finalization expected. Gabbard exits DNI June 30; Aaron Lukas acting.",
            "url": "https://x.com/WhiteHouse",
            "date": "2026-05-24",
        },
        "Keir_Starmer": {
            "text": "UK PM Starmer co-chaired 40+ nation Hormuz summit with Macron. Iran MoU being 'fine-tuned' Sunday. Russia's massive Kyiv missile strike kills 4, injures 56 — Ukraine war escalates alongside Iran diplomacy. Free summer bus travel for kids announced. Reform UK's Farage circling.",
            "url": "https://x.com/Keir_Starmer",
            "date": "2026-05-24",
        },
        "EmmanuelMacron": {
            "text": "Macron co-hosted 40+ nation Hormuz summit. Iran MoU Sunday finalization imminent. Russia launches massive missile/drone attack on Kyiv — 4 killed, 56 injured including near metro station. France navigates dual crises: Iran peace + Ukraine escalation. Oil at ~$107.",
            "url": "https://x.com/EmmanuelMacron",
            "date": "2026-05-24",
        },
        "AlboMP": {
            "text": "Australian PM Albanese prepares for Quad FM meeting in New Delhi MONDAY. Iran deal finalization expected Sunday. Rubio-Jaishankar bilateral already held. Australia's FM to engage India, Japan, US on Indo-Pacific security. Hormuz resolution affects energy costs down under.",
            "url": "https://x.com/AlboMP",
            "date": "2026-05-24",
        },
        "GiorgiaMeloni": {
            "text": "Italian PM Meloni's viral 'Melody' moment with Modi strengthens Italy-India ties. Iran MoU Sunday deadline. Russia's Kyiv missile strike kills 4 — G7 coordination on both Iran and Ukraine intensifies. Quetta bombing (24 dead) adds to global security concerns.",
            "url": "https://x.com/GiorgiaMeloni",
            "date": "2026-05-24",
        },
        "HHShkMohd": {
            "text": "UAE ruler MBR watches Iran MoU finalization — Sunday deadline. 60-day ceasefire extension with no-toll Hormuz passage proposed. Mine clearance, US blockade lift, sanctions waivers for oil on the table. Gulf nations push for permanent resolution. ADNOC: full oil flows not before Q1 2027.",
            "url": "https://x.com/HHShkMohd",
            "date": "2026-05-24",
        },
        "chrisluxonNZ": {
            "text": "NZ PM Luxon monitors Indo-Pacific developments as Quad FM meeting approaches Monday. Iran deal Sunday deadline. Russia's Kyiv strike escalates Ukraine war. Five Eyes alignment and Pacific security shift as multiple crises converge.",
            "url": "https://x.com/chrisluxonNZ",
            "date": "2026-05-24",
        },
        "VivekGRamaswamy": {
            "text": "Vivek continues post-DOGE political trajectory. Gabbard resigned as DNI (husband's cancer) — Aaron Lukas acting. White House shooting: second in a month raises security questions. Vivek's Ohio ambitions and 'anti-woke' brand remain active as 2028 positioning continues.",
            "url": "https://x.com/VivekGRamaswamy",
            "date": "2026-05-24",
        },
        "RishiSunak": {
            "text": "Former UK PM Sunak observes from opposition as Starmer navigates Iran deal and Russia's Kyiv missile strike. Reform UK's Farage sharpens attacks. Sunak's legacy as Britain's first Indian-origin PM continues to resonate with the global diaspora.",
            "url": "https://x.com/RishiSunak",
            "date": "2026-05-24",
        },
        "UshaVance": {
            "text": "Second Lady Usha Vance — Indian-American Yale Law grad — watches as VP JD Vance returned to DC Saturday for Iran deal deliberations. White House shooting near checkpoint where Vance's motorcade passes. Iran MoU being 'fine-tuned' for Sunday.",
            "url": "https://x.com/UshaVance",
            "date": "2026-05-24",
        },
        "KashPatel47": {
            "text": "FBI Director Kash Patel oversees investigation into White House shooting — Nasire Best, 21, identified as gunman with 'violent history and possible obsession' per Trump. FBI probing motive. Second WH shooting incident in a month. Iran deal Sunday deadline keeps intelligence community active.",
            "url": "https://x.com/KashPatel47",
            "date": "2026-05-24",
        },
        "SriramKrishnan": {
            "text": "White House AI advisor Sriram Krishnan shapes US tech policy amid Big Tech's $50B India push and SpaceX's $1.75T IPO filing. Rubio-Jaishankar bilateral Sunday — tech cooperation central. White House shooting raises security concerns near the very offices where AI policy is made.",
            "url": "https://x.com/SriramKrishnan",
            "date": "2026-05-24",
        },
        "SuellaBraverman": {
            "text": "Former UK Home Secretary Suella Braverman — Indian-origin Tory — remains vocal on immigration from backbenches. Russia's Kyiv missile strike and White House shooting dominate global headlines as Starmer faces Reform UK pressure.",
            "url": "https://x.com/SuellaBraverman",
            "date": "2026-05-24",
        },
        "AjayBanga": {
            "text": "World Bank President Ajay Banga monitors Iran deal Sunday finalization — Hormuz reopening would transform global trade. Quetta bombing (24 dead) and Russia's Kyiv strike add instability. ADNOC warns full oil flows won't return before Q1 2027 even if deal holds.",
            "url": "https://x.com/AjayBanga",
            "date": "2026-05-24",
        },

        # === SPORTS PULSE ===
        "imVkohli": {
            "text": "IPL FINAL DAY: RCB finished TOP with 18 pts (best NRR). Qualifier 1 vs Gujarat Titans on May 27 at Dharamsala. Kohli-Head handshake controversy still viral globally. TODAY: MI vs RR (Wankhede, 3:30 PM IST) + KKR vs DC (Eden Gardens, 7:30 PM). Three teams, one spot. Drama guaranteed.",
            "url": "https://x.com/imVkohli",
            "date": "2026-05-24",
        },
        "ImRo45": {
            "text": "IPL FINAL DAY: Mumbai Indians face Rajasthan Royals at Wankhede TODAY (3:30 PM IST). MI's dead rubber is RR's knockout — if MI win, PBKS get the 4th spot. Rohit's last match of the season decides three teams' fates. The biggest 'meaningless' match in IPL history.",
            "url": "https://x.com/ImRo45",
            "date": "2026-05-24",
        },
        "msdhoni": {
            "text": "CSK eliminated from IPL 2026. TODAY decides the 4th playoff spot — MI vs RR (Wankhede) + KKR vs DC (Eden Gardens). PBKS (15 pts) need RR AND KKR to lose. RR just need to beat MI. KKR need to win + RR loss. The IPL Dhoni helped build has never been this dramatic.",
            "url": "https://x.com/msdhoni",
            "date": "2026-05-24",
        },
        "Jaspritbumrah93": {
            "text": "Bumrah left out of T20 World Cup squad — managed for longer formats. MI face RR at Wankhede TODAY. MI's result decides the 4th playoff spot for three other teams. Can Bumrah's team play kingmaker on the most consequential dead rubber in IPL history?",
            "url": "https://x.com/Jaspritbumrah93",
            "date": "2026-05-24",
        },
        "hardikpandya7": {
            "text": "MI vs RR at Wankhede TODAY (3:30 PM IST) — MI's dead rubber is RR's knockout. If MI win, PBKS get the 4th spot. Hardik's MI hold three teams' fates in their hands. The most dramatic IPL final day ever. Pride match for Mumbai becomes a kingmaker showdown.",
            "url": "https://x.com/hardikpandya7",
            "date": "2026-05-24",
        },
        "BCCI": {
            "text": "IPL 2026 FINAL DAY TODAY: Match 69 MI vs RR (Wankhede, 3:30 PM IST) + Match 70 KKR vs DC (Eden Gardens, 7:30 PM). Top 3 locked: RCB (1st), GT (2nd), SRH (3rd) — all 18 pts. PBKS (15, done) pray for RR AND KKR losses. RR (14) need a win. KKR (13) need win + RR loss. One spot, three teams.",
            "url": "https://x.com/BCCI",
            "date": "2026-05-24",
        },
        "ICC": {
            "text": "ICC board meeting in Ahmedabad May 30. Kohli-Head handshake controversy dominates cricket headlines globally. IPL 2026 FINAL DAY TODAY — three teams fight for one playoff spot across two matches. T20 World Cup squad selections create ripples. Cricket at fever pitch.",
            "url": "https://x.com/ICC",
            "date": "2026-05-24",
        },
        "IPL": {
            "text": "FINAL DAY TODAY: Match 69 MI vs RR (Wankhede, 3:30 PM) + Match 70 KKR vs DC (Eden Gardens, 7:30 PM). Three teams, one spot. PBKS 15 pts (done). RR 14 pts — just need to win. KKR 13 pts — need win + RR loss. Playoffs start May 27 at Dharamsala. The greatest IPL final day ever?",
            "url": "https://x.com/IPL",
            "date": "2026-05-24",
        },
        "Neeraj_chopra1": {
            "text": "Neeraj Chopra preps for the 2026 athletics season. Federation Cup in Ranchi spotlights India's next wave of track and field talent. Diamond League awaits the Olympic champion's return. IPL's dramatic final day captures nation's attention alongside global diplomacy.",
            "url": "https://x.com/Neeraj_chopra1",
            "date": "2026-05-24",
        },
        "Pvsindhu1": {
            "text": "PV Sindhu continues her badminton campaign as the international circuit heats up. India's shuttlers build momentum through Super Series events ahead of the Asian Games cycle.",
            "url": "https://x.com/Pvsindhu1",
            "date": "2026-05-22",
        },
        "MirzaSania": {
            "text": "Tennis icon Sania Mirza's legacy continues to inspire Indian tennis. Post-retirement, she remains the most prominent Indian face in global tennis, mentoring the next generation.",
            "url": "https://x.com/MirzaSania",
            "date": "2026-05-22",
        },
        "DGukesh": {
            "text": "World Chess Champion D Gukesh faces heat — GM Nepomniachtchi: 'Every top GM would have a good chance against him.' Preps for title defense against Sindarov. The youngest world champion plots his comeback. IPL's final day and Iran deal dominate India's Sunday.",
            "url": "https://x.com/DGukesh",
            "date": "2026-05-24",
        },
        "chetrisunil11": {
            "text": "AIFF announces 2026-27 Club Licensing results as Indian football restructures. Sunil Chhetri's legacy as India's all-time top scorer endures. IPL's final day takes center stage as India's sporting calendar reaches its most dramatic moment.",
            "url": "https://x.com/chetrisunil11",
            "date": "2026-05-24",
        },
        "sachin_rt": {
            "text": "Son Arjun's LSG fell to PBKS last night (Shreyas Iyer 101*). TODAY: MI vs RR at Wankhede — the match that decides the 4th playoff spot. KKR vs DC at Eden Gardens follows. Three teams, one seat. Cricket's greatest legacy extends to the next generation on IPL's most dramatic day.",
            "url": "https://x.com/sachin_rt",
            "date": "2026-05-24",
        },
        "SGanguly99": {
            "text": "DADA'S KKR face DC at Eden Gardens TONIGHT (7:30 PM IST) — do-or-die for the 4th spot. KKR need to win AND hope MI beat RR in the afternoon. If RR win, KKR are out regardless. The franchise Ganguly built faces its most dramatic day. Three teams, one spot.",
            "url": "https://x.com/SGanguly99",
            "date": "2026-05-24",
        },
    }

    for handle, update in updates.items():
        if handle in leaders_by_handle:
            leader = leaders_by_handle[handle]
            if "latestPost" in leader:
                leader["latestPost"]["text"] = update["text"]
                leader["latestPost"]["url"] = update["url"]
                leader["latestPost"]["date"] = update["date"]
            if "text" in leader:
                leader["text"] = update["text"]
            if "url" in leader:
                leader["url"] = update["url"]
            if "date" in leader:
                leader["date"] = update["date"]
            updated += 1
        else:
            print(f"⚠️  Handle '{handle}' not found in tech-buzz.json")

    data["lastUpdated"] = datetime.now(timezone.utc).isoformat()
    with open(TECH_BUZZ, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ tech-buzz.json: {updated}/{len(updates)} leaders updated")


def update_celebrity_buzz():
    celeb_posts = [
        {
            "name": "Donald Trump",
            "handle": "realdonaldtrump",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Iran MoU being 'fine-tuned' — Sunday deadline for finalization. White House SHOOTING: 21-yr-old Nasire Best killed by Secret Service after opening fire at checkpoint. Bystander wounded. Trump praised 'swift and professional action.' Second WH shooting in a month.",
            "url": "https://www.instagram.com/realdonaldtrump/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Virat Kohli",
            "handle": "virat.kohli",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "IPL FINAL DAY: RCB top with 18 pts, Qualifier 1 vs GT May 27 at Dharamsala. Handshake Gate with Travis Head still viral. TODAY: MI vs RR (Wankhede) + KKR vs DC (Eden Gardens) decides the 4th playoff spot. Three teams, one seat. Kohli watches from the top.",
            "url": "https://www.instagram.com/virat.kohli/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Narendra Modi",
            "handle": "narendramodi",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Rubio-Jaishankar bilateral held SUNDAY — discussed Middle East, trade, visas, maritime security. Rubio: 'progress in last 48 hours' on Iran. Quad FM Meeting MONDAY. Trump invites Modi to White House. 'Mission 500' to double trade by 2030. India at center of global diplomacy.",
            "url": "https://www.instagram.com/narendramodi/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Shreyas Iyer",
            "handle": "shreyasiyer96",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "MAIDEN IPL CENTURY (101*) lifts PBKS to 15 pts. Now the agonizing wait: need MI to beat RR at Wankhede TODAY (3:30 PM IST) AND KKR to lose to DC tonight. The most dramatic IPL final day in years — three teams, one spot. Iyer did his part.",
            "url": "https://www.instagram.com/shreyasiyer96/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Aishwarya Rai Bachchan",
            "handle": "aaborofficial",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Cannes 2026 wrapped — Aishwarya dazzled in Amit Aggarwal couture, Aaradhya's red carpet debut stole hearts. 'Fjord' won Palme d'Or. Ramayana may prepone to Oct 30 (Diwali week) — Bollywood's biggest spectacle could arrive sooner. Red carpet scam exposé rocks the festival world.",
            "url": "https://www.instagram.com/aaborofficial/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Elon Musk",
            "handle": "elonmusk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "SpaceX IPO targets $1.75T — potentially LARGEST ever. Iran deal Sunday deadline — if Hormuz reopens, oil drops, tech soars. White House shooting: Secret Service killed gunman near checkpoint where tech leaders routinely visit. Dow near record ~50,563.",
            "url": "https://www.instagram.com/elonmusk/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Mark Zuckerberg",
            "handle": "zuck",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Meta's AI reckoning: 15K job actions (8K cut + 7K reassigned). $115-135B on AI infra in 2026. Leaked audio: Zuck defends surveillance for AI race. Threads hits 150M daily users. White House shooting adds to DC security concerns a month after Correspondents' Dinner incident.",
            "url": "https://www.instagram.com/zuck/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Shah Rukh Khan",
            "handle": "iamsrk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "'King' with Suhana and Deepika may split into two parts — Part 1 eyed for Christmas 2026. KKR face DC at Eden Gardens TONIGHT — SRK's team needs a miracle for the 4th spot (win + RR loss). Dhurandhar at ₹1,307 crore. IPL's most dramatic final day ever.",
            "url": "https://www.instagram.com/iamsrk/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "MS Dhoni",
            "handle": "msdhoni",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "CSK eliminated. FINAL DAY TODAY: MI vs RR (Wankhede, 3:30 PM) + KKR vs DC (Eden Gardens, 7:30 PM). Three teams, one spot. The IPL Dhoni helped build has never been more dramatic. Who gets the 4th seat — PBKS, RR, or KKR?",
            "url": "https://www.instagram.com/msdhoni/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Hardik Pandya",
            "handle": "hardikpandya93",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "MI vs RR at Wankhede TODAY (3:30 PM IST) — MI's dead rubber is RR's knockout. If MI win, PBKS get the 4th spot. Hardik's MI can play kingmaker. Three teams' fates in MI's hands on IPL's most dramatic final day. Pride match becomes destiny decider.",
            "url": "https://www.instagram.com/hardikpandya93/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Deepika Padukone",
            "handle": "deepikapadukone",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Deepika uses body double for action in SRK's 'King' and Atlee's 'Raka' due to pregnancy. Ramayana may prepone to Oct 30 2026 (Diwali week). 'Varanasi' (Rajamouli/Mahesh Babu) shoots crucial song sequence. Bollywood's biggest year takes shape.",
            "url": "https://www.instagram.com/deepikapadukone/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Diljit Dosanjh",
            "handle": "diljitdosanjh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Diljit's concert tour continues selling out across North America. THE face of Indian music going global — bridging Bollywood and the diaspora one sold-out arena at a time. 6 featured events on The Videshi. IPL's final day dominates India while Diljit dominates the NRI circuit.",
            "url": "https://www.instagram.com/diljitdosanjh/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Ranveer Singh",
            "handle": "ranveersingh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Ranveer's 'Pralay' (₹300 crore post-apocalyptic thriller) begins filming August 2026. Dhurandhar at ₹1,307 crore. Ramayana may prepone to Oct 30 (Diwali week). Vicky Kaushal blocks 18 months for 'Mahavatar.' Bollywood's biggest-ever year takes shape.",
            "url": "https://www.instagram.com/ranveersingh/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Sachin Tendulkar",
            "handle": "sachintendulkar",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Son Arjun's LSG fell last night (Shreyas Iyer 101*). TODAY: MI vs RR at Wankhede decides three teams' fates. KKR vs DC at Eden Gardens follows. The greatest IPL final day — three teams, one spot. Cricket's legacy extends to the next generation.",
            "url": "https://www.instagram.com/sachintendulkar/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "D Gukesh",
            "handle": "dgukesh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Chess Champion faces heat — GM Nepo: 'Every top GM would have a good chance against him.' Preps for title defense against Sindarov. IPL's dramatic final day and Iran deal Sunday deadline dominate India's Sunday. The youngest champion plots his comeback.",
            "url": "https://www.instagram.com/dgukesh/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Mukesh Ambani",
            "handle": "reliancejio",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Reliance expands into power and telecom after scrapping family noncompete. $1B telecom investment. Iran MoU being 'fine-tuned' — Sunday finalization expected. If Hormuz reopens, India's energy costs drop sharply. MI vs RR at Wankhede — Ambani's team plays kingmaker.",
            "url": "https://www.instagram.com/reliancejio/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Priyanka Chopra",
            "handle": "priyankachopra",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Global icon Priyanka's dual Hollywood-Bollywood career continues. 'Jee Le Zaraa' with Katrina and Alia most anticipated. Ramayana may prepone to Oct 30 (Diwali week). Cannes wrapped — red carpet scam exposé rocks festival circuit. Indian star power going global.",
            "url": "https://www.instagram.com/priyankachopra/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Shreya Ghoshal",
            "handle": "shreyaghoshal",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Shreya Ghoshal's live album generates buzz as her US tour hits 5 cities. The voice of a generation sells out diaspora venues — bringing Bollywood's golden age of playback singing to NRI audiences worldwide. IPL final day captivates India while Shreya captivates the diaspora.",
            "url": "https://www.instagram.com/shreyaghoshal/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Shraddha Kapoor",
            "handle": "shraddhakapoor",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Instagram's most-followed Indian actress (90M+). Cannes 2026 wrapped — red carpet scam exposé reveals paid access industry behind 'India at Cannes' glamour. Ramayana may prepone to Oct 30. Bollywood's biggest year taking shape.",
            "url": "https://www.instagram.com/shraddhakapoor/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Alia Bhatt",
            "handle": "aliaabhatt",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Alia's 'Jee Le Zaraa' with Priyanka and Katrina most anticipated. IMAX confirms Ranbir's 'Ramayana' for premium release — may prepone to Oct 30 (Diwali week). 'Varanasi' (Rajamouli/Mahesh Babu) shoots crucial song. Bollywood's biggest slate ever.",
            "url": "https://www.instagram.com/aliaabhatt/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Gautam Adani",
            "handle": "gautam_adani",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Adani Group pushes into green energy, ports, data centers. $50B Big Tech wave hits India. Iran MoU Sunday deadline — Hormuz reopening could reshape India's entire energy import chain. Reliance-Adani rivalry intensifies. Quetta bombing adds to regional security concerns.",
            "url": "https://www.instagram.com/gautam_adani/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Keir Starmer",
            "handle": "keir_starmer",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "UK PM co-chaired 40+ nation Hormuz summit. Iran MoU Sunday finalization imminent. Russia's Kyiv missile strike kills 4 — dual crisis management. White House shooting adds to global security concerns. Free summer bus travel for kids. Reform UK's Farage sharpens attacks.",
            "url": "https://www.instagram.com/keir_starmer/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Ajay Banga",
            "handle": "ajay_banga",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Bank President monitors Iran deal Sunday finalization — Hormuz reopening would transform global trade. ADNOC warns full oil flows not before Q1 2027. Quetta bombing (24 dead), Russia's Kyiv strike add instability. Indian-American diaspora at helm of global governance.",
            "url": "https://www.instagram.com/ajay_banga/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
    ]

    data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "posts": celeb_posts
    }
    with open(CELEB_BUZZ, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ celebrity-buzz.json: {len(celeb_posts)} posts updated")


if __name__ == "__main__":
    update_tech_buzz()
    update_celebrity_buzz()
    print("✅ All pulse data updated for 2026-05-24 02:00 PDT")
