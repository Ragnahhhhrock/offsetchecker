# Offsetcheck — Full Brand Style Guide

Version 1.0 · August 2026 · offsetcheck.com

## Contents
1. The Brand — positioning, name, tagline, attributes
2. Logo — mark, variants, construction, clear space, minimum sizes, misuse
3. Colour — palette, findings colours, usage rules
4. Typography — Inter scale, JetBrains Mono rules
5. UI & Layout Style — shape, depth, buttons, icons, charts, findings card
6. Voice & Tone — principles, say/don't-say, vocabulary
7. Assets & Compliance — kit inventory, checklist

---

## 1. The Brand

Offsetcheck independently verifies the numbers a bank gives its customer — re-calculating the interest charged on a home loan and the benefit credited by an offset account, line by line, to the cent.

**Positioning.** Banks calculate offset benefits and loan interest inside systems customers cannot see. Errors are rare, small, and almost always in the bank's favour — and almost never checked. Offsetcheck is the independent check: a precise, impartial auditor on the customer's side of the table. The brand must feel like a measuring instrument, not a protest movement.

**Name.** Always "Offsetcheck" — one word, capital O, everything else lowercase. Never "Offset Check", "Offset-Check", "OffsetCheck", "offsetCheck", "OFFSETCHECK". The domain `offsetcheck.com` and handles stay lowercase.

**Tagline.** "Keeping the bankers honest." Rules:
- Sentence case, exactly as written, trailing full stop in print and lockups.
- Never reword, translate, abbreviate, or use it as a headline about a specific bank or finding.
- In the tagline lockup it is set in JetBrains Mono — the voice of the ledger. Omit the tagline below 160 px lockup width; never squeeze it to fit.
- The tagline is cheeky but the product is sober: marketing may lean on it, in-product and findings copy must not editorialize.

**Brand attributes:**
| Attribute | In practice |
|---|---|
| Precise | Every claim carries a number and its working — "$412.07 over 14 months", never "a lot". |
| Independent | No bank partnerships or commissions. The answer is the same whoever asks. |
| Plain-spoken | Compound interest explained like a mate would; jargon always defined. |
| Calm | Findings stated, not dramatised. The mathematics is the headline. |

---

## 2. Logo

**The mark** is "the offset check": a bold verification tick with its offset twin — the same shape shifted up-left by 9 units. It visualises what the product does: lay the bank's figure and our independent figure side by side; the match (or mismatch) is the answer.

**Variants** (all in `assets/`):
| Asset | File | Use |
|---|---|---|
| Primary lockup, dark text | `offsetcheck-logo-horizontal-dark.svg` / `.png` | Light backgrounds — headers, documents, invoices |
| Primary lockup, white text | `offsetcheck-logo-horizontal-white.svg` / `.png` | Ink or gradient backgrounds |
| Tagline lockup | `offsetcheck-logo-tagline-dark.svg` / `-white.svg` (+ `.png`) | Hero sections, title pages, campaign end-frames |
| App icon | `offsetcheck-icon.svg`, `offsetcheck-icon-512.png`, `offsetcheck-icon-1024.png` | App icon, avatars, social profiles |
| Mono icons | `offsetcheck-icon-mono-dark.svg`, `offsetcheck-icon-mono-white.svg` | Single-colour print, embossing, watermarks, partner lockups |
| Favicon | `favicon.svg` | Browser tab, 16–64 px |

**Construction.** Tile = 96-unit square, 22-unit corner radius. Main tick stroke 11u; offset twin stroke 5.5u at 38% opacity, translated (−9, −9). Wordmark: Inter 700, "Offset" in Ink (or white), "check" in Signal Orange.

**Clear space** = x = 24 units (¼ tile) on all sides. Nothing enters it.

**Minimum sizes.** Horizontal lockup 120 px / 30 mm; tagline lockup 220 px / 55 mm; icon 16 px / 6 mm.

**Misuse — never:** stretch or condense; recolour gradient or wordmark; add shadows/effects; re-typeset the wordmark; place on busy or low-contrast backgrounds; reduce opacity or use as a faint watermark.

---

## 3. Colour

| Role | Name | Hex | Notes |
|---|---|---|---|
| Brand gradient | — | `linear-gradient(135deg, #FBBF24, #F97316)` | Logo tile, primary CTA, headline figures only |
| Brand | Surveyor Amber | `#FBBF24` | Accent |
| Brand | Signal Orange | `#F97316` | Accent; text only ≥18 pt bold on white, or on Ink |
| Accessible accent | Orange 700 | `#C2410C` | Small text/links on white |
| Neutral | Ink | `#101828` | Headings, dark surfaces |
| Neutral | Ledger Grey | `#344054` | Body text |
| Neutral | Muted | `#667085` | Captions, metadata |
| Neutral | Rule | `#E4E7EC` | Borders, dividers |
| Neutral | Canvas | `#F9FAFB` | Page background |
| Neutral | Surface | `#FFFFFF` | Cards, sheets |
| Findings | Verified | `#12B76A` | Check passed, figures match |
| Findings | Review | `#F79009` | Discrepancy within tolerance |
| Findings | Overcharge | `#F04438` | Confirmed discrepancy in bank's favour |

