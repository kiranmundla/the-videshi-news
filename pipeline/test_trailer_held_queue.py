"""Regression tests for the 2026-10-15 trailer-watch fixes:
- day-first description dates (Netflix India house style)
- teaser-announced dates are NOT release dates (Aakasamlo Oka Tara)
- wider type signals ("Movie:" label, "in theatres")
- prose credits ("directed by X, staring A, B & Others", "It stars ...")
- Netflix title-page completion (anchored, fail-closed)
- held-brief queue: hold -> queue -> retry -> publish/dequeue, expiry
Fixtures are the real 2026-10-15 drops that four-in-a-row holds exposed.
Run: python3 test_trailer_held_queue.py  (exit 0 = all pass)
"""
import os
import sys
from datetime import datetime, timezone

_src = open("trailer-watch.py").read().split("if __name__")[0]
_ns = {}
exec(compile(_src, "trailer-watch.py", "exec"), _ns)

# Network-free stubs: every video is "live"; cast strip is a marker;
# Netflix page fetches are served from fixtures below.
_ns["_video_is_live"] = lambda vid: True
_ns["render_cast_strip_block"] = lambda cast: '<div class="vdc-cast">strip</div>'

parse_description = _ns["parse_description"]
extract_credits = _ns["extract_credits"]
resolve_release = _ns["resolve_release"]
build_brief_article = _ns["build_brief_article"]
netflix_title_completion = _ns["netflix_title_completion"]
load_held = _ns["load_held"]
queue_hold = _ns["queue_hold"]
dequeue_film = _ns["dequeue_film"]
merge_held_into_groups = _ns["merge_held_into_groups"]
attempt_brief = _ns["attempt_brief"]

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


CHANNELS = {
    "Netflix India": {"language": "Hindi", "industry": "streamer",
                      "channel_id": "UCfakeNetflix"},
    "Geetha Arts": {"language": "Telugu", "industry": "film",
                    "channel_id": "UCfakeGeetha"},
    "Sony Pictures": {"language": "English", "industry": "film",
                      "channel_id": "UCfakeSony"},
}

# ------------------------------------------------------- real fixtures
GAJAB_DESC = (
    "Ek raat aakhir kitni gajab ho sakti hai 👀\n\n"
    "Watch Gajab Raat, directed by Neeraj Pandey, staring Manoj Bajpayee, "
    "Nushrratt Bharuccha, Saqib Saleem, Divya Dutta, Kiku Sharda, "
    "Shraddha Das & Others, on 23 October, only on Netflix\n\n"
    "Watch on Netflix: https://www.netflix.com/title/81987289\n\n"
    "Follow Netflix India on:\nWebsite: https://www.netflix.com/")
GAJAB_DROP = {
    "video_id": "BwFuJbHNE4o",
    "title": ("Gajab Raat | Official Trailer | Manoj Bajpayee | "
              "Divya Dutta | Nushrratt B. | Netflix India"),
    "published": "2026-10-15T05:30:17+00:00",
    "description": GAJAB_DESC, "channel": "Netflix India",
}
STEPS_DESC = (
    "At midnight, we ride. Watch STEPS, only on Netflix, 20 November.\r\n\r\n"
    "Watch on Netflix: https://www.netflix.com/title/81212809\r\n\r\n"
    "Follow Netflix India on:\r\nWebsite: https://www.netflix.com/")
STEPS_DROP = {
    "video_id": "yOq52foXX5Y", "title": "STEPS | Official Trailer | Netflix",
    "published": "2026-10-15T13:00:07+00:00",
    "description": STEPS_DESC, "channel": "Netflix India",
}
AAKA_DESC = (
    "Every time he’s on screen, there’s something special about it ❤️\n\n"
    "And he’s all set to make us feel that magic once again 😍\n\n"
    "#AOTTeaser introduces you to its world on October 17th 💥\n\n"
    "Movie: Aakasamlo Oka Tara\n"
    "Starring: Dulquer Salmaan\n"
    "Music: GV Prakash Kumar\n"
    "Director: Pavan Sadineni\n"
    "Produced by Sandeep Gunnam, Ramya Gunnam Under Light Box Media Banner.\n"
    "Presented by Geetha Arts & Swapna Cinema")
