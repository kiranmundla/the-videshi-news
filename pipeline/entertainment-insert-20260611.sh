#!/usr/bin/env bash
# Entertainment Writer — 2026-06-11 articles
# Stories: Lock Upp: Sach Ya Saza, Peddi Box Office

set -euo pipefail
source ~/.env.supabase

NOW=$(date -u +%Y-%m-%dT%H:%M:%S+00:00)

insert_article() {
    local PAYLOAD="$1"
    local LABEL="$2"
    
    RESULT=$(curl -sS "$SUPABASE_URL/rest/v1/p2_articles" \
        -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
        -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
        -H "Content-Type: application/json" \
        -H "Prefer: return=representation" \
        -d "$PAYLOAD" 2>&1)
    
    ID=$(echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['id'] if isinstance(d,list) and d else 'FAIL: '+json.dumps(d)[:300])" 2>&1)
    
    if [[ "$ID" == FAIL* ]]; then
        echo "  ✗ $LABEL: $ID"
        return 1
    else
        echo "  ✓ $LABEL: id=$ID"
        echo "$ID"
        return 0
    fi
}

echo "=========================================="
echo "Entertainment Writer — $(date -u)"
echo "=========================================="

# ── ARTICLE 1: Lock Upp: Sach Ya Saza ──
echo ""
echo "--- Article 1: Lock Upp: Sach Ya Saza ---"

read -r -d '' BODY1 << 'ENDOFBODY' || true
Netflix just played its hand, and the cards are prison-themed.

The streaming giant has officially unveiled the first promo for Lock Upp: Sach Ya Saza, confirming that Farah Khan and Riteish Deshmukh will front the new season of the reality franchise that set the internet on fire in 2022. The show premieres June 27 on Netflix — Saturday through Wednesday at 8 PM — and if the guerrilla marketing campaign is any indication, this season intends to be louder, messier, and significantly more expensive than its predecessor.

## The Promo That Told You Nothing and Everything

The teaser is a masterclass in controlled chaos. Farah and Riteish are introduced as Prisoner No. 06 and Prisoner No. 27 — a playful nod to the premiere date — as they walk through separate jail cells before coming face-to-face behind bars. The tone begins cold and intense, the two exchanging dead-serious glances that would be convincing if you did not already know that these are two of the most entertainingly unserious people in Bollywood. The clip ends with matching smirks and a "To Be Continued" card. Netflix captioned it with surgical precision: "Do khaas mehmaan. Ek Lock Upp."

Whether Farah and Riteish are the official host and jailer, or whether the promo is an elaborate misdirect, has not been formally confirmed by Netflix or Balaji Telefilms. But the industry consensus is strong: Farah is hosting, Riteish is running the jail, and the contestants — whose names the makers are guarding with the kind of paranoia usually reserved for nuclear launch codes — will be revealed closer to premiere night.

## The Season 1 Shadow

The original Lock Upp, subtitled Badass Jail, Atyaachari Khel, premiered in 2022 on ALTBalaji and MX Player with Kangana Ranaut as its polarizing, confrontational host. It became one of the most talked-about digital properties of the year, primarily because Kangana treated every elimination like a cross-examination and every conversation like a press conference. Comedian Munawar Faruqui won the inaugural season, while contestants like Payal Rohatgi, Anjali Arora, Poonam Pandey, and Shivam Sharma kept trending for weeks.

Kangana's return was the first question fans asked when Season 2 was announced. The answer appears to be no — she is now a sitting Member of Parliament and is preparing her acting comeback with Bharat Bhhagya Viddhaata. A reality show, even one she helped make famous, does not appear to be on the agenda.

## Why Farah and Riteish Make Sense

The Farah-Riteish pairing is not random. The two share a deep, long-standing professional relationship — Riteish has been a permanent fixture in the films of Farah's brother, Sajid Khan, starring in Heyy Babyy, Housefull, Housefull 2, and Humshakals. Riteish has also hosted Bigg Boss Marathi, so he knows the grammar of reality television. Farah, meanwhile, has spent years as a judge on dance and talent shows, dispensing the kind of blunt, affectionate commentary that makes contestants cry and audiences laugh in the same breath.

