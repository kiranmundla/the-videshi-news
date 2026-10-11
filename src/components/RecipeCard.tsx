/**
 * RecipeCard — The Videshi's recipe card for food articles.
 * Shows ingredients, numbered steps, time/servings, and optional nutrition.
 * Used for recipes, diet plans, and food brand stories.
 *
 * Data comes from article.data_cards[] entries with type: "recipe".
 * Shape:
 * {
 *   type: "recipe",
 *   title: "Shahi Paneer",
 *   ingredients: ["250g paneer, cubed", "2 onions, finely chopped", ...],
 *   steps: ["Heat ghee in a pan...", "Add onions and sauté until golden...", ...],
 *   prep_time: "15 min",      // optional
 *   cook_time: "25 min",      // optional
 *   servings: "4",            // optional
 *   nutrition: [              // optional
 *     { label: "Calories", value: "320 kcal" },
 *     { label: "Protein", value: "14g" }
 *   ]
 * }
 *
 * Rules: sourced data only — never invent ingredients, times, or nutrition.
 * Returns null on missing/invalid data.
 */

export interface RecipeNutrition {
  label: string;
  value: string;
}

export interface RecipeCardData {
  type?: string;
  title?: string;
  ingredients?: string[];
  steps?: string[];
  prep_time?: string;
  cook_time?: string;
  servings?: string;
  nutrition?: RecipeNutrition[];
}

const NAVY = "#0B1D3A";
const GOLD = "#D4A843";

export default function RecipeCard({ card }: { card: RecipeCardData }) {
  if (
    !card ||
    !Array.isArray(card.ingredients) ||
    card.ingredients.length === 0 ||
    !Array.isArray(card.steps) ||
    card.steps.length === 0
  )
    return null;

  const meta: string[] = [];
  if (card.prep_time) meta.push(`Prep: ${card.prep_time}`);
  if (card.cook_time) meta.push(`Cook: ${card.cook_time}`);
  if (card.servings) meta.push(`Serves: ${card.servings}`);

  const nutrition = (card.nutrition ?? []).filter(
    (n) => n && n.label && n.value
  );

  return (
    <div
      data-testid="recipe-card"
      style={{
        margin: "0 0 28px",
        borderRadius: 14,
        overflow: "hidden",
        border: `1px solid hsl(var(--rule))`,
        background: "hsl(var(--card))",
      }}
    >
      {/* Header bar */}
      <div
        style={{
          background: NAVY,
          color: "#fff",
          padding: "10px 18px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
          flexWrap: "wrap",
        }}
      >
        <span
          style={{
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
          }}
        >
          🍳 Recipe{card.title ? `: ${card.title}` : ""}
        </span>
        {meta.length > 0 && (
          <span
            style={{
              fontSize: 11.5,
              color: "rgba(255,255,255,0.75)",
              lineHeight: 1.4,
            }}
          >
            {meta.join("  •  ")}
          </span>
        )}
      </div>

      {/* Ingredients */}
      <div style={{ padding: "16px 18px 4px" }}>
        <div
          style={{
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: "0.07em",
            textTransform: "uppercase",
            color: "hsl(var(--muted-foreground))",
            marginBottom: 10,
          }}
        >
          Ingredients
        </div>
        <ul
          style={{
            margin: 0,
            padding: 0,
            listStyle: "none",
          }}
        >
          {card.ingredients.map((ing, i) => (
            <li
              key={i}
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: 10,
                padding: "5px 0",
                fontSize: 13.5,
                color: "hsl(var(--foreground))",
                lineHeight: 1.5,
                borderBottom:
                  i < card.ingredients!.length - 1
                    ? "1px solid hsl(var(--rule) / 0.5)"
                    : "none",
              }}
            >
              <span
                aria-hidden
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: "50%",
                  background: GOLD,
                  marginTop: 7,
                  flexShrink: 0,
                }}
              />
              {ing}
            </li>
          ))}
        </ul>
      </div>

      {/* Steps */}
      <div style={{ padding: "12px 18px 4px" }}>
        <div
          style={{
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: "0.07em",
            textTransform: "uppercase",
            color: "hsl(var(--muted-foreground))",
            marginBottom: 10,
          }}
        >
          Method
        </div>
        <ol style={{ margin: 0, padding: 0, listStyle: "none" }}>
          {card.steps.map((step, i) => (
            <li
              key={i}
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: 12,
                padding: "8px 0",
              }}
            >
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  width: 26,
                  height: 26,
                  borderRadius: "50%",
                  background: NAVY,
                  color: "#fff",
                  fontSize: 12.5,
                  fontWeight: 800,
                  flexShrink: 0,
                  marginTop: 1,
                }}
              >
                {i + 1}
              </span>
              <span
                style={{
                  fontSize: 13.5,
                  color: "hsl(var(--foreground))",
                  lineHeight: 1.55,
                }}
              >
                {step}
              </span>
            </li>
          ))}
        </ol>
      </div>

      {/* Nutrition */}
      {nutrition.length > 0 && (
        <div
          style={{
            margin: "12px 18px 18px",
            borderRadius: 10,
            border: `1px solid ${GOLD}55`,
            background: `${GOLD}0f`,
            overflow: "hidden",
          }}
        >
          <div
            style={{
              fontSize: 11,
              fontWeight: 700,
              letterSpacing: "0.07em",
              textTransform: "uppercase",
              color: NAVY,
              padding: "10px 14px 4px",
            }}
          >
            Nutrition (per serving)
          </div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))",
              gap: 0,
              padding: "6px 14px 12px",
            }}
          >
            {nutrition.map((n, i) => (
              <div key={i} style={{ padding: "6px 4px" }}>
                <div
                  style={{
                    fontSize: 11,
                    color: "hsl(var(--muted-foreground))",
                    fontWeight: 600,
                  }}
                >
                  {n.label}
                </div>
                <div
                  style={{
                    fontSize: 14.5,
                    fontWeight: 800,
                    color: NAVY,
                    fontVariantNumeric: "tabular-nums",
                  }}
                >
                  {n.value}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
