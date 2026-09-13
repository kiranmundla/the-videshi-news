#!/usr/bin/env python3
"""Build the IRCTC record-bookings article JSON payload for p2_articles insert."""
import json

body = """<div class="key-takeaways"><ul><li>IRCTC recorded 20,06,353 ticket bookings on September 7, the first time the railway ticketing platform has crossed 20 lakh in a single day.</li><li>Bookings stayed elevated on September 8 with 19,50,699 tickets sold, roughly 6% above last year's festive single-day peak of 18,40,203.</li><li>The surge followed the opening of the 60-day advance reservation window for Diwali and Chhath Puja travel.</li><li>New servers nearly doubled reservation capacity, while upgraded anti-bot measures cut suspicious automated traffic by 55&ndash;65% with no major outage reported.</li></ul></div>

<p>India's online railway ticketing platform has set a new all-time record. The Indian Railway Catering and Tourism Corporation (IRCTC) sold 20,06,353 tickets on September 7, crossing the 20-lakh single-day mark for the first time in its history, according to railway figures reported by NDTV and corroborated across Indian media.</p>

<p>The momentum carried into the following day. On September 8, the platform processed 19,50,699 bookings, about 6% higher than last year's festive-season single-day peak of 18,40,203 tickets, recorded on September 19, 2025. Around 89% of all reserved railway tickets in India are now booked online, the corporation said.</p>

<h2>Context &amp; Background</h2>

<p>Diwali falls on November 8 this year, followed by Chhath Puja, and the two festivals drive the largest annual wave of domestic travel in India. This year the surge is concentrated: Indian Railways shortened the advance reservation period from 120 days to 60 days, compressing festive-season demand into a narrower window and piling pressure onto the days when reservations open.</p>

<p>The system held up because of a major infrastructure refresh. IRCTC replaced older servers with new equipment and carried out software optimisation and architectural changes to its Next Generation e-Ticketing (NGeT) system, built with the Centre for Railway Information Systems (CRIS), roughly doubling capacity. A new website and user interface launched on July 15, 2026 lets passengers check seat availability across travel classes on a single screen, built for exactly these high-demand booking windows. Despite unprecedented volumes, the platform reported no major glitches or service outages.</p>

<p>Demand arrives in sharp spikes. Between 8.43% and 14.14% of each day's bookings are completed in the first hour, from 8 AM to 9 AM, with the first 15 minutes (8:00&ndash;8:15 AM) recording the highest simultaneous demand. The system handles 1.33 crore to 1.74 crore logins a day during the reservation window, while more than 85% of bookings are completed later in the day.</p>

<h2>Impact &amp; Analysis</h2>

<p>Fair access has been the harder battle. IRCTC said its advanced anti-bot system has reduced suspicious automated traffic by 55% to 65%, and a sweeping audit deactivated 3.04 crore user accounts while flagging another 6.33 crore IDs for mandatory re-verification. Authorised ticketing agents are barred from booking during the first 10 minutes after reservations open (8:00 AM to 8:10 AM), and Aadhaar verification is now compulsory for individual users booking as soon as the window opens.</p>

<p>The 20-lakh figure covers IRCTC's online platform alone. The broader Passenger Reservation System, which combines online bookings and reservation counters, set its own single-day record at 22.26 lakh tickets, according to CRIS.</p>

<blockquote class="pull-quote"><p>&ldquo;With 22.26 lakh tickets booked in a day, the PRS continues to demonstrate its scale, resilience and ability to serve millions of passengers.&rdquo;</p><cite>&mdash; Centre for Railway Information Systems (CRIS), statement</cite></blockquote>

<p>Distribution is also diversifying. Third-party platforms including Paytm, MakeMyTrip, ixigo and ConfirmTkt now account for 28% of online railway bookings, according to IRCTC Chairman and Managing Director Rahul Himalian. The IRCTC Rail Connect app handles 53% of online bookings, the official website 17%, and government arrangements about 2%.</p>

<blockquote class="pull-quote"><p>&ldquo;28% are through the business associates through B2C, B2B, ICS platform, whether it is MakeMyTrip, Paytm, ixigo, ConfirmTkt.&rdquo;</p><cite>&mdash; Rahul Himalian, Chairman and Managing Director, IRCTC</cite></blockquote>

<h2>Diaspora Angle</h2>

<p>For NRIs planning Diwali travel to India, the timing is tight. With the reservation window cut to 60 days, festive bookings opened this week and demand is already at record levels, so waiting risks slim pickings on popular routes. Aadhaar verification is compulsory for individual users booking at window opening, so travellers should make sure their IRCTC accounts are verified well in advance. With authorised agents locked out of the first 10 minutes of booking, an early-morning personal booking remains the best shot at a confirmed berth.</p>

<h2>What's Next</h2>

<p>The real test comes through October, when Diwali and Chhath Puja travel bookings peak. Indian Railways typically announces festival special trains in the coming weeks, which would add capacity on the busiest corridors. The longer question is structural: with the 60-day reservation window compressing demand into a narrower band, the expanded NGeT capacity and anti-bot enforcement will be judged on how the system performs in the weeks ahead.</p>
"""

# word count: plain text
import re
text = re.sub(r"<[^>]+>", " ", body)
text = re.sub(r"\s+", " ", text).strip()
word_count = len(text.split())

payload = {
    "headline": "IRCTC Shatters Records as 20 Lakh Tickets Booked in a Single Day",
    "subheadline": "The September 7 milestone marks the first time India's online railway ticketing platform has crossed the 20-lakh single-day mark, with upgraded servers and anti-bot measures keeping the system stable through the Diwali booking rush.",
    "body": body,
    "slug": "irctc-record-20-lakh-tickets-single-day",
    "category": "travel",
    "vertical": "travel",
    "tags": ["IRCTC", "Indian Railways", "train tickets", "festive travel", "Diwali", "Chhath Puja"],
    "sources": [
        "https://www.livemint.com/news/india/irctc-clocks-record-ticket-bookings-ahead-of-festive-rush-daily-volume-breaches-20-lakh-mark-for-first-time-report-11789182290445.html",
        "https://www.businessvibesofindia.com/record-train-bookings-of-over-20-lakh-in-single-day/",
        "https://urbanacres.in/irctc-sets-20-06-lakh-train-booking-record-amid-festive-rush/",
        "https://www.latestly.com/india/news/irctc-record-breaking-booking-20-million-tickets-booked-during-diwali-advance-reservation-period-7600761.html",
        "https://www.latestly.com/india/news/indian-railways-prs-sets-single-day-record-with-over-22-lakh-tickets-booked-check-what-drove-the-surge-7599997.html",
    ],
    "image_url": None,
    "image_caption": None,
    "image_attribution": None,
    "word_count": word_count,
    "diaspora_angle": "NRIs planning Diwali travel to India should book now: the 60-day advance reservation window concentrates festive demand, and Aadhaar verification is compulsory for individual users booking when the window opens.",
    "topic_id": "d035cf38-fe91-406f-a4a3-9f7589d1483e",
    "llm_score": 3,
    "published_at": "2026-09-12T16:55:00Z",
    "article_type": "breaking",
    "status": "published",
}

with open("/tmp/article-irctc.json", "w") as f:
    json.dump(payload, f, ensure_ascii=False)

print("word_count:", word_count)
print("payload written to /tmp/article-irctc.json")
