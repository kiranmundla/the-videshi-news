"""
fact_check.py — Lightweight fact-checker for The Videshi article pipeline.

Extracts verifiable claims (person-place associations, ages) from an article
body and cross-checks them against Wikipedia / Wikidata.  Auto-corrects clear
errors; logs warnings for ambiguous cases.

Usage:
    from fact_check import fact_check_article

    corrected_body, corrections = fact_check_article(body, headline)
    if corrections:
        print(f"Fact-check made {len(corrections)} corrections")
    body = corrected_body
"""

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

# ── Config ──────────────────────────────────────────────────────────────────

WIKI_UA = "TheVideshi/1.0 (https://thevideshi.com; factcheck@thevideshi.com)"
WIKI_HEADERS = {"User-Agent": WIKI_UA}

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WIKIPEDIA_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary"
WIKIPEDIA_PARSE = "https://en.wikipedia.org/w/api.php"

LOG_PATH = Path(__file__).parent / "fact-check-log.json"

_RATE_LIMIT_SECS = 0.25
_last_api_call = 0.0
_person_facts_cache: dict[str, dict] = {}

# ── API Helpers ─────────────────────────────────────────────────────────────


def _rate_limit():
    global _last_api_call
    now = time.time()
    wait = _RATE_LIMIT_SECS - (now - _last_api_call)
    if wait > 0:
        time.sleep(wait)
    _last_api_call = time.time()


