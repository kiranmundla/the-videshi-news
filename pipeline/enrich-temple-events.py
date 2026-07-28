#!/usr/bin/env python3
"""
enrich-temple-events.py — Add descriptions and addresses to BAPS/ISKCON events.

These are well-known Hindu celebrations at known temples. Generates descriptions
based on festival names and links temple addresses.

Usage:
  python3 -u enrich-temple-events.py                    # Enrich all
  python3 -u enrich-temple-events.py --dry-run           # Preview
  python3 -u enrich-temple-events.py --source baps       # BAPS only
"""

import os, sys, json, re, subprocess, argparse, time

sys.stdout.reconfigure(line_buffering=True)

# ── Env ──────────────────────────────────────────────────────────────────────
ENV_FILE = os.path.expanduser("~/.env.supabase")
if os.path.exists(ENV_FILE):
    for line in open(ENV_FILE):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
SB_HOST = SUPABASE_URL.replace("https://", "")

# ── Known Hindu/ISKCON festival descriptions ────────────────────────────────
FESTIVAL_DESCRIPTIONS = {
    "diwali": "Diwali, the Festival of Lights, is one of the most celebrated Hindu festivals worldwide. Join the community for traditional prayers (puja), decorative oil lamps (diyas), rangoli art, cultural performances, and festive sweets. The celebration marks the victory of light over darkness and good over evil.",
    "holi": "Holi, the Festival of Colors, celebrates the arrival of spring with vibrant colors, music, and dance. Enjoy traditional color play, devotional songs, festive food, and community celebration. The festival symbolizes the triumph of good over evil and the joy of new beginnings.",
    "janmashtami": "Janmashtami celebrates the birth of Lord Krishna, one of the most beloved deities in Hinduism. The celebration includes devotional singing (bhajans), dramatic reenactments of Krishna's life, midnight prayers marking his birth time, festive food, and cultural programs for all ages.",
    "ganesh chaturthi": "Ganesh Chaturthi celebrates the birth of Lord Ganesha, the remover of obstacles and god of new beginnings. The celebration features traditional prayers, devotional music, cultural performances, and festive offerings (prasad). A beautiful and uplifting community gathering.",
    "navratri": "Navratri is a nine-night festival celebrating the divine feminine power (Shakti). Join the community for traditional Garba and Dandiya Raas dances, devotional music, cultural programs, and festive food. A joyful celebration of music, dance, and devotion.",
    "ram navami": "Ram Navami celebrates the birth of Lord Rama, an avatar of Vishnu and the hero of the epic Ramayana. The celebration includes devotional chanting, religious discourses, cultural performances, and festive offerings to the community.",
    "raksha bandhan": "Raksha Bandhan celebrates the sacred bond between brothers and sisters. The celebration includes traditional tying of the protective thread (rakhi), prayers, cultural programs, and festive sweets. A heartwarming celebration of family bonds.",
    "guru purnima": "Guru Purnima honors spiritual teachers and mentors. The celebration includes special prayers, devotional talks, expressions of gratitude to teachers, and community gathering. A day to reflect on the importance of guidance in life.",
    "mahashivratri": "Mahashivratri, the Great Night of Lord Shiva, is one of the most significant Hindu festivals. The celebration features night-long prayers and meditation, traditional abhishekam (ritual bathing of the Shiva lingam), devotional songs, and fasting.",
    "ratha yatra": "Ratha Yatra, the Festival of Chariots, is one of the oldest and grandest Hindu festivals. Join the community for a colorful chariot procession, devotional music and dancing, cultural performances, and free vegetarian feast (prasadam). A spectacular celebration open to all.",
    "pramukh swami maharaj jayanti": "A celebration honoring Pramukh Swami Maharaj, the fifth spiritual successor of Bhagwan Swaminarayan and a beloved spiritual leader who inspired millions worldwide with his selfless service and devotion. The program includes prayers, tributes, and cultural presentations.",
    "mahant swami maharaj jayanti": "A celebration honoring His Holiness Mahant Swami Maharaj, the current spiritual head of BAPS Swaminarayan Sanstha. The program includes prayers, devotional music, tributes, and cultural presentations celebrating his spiritual leadership and service.",
    "mandir patotsav": "Mandir Patotsav marks the anniversary of the temple's consecration. This special celebration includes elaborate prayers (pujas), devotional music, cultural performances, and festive community gathering commemorating the sacred occasion of the temple's establishment.",
    "hari jayanti": "Hari Jayanti celebrates the manifestation of Bhagwan Swaminarayan, the central figure of the Swaminarayan tradition. The celebration includes special prayers, devotional music, dramatic presentations of his life, and festive community gathering.",
    "pushpadolotsav": "Pushpadolotsav is a beautiful spring celebration involving the showering of flower petals on the sacred murtis (deities). This colorful and devotional event features traditional prayers, devotional singing, and a joyous atmosphere celebrating the beauty of spring.",
}

