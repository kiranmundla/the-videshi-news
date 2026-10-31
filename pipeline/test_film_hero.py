"""Regression tests for the film-hero resolution rule (film_hero.py).

The case (2026-10-31): the Udta Teer review roundup shipped the
roster's Wikipedia poster as its hero. The poster file is a
non-free fair-use image whose stored size Wikipedia caps at
283x354 px; rendered full-width (~1100 px) it was visibly blurry —
Kiran flagged it from his phone. fetch-theaters.py discarded the
dimensions the REST API returned, and movie-reviews.py published
the poster unconditionally.

The rule under test: a film article's hero must truly measure
>=800px wide. Poster below the floor -> the film's gated official
trailer still (maxres, byte-measured — i.ytimg serves a 120x90
placeholder at maxresdefault.jpg for videos without one). Poster
>=floor -> poster kept. Neither -> NO hero (fail-closed).

All network access is injected (width_of / meta_fetcher fakes);
fixtures use the real Udta Teer roster data and the real Dharma
Productions trailer metadata, as in test_review_trailer.py.

Run: python3 test_film_hero.py  (exit 0 = all pass)
"""
import film_hero as fh

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


DHARMA_ID = "UCGdHCtXEzkCB7-g_NXYZPcw"
REAL_META = {
    "title": "Udta Teer Official Trailer | Ayushmann Khurrana & "
             "Sara Ali Khan | Akash A Kaushik | 23 October",
    "channel_id": DHARMA_ID,
    "channel_title": "Dharma Productions",
    "region_restriction": None,
}
FAN_META = dict(REAL_META, channel_id="UCfanChannel000000000",
                channel_title="Narayanatv")

POSTER_283 = ("https://upload.wikimedia.org/wikipedia/en/c/c8/"
              "Udta_Teer_film_poster.jpg")
MAXRES = "https://i.ytimg.com/vi/hN_ZUElLH44/maxresdefault.jpg"

FILM = {
    "title": "Udta Teer",
    "slug": "udta-teer-2026",
    "director": "Aakash Kaushik",
    "poster_url": POSTER_283,
    "poster_width": 283,
    "poster_height": 354,
    "trailer_url": "https://www.youtube.com/watch?v=hN_ZUElLH44",
    "review_slug": "udta-teer-review-roundup-critics",
}
ARTICLE = {"headline": "Udta Teer: Ayushmann Khurrana Soars in "
                       "This Hilarious Spy Comedy",
           "slug": "udta-teer-review-roundup-critics",
           "category": "entertainment"}


def widths(mapping):
    return lambda url: mapping.get(url)


def meta_of(meta):
    return lambda video_id: meta


# ── 1. THE case: 283x354 poster + gated trailer -> trailer still ──
res = fh.resolve_film_hero(FILM, ARTICLE,
                           width_of=widths({MAXRES: 1280}),
                           meta_fetcher=meta_of(REAL_META))
check("283px poster + gated trailer -> trailer_still",
      res["hero_kind"] == "trailer_still", str(res))
check("trailer still is the maxres URL", res["image_url"] == MAXRES)
check("trailer still caption is honest",
      res["image_caption"] == "Still from the official trailer of "
                              "'Udta Teer'.", str(res["image_caption"]))
check("poster width recorded in decision", res["poster_width"] == 283)

# ── 2. >=1200px poster -> poster kept ──
big = dict(FILM, poster_width=1200, poster_height=1500)
res = fh.resolve_film_hero(big, ARTICLE,
                           width_of=widths({}),
                           meta_fetcher=meta_of(REAL_META))
check("1200px poster -> poster kept",
      res["hero_kind"] == "poster" and res["image_url"] == POSTER_283,
      str(res))
check("kept poster leaves caption to caller",
      res["image_caption"] is None)

# ── 3. Small poster + NO trailer -> no hero (not the blurry poster) ──
notrailer = dict(FILM, trailer_url="https://www.youtube.com/results"
                                   "?search_query=Udta+Teer")