**Usage rules:**
- Proportion ≈ 70% neutrals, 25% grey text/rules, 5% amber/orange. The gradient stays special by staying rare.
- Findings colours are semantic, never decorative — a green badge always means verified.
- Dark mode: surfaces `#0C111D`, body text `#E4E7EC`, gradient unchanged.

---

## 4. Typography

**Inter** — interface and editorial:
| Style | Spec (weight · size/leading · tracking) | Use |
|---|---|---|
| Display | 700 · 40/48 · −2% | Campaign headlines, heroes |
| Heading 1 | 700 · 30/38 · −2% | Page titles |
| Heading 2 | 600 · 24/32 · −1% | Section titles |
| Heading 3 | 600 · 18/28 | Card/panel titles |
| Body | 400 · 16/26 | Paragraphs |
| Caption | 400 · 12/16 | Metadata, footnotes |

**JetBrains Mono** — the ledger voice. Mandatory for dollar amounts, interest rates, ledger/finding dates, account references, technical annotation. Signals "this is a verifiable figure". Mono micro-labels (e.g. VERIFIED) may be uppercase with letter-spacing.

**Rules:** sentence case headings; never body copy in mono; never amounts in a proportional face; no substitute typefaces. Load Inter 400–700 and JetBrains Mono 500/700.

---

## 5. UI & Layout Style

- Cards/panels: radius 12 px, 1 px `#E4E7EC` border, shadow `0 1px 3px rgba(16,24,40,.08)`.
- Inputs/tables: radius 8 px, 1 px Rule border.
- Status chips/findings badges: pill, mono uppercase 11 px, tinted background at 10% of the findings colour.
- Buttons: radius 10 px, height ≥ 44 px.
  - Primary — brand gradient background, `#101828` semibold label, verb label ("Check my offset", "Upload statement"). One per view.
  - Secondary — Surface white, 1 px Rule border, Ledger Grey label.
  - Destructive — `#F04438`, irreversible actions only.
- Icons: Lucide, 1.5 px stroke, Muted by default. No filled or 3D sets.
- Illustration: diagrammatic — thin rules, dimension lines, ledger rows, mono annotations. No stock photography of smiling families or piggy banks.
- Charts: Ink axes; Signal Orange = the bank's figure; Verified green = Offsetcheck's figure. The visual argument is always "two lines, laid side by side".
- **Findings card** (heart of the product), in order: verdict chip (Verified / Review / Overcharge) → headline figure in mono → the two compared amounts → expandable working. The headline figure is the only place outside the logo where the gradient may colour text.

---

## 6. Voice & Tone

Writes like a forensic accountant on your side: precise, plain, unimpressed by authority, never hysterical.

| Principle | Means |
|---|---|
| Show the working | Every claim followed by the figures that prove it. If we can't show it, we don't say it. |
| The customer's side | "Your bank", "your money", "you're owed". Never neutral about whose interest we serve — only about the math. |
| Plain English | "Interest you shouldn't have paid", not "erroneous debit interest accruals". |
| Calm, not alarmist | State the discrepancy and the dollar figure. No exclamation marks in findings. |
| Fair to facts | Accuse systems of errors, never people of crimes. |

| Say | Don't say |
|---|---|
| Your bank short-changed your offset benefit by $412.07 over 14 months. | Your bank is ripping you off! |
| We found a discrepancy. Here is the calculation, line by line. | Banks can't be trusted. |
| Check my offset | Submit |
| This figure is verified to the cent. | Trust us — it adds up. |
| Worth a look: $83.20 difference, inside tolerance. | ALERT: Problem detected!! |

**Vocabulary.** Use: verified, discrepancy, to the cent, the working, independent, tolerance, ledger. Avoid (banned in product copy): fraud, scam, criminal, rip-off, lying, shocking, outrage, guaranteed refund.

---

## 7. Assets & Compliance

**Kit inventory** (in `assets/`): `offsetcheck-icon.svg` (vector master), `offsetcheck-icon-512.png`, `offsetcheck-icon-1024.png`, `offsetcheck-icon-mono-dark.svg`, `offsetcheck-icon-mono-white.svg`, `offsetcheck-logo-horizontal-dark.svg/.png`, `offsetcheck-logo-horizontal-white.svg/.png`, `offsetcheck-logo-tagline-dark.svg/.png`, `offsetcheck-logo-tagline-white.svg/.png`, `favicon.svg`.

**Compliance checklist — every deliverable must pass:**
1. Name written "Offsetcheck"; tagline, if present, exactly "Keeping the bankers honest."
2. Logo used from kit files only — never re-typeset, recoloured, stretched, or rebuilt.
3. Colours only from this palette; gradient reserved for logo, primary CTA, and headline figures.
4. Type only Inter and JetBrains Mono; all amounts, rates and ledger dates in mono.
5. Findings colours used semantically only.
6. Voice: precise, plain, calm; no banned vocabulary.
