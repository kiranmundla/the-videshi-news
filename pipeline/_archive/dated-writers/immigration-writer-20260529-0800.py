#!/usr/bin/env python3
"""Immigration writer — 2026-05-29 08:00 UTC run."""

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


# ── Article 1 ──────────────────────────────────────────────────────────────

article1_body = """She spoke three languages in American courtrooms for 25 years. TSA handed her name to ICE, and she spent 45 days in a detention center.

Meenu Batra was on her way to interpret Punjabi at a jury trial in Milwaukee when Customs and Border Protection officers pulled her out of the TSA line at Valley International Airport in Harlingen, Texas. It was March 17. By that afternoon she was in handcuffs. By that evening she was in a cell at the El Valle Detention Center in Raymondville.

The Department of Homeland Security called her an "illegal alien" and said she was arrested during a "targeted enforcement operation." A federal judge later wrote that Batra "was arrested and detained for no discernible reason, with no identified change in circumstance bearing on the likelihood of removal."

## How the TSA Pipeline Works

A Reuters investigation earlier this year found that TSA has shared more than 31,000 domestic traveler records with Immigration and Customs Enforcement since February 2025, leading to over 800 arrests. The mechanism is straightforward: TSA scans boarding passes and IDs at checkpoints, cross-references names against immigration databases, and flags travelers for ICE officers waiting at the gate.

For Indian Americans — many of whom fly frequently between tech hubs and family across the country — the implications are unsettling. Anyone with a pending visa application, an expired status, or even a decades-old immigration record could theoretically be flagged during a routine domestic flight.

## A Survivor of 1984

Batra's story reaches back to one of the darkest chapters in Indian history. Her parents were among the thousands of Sikhs killed in the organized pogroms that followed Indira Gandhi's assassination in 1984. She arrived in the United States in 1991, an 18-year-old refugee who had lost everything.

An immigration judge gave her a final order of removal in 2000 — but the same day, granted her withholding of removal, a legal protection that says she cannot be deported to India. The government never appealed. For 25 years she lived, worked, raised four American citizen children, and became the only certified Hindi, Punjabi, and Urdu courtroom interpreter in all of Texas.

None of that mattered at the airport.

## The Detention

Batra spent 45 days at El Valle, where she said she used her legal knowledge to help fellow detainees — many of whom had been locked up for years — understand their rights. Her daughter hired an immigration lawyer. On April 30, Federal Judge Rolando Olvera granted a temporary restraining order, ruling that DHS must release Batra and could not re-detain her without providing reasons and an opportunity to respond.

One of Batra's sons had enlisted in the military months before her arrest, which may eventually open a path to a green card through the parole-in-place program. But the legal road remains uncertain.

## What Indian Americans Should Know

The TSA-to-ICE pipeline does not discriminate by visa category. H-1B holders with a pending I-485, F-1 students on OPT with gaps in status, green card applicants who traveled during processing — all are potentially visible in the system. Immigration attorneys now routinely advise clients to carry complete documentation when flying, including approval notices, EAD cards, and attorney contact information.

The ACLU and the National Immigration Law Center have both issued guidance urging travelers to memorize three phrases if approached by immigration officers: "I do not consent to a search," "I wish to remain silent," and "I want to speak with a lawyer."

Batra's attorney, Deepak Ahluwalia, put it more simply: "We need to bring compassion and the human element back to immigration enforcement. Otherwise, we're going to lose ourselves."

Batra herself, despite everything, says she has kept her faith in the country that once gave her refuge. "America is based on people who want to work hard," she said. "I believe we must stand up for those ideals."

The question is whether the system that once protected her still has room for that belief."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "She Interpreted for American Courts for 25 Years. Then TSA Gave Her Name to ICE.",
    "subheadline": "Meenu Batra, a Sikh survivor of the 1984 pogroms, was detained at a Texas airport after the agency shared 31,000 traveler records with immigration enforcement.",
    "slug": make_slug("tsa-ice-airport-pipeline-meenu-batra-indian-interpreter"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The TSA-to-ICE data pipeline affects every Indian American who flies domestically — especially H-1B holders with pending green cards, F-1 students on OPT, and anyone with a historical immigration record. Batra's case shows how decades-old records can surface with zero warning.",
    "tags": ["tsa", "ice", "airport-enforcement", "sikh", "1984-pogrom", "detention", "h1b", "immigration-enforcement"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "CNN", "url": "https://www.cnn.com/2026/05/26/us/texas-meenu-batra-interpreter-dhs"},
        {"name": "Reuters (TSA-ICE data sharing investigation)", "url": "https://www.reuters.com"},
        {"name": "USA Today (ICE detains hundreds using TSA records)", "url": "https://www.usatoday.com"},
        {"name": "ACLU", "url": "https://www.aclu.org"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/2574091/pexels-photo-2574091.jpeg",
    "image_caption": "A traveler enters the security checkpoint at O'Hare Airport. TSA now shares domestic flight records with ICE.",
    "body": article1_body
}


# ── Article 2 ──────────────────────────────────────────────────────────────

article2_body = """Governor Kathy Hochul signed the most aggressive anti-ICE legislation in the country on Wednesday — and the first legal challenge landed within 24 hours.