AAKA_DROP = {
    "video_id": "jcCP78xGycE",
    "title": ("Aakasamlo Oka Tara Teaser on October 17th | Dulquer Salmaan | "
              "#AOTTeaser | GV Prakash Kumar"),
    "published": "2026-10-15T09:22:23+00:00",
    "description": AAKA_DESC, "channel": "Geetha Arts",
}
RAMA_DESC = (
    "From the visual artists behind The Odyssey and Dune watch the new "
    "trailer for RAMAYANA: RISE OF A LEGEND - exclusively in theatres, "
    "IMAX and Premium Large Formats worldwide November 5. Tickets on "
    "Sale now. \n\n\n\nBased on the celebrated ancient epic known to "
    "billions, Namit Malhotra's Ramayana: Rise of a Legend tells the "
    "story of Rama. It stars Ranbir Kapoor, Yash and Sai Pallavi. \n\u202f \n"
    "The film is produced by acclaimed filmmaker Namit Malhotra.\n\n"
    "Directed by Nitesh Tiwari")
RAMA_DROP = {
    "video_id": "AYkPRN874m8",
    "title": "RAMAYANA: RISE OF A LEGEND - NEW TRAILER",
    "published": "2026-10-15T14:00:39+00:00",
    "description": RAMA_DESC, "channel": "Sony Pictures",
}

# Netflix title-page fixtures: metaData anchored on topLevelVideoId,
# persons block after it — same shape as the live pages.
def nf_page(tid, typ, actors, directors=()):
    a = ",".join('{"name":"%s"}' % n.replace(" ", "\\x20") for n in actors)
    d = ",".join('{"name":"%s"}' % n.replace(" ", "\\x20") for n in directors)
    return ('{"metaData":{"isOriginal":true,"topLevelVideoId":%s,'
            '"type":"%s","videoId":%s},"persons":{"actors":[%s],'
            '"directors":[%s]}}' % (tid, typ, tid, a, d))


NF_PAGES = {
    "https://www.netflix.com/title/81212809": nf_page(
        81212809, "Movie",
        ["Ali Wong", "Amanda Seyfried", "Stephanie Hsu"]),
    "https://www.netflix.com/title/81987289": nf_page(
        81987289, "Movie", ["Manoj Bajpayee"], ["Neeraj Pandey"]),
}
_ns["_curl_browser"] = lambda url, timeout=30: NF_PAGES.get(url, "")

# ------------------------------------------------- parse_description
_, mt, rel = parse_description(GAJAB_DESC)
check("desc: day-first date '23 October' extracted", rel == "Oct 23")
check("desc: Gajab type comes from completion, not desc parsing",
      mt is None)
_, mt, rel = parse_description(STEPS_DESC)
check("desc: day-first date '20 November' extracted", rel == "Nov 20")
_, mt, rel = parse_description(AAKA_DESC)
check("desc: 'Movie:' credit label gives type", mt == "Movie")
check("desc: teaser-announced date is NOT a release date", rel is None)
_, mt, rel = parse_description(RAMA_DESC)
check("desc: 'in theatres' gives type Movie", mt == "Movie")
check("desc: month-first date still works", rel == "Nov 5")
_, _, rel = parse_description(
    "Watch the film, in cinemas worldwide December 25. "
    "The teaser broke records on October 10.")
check("desc: first date in text order wins over later teaser mention",
      rel == "Dec 25")

# ------------------------------------------------- extract_credits
cr = extract_credits(GAJAB_DESC)
check("credits: mid-sentence 'directed by' extracted",
      cr.get("director") == "Neeraj Pandey")
check("credits: 'staring' (house typo) cast extracted",
      cr.get("cast", "").startswith("Manoj Bajpayee, Nushrratt Bharuccha"))
