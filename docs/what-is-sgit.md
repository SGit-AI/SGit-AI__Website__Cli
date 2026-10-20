# What is sgit, cli.sgit.ai

> sgit is git for encrypted vaults: how it works, what makes it different from git, and the ecosystem around it.

*Source: <https://cli.sgit.ai/docs/what-is-sgit.html> · site v0.1.0 · generated from the same content as the page, so the two cannot drift. Moved from <https://sgit.ai/docs/what-is-sgit.html> (sgit.ai v0.7.87) on 2026-10-20.*

---
# What is sgit

**sgit is git for encrypted vaults.** Clone, commit, branch, diff and merge folders of files that are encrypted with AES-256-GCM before they leave your machine. The server stores ciphertext under opaque IDs, it never sees your filenames, your contents, or your commit messages.

It's like git and a password vault had a baby.

## How it works

A vault is an ordinary folder plus a `.sg_vault/` directory. When you commit, sgit snapshots the folder into a git-like object graph, commits pointing at trees pointing at content blobs, and encrypts every object client-side. When you push, only changed ciphertext travels. Object IDs are content-addressed (`obj-cas-imm-…`), so unchanged files are never re-uploaded, and the server can deduplicate data it cannot read.

```
your-folder/
├── <your files>            # untouched — a vault is just a folder
└── .sg_vault/
    ├── bare/                # encrypted objects, refs, branch keys
    └── local/               # your private clone-branch key — never pushed
```

The **vault key** (`passphrase:vault-id`) is three things in one string: the address of the vault on the server, the credential to access it, and the root of the local key-derivation hierarchy. Whoever holds it can decrypt the vault; nobody else, including the server, can. See the [security model](../security/index.md) for the full derivation chain.

## What makes it different from git

- **Everything is encrypted client-side**: content, filenames, messages, branch names.
- **No staging area**: commit snapshots the whole folder, like `git commit -a` for everything.
- **A two-branch model**: a private clone branch per machine or agent plus shared named branches, which is what makes safe multi-agent collaboration possible. [Details →](../docs/two-branch-model.md)

## One vault, three doors

- **sgit**: this CLI. Open source, Apache-2.0, `pip install sgit-ai`.
- **SG/Vault**: the web app: browse, edit and review the same vaults in a browser, via an independent implementation of the same wire format. [How it works →](https://sgraph.ai)
- **SG/Send**: the zero-knowledge transfer API both clients speak to. [How it works →](https://sgraph.ai)

**Maturity:** sgit is in beta and has been powering production workflows for a while. The vault format is versioned and `sgit migrate` handles upgrades. Read [when NOT to use sgit](../docs/limitations.md) for the honest edges.

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/docs/what-is-sgit.html)*
