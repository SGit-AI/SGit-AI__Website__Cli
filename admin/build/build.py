#!/usr/bin/env python3
"""Builds cli.sgit.ai: every page, its markdown twin, the indexes, from admin/content/.

Run from anywhere:  python3 admin/build/build.py           write the site into the repository root
                    python3 admin/build/build.py --check   change nothing; exit 1 if any output is stale

The source of every page is one markdown file with flat front matter (admin/build/md.py). A content file at
admin/content/<path>.md becomes <path>.html and its twin <path>.md, at the same path, so a reader or an
agent can swap .html for .md anywhere. Three kinds of page are not written by hand:

  · the command reference, generated from admin/content/reference/sgit-cli-reference.json, which is the
    output of `sgit help all --format json` (schema sgit-cli-reference-v1): one page per top-level command,
    so the reference is the code's own account of itself and cannot describe a flag that does not exist;
  · REALITY.md and BRIEF-CORRECTIONS.md, which live at the repository root where the estate's guidance puts
    them, published as admin/reality.html and admin/corrections.html;
  · llms.txt, llms-full.txt, sitemap.xml and assets/version.js, derived from the pages.

The nav and the footer are defined once, here, and generated from the same page list, so a new page in a
section appears in its menu without an edit anywhere else. Every output is listed in
admin/build/generated.json; a file listed there that the build no longer produces is deleted, so removing a
content file removes its page.

Links in content are root-relative (/docs/quickstart.html). The build rewrites each to a depth-relative
path for the page it lands on, and to .md in the twin, so the site works from any mount point.

Two areas hold writing, and they are kept apart on purpose (v0.2.0):
  · articles/  articles in the newsroom's format (send.sgit.ai's "Every site its own articles"): front matter with
               author and author_url, a lead figure, In short, the argument, What this does not claim, Where this
               comes from; the gate holds them to it;
  · research/  the CLI team's research documents, published as written, each tagged with research topics
               (research/topics/<id>.md), one page per topic with the question and where it stands.
The research documents that were under articles/ in v0.1.x keep their old addresses as redirect pages
(MOVED_TO_RESEARCH), because a published address is a contract.

Content directives, each alone on a line:
  !list SECTION [N]  cards for the pages in that section, in order (articles, research: newest first), the first N
  !topic ID          the articles and the research documents of one research topic
  !shot FILE | DIR | CAPTION | KIND   a figure with its caption (the newsroom's block; the twin gets the caption)
and a ```mermaid fence, whose first line may be `%% <caption>`: the page shows the SVG that
admin/build/render_figures.mjs rendered from it (articles/images/mermaid/<sha256, 12 hex>.svg), the twin keeps the
source. The build stops if a diagram has not been rendered.
  !commands          the command reference index, grouped
  !moved             the table of pages moved from sgit.ai, from their front matter
and tokens anywhere: {{site_version}} {{cli_version}} {{command_count}} {{article_count}} {{research_count}}
{{topic_count}} {{page_count}}
"""
import datetime
import hashlib
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from md import front_matter, inline, render  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "admin/content"
VERSION = (ROOT / "admin/build/version.txt").read_text().strip()
HOST = (ROOT / "CNAME").read_text().strip()
GH = "https://github.com/SGit-AI/SGit-AI__Website__Cli"
GH_CLI = "https://github.com/SGit-AI/SGit-AI__CLI"
MANIFEST = ROOT / "admin/build/generated.json"
REFERENCE = json.loads((CONTENT / "reference/sgit-cli-reference.json").read_text())
ROOT_SOURCES = {"REALITY.md": "admin/reality.md", "BRIEF-CORRECTIONS.md": "admin/corrections.md"}

# section key: (label, the section's own page)
SECTIONS = {
    "home":      ("Home",              "index.html"),
    "start":     ("Get started",       "docs/index.html"),
    "guides":    ("Guides",            "docs/index.html"),
    "security":  ("Security",          "security/index.html"),
    "reference": ("Command reference", "reference/index.html"),
    "api":       ("HTTP API",          "api/index.html"),
    "articles":  ("Articles",          "articles/index.html"),
    "research":  ("Research",          "research/index.html"),
    "topics":    ("Research",          "research/index.html"),
    "briefs":    ("Briefs",            "briefs/index.html"),
    "site":      ("Site",              "admin/index.html"),
}

