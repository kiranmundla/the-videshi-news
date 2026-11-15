"""Tests: reviewer source-provenance flag (2026-11-15).

Keeper case: the Air India non-stop restoration article — an
announcement story whose three sources were a trade blog plus ANI
and Hindustan Times stories republished on unrelated aggregator
domains; the airline's own announcement was never cited.
check_source_provenance must flag it, and must stay silent when a
wire/originator/primary source is present or the story is not
announcement-driven.

Run: python3 test_source_provenance.py  (exit 0 = all pass)
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "review_articles", os.path.join(HERE, "review-articles.py"))
rev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rev)

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


AI = {
    "headline": "Air India Restores Non-Stop Flights to New York",
    "body": "<p>In a statement on Sunday, the airline said flights "
            "that took around 22 hours will now take 17 hours.</p>",
    "sources": [
        {"name": "Safari India",
         "url": "https://safariindia.com/air-india-restores/"},
        {"name": "ANI",
         "url": "https://apnamatvchannel.com/business/air-india/"},
        {"name": "Hindustan Times",
         "url": "https://www.prudigitalmedia.com/india-news/x"},
    ],
}

# 1. The keeper: aggregator-only sources on an announcement story.
f = rev.check_source_provenance(AI)
check("Air India sources flagged", len(f) == 1)
check("flag names the domains",
      any("prudigitalmedia.com" in x for x in f))

# 2. Adding the wire on its own domain clears the flag.
ai2 = {**AI, "sources": AI["sources"] + [
    {"name": "PTI", "url": "https://www.ptinews.com/story/x"}]}
check("PTI source clears the flag",
      rev.check_source_provenance(ai2) == [])

# 3. A primary outlet on its own domain clears the flag.
ai3 = {**AI, "sources": [
    {"name": "Hindustan Times",
     "url": "https://www.hindustantimes.com/india-news/x"}]}
check("primary outlet clears the flag",
      rev.check_source_provenance(ai3) == [])

# 4. A government source clears the flag.
ai4 = {**AI, "sources": [
    {"name": "DGCA", "url": "https://dgca.gov.in/notice"}]}
check("government source clears the flag",
      rev.check_source_provenance(ai4) == [])

# 5. Non-announcement stories are out of scope.
local = {
    "headline": "Morrisville Diwali Mela Draws Record Crowd",
    "body": "<p>Families gathered at the community park on "
            "Saturday for food stalls and fireworks.</p>",
    "sources": [{"name": "Local Blog",
                 "url": "https://exampleblog.com/mela"}],
}
check("non-announcement story not flagged",
      rev.check_source_provenance(local) == [])

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
