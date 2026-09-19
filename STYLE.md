# STYLE — visual direction for the HRV page

**Companion to `HANDOVER.md`.** That doc defines what the page says; this one defines how it looks. Where they disagree, HANDOVER wins on content and this wins on presentation.

**Amendment to HANDOVER §7:** the figure reference is now **`image3.jpeg`**, not `image.jpeg`. Use image3.

---

## 1. Reference images — read them before writing any CSS

Both are in your working directory. Open them first; the written spec below describes intent, but the images are the source of truth for form.

| File | Governs |
|---|---|
| `image3.jpeg` | the central human figure — proportions, pose, line weight |
| `image2.jpeg` | the speech bubble — tail shape, border weight, corner geometry |

If either file is missing or unreadable, stop and say so rather than inventing a substitute.

---

## 2. The Lichtenstein brief

Anna wants Roy Lichtenstein. Take that as a **technique vocabulary**, not a canvas to copy:

- **Ben-Day dots** — regular halftone dot grids as fill, not gradients
- **Heavy black contour lines** — uniform weight, closed shapes, no tapering
- **Flat unmodulated color fills** — no soft shading, no drop shadows, no glows
- **Comic panel structure** — thick-bordered rectangular panels, hard gutters
- **Speech balloons with pointed tails** — see §6
- **Occasional oversized display type** as a graphic element

**Build the style from those techniques. Do not reproduce any specific Lichtenstein painting**, and do not use his titles, his source-comic imagery, or a recognisable figure from his work — this repo will be public under Anna's name, and "derived from a technique" and "a copy of a canvas" are very different things to have on a portfolio. The figure comes from `image3.jpeg`; the dots, lines and balloons are generic printing techniques anyone may use.

**Two places the brief fights itself — resolve them this way:**

1. **Lichtenstein is light-ground; this page is dark.** Treat it as a comic panel printed on black newsprint, not as a white canvas with the lightness inverted. Keep the black contour lines black — do not flip them to white. Let the dark ground read as the gutter between panels, and let panels sit on it as raised surfaces.
2. **Lichtenstein's palette is red/yellow/blue; the HRV scale is green-dominant.** The accent colors are set by the data (§4) and are not negotiable to fit the style. So the pop-art identity has to be carried by **form** — dots, contours, panel borders, balloon geometry — not by hue. Blue survives only as static, non-data chrome: the background halftone field (§3), panel rules, the figure's line work. Blue never encodes a value.

---

## 3. Dark theme tokens

Warm near-black ground, newsprint-white ink. All ratios below measured, not estimated.

```css
:root[data-theme="dark"], :root:where(:not([data-theme="light"])) {
  --ground:       #0A0A0A;  /* page background — near-black */
  --panel:        #1C1A18;  /* comic panel surface */
  --ink:          #0A0908;  /* contour lines — stays BLACK on dark */
  --paper:        #F2EDE4;  /* primary text, newsprint white — 15.9:1 */
  --paper-muted:  #A8A29A;  /* secondary text — 7.3:1 */
  --rule:         #000000;  /* panel borders */
  --benday-blue:  #0057B8;  /* background halftone — Lichtenstein blue */
}
```

### The background halftone

The page ground is black overlaid with a **fixed blue Ben-Day dot field** running edge to edge. `#0057B8` at 50% alpha over black resolves to `#002C5C` — **1.51:1 against the ground**. That is the target: present as texture, invisible as content. Paper-white text over a dot still measures 11.9:1, so the field never threatens legibility.

Implement as a single fixed-position pseudo-element behind everything, not as a `background-image` on `body` (which tiles against the scroll and moirés):

```css
body::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: -1;
  background:
    radial-gradient(circle at center,
      color-mix(in srgb, var(--benday-blue) 50%, transparent) 1.4px,
      transparent 1.5px)
    0 0 / 10px 10px;
  pointer-events: none;
}
```

Keep the pitch at or above 10px. Below that it aliases badly on non-retina displays and shimmers on scroll.

