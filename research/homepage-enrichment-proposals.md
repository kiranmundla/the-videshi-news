# Homepage Enrichment Proposals

**Date:** 2026-10-11
**Scope:** 40 unique articles on the homepage feed (generated 2026-10-11 15:49 UTC)
**Method:** Full-body audit of all 40 articles by 4 research agents, evaluating missing context, actionable info, data visualization, social embeds, structured data, diaspora angle, and depth.

---

## Executive summary

The articles are well-written (avg 744 words, professional tone, data cards on 34/40). But they systematically stop one step short of *useful*. The same gaps repeat across categories:

1. **`social_embeds` is empty on 39 of 40 articles** — yet many paste bare X/YouTube URLs inline in the body as dead text links. The pipeline finds the right social content and then fails to embed it. This is a pipeline bug, not an editorial choice.
2. **Timeline data cards are hallucinating years** — the Nepal flood, IRGC tanker, and Rashid Khan cards label 2026 events as 2023. A wrong-year card on a disaster article is a credibility landmine. This needs an immediate guardrail.
3. **Data cards are sometimes decorative, not informative** — "Largest IPO in India: 1", "Key heritage sites: 2", artist mention-counts, three cards all saying "3.0". Cards need a content rule: no card unless it carries numbers the reader can't get from the headline.
4. **Utility articles lack the links that make them usable** — travel pieces with no booking links, immigration pieces with no application pages, finance pieces with no NRI account mechanics. Every actionable article should ship with a named-links box.
5. **Diaspora sections are emotional, not actionable** — "strikes a chord," "followed closely" — but rarely answer "what do I *do*?" The template should require one actionable sentence.

---

## Quick wins (pipeline-automatable)

These can be built into the pipeline without changing the writer's job:

### 1. Promote inline social URLs to `social_embeds` (HIGH PRIORITY)
**Problem:** 6+ articles paste bare `x.com/...` or `youtube.com/watch?...` URLs inline in the body instead of structured embeds. The enricher should extract these automatically.
**Fix:** In `enrich-on-publish.py` (or a post-writer pass): regex-scan body HTML for `x.com/<user>/status/<id>`, `youtube.com/watch?v=<id>`, `youtu.be/<id>` and register them in `social_embeds`. The structured data already exists in the HTML — it's just not in the metadata the frontend consumes.
**Articles affected:** australia-clinch-odi-series (cricket.com.au tweet), blade-runner-2099 (RottenTomatoes post + trailer URL), canada-fast-track (achev_ca post), ganesh-dust-to-stardust (Sumit Kadel post + trailer), gulshan-devaiah (trailer), hud-fha-loans (GuntherEagleman post), icc-odi-world-cup-2027 (YouTube embed), india-bloc (PTI_News post), india-space-startups (YouTube embed), mandaadi (trailer URL), irgc-supertanker (FaytuksNetwork post).

### 2. Timeline card date guardrail (CRITICAL — data quality bug)
**Problem:** The timeline-card generator labels 2026 events as 2023 (Nepal flood, IRGC tanker, Rashid Khan dinner). It appears to infer years from text instead of anchoring to `published_at`.
**Fix:** In the card generator: any timeline date must be within ±18 months of the article's `published_at`, or the card is rejected / the year is forced from context. Never ship a timeline card with a year the article's own body contradicts.
**Articles affected:** nepal-gorkha-flash-flood, irgc-says-supertanker, rashid-khan-hosts-pathan-brothers.

### 3. Data-card content QA rule
**Problem:** Cards ship with placeholder values ("1", "2"), single-item "highlights" cards, and comparison cards for non-comparative content (academic journey, collaborator lists, tribute quotes).
**Fix:** Generation guardrails:
- Reject stat values that are bare integers 1–5 with no unit/context.
- Reject comparison cards with fewer than 2 genuinely comparable rows.
- Reject single-item cards (merge the fact into the body instead).
- Card-type routing: biographical data → timeline; lists → highlights/chips; quotes → quote cards; never comparison-by-default.

### 4. Mandatory action-link check
**Problem:** Utility articles routinely end without a single actionable link.
**Fix:** Writer/enricher pass: every article tagged as actionable (travel, immigration, finance, health, food) must contain ≥1 authoritative outbound link (booking page, application page, government source, ticket link). Flag articles that fail the check for the writer to fix.
**Articles affected:** sai-kung fireworks (no venue link), sri-lanka itinerary (no hotel/ETA links), lucknow heritage home (no reel/walk/homestay links), air-india student discount (no fare-page link), nri-quantum-challenge (no WISER link), hpv-vaccine (no CDC link), hud-fha-loans (no Mortgagee Letter link), icc-world-cup-2027 (no ballot URL), jio-ipo (no NRI application specifics).

