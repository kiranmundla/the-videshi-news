type Props = {
  onClick: () => void;
  loading: boolean;
  hasMore: boolean;
};

export default function MoreStoriesButton({ onClick, loading, hasMore }: Props) {
  if (!hasMore) return null;
  return (
    <div className="flex justify-center mt-8">
      <button
        type="button"
        onClick={onClick}
        disabled={loading}
        className="inline-flex items-center justify-center gap-2 transition-colors disabled:cursor-not-allowed"
        style={{
          border: "1px solid #ccc",
          background: "transparent",
          color: "#666",
          fontSize: 13,
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          padding: "10px 32px",
          borderRadius: 2,
          fontWeight: 600,
        }}
        onMouseEnter={(e) => {
          if (!loading) (e.currentTarget.style.background = "#f5f5f5");
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = "transparent";
        }}
      >
        {loading ? (
          <>
            <span
              aria-hidden
              className="inline-block h-3 w-3 rounded-full border-2 border-current border-t-transparent animate-spin"
            />
            Loading...
          </>
        ) : (
          "More Stories"
        )}
      </button>
    </div>
  );
}
