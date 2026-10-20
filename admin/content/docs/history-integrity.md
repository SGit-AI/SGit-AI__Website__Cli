---
title: History integrity: the format gate, verifying signatures, and rewinds
summary: sgit vault format (format 2, 128-bit ids, --min-client), who can open a raised vault and what old clients say, the shared branch index, rewind detection and --accept-rewind, sgit check verify, signatures-required and what a signature proves, and a checklist for raising a vault. For sgit-ai 0.21.0.
section: guides
order: 2
moved_from: https://sgit.ai/docs/history-integrity.html
moved_version: v0.7.87
moved_on: 2026-10-20
---

# History integrity: the format gate, verifying signatures, and rewinds

For sgit-ai 0.21.0: `sgit version` to check, `sgit update` to upgrade ([what changed](/docs/update-to-0-21-0.html)). The gate and rewind detection arrived in 0.19.0; 0.21.0 is the first release where all of it is safe for a team of writers. **Nothing changes for an existing vault until its owner raises it** with `sgit vault format`; until then every client, old or new, behaves as it did in 0.18.0.

**The 0.20.0 known issues are fixed in 0.21.0.** `signatures-required` no longer locks out a clone made before a teammate joined, and switching it off sticks; accepting a rewind moves the clone to the new head and re-applies your own unpushed work; `history reset` and `history show` take the short ids `history log` prints. Checked on the live dev API on 10 and 11 October 2026.

A vault is a Merkle tree of encrypted objects: every file, folder and commit is stored under the hash of its ciphertext, every commit names its parents and its root folder by those hashes, and every object and ref is AES-256-GCM encrypted under a key the server never holds. So the server cannot alter a byte of history without it failing to decrypt, and `sgit check fsck` finds anything missing or corrupt. These releases add what that model did not give you: who may open a vault, 128-bit addresses, a branch pointer that only moves forward, and signatures you can check and require. All of it is per vault and off by default.

## The format gate: `sgit vault format`

Every vault has a gate in its branch index. A vault that has never been touched by this command reads as format 1 with no minimum client, which is exactly the 0.18.0 behaviour.

```
$ sgit vault format
  Format:      1  (new objects get 12-hex ids)
  Min client:  none   (this client: v0.21.0)
  Features:    none

Raise it with: sgit vault format --set 2 --min-client <X.Y.Z> [--feature signatures-required]
  Clients older than --min-client refuse the vault by name (sgit update); existing objects are untouched.
```

The owner raises it, from any clone with the vault key:

```
$ sgit vault format --set 2 --min-client 0.21.0
Vault format updated and written to the server.

  Note: once a new object is written here, sgit-ai older than 0.19.0 cannot read this vault.
        Those clients do not know this gate exists, so they will NOT say "update": a fresh clone
        reports "integrity check refused vault data" and a pull reports "missing file … run
        sgit check fsck". The fix for them is `sgit update`, never `vault move` or `fsck --repair`.
        Raise a vault only once every agent that writes to it is on 0.19.0 or newer.
  Format:      2  (new objects get 32-hex ids)
  Min client:  0.21.0   (this client: v0.21.0)
  Features:    ids-128
```