res = fh.resolve_film_hero(notrailer, ARTICLE,
                           width_of=widths({}),
                           meta_fetcher=meta_of(REAL_META))
check("small poster + search-URL trailer -> none",
      res["hero_kind"] == "none" and res["image_url"] is None, str(res))

# ── 4. Small poster + gate-rejected trailer -> no hero ──
res = fh.resolve_film_hero(FILM, ARTICLE,
                           width_of=widths({MAXRES: 1280}),
                           meta_fetcher=meta_of(FAN_META))
check("small poster + fan-channel trailer -> none",
      res["hero_kind"] == "none" and res["image_url"] is None, str(res))

# ── 5. Poster width measured (not recorded) + placeholder maxres ──
unrecorded = {k: v for k, v in FILM.items()
              if k not in ("poster_width", "poster_height")}
res = fh.resolve_film_hero(unrecorded, ARTICLE,
                           width_of=widths({POSTER_283: 283,
                                            MAXRES: 120}),
                           meta_fetcher=meta_of(REAL_META))
check("measured 283px poster + 120px placeholder maxres -> none",
      res["hero_kind"] == "none" and res["image_url"] is None, str(res))

# ── 6. No poster at all + gated trailer -> trailer still ──
noposter = dict(FILM, poster_url="", poster_width=None)
res = fh.resolve_film_hero(noposter, ARTICLE,
                           width_of=widths({MAXRES: 1280}),
                           meta_fetcher=meta_of(REAL_META))
check("no poster + gated trailer -> trailer_still",
      res["hero_kind"] == "trailer_still", str(res))

# ── 7. Width helpers: URL-carried widths need no network ──
check("wikimedia thumb width parses from path",
      fh.measure_image_width(
          "https://upload.wikimedia.org/wikipedia/en/thumb/c/c8/"
          "Udta_Teer_film_poster.jpg/500px-Udta_Teer_film_poster.jpg")
      == 500)
api, fname = fh._wikimedia_parts(POSTER_283)
check("wikimedia file parts", (api, fname) ==
      ("en.wikipedia.org", "Udta_Teer_film_poster.jpg"),
      f"{api} {fname}")
api, fname = fh._wikimedia_parts(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/"
    "Some_File.jpg/1024px-Some_File.jpg")
check("wikimedia thumb parts resolve to the file",
      (api, fname) == ("commons.wikimedia.org", "Some_File.jpg"),
      f"{api} {fname}")

# ── 8. fix_article_hero backstop (enrich-on-publish) ──
roster = [FILM]
art = dict(ARTICLE, image_url=POSTER_283)
fix = fh.fix_article_hero(art, roster=roster,
                          width_of=widths({POSTER_283: 283,
                                           MAXRES: 1280}),
                          meta_fetcher=meta_of(REAL_META))
check("backstop swaps sub-floor poster for trailer still",
      fix and fix["image_url"] == MAXRES, str(fix))
check("backstop caption is the honest trailer caption",
      fix and "official trailer" in (fix["image_caption"] or ""))

wide = dict(ARTICLE, image_url=MAXRES)
fix = fh.fix_article_hero(wide, roster=roster,
                          width_of=widths({MAXRES: 1280}),
                          meta_fetcher=meta_of(REAL_META))
check("backstop leaves a >=floor hero untouched", fix is None)

news = dict(ARTICLE, category="news", image_url=POSTER_283)
fix = fh.fix_article_hero(news, roster=roster,
                          width_of=widths({POSTER_283: 283}),
                          meta_fetcher=meta_of(REAL_META))
check("backstop ignores non-entertainment articles", fix is None)

other = dict(ARTICLE, slug="some-other-story",
             headline="A Story About Something Else",
             image_url=POSTER_283)
fix = fh.fix_article_hero(other, roster=roster,
                          width_of=widths({POSTER_283: 283}),
                          meta_fetcher=meta_of(REAL_META))
check("backstop ignores articles matching no roster film",
      fix is None)

print(f"\n{total - fails}/{total} passed")
raise SystemExit(1 if fails else 0)
