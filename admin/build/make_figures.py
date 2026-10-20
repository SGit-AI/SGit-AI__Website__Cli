#!/usr/bin/env python3
"""Draws the articles' lead figures as SVG, from the site's own colours.

Run from anywhere: python3 admin/build/make_figures.py    (writes articles/images/<slug>.svg)

The guidance (send.sgit.ai, "Every site its own articles") asks for a lead figure on every article, and says an
SVG drawn by hand from the site's colours is enough. These are drawn by this script instead of by hand so a
figure can be corrected in one place and redrawn the same way. Every number in a figure is the article's own,
from the source it names; nothing here is measured.

A figure is a list of shapes: boxes with a title and lines of smaller text, arrows, horizontal bars and labels.
"""
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "articles/images"

BG, PANEL, LINE, FG, DIM = "#faf9f5", "#ffffff", "#d5d0c2", "#1c1d21", "#5c5f66"
ACCENT, ACCENT_BG, WARM, WARM_BG, MUTED_BG = "#0f766e", "#e6f2f0", "#b45309", "#fbefe3", "#f2f0e9"
W = 900


class Fig:
    def __init__(self, h, title):
        self.h, self.parts = h, []
        self.text(24, 34, title, size=17, weight=700)

    def text(self, x, y, s, size=13, weight=400, fill=FG, anchor="start"):
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
                          f'text-anchor="{anchor}">{html.escape(s)}</text>')

    def box(self, x, y, w, h, title, lines=(), kind="plain"):
        fill, stroke = {"plain": (PANEL, LINE), "accent": (ACCENT_BG, ACCENT), "warm": (WARM_BG, WARM),
                        "muted": (MUTED_BG, LINE)}[kind]
        dash = ' stroke-dasharray="5 4"' if kind == "warm" else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>')
        self.text(x + 12, y + 22, title, size=14, weight=700)
        for i, line in enumerate(lines):
            self.text(x + 12, y + 42 + i * 17, line, size=12, fill=DIM)

    def arrow(self, x1, y1, x2, y2, label="", color=DIM):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.8" marker-end="url(#a)"/>')
        if label:
            self.text((x1 + x2) / 2, (y1 + y2) / 2 - 6, label, size=11, fill=DIM, anchor="middle")

    def bar(self, x, y, value, scale, label, note, color=ACCENT):
        w = max(2, value * scale)
        self.text(x - 10, y + 15, label, size=12, anchor="end")
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w:.1f}" height="20" rx="4" fill="{color}"/>')
        self.text(x + w + 8, y + 15, note, size=12, fill=DIM)

    def legend(self, y, items):
        x = 24
        for label, kind in items:
            fill, stroke = {"accent": (ACCENT_BG, ACCENT), "warm": (WARM_BG, WARM), "plain": (PANEL, LINE)}[kind]
            dash = ' stroke-dasharray="4 3"' if kind == "warm" else ""
            self.parts.append(f'<rect x="{x}" y="{y - 11}" width="14" height="14" rx="3" fill="{fill}" stroke="{stroke}"{dash}/>')
            self.text(x + 20, y, label, size=12, fill=DIM)
            x += 30 + 7 * len(label)

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {self.h}" font-family="ui-sans-serif, system-ui, sans-serif">\n'
                f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
                f'<path d="M0 0L10 5L0 10z" fill="{DIM}"/></marker></defs>\n'
                f'<rect width="{W}" height="{self.h}" fill="{BG}"/>\n' + "\n".join(self.parts) + "\n</svg>\n")


def one_vault():
    f = Fig(330, "What an agent fetches from a 35,000-object vault (hosted, from a cloud sandbox)")
    rows = [("full clone", 210, "3½ min · 35,423 objects · 527 MB"),
            ("--depth 1", 57, "57 s · 6,248 objects · 142 MB"),
            ("--sparse --depth 1 + one file", 29.9, "27 s + 2.9 s · 968 objects · 6 MB"),
            ("--path security --depth 1", 13, "13 s · 137 objects · 3 MB"),
            ("pull, nothing changed", 2.5, "2.5 s · 0 objects")]
    for i, (label, v, note) in enumerate(rows):
        f.bar(250, 62 + i * 44, v, 1.6, label, note, ACCENT if i else WARM)
    f.text(24, 300, "Source: the article's table, measured 14 to 16 October 2026 on the comms vault (1,295 commits).", size=11, fill=DIM)
    return f