Together, they represent a different energy from Kangana's era. Where Season 1 was confrontational and combative, Season 2 appears to be leaning toward irreverent and unpredictable — two people who clearly enjoy each other's company presiding over a prison full of people who almost certainly will not.

## The Marketing Campaign No One Saw Coming

Before any official announcement, masked figures described as "qaidis" began appearing on streets in Mumbai, Delhi, and Lucknow. Photos circulated online, theories multiplied, and social media did what social media does: overanalyze everything. Then a massive billboard appeared — built to resemble a prison façade with inmates behind metal bars — drawing crowds, cameras, and the kind of earned media that no paid campaign can replicate.

It was clever, disruptive, and slightly unhinged. In other words, it was exactly the right tone for a show produced by Ektaa Kapoor's Balaji Telefilms.

## What This Means for the Diaspora

Here is the part that matters most to NRIs who have been watching Indian reality television through regional streaming apps with inconsistent subtitles and buffering issues: Lock Upp is on Netflix this time. Not ALTBalaji. Not MX Player. Netflix.

That means global availability on day one. It means the show will appear in the same queue as Squid Game and Love Is Blind. It means your non-Indian friends might accidentally stumble onto it and have questions you will enjoy answering. And it means the production budget, the celebrity caliber of the contestants, and the overall polish will almost certainly be a step above what Season 1 could afford.

For the Indian diaspora, reality television has always been a communal experience — the group chat, the family WhatsApp debates, the office conversations the next morning. Lock Upp on Netflix makes that experience frictionless for the first time. No VPN. No regional app subscription. Just open the app on June 27 at 8 PM and watch two of Bollywood's most entertaining personalities run a digital prison.

The inmates, whoever they turn out to be, should be worried.
ENDOFBODY

BODY1_ESC=$(python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))" <<< "$BODY1")

insert_article "$(cat <<EOF
{
    "headline": "Lock Upp Is Back. Farah Khan and Riteish Deshmukh Are Running the Jail. Netflix Has the Keys.",
    "subheadline": "The reality franchise that made Kangana Ranaut must-watch television returns on June 27 — this time on Netflix, with a new host, a new jailer, and a guerrilla marketing campaign that turned city streets into a prison yard.",
    "slug": "lock-upp-sach-ya-saza-netflix-farah-khan-riteish-deshmukh-season-2-20260611",
    "body": $BODY1_ESC,
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "review",
    "published_at": "$NOW",
    "is_editorial": false,
    "sources": ["Pinkvilla", "Filmibeat", "IANS", "Zoom TV Entertainment", "Netflix India"]
}
EOF
)" "Lock Upp"


# ── ARTICLE 2: Peddi Box Office ──
echo ""
echo "--- Article 2: Peddi Box Office ---"

read -r -d '' BODY2 << 'ENDOFBODY' || true
Ram Charan does not do things quietly. But even by his standards, the first week of Peddi has been emphatic.

In just seven days, the Buchi Babu Sana-directed sports drama has crossed ₹270 Cr worldwide, making it the Mega Power Star's highest-grossing film as a solo lead. It has surpassed the lifetime worldwide collection of Ala Vaikunthapurramuloo (₹269.35 Cr) and entered the Top 15 highest-grossing Tollywood films of all time. In North America alone, it has crossed the $3 million mark — joining an elite club previously reserved for Baahubali, RRR, Salaar, and Pushpa 2: The Rule.

For a sports-based rural drama about a villager who uses kabaddi to unite his community, these are not just good numbers. They are a statement.

## The Numbers That Matter

By Day 7, Peddi's India net collection stood at ₹185.13 Cr, with the domestic gross touching ₹220.05 Cr. The overseas gross had reached approximately ₹48 Cr by Day 6, and the worldwide total has now comfortably breached ₹270 Cr. In the Telugu-speaking APTG region — the film's primary market — the cumulative gross hit ₹163.75 Cr, a figure that speaks to the absolute dominance of Ram Charan's appeal in his home territory.

The film is now only the 12th in history to cross ₹150 Cr in share from the Telugu version alone. The company it keeps at that altitude includes Baahubali 2, RRR, and Kalki 2898 AD. For a mid-June release with no festival bump, that is remarkable.

