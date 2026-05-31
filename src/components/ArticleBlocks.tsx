import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import SocialEmbed from "./SocialEmbed";

type Block =
  | { type: "paragraph"; text?: string; content?: string }
  | { type: "pull_quote"; text?: string; content?: string; attribution?: string }
  | { type: "context_box"; title?: string; text?: string; content?: string; items?: string[] }
  | { type: "nri_angle"; text?: string; content?: string; title?: string }
  | { type: "key_facts"; title?: string; items?: string[]; facts?: string[] }
  | { type: "social_embed"; platform: "instagram" | "twitter"; url: string; caption?: string }
  | { type: string; [k: string]: unknown };

// Convert "• **Label:** text" or "• text" runs into a real markdown list so
// each bullet renders on its own line with spacing.
function bulletsToMarkdown(text: string): string {
  if (!text) return "";
  let t = text.replace(/\r\n/g, "\n");
  // Insert a newline before every • that isn't already at the start of a line
  t = t.replace(/\s*•\s*/g, "\n- ");
  // Trim leading blank line if we created one
  return t.replace(/^\n+/, "").trim();
}

export function tryParseBlocks(body: string): Block[] | null {
  const trimmed = (body ?? "").trim();
  if (!trimmed.startsWith("[")) return null;
  try {
    const parsed = JSON.parse(trimmed);
    if (Array.isArray(parsed)) return parsed as Block[];
    return null;
  } catch {
    return null;
  }
}

function getText(b: any): string {
  return b?.text ?? b?.content ?? "";
}

function getItems(b: any): string[] {
  if (Array.isArray(b?.items)) return b.items;
  if (Array.isArray(b?.facts)) return b.facts;
  return [];
}

export default function ArticleBlocks({ blocks }: { blocks: Block[] }) {
  return (
    <div className="article-prose">
      {blocks.map((block, i) => {
        const b = block as any;
        switch (b.type) {
          case "paragraph":
            return <p key={i}>{getText(b)}</p>;

          case "pull_quote":
            return (
              <blockquote
                key={i}
                className="my-8 border-l-4 border-primary pl-6 py-2 font-serif italic text-xl md:text-2xl text-foreground/90 leading-snug"
              >
                <p className="m-0">"{getText(b)}"</p>
                {b.attribution && (
                  <footer className="mt-3 not-italic text-sm text-muted-foreground font-sans">
                    — {b.attribution}
                  </footer>
                )}
              </blockquote>
            );

          case "context_box": {
            const items = getItems(b);
            return (
              <aside
                key={i}
                className="my-8 bg-secondary/60 border hairline p-6"
              >
                {b.title && (
                  <p className="smallcaps text-primary mb-3">{b.title}</p>
                )}
                {getText(b) && <p className="m-0 text-foreground/85">{getText(b)}</p>}
                {items.length > 0 && (
                  <ul className="mt-3 space-y-1.5 text-foreground/85 list-disc pl-5">
                    {items.map((it, j) => (
                      <li key={j}>{it}</li>
                    ))}
                  </ul>
                )}
              </aside>
            );
          }

          case "nri_angle": {
            const md = bulletsToMarkdown(getText(b));
            return (
              <aside
                key={i}
                className="my-8 border-l-4 border-primary bg-primary/5 p-6"
              >
                <p className="smallcaps text-primary mb-2">
                  {b.title ?? "The NRI Angle"}
                </p>
                <div className="nri-prose text-foreground/90 [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:space-y-3 [&_li]:leading-relaxed [&_p]:m-0 [&_p+ul]:mt-3">
                  <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>{md}</ReactMarkdown>
                </div>
              </aside>
            );
          }

          case "key_facts": {
            const items = getItems(b);
            return (
              <aside
                key={i}
                className="my-8 border hairline p-6 bg-background"
              >
                <p className="smallcaps text-primary mb-3">
                  {b.title ?? "Key Facts"}
                </p>
                <ul className="space-y-2 text-foreground/90 list-disc pl-5">
                  {items.map((it, j) => (
                    <li key={j}>{it}</li>
                  ))}
                </ul>
              </aside>
            );
          }

          case "social_embed":
            return (
              <SocialEmbed
                key={i}
                platform={b.platform}
                url={b.url}
                caption={b.caption}
              />
            );

          default:
            if (getText(b)) return <p key={i}>{getText(b)}</p>;
            return null;
        }
      })}
    </div>
  );
}
