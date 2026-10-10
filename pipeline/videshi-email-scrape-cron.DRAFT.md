# Directory Email Scrape — daily batch
# DRAFT cron definition (not scheduled yet). To enable: cron.add with id
# `videshi-email-scrape`, schedule daily@03:00:00 America/Los_Angeles,
# owner goal:videshi-migration, and the body below.

Scrape contact emails from directory listing websites for future advertising outreach.

## Schedule
Daily at 3:00 AM America/Los_Angeles. Processes up to 200 sites per run (~7 min at 2s/site).

## Instructions

```bash
cd ~/workspace/the-videshi-news/pipeline
set -a; source ~/workspace/.env.supabase; set +a
python3 -u scrape-listing-emails.py --limit 200 --apply
```

## Behavior
- Resumes from checkpoint in `pipeline/.state/email-scrape-progress.json` — never re-scrapes a site.
- Visits homepage, then /contact, /contact-us, /about until an email is found.
- Identifies as `TheVideshi-Bot/1.0`, 2s delay between sites, 15s page timeout.
- Filters garbage (example.com, noreply@, image filenames); prefers info@/contact@/hello@.
- Writes found emails to the `email` column of `directory_listings`.
- Dry-run by default; `--apply` writes to DB.

## Completion
- ~4,435 listings have websites. At 200/run/day, the initial pass takes ~22 days.
- When a run processes 0 sites, the initial pass is done — the job can be left enabled (it will exit quietly) or disabled.

## Cost
Zero API cost — plain HTTP fetches. Only cost is VM time (~7 min/day).

## Reporting
Routine success is silent. Report only genuine errors: Supabase write failures, or 0 sites processed on consecutive days while the checkpoint shows sites remain.
