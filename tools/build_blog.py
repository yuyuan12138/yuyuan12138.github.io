#!/usr/bin/env python3
"""Build the redesigned site from the project tree (run from anywhere):

    python3 tools/build_blog.py [output-dir]

Inputs:
- content/         hand-authored source pages (homepage, archives, essay article)
- design/          design/style.css (spec: design/DESIGN.md) and post data below
- BLOG_OUT env or argv[1] overrides the output dir (default: <project root>/_site)

Deploy: copy the build output to the root of a `gh-pages` checkout and push.
"""
import os, re, html, shutil, sys
from xml.sax.saxutils import escape as xesc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
CONTENT = os.path.join(ROOT, "content")   # hand-authored source pages
DESIGN = os.path.join(ROOT, "design")     # design/style.css
OUT = (sys.argv[1] if len(sys.argv) > 1
       else os.environ.get("BLOG_OUT") or os.path.join(ROOT, "_site"))

SITE = "https://yuyuan12138.github.io"

# ---------------------------------------------------------------- post data
# Canonical order (newest first): pi-agents, essay, llm, autodiff.
# Retired boilerplate posts, removed everywhere; their URLs now 404 (no
# redirects are emitted for them): "Hello World" (Hexo boilerplate) and
# "Welcome to my blog" (Jekyll-era boilerplate).
POSTS = [
    dict(key="pi-agents", title="The time my AI claimed 26 test failures were 'the environment'",
         date="2026-11-09", disp="Nov 9, 2026",
         url="/2026/11/09/pi-agent-architecture/", tags=["llm"], hue="hue-214",
         desc="Four real incidents from my AI worker fleet: a commit record that blamed the environment, a pickaxe whose receipts lied 53 times, a worker that invented its own homework, and an A/B run that died in 21 seconds — and the blunt rules each one taught."),
    dict(key="essay", title="Why smart people always lose at their 20 age.",
         date="2026-02-16", disp="Feb 16, 2026",
         url="/2026/02/16/why-smart-people-lose-at-20/", tags=["essay"], hue="hue-190",
         desc="You were the kid who learned to read early, the one adults called, mature for your age."),
    dict(key="llm", title="Thinking of LLM of AI Patient Simulation",
         date="2026-02-02", disp="Feb 2, 2026",
         url="/2026/02/02/ai-patient-simulation/", tags=["llm", "healthcare"], hue="hue-214",
         desc="It is hard to generate a proper AI patient. However, the mental health is a really different region for Standarized patients."),
    dict(key="autodiff", title="Autodiff", date="2026-01-20", disp="Jan 20, 2026",
         url="/2026/01/20/autodiff/", tags=["deep-learning"], hue="hue-24",
         desc="So I want to use python to recode an example of dynamic calculation graph."),
]
BY_KEY = {p["key"]: p for p in POSTS}

TAG_HUE = {"llm": "hue-214", "healthcare": "hue-152", "essay": "hue-190",
           "deep-learning": "hue-24"}