def standard():
    f = Fig(300, "Everything from one hash: a file is four GETs computed from the read key")
    xs = [24, 168, 312, 456, 600, 744]
    names = [("vault key", ["passphrase:id"]), ("read key", ["derived one way,", "publishable"]), ("ref", ["name: HMAC of", "the read key", "-muw-: refetch"]),
             ("commit", ["-imm-"]), ("tree", ["-imm-, names", "encrypted"]), ("blob", ["-imm-, the file"])]
    for i, (x, (t, lines)) in enumerate(zip(xs, names)):
        f.box(x, 64, 132, 96, t, lines, "muted" if i < 2 else ("warm" if t == "ref" else "accent"))
        if i:
            f.arrow(xs[i - 1] + 132, 112, x - 2, 112)
    f.text(24, 186, "derived locally, nothing discovered", size=12, fill=DIM)
    f.text(312, 186, "GET   GET   GET   GET  of fixed paths: S3, GitHub Pages, a CDN, a folder", size=12, fill=DIM)
    f.box(24, 206, 410, 66, "-imm- objects", ["named by the SHA-256 of their ciphertext:", "anyone in the path may keep them for ever"], "accent")
    f.box(460, 206, 416, 66, "-muw- pointers", ["the ref and the branch index: refetched;", "writing needs one compare-and-swap, the API"], "warm")
    return f


def keys():
    f = Fig(400, "Where each check happens: git and GitHub, sgit today, and a door per member (proposed)")
    f.box(24, 56, 410, 150, "git + GitHub: checked on the server", ["SSH key or token: the account", "push permission on the repository",
          "branch protection: signed commits, no force push", "commit author: a string, unless signed", "a clone is yours: nothing on your disk is protected"], "muted")
    f.box(466, 56, 410, 150, "sgit: the server checks a shared hash", ["access token, write-key hash, compare-and-swap",
          "on every client: commits signed by the clone's key", "signatures-required refuses unsigned commits on pull",
          "the named branch only moves forward", "the server cannot tell one writer from another"], "accent")
    f.box(24, 236, 852, 136, "Proposed: a door per member, outside the tree", [], "warm")
    for i, who in enumerate(["alice", "agent 7", "bob"]):
        x = 48 + i * 196
        f.box(x, 270, 176, 70, f"door: {who}", ["data key sealed to", f"{who}'s public key"], "plain")
    f.text(660, 292, "join: add a door", size=12, fill=DIM)
    f.text(660, 312, "leave: delete it", size=12, fill=DIM)
    f.text(660, 332, "the key held in memory only", size=12, fill=DIM)
    f.text(660, 352, "a copy already made stays", size=12, fill=DIM)
    return f


def cow():
    f = Fig(340, "Share until you write: commits share unchanged trees; a lane would take the stream")
    f.box(24, 60, 150, 54, "commit 1", ["tree t1"], "accent")
    f.box(24, 170, 150, 54, "commit 2", ["tree t2 (new)"], "accent")
    f.box(230, 60, 170, 54, "docs/  (shared)", ["same id in both"], "plain")
    f.box(230, 130, 170, 54, "mail/  (shared)", ["same id in both"], "plain")
    f.box(230, 200, 170, 54, "runs/  (changed)", ["new tree, new blobs"], "accent")
    f.arrow(174, 87, 228, 87); f.arrow(174, 87, 228, 152); f.arrow(174, 197, 228, 160); f.arrow(174, 197, 228, 92); f.arrow(174, 197, 228, 226)
    f.text(24, 290, "Shipped: a branch is a pointer; a commit stores only what changed.", size=12, fill=DIM)
    f.box(480, 60, 180, 70, "many small writes", ["an agent, a log, a stream"], "plain")
    f.box(480, 160, 180, 70, "append lane", ["exists: ~200 entries/s", "in memory"], "accent")
    f.box(700, 160, 176, 70, "fold", ["proposed: a batch", "becomes one commit"], "warm")
    f.box(700, 60, 176, 70, "signed commit", ["proposed"], "warm")
    f.arrow(570, 130, 570, 158); f.arrow(660, 195, 698, 195); f.arrow(788, 160, 788, 132)
    f.text(480, 290, "Proposed: a write-ahead lane, folded later, like an LSM store.", size=12, fill=DIM)
    return f


