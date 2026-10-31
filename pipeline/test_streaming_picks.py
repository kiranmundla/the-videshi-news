"""Regression tests for the streaming-picks corroboration gate.

The case (2026-10-31): streaming-picks.py published a "Gajab Raat" entry
with an entirely invented cast (Rajkummar Rao / Bhumi Pednekar / Vikrant
Massey — none are in the film), a fabricated heist-comedy synopsis, and
the wrong platform (JioHotstar instead of Netflix). Auditing the rest of
that week's file found the same disease in 5 of the other 6 picks:
invented casts throughout, a "Zee5 streaming" pick (Tum Mere Ho) that was
a film still playing in cinemas, wrong platforms for Pooja Meri Jaan and
Ashakal Aayiram, and Taylor Kitsch listed for a season he is not in.

Root cause: GPT-4o-mini was asked to produce platform/cast/synopsis from
search snippets and its output was published unchecked — the prompt's
"do NOT invent cast members" was the only safeguard.

The fix: corroborate_picks() verifies every pick against fetched
evidence (Wikipedia page + infobox, platform-neutral press search) and
DROPS anything it cannot corroborate. verify_pick() is a pure function,
so these tests inject canned evidence — no network, no OpenAI key.

Run: python3 test_streaming_picks.py  (exit 0 = all pass)
"""
import importlib.util
import pathlib

_spec = importlib.util.spec_from_file_location(
    "streaming_picks", pathlib.Path(__file__).parent / "streaming-picks.py")
sp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sp)

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


def empty_evidence(**over):
    ev = {"found": False, "wiki_title": "", "wiki_extract": "",
          "wiki_thumb": "", "infobox": {}, "press_text": "", "text": ""}
    ev.update(over)
    return ev


# ── Canned evidence: what the fetcher returns for the REAL Gajab Raat ──
GAJAB_PRESS = (
    "Gajab Raat is now streaming on Netflix. Manoj Bajpayee plays sub-inspector "
    "Ajay Dikshit in Ritesh Shah's directorial debut, written and produced by "
    "Neeraj Pandey. Set over a single night in Delhi, a young journalist is "
    "found brutally injured after being thrown from a moving car at Connaught "
    "Place; as officers from the CBI and NIA circle the case, Dikshit uncovers "
    "a conspiracy. Also starring Saqib Saleem, Akshay Oberoi, Divya Dutta and "
    "Kiku Sharda."
)
GAJAB_EVIDENCE = empty_evidence(found=True, press_text=GAJAB_PRESS, text=GAJAB_PRESS)

GAJAB_PICK = {
    "title": "Gajab Raat", "platform": "Netflix", "year": 2026,
    "genre": "Crime Thriller", "language": "Hindi", "director": "Ritesh Shah",
    # The first two are real; the last two are the hallucinated kind the
    # model used to add — they must be stripped, not published.
    "cast": ["Manoj Bajpayee", "Saqib Saleem", "Rajkummar Rao", "Bhumi Pednekar"],
    "synopsis": ("Set over a single night in Delhi, sub-inspector Ajay Dikshit "
                 "investigates the case of a young woman found brutally injured "
                 "after being thrown from a moving car, uncovering a conspiracy "
                 "as CBI and NIA officers circle the case."),
}

# 1 ── A plausible-but-nonexistent title must produce NO pick ─────────────
fake_pick = {
    "title": "Chandni Chowk Nights", "platform": "Netflix", "year": 2026,
    "cast": ["Aarav Kapoor", "Meera Sethi", "Dev Malhotra"],
    "director": "Rohan Bhatt",
    "synopsis": "Two rival food bloggers fall in love across Old Delhi's gallis.",
}
cleaned, reason = sp.verify_pick(dict(fake_pick), empty_evidence())
check("nonexistent title: verify_pick drops it", cleaned is None, f"got {cleaned}")
survivors = sp.corroborate_picks([dict(fake_pick)],
                                 evidence_fetcher=lambda p: empty_evidence())
check("nonexistent title: corroborate_picks emits nothing", survivors == [])

