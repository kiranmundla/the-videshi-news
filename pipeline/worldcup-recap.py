#!/usr/bin/env python3
"""
World Cup Daily Recap Writer for The Videshi.

Generates an Economist-quality recap article summarizing the day's World Cup matches.
Reads match data from worldcup.json, enriches with web search for key moments,
and publishes to Supabase p2_articles.

Usage:
  python3 worldcup-recap.py              # Recap yesterday's matches
  python3 worldcup-recap.py 2026-06-12   # Recap a specific date
"""

import json, os, re, sys, uuid, subprocess, urllib.parse, html, time
from datetime import datetime, date, timezone, timedelta
from pathlib import Path

# ── Env setup ──
env_file = Path.home() / ".env.supabase"
if env_file.exists():
    for line in env_file.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# Load OpenAI key from workspace env
env_openai = Path.home() / "workspace" / ".env.openai"
if env_openai.exists():
    for line in env_openai.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

WC_JSON = Path(__file__).parent.parent / "public" / "data" / "worldcup.json"
TOURNAMENT_START = date(2026, 6, 11)
TOURNAMENT_END = date(2026, 7, 19)

# ── Wikipedia image helper ──
TEAM_WIKI_SLUGS = {
    "USA": "United_States_men%27s_national_soccer_team",
    "Mexico": "Mexico_national_football_team",
    "Canada": "Canada_men%27s_national_soccer_team",
    "Brazil": "Brazil_national_football_team",
    "Argentina": "Argentina_national_football_team",
    "Germany": "Germany_national_football_team",
    "France": "France_national_football_team",
    "England": "England_national_football_team",
    "Spain": "Spain_national_football_team",
    "Portugal": "Portugal_national_football_team",
    "Netherlands": "Netherlands_national_football_team",
    "Italy": "Italy_national_football_team",
    "South Korea": "South_Korea_national_football_team",
    "Japan": "Japan_national_football_team",
    "South Africa": "South_Africa_national_football_team",
    "Morocco": "Morocco_national_football_team",
    "Qatar": "Qatar_national_football_team",
    "Switzerland": "Switzerland_national_football_team",
    "Croatia": "Croatia_national_football_team",
    "Czechia": "Czech_Republic_national_football_team",
    "Bosnia & Herzegovina": "Bosnia_and_Herzegovina_national_football_team",
    "Paraguay": "Paraguay_national_football_team",
    "Haiti": "Haiti_national_football_team",
    "Scotland": "Scotland_national_football_team",
}

# Fallback World Cup image
WC_IMAGE = "https://upload.wikimedia.org/wikipedia/en/thumb/e/e3/2026_FIFA_World_Cup_logo.svg/800px-2026_FIFA_World_Cup_logo.svg.png"


def get_wiki_image(team_name):
    """Try to get a Wikipedia image for a team."""
    import requests
    slug = TEAM_WIKI_SLUGS.get(team_name)
    if not slug:
        # Try generic slugging
        slug = team_name.replace(" ", "_") + "_national_football_team"
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}",
            headers={"User-Agent": "TheVideshi/1.0"},
            timeout=10,
        )
        if r.ok:
            data = r.json()
            return data.get("thumbnail", {}).get("source", "")
    except Exception:
        pass
    return ""


def load_matches(target_date_str):
    """Load finished matches for a given date from worldcup.json."""
    data = json.loads(WC_JSON.read_text())
    finished = [
        m for m in data["matches"]
        if m["date"] == target_date_str and m["status"] == "FT"
    ]
    return finished, data


def compute_day_number(target_date):
    """Tournament day number (Day 1 = Jun 11)."""
    return (target_date - TOURNAMENT_START).days + 1


def parse_score(match):
    """Parse score into home/away goals."""
    if not match.get("score"):
        return 0, 0
    parts = match["score"].split("-")
    try:
        return int(parts[0].strip()), int(parts[1].strip())
    except (ValueError, IndexError):
        return 0, 0


def get_match_result_text(match):
    """Generate a result description for a single match."""
    hg, ag = parse_score(match)
    home, away = match["home"], match["away"]
    if hg > ag:
        return f"{home} beat {away} {match['score']}"
    elif ag > hg:
        return f"{away} beat {home} {ag}-{hg}"
    else:
        return f"{home} and {away} drew {match['score']}"


def generate_headline(matches, day_number):
    """Generate a compelling headline based on the day's results."""
    if len(matches) == 1:
        m = matches[0]
        return f"World Cup Day {day_number}: {get_match_result_text(m)}"

    # Find the most notable result — biggest goal difference or upset
    best = None
    best_diff = -1
    for m in matches:
        hg, ag = parse_score(m)
        diff = abs(hg - ag)
        total = hg + ag
        if diff > best_diff or (diff == best_diff and total > (parse_score(best)[0] + parse_score(best)[1] if best else 0)):
            best = m
            best_diff = diff

    lead_result = get_match_result_text(best)
    other_count = len(matches) - 1

    if other_count == 1:
        other = [m for m in matches if m != best][0]
        other_result = get_match_result_text(other)
        return f"World Cup Day {day_number}: {lead_result}; {other_result}"
    else:
        return f"World Cup Day {day_number}: {lead_result} Headlines {len(matches)}-Match Day"


