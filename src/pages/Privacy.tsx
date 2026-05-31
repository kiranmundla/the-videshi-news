import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";

export default function Privacy() {
  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>Privacy Policy — The Videshi</title>
        <meta name="description" content="Privacy Policy for The Videshi — how we collect, use, and protect your information." />
              <link rel="canonical" href="https://www.thevideshi.com/privacy" />
      </Helmet>
      <Masthead />
      <CategoryPills />
      <main className="container flex-1 py-8 max-w-3xl mx-auto">
        <h1 className="font-serif text-3xl md:text-4xl font-bold mb-2">Privacy Policy</h1>
        <p className="text-sm text-muted-foreground mb-8">Last updated: May 16, 2026</p>

        <div className="prose prose-stone max-w-none space-y-6 text-[0.95rem] leading-relaxed">
          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">1. Introduction</h2>
            <p>
              The Videshi ("we," "us," or "our") operates thevideshi.com (the "Site"). This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">2. Information We Collect</h2>
            <p><strong>Information you provide:</strong></p>
            <ul className="list-disc pl-5 space-y-1">
              <li>Email address when subscribing to our newsletter</li>
              <li>Information submitted through our contact form (name, email, message)</li>
            </ul>
            <p className="mt-3"><strong>Information collected automatically:</strong></p>
            <ul className="list-disc pl-5 space-y-1">
              <li>Device and browser type</li>
              <li>IP address and approximate geographic location</li>
              <li>Pages visited and time spent on the Site</li>
              <li>Referring URL and search terms</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">3. How We Use Your Information</h2>
            <p>We use the information we collect to:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li>Deliver and improve our news content and services</li>
              <li>Send newsletter emails to subscribers</li>
              <li>Respond to inquiries and support requests</li>
              <li>Analyze website traffic and usage patterns</li>
              <li>Comply with legal obligations</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">4. Cookies & Tracking</h2>
            <p>
              We use essential cookies to ensure the proper functioning of our website. We may also use analytics tools (such as Google Analytics) to understand how visitors interact with our Site. These tools may place cookies on your device. You can control cookie preferences through your browser settings.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">5. Third-Party Services</h2>
            <p>We may use third-party services that collect, monitor, and analyze data, including:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li><strong>Supabase</strong> — database hosting and authentication</li>
              <li><strong>Vercel</strong> — website hosting and delivery</li>
              <li><strong>Google Analytics</strong> — website analytics (if enabled)</li>
              <li><strong>Google AdSense</strong> — advertising (if enabled)</li>
            </ul>
            <p className="mt-2">
              Each of these services has its own privacy policy governing the data they collect.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">6. Data Sharing & Disclosure</h2>
            <p>We do not sell, trade, or rent your personal information. We may share information in the following circumstances:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li>With service providers who assist in operating our website</li>
              <li>If required by law, regulation, or legal process</li>
              <li>To protect the rights, property, or safety of The Videshi, our users, or others</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">7. Data Retention</h2>
            <p>
              We retain your personal data only as long as necessary to fulfill the purposes outlined in this policy, or as required by law. Newsletter subscribers can unsubscribe at any time, after which we will delete their email address.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">8. Your Rights</h2>
            <p>Depending on your location, you may have the right to:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li>Access the personal data we hold about you</li>
              <li>Request correction or deletion of your data</li>
              <li>Opt out of marketing communications</li>
              <li>Request data portability</li>
            </ul>
            <p className="mt-2">
              To exercise any of these rights, contact us at <a href="mailto:hello@thevideshi.com" className="text-primary hover:underline">hello@thevideshi.com</a>.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">9. Children's Privacy</h2>
            <p>
              Our Site is not directed at children under 13. We do not knowingly collect personal information from children. If you believe we have collected such information, please contact us immediately.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">10. Changes to This Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated "Last updated" date. Your continued use of the Site after changes constitutes acceptance of the revised policy.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">11. Contact Us</h2>
            <p>
              If you have questions about this Privacy Policy, please contact us at{" "}
              <a href="mailto:hello@thevideshi.com" className="text-primary hover:underline">hello@thevideshi.com</a>.
            </p>
          </section>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