- **`--set 2`**: from now on, every new object this vault stores gets a 128-bit content address (`obj-cas-imm-` plus 32 hex characters) instead of 48 bits. Existing objects keep their ids and still verify; a clone holds both. Nothing is re-encrypted and no `vault move` is needed. A format cannot go back down: `error: … format cannot go down (vault is at 2); objects already written at the wider id would be unreadable`.
- **`--min-client X.Y.Z`**: a client from 0.19.0 on that is older than this refuses the vault by name: `error: this vault needs sgit-ai >= 0.21.0 and this is 0.20.0: run `sgit update`, then try again` (checked with 0.20.0 on 11 October 2026). You cannot set a minimum you do not meet yourself (`… you would lock yourself out`). Compared on the three numbers; a dev build is never refused.
- **`--feature NAME` / `--remove-feature NAME`**: policies. `signatures-required` is the one that exists today, [below](#signatures).

**Why 128 bits.** A 48-bit address is plenty against the server, which cannot produce decryptable bytes at all. It is not plenty against someone who holds the vault key and wants to swap an object for another with the same address: that is 248 hashes, hours on a GPU. On a raised vault it is 2128. Cost on the shared CRM vault used as the example in these pages (674 commits, 19,780 objects): 1.5 % more bytes, no visible change in time.

## Who can open a raised vault

| Client | Un-raised vault (format 1) | Raised vault (format 2) |
|---|---|---|
| sgit-ai 0.21.0 | works, unchanged | works |
| sgit-ai 0.20.0, 0.19.0 | works; a 0.20.0 push drops the vault's tags until a 0.21.0 pull restores them | works; refuses by name if below the vault's `--min-client`. Set `--min-client 0.21.0`: earlier clients lack the 0.21.0 fixes |
| sgit-ai 0.18.x and older | works, unchanged | **fails, and blames the data.** A fresh clone says `integrity check refused vault data`; a pull says `missing file … sgit check fsck`. The fix is `sgit update` |
| The web UI | works | reads it; its pushes still write 48-bit ids and drop the index gate until its update ships, and the next CLI pull repairs the index |

**The one thing to plan.** A client older than 0.19.0 does not know the gate exists, so it cannot tell you to update. Raising the vault does nothing to it by itself; the first object written at a 32-hex id after the raise is what stops it, and it stops with one of these, both of which read like damage:

```
error: integrity check refused vault data — clone needs object obj-cas-imm-…, which was
refused by the content-address check … the host served corrupt or substituted content:
do not trust this source.

error: missing file — object obj-cas-imm-… is not in the local store
  hint: try "sgit check fsck ." to check and repair
```

**Neither hint applies.** Nothing is corrupt and nothing was lost: an old client cannot parse a 32-hex id. Do not run `sgit vault move` or `fsck --repair`. Run `sgit update` and retry. Checked on this site on 8 October 2026 with real 0.17.0 and 0.18.0 installs against a throwaway vault on the live dev API: those are the messages, word for word.

**The rule for vault owners:** raise a vault only once every agent that writes to it is on 0.21.0, and pass `--min-client 0.21.0` so that clients from 0.19.0 on refuse by name rather than by symptom.

## The branch index is shared, and now repaired

The branch index lists every clone branch, maps each to its signing key, carries the gate, and (from 0.21.0) holds the vault's tag names. The web UI currently overwrites it with a single entry on every push, which used to lose the other entries for good. From 0.19.0 the CLI treats the index as a shared document: `pull` reads the remote copy, merges it with the local one and writes the merge back with compare-and-swap; `push` registers a clone branch the same way. In 0.21.0 the server's copy of the gate is authoritative, so a policy the owner removes stays removed; pull fetches the signing keys of teammates who joined after this clone was made; and an index entry a client cannot read is kept, untouched, for the clients that can.

```
$ sgit pull
  ▸ Branch index: restored 2 entr(y/ies) the remote copy had lost
```

You do not have to do anything; it is the reason a raised gate survives a web push. If the merged index cannot be written back (a teammate kept winning the race), 0.21.0 fails the push and says so, rather than overwriting it.

## Rewinds: the named branch only moves forward

The named branch is a pointer. The server, or anyone with the key running `sgit push --force`, can point it at an older or unrelated commit. Each clone remembers the last remote head it accepted, one per named branch (in 0.21.0, in `.sg_vault/local/remote_heads.json`), and a new head that does not descend from it is a **rewind**. Only a verified pull, merge or push moves that record; `status` and switching branches never do, and a record that is missing or unreadable refuses the pull rather than accepting whatever the server says.

```
$ sgit status
  Remote: the named branch was REWOUND or rewritten on the server (it no longer descends from obj-cas-imm-…)
          if that was a deliberate `sgit push --force`, run: sgit pull --accept-rewind
          otherwise treat it as tampering and check with the vault owner

$ sgit pull
error: the remote named branch was rewound or rewritten: it pointed at obj-cas-imm-… the last
time this clone saw it and now points at obj-cas-imm-…, which does not descend from it. If this
was a deliberate `sgit push --force`, run `sgit pull --accept-rewind`; otherwise treat it as
tampering and check with the vault owner. Nothing was changed.
```

- **You, or a teammate, force-pushed on purpose** (after `sgit history reset`, say): every other clone runs `sgit pull --accept-rewind` once. The clone that pushed needs nothing. Accepting moves the clone to the new head and drops the removed commits; your own unpushed commits are re-applied on top as one new commit, and if they conflict with the rewind the pull refuses and changes nothing:

```
  ⚠ Accepting a rewound named branch: obj-cas-imm-6bc773765219 -> obj-cas-imm-0d84e4f7f80d
Rewind accepted: 0 added, 1 modified, 0 deleted.
  dc57de5e6520 (HEAD)  Re-apply local work on top of the rewound current
```

 To force-push yourself without clobbering a teammate, use `sgit push --force-with-lease`: it forces only if the remote is still where this clone last accepted it.
- **Nobody did**: do not accept it. Your clone still holds the newer history; in 0.21.0 `sgit push` refuses (exit 1) rather than putting it back silently. Tell the vault owner.
- **The web UI pushed**: today the web UI's push does not compare before writing, so two people saving at the same moment can drop one person's commits. The CLI reports that as a rewind, and it is right to. The web UI team is moving to compare-and-swap.

Normal forward moves, a clone's first pull, and a fresh `sgit init` over an existing vault id are never rewinds.

## Signatures: `sgit check verify`

Every CLI commit is signed with the clone branch's ECDSA P-256 key. 0.19.0 is the first release that checks them.

```
$ sgit check verify
Checked 674 commit(s): 247 verified, 0 bad, 112 unsigned, 315 without a known key, 0 missing
```

| Status | Meaning |
|---|---|
| verified | the signature checks under the key the commit names, or the key the branch index maps its branch to |
| bad | the signature does not check: the commit was altered after signing. `fsck` fails on this |
| unsigned | written without a key: the web UI, or a clone with no local signing key |
| without a known key | signed, but neither the commit nor the index says by which key: commits from before 0.19.0 whose branch has left the index |

New commits carry their key id and sign canonical bytes (RFC 8785 over the stored commit JSON, minus the signature), so from 0.19.0 on "without a known key" stops growing; older signatures still verify. `sgit check fsck` prints the same summary, and on the example vault now takes 12 s instead of 270 s. `check verify` works on a [partial clone](/docs/partial-clones.html) too: a scoped clone checks the commits it holds, a shallow one stops at its boundary.

**Requiring signatures.** `sgit vault format --feature signatures-required` makes every `pull`, and in 0.21.0 every `clone`, refuse the first incoming commit that is not *verified*, by name, before writing anything; a `push` of an unsigned commit is refused before it is sent. The policy covers commits made after it was switched on: the gate records where it starts (`signed-since-<commit>` in `Features`), so older unsigned history does not block anyone:

```
error: this vault requires signed commits and incoming commit obj-cas-imm-… is unsigned; the
pull was refused before anything was merged. Ask the vault owner, or relax the policy with
`sgit vault format --remove-feature signatures-required`.
```

Turn it on only for vaults whose writers all use the 0.21.0 CLI with their keys: today's web UI does not sign. Update every clone before switching a policy off; a 0.19.0 or 0.20.0 clone that saw the policy writes it back. A vault that switched the policy on before 0.21.0 has no recorded start, so a fresh clone checks its head only; switch the policy off and on once with 0.21.0 to record one. `sgit migrate apply` refuses on a vault with signed commits (a migration rewrites history) unless `--force`.

**What a signature proves, and what it does not.** A signing key is trusted because its key file decrypts under the vault's read key. So anyone who holds the read key and can write to the store can make a commit that verifies; today, the server's write-key check is what stands in the way. Signatures tell you which clone wrote a commit and that nothing changed since; they are not yet a list of who is allowed to write. Owner-signed membership is the CLI team's next design item (TM-R01 in their threat model).

## A checklist for raising a vault

1. Every agent that writes to it is on 0.21.0 (`sgit version`). Point them at [Update sgit-ai to 0.21.0](/docs/update-to-0-21-0.html).
2. `sgit check fsck` is clean and `sgit check verify` shows no *bad* commits.
3. `sgit vault format --set 2 --min-client 0.21.0`.
4. Each agent's next `sgit pull` picks the gate up; nothing else to do.
5. `--feature signatures-required` once no web-UI writes are expected on the vault.

From the sgit-ai team's 0.19.0, 0.20.0 and 0.21.0 notes. The old-client messages were found by this site's own check of the 0.19.0 draft, which had said "a validation error"; the CLI team confirmed them and added the warning a raise now prints. The 0.20.0 issues fixed in 0.21.0 were found by this site testing 0.20.0 on the live API. Release notes: [sgit-ai 0.21.0 (includes 0.19.0 and 0.20.0)](https://sgit.ai/updates/index.html#sgit-ai-0-21-0).
