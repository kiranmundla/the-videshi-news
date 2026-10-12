# Image Source Validation — Batch 3
**Date:** 2026-10-11
**Rule:** Validate before building. No implementation until Kiran approves.

## Source 1: Openverse (api.openverse.org) — ❌ REJECTED

**What was tested:** Searched `diwali celebration`, `mumbai skyline`, `cricket stadium`, `taj mahal`, `yoga` with `license=cc0,pdm` filter. No API key needed. Filter works, result counts healthy (25–240).

**Why rejected:** Openverse's CC0 results for India-relevant queries are **80–100% Flickr-sourced**, and `live.staticflickr.com` returns **"Rate limited - CIDR range blocked"** from our server — the entire Flickr pool is unreachable from this box. The remaining results are Wikimedia, which we already source directly. Openverse adds nothing new beyond our existing chain.

**Could revisit if:** Flickr unblocks our IP range, or we route downloads through a different egress.

## Source 2: Pixabay API — ⚠️ CONDITIONAL (needs Kiran's free signup)

**What was tested:** API docs at pixabay.com/api/docs/. Confirmed: free key via instant signup (no approval step per docs), 100 requests/min, royalty-free under Pixabay Content License, `largeImageURL` at 1280px (passes our 800px bar).

**Why conditional:** An API key requires account signup with email verification — cannot be done by the agent. Image quality could not be validated without a key.

**Next step for Kiran:** Sign up at pixabay.com/api/docs/ (free, ~2 min), paste the key. Then a 10-minute test validates quality on 3 articles. This is also the Pexels insurance policy — Pexels paused new key issuance, so if our Pexels key dies we lose the last-resort fallback.

## Source 3: Kerala Tourism — ❌ REJECTED (copyright)

**What was tested:** Copyright terms checked FIRST per the Incredible India lesson.

**Terms found** (keralatourism.org/copyright): *"All rights reserved. No part of this website may be reproduced... without the written permission of the publisher and copyright owner. No photographs or parts of photographs that appear in this site may be reproduced in any form... "*

**Why rejected:** Same trap as Incredible India — requires written permission. Image quality was never evaluated because copyright fails first.

**Path forward:** Same as Incredible India — Kiran could write for blanket editorial permission. Two permission emails (Incredible India already sent 2026-10-11) could unlock both.

## Source 4: PMO copyright check — ✅ VIABLE

**Copyright policy** (pmindia.gov.in/en/website-policies/):

> *"Material featured on this website may be reproduced free of charge. However, the material has to be reproduced accurately and not to be used in a derogatory manner or in a misleading context. Wherever the material is being published or issued to others, the source must be prominently acknowledged."*

**This is the standard GOI open-copyright policy — free reproduction with attribution. No written permission needed.** Clear contrast with Incredible India / Kerala Tourism.

**Bonus discovery:** PMO has a dedicated photo gallery at pmindia.gov.in/en/image-gallery/ with dated filenames (e.g. `H20261011218043.jpg` = 2026-10-11 event). Test download: **2200×1467**, professional quality. The gallery is easier to automate than scraping news pages — filenames encode dates, making freshness matching straightforward.

**Verdict:** PMO is cleared for build whenever Kiran approves. Attribution required: "PMO India" / "pmindia.gov.in".

## Summary

| Source | Verdict | Blocker |
|--------|---------|---------|
| Openverse | ❌ Rejected | Flickr IP-blocked from our server; rest is Wikimedia dupes |
| Pixabay | ⚠️ Conditional | Needs Kiran's free API key signup |
| Kerala Tourism | ❌ Rejected | All-rights-reserved copyright |
| PMO | ✅ Viable | None — free with attribution |

## Updated strategy impact

- **Build-ready:** PMO (copyright cleared, gallery automation path found)
- **Awaiting Kiran:** Pixabay API key (2-min signup)
- **Awaiting permission emails:** Incredible India (sent), Kerala Tourism (not yet requested)
- **Dropped:** Openverse, PIB, brand press kits, diaspora orgs, LoC

No code was written. No images were changed. Validation only.
