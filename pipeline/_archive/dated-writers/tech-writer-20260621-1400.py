#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

apple_intel_body = """Donald Trump broke the news, which is itself the news. In a Truth Social post on Thursday, the president announced that Apple had "agreed to work with Intel to design and build its Chips in America." Intel's shares jumped 11% to a record. Apple said nothing. Intel said nothing. And that silence is the most honest part of the story.

Behind the bluster sits a real shift. The two companies reached a preliminary agreement back in May, after more than a year of talks, for Intel to manufacture some Apple-designed chips. Apple dumped Intel's processors from its Macs in 2020 in favour of its own silicon, built almost entirely by Taiwan Semiconductor Manufacturing Company (TSMC). What is being discussed now is narrower: Intel acting as a contract foundry for chips Apple designs itself, most likely older or lower-end parts, with production not expected before late 2027. Apple's flagship processors stay with TSMC.

**Why a presidential post, not a press release?**

Because this is as much politics as procurement. Washington took a roughly 10% stake in Intel last August, paying about $8 billion; Trump now claims that position is worth more than $60 billion. The administration has been chasing equity in chipmakers and critical-minerals firms to reduce reliance on China and rebuild a domestic supply chain. An Apple win validates Intel's struggling foundry business, which has been bleeding billions a quarter while its 18A manufacturing process slowly matures. Yole Group called it Intel's "biggest external foundry win yet," which tells you both that it matters and that Intel has rarely won big foundry customers before.

The trigger is a memory crisis. Tim Cook told the Wall Street Journal this week that price hikes on Apple products are now "unavoidable" because AI demand has sent memory and storage chip prices soaring. Micron, which reports earnings on June 24, has locked up its entire 2026 high-bandwidth memory supply and warned that DRAM and NAND will stay constrained. When the AI boom eats the world's memory, the bill lands on every phone and laptop buyer.

**The diaspora angle**

For Indian engineers in the Bay Area and beyond, this is a story with two faces. On one side, Intel's revival could mean a fresh hiring cycle at its Arizona and Ohio fabs and design centres, after years of layoffs that hit Indian H-1B holders hard. A government-backed foundry chasing Apple-scale volume needs process engineers, packaging specialists and yield experts, exactly the roles where Indian-origin talent is overrepresented.

On the other side, the deal underlines how concentrated the advanced-chip world remains. Apple's most sophisticated work stays in Taiwan. India's own semiconductor mission, anchored by Micron's assembly plant in Gujarat and Tata's fab in Dholera, is years from competing at the leading edge. For NRIs weighing a move back home to join the chip story, the Apple-Intel episode is a reminder of how long the climb is: even a once-dominant American giant with a 10% government backer is fighting to win lower-end work.

There is also a wallet angle that hits every Indian American household. If Cook is right that price increases are coming, the next iPhone and MacBook will cost more, and the reason traces directly to the AI infrastructure build-out that employs so many in this community. The same boom that pads the stock options also raises the checkout price.

**What's next**

Watch for confirmation that never quite comes. Intel's chief executive, Lip-Bu Tan, said in April that the company will not announce customers "unless the customer wants to announce it." Apple has a long history of saying nothing until silicon ships. Counterpoint Research suggests Apple may test Intel's 18A-P node for a future M-series processor, but analysts caution there is no guarantee Intel can match TSMC's yields, the share of working chips on a wafer that decides whether a foundry makes money.

For now, the deal exists mostly as a presidential post and a stock pop. The fundamentals, Intel's yield curve, Apple's risk tolerance and the trajectory of memory prices, will decide whether it becomes a genuine pillar of American chipmaking or another expensive experiment. Either way, the people building and buying the devices, many of them Indian, will feel the result first."""

