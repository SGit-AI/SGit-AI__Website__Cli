# Pack indexes, 01: the format, cli.sgit.ai

> Where index packs live on the host, the zip layout with an encrypted, signed header first, every member's JSON schema (flat, folder, changes, commits, commit-gen, blob-paths, file-commits), how members are encrypted, the order of members in new data packs, sizes, and versioning.

*Source: <https://cli.sgit.ai/dev/pack-indexes/01-format.html> · generated from the same content as the page, so the two cannot drift.*

---
# 01. The format

## 1. On the host

```
bare/packs/
  commits/    <epoch>__<commit>__<bytes>.zip      data packs, as in 0.24.0
  snapshots/  <epoch>__<commit>__<bytes>.zip
  archive/    <epoch>__<commit>__<bytes>.zip
  indexes/
    commits/    <epoch>__<commit>__<bytes>.zip    the index of commits/<epoch>__<commit>__*.zip
    snapshots/  <epoch>__<commit>__<bytes>.zip    the index of snapshots/<epoch>__<commit>__*.zip
    archive/    <epoch>__<commit>__<bytes>.zip    moved with the data pack they index
```

- **Names follow `PACK_NAME_RE`** (`Vault__Packs`): the epoch and commit of the data pack indexed, and the index pack's own byte count. A reader pairs an index pack with its data pack by (folder, epoch, commit).
- **Two index packs for one data pack** can exist after a backfill race. Any one whose header verifies is usable; prefer one signed by the data pack's own commit author.
- **0.24.0 to 0.25.0 never list `bare/packs/indexes/`.** `list_folder` is only called with `PACK_COMMITS`, `PACK_SNAPSHOTS` and `PACK_ARCHIVE`, and every listing of `bare/` as a whole (push's first-push check, dump, mirror) only reads refs or copies files.

## 2. The zip

- **ZIP_STORED, `allowZip64=True`, `ZIP_EPOCH` timestamps,** like data packs.
- **Member 0 is `index/header`;** members 1..n are `index/000001`, `index/000002`, ... in the order the header lists them.
- The names say nothing; the header says what each member is.

### 2.1 The header member

```
offset 0   8 bytes   magic b'SGIX\x00\x01\x00\x00'          (format 1)
offset 8   4 bytes   L, big-endian: length of the envelope
offset 12  L bytes   Vault__Crypto.encrypt(read_key, zlib.compress(header_json, 6))
           ...       zero bytes up to the member's reserved size R
```

- **R is a multiple of 16 KiB,** chosen by the writer as large enough for the header after the offsets are known (02, section 4). Padding lets the writer fix every later offset before it knows the envelope's exact length.
- **A reader takes it from the first local file header:** read 30 bytes at offset 0; check the name is `index/header` and the method is stored; read R bytes; read L; decrypt L bytes. It never reads the zip's central directory.

`header_json`, canonical (sorted keys, compact separators, UTF-8, the same form as `Vault__Commit.signing_bytes`):

```json
{
  "schema": "pack_index_v1",
  "kind": "commit",
  "commit_id": "obj-cas-imm-…",
  "parents": ["obj-cas-imm-…"],
  "generation": 20003,
  "tree_id": "obj-cas-imm-…",
  "timestamp_ms": 1761480000000,
  "data_packs": ["commits/1761480000__obj-cas-imm-…__171234.zip"],
  "members": {
    "changes":            [1, 16384, 412,  "sha256 of the member's plaintext JSON"],
    "folder:raw/c09/s4":  [2, 16828, 233,  "…"],
    "folder:":            [9, 18190, 120,  "…"]
  },
  "author_key_id": "key-rnd-imm-…",
  "signature": "…"
}
```

| Field | Meaning |
|---|---|
| `kind` | `commit` (a delta) or `snapshot` (the whole head) |
| `commit_id`, `parents`, `generation`, `tree_id`, `timestamp_ms` | the commit the pack is named by; `tree_id` must equal the commit object's |
| `data_packs` | the data packs that `at` fields point into, by index into this list; a commit index lists its own pack and the older packs its folders' unchanged files live in |
| `members` | logical name → `[sequence number, offset of the member's bytes in the zip, length, sha256 hex of the plaintext JSON]` |
| `author_key_id`, `signature` | ECDSA P-256 over the canonical JSON without `signature`, with the pusher's clone key (`PKI__Crypto.sign`), as a commit is signed |

### 2.2 Every other member

`Vault__Crypto.encrypt(read_key, zlib.compress(member_json, 6))`. This is a random IV, so index packs are not byte-deterministic, and they need not be: their names carry their size, and readers accept any verified one. Deterministic encryption would show the host which folders are unchanged between two snapshots.

## 3. Members

The values in the examples are illustrative. Paths are the vault's paths, `/`-separated, no leading slash; the root folder is `""`. Ids are the vault's object ids. Field names follow the flat cache (`Vault__Sub_Tree`, `FLAT_CACHE_VERSION = 2`) so a reader can seed it directly.

### 3.1 `flat`: snapshot only

The head's flat map, byte for byte the flat cache's format:

```json
{"version": 2, "tree_id": "obj-cas-imm-…",
 "flat": {"raw/c09/s4/pub19/page18/2026-10-21T0100Z/meta.json":
            {"blob_id": "obj-cas-imm-…", "size": 74, "content_hash": "5c40ff698f27",
             "content_type": "application/json", "large": false}},
 "dirs": {"": "obj-cas-imm-…", "raw": "obj-cas-imm-…"}}
```

Measured: 76,000 files and 58,062 folders, 17.2 MB as JSON, **2.42 MB deflated**, 0.58 s to inflate and parse.

### 3.2 `folder:<path>`: snapshot (every folder) and commit (the folders on changed paths)

```json
{"schema": "folder_v1", "path": "raw/c09/s4", "tree_id": "obj-cas-imm-…",
 "files": {"meta.json": {"blob_id": "obj-cas-imm-…", "size": 74, "content_hash": "…",
                         "content_type": "application/json", "large": false,
                         "at": [0, 1048576, 160]}},
 "dirs":  {"pub19": "obj-cas-imm-…"},
 "tree_at": [0, 52, 412],
 "totals": {"files": 1520, "bytes": 259292, "folders": 1161}}
```

- **`at`:** `[index into the header's data_packs, offset of the member's bytes in that data pack, length]`, so a reader takes the blob with one ranged read. It is present from Phase 2, when data packs are path-ordered and the writer knows the offsets.
- **`tree_at`:** the same, for the folder's tree object, so a scoped clone can take the trees it needs.
- **`totals`:** the whole subtree below the folder, so "how many files, how many bytes" is one member.

Measured on the benchmark vault: median **226 bytes** deflated, 11.8 MB for all 58,062.

### 3.3 `changes`: commit only

```json
{"schema": "changes_v1", "commit_id": "obj-cas-imm-…", "parents": ["obj-cas-imm-…"],
 "generation": 20003, "timestamp_ms": 1761480000000, "tree_id": "obj-cas-imm-…",
 "changes": [
   {"path": "raw/c09/s4/pub19/page18/x/text.md", "op": "M",
    "old_blob": "obj-cas-imm-…", "new_blob": "obj-cas-imm-…", "size": 276,
    "content_hash": "…", "content_type": "text/markdown", "large": false, "at": [0, 2088, 310]},
   {"path": "raw/c01/old.md", "op": "D", "old_blob": "obj-cas-imm-…"}
 ]}
```

- **`op`:** `A`, `M` or `D`.
- **A merge commit's changes** are against its first parent.
- **Measured:** 253 bytes deflated for five changes.

### 3.4 `commits:<n>` and `commit-gen`: snapshot only

- `commits:<n>` holds every commit reachable from the head whose generation falls in `[n·1024, (n+1)·1024)`:

  ```json
  {"obj-cas-imm-…": {"parents": ["…"], "generation": 4097, "timestamp_ms": 1761480000000, "tree_id": "…"}}
  ```

- `commit-gen` maps every reachable commit id to its generation, so a reader knows which `commits:<n>` to open.
- **Measured:** a merge base on 20,003 commits loaded 3 members, against 97 when sharded by hash.

### 3.5 `blob-paths:<xx>` and `file-commits:<xx>`: snapshot only

| Member | Holds | Shard key |
|---|---|---|
| `blob-paths:<xx>` | `{blob id: [paths that hold it in the head]}` | `xx` = the first two hex digits of the blob id's hash part |
| `file-commits:<xx>` | `{path: [commit ids that changed it, newest first]}`, from the start of history or the vault's shallow boundary | `xx` = the first two hex digits of sha256(path); inside the encryption, so the hash leaks nothing |

There are 256 of each. Commit indexes do not carry them; a reader applies `changes` to its own copy (03).

## 4. Data packs in path order: Phase 2

`Vault__Packs.write_pack` today writes members in sorted id order. From Phase 2 it writes them in this order:

1. the commit objects, by id;
2. tree objects in the depth-first order of their paths (root first, children by name);
3. blob objects by the path of their first use in that order, each once.

The ids and the member rule (`MEMBER_RE`: only `bare/data/<object id>`, stored) do not change. `extract_pack` sorts by name before writing, and `pack verify` checks each member's hash whatever the order, so 0.24.0 to 0.25.0 read path-ordered packs as before.

**What the order shows the host:** which members sit next to each other, so which blobs share a folder and roughly how large each folder is. It does not show names. 04, section 2 sets the rule.

## 5. Sizes

| Index | Benchmark vault (76,000 files) | Newsroom vault (79,465 files), estimated |
|---|---|---|
| snapshot index | about 15 MB: `flat` 2.4 MB, folders 11.8 MB, commits and cross-references about 1 MB each per 20,000 commits | 15 to 25 MB, against a 1.22 GB snapshot data pack |
| commit index, five files changed | **3.1 KB**, 27 members | a pass of 6,807 files: about 0.5 MB of changes plus the folders on the paths |

## 6. Versioning

- **`schema` values** are `pack_index_v1`, `folder_v1` and `changes_v1`. A reader that meets a higher version ignores the index pack and walks, as for a missing one.
- **New members** may be added under new logical names without a version change; readers ignore names they do not know.
- **The magic's format byte** changes only if the header's binary layout does.

---

*[Site index for agents](../../llms.txt) · [HTML version](https://cli.sgit.ai/dev/pack-indexes/01-format.html)*
