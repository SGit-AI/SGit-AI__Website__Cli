# How a vault takes writes, cli.sgit.ai

> One commit per change is right for documents and wrong for a stream. Copy-on-write, a write-ahead append lane folded into signed commits, and a vault in one zip file: what sgit already does, and what is proposed.

*Source: <https://cli.sgit.ai/research/topics/write-path.html> · generated from the same content as the page, so the two cannot drift.*

---
# How a vault takes writes

**The question.** Every change in sgit is a commit: a tree rebuild, a signature and a compare-and-swap on one ref. That suits documents and does not suit an agent writing a line a second, or an API log in bursts. Can a vault take many small writes, attribute every one, and still store only whole, immutable objects?

## Where it stands

| | Status | Where it is said |
|---|---|---|
| Copy-on-write at the object level: a branch is a pointer, a commit shares every unchanged folder | **shipped** (git's design) | [the article](../../articles/copy-on-write-and-the-vault.md) |
| Append lanes: writes with no account and no tree, measured at a thousand entries from a hundred writers in 4.9 s | **shipped** on the server | [Append lanes](../../api/append-lanes.md) |
| A write-ahead lane folded into signed commits, with provenance kept per entry | **proposed**, protocol written out | [Streaming changes](../../articles/streaming-changes-into-a-vault.md) |
| Head and delta zips per commit | **shipped** (`sgit publish --bundles`) | [`sgit publish`](../../reference/publish.md), [the article](../../articles/a-vault-in-one-file.md) |
| A clone that reads a bundle, a bare store that lives in one file | **proposed** | [the article](../../articles/a-vault-in-one-file.md) |
| Copy-on-write inside a large file (content-defined chunks) | **proposed**, later | [the coverage map](../../research/keys-pki-copy-on-write-coverage-map.md) |

## Articles from this topic

- [Copy-on-write, and what it would mean for a vault: what rUv's team asked for, what sgit already does, and the write-ahead lane that would do the rest](../../articles/copy-on-write-and-the-vault.md): After I presented ruv.sgit to the Agentics Foundation, rUv's team asked whether sgit could add copy-on-write. I wanted to know what that would mean for a vault before saying yes or no. Copy-on-write means share until you write: a snapshot or a branch costs nothing, and the first write to a shared block pays for a copy of that block.
- [Streaming changes into a vault: a thousand small writes, one commit, every line attributed](../../articles/streaming-changes-into-a-vault.md): Every change in a vault is a commit, and a commit is a tree rebuild, a signature and a compare-and-swap on one ref. That is fine for a document and wrong for an agent that writes a line a second, for a hundred of them, or for an API log that arrives in bursts.
- [A vault in one file: native zip support for sgit, where it wins, where it loses, and what already exists](../../articles/a-vault-in-one-file.md): A vault is files and folders, so it can be a zip. Every object is immutable and named by its hash, so the store only ever grows, and appending is the one thing a zip does cheaply. I asked how much of that already exists, and the…

## The research documents, newest first

- [Keys the way git does them, PKI access to a vault, and copy-on-write: what is already published, and what is not](../../research/keys-pki-copy-on-write-coverage-map.md): Before writing two articles, a map of what is already published on keys the way git does them, PKI access to a vault and copy-on-write: seven questions from the memo, where each stands, the facts the articles must not get wrong,…

---

*[Site index for agents](../../llms.txt) · [HTML version](https://cli.sgit.ai/research/topics/write-path.html)*