def generate_subheadline(matches, target_date):
    """Generate a subheadline with venue/diaspora context."""
    cities = list(set(m["city"] for m in matches))
    venues = list(set(m["venue"] for m in matches))
    date_str = target_date.strftime("%B %d")

    if len(matches) == 1:
        m = matches[0]
        return f"Group {m['group']} action at {m['venue']} in {m['city']} on {date_str}."
    elif len(cities) <= 3:
        return f"Group stage action from {', '.join(cities)} on {date_str} — {len(matches)} matches, no shortage of drama."
    else:
        return f"{len(matches)} group stage matches across {len(venues)} venues on {date_str}."


def generate_slug(target_date):
    """Generate article slug."""
    return f"world-cup-recap-{target_date.isoformat()}"


def build_match_section(match, idx):
    """Build a markdown section for a single match recap."""
    hg, ag = parse_score(match)
    home, away = match["home"], match["away"]
    total = hg + ag
    group_label = f"Group {match['group']}"
    venue_line = f"{match['venue']}, {match['city']}"

    section = f"## {home} {match['score']} {away}\n"
    section += f"*{group_label} · {venue_line}*\n\n"

    # Build rich narrative based on score patterns
    if hg > ag:
        margin = hg - ag
        if margin >= 3:
            section += (
                f"{home} made a resounding statement in {group_label}, dismantling {away} "
                f"{match['score']} at {match['venue']}. From the opening whistle, they "
                f"looked a level above, converting chance after chance with clinical "
                f"efficiency. {away} will need to regroup quickly; in a group stage this "
                f"compressed, a heavy defeat on goal difference can haunt a team in the "
                f"final reckoning.\n\n"
                f"The {hg}-goal haul will send a message to the rest of {group_label}, and "
                f"perhaps beyond it. {home}'s depth was evident throughout — substitutes "
                f"looked just as sharp as starters, a promising sign for the knockout "
                f"rounds.\n\n")
        elif margin == 2:
            section += (
                f"{home} put in a controlled, professional performance to dispatch {away} "
                f"{match['score']} at {match['venue']}. It was the kind of win that doesn't "
                f"make highlight reels but earns respect in tournament football — composed at "
                f"the back, incisive going forward, and ruthless when it mattered.\n\n"
                f"For {away}, the two-goal deficit is not insurmountable, but their remaining "
                f"{group_label} fixtures now carry the weight of must-win encounters.\n\n")
        else:
            section += (
                f"In a tightly contested {group_label} opener, {home} edged {away} "
                f"{match['score']} in a match that swung on fine margins. The game had "
                f"the tension of a knockout tie rather than a group stage opener, with "
                f"both sides pressing hard and leaving little space in midfield.\n\n"
                f"{away} will feel they deserved more, but tournament football is "
                f"unforgiving. The single goal separating the teams belies how close "
                f"{away} came to snatching a point. They remain very much alive in "
                f"{group_label}.\n\n")
    elif ag > hg:
        margin = ag - hg
        if margin >= 3:
            section += (
                f"{away} produced the standout result of the day, hammering {home} "
                f"{ag}-{hg} at {match['venue']}. It was a masterclass from the opening "
                f"minutes, with {away} pressing high, winning second balls, and punishing "
                f"every defensive lapse. {home} looked shell-shocked by the intensity.\n\n"
                f"For {away}, this is as good a World Cup start as they could have scripted. "
                f"For {home}, the question now is whether they can recover mentally — and on "
                f"goal difference — in time for their remaining group fixtures.\n\n")
        elif margin == 2:
            section += (
                f"{away} turned the form book on its head, coming into {match['venue']} and "
                f"leaving with a convincing {ag}-{hg} victory over {home}. The two-goal "
                f"margin flattered neither side; {away} were genuinely the better team across "
                f"90 minutes, pressing intelligently and finishing with composure.\n\n"
                f"It is a result that reshapes {group_label} and gives {away} a commanding "
                f"platform. {home} now face a nervous wait and must pick up points in their "
                f"remaining matches.\n\n")
        else:
            section += (
                f"{away} snatched the win in a closely contested {group_label} match, edging "
                f"{home} {ag}-{hg} at {match['venue']}. It was a game of slim margins and "
                f"hard tackles, the kind of World Cup fixture where one moment of quality "
                f"makes all the difference.\n\n"
                f"The result is a blow for {home} but not a fatal one. With two group games "
                f"remaining, there is time to recover — but the margin for error has "
                f"narrowed.\n\n")
    else:
        if hg == 0:
            section += (
                f"Neither {home} nor {away} could find the breakthrough in a cagey, "
                f"tension-filled goalless draw at {match['venue']}. Both defences were "
                f"outstanding — or both attacks were lacking, depending on your point of "
                f"view. The point apiece keeps both sides' hopes alive in {group_label}, "
                f"but neither will be satisfied with the result.\n\n"
                f"The lack of goals should not obscure the quality of the defensive battle. "
                f"Both goalkeepers made sharp saves, and the woodwork was struck more than "
                f"once. Sometimes the story of a match is the goal that didn't come.\n\n")
        elif hg == 1:
            section += (
                f"A 1-1 draw was probably a fair reflection of a tightly contested match "
                f"between {home} and {away} at {match['venue']}. Both teams created chances, "
                f"both teams scored, and both teams will look at moments where they might "
                f"have won it. In the end, a share of the spoils was the just outcome.\n\n"
                f"For both sides, the arithmetic is clear: a point is better than none, but "
                f"wins are the currency of a group stage. Their remaining {group_label} "
                f"fixtures take on added importance.\n\n")
        else:
            section += (
                f"An entertaining {hg}-{hg} draw between {home} and {away} delivered the "
                f"kind of end-to-end, goal-laden football that World Cups are remembered "
                f"for. Neither side could establish control for long — every time one team "
                f"took the lead, the other hit back.\n\n"
                f"The shared point leaves {group_label} finely balanced. Both teams showed "
                f"they can score freely; the question is whether they can defend well enough "
                f"to survive a World Cup.\n\n")

    # Add venue context for US venues (diaspora angle)
    us_desi_venues = {
        "MetLife Stadium": (
            "The match was played at MetLife Stadium in the heart of NJ/NY's massive desi "
            "community. Indian-American fans made their presence felt in the stands — the "
            "tri-state area is home to one of the densest concentrations of South Asian "
            "Americans in the country."),
        "Levi's Stadium": (
            "Levi's Stadium in the Bay Area — home to one of the largest Indian-American "
            "populations in the country — provided the backdrop. South Asian fans dotted the "
            "stands, many attending their first-ever World Cup match on home soil."),
        "SoFi Stadium": (
            "The match took place at SoFi Stadium in Los Angeles, where the growing South "
            "Asian community turned out in force. For many Indian-American fans in LA, this "
            "was a once-in-a-lifetime chance to see World Cup football without a "
            "transatlantic flight."),
        "AT&T Stadium": (
            "AT&T Stadium in Dallas hosted the fixture, with DFW's booming desi community "
            "well represented in the crowd. North Texas has become one of the fastest-growing "
            "hubs for Indian-American families in recent years."),
        "NRG Stadium": (
            "The match was held at NRG Stadium in Houston, the heart of Texas's vibrant "
            "South Asian corridor. The Indian-American community in Greater Houston is one "
            "of the largest in the American South."),
        "Gillette Stadium": (
            "Gillette Stadium in the Greater Boston area hosted the match. The region's "
            "strong desi community — bolstered by the tech and university corridors from "
            "Cambridge to Route 128 — brought their energy to the stands."),
        "Hard Rock Stadium": (
            "Hard Rock Stadium in Miami Gardens provided the South Florida sunshine and a "
            "crowd that reflected the city's remarkable diversity."),
        "Lincoln Financial Field": (
            "Philadelphia Stadium played host, with the City of Brotherly Love delivering "
            "the atmosphere it promised."),
    }
    if match["venue"] in us_desi_venues:
        section += us_desi_venues[match["venue"]] + "\n\n"

    return section


