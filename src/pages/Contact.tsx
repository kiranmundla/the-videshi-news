import { useState, type FormEvent } from "react";
import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import SiteFooter from "@/components/SiteFooter";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { toast } from "@/components/ui/sonner";
import { supabase } from "@/integrations/supabase/client";

export default function Contact() {
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const fd = new FormData(form);
    const name = String(fd.get("name") ?? "").trim();
    const email = String(fd.get("email") ?? "").trim();
    const message = String(fd.get("message") ?? "").trim();

    if (!name || !email || !message) {
      toast("Please fill out all fields.");
      return;
    }

    setSubmitting(true);
    try {
      const { error } = await supabase.functions.invoke("send-contact-email", {
        body: { name, email, message },
      });
      if (error) throw error;
      form.reset();
      toast("Thank you, we'll be in touch soon");
    } catch (err) {
      console.error(err);
      toast("Sorry — something went wrong. Please email us directly.");
    } finally {
      setSubmitting(false);
    }
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
            href="mailto:editor@thevideshi.com"
            className="text-primary hover:underline"
          >
            editor@thevideshi.com
          </a>
        </p>

        <form onSubmit={onSubmit} className="mt-10 space-y-4">
          <Input name="name" placeholder="Name" required maxLength={100} />
          <Input name="email" type="email" placeholder="Email" required maxLength={255} />
          <Textarea name="message" placeholder="Message" rows={5} required maxLength={5000} />
          <Button type="submit" disabled={submitting}>
            {submitting ? "Sending…" : "Submit"}
          </Button>
        </form>
      </main>
      <SiteFooter />
    </div>
  );
}
