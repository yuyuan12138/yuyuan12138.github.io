# Publishing a post — runbook

## What this automates + authorization basis
Publishing a new post or site change to <https://yuyuan12138.github.io>. The
`gh-pages` branch root is the published document root: **commit + push IS the
deploy**. Authorized by the repo owner for this repo (it is their own site);
`git push` happens only at step 8 — it is a remote, user-visible mutation.

## Preconditions
- On branch `gh-pages`, working tree clean (`git status`).
- `python3` available; a temp build dir (e.g. `/tmp/blog-build`).
- For a new post: key, title, date, `disp`, url, tags, hue and one-line `desc`
  already decided.

## Procedure
1. **Add the `POSTS` entry** in `tools/build_blog.py:29` with key, title, date,
   `disp`, url, tags, hue, `desc`.
   Success: `python3 -c "import ast; ast.parse(open('tools/build_blog.py').read())"` exits 0.
2. **Author the prose HTML**:
   - default: add a `PROSE["<key>"]` HTML string (`tools/build_blog.py:52`); or
   - hand-authored page (essay pattern): create `content/<url>/index.html` and
     add its `(src, dst)` line to the copy list (`tools/build_blog.py:241-250`).
   Success: the key resolves in both `POSTS` and `PROSE`/content.
3. **Record the revert point**: note current HEAD (`git rev-parse --short HEAD`)
   in the dispatch record BEFORE building or committing.
4. **Build to a temp dir**: `python3 tools/build_blog.py /tmp/blog-build`.
   Success: prints "Built. Files:" and lists the new article path.
5. **Hand-edit the lists** (never done by the build): add the post's
   `<li class="post …">` row to BOTH `content/index.html` and
   `content/archives.html`, newest first. ⚠ These files are copied
   byte-identical — skipping this leaves the post undiscoverable from
   homepage/archives (verified 2026-11-11: the pi-agents post is absent from
   both, `content/index.html:28-46`, `content/archives.html:36-54`).
6. **Rebuild and sync into the repo root**:
   `python3 tools/build_blog.py /tmp/blog-build && rsync -a /tmp/blog-build/ ./`
   The sync never deletes: remove retired paths by hand (`git rm -r <path>`).
7. **Verify the diff is confined**: `git status --short` + `git diff --stat`
   show ONLY expected site files (root output, `content/`, `tools/`; `design/`
   only if the change is a design change). FAIL → do not commit; see Failure
   paths.
8. **Commit + push (the deploy)**: `git add` explicit paths; descriptive
   message; `git push origin gh-pages`.
9. **Post-publish check** (after the Pages build, ~1 min):
   `curl -s https://yuyuan12138.github.io<post-url>` shows the title; homepage
   and `/archives/` list it; `curl -s .../atom.xml | grep -c '<entry>'` grew.

## Verification
- New article URL returns HTTP 200 with the post title.
- Homepage AND `/archives/` list the post; the generated tag page lists it;
  `atom.xml` has the new entry.
- Evidence kept in the dispatch record (`project-space/work/<date>-<slug>/`):
  commit id, curl checks, `git diff --stat` summary.

## Failure paths
| Symptom | Diagnosis | Remediation |
|---|---|---|
| Post live but absent from homepage/archives | Step 5 skipped — lists are hand-authored, byte-identical copies | Edit `content/index.html` + `content/archives.html`, rebuild, re-sync, commit, push |
| Build crashes on the new post | POSTS/PROSE key mismatch, or missing essay copy line (KeyError traceback) | Fix the key or add the copy line; rebuild |
| Step 7 diff contains unexpected files | Stale retired output still in root, or OUT accidentally pointed at repo root | `git checkout -- <unintended paths>`; never build with OUT = repo root; explicitly `git rm` retired paths |
| Live site not updating after push | GitHub Pages build pending or failed | Check the repo's Actions/deploy status; wait or re-run the deploy; never re-push blindly |

## Escalation (hand back to a human)
- Push only on the owner's publish instruction for that change.
- Unknown outcomes (push rejected, Pages build failing, diff surprises) → stop
  and report; never auto-retry a push or rewrite history.
