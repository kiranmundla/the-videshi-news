"""Regression tests for trailer-watch cross-run merge + film-card gate
(2026-10-13 fixes: duplicate #418 article; thin Man with the Bag / River
cards). Run: python3 test_trailer_watch_guards.py  (exit 0 = all pass)
"""
import sys
from datetime import datetime, timezone

_src = open("trailer-watch.py").read().split("if __name__")[0]
_ns = {}
exec(compile(_src, "trailer-watch.py", "exec"), _ns)

# Network-free stubs: every video is "live"; cast strip is a marker.
_ns["_video_is_live"] = lambda vid: True
_ns["render_cast_strip_block"] = lambda cast: '<div class="vdc-cast">strip</div>'

film_key = _ns["film_key"]
resolve_release = _ns["resolve_release"]
build_brief_article = _ns["build_brief_article"]
find_cross_run_match = _ns["find_cross_run_match"]
sb_merge_embeds = _ns["sb_merge_embeds"]

fails = 0
total = 0


def check(name, cond):
    global fails, total
    total += 1
    if cond:
        print(f"ok   {name}")
    else:
        fails += 1
        print(f"FAIL {name}")


def dt(y, m, d):
    return datetime(y, m, d, tzinfo=timezone.utc)


# ---------------------------------------------------------- resolve_release
check("release: Dec 2 from Oct 2026 -> Dec 2, 2026",
      resolve_release("Dec 2", dt(2026, 10, 13)) == "Dec 2, 2026")
check("release: Jan 15 from Oct 2026 -> Jan 15, 2027 (River case)",
      resolve_release("Jan 15", dt(2026, 10, 12)) == "Jan 15, 2027")
check("release: Oct 23 from Oct 5 2026 -> Oct 23, 2026",
      resolve_release("Oct 23", dt(2026, 10, 5)) == "Oct 23, 2026")
check("release: year already present -> unchanged",
      resolve_release("May 8, 2026", dt(2026, 10, 12)) == "May 8, 2026")
check("release: None passes through",
      resolve_release(None, dt(2026, 10, 12)) is None)
check("release: no ref date -> unchanged",
      resolve_release("Dec 2", None) == "Dec 2")

# ---------------------------------------------------------- film_key parity
HOMBALE_TITLE = ("#418 Kannada Official Trailer - The Last Warning | "
                 "Prashanth Neel Presents | Kirtan N | Oct 23rd Rel")
check("film_key: Hombale video title -> '418'",
      film_key(HOMBALE_TITLE) == "418")
check("film_key: published headline -> '418'",
      film_key("#418 Trailer Out: The Last Warning") == "418")

# ---------------------------------------------------------- cross-run match
BRIEFS = [
    {"id": "a1", "slug": "418-trailer-out-the-last-warning",
     "headline": "#418 Trailer Out: The Last Warning", "body": "", "sources": []},
    {"id": "a2", "slug": "drive-the-pretenders-teaser-out",
     "headline": "Drive \u2013 The Pretenders Teaser Out", "body": "", "sources": []},
]
check("cross-run: '418' matches the published #418 brief",
      (find_cross_run_match("418", BRIEFS) or {}).get("id") == "a1")
check("cross-run: exact 'drive' matches its brief",
      (find_cross_run_match("drive", BRIEFS) or {}).get("id") == "a2")
check("cross-run: short prefix 'driv' must NOT match (prefix needs >=5)",
      find_cross_run_match("driv", BRIEFS) is None)
check("cross-run: unknown film -> None",
      find_cross_run_match("someotherfilm", BRIEFS) is None)
check("cross-run: empty key -> None",
      find_cross_run_match("", BRIEFS) is None)

# ---------------------------------------------------------- card gate: hold
CHANNELS = {
    "Hombale Films": {"language": "Kannada", "industry": "film"},
    "Prime Video India": {"language": "English", "industry": "streamer"},
}
man_bag_drop = {
    "video_id": "td120jrwqvg",
    "title": "The Man with the Bag - Official Teaser | Prime Video India",
    "published": "2026-10-13T14:30:11+00:00",
    "description": ("It\u2019s the most wonderful heist of the year\n\n"
                    "#TheManWithTheBagOnPrime, New Movie, Dec 2\n\n"
                    "Follow us on:\nInstagram: https://www.instagram.com/primevideoin/"),
    "channel": "Prime Video India",
}
art = build_brief_article([man_bag_drop], CHANNELS)
check("gate: Man with the Bag (no credits) is held",
      art["card_complete"] is False)
check("gate: hold reason names the missing credit",
      "director/cast credit" in art["card_missing"])
check("gate: held brief's card still pins the year (Dec 2, 2026)",
      '<div class="vdc-stat-val">Dec 2, 2026</div>' in art["body"])

# --------------------------------------------------- card gate: normal film
desc_418 = (
    "Here's the Official Kannada Trailer of #418 movie  \n\n"
    "Movie Credits:\n\n"
    "Written and Directed by Kirtan Nadagouda\n"
    "Producers: Naveen Yerneni & Ravi Shankar\n"
    "Banner: Mythri Movie Makers\n"
    "Presented by: Prashanth Neel\n\n"
    "Cast: Chaithra J Achar, Ramesh Indira, Surya Raj Veerabathini\n\n"
    "Music: Venky GG")
drop_418 = {
    "video_id": "YB1_ZO74noM",
    "title": HOMBALE_TITLE,
    "published": "2026-10-13T12:16:42+00:00",
    "description": desc_418,
    "channel": "Hombale Films",
}
art = build_brief_article([drop_418], CHANNELS)
check("gate: credited film passes the gate (normal insert still works)",
      art["card_complete"] is True and art["card_missing"] == [])
