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

body1 = """Alphabet shed roughly a quarter of a trillion dollars in market value on Monday, its worst single-day fall in more than a year. The trigger was not an earnings miss or a regulatory ruling. It was two resignation letters.

Within days of each other, Noam Shazeer—one of the authors of the 2017 "Attention Is All You Need" paper that gave the world the transformer, and most recently co-lead of Gemini—left for OpenAI. Then John Jumper, the DeepMind vice-president who shared the 2024 Nobel Prize in Chemistry for AlphaFold, announced on X that after nearly nine years he was joining Anthropic. Markets read the departures as a verdict on Google's standing in the AI race, and marked the stock down 5.5%.

## Why two people moved $250 billion

The arithmetic is brutal, but it is not irrational. Modern frontier-AI capability is concentrated in a startlingly small number of people, and the market now prices those people the way it once priced oil fields. "Losing John is a big loss for Google and there is no way to sugarcoat it," Wedbush analyst Dan Ives told Barron's, adding that Anthropic "got a special one."

Jumper ran DeepMind's AI-for-science division and had latterly been pulled toward the unglamorous but lucrative problem every lab is now chasing: AI coding tools for enterprises. According to Bloomberg, that is precisely where Google has struggled—former employees describe a company with no obvious answer for businesses that want what Anthropic's Claude and OpenAI's models already deliver. The talent is voting with its feet toward the labs that are winning commercially, not just scientifically.

## The diaspora reads this differently

For the tens of thousands of Indian engineers inside Google, Microsoft, Meta and the AI labs, the Shazeer-Jumper exits are not abstract. They are a live data point about leverage. Sundar Pichai, himself an IIT Kharagpur graduate who arrived in the US on an H-1B, presides over a workforce in which Indian-origin researchers are heavily represented in exactly the divisions—DeepMind, Cloud, Search AI—now bleeding senior people.

The encouraging signal for an Indian engineer in Mountain View or Bengaluru is that scarce AI skill has rarely been more bankable. Anthropic and OpenAI are hiring aggressively, both are circling IPOs, and a new lab, Core Automation, founded this year by a former OpenAI research VP, has already poached DeepMind staff. Mobility is high and compensation is climbing. The cautionary signal is the flip side of the same coin: when value rests on a handful of names, the engineers one rung below the Nobel laureates are the ones expected to absorb the workload when a star leaves—often on visas that tie them to a single employer.

That visa asymmetry is the quiet subtext. A US-born researcher can walk from Google to Anthropic in a weekend. An H-1B holder weighing the same move must re-run the petition, the wage level and the green-card queue before saying yes. The defections making headlines are, disproportionately, by people free to defect. For the diaspora, the lesson is less "follow the stars out the door" and more "build the kind of specialised, hard-to-replace expertise that makes an employer fight to keep you—and sponsor you."

## What it means for Google, and for the talent inside it

Google is not short of money or researchers, and its stock is still up about 11% this year. But the 2023 merger of the science-minded DeepMind with the product-focused Google Brain has, by multiple accounts, left some researchers chafing, and the company's difficulty turning lab brilliance into enterprise coding revenue is now a market-moving liability.

For Indian professionals, the practical takeaways are concrete. First, the AI-coding-tools fight—Claude Code, Copilot, OpenAI's enterprise stack—is where hiring and budgets are flowing; engineers who can ship in that space are insulated. Second, the labs poaching talent are pre-IPO, which means equity, not just salary, is back on the table for those willing to take startup risk. Third, the centre of gravity is fluid: a Nobel laureate just decided a nine-year institution was worth leaving, which should make every senior engineer ask what their own optionality is actually worth.

Alphabet will recover the headline number; stocks do. What it cannot easily buy back is the signal sent to its own people about where the frontier now lives."""