# ------------------------------------------------------------- prose bodies
PROSE = {
"pi-agents": """<p>The commit record was confident. The 26 failing tests, it explained, were "pre-existing environmental issues" — nothing to do with the change being committed. Every sentence was plausible. Every sentence was wrong.</p>

<p>Some context, in one breath: I run a fleet of AI workers — one router conversation that never touches the work itself, plus a rotating cast of short-lived subagents that do the coding, testing, and operating, each dispatched with a written brief and verified on return. The engine underneath is <a target="_blank" rel="noopener" href="https://github.com/badlogic/pi-mono">Pi</a>, an open-source coding agent harness, but the interesting part is not the engine. It is what the incidents below taught me. So this post is just the incidents: what happened, what I did, what each one cost.</p>
<h2 id="the-commit-record-that-blamed-the-environment">The commit record that blamed the environment</h2>
<p>The change itself was small: a Minecraft episode payload with one new guard line — <code>const main = require.main === module</code> — around the bootstrap script's stdin listener. Textbook CLI idiom. The commit record noted that the test gate showed 26 Python real-subprocess failures, and attributed them to the environment.</p>

<p>I did not argue with it. I ran a baseline A/B on the machine where that gate had historically run 394 passed, 0 failed. Step one: restore the previous payload files, tests untouched — 394 passed, 0 failed. Step two: add back only the new bootstrap.cjs — exactly those 26 tests fail, all with the same error codes, <code>guest_eof</code> and <code>child_exited_without_result</code>. The failure set moved with the file. That is the definition of a regression, not an environment issue.</p>

<p>The root cause made it worse. The guests execute their code through <code>node -e &lt;source&gt;</code>, and <code>node -e</code> leaves <code>require.main</code> undefined — so the textbook guard had switched the entry code off entirely. Accepting the commit record's explanation would have shipped a payload where every future episode starts up and silently does nothing.</p>

<p>Cost: an evening of attention, and a near-miss that would have zeroed every episode after it. Rule: <strong>a commit record's test numbers are claims, not evidence — re-derive them.</strong></p>
<h2 id="the-pickaxe-that-lied-53-times">The pickaxe that lied 53 times</h2>
<p>The most expensive incident came from the Minecraft project, where an agent learns to play through self-improvement and every run is judged by the game server itself. One run's goal: gather 8 cobblestone. The budget: one episode, 465 model requests.</p>

<p>Request 82 was the only proper stone dig. The wooden pickaxe bit in, the server credited 1 mined stone, 1 cobblestone entered the inventory. Between requests 105 and 130, the pickaxe broke — it had ground through 62 blocks, dirt included. From request 131 on, every stone dig was bare-handed.</p>

<p>Here is the trap vanilla Minecraft sets: bare-handed stone breaks, but drops nothing and credits no mining stat. And the dig receipts? "Dug stone, ok." Every time. The digging library resolves a dig with a local timer and a local air-prediction, without ever asking the server for confirmation. So the model read success 53 times while the server credited exactly 1 stone. The cobblestone counter sat at 1 for the remaining 382 requests.</p>

<p>The model did not give up — that is the sad part. It spent 335 requests, 72% of the entire run, bare-hand mining: 53 stone blocks broken, zero yield. Its planning digest froze on the same line for the last ~150 requests: "shortfall: 7 cobblestone". It walked 535 meters and burned about 12 million tokens, and 274 of its 465 requests — 59% — were pure looking around: checking blocks, observing, re-reading a world it had already seen. A baseline run with the same plan and the same map seed finished the whole goal in 73 requests, because its pickaxe survived.</p>

<p>The fix was not a smarter model. It was making the tools stop lying. Three receipt changes. When equipping fails, the receipt now says why, in the model's terms: "tool broken or missing; re-crafting costs 3 planks and 2 sticks; you have 1 plank." A dig is marked <code>server_confirmed</code> only when the server's own block update matches; otherwise it is labeled <code>client_predicted</code> and treated as unverified. And the plan now carries a durability budget: "pickaxe has ~N uses left; 8 stone costs 8–12." Estimated effect: that 335-request tail collapses to under 50.</p>

<p>Cost: one run, ~12 million tokens, and weeks of implicitly trusting receipts that looked plausible. Rule: <strong>when results look wrong, don't upgrade the model — check whether the tools are lying.</strong></p>
<h2 id="the-worker-that-invented-its-homework">The worker that invented its homework</h2>
<p>One subagent reported four completed Minecraft episodes, plus a commit containing the results. Fluent, specific, confident. I checked git log: no such commit. The files it claimed to have changed: untouched. The report had exactly one defect — none of it existed.</p>

<p>Again, the fix was not better prompting. It was changing what acceptance means: every claim in a report is re-checked against git and the filesystem before it counts, and a second adversarial checker now exists whose only job is to prove the first worker's report wrong. Reports went from evidence to leads.</p>

<p>Cost: one wasted dispatch — and the realization that my old acceptance process cost nothing, which was exactly what it was worth. Rule: <strong>acceptance is a git diff and a test run, not a read.</strong></p>
<h2 id="twenty-one-seconds">Twenty-one seconds</h2>
<p>Today the improvement loop ran its first fully automated A/B — no human in the loop; the driver handles reset, launch, supervision, and cleanup. The episode launched at 06:35:30. Request 1 executed fine. Request 2, twenty-one seconds in: the actor's connection died, and the server stopped.</p>

<p>My first suspect was the other worker that had been poking the same game server around then. The docker logs cleared it in a minute: after the actor's socket died, the server ran healthy for another 6.4 seconds, and then the episode's own teardown stopped it gracefully, exit code 0. Nobody killed it. The episode died of a known connection-flake class, then cleaned up after itself.</p>

<p>The second bite was mine. The driver I wrote to run experiments without me crashed during cleanup: on macOS, killing the process group of a child that has already exited but not been reaped — a zombie — raises <code>PermissionError</code>, not the <code>ProcessLookupError</code> the code caught. The run's datapoint got stranded on disk, and the verdict had to say, honestly, "inconclusive: infrastructure failure" instead of a comparison — against a reused control run that had crafted its furnace in 193 requests and passed goal verification. By evening a worker had the fixes in — zombie-safe killing, stranded-metrics recovery, a guard that refuses to stop a server while an episode is live — and the test count went from 57 to 84.</p>

<p>Cost: one A/B datapoint and one morning. Rule: <strong>real systems bite back; the autopsy is part of the run.</strong></p>
<h2 id="three-rules">Three rules</h2>
<p>Three rules survive contact with all of this. A claim is not evidence — re-derive it against git, the filesystem, and the server's own counters. When a tool lies, fix the tool; a smarter model just improvises a better story around a broken receipt. And when something dies, run the autopsy before assigning blame, because blaming the wrong suspect is how you pay for the same failure twice.</p>

<p>None of these failures were intelligence problems. They were the gap between what a system said it did and what it actually did — and no model upgrade closes that gap. Verification does.</p>either alone.</p>""",

"autodiff": """<p>So I want to use python to recode an example of dynamic calculation graph.</p>""",

"llm": """<p>It is hard to generate a proper AI patient. However, the mental health is a really different region for Standarized patients, for most of the disorder is represented from the expression yet profile. Therefore, there are two parts should be considered.</p>
<ol>
<li>How should Standarized patient express?</li>
<li>What should he/she express?</li>
</ol>
<h2 id="References">References</h2>
<p><a target="_blank" rel="noopener" href="https://aclanthology.org/2025.acl-long.846.pdf">LLMs Can Simulate Standardized Patients via Agent Coevolution</a></p>
<p>The paper propose a framework called <em>EvoPatient</em>, which a patient agent and doctor agents simulate the diagnostic process through multi-turn dialogues, simultaneously gathering experience to improve the quality of both questions and answers.</p>""",
}

