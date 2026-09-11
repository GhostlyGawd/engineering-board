# Factory.ai — Style Reference
> Architectural blueprint on white marble. Lines are crisp, colors are limited, and every element serves a clear, functional purpose.

**Theme:** light

Factory.ai embraces a 'technical brutalism meets digital precision' aesthetic, prioritizing informational clarity and directness. The near-monochromatic palette, dominated by light grays and deep charcoals, provides a stark, high-contrast backdrop for technical content. A single vivid orange accent color is deployed sparingly as a functional indicator, highlighting interactive elements and key information without visual noise. The strong typographic voice, characterized by precise letter-spacing and a monospace variant for code, reinforces the structured, engineering-focused identity.

## Tokens — Colors

| Name | Value | Token | Role |
|------|-------|-------|------|
| Factory Black | `#020202` | `--color-factory-black` | Primary text, darkest surface background (e.g., active navigation items), critical interactive elements. |
| Factory Light Gray | `#eeeeee` | `--color-factory-light-gray` | Page background, light surface elements (card backgrounds), default button backgrounds. Provides a clean, spacious canvas. |
| Faded Silver | `#fafafa` | `--color-faded-silver` | Slightly lighter alternative to Factory Light Gray, used for subtle differentiation of card backgrounds and elements. |
| Cool Gray | `#b8b3b0` | `--color-cool-gray` | Subtle borders, inactive button outlines, secondary text. Establishes divisions without harshness. |
| Graphite | `#3d3a39` | `--color-graphite` | Strong borders, dark icons, secondary text. A darker gray for depth and contrast. |
| Ash Gray | `#a49d9a` | `--color-ash-gray` | Subtle interactive borders and backgrounds, similar to Cool Gray but with a touch more warmth. |
| Code Orange | `#ef6f2` | `--color-code-orange` | Accent color for 'NEW' badges, interactive indicators, and small, high-attention elements. Its vividness cuts through the neutral palette. |

## Tokens — Typography

### Geist — Primary typeface for all headings, body text, navigation, and general UI. The carefully tuned negative letter-spacing, particularly at larger sizes, creates a composed, intentional feel, preventing headlines from feeling loose. · `--font-geist`
- **Substitute:** Inter
- **Weights:** 400
- **Sizes:** 14px, 16px, 18px, 24px, 48px, 60px
- **Line height:** 1.00, 1.20, 1.50
- **Letter spacing:** -0.0480em, -0.0300em
- **Role:** Primary typeface for all headings, body text, navigation, and general UI. The carefully tuned negative letter-spacing, particularly at larger sizes, creates a composed, intentional feel, preventing headlines from feeling loose.

### Geist Mono — Used for code snippets, CLI instructions, and any content requiring a fixed-width, precise presentation. Its subtle negative letter-spacing maintains a tight, readable block structure. · `--font-geist-mono`
- **Substitute:** JetBrains Mono
- **Weights:** 400
- **Sizes:** 12px, 14px, 16px, 18px
- **Line height:** 1.00, 1.20, 1.38, 1.50
- **Letter spacing:** -0.0200em
- **Role:** Used for code snippets, CLI instructions, and any content requiring a fixed-width, precise presentation. Its subtle negative letter-spacing maintains a tight, readable block structure.

### Type Scale

| Role | Size | Line Height | Letter Spacing | Token |
|------|------|-------------|----------------|-------|
| caption | 12px | 1.5 | -0.24px | `--text-caption` |
| body-sm | 14px | 1.5 |  | `--text-body-sm` |
| body | 16px | 1.5 |  | `--text-body` |
| subheading | 18px | 1.2 |  | `--text-subheading` |
| heading | 24px | 1.2 |  | `--text-heading` |
| heading-lg | 48px | 1.2 | -2.3px | `--text-heading-lg` |
| display | 60px | 1 | -2.88px | `--text-display` |

## Tokens — Spacing & Shapes

**Density:** comfortable

### Border Radius

| Element | Value |
|---------|-------|
| cards | 6px |
| header | 0px |
| buttons | 4px |
| default | 4px |

### Layout

- **Section gap:** 72px
- **Card padding:** 16px
- **Element gap:** 4px

## Components

### CLI Install Block
### News Article Cards
### Product Section Nav
### Text Link
**Role:** Navigation, inline links, 'Learn More' buttons

