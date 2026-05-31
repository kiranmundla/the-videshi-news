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
        "headline": "Pennsylvania's Indian Community Just Opened an $8.5 Million Learning Center. The Project Took 27 Years.",
        "subheadline": "The Bharatiya Learning Center in Chalfont teaches seven Indian languages to 200 students a week — and just earned recognition in the Congressional record.",
        "slug": make_slug("bharatiya-learning-center-pennsylvania-85-million-languages"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "A community-funded cultural institution that teaches seven Indian languages in suburban Pennsylvania represents the maturing of Indian-American civic infrastructure — from makeshift weekend classes in temple basements to an $8.5 million purpose-built facility with Congressional recognition.",
        "tags": ["nri", "diaspora", "education", "community", "pennsylvania", "language", "heritage"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/05/bharatiya-learning-center-opens-in-pennsylvania-marking-major-milestone-for-indian-american-community/"},
            {"name": "Bharatiya Temple", "url": "https://bharatiyatemple.org"},
            {"name": "U.S. Congressional Record", "url": "https://www.congress.gov"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20556421/pexels-photo-20556421.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "body": """It started in 1999 with a handful of families and a borrowed room. Nearly three decades later, the Bharatiya Learning Center in Chalfont, Pennsylvania stands as an $8.5 million cultural and educational facility — purpose-built, community-funded, and now recognised in the United States Congressional Record.

The inauguration, which drew over 300 attendees including U.S. Congressman Brian Fitzpatrick and Montgomery County Commissioner Neil Makhija, was more than a ribbon-cutting. It was an acknowledgement that Indian-American civic infrastructure has quietly entered a new phase: from improvised weekend classes in temple back rooms to institutions with permanent addresses, professional facilities, and political visibility.

## Seven Languages, One Roof

The centre currently serves roughly 200 students every week, offering instruction in seven Indian languages: Sanskrit, Hindi, Gujarati, Marathi, Kannada, Telugu, and Tamil. The breadth is deliberate. Unlike many heritage language programs that serve a single linguistic community, the Bharatiya Learning Center operates as a pan-Indian educational space — a reflection of how the broader diaspora in the Philadelphia suburbs has diversified well beyond the North Indian professional families who first settled there in the 1970s and 1980s.

Guided by the Sanskrit principle *Vidya Dadati Vinayam* — knowledge imparts humility — the curriculum extends beyond vocabulary drills and grammar charts. Students engage with festival traditions, classical arts, and the kind of cultural literacy that parents worry will evaporate in the American suburbs.

For many families, according to the centre's leadership, the facility has become a "home away from home" — a phrase that sounds saccharine until you consider the alternative: Hindi words disappearing from dinner-table conversation by the third generation, grandparents unable to communicate with grandchildren, and an entire culture of oral tradition going quiet.

## The Nand Todi Vision

Shri Nand Todi, the founder and president of Bharatiya Temple, began the project when the Indian-American population in Bucks and Montgomery counties was a fraction of its current size. "This Learning Center represents nearly three decades of vision, perseverance, and community unity," Todi said at the inauguration. "It is a place where heritage will be preserved, values will be nurtured, and future generations will remain deeply connected to their cultural identity."

Twenty-seven years is a long time to build anything by committee, let alone by donations. The $8.5 million price tag was raised entirely within the community — no government grants, no corporate naming rights, no outside institutional money. The funding model mirrors the temple-building tradition that has dotted the American landscape with Hindu, Jain, and Sikh places of worship since the 1970s, but applied this time to a secular educational mission.

## Political Recognition, Quietly Earned

Congressman Fitzpatrick, a Republican representing Pennsylvania's 1st Congressional District, used his remarks to note that communities preserving their heritage "contribute meaningfully to the nation's diversity and unity." Commissioner Makhija — himself Indian American and one of a growing number of South Asian elected officials in the Philadelphia suburbs — emphasised the civic role such institutions play.

The recognition in the Congressional Record, while largely symbolic, matters for a practical reason: it positions Indian-American cultural institutions alongside the Italian-American clubs, Polish community centres, and Jewish cultural foundations that have long been part of the American civic landscape. For a community that has historically invested more in professional credentials than civic infrastructure, the shift is notable.

## A Broader Pattern

The Bharatiya Learning Center is not an isolated project. Across the United States, Indian-American communities are moving from ad hoc cultural programming to permanent institutions. The BAPS Swaminarayan Akshardham in New Jersey, the proposed India Heritage Center in Washington, D.C., and dozens of smaller community centres and language schools collectively suggest a diaspora that is no longer merely settling in America but actively building the physical infrastructure to stay — and to remember.

The timing matters. The inauguration coincides with the approach of America's 250th anniversary, a moment when immigrant communities are being asked, sometimes gently and sometimes not, what they contribute to the national story. The Bharatiya Learning Center, with its seven languages and 200 weekly students, offers one answer: the same thing every other immigrant community has contributed. Roots, replanted."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The India-UK Trade Deal Is Weeks From Taking Effect. Here's What Actually Changes for the Diaspora.",
        "subheadline": "Professional mobility provisions, social security exemptions, and tariff cuts on everything from whisky to textiles — the CETA's fine print matters more for NRIs than the headlines suggest.",
        "slug": make_slug("india-uk-ceta-trade-deal-nri-diaspora-what-changes"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The India-UK CETA directly affects the 1.9 million-strong Indian diaspora in Britain and the tens of thousands of Indian professionals on temporary assignments — from social security contributions to the cost of sending goods home to the ease of professional mobility.",
        "tags": ["nri", "diaspora", "uk", "trade", "ceta", "business", "social-security", "professional-mobility"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "UK Parliament - Commons Library", "url": "https://commonslibrary.parliament.uk/research-briefings/cbp-10120/"},
            {"name": "UK Parliament - Business and Trade Committee", "url": "https://publications.parliament.uk/pa/cm5804/cmselect/cmbeis/"},
            {"name": "RSM Global", "url": "https://rsm.global"},
            {"name": "Blake Morgan LLP", "url": "https://blakemorgan.co.uk"},
            {"name": "ainvest.com", "url": "https://ainvest.com"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6077239/pexels-photo-6077239.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "body": """The India-UK Comprehensive Economic and Trade Agreement, signed in July 2025 after three years of negotiations, is now in the final stretch before it enters into force. Commerce Minister Piyush Goyal has indicated implementation is expected within weeks. When it does take effect, it will be the most economically significant bilateral trade deal the UK has concluded since leaving the European Union — and for the 1.9 million people of Indian origin living in Britain, the practical implications go well beyond tariff schedules.

## The Professional Mobility Piece

The headline provision that matters most for diaspora professionals is not buried in a tariff annex. It is the Double Contributions Convention, a standalone social security agreement negotiated alongside the CETA. Under the DCC, Indian workers on temporary assignments in the UK — typically intra-company transfers of up to three years — will be exempt from paying UK National Insurance contributions.

The maths is straightforward. National Insurance currently costs employers approximately 13.8% of an employee's salary above the threshold. For a senior Indian technology professional transferred to a London office on a £90,000 salary, the exemption represents roughly £10,000 in annual savings for the employer. Multiply that across the thousands of Indian IT professionals rotating through UK offices, and the aggregate figure is substantial.

The provision has not been universally welcomed. Shadow Business Minister Dame Harriett Baldwin argued in Parliament that the DCC risks "subsidising Indian labour while undercutting British workers." The government has pushed back, noting that Indian workers still face significant visa costs and the immigration health surcharge, which together run into thousands of pounds annually. No one, ministers insist, is being undercut.

For NRIs, however, the practical effect is clear: Indian employers will find it cheaper and administratively simpler to post staff to the UK, which should mean more mobility opportunities for Indian professionals — and more of the cross-border assignments that have historically been a career accelerator in the Indian IT services industry.

## What Moves at the Border

On the goods side, India will remove or reduce tariffs on 90% of tariff lines covering 92% of existing UK goods imports. The UK estimates this translates to roughly £400 million in tariff savings immediately, potentially increasing to £900 million after a decade as phased reductions take full effect.

For the diaspora, certain reductions hit close to home. Indian textiles entering the UK will face lower barriers, potentially reducing prices on the saris, kurtas, and fabrics that sustain a thriving import market. In the other direction, UK goods entering India — including Scotch whisky, whose tariff drops from 150% to 40% over ten years, and British automobiles — will become gradually more affordable for NRIs sending gifts home or families splitting time between countries.

Duty-free access for 99% of Indian exports to the UK is particularly significant for the garment, leather, and processed food sectors that employ millions in India and supply diaspora retailers across Britain.

## The Implementation Question

The deal was debated in the House of Commons in February 2026. The Business and Trade Committee described it as significant but warned that its potential "would only be realised if it were implemented successfully." That caveat is not ceremonial. India's regulatory system is notoriously decentralised, with licensing, certification, and documentation requirements varying by state. The parliamentary committee noted that "state-level stubbornness in bringing those barriers down" could blunt the agreement's impact regardless of what the treaty text promises.

For NRI business owners operating between the two countries — and there are thousands, from restaurant chains to technology consultancies to pharmaceutical importers — this means the CETA is a starting point, not a finish line. The tariff reductions are codified, but the non-tariff friction that actually determines whether cross-border commerce is viable will require sustained effort from both governments.

## Beyond Trade: A Relationship Reset

The CETA sits within a broader recalibration of the India-UK relationship. The UK signed its Free Trade Agreement with the Gulf Cooperation Council on May 20, 2026. India has simultaneously operationalised trade deals with Oman and New Zealand. For the Indian diaspora in Britain — many of whom maintain significant family, business, and property ties in India — the CETA represents something more than a trade mechanism. It is the institutional framework through which two countries, linked by history and demography, are trying to make the economic relationship match the human one.

The deal is weeks away. The fine print, for once, is worth reading."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Chief Justice Will Inaugurate a London Conference on Cross-Border Commercial Disputes. The Timing Is Deliberate.",
        "subheadline": "As the India-UK trade deal nears implementation, the Indian Council of Arbitration's 4th international conference at Westminster on June 5 tackles the dispute resolution architecture NRI businesses will need.",
        "slug": make_slug("cji-surya-kant-london-arbitration-conference-indo-uk"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For the thousands of NRI business owners operating between India and the UK — restaurant chains, IT consultancies, pharmaceutical importers, property developers — commercial dispute resolution has historically been expensive, slow, and uncertain. The London conference signals a push to build the legal infrastructure that makes cross-border business practical.",
        "tags": ["nri", "diaspora", "uk", "legal", "arbitration", "business", "cji", "trade"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "LiveLaw", "url": "https://www.livelaw.in/news-updates/ica-4th-international-conference-arbitrating-indo-uk-commercial-disputes-london-june-5-cji-surya-kant-286789"},
            {"name": "Indian Council of Arbitration", "url": "https://www.icaindia.co.in"},
            {"name": "UK Parliament - Commons Library", "url": "https://commonslibrary.parliament.uk/research-briefings/cbp-10120/"}
        ]),
        "score_total": 68,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Justice_Surya_Kant.jpg/3840px-Justice_Surya_Kant.jpg",
        "body": """On June 5, Chief Justice of India Surya Kant will inaugurate the 4th International Conference on Arbitrating Indo-UK Commercial Disputes at Church House, Westminster. The event, organised by the Indian Council of Arbitration, will feature keynote addresses from India's Union Law Minister Arjun Ram Meghwal and Sir Geoffrey Vos, the Master of the Rolls and Head of Civil Justice of England and Wales. It is, on its face, a gathering of lawyers and policymakers. It is also a signal about what comes next for the commercial relationship between India and Britain — and for the NRI businesses that sit in the middle of it.

## Why Arbitration Matters Now

The conference's timing is not accidental. The India-UK Comprehensive Economic and Trade Agreement, signed in July 2025, is expected to enter into force within weeks. When it does, bilateral trade — already valued at roughly £39 billion annually — will operate under a substantially new legal framework: reduced tariffs, new services provisions, and mobility agreements for professionals.

But trade agreements create disputes as surely as they create opportunities. A British distiller shipping whisky to India under the CETA's phased tariff reduction may find the goods held up at a state-level customs checkpoint that has not yet updated its procedures. An Indian IT services company posting engineers to London under the new professional mobility provisions may disagree with a client about deliverables. A diaspora entrepreneur who has invested in Indian real estate under the FEMA framework may face a contractual dispute with a local developer.

In each case, the question is the same: where do you resolve it, how long does it take, and how much does it cost? For cross-border commercial disputes between India and the UK, the answers have historically been unsatisfying. Indian courts are notoriously slow, with commercial cases routinely taking years to reach resolution. English courts are efficient but expensive and procedurally unfamiliar to Indian parties. Arbitration — a private dispute resolution mechanism in which parties agree in advance on a neutral forum, procedural rules, and a binding outcome — is the alternative that trade lawyers on both sides have long advocated.

## The Institutional Architecture

The Indian Council of Arbitration, established in 1965, has been the primary institutional arbitration body in India for international commercial disputes. Its London conference, now in its fourth edition, reflects a deliberate effort to build the institutional credibility needed for Indo-UK arbitration to become routine rather than exceptional.

The presence of both the CJI and the Master of the Rolls — the two most senior judicial figures in their respective systems — is unusual for an arbitration conference and signals high-level backing for the initiative. The conference agenda includes sessions on enhancing investor confidence, ensuring contractual certainty, facilitating legal and professional mobility, and developing a harmonised framework for cross-border commercial relations.

For the ICA, the strategic calculation is straightforward: if the CETA succeeds in expanding Indo-UK trade, the volume of commercial disputes will increase proportionally. The question is whether those disputes will be resolved through arbitration — generating institutional revenue, building legal expertise, and keeping resolution times manageable — or through litigation in overburdened national courts.

## What NRI Business Owners Should Watch

For NRIs operating businesses between the two countries, the conference's practical implications are worth tracking. First, any movement toward a bilateral investment treaty — which the UK parliamentary committee has recommended — would provide NRI investors with formal protections against expropriation and unfair treatment. Second, the development of sector-specific arbitration protocols for industries like technology services, pharmaceuticals, and food and beverage could reduce both the cost and the uncertainty of cross-border disputes.

Third, and most immediately, the DCC's social security provisions and the CETA's professional mobility framework will generate their own category of disputes — disagreements about whether a particular worker qualifies for the exemption, whether a professional service falls within a covered category, or whether a regulatory barrier violates the agreement's terms. Arbitration clauses in commercial contracts between Indian and British firms will increasingly need to anticipate these scenarios.

## The Bigger Picture

India's High Commissioner-designate to the UK, Periasamy Kumaran, will deliver special remarks at the conference alongside Brett Dixon, Vice-President of the Law Society of England and Wales. The breadth of the speaker list — spanning the judiciary, executive, and legal profession of both countries — reflects a recognition that the CETA is only as good as the legal infrastructure supporting it.

Trade deals are written by negotiators, but they live or die in the hands of businesses trying to use them. For the thousands of NRI entrepreneurs, professionals, and investors whose livelihoods span both countries, the question is not whether the CETA exists but whether the dispute resolution architecture exists to make it workable. The June 5 conference is one attempt to answer that question before the disputes begin arriving."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
