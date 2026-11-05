# DESIGN.md — redesign of yuyuan12138.github.io

Designer: designer role. Date: 2026. Scope: presentation only. Content of all
posts is the author's, verbatim (including its typos — see §9).

## 0. Diagnosis of the current site (why it looked neglected)

1. **Flat hierarchy.** Site title "My Blog" is a placeholder; post titles,
   dates and body text sit in nearly the same size/weight. The article page
   prints the title twice (`h1` + an identical `h2` re-rendered from the
   Markdown body, e.g. `<h2 id="Why-smart-people...">`).
2. **Fake information.** The sidebar shows the *same* categories
   ("LLM", "announcement") and tags ("github-pages", "jekyll", "welcome") on
   every page — global Hexo boilerplate, not per-post metadata. A 10px "Tag
   Cloud" widget, a "Share" link and a Google site-search box compete with the
   actual content.
3. **URL rot.** Slugs duplicate the date
   (`/2026/02/16/2026-02-16-why-smart-people-always-lose-at-their-20-age./`)
   and one contains a trailing dot, which breaks Windows checkouts.
4. **No system.** Default-theme gray-on-white, table-gutter code blocks, no
   spacing rhythm, no color logic.

Information invariant (unchanged by the redesign): the four posts' full text,
their dates, the one real outbound reference (ACL Anthology PDF link), and
clean public URLs.

## 1. Layout system

- One column, reading-first. Text column `max-width: 39rem` (624px ≈ 70ch of
  18px serif — inside the 45–75ch band). No fixed widths; the column is a max,
  phones get the full width minus 1.25rem padding. No sidebar anywhere.
- **Grouping by whitespace, not lines**: year label → list; inter-item gap
  0.625rem; section gaps ≥ 2.25rem (group spacing ≈ 2× item spacing).
- No cards, no shadows, no border-radius (bands are square-edged rectangles —
  they read as editorial section bands, not UI cards).
- Mobile-first: base styles are the phone layout; the only breakpoint-like
  behavior is `clamp()` fluid type. No JavaScript.

## 2. Type scale (1.25–1.5× jumps, four levels)

| Level | Font | Size | Weight | Use |
|---|---|---|---|---|
| Display | serif | clamp(1.625–2.25rem) | 700 | article title |
| H1 / wordmark | serif | clamp(1.5–1.875rem) | 700 | site name, page titles |
| List title | serif | clamp(1.1875–1.375rem) | 600 | post titles in lists |
| Body | serif | 1.125rem / 1.7 | 400 | article prose |
| Meta | mono | 0.8125rem | 400 | dates (mono: numerals align) |
| Label | sans | 0.6875rem, caps, 0.08em | 600 | tag names, nav labels |

Two families total (serif for voice, sans for UI) + mono for dates/code.
Stacks are system-only: `Charter, Iowan Old Style, Palatino Linotype, Georgia,
serif` / `-apple-system, … Segoe UI, Helvetica, Arial, sans-serif` /
`"SF Mono", … Menlo, Consolas, monospace`. Everything left-aligned; no
justification; emphasis by weight only.

## 3. Color system — color as wayfinding, not decoration

One ink + one meta gray + one link blue, plus **five structural hues** assigned
to tags by a documented hash:

`hue = [214, 152, 24, 262, 190][ sum(charcodes(tag)) % 5 ]`

| Tag | Hue | Light gutter | Light band (~4% tint) | Dark gutter | Dark band |
|---|---|---|---|---|---|
| `llm` | 214 blue | `#2259a0` | `#f4f7fb` | `#6997d3` | `#212830` |
| `healthcare` | 152 green | `#22a065` | `#f4fbf8` | `#69d3a2` | `#213029` |
| `deep-learning` | 24 orange | `#a05422` | `#fbf7f4` | `#d39369` | `#302721` |
| `meta` | 262 purple | `#5022a0` | `#f6f4fb` | `#9069d3` | `#272130` |
| `essay` | 190 teal | `#228ba0` | `#f4fafb` | `#69c2d3` | `#212e30` |

Hue appears **only as structure**: a 3px left gutter on list/nav rows, a ~4%
background band, and a 3.5rem accent rule under the article title. Hue never
colors text, so text contrast is hue-independent. This is the same discipline
approved in the email-digest v3 review ("颜色有点少，分栏不够明显" → 3px
colored gutters + ~4% tinted bands, hash-hue accents).

### Contrast ratios (computed, WCAG)

Light mode (`--paper #ffffff`):

| Foreground | Background | Ratio | Bar | Pass |
|---|---|---|---|---|
| ink `#1f1f1f` | paper | **16.48** | 4.5 | ✓ |
| ink | worst tint (`#f6f4fb`) | **15.11** | 4.5 | ✓ |
| meta `#575757` | paper | **7.23** | 4.5 | ✓ |
| meta | worst tint | **6.62** | 4.5 | ✓ |
| link `#1d4ed8` | paper | **6.70** | 4.5 | ✓ |
| gutters (5 hues, min) | paper | **3.34** (`#22a065`) | 3.0 non-text | ✓ |

Dark mode (`prefers-color-scheme`, `--paper #14161a`):

| Foreground | Background | Ratio | Bar | Pass |
|---|---|---|---|---|
| ink `#e8e6e1` | paper | **14.52** | 4.5 | ✓ |
| ink | worst dark tint (`#213029`) | **11.08** | 4.5 | ✓ |
| meta `#a8a8a4` | paper | **7.59** | 4.5 | ✓ |
| meta | worst dark tint | **5.79** | 4.5 | ✓ |
| link `#8ab4f8` | paper | **8.59** | 4.5 | ✓ |
| gutters (5 hues, min) | paper | **4.44** (`#9069d3`) | 3.0 non-text | ✓ |

