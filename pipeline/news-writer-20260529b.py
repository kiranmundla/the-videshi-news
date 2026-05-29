#!/usr/bin/env python3
"""News writer for The Videshi — 2026-05-29 afternoon batch."""

import json, os, re, sys, time, uuid, urllib.parse
import requests
from datetime import datetime, timezone

# ── Load env file ─────────────────────────────────────────────────────
def load_env(path):
    try:
        with open(os.path.expanduser(path)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass

load_env("~/.env.supabase")
load_env("~/.env.pexels")

# ── Supabase credentials ──────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

PEXELS_KEY = os.environ.get("PEXELS_API_KEY")


# ── Image helpers ─────────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Search Pexels for an image. Uses curl because Python urllib gets 403."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                [
                    "curl", "-sS",
                    f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                    "-H", f"Authorization: {PEXELS_KEY}",
                ],
                capture_output=True, text=True, timeout=15,
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


def validate_image(url):
    """Verify image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD didn't give Content-Length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def sb_insert(table, data):
    """Insert a row into Supabase and return the response."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data,
    )
    if r.status_code not in (200, 201):
        print(f"  ✗ Insert error ({r.status_code}): {r.text[:300]}")
        return None
    return r.json()


def sb_patch(table, match, data):
    """Patch a row in Supabase."""
    params = "&".join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=data,
    )
    if r.status_code not in (200, 204):
        print(f"  ✗ Patch error ({r.status_code}): {r.text[:300]}")


# ── Article definitions ───────────────────────────────────────────────

articles = []

