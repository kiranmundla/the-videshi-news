#!/usr/bin/env python3
"""Sports connection gate tests for daily-happenings-v2.py
(Kiran, 2026-11-15).

A sports happening stays a listing, but only earns a published
brief when the fixture itself has an India/diaspora connection.
Regression cases are the three 3/10 briefs Kiran ordered
unpublished on 2026-11-15: Bangladesh v West Indies,
Pakistan v Sri Lanka, South Africa v Bangladesh — all let
through by tournament-level relevance keywords (Asia Cup /
ICC) despite no Indian side playing.

Run: python3 -u test_happenings_sports_gate.py  (no network)
"""
import importlib.util
import os
import sys

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")
os.environ.setdefault("OPENAI_API_KEY", "test-key")

spec = importlib.util.spec_from_file_location(
    "daily_happenings_v2",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "daily-happenings-v2.py"))
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)

conn = H._sports_brief_connection
total = fails = 0


def check(name, got, want):
    global total, fails
    total += 1
    if got == want:
        print(f"  ok {total}: {name}")
    else:
        fails += 1
        print(f"  FAIL {total}: {name} — got {got}, want {want}")


def sports(teams, league="", label="", detail=""):
    return {"category": "sports", "search_terms": teams,
            "league": league, "label": label, "detail": detail}


# The three unpublished briefs — must stay suppressed.
check("regression: Bangladesh v West Indies (Asia Cup)",
      conn(sports(["bangladesh", "west indies"], "Asia Cup")),
      False)
check("regression: Pakistan v Sri Lanka (Asia Cup)",
      conn(sports(["pakistan", "sri lanka"], "Asia Cup")),
      False)
check("regression: South Africa v Bangladesh (ICC ODI series)",
      conn(sports(["south africa", "bangladesh"],
                  "ICC Cricket World Cup League 2")),
      False)
# West Indies must never read as India.
check("west indies is not india",
      conn(sports(["west indies", "england"], "Test Series")),
      False)
# Genuine connections — briefs still allowed.
check("india playing",
      conn(sports(["india", "new zealand"], "ODI Series")), True)
check("india women",
      conn(sports(["india women", "australia women"], "T20I")),
      True)
check("india a",
      conn(sports(["india a", "south africa a"], "Unofficial ODI")),
      True)
check("ipl fixture (franchises, league is the connection)",
      conn(sports(["mumbai indians", "chennai super kings"],
                  "Indian Premier League")),
      True)
check("mlc fixture (US diaspora league)",
      conn(sports(["mi new york", "texas super kings"],
                  "Major League Cricket")),
      True)
check("indian club in a cup fixture",
      conn(sports(["mohun bagan", "al-ahli"], "AFC Cup")), True)
# Non-sports categories are untouched by this gate.
check("earnings item unaffected",
      conn({"category": "markets-finance", "search_terms": [],
            "league": "", "label": "Apple Earnings"}), True)
check("festival item unaffected",
      conn({"category": "news", "search_terms": [],
            "league": "", "label": "Diwali"}), True)
# Tennis (no teams): fail closed unless India is named.
check("tennis, no india named",
      conn(sports([], "", "Alcaraz vs Sinner — Wimbledon Final")),
      False)
check("tennis at indian wells is not a connection",
      conn(sports([], "", "Indian Wells Open — Quarterfinal")),
      False)
check("tennis, india named in detail",
      conn(sports([], "", "Men's Singles — Round 2",
                  "India's Rohan Bopanna in doubles action")),
      True)

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
