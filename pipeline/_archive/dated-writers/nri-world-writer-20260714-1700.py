#!/usr/bin/env python3
"""NRI World Writer — July 14, 2026 5:00 PM PT run"""
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
        "headline": "India's Tricolour in Boston Harbour: The Three-Masted Barque That Sailed Into America's Birthday Party",
        "subheadline": "INS Sudarshini, a 513-ton sail training ship on a ten-month transoceanic odyssey, docked at Boston Fish Pier for the Sail250 celebrations — and the public can walk aboard through July 15.",
        "slug": make_slug("ins-sudarshini-sail-boston-250-lokayan-indian-navy-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "India's naval sailing vessel is docked in Boston through July 15, giving NRIs in New England a rare chance to walk the decks of an active Indian warship — a floating embassy of maritime heritage at America's 250th birthday.",
        "tags": ["nri", "diaspora", "indian-navy", "sail-boston", "sail250", "maritime", "india-us-relations", "lokayan"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/law-order/3353019-ins-sudarshini-brings-indias-maritime-heritage-to-boston"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/07/12/ins-sudarshini-joins-sail-boston-250-celebrations/"},
            {"name": "Press Information Bureau, Ministry of Defence", "url": "https://pib.gov.in/PressReleaseIframePage.aspx?PRID=2216218"},
            {"name": "asiaPOST / IANS", "url": "https://asiapost.in/ins-sudarshini-heads-to-boston-carrying-forward-indian-navys-message-of-maritime-friendship/"},
            {"name": "Sail Boston 2026", "url": "https://sailboston.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/INS_Sudarshini_at_the_Sail250_Virginia_Parade_of_Sails.jpg/1280px-INS_Sudarshini_at_the_Sail250_Virginia_Parade_of_Sails.jpg",
        "image_caption": "INS Sudarshini flying the Indian tricolour during the Sail250 Parade of Sails off the Virginia coast",
        "image_attribution": "Wikimedia Commons",
        "body": """For five days this week, the waterfront of Boston — birthplace of the American Revolution, cradle of the republic — belongs to more than sixty tall ships from over twenty nations, their masts a forest of rigging against a skyline of glass and steel. Among them, flying the saffron, white and green, sits INS Sudarshini, the Indian Navy's three-masted barque and perhaps the most quietly dramatic symbol of how far India's maritime diplomacy has travelled.

Sudarshini — the name means "beautiful lady," after Sundari Nanda, half-sister of the Buddha — arrived in Boston on July 12, sailing past Castle Island and the Seaport District before docking at Boston Fish Pier. India's Consul General in Boston, Raghuram Sastry, boarded the ship at sea for the Grand Parade of Sails, the ceremonial procession that opened Sail Boston 2026. "INS Sudarshini entered historic port of Boston flying tricolour in the majestic Parade of Sails," the Consulate General posted on X, calling it a moment that "underscored India's rich maritime heritage and maritime cooperation between India and US."

The event is part of Sail250, the sweeping, five-city maritime festival marking America's semiquincentennial — two hundred and fifty years since the Declaration of Independence. Since late May, the international fleet has gathered at New Orleans, Norfolk, Baltimore, and New York before making Boston its final and grandest stop. The New York segment alone, held over the Fourth of July weekend, drew an estimated six million spectators and roughly fifteen thousand sailors, making it the largest maritime gathering in United States history. Boston expects four million visitors by the time the ships depart on July 16.

## A ten-month voyage, eighteen ports, thirteen countries

Sudarshini's appearance in Boston is no detour. The 513-ton barque is midway through Lokayan 2026, a ten-month transoceanic expedition flagged off from Kochi on January 20 by Vice Admiral Sameer Saxena of the Southern Naval Command. The route spans 22,000 nautical miles and eighteen foreign ports across thirteen countries — a deployment the Indian Ministry of Defence has called "a powerful symbol of cultural diplomacy, reaffirming the Indian Navy's commitment to building bridges of cooperation and mutual trust across nations."

More than two hundred Indian Navy and Coast Guard trainees are aboard at any given time, rotating through intensive sail training in long-range ocean navigation and traditional seamanship. At each port — from Alexandria and Malta to Sète in the south of France — the crew has hosted professional exchanges and courtesy calls with foreign navies, embodying the Indian doctrine of *Vasudhaiva Kutumbakam*, the world as one family.

The American leg of Lokayan 2026 has been the most high-profile yet. INS Sudarshini joined the Sail250 Virginia celebrations in Norfolk from June 19 to 23, then sailed through the Chesapeake and Delaware Canal to Baltimore. On July 4, she participated in the International Naval Review in New York, passing the Statue of Liberty and proceeding up the Hudson in a Parade of Sail alongside vessels from thirty nations. The Indian Embassy described the three-masted barque as "a symbol of India's maritime heritage flying the tricolour in the Parade of Sail on the Hudson River."

## Walk the deck of an Indian warship — through Tuesday

For the Indian diaspora in New England — a population of roughly three hundred thousand, according to the Ministry of External Affairs — the Boston stopover offers something unusual: a chance to walk the decks of an active Indian naval vessel on American soil. Public open days at Boston Fish Pier run from July 12 to 15, with visitors free to explore the ship and speak with crew members about India's naval traditions. No tickets are required; access is part of the broader Sail Boston programme on a first-come, first-served basis.

The vessel itself has a story worth the walk. Built by Goa Shipyard Limited and commissioned in January 2012, she was designed by the British naval architect Colin Mudie and carries 1,035 square metres of sail. Her twin Kirloskar Cummins diesel engines take over when the wind fails. She has already covered more than 140,000 nautical miles across deployments spanning ASEAN, the Mediterranean, and now the Atlantic.

## A floating embassy at a historic moment

India's presence at Sail250 fits a broader pattern. Prime Minister Modi launched the "Chalo India" global diaspora campaign earlier this year, urging overseas Indians to become tourism ambassadors. The India-US strategic partnership, already layered with defence agreements and technology collaborations, now extends to maritime heritage on the Boston waterfront. And the ship herself is a product of that partnership's most tangible thread — the idea that friendship between nations is, at its most basic, about people walking one another's decks.

INS Sudarshini is expected to depart Boston on July 16, continuing her journey back across the Atlantic toward Kochi, where Lokayan 2026 will conclude later this year."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
