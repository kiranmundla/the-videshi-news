#!/usr/bin/env python3
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
    {
        "id": str(uuid.uuid4()),
        "headline": "Razorpay Came Home to India, Then Quietly Filed to Go Public. The Reverse-Flip Era Has Its Marquee Test.",
        "subheadline": "The payments giant filed confidential IPO papers with SEBI, seeking up to $700 million at a valuation reset to $5-6 billion. After a costly move from Delaware back to Bengaluru, its listing is a referendum on whether Indian startups belong on Indian exchanges.",
        "slug": make_slug("razorpay-confidential-ipo-sebi-reverse-flip-india-fintech"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "For NRIs who built or backed Indian startups through US holding structures, Razorpay's expensive journey home and its listing on an Indian exchange is the clearest signal yet that the centre of gravity for Indian tech value creation has shifted from Delaware and Nasdaq back to Bengaluru and Dalal Street.",
        "tags": ["fintech", "razorpay", "ipo", "reverse-flip", "indian-startups"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Upstox", "url": "https://upstox.com/news/business-news/latest-updates/razorpay-files-confidential-papers-with-sebi-for-a-potential-600-million-ipo/"},
            {"name": "Inc42", "url": "https://inc42.com/buzz/razorpay-to-soon-file-confidential-drhp-to-raise-600-700-mn-report/"},
            {"name": "5paisa", "url": "https://www.5paisa.com/news/razorpay-files-confidential-ipo-papers-with-sebi"},
            {"name": "Entrepreneur India", "url": "https://www.entrepreneur.com/en-in/news-and-trends/razorpay-plans-confidential-ipo-filing/"}
        ]),
        "score_total": 81,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/BSE_building_at_Dalal_Street.JPG/1280px-BSE_building_at_Dalal_Street.JPG",
        "image_caption": "The Bombay Stock Exchange building on Dalal Street, Mumbai. Razorpay has filed confidential IPO papers with SEBI, aiming for a main-board listing on India's exchanges.",
        "image_attribution": "Wikimedia Commons",
        "body": """Two years ago, Razorpay made a decision that looked, on a spreadsheet, like setting money on fire. The payments company unwound its US holding structure and moved its corporate parent from Delaware back to India — a "reverse flip" that reportedly cost it around $150 million in taxes. Founders rarely pay nine figures for paperwork. They do it when they are preparing for something that has to happen at home.

This month, the something arrived. Razorpay has confidentially filed its draft red herring prospectus with the Securities and Exchange Board of India, the first formal step toward an initial public offering on India's main-board exchanges.

## What was filed

In a public notice, the Bengaluru company said it had pre-filed the prospectus with SEBI and the stock exchanges "in relation to the proposed initial public offering of its equity shares on the main-board." It used the confidential route — increasingly the default for India's new-age firms — which lets a company submit its numbers to the regulator without immediately exposing sensitive financials to competitors and the public.

The reported shape of the deal: roughly $600 million to $700 million raised, through a mix of fresh shares and an offer for sale that lets early investors cash out, at a valuation of about $5-6 billion. Axis Capital, JPMorgan, Kotak Mahindra Capital and Citi are the book-running lead managers. The DRHP filing follows the appointment of those banks earlier this year.

## The number that tells the story

That $5-6 billion target is the most revealing figure in the entire filing, because Razorpay was last valued privately at $7.5 billion more than four years ago. The company is going public at a discount to its own peak.

This is not a Razorpay problem; it is a market correction. The era of soaring private valuations has given way to public investors in India who reward profit visibility over growth narratives. Razorpay's own accounts show why the discipline matters. Its consolidated operating revenue jumped 65% to ₹3,783 crore in FY25, and gross profit rose 41% to ₹1,277 crore — genuinely strong operating numbers. Yet it posted a net loss, driven largely by a ₹1,209 crore charge tied to employee stock options and the costs of the reverse flip itself. The headline loss is, in large part, the price of coming home.

## Why the reverse flip is the real headline

For a generation of Indian startups, the standard playbook was to incorporate the parent company in the United States — easier to raise dollars, friendlier to global investors, a cleaner path to a Nasdaq dream. Razorpay, founded in 2014 by IIT-Roorkee graduates Harshil Mathur and Shashank Kumar, followed that script.

Then the script flipped. As India's public markets deepened and domestic capital grew abundant, the logic of being domiciled abroad weakened — and the logic of listing where your customers, revenue and regulators live grew stronger. Razorpay joins PhonePe, Groww, Meesho and others in physically relocating to India before going public. The tax bill on that move is steep and one-time. The bet is that an Indian listing, with Indian institutional and retail demand, ultimately delivers a better, more durable home for the stock.

## Why the diaspora should care

This is one of the most consequential India-tech stories for the diaspora precisely because so many NRIs are entangled in the old structure. Indian-American founders, angel investors and fund managers spent a decade building Indian companies through Delaware shells and Mauritius vehicles. Razorpay's journey home — and the visible cost of it — is a live case study in what unwinding that looks like, and whether the destination justifies the toll.

There is also the matter of access. A Nasdaq listing is trivially easy for an NRI to buy; an Indian main-board IPO is harder to participate in from abroad, routed through specific NRI investment channels. As more marquee Indian tech names choose to list at home, the diaspora faces a quietly significant question: the companies they are emotionally and professionally closest to are becoming, in market terms, slightly further away.

## What's next

The confidential route means the full prospectus — and Razorpay's detailed financials — will surface only when SEBI clears the draft and the company opts to go public with it. Watch for three things: the final split between fresh capital and secondary sales, the valuation the company actually prices at versus the $5-6 billion target, and the timing, given that peers like PhonePe have paused listings amid geopolitical jitters.

Razorpay paid to come home. Now it finds out what home is worth."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "An AI That Refuses to Answer Until It Can Prove It Is Right. IIT Madras Alumni Just Raised $27 Million to Build It.",
        "subheadline": "Pramaana Labs, backed by Vinod Khosla, is wrapping large language models in mathematical proof engines so AI can be trusted in tax, law and medicine. Half its team sits in India — a bet that the next AI breakthrough is reliability, not raw intelligence.",
        "slug": make_slug("pramaana-labs-khosla-formal-verification-ai-iit-madras"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Founded by IIT Madras alumni with half its workforce in India and led by a round from Indian-American legend Vinod Khosla, Pramaana embodies the US-India deep-tech bridge: the hardest problems in AI being attacked by Indian engineering talent on both sides of the Pacific.",
        "tags": ["artificial-intelligence", "pramaana-labs", "vinod-khosla", "deep-tech", "indian-founders"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/18/pramaana-labs-raises-27m-seed-round-from-khosla-ventures-to-bring-formal-verification-to-ai/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/pramaana-labs-raises-27-million-to-build-verifiable-ai-systems/article69730000.ece"},
            {"name": "GlobeNewswire", "url": "https://www.globenewswire.com/news-release/2026/06/18/pramaana-labs-raises-27m-led-by-khosla-ventures.html"}
        ]),
        "score_total": 77,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/2024-03-14_SXSW_Vinod-Khosla_08741.jpg/1280px-2024-03-14_SXSW_Vinod-Khosla_08741.jpg",
        "image_caption": "Vinod Khosla, whose firm Khosla Ventures led Pramaana Labs' $27 million seed round. The Indian-American venture capitalist was an early backer of OpenAI.",
        "image_attribution": "Wikimedia Commons",
        "body": """The dirty secret of the generative-AI boom is that nobody fully trusts the machine. A doctor still reads the diagnosis. A lawyer still checks the brief. An accountant still signs the return. The AI drafts; the human takes the liability. In the highest-stakes corners of the economy — tax, law, medicine, financial compliance — the technology that was supposed to replace expert judgment has instead become an expensive intern that needs constant supervision.

A startup founded by three IIT Madras alumni thinks it can close that gap, and on June 18 it raised $27 million to try.

## What Pramaana is building

Pramaana Labs announced the seed round — about ₹255 crore — led by Khosla Ventures, the firm built by Indian-American investor Vinod Khosla, with participation from Accel, BoldCap, Nexus Venture Partners, Premji Invest and Unbound. Its early backers include Pushmeet Kohli, a vice-president at Google DeepMind, and Sriram Rajamani of Microsoft.

The company's pitch is captured in a single phrase: taking AI "from probably right to provably right." A conventional large language model is probabilistic — it predicts a likely answer, which is why it can sound confident and be wrong. Pramaana wraps that model in a layer of formal verification. It encodes the actual rules of a domain — the US tax code, clinical protocols, financial regulations — into a formal language a machine can reason over with mathematical certainty, using the open-source LEAN proof language originally built to verify mathematical proofs.

When a user asks a question, the system translates it into a formal statement, runs it through a proof engine, and either returns a machine-checkable proof that the answer is correct, or tells the user exactly which rule breaks and why. "It will refuse to answer before it proves," the company says — and claims it has never produced a confidently wrong verified answer.

## Why this is a different bet

Most of the AI industry is racing in one direction: bigger models, more parameters, more raw intelligence. Pramaana is betting the bottleneck is somewhere else entirely. "AI has an accountability gap," said co-founder and CEO Ranjan Rajagopalan. "The world's hardest problems are not unsolvable. They are unformalized."

The insight is that domains like tax law only look messy. Underneath, they are rule systems — and rule systems can be codified. "It's like math in the sense that you have a lot of rules that you need to abide by," Rajagopalan told TechCrunch. "Once you have a codified version of it, the reasoning on top of it starts becoming deterministic." There is precedent: France's CATALA project has formalized much of that country's tax and benefit system into executable code.

Khosla, an early backer of OpenAI, framed the appeal bluntly — auto-formalization addresses a capability today's AI simply lacks. For a domain where being wrong can cost someone their health, their money or their freedom, a system that proves its answers turns the human in the loop from a liability shield into a genuine beneficiary.

## The India thread

Pramaana is a San Francisco company, but it is, in a deeper sense, an Indian one. Its three founders — Rajagopalan, Krishnan Raghavan and Sanjay Ganapathy Subramaniam — are IIT Madras alumni who cut their teeth at Google Maps, Glean and Google DeepMind's Gemini team respectively. Roughly half its workforce sits in India.

That structure — a US headquarters, deep Indian engineering bench, Indian-American capital — is the template for a growing class of frontier startups. The hardest problems in AI are increasingly being attacked by Indian talent operating on both sides of the Pacific, with the research split across Bengaluru and the Bay Area. Pramaana is not a back-office or services play; it is foundational AI research, the kind India has long supplied engineers for but less often headlined.

## Why the diaspora should watch

For the Indian diaspora in technology, Pramaana is a flattering mirror. It pairs IIT pedigree with the validation of Vinod Khosla, perhaps the most storied Indian-American in venture capital, attacking a problem — trustworthy AI for regulated industries — that sits at the centre of the next phase of the boom. For NRIs working in law, medicine, accounting and finance, it is also directly relevant: these are precisely the professions where a "provably right" AI could reshape daily work.

## What's next

The capital goes toward training Pramaana's formalization and prover models, expanding its research team, and onboarding domain experts across tax, healthcare diagnostics, cybersecurity and financial compliance. The hard test is breadth: formalizing one domain is a research project; formalizing many, reliably and at commercial scale, is a company. If it works, the human in the loop stops being a safety net and AI finally gets to be the expert it was always sold as."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}  [{len(art['body'].split())} words]")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
