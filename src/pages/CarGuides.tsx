import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";

function GuideLayout({ title, description, children }: { title: string; description: string; children: React.ReactNode }) {
  return (
    <>
      <Helmet>
        <title>{title} | Cars — The Videshi</title>
        <meta name="description" content={description} />
        <meta property="og:title" content={`${title} | The Videshi`} />
        <meta property="og:description" content={description} />
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
    <GuideLayout title="Your First Car in America" description="Step-by-step guide for H-1B and L-1 visa holders buying their first car in the US.">
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
    <GuideLayout title="Lease vs Buy" description="Should you lease or buy your next car? A practical comparison for the Indian mindset.">
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
    <GuideLayout title="Car Insurance for New Immigrants" description="How to get car insurance in the US with no American driving history. A guide for new Indian immigrants.">
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
    <GuideLayout title="Best Family SUVs for Indian Families" description="Top 3-row SUVs ranked for desi families — space, safety, value, and road trip readiness.">
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
