#!/usr/bin/env python3
"""Self-test for the extractive timeline guard in article-polish.py.

Cases:
  1. Body with NO dates -> a generated timeline (with invented dates)
     must be dropped entirely.
  2. Body with real dates -> timeline keeps only the entries whose dates
     the body supports; an invented 2023 entry is dropped; a timeline
     over a stated day range ("17 to 22 October") is kept.
  3. An entry whose date field is fine but whose event text smuggles an
     unsupported date is dropped.
  4. Non-date label entries ("Within 90 days") assert no calendar date
     and are kept (out of the guard's scope).

Run: python3 -u pipeline/test_timeline_guard.py
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "article_polish", os.path.join(HERE, "article-polish.py"))
ap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ap)

failures = []


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def tl_card(title, items):
    return {"card_title": title, "card_type": "timeline",
            "items": items, "placement_hint": "mid_article"}


# ── Case 1: body with no dates at all ──
body1 = ("The court set aside the death sentence on Tuesday after a long "
         "appeal. The family welcomed the decision and thanked the legal "
         "team. Officials said further proceedings would follow.")
cards1 = [tl_card("From Prison to Freedom", [
    {"date": "March 2023", "event": "He posts the comment."},
    {"date": "June 2023", "event": "He is arrested."},
    {"date": "October 2023", "event": "The appeal court imposes death."},
])]
kept1, dropped1 = ap.guard_timeline_cards(cards1, body1, 2026)
check("no-date body yields no timeline", kept1 == [], f"kept={kept1}")
check("no-date body drops are logged", len(dropped1) >= 3, f"dropped={dropped1}")

# ── Case 2: body with real dates ──
body2 = ("The case began in late June, after footage circulated online. "
         "He was arrested in July. On 17 September, an appeal court "
         "increased the sentence to death. The Supreme Court appeal was "
         "filed on 11 October. The ruling was delivered on 13 October, "
         "two days later. He had travelled abroad in September 2025 for "
         "work. Between 2015 and 2019 he lived in his home town.")
cards2 = [tl_card("The Case So Far", [
    {"date": "June 2026", "event": "Posts the comment."},
    {"date": "July 2026", "event": "Arrested."},
    {"date": "September 17, 2026", "event": "Appeal court imposes death."},
    {"date": "October 11, 2026", "event": "Supreme Court appeal filed."},
    {"date": "October 13, 2026", "event": "Death sentence set aside."},
    {"date": "September 2025", "event": "Travelled abroad for work."},
    {"date": "2015-2019", "event": "Lived in his home town."},
    {"date": "March 2023", "event": "INVENTED entry."},
    {"date": "January 5, 2024", "event": "INVENTED entry."},
])]
kept2, dropped2 = ap.guard_timeline_cards(cards2, body2, 2026)
items2 = kept2[0]["items"] if kept2 else []
check("dated body keeps the card", len(kept2) == 1)
check("dated body keeps exactly the 7 supported entries",
      len(items2) == 7, f"kept={[i['date'] for i in items2]}")
check("invented 2023/2024 entries dropped",
      all(i["date"] not in ("March 2023", "January 5, 2024") for i in items2))

# Day-range body: "from 17 to 22 October" supports each day in the range
body2b = "The minister will travel from 17 to 22 October, officials said."
cards2b = [tl_card("Itinerary", [
    {"date": "October 17", "event": "Arrives."},
    {"date": "October 20", "event": "Meetings."},
    {"date": "October 22", "event": "Departs."},
    {"date": "October 25", "event": "INVENTED day outside the range."},
])]
kept2b, _ = ap.guard_timeline_cards(cards2b, body2b, 2026)
items2b = kept2b[0]["items"] if kept2b else []
check("day-range body supports in-range days only",
      [i["date"] for i in items2b] == ["October 17", "October 20", "October 22"],
      f"kept={[i['date'] for i in items2b]}")

# ── Case 3: smuggled date inside event text ──
cards3 = [tl_card("Timeline of Events", [
    {"date": "October 13, 2026", "event": "Ruling delivered."},
    {"date": "October 11, 2026", "event": "Appeal filed, reversing the March 2023 verdict."},
    {"date": "September 17, 2026", "event": "Appeal court hearing."},
])]
kept3, _ = ap.guard_timeline_cards(cards3, body2, 2026)
items3 = kept3[0]["items"] if kept3 else []
check("event-text smuggled date drops the entry",
      len(items3) == 2 and all("2023" not in i["event"] for i in items3),
      f"kept={[i['date'] for i in items3]}")

# ── Case 4: non-date labels are out of scope ──
cards4 = [tl_card("Passport Update Timeline", [
    {"date": "Within 90 days", "event": "Deadline to upload new passport."},
    {"date": "Upon passport renewal", "event": "Travel allowed while pending."},
])]
kept4, _ = ap.guard_timeline_cards(cards4, body1, 2026)
check("label entries kept (no calendar date asserted)",
      len(kept4) == 1 and len(kept4[0]["items"]) == 2)

# Non-timeline cards pass through untouched
cards5 = [{"card_title": "Key Numbers", "card_type": "stat_grid",
           "items": [{"label": "Fine", "value": "3 million riyals"}]}]
kept5, dropped5 = ap.guard_timeline_cards(cards5, body1, 2026)
check("non-timeline cards untouched", kept5 == cards5 and dropped5 == [])

print()
if failures:
    print(f"FAILED: {len(failures)} check(s): {failures}")
    sys.exit(1)
print("All timeline-guard checks passed.")
