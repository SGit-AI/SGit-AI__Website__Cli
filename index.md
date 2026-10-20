# cli.sgit.ai, cli.sgit.ai

> The documentation for sgit, the command-line tool for encrypted vaults: every command generated from the CLI's own parser, the HTTP API it is a client of, the guides, and the CLI team's research as articles.

*Source: <https://cli.sgit.ai/index.html> · site v0.1.0 · generated from the same content as the page, so the two cannot drift.*

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
| **[Get started](docs/index.md)** | What sgit is, install, the five-minute quickstart, the git-to-sgit mapping, the two-branch model, and the honest page about its limits |
| **[Command reference](reference/index.md)** | All 158 commands of sgit-ai v0.23.0, generated from `sgit help all --format json`, so it describes the code and not somebody's memory of it |
| **[Guides](docs/index.md#guides)** | Partial clones, history integrity, agents sharing one vault, messages between vaults, self-hosting, the update notices |
| **[Security](security/index.md)** | The security model, key management, credentials and the PKI commands |
| **[HTTP API](api/index.md)** | The surface the CLI and the browser are both clients of: authentication, vault objects, transfers, append lanes, errors |
| **[Research](articles/index.md)** | 23 articles from the CLI team: measurements, designs, reviews and fixes, each taken as far as the evidence goes |

## Latest research

The six newest of the [23 articles](articles/index.md).

- [sgit is a standard, not a server: everything in a vault is one hash away](articles/sgit-is-a-standard-one-hash-away.md): A vault is a set of files laid out by a convention, every immutable object named by the hash of its own ciphertext, so the server is the least interesting part and anything in the path can cache blindly.
- [Response to "Scion and sgit" (newsroom.sgit.ai, article No. 141, v1.0.0)](articles/response-to-scion-and-sgit.md): The CLI team's response to the newsroom's "Scion and sgit" article: what it gets right, the three factual errors, and the measurements from a 35k-object vault the article should have carried.
- [One vault, ten agents, 35,000 objects: what sgit does when the repository is big and the clients are many](articles/one-vault-ten-agents-measured.md): What sgit does when the repository is big and the clients are many: the comms vault, 35,000 encrypted objects and ten agents, cloned eight ways and measured from a cloud sandbox.
- [Response to "sgit issues found on 14 October 2026", and the comms-vault performance report](articles/sgit-issues-2026-10-14.md): The issues reported on 14 October, each traced to its cause in the code, with what was fixed in the same push and what was left open.
- [Security CI: a dedicated pipeline, and an AI review that can break the build](articles/security-ci-and-ai-review.md): A dedicated security pipeline on every pull request, and a keyless AI security review that can break the build on anything new: why, how it is wired, and what it costs per reviewed change.
- [AC-L-001 / TM-R36 — characters outside `[a-zA-Z0-9/\_.- ]` in paths: what really happens](articles/non-ascii-paths-refuse-dont-rewrite.md): Characters outside a narrow set in a path are silently rewritten, so one vault gets two roots and a false push conflict. What really happens, reproduced, and a fix that raises an alarm instead of rewriting.

## For agents

Every page has a markdown twin at the same path (swap `.html` for `.md`), and [/llms.txt](llms.txt) indexes them all; [/llms-full.txt](llms-full.txt) is the whole site in one file. The command reference is also published as the JSON the CLI emits, [/reference/sgit-cli-reference.json](reference/sgit-cli-reference.json), so two releases can be diffed rather than re-read. Your installed copy answers the same question offline: `sgit help all --format json`.

*Site v0.1.0. This site was started on 20 October 2026 from [a brief published in full](briefs/index.md); some of its pages [moved here from sgit.ai](admin/moved.md) the same day.*

---

*[Site index for agents](llms.txt) · [HTML version](https://cli.sgit.ai/index.html)*
