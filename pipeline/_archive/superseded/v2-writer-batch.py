#!/usr/bin/env python3
"""
V2 Writer Batch — writes articles from v2-candidates.json using GPT-4o-mini.
Handles dedup filtering, topic creation, article generation, image sourcing, DB insertion.
"""

import json, os, re, subprocess, sys, time, hashlib, urllib.parse
from datetime import datetime, timezone, timedelta

# ── Env ──────────────────────────────────────────────────────────────────────
def load_env(path):
    path = os.path.expanduser(path)
    if not os.path.exists(path): return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env("~/workspace/.env.supabase")
load_env("~/workspace/.env.openai")
load_env("~/workspace/.env.pexels")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

# ── HTTP helper ──────────────────────────────────────────────────────────────
def curl_json(method, url, data=None, headers=None, timeout=60):
    cmd = ["curl", "-sS", "-X", method, url]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    if data:
        cmd += ["-d", json.dumps(data)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return json.loads(r.stdout) if r.stdout.strip() else None
    except Exception as e:
        print(f"  ⚠ curl error: {e}", file=sys.stderr)
        return None

def sb_rest(method, table, params="", data=None):
    url = f"{SUPABASE_URL}/rest/v1/{table}{params}"
    hdrs = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    return curl_json(method, url, data=data, headers=hdrs)

def call_openai(prompt, max_tokens=4000, temperature=0.4, retries=3):
    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"}
    }
    for attempt in range(retries):
        result = curl_json("POST", "https://api.openai.com/v1/chat/completions",
            data=body, headers={
                "Authorization": f"Bearer {OPENAI_KEY}",
                "Content-Type": "application/json"
            }, timeout=120)
        if not result:
            print(f"  ⚠ OpenAI attempt {attempt+1}: no response")
            time.sleep(5 * (attempt + 1))
            continue
        if "error" in result:
            err = result["error"]
            print(f"  ⚠ OpenAI attempt {attempt+1}: {err.get('type','?')} - {err.get('message','?')[:100]}")
            if "rate_limit" in str(err).lower() or err.get("type") == "rate_limit_error":
                time.sleep(15 * (attempt + 1))
                continue
            return None
        try:
            text = result["choices"][0]["message"]["content"]
            return json.loads(text)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"  ⚠ OpenAI parse error: {e}")
            return None
    print(f"  ⚠ OpenAI: all {retries} attempts failed")
    return None

# ── Dedup check ──────────────────────────────────────────────────────────────
SKIP_TITLES = [
    "us launches seventh",
    "netflix wants to be youtube",
    "ebola spreading more quickly",
    "india attracts $10 billion in nri deposits",
    "tech titans are slashing jobs",
    "e-oci card launched: how oci cardholder",  # merge into main OCI article
    "5 ways turmeric can benefit",  # merge into main turmeric article
    "manju warrier on ageing",  # low score, paywalled
    "from maida bread to biscuits",  # wrong category, paywalled
    "bal partner lynden melmed",  # likely old content
    "monsoon myths that could land",  # less relevant to diaspora
    # Already published in this run:
    "tcs bags multi-million",
    "tcs secures multi-million",
    "south africa: significant",
    "south africa's immigration",
    "anushka sharma visits",
    "anushka sharma dines",
    "apple sued over reported",
    "apple faces class action",
    "vimaglabs secures patent",
    "indian startup vimaglabs",
]

def should_skip(title):
    t = title.lower()
    for skip in SKIP_TITLES:
        if skip in t:
            return True
    return False

# ── Slug helper ──────────────────────────────────────────────────────────────
def make_slug(headline):
    slug = re.sub(r'[^a-z0-9\s-]', '', headline.lower())
    slug = re.sub(r'\s+', '-', slug.strip())[:80]
    date_suffix = datetime.now(timezone.utc).strftime("-%Y%m%d")
    return slug.rstrip('-') + date_suffix

