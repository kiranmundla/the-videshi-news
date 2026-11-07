"""Regression tests for the trailer language-version check
(embed_placement.trailer_embed_gate leg 5, source-image.py film
identity, media-sources plumbing) and for source-image embed_trailer
placement normalization (reposition_bottom_trailer).

The case (2026-11-06): the enricher's source-image.py --trailer step
embedded the MALAYALAM Drishyam 3 trailer (2Q79yYfGFEM, Mohanlal /
Jeethu Joseph, Panorama Studios) into the HINDI Drishyam 3 article
(Ajay Devgn / Abhishek Pathak). It was caught by manual review and
removed. The trailer is a legitimate official trailer: title says
trailer, channel is allowlisted, US-playable — it passed every gate
leg because verification was never told which film, or which language
version of it, the article was about. Its title states no language;
only its description betrays the version ('...brought to life through
the lens of Malayalam cinema'). The Hindi film's own trailer
(BSZZwBaNQAA, Sony Music India) states no language anywhere, so the
rule is asymmetric by design: reject only on a POSITIVE mismatch
between a confidently derived article language and a confidently
detected candidate language.

Second case (2026-11-06, same day): the Pyre article's trailer landed
at ~99% through the body — embed_trailer inserts after the first
\n\n block, and on mega-block articles (key-takeaways + body in one
block) that is effectively invisible. The enrich paths have run
reposition_bottom_trailer on every body since 2026-10-12;
embed_trailer now does the same.

Fixtures use the REAL titles, channels and descriptions (fetched live
2026-11-06 via oEmbed + the Data API) and the real article's
headline/body sentences.

Run: python3 test_trailer_language_version.py  (exit 0 = all pass)
"""
import json
import sys
from types import SimpleNamespace

import review_trailer as rt
from embed_placement import (candidate_language, detect_stated_language,
                             detect_title_language, trailer_embed_gate)
from importlib.machinery import SourceFileLoader

ms = SourceFileLoader("media_sources", "media-sources.py").load_module()
si = SourceFileLoader("source_image", "source-image.py").load_module()

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


# ─── Real fixtures (fetched live 2026-11-06) ─────────────────────────
MAL_TITLE = ("Drishyam 3 - Official Trailer | Mohanlal | Jeethu Joseph "
             "| Meena | May 21 | Panorama Studios")
MAL_DESC = ("#Drishyam3 #Mohanlal #JeethuJoseph #Meena #Drishyam3Movie "
            "#AashirvadCinemas #PenStudios #PanoramaStudios\n\n"
            "Presenting Drishyam 3 Official Trailer | Mohanlal | "
            "Jeethu Joseph\n\nMay 21st 2026 | Worldwide Release\n\n"
            "Drishyam 3 continues the gripping saga of truth, deception, "
            "and consequences, brought to life through the lens of "
            "Malayalam cinema.\nHit 'I'm Interested' now for exclusive "
            "updates & more only on BookMyShow.")
MAL_META = {"title": MAL_TITLE, "channel_title": "Panorama Studios",
            "channel_id": "UC47fJuLOxYsOOq5R3adUXQA",
            "region_restriction": None, "description": MAL_DESC}

HIN_TITLE = ("Drishyam: The Conclusion | Official Trailer | Ajay Devgn, "
             "Tabu, Jaideep | Abhishek Pathak | 2 Oct")
HIN_DESC = ("Har drishya ek sawaal. Har raaz ek jawaab. Kaun hoga kispe "
            "bhaari?\n\nThe ultimate end begins now.\n\n"
            "#DrishyamTheConclusion TRAILER OUT NOW.\n\nIn cinemas "
            "2nd October. #DrishyamDay #2ndoctober")
HIN_META = {"title": HIN_TITLE, "channel_title": "Sony Music India",
            "channel_id": "UC56gTxNs4f9xZ7Pa2i5xNzg",
            "region_restriction": None, "description": HIN_DESC}

ARTICLE_HEADLINE = ("Drishyam 3 Ends BookMyShow Run As Bollywood's "
                    "Tenth Highest Ticket-Seller Ever")
ARTICLE_BODY = (
    '<div class="key-takeaways"><ul><li>Drishyam 3 sold 6.72 million '
    'tickets on BookMyShow in its five-week run, the highest for a '
    'Bollywood crime thriller on the platform.</li></ul></div>\n'
    "<p>Ajay Devgn's <em>Drishyam 3</em> has ended its BookMyShow run "
    "as Bollywood's tenth-highest ticket-selling film ever on the "
    "platform.</p>\n"
    "<p>The Hindi-language crime thriller — officially <em>Drishyam: "
    "The Conclusion</em>, directed by Abhishek Pathak — sold a total "
    "of 6.72 million tickets on BookMyShow.</p>\n"
    "<h2>The film</h2>\n"
    "<p>Drishyam 3 is a Hindi film, a point confirmed by its listing "
    "as a 2026 Indian Hindi-language crime thriller.</p>")