# The nav, two levels, the same component sgit.ai and pki.sgit.ai run: (label, own page, sections it
# lights up for, sub-entries). A sub-entry is (label, href) or ("@SECTION", n) for the first n pages of a
# section, so a page added to a section reaches the menu without an edit here. A group label is always a
# link to a real page; nothing is reachable only by opening a dropdown.
NAV = [
    ("Docs", "docs/index.html", ("start", "guides"), [
        ("All the docs", "docs/index.html"), ("@start", 6), ("@guides", 4)]),
    ("Security", "security/index.html", ("security",), [("@security", 8)]),
    ("Reference", "reference/index.html", ("reference", "api"), [
        ("&#9679; Every command", "reference/index.html"), ("sgit vault", "reference/vault.html"),
        ("sgit history", "reference/history.html"), ("sgit pki", "reference/pki.html"),
        ("sgit pack", "reference/pack.html"), ("sgit serve", "reference/serve.html"), ("&#9679; The HTTP API", "api/index.html"), ("@api", 6)]),
    ("Research", "research/index.html", ("research", "topics"), [
        ("&#9679; All research, by topic", "research/index.html"), ("@topics", 8)]),
    ("Articles", "articles/index.html", ("articles",), [
        ("&#9679; All articles", "articles/index.html"), ("@articles", 8)]),
    ("Site", "admin/index.html", ("site", "briefs"), [
        ("The brief", "briefs/index.html"), ("The team", "about/team.html"), ("Release history", "admin/versions.html"),
        ("Engineering", "admin/index.html"), ("Reality", "admin/reality.html"),
        ("Corrections", "admin/corrections.html"), ("What moved from sgit.ai", "admin/moved.html"),
        ("Participant disclosure", "about/participant.html")]),
]

FOOTER = [
    ("Docs", [("@start", 6), ("All the guides", "docs/index.html#guides")]),
    ("Reference", [("Every command", "reference/index.html"), ("@security", 4), ("The HTTP API", "api/index.html")]),
    ("Research", [("All research", "research/index.html"), ("@topics", 7)]),
    ("Articles", [("All articles", "articles/index.html"), ("@articles", 5)]),
    ("Site", [("The brief", "briefs/index.html"), ("Release history", "admin/versions.html"),
              ("Engineering", "admin/index.html"), ("Reality", "admin/reality.html"),
              ("Corrections", "admin/corrections.html"), ("llms.txt", "llms.txt")]),
]

BLURB = ("The documentation for the sgit command-line tool (<code>pip install sgit-ai</code>): every command, the "
         "HTTP API it is a client of, the guides, the CLI team's research by topic, and articles. Part of the "
         "<a href=\"https://sgit.ai\" style=\"display:inline;padding:0\"><b>sgit.ai</b></a> network. "
         "Content CC BY 4.0, code Apache-2.0.")
NETLINE = ('<a href="https://sgit.ai"><b>↗ sgit.ai</b></a>, the project and the vault platform · '
           '<a href="https://github.com/SGit-AI/SGit-AI__CLI">↗ the CLI\'s code</a> · '
           '<a href="https://pypi.org/project/sgit-ai/">↗ sgit-ai on PyPI</a> · '
           '<a href="https://sgit.ai/network/index.html">↗ the network</a>')
PARTNOTE = ('⚠ Participant disclosure: written by the team that builds the sgit CLI. '
            '<a href="{up}about/participant.html" style="display:inline;padding:0">Read the disclosure</a>.')

COMMAND_GROUPS = [
    ("Daily work", ["clone", "init", "create", "status", "commit", "pull", "push", "fetch", "write", "cat", "ls",
                    "file", "publish"]),
    ("Branches and merges", ["branch", "merge-abort", "resolve"]),
    ("History", ["history"]),
    ("The vault as a whole", ["vault", "remote", "migrate", "cache"]),
    ("Keys and identity", ["pki"]),
    ("Checking and looking inside", ["check", "inspect", "doctor"]),
    ("Running a vault locally", ["serve"]),
    ("Other ways to clone", ["clone-branch", "clone-headless", "clone-range"]),
    ("The tool itself", ["help", "version", "update"]),
    ("For developers of sgit", ["dev"]),
]

LINK = re.compile(r"\]\((/[^)\s]*)\)")
TOKEN = re.compile(r"\{\{(site_version|cli_version|command_count|article_count|research_count|topic_count|page_count)\}\}")
SHOT = re.compile(r"^!shot\s+([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(.+?)(?:\s*\|\s*(\w+))?\s*$")

# The research documents that were published under articles/ in v0.1.x: their old address becomes a page that
# sends the reader to the new one, so nothing anybody shared stops working.
MOVED_TO_RESEARCH = [
    "branches-and-test-suite-review", "clone-refetched-shared-subtrees", "compatibility-matrix-cli-web-ui-api",
    "future-features-after-0-21", "git-to-sgit-security-mapping", "history-integrity-cost-and-compatibility",
    "native-pki-vault-mode", "non-ascii-paths-refuse-dont-rewrite", "partial-clones-scope-and-depth",
    "pull-discarded-uncommitted-edits", "read-write-keys-as-pki", "response-to-scion-and-sgit", "sealed-files-layer",
    "security-ci-and-ai-review", "security-review-case-study", "security-review-plan", "security-review-skills",
    "sgit-issues-2026-10-14", "sgit-serve-container-first", "sgit-serve-running-a-vault-locally", "threat-modeling-tools",
]


