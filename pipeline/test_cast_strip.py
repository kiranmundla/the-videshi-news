"""Regression tests for cast_strip identity checks (2026-10-14 fix:
exact-title Wikipedia match is NOT identity proof — the page titled
"Beatrice Campbell" is a Northern Irish actress, 1922-1979, whose page
thumbnail is her husband Nigel Patrick; the film's Beatrice Campbell is
a newcomer child actress who must render as initials).

Network-free: Wikipedia summaries are fixtures modelled on the real
REST page-summary responses, injected via the module's summary cache;
person_images / Commons lookups are stubbed.
Run: python3 test_cast_strip.py  (exit 0 = all pass)
"""
import sys

import cast_strip as cs

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


def summary(title, description, extract, thumb=None, type_="standard"):
    d = {"type": type_, "title": title, "description": description,
         "extract": extract}
    if thumb:
        d["thumbnail"] = {"source": thumb}
        d["originalimage"] = {"source": thumb}
    return d


def prime(name, fixture):
    cs._wiki_summary_cache[name.lower()] = fixture


# Stubs: no Supabase, no Commons network. Commons records its calls.
cs._person_images_lookup = lambda n: None
_commons_calls = []


def _commons_stub(name, ambiguous=False):
    _commons_calls.append((name, ambiguous))
    return None


cs._commons_lookup = _commons_stub

# ------------------------------------------------------- Beatrice Campbell
# Real page data: deceased 1979; thumbnail is Nigel_Patrick.jpg.
prime("Beatrice Campbell", summary(
    "Beatrice Campbell",
    "British actress (1922–1979)",
    "Beatrice Campbell was a Northern Irish stage and film actress, "
    "born in County Down, Northern Ireland",
    "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/8c/"
    "Nigel_Patrick.jpg/330px-Nigel_Patrick.jpg"))
check("Beatrice: identity conflict detected",
      cs._summary_identity_conflict(
          cs._wiki_summary("Beatrice Campbell"), "Beatrice Campbell",
          now_year=2026) is True)
check("Beatrice: wikipedia lookup rejected (exact title is not proof)",
      cs._wikipedia_lookup("Beatrice Campbell") is None)
check("Beatrice: name treated as ambiguous (Commons goes strict)",
      cs._is_ambiguous("Beatrice Campbell") is True)
_commons_calls.clear()
check("Beatrice: resolve falls back to no photo",
      cs.resolve_headshot("Beatrice Campbell") is None)
check("Beatrice: Commons was consulted with ambiguous=True",
      _commons_calls == [("Beatrice Campbell", True)])
block = cs.render_cast_strip_block("Beatrice Campbell",
                                   resolve=cs.resolve_headshot)
check("Beatrice: strip renders initials, no <img>",
      "cast-initials" in block and "<img" not in block)

# ------------------------------------------------------------ Emma Mackey
# Real page data: living (born 1996). REGRESSION GUARD: her extract
# mentions "Sex Education (2019–2023)" — a show run, NOT life dates;
# reading every extract parenthetical as a birth-death range wrongly
# rejected her.
prime("Emma Mackey", summary(
    "Emma Mackey",
    "British and French actress (born 1996)",
    "Emma Margaret Marie Tachard-Mackey is a British-French actress. "
    "She is widely known for her breakthrough performance as troubled "
    "teenager Maeve Wiley in the Netflix comedy-drama series Sex "
    "Education (2019–2023) which earned her the nomination for the "
    "British Academy Television Award.",
    "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/78/"
    "MKr385780_Emma_Mackey_%28Alpha%2C_Cannes_2025%29.jpg/"
    "330px-MKr385780_Emma_Mackey_%28Alpha%2C_Cannes_2025%29.jpg"))
check("Emma Mackey: no conflict (show-run years are not life dates)",
      cs._summary_identity_conflict(
          cs._wiki_summary("Emma Mackey"), "Emma Mackey",
          now_year=2026) is False)
