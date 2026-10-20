---
title: Using sgit from Claude on a Team or Enterprise plan: the network allowlist
summary: On Claude Team and Enterprise plans an Owner sets the code sandbox's network access for the whole organisation, and the default blocks every sgit host. Which domains to allow (apex domains explicitly), how to check from inside a session, how a proxy's CONNECT 403 differs from a server outage, and why web fetch can read sgit.ai while the shell cannot.
section: guides
order: 9
moved_from: https://sgit.ai/docs/how-to/claude-team-egress.html
moved_version: v0.7.87
moved_on: 2026-10-20
---

# Using sgit from Claude on a Team or Enterprise plan: the network allowlist

On Claude's Team and Enterprise plans, the network access of Claude's code sandbox (Cowork, and code execution and file creation in claude.ai) is set once for the whole organisation, by an Owner. The Team default lets `pip install sgit-ai` through and blocks every sgit host. This page says which hosts to allow, how to check from inside a session, and how to tell a blocked host from a server that is down.

**Where this comes from.** An incident on 26 September 2026: an agent in a Claude Cowork cloud session, on sgit-ai v0.16.0, could install sgit and could not reach `sgit.ai`, and a second session confirmed the fix. It was written up as a brief for this site by `mailbox.riskmandate`. The statements about Claude's settings below are Anthropic's, from the two help-centre articles linked here; the statements about which domains matched are what the incident observed, and are labelled so.

## Who has to do this

An **Owner** of the Claude organisation. Members, and the agent itself, cannot change it. On Free, Pro and Max plans the user controls the same setting in their own settings instead. See Anthropic's [Create and edit files with Claude](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude) and [Use Claude Cowork on Team and Enterprise plans](https://support.claude.com/en/articles/13455879-use-claude-cowork-on-team-and-enterprise-plans) for the current menu path.

## The steps

1. In **Organization settings → Capabilities → Code execution**, set network access to **Package managers + custom domains**, or **All domains** if your policy allows it. Anthropic's four levels are Disabled, Package managers only (the Team and Enterprise default), Package managers + custom domains, and All domains. Package managers stay allowed at the third level, which covers `pip install sgit-ai`.
2. Add these domains. **List the apex domains explicitly**: in the incident, `*.sgit.ai` was allowed and `sgit.ai` itself was still blocked.

| Domain | Why |
|---|---|
| `dev.send.sgraph.ai`, or `*.sgraph.ai` | The sgit API server and the default `--base-url`: clone, pull, push, and the append lanes |
| `dev.vault.sgraph.ai`, covered by `*.sgraph.ai` | The web vault UI, if agents open vault links |
| `sgit.ai` | These docs and `llms.txt`. **Needed as the apex** |
| `*.sgit.ai` | `www.sgit.ai` and the other sites in the network |
| your own `--base-url` host | If you run your own sgit server |

3. Save, and **start a new session**. Anthropic says network settings are applied when a session is created, so a running session keeps the old ones. In the incident the change did reach a running session within about fifteen minutes; do not rely on that.

## Check it from inside the session

Paste this to the agent:

```
Run, and report each HTTP code:
  for h in sgit.ai www.sgit.ai dev.send.sgraph.ai dev.vault.sgraph.ai; do
    printf "%-22s " $h; curl -sS -o /dev/null -w '%{http_code}\n' --max-time 15 https://$h/; done
Then: pip install -U sgit-ai && sgit --version
Then: curl -sS "$HTTPS_PROXY/__agentproxy/status"   (report any recentRelayFailures)
Do not retry or route around any 403.
```

**Expected:** 200 everywhere, or 301 for `www.sgit.ai`, which redirects to `sgit.ai`. A code of `000` with `CONNECT tunnel failed, response 403` means that host is still missing from the allowlist.

## A blocked host is not a server outage

The sandbox reaches the internet through an egress proxy. A host that is not allowed fails at the proxy, before any request reaches sgit, and the failure looks like this:

```
> CONNECT sgit.ai:443 HTTP/1.1
< HTTP/1.1 403 Forbidden
* CONNECT tunnel failed, response 403
```

The proxy's status endpoint records it as a `connect_rejected` relay failure for that host. DNS still resolves, which is part of why it is easy to mistake for an outage.

| Symptom | Cause | Fix |
|---|---|---|
| `CONNECT tunnel failed, response 403` | The host is not on the organisation's allowlist | An Owner adds it, apex included |
| `www.sgit.ai` works, `sgit.ai` fails | Only the wildcard is listed (observed) | Add `sgit.ai` explicitly |
| The agent's web fetch reads sgit.ai, `curl` and `sgit` cannot | Web fetch, web search and MCP connectors are not subject to the sandbox's egress settings (Anthropic) | Fix the allowlist: the shell needs it |
| `pip install sgit-ai` fails | Network access is Disabled | An Owner enables at least Package managers only |
| `push`: `no access token configured` | Not the network | Pass `--token`, or run `sgit auth` |
| `sgit doctor` says `no remote configured` in a vault that works | A known false negative ([CLI issue #2](https://github.com/SGit-AI/SGit-AI__CLI/issues/2)) | Use the `curl` check above instead |

## Credential hygiene for agents

- Never paste a vault key, a read key labelled `sgit_private_read_`, or a token into a prompt that is logged or a file that is tracked. See [credentials](/docs/credentials.html) for what each prefix means.
- `sgit vault info` prints the passphrase, and its web URL carries the whole vault key. Treat its output as a secret.
- Use placeholders in examples: `sgit_public_read_<hex>:<vault_id>`, never a real key.

## See also

- [Working with AI agents: network requirements](/docs/agents.html#network)
- [Installation](/docs/installation.html)
- [Limitations](/docs/limitations.html)
