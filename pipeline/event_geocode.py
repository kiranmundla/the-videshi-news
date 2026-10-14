#!/usr/bin/env python3
"""event_geocode.py — shared venue geocoding for events ingestion.

Extracted from events-maintenance.py Step 3 (its proven implementation) so
the temple and spiritual scrapers can geocode at insert time instead of
leaving latitude/longitude NULL — coord-less events are invisible to the
site's ZIP / near-me radius search.

Behaviour:
- Nominatim (OpenStreetMap) via curl subprocess (requests hangs through
  this host's proxy), User-Agent "TheVideshi/1.0 (events geocoder)".
- Three tiers: venue query ("<venue>, <city>, <state>, <country>") first,
  then a city fallback ("<city>, <state>, <country>"). City-level coords
  are enough for radius search. The tier is returned so callers can log it.
- Final tier, only when the venue name itself carries a place anchor
  (", " or " of ", e.g. "ISKCON - Atlanta, Georgia" — many temple-directory
  entries have empty city/state with the place only in the name): query the
  raw venue name constrained to the US (every source feeding this helper
  is a US-events pipeline). The anchor requirement keeps generic names
  ("General Zoom Room") from resolving to a random same-named place, and
  the US constraint prevents wrong-continent matches — an unconstrained
  "ISKCON Atlanta" resolves to Surat, India.
- Country is inferred from the state/province code (US/CA/UK) instead of
  always assuming USA; unknown states fall back to an unconstrained query.
- Results are cached per process on (venue, city, state) — ingestion runs
  insert many events per venue, so each unique venue costs one lookup.
- Network calls are rate-limited to ~1/sec (Nominatim usage policy).
- A failed geocode returns (None, None, None). Coords are never invented;
  the event keeps NULL latitude/longitude and the caller logs it.
"""

import json
import subprocess
import time
from urllib.parse import urlencode

_UA = "TheVideshi/1.0 (events geocoder)"
_MIN_INTERVAL = 1.05  # seconds between Nominatim calls
_cache = {}
_last_call = [0.0]

_US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
    "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
    "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
    "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
    "WV", "WI", "WY",
}
_CA_PROVINCES = {"AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE",
                 "QC", "SK", "YT"}
_UK_REGIONS = {"EN", "SCT", "WLS", "NIR"}


def _country_for_state(state):
    s = (state or "").strip().upper()
    if s in _US_STATES:
        return "USA", "us"
    if s in _CA_PROVINCES:
        return "Canada", "ca"
    if s in _UK_REGIONS:
        return "United Kingdom", "gb"
    return "", ""


def _curl_nominatim(query, countrycodes=None):
    """Single Nominatim lookup via curl. Returns (lat, lon) or (None, None)."""
    wait = _MIN_INTERVAL - (time.time() - _last_call[0])
    if wait > 0:
        time.sleep(wait)
    q = {"q": query, "format": "json", "limit": 1}
    if countrycodes:
        q["countrycodes"] = countrycodes
    url = f"https://nominatim.openstreetmap.org/search?{urlencode(q)}"
    cmd = ["curl", "-s", "-w", "\n%{http_code}", url,
           "-H", f"User-Agent: {_UA}", "--max-time", "10"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    except Exception:
        return None, None
    finally:
        _last_call[0] = time.time()
    output = result.stdout.strip()
    lines = output.rsplit("\n", 1)
    body = lines[0] if len(lines) > 1 else ""
    status = int(lines[-1]) if lines and lines[-1].isdigit() else 0
    if status == 200 and body:
        try:
            results = json.loads(body)
        except json.JSONDecodeError:
            return None, None
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    return None, None


def geocode_venue(venue, city, state=""):
    """Geocode a venue.

    Returns (lat, lon, level) where level is "venue" (the venue query hit),
    "city" (only the city fallback hit), or None when both failed — in
    which case lat/lon are None and the caller must leave coords unset.
    """
    venue = (venue or "").strip()
    city = (city or "").strip()
    state = (state or "").strip()
    if not city and not venue:
        return None, None, None
    key = (venue.lower(), city.lower(), state.lower())
    if key in _cache:
        return _cache[key]

    country, cc = _country_for_state(state)
    cc = cc or None

    def _q(*parts):
        return ", ".join(p for p in parts if p)

    result = (None, None, None)
    if venue and city:
        lat, lon = _curl_nominatim(_q(venue, city, state, country), cc)
        if lat is not None:
            result = (lat, lon, "venue")
    if result[0] is None and city:
        lat, lon = _curl_nominatim(_q(city, state, country), cc)
        if lat is not None:
            result = (lat, lon, "city")
    if result[0] is None and venue and (", " in venue or " of " in venue):
        # Place anchored in the venue name itself (city/state fields empty).
        lat, lon = _curl_nominatim(venue, "us")
        if lat is not None:
            result = (lat, lon, "venue")
    _cache[key] = result
    return result