### 5. Auto-generate sports scorecards
**Problem:** Match reports (cricket) have no scorecard — the most basic structured component for sports.
**Fix:** Now building: `match_scorecard` structured field + frontend component. Writer populates teams, scores, result, top performers for every match-result article. (In progress as of 2026-10-11.)
**Articles affected:** australia-clinch-odi-series, ravichandran-ashwin-blasts, icc-odi-world-cup-2027 (fixtures, not results).

### 6. Register in-body YouTube embeds in `social_embeds`
**Problem:** `<youtube>` tags render as players in-body but are never registered in the structured field the frontend may consume for carousels/embeds sections.
**Fix:** Same pass as #1 — extract `<youtube>VIDEO_ID</youtube>` tags into `social_embeds`.
**Articles affected:** gulshan-devaiah, icc-odi-world-cup-2027, india-space-startups.

---

## New component ideas

These are new UI elements worth building, modeled on the match-scorecard pattern:

### A. "Key dates" box (immigration, policy, IPO)
Structured date lists for deadline-driven stories. Fields: date, event, source link.
*Use for:* federal-court D/S injunction (July 17 rule → Sept 14 injunction → Sept 30 appeal → First Circuit decision), Jio IPO (Oct 19 anchor → Oct 21–23 public → Oct 28 listing), Navratri 9-day goddess/color calendar, Sai Kung Diwali season (Oct 20 Diwali → Oct 29–Nov 1 Wine & Dine → Nov 7 fireworks).

### B. "NRI how-to" box (markets-finance, immigration)
Account type → broker/platform → regulator link. Reusable across finance stories.
*Use for:* jio-ipo (NRE/NRO demat, ASBA, NRI quota mechanics, US-tax note), japan-FDI (NRE/NRO + PIS, Gift City funds, RBI FEMA page), hud-fha-loans (eligibility-by-status table: citizen/green-card/H-1B/OPT/DACA → FHA vs conventional vs non-QM).

### C. "Eligibility checklist" card (immigration, programs)
Checkbox-style requirements with the "catch" called out.
*Use for:* canada-fast-track (PR/citizen, Touchstone assessment, 3-year return-of-service, certification exam), air-india student discount (age 12+, enrollment ≥1yr, documents), nri-return-india (visa backup, OCI, school timelines, insurance portability).

### D. "Get the look / where to buy" card (lifestyle, food)
Three price tiers with named retailers and links.
*Use for:* triptii-dimri sari (designer → diaspora boutiques with addresses → online with shipping buffers), modi-cheeses (pairing + where-to-buy box), modern-indian-food (metro-wise restaurant list with booking links).

### E. Recipe card (food, lifestyle-health)
Ingredients with quantities, method, yield, storage. The ginger-turmeric article gives method with no amounts — currently not a usable recipe.
*Use for:* ginger-turmeric-tea, plus any future recipe content.

### F. "Story so far" developing-story block (news)
Chronological event list for running stories. (Already an open follow-up from 2026-10-07.)
*Use for:* india-bloc march (Oct 6 → Oct 7–8 → Oct 10 → Oct 12), IRGC tanker incident.

### G. Price-comparison table (travel, markets)
Side-by-side cost breakdowns.
*Use for:* air-india student discount (savings-stacking: base −10% −50% fee −₹1,000 UPI), Starlink vs Indian broadband ARPU, sri-lanka itinerary per-day costs with running total.

### H. "Migrant founder playbook" (nri-world profiles)
Distilled steps from founder stories. Reusable template.
*Use for:* indian-founder-australia (ABN/ASIC/VEVO/business.gov.au links), future founder profiles.

### I. Critic-by-critic table (entertainment reviews)
Publication → critic → rating → one-line verdict. Per the 2026-10-09 review bar (named critics, specific scenes).
*Use for:* mandaadi review (currently "12 reviews averaging 3.0" with zero named critics — violates the standing bar).

### J. Film-info card on reviews (entertainment)
Extend the existing trailer-brief film-info/cast-strip standard to reviews.
*Use for:* mandaadi (replace three redundant "3.0" cards), gulshan-devaiah / Little Thomas (release Oct 23, cast, booking links).