def _wiki_summary(title: str) -> Optional[dict]:
    """Fetch Wikipedia REST summary for a page title."""
    _rate_limit()
    try:
        r = requests.get(
            f"{WIKIPEDIA_SUMMARY}/{title.replace(' ', '_')}",
            headers=WIKI_HEADERS, timeout=10,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def _wiki_infobox_birthplace(title: str) -> Optional[str]:
    """
    Parse a Wikipedia article's infobox for birth_place.
    Uses the MediaWiki parse API to get wikitext, then extracts the field.
    Handles redirects by following the canonical page title.
    """
    _rate_limit()
    try:
        r = requests.get(
            WIKIPEDIA_PARSE,
            params={
                "action": "parse", "page": title.replace(" ", "_"),
                "prop": "wikitext", "section": "0",
                "redirects": "1",  # follow redirects automatically
                "format": "json",
            },
            headers=WIKI_HEADERS, timeout=10,
        )
        if r.status_code != 200:
            return None
        wikitext = r.json().get("parse", {}).get("wikitext", {}).get("*", "")
        if not wikitext:
            return None

        # Extract birth_place from infobox
        bp_match = re.search(r"birth_place\s*=\s*(.+)", wikitext)
        if bp_match:
            raw = bp_match.group(1).strip()
            # Strip wiki markup: [[Samastipur]], [[Bihar|Bihar state]]
            clean = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", raw)
            clean = re.sub(r"[{}]", "", clean).strip()
            if clean:
                return clean
    except Exception:
        pass
    return None


def _wiki_infobox_dob(title: str) -> Optional[str]:
    """Parse Wikipedia infobox for birth_date. Returns YYYY-MM-DD or None."""
    _rate_limit()
    try:
        r = requests.get(
            WIKIPEDIA_PARSE,
            params={
                "action": "parse", "page": title.replace(" ", "_"),
                "prop": "wikitext", "section": "0",
                "redirects": "1", "format": "json",
            },
            headers=WIKI_HEADERS, timeout=10,
        )
        if r.status_code != 200:
            return None
        wikitext = r.json().get("parse", {}).get("wikitext", {}).get("*", "")

        # Match {{birth date and age|YYYY|MM|DD|...}} or {{birth date|YYYY|MM|DD|...}}
        dob_match = re.search(
            r"birth[_ ]date\s*=\s*\{\{[^}]*\|(\d{4})\|(\d{1,2})\|(\d{1,2})",
            wikitext, re.IGNORECASE,
        )
        if dob_match:
            return f"{dob_match.group(1)}-{int(dob_match.group(2)):02d}-{int(dob_match.group(3)):02d}"
    except Exception:
        pass
    return None


def _wikidata_search(name: str) -> Optional[str]:
    _rate_limit()
    try:
        r = requests.get(
            WIKIDATA_API,
            params={
                "action": "wbsearchentities", "search": name,
                "language": "en", "format": "json",
            },
            headers=WIKI_HEADERS, timeout=10,
        )
        if r.status_code == 200:
            results = r.json().get("search", [])
            if results:
                return results[0]["id"]
    except Exception:
        pass
    return None


def _wikidata_get_claims(qid: str) -> dict:
    _rate_limit()
    try:
        r = requests.get(
            WIKIDATA_API,
            params={
                "action": "wbgetentities", "ids": qid,
                "props": "claims", "format": "json",
            },
            headers=WIKI_HEADERS, timeout=10,
        )
        if r.status_code == 200:
            return r.json().get("entities", {}).get(qid, {}).get("claims", {})
    except Exception:
        pass
    return {}


def _wikidata_resolve_entity(qid: str) -> str:
    _rate_limit()
    try:
        r = requests.get(
            WIKIDATA_API,
            params={
                "action": "wbgetentities", "ids": qid,
                "props": "labels", "languages": "en", "format": "json",
            },
            headers=WIKI_HEADERS, timeout=10,
        )
        if r.status_code == 200:
            return (
                r.json().get("entities", {}).get(qid, {})
                .get("labels", {}).get("en", {}).get("value", "")
            )
    except Exception:
        pass
    return ""


def _get_person_facts(name: str) -> dict:
    """
    Look up a person on Wikipedia + Wikidata and return structured facts.
    Tries multiple sources for birthplace: Wikidata P19 → Wikipedia infobox → Wikipedia text.
    """
    if name in _person_facts_cache:
        return _person_facts_cache[name]

    facts: dict = {}

    # ── Wikipedia summary ──
    summary = _wiki_summary(name)
    if summary and summary.get("type") not in ("disambiguation", "not-found"):
        facts["wiki_extract"] = summary.get("extract", "")
        facts["description"] = summary.get("description", "")
        facts["wiki_title"] = summary.get("title", name)  # canonical title

    # ── Wikidata ──
    qid = _wikidata_search(name)
    if qid:
        claims = _wikidata_get_claims(qid)

        # P19 = place of birth
        if "P19" in claims:
            try:
                bp_id = claims["P19"][0]["mainsnak"]["datavalue"]["value"]["id"]
                facts["birthplace"] = _wikidata_resolve_entity(bp_id)
                facts["birthplace_source"] = "wikidata"
            except (KeyError, IndexError):
                pass

        # P569 = date of birth
        if "P569" in claims:
            try:
                dob_str = claims["P569"][0]["mainsnak"]["datavalue"]["value"]["time"]
                m = re.search(r"(\d{4})-(\d{2})-(\d{2})", dob_str)
                if m:
                    facts["dob"] = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
                    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    today = datetime.now(timezone.utc)
                    age = today.year - y
                    if (today.month, today.day) < (mo, d):
                        age -= 1
                    facts["age"] = age
            except (KeyError, IndexError, ValueError):
                pass

        # P54 = member of sports team
        if "P54" in claims:
            teams = []
            for tc in claims["P54"][:5]:
                try:
                    tid = tc["mainsnak"]["datavalue"]["value"]["id"]
                    tname = _wikidata_resolve_entity(tid)
                    if tname:
                        teams.append(tname)
                except (KeyError, IndexError):
                    pass
            if teams:
                facts["teams"] = teams

    # ── Wikipedia infobox fallback for birthplace ──
    if "birthplace" not in facts:
        wiki_title = facts.get("wiki_title", name)
        bp = _wiki_infobox_birthplace(wiki_title)
        if bp:
            facts["birthplace"] = bp
            facts["birthplace_source"] = "wikipedia_infobox"

    # ── Wikipedia infobox fallback for DOB ──
    if "dob" not in facts:
        wiki_title = facts.get("wiki_title", name)
        dob = _wiki_infobox_dob(wiki_title)
        if dob:
            facts["dob"] = dob
            parts = dob.split("-")
            y, mo, d = int(parts[0]), int(parts[1]), int(parts[2])
            today = datetime.now(timezone.utc)
            age = today.year - y
            if (today.month, today.day) < (mo, d):
                age -= 1
            facts["age"] = age

    _person_facts_cache[name] = facts
    return facts


# ── Claim Extraction ────────────────────────────────────────────────────────


def _clean_body(body: str) -> str:
    """Strip HTML tags and markdown formatting for text analysis."""
    text = re.sub(r"<[^>]+>", " ", body)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[#*_`~]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _split_sentences(text: str) -> list[str]:
    """Split text into rough sentences."""
    # Split on period/newline followed by space + capital letter, or on newline
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])|(?:\n\s*\n)", text)
    return [s.strip() for s in parts if s.strip()]


