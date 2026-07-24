#!/usr/bin/env python3
"""
Sports Writer — June 25, 2026 (22:30 UTC slot / videshi-writer-sports)

Article: Major League Cricket's Season 4 (MLC4) has come to the Oakland Coliseum
for the FIRST time — the old MLB ballpark, now the postseason and final venue —
and the home-side San Francisco Unicorns lost their Bay Area opener to the Texas
Super Kings by 22 runs. Diaspora angle: pro T20 cricket has landed in a major
Bay Area stadium, putting the world's top players within reach of the huge
South Asian community of the SF Bay Area / Silicon Valley.

DEDUP CHECK (vs recent ~3-4 days sports feed, category=sports):
- Feed HAS: India Women vs Bangladesh T20 WC (19:30 slot today); India men vs
  Ireland T20I preview (Iyer era); Edgbaston Test preview; MI New York "found
  their feet in Texas" (June 23, 01:45) — that was about MINY winning in Dallas
  in MLC4; women's hockey/relay; athletics; Pant to Delhi; Wimbledon doubles.
- The June 23 MI New York piece is a DIFFERENT MLC match (MINY in Texas) and a
  different angle (Edison-raised captain). This piece is about the OAKLAND
  COLISEUM debut + the San Francisco Unicorns' home loss to Texas Super Kings,
  pegged to the June 24/25 Oakland round. Distinct event, distinct venue angle,
  distinct teams. CLEAR TO WRITE.

Key facts (ESPNcricinfo / Wikipedia 2026 MLC season; sportscafe; khelnow):
- 2026 MLC = MLC Season 4 (MLC4), June 18 - July 18, 2026. Double round-robin
  + playoffs; 6 teams; top 4 make playoffs.
- THREE venues this season: Grand Prairie Stadium (Dallas, 15 matches),
  Oakland Coliseum (Oakland, 12 matches), and Knight Riders Cricket Field at
  Fairplex (Pomona, 7 matches). FIRST time MLC uses the Pomona ground. The
  Oakland Coliseum will ALSO host the playoffs and the championship final for
  the first time. Coliseum cricket capacity ~12,000.
- The San Francisco Unicorns' home stadium is the Oakland Coliseum. Unicorns
  owned by Anand Rajaraman & Venky Harinarayan; captain Matthew Short; this
  season signed veteran India all-rounder Ravichandran Ashwin.
- Match (Match 8, Oakland Coliseum, played June 24 D/N, completed in the early
  hours of June 25 PT): Texas Super Kings 161/8 (20 ov) beat San Francisco
  Unicorns 139 all out (17.4 ov) by 22 runs.
  - TSK batting: Donovan Ferreira 45 (28); Matthew Short 28 (16) top-scored for
    SAN. (Short plays for both? No — Short captains SAN. For TSK the top names
    were Ferreira 45.) SAN bowling: Amshi de Silva 4/28 was Player of the Match
    (he bowls for Texas), Ghulam Mudassar 2/30.
  - Correction from scorecards: Amshi de Silva (4/28) is the Texas bowler and
    Player of the Match; Matthew Short (28 off 16) top-scored for San Francisco.
- Standings after the Oakland round (to matches played ~24-25 June, ESPNcricinfo):
  Los Angeles Knight Riders top (2 played, 2 won, 4 pts, NRR +2.602); Texas
  Super Kings 2nd (4 pl, 2 W, 4 pts, NRR around -0.11 and climbing after the
  win); Washington Freedom, MI New York, San Francisco Unicorns and Seattle
  Orcas all on 2 pts, separated by NRR. Unicorns sit mid-table (3 pl, 1 W, 2 L).
- Defending champions: MI New York (2025 title, beat Washington Freedom by 5
  runs). MINY also won 2023; Washington Freedom won 2024.
- Diaspora context: MLC is the USA's franchise T20 league, launched 2023, built
  for the large South Asian-American audience; most recent season set records
  for ticket sales (+53% YoY, 84% first-time buyers) and broadcast reach (90+
  countries). The Bay Area / Silicon Valley has one of the largest Indian
  diaspora populations in the US.

Hero: Wikimedia Commons aerial of the Oakland Coliseum (Sept 2024). Permanent
Wikimedia URL, downloaded + re-uploaded to Supabase.
"""

import os, io, json, subprocess
from datetime import datetime, timezone

import requests
from PIL import Image

# -- ENV --
env_supa = os.path.expanduser("~/.env.supabase")
for line in open(env_supa):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
UA = "TheVideshi/1.0 (thevideshi.com)"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def compress_image(img_bytes, max_width=1200, quality=85):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_url, filename):
    try:
        tmp = f"/tmp/{filename}"
        subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, img_url], capture_output=True)
        if not (os.path.exists(tmp) and os.path.getsize(tmp) > 5000):
            print(f"  \u2717 Download failed for {img_url[:80]}")
            return None
        content = open(tmp, "rb").read()
        compressed = compress_image(content)
        print(f"  \U0001f4e6 Compressed to {len(compressed)/1024:.0f} KB")
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true",
            },
            data=compressed, timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded: {public_url}")
            return public_url
        else:
            print(f"  \u2717 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  \u2717 Upload error: {e}")
        return None


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, json=article, timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  \u2713 Inserted article: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


print("\n" + "=" * 60)
print("ARTICLE: MLC comes to the Oakland Coliseum; Unicorns fall to Texas")
print("=" * 60)

