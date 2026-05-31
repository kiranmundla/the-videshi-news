#!/usr/bin/env python3
"""
Videshi Lifestyle-Health & Markets-Finance Writer
Run: 2026-05-31
Articles:
  1. (lifestyle-health) Pancreatic cancer drug daraxonrasib doubles survival — ASCO 2026
  2. (lifestyle-health) Surgeon General classifies youth screen time as public health crisis — teen sleep
  3. (markets-finance) Dell AI server revenue 757% surge — what it means for NRI tech portfolios
"""

import json, os, re, subprocess, uuid, urllib.parse, sys
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:]
            k, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            os.environ[k.strip()] = v

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──────────────────────────────────────────────────────────────────
def sb_post(table, data):
    import requests
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS_SB, json=data, timeout=30)
    if r.status_code >= 400:
        print(f"  ✗ Supabase POST error {r.status_code}: {r.text[:500]}")
    r.raise_for_status()
    return r.json()

def sb_patch(table, match, data):
    import requests
    q = "&".join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{q}", headers=HEADERS_SB, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import requests
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket article-images."""
    import requests
    try:
        r = requests.get(image_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ⚠ Image download failed: HTTP {r.status_code}")
            return image_url
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image: {content_type}")
            return image_url
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return image_url
        
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        ur = requests.post(upload_url, headers=upload_headers, data=r.content, timeout=30)
        if ur.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {ur.status_code} {ur.text[:200]}")
            # If the source is permanent (wikipedia, pexels), use it directly
            if "upload.wikimedia.org" in image_url or "images.pexels.com" in image_url:
                return image_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if "upload.wikimedia.org" in image_url or "images.pexels.com" in image_url:
            return image_url
        return None

def validate_image_url(url):
    """Check that an image URL returns HTTP 200 with image content type and reasonable size."""
    import requests
    try:
        r = requests.head(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0"}, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD
        r = requests.get(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0"}, stream=True)
        ct = r.headers.get("Content-Type", "")
        chunk = r.raw.read(6000)
        if r.status_code == 200 and "image" in ct and len(chunk) >= 5000:
            return True
    except:
        pass
    return False

def check_skip_list(article_id):
    skip_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/image-skip-list.json")
    if os.path.exists(skip_path):
        with open(skip_path) as f:
            return article_id in json.load(f)
    return False

def publish_article(article):
    """Insert article into Supabase and source image."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Count words in body
    word_count = len(article["body"].split())
    
    row = {
        "id": art_id,
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": article["category"],
        "sources": article["sources"],
        "status": "published",
        "published_at": now,
        "created_at": now,
        "word_count": word_count,
        "tags": article.get("tags", []),
        "urgency": article.get("urgency", "breaking"),
        "vertical": article.get("vertical", "health"),
        "score_total": article.get("score_total", 85),
    }
    
    print(f"\n📝 Publishing: {article['headline'][:70]}...")
    result = sb_post("p2_articles", row)
    print(f"  ✓ Inserted article {art_id}")
    
    # Image sourcing
    if check_skip_list(art_id):
        print("  ⏭ Article in skip list, no image")
        return art_id
    
    img_url = None
    attribution = "The Videshi"
    
    # Try person image from Wikipedia if article has a person focus
    if article.get("person"):
        img_url = fetch_wikipedia_person_image(article["person"])
        if img_url:
            attribution = "Wikimedia Commons"
    
    # Try Pexels fallback
    if not img_url and article.get("image_query"):
        img_url = fetch_pexels_image(article["image_query"], article.get("image_fallback"))
    
    if img_url:
        filename = f"{art_id}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        if final_url:
            sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {
                "image_url": final_url,
                "image_attribution": attribution,
            })
            print(f"  ✓ Image set: {attribution}")
        else:
            print("  ⚠ Image upload failed, article published without image")
    else:
        print("  ⚠ No suitable image found, article published without image")
    
    return art_id

# ── Articles ─────────────────────────────────────────────────────────────────

articles = []

