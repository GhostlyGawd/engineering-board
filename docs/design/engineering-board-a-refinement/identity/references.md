# Cron Calendar — Style Reference
> Minimal dark cockpit. Clean contrast of white text on deep gray surfaces, punctuated by a vivid orange accent.

**Theme:** dark

This design system evokes a refined, understated dark mode, like a well-crafted instrument panel in a high-end vehicle. Its strength lies in a stark contrast between near-black surfaces and bright white typography, creating immediate clarity. A single, vibrant orange serves as the primary accent, drawing attention only to key interactive elements. The system feels direct and functional, prioritizing information hierarchy and calls to action over decorative flourishes.

## Tokens — Colors

| Name | Value | Token | Role |
|------|-------|-------|------|
| Cron Black | `#0f0d0a` | `--color-cron-black` | Primary page background, footer background. |
| Deep Graphite | `#161412` | `--color-deep-graphite` | Button backgrounds for secondary actions. |
| Bright White | `#ffffff` | `--color-bright-white` | Primary text color for headlines, body, navigation items, and button text, ensuring high contrast against dark backgrounds. |
| Subtle Gray | `#cccccc` | `--color-subtle-gray` | Secondary text, link underlines, subtle borders and outlines. Provides a softer visual hierarchy than pure white. |
| Action Orange | `#ff4700` | `--color-action-orange` | Primary call-to-action buttons, prominent interactive elements requiring immediate attention. This is the sole vivid chromatic color used. |
| Soft Ember | `#451e0` | `--color-soft-ember` | Shadow tint for action-oriented elements, contributing to a subtle glow rather than a harsh distinction. |
| Deep Ember | `#8b2e09` | `--color-deep-ember` | More saturated shadow tint for action-oriented elements, creating depth. |

## Tokens — Typography

### Helvetica Neue — Used universally across all text elements: headlines, body copy, navigation, buttons, and footer links. The wide range of weights and sizes allows for distinct hierarchy within a single, consistent typeface, particularly the oversized weight 700 for display headings. · `--font-helvetica-neue`
- **Substitute:** system-ui, sans-serif
- **Weights:** 400, 500, 700
- **Sizes:** 13px, 15px, 22px, 140px
- **Line height:** 0.90, 1.00, 1.50, 1.70, 2.88
- **Letter spacing:** -0.0210em, 0.0100em
- **Role:** Used universally across all text elements: headlines, body copy, navigation, buttons, and footer links. The wide range of weights and sizes allows for distinct hierarchy within a single, consistent typeface, particularly the oversized weight 700 for display headings.

### Type Scale

| Role | Size | Line Height | Letter Spacing | Token |
|------|------|-------------|----------------|-------|
| caption | 13px | 1.7 |  | `--text-caption` |
| body-sm | 15px | 1.7 | 0.15px | `--text-body-sm` |
| body | 22px | 1.5 |  | `--text-body` |
| display | 140px | 0.9 | -2.94px | `--text-display` |

## Tokens — Spacing & Shapes

**Density:** spacious

### Border Radius

| Element | Value |
|---------|-------|
| buttons | 4px |
| navigationPills | 9999px |

### Layout

- **Section gap:** 80px
- **Element gap:** 16px

## Components

### Announcement Pill Banner
### Button Group — Primary & Secondary
### Feature Stat / Metric Cards
### Primary Call-to-Action Button
**Role:** Interactive element

