# Quickstart, cli.sgit.ai

> From zero to a synced, encrypted, versioned vault in five minutes: create, commit, push, clone, pull.

*Source: <https://cli.sgit.ai/docs/quickstart.html> · site v0.1.0 · generated from the same content as the page, so the two cannot drift. Moved from <https://sgit.ai/docs/quickstart.html> (sgit.ai v0.7.87) on 2026-10-20.*

---
# Quickstart

From zero to a synced, encrypted, versioned vault in five minutes.

## 1, Create a vault

```
$ pip install sgit-ai
$ sgit create my-vault
✓ Vault created and registered
✓ Initial commit pushed

  Vault key: <24-char-passphrase>:<vault-id>
```

**Save the vault key now**: in a password manager, not a text file. It is the address, the credential, and the encryption key in one string. There is no reset: lose it and the vault is unrecoverable, by design.

Already have a folder full of files? `cd` into it and run `sgit init --existing` instead, the current contents become the first snapshot.

## 2, Work like git

```
$ cd my-vault
$ echo "# Plan" > plan.md
$ sgit status
  added: plan.md
$ sgit commit -m "add the plan"
✓ Committed 1 file
```

There is no staging area, `sgit commit` snapshots the whole folder. Files like `.env` and private keys are always excluded, automatically.

## 3, Push

```
$ sgit push
✓ Pushed 1 commit — only ciphertext left this machine
```

## 4, Clone somewhere else

```
# on another machine, or in an agent's session
$ sgit clone <vault-key>
✓ Cloned and decrypted 1 file
$ sgit pull      # pick up new commits any time
```

## 5, Look around

```
$ sgit history log --oneline     # commit history
$ sgit history diff              # what changed
$ sgit vault info                # identity, remote, web URL
```

The web URL printed by `sgit vault info` opens the same vault in the SG/Vault browser app, decrypted in the browser, never on the server.

## Where next

- [sgit for git users](../docs/sgit-for-git-users.md), the Rosetta stone
- [The two-branch model](../docs/two-branch-model.md), how collaboration works
- [Working with AI agents](../docs/agents.md), give an agent a private, versioned workspace

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/docs/quickstart.html)*