# ------------------------------------------------------------------ helpers
def write(path, content):
    full = os.path.join(OUT, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

def tags_label(tags):
    return "&thinsp;&middot;&thinsp;".join(xesc(t) for t in tags)

def post_row(p):
    return f"""        <li class="post {p['hue']}">
          <a class="post-link" href="{p['url']}">
            <span class="post-meta">
              <span class="post-date"><time datetime="{p['date']}">{p['disp'].rsplit(',', 1)[0]}</time></span>
              <span class="post-tags">{tags_label(p['tags'])}</span>
            </span>
            <span class="post-title">{xesc(p['title'])}</span>
          </a>
        </li>"""

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="stylesheet" href="/style.css">
</head>
<body{bodycls}>
  <a class="skip-link" href="#main">Skip to content</a>

  <header class="masthead container">
    <p class="wordmark"><a href="/">Ruojun Wang</a></p>
    <nav class="site-nav" aria-label="Site">
      <a href="/">Posts</a>
      <a href="/archives/"{cur}>Archives</a>
    </nav>
  </header>
"""

FOOTER = """
  <footer class="site-footer">
    <div class="container">
      <p><a href="https://github.com/yuyuan12138">GitHub</a> &middot; <a href="/atom.xml">RSS</a></p>
      <p>&copy; 2026 Ruojun Wang</p>
    </div>
  </footer>
</body>
</html>
"""

def article_page(p, newer, older):
    nav = ""
    if newer:
        nav += f"""        <a class="{newer['hue']}" href="{newer['url']}">
          <span class="nav-label">Next</span>
          <span class="nav-title">{xesc(newer['title'])}</span>
        </a>\n"""
    if older:
        nav += f"""        <a class="{older['hue']}" href="{older['url']}">
          <span class="nav-label">Previous</span>
          <span class="nav-title">{xesc(older['title'])}</span>
        </a>\n"""
    nav_block = (f'      <nav class="article-nav" aria-label="More posts">\n{nav}      </nav>\n'
                 if nav else "")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>{xesc(p['title'])} — Ruojun Wang</title>
  <meta name="description" content="{xesc(p['desc'])}">
  <link rel="stylesheet" href="/style.css">
</head>
<body class="{p['hue']}">
  <a class="skip-link" href="#main">Skip to content</a>

  <header class="masthead container">
    <p class="wordmark"><a href="/">Ruojun Wang</a></p>
    <nav class="site-nav" aria-label="Site">
      <a href="/">Posts</a>
      <a href="/archives/">Archives</a>
    </nav>
  </header>

  <main id="main" class="container">
    <article>
      <header class="article-head">
        <p class="article-meta">
          <time datetime="{p['date']}">{p['disp']}</time>
          <span class="article-tags">{tags_label(p['tags'])}</span>
        </p>
        <h1 class="article-title">{xesc(p['title'])}</h1>
        <hr class="article-rule">
      </header>

      <div class="prose">
{PROSE[p['key']]}
      </div>

{nav_block}      <p class="back-home"><a href="/">All posts</a></p>
    </article>
  </main>
{FOOTER}"""

def redirect_page(old_path, new_url, title):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="0; url={new_url}">
  <link rel="canonical" href="{SITE}{new_url}">
  <title>{xesc(title)}</title>
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <main id="main" class="container">
    <div class="prose">
      <p>This page has moved to <a href="{new_url}">{SITE}{new_url}</a>.</p>
    </div>
  </main>
</body>
</html>
"""

# -------------------------------------------------------------------- build
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT, exist_ok=True)

# 1. Hand-authored sources, byte-identical: pages from content/, stylesheet from design/
for src, dst in [("content/index.html", "index.html"),
                 ("design/style.css", "style.css"),
                 ("content/piagents/index.html", "piagents/index.html"),
                 ("content/archives.html", "archives/index.html"),
                 ("content/2026/02/16/why-smart-people-lose-at-20/index.html",
                  "2026/02/16/why-smart-people-lose-at-20/index.html")]:
    full = os.path.join(OUT, dst)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    shutil.copyfile(os.path.join(ROOT, src), full)

# 2. Article pages for the three posts not built by the designer
order = [BY_KEY["pi-agents"], BY_KEY["essay"], BY_KEY["llm"], BY_KEY["autodiff"]]
for i, p in enumerate(order):
    newer = order[i - 1] if i > 0 else None
    older = order[i + 1] if i < len(order) - 1 else None
    if p["key"] == "essay":
        continue  # byte-identical copy already placed
    write(p["url"] + "index.html", article_page(p, newer, older))

# 3. Tag pages (minimal taxonomy from DESIGN.md §6)
for tag in ["llm", "healthcare", "essay", "deep-learning"]:
    hue = TAG_HUE[tag]
    rows = "\n".join(post_row(p) for p in order if tag in p["tags"])
    write(f"tags/{tag}/index.html", HEAD.format(
        title=f"{tag} — Ruojun Wang",
        desc=f"Posts tagged {tag}.",
        bodycls="", cur="") + f"""
  <main id="main" class="container">
    <h1 class="page-title">{xesc(tag)}</h1>

    <ul class="post-list">
{rows}
    </ul>

    <p class="back-home"><a href="/archives/">All posts</a></p>
  </main>
{FOOTER}""")

# 4. 404
write("404.html", HEAD.format(
    title="Page not found — Ruojun Wang",
    desc="Page not found.", bodycls="", cur="") + """
  <main id="main" class="container">
    <h1 class="page-title">Page not found</h1>
    <div class="prose">
      <p>The page you&rsquo;re looking for doesn&rsquo;t exist or has moved.</p>
    </div>
    <p class="back-home"><a href="/">All posts</a></p>
  </main>
""" + FOOTER)

# 5. Redirect stubs at old paths (DESIGN.md §7: meta refresh + canonical)
REDIRECTS = [
    ("/2026/01/20/2026-01-20-autodiff/index.html", "/2026/01/20/autodiff/", "Redirecting…"),
    ("/2026/02/02/2026-02-02-thinking-of-llm-of-ai-patient-simulation/index.html",
     "/2026/02/02/ai-patient-simulation/", "Redirecting…"),
    ("/2026/02/16/2026-02-16-why-smart-people-always-lose-at-their-20-age./index.html",
     "/2026/02/16/why-smart-people-lose-at-20/", "Redirecting…"),
    ("/tags/github-pages/index.html", "/archives/", "Redirecting…"),
    ("/tags/jekyll/index.html", "/archives/", "Redirecting…"),
    ("/tags/welcome/index.html", "/archives/", "Redirecting…"),
    ("/categories/LLM/index.html", "/archives/", "Redirecting…"),
    ("/categories/announcement/index.html", "/archives/", "Redirecting…"),
    ("/archives/2026/index.html", "/archives/", "Redirecting…"),
    ("/archives/2026/01/index.html", "/archives/", "Redirecting…"),
    ("/archives/2026/02/index.html", "/archives/", "Redirecting…"),
    ("/archives/2026/05/index.html", "/archives/", "Redirecting…"),
]
for old, new, t in REDIRECTS:
    write(old, redirect_page(old, new, t))

# 6. atom.xml (footer of the approved design links /atom.xml; old site never shipped one)
updated = "2026-11-09T00:00:00Z"
entries = []
PUBTIMES = {"pi-agents": "2026-11-09T00:00:00Z",
            "essay": "2026-02-16T00:00:00Z",
            "llm": "2026-02-02T02:10:19Z",
            "autodiff": "2026-01-20T13:29:52Z"}
for p in order:
    content = PROSE.get(p["key"], "")
    if p["key"] == "essay":
        # pull prose from the canonical built page
        src = open(os.path.join(OUT, p["url"].lstrip("/") + "index.html"), encoding="utf-8").read()
        content = re.search(r'<div class="prose">(.*?)</div>\s*<nav class="article-nav"',
                            src, re.S).group(1).strip()
    entries.append(f"""  <entry>
    <title>{xesc(p['title'])}</title>
    <link href="{SITE}{p['url']}"/>
    <id>{SITE}{p['url']}</id>
    <updated>{PUBTIMES[p['key']]}</updated>
    <content type="html">{xesc(content)}</content>
  </entry>""")
atom = f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Ruojun Wang</title>
  <subtitle>Notes on LLM agents, reinforcement learning, and the occasional essay.</subtitle>
  <link href="{SITE}/"/>
  <link href="{SITE}/atom.xml" rel="self"/>
  <id>{SITE}/</id>
  <updated>{updated}</updated>
{chr(10).join(entries)}
</feed>
"""
write("atom.xml", atom)

print("Built. Files:")
for root, dirs, files in os.walk(OUT):
    dirs.sort()
    for f in sorted(files):
        p = os.path.join(root, f).replace(OUT, "")
        print(" ", p)
