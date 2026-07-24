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

aia_body = """The Association of Indians in America's New York chapter has been honouring its own since Lyndon Johnson was president. Founded in 1967, it bills itself as the oldest national organisation of Asian Indians in the United States — a claim that, for a community whose American story is usually told as a post-1965 immigration arc, is itself a small piece of history. Its Annual Benefit Gala 2026, held at Terrace on the Park in Flushing, drew more than 300 guests and named seven honorees the chapter calls "Ratnas," or jewels.

The list reads like a cross-section of where the diaspora's first generation landed and excelled. Dr. Dattatreyudu Nori, an oncologist with five decades at Memorial Sloan Kettering and Cornell, has authored more than 300 scientific papers and this year added a Padma Bhushan to a shelf that already held the Padma Shri and the Ellis Island Medal of Honor. Dr. Sahil Khera, an interventional cardiologist at Mount Sinai, has performed more than 2,000 structural heart procedures. Dr. Aprajita Mattoo, a transplant nephrologist at NYU Langone, has worked on the historic pig-to-human kidney transplant trials.

## The shape of a community's elite

What the honours list quietly documents is how concentrated the Indian-American success story remains in a handful of professions. Of the seven Ratnas, four are physicians. The others — a diamond-trade entrepreneur and philanthropist, Manish Dhadda; an attorney, Jessica Kalra; and a Harvard MBA candidate building an AI startup, Pulkita Kini — gesture at where the next generation is headed, but medicine still dominates the room.

That is not an accident of taste. The 1965 Immigration and Nationality Act, which abolished national-origin quotas, favoured applicants with professional and technical skills, and the doctors and engineers who came through that door set the template their children were expected to follow. Galas like AIA-NY's are, in part, a ritual of self-definition: an evening where the community tells itself a story about what excellence looks like, and who gets to embody it.

## Civic weight, measured in attendance

The other story the gala tells is about access. The dignitaries who sent messages or appeared in person — New York State Comptroller Thomas DiNapoli, State Senator John Liu, Nassau County Executive Bruce Blakeman, Suffolk County Executive Edward Romaine, and representatives of the Indian Consulate in New York — are a rough index of how seriously local and state politics now take the South Asian vote in the tri-state area.

For an organisation that began as a cultural and mutual-aid society for a tiny immigrant population, the guest list is its own milestone. Indian-Americans now number an estimated 5.2 million, according to 2023 Census Bureau figures, and the politicians who once might have skipped a community banquet now compete for podium time at one.

AIA-NY used the evening to look forward as well. President Beena Kothari announced the chapter's 39th Deepavali Celebration and Live Fireworks, set for October at Overlook Beach on Long Island — a reminder that the same organisation handing trophies to surgeons also runs the public-facing festivals that introduce Indian culture to non-Indian neighbours.

## The generational handover

The most telling detail of the evening may have been its youngest honoree. Pulkita Kini, recognised before she has even finished her MBA, represents a shift the community's institutions are still learning to accommodate: a generation that measures success not in hospital appointments but in startups, venture rounds and the unglamorous work of building things that did not exist before.

Whether organisations founded in the 1960s can hold the loyalty of that generation is an open question. The children and grandchildren of the founders often feel a looser tie to the association model — they network through professional groups, alumni networks and Slack channels, not banquet halls. Honouring a 20-something AI founder alongside a Padma Bhushan oncologist is one way the old institutions are trying to stay relevant to the people they hope will inherit them.

For now, the formula still works. The tabla and sitar played, the awards were handed out, and a community that arrived in America on professional visas spent an evening celebrating the professions that brought it here — while keeping one eye, however tentatively, on what comes next."""

