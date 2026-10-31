#!/usr/bin/env python3
"""
test_image_ledger.py — unit tests for Rung 0 of the image-sourcing
rebuild: the intent + provenance ledger (image_ledger.py) and its
wiring into the insert choke points and the picture pass.

Covers: canonical file-key parity with the picture pass, route and
rights derivation, intent population (writer values win, derivation
fills gaps, nothing invented for empty articles), JSONL placement +
removal writes with history folding, DB-sync silence when creds /
the column are absent, the picture pass writing ledger records on
--apply and NOT on dry-run, and a stubbed-curl end-to-end proof
that v3-insert-article.py now inserts populated intent columns and
records the writer-hero placement.

All network is stubbed. Run:
  python3 test_image_ledger.py   (exit 0 = all pass)
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import image_ledger as L

FAILS = []


def check(name, cond, extra=""):
    print(("  ✓ " if cond else "  ✗ ") + name
          + (f" — {extra}" if extra and not cond else ""))
    if not cond:
        FAILS.append(name)


def check_eq(name, got, want):
    check(name, got == want, f"got {got!r}, want {want!r}")


# Point the ledger at a temp file for the whole suite, and make
# sure no real Supabase creds leak into DB-sync attempts.
_TMP = tempfile.mkdtemp(prefix="imgledger-")
LEDGER = Path(_TMP) / "ledger.jsonl"
os.environ["IMAGE_LEDGER_PATH"] = str(LEDGER)
_SAVED_ENV = {k: os.environ.pop(k, None)
              for k in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")}

BODY = (
    '<div class="key-takeaways"><ul><li>Takeaway one.</li></ul>'
    '</div>'
    '<p>Intro paragraph about the Reserve Bank of India opening '
    'its new data centre in Bhubaneswar on Sunday.</p>'
    '<h2>What Was Announced</h2>'
    '<p>The Reserve Bank of India said the Bhubaneswar facility '
    'will anchor its cybersecurity training for banks across the '
    'country, with Narendra Modi attending the inauguration.</p>'
    '<p>Officials said the centre will train thousands of bank '
    'staff every year.</p>'
    '<h2>Why It Matters</h2>'
    '<p>Analysts said the Reserve Bank of India move signals a '
    'deeper push on digital-payment security.</p>'
    '<p>More detail on the programme and its first cohort.</p>'
    + '<p>Filler paragraph to clear the word floor. </p>' * 40
)

ARTICLE = {
    "id": "art-1", "slug": "modi-rbi-data-centre-bhubaneswar",
    "headline": "Modi Inaugurates RBI Data Centre in Bhubaneswar",
    "category": "news", "image_url": None,
    "image_caption": "", "image_attribution": "",
    "image_entities": ["Nri World", "Reserve Bank of India"],
    "image_backfill_blocked": False,
    "published_at": "2026-10-25T12:46:00Z",
    "body": BODY, "sources": [],
}


# ── canonical file identity ───────────────────────────────────────
print("file_key parity with the picture pass")
import article_picture_pass as P
_FORMS = [
    "https://upload.wikimedia.org/wikipedia/commons/1/1a/"
    "Reserve_Bank_of_India_Building.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/"
    "Reserve_Bank_of_India_Building.jpg/1920px-"
    "Reserve_Bank_of_India_Building.jpg?utm_source=x",
    "File:Reserve Bank of India Building.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/9/9b/"
    "TCS_SIPCOT_Building.jpg",
]
for form in _FORMS:
    check_eq(f"file_key matches picture pass: {form[:52]}…",
             L.file_key_for(form), P._wikimedia_file_key(form))
check_eq("file_key of empty/None", L.file_key_for(None), None)
check_eq("commons page URL derived",
         L.commons_file_page_url(_FORMS[0]),
         "https://commons.wikimedia.org/wiki/File:"
         "reserve_bank_of_india_building.jpg")
check_eq("no commons page for non-wikimedia URL",
         L.commons_file_page_url("https://example.com/x.jpg"), None)


# ── route + rights derivation ─────────────────────────────────────
print("route derivation")
check_eq("sourcer og:image", L.route_from_sourcer_name("og:image"),
         "source_og")
check_eq("sourcer person_cache",
         L.route_from_sourcer_name("person_cache"), "person_profile")
check_eq("sourcer youtube_thumbnail",
         L.route_from_sourcer_name("youtube_thumbnail"),
         "youtube_thumb")
check_eq("sourcer commons_search",
         L.route_from_sourcer_name("commons_search"), "wikimedia")
check_eq("sourcer unknown name",
         L.route_from_sourcer_name("mystery"), "other")
check_eq("picture pass route A",
         L.route_from_picture_pass("A — Wikimedia Commons"),
         "wikimedia")
check_eq("picture pass route B",
         L.route_from_picture_pass("B — official sources"), "official")
check_eq("picture pass person cache",
         L.route_from_picture_pass("person_images cache"),
         "person_profile")
check_eq("URL wikimedia", L.route_for_url(_FORMS[0]), "wikimedia")
check_eq("URL youtube thumb",
         L.route_for_url("https://img.youtube.com/vi/abc123/maxres.jpg"),
         "youtube_thumb")
check_eq("URL pexels",
         L.route_for_url("https://images.pexels.com/photos/1/x.jpg"),
         "pexels")
check_eq("URL other", L.route_for_url("https://cdn.example.com/a.jpg"),
         "other")

print("rights derivation")
check_eq("CC BY-SA string → verified-license",
         L.rights_status("wikimedia", "CC BY-SA 4.0"), "verified-license")
check_eq("CC0 string → public-domain",
         L.rights_status("wikimedia", "CC0 1.0"), "public-domain")
check_eq("public domain in attribution",
         L.rights_status("other", None, "Public domain, NASA"),
         "public-domain")
check_eq("pexels route → verified-license",
         L.rights_status("pexels"), "verified-license")
check_eq("person_profile route → official",
         L.rights_status("person_profile"), "official")
check_eq("source_og, no license evidence → unknown",
         L.rights_status("source_og", None, "Some Outlet"), "unknown")
check_eq("wikimedia with no license string → unknown (not assumed)",
         L.rights_status("wikimedia", None, "Wikimedia Commons"),
         "unknown")


# ── intent population ─────────────────────────────────────────────
print("intent columns")
intent = L.intent_columns(ARTICLE)
check("entities populated", bool(intent.get("image_entities")))
check("writer's sane image_entities entry kept",
      "Reserve Bank of India" in (intent.get("image_entities") or []))
check("must_show populated from subjects",
      bool(intent.get("image_must_show"))
      and "Must show:" in intent["image_must_show"])
check("search query populated",
      bool(intent.get("image_search_query")))

writer = {**ARTICLE,
          "image_entities": ["Writer Picked Entity"],
          "image_must_show": "Writer Picked Entity at the podium",
          "image_search_query": "writer query"}
wintent = L.intent_columns(writer)
check("writer image_entities entry kept",
      "Writer Picked Entity" in (wintent.get("image_entities") or []))
check_eq("writer must_show wins verbatim",
         wintent.get("image_must_show"),
         "Writer Picked Entity at the podium")
check_eq("writer search query wins verbatim",
         wintent.get("image_search_query"), "writer query")
check_eq("empty article → no invented intent",
         L.intent_columns({}), {})
check_eq("non-dict → {}", L.intent_columns(None), {})


# ── JSONL ledger writes ───────────────────────────────────────────
print("ledger writes (no DB creds in env — sync must stay silent)")
rec = L.record_provenance(
    article_id="art-1", slug=ARTICLE["slug"], surface="hero",
    producer="test", source_route="wikimedia",
    image_url=_FORMS[0], license_text="CC BY-SA 4.0",
    attribution="By A Photographer, CC BY-SA 4.0",
    entity="Reserve Bank of India")
check("placement record returned", rec is not None)
check_eq("record route", rec["source_route"], "wikimedia")
check_eq("record rights derived", rec["rights_status"],
         "verified-license")
check_eq("record file_key canonical", rec["file_key"],
         "reserve bank of india building.jpg")
check_eq("original defaults to placed URL",
         rec["original_file_url"], _FORMS[0])

rm = L.record_removal(article_id="art-1", slug=ARTICLE["slug"],
                      surface="hero", removed_url=_FORMS[0],
                      producer="reviewer", reason="wrong venue")
check("removal record returned", rm is not None)
check_eq("removal action", rm["action"], "removed")

records = L.read_ledger(article_id="art-1")
check_eq("both events in the ledger", len(records), 2)
folded = L.current_with_history(records)
check_eq("current state is the removal", folded["action"], "removed")
check_eq("history preserves the placement",
         [h["action"] for h in folded["history"]], ["placed"])
check_eq("no records for unknown article",
         L.read_ledger(article_id="nope"), [])
bad = L.record_provenance(article_id="art-1", source_route="bogus")
check_eq("invalid route normalized to other",
         bad["source_route"], "other")
auto = L.record_provenance(article_id="art-2", source_route="wikimedia",
                           image_url=_FORMS[1])
check_eq("wikimedia source page auto-derived when not supplied",
         auto["source_page_url"],
         "https://commons.wikimedia.org/wiki/File:"
         "reserve_bank_of_india_building.jpg")


# ── picture pass: ledger on --apply only ─────────────────────────
print("picture pass ledger wiring")
import article_picture_pass as PP


def commons_page(title, w, h, license_short="CC BY-SA 4.0",
                 desc="", cats="", artist="A Photographer"):
    info = {
        "url": "https://upload.wikimedia.org/wikipedia/commons/"
               + title.replace("File:", "").replace(" ", "_"),
        "width": w, "height": h, "mime": "image/jpeg",
        "descriptionurl": "https://commons.wikimedia.org/wiki/"
                          + title.replace(" ", "_"),
        "extmetadata": {
            "LicenseShortName": {"value": license_short},
            "UsageTerms": {"value": license_short},
            "ImageDescription": {"value": desc},
            "Categories": {"value": cats},
            "Artist": {"value": artist},
        },
    }
    return {"title": title, "imageinfo": [info]}


RBI_PAGE = commons_page(
    "File:Reserve Bank of India headquarters Mumbai.jpg", 3200, 2000,
    desc="The headquarters of the Reserve Bank of India in Mumbai, "
         "home of the Bank's first data centre.",
    cats="Reserve Bank of India|Buildings in Mumbai")


def stub_net(pages_by_query=None):
    pages_by_query = pages_by_query or {}
    calls = {"patch": []}

    def commons_search(q, limit=10):
        for key, pages in pages_by_query.items():
            if key.lower() in q.lower():
                return pages
        return []

    net = {
        "commons_search": commons_search,
        "commons_file_info": lambda title: None,
        "brave_links": lambda q, n=8: [],
        "fetch_text": lambda url, timeout=15: "",
        "verify_url": lambda url: {"ok": True, "width": 2400},
        "person_cache": lambda name: None,
        "download_verify": lambda url, dest: [2400, 1500],
    }
    return net, calls


def recording_patch(calls):
    def _patch(article_id, payload):
        calls["patch"].append((article_id, payload))
        return True
    return _patch


LEDGER.write_text("", encoding="utf-8")  # reset: art-1 events above
net, calls = stub_net({"Reserve Bank of India": [RBI_PAGE]})
rec_dry = PP.process_article(ARTICLE, net=net, apply=False,
                             patch_fn=recording_patch(calls),
                             log=lambda *a: None)
check_eq("dry-run: zero ledger events",
         len(L.read_ledger(article_id="art-1")), 0)

net, calls = stub_net({"Reserve Bank of India": [RBI_PAGE]})
rec_app = PP.process_article(ARTICLE, net=net, apply=True,
                             patch_fn=recording_patch(calls),
                             log=lambda *a: None)
check("apply run applied the hero", "hero" in rec_app["applied"])
events = L.read_ledger(article_id="art-1")
heroes = [e for e in events
          if e["surface"] == "hero" and e["action"] == "placed"]
check_eq("apply run: exactly one hero placement recorded",
         len(heroes), 1)
if heroes:
    h = heroes[0]
    check_eq("hero record producer", h["producer"],
             "article_picture_pass")
    check_eq("hero record route", h["source_route"], "wikimedia")
    check_eq("hero record rights from the file's license",
             h["rights_status"], "verified-license")
    check_eq("hero record license kept", h["license"], "CC BY-SA 4.0")
    check_eq("hero record entity", h["entity"], "Reserve Bank of India")
    check("hero record source page is the Commons file page",
          (h["source_page_url"] or "").startswith(
              "https://commons.wikimedia.org/wiki/File:"))
    check("hero record file_key canonical",
          h["file_key"] == "reserve bank of india headquarters "
          "mumbai.jpg")


# ── insert choke point, end to end with a stubbed curl ───────────
print("v3-insert-article choke point (stubbed curl)")
bindir = Path(_TMP) / "bin"
bindir.mkdir(exist_ok=True)
capture = Path(_TMP) / "curl-args.txt"
shim = bindir / "curl"
shim.write_text(
    "#!/bin/sh\n"
    f'printf "%s\\n" "$@" >> "{capture}"\n'
    'case " $* " in\n'
    '  *" POST "*p2_articles*) echo \'[{"id":"proof-id-1"}]\' ;;\n'
    '  *) echo \'[]\' ;;\n'
    "esac\n", encoding="utf-8")
shim.chmod(0o755)
art_json = Path(_TMP) / "article.json"
art_json.write_text(json.dumps({
    **ARTICLE, "id": None,
    "subheadline": "A new facility in Bhubaneswar",
    "sources": [{"name": "Reuters", "url": "https://reuters.com/x"},
                {"name": "PIB", "url": "https://pib.gov.in/y"}],
    "image_url": "https://img.youtube.com/vi/abc123xyz00/maxres.jpg",
    "image_attribution": "YouTube",
    "word_count": 400,
}), encoding="utf-8")
LEDGER.write_text("", encoding="utf-8")
env = dict(os.environ)
env["PATH"] = f"{bindir}:{env.get('PATH', '')}"
env["SUPABASE_URL"] = "https://example.supabase.co"
env["SUPABASE_SERVICE_ROLE_KEY"] = "test-key"
env["IMAGE_LEDGER_PATH"] = str(LEDGER)
r = subprocess.run(
    [sys.executable, str(Path(PP.__file__).parent
                         / "v3-insert-article.py"), str(art_json)],
    capture_output=True, text=True, env=env, timeout=120)
check_eq("insert script exits 0", r.returncode, 0)
captured = capture.read_text(encoding="utf-8") \
    if capture.exists() else ""
check("POST body carried populated image_entities",
      '"image_entities"' in captured and "Reserve Bank of India"
      in captured)
check("POST body carried populated image_must_show",
      '"image_must_show"' in captured and "Must show:" in captured)
placed = L.read_ledger(article_id="proof-id-1")
check_eq("writer hero placement recorded at insert",
         len(placed), 1)
if placed:
    check_eq("insert placement route from URL",
             placed[0]["source_route"], "youtube_thumb")
    check_eq("insert placement producer", placed[0]["producer"],
             "v3-insert-article")

for k, v in _SAVED_ENV.items():
    if v is not None:
        os.environ[k] = v

print()
if FAILS:
    print(f"❌ {len(FAILS)} FAILURES: {FAILS}")
    sys.exit(1)
print("✅ all image ledger tests passed")