---

## Editorial guidelines (writer instructions)

Add to `V3-WRITER-INSTRUCTIONS.md`:

1. **One actionable sentence in every diaspora section.** Not "this strikes a chord" — name the link, the form, the number, the store. If the diaspora angle can't produce one action, cut the section.
2. **Utility articles ship with a named-links box.** Travel → booking/ETA/visa links. Immigration → application/government pages. Finance → account/broker/regulator links. Health → CDC/schedule pages. No exceptions.
3. **Social embeds are not optional for social-native stories.** If the story IS a post (Irfan Pathan's X post, Musk's X posts, a founder's announcement, an Instagram reel tour), the embed is the article's primary source — find it at write time, don't rely on the 4-hour enricher window. (The Rashid Khan article's Oct 9 tweet was missed because the enricher only checks 4h back.)
4. **Quantify the thesis.** Quote pieces asserting a trend (Gulshan's "illusion," IMC's "ambition") need one data section that adjudicates the claim — a genre-split table, a demo count, a flown-vs-planned list.
5. **Name the mechanism.** Policy stories must unpack the mechanism in one paragraph: SHANTI Act = supplier-liability clause repeal; SIR = electoral-roll revision mechanics; D/S = program-length admission vs fixed caps. Never name-drop an acronym the reader can't act on.
6. **Absolute risk, not just relative.** Health articles: convert relative reductions to percentage points against the baseline rate. One sentence of arithmetic.
7. **Verify single-source stories.** Any story built on one wire release gets an explicit verification attempt (registry lookup, named client, or a stated "couldn't verify" note) — not just honest caveating.
8. **Balance developing stories.** Opposition-wire stories (india-bloc) need the other side's response (ECI's SIR defense) in the same article. One paragraph minimum.
9. **Trailer articles: franchise primer + cast + diaspora watch path.** Blade Runner 2099 named no cast and no franchise continuity. Every trailer piece: what came before (one paragraph), who's in it, where the diaspora reader watches it.
10. **In-body deep links to our own explainers.** The NRI-return article's TDS advice should link the site's TDS article; the Sri Lanka piece should link the codeshare piece. Free engagement — do it at write time.

---

## Per-article suggestions (top priorities)

### news
- **nepal-gorkha-flash-flood** — FIX timeline card years (2023→2026). Add donation block (Nepal Red Cross, NDRRMA), "checking on family" helpline paragraph, landslide-dam explainer. Move Mario Nawfal X link to proper embed or replace with @NepalArmy/ANI footage.
- **india-bloc-to-march** — Add SIR explainer paragraph (the acronym currently has no footing), ECI's defense (balance), Form 6A / ECI voter-portal links for diaspora families, Rahul Gandhi's X post embed, key-players card. Ideal candidate for "story so far" block.
- **irgc-supertanker** — FIX timeline card years. Replace misleading casualty stat with market-impact numbers (barrels aboard, strait share, Brent move). Add "key facts" box (vessel unknown, two conflicting reports), IRGC/UKMTO jargon decoder, IndianOil price page + DG Shipping advisory links, remittance-timing one-liner.
- **happening-navratri-begins** — Thin (273 words, 0 sources). Add 9-day goddess/color timeline card, nine-forms + regional-split explainer (garba vs Durga Puja vs Ramlila), ticket links per temple listing (standing events rule), US fasting-food sourcing + kids' garba workshops.

### nri-world
- **nri-return-india** — No data cards at all. Add "Before you move back" checklist (visa backup, OCI, school timelines, insurance, TDS link to our own article), re-entry-shock psychology paragraph, returnee-months timeline visual (1–3 honeymoon → 6–9 low → 12–18 integrate), embed the actual Reddit thread, name the platforms (r/ReturningToIndia, Meetup).
- **nri-students-quantum** — Add quantum-computing plain-English paragraph, WISER/NRI Institute/Amaravati Quantum Valley application links, 3-sentence THRINETRA technical explainer, move Owen Gregorian X link to embed, add 200-student cohort stat to funnel card.
- **indian-founder-australia** — Single AB Newswire source; attempt ASIC verification. Add migrant-business checklist (ABN/ASIC/VEVO/business.gov.au links), journey timeline card, Yatin Jindal LinkedIn embed, US visa-route mapping (E-2/EB-5/O-1).
- **angaraj-duara-nasa** — Convert Academic Journey comparison card → timeline. Add HWO telescope-lineage paragraph (Hubble→Webb→Roman→HWO), phone-sensor vs detector stat comparison, Open University/UKSA/NASA HWO links, NASA internships link for STEM families, his BBC/LinkedIn media embed.