art_slug = "major-league-cricket-2026-oakland-coliseum-debut-san-francisco-unicorns-lose-texas-super-kings-22-runs-bay-area-diaspora-nri"
art_headline = "Big-League Cricket Has Moved Into the Oakland Coliseum — and the Bay Area's Team Lost the First Round"
art_subheadline = "Major League Cricket's fourth season has turned the old A's ballpark into the home of the playoffs and the final, but the San Francisco Unicorns opened their Oakland stand with a 22-run defeat to the Texas Super Kings."

art_body = """For decades the Oakland Coliseum was where the Athletics played baseball and the Raiders played football. This summer it has a new tenant and a new shape: a cricket square in the middle of the diamond, floodlights on for a day-night T20, and a crowd drawn heavily from the Bay Area's enormous South Asian community. Major League Cricket has arrived in Oakland — and the home side could not mark the occasion with a win.

In the first match of the league's Oakland stand, the Texas Super Kings posted 161 for 8 and held the San Francisco Unicorns to 139 all out, a 22-run victory that left the Bay Area franchise to rue a familiar problem: a chase that lost its way once the early wickets fell.

## A ballpark reborn for cricket

The bigger story is the venue itself. MLC's fourth season, running from June 18 to July 18, is being staged across three grounds — the league's established home at Grand Prairie Stadium near Dallas, a new site at the Knight Riders Cricket Field in Pomona, and, for the first time, the Oakland Coliseum. The Coliseum is not just hosting league games; it will also stage the playoffs and the championship final, making it the centrepiece of the 2026 campaign. With a cricket capacity of around 12,000, it is comfortably the largest of the three venues.

That matters for a league still building its footprint in the United States. MLC launched in 2023 as America's franchise T20 competition, explicitly courting the millions of cricket-loving South Asian Americans who had no top-flight league of their own. The most recent season set records for ticket sales — up more than 50 per cent year on year, with the vast majority of buyers attending for the first time — and broadcast reach across more than 90 countries. Planting the playoffs in a major-market stadium like the Coliseum is the next step in that growth.

## The match: Texas hold their nerve

On the field, Texas's 161 for 8 was built around Donovan Ferreira's brisk 45 from 28 balls, a total that looked par on a used surface. San Francisco's reply started brightly through captain Matthew Short, who top-scored with 28 from 16, but the innings unravelled in the middle overs. Texas off-spinner Amshi de Silva was the wrecker-in-chief, taking 4 for 28 to earn the player-of-the-match award, and the Unicorns were bowled out for 139 with more than two overs unused.

It was a sobering result for a team that has invested heavily in star power. The Unicorns, owned by Silicon Valley entrepreneurs Anand Rajaraman and Venky Harinarayan, added veteran India all-rounder Ravichandran Ashwin to their squad for this season, hoping his guile would anchor their bowling. On this night, though, it was Texas — the Chennai Super Kings-backed franchise captained by Faf du Plessis — who looked the sharper outfit.

## Where the table stands

The defeat leaves the Unicorns in the middle of a congested six-team table. The Los Angeles Knight Riders, unbeaten so far, sit top, with the Texas Super Kings climbing on the back of this win. Washington Freedom, MI New York, San Francisco and Seattle Orcas are bunched together on equal points, separated only by net run rate — which is precisely why a 22-run margin stings. With the top four advancing to the playoffs, the Unicorns have ground to make up over their remaining Oakland fixtures. Defending champions MI New York, two-time winners already, remain the team to beat.

## Why the diaspora should care

For Indian Americans in the Bay Area and Silicon Valley — one of the densest concentrations of the diaspora anywhere in the United States — this is a rare chance to watch international-calibre cricket a short drive from home, in a stadium that has hosted World Series baseball. Players who light up the IPL and international circuits are turning out at the Coliseum through July, and the season's biggest night, the final, will be played there too. The Unicorns may have stumbled at the first hurdle on home soil, but the more lasting headline is that the sport itself has finally found a big-league American home in the Bay Area — and the community has the rest of the summer to fill those seats."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing hero image (Wikimedia Commons \u2014 Oakland Coliseum)...")
img_caption = "An aerial view of the Oakland Coliseum, which is hosting Major League Cricket matches, the playoffs and the 2026 final."
img_attribution = "Wikimedia Commons"

wiki_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Oakland_Coliseum_overhead_angle%2C_September_2024.jpg/1280px-Oakland_Coliseum_overhead_angle%2C_September_2024.jpg"
img_final = upload_to_supabase(wiki_img, f"{art_slug}.jpg")

if not img_final:
    print("  \u26a0 No image uploaded \u2014 trying alternate Coliseum view")
    img_final = upload_to_supabase(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Oakland_Coliseum_view_from_Mt._Davis.jpg/1280px-Oakland_Coliseum_view_from_Mt._Davis.jpg",
        f"{art_slug}.jpg",
    )

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Wikipedia \u2014 2026 Major League Cricket season (venues, schedule, results, points table)", "url": "https://en.wikipedia.org/wiki/2026_Major_League_Cricket_season"},
        {"name": "Khel Now \u2014 San Francisco Unicorns 139 vs Texas Super Kings 161/8: TSK won by 22 runs", "url": "https://khelnow.com/cricket"},
        {"name": "SportsCafe \u2014 Major League Cricket 2026 results and points table", "url": "https://www.sportscafe.in/"},
        {"name": "ESPNcricinfo \u2014 Major League Cricket 2026 standings", "url": "https://www.espn.com/cricket/"},
    ]),
    "diaspora_angle": "Major League Cricket has brought top-flight T20 cricket \u2014 and its 2026 playoffs and final \u2014 to the Oakland Coliseum, putting international-calibre players within a short drive of the Bay Area's large South Asian diaspora.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)
print("\nDONE." if art_id else "\nFAILED to insert.")
