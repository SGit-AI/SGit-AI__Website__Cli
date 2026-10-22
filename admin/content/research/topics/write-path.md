---
title: How a vault takes writes
summary: One commit per change is right for documents and wrong for a stream, and many small objects cost a request each. Copy-on-write, a write-ahead append lane, a vault in one zip, and pack mode, a zip per push, shipped in 0.24.0: what sgit already does, and what is proposed.
section: topics
order: 4
question: Can a vault take a thousand small writes a second, keep who wrote each one, and still store whole, immutable, cacheable objects?
articles: [pack-mode-four-rounds, is-there-any-overhead, a-vault-you-can-carry, a-pack-per-push, pack-mode-read-closely, a-vault-in-one-file, copy-on-write-and-the-vault, streaming-changes-into-a-vault]
---

# How a vault takes writes

**The question.** Every change in sgit is a commit: a tree rebuild, a signature and a compare-and-swap on one ref. That suits documents and does not suit an agent writing a line a second, or an API log in bursts. Can a vault take many small writes, attribute every one, and still store only whole, immutable objects? And since the cost over the network is the number of requests, not the bytes, can the objects travel in a few files instead of thousands?

## Where it stands

| | Status | Where it is said |
|---|---|---|
| Copy-on-write at the object level: a branch is a pointer, a commit shares every unchanged folder | **shipped** (git's design) | [the article](/articles/copy-on-write-and-the-vault.html) |
| Append lanes: writes with no account and no tree, measured at a thousand entries from a hundred writers in 4.9 s | **shipped** on the server | [Append lanes](/api/append-lanes.html) |
| A write-ahead lane folded into signed commits, with provenance kept per entry | **proposed**, protocol written out | [Streaming changes](/articles/streaming-changes-into-a-vault.html) |
| Head and delta zips per commit | **shipped** (`sgit publish --bundles`) | [`sgit publish`](/reference/publish.html), [the article](/articles/a-vault-in-one-file.html) |
| A clone that reads a bundle, a bare store that lives in one file | **proposed** | [the article](/articles/a-vault-in-one-file.html) |
| Zip64: 70,000 members and 5 GiB written and read back | **verified** 20 October | [the article](/articles/a-vault-in-one-file.html#does-not-fit) |
| Presigned multipart upload and `Range` reads on the live server | **tested** 20 October, work today | [the article](/articles/a-vault-in-one-file.html#works-today-tested) |
| An append route on the server: `UploadPartCopy` and `If-Match` on complete | **parked** 21 October: the brief now says not to build it; not needed by pack mode's first version | [the brief](/research/zip-append-via-s3-brief.html), [the review](/articles/pack-mode-read-closely.html#brief) |
| **Pack mode**: one pack per push, a snapshot to compact, an archive, a gated packs-only vault, no server change | **shipped** in sgit-ai 0.24.0, opt-in (`sgit init --packs`, `sgit pack import`); built and measured 21 October, verified in four rounds 21 and 22 October | [release notes](/docs/update-to-0-24-0.html), [playbook for agents](/docs/pack-mode-for-agents.html), [the spec](/research/pack-mode-spec.html), [measurements](/research/pack-mode-round-trip-measured.html), [the four rounds](/articles/pack-mode-four-rounds.html) |
| Copy-on-write inside a large file (content-defined chunks) | **proposed**, later | [the coverage map](/research/keys-pki-copy-on-write-coverage-map.html) |
| Compressing blobs before encryption: 1.58 times smaller on the comms vault's files, 1.66 on a published 2,087-object vault | **shipped** on pack vaults in 0.24.0 (`--no-deflate` on import turns it off) | [the feature reference](/research/pack-mode-feature-reference.html) |
| **A vault in one file**: the `bare/` folder zipped, optionally sealed to a public key, cloned from the unpacked folder | **works today** with shipped commands, measured 21 October; one command and a direct clone are proposed | [the article](/articles/a-vault-you-can-carry.html) |

!topic write-path
