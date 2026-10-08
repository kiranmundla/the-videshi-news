"""Regression tests for trailer-watch title parsing (film name, subtitle,
headline). Run: python3 test_trailer_title.py  (exit 0 = all pass)
"""
import re
import sys

_src = open("trailer-watch.py").read().split("if __name__")[0]
_ns = {}
exec(compile(_src, "trailer-watch.py", "exec"), _ns)
split_film_title = _ns["split_film_title"]
extract_subtitle = _ns["extract_subtitle"]
clean_film_name = _ns["clean_film_name"]
_STUDIO_RE = _ns["_STUDIO_RE"]

# (video title, expected film, expected headline)
CASES = [
    # documented behaviors (must not regress)
    ("Bhogi - Official Teaser | Sharwanand",
     "Bhogi", "Bhogi \u2013 Sharwanand Teaser Out"),
    ("The Eken: Kerela - e Kurukshetra Official Trailer",
     "The Eken: Kerela - e Kurukshetra",
     "The Eken: Kerela - e Kurukshetra Trailer Out"),
    ("Our Story. Our History. Our Truth. | Ranabaali Trailer on October 8th | Hombale Films",
     "Ranabaali", "Ranabaali Trailer Out"),
    ("Drive - The Pretenders Official Teaser | Prime Video India",
     "Drive", "Drive \u2013 The Pretenders Teaser Out"),
    ("#418 - Official Trailer (Hindi)",
     "#418", "#418 Trailer Out"),
    ("Mandaadi | Hindi Trailer | Soori, Suhas, Mahima Nambiar",
     "Mandaadi", "Mandaadi Trailer Out: Soori, Suhas, Mahima Nambiar"),
    # bug fixes 2026-10-08: mangled film names caught on the live site
    ("বন্ধুরা পাশে থাকলে #EbhabeoPhireAshaJaye | Rahul Dev Bose | Traya | 10 Oct | hoichoi | #Trailer",
     "Ebhabeo Phire Asha Jaye",
     "Ebhabeo Phire Asha Jaye \u2013 Rahul Dev Bose Trailer Out"),
    ("Official Trailer - Birangana 2 | Sandipta Sen | Nirjhar Mitra | 15 OCT | hoichoi",
     "Birangana 2",
     "Birangana 2 Trailer Out: Sandipta Sen"),
    ("Hanuman Ansh - A Powerful Divine Story | Official Trailer",
     "Hanuman Ansh",
     "Hanuman Ansh \u2013 A Powerful Divine Story Trailer Out"),
    ("Epic - Official Trailer | Anand Deverakonda",
     "Epic", "Epic \u2013 Anand Deverakonda Trailer Out"),
    ("Kappi Squad - Official Trailer | 15th October",
     "Kappi Squad", "Kappi Squad Trailer Out: 15th October"),
    ("Vijaynagar'er Hirey | Official Teaser | Prosenjit Chatterjee | hoichoi",
     "Vijaynagar'er Hirey",
     "Vijaynagar'er Hirey \u2013 Prosenjit Chatterjee Teaser Out"),
]


def headline(title):
    """Mirror build_brief_article's headline construction."""
    kind = "Teaser" if re.search(r"teas", title, re.I) else "Trailer"
    film, rest = split_film_title(title)
    raw_film = clean_film_name(film) or "New release"
    film = raw_film
    subtitle = clean_film_name(extract_subtitle(title))
    if subtitle and subtitle.lower() not in film.lower():
        film = f"{film} \u2013 {subtitle}"
    hook = clean_film_name(rest.split("|")[0].strip()) if rest else ""
    if hook.startswith("@") or _STUDIO_RE.search(hook) or \
            (hook and hook.lower() in film.lower()):
        hook = ""
    return raw_film, f"{film} {kind} Out" + (f": {hook[:60]}" if hook else "")


fails = 0
for title, exp_film, exp_head in CASES:
    raw_film, head = headline(title)
    ok = raw_film == exp_film and head == exp_head
    if not ok:
        fails += 1
        print(f"FAIL {title!r}\n  film: {raw_film!r} (want {exp_film!r})\n"
              f"  head: {head!r} (want {exp_head!r})")

print(f"{len(CASES) - fails}/{len(CASES)} pass")
sys.exit(1 if fails else 0)