def build_standings_context(matches, all_data):
    """Build a paragraph about standings implications."""
    groups_affected = sorted(set(m["group"] for m in matches))

    section = "## What It Means for the Standings\n\n"

    for group in groups_affected:
        group_matches = [m for m in matches if m["group"] == group]
        winners = []
        losers = []
        drawers = []
        for m in group_matches:
            hg, ag = parse_score(m)
            if hg > ag:
                winners.append(m["home"])
                losers.append(m["away"])
            elif ag > hg:
                winners.append(m["away"])
                losers.append(m["home"])
            else:
                drawers.extend([m["home"], m["away"]])

        parts = []
        if winners:
            for w in winners:
                parts.append(f"**{w}** move to 3 points and put themselves in a strong position")
        if drawers:
            draw_names = " and ".join(f"**{d}**" for d in drawers)
            parts.append(f"{draw_names} each take a point — not the worst outcome, but not the result either side wanted")
        if losers:
            for l in losers:
                parts.append(f"**{l}** sit on zero points and will need results in their remaining fixtures")

        section += f"In Group {group}, {'; '.join(parts)}. "

    section += (
        "\n\nWith 48 teams and a format that sends the top two from each group — plus the "
        "eight best third-placed sides — into the round of 32, the margins are tighter than "
        "they appear. Goal difference could prove decisive.\n\n"
    )
    return section


