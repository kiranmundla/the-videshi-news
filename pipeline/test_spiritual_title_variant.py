"""Regression tests for scrape-spiritual-events' title-variant guard.

The LLM extractor returned title variants for single courses
('10-Day' / '10-Day Course' / '10-Day Course for Men's Course'),
each keyed as a distinct source_id — 26 duplicate rows were cleaned
by hand on 2026-11-15. _is_title_variant must catch subset-shaped
variants while NEVER merging concurrent men's/women's courses.
Run: python3 -u test_spiritual_title_variant.py
"""
import importlib.util
import os
import sys

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
spec = importlib.util.spec_from_file_location(
    "scrape_spiritual", os.path.join(HERE, "scrape-spiritual-events.py"))
sp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sp)

FAIL = []


def check(label, cond):
    print(("  ok " if cond else "  FAIL ") + label)
    if not cond:
        FAIL.append(label)


V = sp._is_title_variant
check("bare duration is variant of full title",
      V("10-Day", "10-Day Course for Men's Course"))
check("generic is variant of gendered",
      V("10-Day Course", "10-Day Women's Course"))
check("generic is variant of old-students",
      V("1-Day Course", "1-Day Course for Old Students"))
check("men's vs women's NOT variants",
      not V("10-Day Men's Course", "10-Day Women's Course"))
check("women's vs men's NOT variants (reverse)",
      not V("10-Day Women's Course", "10-Day Men's Course"))
check("different courses NOT variants",
      not V("10-Day Course", "3-Day Meditation Retreat"))
check("identical titles are variants", V("10-Day Course", "10-Day Course"))

print(f"\n{'ALL PASS' if not FAIL else 'FAILURES: ' + str(FAIL)}")
sys.exit(1 if FAIL else 0)
