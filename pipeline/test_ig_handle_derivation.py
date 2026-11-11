"""Tests: Instagram handle derivation in enrich-on-publish.py (2026-11-11).

Covers the fallback used when registry-based IG enrichment finds
nothing (the Tyra Banks case):
  - headline name extraction and literal handle extraction;
  - account-search candidate picking (exact full_name wins, username
    concatenation matches, unrelated candidates rejected);
  - embed-page owner + caption parsing on a minimal synthetic fixture
    (built to resemble the real page structure — no scraped page is
    committed);
  - owner mismatch on the embed page rejects the post;
  - the caption keyword gate is identical to enrich_ig_from_cache
    (>=2 whole-word hits, or >=1 when <=2 keywords; no fallback to an
    unrelated latest post);
  - the full enrich_ig_from_derived_handles flow with subprocess
    fully faked (fake instagram-cli + fake curl embed pages);
  - the per-run derivation cap and the 429 hard stop.

Run: python3 test_ig_handle_derivation.py  (exit 0 = all pass)
"""
import importlib.util
import json
import os
import sys
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
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


def load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


enr = load("enrich_on_publish_derived", "enrich-on-publish.py")

# ── Headline name extraction ──────────────────────────────────────────────
names = enr.extract_headline_names(
    "Tyra Banks Wears a Lehenga by Maneesh Goyal at a New York Diwali Party")
check("headline names include both people",
      "Tyra Banks" in names and "Maneesh Goyal" in names, f"got {names}")
check("leading filler never starts a name",
      enr.extract_headline_names("The Indian Economy Grows Fast") ==
      ["Indian Economy"] or "The Indian" not in
      enr.extract_headline_names("The Indian Economy Grows Fast"))
check("single capitalized words are not names",
      enr.extract_headline_names("Markets rally after the Fed decision") == [])
check("possessive surname still yields the name",
      "Tyra Banks" in enr.extract_headline_names("Tyra Banks' Diwali Look Stuns"))

# ── Literal handle extraction from body / sources ─────────────────────────
article = {
    "headline": "Some headline",
    "body": ("<p>She documented the evening on Instagram as "
             "@tyrabanks, sharing photos.</p>"
             "<p>More at https://www.instagram.com/maneeshkgoyal/ and "
             "the post https://www.instagram.com/p/ABC123/ itself.</p>"),
    "sources": [{"name": "Wire", "url": "https://www.instagram.com/wirehandle/"}],
}
hints = enr.extract_ig_handle_hints(article)
check("instagram.com profile URLs yield handles",
      "maneeshkgoyal" in hints and "wirehandle" in hints, f"got {hints}")
check("@handle in an Instagram-mentioning sentence is a hint",
      "tyrabanks" in hints, f"got {hints}")
check("post path segment is never a handle",
      "p" not in hints and "abc123" not in hints, f"got {hints}")
plain = {"headline": "H", "body": "<p>Follow @randomuser for more.</p>"}
check("@handle outside an Instagram sentence is not a hint",
      enr.extract_ig_handle_hints(plain) == [])

# ── Account-search candidate picking ──────────────────────────────────────
users = [
    {"username": "tyra.banksfanpage", "full_name": "Mya"},
    {"username": "tyrabanks24", "full_name": "Tyra Banks"},
    {"username": "tyrabanks", "full_name": "T Y R A • B A N K S"},
    {"username": "someoneelse", "full_name": "Unrelated Person"},
]
picked = enr.pick_account_search_candidates(users, "Tyra Banks")
check("exact full_name match is picked first",
      picked and picked[0] == "tyrabanks24", f"got {picked}")
check("username-concatenation match is also picked",
      "tyrabanks" in picked, f"got {picked}")
check("non-matching candidates are rejected",
      "tyra.banksfanpage" not in picked and "someoneelse" not in picked,
      f"got {picked}")
check("no plausible candidate returns empty",
      enr.pick_account_search_candidates(users, "Nobody Here") == [])

# ── Embed-page parser (synthetic fixture) ─────────────────────────────────
FIXTURE = """<html><body>
<div class="Header"><a class="Username" href="https://www.instagram.com/tyrabanks/?utm_source=ig_embed&amp;ig_rid=X" data-ios-link="user?username=tyrabanks" target="_blank"><span class="UsernameText">tyrabanks</span></a></div>
<div class="Caption"><a class="CaptionUsername" href="https://www.instagram.com/tyrabanks/?utm_source=ig_embed" target="_blank">tyrabanks</a><br /><br />Green and gold for the Diwali celebration in New York!<br />With my friend <a href="/maneeshkgoyal/?utm_source=ig_embed">&#064;maneeshkgoyal</a> tonight.</div></div>
<div class="Footer">footer</div>
</body></html>"""
owner, caption = enr.parse_ig_embed_page(FIXTURE)
check("parser extracts the owner from the Username anchor",
      owner == "tyrabanks", f"got {owner}")