aus_body = """Ten Australians of Indian origin appear on the 2026 King's Birthday Honours List, and the citations read less like a roll call of celebrity than a map of how a migrant community embeds itself in the institutions of its adopted country. There are no cricketers or film stars here. There are doctors, a psychiatrist, a community organiser who has been at it for half a century, and the quiet machinery of institution-building that rarely makes headlines.

The honours, announced by Governor-General Sam Mostyn, matter to the diaspora precisely because they are conferred by the Australian state rather than by an Indian-community body honouring its own. They are a signal of belonging — recognition that the contributions being celebrated are Australian contributions, made by Australians who happen to trace their roots to India.

## Fifty years, one community

The clearest example is Chethicad Oommen Thomas, a Melbourne-based community leader who received the Medal of the Order of Australia (OAM) for service to the Indian community of Victoria. Thomas arrived in 1969 and spent the following decades doing the unglamorous work that turns a scattering of migrants into a community: he founded the Malayalee Association of Victoria in 1976, helped lead the Australia India Society of Victoria, set up the Victorian Indian Community Charitable Trust, and built out the Indian Orthodox Church network in the state.

That kind of half-century arc is the diaspora's hidden infrastructure. The festivals, associations and charitable trusts that newer migrants take for granted were, in most cases, willed into existence by a handful of early arrivals who had no template to follow.

## The professional class, formally recognised

Several honourees reflect the medical and academic concentration that characterises Indian migration to Australia, much as it does in the United States and Britain. Professor Valsamma Eapen, a child and adolescent psychiatrist, was appointed an Officer of the Order of Australia (AO) — a higher grade — for her internationally recognised research into ADHD, Tourette syndrome and autism. Professor Balasubramaniam Venkatesh, an intensive-care specialist, was made a Member of the Order of Australia (AM) for his work in critical-care medicine and infection control.

Dr. Abhishek Verma, a Melbourne general practitioner, received an OAM for medical administration and for service in migrant and refugee health, while Gold Coast plastic and reconstructive surgeon Dr. Dilipkumar Gahankari was similarly honoured.

## Why the numbers are rising

The presence of ten Indian-origin recipients is not a fluke. The Indian-born population is now the second-largest migrant community in Australia, having overtaken those born in China and trailing only the England-born. In Victoria alone there are more than 371,000 people of Indian descent, with the City of Wyndham home to a 65,000-strong Indian community.

As that population has grown and aged, more of its members have accumulated the decades of professional and civic service that honours lists reward. Recognition tends to lag migration by a generation — the people being decorated now are, in many cases, those who arrived in the 1970s and 1980s and spent careers building reputations.

## Soft power and self-image

For India, the list is a piece of diaspora diplomacy. The Indian High Commission in Australia was quick to publicise it on social media, congratulating "the 10 Australians of Indian origin recognised." New Delhi has increasingly treated diaspora achievement as an extension of national prestige, and a King's Birthday Honours list studded with Indian names serves that narrative neatly.

But the deeper meaning belongs to the community itself. For a diaspora still occasionally reminded that it is seen as a recent arrival, formal recognition by the Crown — however ceremonial the monarchy's role now is — carries a particular weight. It says that the work of healing patients, mentoring migrants and building community institutions is not a parallel ethnic activity but part of the national fabric.

The honours will be conferred at investiture ceremonies in the months ahead. The recipients will collect their medals, and the associations they built will keep running their festivals and trusts — the unspectacular continuity that, decade by decade, turns a migrant community into a permanent feature of the country it chose."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "America's Oldest Indian Association Just Honoured Seven of Its Own. Four Were Doctors.",
        "subheadline": "The AIA-NY benefit gala in Flushing celebrated a community's elite — and quietly revealed how narrow the diaspora's definition of success still is, even as a new generation pushes at the edges.",
        "slug": make_slug("aia-ny-benefit-gala-2026-ratnas-indian-american-honorees-diaspora-flushing"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The honours list of the oldest national Indian-American association is a ritual of self-definition for a community built on professional-visa migration — and a window into whether its founding-era institutions can hold the loyalty of a startup-minded next generation.",
        "tags": ["nri", "diaspora", "indian-american", "new-york", "community", "AIA"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/11/aia-ny-hosts-grand-annual-benefit-gala-2026-to-honor-individuals-for-outstanding-contributions/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/indian-american-lawmakers-urge-diaspora-to-enter-politics-amid-rise-in-anti-india-sentiment/article69730000.ece"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36121661/pexels-photo-36121661.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A Bharatanatyam dancer performs a classical Indian dance on stage, the kind of cultural showcase that anchors diaspora community galas.",
        "image_attribution": "Pexels",
        "body": aia_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Australia Just Honoured Ten Indian-Origin Citizens. None of Them Are Famous.",
        "subheadline": "The 2026 King's Birthday Honours List reads like a map of how a migrant community embeds itself — through doctors, psychiatrists and the half-century grind of building institutions nobody else would.",
        "slug": make_slug("indian-australians-2026-kings-birthday-honours-list-diaspora-oam-victoria"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Honours conferred by the Australian state — not by an Indian-community body — are a signal of belonging, recognising decades of professional and civic service by a migrant population that is now the country's second-largest.",
        "tags": ["nri", "diaspora", "australia", "indian-australian", "honours", "community"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "NewKerala", "url": "https://www.newkerala.com/news/2026/"},
            {"name": "Seattle Indian", "url": "https://www.seattleindian.com/"},
            {"name": "Australia India Institute (University of Melbourne)", "url": "https://aii.unimelb.edu.au/"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/15571947/pexels-photo-15571947.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Sydney's skyline, including the Opera House. Indians are now Australia's second-largest migrant community.",
        "image_attribution": "Pexels",
        "body": aus_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"… {art['slug']} | {wc} words")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
