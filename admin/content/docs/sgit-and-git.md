---
title: sgit and Git: what only sgit does, what both do, and where Git is ahead
summary: The row-by-row comparison, checked against sgit-ai 0.26.0 and the dev builds after it. Twelve things Git has no equivalent for, each with the command and Git's nearest answer: a host that reads nothing, read keys that work from any static host, custody without access, writes without reads, one folder by byte ranges from plain storage, indexes the writer ships encrypted and signed, policy the vault carries, rewinds refused by name, a secret guard, key rotation, a computable cache, files sealed to a person. Fifteen things both have, with what differs. Where Git is ahead: line-level merge and partial commits shipped in the dev builds of 28 October; the rest of the CLI team's Git-parity roadmap is designed, with sizes in days. GitHub's features move to a future server. And the six things zero knowledge rules out, each with its substitute.
section: start
order: 0
---

# sgit and Git

**sgit is not a copy of Git with encryption on top.** It has Git's verbs, so a Git user is at home in an hour. But the host reads nothing, and that makes possible a set of things Git cannot do at all. This page is the map, row by row, checked against sgit-ai 0.26.0:
- what only sgit does;
- what both do, and how they differ;
- where Git is ahead, and how fast the gap is closing;
- what zero knowledge rules out for good.

!shot sg-map.webp | /articles/images/ | sgit and Git, row by row, against sgit-ai 0.26.0 and the dev builds after it. Twelve things only sgit does, from a host that reads nothing to files sealed to a person. Fifteen both do, with sgit's difference. Where Git is ahead: line-level merge and partial commits shipped in the dev builds of 28 October, seven more items designed and sized in days, GitHub's features moved to a future server. And six that zero knowledge rules out for good, each with a client-side substitute. | comparison

**In one paragraph.** Use sgit when the files must stay unreadable to whoever stores them, when readers should need no account, or when many agents work in one large vault, one folder each. Use Git when you need blame, bisect or rebase today, a forge's review and CI, or twenty years of tooling; line-level merges and partial commits arrived in sgit's dev builds on 28 October. Almost everything on Git's side runs on the client in Git too, so sgit can build it. What sgit can never do is anything that needs the host to read your files.