# ─── ARTICLE 1: Trump Iran Ceasefire Deal — India Oil Impact ──────────
articles.append({
    "headline": "Trump Is in the Situation Room Deciding on Iran. India, Which Imports 90 Percent of Its Oil, Is Watching.",
    "subheadline": "A 60-day ceasefire extension could reopen the Strait of Hormuz and ease India's $102-a-barrel crude crisis. But analysts warn the relief may be temporary.",
    "slug": "trump-iran-ceasefire-hormuz-india-oil-imports-crude-crisis-20260529",
    "category": "news",
    "vertical": "news",
    "image_search_person": "Donald Trump",
    "image_fallback_query": "oil tanker strait of hormuz shipping",
    "image_fallback_query2": "crude oil refinery India",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Barron's", "url": "https://www.barrons.com"},
        {"name": "LiveMint", "url": "https://www.livemint.com"},
        {"name": "Investors Business Daily", "url": "https://www.investors.com"}
    ]),
    "body": """As Donald Trump sat down in the White House Situation Room on Friday afternoon, the stakes extended well beyond Washington and Tehran. For India — the world's third-largest oil importer and a country that depends on foreign crude for roughly 90 percent of its needs — the next few hours could determine whether energy prices ease or spiral further into crisis territory.

## The Deal on the Table

The United States and Iran have reportedly reached a framework agreement to extend their ceasefire for another 60 days and lift restrictions on shipping through the Strait of Hormuz, the narrow waterway that carries a fifth of the world's oil and liquefied natural gas. Four sources familiar with the negotiations told Reuters the deal would specify unrestricted shipping through the strait and require the US to lift its blockade of Iranian ports and ease some sanctions on Iranian oil sales.

But Trump added conditions that Iran has previously rejected. "Iran must agree that they will never have a Nuclear Weapon or Bomb. The Hormuz Strait must be immediately open, no tolls, for unrestricted shipping traffic, in both directions," Trump posted on Truth Social before heading into his meeting. He added that nuclear material would be "unearthed" by the US.

Iran's top negotiator Mohammad Baqer Qalibaf struck a sceptical tone. "We do not trust guarantees and words, only actions are the criterion," he said. "The winner of any agreement is the one who is better prepared for war the day after."

## Why India Cannot Afford to Wait

The war launched by the US and Israel on February 28 has choked the Strait of Hormuz for three months. For India, the consequences have been immediate and severe.

The Indian crude oil basket — the weighted average of Brent and Dubai/Oman grades that Indian refiners actually import — stood at $102.05 per barrel as of May 26, according to the petroleum ministry. That is a punishing premium for a country that spent $157 billion on crude imports last fiscal year.

The pain has cascaded downstream. India's petroleum ministry acknowledged this week that shortages have appeared in parts of the country, driven by panic buying and an unusual shift: industrial consumers, including factories and fleet operators, have been abandoning private fuel retailers and flooding government-run retail outlets, where consumer-friendly pricing offers an arbitrage opportunity.

Private oil marketing companies have seen high-speed diesel offtake plunge by approximately 38 percent this month, the ministry said. Public sector bulk customer volumes have also declined by about 29 percent, as that demand migrates to retail outlets meant for households and small users.

## The Strategic Reserve Hedge

India has not been passive. The government ordered a 30-day strategic reserve of cooking gas this week, specifically citing the Iran war and Hormuz disruption risk. But strategic reserves are a finite buffer, not a solution.

Globally, governments have already released more than 400 million barrels from emergency reserves since the conflict began. The Brookings Institution estimates that once all temporary measures are exhausted — likely by July — the market could face a shortfall equivalent to roughly 16 percent of global crude trade. That scenario could send Brent prices far above their current $92 level.

Exxon's senior vice president Neil Chapman put it bluntly at a Bernstein investor conference on Thursday: "We're approaching unheard of inventory levels." The company has warned that oil could hit $150 a barrel if the strait remains closed through summer.

## What a Deal Would Mean — and What It Would Not

Oil prices fell on Friday on news of the potential agreement, with Brent crude dropping 2.25 percent to $91.60 and US benchmark crude falling 2.5 percent to $86.72. Markets are clearly pricing in a resolution.

But analysts caution against premature optimism. RBC Capital Markets analyst Helima Croft warned that even with a signed agreement, "we struggle to see how a sizeable number of Western shipping companies will be willing to risk transiting the waterway," given the ongoing risk of missile and drone attacks and possible mines.

The memorandum of understanding would require Iran to remove all mines from the strait within 30 days. But the April ceasefire proved that paper agreements and actual free passage are different things — tit-for-tat attacks continued even under the existing truce.

## The Diaspora Dimension

For the 5.4 million Indian Americans watching from the US, the stakes are double-edged. Higher energy prices in India mean higher inflation, weaker rupee remittance values, and economic stress on families back home. In the US, the Iran war has already pushed gasoline prices to their highest levels since the pandemic, squeezing household budgets across the country.

Pakistan's foreign minister Ishaq Dar arrived in Washington on Friday for talks with Secretary of State Marco Rubio, underscoring Islamabad's role as a key mediator. The diplomatic choreography involves not just the US and Iran but a web of regional interests — including India's, which has carefully maintained ties with both Washington and Tehran.

The next few hours in the Situation Room will not end this crisis. But they could determine whether the world's most important oil chokepoint begins to reopen — or whether India and the global economy brace for a much harder summer.""",
})

