#!/usr/bin/env python3
"""
videshi-ipl.py — Fetch IPL 2026 standings and write to public/data/ipl-standings.json.

Scrapes the ESPN Cricinfo / Cricbuzz / durhamccc points table page for current
standings. Falls back to keeping existing JSON if scrape fails.

Run:  python3 pipeline/videshi-ipl.py
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("pip install requests beautifulsoup4 first")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT = PROJECT_ROOT / "public" / "data" / "ipl-standings.json"

# Team short-name mapping
TEAM_SHORT = {
    "Gujarat Titans": "GT",
    "Royal Challengers Bengaluru": "RCB",
    "Royal Challengers Bangalore": "RCB",
    "Sunrisers Hyderabad": "SRH",
    "Punjab Kings": "PBKS",
    "Chennai Super Kings": "CSK",
    "Rajasthan Royals": "RR",
    "Delhi Capitals": "DC",
    "Kolkata Knight Riders": "KKR",
    "Mumbai Indians": "MI",
    "Lucknow Super Giants": "LSG",
}

SOURCES = [
    # (url, parser_function_name)
    ("https://www.espncricinfo.com/series/ipl-2026-1473498/points-table-standings", "parse_espn"),
    ("https://www.durhamccc.co.uk/ipl-2026-points-table/", "parse_durham"),
]

def clean_team_name(raw: str) -> str:
    """Strip (E), (Q) markers, extra whitespace."""
    return re.sub(r"\s*\([A-Z]+\)\s*", "", raw).strip()

def parse_durham(html: str) -> list[dict] | None:
    """Parse the durhamccc.co.uk IPL points table."""
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    if not tables:
        return None

    standings = []
    for table in tables:
        rows = table.find_all("tr")
        for row in rows[1:]:  # skip header
            cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
            if len(cells) < 7:
                continue
            # Expected: Rank, Team, P, W, L, NR, Pts, NRR
            try:
                team_raw = cells[1]
                team_clean = clean_team_name(team_raw)
                short = TEAM_SHORT.get(team_clean, team_clean[:3].upper())
                entry = {
                    "team": team_clean,
                    "short": short,
                    "played": int(cells[2]),
                    "won": int(cells[3]),
                    "lost": int(cells[4]),
                    "nr": int(cells[5]),
                    "nrr": cells[7] if len(cells) > 7 else cells[6],
                    "points": int(cells[6]),
                    "position": int(cells[0]) if cells[0].isdigit() else len(standings) + 1,
                }
                # Make sure nrr looks like a number
                nrr = entry["nrr"]
                if nrr and not nrr.startswith(("+", "-")):
                    try:
                        float(nrr)
                        entry["nrr"] = f"+{nrr}" if float(nrr) >= 0 else nrr
                    except ValueError:
                        pass
                standings.append(entry)
            except (ValueError, IndexError):
                continue
    return standings if len(standings) >= 8 else None

def parse_espn(html: str) -> list[dict] | None:
    """Parse ESPN Cricinfo points table page."""
    soup = BeautifulSoup(html, "html.parser")
    # ESPN uses complex React rendering; try to find table data
    tables = soup.find_all("table")
    if not tables:
        return None
    standings = []
    for table in tables:
        rows = table.find_all("tr")
        for i, row in enumerate(rows):
            cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
            if len(cells) < 6:
                continue
            # Look for team name cell
            for j, cell in enumerate(cells):
                for full_name, short in TEAM_SHORT.items():
                    if full_name.lower() in cell.lower() or short.lower() == cell.lower():
                        try:
                            nums = [c for c in cells if c.replace(".", "").replace("-", "").replace("+", "").isdigit()]
                            if len(nums) >= 4:
                                standings.append({
                                    "team": full_name,
                                    "short": short,
                                    "played": int(nums[0]),
                                    "won": int(nums[1]),
                                    "lost": int(nums[2]),
                                    "nr": 0,
                                    "nrr": nums[-1] if "." in nums[-1] else "+0.000",
                                    "points": int(nums[3]),
                                    "position": len(standings) + 1,
                                })
                        except (ValueError, IndexError):
                            pass
                        break
    return standings if len(standings) >= 8 else None

def fetch_standings() -> list[dict] | None:
    """Try each source until we get valid standings."""
    parsers = {"parse_espn": parse_espn, "parse_durham": parse_durham}
    for url, parser_name in SOURCES:
        parser = parsers.get(parser_name)
        if not parser:
            continue
        try:
            print(f"  Trying {url} ...")
            resp = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (compatible; TheVideshi/1.0)"
            })
            if resp.status_code != 200:
                print(f"  → HTTP {resp.status_code}, skipping")
                continue
            result = parser(resp.text)
            if result:
                print(f"  → Got {len(result)} teams from {parser_name}")
                return result
            else:
                print(f"  → Parser returned no data, trying next")
        except Exception as e:
            print(f"  → Error: {e}")
    return None

def main():
    print("=== IPL Data Updater ===")

    # Load existing data
    existing = {}
    if OUTPUT.exists():
        try:
            existing = json.loads(OUTPUT.read_text())
        except json.JSONDecodeError:
            pass

    # Fetch new standings
    standings = fetch_standings()

    if standings:
        existing["standings"] = standings
        existing["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"  Updated standings with {len(standings)} teams")
    else:
        print("  Could not fetch new standings — keeping existing data")
        if not existing.get("standings"):
            print("  ERROR: No existing standings either!")
            sys.exit(1)

    # Ensure required fields
    existing.setdefault("season", "IPL 2026")

    # Write output
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n")
    print(f"  Wrote {OUTPUT}")

if __name__ == "__main__":
    main()
