"""Regression tests for scrape-temples' garbled-title gate.

The 2026-11-01 ISKCON Houston row carried a description fragment as
its title ('29, 2026, at ISKCON of Houston. As we explore the subtle
architecture of honoring others, enjoy blis…') because the generic
date-anchored parser captures whatever prose follows a date.
_title_looks_garbled must reject that class while passing real
festival/event names, including abbreviation titles like 'St. …'.
Run: python3 -u test_title_garble_gate.py
"""
import importlib.util
import os
import sys

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "scrape_temples", os.path.join(HERE, "scrape-temples.py"))
st = importlib.util.module_from_spec(spec)
spec.loader.exec_module(st)

FAIL = []


def check(label, cond):
    print(("  ok " if cond else "  FAIL ") + label)
    if not cond:
        FAIL.append(label)


GARBLED = [
    "29, 2026, at ISKCON of Houston. As we explore the subtle "
    "architecture of honoring others, enjoy blis",
    "2026 Annual Dinner and Cultural Program",
    "November 25 Celebration of Lights and Music",
    "Join us for an evening of devotion. Please bring your family",
]
LEGIT = [
    "Govardhan Puja",
    "Thanksgiving Retreat at ISKCON of Houston",
    "Sri Krishna Janmashtami",
    "St. Patrick's Day Celebration",
    "Dr. Radhakrishnan Memorial Lecture",
    "Diwali Celebration - Special Abhishek & Kirtan",
    "Kartik Deepotsavam 2026",
    "Vaikuntha Ekadashi",
]

for t in GARBLED:
    check(f"garbled rejected: {t[:45]}", st._title_looks_garbled(t))
for t in LEGIT:
    check(f"legit passes: {t[:45]}", not st._title_looks_garbled(t))

print(f"\n{'ALL PASS' if not FAIL else 'FAILURES: ' + str(FAIL)}")
sys.exit(1 if FAIL else 0)