def policies():
    f = Fig(360, "Four levels of enforcement, with RiskMandate's barrier kinds")
    rows = [("4  A server that verifies signed writes", "a boundary against everyone", "proposed (RFC 0001)", "warm"),
            ("3  A policy row: key K may write path/", "a boundary for every honest client, evidence against a dishonest one", "proposed", "warm"),
            ("2  A clone scope (--path)", "a setting: the agent can widen it", "shipped", "accent"),
            ("1  A convention", "an expectation", "exists", "plain")]
    for i, (t, sub, status, kind) in enumerate(rows):
        y = 56 + i * 72
        f.box(24 + i * 24, y, 852 - i * 48, 60, t, [sub], kind)
        f.text(860 - i * 24, y + 22, status, size=12, weight=700, fill=WARM if kind == "warm" else ACCENT, anchor="end")
    f.text(24, 350, "Once a folder is bound to a key it is never rebound: start a new folder. The rule only moves one way.", size=12, fill=DIM)
    return f


def streaming():
    f = Fig(320, "A thousand small writes, one commit, every line attributed")
    for i in range(4):
        f.box(24, 56 + i * 58, 150, 46, f"writer {i + 1}", ["signs its entries"], "plain")
        f.arrow(174, 79 + i * 58, 236, 150)
    f.box(240, 100, 200, 110, "append lane", ["exists", "entries in arrival order", "5 MB, 1,000 pending", "1,000 from 100 writers: 4.9 s"], "accent")
    f.box(490, 100, 160, 110, "fold", ["proposed", "by count, size or time", "stops on a conflict", "the rule cannot settle"], "warm")
    f.box(700, 70, 176, 80, "one signed commit", ["proposed", "says who folded"], "warm")
    f.box(700, 170, 176, 80, "provenance file", ["inside the commit:", "hash, key, seq, paths"], "warm")
    f.arrow(440, 155, 488, 155); f.arrow(650, 140, 698, 112); f.arrow(650, 170, 698, 206)
    f.text(24, 300, "Patches are an ingest format: the store keeps whole, immutable objects; a patch is applied at fold time.", size=12, fill=DIM)
    return f


def zip_fig():
    f = Fig(360, "Requests against one file: a vault as a zip")
    f.text(24, 66, "12 MB vault, local server", size=12, weight=700)
    f.bar(250, 76, 2.25, 120, "106 separate GETs", "2.0 to 2.5 s")
    f.bar(250, 106, 0.13, 120, "one 12.7 MB zip", "0.05 s fetch + 0.08 s unpack", WARM)
    f.text(24, 160, "35,000-object vault, local disk", size=12, weight=700)
    f.bar(250, 170, 111, 3.6, "object by object", "111 s")
    f.bar(250, 200, 3, 3.6, "one 430 MB head zip", "3 s", WARM)
    y = 256
    for i, label in enumerate(["obj", "obj", "obj", "obj", "obj", "… appended", "central directory"]):
        w = 70 if i < 5 else (110 if i == 5 else 170)
        x = 24 + sum(70 if j < 5 else 110 for j in range(i)) + i * 6
        f.box(x, y, w, 40, label, [], "warm" if i == 6 else "plain")
    f.text(24, 330, "The directory sits at the end: one range request reads it, one more reads any member. Appending costs 0.25 s.", size=12, fill=DIM)
    return f