def build_whats_next(target_date, all_data):
    """Build 'What's Next' section with tomorrow's matches."""
    tomorrow = target_date + timedelta(days=1)
    tomorrow_str = tomorrow.isoformat()
    tomorrow_matches = [m for m in all_data["matches"] if m["date"] == tomorrow_str]

    if not tomorrow_matches:
        return ""

    day_num = compute_day_number(tomorrow)
    section = "## What's Next\n\n"
    section += f"Day {day_num} ({tomorrow.strftime('%A, %B %d')}) brings {len(tomorrow_matches)} more group stage {'matches' if len(tomorrow_matches) > 1 else 'match'}:\n\n"

    for m in tomorrow_matches:
        section += f"- **{m['home']} vs {m['away']}** — Group {m['group']} at {m['venue']}, {m['city']}\n"

    section += "\n"
    return section


def generate_article(matches, target_date, all_data):
    """Generate the full recap article."""
    day_number = compute_day_number(target_date)
    headline = generate_headline(matches, day_number)
    subheadline = generate_subheadline(matches, target_date)
    slug = generate_slug(target_date)

    # Build body
    date_str = target_date.strftime("%A, %B %d")
    total_goals = sum(parse_score(m)[0] + parse_score(m)[1] for m in matches)
    body = (
        f"Day {day_number} of the 2026 FIFA World Cup delivered {len(matches)} "
        f"{'match' if len(matches) == 1 else 'matches'} and {total_goals} goals on "
        f"{date_str}. The tournament, spread across the United States, Canada, and Mexico, "
        f"continued its group stage with action that will resonate in standings tables and "
        f"living rooms alike — not least in the Indian-American households tuning in from "
        f"cities that are, for once, hosting the spectacle rather than streaming it from "
        f"half a world away.\n\nHere is everything you need to know.\n\n"
    )

    # Match sections
    for i, m in enumerate(matches):
        body += build_match_section(m, i)

    # Standings implications
    body += build_standings_context(matches, all_data)

    # What's next
    body += build_whats_next(target_date, all_data)

    # Closing with diaspora angle
    body += "---\n\n"
    body += "*The Videshi's World Cup coverage is updated throughout the day. "
    body += "Follow our [World Cup tracker](/world-cup-2026) for live scores, group standings, and highlights. "
    body += "Attending a match? Check our [NRI guide](/world-cup-2026) for venue tips and ticket links.*\n"

    # Pick image — use the "biggest" winner's team image, or fallback to WC logo
    best_match = max(matches, key=lambda m: abs(parse_score(m)[0] - parse_score(m)[1]))
    hg, ag = parse_score(best_match)
    featured_team = best_match["home"] if hg >= ag else best_match["away"]
    image_url = get_wiki_image(featured_team) or WC_IMAGE

    # Tags
    teams = []
    for m in matches:
        teams.extend([m["home"], m["away"]])
    tag_list = ["world-cup", "fifa", "sports", "world-cup-2026"]
    for t in teams:
        tag_list.append(t.lower().replace(" ", "-"))
    # Add venue cities
    for m in matches:
        tag_list.append(m["city"].lower().replace(" ", "-").replace("/", "-"))

    return {
        "id": str(uuid.uuid4()),
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "tags": list(set(tag_list)),
        "urgency": "high",
        "score_total": 80,
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "image_url": image_url,
        "image_caption": f"FIFA World Cup 2026 — Day {day_number} recap",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": f"World Cup matches in US cities near major NRI communities. {len([m for m in matches if m['city'] in ['San Francisco Bay Area', 'New York/New Jersey', 'Los Angeles', 'Houston', 'Dallas', 'Boston']])} of today's {len(matches)} matches were in cities with large Indian-American populations.",
        "body": body,
        "sources": json.dumps([
            {"name": "FIFA.com", "url": "https://www.fifa.com/fifaplus/en/tournaments/mens/worldcup/canadamexicousa2026"},
            {"name": "The Videshi World Cup Tracker", "url": "https://thevideshi.com/world-cup-2026"},
        ]),
    }


def generate_match_slug(match):
    """Generate a slug for an individual match article."""
    home = match["home"].lower().replace(" ", "-").replace("&", "and")
    away = match["away"].lower().replace(" ", "-").replace("&", "and")
    return f"world-cup-2026-{home}-vs-{away}-{match['date']}"


# ── Rich match article helpers ──


