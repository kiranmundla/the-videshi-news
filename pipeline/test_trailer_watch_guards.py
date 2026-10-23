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

# --------------------------------- series type inference (2026-10-17)
# Chaar Yaar held on 'type': its ONLY series marker was the '#webseries'
# hashtag in the Prime description (boilerplate says "original series"
# on film drops too, so the bare word is never read). Fixtures are
# trimmed copies of the real held drops (.state/trailer-watch-held.json).
parse_description = _ns["parse_description"]
CHAAR_DESC = (
    "Prime Video India Presents \n"
    "Chaar Yaar Official Trailer\n"
    "Starring Purav Jha, Naman Jain, Saqib Ayub, Prayrak Mehta, "
    "Sikandar Kher, Sai Tamhankar\n"
    "Directed by Vinay Waikul\n\n"
    "Official Release Date - October 23, 2026 on Prime Video India\n\n"
    "#chaaryaar #puravjha #trailer #officialtrailer #webseries "
    "#primevideoindia")
check("type: '#webseries' hashtag infers Series (Chaar Yaar)",
      parse_description(CHAAR_DESC)[1] == "Series")
check("type: 'web series' prose infers Series",
      parse_description("The web series returns this fall.")[1] == "Series")
check("type: episode count infers Series",
      parse_description("The show drops 8 episodes this fall.")[1] == "Series")
check("type: hyphenated episode adjective infers Series",
      parse_description("An eight-episode crime saga.")[1] == "Series")
check("type: Prime boilerplate 'original series' does NOT infer Series",
      parse_description("Original movies like Maja Ma; original series "
                        "like Mirzapur, only on Prime.")[1] is None)

CHANNELS2 = dict(CHANNELS)
CHANNELS2["Geetha Arts"] = {"language": "Telugu", "industry": "film"}
CHANNELS2["Netflix India"] = {"language": "English", "industry": "streamer"}
# Hermetic: Akka must complete via trailer-verified.json, not the live
# Netflix page (unreachable from this server in production too).
_ns["netflix_title_completion"] = lambda drops: {}

chaar_drop = {
    "video_id": "WZdXyU1fatY",
    "title": "Chaar Yaar - Official Trailer | @Puravjha_, Naman Jain, "
             "Saqib Ayub, Prayrak Mehta | Prime Video IN",
    "published": "2026-10-16T06:30:03+00:00",
    "description": CHAAR_DESC,
    "channel": "Prime Video India",
}
art = build_brief_article([chaar_drop], CHANNELS2)
check("gate: Chaar Yaar (series via hashtag) passes the gate",
      art["card_complete"] is True and art["card_missing"] == [])
check("gate: Chaar Yaar card type is Series",
      '<div class="vdc-stat-val">Series</div>' in art["body"])
check("gate: Chaar Yaar card release is Oct 23, 2026",
      '<div class="vdc-stat-val">Oct 23, 2026</div>' in art["body"])

# ------------------------------ verified completion (2026-10-17)
AOT_DESC = (
    "Movie: Aakasamlo Oka Tara\n"
    "Starring: Dulquer Salmaan, Satvika Veeravalli, Shruti Haasan\n\n"
    "Director - Pavan Sadineni\n"
    "Music Director - G V Prakash Kumar")
aot_drop = {
    "video_id": "h3ElWvu31dc",
    "title": "Aakasamlo Oka Tara - Teaser | Dulquer Salmaan | Satvika | "
             "Shruti Haasan |GV Prakash | Pavan Sadineni",
    "published": "2026-10-17T05:30:03+00:00",
    "description": AOT_DESC,
    "channel": "Geetha Arts",
}
art = build_brief_article([aot_drop], CHANNELS2)
check("control: AOT still types as Movie (series rules do not misfire)",
      '<div class="vdc-stat-val">Movie</div>' in art["body"])
check("gate: AOT passes via verified release date (Nov 20, 2026)",
      art["card_complete"] is True and
      '<div class="vdc-stat-val">Nov 20, 2026</div>' in art["body"])