def own_site():
    f = Fig(340, "sgit.ai is the umbrella; cli.sgit.ai documents the command line")
    f.box(24, 60, 300, 250, "sgit.ai, the umbrella", ["the project and why it exists", "the vault platform: apps, _page.json,",
          "  the browser bridge, publishing", "the newsroom, partnerships", "the commercial side", "",
          "until 20 October: the CLI's docs"], "muted")
    f.box(420, 60, 456, 250, "cli.sgit.ai, the command line", [], "accent")
    items = [("docs and guides", "27 pages moved, same paths"), ("command reference", "158 commands, generated"),
             ("research", "the CLI repository's work"), ("articles", "one topic each")]
    for i, (t, sub) in enumerate(items):
        f.box(440, 96 + i * 52, 416, 44, f"{t}:  {sub}", [], "plain")
    f.arrow(324, 140, 438, 118, "moved")
    f.text(440, 330, "sources: sgit.ai's twins · sgit help all --format json · SGit-AI__CLI", size=11, fill=DIM)
    return f


def research_vs_articles():
    f = Fig(350, "Two areas: research as written, articles as arguments")
    f.box(24, 56, 400, 250, "Research  /research/", ["the CLI team's documents, as written", "source file, commit and branch on each",
          "grouped into seven topics:", "  keys and members · history integrity", "  big vaults · how a vault takes writes",
          "  running locally · security review", "  found in daily use", "each topic: a question, shipped / designed / absent"], "accent")
    f.box(476, 56, 400, 250, "Articles  /articles/", ["one argument each, in the newsroom's format", "summary, lead figure, In short,",
          "what it does not claim, where it comes from", "two kinds of author, marked:", "  Dinis Cruz, through an agent",
          "  an agent, in its own voice", "importable into newsroom.sgit.ai unchanged", "held to the shape by the gate"], "plain")
    f.arrow(424, 200, 474, 200, "")
    f.arrow(476, 230, 426, 230, "")
    f.text(450, 326, "a topic lists its articles; an article names its research", size=12, fill=DIM, anchor="middle")
    return f


def shipped():
    f = Fig(340, "How cli.sgit.ai is made: four sources, one generator, one gate, five areas")
    srcs = [("sgit.ai's twins", "27 pages"), ("sgit help --format json", "158 commands"), ("SGit-AI__CLI", "22 documents, 7 drafts"), ("the briefs", "published in full")]
    for i, (t, s) in enumerate(srcs):
        f.box(24, 56 + i * 64, 210, 52, t, [s], "muted")
        f.arrow(234, 82 + i * 64, 298, 180)
    f.box(300, 140, 150, 80, "build.py", ["pages, twins,", "llms.txt, sitemap"], "accent")
    f.box(490, 140, 130, 80, "validate.js", ["the gate"], "accent")
    f.arrow(450, 180, 488, 180)
    outs = ["docs and guides", "command reference", "HTTP API", "research, by topic", "articles"]
    for i, t in enumerate(outs):
        f.box(680, 46 + i * 54, 196, 42, t, [], "plain")
        f.arrow(620, 180, 678, 67 + i * 54)
    f.text(300, 300, "deployed by GitHub Pages from dev: validate, tag vX.Y.Z, deploy", size=12, fill=DIM)
    return f


FIGURES = {
    "one-vault-ten-agents-measured": one_vault, "sgit-is-a-standard-one-hash-away": standard,
    "keys-the-way-git-does-it": keys, "copy-on-write-and-the-vault": cow, "policies-the-vault-enforces": policies,
    "streaming-changes-into-a-vault": streaming, "a-vault-in-one-file": zip_fig, "the-cli-gets-its-own-site": own_site,
    "research-is-not-an-article": research_vs_articles, "what-shipped-in-v0-1-and-v0-2": shipped,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, draw in FIGURES.items():
        (OUT / f"{slug}.svg").write_text(draw().svg())
    print(f"make_figures: {len(FIGURES)} figures in articles/images/")


if __name__ == "__main__":
    main()