def web_search_match(home, away, match_date):
    """Search the web for match details: scorers, stats, key moments."""
    queries = [
        f"{home} vs {away} FIFA World Cup 2026 match report {match_date}",
        f"{home} {away} World Cup 2026 goals scorers highlights",
    ]
    results = []
    for q in queries:
        try:
            encoded = urllib.parse.quote(q)
            r = subprocess.run(
                ["curl", "-sS", "-L", "--max-time", "12",
                 "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                 f"https://lite.duckduckgo.com/lite/?q={encoded}"],
                capture_output=True, text=True, timeout=15
            )
            if r.returncode == 0 and r.stdout:
                text = re.sub(r'<[^>]+>', ' ', r.stdout)
                text = html.unescape(text)
                text = re.sub(r'\s+', ' ', text).strip()
                if len(text) > 200:
                    results.append(text[:3000])
        except Exception as e:
            print(f"   ⚠ Web search failed for '{q[:50]}': {e}")
    return "\n---\n".join(results) if results else ""


def search_social_embeds(home, away):
    """Search for Instagram/X highlight posts from FIFA and team accounts."""
    embeds = []
    queries = [
        f"site:instagram.com fifaworldcup {home} {away} World Cup 2026",
        f"site:x.com FIFA {home} vs {away} World Cup 2026 goal highlights",
    ]
    for q in queries:
        try:
            encoded = urllib.parse.quote(q)
            r = subprocess.run(
                ["curl", "-sS", "-L", "--max-time", "10",
                 "-H", "User-Agent: Mozilla/5.0",
                 f"https://lite.duckduckgo.com/lite/?q={encoded}"],
                capture_output=True, text=True, timeout=12
            )
            if r.returncode == 0 and r.stdout:
                ig_matches = re.findall(
                    r'https?://(?:www\.)?instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)',
                    r.stdout
                )
                for code in ig_matches[:2]:
                    url = f"https://www.instagram.com/p/{code}/"
                    if url not in embeds:
                        embeds.append(url)
                x_matches = re.findall(
                    r'https?://(?:www\.)?(?:x\.com|twitter\.com)/(\w+/status/\d+)',
                    r.stdout
                )
                for path in x_matches[:2]:
                    url = f"x-official:https://x.com/{path}"
                    if url not in embeds:
                        embeds.append(url)
        except Exception as e:
            print(f"   ⚠ Social search failed: {e}")
    return embeds[:3]


def fetch_stadium_image(venue_name, city):
    """Search Wikimedia Commons for a stadium photo."""
    import requests as req
    queries = [f"{venue_name} stadium", f"{venue_name} {city}"]
    for search_q in queries:
        try:
            params = {
                "action": "query",
                "generator": "search",
                "gsrsearch": search_q,
                "gsrnamespace": "6",
                "gsrlimit": "5",
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "iiurlwidth": "1280",
                "format": "json",
            }
            r = req.get(
                "https://commons.wikimedia.org/w/api.php",
                params=params, headers={"User-Agent": "TheVideshi/1.0"}, timeout=15
            )
            if r.ok:
                data = r.json()
                pages = data.get("query", {}).get("pages", {})
                for pid, page in sorted(pages.items()):
                    ii = page.get("imageinfo", [{}])[0]
                    mime = ii.get("mime", "")
                    width = ii.get("width", 0)
                    if mime in ("image/jpeg", "image/png") and width >= 800:
                        return ii.get("thumburl") or ii.get("url")
        except Exception as e:
            print(f"   ⚠ Wikimedia Commons search failed for '{search_q}': {e}")
    return ""


def call_openai_match(system_prompt, user_prompt, max_tokens=2500):
    """Call OpenAI GPT-4o for match article generation. Returns parsed JSON or None."""
    if not OPENAI_KEY:
        print("   ⚠ No OPENAI_API_KEY found, falling back to template")
        return None
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "response_format": {"type": "json_object"}
    }
    try:
        r = subprocess.run(
            ["curl", "-s", "--max-time", "60",
             "https://api.openai.com/v1/chat/completions",
             "-H", f"Authorization: Bearer {OPENAI_KEY}",
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=90
        )
        data = json.loads(r.stdout)
        if "error" in data:
            print(f"   ⚠ OpenAI error: {data['error'].get('message', '')[:100]}")
            return None
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        print(f"   ⚠ OpenAI call failed: {e}")
        return None


def generate_match_article(match, all_data):
    """Generate a rich, GPT-powered standalone article for a single match."""
    hg, ag = parse_score(match)
    result_text = get_match_result_text(match)
    slug = generate_match_slug(match)
    target_date = date.fromisoformat(match["date"])
    day_number = compute_day_number(target_date)
    date_str = target_date.strftime("%A, %B %d")
    home, away = match["home"], match["away"]
    venue, city = match["venue"], match.get("city", "")
    group = match["group"]

    print(f"   🔍 Searching web for {home} vs {away} match details...")
    web_context = web_search_match(home, away, match["date"])

    print(f"   📱 Searching for social media highlights...")
    social_embeds = search_social_embeds(home, away)
    if social_embeds:
        print(f"   ✅ Found {len(social_embeds)} social embed(s)")
    else:
        print(f"   ℹ️  No social embeds found")

    # Build embed instruction for GPT
    embed_instruction = ""
    if social_embeds:
        embed_lines = "\n".join(social_embeds)
        embed_instruction = (
            f"\n\nIMPORTANT — Social media embeds to include inline in the article body. "
            f"Place each URL on its own line (not inside a markdown link) after a relevant paragraph. "
            f"Use 1-2 of these:\n{embed_lines}"
        )

    # Diaspora venue context
    venue_context_map = {
        "MetLife Stadium": "NJ/NY tri-state area — one of the largest South Asian populations in the US",
        "Levi's Stadium": "Bay Area — home to a massive Indian-American tech community",
        "SoFi Stadium": "Los Angeles — growing South Asian community in Southern California",
        "AT&T Stadium": "Dallas-Fort Worth — one of the fastest-growing desi hubs in America",
        "NRG Stadium": "Houston — heart of Texas's South Asian corridor",
        "Gillette Stadium": "Greater Boston — strong desi community along the tech and university corridor",
        "Hard Rock Stadium": "Miami — remarkably diverse South Florida fanbase",
        "Lincoln Financial Field": "Philadelphia — the City of Brotherly Love",
        "BC Place": "Vancouver — large South Asian community in British Columbia",
        "BMO Field": "Toronto — Canada's largest Indian-Canadian diaspora",
        "Estadio BBVA": "Monterrey, Mexico",
        "Estadio Azteca": "Mexico City — one of football's most iconic grounds",
    }
    diaspora_context = venue_context_map.get(venue, f"{city}")

    # Group standings context
    group_teams = [m for m in all_data.get("matches", []) if m.get("group") == group]
    group_context = "Group {} includes these matches: ".format(group)
    group_context += "; ".join(
        f"{m['home']} vs {m['away']} ({m.get('score', 'TBD')})"
        for m in group_teams[:6]
    )

    # GPT system prompt
    system_prompt = (
        "You are a senior sports editor at The Videshi, an Economist-style digital "
        "publication for the Indian diaspora in North America. You write World Cup "
        "match reports that combine sharp tactical analysis with a diaspora lens.\n\n"
        "Your writing style:\n"
        "- Authoritative, witty, precise — like the Economist's sports writing\n"
        "- Use active voice, strong verbs, vivid detail\n"
        "- Weave in the NRI/diaspora angle naturally (Indian-American fans at the stadium, "
        "desi community in the host city, how the result affects the tournament)\n"
        "- NEVER use clichés like 'rollercoaster', 'nail-biter', 'edge-of-your-seat'\n"
        "- Paragraphs should be meaty but readable\n"
        "- Include specific match facts (scorers, minutes, key moments) from the web search context\n"
        "- If you don't know specific scorer names, write around the gap — describe patterns "
        "of play, tactical shifts, atmosphere\n\n"
        "Return a JSON object with these fields:\n"
        "{\n"
        '  "headline": "Creative, attention-grabbing headline (not template-style)",\n'
        '  "subheadline": "One-sentence subheadline with key match fact",\n'
        '  "body": "Full article body in markdown, 600-800 words. Use ## for section headers. '
        'Include social embeds on their own lines where contextually appropriate.",\n'
        '  "diaspora_angle": "One-sentence summary of the diaspora angle",\n'
        '  "sources": [{"name": "source name", "url": "url"}]\n'
        "}"
    )

    user_prompt = (
        f"Write a match report for this World Cup 2026 game:\n\n"
        f"**Match:** {home} {match['score']} {away}\n"
        f"**Competition:** FIFA World Cup 2026 — Group {group}, Day {day_number}\n"
        f"**Venue:** {venue}, {city}\n"
        f"**Date:** {date_str}\n"
        f"**Result:** {result_text}\n\n"
        f"**Group context:** {group_context}\n\n"
        f"**Diaspora context:** This match was played at {venue} in {diaspora_context}. "
        f"The 2026 World Cup is being hosted across the United States, Canada, and Mexico — "
        f"many venues are in cities with large Indian-American communities.\n\n"
        f"**Web search context (use for facts — scorers, stats, key moments):**\n"
        f"{web_context[:3000] if web_context else 'No web search results available — write based on the score and tactical implications.'}\n"
        f"{embed_instruction}\n\n"
        f"**Article structure:**\n"
        f"1. Opening lead (the result and its significance — hook the reader)\n"
        f"2. How the game unfolded (use specific moments if available from web context)\n"
        f"3. Key tactical or individual performances\n"
        f"4. The NRI/diaspora angle (naturally woven in, not bolted on)\n"
        f"5. What this means for Group {group} going forward\n"
        f"6. Link to The Videshi's World Cup tracker: [World Cup tracker](/world-cup)\n\n"
        f"Important: Do NOT fabricate specific scorer names or minute details. "
        f"If the web context doesn't provide them, focus on tactical narrative and atmosphere. "
        f"Place social embed URLs on their own line (not as markdown links).\n"
        f"Write 600-800 words minimum."
    )

    print(f"   🤖 Generating article with GPT-4o...")
    gpt_result = call_openai_match(system_prompt, user_prompt)

    if gpt_result and gpt_result.get("body"):
        headline = gpt_result.get("headline", f"{home} {match['score']} {away}: World Cup Group {group} Report")
        subheadline = gpt_result.get("subheadline", f"Group {group} action from {city} — Day {day_number} of the 2026 FIFA World Cup")
        body = gpt_result["body"]
        diaspora_angle = gpt_result.get("diaspora_angle", f"World Cup Group {group} match at {venue} in {city}.")
        gpt_sources = gpt_result.get("sources", [])
        print(f"   ✅ GPT article generated: {headline[:70]}...")
        print(f"   📝 Word count: ~{len(body.split())}")
    else:
        print(f"   ⚠️  GPT generation failed, falling back to template article")
        return _generate_match_article_template(match, all_data)

    # Ensure the closing links are present
    if "/world-cup" not in body:
        body += (
            "\n\n---\n\n"
            "*Follow our [World Cup tracker](/world-cup) for live scores, group standings, "
            "and highlights. Read the full [day's recap](/articles/world-cup-recap-"
            f"{match['date']}) for all of today's results.*\n"
        )

    # Image: try Wikimedia Commons stadium photo first, then team wiki image
    print(f"   🖼️  Sourcing image...")
    image_url = fetch_stadium_image(venue, city)
    image_caption = f"{venue} in {city} — venue for {home} vs {away} at the 2026 FIFA World Cup (Wikimedia Commons)"
    if not image_url:
        featured_team = home if hg >= ag else away
        image_url = get_wiki_image(featured_team) or WC_IMAGE
        image_caption = f"{home} vs {away} — FIFA World Cup 2026, Group {group}"
    if image_url:
        print(f"   ✅ Image: {image_url[:80]}...")

    # Tags
    tag_list = [
        "world-cup", "fifa", "sports", "world-cup-2026",
        home.lower().replace(" ", "-"),
        away.lower().replace(" ", "-"),
        city.lower().replace(" ", "-").replace("/", "-"),
        f"group-{group.lower()}",
    ]

    # Sources — merge GPT suggestions with default
    sources = [
        {"name": "FIFA.com", "url": "https://www.fifa.com/fifaplus/en/tournaments/mens/worldcup/canadamexicousa2026"},
    ]
    if gpt_sources:
        for s in gpt_sources[:3]:
            if isinstance(s, dict) and s.get("name") and s.get("url"):
                if s["url"].startswith("http") and s not in sources:
                    sources.append(s)

    return {
        "id": str(uuid.uuid4()),
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "tags": list(set(tag_list)),
        "status": "review",
        "published_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": diaspora_angle,
        "body": body,
        "sources": json.dumps(sources),
    }


def _generate_match_article_template(match, all_data):
    """Fallback: generate a template-based article when GPT is unavailable."""
    hg, ag = parse_score(match)
    result_text = get_match_result_text(match)
    slug = generate_match_slug(match)
    target_date = date.fromisoformat(match["date"])
    day_number = compute_day_number(target_date)
    date_str = target_date.strftime("%A, %B %d")

    # Headline
    if hg == ag:
        headline = f"{match['home']} and {match['away']} Share the Points in {hg}-{ag} Draw"
    elif hg > ag:
        if hg - ag >= 3:
            headline = f"{match['home']} Demolish {match['away']} {hg}-{ag} in World Cup Opener"
        else:
            headline = f"{match['home']} Beat {match['away']} {hg}-{ag} at {match['venue']}"
    else:
        if ag - hg >= 3:
            headline = f"{match['away']} Demolish {match['home']} {ag}-{hg} in World Cup Clash"
        else:
            headline = f"{match['away']} Edge Past {match['home']} {ag}-{hg} at {match['venue']}"

    subheadline = (
        f"Group {match['group']} action from {match['city']} — "
        f"Day {day_number} of the 2026 FIFA World Cup"
    )

    # Build body
    body = build_match_section(match, 0)

    # Add NRI angle
    nri_cities = ["San Francisco Bay Area", "New York/New Jersey", "Los Angeles",
                  "Houston", "Dallas", "Boston", "Miami", "Seattle", "Philadelphia"]
    city = match.get("city", "")
    if any(c in city for c in nri_cities):
        body += (
            f"\n\n## For NRIs Near {city}\n\n"
            f"This match was played at {match['venue']} in {city}, one of America's "
            f"largest Indian-American metro areas. Check our "
            f"[NRI Venue Guide](/world-cup?tab=nri) for nearby desi restaurants, "
            f"transit tips, and community watch parties.\n\n"
        )
    else:
        body += (
            f"\n\n## The NRI Angle\n\n"
            f"The 2026 World Cup is being played across 16 US, Canadian, and Mexican "
            f"cities — many home to large Indian-American communities. Whether you're "
            f"watching from home or heading to a stadium, check our "
            f"[NRI Guide](/world-cup?tab=nri) for venue tips and local desi community info.\n\n"
        )

    # Closing
    body += (
        "---\n\n"
        "*Follow our [World Cup tracker](/world-cup) for live scores, group standings, "
        "and highlights. Read the full [day's recap](/articles/world-cup-recap-"
        f"{match['date']}) for all of today's results.*\n"
    )

    # Image
    featured_team = match["home"] if hg >= ag else match["away"]
    image_url = get_wiki_image(featured_team) or WC_IMAGE

    # Tags
    tag_list = [
        "world-cup", "fifa", "sports", "world-cup-2026",
        match["home"].lower().replace(" ", "-"),
        match["away"].lower().replace(" ", "-"),
        match["city"].lower().replace(" ", "-").replace("/", "-"),
        f"group-{match['group'].lower()}",
    ]

    return {
        "id": str(uuid.uuid4()),
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "category": "sports",
        "vertical": "sports",
        "tags": list(set(tag_list)),
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "image_url": image_url,
        "image_caption": f"{match['home']} vs {match['away']} — FIFA World Cup 2026, Group {match['group']}",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": f"World Cup Group {match['group']} match at {match['venue']} in {city}.",
        "body": body,
        "sources": json.dumps([
            {"name": "FIFA.com", "url": "https://www.fifa.com/fifaplus/en/tournaments/mens/worldcup/canadamexicousa2026"},
        ]),
    }


def check_duplicate(slug):
    """Check if an article with this slug already exists."""
    import requests as req
    try:
        r = req.get(
            f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id",
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
            },
            timeout=30,
        )
        if r.ok:
            existing = r.json()
            return len(existing) > 0
    except Exception as e:
        print(f"⚠️  Could not check for duplicates: {e}")
    return False


