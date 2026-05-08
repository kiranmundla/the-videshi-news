import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import ReactMarkdown from "react-markdown";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";
import ArticleCard from "@/components/ArticleCard";
import SectionRule from "@/components/SectionRule";
import {
  Article,
  formatLongDate,
  getArticleBySlug,
  getRelatedArticles,
  readingTime,
} from "@/lib/articles";
import HeroImage from "@/components/HeroImage";
import ImageCaption from "@/components/ImageCaption";
import ArticleBlocks, { tryParseBlocks } from "@/components/ArticleBlocks";

export default function ArticlePage() {
  const { slug = "" } = useParams();
  const [article, setArticle] = useState<Article | null | undefined>(undefined);
  const [related, setRelated] = useState<Article[]>([]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const a = await getArticleBySlug(slug);
      if (cancelled) return;
      setArticle(a ?? null);
      if (a) setRelated(await getRelatedArticles(a.slug, a.category, 3));
      window.scrollTo(0, 0);
    })();
    return () => {
      cancelled = true;
    };
  }, [slug]);

  if (article === undefined) {
    return (
      <div className="min-h-screen">
        <Masthead />
        <main className="container py-20 text-center text-muted-foreground">Loading…</main>
      </div>
    );
  }

  if (article === null) {
    return (
      <div className="min-h-screen flex flex-col">
        <Masthead />
        <main className="container py-24 text-center flex-1">
          <p className="smallcaps text-primary">404</p>
          <h1 className="font-serif text-4xl mt-3">Article not found</h1>
          <Link to="/" className="inline-block mt-6 text-primary underline underline-offset-4">
            Back to homepage
          </Link>
        </main>
        <SiteFooter />
      </div>
    );
  }

  const time = readingTime(article.body);

  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>{article.title} — The Videshi</title>
        <meta name="description" content={article.excerpt} />
        <meta property="og:title" content={article.title} />
        <meta property="og:description" content={article.excerpt} />
        <meta property="og:type" content="article" />
        <meta property="og:image" content={article.hero_image_url} />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={article.title} />
        <meta name="twitter:description" content={article.excerpt} />
        <meta name="twitter:image" content={article.hero_image_url} />
        <link rel="canonical" href={`/articles/${article.slug}`} />
      </Helmet>

      <Masthead />

      <main className="container flex-1 pt-8 md:pt-12">
        <article className="max-w-3xl mx-auto">
          <p className="smallcaps text-primary">{article.category}</p>
          <h1 className="font-serif text-[2rem] md:text-5xl lg:text-[3.5rem] leading-[1.08] mt-3 font-bold">
            {article.title}
          </h1>
          <p className="mt-5 text-lg md:text-xl text-foreground/75 font-serif italic leading-relaxed">
            {article.excerpt}
          </p>
          <div className="mt-6 flex flex-wrap gap-x-2 gap-y-1 text-xs text-muted-foreground">
            {article.author && (
              <>
                <span>By {article.author}</span>
                <span>·</span>
              </>
            )}
            <span>{formatLongDate(article.published_at)}</span>
            <span>·</span>
            <span>{time} min read</span>
          </div>
        </article>

        <figure className="mt-10 w-full max-w-full md:max-w-[780px] md:mx-auto">
          <div className="w-full max-w-full aspect-[16/9] overflow-hidden relative">
            <HeroImage
              src={article.hero_image_url}
              alt={article.title}
              loading="eager"
              category={article.category}
              className="block w-full h-full object-cover object-center"
            />
          </div>
          <div className="text-center">
            <ImageCaption
              caption={article.image_caption}
              credit={article.image_credit}
              size="md"
              align="center"
            />
          </div>
        </figure>

        <div className="article-prose max-w-2xl mx-auto mt-12">
          {(() => {
            const blocks = tryParseBlocks(article.body);
            if (blocks) return <ArticleBlocks blocks={blocks} />;
            return (
              <ReactMarkdown
                components={{
                  h1: () => null,
                  a: ({ href, children, ...props }) => {
                    const arr = Array.isArray(children) ? children : [children];
                    const onlyImage =
                      arr.filter((c) => typeof c !== "string" || c.trim() !== "").length === 1 &&
                      arr.some(
                        (c: any) => c && typeof c === "object" && (c.type === "img" || c.props?.node?.tagName === "img")
                      );
                    if (onlyImage) return <>{children}</>;
                    return (
                      <a href={href} {...props}>
                        {children}
                      </a>
                    );
                  },
                  img: ({ src, alt }) => {
                    const norm = (u?: string) => (u ?? "").replace(/&amp;/g, "&").split("?")[0];
                    if (!src) return null;
                    if (/counter\.theconversation\.com|\/count\.gif|pixel|tracker/i.test(src)) {
                      return (
                        <img
                          src={src}
                          alt=""
                          width={1}
                          height={1}
                          aria-hidden="true"
                          referrerPolicy="no-referrer"
                          style={{ position: "absolute", width: 1, height: 1, opacity: 0, pointerEvents: "none", margin: 0 }}
                        />
                      );
                    }
                    if (article.hero_image_url && norm(src) === norm(article.hero_image_url)) {
                      return null;
                    }
                    return <img src={src} alt={alt || article.title} loading="lazy" referrerPolicy="no-referrer" />;
                  },
                }}
              >
                {article.body}
              </ReactMarkdown>
            );
          })()}
        </div>

        {article.sources && article.sources.length > 0 && (
          <aside className="max-w-2xl mx-auto mt-10 pt-6 border-t hairline">
            <p className="smallcaps text-muted-foreground mb-3">Sources & attribution</p>
            <ul className="text-sm text-muted-foreground space-y-1.5">
              {article.sources.map((s, i) => (
                <li key={i}>
                  {s.url ? (
                    <a href={s.url} className="underline underline-offset-2 hover:text-primary">
                      {s.label}
                    </a>
                  ) : (
                    s.label
                  )}
                </li>
              ))}
            </ul>
          </aside>
        )}

        {related.length > 0 && (
          <section className="mt-8">
            <SectionRule label="Read More" />
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 md:gap-10">
              {related.map((a) => (
                <ArticleCard key={a.id} article={a} variant="card" />
              ))}
            </div>
          </section>
        )}
      </main>

      <SiteFooter />
    </div>
  );
}
