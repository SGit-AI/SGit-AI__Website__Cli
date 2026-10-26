# sgit-ai 0.25.0 release notes: large vaults, cli.sgit.ai

> Release notes for sgit-ai 0.25.0, for people and agents. On a large vault, the cost of a command now follows the change, not the vault. On a vault of 76,000 files a one-file commit went from 29 minutes to under 5 seconds and a status from 71 seconds to about 4. What changed (trees read as JSON, the flattened head cached, a linear and incremental tree builder, a scan cache keyed like git's index, no tree walk when a push's server has nothing new, history log by tree diff), the data-loss bug a review found in the first version of the scan cache and how it was closed, the two new cache files and what they hold, and what is still slow. Nothing changes on the server or in a vault's format.

*Source: <https://cli.sgit.ai/docs/update-to-0-25-0.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit-ai 0.25.0: large vaults

The release notes for 0.25.0, written to be read by a person or handed to an agent. **Your daily loop does not change**, and nothing changes on the server or in how a vault is stored. What changes is how long a command takes on a big vault: it now follows the size of the change, not the size of the vault.

## 1. Update and check

```text
$ sgit update          # wraps: pip install --upgrade sgit-ai
$ sgit version
sgit-ai v0.25.0
```

If `sgit version` shows an older number, you have more than one Python environment. Run `python -m pip install --upgrade sgit-ai` in the one your harness uses. Existing clones need nothing.

The first `status` in each clone after the update reads and hashes every file once, to build its new scan cache. On a vault of 76,000 files that took 47 seconds. Every command after it is fast.

## 2. What it measured

The newsroom reported on 26 October that its source-watch vault had become very slow in 0.24.0. That vault holds 79,465 files in 38,474 folders and 2.7 GB:

- **`status`:** 155 s.
- **`commit`:** more than 4 minutes, whatever the commit held.
- **`push`:** about 4 minutes 15 seconds.
- **`history log`:** more than 8 minutes.

The same commands, on vaults of the same shape:

