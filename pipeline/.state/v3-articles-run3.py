#!/usr/bin/env python3
"""Stage articles 5-6 (part 3) for the 2026-09-12 21:45 writer run."""
import importlib.util, json, re, os
_spec = importlib.util.spec_from_file_location('run1', os.path.join(os.path.dirname(__file__), 'v3-articles-run1.py'))
_run1 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_run1)
wc, STATE = _run1.wc, _run1.STATE

ARTICLES = []

# ============ 5. Obesity / asprosin study (lifestyle-health) ============
ARTICLES.append({
 'topic_id': '9f1b8145-7d9d-4eac-907b-3843235ce071',
 'llm_score': 3,
 'headline': "Fat Cells Keep Hunger Signal Stuck 'On' After Weight Loss, Study Finds",
 'subheadline': 'Case Western Reserve researchers say a lasting "obesity memory" in fat tissue may explain why weight returns after dieting or stopping GLP-1 drugs \u2014 and can pass from mother to child.',
 'slug': 'fat-cells-obesity-memory-asprosin-weight-loss',
 'category': 'lifestyle-health',
 'vertical': 'lifestyle-health',
 'article_type': 'breaking',
 'tags': ['obesity', 'weight loss', 'asprosin', 'GLP-1', 'health research', 'Case Western Reserve', 'diabetes'],
 'sources': [
   'https://case.edu/news/cleveland-research-team-identifies-biological-mechanism-may-explain-obesity-relapse',
   'https://medicalxpress.com/news/2026-09-fat-cells-retain-hunger-weight.html',
   'https://www.newswise.com/articles/cleveland-research-team-identifies-biological-mechanism-that-may-explain-obesity-relapse',
 ],
 'diaspora_angle': "India's growing obesity and diabetes burden makes the weight-regain problem familiar to diaspora families; the study was led by Indian-origin scientist Dr. Atul Chopra.",
 'image_url': None,
 'image_caption': 'Fat cells under a microscope. Researchers at Case Western Reserve University found that obesity leaves a lasting biological change in fat tissue that keeps the hunger hormone asprosin elevated even after weight loss.',
 'image_attribution': '',
 'body': '''<div class="key-takeaways"><ul>
<li>Scientists at Case Western Reserve University and the Harrington Discovery Institute have identified why weight regain is so common: obesity leaves a lasting "memory" in fat cells.</li>
<li>The study, published in Cell Reports, found that obesity keeps the hunger hormone asprosin elevated even after weight loss &mdash; an appetite signal stuck in the "on" position.</li>
<li>The same signal can cross the placenta from mother to baby, potentially programming a child for obesity before birth.</li>
<li>Blocking the asprosin pathway in mouse models prevented both post-diet weight regain and inherited obesity risk, pointing to future therapies.</li>
</ul></div>
<p>Two of biology's most stubborn mysteries &mdash; why almost everyone who loses weight gains it back, and why obesity passes from mother to child at rates diet and environment cannot explain &mdash; may share a single answer, according to new research from Cleveland.</p>
<p>In a study published in Cell Reports, scientists from Case Western Reserve University and the Harrington Discovery Institute at University Hospitals found that obesity creates a lasting biological change in fat cells that keeps the hunger hormone asprosin elevated even after weight loss. They call it "obesity memory."</p>
<h2>An Appetite Signal That Won't Switch Off</h2>
<p>Asprosin is a hormone produced by fat tissue that stimulates appetite by acting on the brain. The researchers found that once obesity sets in, fat cells keep pumping out elevated levels of asprosin even after the weight is gone &mdash; effectively leaving the body's hunger signal stuck in the "on" position day after day.</p>
<blockquote class="pull-quote">
<p>"Imagine having an appetite-stimulating signal stuck in the 'on' position day after day, despite losing weight. Our findings suggest one reason weight regain can be so difficult to prevent after treatment ends."</p>
<cite>&mdash; Dr. Atul Chopra, senior author, Case Western Reserve University School of Medicine</cite>
</blockquote>
<p>The finding may help explain why so many people regain weight after dieting &mdash; or after discontinuing GLP-1 medications such as Ozempic and Wegovy, a pattern that has frustrated patients and drugmakers alike.</p>
<h2>From Mother to Child</h2>
<p>The same elevated asprosin can cross the placenta from mother to baby, the researchers found, meaning a child can be born with a programmed susceptibility to obesity. "This may also explain why obesity became such an epidemic, and why the cycle has continued for generations," said Chopra, an associate professor of medicine, genetics and genomics at the Case Western Reserve School of Medicine and associate director of the Harrington Rare Disease Program at Harrington Discovery Institute at UH.</p>
<h2>A Path to New Therapies</h2>
<p>The most encouraging finding came from mouse models: blocking the asprosin pathway &mdash; from the gene that produces the hormone to the receptor in the brain that responds to it &mdash; prevented both weight regain after dieting and inherited obesity risk.</p>
<p>That result points to a new class of therapeutic strategies aimed squarely at the relapse problem that pharmaceutical companies are actively trying to solve. Rather than only suppressing appetite during treatment, future drugs could erase the "obesity memory" itself.</p>
<h2>Why It Matters for India</h2>
<p>India carries one of the world's heaviest metabolic burdens, with obesity and diabetes rising sharply across age groups. GLP-1 drugs are increasingly prescribed &mdash; and stopped, often over cost &mdash; making the regain problem a familiar one for Indian patients and physicians. A therapy that addresses the biological memory of obesity, rather than fighting it indefinitely, would be transformative. The study was led by Dr. Atul Chopra, an Indian-origin scientist, adding a familiar name to a global discovery.</p>
<h2>What's Next</h2>
<p>The research is preclinical &mdash; the blocking experiments were done in mice &mdash; so human therapies are years away. But the asprosin pathway is now a validated drug target, and the hunt for safe ways to switch off obesity memory has begun.</p>''',
})