# 2 ── Gajab Raat: corroborated pick keeps Netflix + Bajpayee ─────────────
cleaned, reason = sp.verify_pick(dict(GAJAB_PICK), dict(GAJAB_EVIDENCE))
check("Gajab Raat: pick survives corroboration", cleaned is not None, reason)
if cleaned:
    check("Gajab Raat: platform is Netflix", cleaned["platform"] == "Netflix")
    check("Gajab Raat: cast includes Manoj Bajpayee",
          "Manoj Bajpayee" in cleaned["cast"], f"cast={cleaned['cast']}")
    check("Gajab Raat: hallucinated cast stripped",
          "Rajkummar Rao" not in cleaned["cast"]
          and "Bhumi Pednekar" not in cleaned["cast"],
          f"cast={cleaned['cast']}")
    check("Gajab Raat: director corroborated", cleaned["director"] == "Ritesh Shah")

# 3 ── Same evidence, wrong claimed platform → dropped (the original bug) ─
wrong_platform = dict(GAJAB_PICK, platform="JioHotstar")
cleaned, reason = sp.verify_pick(wrong_platform, dict(GAJAB_EVIDENCE))
check("Gajab Raat as 'JioHotstar': dropped", cleaned is None,
      f"reason={reason!r} cleaned={cleaned}")

# 4 ── Tum Mere Ho trap: real film, but theatrical-only; claimed Zee5 ─────
# (Evidence below is what fetch_title_evidence yields after its year guard
# discards the 1990 namesake's Wikipedia page: press confirms the title,
# the real cast and a CINEMA release — and never mentions Zee5.)
tmh_press = (
    "Tum Mere Ho, directed by Ashish Panda and starring Gurmeet Choudhary "
    "and Isha Malviya in her Bollywood debut, released in cinemas on "
    "23 October 2026. The Hindi romantic drama is produced by Debguru Films."
)
tmh_evidence = empty_evidence(found=True, press_text=tmh_press, text=tmh_press)
tmh_pick = {
    "title": "Tum Mere Ho", "platform": "Zee5", "year": 2026,
    "cast": ["Kartik Aaryan", "Kiara Advani"], "director": "",
    "synopsis": "A poignant love story between two individuals from different "
                "backgrounds who confront their families' disapproval.",
}
cleaned, reason = sp.verify_pick(dict(tmh_pick), tmh_evidence)
check("Tum Mere Ho as 'Zee5 streaming': dropped", cleaned is None,
      f"reason={reason!r} cleaned={cleaned}")

# 5 ── Infobox can supply a cast the model left empty (sourced, not invented)
ashakal_evidence = empty_evidence(
    found=True,
    wiki_title="Ashakal Aayiram",
    wiki_extract=("Ashakal Aayiram is a 2026 Indian Malayalam-language family "
                  "comedy drama film directed by G. Prajith, streaming on Zee5."),
    infobox={"director": "G. Prajith",
             "starring": ["Jayaram", "Kalidas Jayaram", "Asha Sharath"],
             "language": "Malayalam", "year": 2026},
    text=("Ashakal Aayiram is a 2026 Indian Malayalam-language family comedy "
          "drama film directed by G. Prajith, streaming on Zee5. Jayaram "
          "Kalidas Jayaram Asha Sharath Malayalam"),
)
ashakal_pick = {
    "title": "Ashakal Aayiram", "platform": "Zee5", "year": 2026,
    "cast": [], "director": "",
    "synopsis": "A Malayalam family comedy drama directed by G. Prajith.",
}
cleaned, reason = sp.verify_pick(dict(ashakal_pick), ashakal_evidence)
check("Ashakal Aayiram: survives on infobox evidence", cleaned is not None, reason)
if cleaned:
    check("Ashakal Aayiram: cast filled from infobox, not invented",
          cleaned["cast"][:2] == ["Jayaram", "Kalidas Jayaram"],
          f"cast={cleaned['cast']}")
    check("Ashakal Aayiram: director filled from infobox",
          cleaned["director"] == "G. Prajith")

print(f"\n{total - fails}/{total} checks passed")
raise SystemExit(1 if fails else 0)