def publish_article(article):
    """Publish article to Supabase p2_articles."""
    import requests as req
    r = req.post(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def main():
    # Determine target date
    if len(sys.argv) > 1:
        target_date = date.fromisoformat(sys.argv[1])
    else:
        # Default: yesterday
        target_date = date.today() - timedelta(days=1)

    target_date_str = target_date.isoformat()
    day_number = compute_day_number(target_date)

    print(f"🏆 World Cup Recap Writer — {target_date_str} (Day {day_number})")
    print(f"{'='*50}")

    # Validate date range
    if target_date < TOURNAMENT_START or target_date > TOURNAMENT_END:
        print(f"ℹ️  {target_date_str} is outside the tournament window ({TOURNAMENT_START} to {TOURNAMENT_END}). Exiting.")
        return

    # Load matches
    if not WC_JSON.exists():
        print(f"❌ worldcup.json not found at {WC_JSON}")
        sys.exit(1)

    matches, all_data = load_matches(target_date_str)

    if not matches:
        print(f"ℹ️  No finished matches found for {target_date_str}. Exiting.")
        return

    print(f"📋 Found {len(matches)} finished match(es):")
    for m in matches:
        print(f"   {m['home']} {m['score']} {m['away']} (Group {m['group']}) @ {m['venue']}")

    # Check for duplicate recap
    slug = generate_slug(target_date)
    recap_exists = check_duplicate(slug)
    if recap_exists:
        print(f"⚠️  Recap article '{slug}' already exists. Skipping recap, checking individual match articles...")

    if not recap_exists:
        # Generate article
        print(f"\n✍️  Generating recap article...")
        article = generate_article(matches, target_date, all_data)

        print(f"   Headline: {article['headline']}")
        print(f"   Subheadline: {article['subheadline']}")
        print(f"   Slug: {article['slug']}")
        print(f"   Word count: ~{len(article['body'].split())}")

        # Publish
        print(f"\n📤 Publishing to Supabase...")
        try:
            result = publish_article(article)
            print(f"✅ Published! Article ID: {article['id']}")
            print(f"   URL: https://thevideshi.com/articles/{article['slug']}")
        except Exception as e:
            print(f"❌ Failed to publish: {e}")
            # Save locally as backup
            backup_path = Path(__file__).parent / f"recap-{target_date_str}.json"
            backup_path.write_text(json.dumps(article, indent=2))
            print(f"💾 Saved backup to {backup_path}")

    # Generate and publish individual match articles
    print(f"\n📝 Generating individual match articles...")
    for m in matches:
        match_slug = generate_match_slug(m)
        if check_duplicate(match_slug):
            print(f"   ⚠️  {match_slug} already exists, skipping")
            continue
        try:
            match_article = generate_match_article(m, all_data)
            publish_article(match_article)
            print(f"   ✅ {m['home']} vs {m['away']}: https://thevideshi.com/articles/{match_slug}")
        except Exception as e:
            print(f"   ❌ {m['home']} vs {m['away']}: {e}")


if __name__ == "__main__":
    main()