check("Emma Mackey: wikipedia photo accepted",
      (cs._wikipedia_lookup("Emma Mackey") or "").endswith(
          "Emma_Mackey_%28Alpha%2C_Cannes_2025%29.jpg"))
check("Emma Mackey: not ambiguous",
      cs._is_ambiguous("Emma Mackey") is False)

# ------------------------------------------------------------ Meryl Streep
# Living actor with an old birth year: (born 1949) must be accepted.
prime("Meryl Streep", summary(
    "Meryl Streep",
    "American actress (born 1949)",
    "Mary Louise \"Meryl\" Streep is an American actress.",
    "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e5/"
    "Meryl_Streep-_Press_conference.jpg/330px-Meryl_Streep.jpg"))
check("Meryl Streep (born 1949): no conflict",
      cs._summary_identity_conflict(
          cs._wiki_summary("Meryl Streep"), "Meryl Streep",
          now_year=2026) is False)
check("Meryl Streep: wikipedia photo accepted",
      cs._wikipedia_lookup("Meryl Streep") is not None)

# --------------------------------------------------------- disambiguation
prime("Atul Kumar", summary(
    "Atul Kumar", "Topics referred to by the same term",
    "Atul Kumar may refer to: Atul Kumar (ophthalmologist)",
    type_="disambiguation"))
check("disambiguation page: wikipedia lookup rejected",
      cs._wikipedia_lookup("Atul Kumar") is None)
check("disambiguation page: ambiguous (existing behaviour)",
      cs._is_ambiguous("Atul Kumar") is True)
check("disambiguation page: not an identity conflict (separate path)",
      cs._summary_identity_conflict(
          cs._wiki_summary("Atul Kumar"), "Atul Kumar",
          now_year=2026) is False)

# --------------------------------------- death range in the extract lead
# Description carries no dates; the extract's lead parenthetical does.
prime("John Example", summary(
    "John Example",
    "American actor",
    "John Example (3 May 1930 – 2 June 2020) was an American actor.",
    "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a1/"
    "John_Example.jpg/330px-John_Example.jpg"))
check("extract lead birth-death range: conflict",
      cs._summary_identity_conflict(
          cs._wiki_summary("John Example"), "John Example",
          now_year=2026) is True)
check("extract lead birth-death range: lookup rejected",
      cs._wikipedia_lookup("John Example") is None)

# --------------------------------------- thumbnail names a different person
# No dates anywhere; the page's own photo is of someone else entirely.
prime("Jane Doe", summary(
    "Jane Doe",
    "British actress",
    "Jane Doe is a British actress.",
    "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b2/"
    "John_Smith_at_the_premiere.jpg/330px-John_Smith_at_the_premiere.jpg"))
check("thumbnail names another person: conflict",
      cs._summary_identity_conflict(
          cs._wiki_summary("Jane Doe"), "Jane Doe", now_year=2026) is True)
check("thumbnail names another person: lookup rejected",
      cs._wikipedia_lookup("Jane Doe") is None)

# Control: generic filename carries NO identity evidence -> accepted.
prime("Jane Roe", summary(
    "Jane Roe",
    "British actress",
    "Jane Roe is a British actress.",
    "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c3/"
    "DSC_4471.jpg/330px-DSC_4471.jpg"))
check("generic filename, no dates: no conflict (no positive evidence)",
      cs._summary_identity_conflict(
          cs._wiki_summary("Jane Roe"), "Jane Roe", now_year=2026) is False)
check("generic filename, no dates: photo accepted",
      cs._wikipedia_lookup("Jane Roe") is not None)

# ------------------------------------------------- implausible birth year
prime("Old Timer", summary(
    "Old Timer",
    "American actor (born 1901)",
    "Old Timer is an American actor.",
    "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d4/"
    "Old_Timer.jpg/330px-Old_Timer.jpg"))
check("born 1901 (age 125 in 2026): conflict",
      cs._summary_identity_conflict(
          cs._wiki_summary("Old Timer"), "Old Timer",
          now_year=2026) is True)