check("lang: AOT takeaway states the work's language (Telugu movie)",
      "New Telugu movie premiering Nov 20, 2026 on Geetha Arts."
      in art["body"])

AKKA_DESC = (
    "Ab chalega beheno ka shaasan\n\n"
    "Watch Akka, starring Keerthy Suresh, Radhika Apte, Tanvi Azmi & "
    "more, out 30 October, only on Netflix.\n\n"
    "Watch on Netflix: https://www.netflix.com/title/81772076")
akka_drop = {
    "video_id": "d1zge_JMIIU",
    "title": "Akka | Official Teaser | Keerthy Suresh, Radhika Apte | "
             "Netflix India",
    "published": "2026-10-17T05:30:00+00:00",
    "description": AKKA_DESC,
    "channel": "Netflix India",
}
art = build_brief_article([akka_drop], CHANNELS2)
check("gate: Akka passes via verified type/director (Series, Oct 30, 2026)",
      art["card_complete"] is True and
      '<div class="vdc-stat-val">Series</div>' in art["body"] and
      '<div class="vdc-stat-val">Oct 30, 2026</div>' in art["body"] and
      '<div class="vdc-stat-val">Dharmaraj Shetty</div>' in art["body"])

# ------------------------------ 'Trailer 2' cross-run key (2026-10-17)
check("key: 'Trailer 2 :' keys to the film, not 'trailer2...'",
      film_key("Trailer 2 : Ramayana: Rise of a Legend | Ranbir Kapoor")
      == "ramayanariseofalegend")
# (The published headline keys to the prefix 'ramayana' — the
# subtitle-strip treats 'Rise of a Legend' as a suffix descriptor —
# and find_cross_run_match's >=5-char prefix rule is the contract
# that joins the two; the merge check below pins that behaviour.)
check("merge: cross-run match finds the Ramayana brief for Trailer 2",
      find_cross_run_match(
          film_key("Trailer 2 : Ramayana: Rise of a Legend | "
                   "Ranbir Kapoor"),
          [{"headline": "RAMAYANA \u2013 RISE OF A LEGEND Trailer Out",
            "slug": "ramayana-rise-of-a-legend-trailer-out",
            "id": "x", "body": "", "sources": []}]) is not None)

# ----------------- 'Series directed by' type inference (2026-10-23)
# Kauriburir Mandir held on 'type': hoichoi's teaser states the type in
# its own announcement line ('Series directed by Sayantan Ghosal
# premieres 6th November'), which no existing pattern read. Fixture is a
# trimmed copy of the real held drop (.state/trailer-watch-held.json).
drop_key = _ns["drop_key"]
KAURI_DESC = (
    "ঘন জঙ্গলের গভীরে লুকিয়ে আছে এমন এক অভিশাপ।\n\n"
    "#KauriburirMandir: Official Teaser | Series directed by Sayantan "
    "Ghosal premieres 6th November, only on #hoichoi.\n\n"
    "Jeetu Kamal Solanki Roy Paoli Dam Saswata Chatterjee Aniruddha "
    "Gupta Debopriyo Mukherjee Avik Sarkar Nabarun Bose")
check("type: 'Series directed by' infers Series (Kauriburir Mandir)",
      parse_description(KAURI_DESC)[1] == "Series")
check("type: 'The series premieres' clause infers Series",
      parse_description("The series premieres November 6, only on "
                        "hoichoi.")[1] == "Series")
check("type: 'film series premieres' does NOT infer Series",
      parse_description("The film series premieres its third chapter "
                        "this Diwali.")[1] is None)
check("type: 'web series directed by' still infers Series",
      parse_description("A web series directed by Ananya Rao, coming "
                        "soon.")[1] == "Series")

CHANNELS3 = dict(CHANNELS2)
CHANNELS3["Hoichoi"] = {"language": "Bengali", "industry": "streamer"}
kauri_drop = {
    "video_id": "diDs33qgGNI",
    "title": "Official Teaser - Kauriburir Mandir | Jeetu Kamal, Paoli "
             "Dam | Sayantan Ghosal | 6 NOV | hoichoi",
    "published": "2026-10-22T11:30:28+00:00",
    "description": KAURI_DESC,
    "channel": "Hoichoi",
}
art = build_brief_article([kauri_drop], CHANNELS3)
check("gate: Kauriburir Mandir passes once type is read from the drop",
      art["card_complete"] is True and art["card_missing"] == [])
