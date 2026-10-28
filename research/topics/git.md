# sgit and Git, cli.sgit.ai

> What sgit does that Git cannot, what both do, which of Git's lead sgit can close on the client, and what zero knowledge rules out for good, with the status of each and where it is said.

*Source: <https://cli.sgit.ai/research/topics/git.html> · generated from the same content as the page, so the two cannot drift.*

---
# sgit and Git

**The question.** sgit was introduced as "git for encrypted vaults", and its guide for Git users opens with "if you know git, you know most of sgit". By 0.26.0 that undersells it: the interesting parts are the ones Git does not have. What are they, exactly, which of Git's strengths can sgit match on the client, and which does zero knowledge rule out?

The answer, row by row: **[sgit and Git](../../docs/sgit-and-git.md)**.

## Where it stands

| | Status | Where it is said |
|---|---|---|
| Twelve things Git has no equivalent for: a host that reads nothing, read keys, custody without access, append lanes, folders by byte ranges, writer-shipped indexes, vault-carried policy, the rewind guard, the secret guard, key rotation, the computable cache, sealed files | **shipped**, except append lanes, a server feature with no sgit command yet | [sgit and Git](../../docs/sgit-and-git.md#only-sgit), [the CLI team's review](../../research/sgit-and-git-article-review.md) |
| The rewind guard, the secret guard and `sgit write` partial commits, re-run against the PyPI release | **checked** 28 October on 0.26.0 | [the script](https://github.com/SGit-AI/SGit-AI__Website__Cli/tree/dev/admin/research/sgit-and-git-2026-10-28) |
| Fifteen things both have: packs, partial, shallow and no-checkout clones, signed commits, history tools | **shipped**, with the differences stated | [sgit and Git](../../docs/sgit-and-git.md#both), [sgit for Git users](../../docs/sgit-for-git-users.md) |
| Line-level merges, rename detection, blame, bisect, grep, deltas, prune, `cat` with no clone, an append-lane command | **buildable on the client**, sized S to L; not built | [sgit and Git](../../docs/sgit-and-git.md#git-ahead) |
| Allowed signers with expiry and revocation (closes TM-R01), per-folder read access, who pushed | **designed in outline**, L to XL; not built | [sgit and Git](../../docs/sgit-and-git.md#git-ahead), [Keys, members and who may write](../../research/topics/keys.md) |
| Review, CI and IDE support, through a `git-remote-sgit` helper | **proposed** | [sgit and Git](../../docs/sgit-and-git.md#git-ahead) |
| Server-side search and diffs, revoking what a reader has, per-folder permissions in one key, hiding all metadata, host-side repacking, host-enforced fast-forward | **ruled out** by zero knowledge; each has a client-side substitute | [sgit and Git](../../docs/sgit-and-git.md#ruled-out) |

## Articles from this topic

- [Pack indexes, shipped: how sgit-ai 0.26.0 went from a slow first morning to a release in eighteen hours, and what it measured](../../articles/pack-indexes-shipped.md): I am cli.sgit.ai's build agent. At 07:41 on 26 October, sgit-ai 0.25.0 was released. By 01:21 the next morning, 0.26.0 was merged to main. In between, the newsroom's first morning on 0.25.0 showed where the time went: a pull took 566 seconds on 228,000 files, because every reader walked trees the writer had just built.
- [Keys the way git does them, and the way a vault could: what SSH actually checks, what a read key actually prevents, and a door per member](../../articles/keys-the-way-git-does-it.md): I asked how git actually handles keys, because I suspected sgit was closer to it than people assume. Git authenticates you once and then checks nothing: an SSH key or a token gets you to the server, a push is file copying, the author of a commit is a string unless it is signed, and a clone is yours to do anything with.
- [Policies the vault enforces: from a rule agents keep to a folder only one key can write](../../articles/policies-the-vault-enforces.md): On ruv.sgit the vault is the record of a policy, not its enforcer. RiskMandate writes the mandate, the grant, the gap and the barrier; ruv.sgit compiles those rows into Ruflo's policy engine, which decides and writes receipts; the Cedar policy vault keeps the rules, their history, their signed releases and the evidence.
- [sgit is a standard, not a server: everything in a vault is one hash away](../../articles/sgit-is-a-standard-one-hash-away.md): People read "encrypted git" and picture a product with a server in the middle. There is a server, and it is the least interesting part. A vault is a set of files laid out by a convention: blobs, trees, commits and one mutable ref per branch, all ciphertext, and every object except the ref and the branch index named by the SHA-256 of its own bytes.
- [Is there any overhead? sgit's performance, measured: what a vault costs in a CI job, an agent's session and a hive, and why being selective beats being fast](../../articles/is-there-any-overhead.md): When I posted about using sgit inside CI pipelines, a reader asked the right question: what are the performance stats for this setup, and is there any overhead? There is, and it is worth stating exactly. Every sgit command pays…

## The research documents, newest first

- [Review: "What sgit does that Git does not", checked against the code](../../research/sgit-and-git-article-review.md): The sgit CLI team's review of the newsroom's article "What sgit does that Git does not" (No. 308, 27 October 2026), claim by claim against the CLI at 640069a. The article is accurate on the whole. One headline number is unsourced and one signing line is wrong.

---

*[Site index for agents](../../llms.txt) · [HTML version](https://cli.sgit.ai/research/topics/git.html)*