london_spirit_body = """The bidding war for a cricket team at Lord's came down, improbably, to a Silicon Valley group chat. When the dust settled on the England and Wales Cricket Board's sale of The Hundred, the prestigious London Spirit franchise had gone not to an established cricket dynasty but to a consortium of Indian-origin technology billionaires, valuing the Lord's-based side at a staggering £295 million.

The names read like a roll-call of diaspora tech royalty. Microsoft chairman and chief executive Satya Nadella. Alphabet and Google boss Sundar Pichai. Palo Alto Networks chief Nikesh Arora, who led the eleven-strong group. And Satyan Gajwani, vice-chairman of Times Internet and co-founder of Major League Cricket in the United States. Together they bought 49% of the franchise, a stake that hands the ECB roughly £145 million, with the Marylebone Cricket Club retaining 51%.

**Beating the IPL at its own game**

What makes the outcome remarkable is who they beat. The Spirit were chased hard by Sanjiv Goenka, the Kolkata industrialist who owns the Lucknow Super Giants in the Indian Premier League and Durban Super Giants in South Africa's SA20. Goenka wanted the Lord's side badly. After an online auction that ran nearly four hours, he lost to the tech consortium and settled instead for Manchester Originals at a valuation of about £107 million, barely a third of what the Spirit fetched.

The arithmetic tells the story of how money now moves through global cricket. Four IPL owners scooped up other Hundred franchises; the ECB expects to raise close to £1 billion from the whole sale, more than half of it earmarked for English cricket's development. But the single richest deal went to a group whose day jobs are running the world's largest software companies, not cricket boards.

**Why this matters to the diaspora**

For Indian Americans, this is a story that sits at the exact intersection of who they are. These are the executives French president Emmanuel Macron pointed to when he said India "does not just participate in global innovation, it leads it." Now those same figures are buying into the sport that, more than any other, binds the diaspora to home. An NRI in New Jersey who streams the IPL at odd hours and follows Nadella's Azure earnings can now watch both passions converge on a single balance sheet.

It also signals where cricket's next frontier lies. Gajwani's presence is the tell: Major League Cricket is trying to build the game in the United States, where the diaspora is the core audience. A Lord's franchise owned partly by the people behind MLC creates an obvious bridge between English, Indian and American cricket, and a ready-made marketing pipeline aimed squarely at affluent South Asian professionals in the very cities where these readers live.

There is a softer signal too. For a generation of Indian American kids growing up between two cultures, seeing Pichai and Nadella, already heroes in engineering circles, become custodians of a cricket team at the home of the sport collapses the distance between Bangalore, the Bay Area and St John's Wood. It is the diaspora dream rendered as a sports-business deal.

**What's next**

The consortium bought 49%, not control, and questions remain about whether the group will pursue a majority stake later. The London Spirit board now includes Arora and Gajwani alongside cricketing figures such as Eoin Morgan, England's World Cup-winning former captain. The franchise has already signed Dewald Brevis, Adam Zampa and Liam Livingstone ahead of the 2026 season, with the rest of the squad to be settled at the March auction.

The deeper question is what tech money does to a 100-ball competition still finding its feet. These owners built empires on data, audience analytics and global distribution, precisely the tools English cricket has struggled to wield. If they bring even a fraction of that machinery to the Spirit, The Hundred could become the most aggressively marketed cricket product outside the IPL. And the audience they will market to hardest looks a lot like the readers of this page."""

