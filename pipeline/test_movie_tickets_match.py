#!/usr/bin/env python3
"""Regression tests for build-movie-tickets.py title_match.

The 2026-11-16 case: the old token-overlap rule resolved "Pyre" to
Fandango's "Children of the Pyre" — a different film. A wrong ticket
link is worse than no link; matching must fail closed.
"""
import importlib.util
import os

spec = importlib.util.spec_from_file_location(
    "build_movie_tickets",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "build-movie-tickets.py"),
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
title_match = mod.title_match

CASES = [
    # (query title, fandango slug, expected)
    ("Pyre", "children-of-the-pyre-125636", False),          # the 2026-11-16 bug
    ("Pyre", "pyre-2026-248000", True),
    ("Mandaadi", "mandaadi-2026-247228", True),
    ("Drishyam: The Conclusion", "drishyam-the-conclusion-2026-247556", True),
    ("The Vvaan: Force of the Forrest", "the-vvaan-force-of-the-forrest-247541", True),
    ("Prahaar", "prahaar-the-untold-story-of-ujjwal-nikam-2026-247958", True),  # subtitle suffix ok
    ("Ramayana: Part 1", "godzilla-minus-zero-2026-243973", False),
    ("Ramayana: Part 1", "ramayana-part-1-2026-248001", True),
    ("Mookuthi Amman 2", "mookuthi-amman-2-248355", True),
    ("418", "418-2026-246528", True),
    ("418", "room-418-2026-111111", False),
    ("Cult", "cult-248221", True),
    ("Cult", "the-cult-248221", False),
    ("Scene", "scene-2026-248114", True),
    ("Jailer 2", "jailer-2-247862", True),
    ("Jailer 2", "jailer-247862", False),
]

def main():
    fails = 0
    for title, slug, expected in CASES:
        got = title_match(title, slug)
        ok = got == expected
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}  title_match({title!r}, {slug!r}) = {got} (expected {expected})")
    print(f"\n{len(CASES) - fails}/{len(CASES)} passed")
    return 1 if fails else 0

if __name__ == "__main__":
    raise SystemExit(main())
