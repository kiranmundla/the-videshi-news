#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

env_file = Path.home() / ".env.supabase"
if not env_file.exists():
    env_file = Path.home() / "workspace" / ".env.supabase"
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

body1 = """The pitch from Capitol Hill this week was unusually blunt for a community that has long preferred to let its résumé do the talking. "If you don't have a seat at the table, you're on the menu," Congressman Raja Krishnamoorthi told a roomful of Indian-Americans on Tuesday. "And none of you can afford to be on the menu."

The Illinois Democrat was speaking at an event organised by the Foundation for India and Indian Diaspora Studies (FIIDS), and his message was less a celebration than a warning. Indian-Americans, he noted, are among the most educated and prosperous groups in the country. They are also, he argued, increasingly a target.

## A community on the defensive

"There is the rise of anti-Hindu, anti-Indian, anti-Desi hate," Krishnamoorthi said, urging the audience to stop spectating and start running. City council, state legislature, Congress—he was not fussy about the office, or the party. "I don't care if you're a Republican, Democrat, or Independent. I don't care who you are."

He was not alone in the appeal. Congressman Suhas Subramanyam, who in 2024 became the first Indian-American elected to Congress from the East Coast, said the surest way to address the community's problems was to have its people inside the rooms where decisions are made. Congressman Shri Thanedar, of Michigan, struck a darker note, warning that hostility toward immigrants generally was climbing and that the diaspora would have to stay united to weather it.

The concerns are not abstract. Indian-American advocacy groups have spent the past two years cataloguing a string of incidents: vandalism at Hindu temples, anti-Hindu graffiti, the disruption of religious gatherings, and organised campaigns opposing Indian representation in corporate America. None of it amounts to a pogrom, and the community remains spectacularly successful by almost every economic measure. But the gap between economic clout and political protection is precisely what the lawmakers were pointing at.

## The numbers behind the nudge

There is a logic to the timing. The Indian-American population stood at roughly 5.2 million in 2023, according to the US Census Bureau—about 1.5% of the country. Yet the community punches far above that weight, accounting for an outsized share of federal income taxes, a long list of Fortune 500 chief executives, and a heavy presence in medicine, technology and academia.

What it has not built, in proportion, is political muscle. For a first-generation diaspora that arrived to study and to work, electoral politics often felt like someone else's business—a distraction from the careers and the mortgages and the children's college applications that defined the immigrant bargain. The lawmakers on Tuesday were, in effect, asking the second generation to renegotiate that bargain.

The bipartisan cast of supporters underscored the point. Republican Senator Roger Marshall of Kansas used the platform to talk up a US-India trade agreement, framing closer ties as good for his state's farmers. Several Democrats—Sanford Bishop, James Walkinshaw, Brad Sherman and Bill Huizenga among them—pledged help on the issues that animate Indian-American households most directly, including the green-card backlog that traps hundreds of thousands of skilled workers in decades-long limbo.

## The generational question

For the diaspora, the FIIDS event crystallised a tension that has been building for years. Visibility, it turns out, cuts both ways. The same prominence that produces vice-presidents and tech titans also produces resentment, and a community that once measured success in private terms—a good school district, a paid-off home, a child in medical school—is being told that private success no longer buys public safety.

That is an uncomfortable shift for households built on the premise that hard work and a low profile were the surest route to belonging. The lawmakers' answer is that belonging now has to be claimed, not earned quietly. Whether the message lands may depend less on the immigrants in the room than on their American-born children, who grew up fluent in the country's politics in a way their parents rarely were.

Krishnamoorthi, for his part, left the audience with a caveat that drew laughs. Run for anything, he said—state house, state senate, Congress. "Although not in my congressional district."

The joke aside, the ask was serious, and the subtext unmistakable: a community that has spent decades proving it can succeed in America is being asked to prove it can govern it too."""