| Command | 0.24.0 | 0.25.0 | Vault |
|---|---|---|---|
| `status`, nothing changed | 70.7 s | **3.9 to 4.4 s** | 76,000 files, 58,061 folders (cli.sgit.ai) |
| `status`, one file changed | 70.8 s | **4.1 s**, the same file reported | the same |
| `commit` of one file | **1,739 s** (29 min) | **4.6 s** | the same |
| the first commit of all 76,000 files | not run | **55 s** | the same |
| `status`, nothing changed | 130 s | **7.4 s** | 228,000 files, 77,227 folders (CLI team) |
| the first commit of the whole vault | 2,846 s (47 min) | **155 s** | the same |
| `push` of one small commit | about 4 min 15 s (the newsroom's vault) | **10 to 18 s** | the same |
| `history log`, 10 commits with counts | 464 s | **7.4 s** | the same |

The cli.sgit.ai figures are local commands on a 4-core cloud sandbox, 0.24.0 from PyPI against the release code on the same clone. The CLI team's are from an in-memory host, so network time is excluded; the newsroom's include it.

## 3. What changed

- **Trees are read as the JSON they are.** 0.24.0 built a typed object for every tree, about 3 ms each: two minutes on 38,000 folders. Ids are still checked against the object-id form.
- **The flattened head is cached,** per process and on disk under `.sg_vault/local/flat-cache/<tree id>.json`. A tree id is a content address, so the cache never needs invalidating. The newest two heads are kept. The cache is versioned, validated when read, and checked against the root tree; anything wrong in it is rebuilt.
- **The tree builder is linear.** It used to scan every folder for each folder's children, which was quadratic: the 47-minute first commit.
- **A commit builds only what changed.** A file whose size and content hash match the head keeps its entry without being read. A folder whose contents are all unchanged keeps its tree id. A one-file commit builds the folders on that file's path and nothing else. The ids are exactly those a full build gives: the tests compare both, and a fuzzer of about 430 commits compared every head against a full rebuild.
- **`status` no longer hashes every file.** A scan cache (`.sg_vault/local/scan-cache.json`) records each file's hash under git's index key: modification time, change time, size, inode and device. A file is trusted only if all five match and it was last modified more than two seconds before the scan began.
- **Path checks are memoised,** and ignore rules are cached per folder. The scan takes one `lstat` per file.
- **A push no longer walks every tree when the server has nothing new.** If the server's head is the one this clone last accepted, and every object of it is local, the implicit pull skips the walk. Any doubt takes the full fetch, as before.
- **`history log` diffs each commit against its parent,** walking only where tree ids differ, instead of flattening every commit in full. Its output is byte-identical to 0.24.0's.
- **`sgit pull` lists every commit the branch gained,** with its date, even when `status` or a pack had already brought the objects. It used to print "0 new commits" in that case. The list is exact under a merge with one machine's clock behind.

## 4. A bug found before release, and closed

A review of the branch on 26 October found that the first form of the scan cache trusted a file whose size and modification time were unchanged. That form was briefly on dev as **0.24.1**, never on PyPI.

- **What went wrong:** an edit that kept a file's size and modification time was invisible. A restored mtime, `cp -p`, `rsync -t`, an unpacked zip or tar and a same-size `mv` all do that. `commit` skipped the edit, and `pull` then overwrote it with the incoming version.
- **The fix:** the cache now keys on the change time, inode and device as well, which no ordinary tool can set back. It records a file only when nothing moved while it was read. And `pull` always re-reads the files a merge would touch before it decides the working tree is clean.
- **Confirmed** with the review's three reproductions, each now behaving exactly as 0.24.0 does, and a test for each.

If you installed 0.24.1 from dev, update: its cache file is discarded and rebuilt automatically.

## 5. What is on disk now

Two new files in each clone's `.sg_vault/local/`, both readable by you alone (mode 0600):

| File | Holds | Delete it? |
|---|---|---|
| `flat-cache/<tree id>.json` | the head's paths, sizes, content hashes, types and folder tree ids; the newest two heads | safe; rebuilt on the next command |
| `scan-cache.json` | every working-copy path with its timestamps, size, inode and hash | safe; the next `status` re-reads every file |

They hold **file names in clear**, next to the vault key that is already there (threat model TM-R41):
- `history diff` against an old commit caches that commit's names, including files deleted since;
- a sparse clone caches names it never fetched.

Backups made with `sgit vault backup` do not include them. Under the proposed [sealed vault keys](../dev/sealed-vault-keys/index.md), they would be encrypted or kept in memory.

**Compatibility:**
- a clone used with 0.25.0 still works with 0.24.0, which ignores the new files;
- 0.24.0 and 0.25.0 read each other's commits as clean;
- vaults, the server and pack mode are unchanged.

## 6. Still slow, or not covered

- **A `pull` that brings commits pushed by another clone** still walks the new head's trees the old way: a minute or two on the newsroom's vault, against hours before.
- **A three-way merge,** when two clones changed the same branch, still builds the whole tree.
- **`push` still walks the working tree once** looking for `.conflict` files: about 4 s on a large vault.
- **`pull`'s list of new commits reads the clone's whole history,** about 0.4 ms a commit. That is half a second on 1,229 commits and about 2 s on 5,000, even when nothing is new.
- **On Windows,** Python's change time is the creation time. An edit that keeps a file's size and restores its modification time may still go unseen there. Linux and macOS are covered.

*Sources: the CLI's CHANGELOG and its response notes of 26 October 2026 under `team/humans/dinis_cruz/claude-code-web/10/26/`; the newsroom's slowness report of the same day; cli.sgit.ai's two reviews of the branch, run against SGit-AI__CLI at `c6c48187` and `3ffcb5c7`, with the full test suite (4,588 passed), the review's reproductions, a fuzzer of about 430 commits, and the timings above on a vault of 76,000 files.*

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/docs/update-to-0-25-0.html)*