def asset(rel):
    """A stylesheet or script's address with a fingerprint of its contents: assets/site.css?h=1a2b3c4d.

    GitHub Pages lets a browser keep a file for ten minutes. Without the fingerprint, a reader who loads a page
    just after a release can get the new themes.css with the old site.css from the cache, and see the old
    stylesheet's fixed colours on a dark theme: dark headings and grey text on a dark page, seen on an iPad on
    21 October 2026 (v0.2.2). With it, a page asks for exactly the version it was built with. The fingerprint
    is of the file, not of the release, so a release that does not change a file does not rewrite every page.
    assets/version.js is left out on purpose: it changes every release, and nav.js re-fetches it already."""
    return f"{rel}?h={hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:8]}"


def diagram_size(svg):
    """width and height for a diagram's <img>, from its viewBox. Mermaid writes width="100%", so without a size
    the image stretches to the column: on a wide screen a flowchart's 15px labels became 40px (21 October 2026).
    The diagram is shown at 75% of its drawn size, and never taller than 720px; CSS still shrinks it on a phone."""
    m = re.search(r'viewBox="[-0-9.]+ [-0-9.]+ ([0-9.]+) ([0-9.]+)"', svg.read_text())
    w, h = float(m.group(1)), float(m.group(2))
    scale = min(0.75, 720 / h)
    return f'width="{round(w * scale)}" height="{round(h * scale)}"'


def as_list(v):
    return [x.strip() for x in (v if isinstance(v, list) else (v or "").split(",")) if x.strip()]


def teaser(text, limit=230):
    """A card's text: the summary up to the sentence that crosses the limit. An article's summary is its
    abstract, 220 to 360 words, which is too long for a card."""
    if len(text) <= limit:
        return text
    cut = text.find(". ", limit)
    return text[:cut + 1] if 0 < cut < limit + 160 else text[:limit].rsplit(" ", 1)[0] + "…"


class Page:
    def __init__(self, rel, meta, body, source):
        self.rel, self.meta, self.body, self.source = rel, meta, body, source
        self.title = meta.get("title") or rel
        self.plain = self.title.replace("`", "")      # for <title>, the nav, the crumb: places markdown is not rendered
        self.summary = meta.get("summary", "")
        self.section = meta.get("section", "site")
        self.order = float(meta.get("order", 50))

    @property
    def twin(self):
        return self.rel[:-5] + ".md"


# ---------------------------------------------------------------- collecting the pages

def content_pages():
    pages = []
    for f in sorted(CONTENT.rglob("*.md")):
        if f.name == "README.md" or f.name.startswith("_"):
            continue
        meta, body = front_matter(f.read_text())
        rel = f.relative_to(CONTENT).with_suffix(".html").as_posix()
        if rel.startswith("articles/") and rel != "articles/index.html":
            meta.setdefault("section", "articles")
        if meta.get("status") == "draft":
            continue
        pages.append(Page(rel, meta, body, f.relative_to(ROOT).as_posix()))
    for src, out in ROOT_SOURCES.items():
        meta, body = front_matter((ROOT / src).read_text())
        pages.append(Page(out[:-3] + ".html", meta, body, src))
    return pages


def usage(cmd):
    parts = ["sgit", cmd["path"]]
    if cmd["options"]:
        parts.append("[options]")
    for p in cmd["positionals"]:
        parts.append(f"<{p['name']}>" if p["required"] else f"[{p['name']}]")
    return " ".join(parts)