# ─────────────────────────────────────────────────────────────────────────────
# ARTICLE 1: Pancreatic Cancer Drug Daraxonrasib — ASCO 2026
# ─────────────────────────────────────────────────────────────────────────────
articles.append({
    "headline": "A Daily Pill Just Doubled Survival in Advanced Pancreatic Cancer. It Is the First Drug to Ever Do This.",
    "subheadline": "Daraxonrasib cut the risk of death by 60 per cent in a 500-person trial. The results, presented at ASCO 2026 and published in the NEJM, are being called the biggest breakthrough in pancreatic cancer in decades.",
    "slug": "daraxonrasib-pancreatic-cancer-doubles-survival-asco-2026-south-asian-diaspora",
    "category": "lifestyle-health",
    "person": "Brian Wolpin",
    "image_query": "pancreatic cancer research laboratory",
    "image_fallback": "medical oncology treatment",
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "The New England Journal of Medicine", "url": "https://www.nejm.org"},
        {"name": "Revolution Medicines Press Release", "url": "https://www.revmed.com"},
        {"name": "CancerNetwork", "url": "https://www.cancernetwork.com"},
    ],
    "tags": ["pancreatic cancer", "ASCO 2026", "daraxonrasib", "RAS inhibitor", "oncology"],
    "urgency": "breaking",
    "vertical": "health",
    "score_total": 92,
    "body": """Pancreatic cancer has long been the disease that even oncologists fear. The five-year survival rate for metastatic cases sits below 3 per cent. Most patients who fail first-line chemotherapy are told they have three to six months left. Standard second-line treatment buys weeks, not months.

That calculus changed on Sunday at the American Society of Clinical Oncology annual meeting in Chicago. A once-daily oral pill called **daraxonrasib**, developed by Revolution Medicines, doubled median overall survival in patients with previously treated metastatic pancreatic ductal adenocarcinoma — from 6.7 months on standard chemotherapy to 13.2 months. The drug cut the overall risk of death by 60 per cent. These numbers have never been seen before in this cancer, in any line of therapy.

## What the Trial Found

The Phase 3 RASolute 302 trial enrolled 500 patients across 59 sites in six countries. Half received daraxonrasib as a single daily tablet. Half received standard-of-care chemotherapy. The results hit every endpoint the trial set out to measure.

Beyond the survival doubling, the drug halted or reversed tumour progression in nearly a third of patients, compared with just 10 per cent on chemotherapy. Patients on daraxonrasib also reported significantly less cancer-related pain and better overall quality of life. Some resumed activities — walking, cooking, spending time with grandchildren — that they had abandoned after their cancer progressed.

"It ticks all of the boxes," said **Dr. Rachna Shroff** of the University of Arizona Cancer Center. "We really, honestly have never seen in previously treated pancreatic cancer a doubling of survival and a reduced risk of death by 60 per cent. These are not numbers that we typically see."

## Why This Drug Works Where Others Have Failed

The breakthrough lies in what daraxonrasib targets. Roughly 90 per cent of pancreatic cancers are driven by mutations in the RAS family of proteins — specifically KRAS — which acts as an overactive growth switch inside tumour cells. For decades, scientists called RAS "undruggable" because of the way the protein folds, leaving no obvious place for a drug to bind.

Daraxonrasib belongs to a new class called RAS(ON) multi-selective inhibitors. Instead of targeting a single RAS mutation, it blocks multiple active RAS variants simultaneously. Crucially, it works even in patients whose tumours do not carry an identified RAS mutation — both mutant and wild-type groups benefited in the trial.

"These results will change how scientists, clinicians, and patients think about treatment for pancreatic cancer," said **Dr. Brian Wolpin** of Harvard's Dana-Farber Cancer Institute, the trial's principal investigator. The results were simultaneously published in *The New England Journal of Medicine*.

## The Side Effects Are Manageable

The main concern is skin rash, which affected 86 per cent of patients on the drug. But Dr. Wolpin said the rash is largely manageable with antibiotics and topical steroids, and only a small fraction of patients had to discontinue treatment because of adverse events — far fewer than those who dropped out of the chemotherapy arm.

## What This Means for the South Asian Diaspora

Pancreatic cancer disproportionately affects populations with high rates of type 2 diabetes and metabolic syndrome — both of which are significantly elevated in South Asian communities. First-generation immigrants who developed the disease overseas often face fragmented care between two countries; second-generation Indian Americans navigating a parent's diagnosis confront the same despair that has defined this cancer for decades.

The drug is already available through an early access programme in the United States. Revolution Medicines says it is moving urgently toward global regulatory submissions. For families in the diaspora dealing with a pancreatic cancer diagnosis, the question is no longer whether there is anything beyond chemotherapy. There is now a once-daily pill that doubles the time a patient has left — and does so while preserving the quality of that time.

## What Comes Next

Revolution Medicines has four more drugs in its RAS-targeting pipeline. Clinical trials are already underway combining daraxonrasib with other treatments in earlier-stage pancreatic cancer and in other RAS-driven cancers, including lung and colorectal. If those trials succeed, the drug could eventually be used before chemotherapy, not just after it.

For now, the message from ASCO 2026 is unambiguous: the era of RAS-targeted therapy in pancreatic cancer has arrived. And for the first time in the history of this disease, a single pill is doing what decades of chemotherapy regimens could not.
"""
})