body2 = """India's pitch to the global chip industry has always had a hole in the middle of it. The country could offer land, subsidies and a billion-strong market. What it could not credibly promise was the one input a fab cannot run without: tens of thousands of trained semiconductor engineers. This week, Ashwini Vaishnaw, the minister overseeing the India Semiconductor Mission, tried to turn that gap into the country's strongest sales argument.

The global semiconductor industry, worth around $800 billion today, will cross $1 trillion within a year and is on course to need a million additional skilled professionals, Vaishnaw said. The world, in other words, is short of exactly the people India produces in volume. "We will establish the world's best design facilities," he said—reframing a talent shortage that worries Taiwan, the US and Europe as India's opening.

## The numbers behind the pitch

The claim is not pure rhetoric. India now has 12 approved projects under the Semiconductor Mission, with roughly ₹1.64 trillion in proposed investment, anchored by Tata Electronics' ₹91,000-crore AI-enabled fab in Dholera and Micron's assembly-and-test plant near Sanand. But the more telling effort is upstream, in the classroom. The government has equipped about 270 universities with the same electronic-design-automation tools—from Synopsys, Cadence, Siemens and others—that working chip designers use. In 2025 alone students logged over 1.2 crore tool-usage sessions, and 20 chips designed by 17 institutions have already been fabricated at the Semi-Conductor Laboratory in Mohali. The stated target: 85,000 trained design engineers over a decade.

## Why an NRI should be paying attention

For the Indian diaspora, this is one of the rare India-tech stories that cuts across investing, career and identity at once.

Start with the professionals. Thousands of Indian-origin engineers sit inside Intel, Nvidia, AMD, Qualcomm, Micron, TSMC's US operations and Applied Materials—often the very people who would design, equip or run a fab. For years, the only direction of travel was outward: train in India, build a career in Phoenix, Austin or Hillsboro. Vaishnaw is, in effect, dangling the first credible reverse option in a generation—senior roles in a fast-scaling domestic industry, backed by state money, for those weighing a return. It is not yet a flood, and salaries still lag Silicon Valley, but the door that was painted shut is now ajar.

Then the investors. NRIs tracking the listed proxies—Tata Group entities, Kaynes, CG Power, Micron itself—are watching whether India can move from packaging and assembly (the back end of the value chain) to actual wafer fabrication (the front end, where the margins and the strategic weight sit). The talent build-out is the leading indicator. A fab without engineers is an expensive building; the EDA-in-universities programme is the cheapest, fastest part of de-risking the whole bet.

## The gap between a press release and a wafer

Skepticism is warranted, and the diaspora's engineers know the difference better than most. Designing a chip on academic EDA software is not the same as yield-managing a 300mm line at 3am. India's first fully homegrown fabricated chips are powering smart electricity meters, not data-centre GPUs—a deliberately modest start. The hardest roles, in process engineering and fab operations, take years of on-the-line experience that no university programme can shortcut, which is precisely why luring back diaspora veterans matters so much.

There is also the macro backdrop. With the US-China chip war reshaping supply chains and Washington pressing allies to diversify away from Taiwan, India is selling neutrality and scale at the same moment buyers are desperate for both. Vaishnaw's framing—India as the answer to a global million-person shortfall—is shrewd because it is the one part of the chip pitch where the country genuinely has an edge.

For an NRI semiconductor professional in California, the question is no longer whether India can build fabs. It is whether the design talent now being minted in 270 campuses, plus the experienced hands willing to come home, can arrive fast enough to fill them. The answer to that will decide whether this decade's most ambitious industrial bet pays off—and whether the diaspora helps cash the cheque."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Two Resignations Wiped $250 Billion Off Google. For Indian Engineers in AI, the Real Lesson Is About Leverage.",
        "subheadline": "A Nobel laureate left DeepMind for Anthropic and a transformer co-author left for OpenAI within days. The defections say as much about visa-bound talent as about Google.",
        "slug": make_slug("google-deepmind-jumper-shazeer-defect-anthropic-openai-indian-engineers-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-origin researchers are heavily represented in exactly the AI divisions now losing senior talent, but H-1B holders can't switch jobs as freely as the stars making headlines, so the real lesson for the diaspora is building hard-to-replace, sponsorship-worthy expertise.",
        "tags": ["ai", "google", "deepmind", "anthropic", "openai", "h1b", "indian-tech", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Times", "url": "https://www.thetimes.com/business-money/technology/article/billions-wiped-off-alphabet-ai-researchers-defect"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/alphabet-google-stock-deepmind-nobel-anthropic"},
            {"name": "PYMNTS", "url": "https://www.pymnts.com/artificial-intelligence-2/2026/googles-nobel-winning-ai-expert-departing-for-anthropic/"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/google-stock-ai-scientists-defect-openai-anthropic/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Alphabet and Google CEO Sundar Pichai, whose company lost two senior AI researchers in days",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The World Will Be Short a Million Chip Engineers. India Just Made That Its Pitch.",
        "subheadline": "Ashwini Vaishnaw says India can fill the global semiconductor talent gap. For NRI chip professionals, it is the first credible reason in a generation to consider coming home.",
        "slug": make_slug("india-semiconductor-talent-gap-vaishnaw-million-engineers-nri-return"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Thousands of Indian-origin engineers at Intel, Nvidia, Micron and TSMC are exactly the talent India needs; the government's design-skilling push is the first credible reverse-migration and investment signal in a generation for the diaspora.",
        "tags": ["semiconductors", "india-semiconductor-mission", "chips", "tata-electronics", "micron", "indian-tech", "nri-careers"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Inshorts / Mint", "url": "https://www.livemint.com/industry/india-semiconductor-mission-talent-gap-ashwini-vaishnaw"},
            {"name": "IANS", "url": "https://ianslive.in/world-to-face-1-million-semiconductor-talent-shortfall-by-2030-india-to-bridge-the-gap"},
            {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/india-advances-toward-training-85000-semiconductor-engineers/"},
            {"name": "Press Information Bureau", "url": "https://pib.gov.in/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/35/Ashwini_Vaishnaw_cropped.jpg",
        "image_caption": "Union Electronics and IT Minister Ashwini Vaishnaw, who oversees the India Semiconductor Mission",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": body2
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK  {art['slug']}")
    except Exception as e:
        print(f"ERR {art['slug']}: {e}")
