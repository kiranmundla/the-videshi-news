#!/usr/bin/env python3
"""Regression tests for the fetch-theaters poster guard (2026-11-13).

Kiran's screenshot: the movie page for "King" (Shah Rukh Khan,
dir. Siddharth Anand, Dec 24 2026) carried the Aachen Charlemagne
bust as its poster. Root cause: fetch_wikipedia_image tried the
BARE title first and took the lead image of whatever article
Wikipedia ranks for that word, with no check that the page is the
film's article. Same trap had already caught "418" (Visigoth
migration map) and "Pyre" (Bali cremation photo).

The fix: film-page candidates first, and every candidate must
pass _is_film_page (the summary self-describes as a film), plus a
commons-thumb self-heal in main(). These tests pin the guard with
recorded-shape summaries — no network.
"""
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "fetch_theaters", Path(__file__).parent / "fetch-theaters.py")
ft = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ft)

FAILURES = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILURES.append(name)


# --- Recorded-shape REST summaries -------------------------------------

KING_MONARCH = {  # en.wikipedia "King" article (the trap)
    "description": "Male ruler of a kingdom or empire",
    "extract": "A king is a male ruler (one ranked 'just below' an "
               "emperor) in a variety of forms of monarchy...",
    "thumbnail": {"source": "https://thumb.wikimedia.org/wikipedia/"
                  "commons/thumb/b/b5/Aachen_Domschatz_Bueste1.jpg/"
                  "330px-Aachen_Domschatz_Bueste1.jpg"},
    "originalimage": {"source": "https://upload.wikimedia.org/"
                      "wikipedia/commons/b/b5/Aachen_Domschatz_Bueste1.jpg",
                      "width": 500, "height": 667},
}

KING_FILM = {  # en.wikipedia "King (2026 film)" (the real poster)
    "description": "Upcoming Indian Hindi-language action thriller film",
    "extract": "King is an upcoming Indian Hindi-language action "
               "thriller film directed by Siddharth Anand...",
    "thumbnail": {"source": "https://upload.wikimedia.org/wikipedia/en/"
                  "f/fd/King_%28Hindi_film%29.jpg"},
    "originalimage": {"source": "https://upload.wikimedia.org/wikipedia/"
                      "en/f/fd/King_%28Hindi_film%29.jpg",
                      "width": 283, "height": 354},
}

MAP_PAGE = {  # "418" article lead — a history map, not the film
    "description": "Year in history",
    "extract": "418 (CDXVIII) was a common year starting on Tuesday "
               "of the Julian calendar...",
    "thumbnail": {"source": "https://thumb.wikimedia.org/wikipedia/"
                  "commons/thumb/b/b1/Visigoth_migrations.jpg/330px-"
                  "Visigoth_migrations.jpg"},
    "originalimage": {"width": 500, "height": 300},
}

FILM_418 = {  # "418 (film)"
    "description": "2026 Indian horror thriller film by Kirtan Nadagouda",
    "extract": "418 is a 2026 Indian Telugu-language horror thriller "
               "film written and directed by Kirtan Nadagouda...",
    "thumbnail": {"source": "https://upload.wikimedia.org/wikipedia/en/"
                  "9/9b/418_%28film%29_poster.jpg"},
    "originalimage": {"source": "https://upload.wikimedia.org/wikipedia/"
                      "en/9/9b/418_%28film%29_poster.jpg",
                      "width": 273, "height": 365},
}

NO_DESC_FILM = {  # film page whose description is missing; extract decides
    "description": "",
    "extract": "Pyre is a 2024 Indian Hindi-language drama film "
               "directed by Vinod Kapri...",
    "thumbnail": {"source": "https://upload.wikimedia.org/wikipedia/en/"
                  "2/28/Pyre_Film_Poster.jpg"},
    "originalimage": {"width": 263, "height": 379},
}


# --- _is_film_page unit checks ------------------------------------------

check("monarch page rejected", not ft._is_film_page(KING_MONARCH))
check("map/history page rejected", not ft._is_film_page(MAP_PAGE))
check("King film page accepted", ft._is_film_page(KING_FILM))
check("418 film page accepted", ft._is_film_page(FILM_418))
check("extract-only film page accepted", ft._is_film_page(NO_DESC_FILM))
check("empty summary rejected", not ft._is_film_page({}))


# --- fetch flow with a stubbed requests.get ------------------------------

class FakeResp:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def json(self):
        return self._payload


PAGES = {
    "King": KING_MONARCH,
    "King_(film)": KING_MONARCH,          # disambiguation-style payload
    "King_(2026_film)": KING_FILM,
    "418": MAP_PAGE,
    "418_(film)": FILM_418,
    "418_(2026_film)": FILM_418,
}


def fake_get(url, headers=None, timeout=None):
    page = url.rsplit("/", 1)[-1]
    if page in PAGES:
        return FakeResp(PAGES[page])
    return FakeResp({}, status=404)


orig_get = ft.requests.get
orig_sleep = ft.time.sleep
ft.requests.get = fake_get
ft.time.sleep = lambda *_: None
try:
    url, w, h = ft.fetch_wikipedia_image("King", 2026)
    check("King resolves to the film poster, not the bust",
          "King_%28Hindi_film%29.jpg" in url and w == 283 and h == 354)

    url, w, h = ft.fetch_wikipedia_image("418", 2026)
    check("418 resolves to the film poster, not the map",
          "418_%28film%29_poster.jpg" in url and w == 273)

    url, w, h = ft.fetch_wikipedia_image("Nonexistent Title", 2026)
    check("unknown title fails closed", url == "" and w == 0)
finally:
    ft.requests.get = orig_get
    ft.time.sleep = orig_sleep

print(f"\n{len(FAILURES)} failure(s)")
sys.exit(1 if FAILURES else 0)
