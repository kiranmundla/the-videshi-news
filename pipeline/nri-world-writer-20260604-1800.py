#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Revamped Its OCI Portal for Five Million Cardholders. The Old System Was Built in 2013.",
        "subheadline": "Amit Shah launched a modernised Overseas Citizen of India platform with auto-fill, in-built payments, and real-time tracking — replacing a portal that processed 2,000 applications a day on decade-old infrastructure.",
        "slug": make_slug("india-revamps-oci-portal-five-million-cardholders-digital"),
        "category": "nri-world",
        "vertical": "nri-world",
        "is_editorial": False,
        "diaspora_angle": "The OCI card is the primary legal document connecting 5 million diaspora Indians to their homeland. A clunky portal meant lost hours, abandoned applications, and deferred trips. The upgrade matters because it is the bureaucratic front door to India for every NRI who holds one.",
        "tags": ["nri", "diaspora", "oci", "india-policy", "digital-governance"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2025/05/20/india-launches-feature-rich-user-friendly-oci-portal-for-5-million-oci-cardholders/"},
            {"name": "Ministry of Home Affairs (India)", "url": "https://www.mha.gov.in/"},
            {"name": "Formula Group India", "url": "https://formulaindia.com/new-oci-portal-launched/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/fd/Shri_Amit_Shah_in_Raigad.jpg",
        "image_caption": "Union Home Minister Amit Shah, who inaugurated the revamped OCI portal in New Delhi",
        "image_attribution": "Wikimedia Commons",
        "body": """If you have ever tried to renew an OCI card online, you already know the punchline. The portal that five million Overseas Citizens of India relied on was built in 2013, ran on infrastructure older than some of its applicants' passports, and offered the kind of user experience that made a consular queue look appealing. On Monday, Union Home Minister Amit Shah replaced it.

The new platform — live at ociservices.gov.in — introduces auto-fill for profile details, an integrated payment gateway, a dashboard that tracks partially completed applications, and document categorisation that tells applicants exactly what they need before they start uploading. There is also an in-built image cropping tool, which sounds trivial until you recall how many OCI applications have been rejected over photo dimensions.

## Why It Took This Long

The previous portal was operational across more than 180 Indian missions and 12 Foreigners Regional Registration Offices, processing roughly 2,000 applications per day. Replacing it was not a matter of standing up a new website. It meant migrating a decade of records, retraining mission staff in dozens of countries, and coordinating with the security apparatus that vets every application.

The Ministry of Home Affairs said the overhaul was driven by "rapid technological advancements over the past decade and feedback received from OCI cardholders." That is bureaucratic understatement. NRI forums have catalogued years of complaints: sessions timing out mid-application, payment confirmations vanishing, and status pages that displayed nothing at all.

Prime Minister Narendra Modi endorsed the launch on X, calling it "a major step forward in boosting citizen-friendly digital governance." Shah wrote that the portal's new features "will include improved functionality, enhanced security, and a user-friendly experience."

## What Actually Changed

The feature list reads like a corrective audit of everything that was wrong before. Applicants can now edit their submission at any stage before final confirmation — previously, a single error meant starting over. Eligibility criteria and required documents are displayed based on the selected application type, so a spouse applying under the foreign-origin pathway no longer has to guess which fields apply. An integrated FAQ sits inside the portal rather than on a separate government website three clicks away.

For OCI holders who have obtained new passports, the upload process has been simplified. Cardholders under 20 must upload a copy of the new passport and a recent photograph each time a new passport is issued. Those over 50 need to do it once. Foreign-origin spouses must additionally declare that their marriage is still subsisting — a requirement that remains, but the mechanics of complying with it are now less punishing.

## The Bigger Picture

The portal refresh arrives alongside a broader push to streamline diaspora services. In April, the government scrapped the six-month residency rule for OCI applications filed within India. The PIO card was officially discontinued, forcing hundreds of thousands of holdouts to convert. And GOPIO International recently passed a resolution urging full dual nationality for OCI holders — a demand the government has not conceded but has not dismissed either.

For the 5 million NRIs who hold an OCI card and the thousands who apply each month, the portal is not a policy statement. It is the interface between them and a country they still call home. Whether the new version actually works as advertised will become clear soon enough, when the next wave of summer visa-season applicants hits the system. The old portal buckled under far less."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Spirits Just Landed in Canadian Duty-Free. The Diaspora Built the Runway.",
        "subheadline": "An 'Indian Aisle' now sits inside Toronto Pearson, Vancouver International, and duty-free shops along the Ontario-BC border — the first time Indian-made spirits have entered Canada's travel retail market.",
        "slug": make_slug("indian-spirits-canada-duty-free-indian-aisle-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "is_editorial": False,
        "diaspora_angle": "The 1.9 million Indo-Canadians who pass through these airports are now the test market for Indian premium spirits in North America. What looks like a retail launch is really a bet on whether the diaspora's cultural tastes can open a commercial channel that did not exist before.",
        "tags": ["nri", "diaspora", "canada", "indian-spirits", "trade", "duty-free"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/28/great-white-northern-spirits-launches-indian-aisle-in-canada/"},
            {"name": "South Asian Herald", "url": "https://southasianherald.com/indian-spirits-enter-canadas-duty-free-market-through-indian-aisle-initiative/"},
            {"name": "LatestLY / ANI", "url": "https://www.latestly.com/agency-news/business-news-a-historic-bridge-between-nations-indian-aisle-in-canada-brought-indias-premium-craft-to-international-retail-spaces-6792133.html"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Interior_of_Toronto_Pearson_International_Airport_Terminal_1_wider_view.jpg/1280px-Interior_of_Toronto_Pearson_International_Airport_Terminal_1_wider_view.jpg",
        "image_caption": "Interior of Toronto Pearson International Airport Terminal 1, one of the locations hosting the new Indian Aisle",
        "image_attribution": "Wikimedia Commons",
        "body": """Walk through duty-free at Toronto Pearson International Airport and, for the first time, you will find a shelf labelled for Indian spirits. Not relegated to a world-foods curiosity section, not tucked behind Japanese whiskies and Mexican tequilas, but in a dedicated "Indian Aisle" designed to look like it belongs.

The launch, on May 21 at Nuvo Event Space in Brampton, put Indian-made beverages into Canada's premium travel retail corridor. Toronto Pearson, Vancouver International, airports across Alberta, and prominent land-border duty-free shops in Ontario and British Columbia are all stocking the range. The venture is led by Great White Northern Spirits (GWNS), a company founded by Balaji Nagaraja and Pooja S., who describe the initiative as "opening doors for Indian heritage, craftsmanship and stories to travel globally."

## A Market That Did Not Exist

Indian spirits have a paradox. India is the world's largest whisky market by volume — it consumes more than two billion litres a year. Indian single malts like Amrut and Paul John have won international blind tastings. Yet outside specialty liquor stores in a handful of global cities, Indian bottles are almost invisible in mainstream retail. In Canadian duty-free, they were entirely absent until last month.

The gap is partly regulatory. Canada's province-by-province liquor control system makes shelf space fiercely competitive. Duty-free is one of the few retail channels that sidesteps provincial boards entirely, which is why GWNS chose it as the point of entry. If Indian whisky can prove its pull in an airport shop where travellers browse with time and curiosity, it stands a better chance of breaking into the regulated retail market next.

## The Diaspora as Market Maker

The commercial logic runs through the Indo-Canadian community. Canada's 2021 census counted 1.86 million people of South Asian origin, a number the 2026 count is expected to revise sharply upward. British Columbia alone has an estimated 400,000 Indo-Canadians. These are travellers who pass through Vancouver and Pearson regularly, and for whom an Indian single malt in the duty-free is not exotic — it is a reminder of home.

But the ambition goes beyond nostalgia. GWNS is betting that the same cultural shift that turned sake into a global bar staple and mezcal into a cocktail ingredient can work for Indian craft spirits. The Indian Aisle is designed to educate non-Indian travellers too, with tasting notes, heritage stories, and packaging that signals premium rather than budget.

## Soft Power in a Bottle

The launch was attended by government officials, diplomatic representatives, and trade stakeholders — a sign that both Ottawa and New Delhi see this as more than a product placement. India's push for "Brand India" in international markets has gained momentum over the past decade, and spirits are a natural fit. They carry cultural narrative, command premium pricing, and create a halo effect for other Indian exports.

"Canada's multicultural identity makes it the perfect home for an initiative like the Indian Aisle," Nagaraja and Pooja said in a joint statement. "Through this platform, we hope to create stronger cultural connections, introduce travellers to the richness of Indian spirits, and build meaningful commercial opportunities between India and Canada."

Whether the Indian Aisle survives beyond its launch buzz will depend on sales velocity in the first year. Duty-free operators are unsentimental about shelf space. But the timing is favourable: bilateral trade between India and Canada stands at $8.5 billion and both governments have committed to expanding it to $50 billion by 2030. Piyush Goyal just led the largest-ever Indian business delegation to Canada. The spirits on the shelf are one more thread in a fabric that the diaspora has been weaving for decades."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "75,000 Indians Left Britain Last Year. They Were Also the Largest Group Arriving.",
        "subheadline": "New ONS data shows UK net migration fell to 171,000, its lowest since 2021. Indians dominated every category — arrivals, departures, skilled work extensions, and student visas — exposing a contradiction Britain has not resolved.",
        "slug": make_slug("indians-lead-uk-migration-exit-arrivals-ons-paradox"),
        "category": "nri-world",
        "vertical": "nri-world",
        "is_editorial": False,
        "diaspora_angle": "For the 1.8 million-strong Indian diaspora in Britain, the numbers tell a story of a community that is simultaneously the most wanted and the most expendable. Indians fill the NHS, lead skilled worker extensions, and dominate student visas — yet they also lead the exit charts, caught between tightening visa rules and a political climate that treats immigration as a number to be managed down.",
        "tags": ["nri", "diaspora", "uk", "migration", "ons-data", "british-indians"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/indian-students-workers-lead-exit-trend-as-uk-net-migration-falls/article71006039.ece"},
            {"name": "Migration Observatory, University of Oxford", "url": "https://migrationobservatory.ox.ac.uk/resources/briefings/long-term-international-migration-flows-to-and-from-the-uk/"},
            {"name": "Asian Voice UK", "url": "https://www.asian-voice.com/"},
            {"name": "Office for National Statistics (UK)", "url": "https://www.ons.gov.uk/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/22/Shabana_Mahmood_Official_Cabinet_Portrait%2C_September_2025_%28cropped%29~2.jpg",
        "image_caption": "UK Home Secretary Shabana Mahmood, who announced the net migration figures",
        "image_attribution": "Wikimedia Commons",
        "body": """The numbers carry a neat political headline and a messy human story. Britain's net migration fell to 171,000 in 2025, down from a peak of 944,000 under the Conservatives. Home Secretary Shabana Mahmood called it proof that the government is "restoring order and control to our borders." What she did not dwell on is who, exactly, left.

Indians led the departure charts. According to the Office for National Statistics, approximately 51,000 Indians who had come to study, 21,000 who had come to work, and 3,000 others departed the UK last year. No other nationality came close. Chinese nationals followed at 46,000. Ukrainians, Pakistanis, and Nigerians rounded out the top five.

Here is the contradiction: Indians also led the arrival charts. They accounted for 17 per cent of all immigration to the UK, the single largest nationality. They received the most Health and Care Worker visa extensions (107,306), the most Skilled Worker extensions (89,851), and the most Graduate Route visa extensions (70,371). They held 23 per cent of all Sponsored Study visas granted in the period.

## The Squeeze

The fall in net migration was not an organic shift. It was engineered. The previous Conservative government, facing a politically toxic headline number, tightened the student visa route because it was the softest lever available. Cutting work visas in health and social care would have cratered the NHS and the care sector. Students were countable, temporary, and their dependants showed up in the same headline figure. Indian students, who had been arriving in record numbers, bore the brunt.

The current Labour government has continued the squeeze. Mahmood has warned of further visa cuts and penalties for countries that "do not play ball" over the return of illegal migrants. India was added to the UK's "Safe States" list last November, accelerating deportation processing for Indians who enter illegally — a small number, but symbolically loaded.

## A Community Caught in the Middle

For the 1.8 million people of Indian origin who call Britain home, the statistics describe a community that is simultaneously indispensable and exposed. Indian doctors staff NHS wards. Indian engineers fill technology roles that domestic graduates cannot. Indian students pay international fees that subsidise British universities — a sector now facing a £37 billion funding crisis as international enrolments collapse.

The ONS found that non-EU arrivals for work-related reasons fell by 47 per cent last year. "The recent decrease is being driven by fewer people arriving from outside the EU, particularly for work," said ONS deputy director Sarah Crofts. The decline is sharpest in exactly the categories where Indians dominate.

What this means in practice is a generation of Indian professionals reconsidering Britain as a destination. The Graduate Route visa, which allows international students to work for two years after completing a UK degree, is under review. A government-commissioned report recommended keeping it, but the political pressure to cut further is intense, with Reform UK making immigration the centrepiece of its electoral gains.

## The Arithmetic of Belonging

Total long-term immigration to the UK stood at 813,000 last year, a 20 per cent drop from 2024. Emigration was rising before it began to flatten. The gap between the two — net migration — is the number politicians care about. But for the Indian families making the decision to stay or leave, the arithmetic is different. It includes visa uncertainty, the cost of international school fees for children who may not qualify for home status, and the psychic weight of being told, repeatedly, that migration is a problem to be solved rather than a contribution to be welcomed.

Mahmood has promised "a skills-based migration system that rewards contribution and ends Britain's reliance on cheap overseas workers." The irony is that Indians already represent the most skilled, highest-contributing migrant cohort in the country. If the system rewarded contribution, the numbers would be going up, not down.

The 75,000 who left last year made their own calculation. Britain's loss is someone else's gain — likely the Gulf, Canada, Australia, or a return to an India whose own economy is now large enough to absorb its diaspora back. The question Britain has not answered is whether it can afford to keep pushing away the people it most depends on."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
