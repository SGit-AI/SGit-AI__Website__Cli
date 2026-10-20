---
title: cli.sgit.ai
summary: The documentation for sgit, the command-line tool for encrypted vaults: every command generated from the CLI's own parser, the HTTP API it is a client of, the guides, and the CLI team's research as articles.
section: home
---

# The sgit CLI: git for encrypted vaults, documented from the code

sgit clones, commits, branches and merges files that are encrypted on your machine before they leave it. The server stores ciphertext under opaque ids and never sees a filename, a file's contents or a commit message. This site is the CLI's documentation: what each command does, the HTTP API underneath it, the guides for people and for agents, and the research behind the design.

```text
$ pip install sgit-ai          # Python 3.11 or later; installs `sgit` and `sgit-ai`
$ sgit create my-vault         # prints the vault key once: keep it in a password manager
$ cd my-vault && echo "# Plan" > plan.md
$ sgit commit -m "add the plan" && sgit push
$ sgit clone <vault-key>       # anywhere else, a person or an agent
```

**Where things are.** The project, the vault platform and what is built on top of it are on [sgit.ai](https://sgit.ai). Everything about the command-line tool is here.

| | |
|---|---|
| **[Get started](/docs/index.html)** | What sgit is, install, the five-minute quickstart, the git-to-sgit mapping, the two-branch model, and the honest page about its limits |
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
