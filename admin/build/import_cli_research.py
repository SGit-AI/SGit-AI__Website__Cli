#!/usr/bin/env python3
"""Publishes the CLI repository's research documents as articles on this site.

Run from anywhere: python3 admin/build/import_cli_research.py --cli PATH_TO_SGIT-AI__CLI_CLONE

The CLI team writes its research, designs, measurements and fixes as markdown in the CLI repository
(team/humans/dinis_cruz/claude-code-web/MM/DD/). Those documents are the new generation of briefs: each one
takes one topic as far as it goes, with the evidence. This copies the ones listed in ARTICLES into
admin/content/articles/<slug>.md, one file per article, so after the import an article is published or
corrected by editing one file, the contract in admin/content/articles/README.md.

What changes on the way, and nothing else:
  · front matter is added: title (the document's own first heading), date (its folder), kind, the summary
    written here for the card, and where it came from: the path and the commit of the CLI repository;
  · a file name in backticks that names another imported document becomes a link to that article.

The body is not edited. A newer version of a document is taken by re-running this, which overwrites the
article from the CLI repository at its current commit.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "admin/content/articles"
FOLDER = "team/humans/dinis_cruz/claude-code-web"
GH = "https://github.com/SGit-AI/SGit-AI__CLI/blob"

# source (under FOLDER), slug, kind, tags, summary
ARTICLES = [
    ("10/16/article-draft__one-vault-ten-agents-measured.md", "one-vault-ten-agents-measured", "measurement",
     "performance, clone, agents",
     "What sgit does when the repository is big and the clients are many: the comms vault, 35,000 encrypted objects "
     "and ten agents, cloned eight ways and measured from a cloud sandbox."),
    ("10/16/article-draft__sgit-is-a-standard-one-hash-away.md", "sgit-is-a-standard-one-hash-away", "position",
     "architecture, storage, caching",
     "A vault is a set of files laid out by a convention, every immutable object named by the hash of its own "
     "ciphertext, so the server is the least interesting part and anything in the path can cache blindly."),
    ("10/16/response__scion-and-sgit-article.md", "response-to-scion-and-sgit", "review",
     "performance, architecture, newsroom",
     "The CLI team's response to the newsroom's \"Scion and sgit\" article: what it gets right, the three factual "
     "errors, and the measurements from a 35k-object vault the article should have carried."),
    ("10/14/response__sgit-issues-2026-10-14.md", "sgit-issues-2026-10-14", "fix",
     "pull, fetch, large-files",
     "The issues reported on 14 October, each traced to its cause in the code, with what was fixed in the same "
     "push and what was left open."),
    ("10/13/security-ci__pipeline-and-ai-review.md", "security-ci-and-ai-review", "design",
     "security, ci, ai-review",
     "A dedicated security pipeline on every pull request, and a keyless AI security review that can break the "
     "build on anything new: why, how it is wired, and what it costs per reviewed change."),
    ("10/13/AC-L-001__non-ascii-paths__refuse-dont-rewrite.md", "non-ascii-paths-refuse-dont-rewrite", "finding",
     "security, paths, bug",
     "Characters outside a narrow set in a path are silently rewritten, so one vault gets two roots and a false "
     "push conflict. What really happens, reproduced, and a fix that raises an alarm instead of rewriting."),
    ("10/12/research__sgit-serve-local-vault-server.md", "sgit-serve-running-a-vault-locally", "research",
     "serve, local, api",
     "How to run a vault locally: the vault server's API inventory, the browser modes, when TLS is and is not "
     "needed, and how much plumbing sgit would need."),
    ("10/12/options__sgit-serve-container-and-static.md", "sgit-serve-container-first", "decision",
     "serve, containers, docker",
     "The decision to run the SG/Send container image rather than re-implement the server: the runtimes "
     "supported (including Apple's container and Podman), the spike results, and phase 1 as built."),
    ("10/11/research__security-review-skills.md", "security-review-skills", "research",
     "security, skills, agents",
     "Agent skills for security review, each checked at its source, ranked by whether it brings a method, a "
     "tool with deterministic output, or vets the other skills, against this code base."),
    ("10/11/research__threat-modeling-tools.md", "threat-modeling-tools", "research",
     "security, threat-modeling",
     "Threat-modeling tools for an agent-driven review: Matt Adams' stack (STRIDE GPT, the insider-threat "
     "model), the classics, and the house method, with the agent itself named as an actor."),
    ("10/11/plan__security-review-with-skills.md", "security-review-plan", "plan",
     "security, review",
     "The plan for a tool-assisted, data-producing security review of one slice of sgit-ai: the code the "
     "zero-knowledge guarantee and the trust boundaries live in."),
    ("10/11/case-study/README.md", "security-review-case-study", "case study",
     "security, review, tools",
     "What each tool found in the round-1 security review of sgit-ai 0.21.0, with counts and cost: the skill "
     "vetting, the derived graph, 270 function records, 68 STRIDE threats and the insider overlay."),
    ("10/09/design-analysis__read-write-keys-as-pki.md", "read-write-keys-as-pki", "analysis",
     "pki, keys, crypto",
     "Are the read key and the write key really a public and a private key? Half right: the write key should "
     "become a signing key, and the read key cannot become a public key. What that would take."),
    ("10/09/design__native-pki-vault-mode.md", "native-pki-vault-mode", "design",
     "pki, vault-format, crypto",
     "An architecture map for a second vault mode built on key pairs from the start, revised twice after review: "
     "sequence-number pinning, frozen hosts, concurrent writers."),
    ("10/09/design__sealed-files-layer.md", "sealed-files-layer", "design",
     "crypto, sealed-files, pki",
     "A second encryption layer on top of either vault mode: files sealed to named recipients with ECDH P-256, "
     "HKDF and AES-256-GCM, with the corrections from the sgit.ai agent's review."),
    ("10/08/future-features__after-0.21.md", "future-features-after-0-21", "roadmap",
     "roadmap, git-parity, compatibility",
     "The git-parity and security ideas that are not in 0.21.0, what each would take and what it could break, "
     "starting from the constraint that a new commit field breaks older clients' signature checks."),
    ("10/08/review__git-to-sgit-security-mapping.md", "git-to-sgit-security-mapping", "review",
     "security, git",
     "A review of the one-way map from git's security features to sgit, checked against the code: three "
     "corrections, one missing gap, and the four easy gaps closed for 0.21.0."),
    ("10/08/test-suite__branches-performance-quality-review.md", "branches-and-test-suite-review", "review",
     "branches, tests, quality",
     "An end-to-end check found that branches did not work. What was fixed behind it, the tests that now cover "
     "it, and a review of the test suite's speed and quality."),
    ("10/07/history-integrity__cost-and-compatibility.md", "history-integrity-cost-and-compatibility", "measurement",
     "integrity, signatures, performance",
     "What signature verification, ref monotonicity and 128-bit ids would cost, measured on a real vault, and "
     "how to ship all three without a vault move."),
    ("10/07/compatibility-matrix__cli-x-web-ui-x-api.md", "compatibility-matrix-cli-web-ui-api", "analysis",
     "compatibility, web-ui, api",
     "The CLI, the vault web UI and the SG/Send API across the integrity roll-out, step by step: what each "
     "version reads, writes and loses, under the rule that no client may break another still writing."),
    ("10/06/partial-clones__scope-and-depth.md", "partial-clones-scope-and-depth", "design",
     "clone, partial-clones, agents",
     "Cloning just the folders an agent reads and writes, read and write, plus a shallow mode, without changing "
     "the full clone: the Merkle-spine idea and the measurements."),
    ("10/03/pull-discards-uncommitted-edits__fix.md", "pull-discarded-uncommitted-edits", "fix",
     "pull, bug, working-tree",
     "sgit pull silently discarded uncommitted edits to tracked files. The root cause, and the fix: git's "
     "rules for the working tree, applied before any write."),
    ("10/02/clone-performance__shared-subtree-refetch.md", "clone-refetched-shared-subtrees", "measurement",
     "performance, clone",
     "A clone stuck walking trees: the walk re-fetched shared sub-trees once per parent, 10,098 requests for "
     "2,236 unique trees. The instrumented run and the fix."),
]


def git(cli, *args):
    return subprocess.run(["git", "-C", str(cli), *args], check=True, capture_output=True, text=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cli", required=True, help="a clone of SGit-AI/SGit-AI__CLI, at the commit to publish from")
    args = ap.parse_args()
    cli = Path(args.cli)
    commit = git(cli, "rev-parse", "HEAD")
    by_name = {Path(src).name: slug for src, slug, *_ in ARTICLES}
    OUT.mkdir(parents=True, exist_ok=True)
    for src, slug, kind, tags, summary in ARTICLES:
        path = f"{FOLDER}/{src}"
        text = (cli / path).read_text()
        title = re.search(r"^# (.+)$", text, re.M).group(1).strip()
        month, day = src.split("/")[:2]
        date = f"2026-{month}-{day}"
        first = git(cli, "log", "--diff-filter=A", "--format=%cI", "-1", "--", path)
        body = re.sub(r"`([^`\s/]+\.md)`",
                      lambda m: f"[`{m.group(1)}`](/articles/{by_name[m.group(1)]}.html)" if m.group(1) in by_name else m.group(0),
                      text.strip("\n"))
        (OUT / f"{slug}.md").write_text(
            "---\n"
            f"title: {title}\n"
            f"date: {date}\n"
            + (f"time: {first[11:16]}\n" if first.startswith(date) else "")
            + f"kind: {kind}\n"
            f"tags: {tags}\n"
            f"summary: {summary}\n"
            "author: the sgit-ai CLI team (Claude Code sessions), for Dinis Cruz\n"
            f"source: {GH}/{commit}/{path}\n"
            f"source_path: {path}\n"
            f"source_commit: {commit[:7]}\n"
            "status: published\n"
            "---\n\n" + body + "\n")
        print(f"  · {slug}  ({date}, {len(body.split())} words)")
    print(f"import_cli_research: {len(ARTICLES)} articles from SGit-AI__CLI@{commit[:7]}")


if __name__ == "__main__":
    sys.exit(main())
