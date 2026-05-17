# Event Sources Database
# Reference file for the videshi-events cron agent
# Last updated: 2026-05-17

## Tier 1: Structured Data (auto-scrapable)

### Eventbrite (BEST SOURCE)
- Format: `__SERVER_DATA__` JSON in HTML
- URL pattern: `https://www.eventbrite.com/d/{state}--{city}/{keyword}/?page=1`
- Data: 20 events/page, includes title, date, venue, image, ticket URL
- Cities to scrape:
  - `ca--san-jose`, `ca--san-francisco`, `ca--fremont`
  - `ny--new-york`, `nj--edison`, `nj--jersey-city`
  - `tx--dallas`, `tx--houston`, `tx--plano`
  - `il--chicago`, `il--schaumburg`
  - `wa--seattle`, `wa--bellevue`, `wa--redmond`
  - `ga--atlanta`, `ga--alpharetta`
  - `dc--washington`
  - `pa--philadelphia`
  - `nc--charlotte`
  - `mi--detroit`, `mi--troy`
  - `ca--los-angeles`, `ca--irvine`, `ca--cerritos`
- Keywords per city:
  - Indian, Bollywood, Telugu, Tamil, Hindi, Punjabi, Garba, Diwali, Holi
  - Desi, Bhangra, Cricket, Biryani, Carnatic, Bharatanatyam
  - Navratri, Pongal, Onam, Eid, Sikh
  - 5K run, marathon, half marathon, fun run, color run
  - spelling bee, math olympiad, science olympiad, chess tournament
  - DECA, HOSA, FBLA, robotics, Model UN
  - yoga, meditation, kirtan

### Ticketmaster (big concerts/tours)
- Format: JSON via `ticketmaster` CLI
- Command: `ticketmaster search-events --keyword "{kw}" --state-code {state} --size 20 --sort date,asc`
- Keywords: Diljit, Bollywood, Garba, Indian, Desi, Bhangra, Telugu, Shreya Ghoshal, Arijit Singh, AP Dhillon, Badshah, Vishal Shekhar
- Good for: concerts, comedy tours, cricket matches

### events.sulekha.com (Indian-specific)
- Format: JSON-LD `schema.org/Event` in HTML
- URL pattern: `https://events.sulekha.com/indian-events-in-{city-slug}`
- City slugs: `san-francisco-bay-area`, `new-york-tri-state-area`, `dallas-fort-worth`, `houston`, `chicago`, `los-angeles`, `seattle`, `atlanta`, `washington-dc`, `philadelphia`
- Data: title, startDate, endDate, location, URL
- Coverage: 3-10 events per city, Indian-specific (concerts, plays, comedy)

### Meetup.com (community events)
- Format: HTML with event titles in H3 tags
- URL: `https://www.meetup.com/find/?keywords=indian&location={city}%2C+{state}`
- Good for: meetups, networking, cultural groups, food events, language exchange
- Also search: `https://www.meetup.com/find/?keywords=desi&location={city}`

## Tier 2: Web Search Sources (Claude agent reads via web_search)

### us.sulekha.com (rich but JS-rendered)
- Cannot curl directly — JS-rendered SPA
- Agent should web_search: `site:us.sulekha.com events {city}`
- Rich Indian event listings, location-aware

### simplydesi.us (1000+ events aggregator)
- JS-rendered, cannot curl
- Agent should web_search: `site:simplydesi.us {city} events 2026`
- Covers 25+ US cities, Indian cultural events

### allevents.in
- JS-rendered
- Agent should web_search: `site:allevents.in {city} indian events`
- Global event aggregator with US coverage

### 10times.com
- JS-rendered
- Agent should web_search: `site:10times.com {city} indian`
- Conference and expo focused

## Tier 3: Organization Websites (curated, check monthly)

### Telugu Organizations
- TANA (Telugu Association of North America): `tana.org`
- ATA (American Telugu Association): `ataworld.org`
- TTA (Telangana American Telugu Association): `ttaconvention.org`
- MATA: check web for convention dates
- NATA: check web for convention dates

### Pan-Indian Organizations
- FIA (Federation of Indian Associations): `fianynjct.org`
- AAPI (American Association of Physicians of Indian Origin)
- TiE (The Indus Entrepreneurs): `tie.org` — networking, startup events
- Indiaspora: `indiaspora.org`
- GOPIO (Global Organization of People of Indian Origin)

### Regional/Language Organizations
- BMM (Bruhan Maharashtra Mandal): marathi events
- Kannada Koota: kannada events per city
- Tamil Sangam: tamil events per city
- Bengali Association: bengali/durga puja events
- Gujarati Samaj: garba/navratri events per city
- Kerala Association: onam/malayali events

### Consulates & Government
- Indian consulates: `indiainnewyork.gov.in`, `cgisf.gov.in`, `cgihouston.gov.in`
- Check for Republic Day, Independence Day, cultural events

## Tier 4: Running & Sports Events

### Running Calendars
- `runningintheusa.com` — comprehensive US race calendar
- `marathonguide.com` — marathons and halfs
- `active.com/running` — 5Ks, 10Ks, fun runs
- `runsignup.com` — race registration, searchable by city

### Cricket
- `usacricket.org` — USA Cricket official events
- `icc-cricket.com` — ICC events in US
- Minor League Cricket: `mlc.cricket`

## Tier 5: Ticketing Platforms (check for Indian events)

- `premiertickets.co` — Indian concert promoter (Diljit, Shreya, etc.)
- `sulekhatickets.com` — Sulekha's ticketing arm
- `bookmyshow.com/international` — Indian ticketing expanding to US
- `insider.in` — sometimes has US events for Indian artists

## URL Templates for Agent

When the agent runs, it should construct URLs like:
```
# Eventbrite (curl-able, get __SERVER_DATA__)
https://www.eventbrite.com/d/ca--san-jose/indian/?page=1
https://www.eventbrite.com/d/ca--san-jose/telugu/?page=1
https://www.eventbrite.com/d/tx--dallas/diwali/?page=1

# Sulekha events (curl-able, get JSON-LD)
https://events.sulekha.com/indian-events-in-san-francisco-bay-area
https://events.sulekha.com/indian-events-in-new-york-tri-state-area

# Web searches for JS-rendered sites
site:us.sulekha.com events bay area 2026
site:simplydesi.us san jose events
"{org name} convention 2026"
"Indian events {city} {month} 2026"
"5K run {city} {month} 2026"
"garba {city} 2026"
```
