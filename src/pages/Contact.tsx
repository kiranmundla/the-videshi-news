import { useState, type FormEvent } from "react";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { toast } from "@/components/ui/sonner";

export default function Contact() {
  const [submitting, setSubmitting] = useState(false);

  function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSubmitting(true);
    setTimeout(() => {
      setSubmitting(false);
      (e.target as HTMLFormElement).reset();
      toast("Thanks — we'll be in touch.");
    }, 400);
  }

  return (
    <div className="min-h-screen bg-background">
      <Helmet>
        <title>Contact · The Videshi</title>
        <meta name="description" content="Get in touch with The Videshi." />
      </Helmet>
      <Masthead />
      <main className="container max-w-xl py-16">
        <h1 className="font-serif text-4xl font-bold mb-4">Get In Touch</h1>
        <p className="text-foreground/80 leading-relaxed">
          For editorial inquiries, story tips, or partnership opportunities,
          reach us at:
        </p>
        <p className="mt-2">
          <a
            href="mailto:hello@thevideshi.com"
            className="text-primary hover:underline"
          >
            hello@thevideshi.com
          </a>
        </p>

        <form onSubmit={onSubmit} className="mt-10 space-y-4">
          <Input name="name" placeholder="Name" required />
          <Input name="email" type="email" placeholder="Email" required />
          <Textarea name="message" placeholder="Message" rows={5} required />
          <Button type="submit" disabled={submitting}>
            {submitting ? "Sending…" : "Submit"}
          </Button>
        </form>
      </main>
      <SiteFooter />
    </div>
  );
}