body2 = """When Iranian drones sparked a fire at an oil facility in the United Arab Emirates this week, injuring three Indian workers, the incident barely registered on global markets. For the roughly nine million Indians who live and work across the Gulf, it registered as something else entirely: a reminder that the region they had treated as a safe, tax-free haven has become, almost overnight, a frontier.

The conflict that erupted in late February, when the United States and Israel went to war with Iran, has scrambled the calculus for the largest single bloc of the Indian diaspora. The Gulf is home to more Indians than any other region on earth—around 3.5 million in the UAE alone—and for half a century the bargain was simple. Higher wages, no income tax, easy flights home, and a stability that the rest of the neighbourhood conspicuously lacked. The war has cracked the last part of that promise.

## From economic contributors to community backbone

What has been striking is how the diaspora responded. According to reports from the region, Indian community networks moved faster than formal systems when the missiles started flying. Informal support groups, business associations and resident-welfare committees mobilised to arrange temporary housing for stranded workers, coordinate transport for those relocating within the Gulf, and run community kitchens and emergency funds for the most exposed—daily-wage labourers, recent arrivals, and those whose employers had gone quiet.

Indian schools and cultural organisations in the UAE opened their premises as coordination hubs. In an information environment thick with rumour and doctored video, diaspora leaders also took on an unglamorous but vital role: pushing verified information into WhatsApp groups to keep panic from spreading. The result was a kind of people-driven stability that ran parallel to, and sometimes ahead of, official channels.

It also kept the Gulf functioning. Hospitals staffed by Indian doctors and nurses stayed open. Supply chains that lean heavily on Indian managers and operators held together. In ports and energy infrastructure, Indian technical staff quietly ensured the region's critical arteries did not seize up—a continuity that mattered not only to host governments but to a global economy nervously watching the Strait of Hormuz.

## The widening gap between two diasporas

The crisis has also exposed a fault line that prosperity usually papers over. The Indian presence in the Gulf is not one community but two, layered on top of each other. At the top are the professionals and entrepreneurs—doctors, engineers, financiers, the millionaires who have made Dubai one of the world's fastest-growing havens for mobile wealth. Beneath them are the labourers who built the skylines and now staff the oil facilities, often with few protections and fewer exits.

For the first group, the war is a question of risk management and property prices; some are already weighing whether to move capital, or families, elsewhere. For the second, it is existential. Migrant-rights advocates say few workers had access to bomb shelters, and many were simply stranded as airports closed and ticket prices soared. A coalition tracking the toll counts at least two dozen foreign workers killed in the Gulf since the war began, several of them at sea.

The cruel arithmetic facing a labourer is this: stay in a war zone where wages remain far higher than at home, or return to a poorer country where the same conflict has driven up prices. For one Bangladeshi worker killed in a March missile strike on his camp, the choice was made for him; he arrived home in a coffin. Indian labourers face the same brutal ledger.

## What it means for the homeland

India has reasons to watch closely beyond the safety of its citizens. Gulf remittances are a pillar of the national economy, part of the record $135 billion overseas Indians sent home last year. A prolonged disruption to Gulf employment would be felt not in boardrooms but in the small towns of Kerala, Andhra Pradesh and Uttar Pradesh that depend on those monthly transfers.

For now, a fragile ceasefire holds and traffic is creeping back through Hormuz. The UAE's envoys insist the region remains "resilient, open for business." The diaspora that built much of that business is, characteristically, getting on with it—while quietly recalculating just how safe the safe haven really is."""

