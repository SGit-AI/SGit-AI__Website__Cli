---
title: sgit and Git
summary: What sgit does that Git cannot, what both do, which of Git's lead sgit can close on the client, and what zero knowledge rules out for good, with the status of each and where it is said.
section: topics
order: 0
question: What can sgit do that Git cannot, and which of Git's strengths can sgit match without letting the host read anything?
articles: [pack-indexes-shipped, keys-the-way-git-does-it, policies-the-vault-enforces, sgit-is-a-standard-one-hash-away, is-there-any-overhead]
---

# sgit and Git

**The question.** sgit was introduced as "git for encrypted vaults", and its guide for Git users opens with "if you know git, you know most of sgit". By 0.26.0 that undersells it: the interesting parts are the ones Git does not have. What are they, exactly, which of Git's strengths can sgit match on the client, and which does zero knowledge rule out?

The answer, row by row: **[sgit and Git](/docs/sgit-and-git.html)**.

## Where it stands

| | Status | Where it is said |
|---|---|---|
| Twelve things Git has no equivalent for: a host that reads nothing, read keys, custody without access, append lanes, folders by byte ranges, writer-shipped indexes, vault-carried policy, the rewind guard, the secret guard, key rotation, the computable cache, sealed files | **shipped**, except append lanes, a server feature with no sgit command yet | [sgit and Git](/docs/sgit-and-git.html#only-sgit), [the CLI team's review](/research/sgit-and-git-article-review.html) |
| The rewind guard, the secret guard and `sgit write` partial commits, re-run against the PyPI release | **checked** 28 October on 0.26.0 | [the script](https://github.com/SGit-AI/SGit-AI__Website__Cli/tree/dev/admin/research/sgit-and-git-2026-10-28) |
| Fifteen things both have: packs, partial, shallow and no-checkout clones, signed commits, history tools | **shipped**, with the differences stated | [sgit and Git](/docs/sgit-and-git.html#both), [sgit for Git users](/docs/sgit-for-git-users.html) |
| Line-level merges, rename detection, blame, bisect, grep, deltas, prune, `cat` with no clone, an append-lane command | **buildable on the client**, sized S to L; not built | [sgit and Git](/docs/sgit-and-git.html#git-ahead) |
| Allowed signers with expiry and revocation (closes TM-R01), per-folder read access, who pushed | **designed in outline**, L to XL; not built | [sgit and Git](/docs/sgit-and-git.html#git-ahead), [Keys, members and who may write](/research/topics/keys.html) |
| Review, CI and IDE support, through a `git-remote-sgit` helper | **proposed** | [sgit and Git](/docs/sgit-and-git.html#git-ahead) |
| Server-side search and diffs, revoking what a reader has, per-folder permissions in one key, hiding all metadata, host-side repacking, host-enforced fast-forward | **ruled out** by zero knowledge; each has a client-side substitute | [sgit and Git](/docs/sgit-and-git.html#ruled-out) |

!topic git
