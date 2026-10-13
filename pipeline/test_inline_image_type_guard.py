"""Regression tests for the inline-image entity-type agreement gate in
enrich-articles.py (added 2026-10-13 after the "Chelsea 3" incident).

Incident: the inline topic "Chelsea 3" (a VESSEL in a drone-attack story)
matched Commons' top search hit "File:Chelsea Clinton.jpg" — a photo of a
PERSON — because the old guards only compared name tokens. The photo was
inserted into the article captioned as the ship.

The gate's contract:
- a photo depicting a PERSON may only illustrate that same person;
- a depicted entity of an established type must type-match the topic;
- a depicted proper name that cannot be type-verified is skipped
  (no image beats a wrong image).

Network is stubbed with fixtures (Wikipedia summaries + Commons categories
recorded from the real pages involved in the incident).

Run: python3 test_inline_image_type_guard.py  (exit 0 = all pass)
"""
import os
import sys
from importlib.machinery import SourceFileLoader

_HERE = os.path.dirname(os.path.abspath(__file__))
mod = SourceFileLoader(
    "enrich_articles", os.path.join(_HERE, "enrich-articles.py")).load_module()

# ── Fixtures ────────────────────────────────────────────────────────────────
_SUMMARIES = {
    "chelsea clinton": {
        "type": "standard",
        "description": "American writer (born 1980)",
        "extract": "Chelsea Victoria Clinton (born February 27, 1980) is "
                   "an American writer and global health advocate.",
    },
    "james mcneill whistler": {
        "type": "standard",
        "description": "American artist",
        "extract": "James McNeill Whistler was an American artist active "
                   "during the American Gilded Age.",
    },
    "gateway of india": {
        "type": "standard",
        "description": "Triumphal arch in Mumbai, India",
        "extract": "The Gateway of India is an arch-monument built in the "
                   "early 20th century in the city of Mumbai.",
    },
    "rms titanic": {
        "type": "standard",
        "description": "British ocean liner",
        "extract": "RMS Titanic was a British passenger liner that sank "
                   "in the North Atlantic Ocean.",
    },
    "bioluminescence": {
        "type": "standard",
        "description": "Production and emission of light by a living organism",
        "extract": "Bioluminescence is the production and emission of light "
                   "by living organisms.",
    },
    # Recorded from the live page: a London housing development — this is
    # what "Chelsea Waterfront" resolves to, and it is NOT the vessel.
    "chelsea waterfront": {
        "type": "standard",
        "description": "Residential development in Chelsea, London",
        "extract": "Chelsea Waterfront is a residential development on "
                   "the north bank of the River Thames in London.",
    },
    # "chelsea 3", "john smith", ... → no page (None)
}

_CATEGORIES = {
    "File:Chelsea Clinton.jpg": [
        "Chelsea Clinton in 2008", "Chelsea Clinton smiling",
        "2008 in Philadelphia",
    ],
}

mod._wiki_summary = lambda name: _SUMMARIES.get(
    " ".join((name or "").lower().split()))
mod._commons_file_categories = lambda title: list(_CATEGORIES.get(title, []))

_failures = []


