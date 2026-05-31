import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";

function GuideLayout({ title, description, canonicalPath, children }: { title: string; description: string; canonicalPath: string; children: React.ReactNode }) {
  return (
    <>
      <Helmet>
        <title>{title} | Cars — The Videshi</title>
        <meta name="description" content={description} />
        <meta property="og:title" content={`${title} | The Videshi`} />
        <meta property="og:description" content={description} />
        <link rel="canonical" href={`https://www.thevideshi.com${canonicalPath}`} />
      </Helmet>
      <Masthead />
      <CategoryPills />
      <main className="container py-8 max-w-3xl mx-auto">
        <nav className="flex items-center gap-2 text-sm text-foreground/50 mb-6">
          <Link to="/cars" className="hover:text-primary transition-colors flex items-center gap-1">
            <ChevronLeft className="h-4 w-4" /> Cars
          </Link>
          <span>/</span>
          <span className="text-foreground/70">Guide</span>
        </nav>
        <h1 className="font-serif text-3xl md:text-4xl font-bold mb-6">{title}</h1>
        <article className="prose prose-invert prose-sm max-w-none space-y-6 text-foreground/80 leading-relaxed">
          {children}
        </article>
        <div className="mt-12 pt-6 border-t border-border/50">
          <Link to="/cars" className="text-primary hover:underline text-sm">← Back to Cars</Link>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}

/* ================================================================== */

export function FirstCarGuide() {
  return (
    <GuideLayout canonicalPath="/cars/guide/first-car-in-america" title="Your First Car in America" description="Step-by-step guide for H-1B and L-1 visa holders buying their first car in the US.">
      <section>
        <h2 className="text-xl font-bold text-foreground mb-3">🇺🇸 The H-1B/L-1 Car Buying Checklist</h2>
        <p>Just arrived in the US? Here's exactly what you need to do to get your first car — no American credit history required.</p>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">Step 1: Get Your Driver's License</h3>
        <ul className="space-y-2 ml-4">
          <li>• Your Indian license works for a limited time (varies by state — typically 30-90 days)</li>
          <li>• Apply for a state license ASAP — you need your passport, visa, I-94, and SSN</li>
          <li>• Most states require a written test + road test. Study the DMV handbook.</li>
          <li>• Some states (CA, TX, NJ) have long wait times — book your appointment early</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">Step 2: Build Credit (or Work Around It)</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>No credit ≠ bad credit.</strong> Some lenders work with thin-file borrowers</li>
          <li>• Get a secured credit card immediately (Discover It Secured, Capital One)</li>
          <li>• Some dealers have "international professional" programs for H-1B holders</li>
          <li>• Toyota, Honda, and Hyundai dealer financing are more flexible with new immigrants</li>
          <li>• Credit unions (like BECU, Alliant) often give better rates than dealership financing</li>
          <li>• A larger down payment (20-30%) helps you get approved</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">Step 3: Decide — Lease vs Buy</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>Lease</strong> if: You're unsure how long you'll stay, want lower monthly payments, or want a new car every 3 years</li>
          <li>• <strong>Buy</strong> if: You plan to stay 5+ years, want to build equity, or drive more than 12K miles/year</li>
          <li>• Most H-1B holders: <strong>buy a reliable used car (2-3 years old)</strong> to build credit and save money</li>
          <li>• See our <Link to="/cars/guide/lease-vs-buy" className="text-primary hover:underline">Lease vs Buy</Link> guide for details</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">Step 4: Get Insurance BEFORE Buying</h3>
        <ul className="space-y-2 ml-4">
          <li>• You MUST have insurance before driving off the lot</li>
          <li>• Get quotes from 3+ providers: Geico, Progressive, State Farm, Liberty Mutual</li>
          <li>• New immigrant = higher rates (no US driving history). Expect $150-250/month initially</li>
          <li>• Ask about international driving record discounts — some insurers accept Indian driving history</li>
          <li>• See our <Link to="/cars/guide/insurance-for-new-immigrants" className="text-primary hover:underline">Insurance Guide</Link></li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">Step 5: Where to Buy</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>Dealerships:</strong> Higher price but financing is easier. Good for new arrivals with no credit.</li>
          <li>• <strong>Certified Pre-Owned (CPO):</strong> Best value — used car with manufacturer warranty. Toyota and Honda CPO are excellent.</li>
          <li>• <strong>Private party:</strong> Cheapest but riskiest. Get a pre-purchase inspection ($100-150).</li>
          <li>• <strong>Online:</strong> Carvana, CarMax — no-haggle pricing, good for people uncomfortable with dealer negotiation</li>
          <li>• <strong>Pro tip:</strong> Never go alone your first time. Bring a friend who's bought cars in the US before.</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-primary/5 border border-primary/10">
        <h3 className="font-bold text-foreground mb-3">💡 Our Recommendation for New H-1B Arrivals</h3>
        <p>Buy a <strong>2-3 year old Toyota Camry, Honda Civic, or Hyundai Tucson</strong> from a dealer with financing. Put 20% down. You'll build credit, have a reliable car, and in 2-3 years you can trade up to whatever you want with an established credit score.</p>
      </section>
    </GuideLayout>
  );
}

/* ================================================================== */

export function LeaseVsBuyGuide() {
  return (
    <GuideLayout canonicalPath="/cars/guide/lease-vs-buy" title="Lease vs Buy" description="Should you lease or buy your next car? A practical comparison for the Indian mindset.">
      <section>
        <h2 className="text-xl font-bold text-foreground mb-3">📊 The Quick Comparison</h2>
      </section>

      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-3 pr-4 text-foreground/50 font-medium w-1/3"></th>
              <th className="text-left py-3 px-4 font-bold text-foreground">Lease</th>
              <th className="text-left py-3 px-4 font-bold text-foreground">Buy (Finance)</th>
            </tr>
          </thead>
          <tbody className="text-foreground/70">
            <tr className="border-b border-border/30"><td className="py-3 pr-4 font-medium text-foreground/50">Monthly payment</td><td className="py-3 px-4">Lower ($250-500)</td><td className="py-3 px-4">Higher ($350-700)</td></tr>
            <tr className="border-b border-border/30"><td className="py-3 pr-4 font-medium text-foreground/50">Down payment</td><td className="py-3 px-4">$2,000-5,000</td><td className="py-3 px-4">10-20% recommended</td></tr>
            <tr className="border-b border-border/30"><td className="py-3 pr-4 font-medium text-foreground/50">Own the car?</td><td className="py-3 px-4">❌ No — you return it</td><td className="py-3 px-4">✅ Yes — it's yours</td></tr>
            <tr className="border-b border-border/30"><td className="py-3 pr-4 font-medium text-foreground/50">Mileage limits</td><td className="py-3 px-4">10-12K/yr (overage fees)</td><td className="py-3 px-4">No limits</td></tr>
            <tr className="border-b border-border/30"><td className="py-3 pr-4 font-medium text-foreground/50">Maintenance</td><td className="py-3 px-4">Usually under warranty</td><td className="py-3 px-4">Your responsibility after warranty</td></tr>
            <tr className="border-b border-border/30"><td className="py-3 pr-4 font-medium text-foreground/50">New car every 3 years?</td><td className="py-3 px-4">✅ Yes</td><td className="py-3 px-4">Only if you sell/trade</td></tr>
            <tr className="border-b border-border/30"><td className="py-3 pr-4 font-medium text-foreground/50">Total cost (5 years)</td><td className="py-3 px-4">Higher (no equity built)</td><td className="py-3 px-4">Lower (car has resale value)</td></tr>
            <tr><td className="py-3 pr-4 font-medium text-foreground/50">Builds credit?</td><td className="py-3 px-4">✅ Yes</td><td className="py-3 px-4">✅ Yes</td></tr>
          </tbody>
        </table>
      </div>

      <section className="p-5 rounded-xl bg-primary/5 border border-primary/10">
        <h3 className="font-bold text-foreground mb-3">🇮🇳 The Indian Mindset Factor</h3>
        <p className="mb-3">Most Indians grew up hearing "why pay rent when you can own?" — and that logic applies to cars too. <strong>Buying builds equity</strong>. After 5 years of loan payments, you own a car worth $15-20K. After 5 years of lease payments, you own nothing.</p>
        <p>However, leasing makes sense if: you're on a visa and might return to India, you want predictable costs with no surprise repairs, or you love driving the latest models.</p>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">When to LEASE</h3>
        <ul className="space-y-2 ml-4">
          <li>• You're on H-1B and unsure about long-term US plans</li>
          <li>• You drive less than 12,000 miles/year</li>
          <li>• You want a luxury car at a lower monthly cost</li>
          <li>• You hate dealing with car maintenance and selling</li>
          <li>• Your company reimburses car payments</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">When to BUY</h3>
        <ul className="space-y-2 ml-4">
          <li>• You have a green card or plan to stay long-term</li>
          <li>• You drive more than 12,000 miles/year</li>
          <li>• You want to build equity in the car</li>
          <li>• You plan to keep the car 5+ years</li>
          <li>• You want the freedom to modify or customize</li>
        </ul>
      </section>
    </GuideLayout>
  );
}

/* ================================================================== */

export function InsuranceGuide() {
  return (
    <GuideLayout canonicalPath="/cars/guide/insurance-for-new-immigrants" title="Car Insurance for New Immigrants" description="How to get car insurance in the US with no American driving history. A guide for new Indian immigrants.">
      <section>
        <h2 className="text-xl font-bold text-foreground mb-3">🛡️ Insurance Basics for New Arrivals</h2>
        <p>Car insurance is mandatory in every US state. As a new immigrant with no US driving history, expect to pay more initially — but there are ways to save.</p>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">What You Need</h3>
        <ul className="space-y-2 ml-4">
          <li>• Valid US or state driver's license (some accept international licenses temporarily)</li>
          <li>• Vehicle information (VIN, make, model, year)</li>
          <li>• SSN or ITIN (some providers work without SSN)</li>
          <li>• Address in the US</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">Coverage Types</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>Liability (required):</strong> Covers damage you cause to others. Minimum varies by state.</li>
          <li>• <strong>Collision:</strong> Covers your car in an accident. Required if financing/leasing.</li>
          <li>• <strong>Comprehensive:</strong> Covers theft, weather, vandalism. Also required for financed cars.</li>
          <li>• <strong>Uninsured Motorist:</strong> Covers you if hit by an uninsured driver. Highly recommended.</li>
          <li>• <strong>Our advice:</strong> Get at least 100/300/100 liability + collision + comprehensive</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">Best Providers for New Immigrants</h3>
        <ul className="space-y-3 ml-4">
          <li>• <strong>Geico:</strong> Often cheapest, accepts international driving records from some countries</li>
          <li>• <strong>Progressive:</strong> Snapshot program can lower rates based on actual driving</li>
          <li>• <strong>State Farm:</strong> Local agents can help navigate the process in person</li>
          <li>• <strong>Liberty Mutual:</strong> Good rates for H-1B tech professionals</li>
          <li>• <strong>The General / Root:</strong> Options if major insurers decline you</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-primary/5 border border-primary/10">
        <h3 className="font-bold text-foreground mb-3">💡 Money-Saving Tips</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>Get 3+ quotes:</strong> Prices vary wildly. Always compare.</li>
          <li>• <strong>Bundle:</strong> Combine with renter's insurance for 10-15% discount</li>
          <li>• <strong>Drive a safe, boring car:</strong> Honda Civic and Toyota Camry are cheapest to insure</li>
          <li>• <strong>Higher deductible = lower premium:</strong> $1,000 deductible saves ~20% vs $500</li>
          <li>• <strong>Ask about professional discounts:</strong> Engineers, doctors, teachers often get lower rates</li>
          <li>• <strong>After 6 months of clean driving:</strong> Re-quote. Your rate should drop significantly.</li>
        </ul>
      </section>
    </GuideLayout>
  );
}

/* ================================================================== */

export function BestFamilySuvsGuide() {
  return (
    <GuideLayout canonicalPath="/cars/guide/best-family-suvs" title="Best Family SUVs for Indian Families" description="Top 3-row SUVs ranked for desi families — space, safety, value, and road trip readiness.">
      <section>
        <h2 className="text-xl font-bold text-foreground mb-3">👨‍👩‍👧‍👦 The Desi Family Car Criteria</h2>
        <p>When the in-laws visit, when you're loading up for a road trip to Niagara Falls, when 3 car seats need to fit across — these SUVs deliver.</p>
      </section>

      <div className="space-y-6">
        {[
          {
            rank: "🥇",
            name: "Hyundai Palisade",
            price: "From $38,500",
            why: "The best overall family SUV right now. Near-luxury interior, spacious 2nd and 3rd rows, and a 10-year warranty. Costs $20K less than a comparable Mercedes GLE.",
            best: "Best value 3-row",
            link: "/cars/2026-hyundai-palisade",
          },
          {
            rank: "🥈",
            name: "Toyota Highlander Hybrid",
            price: "From $41,070",
            why: "Unbeatable fuel economy for a 3-row (36 MPG). Toyota reliability means this car will still be running when your kids learn to drive. Standard AWD handles any weather.",
            best: "Best fuel economy",
            link: "/cars/2026-toyota-highlander-hybrid",
          },
          {
            rank: "🥉",
            name: "Kia Telluride",
            price: "From $37,690",
            why: "More rugged styling than the Palisade with slightly more cargo space. Same excellent value proposition. 10-year warranty included.",
            best: "Best cargo space",
            link: "/cars/2026-kia-telluride",
          },
          {
            rank: "4",
            name: "Toyota Grand Highlander Hybrid",
            price: "From $45,070",
            why: "Stretched Highlander with a truly usable 3rd row. Adults can actually sit back there. Hybrid efficiency is impressive for something this size.",
            best: "Best 3rd row space",
            link: "/cars/2026-toyota-grand-highlander-hybrid",
          },
          {
            rank: "5",
            name: "Acura MDX",
            price: "From $51,100",
            why: "Honda reliability in a luxury wrapper with 3 rows standard. Lower maintenance costs than German rivals. The Type S with 355 HP is surprisingly fun.",
            best: "Best luxury value with 3 rows",
            link: "/cars/2026-acura-mdx",
          },
        ].map((suv) => (
          <Link key={suv.name} to={suv.link} className="block group">
            <div className="p-5 rounded-xl bg-muted/20 border border-border/50 hover:border-primary/40 transition-colors">
              <div className="flex items-start gap-3">
                <span className="text-2xl">{suv.rank}</span>
                <div className="flex-1">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <h3 className="font-bold text-foreground group-hover:text-primary transition-colors">{suv.name}</h3>
                    <span className="text-sm font-bold text-primary">{suv.price}</span>
                  </div>
                  <p className="text-sm text-foreground/60 mt-1">{suv.why}</p>
                  <span className="inline-block mt-2 text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary">{suv.best}</span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      <section className="p-5 rounded-xl bg-primary/5 border border-primary/10">
        <h3 className="font-bold text-foreground mb-3">💡 Pro Tips for Family Car Shopping</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>Test the 3rd row:</strong> Sit in it yourself. If you're uncomfortable in 5 minutes, your parents will be miserable on a 4-hour drive.</li>
          <li>• <strong>Check car seat compatibility:</strong> Try installing your car seats before buying. Not all 3-row SUVs fit 3 across.</li>
          <li>• <strong>Cargo with 3rd row up:</strong> The number that matters. Some SUVs have zero usable cargo when the 3rd row is occupied.</li>
          <li>• <strong>Sliding 2nd row:</strong> Essential for easy 3rd row access. Palisade and Highlander have this.</li>
          <li>• <strong>Hybrid if possible:</strong> With gas near $5/gallon in California, a hybrid 3-row saves $1,500+/year.</li>
        </ul>
      </section>
    </GuideLayout>
  );
}


/* ================================================================== */

export function CarsUnder30KGuide() {
  return (
    <GuideLayout canonicalPath="/cars/guide/best-cars-under-30k" title="Best Cars Under $30K for New Immigrants" description="Reliable, affordable cars for NRIs building credit in America — ranked by total cost of ownership.">
      <section>
        <h2 className="text-xl font-bold text-foreground mb-3">💰 Why Under-$30K Is the Sweet Spot</h2>
        <p>You just landed in America. You need a car that starts every morning, won't drain your savings on repairs, and won't scare off a lender who's never seen your credit file. The under-$30K bracket is where reliability, insurance costs, and resale value converge perfectly for new immigrants.</p>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">Why Reliability Matters More for NRIs</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>No mechanic uncle nearby.</strong> In India, you had a trusted mechanic who charged ₹500 for a fix. In America, a check-engine visit starts at $150 just for the diagnostic.</li>
          <li>• <strong>No backup car.</strong> If your car is in the shop for 3 days, that's 3 days of Uber to work at $40/day.</li>
          <li>• <strong>Thin credit = expensive surprises.</strong> You can't just swipe a credit card for a $2,000 repair when your limit is $500.</li>
          <li>• <strong>Resale value protects you.</strong> If plans change and you return to India, a Toyota or Honda sells in a weekend. A Chrysler sits for months.</li>
        </ul>
      </section>

      <div className="space-y-6">
        <h2 className="text-xl font-bold text-foreground">🏆 Our Top Picks</h2>

        <Link to="/cars/2026-honda-civic" className="block group">
          <div className="p-5 rounded-xl bg-muted/20 border border-border/50 hover:border-primary/40 transition-colors">
            <div className="flex items-start gap-3">
              <span className="text-2xl">🥇</span>
              <div className="flex-1">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <h3 className="font-bold text-foreground group-hover:text-primary transition-colors">Honda Civic</h3>
                  <span className="text-sm font-bold text-primary">From $24,950</span>
                </div>
                <p className="text-sm text-foreground/60 mt-1">The gold standard. Cheapest to insure in its class, highest resale value, and Honda dealerships are everywhere. The 2026 gets 36 MPG combined. This is the car half of Silicon Valley drove when they first arrived on H-1B.</p>
                <span className="inline-block mt-2 text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary">Best overall pick</span>
              </div>
            </div>
          </div>
        </Link>

        <Link to="/cars/2026-toyota-camry" className="block group">
          <div className="p-5 rounded-xl bg-muted/20 border border-border/50 hover:border-primary/40 transition-colors">
            <div className="flex items-start gap-3">
              <span className="text-2xl">🥈</span>
              <div className="flex-1">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <h3 className="font-bold text-foreground group-hover:text-primary transition-colors">Toyota Camry</h3>
                  <span className="text-sm font-bold text-primary">From $30,450</span>
                </div>
                <p className="text-sm text-foreground/60 mt-1">Slightly above $30K at base but the hybrid trim is worth the stretch — 52 MPG means you're spending $80/month on gas instead of $150. The Camry is the car your parents will approve of: sensible, safe, and it runs forever. Every Toyota dealer in America knows how to service it.</p>
                <span className="inline-block mt-2 text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary">Best for long-term ownership</span>
              </div>
            </div>
          </div>
        </Link>

        <Link to="/cars/2026-hyundai-sonata" className="block group">
          <div className="p-5 rounded-xl bg-muted/20 border border-border/50 hover:border-primary/40 transition-colors">
            <div className="flex items-start gap-3">
              <span className="text-2xl">🥉</span>
              <div className="flex-1">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <h3 className="font-bold text-foreground group-hover:text-primary transition-colors">Hyundai Sonata</h3>
                  <span className="text-sm font-bold text-primary">From $29,350</span>
                </div>
                <p className="text-sm text-foreground/60 mt-1">Best feature-to-price ratio under $30K. You get a 10.25" touchscreen, wireless CarPlay, and advanced safety tech that costs extra on Honda and Toyota. The 10-year/100K-mile powertrain warranty is unbeatable peace of mind for new immigrants.</p>
                <span className="inline-block mt-2 text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary">Best warranty &amp; features</span>
              </div>
            </div>
          </div>
        </Link>

        <Link to="/cars/2026-honda-accord" className="block group">
          <div className="p-5 rounded-xl bg-muted/20 border border-border/50 hover:border-primary/40 transition-colors">
            <div className="flex items-start gap-3">
              <span className="text-2xl">4</span>
              <div className="flex-1">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <h3 className="font-bold text-foreground group-hover:text-primary transition-colors">Honda Accord</h3>
                  <span className="text-sm font-bold text-primary">From $29,690</span>
                </div>
                <p className="text-sm text-foreground/60 mt-1">The bigger sibling of the Civic — more rear legroom for when parents visit. The Accord has been the "professional's sedan" for decades. Drives more like a luxury car than its price suggests.</p>
                <span className="inline-block mt-2 text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary">Best backseat comfort</span>
              </div>
            </div>
          </div>
        </Link>

        <Link to="/cars/2026-kia-sportage-hybrid" className="block group">
          <div className="p-5 rounded-xl bg-muted/20 border border-border/50 hover:border-primary/40 transition-colors">
            <div className="flex items-start gap-3">
              <span className="text-2xl">5</span>
              <div className="flex-1">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <h3 className="font-bold text-foreground group-hover:text-primary transition-colors">Kia Sportage Hybrid</h3>
                  <span className="text-sm font-bold text-primary">From $34,090</span>
                </div>
                <p className="text-sm text-foreground/60 mt-1">Need an SUV but don't want SUV gas bills? The Sportage Hybrid gets 38 MPG with AWD. Higher ride height is great for snowy states. Kia's 10-year warranty matches Hyundai's.</p>
                <span className="inline-block mt-2 text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary">Best affordable hybrid SUV</span>
              </div>
            </div>
          </div>
        </Link>
      </div>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">Total Cost of Ownership — What Really Matters</h3>
        <p className="mb-3">The sticker price is only half the story. Here's what first-year ownership actually looks like on a ~$28K car:</p>
        <ul className="space-y-2 ml-4">
          <li>• <strong>Insurance:</strong> $1,800-3,000/year for new immigrants (no US driving history). Honda Civic is cheapest to insure; see our <Link to="/cars/guide/insurance-for-new-immigrants" className="text-primary hover:underline">insurance guide</Link></li>
          <li>• <strong>Gas:</strong> $1,200-2,400/year depending on MPG and commute. Hybrids save $600+/year</li>
          <li>• <strong>Depreciation:</strong> ~15% in year one. Toyota/Honda lose least; Kia/Hyundai lose more but cost less upfront</li>
          <li>• <strong>Maintenance:</strong> $400-800/year for oil changes, tires, and routine service. Japanese brands are cheapest</li>
          <li>• <strong>Registration &amp; taxes:</strong> Varies wildly by state. California charges ~1% of value/year; Texas has no income tax but higher registration</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-primary/5 border border-primary/10">
        <h3 className="font-bold text-foreground mb-3">💡 The Videshi Recommendation</h3>
        <p className="mb-2">If you're on H-1B with no credit history: walk into a <strong>Honda dealer</strong>, ask about their new immigrant financing program, put 20% down on a <strong>Civic or Accord</strong>, and get a 48-month loan. In two years, your credit score will be 750+ and you can upgrade to whatever you want.</p>
        <p>Already have established credit? The <strong>Hyundai Sonata</strong> gives you the most car for the money, and that 10-year warranty means you won't spend a rupee on repairs for a decade.</p>
      </section>
    </GuideLayout>
  );
}

/* ================================================================== */

export function BestEVsGuide() {
  return (
    <GuideLayout canonicalPath="/cars/guide/best-evs-2026" title="Best EVs Worth Switching To in 2026" description="Electric vehicles ranked for the Indian diaspora — tax credits, apartment charging, and whether an EV actually makes sense for NRIs.">
      <section>
        <h2 className="text-xl font-bold text-foreground mb-3">⚡ The Big Question: Is an EV Right for You?</h2>
        <p>Electric vehicles are cheaper to fuel, cheaper to maintain, and qualify for up to $7,500 in federal tax credits. But most NRIs live in apartments, not houses with garages. Let's figure out if an EV makes sense for your situation.</p>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">The Apartment Problem (and Solutions)</h3>
        <p className="mb-3">Here's the reality: roughly 60% of Indian immigrants in America rent apartments, not houses. No garage = no home charger. But that doesn't mean EVs are off the table:</p>
        <ul className="space-y-2 ml-4">
          <li>• <strong>Workplace charging:</strong> Most tech campuses (Google, Meta, Microsoft, Apple, Amazon) have free or cheap EV charging. If you charge at work, you never need home charging.</li>
          <li>• <strong>Apartment chargers:</strong> Newer complexes in Bay Area, Seattle, and Austin increasingly offer EV charging stations. Ask your leasing office.</li>
          <li>• <strong>Supercharger/DC fast charging:</strong> Tesla Superchargers and Electrify America stations can add 200 miles in 20-30 minutes. Plan a weekly charging stop at Costco or Target.</li>
          <li>• <strong>Plug-in Hybrids (PHEVs):</strong> If charging access is truly limited, consider a plug-in hybrid — 40-50 miles on electric, then gas kicks in. Best of both worlds.</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">Federal Tax Credit — $7,500 Back</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>Who qualifies:</strong> US taxpayers with AGI under $150K (single) or $300K (married). Most H-1B professionals qualify.</li>
          <li>• <strong>How it works:</strong> $7,500 off your federal tax bill. If you owe $10K in taxes, you now owe $2,500. Not a refund — a credit against taxes owed.</li>
          <li>• <strong>Eligible vehicles:</strong> Must be assembled in North America. Tesla Model 3/Y, Chevy Equinox EV, and select Hyundai/Kia models qualify. Check <strong>fueleconomy.gov</strong> for the latest list.</li>
          <li>• <strong>Point of sale:</strong> Starting 2024, you can transfer the credit to the dealer and get it as an instant discount at purchase. No waiting for tax season.</li>
          <li>• <strong>State incentives:</strong> California adds up to $7,500 more (CVRP + IVP). Colorado offers $5,000. Check your state.</li>
        </ul>
      </section>

      <div className="space-y-6">
        <h2 className="text-xl font-bold text-foreground">🏆 Best EVs for Indian Americans in 2026</h2>

        <Link to="/cars/2026-tesla-model-y" className="block group">
          <div className="p-5 rounded-xl bg-muted/20 border border-border/50 hover:border-primary/40 transition-colors">
            <div className="flex items-start gap-3">
              <span className="text-2xl">🥇</span>
              <div className="flex-1">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <h3 className="font-bold text-foreground group-hover:text-primary transition-colors">Tesla Model Y</h3>
                  <span className="text-sm font-bold text-primary">From $44,990</span>
                </div>
                <p className="text-sm text-foreground/60 mt-1">The default choice — and for good reason. 310+ mile range, the best Supercharger network (20,000+ stations), and OTA updates that add features for free. The Long Range AWD handles New Jersey winters and Bay Area summers equally well. Your tech coworkers all drive one, and there's a reason.</p>
                <span className="inline-block mt-2 text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary">Best overall EV • $7,500 credit eligible</span>
              </div>
            </div>
          </div>
        </Link>

        <Link to="/cars/2026-tesla-model-3" className="block group">
          <div className="p-5 rounded-xl bg-muted/20 border border-border/50 hover:border-primary/40 transition-colors">
            <div className="flex items-start gap-3">
              <span className="text-2xl">🥈</span>
              <div className="flex-1">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <h3 className="font-bold text-foreground group-hover:text-primary transition-colors">Tesla Model 3</h3>
                  <span className="text-sm font-bold text-primary">From $38,990</span>
                </div>
                <p className="text-sm text-foreground/60 mt-1">Everything the Model Y offers but in sedan form and $6K cheaper. 341-mile range on the Long Range version. After the $7,500 tax credit, you're looking at ~$31,500 — less than a loaded Camry. Best value per mile of range in the market.</p>
                <span className="inline-block mt-2 text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary">Best value EV • $7,500 credit eligible</span>
              </div>
            </div>
          </div>
        </Link>

        <div className="p-5 rounded-xl bg-muted/20 border border-border/50">
          <div className="flex items-start gap-3">
            <span className="text-2xl">🥉</span>
            <div className="flex-1">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <h3 className="font-bold text-foreground">Hyundai Ioniq 5</h3>
                <span className="text-sm font-bold text-primary">From $44,650</span>
              </div>
              <p className="text-sm text-foreground/60 mt-1">The anti-Tesla. Retro styling that turns heads, 800V ultra-fast charging (10-80% in 18 minutes), and a spacious flat floor that feels like sitting in a living room. The 10-year warranty gives it an edge for NRIs who value peace of mind over brand cachet.</p>
              <span className="inline-block mt-2 text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary">Fastest charging • 10-year warranty</span>
            </div>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-muted/20 border border-border/50">
          <div className="flex items-start gap-3">
            <span className="text-2xl">4</span>
            <div className="flex-1">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <h3 className="font-bold text-foreground">Chevrolet Equinox EV</h3>
                <span className="text-sm font-bold text-primary">From $33,900</span>
              </div>
              <p className="text-sm text-foreground/60 mt-1">The most affordable EV that doesn't feel like a compromise. 319-mile range, proper SUV size, and GM's Ultium platform is solid. After the $7,500 tax credit, this drops to ~$26,400 — essentially Corolla money for an electric SUV. Hard to beat on value.</p>
              <span className="inline-block mt-2 text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary">Most affordable EV SUV • $7,500 credit eligible</span>
            </div>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-muted/20 border border-border/50">
          <div className="flex items-start gap-3">
            <span className="text-2xl">5</span>
            <div className="flex-1">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <h3 className="font-bold text-foreground">Kia EV6</h3>
                <span className="text-sm font-bold text-primary">From $43,975</span>
              </div>
              <p className="text-sm text-foreground/60 mt-1">Shares its platform with the Ioniq 5 but with sportier styling and better driving dynamics. The GT version does 0-60 in 3.4 seconds — quicker than most sports cars. Same ultra-fast 800V charging and 10-year warranty as its Hyundai sibling.</p>
              <span className="inline-block mt-2 text-xs font-medium px-2 py-0.5 rounded-full bg-primary/10 text-primary">Sportiest EV under $50K</span>
            </div>
          </div>
        </div>
      </div>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">Climate Considerations for NRIs</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>Bay Area / Austin / Houston:</strong> Perfect EV climate. Mild weather means range stays consistent year-round. Abundant charging infrastructure.</li>
          <li>• <strong>Seattle / Portland:</strong> Great for EVs despite rain. Hydroelectric power means your electricity is among the cheapest and cleanest in the country.</li>
          <li>• <strong>New Jersey / Chicago / Boston:</strong> Cold weather reduces range by 20-30% in winter. Budget for ~250 miles on a 320-mile-rated car in January. Home or workplace charging becomes much more important.</li>
          <li>• <strong>Road trips to India… just kidding.</strong> But seriously — for those annual 5-hour drives to the temple in another state, the Tesla Supercharger network makes it seamless. One 20-minute stop and you're good.</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-primary/5 border border-primary/10">
        <h3 className="font-bold text-foreground mb-3">💡 The Videshi Verdict</h3>
        <p className="mb-2">If you charge at work or live in a newer apartment with EV chargers: the <Link to="/cars/2026-tesla-model-3" className="text-primary hover:underline">Tesla Model 3</Link> after the $7,500 credit is the best deal in cars right now. Period.</p>
        <p className="mb-2">If you need SUV space: the <Link to="/cars/2026-tesla-model-y" className="text-primary hover:underline">Tesla Model Y</Link> is the default. The Chevy Equinox EV is the budget pick.</p>
        <p>If you have zero charging access at home or work, skip the pure EV for now. Get a <Link to="/cars/2026-toyota-camry" className="text-primary hover:underline">Toyota Camry Hybrid</Link> — 52 MPG, no charging needed, and you'll still spend half what a gas SUV costs on fuel.</p>
      </section>
    </GuideLayout>
  );
}

/* ================================================================== */

export function IndiaVsUSDrivingGuide() {
  return (
    <GuideLayout canonicalPath="/cars/guide/india-vs-us-driving" title="India vs US: Everything Different About Driving" description="All the driving differences between India and America — road rules, highway culture, and the habits you need to unlearn.">
      <section>
        <h2 className="text-xl font-bold text-foreground mb-3">🔄 Two Countries, Two Completely Different Driving Universes</h2>
        <p>You drove in India for years. You think you know how to drive. Then you get on a US highway for the first time and realize: <em>everything</em> is different. This guide covers every adjustment you need to make — from the obvious (which side of the road) to the subtle (why Americans get irrationally angry if you honk).</p>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">🚗 The Basics (That You Already Know, But Let's Confirm)</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>Right-hand traffic.</strong> You drive on the right side of the road. The steering wheel is on the left. Your brain will fight you on turns for the first month.</li>
          <li>• <strong>The turn signal problem.</strong> You'll hit the wipers instead of the turn signal. Repeatedly. For weeks. It's on the other side of the steering column.</li>
          <li>• <strong>Miles, not kilometres.</strong> Speed limits are in MPH. 65 mph ≈ 105 kmph. When the sign says 65, it means 65 (not 65 as a suggestion).</li>
          <li>• <strong>Automatic transmission.</strong> Most cars in America are automatic. Your left foot does nothing. Resist the phantom clutch reflex.</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">🛣️ Highway Driving: The Biggest Culture Shock</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>Lane discipline is REAL.</strong> In India, lanes are a suggestion and the biggest vehicle has right of way. In America, you stay in your lane. Always. No straddling, no weaving, no "adjusting."</li>
          <li>• <strong>The left lane is for passing ONLY.</strong> Driving slowly in the left lane is considered extremely rude and can get you pulled over in some states. Pass, then move right.</li>
          <li>• <strong>Merging onto the highway.</strong> This terrifies new drivers. You have a short on-ramp to accelerate to 65 mph and merge into traffic. Match the speed of traffic BEFORE merging. Do not stop on the on-ramp.</li>
          <li>• <strong>The speed everyone actually drives:</strong> If the limit is 65, most people are doing 70-75. Going 55 in a 65 zone is more dangerous than going 75 because you're blocking traffic.</li>
          <li>• <strong>Tailgating.</strong> In India, bumper-to-bumper is normal. In America, leave 3 seconds of following distance. Tailgating causes road rage incidents — and Americans take road rage seriously.</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">🚦 Rules That Don't Exist in India</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>Right turn on red.</strong> You CAN turn right at a red light after coming to a complete stop and checking for traffic (in most states). This confuses new arrivals — yes, it's legal. Look for "No Turn on Red" signs.</li>
          <li>• <strong>4-way stop.</strong> Four cars arrive at an intersection with stop signs. Who goes first? The car that stopped first. If two arrive simultaneously, the car on the right goes first. This system is based entirely on trust and patience.</li>
          <li>• <strong>School buses.</strong> When a school bus has its red lights flashing and the stop sign extended, ALL traffic in BOTH directions must stop. Not slow down — STOP. The fine is $250-1,000 and you can lose your license. Americans take this extremely seriously.</li>
          <li>• <strong>Pedestrian right of way.</strong> Pedestrians in crosswalks always have right of way. Always. Even if they're walking slowly. Even if there's no traffic light. Stop and wait.</li>
          <li>• <strong>HOV lanes.</strong> The diamond lane (♦) on highways is for vehicles with 2+ occupants (varies by state). Using it alone gets you a $400+ ticket. EVs often get HOV access with a single driver — one more reason to consider going electric.</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">📯 The Horn: Forget Everything You Know</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>In India:</strong> The horn means "I'm here," "I'm coming through," "hello," "move," "thank you," and "I'm alive." You honk 50 times a day. It's communication.</li>
          <li>• <strong>In America:</strong> The horn means "DANGER" or "I am ANGRY at you." Honking at someone who's going slow will be perceived as aggression. People honk maybe once a week.</li>
          <li>• <strong>The rule:</strong> Only honk to prevent an accident or alert someone who's about to do something dangerous. A light tap for "the light turned green" is acceptable after 3-4 seconds. That's it.</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">🍺 DUI / DWI: Don't Even Think About It</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>Legal limit:</strong> 0.08% BAC. That's roughly 2 beers for an average-sized person. After a party, just take an Uber.</li>
          <li>• <strong>The consequences are life-altering:</strong> First DUI = $5,000-10,000 in fines/legal fees, license suspension, possible jail time, insurance doubles for 3-5 years.</li>
          <li>• <strong>For visa holders:</strong> A DUI can trigger deportation proceedings, green card denial, or visa renewal rejection. USCIS treats DUI as a serious negative factor. It's simply not worth the risk.</li>
          <li>• <strong>In India</strong>, drink-driving enforcement is inconsistent. In America, checkpoints are common, especially weekends and holidays. Every police car has a breathalyzer.</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">💳 Tolls, Parking, and the Things Nobody Tells You</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>Toll systems:</strong> Get an E-ZPass (East Coast), FasTrak (California), or TxTag (Texas) immediately. Without one, tolls cost 2-3x more and you'll get bills in the mail weeks later.</li>
          <li>• <strong>Parking tickets are REAL.</strong> In India, you park wherever there's space. In America, wrong parking = $50-100 ticket within minutes. Meter maids are ruthless. Read every parking sign carefully.</li>
          <li>• <strong>Parallel parking:</strong> Your DMV test may include it. Practice in an empty lot. YouTube tutorials are your friend.</li>
          <li>• <strong>Gas stations:</strong> Self-service. You pump your own gas (except in New Jersey and Oregon, where attendants do it by law). Pay at the pump with a card or prepay inside.</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">❄️ Winter Driving (If You're Not in California)</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>Snow and ice driving</strong> is nothing like monsoon driving. Braking distances triple. Get winter tires or all-season tires with the 3-Peak Mountain Snowflake (3PMSF) symbol.</li>
          <li>• <strong>Black ice</strong> is invisible ice on the road. If the road looks wet but it's below freezing, slow down dramatically.</li>
          <li>• <strong>AWD helps.</strong> If you live in the Northeast, Midwest, or Pacific Northwest, consider an AWD vehicle. <Link to="/cars/2026-subaru-outback" className="text-primary hover:underline">Subaru Outback</Link>, <Link to="/cars/2026-toyota-rav4-hybrid" className="text-primary hover:underline">Toyota RAV4 Hybrid</Link>, and <Link to="/cars/2026-hyundai-tucson-hybrid" className="text-primary hover:underline">Hyundai Tucson Hybrid</Link> are popular choices.</li>
          <li>• <strong>Clear your car.</strong> It's illegal (and dangerous) to drive with snow on your roof. Brush off everything before you leave.</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-primary/5 border border-primary/10">
        <h3 className="font-bold text-foreground mb-3">💡 The Three Things That Will Save You</h3>
        <p className="mb-3">If you remember nothing else from this guide, remember these:</p>
        <ul className="space-y-2 ml-4">
          <li>• <strong>1. Stay in your lane.</strong> Literally and figuratively. Lane discipline is the #1 adjustment Indian drivers need to make.</li>
          <li>• <strong>2. Don't honk.</strong> Seriously. Unlearn the horn reflex. Use it only for safety.</li>
          <li>• <strong>3. Never drive after drinking.</strong> The consequences for visa holders are catastrophic. Always Uber. No exceptions.</li>
        </ul>
        <p className="mt-3">Also read: <Link to="/cars/guide/first-car-in-america" className="text-primary hover:underline">Your First Car in America</Link> | <Link to="/cars/guide/insurance-for-new-immigrants" className="text-primary hover:underline">Insurance for New Immigrants</Link></p>
      </section>
    </GuideLayout>
  );
}

/* ================================================================== */

export function TechProfessionalsGuide() {
  return (
    <GuideLayout canonicalPath="/cars/guide/cars-for-tech-professionals" title="Best Cars for Tech Professionals" description="Smart car picks for Bay Area, Seattle, and Austin tech commuters — from entry-level to RSU-fueled upgrades.">
      <section>
        <h2 className="text-xl font-bold text-foreground mb-3">💻 The Indian Tech Worker's Car Journey</h2>
        <p>You arrived on H-1B, bought a Civic, and drove it for three years. Then your RSUs started vesting. Then you noticed every third car in your office parking lot is a Tesla. Here's the practical guide to what you should actually drive at each stage of your tech career in America.</p>
      </section>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">What Tech Commuters Actually Need</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>HOV lane access:</strong> In Bay Area and Seattle, HOV lanes save 20-40 minutes daily. EVs and plug-in hybrids often qualify for solo HOV access with a Clean Air Vehicle sticker.</li>
          <li>• <strong>Workplace charging:</strong> Google, Apple, Meta, Microsoft, Amazon, Salesforce, and most mid-to-large tech companies offer free EV charging. This is a massive perk — $150+/month in free fuel.</li>
          <li>• <strong>Comfort for 30-60 min commutes:</strong> Good seats, a quiet cabin, wireless CarPlay, and adaptive cruise control are non-negotiable for daily highway driving.</li>
          <li>• <strong>Resale value:</strong> If your company does layoffs or you switch to a startup, you might need to sell fast. Toyotas, Teslas, and Lexus hold value best.</li>
          <li>• <strong>Parking:</strong> Tech campus garages are tight. A massive SUV is impractical. Sedans and compact crossovers rule the lot.</li>
        </ul>
      </section>

      <div className="space-y-6">
        <h2 className="text-xl font-bold text-foreground">🏆 The Tech Professional's Car Ladder</h2>

        <div className="p-5 rounded-xl bg-muted/20 border border-border/50">
          <h3 className="font-bold text-foreground mb-3">Level 1: Just Landed (Year 1-2, building credit)</h3>
          <div className="space-y-4 mt-4">
            <Link to="/cars/2026-honda-civic" className="block group">
              <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-background/50 transition-colors">
                <span className="text-lg">🥇</span>
                <div>
                  <h4 className="font-bold text-foreground group-hover:text-primary transition-colors">Honda Civic — $24,950</h4>
                  <p className="text-sm text-foreground/60 mt-1">The official car of "I just got my H-1B stamped." Cheap to insure, cheap to fuel, impossible to kill. You'll see twenty of these in the Apple Park garage. And for good reason.</p>
                </div>
              </div>
            </Link>
            <Link to="/cars/2026-toyota-camry" className="block group">
              <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-background/50 transition-colors">
                <span className="text-lg">🥈</span>
                <div>
                  <h4 className="font-bold text-foreground group-hover:text-primary transition-colors">Toyota Camry Hybrid — $30,450</h4>
                  <p className="text-sm text-foreground/60 mt-1">52 MPG means a Bay Area commute costs about $60/month in fuel. The hybrid battery adds zero maintenance cost. This is the "my parents approve" choice that also happens to be the smartest financial decision.</p>
                </div>
              </div>
            </Link>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-muted/20 border border-border/50">
          <h3 className="font-bold text-foreground mb-3">Level 2: First RSU Vest (Year 2-4, credit established)</h3>
          <div className="space-y-4 mt-4">
            <Link to="/cars/2026-tesla-model-3" className="block group">
              <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-background/50 transition-colors">
                <span className="text-lg">🥇</span>
                <div>
                  <h4 className="font-bold text-foreground group-hover:text-primary transition-colors">Tesla Model 3 — $38,990</h4>
                  <p className="text-sm text-foreground/60 mt-1">The moment your first vest hits, you're going to think about this car. And you should. Free charging at work, HOV lane access, $7,500 tax credit brings it to ~$31,500, and Autopilot handles the 101 crawl. This is the Bay Area default.</p>
                </div>
              </div>
            </Link>
            <Link to="/cars/2026-tesla-model-y" className="block group">
              <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-background/50 transition-colors">
                <span className="text-lg">🥈</span>
                <div>
                  <h4 className="font-bold text-foreground group-hover:text-primary transition-colors">Tesla Model Y — $44,990</h4>
                  <p className="text-sm text-foreground/60 mt-1">Model 3 but with space for a road trip to Yosemite or camping gear to Tahoe. If you got married and a kid is on the way, this is the upgrade path. The 7-seat option means you're covered when parents visit.</p>
                </div>
              </div>
            </Link>
            <Link to="/cars/2026-bmw-3-series" className="block group">
              <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-background/50 transition-colors">
                <span className="text-lg">🥉</span>
                <div>
                  <h4 className="font-bold text-foreground group-hover:text-primary transition-colors">BMW 3 Series — $46,200</h4>
                  <p className="text-sm text-foreground/60 mt-1">The "I want people to notice" choice. The M Sport package looks great in the tech campus parking lot. Be honest with yourself about whether you're buying it for the driving experience or the badge. (Both are valid.)</p>
                </div>
              </div>
            </Link>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-muted/20 border border-border/50">
          <h3 className="font-bold text-foreground mb-3">Level 3: Senior Engineer / Staff+ (Year 5+, money's good)</h3>
          <div className="space-y-4 mt-4">
            <Link to="/cars/2026-lexus-es" className="block group">
              <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-background/50 transition-colors">
                <span className="text-lg">🥇</span>
                <div>
                  <h4 className="font-bold text-foreground group-hover:text-primary transition-colors">Lexus ES Hybrid — $44,970</h4>
                  <p className="text-sm text-foreground/60 mt-1">The wise choice. Toyota reliability in a luxury package. The ES Hybrid is so quiet inside that your conference calls on the commute sound studio-quality. Zero drama, zero maintenance headaches, and the Lexus dealer treats you like royalty.</p>
                </div>
              </div>
            </Link>
            <Link to="/cars/2026-mercedes-benz-e-class" className="block group">
              <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-background/50 transition-colors">
                <span className="text-lg">🥈</span>
                <div>
                  <h4 className="font-bold text-foreground group-hover:text-primary transition-colors">Mercedes-Benz E-Class — $58,850</h4>
                  <p className="text-sm text-foreground/60 mt-1">When the in-laws visit and you pick them up at SFO, the three-pointed star says things you don't have to. The E-Class interior is the best in class. High maintenance costs, but at Staff Engineer salary, $200/month on service isn't moving the needle.</p>
                </div>
              </div>
            </Link>
            <Link to="/cars/2026-porsche-cayenne" className="block group">
              <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-background/50 transition-colors">
                <span className="text-lg">🥉</span>
                <div>
                  <h4 className="font-bold text-foreground group-hover:text-primary transition-colors">Porsche Cayenne — $79,800</h4>
                  <p className="text-sm text-foreground/60 mt-1">The "those RSUs really hit different" car. Drives like a sports car, fits the whole family, and absolutely no one in the Costco parking lot is going to mistake you for a new grad. This is the car Indian dads dream about but would never admit to wanting.</p>
                </div>
              </div>
            </Link>
          </div>
        </div>
      </div>

      <section className="p-5 rounded-xl bg-muted/20 border border-border/50">
        <h3 className="font-bold text-foreground mb-3">What Your Coworkers Are Actually Driving (Bay Area edition)</h3>
        <ul className="space-y-2 ml-4">
          <li>• <strong>Interns / New grads:</strong> Whatever their parents' car is, or a beat-up Corolla</li>
          <li>• <strong>SDE I-II / Junior:</strong> <Link to="/cars/2026-honda-civic" className="text-primary hover:underline">Honda Civic</Link>, <Link to="/cars/2026-toyota-camry" className="text-primary hover:underline">Toyota Camry</Link>, Mazda 3</li>
          <li>• <strong>SDE III / Senior:</strong> <Link to="/cars/2026-tesla-model-3" className="text-primary hover:underline">Tesla Model 3</Link>, <Link to="/cars/2026-bmw-3-series" className="text-primary hover:underline">BMW 3 Series</Link></li>
          <li>• <strong>Staff / Principal:</strong> <Link to="/cars/2026-tesla-model-y" className="text-primary hover:underline">Tesla Model Y</Link>, <Link to="/cars/2026-lexus-rx" className="text-primary hover:underline">Lexus RX</Link>, <Link to="/cars/2026-bmw-x5" className="text-primary hover:underline">BMW X5</Link></li>
          <li>• <strong>Director+:</strong> <Link to="/cars/2026-porsche-cayenne" className="text-primary hover:underline">Porsche Cayenne</Link>, <Link to="/cars/2026-mercedes-benz-gle" className="text-primary hover:underline">Mercedes GLE</Link>, <Link to="/cars/2026-range-rover-sport" className="text-primary hover:underline">Range Rover Sport</Link></li>
          <li>• <strong>VP / C-suite:</strong> You're not reading car guides. You have a person for that.</li>
        </ul>
      </section>

      <section className="p-5 rounded-xl bg-primary/5 border border-primary/10">
        <h3 className="font-bold text-foreground mb-3">💡 The Videshi Recommendation</h3>
        <p className="mb-2"><strong>Best all-around tech commuter:</strong> <Link to="/cars/2026-tesla-model-3" className="text-primary hover:underline">Tesla Model 3</Link>. Free workplace charging + HOV lane + $7,500 credit + Autopilot for highway traffic. The math is simply unbeatable.</p>
        <p className="mb-2"><strong>Best if you want zero drama:</strong> <Link to="/cars/2026-lexus-es" className="text-primary hover:underline">Lexus ES Hybrid</Link>. It just works. Like a Toyota that went to finishing school.</p>
        <p><strong>Real talk:</strong> Don't upgrade your car just because your RSUs vested. The happiest engineers in the Bay Area are the ones driving paid-off Camrys while maxing out their 401(k). The Porsche can wait until you make Staff.</p>
        <p className="mt-3">Related guides: <Link to="/cars/guide/best-evs-2026" className="text-primary hover:underline">Best EVs in 2026</Link> | <Link to="/cars/guide/lease-vs-buy" className="text-primary hover:underline">Lease vs Buy</Link> | <Link to="/cars/guide/best-cars-under-30k" className="text-primary hover:underline">Best Cars Under $30K</Link></p>
      </section>
    </GuideLayout>
  );
}