# ─────────────────────────────────────────────────────────────────────────────
# ARTICLE 2: Surgeon General Classifies Youth Screen Time as Public Health Crisis
# ─────────────────────────────────────────────────────────────────────────────
articles.append({
    "headline": "The US Surgeon General Just Classified Youth Screen Time as a Public Health Crisis. More Than Half of Teens Are on Their Phones Past Midnight.",
    "subheadline": "A new JAMA Pediatrics study found that 50 per cent of American teenagers spend up to an hour on their phones between 10 PM and 6 AM on school nights. The federal advisory calls for immediate parental action.",
    "slug": "surgeon-general-youth-screen-time-public-health-crisis-jama-teen-sleep-south-asian-parents-20260531",
    "category": "lifestyle-health",
    "person": None,
    "image_query": "teenager smartphone night bedroom",
    "image_fallback": "adolescent phone screen dark",
    "sources": [
        {"name": "JAMA Pediatrics", "url": "https://jamanetwork.com/journals/jamapediatrics"},
        {"name": "US Department of Health and Human Services / Office of the Surgeon General", "url": "https://www.hhs.gov"},
        {"name": "CNN", "url": "https://www.cnn.com"},
        {"name": "American Academy of Pediatrics", "url": "https://www.aap.org"},
    ],
    "tags": ["screen time", "teen health", "sleep", "Surgeon General", "parenting", "JAMA"],
    "urgency": "breaking",
    "vertical": "health",
    "score_total": 88,
    "body": """The numbers have been building for years. But this week, the US government made it official: excessive screen time among American children and teenagers is now classified as an urgent national public health concern.

The advisory, issued by the US Department of Health and Human Services and the Office of the Surgeon General, represents the most sweeping federal intervention yet into how young people interact with digital technology. It targets the entire ecosystem — social media scrolling, text messaging, immersive video gaming, and interactions with artificial intelligence chatbots — and warns that by the time children reach adolescence, they spend more hours staring at screens than they do sleeping or attending school.

## The JAMA Study: What Happens After 10 PM

The advisory coincides with a study published in *JAMA Pediatrics* that quantified what many parents already suspect. More than half of US teenagers are spending up to an hour or more on their phones between 10 PM and 6 AM on school nights. The most-used apps during those hours: YouTube, Instagram, and TikTok.

The damage is twofold. Late-night scrolling pushes back the time teens actually fall asleep. And overnight notifications — even when the phone is not actively in use — fragment sleep by waking adolescents repeatedly throughout the night. The American Academy of Pediatrics recommends 8 to 10 hours of sleep per night for teenagers, a target that becomes effectively impossible when a phone is within arm's reach after dark.

**Dr. Mary Carskadon**, a leading sleep researcher, pointed to the arousal problem: "When you're supposed to be sleeping, your arousal levels need to go down. But those are the kinds of interactions that amp up your arousal and make it harder to sleep."

A separate analysis found that 17 per cent of adolescents reported being woken up by phone calls, text messages, or email at least once per night while sleeping. Another 20 per cent said they use their phone if they wake up overnight, creating a feedback loop that makes each subsequent night's sleep worse.

## The Developmental Damage

The Surgeon General's advisory goes well beyond sleep. Federal researchers found that the average teenager now logs between seven and nine hours of daily digital entertainment. The documented consequences include:

- **Disrupted sleep** — the single most impactful finding, affecting cognitive learning, emotional regulation, and physical growth
- **Decreased school productivity** — attention fragmentation carries into the classroom
- **Rising rates of pediatric obesity** — screen time displaces physical activity
- **Heightened anxiety and depression** — particularly among adolescent girls, according to a separate Swedish study published in *PLOS Global Public Health*
- **Weakened in-person relationships** — time with family and peers is replaced by parasocial digital interactions

## Why This Hits South Asian Families Differently

For NRI parents raising children in the US, the screen time conversation carries a particular weight. First-generation South Asian parents often grew up without smartphones entirely. Many had strict parental boundaries around television and leisure time. They are now navigating a digital environment that is designed — algorithmically, intentionally — to maximise engagement at the expense of everything else.

The challenge is compounded by the academic pressure that defines many desi households. If a child is studying on a laptop, the line between productive screen time and recreational doom-scrolling is invisible. If they need their phone for school communication, confiscating it at night feels like a punishment that contradicts the "do well in school" message.

But the data is clear: **the phone in the bedroom after 10 PM is the single largest controllable risk factor for teen sleep deprivation.** And sleep deprivation, in turn, undermines the academic performance that South Asian families prize above nearly everything else. The irony is that the device parents hope will help their child succeed is, between 10 PM and 6 AM, doing the opposite.

## What the Experts Recommend

The American Academy of Pediatrics suggests building a **family media plan** that sets clear expectations around screen use. Practical steps include:

- **Screen-free bedrooms after a set time** — charging stations in a common area, not by the bedside
- **Notification silencing from 10 PM to 7 AM** — using built-in Focus or Do Not Disturb modes
- **Time limits on entertainment apps** — both iOS and Android offer granular screen time controls
- **Modelling the behaviour** — parents who scroll in bed are teaching their children to do the same
- **Planning non-screen evening activities** — reading, board games, or simply talking

The advisory does not propose federal legislation yet. But the classification as a public health crisis puts screen time in the same category as tobacco and youth vaping — areas where government eventually intervened with regulation.

For parents who have been fighting this battle alone, the message from Washington is simple: you were right to worry, and the data now backs you up.
"""
})

