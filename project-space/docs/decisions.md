# Decision log (ADR-style)

Format: Context → Decision → Consequence, ≤10 lines per entry, with date and
source pointers. Append-only — entries are never edited after being written;
newest at the bottom. No decision here is re-litigated in docs work — live
files own the behavior.

---

## ADR-001 — Editorial design language: 624px serif column, no JavaScript
**Date**: 2026-11-05 · **Source**: `design/DESIGN.md:29-50`, `design/style.css:121`, commit `d4c6643` ("redesign: editorial static site (designer-approved)")
- **Context**: The Jekyll-era default theme looked generic; the site needed a designer-approved reading experience that works on any device without client-side machinery.
- **Decision**: One reading-first column, `max-width: 39rem` (624px ≈ 70ch of 18px serif), serif for voice with sans labels and mono dates, per-post hue accents, `clamp()` fluid type — and **no JavaScript** anywhere.
- **Consequence**: The entire look is CSS + hand-authored HTML; every future page must stay inside the DESIGN.md system (see ADR-002 for how prose is produced).

## ADR-002 — Hand-authored HTML over a markdown pipeline
**Date**: 2026-11-05 · **Source**: `tools/build_blog.py` (`POSTS` :29, `PROSE` :52, byte-identical copies :241-250), commit `c097998` ("project home: README, design artifacts, content sources, build script")
- **Context**: With a handful of posts and a fixed design system, a markdown toolchain (Hexo/Jekyll) adds dependencies, frontmatter conventions and template drift for little gain.
- **Decision**: No markdown pipeline. Prose is hand-authored HTML — either pages under `content/` (copied byte-identical by the build, essay pattern) or `PROSE` HTML strings in `tools/build_blog.py` keyed by a `POSTS` entry.
- **Consequence**: Publishing means editing Python + HTML by hand (`docs/runbooks/publishing.md`); the build never touches homepage/archives lists, so a skipped hand-edit hides the post from discovery (observed: ADR-003's sibling finding in the work record).

## ADR-003 — Site v2 retires boilerplate posts; typos fixed in place
**Date**: 2026-11-05 · **Source**: commit `6c9ac12` ("retire boilerplate posts; fix 9 typos (spelling only)"); retirement rationale in the POSTS comment of `tools/build_blog.py`
- **Context**: Two leftover posts — "Hello World" (Hexo boilerplate) and "Welcome to my blog" (Jekyll-era boilerplate) — carried no content, and surviving posts had spelling errors.
- **Decision**: Remove both boilerplate posts everywhere and emit **no redirects** for them (their URLs 404 by design, unlike redesigned-slugs which get redirect stubs). Fix the 9 typos as spelling-only edits, no rewording.
- **Consequence**: Old boilerplate URLs intentionally 404; content corrections remain confined to spelling unless a future ADR supersedes this.
