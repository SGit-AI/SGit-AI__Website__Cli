#!/usr/bin/env python3
"""Moves the CLI's technical pages from sgit.ai to this site, as content files.

Run from anywhere: python3 admin/build/import_sgit_ai.py [--from DIR]

sgit.ai publishes a markdown twin of every page, generated from the same source as the HTML. This reads
those twins (from https://sgit.ai, or from DIR holding the same paths) for the pages listed in MOVED, and
writes one content file per page under admin/content/, at the same path the page had on sgit.ai, so
sgit.ai/docs/quickstart.html becomes cli.sgit.ai/docs/quickstart.html and a redirect is one line.

What changes on the way, and nothing else:
  · the twin's own header (title line, summary, source line, breadcrumb) and footer are replaced by front
    matter: title, summary, the section and order on this site, and where and at which sgit.ai version the
    page was moved from, which the page then states above its first paragraph;
  · the previous/next line at the foot of a docs page is dropped, since this site has its own order;
  · every link is resolved: to a page that moved, it becomes a root-relative link on this site; to
    anything else, an absolute link back to sgit.ai. The build turns root-relative links into
    depth-relative ones.

The body text is not edited. A correction to a moved page is made in its content file here, and recorded in
BRIEF-CORRECTIONS.md when it changes what the page claims.

Re-running overwrites the content files, so do it only to take a newer sgit.ai version on purpose.
"""
import argparse
import datetime
import posixpath
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "admin/content"
SGIT_AI = "https://sgit.ai"

# path on sgit.ai (and here), section on this site, order within the section
MOVED = [
    ("docs/what-is-sgit",            "start",    1),
    ("docs/installation",            "start",    2),
    ("docs/quickstart",              "start",    3),
    ("docs/sgit-for-git-users",      "start",    4),
    ("docs/two-branch-model",        "start",    5),
    ("docs/limitations",             "start",    6),
    ("docs/partial-clones",          "guides",   1),
    ("docs/history-integrity",       "guides",   2),
    ("docs/agents",                  "guides",   3),
    ("docs/agents-sharing-one-vault","guides",   4),
    ("docs/vault-messaging",         "guides",   5),
    ("docs/append-lane-messaging",   "guides",   6),
    ("docs/self-host-for-agents",    "guides",   7),
    ("docs/send-a-vault-key",        "guides",   8),
    ("docs/how-to/claude-team-egress","guides",  9),
    ("docs/update-to-0-21-0",        "guides",  10),
    ("docs/update-to-0-18-0",        "guides",  11),
    ("security/index",               "security", 1),
    ("docs/key-management",          "security", 2),
    ("docs/credentials",             "security", 3),
    ("docs/pki",                     "security", 4),
    ("api/index",                    "api",      1),
    ("api/authentication",           "api",      2),
    ("api/vault-objects",            "api",      3),
    ("api/transfers",                "api",      4),
    ("api/append-lanes",             "api",      5),
    ("api/errors",                   "api",      6),
]
# docs/index is not moved: this site writes its own docs hub, and links to sgit.ai's go to it
MOVED_PATHS = {p for p, _, _ in MOVED} | {"docs/index"}
LINK = re.compile(r"\]\(([^)\s]+)\)")


def fetch(path, local):
    if local:
        return (Path(local) / f"{path}.md").read_text()
    with urllib.request.urlopen(f"{SGIT_AI}/{path}.md", timeout=30) as r:
        return r.read().decode("utf-8")


def relink(body, src_path):
    src_dir = posixpath.dirname(src_path)

    def fix(m):
        target = m.group(1)
        if re.match(r"^(https?:|mailto:|#)", target):
            return m.group(0)
        frag = ""
        if "#" in target:
            target, frag = target.split("#", 1)
            frag = "#" + frag
        resolved = posixpath.normpath(posixpath.join(src_dir, target))
        if resolved.endswith(".md"):
            page = resolved[:-3]
            if page in MOVED_PATHS:
                return f"](/{page}.html{frag})"
            return f"]({SGIT_AI}/{page}.html{frag})"
        return f"]({SGIT_AI}/{resolved}{frag})"
    return LINK.sub(fix, body)


def convert(path, text):
    """(title, summary, version, body) from one sgit.ai twin."""
    summary = re.search(r"^> (.+)$", text, re.M).group(1).strip()
    version = re.search(r"· site (v\d+\.\d+\.\d+) ·", text).group(1)
    start = text.index("\n---\n") + 5                         # end of the twin's header
    end = text.rindex("\n---\n")                              # start of its footer
    body = text[start:end].strip("\n").splitlines()
    if body and re.match(r"^\[[^\]]+\]\([^)]+\)( / .*)?$", body[0]):
        body = body[1:]                                       # the breadcrumb
    while body and re.match(r"^(\[[^\]]*(←|→)[^\]]*\]\([^)]+\))+$", body[-1].strip()):
        body = body[:-1]                                      # previous / next
    body = "\n".join(body).strip("\n")
    title = re.search(r"^# (.+)$", body, re.M).group(1).strip()
    return title, summary, version, relink(body, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="local", help="a directory holding the twins at their sgit.ai paths")
    args = ap.parse_args()
    today = datetime.date.today().isoformat()
    for path, section, order in MOVED:
        title, summary, version, body = convert(path, fetch(path, args.local))
        out = CONTENT / f"{path}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            "---\n"
            f"title: {title}\n"
            f"summary: {summary}\n"
            f"section: {section}\n"
            f"order: {order}\n"
            f"moved_from: {SGIT_AI}/{path}.html\n"
            f"moved_version: {version}\n"
            f"moved_on: {today}\n"
            "---\n\n" + body + "\n")
        print(f"  · {path}  ({version}, {len(body.split())} words)")
    print(f"import_sgit_ai: {len(MOVED)} pages written under admin/content/")


if __name__ == "__main__":
    sys.exit(main())