check("credits: '& Others' / 'only on Netflix' never become names",
      "Others" not in cr.get("cast", "")
      and "Netflix" not in cr.get("cast", ""))
cr = extract_credits(RAMA_DESC)
check("credits: 'It stars X, Y and Z' cast extracted",
      cr.get("cast") == "Ranbir Kapoor, Yash, Sai Pallavi")

# ------------------------------------------- Netflix completion (unit)
comp = netflix_title_completion([STEPS_DROP])
check("netflix: STEPS type from its own title page",
      comp.get("media_type") == "Movie")
check("netflix: STEPS cast from its own title page",
      comp.get("cast", "").startswith("Ali Wong, Amanda Seyfried"))
comp = netflix_title_completion([dict(
    STEPS_DROP, description="Watch: https://www.netflix.com/title/99999999")])
check("netflix: unknown/unanchored id completes nothing", comp == {})
comp = netflix_title_completion([RAMA_DROP])
check("netflix: no title URL in description -> no completion", comp == {})

# ------------------------------------------------- full brief builds
art = build_brief_article([GAJAB_DROP], CHANNELS)
check("brief: Gajab Raat now completes the card", art["card_complete"])
check("brief: Gajab release pinned with year (Oct 23, 2026)",
      '<div class="vdc-stat-val">Oct 23, 2026</div>' in art["body"])
check("brief: Gajab carries Director row",
      '<div class="vdc-stat-val">Neeraj Pandey</div>' in art["body"])
check("brief: Gajab has >=2 sources (gate compliance)",
      len(art["sources"]) >= 2)

art = build_brief_article([STEPS_DROP], CHANNELS)
check("brief: STEPS now completes the card", art["card_complete"])
check("brief: STEPS release pinned with year (Nov 20, 2026)",
      '<div class="vdc-stat-val">Nov 20, 2026</div>' in art["body"])
check("brief: STEPS type row is Movie",
      '<div class="vdc-stat-val">Movie</div>' in art["body"])

art = build_brief_article([RAMA_DROP], CHANNELS)
check("brief: Ramayana now completes the card", art["card_complete"])
check("brief: '- NEW TRAILER' branding stripped from film name",
      art["headline"] == "RAMAYANA \u2013 RISE OF A LEGEND Trailer Out")
check("brief: Ramayana release pinned (Nov 5, 2026)",
      '<div class="vdc-stat-val">Nov 5, 2026</div>' in art["body"])

art = build_brief_article([AAKA_DROP], CHANNELS)
check("brief: Aakasamlo completes via verified date (2026-10-17 registry)",
      art["card_complete"] is True)
check("brief: verified date is the release date, never the teaser's own",
      '<div class="vdc-stat-val">Nov 20, 2026</div>' in art["body"]
      and "Oct 17, 2026" not in art["body"])

# Same-shaped brief for a film with NO registry entry stays held: the
# verified completion is fail-closed, not a blanket date pass. (This
# unregistered twin drives the held-queue scenario below.)
AAKA_UNREG_DROP = dict(
    AAKA_DROP,
    title=("Meghamala Teaser on October 17th | Dulquer Salmaan | "
           "#AOTTeaser | GV Prakash Kumar"))
art_unreg = build_brief_article([AAKA_UNREG_DROP], CHANNELS)
check("brief: unregistered film stays held — only date is the teaser's own",
      art_unreg["card_complete"] is False
      and art_unreg["card_missing"] == ["release date"])

# ------------------------------------------------------- held queue
_ns["sb_check_slug"] = lambda slug: False
_ns["sb_fetch_published_briefs"] = lambda limit=400: []
inserted = []
attempt_brief_fn = attempt_brief

# Run 1: unregistered film held -> outcome 'held'
outcome, art = attempt_brief_fn("meghamala", [AAKA_UNREG_DROP], CHANNELS,
                                [], lambda a: inserted.append(a) or True)
check("queue: incomplete brief outcome is 'held'", outcome == "held")

