#!/usr/bin/env python3
"""Regression tests for the extractor-recall fix (2026-10-31).

The verified_sourcer shadow run of 2026-10-31 failed closed on
three stories with "no headline subject identified" — the
subjects were in the headlines all along:

  * Dallas BAPS Diwali — the extractor's fragment suppression
    deleted 'BAPS', the headline's subject, as a token subset
    of the body phrase 'BAPS Charities'; and BAPS had no
    registry entry, so no single-token subject was eligible.
  * Sensex rally — same suppression deleted 'Nifty' under the
    body phrase 'Nifty Pharma'; 'Sensex' survived extraction
    but had no registry entry and was eligibility-filtered.
  * Chrome/Gmail — 'Chrome' and 'Gmail' survived extraction
    but had no registry entries and were eligibility-filtered.

Fixes pinned here:
  1. article_picture_pass fragment suppression no longer drops
     a headline-material entity whose supersets are body-only
     derivative phrases; when a superset is ALSO headline
     material the suppression still applies ('Aamir' inside
     the headline's own 'Aamir Khan').
  2. Registry curation (entity_registry.json): BAPS (org-level
     Q4936220 — the Dallas/Irving mandir has no Wikidata item),
     S&P BSE Sensex (Q796994, alias 'Sensex'), Google Chrome
     (Q777, curated alias 'Chrome'); Gmail auto-registered via
     entity_resolve cache-back (Q9334). Eligibility still flows
     through verified_sourcer._subject_eligible — the
     extractor's single-token sourceable=False contract is
     UNCHANGED, and unregistered headline common nouns
     ('Ordering', 'Profit', 'Points', 'Rally') still never
     become subjects.

Fixtures: the three real articles (headline + body as
published, fetched from p2_articles 2026-10-31).

Run: python3 -u test_extractor_recall.py
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import article_picture_pass as P
import verified_sourcer as vs

FAILURES = []


def check(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name +
          (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


ARTICLES = {'dallas-baps-mandir-diwali-annakut-fireworks-november-10': {'headline': 'Dallas BAPS Mandir Expects 12,000 for Diwali Annakut and Fireworks on November 10', 'slug': 'dallas-baps-mandir-diwali-annakut-fireworks-november-10', 'category': 'nri-world', 'body': '<div class="key-takeaways"><ul><li>The BAPS Shri Swaminarayan Mandir in Irving expects roughly 12,000 visitors for its Diwali and Hindu New Year celebration on Tuesday, November 10, from 3:00 p.m. to 8:00 p.m.</li><li>The centrepiece is the Annakut, an offering of hundreds of vegetarian dishes prepared by devotees, alongside an exhibition titled "Light Beyond Lamps: Journey Through Hindu Sanskruti" and a closing fireworks and light-and-sound show.</li><li>BAPS Charities will make a food donation to Irving Cares as part of the event; its Dallas-area drive for the same nonprofit collected about 2,000 pounds of food in October 2025.</li><li>No ticket or registration details have been published for the BAPS event — Dallas-area readers should confirm entry arrangements on the mandir\'s page before travelling; the Radha Krishna Temple of Dallas in Allen runs its own Diwali programme November 5-10.</li></ul></div>\n<p>Dallas-Fort Worth\'s Diwali season peaks on Tuesday, November 10, when the BAPS Shri Swaminarayan Mandir in Irving hosts its Diwali and Hindu New Year celebration and expects roughly 12,000 visitors over the course of the day. The event runs from 3:00 p.m. to 8:00 p.m., two days after Diwali itself, which falls on Sunday, November 8 this year, <a href="https://hoodline.com/2026/10/dallas-baps-temple-expects-12-000-for-diwali-fireworks-and-food-drive-nov-10/" target="_blank" rel="noopener">Hoodline reported</a>.</p>\n<h2>Annakut at the Centre</h2>\n<p>The afternoon is built around the Annakut, the traditional mountain of food offered to the deities for the Hindu New Year. BAPS describes the offering as hundreds of vegetarian dishes — snacks, sweets and savouries prepared by devotees and presented in gratitude — set against handcrafted Diwali decor. Visitors can also walk through an immersive exhibition, "Light Beyond Lamps: Journey Through Hindu Sanskruti," which explores Hindu values and traditions; Hoodline reported the same theme is being used across BAPS mandirs throughout North America for this year\'s Diwali and New Year celebrations.</p>\n<p>The programme also weaves in the United States\' 250th anniversary and a tribute to frontline heroes, with a dedicated stage segment and planned flag processions, before closing with a fireworks show and a light-and-sound experience.</p>\n\n<figure style="margin:28px auto;text-align:center"><img src="https://thumb.wikimedia.org/wikipedia/commons/thumb/4/41/Annakut_Puja_01.jpg/960px-Annakut_Puja_01.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail" alt="Annakut. The centrepiece is the Annakut, an offering of hundreds of vegetarian dishes prepared by devotees, alongside an exhibition titled &quot;Light Beyond Lamps: Journey Through Hindu Sanskruti&quot; and a closing fireworks and light-and-sound show." style="max-width:100%;border-radius:8px" loading="lazy"><figcaption style="font-size:0.85rem;color:#666;margin-top:8px">Annakut. The centrepiece is the Annakut, an offering of hundreds of vegetarian dishes prepared by devotees, alongside an exhibition titled "Light Beyond Lamps: Journey Through Hindu Sanskruti" and a closing fireworks and light-and-sound show.</figcaption></figure>\n\n<h2>Service Alongside Celebration</h2>\n<p>BAPS Charities, the organisation\'s humanitarian arm, will make a charitable food donation benefiting Irving Cares, a local nonprofit, as part of the event. The pairing has local history: a BAPS Charities food drive in the Dallas area from October 4 to 21, 2025, also for Irving Cares, collected about 2,000 pounds of food from volunteers of varied ages and backgrounds.</p>\n<h2>The Wider Dallas Diwali Week</h2>\n<p>The BAPS celebration caps a full week of Diwali programming across the metroplex. The <a href="https://www.radhakrishnatemple.net/diwali-mela-dallas" target="_blank" rel="noopener">Radha Krishna Temple of Dallas in Allen</a> runs its Diwali Mahotsav from November 5 to 10, including the lighting of 11,111 diyas on Saturday, November 7, from 6:00 p.m., Lakshmi Puja on November 8 — the temple lists the Drik Panchang muhurat for Dallas as 5:52 to 7:46 p.m. CST — an Annakoot on November 9, cultural performances, a food festival and fireworks. A Frisco Diwali Mela is also scheduled for November 1 at Kaleidoscope Park, with dance, a talent stage, a kids\' fun zone and vendors.</p>\n<h2>Planning Your Visit</h2>\n<p>Hoodline\'s report lists no ticket price, registration or RSVP requirement for the November 10 BAPS event, and the mandir\'s own page is the place to confirm entry and parking arrangements before setting out: see the <a href="http://www.baps.org/Global-Network/North-America/Dallas.aspx" target="_blank" rel="noopener">BAPS Dallas mandir page</a>. With 12,000 visitors expected across five hours, arriving early in the 3:00 p.m. window is the practical move for families who want the Annakut darshan and the exhibition before the evening fireworks crowd builds.</p>\n<div class="related-coverage"><div class="related-coverage-title">Related coverage</div><a class="related-item" href="/articles/times-square-diwali-countdown-2026"><span class="related-item-title">Times Square Rings In Diwali With Diya Countdown and Concert</span><span class="related-item-meta">Nri World · 2026-10-26</span></a><a class="related-item" href="/articles/indian-woman-fined-2500-molesting-singapore-nightclub-server"><span class="related-item-title">Indian Woman Fined S$2,500 for Molesting Singapore Nightclub Server</span><span class="related-item-meta">Nri World · 2026-10-30</span></a><a class="related-item" href="/articles/ajit-kaur-missing-ceres-woman-found-canal-california"><span class="related-item-title">Missing Ceres Woman Ajit Kaur, 72, Found Dead in Canal After Two-Month Search</span><span class="related-item-meta">Nri World · 2026-10-30</span></a></div>', 'image_entities': None}, 'chrome-autofill-gmail-booking-codes-order-numbers-gemini': {'headline': 'Chrome Can Now Pull Booking Codes and Order Numbers From Your Gmail', 'slug': 'chrome-autofill-gmail-booking-codes-order-numbers-gemini', 'category': 'technology', 'body': '<div class="key-takeaways"><ul><li>Chrome\'s enhanced autofill, powered by Gemini, now suggests order numbers, tracking details, flight bookings and vehicle details pulled from your Gmail while you fill in web forms.</li><li>It is opt-in and US-only for now: you must use Gemini in Chrome with Personal Intelligence turned on, be 18 or older, and use a personal Google account — work, school and supervised accounts are excluded.</li><li>Suggestions appear under a "Suggested by Gemini" label; removing a suggestion does not delete the email, but deleting the email removes the suggestion.</li><li>To switch it off: Chrome Settings, then Autofill and passwords, then Enhanced autofill, then turn off "Find and fill with Gemini."</li></ul></div>\n<p>Google Chrome can now fill in online forms with details it finds in your Gmail. The enhanced autofill feature, which Google began rolling out in the United States on October 28, surfaces order numbers, tracking information and flight bookings from your inbox at the moment a form asks for them, <a href="https://www.notebookcheck.net/Google-Chrome-autofill-can-now-pull-details-from-your-Gmail.1437131.0.html" target="_blank" rel="noopener">Notebookcheck reported</a>. A traveller checking in for a flight, for example, can pick up the booking code from the confirmation email without leaving the check-in page.</p>\n<p>The feature is powered by Gemini with Personal Intelligence, Google\'s opt-in setting that lets Gemini read connected Google apps such as Gmail. Chrome product manager Amanda Lim announced the rollout on Google\'s Chrome blog, writing that the new suggestions appear "right when you need them," alongside the names, addresses and cards autofill already offered.</p>\n<h2>Who Gets It — and Who Does Not</h2>\n<p>The gate is narrow. Enhanced autofill reaches only people in the US who use Gemini in Chrome with Personal Intelligence switched on, on desktop, Android and iOS. Users must be 18 or older and signed in with a personal Google account with Keep Activity on; work, school and supervised accounts are excluded. People in Europe will not see it for now, because Personal Intelligence is not available in the European Economic Area, Switzerland or the UK.</p>\n\n<h2>How the Suggestions Work</h2>\n<p>When Gemini finds a match in your inbox, the suggestion appears in the autofill dropdown under a "Suggested by Gemini" heading with the Gemini spark icon, <a href="https://www.ghacks.net/2026/10/29/google-chrome-rolls-out-gemini-autofill-that-pulls-order-numbers-and-flight-bookings-from-gmail/" target="_blank" rel="noopener">gHacks reported</a>. On Android, a long press on a suggestion opens two options: view sources, which opens the original email in a new tab so you can verify the details, and remove suggestion, which dismisses the entry without deleting the email. Deleting the underlying email removes the suggestion permanently. Details pulled from Gmail cannot be edited inside Chrome — if a suggestion is wrong, the fix has to happen in the source email.</p>\n<p>Google says sensitive data is encrypted and that users remain in control. The release builds on an earlier upgrade that let autofill draw passport numbers, addresses and other details from Google accounts and Google Wallet, and Google says support for details from images in Google Photos is coming "soon," with no date given. Google first tested the capability in July in its Canary test build under the name "Find and Fill with Gemini"; the public release is narrower and uses Gmail as its only source.</p>\n<h2>The Privacy Trade-Off</h2>\n<p>The convenience is inseparable from the permission behind it: the feature works only because Gemini has been allowed to read your mail. Google\'s own admin documentation notes the feature also handles page content, the page URL and your interactions with suggestions. Readers who opted in to Personal Intelligence for other Gemini features may now find it active in Chrome forms as well — worth a settings check either way.</p>\n<h2>What to Watch Next</h2>\n<p>Google has not announced when enhanced autofill will reach other countries, languages or account types, or when the Google Photos support from the test build will return. For now, eligible US users will see it arrive gradually as the rollout proceeds.</p>\n<div class="related-coverage"><div class="related-coverage-title">Related coverage</div><a class="related-item" href="/articles/isro-nvs-03-launch-success-navic-restored-gslv-f18"><span class="related-item-title">ISRO Launches NVS-03 Successfully, Restoring NavIC to Full Working Strength</span><span class="related-item-meta">Technology · 2026-10-30</span></a><a class="related-item" href="/articles/kla-ai-demand-chip-equipment-2027-semiconductor-growth"><span class="related-item-title">KLA Revenue Jumps 29 Percent as AI Demand Lifts Chip Equipment Market Toward 2027</span><span class="related-item-meta">Technology · 2026-10-30</span></a><a class="related-item" href="/articles/infosys-opens-1-1-million-sq-ft-block-pocharam-hyderabad"><span class="related-item-title">Infosys Opens 1.1 Million Sq Ft Block at Hyderabad Pocharam Campus</span><span class="related-item-meta">Technology · 2026-10-30</span></a></div>', 'image_entities': None}, 'sensex-adds-308-points-nifty-reclaims-23000-second-rally': {'headline': 'Sensex Adds 308 Points as Nifty Reclaims 23,000 in Second Straight Rally', 'slug': 'sensex-adds-308-points-nifty-reclaims-23000-second-rally', 'category': 'markets-finance', 'body': '<div class="key-takeaways"><ul><li>The Sensex closed 308.49 points higher at 74,459.53 and the Nifty rose 116.35 points to 23,053.10 on Friday, a second straight gain that takes the two-day Sensex advance past 1,200 points.</li><li>IT and pharma stocks led the rally: the Nifty IT index rose 2.3% and Nifty Pharma 1.8%, while midcap and smallcap indices fell 0.8% and 1.8%.</li><li>Trent jumped 5.20% after reporting a 25% rise in quarterly net profit to Rs 468 crore; Infosys, InterGlobe Aviation and Tech Mahindra were also among the top gainers.</li><li>For NRI investors, October closed in positive territory after two losing months — the rupee also firmed 33 paise to 94.93 per dollar on Friday.</li></ul></div>\n<p>Indian equity benchmarks extended their rally for a second consecutive session on Friday, October 30, with the Nifty 50 reclaiming the 23,000 mark as buying in information technology and pharmaceutical stocks offset weakness across the broader market. The 30-share BSE Sensex advanced 308.49 points, or 0.42%, to close at 74,459.53, after touching an intraday high of 74,742.59, according to <a href="https://www.thehindubusinessline.com/markets/sensex-nifty50-today-stock-market-highlights-30th-october-2026/article71640574.ece/amp/" target="_blank" rel="noopener">The Hindu BusinessLine\'s market coverage</a>. The NSE Nifty 50 gained 116.35 points, or 0.51%, to settle at 23,053.10.</p>\n<p>Combined with Thursday\'s 905.01-point surge to 74,151.04, the Sensex has added more than 1,200 points in two sessions. The Nifty, which ended Thursday at 22,936.75, has risen nearly 2% over the week.</p>\n<h2>IT and Earnings Did the Heavy Lifting</h2>\n<p>Technology stocks were the day\'s strongest performers as global investors reassessed crowded artificial intelligence trades, improving sentiment toward Indian IT exporters. The Nifty IT index climbed 2.3% and the Nifty Pharma index gained 1.8%. Among individual stocks, Trent was the standout: the Tata Group retailer\'s shares jumped 5.20% after it reported a 25% year-on-year increase in consolidated net profit to Rs 468 crore for the September quarter, with revenue growth and operating leverage supporting earnings, <a href="https://www.thedailyjagran.com/lite/business/news/sensex-up-308-points-nifty-rallies-again-why-market-climbed-for-second-straight-session-10334577" target="_blank" rel="noopener">PTI reported via The Daily Jagran</a>. InterGlobe Aviation, Infosys, NTPC, Power Grid, Eternal, Tech Mahindra and HCL Technologies were also among the major gainers.</p>\n<h2>A Rally Narrower Than the Headlines</h2>\n<p>The advance was concentrated in large caps. The Nifty Midcap index fell about 0.8% and the Nifty Smallcap index dropped about 1.8%, and 11 of the 15 sector gauges compiled by the NSE ended lower, led by a 1.8% fall in consumer durables. Analysts noted the Nifty closed above the 22,800 level and reclaimed its 20-day moving average, with a breakout above 23,250 needed to confirm the next leg. October as a whole was kinder: the benchmarks snapped a two-month losing streak during the month, supported by resilient corporate earnings and expectations of a possible review of long-term capital gains taxation, according to <a href="https://hdfcsky.com/news/market-close-report-today-october-30-2026-nifty-sensex-rise-for-second-straight-session" target="_blank" rel="noopener">HDFC Sky\'s closing report</a>.</p>\n<h2>What It Means for Diaspora Investors</h2>\n<p>For NRIs holding Indian equities through NRE/NRO demat accounts, Friday\'s session paired equity gains with a firmer currency: the rupee rose 33 paise to close at 94.93 against the US dollar. The offsetting risk sits in energy — Brent crude jumped 2.17% to $117.4 a barrel, a level that historically pressures India\'s import bill and the rupee if it holds.</p>\n<h2>What to Watch Next</h2>\n<p>Traders will watch whether the Nifty can clear 23,250, how the remaining September-quarter earnings land, and whether Brent crude sustains above $115. A rally carried by a handful of heavyweights, with midcaps and smallcaps falling, needs broader participation to hold.</p>\n<div class="related-coverage"><div class="related-coverage-title">Related coverage</div><a class="related-item" href="/articles/sensex-surges-905-points-nifty-tops-22900-banking-fmcg"><span class="related-item-title">Sensex Surges 905 Points, Nifty Tops 22,900 as Banking and FMCG Stocks Lead</span><span class="related-item-meta">Markets Finance · 2026-10-29</span></a><a class="related-item" href="/articles/samvat-2082-largecaps-fall-smallcap-multibaggers-diwali"><span class="related-item-title">Samvat 2082 Ends in Red: 83 Large-Caps Fall Up to 60% as Small-Caps Mint Multibaggers</span><span class="related-item-meta">Markets Finance · 2026-10-30</span></a><a class="related-item" href="/articles/anthropic-revenue-14-fold-indian-it-tcs-infosys-hcltech-ai-test"><span class="related-item-title">Anthropic Revenue Jumps 14-Fold; Indian IT Faces AI Test</span><span class="related-item-meta">Markets Finance · 2026-10-29</span></a></div>', 'image_entities': None}}


BAPS = ARTICLES["dallas-baps-mandir-diwali-annakut-fireworks-november-10"]
CHROME = ARTICLES["chrome-autofill-gmail-booking-codes-order-numbers-gemini"]
SENSEX = ARTICLES["sensex-adds-308-points-nifty-reclaims-23000-second-rally"]

NO_DEPICTS = lambda qid: []  # noqa: E731
tmp = tempfile.mkdtemp()
shadow = os.path.join(tmp, "shadow.jsonl")

# ── 1. BAPS: acronym subject survives fragment suppression ──
print("1. BAPS (org acronym subject)")
ents = P.extract_article_entities(BAPS)
by_name = {e["name"]: e for e in ents}
check("BAPS extracted (not eaten by 'BAPS Charities')",
      "BAPS" in by_name, f"got {sorted(by_name)}")
if "BAPS" in by_name:
    check("BAPS tagged headline", by_name["BAPS"]["source"] == "headline")
    check("BAPS keeps the single-token sourceable=False contract "
          "(eligibility comes from curation, not a loosened flag)",
          by_name["BAPS"]["sourceable"] is False)
check("BAPS is a headline subject name",
      "baps" in P.headline_subject_names(BAPS, ents))
subs = vs.headline_subjects(BAPS)
check("verified path subjects lead with BAPS", subs[:1] == ["BAPS"],
      f"got {subs}")
r = vs.decide(BAPS, resolver=vs.registry_only_resolve,
              depicts_fn=NO_DEPICTS, info_fn=None, log_path=shadow)
check("decide: no longer starved (BAPS attempted, decision made)",
      "no headline subject" not in r["reason"]
      and any(a.get("entity") == "BAPS" for a in r["attempts"]),
      f"got {r['reason'][:120]}")

# ── 2. Sensex/Nifty: index names ──────────────────────────────
print("2. Sensex / Nifty (index names)")
ents = P.extract_article_entities(SENSEX)
by_name = {e["name"]: e for e in ents}
check("Sensex extracted as headline entity",
      by_name.get("Sensex", {}).get("source") == "headline",
      f"got {sorted(by_name)}")
check("Nifty extracted (not eaten by 'Nifty Pharma')",
      by_name.get("Nifty", {}).get("source") == "headline",
      f"got {sorted(by_name)}")
subs = vs.headline_subjects(SENSEX)
check("verified path subjects are Sensex then Nifty",
      subs == ["Sensex", "Nifty"], f"got {subs}")
check("headline common nouns 'Points'/'Rally' stay ineligible",
      "Points" not in subs and "Rally" not in subs)
r = vs.decide(SENSEX, resolver=vs.registry_only_resolve,
              depicts_fn=NO_DEPICTS, info_fn=None, log_path=shadow)
check("decide: no longer starved (Sensex attempted, decision made)",
      "no headline subject" not in r["reason"]
      and any(a.get("entity") == "S&P BSE Sensex"
              for a in r["attempts"]),
      f"got {r['reason'][:120]}")

# ── 3. Chrome/Gmail: product names ────────────────────────────
print("3. Chrome / Gmail (product names)")
subs = vs.headline_subjects(CHROME)
check("verified path subjects are Chrome then Gmail",
      subs == ["Chrome", "Gmail"], f"got {subs}")
r = vs.decide(CHROME, resolver=vs.registry_only_resolve,
              depicts_fn=NO_DEPICTS, info_fn=None, log_path=shadow)
check("decide: no longer starved (Chrome attempted, decision made)",
      "no headline subject" not in r["reason"]
      and any(a.get("entity") == "Google Chrome"
              for a in r["attempts"]),
      f"got {r['reason'][:120]}")

# ── 4. Manufactured-identity guards still hold ────────────────
print("4. guards: common nouns never become subjects")
ORD = {"slug": "ord",
       "headline": "Ordering Goes Digital for Delhi Restaurants",
       "body": ("<p>Ordering has moved online across the "
                "capital.</p><p>Digital Ordering grew sharply "
                "this year, and Ordering volumes doubled for "
                "small restaurants.</p>"),
       "image_entities": None}
check("'Ordering' yields no verified subjects",
      vs.headline_subjects(ORD) == [],
      f"got {vs.headline_subjects(ORD)}")
PROFIT = {"slug": "profit",
          "headline": "Profit Jumps 40 Percent for Delhi "
                      "Traders in Festive Quarter",
          "body": ("<p>Profit rose sharply for small traders "
                   "across the capital this quarter.</p>"
                   "<p>Higher Profit margins were reported by "
                   "wholesale markets, and Profit growth is "
                   "expected to continue into the new year.</p>"),
          "image_entities": None}
check("'Profit' yields no verified subjects",
      vs.headline_subjects(PROFIT) == [],
      f"got {vs.headline_subjects(PROFIT)}")
calls = []
r = vs.decide(PROFIT, resolver=lambda n, c: calls.append(n),
              depicts_fn=NO_DEPICTS, info_fn=None, log_path=shadow)
check("'Profit' is never sent to the resolver",
      calls == [] and r["decision"] == "none", f"calls: {calls}")

# ── 5. Suppression still applies when the superset is the
#       headline's own fuller name ─────────────────────────────
print("5. guards: fragment suppression intact for headline names")
AAMIR = {"slug": "aamir",
         "headline": "Aamir Khan Announces New Film With "
                     "Rajkumar Hirani",
         "body": ("<p>Aamir Khan will headline the project, "
                  "the actor's first with the director in a "
                  "decade.</p><p>Aamir spoke about the film at "
                  "a Mumbai event on Tuesday, where Aamir Khan "
                  "also confirmed the schedule.</p>"),
         "image_entities": None}
names = [e["name"] for e in P.extract_article_entities(AAMIR)]
check("bare 'Aamir' still suppressed inside 'Aamir Khan'",
      "Aamir" not in names and "Aamir Khan" in names,
      f"got {names}")
MANN = {"slug": "mann",
        "headline": "Mann Ki Baat: PM Modi Addresses Nation "
                    "on Festivals",
        "body": ("<p>Mann Ki Baat reached its latest edition "
                 "on Sunday.</p><p>The Mann Ki Baat broadcast "
                 "covered festivals and Mann references in "
                 "listener letters.</p>"),
        "image_entities": None}
names = [e["name"] for e in P.extract_article_entities(MANN)]
check("bare 'Mann' still suppressed inside 'Mann Ki Baat'",
      "Mann" not in names, f"got {names}")

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("ALL CHECKS PASSED")