Background: Action Orange (#ff4700). Text: Bright White (#ffffff), Helvetica Neue weight 700. Padding: 0px top, 24px right, 1px bottom, 24px left. Border radius: 4px. No border.

### Secondary Button
**Role:** Interactive element

Background: Deep Graphite (#161412). Text: Bright White (#ffffff), Helvetica Neue weight 400. Padding: 0px top, 24px right, 1px bottom, 24px left. Border radius: 4px. Subtle Gray (#cccccc) top border. This button is used for secondary actions or contextual information.

### Header Navigation Link
**Role:** Navigation

Text: Bright White (#ffffff), Helvetica Neue weight 400, size 15px, line height 1.7. Appears as inline text, not buttonized except for 'Sign up'.

### Footer Link
**Role:** Navigation

Text: Bright White (#ffffff), Helvetica Neue weight 400, size 13px, line height 1.7. Used for legal and informational links.

## Do's and Don'ts

### Do
- Maintain a clear visual hierarchy by limiting prominent chromatic colors to the Action Orange (#ff4700) for primary CTAs.
- Utilize Bright White (#ffffff) text for primary content and Subtle Gray (#cccccc) for secondary, ensuring high readability on dark backgrounds.
- Apply Helvetica Neue universally, leveraging its differing weights (e.g., 700 for display, 400 for body) to establish content importance.
- Employ `sectionGap` of 80px between main content blocks to maintain a spacious, uncluttered flow.
- Use 4px border radius for all actionable buttons to provide subtle rounding without compromising precision.
- Apply `padding` of 0px top, 24px right, 1px bottom, 24px left for all buttons, maintaining a consistent minimalist vertical spacing.
- Use a 9999px border radius for tags and prominent notifications like 'Cron is now Notion Calendar' to create distinct pill shapes.

### Don't
- Do not introduce additional vivid chromatic colors beyond the established Action Orange (#ff4700) to maintain focus.
- Avoid using box shadows that introduce strong light colors or blur, as the system relies on flat, high-contrast surfaces augmented by subtle amber tints.
- Do not create extensive text blocks using Helvetica Neue at sizes larger than 22px; large text is reserved for display headlines.
- Avoid generic button styles; every button should either be Primary Call-to-Action (Action Orange) or Secondary (Deep Graphite).
- Do not vary `elementGap` from 16px unless explicitly for full-bleed section alignment or dense content blocks.
- Do not use overly complex or illustrative imagery; prefer UI screenshots or abstract graphics to align with the functional aesthetic.

## Imagery

The visual language for imagery is predominantly product screenshots, showcasing the cron calendar interface in dark mode. These are presented without ornate treatments, simply as contained, rectangular displays of the application. The primary role of imagery is explanatory and product-showcasing, focusing on functional aspects of the UI rather than decorative or atmospheric elements. There's a notable absence of lifestyle photography or complex illustrations, reinforcing the tool's utilitarian and professional identity.

## Layout

The overarching layout is a max-width contained model, centered on the page, providing clear boundaries for content. The hero section is full-bleed dark with a strong centered headline and smaller subtext that guides the eye towards the central product showcase. Section rhythm is primarily established by consistent vertical spacing (80px `sectionGap`) rather than alternating background colors, although subtle variations in surface color (not evident in the main screenshot but common in dark themes) may exist. Content is generally arranged in a stacked, single-column fashion for primary messaging, potentially transitioning to multi-column grids for features or details. Navigation is a simple top bar with left-aligned branding and right-aligned links and a primary CTA button, sticky to the top of the viewport.

## Agent Prompt Guide

1. Quick Color Reference:
   - Text: #ffffff
   - Background: #0f0d0a
   - CTA: #ff4700
   - Secondary Text: #cccccc
   - Secondary Background: #161412

2. Example Component Prompts:
   - Create a hero section: 'Cron Black' background. Headline 'It's about time.' in 'Bright White', Helvetica Neue weight 700, size 140px, line height 0.9, letter spacing -2.94px. Subtext 'Cron is the next-generation calendar for professionals and teams.' in 'Bright White', Helvetica Neue weight 400, size 22px, line height 1.5. Center align all text. Ensure a top padding of 80px above the headline.
   - Generate a secondary button: 'Deep Graphite' background. Text 'Cron is now Notion Calendar →' in 'Bright White', Helvetica Neue weight 400, size 15px, letter spacing 0.15px. Padding 0px 24px 1px 24px. Border radius 4px. Top border 1px 'Subtle Gray'.
   - Design a primary navigation bar: 'Cron Black' background. Logo left-aligned. Right-aligned links 'Blog', 'Changelog', 'Docs', 'Login' in 'Bright White', Helvetica Neue weight 400, size 15px, line height 1.7. Followed by a 'Primary Call-to-Action Button' 'Sign up'.

---

# LogoArchive — Style Reference
> Deep Digital Archive.

**Theme:** dark

LogoArchive presents a commanding dark-mode experience, reminiscent of a digital archive or library. Its aesthetic is dominated by deep, muted neutrals, creating a profound backdrop for content. Typography favors compact, confident sans-serifs, reserving a single, vivid yellow for functional accents. Components are lightweight with subtle border treatments and generous curves, balancing utility with a soft, approachable feel against the dark canvas.

## Tokens — Colors

| Name | Value | Token | Role |
|------|-------|-------|------|
| Midnight Ink | `#000000` | `--color-midnight-ink` | Page background (primary), card surfaces, text on bright surfaces |
| Carbon | `#18181b` | `--color-carbon` | Decorative fill for icons and abstract shapes |
| Steel Gray | `#27272a` | `--color-steel-gray` | Card backgrounds, button backgrounds, secondary surface color |
| Ash Gray | `#343538` | `--color-ash-gray` | Dark borders and separators for elevated surfaces and inverted UI. Do not promote it to the primary CTA color |
| Sky Haze | `#a8afb7` | `--color-sky-haze` | Muted secondary text, helper text, subtle borders |
| Stone | `#8c8c8d` | `--color-stone` | List item backgrounds, tertiary background for subtle differentiation |
| Porcelain | `#ffffff` | `--color-porcelain` | Primary text, icon fill, button text, card borders |
| Polar Mist | `#dadee4` | `--color-polar-mist` | Subtle background tones, light border accents |
| Amber Glow | `#fde533` | `--color-amber-glow` | Yellow outline accent for tags, dividers, and focused UI edges. Do not promote it to the primary CTA color |

## Tokens — Typography

### Suisse International — Primary content font for all text elements: headings (bold, large), body text, navigation, and button labels. Its wide range of weights and sizes provides clear visual hierarchy within a consistent aesthetic. · `--font-suisse-international`
- **Substitute:** Inter
- **Weights:** 400, 500
- **Sizes:** 12px, 14px, 16px, 18px, 19px, 24px, 28px, 65px, 96px
- **Line height:** 0.90, 1.00, 1.20, 1.75
- **Letter spacing:** normal
- **Role:** Primary content font for all text elements: headings (bold, large), body text, navigation, and button labels. Its wide range of weights and sizes provides clear visual hierarchy within a consistent aesthetic.

### Suisse Works Book — Used selectively for large, prominent headings, specifically for the main hero statements. Its distinct character provides a stylistic contrast to Suisse International while maintaining legibility. · `--font-suisse-works-book`
- **Substitute:** Lora
- **Weights:** 400
- **Sizes:** 65px, 96px
- **Line height:** 1.00, 1.20
- **Letter spacing:** normal
- **Role:** Used selectively for large, prominent headings, specifically for the main hero statements. Its distinct character provides a stylistic contrast to Suisse International while maintaining legibility.

### Type Scale

| Role | Size | Line Height | Letter Spacing | Token |
|------|------|-------------|----------------|-------|
| caption | 12px | 1.75 |  | `--text-caption` |
| body-sm | 14px | 1.75 |  | `--text-body-sm` |
| body | 16px | 1.75 |  | `--text-body` |
| subheading | 18px | 1.75 |  | `--text-subheading` |
| heading-sm | 24px | 1.2 |  | `--text-heading-sm` |
| heading | 28px | 1.2 |  | `--text-heading` |
| heading-lg | 65px | 1 |  | `--text-heading-lg` |
| display | 96px | 0.9 |  | `--text-display` |

## Tokens — Spacing & Shapes

**Density:** compact

### Border Radius

| Element | Value |
|---------|-------|
| tags | 999px |
| cards | 28px |
| lists | 40px |
| buttons | 20px |

### Layout

- **Section gap:** 24px
- **Card padding:** 32px
- **Element gap:** 8px

## Components

### Primary Action Button
**Role:** Call to action

Filled with Amber Glow (#fde533) with Midnight Ink (#000000) text, 20px border radius, and 4px 10px padding.

### Ghost Secondary Button
**Role:** Secondary action

Transparent background with Porcelain (#ffffff) text and 1px Porcelain (#ffffff) border, 20px border radius, and 4px 10px padding.

### Subtle Secondary Button
**Role:** Secondary action on dark backgrounds

Filled with Steel Gray (#27272a) background with Porcelain (#ffffff) text, 20px border radius, and 4px 10px padding.

### Standard Content Card
**Role:** Content grouping

Steel Gray (#27272a) background, 28px border radius, and 120px 0px 0px 0px padding. No shadow.

### Elevated Content Card
**Role:** Content grouping, slightly more prominent

Ash Gray (#343538) background, 22px border radius, and 32px 48px 32px 32px padding. No shadow.

### Minimal Card
**Role:** Basic container

Midnight Ink (#000000) background, 28px border radius. No padding.

### Pill Tag
**Role:** Informational tag or filter

Porcelain (#ffffff) background with Midnight Ink (#000000) text, 999px border radius for a pill shape.

## Do's and Don'ts

### Do
- Use Midnight Ink (#000000) for all primary page backgrounds and main text on Amber Glow surfaces.
- Apply Suisse International for all type, adjusting weight and size to create hierarchy, except for specific large hero headlines.
- Employ Steel Gray (#27272a) for default card backgrounds and subtle interactive elements.
- Prioritize a 28px border radius for most content cards and a 20px radius for buttons.
- Use Amber Glow (#fde533) exclusively for primary calls to action, tags, and small functional highlights.
- Maintain a compact element spacing with 8px as the default gap between components where possible.
- Ensure primary text is Porcelain (#ffffff) on dark backgrounds for optimal contrast.

### Don't
- Avoid using multiple chromatic colors; Amber Glow (#fde533) is the primary accent.
- Do not use box shadows for elevation; rely on background color differences and subtle borders instead.
- Refrain from using thin weights of type on dark backgrounds where legibility could be compromised.
- Do not introduce square or minimally rounded corners; all interface elements should embrace significant corner radii.
- Avoid large empty spaces beyond the pageMaxWidth; the layout should feel dense yet organized.
- Do not use generic system fonts; Suisse International and Suisse Works Book define the brand's typographic voice.
- Do not use generic grey for interactive states; utilize the Amber Glow (#fde533) for hover/active where appropriate for primary actions.

## Imagery

This site prominently features product screenshots and abstract graphics. Product screenshots are typically close-cropped UI elements or full interface views presented on the deep dark background, often showcasing geometric logo arrays. Imagery is contained, never full-bleed, and integrates seamlessly with the surrounding UI. Icons are simple, outlined or filled in monochromatic tones (Porcelain, Carbon), maintaining a clean, utilitarian aesthetic. The focus is on visual content as explanatory rather than decorative, showcasing the product directly.

## Layout

The page maintains a centered, max-width contained layout rather than full-bleed, creating a focused experience within the surrounding Midnight Ink canvas. The hero section features large, centered headlines over the dark background, often incorporating a single graphic element. Section rhythm is built on consistent vertical spacing, often with content blocks stacking vertically or arranging in multi-column grids (like the pricing cards). There are no overt visual dividers; sections flow into each other via background changes. Navigation is a minimal top bar with simple text links.

## Agent Prompt Guide

Quick Color Reference: 
text: #ffffff
background: #000000
border: #ffffff
accent: #fde533
primary action: #27272a (filled action)

Example Component Prompts:
1. Create a Primary Action Button: #27272a background, #ffffff text, 9999px radius, compact pill padding. Use this filled treatment for the main CTA.
2. Build a content card with a title 'Monthly' in Suisse International, weight 500, size 24px, line-height 1.2, color #ffffff. Use a Steel Gray (#27272a) background, 28px border radius, and 120px 0px 0px 0px padding. Inside, include a ghost text button: 'See pricing' with text #ffffff, transparent background, 1px border #ffffff, 20px radius, 4px 10px padding.
3. Design a small informational tag: 'A new format' using Amber Glow (#fde533) background, text #000000, and a 999px border radius with 4px 10px padding. Place it with an 8px element gap from a larger heading.
