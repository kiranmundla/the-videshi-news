"""Regression tests: temple identity in source_id / slug / fingerprint.

2026-11-09 weekly sweep: 241 new temple-event candidates, 240 failed
with 409 slug conflicts, 1 inserted. Cause: identity built from
festival+date+city only — two temples in the same city running the
same festival on the same date collided on source_id, slug, and (in
scrape-temples.py) the dedupe fingerprint. Every construction site
must include the temple itself. Run: python3 -u test_temple_identity.py
"""
import importlib.util
import os
import sys

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, fname):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tes = load("temple_events_scraper", "temple-events-scraper.py")
st = load("scrape_temples", "scrape-temples.py")

FAIL = []


def check(label, cond):
    print(("  ok " if cond else "  FAIL ") + label)
    if not cond:
        FAIL.append(label)


TEMPLE_A = {"name": "Sri Guruvayurappan Temple", "city": "Houston",
            "state": "TX", "events_url": "https://a.example/events",
            "website": "https://a.example"}
TEMPLE_B = {"name": "Jalaram Mandir", "city": "Houston",
            "state": "TX", "events_url": "https://b.example/events",
            "website": "https://b.example"}

JSONLD = """
<html><head><script type="application/ld+json">
{"@type": "Event", "name": "Diwali Celebration",
 "startDate": "2026-11-08T18:00:00",
 "location": {"name": "Main Hall", "address": {"addressLocality": "Houston"}},
 "url": "https://x.example/diwali"}
</script></head><body></body></html>
"""

print("temple-events-scraper: JSON-LD path")
ea = tes.parse_json_ld_events(JSONLD, TEMPLE_A)
eb = tes.parse_json_ld_events(JSONLD, TEMPLE_B)
check("both temples parse 1 event", len(ea) == 1 and len(eb) == 1)
check("source_id distinct across temples", ea[0]["source_id"] != eb[0]["source_id"])
check("slug distinct across temples", ea[0]["slug"] != eb[0]["slug"])
ea2 = tes.parse_json_ld_events(JSONLD, TEMPLE_A)
check("same temple -> stable source_id", ea[0]["source_id"] == ea2[0]["source_id"])
check("same temple -> stable slug", ea[0]["slug"] == ea2[0]["slug"])

print("temple-events-scraper: static HTML path")
HTML = ('<html><body><h3>Grand Diwali Celebration Night</h3>'
        '<p>Join us on November 8, 2026 for the festival.</p></body></html>')
sa = tes.parse_static_html_events(HTML, TEMPLE_A)
sb = tes.parse_static_html_events(HTML, TEMPLE_B)
check("both temples parse >=1 event", len(sa) >= 1 and len(sb) >= 1)
if sa and sb:
    check("static source_id distinct", sa[0]["source_id"] != sb[0]["source_id"])
    check("static slug distinct", sa[0]["slug"] != sb[0]["slug"])

print("scrape-temples: identity helpers")
row_a = {"name": "Sri Guruvayurappan Temple", "url": "https://a.example"}
row_b = {"name": "Jalaram Mandir", "url": "https://b.example"}
check("temple_key distinct", st.temple_key(row_a) != st.temple_key(row_b))
check("temple_key stable", st.temple_key(row_a) == st.temple_key(dict(row_a)))
sa_ = st.make_slug("Diwali Celebration", "Houston", "2026-11-08", row_a["name"])
sb_ = st.make_slug("Diwali Celebration", "Houston", "2026-11-08", row_b["name"])
check("make_slug distinct across temples", sa_ != sb_)
fa = st.content_fingerprint("Diwali Celebration", "2026-11-08", "Houston", row_a["name"])
fb = st.content_fingerprint("Diwali Celebration", "2026-11-08", "Houston", row_b["name"])
check("fingerprint distinct across temples", fa != fb)
fa2 = st.content_fingerprint("Diwali Celebration", "2026-11-08", "Houston", row_a["name"])
check("fingerprint stable for same temple", fa == fa2)

print(f"\n{'ALL PASS' if not FAIL else 'FAILURES: ' + str(FAIL)}")
sys.exit(1 if FAIL else 0)