check("parser extracts caption text without tags/entities",
      "Diwali celebration in New York" in caption
      and "@maneeshkgoyal" in caption and "<" not in caption,
      f"got {caption!r}")
check("parser returns no owner for an ownerless page",
      enr.parse_ig_embed_page("<html><body>shell</body></html>") == (None, ""))
check("parser returns no owner for empty input",
      enr.parse_ig_embed_page("") == (None, ""))

# ── Caption keyword gate (same rule as enrich_ig_from_cache) ─────────────
kw = enr._ig_headline_keywords(
    "Tyra Banks Lehenga Diwali Celebration New York", "Tyra Banks")
check("keywords exclude the person's own name words and stopwords",
      "banks" not in kw and "tyra" not in kw and "new" not in kw
      and "lehenga" in kw and "diwali" in kw, f"got {kw}")
hits = enr._ig_caption_hits("A Diwali celebration with a lehenga look", kw)
check("whole-word caption hits are counted",
      set(hits) == {"lehenga", "diwali", "celebration"}, f"got {hits}")
check("substring-only caption text scores no hits",
      enr._ig_caption_hits("Looking forward to the weekend", kw) == [])

# ── Full flow with subprocess fully faked ─────────────────────────────────
class FakeResult:
    def __init__(self, stdout, returncode=0, stderr=""):
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = stderr


def embed_fixture(owner, caption_text):
    return (f'<div class="Header"><a class="Username" '
            f'href="https://www.instagram.com/{owner}/?utm_source=ig_embed">'
            f'<span class="UsernameText">{owner}</span></a></div>'
            f'<div class="Caption"><a class="CaptionUsername" '
            f'href="https://www.instagram.com/{owner}/">{owner}</a>'
            f'<br />{caption_text}</div></div><div class="Footer">x</div>')


TYRA_ARTICLE = {
    "headline": "Tyra Banks Lehenga Diwali Celebration in New York",
    "body": "<p>She documented the evening on Instagram.</p>",
    "sources": [],
}


def make_fake_run(post_pages, verified=("tyrabanks",), search_users=None,
                  profile_names=None):
    """post_pages: {shortcode: html}. Returns a subprocess.run stand-in
    dispatching on the command: instagram-cli account-search /
    user-profile / posts, and curl for embed pages."""
    if search_users is None:
        search_users = [
            {"username": "tyrabanks24", "full_name": "Tyra Banks"},
            {"username": "tyrabanks", "full_name": "T Y R A • B A N K S"},
        ]
    if profile_names is None:
        profile_names = {"tyrabanks": "T Y R A • B A N K S",
                         "tyrabanks24": "Tyra Banks"}

    def fake_run(cmd, **_kwargs):
        if cmd[0].endswith("instagram-cli"):
            sub = cmd[1]
            if sub == "account-search":
                return FakeResult(json.dumps({"users": search_users}))
            if sub == "user-profile":
                handle = cmd[cmd.index("--username") + 1]
                return FakeResult(json.dumps({"profiles": [{
                    "username": handle,
                    "name": profile_names.get(handle, handle),
                    "is_verified": handle in verified,
                    "follower_count": 100,
                }]}))
            if sub == "posts":
                posts = [{"platform": "instagram", "rank": i + 1,
                          "source_app": "INSTAGRAM",
                          "url": f"https://www.instagram.com/p/{sc}/"}
                         for i, sc in enumerate(post_pages)]
                return FakeResult(json.dumps(
                    {"count": len(posts), "posts": posts}))
        if cmd[0] == "curl":
            url = cmd[-1]
            sc = url.split("/p/")[1].split("/")[0]
            return FakeResult(post_pages[sc])
        raise AssertionError(f"unexpected command: {cmd}")

    return fake_run


orig_subprocess = enr.subprocess
orig_sleep = enr.time.sleep
enr.time.sleep = lambda *_a, **_k: None

