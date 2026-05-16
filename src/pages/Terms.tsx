import { Helmet } from "react-helmet-async";
import Masthead from "@/components/Masthead";
import CategoryPills from "@/components/CategoryPills";
import SiteFooter from "@/components/SiteFooter";

export default function Terms() {
  return (
    <div className="min-h-screen flex flex-col">
      <Helmet>
        <title>Terms of Service — The Videshi</title>
        <meta name="description" content="Terms of Service for The Videshi — rules and guidelines for using our website." />
      </Helmet>
      <Masthead />
      <CategoryPills />
      <main className="container flex-1 py-8 max-w-3xl mx-auto">
        <h1 className="font-serif text-3xl md:text-4xl font-bold mb-2">Terms of Service</h1>
        <p className="text-sm text-muted-foreground mb-8">Last updated: May 16, 2026</p>

        <div className="prose prose-stone max-w-none space-y-6 text-[0.95rem] leading-relaxed">
          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">1. Acceptance of Terms</h2>
            <p>
              By accessing and using The Videshi ("thevideshi.com," the "Site"), you agree to be bound by these Terms of Service. If you do not agree, please discontinue use of the Site immediately.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">2. Description of Service</h2>
            <p>
              The Videshi is an online news publication providing editorial reporting and analysis for the global Indian diaspora. We cover news, politics, business, culture, travel, technology, sports, and lifestyle topics relevant to Indians living abroad.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">3. Intellectual Property</h2>
            <p>
              All content on the Site — including but not limited to articles, text, graphics, images, logos, and software — is the property of The Videshi or its content suppliers and is protected by intellectual property laws.
            </p>
            <p className="mt-2">You may not, without our prior written permission:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li>Reproduce, distribute, or republish any content from the Site</li>
              <li>Use content for commercial purposes</li>
              <li>Modify or create derivative works from our content</li>
            </ul>
            <p className="mt-2">
              Sharing links to articles on social media and messaging platforms is encouraged and permitted.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">4. User Conduct</h2>
            <p>When using the Site, you agree not to:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li>Violate any applicable laws or regulations</li>
              <li>Attempt to gain unauthorized access to any part of the Site</li>
              <li>Use automated systems (bots, scrapers) to access the Site without permission</li>
              <li>Interfere with or disrupt the Site's functionality</li>
              <li>Transmit viruses, malware, or harmful code</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">5. Editorial Content</h2>
            <p>
              The Videshi strives for accuracy in its reporting. However, we do not guarantee that all content is error-free, complete, or current. Articles represent editorial analysis and reporting and should not be construed as professional advice (legal, financial, medical, or otherwise).
            </p>
            <p className="mt-2">
              Some articles may utilize AI-assisted writing tools. All content is editorially reviewed before publication.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">6. Third-Party Links</h2>
            <p>
              The Site may contain links to third-party websites. We do not control and are not responsible for the content, privacy policies, or practices of any third-party sites. Following links to external sites is at your own risk.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">7. Newsletter & Communications</h2>
            <p>
              By subscribing to our newsletter, you consent to receive periodic emails from The Videshi. You can unsubscribe at any time using the unsubscribe link in any email or by contacting us directly.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">8. Disclaimer of Warranties</h2>
            <p>
              The Site is provided "as is" and "as available" without warranties of any kind, express or implied. We do not warrant that the Site will be uninterrupted, secure, or error-free.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">9. Limitation of Liability</h2>
            <p>
              To the fullest extent permitted by law, The Videshi shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of the Site.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">10. Changes to Terms</h2>
            <p>
              We reserve the right to modify these Terms at any time. Changes will be posted on this page with an updated "Last updated" date. Continued use of the Site after changes constitutes acceptance.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">11. Governing Law</h2>
            <p>
              These Terms shall be governed by and construed in accordance with the laws of the State of California, United States, without regard to conflict of law principles.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-xl font-bold mt-8 mb-3">12. Contact</h2>
            <p>
              For questions about these Terms, please contact us at{" "}
              <a href="mailto:hello@thevideshi.com" className="text-primary hover:underline">hello@thevideshi.com</a>.
            </p>
          </section>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
