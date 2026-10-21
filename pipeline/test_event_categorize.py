#!/usr/bin/env python3
"""Regression tests for event categorization (2026-10-21).

Incident: "Bollywood and Bites" (AllEvents, Pleasanton — a women's
Bollywood dance/social evening) was badged Religious because categorize()
substring-matched "pooja" in the FULL description's agenda line
"Host: Bandhavi & Pooja" — a person's name, not the ritual. Fixes under
test: title-first categorization, short-description lead only,
word-boundary keyword matching, TM's bare "guru" removed (Guru Randhawa
is a singer), Sulekha boundary matching.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FAILURES = []


def check(name, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'} {name}: got {got!r}, want {want!r}")
    if not ok:
        FAILURES.append(name)


def load(mod_name, filename):
    spec = importlib.util.spec_from_file_location(mod_name, os.path.join(HERE, filename))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ae = load("scrape_allevents", "scrape-allevents.py")
tm = load("events_tm_refresh_v2", "events-tm-refresh-v2.py")
su = load("scrape_sulekha_events", "scrape-sulekha-events.py")

BB_LONG = (
    "An evening of Bollywood dancing, fun games, delicious bites & drinks, "
    "laughter and new connections-come solo or bring a friend!!\n\n"
    "About this Event\n\nCome for the Bollywood, stay for the bites and leave "
    "with new connections and unforgetable memories!\n\nAgenda\n\n"
    "06:00 PM - 07:00 PM\nBollywood Beats - Dance & groove to your favorite hits.\n"
    "Host: Bandhavi & Pooja\n\n07:00 PM - 08:00 PM\nSip & Socialize - Drinks, "
    "Bites & good conversations."
)

# ── The incident ──
check("allevents: Bollywood and Bites (long desc, host named Pooja)",
      ae.categorize("Bollywood and Bites", BB_LONG), "Entertainment")
check("allevents: Bollywood and Bites (short desc)",
      ae.categorize("Bollywood and Bites",
                    "An evening of Bollywood dancing, fun games, delicious "
                    "bites & drinks, laughter and new connections"),
      "Entertainment")

# ── Genuine religious events still land Religious ──
check("allevents: Diwali Puja",
      ae.categorize("Diwali Puja and Aarti at Hindu Temple", ""), "Religious")
check("allevents: sunrise yoga",
      ae.categorize("Sunrise Yoga and Meditation", ""), "Religious")
check("allevents: vague title, religious lead description",
      ae.categorize("Saturday Morning Session",
                    "Join us for yoga and meditation at the mandir hall"), "Religious")
check("allevents: yogathon",
      ae.categorize("Yogathon for Charity", ""), "Religious")

# ── Substring traps ──
check("allevents: holiday is not Holi",
      ae.categorize("Holiday Craft Fair and Bake Sale", ""), "Entertainment")
check("allevents: party is not art/culture",
      ae.categorize("Neighborhood Block Party", ""), "Community")
check("allevents: laughter is not a comedy show",
      ae.categorize("An Evening of Music, Dance and Laughter", ""), "Music")

# ── Ordinary categories still work ──
check("allevents: kathak recital",
      ae.categorize("Kathak Dance Recital", ""), "Dance")
check("allevents: comedy night",
      ae.categorize("Desi Comedy Night with Raj Kumar", ""), "Comedy")
check("allevents: food festival title hits Festival first (existing order)",
      ae.categorize("Grand Diwali Festival and Food Bazaar", ""), "Festival")

# ── Ticketmaster ──
check("tm: Guru Randhawa concert is Entertainment, not Spiritual",
      tm.categorize("Guru Randhawa Live in Concert"), "Entertainment")
check("tm: temple kirtan stays Spiritual",
      tm.categorize("Evening Kirtan at the Mandir"), "Spiritual")
check("tm: charity run",
      tm.categorize("Annual Charity Run 5K"), "Sports & Fitness")

# ── Sulekha ──
check("sulekha: holiday special is not Holi",
      su.guess_category("Holiday Special Kathak Recital"), "Dance")
check("sulekha: bhajan evening",
      su.guess_category("Bhajan Sandhya with Local Artists"), "Religious")
check("sulekha: diwali mela",
      su.guess_category("Grand Diwali Mela 2026"), "Festival")

print(f"\n{18 - len(FAILURES)}/18 checks passed" if not FAILURES else f"\nFAILURES: {FAILURES}")
sys.exit(1 if FAILURES else 0)