Color Factory Black (#020202) for primary links, transitioning to Graphite (#3d3a39) for secondary. No explicit underline until hover, relying on contrast and context for discoverability. Uses Geist, 14-16px, weight 400.

### Navigation Link
**Role:** Top navigation menu items

Color Factory Black (#020202) on Factory Light Gray (#eeeeee) background. No special styling, relying solely on typography (Geist, 14px, 400 weight) for visual presence. Active items use the same styling with a subtle visual cue or background change.

### Ghost Button
**Role:** Secondary actions, grouped options (macOS / Linux)

Transparent background with text color Factory Black (#020202). Has a subtle Cool Gray (#b8b3b0) border. Padding 0 for inline context. Radius 0px.

### Outlined Button
**Role:** Download buttons, secondary calls to action

Transparent background with Factory Black (#020202) text. Border color Cool Gray (#b8b3b0), 1px solid. Padding 0 vertically, 12px horizontally. Radius 4px. Font Geist, 16px, 400 weight.

### Filled Button (Light)
**Role:** Download buttons, primary calls to action

Background Factory Light Gray (#eeeeee), text Factory Black (#020202). Border color Ash Gray (#a49d9a). Padding 0 vertically, 12px horizontally. Radius 4px. Font Geist, 16px, 400 weight.

### Filled Button (Dark)
**Role:** Download buttons, primary calls to action (alternative)

Background Factory Black (#020202), text Factory Black (#020202). Border color Ash Gray (#a49d9a). Padding 6px vertically, 12px horizontally. Radius 8px. The dark background with dark text is counter-intuitive for contrast, suggesting a specific functional or state-based context.

### List Item Card
**Role:** Content blocks in feature sections

Transparent background, no shadow, 0px border radius. Padding 0 vertically, 16px horizontally. Used as a container for grouped information. Text uses Factory Black (#020202).

### Elevated Content Card
**Role:** Featured content blocks, forms, interactive elements

Background Faded Silver (#fafafa), no shadow, 6px border radius. Padding 16px vertically, 0 horizontally. Provides a slight visuallift from the main background.

### Code Input Block
**Role:** CLI instruction display, interactive code examples

Background Factory Light Gray (#eeeeee), no shadow, 6px border radius. Padding 0. Contains monospaced text for commands. May feature interactive elements like a copy button.

### 'NEW' Badge
**Role:** Highlights new features or content

Transparent background, text Code Orange (#ef6f2e). Radius 0px, padding 0. Appears as a small, vivid text label next to titles, using Geist Mono 12px.

## Do's and Don'ts

### Do
- Prioritize Factory Black (#020202) for primary text and Factory Light Gray (#eeeeee) for background, ensuring AAA contrast.
- Apply Geist font consistently for all UI text, utilizing negative letter-spacing for large headlines (e.g., -0.0480em at 60px) to achieve a condensed, precise appearance.
- Use Geist Mono for all code snippets and CLI instructions at weights 400 and sizes 12-18px for clear distinction.
- Implement Cool Gray (#b8b3b0) for subtle borders and dividers to maintain visual structure without heavy lines.
- Reserve Code Orange (#ef6f2e) strictly for highlighting functional elements like 'NEW' badges and active indicators.
- Maintain a default border radius of 4px for buttons and form elements, extending to 6px for elevated cards.
- Ensure consistent vertical spacing of 24px and horizontal elements gaps of 12px or 8px using the base 4px unit.

### Don't
- Avoid using chromatic colors beyond Code Orange (#ef6f2e) to maintain the stark, technical aesthetic.
- Do not introduce shadows or complex gradients; rely on color and typography for hierarchy and depth.
- Do not use generic system fonts; always specify Geist or Geist Mono for design consistency.
- Avoid excessive padding or large border radii; the design favors a compressed, precise feel.
- Do not use underlines for links unless on hover, rely on color and context (Factory Black on light backgrounds).
- Avoid arbitrary text styling (bolding, italics); rely on the established type scale (Geist, 400 weight) for hierarchy.
- Do not deviate from the specified negative letter-spacing values, especially for headlines, as it is a core characteristic of the brand's typography.

## Imagery

The visual language for imagery is primarily functional and technical, leaning heavily on abstract conceptual graphics, UI screenshots, and code blocks. Product screenshots are contained within precise, slightly rounded frames, often featuring stylized UI elements rather than raw interfaces. Graphics are typically monochromatic or use a limited palette, often employing dotted patterns (like the 'grid' in the hero section) and stark lines. There's an absence of photography or human elements, focusing instead on the tools and concepts of software development. Imagery serves an explanatory role, illustrating functionality or abstracting complex ideas, with a high density relative to other pure UI sites.

## Layout

The page structure employs a full-width layout with a primary content area constrained by a clear maximum width, centered on the screen. The hero section is a split two-column design: text-dominant on the left with a headline and descriptive copy, and abstract/UI visuals on the right, punctuated by sparse dot patterns. Sections generally follow a consistent vertical rhythm, often alternating between text-heavy content and content paired with product screenshots or conceptual graphics, typically in a two-column arrangement (text left, image right, or vice versa). There are occasional three-column card grids for presenting features or articles. The navigation is a persistent top bar, clean and functional, with a clear separation of branding and menu items. The layout emphasizes clarity and content organization, feeling spacious yet structured.

## Agent Prompt Guide

### Quick Color Reference
- **Text Primary:** #020202
- **Page Background:** #eeeeee
- **Card Background:** #fafafa
- **Border/Divider:** #b8b3b0
- **Accent:** #ef6f2e

### Example Component Prompts
1. **Create a Hero Section:** Set page background to Factory Light Gray (#eeeeee). Left half: headline 'Agent-Native Software Development' in Geist, 60px, weight 400, letter-spacing -0.0480em, color Factory Black (#020202). Subheading 'The only software development agents that work everywhere you do.' in Geist, 18px, weight 400, color Graphite (#3d3a39). Right half: an abstract graphic with subtle dotted patterns.
2. **Generate an Outlined Button:** Label 'Download macOS (Apple Silicon)'. Use transparent background, Factory Black (#020202) text, Cool Gray (#b8b3b0) 1px border. Padding top/bottom 0px, left/right 12px. Border radius 4px. Font Geist, 16px, weight 400.
3. **Design a Code Input Block:** Use background Factory Light Gray (#eeeeee), no border, 6px border-radius. Inside, display code `curl -fsSL https://app.factory.ai/cli | sh` in Geist Mono, 16px, weight 400, letter-spacing -0.0200em, color Factory Black (#020202). Add a copy icon next to it.
4. **Create an Elevated Content Card:** Use background Faded Silver (#fafafa), no box-shadow, 6px border-radius. Padding 16px top/bottom, 0px left/right. Insert a 'NEW' badge next to a section title. The 'NEW' badge should be text 'NEW' in Geist Mono, 12px, weight 400, color Code Orange (#ef6f2e).
5. **Build a Navigation Bar:** Use background Factory Light Gray (#eeeeee) with no border. Nav links like 'Product', 'Enterprise' use Geist, 14px, weight 400, color Factory Black (#020202). Include 'Log In' button as a Filled Button (Dark) variant and 'Contact Sales' as an Outlined Button.

---

# Linear — Style Reference
> Midnight Command Center: A dark, layered interface lit by precise accents, like a high-tech control panel.

**Theme:** dark

Linear presents a sophisticated and focused dark-mode experience, reminiscent of a command center dashboard. A deep charcoal base creates a serious, immersive canvas, while subtle gradients and layered surfaces build depth without harsh contrasts. Distinctive muted text colors (#8a8f98 for secondary, #62666d for tertiary) maintain readability against the dark backdrop. Critically, interaction is marked by a single vivid lime green (#e4f222), applied selectively to primary calls to action, preventing visual clutter and guiding the user's eye with precision.

## Tokens — Colors

| Name | Value | Token | Role |
|------|-------|-------|------|
| Pitch Black | `#08090a` | `--color-pitch-black` | Page background, primary surface for base elements, subtly integrated into shadows for depth. |
| Graphite | `#0f1011` | `--color-graphite` | Elevated card backgrounds, slightly lighter than the canvas to denote layering. |
| Deep Slate | `#161718` | `--color-deep-slate` | Secondary elevated card backgrounds, providing another layer of visual hierarchy. |
| Charcoal Grey | `#23252a` | `--color-charcoal-grey` | Borders and some shadowed card surfaces, framing elements with a subtle distinction. |
| Muted Ash | `#323334` | `--color-muted-ash` | Subtle borders and dividers, indicating soft separations within the dark theme. |
| Gunmetal | `#383b3f` | `--color-gunmetal` | Tertiary background elements and input borders, a darker neutral for functional elements. |
| Porcelain | `#f7f8f8` | `--color-porcelain` | Primary text and icons, providing strong contrast for readability against dark backgrounds. |
| Light Steel | `#d0d6e0` | `--color-light-steel` | Secondary text and borders, for less prominent information or structural lines. |
| Storm Cloud | `#8a8f98` | `--color-storm-cloud` | Tertiary text, descriptive labels, and inactive states, recedes into the background for low-priority details. |
| Fog Grey | `#62666d` | `--color-fog-grey` | Muted text for metadata, timestamps, and further de-emphasized content. |
| Alabaster | `#e5e5e6` | `--color-alabaster` | Informational borders and subtle fills, often seen in code blocks or explanatory components. |
| Neon Lime | `#e4f222` | `--color-neon-lime` | Primary action indicators, active states, and focus elements — a high-energy focal point. |
| Aether Blue | `#5e6ad2` | `--color-aether-blue` | Decorative highlights and occasional background elements, suggesting a technological or informational context. |
| Forest Green | `#008d2c` | `--color-forest-green` | Positive status indicators, success messages, and related iconography. |
| Cyan Spark | `#02b8cc` | `--color-cyan-spark` | Informational highlights and unique icon fills, providing a cool accent. |
| Emerald | `#27a644` | `--color-emerald` | Success and completion states, often paired with green text. |
| Warning Red | `#eb5757` | `--color-warning-red` | Observed in icon fill, body borderColor, other fill. Extracted usage does not support a distinct primary control color. |
| Deep Violet | `#6366f1` | `--color-deep-violet` | Background accents in specific content blocks, indicating a distinct informational category. |
| Amethyst | `#8b5cf6` | `--color-amethyst` | Another variant of violet for backgrounds, used interchangeably with Deep Violet for visual diversity. |

## Tokens — Typography

### Inter Variable — Primary UI typeface for all content including headings, body text, and interactive elements. Its variable weights provide a clean, modern aesthetic with strong technical readability. · `--font-inter-variable`
- **Substitute:** Inter
- **Weights:** 300, 400, 510, 590
- **Sizes:** 10px, 11px, 12px, 13px, 14px, 15px, 16px, 17px, 20px, 24px, 32px, 48px, 64px, 72px
- **Line height:** 1.00, 1.13, 1.20, 1.33, 1.40, 1.47, 1.50, 1.60, 2.00, 2.46, 2.75
- **Letter spacing:** -0.22, -0.15, -0.13, -0.12, -0.11, -0.1
- **Role:** Primary UI typeface for all content including headings, body text, and interactive elements. Its variable weights provide a clean, modern aesthetic with strong technical readability.

### Berkeley Mono — Monospaced font for code snippets, technical details, and certain data displays, ensuring consistent character alignment and technical clarity. · `--font-berkeley-mono`
- **Substitute:** IBM Plex Mono
- **Weights:** 400
- **Sizes:** 12px, 13px, 14px
- **Line height:** 1.30, 1.40, 1.50, 1.71
- **Letter spacing:** -0.15
- **Role:** Monospaced font for code snippets, technical details, and certain data displays, ensuring consistent character alignment and technical clarity.

### Type Scale

| Role | Size | Line Height | Letter Spacing | Token |
|------|------|-------------|----------------|-------|
| caption | 10px | 1.4 | -0.1px | `--text-caption` |
| body | 14px | 1.4 | -0.13px | `--text-body` |
| heading | 24px | 1.33 | -0.22px | `--text-heading` |
| heading-lg | 48px | 1.2 | -0.22px | `--text-heading-lg` |
| display | 72px | 1 | -0.22px | `--text-display` |

## Tokens — Spacing & Shapes

**Density:** compact

### Border Radius

| Element | Value |
|---------|-------|
| pill | 9999px |
| tags | 2px |
| cards | 6px |
| badges | 4px |
| inputs | 6px |
| buttons | 6px |
| default | 6px |

### Shadows

| Name | Value | Token |
|------|-------|-------|
| Default Card | `rgba(0, 0, 0, 0.4) 0px 2px 4px 0px` | `--shadow-default-card` |
| Sidebar/Menu Element Focus | `rgba(0, 0, 0, 0.2) 0px 0px 12px 0px inset` | `--shadow-sidebar/menu-element-focus` |
| Elevated Card Inset | `rgb(35, 37, 42) 0px 0px 0px 1px inset` | `--shadow-elevated-card-inset` |
| Card Border/Input Focus | `rgba(0, 0, 0, 0.2) 0px 0px 0px 1px` | `--shadow-card-border/input-focus` |
| Navigation/Button Subtle Lift | `rgba(0, 0, 0, 0.01) 0px 5px 2px 0px, rgba(0, 0, 0, 0.04) 0px 3px 2px 0px, rgba(0, 0, 0, 0.07) 0px 1px 1px 0px, rgba(0, 0, 0, 0.08) 0px 0px 1px 0px` | `--shadow-navigation/button-subtle-lift` |

### Layout

- **Section gap:** 24px
- **Card padding:** 12px
- **Element gap:** 8px

## Components

### Issue Card
### CTA Button Group
### Issue List Board
### Primary Action Button
**Role:** Call to action button

Filled button with 'Neon Lime' background (#e4f222), 'Pitch Black' text (#08090a), 6px border-radius, and variable padding. Used for primary user actions.

### Ghost Navigation Button
**Role:** Navigation and secondary actions

Ghost button with transparent background, 'Porcelain' text (#f7f8f8), no explicit padding, and 0px border-radius. Navigational links or simple interactive elements.

### Subtle Link Button
**Role:** Tertiary actions and links

Ghost button with transparent background, 'Light Steel' text (#d0d6e0), 6px border-radius, and minimal padding (0px top/bottom, 6px left/right). Used for less prominent interactive elements or textual links.

### Navigation Item Button
**Role:** Sidebar navigation items

Ghost button with transparent background, 'Storm Cloud' text (#8a8f98), 2px border-radius, and no explicit padding. Used for items in a navigation list.

### Default Card
**Role:** Content container

Card with 'Graphite' background (#0f1011), 6px border-radius, and an outer shadow of rgba(0, 0, 0, 0.4) 0px 2px 4px 0px. Padding is 8px on all sides.

### Elevated Card
**Role:** Prominent content container

Card with 'Deep Slate' background (#161718), 12px top border-radius (0px bottom), and an inset shadow of rgb(35, 37, 42) 0px 0px 0px 1px. Padding is 24px vertical and 0px horizontal.

### Nested Card
**Role:** Internal content grouping

Card with 'Pitch Black' background (#08090a) and 12px border-radius, no shadow. Padding 8px on all sides, used for containing sub-elements within larger cards.

### Input Field
**Role:** User input fields

Input field with transparent background, 'Porcelain' text (#f7f8f8), 'Charcoal Grey' border (#23252a), and 6px border-radius. Padding is 12px vertical and 14px horizontal.

### Subtle Input Field
**Role:** Search or secondary input fields

Input field with 'Gunmetal' background (#383b3f), 'Porcelain' text (#f7f8f8), no explicit border, and 0px border-radius. Used for less emphasized data entry.

### Badge
**Role:** Label or tag

Badge with a 'Gunmetal' background (#383b3f), 'Storm Cloud' text (#8a8f98), 4px border-radius, and padding of 0px vertical and 6px horizontal. Used for small categorical labels.

## Do's and Don'ts

### Do
- Use 'Pitch Black' (#08090a) for the primary page background to establish the dark theme.
- Apply 'Porcelain' (#f7f8f8) for all primary text and important icons to ensure readability.
- Highlight primary interactive elements exclusively with 'Neon Lime' (#e4f222) as a background, restricting its use to guide user attention.
- Create depth and hierarchy by layering surfaces using 'Pitch Black' (#08090a), 'Graphite' (#0f1011), and 'Deep Slate' (#161718) backgrounds.
- Employ the Inter Variable font family with specific letter-spacing adjustments for all UI text, such as -0.22px for display sizes and -0.11px for body text, to maintain a tight, precise feel.
- Utilize 6px border-radius for all primary buttons, cards, and input fields to maintain a consistent, subtly rounded aesthetic.
- Use 'Storm Cloud' (#8a8f98) for secondary text and descriptive labels to recede into the background.

### Don't
- Do not introduce additional bright or saturated colors beyond 'Neon Lime' (#e4f222) for interactive elements; maintain its singular role.
- Avoid using harsh white backgrounds or light-themed patterns, as the system is anchored in a dark mode aesthetic.
- Do not deviate from the specified typeface choices; 'Inter Variable' and 'Berkeley Mono' are fundamental to the visual identity.
- Refrain from using strong, diffuse shadows; elevation is achieved through subtle layering and sharp, contained shadows like rgba(0, 0, 0, 0.4) 0px 2px 4px 0px.
- Do not apply broad, decorative background gradients across large sections of the UI; gradients are subtle and contained to specific functional areas.
- Do not use generic border-radii; adhere to 6px for key components like cards and buttons, and 2px for smaller tags, to preserve the signature balance of softness and precision.
- Avoid large amounts of white space; the design is compact, leveraging an 8px element gap as a standard measurement.

## Surfaces

| Level | Name | Value | Purpose |
|-------|------|-------|---------|
| 0 | Pitch Black Canvas | `#08090a` | Base page background and deepest surface level. |
| 1 | Graphite Card | `#0f1011` | Primary card surface for general content, slightly elevated from the canvas. |
| 2 | Deep Slate Elevated Card | `#161718` | More prominent card surface, used for focused content sections or lists. |
| 3 | Charcoal Grey Overlay | `#23252a` | Accent surface for borders, shadows, and subtle overlays, providing clear separation. |

## Imagery

The site's visual language is dominated by UI elements and product screenshots, emphasizing functionality over decorative imagery. Where images appear, they are often contained within realistic product mockups or embedded application frames. Abstract graphics are minimal, primarily serving as subtle background textures or data visualizations. Icons are filled, minimalist, and mono-color, often adopting the 'Porcelain' (#f7f8f8) or 'Storm Cloud' (#8a8f98) neutral palette, enhancing the dashboard aesthetic. The overall density of imagery is low; it serves an explanatory or product showcase role rather than a decorative one.

## Layout

The page primarily uses a full-bleed structure for background content, with main content sections constrained by a centered maximum width (not explicitly defined but visually present). The hero section features a full-bleed 'Pitch Black' background with a centered, prominent headline. Subsequent sections alternate between dark backgrounds for narrative content and embedded UI examples, often featuring split layouts (text on one side, product UI on the other). Content is generally arranged in vertical stacks or multi-column grids for feature display. Navigation consists of a sticky top bar and frequently observed left-hand sidebar for application-like structures. Spacing is compact yet deliberate, creating a dense but organized information flow.

## Agent Prompt Guide

Quick Color Reference:
- text: #f7f8f8 (Porcelain)
- background: #08090a (Pitch Black)
- border: #23252a (Charcoal Grey)
- accent: #5e6ad2 (Aether Blue)
- primary action: #e4f222 (filled action)

3-5 Example Component Prompts:
- Create a call-to-action button: 'Neon Lime' background (#e4f222), 'Pitch Black' text (#08090a), Inter Variable font weight 590 at 15px, 6px border-radius, 12px vertical and 24px horizontal padding.
- Create a default card with content: 'Graphite' background (#0f1011), 6px border-radius, rgba(0, 0, 0, 0.4) 0px 2px 4px 0px shadow. Inside, use Inter Variable font weight 400 at 14px with 'Porcelain' text (#f7f8f8), and a subsection headline at 17px weight 510 with 'Porcelain' text (#f7f8f8). Apply 8px padding internally.
- Create a sidebar navigation item: Ghost button with transparent background, 'Storm Cloud' text (#8a8f98), Inter Variable font weight 400 at 14px, 2px border-radius, no padding.
- Create an input field: transparent background with a 'Gunmetal' fill (#383b3f), 'Light Steel' text (#d0d6e0) using Inter Variable font weight 400 at 14px, 6px border-radius. Inset with a 1px 'Charcoal Grey' border (#23252a). Padding 12px vertical and 14px horizontal.

---

# SST — Style Reference
> Config File on Paper — An architects precise blueprint on pristine white, using code as a primary visual element.

**Theme:** light

This design system presents complex technical configurations with a light, spacious, and highly legible aesthetic. The dominant use of a nearly white background provides a clean canvas, while a nuanced palette of near-gray and muted violet shades for text and interactive elements grounds the interface without heavy contrasts. A signature element is the code block's precise syntax highlighting, which uses a range of vivid and moderate hues to structure information within a constrained, elegant form.

## Tokens — Colors

| Name | Value | Token | Role |
|------|-------|-------|------|
| Page White | `#ffffff` | `--color-page-white` | Page backgrounds, elevated components like the code editor card. |
| Border Ash | `#e8e8f2` | `--color-border-ash` | Subtle borders on interactive elements like search buttons and code editors, providing minimal visual separation. |
| Text Graphite | `#403f53` | `--color-text-graphite` | Body text and secondary information, offering good contrast against white without being stark black. |
| Text Slate | `#767682` | `--color-text-slate` | Tertiary text, icons, and muted UI elements. It provides a soft, secondary visual cue. |
| Text Fog | `#a8a8b0` | `--color-text-fog` | Dimmed or inactive text elements, such as placeholder text or disabled states, providing low visual impact. |
| Text Jet | `#111111` | `--color-text-jet` | Heading text, providing highest contrast for primary titles. |
| Primary Violet | `#303055` | `--color-primary-violet` | Main call-to-action text, links, and prominent headings. This muted violet provides the primary brand identity, appearing frequently for interactive elements. |
| Code Rose | `#984e4d` | `--color-code-rose` | Syntax highlighting in code blocks, for specific types of values or keywords. |
| Code Magenta | `#8844ae` | `--color-code-magenta` | Syntax highlighting in code blocks, providing vivid contrast for important elements like function names or variables. |
| Code Sky | `#5196b3` | `--color-code-sky` | Syntax highlighting for specific code elements, like type definitions or comments. |
| Code Indigo | `#3b61b0` | `--color-code-indigo` | Syntax highlighting for string literals or other specific code constructs. |
| Code Teal | `#096e72` | `--color-code-teal` | Syntax highlighting for certain keywords or declarations within code blocks. |

## Tokens — Typography

### IBM Plex Mono — Code blocks and monospaced text. The tight letter-spacing gives code a compact, precise appearance. · `--font-ibm-plex-mono`
- **Substitute:** monospace
- **Weights:** 400, 600
- **Sizes:** 14px, 16px, 18px, 48px
- **Line height:** 1.00, 1.10, 1.80
- **Letter spacing:** -0.021em
- **Role:** Code blocks and monospaced text. The tight letter-spacing gives code a compact, precise appearance.

### Rubik Variable — General UI text, headings, buttons, and body copy. Variable weights and fine letter-spacing adjustments provide legibility and a crisp, modern feel across different sizes. · `--font-rubik-variable`
- **Substitute:** sans-serif
- **Weights:** 400, 500, 600
- **Sizes:** 12px, 13px, 14px, 16px, 18px, 20px
- **Line height:** 1.00, 1.20, 1.50, 1.65, 1.78, 1.80
- **Letter spacing:** 0.016em (for 12px), 0.038em (for 13px), 0.056em (for 14px)
- **Role:** General UI text, headings, buttons, and body copy. Variable weights and fine letter-spacing adjustments provide legibility and a crisp, modern feel across different sizes.

### Type Scale

| Role | Size | Line Height | Letter Spacing | Token |
|------|------|-------------|----------------|-------|
| caption | 12px | 1.78 | 0.016px | `--text-caption` |
| body | 14px | 1.5 | 0.056px | `--text-body` |
| body-lg | 16px | 1.5 |  | `--text-body-lg` |
| subheading | 18px | 1.2 |  | `--text-subheading` |
| heading | 20px | 1.2 |  | `--text-heading` |
| display | 48px | 1.1 | -0.96px | `--text-display` |

## Tokens — Spacing & Shapes

**Density:** comfortable

### Border Radius

| Element | Value |
|---------|-------|
| cards | 8px |
| buttons | 4px |
| default | 4px |

### Shadows

| Name | Value | Token |
|------|-------|-------|
| Code Editor Card | `0px 1px 3px rgba(0, 0, 0, 0.1), 0px 1px 2px rgba(0, 0, 0, 0.06)` | `--shadow-code-editor-card` |

### Layout

- **Section gap:** 64px
- **Element gap:** 3-16px

## Components

### Code Editor Card
### npm Install CTA with Badge
### Nav Button Group
### Primary Heading
**Role:** Hero section titles

Uses 'Text Jet' (#111111) text color, IBM Plex Mono, 48px size, 600 weight, and 1.00 line height, creating a bold, assertive primary statement.

### Nav Button Default
**Role:** Secondary navigation and utility buttons

Background 'Page White' (rgba(255, 255, 255, 0.8)), text 'Text Graphite' (rgba(26, 26, 46, 0.6)), border 'Border Ash' (rgb(232, 232, 242)), 4px border radius with 4px 0px 0px 4px for left grouping and 0px 4px 4px 0px for right. Padding is 1px top/bottom, 9-10px left/right. Uses Rubik Variable 400 weight.

### Nav Button Solitary
**Role:** Standalone secondary actions or filters in header.

Background 'Page White' (rgba(255, 255, 255, 0.8)), text 'Text Graphite' (rgba(26, 26, 46, 0.6)), border 'Border Ash' (rgb(232, 232, 242)), 4px border radius. Padding is 0px top/bottom, 12px left/right. Uses Rubik Variable 400 weight.

### Text Link Button
**Role:** Inline textual actions

Transparent background, text 'Primary Violet' (rgb(48, 48, 85)), no border radius. Uses Rubik Variable 400 weight with no explicit padding, relying on surrounding text flow.

### Code Editor Card
**Role:** Display of structured code examples

Background 'Page White' (#ffffff) with a subtle shadow, 8px border radius, and text styled with 'IBM Plex Mono'. Contains syntax highlighting with 'Code Rose' (#984e4d), 'Code Magenta' (#8844ae), 'Code Sky' (#5196b3), 'Code Indigo' (#3b61b0), and 'Code Teal' (#096e72).

### npm install Button
**Role:** Call to action for installation

Text 'Primary Violet' (rgb(48, 48, 85)) on a transparent background, prefixed with a 'Text Slate' (rgb(118, 118, 130)) chevron icon. Acts as a simple, actionable link.

## Do's and Don'ts

### Do
- Prioritize 'Primary Violet' (#303055) for all interactive clickable elements to maintain brand identity.
- Use 'Page White' (#ffffff) as the primary background for all page sections and elevated components.
- Apply 'Border Ash' (#e8e8f2) for subtle borders on all secondary buttons and input fields to define interactive regions subtly.
- Ensure headings use 'Text Jet' (#111111) to establish clear hierarchy and strong visual anchors.
- Employ IBM Plex Mono for all code displays, capitalizing on its fixed-width and precise letter-spacing of -0.021em.
- Maintain a default border-radius of 4px for all buttons and interactive elements, and 8px for cards and containers.
- Utilize the full range of custom colors for syntax highlighting within code blocks to ensure legibility and structural clarity.

### Don't
- Avoid using highly saturated, non-brand colors outside of code syntax highlighting.
- Do not use letter-spacing values less than -0.021em or greater than 0.056em for any text element.
- Do not introduce strong, intrusive shadows; rely on 'Page White' backgrounds on 'Border Ash' for subtle elevation.
- Avoid mixed-case headings; all primary headings are sentence case with a strong weight.
- Do not use large images or prominent graphical elements that disrupt the clean, text-heavy layout.
- Never use `background-color: transparent` for primary call-to-action buttons; solid backgrounds are preferred for prominence.

## Imagery

The site primarily uses code snippets and icons as its visual language. Photography is absent. Illustrations are minimal and functional, focused on conveying technical concepts rather than decorative flourishes. The code snippets, particularly the 'Code Editor Card', are themselves a central visual element, colorized using the accent palette for enhanced readability and visual interest. Icons are either monocolor (Text Slate, Primary Violet) or outlined, maintaining a lightweight and functional aesthetic. Visuals serve an explanatory role, illustrating product functionality directly and minimally, rather than creating atmosphere.

## Layout

The page maintains a centered, max-width layout, relying on ample white space. The hero section prominently features a split layout with a large, bold 'IBM Plex Mono' headline on the right and a 'Code Editor Card' on the left, demonstrating the product's core functionality upfront. Content generally follows a vertical stacking of sections, with consistent padding. Navigation is handled by a standard top bar with right-aligned utility links and branding on the left. The overall density is comfortable, prioritizing readability and systematic information presentation.

## Agent Prompt Guide

### Quick Color Reference
- Text: #111111 (Jet)
- Primary CTA: #303055 (Violet)
- Background: #ffffff (White)
- Border: #e8e8f2 (Ash)
- Secondary Text: #403f53 (Graphite)

### 3-5 Example Component Prompts
1. Create a primary heading: 'For whatever you build.' using IBM Plex Mono, weight 600, size 48px, line height 1.00, color #111111. Position it prominently in a hero section.
2. Construct a button group for header navigation: two buttons. Left button: background rgba(255, 255, 255, 0.8), text rgba(26, 26, 46, 0.6), border #e8e8f2, border-radius 4px 0px 0px 4px, padding 1px 10px 1px 10px. Right button: same style but border-radius 0px 4px 4px 0px, padding 1px 9px 1px 10px. Both use Rubik Variable 400 weight.
3. Design a code editor card: background #ffffff, border-radius 8px, box-shadow light elevation. Inside, display code using IBM Plex Mono, 14px, 400 weight, letter-spacing -0.021em, with various syntax colors: #984e4d, #8844ae, #5196b3, #3b61b0, #096e72.
4. Generate an 'npm install' prompt: Text 'npm i sst' in rgb(48, 48, 85) using Rubik Variable 400 weight, preceded by a chevron icon in rgb(118, 118, 130).