prime("Senior Actor", summary(
    "Senior Actor",
    "American actor (born 1930)",
    "Senior Actor is an American actor.",
    "https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e6/"
    "Senior_Actor.jpg/330px-Senior_Actor.jpg"))
check("born 1930 (age 96 in 2026): no conflict — old but plausible",
      cs._summary_identity_conflict(
          cs._wiki_summary("Senior Actor"), "Senior Actor",
          now_year=2026) is False)

# Hyphen (not en dash) life range in description also counts.
prime("Hyphen Case", summary(
    "Hyphen Case",
    "English actor (1889-1977)",
    "Hyphen Case was an English actor.",
    "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f7/"
    "Hyphen_Case.jpg/330px-Hyphen_Case.jpg"))
check("hyphen life range (1889-1977): conflict",
      cs._summary_identity_conflict(
          cs._wiki_summary("Hyphen Case"), "Hyphen Case",
          now_year=2026) is True)

# ------------------------------------- filename tokenisation edge cases
# Merged-name filename ("PaulBettany-byPhilipRomano.jpg") plainly names
# the right person — one token containing both name tokens must count
# as overlap, not as "names another person".
check("merged-name filename is the person, not another person",
      cs._image_names_other_person(
          "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/2b/"
          "PaulBettany-byPhilipRomano.jpg/330px-PaulBettany.jpg",
          "Paul Bettany") is False)
# Diacritics: 'Misel Maticevic' (ASCII-folded file) is 'Mišel Matičević'.
check("diacritic-folded filename matches the accented name",
      cs._image_names_other_person(
          "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/46/"
          "Misel_Maticevic_2011.JPG/330px-Misel_Maticevic_2011.JPG",
          "Mišel Matičević") is False)
# ... while a folded filename of a genuinely different person still fires.
check("folded filename of a different person still rejected",
      cs._image_names_other_person(
          "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/8c/"
          "Nigel_Patrick.jpg/330px-Nigel_Patrick.jpg",
          "Beatrice Campbell") is True)

# ------------------------------------------------------ real-page edges
# Mišel Matičević: real thumbnail URL — percent-encoded diacritics in
# the name AND a utm query string. Both used to shred the filename
# tokens and fake a "different person" verdict.
prime("Mišel Matičević", summary(
    "Mišel Matičević",
    "German actor (born 1970)",
    "Mišel Matičević is a German film, television, and theater actor "
    "of Croatian descent.",
    "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/46/"
    "Grimme-Preis_2011_-_Mi%C5%A1el_Mati%C4%8Devi%C4%87_1.JPG/"
    "330px-Grimme-Preis_2011_-_Mi%C5%A1el_Mati%C4%8Devi%C4%87_1.JPG"
    "?utm_source=en.wikipedia.org&utm_campaign=api"))
check("Mišel Matičević: no conflict (diacritics + query string)",
      cs._summary_identity_conflict(
          cs._wiki_summary("Mišel Matičević"), "Mišel Matičević",
          now_year=2026) is False)
check("Mišel Matičević: wikipedia photo accepted",
      cs._wikipedia_lookup("Mišel Matičević") is not None)

# Lewis Tan: page photo is a CHARACTER still ("Cole Young as depicted
# in Mortal Kombat II") — of the actor himself. A "(born 1987)" living
# marker anchors the page, so the filename check must not fire.
prime("Lewis Tan", summary(
    "Lewis Tan",
    "British and American actor and martial artist (born 1987)",
    "Lewis Singwah Tan is a British-American actor and martial artist.",
    "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/45/"
    "Cole_Young_as_depicted_in_Mortal_Kombat_II_%282026_film%29_"
    "%28cropped%29.png/330px-Cole_Young.png"))
check("Lewis Tan: character-still thumbnail is not a conflict",
      cs._summary_identity_conflict(
          cs._wiki_summary("Lewis Tan"), "Lewis Tan",
          now_year=2026) is False)
check("Lewis Tan: wikipedia photo accepted",
      cs._wikipedia_lookup("Lewis Tan") is not None)

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