# Queue bookkeeping round-trip
held = {}
queue_hold(held, "meghamala", [AAKA_UNREG_DROP], art["card_missing"],
           "2026-10-15T10:11:00+00:00", attempts=1)
check("queue: hold persisted with missing fields + attempts",
      held["meghamala"]["last_missing"] == ["release date"]
      and held["meghamala"]["attempts"] == 1)

# A later drop for the same film (the real teaser, WITH a release date)
# unions into the queued entry.
teaser_drop = dict(AAKA_UNREG_DROP, video_id="teaserReal1",
                   title="Meghamala Official Teaser | Dulquer Salmaan",
                   description=AAKA_DESC + "\nIn Cinemas December 25, 2026.")
work = merge_held_into_groups([], held)
check("queue: queue-only film becomes a retry group",
      len(work) == 1 and work[0][0] == "meghamala")
work2 = merge_held_into_groups([["meghamala", [teaser_drop]]], held)
check("queue: fresh drop unions with queued drops (2 versions)",
      len(work2) == 1 and len(work2[0][1]) == 2)

# NOTE: at this point `attempt_brief`, etc. still refer to the exec'd
# namespace's functions — the completion stub above serves them.
outcome, art = attempt_brief_fn("meghamala", work2[0][1], CHANNELS,
                                [], lambda a: inserted.append(a) or True)
check("queue: retry with completed card publishes", outcome == "published")
check("queue: insert was called exactly once", len(inserted) == 1)
dequeue_film(held, "meghamala")
check("queue: published film dequeued", held == {})

# Insert failure is retryable, not terminal
outcome, _ = attempt_brief_fn("gajabraat", [GAJAB_DROP], CHANNELS, [],
                              lambda a: False)
check("queue: failed insert outcome is 'failed' (retryable)",
      outcome == "failed")

# -------------------- phantom-key re-keying (2026-10-23)
# A queue entry born from a dialogue-line title carries a phantom key;
# its drops re-key to the real film, so the retry works the real key,
# _held_entry_for still finds the entry (first_held_at/attempts carry
# over), and dequeue under the real key removes the phantom entry.
_held_entry_for = _ns["_held_entry_for"]
DNK_DROP = {
    "video_id": "WWBWDkWZjgg",
    "title": "Manam kooda families ey kada saar \U0001f642 | #DNKTeaser "
             "Out Now | Mouli | Sushmita Shetty | Sreenu Kambala",
    "published": "2026-10-22T12:58:00+00:00",
    "description": "Manam kooda families ey kada saar, Donga Naa Koduku "
                   "Teaser Out Now Video on @MythriMovieMakers \n\n"
                   "Donga Naa Koduku is an Upcoming Telugu movie ft. "
                   "Mouli, Sushmita Shetty & others.",
    "channel": "Mythri Movie Makers",
}
held2 = {}
queue_hold(held2, "manamkoodafamilieseykadasaar", [DNK_DROP],
           ["release date"], "2026-10-22T16:12:25+00:00", attempts=5)
work3 = merge_held_into_groups([], held2)
check("queue: phantom-key entry retries under the real film key",
      len(work3) == 1 and work3[0][0] == "donganaakoduku")
qk, entry = _held_entry_for(held2, "donganaakoduku")
check("queue: _held_entry_for finds the phantom entry by the real key",
      qk == "manamkoodafamilieseykadasaar" and entry["attempts"] == 5)
dnk_fresh = dict(DNK_DROP, video_id="otherVid1",
                 title="Donga Naa Koduku - Official Teaser | Mouli")
work4 = merge_held_into_groups([["donganaakoduku", [dnk_fresh]]], held2)
check("queue: fresh group unions phantom-key queued drops, keeps key",
      len(work4) == 1 and work4[0][0] == "donganaakoduku"
      and len(work4[0][1]) == 2)
dequeue_film(held2, "donganaakoduku")
check("queue: dequeue by the real key removes the phantom entry",
      held2 == {})

print(f"\n{total - fails}/{total} pass")
sys.exit(1 if fails else 0)