# Keywords to match festival titles (case-insensitive)
FESTIVAL_KEYWORDS = {
    "diwali": ["diwali", "deepavali"],
    "holi": ["holi celebration", "festival of color"],
    "janmashtami": ["janmashtami", "janmastami", "krishna jayanti"],
    "ganesh chaturthi": ["ganesh chaturthi", "ganesh utsav", "ganeshotsav"],
    "navratri": ["navratri", "navaratri", "garba", "dandiya"],
    "ram navami": ["ram navami", "ramnavami"],
    "raksha bandhan": ["raksha bandhan", "rakshabandhan", "rakhi"],
    "guru purnima": ["guru purnima"],
    "mahashivratri": ["mahashivratri", "maha shivratri", "shivaratri"],
    "ratha yatra": ["ratha yatra", "rath yatra", "rathayatra", "festival of chariots"],
    "pramukh swami maharaj jayanti": ["pramukh swami", "pramukh swami maharaj jayanti"],
    "mahant swami maharaj jayanti": ["mahant swami maharaj jayanti", "mahant swami"],
    "mandir patotsav": ["mandir patotsav", "patotsav"],
    "hari jayanti": ["hari jayanti"],
    "pushpadolotsav": ["pushpadolotsav"],
}


def match_festival(title: str) -> str | None:
    """Match event title to a known festival."""
    lower_title = title.lower().strip()
    for festival, keywords in FESTIVAL_KEYWORDS.items():
        for kw in keywords:
            if kw in lower_title:
                return festival
    return None


def generate_description(title: str, venue_name: str, city: str, state: str) -> str | None:
    """Generate a description for a temple event based on its title."""
    festival = match_festival(title)
    if festival and festival in FESTIVAL_DESCRIPTIONS:
        base = FESTIVAL_DESCRIPTIONS[festival]
        location = f" at {venue_name}" if venue_name else ""
        city_state = f" in {city}, {state}" if city else ""
        return f"{base}\n\nThis celebration takes place{location}{city_state}. All are welcome."
    
    # Generic temple event description for unmatched events
    location = f" at {venue_name}" if venue_name else ""
    city_state = f" in {city}, {state}" if city else ""
    return f"Join the community for this special celebration{location}{city_state}. The program includes traditional prayers, devotional music, and cultural activities. All are welcome to participate in this uplifting gathering."


def fetch_events(sources: list):
    """Fetch upcoming temple events needing enrichment."""
    source_filter = ",".join(sources)
    url = (
        f"{SUPABASE_URL}/rest/v1/events"
        f"?source=in.({source_filter})"
        f"&date=gte.{time.strftime('%Y-%m-%d')}"
        f"&select=id,title,description,long_description,venue_name,city,state,source"
        f"&order=date.asc"
        f"&limit=500"
    )
    r = subprocess.run(
        ["curl", "-sS", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, text=True, timeout=30
    )
    return json.loads(r.stdout)


def update_event(event_id: str, updates: dict) -> bool:
    payload = json.dumps(updates)
    url = f"{SUPABASE_URL}/rest/v1/events?id=eq.{event_id}"
    r = subprocess.run(
        ["curl", "-sS", "-X", "PATCH", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=minimal",
         "-d", payload],
        capture_output=True, text=True, timeout=15
    )
    return r.returncode == 0 and "error" not in r.stdout.lower()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="all", help="baps, iskcon, or all")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sources = ["baps", "iskcon"] if args.source == "all" else [args.source]
    events = fetch_events(sources)
    
    # Filter to events needing descriptions
    needs_work = [e for e in events if not e.get("long_description") or len(e.get("long_description", "")) < 50]
    
    print(f"Total upcoming temple events: {len(events)}")
    print(f"Events needing descriptions: {len(needs_work)}")
    
    updated = 0
    matched = 0
    generic = 0
    
    for e in needs_work:
        title = e["title"]
        festival = match_festival(title)
        desc = generate_description(title, e.get("venue_name", ""), e.get("city", ""), e.get("state", ""))
        
        if not desc:
            continue
        
        # Use first sentence as short description
        short = desc.split(".")[0] + "." if "." in desc else desc[:200]
        
        patch = {
            "long_description": desc,
            "description": short,
        }
        
        if festival:
            matched += 1
            tag = f"✅ {festival}"
        else:
            generic += 1
            tag = "📝 generic"
        
        if args.dry_run:
            print(f"  [{tag}] {title[:50]} | {desc[:80]}...")
        else:
            if update_event(e["id"], patch):
                print(f"  [{tag}] {title[:50]}")
                updated += 1
            else:
                print(f"  ❌ Failed: {title[:50]}")
    
    print(f"\nDone: {updated} updated, {matched} known festivals, {generic} generic descriptions")


if __name__ == "__main__":
    main()