# ============ 6. MIT HITMAN glioblastoma (technology) ============
ARTICLES.append({
 'topic_id': '13091638-53e6-4e7d-9fe7-97e4c2bf8aa0',
 'llm_score': 3,
 'headline': "MIT's Injectable 'Nanoantennas' Destroy Drug-Resistant Brain Cancer Cells",
 'subheadline': 'The magnetically activated HITMAN technology eliminated 52 percent of chemotherapy-resistant glioblastoma cells in lab tests and extended survival in mice, without harming healthy brain tissue.',
 'slug': 'mit-hitman-nanoantennas-glioblastoma',
 'category': 'technology',
 'vertical': 'technology',
 'article_type': 'breaking',
 'tags': ['MIT', 'glioblastoma', 'nanotechnology', 'cancer research', 'Deblina Sarkar', 'brain cancer'],
 'sources': [
   'https://news.mit.edu/2026/injectable-nanodevices-could-provide-effective-treatment-drug-resistant-glioblastoma-0909',
   'https://phys.org/news/2026-09-nanodevices-effective-treatment-drug-resistant.html',
 ],
 'diaspora_angle': "The breakthrough was led by MIT Media Lab's Deblina Sarkar, an Indian-origin researcher heading the Nano-Cybernetic Biotrek group.",
 'image_url': None,
 'image_caption': 'An illustration of injectable nanoantennas being wirelessly activated by a magnetic field to target a brain tumor. MIT researchers developed the HITMAN technology to destroy drug-resistant glioblastoma cells while leaving healthy tissue unharmed.',
 'image_attribution': 'Baju Joy and Gopikrishna Pillai / MIT Media Lab',
 'body': '''<div class="key-takeaways"><ul>
<li>MIT Media Lab researchers have developed injectable nanoantennas, each about one-hundredth the width of a human hair, that can be wirelessly activated to kill brain cancer cells.</li>
<li>The technology, called HITMAN, eliminated 52.2 percent of drug-resistant glioblastoma cells in laboratory tests &mdash; more than five times the effect of the standard chemotherapy drug temozolomide.</li>
<li>In mouse models, it extended median survival by more than 50 percent with no detectable toxicity to major organs or healthy brain tissue.</li>
<li>The open-access paper was published in Science Advances; the work was led by MIT's Deblina Sarkar using tumor tissue from Mayo Clinic patients.</li>
</ul></div>
<p>Glioblastoma, one of the most aggressive cancers known to medicine, may have met its match in particles smaller than a speck of dust. Researchers at the MIT Media Lab have developed injectable "nanoantennas" that can be magnetically activated from outside the body to generate localized electric fields that destroy brain cancer cells &mdash; while leaving healthy tissue alone.</p>
<p>The researchers call the technology HITMAN, short for highly localized electric-field-induced tumor therapy using magnetically actuated nanoantennas. An open-access paper describing it was published this week in Science Advances, according to MIT News.</p>
<h2>How It Works</h2>
<p>Each nanoantenna is about one-hundredth the width of a human hair. Once injected, the particles can be activated wirelessly by a low-frequency magnetic field &mdash; no higher than 200 kHz, deliberately kept below levels that would damage tissue &mdash; that penetrates the skull and brain. The magnetic field actuates magnetostrictive components inside the nanoantennas, creating stress and strain that deforms a piezoelectric film and produces localized electric fields around the tumor.</p>
<blockquote class="pull-quote">
<p>"In laboratory and animal studies, this approach significantly reduced tumor growth and extended survival without detectable side effects, highlighting its potential as a precise and safe brain cancer therapy."</p>
<cite>&mdash; Deblina Sarkar, associate professor, MIT Media Lab</cite>
</blockquote>
<p>Sarkar is an associate professor and AT&T Career Development Chair at the MIT Media Lab, where she heads the Nano-Cybernetic Biotrek group.</p>
<h2>Tested Against the Toughest Tumors</h2>
<p>To test HITMAN against the most clinically realistic version of the disease, the team worked with tumor tissue from patients diagnosed with aggressive, chemotherapy-resistant glioblastoma at the Mayo Clinic. In the laboratory, HITMAN eliminated 52.2 percent of these drug-resistant cancer cells &mdash; more than five times the effect of temozolomide, the standard chemotherapy drug &mdash; while leaving healthy neurons and brain-supporting astrocytes unharmed, MIT News reported.</p>
<p>The researchers then implanted those patient-derived tumor cells into the brains of mice, recreating the disease in a living system. In these orthotopic models &mdash; widely regarded as the gold standard for preclinical brain-tumor research &mdash; HITMAN substantially inhibited tumor growth and extended median survival by more than 50 percent, with no detectable toxicity to major organs or surrounding healthy tissue.</p>
<h2>Why Glioblastoma Needs New Weapons</h2>
<p>Glioblastoma is the most aggressive and treatment-resistant brain cancer known to medicine, carrying a median survival of just 12 to 15 months even with the best available care. Surgery, radiation, and chemotherapy buy time but rarely change the outcome; the cancer's resistance to drugs and its infiltration of healthy brain tissue make it exceptionally hard to treat.</p>
<p>HITMAN's appeal is precision. Unlike chemotherapy or radiation, which damage healthy cells alongside cancerous ones, the nanoantennas concentrate their electric fields at the tumor site.</p>
<h2>Diaspora Connection</h2>
<p>The research was led by Deblina Sarkar, an Indian-origin scientist at the MIT Media Lab. The study's illustrations were created by Baju Joy and Gopikrishna Pillai, adding more Indian-origin names to a breakthrough that originated in Cambridge, Massachusetts.</p>
<h2>What's Next</h2>
<p>The results are preclinical &mdash; mice, not people &mdash; and significant hurdles remain before human trials, including scaling the technology and proving long-term safety. But as a targeted, wireless therapy for one of medicine's deadliest cancers, HITMAN has earned its place on the watch list.</p>''',
})

for a in ARTICLES:
    a['word_count'] = wc(a['body'])
    fn = os.path.join(STATE, 'v3-article-%s.json' % a['topic_id'])
    with open(fn, 'w') as f:
        json.dump(a, f, indent=1, ensure_ascii=False)
    print('%s | slug=%s | words=%d' % (a['topic_id'], a['slug'], a['word_count']))
