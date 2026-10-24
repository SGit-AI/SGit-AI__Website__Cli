# Sealed vault keys for sgit: a design pack, cli.sgit.ai

> A design pack for the agents and engineers who will build sealed vault keys into sgit. A vault key arrives sealed (pki.sgit.ai's QR handover), stays sealed on disk and is opened only inside a small KMS. sgit is split into four components (cli, fs, net, kms), each under a Process Behaviour Policy enforced by the kernel and by mutual TLS. Everything is opt-in: with nothing switched on, sgit runs exactly as 0.24.0 does, one process with vault keys on disk, and sealed and plain clones of the same vault work side by side. Six documents: the problem and decisions, the architecture, the key flow and KMS protocol, the policies, the measured evidence, and compatibility and rollout.

*Source: <https://cli.sgit.ai/dev/sealed-vault-keys/index.html> · generated from the same content as the page, so the two cannot drift.*

---
# Sealed vault keys for sgit: a design pack

**Status:** design, 24 October 2026. Nothing here is built. **Compatibility is a requirement, not a phase:** with nothing switched on, sgit behaves exactly as 0.24.0 does, and every vault and agent keeps working unchanged ([05](../../dev/sealed-vault-keys/05-compatibility-and-rollout.md)). Every number marked *measured* was measured on 24 October 2026 in a Claude agent workspace (details in [04-environment-evidence.md](../../dev/sealed-vault-keys/04-environment-evidence.md)). Everything else is a proposal.

**Audience:** the agents and engineers who will build this. Read in order.

| # | Document | What it settles |
|---|---|---|
| 00 | this file | problem, goals, threat model, glossary, decisions |
| 01 | [01-architecture.md](../../dev/sealed-vault-keys/01-architecture.md) | the four components, who may talk to whom, mutual TLS with a session CA, deployment topologies, the refactor path in sgit |
| 02 | [02-sealed-key-flow-and-kms.md](../../dev/sealed-vault-keys/02-sealed-key-flow-and-kms.md) | the handover flow, the KMS protocol, sealing, what lives on disk, how long a key lives and where |
| 03 | [03-process-behaviour-policy.md](../../dev/sealed-vault-keys/03-process-behaviour-policy.md) | Process Behaviour Policies: schema, layering, hashing and signing, how each line is enforced, learning a policy from traces |
| 04 | [04-environment-evidence.md](../../dev/sealed-vault-keys/04-environment-evidence.md) | every probe and measurement, with method and caveats |
| 05 | [05-compatibility-and-rollout.md](../../dev/sealed-vault-keys/05-compatibility-and-rollout.md) | the default stays today's sgit; how the new path is switched on per clone, tested in production beside the old one, and rolled back |

---

## 1. The problem

The pki.sgit.ai handover protects a vault key **while it travels**: the sending agent seals it to the receiving agent's public key, and a person carries a QR image they cannot read. It stops protecting it **the moment it arrives**:

```
   travel                          arrival (sgit 0.24.0 today)
 ┌────────────────────┐   ┌──────────────────────────────────────────────────────┐
 │ QR: sealed to the  │──►│ pki-agent open --save  → vault-key-<id>.txt   CLEAR │
 │ receiving agent    │   │ sgit clone <vault key> → argv, shell history, CLEAR │
 │ (person can't read)│   │                          the agent's transcript     │
 └────────────────────┘   │ .sg_vault/local/vault_key            (0600)  CLEAR │
                          │ .sg_vault/local/key-rnd-imm-*.pem    (PKCS#8) CLEAR │
                          │ .sg_vault/local/token                         CLEAR │
                          └──────────────────────────────────────────────────────┘
```

For an AI agent the worst leak is not the disk. It is the **transcript**: every command line the agent writes and everything a command prints lands in the model's context and in conversation logs.

## 2. Goals

0. **Nothing changes unless it is asked for.** The default is today's sgit: one process, the vault key in `.sg_vault/local/vault_key`, every command, flag, output and workflow as in 0.24.0. The sealed path is switched on per clone, and sealed and plain clones of the same vault work side by side ([05](../../dev/sealed-vault-keys/05-compatibility-and-rollout.md)).
1. **On a sealed clone, the clear vault key is never written to disk, never on a command line, never printed.** It never enters the transcript.
2. **One place holds the private key.** A small KMS process (local, frozen between calls) or a remote one (serverless, Kubernetes, HSM-backed, or provided by the agent platform itself). Same protocol for all of them.
3. **Each component does one job and can do nothing else.** Four components (CLI, fs, net, kms), each under its own Process Behaviour Policy, enforced by the kernel and by mutual TLS.
4. **Ephemeral.** Nothing exists before the session starts or after it ends: identities, certificates, users and policies are all made for the session and die with it.
5. **Policies come from outside the agent.** The person supplies (or signs) the hash of the policy; the agent cannot widen it.
6. **No server changes.** What goes to the vault server is exactly what goes today.

## 3. Threat model

**Trusted:** the kernel, the hardware, the platform that runs the VM. Root and kernel compromise are **out of scope**: anything with root on the machine can read any process's memory, or make the process read it for them. The design shrinks where a key lives; it does not hide it from root.

**Who is root matters.** In the measured environment the agent itself is root. Every defence in the table that is enforced locally (the launcher, the policies, the KMS's binding) is therefore a *Boundary* against a prompt-injected **sgit** process but only a *Setting* against a prompt-injected **agent**, which could undo it. Those rows bind the agent only when the launcher and the KMS run outside it: a remote KMS (01 §5 D) or the platform (01 §5 E).

**In scope:**

| Threat | Example | Primary defence |
|---|---|---|
| Transcript leakage | the key printed by `show-key`, or passed as `sgit clone <key>` | the key never reaches stdout or argv; only sealed forms (`m1`) and public keys appear |
| At-rest leakage | a backup, a workspace zip, a container image with the folder in it | only sealed files on disk; clear keys live in one process's memory |
| Prompt injection driving the **agent** | a web page or vault file tells the agent to run `show-key` or push to another vault | policy hash fixed by the person; sgit-net refuses vault ids and hosts not in policy; `show-key` refused on sealed clones. **Binding on the agent only when the launcher and KMS are outside it** (see above); locally against a root agent, a Setting |
| Prompt injection driving **sgit** (confused deputy) | crafted QR JSON or vault content exploits sgit's parsing | strict input schemas; the exploited process holds no key, has no network, cannot start processes, cannot write outside its folder |
| A buggy or compromised component exceeding its job | sgit-fs tries to reach the KMS | per-component uid, Landlock, seccomp, firewall, mTLS edge rules |
| A sealed key stolen from the transcript and replayed | the `m1` code copied out of a log | the KMS answers only its bound caller (session auth key); nonces are single use; responses are sealed to one-time keys. Against another session or machine, a Boundary; against root in the same session, which can act as the bound caller, a Setting |

**Not claimed:** Python cannot guarantee erasure of secrets (scrubbing `bytes` in place works in CPython, measured, but relies on its internals); expiry on a sealed key is policy enforced by the KMS, not cryptography; a session identity dies with its session, so a restarted session needs a new handover (by design).

## 4. Glossary

| Term | Meaning |
|---|---|
| **vault key** | the secret that opens an sgit vault; read key, write key, vault id and file ids are derived from it (PBKDF2, 600,000 iterations, ~108 ms) |
| **derived keys** | read key and write key. Almost all of sgit runs on these, not on the vault key |
| **k1 / `pki.sgit.ai/qr/key/v1`** | a public key bundle as a QR / JSON |
| **m1 / `pki.sgit.ai/qr/sealed/v1`** | a sealed message: RSA-OAEP 4096 wraps an AES-256-GCM key; the sender signs with ECDSA P-256 over recipient, time, expiry |
| **session identity** | the key pair (RSA-4096 encryption + ECDSA P-256 signing) the KMS makes for this session; its public half is what the person carries to the sender |
| **record fingerprint** | the signing key's fingerprint; what `--to` names (per the 24 Oct requirements update) |
| **E** | a one-time key pair made by the caller for a single KMS request; the response is sealed to E.pub |
| **session CA** | a throwaway certificate authority that issues one TLS certificate per component, then has its private key destroyed |
| **edge** | an allowed caller→callee connection between components |
| **PBP** | Process Behaviour Policy: the ABP model (grant, mandate, delta, barrier) applied to a process |
| **launcher / runtime** | whatever creates the users, CA, certificates and policies and starts the components. Ideally the agent platform, not the agent |

## 5. Decisions

| Decided | Why |
|---|---|
| **Opt-in, per clone; the default is 0.24.0's behaviour** | a fleet of vaults and agents must keep working through every step; sealing touches only `.sg_vault/local/`, which is never pushed, so the server and other clones see no difference (05) |
| Four components: **cli, fs, net, kms** | each has exactly one job; the edges between them are the security model |
| Edges: cli→fs, cli→net, net→kms. Nothing else | fs never sees keys; cli never sees keys or the network; kms never sees the network or disk |
| **mutual TLS 1.3 everywhere**, roles in certificate URI SANs, issued by a session CA whose key is destroyed after issuing | same code local, Docker, Kubernetes, remote; ~3.2 ms per handshake, measured |
| The KMS **never returns a clear key**; it returns derived keys sealed to the caller's one-time key E | nothing between the KMS and the consumer sees plaintext, including the agent |
| The KMS makes its own private key; it never leaves | one sealed place |
| Default key holding (once a KMS process exists): **frozen process + `memfd_secret`** | 0.28 ms freeze / 0.13 ms thaw, measured; secret pages unreadable even via `/proc/pid/mem`. Not proof against root, which can attach to the process and make it read its own pages |
| Policies are hashed (canonical JSON, SHA-256) and the hash comes from the person or is signed by the root key `sha256:db7f79fdd87e030a` | otherwise a prompt-injected agent could widen them |
| A handover's expiry is checked when it is taken in; what is kept at rest is **re-sealed** to the identity and a recovery recipient, without the handover's one-week expiry | storing the received `m1` as it is would stop the clone opening after seven days (02 §2) |
| The KMS judges a sender against **fingerprints pinned in the session policy** first; the register's chain rules come later | the KMS has no network, so register data reaches it only through sgit-net, which could withhold a revocation; a pin from the person is also the requirements' "vouched by the operator" mode, without a flag (02 §3.3) |
| Host allowlisting is done by **sgit-net as the TLS client**, not by the kernel | the kernel only sees the platform proxy's port; sgit-net sees and verifies the name |

| Open | Notes |
|---|---|
| Full split (sgit-net holds derived keys and does all vault crypto) vs. step 1 (sgit-net filters; cli receives derived keys sealed to its own E) | step 1 works with sgit 0.24 internals; full split is the target |
| Remote KMS backend | AWS KMS asymmetric RSA-4096 with OAEP-SHA-256 should match sgit's envelope: **verify** before relying on it. A cloud KMS key is a lasting identity, not a session one: it cannot be made inside the session and die with it |
| `rekey`, `move`, `show-key --reveal` | these need the vault key itself; the KMS needs an operation that performs them inside it, or they stay plain-mode commands for now |
| sgit-fs as a process that owns the folder vs. a FUSE mount | FUSE is available in the measured environment; start with the owning process |
| Who runs the launcher | the agent today (so locks are "Settings" against the agent); the platform in the end state |

## 6. End state: the platform provides it

The local `sgit-kms` user and a Lambda are stand-ins. The right owner of the KMS and of policy enforcement is the **agent execution environment** (Claude, ChatGPT, etc.):

- it already knows which session is calling, which solves caller authentication for an ephemeral container;
- it already sits outside the container (this environment's egress proxy is the precedent);
- it can bind key lifetime to session lifetime and keep decrypted results out of transcripts and logs.

The protocol in this pack is designed so that sgit doesn't change when the KMS moves from a local uid to a Lambda to a platform service. This is a proposal for what platforms should offer; no such service is known to exist today.

## 7. Sources

- [A vault key that never lands](../../articles/a-vault-key-that-never-lands.md): the original analysis (sgit 0.24.0 at `182cfc1`), including its 24 Oct update: plain keys refused on all 14 commands that take one; `--to` is the record fingerprint; seal to a lasting recovery recipient too; trust an explicit fingerprint first.
- [pki.sgit.ai handover](https://pki.sgit.ai/handover.md): QR formats, refusal rules, root fingerprint.
- [Agent Behaviour Policy](https://riskmandate.ai/abp.html): grant, mandate, delta, barrier.
- [Sealed vault keys in sgit: requirements](../../research/sealed-vault-keys-requirements.md) and [the side-by-side review](../../research/sealed-vault-keys-side-by-side.md), 24 October 2026.
- This design session, 24 Oct 2026 (Dinis Cruz with Claude).

## 8. Review before publishing

The pack was written in a design session of Dinis Cruz's with a Claude agent on 24 October 2026, and reviewed the same day by cli.sgit.ai's build agent before it was published here. The review changed:

1. **Compatibility made a requirement.** At Dinis's instruction: the default is 0.24.0's behaviour, the new path is opt-in per clone, and the rollout is staged in production. New: goal 0, the first decision, and [05](../../dev/sealed-vault-keys/05-compatibility-and-rollout.md). The refactor path (01 §7) and the refusals (01 §2.1, 03 §8) now say which behaviour is the default.
2. **The handover's expiry.** A received `m1` expires in a week (handover.md). Kept at rest as it is, a clone would stop opening after seven days. The KMS now checks expiry at intake and keeps a re-sealed copy (02 §1.2, §2, §3.3).
3. **Trust without a network.** The KMS has no network, yet it was asked to check the sender's chain to the root. It now checks against fingerprints pinned in the session policy first (02 §3.3).
4. **The threat model says who is root.** Local defences are Boundaries against sgit and Settings against a root agent. `memfd_secret` stops `/proc/<pid>/mem` and the kernel's direct map, not root acting through the process (§3, 02 §8).
5. **Smaller points.**
   - `rekey`, `move` and `show-key --reveal` need the vault key, and have no KMS operation yet (§5).
   - sgit-fs's clear-key detection is best-effort, because a vault key's passphrase can be chosen by its owner (01 §2.2).
   - Scrubbing `bytes` relies on CPython internals (§3).
6. **Publishing.**
   - The platform's egress proxy port is generalised, and 04 says that root inside the microVM is the platform's design.
   - Em dashes are replaced, house style.
   - Links point at this site.
   - Nothing else in the text was changed.

---

*[Site index for agents](../../llms.txt) · [HTML version](https://cli.sgit.ai/dev/sealed-vault-keys/index.html)*