def gate(meta, **kw):
    return trailer_embed_gate(
        meta["title"], meta["channel_title"],
        channel_id=meta["channel_id"],
        region_restriction=meta["region_restriction"],
        region_checked=True, description=meta.get("description"), **kw)


# ─── Detectors: title tag ────────────────────────────────────────────
check("detect: parenthesized title tag",
      detect_title_language("#418 - Official Trailer (Hindi)") == "Hindi")
check("detect: inline title tag",
      detect_title_language("Mandaadi | Hindi Trailer | Soori, Suhas")
      == "Hindi")
check("detect: Malayalam trailer title states no language",
      detect_title_language(MAL_TITLE) is None)
check("detect: Hindi trailer title states no language",
      detect_title_language(HIN_TITLE) is None)

# ─── Detectors: stated language ──────────────────────────────────────
check("detect: Malayalam description states Malayalam",
      detect_stated_language(MAL_DESC) == "Malayalam")
check("detect: Hindi trailer description states nothing",
      detect_stated_language(HIN_DESC) is None)
check("detect: article body states Hindi",
      detect_stated_language(ARTICLE_BODY) == "Hindi")
check("detect: multi-language body is not single-language",
      detect_stated_language(
          "<p>Drishyam 3 is a Hindi film. The original was a "
          "Malayalam film.</p>") is None)
check("detect: subtitle mention is not the work's language",
      detect_stated_language(
          "<p>Now streaming with subtitles in English.</p>") is None)
check("detect: language list is not single-language",
      detect_stated_language(
          "Available in Hindi, Tamil and Telugu.") is None)

# ─── candidate_language precedence ───────────────────────────────────
check("candidate: description-only detection (the incident shape)",
      candidate_language(MAL_TITLE, MAL_DESC) == "Malayalam")
check("candidate: undetected language stays None",
      candidate_language(HIN_TITLE, HIN_DESC) is None)
check("candidate: title tag beats description statement",
      candidate_language("Vaashi | Telugu Official Trailer",
                         "a Malayalam cinema presentation") == "Telugu")

# ─── Gate leg 5: the Drishyam 3 regression ───────────────────────────
reason = gate(MAL_META, film_language="Hindi")
check("gate: Malayalam trailer rejected for the Hindi article",
      reason is not None and "wrong language version" in reason
      and "Malayalam" in reason, f"(got {reason!r})")
check("gate: same trailer accepted for a Malayalam article",
      gate(MAL_META, film_language="Malayalam") is None)
check("gate: version leg inert without an article language",
      gate(MAL_META) is None)
check("gate: article language compare is case-insensitive",
      gate(MAL_META, film_language="hindi") is not None)
check("gate: Hindi trailer accepted for the Hindi article "
      "(undetected candidate language never rejects)",
      gate(HIN_META, film_language="Hindi") is None)
check("gate: Hindi trailer accepted with roster title + language",
      gate(HIN_META, film_title="Drishyam: The Conclusion",
           film_language="Hindi") is None)

# Title-tagged candidate: language carried by the title alone.
tagged = dict(MAL_META,
              title="Drishyam 3 | Malayalam Official Trailer | Mohanlal",
              description="")
reason = gate(tagged, film_language="Hindi")
check("gate: title-tagged wrong version rejected",
      reason is not None and "wrong language version" in reason,
      f"(got {reason!r})")

# ─── media-sources plumbing ──────────────────────────────────────────
def oe(meta):
    return lambda vid: {"title": meta["title"],
                        "author": meta["channel_title"]}


def mf(meta):
    return lambda vid: meta


url = ms._verify_official_trailer(
    "2Q79yYfGFEM", film_language="Hindi", meta_fetcher=mf(MAL_META),
    oembed_fetcher=oe(MAL_META))
check("verify(media-sources): Malayalam candidate rejected for Hindi",
      url is None, f"(got {url!r})")

url = ms._verify_official_trailer(
    "2Q79yYfGFEM", film_language="Malayalam",
    meta_fetcher=mf(MAL_META), oembed_fetcher=oe(MAL_META))
check("verify(media-sources): Malayalam candidate accepted for Malayalam",
      url == "https://youtube.com/watch?v=2Q79yYfGFEM", f"(got {url!r})")

url = ms._verify_official_trailer(
    "BSZZwBaNQAA", film_language="Hindi", meta_fetcher=mf(HIN_META),
    oembed_fetcher=oe(HIN_META))
check("verify(media-sources): Hindi candidate accepted for Hindi",
      url == "https://youtube.com/watch?v=BSZZwBaNQAA", f"(got {url!r})")

# ─── source-image: article film identity ─────────────────────────────
article = {"headline": ARTICLE_HEADLINE,
           "slug": "drishyam-3-bookmyshow-tenth-highest-ticket-selling-"
                   "bollywood-film",
           "body": ARTICLE_BODY}
title, lang = si._article_film_identity(article)
check("identity: BookMyShow article derives Hindi from its body",
      lang == "Hindi", f"(got title={title!r}, lang={lang!r})")

title, lang = si._article_film_identity(
    {"headline": "Sensex Rallies 900 Points on Strong Earnings",
     "slug": "sensex-rallies-900-points", "body": "<p>Markets rose.</p>"})