Tucked inside New York's $268 billion state budget, passed nearly two months late on May 27, sits a package of provisions that fundamentally reshape how state and local law enforcement interact with federal immigration authorities. Local police are now barred from contacting or cooperating with ICE in most circumstances absent a judicial order. The 287(g) agreements that gave local jails a direct line to federal immigration agents? Banned. A new "Office of Immigrant Trust" under Attorney General Letitia James will oversee compliance.

For the roughly 800,000 Indian Americans in the New York metro area — one of the largest concentrations of the Indian diaspora anywhere in the world — this is the most consequential state-level immigration development since Trump's second-term enforcement expansion began.

## What the Law Actually Does

The provisions are broad. State and local officers cannot assist in civil immigration enforcement unless a judge signs off. Police cannot hold someone solely on an ICE detainer request. Local agencies cannot share information about an individual's immigration status with federal authorities without a warrant. ICE agents are barred from entering nonpublic areas of state and local facilities — courthouses, schools, hospitals — without judicial authorization.

The legislation also creates a formal process for individuals to file complaints if they believe local officials violated the new restrictions.

This matters in practice. An Indian national on H-1B status who gets pulled over for a broken taillight in Manhattan will not have their immigration status checked or shared with ICE. A green card applicant called to traffic court in Queens will not encounter ICE agents in the hallway. A family dealing with a domestic dispute in Jersey City — well, that is New Jersey's problem. But across the Hudson, the shield is now statutory.

## The Showdown

Within hours of Hochul's signature, Nassau County Executive Bruce Blakeman — a Republican gubernatorial candidate — announced he would refuse to unwind his county's cooperation agreement with ICE, which gives the agency space in Nassau County's jail.

"What's going on up here in Albany is a disgrace to the people of this state," Blakeman said outside the state capitol. "We will take them to court."

The law starts a 90-day clock for jurisdictions like Nassau to end their ICE partnerships. If Blakeman does not comply, enforcement falls to James's new Office of Immigrant Trust. Sheriffs across the state have reportedly contacted Blakeman about joining a legal challenge.

Hochul seemed unworried. "I'm proud to lean into this," she told reporters. "My job is to protect people, but also not to allow the continued harassment that has occurred under the Trump administration."

## The Federal Backdrop

New York's move arrives in a hostile federal environment. DHS Secretary Markwayne Mullin has repeatedly threatened to shut down customs operations at airports in sanctuary jurisdictions — a move that would cripple JFK, LaGuardia, and Newark, three of the busiest international gateways in the country. The Trump administration has already sued four states for denying ICE undercover license plates.

The question for Indian Americans in New York is whether a state-level shield actually protects anyone when the federal government controls airports, borders, and the immigration court system. The answer is complicated: state law cannot stop ICE from conducting its own operations on federal property or through federal channels. What it can do is close the local data pipelines — the traffic stop that becomes an immigration inquiry, the jail booking that becomes a deportation referral.

## What NRIs in New York Should Know

For H-1B holders, green card applicants, and undocumented family members living in New York, the practical effect is meaningful but narrow. You are less likely to be flagged during routine interactions with local government. But federal enforcement channels — airports, ICE's own operations, the TSA data pipeline — remain fully active.

Immigration attorneys in the tristate area are advising clients to understand the distinction: your local police department is now on your side of the line, but CBP and ICE operate on the other. Carry your documents. Know your rights. And understand that the legal battle over New York's new law is just beginning — the 90-day compliance window, the inevitable Nassau County lawsuit, and whatever DHS does next will reshape this landscape through the fall."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "New York Just Drew the Sharpest Line in America Between Local Police and ICE",
    "subheadline": "Governor Hochul signed sweeping anti-ICE provisions into the state's $268 billion budget. Nassau County is already refusing to comply.",
    "slug": make_slug("new-york-sanctuary-state-ice-ban-hochul-indian-diaspora"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The NYC metro area is home to roughly 800,000 Indian Americans. The new law means local police interactions — traffic stops, court appearances, domestic complaints — can no longer become immigration enforcement events. But federal channels like airports remain active.",
    "tags": ["new-york", "sanctuary-state", "ice", "hochul", "287g", "local-enforcement", "nri", "immigration-reform"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "NY Post", "url": "https://nypost.com/2026/05/28/us-news/blakeman-refuses-to-wind-down-ice-agreement-despite-hochul-sanctuary-law/"},
        {"name": "USA Today (Hochul sanctuary law)", "url": "https://www.usatoday.com"},
        {"name": "Reuters (DHS airport threats)", "url": "https://www.reuters.com"},
        {"name": "NY State Senate Bill S2235-A", "url": "https://www.nysenate.gov/legislation/bills/2025/S2235"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/17168258/pexels-photo-17168258.jpeg",
    "image_caption": "The New York State Capitol in Albany, where Governor Hochul signed the nation's strongest anti-ICE provisions into law.",
    "body": article2_body
}


# ── Publish ────────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
