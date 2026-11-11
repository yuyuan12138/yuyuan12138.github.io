# Work record — November redesign + Post v2 (retrofit record)

- **Date**: 2026-11-11 (UTC; documented work spans 2026-11-05 → 2026-11-09)
- **Task**: Editorial redesign of yuyuan12138.github.io, boilerplate retirement,
  project-home tooling, the pi-agents post + its v2 rewrite; project space
  bootstrapped retroactively around them
- **Dispatched-by**: coordinator conversation
- **Worker**: background subagent (project-space bootstrap dispatch)
- **Status**: delivered (retrofit record; every claim re-verified against git
  and files on 2026-11-11)

## Task brief
Create the project space per PiAgents `PROJECT-SPACE-STANDARD.md` under
`project-space/` (git-tracked, never emitted by the build): charter README,
ADR log for the November decisions, a publishing runbook, and one record for
the Nov redesign + Post v2. Verify every claim against real files; stage
explicit new files only; one commit; no push.

## Delivered
- `project-space/README.md` — charter, status table, directory map, conventions
- `project-space/docs/decisions.md` — ADR-001 (design language), ADR-002
  (hand-authored HTML), ADR-003 (boilerplate retirement + typo fixes)
- `project-space/docs/runbooks/publishing.md` and `docs/runbooks/INDEX.md`
- `project-space/work/2026-11-11-nov-redesign-post-v2/RECORD.md` (this file)
- No live site file touched.

## Verification evidence
- **Not-served claim**: `tools/build_blog.py:238` wipes OUT; `:241-250` copies
  five named files from `content/`/`design/`; the rest of the script generates
  only known paths; `grep project-space tools/build_blog.py` → no match.
  Fresh build reproduced exactly the 24 output files; `diff -rq` vs repo root
  → zero differing site files (only extra root file: pre-existing `README.md`).
- **Design claims**: `design/DESIGN.md:29-37` (39rem/624px column, 18px serif,
  no JavaScript), `design/style.css:121`; commit `d4c6643` "designer-approved".
- **Post count**: the task brief said "5 posts"; verified **4 posts** (`POSTS`,
  `tools/build_blog.py:29-45`; `atom.xml` has 4 entries) **+ 1 product page**
  (`/piagents/`, commit `ea90831`) = 5 published content pages. Brief corrected
  here rather than restated.
- **Boilerplate retirement**: commit `6c9ac12` (full id `6c9ac12e7e1e…`),
  "retire boilerplate posts; fix 9 typos (spelling only)"; no-redirect rule per
  the POSTS comment in the build script.
- **Post v2**: commits `9a5d952` (rewrite as incident-driven narrative),
  `520a6da` (artifact rebuild), `0bbe590` (stray-text fix + product page).
- **NEW FINDING**: the pi-agents post is absent from the homepage and archives
  — `content/index.html:28-46` and `content/archives.html:36-54` list only the
  3 older posts; root `index.html` is byte-identical to `content/index.html`.
  The post is reachable only via `/tags/llm/`, `atom.xml`, article nav, or its
  direct URL — the runbook's step-5 warning exists because of exactly this.

## Open items
- Hand-add the pi-agents row to `content/index.html` + `content/archives.html`,
  rebuild, publish (runbook steps 5–9) — awaits owner go-ahead.
- `architecture.md` intentionally not created: `design/DESIGN.md` (198 lines)
  serves as the design/architecture doc (retrofit rule: index-in-place).
- No `docs/postmortems/` — no qualifying incident recorded for this project.