check("identity: no film evidence derives nothing",
      title is None and lang is None, f"(got {title!r}, {lang!r})")

# Roster route: a claimed article takes the roster's curated record.
_orig_load_roster = rt.load_roster
rt.load_roster = lambda: [{
    "title": "Drishyam: The Conclusion",
    "review_slug": "drishyam-the-conclusion-review",
    "trailer_url": "https://www.youtube.com/watch?v=BSZZwBaNQAA",
    "language": "Hindi"}]
try:
    title, lang = si._article_film_identity(
        {"headline": "Drishyam: The Conclusion Review: A Taut Finale",
         "slug": "drishyam-the-conclusion-review", "body": ""})
finally:
    rt.load_roster = _orig_load_roster
check("identity: roster-claimed article takes roster title + language",
      title == "Drishyam: The Conclusion" and lang == "Hindi",
      f"(got {title!r}, {lang!r})")

# ─── source-image: route-level verification (stubbed lookups) ────────
class _FakeResp:
    def __init__(self, payload):
        self.status_code = 200
        self._payload = payload

    def json(self):
        return self._payload


def _stub_route(meta):
    si.requests = SimpleNamespace(
        get=lambda url, params=None, timeout=None: _FakeResp(
            {"title": meta["title"], "author_name": meta["channel_title"]}))
    rt.fetch_video_meta = lambda vid: meta


_orig_requests, _orig_fvm = si.requests, rt.fetch_video_meta
try:
    _stub_route(MAL_META)
    check("route(source-image): Malayalam video rejected for Hindi",
          si._verify_trailer_candidate("2Q79yYfGFEM",
                                       film_language="Hindi") is None)
    got = si._verify_trailer_candidate("2Q79yYfGFEM",
                                       film_language="Malayalam")
    check("route(source-image): Malayalam video accepted for Malayalam",
          got is not None and got[1] == "Panorama Studios",
          f"(got {got!r})")
    check("route(source-image): roster title leg also stops it",
          si._verify_trailer_candidate(
              "2Q79yYfGFEM", film_title="Drishyam: The Conclusion",
              film_language="Hindi") is None)
    _stub_route(HIN_META)
    got = si._verify_trailer_candidate("BSZZwBaNQAA",
                                       film_language="Hindi")
    check("route(source-image): Hindi video accepted for Hindi",
          got is not None and got[1] == "Sony Music India",
          f"(got {got!r})")
finally:
    si.requests, rt.fetch_video_meta = _orig_requests, _orig_fvm

# ─── embed_trailer placement (the Pyre regression) ───────────────────
class _FakeSubprocess:
    def __init__(self):
        self.payloads = []

    def run(self, args, capture_output=None, text=None, timeout=None):
        if "-d" in args:
            self.payloads.append(json.loads(args[args.index("-d") + 1]))
        return SimpleNamespace(stdout="204", stderr="")


def _embed_with(article_body, url="https://youtube.com/watch?v=BSZZwBaNQAA"):
    fake = _FakeSubprocess()
    orig_get, orig_sub = si.get_article, si.subprocess
    si.get_article = lambda aid: {"id": aid, "headline": "Pyre fixture",
                                  "body": article_body}
    si.subprocess = fake
    try:
        ok = si.embed_trailer("fixture-id", url, dry_run=False)
    finally:
        si.get_article, si.subprocess = orig_get, orig_sub
    return ok, (fake.payloads[0]["body"] if fake.payloads else None)


# Mega-block body: key-takeaways + eight paragraphs with NO \n\n until
# a short closing block — the first-\n\n split lands the tag at ~99%.
_paras = "".join(
    f"<p>Paragraph {i} of the story carries the narrative forward with "
    f"reported detail, named people and concrete numbers throughout.</p>"
    for i in range(8))
MEGA_BODY = ('<div class="key-takeaways"><ul><li>Pyre has won 18 '
             'awards.</li></ul></div>' + _paras
             + "\n\n<p>Short closing block.</p>")
ok, new_body = _embed_with(MEGA_BODY)
pos = new_body.find("<youtube>") / len(new_body) if new_body else -1
check("embed: mega-block trailer does not stay in the bottom 20%",
      ok and new_body is not None and 0 <= pos < 0.80,
      f"(ok={ok}, pos={pos:.2f})")
check("embed: mega-block trailer present exactly once",
      new_body is not None and new_body.count("<youtube>") == 1)

NORMAL_BODY = ("<p>First paragraph of the story.</p>\n\n"
               "<p>Second paragraph with more reported detail.</p>\n\n"
               "<p>Third paragraph continues the story at length.</p>\n\n"
               "<p>Fourth paragraph closes the piece.</p>")
ok, new_body = _embed_with(NORMAL_BODY)
pos = new_body.find("<youtube>") / len(new_body) if new_body else -1
check("embed: normal body keeps trailer mid-article",
      ok and new_body is not None and 0 <= pos < 0.80,
      f"(ok={ok}, pos={pos:.2f})")

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
