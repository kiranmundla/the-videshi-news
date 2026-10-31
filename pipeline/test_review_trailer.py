"""Regression tests for the roster trailer step (review_trailer.py).

The case (2026-10-31): the Udta Teer review roundup published with
ZERO embeds although the film's roster entry in now-in-theaters.json
already carried the official Dharma Productions trailer
(hN_ZUElLH44). movie-reviews.py has no trailer step; enrich-on-
publish's registry search cannot find film trailers (Ayushmann
Khurrana is not a registry entity; film titles never are); the
official-video pass was env-gated OFF in that subprocess and maps
channels by studio names in the body ("Dharma" appears 0 times in
the review). 0 of 5 review roundups published Oct 17-31 had a
trailer at production; Prahaar and Jailer 2 still have none.

Fixtures use the REAL roster entry and the REAL video metadata for
hN_ZUElLH44 (fetched live 2026-10-31). Gate failures are simulated
by mutating that metadata — the same mutations the gate exists for:
fan-channel upload, another film's trailer on the right channel,
US region block, metadata lookup failure.

Run: python3 test_review_trailer.py  (exit 0 = all pass)
"""
import copy

import review_trailer as rt

fails = 0
total = 0


def check(name, cond, extra=""):
    global fails, total
    total += 1
    if cond:
        print(f"ok   {name}")
    else:
        fails += 1
        print(f"FAIL {name} {extra}")


ROSTER = [{
    "title": "Udta Teer",
    "slug": "udta-teer-2026",
    "director": "Aakash Kaushik",
    "trailer_url": "https://www.youtube.com/watch?v=hN_ZUElLH44",
    "review_slug": "udta-teer-review-roundup-critics",
}, {
    "title": "Cult",
    "slug": "cult-2026",
    "trailer_url": "https://www.youtube.com/watch?v=MDv5HHUNsbE",
    "review_slug": None,
}, {
    "title": "No Trailer Film",
    "slug": "no-trailer-film-2026",
    "trailer_url": "https://www.youtube.com/results?search_query=No+Trailer",
    "review_slug": None,
}]

DHARMA_ID = "UCGdHCtXEzkCB7-g_NXYZPcw"
REAL_META = {
    "title": "Udta Teer Official Trailer | Ayushmann Khurrana & "
             "Sara Ali Khan | Akash A Kaushik | 23 October",
    "channel_id": DHARMA_ID,
    "channel_title": "Dharma Productions",
    "region_restriction": None,
}

ARTICLE = {
    "headline": "Udta Teer: Ayushmann Khurrana Soars in This "
                "Hilarious Spy Comedy",
    "slug": "udta-teer-review-roundup-critics",
    "category": "entertainment",
    "body": "<p>review</p>",
}


def fake_fetcher(meta):
    return lambda video_id: meta


def decide(article=ARTICLE, meta=REAL_META, roster=ROSTER):
    return rt.review_trailer_for_article(
        article, roster=roster, meta_fetcher=fake_fetcher(meta))


# ── The Udta Teer case: accepted, exact video ──
d = decide()
check("udta teer: accepted", d["status"] == "accepted", str(d))
check("udta teer: video id", d.get("video_id") == "hN_ZUElLH44")
check("udta teer: channel", d.get("channel") == "Dharma Productions")

# ── Match routes ──
d = decide(article={**ARTICLE, "headline": "A Spy Comedy Triumph",
                    "slug": "udta-teer-review-roundup-critics"})
check("match via review_slug alone", d["status"] == "accepted", str(d))

d = decide(article={**ARTICLE, "slug": "some-other-slug"})
check("match via headline title", d["status"] == "accepted", str(d))

d = decide(article={"headline": "Sensex Surges 905 Points",
                    "slug": "sensex-surges-905-points",
                    "category": "markets-finance", "body": ""})
check("unrelated article: no film", d["status"] == "no_film", str(d))

# Roster film whose trailer_url is a search URL — not embeddable.
d = decide(article={"headline": "No Trailer Film Review: A Miss",
                    "slug": "no-trailer-film-review",
                    "category": "entertainment", "body": ""})
check("search-url trailer: no candidate", d["status"] == "no_film",
      str(d))

# ── Gate: fan-channel upload of the same trailer ──
meta = {**REAL_META, "channel_id": "UCfanupload1234567",
        "channel_title": "Bollywood Trailers HD"}
d = decide(meta=meta)
check("fan channel rejected", d["status"] == "rejected"
      and "allowlist" in d["reason"], str(d))

# ── Gate: another film's trailer on the RIGHT channel ──
meta = {**REAL_META,
        "title": "Bad Apples Official Trailer | Dharma Productions"}
d = decide(meta=meta)
check("wrong film on right channel rejected",
      d["status"] == "rejected" and "does not name the film"
      in d["reason"], str(d))

# ── Gate: not a trailer at all ──
meta = {**REAL_META, "title": "Udta Teer Full Movie | Ayushmann "
                             "Khurrana"}
d = decide(meta=meta)
check("non-trailer title rejected", d["status"] == "rejected",
      str(d))

# ── Gate: US region ──
meta = {**REAL_META, "region_restriction": {"allowed": ["IN"]}}
d = decide(meta=meta)
check("region allowed=[IN] rejected", d["status"] == "rejected"
      and "region-blocked" in d["reason"], str(d))

meta = {**REAL_META, "region_restriction": {"blocked": ["US"]}}
d = decide(meta=meta)
check("region blocked=[US] rejected", d["status"] == "rejected",
      str(d))

meta = {**REAL_META, "region_restriction": {"allowed": ["IN", "US"]}}
d = decide(meta=meta)
check("region allowed incl. US accepted", d["status"] == "accepted",
      str(d))

# ── Gate: metadata lookup failure fails closed ──
d = decide(meta=None)
check("metadata failure rejected (fail-closed)",
      d["status"] == "rejected" and "fail-closed" in d["reason"],
      str(d))

# ── Gate: teaser titles count; title case does not matter ──
meta = {**REAL_META, "title": "UDTA TEER | Official Teaser"}
d = decide(meta=meta)
check("teaser accepted", d["status"] == "accepted", str(d))

# ── Real roster file: the film is in it with this trailer ──
live_roster = rt.load_roster()
film = rt.match_roster_film(ARTICLE, live_roster)
check("live roster matches Udta Teer",
      film is not None and film.get("title") == "Udta Teer",
      str(film and film.get("title")))
check("live roster trailer id",
      film is not None
      and rt.video_id_from_url(film.get("trailer_url") or "")
      == "hN_ZUElLH44")

print(f"\n{total - fails}/{total} passed")
raise SystemExit(1 if fails else 0)
