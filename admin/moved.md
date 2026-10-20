# What moved from sgit.ai, cli.sgit.ai

> The pages that moved from sgit.ai to cli.sgit.ai on 20 October 2026, each at the same path, and why: the CLI now has use cases of its own, and sgit.ai is the umbrella.

*Source: <https://cli.sgit.ai/admin/moved.html> · site v0.1.0 · generated from the same content as the page, so the two cannot drift.*

---
# What moved from sgit.ai

On 20 October 2026 the CLI's most technical pages moved here from sgit.ai, as [the brief](../briefs/index.md) asks: the CLI now has a set of use cases of its own, and sgit.ai is the umbrella for the project and its commercial side. Each page kept its path, so `sgit.ai/docs/quickstart.html` is now `cli.sgit.ai/docs/quickstart.html`, and a redirect on sgit.ai is one rule.

The pages were taken from sgit.ai's markdown twins, which are generated from the same source as its HTML, at sgit.ai site v0.7.87, by `admin/build/import_sgit_ai.py`. The text is unchanged. Links to a page that moved now stay on this site; links to anything else go back to sgit.ai.

| Was on sgit.ai | Is now | Section here |
|---|---|---|
| <https://sgit.ai/api/append-lanes.html> | [Append lanes](../api/append-lanes.md) | HTTP API |
| <https://sgit.ai/api/authentication.html> | [Authentication](../api/authentication.md) | HTTP API |
| <https://sgit.ai/api/errors.html> | [Errors and limits](../api/errors.md) | HTTP API |
| <https://sgit.ai/api/index.html> | [The HTTP API](../api/index.md) | HTTP API |
| <https://sgit.ai/api/transfers.html> | [The transfer API, one encrypted handover, one link](../api/transfers.md) | HTTP API |
| <https://sgit.ai/api/vault-objects.html> | [Vault objects](../api/vault-objects.md) | HTTP API |
| <https://sgit.ai/docs/agents-sharing-one-vault.html> | [Agents sharing one vault](../docs/agents-sharing-one-vault.md) | Guides |
| <https://sgit.ai/docs/agents.html> | [Working with AI agents](../docs/agents.md) | Guides |
| <https://sgit.ai/docs/append-lane-messaging.html> | [Append-lane messaging between agents that hold no one else's vault key](../docs/append-lane-messaging.md) | Guides |
| <https://sgit.ai/docs/credentials.html> | [Vault credentials: what each one can do, and what its prefix declares](../docs/credentials.md) | Security |
| <https://sgit.ai/docs/history-integrity.html> | [History integrity: the format gate, verifying signatures, and rewinds](../docs/history-integrity.md) | Guides |
| <https://sgit.ai/docs/how-to/claude-team-egress.html> | [Using sgit from Claude on a Team or Enterprise plan: the network allowlist](../docs/how-to/claude-team-egress.md) | Guides |
| <https://sgit.ai/docs/installation.html> | [Installation](../docs/installation.md) | Get started |
| <https://sgit.ai/docs/key-management.html> | [Vault key management: where each key lives, and how it travels](../docs/key-management.md) | Security |
| <https://sgit.ai/docs/limitations.html> | [When NOT to use sgit](../docs/limitations.md) | Get started |
| <https://sgit.ai/docs/partial-clones.html> | [Partial clones: a folder scope and a history depth](../docs/partial-clones.md) | Guides |
| <https://sgit.ai/docs/pki.html> | [Keys, signatures and encrypting to someone else](../docs/pki.md) | Security |
| <https://sgit.ai/docs/quickstart.html> | [Quickstart](../docs/quickstart.md) | Get started |
| <https://sgit.ai/docs/self-host-for-agents.html> | [Self-hosting a vault server for agents](../docs/self-host-for-agents.md) | Guides |
| <https://sgit.ai/docs/send-a-vault-key.html> | [Send a vault key to the registry](../docs/send-a-vault-key.md) | Guides |
| <https://sgit.ai/docs/sgit-for-git-users.html> | [sgit for git users](../docs/sgit-for-git-users.md) | Get started |
| <https://sgit.ai/docs/two-branch-model.html> | [The two-branch model](../docs/two-branch-model.md) | Get started |
| <https://sgit.ai/docs/update-to-0-18-0.html> | [Update sgit-ai to 0.18.0](../docs/update-to-0-18-0.md) | Guides |
| <https://sgit.ai/docs/update-to-0-21-0.html> | [Update sgit-ai to 0.21.0](../docs/update-to-0-21-0.md) | Guides |
| <https://sgit.ai/docs/vault-messaging.html> | [Sending messages between vaults](../docs/vault-messaging.md) | Guides |
| <https://sgit.ai/docs/what-is-sgit.html> | [What is sgit](../docs/what-is-sgit.md) | Get started |
| <https://sgit.ai/security/index.html> | [Security model](../security/index.md) | Security |

## What stayed on sgit.ai, and why

- **Vaults as a platform**: vault apps, `_page.json`, the browser bridge, sub-vaults, static hosting, publishing a vault, and the guidance for working on one. They are about the vault, not the command line.
- **The project**: why it exists, use cases, case studies, the published vaults, comparisons, the newsroom, partnerships.
- **The docs hub and the agent-contact protocol**, which serve the whole network.

## What sgit.ai still has to do

This site cannot change sgit.ai. Until sgit.ai's team acts, both copies exist, and **the copy here is the one maintained from now on**. The request to them, as recorded in [the corrections file](../admin/corrections.md):

1. Point each moved page at its new address: a link at the top, then a redirect.
2. Point sgit.ai's docs hub and `llms.txt` at cli.sgit.ai for the CLI.
3. Add cli.sgit.ai to the network directory (`admin/content/sites/cli.md`, the Cartographer's file).

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/admin/moved.html)*