# ── Hero image sourcing ─────────────────────────────────────────────────────
def find_person_image(entities):
    for name in entities[:3]:
        name_lower = name.lower().strip()
        if len(name_lower) < 3: continue
        result = sb_rest("GET", "person_images",
            f"?person_name_lower=eq.{urllib.parse.quote(name_lower)}&order=use_count.asc,last_used_at.asc.nullsfirst&limit=1")
        if result and isinstance(result, list) and len(result) > 0:
            img = result[0]
            # Update use count
            sb_rest("PATCH", "person_images",
                f"?id=eq.{img['id']}",
                data={"use_count": img.get("use_count", 0) + 1,
                      "last_used_at": datetime.now(timezone.utc).isoformat()})
            print(f"  🖼 Person image found for: {name}")
            return img["image_url"]
    return None

def find_pexels_image(query):
    if not PEXELS_KEY: return None
    url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape"
    result = curl_json("GET", url, headers={"Authorization": PEXELS_KEY})
    if result and isinstance(result, dict) and result.get("photos"):
        return result["photos"][0]["src"]["large2x"]
    return None

def source_image(article_data):
    entities = article_data.get("image_entities", [])
    # Try person images first
    url = find_person_image(entities) if entities else None
    if url: return url
    # Fallback to Pexels
    query = article_data.get("image_search_query", "")
    if query:
        url = find_pexels_image(query)
        if url: return url
    return None