# ─── ARTICLE 2: China Nuclear Buildup — India Security ────────────────
articles.append({
    "headline": "Satellite Images Show China Building 80 Launch Pads Near Its Nuclear Silos. India Should Be Paying Attention.",
    "subheadline": "A Reuters investigation reveals a sprawling military complex in Xinjiang designed to ensure China can strike back after a nuclear attack. The implications reach far beyond the US-China rivalry.",
    "slug": "china-nuclear-missile-silos-xinjiang-launch-pads-india-security-20260529",
    "category": "news",
    "vertical": "news",
    "image_search_person": None,
    "image_fallback_query": "military satellite defense China",
    "image_fallback_query2": "nuclear missile defense system",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "Defense News", "url": "https://www.defensenews.com"},
        {"name": "Federation of American Scientists", "url": "https://fas.org"}
    ]),
    "body": """In the desert of eastern Xinjiang, China is building something that has left even the most seasoned nuclear weapons analysts startled.

Satellite images reviewed by Reuters reveal more than 80 concrete launch pads, hardened bunkers, communications nodes, and octagon-shaped military installations — all positioned near the nuclear missile silos that house China's longest-range intercontinental ballistic missiles. The construction, which has not been previously reported at this scale, represents what analysts call the most significant upgrade to China's land-based nuclear forces in decades.

"I've never seen anything quite like it," said Hans Kristensen, director of the Federation of American Scientists' Nuclear Information Project. "It's an extraordinary effort."

## The Architecture of Second Strike

The infrastructure is centred on two massive octagon-shaped installations built over the past six years, both southwest of the Hami nuclear silo fields in Xinjiang. One sits about 140 kilometres from the silos; the other, roughly 230 kilometres away.

The purpose, according to five security scholars who assessed the imagery for Reuters, appears designed to ensure that no American first strike could reliably knock out China's ability to retaliate with nuclear weapons — the doctrine known as "second-strike capability."

Satellite images show the octagon structures contain housing for personnel and large military vehicles, flanked by armoured bunkers and fortified weapons-storage areas. Airfields and railheads link the octagons to the Hami silos. Recent images from this month and April show exercises involving large military vehicles and what analysts said appear to be camouflaged launch sites cut into the desert, some with air-defence missile batteries.

The pads could field mobile air-defence missiles, electronic warfare nodes, or road-mobile ICBM launchers, three security scholars said. Conduits linking the pads to the octagon structures may contain fibre-optic cables for secure communications.

## Why India Cannot Ignore This

While the immediate framing of China's nuclear expansion centres on US-China competition, the implications for India are direct and consequential.

China's nuclear missiles can already reach any city in the United States — and every city in India. The Hami silo fields in Xinjiang are roughly 2,500 kilometres from India's northern border, well within the range from which intermediate-range ballistic missiles could be launched against Indian targets.

India and China held their 35th Working Mechanism for Consultation and Coordination on border affairs in Beijing just this week. Both sides called the talks "constructive." But constructive border meetings and a neighbouring nuclear buildup of unprecedented scale are two very different strategic signals.

The Quad — comprising India, the US, Japan, and Australia — pledged $20 billion this week to break China's grip on critical minerals, a move that reflects deepening strategic alignment against Beijing. India is positioned at the centre of that effort. But the Quad's economic countermeasures operate on a different timeline than nuclear modernisation.

India's own nuclear posture remains anchored in a "no first use" policy, a doctrine China also officially maintains. But some senior Western diplomats and analysts told Reuters they believe China would possibly resort to nuclear coercion to limit outside involvement in a conflict over Taiwan — a scenario that could reshape the security calculus for every nuclear-armed state in Asia.

## The Numbers That Matter

The Pentagon's latest report on China's military modernisation says the country is on track to field 1,000 warheads by 2030. It estimated China has likely loaded 100 ICBMs across its three main silo fields. For context, India's nuclear arsenal is estimated at roughly 170 warheads.

China has also strengthened its early-warning system with Huoyan-1 satellites that can detect an incoming ICBM within 90 seconds of launch and alert a command centre within three to four minutes — sufficient time to fire silo-based weapons before they are hit.

The scale of China's defensive infrastructure near its silos potentially sets it apart from the US and Russia, which rely on sheer numbers and hardened construction rather than extensive missile defence networks around their silo fields.

## Xi's Warning, Modi's Calculations

President Xi Jinping warned Donald Trump this month that mishandling of their countries' disagreements over Taiwan could lead them to a "dangerous place." That warning came weeks before the Reuters satellite investigation revealed the full scope of what China is building in the desert.

For New Delhi, the calculus is layered. India maintains strategic autonomy, purchasing Russian weapons systems while deepening ties with Washington. It engages with Beijing on border management while competing with China for influence across the Indo-Pacific. The nuclear dimension adds a layer that no amount of diplomatic language about "constructive talks" can paper over.

Tong Zhao, a senior fellow in nuclear policy at the Carnegie Endowment for International Peace, assessed the infrastructure as likely linked to "command, control, and communications — as well as maintenance and storage activities related to China's nuclear operations."

A third octagon-shaped installation south of the Lop Nur nuclear test facilities appears less developed and is being used as a target range. Satellite images show mock-ups of Western jet fighters and pock-marked earth from weapons testing.

China's defence ministry did not respond to Reuters' questions about the developments. The Pentagon said it would not comment on intelligence-related matters.

For India, the silence from Beijing may be the most telling signal of all.""",
})