check("gate: Kauriburir Mandir card type is Series",
      '<div class="vdc-stat-val">Series</div>' in art["body"])
check("gate: Kauriburir Mandir card release is Nov 6, 2026",
      '<div class="vdc-stat-val">Nov 6, 2026</div>' in art["body"])

# ----------------- dialogue-line title keying (2026-10-23)
# Mythri titled the Donga Naa Koduku teaser with a dialogue line, so the
# drop keyed a phantom film and could not merge into the published brief.
DNK_TITLE = ("Manam kooda families ey kada saar \U0001f642 | #DNKTeaser "
             "Out Now | Mouli | Sushmita Shetty | Sreenu Kambala")
DNK_DESC = (
    "Manam kooda families ey kada saar, Donga Naa Koduku Teaser Out Now "
    "Video on @MythriMovieMakers \n\n"
    "Donga Naa Koduku is an Upcoming Telugu movie ft. Mouli, Sushmita "
    "Shetty & others. Directed by Sreenu Kambala.\n\n"
    "#DongaNaaKodukuTeaser #DongaNaaKoduku #Mouli #SushmitaShetty")
check("key: dialogue-line title keys via description announcement",
      drop_key({"title": DNK_TITLE, "description": DNK_DESC})
      == "donganaakoduku")
check("key: announcement corroborating the title keeps the title key",
      drop_key({"title": "Donga Naa Koduku - Official Teaser | Mouli",
                "description": "Donga Naa Koduku Teaser Out Now."})
      == "donganaakoduku")
check("key: no announcement in description keeps the title key",
      drop_key({"title": "Bhogi - Official Teaser | Sharwanand",
                "description": "Bhogi teaser out now. Starring "
                               "Sharwanand."}) == "bhogi")
check("key: announcement beyond the opening lines is ignored",
      drop_key({"title": DNK_TITLE,
                "description": "Line one.\nLine two.\nLine three.\n"
                               "Line four.\nSome Other Film Teaser Out "
                               "Now."}) == "manamkoodafamilieseykadasaar")

# ----------------- work language in brief + card (2026-10-23)
# Kiran: movie/series coverage must state the work's language — in the
# brief text and the Film information card. Production
# trailer-channels.json sets NO per-channel language (channels carry
# industry only), so these fixtures use production-shaped channel dicts:
# derivation must come from the title tag, the description, or the
# single-language industry map — never an invented label.
derive_drop_language = _ns["derive_drop_language"]
extract_description_language = _ns["extract_description_language"]
CHANNELS_PROD = {
    "Hoichoi": {"industry": "bengali"},
    "Mythri Movie Makers": {"industry": "telugu"},
    "Warner Bros. Pictures": {"industry": "hollywood"},
}
check("lang: hashtag '#BengaliWebSeries' states Bengali",
      extract_description_language(
          "Watch it now #BengaliWebSeries only on hoichoi") == "Bengali")
check("lang: 'language: Bengali' credit line states Bengali",
      extract_description_language(
          "Credits\nLanguage: Bengali\nRuntime: 40 min") == "Bengali")
check("lang: 'Bengali series' adjective phrase states Bengali",
      extract_description_language(
          "A gripping Bengali series about a cursed temple.") == "Bengali")
check("lang: 'in Bengali' states Bengali",
      extract_description_language(
          "The teaser is in Bengali with English subtitles.") == "Bengali")
check("lang: subtitle-only mention yields None (not the work's language)",
      extract_description_language(
          "Subtitles in English available on release day.") is None)
check("lang: several languages named -> None (no guessed label)",
      extract_description_language(
          "Releasing in Hindi, Tamil and Telugu.") is None)
check("lang: hoichoi industry alone -> Bengali",
      derive_drop_language(
          {"title": "Some Teaser | hoichoi", "description": "A teaser.",
           "channel": "Hoichoi"}, CHANNELS_PROD["Hoichoi"]) == "Bengali")