### immigration
- **federal-court-D/S** — Add "key dates" box (July 17 → Sept 14 → Sept 30 → First Circuit), old-vs-blocked rule comparison table, student checklist (i94.cbp.dhs.gov, DSO/NAFSA advisory, court opinion link), Presidents' Alliance/NAFSA embed, contingency paragraph (what if the government wins the appeal), university ISSS guidance links.
- **hud-fha-loans** — Best article in its batch; needs utility layer: Mortgagee Letter 2025-09 (hud.gov) + Fannie Mae eligibility links, eligibility-by-status table, policy timeline visual (Mar 26 → May 25 → stampede → near-zero), HUD Secretary announcement embed, state down-payment programs for visa holders, conventional/non-QM cost numbers.
- **canada-fast-track** — Add application-steps box (PRO program page, Touchstone Institute, Health Canada, federal PR pathway), eligibility checklist card with return-of-service callout, PRO-vs-traditional comparison (<1yr vs 3–5yr), achev_ca X embed, US-physician comparison (USMLE grind), intake-competitiveness paragraph.

### markets-finance
- **jio-ipo** — Add NRI application checklist (NRE/NRO demat, PAN, ASBA, lot size ~₹14,547, dates Oct 19→21–23→28), NRI quota mechanics box (repatriation vs non-repatriation), US-tax note (DTAA/FBAR), listing-day precedent (Hyundai Motor India Oct 2024), expectations-vs-pricing bar visual, grey-market premium sourcing, Reliance/Jio X announcement embed.
- **japan-FDI** — Add treaty-routing glossary (Singapore/Mauritius), NRI investor playbook (NRE/NRO+PIS, Gift City, RBI FEMA page, Zerodha NRI), YoY swing chart + Tamil Nadu mini-table, @PiyushGoyal X post embed, manufacturing-FDI section (the actual missing number), US-capital-pullback portfolio note.
- **musk-starlink** — Embed the actual @elonmusk Oct 11 X posts (the story's primary sources). Replace weak cards with Starlink-vs-Indian-broadband price table, feud timeline (2024 spectrum fight → clearance limbo → Oct 11 posts → Jio IPO), 2024 spectrum-fight explainer, starlink.com notify-me + Jio IPO cross-link, US pricing calibration, affordability-math section (Kenya precedent).
- **india-nuclear-30gw** — Add SHANTI Act mechanism paragraph (supplier-liability repeal), DAE consultation link, capacity-ramp chart (8.78→22→100 GW), policy timeline box, @PIB_India/DAE X embed, Indo-US 123 Agreement hook, SMR section expansion.

### sports
- **australia-clinch-odi** — Add match scorecard box (BAN 220/6 vs AUS 222/1, 9 wickets, 2-0). Convert inline cricket.com.au X URL to embed + highlights video. Add "records broken in one night" stat card, 3rd ODI date/venue/US watch info (Willow TV/ESPN+, ET/PT), WPL auction angle.
- **ashwin-blasts** — Add mini scorecard card, embed the "Ash ki Baat" YouTube segment (the article reacts to a video the reader can't watch), remaining T20I fixtures + US watch info, Samson-vs-Hosein ball-by-ball visual, IPL auction angle for Hope.
- **icc-world-cup-2027** — Move format-change explainer up top, add ICC ballot URL + Willow TV/ESPN+ verification + calendar download, venue map (12 venues), key-dates box, ticket-economics section, @ICC/@BCCI announcement embed.
- **nz-recall** — Replace vapid "Key Players" card with split-squad roster card (ODIs 1–3 vs 4–5). Add full 5-ODI fixtures + NZC ticket link + broadcast times, head-to-head mini-card, @BLACKCAPS announcement embed, Test-leg overlap analysis.

### technology
- **deepinder-goyal-temple** — Replace Collaborators comparison card with price-positioning table (Temple ~$900 vs Apple Watch Ultra vs Oura vs Whoop). Add spec-sheet card, Temple waitlist link + US availability/FDA status, Goyal X posts + Raj Shamani clip + Sindhu IG embeds, clinician-credibility paragraph (peer-review bar, n=60 caveat).
- **nasa-curiosity** — Replace apples-to-oranges card with 14-year mission timeline. Add blue-sunrise physics explainer (the article's most shareable fact, currently unexplained), sol definition, full-res panorama links (JPL Photojournal), mission-at-a-glance box, @MarsCuriosity X embed, Ashwin Vasavada Indian-American hook, yardang-puzzle detective section.
- **india-mobile-congress** — Thinnest substantive tech article (single ET source, no product names). Add IMC scale/context paragraph, key-announcements box (1B 5G, 6G patents, agri-AI, semiconductors), 2–3 actual demos, @IndiaMobileCong embed, US-reader travel angle (5G roaming).
- **india-space-startups** — Replace weak comparison card with company matrix (Digantara/GalaxEye/Agnikul/Skyroot/Pixxel × focus × milestone). Add IN-SPACe/2020-reforms paragraph, startup directory table, IN-SPACe + careers links, FDI policy verification flag, flown-vs-planned reality check, in-body YouTube → social_embeds.

### entertainment
- **mandaadi-review** — Violates the 2026-10-09 review bar (no named critics, no scenes). Consolidate three "3.0" cards into one film-info card with cast strip, add critic-by-critic table (TOI/Rediff/Cinema Express scores + pull-quotes), named scenes, Soori background paragraph, vallam-culture explainer, where-to-watch (BookMyShow + US Tamil-theater listings), trailer embed from bare URL.
- **amitabh-bachchan-84** — Replace "Tributes" comparison card with career-milestones timeline. Embed the actual tribute posts (Kajol IG, Kamal Haasan, Sanjay Dutt) instead of paraphrasing, link scholarship details (Lotus Foundation/Anand Pandit), add US watch-list (SonyLIV US, Prime/Netflix classics, Kalki 2 window), expand birthday-philanthropy thread.
- **ganesh-dust-to-stardust** — Replace one-item card with full film-info card + cast strip. Convert bare YouTube/X URLs to embeds, add Akshay/Ajay trailer-share embeds, "songs that made him" card, BookMyShow + US theatrical/streaming note, self-directed-biopic angle.
- **blade-runner-2099** — Stub (108 words). Needs full trailer-article treatment: film-info card (limited series, Nov 25, Prime Video, cast/creators), franchise primer (1982→2049→2099), NYCC expansion, RottenTomatoes X + trailer embeds, Prime Video watchlist link, Indian/diaspora connection check (standing bar).
- **gulshan-devaiah** — Add genre-labeled table of 2024–25 top Hindi grossers to test the "illusion" thesis, name the "violence wave" films, film-info card for Little Thomas (Oct 23, dir. Kaushal Oza), BookMyShow + US theatrical note, register in-body YouTube in social_embeds, Devaiah's own announcement post.

### lifestyle-health
- **ginger-turmeric-tea** — Add quantities to make it a real recipe (currently method-only), printable recipe card (ingredients/method/yield/storage), ritucharya concept paragraph, curcumin dose-vs-trial honesty, Patel Brothers locator + freezer tip, credentialed-creator reel embed, flu-season framing.
- **triptii-dimri-sari** — Replace mood-board card with three-price-point "get the look" card (designer → diaspora boutiques with addresses → online + shipping buffers). Link Myntra Utsav edit + Vogue India + ANI video, embed Triptii's IG post + stylist post, "style the look" checklist card, crystal-sari packing guide (tissue-roll, carry-on), US Diwali dress-code calibration.
- **navratri-bhajans** — Strongest in batch; needs playable surface: embed the JioSaavn playlists it cites as buttons + YouTube/Spotify equivalents, replace mention-count card with 9-day listening-plan card (day ↔ goddess ↔ track), morning-aarti checklist box, romanized-lyrics bridge for the Sanskrit stotras, US temple livestream links, official video embed (Jubin Nautiyal/T-Series).
- **hpv-vaccine** — Add numbers-at-a-glance card (aOR 0.95/0.85/0.93/0.92), "what to do by age" box (US CDC vs India schedule columns), CDC + India immunization-schedule links, BMJ/Karolinska X embed, absolute-risk translation (baseline → percentage points), Vaccines-for-Children cost note.

### food
- **rashid-khan-feast** — FIX timeline card (2023→2026, drop filler). Embed @IrfanPathan's Oct 9 post (the story's primary source — highest-value single embed in the audit). Add Dubai Afghan restaurant names + Maps/Zomato links, dish-by-dish mini-table (mantu/aushak/firni explained), kabuli pulao recipe link, US "Little Kabul" corridors (Fremont/Artesia), Layloma human-interest sentence.
- **modi-cheeses** — Add where-to-buy box (Eleftheria shop, Nature's Basket/Foodhall verification, honest US-availability caveat), pairing card (Gulmarg→hot honey, Konark→fondue, Yeoor→baked), Eleftheria IG announcement embed, Modi food-diplomacy history paragraph, India's artisan-cheese scene mini-directory.
- **modern-indian-food** — Replace cuisine-numbering card with chefs-&-books card (Mehrotra, Gaggan, Zacharias, Pandya, Ved). Add metro-wise restaurant list with booking links (NYC Adda/Dhamaka, Edison, Bay Area, London), chef IG embeds (Zacharias, Bombay Canteen), Gaggan molecular-era explainer, skeptic's-take paragraph, home-cook recipe links.
- **sai-kung-fireworks** — Thinnest in batch; restaurant unnamed. Name it + booking link when confirmed; link Sai Kung Buzz issue page meanwhile. Add HK Indian-community background, fireworks-permit context, "Diwali season in HK" event box, @saikungbuzz IG/FB announcement embed, date-map timeline card, "how HK does Diwali" reported paragraph.

### travel
- **air-india-surcharges** — Add "what to do now" box (existing bookings unaffected; check fare breakdown), route-impact table (DEL–BOM +₹800–1,200, DEL–LHR +~$270, JFK–DEL +$430), Air India/Akasa X announcement embeds, US-reader callout ($430 round-trip surcharge), surcharge reversibility paragraph.
- **air-india-student** — Add savings-stacking table (base −10% −50% fee −₹1,000 UPI), direct student-fare page link, eligibility checklist box, Air India Express comparison, @airindia X announcement embed, free-date-change diaspora hook (worth more than 10% on US sectors), IndiGo/Akasa student-fare comparison.
- **lucknow-heritage-home** — Kill junk stat card; replace with 2-day slow-Lucknow itinerary. Embed the original Instagram reel (non-negotiable — the article tours a reel), add heritage-walk + homestay booking links, UP Tourism link, 1949-Lucknow context paragraph, NRI ancestral-property restoration guide (craftspeople, INTACH, caretaker services, cost per sq ft).
- **sri-lanka-itinerary** — Replace incoherent budget card with per-day cost table + trip total. Add where-to-stay box (Talpe/Ahangama/Weligama picks + rates + Booking.com/Agoda links), eta.gov.lk + train/transfer booking links, October weather/expectations paragraph, vlogger video + IG swing-spot embeds, diaspora frame (India→Colombo flights, Diwali-week window, US-Indian add-on trip).

---

## Bugs to fix immediately

1. **Timeline cards hallucinating years** (2023 for 2026 events) — nepal flood, IRGC tanker, Rashid Khan. Add date guardrail vs `published_at`.
2. **`social_embeds` empty while inline URLs exist** — 11+ articles. Add URL-promotion pass to enricher.
3. **Junk stat values in generated cards** — "1", "2", single-item cards, comparison-for-lists. Add generation guardrails.
4. **Mandaadi review violates the 2026-10-09 review bar** — no named critics/scenes. The review-roundup generator needs the same prompt constraints as auto-reviews.
5. **Navratri happening-brief ships with 0 sources** — even briefs need 1–2 source links for listing verifiability.
6. **Blade Runner 2099 is a 108-word stub** — below the bar for a published article; needs the full trailer-article treatment or shouldn't be on the homepage.

---

## What "useful" looks like — the pattern

The best enrichment in this audit shares one shape: **it answers the reader's next question, not the one just answered.**

- The article says surcharges rose → the reader asks "what do I pay on MY route?" → route-impact table.
- The article says Temple costs ₹75,000 → the reader asks "vs what?" → price-positioning table.
- The article says Jio IPO is NRI-accessible → the reader asks "how do I apply?" → NRI checklist with account types.
- The article says the rule is blocked → the student asks "what do I do Monday?" → i94 check + DSO advisory + contingency plan.
- The article describes a sari → the reader asks "where do I buy it?" → three price tiers with links.
- The article tours a reel → the reader asks "show me" → the actual embed.

Every article should end with the reader able to DO something they couldn't do before reading. That's the bar.