But the Hindi belt is where the conversation gets interesting. The Rest of India markets — largely driven by the Hindi dubbed version — have contributed ₹20.66 Cr gross, outperforming Karnataka (₹23.08 Cr) and significantly ahead of Tamil Nadu (₹5.10 Cr). In Ghazipur, Uttar Pradesh, fans were filmed dancing on the streets to the infectious Chikiri Chikiri track immediately after a screening. When a Telugu star's rural drama has people dancing in UP, the pan-India label is no longer aspirational. It is factual.

## The RRR Comparison Is Inevitable

Peddi is now Ram Charan's second film after RRR to cross ₹200 Cr in India gross. The comparison is uncomfortable for a reason: RRR was a Rajamouli tentpole with a $72 million budget, a dual-hero format, and a Hollywood-level promotional campaign. Peddi is a single-hero sports drama directed by a filmmaker making only his second feature. The budgets are not comparable. The co-star is Janhvi Kapoor, not Jr. NTR. And yet the box office trajectory is not embarrassing itself in the comparison.

This is what a genuine star looks like. Not an actor who needs a franchise or a director's reputation to open a film, but one whose name on the marquee is enough to fill opening weekends across multiple languages and territories.

## The Re-Edit Question

Not everything has been smooth. Reports have surfaced that the makers are planning a significant re-edit of the film — specifically, removing the Gouraidu flashback sequences in the second half and adding fresh scenes featuring Ram Charan and Jagapathi Babu. If confirmed, the revised version would be resubmitted to the censor board before returning to theaters.

This is a calculated gamble. Re-edits mid-run are rare, and they carry a risk: admitting that the theatrical cut has structural issues. But the logic is sound. If the second half is dragging audience word-of-mouth — and the weekday drops suggest it might be — then a tighter cut could revitalize the film heading into its second weekend. Buchi Babu Sana's debut, Uppena, was a tight, emotionally concentrated film. If the same discipline is applied retroactively to Peddi, the second weekend could see a meaningful revival.

## Why the Diaspora Should Care

For NRIs, Peddi is doing two things simultaneously. First, it is proving that Telugu cinema's box office muscle is not limited to the Rajamouli universe. Ram Charan, as a solo lead in a sports drama with no mythology, no VFX spectacle, and no crossover Hollywood marketing, has generated numbers that most Bollywood films would celebrate as career-defining. That is the state of the Telugu industry in 2026 — it does not need anyone's permission to dominate.

Second, the $3 million North America milestone matters specifically because of how it was achieved. This was not NRI nostalgia tourism for a franchise sequel. This was a rural sports drama that earned its North American audience through the South Asian diaspora's appetite for stories rooted in community, physicality, and emotional directness. When a film about a kabaddi-playing villager from Andhra Pradesh crosses $3 million in the same market where Marvel films open, the cultural shift is no longer theoretical.

Peddi is Ram Charan's biggest solo film. By the end of its theatrical run, it could become something more: the proof that Telugu cinema's stars can carry original stories to global audiences without leaning on the safety net of established IP. The numbers are already there. The legacy is being written in real time.
ENDOFBODY

BODY2_ESC=$(python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))" <<< "$BODY2")

insert_article "$(cat <<EOF
{
    "headline": "Peddi Just Became Ram Charan's Biggest Solo Film. The Numbers Are Staggering and the Re-Edit Rumors Are Real.",
    "subheadline": "₹270 Cr worldwide in seven days. $3 million in North America. Top 15 all-time in Telugu cinema. And the makers might be re-cutting the second half anyway. Welcome to the most interesting box office story of the summer.",
    "slug": "peddi-ram-charan-box-office-270-crore-week-one-recut-20260611",
    "body": $BODY2_ESC,
    "category": "entertainment",
    "vertical": "entertainment",
    "status": "review",
    "published_at": "$NOW",
    "is_editorial": false,
    "sources": ["Sacnilk", "Zoom TV Entertainment", "Bollywood Hungama", "BookMyShow"]
}
EOF
)" "Peddi Box Office"

echo ""
echo "=========================================="
echo "ENTERTAINMENT WRITER COMPLETE"
echo "=========================================="
