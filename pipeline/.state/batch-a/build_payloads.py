#!/usr/bin/env python3
"""Build Supabase insert payloads for batch-a articles."""
import json, re, datetime, os, sys

BASE = os.path.expanduser("~/workspace/the-videshi-news/pipeline/.state/batch-a")

def word_count(html):
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text.split())

def read(n):
    with open(os.path.join(BASE, f"article{n}.html")) as f:
        return f.read()

now = datetime.datetime.now(datetime.timezone.utc).isoformat()

articles = [
    {
        "headline": "Russian drones kill 2 at Ukraine-Moldova border crossing; Zelenskyy demands global action",
        "subheadline": "Moscow's drones struck the Starokozache crossing in Odesa region and renewed attacks on Kyiv, a day after Russian drones violated Moldovan airspace and delayed Zelenskyy's flight to Norway.",
        "slug": "russian-drones-kill-2-ukraine-moldova-border-crossing-zelenskyy-demands-global-action",
        "category": "news",
        "tags": ["Ukraine", "Russia", "Moldova", "Zelenskyy", "border security", "drone strikes"],
        "sources": [
            {"name": "The Times of India", "url": "https://timesofindia.indiatimes.com/world/europe/russian-drones-kills-2-in-ukraines-moldova-zelenskyy-urges-stronger-global-response/articleshow/133960782.cms"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/europe/russian-drones-kill-injure-people-ukraine-moldova-border-crossing-2026-09-09/"},
            {"name": "CNN", "url": "https://www.cnn.com/2026/09/09/europe/zelensky-plane-almost-hit-drone-tuesday-norway-pm-intldsk-latam?cid=external-feeds_iluminar_meta"},
        ],
        "diaspora_angle": "Prolonged disruption of Black Sea and overland trade routes keeps upward pressure on global crude and freight costs felt by NRIs, while the safety of Indians still in Ukraine is a recurring concern.",
        "topic_id": "b20f4bfe-0602-4f2c-966f-992126784b20",
        "llm_score": 4,
        "n": 1,
    },
    {
        "headline": "Pakistan rules out immediate military action under Mecca pact after Houthi attacks",
        "subheadline": "Islamabad says no military response is under discussion following Houthi strikes on Saudi cities and energy infrastructure, but pledges it will act under the trilateral defence pact 'when time comes.'",
        "slug": "pakistan-rules-out-immediate-military-action-under-mecca-pact-after-houthi-attacks",
        "category": "news",
        "tags": ["Pakistan", "Houthis", "Saudi Arabia", "Mecca defence pact", "Middle East", "Turkey", "Iran"],
        "sources": [
            {"name": "The Times of India", "url": "https://timesofindia.indiatimes.com/world/pakistan/attack-on-one-is-attack-on-all-pakistan-warns-houthis-invokes-mecca-defence-pact/articleshow/133955778.cms"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/middle-east/pakistan-says-no-military-response-discussed-under-mecca-pact-over-houthi-2026-09-10/"},
            {"name": "Fox News", "url": "https://foxnews.com/world/iran-backed-terror-groups-latest-territorial-grab-threatens-second-global-shipping-chokepoint"},
        ],
        "diaspora_angle": "Millions of Indians live and work in Saudi Arabia and the wider Gulf; any widening of the conflict threatens their safety and remittance flows, while crude price spikes feed India's import bill.",
        "topic_id": "f89a8a52-07b5-47a8-b3ed-96fbe88d6794",
        "llm_score": 4,
        "n": 2,
    },
    {
        "headline": "'More or less' finalised: commerce secretary says India-US trade deal nears signing",
        "subheadline": "Rajesh Agrawal said the two sides are working on a framework for preferential market access bridging India's MFN tariffs and US executive tariffs, with signing to follow at an 'appropriate time.'",
        "slug": "more-or-less-finalised-commerce-secretary-says-india-us-trade-deal-nears-signing",
        "category": "news",
        "tags": ["India-US trade", "trade deal", "Rajesh Agrawal", "exports", "fintech", "free trade agreements"],
        "sources": [
            {"name": "The Times of India", "url": "https://timesofindia.indiatimes.com/business/india-business/more-or-less-finalised-india-us-trade-deal-nears-signing-says-commerce-secretary/articleshow/133962494.cms"},
            {"name": "IBEF", "url": "https://www.ibef.org/news/india-us-trade-deal-more-or-less-finalised-to-be-signed-at-appropriate-time-commerce-secretary-mr-rajesh-agrawal"},
            {"name": "Informist Media", "url": "https://informistmedia.com/MoneyWire/59384/Global-Fintech-Fest-2026-Trade-deal-with-US-will-be-signed-at-opportune-time-says-trade-secy"},
        ],
        "diaspora_angle": "Indian-American businesses and exporters stand to gain preferential US market access, while NRIs could benefit if fintech-driven remittance costs fall as the commerce secretary envisions.",
        "topic_id": "885058f1-2a98-42bd-8559-09d045d725f4",
        "llm_score": 4,
        "n": 3,
    },
    {
        "headline": "Rights groups condemn 'racist murder' of Manipuri singer in Delhi, demand racial-motive probe",
        "subheadline": "Civil society and human rights organisations say the mob killing of musician Chongtham Vikram Singh must be examined in the wider context of racial violence against people from Northeast India.",
        "slug": "rights-groups-condemn-racist-murder-of-manipuri-singer-in-delhi",
        "category": "news",
        "tags": ["Manipur", "Delhi", "racism", "human rights", "Northeast India", "Chongtham Vikram Singh"],
        "sources": [
            {"name": "The Times of India", "url": "https://timesofindia.indiatimes.com/india/human-rights-organisations-condemn-racist-murder-of-manipuri-singer-chongtham-vikram-in-delhi/articleshow/133962713.cms"},
            {"name": "LatestLY", "url": "https://www.latestly.com/agency-news/india-news-manipuri-musician-killed-kiren-rijiju-says-all-accused-arrested-chargesheet-to-be-filed-soon-7595042.html"},
            {"name": "LatestLY", "url": "https://www.latestly.com/agency-news/india-news-manipur-hundreds-hold-candlelight-vigil-in-imphal-to-pay-tribute-to-musician-chongtham-vikram-singh-7595852.html"},
        ],
        "diaspora_angle": "For the Northeastern diaspora abroad, the case is a measure of how India confronts racial violence at home, shaping how safe the community feels in Indian cities.",
        "topic_id": "548336da-78d6-4ce3-93c2-2a892bcffa16",
        "llm_score": 4,
        "n": 4,
    },
]

for a in articles:
    body = read(a.pop("n"))
    wc = word_count(body)
    payload = {
        "headline": a["headline"],
        "subheadline": a["headline"] and a["subheadline"],
        "body": body,
        "slug": a["slug"],
        "category": a["category"],
        "vertical": a["category"],
        "tags": a["tags"],
        "sources": a["sources"],
        "image_url": None,
        "image_caption": None,
        "image_attribution": None,
        "word_count": wc,
        "diaspora_angle": a["diaspora_angle"],
        "topic_id": a["topic_id"],
        "llm_score": a["llm_score"],
        "published_at": now,
        "article_type": "breaking",
        "status": "published",
    }
    out = os.path.join("/tmp", f"batcha_payload_{a['slug'][:30]}.json")
    with open(out, "w") as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f"{a['slug']}  wc={wc}  payload={out}")
