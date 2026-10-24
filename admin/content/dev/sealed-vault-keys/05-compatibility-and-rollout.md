---
title: Sealed vault keys, 05: compatibility and rollout
summary: The rule that governs the whole pack: with nothing switched on, sgit behaves exactly as 0.24.0 does, one process with the vault key on disk, and every vault and agent keeps working unchanged. What must not change, how the sealed path is switched on per clone and never globally, why sealed and plain clones of one vault work side by side, what an older sgit sees, five rollout stages that test the new path in production beside the old one, rollback at every stage, and the tests that prove nothing broke.
section: devpacks
order: 6
---

# 05. Compatibility and rollout

**The rule.** With nothing switched on, sgit behaves exactly as 0.24.0 does:
- one process;
- the vault key in `.sg_vault/local/vault_key`;
- every command, flag, output and exit code as today.

The pack can be deployed to every machine, and every vault and agent keeps working with no change. The sealed path is introduced alongside, switched on clone by clone, tested in production next to the old one, and rolled back without loss at every stage. The default may change one day, in a major version and for new clones only. Plain clones keep working for as long as anyone uses them.

Added on 24 October 2026 at Dinis Cruz's instruction, after the review of 00 to 04.

## 1. What must not change

| Area | Invariant |
|---|---|
| Commands | Every existing command, flag, output and exit code. New behaviour comes through new flags (`clone --sealed`) and new commands (`vault seal-local`), never through a changed default. |
| Keys on argv | The 14 commands that take a vault key keep taking it. Refusing it is a line in a session policy (03), not a default. A warning is printed only in a sealed session. |
| Clone layout | An unsealed clone's `.sg_vault/` is byte for byte what 0.24.0 writes. |
| The vault and the server | Nothing under `bare/` changes, and no request changes. Sealing lives only in `.sg_vault/local/`, which is never pushed. |
| Key derivation | The same PBKDF2 and the same derived keys. A sealed clone and a plain clone of one vault derive identical keys. |
| The pki key store | `~/.sg-send/keys/` in today's format. Keys made before still open. New keys get Argon2id only when they are made. |
| The handover | `pki-agent open --save` and `seal --from-vault` keep working, and handover.md stays valid. |
| Process model | One process. The KMS, the components and the launcher are deployments of the same interface, never required. |
| Dependencies | The base install adds nothing beyond `cryptography`. QR images, FIDO2 and the component launcher are optional extras. |
| Speed | An unsealed clone pays nothing: the default key source is a function call over the same file. |

## 2. How the sealed path is switched on

**Per clone, by what is on disk.** `Key_Source` (01 §7 step 1) looks in `.sg_vault/local/`:

| Present | Mode | Behaviour |
|---|---|---|
| `vault_key` | plain | today's sgit, unchanged |
| `vault_key.sealed` | sealed | opened through the sealed backend: in-process first, a KMS later |
| both | shadow (stage 2) | uses the plain key; derives the keys both ways and reports any mismatch |
| neither | n/a | today's error, plus one line saying what a sealed clone needs, when sgit knows sealing |

There is no global switch and no environment variable that changes the default. A clone becomes sealed only through an explicit command:
- `sgit clone --sealed <m1|qr|file|->` for a new clone;
- `sgit vault seal-local` for an existing one.

A session policy (03) can also **require** sealed clones, for the agents being trialled.

## 3. Mixed fleets work by construction

- **One vault, sealed and plain clones at once.** The server sees identical requests from both, and other clones cannot tell. A sealed agent and a plain agent push and pull the same vault.
- **One agent, sealed and plain clones at once.** Each clone carries its own mode. Nothing is shared between clones except the pki key store, which plain clones never read.
- **No vault-level gate.** Unlike pack mode, which needed `min_client` because it changed what is on the host, sealing changes nothing any other client reads, so it needs no gate.

## 4. What an older sgit sees

| Situation | Behaviour | Mitigation |
|---|---|---|
| sgit 0.24.0 or older on a **plain** clone made by a newer sgit | works: the layout is unchanged | none needed |
| sgit 0.24.0 or older on a **sealed** clone | fails: no `vault_key` | `sgit vault unseal-local` with the newer sgit first (§6), or a fresh plain clone. Sealing is a per-clone choice that is easy to undo, not a format migration |
| A newer sgit on a sealed file whose format version it does not know | refuses by name | the sealed files carry a format version from the first release |