**The two dot systems must not be confused.** This is the one thing to get right:

| | Background field | Data dots (§4) |
|---|---|---|
| Color | blue, fixed | HRV band accent |
| Pitch | 10px, **never changes** | 6–14px, **encodes the band** |
| Contrast | ~1.5:1, recedes | high, demands attention |
| Where | behind everything | inside the figure's torso only |

If the background field is loud enough to compete, the density encoding stops being readable and the accessibility fallback in §4 is dead. When in doubt, make the background dimmer.

Panels sit **opaque** on top of the field (`--panel`, no transparency) so the dots run behind them, not through them — that's what makes the panels read as printed objects laid on a dotted sheet.

Ship a light theme too — a white-ground comic panel is the more natural Lichtenstein, and having both proves the theming was designed rather than defaulted. Dark is the default.

**Contour lines stay black in both themes.** A white outline is not this style.

---

## 4. HRV accent bands

Anna's bands, with hexes chosen and validated against the `#141312` ground:

| HRV | Band | Fill | vs ground | Text variant | vs ground |
|---|---|---|---|---|---|
| 130+ | forest green | `#1F8F45` | 4.48:1 | `#35C066` | 7.85:1 |
| 110–129 | bright green | `#5CCB3E` | 8.90:1 | (same) | — |
| 90–109 | yellow | `#FFD400` | 12.96:1 | (same) | — |
| 70–89 | orange | `#F4761B` | 6.59:1 | (same) | — |
| <70 | red | `#CC2222` | 3.38:1 | `#E85C50` | 5.37:1 |

**Use the fill hex for large areas — dots, fills, thick strokes. Use the text variant whenever the color carries text or a stroke under 2px.** Forest green and red both fall below 4.5:1 as fills; at small sizes they will be unreadable. This is the one place where the literal "forest green" gets brightened, and it's a legibility requirement, not a style preference.

Deliberate deviations, both fine, both worth a line in the README:

- `#FFD400` sits well above the usual dark-mode lightness ceiling. A muted yellow is not a pop-art yellow; it passes contrast comfortably, so it stays.
- `#CC2222` as a fill is a low-contrast alarm color. Acceptable because red is always paired with the number and the band label, never used alone.

### The colorblindness problem — this one needs fixing, not noting

I ran the five bands through a CVD validator against the dark ground. Normal vision and contrast both pass (worst pair ΔE 17.5). **Color-vision deficiency does not:** bright green ↔ orange separate by only ΔE 4.2 under deuteranopia, where 8 is the floor. Roughly 1 in 12 men cannot tell a 115ms reading from an 85ms one by color.

This is a property of any green→yellow→orange→red ramp, not of these particular hexes — I tested several and none clear it. So the ramp needs a **second, non-color encoding channel**, and Lichtenstein hands you a perfect one for free:

**Ben-Day dot density encodes the same information as hue.**

| Band | Dot diameter / pitch | Reads as |
|---|---|---|
| 130+ | 2px / 14px | sparse, open, calm |
| 110–129 | 3px / 12px | |
| 90–109 | 4px / 10px | |
| 70–89 | 5px / 8px | |
| <70 | 6px / 6px | dense, crowded, loud |

Density rises as HRV falls. Now the state is legible in greyscale, under any CVD, and in forced-colors mode. Implement as a CSS `radial-gradient` background whose size and dot radius are driven by custom properties, so one class swap changes both channels together.

Additionally: **the numeric HRV value and the band label are always on screen.** Never state the band by color alone.

---

## 5. Applying the accent

One HRV value drives the whole page. On change, update a single `data-band` attribute on `<body>` and let CSS cascade — don't set colors imperatively in JS.

```html
<body data-band="high">   <!-- high | good | mid | low | poor -->
```

What the accent touches: the hero HRV number, the dot fill inside the figure's torso, the connector lines from figure to factors, the active slider track and thumb, the speech bubble border. What it must **not** touch: body text, panel borders (always black), the figure's contour lines (always black), axis and grid work.

