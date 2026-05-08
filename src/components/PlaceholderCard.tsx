type Variant = "hero" | "featured" | "card" | "long" | "compact";

export default function PlaceholderCard({ variant = "card" }: { variant?: Variant }) {
  if (variant === "compact") {
    return (
      <div className="flex gap-4 items-start opacity-70">
        <div className="w-20 h-20 bg-muted flex-shrink-0" />
        <div className="min-w-0">
          <p className="smallcaps text-primary mb-1">Coming soon</p>
          <h3 className="font-serif text-[0.95rem] md:text-base leading-snug text-muted-foreground">
            More reporting on the way
          </h3>
        </div>
      </div>
    );
  }

  if (variant === "long") {
    return (
      <div className="grid md:grid-cols-2 gap-6 md:gap-10 items-center bg-secondary/60 p-6 md:p-10 border hairline opacity-80">
        <div className="w-full aspect-[4/3] bg-muted" />
        <div>
          <p className="smallcaps text-primary mb-3">Long read · Coming soon</p>
          <h2 className="font-serif text-2xl md:text-4xl leading-[1.15] text-muted-foreground">
            A long read is on the way
          </h2>
          <p className="mt-4 text-muted-foreground leading-relaxed text-[0.98rem]">
            Check back shortly for in-depth diaspora reporting.
          </p>
        </div>
      </div>
    );
  }

  const headlineSize =
    variant === "hero"
      ? "text-[2rem] md:text-[2.75rem] lg:text-[3rem] leading-[1.05]"
      : variant === "featured"
        ? "text-[1.35rem] md:text-[1.5rem] leading-[1.2]"
        : "text-[1.05rem] md:text-[1.125rem] leading-snug";

  const aspect = "aspect-[16/9]";

  return (
    <div className="block opacity-80">
      <div className={`w-full ${aspect} bg-muted overflow-hidden flex items-center justify-center`}>
        <span className="smallcaps text-muted-foreground text-xs">Coming soon</span>
      </div>
      <p className="smallcaps text-primary mt-4 mb-2">Coming soon</p>
      <h2 className={`font-serif text-muted-foreground ${headlineSize}`}>
        More stories coming soon
      </h2>
      <p className="mt-3 text-muted-foreground leading-relaxed text-[0.95rem] md:text-base">
        New reporting from across the diaspora is on its way.
      </p>
    </div>
  );
}
