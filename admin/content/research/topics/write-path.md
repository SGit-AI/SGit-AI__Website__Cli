---
title: How a vault takes writes
summary: One commit per change is right for documents and wrong for a stream. Copy-on-write, a write-ahead append lane folded into signed commits, and a vault in one zip file: what sgit already does, and what is proposed.
section: topics
order: 4
question: Can a vault take a thousand small writes a second, keep who wrote each one, and still store whole, immutable, cacheable objects?
articles: [copy-on-write-and-the-vault, streaming-changes-into-a-vault, a-vault-in-one-file]
---

# How a vault takes writes

**The question.** Every change in sgit is a commit: a tree rebuild, a signature and a compare-and-swap on one ref. That suits documents and does not suit an agent writing a line a second, or an API log in bursts. Can a vault take many small writes, attribute every one, and still store only whole, immutable objects?

## Where it stands

| | Status | Where it is said |
|---|---|---|
| Copy-on-write at the object level: a branch is a pointer, a commit shares every unchanged folder | **shipped** (git's design) | [the article](/articles/copy-on-write-and-the-vault.html) |
| Append lanes: writes with no account and no tree, measured at a thousand entries from a hundred writers in 4.9 s | **shipped** on the server | [Append lanes](/api/append-lanes.html) |
| A write-ahead lane folded into signed commits, with provenance kept per entry | **proposed**, protocol written out | [Streaming changes](/articles/streaming-changes-into-a-vault.html) |
| Head and delta zips per commit | **shipped** (`sgit publish --bundles`) | [`sgit publish`](/reference/publish.html), [the article](/articles/a-vault-in-one-file.html) |
| A clone that reads a bundle, a bare store that lives in one file | **proposed** | [the article](/articles/a-vault-in-one-file.html) |
| Copy-on-write inside a large file (content-defined chunks) | **proposed**, later | [the coverage map](/research/keys-pki-copy-on-write-coverage-map.html) |

!topic write-path