Transition color over ~240ms ease-out. Dot density should snap rather than tween — a halftone screen that morphs looks like a rendering bug.

---

## 6. The speech bubble

Match `image2.jpeg` for geometry. Constants regardless:

- Solid `--paper` fill, **4px black border**, hard corners or a tight radius — never a soft pill
- A **pointed triangular tail** with the same 4px border, aimed at the figure's head, repositioning when the bubble moves
- Text in black, not paper-white — the bubble is a light object on a dark page
- Border takes the **band accent** color; fill stays paper
- Comic lettering: uppercase, slightly condensed, generous letter-spacing. `Bangers`, `Anton` or similar for display; **never Comic Sans**
- The `n` and confidence tier (HANDOVER §6) sit in a small footer strip inside the bubble, lowercase, muted — the hedge is visible without shouting
- Low-confidence statements: swap the solid border for a **dashed** one. Second channel again; don't rely on a color or opacity shift
- Enter with a 120ms scale-from-0.96 + fade. No bounce, no spring

---

## 7. The figure

Trace `image3.jpeg` to **inline SVG paths** — do not embed the JPEG, do not trace to a bitmap.

- Uniform black contour, 3–4px, `stroke-linejoin: round`, all shapes closed
- Torso filled with the Ben-Day dot pattern in the current band color — this is the page's main color surface, the thing that visibly changes as sliders move
- Everything else flat `--paper` or left unfilled
- Factor anchors: head (sleep), chest (HRV readout), gut (alcohol), limbs (strain, workouts)
- Connector lines from anchors to their control: 2px black, with a 1px accent line inset — stroke weight scales with that factor's effect size, so sleep and alcohol are visibly heavier than strain and consistency
- The "signal, not lever" readings (RHR, respiratory rate) sit **outside** the radial ring, in their own panel, visually quieter — no connectors to the body

Below ~700px the radial layout collapses to a vertical stack: figure, then bubble, then controls. Don't try to preserve the ring at phone width.

---

## 8. Typography

- **Display** (hero HRV number, band label, bubble text): a condensed poster face — `Anton`, `Bangers`, or similar. Uppercase.
- **Body / data** (statements, stats, methodology): a plain grotesque — `Inter`, system stack. Mixed case. The statistical content must stay readable; do not set paragraphs in comic lettering.
- Hero HRV number: very large, 4–6rem, accent-colored, with `ms` in a much smaller muted weight.
- Panel headings get a thick black underline rule, like a comic caption box.

The split matters: pop art for the chrome, plain type for the numbers. A page where the caveats are set in Bangers reads as a joke rather than as analysis.

---

## 9. Don'ts

- No gradients as fills. Dots are the only texture.
- No drop shadows, no glass, no blur, no glow.
- No rounded-everything card UI — this is panels and rules.
- No emoji as icons.
- No color-only state anywhere.
- No animated dot patterns or parallax.
- Do not let the pop-art treatment reach the methodology and caveats sections — those stay sober. The tension between a loud page and a careful footnote is the point.

---

## 10. Acceptance checklist

- [ ] Figure traced from `image3.jpeg` as SVG paths; bubble geometry matches `image2.jpeg`
- [ ] All five bands render correct fill + dot density; band changes drive one `data-band` attribute
- [ ] Screenshot at each band, greyscaled — all five still distinguishable
- [ ] Deuteranopia simulation — all five still distinguishable (via dots, not hue)
- [ ] No text below 4.5:1 against its own background; forest green and red use their text variants
- [ ] Contour lines black in both themes
- [ ] Background halftone reads as texture at arm's length, never as content; data dots still clearly dominant against it
- [ ] No moiré or shimmer when scrolling fast; check on a non-retina display or at 100% zoom
- [ ] Light theme present and deliberately stepped, not an inverted dark
- [ ] Phone width: no horizontal scroll, ring collapsed to a stack
- [ ] `prefers-reduced-motion` honored — color still changes, transitions don't
- [ ] Rendered and eyeballed at 360px, 768px and 1440px before calling it done