arora_body = """Nikesh Arora does not do small. Since taking over Palo Alto Networks in 2018, the Indian-origin chief executive has turned a firewall vendor into the most acquisitive force in cybersecurity, and the past few months have been his most aggressive stretch yet. The company is in the middle of a $25 billion purchase of CyberArk, the identity-security specialist, and has just completed a $3.35 billion acquisition of Chronosphere, an observability platform. The common thread, in Arora's words, is simple: "the AI cycle is moving fast."

For a man who once ran Google's global business and briefly served as president of SoftBank, the strategy is characteristically blunt. AI agents, software that acts autonomously rather than waiting for human clicks, are about to flood enterprise networks. Every agent is a new identity to secure and a new failure point to monitor. Arora's bet is that the company defending all of it should be one vendor, not a dozen, ending what he calls "identity silos."

**Buying the AI security stack**

The CyberArk deal, announced last July and now beginning product integration, gives Palo Alto control of privileged-access management, the locks on the most sensitive accounts in any organisation. As part of it, the company plans a secondary listing on the Tel Aviv Stock Exchange under the ticker "CYBR," a nod to CyberArk's Israeli roots and Israel's status as a cybersecurity powerhouse.

Chronosphere, closed last week, adds observability, the ability to watch vast cloud systems in real time and spot when something breaks. Arora wants to fuse it with Cortex AgentiX, Palo Alto's agentic security platform, to move from passive dashboards to AI agents that detect, investigate and fix problems on their own. Chronosphere's co-founder Martin Mao has joined as general manager of observability. Together the deals show a company trying to own the entire security-and-monitoring stack for the AI era, not merely a slice of it.

**Why the diaspora should care**

Cybersecurity is one of the densest concentrations of Indian engineering talent in American tech, and Palo Alto, headquartered in Santa Clara, sits at the centre of it. A buying spree of this scale reshapes thousands of careers. Acquisitions bring integration, and integration brings both opportunity and risk: new senior roles for those who fit the agentic-AI roadmap, and redundancy for those whose products overlap. Indian professionals on H-1B visas, who fill a large share of security-engineering ranks across these firms, watch such consolidation closely, because a role eliminated in a post-merger reorganisation can start a 60-day clock on their immigration status.

There is an investment angle too. Palo Alto is one of the most widely held stocks in the diaspora's portfolios, a proxy for the broader cybersecurity boom that has minted fortunes during the AI wave. Arora's appetite for multibillion-dollar deals, funded partly by the company's soaring valuation, is the kind of capital-allocation bet that either compounds wealth or destroys it. The CyberArk price tag, $25 billion, is enormous even by today's standards, and integrating two large acquisitions at once is exactly the sort of execution challenge that has tripped up lesser managers.

For the NRI watching India's own cybersecurity ambitions, the Arora playbook is also a template. Indian firms and the government, stung by attacks like the recent FortiBleed breach that hit the country hard, are pouring money into homegrown security. The agentic-security architecture Arora is assembling, where AI defends against AI, is precisely the model India will have to import or imitate.

**What's next**

The immediate test is integration. Palo Alto is now absorbing two companies simultaneously while convincing customers that one platform is better than best-of-breed point products, a pitch the industry has heard, and doubted, before. The CyberArk acquisition still has to clear its final steps, and the Tel Aviv listing adds a new layer of complexity.

Arora has built his reputation on moving faster than the market and being proved right. The AI security wave he is betting on is real; the question is whether one company can swallow this much of it without indigestion. For the Indian American engineers building these systems and the investors funding them, the answer will shape both their paychecks and their portfolios."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Trump Said Apple Will Build Chips With Intel. Apple and Intel Said Nothing. That Silence Is the Story.",
        "subheadline": "A presidential post sent Intel's stock to a record, but the real shift is narrower, slower, and aimed at older chips. For Indian engineers and iPhone buyers alike, the memory crunch behind it lands closer to home.",
        "slug": make_slug("apple-intel-chip-deal-trump-foundry-memory-crunch-nri-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian engineers at Intel's US fabs could see a fresh hiring cycle after years of layoffs, while the AI-driven memory shortage behind the deal means pricier iPhones and MacBooks for every Indian American household.",
        "tags": ["semiconductors", "apple", "intel", "chips", "silicon-valley", "indian-tech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/trump-says-apple-partner-intel-us-chip-design-production"},
            {"name": "The Wall Street Journal", "url": "https://www.wsj.com/tech/intel-shares-surge-after-trump-announces-apple-partnership"},
            {"name": "The Motley Fool", "url": "https://www.fool.com/investing/intel-stock-soared-after-trump-said-apple-will-build-chips"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/intel-stock-trump-apple-customer"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/12-inch_silicon_wafer.jpg/1280px-12-inch_silicon_wafer.jpg",
        "image_caption": "A 12-inch silicon wafer of the kind used in advanced semiconductor manufacturing.",
        "image_attribution": "Wikimedia Commons",
        "body": apple_intel_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Nadella, Pichai and Arora Just Bought a Cricket Team at Lord's. They Outbid the IPL to Do It.",
        "subheadline": "A consortium of Indian-origin tech billionaires valued London Spirit at £295 million, beating Lucknow Super Giants owner Sanjiv Goenka in a four-hour auction. The diaspora's two great loves just merged onto one balance sheet.",
        "slug": make_slug("london-spirit-hundred-tech-consortium-nadella-pichai-arora-gajwani-nri-cricket"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The same Indian-origin CEOs the diaspora idolises in engineering now own a stake in cricket's spiritual home, building a bridge between English, Indian and American cricket aimed squarely at South Asian professionals in the US and UK.",
        "tags": ["indian-tech", "satya-nadella", "sundar-pichai", "nikesh-arora", "cricket", "the-hundred"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Cricbuzz", "url": "https://www.cricbuzz.com/cricket-news/microsoft-head-google-ceo-times-internet-vc-consortium-london-spirit"},
            {"name": "CricTracker", "url": "https://www.crictracker.com/sanjiv-goenka-rpsg-group-secure-manchester-originals-stake"},
            {"name": "Cricbuzz (Hundred sale)", "url": "https://www.cricbuzz.com/cricket-news/the-hundred-sale-ipl-owners-tech-giants-investors"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Lords-Cricket-Ground-Pavilion-06-08-2017.jpg/1280px-Lords-Cricket-Ground-Pavilion-06-08-2017.jpg",
        "image_caption": "The Pavilion at Lord's Cricket Ground in London, home of the London Spirit franchise.",
        "image_attribution": "Wikimedia Commons",
        "body": london_spirit_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Nikesh Arora Is Spending $28 Billion to Own the AI Security Stack. His Engineers Are Watching Closely.",
        "subheadline": "Palo Alto Networks is absorbing CyberArk and Chronosphere at once, a bet that one vendor should secure every human, machine and AI agent. For the Indian engineers who fill its ranks, consolidation cuts both ways.",
        "slug": make_slug("nikesh-arora-palo-alto-cyberark-chronosphere-agentic-security-nri-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Cybersecurity holds one of the densest concentrations of Indian engineering talent in US tech, and Arora's multibillion-dollar buying spree reshapes careers, H-1B job security and the diaspora's stock portfolios all at once.",
        "tags": ["cybersecurity", "nikesh-arora", "palo-alto-networks", "cyberark", "indian-tech", "agentic-ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CRN", "url": "https://www.crn.com/news/security/palo-alto-networks-completes-chronosphere-acquisition"},
            {"name": "StockTitan", "url": "https://www.stocktitan.net/news/PANW"},
            {"name": "Palo Alto Networks", "url": "https://www.paloaltonetworks.com/company/press/2025/palo-alto-networks-to-acquire-chronosphere"},
            {"name": "Morningstar", "url": "https://www.morningstar.com/news/pr-newswire/palo-alto-networks-cyberark"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
        "image_caption": "Palo Alto Networks chief executive Nikesh Arora speaking at TechCrunch Disrupt.",
        "image_attribution": "Wikimedia Commons",
        "body": arora_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  ~{wc} words | {art['headline'][:60]}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