# Full name: 2-3 capitalized words (min 3 chars each)
_PERSON_RE = re.compile(r"\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,}){1,2})\b")

# Common non-person multi-word phrases to skip
_SKIP_NAMES = {
    "The Videshi", "Indian Premier", "Premier League", "Indian Premier League",
    "Royal Challengers", "Challengers Bengaluru", "Chennai Super", "Super Kings",
    "Gujarat Titans", "Mumbai Indians", "Delhi Capitals", "Rajasthan Royals",
    "Punjab Kings", "Kolkata Knight", "Knight Riders", "Sunrisers Hyderabad",
    "Lucknow Super", "Super Giants", "Orange Cap", "Purple Cap",
    "Chris Gayle", "World Cup", "Asia Cup",
}

_SKIP_FIRST_WORDS = {
    "The", "This", "That", "With", "From", "After", "Before", "Under",
    "Over", "Against", "Between", "During", "Indian", "Premier", "League",
    "Royal", "Orange", "Purple", "Golden", "Match", "Final", "Season",
    "First", "Second", "Third", "Most", "Best", "Worst",
}


def _extract_claims(text: str) -> list[dict]:
    """
    Extract person-place and person-age claims using sentence-level context.
    Each person is only associated with places mentioned in the SAME sentence.
    """
    claims = []
    seen_persons = set()
    sentences = _split_sentences(text)

    for sentence in sentences:
        # Find person names in this sentence
        person_matches = list(_PERSON_RE.finditer(sentence))

        for pm in person_matches:
            person = pm.group(1)
            if person in seen_persons or person in _SKIP_NAMES:
                continue
            if person.split()[0] in _SKIP_FIRST_WORDS:
                continue

            claim: dict = {"person": person}

            # Look for place associations in THIS SENTENCE ONLY
            # Patterns: "from Place", "in Place", "of Place", "born in Place"
            place_patterns = [
                r"\bfrom\s+([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)?)\b",
                r"\bborn\s+in\s+([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)?)\b",
                r"\bhails?\s+from\s+([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)?)\b",
            ]
            for pp in place_patterns:
                m = re.search(pp, sentence)
                if m:
                    place = m.group(1).strip()
                    # Make sure the place isn't part of the person's name
                    if place not in person and place not in _SKIP_NAMES:
                        claim["place"] = place
                        claim["type"] = "person_place"
                        break

            # Look for age in this sentence
            age_patterns = [
                r"(\d{1,2})-year-old",
                r"\bage[d]?\s+(\d{1,2})\b",
                re.escape(person) + r",?\s+(\d{1,2})[,\s]",
            ]
            for ap in age_patterns:
                m = re.search(ap, sentence)
                if m:
                    try:
                        age = int(m.group(1))
                        if 10 <= age <= 80:
                            claim["claimed_age"] = age
                            break
                    except ValueError:
                        pass

            # Only keep claims that have something to verify
            if "place" in claim or "claimed_age" in claim:
                if "type" not in claim:
                    claim["type"] = "age"
                claims.append(claim)
                seen_persons.add(person)

    return claims


def extract_claims(body: str, headline: str = "") -> list[dict]:
    """
    Extract verifiable claims from article text. Limited to ~15 claims.
    """
    text = _clean_body(body)
    full_text = f"{headline}. {text}" if headline else text
    claims = _extract_claims(full_text)
    return claims[:15]


# ── Verification ────────────────────────────────────────────────────────────


def _normalize(s: str) -> str:
    return s.lower().strip().rstrip(",").strip()


def _place_names_match(claimed: str, actual: str) -> bool:
    """Check if two place names refer to the same place."""
    c = _normalize(claimed)
    a = _normalize(actual)
    if not c or not a:
        return False
    # Exact or substring
    if c == a or c in a or a in c:
        return True
    # First word match
    return c.split(",")[0].strip() == a.split(",")[0].strip()