Note: the digest's 2.81:1 meta-gray bug class is closed — meta gray is ≥6.62:1
on every background in both modes, verified per tint.

## 4. Homepage (`/index.html`)

Masthead: wordmark (name) → one-line byline → text nav (Posts / Archives).
Then one year group (`2026`, mono label) containing the post list. Each row:
date (mono) on the left, tag (small caps) on the right, serif title below, all
inside the tag's tinted band with its 3px gutter. Newest first. The row itself
is the link — one target per row, no card chrome.

## 5. Article page (`/:year/:month/:day/:slug/`)

Masthead shrinks (wordmark + nav, no byline). Article head: meta row (date ·
tag) → serif display title → 3.5rem accent rule in the post's hue (the page's
echo of its list gutter). Prose: serif 18px/1.7, paragraph spacing 1.375rem,
no drop caps, no pull quotes — the essay is one voice, it doesn't need
furniture. Footer: prev/next rows, each carrying **the neighbor post's** hue
(color tells you which tag you're about to enter), then "All posts".
Duplicate in-body title heading from the old Hexo render is dropped (pure
duplication, zero information).

## 6. Tags and dates

- **Tags** are the only taxonomy (no categories). The old "tags" were global
  boilerplate, so a minimal honest taxonomy is *proposed* from each post's
  actual content — implementer puts these in front matter:
  - Autodiff → `deep-learning`
  - Thinking of LLM of AI Patient Simulation → `llm`, `healthcare`
  - Why smart people always lose at their 20 age. → `essay`
  - Hello World → `meta`  (Welcome to my blog → `meta`)
- Homepage shows the primary tag (first listed); archives show all tags with
  counts. Tag → hue comes from the hash above, so new posts are colored
  consistently without design work.
- **Dates**: ISO in markup (`<time datetime>`, machine-readable), compact
  "Feb 16" in year-grouped lists, full "Feb 16, 2026" on article pages. Year
  lives in the group heading, not repeated per row.

## 7. URL structure and redirect note

Clean slugs (`permalink: :year/:month/:day/:slug/`):

| Old path | New path |
|---|---|
| `/2026/01/20/2026-01-20-autodiff/` | `/2026/01/20/autodiff/` |
| `/2026/02/02/2026-02-02-thinking-of-llm-of-ai-patient-simulation/` | `/2026/02/02/ai-patient-simulation/` |
| `/2026/02/16/2026-02-16-why-smart-people-always-lose-at-their-20-age./` | `/2026/02/16/why-smart-people-lose-at-20/` |
| `/2026/05/04/hello-world/` | unchanged |

**Redirects (for the implementer, not implemented here):** GitHub Pages has no
server-side redirects. Options, in order of preference: (1) keep both URLs by
configuring Hexo `permalink`/`alias` generation so each old path emits a stub
page with `<meta http-equiv="refresh" content="0; url=NEW">` plus a canonical
link; (2) if the site is Jekyll, the `jekyll-redirect-from` gem does the same;
(3) worst case, leave the old slugs untouched — the design does not depend on
slug text. Do *not* drop the trailing-dot path silently; it is linked from the
old Atom feed. Old `/tags/*`, `/categories/*`, `/archives/:year/:month/` paths
should also get stub redirects to `/archives/`.

## 8. Slop checklist (run against this output)

- Gradient banners — **none** (zero gradients anywhere).
- Emoji / per-heading icons — **none**.
- Pill-shaped keyword chips — **none**: tags are plain small-caps text; the
  tinted band + gutter carries the color, no rounded chips.
- Glassmorphism / layered shadows — **none** (zero box-shadows).
- Dashboard look / 3-column icon cards — **none**: one column, editorial list.
- Empty slogans ("赋能", "supercharge", triple parallel constructions) —
  **none**: byline is factual ("CS student. LLM agents, RL, algorithms."),
  labels are single words (Posts, Archives, Next, Previous).
- Decoration must serve information — the only color-bearing elements are
  wayfinding (gutter/band/rule = which tag am I in / entering) and states
  (hover band deepens on the linked row). Hairline rules appear only in the
  footer and blockquotes.
- Element-deletion test: removing any element (byline, rule, tag row) loses
  either identity or wayfinding, not redundancy; the design survives with
  masthead + list + prose alone.

## 9. Notes and escalations for the implementer

- **Content typos found in the essay (left verbatim, fix at source in the
  Markdown, not in templates):** "youhad" (missing space), "prasied",
  "take care too much", "eaiser", "frameword", "let fo", "unconfortable",
  "Real smarts", "why you stuck". The title's "at their 20 age." is the
  author's; kept in display, dropped from the slug.
- **"Welcome to my blog"** (2026-01-20) is Jekyll-era boilerplate on what is
  now a Hexo site, and contains a broken-looking markup dump. Recommend the
  user retire it; it is nonetheless included in the archive sketch so nothing
  silently disappears.
- "Hello World" is Hexo boilerplate — kept (newest post, user's call).
- "Ruojun Wang" comes from the old site's `article:author` meta; confirm with
  the user before launch (fallback: the GitHub handle).
- Hexo highlight: set `line_number: false` so code blocks render as plain
  `<pre>` (the stylesheet styles plain `pre`; the old table-gutter markup is
  not supported).
- The stylesheet covers `h2/h3`, lists, blockquote, inline code, and `pre` so
  the shorter posts (the LLM post's `<ol>` + References section, future code
  posts) render correctly with the same CSS.