# ─── ARTICLE 3: WHO Ebola Treatment Plan + Serum Institute ───────────
articles.append({
    "headline": "The WHO Just Named the Three Drugs and Two Vaccines That Could Stop Ebola. One Vaccine Is From India.",
    "subheadline": "With 906 suspected cases and 223 deaths, the WHO has fast-tracked experimental treatments for the Bundibugyo strain. The Oxford-Serum Institute vaccine could be ready for trials in two months.",
    "slug": "who-ebola-treatment-vaccines-serum-institute-oxford-bundibugyo-trials-20260529",
    "category": "news",
    "vertical": "news",
    "image_search_person": None,
    "image_fallback_query": "WHO Ebola health workers protective equipment Africa",
    "image_fallback_query2": "vaccine laboratory research",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com"},
        {"name": "ECDC", "url": "https://www.ecdc.europa.eu"},
        {"name": "WHO", "url": "https://www.who.int"}
    ]),
    "body": """Two weeks into the worst Ebola outbreak in six years, the World Health Organization has done something it rarely does with such speed: it has named specific drugs and vaccines for immediate clinical trials against a strain of the virus for which no approved treatment exists.

The announcement on Thursday marks a turning point in the response to the Bundibugyo Ebola epidemic sweeping through the Democratic Republic of the Congo and Uganda. Among the vaccine candidates the WHO has fast-tracked for evaluation is ChAdOx1 Bundibugyo — developed by Oxford University and the Serum Institute of India, the same partnership that produced one of the world's most widely used COVID-19 vaccines.

## The Treatment Shortlist

The WHO's expert advisory groups recommended three experimental drugs for priority evaluation in clinical trials among confirmed Bundibugyo virus disease cases:

**MBP134**, a monoclonal antibody cocktail from Mapp Biopharmaceutical. **Maftivimab**, a monoclonal antibody from Regeneron Pharmaceuticals, which already has supply on the ground in the DRC. And **remdesivir**, the antiviral from Gilead Sciences originally developed for hepatitis C and later used extensively during COVID-19.

The WHO also recommended evaluating combination therapy — a monoclonal antibody paired with remdesivir — to determine whether dual-action treatment improves survival rates.

For post-exposure prevention in contacts of confirmed cases, the WHO highlighted Gilead's experimental oral antiviral obeldesivir as a priority candidate, though its effectiveness depends on robust contact tracing — a formidable challenge in the conflict-affected eastern DRC.

## India's Vaccine in the Race

Among vaccines, the WHO identified two leading candidates. The most promising is rVSV Bundibugyo, a single-dose vaccine being developed by the International AIDS Vaccine Initiative. But it is unlikely to be ready for trials for another seven to nine months — an eternity in an active outbreak.

That makes the second candidate critically important. ChAdOx1 Bundibugyo, developed by Oxford University and manufactured by the Serum Institute of India in Pune, could be available for efficacy testing within two to three months, the WHO said. The vaccine uses the same chimpanzee adenovirus vector technology that powered the Oxford-AstraZeneca COVID-19 vaccine, which the Serum Institute produced at a scale of over one billion doses.

Additional animal data are still needed before human trials can begin. But the timeline is aggressive by any standard — a reflection of how rapidly the outbreak is escalating.

The WHO also reviewed Merck's Ervebo, the only licensed Ebola vaccine in the world. But it recommended against deployment outside research settings, saying evidence of protection against the Bundibugyo strain "remains limited and inconclusive." Ervebo was designed for the Zaire strain of Ebola, which is genetically distinct.

## The Numbers Keep Climbing

The DRC's Ministry of Health reported on Wednesday that there are now 125 confirmed Ebola cases, including 17 deaths, and 906 suspected cases with 223 suspected deaths across Ituri, North Kivu, and South Kivu provinces. Uganda has confirmed nine cases, including one death, with at least three linked to travel from the DRC.

The WHO declared the outbreak a Public Health Emergency of International Concern on May 16 — just one day after it was first reported — reflecting the speed and severity of the spread.

"It's a disease that you get when you care for someone — for your husband or your partner or your child or your mother," said Anaïs Legand, a WHO technical officer. "You get it when you want to help someone with symptoms, and this is terrible."

The mortality rate among confirmed cases ranges from 30 to 50 percent. "Five out of ten people are likely to die," Legand said. "We can scale up optimised intensive care. We can support communities to recognise the symptoms early."

## India's Dual Exposure

India has already felt the outbreak's impact. A suspected Ebola case — a woman who had travelled from Uganda — was quarantined in Bengaluru this week, prompting India to postpone the India-Africa Summit. The government dispatched its first medical shipment to affected countries in Africa, positioning India as both a responder and a potential vaccine supplier.

The Serum Institute's role is not incidental. CEO Adar Poonawalla has built the world's largest vaccine manufacturing facility specifically to serve as a rapid-response platform for emerging outbreaks. The institute's capacity to scale production from clinical-trial quantities to mass doses within weeks is a strategic asset that the WHO has relied on before.

Uganda has now closed its border with the DRC at the Kasindi-Lubiriha crossing, deploying military personnel and health workers for temperature checks and disinfection. Stranded traders and disrupted commerce underscore how the health crisis is rapidly becoming an economic one for the region.

## What Comes Next

The WHO is working with the DRC and Uganda to set up clinical trial sites. Regeneron confirmed that maftivimab supply is already positioned in the DRC for immediate use. Gilead said it is prepared to work with governments and global partners to support response efforts.

But the fundamental challenge remains: the Bundibugyo strain is a variant for which the world had no specific countermeasures until this week. Every day that passes without approved treatments means more families face the disease with nothing but supportive care.

The race between the virus and the trials has begun. And for once, India is not just watching from the sidelines — it is manufacturing one of the frontrunners.""",
})


