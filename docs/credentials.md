# Vault credentials: what each one can do, and what its prefix declares, cli.sgit.ai

> Two capabilities, a vault key that reads and writes and a read key derived from it one way, plus the five prefixes that declare which you are holding and whether it was meant to be published. Why sgit_public_read_ is the form for an open vault, why publishing one under sgit_private_read_ is a mislabel that an agent will correctly refuse, and why the word matters when the bytes are identical.

*Source: <https://cli.sgit.ai/docs/credentials.html> · site v0.1.0 · generated from the same content as the page, so the two cannot drift. Moved from <https://sgit.ai/docs/credentials.html> (sgit.ai v0.7.87) on 2026-10-20.*

---
# Vault credentials: what each one can do, and what its prefix declares

A vault credential is the whole thing you need: the address, the capability and the decryption key, in one string. There are two capabilities, **write** and **read**, and five prefixes in circulation that declare which one you are holding and whether it was meant to be published. The prefix is a **declaration, not cryptography**: strip it and the bytes are identical. It still matters, and this page is why.

**Why this page exists, with the date on it.** On 20 September 2026 an agent was asked to open two vaults published on this site and refused, because their read keys were labelled `sgit_private_read_`. It was right to refuse and our label was wrong: those keys are deliberately public, and the prefix that says so is `sgit_public_read_`. The keys were relabelled the same day, the build now refuses a private-prefixed credential in any tracked file, and this page is the explanation that was missing.

## Two capabilities, and one is derived from the other

A vault key carries read *and* write. A read key carries read only, and is derived from the vault key by a one-way function, so a read key can never be turned back into write access. That derivation is the whole publishing model on this site: [fifty-four vaults](https://sgit.ai/demos/vaults/index.html) hand out read keys on purpose, and not one of them can be used to change anything.

*[diagram]*

## The five prefixes

Three are current and emitted by the CLI today. Two are legacy, released briefly in v0.15.5, accepted on input forever and never emitted again.

| Prefix | Declares | Capability | Publish it? |
|---|---|---|---|
| `sgit_private_vault_` | A vault key, kept secret | **Read and write** | **Never.** Not in a page, a repository, a commit message, an issue or a release log |
| `sgit_private_read_` | A read key, **kept secret** | Read only | **No.** Publishing it leaks no write capability, but the label says the opposite of what you are doing. Re-derive the string with the public prefix first |
| `sgit_public_read_` | A read key, **deliberately published** | Read only | **Yes.** This is the form every open vault on this site should carry |
| `sgit_vk1_`legacy | A vault key | Read and write | Never |
| `sgit_rk1_`legacy | A read key, intent unstated | Read only | Safe, and says nothing about intent. Most pages on this site still carry this form; the bytes are the same |

A credential with no prefix at all is the oldest form and still circulates. It is read as **unknown** and resolved by context, which is exactly the ambiguity the prefixes were introduced to end.

## Classification is by declaration, never by shape

This is the rule the CLI states in its own source, and it was learned the hard way: *"guessing from shape is what once misrouted a 64-hex passphrase to a read-only clone."* A surface that accepts read credentials must refuse a vault key because the string *says* it is one, not because it looks long enough to be a passphrase.

Shape is still the backstop for the years of keys created before prefixes existed: a read key is 64 hexadecimal characters, and anything else before the colon is a passphrase, which means write. [The publishing method](https://sgit.ai/demos/vaults/publishing.html) runs both checks on every credential submitted to this site, and the front stop is one command:

```
$ python3 admin/build/check_credential.py '<credential>'
  form      : read key (public, prefixed)
  publish?  : YES — read-only, declared public
  why       : the sgit_public_read_ prefix marks a key meant to be published
```

## Why the word matters when the bytes do not

Relabelling a key changes nothing an attacker can use. It changes three things that people and machines rely on.

- **One scanner rule covers every secret credential.** `sgit_private_` matches the vault key, the private read key, and any private credential type invented later. Publishing keys under a private prefix trains that alarm into noise, which is the failure mode where a real leak goes unnoticed because the alert fires every day.
- **Public and private differ by a word, not a character.** That is deliberate. A tired reviewer can misread `rk1` for `vk1`; nobody misreads *public* for *private*.
- **An agent reads the label and acts on it.** The refusal that produced this page was correct behaviour on a wrong label. An agent that ignores a *private* marker because the content happened to be on a public page is an agent that will ignore the next one too.

## What a read key can and cannot do

| **Can** | Clone the vault, read every file, read **every commit in its history**, and run the vault's app in a browser with no account and nothing installed |
|---|---|
| **Cannot** | Commit, push, delete, rotate the key, or reach any other vault. There is no privilege inside it to escalate |
| **Costs** | Nothing to issue, and nothing to the server, which stores ciphertext either way |
| **Does not do** | **Revocation is not retroactive.** Anyone who has fetched the objects keeps them; rotating protects future commits only. Publish a read key the way you would publish the content itself, because that is what you are doing |

## What this site publishes

Every vault in [the gallery](https://sgit.ai/demos/vaults/index.html) carries a read key published on purpose, and no vault key appears anywhere: the release refuses to push if a write credential reaches a tracked file, and since 20 September it refuses a `sgit_private_` credential of any kind. New pages use `sgit_public_read_`. Older pages carry the legacy `sgit_rk1_` form or a bare key, which are the same bytes and open the same way, in the CLI and in the browser.

Checked against sgit-ai v0.16.2 and the SG/Vault web loader on 20 September 2026: all five prefixes plus the bare form strip to the same value and clone the same vault, verified with an all-zeros negative control that produces nothing.

Where each of these should be kept, how a key travels and how to give one to an agent is on [Vault key management](../docs/key-management.md).

---

*[Site index for agents](../llms.txt) · [HTML version](https://cli.sgit.ai/docs/credentials.html)*
