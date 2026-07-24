#!/usr/bin/env python3
"""PATCH the Manika Batra article to correct the world-ranking figure.
Wikipedia's No. 27 was a stale November rank. Current ITTF reporting (SportsTak,
RevSportz) puts her at No. 51 — and the decisive fact is the TTFI rule that a
top-50 world ranking guarantees automatic selection regardless of domestic
play. Sreeja Akula (No. 45) cleared it; Batra (No. 51) missed by one place.
"""
import os, json, requests

env_supa = os.path.expanduser("~/.env.supabase")
for line in open(env_supa):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
SLUG = "manika-batra-left-out-india-asian-games-2026-squad-table-tennis-selection-row-ttfi-ranking-rule-pm-modi-appeal-diaspora"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

new_headline = "India's Most Famous Paddler Missed the Asian Games Team by One Ranking Place"
new_subheadline = "Manika Batra, the face of Indian table tennis, has been named only a reserve: world No. 51, one spot short of the top-50 ranking that would have guaranteed her a place. Her public appeal to the Prime Minister has reopened an old fight over how India picks its athletes."

new_body = """Manika Batra is, by some distance, the most recognisable name in Indian table tennis. She is a double Commonwealth Games gold medallist, an Asian Games bronze medallist and an Olympian — for the better part of a decade, the face of the sport in a cricket-soaked country. So when the Table Tennis Federation of India (TTFI) named its squad for the 2026 Asian Games in Aichi-Nagoya, Japan, the most striking name was the one missing from the main list. Batra was relegated to the reserves.

Her response was not quiet. Within a day she went to X to call the decision "deeply disheartening, with no specific reason communicated," and did something Indian athletes rarely do in public: she escalated it straight to the top, requesting that "the Hon'ble Prime Minister, Hon'ble Sports Minister and Indian Olympic Association look into the matter and ensure transparency and fair application of selection norms." For a sport that usually fights its battles behind closed doors, it was an extraordinary appeal.

## The Rule That Sank Her

The maths, on paper, is straightforward. The TTFI says it picked the squad using a fixed formula: 50 per cent weight to a player's national ranking, 40 per cent to world ranking, and 10 per cent to the selection committee's discretion. There is also a cleaner shortcut buried in the policy — a place inside the world's top 50 guarantees automatic selection, regardless of how much domestic cricket-circuit table tennis a player has skipped. That single clause is the whole story.

Batra currently sits at world No. 51, India's second-highest-ranked woman. One place higher and she would have walked into the squad on the automatic rule. Instead, she dropped into the weighted formula — and there her problem is the largest bucket of all. By skipping recent domestic tournaments, she no longer holds an official national ranking, so half of her selection score effectively reads as zero. Her world ranking, worth 40 per cent, was not enough to drag her back above the cut line.

That is how the most decorated active woman in the sport ends up outside the team. Sreeja Akula, ranked world No. 45, cleared the top-50 bar comfortably and will captain the side. The squad also features Yashaswini Ghorpade, Diya Chitale, Sutirtha Mukherjee and Syndrela Das, with Swastika Ghosh and Batra named as reserves. The men's team will be led by G. Sathiyan, alongside Harmeet Desai, Manav Thakkar, Manush Shah and Payas Jain.

## Letter Versus Spirit

Batra's central charge is not that the rule was broken, but that it was applied inconsistently. "Questions arise on consistency, as different thresholds and considerations were applied in the previous selection cycle compared to my case," she wrote, arguing that the same standard was not used across cycles. The federation's defenders counter that a published, weighted formula is precisely what athletes have demanded for years — an objective system that does not bend for big names. Skip the domestic grind, the logic goes, and you forfeit the points it earns, however many medals you have on the shelf.

Not everyone in the sport is convinced the system served India well. "You can't overlook Manika. She is absolutely critical if we are to win a medal. This is a very strange selection, and the eventual loser here is India," one member of a previous Asian Games squad told RevSportz on condition of anonymity. A senior administrator was blunter still: "Are you seriously going to field a domestic player in Nagoya when 60 per cent weightage is effectively being given to domestic competitions?" It is, notably, not the first time Batra has clashed with the federation over selection — she has previously gone to court to secure her rights, and won.

## Why It Travels

For the diaspora, this is more than a domestic selection spat. Manika Batra is one of the handful of Indian Olympic-sport athletes who broke through to genuine global recognition — the player who stunned the field at the 2018 Commonwealth Games and turned table tennis, briefly, into back-page news. NRIs who have watched India slowly build depth in Olympic sports tend to follow names like hers closely, because they represent the part of Indian sport that exists beyond the IPL economy.

The deeper resonance is about fairness and process — themes that travel well in diaspora communities built on the idea of merit. Indians abroad have spent decades navigating systems where rules and rankings decide outcomes, and the Batra row lands on a familiar nerve: when does a transparent rule become a blunt instrument, and who gets to override it? Her appeal to the Prime Minister has guaranteed the question will not be settled quietly.

## What Happens Next

As a reserve, Batra is not fully out; an injury or withdrawal could still pull her into the squad before the Games, which run from September 19 to October 4. But the larger fight is now about the criteria themselves, and whether the TTFI or the sports ministry revisits how heavily a missing domestic ranking should count against proven international pedigree. For now, India's most famous paddler is on the outside of its biggest team of the year — beaten not by an opponent across the table, but by a single place in the world rankings — and she has made sure everyone, all the way up to the Prime Minister, knows it."""

patch = {
    "headline": new_headline,
    "subheadline": new_subheadline,
    "body": new_body,
}

r = requests.patch(
    f"{SUPABASE_URL}/rest/v1/p2_articles?slug=eq.{SLUG}",
    headers=HEADERS, json=patch, timeout=30,
)
print("status:", r.status_code)
print("words:", len(new_body.split()))
if r.status_code in (200, 204):
    print("\u2713 Patched")
else:
    print(r.text[:300])
