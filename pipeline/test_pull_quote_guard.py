#!/usr/bin/env python3
"""
test_pull_quote_guard.py — regression tests for the pull-quote
fragment guard (2026-11-14).

Live failure: the Janakpur–Ayodhya train article shipped the
pull quote "Route and schedule Besides its terminal stations,
the train will have commercial stoppages at Jaynagar,
Madhubani, …" — extract_pull_quote stripped ALL HTML tags, so
the <h2> heading merged into the stops-list sentence, which
then scored on its mid-article position bonus alone.

Run: python3 test_pull_quote_guard.py   (exit 0 = all pass)
"""
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
E = SourceFileLoader(
    "enrich_articles",
    str(Path(__file__).resolve().parent / "enrich-articles.py"),
).load_module()

FAILS = []


def check(name, cond, extra=""):
    print(("  ✓ " if cond else "  ✗ ") + name
          + (f" — {extra}" if extra and not cond else ""))
    if not cond:
        FAILS.append(name)


STOPS = ("Route and schedule Besides its terminal stations, "
         "the train will have commercial stoppages at Jaynagar, "
         "Madhubani, Shisho, Sitamarhi, Raxaul, Narkatiaganj, "
         "Gorakhpur, Basti, Mankapur and Ayodhya Dham.")

print("valid_pull_quote")
check("heading-glued stops list rejected",
      E.valid_pull_quote(STOPS, ["Route and schedule"]) is False)
check("enumeration rejected on commas alone",
      E.valid_pull_quote(STOPS, []) is False)
check("fragment opener 'Besides …' rejected",
      E.valid_pull_quote(
          "Besides its terminal stations, the train will also "
          "stop at Jaynagar on its weekly run north.", []) is False)
check("a complete statement passes",
      E.valid_pull_quote(
          "The service will cover approximately 604 kilometres "
          "between the two temple cities.", []) is True)

BODY = """
<div class="key-takeaways"><ul><li>The government announced a new weekly train service.</li></ul></div>
<p>A weekly train will connect Janakpur Dham in Nepal with Ayodhya in Uttar Pradesh, the government announced on Saturday.</p>
<p>Janakpur Dham is revered as the birthplace of Mata Sita and Ayodhya as the birthplace of Prabhu Shri Ram.</p>
<h2>Route and schedule</h2>
<p>Besides its terminal stations, the train will have commercial stoppages at Jaynagar, Madhubani, Shisho, Sitamarhi, Raxaul, Narkatiaganj, Gorakhpur, Basti, Mankapur and Ayodhya Dham.</p>
<p>The announcement follows weeks of preparation on the corridor between the two countries.</p>
<p>"This is a historic link for pilgrims on both sides of the border," a railway official said.</p>
<p>Trains will originate from Janakpur Dham on Saturdays and from Ayodhya Cantt on Mondays.</p>
"""

print("extract_pull_quote on the Janakpur-shaped body")
q = E.extract_pull_quote(BODY)
check("a quote is still extracted", q is not None)
check("the quote is not the stops list",
      q is not None and "commercial stoppages" not in q)
check("the quote carries no heading text",
      q is not None and not q.startswith("Route and schedule"))
check("the genuinely quotable sentence wins",
      q is not None and "historic link for pilgrims" in q)

print()
if FAILS:
    print(f"FAILED: {len(FAILS)} check(s): {FAILS}")
    sys.exit(1)
print("ALL CHECKS PASSED")