def cell(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def command_md(cmd, level, heading=True):
    h = "#" * level
    out = [f"{h} sgit {cmd['path']} {{#{cmd['path'].replace(' ', '-')}}}", "", (cmd["help"] or "*(no help text)*"), ""] if heading else []
    out += ["```text", usage(cmd), "```", ""]
    if cmd["positionals"]:
        out += ["| Argument | | What it is |", "|---|---|---|"]
        out += [f"| `{p['name']}` | {'required' if p['required'] else 'optional'} | {cell(p['help'])} |" for p in cmd["positionals"]]
        out.append("")
    if cmd["options"]:
        out += ["| Option | What it does |", "|---|---|"]
        for o in cmd["options"]:
            flags = ", ".join(f"`{f}`" for f in o["flags"])
            choices = (" One of: " + ", ".join(f"`{c}`" for c in o["choices"]) + ".") if o["choices"] else ""
            out.append(f"| {flags} | {cell(o['help'])}{choices} |")
        out.append("")
    return out


def reference_pages():
    cmds = REFERENCE["commands"]
    tops = [c for c in cmds if " " not in c["path"]]
    pages = []
    for i, top in enumerate(tops):
        subs = [c for c in cmds if c["path"].startswith(top["path"] + " ")]
        body = [f"# sgit {top['path']}", "",
                f"{top['help']}." if top["help"] and not top["help"].endswith(".") else (top["help"] or ""), "",
                f"*Generated from `sgit help all --format json`, sgit-ai {REFERENCE['cli_version']}. "
                + (f"{len(subs)} subcommand{'s' if len(subs) != 1 else ''} below." if subs else "No subcommands.")
                + " To change this page, change the command's `register()` in the CLI and regenerate.*", ""]
        body += command_md(top, 2, heading=False)
        if subs:
            body += ["## Subcommands", ""]
            body += [f"- [`sgit {s['path']}`](#{s['path'].replace(' ', '-')}): {s['help']}" for s in subs]
            body.append("")
            for s in subs:
                body += command_md(s, 3 if s["path"].count(" ") == 1 else 4)
        meta = {"title": f"sgit {top['path']}", "summary": top["help"] or f"The sgit {top['path']} command.",
                "section": "reference", "order": str(10 + i), "generated": "reference"}
        pages.append(Page(f"reference/{top['path']}.html", meta, "\n".join(body),
                          "admin/content/reference/sgit-cli-reference.json"))
    return pages


# ---------------------------------------------------------------- directives and links

def section_pages(pages, section):
    """The pages of a section in reading order: articles newest first, everything else by `order`. A hub
    (front matter `hub: true`, the page that lists a section) is not one of its own entries."""
    ps = [p for p in pages if p.section == section and p.meta.get("hub") != "true"]
    if section in ("articles", "research"):
        return sorted(ps, key=lambda p: (p.meta.get("date", ""), p.meta.get("time", "00:00"), p.rel), reverse=True)
    return sorted(ps, key=lambda p: (p.order, p.rel))


def resolve_nav_entries(entries, pages):
    out = []
    for label, href in entries:
        if label.startswith("@"):
            out += [(html.escape(p.plain), p.rel) for p in section_pages(pages, label[1:])[:href]]
        else:
            out.append((label, href))
    return out


def tokens(text, ctx):
    return TOKEN.sub(lambda m: str(ctx[m.group(1)]), text)


def topic_members(pages, tid):
    docs = [p for p in section_pages(pages, "research") if tid in as_list(p.meta.get("topics"))]
    topic = next((p for p in pages if p.rel == f"research/topics/{tid}.html"), None)
    by_rel = {p.rel: p for p in pages}
    arts = [by_rel[f"articles/{a}.html"] for a in as_list(topic.meta.get("articles")) if f"articles/{a}.html" in by_rel] if topic else []
    return docs, arts


def card_html(p, up, pages=()):
    m = p.meta
    summary = p.summary
    if p.section == "articles":
        tag = f'<span class="tag">article · {html.escape(m.get("author", ""))}</span>'
        meta = f'<span class="meta">{m.get("date", "")}</span>'
        summary = teaser(p.summary)
    elif p.section == "research":
        tag = f'<span class="tag">{html.escape(m.get("kind", "research"))}</span>'
        meta = f'<span class="meta">{m.get("date", "")} · ' + ", ".join(as_list(m.get("topics"))) + "</span>"
    elif p.section == "topics":
        docs, arts = topic_members(pages, p.rel.split("/")[-1][:-5])
        tag = '<span class="tag">research topic</span>'
        meta = f'<span class="meta">{len(docs)} document{"s" if len(docs) != 1 else ""}' + (f' · {len(arts)} article{"s" if len(arts) != 1 else ""}' if arts else "") + "</span>"
    elif m.get("moved_from"):
        tag, meta = "", '<span class="meta">moved from sgit.ai</span>'
    else:
        tag, meta = "", ""
    return (f'<a class="card" href="{up}{p.rel}">{tag}<h3>{inline(p.title)}</h3>'
            f'<p>{html.escape(summary)}</p>{meta}</a>')


def commands_md():
    tops = {c["path"]: c for c in REFERENCE["commands"] if " " not in c["path"]}
    counts = {t: sum(1 for c in REFERENCE["commands"] if c["path"].startswith(t + " ")) for t in tops}
    grouped, out = set(), []
    groups = COMMAND_GROUPS + [("Not yet grouped", [t for t in sorted(tops) if not any(t in g for _, g in COMMAND_GROUPS)])]
    for label, names in groups:
        names = [n for n in names if n in tops]
        if not names:
            continue
        out += [f"### {label}", "", "| Command | Subcommands | What it does |", "|---|---|---|"]
        for n in names:
            grouped.add(n)
            out.append(f"| [`sgit {n}`](/reference/{n}.html) | {counts[n] or ''} | {cell(tops[n]['help'])} |")
        out.append("")
    missing = [n for n in COMMAND_GROUPS for n in n[1] if n not in tops]
    if missing:
        out += ["> Grouped here but not in this release's reference: " + ", ".join(f"`{m}`" for m in missing), ""]
    return "\n".join(out)


def expand(page, pages, twin, up):
    """The body with directives expanded: markdown for the twin, placeholders for the HTML."""
    blocks, lines = [], []
    fence, mermaid = None, None
    for line in page.body.splitlines():
        if mermaid is not None:
            if line.strip() != "```":
                mermaid.append(line)
                continue
            src = "\n".join(mermaid)
            mermaid = None
            if twin:
                lines += ["```mermaid", src, "```"]
                continue
            name = hashlib.sha256(src.encode()).hexdigest()[:12] + ".svg"
            if not (ROOT / "articles/images/mermaid" / name).exists():
                raise SystemExit(f"build: a mermaid diagram in {page.source} is not rendered: run node admin/build/render_figures.mjs")
            size = diagram_size(ROOT / "articles/images/mermaid" / name)
            first = src.splitlines()[0].strip() if src.strip() else ""
            caption = first[2:].strip() if first.startswith("%%") else ""
            blocks.append(f'<figure class="diagram"><img src="{up}articles/images/mermaid/{name}" {size} alt="{html.escape(caption or "diagram", quote=True)}" loading="lazy">'
                          + (f'<figcaption>{html.escape(caption)}</figcaption>' if caption else "") + "</figure>")
            lines.append(f"@@BLOCK{len(blocks) - 1}@@")
            continue
        if fence is None and line.strip() == "```mermaid":
            mermaid = []
            continue
        if line.strip().startswith("```"):
            fence = None if fence is not None else line
            lines.append(line)
            continue
        if fence is not None:
            lines.append(line)
            continue
        m = re.match(r"^!list (\w+)(?:\s+(\d+))?\s*$", line)
        if m:
            ps = [p for p in section_pages(pages, m.group(1)) if p is not page][:int(m.group(2) or 9999)]
            if twin:
                lines += [f"- [{p.title}](/{p.rel}): {p.summary}" for p in ps]
            else:
                blocks.append('<div class="cards inpage">' + "".join(card_html(p, up, pages) for p in ps) + "</div>")
                lines.append(f"@@BLOCK{len(blocks) - 1}@@")
            continue
        m = re.match(r"^!topic ([\w-]+)\s*$", line)
        if m:
            docs, arts = topic_members(pages, m.group(1))
            for head, ps in (("Articles from this topic", arts), ("The research documents, newest first", docs)):
                if not ps:
                    continue
                lines += [f"## {head}", ""]
                if twin:
                    lines += [f"- [{p.title}](/{p.rel}): {teaser(p.summary)}" for p in ps] + [""]
                else:
                    blocks.append('<div class="cards inpage">' + "".join(card_html(p, up, pages) for p in ps) + "</div>")
                    lines += [f"@@BLOCK{len(blocks) - 1}@@", ""]
            continue
        m = SHOT.match(line)
        if m:
            name, folder, caption = m.group(1), m.group(2), m.group(3)
            src = folder.rstrip("/") + "/" + name
            if twin:
                lines += [f"![{caption}]({src})", "", f"*{caption}*", ""]
            else:
                img = (up + src[1:]) if src.startswith("/") else src
                blocks.append(f'<figure class="shot"><img src="{img}" alt="{html.escape(caption, quote=True)}" loading="lazy">'
                              f'<figcaption>{html.escape(caption)}</figcaption></figure>')
                lines.append(f"@@BLOCK{len(blocks) - 1}@@")
            continue
        if line.strip() == "!commands":
            lines += commands_md().splitlines()
            continue
        if line.strip() == "!moved":
            moved = sorted((p for p in pages if p.meta.get("moved_from")), key=lambda p: p.rel)
            lines += ["| Was on sgit.ai | Is now | Section here |", "|---|---|---|"]
            lines += [f"| <{p.meta['moved_from']}> | [{p.title}](/{p.rel}) | {SECTIONS[p.section][0]} |" for p in moved]
            continue
        lines.append(line)
    return "\n".join(lines), blocks


def relink(md_text, rel, twin):
    up = "../" * rel.count("/")

    def fix(m):
        target, frag = m.group(1), ""
        if "#" in target:
            target, frag = target.split("#", 1)
            frag = "#" + frag
        if target.endswith("/"):
            target += "index.html"
        if twin and target.endswith(".html"):
            target = target[:-5] + ".md"
        return f"]({up}{target[1:]}{frag})"
    return LINK.sub(fix, md_text)


# ---------------------------------------------------------------- chrome

def nav_html(page, pages, up):
    groups = []
    for label, own, sections, entries in NAV:
        active = page.section in sections
        links = "\n".join(
            f'      <a class="sl{" here" if href == page.rel else ""}" href="{up}{href}">{text}</a>'
            for text, href in resolve_nav_entries(entries, pages))
        groups.append(
            f'    <div class="ni ni-has">\n'
            f'      <a class="nl{" here" if active else ""}" href="{up}{own}">{label}<span class="caret">&#9662;</span></a>\n'
            f'      <div class="sub">\n{links}\n      </div>\n'
            f'    </div>')
    rows = "\n".join(groups)
    return (f'<nav class="site"><div class="row">\n'
            f'  <a class="brand" href="{up}index.html">cli<span>.sgit.ai</span></a>\n'
            f'  <a class="parent" href="https://sgit.ai" title="sgit.ai, the project: the vault platform this CLI is the client of">↗ part of <b>sgit.ai</b></a>\n'
            f'  <span class="stage-pill">sgit-ai {REFERENCE["cli_version"]}</span>\n'
            f'  <a class="ver" href="{up}admin/versions.html" title="Site release history" data-site-version></a>\n'
            f'  <button class="nav-toggle" type="button" aria-expanded="false" aria-label="Menu">Menu</button>\n'
            f'  <div class="nav-items">\n{rows}\n  </div>\n'
            f'  <div class="theme-pick"></div>\n'
            f'  <a class="gh" href="{GH}">★ GitHub</a>\n'
            f'</div></nav>')


def footer_html(page, pages, up):
    partnote = ("⚠ Participant disclosure: written by the team that builds the sgit CLI. You are on the disclosure page."
                if page.rel == "about/participant.html" else PARTNOTE.format(up=up))
    cols = "\n".join(
        "  <div>\n"
        f"    <h4>{head}</h4>\n"
        + "\n".join(f'    <a href="{l if l.startswith("http") else up + l}">{t}</a>' for t, l in resolve_nav_entries(links, pages))
        + "\n  </div>"
        for head, links in FOOTER)
    return (f'<footer class="site"><div class="cols">\n'
            f'  <div>\n'
            f'    <div class="brandline">cli<span>.sgit.ai</span></div>\n'
            f'    <p>{BLURB}</p>\n'
            f'    <p class="netline">{NETLINE}</p>\n'
            f'    <p class="partnote">{partnote}</p>\n'
            f'    <p class="verline">site <a href="{up}admin/versions.html" data-site-version>release history</a> · '
            f'<a href="{up}admin/index.html">engineering</a> · <a href="{up}{page.twin}">this page as markdown</a></p>\n'
            f'  </div>\n{cols}\n</div></footer>')


def provenance_html(page, up):
    m = page.meta
    if m.get("moved_from"):
        when = datetime.date.fromisoformat(m["moved_on"]).strftime("%-d %B %Y")
        return (f'<div class="prov"><b>Moved from sgit.ai.</b> This page was '
                f'<a href="{m["moved_from"]}">{html.escape(m["moved_from"][8:])}</a> (sgit.ai site {m["moved_version"]}), '
                f'moved here on {when} as cli.sgit.ai becomes the CLI\'s main documentation. The text is as it was; '
                f'links to pages that moved now stay on this site. <a href="{up}admin/moved.html">What moved, and why</a>.</div>')
    if page.section == "articles" and m.get("hub") != "true":
        author = html.escape(m.get("author", ""))
        if m.get("author_url"):
            url = m["author_url"]
            author = f'<a href="{up + url[1:] if url.startswith("/") else url}">{author}</a>'
        chips = " ".join(f'<span class="chip">{html.escape(t)}</span>' for t in as_list(m.get("tags")) if t != "article")
        return (f'<p class="byline">By {author} · {m.get("date", "")} · {html.escape(m.get("status", ""))}'
                f'{" · site " + html.escape(m["version"]) if m.get("version") else ""}</p>'
                f'<p class="lead"><b>Summary:</b> {html.escape(m.get("summary", ""))}</p>'
                f'<p class="chips">{chips}</p>')
    if page.section == "research" and m.get("hub") != "true":
        topics = " ".join(f'<a class="chip" href="{up}research/topics/{t}.html">{t}</a>' for t in as_list(m.get("topics")))
        rows = [("Date", m.get("date", "") + (f" · {m['time']} UTC" if m.get("time") else "")),
                ("Kind", html.escape(m.get("kind", "research"))),
                ("Research topics", topics),
                ("Written by", html.escape(m.get("author", "")))]
        if m.get("source"):
            branch = m.get("source_branch", "dev")
            rows.append(("Source", f'<a href="{m["source"]}"><code>{html.escape(m.get("source_path", ""))}</code></a> '
                                   f'in SGit-AI__CLI at <code>{html.escape(m.get("source_commit", ""))}</code>'
                                   + (f' (branch <code>{html.escape(branch)}</code>, not yet merged to dev)' if branch != "dev" else "")
                                   + '. Published here as written; the CLI repository is where the work happened.'))
        return '<div class="docmeta">' + "".join(f'<span class="k">{k}</span><span class="v">{v}</span>' for k, v in rows if v) + "</div>"
    return ""


def with_title(page, body):
    """A newsroom-format article has no heading of its own: the title is its front matter. Give the page one."""
    if re.search(r"^# ", body, re.M):
        return body
    return f"# {page.title}\n\n{body}"


def page_html(page, pages, ctx):
    up = "../" * page.rel.count("/")
    body, blocks = expand(page, pages, False, up)
    body = relink(tokens(with_title(page, body), ctx), page.rel, False)
    content = render(body)
    for i, b in enumerate(blocks):
        content = content.replace(f"<p>@@BLOCK{i}@@</p>", b)
    prov = provenance_html(page, up)
    if prov:
        content = re.sub(r"(</h1>)", r"\1\n" + prov.replace("\\", "\\\\"), content, count=1)
    label, own = SECTIONS.get(page.section, SECTIONS["site"])
    crumb = f'<a href="{up}index.html">cli.sgit.ai</a>'
    if page.rel != "index.html":
        if own != page.rel:
            crumb += f' / <a href="{up}{own}">{label}</a>'
        crumb += f" / {html.escape(page.plain)}"
    siblings = section_pages(pages, page.section)
    pagenav = ""
    if page in siblings and len(siblings) > 1:
        i = siblings.index(page)
        prev_ = f'<a href="{up}{siblings[i - 1].rel}">← {html.escape(siblings[i - 1].plain)}</a>' if i > 0 else "<span></span>"
        next_ = f'<a href="{up}{siblings[i + 1].rel}">{html.escape(siblings[i + 1].plain)} →</a>' if i + 1 < len(siblings) else "<span></span>"
        pagenav = f'<div class="pagenav">{prev_}{next_}</div>'
    src_link = f'{GH}/blob/dev/{page.source}'
    title = page.plain if page.rel != "index.html" else "cli.sgit.ai, the sgit CLI documentation"
    desc = html.escape(page.summary, quote=True)
    wide = " wide" if page.section == "reference" else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)} · cli.sgit.ai</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://{HOST}/{page.rel}">
