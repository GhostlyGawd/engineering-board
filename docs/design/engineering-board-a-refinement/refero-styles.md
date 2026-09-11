# Attio — Style Reference
> Precision Digital Toolkit. A design system built on a foundation of high-contrast monochrome, where soft serif headlines provide a human touch to a clinical, tool-like interface.

**Theme:** light

The design feels like a meticulously organized, high-end instrument. It operates on a starkly minimalist, black-and-white axis, where near-black (#1c1d1f) on pure white is the default state for text and primary actions. The most distinctive choice is the typographic duality: large, inviting headlines are set in the soft serif Tiempos Text, while the entire user interface, from buttons to body copy, uses the neutral sans-serif Inter. This creates a rhythm between approachable storytelling and functional precision. Color is used with extreme restraint, appearing as subtle accents for interactive states or status indicators, ensuring the user's focus remains on content and functionality. A consistent 10px radius on buttons provides a soft counterpoint to the otherwise sharp, grid-aligned UI frames.

## Tokens — Colors

| Name | Value | Token | Role |
|------|-------|-------|------|
| White | `#ffffff` | `--color-white` | Primary page background, text on dark surfaces |
| Ash | `#f3f4f6` | `--color-ash` | Subtle background panels, button pressed state |
| Stone | `#e4e7ec` | `--color-stone` | Light borders, dividers |
| Slate | `#d3d8df` | `--color-slate` | Default borders, inactive UI elements |
| Lead | `#b5bdc9` | `--color-lead` | Placeholder text, disabled text |
| Overcast | `#8f99a8` | `--color-overcast` | Secondary body text, supporting labels |
| Metal | `#6f7988` | `--color-metal` | Tertiary body text, icons |
| Carbon | `#505967` | `--color-carbon` | Icons, subtle interactive elements |
| Ink | `#1c1d1f` | `--color-ink` | Primary text, headlines, primary button background |
| Abyss | `#000000` | `--color-abyss` | Footer background |
| Action Blue | `#407ff2` | `--color-action-blue` | Links, active state indicators — a rare injection of color for interactivity |
| Focus Blue | `#94b9ff` | `--color-focus-blue` | Focus rings and glows on interactive elements |
| Success Green | `#075a39` | `--color-success-green` | Status indicators, success notifications |
| Danger Red | `#772322` | `--color-danger-red` | Error messages, destructive action indicators |
| Warning Yellow | `#705500` | `--color-warning-yellow` | Warning notifications, status indicators |
| Magic Aura | `#70a1f0` | `--color-magic-aura` | Decorative gradients for background accents |

## Tokens — Typography

### Tiempos Text — Used exclusively for large, emotive headlines (28px+) to add a soft, human, and editorial quality that contrasts with the functional UI. The signature `ss03` stylistic set is critical. · `--font-tiempos-text`
- **Substitute:** Newsreader, Lora
- **Weights:** 400, 500
- **Sizes:** 28px, 40px
- **Line height:** 1.10, 1.23
- **Role:** Used exclusively for large, emotive headlines (28px+) to add a soft, human, and editorial quality that contrasts with the functional UI. The signature `ss03` stylistic set is critical.

### Inter Display — An optically-sized sans-serif for display text (32px+) where clarity and precision are paramount. Its tighter letter-spacing is key to its compact, authoritative appearance. · `--font-inter-display`
- **Substitute:** Inter
- **Weights:** 500, 600
- **Sizes:** 12px, 20px, 32px, 40px, 56px, 64px
- **Line height:** 1.00, 1.07, 1.10, 1.17, 1.19, 1.30
- **Role:** An optically-sized sans-serif for display text (32px+) where clarity and precision are paramount. Its tighter letter-spacing is key to its compact, authoritative appearance.

### Inter — The workhorse font for all UI elements: body copy, navigation, buttons, and labels. Its neutrality and legibility at all sizes make it the foundation of the user interface. The `ss03` stylistic set is always applied. · `--font-inter`
- **Substitute:** system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif
- **Weights:** 400, 500, 600, 700
- **Sizes:** 10px, 11px, 12px, 13px, 14px, 15px, 16px, 18px, 20px, 32px
- **Line height:** 1.00, 1.17, 1.19, 1.20, 1.23, 1.25, 1.30, 1.33, 1.38, 1.40, 1.42, 1.43, 1.45, 1.47, 1.50, 1.57, 2.20
- **Letter spacing:** -0.0200em, -0.0150em, -0.0130em, -0.0120em, -0.0110em, -0.0100em, -0.0050em
- **Role:** The workhorse font for all UI elements: body copy, navigation, buttons, and labels. Its neutrality and legibility at all sizes make it the foundation of the user interface. The `ss03` stylistic set is always applied.

### Type Scale

| Role | Size | Line Height | Letter Spacing | Token |
|------|------|-------------|----------------|-------|
| caption | 12px | 1.5 | -0.14px | `--text-caption` |
| body-sm | 14px | 1.43 | -0.14px | `--text-body-sm` |
| body | 16px | 1.5 | -0.24px | `--text-body` |
| subheading | 20px | 1.3 | -0.4px | `--text-subheading` |
| heading-sm | 28px | 1.23 | -0.42px | `--text-heading-sm` |
| heading | 40px | 1.1 | -0.6px | `--text-heading` |
| heading-lg | 56px | 1.1 | -1.12px | `--text-heading-lg` |
| display | 64px | 1.07 | -1.28px | `--text-display` |

## Tokens — Spacing & Shapes

**Density:** compact

### Border Radius

| Element | Value |
|---------|-------|
| tabs | 0px |
| tags | 4px |
| cards | 8px |
| inputs | 7px |
| buttons | 10px |

### Shadows

| Name | Value | Token |
|------|-------|-------|
| UI Frame Card | `rgba(28, 40, 64, 0.1) 0px 2px 3px -2px, rgba(28, 40, 64, 0.04) 0px 4px 6px -2px` | `--shadow-ui-frame-card` |
| Input Focus | `0 0 0 3px color-mix(in srgb, #94b9ff 40%, transparent)` | `--shadow-input-focus` |

### Layout

- **Section gap:** 96px
- **Card padding:** 16px
- **Element gap:** 8px
- **Page max width:** 1440px

## Components

### CTA Button Group
### Feature Tab Bar
### AI Ask Input Card
### Primary CTA Button
**Role:** The main call-to-action.

Background: Ink (#1c1d1f). Text: White (#ffffff). Font: 14px Inter weight 500. Padding: 8px 12px. Border: 1px solid #1c1d1f. Radius: 10px.

### Secondary CTA Button
**Role:** Secondary call-to-action, or an alternative to the primary.

Background: White (#ffffff). Text: Ink (#1c1d1f). Font: 14px Inter weight 500. Padding: 8px 12px. Border: 1px solid Slate (#d3d8df). Radius: 10px.

### Header Navigation Button
**Role:** Used for navigation links in the main header.

Background: transparent. Text: Metal (#6f7988). Font: 14px Inter weight 500. Padding: 6px 10px. Radius: 10px. Hover state has an Ash (#f3f4f6) background.

### Feature Tab Button
**Role:** Used in a tab group to switch between content views.

Background: transparent. Text: Metal (#6f7988). Font: 15px Inter weight 500. Padding: 8px 16px. Radius: 0px. Active state has Ink (#1c1d1f) text and a 2px bottom border of Ink (#1c1d1f).

### UI Frame Card
**Role:** Container for complex UI modules, like the main app demo.

Background: White (#ffffff). Padding: 16px. Border: 1px solid Stone (#e4e7ec). Radius: 8px. Shadow: `rgba(28, 40, 64, 0.1) 0px 2px 3px -2px, rgba(28, 40, 64, 0.04) 0px 4px 6px -2px`.

### Text Input
**Role:** Standard text input field.

Background: White (#ffffff). Text: Ink (#1c1d1f). Font: 14px Inter. Placeholder text: Lead (#b5bdc9). Border: 1px solid Slate (#d3d8df). Radius: 7px. Focus state shows a blue glow using Focus Blue (#94b9ff).

### Logo Cloud Item
**Role:** Displays a partner or customer logo.

Grayscale logo fill using Carbon (#505967) or Metal (#6f7988). No background or border.

### Page Footer
**Role:** The closing section of the page with site-wide links.

Background: Abyss (#000000). Organized into columns. Column titles use White (#ffffff) text at 14px, weight 500. Links use Overcast (#8f99a8) text at 14px, weight 400, changing to White on hover.

## Do's and Don'ts

### Do
- Always set display and hero headlines in Tiempos Text.
- Use Inter with the `ss03` font feature setting for all UI copy.
- Apply negative letter-spacing to all text 18px and larger, following the type scale.
- Construct primary CTAs from Ink (#1c1d1f) backgrounds with White (#ffffff) text.
- Maintain a consistent 10px radius on all major buttons.
- Use borders (1px Slate #d3d8df) as the primary method for separating UI elements.
- Reserve color (Action Blue #407ff2) for interactive states like links and focus rings.

### Don't
- Don't use Tiempos Text for body copy or any text smaller than 28px.
- Don't use color in headlines or primary buttons.
- Don't use fill-based colors unless for semantic status indicators.
- Don't apply shadows to buttons, inputs, or simple cards.
- Don't use radii other than 10px for buttons or 8px for cards.
- Don't forget to include the `ss03` font feature when setting type.
- Don't introduce new saturated colors; the palette is intentionally monochrome.

## Imagery

Imagery is functional and abstract, avoiding lifestyle photography. The primary visuals are clean product UI screenshots contained within minimalist browser or app frames. Secondary visuals consist of abstract data visualizations, like the grid of grayscale profile pictures, which serve as atmospheric graphics rather than literal content. All imagery is rendered with sharp edges and presented in a clean, isolated manner.

## Layout

The layout is built on a centered, max-width (1440px) model, creating generous white space on the peripheries. Hero sections are minimal, typically a large, centered headline stack. Page content follows a predictable rhythm of stacked, centered sections or simple two-column layouts. A key structural element is the large, embedded product UI demonstration, which acts as the visual centerpiece. Navigation is contained within a simple, sticky top bar.

## Agent Prompt Guide

### Quick Color Reference
- **Primary Text:** `#1c1d1f` (Ink)
- **Secondary Text:** `#8f99a8` (Overcast)
- **Page Background:** `#ffffff` (White)
- **Primary CTA:** bg `#1c1d1f` (Ink), text `#ffffff` (White)
- **Border:** `#d3d8df` (Slate)
- **Interactive Accent:** `#407ff2` (Action Blue)

### Example Component Prompts
1.  **Hero Section:** Create a hero with a white background. Main headline: 'Customer relationship magic.', font Tiempos Text, size 64px, weight 500, color Ink (#1c1d1f), line-height 1.07, letter-spacing -1.28px. Sub-headline below: 'Attio is the AI CRM for GTM.', font Inter, size 20px, weight 500, color Metal (#6f7988), letter-spacing -0.4px. Centered layout.

2.  **Primary CTA Button:** Create a button with the text 'Start for free'. Background color Ink (#1c1d1f), text color White (#ffffff). Font is 14px Inter at weight 500. Padding is 8px top/bottom and 12px left/right. Border-radius is 10px.

3.  **UI Frame Card:** Create a card with a White (#ffffff) background, 16px padding on all sides, an 8px border-radius, and a 1px solid border of color Stone (#e4e7ec). Apply the shadow style: `rgba(28, 40, 64, 0.1) 0px 2px 3px -2px, rgba(28, 40, 64, 0.04) 0px 4px 6px -2px`.

---

# Changelog — Style Reference
> Midnight command center behind frosted glass.

**Theme:** dark

This design system evokes a 'midnight command center behind frosted glass,' achieving a focused, high-tech atmosphere through a dark achromatic palette and precise typographic choices. A subtly layered grayscale background creates depth without relying on heavy shadows, while crisp text and restrained accenting maintain readability. Signature anti-conventional headlines use weight 500 at larger sizes, conveying authority through subtle refinement rather than bold weight. The system relies on precise border treatments and a dominant 9999px radius for interactive elements, contrasting with 8px radius for cards, to define interaction points within the otherwise serious interface.

## Tokens — Colors

| Name | Value | Token | Role |
|------|-------|-------|------|
| Canvas Black | `#08090a` | `--color-canvas-black` | Page backgrounds, base surface for main content areas. |
| Surface Dark | `#141516` | `--color-surface-dark` | Slightly elevated surfaces, button backgrounds in hover states, subtle distinctions from Canvas Black. |
| Line Graphite | `#34343a` | `--color-line-graphite` | Subtle dividers, borders on interactive elements, visual separation within dark surfaces. |
| Deep Charcoal | `#1c1c1f` | `--color-deep-charcoal` | Darker interactive elements, further elevated background layers for specific components. |
| Border Carbon | `#23252a` | `--color-border-carbon` | Input borders, subtle outlines for inactive states, separating elements on dark backgrounds. |
| Border Ash | `#2d2e31` | `--color-border-ash` | Border color for certain interactive components, providing a slightly lighter outline than Carbon. |
| Text Primary | `#f7f8f8` | `--color-text-primary` | Primary text, headings, icons, ensuring high contrast against dark backgrounds. Also used as background for ghost buttons. |
| Text Secondary | `#d0d6e0` | `--color-text-secondary` | Secondary text, muted information, subtle accents, less prominent list items. Provides visual relief from primary text. |
| Text Muted | `#8a8f98` | `--color-text-muted` | Placeholder text, tertiary information, disabled states. Signifies lower importance or non-interactivity. |
| Highlight Fog | `#e4e5e9` | `--color-highlight-fog` | Light background highlight on interactive elements, subtle iconography against dark backgrounds. |
| Shadow Tint | `#3e3e44` | `--color-shadow-tint` | Border color for interactive elements and subtle shadow effects. Creates definition without heavy contrast. |

## Tokens — Typography

### Inter Variable — Used for all primary UI text, body copy, headings, and interactive elements. Its variable nature allows fine-grained control over weight, with a specific emphasis on a mid-range weight (500) for headlines to convey modern, understated authority. The tight letter-spacing (-0.01em) maintains a compact, disciplined appearance. · `--font-inter-variable`
- **Substitute:** Inter
- **Weights:** 400, 500, 510, 590
- **Sizes:** 12px, 13px, 14px, 15px, 16px, 17px, 24px, 32px, 48px
- **Line height:** 1.00, 1.13, 1.20, 1.33, 1.40, 1.50, 1.60, 2.46, 2.67, 2.86
- **Letter spacing:** -0.01em
- **Role:** Used for all primary UI text, body copy, headings, and interactive elements. Its variable nature allows fine-grained control over weight, with a specific emphasis on a mid-range weight (500) for headlines to convey modern, understated authority. The tight letter-spacing (-0.01em) maintains a compact, disciplined appearance.

### Berkeley Mono — Exclusively for code blocks, timestamps, and technical notations. Its monospaced nature clearly differentiates technical content, and the slightly tighter letter-spacing hints at precision. · `--font-berkeley-mono`
- **Substitute:** Space Mono
- **Weights:** 400, 590
- **Sizes:** 15px, 21px
- **Line height:** 1.30
- **Letter spacing:** -0.014em
- **Role:** Exclusively for code blocks, timestamps, and technical notations. Its monospaced nature clearly differentiates technical content, and the slightly tighter letter-spacing hints at precision.

### Type Scale

| Role | Size | Line Height | Letter Spacing | Token |
|------|------|-------------|----------------|-------|
| caption | 12px | 1.4 | -0.12px | `--text-caption` |
| heading | 24px | 1.33 | -0.29px | `--text-heading` |
| heading-lg | 32px | 1.2 | -0.38px | `--text-heading-lg` |
| display | 48px | 1.13 | -0.58px | `--text-display` |

## Tokens — Spacing & Shapes

**Density:** compact

### Border Radius

| Element | Value |
|---------|-------|
| cards | 8px |
| search | 100px |
| buttons | 9999px |
| interactive | 4.46px |

### Shadows

| Name | Value | Token |
|------|-------|-------|
| Button (filled) | `rgba(255, 255, 255, 0.03) 0px 0px 0px 1px inset, rgba(255, 255, 255, 0.04) 0px 1px 0px 0px inset, rgba(0, 0, 0, 0.6) 0px 0px 0px 1px, rgba(0, 0, 0, 0.1) 0px 4px 4px 0px` | `--shadow-button-(filled)` |
| Input Focus/Hover | `rgb(62, 62, 68) 0px 0px 0px 1px` | `--shadow-input-focus/hover` |
| Navigation Bar | `rgba(0, 0, 0, 0.01) 0px 5px 2px 0px, rgba(0, 0, 0, 0.04) 0px 3px 2px 0px, rgba(0, 0, 0, 0.07) 0px 1px 1px 0px, rgba(0, 0, 0, 0.08) 0px 0px 1px 0px` | `--shadow-navigation-bar` |

### Layout

- **Section gap:** 24px
- **Card padding:** 16px
- **Element gap:** 8px

## Components

### Text Link
**Role:** Interactive text, navigation items.

Text Primary #f7f8f8, Inter Variable weight 400. No underline by default; hover state adds underline or changes background.

### Ghost Button (Primary)
**Role:** Primary Call to Action, outlines interactiveness without filling.

Background transparent, text #f7f8f8 (Text Primary). Border 1px solid #f7f8f8. Border radius 9999px. Padding 0px top/bottom, 12px left/right for medium, 16px for large.

### Ghost Button (Secondary)
**Role:** Secondary actions that need less visual emphasis.

Background transparent, text #8a8f98 (Text Muted). Border 1px solid #8a8f98. Border radius 9999px. Padding 0px top/bottom, 12px left/right.

### Filled Button (Compact)
**Role:** Small, contained action buttons.

Background #141516 (Surface Dark), text #8a8f98 (Text Muted). Border 1px solid #23252a (Border Carbon). Border radius 100px. Padding 0px top/bottom, 16px left/right.

### Search Input
**Role:** Input elements for search functionality.

Background transparent. Placeholder text #8a8f98 (Text Muted). Border 1px solid #34343a (Line Graphite). Border radius 100px. Icon fill #8a8f98. Padding 0px vertical, 12px horizontal.

### Changelog Card
**Role:** Container for changelog entries.

Background transparent. Contents date in Berkeley Mono, title as Heading Small. Border 1px solid #34343a (Line Graphite) on inactive/hover. Border radius 8px. Inner padding around content section 16px.

### Navigation Tab
**Role:** Filtering or category navigation.

Text #f7f8f8 (Text Primary) for active, #8a8f98 (Text Muted) for inactive. Background transparent. Border radius 9999px. Padding 0px top/bottom, 12px left/right.

### Pill Tag
**Role:** Categorization or short labels.

Background #141516 (Surface Dark), text #f7f8f8 (Text Primary). Border radius 9999px. Padding 0px top/bottom, 12px left/right.

## Do's and Don'ts

### Do
- Prioritize Inter Variable font for all UI text, ensuring readability and consistency.
- Use Text Primary #f7f8f8 for all main text elements and headings on dark backgrounds to maintain strong contrast.
- Apply Canvas Black #08090a as the dominant background color across all pages.
- Use 9999px border radius for all actionable buttons and interactive pill components.
- Employ a 1px solid border using Line Graphite #34343a for subtle visual separation of components and containers, especially on hover.
- Leverage Berkeley Mono for all code snippets, timestamps, or technical text, keeping its distinct letter-spacing.
- Apply Surface Dark #141516 for subtle elevation for backgrounds of interactive components or hover states.

### Don't
- Avoid using multiple vibrant colors; restrict accent colors to functional elements if not present in the palette.
- Do not use heavy shadows for visual depth; rely on background color layering and subtle borders instead.
- Do not introduce new typefaces; the system is built on Inter Variable and Berkeley Mono.
- Avoid large hero imagery; prefer UI-focused elements or subtle graphic overlays.
- Do not use generic square corners; apply 8px radius to cards and containers for a softer, integrated feel.
- Do not use standard, bold font weights for large headlines; leverage Inter Variable weight 500-590 for a refined, modern approach.
- Avoid overly bright or pure white backgrounds; the system is designed for a dark interface.

## Surfaces

| Level | Name | Value | Purpose |
|-------|------|-------|---------|
| 0 | Canvas Black | `#08090a` | Dominant page background, providing the base dark theme. |
| 1 | Surface Dark | `#1c1c1f` | Slightly elevated component backgrounds, such as the search input or interactive elements on hover. |
| 2 | Interactive Surface | `#141516` | Backgrounds for ghost buttons, tags, or other active interactive components, offering a minimal step up from the base canvas. |

## Imagery

The visual language is characterized by functional abstraction and product-focused graphics. It primarily uses icons and stylized, often monochrome, product screenshots or UI elements within dark, contained boxes. Icons are outlined, with a moderate stroke weight, and mostly monochromatic, occasionally using a subtle gradient. Imagery serves an explanatory role for product features or decorative atmosphere within the dark UI, always contained and never full-bleed. There's a high density of text-dominant content, punctuated by these visually precise, often button-like, graphics.

## Layout

The page maintains a max-width contained layout, with content centered within a defined vertical flow. The hero section is a full-bleed dark canvas with a left-aligned, prominent headline. Sections follow a consistent vertical rhythm, primarily using a text-heavy, single-column stack for changelog entries, occasionally broken by centered visual components like the grid of app icons. Navigation is provided by a sticky top bar with clearly segmented, low-prominence text links and a ghost button for primary action. The layout emphasizes clarity and direct information delivery, with ample vertical rhythm from the 24px section gap and compact element spacing.

## Agent Prompt Guide

### Quick Color Reference
- text: #f7f8f8
- background: #08090a
- border: #34343a
- accent: no distinct accent color
- primary action: no distinct CTA color

### 3-5 Example Component Prompts
1. Create a changelog entry: Date in Berkeley Mono #d0d6e0, background transparent, border bottom 1px solid #34343a. Headline (weight 590, Inter Variable, size 24px, #f7f8f8, letter-spacing -0.29px). Body text (weight 400, Inter Variable, size 15px, #d0d6e0, letter-spacing -0.15px).
2. Create a ghost button: Text 'Log in' in Inter Variable weight 400, size 15px, #f7f8f8. Background transparent. Border 1px solid #f7f8f8. Radius 9999px. Padding 0px vertical, 12px horizontal.
3. Create a search input: Background transparent. Placeholder 'Search…' in Inter Variable weight 400, size 15px, #8a8f98. Icon (magnifying glass) fill #8a8f98. Border 1px solid #34343a. Radius 100px. Padding 0px vertical, 12px horizontal.
4. Create a pill tag: Text 'Fixes' in Inter Variable weight 400, size 13px, #f7f8f8. Background #141516. Radius 9999px. Padding 0px vertical, 12px horizontal.
5. Create a header navigation item: Text 'Customers' in Inter Variable weight 400, size 15px, #f7f8f8. Hover state changes text to #e4e5e9.

---

# Mintlify — Style Reference
> Digital librarian's desk. Precise information architecture meets subtle brand identity through selective color accents.

**Theme:** light

Mintlify captures an atmosphere of serene, intelligent efficiency, like navigating a well-organized digital library. The predominant use of highly desaturated grays and stark black-on-white provides a clean, information-focused base. A single vivid green (#0c8c5e) acts as a digital beacon, highlighting interactive elements and key information without visual clutter. The visual restraint in color and a subtle elevation system communicate authority through clarity, making complex documentation feel approachable.

## Tokens — Colors

| Name | Value | Token | Role |
|------|-------|-------|------|
| Ink | `#000000` | `--color-ink` | Primary text, core UI elements, strong contrasts against light backgrounds |
| White Canvas | `#ffffff` | `--color-white-canvas` | Page backgrounds, card surfaces, inverted text on dark elements |
| Coal | `#08090a` | `--color-coal` | Prominent headings, button backgrounds, elevated text |
| Platinum | `#f2f2f2` | `--color-platinum` | Subtle borders, dividers, subtle background variations |
| Steel | `#dddddd` | `--color-steel` | Thin stroke borders, less noticeable dividers |
| Sage Mark | `#0c8c5` | `--color-sage-mark` | Primary brand accent, interactive elements like CTA buttons, active states, key icons, and selected links. Its vividness provides clear visual cues in an otherwise neutral palette. |
| Emerald Glow | `#00dc8d` | `--color-emerald-glow` | Secondary accent for icons or subtle graphic highlights, complementing the primary Sage Mark. |
| Deep Cobalt | `#0052ff` | `--color-deep-cobalt` | Specific graphic elements, illustrations where a strong, vibrant blue is needed. |

## Tokens — Typography

### Inter — The sole typeface, used across all elements from headings to body text. Its clean, sans-serif design maintains legibility and a modern feel. The slight negative letter spacing on larger sizes adds a touch of sophistication to headlines, while positive spacing on smaller text ensures clarity, creating a subtly formal yet efficient tone. · `--font-inter`
- **Substitute:** system-ui
- **Weights:** 400, 500, 600
- **Sizes:** 13px, 14px, 15px, 16px, 18px, 20px, 24px, 40px, 57px
- **Line height:** 1.10, 1.15, 1.30, 1.33, 1.50, 1.71
- **Letter spacing:** -0.0200em at 57px, -0.0100em at 40px/24px, 0.0500em at 13px
- **Role:** The sole typeface, used across all elements from headings to body text. Its clean, sans-serif design maintains legibility and a modern feel. The slight negative letter spacing on larger sizes adds a touch of sophistication to headlines, while positive spacing on smaller text ensures clarity, creating a subtly formal yet efficient tone.

### Type Scale

| Role | Size | Line Height | Letter Spacing | Token |
|------|------|-------------|----------------|-------|
| caption | 13px | 1.71 | 0.65px | `--text-caption` |
| body | 16px | 1.5 |  | `--text-body` |
| subheading | 18px | 1.33 |  | `--text-subheading` |
| heading-sm | 20px | 1.3 |  | `--text-heading-sm` |
| heading | 24px | 1.15 | -0.24px | `--text-heading` |
| heading-lg | 40px | 1.15 | -0.4px | `--text-heading-lg` |
| display | 57px | 1.1 | -1.14px | `--text-display` |

## Tokens — Spacing & Shapes

**Density:** comfortable

### Border Radius

| Element | Value |
|---------|-------|
| tags | 4px |
| cards | 16px |
| inputs | 0px |
| buttons | 1.67772e+07px |
| largeElements | 24px |

### Shadows

| Name | Value | Token |
|------|-------|-------|
| Elevated Button (Dark) | `lab(2.42579 -0.165291 -0.470081 / 0.03) 0px 2px 4px 0px` | `--shadow-elevated-button-(dark)` |
| Elevated Button (Light) | `lab(100 0 0 / 0.05) 0px 2px 4px 0px` | `--shadow-elevated-button-(light)` |

### Layout

- **Section gap:** 64px
- **Card padding:** 16-24px

## Components

### Email CTA Input
### Feature Cards — Built for the Intelligence Age
### Customer Story Cards
### Text Link
**Role:** Navigation, inline links, secondary actions

backgroundColor=rgba(0,0,0,0), color=rgb(0,0,0) / lab(2.42579 -0.165291 -0.470081), borderRadius=16777216px, paddingTop=0px, paddingRight=0px, paddingBottom=0px, paddingLeft=0px. Appears as pure text initially, relying on context for interactivity.

### Outline Button
**Role:** Call to action, navigation items

backgroundColor=rgba(0,0,0,0), color=rgb(0,0,0), borderTopColor=rgb(0,0,0), borderRadius=4px, paddingTop=0px, paddingRight=0px, paddingBottom=0px, paddingLeft=0px. A subtle interactive element, contrasting with the filled button through its transparent background and border.

### Pill Ghost Button - Light Text
**Role:** Navigation, secondary actions on dark backgrounds

backgroundColor=rgba(0, 0, 0, 0), color=lab(100 0 0), borderTopColor=lab(100 0 0), borderRadius=1.67772e+07px, paddingTop=4px, paddingRight=12px, paddingBottom=4px, paddingLeft=12px. Used for subtle interactions, particularly within headers or on contrasting sections.

### Pill Filled Button - Dark Text
**Role:** Primary call to action in light contexts

backgroundColor=lab(100 0 0), color=lab(2.42579 -0.165291 -0.470081), borderTopColor=lab(100 0 0), borderRadius=1.67772e+07px, paddingTop=4.5px, paddingRight=12px, paddingBottom=4.5px, paddingLeft=12px. Provides strong visual emphasis for conversions when paired with a light background.

### Email Input Field
**Role:** Data entry, form submissions

backgroundColor=rgba(0, 0, 0, 0), color=lab(100 0 0), borderTopColor=lab(100 0 0), borderRadius=0px, paddingTop=0px, paddingRight=12px, paddingBottom=0px, paddingLeft=12px. A minimal input style with no background or border, relying on context and focus states for discoverability.

### Elevated Button (Light)
**Role:** Key interactive elements where a subtle lift is desired.

background: White Canvas (#ffffff), text: Coal (#08090a), shadow: lab(100 0 0 / 0.05) 0px 2px 4px 0px. This variant provides a subtle elevated visual for interactions without being visually heavy.

### Elevated Button (Dark)
**Role:** Key interactive elements on darker backgrounds where a subtle lift is desired.

background: Coal (#08090a), text: White Canvas (#ffffff), shadow: lab(2.42579 -0.165291 -0.470081 / 0.03) 0px 2px 4px 0px. Offers elevation on darker elements, maintaining visual hierarchy.

## Do's and Don'ts

### Do
- Prioritize Inter font at all sizes and weights; use negative letter spacing on display sizes (57px: -1.14px, 40px: -0.4px) for a refined look and positive spacing (13px: 0.65px) for captions to ensure legibility.
- Use Sage Mark (#0c8c5e) exclusively for primary interactive elements, active states, and essential brand indicators to maintain its visual impact and clarity.
- Apply White Canvas (#ffffff) strictly as the default page background and for card surfaces, allowing content to breathe and accent colors to pop.
- Form inputs should be minimal, using a borderRadius of 0px and a transparent background (rgba(0,0,0,0)), allowing the surrounding design to define their presence.
- Employ the `lab(2.42579 -0.165291 -0.470081 / 0.03) 0px 2px 4px 0px` shadow for subtle content elevation against dark backgrounds and `lab(100 0 0 / 0.05) 0px 2px 4px 0px` for light backgrounds.
- Maintain a consistent elementGap of 4px, 6px, 8px, 10px, or 12px between adjacent UI elements to ensure a harmonious and comfortable density.
- Round all buttons, and other interactive pill-shaped elements to 1.67772e+07px for a modern, distinct soft edge that contrasts with the sharper 4px and 16px radii found elsewhere.

### Don't
- Do not introduce new typefaces; rely solely on Inter to preserve the visual identity.
- Avoid using highly saturated colors other than Sage Mark (#0c8c5e) or Emerald Glow (#00dc8d) for primary UI elements; reserve others for illustrative accents only.
- Do not deviate from the specified borderRadius values (1.67772e+07px for pills, 0px for inputs, 4px for tags, 16px for cards) to maintain shape consistency.
- Do not use dark backgrounds where White Canvas (#ffffff) is expected, as this would break the light theme consistency and intended contrast ratios.
- Do not use letter-spacing: normal. Always apply precise letter-spacing according to the type scale to maintain typographic rhythm.
- Avoid excessive decoration or complex gradients on UI elements; the design emphasizes clarity and directness.
- Do not add additional shadows beyond the specified `lab(2.42579 -0.165291 -0.470081 / 0.03) 0px 2px 4px 0px` or `lab(100 0 0 / 0.05) 0px 2px 4px 0px` to maintain a light and intentional elevation profile.

## Imagery

The visual language for imagery leans heavily into abstract illustrations and product-focused visuals. Illustrations feature soft-edged, almost cloud-like shapes with subtle gradients and muted colors (like the light blue and orange clouds in the hero). Product screenshots, when present, are often cleanly cropped and contained within UI elements or cards, focusing on function. Photography is absent. Icons are typically monoline in style, either black on white or the brand's Sage Mark green, providing clear visual cues for functionality. The overall role of imagery is decorative and atmospheric in hero sections, illustrative for concepts, and clearly explanatory for product features, maintaining a text-dominant layout punctuated by strategic visual aids.

## Layout

The site uses a max-width contained layout rather than full-bleed, centering content to enhance focus. The hero section is full-width with large background illustrations, overlaid by a centered headline and call to action. Subsequent sections alternate between clear, distinct blocks with generous vertical spacing (sectionGap of ~64px). Content within sections often defaults to centered stacking or a 2-column layout with text on one side and a visual element or card grid on the other. Card grids often feature 3-5 columns. The navigation is a sticky top bar, providing persistent access without intruding on content. The overall density feels comfortable and spacious, allowing for easy readability.

## Agent Prompt Guide

### Quick Color Reference
- Text: Ink (#000000)
- Background: White Canvas (#ffffff)
- CTA Primary: Sage Mark (#0c8c5e)
- Border Subtle: Platinum (#f2f2f2)
- Heading: Coal (#08090a)

### 3-5 Example Component Prompts
1. Create a Hero Section: Background with abstract cloud illustration. Centered headline 'The Intelligent Knowledge Platform' in Inter weight 600, size 57px, Coal (#08090a), letterSpacing -1.14px. Subhead below it 'Helping teams create and maintain world-class documentation built for both humans and AI' in Inter weight 400, size 18px, Ink (#000000). Below that, a horizontal stack of an Email Input Field on left with a Pill Filled Button - Dark Text (White Canvas background, Coal text) on the right.
2. Create a Navigation Bar: Background White Canvas (#ffffff). Logo 'mintlify' Sage Mark (#0c8c5e). Top-right navigation links: 'Resources', 'Documentation', 'Customers', 'Blog', 'Pricing' as Text Links (Ink #000000). Alongside 'Contact sales' as an Outline Button, and 'Start for free' as a Pill Filled Button - Dark Text (White Canvas background, Coal text, borderRadius 1.67772e+07px, paddingTop 4.5px, paddingRight 12px).
3. Create a Feature Card: White Canvas (#ffffff) background, borderRadius 16px. Padding 24px all sides. Headline 'Quickstart Guide' in Inter weight 600, size 24px, Coal (#08090a). Body text beneath 'Start building intelligent documentation in five minutes' in Inter weight 400, size 16px, Ink (#000000).
