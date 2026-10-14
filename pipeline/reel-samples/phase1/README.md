# Phase 1 reel + carousel samples (LOCAL ONLY — nothing uploaded)

Produced by the Phase 1 production pipeline (reel_renderer.py +
reel_factcheck.py + reel_frame_qa.py, driven by reel_produce.py;
carousel_render.py for the carousel set). Both reel crons remained
disabled throughout; no sample was uploaded or marked ready in
prebuilt_reels. "ready" in a verdict.json is a LOCAL sample status.

## Reel samples

| Dir | Article type | Composition exercised |
|---|---|---|
| sukanya-chakrabarti-american-physical-society-fellow-dark-matter | clear face photo (2000×1336) | cover-fill |
| indian-american-republicans-h-1b-backlash-ballot-2026 | tight close-up (2348×3128, face 62% chin) | dark-stage fit fallback |
| cracker-prices-rise-15-20-percent-diwali-sivakasi-production-falls | non-face photo (1280×853) | cover-fill, heuristic focal box |

Each dir: article.json (the source article row), script.json (the
reel script — for the H-1B sample this is the generator's own
pulse-stats output, reused as-is), output/ with the MP4,
render-manifest.json, factcheck-report.json, qa-report.json +
qa/frames/*.png (one frame grab per text beat), verdict.json.

## Negative tests

- negative-wrong-fact/ — the Sukanya script with three planted errors
  (name "Sukanya Chatterjee", stat "12%", year "2029"). The
  fact-check gate must HOLD it; see its factcheck report.
- Over-long line — covered by test_reel_gates.py (measured fit
  raises TextFitError instead of shipping cropped text).

## Carousel sample

sukanya-...-dark-matter/carousel/ — 4 cards at 1080×1350
(carousel-<slug>-1..4.png): cover, verbatim-quote card (speaker photo
= the article's verified hero), key-facts card, end card carrying
THIS story's headline. Gates: carousel-factcheck.json (verbatim
quote verified as a substring of the article body + full claim gate)
and carousel-qa.json (computed margins/contrast/face checks).

## Reproduce

    set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; set +a
    cd pipeline
    python3 -u reel_produce.py --slug <slug> --script <dir>/script.json \
        --article-file <dir>/article.json --outdir <dir>/output
    python3 -u carousel_render.py --spec <dir>/carousel-spec.json \
        --article <dir>/article.json --hero <dir>/output/hero.jpg \
        --outdir <dir>/carousel
    python3 -u test_reel_gates.py