<link rel="alternate" type="text/markdown" href="{up}{page.twin}">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://{HOST}/{page.rel}">
<meta property="og:type" content="{'article' if page.section in ('articles', 'research') else 'website'}">
<link rel="stylesheet" href="{up}{asset('assets/site.css')}">
<link rel="stylesheet" href="{up}{asset('assets/themes/themes.css')}">
<script src="{up}{asset('assets/themes/themes.js')}"></script>
</head>
<body>

{nav_html(page, pages, up)}

<main class="doc{wide}">
<div class="crumb">{crumb}</div>
{content}
{pagenav}
<p class="small dim" style="margin-top:2rem">This page as <a href="{up}{page.twin}">markdown</a> · its source, <a href="{src_link}"><code>{html.escape(page.source)}</code></a></p>
</main>

{footer_html(page, pages, up)}
<script src="{up}assets/version.js" defer></script>
<script src="{up}{asset('assets/nav.js')}" defer></script>
</body>
</html>
"""


def twin_md(page, pages, ctx):
    body, _ = expand(page, pages, True, "")
    m = page.meta
    if page.section == "articles" and m.get("hub") != "true":
        byline = (f"By [{m.get('author', '')}]({m.get('author_url', '')}) · {m.get('date', '')} · {m.get('status', '')}"
                  if m.get("author_url") else f"By {m.get('author', '')} · {m.get('date', '')} · {m.get('status', '')}")
        body = f"{byline}\n\n**Summary:** {m.get('summary', '')}\n\n{body}"
    body = relink(tokens(body, ctx), page.rel, True)
    head = [f"# {page.title}, cli.sgit.ai", ""]
    if page.summary:
        head += [f"> {page.summary}", ""]
    # No site version here: stamping it into every twin rewrote ~100 files per release, the problem pki.sgit.ai
    # solved with assets/version.js. llms.txt and version.js carry it.
    src = f"*Source: <https://{HOST}/{page.rel}> · generated from the same content as the page, so the two cannot drift."
    if m.get("moved_from"):
        src += f" Moved from <{m['moved_from']}> (sgit.ai {m['moved_version']}) on {m['moved_on']}."
    if m.get("source"):
        src += f" Published from <{m['source']}>."
    head += [src + "*", "", "---", ""]
    up = "../" * page.rel.count("/")
    return "\n".join(head) + body.strip("\n") + f"\n\n---\n\n*[Site index for agents]({up}llms.txt) · [HTML version](https://{HOST}/{page.rel})*\n"


# ---------------------------------------------------------------- the derived files

def llms_txt(pages, ctx):
    out = ["# cli.sgit.ai", "",
           "> The documentation for sgit, the command-line tool for encrypted vaults (pip install sgit-ai; entry",
           "> points `sgit` and `sgit-ai`): every command, generated from the CLI's own parser; the HTTP API it is a",
           "> client of; the guides; and the CLI team's research, published as articles.", "",
           f"Site version: {VERSION} · command reference generated from sgit-ai {ctx['cli_version']} "
           f"({ctx['command_count']} commands) · {ctx['page_count']} pages.", "",
           "Every page below is markdown, generated from the same source as the HTML page at the same path (swap",
           "`.md` for `.html`). Links inside the markdown point at markdown. Every page in one document: /llms-full.txt.", "",
           "Notes for agents:",
           "- The command reference is the code's own account of itself: /reference/sgit-cli-reference.json is the",
           "  output of `sgit help all --format json` (schema sgit-cli-reference-v1). Diff two releases' JSON to see",
           "  exactly what changed. Your installed version answers the same question: `sgit help all --format json`.",
           "- Never write a vault key into a tracked file. Read keys may be published; vault keys never.",
           "- The project, the vault platform and the network of sites: https://sgit.ai/llms.txt", ""]
    order = ["home", "start", "guides", "security", "reference", "api", "topics", "research", "articles", "briefs", "site"]
    for sec in order:
        ps = [p for p in pages if p.section == sec]
        if not ps:
            continue
        hubs = [p for p in ps if p.meta.get("hub") == "true"]
        listed = hubs + section_pages(pages, sec)
        out.append("## " + {"topics": "Research topics", "research": "Research documents"}.get(sec, SECTIONS[sec][0]))
        out += [f"- [{p.title}](/{p.twin}): {p.summary}" for p in listed]
        out.append("")
    return "\n".join(out)


def sitemap(pages):
    urls = "\n".join(f"  <url><loc>https://{HOST}/{p.rel}</loc></url>" for p in sorted(pages, key=lambda p: p.rel))
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'


def build():
    pages = content_pages() + reference_pages()
    seen = {}
    for p in pages:
        if p.rel in seen:
            raise SystemExit(f"build: two sources for {p.rel}: {seen[p.rel]} and {p.source}")
        seen[p.rel] = p.source
    ctx = {"site_version": VERSION, "cli_version": REFERENCE["cli_version"],
           "command_count": REFERENCE["command_count"],
           "article_count": len(section_pages(pages, "articles")), "research_count": len(section_pages(pages, "research")),
           "topic_count": len(section_pages(pages, "topics")), "page_count": len(pages)}
    out = {}
    for p in pages:
        out[p.rel] = page_html(p, pages, ctx)
        out[p.twin] = twin_md(p, pages, ctx)
    out["llms.txt"] = llms_txt(pages, ctx)
    out["llms-full.txt"] = "\n\n".join(out[p.twin] for p in sorted(pages, key=lambda p: p.rel))
    out["sitemap.xml"] = sitemap(pages)
    out["robots.txt"] = f"User-agent: *\nAllow: /\nSitemap: https://{HOST}/sitemap.xml\n"
    out["assets/version.js"] = f'window.SITE_VERSION = "{VERSION}";\n'
    out["reference/sgit-cli-reference.json"] = (CONTENT / "reference/sgit-cli-reference.json").read_text()
    for slug in MOVED_TO_RESEARCH:
        out[f"articles/{slug}.html"], out[f"articles/{slug}.md"] = moved_stub(slug, seen)
    return out, pages


def moved_stub(slug, seen):
    """The page left at a v0.1.x article address whose document moved to research/ in v0.2.0."""
    new = f"research/{slug}.html"
    if new not in seen:
        raise SystemExit(f"build: articles/{slug}.html is listed as moved, but {new} is not built")
    url = f"https://{HOST}/{new}"
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Moved to research · cli.sgit.ai</title>
<meta name="sgit:moved-to" content="{new}">
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url=../{new}">
<link rel="stylesheet" href="../{asset('assets/site.css')}">
<link rel="stylesheet" href="../{asset('assets/themes/themes.css')}">
<script src="../{asset('assets/themes/themes.js')}"></script>
</head>
<body>
<main class="doc">
<p>This document moved to <a href="../{new}">{url}</a> on 20 October 2026 (site v0.2.0), when research got its own
area on this site. Research documents are published as written; articles are written for a reader.</p>
</main>
</body>
</html>
"""
    twin = f"# Moved, cli.sgit.ai\n\nThis document moved to <{url[:-5]}.md> (site v0.2.0).\n"
    return page, twin


def main():
    check = "--check" in sys.argv
    out, pages = build()
    old = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else []
    stale = [rel for rel, text in out.items() if not (ROOT / rel).exists() or (ROOT / rel).read_text() != text]
    gone = [rel for rel in old if rel not in out and (ROOT / rel).exists()]
    manifest = json.dumps(sorted(out), indent=1) + "\n"
    if check:
        problems = stale + [f"{g} (no longer built)" for g in gone]
        if not MANIFEST.exists() or MANIFEST.read_text() != manifest:
            problems.append("admin/build/generated.json")
        if problems:
            print(f"build --check: {len(problems)} file(s) stale; run python3 admin/build/build.py", file=sys.stderr)
            for s in problems[:20]:
                print(f"  · {s}", file=sys.stderr)
            return 1
        print(f"build --check: {len(out)} files current")
        return 0
    for rel in stale:
        (ROOT / rel).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / rel).write_text(out[rel])
    for rel in gone:
        (ROOT / rel).unlink()
    MANIFEST.write_text(manifest)
    print(f"build: {VERSION}, {len(pages)} pages, {len(out)} files; {len(stale)} written, {len(gone)} removed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