check("lang: description cue beats industry",
      derive_drop_language(
          {"title": "Some Teaser | hoichoi",
           "description": "Presenting our new Hindi series, coming soon.",
           "channel": "Hoichoi"}, CHANNELS_PROD["Hoichoi"]) == "Hindi")
check("lang: title tag beats description + industry",
      derive_drop_language(
          {"title": "Some Film - Official Trailer (Telugu)",
           "description": "A Bengali series event.",
           "channel": "Hoichoi"}, CHANNELS_PROD["Hoichoi"]) == "Telugu")
check("lang: pan-language industry (hollywood) + no cue -> None",
      derive_drop_language(
          {"title": "Some Film - Official Trailer",
           "description": "A trailer.", "channel": "Warner Bros. Pictures"},
          CHANNELS_PROD["Warner Bros. Pictures"]) is None)

# End-to-end, production channels: the Kauriburir fixture's description
# never names Bengali in Latin text — the language comes from hoichoi's
# bengali industry, and must land in the card, the takeaway, and the
# corrected (streaming, not theaters) diaspora sentence.
art = build_brief_article([kauri_drop], CHANNELS_PROD)
check("lang: Kauriburir gate still passes with production channels",
      art["card_complete"] is True)
check("lang: Kauriburir card carries a Language stat (Bengali)",
      '<div class="vdc-stat-val">Bengali</div>'
      '<div class="vdc-stat-lbl">Language</div>' in art["body"])
check("lang: Kauriburir takeaway states 'Bengali series'",
      "New Bengali series premiering Nov 6, 2026 on Hoichoi."
      in art["body"])
check("lang: series heads to its platform, not theaters",
      "what's headed to Hoichoi" in art["body"]
      and "headed to theaters" not in art["body"])

# Pan-language channel, no cue anywhere: no stat, brief still publishes,
# and a theatrical film still says theaters.
wb_drop = {
    "video_id": "wbTest12345",
    "title": "The Longest Yard Sale - Official Trailer | Warner Bros. "
             "Pictures",
    "published": "2026-10-20T10:00:00+00:00",
    "description": ("The Longest Yard Sale Official Trailer\n\n"
                    "Directed by Jane Doe\n"
                    "Starring John Smith, Ana Lee\n\n"
                    "New Movie, Nov 20"),
    "channel": "Warner Bros. Pictures",
}
art = build_brief_article([wb_drop], CHANNELS_PROD)
check("lang: unknown language -> no Language/Languages stat on the card",
      'vdc-stat-lbl">Language<' not in art["body"]
      and 'vdc-stat-lbl">Languages<' not in art["body"])
check("lang: unknown language -> brief still publishes (gate passes)",
      art["card_complete"] is True)
check("lang: theatrical film still heads to theaters",
      "what's headed to theaters" in art["body"])

# Two language versions of one film: plural stat, 'Out in' takeaway,
# and no single language woven into the premiere takeaway.
multi_desc = ("Film Credits:\n\nDirected by Raj Rao\n"
              "Cast: Ana Lee, John Smith\n\nNew Movie, Dec 5")
drop_h = {"video_id": "multiH12345",
          "title": "Border Tales - Official Trailer (Hindi)",
          "published": "2026-10-20T10:00:00+00:00",
          "description": multi_desc, "channel": "Mythri Movie Makers"}
drop_t = dict(drop_h, video_id="multiT12345",
              title="Border Tales - Official Trailer (Telugu)")
art = build_brief_article([drop_h, drop_t], CHANNELS_PROD)
check("lang: two versions -> plural Languages stat",
      '<div class="vdc-stat-val">Hindi, Telugu</div>'
      '<div class="vdc-stat-lbl">Languages</div>' in art["body"])
check("lang: two versions -> 'Out in' takeaway, no single-language weave",
      "Out in Hindi, Telugu" in art["body"]
      and "New Hindi movie premiering" not in art["body"])

print(f"\n{total - fails}/{total} pass")
sys.exit(1 if fails else 0)
