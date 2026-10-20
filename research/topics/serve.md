# Running a vault locally, cli.sgit.ai

> How to run a working vault, UI and API, on your own machine: the research into the server's API, the decision to run the SG/Send container rather than re-implement it, and the runtimes sgit supports.

*Source: <https://cli.sgit.ai/research/topics/serve.html> · generated from the same content as the page, so the two cannot drift.*

---
# Running a vault locally

**The question.** "Just clone a vault and run it from there." Can sgit run a working vault, the web UI and the API, on a laptop, with no TLS to set up and no server to write?

## Where it stands

| | Status | Where it is said |
|---|---|---|
| The vault server's API, inventoried; when TLS is and is not needed | **research**, 12 October | [Running a vault locally](../../research/sgit-serve-running-a-vault-locally.md) |
| Run the SG/Send container image rather than re-implement the server; Docker, Podman and Apple's `container` | **decided** 12 October; phase 1 built | [Container first](../../research/sgit-serve-container-first.md) |
| `sgit serve` and its subcommands (install, runtimes, status, logs, push, pull, stop, update) | **shipped**; in the 0.23.0 reference | [`sgit serve`](../../reference/serve.md) |
| Self-hosting a server for agents in VMs, containers and the cloud | **documented** | [Self-hosting for agents](../../docs/self-host-for-agents.md) |

## The research documents, newest first

- [`sgit serve`: container first. Options map and spike results](../../research/sgit-serve-container-first.md): The decision to run the SG/Send container image rather than re-implement the server: the runtimes supported (including Apple's container and Podman), the spike results, and phase 1 as built.
- [`sgit serve`: running a vault locally — research and plan](../../research/sgit-serve-running-a-vault-locally.md): How to run a vault locally: the vault server's API inventory, the browser modes, when TLS is and is not needed, and how much plumbing sgit would need.

---

*[Site index for agents](../../llms.txt) · [HTML version](https://cli.sgit.ai/research/topics/serve.html)*
