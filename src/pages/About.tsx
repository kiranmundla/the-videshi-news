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
          content="The Videshi is an independent news platform serving the global Indian diaspora."
        />
      </Helmet>
      <Masthead />
      <main className="container max-w-2xl py-16">
        <h1 className="font-serif text-4xl font-bold mb-6">About</h1>
        <p className="text-foreground/80 leading-relaxed text-lg">
          The Videshi is an independent news platform serving the global Indian
          diaspora. We aggregate, synthesize and contextualize news from India
          with a focus on what matters to Indian-Americans — from politics and
          business to culture and community. Our name means "the foreigner" in
          Hindi — a nod to the diaspora experience of living between two worlds.
        </p>
      </main>
      <SiteFooter />
    </div>
  );
}
