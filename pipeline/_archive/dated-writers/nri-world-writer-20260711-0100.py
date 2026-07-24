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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Minister Called Them a 'Butter Chicken Tsunami.' A Preacher Threatened to Burn Their Temples. Then New Zealand Rolled Out the Red Carpet.",
        "subheadline": "As Modi and Luxon elevated ties to a strategic partnership and 10,000 cheered at Auckland's Spark Arena, New Zealand's 300,000 Indians confronted a parallel reality — one defined by 4,767 hate incidents, death threats, and a political appetite for anti-migrant rhetoric.",
        "slug": make_slug("nz-anti-indian-hate-butter-chicken-tsunami-modi-strategic-partnership"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "New Zealand's 292,000-strong Indian diaspora faces the sharpest disconnect in the democratic world: courted as strategic partners at the state level while enduring the highest rate of racially motivated abuse in the country. The story maps the lived experience of Indians navigating hate crimes, political slurs, and temple threats in a nation that simultaneously seeks their trade, their talent, and their tourism dollars.",
        "tags": ["nri", "diaspora", "new-zealand", "hate-crime", "anti-indian", "modi", "racism"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/new-zealand-india-upgrade-ties-pm-modi-visits-auckland-2026-07-11/"},
            {"name": "TBS News / AFP", "url": "https://www.tbsnews.net/world/modi-visits-new-zealand-trade-deal-sparks-india-pushback-1484686"},
            {"name": "Radio New Zealand", "url": "https://www-green.cache-blue.aws.rnz.net.nz/news/national/588448/south-asians-most-targeted-by-racial-abuse-police-hate-crime-data-reveals"},
            {"name": "Madhyamam Online", "url": "https://madhyamamonline.com/world/hate-graffiti-targeting-indians-seen-outside-an-auckland-school-1511380"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Auckland_skyline_-_May_2024_%282%29.jpg/1200px-Auckland_skyline_-_May_2024_%282%29.jpg",
        "image_caption": "The Auckland skyline, where PM Modi addressed Indian New Zealanders at the Kia Ora Modi event at Spark Arena",
        "image_attribution": "Wikimedia Commons",
        "body": """The optics at Spark Arena on Saturday could not have been more celebratory. An estimated ten thousand members of New Zealand's Indian diaspora packed Auckland's largest indoor venue for the "Kia Ora Modi" event — a community reception for Prime Minister Narendra Modi that had been four decades in the making. The last time an Indian prime minister set foot in New Zealand was 1986, when Rajiv Gandhi visited. For a community that has swelled from a few thousand to roughly 292,000 in the years since, this felt like a vindication.

Hours earlier, Modi and his counterpart Christopher Luxon had elevated bilateral relations to a "strategic partnership," signed a defence cooperation arrangement, and pledged deeper collaboration on maritime security in the Indo-Pacific. A free-trade agreement, sealed in April, is expected to pass New Zealand's parliament. By every diplomatic yardstick, the visit was a triumph.

But the Indians cheering inside the arena know a country the bilateral communiqués rarely describe.

## 'You're in my country, you're my servant'

In April, "Kill All Indians" was spray-painted in red on the footpath outside Papatoetoe Central School in South Auckland. Police treated it as a hate-motivated offence. The school's principal, Raj Dullabh, called it "deeply saddening." Indian-origin MP Parmjeet Parmar — herself a target of racially tinged mockery during a haka competition earlier this year — called it "vile and cowardly."

The graffiti was not an isolated act. According to New Zealand Police hate-crime data, 4,767 hate incidents involving South Asian victims were reported between January 2022 and October 2025 — making South Asians the country's most frequently targeted group. Among them was Auckland bus driver Rajnish Trehan, whose passenger told him he was a "servant" before smashing out four of his teeth in September 2024. Trehan left public transport to drive school buses instead, but the trauma lingers.

"You can heal yourself physically," Trehan told Radio New Zealand, "but when you get emotionally hurt, it's very hard to come out from those emotions."

## From parliament to the pulpit

What distinguishes New Zealand's anti-Indian climate is how far up the ladder the rhetoric reaches. Shane Jones, a government minister from the populist New Zealand First party — part of Luxon's own ruling coalition — dismissed the India free-trade deal's migration provisions with a phrase that became instantly infamous: "I don't care how much criticism we get, I am just never going to agree with a butter chicken tsunami coming to New Zealand."

An Indian community leader called the remark "outright racism." New Zealand's Race Relations Commissioner condemned it.

Then came Brian Tamaki, a self-proclaimed evangelical "apostle," who used Modi's impending arrival as an occasion to issue an eliminationist threat. "Let's purge New Zealand of Hindus, Sikhs and Muslims," Tamaki said on Instagram. "While we're at it, if they're burning churches down, why don't we burn mosques and their temples down? Tit for tat." The Race Relations Commissioner called his comments "utterly appalling."

In May, a far-right group disrupted a Sikh procession in Auckland's Manurewa suburb with Christian slogans and a confrontational haka — reportedly the third such incident targeting the Indian community that year. Massey University anthropologist Sita Venkateswar summed up the pattern: "A 'butter chicken tsunami,' slurs set to a haka, graffiti on a school wall — South Asians are already the most frequent targets of racially motivated incidents in our data. That is real and it is wrong."

## A growing community, a narrowing space

New Zealand's Indian population has surged. The 2023 census recorded roughly 292,000 Indians — about 5.5 per cent of the country's 5.3 million people. Many are students, tech professionals, and healthcare workers who arrived in the past decade. Their visibility has made them a flashpoint in an immigration debate where politicians, including those inside government, push for tighter migrant controls.

Luxon himself has struck a welcoming tone, calling the Modi visit "a winning partnership between New Zealand and India — one that delivers for our people and supports greater prosperity and security for both our countries." But the disconnect between the prime ministerial embrace and the street-level hostility is jarring. Indians in New Zealand are simultaneously courted as strategic partners and scapegoated as cultural invaders.

The strategic partnership is welcome. The free-trade deal may deliver jobs and investment. But the real test of New Zealand's relationship with its 300,000 Indians will not be measured in communiqués or trade data. It will be measured in whether a bus driver can finish his shift without losing his teeth — and whether a child can walk past her school wall without reading a death wish painted in red."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        print(f"   Headline: {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