body3 = """Most diaspora stories are about arrival—the first restaurant, the first temple, the first member of the community elected to something. The story of the Sindhis is about the opposite: a people who arrived everywhere precisely because they had nowhere left to return to. This summer, that scattered community is attempting something it has rarely managed in seven decades. It is trying to organise itself.

From July 2nd to 5th, the Sindhi Association of North America (SANA) will hold its 42nd annual convention at a hotel near Toronto's airport, under the theme "From Literacy to Light." It is the kind of gathering—cultural performances, youth programmes, a few visiting singers "subject to visa"—that hundreds of diaspora associations stage every summer across North America. But for the Sindhis, the convening carries an unusual weight, because it follows an ambitious attempt earlier this year to build something more permanent.

## A diaspora without a homeland to go home to

The Sindhi predicament is distinct within the broader Indian and South Asian story. When the subcontinent was partitioned in 1947, the province of Sindh went to Pakistan in its entirety. Hindu Sindhis, unlike Punjabis or Bengalis, did not move from one side of a new border to the other side of the same region; they left their homeland altogether, fanning out to Mumbai, to Gujarat, and then across the world to Hong Kong, Dubai, West Africa, Britain and the Americas.

The consequence is a community defined by mobility and commerce, famous for its entrepreneurial reach and infamous, within its own ranks, for its difficulty cohering. There is no Sindh to return to, no provincial government to lobby, no single religious centre to orient around. Language has frayed across generations raised in English, Hindi and a dozen host tongues. For a community that traces its lineage to the Indus Valley—the civilisation that gave the word "Hindu" and arguably "India" itself their names—the irony of fragmentation is not lost on its leaders.

## The push to institutionalise

That is the gap SANA and its partners are trying to close. In April, organisers convened what they billed as the inaugural International Sindhi Diaspora Conference in London, with the explicit goal of turning "fragmented efforts into a coordinated global movement." The headline deliverable was the proposed creation of INDUS—the International Diaspora Union of Sindhis—a permanent body intended to coordinate Sindhi organisations worldwide, alongside a "London Declaration" of shared principles.

The language is grand, and the targets—youth leadership, cultural preservation, a "unified global narrative"—are the familiar furniture of diaspora summits everywhere. The harder question is whether a community structurally inclined toward dispersal can sustain a central institution. Plenty of diaspora federations have launched with declarations and faded into dormant websites.

What gives the effort some plausibility is generational anxiety. The elders who carried Sindhi from the lost homeland are ageing out, and their grandchildren, comfortably American or Canadian or British, have little obvious reason to maintain a language and identity their friends have never heard of. The Toronto convention's literacy theme is a direct response: an admission that without deliberate transmission, the culture simply evaporates.

## A test case for the wider diaspora

For the broader Indian diaspora, the Sindhi experiment is worth watching as a kind of accelerated preview. Every immigrant community eventually confronts the same arithmetic—the founding generation's fierce attachment giving way to a second generation's selective interest and a third's polite indifference. Most groups still have the cushion of a homeland to renew the bond: a village to visit, a state to invest in, a passport's worth of belonging to fall back on.

The Sindhis do not. They are running the assimilation experiment without a safety net, which makes their attempt to build durable global institutions both more urgent and more instructive. If a homeland-less, commerce-minded, famously decentralised community can manufacture cohesion through sheer organisational will, it offers a template for diasporas that still take their continuity for granted.

The convention in Toronto will not answer that question in a weekend. But the fact that it is being asked—earnestly, and with an actual institution attached—marks a quiet shift for a people who have spent generations succeeding as individuals while struggling to act as one."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "‘On the Menu’: Indian-American Lawmakers Tell the Diaspora to Stop Watching and Start Running for Office",
        "subheadline": "At a Capitol Hill event, three Indian-American congressmen warned that economic success no longer buys political protection, and urged the community to seek power at every level of government.",
        "slug": make_slug("indian-american-lawmakers-fiids-capitol-hill-run-for-office-anti-india-hate"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For a first-generation diaspora that arrived to study and work, these lawmakers are asking the community to trade quiet, private success for visible political power as anti-India and anti-Hindu incidents rise.",
        "tags": ["nri", "diaspora", "indian-american", "politics", "civic-engagement", "usa"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/world/indian-american-lawmakers-urge-diaspora-to-enter-politics-amid-rise-in-anti-india-sentiment/article71140524.ece"},
            {"name": "Indiaspora / US Census Bureau (population and tax data)", "url": "https://indiaspora.org/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/aa/Raja_Krishnamoorthi_official_photo.jpg",
        "image_caption": "Congressman Raja Krishnamoorthi, who urged Indian-Americans to run for public office at a FIIDS event on Capitol Hill.",
        "image_attribution": "Wikimedia Commons",
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Gulf Was the Diaspora's Safe Haven. A War Is Forcing 9 Million Indians to Recalculate.",
        "subheadline": "As conflict reshapes West Asia, Indian community networks have become a quiet backbone of mutual aid, even as the divide between the diaspora's professionals and its labourers grows starker.",
        "slug": make_slug("indian-diaspora-gulf-west-asia-conflict-mutual-aid-migrant-workers-uae"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Gulf holds the largest single bloc of overseas Indians and a pillar of India's $135bn in remittances; the war is testing both their physical safety and the unspoken bargain that drew them there.",
        "tags": ["nri", "diaspora", "gulf", "uae", "remittances", "migrant-workers", "west-asia"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "IANS / newkerala.com — Indian diaspora stabilises Gulf", "url": "https://newkerala.com/news/2026/"},
            {"name": "Associated Press (via KSAT) — Iran war and Gulf foreign workers", "url": "https://www.ksat.com/"},
            {"name": "Reuters — India File: Rupee gets diaspora lifeline", "url": "https://www.reuters.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/692102/pexels-photo-692102.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The Dubai skyline at dusk; nearly 3.5 million Indians live and work in the United Arab Emirates.",
        "image_attribution": "Pexels",
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Diaspora With No Homeland to Return To Is Trying to Build One in the Cloud",
        "subheadline": "As Sindhis gather in Toronto this July, the community is attempting something it has rarely managed in 70 years of dispersal: a permanent global institution to hold itself together.",
        "slug": make_slug("sindhi-diaspora-sana-convention-toronto-indus-london-declaration-identity"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Sindhis run the assimilation experiment without the safety net of a homeland, making their fight to preserve language and identity an accelerated preview of what every Indian diaspora community eventually faces.",
        "tags": ["nri", "diaspora", "sindhi", "community-organization", "canada", "cultural-preservation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Sindhi Association of North America — 42nd Convention", "url": "https://sanaonline.org/42nd-convention-2026/"},
            {"name": "Sindhi Association of North America — Diaspora Conference 2026", "url": "https://sanaonline.org/diasporaconference2026/"},
            {"name": "Pak Prism — SANA to hold International Sindhi Diaspora Conference in London", "url": "https://pakprism.com/"}
        ]),
        "score_total": 68,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/34755223/pexels-photo-34755223.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Members of the South Asian diaspora gather at a community cultural event.",
        "image_attribution": "Pexels",
        "body": body3
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"… {art['slug']} ({wc} words)")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
