---
title: Running a vault locally
summary: How to run a working vault, UI and API, on your own machine: the research into the server's API, the decision to run the SG/Send container rather than re-implement it, and the runtimes sgit supports.
section: topics
order: 5
question: Can anyone clone a vault and run it on their own machine, UI and API, with one command?
articles: []
---

# Running a vault locally

**The question.** "Just clone a vault and run it from there." Can sgit run a working vault, the web UI and the API, on a laptop, with no TLS to set up and no server to write?

## Where it stands

| | Status | Where it is said |
|---|---|---|
| The vault server's API, inventoried; when TLS is and is not needed | **research**, 12 October | [Running a vault locally](/research/sgit-serve-running-a-vault-locally.html) |
| Run the SG/Send container image rather than re-implement the server; Docker, Podman and Apple's `container` | **decided** 12 October; phase 1 built | [Container first](/research/sgit-serve-container-first.html) |
| `sgit serve` and its subcommands (install, runtimes, status, logs, push, pull, stop, update) | **shipped**; in the 0.23.0 reference | [`sgit serve`](/reference/serve.html) |
| Self-hosting a server for agents in VMs, containers and the cloud | **documented** | [Self-hosting for agents](/docs/self-host-for-agents.html) |

!topic serve