# Happy path: rank-1 post is unrelated (skipped), rank-2 is the topical
# Diwali post and must win; the unverified exact-name fan account is
# passed over for the verified concatenated-username account.
pages = {
    "UNREL1": embed_fixture("tyrabanks", "A quiet morning coffee at home"),
    "DIWALI1": embed_fixture(
        "tyrabanks",
        "Green and gold lehenga for the Diwali celebration in New York"),
}
enr.subprocess = SimpleNamespace(run=make_fake_run(pages))
enr.IG_RATE_LIMITED = False
enr._IG_DERIVED_ATTEMPTS = 0
cache = {"ig": {}}
url, info = enr.enrich_ig_from_derived_handles(TYRA_ARTICLE, cache=cache)
check("derivation returns the topical post URL",
      url == "https://www.instagram.com/p/DIWALI1/", f"got {url}")
check("derivation info carries derived source, score and matches",
      info and info["source"] == "derived" and info["handle"] == "tyrabanks"
      and info["score"] == 9 and "diwali" in info["matched_keywords"]
      and "lehenga" in info["matched_keywords"], f"got {info}")
check("derivation writes verified posts into the shared cache shape",
      cache["ig"].get("tyrabanks", {}).get("posts")
      and cache["ig"]["tyrabanks"]["posts"][0]["ownerUsername"] == "tyrabanks"
      and cache["ig"]["tyrabanks"]["fetched_at"], f"got {cache}")

# Owner mismatch: the embed page proves a different author — reject.
pages_bad = {"BADOWN1": embed_fixture(
    "nottyra", "Diwali celebration lehenga New York")}
enr.subprocess = SimpleNamespace(run=make_fake_run(pages_bad))
enr._IG_DERIVED_ATTEMPTS = 0
url, info = enr.enrich_ig_from_derived_handles(TYRA_ARTICLE, cache={"ig": {}})
check("embed-page owner mismatch rejects the post",
      url is None and info is None, f"got {url} {info}")

# Unrelated captions only: never fall back to the latest post.
pages_off = {"OFFTOP1": embed_fixture("tyrabanks", "Beach day with friends")}
enr.subprocess = SimpleNamespace(run=make_fake_run(pages_off))
enr._IG_DERIVED_ATTEMPTS = 0
url, info = enr.enrich_ig_from_derived_handles(TYRA_ARTICLE, cache={"ig": {}})
check("unrelated latest post is never used as a fallback",
      url is None and info is None)

# One hit with many keywords fails the gate.
pages_one = {"ONEHIT1": embed_fixture("tyrabanks", "Diwali lights at home")}
enr.subprocess = SimpleNamespace(run=make_fake_run(pages_one))
enr._IG_DERIVED_ATTEMPTS = 0
url, info = enr.enrich_ig_from_derived_handles(TYRA_ARTICLE, cache={"ig": {}})
check("one keyword hit with many keywords fails",
      url is None and info is None, f"got {url} {info}")

# Unverified accounts are rejected even with an exact name match.
enr.subprocess = SimpleNamespace(run=make_fake_run(pages, verified=()))
enr._IG_DERIVED_ATTEMPTS = 0
url, info = enr.enrich_ig_from_derived_handles(TYRA_ARTICLE, cache={"ig": {}})
check("unverified candidate handles are rejected",
      url is None and info is None)

# Per-run cap: with the counter at the cap, no connector call is made.
cap_calls = []
cap_fake = make_fake_run(pages)


def counting_run(cmd, **kw):
    cap_calls.append(cmd)
    return cap_fake(cmd, **kw)


enr.subprocess = SimpleNamespace(run=counting_run)
enr._IG_DERIVED_ATTEMPTS = enr.IG_MAX_DERIVED_PER_RUN
url, info = enr.enrich_ig_from_derived_handles(TYRA_ARTICLE, cache={"ig": {}})
check("per-run derivation cap blocks further attempts",
      url is None and info is None and cap_calls == [])
enr._IG_DERIVED_ATTEMPTS = 0

# 429 from account-search is a hard stop for the whole run.
def fake_run_429(cmd, **_kwargs):
    if cmd[0].endswith("instagram-cli"):
        return FakeResult(json.dumps(
            {"provider_error": {"code": 429, "message": "rate limited"}}))
    raise AssertionError("curl must not be reached after a 429")


enr.subprocess = SimpleNamespace(run=fake_run_429)
enr.IG_RATE_LIMITED = False
url, info = enr.enrich_ig_from_derived_handles(TYRA_ARTICLE, cache={"ig": {}})
check("429 during derivation sets the run-wide IG stop",
      url is None and info is None and enr.IG_RATE_LIMITED is True)

enr.subprocess = orig_subprocess
enr.time.sleep = orig_sleep
enr.IG_RATE_LIMITED = False
enr._IG_DERIVED_ATTEMPTS = 0

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
