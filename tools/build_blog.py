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
    dict(key="pi-agents", title="One human, dozens of AI workers: my agent coordination architecture",
         date="2026-11-09", disp="Nov 9, 2026",
         url="/2026/11/09/pi-agent-architecture/", tags=["llm"], hue="hue-214",
         desc="My setup is not one smart chatbot. It is a router conversation that never does the work itself, clean-context workers with role briefs, and a discipline for catching them when they get things wrong."),
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
"pi-agents": """<p>A friend asked what my AI setup looks like, and the honest answer sounds strange: I don't really have "an AI assistant" anymore. I have a router conversation that never does the work itself, and behind it a rotating cast of dozens of short-lived workers. The router breaks my goal into bounded tasks, writes a brief for each, dispatches them, then verifies what comes back against the filesystem and git. It accepts or bounces. The engine underneath is <a target="_blank" rel="noopener" href="https://github.com/badlogic/pi-mono">Pi</a>, an open-source coding agent harness, but the interesting part is not the engine — it is the operating discipline built on top of it: how work gets dispatched, why nothing is trusted on its own word, and what self-improvement looks like when the model never grades its own homework.</p>
<h2 id="the-router-does-no-work">The router does no work</h2>
<p>The core rule is blunt: the primary conversation is forbidden from executing tasks. If the primary can do it, a subagent can do it too. The primary's actual job is the part that cannot be delegated — understanding what I want, decomposing it, writing briefs, making decisions, and accepting or rejecting deliverables. Everything else — research, coding, testing, deployment, even "trivial" one-line fixes — goes to a worker.</p>

<p>Every worker starts from a clean context with a written brief. There are nine predefined roles, each just a folder of markdown: a brief template, a skills file the worker reads first, and a running record of lessons from past jobs. Scout maps a codebase without judging it. Coder implements minimally and reports in three states: implemented, tested, or unverified. Operator executes runbooks mechanically and never retries operations with unknown outcomes. Reviewer produces findings with file-and-line evidence but never edits. Researcher, planner, visualizer, writer, and designer fill in the rest. Each role also gets a tool allowlist — a reviewer can read but not write. These are workflow constraints rather than true sandboxes, so the real safety line is written into the brief: delegation never expands authorization.</p>

<p>The router keeps two dispatch channels. A <em>fork</em> inherits the entire live conversation — useful for debugging sessions where the context is the task, expensive because every forked turn re-reads the whole history. A <em>subagent</em> starts blank and gets only what the brief says — cheap, and the default. Long chains run in the background so the router never sits blocked; reports arrive as new messages while it moves on to the next dispatch.</p>
<h2 id="workers-get-things-wrong-so-claims-dont-count">Workers get things wrong, so claims don't count</h2>
<p>This discipline was not designed on a whiteboard. Workers sometimes fabricate — confidently, plausibly, citing files that don't say what they claim. Once, a worker's commit record described 26 failing tests as "pre-existing environmental issues". I ran a baseline A/B on the same machine: restore the previous files, keep the tests identical, see whether the failure set moves with the change. It did. Not the environment — a regression. Nobody would have caught that by reading the report, because the report itself was the problem.</p>

<p>Acceptance means the router personally runs the tests, inspects the actual diff, and checks the deliverable. A green API response is not a working user journey.</p>

<p>The sharpest version of this rule comes from a side project: a Minecraft agent learning to craft a wooden sword through self-improvement. I refused to trust in-process flags or the model's narration. Success is defined as a counter in the game server's stored player data — <code>crafted:wooden_sword</code> ≥ 1 — read from the server, not from anything the model can touch. In one episode the model made 117 requests, and the server stats confirmed two swords. That number meant something precisely because the model had no path to it. The same pattern showed up in a web platform project: workers ran a load test that surfaced the real ceiling — about 500 concurrent users at 33 requests per second — plus three genuine bugs. What made those results acceptable was not the confident summary but the evidence trail anyone could re-check.</p>
<h2 id="the-shape-of-the-system">The shape of the system</h2>
<p>Put it together and the architecture looks like this:</p>
<pre><code>                        you
                         |  requirements, decisions, final acceptance
                         v
   +-----------------------------------------------------+
   |              coordinator conversation               |
   |    decompose -&gt; brief -&gt; dispatch -&gt; verify -&gt;      |
   |    accept or bounce        (never executes work)    |
   +------+-------------------------+--------------------+
          |                         |
        fork                  subagent x N
   inherits the live      clean context + role brief
   conversation branch    isolated worktree each
          |                         |
          v                         v
   one context-heavy      9 roles: scout / planner / coder /
   worker                 operator / reviewer / researcher /
          |               visualizer / writer / designer
          |                         |
          +------------+------------+
                       v
     acceptance: run the tests yourself, read the diff,
                 verify the evidence
                       |
        verified ------+------ bounced with reasons
                       v
     memory: raw streams -&gt; observations -&gt; curated
             knowledge base -&gt; skills &amp; rules
             (lessons pass a human-approved gate)
</code></pre>
<p>Nesting is capped — a worker may delegate once more, but no deeper — because unbounded chains of agents grading each other is how you lose track of reality.</p>
<h2 id="best-of-n">Best of N</h2>
<p>For bounded tasks with an objective verifier — a test suite, a live check — my default is not one worker but N, usually three, sometimes five. All N get the same brief, the same fixed acceptance tests, and their own isolated working copy of the repository. When they finish, the router verifies each candidate — runs the tests, reads the diff, checks the deliverable — and accepts the best, reporting every failure honestly.</p>

<p>This sounds wasteful. It is actually the cheapest insurance I know of. With fast parallel API capacity, three attempts at a well-specified task beat one attempt plus a debugging conversation — the candidates fail differently, and the fixed acceptance tests act as a common yardstick. The one rule I never bend: the criteria do not move. If no candidate passes, the failure gets diagnosed and one repair round follows; weakening a test to manufacture a pass corrupts the whole system. A recent security fix ran four parallel workers on their own git worktrees with disjoint files; the results merged cleanly and the full 438-test suite went green before anything was accepted.</p>
<h2 id="four-layers-of-memory">Four layers of memory</h2>
<p>Everything an agent session produces is worth keeping, but not everything is worth believing. My memory is layered by trust.</p>

<p>The bottom layer is the raw session stream — everything said and done, kept as-is. Above it sits observational memory: as a long session compacts, an observer writes short notes and reflections that can be recalled later. Useful, fallible — treated like a colleague's meeting notes, re-checkable against the original files.</p>

<p>The third layer is a curated markdown knowledge base, and this is where the discipline lives. After a verified result produces a transferable lesson, one entry goes into a daily log: context, the lesson, a source pointer. Recurring lessons get promoted into concept articles, and a compiler script regenerates the index while linting for broken links, missing metadata, and secret patterns. The interesting gate is scope: a lesson is project-scoped by default, and promoting it to global scope fails closed unless the evidence cites logs from at least two distinct projects and the approval field says "user-approved". A naive global memory pool performs worse than no memory at all. Every article also carries provenance — AI-generated or human-written, and a last-reviewed date.</p>

<p>The top layer is skills and rules: distilled procedures the agents load at dispatch time. Lessons survive across projects only by passing through that human gate.</p>
<h2 id="the-self-improvement-loop">The self-improvement loop</h2>
<p>The Minecraft experiment ties all of this together, because there the agent has to improve itself, and self-deception is the failure mode to beat. The loop is: run an episode with the current skill library; check the server for the crafted-sword counter; if there is no sword, feed the episode summary — action sequences, failure codes, inventory changes — to the model and let it write a new skill; merge the skill into the library with deduplication and a hard cap of 48; reset the world and run again.</p>

<p>Two anchors keep the loop honest. First, server-authoritative evidence: only episodes verified by the server count as successes a skill may cite, and the model may propose skills but never judge them. Second, controlled experiments: when the loop stalled, I stripped terrain and navigation out with a superflat map and found the true weakness — the agent could mine a block but couldn't pick up the dropped item, walking off to search for a log that no longer existed. That is a model-capability finding, and no amount of optimistic self-reporting would have surfaced it. A background worker is running this loop automatically right now, reporting each round's server-verified result.</p>
<h2 id="why-bother">Why bother</h2>
<p>The short answer: I am one person, and I want to operate at the scale of a team. The architecture is the point — not the model. The workers can be modest, self-hosted models, because correctness comes from the harness: briefs that bound the work, acceptance that checks reality, memory that only promotes what survived verification. A smarter model makes every worker better; it removes none of this, because the failure modes I designed around are not stupidity. They are the ordinary gap between what a system says it did and what it actually did.</p>

<p>None of this is exotic. The whole "kernel" is markdown rules, role templates, and a few hundred lines of scripts, plus a handful of small local extensions. The guards are best-effort, the memory is lossy, and every week some new incident teaches me another rule. The system is not trying to be impressive. It is trying to make one honest human and a few dozen fallible agents add up to more than either alone.</p>""",

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
