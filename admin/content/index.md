---
title: cli.sgit.ai
summary: sgit is version control for files the host must never read. It has Git's verbs, and it does twelve things Git has no equivalent for: a host that reads nothing, read keys that work from any static host, custody without access, writes without reads, one folder by byte ranges, indexes the writer ships encrypted, policy the vault carries, rewinds refused by name. This is its documentation: every command generated from the CLI's own parser, the HTTP API, the guides, and the research.
section: home
---

# sgit: version control for files the host must never read

sgit clones, commits, branches and merges files that are encrypted on your machine before they leave it. The host stores ciphertext under opaque ids and never sees a file name, a file's contents, a commit message or a branch name. It has Git's verbs, so a Git user is at home in an hour. And because the host reads nothing, it does things Git cannot do at all.

```text
$ pip install sgit-ai          # Python 3.11 or later; installs `sgit` and `sgit-ai`
$ sgit create my-vault         # prints the vault key once: keep it in a password manager
$ cd my-vault && echo "# Plan" > plan.md
$ sgit commit -m "add the plan" && sgit push
$ sgit clone <vault-key>       # anywhere else, a person or an agent
```

## What only sgit does {#only-sgit}

| | |
|---|---|
| **The host reads nothing** | contents, names, messages and branches are encrypted on the client; git-crypt leaves names and messages in clear |
| **Read keys, no accounts** | a read key cannot become write access, and reads from any static host: [`clone --read-key`](/reference/clone.html), [`publish`](/reference/publish.html) |
| **Custody without access** | a backup host copies and verifies a vault it cannot read: [`vault mirror`](/reference/vault.html) |
| **Write without read** | an append lane takes a deposit and tells the sender nothing: [append lanes](/api/append-lanes.html) |
| **Agents on one huge vault, one folder each** | a folder by byte ranges from plain storage, 2.8 s against 36 on 76,000 files; commits outside the folder refused by name; two folders never conflict: [0.26.0](/docs/update-to-0-26-0.html) |
| **Trust carried by the vault** | a format gate and `signatures-required` every client enforces; rewinds refused by name; a secret guard at commit; key rotation |

!shot sg-map.webp | /articles/images/ | sgit and Git, row by row, against sgit-ai 0.26.0. Twelve things only sgit does, from a host that reads nothing to files sealed to a person. Fifteen both do, with sgit's difference. Sixteen where Git is ahead, fourteen of which sgit can build on the client without giving up zero knowledge. And six that zero knowledge rules out, each with a client-side substitute. | comparison

Git is still ahead on line-level merges, blame, bisect, its forges and twenty years of tooling. Almost all of that runs on the client in Git too, so sgit can build it; what it can never do is anything that needs the host to read your files. **The full map, row by row, with the commands and the qualifiers: [sgit and Git](/docs/sgit-and-git.html).**

**Where things are.** The project, the vault platform and what is built on top of it are on [sgit.ai](https://sgit.ai). Everything about the command-line tool is here.

| | |
|---|---|
| **[Get started](/docs/index.html)** | [sgit and Git](/docs/sgit-and-git.html), what sgit is, install, the five-minute quickstart, the git-to-sgit mapping, the two-branch model, and the honest page about its limits |
| **[Command reference](/reference/index.html)** | All {{command_count}} commands of sgit-ai {{cli_version}}, generated from `sgit help all --format json`, so it describes the code and not somebody's memory of it |
| **[Guides](/docs/index.html#guides)** | Partial clones, history integrity, agents sharing one vault, messages between vaults, self-hosting, the update notices |
| **[Security](/security/index.html)** | The security model, key management, credentials and the PKI commands |
| **[HTTP API](/api/index.html)** | The surface the CLI and the browser are both clients of: authentication, vault objects, transfers, append lanes, errors |
| **[Research](/research/index.html)** | {{research_count}} documents from the CLI team, published as written, in {{topic_count}} topics: measurements, designs and the reviews that corrected them, security reviews, and the bugs found in daily use |
| **[Articles](/articles/index.html)** | {{article_count}} articles in the newsroom's format, each one argument: written up from Dinis Cruz's memos, or by an agent about what it delivered |

## Latest articles

The six newest of the [{{article_count}} articles](/articles/index.html).

!list articles 6

## Research topics

Each topic is one open question, with what is shipped, what is designed and what is absent. [All {{research_count}} research documents →](/research/index.html)

!list topics

## For agents

Every page has a markdown twin at the same path (swap `.html` for `.md`), and [/llms.txt](/llms.txt) indexes them all; [/llms-full.txt](/llms-full.txt) is the whole site in one file. The command reference is also published as the JSON the CLI emits, [/reference/sgit-cli-reference.json](/reference/sgit-cli-reference.json), so two releases can be diffed rather than re-read. Your installed copy answers the same question offline: `sgit help all --format json`.

*Site {{site_version}}. This site was started on 20 October 2026 from [a brief published in full](/briefs/index.html); some of its pages [moved here from sgit.ai](/admin/moved.html) the same day.*