## 5. Rollout, in production, stage by stage

Each stage ships only when the previous one has run in production without a regression. Each stage is reversible on its own.

| Stage | What ships | Who uses it | How it is proved |
|---|---|---|---|
| **0. Dormant** | `Key_Source` with only the plain backend (01 §7 step 1), and the compatible step-0 fixes (Argon2id and per-user salts for **new** keys and stores only) | everyone, invisibly | The existing test suite, unchanged, plus the golden run in §7. No user-visible change. |
| **1. Shadow** | `vault seal-local --shadow`: writes `vault_key.sealed` and keeps `vault_key`. Every command uses the plain key, opens the sealed one too, compares the derived keys, and logs any mismatch (never a key). | one or two trial agents, on real vaults | Mismatch count at zero over real use; the sealed path proved in production at no risk |
| **2. Sealed, one process** | `clone --sealed`, `vault seal-local` without `--shadow`, `vault unseal-local`. The sealed file is opened in-process with the local pki key, with the passphrase as `sgit pki` gets it today. | trial agents, opted in per clone | §7's tests; rollback by `unseal-local` |
| **3. Sealed, with a KMS process** | The KMS protocol (02) behind the same `Key_Source`: a local frozen process first. | agents on platforms that allow a long-running process | The same tests, plus the KMS's own (02 §3.3) |
| **4. Components and policies** | The launcher, sgit-fs, sgit-net, policies (01, 03), per deployment topology | where the platform supports it; the end state is a platform-provided launcher and KMS | Policy footprints from traces (03 §7), in audit mode before enforce mode |

**The default** stays plain through all five stages. A change of default is a separate decision, for a major version, for new clones only, and only after stage 2 has run in production long enough to trust.

## 6. Rollback at every stage

- **Stage 0:** nothing to roll back; the plain backend is today's code behind one interface.
- **Stage 1:** delete `vault_key.sealed`; the clone is plain again.
- **Stage 2 and later:** `sgit vault unseal-local` opens the sealed key and writes `vault_key` back, with a warning that names what it does. Or make a fresh plain clone with the key from wherever it is kept. The vault itself is never affected, because nothing under `bare/` ever changed.
- **A downgrade of sgit** needs `unseal-local` first on any sealed clone (§4).

## 7. The tests that prove nothing broke

1. **The existing suite, unchanged,** at every stage: 4,540 tests at the 0.24.0 release.
2. **A golden run.** A scripted session against a counted in-memory host: `init`, `commit`, `push`, `clone`, `pull`, `status`, `history log`, `vault show-key`. Run with 0.24.0 and with the new build on a plain clone. Outputs, exit codes, the files in `.sg_vault/` and the requests to the host must be identical.
3. **Mixed fleet.** A sealed clone and a plain clone of one vault push and pull each other's commits, and the host sees byte-identical requests from both.
4. **Shadow agreement.** For every vault in a test fleet, the sealed and plain paths derive identical keys.
5. **Round trip.** `seal-local` then `unseal-local` restores a `vault_key` identical to the original, and the clone works with 0.24.0 again.
6. **Handover compatibility.** A key handed over by today's `pki-agent seal --from-vault` opens with `clone --sealed`. A clone made the old way (`open --save`, then `clone <key>`) still works.
7. **No new cost on plain clones.** The time of a plain-clone command stays within noise of 0.24.0.
8. **Feature detection.** `sgit help all --format json` lists `--sealed` only in builds that support it, so handover.md and the agent tool can choose the new path or the old one per agent.

## 8. For the agents and documents already in use

- **handover.md** gains a branch, "if your sgit lists `--sealed`", and keeps the old path for every agent that does not.
- **The agent playbook for pack mode,** the release notes and every guide stay correct, because none of them changes for a plain clone.
- **The requirements' list** (R1 to R10) maps onto stages 2 and 3, with **R2**, refusing keys on argv, as a policy line rather than a default.