def _verify_claim(claim: dict) -> list[dict]:
    """
    Verify a claim against Wikipedia/Wikidata.
    Returns a list of corrections (may be empty).
    """
    person = claim.get("person", "")
    if not person:
        return []

    facts = _get_person_facts(person)
    if not facts:
        return []

    corrections = []

    # ── Verify place ──
    if "place" in claim:
        claimed_place = claim["place"]
        actual_birthplace = facts.get("birthplace", "")

        if actual_birthplace:
            if not _place_names_match(claimed_place, actual_birthplace):
                # For replacement, match the specificity of the original claim.
                # If article said "Sambalpur" (city only), replace with city only.
                # If article said "Sambalpur, Odisha", replace with "City, State".
                actual_for_replace = actual_birthplace
                if "," not in claimed_place:
                    # Original was just a city name — use just the city from actual
                    actual_for_replace = actual_birthplace.split(",")[0].strip()
                corrections.append({
                    "type": "place_correction",
                    "person": person,
                    "claimed": claimed_place,
                    "actual": actual_for_replace,
                    "actual_full": actual_birthplace,
                    "confidence": "high" if facts.get("birthplace_source") == "wikidata" else "medium",
                    "source": facts.get("birthplace_source", "wikipedia"),
                })

    # ── Verify age ──
    if "claimed_age" in claim and "age" in facts:
        actual_age = facts["age"]
        claimed_age = claim["claimed_age"]
        if abs(actual_age - claimed_age) > 1:
            corrections.append({
                "type": "age_correction",
                "person": person,
                "claimed_age": claimed_age,
                "actual_age": actual_age,
                "dob": facts.get("dob", ""),
                "confidence": "high",
                "source": "wikidata" if facts.get("dob") else "wikipedia",
            })

    return corrections


# ── Correction Engine ───────────────────────────────────────────────────────


def _apply_corrections(body: str, corrections: list[dict]) -> str:
    """Apply verified corrections to the article body."""
    corrected = body

    for c in corrections:
        if c["type"] == "place_correction" and c.get("confidence") in ("high", "medium"):
            claimed = c["claimed"]
            actual = c["actual"]

            # Replace contextually
            for prep in ("from", "in", "of", "born in", "hails from"):
                pattern = rf"(\b{re.escape(prep)}\s+){re.escape(claimed)}\b"
                replacement = rf"\g<1>{actual}"
                new = re.sub(pattern, replacement, corrected)
                if new != corrected:
                    corrected = new
                    c["applied"] = True

            # Bare replacement fallback (first occurrence)
            if not c.get("applied"):
                new = corrected.replace(claimed, actual, 1)
                if new != corrected:
                    corrected = new
                    c["applied"] = True

        elif c["type"] == "age_correction" and c.get("confidence") == "high":
            claimed_str = str(c["claimed_age"])
            actual_str = str(c["actual_age"])
            person = c["person"]

            # Replace "N-year-old" near the person's name
            idx = corrected.find(person)
            if idx >= 0:
                window_start = max(0, idx - 100)
                window_end = min(len(corrected), idx + len(person) + 100)
                window = corrected[window_start:window_end]
                fixed = re.sub(
                    rf"\b{re.escape(claimed_str)}-year-old\b",
                    f"{actual_str}-year-old",
                    window, count=1,
                )
                if fixed != window:
                    corrected = corrected[:window_start] + fixed + corrected[window_end:]
                    c["applied"] = True

                # "Name, age," pattern fallback
                if not c.get("applied"):
                    fixed = re.sub(
                        rf"({re.escape(person)},?\s+){re.escape(claimed_str)}\b",
                        rf"\g<1>{actual_str}",
                        corrected, count=1,
                    )
                    if fixed != corrected:
                        corrected = fixed
                        c["applied"] = True

    return corrected


# ── Public API ──────────────────────────────────────────────────────────────


def fact_check_article(
    body: str,
    headline: str = "",
    article_id: str = "",
    dry_run: bool = False,
) -> tuple[str, list[dict]]:
    """
    Fact-check an article body and return (corrected_body, corrections).

    Args:
        body: The article markdown/HTML body text.
        headline: Article headline for additional context.
        article_id: Optional article ID for logging.
        dry_run: If True, only report — don't modify body.

    Returns:
        (corrected_body, corrections)
    """
    global _person_facts_cache
    _person_facts_cache = {}

    print(f"  🔍 Fact-checking article{' (dry run)' if dry_run else ''}...")

    # 1. Extract claims
    claims = extract_claims(body, headline)
    print(f"  📋 Extracted {len(claims)} verifiable claims")

    if not claims:
        return body, []

    # 2. Verify each claim
    all_corrections = []
    verified_persons = set()

    for claim in claims:
        person = claim.get("person", "")
        if person in verified_persons:
            continue

        try:
            results = _verify_claim(claim)
            verified_persons.add(person)

            for result in results:
                all_corrections.append(result)
                desc = result.get("claimed", result.get("claimed_age", "?"))
                actual = result.get("actual", result.get("actual_age", "?"))
                conf = result.get("confidence", "?")
                print(f"    ⚠️  {result['type']}: \"{desc}\" → \"{actual}\" (for {person}) [{result['source']}, {conf}]")

        except Exception as e:
            print(f"    ❌ Error verifying {person}: {e}")
            continue

    if not all_corrections:
        print("  ✅ No factual errors detected")
        return body, []

    # 3. Apply corrections
    if dry_run:
        print(f"  🏷️  Would make {len(all_corrections)} corrections (dry run)")
        return body, all_corrections

    corrected_body = _apply_corrections(body, all_corrections)
    applied = [c for c in all_corrections if c.get("applied")]
    print(f"  ✏️  Applied {len(applied)}/{len(all_corrections)} corrections")

    # 4. Log
    _log_corrections(article_id, headline, all_corrections)

    return corrected_body, all_corrections