# ── Main execution ────────────────────────────────────────────────────
def main():
    published = 0
    for i, art in enumerate(articles, 1):
        print(f"\n{'='*60}")
        print(f"Article {i}: {art['headline'][:70]}...")
        print(f"{'='*60}")

        # Image sourcing
        img_url = None

        # Try Wikipedia if there's a person
        if art.get("image_search_person"):
            img_url = fetch_wikipedia_person_image(art["image_search_person"])
            if img_url and not validate_image(img_url):
                print(f"  ⚠ Wikipedia image failed validation, trying Pexels")
                img_url = None

        # Fallback to Pexels
        if not img_url:
            img_url = fetch_pexels_image(art["image_fallback_query"], art.get("image_fallback_query2"))
            if img_url and not validate_image(img_url):
                print(f"  ⚠ Pexels image failed validation")
                img_url = None

        if img_url:
            print(f"  ✓ Final image: {img_url[:80]}...")
        else:
            print(f"  ⚠ No valid image found — publishing without image")

        # Build article payload
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "headline": art["headline"],
            "subheadline": art["subheadline"],
            "slug": art["slug"],
            "body": art["body"],
            "category": "news",
            "vertical": "news",
            "status": "published",
            "published_at": now,
            "sources": json.loads(art["sources"]),
            "image_url": img_url,
            "image_attribution": "Wikimedia Commons" if img_url and "wikimedia" in (img_url or "").lower() else ("Pexels" if img_url else None),
        }

        result = sb_insert("p2_articles", payload)
        if result:
            rid = result[0]["id"] if isinstance(result, list) else result.get("id")
            print(f"  ✓ Published: {rid}")
            print(f"    Slug: {art['slug']}")
            published += 1
        else:
            print(f"  ✗ Failed to publish")

        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"Done. Published {published}/{len(articles)} articles.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