The evidence:
- the sgit CLI team's [claim-by-claim review](/research/sgit-and-git-article-review.html) of the newsroom's article [What sgit does that Git does not](https://newsroom.sgit.ai/articles/what-sgit-does-that-git-does-not.html), against the CLI's source and threat model;
- three behaviours re-run by this site against the PyPI release, [the script](https://github.com/SGit-AI/SGit-AI__Website__Cli/tree/dev/admin/research/sgit-and-git-2026-10-28);
- Git's and GitHub's own documentation.

## 1. What only sgit does {#only-sgit}

"No equivalent" means the mainstream Git toolchain and GitHub. Add-ons such as git-crypt and git-remote-gcrypt cover parts of the first row, with the trade-offs their own READMEs state.

| # | What sgit does | How | Git's nearest answer |
|---|---|---|---|
| 1 | **The host reads nothing.** Contents, file names, commit messages and branch names are encrypted on the client (AES-256-GCM) before they leave it | every command; objects stored under opaque ids | git-crypt encrypts contents only; its README says it "does not encrypt file names, commit messages" or other metadata |
| 2 | **A read key is a capability, not a permission.** It is derived one way from the vault key, so it can never become write access. It reads from any static host, with no account and no server code | [`clone --read-key`](/reference/clone.html), `--transport static`, [`sgit publish`](/reference/publish.html) | read access is a role a server enforces (a collaborator, a deploy key), or the repository is public |
| 3 | **Custody without access.** Copy a published vault you cannot read, keyless, and verify it. A backup service or a second host holds and checks the vault and learns nothing | [`sgit vault mirror`](/reference/vault.html) `[--verify DIR]` | a mirror of a Git repository can read all of it |
| 4 | **Write without read.** An append lane lets a sender put something into a vault and learn nothing, not even whether anyone else writes there: the answer is `{"ok": true}` | the server's [append lanes](/api/append-lanes.html); **no sgit command yet** | no Git or GitHub role can write without reading |
| 5 | **One folder by byte ranges from plain storage.** A scoped clone of a pack vault reads the packs' directories, then only that folder's byte ranges, verifying each object by its hash. On 76,000 files: 2.8 s and 12.5 MB, against 36 s and the whole 88 MB pack | [`clone --path`](/reference/clone.html) on a pack vault (0.26.0) | Git's dumb HTTP takes whole packs; its partial clone needs a smart server that reads the content |
| 6 | **Indexes the writer ships, encrypted and signed.** Each push carries an index pack beside its data pack, so readers plan pulls and clones without walking trees. An index is a plan, never a proof: every object is still verified by its id | automatic on pack vaults (0.26.0); [`pack index build \| verify \| stats`](/reference/pack.html) | Git's commit-graph and pack indexes are built by each reader, as local plaintext caches |
| 7 | **Policy carried by the vault.** The format gate (`min_client`, features) and `signatures-required` live in the encrypted branch index. Every sgit client enforces them before it writes anything | [`sgit vault format`](/reference/vault.html) (0.19.0) | signature checks are each user's local config; a repository cannot require them of whoever clones it |
| 8 | **A rewind is refused by name, on every clone.** A remote head that does not descend from the last one this clone accepted is refused, even though the host took the forced push (it cannot read refs) | `pull` refuses; `pull --accept-rewind` takes it (0.19.0) | the default `+` refspec takes a forced update with one line of output; `receive.denyNonFastForwards` is a server setting |
| 9 | **A secret guard at commit.** A vault key in a zip under any name, a hard link to one of the clone's secrets, and `.env` files are refused | `commit`, `write` | nothing built in; GitHub's push protection runs on a server that reads the content |
| 10 | **Rotate the key that encrypts the history.** Move a vault to a new key, and optionally a new server | [`sgit vault rekey`](/reference/vault.html), `vault move` | a leaked credential is revoked on the server; the content was never encrypted |
| 11 | **A computable cache.** A hot path gets a fixed-cost read at a location only key holders can compute, so an edge function reads it in one request, without walking trees | [`sgit cache add`](/reference/cache.html) | every read walks from a ref |
| 12 | **Seal a file to a person.** Encrypt a file to someone's public key, then commit the sealed file | [`sgit pki encrypt --recipient`](/reference/pki.html) | Git signs commits; it has no "encrypt this to that person" |

Checked by this site against 0.26.0: rows 8 and 9, and `write` in section 2 ([the script and its output](https://github.com/SGit-AI/SGit-AI__Website__Cli/tree/dev/admin/research/sgit-and-git-2026-10-28)). The other rows are from the CLI team's review of the code, and from the release notes of [0.24.0](/docs/update-to-0-24-0.html), [0.25.0](/docs/update-to-0-25-0.html) and [0.26.0](/docs/update-to-0-26-0.html).

## 2. What both have, and what differs {#both}

| Git | sgit | What differs |
|---|---|---|
| packs | pack mode (0.24.0) | sgit's packs are ciphertext on plain object storage; Git's are delta-compressed, sgit's are not |
| kept packs above `fetch.unpackLimit` | `clone --pack-store` (0.26.0) | the same idea; sgit verifies each object on every read |
| partial clone plus sparse-checkout | `clone --path`, `fetch <folder>` to widen, `clone --sparse` (0.18.0) | against ciphertext on S3. A commit outside the scope is refused by name, and two scoped clones in different folders never conflict |
| `clone --no-checkout` | `clone --no-checkout`, then `sgit checkout <paths>` (0.26.0) | the agent loop: `pull --no-checkout`, then `checkout --since-pull` writes only what changed |
| shallow clone, `fetch --unshallow` | `clone --depth N`, `fetch --unshallow` (0.18.0) | combines with `--path` |
| bare clone | `clone --bare`, `clone-headless`, `clone-branch`, `clone-range` | |
| `git commit <paths>`, `add -p` | `sgit commit <paths>`, `commit -p`, `--list-hunks` / `--hunk` (0.26.6); `sgit write <path> --file F [--also P:F …] [--push] [--json]` | `commit <paths>` matches Git's committed trees; hunk ids refuse to pick a different hunk once the file changed; `write` commits files without scanning the working copy. No persistent staging area |
| signed commits and tags | commits signed by each clone's key; verification and `signatures-required` (0.19.0); signed tags (0.21.0) | sgit's check is required by the vault (row 7). A signature proves a key holder, not a person; see [section 5](#qualifiers) |
| `log`, `diff`, `show`, `reflog` | `history log --grep --since --until --author --file --patch --stat --json`, `history diff A..B`, `history show`, `history reflog` | `history log --vault-key` runs with no clone |
| `revert`, `reset`, `commit --amend` | `history revert`, `history reset`, `history undo`, `commit --amend` (0.21.0) | |
| `stash` | `vault stash` | |
| `merge` and conflicts | `branch merge`, `resolve`, `merge-abort` | whole-file `<path>.conflict` by default; line-level with Git's markers with `--merge lines` (0.26.5) |
| `remote` | `remote add / list / set-url` | |
| `fsck` | `check fsck`, `check verify` | checks encrypted objects and their signatures; can repair |
| reading over dumb HTTP | `--transport static` | one file from a normal vault is a ref, a commit, one tree per folder level and the blob, as plain GETs; one batch request for a path declared with `sgit cache add` |

The full Git-to-sgit command table is [sgit for Git users](/docs/sgit-for-git-users.html).

## 3. Where Git is ahead, and how fast the gap is closing {#git-ahead}

Git is a client-side program. Almost all of its lead runs on the client in Git too, on plaintext the client holds, so sgit can build the same things with no new server feature.
- **The plan:** the CLI team's [Git-parity roadmap](/research/git-parity-roadmap.html) (28 October): Git the client is the bar, and every new feature is off by default.
- **The first deliveries** are already on PyPI as [dev builds](/builds/index.html), each reviewed.
- **Sizes** are the roadmap's estimates.

```text
 Git's lead on 27 Oct            on 28 Oct, dev builds 0.26.3 – 0.26.6
 ──────────────────────          ──────────────────────────────────────────────
 line-level merge         ──►    ✓ shipped, opt-in: pull/branch merge --merge lines   0.26.5
 commit some files/hunks  ──►    ✓ shipped: commit <paths>, -p, --list-hunks/--hunk    0.26.6
 commit messages > 740 B  ──►    ✓ shipped: up to 64 KiB with long-messages            0.26.4
 forks deeper than 200    ──►    ✓ fixed: merge base with no cap                        0.26.3
 the rest of priority 1-2 ──►    designed, with acceptance checklists: 7 documents
```

| Git has | sgit, 28 October | Roadmap | Design | Size |
|---|---|---|---|---|
| line-by-line three-way merge | **shipped, opt-in** in [0.26.5](/builds/0-26-5.html): `--merge lines`, `--conflict diff3`; whole-file `.conflict` stays the default | 2.1 | [01](/research/git-parity-design-line-merge.html) | done |
| a staging area, `commit <paths>`, `commit -p` | **shipped** in [0.26.6](/builds/0-26-6.html): `commit <paths>`, `commit -p`, and `--list-hunks` / `--hunk` for agents; no persistent `add` | 2.3 | [03](/research/git-parity-design-partial-commits.html) | done |
| sign with your own key, verify against your allowed signers | each clone signs with its own key; designed: an SSH or GPG key as a second signature, and an allowed-signers file per verifier, as Git does | 2.2 | [02](/research/git-parity-design-signing.html) | 3–4 days |
| `cherry-pick` | designed, on the line merge | 2.8 | [01](/research/git-parity-design-line-merge.html) | 1 day |
| rename detection | none; designed from the plaintext content hash tree entries already carry | 2.4 | [04](/research/git-parity-design-blame-grep.html) | 1–2 days |
| `blame` | none; designed as `history blame`, cheap through the index pack's file → commits member | 2.5 | [04](/research/git-parity-design-blame-grep.html) | 2 days |
| `grep`, `log -S` / `-G` | `history log --grep` over messages; designed: `sgit grep` over content | 2.7 | [04](/research/git-parity-design-blame-grep.html) | 1–2 days |
| `bisect` | none; designed, by generation number | 2.6 | [05](/research/git-parity-design-bisect.html) | 1–2 days |
| hooks | none; designed as local hooks that never sync | 2.9 | [03](/research/git-parity-design-partial-commits.html) | 1 day |
| `rebase`, `pull --rebase`, `rebase -i` | none; designed, opt-in, never rewriting pushed history | 2.12 | [07](/research/git-parity-design-rebase.html) | 2–3 days |
| `worktree` | none; designed: a second working copy in seconds that borrows the main store, like Git's alternates | 2.13 | [06](/research/git-parity-design-worktree.html) | 2–3 days |
| garbage collection | none; compaction moves old packs to `archive/`; client-driven `vault prune` planned | 2.10 | | 2–3 days |
| delta compression | each blob deflated, no deltas; needs a format feature and a gate | 2.11 | | 1–2 weeks |
| `archive`, `shortlog`, `describe`, aliases | none | 2.14 | | small each |
| read one file with no clone, from the CLI | the browser reader does it on normal vaults; on pack vaults, Phase 4 of [pack indexes](/dev/pack-indexes/index.html) | | | S / L |
| a command for append lanes | the server feature only | | | S–M |
| per-folder read access | one key per vault; a scoped clone is not a boundary; would need folder keys | | | XL |
| submodules | none; a design if someone asks | 2.15 | | design |
| 160-bit ids by default | format 2, 128-bit, opt-in since 0.19.0 | | | shipped, opt-in |
| twenty years of maturity | a month of releases, now one reviewed build per merge | | | time |

**Moved to a future server, "SGitHub"** ([the roadmap, section 4](/research/git-parity-roadmap.html)): GitHub's features, not Git's.
- accounts, and who pushed;
- branches protected per person;
- an owner-signed list of who may write, which closes TM-R01;
- review, CI and verified badges.

These are possible under zero knowledge, with per-member write tokens checked by ref id and review objects kept in the vault, but they belong to a host, not to the CLI.

## 4. What zero knowledge rules out {#ruled-out}

These are limits of the model, not of effort. Each has a substitute on the client.

| Ruled out | Why | The substitute |
|---|---|---|
| anything the host must read to do: server-side search, diffs, a merge button, code scanning, language statistics | the host holds ciphertext; giving it the key ends zero knowledge | do it in the client, the browser, or a runner the key holder controls |
| taking back what a reader already has | no system can; a removed GitHub collaborator keeps their clone too | rotate forward (`vault rekey`, `vault move`), delete the old vault; per-folder keys limit what each reader ever got |
| per-folder permissions inside one key | the host cannot tell folders apart, and the key decrypts every object | per-folder keys (section 3) |
| hiding all metadata | sizes, timing, counts and access patterns are visible to any store | padding, fixed-size packs and decoy reads reduce it at a bandwidth cost; only an ORAM-style protocol removes it |
| the host optimising the store: repacking, deltas, dedupe across vaults | the host has only ciphertext; dedupe across vaults would need convergent encryption, which leaks equality | client-side deltas and prune (section 3) |
| a host that enforces fast-forward-only | the host cannot read a ref, so it cannot check ancestry | the client-side rewind guard (row 8), shipped |

## 5. The qualifiers {#qualifiers}

Said plainly, so that nobody builds on a stronger claim than the code makes:

- **What the host still sees:**
  - sizes, timing and object counts;
  - in pack mode, which commit each push carried;
  - which trees are equal, because tree encryption is deterministic;
  - with `blob-deflate`, how compressible each file is;
  - the sizes of index packs;
  - in path-ordered packs, which blobs share a folder;
  - for a scoped clone, which byte ranges it read.
- **Reading is a capability; writing is a permission.** The write key is a bearer secret that the host checks, with no cryptographic role. A read-key holder who can write to the store can author history that `check verify` calls verified. A signature today proves "a key holder", not a particular clone or person. This is the threat model's top accepted risk, TM-R01. On the roadmap, own-key signing (design 02) lets each verifier decide whom to trust, as Git does, and an owner-signed list of who may write moves to the future server.
- **An index is checked under the vault's signature policy.** An unsigned index is accepted unless the vault has `signatures-required`. A signing teammate could mislead a fresh clone's working copy, as a commit from that key could. `sgit pack index verify` catches it (TM-R42).
- **A read key cannot be revoked after the fact,** and it is per vault, not per folder (TM-R12). The remedy is rotation, as above.

*Sources: the CLI team's [review of the newsroom's article](/research/sgit-and-git-article-review.html), written against SGit-AI__CLI at `640069a`; sgit-ai 0.26.0 from PyPI and its [command reference](/reference/index.html); [the check script](https://github.com/SGit-AI/SGit-AI__Website__Cli/tree/dev/admin/research/sgit-and-git-2026-10-28), run on 28 October 2026; [git-crypt's README](https://github.com/AGWA/git-crypt/blob/master/README.md); Git's documentation on [git-clone](https://git-scm.com/docs/git-clone) and [git-config](https://git-scm.com/docs/git-config). Where this page and the code disagree, the code wins and this page is wrong: say so on [GitHub](https://github.com/SGit-AI/SGit-AI__CLI/issues).*
