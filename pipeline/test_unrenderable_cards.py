"""Tests: unrenderable data cards (2026-11-15).

ArticlePage.tsx renders data_cards only via `type`-keyed components
(movie_review_ratings, match_scorecard, key_dates, how_to, checklist,
price_compare, recipe, critic_table). The polish family's
card_type-keyed cards (stat_grid / comparison / timeline /
highlights) were stored and counted in run reports but NEVER shown
to readers — the Air India article's 'Flight Frequencies' and
'Journey Time Reduction' cards, and the U19 final's 'Match Summary'
and 'Top Performers' cards, were all invisible.

Two fixes under test:
  1. content_gate.check_unrenderable_data_cards fails any card
     ArticlePage cannot render.
  2. article-polish.to_renderable_cards converts polish output into
     renderable shapes at persist time.

Run: python3 test_unrenderable_cards.py  (exit 0 = all pass)
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, filename):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(HERE, filename))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


gate = load("content_gate", "content_gate.py")
polish = load("article_polish", "article-polish.py")

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


BASE = {"headline": "Test", "body": "<p>Body text.</p>", "sources": []}

# 1. The Air India cards as actually published must fail the gate.
ai_cards = [
    {"card_type": "stat_grid", "card_title": "Flight Frequencies",
     "items": [{"label": "Daily flights from Delhi to JFK", "value": "1"},
               {"label": "Weekly flights from Delhi to Newark",
                "value": "4"}]},
    {"card_type": "comparison", "card_title": "Journey Time Reduction",
     "items": [{"name": "Previous Journey Time", "value": "22 hours"},
               {"name": "Current Journey Time", "value": "17 hours"}]},
]
f = gate.check_unrenderable_data_cards({**BASE, "data_cards": ai_cards})
check("Air India polish cards fail the gate", len(f) == 2)
check("failure names the card", any("Flight Frequencies" in x for x in f))

# 2. Every renderable type passes.
for t in ["movie_review_ratings", "match_scorecard", "key_dates",
          "how_to", "checklist", "price_compare", "recipe",
          "critic_table"]:
    f = gate.check_unrenderable_data_cards(
        {**BASE, "data_cards": [{"type": t, "title": "X"}]})
    check(f"renderable type {t} passes", f == [])

# 3. An invented type fails; no cards passes.
f = gate.check_unrenderable_data_cards(
    {**BASE, "data_cards": [{"type": "pie_chart", "title": "X"}]})
check("invented type fails", len(f) == 1)
check("no cards passes",
      gate.check_unrenderable_data_cards({**BASE, "data_cards": []}) == [])

# 4. Polish conversion: the Air India cards become renderable.
out = polish.to_renderable_cards(ai_cards)
check("conversion yields 2 cards", len(out) == 2)
check("converted cards are price_compare",
      all(c["type"] == "price_compare" for c in out))
check("converted cards pass the gate",
      gate.check_unrenderable_data_cards({**BASE, "data_cards": out}) == [])
freq = out[0]
check("stat_grid rows carry label+value",
      freq["rows"][0] == ["Daily flights from Delhi to JFK", "1"]
      and freq["title"] == "Flight Frequencies")

# 5. Timeline converts to key_dates with dates intact.
tl = [{"card_type": "timeline", "card_title": "Timeline of Events",
       "items": [{"date": "Nov 4", "event": "Non-stops resume"},
                 {"date": "Nov 15", "event": "Airline announces"}]}]
out = polish.to_renderable_cards(tl)
check("timeline -> key_dates",
      len(out) == 1 and out[0]["type"] == "key_dates"
      and out[0]["dates"][1]["event"] == "Airline announces")

# 6. Highlights convert to checklist; hero_stat leads a stat_grid.
hl = [{"card_type": "highlights", "card_title": "Key Points",
       "items": [{"text": "Rome stop removed", "stat": "5h saved"},
                 {"text": "Four routes affected"}]}]
out = polish.to_renderable_cards(hl)
check("highlights -> checklist",
      len(out) == 1 and out[0]["type"] == "checklist"
      and out[0]["items"][0]["text"] == "Rome stop removed — 5h saved")
sg = [{"card_type": "stat_grid", "card_title": "By the Numbers",
       "hero_stat": {"value": "17h", "label": "New journey time",
                     "trend": "↓ 5h"},
       "items": [{"label": "Routes", "value": "4"}]}]
out = polish.to_renderable_cards(sg)
check("hero_stat becomes first row",
      out[0]["rows"][0] == ["New journey time", "17h (↓ 5h)"])

# 7. Unknown polish kinds are dropped, not stored invisibly.
out = polish.to_renderable_cards(
    [{"card_type": "word_cloud", "card_title": "X",
      "items": [{"text": "a"}]}])
check("unknown kind dropped", out == [])

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