def check(label, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {label}"
          + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        _failures.append(label)


# ── 1. Classifier sanity ────────────────────────────────────────────────────
print("Classifier:")
check("Chelsea Clinton summary → person",
      mod._classify_wiki_type(_SUMMARIES["chelsea clinton"]) == "person")
check("RMS Titanic summary → vessel",
      mod._classify_wiki_type(_SUMMARIES["rms titanic"]) == "vessel")
check("Gateway of India summary → place",
      mod._classify_wiki_type(_SUMMARIES["gateway of india"]) == "place")
check("Bioluminescence summary → other",
      mod._classify_wiki_type(_SUMMARIES["bioluminescence"]) == "other")
check("No page (Chelsea 3) → None",
      mod._topic_entity_type("Chelsea 3") is None)

# ── 2. Gate cases ───────────────────────────────────────────────────────────
print("Gate:")
GATE_CASES = [
    # (label, topic, candidate file title, expect_allowed)
    ("vessel name vs person photo (the Chelsea incident)",
     "Chelsea 3", "File:Chelsea Clinton.jpg", False),
    ("person entity + same person photo",
     "Chelsea Clinton", "File:Chelsea Clinton.jpg", True),
    ("place entity + person photo",
     "Gateway of India", "File:Chelsea Clinton.jpg", False),
    ("place entity + place photo of itself",
     "Gateway of India", "File:Gateway of India Mumbai.jpg", True),
    ("vessel entity + vessel photo",
     "RMS Titanic", "File:RMS Titanic.jpg", True),
    ("vessel entity + person photo",
     "RMS Titanic", "File:Chelsea Clinton.jpg", False),
    ("unverifiable proper-name photo is skipped",
     "Gateway of India", "File:John Smith 2019.jpg", False),
    ("unverifiable topic + different named entity photo",
     "Chelsea 3", "File:Chelsea Waterfront 3.jpg", False),
    ("descriptive photo for a phenomenon topic",
     "Bioluminescence", "File:Bioluminescent waves at night.jpg", True),
]
for label, topic, title, expect_ok in GATE_CASES:
    topic_type = mod._topic_entity_type(topic)
    ok, why = mod._inline_type_gate(topic, topic_type, {"title": title})
    check(label, ok == expect_ok, f"gate returned ok={ok} ({why})")

# ── 3. End-to-end: the incident article gets NO inline image ───────────────
print("End-to-end (incident reproduction):")
_INCIDENT_RESULTS = [
    {"title": "File:Chelsea Clinton.jpg", "source": "wikimedia",
     "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/"
            "Chelsea_Clinton.jpg/1200px-Chelsea_Clinton.jpg",
     "width": 1200, "height": 1500},
    {"title": "File:Chelsea Waterfront 3.jpg", "source": "wikimedia",
     "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/"
            "Chelsea_Waterfront_3.jpg/1200px-Chelsea_Waterfront_3.jpg",
     "width": 1200, "height": 900},
    {"title": "File:James McNeill Whistler - Chelsea - B2000.5.7 - "
              "Yale Center for British Art.jpg", "source": "wikimedia",
     "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/"
            "Whistler_Chelsea.jpg/1200px-Whistler_Chelsea.jpg",
     "width": 1200, "height": 900},
    {"title": "File:Stewarts Grove, Chelsea, London - geograph.org.uk - "
              "3385918.jpg", "source": "wikimedia",
     "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/"
            "Stewarts_Grove.jpg/1200px-Stewarts_Grove.jpg",
     "width": 1200, "height": 900},
    {"title": "File:Upcerne Road, Chelsea - geograph.org.uk - 4585253.jpg",
     "source": "wikimedia",
     "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/"
            "Upcerne_Road.jpg/1200px-Upcerne_Road.jpg",
     "width": 1200, "height": 900},
]
mod._extract_inline_visual_topics = lambda h, b, c: ["Chelsea 3"]
mod.search_wikimedia_commons = lambda q, limit=5: list(_INCIDENT_RESULTS)
_body = ("A drone attack sank the Chelsea 3 off the Bulgarian coast late "
         "on Monday. The Chelsea 3, a general cargo vessel, went down in "
         "the Black Sea after an explosion on board. All crew members "
         "were rescued by the coast guard, officials said.")
res = mod.find_inline_images(
    "Drone Attack Sinks Ship Off Bulgaria in Black Sea", _body, "",
    category="news")
check("incident article yields no inline image", res == [], f"got {res}")

# ── 4. End-to-end: a legitimate place topic still gets its photo ────────────
print("End-to-end (legitimate match):")
_GATEWAY_RESULT = [{
    "title": "File:Gateway of India Mumbai.jpg", "source": "wikimedia",
    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/"
           "Gateway_of_India_Mumbai.jpg/1200px-Gateway_of_India_Mumbai.jpg",
    "width": 1600, "height": 1200,
}]
mod._extract_inline_visual_topics = lambda h, b, c: ["Gateway of India"]
mod.search_wikimedia_commons = lambda q, limit=5: list(_GATEWAY_RESULT)
_body2 = ("The Gateway of India will undergo a year-long restoration, the "
          "state government announced on Tuesday. The Gateway of India "
          "overlooks the harbour and draws visitors from across the "
          "country throughout the year.")
res2 = mod.find_inline_images(
    "Gateway of India Restoration Plan Announced", _body2, "",
    category="news")
check("place topic gets its own photo",
      len(res2) == 1 and res2[0][0] == "Gateway of India", f"got {res2}")

print()
if _failures:
    print(f"❌ {len(_failures)} FAILURE(S): {_failures}")
    sys.exit(1)
print("✅ All inline-image type-gate tests passed")
