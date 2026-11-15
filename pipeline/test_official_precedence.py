"""Tests: official/brand precedence over low-trust og:image
(2026-11-15) + the health check's reader-view probe wiring.

Keeper case: the Air India non-stop restoration article shipped
with a hero hotlinked from safariindia.com (a travel-trade blog)
although airindia.com is in the brand map — resolution points let
the hotlink outscore the official candidate. _apply_official_
precedence must drop low-trust og:image candidates whenever an
official/brand candidate exists, and must leave og:image from a
preferred news domain in competition.

The reader-view probe in videshi-health.py (browser UA +
thevideshi.com referer) exists because the Hina Khan hero passed
every bare health check while India Forums 403'd real readers;
here we only assert the check is wired into the image_health
result (the live run exercises the probe itself).

Run: python3 test_official_precedence.py  (exit 0 = all pass)
"""
import os
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sourcer = SourceFileLoader("image_sourcer", str(HERE / "image_sourcer.py")).load_module()

fails = 0
total = 0


def check(name, cond):
    global fails, total
    total += 1
    if cond:
        print(f"  ok {total}: {name}")
    else:
        fails += 1
        print(f"  FAIL {total}: {name}")


def cand(source, attribution):
    return {"img_url": f"https://{attribution}/img.jpg",
            "attribution": attribution, "source_name": source,
            "upload_date": None}


# 1. The keeper: brand candidate + trade-blog og:image -> og dropped.
out = sourcer._apply_official_precedence([
    cand("og:image", "safariindia.com"),
    cand("brand_official", "Air India"),
])
check("trade-blog og:image dropped when brand candidate exists",
      [c["source_name"] for c in out] == ["brand_official"])

# 2. og:image from a preferred news domain keeps competing.
out = sourcer._apply_official_precedence([
    cand("og:image", "thehindu.com"),
    cand("brand_official", "Air India"),
])
check("preferred-domain og:image kept", len(out) == 2)

# 3. No official candidate -> list unchanged.
orig = [cand("og:image", "safariindia.com"),
        cand("commons_search", "Wikimedia Commons")]
check("no official candidate -> unchanged",
      sourcer._apply_official_precedence(orig) == orig)

# 4. official_source triggers the same precedence.
out = sourcer._apply_official_precedence([
    cand("og:image", "apnamatvchannel.com"),
    cand("official_source", "Government of India"),
    cand("commons_search", "Wikimedia Commons"),
])
check("official_source drops low-trust og:image, keeps Commons",
      [c["source_name"] for c in out]
      == ["official_source", "commons_search"])

# 5. Health check exposes the reader-blocked result field.
health_src = (HERE / "videshi-health.py").read_text()
check("health check has reader-view probe",
      "reader_blocked" in health_src
      and "thevideshi.com/" in health_src
      and "reader_blocked_images" in health_src)

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
