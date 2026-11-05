# yuyuan12138.github.io

Source and deploy repo for the personal blog at <https://yuyuan12138.github.io>
(GitHub Pages, served from the `gh-pages` branch — the repo's only branch).

## Layout

- `content/` — hand-authored source pages (homepage, archives, essay article).
- `design/` — the editorial redesign: `DESIGN.md` (design spec) and `style.css`.
- `tools/build_blog.py` — static site builder: generates article pages, tag
  pages, 404, old-slug redirects and `atom.xml` from `content/`,
  `design/style.css` and the post data embedded in the script.
- Everything else at the repo root is **build output** (what GitHub Pages serves).

## Rebuild

    python3 tools/build_blog.py              # writes ./_site/
    python3 tools/build_blog.py /tmp/out     # or any output dir

## Deploy

Deploy = push to `gh-pages`: copy the build output into the root of a
`gh-pages` checkout of this repo, commit, and push. GitHub Pages serves it.
