#!/usr/bin/env python3
"""Publishes the CLI repository's research documents in this site's research area.

Run from anywhere: python3 admin/build/import_cli_research.py --cli PATH_TO_SGIT-AI__CLI_CLONE

The CLI team writes its research, designs, measurements and fixes as markdown in the CLI repository
(team/humans/dinis_cruz/claude-code-web/MM/DD/). Those documents are the new generation of briefs: each one
takes one topic as far as it goes, with the evidence. This copies the ones listed in DOCS into
admin/content/research/<slug>.md, published as written, each tagged with the research topics it belongs to
(admin/content/research/topics/). Since v0.2.0 research is its own area: the articles section holds articles in
the newsroom's format, and the CLI's `article-draft__` documents were converted into those by hand, once.

What changes on the way, and nothing else:
  · front matter is added: title (the document's own first heading), date (its folder), kind, topics, the
    summary written here for the card, and where it came from: the path and the commit of the CLI repository;
  · a file name in backticks that names another imported document becomes a link to it.

The body is not edited. A newer version of a document is taken by re-running this, which overwrites it from the
CLI repository at the clone's current commit; name the branch in --branch when it is not dev.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "admin/content/research"
FOLDER = "team/humans/dinis_cruz/claude-code-web"
GH = "https://github.com/SGit-AI/SGit-AI__CLI/blob"

# source (under FOLDER), slug, kind, research topics (admin/content/research/topics/<id>.md), tags, summary
DOCS = [
    ('10/26/architecture__pack-resident-store-and-pack-carried-indexes.md', 'pack-carried-indexes-architecture',
     'architecture', 'scale, write-path', 'packs, indexes, sqlite, lets, sparse, store, 0.25.0',
     'The CLI team\'s exploration after the 0.25.0 field report: keep the packs a clone downloads and read objects in '
     'place; carry flat, diff and graph indexes inside the pack, encrypted under the read key and signed by the '
     'pusher; assemble them locally into SQLite; four phases. Nothing in it is built.'),
    ('10/26/review__indexes-and-caches-across-the-board.md', 'indexes-and-caches-review', 'review',
     'scale', 'indexes, caches, packs, flat cache, scan cache, 0.25.0',
     'What sgit already holds as indexes and caches after 0.25.0, by name; why the commands still slow on the '
     'newsroom\'s vault were where no cache existed yet; and the one index worth adding first: the flat map of a '
     'head, carried in the pack.'),
    ('10/22/feature-reference__pack-mode.md', 'pack-mode-feature-reference', 'reference',
     'write-path, scale', 'packs, release, 0.24.0, compression, compaction, gate',
     'The CLI team\'s one-page reference for pack mode as released in sgit-ai 0.24.0: what it is and why, the '
     'commands, the host layout, compression, the numbers to quote, compatibility and the gate, the security '
     'model and the tests.'),
    ('10/22/workflow__pack-mode-from-idea-to-release.md', 'pack-mode-idea-to-release', 'workflow',
     'write-path', 'packs, process, review, release',
     'How pack mode went from a measured problem to a release in eight days: research before code, a spec '
     'reviewed before the build, tests on a counted host, a live trial, four verification rounds by a second '
     'agent, and the documents each step left behind.'),
    ('10/21/note__pack-mode-round-trip.md', 'pack-mode-round-trip-measured', 'measurement',
     'write-path, scale', 'packs, round-trip, import, export, performance',
     'What was built for pack mode, how the round trip from a normal vault to a pack vault and back is tested, '
     'and every measurement: the synthetic request-count gates, the live trial with the comms vault\'s 33,000 '
     'objects (a 25 s clone against 3½ minutes), and the reviewer\'s numbers.'),
    ('10/21/howto__test-pack-mode.md', 'pack-mode-testers-howto', 'how-to',
     'write-path', 'packs, testing, how-to',
     'The CLI team\'s page for testing pack mode on throwaway vaults, step by step: create, push and pull '
     'between clones, compaction, the round trip, what to report and the known limits.'),
    ('10/21/response__pack-mode-verification.md', 'pack-mode-verification-response-1', 'response',
     'write-path, security-review, correctness', 'packs, review, fixes',
     'The CLI team\'s answer to the first verification round: all eight findings agreed and fixed with a test '
     'each, three more found in its own pass, and the how-to corrected.'),
    ('10/21/response__pack-mode-verification-round-2.md', 'pack-mode-verification-response-2', 'response',
     'write-path, security-review, correctness', 'packs, review, fixes',
     'The answer to round two: a clone chooses its snapshot by the branch head, a pack that names a member '
     'twice is refused whole, an aborted compaction takes its snapshot back, and the gate exemption checks '
     'every feature.'),
    ('10/21/response__pack-mode-verification-round-3.md', 'pack-mode-verification-response-3', 'response',
     'write-path, security-review, correctness', 'packs, review, fixes',
     'The answer to round three: the round-two clean-up was the bug, so an aborted compaction now leaves its '
     'snapshot; a 404 on an already archived pack is success; the gate exemption needs the hex form.'),
    ('10/21/response__pack-mode-verification-round-4.md', 'pack-mode-verification-response-4', 'response',
     'write-path, security-review', 'packs, review, fixes',
     'The answer to round four: no blockers, and the three nits done; "already gone" is decided by the status '
     'code, never by "404" inside a pack name.'),
    ('10/21/spec__pack-mode.md', 'pack-mode-spec', 'spec',
     'write-path, scale', 'packs, zip, push, pull, clone, compaction, s3',
     'The specification for pack mode: every push writes one zip pack, a snapshot pack compacts them, nothing is '
     'deleted, large packs go straight to S3 by presigned URL, and a gated packs-only vault needs no server '
     'change. Commands, layout, failure handling, tests and the four performance runs.'),
    ('10/20/brief__to-sg-send-team__zip-append-via-s3.md', 'zip-append-via-s3-brief', 'brief',
     'write-path', 'zip, s3, presigned, multipart, sg-send, server',
     'A brief to the SG/Send team: a presigned append route that grows a zip on S3 by UploadPartCopy, '
     'conditional completes with If-Match and If-None-Match, and size and ETag with the read URL. Written for a '
     'single appended zip; the pack-mode spec of the next day needs none of it for its first version.'),
    ('10/16/research__keys-pki-cow__coverage-map.md', 'keys-pki-copy-on-write-coverage-map', 'coverage map',
     'keys, write-path', 'keys, pki, copy-on-write, membership',
     'Before writing two articles, a map of what is already published on keys the way git does them, PKI '
     'access to a vault and copy-on-write: seven questions from the memo, where each stands, the facts the'
     ' articles must not get wrong, and seven code questions for the thread.'),
    ('10/16/response__scion-and-sgit-article.md', 'response-to-scion-and-sgit', 'review',
     'scale', 'performance, architecture, newsroom',
     'The CLI team\'s response to the newsroom\'s "Scion and sgit" article: what it gets right, the three '
     'factual errors, and the measurements from a 35k-object vault the article should have carried.'),
    ('10/14/response__sgit-issues-2026-10-14.md', 'sgit-issues-2026-10-14', 'fix',
     'scale, correctness', 'pull, fetch, large-files',
     'The issues reported on 14 October, each traced to its cause in the code, with what was fixed in the '
     'same push and what was left open.'),
    ('10/13/security-ci__pipeline-and-ai-review.md', 'security-ci-and-ai-review', 'design',
     'security-review', 'security, ci, ai-review',
     'A dedicated security pipeline on every pull request, and a keyless AI security review that can break'
     ' the build on anything new: why, how it is wired, and what it costs per reviewed change.'),
    ('10/13/AC-L-001__non-ascii-paths__refuse-dont-rewrite.md', 'non-ascii-paths-refuse-dont-rewrite', 'finding',
     'security-review, correctness', 'security, paths, bug',
     'Characters outside a narrow set in a path are silently rewritten, so one vault gets two roots and a '
     'false push conflict. What really happens, reproduced, and a fix that raises an alarm instead of '
     'rewriting.'),
    ('10/12/research__sgit-serve-local-vault-server.md', 'sgit-serve-running-a-vault-locally', 'research',
     'serve', 'serve, local, api',
     "How to run a vault locally: the vault server's API inventory, the browser modes, when TLS is and is "
     'not needed, and how much plumbing sgit would need.'),
    ('10/12/options__sgit-serve-container-and-static.md', 'sgit-serve-container-first', 'decision',
     'serve', 'serve, containers, docker',
     'The decision to run the SG/Send container image rather than re-implement the server: the runtimes '
     "supported (including Apple's container and Podman), the spike results, and phase 1 as built."),
    ('10/11/research__security-review-skills.md', 'security-review-skills', 'research',
     'security-review', 'security, skills, agents',
     'Agent skills for security review, each checked at its source, ranked by whether it brings a method, '
     'a tool with deterministic output, or vets the other skills, against this code base.'),
    ('10/11/research__threat-modeling-tools.md', 'threat-modeling-tools', 'research',
     'security-review', 'security, threat-modeling',
     "Threat-modeling tools for an agent-driven review: Matt Adams' stack (STRIDE GPT, the insider-threat "
     'model), the classics, and the house method, with the agent itself named as an actor.'),
    ('10/11/plan__security-review-with-skills.md', 'security-review-plan', 'plan',
     'security-review', 'security, review',
     'The plan for a tool-assisted, data-producing security review of one slice of sgit-ai: the code the '
     'zero-knowledge guarantee and the trust boundaries live in.'),
    ('10/11/case-study/README.md', 'security-review-case-study', 'case study',
     'security-review', 'security, review, tools',
     'What each tool found in the round-1 security review of sgit-ai 0.21.0, with counts and cost: the '
     'skill vetting, the derived graph, 270 function records, 68 STRIDE threats and the insider overlay.'),
    ('10/09/design-analysis__read-write-keys-as-pki.md', 'read-write-keys-as-pki', 'analysis',
     'keys', 'pki, keys, crypto',
     'Are the read key and the write key really a public and a private key? Half right: the write key '
     'should become a signing key, and the read key cannot become a public key. What that would take.'),
    ('10/09/design__native-pki-vault-mode.md', 'native-pki-vault-mode', 'design',
     'keys', 'pki, vault-format, crypto',
     'An architecture map for a second vault mode built on key pairs from the start, revised twice after '
     'review: sequence-number pinning, frozen hosts, concurrent writers.'),
    ('10/09/design__sealed-files-layer.md', 'sealed-files-layer', 'design',
     'keys', 'crypto, sealed-files, pki',
     'A second encryption layer on top of either vault mode: files sealed to named recipients with ECDH '
     "P-256, HKDF and AES-256-GCM, with the corrections from the sgit.ai agent's review."),
    ('10/08/future-features__after-0.21.md', 'future-features-after-0-21', 'roadmap',
     'integrity', 'roadmap, git-parity, compatibility',
     'The git-parity and security ideas that are not in 0.21.0, what each would take and what it could '
     "break, starting from the constraint that a new commit field breaks older clients' signature checks."),
    ('10/08/review__git-to-sgit-security-mapping.md', 'git-to-sgit-security-mapping', 'review',
     'integrity, security-review', 'security, git',
     "A review of the one-way map from git's security features to sgit, checked against the code: three "
     'corrections, one missing gap, and the four easy gaps closed for 0.21.0.'),
    ('10/08/test-suite__branches-performance-quality-review.md', 'branches-and-test-suite-review', 'review',
     'correctness', 'branches, tests, quality',
     'An end-to-end check found that branches did not work. What was fixed behind it, the tests that now '
     "cover it, and a review of the test suite's speed and quality."),
    ('10/07/history-integrity__cost-and-compatibility.md', 'history-integrity-cost-and-compatibility', 'measurement',
     'integrity', 'integrity, signatures, performance',
     'What signature verification, ref monotonicity and 128-bit ids would cost, measured on a real vault, '
     'and how to ship all three without a vault move.'),
    ('10/07/compatibility-matrix__cli-x-web-ui-x-api.md', 'compatibility-matrix-cli-web-ui-api', 'analysis',
     'integrity', 'compatibility, web-ui, api',
     'The CLI, the vault web UI and the SG/Send API across the integrity roll-out, step by step: what each'
     ' version reads, writes and loses, under the rule that no client may break another still writing.'),
    ('10/06/partial-clones__scope-and-depth.md', 'partial-clones-scope-and-depth', 'design',
     'scale', 'clone, partial-clones, agents',
     'Cloning just the folders an agent reads and writes, read and write, plus a shallow mode, without '
     'changing the full clone: the Merkle-spine idea and the measurements.'),
    ('10/03/pull-discards-uncommitted-edits__fix.md', 'pull-discarded-uncommitted-edits', 'fix',
     'correctness', 'pull, bug, working-tree',
     "sgit pull silently discarded uncommitted edits to tracked files. The root cause, and the fix: git's "
     'rules for the working tree, applied before any write.'),
    ('10/02/clone-performance__shared-subtree-refetch.md', 'clone-refetched-shared-subtrees', 'measurement',
     'scale', 'performance, clone',
     'A clone stuck walking trees: the walk re-fetched shared sub-trees once per parent, 10,098 requests '
     'for 2,236 unique trees. The instrumented run and the fix.'),
]

# The CLI's article drafts were converted into articles on this site (admin/content/articles/, newsroom format) by
# hand, once. A research document that names one in backticks links to the article.
ARTICLE_DRAFTS = {
    "article-draft__one-vault-ten-agents-measured.md": "one-vault-ten-agents-measured",
    "article-draft__sgit-is-a-standard-one-hash-away.md": "sgit-is-a-standard-one-hash-away",
    "article-draft__keys-the-way-git-does-it.md": "keys-the-way-git-does-it",
    "article-draft__copy-on-write-and-the-vault.md": "copy-on-write-and-the-vault",
    "article-draft__policies-the-vault-enforces.md": "policies-the-vault-enforces",
    "article-draft__streaming-changes.md": "streaming-changes-into-a-vault",
    "article-draft__native-zip-support.md": "a-vault-in-one-file",
    "article-draft__a-pack-per-push.md": "a-pack-per-push",
}


def git(cli, *args):
    return subprocess.run(["git", "-C", str(cli), *args], check=True, capture_output=True, text=True).stdout.strip()


def link(name, by_name):
    if name in by_name:
        return f"[`{name}`](/research/{by_name[name]}.html)"
    if name in ARTICLE_DRAFTS:
        return f"[`{name}`](/articles/{ARTICLE_DRAFTS[name]}.html)"
    return f"`{name}`"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cli", required=True, help="a clone of SGit-AI/SGit-AI__CLI, at the commit to publish from")
    ap.add_argument("--branch", default="dev", help="the branch that commit is on, stated on each document")
    ap.add_argument("--only", nargs="*", help="import only these slugs; the others keep the commit they came from")
    args = ap.parse_args()
    cli = Path(args.cli)
    commit = git(cli, "rev-parse", "HEAD")
    by_name = {Path(src).name: slug for src, slug, *_ in DOCS}
    OUT.mkdir(parents=True, exist_ok=True)
    for src, slug, kind, topics, tags, summary in DOCS:
        if args.only and slug not in args.only:
            continue
        path = f"{FOLDER}/{src}"
        text = (cli / path).read_text()
        title = re.search(r"^# (.+)$", text, re.M).group(1).strip()
        month, day = src.split("/")[:2]
        date = f"2026-{month}-{day}"
        first = git(cli, "log", "--diff-filter=A", "--format=%cI", "-1", "--", path)
        body = re.sub(r"`([^`\s/]+\.md)`", lambda m: link(m.group(1), by_name), text.strip("\n"))
        (OUT / f"{slug}.md").write_text(
            "---\n"
            f"title: {title}\n"
            f"date: {date}\n"
            + (f"time: {first[11:16]}\n" if first.startswith(date) else "")
            + "section: research\n"
            f"kind: {kind}\n"
            f"topics: [{topics}]\n"
            f"tags: {tags}\n"
            f"summary: {summary}\n"
            "author: the sgit-ai CLI team (Claude Code sessions), for Dinis Cruz\n"
            f"source: {GH}/{commit}/{path}\n"
            f"source_path: {path}\n"
            f"source_commit: {commit[:7]}\n"
            f"source_branch: {args.branch}\n"
            "status: published\n"
            "---\n\n" + body + "\n")
        print(f"  · {slug}  ({date}, {len(body.split())} words)")
    count = len(args.only) if args.only else len(DOCS)
    print(f"import_cli_research: {count} research documents from SGit-AI__CLI@{commit[:7]} ({args.branch})")


if __name__ == "__main__":
    sys.exit(main())
