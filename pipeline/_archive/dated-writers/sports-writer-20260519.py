#!/usr/bin/env python3
"""Sports writer — 2 articles + topic status updates for 2026-05-19 run."""
import json, os, subprocess, uuid, hashlib
from datetime import datetime, timezone

# Load env
env = {}
with open(os.path.expanduser("~/.env.supabase")) as f:
    for line in f:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k] = v

SB_URL = env["SUPABASE_URL"]
SB_KEY = env["SUPABASE_SERVICE_ROLE_KEY"]
REST = f"{SB_URL}/rest/v1"
HEADERS = [
    "-H", f"apikey: {SB_KEY}",
    "-H", f"Authorization: Bearer {SB_KEY}",
    "-H", "Content-Type: application/json",
    "-H", "Prefer: return=representation",
]

def sb_post(table, data):
    """Insert row into Supabase."""
    cmd = ["curl", "-s", "-X", "POST", f"{REST}/{table}"] + HEADERS + ["-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(r.stdout) if r.stdout else None

def sb_patch(table, filter_str, data):
    """Patch rows matching filter."""
    cmd = ["curl", "-s", "-X", "PATCH", f"{REST}/{table}?{filter_str}"] + HEADERS + ["-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout

now = datetime.now(timezone.utc).isoformat()

# ── ARTICLE 1: BBL Chennai Opener ──────────────────────────
article1_id = str(uuid.uuid4())
article1_slug = "big-bash-league-chennai-opener-chepauk-bcci-cricket-australia-20260519"
article1 = {
    "id": article1_id,
    "headline": "Chepauk Goes Antipodean: Why the Big Bash League's India Debut Matters More Than a Single Match",
    "subheadline": "BCCI's green light for the BBL's first overseas fixture at Chennai signals a new era of franchise cricket diplomacy — and a commercial gateway that could reshape how Australian cricket courts Indian money",
    "slug": article1_slug,
    "category": "sports",
    "content": """The Big Bash League is coming to India. Cricket Australia has received formal approval from the Board of Control for Cricket in India to stage the opening match of the BBL 2026-27 season at the M.A. Chidambaram Stadium in Chennai — popularly known as Chepauk — in December this year. It will be the first time the Australian T20 domestic competition has ever held a regular-season fixture outside its home borders.

A five-member delegation from Cricket Australia has already arrived in Chennai to assess the venue's outfield, broadcast infrastructure, pitch preparation timeline, and corporate hospitality setup. The match is expected to feature the Perth Scorchers, defending BBL champions, whose home time zone sits just two-and-a-half hours ahead of Indian Standard Time — a broadcast scheduling gift that makes the game viable for simultaneous Australian and Indian audiences.

## The Commercial Logic

This is not an exhibition. The Chennai fixture is a carefully calculated move tied to Cricket Australia's ambitions to partially privatise the BBL. Under a proposal circulated to Australian state cricket boards in March 2026, CA is seeking to sell minority stakes of up to 49 per cent in BBL franchises to private investors. The estimated total valuation sits between A$394 million and A$525 million.

The most obvious buyers? IPL franchise owners. Indian-backed ownership groups already run teams across SA20 in South Africa, the ILT20 in the UAE, Major League Cricket in the United States, and the Caribbean Premier League. The BBL's privatisation would extend this global footprint into the last major T20 market without Indian capital.

Staging the opener in Chennai — MS Dhoni's spiritual fortress, a city that bleeds cricket — gives potential Indian investors and sponsors a front-row seat to the product they are being asked to buy into. It is a sales pitch disguised as a cricket match.

## The BCCI Calculus

For the BCCI, granting permission is its own power play. India's cricket board has historically resisted allowing foreign domestic leagues to operate on its soil, viewing it as a commercial threat to the IPL's monopoly on the Indian T20 audience. That the BCCI has now said yes speaks to a broader strategic shift under the leadership structure shaped by Jay Shah's tenure: India positions itself not as a gatekeeper blocking competition, but as the marketplace that every league must eventually pass through.

The quid pro quo is implicit. Cricket Australia needs Indian fans, Indian broadcasters, and Indian investors. India needs Australia's cooperation on the international calendar — particularly as the BCCI pushes for a larger IPL window in the ICC's post-2027 Future Tours Programme. The BBL opener in Chennai is a handshake that serves both.

## What NRIs Should Watch

For the Indian diaspora in Australia — estimated at over 900,000 people, making Indians the fastest-growing migrant group — the BBL has always occupied a peculiar space. It is accessible, affordable, and local, yet feels detached from the cricketing ecosystem they grew up in. A BBL match at Chepauk collapses that distance.

It also raises practical questions. Will BBL streaming rights in India expand beyond the current patchwork? Could future seasons see more matches in Indian cities, or even a full "India leg"? And for NRI fans watching from Sydney, Melbourne, and Perth: could the team they cheer for on summer evenings at the MCG soon be part-owned by the same groups that run their IPL favourites?

The Western Australia Cricket Association has already signalled openness to investment from Indian business conglomerates. If the privatisation process clears state-level approvals — New South Wales and Queensland have pushed back — the BBL could soon look a lot less Australian and a lot more IPL.

## The Bigger Picture

Cricket's franchise ecosystem is rapidly consolidating around a handful of cross-border ownership groups with Indian capital at the centre. The IPL, valued at an estimated $18.5 billion, sits at the apex. Recent sales of Royal Challengers Bengaluru ($1.78 billion to an Aditya Birla-led consortium) and Rajasthan Royals ($1.63 billion) have set benchmarks that BBL franchises — currently valued in the tens of millions — can only aspire to.

The Chennai match is the thin end of the wedge. If it succeeds commercially and logistically, it will validate a model where domestic leagues regularly cross borders, chasing audiences and investment wherever cricket's economic gravity pulls strongest. Right now, that gravity pulls unmistakably toward India.

A single T20 match at Chepauk in December will not transform the BBL overnight. But it will prove — or disprove — whether Australian cricket's most ambitious export strategy can work on the soil where franchise cricket was perfected.""",
    "status": "published",
    "published_at": now,
    "score_total": 80,
    "source_count": 5,
}

# ── ARTICLE 2: IPL Bigger Window ──────────────────────────
article2_id = str(uuid.uuid4())
article2_slug = "ipl-expansion-bigger-window-icc-2027-arun-dhumal-20260519"
article2 = {
    "id": article2_id,
    "headline": "The IPL Wants More of the Calendar. The Rest of World Cricket Should Be Paying Attention.",
    "subheadline": "IPL chairman Arun Singh Dhumal's pitch for a longer tournament window after 2027 is less a request than a forecast — one with major implications for how NRI fans consume cricket year-round",
    "slug": article2_slug,
    "category": "sports",
    "content": """Arun Singh Dhumal, the chairman of the Indian Premier League, has made the BCCI's ambitions unmistakably clear: when the ICC's current Future Tours Programme expires in 2027, India will push for a significantly larger IPL window.

In an interview with the Financial Times, Dhumal outlined a future where the IPL grows from its current 74-match format to 94 matches — a full home-and-away schedule across all ten franchises. The current format, introduced when the Gujarat Titans and Lucknow Super Giants joined in 2022, does not allow every team to play each other twice. Expanding to 94 matches would eliminate that asymmetry and, not incidentally, generate substantially more revenue.

"If you look at the transition over the last few years, there is definitely less interest in some bilateral games," Dhumal told the FT. "That is why countries are coming up with their own leagues."

## The Calendar Arithmetic

The mathematics are straightforward but politically explosive. The international cricket calendar is a zero-sum game. More IPL means fewer bilateral series — the three-match ODI tours and five-match Test series that have historically been the financial backbone of boards in England, Australia, and South Africa. Every additional week the IPL occupies is a week that bilateral cricket loses.

Dhumal has proposed several workarounds. One involves reducing bilateral commitments outright. Another suggests carving out a secondary IPL window in September or October — the gap between the end of the English county season and the start of the Australian summer — creating a split-season format.

The current calendar is locked until 2027. But the negotiations for the next cycle are already underway, and the BCCI's leverage is formidable. The IPL's central sponsorship portfolio alone is worth approximately ₹850 crore ($101 million) annually. Its most recent media rights deal — ₹48,390 crore over five years — dwarfs the broadcast revenues of any other cricket property on earth.

## A Football Model for Cricket

Dhumal's vision is explicit: cricket should look more like football. "Fewer bilaterals, more league cricket, and in between you have ICC events," he said. In this model, franchise leagues — the IPL, England's The Hundred, Australia's BBL, South Africa's SA20 — form the spine of the cricket calendar, with bilateral series and World Cups filling the gaps rather than the other way around.

This is not hypothetical. It is already happening. IPL franchise owners now run teams in at least five countries. The SA20 is entirely IPL-backed. Cricket Australia is exploring BBL privatisation with IPL money. The Hundred has sold minority stakes to investor groups that include IPL franchisees. The infrastructure for a franchise-first calendar already exists; the FTP just has not caught up.

## What It Means for NRI Cricket Fans

For the Indian diaspora, this shift has immediate practical consequences. NRI fans in the United States, United Kingdom, Canada, and Australia have long navigated a fragmented cricket viewing experience — different broadcasters for different tours, blackout restrictions, and time zone misery for Test matches in the subcontinent.

A longer, more dominant IPL season simplifies the equation. The IPL's broadcast partners already offer global streaming packages. A 94-match season stretching from mid-March to early June would give diaspora fans a reliable daily appointment with high-quality cricket for nearly three months, with matches timed for evening viewing in India — which means morning or afternoon in most Western time zones.

There is also the cultural dimension. Bilateral series pit country against country, reinforcing national identity. Franchise cricket is explicitly transnational. An IPL match features Indian, Australian, English, West Indian, and South African players on the same team, watched by fans on five continents. For NRIs who straddle two (or more) national identities, this framing is easier to inhabit.

## The Resistance

Not everyone is cheering. England and Australia both depend on bilateral home series against India for a significant portion of their cricket revenue. A longer IPL window means fewer available weeks for those marquee tours. Cricket boards in the Caribbean, Sri Lanka, and Bangladesh — already financially precarious — could find themselves squeezed further.

The ICC itself faces an existential question about relevance. If franchise leagues capture the best players, the biggest audiences, and the largest broadcast deals, what role does the governing body serve beyond organising a World Cup every few years?

## The Real Timeline

Dhumal has been careful to frame this as a future discussion, not an immediate demand. "When they plan post-2027, we will have discussions," he said. But the signals are clear. The BCCI wants more. It has the commercial leverage to get it. And the rest of the cricketing world will have to decide how much of the calendar it is willing to concede to the league that already dominates the sport's economics.

For the millions of NRI cricket fans setting their alarms for IPL games from Edison to Ealing to Eastern Creek, the question is simpler: more IPL is more of what they already love. Whether that comes at a cost they care about — the slow erosion of Test cricket, the marginalisation of smaller nations, the transformation of a sport into a content franchise — remains, for now, a question most would rather not answer.""",
    "status": "published",
    "published_at": now,
    "score_total": 78,
    "source_count": 4,
}

# ── Insert articles ──
print("Inserting article 1 (BBL Chennai)...")
r1 = sb_post("p2_articles", article1)
if isinstance(r1, list) and len(r1) > 0:
    print(f"  ✅ Article 1 inserted: {article1_id}")
elif isinstance(r1, dict) and r1.get("code"):
    print(f"  ❌ Error: {r1}")
else:
    print(f"  Result: {r1}")

print("Inserting article 2 (IPL Window)...")
r2 = sb_post("p2_articles", article2)
if isinstance(r2, list) and len(r2) > 0:
    print(f"  ✅ Article 2 inserted: {article2_id}")
elif isinstance(r2, dict) and r2.get("code"):
    print(f"  ❌ Error: {r2}")
else:
    print(f"  Result: {r2}")

# ── Update topic statuses ──
topics_to_publish = [
    ("3c064511-8b89-4816-84e4-a16bb56971de", "published"),  # BBL Chennai
    ("b148dc02-308f-498d-a59d-f612565f3e10", "published"),  # IPL bigger window
]
topics_to_reject = [
    ("f07f3a10-545a-4213-805d-d46b2c50b115", "rejected"),   # Brock Lesnar WWE
    ("93062c83-8cbc-42d4-a93e-a3b6e63fddbe", "rejected"),   # Guardiola Man City
    ("59e4d162-c370-45db-81fd-0dcbfbb7b339", "rejected"),   # Neymar Brazil
]

print("\nUpdating topic statuses...")
for tid, status in topics_to_publish + topics_to_reject:
    sb_patch("p2_topics", f"id=eq.{tid}", {"status": status, "updated_at": now})
    print(f"  Topic {tid[:8]}... → {status}")

print(f"\nArticle IDs for image sourcing:")
print(f"  Article 1 (BBL): {article1_id}")
print(f"  Article 2 (IPL): {article2_id}")
