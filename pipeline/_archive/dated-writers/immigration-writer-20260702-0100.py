#!/usr/bin/env python3
"""
Immigration writer — 2026-07-02 01:00 PDT
Two articles:
1. EB-1A/NIW self-petition surge among Indians + falling approval rates
2. $100K H-1B fee ruling aftermath: what comes next
"""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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
    # ============================================================
    # ARTICLE 1: EB-1A/NIW Self-Petition Surge
    # ============================================================
    {
        "id": str(uuid.uuid4()),
        "headline": "EB-2 India Went Dark. Now the Escape Routes Are Getting Crowded Too",
        "subheadline": "Indian professionals are flooding EB-1A and NIW self-petition channels to bypass the green card backlog. But USCIS approval rates are falling fast, and the agency is watching.",
        "slug": make_slug("eb1a-niw-self-petition-surge-india-approval-rates-falling"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "With EB-2 India now showing 'Unavailable' on the July visa bulletin, the hundreds of thousands of Indian professionals stuck in the employer-sponsored green card queue face an indefinite wait that may outlast their careers. EB-1A and NIW self-petitions have become the primary escape route — but falling approval rates and tighter USCIS scrutiny mean the window is narrowing.",
        "tags": ["eb-1a", "niw", "green-card", "uscis", "self-petition", "backlog", "eb-2"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "LexBlog — USCIS Data on EB-2 NIW and EB-1A Approval Rates", "url": "https://www.lexblog.com/2026/06/11/what-recent-uscis-data-means-for-eb-2-niw-eb-1a-petitioners/"},
            {"name": "India Times Online — Swatilina Barik on the EB-1A Surge", "url": "https://indiatimesonline.co.in/swatilina-barik-on-the-eb-1a-surge/"},
            {"name": "Mukherji v. Miller, D. Neb. (Jan. 28, 2026)", "url": "https://www.lexblog.com/2026/06/11/what-recent-uscis-data-means-for-eb-2-niw-eb-1a-petitioners/"},
            {"name": "Bipartisan Policy Center — EAGLE Act Analysis", "url": "https://bipartisanpolicy.org/blog/modernizing-americas-legal-immigration-system-piece-by-piece-the-eagle-act/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
        "image_caption": "A USCIS Application Support Center in Queens, New York",
        "image_attribution": "Wikimedia Commons",
        "body": """The July 2026 visa bulletin delivered the news that Indian professionals had been dreading: EB-2 India is now marked "Unavailable." No green cards will be issued in that category until the new fiscal year begins in October — and even then, the backlog stretches decades. For the roughly 800,000 Indian nationals waiting in the employment-based queue, the employer-sponsored path has effectively stalled.

So they are doing what rational people do when the front door is locked: looking for the side entrance.

## The Self-Petition Pivot

EB-1A (Extraordinary Ability) and EB-2 NIW (National Interest Waiver) petitions allow professionals to sponsor themselves for a green card, bypassing both the employer-dependent PERM labour certification and, in many cases, the per-country backlog that traps Indians for decades. Unlike the standard EB-2 and EB-3 categories, EB-1A carries no per-country queue of comparable length — a filed-and-approved petition can lead to a green card in months rather than generations.

The result is a surge in filings. Immigration strategist Swatilina Barik, who works with Indian professionals on EB-1A and NIW cases, points to two drivers. "The obvious one is the EB-2 backlog," she told India Times Online. "An Indian engineer who files EB-2 today is looking at a wait that may outlast their working career."

The less obvious driver, she argues, is generational. "Ten years ago, most senior engineers in India did not have publications, did not judge competitions, and did not sit on standards bodies. Today, many do. So the pool of people who can credibly file has grown, not just the pool of people who want to."

## But the Gate Is Tightening

Here is the problem: USCIS has noticed. And it is responding by raising the bar.

Fiscal year 2025 data paints a sobering picture. The NIW approval rate dropped to 55.2 per cent overall, with Q4 FY2025 falling further to just 35.7 per cent. EB-1A fared somewhat better at 66.9 per cent overall, but its Q4 rate slid to roughly 53 per cent. Both represent significant declines from prior years, when approval rates in these categories routinely exceeded 80 per cent.

For NIW cases, USCIS is applying the *Matter of Dhanasar* framework with heightened rigour, demanding measurable, demonstrated impact on the United States — not forward-looking potential or broad claims about a sector's importance. Healthcare, core STEM, and national-security-adjacent fields continue to fare well. But the software engineer who argues that their work at a mid-tier consulting firm serves the national interest is increasingly likely to receive a denial.

For EB-1A, adjudicators are leaning harder on the two-step "final merits" analysis, treating the three-criteria threshold as a starting point rather than a conclusion. Meeting three of the ten criteria gets your foot in the door; it no longer gets you through it.

## A Court Pushes Back

Not everyone agrees that USCIS has the authority to move the goalposts. In *Mukherji v. Miller* (D. Neb., January 28, 2026), a federal district court questioned whether the agency properly adopted the two-step framework and ordered an EB-1A petition approved after USCIS conceded the petitioner met five of the ten criteria. The decision is limited to that case, and USCIS has not changed its guidance. But it represents the first notable judicial pushback against the increasingly aggressive posture.

Immigration attorneys say the case may provide ammunition for future appeals, particularly where a strong record is denied on vague or conclusory reasoning.

## What This Means for Indian Professionals

The arithmetic is unfriendly. With EB-2 India dark, EB-5 India's unreserved quota exhausted for FY2026, and employer-sponsored paths growing slower and more expensive, self-petition routes are the most viable option for many mid-career Indian professionals. But those routes are narrowing precisely because demand is surging.

The practical guidance from immigration lawyers is consistent: start building an EB-1A or NIW case years before you plan to file. Publish in peer-reviewed venues. Serve as a reviewer or judge. Document your contributions' impact in concrete, quantifiable terms — revenue generated, systems adopted, patents cited. The days of filing a "good enough" petition and trusting the approval rates are over.

For the Indian professional on an H-1B with a decade-old priority date that has not moved, the self-petition route remains the best path available. It is just no longer the easy one."""
    },
    # ============================================================
    # ARTICLE 2: $100K H-1B Fee Ruling Aftermath
    # ============================================================
    {
        "id": str(uuid.uuid4()),
        "headline": "A Federal Judge Killed the $100,000 H-1B Fee. The White House Says It Is Coming Back",
        "subheadline": "The court ruled Trump's fee was an unconstitutional tax. The administration called it 'crazy' and vowed to appeal. For Indian H-1B holders, the legal victory may be the easy part.",
        "slug": make_slug("100k-h1b-fee-ruling-appeal-whats-next-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals account for over 70 per cent of all H-1B approvals. The $100,000 fee, imposed in September 2025, hit Indian-dependent employers hardest. The court ruling provides immediate relief, but the administration's appeal and alternative procedural tactics could create fresh uncertainty for hundreds of thousands of Indian professionals and their families.",
        "tags": ["h1b", "100k-fee", "court-ruling", "uscis", "trump", "appeal"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Trump's $100,000 H-1B visa fee is unlawful, US judge rules", "url": "https://www.reuters.com/world/us/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/"},
            {"name": "The Indian Eye — US Judge blocks, Lawmakers cheer, Trump lambasts", "url": "https://theindianeye.com/2026/06/09/100000-h-1b-visa-fee-us-judge-blocks-lawmakers-cheer-and-trump-lambasts/"},
            {"name": "Reason.com — Federal Court Invalidates $100K H-1B Fee", "url": "https://reason.com/2026/06/09/federal-court-invalidates-trumps-100000-h-1b-visa-fee-as-illegal-usurpation-of-congress-power-to-tax/"},
            {"name": "Livemint — Expert says 'sigh of relief but...'", "url": "https://www.livemint.com/news/india/100000-h1b-visa-fee-struck-down-expert-says-sigh-of-relief-but-why-it-matters-for-indians-11749462000123.html"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16151491/pexels-photo-16151491.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "A neoclassical government building in Washington, DC with American flag and cherry blossoms",
        "image_attribution": "Pexels",
        "body": """On June 9, U.S. District Judge Leo Sorokin in Boston did what the tech industry, universities, and roughly 300,000 Indian H-1B holders had been hoping for: he struck down President Trump's $100,000 fee on new H-1B visa applications, ruling that it was an unconstitutional tax that Congress never authorised.

The ruling, in *California v. Mullin*, was filed by 20 Democratic state attorneys general. Sorokin's reasoning was direct. The administration had framed the fee as a "penalty" to deter employers from using foreign labour. Sorokin said it was a tax, regardless of what the administration called it, and the president has no power to levy taxes without Congress.

"Here, the substance and application of the $100,000 payment reveal that it is a tax, regardless of what the payment is called," Sorokin wrote. He cited the Supreme Court's February ruling in *Learning Resources v. Trump*, which struck down the president's sweeping tariffs as an overreach of executive authority. If the president cannot unilaterally impose tariffs, Sorokin reasoned, he cannot unilaterally impose a $100,000 tax on visa applications either.

The White House did not take it well.

## 'Crazy,' Says the President

Trump described the ruling as "crazy" and part of a pattern of judicial interference with his immigration agenda. White House spokeswoman Taylor Rogers said the administration was "confident" the order would be reversed on appeal. "President Trump has clear legal authority to restrict entry of any class of aliens he determines is not in America's best interests," she said.

The Department of Homeland Security went further, calling the ruling "blatant judicial activism dismantling President Trump's historic efforts for immigration reform."

But the political landscape has shifted. Several Republican lawmakers — typically aligned with the White House on immigration — broke ranks to support the ruling. Their argument was not about protecting Indian IT workers, but about protecting rural hospitals and universities. The $100,000 fee, they pointed out, would cripple small-town healthcare systems that depend on international medical graduates and gut university research departments that hire specialised foreign faculty.

The American Association of Physicians of Indian Origin called the ruling "a healthcare victory, not a political one." AAPI President Dr Amit Chakrabarty warned that the fee would have forced hospitals to withdraw employment offers, leaving critical vacancies unfilled.

## The Contradictory Legal Landscape

The Sorokin ruling is not the final word. In a separate case filed by the U.S. Chamber of Commerce, a different federal judge in Washington, D.C. — Judge Beryl Howell — had ruled *in favour* of the administration, finding that Congress did give the president authority to impose the fee. That earlier ruling, however, came before the Supreme Court's tariff decision, which reshaped the legal terrain.

The administration is expected to appeal Sorokin's ruling to the First Circuit Court of Appeals. Until that appeal is resolved — or the Supreme Court takes up the issue — employers face contradictory guidance. The fee has been vacated in Boston, but the D.C. ruling provides the administration with a foothold to argue it is still enforceable.

## What Comes After the Fee

For Indian professionals, the real worry is not whether the $100,000 fee returns. It is what the administration does instead.

Sanjeev Joshipura, Executive Director of Indiaspora, captured the uncertainty. "All stakeholders connected with H-1B visas will heave a sigh of relief after the court order," he told PTI. "But one wonders if this is truly the end of the matter."

He warned that the administration could impose "procedural impediments" that achieve the same goal — making H-1B hiring more expensive and uncertain — without running afoul of the courts. The options include more aggressive Requests for Evidence (RFEs), longer processing times, higher denial rates at the adjudication stage, and stricter interpretations of "specialty occupation."

The evidence suggests this is already happening. USCIS's 11-million-case backlog, the new wage-weighted lottery that favours senior roles over entry-level positions, and the signature rule taking effect on July 10 — which could result in automatic denials for improperly signed petitions — all point in the same direction. The system is being restructured to admit fewer H-1B workers, one procedural change at a time.

## The India Dimension

Indian nationals account for over 70 per cent of H-1B approvals annually. No other country comes close. The fee, had it survived, would have fallen disproportionately on Indian-dependent employers — IT services firms, hospital systems, and universities with large foreign-worker contingents.

India's foreign ministry called the fee "likely to have humanitarian consequences by way of the disruption caused for families." The diplomatic language was notably restrained. Behind the scenes, Indian trade negotiators have been pressing the visa issue as part of broader India-U.S. bilateral talks, though as The Videshi reported earlier this week, the trade deal that is "99 per cent done" conspicuously omits any mention of talent mobility.

For the Indian engineer on an H-1B, the court ruling is good news. But it is also a reminder that their status in the United States is increasingly determined not by their skills or their employer's willingness to sponsor them, but by which judge hears the case, which circuit reviews the appeal, and which procedural rule USCIS decides to enforce on any given Tuesday.

The fee may be dead. The uncertainty is very much alive."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
