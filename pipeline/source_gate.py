#!/usr/bin/env python3
"""≥2-source publish gate — shared by every article insert path.

Kiran's rule (approved 2026-10-14): EVERY new article must carry at least
2 legitimate sources before it may be published. Prompted by audits that
found 12 articles published Oct 8-12 with a single source (bypassing the
2026-06-25 food-writer assertion, which covered one producer only) and
30 of the latest 400 articles carrying exactly 1 source.

A source counts only if it is REAL:
  - a dict {"name": ..., "url": ...} with a non-empty name and an
    http(s) URL, or a bare http(s) URL string (legacy format used by
    movie-reviews.py / batch writers);
  - the URL must point at a specific page — a bare root-domain homepage
    (https://www.reuters.com/) is not a source. A root URL on a
    dedicated subdomain (https://investor.apple.com/,
    https://ir.tesla.com/) DOES count: that subdomain root is itself
    the specific destination (a company's investor-relations page),
    and the earnings gate has relied on those verified IR URLs since
    2026-10-13;
  - sources are deduplicated by normalized URL: the same page listed
    twice is still ONE source.

Failure semantics at every choke point: HOLD the article (do not insert
it as published; per-path conventions decide draft/skip), log loudly.
NEVER pad with fabricated or irrelevant sources to satisfy the count —
producers must supply 2 legitimate sources or the article does not run.

Prospective only: already-published articles are never touched here.
"""
import json
from urllib.parse import urlparse

MIN_SOURCES = 2


class SourceGateError(Exception):
    """Raised when an article fails the ≥2-source publish gate."""


def _normalize_url(url):
    """Canonical form for dedupe: lowercase scheme/host, no trailing
    slash on the path, no fragment. Query string is significant."""
    try:
        p = urlparse(url.strip())
    except Exception:
        return url.strip().lower()
    path = p.path.rstrip("/")
    out = f"{p.scheme.lower()}://{p.netloc.lower()}{path}"
    if p.query:
        out += f"?{p.query}"
    return out


def _is_bare_domain(url):
    """True for generic homepage URLs (no path, no query, root domain) —
    not a real source. Root URLs on a dedicated subdomain (investor.*,
    ir.*) are specific destinations and are NOT bare (see module doc)."""
    try:
        p = urlparse(url.strip())
    except Exception:
        return True
    if p.path not in ("", "/") or p.query:
        return False
    host = p.netloc.lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    return len(host.split(".")) <= 2


def valid_sources(sources):
    """Return the list of sources that count toward the gate, normalized
    to {"name", "url"} dicts and deduplicated by URL.

    Accepts the formats the corpus actually uses: a list of dicts, a list
    of bare URL strings, a mixed list, or a JSON string encoding any of
    those (breaking-detector / worldcup-recap store sources json.dumps'd).
    """
    if sources is None:
        return []
    if isinstance(sources, str):
        text = sources.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            parsed = text  # a single bare URL string
        return valid_sources(parsed)
    if isinstance(sources, dict):
        sources = [sources]
    if not isinstance(sources, (list, tuple)):
        return []

    out, seen = [], set()
    for entry in sources:
        name, url = "", ""
        if isinstance(entry, dict):
            name = (entry.get("name") or "").strip()
            url = (entry.get("url") or "").strip()
            if not url and name.startswith("http"):
                # normalize_sources() fallback shape: the URL landed in name
                url, name = name, ""
        elif isinstance(entry, str):
            url = entry.strip()
        if not url.startswith(("http://", "https://")):
            continue
        if _is_bare_domain(url):
            continue
        key = _normalize_url(url)
        if key in seen:
            continue
        seen.add(key)
        out.append({"name": name or url, "url": url})
    return out


def count_valid(sources):
    return len(valid_sources(sources))


def gate_failure(sources):
    """None if the article passes the gate, else a human-readable reason."""
    valid = valid_sources(sources)
    if len(valid) >= MIN_SOURCES:
        return None
    return (f"only {len(valid)} valid source(s), need >={MIN_SOURCES} "
            f"(distinct http(s) page URLs with names; bare homepages "
            f"and duplicates don't count)")


def assert_publishable(sources, context="article"):
    """Raise SourceGateError if `sources` fails the gate; else return the
    normalized valid-source list (handy for storing a clean sources[])."""
    reason = gate_failure(sources)
    if reason is not None:
        raise SourceGateError(f"≥2-source gate HOLD for {context}: {reason}")
    return valid_sources(sources)
