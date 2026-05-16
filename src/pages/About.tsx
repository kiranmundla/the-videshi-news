import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";

export default function About() {
  return (
    <div className="min-h-screen bg-background">
      <Helmet>
        <title>About · The Videshi</title>
        <meta
          name="description"
          content="The Videshi is an independent news platform serving the global Indian diaspora with original reporting and analysis."
        />
      </Helmet>
      <Masthead />
      <main className="container max-w-2xl py-16">
        <h1 className="font-serif text-4xl font-bold mb-8">About The Videshi</h1>

        <div className="space-y-6 text-foreground/80 leading-relaxed text-[1.05rem]">
          <p>
            <strong className="text-foreground">The Videshi</strong> is an independent news platform built for the global Indian diaspora. We cover the stories that matter to Indians living abroad — from policy shifts in New Delhi to immigration debates in Washington, from IPL scores to market movements across Mumbai and Wall Street.
          </p>

          <p>
            Our name means <em>"the foreigner"</em> in Hindi — a word every member of the diaspora has felt at one point or another, whether in the country they left or the one they chose. We wear it as a badge.
          </p>

          <h2 className="font-serif text-2xl font-bold text-foreground pt-4">What We Do</h2>
          <p>
            We aggregate news from dozens of sources, synthesize it with original context, and publish stories written with the diaspora reader in mind. Every article carries an NRI angle — not as an afterthought, but as the lens through which the story is told. Our coverage spans India, NRI affairs, global politics, markets &amp; finance, technology, sports, entertainment, travel, and food.
          </p>

          <h2 className="font-serif text-2xl font-bold text-foreground pt-4">Editorial Standards</h2>
          <p>
            We are committed to accuracy, fairness, and independence. Our reporting draws from verified sources and established news agencies. We do not publish opinion as news. When we get something wrong, we correct it promptly and transparently.
          </p>

          <h2 className="font-serif text-2xl font-bold text-foreground pt-4">Technology</h2>
          <p>
            The Videshi is built with modern technology at its core. We use AI-assisted tools to monitor global news sources, identify stories relevant to the diaspora, and accelerate our editorial workflow. Every article is reviewed for quality, accuracy, and editorial judgment. Technology helps us move faster — it does not replace the editorial voice.
          </p>

          <h2 className="font-serif text-2xl font-bold text-foreground pt-4">Contact</h2>
          <p>
            For editorial inquiries, story tips, corrections, or partnership opportunities:
          </p>
          <p>
            <a
              href="mailto:editor@thevideshi.com"
              className="text-primary hover:underline font-medium"
            >
              editor@thevideshi.com
            </a>
          </p>

          <div className="border-t pt-6 mt-8 text-sm text-muted-foreground">
            <p>© {new Date().getFullYear()} The Videshi. All rights reserved.</p>
            <p className="mt-1">Based in the United States. Serving the diaspora worldwide.</p>
          </div>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
