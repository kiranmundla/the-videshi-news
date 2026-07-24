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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Forty-One Years On, the Diaspora Still Gathers for Air India 182. The State Mostly Doesn't.",
        "subheadline": "On June 23, families lit candles from Stanley Park to Ahakista for the 329 people killed in the world's deadliest act of aviation terrorism before 9/11 — a grief that built Canada's South Asian community and a justice it never received.",
        "slug": make_slug("air-india-182-flight-41st-anniversary-memorial-kanishka-bombing-diaspora-canada-ireland-nri"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The 1985 Air India bombing killed 268 Canadians, most of them of Indian origin, and remains the deadliest terror attack in Canadian history — a foundational wound for the Indo-Canadian community, whose families have spent four decades organizing memorials and fighting the perception that their dead were treated as a foreign tragedy rather than a Canadian one.",
        "tags": ["air-india-182", "kanishka", "indo-canadian", "diaspora", "memorial", "canada", "ireland"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Air India Flight 182 Archive, McMaster University", "url": "https://airindiaflight182.humanities.mcmaster.ca/"},
            {"name": "Air India Victims' Families Association", "url": "https://airindiaflight182.humanities.mcmaster.ca/"},
            {"name": "Wikipedia – Air India Flight 182", "url": "https://en.wikipedia.org/wiki/Air_India_Flight_182"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Air_India_Flight_182_Memorial%2C_Toronto%2C_Canada.jpg/1280px-Air_India_Flight_182_Memorial%2C_Toronto%2C_Canada.jpg",
        "image_caption": "The Air India Flight 182 memorial at Humber Bay Park East in Etobicoke, Toronto",
        "image_attribution": "Wikimedia Commons",
        "body": """On the morning of June 23, in five Canadian cities and on a windswept headland in southwest Ireland, families gathered again to read the same 329 names. In Toronto they came to the sundial at Humber Bay Park, where the sea-facing memorial is engineered so that on each anniversary the sun's shadow falls across the inscription at the exact moment the plane went down. In Ottawa, Montreal, Vancouver and at Ahakista in County Cork, the ritual was the same: wreaths, candles, and the long, deliberate recitation of every person lost. This was the 41st year they have done it.

The Air India Victims' Families Association organizes the services, as it has for four decades, and the arithmetic of who attends has changed. The parents who lost children are mostly gone now. The mourners are increasingly the siblings, the cousins, the second generation — people who were small in 1985 or not yet born, keeping a vigil they inherited.

## What was lost

On June 23, 1985, a bomb planted by extremists from the Babbar Khalsa, a Sikh separatist group based in Canada, detonated in the cargo hold of a Boeing 747 named *Emperor Kanishka* as it cruised off the Irish coast. All 329 people aboard were killed. The dead included 268 Canadian citizens, 27 British nationals and 22 Indians — and the overwhelming majority of the Canadians were of Indian origin: families flying home for the summer, university students, 86 children.

It remained the deadliest act of aviation terrorism anywhere in the world until September 11, 2001, and it is still the worst terrorist attack in Canadian history. Yet for years many Canadians filed it away as something that had happened to *Indians*, on an *Indian* airline, in *Indian* airspace of the imagination — a foreign event that landed, by some accident of routing, in Canadian obituary columns.

## A grief that was treated as foreign

That misclassification is the wound the diaspora has spent forty years trying to close. The plane took off from Toronto. The bomb was built in British Columbia. The victims paid Canadian taxes and held Canadian passports. But the investigation that followed was, in the words of a later public inquiry, a "cascading series of errors" — jurisdictional confusion, intelligence not shared between the RCMP and Canada's spy agency, surveillance tapes erased. After a two-decade investigation and the most expensive trial in Canadian history, only one man was convicted, of manslaughter, for building the bombs. The two principal accused were acquitted in 2005.

Justice John Major, who led the federal inquiry that reported in 2010, concluded that the bombing was the result of preventable failures and that the families had endured "exceptional and unacceptable" treatment afterward — made to feel, as many testified, that they were grieving a problem India should handle rather than fellow citizens Canada had failed to protect.

## Why the diaspora keeps the date

For Indo-Canadians, the anniversary is therefore about two things at once. It is mourning, plainly. But it is also an annual insistence on a fact the country was slow to accept: that this was a Canadian atrocity against Canadian families, and that the South Asian community's dead belong to the national story, not the margins of it.

That insistence has slowly been answered. There are now permanent memorials in Toronto, Vancouver, Ottawa, Montreal and Ireland, and June 23 was designated a National Day of Remembrance for Victims of Terrorism in Canada. Prime ministers have attended Ahakista; the Irish village has cared for the cliffside garden for forty-one years with a tenderness the families never forget.

For the broader diaspora, the lesson of Air India 182 has outlived the headlines. It is a case study in how an immigrant community's pain can be quietly externalized as someone else's — and in how that community refused, year after year, to let the names be rounded down to a footnote. Four decades on, the candles at Humber Bay are lit not only for the dead, but for the principle that they were Canadians, and were owed more.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian-Australians Give Generously. A New Study Wants to Know Why So Little of It Is Counted.",
        "subheadline": "Now the largest overseas-born group in Australia, the community gives out of faith, family and duty — but mostly outside the formal channels that track, deduct and amplify philanthropy. Researchers think that is a missed opportunity worth measuring.",
        "slug": make_slug("indian-australian-diaspora-philanthropy-study-myriad-per-capita-giving-nri"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indians are now the largest overseas-born community in Australia, yet their considerable charitable giving is largely invisible to the formal philanthropic sector because it flows through temples, family networks and remittances home rather than registered foundations — a gap a new research effort aims to map, with implications for how the diaspora's wealth shapes both Australian causes and India.",
        "tags": ["australia", "diaspora", "philanthropy", "giving", "indian-australians", "nri-world"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "Per Capita – think tank research", "url": "https://percapita.org.au/"},
            {"name": "DFAT – Australia's Indian Diaspora: A National Asset", "url": "https://www.dfat.gov.au/"},
            {"name": "Philanthropy Australia", "url": "https://www.philanthropy.org.au/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/11094777/pexels-photo-11094777.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Performers play traditional drums at an Indian community cultural festival",
        "image_attribution": "Pexels / Swastik Arora",
        "body": """There is a particular kind of giving that does not show up in any spreadsheet. An envelope pressed into a hand at a temple in Melbourne. A few thousand dollars wired to a school back in Gujarat. A community whip-round for a family hit by a medical bill. By every account, Indian-Australians do an enormous amount of it. By almost every formal measure, none of it exists.

That invisibility is the puzzle a new wave of research, championed by the philanthropic advisory group Myriad Australia in partnership with the progressive think tank Per Capita, is setting out to address. The premise is simple and slightly provocative: one of the country's largest and fastest-growing communities is also one of its most generous, and the formal philanthropic sector has almost no idea how to see it, count it, or work with it.

## The community that became the largest

The context has shifted faster than the institutions have. India is now the largest single source of Australia's overseas-born population, having overtaken England and China — a community approaching a million people, young, well-educated and increasingly affluent. It is concentrated in exactly the professions, technology, medicine, finance, that generate disposable wealth.

What it has not done, by and large, is route its generosity through the registered foundations, donor-advised funds and structured bequests that the Australian philanthropic establishment recognizes as "philanthropy." The giving is real and substantial. It simply travels along older roads.

## Faith, family and duty — not the tax deduction

This is the finding that earlier work, including Dr Wesa Chau's 2018 study of Asian-Australian diaspora philanthropy, had already begun to surface, and which the new research builds on. Indian-Australians tend to give for reasons rooted in religion, kinship and a sense of obligation — *seva*, *dana*, *zakat*, the dharmic and faith traditions that frame giving as duty rather than discretionary largesse.

The motivations carry practical consequences. Much of the money flows to temples and gurdwaras, to family members directly, or back to causes in India — schools, hospitals, village development — rather than to Australian charities. And because it moves through informal channels, donors frequently miss the tax-effective structures that would let a dollar given become more than a dollar received. Many, researchers note, are simply unaware that such channels exist, or find that the ones that do are not built for cross-border giving to India.

## The friction at the border

That cross-border dimension is where good intentions meet hard regulation. Sending charitable money from Australia to India runs into the Foreign Contribution Regulation Act, India's increasingly strict law governing foreign donations to Indian organizations. FCRA compliance has tightened sharply in recent years, and many Indian NGOs have lost their registration to receive foreign funds at all. For a diaspora donor in Sydney who wants to support a cause back home, the result is a maze: the gift may be legal in Australia and blocked in India, deductible in neither.

## Why mapping it matters

The case the researchers and bodies like Philanthropy Australia are making is not that the community should give differently. It gives plenty. It is that a community this large and this generous represents, in the dry language of the sector, an enormous untapped resource for Australian civil society — and that the diaspora itself loses out when its giving is unstructured, untracked and unleveraged.

The Australian government has begun to notice the broader picture. A Department of Foreign Affairs and Trade report, "Australia's Indian Diaspora: A National Asset," framed the community as central to the bilateral relationship, and separate academic work from the University of Queensland, Deakin and Griffith has mapped Indian-Australians' rising presence across business, medicine, academia and public life.

Philanthropy is the missing chapter. If the new research succeeds, it will do something modest but useful: make visible a flow of generosity that has always been there, and give a community that gives instinctively the tools to give strategically — to its adopted country and, where the law allows, to the one it came from.
"""
    }
]

print(f"Inserting {len(articles)} NRI World articles...\n")
for art in articles:
    wc = len(art["body"].split())
    try:
        res = sb_post("p2_articles", art)
        print(f"✅ [{wc} words] {art['headline'][:60]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['headline'][:60]}... → {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   {e.response.text[:300]}")
    print()
