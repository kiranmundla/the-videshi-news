"""Tests: headline qualifier gate (2026-11-15).

Keeper case: Air India said travel time falls "by up to five hours";
the published headline ran "Cutting Travel Time by Five Hours" —
a maximum restated as a flat claim. check_headline_qualifier must
hold that article, and must not fire when the headline keeps the
qualifier, when the body also states the figure flatly (a hard
fact), or when the figures differ.

Run: python3 test_headline_qualifier.py  (exit 0 = all pass)
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "content_gate", os.path.join(HERE, "content_gate.py"))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

fails = 0
total = 0


def check(name, cond):
    global fails, total
    total += 1
    if cond:
        print(f"  ok {total}: {name}")
    else:
        fails += 1
        print(f"  FAIL {total}: {name}")


AI_BODY = ("<p>Air India has restored non-stop flights, cutting "
           "journey times by up to five hours. Flights that took "
           "around 22 hours with the stop now take approximately "
           "17 hours.</p>")

# 1. The keeper: flat headline, consistently qualified body -> hold.
f = gate.check_headline_qualifier({
    "headline": "Air India Restores Non-Stop Flights to New York, "
                "Cutting Travel Time by Five Hours",
    "body": AI_BODY})
check("Air India headline held", len(f) == 1)
check("failure names the figure", any("5 hours" in x for x in f))

# 2. Qualified headline passes.
f = gate.check_headline_qualifier({
    "headline": "Air India Restores Nonstop New York and Newark "
                "Flights, Saving Up to Five Hours",
    "body": AI_BODY})
check("qualified headline passes", f == [])

# 3. Body that also states the figure flatly passes (hard fact).
f = gate.check_headline_qualifier({
    "headline": "Five Hours Cut From New York Flight Times",
    "body": "<p>The schedule cuts five hours from the route. "
            "Savings reach up to five hours on peak days.</p>"})
check("flat body mention passes", f == [])

# 4. Digit form: 'at least' floor dropped in the headline -> hold.
f = gate.check_headline_qualifier({
    "headline": "Airline Adds 200 Flights for the Holiday Season",
    "body": "<p>The airline will add at least 200 flights in "
            "December, the statement said.</p>"})
check("dropped 'at least' held", len(f) == 1)

# 5. A different figure in the headline is not this check's business.
f = gate.check_headline_qualifier({
    "headline": "Air India Restores Four New York Routes",
    "body": AI_BODY})
check("unrelated headline figure passes", f == [])

# 6. Percent figure with qualifier dropped -> hold.
f = gate.check_headline_qualifier({
    "headline": "Exports Jump 30% in October",
    "body": "<p>Exports rose by up to 30% in some categories, "
            "officials said.</p>"})
check("dropped percent qualifier held", len(f) == 1)

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
