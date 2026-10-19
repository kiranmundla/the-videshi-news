"""Regression tests for the named-person extraction in image_sourcer.py
(headline_person_name + _person_name_candidates), which drives the
named-person identity guard and the person-profile lookup.

2026-10-19 audit cases: entity extraction was inventing "names" that
tripped the stay-imageless rule — 'British Mother' (demonym + kinship
noun), 'Para Shooter' (role descriptor that also displaced the real
subject), 'Unbeaten Only' (resultative adjective + focusing adverb from
the mid-headline scan), and 'Min Woo' (a three-part name truncated to
two tokens). The fix adds the missing non-name word CLASSES (demonyms,
kinship/role nouns, pronouns, headline verb forms), a first-token
possessive rule, a sentence-boundary break in the scan, and full-name
recovery for three-part names. It does NOT touch the identity rule
itself: a real named person still engages the guard exactly as before.

Historical cases from the module's own comments are pinned here too —
the word lists are encounter-driven, so every documented encounter gets
a case that must keep passing.

Run: python3 test_person_name_extraction.py  (exit 0 = all pass)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import image_sourcer as IS  # noqa: E402

# (headline, expected headline_person_name)
LEAD_CASES = [
    # ── 2026-10-19 audit: garbage "persons" that must now be None ─────
    ("British Mother Referred to Prevent Counter-Extremism Programme "
     "After Trip to Israel", None),
    ("Para Shooter Rakesh Nidagundi, a Designer Who Found Shooting by "
     "Accident, Targets Asian Para Games Gold", None),
    ("He Asked Followers for Diwali Sweets. They Sent a TV", None),
    ("Sammy Hopes India Series Showing Helps West Indies Attract "
     "Sponsors and Financial Backing", None),
    ("Anthropic's Junior Tech Hires Fall From 27% to 9% as AI Agents "
     "Outwork Staff", None),
    # ── 2026-10-19 audit: real persons, incl. full-name recovery ─────
    ("Min Woo Lee Withdraws in Delhi After Stomach Illness Triggers "
     "Back Spasms", "Min Woo Lee"),
    ("Chinmay Sutar Hits Unbeaten 400, Only Second Indian to Reach "
     "the Mark", "Chinmay Sutar"),
    ("Anshul Kamboj Earns Test Recall for New Zealand After Year of "
     "Rebuilding", "Anshul Kamboj"),
    ("Rahul Agarwal's Fold-Flat Spoon Wins $350,000 Shark Tank Deal",
     "Rahul Agarwal"),
    ("Simran Sharma Replaces Bhavina Patel as India Flag Bearer at "
     "Para Asian Games", "Simran Sharma"),
    # ── Historical documented behaviour (must not regress) ───────────
    ("Ranveer Brar's Tandoori Chicken Wins Hearts", "Ranveer Brar"),
    ("Varun Chakravarthy Ruled Out of Asia Cup", "Varun Chakravarthy"),
    ("Ayurveda Expert Shares Winter Wellness Tips", None),
    ("Supreme Court Rules on Citizenship Case", None),
    ("Allahabad Vendor's Cart Seized by Officials", None),
    ("Air Marshal Arjan Singh Remembered on Anniversary", None),
    ("Delhi Cracks Down on Illegal Parking", None),
    ("Mumbai Rains Disrupt Local Trains", None),
    ("Hurricane Isaias Shuts Gulf Oil Output", None),
    ("King's Lynn Tandoori Named England's Best Curry Restaurant", None),
    ("Hoover's Kabob-Licious Opens Second Location", None),
    ("Sai Kung's Top Indian Restaurant Revealed", None),
    ("West Indies' Plan B Against Abhishek Sharma Revealed", None),
    ("No Handshake, No Trophy for Team India", None),
    ("Five Visa Application Mistakes to Avoid", None),
    ("Radiology Groups Join Forces Against Insurer", None),
    ("Mortgage Rates Rise Again in October", None),
    ("Rat Found Swimming in Gulab Jamun Syrup", None),
    ("Electric Blue Waves Captivate Beachgoers", None),
    ("Still LA's Best Biryani Draws Crowds", None),
    ("Indian National Arrested by ICE Over False Citizenship Claim",
     None),
    ("Kenya Confirms Four More Ebola Cases", None),
    ("Karnataka Requires Night-Time Attendance for Doctors", None),
    ("Google Adopts Meta's Pyrefly as Its Python Type Checker", None),
    ("Mother Teresa Remembered on Her Birth Anniversary", "Mother Teresa"),
    ("Son Heung-min Scores Twice in Spurs Win", "Son Heung-min"),
    ("Mary Kom Wins Gold at Asian Championships", "Mary Kom"),
    ("Neeraj Chopra Wins Gold Again", "Neeraj Chopra"),
]

# (headline, candidates that must be ABSENT from _person_name_candidates)
SCAN_REJECT_CASES = [
    ("Chinmay Sutar Hits Unbeaten 400, Only Second Indian to Reach "
     "the Mark", ["Unbeaten Only", "Unbeaten Only Second"]),
    ("British Mother Referred to Prevent Counter-Extremism Programme "
     "After Trip to Israel",
     ["British Mother", "Mother Referred", "Counter-Extremism Programme",
      "Prevent Counter-Extremism Programme"]),
    ("Para Shooter Rakesh Nidagundi, a Designer Who Found Shooting by "
     "Accident, Targets Asian Para Games Gold",
     ["Para Shooter", "Shooter Rakesh", "Para Shooter Rakesh"]),
    ("He Asked Followers for Diwali Sweets. They Sent a TV on "
     "Cash-on-Delivery",
     ["He Asked", "Sweets They", "They Sent", "He Asked Followers"]),
    ("Anthropic's Junior Tech Hires Fall From 27% to 9% as AI Agents "
     "Outwork Staff", ["Anthropic Junior", "Junior Tech"]),
    ("Four Killed in Manipur as Firewood Collectors Ambushed, "
     "Protesters Reach CM's Gate",
     ["Protesters Reach", "Firewood Collectors", "Collectors Ambushed"]),
    ("NRI Capital Gains: When the Basic Exemption Limit Can Cut Your "
     "Tax", ["Basic Exemption", "Exemption Limit", "Cannot Cut"]),
    ("KKR Plans Over Rs 6,000 Crore Investment in PETRONAS Renewable "
     "Arm Gentari India",
     ["Crore Investment", "Rs Crore", "Renewable Arm", "Arm Gentari"]),
]

# (headline, candidate that must be PRESENT, and its max index)
SCAN_KEEP_CASES = [
    ("Para Shooter Rakesh Nidagundi, a Designer Who Found Shooting by "
     "Accident, Targets Asian Para Games Gold", "Rakesh Nidagundi", 0),
    ("Min Woo Lee Withdraws in Delhi After Stomach Illness Triggers "
     "Back Spasms", "Min Woo Lee", 0),
    ("FBI 'Most Wanted Fraudster' Manjit Bedi Returned From India in "
     "$600,000 SNAP Case", "Manjit Bedi", 0),
    ("From Bollywood to the New York Stage: Jay Patel Co-Produces The "
     "Flowers of Forest Hills", "Jay Patel", 5),
]


def main():
    failures = []

    for headline, expected in LEAD_CASES:
        got = IS.headline_person_name(headline)
        if got != expected:
            failures.append(
                f"LEAD {headline[:60]!r}: got {got!r}, want {expected!r}")

    for headline, banned in SCAN_REJECT_CASES:
        cands = IS._person_name_candidates(
            {"headline": headline, "image_entities": []})
        for b in banned:
            if b in cands:
                failures.append(
                    f"SCAN-REJECT {headline[:50]!r}: {b!r} in {cands}")

    for headline, keep, max_idx in SCAN_KEEP_CASES:
        cands = IS._person_name_candidates(
            {"headline": headline, "image_entities": []})
        if keep not in cands:
            failures.append(
                f"SCAN-KEEP {headline[:50]!r}: {keep!r} missing from {cands}")
        elif cands.index(keep) > max_idx:
            failures.append(
                f"SCAN-KEEP {headline[:50]!r}: {keep!r} at index "
                f"{cands.index(keep)} > {max_idx} in {cands}")

    # Shape checks for the writer-entity path (shares the scan vocabulary)
    if IS._looks_like_person_name("British Mother"):
        failures.append("ENTITY: 'British Mother' passed _looks_like_person_name")
    if not IS._looks_like_person_name("Min Woo Lee"):
        failures.append("ENTITY: 'Min Woo Lee' failed _looks_like_person_name")
    if not IS._looks_like_person_name("Ramya Anche"):
        failures.append("ENTITY: 'Ramya Anche' failed _looks_like_person_name")

    total = (len(LEAD_CASES) + len(SCAN_REJECT_CASES)
             + len(SCAN_KEEP_CASES) + 3)
    if failures:
        print(f"FAIL — {len(failures)}/{total} checks failed:")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print(f"PASS — all {total} extraction checks green "
          f"({len(LEAD_CASES)} lead, {len(SCAN_REJECT_CASES)} scan-reject, "
          f"{len(SCAN_KEEP_CASES)} scan-keep, 3 entity-shape)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
