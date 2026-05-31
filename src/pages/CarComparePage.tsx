import { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { ChevronLeft, Fuel, Users, Package, Shield, ArrowRight } from "lucide-react";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";
import {
  Car,
  getCarsByIds,
  formatMsrp,
  formatPrice,
  brandGradient,
  CATEGORY_ICONS,
} from "@/lib/cars";

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
/* ------------------------------------------------------------------ */

/** Return "best" | "worst" | null for numeric comparison rows */
function rankValue(values: (number | null)[], idx: number, higherIsBetter: boolean): "best" | "worst" | null {
  const nums = values.map((v) => (v != null ? v : null));
  const validNums = nums.filter((n): n is number => n !== null);
  if (validNums.length < 2) return null;
  const val = nums[idx];
  if (val === null) return null;
  const best = higherIsBetter ? Math.max(...validNums) : Math.min(...validNums);
  const worst = higherIsBetter ? Math.min(...validNums) : Math.max(...validNums);
  if (val === best) return "best";
  if (val === worst && validNums.length > 2) return "worst";
  return null;
}

function rankClass(rank: "best" | "worst" | null): string {
  if (rank === "best") return "text-green-400 font-bold";
  if (rank === "worst") return "text-foreground/40";
  return "";
}

/* ------------------------------------------------------------------ */
/* Spec Row                                                           */
/* ------------------------------------------------------------------ */
function SpecRow({
  label,
  icon,
  values,
  higherIsBetter,
  format = (v) => (v != null ? String(v) : "—"),
}: {
  label: string;
  icon: React.ReactNode;
  values: (number | string | null)[];
  higherIsBetter?: boolean;
  format?: (v: any) => string;
}) {
  return (
    <tr className="border-t border-border/50">
      <td className="sticky left-0 bg-background z-10 p-3 text-sm text-foreground/60 font-medium whitespace-nowrap">
        <div className="flex items-center gap-2">
          {icon}
          {label}
        </div>
      </td>
      {values.map((val, i) => {
        const numVal = typeof val === "number" ? val : null;
        const rank =
          higherIsBetter !== undefined && numVal !== null
            ? rankValue(
                values.map((v) => (typeof v === "number" ? v : null)),
                i,
                higherIsBetter
              )
            : null;
        return (
          <td key={i} className={`p-3 text-sm text-center ${rankClass(rank)}`}>
            {format(val)}
          </td>
        );
      })}
    </tr>
  );
}

/* ------------------------------------------------------------------ */
/* Main Page                                                          */
/* ------------------------------------------------------------------ */
export default function CarComparePage() {
  const [searchParams] = useSearchParams();
  const [cars, setCars] = useState<Car[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const idsParam = searchParams.get("ids");
    if (!idsParam) {
      setLoading(false);
      return;
    }
    const ids = idsParam.split(",").filter(Boolean).slice(0, 3);
    if (ids.length === 0) {
      setLoading(false);
      return;
    }
    setLoading(true);
    getCarsByIds(ids)
      .then((data) => {
        // Maintain URL order
        const map = new Map(data.map((c) => [c.id, c]));
        setCars(ids.map((id) => map.get(id)).filter(Boolean) as Car[]);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [searchParams]);

  if (loading) {
    return (
      <>
        <Masthead />
        <CategoryPills />
        <div className="flex items-center justify-center py-32">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
        </div>
        <SiteFooter />
      </>
    );
  }

  if (cars.length < 2) {
    return (
      <>
        <Masthead />
        <CategoryPills />
        <main className="container py-20 text-center">
          <p className="text-5xl mb-4">📊</p>
          <h1 className="text-2xl font-bold mb-2">Select at least 2 cars to compare</h1>
          <p className="text-foreground/50 mb-6">
            Go back to the Cars page and use the + button on car cards to add them.
          </p>
          <Link to="/cars" className="text-primary hover:underline inline-flex items-center gap-1">
            <ChevronLeft className="h-4 w-4" /> Back to Cars
          </Link>
        </main>
        <SiteFooter />
      </>
    );
  }

  return (
    <>
      <Helmet>
        <title>{cars.map((c) => c.name).join(" vs ")} — Compare | The Videshi</title>
        <meta
          name="description"
          content={`Compare ${cars.map((c) => c.name).join(", ")} — side-by-side specs, pricing, lease deals, and NRI take.`}
        />
              <link rel="canonical" href="https://www.thevideshi.com/cars/compare" />
      </Helmet>
      <Masthead />
      <CategoryPills />

      <main className="container py-8 max-w-5xl mx-auto">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-foreground/50 mb-6">
          <Link to="/cars" className="hover:text-primary transition-colors flex items-center gap-1">
            <ChevronLeft className="h-4 w-4" />
            Cars
          </Link>
          <span>/</span>
          <span className="text-foreground/70">Compare</span>
        </nav>

        <h1 className="font-serif text-2xl md:text-3xl font-bold mb-2">
          {cars.map((c) => c.name).join(" vs ")}
        </h1>
        <p className="text-foreground/50 mb-8">Side-by-side comparison of specs, pricing, and lease deals</p>

        {/* Comparison table */}
        <div className="border border-border rounded-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[500px]">
              {/* Car headers */}
              <thead>
                <tr className="bg-muted/30">
                  <th className="sticky left-0 bg-muted/30 z-10 p-4 w-[160px]" />
                  {cars.map((car) => {
                    const grad = brandGradient(car.brand);
                    return (
                      <th key={car.id} className="p-4 text-center">
                        <Link to={`/cars/${car.slug}`} className="block group">
                          <div className={`h-32 rounded-xl bg-gradient-to-br ${grad} flex items-center justify-center overflow-hidden mx-auto max-w-[200px] mb-3`}>
                            {car.image_url ? (
                              <img src={car.image_url} alt={car.name} className="w-full h-full object-contain p-2" loading="lazy" />
                            ) : (
                              <span className="text-foreground/40 text-sm font-bold">{car.brand}</span>
                            )}
                          </div>
                          <h2 className="font-semibold text-sm group-hover:text-primary transition-colors">
                            {car.name}
                          </h2>
                          <p className="text-xs text-foreground/50 mt-0.5">
                            {CATEGORY_ICONS[car.category]} {car.category} · {car.year}
                          </p>
                        </Link>
                      </th>
                    );
                  })}
                </tr>
              </thead>

              <tbody>
                {/* Price */}
                <SpecRow
                  label="MSRP"
                  icon={<span className="text-sm">💰</span>}
                  values={cars.map((c) => c.msrp_low)}
                  higherIsBetter={false}
                  format={(v) => (v ? formatPrice(v) : "TBD")}
                />
                <SpecRow
                  label="MSRP (High)"
                  icon={<span className="text-sm">💰</span>}
                  values={cars.map((c) => c.msrp_high)}
                  higherIsBetter={false}
                  format={(v) => (v ? formatPrice(v) : "—")}
                />

                {/* Fuel */}
                <SpecRow
                  label="Fuel Type"
                  icon={<Fuel className="h-4 w-4" />}
                  values={cars.map((c) => c.fuel_type)}
                  format={(v) => v ?? "—"}
                />
                <SpecRow
                  label="MPG / Range"
                  icon={<Fuel className="h-4 w-4" />}
                  values={cars.map((c) => c.mpg)}
                  format={(v) => v ?? "—"}
                />

                {/* Seating & Cargo */}
                <SpecRow
                  label="Seating"
                  icon={<Users className="h-4 w-4" />}
                  values={cars.map((c) => c.seating)}
                  higherIsBetter={true}
                  format={(v) => (v ? `${v} passengers` : "—")}
                />
                <SpecRow
                  label="Cargo"
                  icon={<Package className="h-4 w-4" />}
                  values={cars.map((c) => c.cargo_cu_ft)}
                  higherIsBetter={true}
                  format={(v) => (v ? `${v} cu ft` : "—")}
                />

                {/* Safety */}
                <SpecRow
                  label="Safety"
                  icon={<Shield className="h-4 w-4" />}
                  values={cars.map((c) => c.safety_rating)}
                  format={(v) => v ?? "—"}
                />

                {/* Body Type */}
                <SpecRow
                  label="Body Type"
                  icon={<span className="text-sm">🚗</span>}
                  values={cars.map((c) => c.body_type)}
                  format={(v) => v ?? "—"}
                />

                {/* Lease deal */}
                <tr className="border-t-2 border-primary/20">
                  <td className="sticky left-0 bg-background z-10 p-3 text-sm font-bold text-primary whitespace-nowrap" colSpan={1 + cars.length}>
                    Lease Deals
                  </td>
                </tr>
                <SpecRow
                  label="Monthly"
                  icon={<span className="text-sm">📋</span>}
                  values={cars.map((c) => c.lease_monthly)}
                  higherIsBetter={false}
                  format={(v) => (v ? `${formatPrice(v)}/mo` : "No deal")}
                />
                <SpecRow
                  label="Due at Signing"
                  icon={<span className="text-sm">💳</span>}
                  values={cars.map((c) => c.lease_due_at_signing)}
                  higherIsBetter={false}
                  format={(v) => (v ? formatPrice(v) : "—")}
                />

                {/* NRI Take */}
                <tr className="border-t-2 border-primary/20">
                  <td className="sticky left-0 bg-background z-10 p-3 text-sm font-bold text-primary whitespace-nowrap" colSpan={1 + cars.length}>
                    🇮🇳 The NRI Take
                  </td>
                </tr>
                <tr className="border-t border-border/50">
                  <td className="sticky left-0 bg-background z-10 p-3" />
                  {cars.map((car) => (
                    <td key={car.id} className="p-4 text-sm text-foreground/70 align-top">
                      {car.nri_take || <span className="text-foreground/30 italic">No NRI take yet</span>}
                    </td>
                  ))}
                </tr>

                {/* Pros & Cons */}
                <tr className="border-t-2 border-primary/20">
                  <td className="sticky left-0 bg-background z-10 p-3 text-sm font-bold text-green-400 whitespace-nowrap" colSpan={1 + cars.length}>
                    ✅ Pros
                  </td>
                </tr>
                <tr className="border-t border-border/50">
                  <td className="sticky left-0 bg-background z-10 p-3" />
                  {cars.map((car) => (
                    <td key={car.id} className="p-4 align-top">
                      {car.pros?.length ? (
                        <ul className="space-y-1.5">
                          {car.pros.map((p, i) => (
                            <li key={i} className="text-xs text-foreground/70 flex items-start gap-1.5">
                              <span className="text-green-400 mt-0.5">✓</span> {p}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <span className="text-xs text-foreground/30 italic">—</span>
                      )}
                    </td>
                  ))}
                </tr>
                <tr className="border-t-2 border-primary/20">
                  <td className="sticky left-0 bg-background z-10 p-3 text-sm font-bold text-red-400 whitespace-nowrap" colSpan={1 + cars.length}>
                    ❌ Cons
                  </td>
                </tr>
                <tr className="border-t border-border/50">
                  <td className="sticky left-0 bg-background z-10 p-3" />
                  {cars.map((car) => (
                    <td key={car.id} className="p-4 align-top">
                      {car.cons?.length ? (
                        <ul className="space-y-1.5">
                          {car.cons.map((c, i) => (
                            <li key={i} className="text-xs text-foreground/70 flex items-start gap-1.5">
                              <span className="text-red-400 mt-0.5">✗</span> {c}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <span className="text-xs text-foreground/30 italic">—</span>
                      )}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* View individual pages */}
        <div className="mt-8 flex flex-wrap gap-3">
          {cars.map((car) => (
            <Link
              key={car.id}
              to={`/cars/${car.slug}`}
              className="flex items-center gap-2 px-4 py-2 bg-card border border-border rounded-lg hover:border-primary/40 transition-colors text-sm font-medium group"
            >
              {car.name}
              <ArrowRight className="h-3.5 w-3.5 text-foreground/30 group-hover:text-primary transition-colors" />
            </Link>
          ))}
        </div>

        <div className="mt-6">
          <Link to="/cars" className="text-sm text-primary hover:underline inline-flex items-center gap-1">
            <ChevronLeft className="h-4 w-4" /> Back to all cars
          </Link>
        </div>
      </main>

      <SiteFooter />
    </>
  );
}