check("gate: passing brief pins release year from title date (Oct 23, 2026)",
      '<div class="vdc-stat-val">Oct 23, 2026</div>' in art["body"])
check("gate: passing brief carries a Producer credit row",
      '<div class="vdc-stat-val">Naveen Yerneni, Ravi Shankar</div>' in art["body"])
check("gate: passing brief headline matches the real 2026-10-13 stub headline",
      art["headline"] == "#418 \u2013 The Last Warning Trailer Out: Prashanth Neel Presents")

# ---------------------------------------------------------- merge behaviour
patches = []
_ns["sb_patch_article"] = lambda aid, payload: patches.append((aid, payload)) or True
existing = {
    "id": "a1", "slug": "418-trailer-out-the-last-warning",
    "body": ('<p>intro</p>'
             '<p><b>Kannada</b> \u2014 Mythri Movie Makers</p>'
             '<youtube>https://www.youtube.com/watch?v=IFgK5ynoe6s</youtube>'
             '<div class="related-coverage">related</div>'),
    "sources": [{"name": "Mythri Movie Makers",
                 "url": "https://www.youtube.com/watch?v=IFgK5ynoe6s"}],
}
old_drop = dict(drop_418, video_id="IFgK5ynoe6s",
                title="#418 Kannada Official Trailer - The Last Warning | Mythri Movie Makers")
added = sb_merge_embeds(existing, [old_drop, drop_418], CHANNELS)
check("merge: only the genuinely new video is added", added == 1)
check("merge: exactly one PATCH issued", len(patches) == 1)
new_body = patches[0][1]["body"] if patches else ""
check("merge: new embed lands before related-coverage",
      0 < new_body.find("YB1_ZO74noM") < new_body.find("related-coverage"))
check("merge: source appended for the new channel",
      len((patches[0][1].get("sources") or [])) == 2)
existing["body"] = new_body
added2 = sb_merge_embeds(existing, [old_drop, drop_418], CHANNELS)
check("merge: re-run with everything embedded adds nothing, no PATCH",
      added2 == 0 and len(patches) == 1)

# --------------------------------------- is_trailer: launch-event coverage
# 2026-10-14: Lahari Music uploaded launch-event speeches whose titles say
# "Teaser Launch" (and one "Teaser Lunch Event Live") — the Oct-7 block only
# covered "trailer launch", so all 7 reached the trailers rail pool. Fixtures
# are the exact titles from .state/trailer-watch-feed.json (purged same day).
is_trailer = _ns["is_trailer"]
LIVE_EVENT_RE = _ns["_LIVE_EVENT_RE"]
HAINDAVA_BAD = [
    "Producer Mahesh Chandu Speech at Haindava Teaser Launch | Bellamkonda Sai Sreenivas | Lahari Music",
    "Production Designer Siva Kamesh Speech at Haindava Teaser Launch | Bellamkonda Sai Sreenivas",
    "Hero Bellamkonda Sai Sreenivas Speech at Haindava Teaser Launch | Lahari Music",
    "Haindava Teaser Lunch Event Live | Bellamkonda Sai Sreenivas, Samyuktha | Sam C.S. | Ludheer Byreddy",
    "Production Designer Mallikarjun Speech at Haindava Teaser Launch | Bellamkonda Sai Sreenivas",
    "Director Ludheer Byreddy Speech at Haindava Teaser Launch | Bellamkonda Sai Sreenivas | Lahari Music",
    "Samyuktha Speech at Haindava Teaser Launch | Bellamkonda Sai Sreenivas | Lahari Music",
]
for i, t in enumerate(HAINDAVA_BAD, 1):
    check(f"filter: Haindava launch-coverage #{i} is NOT a trailer",
          is_trailer(t) is False)
check("filter: 'Lunch Event Live' title is a live event (brief gate)",
      bool(LIVE_EVENT_RE.search(HAINDAVA_BAD[3])))
HAINDAVA_GOOD = ("Haindava Official Teaser | Bellamkonda Sai Sreenivas, "
                 "Samyuktha | Sam C.S. | Ludheer Byreddy")
check("filter: the real Haindava teaser still passes",
      is_trailer(HAINDAVA_GOOD) is True)
check("filter: Man with the Bag teaser still passes",
      is_trailer("The Man with the Bag - Official Teaser | Prime Video India") is True)
check("filter: #418 trailer still passes",
      is_trailer(HOMBALE_TITLE) is True)
check("filter: Narnia trailer still passes",
      is_trailer("NARNIA: THE MAGICIAN\u2019S NEPHEW | Official Trailer | Netflix") is True)

# --------------------------------------- published-briefs query encoding
# 2026-10-14: sb_fetch_published_briefs hand-built its PostgREST query and
# embedded the ISO since-timestamp raw; its '+00:00' decoded as a space,
# PostgREST returned HTTP 400 (Postgres 22007), and the error object was
# silently read as "no briefs" — the cross-run duplicate guard was inert
# in production. The query builder must round-trip every value intact.
from urllib.parse import parse_qs

build_q = _ns["_published_briefs_query"]
SINCE_ISO = "2026-04-18T02:12:01.150201+00:00"
qs = parse_qs(build_q(SINCE_ISO, 400))
check("query: published_at survives URL round-trip ('+00:00' intact)",
      qs.get("published_at") == [f"gte.{SINCE_ISO}"])
check("query: or-filter survives URL round-trip",
      qs.get("or") == ["(headline.like.*Trailer Out*,headline.like.*Teaser Out*)"])
check("query: no raw '+' anywhere in the built query string",
      "+" not in build_q(SINCE_ISO, 400))

print(f"\n{total - fails}/{total} pass")
sys.exit(1 if fails else 0)