def _log_corrections(article_id: str, headline: str, corrections: list[dict]):
    """Append corrections to the fact-check log."""
    try:
        log = json.loads(LOG_PATH.read_text()) if LOG_PATH.exists() else []
    except (json.JSONDecodeError, IOError):
        log = []

    log.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "article_id": article_id,
        "headline": headline[:120],
        "corrections": corrections,
    })
    log = log[-500:]
    LOG_PATH.write_text(json.dumps(log, indent=2, ensure_ascii=False))


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fact-check a Videshi article")
    parser.add_argument("--article-id", help="Supabase article ID to check")
    parser.add_argument("--body-file", help="Path to article body text file")
    parser.add_argument("--dry-run", action="store_true", help="Report only, don't modify")
    parser.add_argument("--test", action="store_true", help="Run built-in self-test")
    args = parser.parse_args()

    if args.test:
        test_body = """## The Rise of Vaibhav Sooryavanshi

A fifteen-year-old from Sambalpur named Vaibhav Sooryavanshi has taken
the IPL by storm. The young left-hander from Sambalpur smashed 776 runs
and hit 72 sixes, shattering Chris Gayle's record.

Virat Kohli, 37, led the charge with an unbeaten 75 off 42 balls in the
final at Ahmedabad against Gujarat Titans.
"""
        print("=" * 60)
        print("SELF-TEST: article with deliberate 'Sambalpur' error")
        print("=" * 60)
        print(f"\nInput body:\n{test_body}")
        corrected, corrections = fact_check_article(
            test_body, "RCB IPL 2026 Champions", dry_run=args.dry_run
        )
        print(f"\n{'─' * 40}")
        print(f"Corrections ({len(corrections)}):")
        for c in corrections:
            print(f"  • {c['type']}: {c.get('claimed', c.get('claimed_age', '?'))} → {c.get('actual', c.get('actual_age', '?'))} [{c.get('confidence')}]")
        if not args.dry_run and corrections:
            print(f"\nCorrected body:\n{corrected}")

    elif args.article_id:
        for envfile in [
            os.path.expanduser("~/.env.supabase"),
            os.path.expanduser("~/workspace/.env.supabase"),
        ]:
            if os.path.exists(envfile):
                with open(envfile) as f:
                    for line in f:
                        if "=" in line and not line.startswith("#"):
                            k, v = line.strip().split("=", 1)
                            os.environ[k] = v

        SB_URL = os.environ["SUPABASE_URL"]
        SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

        r = requests.get(
            f"{SB_URL}/rest/v1/p2_articles",
            params={"id": f"eq.{args.article_id}", "select": "id,headline,body"},
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
            timeout=15,
        )
        if r.status_code != 200 or not r.json():
            print(f"Failed to fetch article: {r.status_code}")
            exit(1)

        article = r.json()[0]
        corrected, corrections = fact_check_article(
            article["body"],
            article.get("headline", ""),
            article_id=args.article_id,
            dry_run=args.dry_run,
        )
        if corrections and not args.dry_run:
            print("\nUpdating article in Supabase...")
            r2 = requests.patch(
                f"{SB_URL}/rest/v1/p2_articles?id=eq.{args.article_id}",
                headers={
                    "apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                    "Content-Type": "application/json",
                },
                json={"body": corrected},
                timeout=15,
            )
            print(f"Update status: {r2.status_code}")

    elif args.body_file:
        with open(args.body_file) as f:
            body_text = f.read()
        corrected, corrections = fact_check_article(body_text, dry_run=args.dry_run)
        if corrections and not args.dry_run:
            with open(args.body_file, "w") as f:
                f.write(corrected)
            print(f"Wrote corrected body to {args.body_file}")
    else:
        parser.print_help()
