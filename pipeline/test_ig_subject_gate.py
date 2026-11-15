"""Tests: IG caption subject veto in enrich-on-publish.py (2026-11-15).

The keeper case is the Air India Seoul reel: an @airindia reel
promoting Seoul flights passed the keyword-hit gate for the New York
non-stop restoration article because its caption shares the words
"non-stop", "flights", "new" and "Delhi" — while its actual subject
(Seoul) appears nowhere in the article. The subject veto
(_ig_caption_foreign_subjects) must reject it, and must NOT reject
captions whose named subjects are the article's own.

Run: python3 test_ig_subject_gate.py  (exit 0 = all pass)
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "enrich_on_publish", os.path.join(HERE, "enrich-on-publish.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

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


ARTICLE = {
    "headline": "Air India Restores Non-Stop Flights to New York, "
                "Cutting Travel Time by Five Hours",
    "body": "<p>Air India has restored non-stop flights on all four "
            "India-New York routes — Delhi and Mumbai to JFK and "
            "Newark — ending the Rome refuelling stop. Flights from "
            "Delhi use the Airbus A350-900; services from Mumbai are "
            "operated by Boeing 777-300ER aircraft. The shorter "
            "routing uses Iraqi airspace.</p>",
    "key_entities": ["Air India", "New York", "Newark", "Delhi",
                     "Mumbai"],
}

# 1. The keeper: the real Seoul caption must be vetoed, naming Seoul.
seoul = ("New experiences, new favourites and a whole new city to "
         "fall in love with. Seoul is waiting to be explored. Get "
         "there with our daily non-stop flights from Delhi this "
         "winter.")
foreign = mod._ig_caption_foreign_subjects(seoul, ARTICLE)
check("Seoul caption vetoed", len(foreign) > 0)
check("Seoul named as the foreign subject",
      any("Seoul" in f for f in foreign))

# 2. An on-topic caption naming the article's own subjects passes.
ontopic = ("Our Delhi to New York non-stop is back — no more Rome "
           "stop. Now boarding at JFK and Newark.")
check("on-topic caption passes",
      mod._ig_caption_foreign_subjects(ontopic, ARTICLE) == [])

# 3. A caption with no proper-noun subjects passes.
generic = "Non-stop flights, five hours saved, zero layovers. Book now."
check("subject-free caption passes",
      mod._ig_caption_foreign_subjects(generic, ARTICLE) == [])

# 4. A caption about a different person is vetoed.
person = "Join Chef Ranveer Brar in Mumbai as he tastes the new menu."
foreign = mod._ig_caption_foreign_subjects(person, ARTICLE)
check("foreign person vetoed",
      any("Ranveer" in f for f in foreign))

# 5. Sentence-start marketing words are not subjects.
marketing = ("Experience the new A350 cabin on our Delhi route. "
             "Discover more today.")
check("marketing sentence-starters pass",
      mod._ig_caption_foreign_subjects(marketing, ARTICLE) == [])

# 6. A foreign place inside a hashtag is vetoed.
hashtag = "Daily non-stop flights from Delhi! #VisitSeoul #Travel"
foreign = mod._ig_caption_foreign_subjects(hashtag, ARTICLE)
check("hashtag Seoul vetoed", any("Seoul" in f for f in foreign))

# 7. A different route pair (same vocabulary, other subject) vetoed.
other_route = "Now flying non-stop from Delhi to Toronto, daily."
foreign = mod._ig_caption_foreign_subjects(other_route, ARTICLE)
check("Toronto route vetoed", any("Toronto" in f for f in foreign))

# 8. Empty caption never vetoes.
check("empty caption passes",
      mod._ig_caption_foreign_subjects("", ARTICLE) == [])

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
