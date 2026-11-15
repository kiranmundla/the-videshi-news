"""Tests: guards codified from GPT's Muse Enhancement Kit review
(2026-11-15), each verified against the live article first.

Keepers (all confirmed in the DB before codifying):
  - Microsoft 365 phishing + JLR earnings articles: inline captions
    appended the article lede verbatim onto unrelated/archival
    photos (campus aerial, 2004 Xbox conference, 2014 Paris Motor
    Show). Two layers: build_caption's lede skip was defeated by
    the key-takeaways box sitting ahead of the lede; and no
    reviewer check compared caption sentences to the lede.
  - Canada levels plan: qualifier propagation — a data card must
    not restate a target/notional figure without its qualifier.
  - Janakpur acceptance example: a not-yet-operating service must
    never carry a booking CTA.

Run: python3 test_gpt_kit_guards.py  (exit 0 = all pass)
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, filename):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(HERE, filename))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


pp = load("article_picture_pass", "article_picture_pass.py")
rev = load("review_articles", "review-articles.py")
gate = load("content_gate", "content_gate.py")

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


# ── 1. build_caption: the takeaways box must not defeat the lede skip
MS_BODY = (
    '<div class="key-takeaways"><ul>'
    "<li>Microsoft Threat Intelligence detected an active phishing "
    "campaign on November 13 that impersonates Microsoft 365 "
    "service-health notices.</li>"
    "<li>Do not use the recovery link in an unexpected email.</li>"
    "</ul></div>"
    "<p>Microsoft Threat Intelligence detected an active phishing "
    "campaign on November 13 that impersonates Microsoft 365 "
    "service-health notices and references the real Exchange Online "
    "incident.</p>"
    "<p>The Microsoft campus in Redmond hosts the security teams "
    "who track these campaigns year round.</p>")
cand = {"subject": "The west campus of Microsoft, Redmond, "
                   "Washington, taken from about 1,500 feet",
        "title": "File:Aerial Microsoft West Campus August 2019.jpg"}
cap = pp.build_caption("Microsoft", cand, {"body": MS_BODY})
check("caption describes the campus photo",
      cap.startswith("The west campus of Microsoft"))
check("caption does NOT append the phishing lede",
      "phishing campaign" not in cap)
check("genuine context sentence about the depicted subject appends",
      "hosts the security teams" in cap)

# ── 2. Reviewer: lede-append captions flagged (real published text)
ms_article = {
    "headline": "Microsoft Warns of Phishing Campaign",
    "image_caption": "",
    "body": (
        '<div class="key-takeaways"><ul><li>Phishing campaign '
        "detected.</li></ul></div>"
        "<p>Microsoft Threat Intelligence detected an active "
        "phishing campaign on November 13 that impersonates "
        "Microsoft 365 service-health notices.</p>"
        '<figure><img src="https://upload.wikimedia.org/x.jpg" '
        'alt="x"><figcaption>Peter Moore presenting at the 2004 '
        "Xbox conference, Shrine Auditorium, Los Angeles. Microsoft "
        "Threat Intelligence detected an active phishing campaign "
        "on November 13 that impersonates Microsoft 365 "
        "service-health notices.</figcaption></figure>"),
}
f = rev.check_caption_lede_append(ms_article)
check("reviewer flags the Xbox-photo lede append", len(f) == 1)

good_article = {
    "headline": "Janakpur Train Approved",
    "image_caption": "",
    "body": (
        "<p>India and Nepal have approved a weekly train between "
        "Janakpur and Ayodhya, officials said on Friday.</p>"
        '<figure><img src="https://upload.wikimedia.org/y.jpg" '
        'alt="y"><figcaption>Janaki Mandir, Janakpur. The temple '
        "town is the Nepal terminus of the approved weekly "
        "service.</figcaption></figure>"),
}
check("reviewer passes a subject-true caption",
      rev.check_caption_lede_append(good_article) == [])

# ── 3. Gate: card qualifier propagation
ca_body = ("<p>The plan holds new international student arrivals "
           "at up to 150,000 a year. The 2028 and 2029 figures are "
           "notional and are confirmed or adjusted later.</p>")
card = [{"type": "price_compare", "title": "Student Arrivals",
         "headers": ["Year", "Arrivals"],
         "rows": [["2028", "150,000"]]}]
f = gate.check_card_qualifier(
    {"headline": "Canada Plan", "body": ca_body, "data_cards": card})
check("card dropping 'up to' is held", len(f) == 1)
framed = [{"type": "price_compare",
           "title": "Student Arrival Targets (Notional)",
           "headers": ["Year", "Arrivals"],
           "rows": [["2028", "150,000"]]}]
check("target-framed card title exempts",
      gate.check_card_qualifier(
          {"headline": "Canada Plan", "body": ca_body,
           "data_cards": framed}) == [])
flat_body = ("<p>Arrivals were 150,000 last year, a record. "
             "Officials cite up to 150,000 places in the plan.</p>")
check("figure also stated flatly in body passes",
      gate.check_card_qualifier(
          {"headline": "Canada Plan", "body": flat_body,
           "data_cards": card}) == [])

# ── 4. Gate: service-state contradiction
janakpur_bad = (
    '<div class="service-status"><strong>Approved, not yet '
    "operating:</strong> launch date not announced.</div>"
    "<p>The weekly train will link the two temple towns.</p>"
    "<p>Book now to reserve your seat on the first run.</p>")
f = gate.check_service_state_contradiction(
    {"headline": "Train Approved", "body": janakpur_bad})
check("'Book now' on a not-yet-operating service is held",
      len(f) == 1)
janakpur_ok = janakpur_bad.replace(
    "<p>Book now to reserve your seat on the first run.</p>",
    "<p>Fares and booking details have not been announced.</p>")
check("no CTA -> no contradiction",
      gate.check_service_state_contradiction(
          {"headline": "Train Approved", "body": janakpur_ok}) == [])
live_service = ("<p>The daily service now runs between the two "
                "cities.</p><p>Book now on the official site.</p>")
check("operating service may carry a CTA",
      gate.check_service_state_contradiction(
          {"headline": "Service Live", "body": live_service}) == [])

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
