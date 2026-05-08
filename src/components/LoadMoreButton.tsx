import { Loader2, ArrowDown } from "lucide-react";

type Props = {
  onClick: () => void;
  loading?: boolean;
  hasMore: boolean;
  label?: string;
  doneLabel?: string;
  className?: string;
};

export default function LoadMoreButton({
  onClick,
  loading = false,
  hasMore,
  label = "Load More Stories",
  doneLabel = "You're all caught up ✓",
  className = "",
}: Props) {
  if (!hasMore) {
    return (
      <p className={`smallcaps text-center text-muted-foreground py-8 ${className}`}>
        {doneLabel}
      </p>
    );
  }
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className={`w-full flex items-center justify-center gap-2 smallcaps py-4 mt-12 bg-muted/40 hover:bg-muted border border-rule rounded-md text-foreground/80 hover:text-foreground transition-colors disabled:opacity-60 ${className}`}
    >
      {loading ? (
        <>
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading…
        </>
      ) : (
        <>
          {label}
          <ArrowDown className="h-4 w-4" />
        </>
      )}
    </button>
  );
}