# ── Data card rendering ──────────────────────────────────────────────────────
def _esc(s):
    return (str(s) if s is not None else "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def render_card_html(card):
    ctype = card.get("card_type", "stat_grid")
    title = _esc(card.get("card_title", ""))
    hs = card.get("hero_stat")
    items = card.get("items", [])
    source = _esc(card.get("source_note", ""))
    html = '<div class="vdc"><div class="vdc-glow"></div>'
    if title:
        html += f'<div class="vdc-title">{title}</div>'
    if hs:
        val = _esc(hs.get("value", ""))
        label = _esc(hs.get("label", ""))
        trend = _esc(hs.get("trend", ""))
        trend_cls = "vdc-hero-trend-neg" if (trend.startswith("↓") or trend.startswith("-")) else "vdc-hero-trend"
        html += '<div class="vdc-hero">'
        html += f'<div class="vdc-hero-num">{val}</div>'
        if trend: html += f'<div class="{trend_cls}">{trend}</div>'
        if label: html += f'<div class="vdc-hero-label">{label}</div>'
        html += '</div>'
    if items:
        if ctype == "stat_grid":
            html += '<div class="vdc-grid">'
            for it in items:
                html += f'<div class="vdc-cell"><div class="vdc-cell-num">{_esc(it.get("value",""))}</div><div class="vdc-cell-label">{_esc(it.get("label",""))}</div></div>'
            html += '</div>'
        elif ctype == "comparison":
            html += '<div class="vdc-bars">'
            vals = [abs(it.get("numeric_value", 0)) for it in items]
            mx = max(vals) if vals else 1
            for it in items:
                w = max(5, int(abs(it.get("numeric_value", 0)) / mx * 100)) if mx else 50
                html += f'<div class="vdc-bar-row"><span class="vdc-bar-name">{_esc(it.get("name",""))}</span><div class="vdc-bar-track"><div class="vdc-bar-fill" style="width:{w}%"></div></div><span class="vdc-bar-val">{_esc(it.get("value",""))}</span></div>'
            html += '</div>'
        elif ctype == "timeline":
            html += '<div class="vdc-timeline">'
            for it in items:
                html += f'<div class="vdc-tl-item"><span class="vdc-tl-date">{_esc(it.get("date",""))}</span><span class="vdc-tl-event">{_esc(it.get("event",""))}</span></div>'
            html += '</div>'
        elif ctype == "highlights":
            html += '<div class="vdc-highlights">'
            for it in items:
                html += f'<div class="vdc-hl-item">'
                if it.get("stat"): html += f'<span class="vdc-hl-stat">{_esc(it["stat"])}</span>'
                html += f'<span class="vdc-hl-text">{_esc(it.get("text",""))}</span></div>'
            html += '</div>'
    if source:
        html += f'<div class="vdc-source">{source}</div>'
    html += '</div>'
    return html

CARD_MARKER = '<!-- data-card -->'

def inject_data_cards(body, data_cards, key_takeaways):
    injected = ""
    if key_takeaways:
        injected += '<div class="vdc vdc-takeaways"><div class="vdc-glow"></div><div class="vdc-title">Key Takeaways</div><ul class="vdc-kt-list">'
        for t in key_takeaways:
            injected += f'<li>{_esc(t)}</li>'
        injected += '</ul></div>'
    for card in data_cards:
        injected += render_card_html(card)
    if not injected:
        return body
    marker_pos = body.find(CARD_MARKER)
    if marker_pos >= 0:
        return body[:marker_pos] + injected + body[marker_pos + len(CARD_MARKER):]
    # Insert after first </p>
    first_p = body.find('</p>')
    if first_p >= 0:
        return body[:first_p + 4] + injected + body[first_p + 4:]
    return injected + body

# ── Article generation prompt ────────────────────────────────────────────────
def build_prompt(candidate, source_text=""):
    title = candidate["title"]
    category = candidate["category"]
    coverage = candidate.get("coverage", "new")
    source_urls = candidate.get("source_urls", [])

    source_context = source_text if source_text else "\n".join([f"- {u}" for u in source_urls[:5]])
    today_str = datetime.now(timezone.utc).strftime('%B %d, %Y')
    
    coverage_note = ""
    if coverage == "update":
        coverage_note = """
IMPORTANT: This is an UPDATE to a story we previously covered. Frame the article as new developments.
Lead with WHAT'S NEW, not a recap. Reference that this is an ongoing/developing story."""

    return f"""You are a senior journalist at The Videshi, a premium English-language news site for the Indian diaspora.

TODAY'S DATE: {today_str}. Do NOT invent dates, quotes, or statistics.
{coverage_note}

Write a complete article about: {title}
CATEGORY: {category}

SOURCE MATERIAL (write from these facts only — original prose, never copy sentences):
{source_context}

REQUIREMENTS:
1. headline: 20-120 chars, newspaper style, declarative
2. subheadline: 30-120 chars, adds context
3. body: 400-700 words clean HTML. Use <h2> for sections, <p> for paragraphs. Present tense for current events. At least one section header.
4. tags: Array of 3-6 lowercase tags
5. slug: lowercase-hyphenated URL slug (max 80 chars)
6. vertical: "geopolitics", "economy", "immigration", "tech", "entertainment", "culture", "diaspora", etc.
7. diaspora_angle: One sentence why NRIs should care
8. sources: Array of {{"name":"...", "url":"..."}} — at least 2
9. newsworthiness: Integer 1-30
10. diaspora_impact: Integer 1-30
11. prominence: Integer 1-20
12. article_type: "breaking", "analysis", "report", or "feature"
13. image_search_query: Specific query for hero image
14. image_must_show: What hero image must depict
15. image_entities: Array of main people/entities
16. key_takeaways: Array of 3-5 bullet point strings (under 20 words each)
17. data_cards: Array of 0-2 data cards with card_title, card_type (stat_grid/comparison/timeline/highlights), items, optional hero_stat. Empty array if no stats.

STYLE: Write like The Economist or Bloomberg. Lead with news, then context, then analysis. Include 3+ concrete data points. No filler. No "In a significant development...". End with impact or what to watch.
{"For markets-finance: straight financial journalism, no forced NRI framing for US/global stories." if category == "markets-finance" else "Weave in diaspora context naturally where it adds value."}

Return a single JSON object with ALL these fields."""

# ── Source material for each candidate ───────────────────────────────────────
SOURCE_MATERIAL = {
    "tcs": """Reuters: TCS secured multi-million, multi-year contract from ABB (Swiss-Swedish industrial tech firm).
TCS will design and run ABB's global network ecosystem as AI-driven service + cybersecurity.
Extension of 20-year partnership. Previously consolidated multiple accounting software into single SAP platform.
TCS transitions from managing software/hardware to end-to-end global network operations via unified network-as-a-service framework.
ABB's Future Network Model programme — standardize, centrally manage digital infrastructure.
Replaces fragmented network environments with secure, scalable, service-driven architecture.
SIAM, global network operations center, advanced security, upgraded LAN/WAN/SD-WAN.
ABB has ~110,000 employees. TCS shares jumped 5.5% on announcement.
Outlook Business: Published July 13, 2026. Multi-year, several million dollars.""",

    "apple_hide_email": """MacRumors (July 2026): Apple sued over "Hide My Email" flaw — proposed class action.
Alleges Apple violated California's false advertising law + consumer protection statutes.
Feature allegedly does not work as advertised — could expose user's real email address.
Security researcher disclosed vulnerability to Apple in June 2025.
No known instances of exploitation — steps not shared publicly as precaution.
Separate from Apple vs OpenAI trade secret lawsuit (40+ former employees, legal preservation letters).
Also separate from DOJ antitrust settlement talks.""",

    "vimaglabs": """Autocar Professional (July 8, 2026): Vimag Labs secured 5th patent in India for Virtual Magnet Synchronous Motor (VMSM).
Patent: "A Robust Rotating Transformer Excited Synchronous Motor and Its Control"
Software-defined motor — no rare-earth permanent magnets. Generates magnetic field electronically in real time.
Brushless, slip-ring-free design using power electronics + proprietary control algorithms.
87,600 engineering hours. 5 granted patents, 10 pending, 15 trademarks.
Founded Sept 2025 by Manish Seth and Dr Piyush Desai, Bengaluru.
$5M Series A led by Accel (Jan 2026), with Chakra Growth Fund and Thinkuvate.
Operates under Volektra brand. Teams in Germany, US, Poland.
Pilot programmes with 2-wheeler and passenger vehicle OEMs.
Plans for light commercial vehicles, robotics, defence, HVAC, cooling in 200-600kW range.
Technology at TRL-7 (real-world vehicle testing).
Plug-and-play for automakers, no major manufacturing line changes needed.
Rare-earth magnets dominated by China (~70% of mining, ~90% of processing). 
Global EV motor market projected >$25 billion by 2030.""",

    "oci": """Embassy of India Berne: e-OCI card launched June 30, 2026 for new applicants and existing physical booklet holders.
Enhanced security features, integrated with all Immigration Check Posts (ICPs).
No need to carry physical OCI card for immigration clearance.
Download via ociservices.gov.in portal or "Indian Visa Su Swagatam" mobile app.
Physical booklets remain valid. Only digital e-OCI issued going forward.
Amit Shah (Home Minister) launched new OCI portal + FCRA 2.0 portal.
5 million+ OCI cardholders worldwide affected.
OCI booklets no longer need reissuing when passport renewed after age 20 — just update passport details online.
e-OCI features: unique registration number, real-time verification, eliminates lost/damaged document risk.
Entire process online — submit, upload docs, download after approval.
Revamped portal: improved UI, enhanced security, user-friendly.
India West: New fees: Fresh e-OCI USD 275 (outside India), INR 15,000 (within).
Online passport update within 3 months: free. Late update penalty: USD 25.
PM Modi praised it as "major step forward in citizen friendly digital governance."
QR-coded credential in mobile wallet. E-gates at 6 major airports scan QR + biometrics in <15 seconds.
VisaHQ: 4.5-4.7 million overseas citizens affected.""",

    "daca": """Rep. Sara Jacobs (.gov), July 1, 2026: Led 54 colleagues demanding answers from USCIS on extreme delays in DACA renewal processing.
Letter to USCIS Director Joseph Edlow.
Delays jeopardizing livelihoods, financial stability, well-being of recipients.
"DACA recipients have done everything right, and yet the Trump Administration continues to punish them."
"Republicans will claim that immigrants have to play by the rules, but even when they follow every single rule..."
Recipients losing jobs, unable to provide for families, at risk of detention/deportation.
Separate: Rep. Andrea Salinas led 15 colleagues in similar April letter.
Senate: Cortez Masto, Durbin led Democrats demanding DHS reduce delays.
As of March 2026: 270 DACA recipients detained, 174 deported.
DACA recipients contribute billions annually to national economy.
Federal judge struck down $100,000 H-1B fee in June (Massachusetts court).
Third federal judge (Bates) issued strongest order yet backing DACA — "arbitrary," "capricious," "unlawful."
120-day guidance window for renewals often missed due to processing delays.""",

    "h1b_healthcare": """AHA (American Hospital Association): Bipartisan letter Feb 11 to DHS, supported by AHA.
Led by Reps. Yvette D. Clarke (D-NY) and Michael Lawler (R-NY), signed by 100 lawmakers.
Urge exemption from $100,000 filing fee for H-1B visas for health care workers.
"Imposing a $100,000 fee will exacerbate hospitals' existing staffing challenges."
"Chronically underfunded hospitals pushed to financial brink."
Rural and high-poverty urban areas left without adequate access to care.
87 million Americans live in areas designated as lacking enough medical professionals (HRSA).
Physician demand could exceed supply by up to 86,000 in next decade.
Clinical lab science programs educating less than half professionals needed.
Bipartisan bill: Physicians and Healthcare Workforce Act (March 17, 2026) — Reps. Lawler, Bishop, Salazar, Clarke.
Would exempt foreign-trained health care workers from $100K fee + prohibit new fees greater than existing.
Endorsed by 40 organizations including AAMC.
Federal judge (Massachusetts) struck down $100K fee in June 2026.""",

    "anushka": """NDTV Food: Anushka Sharma spotted at OMNOM, vegan/vegetarian restaurant in London's Islington Square.
Visited with Grammy-nominated spiritual singer Krishna Das.
OMNOM team described Anushka as "warm, humble and graceful."
Expressed hope Virat Kohli would visit.
OMNOM: plant-based, Ayurveda-inspired, sattvic menu, no onion/garlic.
Kitchen in collaboration with Namaste Village.
Menu: parathas, dosa waffles, pav bhaji, undhiyu, mirchi pakoda, samosas, jackfruit biryani, thalis.
Desserts: gulab jamun, boondi laddoo.
Also houses wellness space: yoga, meditation, sound healing, music performances.
Inspired by Bhakti Yoga, Ayurveda, ancient Indian philosophies.""",

    "priyanka": """Devdiscourse: Priyanka Chopra earned nomination for Best Actress in an Action Movie at 2026 Critics Choice Super Awards.
Role in "The Bluff."
Also recently got Emmy nomination for "Heads of State."
Competing against: Pamela Anderson (The Naked Gun), Charlize Theron (Apex), Eiza González, Akari Takaishi, Samara Weaving, Maddie Ziegler.
Winners announced August 6, 2026.
"Superman" leads film nominations with 6. "The Boys" leads TV with 5.
Wikipedia: 6th Critics Choice Super Awards — honors popular genre films (action, superhero, horror, sci-fi/fantasy).
Previous nomination: Best Actress in Action Series for Citadel (2024).
Priyanka has won 5 Filmfare Awards, Padma Shri (2016).""",

    "govinda": """Bollywood Hungama (July 14, 2026): Govinda announces comeback with Roopa, self-produced film.
Press conference: unveiled first poster, introduced newcomer Rani Swarankar as leading lady.
Also producing — first foray into film production.
"People kept saying, 'Now he won't appear in films anymore.' But I always started again."
Film aimed at youngsters, hopes to inspire dreams.
Believes in numerology — number 14 is lucky. Signed 14 films in one week at age 14. 14 years of superstardom.
Member of Parliament in 14th Lok Sabha. 14-year struggle before return.
Also announced second film: Duniyadari.
Last seen in 2019's Rangeela Raja — 7-year hiatus from theatrical releases.
Was one of biggest superstars of 1990s — known as "Hero No. 1."
Recent appearance on Lock Upp Season 2 (supporting wife Sunita Ahuja).
Pinkvilla: seven-year hiatus, career resurgence narrative.""",

    "world_cup_travel": """Travel and Tour World (July 2026): World Cup tourism impact more modest than expected.
US welcomed 4.39 million foreign air arrivals during June — stable 0.2% increase YoY.
Distribution shifted: more from Mexico/Canada, less from traditional long-haul.
Tournament created concentrated demand around match venues, not nationwide lift.
Quarterfinal tickets averaged upwards of $6,000 on secondary resale markets.
Semi-finals (France vs Spain in Dallas, England vs Argentina in Atlanta) drove late booking surge.
International flight demand, premium hotel rates, tourism spending climbed during knockout rounds.
California outweighed other host states, but most states saw weaker-than-expected tourism gains.
European tourists from Denmark, Netherlands, Germany, France turning away due to higher inflation, strict visa, high ticket prices.
US air travel demand slipped in June 2026 — 24.6 million international air traffic passenger enplanements.
Decline came during critical summer travel period.""",

    "turmeric": """Real Simple (2026): 8 Health Benefits of Turmeric Tea — doctors recommend drinking it.
Turmeric contains curcumin — anti-inflammatory, antioxidant properties.
Benefits: easing pain, reducing inflammation, supporting brain health, liver function.
GQ: 5 Ways Turmeric Can Benefit Health — easing pain to reducing inflammation.
Curcumin is main bioactive compound. Only ~3% of turmeric by weight.
Absorption improved with black pepper (piperine increases bioavailability by 2000%).
Used in traditional Ayurvedic medicine for thousands of years.
Global turmeric market valued at $5.6 billion, projected to reach $9.3 billion by 2030.
India produces ~80% of world's turmeric supply.
"Golden milk" (haldi doodh) — traditional Indian remedy gaining global popularity.""",

    "south_africa": """BAL Immigration Law: South Africa — significant immigration changes on the horizon.
South Africa undergoing major immigration reform.
Indian community in SA is substantial (~1.5 million, mainly in Durban/KwaZulu-Natal).
Largest Indian diaspora community in Africa.
Changes likely to affect work permits, business visas, permanent residence pathways.""",

    "immigration_court": """Talking Points Memo: "A Complete Devastation of Due Process" — what really happens inside immigration court.
Immigration courts face massive backlogs — over 3 million pending cases.
Average case takes years. Judges handle 1,000+ cases.
No right to government-appointed attorney (unlike criminal court).
Respondents often unrepresented — outcomes dramatically worse.
Due process concerns raised by judges and legal scholars.
System described as "failing" by former judges.""",
}

# ── Main pipeline ────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print(f"V2 Writer Batch — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    with open("/tmp/v2-candidates.json") as f:
        data = json.load(f)
    candidates = data["candidates"]
    print(f"\nLoaded {len(candidates)} candidates")

    # Filter candidates
    filtered = []
    merged_oci = False
    merged_turmeric = False
    for c in candidates:
        title = c["title"]
        if should_skip(title):
            print(f"  ⏭ SKIP: {title[:70]}")
            continue
        # Merge OCI candidates
        if "e-oci" in title.lower() or "oci process" in title.lower() or "oci card" in title.lower():
            if merged_oci:
                print(f"  ⏭ MERGE (already have OCI): {title[:70]}")
                continue
            merged_oci = True
            c["title"] = "India Launches Digital e-OCI Card, Eliminating Need for Physical Booklet"
            c["_source_key"] = "oci"
        # Merge turmeric
        elif "turmeric" in title.lower():
            if merged_turmeric:
                print(f"  ⏭ MERGE (already have turmeric): {title[:70]}")
                continue
            merged_turmeric = True
            c["title"] = "Why Doctors Are Now Recommending Turmeric Tea — The Science Behind India's Golden Spice"
            c["_source_key"] = "turmeric"
        else:
            # Map to source material key
            tl = title.lower()
            if "tcs" in tl and "abb" in tl: c["_source_key"] = "tcs"
            elif "hide my email" in tl: c["_source_key"] = "apple_hide_email"
            elif "vimaglabs" in tl or "vimag" in tl: c["_source_key"] = "vimaglabs"
            elif "daca" in tl: c["_source_key"] = "daca"
            elif "health care" in tl and "h-1b" in tl: c["_source_key"] = "h1b_healthcare"
            elif "anushka" in tl and "omnom" in tl: c["_source_key"] = "anushka"
            elif "priyanka chopra" in tl and "critics" in tl: c["_source_key"] = "priyanka"
            elif "govinda" in tl and "roopa" in tl: c["_source_key"] = "govinda"
            elif "world cup" in tl and "travel" in tl: c["_source_key"] = "world_cup_travel"
            elif "south africa" in tl and "immigration" in tl: c["_source_key"] = "south_africa"
            elif "devastation of due process" in tl or "immigration court" in tl: c["_source_key"] = "immigration_court"
            elif "kerala fish curry" in tl: c["_source_key"] = "kerala_fish"
            elif "kunal kapur" in tl: c["_source_key"] = "kunal_kapur"
            elif "pm modi" in tl and "punjab" in tl: c["_source_key"] = "pm_modi_punjab"
            else: c["_source_key"] = None
        filtered.append(c)

    # Remove candidates with paywalled sources and no source material
    final = []
    for c in filtered:
        key = c.get("_source_key")
        if key and key in SOURCE_MATERIAL:
            final.append(c)
        elif key in ("kerala_fish", "kunal_kapur"):
            print(f"  ⏭ SKIP (paywalled): {c['title'][:70]}")
        elif key == "pm_modi_punjab":
            print(f"  ⏭ SKIP (no source material): {c['title'][:70]}")
        elif key is None:
            # Try to include with just source URLs
            if c.get("source_urls"):
                c["_source_key"] = "generic"
                final.append(c)
            else:
                print(f"  ⏭ SKIP (no sources): {c['title'][:70]}")
        else:
            final.append(c)

    print(f"\n{len(final)} articles to write\n")
    
    written = []
    failed = []

    for i, candidate in enumerate(final):
        print(f"\n{'─' * 50}")
        print(f"[{i+1}/{len(final)}] {candidate['title'][:70]}")
        print(f"  Category: {candidate['category']} | Score: {candidate.get('llm_score', '?')} | Coverage: {candidate.get('coverage', 'new')}")

        # Get source material
        source_key = candidate.get("_source_key", "")
        source_text = SOURCE_MATERIAL.get(source_key, "")
        if not source_text:
            source_text = "\n".join([f"- {u}" for u in candidate.get("source_urls", [])[:5]])

        # Generate article via GPT-4o-mini
        prompt = build_prompt(candidate, source_text)
        print("  📝 Generating article...")
        article_data = call_openai(prompt)
        if not article_data:
            print("  ✗ Article generation failed")
            failed.append(candidate["title"])
            continue

        headline = article_data.get("headline", "")
        body = article_data.get("body", "")
        if not headline or len(headline) < 15 or not body or len(body) < 300:
            print(f"  ✗ Bad article: headline={len(headline)}chars, body={len(body)}chars")
            failed.append(candidate["title"])
            continue

        # Clean up body
        body = re.sub(r'^### (.+)$', r'<h3>\1</h3>', body, flags=re.MULTILINE)
        body = re.sub(r'^## (.+)$', r'<h2>\1</h2>', body, flags=re.MULTILINE)
        body = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', body)

        # Slug
        slug = article_data.get("slug", "") or make_slug(headline)
        slug = re.sub(r'[^a-z0-9-]', '', slug.lower())[:90]
        date_suffix = datetime.now(timezone.utc).strftime("-%Y%m%d")
        if not re.search(r'-\d{8}$', slug):
            slug = slug.rstrip('-')[:80] + date_suffix

        # Data cards + key takeaways
        key_takeaways = article_data.get("key_takeaways", [])
        data_cards = article_data.get("data_cards", [])
        if isinstance(key_takeaways, list) and key_takeaways:
            key_takeaways = [str(t) for t in key_takeaways if t][:5]
        else:
            key_takeaways = []
        valid_card_types = {"stat_grid", "comparison", "timeline", "highlights"}
        validated_cards = []
        if isinstance(data_cards, list):
            for card in data_cards[:2]:
                if (isinstance(card, dict)
                    and card.get("card_title")
                    and card.get("card_type") in valid_card_types
                    and isinstance(card.get("items"), list)
                    and len(card["items"]) >= 1):
                    validated_cards.append(card)
        data_cards = validated_cards

        if key_takeaways or data_cards:
            body = inject_data_cards(body, data_cards, key_takeaways)

        # Create topic
        topic_data = {
            "canonical_title": candidate["title"][:200],
            "category": candidate["category"],
            "status": "used",
            "score_total": candidate.get("llm_score", 3) * 5,
            "signal_count": candidate.get("signal_count", 1),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        topic_result = sb_rest("POST", "p2_topics", data=topic_data)
        topic_id = None
        if topic_result and isinstance(topic_result, list) and len(topic_result) > 0:
            topic_id = topic_result[0].get("id")
        elif topic_result and isinstance(topic_result, dict):
            topic_id = topic_result.get("id")
        
        if not topic_id:
            print(f"  ⚠ Topic creation failed, using null topic_id")

        # Source hero image
        print("  🖼 Sourcing hero image...")
        hero_url = source_image(article_data)
        if hero_url:
            print(f"  ✓ Hero image found")
        else:
            print(f"  ⚠ No hero image found")

        # Build article record
        category = candidate["category"]
        if category == "lifestyle": category = "lifestyle-health"
        
        word_count = len(re.findall(r'\b\w+\b', body))
        article = {
            "headline": headline[:200],
            "subheadline": (article_data.get("subheadline") or "")[:200],
            "body": body,
            "category": category,
            "vertical": article_data.get("vertical", "general"),
            "tags": article_data.get("tags", []),
            "slug": slug,
            "sources": json.dumps(article_data.get("sources", [{"name": "The Videshi", "url": "https://thevideshi.com"}])),
            "diaspora_angle": article_data.get("diaspora_angle", ""),
            "article_type": article_data.get("article_type", "report"),
            "newsworthiness": min(30, max(1, article_data.get("newsworthiness", 15))),
            "diaspora_impact": min(30, max(1, article_data.get("diaspora_impact", 10))),
            "prominence": min(20, max(1, article_data.get("prominence", 10))),
            "status": "published",
            "is_featured": False,
            "is_editorial": False,
            "topic_id": topic_id,
            "published_at": datetime.now(timezone.utc).isoformat(),
            "word_count": word_count,
            "key_takeaways": key_takeaways,
            "data_cards": data_cards,
            "enriched_at": datetime.now(timezone.utc).isoformat(),
            "cards_rendered_at": datetime.now(timezone.utc).isoformat(),
            "llm_score": candidate.get("llm_score", 3),
            "signal_count": candidate.get("signal_count", 1),
        }
        if hero_url:
            article["hero_image"] = hero_url
        
        article["score_total"] = (
            article["newsworthiness"] + article["diaspora_impact"] + article["prominence"]
        )

        # Insert
        result = sb_rest("POST", "p2_articles", data=article)
        if result and isinstance(result, list) and len(result) > 0:
            art_id = result[0].get("id", "?")[:8]
            print(f"  ✓ Published: {headline[:60]} (id: {art_id}...)")
            written.append({"headline": headline, "category": category})
        elif result and isinstance(result, dict) and not result.get("error"):
            print(f"  ✓ Published: {headline[:60]}")
            written.append({"headline": headline, "category": category})
        else:
            err = json.dumps(result)[:200] if result else "no response"
            print(f"  ✗ Insert failed: {err}")
            failed.append(headline)

        # Small delay to avoid rate limits
        time.sleep(3)

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"SUMMARY: {len(written)} published, {len(failed)} failed")
    print("=" * 60)
    for a in written:
        print(f"  ✓ [{a['category']}] {a['headline'][:70]}")
    if failed:
        print(f"\nFailed ({len(failed)}):")
        for f in failed:
            print(f"  ✗ {f[:70]}")

if __name__ == "__main__":
    main()