# ─────────────────────────────────────────────────────────────────────────────
# ARTICLE 3: Dell AI Server Surge — NRI Tech Portfolio Implications
# ─────────────────────────────────────────────────────────────────────────────
articles.append({
    "headline": "Dell's AI Server Revenue Just Jumped 757 Per Cent. The Stock Gained 33 Per Cent in a Single Day. Here Is What NRI Tech Investors Should Know.",
    "subheadline": "Dell reported $16.1 billion in AI server sales in a single quarter — more than its entire PC business. The company raised its full-year AI revenue outlook to $60 billion. For NRI investors holding US tech stocks, the AI infrastructure trade just entered a new phase.",
    "slug": "dell-ai-server-revenue-757-percent-surge-nri-tech-investors-portfolio-india-it-20260531",
    "category": "markets-finance",
    "person": "Michael Dell",
    "image_query": "data center server room AI",
    "image_fallback": "server rack technology",
    "sources": [
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "The Wall Street Journal", "url": "https://www.wsj.com"},
        {"name": "LiveMint", "url": "https://www.livemint.com"},
        {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net"},
    ],
    "tags": ["Dell", "AI servers", "tech stocks", "NRI investors", "data centers", "Nvidia"],
    "urgency": "breaking",
    "vertical": "markets",
    "score_total": 90,
    "body": """Dell Technologies just delivered the kind of quarter that forces the market to recategorise a company. On Friday, the stock surged 33 per cent — adding $62 billion in market value in a single session — after the PC maker reported results that confirmed its transformation into one of the biggest beneficiaries of the AI infrastructure build-out.

The numbers were not just good. They were unprecedented.

## The Quarter That Changed Dell's Identity

Fiscal first-quarter revenue came in at **$43.8 billion**, up 88 per cent from a year earlier. Adjusted earnings per share hit $4.86, more than 200 per cent higher than the same period last year and far above the $2.99 Wall Street had expected. But the headline figure was in one specific line: **AI-optimised server sales of $16.1 billion**, up 757 per cent year over year.

That number is significant for a reason beyond its magnitude. For the first time, Dell's AI server revenue surpassed its entire Client Solutions Group — the PC, laptop, and monitor business that the company was built on. Infrastructure Solutions revenue, which houses AI servers alongside traditional servers and storage, climbed 181 per cent to $29 billion. The PC business still grew a healthy 17 per cent to $14.6 billion, but it is no longer what moves the stock.

Dell ended the quarter with an **AI server order backlog of $51.3 billion**. The company raised its full-year AI server revenue forecast from $50 billion to **$60 billion** — a 144 per cent increase over the prior year. "The AI opportunity shows no signs of slowing," Chief Operating Officer Jeff Clarke said.

## What Is Driving the Demand

Dell is not making the AI chips. That remains Nvidia's domain. Dell's role is assembling, configuring, and delivering the physical server infrastructure that companies need to train and deploy AI models. Its customers include hyperscalers (Microsoft Azure, AWS, Google Cloud), AI-native companies (CoreWeave, Nscale), and increasingly, enterprises building private AI infrastructure.

The shift from AI training to AI inference — using trained models rather than building them — is creating a second wave of hardware demand. "That makes it a more broad-based, durable growth over the long term for us," Chief Financial Officer David Kennedy said.

A $9.7 billion Pentagon contract announced the same week, for Microsoft software and services across the Defence Department, added another layer to the story. Melius Research analysts wrote: "We've been following Dell a long time and never seen anything like this. You can make an argument that Dell is even the best way to play AI out there."

## What This Means for NRI Investors

For Indian Americans holding US tech stocks — and many do, given the diaspora's concentration in Silicon Valley and tech employment broadly — Dell's results raise three questions.

**First, is the AI infrastructure trade still investable?** Dell's stock has risen roughly 150 per cent since February. At these levels, you are paying for continued 757 per cent growth in AI servers, which is unlikely to sustain. But the backlog of $51.3 billion suggests that revenue growth, while decelerating, has a long runway. Analysts at Evercore, Mizuho, and Bank of America all raised price targets after the report.

**Second, what about the rest of the AI supply chain?** Dell's results lifted Super Micro Computer and Hewlett Packard Enterprise by roughly 14 per cent each. Nvidia, which supplies the GPUs inside Dell's servers, is already the world's most valuable company. Memory chipmakers — Samsung, SK Hynix, Micron — are in a supply-constrained environment with pricing power. For NRI investors who hold semiconductor ETFs (SOXX, SMH) or individual chipmakers, Dell's demand signal is confirmation that the infrastructure cycle has legs.

**Third, what does this mean for Indian IT services?** This is the less obvious connection but arguably the most relevant for the diaspora. TCS, Infosys, HCLTech, and Wipro are the services layer of global enterprise IT. When companies build AI infrastructure, they need systems integrators to design, implement, manage, and maintain it. Dell's AI order backlog does not directly flow to Indian IT companies, but the customers placing those orders — Fortune 500 enterprises and cloud providers — are also the largest clients of Indian IT services firms.

HCLTech has been the most aggressive in positioning itself as an AI infrastructure services partner. Infosys has built AI consulting practices. TCS is investing in AI-specific delivery centres. The tailwind is real but lagged — Indian IT companies will see the revenue from this infrastructure cycle 12 to 18 months after the hardware ships.

## The Broader Picture

Dell's quarter also contained a cautionary note. The company acknowledged that memory chip supply is constrained and that customers are locking in supply for extended periods. That supply tightness, if it worsens, could slow server deliveries and push some revenue into later quarters.

The political angle is also impossible to ignore. The Wall Street Journal reported that President Trump's personal accounts purchased Dell stock in a transaction worth between $1 million and $5 million in February. A week later, Trump publicly praised Dell's CEO and told a crowd to "go out and buy a Dell computer." Since that purchase, the stock has risen roughly 150 per cent. Dell declined to comment on the purchases.

For NRI investors, the takeaway is pragmatic: the AI infrastructure build-out is not a bubble. The demand is real, the revenue is real, and the backlog is real. But the easy money has been made. At current valuations, you are buying into a company that must sustain extraordinary growth to justify its price — and extraordinary growth, by definition, does not last forever.

The smart play may not be Dell itself but the less obvious beneficiaries: the memory chipmakers who supply it, the Indian IT companies who service its customers, and the cloud providers who operate the servers Dell builds. The infrastructure cycle is here. The question for investors is where in the stack they want to own it.
"""
})

# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("VIDESHI LIFESTYLE-HEALTH & MARKETS-FINANCE WRITER")
    print(f"Run: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    published_ids = []
    for art in articles:
        try:
            art_id = publish_article(art)
            published_ids.append(art_id)
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 60}")
    print(f"✓ Published {len(published_ids)} / {len(articles)} articles")
    for pid in published_ids:
        print(f"  - {pid}")
    print("=" * 60)
